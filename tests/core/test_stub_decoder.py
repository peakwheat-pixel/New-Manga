"""Production decoder wiring and retained legacy test-double behavior."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

from PIL import Image
import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import DecodedImage, ImageDecodeError
from bootstrap.core_service import (
    _PassthroughImageDecoder,
    assemble_production_core,
)
from infrastructure.importing import QtImageDecoder


def test_production_stub_decoder_returns_valid_decoded_image(tmp_path: Path) -> None:
    """AC1: production uses Qt decoding, reports real dimensions, and rejects invalid bytes."""
    core = assemble_production_core(tmp_path / "data")
    try:
        decoder = core.importer._decoder
        assert isinstance(decoder, QtImageDecoder)

        payload = BytesIO()
        Image.new("RGB", (16, 12), "white").save(payload, format="PNG")
        img = decoder.decode(payload.getvalue())
        assert isinstance(img, DecodedImage)
        assert (img.width, img.height) == (16, 12)
        assert img.mime_type == "image/png"
        with pytest.raises(ImageDecodeError):
            decoder.decode(b"fake")
    finally:
        core.conn.close()


def test_stub_decoder_passthrough_any_payload_does_not_raise() -> None:
    """Only covers the retained legacy test double; it does not describe production assembly."""
    decoder = _PassthroughImageDecoder()
    for payload in (b"fake", b"", b"\x00\xff\x10" * 32, b"not an image at all"):
        img = decoder.decode(payload)
        assert isinstance(img, DecodedImage)
        assert img.width == 1
        assert img.height == 1
        assert img.mime_type != ""
