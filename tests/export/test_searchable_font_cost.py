"""SEARCHABLE-PDF-CJK-1 AC4: the font is a fixed cost, not a per-page one.

r40 read the source and said the font object is created once per PDF. r41 said
that observation is not a passing test and required a measurement. So this
measures: export the same page 1, 3 and 5 times and check that the gap between
searchable and plain stays flat.

Why this matters rather than being a curiosity: if the true behaviour were
per-page embedding, a 200-page comic would carry 200 copies of a 19.5 MB font
and the format would be unusable. The constant-overhead result is what makes
the feature's cost predictable at all.

Threshold: the spread across page counts must stay under 10% of the overhead.
Measured spread was 333 bytes against a 12.4 MB overhead (0.0%), so the margin
is enormous - which is the point. A test that barely passes on threshold
tuning would say nothing about whether the behaviour is right.
"""

from __future__ import annotations

import io
import os

import pytest
from PIL import Image

pymupdf = pytest.importorskip("pymupdf", reason="PyMuPDF is required")

ASSETS = os.path.join(r"G:\CODEX\New Manga", "test_assets", "comic_golden_suite")


def _find_page():
    for root, _, files in os.walk(os.path.join(ASSETS, "日漫_JA")):
        for name in sorted(files):
            if not name.lower().endswith((".jpg", ".png")):
                continue
            path = os.path.join(root, name)
            try:
                with Image.open(path) as image:
                    width, height = image.size
            except Exception:
                continue
            if 400 <= width <= 1600 and 600 <= height <= 2400:
                return path
    return None


@pytest.fixture(scope="module")
def source_page():
    page = _find_page()
    if page is None:
        pytest.fail("no suitable real page under test_assets/comic_golden_suite")
    return page


def _export(source: str, pages: int, searchable: bool) -> int:
    from application.export.service import (
        ExportFormat, ExportPage, ExportRequest, ExportService,
    )
    from infrastructure.export.qt_free import QtFreePdfComposer

    with Image.open(source) as image:
        width, height = image.size

    def region():
        return ({"geometry": {"bbox": [40, 120, max(width - 80, 100), 70]},
                 "ocr_text": "こんにちは世界", "translated_text": ""},)

    entries = [
        ExportPage(page_id="p%d" % index, filename="%04d.png" % (index + 1),
                   source_provider=lambda path=source: io.open(path, "rb").read(),
                   regions=region() if searchable else ())
        for index in range(pages)
    ]
    service = ExportService(history_store=None, pdf_composer=QtFreePdfComposer())
    target = os.path.join(
        os.path.dirname(source), "_ac4_%d_%s.pdf" % (pages, searchable))
    try:
        service.export(ExportRequest(
            book_id="ac4", chapter_id="ac4", format=ExportFormat.PDF,
            output_path=target, pages=entries, export_id="ac4",
            format_options={"pdf_content": "searchable_dual_layer"}
            if searchable else None,
        ))
        return os.path.getsize(target)
    finally:
        if os.path.exists(target):
            os.remove(target)


def test_font_overhead_is_constant_across_page_counts(source_page) -> None:
    """AC4: the searchable-minus-plain gap must not grow with page count."""
    overheads = []
    for pages in (1, 3, 5):
        plain = _export(source_page, pages, searchable=False)
        searchable = _export(source_page, pages, searchable=True)
        overheads.append(searchable - plain)

    smallest = min(overheads)
    spread = max(overheads) - min(overheads)
    assert smallest > 100_000, (
        "the searchable path added almost nothing; the font is probably not "
        "being embedded at all: %r" % (overheads,)
    )
    assert spread < 0.10 * smallest, (
        "font overhead scales with page count (%r, spread %d). That means the "
        "font is embedded per page, which breaks the cost model for long books."
        % (overheads, spread)
    )


def test_the_pdf_still_has_a_text_layer(source_page) -> None:
    """Guards against passing the size test by not embedding anything."""
    from application.export.service import (
        ExportFormat, ExportPage, ExportRequest, ExportService,
    )
    from infrastructure.export.qt_free import QtFreePdfComposer

    with Image.open(source_page) as image:
        width, _ = image.size
    entry = ExportPage(
        page_id="p0", filename="0001.png",
        source_provider=lambda: io.open(source_page, "rb").read(),
        regions=({"geometry": {"bbox": [40, 120, max(width - 80, 100), 70]},
                  "ocr_text": "こんにちは世界", "translated_text": ""},),
    )
    service = ExportService(history_store=None, pdf_composer=QtFreePdfComposer())
    target = os.path.join(os.path.dirname(source_page), "_ac4_text.pdf")
    try:
        service.export(ExportRequest(
            book_id="ac4", chapter_id="ac4", format=ExportFormat.PDF,
            output_path=target, pages=[entry], export_id="ac4",
            format_options={"pdf_content": "searchable_dual_layer"},
        ))
        document = pymupdf.open(target)
        try:
            text = document.load_page(0).get_text()
        finally:
            document.close()
        assert "こんにちは世界" in text, "text layer missing: %r" % (text,)
    finally:
        if os.path.exists(target):
            os.remove(target)
