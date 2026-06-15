# Deployment

Status: initial design.

## Local development

Planned local run:

```bash
uv sync
cp .env.example .env
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If `uv` is not used, plain `pip` installation may be documented later.

## Environment variables

See `.env.example`.

Important variables:

```text
YOLO_SERVICE_API_KEY
YOLO_SERVICE_MODEL_NAME
YOLO_SERVICE_MODEL_PATH
YOLO_SERVICE_CONFIDENCE
YOLO_SERVICE_IOU
YOLO_SERVICE_MAX_REQUEST_BYTES
YOLO_SERVICE_MAX_IMAGE_PIXELS
YOLO_SERVICE_ALLOW_EXTERNAL_IMAGE_URLS
```

## Docker

A CPU-only Dockerfile is planned before RC1.

Rules:

- no CUDA base image;
- no NVIDIA runtime requirement;
- API key passed by environment variable;
- expose port 8000 by default;
- do not bake secrets into image;
- model download/cache behavior must be documented.

Planned run:

```bash
docker build -t yolo-openai-vision-api .
docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=dev-secret-change-me \
  yolo-openai-vision-api
```

## Production warnings

The initial service is not production-certified.

Before public deployment, add or review:

- HTTPS/TLS termination;
- reverse proxy config;
- secret manager;
- rate limiting;
- request size limits at proxy and app;
- logging/metrics;
- vulnerability scanning;
- dependency/license review;
- abuse protections;
- CORS policy;
- public-browser auth design;
- operational runbook.

## No database in v0

The service has no persistence in v0. Restarting it should not lose durable project state because there is none.

## No Redis in v0

Redis is not required for synchronous CPU inference. It may be considered later for rate limiting, queues, or multi-worker coordination.
