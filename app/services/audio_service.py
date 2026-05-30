from filetype import guess

ALLOWED_AUDIO_EXTENSIONS = {"mp3", "wav", "m4a", "flac", "ogg", "opus"}

def detect_audio_format(data) -> dict:
  kind = guess(data)

  if kind is None:
    raise ValueError("Could not identify file type from its contents")

  if kind.extension not in ALLOWED_AUDIO_EXTENSIONS:
    raise ValueError(
      f"Unsupported format: {kind.extension} ({kind.mime}). "
      f"Allowed: {', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}"
    )

  return {
    "extension": kind.extension,
    "mime": kind.mime
  }

if __name__ == "__main__":
  from pathlib import Path

  fixtures = Path("tests/fixtures/audio")
  for path in sorted(fixtures.iterdir()):
    if path.is_dir():
      continue
    data = path.read_bytes()[:261]
    try:
      result = detect_audio_format(data)
      print(f"✓ {path.name:25} → {result}")
    except ValueError as e:
      print(f"✗ {path.name:25} → rejected: {e}")
