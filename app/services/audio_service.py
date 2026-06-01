import json
import subprocess
from pathlib import Path

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

    return {"extension": kind.extension, "mime": kind.mime}


def probe_duration_seconds(file_path: Path) -> float:
    """Return audio duration in seconds, via ffprobe.

    Raises ValueError if ffprobe fails or returns no duration.
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",  # suppress ffprobe's chatter
            "-show_format",  # we want the container's format block
            "-print_format",
            "json",  # machine-readable output
            str(file_path),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise ValueError(f"ffprobe failed: {result.stderr.strip()}")

    try:
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"Could not read duration from ffprobe output: {e}")


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
