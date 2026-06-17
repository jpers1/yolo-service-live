from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.detection_common import (
    decode_request_image,
    enforce_request_size,
    run_detector,
    validate_model,
)
from app.auth import get_app_settings, require_api_key
from app.config import Settings
from app.schemas.detections import DetectionPayload
from app.schemas.vision import VisionDetectionsRequest

router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


@router.post("/vision/detections")
async def create_vision_detection(
    http_request: Request,
    request: VisionDetectionsRequest,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> DetectionPayload:
    await enforce_request_size(http_request, settings)

    requested_model = request.model or settings.public_model_name
    validate_model(requested_model=requested_model, settings=settings)

    decoded_image = decode_request_image(image_url=request.image.url, settings=settings)
    return run_detector(
        http_request=http_request,
        image=decoded_image,
        model=settings.public_model_name,
    )
