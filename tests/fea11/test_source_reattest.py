"""FEA-11-L-S4-B (C-16 v1.5 §2.5): ``ReattestSourceLocation`` condition-write.

The B1 explicit re-authorization only changes the Host Registry; the Core
``source_locations`` row keeps the old ``(registry_id, authorization_generation)``
pair, so the Host's exact-match scan enumeration typed-skips the source. These
tests run the REAL production assembly (migrations, live grant registry, the
single refresh SQL) over a real zip container and a real Host-minted grant:

* AC-LS4B-3: closed shape, host-only/session, grant live/unexpired/unrevoked,
  ``grant.scope.source_id`` and the four physical facts -> typed refusal with
  ZERO writes;
* AC-LS4B-4: success writes ONLY the two auth columns (``last_verified_at``
  keeps its original value, no ``now()``), no location row is added and every
  other column/table stays byte-identical; repeat -> ``updated: 0`` + zero
  write; same-registry regression is a no-op, cross-registry is allowed;
* AC-LS4B-5: the command never creates/revives a grant and never touches
  ``page_bindings``/the location identity; folder sources are refused;
* AC-LS4B-6: after the re-attest the cold-start enumeration returns the NEW
  ``(registry_id, generation)`` pair with the same identity/projects;
* AC-LS4B-10: no automatic recovery wording/model — the command is only the
  fact propagation of the user's explicit action.

Isolation: every scratch DB/zip lives under
``G:/CODEX/New Manga.workspace/FEA-11-L-S4-B-AUTO-RECOVERY-1/``.
"""

from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
import time
import uuid
from pathlib import Path

import pytest

from application.importing.referenced.errors import SOURCE_ERROR_TABLE
from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    file_facts,
    mint_grant,
    png_bytes,
    write_zip,
)

#: Task isolation root (never a real user data root).
WORKSPACE_ROOT = Path("G:/CODEX/New Manga.workspace/FEA-11-L-S4-B-AUTO-RECOVERY-1")
FIXTURE_ROOT = WORKSPACE_ROOT / "fixtures"

HOST_SESSION_ID = "host-session-l-s4b-reattest"
HOST_CREDENTIAL = base64.urlsafe_b64encode(bytes(range(32))).decode().rstrip("=")

#: The original audit value seeded on the location row; the re-attest must
#: write it back unchanged (the command never refreshes the audit time).
ORIGINAL_LAST_VERIFIED_AT = "2026-01-01T00:00:00.000+00:00"


@pytest.fixture()
def reattest_root(request) -> Path:
    root = FIXTURE_ROOT / f"{request.node.name[:40]}-{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


def _seed_library(db_path: Path) -> dict:
    """One real v8 library with ONE real zip source and one referenced page."""
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    MigrationRunner(conn, default_migrations()).apply_pending()
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b1', 'Book', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c1', 'b1', 'Ch', ?, ?)",
        (NOW, NOW),
    )
    first = png_bytes(4, 3, (255, 0, 0))
    second = png_bytes(4, 3, (0, 255, 0))
    archive = write_zip(db_path.parent / "source.zip", [("001.png", first), ("002.png", second)])
    facts = file_facts(archive)
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=facts["sha256"],
        entries=[
            ("se1", "001.png", hashlib.sha256(first).hexdigest()),
            ("se2", "002.png", hashlib.sha256(second).hexdigest()),
        ],
        volume_serial=facts["volume_serial"],
        file_id=facts["file_id"],
        registry_id="reg-old",
        generation=1,
    )
    # ``add_source_tree`` hand-seeds the container size and leaves the audit
    # column NULL; align the row with the REAL file identity and seed the audit
    # sentinel this command must preserve byte for byte.
    conn.execute(
        "UPDATE source_locations SET size_bytes = ?, last_verified_at = ?"
        " WHERE source_id = 's1'",
        (facts["size"], ORIGINAL_LAST_VERIFIED_AT),
    )
    add_referenced_page(
        conn,
        "p1",
        "c1",
        "b1",
        order=1,
        source_id="s1",
        version_id="sv1",
        entry_id="se1",
        digest=hashlib.sha256(first).hexdigest(),
    )
    conn.commit()
    conn.close()
    return {"archive": archive, "facts": facts}


def _assemble(db_path: Path, managed_root: Path):
    managed_root.mkdir(parents=True, exist_ok=True)
    # ``db_path`` already lives inside the data root (``<data>/library.db``).
    return assemble_production_core(db_path.parent)


@pytest.fixture()
def core_bundle(reattest_root: Path):
    db_path = reattest_root / "data" / "library.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    seeded = _seed_library(db_path)
    core = _assemble(db_path, reattest_root / "managed")
    core.pipeline.set_scheduler_owner(True)
    server = CoreServiceServer(core, stdin=None, stdout=None)
    try:
        yield core, server, seeded
    finally:
        server.close()
        core.conn.close()


# ---------------------------------------------------------------------------
# host-control helpers (real CoreServiceServer over the assembled Core)
# ---------------------------------------------------------------------------


def _wire(command: str, payload: dict) -> dict:
    return {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": uuid.uuid4().hex,
        "channel": "host-control",
        "command": command,
        "payload": payload,
    }


def _open(server: CoreServiceServer) -> str:
    response, _ = server.dispatch_request(
        json.dumps(
            _wire(
                "OpenHostSession",
                {
                    "host_session_id": HOST_SESSION_ID,
                    "host_session_credential": HOST_CREDENTIAL,
                },
            )
        )
    )
    assert response["error"] is None, response["error"]
    return response["result"]["core_session_id"]


def _request(
    server: CoreServiceServer, core_session_id: str, command: str, payload: object
) -> dict:
    request = _wire(command, payload)  # type: ignore[arg-type]
    request.update(
        {
            "core_session_id": core_session_id,
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": HOST_CREDENTIAL,
        }
    )
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def _app_request(server: CoreServiceServer, command: str, payload: object) -> dict:
    request = {
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": uuid.uuid4().hex,
        "command": command,
        "payload": payload,
    }
    response, should_exit = server.dispatch_request(json.dumps(request))
    assert not should_exit
    return response


def _reattest(
    server: CoreServiceServer,
    core_session_id: str,
    *,
    source_id: str = "s1",
    grant_id: str,
) -> dict:
    return _request(
        server,
        core_session_id,
        "ReattestSourceLocation",
        {"source_id": source_id, "grant_id": grant_id},
    )


def _mint(
    core,
    seeded: dict,
    *,
    source_id: str = "s1",
    version: str = "sv1",
    kind: str = "zip",
    registry_id: str = "reg-new",
    generation: int = 3,
    locator: str = "001.png",
    ordinal: int = 0,
    entries=None,
) -> str:
    grant_id, _facts = mint_grant(
        core.source_read_refs,
        source_id=source_id,
        version=version,
        kind=kind,
        entries=entries
        if entries is not None
        else [(seeded["archive"], locator, ordinal)],
        session_id=HOST_SESSION_ID,
        registry_id=registry_id,
        generation=generation,
    )
    return grant_id


def _table_snapshot(core) -> dict[str, str]:
    names = [
        row[0]
        for row in core.conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    snapshot: dict[str, str] = {}
    for name in names:
        rows = core.conn.execute(f'SELECT * FROM "{name}"').fetchall()
        payload = repr(sorted(repr(tuple(row)) for row in rows))
        snapshot[name] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return snapshot


def _location_row(core, source_id: str = "s1") -> dict:
    row = core.conn.execute(
        "SELECT * FROM source_locations WHERE source_id = ? AND is_current = 1",
        (source_id,),
    ).fetchone()
    assert row is not None
    return dict(row)


#: Envelope-level codes (host-control guards/shape) are NOT part of the C-16 §6
#: source closed set: the frozen v1.5 rules reuse the existing host-only/session
#: guards + ``INVALID_REQUEST`` (no new code is introduced by this command).
_ENVELOPE_ERRORS = {
    "INVALID_REQUEST": "validation",
    "HOST_ONLY_REQUIRED": "validation",
    "HOST_SESSION_INVALID": "conflict",
    "CORE_SESSION_MISMATCH": "conflict",
}


def _assert_refused(response: dict, code: str) -> None:
    assert response["result"] is None, response
    assert response["error"]["code"] == code, response["error"]
    if code in SOURCE_ERROR_TABLE:
        assert response["error"]["category"] == SOURCE_ERROR_TABLE[code][0]
        assert response["error"]["retryable"] == SOURCE_ERROR_TABLE[code][1]
    else:
        assert code in _ENVELOPE_ERRORS, code
        assert response["error"]["category"] == _ENVELOPE_ERRORS[code]


# ---------------------------------------------------------------------------
# AC-LS4B-3/4: success writes ONLY the two auth columns, in place
# ---------------------------------------------------------------------------


def test_reattest_updates_only_the_two_auth_columns(core_bundle) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    before_row = _location_row(core)
    before_tables = _table_snapshot(core)
    before_bindings = core.conn.execute(
        "SELECT * FROM page_bindings ORDER BY binding_id"
    ).fetchall()
    location_count = core.conn.execute(
        "SELECT COUNT(*) FROM source_locations"
    ).fetchone()[0]
    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)

    response = _reattest(server, core_session, grant_id=grant_id)

    assert response["error"] is None, response["error"]
    assert response["result"] == {
        "source_id": "s1",
        "updated": 1,
        "version": "sv1",
    }
    after_row = _location_row(core)
    # The two auth columns are the ONLY changed columns...
    assert after_row["registry_id"] == "reg-new"
    assert after_row["authorization_generation"] == 3
    # ...and ``last_verified_at`` keeps the original audit value (no now()).
    assert after_row["last_verified_at"] == ORIGINAL_LAST_VERIFIED_AT
    assert after_row["observed_at"] == before_row["observed_at"]
    changed = {
        key for key in before_row if before_row[key] != after_row[key]
    }
    assert changed == {"registry_id", "authorization_generation"}
    assert core.conn.execute(
        "SELECT COUNT(*) FROM source_locations"
    ).fetchone()[0] == location_count == 1
    # Business tables other than the ONE row stay byte-identical: the location
    # table is expected to differ, everything else (notably page_bindings) not.
    after_tables = _table_snapshot(core)
    assert {
        name for name in before_tables if before_tables[name] != after_tables[name]
    } == {"source_locations"}
    assert core.conn.execute(
        "SELECT * FROM page_bindings ORDER BY binding_id"
    ).fetchall() == before_bindings
    # The command never registers a new grant: the ledger gained exactly the
    # Host-minted witness grant and nothing else.
    assert set(core.source_read_refs._grants) == {grant_id}
    # The capability is advertised and the client cannot widen the surface.
    ping = _app_request(server, "core.ping", {})
    assert "source.reattest/1" in ping["result"]["capabilities"]


def test_reattest_is_idempotent_and_writes_nothing_on_repeat(core_bundle) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
    first = _reattest(server, core_session, grant_id=grant_id)
    assert first["result"]["updated"] == 1, first
    before_row = _location_row(core)
    before_tables = _table_snapshot(core)

    second = _reattest(server, core_session, grant_id=grant_id)

    assert second["error"] is None, second["error"]
    assert second["result"] == {
        "source_id": "s1",
        "updated": 0,
        "version": "sv1",
    }
    assert _location_row(core) == before_row
    assert _table_snapshot(core) == before_tables


def test_reattest_generation_is_monotonic_and_cross_registry_is_allowed(
    core_bundle,
) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    # Cross registry: the new registration starts at generation 1 (allowed).
    high = _mint(core, seeded, registry_id="reg-high", generation=5)
    assert _reattest(server, core_session, grant_id=high)["result"]["updated"] == 1
    # Same registry MUST NOT move the generation backwards.
    lower = _mint(core, seeded, registry_id="reg-high", generation=4)
    before = _location_row(core)
    response = _reattest(server, core_session, grant_id=lower)
    assert response["error"] is None, response["error"]
    assert response["result"]["updated"] == 0
    assert _location_row(core) == before
    # A different registry is a re-registration, generation 1 is legitimate.
    other = _mint(core, seeded, registry_id="reg-other", generation=1)
    assert _reattest(server, core_session, grant_id=other)["result"]["updated"] == 1
    assert _location_row(core)["registry_id"] == "reg-other"
    assert _location_row(core)["authorization_generation"] == 1


# ---------------------------------------------------------------------------
# AC-LS4B-3: grant liveness / scope / identity refusals with ZERO writes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("case", ["missing", "expired", "revoked"])
def test_reattest_refuses_when_the_grant_is_not_live(
    core_bundle, monkeypatch, case: str
) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    if case == "missing":
        grant_id = "grant-" + uuid.uuid4().hex
        expected = "SOURCE_ACCESS_DENIED"
    else:
        grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
        if case == "expired":
            monkeypatch.setattr(
                core.source_read_refs, "_clock", lambda: time.time() + 301
            )
            expected = "SOURCE_GRANT_EXPIRED"
        else:
            revoked = _request(
                server,
                core_session,
                "RevokeSourceReadGrant",
                {
                    "registry_id": "reg-new",
                    "generation": 4,
                    "grant_ids": [grant_id],
                },
            )
            assert revoked["error"] is None
            expected = "SOURCE_GRANT_REVOKED"
    before_tables = _table_snapshot(core)
    response = _reattest(server, core_session, grant_id=grant_id)
    _assert_refused(response, expected)
    # §7: no absolute path / entry name / signing material in the error.
    serialized = json.dumps(response["error"])
    assert str(seeded["archive"].parent) not in serialized
    assert "source.zip" not in serialized
    assert _table_snapshot(core) == before_tables


def test_reattest_requires_the_grant_scope_source(core_bundle) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    grant_id = _mint(
        core, seeded, source_id="other-source", registry_id="reg-new", generation=3
    )
    before_tables = _table_snapshot(core)
    response = _reattest(server, core_session, grant_id=grant_id)
    _assert_refused(response, "SOURCE_ACCESS_DENIED")
    assert _table_snapshot(core) == before_tables


@pytest.mark.parametrize("case", ["digest", "volume", "file", "size"])
def test_reattest_requires_the_same_physical_identity(core_bundle, case: str) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    facts = seeded["facts"]
    column, value = {
        "digest": ("content_digest", "f" * 64),
        "volume": ("volume_serial", facts["volume_serial"] + 1),
        "file": ("file_id", facts["file_id"] + 1),
        "size": ("size_bytes", facts["size"] + 1),
    }[case]
    core.conn.execute(
        f"UPDATE source_locations SET {column} = ? WHERE source_id = 's1'",
        (value,),
    )
    core.conn.commit()
    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
    before_tables = _table_snapshot(core)
    response = _reattest(server, core_session, grant_id=grant_id)
    _assert_refused(response, "SOURCE_ACCESS_DENIED")
    assert _table_snapshot(core) == before_tables


def test_reattest_without_a_current_location_is_refused(core_bundle) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    core.conn.execute(
        "INSERT INTO sources (source_id, source_kind, created_at, updated_at)"
        " VALUES ('src-no-location', 'zip', ?, ?)",
        (NOW, NOW),
    )
    core.conn.commit()
    grant_id = _mint(
        core, seeded, source_id="src-no-location", registry_id="reg-new", generation=3
    )
    before_tables = _table_snapshot(core)
    response = _reattest(
        server, core_session, source_id="src-no-location", grant_id=grant_id
    )
    _assert_refused(response, "SOURCE_ACCESS_DENIED")
    assert _table_snapshot(core) == before_tables


def test_reattest_rejects_folder_grants(core_bundle) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    folder = seeded["archive"].parent / "folder-source"
    folder.mkdir(parents=True, exist_ok=True)
    first = folder / "001.png"
    second = folder / "002.png"
    first.write_bytes(png_bytes(4, 3, (1, 2, 3)))
    second.write_bytes(png_bytes(4, 3, (4, 5, 6)))
    grant_id = _mint(
        core,
        seeded,
        kind="folder",
        registry_id="reg-new",
        generation=3,
        entries=[(first, "001.png", 0), (second, "002.png", 1)],
    )
    before_tables = _table_snapshot(core)
    response = _reattest(server, core_session, grant_id=grant_id)
    _assert_refused(response, "SOURCE_ACCESS_DENIED")
    assert _table_snapshot(core) == before_tables


# ---------------------------------------------------------------------------
# AC-LS4B-3: closed shape / host-only / session (no new error codes)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "case",
    [
        "non_object",
        "empty",
        "missing_grant",
        "missing_source",
        "unknown_key",
        "non_string_source",
        "non_string_grant",
        "empty_source",
        "empty_grant",
        "three_keys",
    ],
)
def test_reattest_rejects_non_closed_shapes(core_bundle, case: str) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
    payload: object = {"source_id": "s1", "grant_id": grant_id}
    if case == "non_object":
        payload = "source_id=s1"
    elif case == "empty":
        payload = {}
    elif case == "missing_grant":
        payload = {"source_id": "s1"}
    elif case == "missing_source":
        payload = {"grant_id": grant_id}
    elif case == "unknown_key":
        payload = {"source_id": "s1", "grant_id": grant_id, "registry_id": "reg-new"}
    elif case == "non_string_source":
        payload = {"source_id": 1, "grant_id": grant_id}
    elif case == "non_string_grant":
        payload = {"source_id": "s1", "grant_id": 2}
    elif case == "empty_source":
        payload = {"source_id": "", "grant_id": grant_id}
    elif case == "empty_grant":
        payload = {"source_id": "s1", "grant_id": ""}
    elif case == "three_keys":
        payload = {"source_id": "s1", "grant_id": grant_id, "command": "start_run"}
    before_tables = _table_snapshot(core)
    response = _request(server, core_session, "ReattestSourceLocation", payload)
    _assert_refused(response, "INVALID_REQUEST")
    assert _table_snapshot(core) == before_tables


def test_reattest_is_host_only_and_session_gated(core_bundle) -> None:
    core, server, seeded = core_bundle
    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
    ordinary = _app_request(
        server, "ReattestSourceLocation", {"source_id": "s1", "grant_id": grant_id}
    )
    _assert_refused(ordinary, "HOST_ONLY_REQUIRED")

    core_session = _open(server)
    before_tables = _table_snapshot(core)
    wrong_credential = _wire("ReattestSourceLocation", {"source_id": "s1", "grant_id": grant_id})
    wrong_credential.update(
        {
            "core_session_id": core_session,
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": "wrong credential",
        }
    )
    response, _ = server.dispatch_request(json.dumps(wrong_credential))
    _assert_refused(response, "HOST_SESSION_INVALID")

    other_core = _wire("ReattestSourceLocation", {"source_id": "s1", "grant_id": grant_id})
    other_core.update(
        {
            "core_session_id": "another-core-process",
            "host_session_id": HOST_SESSION_ID,
            "host_session_credential": HOST_CREDENTIAL,
        }
    )
    response, _ = server.dispatch_request(json.dumps(other_core))
    _assert_refused(response, "CORE_SESSION_MISMATCH")
    assert _table_snapshot(core) == before_tables


# ---------------------------------------------------------------------------
# AC-LS4B-4/5: single SQL implementation and no new error code
# ---------------------------------------------------------------------------


def test_reattest_uses_the_single_location_refresh_sql() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    occurrences: list[str] = []
    for path in sorted((repo_root / "src").rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "UPDATE source_locations SET registry_id" in text:
            occurrences.append(path.relative_to(repo_root).as_posix())
    assert occurrences == ["src/infrastructure/sqlite/library.py"], occurrences


def test_reattest_introduces_no_new_error_codes(core_bundle) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
    codes: set[str] = set()
    for payload in (
        {"source_id": "s1"},
        {"source_id": "s1", "grant_id": grant_id, "x": 1},
        {"source_id": "s2", "grant_id": grant_id},
        {"source_id": "s1", "grant_id": "grant-" + uuid.uuid4().hex},
    ):
        response = _request(server, core_session, "ReattestSourceLocation", payload)
        assert response["error"] is not None
        codes.add(response["error"]["code"])
    assert codes <= set(SOURCE_ERROR_TABLE) | {"INVALID_REQUEST"}
    ping = _app_request(server, "core.ping", {})
    capabilities = set(ping["result"]["capabilities"])
    assert "source.reattest/1" in capabilities
    assert not any(
        name.startswith("source.reattest/") and name != "source.reattest/1"
        for name in capabilities
    )


# ---------------------------------------------------------------------------
# AC-LS4B-6: re-attest -> cold-start enumeration returns the NEW auth pair
# ---------------------------------------------------------------------------


def test_reattest_then_cold_start_enumeration_recovers_the_new_pair(
    core_bundle,
) -> None:
    core, server, seeded = core_bundle
    core_session = _open(server)
    before = _app_request(server, "source_list_scan_targets", {})["result"]["targets"]
    assert [(target["registry_id"], target["generation"]) for target in before] == [
        ("reg-old", 1)
    ]
    assert before[0]["source_id"] == "s1"
    identity = before[0]["identity_digest"]
    projects = before[0]["project_ids"]

    grant_id = _mint(core, seeded, registry_id="reg-new", generation=3)
    assert _reattest(server, core_session, grant_id=grant_id)["result"]["updated"] == 1

    after = _app_request(server, "source_list_scan_targets", {})["result"]["targets"]
    assert [(target["registry_id"], target["generation"]) for target in after] == [
        ("reg-new", 3)
    ]
    assert after[0]["identity_digest"] == identity
    assert after[0]["project_ids"] == projects

    # The enumeration itself stays a zero-write read face after the re-attest.
    tables_before = _table_snapshot(core)
    _app_request(server, "source_list_scan_targets", {})
    assert _table_snapshot(core) == tables_before
