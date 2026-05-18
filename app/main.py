from fastapi import FastAPI
from app.api import transcribe

app = FastAPI(title="fast-whisper-bridge")

app.include_router(transcribe.router)

@app.get("/health")
def health():
  return {"status": "ok"}
