# Performance

Status: initial design.

## Performance goal

The initial service is CPU-only and optimized for correctness, simplicity, and reliable demonstration, not maximum throughput.

## Honest expectation

CPU inference can be useful for:

- single-image API requests;
- low-rate browser demos;
- workshop examples;
- development and testing.

CPU inference should not be advertised as:

- 30 FPS real-time video analytics;
- production-scale multi-user video processing;
- high-throughput object-detection service.

## Default model

Use `yolo11n.pt` as the default model because it is the smallest YOLO11 detection variant.

## Real YOLO CPU inference

The service can use a real YOLO11n CPU detector backend when configured with:

```text
YOLO_SERVICE_DETECTOR_BACKEND=yolo
YOLO_SERVICE_MODEL_WEIGHTS=yolo11n.pt
```

The first real inference may download model weights through Ultralytics if the weights are not already present. CPU inference may be slow depending on host CPU, image dimensions, PyTorch build, and concurrent load.

Normal CI does not run real model inference and does not install the optional YOLO extra. Real-model verification is manual:

```bash
python -m pip install -e ".[yolo]"
python scripts/smoke_yolo.py
```

## Browser demo target

Initial browser live mode should target:

```text
1-5 FPS
one in-flight request at a time
frame dropping instead of queueing
visible latency display
visible inference time display
confidence threshold control
```

## Backpressure rule

The browser must not send frames faster than the backend can process them.

Correct behavior:

```text
capture frame
send request
wait for response
draw boxes
capture next frame
```

Incorrect behavior:

```text
send every camera frame
build unbounded queue
display stale detections seconds later
```

## Image size

The first live demo should use modest frame sizes, for example:

```text
320 px or 416 px inference size for live mode
640 px for single-image mode when acceptable
```

Exact values should be implemented as configuration and measured.

## Metrics to record

Once implemented, record:

- CPU model;
- Python version;
- OS/container;
- model path;
- image dimensions;
- inference size;
- preprocessing time;
- inference time;
- postprocessing time;
- total request latency;
- browser displayed FPS.

## RC1 performance evidence

RC1 should include a small manual benchmark table for at least one CPU machine.

Example placeholder:

| Machine | Image size | Mode | Median latency | Notes |
|---|---:|---|---:|---|
| TBD | 640x480 | HTTP single image | TBD | TBD |
| TBD | 416 px live | browser loop | TBD | one request in flight |
