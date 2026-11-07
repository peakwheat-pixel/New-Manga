"""FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A): import reuse-path refresh.

C-15 §2/§3.3: re-registering the SAME physical source updates the recorded
``source_locations`` auth baseline (``registry_id``/``authorization_generation``
/``last_verified_at``) **in place** — no duplicate location row and no rewrite
of the identity columns.  DSH D-2 also allows the zero-page skip paths
(whole-source skip / every page already referenced) to perform exactly ONE
conditional refresh when a live grant covers the recorded identity.

Discriminators: removing the import refresh call (page unit or D-2 skip)
leaves the old ``reg-1`` registry in place and these assertions turn red; a
revoked grant must never refresh (fail-closed, no auto re-authorization).
"""

from __future__ import annotations

import time
from datetime import datetime

import pytest

from support import FakeSourceReadAccess, build_runtime, png_bytes, write_zip

NOW = "2026-11-03T00:00:00.000+00:00"
OP = "op-0000000000000001"
OP2 = "op-0000000000000002"


def _wait_terminal(runtime, operation_id, timeout=20.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        receipt = runtime.receipt(operation_id)
        if receipt["state"] in {"completed", "cancelled", "failed"}:
            return receipt
        time.sleep(0.01)
    return runtime.receipt(operation_id)


def _plan_and_start(runtime, grant_ids, *, chapter="c1", policy="skip",
                    operation=OP):
    plan = runtime._planner.plan(
        chapter_id=chapter, grants=grant_ids, duplicate_policy=policy
    )
    runtime.start(
        chapter_id=chapter,
        plan_id=plan["plan_id"],
        plan_digest=plan["plan_digest"],
        grants=grant_ids,
        duplicate_policy=policy,
        operation_id=operation,
    )
    return plan


def _two_page_zip(tmp_path, name="book.zip"):
    return write_zip(
        tmp_path / name,
        [("001.png", png_bytes(color=(255, 0, 0))),
         ("002.png", png_bytes(color=(0, 255, 0)))],
    )


def _current_location(conn):
    return conn.execute(
        "SELECT * FROM source_locations WHERE is_current = 1 ORDER BY source_id"
    ).fetchall()


def _location(conn, source_id):
    row = conn.execute(
        "SELECT * FROM source_locations WHERE source_id = ? AND is_current = 1",
        (source_id,),
    ).fetchone()
    assert row is not None
    return row


def _iso(value: str):
    text = value.replace("Z", "+00:00") if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    assert parsed.tzinfo is not None
    return parsed


def _first_import(tmp_path, conn, repo):
    """Import one real zip into book b1 / chapter c1; return its source id."""
    path = _two_page_zip(tmp_path)
    access = FakeSourceReadAccess()
    access.add_file("g-first-00000000001", "zip", path)
    runtime = build_runtime(repo, access)
    _plan_and_start(runtime, ["g-first-00000000001"])
    receipt = _wait_terminal(runtime, OP)
    assert receipt["state"] == "completed"
    assert receipt["totals"]["imported_pages"] == 2
    source = conn.execute("SELECT source_id FROM sources").fetchone()
    return path, access, runtime, source["source_id"]


def _second_project(conn):
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('b2', 'Book 2', ?, ?)",
            (NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('c2', 'b2', 'Ch 2', ?, ?)",
            (NOW, NOW),
        )


def test_reimport_into_another_project_refreshes_location_auth_in_place(
    tmp_path, conn, repo, book_chapter
):
    """AC-LS4-2 (import page unit): the same physical source imported into a
    second project with a NEW registry refreshes the existing location row."""
    path, access, runtime, source_id = _first_import(tmp_path, conn, repo)
    before = _location(conn, source_id)
    assert before["registry_id"] == "reg-1"
    assert before["authorization_generation"] == 1
    assert before["last_verified_at"] is None

    _second_project(conn)
    access.add_file(
        "g-second-00000000002", "zip", path, registry_id="reg-2", generation=1
    )
    plan = _plan_and_start(
        runtime, ["g-second-00000000002"], chapter="c2", operation=OP2
    )
    assert plan["totals"]["skip"] == 0  # a second project imports the pages
    second = _wait_terminal(runtime, OP2)
    assert second["state"] == "completed"
    assert second["totals"]["imported_pages"] == 2

    after = _location(conn, source_id)
    assert after["location_id"] == before["location_id"]  # in place, same row
    assert after["registry_id"] == "reg-2"
    assert after["authorization_generation"] == 1
    assert after["last_verified_at"] is not None
    _iso(after["last_verified_at"])
    for column in (
        "source_id", "content_digest", "volume_serial", "file_id",
        "size_bytes", "is_current", "created_at",
    ):
        assert after[column] == before[column], column
    assert len(_current_location(conn)) == 1  # never a duplicate location row
    assert conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0] == 1
    assert len(repo.list_pages("c2")) == 2


def test_whole_source_skip_refreshes_location_auth_once(
    tmp_path, conn, repo, book_chapter
):
    """AC-LS4-3 / DSH D-2: a whole-source skip writes exactly one conditional
    refresh (and nothing else)."""
    path, access, runtime, source_id = _first_import(tmp_path, conn, repo)
    before = _location(conn, source_id)
    pages_before = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]

    access.add_file(
        "g-second-00000000002", "zip", path, registry_id="reg-2", generation=1
    )
    _plan_and_start(runtime, ["g-second-00000000002"], operation=OP2)
    second = _wait_terminal(runtime, OP2)
    assert second["state"] == "completed"
    item = second["items"][0]
    assert item["outcome"] == "skipped"
    assert item["counts"] == {
        "imported_pages": 0, "skipped_pages": 0, "skipped_sources": 1,
        "failed_sources": 0, "unsupported_entries": 0, "pending_pages": 0,
    }

    after = _location(conn, source_id)
    assert after["location_id"] == before["location_id"]
    assert after["registry_id"] == "reg-2"  # the live grant's registry
    assert after["last_verified_at"] is not None
    _iso(after["last_verified_at"])
    # Skip stays a skip: no page, version, entry or binding was created.
    assert conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0] == pages_before
    assert conn.execute("SELECT COUNT(*) FROM source_versions").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM source_locations").fetchone()[0] == 1


def test_revoked_grant_never_refreshes_on_a_skip_path(
    tmp_path, conn, repo, book_chapter
):
    """AC-LS4-4: revoking the grant before start refreshes nothing — the skip
    stays fail-closed and never auto re-authorizes the source."""
    path, access, runtime, source_id = _first_import(tmp_path, conn, repo)
    before = _location(conn, source_id)

    access.add_file(
        "g-second-00000000002", "zip", path, registry_id="reg-2", generation=1
    )
    # The plan is built while the grant is still live (the planner resolves
    # it), then the grant is revoked BEFORE start: the worker's live resolve
    # fails and no refresh may happen.
    plan = runtime._planner.plan(
        chapter_id="c1", grants=["g-second-00000000002"], duplicate_policy="skip"
    )
    access.revoke("g-second-00000000002")
    runtime.start(
        chapter_id="c1",
        plan_id=plan["plan_id"],
        plan_digest=plan["plan_digest"],
        grants=["g-second-00000000002"],
        duplicate_policy="skip",
        operation_id=OP2,
    )
    receipt = _wait_terminal(runtime, OP2)
    assert receipt["state"] == "completed"
    assert receipt["items"][0]["outcome"] == "skipped"

    after = _location(conn, source_id)
    assert tuple(after) == tuple(before)  # zero write: no refresh, no auto re-authorization
    assert after["registry_id"] == "reg-1"
    assert after["last_verified_at"] is None


def test_all_pages_already_referenced_import_as_new_still_refreshes(
    tmp_path, conn, repo, book_chapter
):
    """AC-LS4-3 / D-2: with a non-skip duplicate policy the zero-page outcome
    ("skipped") still performs the one conditional refresh."""
    path, access, runtime, source_id = _first_import(tmp_path, conn, repo)
    access.add_file(
        "g-second-00000000002", "zip", path, registry_id="reg-2", generation=1
    )
    _plan_and_start(
        runtime, ["g-second-00000000002"], policy="import_as_new", operation=OP2
    )
    receipt = _wait_terminal(runtime, OP2)
    assert receipt["state"] == "completed"
    item = receipt["items"][0]
    assert item["outcome"] == "skipped"
    assert item["counts"]["skipped_pages"] == 2
    assert item["counts"]["imported_pages"] == 0

    after = _location(conn, source_id)
    assert after["registry_id"] == "reg-2"
    assert after["last_verified_at"] is not None
    assert conn.execute("SELECT COUNT(*) FROM source_locations").fetchone()[0] == 1
    assert len(repo.list_pages("c1")) == 2
