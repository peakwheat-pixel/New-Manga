"""FEA-11-RUN-GRANT-1 evidence: Run-scoped source-read authorization.

Covers the frozen C-16 v1.3 §2.4 ``AuthorizeSourceReadForRun`` semantics on a
REAL production assembly (``assemble_core_services`` over real migrations, a
real zip/PNG source and real HMAC-signed grants) plus a Run-level commit test
driven by the same production handler:

* AC-R1: protocol surface is covered in ``tests/core/test_host_control.py``;
  the idempotent success path lives here.
* AC-R2: after the new command binds the grant, the Run target expands, the
  provider reads the CURRENT binding's pixels (not the managed copy) and the
  Run commit guard opens; Run-level commits then write the expected
  region/revision/lineage rows. Discrimination: no write, wrong entry, wrong
  facts -> typed refusal with zero business writes.
* AC-R3: fail-closed matrix (no grant / expired / revoked / scope+facts
  mismatch / pending gate / binding switched mid-Run) stays typed, writes
  nothing and never leases the source on the authorization face.
* AC-R5: managed targets are skipped (``bound_pages == 0``), never refused,
  and the TargetSnapshot metadata key set is unchanged.

Isolation: every scratch DB/zip lives under
``G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/`` (task data root).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import io
import json
import sqlite3
import time
import uuid
from pathlib import Path
from types import SimpleNamespace

import pytest

from application.importing.referenced.errors import SourceImportError
from application.tasks.service import PipelineService
from bootstrap.core_assembly import assemble_core_services
from bootstrap.core_service import PROTOCOL_MAJOR, PROTOCOL_MINOR, CoreServiceServer
from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
)
from infrastructure.resource_channel.source_read_refs import SourceReadGrantRegistry
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from infrastructure.sqlite.source_sync import SourceSyncStore
from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    file_facts,
    write_zip,
)
from tests.fea11.test_source_rendition_gates import (
    _assemble as _assembled_core,
    _handler_bound,
)
from tests.fea11.test_source_rendition_run import (
    _execute,
    _lineage_rows,
    _page_scope,
    _region_rows,
    _revision_rows,
    build_run_harness,
)
from tests.fea11.test_source_rendition_source import (
    OLD_A,
    NEW_B,
    build_rendition_site,
    png_of,
)

#: Task data/isolation root (never a real user data root).
WORKSPACE_ROOT = Path("G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1")
FIXTURE_ROOT = WORKSPACE_ROOT / "fixtures"

HOST_SESSION_ID = "host-session-run-grant"
HOST_CREDENTIAL = base64.urlsafe_b64encode(bytes(range(32))).decode().rstrip("=")
SIGNING_KEY = bytes(range(32))

#: The frozen TargetSnapshot.metadata key set (no new key may be added).
TARGET_METADATA_KEYS = {
    "source_filename",
    "managed_original_ref",
    "source_hash",
    "lineage_hidden_regions",
    "commit_guard",
    # The pre-existing ``create_run`` context projection (RENDITION-1 froze the
    # same six-key set; this card adds no key).
    "context_pages",
}


@pytest.fixture()
def run_root(request) -> Path:
    root = FIXTURE_ROOT / f"{request.node.name}-{uuid.uuid4().hex[:8]}"
    root.mkdir(parents=True, exist_ok=True)
    return root


# ---------------------------------------------------------------------------
# real seed: v8 library + real zip + pure referenced pages
# ---------------------------------------------------------------------------


def _seed_library(db_path: Path, managed_root: Path) -> dict:
    """A real v8 library with two referenced pages over ONE real zip archive."""
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
    old_png = png_of(OLD_A)
    current_png = png_of(NEW_B)
    old_digest = hashlib.sha256(old_png).hexdigest()
    current_digest = hashlib.sha256(current_png).hexdigest()
    archive = write_zip(
        db_path.parent / "current-source.zip",
        [("001-old.png", old_png), ("002-current.png", current_png)],
    )
    archive_facts = file_facts(archive)
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=archive_facts["sha256"],
        entries=[
            ("se1", "001-old.png", old_digest),
            ("se2", "002-current.png", current_digest),
        ],
        volume_serial=archive_facts["volume_serial"],
        file_id=archive_facts["file_id"],
        legacy_v7_evidence=False,
    )
    # ``add_source_tree`` writes the container size as a hand-seeded 100; the
    # facts check needs the REAL container identity (no path fallback).
    conn.execute(
        "UPDATE source_locations SET size_bytes = ? WHERE source_id = 's1'",
        (archive_facts["size"],),
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
        digest=old_digest,
        width=OLD_A["width"],
        height=OLD_A["height"],
    )
    add_referenced_page(
        conn,
        "p2",
        "c1",
        "b1",
        order=2,
        source_id="s1",
        version_id="sv1",
        entry_id="se2",
        digest=current_digest,
        width=NEW_B["width"],
        height=NEW_B["height"],
    )
    (managed_root / "legacy").mkdir(parents=True, exist_ok=True)
    (managed_root / "legacy" / "pm.png").write_bytes(png_of(OLD_A))
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
        " updated_at, source_filename, source_order, source_hash,"
        " source_size_bytes, width, height, managed_original_ref,"
        " source_mode, integrity_status)"
        " VALUES ('pm', 'c1', 3, ?, ?, 'pm.png', 3, ?, 10, ?, ?,"
        " 'legacy/pm.png', 'managed', 'complete')",
        (NOW, NOW, "b" * 64, OLD_A["width"], OLD_A["height"]),
    )
    conn.commit()
    conn.close()
    return {
        "archive": archive,
        "archive_facts": archive_facts,
        "old_digest": old_digest,
        "current_digest": current_digest,
    }


def _assemble(db_path: Path, managed_root: Path):
    return _assembled_core(db_path, managed_root)


# ---------------------------------------------------------------------------
# host-control dispatch helpers (real CoreServiceServer over the assembled core)
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
            {
                **_wire(
                    "OpenHostSession",
                    {
                        "host_session_id": HOST_SESSION_ID,
                        "host_session_credential": HOST_CREDENTIAL,
                    },
                )
            }
        )
    )
    assert response["error"] is None, response["error"]
    return response["result"]["core_session_id"]


def _request(
    server: CoreServiceServer, core_session_id: str, command: str, payload: dict
) -> dict:
    request = _wire(command, payload)
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


def _sign(key: bytes, fields: dict) -> str:
    encoded = json.dumps(
        fields, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return (
        base64.urlsafe_b64encode(hmac.new(key, encoded, hashlib.sha256).digest())
        .decode()
        .rstrip("=")
    )


def _grant_payload(
    archive: Path,
    *,
    source_id: str = "s1",
    version: str = "sv1",
    locator: str = "002-current.png",
    ordinal: int = 1,
    kind: str = "zip",
    grant_id: str | None = None,
    expires_at: float | None = None,
) -> dict:
    """One real HMAC-signed source-read grant payload over the real archive."""
    facts = file_facts(archive)
    grant_id = grant_id or ("source-" + uuid.uuid4().hex)
    expires = expires_at if expires_at is not None else time.time() + 290.0
    payload = {
        "grant_id": grant_id,
        "session_id": HOST_SESSION_ID,
        "operation": "source-read",
        "scope_class": "user-source",
        "registry_id": "reg-1",
        "generation": 1,
        "expires_at": expires,
        "budget": {
            "max_bytes": 8 * 1024 * 1024,
            "max_decode_bytes": 8 * 1024 * 1024,
            "max_entries": 10000,
        },
        "scope": {
            "source_id": source_id,
            "version": version,
            "rendition": {
                "decoder": kind,
                "scale": 1.0,
                "params_digest": "0" * 64,
            },
            "entries": [
                {
                    "entry_key": "entry-0",
                    "locator": locator,
                    "ordinal": ordinal,
                    "path": str(archive.resolve()),
                    "facts": facts,
                }
            ],
        },
    }
    signed = dict(payload)
    signed["expires_at"] = f"{expires:.6f}"
    payload["signing_key"] = (
        base64.urlsafe_b64encode(SIGNING_KEY).decode().rstrip("=")
    )
    payload["signature"] = _sign(SIGNING_KEY, signed)
    return payload


def _register(
    server: CoreServiceServer, core_session_id: str, payload: dict
) -> dict:
    return _request(server, core_session_id, "RegisterSourceReadGrant", payload)


def _authorize(
    server: CoreServiceServer,
    core_session_id: str,
    grant_ids: list[str],
    *,
    command: str = "reocr_all",
    scope: dict | None = None,
) -> dict:
    return _request(
        server,
        core_session_id,
        "AuthorizeSourceReadForRun",
        {
            "grant_ids": grant_ids,
            "command": command,
            "scope": scope or {"kind": "page", "page_id": "p2"},
        },
    )


def _table_snapshot(core) -> dict[str, str]:
    """Per-table row snapshot (every business table, byte-for-byte)."""
    conn = core.conn
    names = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
            " AND name NOT LIKE 'sqlite_%' ORDER BY name"
        ).fetchall()
    ]
    snapshot: dict[str, str] = {}
    for name in names:
        try:
            rows = conn.execute(f'SELECT * FROM "{name}"').fetchall()
        except sqlite3.Error:  # virtual/fts tables keep a live count only
            rows = [("__count__", conn.execute(
                f'SELECT COUNT(*) FROM "{name}"').fetchone()[0])]
        payload = repr(sorted(repr(tuple(row)) for row in rows))
        snapshot[name] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    return snapshot


def _bindings(registry: SourceReadGrantRegistry) -> dict:
    return {
        grant_id: {
            "source_id": value["source_id"],
            "version_id": value["version_id"],
            "entry_ids": set(value["entry_ids"]),
        }
        for grant_id, value in registry._bindings.items()
    }


def _switch_page_binding_to_new_version(conn, *, page_id: str, binding_id: str) -> str:
    """Supersede one page binding with a healthy binding on a NEW source version.

    Mirrors a sync apply switch (C-17 §6): the real v8 rows/FKs are honoured,
    only the version identity differs from the granted one.
    """
    conn.execute(
        "INSERT INTO source_versions (version_id, source_id, location_id,"
        " content_digest, size_bytes, observed_at, created_at)"
        " SELECT 'sv2', source_id, location_id, ?, size_bytes, observed_at,"
        " created_at FROM source_versions WHERE version_id = 'sv1'",
        ("f" * 64,),
    )
    conn.execute(
        "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
        " ordinal, stable_sort_key, content_digest_kind, content_digest,"
        " size_bytes, created_at)"
        " SELECT source_id, 'sv2', entry_id, locator, ordinal, stable_sort_key,"
        " content_digest_kind, content_digest, size_bytes, created_at"
        " FROM source_entries WHERE version_id = 'sv1' AND entry_id = 'se2'",
    )
    conn.execute(
        "UPDATE page_bindings SET status = 'superseded' WHERE binding_id = ?",
        (binding_id,),
    )
    # The C-15 visibility witness compares verified_digest with the entry
    # digest: keep the switched page visible so the refusal under test is the
    # GRANT one, not the library visibility predicate.
    digest = conn.execute(
        "SELECT content_digest FROM source_entries WHERE version_id = 'sv2'"
        " AND entry_id = 'se2'"
    ).fetchone()[0]
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, previous_binding_id, authorization_generation,"
        " authorized_at, verified_digest, created_at, updated_at)"
        " VALUES (?, ?, 'b1', 2, 's1', 'se2', 'sv2', 'healthy', ?, 1, ?, ?,"
        " ?, ?)",
        (binding_id + "-b2", page_id, binding_id, NOW, digest, NOW, NOW),
    )
    conn.commit()
    return binding_id + "-b2"


@pytest.fixture()
def real_core(run_root: Path):
    db_path = run_root / "core" / "library.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    managed_root = run_root / "core" / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    facts = _seed_library(db_path, managed_root)
    core = _assemble(db_path, managed_root)
    server = CoreServiceServer(core, stdin=io.StringIO(), stdout=io.StringIO())
    # The assembled pipeline defers Run recovery to its process-wide scheduler
    # lease; this test drives ``create_run`` directly (no scheduler thread).
    core.pipeline.set_scheduler_owner(True)
    try:
        yield core, server, facts
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# AC-R2: real assembly -> authorize -> Run target/provider/commit guard
# ---------------------------------------------------------------------------


def test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard(
    real_core,
) -> None:
    core, server, facts = real_core
    core_session = _open(server)

    # Zero business writes by the authorization itself: per-table snapshot.
    before = _table_snapshot(core)
    grant = _grant_payload(facts["archive"])
    registered = _register(server, core_session, grant)
    assert registered["error"] is None, registered["error"]

    before_authorize = _table_snapshot(core)
    authorized = _authorize(server, core_session, [grant["grant_id"]])
    assert authorized["error"] is None, authorized["error"]
    assert authorized["result"] == {"bound_pages": 1}
    assert _table_snapshot(core) == before_authorize, (
        "AuthorizeSourceReadForRun must not write any business table"
    )
    assert before_authorize["pages"] == before["pages"]

    # The mapping is the same in-process shape bind_imported_entry writes.
    assert _bindings(core.source_read_refs) == {
        grant["grant_id"]: {
            "source_id": "s1",
            "version_id": "sv1",
            "entry_ids": {"se2"},
        }
    }

    # The Run expands the SAME page through the SAME catalog the Run command
    # uses, and the commit guard (which requires a bound live grant) opens.
    run = core.pipeline.create_run(
        CommandType.REOCR_ALL, PipelineScope(ScopeType.PAGE, selected_ids=("p2",))
    )
    assert [target.target_id for target in run.targets] == ["p2"]
    assert set(run.targets[0].snapshot.metadata) == TARGET_METADATA_KEYS
    with core.pipeline._catalog.source_commit_guard("p2"):
        pass  # no exception: grant + lease + facts are live

    # The provider really reads the CURRENT binding's pixels, not the stale
    # managed copy (12x7 B vs 30x20 A).
    images = _handler_bound(core).__self__.deps.images
    frame = images.page_frame("p2")
    assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])
    # The managed page is still read from the Managed Copy (zero regression).
    managed = images.page_frame("pm")
    assert (managed.width, managed.height) == (OLD_A["width"], OLD_A["height"])

    # Idempotent: the same request returns the same result and mapping.
    again = _authorize(server, core_session, [grant["grant_id"]])
    assert again["error"] is None, again["error"]
    assert again["result"] == {"bound_pages": 1}
    assert _bindings(core.source_read_refs) == {
        grant["grant_id"]: {
            "source_id": "s1",
            "version_id": "sv1",
            "entry_ids": {"se2"},
        }
    }


def test_authorization_is_entry_granular_and_refuses_other_pages(real_core) -> None:
    """The Core matches the binding's own entry inside the signed scope.

    R1-03 boundary: this test signs a member-shaped entry
    (``locator=002-current.png``, ``ordinal=1``) because that is the only shape
    that can name an archive member; the production Host cannot mint it for a
    container (it mints ONE container entry — see L-G12). The assertion here
    proves the Core-side entry matching, NOT that a Host container grant covers
    arbitrary members.
    """
    core, server, facts = real_core
    core_session = _open(server)
    # The grant covers the CURRENT entry (002-current.png / se2).
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None

    # p1 binds the OTHER archive member: not covered by the signed entry.
    refused = _authorize(
        server,
        core_session,
        [grant["grant_id"]],
        scope={"kind": "page", "page_id": "p1"},
    )
    assert refused["result"] is None
    assert refused["error"]["code"] == "SOURCE_ACCESS_DENIED"
    refused_details = refused["error"]["details"][0]
    assert refused_details == {"refused_pages": 1}
    assert _bindings(core.source_read_refs) == {}
    with pytest.raises(SourceImportError) as guard:
        with core.pipeline._catalog.source_commit_guard("p1"):
            pytest.fail("an unauthorized entry must never open the commit window")
    assert guard.value.code == "SOURCE_ACCESS_DENIED"


def test_real_run_commit_writes_expected_rows_after_authorization(run_root) -> None:
    """AC-R2 commit half: the production handler's mapping feeds a real Run."""
    conn = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
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
    conn.commit()
    registry = SourceReadGrantRegistry()
    site = build_rendition_site(
        conn,
        ("b1", "c1"),
        run_root,
        registry,
        bind_grant=False,
        managed_copy=False,
    )
    # The real container identity: the facts check has no path fallback and
    # reads only source_locations/source_entries.
    facts = file_facts(site.archive_path)
    conn.execute(
        "UPDATE source_locations SET content_digest = ?, volume_serial = ?,"
        " file_id = ?, size_bytes = ? WHERE source_id = 's1'",
        (
            facts["sha256"],
            facts["volume_serial"],
            facts["file_id"],
            facts["size"],
        ),
    )
    conn.commit()
    harness = build_run_harness(site, access=registry)

    # The production handler runs against this real store: fake only the
    # ``self._core`` bag, never the code under test.
    server = CoreServiceServer.__new__(CoreServiceServer)
    server._core = SimpleNamespace(
        pipeline=harness.service,
        source_read_refs=registry,
        source_sync={"store": SourceSyncStore(conn)},
    )
    assert (
        server._authorize_source_read_for_run(
            {
                "grant_ids": [site.grant_id],
                "command": "reocr_all",
                "scope": {"kind": "page", "page_id": "pr"},
            }
        )
        == {"bound_pages": 1}
    )

    run = _execute(harness, _page_scope("pr"))
    assert run.status.value in ("completed", "completed_with_failures"), run.status
    assert _region_rows(conn) >= 1
    assert _revision_rows(conn) >= 1
    assert _lineage_rows(conn) >= 1  # detect registers native lineage on commit
    assert harness.detector.requests, "the detect step never received the page"


def test_real_run_without_authorization_writes_nothing(run_root) -> None:
    """Discrimination: the SAME Run stays typed and writes zero rows without
    the authorization mapping (the pre-fix L-R1 behaviour)."""
    conn = sqlite3.connect(":memory:", check_same_thread=False, isolation_level=None)
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
    conn.commit()
    registry = SourceReadGrantRegistry()
    site = build_rendition_site(
        conn,
        ("b1", "c1"),
        run_root,
        registry,
        bind_grant=False,
        managed_copy=False,
    )
    facts = file_facts(site.archive_path)
    conn.execute(
        "UPDATE source_locations SET content_digest = ?, volume_serial = ?,"
        " file_id = ?, size_bytes = ? WHERE source_id = 's1'",
        (
            facts["sha256"],
            facts["volume_serial"],
            facts["file_id"],
            facts["size"],
        ),
    )
    conn.commit()
    harness = build_run_harness(site, access=registry)

    executed = _execute(harness, _page_scope("pr"))
    assert executed.status in {
        PipelineRunStatus.FAILED,
        PipelineRunStatus.COMPLETED_WITH_FAILURES,
    }, [(step.step_type, step.error_code) for step in executed.step_runs]
    step_codes = {
        step.error_code for step in executed.step_runs if step.error_code
    }
    assert step_codes & {"INVALID_INPUT", "PROVIDER_FAILED"}, step_codes
    assert _region_rows(conn) == 0
    assert _revision_rows(conn) == 0
    assert _lineage_rows(conn) == 0
    assert not harness.detector.requests


# ---------------------------------------------------------------------------
# AC-R3: fail-closed matrix
# ---------------------------------------------------------------------------


def _assert_refused(response: dict, code: str) -> dict:
    assert response["result"] is None
    assert response["error"]["code"] == code, response["error"]
    return response["error"]


def test_missing_grant_is_refused_and_writes_nothing(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    before = _table_snapshot(core)
    error = _assert_refused(
        _authorize(server, core_session, ["source-" + "0" * 32]),
        "SOURCE_ACCESS_DENIED",
    )
    assert error["category"] == "authorization"
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}


def test_expired_grant_is_refused_with_the_frozen_priority(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    # Inject the clock: a 300s window that has just elapsed.
    original_clock = core.source_read_refs._clock
    core.source_read_refs._clock = lambda: time.time() + 301
    try:
        before = _table_snapshot(core)
        error = _assert_refused(
            _authorize(server, core_session, [grant["grant_id"]]),
            "SOURCE_GRANT_EXPIRED",
        )
        assert error["category"] == "authorization"
        assert _table_snapshot(core) == before
        assert _bindings(core.source_read_refs) == {}
    finally:
        core.source_read_refs._clock = original_clock


def test_revoked_grant_is_refused_with_the_frozen_priority(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    revoked = _request(
        server,
        core_session,
        "RevokeSourceReadGrant",
        {
            "registry_id": "reg-1",
            "generation": 2,
            "grant_ids": [grant["grant_id"]],
        },
    )
    assert revoked["error"] is None, revoked["error"]
    before = _table_snapshot(core)
    error = _assert_refused(
        _authorize(server, core_session, [grant["grant_id"]]),
        "SOURCE_GRANT_REVOKED",
    )
    assert error["category"] == "authorization"
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}


def test_scope_and_facts_mismatch_is_refused(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    # A grant for a DIFFERENT version never matches the current binding.
    wrong_version = _grant_payload(facts["archive"], version="sv2")
    assert _register(server, core_session, wrong_version)["error"] is None
    before = _table_snapshot(core)
    _assert_refused(
        _authorize(server, core_session, [wrong_version["grant_id"]]),
        "SOURCE_ACCESS_DENIED",
    )
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}

    # A fact mismatch (the recorded physical identity moved) also refuses.
    ok_grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, ok_grant)["error"] is None
    core.conn.execute(
        "UPDATE source_locations SET size_bytes = size_bytes + 1"
        " WHERE source_id = 's1'"
    )
    core.conn.commit()
    error = _assert_refused(
        _authorize(server, core_session, [ok_grant["grant_id"]]),
        "SOURCE_ACCESS_DENIED",
    )
    assert error["details"][0] == {"refused_pages": 1}
    assert _bindings(core.source_read_refs) == {}


def test_pending_publication_gate_blocks_the_authorization(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    from tests.fea11.test_source_rendition_gates import _insert_publication

    _insert_publication(core.conn, "pb-p2", "pending")
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    before = _table_snapshot(core)

    # Run face: the pending gate is the existing typed TARGET_NOT_FOUND.
    with pytest.raises(Exception) as run_refusal:
        core.pipeline.create_run(
            CommandType.REOCR_ALL,
            PipelineScope(ScopeType.PAGE, selected_ids=("p2",)),
        )
    assert getattr(run_refusal.value, "code", None) == "TARGET_NOT_FOUND"

    # Authorization face: the page cannot be expanded through the Run target
    # catalog (the SAME gate predicate), so the command is refused typed and
    # writes neither a mapping nor a business row.
    error = _assert_refused(
        _authorize(server, core_session, [grant["grant_id"]]),
        "INVALID_REQUEST",
    )
    assert error["category"] == "validation"
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}
    assert core.source_read_refs._grants  # the grant itself is untouched


def test_binding_switched_mid_run_is_typed_and_writes_nothing(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    authorized = _authorize(server, core_session, [grant["grant_id"]])
    assert authorized["error"] is None, authorized["error"]
    assert _bindings(core.source_read_refs) != {}

    # A sync apply switches the page's binding to a DIFFERENT version: the old
    # granted entry is no longer the current binding's entry.
    conn = core.conn
    _switch_page_binding_to_new_version(conn, page_id="p2", binding_id="pb-p2")
    regions_before = _region_rows(conn)
    revisions_before = _revision_rows(conn)
    lineage_before = _lineage_rows(conn)

    images = _handler_bound(core).__self__.deps.images
    from ports.providers.errors import ProviderInputError

    with pytest.raises(ProviderInputError) as provider_refusal:
        images.page_frame("p2")
    assert provider_refusal.value.error_code == "INVALID_INPUT"
    assert "SOURCE_ACCESS_DENIED" in provider_refusal.value.detail
    with pytest.raises(SourceImportError):
        with core.pipeline._catalog.source_commit_guard("p2"):
            pytest.fail("a switched binding must not open the commit window")
    assert _region_rows(conn) == regions_before
    assert _revision_rows(conn) == revisions_before
    assert _lineage_rows(conn) == lineage_before


def test_per_page_gate_refusal_uses_the_shared_gate_predicate(real_core) -> None:
    """R1-07: the per-page ``gate != open`` refusal inside
    ``authorize_run_bindings`` is reachable through a MIXED page (a pure
    referenced page is refused earlier by the Run target expander). It must be a
    whole-request typed ``SOURCE_ACCESS_DENIED`` with
    ``details={"refused_pages": 1}``, no mapping and no business write."""
    core, server, facts = real_core
    core_session = _open(server)
    from tests.fea11.test_source_rendition_gates import _insert_publication

    # Mixed page: referenced binding + a (stale) managed original -> the Run
    # target expander admits it; the per-page publication gate then refuses.
    conn = core.conn
    # A separate project/book keeps the frozen (project_id, entry_id) uniqueness
    # of the existing p1/p2 bindings intact.
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES ('b2', 'Book 2', ?, ?)",
        (NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES ('c2', 'b2', 'Ch 2', ?, ?)",
        (NOW, NOW),
    )
    conn.commit()
    (core.data_root / "managed" / "legacy").mkdir(parents=True, exist_ok=True)
    (core.data_root / "managed" / "legacy" / "p3.png").write_bytes(png_of(OLD_A))
    add_referenced_page(
        conn,
        "p3",
        "c2",
        "b2",
        order=1,
        source_id="s1",
        version_id="sv1",
        entry_id="se2",
        digest=facts["current_digest"],
        width=NEW_B["width"],
        height=NEW_B["height"],
    )
    conn.execute(
        "UPDATE pages SET managed_original_ref = 'legacy/p3.png'"
        " WHERE page_id = 'p3'"
    )
    conn.commit()
    _insert_publication(conn, "pb-p3", "pending")

    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    before = _table_snapshot(core)
    error = _assert_refused(
        _authorize(
            server,
            core_session,
            [grant["grant_id"]],
            scope={"kind": "page", "page_id": "p3"},
        ),
        "SOURCE_ACCESS_DENIED",
    )
    assert error["details"][0] == {"refused_pages": 1}
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}


def test_authorization_never_leases_or_reads_the_source(real_core, monkeypatch) -> None:
    """R1-07: the authorization face reads NO source bytes.

    Two spies: ``source_lease`` (the strict-read lease every granted byte read
    goes through) and ``read_entry_bytes`` (the decode entry point). Both must
    stay at zero for the authorization command.
    """
    core, server, facts = real_core
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    leases: list[str] = []
    reads: list[tuple] = []
    import infrastructure.resource_channel.source_strict_read as strict
    from application.importing.referenced import reader as referenced_reader

    original_lease = strict.source_lease
    original_read = referenced_reader.read_entry_bytes

    def lease_spy(path, facts, max_bytes):
        leases.append(str(path))
        return original_lease(path, facts, max_bytes)

    def read_spy(*args, **kwargs):
        reads.append((args, kwargs))
        return original_read(*args, **kwargs)

    monkeypatch.setattr(strict, "source_lease", lease_spy)
    monkeypatch.setattr(referenced_reader, "read_entry_bytes", read_spy)
    authorized = _authorize(server, core_session, [grant["grant_id"]])
    assert authorized["error"] is None, authorized["error"]
    assert leases == [], "AuthorizeSourceReadForRun must not lease source bytes"
    assert reads == [], "AuthorizeSourceReadForRun must not read entry bytes"


# ---------------------------------------------------------------------------
# AC-R5: managed zero regression
# ---------------------------------------------------------------------------


def test_managed_targets_are_skipped_not_refused(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    before = _table_snapshot(core)

    # A managed-only scope: nothing to authorize, no mapping, no refusal.
    skipped = _authorize(
        server,
        core_session,
        [grant["grant_id"]],
        scope={"kind": "page", "page_id": "pm"},
    )
    assert skipped["error"] is None, skipped["error"]
    assert skipped["result"] == {"bound_pages": 0}
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}

    # The managed page keeps reading the Managed Copy through the same
    # provider (no grant, no gate, no registry touch).
    images = _handler_bound(core).__self__.deps.images
    frame = images.page_frame("pm")
    assert (frame.width, frame.height) == (OLD_A["width"], OLD_A["height"])

    run = core.pipeline.create_run(
        CommandType.REOCR_ALL, PipelineScope(ScopeType.PAGE, selected_ids=("pm",))
    )
    assert set(run.targets[0].snapshot.metadata) == TARGET_METADATA_KEYS


def test_forged_shape_requests_are_invalid_requests(real_core) -> None:
    core, server, facts = real_core
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    before = _table_snapshot(core)
    invalid_payloads = [
        {"grant_ids": [grant["grant_id"]], "command": "reocr_all"},
        {
            "grant_ids": [grant["grant_id"]],
            "command": "reocr_all",
            "scope": {"kind": "page", "page_id": "p2"},
            "extra": 1,
        },
        {
            "grant_ids": [],
            "command": "reocr_all",
            "scope": {"kind": "page", "page_id": "p2"},
        },
        {
            "grant_ids": [grant["grant_id"], grant["grant_id"]],
            "command": "reocr_all",
            "scope": {"kind": "page", "page_id": "p2"},
        },
        {
            "grant_ids": [grant["grant_id"]],
            "command": "not_a_command",
            "scope": {"kind": "page", "page_id": "p2"},
        },
        {
            "grant_ids": [grant["grant_id"]],
            "command": "reocr_all",
            "scope": {"kind": "region", "region_id": "r1"},
        },
    ]
    for payload in invalid_payloads:
        response = _request(
            server, core_session, "AuthorizeSourceReadForRun", payload
        )
        _assert_refused(response, "INVALID_REQUEST")
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}
