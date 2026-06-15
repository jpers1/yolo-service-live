from app.schemas.detections import Detection, DetectionPayload, DetectionSource
from app.vision.image_decode import DecodedImage


def detect_mock_image_url(*, model: str, image: DecodedImage | None = None) -> DetectionPayload:
    source = DetectionSource(
        kind="image_url",
        decoded=image is not None,
        mime_type=image.mime_type if image else None,
        width=image.width if image else None,
        height=image.height if image else None,
    )

    return DetectionPayload(
        model=model,
        source=source,
        detections=[
            Detection(
                class_id=0,
                class_name="person",
                confidence=0.99,
                box_xyxy=[0.0, 0.0, 1.0, 1.0],
                box_normalized_xyxy=[0.0, 0.0, 1.0, 1.0],
            )
        ],
        mock=True,
    )
