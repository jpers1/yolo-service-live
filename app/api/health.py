from typing import Any

from fastapi import APIRouter, Request

from app.config import Settings

router = APIRouter()


def _settings_from_request(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/healthz")
def healthz(request: Request) -> dict[str, str]:
    settings = _settings_from_request(request)
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.service_version,
    }


@router.get("/readyz")
def readyz(request: Request) -> dict[str, Any]:
    settings = _settings_from_request(request)
    return {
        "status": "ready",
        "checks": {
            "config": "ok",
            "model": settings.public_model_name,
            "api_key_configured": settings.api_key is not None
            and bool(settings.api_key.get_secret_value()),
        },
    }
