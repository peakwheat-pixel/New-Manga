"""TASK-021 trash subset: page-level soft delete, batch restore and
controlled-only purge — real SQLite + real ManagedFileStorage.

Guarantees under test:

- soft delete hides pages from the reader/imports but loses no data; a batch
  restores together (同 batch 恢复);
- permanent deletion removes **controlled data only** — managed files and
  rows — and never anything outside the managed root (user source files are
  simulated as files outside ``tmp managed`` and must survive verbatim);
- unknown batches and purge-without-manifest fail typed, not silently.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance import TrashService  # noqa: E402
from application.maintenance.trash import _JsonTrashManifest  # noqa: E402
from domain.pages.entities import Page  # noqa: E402
from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ImmutablePathViolation,
    ManagedFileStorage,
)
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.library import SqliteLibraryRepository  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

NOW = "2026-09-18T05:00:00+00:00"


@pytest.fixture()
def workspace(tmp_path: Path):
    conn, _opened = open_database(
        tmp_path / "library.db", latest_known_schema_version=max(
            m.schema_version for m in default_migrations()
        )
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    storage = ManagedFileStorage(tmp_path / "managed")
    storage.ensure_layout()
    repository = SqliteLibraryRepository(conn)

    # a "user source file" OUTSIDE the managed root — purge must never touch it
    user_source = tmp_path / "user-side" / "original-art.tiff"
    user_source.parent.mkdir(parents=True, exist_ok=True)
    user_source.write_bytes(b"USER SOURCE BYTES")

    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-1', 'Book', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES ('chapter-1', 'book-1', 'Chapter', ?, ?)",
            (NOW, NOW),
        )

    def make_page(page_id: str, payload: bytes) -> Page:
        relative = f"books/book-1/chapters/chapter-1/original/{page_id}.png"
        (tmp_path / "managed" / Path(relative.replace("/", "\\"))).parent.mkdir(
            parents=True, exist_ok=True
        )
        (tmp_path / "managed" / Path(relative.replace("/", "\\"))).write_bytes(payload)
        page = Page(
            page_id=page_id,
            chapter_id="chapter-1",
            source_filename=f"{page_id}.png",
            source_order=int(page_id[-1]),
            sort_order=int(page_id[-1]),
            source_hash=hashlib.sha256(payload).hexdigest(),
            source_size_bytes=len(payload),
            width=4,
            height=3,
            managed_original_ref=relative,
        )
        repository.add_page(page)
        return page

    manifest_path = tmp_path / "managed" / "trash-manifest.json"
    service = TrashService(
        repository, storage, _JsonTrashManifest(manifest_path)
    )
    yield {
        "conn": conn,
        "repository": repository,
        "storage": storage,
        "service": service,
        "make_page": make_page,
        "user_source": user_source,
        "manifest_path": manifest_path,
        "tmp_path": tmp_path,
    }
    conn.close()


import hashlib  # noqa: E402


def _pages(repository, chapter_id="chapter-1"):
    return {page.page_id: page for page in repository.list_pages(chapter_id)}


def test_soft_delete_hides_and_batch_restore_brings_back(workspace) -> None:
    repository, service = workspace["repository"], workspace["service"]
    workspace["make_page"]("p1", b"one")
    workspace["make_page"]("p2", b"two")

    batch = service.soft_delete_pages("chapter-1", ("p1", "p2"))
    assert batch.chapter_id == "chapter-1"
    assert batch.page_ids == ("p1", "p2")
    # reader/import views hide soft-deleted pages (list_pages filters)
    assert list(_pages(repository)) == []

    restored = service.restore_batch(batch.batch_id)
    assert restored == 2
    pages = _pages(repository)
    assert set(pages) == {"p1", "p2"}
    # restore loses nothing: content, order metadata and managed refs intact
    assert pages["p1"].managed_original_ref.endswith("p1.png")
    assert [pages["p1"].source_order, pages["p2"].source_order] == [1, 2]
    # the manifest drops the consumed batch
    assert service.list_batches() == []


def test_purge_removes_controlled_data_only(workspace) -> None:
    repository, service, storage = (
        workspace["repository"],
        workspace["service"],
        workspace["storage"],
    )
    user_source: Path = workspace["user_source"]
    page = workspace["make_page"]("p9", b"controlled bytes")
    managed_file = Path(storage.absolute_path(page.managed_original_ref))
    assert managed_file.is_file()

    batch = service.soft_delete_pages("chapter-1", ("p9",))
    service.purge_batch(batch.batch_id)

    # controlled data gone: row + managed file
    assert repository.get_page("p9") is None
    assert _pages(repository) == {}
    assert not managed_file.exists()
    # user source file outside the managed root survives verbatim
    assert user_source.read_bytes() == b"USER SOURCE BYTES"
    assert service.list_batches() == []


def test_unknown_batch_fails_typed(workspace) -> None:
    with pytest.raises(KeyError, match="unknown trash batch"):
        workspace["service"].restore_batch("no-such-batch")
    with pytest.raises(KeyError, match="unknown trash batch"):
        workspace["service"].purge_batch("no-such-batch")


def test_remove_managed_refuses_paths_escaping_the_root(workspace) -> None:
    storage: ManagedFileStorage = workspace["storage"]
    outside = workspace["tmp_path"] / "outside.txt"
    outside.write_bytes(b"precious")
    with pytest.raises(ImmutablePathViolation, match="escapes the managed root"):
        storage.remove_managed("../outside.txt")
    assert outside.read_bytes() == b"precious"


def test_batches_are_independent(workspace) -> None:
    service, repository = workspace["service"], workspace["repository"]
    workspace["make_page"]("p1", b"one")
    workspace["make_page"]("p2", b"two")

    batch_a = service.soft_delete_pages("chapter-1", ("p1",))
    batch_b = service.soft_delete_pages("chapter-1", ("p2",))
    assert batch_a.batch_id != batch_b.batch_id
    assert len(service.list_batches()) == 2

    service.restore_batch(batch_a.batch_id)
    assert set(_pages(repository)) == {"p1"}  # p2 stays trashed
    service.purge_batch(batch_b.batch_id)
    assert set(_pages(repository)) == {"p1"}  # p2 rows gone, p1 untouched
    assert list(workspace["service"].list_batches()) == []


def test_overlapping_soft_delete_does_not_cross_batches(workspace) -> None:
    """TASK-021 R-001 (Review a9b4141, P2): a page that is already in an
    earlier batch must never be recorded into (or restored/purged by) a
    later batch — batches stay disjoint even when callers overlap id lists."""
    service, repository = workspace["service"], workspace["repository"]
    workspace["make_page"]("p1", b"one")
    workspace["make_page"]("p2", b"two")
    workspace["make_page"]("p3", b"three")

    batch_a = service.soft_delete_pages("chapter-1", ("p1", "p2"))
    assert batch_a.page_ids == ("p1", "p2")

    # p2 is still in batch A: the overlapping call may only take p3
    batch_c = service.soft_delete_pages("chapter-1", ("p2", "p3"))
    assert batch_c.page_ids == ("p3",)

    # restoring batch C must not resurrect p2 (it belongs to batch A)
    service.restore_batch(batch_c.batch_id)
    # all three rows still exist (get_pages_by_ids sees soft-deleted ones);
    # only p3 is live, p1/p2 remain trashed in batch A
    rows = {page.page_id: page for page in repository.get_pages_by_ids(("p1", "p2", "p3"))}
    assert set(rows) == {"p1", "p2", "p3"}
    assert rows["p3"].deleted_at is None  # p3 restored
    assert rows["p1"].deleted_at and rows["p2"].deleted_at  # p1/p2 still trashed

    # purging batch A removes exactly its own pages (p2 is soft-deleted by A,
    # so purging A is safe); the live p3 is untouched
    service.purge_batch(batch_a.batch_id)
    pages = _pages(repository)
    assert set(pages) == {"p3"}
    managed_left = list((workspace["tmp_path"] / "managed").rglob("original/*.png"))
    assert all("p3" in path.name for path in managed_left)
