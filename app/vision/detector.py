from typing import Protocol, cast

from fastapi import Request

from app.schemas.detections import DetectionPayload
from app.vision.image_decode import DecodedImage


class Detector(Protocol):
    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        ...


def get_app_detector(request: Request) -> Detector:
    return cast(Detector, request.app.state.detector)
