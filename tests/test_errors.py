from app.errors import OpenAIError, openai_error, openai_error_body


def test_openai_error_body_returns_expected_structure() -> None:
    assert openai_error_body(
        message="Invalid API key.",
        error_type="authentication_error",
        code="invalid_api_key",
    ) == {
        "error": {
            "message": "Invalid API key.",
            "type": "authentication_error",
            "param": None,
            "code": "invalid_api_key",
        }
    }


def test_openai_error_preserves_status_body_and_headers() -> None:
    error = openai_error(
        status_code=401,
        message="Missing API key.",
        error_type="authentication_error",
        code="missing_api_key",
        headers={"WWW-Authenticate": "Bearer"},
    )

    assert isinstance(error, OpenAIError)
    assert error.status_code == 401
    assert error.headers == {"WWW-Authenticate": "Bearer"}
    assert error.body["error"]["code"] == "missing_api_key"


def test_openai_error_does_not_include_secret_values() -> None:
    error = openai_error(
        status_code=503,
        message="Service API key is not configured.",
        error_type="configuration_error",
        code="service_not_configured",
    )

    assert "server-secret-key" not in str(error.body)
