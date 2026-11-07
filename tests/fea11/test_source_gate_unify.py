"""FEA-11-L-R11-GATE-UNIFY-1 evidence: ONE Core publication-gate predicate.

L-R11: ``core_assembly.read_gate`` (Run target admission / commit guard /
provider) and ``core_service._assert_source_sync_gate`` (resolve/reader) used
to answer the C-17 §3.3 publication-gate question with two different rules:

* ``read_gate`` treated EVERY current binding without a publication row as
  ``open`` (so a new sync chain with a missing row was admitted), and
* the resolve face only checked ONE hop of ``previous_binding_id`` (so a
  two-hop damaged chain ``B3(no row) -> B2(no row) -> B1(row)`` was admitted
  by BOTH faces).

This module proves the unified predicate:

* one judgement lives in ``source_sync.SourceSyncStore.publication_gate_of_page``
  (four states: ``open`` / ``pending`` / ``unavailable`` / ``corrupt_chain``);
* ``core_assembly.read_gate`` and ``core_service._assert_source_sync_gate``
  both consume it (static + behavioural assertions, no second one-hop copy);
* legacy v7 bindings whose WHOLE previous chain never published stay ``open``
  (C-16 v1.7 §2.4; a previous link alone is NOT sync evidence);
* a new sync chain missing its publication row fails closed on every read
  face (Run target / commit guard / provider / resolve / reader /
  ``AuthorizeSourceReadForRun``), mapped onto the EXISTING error families;
* a two-hop chain fails closed exactly like the one-hop shape.

Every fixture is REAL: the production migration runner (a genuine v7 database
upgraded to v8 for the legacy case), real zip + PNG bytes, real HMAC-signed
grants and the REAL ``assemble_core_services`` / ``CoreServiceServer``. No fake
gate reader or stub image source is used to prove any of it.
"""

from __future__ import annotations

import hashlib
import inspect
import io
import sqlite3
from pathlib import Path

import pytest

from application.importing.referenced import reader as referenced_reader
from application.importing.referenced import resolve as resolve_module
from application.importing.referenced.errors import SourceImportError
from bootstrap import core_assembly
from bootstrap.core_service import CoreServiceServer
from domain.tasks.models import (
    CommandType,
    PipelineError,
    PipelineScope,
    ScopeType,
)
from infrastructure.sqlite import source_sync as source_sync_module
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from ports.providers.errors import ProviderInputError
from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    file_facts,
    mint_grant,
    write_zip,
)
from tests.fea11.test_source_rendition_gates import (
    _assemble,
    _handler_bound,
    _insert_publication,
)
from tests.fea11.test_source_rendition_source import NEW_B, OLD_A, png_of
from tests.fea11.test_source_run_grant import (
    _authorize,
    _bindings,
    _grant_payload,
    _open,
    _register,
    _table_snapshot,
)

MIGRATIONS = default_migrations()
V7 = MIGRATIONS[:7]

#: The honest legacy row shape: a v7 database seeded BEFORE the v8 migration.
LEGACY = "legacy"
#: The v8 seed used by the damage cases.
CURRENT = "current"


# ---------------------------------------------------------------------------
# real seeds (production migrations + real zip/PNG + real DB rows)
# ---------------------------------------------------------------------------


def _new_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _seed_books(conn: sqlite3.Connection) -> None:
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


def _seed_source(conn: sqlite3.Connection, root: Path, shape: str) -> dict:
    """sources + current location + one version + two entries over a real zip.

    ``shape=LEGACY`` writes the honest v7 evidence (pixel/orientation NULL);
    ``shape=CURRENT`` writes the v8-native evidence. The grant/authorization
    path needs the REAL container identity, so ``source_locations`` carries the
    true file facts (run-grant precedent: no path fallback, no hand-guessed
    identity).
    """
    old_png = png_of(OLD_A)
    current_png = png_of(NEW_B)
    old_digest = hashlib.sha256(old_png).hexdigest()
    current_digest = hashlib.sha256(current_png).hexdigest()
    archive = write_zip(
        root / "source.zip",
        [("001-old.png", old_png), ("002-current.png", current_png)],
    )
    facts = file_facts(archive)
    add_source_tree(
        conn,
        source_id="s1",
        version_id="sv1",
        digest=facts["sha256"],
        entries=[
            ("se1", "001-old.png", old_digest),
            ("se2", "002-current.png", current_digest),
        ],
        volume_serial=facts["volume_serial"],
        file_id=facts["file_id"],
        legacy_v7_evidence=shape == LEGACY,
    )
    conn.execute(
        "UPDATE source_locations SET size_bytes = ? WHERE source_id = 's1'",
        (facts["size"],),
    )
    conn.commit()
    return {
        "archive": archive,
        "facts": facts,
        "old_digest": old_digest,
        "current_digest": current_digest,
    }


def _seed_v7_legacy_library(db_path: Path, root: Path) -> dict:
    """A REAL v7 database with two legacy binding shapes, then upgraded to v8.

    * ``p1``: healthy binding, ``previous_binding_id IS NULL``, no publication
      (the pre-v8 / C-16-imported shape).
    * ``p2``: a two-generation chain whose WHOLE chain never published. The
      previous link alone is NOT sync evidence, so this is still legacy and
      must stay ``open``.
    """
    conn = _new_db(db_path)
    MigrationRunner(conn, V7).apply_pending()
    _seed_books(conn)
    facts = _seed_source(conn, root, LEGACY)
    add_referenced_page(
        conn,
        "p1",
        "c1",
        "b1",
        order=1,
        source_id="s1",
        version_id="sv1",
        entry_id="se1",
        digest=facts["old_digest"],
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
        digest=facts["current_digest"],
        width=NEW_B["width"],
        height=NEW_B["height"],
    )
    conn.execute(
        "UPDATE page_bindings SET status = 'superseded' WHERE binding_id = 'pb-p2'"
    )
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, previous_binding_id, authorization_generation,"
        " authorized_at, verified_digest, created_at, updated_at)"
        " VALUES ('pb-p2-b2', 'p2', 'b1', 2, 's1', 'se2', 'sv1', 'healthy',"
        " 'pb-p2', 1, ?, ?, ?, ?)",
        (NOW, facts["current_digest"], NOW, NOW),
    )
    conn.commit()
    applied = MigrationRunner(conn, MIGRATIONS).apply_pending()
    assert [record.schema_version for record in applied] == [8, 9]
    conn.close()
    return facts


def _seed_v8_library(db_path: Path, root: Path, *, page_ids=("p2",)) -> dict:
    """A real v8 library with the named referenced page(s) over one real zip."""
    conn = _new_db(db_path)
    MigrationRunner(conn, MIGRATIONS).apply_pending()
    _seed_books(conn)
    facts = _seed_source(conn, root, CURRENT)
    for order, page_id in enumerate(page_ids, start=1):
        add_referenced_page(
            conn,
            page_id,
            "c1",
            "b1",
            order=order,
            source_id="s1",
            version_id="sv1",
            entry_id="se2",
            digest=facts["current_digest"],
            width=NEW_B["width"],
            height=NEW_B["height"],
        )
    conn.close()
    return facts


def _add_unnamed_generation(
    conn: sqlite3.Connection,
    *,
    page_id: str,
    binding_id: str,
    binding_version: int,
    previous_binding_id: str,
    status: str,
    digest: str,
) -> None:
    """A real binding generation WITHOUT a publication row (the damage)."""
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, previous_binding_id, authorization_generation,"
        " authorized_at, verified_digest, created_at, updated_at)"
        " VALUES (?, ?, 'b1', ?, 's1', 'se2', 'sv1', ?, ?, 1, ?, ?, ?, ?)",
        (
            binding_id,
            page_id,
            binding_version,
            status,
            previous_binding_id,
            NOW,
            digest,
            NOW,
            NOW,
        ),
    )


def _seed_damaged_chain(
    conn: sqlite3.Connection, *, page_id: str, hops: int
) -> None:
    """Turn ``pb-<page>`` into a sync chain whose current binding lost its row.

    ``hops=1``: B2(cur, no row) -> B1(row).
    ``hops=2``: B3(cur, no row) -> B2(no row) -> B1(row).
    """
    base = f"pb-{page_id}"
    # B1 really published (an applied operation row + an open publication).
    _insert_publication(conn, base, "open")
    digest = conn.execute(
        "SELECT content_digest FROM source_entries"
        " WHERE version_id = 'sv1' AND entry_id = 'se2'"
    ).fetchone()["content_digest"]
    conn.execute(
        "UPDATE page_bindings SET status = 'superseded' WHERE binding_id = ?",
        (base,),
    )
    previous = base
    for index in range(2, hops + 2):
        binding_id = f"{base}-b{index}"
        is_current = index == hops + 1
        _add_unnamed_generation(
            conn,
            page_id=page_id,
            binding_id=binding_id,
            binding_version=index,
            previous_binding_id=previous,
            status="healthy" if is_current else "superseded",
            digest=digest,
        )
        previous = binding_id
    conn.commit()


# ---------------------------------------------------------------------------
# real assembly + real resource publisher (production handler faces)
# ---------------------------------------------------------------------------


def _assemble_core(db_path: Path, managed_root: Path) -> object:
    managed_root.mkdir(parents=True, exist_ok=True)
    core = _assemble(db_path, managed_root)
    core.pipeline.set_scheduler_owner(True)
    return core


def _real_previews(core, root: Path):
    """The production resource publisher over a real catalog/derived root."""
    from infrastructure.resource_channel.catalog_store import (
        ResourceCatalogStore,
        initialize_namespace,
    )
    from infrastructure.resource_channel.render_preview import (
        RenderPreviewPublisher,
    )

    catalog_db = root / "catalog" / "catalog.sqlite"
    derived_root = root / "derived"
    catalog_db.parent.mkdir(parents=True, exist_ok=True)
    derived_root.mkdir(parents=True, exist_ok=True)
    initialize_namespace(catalog_db, derived_root)
    store = ResourceCatalogStore(catalog_db)
    publisher = RenderPreviewPublisher(derived_root, store)
    server = CoreServiceServer(
        core, stdin=io.StringIO(), stdout=io.StringIO(), render_previews=publisher
    )
    # ``CoreServiceServer`` re-arms the scheduler-owner requirement; this test
    # drives ``create_run`` directly (no production scheduler thread).
    core.pipeline.set_scheduler_owner(True)
    return server, publisher, store


def _bind_real_grant(core, facts: dict, *, locator: str, ordinal: int, entry_id: str) -> str:
    grant_id, _ = mint_grant(
        core.source_read_refs,
        source_id="s1",
        version="sv1",
        kind="zip",
        entries=[(str(facts["archive"]), locator, ordinal)],
    )
    core.source_read_refs.bind_imported_entry(grant_id, "s1", "sv1", entry_id)
    return grant_id


def _page_frame(core, page_id: str):
    return _handler_bound(core).__self__.deps.images.page_frame(page_id)


# ---------------------------------------------------------------------------
# AC-2: legacy v7 -> v8 zero regression
# ---------------------------------------------------------------------------


def test_legacy_v7_bindings_stay_open_on_every_face(tmp_path):
    """Real v7 DB upgraded to v8: no publication + previous NULL (or a
    previous chain that never published) is still the legacy ``open`` shape."""
    db_path = tmp_path / "core" / "library.db"
    managed_root = tmp_path / "core" / "managed"
    facts = _seed_v7_legacy_library(db_path, tmp_path / "seed")
    core = _assemble_core(db_path, managed_root)
    try:
        gate = core.pipeline._catalog.source_gate_reader
        store = core.source_sync["store"]
        # The single predicate itself: both legacy shapes are open.
        assert store.publication_gate_of_page("p1") == "open"
        assert store.publication_gate_of_page("p2") == "open"
        assert gate("p1") == "open"
        assert gate("p2") == "open"

        server, _publisher, _catalog = _real_previews(core, tmp_path / "previews")
        core_session = _open(server)
        grant = _grant_payload(facts["archive"])
        assert _register(server, core_session, grant)["error"] is None
        # Bind the wire-registered live grant (the third frozen producer) so
        # the commit guard/provider resolve succeeds for the legacy page.
        core.source_read_refs.bind_imported_entry(
            grant["grant_id"], "s1", "sv1", "se2"
        )

        # Run target admission + commit guard (pre-fix behaviour preserved).
        run = core.pipeline.create_run(
            CommandType.REOCR_ALL, PipelineScope(ScopeType.PAGE, selected_ids=("p2",))
        )
        assert [target.target_id for target in run.targets] == ["p2"]
        with core.pipeline._catalog.source_commit_guard("p2"):
            pass

        # The provider really reads the current archive member.
        frame = _page_frame(core, "p2")
        assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])

        # Resolve + AuthorizeSourceReadForRun keep working (real grant).
        resolved = server.handle_resolve_page_resource({"page_id": "p2"})
        assert resolved["resource_id"].startswith("page-rendition-v2-")
        authorized = _authorize(
            server,
            core_session,
            [grant["grant_id"]],
            scope={"kind": "page", "page_id": "p2"},
        )
        assert authorized["error"] is None, authorized["error"]
        assert authorized["result"] == {"bound_pages": 1}
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# AC-3 / AC-4: new sync chain with a missing publication row fails closed
# ---------------------------------------------------------------------------


def _assert_damage_refused(core, server, facts: dict, page_id: str, monkeypatch) -> None:
    """Every read face refuses the damaged chain with an existing family code."""
    store = core.source_sync["store"]
    gate = core.pipeline._catalog.source_gate_reader

    # The single predicate names the damage; the frozen three-state view maps
    # it onto ``unavailable`` (no new gate state leaks to consumers).
    assert store.publication_gate_of_page(page_id) == "corrupt_chain"
    assert gate(page_id) == "unavailable"

    # Run target admission: existing TARGET_NOT_FOUND family.
    with pytest.raises(PipelineError) as target:
        core.pipeline.create_run(
            CommandType.REOCR_ALL,
            PipelineScope(ScopeType.PAGE, selected_ids=(page_id,)),
        )
    assert target.value.code == "TARGET_NOT_FOUND"

    # Run commit guard: existing TARGET_NOT_FOUND family, before any grant.
    with pytest.raises(PipelineError) as guard:
        with core.pipeline._catalog.source_commit_guard(page_id):
            pytest.fail("a corrupt chain must never open the commit window")
    assert guard.value.code == "TARGET_NOT_FOUND"
    assert guard.value.detail == "source binding is unavailable"

    # Provider: typed INVALID_INPUT BEFORE any decode/read of source bytes.
    calls = {"prepare": 0, "read": 0}
    real_prepare = resolve_module.prepare_referenced_rendition
    real_read = referenced_reader.read_entry_bytes

    def spy_prepare(*args, **kwargs):
        calls["prepare"] += 1
        return real_prepare(*args, **kwargs)

    def spy_read(*args, **kwargs):
        calls["read"] += 1
        return real_read(*args, **kwargs)

    monkeypatch.setattr(resolve_module, "prepare_referenced_rendition", spy_prepare)
    monkeypatch.setattr(referenced_reader, "read_entry_bytes", spy_read)
    with pytest.raises(ProviderInputError) as provider:
        _page_frame(core, page_id)
    assert provider.value.error_code == "INVALID_INPUT"
    assert "unavailable" in provider.value.detail
    assert calls == {"prepare": 0, "read": 0}

    # Resolve face: the existing SOURCE_ACCESS_DENIED family, fixed text.
    with pytest.raises(SourceImportError) as resolved:
        server.handle_resolve_page_resource({"page_id": page_id})
    assert resolved.value.code == "SOURCE_ACCESS_DENIED"
    assert str(resolved.value) == "page binding has no read gate"

    # Reader projection: per-page resolve refuses the chapter typed.
    with pytest.raises(SourceImportError) as reader:
        server.handle_get_reader_projection(
            {
                "chapter_id": "c1",
                "mode": "original",
                "start_position": "beginning",
            }
        )
    assert reader.value.code == "SOURCE_ACCESS_DENIED"

    # AuthorizeSourceReadForRun: the whole request is refused typed through the
    # SAME injected gate, with ZERO mapping writes and ZERO business writes.
    core_session = _open(server)
    grant = _grant_payload(facts["archive"])
    assert _register(server, core_session, grant)["error"] is None
    before = _table_snapshot(core)
    refused = _authorize(
        server,
        core_session,
        [grant["grant_id"]],
        scope={"kind": "page", "page_id": page_id},
    )
    assert refused["result"] is None
    assert refused["error"]["code"] == "INVALID_REQUEST"
    assert _table_snapshot(core) == before
    assert _bindings(core.source_read_refs) == {}


def _damaged_core(tmp_path, hops: int):
    db_path = tmp_path / "core" / "library.db"
    managed_root = tmp_path / "core" / "managed"
    facts = _seed_v8_library(db_path, tmp_path / "seed")
    conn = _new_db(db_path)
    _seed_damaged_chain(conn, page_id="p2", hops=hops)
    conn.close()
    core = _assemble_core(db_path, managed_root)
    server, _publisher, _catalog = _real_previews(core, tmp_path / "previews")
    return core, server, facts


def test_one_hop_missing_publication_fails_closed_everywhere(tmp_path, monkeypatch):
    """AC-3 (L-R11): B1(published) -> B2(current, no row) is corruption."""
    core, server, facts = _damaged_core(tmp_path, hops=1)
    try:
        _assert_damage_refused(core, server, facts, "p2", monkeypatch)
    finally:
        core.conn.close()


def test_two_hop_missing_publication_fails_closed_everywhere(tmp_path, monkeypatch):
    """AC-4: B1(published) -> B2(no row) -> B3(current, no row).

    A one-hop implementation sees B2 without a row and would admit the page;
    the whole-chain walk must refuse it exactly like the one-hop shape.
    """
    core, server, facts = _damaged_core(tmp_path, hops=2)
    try:
        _assert_damage_refused(core, server, facts, "p2", monkeypatch)
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# pending/open regression on the same real assembly
# ---------------------------------------------------------------------------


def test_pending_and_open_current_publication_keep_the_frozen_states(tmp_path):
    db_path = tmp_path / "core" / "library.db"
    managed_root = tmp_path / "core" / "managed"
    facts = _seed_v8_library(db_path, tmp_path / "seed")
    core = _assemble_core(db_path, managed_root)
    try:
        store = core.source_sync["store"]
        gate = core.pipeline._catalog.source_gate_reader
        _bind_real_grant(
            core, facts, locator="002-current.png", ordinal=1, entry_id="se2"
        )

        _insert_publication(core.conn, "pb-p2", "pending")
        assert store.publication_gate_of_page("p2") == "pending"
        assert gate("p2") == "pending"
        with pytest.raises(PipelineError) as target:
            core.pipeline.create_run(
                CommandType.REOCR_ALL,
                PipelineScope(ScopeType.PAGE, selected_ids=("p2",)),
            )
        assert target.value.code == "TARGET_NOT_FOUND"
        with pytest.raises(ProviderInputError) as provider:
            _page_frame(core, "p2")
        assert provider.value.error_code == "INVALID_INPUT"

        core.conn.execute(
            "UPDATE source_binding_publications SET read_gate = 'open',"
            " opened_at = ? WHERE binding_id = 'pb-p2'",
            (NOW,),
        )
        core.conn.commit()
        assert store.publication_gate_of_page("p2") == "open"
        assert gate("p2") == "open"
        run = core.pipeline.create_run(
            CommandType.REOCR_ALL, PipelineScope(ScopeType.PAGE, selected_ids=("p2",))
        )
        assert [item.target_id for item in run.targets] == ["p2"]
        with core.pipeline._catalog.source_commit_guard("p2"):
            pass
        frame = _page_frame(core, "p2")
        assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])
    finally:
        core.conn.close()


def test_no_binding_page_stays_unavailable(tmp_path):
    """A managed/no-binding page is ``unavailable`` (unchanged pre-fix state)."""
    db_path = tmp_path / "core" / "library.db"
    managed_root = tmp_path / "core" / "managed"
    _seed_v8_library(db_path, tmp_path / "seed", page_ids=())
    core = _assemble_core(db_path, managed_root)
    try:
        store = core.source_sync["store"]
        gate = core.pipeline._catalog.source_gate_reader
        assert store.publication_gate_of_page("missing") == "unavailable"
        assert gate("missing") == "unavailable"
    finally:
        core.conn.close()


# ---------------------------------------------------------------------------
# AC-1: static uniqueness of the predicate and its delegation
# ---------------------------------------------------------------------------


def test_core_has_exactly_one_publication_gate_judgement():
    """One judgement in source_sync.py; every Core consumer delegates to it."""
    store_source = inspect.getsource(source_sync_module)
    # The ONLY publication-gate judgement...
    assert store_source.count("def _publication_gate_verdict(") == 1
    # ... exposed through the single public predicate...
    assert store_source.count("def publication_gate_of_page(") == 1
    # ... and the ONLY binding-chain walk both it and the lineage fact use.
    assert store_source.count("def _binding_chain_ids(") == 1

    assembly_source = inspect.getsource(core_assembly)
    assert assembly_source.count("def read_gate(") == 1
    assert "publication_gate_of_page(" in assembly_source
    # No second gate judgement in the assembly (no row read, no one-hop walk).
    assert "gate_of_binding(" not in assembly_source
    assert "previous_binding_id" not in assembly_source

    service_source = inspect.getsource(CoreServiceServer._assert_source_sync_gate)
    assert ".publication_gate_of_page(" in service_source
    assert "gate_of_binding(" not in service_source
    # No one-hop ``previous_binding_id`` read in the code (the docstring may
    # name the removed heuristic; the implementation must not read it).
    assert 'binding["previous_binding_id"]' not in service_source
    assert 'binding.get("previous_binding_id")' not in service_source

    plural_source = inspect.getsource(CoreServiceServer._assert_source_sync_gates)
    assert "_assert_source_sync_gate(page_id)" in plural_source
    assert "publication_gate_of_page" not in plural_source

    # ``AuthorizeSourceReadForRun`` keeps consuming the injected predicate.
    authorize_source = inspect.getsource(
        CoreServiceServer._authorize_source_read_for_run
    )
    assert 'getattr(catalog, "source_gate_reader", None)' in authorize_source
    assert "gate_reader(page_id)" in authorize_source
