from fastapi import Request

from app.config import Settings
from app.errors import openai_error
from app.schemas.detections import DetectionPayload
from app.vision.detector import (
    DetectorInferenceError,
    DetectorUnavailableError,
    get_app_detector,
)
from app.vision.image_decode import DecodedImage, ImageDecodeError, decode_image_data_url


async def enforce_request_size(http_request: Request, settings: Settings) -> None:
    if len(await http_request.body()) > settings.max_request_bytes:
        raise openai_error(
            status_code=413,
            message="Request payload is too large.",
            error_type="invalid_request_error",
            code="payload_too_large",
        )


def validate_model(*, requested_model: str, settings: Settings) -> None:
    if requested_model != settings.public_model_name:
        raise openai_error(
            status_code=400,
            message="The requested model is not supported.",
            error_type="invalid_request_error",
            code="unsupported_model",
        )


def decode_request_image(*, image_url: str, settings: Settings) -> DecodedImage:
    try:
        return decode_image_data_url(
            image_url,
            max_request_bytes=settings.max_request_bytes,
            max_image_pixels=settings.max_image_pixels,
        )
    except ImageDecodeError as exc:
        raise openai_error(
            status_code=exc.status_code,
            message=exc.message,
            error_type="invalid_request_error",
            code=exc.code,
        ) from exc


def run_detector(
    *,
    http_request: Request,
    image: DecodedImage,
    model: str,
) -> DetectionPayload:
    detector = get_app_detector(http_request)
    try:
        return detector.detect(model=model, image=image)
    except DetectorUnavailableError as exc:
        raise openai_error(
            status_code=503,
            message="Detector backend is not available.",
            error_type="server_error",
            code="detector_not_available",
        ) from exc
    except DetectorInferenceError as exc:
        raise openai_error(
            status_code=500,
            message="Detector inference failed.",
            error_type="server_error",
            code="inference_failed",
        ) from exc
