import importlib.util
import json
import sys
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError, URLError

import pytest
from PIL import Image


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "demo_api_internet_image.py"
SPEC = importlib.util.spec_from_file_location("demo_api_internet_image", SCRIPT_PATH)
assert SPEC is not None
demo_api = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = demo_api
SPEC.loader.exec_module(demo_api)


def _image_bytes(*, image_format: str) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (5, 4), color=(20, 40, 80)).save(buffer, format=image_format)
    return buffer.getvalue()


def test_default_image_url_is_present() -> None:
    assert (
        demo_api.DEFAULT_IMAGE_URL
        == "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/bus.jpg"
    )


def test_downloaded_jpeg_bytes_become_jpeg_data_url() -> None:
    data_url = demo_api.image_bytes_to_data_url(_image_bytes(image_format="JPEG"))

    assert data_url.startswith("data:image/jpeg;base64,")
    assert len(data_url.partition(",")[2]) > 0


def test_downloaded_png_bytes_become_png_data_url() -> None:
    data_url = demo_api.image_bytes_to_data_url(_image_bytes(image_format="PNG"))

    assert data_url.startswith("data:image/png;base64,")
    assert len(data_url.partition(",")[2]) > 0


def test_unsupported_content_is_rejected() -> None:
    with pytest.raises(demo_api.DemoError, match="not a valid JPEG or PNG"):
        demo_api.image_bytes_to_data_url(b"not an image")


def test_request_goes_to_native_endpoint_and_sets_authorization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    secret_key = "secret-demo-key"

    class FakeResponse:
        status = 200

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(
                {
                    "model": "yolo11n-coco",
                    "mock": True,
                    "source": {"width": 5, "height": 4, "mime_type": "image/jpeg"},
                    "detections": [],
                }
            ).encode("utf-8")

    def fake_urlopen(request: object, timeout: int) -> FakeResponse:
        assert timeout == 30
        assert request.full_url == "http://service.test/v1/vision/detections"
        assert request.get_header("Authorization") == f"Bearer {secret_key}"
        body = json.loads(request.data.decode("utf-8"))
        assert body["image"]["url"] == "data:image/jpeg;base64,abc"
        return FakeResponse()

    monkeypatch.setattr(demo_api, "urlopen", fake_urlopen)

    status_code, response = demo_api.post_detection(
        base_url="http://service.test",
        api_key=secret_key,
        model="yolo11n-coco",
        image_url="data:image/jpeg;base64,abc",
    )

    assert status_code == 200
    assert response["model"] == "yolo11n-coco"


def test_summary_prints_expected_fields_without_secrets_or_payload(
    capsys: pytest.CaptureFixture[str],
) -> None:
    demo_api.print_summary(
        status_code=200,
        response={
            "model": "yolo11n-coco",
            "mock": True,
            "source": {"width": 640, "height": 480, "mime_type": "image/jpeg"},
            "detections": [{"class_name": "person"}],
        },
    )

    output = capsys.readouterr().out
    assert "status=200" in output
    assert "model=yolo11n-coco" in output
    assert "mock=true" in output
    assert "source=640x480 image/jpeg" in output
    assert "detections=1" in output
    assert "secret-demo-key" not in output
    assert "base64" not in output


def test_openai_like_error_response_is_printed_safely(
    capsys: pytest.CaptureFixture[str],
) -> None:
    demo_api.print_error(
        {
            "error": {
                "code": "invalid_api_key",
                "message": "Invalid API key.",
            }
        }
    )

    output = capsys.readouterr().out
    assert "error_code=invalid_api_key" in output
    assert "error_message=Invalid API key." in output
    assert "secret-demo-key" not in output


def test_http_error_body_is_returned(monkeypatch: pytest.MonkeyPatch) -> None:
    error_body = {
        "error": {
            "code": "invalid_api_key",
            "message": "Invalid API key.",
        }
    }

    def fake_urlopen(request: object, timeout: int) -> object:
        raise HTTPError(
            url="http://service.test/v1/vision/detections",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=BytesIO(json.dumps(error_body).encode("utf-8")),
        )

    monkeypatch.setattr(demo_api, "urlopen", fake_urlopen)

    status_code, response = demo_api.post_detection(
        base_url="http://service.test",
        api_key="secret-demo-key",
        model="yolo11n-coco",
        image_url="data:image/jpeg;base64,abc",
    )

    assert status_code == 401
    assert response == error_body


def test_network_error_is_handled_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_urlopen(request: object, timeout: int) -> object:
        raise URLError("network unavailable")

    monkeypatch.setattr(demo_api, "urlopen", fake_urlopen)

    with pytest.raises(demo_api.DemoError, match="Image download failed"):
        demo_api.download_image("https://example.test/image.jpg")
