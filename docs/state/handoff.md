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

No application code yet. Initial docs and constitution are being inserted.

## Next step

Insert the generated files into the repository, commit them, then proceed to PR 1.1 from `docs/roadmap.md`.

## Warning for future agents

Do not start by generating the whole service. This project must be built in narrow, evidence-backed PRs.
