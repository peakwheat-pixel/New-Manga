"""DIAG-READING-EXPORT-001 probe 1 (read-only, two phases, one probe):
export terminal-signal delivery window versus the `running` flag.

Question (falsifiable): can an observer see ``vm.running is False`` before the
``exportFinished`` slot connected from the main thread has run -- i.e. can the
exact assertion pattern of ``test_start_export_completes_and_updates_history``
fail with ``running=False, finished=[]`` while ``statusMessage`` already says
导出完成 and ``history`` already has the row (the historical shape)?

Shape of the race, from source (no editing, read-only):
  * the export runs on a ``threading.Thread`` (`ExportViewModel.startExport`);
  * ``_finish`` runs on that worker thread and does
    ``changed.emit() -> exportFinished.emit(summary) -> self._running = False``;
  * the test/main-thread slot is therefore invoked through Qt's **queued**
    delivery, while the wait predicate in ``pump_until`` reads the plain
    ``running`` attribute -- no event delivery required.

Phase 1 replays the test pattern in isolation. Phase 2 replays it while the
main thread runs a busy event handler inside ``processEvents`` (the condition a
full-suite run creates: a loaded main-thread event queue), which is the
prediction that would widen the window. A probe-local subclass only timestamps
after ``_finish`` returns, to measure the queued-delivery latency.

Run with the frozen interpreter:
  python verification/DIAG-READING-EXPORT-001/probe-export-signal-window.py [phase1_iters] [phase2_iters]
"""

from __future__ import annotations

import statistics
import sys
import tempfile
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from PySide6.QtCore import QTimer  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402

from application.export import (  # noqa: E402
    ExportPage,
    ExportService,
    JsonHistoryDocumentStore,
    file_bytes_provider,
)
from ui.viewmodels.export.viewmodel import ExportViewModel  # noqa: E402

PHASE1 = int(sys.argv[1]) if len(sys.argv) > 1 else 400
PHASE2 = int(sys.argv[2]) if len(sys.argv) > 2 else 200
MAIN_THREAD = threading.get_ident()
BUSY_MS = 2.0  # time spent inside one processEvents() call in phase 2


class InstrumentedVM(ExportViewModel):
    """Probe-local subclass: records when the worker cleared `running`.

    The product module is not modified and nothing is monkeypatched; the
    override only timestamps after the real implementation returns.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.probe_flag_clear_time: float | None = None

    def _finish(self, summary):  # noqa: D102 - probe instrumentation
        super()._finish(summary)
        self.probe_flag_clear_time = time.monotonic()


def pump_until(app, condition, timeout=5.0):
    """Verbatim copy of the test's wait pattern (test_viewmodels.py:34-48)."""

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.processEvents()
        if condition():
            return True
        time.sleep(0.02)
    return condition()


def build_vm(lab: Path) -> InstrumentedVM:
    """Mirror the test fixtures: current translated pages, so the default
    ``translated`` mode takes the success path (`_finish`)."""

    page_dir = lab / "pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    pages = []
    for index in range(3):
        path = page_dir / f"page_{index}.png"
        path.write_bytes(f"PNG-{index}".encode())
        translated = page_dir / f"page_{index}_translated.png"
        translated.write_bytes(f"PNG-trans-{index}".encode())
        pages.append(
            ExportPage(
                page_id=f"p{index}",
                filename=path.name,
                source_provider=file_bytes_provider(str(path)),
                translated_provider=file_bytes_provider(str(translated)),
                translated_revision_id=f"rev-{index}",
                current_translated_revision_id=f"rev-{index}",
                text=f"第 {index} 页译文",
            )
        )
    service = ExportService(JsonHistoryDocumentStore(lab / "export_history.json"))
    return InstrumentedVM(
        service,
        lambda: list(pages),
        book_id="b",
        chapter_id="c",
        output_dir=str(lab / "out"),
    )


def run_phase(app, lab: Path, iterations: int, label: str, busy: bool) -> dict:
    misses = 0
    delivered_by_extra_pump = 0
    completed = 0
    failed = 0
    slot_threads: set[str] = set()
    orders = {"slot_before_flag": 0, "slot_after_flag": 0}
    latencies_us: list[float] = []
    first_miss = None

    for iteration in range(iterations):
        vm = build_vm(lab)
        vm.setOutputPath(str(lab / "out" / f"{label}-{iteration}.zip"))
        state = {"arrived": False, "flag_seen": None, "slot_time": None, "thread": None}
        errors: list[str] = []

        def slot(summary, state=state):
            state["arrived"] = True
            state["slot_time"] = time.monotonic()
            state["thread"] = threading.get_ident()

        vm.exportFinished.connect(slot)
        vm.exportFailed.connect(lambda message, errors=errors: errors.append(message))

        # phase 2 stimulus: keep the main thread busy INSIDE processEvents
        busy_stop = {"until": time.monotonic() + 3.0}

        def busy_handler():
            if not busy or time.monotonic() > busy_stop["until"]:
                return
            end = time.monotonic() + BUSY_MS / 1000.0
            while time.monotonic() < end:
                pass
            QTimer.singleShot(0, busy_handler)

        if busy:
            QTimer.singleShot(0, busy_handler)

        vm.startExport()
        ok = pump_until(app, lambda: not vm.running)
        if not ok:
            print(f"{label} iteration {iteration}: wait timed out")
            continue
        state["flag_seen"] = time.monotonic()
        if errors:
            failed += 1
            continue
        completed += 1

        # ---- the test's very next statement, with no further pumping ----
        if not state["arrived"]:
            misses += 1
            if first_miss is None:
                first_miss = (
                    f"iteration={iteration} running={vm.running!r} "
                    f"statusMessage={vm.statusMessage!r} history={len(vm.history)}"
                )
            app.processEvents()
            if state["arrived"]:
                delivered_by_extra_pump += 1

        if state["thread"] is not None:
            slot_threads.add("main" if state["thread"] == MAIN_THREAD else "worker/other")
        if state["arrived"] and state["slot_time"] and state["flag_seen"]:
            orders[
                "slot_before_flag" if state["slot_time"] <= state["flag_seen"] else "slot_after_flag"
            ] += 1
        if state["arrived"] and state["slot_time"] and vm.probe_flag_clear_time:
            latencies_us.append((state["slot_time"] - vm.probe_flag_clear_time) * 1e6)
        vm.cancelExport()

    def stat(values):
        if not values:
            return "n/a"
        ordered = sorted(values)
        return (
            f"min={ordered[0]:.1f} p50={statistics.median(ordered):.1f} "
            f"p95={ordered[int(len(ordered) * 0.95) - 1]:.1f} max={ordered[-1]:.1f}"
        )

    return {
        "label": label,
        "iterations": iterations,
        "completed": completed,
        "failed": failed,
        "misses": misses,
        "delivered_by_extra_pump": delivered_by_extra_pump,
        "slot_threads": sorted(slot_threads),
        "orders": orders,
        "first_miss": first_miss,
        "latency_us": stat(latencies_us),
    }


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    with tempfile.TemporaryDirectory() as temp:
        lab = Path(temp)
        results = [
            run_phase(app, lab, PHASE1, "isolated", busy=False),
            run_phase(app, lab, PHASE2, "busy-main-thread", busy=True),
        ]
    for result in results:
        print(f"=== phase: {result['label']} ===")
        print(f"  replays of the test wait pattern : {result['iterations']}")
        print(f"  completed / failed               : {result['completed']} / {result['failed']}")
        print(f"  MISSES (running=False, finished=[] immediately after the wait) : {result['misses']}")
        print(f"    delivered by ONE more processEvents                          : {result['delivered_by_extra_pump']}")
        print(f"  slot thread(s)                   : {result['slot_threads']} (main tid={MAIN_THREAD})")
        print(f"  observed ordering                : {result['orders']}")
        print(f"  queued-delivery latency (us)     : {result['latency_us']}")
        if result["first_miss"]:
            print(f"  first miss                       : {result['first_miss']}")
        print()
    verdict = (
        "WINDOW DEMONSTRATED -- the running flag can be observed before the terminal signal"
        if any(r["misses"] for r in results)
        else "window not hit in this sample (both phases): signal was always delivered before the flag was observed"
    )
    print("verdict: " + verdict)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
