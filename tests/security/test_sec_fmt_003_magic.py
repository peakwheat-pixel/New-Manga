"""AC3: prove a disguised file is rejected before the decoder is asked.

SEC-FMT-003 asks for header sniffing that identifies a non-image renamed to
.png/.jpg and reports it without crashing the decoder.

IMPORTANT - the mechanism is delegation, not an in-house check:

    src/bootstrap/core_service.py rejects whatever Pillow's Image.open()
    did not identify as PNG or JPEG:

        if image.format not in _DETECT_PAGE_FORMATS:   # {"PNG", "JPEG"}
            raise DetectRequestError(...)

There is no explicit magic-number comparison for JPEG anywhere in src/
(PDF has %PDF-, PNG has its signature in three places). So the guarantee
holds because Pillow sniffs the header, plus a fail-closed whitelist on top.

Two consequences, both tested below:
  - disguising a file does not get it past the whitelist;
  - a truncated but correctly-headed image is still a decode failure, not a
    crash, and must surface as a typed error.
"""

from __future__ import annotations

import base64
import io

import pytest
from PIL import Image

from bootstrap.core_service import (
    MAX_DETECT_PIXELS,
    CoreServiceServer,
    DetectRequestError,
)


def _server() -> CoreServiceServer:
    """A server instance with only the detect path usable.

    handle_detect validates the payload before touching _core, so __new__ is
    enough for the rejection paths. The tests below that reach a provider are
    not in this file.
    """
    return CoreServiceServer.__new__(CoreServiceServer)


def _payload(raw: bytes, width: int = 10, height: int = 10) -> dict:
    return {
        "page": base64.b64encode(raw).decode("ascii"),
        "width": width,
        "height": height,
    }


def _expect_rejected(raw: bytes, width: int = 10, height: int = 10) -> str:
    with pytest.raises(DetectRequestError) as excinfo:
        _server().handle_detect(_payload(raw, width, height))
    return str(excinfo.value)


def test_text_file_renamed_to_png_is_rejected() -> None:
    """A text file with a .png name never reaches the decoder."""
    message = _expect_rejected(b"this is not a png, it is just text\n" * 10)
    assert "PNG or JPEG" in message or "image" in message.lower()


def test_executable_header_renamed_to_png_is_rejected() -> None:
    """An MZ header is the classic disguise."""
    message = _expect_rejected(b"MZ\x90\x00" + b"\x00" * 200)
    assert "PNG or JPEG" in message or "image" in message.lower()


def test_gif_is_rejected_even_though_pillow_can_read_it() -> None:
    """The whitelist, not Pillow's ability, is what excludes GIF.

    This is the load-bearing test for the delegation claim: Pillow identifies
    GIF happily (so Image.open succeeds), and only the frozenset stops it.
    """
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buffer, "GIF")
    raw = buffer.getvalue()

    assert Image.open(io.BytesIO(raw)).format == "GIF", (
        "Pillow must accept GIF here, otherwise this test proves nothing"
    )
    message = _expect_rejected(raw)
    assert "PNG or JPEG" in message
    assert "GIF" in message


def test_truncated_png_is_a_typed_error_not_a_crash() -> None:
    """A correct header with no data behind it must not raise something raw."""
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buffer, "PNG")
    truncated = buffer.getvalue()[:40]

    message = _expect_rejected(truncated)
    assert message, "expected a message, not an empty error"


def test_genuine_png_passes_the_format_gate() -> None:
    """Control arm: a real PNG gets past format validation.

    The tests above would otherwise all pass for a gate that rejected every
    input.

    A genuine PNG proceeds past the format gate and the pixel/width checks and
    then reaches the provider lookup, where this bare instance has no _core.
    That AttributeError is therefore evidence of SUCCESS at the gate, not a
    failure - so it is accepted here, and the assertion is that no format
    rejection occurred.
    """
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "white").save(buffer, "PNG")
    raw = buffer.getvalue()

    reached_provider_lookup = False
    try:
        _server().handle_detect(_payload(raw))
    except DetectRequestError as error:
        message = str(error)
        assert "PNG or JPEG" not in message, (
            f"a genuine PNG was rejected by the format gate: {message}"
        )
    except AttributeError:
        # self._core is absent on a __new__ instance: the payload was accepted
        reached_provider_lookup = True

    assert reached_provider_lookup, (
        "expected the genuine PNG to reach the provider lookup"
    )


def test_pixel_cap_is_still_the_practical_ceiling() -> None:
    """Sanity: the format gate is not the only thing standing between a
    caller and the decoder - the pixel cap still applies and is unchanged."""
    assert MAX_DETECT_PIXELS == (32 * 1024 * 1024) // 3
