"""Sanity: existing QtFreePdfComposer via ExportService (image_only + searchable)."""
import hashlib
from pathlib import Path

from PIL import Image
import io

from application.export import (
    ExportFormat,
    ExportPage,
    ExportRequest,
    ExportService,
    JsonHistoryDocumentStore,
)
from infrastructure.export.qt_free import QtFreePdfComposer

TE = Path(r"G:\CODEX\New Manga.workspace\task-envs\PDF-EXPORT-1")


def png(w, h, color):
    buffer = io.BytesIO()
    Image.new("RGB", (w, h), color).save(buffer, format="PNG")
    return buffer.getvalue()


def page(i, w=800, h=1200, regions=()):
    return ExportPage(
        page_id=f"p{i}", filename=f"{i:03d}.png",
        source_provider=lambda w=w, h=h, i=i: png(w, h, (200 + 10 * i, 255, 255)),
        sha256="0" * 64, regions=tuple(regions),
    )


def run(name, options, regions):
    svc = ExportService(
        JsonHistoryDocumentStore(TE / f"sanity-history-{name}.json"),
        pdf_composer=QtFreePdfComposer(),
    )
    pages = tuple(page(i, regions=regions if i == 1 else ()) for i in (1, 2, 3))
    out = TE / f"sanity-{name}.pdf"
    result = svc.export(ExportRequest(
        book_id="b", chapter_id="c", format=ExportFormat.PDF, output_path=out,
        pages=pages, mode="original", export_id=f"exp-{name}",
        format_options={"pdf_content": options},
    ))
    data = out.read_bytes()
    print(f"[{name}] status={result.status} bytes={len(data)} header={data[:8]!r} eof={data[-6:]!r}")
    print(f"[{name}] file_hash={result.file_hash} sha256={hashlib.sha256(data).hexdigest()}")
    import pymupdf
    doc = pymupdf.open(str(out))
    print(f"[{name}] page_count={doc.page_count}")
    for index, p in enumerate(doc):
        print(f"  page{index + 1}: {p.rect.width:g}x{p.rect.height:g} images={len(p.get_images())} text={len(p.get_text())}")
    doc.close()


if __name__ == "__main__":
    run("image-only", "image_only", ())
    run("searchable", "searchable_dual_layer", (
        {"region_id": "r1", "geometry": {"bbox": [10, 20, 120, 40]},
         "ocr_text": "こんにちは", "translated_text": "Hello"},
    ))
