# 0001 Use YOLO11n on CPU

Status: accepted

## Context

The project must run without a GPU. The user wants a professional-grade YOLO object-detection API that can run locally on CPU.

Ultralytics documents YOLO11 detection variants including `yolo11n.pt`, `yolo11s.pt`, `yolo11m.pt`, `yolo11l.pt`, and `yolo11x.pt`. `yolo11n.pt` is the smallest planned detection model.

## Decision

Use `yolo11n.pt` as the default detector model.

Expose it publicly as:

```text
yolo11n-coco
```

The service must be CPU-only by default.

## Consequences

- Lower accuracy than larger models may be expected.
- Lower compute cost and better CPU viability.
- Browser live demo must still be low-FPS and adaptive.
- GPU-specific dependencies are forbidden unless this decision is explicitly revisited.
- Tests should use a fake detector by default; real YOLO tests may be integration/manual.

## May be revisited when

- A GPU deployment target is approved.
- A larger CPU host is available and `yolo11s.pt` is acceptable.
- A custom fine-tuned model becomes the real product goal.
