# Project State

Last updated: 2026-06-17

## Current truth

The repository now has an importable FastAPI service skeleton with typed configuration loading, public health/readiness endpoints, Bearer authentication for protected `/v1` endpoints, `GET /v1/models`, `POST /v1/chat/completions`, native `POST /v1/vision/detections`, safe base64 JPEG/PNG decoding, a detector abstraction, configurable fake/YOLO detector backends, Docker deployment baseline, browser demo baseline, local-image CLI demo, boss-demo quickstart, a full local check script, coverage baseline, and GitHub Actions CI.

Merged PR #2 added the minimal Python backend project structure and app factory, but no API behavior yet.

Merged PR #3 synchronized durable state docs with the FastAPI skeleton baseline.

Merged PR #4 added the strategic review gate and GPT-5.5 work-unit sizing policy.

Merged PR #5 added typed configuration loading and public health/readiness endpoints.

Merged PR #6 added Bearer authentication, OpenAI-like auth/config errors, and protected `GET /v1/models`.

Merged PR #7 added the full local verification script, coverage baseline, and GitHub Actions CI.

Merged PR #8 added the protected `POST /v1/chat/completions` contract with a mocked detector response.

Merged PR #9 added safe base64 JPEG/PNG decoding, payload and pixel limits, and declared-MIME versus decoded-format validation.

Merged PR #10 added the detector abstraction and wired chat-completions through an app-state fake detector object.

Merged PR #11 added the lazy-loading YOLO11n CPU detector backend, optional `yolo` dependency extra, and direct manual YOLO smoke script.

Merged PR #12 added API-level YOLO chat smoke verification and documented local real-runtime evidence.

Merged PR #13 added the protected native `/v1/vision/detections` endpoint using the shared decoder and detector path.

Merged PR #14 added the Docker deployment baseline, Compose fake-backend baseline, HTTP smoke script, and CI fake-backend Docker smoke.

Merged PR #15 added the browser camera demo baseline and demo static smoke coverage.

Merged PR #16 added the local-image CLI demo for sending JPEG/PNG files from disk to the native endpoint.

Merged PR #17 added the Docker boss-demo quickstart and internet-image API demo script.

Current baseline merge commit:

```text
422d57fc309c525e99f38c7a89d6138abe0a0bce
```

## Product goal

Build a professional-grade, CPU-only YOLO11 object-detection web service with a limited OpenAI-compatible API surface.

## Default model

```text
yolo11n.pt
```

Public model name:

```text
yolo11n-coco
```

## Current phase

Phase 12: YOLO Docker runtime repair.

## Implemented

- `AGENTS.md`
- `README.md`
- `QUICKSTART.md`
- `.env.example`
- `.dockerignore`
- `Dockerfile`
- `compose.yaml`
- `docs/architecture.md`
- `docs/api-contract.md`
- `docs/openai-compatibility.md`
- `docs/security.md`
- `docs/model-card.md`
- `docs/performance.md`
- `docs/testing.md`
- `docs/deployment.md`
- `docs/browser-demo.md`
- `docs/roadmap.md`
- `docs/release-criteria.md`
- decision records
- state docs
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `scripts/check.sh`
- `scripts/detect_image.py`
- `scripts/demo_api_internet_image.py`
- `scripts/smoke_http_vision.py`
- `app/__init__.py`
- `app/api/__init__.py`
- `app/api/chat.py`
- `app/api/demo.py`
- `app/api/detection_common.py`
- `app/api/health.py`
- `app/api/models.py`
- `app/api/vision.py`
- `app/auth.py`
- `app/config.py`
- `app/errors.py`
- `app/main.py`
- `app/static/demo.html`
- `app/static/demo.css`
- `app/static/demo.js`
- `app/schemas/__init__.py`
- `app/schemas/detections.py`
- `app/schemas/openai.py`
- `app/schemas/vision.py`
- `app/vision/__init__.py`
- `app/vision/detector.py`
- `app/vision/fake_detector.py`
- `app/vision/image_decode.py`
- `app/vision/yolo_detector.py`
- `tests/__init__.py`
- `tests/test_auth.py`
- `tests/test_app_factory.py`
- `tests/test_chat_completions.py`
- `tests/test_config.py`
- `tests/test_demo_page.py`
- `tests/test_demo_api_internet_image.py`
- `tests/test_detect_image_script.py`
- `tests/test_detection_schema.py`
- `tests/test_errors.py`
- `tests/test_health.py`
- `tests/test_image_decode.py`
- `tests/test_models.py`
- `tests/test_vision_detections.py`
- `tests/test_yolo_detector.py`
- `scripts/smoke_yolo.py`
- `scripts/smoke_chat_yolo.py`
- `scripts/smoke_vision_yolo.py`
- `scripts/smoke_demo_static.py`
- minimal FastAPI app factory
- module-level `app`
- typed settings loaded from `YOLO_SERVICE_` environment variables and optional `.env`
- settings stored on `app.state.settings`
- public `/healthz`
- public `/readyz`
- Bearer authentication for protected `/v1` endpoints
- fail-closed behavior when server API key is missing
- minimal OpenAI-like error helper for auth/config failures
- protected `GET /v1/models`
- protected `POST /v1/chat/completions`
- protected native `POST /v1/vision/detections`
- OpenAI-like chat request and response schemas
- native vision detection request schema
- mocked detector response marked with `"mock": true`
- detector abstraction for decoded images
- fake detector object used by the chat-completions endpoint
- detector stored on `app.state.detector`
- configurable detector backend with `fake` and `yolo` modes
- real YOLO11n CPU detector backend loaded lazily on first inference
- YOLO backend uses configured model weights and confidence threshold
- YOLO backend returns `mock: false`
- manual real-model smoke script
- manual API-level YOLO chat-completions smoke script
- manual native YOLO vision smoke script
- Docker fake-backend image build path
- optional manual YOLO Docker build path
- OpenCV/Ultralytics native runtime libraries in the Docker image for YOLO backend use
- Compose fake-backend baseline
- HTTP smoke script for running service/container
- CI fake-backend Docker smoke job
- browser demo at `GET /demo`
- local browser demo static assets at `/demo-static/demo.css` and `/demo-static/demo.js`
- browser demo camera preview, JPEG capture, native endpoint calls, and overlay rendering
- browser demo request-after-response loop with one in-flight request maximum
- browser demo static route tests
- browser demo static smoke script
- local-image CLI demo for JPEG/PNG files on disk
- local-image CLI demo tests for encoding, request construction, summaries, and errors
- Docker boss-demo quickstart
- internet-image API demo script that downloads image data client-side
- internet-image demo tests using monkeypatched network calls
- real YOLO runtime verified locally on CPU with generated 64x64 JPEG smoke inputs
- image URL content part extraction
- safe base64 JPEG/PNG data URL decoding
- image MIME allowlist validation
- declared MIME versus decoded image format validation
- encoded image payload limit
- decoded image pixel limit
- decoded image metadata in mocked chat response source
- focused app-factory test
- focused auth tests
- focused chat-completions contract tests
- focused config tests
- focused detection schema tests
- focused detector abstraction tests
- focused error helper tests
- focused health/readiness endpoint tests
- focused image decoding tests
- focused model-list tests
- full local check script
- pytest coverage baseline for `app` with 80% threshold
- GitHub Actions CI for lint and coverage test suite
- GitHub Actions CI for fake-backend Docker build and HTTP smoke
- foundational runtime and test dependencies plus Pillow for safe image decoding
- optional `yolo` extra for Ultralytics

## Not implemented yet

- Streaming or WebSocket.
- Production browser auth/session design.

## Current hard constraints

- CPU-only.
- YOLO11n default.
- One Bearer API key.
- No database.
- No Redis.
- No arbitrary external image URL fetching in MVP.
- No image persistence.
- GPT-5.5 work units must remain bounded, reviewable, and evidence-backed.
- Every PR must pass through strategic AI review before human merge.

## Next recommended task

Select the next RC1 hardening slice after strategic review.

Suggested branch:

```text
feature/016-rc1-hardening
```

Suggested commit message:

```text
Harden RC1 demo readiness
```
