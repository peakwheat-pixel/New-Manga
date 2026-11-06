"""FEA-11-SCAN-2 B1: Core read-only cold-start scan-target enumeration.

C-17 v1.1 §5.1/§5.2: ``source_list_scan_targets`` is an ordinary application-face
command with the closed shape ``{}`` returning ``ScanTargets``
(``{targets:[{source_id,registry_id,generation,source_kind,identity_digest,
project_ids[]}]}``), sorted by ``source_id`` ascending, unique, empty array
legal.  It performs a single SELECT-level projection: zero DB writes, no
plan/apply/operation/receipt/grant/journal, and the authoritative ``source_id``
always comes from Core ``sources``.

The tests below are the discriminating guards for the frozen rulings:
  * unsorted output      -> the order assertions fail;
  * duplicate sources    -> the dedupe assertions fail;
  * widened/removed caps -> the budget tests fail;
  * fabricated identity  -> the identity recomputation test fails.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.sources.errors import SourceSyncError  # noqa: E402
from application.sources.model import identity_digest_of  # noqa: E402
from application.sources.scanner import list_scan_targets  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    CoreServiceServer,
    assemble_production_core,
)

NOW = "2026-11-06T00:00:00+00:00"
DIGEST_A = "a" * 64
DIGEST_B = "b" * 64

#: The frozen read faces that must stay byte-identical (the "14-table snapshot"
#: includes the source tables plus the sync audit tables).
SNAPSHOT_TABLES = (
    "books",
    "chapters",
    "pages",
    "page_bindings",
    "sources",
    "source_locations",
    "source_versions",
    "source_entries",
    "source_sync_plans",
    "source_operations",
    "source_binding_publications",
    "source_revision_lineage",
    "book_cleanup_manifests",
    "reading_progress",
)


@pytest.fixture
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    try:
        yield assembled
    finally:
        assembled.conn.close()


@pytest.fixture
def server(core):
    return CoreServiceServer(core)


def _dispatch(server: CoreServiceServer, command: str, payload: object) -> dict:
    raw, should_exit = server.dispatch_request(
        json.dumps(
            {
                "protocol": "new-manga.core",
                "version": {"major": 2, "minor": 3},
                "request_id": "fea11-scan2-core",
                "command": command,
                "payload": payload,
            }
        )
    )
    assert not should_exit
    return raw


def _enumerate(server: CoreServiceServer) -> dict:
    response = _dispatch(server, "source_list_scan_targets", {})
    assert response["error"] is None, response["error"]
    return response["result"]


def _snapshot(conn) -> dict[str, list[tuple]]:
    snapshot: dict[str, list[tuple]] = {}
    for table in SNAPSHOT_TABLES:
        rows = conn.execute(f'SELECT * FROM "{table}"').fetchall()
        snapshot[table] = [tuple(row) for row in rows]
    return snapshot


def _seed_source(conn, source_id: str, *, kind: str = "folder",
                 deleted: bool = False) -> None:
    conn.execute(
        "INSERT INTO sources (source_id, source_kind, display_name, created_at,"
        " updated_at, deleted_at) VALUES (?, ?, '', ?, ?, ?)",
        (source_id, kind, NOW, NOW, NOW if deleted else None),
    )


def _seed_location(
    conn,
    source_id: str,
    *,
    location_id: str | None = None,
    registry_id: str = "registry-1",
    generation: int = 1,
    content_digest: str = DIGEST_A,
    volume_serial: int = 1,
    file_id: int = 2,
    size_bytes: int = 10,
    is_current: int = 1,
) -> str:
    location_id = location_id or f"loc-{source_id}-{generation}"
    conn.execute(
        "INSERT INTO source_locations (location_id, source_id, registry_id,"
        " authorization_generation, content_digest, volume_serial, file_id,"
        " size_bytes, observed_at, is_current, created_at)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            location_id, source_id, registry_id, generation, content_digest,
            volume_serial, file_id, size_bytes, NOW, is_current, NOW,
        ),
    )
    return location_id


def _seed_version_entry(
    conn,
    source_id: str,
    *,
    version_id: str = "ver-1",
    entry_id: str = "entry-1",
) -> None:
    current = conn.execute(
        "SELECT location_id FROM source_locations"
        " WHERE source_id = ? AND is_current = 1",
        (source_id,),
    ).fetchone()
    assert current is not None
    conn.execute(
        "INSERT INTO source_versions (version_id, source_id, location_id,"
        " content_digest, size_bytes, observed_at, created_at)"
        " VALUES (?, ?, ?, ?, 10, ?, ?)",
        (version_id, source_id, current[0], DIGEST_A, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source_entries (source_id, version_id, entry_id, locator,"
        " ordinal, stable_sort_key, content_digest_kind, content_digest,"
        " size_bytes, created_at)"
        " VALUES (?, ?, ?, 'img/1.png', 0, '0', 'page-identity', ?, 10, ?)",
        (source_id, version_id, entry_id, DIGEST_B, NOW),
    )


def _seed_book_page(conn, book_id: str, *, page_id: str, chapter_id: str) -> None:
    conn.execute(
        "INSERT INTO books (book_id, title, created_at, updated_at)"
        " VALUES (?, ?, ?, ?)",
        (book_id, book_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
        " VALUES (?, ?, 'Ch', ?, ?)",
        (chapter_id, book_id, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, created_at, updated_at)"
        " VALUES (?, ?, ?, ?)",
        (page_id, chapter_id, NOW, NOW),
    )


def _seed_binding(
    conn,
    *,
    binding_id: str,
    page_id: str,
    project_id: str,
    source_id: str,
    entry_id: str = "entry-1",
    version_id: str = "ver-1",
    generation: int = 1,
    status: str = "healthy",
    binding_version: int = 1,
) -> None:
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version, status,"
        " authorization_generation, authorized_at, verified_digest, created_at,"
        " updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            binding_id, page_id, project_id, binding_version, source_id,
            entry_id, version_id, status, generation, NOW, "c" * 64, NOW, NOW,
        ),
    )


# --- AC-S2-1 (Core side): empty inventory + capability --------------------


def test_enumeration_empty_is_legal_and_zero_write(core, server) -> None:
    before = _snapshot(core.conn)
    response = _dispatch(server, "source_list_scan_targets", {})
    assert response["error"] is None
    assert response["result"] == {"targets": []}
    assert _snapshot(core.conn) == before

    ping = _dispatch(server, "core.ping", {})
    capabilities = ping["result"]["capabilities"]
    assert "source.sync.enumerate/1" in capabilities
    # The other frozen capabilities stay; no 8th *Host DTO* item is implied
    # here (the ping list is the additive wire surface only).
    for name in (
        "source.sync.scan/1", "source.sync.plan/1", "source.sync.apply/1",
        "source.sync.relink/1", "source.sync.repoint/1",
        "source.sync.resync/1", "source.sync.operation/1",
    ):
        assert name in capabilities


def test_enumeration_does_not_create_plan_apply_or_journal(core, server) -> None:
    _seed_source(core.conn, "src-11111111-1111-1111-1111-111111111111")
    _seed_location(core.conn, "src-11111111-1111-1111-1111-111111111111")
    with core.conn:
        pass
    before = _snapshot(core.conn)
    _enumerate(server)
    assert _snapshot(core.conn) == before
    assert core.conn.execute("SELECT COUNT(*) FROM source_sync_plans").fetchone()[0] == 0
    assert core.conn.execute("SELECT COUNT(*) FROM source_operations").fetchone()[0] == 0


# --- AC-S2-1/3: ordering, uniqueness, identity, project_ids ----------------


def test_enumeration_is_sorted_unique_and_computes_identity(core, server) -> None:
    conn = core.conn
    source_b = "src-22222222-2222-2222-2222-222222222222"
    source_a = "src-11111111-1111-1111-1111-111111111111"
    with conn:
        _seed_source(conn, source_b)
        _seed_location(
            conn, source_b, registry_id="registry-b", generation=3,
            content_digest=DIGEST_B, volume_serial=7, file_id=8, size_bytes=99,
        )
        _seed_version_entry(conn, source_b, version_id="ver-b", entry_id="entry-b")
        _seed_book_page(conn, "book-b1", page_id="page-b1", chapter_id="ch-b1")
        _seed_binding(
            conn, binding_id="bind-b1", page_id="page-b1", project_id="book-b1",
            source_id=source_b, entry_id="entry-b", version_id="ver-b",
        )

        _seed_source(conn, source_a)
        _seed_location(conn, source_a, registry_id="registry-a", generation=2)
        _seed_version_entry(conn, source_a)
        for index in range(2):
            _seed_book_page(
                conn, f"book-a{index}", page_id=f"page-a{index}",
                chapter_id=f"ch-a{index}",
            )
            _seed_binding(
                conn, binding_id=f"bind-a{index}", page_id=f"page-a{index}",
                project_id=f"book-a{index}", source_id=source_a,
            )
        # A superseded binding must NOT contribute a project/source target.
        _seed_binding(
            conn, binding_id="bind-a-old", page_id="page-a0",
            project_id="book-a0", source_id=source_a, status="superseded",
            binding_version=2,
        )
        # Soft-deleted sources are excluded from the cold-start target set.
        _seed_source(conn, "src-33333333-3333-3333-3333-333333333333",
                     deleted=True)
        _seed_location(
            conn, "src-33333333-3333-3333-3333-333333333333",
            location_id="loc-deleted",
        )

    result = _enumerate(server)
    targets = result["targets"]
    # Discriminator: removing the sort would return insertion order (b then a).
    assert [t["source_id"] for t in targets] == [source_a, source_b]
    assert len({t["source_id"] for t in targets}) == len(targets)

    target_a, target_b = targets
    assert set(target_a) == {
        "source_id", "registry_id", "generation", "source_kind",
        "identity_digest", "project_ids",
    }
    assert target_a["registry_id"] == "registry-a"
    assert target_a["generation"] == 2
    assert target_a["source_kind"] == "folder"
    assert target_a["project_ids"] == ["book-a0", "book-a1"]
    assert target_a["identity_digest"] == identity_digest_of(
        DIGEST_A, 1, 2, 10
    )
    assert target_b["registry_id"] == "registry-b"
    assert target_b["generation"] == 3
    assert target_b["identity_digest"] == identity_digest_of(
        DIGEST_B, 7, 8, 99
    )
    # Deterministic across calls; no cached/fabricated identity.
    assert _enumerate(server) == result


def test_identity_and_facts_are_recomputed_from_current_location(core, server) -> None:
    conn = core.conn
    source_id = "src-44444444-4444-4444-4444-444444444444"
    with conn:
        _seed_source(conn, source_id)
        _seed_location(conn, source_id, generation=1)
        _seed_version_entry(conn, source_id)
        _seed_book_page(conn, "book-identity", page_id="page-identity",
                        chapter_id="ch-identity")
        _seed_binding(
            conn, binding_id="bind-identity", page_id="page-identity",
            project_id="book-identity", source_id=source_id,
        )
    first = _enumerate(server)["targets"][0]
    assert first["generation"] == 1
    assert first["identity_digest"] == identity_digest_of(DIGEST_A, 1, 2, 10)

    # Discriminator: a cached/hard-coded identity or generation cannot follow
    # the current-location facts.
    with conn:
        conn.execute(
            "UPDATE source_locations SET authorization_generation = 5,"
            " content_digest = ?, volume_serial = 7, file_id = 8, size_bytes = 99"
            " WHERE source_id = ? AND is_current = 1",
            (DIGEST_B, source_id),
        )
    second = _enumerate(server)["targets"][0]
    assert second["generation"] == 5
    assert second["identity_digest"] == identity_digest_of(
        DIGEST_B, 7, 8, 99
    )
    assert second["identity_digest"] != first["identity_digest"]


# --- AC-S2-1/§5.1 closed shape -------------------------------------------


def test_enumeration_closed_shape_rejects_unknown_keys(core, server) -> None:
    before = _snapshot(core.conn)
    for payload in ({"source_id": "x"}, {"bookIds": []}, {"": None}):
        response = _dispatch(server, "source_list_scan_targets", payload)
        assert response["result"] is None
        assert response["error"]["code"] == "INVALID_REQUEST"
        assert response["error"]["category"] == "validation"
        assert response["error"]["retryable"] is False
    # Non-object payloads are rejected by the app-face guard too.
    for payload in ([], None, "x"):
        response = _dispatch(server, "source_list_scan_targets", payload)
        assert response["error"]["code"] == "INVALID_REQUEST"
    assert _snapshot(core.conn) == before


# --- AC-S2-1/§5.1 typed skips (no fabrication, no truncation) --------------


def test_typed_skips_missing_facts_unknown_kind_and_project_limit(
    core, server, capsys,
) -> None:
    conn = core.conn
    ok_source = "src-66666666-6666-6666-6666-666666666666"
    missing_source = "src-55555555-5555-5555-5555-555555555555"
    unknown_source = "src-77777777-7777-7777-7777-777777777777"
    shared_source = "src-88888888-8888-8888-8888-888888888888"
    empty_project_source = "src-99999999-9999-9999-9999-999999999999"
    with conn:
        # (1) no current location facts at all -> typed skip, never fabricated.
        _seed_source(conn, missing_source)
        # (2) unknown source_kind: the schema CHECK normally forbids it, but a
        # widened/future kind must fail closed instead of being guessed.
        conn.execute("PRAGMA ignore_check_constraints = ON")
        try:
            _seed_source(conn, unknown_source, kind="future-kind")
        finally:
            conn.execute("PRAGMA ignore_check_constraints = OFF")
        _seed_location(conn, unknown_source)
        # (3) shared source across 21 projects -> typed skip (never truncate).
        _seed_source(conn, shared_source)
        _seed_location(conn, shared_source, registry_id="registry-shared")
        _seed_version_entry(conn, shared_source, version_id="ver-shared",
                            entry_id="entry-shared")
        for index in range(21):
            book_id = f"book-shared-{index:02d}"
            _seed_book_page(conn, book_id, page_id=f"page-shared-{index:02d}",
                            chapter_id=f"ch-shared-{index:02d}")
            _seed_binding(
                conn, binding_id=f"bind-shared-{index:02d}",
                page_id=f"page-shared-{index:02d}",
                project_id=book_id, source_id=shared_source,
                entry_id="entry-shared", version_id="ver-shared",
            )
        # (4) a source with no live binding: project_ids would be [] -> skip
        # (C-17 §5 requires 1..20; r2 P2-2: never a healthy empty target).
        _seed_source(conn, empty_project_source)
        _seed_location(conn, empty_project_source,
                       registry_id="registry-empty")
        # (5) a healthy bound source that must still be returned.
        _seed_source(conn, ok_source)
        _seed_location(conn, ok_source, registry_id="registry-ok")
        _seed_version_entry(conn, ok_source, version_id="ver-ok",
                            entry_id="entry-ok")
        _seed_book_page(conn, "book-ok", page_id="page-ok",
                        chapter_id="ch-ok")
        _seed_binding(
            conn, binding_id="bind-ok", page_id="page-ok",
            project_id="book-ok", source_id=ok_source,
            entry_id="entry-ok", version_id="ver-ok",
        )

    result = _enumerate(server)
    targets = result["targets"]
    assert [t["source_id"] for t in targets] == [ok_source]
    assert targets[0]["project_ids"] == ["book-ok"]
    stderr = capsys.readouterr().err
    assert "missing_location_facts=1" in stderr
    assert "unknown_source_kind=1" in stderr
    assert "project_ids_empty=1" in stderr
    assert "project_ids_over_limit=1" in stderr
    # The skipped targets are absent without being replaced by a current/guess.
    for skipped_source in (
        shared_source, unknown_source, empty_project_source,
    ):
        assert all(t["source_id"] != skipped_source for t in targets)
    # Contract invariant: every returned ScanTarget has 1..20 project_ids.
    assert all(1 <= len(t["project_ids"]) <= 20 for t in targets)


# --- r2 P2-2: project_ids 1..20; an unbound source is a typed skip ---------


def test_source_without_bindings_is_typed_skipped(core, server, capsys) -> None:
    """C-17 v1.1 §5/§5.2: ``project_ids`` is 1..20 — a source with an empty
    (deduped) project set must not appear as a healthy target with ``[]``.

    Discriminator: deleting the empty-project skip makes the unbound source
    reappear with ``project_ids: []`` and this test goes red.
    """
    conn = core.conn
    bound_source = "src-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    unbound_source = "src-bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    with conn:
        for source_id in (bound_source, unbound_source):
            _seed_source(conn, source_id)
            _seed_location(conn, source_id, registry_id=f"registry-{source_id}")
        _seed_version_entry(conn, bound_source)
        _seed_book_page(conn, "book-bound", page_id="page-bound",
                        chapter_id="ch-bound")
        _seed_binding(
            conn, binding_id="bind-bound", page_id="page-bound",
            project_id="book-bound", source_id=bound_source,
        )

    result = _enumerate(server)
    targets = result["targets"]
    # The bound source is still enumerated; the unbound one is absent.
    assert [t["source_id"] for t in targets] == [bound_source]
    assert targets[0]["project_ids"] == ["book-bound"]
    assert all(t["project_ids"] for t in targets)
    stderr = capsys.readouterr().err
    assert "project_ids_empty=1" in stderr


# --- AC-S2-1/§5.3 budget: typed error, never silent truncation -------------


class _FakeStore:
    def __init__(self, candidates: list[dict]) -> None:
        self._candidates = candidates

    def list_scan_target_candidates(self) -> list[dict]:
        return list(self._candidates)


def _candidate(
    source_id: str, *, registry_id: str = "reg",
    project_ids: list[str] | None = None,
) -> dict:
    return {
        "source_id": source_id,
        "source_kind": "folder",
        "registry_id": registry_id,
        "generation": 1,
        "content_digest": DIGEST_A,
        "volume_serial": 1,
        "file_id": 2,
        "size_bytes": 10,
        "project_ids": ["book-x"] if project_ids is None else list(project_ids),
    }


def test_budget_limits_are_typed_and_never_truncate() -> None:
    # Target-count cap (10000): 10001 candidates -> typed error, no partial DTO.
    many = [_candidate(f"src-{index:05d}") for index in range(10001)]
    with pytest.raises(SourceSyncError) as count_error:
        list_scan_targets(_FakeStore(many))
    assert count_error.value.code == "SOURCE_BUDGET_EXCEEDED"
    assert count_error.value.category == "validation"
    assert count_error.value.retryable is False

    # Byte budget: a small override proves the 8MiB guard is wired.
    small = [_candidate("src-1", registry_id="r" * 200)]
    with pytest.raises(SourceSyncError) as bytes_error:
        list_scan_targets(_FakeStore(small), max_bytes=10)
    assert bytes_error.value.code == "SOURCE_BUDGET_EXCEEDED"


def test_duplicate_candidates_are_deduped_and_sorted() -> None:
    """Discriminator for the dedupe/sort guards (fake store, no DB)."""
    candidates = [
        _candidate("src-b"),
        _candidate("src-a"),
        _candidate("src-b", registry_id="duplicate"),
    ]
    result = list_scan_targets(_FakeStore(candidates))
    assert [t["source_id"] for t in result["targets"]] == ["src-a", "src-b"]
    # First occurrence wins; the duplicate row never adds a second target.
    assert result["targets"][1]["registry_id"] == "reg"
