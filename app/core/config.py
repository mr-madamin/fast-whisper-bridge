from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Loaded from environment / .env, with sensible local default.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Queue + worker
    queue_name: str = "transcription"
    job_timeout: int = 3600  # seconds a single job may run before RQ kills it
    job_ttl: int = 86400  # seconds the job hash survives after completion

    # Paths (relative to project root, matching your existing layout)
    upload_dir: Path = Path("data/uploads")
    results_dir: Path = Path("data/results")
    whisper_model_dir: Path = Path("data/whisper_models")

    default_model: str = "base"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


settings = Settings()
