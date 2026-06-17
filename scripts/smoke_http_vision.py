#!/usr/bin/env python

import base64
import json
import os
from io import BytesIO
from typing import Any
from urllib.request import Request, urlopen

from PIL import Image


BASE_URL = os.getenv("YOLO_SERVICE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
API_KEY = os.getenv("YOLO_SERVICE_API_KEY", "change-me-local-dev-key")
MODEL = "yolo11n-coco"


def main() -> None:
    health = _get_json("/healthz")
    ready = _get_json("/readyz")
    models = _get_json("/v1/models", authenticated=True)
    vision = _post_json("/v1/vision/detections", _vision_request(), authenticated=True)

    _assert(health["status"] == "ok", "healthz status mismatch")
    _assert(ready["status"] == "ready", "readyz status mismatch")
    _assert(models["object"] == "list", "models object mismatch")
    _assert(any(model["id"] == MODEL for model in models["data"]), "expected model missing")
    _assert(vision["task"] == "object_detection", "vision task mismatch")
    _assert(vision["model"] == MODEL, "vision model mismatch")
    _assert(vision["source"]["decoded"] is True, "vision source is not decoded")
    _assert(isinstance(vision["detections"], list), "detections must be a list")
    _assert(isinstance(vision["mock"], bool), "mock must be a boolean")

    print("healthz=ok")
    print("readyz=ready")
    print("models=ok")
    print("vision_status=200")
    print(f"model={vision['model']}")
    print(f"mock={str(vision['mock']).lower()}")
    print(f"detections={len(vision['detections'])}")
    print("http_smoke_completed=true")


def _get_json(path: str, *, authenticated: bool = False) -> dict[str, Any]:
    request = Request(f"{BASE_URL}{path}", headers=_headers(authenticated=authenticated))
    with urlopen(request, timeout=10) as response:
        _assert(response.status == 200, f"{path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _post_json(path: str, payload: dict[str, Any], *, authenticated: bool = False) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    headers = _headers(authenticated=authenticated)
    headers["Content-Type"] = "application/json"
    request = Request(f"{BASE_URL}{path}", data=body, headers=headers, method="POST")
    with urlopen(request, timeout=30) as response:
        _assert(response.status == 200, f"{path} returned HTTP {response.status}")
        return json.loads(response.read().decode("utf-8"))


def _headers(*, authenticated: bool) -> dict[str, str]:
    if not authenticated:
        return {}
    return {"Authorization": f"Bearer {API_KEY}"}


def _vision_request() -> dict[str, Any]:
    return {
        "model": MODEL,
        "image": {"url": _jpeg_data_url(size=(64, 64))},
    }


def _jpeg_data_url(*, size: tuple[int, int]) -> str:
    buffer = BytesIO()
    Image.new("RGB", size, color=(255, 255, 255)).save(buffer, format="JPEG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    main()
