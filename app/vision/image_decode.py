import base64
import binascii
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_MIME_TYPES = ("image/jpeg", "image/png")
JPEG_MIME_ALIAS = "image/jpg"


@dataclass(frozen=True)
class DecodedImage:
    mime_type: str
    width: int
    height: int
    mode: str
    format: str | None


class ImageDecodeError(ValueError):
    def __init__(self, *, message: str, code: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def decode_image_data_url(
    url: str,
    *,
    max_request_bytes: int,
    max_image_pixels: int,
) -> DecodedImage:
    if not url:
        raise _invalid_image_data("Image data URL is required.")

    if not url.startswith("data:"):
        raise ImageDecodeError(
            message="Only base64 image data URLs are supported.",
            code="external_image_url_not_supported",
        )

    header, separator, encoded_payload = url.partition(",")
    if separator == "" or not encoded_payload:
        raise _invalid_image_data("Image data URL is malformed.")

    mime_type = _parse_data_url_header(header)

    try:
        encoded_payload_bytes = encoded_payload.encode("ascii")
    except UnicodeEncodeError as exc:
        raise _invalid_image_data("Image data is not valid base64.") from exc

    if len(encoded_payload_bytes) > max_request_bytes:
        raise _payload_too_large("Encoded image payload is too large.")

    try:
        decoded = base64.b64decode(encoded_payload_bytes, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise _invalid_image_data("Image data is not valid base64.") from exc

    if len(decoded) > max_request_bytes:
        raise _payload_too_large("Decoded image payload is too large.")

    try:
        with Image.open(BytesIO(decoded)) as image:
            width, height = image.size
            if width * height > max_image_pixels:
                raise ImageDecodeError(
                    message="Decoded image dimensions are too large.",
                    code="image_too_large",
                    status_code=413,
                )

            mode = image.mode
            image_format = image.format
            image.load()
    except ImageDecodeError:
        raise
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise _invalid_image_data("Decoded bytes are not a valid image.") from exc

    return DecodedImage(
        mime_type=mime_type,
        width=width,
        height=height,
        mode=mode,
        format=image_format,
    )


def _parse_data_url_header(header: str) -> str:
    parts = header.removeprefix("data:").split(";")
    if len(parts) < 2 or "base64" not in parts[1:]:
        raise _invalid_image_data("Image data URL must use base64 encoding.")

    mime_type = parts[0].lower()
    if mime_type == JPEG_MIME_ALIAS:
        mime_type = "image/jpeg"

    if mime_type not in ALLOWED_IMAGE_MIME_TYPES:
        raise ImageDecodeError(
            message="Image MIME type is not supported.",
            code="unsupported_image_mime",
        )

    return mime_type


def _invalid_image_data(message: str) -> ImageDecodeError:
    return ImageDecodeError(message=message, code="invalid_image_data")


def _payload_too_large(message: str) -> ImageDecodeError:
    return ImageDecodeError(message=message, code="payload_too_large", status_code=413)
