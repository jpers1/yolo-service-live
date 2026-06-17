from collections.abc import Callable
from typing import Any

from app.schemas.detections import Detection, DetectionPayload, DetectionSource
from app.vision.detector import Detector, DetectorInferenceError, DetectorUnavailableError
from app.vision.image_decode import DecodedImage


ModelLoader = Callable[[str], Any]


class YoloDetector(Detector):
    def __init__(
        self,
        *,
        model_weights: str,
        confidence: float,
        model_loader: ModelLoader | None = None,
    ) -> None:
        self.model_weights = model_weights
        self.confidence = confidence
        self._model_loader = model_loader
        self._model: Any | None = None

    def detect(self, *, image: DecodedImage, model: str) -> DetectionPayload:
        yolo_model = self._load_model()

        try:
            results = yolo_model.predict(
                image.image,
                device="cpu",
                conf=self.confidence,
                verbose=False,
            )
        except Exception as exc:  # pragma: no cover - exact Ultralytics exceptions vary.
            raise DetectorInferenceError("YOLO inference failed.") from exc

        try:
            detections = _detections_from_results(results, image=image, yolo_model=yolo_model)
        except Exception as exc:  # pragma: no cover - defensive postprocessing boundary.
            raise DetectorInferenceError("YOLO inference failed.") from exc

        return DetectionPayload(
            model=model,
            source=DetectionSource(
                kind="image_url",
                decoded=True,
                mime_type=image.mime_type,
                width=image.width,
                height=image.height,
            ),
            detections=detections,
            mock=False,
        )

    def _load_model(self) -> Any:
        if self._model is not None:
            return self._model

        loader = self._model_loader
        if loader is None:
            try:
                from ultralytics import YOLO
            except ImportError as exc:
                raise DetectorUnavailableError(
                    "YOLO backend could not import Ultralytics or one of its native "
                    "dependencies. Install the optional yolo extra and required "
                    "OpenCV runtime libraries."
                ) from exc

            loader = YOLO

        try:
            self._model = loader(self.model_weights)
        except DetectorUnavailableError:
            raise
        except ImportError as exc:
            raise DetectorUnavailableError(
                "YOLO backend could not import Ultralytics or one of its native "
                "dependencies. Install the optional yolo extra and required "
                "OpenCV runtime libraries."
            ) from exc
        except Exception as exc:
            raise DetectorUnavailableError("YOLO detector could not be initialized.") from exc

        return self._model


def _detections_from_results(
    results: Any,
    *,
    image: DecodedImage,
    yolo_model: Any,
) -> list[Detection]:
    if not results:
        return []

    result = results[0]
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return []

    xyxy_rows = _rows(getattr(boxes, "xyxy", []))
    confidence_values = _flat_values(getattr(boxes, "conf", []))
    class_values = _flat_values(getattr(boxes, "cls", []))
    names = getattr(result, "names", None) or getattr(yolo_model, "names", {})

    detections: list[Detection] = []
    for index, box_xyxy in enumerate(xyxy_rows):
        class_id = int(class_values[index])
        confidence = float(confidence_values[index])
        absolute_box = [float(value) for value in box_xyxy]

        detections.append(
            Detection(
                class_id=class_id,
                class_name=_class_name(names, class_id),
                confidence=confidence,
                box_xyxy=absolute_box,
                box_normalized_xyxy=_normalized_xyxy(absolute_box, image=image),
            )
        )

    return detections


def _rows(value: Any) -> list[list[float]]:
    converted = _as_python(value)
    if converted is None:
        return []
    return [list(row) for row in converted]


def _flat_values(value: Any) -> list[float]:
    converted = _as_python(value)
    if converted is None:
        return []
    return list(converted)


def _as_python(value: Any) -> Any:
    for method_name in ("detach", "cpu"):
        method = getattr(value, method_name, None)
        if callable(method):
            value = method()

    tolist = getattr(value, "tolist", None)
    if callable(tolist):
        return tolist()

    return value


def _class_name(names: Any, class_id: int) -> str:
    if isinstance(names, dict):
        return str(names.get(class_id, class_id))

    if isinstance(names, list) and 0 <= class_id < len(names):
        return str(names[class_id])

    return str(class_id)


def _normalized_xyxy(box_xyxy: list[float], *, image: DecodedImage) -> list[float]:
    width = float(image.width)
    height = float(image.height)
    return [
        box_xyxy[0] / width,
        box_xyxy[1] / height,
        box_xyxy[2] / width,
        box_xyxy[3] / height,
    ]
