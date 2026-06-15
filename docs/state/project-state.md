# Project State

Last updated: 2026-06-15

## Current truth

The repository now has an importable FastAPI service skeleton with typed configuration loading, public health/readiness endpoints, Bearer authentication for protected `/v1` endpoints, `GET /v1/models`, `POST /v1/chat/completions` with safe base64 JPEG/PNG decoding, a detector abstraction, configurable fake/YOLO detector backends, a full local check script, coverage baseline, and GitHub Actions CI.

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

Current baseline merge commit:

```text
b47e492a3118050e387feadef892f5b5f180fe97
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

Phase 6: Real YOLO.

## Implemented

- `AGENTS.md`
- `README.md`
- `.env.example`
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
- `app/__init__.py`
- `app/api/__init__.py`
- `app/api/chat.py`
- `app/api/health.py`
- `app/api/models.py`
- `app/auth.py`
- `app/config.py`
- `app/errors.py`
- `app/main.py`
- `app/schemas/__init__.py`
- `app/schemas/detections.py`
- `app/schemas/openai.py`
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
- `tests/test_detection_schema.py`
- `tests/test_errors.py`
- `tests/test_health.py`
- `tests/test_image_decode.py`
- `tests/test_models.py`
- `tests/test_yolo_detector.py`
- `scripts/smoke_yolo.py`
- `scripts/smoke_chat_yolo.py`
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
- OpenAI-like chat request and response schemas
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
- foundational runtime and test dependencies plus Pillow for safe image decoding
- optional `yolo` extra for Ultralytics

## Not implemented yet

- Native detection endpoint.
- Docker.
- Browser demo.

## Current hard constraints

- CPU-only.
- YOLO11n default.
- One Bearer API key.
- No database.
- No Redis.
- No arbitrary external image URL fetching in MVP.
- No image persistence.
- Browser demo later.
- GPT-5.5 work units must remain bounded, reviewable, and evidence-backed.
- Every PR must pass through strategic AI review before human merge.

## Next recommended task

Add native `/v1/vision/detections` endpoint using the existing image decoder and detector abstraction.

Suggested branch:

```text
feature/012-native-vision-detections
```

Suggested commit message:

```text
Add native vision detections endpoint
```
