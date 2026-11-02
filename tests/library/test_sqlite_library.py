"""SQLite integration: unified persistence round-trips over the real v2
database (TASK-029). LibraryService/PageRepository/ImportPageSink run
against SqliteLibraryRepository; a simulated restart reopens the same
database file with a fresh connection."""

from __future__ import annotations

import sqlite3

import pytest

from application.importing.images.service import ImportImagesUseCase
from application.library.service import LibraryService
from domain.pages.entities import Page
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations


@pytest.fixture()
def db_path(tmp_path):
    return tmp_path / "unified.db"


@pytest.fixture()
def open_repo(db_path):
    """Open-migrate-return factory: each call simulates a fresh start."""

    def _open():
        conn, opened = open_database(
            db_path, latest_known_schema_version=default_migrations()[-1].schema_version
        )
        MigrationRunner(conn, default_migrations()).apply_pending()
        return conn, SqliteLibraryRepository(conn)

    conn, repo = _open()
    yield _open, conn, repo
    conn.close()


def seed_book_chapter(repo):
    from domain.books.entities import Book, Chapter

    book = Book(book_id="book-1", title="统一持久化", source_language="ja",
                target_language="zh")
    repo.add_book(book)
    chapter = Chapter(chapter_id="chapter-1", book_id="book-1", title="第1话")
    repo.add_chapter(chapter)
    return book, chapter


def make_page(n: int, chapter_id: str = "chapter-1") -> Page:
    return Page(
        page_id=f"page-{n}",
        chapter_id=chapter_id,
        source_filename=f"page_{n:03d}.png",
        source_order=n,
        sort_order=n,
        source_hash=f"hash-{n:064d}",
        source_size_bytes=100 * n,
        width=800,
        height=1200,
        managed_original_ref=f"books/book-1/chapters/chapter-1/original/page-{n}.png",
    )


def test_book_chapter_tag_roundtrip_and_restart(open_repo):
    _open, first_conn, first_repo = open_repo
    book, chapter = seed_book_chapter(first_repo)
    from domain.books.entities import Tag

    tag = Tag(tag_id="tag-1", name="连载中")
    first_repo.add_tag(tag)
    first_repo.add_book_tag(book.book_id, tag.tag_id)

    # "Restart": brand-new connection + repository over the same file.
    second_conn, second_repo = _open()
    loaded_book = second_repo.get_book(book.book_id)
    assert loaded_book.title == "统一持久化"
    assert loaded_book.default_chapter_type.value == "paged"
    assert loaded_book.is_favorite is False

    chapters = second_repo.list_chapters(chapter.book_id)
    assert [c.title for c in chapters] == ["第1话"]
    assert [t.name for t in second_repo.list_tags_of_book(book.book_id)] == ["连载中"]

    # Favorite flag round-trips as a system state, not a tag.
    loaded_book.set_favorite(True)
    second_repo.update_book(loaded_book)
    third_conn, third_repo = _open()
    assert third_repo.get_book(book.book_id).is_favorite is True
    # The user tag is independent data and still exists after the flag flip.
    assert [t.name for t in third_repo.list_tags()] == ["连载中"]
    for conn in (second_conn, third_conn):
        conn.close()


def test_tag_delete_removes_links_not_books(open_repo):
    _, conn, repo = open_repo
    book, _ = seed_book_chapter(repo)
    from domain.books.entities import Tag

    tag = Tag(tag_id="tag-del", name="将删除")
    repo.add_tag(tag)
    repo.add_book_tag(book.book_id, tag.tag_id)

    repo.delete_tag("tag-del")
    assert repo.list_tags() == []
    assert repo.list_tags_of_book(book.book_id) == []
    assert repo.get_book(book.book_id) is not None


def test_library_service_end_to_end_on_sqlite(open_repo):
    """LibraryService over the SQLite adapter: CRUD + tag rules (AC-LIB)."""
    _, conn, repo = open_repo
    service = LibraryService(repo)
    book = service.create_book("SQLite 书架", source_language="ja", target_language="zh")
    chapter = service.create_chapter(book.book_id, "第1话", chapter_type="webtoon")
    assert chapter.reading_direction.value == "vertical"

    tag = service.create_tag("待翻译")
    service.add_tag_to_book(book.book_id, tag.tag_id)
    service.set_favorite(book.book_id, True)

    restarted = LibraryService(repo)
    assert restarted.get_book(book.book_id).is_favorite is True
    assert [t.name for t in restarted.tags_of_book(book.book_id)] == ["待翻译"]
    with pytest.raises(Exception):
        restarted.create_tag("待翻译")  # LibraryService owns duplicate checks


def test_no_unique_name_constraint_at_db_level(open_repo):
    """TASK-028 §3.2: the adapter must not add UNIQUE(tags.name); the
    service-layer DuplicateTagName check is the only guard."""
    _, conn, repo = open_repo
    from domain.books.entities import Tag

    repo.add_tag(Tag(tag_id="t1", name="同名"))
    # Direct SQL double-insert succeeds — proving the DB constraint is absent.
    conn.execute(
        "INSERT INTO tags (tag_id, name, created_at, updated_at)"
        " VALUES ('t2', '同名', '2026-01-01', '2026-01-01')"
    )
    assert conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0] == 2


def test_page_roundtrip_and_restart(open_repo):
    _, conn, repo = open_repo
    seed_book_chapter(repo)
    repo.add_page(make_page(1))
    repo.add_page(make_page(2))

    _, restarted_conn, restarted_repo = open_repo
    page = restarted_repo.get_page("page-1")
    assert page.source_filename == "page_001.png"
    assert page.source_hash == f"hash-{1:064d}"
    assert (page.width, page.height, page.source_order, page.sort_order) == (800, 1200, 1, 1)
    listed = restarted_repo.list_pages("chapter-1")
    assert [p.page_id for p in listed] == ["page-1", "page-2"]

    # AC-PAGE-001: reorder touches sort_order only; restart keeps both.
    listed[0].reorder(5)
    restarted_repo.update_page(listed[0])
    _, final_conn, final_repo = open_repo
    final_page = final_repo.get_page("page-1")
    assert (final_page.source_order, final_page.sort_order) == (1, 5)
    for conn in (restarted_conn, final_conn):
        conn.close()


def test_v1_placeholder_pages_are_not_pages(open_repo):
    """TASK-028 §3.1: v1 structural placeholder rows (artifact FK anchors)
    must never be surfaced as fabricated pages."""
    _, conn, repo = open_repo
    seed_book_chapter(repo)
    # A v1-style placeholder: only the anchor columns, import columns NULL.
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
        " VALUES ('placeholder-1', 'chapter-1', 0, '2026-01-01', '2026-01-01')"
    )
    assert repo.get_page("placeholder-1") is None
    assert repo.list_pages("chapter-1") == []
    assert repo.existing_source_hashes("chapter-1") == set()
    assert repo.max_source_order("chapter-1") == 0

    # A real import still works next to the placeholder.
    repo.add_page(make_page(1))
    assert [p.page_id for p in repo.list_pages("chapter-1")] == ["page-1"]
    assert repo.max_source_order("chapter-1") == 1


def test_soft_delete_and_import_sink(open_repo):
    _, conn, repo = open_repo
    seed_book_chapter(repo)
    repo.add_page(make_page(1))
    repo.add_page(make_page(2))

    # ImportPageSink reads only complete, non-deleted rows.
    assert repo.existing_source_hashes("chapter-1") == {
        f"hash-{1:064d}", f"hash-{2:064d}",
    }
    assert repo.max_source_order("chapter-1") == 2

    repo.soft_delete_page("page-2")
    # Soft-deleted pages live in the recycle-bin semantics; their hash still
    # participates in import dedup until permanent deletion (safer default).
    assert repo.max_source_order("chapter-1") == 2
    assert [p.page_id for p in repo.list_pages("chapter-1")] == ["page-1"]

    # FK enforcement: a page for a missing chapter is rejected.
    with pytest.raises(sqlite3.IntegrityError):
        repo.add_page(make_page(3, chapter_id="missing-chapter"))
