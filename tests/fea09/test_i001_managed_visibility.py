"""C-05 v1.2 / C-15 v1.1 (R1-I001): managed witness matrix + projection."""

from __future__ import annotations

import sqlite3

import pytest

from domain.pages.entities import Page, PageView

NOW = "2026-11-01T00:00:00.000+00:00"
FUTURE = "2999-01-01T00:00:00.000+00:00"


def _page(
    conn: sqlite3.Connection,
    page_id: str,
    chapter_id: str,
    *,
    order: int,
    source_hash: str | None,
    ref: str | None,
    width: int | None,
    height: int | None,
    integrity: str = "incomplete",
    created_at: str = NOW,
    deleted_at: str | None = None,
    mode: str = "managed",
) -> None:
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref, deleted_at,"
        " source_mode, integrity_status)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, 10, ?, ?, ?, ?, ?, ?)",
        (page_id, chapter_id, order, created_at, created_at, f"{page_id}.png",
         order, source_hash, width, height, ref, deleted_at, mode, integrity),
    )
    conn.commit()


def _original_artifact(
    conn: sqlite3.Connection,
    page_id: str,
    book_id: str,
    chapter_id: str,
    *,
    artifact_id: str,
    revision_id: str,
    managed_path: str,
    file_hash: str,
    width: int | None,
    height: int | None,
    integrity: str = "valid",
    created_at: str = NOW,
    artifact_type: str = "original",
) -> None:
    conn.execute(
        "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
        " artifact_type, current_revision_id, created_at, updated_at)"
        " VALUES (?, ?, ?, ?, ?, NULL, ?, ?)",
        (artifact_id, book_id, chapter_id, page_id, artifact_type, created_at, created_at),
    )
    conn.execute(
        "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
        " revision_no, managed_path, file_hash, mime_type, width, height,"
        " size_bytes, integrity_status, created_at)"
        " VALUES (?, ?, 1, ?, ?, 'image/png', ?, ?, 10, ?, ?)",
        (revision_id, artifact_id, managed_path, file_hash, width, height,
         integrity, created_at),
    )
    conn.execute(
        "UPDATE media_artifacts SET current_revision_id = ? WHERE artifact_id = ?",
        (revision_id, artifact_id),
    )
    conn.commit()


def _chapter(conn: sqlite3.Connection, book: str, chapter: str, order: int = 0) -> None:
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?)", (book, book, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, sort_order,"
        " created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (chapter, book, chapter, order, NOW, NOW),
    )
    conn.commit()


def test_artifact_only_page_visible_as_read_only_projection(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_art", "c1", order=1, source_hash=None, ref=None,
          width=None, height=None)
    _original_artifact(
        conn, "p_art", "b1", "c1", artifact_id="a1", revision_id="r1",
        managed_path="managed/p_art.png", file_hash="a" * 64,
        width=None, height=None,
    )
    result = repo.get_page("p_art")
    assert isinstance(result, PageView)
    assert result.visibility_witness == "artifact"
    assert result.original_available is True
    assert result.source_hash == "a" * 64
    assert (result.width, result.height) == (None, None)
    assert [p.page_id for p in repo.list_pages("c1")] == ["p_art"]


def test_copy_only_page_visible_as_full_page(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_copy", "c1", order=1, source_hash="b" * 64,
          ref="managed/p_copy.png", width=10, height=10, integrity="complete")
    result = repo.get_page("p_copy")
    assert isinstance(result, Page)
    assert result.managed_original_ref == "managed/p_copy.png"


def test_both_witnesses_are_single_page(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_both", "c1", order=1, source_hash="c" * 64,
          ref="managed/p_both.png", width=10, height=10, integrity="complete")
    _original_artifact(
        conn, "p_both", "b1", "c1", artifact_id="a1", revision_id="r1",
        managed_path="managed/artifact.png", file_hash="c" * 64,
        width=10, height=10,
    )
    pages = repo.list_pages("c1")
    assert [p.page_id for p in pages] == ["p_both"]
    assert isinstance(pages[0], Page)
    assert repo.get_visible_original_path("p_both") == "managed/artifact.png"


def test_both_witnesses_failing_page_invisible(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_half", "c1", order=1, source_hash=None, ref=None,
          width=None, height=None)
    assert repo.get_page("p_half") is None
    assert repo.list_pages("c1") == []


def test_thumbnail_only_page_visible_but_not_original(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_thumb", "c1", order=1, source_hash=None, ref=None,
          width=None, height=None)
    _original_artifact(
        conn, "p_thumb", "b1", "c1", artifact_id="a1", revision_id="r1",
        managed_path="managed/thumb.png", file_hash="d" * 64,
        width=4, height=4, artifact_type="thumbnail",
    )
    result = repo.get_page("p_thumb")
    assert isinstance(result, PageView)
    assert result.visibility_witness == "artifact"
    assert result.original_available is False
    assert result.source_hash is None  # never a thumbnail hash
    assert result.width is None


def test_invalid_artifact_does_not_negate_copy_witness(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_ind", "c1", order=1, source_hash="e" * 64,
          ref="managed/p_ind.png", width=10, height=10, integrity="complete")
    _original_artifact(
        conn, "p_ind", "b1", "c1", artifact_id="a1", revision_id="r1",
        managed_path="managed/p_ind_art.png", file_hash="e" * 64,
        width=10, height=10, integrity="corrupted",
    )
    result = repo.get_page("p_ind")
    assert isinstance(result, Page)  # copy witness still holds


@pytest.mark.parametrize("created_at", [FUTURE])
def test_future_witnesses_invisible(conn, repo, created_at):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_future_copy", "c1", order=1, source_hash="f" * 64,
          ref="managed/p.png", width=10, height=10, integrity="complete",
          created_at=created_at)
    _page(conn, "p_future_art", "c1", order=2, source_hash=None, ref=None,
          width=None, height=None)
    _original_artifact(
        conn, "p_future_art", "b1", "c1", artifact_id="a1", revision_id="r1",
        managed_path="managed/future.png", file_hash="f" * 64,
        width=10, height=10, created_at=created_at,
    )
    assert repo.list_pages("c1") == []


def test_deleted_page_and_parent_hidden(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_del", "c1", order=1, source_hash="1" * 64,
          ref="managed/p.png", width=10, height=10, integrity="complete",
          deleted_at=NOW)
    _page(conn, "p_ok", "c1", order=2, source_hash="2" * 64,
          ref="managed/p2.png", width=10, height=10, integrity="complete")
    assert [p.page_id for p in repo.list_pages("c1")] == ["p_ok"]
    conn.execute("UPDATE chapters SET deleted_at = ? WHERE chapter_id = 'c1'",
                 (NOW,))
    conn.commit()
    assert repo.get_page("p_ok") is None


def test_get_visible_original_path_prefers_artifact_then_copy(conn, repo):
    _chapter(conn, "b1", "c1")
    _page(conn, "p_copy", "c1", order=1, source_hash="3" * 64,
          ref="managed/copy.png", width=10, height=10, integrity="complete")
    assert repo.get_visible_original_path("p_copy") == "managed/copy.png"
    _original_artifact(
        conn, "p_copy", "b1", "c1", artifact_id="a1", revision_id="r1",
        managed_path="managed/artifact.png", file_hash="3" * 64,
        width=10, height=10,
    )
    assert repo.get_visible_original_path("p_copy") == "managed/artifact.png"
    assert repo.get_visible_original_path("missing") is None
