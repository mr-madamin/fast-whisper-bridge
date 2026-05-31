from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.audio_service import detect_audio_format

router = APIRouter()

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

  return {
    "filename": file.filename,
    "detected_format": audio_info,
    "model": model,
    "language": language,
    "word_timestamps": word_timestamps,
  }
