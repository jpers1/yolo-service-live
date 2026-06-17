# YOLO OpenAI Vision API

Status: backend API baseline.

This project implements a professional-grade, CPU-only YOLO11 object-detection web service with an OpenAI-compatible API surface.

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

## Implemented endpoints

```text
GET  /healthz
GET  /readyz
GET  /v1/models
POST /v1/chat/completions
POST /v1/vision/detections
GET  /demo
```

The browser demo is a local/internal plain HTML page for exercising the native endpoint.

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

## Local run

```bash
python -m pip install -e ".[dev]"
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
YOLO_SERVICE_DETECTOR_BACKEND=fake \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

In another terminal:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

Open the browser demo at:

```text
http://127.0.0.1:8000/demo
```

Enter the API key in the page only for local/demo use. Do not expose this demo with a
shared real API key on the public internet.

## Command-line local image demo

With a service running locally, send a JPEG or PNG file from disk to the native endpoint:

```bash
python -m pip install -e ".[dev]"
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/detect_image.py ./example.jpg --base-url http://127.0.0.1:8000
```

The script loads the local image file, encodes it as a base64 data URL, sends it to
`POST /v1/vision/detections`, and prints a concise detection summary. It does not print
the API key or base64 payload.

## Docker quickstart

The default Docker path uses the fake detector so it starts quickly and does not download YOLO weights:

```bash
docker build -t yolo-service-live:fake --build-arg INSTALL_TARGET=. .
docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=fake \
  yolo-service-live:fake
```

Then run:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

The same running container serves:

```text
http://127.0.0.1:8000/demo
```

The local-image CLI demo works against the Docker container too:

```bash
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/detect_image.py ./example.jpg --base-url http://127.0.0.1:8000
```

The YOLO Docker build is optional and heavier:

```bash
docker build -t yolo-service-live:yolo --build-arg INSTALL_TARGET='.[yolo]' .
```

First YOLO inference may download `yolo11n.pt`. PyPI may also pull large Torch runtime wheels, including CUDA-named wheels, even though inference is forced to CPU.

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
