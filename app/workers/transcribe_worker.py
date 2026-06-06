"""The job function RQ runs in the worker process.

IMPORTANT: this runs in a separate process from the FastAPI app.
The whisper_service singleton (and its lazy-loaded model) lives in the
worker's memory, not the API's. The API never loads a model again
after Step 3.

RQ stores "app.workers.transcribe_worker.run_transcription" + args and
the worker re-imports this function to run it -- which is why it
must be an importable module-level function, not a closure or a method
"""

import traceback
from datetime import datetime, timezone

from app.core.config import settings
from app.core.queue import update_job
from app.services.whisper_service import whisper_service


def run_transcription(
    job_id: str,
    audio_path: str,
    model: str = "base",
    language: str = "auto",
    word_timestamps: bool = True,
) -> str:
    """Transcribe one file. Returns the path to the written result JSON.

    State transitions written to our job hash:
        queued -> processing -> completed   (happy path)
        queued -> processing -> failed      (on any exception)
    """
    update_job(
        job_id,
        status="processing",
        started_at=datetime.now(timezone.utc).isoformat(),
        progress=0.0,
    )

    try:
        result = whisper_service.transcribe(
            audio_path=audio_path,
            model=model,
            language=language,
            word_timestamps=word_timestamps,
        )

        # Heavy output goes to disk, not Redis
        settings.results_dir.mkdir(parents=True, exist_ok=True)
        result_path = settings.results_dir / f"{job_id}.json"
        with open(result_path, "w") as f:
            # Pydantic v2: model_dump_json gives us serialization for free
            f.write(result.model_dump_json(indent=2))

        update_job(
            job_id,
            status="completed",
            progress=1.0,
            finished_at=datetime.now(timezone.utc).isoformat(),
            detected_language=result.language,
            result_path=str(result_path),
        )
        return str(result_path)
    except Exception as e:
        # Catch everything: a bad file marks this job failed but must not
        # crash the worker -- the next job still runs.
        update_job(
            job_id,
            status="failed",
            finished_at=datetime.now(timezone.utc).isoformat(),
            error=str(e),
            traceback=traceback.format_exc(),
        )
        # Re-raise so RQ also records it in its own failed-job registry
        raise
