#!/usr/bin/env python3
"""BOOK-FIXTURE-1 helper: import one test book into an isolated Core data root.

This is a *fixture* script, not product code:

- it runs the PRODUCTION assembly and the PRODUCTION import use case
  (``bootstrap.core_service.assemble_production_core`` +
  ``core.importer.import_files``) inside an isolated data root created by
  ``new-test-book.ps1``; no product source is modified and nothing touches the
  real ``%APPDATA%``;
- the pages are read from the golden-suite fixture tree **in place**
  (read-only reference: no copy into the repo, no managed-copy bypass — the
  importer stores its own Managed Copy under the isolated data root);
- it is IDEMPOTENT: an already-present book with the same title and >0 pages is
  reused (``status: "existing"``) instead of creating a duplicate; ``--force``
  soft-deletes the old book first and re-imports.

Output: one JSON object on stdout (and optionally ``--json-out``) with the
book/chapter ids, the ordered page list (source filename + parsed width/height)
and the import report. Protocol/command semantics are untouched.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--pages-root", required=True)
    parser.add_argument("--title", default="BOOK-FIXTURE-1 日漫_JA 测试书")
    parser.add_argument("--chapter-title", default="第 1 章")
    parser.add_argument("--page-limit", type=int, default=8)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--json-out", default="")
    return parser.parse_args(argv)


def _selected_pages(pages_root: Path, limit: int) -> list[Path]:
    images = sorted(
        path
        for path in pages_root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not images:
        raise SystemExit(
            f"no {sorted(IMAGE_SUFFIXES)} pages under {pages_root}"
        )
    return images[: max(1, limit)]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    data_root = Path(args.data_root).expanduser().resolve()
    pages_root = Path(args.pages_root).expanduser().resolve()
    if not pages_root.is_dir():
        raise SystemExit(f"pages root does not exist: {pages_root}")

    # Same startup layout the production Core entry uses (bootstrap/core_service.py main()).
    derived_root = Path(os.environ.get("M2RC1_DERIVED_ROOT", data_root / "derived"))
    catalog_db = Path(
        os.environ.get("M2RC2_CATALOG_DB", data_root / "catalog" / "catalog.sqlite")
    )
    derived_root.mkdir(parents=True, exist_ok=True)
    catalog_db.parent.mkdir(parents=True, exist_ok=True)

    sys.path.insert(0, str(SRC_ROOT))
    from application.importing.images.ports import ImportSource  # noqa: PLC0415
    from bootstrap.core_service import (  # noqa: PLC0415
        _ensure_preview_namespace,
        assemble_production_core,
    )
    from domain.books.entities import ChapterType  # noqa: PLC0415

    pages = _selected_pages(pages_root, args.page_limit)
    _ensure_preview_namespace(catalog_db, derived_root)
    core = assemble_production_core(data_root)
    try:
        existing = [
            book
            for book in core.repository.list_books()
            if book.title == args.title
        ]
        status = "existing"
        report = None
        if existing and not args.force:
            book = existing[0]
        else:
            if existing:  # --force: soft-delete the previous fixture book first
                core.library.delete_book(existing[0].book_id)
            book = core.library.create_book(
                args.title, default_chapter_type=ChapterType.WEBTOON
            )
            chapter = core.library.create_chapter(
                book.book_id,
                args.chapter_title,
                chapter_number="1",
                chapter_type=ChapterType.WEBTOON,
            )
            sources = [
                ImportSource(path.name, lambda path=path: path.read_bytes())
                for path in pages
            ]
            report = core.importer.import_files(chapter.chapter_id, sources)
            status = "created"
        chapters = core.repository.list_chapters(book.book_id)
        if not chapters:
            raise SystemExit(f"book {book.book_id} has no chapter")
        chapter = chapters[0]
        imported_pages = core.repository.list_pages(chapter.chapter_id)
        payload = {
            "status": status,
            "book_id": book.book_id,
            "book_title": book.title,
            "chapter_id": chapter.chapter_id,
            "chapter_title": chapter.title,
            "chapter_type": str(getattr(chapter.chapter_type, "value", chapter.chapter_type)),
            "data_root": str(data_root),
            "pages_root": str(pages_root),
            "pages_requested": args.page_limit,
            "page_count": len(imported_pages),
            "pages": [
                {
                    "page_id": page.page_id,
                    "source_filename": page.source_filename,
                    "order": page.source_order,
                    "width": page.width,
                    "height": page.height,
                    "source_size_bytes": page.source_size_bytes,
                }
                for page in imported_pages
            ],
            "import_report": None
            if report is None
            else {
                "imported": len(report.imported),
                "failed": [failure.filename for failure in report.failed],
            },
        }
        if report is not None and report.failed:
            raise SystemExit(
                "import failed for: " + ", ".join(f.filename for f in report.failed)
            )
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        if args.json_out:
            out = Path(args.json_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    finally:
        core.conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
