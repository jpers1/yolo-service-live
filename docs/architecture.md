# Architecture

Status: initial design.

## Product shape

This project is a CPU-only object-detection inference gateway.

It exposes Ultralytics YOLO11n COCO detection through:

1. an OpenAI-compatible `/v1/chat/completions` endpoint;
2. a native computer-vision endpoint, `/v1/vision/detections`;
3. a later browser camera demo.

The service is not a general chatbot. It uses an OpenAI-shaped request/response envelope only to make existing OpenAI-style client code easy to adapt.

## High-level architecture

```text
OpenAI-style client or browser
        |
        v
FastAPI application
        |
        +--> auth and request validation
        |
        +--> OpenAI-compatible API adapter
        |
        +--> native vision API adapter
        |
        v
Detector service abstraction
        |
        v
Ultralytics YOLO11n on CPU
        |
        v
Structured COCO detections
```

## Planned internal modules

```text
app/
  main.py
  config.py
  auth.py

  api/
    health.py
    models.py
    openai_chat.py
    vision.py

  schemas/
    openai.py
    detections.py
    errors.py

  vision/
    image_decode.py
    detector.py
    fake_detector.py
    yolo_service.py
    postprocess.py

  web/
    static/
      index.html
      app.js
      style.css
```

## Runtime model

The service runs as a normal HTTP API process using Uvicorn.

No database is required for v0 because there is one static API key, no users, no quota accounting, and no persistence.

No Redis or queue is required for v0 because inference is synchronous and CPU-only. The browser live demo must use adaptive request pacing rather than queueing frames.

## Model lifecycle

Initial implementation may use a fake detector for API tests.

Real inference is introduced later by loading `yolo11n.pt` through Ultralytics. Model loading may happen lazily on first inference or during readiness startup; the final decision should be documented once implemented.

## OpenAI-compatible adapter

The OpenAI-compatible adapter should:

- accept `POST /v1/chat/completions`;
- accept model `yolo11n-coco`;
- parse `messages`;
- find one `image_url` content part;
- decode base64 `data:image/...;base64,...`;
- call the detector service;
- return an OpenAI-shaped response envelope;
- place structured detection JSON in `choices[0].message.content`.

Current implementation path:

```text
chat endpoint -> image decoder -> detector interface -> fake detector
```

The detector is stored on FastAPI app state so tests and future runtime wiring can inject a different implementation. Real YOLO inference remains planned but is not implemented yet.

## Native vision endpoint

The native endpoint should be simpler than chat completions:

```text
POST /v1/vision/detections
```

It should accept an image data URL plus optional thresholds and return the detection payload directly.

## Browser demo

The browser demo is intentionally simple:

```text
camera -> canvas -> JPEG data URL -> /v1/vision/detections -> canvas overlay
```

It should not use React/Vite/Next.js in the first version. Plain HTML, CSS, and JavaScript are sufficient.

## CPU-only design implications

- Use `yolo11n.pt` as the default model.
- Keep input image sizes modest.
- Use adaptive low FPS in browser demo.
- Avoid request backlogs.
- Return 429 or 503 when too busy, once concurrency limits exist.
- Do not promise real-time 30 FPS on CPU.

## Durable architecture decisions

See `docs/decisions/`.
