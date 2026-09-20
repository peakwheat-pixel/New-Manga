"""TASK-057 Q-008 前置① / TASK-061 R-004: the restore gate, three parts.

1. ``beginRestore`` refuses while a run worker is executing (the gate's
   "drained" premise, checked VM-side);
2. while latched, EVERY worker-starting path is rejected with no worker
   born and the refusal on the typed command-error surface.  Review
   R-001 (head b0e4cb1) proved the shipped case only covered the
   ``_start_run`` choke point while ``continueRun``/``restartRun``/
   ``retryFailedPages`` each reached ``controller.start`` unguarded —
   these cases now enumerate all four faces for real (real states:
   PAUSED for continue, INTERRUPTED/FAILED targets for restart/retry).
   The latch itself lives at the sole worker birthplace
   (``RunController.start`` via ``set_restore_latch``), so a future
   fifth call site cannot silently bypass it;
3. ``endRestore`` releases the latch — normal runs start again — and
   ``restoreGate()`` releases it even when the restore body raises
   (review R-002).

Pre-fix discriminating evidence (no latch existed at all —
``beginRestore`` raised AttributeError and startRun had no rejection
path): ``verification/TASK-057/pre-fix-probes/pre-fix-r004-latch-run1.log``.
Mid-fix discriminating evidence (latch only on one of four faces —
``continueRun`` birthed a worker while latched):
``verification/TASK-057/review-b0e4cb1/probe-gate-b0e4cb1-run1.log``
(Qoder, non-author).
"""

from __future__ import annotations

import time
import types

import workbench_helpers  # noqa: F401  (sys.path injection: src + tests)

import pytest

from domain.tasks.models import (
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    ScopeType,
    TargetType,
)


def _vm():
    from workbench_helpers import make_pipeline, make_vm

    service, _catalog = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    return vm


def _pump(qapp, predicate, timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not predicate():
        qapp.processEvents()
        time.sleep(0.005)
    return predicate()


def _pending_pair(vm):
    """Two genuinely PENDING runs from the real planner on the VM's own
    (clean) in-memory store — the shape the production planner yields
    when unfinished work exists.  The first plays the interrupted/retried
    run, the second the fresh run the control call hands back."""
    runs = []
    for _ in range(2):
        run = vm._pipeline.create_run(
            CommandType.TRANSLATE_ALL.value,
            PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
        )
        vm._pipeline.plan_run(run.run_id)
        assert run.status is PipelineRunStatus.PENDING
        runs.append(run)
    return runs[0], runs[1]


def _run_to_settled(vm, qapp, *, pause: bool) -> str:
    """Start a real run, optionally pause it, drain the worker; the run
    object stays (PAUSED resumable, or terminal)."""
    vm.startTranslateAll()
    try:
        assert _pump(qapp, lambda: vm._controller.is_running, 20) is True
        if pause:
            vm.pauseRun()
        assert _pump(qapp, lambda: not vm._controller.is_running, 40) is True
    finally:
        assert vm.shutdown() is True
    return vm._run.status.value


def _assert_refused(vm) -> None:
    """The two claims of gate part 3, per face: no worker born + the
    typed restore-latch error surface."""
    assert vm._controller.is_running is False, (
        "a run worker was born while the restore latch was engaged")
    assert "恢复进行中" in vm.commandErrorText, (
        f"rejection not surfaced as restore-latch error: "
        f"{vm.commandErrorText!r}")


def test_begin_restore_refuses_while_a_run_is_active(qapp):
    """Gate part 1: an executing run worker means NOT drained — the
    maintenance entry must not engage the latch."""
    vm = _vm()
    vm.startTranslateAll()
    try:
        assert vm._controller.is_running is True
        assert vm.beginRestore() is False, (
            "restore gate engaged while a run worker was alive")
        assert vm._restore_in_progress is False
    finally:
        assert vm.shutdown() is True


def test_latched_start_translate_all_rejected(qapp):
    """Face 1 (``_start_run``): rejection happens BEFORE create_run —
    no run object, no worker."""
    vm = _vm()
    assert vm.beginRestore() is True
    try:
        vm.startTranslateAll()
        _assert_refused(vm)
        assert vm._run is None
    finally:
        vm.endRestore()
    assert vm._restore_in_progress is False


def test_latched_start_translate_untranslated_rejected(qapp):
    """Face 2 (same ``_start_run`` choke, other entry): rejected too."""
    vm = _vm()
    assert vm.beginRestore() is True
    try:
        vm.startTranslateUntranslated()
        _assert_refused(vm)
        assert vm._run is None
    finally:
        vm.endRestore()


def test_latched_continue_run_rejected(qapp):
    """R-009 face 3: reject before the PAUSED run is mutated."""
    vm = _vm()
    status = _run_to_settled(vm, qapp, pause=True)
    assert status in {"paused", "interrupted"}, (
        f"expected a resumable run, got {status!r}")
    original_run = vm._run
    original_status = original_run.status
    assert vm.beginRestore() is True
    try:
        vm.continueRun()
        _assert_refused(vm)
        assert vm._run is original_run
        assert vm._run.status is original_status
    finally:
        vm.endRestore()


def test_latched_restart_run_rejected(qapp):
    """R-009 face 4a: reject before restart replaces the current run."""
    vm = _vm()
    interrupted, fresh = _pending_pair(vm)
    vm._run = interrupted
    interrupted.status = PipelineRunStatus.INTERRUPTED
    vm._pipeline.control_run = (
        lambda _rid, _action, _new=fresh.run_id:
        types.SimpleNamespace(new_run_id=_new))
    assert vm.beginRestore() is True
    try:
        vm.restartRun()
        _assert_refused(vm)
        assert vm._run is interrupted
        assert vm._run.status is PipelineRunStatus.INTERRUPTED
    finally:
        vm.endRestore()


def test_latched_retry_failed_pages_rejected(qapp):
    """R-009 face 4b: reject before retry replaces the current run."""
    vm = _vm()
    retried, fresh = _pending_pair(vm)
    vm._run = retried
    page_task = next(
        t for t in retried.tasks if t.target_type is TargetType.PAGE
    )
    page_task.status = PipelineTaskStatus.FAILED
    vm._pipeline.retry_failed_targets = lambda _rid: fresh
    assert vm.beginRestore() is True
    try:
        vm.retryFailedPages()
        _assert_refused(vm)
        assert vm._run is retried
        assert page_task.status is PipelineTaskStatus.FAILED
    finally:
        vm.endRestore()


def test_end_restore_releases_the_latch(qapp):
    """After ``endRestore`` the workbench starts runs normally again."""
    vm = _vm()
    assert vm.beginRestore() is True
    vm.endRestore()
    assert vm._restore_in_progress is False
    assert vm._controller.admission_closed is False
    vm.startTranslateAll()
    try:
        assert vm._controller.is_running is True
    finally:
        assert vm.shutdown() is True


def test_restore_gate_releases_the_latch_when_the_body_raises(qapp):
    """Review R-002: an exception inside ``restoreGate()`` must release
    the latch — a failed restore must not wedge every start path."""
    vm = _vm()
    with pytest.raises(RuntimeError, match="restore body exploded"):
        with vm.restoreGate():
            assert vm._restore_in_progress is True
            assert vm._controller.admission_closed is True
            raise RuntimeError("restore body exploded")
    assert vm._restore_in_progress is False
    assert vm._controller.admission_closed is False
    vm.startTranslateAll()
    try:
        assert vm._controller.is_running is True, (
            "the latch was not released after the restore body raised")
    finally:
        assert vm.shutdown() is True


def test_restore_gate_rejects_nested_entry_without_releasing_outer_latch(qapp):
    """R-008: an inner gate cannot release the still-active outer gate."""
    vm = _vm()
    try:
        with vm.restoreGate():
            with pytest.raises(RuntimeError, match="cannot enter the restore gate"):
                with vm.restoreGate():
                    pass
            assert vm._restore_in_progress is True
            assert vm._controller.admission_closed is True
    finally:
        assert vm.shutdown() is True


def test_restore_gate_refuses_entry_while_a_run_is_active(qapp):
    """``restoreGate()`` must not run its body un-latched: entering while
    a worker is alive raises instead of yielding without the latch."""
    vm = _vm()
    vm.startTranslateAll()
    try:
        with pytest.raises(RuntimeError, match="cannot enter the restore gate"):
            with vm.restoreGate():
                pass  # the body must never run
        assert vm._restore_in_progress is False
    finally:
        assert vm.shutdown() is True
