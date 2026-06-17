# Quickstart: Real YOLO Boss Test

This is the primary local demo path. It uses the real YOLO backend in Docker,
not the fake detector.

## What This Test Proves

- Docker image builds with YOLO extras.
- Real YOLO backend starts in Docker.
- OpenCV/Ultralytics native runtime libraries are present.
- API accepts image input and returns `mock=false`.
- The internet-image API test returns real detections.
- Browser demo can call the same real backend.
- First inference may download `yolo11n.pt`.

## What This Test Does Not Prove

- Production public deployment.
- Multi-user auth.
- GPU/CUDA acceleration.
- High-FPS performance guarantees.
- WebSocket/streaming.

## Prerequisites

- Docker installed and usable with `sudo docker`.
- Internet access may be needed for Python/Torch dependencies during build.
- Internet access may be needed for the first `yolo11n.pt` model-weight download.
- Host Python client scripts require Python 3.11+ with project dependencies installed.
- If host Python is older, the Docker server can still run; use a Python 3.11 virtual environment for the client script, or use the `curl` health check below to verify the container is serving HTTP.

Install the host-side client script dependencies if needed:

```bash
python -m pip install -e ".[dev]"
```

## Step 1 - Build Real YOLO Docker Image

```bash
sudo env DOCKER_BUILDKIT=1 docker build \
  -t yolo-service-live:yolo \
  --build-arg INSTALL_TARGET='.[yolo]' .
```

This can take several minutes because Torch and Ultralytics wheels are large.
The Dockerfile uses a BuildKit pip cache mount for repeated rebuilds. Do not use
`docker build --no-cache` for normal rebuilds; reserve it only for explicitly
debugging cache corruption.

## Step 2 - Run Real YOLO Backend

Primary command using host port `8000`:

```bash
sudo docker rm -f yolo-service-live-real-demo 2>/dev/null || true

sudo docker run --rm -p 8000:8000 \
  --name yolo-service-live-real-demo \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=yolo \
  -e YOLO_SERVICE_MODEL_WEIGHTS=yolo11n.pt \
  -e YOLO_SERVICE_DEFAULT_CONFIDENCE=0.25 \
  yolo-service-live:yolo
```

If port `8000` is occupied, use host port `8002`:

```bash
sudo docker rm -f yolo-service-live-real-demo 2>/dev/null || true

sudo docker run --rm -p 8002:8000 \
  --name yolo-service-live-real-demo \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=yolo \
  -e YOLO_SERVICE_MODEL_WEIGHTS=yolo11n.pt \
  -e YOLO_SERVICE_DEFAULT_CONFIDENCE=0.25 \
  yolo-service-live:yolo
```

If using host port `8002`, all client commands must use:

```text
http://127.0.0.1:8002
```

## Step 3 - Check Health

For port `8000`:

```bash
curl http://127.0.0.1:8000/healthz
```

For port `8002`:

```bash
curl http://127.0.0.1:8002/healthz
```

Expected result: HTTP 200 with `status` set to `ok`.

## Step 4 - Real API Test With Internet Image

The service does not fetch external image URLs. The client script downloads the
internet image, validates it locally, encodes it as a base64 data URL, and sends
that data URL to `POST /v1/vision/detections`.

For port `8000`:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/demo_api_internet_image.py
```

For port `8002`:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8002 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/demo_api_internet_image.py
```

Expected output includes:

```text
mock=false
detections=<non-zero number>
```

`mock=false` is the key proof that the real YOLO backend is running. A non-zero
detection count on the default bus image is expected. The first request may be
slower because model weights may download.

## Step 5 - Browser Camera Demo With Real YOLO

For port `8000`, open:

```text
http://127.0.0.1:8000/demo
```

For port `8002`, open:

```text
http://127.0.0.1:8002/demo
```

Steps:

1. Enter API key:

   ```text
   change-me-local-dev-key
   ```

2. Allow camera access.
3. Click start.
4. Aim camera at obvious COCO objects: person, chair, laptop, bottle, cup, book, keyboard, mouse, backpack, car, bicycle.
5. Confirm request status is OK.
6. Confirm detections appear, or confirm detection count changes.
7. If detections are zero, first verify the internet-image API test returns `mock=false` and non-zero detections.

Do not expose this browser demo publicly with a shared API key.

## Troubleshooting

### 401 Unauthorized

Meaning:

- API key missing or wrong in browser/client.

Fix:

- Enter exactly `change-me-local-dev-key`.
- Make sure container was started with `YOLO_SERVICE_API_KEY=change-me-local-dev-key`.

### 503 Service Unavailable

Meaning:

- Detector backend not available.

Check logs:

```bash
sudo docker logs yolo-service-live-real-demo
```

PR #18 fixed the known `libxcb.so.1` issue in the repository Dockerfile.

### `ImportError: libxcb.so.1`

Meaning:

- Old image is being used or Dockerfile/runtime libraries are missing.

Fix:

```bash
sudo env DOCKER_BUILDKIT=1 docker build \
  -t yolo-service-live:yolo \
  --build-arg INSTALL_TARGET='.[yolo]' .
```

Then rerun the real container. Use `--no-cache` only if you are explicitly
debugging Docker cache corruption.

### `mock=true`

Meaning:

- Fake backend is running, not real YOLO.

Fix:

- Ensure container is started with:

  ```bash
  -e YOLO_SERVICE_DETECTOR_BACKEND=yolo
  ```

- Ensure the image was built with:

  ```bash
  --build-arg INSTALL_TARGET='.[yolo]'
  ```

### No Detections In Browser

- Real YOLO may return zero detections if the camera view has no recognizable COCO object.
- First prove the real backend using the internet-image script.
- Then aim camera at person, chair, laptop, bottle, cup, book, keyboard, mouse, backpack, car, or bicycle.

### Boxes Extend Into Black Side Bands

This should be fixed. The browser overlay compensates for letterboxing and
pillarboxing by drawing boxes inside the actual displayed camera image rectangle,
not the full canvas.

## Optional Fallback: Fake Backend Wiring Smoke

This is not the boss test. It only proves service, API, and browser wiring. It
returns `mock=true`.

```bash
sudo docker build -t yolo-service-live:fake --build-arg INSTALL_TARGET=. .
sudo docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=fake \
  yolo-service-live:fake
```

Use the fake backend only for lightweight CI/developer smoke checks.
