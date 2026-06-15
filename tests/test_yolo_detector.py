import builtins
from typing import Any

import pytest
from PIL import Image

from app.schemas.detections import DetectionPayload
from app.vision.detector import DetectorUnavailableError
from app.vision.image_decode import DecodedImage
from app.vision.yolo_detector import YoloDetector


class FakeBoxes:
    def __init__(
        self,
        *,
        xyxy: list[list[float]],
        conf: list[float],
        cls: list[float],
    ) -> None:
        self.xyxy = xyxy
        self.conf = conf
        self.cls = cls


class FakeResult:
    def __init__(self, boxes: FakeBoxes | None, names: dict[int, str] | None = None) -> None:
        self.boxes = boxes
        self.names = names


class FakeYoloModel:
    def __init__(self, results: list[FakeResult]) -> None:
        self.results = results
        self.names = {0: "person", 1: "bicycle"}
        self.calls: list[dict[str, Any]] = []

    def predict(self, source: Image.Image, *, device: str, conf: float, verbose: bool) -> list[Any]:
        self.calls.append(
            {
                "source": source,
                "device": device,
                "conf": conf,
                "verbose": verbose,
            }
        )
        return self.results


def _decoded_image(width: int = 100, height: int = 200) -> DecodedImage:
    image = Image.new("RGB", (width, height), color=(255, 255, 255))
    return DecodedImage(
        mime_type="image/jpeg",
        width=image.width,
        height=image.height,
        mode=image.mode,
        format="JPEG",
        image=image,
    )


def test_yolo_detector_does_not_load_model_at_construction() -> None:
    loaded: list[str] = []

    def loader(model_weights: str) -> FakeYoloModel:
        loaded.append(model_weights)
        return FakeYoloModel([])

    detector = YoloDetector(model_weights="yolo11n.pt", confidence=0.25, model_loader=loader)

    assert detector.model_weights == "yolo11n.pt"
    assert detector.confidence == 0.25
    assert loaded == []


def test_missing_ultralytics_raises_detector_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "ultralytics":
            raise ImportError("not installed")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    detector = YoloDetector(model_weights="yolo11n.pt", confidence=0.25)

    with pytest.raises(DetectorUnavailableError):
        detector.detect(image=_decoded_image(), model="yolo11n-coco")


def test_yolo_detector_empty_boxes_produce_non_mock_empty_payload() -> None:
    model = FakeYoloModel([FakeResult(boxes=None)])
    detector = YoloDetector(
        model_weights="yolo11n.pt",
        confidence=0.33,
        model_loader=lambda _: model,
    )

    payload = detector.detect(image=_decoded_image(), model="yolo11n-coco")

    assert isinstance(payload, DetectionPayload)
    assert payload.model == "yolo11n-coco"
    assert payload.mock is False
    assert payload.detections == []


def test_yolo_detector_maps_one_box_and_preserves_source_metadata() -> None:
    model = FakeYoloModel(
        [
            FakeResult(
                boxes=FakeBoxes(
                    xyxy=[[10.0, 20.0, 50.0, 120.0]],
                    conf=[0.875],
                    cls=[1.0],
                )
            )
        ]
    )
    detector = YoloDetector(
        model_weights="yolo11n.pt",
        confidence=0.42,
        model_loader=lambda _: model,
    )

    payload = detector.detect(image=_decoded_image(width=100, height=200), model="yolo11n-coco")

    assert payload.mock is False
    assert payload.source.mime_type == "image/jpeg"
    assert payload.source.width == 100
    assert payload.source.height == 200
    assert len(payload.detections) == 1
    detection = payload.detections[0]
    assert detection.class_id == 1
    assert detection.class_name == "bicycle"
    assert detection.confidence == 0.875
    assert detection.box_xyxy == [10.0, 20.0, 50.0, 120.0]
    assert detection.box_normalized_xyxy == [0.1, 0.1, 0.5, 0.6]


def test_yolo_detector_uses_cpu_device_and_configured_confidence() -> None:
    model = FakeYoloModel([FakeResult(boxes=None)])
    detector = YoloDetector(
        model_weights="yolo11n.pt",
        confidence=0.67,
        model_loader=lambda _: model,
    )

    detector.detect(image=_decoded_image(), model="yolo11n-coco")

    assert model.calls == [
        {
            "source": model.calls[0]["source"],
            "device": "cpu",
            "conf": 0.67,
            "verbose": False,
        }
    ]
    assert isinstance(model.calls[0]["source"], Image.Image)
