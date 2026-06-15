from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.models import router as models_router
from app.config import Settings, get_settings
from app.errors import OpenAIError, openai_error_handler


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()

    app = FastAPI(
        title=resolved_settings.service_name,
        version=resolved_settings.service_version,
        description="CPU-only YOLO11 object detection service with OpenAI-compatible API endpoints.",
    )
    app.state.settings = resolved_settings
    app.add_exception_handler(OpenAIError, openai_error_handler)
    app.include_router(health_router)
    app.include_router(models_router)
    return app


app = create_app()
