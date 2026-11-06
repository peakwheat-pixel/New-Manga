"""Generate verification/FEA-11-RUN-GRANT-2A/RESOURCE-MANIFEST.json.

Registers the out-of-repo isolated resource root
``G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2A/`` (test fixtures, gate logs,
discrimination backups) with an aggregate sha256 over every file, plus an
explicit "no repo deletion/move/migration/archive" closeout. No user data /
AppData / external volume / recycle bin is touched.

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2A/tools/gen_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WORKSPACE = Path("G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2A")
OUT = REPO / "verification" / "FEA-11-RUN-GRANT-2A" / "RESOURCE-MANIFEST.json"


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
    all_entries = _scan(WORKSPACE)
    groups = []
    for child in sorted(WORKSPACE.iterdir()):
        if child.is_file():
            groups.append(
                {
                    "name": child.name,
                    "kind": "file",
                    "file_count": 1,
                    "sha256": _sha256(child),
                }
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
                    {"name": rel, "sha256": digest}
                    for rel, digest in entries[:20]
                ] + [{"name": f"... ({len(entries) - 20} more files, aggregate above)", "sha256": ""}],
            }
        )
    manifest = {
        "schema_version": 1,
        "task_id": "FEA-11-RUN-GRANT-2A",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "run-grant-2a-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": _git_head(),
        "note": (
            "Host Run source version channel delivery (ScanSourceSync response -> "
            "SourceIdentityCache -> Run grant mint; bounded on-demand cold-cache scan; "
            "R3-02 AcceptRun delegation test). The isolated task root "
            "G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2A/ holds runtime IPC "
            "fixtures, gate logs and discrimination backups; no tracked repository "
            "file lives there. Canonical copies of the gate logs are committed under "
            "verification/FEA-11-RUN-GRANT-2A/logs/. No user data, AppData, external "
            "volume or recycle bin was touched; no delete/move/migrate/archive was "
            "performed."
        ),
        "resources": [
            {
                "resource_type": "worktree",
                "source_path": f"NOT_APPLICABLE（main worktree; delivery head {_git_head()[:9]}）",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "未创建 linked worktree（任务要求显式不建）；实施全部在 main 工作树 apps/src/tests/verification/doc 内。",
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
                    "仓外隔离根（工作区治理边界）。仅含 agent 运行夹具/门禁原始日志/判别备份；"
                    "产品代码与测试通过路径常量引用，不依赖其内容。"
                    "closeout 保留（PRESERVE_REFERENCED），不删除。"
                ),
            },
            {
                "resource_type": "test-fixture",
                "source_path": "apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs（运行时真实 zip/PNG/DB/folder）",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "真实 zip/PNG/迁移库/folder/真实签名 grant 全部在测试运行时生成；"
                    "IPC 用例写入隔离根 fixtures/ 子目录（上述 temp 资源内）；仓库不提交二进制 fixture。"
                ),
            },
            {
                "resource_type": "user-data",
                "source_path": "NOT_APPLICABLE",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "未读写真实用户数据/AppData/外部卷/回收站；.NET IPC 用例使用隔离 fixture 根。",
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
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="",
    )
    print(f"WROTE {OUT} files={len(all_entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
