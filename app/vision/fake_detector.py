from app.schemas.detections import Detection, DetectionPayload, DetectionSource
from app.vision.detector import Detector
from app.vision.image_decode import DecodedImage


class FakeDetector(Detector):
    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        source = DetectionSource(
            kind="image_url",
            decoded=True,
            mime_type=image.mime_type,
            width=image.width,
            height=image.height,
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
