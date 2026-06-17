#!/usr/bin/env python

import argparse
import base64
import json
import os
import sys
from io import BytesIO
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError


DEFAULT_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_IMAGE_URL = "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/bus.jpg"
DEFAULT_MODEL = "yolo11n-coco"
FORMAT_TO_MIME_TYPE = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
}


class DemoError(RuntimeError):
    pass


def main() -> int:
    args = parse_args()
    try:
        api_key = resolve_api_key(args.api_key)
        image_bytes = download_image(args.image_url)
        image_data_url = image_bytes_to_data_url(image_bytes)
        status_code, response = post_detection(
            base_url=args.base_url,
            api_key=api_key,
            model=args.model,
            image_url=image_data_url,
        )
        if "error" in response:
            print_error(response)
            return 1
        print_summary(status_code=status_code, response=response)
        return 0
    except DemoError as exc:
        print(f"error_message={exc}", file=sys.stderr)
        return 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download a public image client-side and send it to /v1/vision/detections.",
    )
    parser.add_argument(
        "--image-url",
        default=DEFAULT_IMAGE_URL,
        help=f"Public JPEG/PNG image URL. Defaults to {DEFAULT_IMAGE_URL}.",
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("YOLO_SERVICE_BASE_URL", DEFAULT_BASE_URL),
        help="Service base URL. Defaults to YOLO_SERVICE_BASE_URL or http://127.0.0.1:8000.",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="Bearer API key. Defaults to YOLO_SERVICE_API_KEY when omitted.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Public model name. Defaults to {DEFAULT_MODEL}.",
    )
    return parser.parse_args()


def resolve_api_key(api_key: str | None) -> str:
    resolved = api_key or os.getenv("YOLO_SERVICE_API_KEY")
    if not resolved:
        raise DemoError("API key is required via --api-key or YOLO_SERVICE_API_KEY.")
    return resolved


def download_image(image_url: str) -> bytes:
    request = Request(
        image_url,
        headers={"User-Agent": "yolo-service-live-demo/0.1"},
    )
    try:
        with urlopen(request, timeout=30) as response:
            return response.read()
    except HTTPError as exc:
        raise DemoError(f"Image download failed with HTTP {exc.code}.") from exc
    except URLError as exc:
        raise DemoError(f"Image download failed: {exc.reason}") from exc


def image_bytes_to_data_url(image_bytes: bytes) -> str:
    try:
        with Image.open(BytesIO(image_bytes)) as image:
            image.load()
            mime_type = FORMAT_TO_MIME_TYPE.get(image.format or "")
    except UnidentifiedImageError as exc:
        raise DemoError("Downloaded content is not a valid JPEG or PNG image.") from exc

    if mime_type is None:
        raise DemoError("Downloaded image must be JPEG or PNG.")

    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def post_detection(
    *,
    base_url: str,
    api_key: str,
    model: str,
    image_url: str,
) -> tuple[int, dict[str, Any]]:
    payload = {
        "model": model,
        "image": {"url": image_url},
    }
    body = json.dumps(payload).encode("utf-8")
    request = Request(
        f"{base_url.rstrip('/')}/v1/vision/detections",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        return exc.code, load_error_body(exc)
    except URLError as exc:
        raise DemoError(f"API request failed: {exc.reason}") from exc


def print_summary(*, status_code: int, response: dict[str, Any]) -> None:
    source = response.get("source", {})
    detections = response.get("detections", [])
    print(f"status={status_code}")
    print(f"model={response.get('model')}")
    print(f"mock={str(response.get('mock')).lower()}")
    print(f"source={source.get('width')}x{source.get('height')} {source.get('mime_type')}")
    print(f"detections={len(detections)}")


def print_error(response: dict[str, Any]) -> None:
    error = response.get("error", {})
    print(f"error_code={error.get('code')}")
    print(f"error_message={error.get('message')}")


def load_error_body(exc: HTTPError) -> dict[str, Any]:
    try:
        return json.loads(exc.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {
            "error": {
                "code": f"http_{exc.code}",
                "message": "Server returned a non-JSON error response.",
            }
        }


if __name__ == "__main__":
    raise SystemExit(main())
