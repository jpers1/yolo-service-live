# Browser Demo

Status: planned, not MVP.

## Goal

Create a local/internal HTML5 demo where the browser:

1. asks for camera access;
2. displays the camera preview;
3. captures frames to a canvas;
4. sends JPEG data URLs to `/v1/vision/detections`;
5. draws returned YOLO boxes and labels over the video/canvas.

## First implementation rule

Use plain HTML, CSS, and JavaScript.

Do not add React, Vite, Next.js, Vue, Svelte, or another frontend framework for the first demo unless explicitly requested.

## Planned flow

```text
navigator.mediaDevices.getUserMedia()
        |
        v
video element
        |
        v
canvas capture at controlled FPS
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
    capture and send next frame
```

## API key handling

For a local/internal demo, the page may have an input field where the user enters the API key.

Do not hard-code a real API key in JavaScript.

A public deployment needs a different auth/session design and is outside v0.

## UI elements

Planned simple UI:

- camera preview;
- overlay canvas;
- API base URL field;
- API key field;
- start/stop button;
- target FPS selector: 1, 2, 5;
- confidence threshold slider;
- latency display;
- inference time display;
- detection count;
- raw JSON toggle.

## RC1 browser demo requirements

- Works on localhost in a modern browser.
- Does not queue unlimited requests.
- Shows low-FPS CPU expectation.
- Draws boxes in the correct positions.
- Handles auth errors.
- Handles service busy/timeout gracefully.
