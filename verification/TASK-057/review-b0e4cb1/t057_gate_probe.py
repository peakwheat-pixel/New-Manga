r"""TASK-057 review probe (Qoder, non-author): is the restore latch on EVERY
worker-starting path?  Read-only w.r.t. the repository.

Run:  python t057_gate_probe.py [tree_root]

`WorkbenchViewModel._start_run` checks ``_restore_in_progress`` before
``RunController.start()`` — but the VM reaches ``controller.start()`` from FOUR
places: ``_start_run``, ``continueRun`` (viewmodel.py:784),
``_restart_or_abandon`` (:808) and ``retryFailedPages`` (:827).  The handoff
item 2 and ``tests/workbench/test_restore_gate.py`` both claim "every workbench
start path is rejected" while latched; the shipped case enumerates two methods
that share the one guarded choke point.

This probe measures the claim.  Two modes, both reported:

MODE A (faithful states)  — drive the real in-memory pipeline into the state
  each slot needs (PAUSED for continue, terminal for restart/retry), engage the
  latch, call the slot, and report whether a worker started anyway.  The store
  here is InMemoryPipelineStore, i.e. not sqlite; that does not weaken the
  measurement, because what is being tested is *writer admission* at the VM,
  which is identical for the production service.
MODE B (state forced)     — the same three slots with the run state pinned to
  PENDING (``control_run`` stubbed to a no-new-run result, ``retry_failed_targets``
  to a real PENDING run).  Used only where MODE A cannot reach the
  ``if status is PENDING: start()`` line, to separate "the mock's state machine
  did not allow it" from "the latch stopped it".

Also reported: the error surface each path shows while latched, and whether any
release path exists other than an explicit endRestore() (G5 stickiness).
"""

from __future__ import annotations

import subprocess
import sys
import time
import types
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "workbench"))

from PySide6.QtGui import QGuiApplication  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])

import workbench_helpers as helpers  # noqa: E402
from domain.tasks.models import CommandType, PipelineRunStatus, PipelineScope, ScopeType  # noqa: E402

head = subprocess.run(
    ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True).stdout.strip()
print(f"== tree: {ROOT} @ {head}")


def make_vm():
    service, _catalog = helpers.make_pipeline(pages=[("p1", 1), ("p2", 2)])
    vm = helpers.make_vm(service)
    vm.setContext("book-1", "chapter-1", "书", "章")
    return vm


def pump(predicate, timeout=20.0):
    stop = time.monotonic() + timeout
    while time.monotonic() < stop and not predicate():
        app.processEvents()
        time.sleep(0.005)
    return predicate()


def status_of(vm):
    return vm._run.status.value if vm._run else "no-run"


def report(label, vm, started_before, note=""):
    started = vm._controller.is_running
    err = vm.commandErrorText or ""
    print(
        f"   {label:<34} worker started during restore? {started}"
        f"   latch-error surfaced? {'恢复进行中' in err}"
        f"   state after call={status_of(vm)}  {note}"
        + (f"\n       error surface: {err!r}" if err else "")
    )
    if started:
        vm._controller.shutdown()
        pump(lambda: not vm._controller.is_running, timeout=15)
    return started


def with_latch(vm):
    ok = vm.beginRestore()
    assert ok is True, f"beginRestore refused: {vm.commandErrorText!r}"
    return vm


results: dict[str, dict[str, bool]] = {}

# ---------------------------------------------------------------- A0 control
print("\n-- MODE A.0 control: the two paths the shipped case covers")
vm = with_latch(make_vm())
vm.startTranslateAll()
pump(lambda: vm._controller.is_running, timeout=2)
results["startTranslateAll"] = {"started": report(
    "A0 startTranslateAll", vm, False, "run object created? "
    + str(vm._run is not None))}
vm.endRestore()

vm = with_latch(make_vm())
vm.startTranslateUntranslated()
pump(lambda: vm._controller.is_running, timeout=2)
report("A0 startTranslateUntranslated", vm, False)

# ---------------------------------------------------------------- A1 continue
print("\n-- MODE A.1 continueRun (needs a PAUSED run)")
vm = make_vm()
vm.startTranslateAll()
pump(lambda: vm._controller.is_running)
vm.pauseRun()
pump(lambda: not vm._controller.is_running, timeout=40)
vm._controller.shutdown()
pump(lambda: not vm._controller.is_running, timeout=10)
print(f"   run state after pause+drain: {status_of(vm)}")
if status_of(vm) in {"paused", "pausing", "interrupted", "pending"}:
    with_latch(vm)
    vm.continueRun()
    reached = pump(lambda: vm._controller.is_running, timeout=3)
    results["continueRun"] = {"started": report(
        "A1 continueRun", vm, False, f"started_seen={reached}")}
else:
    print("   A1 skipped: the mock did not leave a resumable run")

# ---------------------------------------------------------------- A2/A3
print("\n-- MODE A.2/A.3 restartRun / retryFailedPages (terminal run)")
for label, call in (("restartRun", lambda v: v.restartRun()),
                    ("retryFailedPages", lambda v: v.retryFailedPages())):
    vm = make_vm()
    vm.startTranslateAll()
    pump(lambda: vm._controller.is_running)
    pump(lambda: not vm._controller.is_running, timeout=40)
    vm._controller.shutdown()
    pump(lambda: not vm._controller.is_running, timeout=10)
    print(f"   {label}: run state before latch = {status_of(vm)}")
    with_latch(vm)
    call(vm)
    pump(lambda: vm._controller.is_running, timeout=3)
    results[label] = {"started": report(f"A {label}", vm, False)}

# ---------------------------------------------------------------- MODE B
print("\n-- MODE B: same three slots with the run pinned to PENDING")
for label, call in (
    ("continueRun", lambda v: v.continueRun()),
    ("restartRun", lambda v: v.restartRun()),
    ("retryFailedPages", lambda v: v.retryFailedPages()),
):
    vm = make_vm()
    pending = vm._pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
    )
    vm._pipeline.plan_run(pending.run_id)
    assert pending.status is PipelineRunStatus.PENDING

    if label == "restartRun":
        # the production PipelineService returns a NEW run id for "restart";
        # supply one so the ``new_run_id is not None`` branch is reachable.
        second = vm._pipeline.create_run(
            CommandType.TRANSLATE_ALL.value,
            PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1"),
        )
        vm._pipeline.control_run = lambda _r, _a, _id=second.run_id: (
            types.SimpleNamespace(new_run_id=_id))
    else:
        vm._pipeline.control_run = lambda _r, _a: types.SimpleNamespace(
            new_run_id=None)
    vm._pipeline.retry_failed_targets = lambda _rid: pending
    vm._run = pending
    vm._refresh_projection = lambda: None
    with_latch(vm)
    call(vm)
    seen = pump(lambda: vm._controller.is_running, timeout=3)
    report(f"B {label}", vm, False, f"started_seen={seen}")

# ---------------------------------------------------------------- G5
print("\n-- G5 latch stickiness: who can release it?")
vm = with_latch(make_vm())
callers = subprocess.run(
    ["git", "-C", str(ROOT), "grep", "-n", "beginRestore\\|endRestore",
     "--", "src"], capture_output=True).stdout.decode("utf-8", "replace").strip()
print("   production callers of beginRestore/endRestore inside src/:")
print("       " + (callers.replace("\n", "\n       ") if callers else "(none)"))
vm.startTranslateAll()
pump(lambda: False, timeout=0.5)
print(
    f"   latched and abandoned: _restore_in_progress={vm._restore_in_progress};"
    f" controller idle={not vm._controller.is_running}"
    "   => an exception between begin/end leaves the workbench permanently"
    " closed (no finally, no timeout, no context manager)"
)
vm.endRestore()
print("\n== done")
