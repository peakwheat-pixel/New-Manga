"""FEA-11-RENDITION-1 gate/assembly evidence (I-3, I-4, AC-R1/R4/R6/R7).

Two layers:

* the REAL production assembly (``assemble_core_services``) over a real
  file-backed v8 database proves the I-3 wiring: ONE ``read_gate`` predicate
  object feeds the Run commit guard, the provider image source AND the Run
  target catalog (identity assertions, not "something callable"), and the
  C-17 §3.3 refusal behaves typed at every one of those faces;
* a focused ``handle_detect`` test proves I-4: the guard digest is re-checked
  BEFORE ``region_creator`` runs, with zero writes on mismatch and the
  historical behaviour preserved when the dependency (or the ref) is absent.
"""

from __future__ import annotations

import inspect
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from application.importing.referenced.errors import SourceImportError
from application.translation.color.service import SourceStyleService
from application.translation.pipeline.executor import StepExecutionError
from application.tasks.store import snapshot_digest
from bootstrap import core_assembly
from bootstrap.core_assembly import (
    _ManagedPageImageSource,
    _RegionGeometrySource,
    assemble_core_services,
)
from domain.tasks.models import (
    CommandType,
    PipelineError,
    PipelineScope,
    PlanDecision,
    PlanUnit,
    ScopeType,
    StepRun,
    StepRunStatus,
)
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    STEP_DETECT,
)
from infrastructure.providers.registry import ProviderRegistry
from infrastructure.providers.retry import RetryPolicy
from infrastructure.providers.step_writes import ArtifactStepWriter, RegionStepWriter
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from ports.providers.errors import ProviderInputError
from tests.fea11.conftest import (
    NOW,
    add_referenced_page,
    add_source_tree,
    mint_grant,
    write_zip,
)
from tests.fea11.test_source_rendition_run import RecordingDetector
from tests.fea11.test_source_rendition_source import (
    NEW_B,
    OLD_A,
    build_rendition_site,
    png_of,
)


# ---------------------------------------------------------------------------
# real production assembly
# ---------------------------------------------------------------------------


class _PassthroughDecoder:
    """Injection marker only — these tests never import a page."""

    def decode(self, data: bytes):  # pragma: no cover - never called
        raise AssertionError("the rendition gate tests never import pages")


class _StubStyleAnalyzer:
    """Qt-free stand-in for the ``SourceStyleAnalyzer`` port."""

    def analyze(self, original_png: bytes, box):  # pragma: no cover
        raise AssertionError("the rendition gate tests never render")


def _assemble(db_path: Path, managed_root: Path):
    return assemble_core_services(
        db_path,
        managed_root,
        image_decoder=_PassthroughDecoder(),
        font_catalog=object(),
        layout_engine=object(),
        compositor=object(),
        source_styles=SourceStyleService(_StubStyleAnalyzer()),
    )


def _seed_library(db_path: Path, managed_root: Path, *, pages=("pr", "pm")) -> dict:
    """A v8 library with one pure referenced page and one managed page."""
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
    facts: dict = {}
    if "pr" in pages:
        zip_path = write_zip(
            db_path.parent / "current-source.zip",
            [
                ("001-old.png", png_of({"width": 20, "height": 9, "background": (225, 195, 20),
                                         "block": (1, 1, 5, 5), "block_color": (190, 20, 190)})),
                ("002-current.png", png_of(NEW_B)),
            ],
        )
        import hashlib

        current_bytes = png_of(NEW_B)
        digest = hashlib.sha256(current_bytes).hexdigest()
        add_source_tree(
            conn,
            source_id="s1",
            version_id="sv1",
            digest="a" * 64,
            entries=[("se1", "001-old.png", "c" * 64), ("se2", "002-current.png", digest)],
            legacy_v7_evidence=False,
        )
        add_referenced_page(
            conn,
            "pr",
            "c1",
            "b1",
            order=1,
            source_id="s1",
            version_id="sv1",
            entry_id="se2",
            digest=digest,
            width=NEW_B["width"],
            height=NEW_B["height"],
        )
        facts = {"zip_path": zip_path, "digest": digest}
    if "pm" in pages:
        (managed_root / "legacy").mkdir(parents=True, exist_ok=True)
        (managed_root / "legacy" / "pm.png").write_bytes(png_of(OLD_A))
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, sort_order, created_at,"
            " updated_at, source_filename, source_order, source_hash,"
            " source_size_bytes, width, height, managed_original_ref,"
            " source_mode, integrity_status)"
            " VALUES ('pm', 'c1', 2, ?, ?, 'pm.png', 2, ?, 10, ?, ?,"
            " 'legacy/pm.png', 'managed', 'complete')",
            (NOW, NOW, "b" * 64, OLD_A["width"], OLD_A["height"]),
        )
    conn.commit()
    conn.close()
    return facts


def _insert_publication(conn, binding_id: str, read_gate: str) -> None:
    """One real publication row (with the plan/operation rows its FKs demand)."""
    digest = "a" * 64
    conn.execute(
        "INSERT INTO source_sync_plans (plan_id, source_id, kind, state,"
        " plan_digest, body_json, created_at, expires_at, previewed_at,"
        " confirmed_at, applied_at) VALUES ('plan-rendition-1', 's1', 'resync',"
        " 'applied', ?, '{}', ?, ?, ?, ?, ?)",
        (digest, NOW, NOW, NOW, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO source_operations (operation_id, plan_id, plan_digest,"
        " kind, request_digest, state, authorization_digest,"
        " authorization_json, host_receipt_id, commit_receipt_json,"
        " commit_digest, created_at, updated_at, committed_at)"
        " VALUES ('op-rendition-1', 'plan-rendition-1', ?, 'resync', ?,"
        " 'core-committed', ?, '{}', 'host-rendition-1', '{}', ?, ?, ?, ?)",
        (digest, digest, digest, digest, NOW, NOW, NOW),
    )
    # The frozen CHECK ties ``read_gate='open'`` to a non-NULL ``opened_at``:
    # a pending gate is exactly "the publication has not opened yet".
    opened_at = NOW if read_gate == "open" else None
    conn.execute(
        "INSERT INTO source_binding_publications (binding_id, operation_id,"
        " previous_binding_id, relation, read_gate, opened_at)"
        " VALUES (?, 'op-rendition-1', NULL, 'added', ?, ?)",
        (binding_id, read_gate, opened_at),
    )
    conn.commit()


@pytest.fixture()
def real_core(tmp_path):
    db_path = tmp_path / "core" / "library.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    managed_root = tmp_path / "core" / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    facts = _seed_library(db_path, managed_root)
    core = _assemble(db_path, managed_root)
    try:
        yield core, facts
    finally:
        core.conn.close()


def _handler_bound(core):
    """The bound ``handle_detect`` behind the production handler table."""
    wrapped = core.pipeline._executor._handlers[STEP_DETECT]
    for cell in wrapped.__closure__ or ():
        value = cell.cell_contents
        if hasattr(value, "__self__") and isinstance(value.__self__, ProductionHandlers):
            return value
    raise AssertionError("detect handler binding not found")


def test_real_assembly_wires_one_gate_object_into_every_consumer(real_core):
    core, facts = real_core
    catalog = core.pipeline._catalog
    deps = _handler_bound(core).__self__.deps

    # I-3: exactly one predicate object feeds the target gate and the provider.
    assert callable(catalog.source_gate_reader)
    assert callable(catalog.page_visibility)
    assert deps.images._read_gate is catalog.source_gate_reader
    # ... and the same grant registry the resolve face uses.
    assert deps.images._source_access is core.source_read_refs
    # I-4: the detect handler got the SAME commit-guard reader the catalog uses.
    assert deps.commit_guard is not None
    assert deps.commit_guard("pr") == catalog.guard_reader("pr")
    # The gate predicate is defined exactly once in the assembly.
    source = inspect.getsource(core_assembly)
    assert source.count("def read_gate(") == 1
    assert source.count("source_gate_reader = read_gate") == 1
    assert facts["zip_path"].exists()


def test_gate_predicate_reports_the_three_frozen_states(real_core):
    core, _facts = real_core
    gate = core.pipeline._catalog.source_gate_reader

    assert gate("pm") == "unavailable"  # no binding at all
    assert gate("nope") == "unavailable"
    assert gate("pr") == "open"  # healthy binding, no publication row yet

    _insert_publication(core.conn, "pb-pr", "pending")
    assert gate("pr") == "pending"

    core.conn.execute(
        "UPDATE source_binding_publications SET read_gate = 'open', opened_at = ?"
        " WHERE binding_id = 'pb-pr'",
        (NOW,),
    )
    core.conn.commit()
    assert gate("pr") == "open"


def test_pending_gate_blocks_the_real_run_target_and_opens_when_acknowledged(real_core):
    core, _facts = real_core
    scope = PipelineScope(ScopeType.PAGE, selected_ids=("pr",))
    _insert_publication(core.conn, "pb-pr", "pending")

    with pytest.raises(PipelineError) as pending:
        core.pipeline.create_run(CommandType.REOCR_ALL, scope)
    assert pending.value.code == "TARGET_NOT_FOUND"

    core.conn.execute(
        "UPDATE source_binding_publications SET read_gate = 'open', opened_at = ?"
        " WHERE binding_id = 'pb-pr'",
        (NOW,),
    )
    core.conn.commit()
    run = core.pipeline.create_run(CommandType.REOCR_ALL, scope)
    assert [target.target_id for target in run.targets] == ["pr"]


def test_real_run_commit_guard_refuses_pending_gate_and_missing_grant(real_core):
    core, facts = real_core
    guard = core.pipeline._catalog.source_commit_guard
    _insert_publication(core.conn, "pb-pr", "pending")

    with pytest.raises(PipelineError) as pending:
        with guard("pr"):
            pytest.fail("a pending gate must never open the commit window")
    assert pending.value.code == "TARGET_NOT_FOUND"

    core.conn.execute(
        "UPDATE source_binding_publications SET read_gate = 'open', opened_at = ?"
        " WHERE binding_id = 'pb-pr'",
        (NOW,),
    )
    core.conn.commit()
    # L-R1 evidence: with an open gate but NO live Run-scoped grant, the commit
    # guard refuses typed (the existing SourceImportError family, projected to
    # DB_FAILED by commit_step — never a crash, never a silent pass).
    with pytest.raises(SourceImportError) as no_grant:
        with guard("pr"):
            pytest.fail("a missing source-read grant must never open the commit window")
    assert no_grant.value.code == "SOURCE_ACCESS_DENIED"

    # A real minted+bound grant opens it: the wiring itself is not broken.
    mint_grant(
        core.source_read_refs,
        source_id="s1",
        version="sv1",
        kind="zip",
        entries=[(str(facts["zip_path"]), "002-current.png", 1)],
    )
    grant_id = next(iter(core.source_read_refs._grants))
    core.source_read_refs.bind_imported_entry(grant_id, "s1", "sv1", "se2")
    with guard("pr"):
        pass


def test_real_assembly_provider_reads_the_binding_rendition_end_to_end(real_core):
    core, facts = real_core
    images = _handler_bound(core).__self__.deps.images

    # Pending gate: typed refusal before any source byte is read.
    _insert_publication(core.conn, "pb-pr", "pending")
    with pytest.raises(ProviderInputError) as pending:
        images.page_frame("pr")
    assert pending.value.error_code == "INVALID_INPUT"
    assert "pending" in pending.value.detail

    core.conn.execute(
        "UPDATE source_binding_publications SET read_gate = 'open', opened_at = ?"
        " WHERE binding_id = 'pb-pr'",
        (NOW,),
    )
    core.conn.commit()
    # No grant yet: typed refusal (L-R1), still no crash.
    with pytest.raises(ProviderInputError) as no_grant:
        images.page_frame("pr")
    assert "SOURCE_ACCESS_DENIED" in no_grant.value.detail

    # Real grant over the real zip: the production image source returns B.
    grant_id, _ = mint_grant(
        core.source_read_refs,
        source_id="s1",
        version="sv1",
        kind="zip",
        entries=[(str(facts["zip_path"]), "002-current.png", 1)],
    )
    core.source_read_refs.bind_imported_entry(grant_id, "s1", "sv1", "se2")
    frame = images.page_frame("pr")
    assert (frame.width, frame.height) == (NEW_B["width"], NEW_B["height"])
    # The managed page still reads the Managed Copy (zero regression).
    managed_frame = images.page_frame("pm")
    assert (managed_frame.width, managed_frame.height) == (
        OLD_A["width"],
        OLD_A["height"],
    )


# ---------------------------------------------------------------------------
# I-4: detect re-checks the commit guard BEFORE the first Region write
# ---------------------------------------------------------------------------


def _guard_value(binding_id: str) -> dict:
    return {"binding": {"binding_id": binding_id}, "drafts": []}


def _detect_step(guard_at_attempt: dict) -> StepRun:
    return StepRun(
        step_run_id="step-1",
        task_id="task-1",
        target_id="pr",
        page_id="pr",
        region_id=None,
        step_type=STEP_DETECT,
        status=StepRunStatus.RUNNING,
        input_refs={"__fea10_guard__": snapshot_digest(guard_at_attempt)},
    )


def _detect_unit() -> PlanUnit:
    return PlanUnit(
        unit_id="task-1:pr:detect",
        task_id="task-1",
        target_id="pr",
        page_id="pr",
        region_id=None,
        step_type=STEP_DETECT,
        decision=PlanDecision.RUN,
    )


def _detect_handlers(site, *, commit_guard, created: list) -> ProductionHandlers:
    def region_creator(page_id, polygon, reading_order, provenance, provider_label=""):
        created.append((page_id, tuple(polygon), reading_order, provider_label))
        return "rg-detected"

    return ProductionHandlers(
        HandlerDependencies(
            registry=ProviderRegistry(),
            regions=site.regions,
            region_writer=RegionStepWriter(site.conn, site.regions),
            artifacts=ArtifactStepWriter(site.conn, site.storage),
            images=site.image_source(),
            geometry=_RegionGeometrySource(site.regions),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=RecordingDetector(),
            region_creator=region_creator,
            commit_guard=commit_guard,
        )
    )


def test_detect_refuses_before_any_region_write_when_the_guard_digest_differs(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    created: list = []
    guard_state = {"value": _guard_value("pb-pr")}
    handlers = _detect_handlers(site, commit_guard=lambda page_id: guard_state["value"], created=created)
    step = _detect_step(guard_state["value"])
    run = SimpleNamespace(settings_snapshot={})

    # The binding switches AFTER the step attempt recorded its guard digest.
    guard_state["value"] = _guard_value("pb-pr-b2")

    with pytest.raises(StepExecutionError) as info:
        handlers.handle_detect(step, _detect_unit(), run)

    assert info.value.code == "INPUT_REVISION_CHANGED"
    assert created == [], "zero Region may be written on a guard mismatch"


def test_detect_creates_the_region_when_the_guard_is_unchanged(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    created: list = []
    guard_state = {"value": _guard_value("pb-pr")}
    handlers = _detect_handlers(site, commit_guard=lambda page_id: guard_state["value"], created=created)

    result = handlers.handle_detect(
        _detect_step(guard_state["value"]), _detect_unit(),
        SimpleNamespace(settings_snapshot={}),
    )

    assert result.outputs["region_ids"] == ("rg-detected",)
    assert len(created) == 1


def test_detect_without_a_commit_guard_reader_keeps_the_historical_behaviour(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    created: list = []
    handlers = _detect_handlers(site, commit_guard=None, created=created)
    guard = _guard_value("pb-pr")
    step = _detect_step(guard)
    # Even though the state now differs, an un-wired dependency changes nothing.
    result = handlers.handle_detect(
        step, _detect_unit(), SimpleNamespace(settings_snapshot={})
    )
    assert result.outputs["region_ids"] == ("rg-detected",)
    assert len(created) == 1


def test_detect_without_a_recorded_guard_ref_skips_the_recheck(
    conn, book_chapter, tmp_path, registry
):
    site = build_rendition_site(
        conn, book_chapter, tmp_path, registry, managed_copy=False
    )
    created: list = []
    guard_state = {"value": _guard_value("pb-pr")}
    handlers = _detect_handlers(site, commit_guard=lambda page_id: guard_state["value"], created=created)
    step = StepRun(
        step_run_id="step-legacy",
        task_id="task-1",
        target_id="pr",
        page_id="pr",
        region_id=None,
        step_type=STEP_DETECT,
        status=StepRunStatus.RUNNING,
        input_refs={},
    )
    guard_state["value"] = _guard_value("pb-pr-b2")

    result = handlers.handle_detect(
        step, _detect_unit(), SimpleNamespace(settings_snapshot={})
    )

    assert result.outputs["region_ids"] == ("rg-detected",)
    assert len(created) == 1


# ---------------------------------------------------------------------------
# L-R8 / I-3 static guards
# ---------------------------------------------------------------------------


def test_run_target_face_never_introduces_a_source_star_error_code():
    from infrastructure.sqlite.pipeline import SqliteTargetCatalog

    source = inspect.getsource(SqliteTargetCatalog)
    assert '"SOURCE_' not in source
    assert "'SOURCE_" not in source


