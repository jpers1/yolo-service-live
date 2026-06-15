# Project State

Last updated: 2026-06-15

## Current truth

The repository now has an importable FastAPI service skeleton with typed configuration loading and public health/readiness endpoints.

Merged PR #2 added the minimal Python backend project structure and app factory, but no API behavior yet.

Merged PR #3 synchronized durable state docs with the FastAPI skeleton baseline.

Merged PR #4 added the strategic review gate and GPT-5.5 work-unit sizing policy.

Current baseline merge commit:

```text
88e5c58d473f39aa05705ddf036081761209efd1
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

Phase 1: FastAPI shell.

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
- `pyproject.toml`
- `app/__init__.py`
- `app/api/__init__.py`
- `app/api/health.py`
- `app/config.py`
- `app/main.py`
- `tests/__init__.py`
- `tests/test_app_factory.py`
- `tests/test_config.py`
- `tests/test_health.py`
- minimal FastAPI app factory
- module-level `app`
- typed settings loaded from `YOLO_SERVICE_` environment variables and optional `.env`
- settings stored on `app.state.settings`
- public `/healthz`
- public `/readyz`
- focused app-factory test
- focused config tests
- focused health/readiness endpoint tests
- foundational runtime and test dependencies only

## Not implemented yet

- Auth.
- `/v1/models`.
- `/v1/chat/completions`.
- Image decoding.
- Detector abstraction.
- Real YOLO inference.
- Native detection endpoint.
- Docker.
- Browser demo.
- CI.

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

Add Bearer authentication plus `/v1/models`.

Suggested branch:

```text
feature/005-auth-and-models
```

Suggested commit message:

```text
Add auth and model listing
```
