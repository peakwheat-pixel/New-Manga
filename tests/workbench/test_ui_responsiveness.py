"""UI responsiveness while a pipeline runs (AC-NFR-UI-001, Mock evidence).

``PipelineService.execute_run`` is a synchronous loop; the RunController
must keep it off the GUI thread. These tests prove the GUI thread keeps
servicing timers/events during a slow mock run — they make no claim about
real OCR/translation/inpaint performance.
"""

from __future__ import annotations

import threading
import time

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import make_pipeline, make_vm, wait_until

from PySide6.QtCore import QTimer

from application.translation.pipeline.executor import DeterministicStepExecutor


def test_execute_run_runs_off_the_gui_thread(qapp):
    worker_threads: list[threading.Thread] = []

    def note_thread(step_run, unit, run):
        worker_threads.append(threading.current_thread())
        time.sleep(0.01)

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 5)],
        executor=DeterministicStepExecutor(on_execute=note_thread),
    )
    vm = make_vm(
        service,
        pages=[
            workbench_helpers.FakePage(f"p{i}", "chapter-1", i, f"{i:03d}.jpg")
            for i in range(1, 5)
        ],
    )
    vm.setContext("book-1", "chapter-1", "书", "章")

    main_thread = threading.current_thread()
    finished = []
    vm.runFinished.connect(lambda run_id, status: finished.append(status))

    vm.startTranslateAll()
    assert wait_until(qapp, lambda: bool(finished), timeout_ms=10000)

    # every pipeline step executed on one non-GUI thread (the QThread worker)
    assert worker_threads, "executor must have run"
    assert all(thread is not main_thread for thread in worker_threads), (
        "execute_run must not run on the GUI thread"
    )
    assert len({id(thread) for thread in worker_threads}) == 1
    assert finished == ["completed"]
    vm.shutdown()


def test_gui_thread_stays_alive_during_run(qapp):
    """Heartbeats keep firing while the mock pipeline occupies the worker
    thread; a blocked GUI thread would freeze the counter."""

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 9)],
        executor=DeterministicStepExecutor(
            on_execute=lambda *a: time.sleep(0.03)
        ),
    )
    vm = make_vm(
        service,
        pages=[
            workbench_helpers.FakePage(f"p{i}", "chapter-1", i, f"{i:03d}.jpg")
            for i in range(1, 9)
        ],
    )
    vm.setContext("book-1", "chapter-1", "书", "章")

    heartbeats = []
    timer = QTimer()
    timer.setInterval(25)
    timer.timeout.connect(lambda: heartbeats.append(time.monotonic()))
    timer.start()

    finished = []
    vm.runFinished.connect(lambda run_id, status: finished.append(status))
    vm.startTranslateAll()
    assert wait_until(qapp, lambda: bool(finished), timeout_ms=15000)
    timer.stop()

    # a multi-second-scale run produced many GUI-thread heartbeats
    assert len(heartbeats) >= 8, (
        f"GUI thread serviced only {len(heartbeats)} heartbeats during the run"
    )
    vm.shutdown()


def test_page_switch_remains_possible_while_run_active(qapp):
    """AC-NFR-UI-001 verbatim: 切换 Page / 滚动 while OCR/translation run."""

    service, _ = make_pipeline(
        pages=[(f"p{i}", i) for i in range(1, 13)],
        executor=DeterministicStepExecutor(
            on_execute=lambda *a: time.sleep(0.02)
        ),
    )
    vm = make_vm(
        service,
        pages=[
            workbench_helpers.FakePage(f"p{i}", "chapter-1", i, f"{i:03d}.jpg")
            for i in range(1, 13)
        ],
    )
    vm.setContext("book-1", "chapter-1", "书", "章")

    finished = []
    vm.runFinished.connect(lambda *a: finished.append(True))
    vm.startTranslateAll()

    # switch pages mid-run — must not block or raise
    switched = []
    while not finished:
        target = f"p{(len(switched) % 12) + 1}"
        vm.selectPage(target)
        switched.append(vm.viewerPageId)
        qapp.processEvents()
        if len(switched) > 40:
            break

    assert wait_until(qapp, lambda: bool(finished), timeout_ms=15000)
    assert len(switched) >= 10, "page switching must remain responsive"
    vm.shutdown()
