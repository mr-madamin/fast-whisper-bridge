from datetime import datetime

from pydantic import BaseModel, Field


class TranscriptionJob(BaseModel):
    job_id: str
    status: str = Field(description="Job status", examples=["queued"])
    filename: str
    file_size: int = Field(description="Size of uploaded file in bytes", gt=0)
    audio_duration_seconds: float = Field(gt=0)
    model: str
    language: str
    word_timestamps: bool
    created_at: datetime
