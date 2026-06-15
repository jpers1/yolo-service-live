# AGENTS.md

## Mission

This repository implements a professional-grade, CPU-only web service for YOLO11 COCO object detection with an OpenAI-compatible API surface.

The first supported model is `yolo11n.pt`, exposed publicly as `yolo11n-coco`.

The service must allow an OpenAI-style client to set:

```text
base_url = "http://<host>:<port>/v1"
api_key = "<single service API key>"
model = "yolo11n-coco"
```

and send a base64 image through a `/v1/chat/completions`-style request. The service returns structured object detections, not natural-language guessing.

## Product identity

This is an object-detection inference service, not a general chatbot, not a SaaS platform, not a billing gateway, and not an LLM proxy.

The OpenAI compatibility target is transport and envelope compatibility for image-based chat-completions requests. The inner assistant content is JSON containing YOLO detections.

## Current hard constraints

- CPU-only. Do not add CUDA, NVIDIA runtime, GPU-specific Docker bases, or GPU-only dependencies.
- Default detector: Ultralytics YOLO11n loaded from `yolo11n.pt`.
- Public model name: `yolo11n-coco`.
- Dataset/classes: COCO 80-class pretrained detector.
- API auth: one static API key using `Authorization: Bearer <key>`.
- MVP image input: base64 `data:image/jpeg;base64,...` and `data:image/png;base64,...`.
- MVP must not fetch arbitrary external image URLs.
- No database in v0.
- No Redis, Celery, queues, Kubernetes, user accounts, billing, or admin UI in v0.
- No image persistence unless a future explicit task changes this.
- Browser demo comes after backend MVP.
- Browser live mode must be CPU-honest: adaptive low FPS and no unbounded frame queue.

## Strategic architecture

Planned backend stack:

- Python 3.11+
- FastAPI
- Pydantic / pydantic-settings
- Uvicorn
- Ultralytics
- PyTorch CPU
- Pillow
- NumPy
- OpenCV headless where useful
- pytest
- httpx
- ruff
- Docker CPU image

Planned API surface:

```text
GET  /healthz
GET  /readyz
GET  /v1/models
POST /v1/chat/completions
POST /v1/vision/detections
GET  /demo                 # later browser demo
```

Optional later API surface:

```text
WebSocket /v1/vision/detections/stream
```

## Repository truth and documentation

The repository is the durable source of truth. Chat history and execution-agent context are not authoritative.

Before changing architecture, read:

```text
docs/architecture.md
docs/api-contract.md
docs/openai-compatibility.md
docs/security.md
docs/roadmap.md
docs/state/project-state.md
docs/decisions/*.md
```

Update the relevant docs when behavior changes. Do not leave docs claiming behavior that code does not implement.

## Execution-agent capability assumption

The default execution coding agent is expected to be a small/medium model, currently planned as GPT-5.4-mini. Therefore tasks must be narrow and explicit.

One PR should normally implement one behavior.

Preferred PR size:

- 1-5 files changed
- 50-250 lines of application code
- focused tests only
- no architectural invention
- no broad refactors unless explicitly requested

Do not combine API contract, image decoding, YOLO inference, browser UI, Docker, and documentation in one PR.

## Required workflow

For implementation tasks:

1. Read this `AGENTS.md`.
2. Read relevant docs under `docs/`.
3. Start from current `main`.
4. Verify working tree state before editing.
5. Create a feature branch.
6. Make the smallest scoped change.
7. Add or update focused tests.
8. Run the requested tests and lint commands.
9. Commit only related files.
10. Push branch and open a PR if the environment supports it.
11. Do not merge your own PR.
12. Report exact evidence.

If live repository state differs from the prompt or docs, report the mismatch before making broad changes.

## Forbidden actions

Do not:

- add a database unless explicitly requested by the strategic layer;
- add Redis, Celery, Kafka, RabbitMQ, Kubernetes, or a job queue unless explicitly requested;
- add React, Vite, Next.js, or a large frontend framework for the first browser demo;
- add GPU/CUDA/NVIDIA-specific dependencies;
- fetch arbitrary external image URLs in MVP;
- log API keys;
- log full base64 images;
- store uploaded images;
- commit real secrets;
- commit `.env`;
- print credentials in tests, docs, logs, or examples;
- silently change public API schema;
- silently rename `yolo11n-coco`;
- claim full OpenAI API compatibility;
- claim production certification;
- report skipped tests as passed;
- weaken validation only to make tests pass.

## Security rules

- All `/v1/*` endpoints require `Authorization: Bearer <key>`.
- `/healthz` may be public.
- `/readyz` may be public but must not expose secrets.
- Use fake placeholders in docs and tests.
- Never include actual API keys in screenshots, examples, commits, or logs.
- Do not fetch external URLs in MVP; accept only base64 data URLs.
- Enforce maximum request size, decoded image dimensions, and allowed MIME types.
- Prefer fail-closed behavior.
- Return structured OpenAI-like errors.
- Do not persist images or request bodies.
- Do not store user data.
- Use safe CORS defaults and document changes.

## OpenAI compatibility rules

The compatibility target is limited and explicit.

Required:

- `/v1/models` lists `yolo11n-coco`.
- `/v1/chat/completions` accepts OpenAI-style `messages`.
- It supports content parts of type `text` and `image_url`.
- The `image_url.url` field supports base64 data URLs for JPEG and PNG.
- Response is an OpenAI-shaped chat-completion envelope.
- Assistant message `content` is a JSON string containing detections.

Not required for MVP:

- general language chatting;
- tool calls;
- embeddings;
- audio;
- full OpenAI error parity;
- multi-user organization/project semantics;
- billing/token accounting;
- arbitrary image URL fetching;
- `stream: true`.

If a field is accepted but ignored, document it.

## Detection schema rules

Detections should include at least:

```json
{
  "class_id": 0,
  "class_name": "person",
  "confidence": 0.91,
  "box_xyxy": [102.4, 55.2, 310.1, 460.8],
  "box_xywh": [102.4, 55.2, 207.7, 405.6],
  "box_normalized_xyxy": [0.16, 0.12, 0.48, 0.96]
}
```

Detection results should include image metadata:

```json
{
  "task": "object_detection",
  "model": "yolo11n-coco",
  "image": {"width": 640, "height": 480},
  "thresholds": {"confidence": 0.25, "iou": 0.7},
  "detections": []
}
```

## Testing requirements

Use fake detector tests for normal CI. Real YOLO model tests may be manual or integration tests because model download and runtime can be slow or unavailable in CI.

Every behavior PR should include focused tests.

Minimum test areas:

- config loading;
- auth success/failure;
- `/v1/models`;
- OpenAI-style request parsing;
- image content extraction;
- base64 data URL decoding;
- MIME validation;
- image size/payload limits;
- detection schema formatting;
- mocked detector API response;
- OpenAI-shaped errors.

A test that was not run is not evidence. A skipped test is not a passing test.

## Documentation requirements

Update docs when behavior changes.

Docs that commonly need updates:

```text
README.md
docs/api-contract.md
docs/openai-compatibility.md
docs/security.md
docs/testing.md
docs/deployment.md
docs/browser-demo.md
docs/roadmap.md
docs/state/project-state.md
docs/state/rc1-readiness.md
```

Do not overclaim. Use terms such as "planned", "implemented", "tested", "manual-only", "post-RC1" precisely.

## Final report format

Every execution-agent task must end with:

```markdown
## Agent Report

Branch:
Commit:
PR:

## Summary
- ...

## Files changed
- ...

## Tests run
- `command`: result

## Documentation impact
- ...

## Safety confirmations
- No real secrets committed.
- No API keys logged.
- No image payload persistence added.
- No unrelated files changed.
- No skipped tests reported as passed.

## Known limitations or blockers
- ...

## Recommended next step
- ...
```

## Definition of done for a PR

A PR is done only when:

- scope matches the work order;
- tests were added or updated where appropriate;
- focused tests pass or blockers are explicitly reported;
- lint passes if configured;
- docs are updated or explicitly not needed;
- no unrelated files are changed;
- no forbidden actions occurred;
- final report includes evidence.

## Current status

Initial repository constitution. No application code is assumed to exist yet.

See `docs/state/project-state.md` for current project truth.
