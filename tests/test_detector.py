from app.schemas.detections import DetectionPayload
from app.vision.fake_detector import FakeDetector
from app.vision.image_decode import DecodedImage


def test_fake_detector_returns_mock_payload_for_decoded_image() -> None:
    image = DecodedImage(
        mime_type="image/jpeg",
        width=2,
        height=3,
        mode="RGB",
        format="JPEG",
    )

    payload = FakeDetector().detect(image=image, model="configured-model")

    assert isinstance(payload, DetectionPayload)
    assert payload.model == "configured-model"
    assert payload.task == "object_detection"
    assert payload.mock is True
    assert payload.source.kind == "image_url"
    assert payload.source.decoded is True
    assert payload.source.mime_type == "image/jpeg"
    assert payload.source.width == 2
    assert payload.source.height == 3
    assert len(payload.detections) == 1
    assert payload.detections[0].class_id == 0
    assert payload.detections[0].class_name == "person"
    assert payload.detections[0].confidence == 0.99
    assert payload.detections[0].box_xyxy == [0.0, 0.0, 1.0, 1.0]
    assert payload.detections[0].box_normalized_xyxy == [0.0, 0.0, 1.0, 1.0]
