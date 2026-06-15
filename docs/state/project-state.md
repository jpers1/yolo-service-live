# Project State

Last updated: 2026-06-15

## Current truth

The repository now has an importable FastAPI skeleton on `main`.

Merged PR #2 added the minimal Python backend project structure and app factory, but no API behavior yet.

Current baseline merge commit:

```text
ba88f8f9f434873afe41540bc3899c07a902cb2b
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
- `app/main.py`
- `tests/__init__.py`
- `tests/test_app_factory.py`
- minimal FastAPI app factory
- module-level `app`
- focused app-factory test
- foundational runtime and test dependencies only

## Not implemented yet

- Configuration loading.
- Auth.
- Health endpoints.
- OpenAI-compatible endpoints.
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
- Micro-PRs suitable for GPT-5.4-mini execution agent.

## Next recommended task

Add configuration loading only.

After that, add health and readiness endpoints.

Suggested branch:

```text
feature/003-config-loading
```

Suggested commit message:

```text
Add config loading
```
