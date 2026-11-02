"""TASK-011 in-memory persistence seams used by deterministic tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.store import (  # noqa: E402
    InMemoryPipelineStore,
    InMemorySnapshotProvider,
    InMemoryTargetCatalog,
)
from domain.tasks.models import (  # noqa: E402
    PipelineError,
    PipelineScope,
    RegionSnapshot,
    ScopeType,
    StageState,
)


def make_catalog() -> InMemoryTargetCatalog:
    catalog = InMemoryTargetCatalog()
    catalog.add_page(
        "p1",
        book_id="b1",
        chapter_id="c1",
        page_order=2,
        regions=(
            RegionSnapshot(
                "r1", "p1", current_revisions={"region": "rev-1"}
            ),
            RegionSnapshot(
                "r2", "p1", current_revisions={"region": "rev-2"}
            ),
        ),
    )
    catalog.add_page("p2", book_id="b1", chapter_id="c1", page_order=1)
    catalog.add_page("p3", book_id="b2", chapter_id="c2", page_order=3)
    return catalog


def test_scope_expansion_is_stable_and_region_scope_is_a_leaf() -> None:
    catalog = make_catalog()

    pages = catalog.expand(PipelineScope(ScopeType.CHAPTER, chapter_id="c1"))
    assert [target.page_id for target in pages] == ["p2", "p1"]
    assert pages[1].target_type.value == "page"

    region = catalog.expand(
        PipelineScope(ScopeType.REGION, selected_ids=("r1",))
    )
    assert len(region) == 1
    assert region[0].target_id == "r1"
    assert region[0].region_id == "r1"
    assert region[0].page_id == "p1"


def test_scope_expansion_rejects_empty_missing_and_deleted_targets() -> None:
    catalog = make_catalog()
    with pytest.raises(PipelineError) as empty:
        catalog.expand(PipelineScope(ScopeType.PAGE_SELECTION))
    assert empty.value.code == "EMPTY_TARGET_SELECTION"

    with pytest.raises(PipelineError) as missing:
        catalog.expand(PipelineScope(ScopeType.PAGE, selected_ids=("missing",)))
    assert missing.value.code == "TARGET_NOT_FOUND"

    catalog.soft_delete_page("p1")
    with pytest.raises(PipelineError) as deleted:
        catalog.expand(PipelineScope(ScopeType.PAGE, selected_ids=("p1",)))
    assert deleted.value.code == "TARGET_DELETED"


def test_catalog_commit_rechecks_revision_and_lock_before_mutating() -> None:
    catalog = make_catalog()
    target = catalog.current("r1")
    result = catalog.commit_step(
        target_id="r1",
        expected_revisions={"region": "rev-1"},
        expected_lock=target.lock,
        stage_updates={"translate": StageState.COMPLETED},
        revision_updates={"region": "rev-3"},
    )
    assert result.status == "applied"
    assert catalog.current("r1").current_revisions["region"] == "rev-3"
    assert catalog.current("r1").stage("translate") is StageState.COMPLETED

    catalog.update_region("r1", current_revisions={"region": "rev-4"})
    conflict = catalog.commit_step(
        target_id="r1",
        expected_revisions={"region": "rev-3"},
        expected_lock=target.lock,
        stage_updates={"translate": StageState.COMPLETED},
        revision_updates={"region": "rev-5"},
    )
    assert conflict.status == "input_revision_changed"
    assert catalog.current("r1").current_revisions["region"] == "rev-4"


def test_snapshot_provider_returns_independent_frozen_values() -> None:
    provider = InMemorySnapshotProvider(
        settings={"model": {"name": "m"}},
        provider_bindings={"translate": "primary"},
        constraint_snapshot_ref="constraint-rev-1",
        context_policy={"window": "both"},
    )
    first = provider.freeze("run-1", overrides={"model": {"temperature": 0}})
    assert first.settings["model"]["name"] == "m"
    with pytest.raises(TypeError):
        first.settings["model"]["name"] = "changed"

    provider.settings["model"]["name"] = "new"
    second = provider.freeze("run-2")
    assert first.settings["model"]["name"] == "m"
    assert second.settings["model"]["name"] == "new"


def test_pipeline_store_keeps_runs_by_id() -> None:
    store = InMemoryPipelineStore()
    store.put("run-1", object())
    assert store.get("run-1") is not None
    assert store.list_ids() == ("run-1",)
