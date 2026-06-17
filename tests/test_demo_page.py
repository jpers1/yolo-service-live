from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from app.vision.fake_detector import FakeDetector


def _client() -> TestClient:
    return TestClient(
        create_app(
            Settings(api_key="test-key", detector_backend="fake", _env_file=None),
            detector=FakeDetector(),
        )
    )


def test_demo_page_returns_html_with_local_assets() -> None:
    response = _client().get("/demo")

    assert response.status_code == 200
    assert "/demo-static/demo.css" in response.text
    assert "/demo-static/demo.js" in response.text


def test_demo_static_assets_are_served() -> None:
    client = _client()

    js_response = client.get("/demo-static/demo.js")
    css_response = client.get("/demo-static/demo.css")

    assert js_response.status_code == 200
    assert css_response.status_code == 200
    assert "getUserMedia" in js_response.text
    assert "/v1/vision/detections" in js_response.text


def test_demo_has_start_stop_controls_and_api_key_warning() -> None:
    html = _client().get("/demo").text

    assert "Start camera" in html
    assert "Stop camera" in html
    assert "API key" in html
    assert "Local/demo use only" in html


def test_demo_does_not_hardcode_api_key_or_remote_assets() -> None:
    client = _client()
    html = client.get("/demo").text
    js = client.get("/demo-static/demo.js").text
    combined = f"{html}\n{js}"

    assert "change-me-local-dev-key" not in combined
    assert "ci-test-key" not in combined
    assert "test-key" not in combined
    assert "http://" not in combined
    assert "https://" not in combined
