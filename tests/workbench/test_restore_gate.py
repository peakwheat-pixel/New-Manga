"""TASK-057 Q-008 前置① / TASK-061 R-004: the restore gate, three parts.

1. ``beginRestore`` refuses while a run worker is executing (the gate's
   "drained" premise, checked VM-side);
2. while latched, every workbench start path is rejected — no run
   object, the controller stays idle, the error lands on the typed
   command-error surface (``any_in_transaction()`` is a snapshot, not an
   admission gate: this latch is what keeps the gate closed);
3. ``endRestore`` releases the latch — normal runs start again.

Pre-fix discriminating evidence (no latch existed at all —
``beginRestore`` raised AttributeError and startRun had no rejection
path): ``verification/TASK-057/pre-fix-probes/pre-fix-r004-latch-run1.log``.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)

import pytest


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app


def _vm():
    from workbench_helpers import make_pipeline, make_vm

    service, _catalog = make_pipeline(pages=[("p1", 1), ("p2", 2)])
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    return vm


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


def test_latched_restore_rejects_every_start_path(qapp):
    """Gate part 3: while the latch holds, no start path creates a run —
    the rejection lands on the typed error surface."""
    vm = _vm()
    assert vm.beginRestore() is True
    try:
        for start in (vm.startTranslateAll, vm.startTranslateUntranslated):
            start()
            assert vm._controller.is_running is False, (
                "a run started while the restore latch was engaged")
            assert vm._run is None
        assert "恢复进行中" in vm.commandErrorText, (
            f"rejection not surfaced as restore-latch error: "
            f"{vm.commandErrorText!r}")
    finally:
        vm.endRestore()
    assert vm._restore_in_progress is False


def test_end_restore_releases_the_latch(qapp):
    """After ``endRestore`` the workbench starts runs normally again."""
    vm = _vm()
    assert vm.beginRestore() is True
    vm.endRestore()
    assert vm._restore_in_progress is False
    vm.startTranslateAll()
    try:
        assert vm._controller.is_running is True
    finally:
        assert vm.shutdown() is True
