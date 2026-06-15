# Project State

Last updated: 2026-06-15

## Current truth

Initial repository state package generated.

No application code is assumed to exist yet.

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

Phase 0: governance and documentation.

## Implemented

Planned initial insertion:

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

## Not implemented yet

- Python project structure.
- FastAPI app.
- Auth.
- Health endpoints.
- OpenAI-compatible endpoints.
- Image decoding.
- Detector abstraction.
- Real YOLO inference.
- Tests.
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

Create the initial repository files from this package and commit them as the first governance/documentation commit.

Suggested branch:

```text
docs/initial-oap-constitution
```

Suggested commit message:

```text
Add initial OAP constitution and project state docs
```

## Next coding-agent task after insertion

PR 1.1: Add Python project structure with `pyproject.toml`, empty `app/`, empty `tests/`, and initial tooling configuration.

Do not implement FastAPI endpoints in the same PR.
