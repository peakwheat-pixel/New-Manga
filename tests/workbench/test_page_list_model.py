"""WorkbenchPageListModel behavior (TASK-013, AC-PAGE-002/003, PROGRESS-004/005).

The model only reshapes projection rows; all statuses come from the
shared projection, so these tests pin roles, filtering and selection.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import fail_first_region_step, make_pipeline

from domain.tasks.models import PipelineScope, ScopeType
from ui.models.tasks.page_list_model import WorkbenchPageListModel
from ui.models.tasks.projection import build_projection


def make_model(failed=("p2",)):
    from application.translation.pipeline.executor import DeterministicStepExecutor

    executor = DeterministicStepExecutor(
        fail_on=fail_first_region_step(failed)
    )
    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 5)], executor=executor
    )
    run = service.create_run(
        "translate_all", PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
    )
    service.plan_run(run.run_id)
    service.execute_run(run.run_id)
    projection = build_projection(run)
    model = WorkbenchPageListModel()
    model.apply_projection(projection)
    return model, projection


def test_roles_carry_projection_fields():
    model, projection = make_model()
    assert model.rowCount() == 4
    index = model.index(0, 0)
    role = model.roleForName("pageId")
    assert model.data(index, role) == "p1"
    order = model.roleForName("pageOrder")
    assert model.data(index, order) == 1
    status_role = model.roleForName("status")
    assert model.data(index, status_role) == "completed"
    failed_role = model.roleForName("errorCode")
    assert model.data(index, failed_role) is None


def test_filter_failed_shows_only_failed_rows():
    """AC-PROGRESS-004: 点击“失败 N” → PageList 筛出失败 Page。"""

    model, _projection = make_model()
    model.set_filter("failed")
    assert model.rowCount() == 1
    assert model.page_id_at(0) == "p2"
    model.set_filter("all")
    assert model.rowCount() == 4


def test_filter_completed_and_skipped_sets():
    """AC-PROGRESS-005: 点击已完成/跳过 → PageList 显示对应集合。"""

    model, _ = make_model(failed=("p2", "p3"))
    model.set_filter("completed")
    assert model.rowCount() == 2
    model.set_filter("skipped")
    assert model.rowCount() == 0  # no skips in this run
    try:
        model.set_filter("bogus")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown filter must raise")
    model.set_filter("all")
    assert model.rowCount() == 4


def test_selection_toggle_and_clear():
    """AC-PAGE-002: multi-select within the chapter only."""

    model, _ = make_model()
    model.toggle_selected("p1")
    model.toggle_selected("p3")
    assert model.get_selected_ids() == ["p1", "p3"]
    assert model.row_index_of("p1") == 0
    # selection roles visible through data()
    selected_role = model.roleForName("isSelected")
    assert model.data(model.index(0, 0), selected_role) is True
    assert model.data(model.index(1, 0), selected_role) is False
    model.clear_selection()
    assert model.get_selected_ids() == []


def test_selection_ignores_unknown_pages():
    model, _ = make_model()
    model.toggle_selected("nope")
    model.set_selected(["p1", "ghost"])
    assert model.get_selected_ids() == ["p1"]


def test_projection_refresh_preserves_selection():
    model, projection = make_model()
    model.toggle_selected("p1")
    model.apply_projection(projection)  # e.g. a throttled refresh
    assert model.get_selected_ids() == ["p1"]


def test_row_index_of_respects_filter():
    model, _ = make_model()
    model.set_filter("failed")
    assert model.row_index_of("p2") == 0
    assert model.row_index_of("p1") == -1  # filtered out, not gone
