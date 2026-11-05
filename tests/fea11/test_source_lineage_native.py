"""FEA-11-LINEAGE-1 AC1/AC2/AC3 evidence on REAL SQLite (r1 P1-5).

No fake repository and no ``__new__`` bypass: every test drives the
production ``SqliteRegionRepository`` / ``RegionEditingService`` /
``DraftProtectionService`` / ``SqliteTargetCatalog`` / ``RenderService``
against a fully migrated v8 ``:memory:`` database, with the production
``LineageIsolationGuard`` wired exactly like ``bootstrap.core_assembly`` does.

Covered (r1 findings):
* P0-1a — ``save_manual_translation`` / ``confirm_final`` / ``set_locks``
  register native lineage in the same transaction;
* P0-1b — ``restore_revision`` registers lineage;
* P0-1c — draft apply registers lineage;
* P0-1d — the Run region-candidate writer registers lineage;
* P0-1e — ``add_revision`` accepts + writes lineage;
* P0-1f — the batch/reorder path registers lineage (plus a grep of the three
  ``INSERT INTO region_revisions`` writers lives in the verification log);
* backfill — missing rows on ALREADY sync-managed pages become
  ``legacy_unverified`` (no guessed attribution, idempotent, non-synced pages
  untouched so the first switch can still capture ``captured_v7``);
* P1-1 — ``same_content`` read edges (multi-hop) allow the old revision;
* P1-2 / P1-5 — changed cut → typed refusal, no-lineage / legacy_unverified →
  typed unverifiable; render/list/edit/Run entries all covered;
* rollback — a failed revision transaction leaves no orphan lineage row;
* P0 regression — a page with a binding but NO sync publication (never
  switched) keeps the pre-LINEAGE-1 behaviour and its normal edits work.
"""

from __future__ import annotations

import json

import pytest

from application.editing.drafts import DraftProtectionService
from application.editing.service import RegionEditingService
from application.rendering.service import RenderService
from application.sources.lineage import (
    LINEAGE_BINDING_CHANGED,
    LINEAGE_UNVERIFIED,
    LineageBindingChanged,
    LineageIsolationGuard,
    LineageUnverified,
    LineageVerificationError,
)
from domain.regions.entities import BBox, Region, RegionGeometry
from domain.tasks.models import (
    CommandType,
    PipelineScope,
    ScopeType,
    StepResult,
)
from infrastructure.filesystem.draft_journal import DraftJournal
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.step_writes import RegionStepWriter
from infrastructure.sqlite.pipeline import SqliteTargetCatalog
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.source_sync import (
    SourceSyncLineageFacts,
    SourceSyncStore,
)
from tests.fea11.conftest import add_source_tree, add_sync_switch

NOW = "2026-11-05T00:00:00.000+00:00"
DIGEST = "b" * 64

_TEXT_EMPTY = {
    "ocr_text": "",
    "machine_translation": "",
    "edited_translation": "",
    "final_translation": "",
    "final_source": "none",
    "edited_confirmed": False,
    "manual_edited": False,
    "translation_locked": False,
}


# ---------------------------------------------------------------------------
# real-DB seeding helpers (production migrations come from the conn fixture)
# ---------------------------------------------------------------------------


def seed_page(conn, book_chapter, page_id: str = "p1") -> str:
    book_id, chapter_id = book_chapter
    conn.execute(
        "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
        " sort_order, source_hash, source_size_bytes, width, height,"
        " managed_original_ref, source_mode, integrity_status, created_at,"
        " updated_at) VALUES (?, ?, ?, 1, 1, ?, 10, 4, 3, ?, 'referenced',"
        " 'complete', ?, ?)",
        (page_id, chapter_id, f"{page_id}.png", DIGEST,
         f"original/{page_id}.png", NOW, NOW),
    )
    conn.commit()
    return page_id


def seed_source(conn) -> None:
    add_source_tree(
        conn, source_id="s1", version_id="sv1", digest="a" * 64,
        entries=[
            ("e1", "001.png", DIGEST),
            ("e2", "002.png", "c" * 64),
            ("e3", "003.png", "d" * 64),
            ("e4", "004.png", "e" * 64),
            ("e5", "005.png", "f" * 64),
        ],
        legacy_v7_evidence=False,
    )


def seed_binding(
    conn,
    page_id: str,
    binding_id: str = "pb-p1",
    *,
    binding_version: int = 1,
    previous_binding_id: str | None = None,
    entry_id: str = "e1",
) -> str:
    conn.execute(
        "INSERT INTO page_bindings (binding_id, page_id, project_id,"
        " binding_version, source_id, entry_id, accepted_source_version,"
        " status, previous_binding_id, authorization_generation,"
        " authorized_at, verified_digest, created_at, updated_at)"
        " VALUES (?, ?, 'b1', ?, 's1', ?, 'sv1', 'healthy', ?, 1, ?, ?,"
        " ?, ?)",
        (binding_id, page_id, binding_version, entry_id, previous_binding_id,
         NOW, DIGEST, NOW, NOW),
    )
    conn.commit()
    return binding_id


def seed_referenced_page(
    conn, book_chapter, *, page_id: str = "p1", binding_id: str = "pb-p1"
) -> tuple[str, str]:
    """page + source tree + healthy binding B1 (no publication: not synced)."""
    seed_page(conn, book_chapter, page_id)
    seed_source(conn)
    seed_binding(conn, page_id, binding_id)
    return page_id, binding_id


def seed_region(
    conn,
    page_id: str,
    region_id: str = "rg1",
    *,
    revision_id: str = "rv1",
    lineage: tuple[str | None, str] | None = None,
    reading_order: int = 1,
    region_locked: bool = False,
) -> Region:
    region = Region(
        region_id=region_id,
        page_id=page_id,
        geometry=RegionGeometry(
            bbox=BBox(0, 0, 4, 3),
            polygon=((0, 0), (4, 0), (4, 3), (0, 3)),
        ),
        reading_order=reading_order,
        region_locked=region_locked,
    )
    region.created_at = NOW
    region.updated_at = NOW
    region.current_revision_id = revision_id
    snapshot = region.snapshot_state()
    # One explicit transaction: ``regions.current_revision_id`` carries a
    # DEFERRABLE forward FK onto the revision row, and this fixture connection
    # is in autocommit mode (production connections are not).
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            "INSERT INTO regions (region_id, page_id, region_type, reading_order,"
            " geometry_json, text_json, style_json, sfx_policy, region_locked,"
            " translation_locked, inpaint_locked, current_revision_id, created_at,"
            " updated_at) VALUES (?, ?, 'speech', ?, ?, ?, ?, 'skip', ?, 0, 0, ?,"
            " ?, ?)",
            (
                region_id, page_id, reading_order,
                json.dumps(snapshot["geometry"], sort_keys=True),
                json.dumps(snapshot["text"], sort_keys=True),
                json.dumps(snapshot["style"], sort_keys=True),
                int(region_locked), revision_id, NOW, NOW,
            ),
        )
        conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES (?, ?, 1, ?, 'machine', 'confirmed', 0, ?)",
            (revision_id, region_id, json.dumps(snapshot, sort_keys=True), NOW),
        )
        if lineage is not None:
            binding_id, provenance = lineage
            SourceSyncStore(conn).insert_lineage(
                revision_id=revision_id,
                region_id=region_id,
                binding_id=binding_id,
                provenance=provenance,
                now=NOW,
            )
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    return region


def make_guard(conn) -> LineageIsolationGuard:
    return LineageIsolationGuard(SourceSyncLineageFacts(conn))


def make_editing(conn, guard, bindings: dict[str, str]):
    repo = SqliteRegionRepository(conn, lineage_guard=guard)
    service = RegionEditingService(
        repo,
        lineage_binding=bindings.get,
        lineage_guard=guard,
    )
    return repo, service


def lineage_rows(conn):
    return conn.execute(
        "SELECT revision_id, region_id, binding_id, provenance"
        " FROM source_revision_lineage ORDER BY revision_id"
    ).fetchall()


def revision_count(conn, region_id: str) -> int:
    return conn.execute(
        "SELECT COUNT(*) AS n FROM region_revisions WHERE region_id = ?",
        (region_id,),
    ).fetchone()["n"]


def latest_lineage(conn, revision_id: str):
    return SourceSyncStore(conn).lineage_of_revision(revision_id)


# ---------------------------------------------------------------------------
# AC1 — every revision write path registers native lineage (r1 P0-1a/b/f)
# ---------------------------------------------------------------------------


def test_every_user_single_revision_write_path_registers_native_lineage(
    conn, book_chapter
):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    _repo, editing = make_editing(
        conn, make_guard(conn), {page_id: binding_id}
    )

    region = editing.create_region(
        page_id, RegionGeometry(bbox=BBox(0, 0, 4, 3))
    )
    editing.save_manual_translation(region.region_id, "人手译文")
    editing.confirm_final(region.region_id)
    editing.set_locks(region.region_id, region_locked=True)
    editing.restore_revision(region.region_id, 1)

    rows = lineage_rows(conn)
    assert len(rows) == revision_count(conn, region.region_id) == 5
    assert {row["binding_id"] for row in rows} == {binding_id}
    assert {row["provenance"] for row in rows} == {"native"}
    assert {row["region_id"] for row in rows} == {region.region_id}


def test_reorder_batch_registers_native_lineage(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    _repo, editing = make_editing(
        conn, make_guard(conn), {page_id: binding_id}
    )
    first = editing.create_region(page_id, RegionGeometry(bbox=BBox(0, 0, 2, 2)))
    second = editing.create_region(page_id, RegionGeometry(bbox=BBox(2, 2, 2, 2)))

    editing.reorder_regions(page_id, [second.region_id, first.region_id])

    rows = lineage_rows(conn)
    assert len(rows) == revision_count(conn, first.region_id) + revision_count(
        conn, second.region_id
    ) == 4
    assert {row["binding_id"] for row in rows} == {binding_id}
    assert {row["provenance"] for row in rows} == {"native"}


def test_add_revision_writes_the_requested_lineage(conn, book_chapter):
    from application.editing.ports import RevisionLineage
    from domain.regions.entities import RegionOrigin, RegionRevision, ReviewState

    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    region = seed_region(conn, page_id)
    repo = SqliteRegionRepository(conn)
    repo.add_revision(
        RegionRevision(
            region_revision_id="rv2",
            region_id=region.region_id,
            revision_no=2,
            snapshot=region.snapshot_state(),
            origin=RegionOrigin.USER,
            review_state=ReviewState.UNREVIEWED,
        ),
        RevisionLineage(binding_id=binding_id, provenance="native"),
    )
    row = latest_lineage(conn, "rv2")
    assert row["binding_id"] == binding_id
    assert row["provenance"] == "native"
    # The explicit new-history insert never moves the current pointer.
    assert conn.execute(
        "SELECT current_revision_id FROM regions WHERE region_id = ?",
        (region.region_id,),
    ).fetchone()["current_revision_id"] == "rv1"


def test_draft_apply_registers_native_lineage(conn, book_chapter, tmp_path):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    repo, editing = make_editing(
        conn, make_guard(conn), {page_id: binding_id}
    )
    region = editing.create_region(
        page_id, RegionGeometry(bbox=BBox(0, 0, 4, 3))
    )
    journal = DraftJournal(tmp_path / "drafts")
    try:
        drafts = DraftProtectionService(
            repository=repo,
            committer=repo,
            connection=conn,
            journal=journal,
            lineage_binding=lambda target_page: (
                binding_id if target_page == page_id else None
            ),
        )
        lease = drafts.open_draft(
            "session-1", page_id, None,
            base_revision_id=None, page_binding_version=1,
        )
        assert lease.can_edit and lease.token is not None
        candidate = drafts.prepare_candidate(
            region.region_id,
            {"text": {"edited_translation": "草稿译文"}},
            origin="user",
            draft_id=lease.draft.draft_id,
        )
        applied = drafts.apply_candidates(
            lease.token, [candidate.candidate_id]
        )
    finally:
        journal.close()

    applied_revision = applied[region.region_id]
    row = latest_lineage(conn, applied_revision)
    assert row is not None
    assert row["binding_id"] == binding_id
    assert row["provenance"] == "native"


def test_run_region_candidate_registers_native_lineage(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "native"))
    # same_content switch: the old revision stays readable on the new binding,
    # so the Run is allowed to register its candidate as native on B2.
    new_binding = add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    guard = make_guard(conn)
    bindings = {page_id: new_binding}
    repo = SqliteRegionRepository(conn, lineage_guard=guard)
    pipeline = build_production_pipeline(
        conn, provider_bindings={"ocr": {"provider_id": "test-ocr"}}
    )
    pipeline._catalog.lineage_guard = guard
    pipeline._catalog.lineage_binding = bindings.get

    run = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("rg1",)),
    )
    pipeline.plan_run(run.run_id)
    step = pipeline.record_step_attempt(run.tasks[0].task_id, "ocr")
    prepared = RegionStepWriter(conn, repo).prepare_ocr_text(
        "rg1", "新的原文",
        source_run_id=run.run_id,
        source_step_run_id=step.step_run_id,
        expected_current_revision_id="rv1",
    )
    outcome = pipeline.commit_step_result(
        step.step_run_id,
        StepResult(
            target_id="rg1",
            step_type="ocr",
            outputs={"ocr_text": "新的原文"},
            revision_updates={"region": prepared.revision_id},
        ),
    )
    assert outcome.status == "committed"
    row = latest_lineage(conn, prepared.revision_id)
    assert row is not None
    assert row["binding_id"] == new_binding
    assert row["provenance"] == "native"


def test_run_entry_refuses_a_changed_binding_region_typed(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "captured_v7"))
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="changed", seq=1,
    )
    guard = make_guard(conn)
    pipeline = build_production_pipeline(conn, provider_bindings={})
    pipeline._catalog.lineage_guard = guard
    pipeline._catalog.lineage_binding = lambda target_page: "pb-p1-b2"

    with pytest.raises(Exception) as error:
        pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=("rg1",)),
        )
    assert getattr(error.value, "code", None) == LINEAGE_BINDING_CHANGED


# ---------------------------------------------------------------------------
# AC1 — rollback atomicity: no orphan lineage row (r1 P1-5)
# ---------------------------------------------------------------------------


def test_failed_revision_transaction_leaves_no_orphan_lineage(conn, book_chapter):
    from application.editing.ports import RevisionLineage
    from domain.regions.entities import RegionOrigin, RegionRevision, ReviewState

    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    region = seed_region(conn, page_id)
    repo = SqliteRegionRepository(conn)
    staged = repo.get_region(region.region_id)
    # Force the region-row UPDATE to fail AFTER the revision + lineage INSERT:
    # the foreign key to pages rejects the unknown page id, the whole
    # transaction must roll back (no region_revision, no lineage row).
    staged.page_id = "missing-page"
    result = repo.commit_region_revision(
        staged,
        RegionRevision(
            region_revision_id="rv-orphan",
            region_id=region.region_id,
            revision_no=0,
            snapshot=staged.snapshot_state(),
            origin=RegionOrigin.USER,
            review_state=ReviewState.UNREVIEWED,
        ),
        lineage=RevisionLineage(binding_id=binding_id, provenance="native"),
    )
    assert result.status.value == "db_failed"
    assert revision_count(conn, region.region_id) == 1
    assert [row["revision_id"] for row in lineage_rows(conn)] == []


# ---------------------------------------------------------------------------
# AC2 — the C-17 §7.1 isolation guard semantics
# ---------------------------------------------------------------------------


def test_same_content_chain_is_readable_multi_hop(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "captured_v7"))
    b2 = add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    b3 = add_sync_switch(
        conn, page_id=page_id, old_binding_id=b2,
        new_binding_id="pb-p1-b3", relation="same_content", seq=2,
    )
    guard = make_guard(conn)

    verdict = guard.page_verdict(page_id, [("rg1", "rv1")])
    assert verdict.guarded and verdict.hidden == ()
    assert guard.is_region_readable(
        page_id=page_id, region_id="rg1", revision_id="rv1"
    )

    _repo, editing = make_editing(conn, guard, {page_id: b3})
    assert [row["region_id"] for row in editing.list_region_summaries(page_id)] == [
        "rg1"
    ]
    # An edit is allowed too: same_content means equivalent coordinates, so the
    # new revision may be registered as native on B3.
    editing.save_manual_translation("rg1", "等价边上的编辑")
    native = [
        row for row in lineage_rows(conn) if row["provenance"] == "native"
    ]
    assert [row["binding_id"] for row in native] == [b3]


def test_changed_cut_hides_and_refuses_typed(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "native"))
    b2 = add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=b2,
        new_binding_id="pb-p1-b3", relation="changed", seq=2,
    )
    guard = make_guard(conn)

    verdict = guard.page_verdict(page_id, [("rg1", "rv1")])
    assert verdict.guarded
    assert [(item.region_id, item.code) for item in verdict.hidden] == [
        ("rg1", LINEAGE_BINDING_CHANGED)
    ]

    _repo, editing = make_editing(conn, guard, {page_id: "pb-p1-b3"})
    # ListRegions: the old-coordinate region is not part of the new image set.
    assert editing.list_region_summaries(page_id) == []
    assert editing.list_region_details(page_id) == []
    # Edit entry: typed refusal, zero write (current revision stays rv1).
    with pytest.raises(LineageBindingChanged):
        editing.save_manual_translation("rg1", "不应写入")
    assert revision_count(conn, "rg1") == 1
    assert [row["revision_id"] for row in lineage_rows(conn)] == ["rv1"]


def test_missing_lineage_row_is_typed_unverified(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id)  # no lineage row at all
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    guard = make_guard(conn)

    verdict = guard.page_verdict(page_id, [("rg1", "rv1")])
    assert [(item.region_id, item.code) for item in verdict.hidden] == [
        ("rg1", LINEAGE_UNVERIFIED)
    ]
    _repo, editing = make_editing(conn, guard, {page_id: "pb-p1-b2"})
    assert editing.list_region_summaries(page_id) == []
    with pytest.raises(LineageUnverified):
        editing.save_manual_translation("rg1", "无法验证")
    assert [
        row for row in lineage_rows(conn) if row["revision_id"] == "rv1"
    ] == []


def test_legacy_unverified_row_is_not_coordinate_evidence(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(None, "legacy_unverified"))
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    guard = make_guard(conn)

    verdict = guard.page_verdict(page_id, [("rg1", "rv1")])
    assert [(item.region_id, item.code) for item in verdict.hidden] == [
        ("rg1", LINEAGE_UNVERIFIED)
    ]


def test_null_current_revision_is_unverified_on_a_synced_page(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "native"))
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    guard = make_guard(conn)
    verdict = guard.page_verdict(page_id, [("rg2", None)])
    assert [(item.region_id, item.code) for item in verdict.hidden] == [
        ("rg2", LINEAGE_UNVERIFIED)
    ]


def test_page_without_binding_is_outside_the_guard_scope(conn, book_chapter):
    seed_page(conn, book_chapter, "p1")
    seed_region(conn, "p1")  # managed page: no binding, no lineage
    guard = make_guard(conn)

    verdict = guard.page_verdict("p1", [("rg1", "rv1")])
    assert not verdict.guarded and verdict.hidden == ()


def test_non_synced_page_keeps_pre_lineage_behaviour(conn, book_chapter):
    """r1 P0-1 regression: a binding that never went through a sync switch
    must NOT make its pre-lineage revisions unreadable, and its edits still
    write native lineage on the only binding the page ever had."""
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id)  # no lineage row: stock data before the fix
    guard = make_guard(conn)

    verdict = guard.page_verdict(page_id, [("rg1", "rv1")])
    assert not verdict.guarded and verdict.hidden == ()

    _repo, editing = make_editing(conn, guard, {page_id: binding_id})
    assert [row["region_id"] for row in editing.list_region_summaries(page_id)] == [
        "rg1"
    ]
    editing.save_manual_translation("rg1", "普通页编辑")
    native = [
        row for row in lineage_rows(conn) if row["provenance"] == "native"
    ]
    assert len(native) == 1 and native[0]["binding_id"] == binding_id


# ---------------------------------------------------------------------------
# AC2 — render entry (rerender_region typed BLOCKED; page render skips)
# ---------------------------------------------------------------------------


def _render_service(conn, guard) -> RenderService:
    return RenderService(
        region_repo=SqliteRegionRepository(conn),
        locator=None,
        artifacts=None,
        storage=None,
        layout_engine=None,
        compositor=None,
        source_styles=None,
        font_catalog=None,
        lineage_guard=guard,
    )


def test_single_region_rerender_refuses_a_changed_binding_typed(
    conn, book_chapter
):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "native"))
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="changed", seq=1,
    )
    service = _render_service(conn, make_guard(conn))

    outcome = service.rerender_region("rg1")
    assert outcome.status == "blocked"
    assert outcome.error_code == LINEAGE_BINDING_CHANGED


def test_single_region_rerender_refuses_unverified_typed(conn, book_chapter):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id)
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    service = _render_service(conn, make_guard(conn))

    outcome = service.rerender_region("rg1")
    assert outcome.status == "blocked"
    assert outcome.error_code == LINEAGE_UNVERIFIED


def test_page_render_active_regions_excludes_hidden_with_reason(
    conn, book_chapter
):
    page_id, binding_id = seed_referenced_page(conn, book_chapter)
    seed_region(conn, page_id, lineage=(binding_id, "native"))
    seed_region(
        conn, page_id, region_id="rg2", revision_id="rv2",
        lineage=(binding_id, "native"), reading_order=2,
    )
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="changed", seq=1,
    )
    service = _render_service(conn, make_guard(conn))
    visible, hidden = service._active_regions(page_id)
    assert [region.region_id for region in visible] == []
    assert [(item.region_id, item.code) for item in hidden] == [
        ("rg1", LINEAGE_BINDING_CHANGED),
        ("rg2", LINEAGE_BINDING_CHANGED),
    ]


# ---------------------------------------------------------------------------
# Stock backfill (r1 P0-1): legacy_unverified only, no guessed attribution
# ---------------------------------------------------------------------------


def test_backfill_marks_only_already_synced_pages_legacy_unverified(
    conn, book_chapter
):
    # Page p1 has been through one switch; its region revisions lost their
    # lineage rows (pre-fix writers). Page p2 has a binding but never switched.
    page_id, binding_id = seed_referenced_page(conn, book_chapter, page_id="p1")
    seed_page(conn, book_chapter, "p2")
    seed_binding(conn, "p2", "pb-p2", entry_id="e2")
    seed_region(conn, page_id)
    seed_region(conn, "p2", region_id="rg2", revision_id="rv2")
    add_sync_switch(
        conn, page_id=page_id, old_binding_id=binding_id,
        new_binding_id="pb-p1-b2", relation="same_content", seq=1,
    )
    store = SourceSyncStore(conn)

    assert store.backfill_legacy_unverified_lineage(now=NOW) == 1
    rows = {row["revision_id"]: row for row in lineage_rows(conn)}
    assert set(rows) == {"rv1"}
    assert rows["rv1"]["binding_id"] is None
    assert rows["rv1"]["provenance"] == "legacy_unverified"
    # Idempotent: nothing left to insert, and rv2 (non-synced page) is NOT
    # captured here — the first switch must still be able to register its
    # current revision as captured_v7.
    assert store.backfill_legacy_unverified_lineage(now=NOW) == 0
    assert "rv2" not in {row["revision_id"] for row in lineage_rows(conn)}


# ---------------------------------------------------------------------------
# r2 scope matrix (DSH ruling on the guard scope): what an upgraded REAL user
# library can still read and what it must refuse, for a mixed library that
# contains managed pages, referenced-not-synced pages and switched pages.
# The matrix is printed so `pytest -s` captures it as evidence.
# ---------------------------------------------------------------------------


def test_mixed_library_scope_matrix_is_diagnosable(conn, book_chapter):
    # 1) managed page: no binding at all, old region without lineage.
    seed_page(conn, book_chapter, "p-managed")
    seed_region(conn, "p-managed", region_id="rg-managed",
                revision_id="rv-managed")
    # 2) referenced page that never went through a sync switch.
    seed_page(conn, book_chapter, "p-ref")
    seed_source(conn)
    seed_binding(conn, "p-ref", "pb-ref", entry_id="e2")
    seed_region(conn, "p-ref", region_id="rg-ref", revision_id="rv-ref")
    # 3) switched page with a CUT (changed) relation.
    seed_page(conn, book_chapter, "p-cut")
    seed_binding(conn, "p-cut", "pb-cut", entry_id="e3")
    seed_region(conn, "p-cut", region_id="rg-cut", revision_id="rv-cut",
                lineage=("pb-cut", "captured_v7"))
    add_sync_switch(
        conn, page_id="p-cut", old_binding_id="pb-cut",
        new_binding_id="pb-cut-b2", relation="changed", seq=11,
    )
    # 4) switched page with a two-hop same_content relation.
    seed_page(conn, book_chapter, "p-same")
    seed_binding(conn, "p-same", "pb-same", entry_id="e4")
    seed_region(conn, "p-same", region_id="rg-same", revision_id="rv-same",
                lineage=("pb-same", "captured_v7"))
    b2 = add_sync_switch(
        conn, page_id="p-same", old_binding_id="pb-same",
        new_binding_id="pb-same-b2", relation="same_content", seq=12,
    )
    add_sync_switch(
        conn, page_id="p-same", old_binding_id=b2,
        new_binding_id="pb-same-b3", relation="same_content", seq=13,
    )
    # 5) switched page whose region revision lost its lineage row (pre-fix
    #    writer): the start-up backfill must register it unverified.
    seed_page(conn, book_chapter, "p-stock")
    seed_binding(conn, "p-stock", "pb-stock", entry_id="e5")
    seed_region(conn, "p-stock", region_id="rg-stock",
                revision_id="rv-stock")
    add_sync_switch(
        conn, page_id="p-stock", old_binding_id="pb-stock",
        new_binding_id="pb-stock-b2", relation="same_content", seq=14,
    )

    store = SourceSyncStore(conn)
    first = store.backfill_legacy_unverified_lineage(now=NOW)
    second = store.backfill_legacy_unverified_lineage(now=NOW)
    assert (first, second) == (1, 0)

    guard = make_guard(conn)
    bindings = {
        "p-managed": None,
        "p-ref": "pb-ref",
        "p-cut": "pb-cut-b2",
        "p-same": "pb-same-b3",
        "p-stock": "pb-stock-b2",
    }
    repo = SqliteRegionRepository(conn, lineage_guard=guard)
    editing = RegionEditingService(
        repo, lineage_binding=bindings.get, lineage_guard=guard
    )
    render = _render_service(conn, guard)
    pipeline = build_production_pipeline(conn, provider_bindings={})
    pipeline._catalog.lineage_guard = guard
    pipeline._catalog.lineage_binding = bindings.get

    cases = [
        ("p-managed", "rg-managed", "rv-managed"),
        ("p-ref", "rg-ref", "rv-ref"),
        ("p-cut", "rg-cut", "rv-cut"),
        ("p-same", "rg-same", "rv-same"),
        ("p-stock", "rg-stock", "rv-stock"),
    ]
    print("lineage-matrix: page scope lineage guarded hidden_code visible edit")
    rows = []
    for page_id, region_id, revision_id in cases:
        standing = store.lineage_of_revision(revision_id)
        lineage_label = (
            "none" if standing is None
            else f"{standing['provenance']}:{standing['binding_id'] or '-'}"
        )
        verdict = guard.page_verdict(page_id, [(region_id, revision_id)])
        visible = [
            row["region_id"]
            for row in editing.list_region_summaries(page_id)
        ]
        try:
            editing.save_manual_translation(region_id, "scope probe")
            edit = "allowed"
        except LineageVerificationError as error:
            edit = error.code
        hidden_code = verdict.hidden[0].code if verdict.hidden else "-"
        rows.append(
            (page_id, lineage_label, verdict.guarded, hidden_code, visible, edit)
        )
        print(
            f"lineage-matrix: {page_id} lineage={lineage_label}"
            f" guarded={verdict.guarded} hidden={hidden_code}"
            f" visible={len(visible)} edit={edit}"
        )

    by_page = {row[0]: row for row in rows}
    managed, referenced = by_page["p-managed"], by_page["p-ref"]
    cut, same, stock = by_page["p-cut"], by_page["p-same"], by_page["p-stock"]

    # Managed + referenced-not-synced pages: outside the C-17 §7.1 sync scope,
    # their missing lineage is NOT a refusal (P0 regression guard).
    assert managed[2] is False and managed[4] == ["rg-managed"]
    assert managed[5] == "allowed"
    assert referenced[2] is False and referenced[4] == ["rg-ref"]
    assert referenced[5] == "allowed"
    # The allowed edit on the referenced page registered native lineage on the
    # only binding that page ever had.
    ref_native = [
        row for row in lineage_rows(conn)
        if row["revision_id"] not in {"rv-managed", "rv-ref"}
        and row["binding_id"] == "pb-ref"
    ]
    assert [row["provenance"] for row in ref_native] == ["native"]

    # Switched pages: fail-closed and typed.
    assert cut[3] == LINEAGE_BINDING_CHANGED and cut[4] == []
    assert cut[5] == LINEAGE_BINDING_CHANGED
    assert stock[3] == LINEAGE_UNVERIFIED and stock[4] == []
    assert stock[5] == LINEAGE_UNVERIFIED
    assert same[3] == "-" and same[4] == ["rg-same"]
    assert same[5] == "allowed"

    # Render entry: hidden pages are typed BLOCKED; the same_content page is
    # readable through the two-hop edge.
    assert render.rerender_region("rg-cut").error_code == LINEAGE_BINDING_CHANGED
    assert render.rerender_region("rg-stock").error_code == LINEAGE_UNVERIFIED
    assert render._active_regions("p-same")[0][0].region_id == "rg-same"

    # Run entry: a switched cut page is refused typed at plan time; the
    # same_content page plans normally. A page-scope target is FILTERED (the
    # new image's region set excludes the old coordinates) and the catalog
    # logs the filtered count.
    page_scope = pipeline._catalog.expand(
        PipelineScope(ScopeType.PAGE, selected_ids=("p-cut",))
    )
    assert page_scope[0].regions == ()
    with pytest.raises(Exception) as refused:
        pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=("rg-cut",)),
        )
    assert getattr(refused.value, "code", None) == LINEAGE_BINDING_CHANGED
    allowed_run = pipeline.create_run(
        CommandType.OCR_REGION,
        PipelineScope(ScopeType.REGION, selected_ids=("rg-same",)),
    )
    assert allowed_run.run_id
