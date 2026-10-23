"""Small subprocess / filesystem helpers for the software smoke tool."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"


class CommandResult:
    """Captured result of one subprocess run, including a written log file."""

    def __init__(
        self,
        argv: list[str],
        exit_code: int,
        stdout: str,
        stderr: str,
        duration_ms: int,
        timed_out: bool,
        log_path: Path | None,
    ) -> None:
        self.argv = argv
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.timed_out = timed_out
        self.log_path = log_path

    @property
    def combined(self) -> str:
        return self.stdout + self.stderr


def make_run_root(prefix: str = "nm-software-smoke-") -> Path:
    return Path(tempfile.mkdtemp(prefix=prefix))


def remove_tree(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def tail(text: str, limit: int = 900) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return "…" + text[-limit:]


def write_log(path: Path, header: str, result: "CommandResult | None" = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [header]
    if result is not None:
        lines.append(f"# exit: {result.exit_code} timed_out={result.timed_out}")
        lines.append("# stdout:")
        lines.append(result.stdout)
        lines.append("# stderr:")
        lines.append(result.stderr)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_command(
    argv: list[str],
    *,
    cwd: Path,
    timeout: float,
    log_path: Path | None = None,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """Run one command, capture text output and persist a full log when asked."""

    started = time.perf_counter()
    timed_out = False
    stdout = ""
    stderr = ""
    exit_code = -1
    try:
        completed = subprocess.run(
            argv,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_code = -1
        stdout = _as_text(error.stdout)
        stderr = _as_text(error.stderr)
        stderr = (stderr + f"\nTIMEOUT after {timeout}s").strip()
    duration_ms = int((time.perf_counter() - started) * 1000)
    result = CommandResult(
        argv=list(argv),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        duration_ms=duration_ms,
        timed_out=timed_out,
        log_path=log_path,
    )
    if log_path is not None:
        header = (
            f"# command: {subprocess.list2cmdline(argv)}\n"
            f"# cwd: {cwd}\n"
            f"# started: {now_iso()}"
        )
        write_log(log_path, header, result)
    return result


def _as_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def child_environment(
    *,
    data_root: Path,
    src_root: Path = SRC_ROOT,
    derived_root: Path | None = None,
    catalog_db: Path | None = None,
) -> dict[str, str]:
    """Hermetic environment for a real Core subprocess (no host detector env)."""

    env = os.environ.copy()
    for key in (
        "NEWMANGA_DETECTOR_WEIGHTS",
        "NEWMANGA_DETECTOR_BACKEND",
        "M2RC1_PROBE_OUT",
        "M2AC1_TEST_MODE",
        "M2RC1_PACKAGED",
        "M2RC1_FIXTURES",
    ):
        env.pop(key, None)
    env["PYTHONPATH"] = str(src_root)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["NEWMANGA_DATA_ROOT"] = str(data_root)
    env["M2RC1_DERIVED_ROOT"] = str(derived_root or (data_root / "derived"))
    env["M2RC2_CATALOG_DB"] = str(
        catalog_db or (data_root / "catalog" / "catalog.sqlite")
    )
    return env


def is_pid_alive(pid: int) -> bool:
    """Windows process-liveness probe (no extra dependency)."""

    if os.name != "nt":
        return False
    if pid <= 0:
        return False
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    handle = kernel32.OpenProcess(0x1000, False, int(pid))  # QUERY_LIMITED_INFORMATION
    if not handle:
        return False
    try:
        exit_code = ctypes.c_ulong(0)
        kernel32.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        if not kernel32.GetExitCodeProcess(ctypes.c_void_p(handle), ctypes.byref(exit_code)):
            return True
        return exit_code.value == 259  # STILL_ACTIVE
    finally:
        kernel32.CloseHandle(ctypes.c_void_p(handle))


def wait_pid_gone(pid: int, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if not is_pid_alive(pid):
            return True
        time.sleep(0.1)
    return not is_pid_alive(pid)


def find_executable(names: tuple[str, ...]) -> str | None:
    for name in names:
        found = shutil.which(name)
        if found:
            return found
    return None


def ensure_src_on_path() -> None:
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))
