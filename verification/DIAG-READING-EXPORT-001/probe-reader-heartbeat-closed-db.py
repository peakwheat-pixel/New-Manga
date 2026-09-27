"""DIAG-READING-EXPORT-001 probe 2 (read-only): leaked reader heartbeat writing
into a closed SQLite reading store.

Question (falsifiable): does a ``ReaderViewModel`` whose chapter was opened keep
its 5 s heartbeat alive after the owning store/connection is torn down, and does
the next fire reproduce the historical stderr trace
``settleReadingTime -> add_time -> _touch -> _persist -> store.write ->
sqlite3.ProgrammingError: Cannot operate on a closed database``?

Method (no product/test file is edited, no monkeypatching):
 1. build the real production adapters -- ``SqliteReadingProgressStore`` +
    ``ReadingService`` + ``ReaderViewModel`` -- exactly as ``assemble_services``
    wires them;
 2. ``openChapter`` through the ViewModel (which starts the heartbeat) and
    record ``_heartbeat.isActive()``;
 3. close the store the way a test teardown does, then
    (a) call ``settleReadingTime()`` synchronously and capture the exception,
    (b) run the real Qt event loop long enough for the heartbeat to fire and
        capture what the timer slot raises, and confirm the timer keeps running.

Run with the frozen interpreter:
  python verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.py
"""

from __future__ import annotations

import sys
import tempfile
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from PySide6.QtCore import QEventLoop, QTimer  # noqa: E402
from PySide6.QtGui import QGuiApplication  # noqa: E402

from application.reading import ReaderPage, ReadingService  # noqa: E402
from infrastructure.sqlite import SqliteReadingProgressStore  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import SCHEMA_VERSION_V4, default_migrations  # noqa: E402
from ui.viewmodels.reader.viewmodel import ReaderViewModel  # noqa: E402

HEARTBEAT_MS = 5000


class Catalog:
    """ReaderPageCatalog-shaped fake over a fixed page list (as in the tests)."""

    def __init__(self, pages):
        self.pages = pages

    def list_pages(self, chapter_id):
        return list(self.pages)


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    captured: list[str] = []
    original_hook = sys.excepthook

    def hook(exc_type, exc, tb):
        captured.append("".join(traceback.format_exception(exc_type, exc, tb)))
        original_hook(exc_type, exc, tb)

    sys.excepthook = hook

    with tempfile.TemporaryDirectory() as temp:
        lab = Path(temp)
        db = lab / "library.db"
        page_dir = lab / "pages"
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "p0.png").write_bytes(b"PNG-0")
        pages = [
            ReaderPage(
                page_id="p0",
                filename="p0.png",
                original_path=str(page_dir / "p0.png"),
            )
        ]

        store_conn, _opened = open_database(db, latest_known_schema_version=SCHEMA_VERSION_V4)
        MigrationRunner(store_conn, default_migrations()).apply_pending()
        store = SqliteReadingProgressStore(store_conn)
        service = ReadingService(store)
        vm = ReaderViewModel(service, Catalog(pages))
        vm.openChapter("b", "c", "第1话", "paged", "rtl")

        print(f"after openChapter : heartbeat active = {vm._heartbeat.isActive()}")
        print(f"                    hasChapter      = {vm.hasChapter}")
        print(f"                    progress loaded = {service.progress is not None}")

        # ---- teardown equivalent: the store/connection is closed -------------
        store_conn.close()
        print("sqlite connection closed (teardown equivalent: tests/.../fresh_db yields conn.close())")

        # (a) deterministic: the same call the heartbeat makes
        print("\n--- (a) synchronous settleReadingTime() after close ---")
        try:
            vm._last_settle = time.monotonic() - 1.0
            vm.settleReadingTime()
            print("RESULT: no exception (unexpected)")
        except Exception as error:  # noqa: BLE001
            print(f"RESULT: {type(error).__module__}.{type(error).__name__}: {error}")
            print("call chain:", " -> ".join(
                f"{frame.name}" for frame in traceback.extract_tb(error.__traceback__)
            ))

        # (b) the real timer: run the event loop past one heartbeat interval
        print(f"\n--- (b) real QTimer heartbeat (interval {HEARTBEAT_MS} ms) ---")
        before = len(captured)
        loop = QEventLoop()
        QTimer.singleShot(HEARTBEAT_MS + 800, loop.quit)
        loop.exec()
        new_traces = len(captured) - before
        print(f"unhandled exceptions captured while the loop ran: {new_traces}")
        for text in captured[before:]:
            print(text.rstrip())
        print(f"heartbeat still active after the failed fire = {vm._heartbeat.isActive()}")
        print(
            "verdict: "
            + (
                "LEAK CONFIRMED -- an unclosed reader heartbeat writes a closed store"
                if new_traces
                else "no unhandled exception observed in this window"
            )
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
