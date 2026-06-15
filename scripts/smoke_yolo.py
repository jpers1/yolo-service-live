#!/usr/bin/env python

from PIL import Image

from app.vision.detector import DetectorUnavailableError
from app.vision.image_decode import DecodedImage
from app.vision.yolo_detector import YoloDetector


def main() -> None:
    image = Image.new("RGB", (64, 64), color=(255, 255, 255))
    decoded_image = DecodedImage(
        mime_type="image/jpeg",
        width=image.width,
        height=image.height,
        mode=image.mode,
        format="JPEG",
        image=image,
    )
    detector = YoloDetector(model_weights="yolo11n.pt", confidence=0.25)

    try:
        payload = detector.detect(image=decoded_image, model="yolo11n-coco")
    except DetectorUnavailableError as exc:
        print('YOLO smoke failed. Install YOLO extras first: python -m pip install -e ".[yolo]"')
        raise SystemExit(1) from exc
    except Exception as exc:
        print("YOLO smoke failed during inference.")
        raise SystemExit(1) from exc

    print(f"model_weights={detector.model_weights}")
    print(f"detections={len(payload.detections)}")
    print("inference_completed=true")


if __name__ == "__main__":
    main()
