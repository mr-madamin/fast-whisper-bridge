"""Smoke test for WhisperService - run directly, eyeball the output.

python -m scripts.test_transcribe
"""

import time
from pathlib import Path

from app.services.whisper_service import whisper_service

FIXTURE = Path("tests/fixtures/audio/test_clip.mp3")


def test_transcribe_returns_result():
    result = whisper_service.transcribe(str(FIXTURE), model="tiny")

    assert result.language, f"expected a language, got {result.language!r}"
    assert result.duration > 0, (
        f"expected duration to be greater than 0, got {result.duration}"
    )
    assert len(result.segments) >= 1, (
        f"expected to have at least 1 segment, got {len(result.segments)}"
    )
    assert len(result.segments[0].words) >= 1, (
        f"expected at least 1 word, got {len(result.segments[0].words)}"
    )

    print(f"✓ transcribed {len(result.segments)} segments, lang={result.language}")


def test_verify_cpu_execution():
    start = time.perf_counter()
    result = whisper_service.transcribe(str(FIXTURE), model="tiny")
    elapsed = time.perf_counter() - start

    device = whisper_service._model.model.device

    # real-time factor: processing time vs audio length
    rtf = elapsed / result.duration

    assert device == "cpu", f"expected cpu, got {device}"
    assert rtf < 1.0, f"slower than real-time: rtf={rtf:.2f}"
    print(
        f"✓ device={device}, {elapsed:.1f}s for {result.duration:.1f}s audio (rtf={rtf:.2f})"
    )


if __name__ == "__main__":
    test_transcribe_returns_result()
    test_verify_cpu_execution()
    print("\nAll checks passed.")
