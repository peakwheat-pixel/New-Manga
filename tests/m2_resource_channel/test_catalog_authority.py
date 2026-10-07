"""RC2-AC1: Core/SQLite catalog authority and bridge denial matrix (F-03).

The WebView/host control surface must not be able to name OS paths, extend
reference lifetimes, or fabricate catalog state. These tests pin the denial
side of the allow/deny matrix at the Python Core boundary:

- catalog writes are validated (servable scope class, rel-path gate);
- bridge ``issue`` resolves paths only from the catalog store -- a
  ``rel_path``/``scope_class`` request parameter is a typed refusal;
- an uncataloged resource id is ``RESOURCE_NOT_CATALOGED`` (fail-closed);
- a ``ttl_seconds`` override can only shorten a grant (0/negative and
  above-default values are refused), so no caller can extend a lifetime.
"""

from __future__ import annotations

import io

import pytest

from application.resource_channel import TypedResourceChannelError
from application.resource_channel.dto import DEFAULT_TTL_SECONDS
from infrastructure.resource_channel.catalog_store import (
    ResourceCatalogStore,
    initialize_namespace,
)
from infrastructure.resource_channel.host_bridge import CoreChannelServer
from infrastructure.resource_channel.scope import ScopeRoots

from conftest import issue_for


@pytest.fixture()
def catalog() -> ResourceCatalogStore:
    return ResourceCatalogStore(":memory:")


@pytest.fixture()
def seeded_server(scope, service, catalog):
    catalog.upsert("res-001", "derived-read-only", "asset.png")

    def _server() -> CoreChannelServer:
        roots = ScopeRoots(derived_root=scope.derived, managed_root=scope.managed)
        return CoreChannelServer(
            service=service, roots=roots, catalog=catalog, stdin=io.StringIO(), stdout=io.StringIO()
        )

    return _server


class TestCatalogStoreValidation:
    def test_upsert_lookup_remove_roundtrip(self, catalog, tmp_path):
        assert catalog.count() == 0
        catalog.upsert("res-x", "derived-read-only", "pages/page-002.png")
        entry = catalog.lookup("res-x")
        assert entry == ("res-x", "derived-read-only", "pages/page-002.png")
        assert catalog.count() == 1
        # upsert replaces the mapping: the catalog row is authoritative state
        catalog.upsert("res-x", "managed-read-only", "asset.png")
        assert catalog.lookup("res-x") == ("res-x", "managed-read-only", "asset.png")
        assert catalog.count() == 1
        assert catalog.remove("res-x") is True
        assert catalog.lookup("res-x") is None
        assert catalog.remove("res-x") is False

    def test_persists_across_connections(self, tmp_path):
        # M2-DERIVED-GC-2 (R4-A1): the file-backed fixture first binds its
        # own fresh derived root; the second store then opens through the
        # bound-namespace shared path.
        db = tmp_path / "catalog.sqlite"
        derived = tmp_path / "derived"
        derived.mkdir()
        initialize_namespace(db, derived)
        first = ResourceCatalogStore(db)
        first.upsert("res-disk", "derived-read-only", "asset.png")
        first.close()
        second = ResourceCatalogStore(db)
        try:
            assert second.lookup("res-disk") == ("res-disk", "derived-read-only", "asset.png")
        finally:
            second.close()

    def test_user_source_scope_refused_at_write(self, catalog):
        with pytest.raises(TypedResourceChannelError) as excinfo:
            catalog.upsert("res-user", "user-source", "whatever.png")
        assert excinfo.value.code == "REF_SCOPE_DENIED"
        assert catalog.lookup("res-user") is None

    def test_traversal_rel_path_refused_at_write(self, catalog):
        for bad in ("../outside_secret.png", "a/../../b.png", "C:/win/secret.png", "\\\\srv\\share", ""):
            with pytest.raises(TypedResourceChannelError) as excinfo:
                catalog.upsert("res-bad", "derived-read-only", bad)
            assert excinfo.value.code == "REF_MALFORMED", bad
        assert catalog.count() == 0

    def test_empty_resource_id_refused_at_write(self, catalog):
        with pytest.raises(TypedResourceChannelError) as excinfo:
            catalog.upsert("", "derived-read-only", "asset.png")
        assert excinfo.value.code == "REF_MALFORMED"


class TestBridgeIssueDenialMatrix:
    def test_issue_resolves_path_from_catalog(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
        }})
        assert "error" not in response
        opaque = response["result"]["id"]
        resolved = server._dispatch({"id": 2, "method": "resolve", "params": {"id": opaque}})
        assert resolved["result"]["rel_path"] == "asset.png"
        assert resolved["result"]["scope_class"] == "derived-read-only"

    def test_issue_unknown_resource_fail_closed(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-never-cataloged", "revision_fingerprint": "rev-1",
        }})
        assert response["error"]["code"] == "RESOURCE_NOT_CATALOGED"

    def test_issue_with_rel_path_param_refused(self, scope, service, seeded_server):
        """The host may not name paths: a smuggled rel_path is a typed refusal
        even when the value matches a legitimate catalog row."""

        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "rel_path": "asset.png",
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_issue_with_traversal_rel_path_param_refused(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "rel_path": "../../outside/outside_secret.png",
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_issue_with_scope_class_param_refused(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "scope_class": "user-source",
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_fail_closed_without_catalog_source(self, scope, service):
        roots = ScopeRoots(derived_root=scope.derived, managed_root=scope.managed)
        server = CoreChannelServer(
            service=service, roots=roots, stdin=io.StringIO(), stdout=io.StringIO()
        )
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
        }})
        assert response["error"]["code"] == "RESOURCE_NOT_CATALOGED"
        # the bridge itself stays responsive for control operations
        assert server._dispatch({"id": 2, "method": "ping"})["result"]["pong"] is True


class TestTtlCannotBeExtended:
    def test_issue_with_default_ttl_passes(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "ttl_seconds": DEFAULT_TTL_SECONDS,
        }})
        assert "error" not in response

    def test_issue_with_probe_short_ttl_passes(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "ttl_seconds": 0.3,
        }})
        assert "error" not in response

    def test_issue_with_ttl_above_default_refused(self, scope, service, seeded_server):
        server = seeded_server()
        response = server._dispatch({"id": 1, "method": "issue", "params": {
            "resource_id": "res-001", "revision_fingerprint": "rev-1",
            "ttl_seconds": DEFAULT_TTL_SECONDS + 1,
        }})
        assert response["error"]["code"] == "REF_MALFORMED"

    def test_issue_with_non_positive_ttl_refused(self, scope, service, seeded_server):
        server = seeded_server()
        for bad in (0, -1, 0.0, -0.5):
            response = server._dispatch({"id": 1, "method": "issue", "params": {
                "resource_id": "res-001", "revision_fingerprint": "rev-1",
                "ttl_seconds": bad,
            }})
            assert response["error"]["code"] == "REF_MALFORMED", bad

    def test_service_level_ttl_extension_refused(self, reader, service, scope):
        facts = reader.capture_facts("asset.png")
        with pytest.raises(TypedResourceChannelError) as excinfo:
            service.issue(
                scope_class="derived-read-only", resource_id="res-ttl",
                revision_fingerprint="rev-1", rel_path="asset.png", facts=facts,
                ttl_seconds=DEFAULT_TTL_SECONDS * 2,
            )
        assert excinfo.value.code == "REF_MALFORMED"

    def test_service_level_non_finite_and_boolean_ttl_refused(self, reader, service, scope):
        """R2-02: NaN survives every comparison, so it must be refused
        explicitly (a NaN expiry would never fire and the entry would evade
        the active-reference limit). Booleans subclass int and must not pass
        as 1 s."""

        import math

        facts = reader.capture_facts("asset.png")
        for bad in (float("nan"), float("inf"), float("-inf"), True, False):
            with pytest.raises(TypedResourceChannelError) as excinfo:
                service.issue(
                    scope_class="derived-read-only", resource_id="res-ttl-bad",
                    revision_fingerprint="rev-1", rel_path="asset.png", facts=facts,
                    ttl_seconds=bad,
                )
            assert excinfo.value.code == "REF_MALFORMED", bad
        assert service.active_reference_count() == 0

    def test_wire_level_nan_literal_refused(self, scope, service, seeded_server):
        """R2-02 at the wire: json.loads accepts bare NaN/Infinity literals,
        so a raw bridge line could smuggle them to the service; the typed
        refusal must survive the round trip."""

        import json as json_module

        server = seeded_server()
        for literal in ("NaN", "Infinity"):
            request = json_module.loads(
                '{"id":1,"method":"issue","params":{"resource_id":"res-001",'
                f'"revision_fingerprint":"rev-1","ttl_seconds":{literal}}}}}'
            )
            response = server._dispatch(request)
            assert response["error"]["code"] == "REF_MALFORMED", literal

    def test_sliding_renewal_rearms_to_ruled_default(self, reader, scope):
        """Sliding renewal (T6, unchanged from RC1) always re-arms the ruled
        default TTL -- never a caller-chosen value and never an accumulation
        of shortened issue overrides."""

        from application.resource_channel import ResourceChannelService

        clock = {"now": 1000.0}
        service = ResourceChannelService(clock=lambda: clock["now"])
        facts = reader.capture_facts("asset.png")
        opaque = service.issue(
            scope_class="derived-read-only", resource_id="res-ttl2",
            revision_fingerprint="rev-1", rel_path="asset.png", facts=facts,
            ttl_seconds=10.0,
        )
        clock["now"] += 5.0
        service.resolve(opaque)
        # the renewal armed the DEFAULT ttl, not the shortened issue ttl:
        # the grant now survives until now + 300
        clock["now"] += 200.0
        assert service.resolve(opaque, renew=False) is not None


class TestPreviewNamespaceAuthority:
    """M2-DERIVED-GC-2 (G3): the frozen namespace bootstrap and the narrow
    first-bind initializer. Unbound = typed refusal; the initializer only
    claims a brand-new/empty self-owned catalog; a second binding on the
    same derived root is refused by the singleton row."""

    @staticmethod
    def _fresh(tmp_path, name="derived"):
        derived = tmp_path / name
        derived.mkdir(parents=True, exist_ok=True)
        return derived

    def test_unbound_file_backed_store_is_refused(self, tmp_path):
        db = tmp_path / "catalog.sqlite"
        with pytest.raises(TypedResourceChannelError) as excinfo:
            ResourceCatalogStore(db)
        assert excinfo.value.code == "REF_SCOPE_DENIED"
        assert not db.exists(), "a refused open must never create the database"

    def test_initialize_then_open_then_second_instance(self, tmp_path):
        derived = self._fresh(tmp_path)
        db = tmp_path / "catalog.sqlite"
        initialize_namespace(db, derived)
        first = ResourceCatalogStore(db)
        first.upsert("res-a", "derived-read-only", "asset.png")
        second = ResourceCatalogStore(db)
        try:
            assert second.lookup("res-a") is not None
            assert second.count() == 1
        finally:
            first.close()
            second.close()

    def test_initialize_refuses_catalog_with_rows(self, tmp_path):
        derived = self._fresh(tmp_path)
        db = tmp_path / "a.sqlite"
        initialize_namespace(db, derived)
        store = ResourceCatalogStore(db)
        store.upsert("res-1", "derived-read-only", "asset.png")
        store.close()

        other = self._fresh(tmp_path, "derived2")
        db2 = tmp_path / "b.sqlite"
        initialize_namespace(db2, other)
        store2 = ResourceCatalogStore(db2)
        store2.upsert("res-2", "derived-read-only", "asset.png")
        store2.close()
        # strip the binding to simulate a catalog with rows but no namespace
        import sqlite3 as _sq

        conn = _sq.connect(str(db2))
        conn.execute("DELETE FROM preview_namespace")
        conn.commit()
        conn.close()

        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db2, other)

    def test_initialize_refuses_legacy_schema_with_rows(self, tmp_path):
        # Codex r1 F-01: an old-schema catalog (resource_catalog WITH rows,
        # NO preview_lifecycle table) is unknown history. The two table
        # probes are independent, so the missing lifecycle table can never
        # zero out the resource count -- the bind is refused and NOTHING is
        # written (no lifecycle/namespace table may appear, row intact).
        import sqlite3 as _sq

        db = tmp_path / "legacy.sqlite"
        conn = _sq.connect(str(db))
        conn.execute(
            "CREATE TABLE resource_catalog ("
            "resource_id TEXT PRIMARY KEY, scope_class TEXT NOT NULL, rel_path TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO resource_catalog VALUES"
            " ('historic-row', 'derived-read-only', 'previews/historic-row.png')"
        )
        conn.commit()
        conn.close()

        derived = tmp_path / "derived"
        derived.mkdir()
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db, derived)

        conn = _sq.connect(str(db))
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        (count,) = conn.execute("SELECT COUNT(*) FROM resource_catalog").fetchone()
        conn.close()
        assert count == 1, "the historic row must be untouched"
        assert "preview_lifecycle" not in tables and "preview_namespace" not in tables, (
            "a refused initialization must not create any table"
        )

    def test_initialize_refuses_non_sqlite_file(self, tmp_path):
        # Unknown/corrupt database files are a refusal, never a bind.
        db = tmp_path / "garbage.sqlite"
        db.write_bytes(b"definitely not a sqlite database" * 10)
        derived = tmp_path / "derived"
        derived.mkdir()
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db, derived)

    def test_initialize_refuses_uncheckpointed_wal_rows(self, tmp_path):
        # Codex r2/r3 F-01: an immutable read can silently MISS rows sitting
        # in an un-checkpointed WAL. Here the TABLE STRUCTURE is already
        # checkpointed into the main database and ONLY THE ROW lives in the
        # WAL -- so the pre-lock immutable probe sees an adoptable EMPTY
        # table, and this test discriminates exactly the authoritative
        # WAL-visible re-check under the exclusive lock (a plain ro
        # connection). The bind is refused and nothing is written.
        import sqlite3 as _sq

        db = tmp_path / "wal.sqlite"
        conn = _sq.connect(str(db))
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            "CREATE TABLE resource_catalog ("
            "resource_id TEXT PRIMARY KEY, scope_class TEXT NOT NULL, rel_path TEXT NOT NULL)"
        )
        conn.commit()
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")  # structure -> main db
        conn.execute(
            "INSERT INTO resource_catalog VALUES"
            " ('wal-row', 'derived-read-only', 'previews/wal-row.png')"
        )
        conn.commit()  # commits INTO THE WAL; TRUNCATE keeps the main db clean
        # keep conn OPEN: without a checkpoint the row stays in the -wal file
        probe = _sq.connect("file:" + str(db).replace("\\", "/") + "?mode=ro&immutable=1", uri=True)
        try:
            (probe_count,) = probe.execute("SELECT COUNT(*) FROM resource_catalog").fetchone()
        finally:
            probe.close()
        assert probe_count == 0, (
            "test premise: the immutable probe must see an EMPTY adoptable table"
        )

        derived = tmp_path / "derived"
        derived.mkdir()
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db, derived)
        conn.close()

        # zero writes: the row survives and no binding appeared
        conn = _sq.connect(str(db))
        (count,) = conn.execute("SELECT COUNT(*) FROM resource_catalog").fetchone()
        (bound,) = conn.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='preview_namespace'"
        ).fetchone()
        conn.close()
        assert count == 1 and bound == 0

    def test_initialize_refuses_foreign_known_table_shape(self, tmp_path):
        # Codex r3 F-01: an EMPTY but foreign-shaped known table must not be
        # silently adopted by CREATE TABLE IF NOT EXISTS.
        import sqlite3 as _sq

        db = tmp_path / "foreign-shape.sqlite"
        conn = _sq.connect(str(db))
        conn.execute("CREATE TABLE resource_catalog (resource_id TEXT)")  # wrong shape
        conn.commit()
        conn.close()

        derived = tmp_path / "derived"
        derived.mkdir()
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db, derived)

        conn = _sq.connect(str(db))
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        conn.close()
        assert tables == {"resource_catalog"}, (
            "a refused initialization must not create any other table"
        )
    def test_initialize_refuses_unknown_tables(self, tmp_path):
        # Codex r2 F-01: history may live in tables this version does not
        # know -- any user table outside the known set is an unknown schema
        # and is refused even when the known tables are empty.
        import sqlite3 as _sq

        db = tmp_path / "unknown-table.sqlite"
        conn = _sq.connect(str(db))
        conn.execute("CREATE TABLE resource_catalog ("
                     "resource_id TEXT PRIMARY KEY, scope_class TEXT NOT NULL, rel_path TEXT NOT NULL)")
        conn.execute("CREATE TABLE some_legacy_widget (id TEXT PRIMARY KEY, payload TEXT)")
        conn.execute("INSERT INTO some_legacy_widget VALUES ('w1', 'historic')")
        conn.commit()
        conn.close()

        derived = tmp_path / "derived"
        derived.mkdir()
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db, derived)

    def test_production_core_refuses_unbound_legacy_catalog(self, tmp_path):
        # Codex r2 F-03: the production main() must FAIL CLOSED on an
        # existing but unbound (legacy) catalog -- non-zero exit, no binding
        # written, no silent migration. Real subprocess, real main().
        import os as _os
        import sqlite3 as _sq
        import subprocess as _sp
        import sys as _sys

        from pathlib import Path as _Path

        src_root = _Path(__file__).resolve().parents[2] / "src"
        root = tmp_path / "data"
        (root / "catalog").mkdir(parents=True)
        derived = tmp_path / "derived"
        derived.mkdir()
        catalog_db = root / "catalog" / "catalog.sqlite"
        conn = _sq.connect(str(catalog_db))
        conn.execute(
            "CREATE TABLE resource_catalog ("
            "resource_id TEXT PRIMARY KEY, scope_class TEXT NOT NULL, rel_path TEXT NOT NULL)"
        )
        conn.execute(
            "INSERT INTO resource_catalog VALUES"
            " ('historic', 'derived-read-only', 'previews/historic.png')"
        )
        conn.commit()
        conn.close()

        env = dict(_os.environ)
        env["PYTHONPATH"] = str(src_root)
        env["NEWMANGA_DATA_ROOT"] = str(root)
        env["M2RC1_DERIVED_ROOT"] = str(derived)
        env["M2RC2_CATALOG_DB"] = str(catalog_db)
        completed = _sp.run(
            [_sys.executable, "-m", "bootstrap.core_service"],
            cwd=src_root.parents[1],
            env=env,
            input="",
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        assert completed.returncode != 0, "an unbound legacy catalog must fail closed"
        assert "namespace" in completed.stderr.lower()
        conn = _sq.connect(str(catalog_db))
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        (count,) = conn.execute("SELECT COUNT(*) FROM resource_catalog").fetchone()
        conn.close()
        assert count == 1 and "preview_namespace" not in tables, (
            "the refusal must not migrate, bind or rewrite the legacy catalog"
        )

    def test_initialize_refuses_same_columns_without_primary_key(self, tmp_path):
        # Codex r4 F-01: identical column NAMES but no PRIMARY KEY is still a
        # foreign table -- the runtime leans on the keys (upsert's
        # ON CONFLICT(resource_id), the singleton namespace row), so the
        # key-less look-alike is refused and nothing is written.
        import sqlite3 as _sq

        db = tmp_path / "no-pk.sqlite"
        conn = _sq.connect(str(db))
        conn.execute(
            "CREATE TABLE resource_catalog ("
            "resource_id TEXT, scope_class TEXT, rel_path TEXT)"
        )
        conn.commit()
        conn.close()

        derived = tmp_path / "derived"
        derived.mkdir()
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(db, derived)

        conn = _sq.connect(str(db))
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        conn.close()
        assert tables == {"resource_catalog"}, (
            "a refused initialization must not create any other table"
        )

    def test_second_binding_on_same_derived_is_refused(self, tmp_path):
        derived = self._fresh(tmp_path)
        first_db = tmp_path / "first.sqlite"
        initialize_namespace(first_db, derived)

        second_db = tmp_path / "second.sqlite"
        with pytest.raises(TypedResourceChannelError):
            initialize_namespace(second_db, derived)
        # the refused attempt leaves no half-bound catalog behind
        import sqlite3 as _sq

        conn = _sq.connect(str(second_db))
        try:
            (count,) = conn.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            ).fetchone()
        except _sq.Error:
            count = 0
        conn.close()
        assert count == 0, "a refused initialization must not create a half-bound catalog"

    def test_bootstrap_refuses_hint_binding_change(self, tmp_path):
        # G3 bootstrap discrimination: the immutable read-only hint locates
        # the derived root; a lock whose CONTENT no longer matches the
        # hinted catalog identity must refuse business access (never guess).
        from infrastructure.resource_channel.handle_resolver import (
            PREVIEW_NAMESPACE_LOCK_NAME,
        )

        derived = self._fresh(tmp_path)
        db = tmp_path / "catalog.sqlite"
        initialize_namespace(db, derived)
        store = ResourceCatalogStore(db)
        store.close()

        import json

        other_derived = self._fresh(tmp_path, "derived-b")
        other_db = tmp_path / "catalog-b.sqlite"
        initialize_namespace(other_db, other_derived)
        forged = json.loads(
            (other_derived / PREVIEW_NAMESPACE_LOCK_NAME).read_text(encoding="utf-8")
        )
        # overwrite derived-a's lock with derived-b's binding: the lock's
        # own catalog-identity check must refuse the business open
        (derived / PREVIEW_NAMESPACE_LOCK_NAME).write_text(
            json.dumps(forged), encoding="utf-8"
        )
        with pytest.raises(TypedResourceChannelError):
            ResourceCatalogStore(db)


class TestLifecycleWrites:
    """M2-DERIVED-GC-2 (G1/G2): the lifecycle table is Core-minted only,
    loader writes invalidate eligibility, and the channel mark is a
    zero-busy independent connection."""

    @staticmethod
    def _bound(tmp_path):
        derived = tmp_path / "derived"
        derived.mkdir(parents=True, exist_ok=True)
        db = tmp_path / "catalog.sqlite"
        initialize_namespace(db, derived)
        return ResourceCatalogStore(db), derived

    @staticmethod
    def _origin(producer_root):
        from infrastructure.resource_channel.catalog_store import PreviewOrigin

        return PreviewOrigin(
            producer_root=str(producer_root),
            artifact_id="artifact-1",
            artifact_revision_id="revision-1",
            managed_rel_path="books/b/chapters/c/translated/r1.png",
        )

    def test_register_origin_and_mark_roundtrip(self, tmp_path):
        store, _ = self._bound(tmp_path)
        store.register_preview_with_origin(
            "preview-1", "previews/preview-1.png", self._origin(tmp_path / "data")
        )
        row = store.preview_lifecycle_row("preview-1")
        assert row is not None and row["retired"] is False
        assert store.mark_preview_retired("preview-1") is True
        assert store.preview_lifecycle_row("preview-1")["retired"] is True
        store.close()

    def test_mark_is_noop_for_unknown_or_retargeted_keys(self, tmp_path):
        store, _ = self._bound(tmp_path)
        assert store.mark_preview_retired("preview-unknown") is False
        store.register_preview_with_origin(
            "preview-1", "previews/preview-1.png", self._origin(tmp_path / "data")
        )
        assert store.mark_preview_retired("preview-1") is True
        # second mark: already retired, rowcount 0
        assert store.mark_preview_retired("preview-1") is False
        store.close()

    def test_loader_upsert_invalidates_origin_eligibility(self, tmp_path):
        # design 2.3: a re-bound row must not inherit the old origin (or
        # its retired flag) -- even if the path later matches again.
        store, _ = self._bound(tmp_path)
        store.register_preview_with_origin(
            "preview-1", "previews/preview-1.png", self._origin(tmp_path / "data")
        )
        store.mark_preview_retired("preview-1")
        store.upsert("preview-1", "derived-read-only", "previews/preview-1.png")
        assert store.preview_lifecycle_row("preview-1") is None
        assert store.retired_preview_candidates(str(tmp_path / "data")) == []
        store.close()

    def test_loader_remove_clears_origin_row(self, tmp_path):
        store, _ = self._bound(tmp_path)
        store.register_preview_with_origin(
            "preview-1", "previews/preview-1.png", self._origin(tmp_path / "data")
        )
        store.remove("preview-1")
        assert store.preview_lifecycle_row("preview-1") is None
        store.close()

    def test_retired_candidates_shape_gate(self, tmp_path):
        store, _ = self._bound(tmp_path)
        producer_root = str(tmp_path / "data")
        # correct shape
        store.register_preview_with_origin(
            "preview-ok", "previews/preview-ok.png", self._origin(producer_root)
        )
        store.mark_preview_retired("preview-ok")
        # wrong rel_path shape (catalog row not previews/<id>.png)
        store._connection.execute(
            "INSERT INTO preview_lifecycle (resource_id, producer_root, artifact_id,"
            " artifact_revision_id, managed_rel_path, retired)"
            " VALUES ('preview-shape', ?, 'a', 'r', 'books/x.png', 1)",
            (producer_root,),
        )
        store._connection.execute(
            "INSERT INTO resource_catalog (resource_id, scope_class, rel_path)"
            " VALUES ('preview-shape', 'derived-read-only', 'previews/other-name.png')"
        )
        store._connection.commit()
        # unretired origin row
        store.register_preview_with_origin(
            "preview-live", "previews/preview-live.png", self._origin(producer_root)
        )

        candidates = store.retired_preview_candidates(producer_root)
        assert [c.resource_id for c in candidates] == ["preview-ok"]

    def test_mark_uses_zero_busy_independent_connection(self, tmp_path):
        # G2 (Codex r1 F-04): the discriminating evidence for busy_timeout=0
        # is the SQLITE_BUSY failure ITSELF -- with timeout=0 a contended
        # BEGIN IMMEDIATE fails immediately with "database is locked"
        # (OperationalError); the default 5 s wait would instead succeed
        # after blocking. The elapsed bound is a coarse backstop, not the
        # zero-wait proof.
        import sqlite3 as _sq
        import time as _time

        store, _ = self._bound(tmp_path)
        db_path = store._db_path
        store.register_preview_with_origin(
            "preview-1", "previews/preview-1.png", self._origin(tmp_path / "data")
        )
        blocker = _sq.connect(str(db_path), timeout=5)
        try:
            blocker.execute("BEGIN IMMEDIATE")
            started = _time.monotonic()
            with pytest.raises(_sq.OperationalError, match="locked|busy"):
                store.mark_preview_retired("preview-1")
            elapsed = _time.monotonic() - started
        finally:
            blocker.rollback()
            blocker.close()
        assert elapsed < 1.0, (
            f"a timeout=0 mark must fail immediately, not wait (took {elapsed:.2f}s)"
        )
        assert store.preview_lifecycle_row("preview-1")["retired"] is False
        store.close()

    def test_metadata_reclaim_only_touches_lifecycle_rows(self, tmp_path):
        store, _ = self._bound(tmp_path)
        store.register_preview_with_origin(
            "preview-1", "previews/preview-1.png", self._origin(tmp_path / "data")
        )
        store._connection.execute(
            "DELETE FROM resource_catalog WHERE resource_id = 'preview-1'"
        )
        store._connection.commit()
        assert store.reclaim_orphan_lifecycle_rows() == 1
        assert store.reclaim_orphan_lifecycle_rows() == 0
        assert store.count() == 0
        store.close()
