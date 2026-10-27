#!/usr/bin/env python3
"""S4-CMD-BATCH-1 fixture: seed a region-write / reader-progress data root.

This is a *fixture* script, not product code. It runs the production assembly and the
production import/editing/artifact use cases inside an isolated data root (never the real
``%APPDATA%``, never the repository tree), so the frozen ``core_service.exe`` can execute the
region write face (set_region_type / restore_region_revision / rerender_page /
resolve_page_resource) and the reader progress face (SaveReadingProgress /
GetReaderProjection) with *valid* targets.

Source data (first that applies):
  1. ``--source-data-root`` / ``$NEWMANGA_BOOK_FIXTURE_ROOT``: copy the durable state of an
     already-imported BOOK-FIXTURE data root (library.db + managed/) and reuse its book,
     chapter and pages. This is the standard path in the team test environment.
  2. ``--pages-root``: import real manga pages into a fresh book/chapter WEBTOON chapter
     (the BOOK-FIXTURE-1 helper method; used when no BOOK-FIXTURE is available).

What it always adds through production use cases:
  * one CLEAN artifact for the first page (plain PNG; the renderer's content decoder passes
    non-NMFR payloads through unchanged) -- the required input of ``rerender_page``;
  * one translated region on that page confirmed to a final translation, so the rerender
    report has a real region to render and the retype/restore faces have real revisions.

Output: one JSON object (stdout and/or ``--json-out``) with the ids the C# integration test
consumes: ``book_id``, ``chapter_id``, ``chapter_type``, ``page_id``, ``page_count``,
``region_id``, ``region_revision_no``, ``clean_artifact_id`` and the library.db sha256.

Usage (called by scripts/test.ps1, can also be re-run by hand):
  python apps/desktop-avalonia/scripts/seed_s4_region_fixture.py \
      --data-root "G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"
DEFAULT_PAGES_ROOT = (
    REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "oc material" / "17"
)
DEFAULT_BOOK_FIXTURE = Path(
    r"G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data"
)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
TITLE = "S4-CMD-BATCH-1 region fixture"
CHAPTER_TITLE = "第 1 章"
PAGE_LIMIT = 8
REGION_TEXT = "S4 区域排版测试文本"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--source-data-root", default="")
    parser.add_argument("--pages-root", default="")
    parser.add_argument("--page-limit", type=int, default=PAGE_LIMIT)
    parser.add_argument("--json-out", default="")
    return parser.parse_args(argv)


def _guard_data_root(data_root: Path) -> None:
    resolved = data_root.resolve()
    repo = REPO_ROOT.resolve()
    if resolved == repo or repo in resolved.parents:
        raise SystemExit(f"refusing to seed inside the repository tree: {resolved}")
    if resolved.exists():
        shutil.rmtree(resolved)


def _sha256(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in paths:
        if path.is_file():
            digest.update(path.read_bytes())
    return digest.hexdigest()


def _resolve_source_data_root(args: argparse.Namespace) -> Path | None:
    for candidate in (
        args.source_data_root,
        os.environ.get("NEWMANGA_BOOK_FIXTURE_ROOT", ""),
        str(DEFAULT_BOOK_FIXTURE),
    ):
        if not candidate:
            continue
        root = Path(candidate).expanduser()
        if (root / "library.db").is_file():
            return root.resolve()
    return None


def _copy_durable_state(source: Path, destination: Path) -> None:
    """Copy only durable state: the SQLite library (+WAL sidecars) and Managed Copy files.

    Derived caches carry a namespace-binding identity of the source root, so they are never
    copied: the production assembly rebuilds them for the destination root.
    """
    destination.mkdir(parents=True, exist_ok=True)
    for name in ("library.db", "library.db-wal", "library.db-shm"):
        candidate = source / name
        if candidate.is_file():
            shutil.copy2(candidate, destination / name)
    if not (destination / "library.db").is_file():
        raise SystemExit(f"source data root has no library.db: {source}")
    managed = source / "managed"
    if managed.is_dir():
        shutil.copytree(managed, destination / "managed", dirs_exist_ok=True)


def _selected_pages(pages_root: Path, limit: int) -> list[Path]:
    images = sorted(
        path
        for path in pages_root.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if not images:
        raise SystemExit(f"no {sorted(IMAGE_SUFFIXES)} pages under {pages_root}")
    return images[: max(1, limit)]


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    data_root = Path(args.data_root).expanduser().resolve()
    _guard_data_root(data_root)

    derived_root = data_root / "derived"
    catalog_db = data_root / "catalog" / "catalog.sqlite"
    managed_root = data_root / "managed"
    for directory in (data_root, derived_root, catalog_db.parent, managed_root):
        directory.mkdir(parents=True, exist_ok=True)

    source_root = _resolve_source_data_root(args)
    pages_root = Path(args.pages_root).expanduser() if args.pages_root else DEFAULT_PAGES_ROOT

    sys.path.insert(0, str(SRC_ROOT))
    from application.importing.images.ports import ImportSource  # noqa: PLC0415
    from bootstrap.core_service import (  # noqa: PLC0415
        _ensure_preview_namespace,
        assemble_production_core,
    )
    from domain.books.entities import ChapterType  # noqa: PLC0415
    from domain.regions.entities import (  # noqa: PLC0415
        BBox,
        RegionGeometry,
        RegionType,
        SfxPolicy,
    )
    from infrastructure.sqlite.artifacts import SqliteArtifactRepository  # noqa: PLC0415
    from PIL import Image  # noqa: PLC0415
    from ports.repositories.artifacts import (  # noqa: PLC0415
        ArtifactType,
        ContentProvider,
        NewArtifact,
        PendingArtifactCommit,
    )

    if source_root is not None:
        _copy_durable_state(source_root, data_root)
    elif not pages_root.is_dir():
        raise SystemExit(
            "no source data root and no usable --pages-root; cannot build the S4 region fixture "
            f"(tried BOOK-FIXTURE and {pages_root})"
        )

    _ensure_preview_namespace(catalog_db, derived_root)
    core = assemble_production_core(data_root)
    try:
        book = None
        chapter = None
        report = None
        if source_root is not None:
            books = core.repository.list_books()
            if not books:
                raise SystemExit(f"source data root has no books: {source_root}")
            book = books[0]
            chapters = core.repository.list_chapters(book.book_id)
            if not chapters:
                raise SystemExit(f"source book has no chapters: {book.book_id}")
            chapter = chapters[0]
            imported = core.repository.list_pages(chapter.chapter_id)
            if not imported:
                raise SystemExit(f"source chapter has no pages: {chapter.chapter_id}")
        else:
            book = core.library.create_book(TITLE, default_chapter_type=ChapterType.WEBTOON)
            chapter = core.library.create_chapter(
                book.book_id,
                CHAPTER_TITLE,
                chapter_number="1",
                chapter_type=ChapterType.WEBTOON,
            )
            sources = [
                ImportSource(path.name, lambda path=path: path.read_bytes())
                for path in _selected_pages(pages_root.resolve(), args.page_limit)
            ]
            report = core.importer.import_files(chapter.chapter_id, sources)
            if report.failed:
                raise SystemExit(
                    "import failed for: " + ", ".join(f.filename for failure in report.failed)
                )
            imported = core.repository.list_pages(chapter.chapter_id)
            if not imported:
                raise SystemExit("fixture import produced no pages")
        page = imported[0]

        # CLEAN artifact: the render input ``rerender_page`` requires. A plain PNG is a valid
        # content frame for the production decoder (non-NMFR payloads pass through unchanged).
        clean_png = data_root / "_seed-clean.png"
        with Image.new("RGB", (page.width, page.height), (255, 255, 255)) as clean:
            clean.save(clean_png, format="PNG")
        artifacts = SqliteArtifactRepository(core.conn, core.storage)
        artifact = artifacts.create_artifact(
            NewArtifact(
                book_id=book.book_id,
                chapter_id=chapter.chapter_id,
                page_id=page.page_id,
                artifact_type=ArtifactType.CLEAN,
            )
        )
        commit = artifacts.commit_revision(
            PendingArtifactCommit(
                artifact_id=artifact.artifact_id,
                content_provider=ContentProvider(payload=clean_png.read_bytes()),
                mime_type="image/png",
                expected_current_revision_id=None,
                file_suffix=".png",
            )
        )
        clean_png.unlink(missing_ok=True)
        if commit.status.value != "committed":
            raise SystemExit(f"clean artifact commit failed: {commit.detail}")

        # One translated region: creation + manual save + confirm revisions, so the retype and
        # restore faces act on real history (restore targets revision 1).
        margin_x = max(8, page.width // 10)
        margin_y = max(8, page.height // 10)
        geometry = RegionGeometry(
            bbox=BBox(
                margin_x,
                margin_y,
                max(64, page.width - 2 * margin_x),
                max(64, page.height - 2 * margin_y),
            )
        )
        region = core.editing.create_region(
            page.page_id,
            geometry,
            region_type=RegionType.SPEECH,
            reading_order=1,
            sfx_policy=SfxPolicy.SKIP,
        )
        core.editing.save_manual_translation(region.region_id, REGION_TEXT)
        confirmed_no = core.editing.confirm_final(region.region_id)
        current = core.editing.get_region(region.region_id)
        if not current.text.final_translation.strip():
            raise SystemExit("seeded region has no final translation")
        history = core.editing.list_revision_summaries(region.region_id)
        if history["current_revision_no"] != confirmed_no:
            raise SystemExit("seeded region revision pointer does not match the confirm revision")

        payload = {
            "status": "created",
            "title": book.title,
            "data_root": str(data_root),
            "source": "book-fixture" if source_root is not None else f"pages:{pages_root}",
            "source_data_root": str(source_root) if source_root is not None else None,
            "book_id": book.book_id,
            "chapter_id": chapter.chapter_id,
            "chapter_title": chapter.title,
            "chapter_type": str(getattr(chapter.chapter_type, "value", chapter.chapter_type)),
            "page_id": page.page_id,
            "page_width": page.width,
            "page_height": page.height,
            "page_count": len(imported),
            "page_ids": [item.page_id for item in imported],
            "source_filenames": [item.source_filename for item in imported],
            "region_id": region.region_id,
            "region_revision_no": history["current_revision_no"],
            "region_type": str(current.region_type.value),
            "region_text": current.text.final_translation,
            "clean_artifact_id": artifact.artifact_id,
            "clean_revision_no": getattr(commit.revision, "revision_no", None),
            "library_db_sha256": _sha256(
                [data_root / "library.db", data_root / "library.db-wal"]
            ),
            "import_report": None
            if report is None
            else {
                "imported": len(report.imported),
                "failed": [failure.filename for failure in report.failed],
            },
        }
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
