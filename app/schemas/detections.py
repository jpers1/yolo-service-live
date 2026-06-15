from typing import Literal

from pydantic import BaseModel, Field


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    box_xyxy: list[float] = Field(min_length=4, max_length=4)
    box_normalized_xyxy: list[float] = Field(min_length=4, max_length=4)


class DetectionSource(BaseModel):
    kind: Literal["image_url"]
    decoded: bool


class DetectionPayload(BaseModel):
    task: Literal["object_detection"] = "object_detection"
    model: str
    source: DetectionSource
    detections: list[Detection]
    mock: bool
