import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.auth import get_app_settings, require_api_key
from app.config import Settings
from app.errors import openai_error
from app.schemas.openai import (
    AssistantMessage,
    ChatCompletionChoice,
    ChatCompletionResponse,
    ChatCompletionsRequest,
    ChatContentPart,
)
from app.vision.detector import (
    DetectorInferenceError,
    DetectorUnavailableError,
    get_app_detector,
)
from app.vision.image_decode import ImageDecodeError, decode_image_data_url

router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


@router.post("/chat/completions")
async def create_chat_completion(
    http_request: Request,
    request: ChatCompletionsRequest,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ChatCompletionResponse:
    if len(await http_request.body()) > settings.max_request_bytes:
        raise openai_error(
            status_code=413,
            message="Request payload is too large.",
            error_type="invalid_request_error",
            code="payload_too_large",
        )

    if request.stream:
        raise _invalid_request(
            message="Streaming is not supported.",
            code="streaming_not_supported",
        )

    if request.model != settings.public_model_name:
        raise _invalid_request(
            message="The requested model is not supported.",
            code="unsupported_model",
        )

    image_parts = _image_content_parts(request)
    if not image_parts:
        raise _invalid_request(
            message="Exactly one image_url content part is required.",
            code="missing_image",
        )
    if len(image_parts) > 1:
        raise _invalid_request(
            message="Multiple image_url content parts are not supported.",
            code="multiple_images_not_supported",
        )

    image_url = image_parts[0].image_url
    if image_url is None:
        raise _invalid_request(
            message="Exactly one image_url content part is required.",
            code="missing_image",
        )

    try:
        decoded_image = decode_image_data_url(
            image_url.url,
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

    detector = get_app_detector(http_request)
    try:
        detection_payload = detector.detect(
            model=settings.public_model_name,
            image=decoded_image,
        )
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
    assistant_content = json.dumps(detection_payload.model_dump(), separators=(",", ":"))

    return ChatCompletionResponse(
        id="chatcmpl-local-mock",
        object="chat.completion",
        created=0,
        model=settings.public_model_name,
        choices=[
            ChatCompletionChoice(
                index=0,
                message=AssistantMessage(role="assistant", content=assistant_content),
                finish_reason="stop",
            )
        ],
    )


def _image_content_parts(request: ChatCompletionsRequest) -> list[ChatContentPart]:
    return [
        content_part
        for message in request.messages
        for content_part in message.content
        if content_part.type == "image_url" and content_part.image_url is not None
    ]


def _invalid_request(*, message: str, code: str) -> Exception:
    return openai_error(
        status_code=400,
        message=message,
        error_type="invalid_request_error",
        code=code,
    )
