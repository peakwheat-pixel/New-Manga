"""SEARCHABLE-PDF-CJK-1 AC2: a real Korean page exports a searchable PDF.

ZCode's F-2: the AC1 evidence table claimed a real 600x18401 Korean page exported
with text '안녕하세요 세계' extractable, but that measurement ran in a shell and
was never committed - so the claim had no artefact behind it, and the only
end-to-end test in the suite used Japanese. An AC whose evidence is a sentence
in a table is not evidence.

This closes it. A real page from 韩漫_KO goes through ExportService with a text
region, and the text is read back out of the PDF.
"""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest
from PIL import Image

pymupdf = pytest.importorskip("pymupdf", reason="PyMuPDF is required")

Image.MAX_IMAGE_PIXELS = 200_000_000

# V11R-A-4: repo-relative assets; NEWMANGA_GOLDEN_ASSETS overrides for an out-of-tree asset root.
REPO_ROOT = Path(__file__).resolve().parents[2]
ROOT = os.environ.get("NEWMANGA_GOLDEN_ASSETS") or str(REPO_ROOT / "test_assets" / "comic_golden_suite")
KOREAN_TREE = os.path.join(ROOT, "韩漫_KO")
def _korean_pages():
    for root, _, files in os.walk(KOREAN_TREE):
        for name in files:
            if name.lower().endswith((".png", ".jpg", ".jpeg")):
                yield os.path.join(root, name)


if next(_korean_pages(), None) is None:
    pytest.skip(
        f"no Korean page images under {KOREAN_TREE} (tracked manifests only); set "
        "NEWMANGA_GOLDEN_ASSETS or check out the asset bundle (environmental, not a product failure)",
        allow_module_level=True,
    )
KOREAN_TEXT = "안녕하세요 세계"


def _find_korean_page():
    """Any real Korean image wide and tall enough to place a text region on."""
    candidates = []
    for root, _, files in os.walk(KOREAN_TREE):
        for name in files:
            if name.lower().endswith((".png", ".jpg", ".jpeg")):
                if "visualization" in name.lower():
                    continue
                candidates.append(os.path.join(root, name))
    candidates.sort(key=lambda path: os.path.getsize(path))
    for path in candidates:
        try:
            with Image.open(path) as image:
                width, height = image.size
        except Exception:
            continue
        if width >= 400 and height >= 400:
            return path
    return None


@pytest.fixture(scope="module")
def korean_page():
    page = _find_korean_page()
    if page is None:
        pytest.fail("no real Korean page under 韩漫_KO - the asset tree is "
                    "missing, which is an environment problem worth seeing")
    return page


def test_real_korean_page_yields_extractable_text(korean_page) -> None:
    """AC1/AC2 end to end: compose, embed, open, extract."""
    from application.export.service import (
        ExportFormat, ExportPage, ExportRequest, ExportService,
    )
    from infrastructure.export.qt_free import QtFreePdfComposer

    with Image.open(korean_page) as image:
        width, height = image.size

    entry = ExportPage(
        page_id="p0", filename="0001.png",
        source_provider=lambda: io.open(korean_page, "rb").read(),
        regions=({"geometry": {"bbox": [40, 120, max(width - 80, 100), 70]},
                  "ocr_text": KOREAN_TEXT, "translated_text": ""},),
    )
    service = ExportService(history_store=None, pdf_composer=QtFreePdfComposer())
    target = os.path.join(os.path.dirname(korean_page), "_ko_e2e.pdf")
    try:
        service.export(ExportRequest(
            book_id="ko", chapter_id="ko", format=ExportFormat.PDF,
            output_path=target, pages=[entry], export_id="ko",
            format_options={"pdf_content": "searchable_dual_layer"},
        ))
        document = pymupdf.open(target)
        try:
            page = document.load_page(0)
            text = page.get_text()
            fonts = [entry[3] for entry in page.get_fonts()]
        finally:
            document.close()
    finally:
        if os.path.exists(target):
            os.remove(target)

    assert fonts, "no font embedded - the text layer cannot exist without one"
    assert KOREAN_TEXT in text, (
        "Korean text did not survive the round trip. extracted: %r. A text "
        "layer that renders boxes would look fine in a screenshot and fail "
        "here, which is why this asserts on the string and not on the bytes."
        % (text,)
    )


def test_korean_page_still_renders(korean_page) -> None:
    """Embedding a text layer must not spoil the image underneath it."""
    from application.export.service import (
        ExportFormat, ExportPage, ExportRequest, ExportService,
    )
    from infrastructure.export.qt_free import QtFreePdfComposer

    with Image.open(korean_page) as image:
        width, _ = image.size

    entry = ExportPage(
        page_id="p0", filename="0001.png",
        source_provider=lambda: io.open(korean_page, "rb").read(),
        regions=({"geometry": {"bbox": [40, 120, max(width - 80, 100), 70]},
                  "ocr_text": KOREAN_TEXT, "translated_text": ""},),
    )
    service = ExportService(history_store=None, pdf_composer=QtFreePdfComposer())
    target = os.path.join(os.path.dirname(korean_page), "_ko_render.pdf")
    try:
        service.export(ExportRequest(
            book_id="ko", chapter_id="ko", format=ExportFormat.PDF,
            output_path=target, pages=[entry], export_id="ko",
            format_options={"pdf_content": "searchable_dual_layer"},
        ))
        document = pymupdf.open(target)
        try:
            pixmap = document.load_page(0).get_pixmap(dpi=24)
        finally:
            document.close()
    finally:
        if os.path.exists(target):
            os.remove(target)

    rendered = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
    colours = rendered.getcolors(maxcolors=1_000_000) or []
    assert len(colours) > 1, (
        "rendered page has a single colour - the image stream is gone"
    )
    assert rendered.convert("L").histogram(), "no pixel data at all"
