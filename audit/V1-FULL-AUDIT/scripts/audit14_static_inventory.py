#!/usr/bin/env python3
"""Capture a bounded, read-only AUDIT-14 source inventory.

This script inspects selected current authority documents, app composition points,
explicit NOT_WIRED declarations, and legacy packaging references. It does not run
the application, tests, builds, migrations, or inspect user data.
"""

from __future__ import annotations

import datetime as dt
import json
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "audit" / "V1-FULL-AUDIT"
BASE_COMMIT = "10e4ee013835605800d3830fb960ae8d3aa04167"
STAMP = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LOG_PATH = AUDIT / "logs" / f"audit14-static-{STAMP}.log"
JSON_PATH = AUDIT / "evidence" / f"audit14-static-{STAMP}.json"

SCANS: list[tuple[str, list[str]]] = [
    (
        "index_and_current_status",
        [
            "rg", "-n", "仓库根目录没有 README|V11R 程序已收官|V11R 程序.*已收官|当前 Task|NEW-MANGA-V1-FULL-AUDIT",
            "doc/00_INDEX.md", "doc/STATUS.md", "doc/REBASELINE_PLAN.md",
        ],
    ),
    (
        "readme_claims_and_release_versions",
        [
            "rg", "-n", "^> \\*\\*Status:|^[-] \\*\\*(Bookshelf|Workbench|Reader|Settings|Export)|四个一级页面|0\\.1\\.0|0\\.1\\.1|managed copy",
            "README.md",
        ],
    ),
    (
        "v11r_state_and_historical_acceptance",
        [
            "rg", "-n", "^状态：`ACTIVE`|Console：9 分区|术语与约束|发布产物（0\\.1\\.1",
            "doc/V11R_PROGRAM.md", "doc/V11R_ACCEPTANCE_REPORT.md",
        ],
    ),
    (
        "ad003_implementation_snapshot",
        [
            "rg", "-n", "未冻结与未实现|SourceAccessRegistry.*当前均无实现|V2 的删除.*NOT_WIRED|source-read",
            "doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md",
        ],
    ),
    (
        "production_shell_composition",
        [
            "rg", "-n", "new HostController|new BookshelfPage|new WorkbenchPage|new ReaderPage|new SettingsPage|StudioWorkspaceViewModel\\(|new StudioWorkspaceAdapter|EnsureLoadedAsync|RefreshCredentialsAsync|RefreshProfilesAsync",
            "apps/desktop-avalonia/src/NewManga.App/App.axaml.cs",
            "apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs",
            "apps/desktop-avalonia/src/NewManga.App/Shell/V2/AppShellV2.axaml.cs",
        ],
    ),
    (
        "v2_studio_explicit_gaps",
        [
            "rg", "-n", "RunSource = runSource \\?\\? NotWiredRunDataSource|TextSource = textSource \\?\\? new NotWiredRegionTextSource|FlagSource = flagSource \\?\\? new NotWiredRegionFlagSource|IRunDataSource: NOT_WIRED|IRegionTextSource: NOT_WIRED|IRegionFlagSource: NOT_WIRED|PageSurface\\.Final/Split: NOT_WIRED|NotWiredTermsSource",
            "apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioPageViewModel.cs",
            "apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/StudioTermsViewModel.cs",
        ],
    ),
    (
        "source_and_trash_implementation_symbols",
        [
            "rg", "-n", "class SourceAccessRegistry|class HostOperationOrchestrator|RestoreFromTrashAsync|PreviewPermanentDeleteBooks|MoveToTrashAsync|source-read",
            "apps/desktop-avalonia/src/NewManga.Host",
            "apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs",
            "src/application/sources",
        ],
    ),
    (
        "legacy_build_and_release_references",
        [
            "rg", "-n", "src-tauri|apps/desktop/src-tauri|0\\.1\\.0|0\\.1\\.1",
            "apps/desktop-avalonia/scripts/prepare-sidecar.ps1",
            "apps/desktop-avalonia/scripts/build-installer.ps1",
            "packaging/release-gate/run_release_gate.py",
            ".github/workflows/build-release.yml",
            "README.md",
        ],
    ),
    (
        "legacy_surface_presence",
        [
            "rg", "--files", "apps/desktop", "src/ui",
        ],
    ),
]


def run(argv: list[str]) -> dict[str, object]:
    start = time.monotonic()
    result = subprocess.run(
        argv,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    executable = argv[0]
    interpreter = "ripgrep" if executable == "rg" else executable
    return {
        "argv": argv,
        "cwd": str(ROOT),
        "shell": False,
        "interpreter": interpreter,
        "elapsed_seconds": round(time.monotonic() - start, 6),
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def main() -> int:
    generated_at = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    head = run(["git", "rev-parse", "HEAD"])
    status = run(["git", "status", "--porcelain"])
    branch = run(["git", "branch", "--show-current"])
    product_diff = run(["git", "diff", "--quiet", BASE_COMMIT, "HEAD", "--", "src", "apps", "tests"])
    scans = [{"name": name, **run(argv)} for name, argv in SCANS]

    record = {
        "schema": "audit14-static-inventory/v1",
        "generated_at_utc": generated_at,
        "generated_head": str(head["stdout"]).strip(),
        "branch": str(branch["stdout"]).strip(),
        "git_status_porcelain": status["stdout"],
        "git_status_exit": status["exit"],
        "product_diff_base": BASE_COMMIT,
        "product_diff_exit": product_diff["exit"],
        "scope": "bounded read-only static inventory; no tests/build/GUI/user-data access",
        "commands": [head, status, branch, product_diff, *scans],
    }

    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    lines = [
        "AUDIT-14 bounded static inventory",
        f"generated_at_utc={generated_at}",
        f"generated_head={record['generated_head']}",
        f"branch={record['branch']}",
        f"cwd={ROOT}",
        "scope=bounded read-only static inventory; no tests/build/GUI/user-data access",
        f"json={JSON_PATH.relative_to(ROOT).as_posix()}",
    ]
    for item in record["commands"]:
        lines.extend(
            [
                "",
                f"[{item.get('name', item['argv'][0])}]",
                f"argv={json.dumps(item['argv'], ensure_ascii=False)}",
                f"shell={item.get('shell', False)} interpreter={item.get('interpreter', 'native')} cwd={item.get('cwd', ROOT)}",
                f"elapsed_seconds={item.get('elapsed_seconds', 0)} EXIT={item['exit']}",
                "stdout:",
                str(item["stdout"]).rstrip("\n"),
            ]
        )
        if item["stderr"]:
            lines.extend(["stderr:", str(item["stderr"]).rstrip("\n")])
    LOG_PATH.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    print(f"generated_head={record['generated_head']}")
    print(f"log={LOG_PATH.relative_to(ROOT).as_posix()}")
    print(f"json={JSON_PATH.relative_to(ROOT).as_posix()}")
    failed = [item for item in record["commands"] if item["exit"] != 0]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
