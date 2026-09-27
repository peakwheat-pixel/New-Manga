"""DIAG-READING-EXPORT-001-FIX-B verification probe (read-only).

Question (falsifiable): after the fix, does a reader heartbeat that fires
after the storage connection was torn down (a) raise nothing through the
event loop, (b) stop itself (no repeat every HEARTBEAT_MS), and (c) leave
the typed failure diagnosable on the view model?

Method mirrors the DIAG-READING-EXPORT-001 probe 2 (deterministic pre-fix
reproduction, archived there): build the real production adapters
(``open_database`` + ``MigrationRunner`` + ``SqliteReadingProgressStore`` +
``ReadingService`` + ``ReaderViewModel``), ``openChapter`` (heartbeat
active), close the connection, then

  (a) run the REAL Qt event loop past one full heartbeat interval and
      verify: zero unhandled exceptions, heartbeat stopped,
      ``heartbeat_error`` recorded;
  (b) after that, keep running the loop for one more interval and verify
      still zero exceptions (a stopped timer cannot repeat);
  (c) synchronous ``settleReadingTime()`` calls after the loss stay safe.

No product or test file is edited or monkeypatched.  Exit code: 0 = all
checks passed, 1 = any check failed.

Run with the frozen interpreter:
  python verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.py
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


def wait_ms(ms: int) -> None:
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication([])
    captured: list[str] = []
    original_hook = sys.excepthook

    def hook(exc_type, exc, tb):
        captured.append("".join(traceback.format_exception(exc_type, exc, tb)))
        original_hook(exc_type, exc, tb)

    sys.excepthook = hook

    checks: list[tuple[str, bool]] = []
    with tempfile.TemporaryDirectory() as temp:
        lab = Path(temp)
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

        store_conn, _opened = open_database(
            lab / "library.db", latest_known_schema_version=SCHEMA_VERSION_V4
        )
        MigrationRunner(store_conn, default_migrations()).apply_pending()
        service = ReadingService(SqliteReadingProgressStore(store_conn))
        vm = ReaderViewModel(service, Catalog(pages))
        vm.openChapter("b", "c", "第1话", "paged", "rtl")
        checks.append(("heartbeat active after openChapter", vm._heartbeat.isActive()))
        print(f"after openChapter : heartbeat active = {vm._heartbeat.isActive()}")

        store_conn.close()
        print("sqlite connection closed (teardown equivalent)")

        # (a) real event loop across one full heartbeat interval
        print(f"\n--- (a) real QTimer heartbeat, one full interval ({HEARTBEAT_MS} ms + 800 ms) ---")
        before = len(captured)
        wait_ms(HEARTBEAT_MS + 800)
        new_traces = len(captured) - before
        checks.append(("(a) zero unhandled exceptions across one interval", new_traces == 0))
        checks.append(("(a) heartbeat stopped itself", not vm._heartbeat.isActive()))
        checks.append(("(a) failure recorded on the VM", vm.heartbeat_error is not None))
        print(f"unhandled exceptions captured : {new_traces}")
        print(f"heartbeat still active        : {vm._heartbeat.isActive()}")
        print(f"heartbeat_error               : {vm.heartbeat_error!r}")
        for text in captured[before:]:
            print(text.rstrip())

        # (b) one more interval: a stopped timer cannot repeat
        print("\n--- (b) one more interval after the stop ---")
        before = len(captured)
        wait_ms(HEARTBEAT_MS + 800)
        new_traces = len(captured) - before
        checks.append(("(b) zero unhandled exceptions in the second interval", new_traces == 0))
        checks.append(("(b) heartbeat still stopped", not vm._heartbeat.isActive()))
        print(f"unhandled exceptions captured : {new_traces}")
        print(f"heartbeat still active        : {vm._heartbeat.isActive()}")

        # (c) synchronous settles after the loss stay safe
        print("\n--- (c) synchronous settleReadingTime() after the loss ---")
        raised = False
        try:
            vm._last_settle = time.monotonic() - 2.0
            vm.settleReadingTime()
        except Exception as error:  # noqa: BLE001
            raised = True
            print(f"UNEXPECTED RAISE: {type(error).__module__}.{type(error).__name__}: {error}")
        checks.append(("(c) synchronous settle does not raise", not raised))
        print("synchronous settle raised     : " + ("YES (BAD)" if raised else "no"))

    print()
    failed = False
    for name, ok in checks:
        print(f"check [{'PASS' if ok else 'FAIL'}] {name}")
        failed = failed or not ok
    verdict = (
        "LEAK CLOSED -- a torn-down storage under a live heartbeat is recorded, not raised, and the heartbeat stops"
        if not failed
        else "LEAK STILL OPEN -- at least one check failed"
    )
    print(f"verdict: {verdict}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
