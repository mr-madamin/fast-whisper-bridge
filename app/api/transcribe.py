from fastapi import APIRouter, UploadFile, File

router = APIRouter()

@router.post("/transcribe")
async def create_transcription(file: UploadFile = File(...)):
  contents = await file.read()
  print(f"got file: name={file.filename}, "
        f"content_type={file.content_type}, "
        f"size={len(contents)} bytes")
  return {
    "filename": file.filename,
    "content_type": file.content_type,
    "size": len(contents)
  }
