from typing import Annotated
from fastapi import APIRouter, UploadFile, File, Form

router = APIRouter()

@router.post("/transcribe")
async def create_transcription(
  file: Annotated[UploadFile, File(description="Audio file to transcribe")],
  model: Annotated[str, Form()] = "base",
  language: Annotated[str, Form()] = "auto",
  word_timestamps: Annotated[bool, Form()] = True,
):
  contents = await file.read()
  print(f"got file: name={file.filename}, size={len(contents)} bytes")
  print(f"params: model={model}, language={language}, "
        f"word_timestamps={word_timestamps}")
  return {
    "filename": file.filename,
    "size": len(contents),
    "model": model,
    "language": language,
    "word_timestamps": word_timestamps,
  }
