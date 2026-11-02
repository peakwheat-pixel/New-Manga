"""RUN-STORE-CACHE-RACE-FIX-1: store-level unit tests for the shared run cache.

Covers:
  AC1  ``refresh()`` / ``get_run_snapshot(fresh=True)`` is a *view read* and must
       never replace the execution cache entry (or return the cached object).
  AC2  ``run_json`` writes are owner/revision guarded: a stale snapshot captured
       before a newer commit is rejected instead of silently overwriting it
       (last-writer-wins).

These tests fail on the pre-fix implementation and pass after the fix; the
end-to-end concurrent reproduction lives in
``tests/pipeline/test_regionless_rebinding.py::test_projection_fresh_polling_does_not_corrupt_execution``
and ``verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py``.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.tasks.store import InMemoryPipelineStore  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineError,
    PipelineRun,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
)
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.pipeline import SqlitePipelineStore  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402


def _run(run_id: str = "run-cache-1") -> PipelineRun:
    return PipelineRun(
        run_id=run_id,
        command_type=CommandType.REOCR_ALL,
        scope=PipelineScope(ScopeType.PAGE, selected_ids=("page-1",)),
        requested_targets=("page-1",),
        targets=(),
        settings_snapshot={},
        provider_binding_snapshot={},
        constraint_snapshot_ref=None,
        context_policy={},
    )


@pytest.fixture()
def store(tmp_path: Path) -> SqlitePipelineStore:
    conn, _ = open_database(
        tmp_path / "app.db",
        latest_known_schema_version=default_migrations()[-1].schema_version,
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    try:
        yield SqlitePipelineStore(conn)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# AC1: view reads must not replace the execution cache
# ---------------------------------------------------------------------------


def test_refresh_returns_detached_view_and_keeps_execution_cache(store: SqlitePipelineStore) -> None:
    run = _run()
    store.put(run.run_id, run)
    owner = store.get(run.run_id)
    assert owner is not None

    view = store.refresh(run.run_id)

    assert view is not None
    assert view is not owner, "refresh() must return an independent read object"
    assert store.get(run.run_id) is owner, "refresh() must not replace the cached execution object"


def test_fresh_view_sees_committed_state_without_touching_owner(store: SqlitePipelineStore) -> None:
    run = _run()
    store.put(run.run_id, run)
    owner = store.get(run.run_id)
    assert owner is not None

    # the owner mutates in memory but has not persisted yet
    owner.status = PipelineRunStatus.RUNNING
    view = store.refresh(run.run_id)

    assert view is not None
    assert view.status is PipelineRunStatus.PENDING, "view must reflect durable state, not owner memory"
    assert owner.status is PipelineRunStatus.RUNNING
    assert store.get(run.run_id) is owner


def test_in_memory_refresh_returns_independent_view() -> None:
    store = InMemoryPipelineStore()
    store.put("run-1", _run("run-1"))
    owner = store.get("run-1")
    view = store.refresh("run-1")
    assert view is not None and owner is not None
    assert view is not owner
    view.status = PipelineRunStatus.RUNNING
    assert owner.status is PipelineRunStatus.PENDING
    assert store.get("run-1") is owner


def test_get_run_snapshot_fresh_is_read_only(store: SqlitePipelineStore) -> None:
    """Service-level AC1: ``get_run_snapshot(fresh=True)`` must not swap the cache."""
    from application.tasks.service import PipelineService

    service = PipelineService(catalog=_NoopCatalog(), store=store)
    run = _run()
    store.put(run.run_id, run)
    owner = store.get(run.run_id)
    snapshot = service.get_run_snapshot(run.run_id, fresh=True)
    assert snapshot is not owner
    assert store.get(run.run_id) is owner


class _NoopCatalog:
    def expand(self, scope):  # pragma: no cover - only the store path is exercised
        raise AssertionError("catalog is not used by get_run_snapshot")


# ---------------------------------------------------------------------------
# AC2: owner / revision CAS on run_json writes
# ---------------------------------------------------------------------------


def test_stale_snapshot_write_is_rejected(store: SqlitePipelineStore) -> None:
    run = _run()
    store.put(run.run_id, run)
    owner = store.get(run.run_id)
    assert owner is not None
    stale = store.refresh(run.run_id)  # snapshot taken before the next commit
    assert stale is not None

    owner.status = PipelineRunStatus.COMPLETED
    store.put(run.run_id, owner)  # the current owner commits

    stale.status = PipelineRunStatus.FAILED
    with pytest.raises(PipelineError) as error:
        store.put(run.run_id, stale)
    assert error.value.code == "STALE_RUN_SNAPSHOT"

    persisted = store.get(run.run_id)
    assert persisted is not None
    assert persisted.status is PipelineRunStatus.COMPLETED, "stale write must not clobber the commit"


def test_repeated_owner_writes_are_accepted(store: SqlitePipelineStore) -> None:
    run = _run()
    store.put(run.run_id, run)
    owner = store.get(run.run_id)
    assert owner is not None
    for index in range(3):
        owner.terminal_step_units = index + 1
        owner.status = PipelineRunStatus.RUNNING
        store.put(run.run_id, owner)
    persisted = store.get(run.run_id)
    assert persisted is not None
    assert persisted.terminal_step_units == 3
    assert persisted.status is PipelineRunStatus.RUNNING


def test_stale_write_inside_transaction_is_rejected(store: SqlitePipelineStore) -> None:
    run = _run()
    store.put(run.run_id, run)
    owner = store.get(run.run_id)
    assert owner is not None
    stale = store.refresh(run.run_id)
    assert stale is not None

    owner.status = PipelineRunStatus.COMPLETED
    store.put(run.run_id, owner)

    stale.status = PipelineRunStatus.FAILED
    with pytest.raises(PipelineError) as error:
        store._conn.execute("BEGIN IMMEDIATE")
        try:
            store.write_in_current_transaction(stale)
        finally:
            store._conn.rollback()
    assert error.value.code == "STALE_RUN_SNAPSHOT"
    assert store.get(run.run_id).status is PipelineRunStatus.COMPLETED
