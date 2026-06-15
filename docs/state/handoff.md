# Strategic Handoff

Last updated: 2026-06-15

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

The repository now has an importable FastAPI service skeleton with typed configuration loading, public health/readiness endpoints, Bearer authentication for protected `/v1` endpoints, and `GET /v1/models`.

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
- typed settings loaded from `YOLO_SERVICE_` environment variables and optional `.env`
- settings stored on `app.state.settings`
- public `/healthz`
- public `/readyz`
- Bearer authentication for protected `/v1` endpoints
- fail-closed behavior when server API key is missing
- OpenAI-like error responses for auth/config failures
- protected `GET /v1/models`
- focused auth tests
- focused config tests
- focused health/readiness endpoint tests
- focused model-list tests

No `/v1/chat/completions`, image decoding, or detector logic exists yet.

## Next step

Add OpenAI chat-completions schemas plus mocked detector response in the next PR. Do not add image decoding or YOLO inference yet.

## Warning for future agents

Do not start by generating the whole service. This project must be built in bounded, evidence-backed PRs.

No architecture change has been made; the service is still planned as a CPU-only YOLO11 OpenAI-compatible API.
