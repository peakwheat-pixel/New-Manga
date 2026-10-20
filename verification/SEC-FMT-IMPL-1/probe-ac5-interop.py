# -*- coding: utf-8 -*-
"""AC5: validate exported CBZ and PDF with INDEPENDENT third-party tools.

Not with the project's own code. 7-Zip is a separate ZIP implementation;
PyMuPDF (fitz) is MuPDF, a separate PDF implementation. Neither is a user's
comic reader, which is the point recorded in the limitation.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, r"G:\CODEX\New Manga")
sys.path.insert(0, r"G:\CODEX\New Manga\src")

from PIL import Image

from application.export.service import (
    ExportFormat,
    ExportPage,
    ExportRequest,
    ExportService,
    JsonHistoryDocumentStore,
)
from infrastructure.export.qt_free import QtFreePdfComposer

SEVEN_ZIP = r"C:\Program Files\7-Zip\7z.exe"
OUT_JSON = r"G:\CODEX\New Manga\verification\SEC-FMT-IMPL-1\ac5-interop-results.json"


def make_page(index: int) -> bytes:
    """A page that is obviously not blank and has a distinct size per index."""
    buffer = io.BytesIO()
    image = Image.new("RGB", (600 + index * 10, 900), (240, 235, 225))
    image.save(buffer, "PNG", optimize=False)
    return buffer.getvalue()


def build_service(workdir: str) -> ExportService:
    store = JsonHistoryDocumentStore(os.path.join(workdir, "history.json"))
    return ExportService(store, pdf_composer=QtFreePdfComposer())


def export_one(service: ExportService, fmt: ExportFormat, path: str) -> dict:
    pages = tuple(
        ExportPage(page_id="p%d" % i, filename="%03d.png" % (i + 1),
                   source_provider=lambda i=i: make_page(i))
        for i in range(3)
    )
    request = ExportRequest(
        book_id="AC5 Book", chapter_id="ch1", format=fmt,
        output_path=path, pages=pages,
        export_id="ac5-" + fmt.value,
        book_metadata={"title": "AC5 Book", "author": "DSH"},
        chapter_metadata={"title": "Chapter 1", "chapter_number": "1"},
    )
    result = service.export(request)
    return {
        "format": fmt.value,
        "status": result.status.value,
        "path": str(result.output_path),
        "size_bytes": os.path.getsize(result.output_path) if result.output_path else 0,
        "page_count": len(result.page_ids),
    }


def verify_cbz_with_7zip(path: str) -> dict:
    if not os.path.exists(SEVEN_ZIP):
        return {"available": False}
    proc = subprocess.run([SEVEN_ZIP, "l", "-ba", path],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    entries = [l.split()[-1] for l in (proc.stdout or "").split("\n")
               if l.strip() and not l.strip().startswith("--")]
    test = subprocess.run([SEVEN_ZIP, "t", path],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    return {
        "available": True,
        "tool": "7-Zip " + os.path.basename(SEVEN_ZIP),
        "exit_code_list": proc.returncode,
        "exit_code_test": test.returncode,
        "test_ok": test.returncode == 0 and "Everything is Ok" in (test.stdout or ""),
        "entry_count": len(entries),
        "entries": entries[:12],
        "has_comicinfo": any("ComicInfo.xml" in e for e in entries),
    }


def verify_pdf_with_fitz(path: str) -> dict:
    try:
        import pymupdf as fitz
    except Exception:
        try:
            import fitz  # noqa
        except Exception:
            return {"available": False}
    doc = fitz.open(path)
    pages = doc.page_count
    sizes = []
    texts = 0
    for i in range(min(pages, 5)):
        page = doc.load_page(i)
        rect = page.rect
        sizes.append([round(rect.width, 1), round(rect.height, 1)])
        texts += len(page.get_text().strip())
    images = sum(len(doc.load_page(i).get_images(full=True)) for i in range(min(pages, 5)))
    doc.close()
    return {
        "available": True,
        "tool": "PyMuPDF (MuPDF)",
        "page_count": pages,
        "page_sizes_pt": sizes,
        "embedded_images_first5": images,
        "text_chars_first5": texts,
        "opened_ok": pages > 0,
    }


def render_pdf_with_chrome(path: str, workdir: str) -> dict:
    chrome = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome):
        return {"available": False}
    out = os.path.join(workdir, "render.png")
    proc = subprocess.run(
        [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
         "--screenshot=" + out, "--window-size=800,1000",
         "file:///" + path.replace("\\", "/")],
        capture_output=True, text=True, timeout=120)
    return {
        "available": True,
        "tool": "Chrome headless",
        "exit_code": proc.returncode,
        "rendered": os.path.exists(out),
        "png_bytes": os.path.getsize(out) if os.path.exists(out) else 0,
    }


def main():
    workdir = tempfile.mkdtemp(prefix="ac5-")
    service = build_service(workdir)
    report = {"workdir": workdir, "exports": [], "verifications": {}}

    cbz_path = os.path.join(workdir, "ac5.cbz")
    pdf_path = os.path.join(workdir, "ac5.pdf")

    print("=== exporting ===")
    for fmt, path in ((ExportFormat.CBZ, cbz_path), (ExportFormat.PDF, pdf_path)):
        try:
            info = export_one(service, fmt, path)
            print("  %-4s %-8s %8d bytes  %s"
                  % (info["format"], info["status"], info["size_bytes"],
                     os.path.basename(info["path"])))
            report["exports"].append(info)
        except Exception as exc:
            print("  %-4s FAILED %s: %s" % (fmt.value, type(exc).__name__, str(exc)[:120]))
            report["exports"].append({"format": fmt.value, "error": repr(exc)[:200]})

    print("\n=== verifying CBZ with 7-Zip ===")
    if os.path.exists(cbz_path):
        r = verify_cbz_with_7zip(cbz_path)
        report["verifications"]["cbz_7zip"] = r
        if r.get("available"):
            print("  list exit=%s test exit=%s ok=%s entries=%d comicinfo=%s"
                  % (r["exit_code_list"], r["exit_code_test"], r["test_ok"],
                     r["entry_count"], r["has_comicinfo"]))
            for e in r["entries"][:6]:
                print("    ", e)
        else:
            print("  7-Zip not available")

    print("\n=== verifying PDF with PyMuPDF ===")
    if os.path.exists(pdf_path):
        r = verify_pdf_with_fitz(pdf_path)
        report["verifications"]["pdf_fitz"] = r
        if r.get("available"):
            print("  opened ok=%s pages=%d sizes=%s images=%d"
                  % (r["opened_ok"], r["page_count"], r["page_sizes_pt"],
                     r["embedded_images_first5"]))
        else:
            print("  PyMuPDF not available")

    print("\n=== rendering PDF with Chrome headless ===")
    if os.path.exists(pdf_path):
        r = render_pdf_with_chrome(pdf_path, workdir)
        report["verifications"]["pdf_chrome"] = r
        if r.get("available"):
            print("  exit=%s rendered=%s png_bytes=%d"
                  % (r["exit_code"], r["rendered"], r["png_bytes"]))
        else:
            print("  Chrome not available")

    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=1) + "\n")
    print("\nwritten:", OUT_JSON)


if __name__ == "__main__":
    main()
