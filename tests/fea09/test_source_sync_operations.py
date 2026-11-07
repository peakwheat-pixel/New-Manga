"""FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A): sync apply-path refresh.

C-15 §2 约束语义 / §3.3 源复用规则: when a live grant (resolved through the
real HMAC-signed registry) covers the SAME physical identity as the recorded
current location row, the C-17 apply transaction updates
``source_locations.registry_id/authorization_generation/last_verified_at`` in
place.  A changed container keeps the existing supersede+insert path; a
different physical identity (an identical copy) and a revoked grant must never
refresh — fail-closed, zero write, no automatic re-authorization.

The fixtures are local because the sync apply transaction needs an autocommit
connection (``BEGIN IMMEDIATE``); the shared FEA-09 fixture uses the default
isolation level.
"""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from datetime import datetime

import pytest

from tests.fea11.conftest import (
    add_referenced_page,
    add_source_tree,
    build_plan_body,
    file_facts,
    host_authorization,
    mint_grant,
    png_bytes,
    run_full_sync,
    write_zip,
)

NOW = "2026-11-04T00:00:00.000+00:00"


@pytest.fixture()
def sync_conn():
    connection = sqlite3.connect(
        ":memory:", check_same_thread=False, isolation_level=None
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    MigrationRunner(connection, default_migrations()).apply_pending()
    return connection


@pytest.fixture()
def sync_repo(sync_conn):
    from infrastructure.sqlite.library import SqliteLibraryRepository

    return SqliteLibraryRepository(sync_conn)


@pytest.fixture()
def sync_registry():
    from infrastructure.resource_channel.source_read_refs import (
        SourceReadGrantRegistry,
    )

    return SourceReadGrantRegistry()


@pytest.fixture()
def sync_stack(sync_conn, sync_repo, sync_registry):
    from application.sources.ports import build_source_sync_stack
    from infrastructure.sqlite.source_sync import SourceSyncStore

    return build_source_sync_stack(
        store=SourceSyncStore(sync_conn),
        access=sync_registry,
        repository=sync_repo,
    )


@pytest.fixture()
def sync_book(sync_conn):
    with sync_conn:
        sync_conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('b1', 'Book', ?, ?)",
            (NOW, NOW),
        )
        sync_conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES ('c1', 'b1', 'Ch', ?, ?)",
            (NOW, NOW),
        )
    return "b1", "c1"


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _seed_two_page_source(conn, tmp_path):
    """s1 (reg-1/gen1) + sv1 + two referenced pages on the real zip bytes."""
    page1, page2 = png_bytes(color=(255, 0, 0)), png_bytes(color=(0, 255, 0))
    zip_path = write_zip(
        tmp_path / "old.zip", [("001.png", page1), ("002.png", page2)]
    )
    digest = _digest(zip_path.read_bytes())
    facts = file_facts(zip_path)
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=digest,
        entries=[("e1", "001.png", _digest(page1)),
                 ("e2", "002.png", _digest(page2))],
        volume_serial=facts["volume_serial"],
        file_id=facts["file_id"],
    )
    add_referenced_page(
        conn, "p1", "c1", "b1", order=1, source_id="s1", version_id="sv1",
        entry_id="e1", digest=_digest(page1),
    )
    add_referenced_page(
        conn, "p2", "c1", "b1", order=2, source_id="s1", version_id="sv1",
        entry_id="e2", digest=_digest(page2),
    )
    return zip_path, page1, page2, digest


def _scan(stack, registry, zip_path, *, kind="resync", registry_id="reg-1",
          generation=1):
    grant_id, _facts = mint_grant(
        registry,
        source_id="s1",
        kind="zip",
        entries=[(zip_path, zip_path.name, 0)],
        registry_id=registry_id,
        generation=generation,
    )
    scan = stack["scanner"].scan(
        {
            "source_id": "s1", "project_ids": ["b1"], "scope": "current",
            "kind": kind, "grant_ids": [grant_id], "missing": [],
        }
    )
    return grant_id, scan


def _location(conn):
    return conn.execute(
        "SELECT * FROM source_locations WHERE source_id = 's1' AND is_current = 1"
    ).fetchone()


def _locations(conn):
    return conn.execute(
        "SELECT * FROM source_locations WHERE source_id = 's1'"
    ).fetchall()


def _iso(value: str):
    text = value.replace("Z", "+00:00") if value.endswith("Z") else value
    parsed = datetime.fromisoformat(text)
    assert parsed.tzinfo is not None
    return parsed


def test_resync_same_identity_refreshes_the_location_auth(
    sync_conn, sync_registry, sync_stack, sync_book, tmp_path
):
    """AC-LS4-3: a same-container resync under a NEW registry refreshes the
    recorded location auth in place (relink is not the only path)."""
    zip_path, _p1, _p2, _digest_before = _seed_two_page_source(
        sync_conn, tmp_path
    )
    before = _location(sync_conn)
    assert before["registry_id"] == "reg-1"
    assert before["last_verified_at"] is None
    grant_id, scan = _scan(
        sync_stack, sync_registry, zip_path, kind="resync",
        registry_id="reg-2",
    )
    _plan, dispatch = run_full_sync(
        sync_stack, scan, grant_ids=[grant_id], kind="resync",
        command="ResyncSource",
    )
    assert dispatch["state"] == "core-committed"

    after = _location(sync_conn)
    assert after["location_id"] == before["location_id"]
    assert after["registry_id"] == "reg-2"
    assert after["authorization_generation"] == 1
    assert after["last_verified_at"] is not None
    _iso(after["last_verified_at"])
    for column in (
        "source_id", "content_digest", "volume_serial", "file_id",
        "size_bytes", "observed_at", "is_current", "created_at",
    ):
        assert after[column] == before[column], column
    assert len(_locations(sync_conn)) == 1
    # A same-container resync keeps every page/binding generation.
    bindings = sync_conn.execute(
        "SELECT page_id, binding_version, authorization_generation"
        " FROM page_bindings ORDER BY page_id"
    ).fetchall()
    assert [tuple(row) for row in bindings] == [
        ("p1", 1, 1), ("p2", 1, 1),
    ]


def test_identical_copy_never_refreshes_the_recorded_location(
    sync_conn, sync_registry, sync_stack, sync_book, tmp_path
):
    """AC-LS4-4②: same bytes in a DIFFERENT physical file (a copy) is a
    different identity — the refresh must be a zero write (no auth transfer)."""
    zip_path, _p1, _p2, _digest_before = _seed_two_page_source(
        sync_conn, tmp_path
    )
    before = _location(sync_conn)
    copied = tmp_path / "copied.zip"
    copied.write_bytes(zip_path.read_bytes())  # same digest, new volume/file
    grant_id, scan = _scan(
        sync_stack, sync_registry, copied, kind="repoint", registry_id="reg-2"
    )
    _plan, dispatch = run_full_sync(
        sync_stack, scan, grant_ids=[grant_id], kind="repoint",
        command="RepointSource",
    )
    assert dispatch["state"] == "core-committed"
    after = _location(sync_conn)
    assert tuple(after) == tuple(before)  # identity mismatch → zero write
    assert after["registry_id"] == "reg-1"
    assert after["last_verified_at"] is None
    assert len(_locations(sync_conn)) == 1


def test_revoked_grant_never_refreshes_and_never_publishes(
    sync_conn, sync_registry, sync_stack, sync_book, tmp_path
):
    """AC-LS4-4/5: a grant revoked between plan and apply is refused typed and
    the location auth baseline stays byte-identical (no auto re-authorization)."""
    from application.importing.referenced.errors import SourceImportError
    from application.sources.errors import SourceSyncError

    zip_path, _p1, _p2, _digest_before = _seed_two_page_source(
        sync_conn, tmp_path
    )
    grant_id, scan = _scan(
        sync_stack, sync_registry, zip_path, kind="resync",
        registry_id="reg-2",
    )
    body = build_plan_body(scan, kind="resync")
    plan = sync_stack["planner"].create(body)
    sync_stack["planner"].preview(
        {"plan_id": body["plan_id"], "plan_digest": plan["plan_digest"]}
    )
    sync_stack["planner"].confirm(
        {
            "plan_id": body["plan_id"],
            "plan_digest": plan["plan_digest"],
            "confirmation": body["confirmation"],
        }
    )
    from application.sources.model import request_digest_of

    operation_id = "op-" + uuid.uuid4().hex[:16]
    request_digest = request_digest_of(
        operation_id, body["plan_id"], plan["plan_digest"], "resync"
    )
    payload = {
        "operation_id": operation_id,
        "plan_id": body["plan_id"],
        "plan_digest": plan["plan_digest"],
        "grant_ids": [grant_id],
        "authorization": host_authorization(
            operation_id=operation_id,
            request_digest=request_digest,
            authorizations=scan["authorizations"],
        ),
    }
    sync_registry.revoke_grant_ids([grant_id])

    snapshot_before = [tuple(row) for row in _locations(sync_conn)]
    bindings_before = [
        tuple(row) for row in sync_conn.execute(
            "SELECT * FROM page_bindings ORDER BY binding_id"
        ).fetchall()
    ]
    with pytest.raises((SourceSyncError, SourceImportError)) as error:
        sync_stack["service"].apply("ResyncSource", payload)
    assert error.value.code in ("SOURCE_GRANT_REVOKED", "SOURCE_ACCESS_DENIED")
    # Zero writes: no refresh, no location/binding/operation row.
    assert [tuple(row) for row in _locations(sync_conn)] == snapshot_before
    assert [
        tuple(row) for row in sync_conn.execute(
            "SELECT * FROM page_bindings ORDER BY binding_id"
        ).fetchall()
    ] == bindings_before
    after = _location(sync_conn)
    assert after["registry_id"] == "reg-1"
    assert after["last_verified_at"] is None
    assert sync_conn.execute(
        "SELECT COUNT(*) FROM source_locations"
    ).fetchone()[0] == 1
