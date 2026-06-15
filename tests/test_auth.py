from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def _client(api_key: str | None = "correct-test-key") -> TestClient:
    return TestClient(create_app(Settings(api_key=api_key, _env_file=None)))


def test_auth_accepts_correct_bearer_token() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Bearer correct-test-key"})

    assert response.status_code == 200


def test_auth_accepts_bearer_scheme_case_insensitively() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "bearer correct-test-key"})

    assert response.status_code == 200


def test_missing_server_api_key_fails_closed() -> None:
    response = _client(api_key=None).get(
        "/v1/models",
        headers={"Authorization": "Bearer any-client-key"},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_not_configured"


def test_empty_server_api_key_fails_closed() -> None:
    response = _client(api_key="").get(
        "/v1/models",
        headers={"Authorization": "Bearer any-client-key"},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_not_configured"


def test_missing_authorization_header_fails() -> None:
    response = _client().get("/v1/models")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_wrong_auth_scheme_fails() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Basic wrong-token"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_auth_scheme"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_empty_bearer_token_fails() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Bearer "})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_whitespace_only_bearer_token_fails() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Bearer    "})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_wrong_bearer_token_fails() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Bearer wrong-token"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_api_key"
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_wrong_token_value_does_not_appear_in_response_body() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Bearer wrong-token"})

    assert "wrong-token" not in response.text


def test_configured_api_key_value_does_not_appear_in_response_body() -> None:
    response = _client(api_key="server-secret-key").get(
        "/v1/models",
        headers={"Authorization": "Bearer wrong-token"},
    )

    assert "server-secret-key" not in response.text


def test_auth_error_response_shape() -> None:
    response = _client().get("/v1/models", headers={"Authorization": "Bearer wrong-token"})

    assert response.json() == {
        "error": {
            "message": "Invalid API key.",
            "type": "authentication_error",
            "param": None,
            "code": "invalid_api_key",
        }
    }
