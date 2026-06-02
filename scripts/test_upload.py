from pathlib import Path

import httpx

BASE_URL = "http://127.0.0.1:8000"
FIXTURES_DIR = Path("tests/fixtures/audio")


def test_valid_uploads():
    for path in sorted(FIXTURES_DIR.glob("sample.*")):
        with path.open("rb") as f:
            r = httpx.post(
                f"{BASE_URL}/transcribe",
                files={"file": (path.name, f, "application/octet-stream")},
                data={"model": "small", "language": "en", "word_timestamps": "false"},
            )
        assert r.status_code == 200, f"{path.name}: expected 200, got {r.status_code}"
        body = r.json()
        assert body["status"] == "queued", f"{path.name}: status was {body['status']}"
        assert body["job_id"], f"{path.name}: no job_id"
        print(f"✓ {path.name} → 200, job {body['job_id'][:8]}...")


def test_rejects_non_audio():
    bad = Path("/tmp/notaudio.txt")
    bad.write_text("definitely not audio")
    with bad.open("rb") as f:
        r = httpx.post(
            f"{BASE_URL}/transcribe",
            files={"file": ("notaudio.txt", f, "application/octet-stream")},
            data={"model": "base"},
        )
        assert r.status_code == 400, f"expected 400, got {r.status_code}"
        assert "identify" in r.json()["detail"].lower(), (
            f"unexpected detail: {r.json()['detail']}"
        )
        print("✓ rejected non-audio → 400")


if __name__ == "__main__":
    test_valid_uploads()
    test_rejects_non_audio()
    print("\nAll checks passed.")
