"""Reproduce the pause-test stall under the TASK-060 run_controller change."""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src"
WS = Path(__file__).resolve().parents[2] / "tests" / "workbench"
for entry in (str(WS), str(ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QGuiApplication

import workbench_helpers as h
import time as _time
from application.translation.pipeline.executor import DeterministicStepExecutor

def slow_executor(seconds_per_step: float = 0.02):
    return DeterministicStepExecutor(on_execute=lambda *a: _time.sleep(seconds_per_step))


app = QGuiApplication.instance() or QGuiApplication([])

import traceback
from ui.viewmodels.workbench.run_controller import RunController
_orig_shutdown = RunController.shutdown
def _spy_shutdown(self, *a, **k):
    print("=== shutdown CALLED ===")
    traceback.print_stack()
    return _orig_shutdown(self, *a, **k)
RunController.shutdown = _spy_shutdown
_orig_request_stop = RunController.request_stop
def _spy_stop(self, *a, **k):
    print("=== request_stop CALLED ===")
    traceback.print_stack()
    return _orig_request_stop(self, *a, **k)
RunController.request_stop = _spy_stop


service, _ = h.make_pipeline(pages=[(f"p{i}", i) for i in range(1, 9)], executor=slow_executor())
vm = h.make_vm(service)
vm.setContext("book-1", "chapter-1", "书", "章")
vm.startTranslateAll()

deadline = time.monotonic() + 10
while time.monotonic() < deadline and vm.taskProgress["run_status"] != "running":
    app.processEvents()
    time.sleep(0.01)
print("phase=started status=", vm.taskProgress["run_status"])

vm.pauseRun()
deadline = time.monotonic() + 10
while time.monotonic() < deadline and vm.taskProgress["run_status"] != "paused":
    app.processEvents()
    time.sleep(0.01)
print("phase=paused status=", vm.taskProgress["run_status"], "can_continue=", vm.taskProgress["can_continue"])

vm.continueRun()
for i in range(300):
    app.processEvents()
    time.sleep(0.05)
    status = vm.taskProgress["run_status"]
    if i % 20 == 0 or status not in ("running", "pausing"):
        print(f"t={i*0.05:.2f}s status={status!r} controller.is_running={vm._controller.is_running}")
    if status == "completed":
        break
print("final=", vm.taskProgress["run_status"])
try:
    run = vm._run
    print("cancel_requested=", run.cancel_requested, "pause=", run.pause_requested, "status=", run.status)
except Exception as e:
    print(e)
