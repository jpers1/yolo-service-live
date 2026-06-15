import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings


def test_default_settings_load() -> None:
    settings = Settings(_env_file=None)

    assert settings.service_name == "YOLO OpenAI Vision API"
    assert settings.service_version == "0.1.0"
    assert settings.environment == "development"
    assert settings.public_model_name == "yolo11n-coco"
    assert settings.model_weights == "yolo11n.pt"
    assert settings.default_confidence == 0.25


def test_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("YOLO_SERVICE_ENVIRONMENT", "test")
    monkeypatch.setenv("YOLO_SERVICE_PUBLIC_MODEL_NAME", "custom-model")

    settings = Settings(_env_file=None)

    assert settings.environment == "test"
    assert settings.public_model_name == "custom-model"


def test_invalid_confidence_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        Settings(default_confidence=1.1, _env_file=None)


def test_api_key_is_secret() -> None:
    settings = Settings(api_key="fake-test-key", _env_file=None)

    assert isinstance(settings.api_key, SecretStr)
    assert settings.api_key.get_secret_value() == "fake-test-key"
    assert "fake-test-key" not in repr(settings.api_key)
    assert str(settings.api_key) == "**********"
