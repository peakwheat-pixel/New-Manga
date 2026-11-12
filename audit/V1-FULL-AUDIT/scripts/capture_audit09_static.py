#!/usr/bin/env python3
"""Capture a bounded, source-only AUDIT-09 UI inventory.

This does not start the application, run tests, open user data, or claim that UI/UX passed.
It records selected source anchors and whether a matching application process is present.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


BASE_COMMIT = "10e4ee013835605800d3830fb960ae8d3aa04167"
ROOT = Path(__file__).resolve().parents[3]
AUDIT_ROOT = ROOT / "audit" / "V1-FULL-AUDIT"

SOURCES: dict[str, tuple[str, ...]] = {
    "apps/desktop-avalonia/src/NewManga.App/AppOptions.cs": (
        r"DefaultShellId|public string Shell|UseV2Shell|PresentationHost",
    ),
    "apps/desktop-avalonia/src/NewManga.App/App.axaml.cs": (
        r"if \(!options.UseV2Shell\)|if \(options.PresentationHost\)|selection.IsFluent|CreateLegacyShell",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Services/FrontendSelector.cs": (
        r"DefaultDiagnostic|FrontendKind\.(AvaloniaV2|Fluent)|IsFallback|CurrentV2FrontendId",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml": (
        r"Width=|MinWidth=|PageHost|DockHost|SidebarHost",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs": (
        r'_pages\["(bookshelf|workbench|reader|settings)"\]|AddNav\(|Reader\.SetExport|OpenReaderForBookAsync',
    ),
    "apps/desktop-avalonia/src/NewManga.App/Shell/V2/AppShellV2.axaml": (
        r"ReaderOverlay|V2WorkspaceHost|ThemeStudio|CommandPaletteOverlay|HelpOverlay|AlertBanner",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Shell/V2/AppShellV2.axaml.cs": (
        r"RegisterWorkspace|LibraryWorkspaceView|ConsoleWorkspaceView|StudioWorkspace|HandleKey",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ReaderOverlay.axaml": (
        r"ToggleLayoutCommand|ToggleDirectionCommand|PreviousPageCommand|NextPageCommand|HasError|IsLoading|CurrentPage",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs": (
        r"enum FluentPage|FluentPage\.(Library|Workbench|Reader|Settings)|new (ShelfPageView|WorkbenchPageView|ReaderPageView|SettingsPageView)|ApplyResponsiveBand|OnPreviewKeyDown",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs": (
        r"Zoom|DoublePage|ScaleTransform|OnKeyDown|Key\.(Left|Right|PageUp|PageDown)|AutomationProperties|FluentPageState\.(Empty|Error|Partial)",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ShelfPageView.cs": (
        r"正在读取书架|书架读取失败|ImportFilesAsync|ImportFolderAsync|FluentUi\.Empty|AutomationProperties",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/Fluent/WorkbenchPageView.cs": (
        r"WorkbenchViewTab|Batch|OCR|SFX|Glossary|Region|Revision|FluentUi\.Empty|Loading|Error|AutomationProperties",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs": (
        r"theme\.frontendId|凭据|Network|Backup|正在读取设置|设置错误|AutomationProperties",
    ),
    "apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioCapabilities.cs": (
        r"NotWiredTooltip|WiredCommands|SetRegionType|RestoreRevision|RerenderPage|CanExecute",
    ),
    "apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioTermsViewModel.cs": (
        r"NOT_WIRED|能力待接入|搜索不可用|未接入：不展示|未执行任何写入",
    ),
    "apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioBatchViewModel.cs": (
        r"NotWiredText|NOT_WIRED|投影未接入|IRunController",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/Controls/StudioCanvasViewport.cs": (
        r"NOT_WIRED|成品预览|能力待接入",
    ),
    "apps/desktop-avalonia/src/NewManga.App/Views/V2/Studio/Controls/StudioPageWorkspace.cs": (
        r"StudioSurfaceMode\.Final|StudioSurfaceMode\.Split|NOT_WIRED|成品预览读取未接入",
    ),
}

PROCESS_QUERY = (
    "Get-Process | Where-Object { $_.ProcessName -match 'NewManga|Manga|Avalonia' } "
    "| Select-Object -ExpandProperty ProcessName -Unique"
)


def run(argv: list[str], *, cwd: Path = ROOT) -> dict[str, object]:
    started = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    before = time.monotonic()
    result = subprocess.run(
        argv,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "argv": argv,
        "started_utc": started,
        "elapsed_seconds": round(time.monotonic() - before, 3),
        "exit": result.returncode,
        "output": result.stdout,
    }


def main() -> int:
    generated_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    captured_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    product_diff = run(["git", "diff", "--quiet", BASE_COMMIT, generated_head, "--", "apps/desktop-avalonia"])
    process_check = run(["pwsh", "-NoProfile", "-Command", PROCESS_QUERY])

    files: list[dict[str, object]] = []
    for relative, patterns in SOURCES.items():
        path = ROOT / relative
        data = path.read_bytes()
        lines = data.decode("utf-8").splitlines()
        matches: list[dict[str, object]] = []
        for pattern in patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            hits = [
                {"line": index, "text": line.strip()}
                for index, line in enumerate(lines, 1)
                if regex.search(line)
            ][:24]
            matches.append({"pattern": pattern, "hits": hits})
        files.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(data).hexdigest().upper(),
                "line_count": len(lines),
                "matches": matches,
            }
        )

    process_names = [line.strip() for line in str(process_check["output"]).splitlines() if line.strip()]
    gui_status = "PROCESS_PRESENT_UI_NOT_OBSERVED" if process_names else "BLOCKED_NO_MATCHING_APP_PROCESS"
    success = product_diff["exit"] == 0 and process_check["exit"] == 0 and all(item["path"] for item in files)
    exit_code = 0 if success else 1
    base_name = f"audit09-static-{captured_utc}"
    log_path = AUDIT_ROOT / "logs" / f"{base_name}.log"
    json_path = AUDIT_ROOT / "evidence" / f"{base_name}.json"

    metadata = {
        "generated_head": generated_head,
        "branch": branch,
        "captured_utc": captured_utc,
        "base_commit": BASE_COMMIT,
        "product_source_diff": {key: value for key, value in product_diff.items() if key != "output"},
        "process_check": {key: value for key, value in process_check.items() if key != "output"},
        "matching_process_names": process_names,
        "gui_runtime_status": gui_status,
        "files": files,
        "exit": exit_code,
    }

    log_lines = [
        f"generated HEAD={generated_head}",
        f"branch={branch}",
        f"command=python audit/V1-FULL-AUDIT/scripts/capture_audit09_static.py",
        f"UTC={captured_utc}",
        f"base product-source diff EXIT={product_diff['exit']}",
        "product-source diff output=" + (str(product_diff["output"]).strip() or "<no diff>"),
        f"process query={PROCESS_QUERY}",
        f"process query EXIT={process_check['exit']}",
        "matching process names=" + (", ".join(process_names) if process_names else "<none>"),
        f"GUI runtime status={gui_status}",
    ]
    for source in files:
        log_lines.append(f"--- {source['path']} sha256={source['sha256']} lines={source['line_count']} ---")
        for group in source["matches"]:
            log_lines.append(f"pattern={group['pattern']}")
            for hit in group["hits"]:
                log_lines.append(f"{hit['line']}: {hit['text']}")
    log_lines.append(f"EXIT={exit_code}")
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8", newline="\n")
    json_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"generated HEAD={generated_head}")
    print(f"branch={branch}")
    print(f"UTC={captured_utc}")
    print(f"product-source diff EXIT={product_diff['exit']}")
    print(f"process query EXIT={process_check['exit']}; matches={len(process_names)}")
    print(f"GUI runtime status={gui_status}")
    print(f"files captured={len(files)}")
    print(f"log={log_path.relative_to(ROOT).as_posix()}")
    print(f"json={json_path.relative_to(ROOT).as_posix()}")
    print(f"EXIT={exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
