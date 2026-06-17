from pydantic import BaseModel, ConfigDict


class VisionImage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    url: str


class VisionDetectionsRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    image: VisionImage
    model: str | None = None
    include_normalized_boxes: bool = True
