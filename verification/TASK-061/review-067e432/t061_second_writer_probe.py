r"""TASK-061 review, second probe (Qoder, non-author): the four faces the
shipped cases and t061_review_probe.py leave unmeasured.

Run:  python t061_second_writer_probe.py [tree_root]

M1  positive direction of the AC ④ predicate: does ``any_in_transaction()``
    actually see *another* thread's open write transaction?  The shipped
    case (``test_any_in_transaction_tracks_the_callers_own_transaction``)
    only ever measures the calling thread's own — which is the semantics
    the same slice just documented as a trap (R-004).
M2  what eviction does to an *uncommitted* write: a worker that dies with a
    half-open transaction — is the aggregate view clean again, and is the
    row really rolled back on disk?
M3  cost attribution for focus ③: how much of ``remove_managed`` is the new
    6-step lstat walk, and how much is the pre-existing ``resolve()``?
M4  does ``open_connection_count()`` (an observability call from the GUI
    thread) *execute statements* on other threads' live connections, and
    what does that do to a worker holding an open transaction?
M5  leading-segment asymmetry: the lexical rule checks emptiness only for
    ``segments[1:]``, so a leading ``/`` (or ``\``) is not refused on
    Windows even though ``Path.parts``-based POSIX resolution differs.
"""

from __future__ import annotations

import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[2]
ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else DEFAULT_ROOT
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage  # noqa: E402

from application.importing.images.ports import ImportSource  # noqa: E402
from bootstrap.app import assemble_services  # noqa: E402
from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ImmutablePathViolation,
    ManagedFileStorage,
)

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


def make_png() -> bytes:
    image = QImage(40, 60, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def assemble(tmp: Path):
    services = assemble_services(tmp / "library.db", tmp / "managed")
    book = services.library.create_book("探针书")
    chapter = services.library.create_chapter(
        book.book_id, "话", chapter_type="webtoon", reading_direction="vertical"
    )
    services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="p1.png", data_provider=make_png)],
    )
    return services, chapter


def registry(services) -> int:
    getter = getattr(services.conn, "registry_size", None)
    if getter is not None:
        return getter()
    return len(getattr(services.conn, "_connections", {}))


def any_tx(services):
    getter = getattr(services.conn, "any_in_transaction", None)
    return getter() if getter is not None else "<absent pre-fix>"


# ---------------------------------------------------------------- M1 / M4
print("\n-- M1 aggregate view of a FOREIGN open write transaction (+ M4)")
tmp1 = Path(tempfile.mkdtemp(prefix="t061-m1-"))
services, _chapter = assemble(tmp1)
hold = threading.Event()
free = threading.Event()
notes: list[str] = []


def writer() -> None:
    conn = services.conn
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('m1-orphan', 'M1', 'now', 'now')"
        )
        hold.set()
        free.wait(15)
        conn.rollback()
    except Exception:  # noqa: BLE001
        notes.append(traceback.format_exc(limit=3))


before = registry(services)
t = threading.Thread(target=writer, daemon=True)
t.start()
hold.wait(5)
print(f"   registry {before} -> {registry(services)} (worker registered)")
print(
    f"   worker is in an open write transaction; GUI-side"
    f" any_in_transaction() -> {any_tx(services)}   <-- the aggregate must be True"
    " for AC ④ to mean anything"
)
print(f"   GUI thread's own in_transaction (per-thread trap): {services.conn.in_transaction}")

# M4: does the observability call execute on the worker's live handle?
probe_out = "<absent pre-fix>"
if hasattr(services.conn, "open_connection_count"):
    started = time.perf_counter()
    try:
        probe_out = f"returned {services.conn.open_connection_count()}"
    except Exception as error:  # noqa: BLE001
        probe_out = f"RAISED {type(error).__name__}: {error}"
    print(
        f"   M4 open_connection_count() while a foreign txn is open: {probe_out}"
        f" ({(time.perf_counter() - started) * 1000:.1f} ms)"
        "   <-- it runs SELECT 1 on every registered connection, including"
        " another thread's"
    )
print(f"   releasing the worker (it rolls back on the way out)")
free.set()
t.join(10)
print(f"   any_in_transaction after the worker finished -> {any_tx(services)}")
for n in notes[:2]:
    print("   " + n.replace("\n", " | "))
print(
    "   M1/M4 note: the aggregate reads are taken from the GUI thread against a"
    " connection owned by another thread (check_same_thread=False)."
)
sys.stdout.flush()

# ---------------------------------------------------------------- M2
print("\n-- M2 eviction of a worker that dies with a HALF-OPEN transaction")
tmp2 = Path(tempfile.mkdtemp(prefix="t061-m2-"))
services2, _ = assemble(tmp2)
hold2 = threading.Event()
notes2: list[str] = []


def suicide_writer() -> None:
    conn = services2.conn
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('m2-orphan', 'M2', 'now', 'now')"
        )
        hold2.set()
        # return with the transaction open: no commit, no rollback, no close
    except Exception:  # noqa: BLE001
        notes2.append(traceback.format_exc(limit=3))


t2 = threading.Thread(target=suicide_writer, daemon=True)
t2.start()
hold2.wait(5)
t2.join()
time.sleep(0.5)
print(
    f"   after the writer died: registry={registry(services2)}"
    f" any_in_transaction={any_tx(services2)}"
)
judge2 = sqlite3.connect(str(tmp2 / "library.db"))
rows = judge2.execute(
    "SELECT COUNT(*) FROM books WHERE book_id = 'm2-orphan'"
).fetchone()[0]
judge2.close()
print(
    f"   was the half-open row published? {rows > 0}"
    " (False = eviction's close() rolled the dead thread's transaction back)"
)
for n in notes2[:2]:
    print("   " + n.replace("\n", " | "))
sys.stdout.flush()

# ---------------------------------------------------------------- M3
print("\n-- M3 cost attribution: lstat walk vs resolve() vs the unlink")
tmp3 = Path(tempfile.mkdtemp(prefix="t061-m3-"))
storage3 = ManagedFileStorage(tmp3 / "managed")
storage3.ensure_layout()
rel = "books/b/chapters/c/original/r.png"
segments = rel.split("/")


def median(samples, k=0.5):
    samples = sorted(samples)
    return samples[int(len(samples) * k)]


def timeit(fn, n=400):
    out = []
    for _ in range(n):
        started = time.perf_counter()
        fn()
        out.append((time.perf_counter() - started) * 1e6)
    return out


probe = storage3.root / Path(*segments)
probe.parent.mkdir(parents=True, exist_ok=True)
probe.write_bytes(b"x")
lstat_walk = []
cursor = storage3.root
for s in segments:
    cursor = cursor / s
    lstat_walk.append(cursor)
lstat_us = median(timeit(lambda: [p.lstat() for p in lstat_walk]))
resolved_us = median(timeit(lambda: (storage3.root / Path(*segments)).resolve()))
root_resolved_us = median(timeit(lambda: storage3.root.resolve()))
whole_us: list[float] = []
for _ in range(120):
    if not probe.exists():
        probe.write_bytes(b"x")
    started = time.perf_counter()
    storage3.remove_managed(rel)
    whole_us.append((time.perf_counter() - started) * 1e6)
print(
    f"   per removal (median us): whole remove_managed={median(whole_us):.0f};"
    f" 6-step lstat walk={lstat_us:.0f}; path resolve={resolved_us:.0f};"
    f" root resolve={root_resolved_us:.0f}"
)
print(
    f"   => the walk is {lstat_us / median(whole_us) * 100:.0f}% of the call"
    f" ({lstat_us:.0f} us of {median(whole_us):.0f} us)"
)
sys.stdout.flush()

# ---------------------------------------------------------------- M5
print("\n-- M5 leading-segment asymmetry")
tmp5 = Path(tempfile.mkdtemp(prefix="t061-m5-"))
storage5 = ManagedFileStorage(tmp5 / "managed")
storage5.ensure_layout()
victim = tmp5 / "managed" / "revisions" / "keep_m5.png"
victim.parent.mkdir(parents=True, exist_ok=True)
victim.write_bytes(b"M5")
print(f"   joinpath('', 'revisions', 'keep_m5.png') -> {storage5.absolute_path('/revisions/keep_m5.png')}")
for ref in ("/revisions/keep_m5.png", "\\revisions\\keep_m5.png", "revisions/keep_m5.png/"):
    if not victim.exists():
        victim.write_bytes(b"M5")
    try:
        storage5.remove_managed(ref)
        verdict = "ALLOWED"
    except ImmutablePathViolation as error:
        verdict = f"typed refusal ({str(error)[:48]})"
    except Exception as error:  # noqa: BLE001
        verdict = f"UNtyped {type(error).__name__}"
    print(f"   {ref!r:<32} -> {verdict}; file survives? {victim.exists()}")
print("\n== done")
