"""PDF-EXPORT-1 supplementary verification.

Two extra cases beyond the wire-level image_only export:

  A) engine-level 8-page PDF of the whole 8-page book (3 pages have translated
     renders, 5 pages are text-free and fall back to the original under
     stale_policy=continue_existing) — the literal AC3 "8 页" reading.
  B) wire-level searchable_dual_layer PDF (text layer over the translated pages)
     if the data root carries regions with text.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import shutil
import sys
import time
from pathlib import Path

TASK_ENV = Path(r"G:\CODEX\New Manga.workspace\task-envs\PDF-EXPORT-1")
SOURCE_ROOT = Path(
    r"G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-2\data-roots\data-root-full-chain"
)
BOOK_ID = "14340ddad0ed472fbe687fe12340c5d8"
CHAPTER_ID = "240bdba549b74281bfc6d901b1a7abd7"
TRANSLATED_PAGES = [
    "f52f2772e8044557a72e82f5ea6ab932",
    "4f8a24147b3044deabf4f5a2dd83b84f",
    "a607fc4ca3034f47b5bc43d59f94f2ca",
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def prepare_root(tag: str) -> Path:
    root = TASK_ENV / ("data-root-" + tag)
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(SOURCE_ROOT, root)
    for pat in ("library.db-wal", "library.db-shm", "library.db.run-owner.lock",
                "catalog/catalog.sqlite", "catalog/catalog.sqlite-wal",
                "catalog/catalog.sqlite-shm", "derived/.preview-lifecycle.lock"):
        target = root / pat
        try:
            if target.is_dir():
                shutil.rmtree(target)
            elif target.exists():
                target.unlink()
        except OSError:
            pass
    for sub in ("derived", "catalog"):
        target = root / sub
        target.mkdir(parents=True, exist_ok=True)
        for child in list(target.iterdir()):
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
    return root


def validate(path: Path, expected_sizes) -> dict:
    import pymupdf

    data = path.read_bytes()
    doc = pymupdf.open(str(path))
    pages = []
    for index, page in enumerate(doc):
        pix = page.get_pixmap(dpi=36)
        samples = pix.samples
        ink = sum(1 for i in range(0, len(samples), 3 * 97) if samples[i] < 240)
        pages.append({
            "page": index + 1,
            "width_pt": round(page.rect.width, 3),
            "height_pt": round(page.rect.height, 3),
            "images": len(page.get_images()),
            "text_chars": len(page.get_text()),
            "ink_samples": ink,
        })
    sizes_ok = (expected_sizes is not None and len(pages) == len(expected_sizes)
                and all(abs(p["width_pt"] - w) < 0.01 and abs(p["height_pt"] - h) < 0.01
                        for p, (w, h) in zip(pages, expected_sizes)))
    result = {
        "path": str(path), "bytes": len(data),
        "header": data[:8].decode("latin-1"), "eof": data[-6:].decode("latin-1"),
        "sha256": sha256_file(path), "pdf_page_count": doc.page_count,
        "pages": pages, "sizes_match": sizes_ok,
    }
    doc.close()
    return result


def main() -> int:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    evidence: dict = {"ac": "AC3 supplementary", "stamp": stamp,
                      "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    root = prepare_root("supplementary")
    os.environ["NEWMANGA_DATA_ROOT"] = str(root)
    os.environ["M2RC1_DERIVED_ROOT"] = str(root / "derived")
    os.environ["M2RC2_CATALOG_DB"] = str(root / "catalog" / "catalog.sqlite")
    os.environ["M2RC1_MANAGED_ROOT"] = str(root / "managed")
    sys.path.insert(0, r"G:\CODEX\New Manga\src")

    import bootstrap.core_service as cs
    from application.export import ExportPage, ExportFormat, ExportRequest, StalePolicy
    from infrastructure.export.target_refs import _signature

    cs._ensure_preview_namespace(root / "catalog" / "catalog.sqlite", root / "derived")
    core = cs.assemble_production_core(root)
    out_dir = TASK_ENV / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    server = cs.CoreServiceServer(core)
    try:
        # ---------- A) engine-level 8-page export ----------
        # list_pages already returns the chapter's reading order
        ordered = list(core.reader_catalog.list_pages(CHAPTER_ID))
        export_pages = []
        for page in ordered:
            translated_ok = bool(page.translated_path and page.translated_revision_id)
            export_pages.append(ExportPage(
                page_id=page.page_id, filename=page.filename,
                source_provider=lambda ref=page.original_path: server._read_verified_managed(ref),
                translated_provider=(lambda ref=page.translated_path: server._read_verified_managed(ref))
                if translated_ok else None,
                translated_revision_id=page.translated_revision_id,
                current_translated_revision_id=page.current_translated_revision_id,
                rendered_from_revision_id=page.rendered_from_revision_id,
                current_source_revision_id=page.current_source_revision_id,
                regions=tuple(server._export_regions(page.page_id)),
                sha256=page.translated_sha256 or "",
            ))
        path8 = out_dir / f"BOOK-FIXTURE-1-8pages-{stamp}.pdf"
        result8 = core.export_service.export(ExportRequest(
            book_id=BOOK_ID, chapter_id=CHAPTER_ID, format=ExportFormat.PDF,
            output_path=path8, pages=tuple(export_pages), mode="translated",
            stale_policy=StalePolicy.CONTINUE, export_id=f"exp-8pages-{stamp}",
            format_options={"pdf_content": "image_only"},
            book_metadata={"title": "BOOK-FIXTURE-1", "author": ""},
            chapter_metadata={"title": "第 1 章", "chapter_ids": [CHAPTER_ID]},
        ))
        db_sizes = [(page.width_px, page.height_px) for page in ordered]
        evidence["engine_8page"] = {
            "status": result8.status.value, "pages_requested": len(export_pages),
            "translated_pages": sum(1 for p in export_pages if p.translated_provider is not None),
            "artifact": validate(path8, db_sizes),
        }

        # ---------- B) wire-level searchable PDF over the translated pages ----------
        target = out_dir / f"BOOK-FIXTURE-1-searchable-{stamp}.pdf"
        signing_key = os.urandom(32)
        grant_id = secrets.token_urlsafe(24)[:32]
        session_id = "pdf-export-searchable"
        expires_at = time.time() + 120.0
        signature = _signature(signing_key, grant_id, session_id, target, "pdf", True, expires_at)
        server._register_export_target({
            "grant_id": grant_id, "session_id": session_id,
            "target_path": str(target), "format": "pdf",
            "replace_existing": True, "expires_at": expires_at,
            "signing_key": base64.urlsafe_b64encode(signing_key).decode().rstrip("="),
            "signature": signature,
        })
        started = server.handle_start_export({
            "book_id": BOOK_ID, "chapter_ids": [CHAPTER_ID],
            "ordered_page_ids": list(TRANSLATED_PAGES), "format": "pdf",
            "format_options": {"pdf_content": "searchable_dual_layer"},
            "stale_policy": "abort",
            "target_ref": f"etref1.{grant_id}.{signature}",
        })
        export_id = started.get("export_id")
        snapshot = started
        deadline = time.time() + 120
        while time.time() < deadline:
            snapshot = server._exports.snapshot(export_id)
            if snapshot.get("status") in ("completed", "failed", "cancelled", "skipped"):
                break
            time.sleep(0.1)
        evidence["wire_searchable"] = {
            "snapshot": snapshot,
            "error_code": snapshot.get("error_code"),
            "error": snapshot.get("error"),
            "artifact": validate(target, [(1200, 1660), (1200, 1660), (1200, 726)])
            if target.is_file() else None,
        }
    except BaseException as error:  # noqa: BLE001
        import traceback
        evidence["exception"] = f"{type(error).__name__}: {error}"
        evidence["traceback"] = traceback.format_exc()[-3000:]
    finally:
        try:
            core.conn.close()
        except Exception:
            pass
        evidence["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        out = TASK_ENV / "evidence" / f"supplementary-{stamp}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        latest = TASK_ENV / "evidence" / "supplementary.json"
        latest.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({
            "engine_8page": {
                "status": evidence.get("engine_8page", {}).get("status"),
                "requested": evidence.get("engine_8page", {}).get("pages_requested"),
                "translated": evidence.get("engine_8page", {}).get("translated_pages"),
                "artifact": {k: evidence.get("engine_8page", {}).get("artifact", {}).get(k)
                             for k in ("bytes", "sha256", "pdf_page_count", "sizes_match")},
                "pages": [{"page": p["page"], "w": p["width_pt"], "h": p["height_pt"],
                           "text": p["text_chars"]}
                          for p in evidence.get("engine_8page", {}).get("artifact", {}).get("pages", [])],
            },
            "wire_searchable": {
                "status": evidence.get("wire_searchable", {}).get("snapshot", {}).get("status"),
                "error_code": evidence.get("wire_searchable", {}).get("error_code"),
                "artifact": {k: evidence.get("wire_searchable", {}).get("artifact", {}).get(k)
                             for k in ("bytes", "sha256", "pdf_page_count", "sizes_match")}
                if evidence.get("wire_searchable", {}).get("artifact") else None,
                "text_chars": [p["text_chars"] for p in
                               (evidence.get("wire_searchable", {}).get("artifact") or {}).get("pages", [])],
            },
            "exception": evidence.get("exception"),
            "evidence": str(latest),
        }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
