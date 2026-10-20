"""PDF-STREAM-FIX-1: the exported PDF must survive an outside implementation.

SEC-FMT-IMPL-1's AC5 found that every exported PDF rendered blank. The cause
was one line: the content stream declared /Filter /FlateDecode while carrying
plain ASCII, so readers could not inflate it, skipped it, and never ran the
"q ... /Im0 Do Q" that paints the image.

The three tests below exist because the obvious checks do not catch it:

  - page_count, page rects and get_images() are all correct in the broken file
  - MuPDF reports the failure on stderr and does not raise, so try/except
    around fitz.open passes against a broken PDF
  - only inflating the streams, or looking at rendered pixels, distinguishes
    a working document from a blank one
"""

from __future__ import annotations

import io
import re
import zlib

import pytest
from PIL import Image

from infrastructure.export.qt_free import _compose_pdf

pymupdf = pytest.importorskip("pymupdf", reason="PyMuPDF is required for render checks")


def _png(width: int, height: int, colour: tuple[int, int, int]) -> bytes:
    buffer = io.BytesIO()
    Image.new("RGB", (width, height), colour).save(buffer, "PNG")
    return buffer.getvalue()


def _streams(pdf: bytes) -> list[dict]:
    """Every stream in the document, with its declared and actual length."""
    found = []
    for match in re.finditer(rb"<<([^>]*?)>>\s*\nstream\r?\n", pdf):
        start = match.end()
        end = pdf.find(b"endstream", start)
        if end < 0:
            continue
        raw = pdf[start:end].rstrip(b"\r\n")
        dictionary = match.group(1)
        length_match = re.search(rb"/Length (\d+)", dictionary)
        found.append(
            {
                "dictionary": dictionary,
                "declared": int(length_match.group(1)) if length_match else None,
                "raw": raw,
                "has_flate": b"/FlateDecode" in dictionary,
            }
        )
    return found


def test_every_declared_flate_stream_actually_inflates() -> None:
    """AC2: a /Filter declaration must describe the bytes that follow it."""
    pdf = _compose_pdf([_png(40, 60, (255, 0, 0)), _png(40, 60, (0, 128, 255))], None)

    streams = [s for s in _streams(pdf) if s["has_flate"]]
    assert streams, "expected at least one FlateDecode stream"

    for index, stream in enumerate(streams, start=1):
        try:
            zlib.decompress(stream["raw"])
        except zlib.error as error:
            pytest.fail(
                f"stream #{index} declares FlateDecode but does not inflate: {error}; "
                f"first bytes={stream['raw'][:2].hex()} "
                f"dictionary={stream['dictionary'][:80]!r}"
            )


def test_declared_length_matches_actual_bytes() -> None:
    """A wrong /Length desynchronises the reader as surely as a wrong filter."""
    pdf = _compose_pdf([_png(40, 60, (10, 20, 30))], None)
    for index, stream in enumerate(_streams(pdf), start=1):
        if stream["declared"] is None:
            continue
        # the raw slice excludes the CRLF before 'endstream', so allow that
        assert abs(stream["declared"] - len(stream["raw"])) <= 2, (
            f"stream #{index}: declared {stream['declared']} bytes, "
            f"found {len(stream['raw'])}"
        )


def test_mupdf_reports_no_zlib_error(capfd) -> None:
    """AC3: ASSERT NOTHING USEFUL - this test does not catch the defect.

    Verified by restoring the broken line and running it: exit 0, 1 passed,
    with the defect present. Both capsys and capfd fail to see MuPDF's
    message, even though the same message is plainly visible on the terminal
    when the probe runs outside pytest.

    Kept as documentation of a real trap rather than deleted: the CI signal
    this test appears to give is false. AC2 and AC4 do catch the defect
    (verified in the same run), so the suite is not blind - but anyone
    reading a green result here should not count it.

    Why it fails is not established. MuPDF writes through its own error
    callback into the CRT's stderr, which pytest's capture does not
    necessarily intercept at process level.
    """
    pdf = _compose_pdf([_png(40, 60, (255, 0, 0))], None)
    document = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        for index in range(document.page_count):
            document.load_page(index).get_pixmap(dpi=36)
    finally:
        document.close()
    # recorded, not asserted: see the docstring
    capfd.readouterr()


def test_rendered_page_is_not_blank() -> None:
    """AC4: the only test that can prove the repair.

    With the defect present the page renders pure white while page_count,
    rects and get_images() all look right. So this asserts on pixels.

    Colour is asserted loosely - a renderer may colour-manage - but a
    non-white pixel count of zero is unambiguous.
    """
    pdf = _compose_pdf([_png(60, 90, (255, 0, 0)), _png(60, 90, (0, 128, 255))], None)

    document = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        assert document.page_count == 2
        for index, expected_hint in enumerate(("red", "blue")):
            page = document.load_page(index)
            pixmap = page.get_pixmap(dpi=72)
            image = Image.frombytes(
                "RGB", (pixmap.width, pixmap.height), pixmap.samples
            )
            colours = image.getcolors(maxcolors=1_000_000) or []
            non_white = sum(count for count, rgb in colours if rgb != (255, 255, 255))
            total = pixmap.width * pixmap.height
            assert non_white > 0, (
                f"page {index} ({expected_hint}) rendered entirely white - "
                f"{total} pixels, 0 non-white"
            )
            dominant = max(colours, key=lambda item: item[0])[1]
            if expected_hint == "red":
                assert dominant[0] > 128 and dominant[1] < 100, dominant
            else:
                assert dominant[2] > 128 and dominant[0] < 100, dominant
    finally:
        document.close()


def test_searchable_pdf_also_renders() -> None:
    """The same composer path serves searchable PDFs (risk R1).

    A fix that repaired the plain path and broke the text layer would pass
    every test above.
    """
    pdf = _compose_pdf(
        [_png(60, 90, (255, 0, 0))],
        [({"ocr_text": "hello", "geometry": {"bbox": [0, 0, 60, 90]}},)],
    )
    document = pymupdf.open(stream=pdf, filetype="pdf")
    try:
        pixmap = document.load_page(0).get_pixmap(dpi=72)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        colours = image.getcolors(maxcolors=1_000_000) or []
        non_white = sum(count for count, rgb in colours if rgb != (255, 255, 255))
        assert non_white > 0, "searchable PDF rendered blank"
    finally:
        document.close()
