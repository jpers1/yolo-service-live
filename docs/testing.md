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

These scripts may trigger model download on first run. They are not part of normal CI.

Last local verification on 2026-06-15 completed both manual YOLO smokes against a generated 64x64 JPEG image. The direct detector smoke and API chat smoke both completed on CPU with `detections=0`; the API smoke verified `mock=false`.

### Browser demo tests

Initial browser demo can be manually tested.

Later optional tests:

- static page loads;
- JavaScript sends request;
- canvas overlay logic can be unit-tested separately if worthwhile.

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
