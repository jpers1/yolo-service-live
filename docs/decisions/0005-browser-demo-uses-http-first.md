# 0005 Browser demo uses repeated HTTP first

Status: accepted

## Context

The project should later include a browser demo that reads camera frames, sends them to the API, and displays detections. CPU-only inference is unlikely to support high-rate streaming.

## Decision

The first browser demo will use repeated HTTP `POST /v1/vision/detections` requests, not WebSocket.

The browser sends a new frame only after the previous response returns.

## Consequences

- Simpler implementation.
- Easier debugging.
- Natural CPU backpressure.
- No unbounded frame queue.
- WebSocket can be added later if needed.

## May be revisited when

- HTTP overhead becomes the bottleneck;
- multi-frame sessions need persistent connection state;
- live streaming becomes an explicit RC/post-RC requirement.
