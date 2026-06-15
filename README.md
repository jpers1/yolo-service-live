# YOLO OpenAI Vision API

Status: initial planning scaffold.

This project will implement a professional-grade, CPU-only YOLO11 object-detection web service with an OpenAI-compatible API surface.

The default model is planned to be:

```text
yolo11n.pt
```

The public API model name is planned to be:

```text
yolo11n-coco
```

## Goal

A client should be able to use an OpenAI-style SDK configuration:

```python
from openai import OpenAI

client = OpenAI(
    api_key="dev-secret",
    base_url="http://localhost:8000/v1",
)
```

and call `/v1/chat/completions` with a base64 image in an `image_url` content part. The service will return structured COCO object detections.

## Non-goals for v0

- No GPU requirement.
- No database.
- No Redis.
- No user accounts.
- No billing.
- No arbitrary external image URL fetching.
- No general chatbot behavior.
- No claim of full OpenAI API compatibility.
- No production certification.

## Planned endpoints

```text
GET  /healthz
GET  /readyz
GET  /v1/models
POST /v1/chat/completions
POST /v1/vision/detections
GET  /demo
```

The browser demo comes after the backend MVP.

## Planned stack

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- Ultralytics
- PyTorch CPU
- Pillow
- NumPy
- OpenCV headless
- pytest
- httpx
- ruff
- Docker

## Security model

All `/v1/*` endpoints require:

```http
Authorization: Bearer <YOLO_SERVICE_API_KEY>
```

The service must not log API keys, persist images, or fetch arbitrary external image URLs in MVP.

## Documentation

Important project state is stored in:

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

## Sources to periodically re-check

- Ultralytics YOLO11 documentation: https://docs.ultralytics.com/models/yolo11/
- OpenAI chat completions API reference: https://platform.openai.com/docs/api-reference/chat/create
- OpenAI image input guide: https://platform.openai.com/docs/guides/images-vision
- FastAPI documentation: https://fastapi.tiangolo.com/
