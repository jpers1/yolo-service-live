# Project State

Last updated: 2026-06-15

## Current truth

The repository now has an importable FastAPI service skeleton with typed configuration loading, public health/readiness endpoints, Bearer authentication for protected `/v1` endpoints, `GET /v1/models`, a full local check script, coverage baseline, and GitHub Actions CI.

Merged PR #2 added the minimal Python backend project structure and app factory, but no API behavior yet.

Merged PR #3 synchronized durable state docs with the FastAPI skeleton baseline.

Merged PR #4 added the strategic review gate and GPT-5.5 work-unit sizing policy.

Merged PR #5 added typed configuration loading and public health/readiness endpoints.

Merged PR #6 added Bearer authentication, OpenAI-like auth/config errors, and protected `GET /v1/models`.

Current baseline merge commit:

```text
d5b38c8f4badb71968ee89ed836c7baaf6d21423
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

Phase 2: Auth and model listing.

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
- `app/api/health.py`
- `app/api/models.py`
- `app/auth.py`
- `app/config.py`
- `app/errors.py`
- `app/main.py`
- `tests/__init__.py`
- `tests/test_auth.py`
- `tests/test_app_factory.py`
- `tests/test_config.py`
- `tests/test_errors.py`
- `tests/test_health.py`
- `tests/test_models.py`
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
- focused app-factory test
- focused auth tests
- focused config tests
- focused error helper tests
- focused health/readiness endpoint tests
- focused model-list tests
- full local check script
- pytest coverage baseline for `app` with 80% threshold
- GitHub Actions CI for lint and coverage test suite
- foundational runtime and test dependencies only

## Not implemented yet

- `/v1/chat/completions`.
- Image decoding.
- Detector abstraction.
- Real YOLO inference.
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

Add OpenAI chat-completions schemas plus mocked detector response.

Suggested branch:

```text
feature/006-chat-schemas-mocked-detector
```

Suggested commit message:

```text
Add chat schemas with mocked detector response
```
