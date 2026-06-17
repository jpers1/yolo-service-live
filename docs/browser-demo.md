# Browser Demo

Status: implemented baseline.

## Goal

Provide a local/internal HTML5 demo where the browser:

1. asks for camera access;
2. displays the camera preview;
3. captures frames to a canvas;
4. sends JPEG data URLs to `/v1/vision/detections`;
5. draws returned YOLO boxes and labels over the video/canvas.

## Implementation

Use plain HTML, CSS, and JavaScript.

Do not add React, Vite, Next.js, Vue, Svelte, or another frontend framework for the first demo unless explicitly requested.

Current route:

```text
GET /demo
```

Static assets:

```text
/demo-static/demo.css
/demo-static/demo.js
```

## Current flow

```text
navigator.mediaDevices.getUserMedia()
        |
        v
video element
        |
        v
canvas capture as JPEG data URL
        |
        v
POST /v1/vision/detections
        |
        v
draw boxes on overlay canvas
```

## CPU backpressure

The browser must not queue unlimited frames.

Correct loop:

```text
if request is in flight:
    do not send another frame
else:
    capture and send next frame after the previous response
```

The current implementation uses a request-after-response loop with one in-flight request maximum.

## API key handling

For a local/internal demo, the page has an input field where the user enters the API key.

Do not hard-code a real API key in JavaScript.

The current page keeps the entered key in memory only. It does not use localStorage and does not persist the key.

A public deployment needs a different auth/session design and is outside v0.

## UI elements

Current simple UI:

- camera preview;
- overlay canvas;
- API key field;
- start/stop buttons;
- status fields for camera, request, latency, and detection count;
- error display;
- local/demo API-key warning.

Not implemented yet:

- API base URL field;
- target FPS selector;
- confidence threshold slider;
- raw JSON toggle;
- WebSocket or streaming mode.

## Testing

Current baseline has static route tests and a static smoke script:

```bash
python scripts/smoke_demo_static.py
```

The smoke verifies that `/demo`, the CSS asset, and the JavaScript asset are served without a real camera.

No headless camera E2E test is included yet.

## RC1 browser demo requirements

- Works on localhost in a modern browser.
- Does not queue unlimited requests.
- Shows low-FPS CPU expectation.
- Draws boxes in the correct positions.
- Handles auth errors.
- Handles service busy/timeout gracefully.
