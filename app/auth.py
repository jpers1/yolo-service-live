import secrets
from typing import Annotated

from fastapi import Depends, Header, Request

from app.config import Settings
from app.errors import OpenAIError, openai_error


def get_app_settings(request: Request) -> Settings:
    return request.app.state.settings


def require_api_key(
    settings: Annotated[Settings, Depends(get_app_settings)],
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> None:
    if settings.api_key is None or not settings.api_key.get_secret_value():
        raise openai_error(
            status_code=503,
            message="Service API key is not configured.",
            error_type="configuration_error",
            code="service_not_configured",
        )

    if authorization is None:
        raise _auth_error(message="Missing API key.", code="missing_api_key")

    scheme, separator, token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise _auth_error(message="Invalid authentication scheme.", code="invalid_auth_scheme")

    if not separator or not token.strip():
        raise _auth_error(message="Missing API key.", code="missing_api_key")

    expected_token = settings.api_key.get_secret_value()
    if not secrets.compare_digest(token.strip(), expected_token):
        raise _auth_error(message="Invalid API key.", code="invalid_api_key")


def _auth_error(*, message: str, code: str) -> OpenAIError:
    return openai_error(
        status_code=401,
        message=message,
        error_type="authentication_error",
        code=code,
        headers={"WWW-Authenticate": "Bearer"},
    )
