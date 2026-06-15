#!/usr/bin/env python

import base64
import json
from io import BytesIO
from typing import Any

from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.main import create_app


API_KEY = "local-smoke-test-key"
MODEL = "yolo11n-coco"


def main() -> None:
    image_url = _jpeg_data_url(size=(64, 64))
    app = create_app(
        Settings(
            api_key=API_KEY,
            detector_backend="yolo",
            model_weights="yolo11n.pt",
            default_confidence=0.25,
            _env_file=None,
        )
    )
    client = TestClient(app)

    response = client.post(
        "/v1/chat/completions",
        json=_request_body(image_url),
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    if response.status_code != 200:
        _print_dependency_hint(response)
        raise SystemExit(f"Expected HTTP 200, got {response.status_code}: {response.text}")

    body = response.json()
    _assert(body["object"] == "chat.completion", "response object is not chat.completion")
    _assert(body["model"] == MODEL, "response model mismatch")

    choices = body["choices"]
    _assert(len(choices) == 1, "expected exactly one choice")
    message = choices[0]["message"]
    _assert(message["role"] == "assistant", "assistant role mismatch")

    content = json.loads(message["content"])
    _assert(content["task"] == "object_detection", "task mismatch")
    _assert(content["model"] == MODEL, "content model mismatch")
    _assert(content["mock"] is False, "YOLO response must not be marked mock")
    _assert(content["source"]["decoded"] is True, "source must be decoded")
    _assert(content["source"]["width"] == 64, "source width mismatch")
    _assert(content["source"]["height"] == 64, "source height mismatch")
    _assert(isinstance(content["detections"], list), "detections must be a list")

    print(f"chat_status={response.status_code}")
    print(f"model={body['model']}")
    print(f"mock={str(content['mock']).lower()}")
    print(f"detections={len(content['detections'])}")
    print("inference_completed=true")


def _jpeg_data_url(*, size: tuple[int, int]) -> str:
    buffer = BytesIO()
    Image.new("RGB", size, color=(255, 255, 255)).save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _request_body(image_url: str) -> dict[str, Any]:
    return {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "detect objects"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
    }


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def _print_dependency_hint(response) -> None:
    try:
        code = response.json()["error"]["code"]
    except (KeyError, TypeError, ValueError):
        return

    if code == "detector_not_available":
        print('Install YOLO extras first: python -m pip install -e ".[yolo]"')


if __name__ == "__main__":
    main()
