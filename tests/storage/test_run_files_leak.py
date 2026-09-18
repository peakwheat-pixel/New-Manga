"""TASK-053: TASK-044 leftovers R-03 (target-less run rows accumulate)
and R-04 (un-retryable orphan files after a partial purge) — real SQLite
+ real ManagedFileStorage.

Guarantees under test:

- R-04: the purge file sweep list is persisted *before* the destructive
  step; a file-removal failure leaves a retryable pending entry (not an
  undiscoverable orphan), retry is idempotent, success clears it;
- R-03: target-less runs survive page purges **by policy** (kept for
  audit) and are reclaimed only through the explicit maintenance entry,
  which never touches active (running/paused) runs;
- AC ④ trigger discipline: the schema's trigger set is enumerated and
  the reclaim is proven to coexist with it (no trigger refuses the
  delete).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.pipeline import SqliteRunLedgerMaintenance  # noqa: E402

NOW = "2026-09-19T02:00:00+00:00"

_DOCUMENTED_TRIGGERS = {
    "trg_media_artifacts_current_not_clearable",
    "trg_regions_current_not_clearable",
}


class FlakyRemover:
    """Remover wrapper whose first N real removal attempts fail (the
    transient storage fault of R-04); then it delegates."""

    def __init__(self, inner, failures: int) -> None:
        self._inner = inner
        self._remaining = failures
        self.refused: list[str] = []

    def remove_managed(self, relative_path: str) -> None:
        if self._remaining > 0:
            self._remaining -= 1
            self.refused.append(relative_path)
            raise OSError(f"transient storage fault on {relative_path}")
        self._inner.remove_managed(relative_path)


class FailingPages:
    """Store wrapper whose ``purge_pages`` always fails: the row deletion
    itself is impossible, so the pages stay live with a pending sweep
    already recorded (the first-review R-001 premature-entry scenario)."""

    def __init__(self, inner) -> None:
        self._inner = inner

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def purge_pages(self, page_ids) -> None:
        raise OSError("simulated purge_pages failure: rows stay live")


def _insert_run(conn, run_id: str, *, status: str = "completed") -> None:
    conn.execute(
        "INSERT INTO pipeline_runs (run_id, command_type, scope_type,"
        " requested_targets_json, settings_snapshot_json,"
        " provider_binding_snapshot_json, context_policy_json, status,"
        " run_json, updated_at)"
        " VALUES (?, 'translate', 'chapter', '[]', '{}', '{}', '{}', ?, '{}', ?)",
        (run_id, status, NOW),
    )


def _insert_run_target(conn, run_id: str, page_id: str, order: int) -> None:
    conn.execute(
        "INSERT INTO pipeline_run_targets (run_target_id, pipeline_run_id,"
        " target_id, target_type, page_id, target_order, snapshot_json)"
        " VALUES (?, ?, ?, 'page', ?, ?, '{}')",
        (f"{run_id}-t{order}", run_id, page_id, page_id, order),
    )


def _run_ids(conn) -> set[str]:
    return {row[0] for row in conn.execute("SELECT run_id FROM pipeline_runs")}


class TestR04RetryablePendingPurge:
    def test_file_failure_leaves_retryable_pending_entry(
        self, trash_workspace
    ) -> None:
        """Discriminating case: against the pre-fix tree the pending entry
        does not exist, so the assertions below cannot pass (the orphan was
        undiscoverable once the batch left the ledger)."""
        workspace = trash_workspace
        service = workspace["service"]
        page = workspace["make_page"]("p1", b"payload-one")
        batch = service.soft_delete_pages("chapter-1", ("p1",))
        flaky = FlakyRemover(workspace["storage"], failures=1)
        failing_service = workspace["with_remover"](flaky)

        with pytest.raises(OSError):
            failing_service.purge_batch(batch.batch_id)

        # rows and the ledger entry are gone, but the orphan is *rediscoverable*
        assert page.page_id not in workspace["live_page_ids"]()
        assert service.pending_purge_count() == 1
        pending = workspace["read_pending"]()
        assert len(pending) == 1
        assert pending[0]["batch_id"] == batch.batch_id
        assert pending[0]["targets"] == [page.managed_original_ref]
        assert (workspace["managed"] / page.managed_original_ref).is_file()

        # retry with the real remover: idempotent completion
        assert service.retry_pending_purges() == 1
        assert service.pending_purge_count() == 0
        assert not (workspace["managed"] / page.managed_original_ref).exists()
        # the user source file outside the managed root is untouched
        assert workspace["user_source"].read_bytes() == b"USER SOURCE BYTES"

    def test_retry_is_idempotent_when_files_are_already_gone(
        self, trash_workspace
    ) -> None:
        workspace = trash_workspace
        service = workspace["service"]
        page = workspace["make_page"]("p2", b"payload-two")
        batch = service.soft_delete_pages("chapter-1", ("p2",))
        # the real flow at this point: rows gone, batch already out of the
        # ledger, files removed — but the entry-clearing write was lost
        workspace["storage"].remove_managed(page.managed_original_ref)
        service._record_pending_purge(batch.batch_id, [page.managed_original_ref])
        service._drop_batch(batch.batch_id)

        assert service.retry_pending_purges() == 1
        assert service.pending_purge_count() == 0

    def test_successful_purge_clears_its_pending_entry(
        self, trash_workspace
    ) -> None:
        workspace = trash_workspace
        service = workspace["service"]
        workspace["make_page"]("p3", b"payload-three")
        batch = service.soft_delete_pages("chapter-1", ("p3",))

        service.purge_batch(batch.batch_id)

        assert service.pending_purge_count() == 0

    def test_retry_skips_premature_entry_while_rows_are_still_live(
        self, trash_workspace
    ) -> None:
        """First-review R-001 guard: when the failure happened *before* the
        rows were deleted (purge_pages itself failed), the batch is still in
        the ledger and its pages are alive — the pending entry is premature
        and a retry must NOT remove the live pages' files. The real purge
        later overwrites the same-id entry and completes the sweep."""
        workspace = trash_workspace
        service = workspace["service"]
        page = workspace["make_page"]("p9", b"payload-nine")
        batch = service.soft_delete_pages("chapter-1", ("p9",))

        from application.maintenance import TrashService
        from application.maintenance.trash import _JsonTrashManifest

        row_fault_service = TrashService(
            FailingPages(workspace["repository"]),
            workspace["storage"],
            _JsonTrashManifest(workspace["manifest_path"]),
        )
        with pytest.raises(OSError):
            row_fault_service.purge_batch(batch.batch_id)

        assert service.pending_purge_count() == 1
        # the guard: retry skips the premature entry, live file untouched
        assert service.retry_pending_purges() == 0
        assert service.pending_purge_count() == 1
        assert (workspace["managed"] / page.managed_original_ref).is_file()
        # the page ROW is still there (soft-deleted, never hard-purged)
        row_left = workspace["conn"].execute(
            "SELECT COUNT(*) FROM pages WHERE page_id = ?", (page.page_id,)
        ).fetchone()[0]
        assert row_left == 1

        # the real purge overwrites the same-id entry and completes it
        service.purge_batch(batch.batch_id)
        assert service.pending_purge_count() == 0
        assert not (workspace["managed"] / page.managed_original_ref).exists()


class TestR03TargetlessRuns:
    def test_targetless_run_survives_page_purge_by_policy(
        self, trash_workspace
    ) -> None:
        """Pinning case (declared non-discriminating): page deletion already
        removed the run's target rows *before* this slice; the run row is
        deliberately kept (TASK-044 ruling — a run spans pages)."""
        workspace = trash_workspace
        service = workspace["service"]
        conn = workspace["conn"]
        page = workspace["make_page"]("p4", b"payload-four")
        _insert_run(conn, "run-1")
        with conn:
            _insert_run_target(conn, "run-1", page.page_id, 0)

        batch = service.soft_delete_pages("chapter-1", (page.page_id,))
        service.purge_batch(batch.batch_id)

        assert "run-1" in _run_ids(conn)
        maintenance = SqliteRunLedgerMaintenance(conn)
        assert maintenance.count_targetless_runs() == 1

    def test_purge_targetless_runs_reclaims_and_cascades(
        self, trash_workspace
    ) -> None:
        workspace = trash_workspace
        conn = workspace["conn"]
        page_a = workspace["make_page"]("p5", b"five")
        page_b = workspace["make_page"]("p6", b"six")
        # run-2 keeps a live target (page_b) and must survive;
        # run-1's only target (page_a) will be purged away
        _insert_run(conn, "run-1", status="failed")
        _insert_run(conn, "run-2")
        with conn:
            _insert_run_target(conn, "run-1", page_a.page_id, 0)
            _insert_run_target(conn, "run-2", page_b.page_id, 0)

        maintenance = SqliteRunLedgerMaintenance(conn)
        assert maintenance.count_targetless_runs() == 0

        service = workspace["service"]
        batch = service.soft_delete_pages("chapter-1", (page_a.page_id,))
        service.purge_batch(batch.batch_id)

        assert maintenance.count_targetless_runs() == 1
        assert maintenance.purge_targetless_runs() == 1
        assert _run_ids(conn) == {"run-2"}
        # cascade took the task/step children with the run (none here), and
        # the live run's target is untouched
        remaining_targets = conn.execute(
            "SELECT COUNT(*) FROM pipeline_run_targets"
        ).fetchone()[0]
        assert remaining_targets == 1
        assert maintenance.purge_targetless_runs() == 0

    def test_active_targetless_run_is_never_reclaimed(
        self, trash_workspace
    ) -> None:
        workspace = trash_workspace
        conn = workspace["conn"]
        page = workspace["make_page"]("p7", b"seven")
        _insert_run(conn, "run-active", status="running")
        _insert_run(conn, "run-done", status="failed")
        with conn:
            _insert_run_target(conn, "run-active", page.page_id, 0)
            _insert_run_target(conn, "run-done", page.page_id, 1)

        service = workspace["service"]
        batch = service.soft_delete_pages("chapter-1", (page.page_id,))
        service.purge_batch(batch.batch_id)

        maintenance = SqliteRunLedgerMaintenance(conn)
        assert maintenance.count_targetless_runs() == 2
        assert maintenance.purge_targetless_runs() == 1
        assert _run_ids(conn) == {"run-active"}


class TestTriggerDiscipline:
    def test_documented_triggers_survive_and_never_refuse_the_reclaim(
        self, trash_workspace
    ) -> None:
        """AC ④: the sqlite_master trigger set is enumerated before and
        after the reclaim; the delete succeeds with enforcement on."""
        workspace = trash_workspace
        conn = workspace["conn"]

        def triggers() -> set[str]:
            return {
                row[0]
                for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'trigger'"
                )
            }

        assert triggers() == _DOCUMENTED_TRIGGERS

        page = workspace["make_page"]("p8", b"eight")
        _insert_run(conn, "run-3", status="failed")
        with conn:
            _insert_run_target(conn, "run-3", page.page_id, 0)
        service = workspace["service"]
        batch = service.soft_delete_pages("chapter-1", (page.page_id,))
        service.purge_batch(batch.batch_id)

        maintenance = SqliteRunLedgerMaintenance(conn)
        assert maintenance.purge_targetless_runs() == 1
        # both documented triggers still exist and nothing refused the deletes
        assert triggers() == _DOCUMENTED_TRIGGERS
