r"""TASK-058 post-hoc reviewer probe (Qoder, non-author): what actually
happens when the exit drain times out?

    python t058_drain_timeout_probe.py [tree_root]

TASK-058 added ``bootstrap.app._shutdown_services`` = "drain the workbench
worker, then close the shared connection" (SS11 P-10).  Two later slices
wrote the *contract* into master:

  * ``RunController._reap_worker`` docstring: ``False`` means the budget
    expired with the thread "still alive and writing" - "the caller must then
    not close the shared database connection (see bootstrap.app
    ._shutdown_services)";
  * ``ThreadRoutedConnection.close`` docstring: "if the drain timed out,
    ``_shutdown_services`` skips close entirely - Q-003";
  * the shipped AC1 stub comments that "False/None would make
    _shutdown_services skip close on purpose";
  * ``WorkbenchViewModel.shutdown`` returns that bool to the caller.

This probe measures whether ``_shutdown_services`` honours it, driving the
real production assembly with a worker step that outlives the 5 s budget.

S1  timeout path: the bool the caller received, whether close() ran, and what
    the worker sees when it touches the connection afterwards.
S2  the shipped AC2 premise: is a worker actually alive at the drain call?
S3  machine-check: does the function branch on the result at all?

Read-only w.r.t. the repository; writes only into a temp dir.
"""

from __future__ import annotations

import inspect
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QCoreApplication, QIODevice  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402

app = QCoreApplication.instance() or QCoreApplication([])

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import _shutdown_services, assemble_services  # noqa: E402
from domain.tasks.models import PipelineRunStatus  # noqa: E402

print(f"== tree: {ROOT}")


def make_services(tmp: Path):
    def png() -> bytes:
        image = QImage(40, 60, QImage.Format.Format_RGB32)
        image.fill(0xFF00FF00)
        buf = QBuffer()
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buf, "PNG")
        return bytes(buf.data())

    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("排空书")
    chapter = services.library.create_chapter(
        book.book_id, "排空话", chapter_type="webtoon", reading_direction="vertical"
    )
    services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename=f"p{i}.png", data_provider=png) for i in range(1, 4)],
    )
    return services, book, chapter


# ---------------------------------------------------------------- S3
print("\n-- S3 does _shutdown_services branch on the drain result?")
src = inspect.getsource(_shutdown_services)
body = src.split('"""')[2]
code_lines = [ln for ln in body.splitlines() if ln.strip()]
for line in code_lines:
    print("      ", line)
print(f"   statements: {len(code_lines)}   branches: "
      f"{sum(1 for ln in code_lines if ln.strip().startswith(('if', 'elif', 'else')))}"
      "   <- a non-zero count means the caller DOES branch on the bool")

# ---------------------------------------------------------------- S1
print("\n-- S1 drain timeout (a worker step outlives the 5 s budget)")
tmp = Path(tempfile.mkdtemp(prefix="t058-s1-"))
services, book, chapter = make_services(tmp)
vm = services.workbench
vm.setContext(book.book_id, chapter.chapter_id, "排空书", "排空话")

observed: dict[str, str] = {}
real_execute_run = services.pipeline.execute_run


def slow_execute_run(run_id: str):
    """Stand-in for a real provider step - OCR/translation over the network
    routinely exceeds the 5 s drain budget."""
    time.sleep(7.0)
    try:
        services.conn.execute("UPDATE pipeline_runs SET status = status")
        observed["worker_write"] = "OK - the connection was still usable"
    except Exception as error:  # noqa: BLE001
        observed["worker_write"] = f"{type(error).__name__}: {error}"
    return real_execute_run(run_id)


services.pipeline.execute_run = slow_execute_run

returned: list[object] = []
real_vm_shutdown = vm.shutdown


def spy_shutdown(*args, **kwargs):
    value = real_vm_shutdown(*args, **kwargs)
    returned.append(value)
    return value


vm.shutdown = spy_shutdown  # services.workbench IS this object

vm.startTranslateAll()
time.sleep(0.4)
print(f"   worker alive before the exit drain? {vm._controller.is_running}")
t0 = time.monotonic()
_shutdown_services(services)
elapsed = time.monotonic() - t0
thread = vm._controller._thread
print(f"   bool the caller received from shutdown(): {returned}")
print(f"   _shutdown_services took                  : {elapsed:.2f}s (budget 5s)")
print(f"   worker thread still running at return?   : "
      f"{thread is not None and thread.isRunning()}")
try:
    services.conn.execute("SELECT 1")
    print("   conn after _shutdown_services            : STILL OPEN -> close skipped")
except sqlite3.ProgrammingError as error:
    print(f"   conn after _shutdown_services            : CLOSED ({error})")

print("   waiting for the worker to wake and write...")
deadline = time.monotonic() + 15
while time.monotonic() < deadline and "worker_write" not in observed:
    app.processEvents()
    time.sleep(0.05)
print(f"   what the worker saw writing after close  : "
      f"{observed.get('worker_write', '<never ran>')}")
print("   probe process still alive (no interpreter crash)")

# ---------------------------------------------------------------- S2
print("\n-- S2 is a worker actually alive when the shipped AC2 drains? (5 samples)")
for sample in range(5):
    tmp2 = tmp / f"s2-{sample}"
    tmp2.mkdir(parents=True, exist_ok=True)
    services2, book2, chapter2 = make_services(tmp2)
    vm2 = services2.workbench
    vm2.setContext(book2.book_id, chapter2.chapter_id, "排空书", "排空话")
    vm2.startTranslateAll()
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        app.processEvents()
        if vm2._run is not None and vm2._run.status is not PipelineRunStatus.PENDING:
            break
        time.sleep(0.01)
    status_at_drain = vm2._run.status.value if vm2._run is not None else "<no run>"
    alive = vm2._controller.is_running
    _shutdown_services(services2)
    print(f"   sample {sample}: status at the drain call = {status_at_drain!r}"
          f"   worker alive = {alive}")
    shutil.rmtree(tmp2, ignore_errors=True)


# ---------------------------------------------------------------- S4
print()
print("-- S4 the shape AC2 should have: worker alive, but drainable in budget")
tmp4 = tmp / "s4"
tmp4.mkdir(parents=True, exist_ok=True)
services4, book4, chapter4 = make_services(tmp4)
vm4 = services4.workbench
vm4.setContext(book4.book_id, chapter4.chapter_id, "排空书", "排空话")
wrote: list[str] = []
real4 = services4.pipeline.execute_run


def block_1s(run_id: str):
    time.sleep(1.0)
    services4.conn.execute("UPDATE pipeline_runs SET status = status")
    wrote.append("write landed while the drain was waiting")
    return real4(run_id)


services4.pipeline.execute_run = block_1s
vm4.startTranslateAll()
time.sleep(0.3)
alive = vm4._controller.is_running
t0 = time.monotonic()
_shutdown_services(services4)
took = time.monotonic() - t0
try:
    services4.conn.execute("SELECT 1")
    closed = False
except sqlite3.ProgrammingError:
    closed = True
print(f"   worker alive at the drain call: {alive}   drain took {took:.2f}s")
print(f"   worker wrote before close?     {bool(wrote)}   conn closed afterwards? {closed}")
print(f"   -> this is the case the shipped AC2 does NOT exercise (S2: alive=False)")

shutil.rmtree(tmp, ignore_errors=True)
print("\n== done")
