"""Generate verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/RESOURCE-MANIFEST.json.

Registers:
* the out-of-repo isolated resource root
  ``G:/CODEX/New Manga.workspace/FEA-11-L-S1-REGISTRY-RESILIENCE-1/`` (IPC fixtures, gate logs,
  discrimination backups; NOTE: it also holds the earlier PREREQ session's scratch scripts and
  ``tmp/c15.blob`` — this delivery neither created nor modified those files) with an aggregate
  sha256 over every file and per-child details;
* the tracked canonical evidence files under ``verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/``
  (each with its sha256);
* an explicit "no repo deletion/move/migration/archive" closeout. No user data / AppData /
  external volume / recycle bin is touched.

Usage (repo root, AFTER the implementation/test commits and gate logs are final):
    C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/gen_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK = "FEA-11-L-S1-REGISTRY-RESILIENCE-1"
WORKSPACE = Path("G:/CODEX/New Manga.workspace") / TASK
EVIDENCE = REPO / "verification" / TASK
OUT = EVIDENCE / "RESOURCE-MANIFEST.json"

#: This ticket's delivery head (implementation + tests). The repository HEAD at generation time may
#: already carry the concurrent FEA-11-L-S4 commits, so the delivery head is pinned explicitly and
#: the observed head is recorded separately (never silently substituted).
DELIVERY_HEAD = "b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=True,
    ).stdout.strip()


def _aggregate(entries: list[tuple[str, str]]) -> str:
    payload = "\n".join(f"{rel}\t{digest}" for rel, digest in sorted(entries))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _scan(root: Path) -> list[tuple[str, str]]:
    return [
        (str(path.relative_to(root)).replace("\\", "/"), _sha256(path))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]


def main() -> int:
    all_entries = _scan(WORKSPACE) if WORKSPACE.exists() else []
    groups = []
    if WORKSPACE.exists():
        for child in sorted(WORKSPACE.iterdir()):
            if child.is_file():
                groups.append(
                    {"name": child.name, "kind": "file", "file_count": 1, "sha256": _sha256(child)}
                )
                continue
            entries = _scan(child)
            groups.append(
                {
                    "name": child.name + "/",
                    "kind": "directory",
                    "file_count": len(entries),
                    "aggregate_sha256": _aggregate(entries),
                    "files": [
                        {"name": rel, "sha256": digest} for rel, digest in entries
                    ] if len(entries) <= 60 else [
                        {"name": rel, "sha256": digest} for rel, digest in entries[:20]
                    ] + [
                        {"name": f"... ({len(entries) - 20} more files, aggregate above)", "sha256": ""}
                    ],
                }
            )
    evidence_files = [
        {"name": str(path.relative_to(REPO)).replace("\\", "/"), "sha256": _sha256(path)}
        for path in sorted(EVIDENCE.rglob("*"))
        if path.is_file() and path.name != OUT.name
    ]
    meta = {
        "schema_version": 1,
        "task_id": TASK,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "l-s1-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": DELIVERY_HEAD,
        "repo_head_at_generation": _git_head(),
        "note": (
            "Registry read resilience delivery (C-15 v1.5 §5): Load validates the file only, "
            "Authorize re-verifies the requested root identity per request, List keeps every "
            "entry; the file-level corruption path is unchanged. delivery_head is THIS ticket's "
            "implementation/test head; repo_head_at_generation is the shared main working tree "
            "head at generation time and may already contain the concurrent FEA-11-L-S4 commits "
            "(Python only), which are NOT part of this delivery. The isolated task root "
            "G:/CODEX/New Manga.workspace/FEA-11-L-S1-REGISTRY-RESILIENCE-1/ holds the mixed-"
            "registry IPC fixture, gate logs and discrimination backups; no tracked repository "
            "file lives there. It ALSO still holds the earlier PREREQ session's scratch scripts "
            "(closeout_prereq.py / edit_c15.py / fix_*.py / frozen_c15.py / ptr3.py / r2_fix.py) "
            "and tmp/c15.blob — those files pre-date this delivery, were not created or modified "
            "by it, and are preserved as-is. Canonical copies of the gate logs are committed "
            "under verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/. No user data, AppData, "
            "external volume or recycle bin was touched; no delete/move/migrate/archive was "
            "performed on repository content."
        ),
        "resources": [
            {
                "resource_type": "worktree",
                "source_path": f"NOT_APPLICABLE（main worktree; delivery head {DELIVERY_HEAD[:9]}）",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "未创建 linked worktree（任务要求显式不建）；实施全部在 main 工作树 "
                    "apps/desktop-avalonia/{src,tests} 与 verification/doc 内。"
                ),
            },
            {
                "resource_type": "temp",
                "source_path": str(WORKSPACE).replace("/", "\\") + "\\",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "sha256": _aggregate(all_entries),
                "file_count": len(all_entries),
                "children": groups,
                "process_check": (
                    "仓外隔离根（工作区治理边界）。本交付仅新增 fixtures/ipc-*/ 与 discrimination/；"
                    "PREREQ 会话遗留脚本与 tmp/c15.blob 原样保留，未改未删（见 note）。"
                    "closeout 保留（PRESERVE_REFERENCED），不删除。"
                ),
            },
            {
                "resource_type": "canonical-evidence",
                "source_path": f"verification/{TASK}/",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "files": evidence_files,
                "process_check": (
                    "仓内 canonical 证据：EV.md / changed-files.txt / scope-validation.log / "
                    "RESOURCE-MANIFEST.json / logs/* / tools/*。全部由本交付生成并随 docs commit 提交。"
                ),
            },
            {
                "resource_type": "test-fixture",
                "source_path": (
                    "apps/desktop-avalonia/tests/NewManga.Host.Tests/"
                    "SourceRegistryResilienceTests.cs（运行时临时根 / 真实 DPAPI / 真实 Core）"
                ),
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "单测夹具在 %TEMP%/newmanga-ls1-* 内创建并自清理；gated IPC 夹具写入上述隔离根 "
                    "fixtures/ipc-*/；仓库不提交任何二进制夹具。未写 "
                    "verification/FEA-09/native-registry/**。"
                ),
            },
            {
                "resource_type": "user-data",
                "source_path": "NOT_APPLICABLE",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "未读写真实用户数据/AppData/外部卷/回收站；IPC 用例使用隔离 fixture 根。",
            },
            {
                "resource_type": "build-artifact",
                "source_path": "NOT_APPLICABLE",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "dotnet build/test 的 obj/bin 在既有 build 目录内，未纳入交付；未新建仓内 artifact 目录。",
            },
            {
                "resource_type": "repo-deletion",
                "source_path": "NOT_APPLICABLE",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "仓内零删除/移动/迁移/归档（changed-files.txt 仅 A/M）。",
            },
        ],
        "closeout_counts": {"deleted": 0, "moved": 0, "migrated": 0, "archived": 0},
        "closeout_note": (
            "Owner 未执行删除/移动/迁移/归档；仓外隔离根保留供 Review 复核（不随仓库分发）。"
            "全量 pytest / .NET 对 tracked verification/FEA-09 的已知字节副作用已用 "
            "`git checkout -- verification/FEA-09` 恢复（见 logs/gates-governance.log 尾注）。"
        ),
    }
    OUT.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"WROTE {OUT} workspace_files={len(all_entries)} evidence_files={len(evidence_files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
