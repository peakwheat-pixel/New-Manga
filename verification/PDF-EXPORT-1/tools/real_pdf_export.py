"""PDF-EXPORT-1: real PDF export through the production Core (wire-level in-process).

Uses the completed-run data root (8 pages, 3 with translated renders), the real
production assembly (`assemble_production_core`), the real `CoreServiceServer`
host-control export-grant handler, and the real `handle_start_export` entry —
only the Host-side grant minting is reproduced locally (same HMAC recipe the
HostIssuer uses; see HostIssuer.MintExportGrant).

Outputs:
  <task-env>/out/pdf-export-<stamp>.pdf   the real PDF artefact
  <task-env>/evidence/pdf-export.json     validation + sha256 + request/response log
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import shutil
import sqlite3
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


def prepare_root() -> Path:
    root = TASK_ENV / "data-root"
    if root.exists():
        shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(SOURCE_ROOT, root)
    # A copied root keeps the *old* absolute binding identity in the catalog and
    # derived/lock state; drop them so the Core re-binds to this copy (same
    # recipe as the RUN-OCR-DIAG-1 / CORE-PIPELINE-FIX-1 verification roots).
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
    for sub in ("derived", "catalog", "managed"):
        target = root / sub
        target.mkdir(parents=True, exist_ok=True)
        if sub != "managed":
            for child in list(target.iterdir()):
                if child.is_dir():
                    shutil.rmtree(child, ignore_errors=True)
                else:
                    child.unlink(missing_ok=True)
    return root


def main() -> int:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    root = prepare_root()
    os.environ["NEWMANGA_DATA_ROOT"] = str(root)
    os.environ["M2RC1_DERIVED_ROOT"] = str(root / "derived")
    os.environ["M2RC2_CATALOG_DB"] = str(root / "catalog" / "catalog.sqlite")
    os.environ["M2RC1_MANAGED_ROOT"] = str(root / "managed")
    sys.path.insert(0, r"G:\CODEX\New Manga\src")

    import bootstrap.core_service as cs
    from infrastructure.export.target_refs import _signature

    evidence: dict = {
        "ac": "AC2/AC3", "stamp": stamp,
        "source_root": str(SOURCE_ROOT), "data_root": str(root),
        "book_id": BOOK_ID, "chapter_id": CHAPTER_ID,
        "ordered_page_ids": TRANSLATED_PAGES,
        "request": {"format": "pdf", "format_options": {"pdf_content": "image_only"},
                    "stale_policy": "abort"},
        "python": sys.version.split()[0],
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out_dir = TASK_ENV / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    target_path = out_dir / f"BOOK-FIXTURE-1-第1章-{stamp}.pdf"

    cs._ensure_preview_namespace(root / "catalog" / "catalog.sqlite", root / "derived")
    core = cs.assemble_production_core(root)
    server = cs.CoreServiceServer(core)
    try:
        # --- Host-side equivalent: mint + register an export grant for pdf ---
        signing_key = os.urandom(32)
        grant_id = secrets.token_urlsafe(24)[:32]
        session_id = "pdf-export-verification"
        expires_at = time.time() + 120.0
        signature = _signature(signing_key, grant_id, session_id, target_path,
                               "pdf", True, expires_at)
        signing_key_b64 = base64.urlsafe_b64encode(signing_key).decode().rstrip("=")
        registered = server._register_export_target({
            "grant_id": grant_id, "session_id": session_id,
            "target_path": str(target_path), "format": "pdf",
            "replace_existing": True, "expires_at": expires_at,
            "signing_key": signing_key_b64, "signature": signature,
        })
        target_ref = f"etref1.{grant_id}.{signature}"
        evidence["grant"] = {"registered": registered, "target_path": str(target_path),
                             "format": "pdf", "grant_id_len": len(grant_id)}

        started = server.handle_start_export({
            "book_id": BOOK_ID,
            "chapter_ids": [CHAPTER_ID],
            "ordered_page_ids": list(TRANSLATED_PAGES),
            "format": "pdf",
            "format_options": {"pdf_content": "image_only"},
            "stale_policy": "abort",
            "target_ref": target_ref,
        })
        evidence["start_response"] = started
        export_id = started.get("export_id")
        polls = []
        deadline = time.time() + 120
        snapshot = started
        while time.time() < deadline:
            snapshot = server._exports.snapshot(export_id)
            polls.append({"t_ms": round((time.time() - (deadline - 120)) * 1000, 1),
                          "status": snapshot.get("status"),
                          "completed_pages": snapshot.get("completed_pages"),
                          "total_pages": snapshot.get("total_pages")})
            if snapshot.get("status") in ("completed", "failed", "cancelled", "skipped"):
                break
            time.sleep(0.1)
        evidence["snapshot"] = snapshot
        evidence["polls"] = polls
        evidence["export_id"] = export_id
    finally:
        try:
            core.conn.close()
        except Exception:
            pass

    # --- independent artefact validation ---
    if target_path.is_file():
        data = target_path.read_bytes()
        import pymupdf

        doc = pymupdf.open(str(target_path))
        pages = []
        for index, page in enumerate(doc):
            pix = page.get_pixmap(dpi=36)
            samples = pix.samples
            non_white = sum(1 for i in range(0, len(samples), 3 * 97) if samples[i] < 240)
            pages.append({
                "page": index + 1,
                "width_pt": round(page.rect.width, 3),
                "height_pt": round(page.rect.height, 3),
                "images": len(page.get_images()),
                "text_chars": len(page.get_text()),
                "ink_samples": non_white,
            })
        db_pages = []
        con = sqlite3.connect("file:%s?mode=ro" % str(root / "library.db").replace("\\", "/"), uri=True)
        con.row_factory = sqlite3.Row
        for row in con.execute(
            "select page_id, width, height from pages where page_id in (%s) order by sort_order"
            % ",".join("?" * len(TRANSLATED_PAGES)), TRANSLATED_PAGES,
        ):
            db_pages.append(dict(row))
        con.close()
        evidence["artifact"] = {
            "path": str(target_path), "bytes": len(data),
            "header": data[:8].decode("latin-1"), "eof": data[-6:].decode("latin-1"),
            "sha256": sha256_file(target_path),
            "pdf_page_count": doc.page_count, "pages": pages,
            "db_pages": db_pages,
            "page_count_matches": doc.page_count == len(TRANSLATED_PAGES),
            "sizes_match_db": all(
                abs(p["width_pt"] - db["width"]) < 0.01 and abs(p["height_pt"] - db["height"]) < 0.01
                for p, db in zip(pages, db_pages)
            ) and len(pages) == len(db_pages),
        }
        doc.close()
    else:
        evidence["artifact"] = {"path": str(target_path), "missing": True}

    evidence["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    out = TASK_ENV / "evidence" / f"pdf-export-{stamp}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    latest = TASK_ENV / "evidence" / "pdf-export.json"
    latest.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    artifact = evidence.get("artifact", {})
    print(json.dumps({
        "status": (evidence.get("snapshot") or {}).get("status"),
        "error_code": (evidence.get("snapshot") or {}).get("error_code"),
        "artifact": {k: artifact.get(k) for k in (
            "bytes", "sha256", "pdf_page_count", "page_count_matches", "sizes_match_db")},
        "pages": artifact.get("pages"),
        "evidence": str(latest),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
