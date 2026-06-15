from app.schemas.detections import Detection, DetectionPayload, DetectionSource


def test_detection_payload_serializes_expected_shape() -> None:
    payload = DetectionPayload(
        model="yolo11n-coco",
        source=DetectionSource(
            kind="image_url",
            decoded=True,
            mime_type="image/jpeg",
            width=2,
            height=3,
        ),
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

    assert payload.model_dump() == {
        "task": "object_detection",
        "model": "yolo11n-coco",
        "source": {
            "kind": "image_url",
            "decoded": True,
            "mime_type": "image/jpeg",
            "width": 2,
            "height": 3,
        },
        "detections": [
            {
                "class_id": 0,
                "class_name": "person",
                "confidence": 0.99,
                "box_xyxy": [0.0, 0.0, 1.0, 1.0],
                "box_normalized_xyxy": [0.0, 0.0, 1.0, 1.0],
            }
        ],
        "mock": True,
    }
