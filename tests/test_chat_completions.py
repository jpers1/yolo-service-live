import json
import base64
from io import BytesIO
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app


def _client(
    api_key: str | None = "test-key",
    public_model_name: str = "yolo11n-coco",
    max_request_bytes: int = 5_242_880,
    max_image_pixels: int = 4_194_304,
) -> TestClient:
    return TestClient(
        create_app(
            Settings(
                api_key=api_key,
                public_model_name=public_model_name,
                max_request_bytes=max_request_bytes,
                max_image_pixels=max_image_pixels,
                _env_file=None,
            )
        )
    )


def _image_data_url(
    *,
    mime_type: str = "image/jpeg",
    image_format: str = "JPEG",
    size: tuple[int, int] = (2, 3),
) -> str:
    buffer = BytesIO()
    Image.new("RGB", size, color=(255, 0, 0)).save(buffer, format=image_format)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _valid_request(model: str = "yolo11n-coco", image_url: str | None = None) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "detect objects"},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url or _image_data_url()},
                    },
                ],
            }
        ],
    }


def _auth_headers(api_key: str = "test-key") -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def test_unauthenticated_chat_completions_request_is_rejected() -> None:
    response = _client().post("/v1/chat/completions", json=_valid_request())

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_missing_server_api_key_fails_closed() -> None:
    response = _client(api_key=None).post(
        "/v1/chat/completions",
        json=_valid_request(),
        headers=_auth_headers(),
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_not_configured"


def test_authenticated_valid_request_returns_chat_completion() -> None:
    response = _client(public_model_name="configured-model").post(
        "/v1/chat/completions",
        json=_valid_request(model="configured-model"),
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "chatcmpl-local-mock"
    assert body["object"] == "chat.completion"
    assert body["created"] == 0
    assert body["model"] == "configured-model"
    assert len(body["choices"]) == 1
    assert body["choices"][0]["index"] == 0
    assert body["choices"][0]["message"]["role"] == "assistant"
    assert body["choices"][0]["finish_reason"] == "stop"


def test_authenticated_valid_png_request_returns_chat_completion() -> None:
    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(image_url=_image_data_url(mime_type="image/png", image_format="PNG")),
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["object"] == "chat.completion"


def test_assistant_message_content_is_valid_mock_detection_json() -> None:
    image_url = _image_data_url()
    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(image_url=image_url),
        headers=_auth_headers(),
    )

    content = response.json()["choices"][0]["message"]["content"]
    parsed_content = json.loads(content)

    assert isinstance(content, str)
    assert parsed_content["task"] == "object_detection"
    assert parsed_content["model"] == "yolo11n-coco"
    assert parsed_content["source"] == {
        "kind": "image_url",
        "decoded": True,
        "mime_type": "image/jpeg",
        "width": 2,
        "height": 3,
    }
    assert parsed_content["mock"] is True
    assert image_url not in response.text
    assert len(parsed_content["detections"]) == 1
    assert parsed_content["detections"][0] == {
        "class_id": 0,
        "class_name": "person",
        "confidence": 0.99,
        "box_xyxy": [0.0, 0.0, 1.0, 1.0],
        "box_normalized_xyxy": [0.0, 0.0, 1.0, 1.0],
    }


def test_unsupported_model_returns_openai_like_error() -> None:
    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(model="unknown-model"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["type"] == "invalid_request_error"
    assert response.json()["error"]["code"] == "unsupported_model"


def test_missing_image_returns_openai_like_error() -> None:
    request_body = _valid_request()
    request_body["messages"][0]["content"] = [{"type": "text", "text": "detect objects"}]

    response = _client().post(
        "/v1/chat/completions",
        json=request_body,
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "missing_image"


def test_multiple_images_return_openai_like_error() -> None:
    request_body = _valid_request()
    request_body["messages"][0]["content"].append(
        {
            "type": "image_url",
            "image_url": {"url": _image_data_url(mime_type="image/png", image_format="PNG")},
        }
    )

    response = _client().post(
        "/v1/chat/completions",
        json=request_body,
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "multiple_images_not_supported"


def test_stream_true_returns_unsupported_error() -> None:
    request_body = _valid_request()
    request_body["stream"] = True

    response = _client().post(
        "/v1/chat/completions",
        json=request_body,
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "streaming_not_supported"


def test_secret_api_key_does_not_appear_in_success_response() -> None:
    response = _client(api_key="secret-chat-key").post(
        "/v1/chat/completions",
        json=_valid_request(),
        headers=_auth_headers("secret-chat-key"),
    )

    assert response.status_code == 200
    assert "secret-chat-key" not in response.text


def test_secret_api_key_does_not_appear_in_error_response() -> None:
    response = _client(api_key="secret-chat-key").post(
        "/v1/chat/completions",
        json=_valid_request(model="unknown-model"),
        headers=_auth_headers("secret-chat-key"),
    )

    assert response.status_code == 400
    assert "secret-chat-key" not in response.text


def test_external_image_url_returns_openai_like_error() -> None:
    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(image_url="https://example.test/image.jpg"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "external_image_url_not_supported"
    assert "example.test" not in response.text


def test_unsupported_image_mime_returns_openai_like_error() -> None:
    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(image_url="data:image/gif;base64,AAAA"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_image_mime"


def test_invalid_base64_returns_openai_like_error() -> None:
    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(image_url="data:image/jpeg;base64,not-valid!!!"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image_data"
    assert "not-valid" not in response.text


def test_mime_format_mismatch_returns_openai_like_error_without_payload() -> None:
    image_url = _image_data_url(mime_type="image/png", image_format="JPEG")
    encoded_payload = image_url.partition(",")[2]

    response = _client().post(
        "/v1/chat/completions",
        json=_valid_request(image_url=image_url),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image_data"
    assert encoded_payload not in response.text


def test_oversized_image_returns_openai_like_error() -> None:
    response = _client(max_image_pixels=5).post(
        "/v1/chat/completions",
        json=_valid_request(image_url=_image_data_url(size=(3, 3))),
        headers=_auth_headers(),
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "image_too_large"


def test_oversized_request_body_returns_openai_like_error() -> None:
    response = _client(max_request_bytes=100).post(
        "/v1/chat/completions",
        json=_valid_request(),
        headers=_auth_headers(),
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


def test_secret_api_key_does_not_appear_in_image_error_response() -> None:
    response = _client(api_key="secret-chat-key").post(
        "/v1/chat/completions",
        json=_valid_request(image_url="data:image/jpeg;base64,not-valid!!!"),
        headers=_auth_headers("secret-chat-key"),
    )

    assert response.status_code == 400
    assert "secret-chat-key" not in response.text
