# Testing Strategy

Status: initial design.

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

### Browser demo tests

Initial browser demo can be manually tested.

Later optional tests:

- static page loads;
- JavaScript sends request;
- canvas overlay logic can be unit-tested separately if worthwhile.

## Required commands

Once tooling exists, expected commands:

```bash
ruff check app tests
pytest
```

Optional later:

```bash
mypy app
pytest -m integration
```

## Reporting vocabulary

Reports must distinguish:

- passed;
- failed;
- skipped;
- not run;
- blocked.

Do not report skipped tests as passed.

## Minimum CI for early repository

CI should initially run:

```bash
ruff check
pytest
```

Real model download should not be mandatory in first CI unless explicitly planned.

## Test data

Use small synthetic images where possible.

Do not commit large images unless necessary. If sample images are added, document license/source.
