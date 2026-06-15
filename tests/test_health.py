from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_healthz_returns_ok() -> None:
    app = create_app(Settings(_env_file=None))
    client = TestClient(app)

    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "YOLO OpenAI Vision API",
        "version": "0.1.0",
    }


def test_readyz_returns_ready_with_model_identity() -> None:
    app = create_app(Settings(public_model_name="test-model", _env_file=None))
    client = TestClient(app)

    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {
            "config": "ok",
            "model": "test-model",
            "api_key_configured": False,
        },
    }


def test_readyz_reports_api_key_boolean_without_secret() -> None:
    app = create_app(Settings(api_key="fake-test-key", _env_file=None))
    client = TestClient(app)

    response = client.get("/readyz")
    response_body = response.text

    assert response.status_code == 200
    assert response.json()["checks"]["api_key_configured"] is True
    assert "api_key" not in response.json()["checks"]
    assert "api_key_configured" in response.json()["checks"]
    assert "fake-test-key" not in response_body


def test_healthz_and_readyz_remain_public_without_server_api_key() -> None:
    client = TestClient(create_app(Settings(api_key=None, _env_file=None)))

    health_response = client.get("/healthz")
    ready_response = client.get("/readyz")

    assert health_response.status_code == 200
    assert ready_response.status_code == 200
    assert ready_response.json()["checks"]["api_key_configured"] is False


def test_app_factory_accepts_explicit_settings() -> None:
    settings = Settings(
        service_name="Test Service",
        service_version="9.9.9",
        public_model_name="factory-test-model",
        _env_file=None,
    )

    app = create_app(settings)

    assert app.title == "Test Service"
    assert app.version == "9.9.9"
    assert app.state.settings is settings
