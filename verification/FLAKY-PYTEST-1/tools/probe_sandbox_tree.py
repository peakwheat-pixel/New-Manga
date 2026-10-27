#!/usr/bin/env python
"""FLAKY-PYTEST-1 AC1 probe: how long does the sandbox job tree actually live?

Replicates ``tests/infrastructure/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren``
against the production ``AppContainerSandbox`` + ``PluginService`` and polls the
grandchild for up to ``--window`` seconds per iteration, recording:

  * whether the grandchild ever dies,
  * how long it takes (ms),
  * whether the assertion window used by the test (2 s) is sufficient.

Run from the FLAKY-PYTEST-1 worktree:
  python <this> [iterations] [window_seconds]
"""
from __future__ import annotations

import ctypes
import json
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\FLAKY-PYTEST-1")
sys.path.insert(0, str(REPO / "src"))

from infrastructure.plugins.sandbox import AppContainerSandbox  # noqa: E402
from infrastructure.plugins.service import PluginService  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

HOOK_SOURCE = (
    "import subprocess, sys\n"
    "def after_detect(payload):\n"
    "    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(120)'])\n"
    "    return {'pid': child.pid}\n"
)
MANIFEST = {
    "id": "acme-tree",
    "name": "acme-tree",
    "version": "1.0.0",
    "entry": "plugin.py",
    "hooks": ["after_detect"],
    "permissions": [],
    "description": "sandbox tree probe",
}

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
kernel32.OpenProcess.restype = ctypes.c_void_p


def alive(pid: int) -> bool:
    handle = kernel32.OpenProcess(0x1000, False, pid)
    try:
        return bool(handle)
    finally:
        if handle:
            kernel32.CloseHandle(ctypes.c_void_p(handle))


def one(iteration: int, window: float) -> dict:
    root = Path(tempfile.mkdtemp(prefix=f"flaky-probe-{iteration}-"))
    conn, _ = open_database(
        root / "library.db",
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    plugins = root / "plugins" / "acme-tree"
    plugins.mkdir(parents=True)
    (plugins / "plugin.py").write_text(HOOK_SOURCE, encoding="utf-8")
    (plugins / "manifest.json").write_text(json.dumps(MANIFEST), encoding="utf-8")
    sandbox = AppContainerSandbox()
    service = PluginService(conn, root / "plugins", app_version="0.1.0", sandbox=sandbox)
    record: dict = {"iteration": iteration}
    try:
        service.set_global_enabled(True)
        service.set_plugin_enabled("acme-tree", True)
        started = time.monotonic()
        outcome = service.run_hook("after_detect", {})
        record["hook_ms"] = round((time.monotonic() - started) * 1000, 1)
        record["applied"] = outcome.get("applied")
        record["errors"] = outcome.get("errors")
        pid = int(outcome["results"][0]["result"]["pid"])
        record["pid"] = pid
        poll_start = time.monotonic()
        died_after = None
        while time.monotonic() - poll_start < window:
            if not alive(pid):
                died_after = round((time.monotonic() - poll_start) * 1000, 1)
                break
            time.sleep(0.02)
        record["died_after_ms"] = died_after
        record["alive_after_window"] = died_after is None
        record["within_test_2s"] = died_after is not None and died_after <= 2000
    finally:
        sandbox.close()
        conn.close()
    return record


def main() -> int:
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    window = float(sys.argv[2]) if len(sys.argv) > 2 else 30.0
    results = [one(index + 1, window) for index in range(iterations)]
    for row in results:
        print(json.dumps(row, ensure_ascii=False), flush=True)
    summary = {
        "iterations": iterations,
        "window_s": window,
        "within_test_2s": sum(1 for r in results if r.get("within_test_2s")),
        "alive_after_window": sum(1 for r in results if r.get("alive_after_window")),
        "died_after_ms": [r.get("died_after_ms") for r in results],
    }
    print("SUMMARY " + json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
