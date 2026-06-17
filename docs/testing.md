# Testing Strategy

Status: active baseline.

## Testing principle

Most automated tests should not require downloading or running the real YOLO model. Use fake detector tests for API behavior, schema stability, auth, image decoding, and error handling.

Real YOLO tests are integration or manual smoke tests unless CI is explicitly configured to cache/download the model.

## Test categories

### Unit tests

Planned areas:

- config loading;
- auth parsing;
- constant-time key comparison where practical;
- base64 data URL parsing;
- MIME validation;
- image dimension validation;
- detection schema conversion;
- error object formatting.

### API tests

Planned endpoints:

- `/healthz`;
- `/readyz`;
- `/v1/models`;
- `/v1/chat/completions`;
- `/v1/vision/detections`.

Use FastAPI test client or HTTPX.

### Fake-detector tests

The fake detector should return deterministic detections.

It lets tests prove:

- request parsing;
- detector invocation;
- response envelope shape;
- assistant content JSON;
- native endpoint response shape.

### Real YOLO smoke tests

Manual or integration tests should prove:

- `yolo11n.pt` loads on CPU;
- a sample image produces detections;
- postprocessing works against real Ultralytics outputs.

These tests may be skipped in CI unless explicitly enabled.

The current direct detector smoke command is:

```bash
python -m pip install -e ".[dev,yolo]"
python scripts/smoke_yolo.py
```

The current API-level chat-completions smoke command is:

```bash
python -m pip install -e ".[dev,yolo]"
python scripts/smoke_chat_yolo.py
```

The current native vision endpoint smoke command is:

```bash
python -m pip install -e ".[dev,yolo]"
python scripts/smoke_vision_yolo.py
```

These scripts may trigger model download on first run. They are not part of normal CI.

Last local verification on 2026-06-15 completed both manual YOLO smokes against a generated 64x64 JPEG image. The direct detector smoke and API chat smoke both completed on CPU with `detections=0`; the API smoke verified `mock=false`.

### Docker smoke tests

The HTTP smoke script verifies a running service over real HTTP with a generated
in-memory image:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

Normal CI builds the Docker image with the fake detector path and runs this smoke against a container. CI does not install YOLO extras and does not download model weights.

Manual YOLO Docker smoke is optional:

```bash
docker build -t yolo-service-live:yolo --build-arg INSTALL_TARGET='.[yolo]' .
docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=yolo \
  yolo-service-live:yolo
```

Then run `scripts/smoke_http_vision.py` with the same API key.

### Local-image CLI demo tests

`scripts/detect_image.py` is a user-facing command-line demo. Unlike the smoke scripts,
it loads a local JPEG or PNG file from disk, encodes it as a base64 data URL, and sends
it to `POST /v1/vision/detections`.

Usage:

```bash
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/detect_image.py ./example.jpg --base-url http://127.0.0.1:8000
```

Helper-level tests cover local image encoding, unsupported image rejection, request
construction, summary printing, OpenAI-like error handling, and avoiding API key/base64
payload output:

```bash
python -m pytest tests/test_detect_image_script.py
```

### Internet-image boss demo tests

`scripts/demo_api_internet_image.py` is a user-facing demo script for boss demos. It
downloads a fixed public image client-side, validates it as JPEG or PNG with Pillow,
base64-encodes it, and calls `POST /v1/vision/detections`.

Usage against a running local or Docker service:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/demo_api_internet_image.py
```

Normal CI does not depend on internet access. Tests monkeypatch network calls and cover
the default image URL, JPEG/PNG encoding, unsupported content rejection, request
construction, safe summary/error output, and network error handling:

```bash
python -m pytest tests/test_demo_api_internet_image.py
```

### Browser demo tests

The browser demo baseline has static route tests:

```bash
python -m pytest tests/test_demo_page.py
```

The static smoke script verifies `/demo` and local assets without requiring a real camera:

```bash
python scripts/smoke_demo_static.py
```

When `YOLO_SERVICE_BASE_URL` is set, the smoke checks a running HTTP service. Without a
running service, it falls back to FastAPI `TestClient`.

CI runs the demo static smoke against the fake-backend Docker container.

No real camera access is required in CI.

Later optional tests:

- canvas overlay logic can be unit-tested separately if worthwhile.
- headless browser rendering with fake media devices.

## Required commands

Run the full local verification command before every implementation PR report unless a work order explicitly says otherwise:

```bash
scripts/check.sh
```

The script runs:

```bash
python -m pytest
ruff check app tests
git diff --check
```

Focused tests are useful during development, for example:

```bash
python -m pytest tests/test_auth.py
```

Focused tests are not enough for the final PR report unless the work order explicitly narrows verification.

CI runs lint plus full tests with coverage:

```bash
ruff check app tests
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Optional later:

```bash
mypy app
pytest -m integration
```

## Coverage

Coverage is measured for `app`.

The initial required threshold is 80%:

```bash
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

Raise the threshold only when the codebase and tests make that realistic without gaming coverage.

## Reporting vocabulary

Reports must distinguish:

- passed;
- failed;
- skipped;
- not run;
- blocked.

Do not report skipped tests as passed.

Skipped tests and tests that were not run are not passing tests.

## Minimum CI for early repository

CI runs on pull requests and pushes to `main`.

The baseline workflow runs:

```bash
ruff check app tests
python -m pytest --cov=app --cov-report=term-missing --cov-fail-under=80
docker build -t yolo-service-live:fake --build-arg INSTALL_TARGET=. .
python scripts/smoke_http_vision.py
python scripts/smoke_demo_static.py
```

Real model download should not be mandatory in first CI unless explicitly planned.

The current CI intentionally installs only:

```bash
python -m pip install -e ".[dev]"
```

YOLO-specific behavior is covered by tests with fake model objects. This keeps CI fast and avoids network/model-download dependency.

## Test data

Use small synthetic images where possible.

Do not commit large images unless necessary. If sample images are added, document license/source.
