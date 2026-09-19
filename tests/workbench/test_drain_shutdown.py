"""TASK-060 Q-003: the exit drain reports truth, and close() respects it.

- ``RunController.shutdown`` returns whether the worker thread is really
  gone; a timed-out drain must NOT be reported as drained;
- a PAUSED run is cancelled on shutdown (no session to resume into), but
  the pause→continue product flow is untouched (that path reaps without
  cancelling — pinned by ``test_workbench_viewmodel.py``'s pause tests);
- ``_shutdown_services`` (bootstrap) skips ``conn.close()`` on a
  timed-out drain and reports it on stderr instead of failing silently.
"""

from __future__ import annotations

import sys
from pathlib import Path

import workbench_helpers  # noqa: F401  (sys.path injection)

import pytest


@pytest.fixture(scope="session")
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app


def _slow_vm(pages: int = 8, seconds_per_step: float = 0.05):
    import time

    from application.translation.pipeline.executor import (
        DeterministicStepExecutor,
    )
    from workbench_helpers import make_pipeline, make_vm

    def on_execute(*_a) -> None:
        time.sleep(seconds_per_step)

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, pages + 1)],
        executor=DeterministicStepExecutor(on_execute=on_execute),
    )
    vm = make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    return service, vm


def _pump(qapp, seconds: float) -> None:
    import time

    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        qapp.processEvents()
        time.sleep(0.01)


def test_shutdown_reports_drained_on_a_live_run(qapp):
    """A real wait budget on an active run ends drained: True."""
    _service, vm = _slow_vm()
    vm.startTranslateAll()
    try:
        assert vm._controller.is_running is True
        assert vm.shutdown() is True
        assert vm._controller.is_running is False
    finally:
        vm.shutdown()


def test_shutdown_timeout_is_reported_as_not_drained(qapp):
    """A zero budget cannot drain a live worker: shutdown returns False
    (and the run slot survives — the caller must not treat it as gone)."""
    _service, vm = _slow_vm()
    vm.startTranslateAll()
    _pump(qapp, 0.2)
    try:
        assert vm.shutdown(wait_ms=0) is False
    finally:
        # a real drain still finishes the job (bounded, never force-kills)
        assert vm.shutdown() is True


def test_shutdown_cancels_a_paused_run(qapp):
    """Q-003: on exit there is no session to resume into — a PAUSED run
    must carry the cancel request across the drain."""
    _service, vm = _slow_vm()
    vm.startTranslateAll()
    _pump(qapp, 0.2)
    vm.pauseRun()
    _pump(qapp, 2.0)
    assert vm.taskProgress["run_status"] == "paused"
    assert vm.shutdown() is True
    assert vm._run is not None and vm._run.cancel_requested is True


def test_bootstrap_shutdown_skips_close_and_reports_on_timeout(capsys):
    """The bootstrap exit path must not close the connection under a
    timed-out drain, and must say so on stderr (no silent close)."""
    from types import SimpleNamespace

    from bootstrap.app import _shutdown_services

    calls: list[str] = []
    services = SimpleNamespace(
        workbench=SimpleNamespace(shutdown=lambda: False),
        conn=SimpleNamespace(
            close=lambda: calls.append("close"),
            execute=lambda *_a: calls.append("execute"),
        ),
    )
    _shutdown_services(services)
    assert calls == [], "connection was closed under an undrained worker"
    err = capsys.readouterr().err
    assert "drain timed out" in err, err
    assert sys.stderr is not None
