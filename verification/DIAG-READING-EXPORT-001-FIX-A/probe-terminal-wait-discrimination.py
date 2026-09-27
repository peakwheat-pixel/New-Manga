"""DIAG-READING-EXPORT-001-FIX-A discrimination probe (read-only).

Question (falsifiable, three phases):
  A. With the OLD wait predicate (`not vm.running`), does the busy-main-thread
     stimulus still reproduce the historical miss shape
     (`running=False` observed while the `exportFinished` slot has not run)?
     Expected: misses > 0 (the fixed window DIAG-READING-EXPORT-001 measured
     at 26/200; each miss corresponds to the exact historical assertion
     failure `len(finished) == 1` with `statusMessage` already complete).
  B. With the NEW wait predicate (`not vm.running and finished`), is the same
     stimulus clean?  Expected: misses == 0 over >= 200 replays.
  C. Fault injection: a probe-local BrokenVM whose `_finish` clears `running`
     but never emits `exportFinished` (the controlled historical shape).  The
     NEW predicate must time out and report "terminal not reached" every time
     -- proving the fixed wait did not learn to accept a missing signal.

No product or test file is edited or monkeypatched; only probe-local
subclasses timestamp/override behaviour inside this file.  Run with the
frozen interpreter:

  python verification/DIAG-READING-EXPORT-001-FIX-A/probe-terminal-wait-discrimination.py [old_iters] [new_iters] [broken_iters]
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

OLD_ITERS = int(sys.argv[1]) if len(sys.argv) > 1 else 200
NEW_ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 200
BROKEN_ITERS = int(sys.argv[3]) if len(sys.argv) > 3 else 2
MAIN_THREAD = threading.get_ident()
BUSY_MS = 2.0  # time spent inside one processEvents() call (busy stimulus)


class TimestampedVM(ExportViewModel):
    """Probe-local subclass: timestamps after the real _finish returns."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.probe_flag_clear_time: float | None = None

    def _finish(self, summary):  # noqa: D102
        super()._finish(summary)
        self.probe_flag_clear_time = time.monotonic()


class BrokenVM(ExportViewModel):
    """Fault injection: clears `running` without ever emitting the terminal
    signal (the controlled historical shape).  Probe-local only."""

    def _finish(self, summary) -> None:  # noqa: D102
        status = summary.get("status", "")
        self._status = f"导出完成：{summary.get('output_path', '')}" if status == "completed" else f"导出状态：{status}"
        self.changed.emit()
        self._running = False
        self.changed.emit()


def pump_until(app, condition, timeout=5.0):
    """Verbatim copy of the test's wait pattern (test_viewmodels.py:34-48)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        app.processEvents()
        if condition():
            return True
        time.sleep(0.02)
    return condition()


def build_vm(vm_cls, lab: Path) -> ExportViewModel:
    """Mirror the test fixtures: translated pages take the success path."""
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
    return vm_cls(
        service,
        lambda: list(pages),
        book_id="b",
        chapter_id="c",
        output_dir=str(lab / "out"),
    )


def run_phase(app, lab: Path, vm_cls, iterations: int, label: str, predicate_kind: str) -> dict:
    misses = 0
    completed = 0
    detected_failures = 0
    first_miss = None
    latencies_us: list[float] = []

    for iteration in range(iterations):
        vm = build_vm(vm_cls, lab)
        vm.setOutputPath(str(lab / "out" / f"{label}-{iteration}.zip"))
        state = {"arrived": False, "slot_time": None}

        def slot(summary, state=state):
            state["arrived"] = True
            state["slot_time"] = time.monotonic()

        vm.exportFinished.connect(slot)

        busy_stop = {"until": time.monotonic() + 3.0}

        def busy_handler():
            if time.monotonic() > busy_stop["until"]:
                return
            end = time.monotonic() + BUSY_MS / 1000.0
            while time.monotonic() < end:
                pass
            QTimer.singleShot(0, busy_handler)

        QTimer.singleShot(0, busy_handler)

        vm.startExport()
        if predicate_kind == "old":
            ok = pump_until(app, lambda: not vm.running)
        else:
            ok = pump_until(app, lambda: not vm.running and state["arrived"])

        if predicate_kind == "broken":
            if not ok:
                detected_failures += 1
            else:
                misses += 1  # a never-emitted signal was accepted: BAD
            continue

        if not ok:
            print(f"{label} iteration {iteration}: wait timed out")
            continue
        completed += 1
        if not state["arrived"]:
            misses += 1
            if first_miss is None:
                first_miss = (
                    f"iteration={iteration} running={vm.running!r} "
                    f"statusMessage={vm.statusMessage!r} history={len(vm.history)}"
                )
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
        "misses": misses,
        "detected_failures": detected_failures,
        "first_miss": first_miss,
        "latency_us": stat(latencies_us),
    }


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    with tempfile.TemporaryDirectory() as temp:
        lab = Path(temp)
        old = run_phase(app, lab, TimestampedVM, OLD_ITERS, "old-predicate-busy", "old")
        new = run_phase(app, lab, TimestampedVM, NEW_ITERS, "new-predicate-busy", "new")
        broken = run_phase(app, lab, BrokenVM, BROKEN_ITERS, "broken-vm-fault-injection", "broken")

    for r in (old, new, broken):
        print(f"=== phase: {r['label']} ===")
        print(f"  replays                : {r['iterations']}")
        print(f"  completed              : {r['completed']}")
        print(f"  MISSES (flag seen, terminal signal not yet arrived) : {r['misses']}")
        print(f"  detected failures (broken phase: predicate timed out) : {r['detected_failures']}")
        print(f"  queued-delivery latency (us)     : {r['latency_us']}")
        if r["first_miss"]:
            print(f"  first miss : {r['first_miss']}")
        print()

    verdict_parts = []
    if old["misses"] > 0:
        verdict_parts.append("A: OLD predicate reproduces the historical miss shape (discrimination intact)")
    else:
        verdict_parts.append("A: OLD predicate produced no miss in this sample (stimulus may be too weak this run)")
    if new["misses"] == 0:
        verdict_parts.append("B: NEW predicate is clean under the same stimulus")
    else:
        verdict_parts.append("B: NEW predicate STILL MISSES -- fix insufficient")
    if broken["detected_failures"] == broken["iterations"] and broken["iterations"] > 0:
        verdict_parts.append("C: NEW predicate correctly reports terminal-not-reached under fault injection")
    else:
        verdict_parts.append("C: fault injection was ACCEPTED by the NEW predicate -- wait lost discrimination")
    for part in verdict_parts:
        print("verdict: " + part)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
