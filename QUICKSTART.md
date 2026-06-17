# Quickstart: Docker Boss Demo

## What this demo proves

- Docker container starts.
- API accepts image input.
- Python client can download an image from the internet, encode it as base64, and call `/v1/vision/detections`.
- Browser demo can capture a camera frame and submit it to the service.

## What this demo does not prove

- Production auth.
- Public internet deployment.
- Streaming/WebSocket.
- High-FPS performance.

## 1. Start Docker With The Fake Backend

Use the fake backend for the fastest boss demo:

```bash
docker build -t yolo-service-live:fake --build-arg INSTALL_TARGET=. .
docker run --rm -p 8000:8000 \
  -e YOLO_SERVICE_API_KEY=change-me-local-dev-key \
  -e YOLO_SERVICE_DETECTOR_BACKEND=fake \
  yolo-service-live:fake
```

The fake backend returns `mock=true`. It proves API and browser wiring, not real YOLO inference.

## 2. Test The API With An Internet Image

The service does not fetch external image URLs. This client-side snippet downloads the image,
encodes it as a base64 data URL, and sends that data URL to the service.

Run it from a Python environment with Pillow installed, for example:

```bash
python -m pip install -e ".[dev]"
```

```bash
python - <<'PY'
import base64
import json
from io import BytesIO
from urllib.request import Request, urlopen

from PIL import Image

base_url = "http://127.0.0.1:8000"
api_key = "change-me-local-dev-key"
image_url = "https://raw.githubusercontent.com/ultralytics/yolov5/master/data/images/bus.jpg"

with urlopen(Request(image_url, headers={"User-Agent": "yolo-service-live-demo/0.1"}), timeout=30) as response:
    image_bytes = response.read()

with Image.open(BytesIO(image_bytes)) as image:
    image.load()
    mime_type = {"JPEG": "image/jpeg", "PNG": "image/png"}[image.format]

encoded = base64.b64encode(image_bytes).decode("ascii")
payload = {
    "model": "yolo11n-coco",
    "image": {"url": f"data:{mime_type};base64,{encoded}"},
}
request = Request(
    f"{base_url}/v1/vision/detections",
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    method="POST",
)
with urlopen(request, timeout=30) as response:
    body = json.loads(response.read().decode("utf-8"))
    status = response.status

source = body["source"]
print(f"status={status}")
print(f"model={body['model']}")
print(f"mock={str(body['mock']).lower()}")
print(f"source={source['width']}x{source['height']} {source['mime_type']}")
print(f"detections={len(body['detections'])}")
PY
```

Or run the script version:

```bash
YOLO_SERVICE_BASE_URL=http://127.0.0.1:8000 \
YOLO_SERVICE_API_KEY=change-me-local-dev-key \
python scripts/demo_api_internet_image.py
```

Expected fake-backend output:

```text
status=200
model=yolo11n-coco
mock=true
source=<width>x<height> image/jpeg
detections=1
```

## 3. Try The Browser Camera Demo

Open:

```text
http://127.0.0.1:8000/demo
```

Steps:

1. Enter API key: `change-me-local-dev-key`.
2. Allow camera access.
3. Click start.
4. Verify that detections or status updates appear.
5. Click stop.

Do not expose this browser demo publicly with a shared API key.

Browser manual camera validation is not CI-automated. Static demo route smoke is automated.
If manual camera validation is performed, record it in the final report.

## Optional Real YOLO Backend

This is heavier and may download model weights or large Torch wheels. Use fake backend
for the fastest boss demo.

See `docs/deployment.md` for the manual YOLO Docker path.
