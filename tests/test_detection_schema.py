from app.schemas.detections import Detection, DetectionPayload, DetectionSource
from app.vision.fake_detector import detect_mock_image_url


def test_detection_payload_serializes_expected_shape() -> None:
    payload = DetectionPayload(
        model="yolo11n-coco",
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

    assert payload.model_dump() == {
        "task": "object_detection",
        "model": "yolo11n-coco",
        "source": {"kind": "image_url", "decoded": False},
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


def test_fake_detector_returns_mock_image_url_payload() -> None:
    payload = detect_mock_image_url(model="configured-model")

    assert payload.model == "configured-model"
    assert payload.task == "object_detection"
    assert payload.source.kind == "image_url"
    assert payload.source.decoded is False
    assert payload.mock is True
    assert len(payload.detections) == 1
