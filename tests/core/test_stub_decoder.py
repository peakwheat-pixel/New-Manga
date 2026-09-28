"""M2-FIX-STUB-DECODER — production stub decoder must honor DecodedImage contract.

Defect (M2-AC2 registration + DSH r2 P3-3): ``_PassthroughImageDecoder.decode``
constructed ``DecodedImage(width=1, height=1, format="rgb")`` while the frozen
contract (``src/application/importing/images/ports.py``) only has
``width/height/mime_type`` — a double TypeError on every stub decode.
These tests lock the stub to the real contract via the production assembly
path (AC2), plus a direct-construction passthrough semantics check.
"""

from __future__ import annotations

from pathlib import Path
import sys

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.importing.images.ports import DecodedImage
from bootstrap.core_service import (
    # Private-name import: the task explicitly allows direct construction of
    # the stub decoder as a secondary path; the primary test goes through the
    # production assembly.
    _PassthroughImageDecoder,
    assemble_production_core,
)


def test_production_stub_decoder_returns_valid_decoded_image(tmp_path: Path) -> None:
    """AC2: the decoder injected by the production assembly must decode to a
    valid ``DecodedImage`` (real contract fields only)."""
    core = assemble_production_core(tmp_path / "data")
    try:
        # CoreServices exposes the injected decoder inside the ImportImagesUseCase
        # slot (``core.importer``); that is the production-assembled instance.
        decoder = core.importer._decoder
        img = decoder.decode(b"fake")

        assert isinstance(img, DecodedImage)
        assert img.width == 1
        assert img.height == 1
        assert isinstance(img.mime_type, str)
        assert img.mime_type != ""
    finally:
        core.conn.close()


def test_stub_decoder_passthrough_any_payload_does_not_raise() -> None:
    """Passthrough semantics: decode never raises and always returns a valid
    DecodedImage, regardless of payload."""
    decoder = _PassthroughImageDecoder()
    for payload in (b"fake", b"", b"\x00\xff\x10" * 32, b"not an image at all"):
        img = decoder.decode(payload)
        assert isinstance(img, DecodedImage)
        assert img.width == 1
        assert img.height == 1
        assert img.mime_type != ""
