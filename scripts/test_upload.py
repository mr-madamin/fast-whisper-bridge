import httpx

BASE_URL = "http://127.0.0.1:8000"

if __name__ == "__main__":
    with open("tests/fixtures/audio/sample.wav", "rb") as f:
        response = httpx.post(
            f"{BASE_URL}/transcribe",
            files={"file": ("sample.wav", f, "audio/wav")},
            data={"model": "small", "language": "en", "word_timestamps": "false"},
        )

    assert response.status_code == 200, f"expected 200, got {response.status_code}"
