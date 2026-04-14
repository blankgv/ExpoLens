import json
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

FILLER_WORDS_PATH = Path(__file__).parent / "data" / "filler_words.json"


def load_filler_words() -> list[str]:
    with open(FILLER_WORDS_PATH, encoding="utf-8") as f:
        data = json.load(f)
    words = []
    for category_words in data["categories"].values():
        words.extend(category_words)
    # Eliminar duplicados manteniendo orden
    return list(dict.fromkeys(words))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "ExpoLens"
    environment: str
    log_level: str
    api_key: str

    # Pipeline
    feedback_interval_seconds: float = 10.0
    metrics_window_seconds: float = 10.0

    # Audio
    whisper_model_size: str = "base"
    filler_words: list[str] = load_filler_words()


settings = Settings()