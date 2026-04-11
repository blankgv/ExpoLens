from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "ExpoLens"
    environment: str
    log_level: str
    api_key: str

    # Pipeline
    feedback_interval_seconds: float = 10.0
    metrics_window_seconds: float = 10.0

    # Audio
    whisper_model_size: str = "base"
    filler_words: list[str] = [
        "este", "o sea", "vale", "no sé", "bueno", "digamos",
        "em", "eh", "nove", "básicamente", "literalmente",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
