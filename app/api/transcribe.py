from typing import Annotated
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.audio_service import detect_audio_format, probe_duration_seconds

router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/transcribe")
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
    raise HTTPException(status_code=400, detail=str(e))

  job_id = str(uuid4())
  ext = audio_info["extension"]
  dest = UPLOAD_DIR / f"{job_id}.{ext}"

  # Write file
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
    raise HTTPException(status_code=400, detail=f"Invalid audio file: {e}")

  return {
    "job_id": job_id,
    "status": "queued",
    "file_size": dest.stat().st_size,
    "filename": file.filename,
    "audio_duration_seconds": duration,
    "model": model,
    "language": language,
    "word_timestamps": word_timestamps,
  }
