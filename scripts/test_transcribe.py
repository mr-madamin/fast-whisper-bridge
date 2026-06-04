"""Smoke test for WhisperService - run directly, eyeball the output.

python -m scripts.test_transcribe
"""

from pathlib import Path

FIXTURE = Path("tests/fixtures/audio/test_clip.mp3")
