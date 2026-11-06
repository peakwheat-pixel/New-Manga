"""FEA-11-RUN-GRANT-2 (2B) resource manifest (card AC-J4 evidence).

Records the disposition of every resource this delivery touched:

* the main worktree (no linked worktree was created — the card forbids it);
* the isolated task root ``G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2/``
  (real IPC fixtures, gate logs, discrimination backups) -> PRESERVE_REFERENCED;
* the canonical evidence tree ``verification/FEA-11-RUN-GRANT-2/**`` committed in
  the docs commit (per-file sha256);
* explicit zero-impact statements for repository deletes/moves/archives, user
  data / AppData / external volumes / recycle bin, and the frozen contract bytes.

Writes ``verification/FEA-11-RUN-GRANT-2/RESOURCE-MANIFEST.json``.

Usage (repo root): C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2/tools/gen_manifest.py
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
EVIDENCE = REPO / "verification" / "FEA-11-RUN-GRANT-2"
WORKSPACE = Path("G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2")
OUT = EVIDENCE / "RESOURCE-MANIFEST.json"

DELIVERY_COMMITS = ["7466cb99d", "018008989"]
DELIVERY_HEAD = "0180089894b2286d8ff6a94289b84dd318871d18"
NOTE = (
    "FEA-11-RUN-GRANT-2 (2B) delivery: container member entry authorization channel "
    "(C-16 v1.4 §2 Core registry/match + Host N-entry Run mint + tests/evidence). "
    "The isolated task root G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2/ holds the real "
    "Core IPC fixtures, gate logs and discrimination byte backups; no tracked repository file "
    "lives there. Canonical copies of the gate logs are committed under "
    "verification/FEA-11-RUN-GRANT-2/logs/. The workspace listing below is a GENERATION-TIME "
    "snapshot: the Lead's integration gate may later append integration/ logs to the same "
    "isolated root, so the aggregate is not presented as a frozen final state. "
    "No user data, AppData, external volume or recycle bin was touched; no repository "
    "delete/move/migrate/archive was performed; the frozen C-16 v1.4 bytes were NOT modified "
    "(pin audit is the proof)."
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_row(path: Path) -> dict:
    return {"name": path.name, "sha256": _sha256_bytes(path.read_bytes())}


def _tree(root: Path) -> dict:
    """Aggregate sha256 over the sorted ``sha256  relative_name`` lines."""
    files: list[dict] = []
    for path in sorted(root.rglob("*")):
        if path.is_file():
            files.append({
                "name": path.relative_to(root).as_posix(),
                "sha256": _sha256_bytes(path.read_bytes()),
            })
    aggregate = _sha256_bytes(
        "\n".join(f"{item['sha256']}  {item['name']}" for item in files).encode("utf-8")
    )
    return {"file_count": len(files), "aggregate_sha256": aggregate, "files": files}


def main() -> int:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO), capture_output=True,
        text=True, encoding="utf-8",
    ).stdout.strip()
    children = []
    excluded_children = []
    if WORKSPACE.exists():
        for child in sorted(WORKSPACE.iterdir()):
            # ``integration/`` is the Lead's integration-gate output for this task: it is
            # created/updated after this delivery and is NOT part of this ticket's evidence,
            # so it is excluded from the snapshot (documented instead of silently hashed
            # while another process is still writing it).
            if child.name == "integration":
                excluded_children.append({
                    "name": child.name + "/",
                    "reason": "Lead 集成门禁输出，不属于本交付；生成时点可能仍在写入，故不纳入快照。",
                })
                continue
            if child.is_dir():
                tree = _tree(child)
                children.append({
                    "name": child.name + "/",
                    "kind": "directory",
                    **tree,
                })
            else:
                children.append({"name": child.name, "kind": "file", **_file_row(child)})
    total = sum(
        child.get("file_count", 1) for child in children
    )
    aggregate = _sha256_bytes(
        "\n".join(f"{child['aggregate_sha256']}  {child['name']}"
                  for child in children if "aggregate_sha256" in child).encode("utf-8")
    )
    evidence_files = []
    for path in sorted(EVIDENCE.rglob("*")):
        if path.is_file() and path.name not in {"RESOURCE-MANIFEST.json", "EV.md"}:
            evidence_files.append({
                "name": path.relative_to(EVIDENCE).as_posix(),
                "sha256": _sha256_bytes(path.read_bytes()),
            })
    manifest = {
        "schema_version": 1,
        "task_id": "FEA-11-RUN-GRANT-2",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "run-grant-2b-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": DELIVERY_HEAD,
        "delivery_commits": DELIVERY_COMMITS,
        "repo_head_at_generation": head,
        "note": NOTE,
        "resources": [
            {
                "resource_type": "worktree",
                "source_path": "NOT_APPLICABLE（main worktree; delivery head " + DELIVERY_HEAD + "）",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "未创建 linked worktree（任务要求显式不建）；实施全部在 main 工作树 src/apps/tests/verification/doc 内，未 push。",
            },
            {
                "resource_type": "temp",
                "source_path": str(WORKSPACE),
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "sha256": aggregate,
                "file_count": total,
                "children": children,
                "excluded_children": excluded_children,
            },
            {
                "resource_type": "evidence",
                "source_path": "verification/FEA-11-RUN-GRANT-2/",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same repository path（docs commit）",
                "file_count": len(evidence_files),
                "note": "EV.md 与 RESOURCE-MANIFEST.json 互相引用，故各自排除自身与对方；EV.md 记录 manifest 的 sha256。",
                "files": evidence_files,
            },
            {
                "resource_type": "repository_files",
                "source_path": "src/**, tests/**, apps/desktop-avalonia/**（allowed_paths 内）",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same repository paths",
                "process_check": "无删除/移动/归档；仅修改 7 个 allowed_paths 文件（3 实现 + 4 测试）。",
            },
            {
                "resource_type": "user_data",
                "source_path": "NOT_APPLICABLE（未触碰真实用户数据 / AppData / 外部卷 / 回收站）",
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": "所有运行期夹具均在 G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2/ 隔离根内。",
            },
            {
                "resource_type": "contract_bytes",
                "source_path": "doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md（v1.4 FROZEN）",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Unchanged",
                "process_check": "本卡零契约字节变更；verify_pins 18/18 PASS 为独立证明（logs/gates.log）。",
            },
        ],
    }
    OUT.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8", newline="",
    )
    print("wrote", OUT)
    print("workspace files:", total, "aggregate:", aggregate)
    print("evidence files:", len(evidence_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
