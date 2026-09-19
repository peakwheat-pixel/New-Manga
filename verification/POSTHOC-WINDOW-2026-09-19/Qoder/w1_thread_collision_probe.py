"""POSTHOC-WINDOW-2026-09-19 review (Qoder), target 1: W1 TASK-048 past the
shipped end-to-end test.

The slice's own e2e (`tests/workbench/test_run_thread_e2e.py`) proves the P0 is
gone: a real `assemble_services` + real `RunController`(QThread) + real SQLite
completes a `TRANSLATE_ALL` run instead of crashing with
`sqlite3.ProgrammingError`.  What it does not probe is the cost of the chosen
fix: ONE connection object is now shared by the GUI thread and the worker
thread (`check_same_thread=False`), while the production code on both sides
drives **explicit transactions on that one connection**:

- worker: `SqlitePipelineStore.put` -> `with self._conn:` (src/infrastructure/sqlite/pipeline.py:398)
- GUI:    `RegionEditingService` -> `SqliteRegionRepository.commit_region_revision`
          -> `conn.execute("BEGIN IMMEDIATE")` **outside** its try (src/infrastructure/sqlite/regions.py:210),
          with `except Exception: conn.rollback()` (regions.py:272-275)

Two threads issuing BEGIN / commit() / rollback() on one connection are not
independent transactions.  Parts:

A  reproduce the P0 fix (uphold check, my own run)
B  realism: real run on the worker while the GUI thread issues real region
   commits; measure how often the collision fires
C  control: the same GUI loop with no worker run
D  mechanism (forced schedule, statement shapes quoted from src): D1 the GUI's
   BEGIN IMMEDIATE against a worker-held transaction; D2 a worker-shaped commit
   landing mid-GUI-transaction, then the GUI rollback - does the
   "rolling back entirely" promise of regions.py:7 still hold?
E  invariant/integrity readback through an independent connection

Run: python verification/POSTHOC-WINDOW-2026-09-19/Qoder/w1_thread_collision_probe.py [tree_root]
"""

from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import threading
import time
from collections import Counter
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry, RegionType  # noqa: E402
from domain.tasks.models import CommandType, PipelineScope, ScopeType  # noqa: E402
from ui.viewmodels.workbench.run_controller import RunController  # noqa: E402

TERMINAL = {
    "completed",
    "completed_with_failures",
    "failed",
    "cancelled",
    "interrupted",
}
GUI_LOOP_SECONDS = 20.0
app = QGuiApplication.instance() or QGuiApplication([])


def make_png(width: int = 40, height: int = 60) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def assemble(tmp: Path, pages: int):
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("posthoc-W1")
    chapter = services.library.create_chapter(
        book.book_id, "条漫话", chapter_type="webtoon", reading_direction="vertical"
    )
    services.importer.import_files(
        chapter.chapter_id,
        [
            ImportSource(filename=f"p{i}.png", data_provider=lambda i=i: make_png())
            for i in range(1, pages + 1)
        ],
    )
    return services, chapter


def plan(services, chapter):
    run = services.pipeline.create_run(
        CommandType.TRANSLATE_ALL.value,
        PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
    )
    services.pipeline.plan_run(run.run_id)
    return run


def page_ids(db: Path) -> list[str]:
    conn = sqlite3.connect(str(db))
    try:
        return [row[0] for row in conn.execute(
            "SELECT page_id FROM pages ORDER BY sort_order"
        )]
    finally:
        conn.close()


def run_on_controller(services, run, timeout=60.0):
    crashed: list[str] = []
    finished: list[str] = []
    controller = RunController()
    controller.runCrashed.connect(lambda _id, error: crashed.append(error))
    controller.runFinished.connect(lambda _id, status: finished.append(status))
    controller.start(services.pipeline, run)
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline and not finished and not crashed:
        app.processEvents()
        time.sleep(0.005)
    controller.shutdown()
    return crashed, finished


def db_run_status(db: Path, run_id: str):
    conn = sqlite3.connect(str(db))
    try:
        row = conn.execute(
            "SELECT status FROM pipeline_runs WHERE run_id = ?", (run_id,)
        ).fetchone()
    finally:
        conn.close()
    return row[0] if row else None


def new_tally():
    return {
        "attempts": 0, "created": 0, "translated": 0, "raised": 0,
        "kinds": Counter(), "first": {},
    }


def gui_commit_loop(services, pages, stop_at, tally):
    """The production GUI-thread write path: create region + save translation."""
    index = 0
    while time.monotonic() < stop_at:
        page_id = pages[index % len(pages)]
        index += 1
        tally["attempts"] += 1
        try:
            region = services.editing.create_region(
                page_id,
                RegionGeometry(bbox=BBox((11 * index) % 200, 20, 60, 40)),
                region_type=RegionType.SPEECH,
            )
            tally["created"] += 1
            app.processEvents()
            services.editing.save_manual_translation(region.region_id, f"译文 {index}")
            tally["translated"] += 1
        except Exception as error:  # noqa: BLE001 - the exception IS the measurement
            tally["raised"] += 1
            key = f"{type(error).__module__}.{type(error).__name__}"
            tally["kinds"][key] += 1
            tally["first"].setdefault(key, str(error)[:240])
        app.processEvents()


def invariants(db: Path):
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    report = {}
    try:
        report["pointer_points_at_other_region"] = conn.execute(
            "SELECT COUNT(*) FROM regions r JOIN region_revisions v"
            " ON v.region_revision_id = r.current_revision_id"
            " WHERE r.deleted_at IS NULL AND v.region_id <> r.region_id"
        ).fetchone()[0]
        # a half-created region: add_region committed but the revision seam
        # never landed (the BEGIN IMMEDIATE raised against the worker's txn)
        report["regions_with_null_pointer"] = conn.execute(
            "SELECT COUNT(*) FROM regions WHERE deleted_at IS NULL"
            " AND current_revision_id IS NULL"
        ).fetchone()[0]
        report["revisions_without_region_row"] = conn.execute(
            "SELECT COUNT(*) FROM region_revisions v LEFT JOIN regions r"
            " ON r.region_id = v.region_id"
            " WHERE r.region_id IS NULL OR v.region_id <> r.region_id"
        ).fetchone()[0]
        report["pointer_dangling"] = conn.execute(
            "SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions v"
            " ON v.region_revision_id = r.current_revision_id"
            " WHERE r.deleted_at IS NULL AND r.current_revision_id IS NOT NULL"
            " AND v.region_revision_id IS NULL"
        ).fetchone()[0]
        torn = 0
        for row in conn.execute(
            "SELECT r.text_json, r.geometry_json, v.snapshot_json"
            " FROM regions r JOIN region_revisions v"
            " ON v.region_revision_id = r.current_revision_id"
            " WHERE r.deleted_at IS NULL"
        ).fetchall():
            snapshot = json.loads(row["snapshot_json"])
            if json.dumps(snapshot["text"], ensure_ascii=False, sort_keys=True) != row["text_json"]:
                torn += 1
            elif json.dumps(snapshot["geometry"], ensure_ascii=False, sort_keys=True) != row["geometry_json"]:
                torn += 1
        report["state_torn_vs_current_revision"] = torn
        report["integrity_check"] = conn.execute("PRAGMA integrity_check").fetchone()[0]
        report["foreign_key_check_rows"] = len(conn.execute("PRAGMA foreign_key_check").fetchall())
    finally:
        conn.close()
    return report


print(f"== tree: {ROOT}")
print(f"== sqlite3.threadsafety = {sqlite3.threadsafety} (docstring premise #1 needs 3=serialized)")

# ------------------------------------------------------------------- Part A
tmp_a = Path(tempfile.mkdtemp(prefix="ph-w1-a-"))
services, chapter = assemble(tmp_a, pages=6)
run = plan(services, chapter)
crashed, finished = run_on_controller(services, run)
status = db_run_status(tmp_a / "library.db", run.run_id)
print(
    "\n-- A uphold (real assembly + real RunController + TRANSLATE_ALL):"
    f" crashed={len(crashed)} finished={finished} db_status={status}"
    f" -> {'P0 FIX REPRODUCED' if not crashed and status in TERMINAL else 'NOT REPRODUCED'}"
)

# ------------------------------------------------------------------- Part B
tmp_b = Path(tempfile.mkdtemp(prefix="ph-w1-b-"))
db_b = tmp_b / "library.db"
services, chapter = assemble(tmp_b, pages=40)
pages_b = page_ids(db_b)
run = plan(services, chapter)
tally = new_tally()
controller = RunController()
crashed_b: list[str] = []
finished_b: list[str] = []
controller.runCrashed.connect(lambda _id, error: crashed_b.append(error))
controller.runFinished.connect(lambda _id, status: finished_b.append(status))
controller.start(services.pipeline, run)
stop_at = time.monotonic() + GUI_LOOP_SECONDS
gui_commit_loop(services, pages_b, stop_at, tally)
while time.monotonic() < stop_at and not finished_b and not crashed_b:
    app.processEvents()
    time.sleep(0.005)
controller.shutdown()
print(
    f"\n-- B realism ({GUI_LOOP_SECONDS:.0f}s of real GUI region commits during a real run)"
    f"\n   GUI attempts={tally['attempts']} raised={tally['raised']}"
    f" created={tally['created']} translated={tally['translated']}"
    f"\n   run: crashed={len(crashed_b)} finished={finished_b}"
    f" db_status={db_run_status(db_b, run.run_id)}"
)
for error in crashed_b:  # run5+: the crash text is the point, not just its count
    print(f"   run crash payload: {str(error)[:400]}")
for kind, count in tally["kinds"].most_common():
    print(f"   {count:6d}x {kind}\n          first: {tally['first'][kind]}")
verify = sqlite3.connect(str(db_b))
durable_regions = verify.execute(
    "SELECT COUNT(*) FROM regions WHERE deleted_at IS NULL"
).fetchone()[0]
verify.close()
print(
    f"   durability: GUI create_region succeeded={tally['created']},"
    f" region rows durable={durable_regions}"
    f", lost={tally['created'] - durable_regions}"
)
print(f"   invariants: {invariants(db_b)}")

# ------------------------------------------------------------------- Part C
tmp_c = Path(tempfile.mkdtemp(prefix="ph-w1-c-"))
services_c, chapter_c = assemble(tmp_c, pages=8)
tally_c = new_tally()
gui_commit_loop(services_c, page_ids(tmp_c / "library.db"), time.monotonic() + GUI_LOOP_SECONDS / 2, tally_c)
print(
    f"\n-- C control (same GUI loop, NO worker run): attempts={tally_c['attempts']}"
    f" raised={tally_c['raised']} kinds={dict(tally_c['kinds'])}"
)

# ------------------------------------------------------------------- Part D
tmp_d = Path(tempfile.mkdtemp(prefix="ph-w1-d-"))
db_d = tmp_d / "library.db"
services_d, chapter_d = assemble(tmp_d, pages=2)
shared = services_d.conn  # the ONE production connection every service holds
region = services_d.editing.create_region(
    page_ids(db_d)[0], RegionGeometry(bbox=BBox(1, 2, 30, 40))
)
print("\n-- D mechanism (forced schedule; `with conn:` shape = pipeline.py:398)")

hold = threading.Event()
release = threading.Event()
d_errors: dict[str, str] = {}


def worker_transaction():
    try:
        with shared:  # production shape: `with self._conn:` around a write
            shared.execute("DELETE FROM pipeline_runs WHERE run_id = '__probe__'")
            hold.set()
            release.wait(10)
    except Exception as error:  # noqa: BLE001
        d_errors["worker"] = repr(error)


threading.Thread(target=worker_transaction, daemon=True).start()
hold.wait(5)
try:
    services_d.editing.save_manual_translation(region.region_id, "并发下写的译文")
    print("   D1 GUI BEGIN IMMEDIATE against a worker-held txn: NO exception")
except Exception as error:  # noqa: BLE001
    print(f"   D1 GUI BEGIN IMMEDIATE against a worker-held txn: {type(error).__name__}: {str(error)[:170]}")
release.set()
time.sleep(0.2)
print(f"   D1 worker side: {d_errors.get('worker', 'no error')}"
      "  (a worker rollback here would also erase GUI work in flight)")

# D2: GUI mid-`commit_region_revision` (revision inserted, region row not yet
# updated) and a worker-shaped commit lands in between; the GUI txn then fails
# and rolls back.  regions.py:7 promises it rolls back *entirely*.
gui_arrived = threading.Event()
worker_committed = threading.Event()
revision_id = "ph-w1-rev"


def gui_half_commit():
    try:
        shared.execute("BEGIN IMMEDIATE")
        shared.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES (?, ?, 999, ?, 'user', 'unreviewed', 0,"
            " '2026-01-01T00:00:00+00:00')",
            (
                revision_id,
                region.region_id,
                json.dumps({
                    "text": {"edited_translation": "半提交"}, "geometry": {},
                    "style": {}, "region_type": "speech", "reading_order": 1,
                    "sfx_policy": "skip", "region_locked": 0,
                    "translation_locked": 0, "inpaint_locked": 0,
                }, ensure_ascii=False),
            ),
        )
        gui_arrived.set()
        worker_committed.wait(5)
        raise RuntimeError("simulated failure after the foreign commit")
    except Exception as error:  # noqa: BLE001
        shared.rollback()  # exactly regions.py:274
        d_errors["gui"] = repr(error)
    finally:
        pass


threading.Thread(target=gui_half_commit, daemon=True).start()
gui_arrived.wait(5)
with shared:  # the worker's persist shape commits on exit - and commits the
    shared.execute("DELETE FROM pipeline_runs WHERE run_id = '__probe__2'")
worker_committed.set()
time.sleep(0.3)
check = sqlite3.connect(str(db_d))
survived = check.execute(
    "SELECT COUNT(*) FROM region_revisions WHERE region_revision_id = ?", (revision_id,)
).fetchone()[0]
pointer = check.execute(
    "SELECT current_revision_id FROM regions WHERE region_id = ?", (region.region_id,)
).fetchone()[0]
check.close()
print(
    f"   D2 after the GUI rollback: orphan revision rows={survived}"
    f" (0 expected if 'rolling back entirely' held); region pointer={pointer}"
)
print(f"   D2 invariants: {invariants(db_d)}")

# D3: the deterministic version of what the window logged as a timing float
# (verification/TASK-056/revision-full-suite-run2.log:67 -> line 177 of
# tests/workbench/test_run_thread_e2e.py).  GUI thread inside its `with conn:`
# write (library.py:109 shape) while the worker's error path rolls the SAME
# connection back (pipeline.py:622, commit_step's `except Exception: rollback()`).
gui_in_txn = threading.Event()
worker_rolled = threading.Event()
d3: dict[str, str] = {}


def gui_writer():
    try:
        with shared:  # production shape: SqliteLibraryRepository write
            shared.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('ph-w1-lost', '丢失的书',"
                " '2026-01-01T00:00:00+00:00', '2026-01-01T00:00:00+00:00')"
            )
            gui_in_txn.set()
            worker_rolled.wait(5)
        d3["outcome"] = "returned normally (its commit() had nothing left to commit)"
    except Exception as error:  # noqa: BLE001
        d3["outcome"] = f"raised {type(error).__name__}: {error}"


threading.Thread(target=gui_writer, daemon=True).start()
gui_in_txn.wait(5)
shared.rollback()  # exactly pipeline.py:622
worker_rolled.set()
time.sleep(0.3)
check = sqlite3.connect(str(db_d))
durable_book = check.execute(
    "SELECT COUNT(*) FROM books WHERE book_id = 'ph-w1-lost'"
).fetchone()[0]
check.close()
print(
    f"   D3 GUI write: {d3['outcome']}; rows durable={durable_book}"
    " -> 0 means a silently lost user write (the 'flaky' signature)"
)
