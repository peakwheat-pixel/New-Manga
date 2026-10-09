"""P02 Read-Only Environment and Source Identity Probe.

Collects and verifies host environment, WebView2 Runtime presence,
Git repository/worktree baseline, and build artifact directory status
without running any Cargo/Tauri builds or modifying product source code.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import winreg
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFICATION_DIR = REPO_ROOT / "verification" / "P02"
DIST_DIR = REPO_ROOT / "apps" / "desktop" / "frontend" / "dist"
CARGO_TARGET_DIR = VERIFICATION_DIR / "cargo-target"


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
        "porcelain_status": status_out,
    }


def query_webview2_runtime() -> dict[str, str]:
    results = {}
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\EdgeUpdate\Clients"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\EdgeUpdate\Clients"),
    ]

    for hive, subkey in reg_paths:
        try:
            with winreg.OpenKey(hive, subkey) as root_key:
                num_subkeys = winreg.QueryInfoKey(root_key)[0]
                for i in range(num_subkeys):
                    sub_name = winreg.EnumKey(root_key, i)
                    try:
                        with winreg.OpenKey(root_key, sub_name) as client_key:
                            pv, _ = winreg.QueryValueEx(client_key, "pv")
                            hive_name = "HKLM" if hive == winreg.HKEY_LOCAL_MACHINE else "HKCU"
                            results[f"{hive_name}_{sub_name}"] = str(pv)
                    except OSError:
                        continue
        except OSError:
            continue

    # File system check
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


def main() -> int:
    git_state = get_git_state()
    wv2_findings = query_webview2_runtime()
    dist_state = check_directory_state(DIST_DIR)
    cargo_target_state = check_directory_state(CARGO_TARGET_DIR)

    _, node_ver, _ = run_cmd(["node", "-v"])
    _, npm_ver, _ = run_cmd(["npm", "-v"])

    detected_ver = "UNKNOWN"
    for k, v in wv2_findings.items():
        if k.startswith("FS_") or "F3017226-9E4A-4437-B3B1-FD94E1568A91" in k:
            detected_ver = k.replace("FS_", "") if k.startswith("FS_") else v
            break
    if detected_ver == "UNKNOWN" and wv2_findings:
        detected_ver = next(iter(wv2_findings.values()))

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
        },
        "runtimes": {
            "python": sys.version,
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

    with json_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    txt_lines = [
        "=== P02 Read-Only Environment & Identity Report ===",
        f"Host OS: {report['host_os']['platform']}",
        f"WebView2 Detected Version: {report['webview2_runtime']['detected_version']}",
        f"Git Branch: {git_state['branch']}",
        f"Git HEAD: {git_state['head']}",
        f"Git Tree: {git_state['tree']}",
        f"Git Clean Status: {git_state['is_clean']}",
        f"frontend/dist Exists: {dist_state['exists']}",
        f"cargo-target Exists: {cargo_target_state['exists']}",
        f"Hard Build Barrier Active: {report['build_barrier']['hard_barrier_active']}",
        f"Barrier Rationale: {report['build_barrier']['reason']}",
    ]
    with txt_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(txt_lines) + "\n")

    print("\n".join(txt_lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
