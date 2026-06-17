# Deployment

Status: Docker baseline.

## Boss demo quickstart

For a short Docker-based demo covering container start, an internet-image API test, and
the browser camera demo, see:

```text
QUICKSTART.md
```

## Local development

Install the lightweight development dependencies and run with the fake detector:

```bash
python -m pip install -e ".[dev]"
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
YOLO_SERVICE_DETECTOR_BACKEND=fake \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Run the HTTP smoke from another shell:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

Open the browser demo at:

```text
http://127.0.0.1:8000/demo
```

Enter the API key in the browser page only for local/demo use.

Use the local-image CLI demo against the running service:

```bash
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/detect_image.py ./example.jpg --base-url http://127.0.0.1:8000
```

The script supports local `.jpg`, `.jpeg`, and `.png` files. It sends the image to
`POST /v1/vision/detections` and prints a concise detection summary.

## Environment variables

See `.env.example`.

Important variables:

```text
YOLO_SERVICE_API_KEY
YOLO_SERVICE_DETECTOR_BACKEND
YOLO_SERVICE_PUBLIC_MODEL_NAME
YOLO_SERVICE_MODEL_WEIGHTS
YOLO_SERVICE_DEFAULT_CONFIDENCE
YOLO_SERVICE_MAX_REQUEST_BYTES
YOLO_SERVICE_MAX_IMAGE_PIXELS
```

Do not commit `.env` or real secrets.

## Docker fake-backend baseline

The default container path installs only the base package and uses the fake detector. It is CI-safe and does not install Ultralytics or download YOLO weights.

```bash
docker build -t yolo-service-live:fake --build-arg INSTALL_TARGET=. .
docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=fake \
  yolo-service-live:fake
```

Smoke the running container:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

The running container also serves the browser demo:

```text
http://127.0.0.1:8000/demo
```

Static demo assets can be checked with:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
python scripts/smoke_demo_static.py
```

The local-image CLI demo can target the same container:

```bash
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/detect_image.py ./example.jpg --base-url http://127.0.0.1:8000
```

The internet-image API demo downloads a fixed public image client-side and sends it to
the same endpoint:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/demo_api_internet_image.py
```

The service does not fetch the internet image URL. The client script downloads and
base64-encodes the image before calling the API.

## Compose

The default Compose service uses the fake detector:

```bash
docker compose up --build
```

Then run:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

The Compose service also serves `/demo`.

## Manual YOLO container

The YOLO build path is manual and heavier:

```bash
docker build -t yolo-service-live:yolo --build-arg INSTALL_TARGET='.[yolo]' .
docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=yolo \
  -e YOLO_SERVICE_MODEL_WEIGHTS=yolo11n.pt \
  yolo-service-live:yolo
```

Smoke it with:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/smoke_http_vision.py
```

First YOLO inference may download `yolo11n.pt`. PyPI may pull large Torch runtime wheels, including CUDA-named wheels, even though this service forces inference to CPU.

The browser demo can target the YOLO-backed container, but first inference may be slow
because the model may download and CPU inference is synchronous.

## Healthcheck

The Docker image includes a healthcheck against:

```text
GET /healthz
```

`/healthz` and `/readyz` are public. All `/v1/*` endpoints remain authenticated.

## Container security baseline

- The image uses a Python slim base.
- The app runs as a non-root user.
- API keys must be passed at runtime as environment variables.
- `.env` is excluded from the Docker build context.
- Uploaded image bytes are decoded in memory only and are not persisted.
- External image URL fetching remains unsupported.
- No GPU, CUDA runtime, or NVIDIA container runtime is required.

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
