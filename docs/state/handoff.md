# Strategic Handoff

Last updated: 2026-06-17

## Project

YOLO OpenAI Vision API.

## Human intent

Build a professional-grade CPU-only YOLO object-detection web service with an OpenAI-compatible API and later browser camera demo.

## Strategic decisions accepted

- Use Ultralytics YOLO11n as default.
- Expose public model name `yolo11n-coco`.
- CPU-only; no GPU/CUDA assumptions.
- Implement limited OpenAI-compatible `/v1/chat/completions`.
- Add native `/v1/vision/detections`.
- Use one static Bearer API key.
- Accept only base64 image data URLs in MVP.
- No database in v0.
- No Redis in v0.
- Browser demo uses repeated HTTP first.
- Use bounded, reviewable GPT-5.5 work units with strategic AI review before human merge.

## Durable files to read first

```text
AGENTS.md
docs/architecture.md
docs/api-contract.md
docs/openai-compatibility.md
docs/security.md
docs/roadmap.md
docs/state/project-state.md
docs/decisions/
```

## Current implementation state

The repository now has an importable FastAPI service skeleton with typed configuration loading, public health/readiness endpoints, Bearer authentication for protected `/v1` endpoints, `GET /v1/models`, `POST /v1/chat/completions`, native `POST /v1/vision/detections`, safe base64 JPEG/PNG decoding, a detector abstraction with fake and YOLO backends, Docker deployment baseline, browser demo baseline, local-image CLI demo, a full local check script, coverage baseline, and GitHub Actions CI.

Implemented in PR #2:

- `pyproject.toml`
- `app/__init__.py`
- `app/main.py`
- `tests/__init__.py`
- `tests/test_app_factory.py`
- a minimal `create_app()` FastAPI factory
- a module-level `app` instance
- a focused factory test

Implemented after the skeleton:

- `app/config.py`
- `app/api/health.py`
- `app/auth.py`
- `app/errors.py`
- `app/api/models.py`
- `app/api/chat.py`
- `app/api/demo.py`
- `app/api/detection_common.py`
- `app/api/vision.py`
- `app/schemas/openai.py`
- `app/schemas/detections.py`
- `app/schemas/vision.py`
- `app/vision/detector.py`
- `app/vision/fake_detector.py`
- `app/vision/image_decode.py`
- `app/vision/yolo_detector.py`
- `app/static/demo.html`
- `app/static/demo.css`
- `app/static/demo.js`
- `.github/workflows/ci.yml`
- `Dockerfile`
- `.dockerignore`
- `compose.yaml`
- `scripts/check.sh`
- `scripts/detect_image.py`
- `scripts/smoke_http_vision.py`
- `scripts/smoke_demo_static.py`
- `scripts/smoke_yolo.py`
- `scripts/smoke_chat_yolo.py`
- `scripts/smoke_vision_yolo.py`
- typed settings loaded from `YOLO_SERVICE_` environment variables and optional `.env`
- settings stored on `app.state.settings`
- public `/healthz`
- public `/readyz`
- Bearer authentication for protected `/v1` endpoints
- fail-closed behavior when server API key is missing
- OpenAI-like error responses for auth/config failures
- protected `GET /v1/models`
- protected `POST /v1/chat/completions`
- protected native `POST /v1/vision/detections`
- OpenAI-like chat request/response schemas
- native vision request schema
- mocked detector response marked with `"mock": true`
- detector abstraction for decoded images
- fake detector object stored on `app.state.detector`
- chat-completions endpoint calls the detector interface
- real YOLO11n CPU detector backend available through `YOLO_SERVICE_DETECTOR_BACKEND=yolo`
- YOLO detector loads Ultralytics lazily on first detection
- optional `yolo` dependency extra for manual/runtime real inference
- manual real-model smoke script
- manual API-level YOLO chat-completions smoke script
- manual native YOLO vision smoke script
- Docker fake-backend image build path
- optional manual YOLO Docker build path
- Compose fake-backend baseline
- HTTP smoke script for running service/container
- CI fake-backend Docker smoke job
- browser demo at `GET /demo`
- browser demo static assets under `/demo-static/`
- browser demo native endpoint loop with one in-flight request maximum
- browser demo route tests and static smoke script
- local-image CLI demo for sending JPEG/PNG files from disk to `/v1/vision/detections`
- local-image CLI helper tests
- real YOLO runtime verified locally on CPU with generated 64x64 JPEG smoke inputs
- image URL content part extraction
- safe base64 JPEG/PNG data URL decoding
- MIME allowlist validation
- declared MIME versus decoded image format validation
- payload and pixel limit enforcement
- decoded image metadata in the mocked chat response source
- full local verification script running pytest, Ruff, and diff whitespace checks
- CI running Ruff plus pytest coverage on pull requests and pushes to `main`
- coverage baseline for `app` with 80% threshold
- focused auth tests
- focused chat-completions contract tests
- focused config tests
- focused detection schema tests
- focused error helper tests
- focused health/readiness endpoint tests
- focused image decoding tests
- focused model-list tests
- focused native vision detection tests

Normal CI avoids real YOLO downloads by using fake detectors and fake YOLO model objects. CI also builds and smokes the fake-backend Docker image. Manual smoke verification on 2026-06-15 completed direct detector and chat-completions YOLO runtime paths with `mock=false` in the API response.

## Next step

Select the next RC1 hardening slice after strategic review. Browser manual camera
validation, streaming/WebSocket, and production browser authentication/session design
remain unimplemented.

## Warning for future agents

Do not start by generating the whole service. This project must be built in bounded, evidence-backed PRs.

No architecture change has been made; the service is still planned as a CPU-only YOLO11 OpenAI-compatible API.
