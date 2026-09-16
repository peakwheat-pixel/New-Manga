"""TASK-011 domain records: command catalog and immutable snapshots."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from domain.tasks.models import (  # noqa: E402
    COMMAND_CATALOG,
    PlanDecision,
    PipelineScope,
    ScopeType,
    StageState,
    TargetSnapshot,
)


def test_command_catalog_contains_every_page_and_region_command() -> None:
    assert set(COMMAND_CATALOG) == {
        "translate_all",
        "translate_untranslated",
        "translate_selected",
        "translate_single",
        "rerender_all",
        "rerender_selected",
        "rerender_single",
        "reinpaint_all",
        "reinpaint_selected",
        "reinpaint_single",
        "reocr_all",
        "reocr_selected",
        "reocr_single",
        "ocr_region",
        "retranslate_region",
        "retranslate_region_full",
        "reinpaint_region",
        "rerender_region",
    }


def test_scope_and_target_snapshots_are_defensive_and_immutable() -> None:
    scope = PipelineScope(ScopeType.PAGE_SELECTION, selected_ids=("p1",))
    target = TargetSnapshot(
        target_id="p1",
        page_id="p1",
        target_type="page",
        stage_states={"ocr": StageState.COMPLETED},
        current_revisions={"region:r1": "rev-1"},
        metadata={"nested": {"value": 1}},
    )

    assert scope.selected_ids == ("p1",)
    assert target.stage_states["ocr"] is StageState.COMPLETED
    with pytest.raises(TypeError):
        target.current_revisions["region:r1"] = "rev-2"
    with pytest.raises(TypeError):
        target.metadata["nested"]["value"] = 2


def test_plan_decisions_and_stage_states_expose_terminal_boundaries() -> None:
    assert PlanDecision.RUN.is_terminal is False
    assert PlanDecision.BLOCKED.is_terminal is False
    assert PlanDecision.SKIP_VALID.is_terminal is True
    assert PlanDecision.SKIP_LOCK.is_terminal is True
    assert StageState.STALE.is_valid is False
    assert StageState.COMPLETED.is_valid is True
