"""FEA-09 Phase A — the five read paths under C-15 §4.2 / C-05 v1.1.

Covers: existing_source_hashes / max_source_order (is_complete_page, with
and without soft-deleted rows), get_page / list_pages (V(p,t) with parent
deletion), referenced visibility (healthy binding required; broken
binding / incomplete rows invisible), and the SOURCE_PROJECT_MISMATCH
book-ownership guard.
"""

from __future__ import annotations

import sqlite3

import pytest

from infrastructure.sqlite.library import SourceProjectMismatch, SqliteLibraryRepository

from tests.fea09.conftest import (
    NOW,
    add_managed_page,
    add_referenced_page,
    add_source_tree,
)


def test_existing_source_hashes_and_max_source_order_dual_mode(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    _, chapter = book_chapter
    add_source_tree(conn, entries=(("e1", "001.png", 0), ("e2", "002.png", 1)),
                     digest="3" * 64)
    d_ok = add_managed_page(conn, "p_m1", chapter, order=1, digest="1" * 64)
    add_managed_page(conn, "p_mdel", chapter, order=2, digest="2" * 64, soft_deleted=True)
    add_referenced_page(conn, "p_r1", chapter, "b1", order=3, source_id="s1",
                        version_id="sv1", entry_id="e1", digest="3" * 64)
    # referenced page whose binding is broken must not be complete/visible
    add_referenced_page(conn, "p_rbad", chapter, "b1", order=4, source_id="s1",
                        version_id="sv1", entry_id="e2", digest="4" * 64,
                        binding_status="needs_confirmation")

    hashes = repo.existing_source_hashes(chapter)
    # soft-deleted managed page excluded; broken-binding referenced page excluded
    assert hashes == {d_ok, "3" * 64}

    # max_source_order includes soft-deleted pages (order slot reservation)
    # but NOT the broken-binding referenced page (not is_complete_page).
    assert repo.max_source_order(chapter) == 3


def test_referenced_incomplete_row_invisible(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    _, chapter = book_chapter
    add_source_tree(conn)
    add_referenced_page(conn, "p_inc", chapter, "b1", order=1, source_id="s1",
                        version_id="sv1", entry_id="e1", digest="5" * 64,
                        integrity="incomplete")
    assert repo.get_page("p_inc") is None
    assert repo.list_pages(chapter) == []
    assert repo.existing_source_hashes(chapter) == set()
    assert repo.max_source_order(chapter) == 0
    # the row itself survives (recoverable, not deleted)
    assert conn.execute(
        "SELECT COUNT(*) FROM pages WHERE page_id='p_inc'").fetchone()[0] == 1


def test_broken_binding_makes_referenced_page_invisible(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    _, chapter = book_chapter
    add_source_tree(conn, digest="6" * 64)
    add_referenced_page(conn, "p_r", chapter, "b1", order=1, source_id="s1",
                        version_id="sv1", entry_id="e1", digest="6" * 64)
    assert repo.get_page("p_r") is not None
    conn.execute(
        "UPDATE page_bindings SET status='missing' WHERE page_id='p_r'")
    conn.commit()
    assert repo.get_page("p_r") is None
    assert repo.list_pages(chapter) == []


def test_verified_digest_mismatch_breaks_visibility(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    """P8 requires binding.verified_digest == entry.content_digest."""
    _, chapter = book_chapter
    add_source_tree(conn, digest="7" * 64)
    add_referenced_page(conn, "p_r", chapter, "b1", order=1, source_id="s1",
                        version_id="sv1", entry_id="e1", digest="7" * 64)
    conn.execute(
        "UPDATE page_bindings SET verified_digest = ? WHERE page_id='p_r'",
        ("f" * 64,))
    conn.commit()
    assert repo.get_page("p_r") is None


def test_parent_deletion_hides_pages_in_get_and_list(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    _, chapter = book_chapter
    add_managed_page(conn, "p_m1", chapter, order=1, digest="8" * 64)
    # chapter soft-deleted → page invisible via V(p,t) P1
    conn.execute("UPDATE chapters SET deleted_at = ? WHERE chapter_id = ?", (NOW, chapter))
    conn.commit()
    assert repo.get_page("p_m1") is None
    assert repo.list_pages(chapter) == []
    # restore
    conn.execute("UPDATE chapters SET deleted_at = NULL WHERE chapter_id = ?", (chapter,))
    conn.commit()
    assert repo.get_page("p_m1") is not None


def test_list_pages_orders_and_mixes_modes(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    _, chapter = book_chapter
    add_source_tree(conn, entries=(("e1", "001.png", 0), ("e2", "002.png", 1)),
                     digest="b" * 64)
    add_managed_page(conn, "p_m1", chapter, order=1, digest="a" * 64)
    add_referenced_page(conn, "p_r1", chapter, "b1", order=2, source_id="s1",
                        version_id="sv1", entry_id="e1", digest="b" * 64)
    add_managed_page(conn, "p_m2", chapter, order=3, digest="c" * 64)
    pages = repo.list_pages(chapter)
    assert [p.page_id for p in pages] == ["p_m1", "p_r1", "p_m2"]
    assert [p.source_mode for p in pages] == ["managed", "referenced", "managed"]
    ref_page = pages[1]
    assert ref_page.managed_original_ref is None
    assert ref_page.source_hash == "b" * 64


def test_binding_project_mismatch_rejected_same_transaction(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    """C-15 §2: page→chapter→book must equal binding.project_id inside the
    commit transaction; mismatch raises and rolls back."""
    _, chapter = book_chapter
    # a second book whose id is NOT the page's owning book
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b_other', 'Other', ?, ?)", (NOW, NOW))
    conn.commit()
    add_managed_page(conn, "p_x", chapter, order=1, digest="9" * 64)
    binding = {
        "binding_id": "bind_x", "page_id": "p_x", "project_id": "b_other",
        "binding_version": 1, "source_id": "s1", "entry_id": "e1",
        "accepted_source_version": "sv1", "status": "healthy",
        "previous_binding_id": None, "authorization_generation": 1,
        "authorized_at": NOW, "verified_digest": "9" * 64,
        "created_at": NOW, "updated_at": NOW,
    }
    with pytest.raises(SourceProjectMismatch):
        with conn:
            repo.insert_page_binding(binding)
    assert conn.execute(
        "SELECT COUNT(*) FROM page_bindings WHERE binding_id='bind_x'").fetchone()[0] == 0


def test_managed_artifact_only_legacy_rows_stay_visible_via_columns(
    conn: sqlite3.Connection, repo: SqliteLibraryRepository, book_chapter
) -> None:
    """R2S-001: legacy managed visibility is unchanged — pages complete by
    import columns stay visible; no artifact rows are required (the pre-v7
    behaviour is conserved byte-for-byte)."""
    _, chapter = book_chapter
    add_managed_page(conn, "p_legacy", chapter, order=1, digest="d" * 64)
    page = repo.get_page("p_legacy")
    assert page is not None
    assert page.source_mode == "managed"
    assert page.integrity_status == "complete"
