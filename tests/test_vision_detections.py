import base64
from io import BytesIO
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app
from app.schemas.detections import Detection, DetectionPayload, DetectionSource
from app.vision.detector import DetectorInferenceError, DetectorUnavailableError
from app.vision.fake_detector import FakeDetector
from app.vision.image_decode import DecodedImage


class NonFakeDetector:
    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        return DetectionPayload(
            model=model,
            source=DetectionSource(
                kind="image_url",
                decoded=True,
                mime_type=image.mime_type,
                width=image.width,
                height=image.height,
            ),
            detections=[
                Detection(
                    class_id=1,
                    class_name="bicycle",
                    confidence=0.75,
                    box_xyxy=[1.0, 2.0, 3.0, 4.0],
                    box_normalized_xyxy=[0.1, 0.2, 0.3, 0.4],
                )
            ],
            mock=False,
        )


class UnavailableDetector:
    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        raise DetectorUnavailableError("missing dependency with secret-vision-key")


class FailingDetector:
    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        raise DetectorInferenceError("failed with image payload")


def _client(
    *,
    api_key: str | None = "test-key",
    public_model_name: str = "yolo11n-coco",
    max_image_pixels: int = 4_194_304,
    detector=None,
) -> TestClient:
    return TestClient(
        create_app(
            Settings(
                api_key=api_key,
                public_model_name=public_model_name,
                max_image_pixels=max_image_pixels,
                _env_file=None,
            ),
            detector=detector or FakeDetector(),
        )
    )


def _auth_headers(api_key: str = "test-key") -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


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


def _request_body(
    *,
    image_url: str | None = None,
    model: str | None = "yolo11n-coco",
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "image": {"url": image_url or _image_data_url()},
        "include_normalized_boxes": True,
    }
    if model is not None:
        body["model"] = model
    return body


def test_unauthenticated_vision_detections_request_is_rejected() -> None:
    response = _client().post("/v1/vision/detections", json=_request_body())

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "missing_api_key"


def test_missing_server_api_key_fails_closed() -> None:
    response = _client(api_key=None).post(
        "/v1/vision/detections",
        json=_request_body(),
        headers=_auth_headers(),
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_not_configured"


def test_authenticated_valid_request_returns_direct_detection_payload() -> None:
    response = _client(public_model_name="configured-model").post(
        "/v1/vision/detections",
        json=_request_body(model="configured-model"),
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert "choices" not in body
    assert "object" not in body
    assert body["task"] == "object_detection"
    assert body["model"] == "configured-model"
    assert body["source"] == {
        "kind": "image_url",
        "decoded": True,
        "mime_type": "image/jpeg",
        "width": 2,
        "height": 3,
    }
    assert body["mock"] is True
    assert body["detections"] == [
        {
            "class_id": 0,
            "class_name": "person",
            "confidence": 0.99,
            "box_xyxy": [0.0, 0.0, 1.0, 1.0],
            "box_normalized_xyxy": [0.0, 0.0, 1.0, 1.0],
        }
    ]


def test_injected_non_fake_detector_response_has_mock_false() -> None:
    response = _client(detector=NonFakeDetector()).post(
        "/v1/vision/detections",
        json=_request_body(),
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mock"] is False
    assert body["detections"][0]["class_name"] == "bicycle"


def test_omitted_model_defaults_to_configured_public_model_name() -> None:
    response = _client(public_model_name="configured-model").post(
        "/v1/vision/detections",
        json=_request_body(model=None),
        headers=_auth_headers(),
    )

    assert response.status_code == 200
    assert response.json()["model"] == "configured-model"


def test_unsupported_model_returns_openai_like_error() -> None:
    response = _client().post(
        "/v1/vision/detections",
        json=_request_body(model="unknown-model"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_model"


def test_external_image_url_returns_openai_like_error_without_url() -> None:
    response = _client().post(
        "/v1/vision/detections",
        json=_request_body(image_url="https://example.test/image.jpg"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "external_image_url_not_supported"
    assert "example.test" not in response.text


def test_invalid_base64_returns_openai_like_error_without_payload() -> None:
    response = _client().post(
        "/v1/vision/detections",
        json=_request_body(image_url="data:image/jpeg;base64,not-valid!!!"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_image_data"
    assert "not-valid" not in response.text


def test_unsupported_image_mime_returns_openai_like_error() -> None:
    response = _client().post(
        "/v1/vision/detections",
        json=_request_body(image_url="data:image/gif;base64,AAAA"),
        headers=_auth_headers(),
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_image_mime"


def test_oversized_image_returns_openai_like_error() -> None:
    response = _client(max_image_pixels=5).post(
        "/v1/vision/detections",
        json=_request_body(image_url=_image_data_url(size=(3, 3))),
        headers=_auth_headers(),
    )

    assert response.status_code == 413
    assert response.json()["error"]["code"] == "image_too_large"


def test_detector_unavailable_returns_openai_like_error_without_secrets_or_payload() -> None:
    image_url = _image_data_url()
    encoded_payload = image_url.partition(",")[2]

    response = _client(api_key="secret-vision-key", detector=UnavailableDetector()).post(
        "/v1/vision/detections",
        json=_request_body(image_url=image_url),
        headers=_auth_headers("secret-vision-key"),
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "detector_not_available"
    assert "secret-vision-key" not in response.text
    assert encoded_payload not in response.text


def test_detector_inference_error_returns_openai_like_error_without_secrets_or_payload() -> None:
    image_url = _image_data_url()
    encoded_payload = image_url.partition(",")[2]

    response = _client(api_key="secret-vision-key", detector=FailingDetector()).post(
        "/v1/vision/detections",
        json=_request_body(image_url=image_url),
        headers=_auth_headers("secret-vision-key"),
    )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "inference_failed"
    assert "secret-vision-key" not in response.text
    assert encoded_payload not in response.text
