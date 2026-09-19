"""TASK-060 review probe (Qoder, non-author) — what the shipped tests do not
measure.  Read-only w.r.t. the repository; every artefact goes to %TEMP%.

Run:  python t060_review_probe.py [tree_root]      (default: this file's repo)

S1  facade registry growth over *real* runs: `ThreadRoutedConnection` keeps one
    entry per thread ident and never evicts a finished worker (the code comment
    calls it "bounded and cheap").  Measure what a long session accumulates and
    whether the registered connections are still open.
S2  Q-007 ① at the physical layer: the trash face (`_remove_pending_targets`)
    documents that the never-clean boundary "is enforced once, at the physical
    removal point (ManagedFileStorage.remove_managed)"; probe that claim with a
    root-internal `..` through the *production* retry path.
S3  what a bare attribute read on the facade means now: `in_transaction` used to
    describe *the database*; check both (a) does reading it open a real
    connection on a new thread, and (b) can any aggregate "is someone writing"
    question still be answered (TASK-057 前置① depends on it).
S4  the new cost of per-thread connections: a GUI save that meets a worker
    holding the write lock now waits on busy_timeout instead of failing at once.
    Measure the wait and whether the failure is typed (AC ⑤) or raw.
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import time
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry, RegionType  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from ui.viewmodels.workbench.run_controller import RunController  # noqa: E402

app = QGuiApplication.instance() or QGuiApplication([])
print(f"== tree: {ROOT}")
print(f"== branch/head: ", end="")
import subprocess  # noqa: E402

print(
    subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True,
    ).stdout.strip() or "(not a git tree)"
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


def one_run(services, chapter) -> str:
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
    stop = time.monotonic() + 30
    while time.monotonic() < stop and not done and not crash:
        app.processEvents()
        time.sleep(0.005)
    controller.shutdown()
    return crash[0] if crash else (done[0] if done else "TIMEOUT")


def registry(services) -> tuple[int, int]:
    conns = getattr(services.conn, "_connections", {})
    open_count = 0
    for candidate in list(conns.values()):
        try:
            candidate.execute("SELECT 1")
            open_count += 1
        except Exception:  # noqa: BLE001 - closed connections raise here
            pass
    return len(conns), open_count


# ---------------------------------------------------------------- S1
tmp = Path(tempfile.mkdtemp(prefix="t060-s1-"))
services, chapter = assemble(tmp, pages=2)
print("\n-- S1 ThreadRoutedConnection registry growth over real runs")
print(f"   after assembly: registry={registry(services)}")
for i in range(1, 9):
    outcome = one_run(services, chapter)
    size, alive = registry(services)
    print(f"   run {i}: outcome={outcome} registry={size} open_connections={alive}")
print(
    "   (each run is a new QThread => a new ident; the facade never evicts a"
    " finished worker's connection, so both numbers grow monotonically)"
)
sys.stdout.flush()

# ---------------------------------------------------------------- S2
print("\n-- S2 Q-007 ① physical backstop, through the production trash retry path")
from application.maintenance.cleanup import is_safe_relative_path  # noqa: E402
from application.maintenance.trash import _JsonTrashManifest  # noqa: E402
from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ManagedFileStorage,
)

tmp2 = Path(tempfile.mkdtemp(prefix="t060-s2-"))
storage = ManagedFileStorage(tmp2 / "managed")
storage.ensure_layout()
protected = tmp2 / "managed" / "revisions" / "keep.png"
protected.parent.mkdir(parents=True, exist_ok=True)
protected.write_bytes(b"committed revision - must never be swept")
sneaky = "books/../revisions/keep.png"  # one .., resolves INSIDE the root
print(f"   target {sneaky!r} resolves to: "
      f"{(tmp2 / 'managed' / 'books' / '..' / 'revisions' / 'keep.png').resolve()}")
print(f"   policy predicate says safe? is_safe_relative_path={is_safe_relative_path(sneaky)}"
      "  (False = the single authority refuses it)")
try:
    storage.remove_managed(sneaky)
    print("   remove_managed(): returned normally")
except Exception as error:  # noqa: BLE001
    print(f"   remove_managed(): {type(error).__name__}: {str(error)[:120]}")
print(
    f"   protected revision file still there? {protected.exists()}"
    "  (False = the physical layer has no component rule)"
)


class DeadPages:
    """minimal PageTrashStore stub: no live rows, no batches."""

    def get_pages_by_ids(self, ids):  # noqa: D102
        return ()

    def list_live_managed_refs(self, refs):  # noqa: D102
        return set()

    def list_trashed_page_groups(self):  # noqa: D102
        return ()


from application.maintenance.trash import TrashService  # noqa: E402

protected2 = tmp2 / "managed" / "revisions" / "keep2.png"
protected2.write_bytes(b"another committed revision")
manifest = _JsonTrashManifest(tmp2 / "trash.json")
manifest.write_manifest(
    {
        "batches": [],
        "pending_purges": [
            {"batch_id": "tampered", "targets": ["revisions/../books/../revisions/keep2.png"]}
        ],
    }
)
service = TrashService(DeadPages(), storage, manifest)
cleared = service.retry_pending_purges()
print(
    f"   TrashService.retry_pending_purges() cleared={cleared};"
    f" protected file survives? {protected2.exists()}"
    "   <-- production path: a tampered manifest entry reaches unlink"
)
print(
    "   note: cache faces pass is_safe_relative_path() first (AC ⑦ ④ is real);"
    " the trash face has no predicate call and relies on the physical layer."
)
sys.stdout.flush()

# ---------------------------------------------------------------- S3
print("\n-- S3 what a facade attribute read means now")
tmp3 = Path(tempfile.mkdtemp(prefix="t060-s3-"))
services3, chapter3 = assemble(tmp3, pages=1)
base_size, _ = registry(services3)
seen: dict[str, object] = {}


def read_attr() -> None:
    seen["in_transaction"] = services3.conn.in_transaction


reader = threading.Thread(target=read_attr)
reader.start()
reader.join(10)
after_size, _ = registry(services3)
print(
    f"   a worker thread that only READ conn.in_transaction: value="
    f"{seen.get('in_transaction')!r}; registry {base_size} -> {after_size}"
    "  (a read-only attribute opened a real connection)"
)
gate: list[bool] = []
hold = threading.Event()
release = threading.Event()


def writing_worker() -> None:
    conn = services3.conn
    conn.execute("BEGIN IMMEDIATE")
    conn.execute("UPDATE books SET title = title")
    hold.set()
    release.wait(15)
    gate.append(conn.in_transaction)
    conn.rollback()


threading.Thread(target=writing_worker, daemon=True).start()
hold.wait(5)
gui_view = services3.conn.in_transaction
print(
    f"   while the worker holds an open write transaction,"
    f" GUI thread reads in_transaction -> {gui_view!r}"
    f" (worker's own view: True once released)"
)
print(
    f"   aggregate 'is any thread writing?' API on the facade:"
    f" {[n for n in dir(services3.conn) if not n.startswith('_')]}"
)
release.set()
time.sleep(0.3)
print(f"   worker-side in_transaction before rollback: {gate}")
sys.stdout.flush()

# ---------------------------------------------------------------- S4
print("\n-- S4 GUI save cost when a worker holds the write lock")
tmp4 = Path(tempfile.mkdtemp(prefix="t060-s4-"))
services4, chapter4 = assemble(tmp4, pages=1)
probe = sqlite3.connect(str(tmp4 / "library.db"))
page_id = probe.execute("SELECT page_id FROM pages").fetchone()[0]
probe.close()
region = services4.editing.create_region(
    page_id,
    RegionGeometry(bbox=BBox(10, 20, 60, 40)),
    region_type=RegionType.SPEECH,
)
busy = threading.Event()
free = threading.Event()
worker_errors: list[str] = []


def lock_holder() -> None:
    conn = services4.conn
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("UPDATE books SET title = title")
        busy.set()
        free.wait(20)
        conn.commit()
    except Exception as error:  # noqa: BLE001
        worker_errors.append(f"holder: {type(error).__name__}: {str(error)[:160]}")
        conn.rollback()


threading.Thread(target=lock_holder, daemon=True).start()
busy.wait(10)
started = time.monotonic()
outcome = "returned normally"
try:
    services4.editing.save_manual_translation(region.region_id, "并发下的保存")
except Exception as error:  # noqa: BLE001
    outcome = f"RAISED {type(error).__name__}: {str(error)[:160]}"
elapsed = time.monotonic() - started
print(f"   GUI save while locked: {elapsed:.2f}s -> {outcome}")
free.set()
time.sleep(0.3)
print(f"   worker side: {worker_errors or 'no error'}")
check = sqlite3.connect(str(tmp4 / "library.db"))
row = check.execute(
    "SELECT current_revision_id FROM regions WHERE region_id = ?",
    (region.region_id,),
).fetchone()
text = check.execute(
    "SELECT text_json FROM regions WHERE region_id = ?", (region.region_id,)
).fetchone()
check.close()
print(
    f"   after the wait: revision pointer set? {bool(row[0])};"
    f" edited_translation present? {'edited_translation' in (text[0] or '')}"
    f"  ({json.dumps(json.loads(text[0]), ensure_ascii=False)[:90] if text else ''})"
)
print("\n== done")
