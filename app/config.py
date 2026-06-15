from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="YOLO_SERVICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "YOLO OpenAI Vision API"
    service_version: str = "0.1.0"
    environment: Literal["development", "test", "production"] = "development"

    api_key: SecretStr | None = None

    public_model_name: str = "yolo11n-coco"
    model_weights: str = "yolo11n.pt"
    default_confidence: float = Field(default=0.25, ge=0.0, le=1.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
