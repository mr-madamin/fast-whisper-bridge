from datetime import datetime, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.core.config import settings
from app.core.queue import queue, save_job
from app.models.schemas import TranscriptionJob
from app.services.audio_service import detect_audio_format, probe_duration_seconds
from app.workers.transcribe_worker import run_transcription

router = APIRouter()

UPLOAD_DIR = settings.upload_dir
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/transcribe", response_model=TranscriptionJob)
async def create_transcription(
    file: Annotated[UploadFile, File(description="Audio file to transcribe")],
    model: Annotated[str, Form()] = "base",
    language: Annotated[str, Form()] = "auto",
    word_timestamps: Annotated[bool, Form()] = True,
):
    # Read just enough to identify the format (filetype needs ~261 bytes)
    header = await file.read(261)

    try:
        audio_info = detect_audio_format(header)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    job_id = str(uuid4())
    ext = audio_info["extension"]
    dest = UPLOAD_DIR / f"{job_id}.{ext}"
    created_at = datetime.now(timezone.utc)

    # Rewind and stream the whole file to disk in 1 MB chunks.
    await file.seek(0)
    with open(dest, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)

    # Probe duration
    duration = None
    try:
        duration = probe_duration_seconds(dest)
    except ValueError as e:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400, detail=f"Invalid audio file: {e}"
        ) from None

    # Persist initial job state to Redis
    save_job(
        job_id,
        {
            "status": "queued",
            "filename": file.filename,
            "file_size": dest.stat().st_size,
            "audio_duration_seconds": duration,
            "model": model,
            "language": language,
            "word_timestamps": word_timestamps,
            "created_at": created_at.isoformat(),
        },
    )

    # Hand the slow work to the worker and return immediately
    queue.enqueue(
        run_transcription,
        job_id,
        str(dest),
        model=model,
        language=language,
        word_timestamps=word_timestamps,
    )

    return TranscriptionJob(
        job_id=job_id,
        status="queued",
        file_size=dest.stat().st_size,
        filename=file.filename,
        audio_duration_seconds=duration,
        model=model,
        language=language,
        word_timestamps=word_timestamps,
        created_at=created_at,
    )
