"""TASK-061 review probe (Qoder, non-author) — the faces the shipped tests
do not measure.  Read-only w.r.t. the repository; every artefact goes to
%TEMP%.  The SAME file runs against both trees (post-fix HEAD and the
detached pre-fix 6cb0afb) so the comparison is one ruler, not two.

Run:  python t061_review_probe.py [tree_root]

T1  registry growth over *real* runs — my TASK-060 S1 instrument re-aimed:
    pre-fix it measured registry 9 / open 9 after 8 runs.  Here the same
    loop prints the same two numbers, plus the peak *while* a worker is
    alive (eviction must not shrink the set of threads that are running).
T2  is eviction deterministic (refcount at thread exit) or GC-deferred?
    40 sequential worker threads, no gc.collect() anywhere.
T3  ident-reuse stress: thousands of short-lived threads so the OS recycles
    thread idents.  If the stale-slot branch could close a *live* thread's
    connection, this surfaces as "Cannot operate on a closed database".
T4  the strong half of the concurrency claim ("no other party can reference
    conn"): a cursor created by a worker and kept by the GUI thread pins the
    real connection.  Does eviction yank it?
T5  is ``shutdown() is True and not any_in_transaction()`` enough for
    TASK-057 前置①?  Two independent questions: (a) does anything stop a new
    run from starting right after the check (admission), (b) does "no thread
    is in a transaction" imply "no thread holds a writer connection"?
T6  the guard matrix at the physical removal point AND through the production
    trash retry path: ``..`` / ``.`` / empty segment / absolute / root-internal
    directory junction / root-internal file symlink / legit deletion.
T7  cost of the per-level lstat walk (calls per removal, microseconds).
"""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
# argv[2] = T3 thread-churn budget in seconds (lower it on the pre-fix tree,
# where nothing is evicted and hundreds of open connections are themselves
# the finding).
_raw_churn = sys.argv[2].strip() if len(sys.argv) > 2 else ""
CHURN_SECONDS = float(_raw_churn) if _raw_churn else 12.0
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ImmutablePathViolation,
    ManagedFileStorage,
)
from ui.viewmodels.workbench.run_controller import RunController  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])
print(f"== tree: {ROOT}")
print(
    "== head: "
    + (
        subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
        ).stdout.strip()
        or "(not a git tree)"
    )
)
sys.stdout.flush()


def make_png(width: int, height: int) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def assemble(tmp: Path, pages: int):
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("探针书")
    chapter = services.library.create_chapter(
        book.book_id, "话", chapter_type="webtoon", reading_direction="vertical"
    )
    services.importer.import_files(
        chapter.chapter_id,
        [
            ImportSource(
                filename=f"p{i}.png",
                data_provider=lambda i=i: make_png(40, 60),
            )
            for i in range(1, pages + 1)
        ],
    )
    return services, chapter


def one_run(services, chapter) -> tuple[str, int]:
    """Start a run, pump the GUI loop until it ends; return (outcome, peak
    registry size observed *while* the worker was alive)."""
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    services.pipeline.plan_run(run.run_id)
    controller = RunController()
    done: list[str] = []
    crash: list[str] = []
    controller.runFinished.connect(lambda _r, status: done.append(status))
    controller.runCrashed.connect(lambda _r, error: crash.append(error))
    controller.start(services.pipeline, run)
    peak = 0
    stop = time.monotonic() + 30
    while time.monotonic() < stop and not done and not crash:
        app.processEvents()
        peak = max(peak, registry_size(services))
        time.sleep(0.005)
    drained = controller.shutdown()
    return (crash[0] if crash else (done[0] if done else "TIMEOUT")), peak


def registry_size(services) -> int:
    getter = getattr(services.conn, "registry_size", None)
    if getter is not None:
        return getter()
    return len(getattr(services.conn, "_connections", {}))


def open_connections(services) -> int:
    """Count registered connections that still answer a statement."""
    conns = list(getattr(services.conn, "_connections", {}).values())
    alive = 0
    for candidate in conns:
        try:
            candidate.execute("SELECT 1")
        except Exception:  # noqa: BLE001 - closed handles raise
            continue
        alive += 1
    return alive


# ---------------------------------------------------------------- T1
print("\n-- T1 registry growth over 8 real runs (my TASK-060 S1 instrument)")
tmp1 = Path(tempfile.mkdtemp(prefix="t061-t1-"))
services, chapter = assemble(tmp1, pages=2)
print(f"   after assembly: registry={registry_size(services)}")
sizes: list[int] = []
peaks: list[int] = []
for i in range(1, 9):
    outcome, peak = one_run(services, chapter)
    sizes.append(registry_size(services))
    peaks.append(peak)
    print(f"   run {i}: outcome={outcome} registry_after={sizes[-1]} peak_during={peak}")
def pump_until(predicate, timeout=30.0):
    """Pump the GUI event loop until predicate() is true or the budget ends."""
    stop = time.monotonic() + timeout
    while time.monotonic() < stop and not predicate():
        app.processEvents()
        time.sleep(0.005)
    return predicate()


print(f"   SUMMARY T1 shape={sizes} bounded(<=2)? {max(sizes) <= 2} peaks={peaks}")
print(f"   open connections after 8 runs: {open_connections(services)}")

# T1b — the same production execute_run on a live worker thread: how many
# entries does the registry hold *while* a writer is alive?  (T1's GUI-side
# poll is too coarse to catch the window; runs here are ~2 pages of mocks.)
run = services.pipeline.create_run(
    CommandType.TRANSLATE_ALL.value,
    PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
)
services.pipeline.plan_run(run.run_id)
worker_errors: list[str] = []


def live_worker() -> None:
    try:
        services.pipeline.execute_run(run.run_id)
    except Exception:  # noqa: BLE001
        worker_errors.append(traceback.format_exc(limit=3))


t1b = threading.Thread(target=live_worker)
t1b.start()
time.sleep(0.4)
during = registry_size(services) if t1b.is_alive() else -1
t1b.join(60)
time.sleep(0.4)
print(
    f"   T1b while a worker executes execute_run: registry={during}"
    f" (2 = GUI + worker, i.e. bounded by LIVE threads, not by runs);"
    f" after it dies: registry={registry_size(services)}"
    f" open={open_connections(services)} errors={len(worker_errors)}"
)
for e in worker_errors[:2]:
    print("   " + e.replace("\n", " | "))
sys.stdout.flush()

# ---------------------------------------------------------------- T2
print("\n-- T2 deterministic eviction (no gc.collect() anywhere)")
tmp2 = Path(tempfile.mkdtemp(prefix="t061-t2-"))
services2, _ = assemble(tmp2, pages=1)
peak2 = 0
failures: list[str] = []


def short_worker() -> None:
    global peak2
    try:
        services2.conn.execute("SELECT 1").fetchone()
    except Exception:  # noqa: BLE001
        failures.append(traceback.format_exc(limit=2))


for _ in range(40):
    t = threading.Thread(target=short_worker)
    t.start()
    t.join()
    peak2 = max(peak2, registry_size(services2))
print(
    f"   40 sequential threads: peak registry={peak2}"
    f" final registry={registry_size(services2)} errors={len(failures)}"
)
for f in failures[:3]:
    print("   " + f.replace("\n", " | "))
sys.stdout.flush()

# ---------------------------------------------------------------- T3
print("\n-- T3 ident-reuse stress (recycled thread idents vs the stale-slot branch)")
errors3: list[str] = []
peak3 = 0
lock3 = threading.Lock()
stop_at = time.monotonic() + CHURN_SECONDS


def reuse_worker() -> None:
    global peak3
    try:
        row = services2.conn.execute("SELECT 1").fetchone()
        if row[0] != 1:
            with lock3:
                errors3.append("bad row")
    except Exception:  # noqa: BLE001
        with lock3:
            errors3.append(traceback.format_exc(limit=3))


threads_started = 0
while time.monotonic() < stop_at:
    batch = [threading.Thread(target=reuse_worker) for _ in range(40)]
    for t in batch:
        t.start()
        threads_started += 1
    for t in batch:
        t.join()
    with lock3:
        peak3 = max(peak3, registry_size(services2))
print(
    f"   {threads_started} threads churned: peak registry={peak3}"
    f" final={registry_size(services2)} open={open_connections(services2)}"
    f" errors={len(errors3)}"
)
for e in errors3[:3]:
    print("   " + e.replace("\n", " | "))
sys.stdout.flush()

# ---------------------------------------------------------------- T4
print("\n-- T4 a GUI-held cursor from a dead worker (the 'no other reference' claim)")
tmp4 = Path(tempfile.mkdtemp(prefix="t061-t4-"))
services4, _ = assemble(tmp4, pages=1)
held_cursor: list[object] = []
worker_done = threading.Event()


def cursor_worker() -> None:
    # a statement whose *cursor* outlives the thread — the shape of
    # ``cur = conn.execute(...)`` stored on a shared object
    cur = services4.conn.execute("SELECT book_id, title FROM books")
    held_cursor.append(cur)
    worker_done.set()


before4 = registry_size(services4)
t4 = threading.Thread(target=cursor_worker)
t4.start()
worker_done.wait(5)
t4.join()
time.sleep(0.5)  # thread is gone; eviction (if any) has fired
print(
    f"   registry {before4} -> {registry_size(services4)}"
    f" after the cursor's thread died"
)
try:
    rows = held_cursor[0].fetchall()
    print(f"   held cursor still usable: fetchall() -> {len(rows)} row(s)")
except Exception as error:  # noqa: BLE001
    print(
        f"   held cursor BROKEN after eviction: {type(error).__name__}: {error}"
        "   <-- the evicting thread closed a connection another thread still referenced"
    )
sys.stdout.flush()

# ---------------------------------------------------------------- T5
print("\n-- T5 is the TASK-057 前置① predicate a *barrier*?")
tmp5 = Path(tempfile.mkdtemp(prefix="t061-t5-"))
services5, chapter5 = assemble(tmp5, pages=1)
controller5 = RunController()


def start_run(tag: str) -> None:
    run = services5.pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter5.chapter_id),
    )
    services5.pipeline.plan_run(run.run_id)
    controller5.start(services5.pipeline, run)


start_run("first")
pump_until(lambda: not controller5.is_running)
drained = controller5.shutdown()
any_tx = getattr(services5.conn, "any_in_transaction", None)
gate_value = (drained is True) and (any_tx is None or any_tx() is False)
print(
    f"   composite predicate right after a completed run:"
    f" shutdown() is True={drained is True};"
    f" any_in_transaction={any_tx() if any_tx else '<absent pre-fix>'}"
    f" -> gate passes? {gate_value}"
)
print("   (a) admission: can a NEW run still start after the gate passed?")
try:
    start_run("second")
    print("       YES — RunController.start() has no shut-down latch; a writer")
    print("            can appear one statement after the check returns False")
    pump_until(lambda: not controller5.is_running)
    print(f"       second run done; controller.shutdown() -> {controller5.shutdown()}")
except Exception as error:  # noqa: BLE001
    print(f"       NO — {type(error).__name__}: {error}")


print("   (b) does 'no thread in a transaction' mean 'no live writer'?")
hold = threading.Event()
free = threading.Event()
views: dict[str, object] = {}


def idle_writer() -> None:
    conn = services5.conn
    conn.execute("SELECT 1").fetchone()  # opens this thread's connection
    hold.set()                    # alive, holding a writer-capable connection,
    free.wait(10)                 # but NOT in a transaction
    views["own_in_transaction"] = conn.in_transaction


threading.Thread(target=idle_writer, daemon=True).start()
hold.wait(5)
time.sleep(0.5)  # let the two finished workers' evictions settle
if any_tx is not None:
    views["aggregate_any_in_transaction"] = any_tx()
views["registry_size"] = registry_size(services5)
free.set()
time.sleep(0.3)
print(f"       live-but-idle writer thread: {views}")
print(
    "       => any_in_transaction()==False while a second thread holds an open,"
    " writable connection; drained=>no-worker is what actually carries the guarantee"
)
sys.stdout.flush()

# ---------------------------------------------------------------- T6
print("\n-- T6 remove_managed guard matrix")
tmp6 = Path(tempfile.mkdtemp(prefix="t061-t6-"))
storage = ManagedFileStorage(tmp6 / "managed")
storage.ensure_layout()


def plant(rel: str, data: bytes = b"PROTECTED") -> Path:
    target = tmp6 / "managed" / Path(*rel.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return target


def attempt(label: str, rel: str, protected: Path) -> None:
    try:
        storage.remove_managed(rel)
        verdict = "ALLOWED (no refusal)"
    except ImmutablePathViolation as error:
        verdict = f"typed refusal: {str(error)[:70]}"
    except Exception as error:  # noqa: BLE001
        verdict = f"UNtyped {type(error).__name__}: {str(error)[:60]}"
    print(
        f"   {label:<26} {rel[:46]:<46} -> {verdict};"
        f" target survives? {protected.exists()}"
    )


prot_a = plant("revisions/keep_a.png")
attempt(".. traversal", "books/../revisions/keep_a.png", prot_a)
prot_b = plant("books/keep_b.png")
attempt(". segment", "books/./keep_b.png", prot_b)
prot_c = plant("books/keep_c.png")
attempt("empty middle segment", "books//keep_c.png", prot_c)
prot_d = plant("books/keep_d.png")
attempt("backslash traversal", "books\\..\\revisions\\keep_a.png", prot_d)

# root-internal directory junction
twin = tmp6 / "managed" / "books" / "book-1" / "chapters" / "chapter-twin"
twin.parent.mkdir(parents=True, exist_ok=True)
prot_j = plant("books/book-1/chapters/chapter-1/original/keep_j.png")
made = subprocess.run(
    ["cmd", "/c", "mklink", "/J", str(twin), str(prot_j.parent)],
    capture_output=True,
)
print(f"   mklink /J rc={made.returncode} (directory junction)")
attempt("dir junction (root-internal)",
        "books/book-1/chapters/chapter-twin/original/keep_j.png", prot_j)

# junction placed HIGHER in the walk (books level)
high = tmp6 / "managed" / "books" / "book-twin"
prot_h = tmp6 / "managed" / "books" / "book-1" / "chapters" / "chapter-1" / "original" / "keep_j.png"
made_h = subprocess.run(
    ["cmd", "/c", "mklink", "/J", str(high), str(tmp6 / "managed" / "books" / "book-1")],
    capture_output=True,
)
print(f"   mklink /J (books level) rc={made_h.returncode}")
attempt("junction at books level",
        "books/book-twin/chapters/chapter-1/original/keep_j.png", prot_h)

# junction pointing OUT of the root
out_dir = tmp6 / "outside"
out_dir.mkdir(parents=True, exist_ok=True)
out_file = out_dir / "victim.png"
out_file.write_bytes(b"OUTSIDE THE ROOT")
out_link = tmp6 / "managed" / "books" / "outlink"
made_o = subprocess.run(
    ["cmd", "/c", "mklink", "/J", str(out_link), str(out_dir)],
    capture_output=True,
)
print(f"   mklink /J (outside root) rc={made_o.returncode}")
attempt("junction to outside root", "books/outlink/victim.png", out_file)

# file-level symlink (needs privilege / dev mode: record the outcome honestly)
sym = tmp6 / "managed" / "books" / "book-1" / "chapters" / "chapter-1" / "original" / "sym.png"
made_s = subprocess.run(
    ["cmd", "/c", "mklink", str(sym), str(prot_j)], capture_output=True
)
print(
    f"   mklink (file symlink) rc={made_s.returncode}"
    f" stderr={made_s.stderr.decode(errors='replace').strip()[:70]}"
)
if made_s.returncode == 0:
    attempt("file symlink to protected", 
            "books/book-1/chapters/chapter-1/original/sym.png", prot_j)
    print(f"   (the symlink itself is inside the root; deleting it is harmless."
          f" protected target survives? {prot_j.exists()})")

# what the detection primitive actually sees
for label, probe in (("dir junction", twin), ("books-level junction", high)):
    st = probe.lstat()
    attrs = getattr(st, "st_file_attributes", None)
    print(
        f"   lstat {label}: st_file_attributes={attrs}"
        f" REPARSE bit? {bool(attrs and attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)}"
        f" st_reparse_tag={getattr(st, 'st_reparse_tag', None)}"
    )

# legitimate deletion must still work
legit = plant("books/book-legit/chapters/ch-1/original/ok.png", b"LEGIT")
try:
    storage.remove_managed("books/book-legit/chapters/ch-1/original/ok.png")
    print(f"   legit deletion: allowed; file gone? {not legit.exists()}")
except Exception as error:  # noqa: BLE001
    print(f"   legit deletion: REGRESSION {type(error).__name__}: {error}")

# through the production trash retry path
print("\n   same shapes through TrashService.retry_pending_purges():")
from application.maintenance.trash import (  # noqa: E402
    TrashService,
    _JsonTrashManifest,
)


class DeadPages:
    def get_pages_by_ids(self, ids):  # noqa: D102
        return ()

    def list_live_managed_refs(self, refs):  # noqa: D102
        return set()

    def list_trashed_page_groups(self):  # noqa: D102
        return ()


for label, rel, victim in (
    (".. traversal", "books/../revisions/keep_a.png", tmp6 / "managed" / "revisions" / "keep_a.png"),
    (". segment", "revisions/./keep_a.png", tmp6 / "managed" / "revisions" / "keep_a.png"),
    ("dir junction", "books/book-1/chapters/chapter-twin/original/keep_j.png", prot_j),
):
    if not victim.exists():
        plant(victim.relative_to(tmp6 / "managed").as_posix())
    manifest = _JsonTrashManifest(tmp6 / "trash.json")
    manifest.write_manifest(
        {"batches": [], "pending_purges": [{"batch_id": "tampered", "targets": [rel]}]}
    )
    service = TrashService(DeadPages(), storage, manifest)
    try:
        cleared = service.retry_pending_purges()
        outcome = f"cleared={cleared}"
    except Exception as error:  # noqa: BLE001
        outcome = f"raised {type(error).__name__}"
    print(f"   {label:<16} {rel[:44]:<44} -> {outcome}; victim survives? {victim.exists()}")
sys.stdout.flush()

# ---------------------------------------------------------------- T7
print("\n-- T7 cost of the per-level lstat walk")
calls = {"n": 0}
real_lstat = Path.lstat


def counting_lstat(self):
    calls["n"] += 1
    return real_lstat(self)


if hasattr(Path, "lstat"):
    Path.lstat = counting_lstat  # type: ignore[method-assign]
tmp7 = Path(tempfile.mkdtemp(prefix="t061-t7-"))
storage7 = ManagedFileStorage(tmp7 / "managed")
storage7.ensure_layout()
rel7 = "books/b/chapters/c/original/r.png"
samples: list[float] = []
lstat_counts: list[int] = []
for i in range(60):
    target = tmp7 / "managed" / Path(*rel7.split("/"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"x")
    calls["n"] = 0
    started = time.perf_counter()
    storage7.remove_managed(rel7)
    samples.append((time.perf_counter() - started) * 1e6)
    lstat_counts.append(calls["n"])
Path.lstat = real_lstat  # type: ignore[method-assign]
samples.sort()
print(
    f"   60 real removals of a 6-segment managed path:"
    f" lstat calls per removal={sorted(set(lstat_counts))}"
    f" median={samples[len(samples)//2]:.0f}us p95={samples[int(len(samples)*0.95)]:.0f}us"
)
print("\n== done")
