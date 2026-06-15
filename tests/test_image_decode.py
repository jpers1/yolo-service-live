import base64
from io import BytesIO

import pytest
from PIL import Image

from app.vision.image_decode import ImageDecodeError, decode_image_data_url


def _image_data_url(
    *,
    mime_type: str = "image/jpeg",
    image_format: str = "JPEG",
    size: tuple[int, int] = (2, 3),
) -> str:
    buffer = BytesIO()
    Image.new("RGB", size, color=(255, 0, 0)).save(buffer, format=image_format)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def _decode(url: str, *, max_request_bytes: int = 5_242_880, max_image_pixels: int = 100):
    return decode_image_data_url(
        url,
        max_request_bytes=max_request_bytes,
        max_image_pixels=max_image_pixels,
    )


def test_valid_jpeg_data_url_decodes() -> None:
    image = _decode(_image_data_url(mime_type="image/jpeg", image_format="JPEG", size=(2, 3)))

    assert image.mime_type == "image/jpeg"
    assert image.width == 2
    assert image.height == 3
    assert image.mode == "RGB"
    assert image.format == "JPEG"


def test_valid_png_data_url_decodes() -> None:
    image = _decode(_image_data_url(mime_type="image/png", image_format="PNG", size=(4, 5)))

    assert image.mime_type == "image/png"
    assert image.width == 4
    assert image.height == 5
    assert image.mode == "RGB"
    assert image.format == "PNG"


def test_image_jpg_alias_normalizes_to_jpeg() -> None:
    image = _decode(_image_data_url(mime_type="image/jpg", image_format="JPEG"))

    assert image.mime_type == "image/jpeg"


@pytest.mark.parametrize("url", ["https://example.test/image.jpg", "http://example.test/image.jpg"])
def test_external_url_is_rejected(url: str) -> None:
    with pytest.raises(ImageDecodeError) as exc_info:
        _decode(url)

    assert exc_info.value.code == "external_image_url_not_supported"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "data:image/jpeg;base64",
        "data:image/jpeg,AAAA",
        "data:image/jpeg;base64,",
    ],
)
def test_malformed_data_url_is_rejected(url: str) -> None:
    with pytest.raises(ImageDecodeError) as exc_info:
        _decode(url)

    assert exc_info.value.code == "invalid_image_data"


def test_unsupported_mime_type_is_rejected() -> None:
    with pytest.raises(ImageDecodeError) as exc_info:
        _decode("data:image/gif;base64,AAAA")

    assert exc_info.value.code == "unsupported_image_mime"


def test_invalid_base64_is_rejected() -> None:
    with pytest.raises(ImageDecodeError) as exc_info:
        _decode("data:image/jpeg;base64,not-valid!!!")

    assert exc_info.value.code == "invalid_image_data"


def test_valid_base64_non_image_bytes_are_rejected() -> None:
    encoded = base64.b64encode(b"not an image").decode("ascii")

    with pytest.raises(ImageDecodeError) as exc_info:
        _decode(f"data:image/jpeg;base64,{encoded}")

    assert exc_info.value.code == "invalid_image_data"


def test_too_large_encoded_payload_is_rejected() -> None:
    with pytest.raises(ImageDecodeError) as exc_info:
        _decode("data:image/jpeg;base64,AAAA", max_request_bytes=3)

    assert exc_info.value.status_code == 413
    assert exc_info.value.code == "payload_too_large"


def test_too_large_decoded_payload_is_rejected() -> None:
    encoded = base64.b64encode(b"abcd").decode("ascii")

    with pytest.raises(ImageDecodeError) as exc_info:
        _decode(f"data:image/jpeg;base64,{encoded}", max_request_bytes=7)

    assert exc_info.value.status_code == 413
    assert exc_info.value.code == "payload_too_large"


def test_too_large_image_dimensions_are_rejected() -> None:
    with pytest.raises(ImageDecodeError) as exc_info:
        _decode(_image_data_url(size=(3, 3)), max_image_pixels=8)

    assert exc_info.value.status_code == 413
    assert exc_info.value.code == "image_too_large"


def test_decoder_does_not_write_files(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    _decode(_image_data_url())

    assert list(tmp_path.iterdir()) == []
