from typing import Protocol, cast

from fastapi import Request

from app.config import Settings
from app.schemas.detections import DetectionPayload
from app.vision.image_decode import DecodedImage


class DetectorError(RuntimeError):
    """Base error for detector failures that should be translated at the API boundary."""


class DetectorUnavailableError(DetectorError):
    """Raised when the selected detector backend cannot be used."""


class DetectorInferenceError(DetectorError):
    """Raised when detector inference fails after the backend is available."""


class Detector(Protocol):
    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        ...


def build_detector(settings: Settings) -> Detector:
    if settings.detector_backend == "fake":
        from app.vision.fake_detector import FakeDetector

        return FakeDetector()

    if settings.detector_backend == "yolo":
        from app.vision.yolo_detector import YoloDetector

        return YoloDetector(
            model_weights=settings.model_weights,
            confidence=settings.default_confidence,
        )

    raise DetectorUnavailableError("Configured detector backend is not supported.")


def get_app_detector(request: Request) -> Detector:
    return cast(Detector, request.app.state.detector)
