"""P02 Static Source Contract & Front-End Control Probe (Stage A r4).

Performs static analysis of live Workbench frontend source files to verify:
- WorkbenchPage debounce default parameters (resolveDebounceMs=300, regionDebounceMs=300)
- App.tsx navigation and toggle selectors
- Child component structure (PageListPanel, ViewerPanel, RegionInspector)
- Expected IPC command surface consumption in Workbench

Produces structured JSON and human-readable text verification reports with pure LF.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VERIFICATION_DIR = REPO_ROOT / "verification" / "P02"
FRONTEND_SRC = REPO_ROOT / "apps" / "desktop" / "frontend" / "src"


def check_workbench_page() -> dict[str, object]:
    path = FRONTEND_SRC / "workbench" / "WorkbenchPage.tsx"
    if not path.exists():
        return {"status": "FAIL", "reason": f"File not found: {path}"}

    content = path.read_text(encoding="utf-8")
    checks = {}

    # Check debounce defaults
    has_resolve_debounce = bool(re.search(r"resolveDebounceMs\s*=\s*300", content))
    has_region_debounce = bool(re.search(r"regionDebounceMs\s*=\s*300", content))
    checks["resolveDebounceMs_default_300"] = has_resolve_debounce
    checks["regionDebounceMs_default_300"] = has_region_debounce

    # Check client classes imported and instantiated
    clients = ["LibraryClient", "RegionClient", "ResourceChannelClient"]
    client_presence = {cl: (cl in content) for cl in clients}
    checks["client_references"] = client_presence

    # Check command surface at client layer
    client_files = [
        FRONTEND_SRC / "library" / "client.ts",
        FRONTEND_SRC / "region" / "client.ts",
        FRONTEND_SRC / "workbench" / "pageImage.ts",
    ]
    all_client_text = "\n".join(
        cf.read_text(encoding="utf-8") for cf in client_files if cf.exists()
    )

    commands = [
        "library_list_books",
        "list_regions",
        "set_region_type",
        "restore_region_revision",
        "resolve_page_resource",
        "list_chapters",
        "list_chapter_pages",
    ]
    command_presence = {cmd: (cmd in all_client_text or cmd in content) for cmd in commands}
    checks["command_surface_references"] = command_presence

    # Check child components
    components = [
        "PageListPanel",
        "ViewerPanel",
        "RegionInspector",
        "WorkbenchToolbar",
        "TaskProgressPanel",
        "RelabelConfirmDialog",
    ]
    comp_presence = {comp: (comp in content) for comp in components}
    checks["component_references"] = comp_presence

    all_passed = (
        has_resolve_debounce
        and has_region_debounce
        and all(client_presence.values())
        and all(command_presence.values())
        and all(comp_presence.values())
    )

    return {
        "status": "PASS" if all_passed else "FAIL",
        "file": str(path.relative_to(REPO_ROOT)),
        "checks": checks,
    }


def check_app_navigation() -> dict[str, object]:
    path = FRONTEND_SRC / "App.tsx"
    if not path.exists():
        return {"status": "FAIL", "reason": f"File not found: {path}"}

    content = path.read_text(encoding="utf-8")
    checks = {
        "has_app_nav_testid": 'data-testid="app-nav"' in content,
        "has_nav_console_testid": 'data-testid="nav-console"' in content,
        "has_nav_workbench_testid": 'data-testid="nav-workbench"' in content,
        "has_workbench_mount": "<WorkbenchPage />" in content or "<WorkbenchPage" in content,
        "has_nav_chrome_toggle": "setNavChrome(true)" in content,
        "has_interactive_view_state": 'const [view, setView] = useState<"console" | "workbench">("console")' in content,
    }

    all_passed = all(checks.values())
    return {
        "status": "PASS" if all_passed else "FAIL",
        "file": str(path.relative_to(REPO_ROOT)),
        "checks": checks,
    }


def check_child_components() -> dict[str, object]:
    sub_files = [
        "workbench/PageListPanel.tsx",
        "workbench/ViewerPanel.tsx",
        "workbench/RegionInspector.tsx",
    ]
    results = {}
    for sub in sub_files:
        path = FRONTEND_SRC / sub
        if not path.exists():
            results[sub] = {"exists": False}
            continue
        content = path.read_text(encoding="utf-8")
        results[sub] = {
            "exists": True,
            "line_count": len(content.splitlines()),
            "has_keyboard_or_focus": bool(re.search(r"onKeyDown|tabIndex|focus", content, re.IGNORECASE)),
        }
    return results


def get_git_rev(args: list[str]) -> str:
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return proc.stdout.strip()
    except Exception:
        return "UNKNOWN"


def main() -> int:
    wb_report = check_workbench_page()
    app_report = check_app_navigation()
    children_report = check_child_components()

    overall_pass = (wb_report["status"] == "PASS" and app_report["status"] == "PASS")
    exit_code = 0 if overall_pass else 1

    report = {
        "probe": "P02_STATIC_SOURCE_CONTRACT_CONTROL",
        "overall_status": "PASS" if overall_pass else "FAIL",
        "source_head": get_git_rev(["rev-parse", "HEAD"]),
        "source_tree": get_git_rev(["rev-parse", "HEAD^{tree}"]),
        "exit_code": exit_code,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "workbench_page": wb_report,
        "app_navigation": app_report,
        "child_components": children_report,
    }

    VERIFICATION_DIR.mkdir(parents=True, exist_ok=True)
    json_path = VERIFICATION_DIR / "static-control-report.json"
    txt_path = VERIFICATION_DIR / "static-control-report.txt"

    with json_path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    txt_lines = [
        "=== P02 Static Source Contract Control Report ===",
        f"Overall Status: {report['overall_status']}",
        f"WorkbenchPage Status: {wb_report['status']}",
        f"  - resolveDebounceMs default 300: {wb_report.get('checks', {}).get('resolveDebounceMs_default_300')}",
        f"  - regionDebounceMs default 300: {wb_report.get('checks', {}).get('regionDebounceMs_default_300')}",
        f"App Navigation Status: {app_report['status']}",
        f"  - app-nav testid present: {app_report.get('checks', {}).get('has_app_nav_testid')}",
        f"  - nav-workbench testid present: {app_report.get('checks', {}).get('has_nav_workbench_testid')}",
    ]
    with txt_path.open("w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(txt_lines) + "\n")

    print("\n".join(txt_lines))
    return 0 if overall_pass else 1


if __name__ == "__main__":
    sys.exit(main())
