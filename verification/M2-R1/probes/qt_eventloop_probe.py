"""M2-R1 supplementary probe: event loop stability and window census.

Two questions the main matrix does not answer directly:

1. Does a real Qt event loop start and *exit cleanly* without a visible GUI?
   (``QTimer`` + ``QGuiApplication.exec()``, then the process exit code.)
2. What top-level HWNDs does the process actually own — including hidden
   ones — so "no visible GUI" is backed by the full window list, not just a
   visible-window count.

Research only: no production code path, no user data root.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import time
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_ROOT = REPO_ROOT / "src"


def hwnd_census(pid: int) -> dict:
    user32 = ctypes.windll.user32
    entries: list[dict] = []
    proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)

    def _cb(hwnd, _lparam):  # noqa: ANN001
        wpid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(wpid))
        if wpid.value != pid:
            return True
        title_len = user32.GetWindowTextLengthW(hwnd)
        title = ctypes.create_unicode_buffer(title_len + 1)
        user32.GetWindowTextW(hwnd, title, title_len + 1)
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        entries.append(
            {
                "hwnd": f"{int(hwnd):#x}",
                "class": cls.value,
                "title": title.value,
                "visible": bool(user32.IsWindowVisible(hwnd)),
                "iconic": bool(user32.IsIconic(hwnd)),
                "owner": f"{int(user32.GetWindow(hwnd, 4)):#x}",  # GW_OWNER = 4
            }
        )
        return True

    user32.EnumWindows(proc(_cb), 0)
    return {
        "top_level_windows": len(entries),
        "visible_windows": sum(1 for e in entries if e["visible"]),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--platform", required=True)
    parser.add_argument("--json", required=True)
    parser.add_argument("--loop-ms", type=int, default=300)
    args = parser.parse_args()

    os.environ["QT_QPA_PLATFORM"] = args.platform
    report: dict = {
        "probe": "M2-R1 event-loop / window-census probe",
        "platform_requested": args.platform,
        "pid": os.getpid(),
        "python": sys.version.replace("\n", " "),
        "python_executable": sys.executable,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "errors": [],
        "exit_code": None,
    }
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    try:
        import PySide6
        from PySide6.QtCore import QTimer, qVersion
        from PySide6.QtGui import QGuiApplication

        report["PySide6.__version__"] = PySide6.__version__
        report["qVersion"] = qVersion()

        app = QGuiApplication.instance() or QGuiApplication([sys.argv[0]])
        report["platformName"] = app.platformName()
        report["topLevelWindows_before_loop"] = len(app.topLevelWindows())
        report["census_before_loop"] = hwnd_census(report["pid"])

        fired = {"timer": False}

        def _tick() -> None:
            fired["timer"] = True
            app.quit()

        QTimer.singleShot(args.loop_ms, _tick)
        t0 = time.perf_counter()
        rc = app.exec()
        elapsed = time.perf_counter() - t0
        report["event_loop"] = {
            "requested_ms": args.loop_ms,
            "timer_fired": fired["timer"],
            "exec_return_code": int(rc),
            "wall_seconds": round(elapsed, 4),
            "exited_within_budget": elapsed < (args.loop_ms / 1000.0) + 5.0,
        }
        report["census_after_loop"] = hwnd_census(report["pid"])
        report["topLevelWindows_after_loop"] = len(app.topLevelWindows())
    except BaseException as exc:  # noqa: BLE001
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        report["traceback"] = traceback.format_exc()

    report["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    report["exit_code"] = 0 if not report["errors"] else 2
    Path(args.json).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    loop = report.get("event_loop", {})
    print(
        f"[loop] platform={args.platform} platformName={report.get('platformName')} "
        f"exec_rc={loop.get('exec_return_code')} timer_fired={loop.get('timer_fired')} "
        f"wall={loop.get('wall_seconds')}s visible_windows="
        f"{report.get('census_after_loop', {}).get('visible_windows')} "
        f"top_level={report.get('census_after_loop', {}).get('top_level_windows')} "
        f"exit_code={report['exit_code']}"
    )
    return report["exit_code"]


if __name__ == "__main__":
    try:
        code = main()
    except BaseException:  # noqa: BLE001
        traceback.print_exc()
        code = 3
    sys.exit(code)
