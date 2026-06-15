# Model Card: yolo11n-coco

Status: initial design.

## Model identity

Internal model file:

```text
yolo11n.pt
```

Public API model name:

```text
yolo11n-coco
```

## Source

Ultralytics YOLO11 documentation:

https://docs.ultralytics.com/models/yolo11/

## Intended use

CPU-friendly object detection on images for local/internal API use and browser-camera demonstrations.

## Task

Object detection.

## Dataset/classes

The planned default model is a COCO-pretrained YOLO11 detection model with 80 pretrained COCO classes.

## Why YOLO11n?

`yolo11n.pt` is the smallest YOLO11 detection model variant documented by Ultralytics. It is the best default for CPU-only service development.

## Runtime

The service must run on CPU without CUDA or GPU assumptions.

Expected real-world performance depends on:

- CPU model;
- image size;
- PyTorch/ONNX path;
- preprocessing;
- concurrent requests;
- container overhead.

Do not promise 30 FPS live video on CPU.

## Output

Each detection should include:

- class ID;
- COCO class name;
- confidence score;
- absolute bounding box coordinates;
- normalized bounding box coordinates.

## Known limitations

- COCO classes only.
- Not trained for specialized industrial or medical classes unless replaced/fine-tuned later.
- False positives and false negatives are expected.
- Performance depends heavily on input size.
- Browser demo must use low FPS and frame dropping on CPU.
- Results are object detections, not semantic understanding.
- This model does not perform OCR, tracking, segmentation, or pose estimation in v0.

## License note

Ultralytics documentation states that YOLO11 models are provided under AGPL-3.0 and Enterprise licenses. This project must not claim closed commercial deployment readiness without license review.

This document is not legal advice.

## Future model options

Possible later additions:

- `yolo11s-coco` for better accuracy if CPU performance permits;
- segmentation variants only if explicitly scoped;
- custom fine-tuned model only after API contract and deployment behavior are stable.
