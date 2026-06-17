import importlib.util
import json
import sys
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError

import pytest
from PIL import Image


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "detect_image.py"
SPEC = importlib.util.spec_from_file_location("detect_image_script", SCRIPT_PATH)
assert SPEC is not None
detect_image = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = detect_image
SPEC.loader.exec_module(detect_image)


def _write_image(path: Path, *, image_format: str) -> Path:
    Image.new("RGB", (4, 3), color=(20, 40, 80)).save(path, format=image_format)
    return path


def test_jpeg_file_becomes_jpeg_data_url(tmp_path: Path) -> None:
    image_path = _write_image(tmp_path / "sample.jpg", image_format="JPEG")

    data_url = detect_image.image_file_to_data_url(image_path)

    assert data_url.startswith("data:image/jpeg;base64,")
    assert len(data_url.partition(",")[2]) > 0


def test_png_file_becomes_png_data_url(tmp_path: Path) -> None:
    image_path = _write_image(tmp_path / "sample.png", image_format="PNG")

    data_url = detect_image.image_file_to_data_url(image_path)

    assert data_url.startswith("data:image/png;base64,")
    assert len(data_url.partition(",")[2]) > 0


def test_unsupported_extension_is_rejected(tmp_path: Path) -> None:
    image_path = _write_image(tmp_path / "sample.gif", image_format="PNG")

    with pytest.raises(detect_image.CliError, match="Only .jpg"):
        detect_image.image_file_to_data_url(image_path)


def test_unsupported_image_type_is_rejected(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    Image.new("RGB", (4, 3), color=(20, 40, 80)).save(image_path, format="GIF")

    with pytest.raises(detect_image.CliError, match="Only JPEG and PNG"):
        detect_image.image_file_to_data_url(image_path)


def test_summary_prints_detection_count_without_base64_payload(capsys: pytest.CaptureFixture[str]) -> None:
    detect_image.print_summary(
        status_code=200,
        response={
            "model": "yolo11n-coco",
            "mock": True,
            "source": {"width": 640, "height": 480, "mime_type": "image/jpeg"},
            "detections": [
                {
                    "class_name": "person",
                    "confidence": 0.91,
                    "box_xyxy": [1.0, 2.0, 3.0, 4.0],
                }
            ],
        },
    )

    output = capsys.readouterr().out
    assert "status=200" in output
    assert "model=yolo11n-coco" in output
    assert "mock=true" in output
    assert "source=640x480 image/jpeg" in output
    assert "detections=1" in output
    assert "0 person 0.91 [1,2,3,4]" in output
    assert "base64" not in output


def test_main_prints_openai_like_error_and_exits_nonzero(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    image_path = _write_image(tmp_path / "sample.jpg", image_format="JPEG")

    def fake_post_detection(**_: object) -> tuple[int, dict[str, object]]:
        return 401, {
            "error": {
                "code": "invalid_api_key",
                "message": "Invalid API key.",
            }
        }

    monkeypatch.setattr(detect_image, "post_detection", fake_post_detection)
    monkeypatch.setattr(
        sys,
        "argv",
        ["detect_image.py", str(image_path), "--api-key", "secret-cli-key"],
    )

    exit_code = detect_image.main()

    output = capsys.readouterr().out
    assert exit_code == 1
    assert "error_code=invalid_api_key" in output
    assert "error_message=Invalid API key." in output
    assert "secret-cli-key" not in output


def test_post_detection_sends_auth_without_printing_key(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    secret_key = "secret-cli-key"

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
                    "source": {"width": 4, "height": 3, "mime_type": "image/jpeg"},
                    "detections": [],
                }
            ).encode("utf-8")

    def fake_urlopen(request: object, timeout: int) -> FakeResponse:
        assert timeout == 30
        assert request.get_header("Authorization") == f"Bearer {secret_key}"
        body = json.loads(request.data.decode("utf-8"))
        assert body["image"]["url"] == "data:image/jpeg;base64,abc"
        return FakeResponse()

    monkeypatch.setattr(detect_image, "urlopen", fake_urlopen)

    status_code, response = detect_image.post_detection(
        base_url="http://service.test",
        api_key=secret_key,
        model="yolo11n-coco",
        image_url="data:image/jpeg;base64,abc",
    )

    assert status_code == 200
    assert response["model"] == "yolo11n-coco"
    assert secret_key not in capsys.readouterr().out


def test_post_detection_returns_openai_like_error_body(monkeypatch: pytest.MonkeyPatch) -> None:
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

    monkeypatch.setattr(detect_image, "urlopen", fake_urlopen)

    status_code, response = detect_image.post_detection(
        base_url="http://service.test",
        api_key="secret-cli-key",
        model="yolo11n-coco",
        image_url="data:image/jpeg;base64,abc",
    )

    assert status_code == 401
    assert response == error_body
