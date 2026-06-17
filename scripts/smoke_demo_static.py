#!/usr/bin/env python

import os
from dataclasses import dataclass
from typing import Protocol
from urllib.request import urlopen


BASE_URL = os.getenv("YOLO_SERVICE_BASE_URL")


class DemoClient(Protocol):
    def get_text(self, path: str) -> str:
        ...


@dataclass(frozen=True)
class HttpDemoClient:
    base_url: str

    def get_text(self, path: str) -> str:
        with urlopen(f"{self.base_url.rstrip('/')}{path}", timeout=10) as response:
            _assert(response.status == 200, f"{path} returned HTTP {response.status}")
            return response.read().decode("utf-8")


class TestClientDemoClient:
    def __init__(self) -> None:
        from fastapi.testclient import TestClient

        from app.config import Settings
        from app.main import create_app
        from app.vision.fake_detector import FakeDetector

        self._client = TestClient(
            create_app(
                Settings(api_key="demo-smoke-key", detector_backend="fake", _env_file=None),
                detector=FakeDetector(),
            )
        )

    def get_text(self, path: str) -> str:
        response = self._client.get(path)
        _assert(response.status_code == 200, f"{path} returned HTTP {response.status_code}")
        return response.text


def main() -> None:
    client = _client()
    html = client.get_text("/demo")
    css = client.get_text("/demo-static/demo.css")
    js = client.get_text("/demo-static/demo.js")
    combined = f"{html}\n{css}\n{js}"

    _assert("/demo-static/demo.css" in html, "demo CSS is not referenced")
    _assert("/demo-static/demo.js" in html, "demo JS is not referenced")
    _assert("getUserMedia" in js, "demo JS does not request camera access")
    _assert("/v1/vision/detections" in js, "demo JS does not call native endpoint")
    _assert("Start camera" in html, "start control missing")
    _assert("Stop camera" in html, "stop control missing")
    _assert("Local/demo use only" in html, "API key warning missing")
    _assert("change-me-local-dev-key" not in combined, "hardcoded demo key found")
    _assert("http://" not in combined, "remote or absolute HTTP URL found")
    _assert("https://" not in combined, "remote or absolute HTTPS URL found")

    print("demo_page=ok")
    print("demo_css=ok")
    print("demo_js=ok")
    print("demo_static_smoke_completed=true")


def _client() -> DemoClient:
    if BASE_URL:
        return HttpDemoClient(BASE_URL)
    return TestClientDemoClient()


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


if __name__ == "__main__":
    main()
