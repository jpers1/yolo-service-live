from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_unauthenticated_models_request_is_rejected() -> None:
    client = TestClient(create_app(Settings(api_key="test-key", _env_file=None)))

    response = client.get("/v1/models")

    assert response.status_code == 401


def test_authenticated_models_request_returns_model_list() -> None:
    client = TestClient(
        create_app(
            Settings(
                api_key="test-key",
                public_model_name="configured-model",
                _env_file=None,
            )
        )
    )

    response = client.get("/v1/models", headers={"Authorization": "Bearer test-key"})

    assert response.status_code == 200
    assert response.json() == {
        "object": "list",
        "data": [
            {
                "id": "configured-model",
                "object": "model",
                "created": 0,
                "owned_by": "local",
                "root": "configured-model",
                "parent": None,
            }
        ],
    }


def test_models_response_contains_exactly_one_model() -> None:
    client = TestClient(create_app(Settings(api_key="test-key", _env_file=None)))

    response = client.get("/v1/models", headers={"Authorization": "Bearer test-key"})

    assert response.status_code == 200
    assert response.json()["object"] == "list"
    assert len(response.json()["data"]) == 1


def test_model_id_and_root_come_from_settings() -> None:
    client = TestClient(
        create_app(
            Settings(
                api_key="test-key",
                public_model_name="settings-model",
                _env_file=None,
            )
        )
    )

    response = client.get("/v1/models", headers={"Authorization": "Bearer test-key"})
    model = response.json()["data"][0]

    assert model["id"] == "settings-model"
    assert model["root"] == "settings-model"


def test_model_response_does_not_include_secret() -> None:
    client = TestClient(
        create_app(
            Settings(
                api_key="secret-model-key",
                public_model_name="safe-model",
                _env_file=None,
            )
        )
    )

    response = client.get("/v1/models", headers={"Authorization": "Bearer secret-model-key"})

    assert response.status_code == 200
    assert "secret-model-key" not in response.text
