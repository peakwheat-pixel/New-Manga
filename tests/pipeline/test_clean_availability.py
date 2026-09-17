"""TASK-039: planner Clean-availability regression (TASK-033 R-001).

The inherited ``_clean_available`` judge read a ``clean`` *stage* that no
step ever writes, so render-only commands stayed planning-BLOCKED across
runs. These tests pin the fixed behaviour:

- a real current-Clean probe turns render-only planning to RUN;
- a missing-Clean probe keeps the BLOCKED guard (never relaxed);
- ``probe=None`` (every pre-existing construction) keeps the inherited
  decisions — the AC ③ matrix proves no other command family moved.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.service import PipelineService
from domain.tasks.models import (
    LockSnapshot,
    PipelineScope,
    PlanDecision,
    ScopeType,
    StageState,
)

from application.tasks.store import (
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
)
from test_pipeline import catalog_with_pages


def _region_scope(region_id: str) -> PipelineScope:
    return PipelineScope(ScopeType.REGION, selected_ids=(region_id,))


def _unit_decisions(pipeline, command: str, region_id: str) -> dict[str, str]:
    run = pipeline.create_run(command, _region_scope(region_id))
    pipeline.plan_run(run.run_id)
    task = run.tasks[0]
    return {
        unit.step_type: (
            f"{unit.decision.value}:{unit.reason or ''}"
        )
        for unit in task.units
    }


# r3 lives on page p2 with no stage rows at all — the real-data shape that
# exposed the defect (the inherited fixtures hand-wrote a "clean" stage).
REGION = "r3"


def _service(clean_probe):
    """Local PipelineService builder (the shared helper does not take a
    probe; constructing here keeps the probe kwarg first-class)."""
    store = InMemoryPipelineStore()
    snapshots = InMemorySnapshotProvider(
        settings={"model": "test"},
        provider_bindings={},
        constraint_snapshot_ref="constraint-1",
        context_policy={"window": "current"},
    )
    pipeline = PipelineService(
        catalog_with_pages(),
        store=store,
        snapshots=snapshots,
        clean_probe=clean_probe,
    )
    return pipeline, catalog_with_pages(), store


def test_render_only_command_runs_when_probe_reports_clean() -> None:
    pipeline, _catalog, _store = _service(lambda page_id: True)
    decisions = _unit_decisions(pipeline, "rerender_region", REGION)
    assert decisions == {"render": "run:"}


def test_render_only_command_stays_blocked_when_probe_reports_missing() -> None:
    pipeline, _catalog, _store = _service(lambda page_id: False)
    decisions = _unit_decisions(pipeline, "rerender_region", REGION)
    assert decisions == {"render": "blocked:missing_clean_artifact"}


def test_without_probe_the_inherited_judgement_is_preserved() -> None:
    pipeline, _catalog, _store = _service(clean_probe=None)
    decisions = _unit_decisions(pipeline, "rerender_region", REGION)
    assert decisions == {"render": "blocked:missing_clean_artifact"}


def test_probe_receives_the_target_page_id() -> None:
    seen: list[str] = []
    pipeline, _catalog, _store = _service(
        lambda page_id: seen.append(page_id) or False
    )
    _unit_decisions(pipeline, "rerender_region", REGION)
    assert seen == ["p2"]


@pytest.mark.parametrize(
    "command,expected",
    [
        # no render unit in the step list: decisions cannot move
        ("reinpaint_region", {"segment": "run:", "mask_refine": "run:", "inpaint": "run:"}),
        ("reocr_single", {"ocr": "run:"}),
        # render is planned BLOCKED without a Clean artifact — with or without
        # the probe (the probe answers False here, same as the old judge)
        (
            "translate_region",
            {"translate": "run:", "render": "blocked:missing_clean_artifact"},
        ),
        (
            "retranslate_region",
            {"translate": "run:", "render": "blocked:missing_clean_artifact"},
        ),
    ],
)
def _catalog_with_ocr_ready_region():
    """r4 on page p3: OCR completed, **no** clean stage — the real-data shape
    where only the probe can tell whether a current Clean artifact exists."""
    from domain.tasks.models import RegionSnapshot

    catalog = catalog_with_pages()
    catalog.add_page(
        "p3",
        book_id="book-1",
        chapter_id="chapter-1",
        page_order=3,
        regions=(
            RegionSnapshot(
                "r4",
                "p3",
                current_revisions={"region": "r4-rev-1"},
                stage_states={"ocr": "completed"},
            ),
        ),
    )
    return catalog


def _service_on_ocr_ready_region(clean_probe):
    store = InMemoryPipelineStore()
    snapshots = InMemorySnapshotProvider(
        settings={"model": "test"},
        provider_bindings={},
        constraint_snapshot_ref="constraint-1",
        context_policy={"window": "current"},
    )
    pipeline = PipelineService(
        _catalog_with_ocr_ready_region(),
        store=store,
        snapshots=snapshots,
        clean_probe=clean_probe,
    )
    return pipeline, _catalog_with_ocr_ready_region(), store


def test_command_family_matrix_with_probe_reporting_missing() -> None:
    """AC ③ matrix (probe reports *missing*): every decision is identical to
    the inherited judge — the fix never blocks something that used to run."""
    pipeline, _catalog, _store = _service_on_ocr_ready_region(lambda page_id: False)
    assert _unit_decisions(pipeline, "retranslate_region", "r4") == {
        "translate": "run:",
        "render": "blocked:missing_clean_artifact",
    }
    assert _unit_decisions(pipeline, "reinpaint_region", "r4") == {
        "segment": "run:",
        "mask_refine": "run:",
        "inpaint": "run:",
    }
    assert _unit_decisions(pipeline, "rerender_region", "r4") == {
        "render": "blocked:missing_clean_artifact"
    }
    # page-scope rerender (RERENDER_SINGLE): same guard, page scope
    run = pipeline.create_run(
        "rerender_single",
        PipelineScope(ScopeType.PAGE, selected_ids=("p3",)),
    )
    pipeline.plan_run(run.run_id)
    assert {
        unit.step_type: f"{unit.decision.value}:{unit.reason or ''}"
        for unit in run.tasks[0].units
    } == {"render": "blocked:missing_clean_artifact"}


def test_command_family_matrix_with_probe_reporting_present() -> None:
    """AC ③ matrix (probe reports *present*): command families without a
    render unit are untouched; every family containing render gains RUN
    exactly where the artifact really exists — the fix's intended scope."""
    pipeline, _catalog, _store = _service_on_ocr_ready_region(lambda page_id: True)
    assert _unit_decisions(pipeline, "reinpaint_region", "r4") == {
        "segment": "run:",
        "mask_refine": "run:",
        "inpaint": "run:",
    }
    assert _unit_decisions(pipeline, "retranslate_region", "r4")["render"] == "run:"
    assert _unit_decisions(pipeline, "rerender_region", "r4") == {"render": "run:"}
    run = pipeline.create_run(
        "rerender_single",
        PipelineScope(ScopeType.PAGE, selected_ids=("p3",)),
    )
    pipeline.plan_run(run.run_id)
    assert {
        unit.step_type: unit.decision.value for unit in run.tasks[0].units
    } == {"render": "run"}


def test_same_run_inpaint_branch_still_short_circuits() -> None:
    """The inherited same-run branch (inpaint RUN -> clean available) is the
    first judge input and stays authoritative for the full chain."""
    pipeline, _catalog, _store = _service_on_ocr_ready_region(lambda page_id: False)
    decisions = _unit_decisions(pipeline, "retranslate_region_full", "r4")
    assert decisions["render"] == "run:"  # inpaint ran earlier in this run
    assert decisions["inpaint"] == "run:"


def test_hand_written_clean_stage_still_counts_for_future_writers() -> None:
    """A valid ``clean`` stage (as the old fixtures hand-wrote) still counts —
    kept so a future writer of that stage is honoured, not punished."""
    from domain.tasks.models import RegionSnapshot

    catalog = catalog_with_pages()
    catalog.add_page(
        "p3",
        book_id="book-1",
        chapter_id="chapter-1",
        page_order=3,
        regions=(
            RegionSnapshot(
                "r4",
                "p3",
                current_revisions={"region": "r4-rev-1"},
                stage_states={"clean": "completed"},
            ),
        ),
    )
    store = InMemoryPipelineStore()
    snapshots = InMemorySnapshotProvider(
        settings={"model": "test"},
        provider_bindings={},
        constraint_snapshot_ref="constraint-1",
        context_policy={"window": "current"},
    )
    pipeline = PipelineService(catalog, store=store, snapshots=snapshots)
    decisions = _unit_decisions(pipeline, "rerender_region", "r4")
    assert decisions == {"render": "run:"}
