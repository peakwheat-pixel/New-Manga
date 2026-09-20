r"""TASK-057 round-2 reviewer probe (Qoder, non-author): hostile checks.

Round 1 (R-001) proved the latch sat on one of four worker-birth faces.
The rework moves it to ``RunController.start()``.  This probe does not
re-ask "does it hold" (``t057_gate_probe.py`` does that); it tries to
BREAK the new arrangement three ways:

H1 birthplace-only  — engage the latch on the CONTROLLER alone (the VM
   mirror ``_restore_in_progress`` stays False) and call every face.
   If the refusal still lands, the choke point is doing the work and the
   VM pre-check is redundant depth rather than the load-bearing part.
H2 nesting         — ``restoreGate()`` entered twice (e.g. a restore body
   that itself opens a gate).  Does the inner ``__exit__`` release the
   OUTER body's protection?
H3 half-applied    — with the latch engaged, ``continueRun`` refuses the
   worker but the run control has already landed.  What state is left
   behind, and does releasing the latch start it?

Read-only w.r.t. the repository.  Run:  python t057_chokepoint_probe.py [tree_root]
"""

from __future__ import annotations

import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "workbench"))

from PySide6.QtGui import QGuiApplication  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])

import workbench_helpers as helpers  # noqa: E402

head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                      capture_output=True).stdout.decode("utf-8", "replace").strip()
dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                       capture_output=True).stdout.decode("utf-8", "replace").strip()
print(f"== tree: {ROOT} @ {head}  dirty={'yes' if dirty else 'no'}")


def make_vm():
    service, _catalog = helpers.make_pipeline(pages=[("p1", 1), ("p2", 2)])
    vm = helpers.make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    return vm


def pump(predicate, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not predicate():
        app.processEvents()
        time.sleep(0.005)
    return predicate()


def pause_and_drain(vm):
    """Real chain: start -> pause -> drain, so continueRun has a genuine
    resumable run (the face that birthed a worker at b0e4cb1)."""
    vm.startTranslateAll()
    assert pump(lambda: vm._controller.is_running, 20), "run never started"
    vm.pauseRun()
    assert pump(lambda: not vm._controller.is_running, 40), "run never drained"
    vm.shutdown()
    return vm._run.status.value


def store_status(vm, run_id):
    """Read the run straight from the store (private access is fine in a
    read-only probe; the service has no public status getter)."""
    run = vm._pipeline._store.get(run_id)
    return "<missing>" if run is None else run.status.value


print("\n-- H1 latch engaged on the CONTROLLER only (VM mirror left False)")
vm = make_vm()
vm._controller.set_restore_latch(True)
print(f"   vm._restore_in_progress={vm._restore_in_progress}  "
      f"controller.admission_closed={vm._controller.admission_closed}")
for name in ("startTranslateAll", "startTranslateUntranslated"):
    getattr(vm, name)()
    print(f"   H1 {name:<28} worker born={vm._controller.is_running}  "
          f"run object={vm._run is not None}  error={vm.commandErrorText!r}")
vm._controller.set_restore_latch(False)
status = pause_and_drain(vm)            # release first: this needs a real start
vm._controller.set_restore_latch(True)  # controller-only, mirror stays False
vm.continueRun()
print(f"   H1 continueRun (state {status})      worker born={vm._controller.is_running}  "
      f"error={vm.commandErrorText!r}")
vm._controller.set_restore_latch(False)
vm.shutdown()

print("\n-- H2 nested restoreGate(): does the inner exit unlock the outer body?")
vm = make_vm()
with vm.restoreGate():
    print(f"   outer engaged: _restore_in_progress={vm._restore_in_progress} "
          f"admission_closed={vm._controller.admission_closed}")
    try:
        with vm.restoreGate():
            print("   inner gate entered while already engaged (no refusal)")
    except RuntimeError as error:
        print(f"   inner gate refused: {error}")
    vm.startTranslateAll()
    born = vm._controller.is_running
    pump(lambda: not vm._controller.is_running, 40)
    print(f"   after inner exit, still inside the OUTER body: admission_closed="
          f"{vm._controller.admission_closed}  _restore_in_progress="
          f"{vm._restore_in_progress}  WORKER BORN DURING OUTER RESTORE={born}")
print(f"   outer exited: admission_closed={vm._controller.admission_closed}")
vm.shutdown()

print("\n-- H3 half-applied command: what survives a latched continueRun?")
vm = make_vm()
status = pause_and_drain(vm)
run_id = vm._run.run_id
assert vm.beginRestore() is True
vm.continueRun()
print(f"   before latch: run={status!r}   after latched continueRun: "
      f"store={store_status(vm, run_id)!r}  vm._run={vm._run.status.value!r}")
print(f"   worker born={vm._controller.is_running}  error={vm.commandErrorText!r}")
print(f"   tasks in store after the refusal: "
      f"{dict(Counter(t.status.value for t in vm._pipeline._store.get(run_id).tasks))}")
vm.endRestore()
print(f"   endRestore() auto-started the pending run? {vm._controller.is_running}")
print(f"   run status after release: {store_status(vm, run_id)!r}  "
      f"(a PENDING run with no worker is what recover_running_runs faces next boot)")
vm.shutdown()
print("\n== done")
