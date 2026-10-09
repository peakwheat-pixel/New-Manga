"""P02 Read-Only Environment and Source Identity Probe (Stage A r2).

Collects and verifies host environment, Edge WebView2 Runtime presence,
Git repository/worktree baseline, and build artifact directory status
without running any Cargo/Tauri builds or modifying product source code.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import winreg
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFICATION_DIR = REPO_ROOT / "verification" / "P02"
DIST_DIR = REPO_ROOT / "apps" / "desktop" / "frontend" / "dist"
CARGO_TARGET_DIR = VERIFICATION_DIR / "cargo-target"
BEHAVIOR_BASELINE_COMMIT = "241ff3b70b6fc0490ea238efd486cc707f849031"


def run_cmd(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd or REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as exc:
        return -1, "", str(exc)


def get_git_state() -> dict[str, str | bool]:
    _, head, _ = run_cmd(["git", "rev-parse", "HEAD"])
    _, tree, _ = run_cmd(["git", "rev-parse", "HEAD^{tree}"])
    _, branch, _ = run_cmd(["git", "branch", "--show-current"])
    ret, status_out, _ = run_cmd(["git", "status", "--porcelain"])
    is_clean = (ret == 0 and len(status_out.strip()) == 0)

    return {
        "head": head,
        "tree": tree,
        "branch": branch,
        "is_clean": is_clean,
        "behavior_baseline_commit": BEHAVIOR_BASELINE_COMMIT,
        "porcelain_status": status_out,
    }


def query_webview2_runtime() -> dict[str, str]:
    results = {}
    # Verified WebView2 Runtime Client GUID: {F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}
    wv2_guid = "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{wv2_guid}"),
        (winreg.HKEY_CURRENT_USER, rf"Software\Microsoft\EdgeUpdate\Clients\{wv2_guid}"),
        (winreg.HKEY_LOCAL_MACHINE, rf"SOFTWARE\Microsoft\EdgeUpdate\Clients\{wv2_guid}"),
    ]

    for hive, subkey in reg_paths:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                pv, _ = winreg.QueryValueEx(key, "pv")
                hive_name = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
                results[f"{hive_name}_{subkey}"] = str(pv)
        except OSError:
            continue

    # File system installation directory check
    app_dir = Path(r"C:\Program Files (x86)\Microsoft\EdgeWebView\Application")
    if app_dir.exists():
        for child in app_dir.iterdir():
            if child.is_dir() and child.name[0].isdigit():
                results[f"FS_{child.name}"] = str(child)

    return results


def check_directory_state(path: Path) -> dict[str, object]:
    exists = path.exists()
    is_dir = path.is_dir() if exists else False
    entries = []
    if exists and is_dir:
        entries = [str(p.name) for p in path.iterdir()]
    return {
        "path": str(path),
        "exists": exists,
        "is_dir": is_dir,
        "entry_count": len(entries),
        "entries": entries,
    }


def get_npm_version() -> str:
    npm_exe = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm_exe:
        return "UNAVAILABLE: npm binary not found in PATH"
    code, stdout, stderr = run_cmd([npm_exe, "-v"])
    if code == 0 and stdout:
        return stdout
    return f"ERROR: exit={code}, stderr={stderr}"


def main() -> int:
    git_state = get_git_state()
    wv2_findings = query_webview2_runtime()
    dist_state = check_directory_state(DIST_DIR)
    cargo_target_state = check_directory_state(CARGO_TARGET_DIR)

    _, node_ver, node_err = run_cmd(["node", "-v"])
    if not node_ver and node_err:
        node_ver = f"ERROR: {node_err}"
    npm_ver = get_npm_version()

    detected_ver = "UNKNOWN"
    for k, v in wv2_findings.items():
        if k.startswith("FS_"):
            detected_ver = k.replace("FS_", "")
            break
        if "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}" in k:
            detected_ver = v
            break

    report = {
        "probe": "P02_READONLY_ENV_IDENTITY",
        "task_id": "P02",
        "owner": "Antigravity",
        "host_os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "platform": platform.platform(),
        },
        "webview2_runtime": {
            "findings": wv2_findings,
            "detected_version": detected_ver,
            "verified_client_guid": "{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
        },
        "runtimes": {
            "python": sys.version.splitlines()[0],
            "python_executable": sys.executable,
            "node": node_ver,
            "npm": npm_ver,
        },
        "git_state": git_state,
        "build_output_directories": {
            "frontend_dist": dist_state,
            "cargo_target": cargo_target_state,
        },
        "build_barrier": {
            "hard_barrier_active": True,
            "reason": (
                "tauri_build writes into source tree (gen/schemas and command permission TOMLs), "
                "and fixed baseline lacks trusted sidecar inputs. Cargo/Tauri builds prohibited in this Owner worktree."
            ),
        },
    }

    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    json_path = VERIFICATION_DIR / "env-identity-report.json"
    txt_path = VERIFICATION_DIR / "env-identity-report.txt"

    with json_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    txt_lines = [
        "=== P02 Read-Only Environment & Identity Report ===",
        f"Host OS: {report['host_os']['platform']}",
        f"WebView2 Detected Version: {report['webview2_runtime']['detected_version']}",
        f"WebView2 Verified Key: {report['webview2_runtime']['verified_client_guid']}",
        f"Node Runtime: {report['runtimes']['node']}",
        f"npm Tool: {report['runtimes']['npm']}",
        f"Python Executable: {report['runtimes']['python_executable']}",
        f"Git Branch: {git_state['branch']}",
        f"Source HEAD: {git_state['head']}",
        f"Source Tree: {git_state['tree']}",
        f"Behavior Baseline: {git_state['behavior_baseline_commit']}",
        f"frontend/dist Exists: {dist_state['exists']}",
        f"cargo-target Exists: {cargo_target_state['exists']}",
        f"Hard Build Barrier Active: {report['build_barrier']['hard_barrier_active']}",
        f"Barrier Rationale: {report['build_barrier']['reason']}",
    ]
    with txt_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(txt_lines) + "\n")

    print("\n".join(txt_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
