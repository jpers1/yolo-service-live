import json
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
from app.errors import openai_error
from app.schemas.openai import (
    AssistantMessage,
    ChatCompletionChoice,
    ChatCompletionResponse,
    ChatCompletionsRequest,
    ChatContentPart,
)

router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


@router.post("/chat/completions")
async def create_chat_completion(
    http_request: Request,
    request: ChatCompletionsRequest,
    settings: Annotated[Settings, Depends(get_app_settings)],
) -> ChatCompletionResponse:
    await enforce_request_size(http_request, settings)

    if request.stream:
        raise _invalid_request(
            message="Streaming is not supported.",
            code="streaming_not_supported",
        )

    validate_model(requested_model=request.model, settings=settings)

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

    decoded_image = decode_request_image(image_url=image_url.url, settings=settings)
    detection_payload = run_detector(
        http_request=http_request,
        image=decoded_image,
        model=settings.public_model_name,
    )
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
