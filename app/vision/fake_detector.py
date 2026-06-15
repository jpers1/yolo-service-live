from app.schemas.detections import Detection, DetectionPayload, DetectionSource


def detect_mock_image_url(*, model: str) -> DetectionPayload:
    return DetectionPayload(
        model=model,
        source=DetectionSource(kind="image_url", decoded=False),
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
