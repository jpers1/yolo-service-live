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
- Split tasks into micro-PRs for GPT-5.4-mini execution agent.

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

The repository now has an importable FastAPI skeleton on `main`.

Implemented in PR #2:

- `pyproject.toml`
- `app/__init__.py`
- `app/main.py`
- `tests/__init__.py`
- `tests/test_app_factory.py`
- a minimal `create_app()` FastAPI factory
- a module-level `app` instance
- a focused factory test

No API endpoints, configuration layer, auth, image decoding, or detector logic exist yet.

## Next step

Add configuration loading only in the next PR. Do not add endpoints yet.

## Warning for future agents

Do not start by generating the whole service. This project must be built in narrow, evidence-backed PRs.

No architecture change has been made; the service is still planned as a CPU-only YOLO11 OpenAI-compatible API.
