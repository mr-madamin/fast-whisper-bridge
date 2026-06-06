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


class Word(BaseModel):
    start: float
    end: float
    word: str
    probability: float


class Segment(BaseModel):
    start: float
    end: float
    text: str
    words: list[Word]


class TranscriptionResult(BaseModel):
    language: str
    language_probability: float
    duration: float
    segments: list[Segment]


class JobStatus(BaseModel):
    job_id: str
    status: str = Field(examples=["queued", "processing", "completed", "failed"])
    progress: float | None = None
    model: str | None = None
    language: str | None = None
    filename: str | None = None
    detected_language: str | None = None
    created_at: datetime | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error: str | None = None
    result_url: str | None = Field(
        default=None,
        description="Populated once status == 'completed'",
    )
