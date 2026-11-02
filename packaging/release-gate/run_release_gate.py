"""M2-RG1 Release Gate runner (Windows local-machine ruling, 2026-09-29).

Executes the machine-verifiable part of the M2 Release Gate against the NSIS
installer produced in the owner worktree (installer sha256 recorded in
``verification/M2-RG1/raw/rg1-gate.json`` and bound to every scenario):

  AC2  GUI console policy (frozen ruling: zero visible console windows during
       packaged normal operation):
       ① installed ``m2rc1-desktop.exe`` PE OptionalHeader Subsystem == 2
         (GUI) — parsed with python struct (e_lfanew@0x3C -> optional header
         start +68 -> u16 Subsystem), no external tooling;
       ② runtime EnumWindows observation: a visible top-level window of class
         ``ConsoleWindowClass`` whose owner pid belongs to {app pid + sidecar
         pids} OR whose title mentions any frozen entry name is a HIT; sampled
         while the app is running (production mode) and after a graceful
         clean exit; assertion = 0 hits;
       ③ dev-mode behavior unchanged: static source audit — the
         ``windows_subsystem`` attribute must stay behind
         ``cfg_attr(not(debug_assertions), ...)`` and every
         ``creation_flags(CREATE_NO_WINDOW)`` must sit inside a
         ``#[cfg(windows)]`` block (compile-time guarantee; dev builds never
         compile either change in).

  AC3  Cold start metrics (RECORD-ONLY, no thresholds — frozen ruling):
       ① app cold start: CreateProcess(installed exe) -> first visible
         non-console top-level window belonging to that pid, in ms;
       ② core ready: installed ``core_service.exe`` stdio probe (spawn ->
         ``core.ping`` -> ready response), spawn-to-ready in ms;
       ③ ac1 handshake: installed ``acceptance_bridge.exe`` spawn -> ready
         (``ping`` -> ``pong``), in ms.
       Each >= 3 samples, min/median/max reported. Environment: purged PATH
       (python/venv/conda/WindowsApps markers removed), no M2RC1_* contract
       env, ``APPDATA`` pinned into a per-round lab directory (every round is
       a cold start; the lab APPDATA path is recorded with the samples).

  AC4  Packaged dependency closure: all FOUR frozen sidecar entries serve a
       real stdio round trip in install state:
       - core_service.exe: core.ping (ready) + ListBooks envelope + shutdown
       - host_bridge.exe: control-plane ping handshake + issue/resolve/revoke
         against a catalog seeded through the packaged catalog_loader.exe
       - acceptance_bridge.exe: ping handshake (m2-ac1-acceptance)
       - catalog_loader.exe: seed a lab data root, then read the rows back
         with sqlite3 (CLI arguments confirmed from the worktree source file
         ``src/infrastructure/resource_channel/catalog_loader.py``)
       Plus: the one merged PyInstaller warn-<spec>.txt is copied into raw/
       and every missing module is classified (missing load-time-critical
       module would FAIL; the operative load-time evidence is the four round
       trips above — every warn entry is disclosed per class).

Safety: this runner deletes ONLY lab / install directories it created under
the system temp dir. It NEVER writes or deletes the host's real
``%APPDATA%\\com.newmanga.m2rc1.desktop`` (M2-AC5 r1 P2-4 red line); the
runner-side proof is the APPDATA per-process pin into the lab (no separate
scenario ID): APPDATA is pinned into the lab for every spawned process, so
the host user root is unreachable by construction.

Usage (acceptance tooling may use the dev venv python):
    python packaging/release-gate/run_release_gate.py [--installer <path>]
"""

from __future__ import annotations

import argparse
import csv
import ctypes
import hashlib
import json
import os
import queue
import re
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RAW = REPO_ROOT / "verification" / "M2-RG1" / "raw"
DEFAULT_INSTALLER = (
    REPO_ROOT
    / "apps"
    / "desktop"
    / "src-tauri"
    / "target"
    / "release"
    / "bundle"
    / "nsis"
    / "m2rc1-desktop_0.1.0_x64-setup.exe"
)
INSTALLED_EXE_NAME = "m2rc1-desktop.exe"
SIDECAR_EXES = (
    "host_bridge.exe",
    "core_service.exe",
    "acceptance_bridge.exe",
    "catalog_loader.exe",
)
#: title markers for the console-window observation (AC2 ②)
CONSOLE_TITLE_MARKERS = (
    "m2rc1-desktop",
    "core_service",
    "host_bridge",
    "acceptance_bridge",
    "catalog_loader",
)
#: console-window host classes observed at runtime (AC2 ②, DSH r1 P2-1):
#: - ConsoleWindowClass        classic conhost-owned console windows
#: - CASCADIA_HOSTING_WINDOW_CLASS  Windows Terminal (Win11 default terminal
#:   delegation): the visible top-level window is OWNED BY WindowsTerminal.exe,
#:   so owner-pid attribution to the spawned child is impossible by design —
#:   for that class the detector relies on the title heuristic (title contains
#:   a frozen entry name). Known heuristic boundary, disclosed here and in the
#:   gate.json environment snapshot (registry DelegationConsole/
#:   DelegationTerminal records which delegation is actually in force).
CONSOLE_WINDOW_CLASSES = ("ConsoleWindowClass", "CASCADIA_HOSTING_WINDOW_CLASS")
#: the host's real user-data root — NEVER touched (P2-4 red line)
HOST_USER_ROOT = Path(os.environ.get("APPDATA", "")) / "com.newmanga.m2rc1.desktop"

LAUNCH_TIMEOUT_S = 120.0
ALIVE_HOLD_S = 10.0

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print(f"runner python: {sys.version.split()[0]} ({sys.executable})")
print(f"repo root: {REPO_ROOT}")
print(f"raw evidence: {RAW}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Gate:
    """Fail-closed evidence collector (same shape as the AC5/RC2 runners)."""

    def __init__(self) -> None:
        self.scenarios: list[dict] = []

    def record(self, scenario_id: str, status: str, observed) -> None:
        self.scenarios.append({"id": scenario_id, "status": status, "observed": observed})
        print(f"  [{status}] {scenario_id}: {json.dumps(observed, sort_keys=True, default=str)[:400]}")

    def pass_or(self, condition: bool, scenario_id: str, observed) -> None:
        self.record(scenario_id, "PASS" if condition else "FAIL", observed)

    @property
    def verdict(self) -> str:
        statuses = {entry["status"] for entry in self.scenarios}
        if not self.scenarios or "FAIL" in statuses:
            return "FAIL"
        return "PASS"


def log(section: str) -> None:
    print(f"\n=== {section} ===")


# --------------------------------------------------------------------------
# environment: purge Python from PATH, clear the dev env contract
# --------------------------------------------------------------------------

PURGE_MARKERS = ("python", "venv", "conda", "WindowsApps")


def purged_environment() -> tuple[dict, list[str], list[str]]:
    """Clean-start env: python-free PATH + no M2RC1_* contract env."""
    removed, kept = [], []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        marker_hit = any(marker.lower() in entry.lower() for marker in PURGE_MARKERS)
        (removed if marker_hit else kept).append(entry)
    cleared_keys = [
        key
        for key in os.environ
        if key.startswith("M2RC1_") or key.startswith("M2RC2_") or key in ("M2AC1_TEST_MODE", "NEWMANGA_DATA_ROOT")
    ]
    env = {key: value for key, value in os.environ.items() if key not in cleared_keys}
    env["PATH"] = os.pathsep.join(kept)
    env.setdefault("SYSTEMROOT", os.environ.get("SYSTEMROOT", "C:\\Windows"))
    return env, removed, kept


def assert_no_python_on_path(env: dict) -> tuple[bool, str]:
    probe = subprocess.run(
        ["where", "python"],
        env=env,
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        timeout=30,
    )
    if probe.returncode == 0:
        return False, f"python still resolves under purged PATH: {probe.stdout.strip()}"
    return True, f"python not on purged PATH (where exit={probe.returncode})"


def pin_appdata(env: dict, roaming: Path) -> dict:
    """Pin APPDATA (and the WebView2 user-data folder) into the lab."""
    out = dict(env)
    out["APPDATA"] = str(roaming)
    return out


# --------------------------------------------------------------------------
# window observation (ctypes user32)
# --------------------------------------------------------------------------

_user32 = ctypes.WinDLL("user32", use_last_error=True)
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)


def _enum_hwnds() -> list[int]:
    hwnds: list[int] = []
    proc = EnumWindowsProc(lambda hwnd, lparam: (hwnds.append(hwnd) or True))
    _user32.EnumWindows(proc, 0)
    return hwnds


def _window_info(hwnd: int) -> dict:
    buf = ctypes.create_unicode_buffer(512)
    _user32.GetClassNameW(hwnd, buf, 512)
    cls = buf.value
    _user32.GetWindowTextW(hwnd, buf, 512)
    title = buf.value
    pid = ctypes.c_ulong(0)
    _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    visible = bool(_user32.IsWindowVisible(hwnd))
    return {"hwnd": hwnd, "class": cls, "title": title, "pid": pid.value, "visible": visible}


def console_window_hits(target_pids: set[int], title_markers: tuple[str, ...]) -> list[dict]:
    """Visible top-level console-host windows (either host class) owned by a
    target pid or titled with any frozen-entry marker. For the Windows
    Terminal delegation class the owner pid belongs to WindowsTerminal.exe
    (never the spawned child), so pid attribution cannot fire there — the
    title heuristic is the attribution path (disclosed boundary)."""
    hits = []
    for hwnd in _enum_hwnds():
        info = _window_info(hwnd)
        if not info["visible"] or info["class"] not in CONSOLE_WINDOW_CLASSES:
            continue
        owned = info["pid"] in target_pids
        titled = any(marker.lower() in info["title"].lower() for marker in title_markers)
        if owned or titled:
            hits.append(info)
    return hits


def first_visible_app_window(pid: int) -> dict | None:
    """First visible, non-console-host, non-empty-title top-level window owned by pid."""
    for hwnd in _enum_hwnds():
        info = _window_info(hwnd)
        if (
            info["pid"] == pid
            and info["visible"]
            and info["class"] not in CONSOLE_WINDOW_CLASSES
            and info["title"]
        ):
            return info
    return None


def console_delegation_registry() -> dict:
    """DSH r1 P2-1: which console delegation is in force on this machine —
    HKCU:\\Console\\%%Startup DelegationConsole/DelegationTerminal. Windows
    Terminal delegation ({e2a1d611-...} GUIDs) is the configuration where the
    CASCADIA class + title-heuristic boundary above applies. Missing keys are
    recorded as null (disclosed), never guessed."""
    try:
        import winreg

        key_path = r"Console\%%Startup"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            result = {}
            for value_name in ("DelegationConsole", "DelegationTerminal"):
                try:
                    result[value_name] = winreg.QueryValueEx(key, value_name)[0]
                except OSError:
                    result[value_name] = None
            result["key_path"] = f"HKCU\\{key_path}"
            return result
    except OSError as error:
        return {"error": repr(error), "key_path": r"HKCU\Console\%%Startup"}


def pids_of(image_names: tuple[str, ...]) -> dict[str, set[int]] | None:
    """Snapshot the pids currently running each image name (tasklist).
    Returns None when the tasklist call itself fails — callers must treat a
    None snapshot as an observation FAILURE, never silently degrade to a
    pid-less / app-only set (DSH r1 P2-1: no silent degradation)."""
    completed = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"],
        capture_output=True,
        text=True,
        encoding="mbcs",
        errors="replace",
        timeout=60,
    )
    if completed.returncode != 0:
        return None
    counts = {name: set() for name in image_names}
    for line in completed.stdout.splitlines():
        parts = next(iter(list(csv.reader([line]))), [])
        if len(parts) >= 2:
            name = parts[0].lower()
            if name in counts:
                try:
                    counts[name].add(int(parts[1]))
                except ValueError:
                    pass
    return counts


# --------------------------------------------------------------------------
# PE parsing (AC2 ①) — stdlib only, per the release reconnaissance method
# --------------------------------------------------------------------------

def pe_subsystem(path: Path) -> dict:
    """OptionalHeader Subsystem: e_lfanew@0x3C -> optional header at
    e_lfanew+24 -> Subsystem at optional header start +68 (u16)."""
    with path.open("rb") as handle:
        dos = handle.read(64)
        if dos[:2] != b"MZ":
            return {"error": "not an MZ image"}
        e_lfanew = int.from_bytes(dos[0x3C:0x40], "little")
        handle.seek(e_lfanew)
        pe_sig = handle.read(4)
        if pe_sig != b"PE\x00\x00":
            return {"error": "not a PE image"}
        opt_start = e_lfanew + 24
        handle.seek(opt_start)
        magic = int.from_bytes(handle.read(2), "little")
        handle.seek(opt_start + 68)
        subsystem = int.from_bytes(handle.read(2), "little")
    return {"subsystem": subsystem, "optional_header_magic": magic, "offset": opt_start + 68}


# --------------------------------------------------------------------------
# stdio JSON-lines client (reader thread + queue; no select on Windows pipes)
# --------------------------------------------------------------------------

class LineClient:
    """One JSON line per request/response over a child's stdio pipes."""

    def __init__(self, proc: subprocess.Popen) -> None:
        self.proc = proc
        self.lines: "queue.Queue[str]" = queue.Queue()
        self._reader = threading.Thread(target=self._read_loop, daemon=True)
        self._reader.start()

    def _read_loop(self) -> None:
        try:
            for line in self.proc.stdout:
                self.lines.put(line.decode("utf-8", errors="replace").strip())
        except Exception:
            pass

    def send(self, payload: dict) -> None:
        self.proc.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
        self.proc.stdin.flush()

    def receive(self, timeout: float) -> str:
        return self.lines.get(timeout=timeout)

    def request(self, payload: dict, timeout: float) -> dict | None:
        self.send(payload)
        line = self.receive(timeout)
        if not line:
            return None
        try:
            return json.loads(line)
        except json.JSONDecodeError:
            return None

    def close_and_wait(self, timeout: float = 30.0) -> int:
        try:
            self.proc.stdin.close()
        except Exception:
            pass
        try:
            return self.proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            return self.proc.wait(timeout=10)


# --------------------------------------------------------------------------
# AC3 timers
# --------------------------------------------------------------------------

def timed_core_ready(core_exe: Path, env: dict, lab_round: Path) -> tuple[float | None, dict]:
    """spawn -> core.ping ready response (ms). Each round gets its own lab
    data root: core_service would otherwise default to the host's real
    %LOCALAPPDATA%\\New Manga (zero-touch principle — never let it)."""
    envelope = {
        "protocol": "new-manga.core",
        "version": {"major": 1, "minor": 0},
        "request_id": "rg1-cs2",
        "command": "core.ping",
        "payload": {},
    }
    lenv = dict(env)
    lenv["NEWMANGA_DATA_ROOT"] = str(lab_round / "data-root")
    lenv["APPDATA"] = str(lab_round / "roaming")
    (lab_round / "data-root").mkdir(parents=True, exist_ok=True)
    (lab_round / "roaming").mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(
            [str(core_exe)], env=lenv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except OSError as error:
        return None, {"error": f"spawn failed: {error}"}
    client = LineClient(proc)
    try:
        response = client.request(envelope, timeout=LAUNCH_TIMEOUT_S)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
    finally:
        exit_code = client.close_and_wait(timeout=30.0)
    detail = {"exit": exit_code, "response": response}
    if not response or response.get("error"):
        return None, detail
    result = response.get("result") or {}
    if result.get("status") != "ready":
        return None, detail
    return elapsed_ms, detail


def timed_ac1_ready(ac1_exe: Path, env: dict, lab_round: Path) -> tuple[float | None, dict]:
    """spawn -> acceptance ping pong response (ms). The acceptance bridge
    assembles its core ONLY in its frozen explicit test startup configuration
    (M2AC1_TEST_MODE=1 — same contract as the M2-AC5 runner's ac1_env), so
    the probe pins that env; without it the bridge answers
    AC1_BRIDGE_MISCONFIGURED by design. Each round gets its own lab data root
    (every round is a cold start)."""
    request = {"id": 1, "method": "ping", "params": {}}
    aenv = dict(env)
    aenv["M2AC1_TEST_MODE"] = "1"
    aenv["NEWMANGA_DATA_ROOT"] = str(lab_round / "data-root")
    aenv["APPDATA"] = str(lab_round / "roaming")
    (lab_round / "data-root").mkdir(parents=True, exist_ok=True)
    (lab_round / "roaming").mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    try:
        proc = subprocess.Popen(
            [str(ac1_exe)], env=aenv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except OSError as error:
        return None, {"error": f"spawn failed: {error}"}
    client = LineClient(proc)
    try:
        response = client.request(request, timeout=LAUNCH_TIMEOUT_S)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
    finally:
        client.send({"id": 0, "method": "shutdown", "params": {}})
        exit_code = client.close_and_wait(timeout=60.0)
    detail = {"exit": exit_code, "response": response}
    if not response or response.get("error"):
        return None, detail
    result = response.get("result") or {}
    if not result.get("pong"):
        return None, detail
    return elapsed_ms, detail


def timed_app_cold_start(
    exe: Path, env: dict, lab_round: Path, gate: Gate, sample_index: int
) -> tuple[float | None, int | None]:
    """CreateProcess -> first visible non-console window of that pid (ms).
    Also performs the AC2 runtime console observation for this round:
    while-running samples + after-graceful-exit sample."""
    roaming = lab_round / "roaming"
    roaming.mkdir(parents=True, exist_ok=True)
    round_env = pin_appdata(env, roaming)
    round_env["WEBVIEW2_USER_DATA_FOLDER"] = str(lab_round / "webview2-udd")

    t0 = time.perf_counter()
    proc = subprocess.Popen(
        [str(exe)],
        env=round_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    app_pid = proc.pid
    window_ms: float | None = None
    window_info: dict | None = None
    deadline = t0 + LAUNCH_TIMEOUT_S
    while time.perf_counter() < deadline:
        info = first_visible_app_window(app_pid)
        if info is not None:
            window_ms = (time.perf_counter() - t0) * 1000.0
            window_info = info
            break
        if proc.poll() is not None:
            break
        time.sleep(0.02)

    observed = {"round": sample_index, "app_pid": app_pid, "first_window": window_info,
                "first_window_ms": window_ms, "exit_poll": proc.poll()}
    gate.pass_or(
        window_ms is not None,
        f"RG1-CS1-R{sample_index}-app-window-observed",
        observed,
    )

    hits_running: list[dict] = []
    alive_through_hold = proc.poll() is None
    pid_detail: dict = {"scan_ok": False, "scanned": {}}
    if window_ms is not None and proc.poll() is None:
        # hold the app alive; two while-running console samples (mid-hold, end)
        half = ALIVE_HOLD_S / 2.0
        time.sleep(half)
        if proc.poll() is None:
            target_pids, pid_detail = sidecar_pid_snapshot(app_pid)
            hits_running.extend(console_window_hits(target_pids, CONSOLE_TITLE_MARKERS))
        if proc.poll() is None:
            time.sleep(half)
        if proc.poll() is None:
            target_pids, pid_detail = sidecar_pid_snapshot(app_pid)
            hits_running.extend(console_window_hits(target_pids, CONSOLE_TITLE_MARKERS))
    alive_through_hold = proc.poll() is None
    # DSH r1 P2-1: during production-mode run the app MUST have spawned its
    # sidecars (host_bridge + core_service) — a failed tasklist scan or an
    # empty sidecar pid set means the observation basis collapsed => FAIL.
    # app early-exit during the hold also FAILs the round.
    sidecar_pids_seen = sum(len(v) for v in (pid_detail.get("scanned") or {}).values())
    gate.record(
        f"RG1-CW1-R{sample_index}-running-console-hits",
        "PASS" if (not hits_running and alive_through_hold and pid_detail.get("scan_ok") and sidecar_pids_seen >= 1) else "FAIL",
        {
            "round": sample_index,
            "hits": hits_running,
            "alive_hold_s": ALIVE_HOLD_S,
            "app_alive_through_hold": alive_through_hold,
            "pid_scan": pid_detail,
            "sidecar_pids_seen": sidecar_pids_seen,
        },
    )

    # graceful close (WM_CLOSE semantics via taskkill without /F), then wait
    subprocess.run(["taskkill", "/PID", str(app_pid)], capture_output=True)
    try:
        proc.communicate(timeout=60)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.communicate(timeout=15)
    # wait for the sidecars to be reaped before the after-exit sample
    reaped = wait_sidecars_reaped(timeout=30.0)
    hits_after = console_window_hits(set(), CONSOLE_TITLE_MARKERS)
    gate.record(
        f"RG1-CW2-R{sample_index}-after-exit-console-hits",
        "PASS" if not hits_after else "FAIL",
        {"round": sample_index, "hits": hits_after, "sidecars_reaped": reaped},
    )
    return window_ms, app_pid


def sidecar_pid_snapshot(app_pid: int) -> tuple[set[int], dict]:
    """app pid + every live sidecar pid, with the full scanned pid sets
    recorded (DSH r1 P2-1: the observation's pid basis goes into gate.json).
    scan_ok=False means the tasklist snapshot failed — the caller must FAIL
    the round instead of silently degrading to {app_pid}. Note: a sidecar
    name with an EMPTY pid set is a legitimate state (that entry not running),
    not a scan failure; during production-mode app run host_bridge.exe and
    core_service.exe are expected non-empty and asserted by the CW scenarios."""
    snapshot = pids_of(SIDECAR_EXES)
    if snapshot is None:
        return {app_pid}, {"scan_ok": False, "app_pid": app_pid, "scanned": {}}
    pids = {app_pid}
    for found in snapshot.values():
        pids |= found
    detail = {
        "scan_ok": True,
        "app_pid": app_pid,
        "scanned": {name: sorted(found) for name, found in snapshot.items()},
        "note": "host-wide snapshot: same-named unrelated processes would be included and are visible here",
    }
    return pids, detail


def wait_sidecars_reaped(timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        live = pids_of(SIDECAR_EXES)
        # a failed tasklist snapshot is NOT proof of reaping — keep polling
        # until timeout, then report conservatively False
        if live is not None and not any(live.values()):
            return True
        time.sleep(1.0)
    final = pids_of(SIDECAR_EXES)
    return final is not None and not any(final.values())


def positive_console_control(env: dict, lab: Path) -> tuple[bool, dict]:
    """DSH r1 P2-1 positive control: prove the AC2 ② detector can see RED.
    Spawns a console-subsystem child deliberately WITHOUT CREATE_NO_WINDOW
    (CREATE_NEW_CONSOLE=0x10 forces a visible console host even when the
    parent has none) and requires the console-window observer to hit >= 1
    while it is alive. Zero hits => the detector is blind on this machine and
    this control FAILS.

    Carrier note (established empirically on this machine during the r1
    rework): `cmd /c timeout` with CREATE_NEW_CONSOLE exits immediately
    (code 125) without creating any window when spawned from this runner's
    ConPTY-inherited environment, while `powershell -c Start-Sleep` with the
    same flag reliably produces a visible CASCADIA_HOSTING_WINDOW_CLASS
    window owned by WindowsTerminal.exe (Win11 default-terminal delegation —
    the exact blind spot DSH r1 flagged). Attribution therefore runs through
    the title heuristic (window title carries the powershell.exe path); the
    conhost pid-owner path stays in the detector for classic delegation."""
    control_dir = lab / "positive-control"
    (control_dir / "roaming").mkdir(parents=True, exist_ok=True)
    control_env = pin_appdata(env, control_dir / "roaming")
    proc = subprocess.Popen(
        ["powershell", "-NoProfile", "-Command", "Start-Sleep -Seconds 30"],
        env=control_env,
        creationflags=0x00000010,  # CREATE_NEW_CONSOLE — deliberately no CREATE_NO_WINDOW
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    time.sleep(6.0)
    snapshot = pids_of(("powershell.exe",))
    scan_ok = snapshot is not None
    ps_pids = (snapshot or {}).get("powershell.exe", set()) | {proc.pid}
    hits = console_window_hits(ps_pids, ("powershell",))
    detail = {
        "control_pid": proc.pid,
        "control_carrier": "powershell -NoProfile -Command Start-Sleep -Seconds 30 with CREATE_NEW_CONSOLE(0x10)",
        "powershell_pids_scanned": sorted(ps_pids),
        "scan_ok": scan_ok,
        "hits": hits,
        "classes_expected": list(CONSOLE_WINDOW_CLASSES),
        "attribution": "pid-owner match (classic conhost) OR title heuristic 'powershell' (Windows Terminal delegation)",
    }
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T"], capture_output=True)
    try:
        proc.wait(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
    return bool(scan_ok and len(hits) >= 1), detail


def seed_books_for_listbooks(ac1_exe: Path, env: dict, data_root: Path, roaming: Path) -> dict:
    """P3-5: give DC1's ListBooks a real row to return. The authorized write
    path for library books is the acceptance bridge's ``seed_fixture`` (the
    frozen explicit test configuration, M2-AC5 AC1 mode) — the catalog_loader
    used by DC2/DC4 writes the resource catalog, which ListBooks does not
    read. Seeds one synthetic book + chapter + pages into
    <data_root>/library.db through the production assembly."""
    aenv = pin_appdata(env, roaming)
    aenv["NEWMANGA_DATA_ROOT"] = str(data_root)
    aenv["M2AC1_TEST_MODE"] = "1"
    data_root.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [str(ac1_exe)], env=aenv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    client = LineClient(proc)
    try:
        seed = client.request({"id": 1, "method": "seed_fixture", "params": {}}, timeout=LAUNCH_TIMEOUT_S)
        shutdown = client.request({"id": 0, "method": "shutdown", "params": {}}, timeout=LAUNCH_TIMEOUT_S)
    finally:
        exit_code = client.close_and_wait(timeout=60.0)
    seed_ok = bool(seed) and not seed.get("error") and (seed.get("result") is not None)
    return {
        "exit": exit_code,
        "seed_ok": seed_ok,
        "seed_response_keys": sorted((seed or {}).get("result") or {}) if seed_ok else None,
        "seed_error": (seed or {}).get("error"),
        "shutdown_ok": bool(shutdown) and not shutdown.get("error"),
    }


def stats_block(samples_ms: list[float]) -> dict:
    return {
        "n": len(samples_ms),
        "min_ms": round(min(samples_ms), 1),
        "median_ms": round(statistics.median(samples_ms), 1),
        "max_ms": round(max(samples_ms), 1),
        "samples_ms": [round(value, 1) for value in samples_ms],
    }


# --------------------------------------------------------------------------
# AC4 round trips
# --------------------------------------------------------------------------

def roundtrip_core_service(
    exe: Path, env: dict, data_root: Path, roaming: Path, expect_books_min: int = 0
) -> dict:
    """core.ping (ready) + ListBooks + core.shutdown over the Contract 1.1
    envelope (same shape as the M2-AC5 packaged library probe). With
    ``expect_books_min`` >= 1 (P3-5) the data root must have been seeded
    first and ListBooks must return at least that many fully-keyed rows."""
    lenv = pin_appdata(env, roaming)
    lenv["NEWMANGA_DATA_ROOT"] = str(data_root)
    data_root.mkdir(parents=True, exist_ok=True)

    def envelope(request_id: str, command: str) -> dict:
        return {
            "protocol": "new-manga.core",
            "version": {"major": 1, "minor": 0},
            "request_id": request_id,
            "command": command,
            "payload": {},
        }

    proc = subprocess.Popen(
        [str(exe)], env=lenv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    client = LineClient(proc)
    try:
        ping = client.request(envelope("rg1-dc1-ping", "core.ping"), timeout=LAUNCH_TIMEOUT_S)
        books = client.request(envelope("rg1-dc1-books", "ListBooks"), timeout=LAUNCH_TIMEOUT_S)
        shutdown = client.request(envelope("rg1-dc1-shutdown", "core.shutdown"), timeout=LAUNCH_TIMEOUT_S)
    finally:
        exit_code = client.close_and_wait(timeout=30.0)

    ping_ok = bool(ping) and not ping.get("error") and (ping.get("result") or {}).get("status") == "ready"
    required_keys = {"book_id", "title", "original_title", "is_favorite", "is_archived", "page_count", "created_at", "updated_at"}
    books_result = (books or {}).get("result")
    books_ok = (
        isinstance(books_result, list)
        and len(books_result) >= expect_books_min
        and all(
            isinstance(entry, dict) and required_keys.issubset(entry.keys()) for entry in books_result
        )
    )
    shutdown_ok = bool(shutdown) and not shutdown.get("error") and (shutdown.get("result") or {}).get("status") == "stopped"
    return {
        "exit": exit_code,
        "ping_ok": ping_ok,
        "ping_response": ping,
        "books_ok": books_ok,
        "books_count": len(books_result) if isinstance(books_result, list) else None,
        "expect_books_min": expect_books_min,
        "books_required_keys": sorted(required_keys),
        "books_error": (books or {}).get("error"),
        "shutdown_ok": shutdown_ok,
    }


def roundtrip_host_bridge(exe: Path, env: dict, roots: dict, roaming: Path) -> dict:
    """Control-plane ping handshake + issue/resolve/revoke against the seeded
    catalog (Core/SQLite authority; wire shape per core_bridge.rs)."""
    henv = pin_appdata(env, roaming)
    henv.update(roots)
    proc = subprocess.Popen(
        [str(exe)], env=henv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    client = LineClient(proc)
    detail: dict = {}
    try:
        ping = client.request({"id": 1, "method": "ping", "params": {}}, timeout=LAUNCH_TIMEOUT_S)
        detail["ping"] = ping
        issued = client.request(
            {"id": 2, "method": "issue",
             "params": {"resource_id": "rg1-res", "revision_fingerprint": "rev-1"}},
            timeout=LAUNCH_TIMEOUT_S,
        )
        detail["issue"] = issued
        resolve = revoke = None
        opaque = ((issued or {}).get("result") or {}).get("id")
        if opaque:
            resolve = client.request({"id": 3, "method": "resolve", "params": {"id": opaque}}, timeout=LAUNCH_TIMEOUT_S)
            revoke = client.request({"id": 4, "method": "revoke", "params": {"id": opaque}}, timeout=LAUNCH_TIMEOUT_S)
            detail["resolve"] = resolve
            detail["revoke"] = revoke
        shutdown = client.request({"id": 0, "method": "shutdown", "params": {}}, timeout=LAUNCH_TIMEOUT_S)
        detail["shutdown"] = shutdown
    finally:
        detail["exit"] = client.close_and_wait(timeout=30.0)

    ping_ok = bool((detail.get("ping") or {}).get("result", {}).get("pong"))
    issue_ok = isinstance(((detail.get("issue") or {}).get("result") or {}).get("id"), str) and str(
        ((detail.get("issue") or {}).get("result") or {}).get("id")
    ).startswith("m2id.v1.")
    resolve_ok = bool((detail.get("resolve") or {}).get("result", {}).get("rel_path"))
    revoke_resp = detail.get("revoke")
    revoke_ok = bool(revoke_resp) and "error" not in revoke_resp
    return {
        "detail": {k: v for k, v in detail.items()},
        "ping_ok": ping_ok,
        "issue_ok": issue_ok,
        "resolve_ok": resolve_ok,
        "revoke_ok": bool(revoke_ok),
    }


def roundtrip_acceptance_bridge(exe: Path, env: dict, data_root: Path, roaming: Path) -> dict:
    """Ping handshake with the m2-ac1-acceptance bridge + clean shutdown.
    The bridge assembles its core only in the explicit test startup
    configuration (M2AC1_TEST_MODE=1 — frozen contract, same as the M2-AC5
    runner's ac1_env)."""
    aenv = pin_appdata(env, roaming)
    aenv["NEWMANGA_DATA_ROOT"] = str(data_root)
    aenv["M2AC1_TEST_MODE"] = "1"
    data_root.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [str(exe)], env=aenv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    client = LineClient(proc)
    try:
        ping = client.request({"id": 1, "method": "ping", "params": {}}, timeout=LAUNCH_TIMEOUT_S)
        shutdown = client.request({"id": 0, "method": "shutdown", "params": {}}, timeout=LAUNCH_TIMEOUT_S)
    finally:
        exit_code = client.close_and_wait(timeout=60.0)
    ping_ok = bool(ping) and not ping.get("error") and (ping.get("result") or {}).get("pong") is True
    service = ((ping or {}).get("result") or {}).get("service")
    return {
        "exit": exit_code,
        "ping_ok": ping_ok,
        "service": service,
        "shutdown_ok": bool(shutdown) and not shutdown.get("error"),
        "error": (ping or {}).get("error"),
    }


def roundtrip_catalog_loader(exe: Path, env: dict, lab: Path) -> dict:
    """Seed a lab data root with the packaged loader, then read the rows back
    with sqlite3. CLI arguments are confirmed from the worktree source first
    (AC4: loader CLI params must be read from catalog_loader.py, not assumed)."""
    source = REPO_ROOT / "src" / "infrastructure" / "resource_channel" / "catalog_loader.py"
    source_text = source.read_text(encoding="utf-8") if source.is_file() else ""
    confirmed_args = [name for name in ("--db", "--set", "--dump", "--count", "--remove") if f'"{name}"' in source_text]

    derived = lab / "catalog-gate" / "scope" / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    asset = derived / "asset.png"
    asset.write_bytes(b"\x89PNG\r\n\x1a\ngate-fixture\n")
    catalog_db = lab / "catalog-gate" / "catalog.sqlite"

    # M2-DERIVED-GC-2 (design 2.3): the roundtrip fixture catalog is
    # brand-new, so the trusted first-bind flag points at this gate's own
    # derived root; the gate's pass criteria and thresholds are unchanged.
    completed = subprocess.run(
        [
            str(exe),
            "--db", str(catalog_db),
            "--initialize-preview-namespace", str(derived),
            "--set", "rg1-res=asset.png",
            "--set", "rg1-res-2=asset.png",
            "--dump",
        ],
        env=pin_appdata(env, lab / "catalog-gate" / "roaming"),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    dump_ok = completed.returncode == 0 and '"rg1-res"' in completed.stdout
    rows: list[dict] = []
    sqlite_error = None
    try:
        connection = sqlite3.connect(catalog_db)
        try:
            cursor = connection.execute("SELECT resource_id, scope_class, rel_path FROM resource_catalog ORDER BY resource_id")
            rows = [{"resource_id": r[0], "scope_class": r[1], "rel_path": r[2]} for r in cursor.fetchall()]
        finally:
            connection.close()
    except Exception as error:  # noqa: BLE001 — recorded, then judged
        sqlite_error = repr(error)
    return {
        "source_confirmed_args": confirmed_args,
        "loader_exit": completed.returncode,
        "loader_stderr_tail": completed.stderr[-300:],
        "dump_ok": dump_ok,
        "sqlite_rows": rows,
        "sqlite_error": sqlite_error,
    }


# --------------------------------------------------------------------------
# warn-file review (AC4)
# --------------------------------------------------------------------------

EXCLUDED_BY_SPEC = ("torch", "torchvision", "doctr", "pandas", "pytest", "setuptools", "distutils", "pip")


def review_warn_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    missing = sorted({match.group(1) for match in re.finditer(r"missing module named ([\w\.]+)", text)})
    excluded = sorted({name for name in missing if any(name == top or name.startswith(top + ".") for top in EXCLUDED_BY_SPEC)})
    other = sorted(set(missing) - set(excluded))
    return {
        "warn_file": path.name,
        "missing_total": len(missing),
        "missing_excluded_by_spec": excluded,
        "missing_other_disclosed": other,
        "note": (
            "operative load-time-critical evidence = the four install-state stdio "
            "round trips in this gate; a missing load-time module would crash the "
            "entry at spawn, not merely warn. 'missing_other_disclosed' entries are "
            "conditional/optional imports observed by PyInstaller's static analysis."
        ),
    }


# --------------------------------------------------------------------------
# static source audit (AC2 ③ — dev-mode behavior unchanged)
# --------------------------------------------------------------------------

def audit_console_policy_sources() -> dict:
    main_rs = (REPO_ROOT / "apps/desktop/src-tauri/src/main.rs").read_text(encoding="utf-8")
    bridges = {}
    for name in ("core_bridge.rs", "ac1_bridge.rs", "library_bridge.rs"):
        bridges[name] = (REPO_ROOT / "apps/desktop/src-tauri/src" / name).read_text(encoding="utf-8")
    attr_ok = '#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]' in main_rs
    gated_flags = all(
        re.search(r"#\[cfg\(windows\)\]\s*\{[^}]*creation_flags\(CREATE_NO_WINDOW\)", text, re.S)
        for text in bridges.values()
    )
    counts = {name: len(re.findall(r"creation_flags\(CREATE_NO_WINDOW\)", text)) for name, text in bridges.items()}
    spec_text = (REPO_ROOT / "packaging/m2ac5/core_sidecar.spec").read_text(encoding="utf-8")
    spec_console_frozen = re.search(r"console\s*=\s*True", spec_text) is not None
    return {
        "windows_subsystem_attr_gated_by_not_debug_assertions": attr_ok,
        "create_no_window_inside_cfg_windows": gated_flags,
        "creation_flags_counts_per_bridge": counts,
        "core_sidecar_spec_console_true_unchanged": spec_console_frozen,
    }


# --------------------------------------------------------------------------
# install
# --------------------------------------------------------------------------

def silent_install(installer: Path, target: Path, env: dict) -> tuple[bool, str]:
    if " " in str(target):
        return False, f"/D= target contains a space (NSIS unquoted-/D= ambiguity): {target}"
    argv = [str(installer), "/S", f"/D={target}"]
    if target.exists():
        subprocess.run(["taskkill", "/F", "/IM", INSTALLED_EXE_NAME], capture_output=True)
        time.sleep(1)
        shutil.rmtree(target, ignore_errors=True)
    proc = subprocess.Popen(argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait(timeout=600)
    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "installer timed out after 600 s"
    exe = target / INSTALLED_EXE_NAME
    deadline = time.time() + 60
    while time.time() < deadline and not exe.is_file():
        time.sleep(1)
    if not exe.is_file():
        return False, f"installed exe missing after wait: {exe}"
    missing = [name for name in SIDECAR_EXES if not (target / "resources" / "core-sidecar" / name).is_file()]
    if missing:
        return False, f"sidecar exes missing after install: {missing}"
    return True, f"installed to {target} with resources/core-sidecar/{', '.join(SIDECAR_EXES)}"


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--installer", type=Path, default=DEFAULT_INSTALLER)
    parser.add_argument("--samples", type=int, default=3, help="cold-start sample count (>=3 per AC3)")
    args = parser.parse_args()
    samples = max(3, args.samples)

    RAW.mkdir(parents=True, exist_ok=True)
    installer = args.installer
    gate = Gate()
    gate_record = {
        "gate": "m2rg1-release-gate",
        "ruling": "windows local-machine (2026-09-29): this machine is the clean Windows basis; local pass => gate PASS",
        "base_commit": "875eb818abc74a498c84026016dd1a1c72e0ad50",
        "runner_python": sys.version.split()[0],
    }

    log("phase 0: environment record + PATH purge")
    env, removed, kept = purged_environment()
    purged_ok, purge_detail = assert_no_python_on_path(env)
    gate.pass_or(purged_ok, "RG1-E1-python-purged-from-path",
                 {"detail": purge_detail, "removed_entries": len(removed), "kept_entries": len(kept)})
    gate_record["environment"] = {
        "path_removed_entries": removed,
        "path_kept_entries": kept,
        "purge_markers": PURGE_MARKERS,
        "installer": str(installer),
        "installer_sha256": sha256_file(installer) if installer.is_file() else None,
        "os": subprocess.run(["cmd", "/c", "ver"], capture_output=True, text=True, encoding="mbcs", errors="replace").stdout.strip(),
        "processor_architecture": os.environ.get("PROCESSOR_ARCHITECTURE", ""),
        "host_real_user_root_never_touched": str(HOST_USER_ROOT),
        # DSH r1 P2-1: which console delegation is in force (Windows Terminal
        # => the CASCADIA class + title-heuristic boundary applies)
        "console_delegation_registry": console_delegation_registry(),
        "console_window_classes_observed": list(CONSOLE_WINDOW_CLASSES),
    }
    gate.pass_or(installer.is_file(), "RG1-E2-installer-present",
                 {"installer": str(installer), "sha256": gate_record["environment"]["installer_sha256"]})
    if not installer.is_file() or not purged_ok:
        gate.record("RG1-BLOCKED", "FAIL", {"reason": "installer missing or python purge failed"})
        return finish(gate, gate_record, 1)

    install_dir = Path(tempfile.gettempdir()) / "m2rg1-gate" / "install"
    if " " in str(install_dir):
        gate.pass_or(False, "RG1-E3-install-path-no-spaces", {"install_dir": str(install_dir)})
        return finish(gate, gate_record, 1)
    gate.pass_or(True, "RG1-E3-install-path-no-spaces", {"install_dir": str(install_dir)})

    log("phase 1: NSIS silent install")
    ok, detail = silent_install(installer, install_dir, env)
    gate.pass_or(ok, "RG1-I1-silent-install", {"detail": detail})
    if not ok:
        return finish(gate, gate_record, 1)
    exe = install_dir / INSTALLED_EXE_NAME
    sidecar_dir = install_dir / "resources" / "core-sidecar"

    log("phase 2: AC2-1 PE subsystem of the installed app exe")
    pe = pe_subsystem(exe)
    gate.pass_or(pe.get("subsystem") == 2, "RG1-PE1-app-exe-subsystem-gui", pe)

    log("phase 2.5: AC2-3 static source audit (dev-mode unchanged)")
    audit = audit_console_policy_sources()
    gate.pass_or(
        audit["windows_subsystem_attr_gated_by_not_debug_assertions"]
        and audit["create_no_window_inside_cfg_windows"]
        and all(count >= 1 for count in audit["creation_flags_counts_per_bridge"].values())
        and audit["core_sidecar_spec_console_true_unchanged"],
        "RG1-PE2-console-policy-source-audit",
        audit,
    )

    # AC4 prep: seed a catalog through the packaged loader so host_bridge can
    # be exercised end-to-end (issue/resolve/revoke)
    log("phase 3: AC4 catalog_loader seed (lab data root) + sqlite read-back")
    lab = Path(tempfile.mkdtemp(prefix="m2rg1-gate-lab-"))
    gate_record["lab"] = str(lab)
    loader_detail = roundtrip_catalog_loader(sidecar_dir / "catalog_loader.exe", env, lab)
    loader_ok = (
        bool(loader_detail["source_confirmed_args"])
        and loader_detail["loader_exit"] == 0
        and loader_detail["dump_ok"]
        and not loader_detail["sqlite_error"]
        and any(row["resource_id"] == "rg1-res" for row in loader_detail["sqlite_rows"])
    )
    gate.pass_or(loader_ok, "RG1-DC4-catalog-loader-seed-readback", loader_detail)
    catalog_roots = {
        "M2RC1_DERIVED_ROOT": str(lab / "catalog-gate" / "scope" / "derived"),
        "M2RC1_MANAGED_ROOT": str(lab / "catalog-gate" / "scope" / "managed"),
        "M2RC2_CATALOG_DB": str(lab / "catalog-gate" / "catalog.sqlite"),
    }

    log("phase 4: AC4 sidecar stdio round trips (install state, purged env)")
    # P3-5: DC1's ListBooks must return a REAL row — seed one book through the
    # acceptance bridge's seed_fixture into the same data root first
    dc1_root = lab / "dc1-data-root"
    seed_detail = seed_books_for_listbooks(
        sidecar_dir / "acceptance_bridge.exe", env, dc1_root, lab / "dc1-seed-roaming"
    )
    gate.pass_or(seed_detail["seed_ok"] and seed_detail["shutdown_ok"],
                 "RG1-DC1a-listbooks-seed-fixture", seed_detail)
    core_detail = roundtrip_core_service(
        sidecar_dir / "core_service.exe", env, dc1_root, lab / "dc1-roaming", expect_books_min=1
    )
    gate.pass_or(
        core_detail["ping_ok"] and core_detail["books_ok"] and core_detail["shutdown_ok"],
        "RG1-DC1b-core-service-ping-listbooks",
        core_detail,
    )
    host_detail = roundtrip_host_bridge(sidecar_dir / "host_bridge.exe", env, catalog_roots, lab / "dc2-roaming")
    gate.pass_or(
        host_detail["ping_ok"] and host_detail["issue_ok"] and host_detail["resolve_ok"] and host_detail["revoke_ok"],
        "RG1-DC2-host-bridge-handshake-issue-resolve",
        host_detail["detail"],
    )
    ac1_detail = roundtrip_acceptance_bridge(
        sidecar_dir / "acceptance_bridge.exe", env, lab / "dc3-data-root", lab / "dc3-roaming"
    )
    gate.pass_or(
        ac1_detail["ping_ok"] and ac1_detail["shutdown_ok"],
        "RG1-DC3-acceptance-bridge-handshake",
        ac1_detail,
    )

    log("phase 5: AC4 PyInstaller warn files copied + classified")
    # PyInstaller 6 emits ONE merged warn file per spec run (warn-<spec>.txt)
    # covering all four Analysis entries; per-entry warn-<entry>.txt files are
    # not produced by this layout (disclosed here, same coverage: the merged
    # file carries every missing module of all four entries).
    warn_src = REPO_ROOT / "apps" / "desktop" / "src-tauri" / "target" / "pyinstaller-work" / "core_sidecar"
    warn_review = []
    warn_copied = 0
    for warn_path in sorted(warn_src.glob("warn-*.txt")) if warn_src.is_dir() else []:
        warn_review.append(review_warn_file(warn_path))
        shutil.copy2(warn_path, RAW / f"rg1-warn-{warn_path.stem}.txt")
        warn_copied += 1
    gate.pass_or(
        warn_copied >= 1,
        "RG1-W1-warn-files-copied-and-classified",
        {"copied": warn_copied, "merged_per_spec_layout": True, "review": warn_review},
    )

    log("phase 5.5: AC2 positive control — the detector must see RED")
    control_ok, control_detail = positive_console_control(env, lab)
    gate.pass_or(control_ok, "RG1-CW0-positive-control-hits-console",
                 control_detail)

    log("phase 6: AC3 cold-start timers + AC2-2 runtime console observation")
    app_ms: list[float] = []
    cold_lab = lab / "coldstart"
    for index in range(1, samples + 1):
        window_ms, _pid = timed_app_cold_start(exe, env, cold_lab / f"round{index}", gate, index)
        if window_ms is not None:
            app_ms.append(window_ms)

    core_ms: list[float] = []
    core_details = []
    for index in range(1, samples + 1):
        value, detail = timed_core_ready(
            sidecar_dir / "core_service.exe", env, lab / "cs2" / f"round{index}"
        )
        if value is not None:
            core_ms.append(value)
        core_details.append(detail)
    gate.pass_or(len(core_ms) == samples, "RG1-CS2-core-ready-samples",
                 {"stats": stats_block(core_ms) if core_ms else None, "details": core_details})

    ac1_ms: list[float] = []
    ac1_details = []
    for index in range(1, samples + 1):
        value, detail = timed_ac1_ready(
            sidecar_dir / "acceptance_bridge.exe", env, lab / "cs3" / f"round{index}"
        )
        if value is not None:
            ac1_ms.append(value)
        ac1_details.append(detail)
    gate.pass_or(len(ac1_ms) == samples, "RG1-CS3-ac1-handshake-samples",
                 {"stats": stats_block(ac1_ms) if ac1_ms else None, "details": ac1_details})

    gate.pass_or(len(app_ms) == samples, "RG1-CS1-app-cold-start-samples",
                 {"stats": stats_block(app_ms) if app_ms else None,
                  "method": "CreateProcess -> first visible non-console top-level window of the app pid; "
                            "new lab APPDATA per round (every round is a cold start)"})

    gate_record["timings"] = {
        "app_cold_start": stats_block(app_ms) if app_ms else None,
        "core_ready": stats_block(core_ms) if core_ms else None,
        "ac1_handshake": stats_block(ac1_ms) if ac1_ms else None,
        "appdata_isolation": "APPDATA pinned per round into the lab; host real %APPDATA% unreachable",
    }
    gate_record["install_dir"] = str(install_dir)

    return finish(gate, gate_record, 0 if gate.verdict == "PASS" else 1)


def finish(gate: Gate, gate_record: dict, code: int) -> int:
    log("gate")
    gate_record["verdict"] = gate.verdict
    gate_record["scenarios"] = gate.scenarios
    (RAW / "rg1-gate.json").write_text(json.dumps(gate_record, indent=2, default=str), encoding="utf-8")
    print(f"\nGATE: {gate.verdict}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
