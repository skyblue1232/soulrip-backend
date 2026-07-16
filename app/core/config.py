from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Soulrip API"
    api_prefix: str = "/api/v1"

    database_url: str = f"sqlite:///{BASE_DIR / 'soulrip.db'}"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # OpenAI - AI 인사이트
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    # Gemini - 챗봇 등 기존 기능
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.5-flash"

    admin_key: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            return [
                item.strip()
                for item in value.split(",")
                if item.strip()
            ]

        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()