from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.models import router as models_router
from app.config import Settings, get_settings
from app.errors import OpenAIError, openai_error_handler
from app.vision.detector import Detector, build_detector


def create_app(settings: Settings | None = None, detector: Detector | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_detector = detector or build_detector(resolved_settings)

    app = FastAPI(
        title=resolved_settings.service_name,
        version=resolved_settings.service_version,
        description="CPU-only YOLO11 object detection service with OpenAI-compatible API endpoints.",
    )
    app.state.settings = resolved_settings
    app.state.detector = resolved_detector
    app.add_exception_handler(OpenAIError, openai_error_handler)
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(models_router)
    return app


app = create_app()
