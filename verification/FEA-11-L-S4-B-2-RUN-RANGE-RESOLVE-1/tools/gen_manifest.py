"""FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1 resource manifest generator.

Hashes the canonical evidence files plus every repository file changed by the
delivery commits and writes ``RESOURCE-MANIFEST.json`` next to ``EV.md``. The
manifest itself is not hashed (it is the container); ``EV.md`` references it by
path.

Usage (repo root), after the delivery commits exist:
  C:/Python314/python.exe verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/gen_manifest.py \
      --commits <sha1>,<sha2>,<sha3>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TASK_ID = "FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1"
EVIDENCE = REPO / "verification" / TASK_ID


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace", check=True,
    ).stdout


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--commits", required=True)
    parser.add_argument(
        "--delivery-head",
        default=None,
        help="implementation/test delivery head (defaults to the last commit)",
    )
    args = parser.parse_args()
    commits = [item.strip() for item in args.commits.split(",") if item.strip()]
    delivery_head = args.delivery_head or commits[-1]
    head = _git("rev-parse", "HEAD").strip()

    manifest_relative = f"verification/{TASK_ID}/RESOURCE-MANIFEST.json"
    changed: list[dict] = []
    for commit in commits:
        names = [
            name.strip()
            for name in _git("show", "--pretty=format:", "--name-only", commit)
            .splitlines()
            if name.strip()
        ]
        for name in names:
            if name == manifest_relative:
                # The manifest cannot hash itself; it is the container.
                continue
            path = REPO / name
            changed.append(
                {
                    "commit": commit,
                    "path": name,
                    "sha256": _sha256(path) if path.is_file() else "DELETED",
                }
            )

    evidence_files = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(EVIDENCE).as_posix()
        if relative == "RESOURCE-MANIFEST.json":
            continue
        evidence_files.append({"path": relative, "sha256": _sha256(path)})

    manifest = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "l-s4b1-impl (DSH Agent Teams teammate; Lead `lead`; 实际实施者，卡 owner 已由 Lead 对齐)",
        "delivery_head": delivery_head,
        "delivery_commits": commits,
        "repo_head_at_generation": head,
        "note": (
            "FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1 (L-S4-B-2) delivery: the Host-only "
            "Run source-RANGE resolution recovery. An ENUMERATED Run target is now "
            "authorized with its OWN live (registry_id, generation) entry by reusing the "
            "public static SelectEnumeratedEntry that L-S4-B-1 proved for the scan face "
            "(never a second path-only ResolveRegistryEntry, which met the sibling REVOKED "
            "row first and failed closed); non-enumerated targets keep the unchanged "
            "path-exact/containment resolver. A refused/failed resolution is only counted "
            "as unresolved (best-effort, never thrown), the live-but-cold source still "
            "enters ColdSources and the existing bounded on-demand scan fills it. No "
            "linked worktree, no push, no user data; zero Core/Python change; zero contract "
            "byte change (C-16 v1.5 and C-17 v1.1 pins are the proof); the scan/registry/"
            "coordinator helpers were REUSED but not modified. This is a GENERATION-TIME "
            "snapshot of the tracked delivery tree; the manifest itself is the container "
            "and is deliberately NOT hashed inside its own file list."
        ),
        "resources": [
            {
                "resource_type": "worktree",
                "source_path": (
                    "NOT_APPLICABLE（main worktree; delivery head "
                    f"{delivery_head}）"
                ),
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "未创建 linked worktree（任务要求显式不建）；实施全部在 "
                    "main 工作树 apps/verification/doc 内，未 push。"
                ),
            },
            {
                "resource_type": "temp_workspace",
                "source_path": (
                    "G:\\CODEX\\New Manga.workspace\\"
                    "FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1"
                ),
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "process_check": (
                    "任务隔离根仅用于仓库外派生产物；gated 真 IPC 的 fixture/证据位于 "
                    "G:/CODEX/New Manga.workspace/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/"
                    "fixtures/ipc-*/（本卡新增目录，仓外、无 tracked 副作用）。均为仓外"
                    "派生产物，不属仓库交付；未清理。"
                ),
            },
            {
                "resource_type": "repository",
                "source_path": "G:\\CODEX\\New Manga (main)",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "file_count": len(changed),
                "changed_files": changed,
            },
            {
                "resource_type": "evidence_tree",
                "source_path": f"verification/{TASK_ID}",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "file_count": len(evidence_files),
                "files": evidence_files,
            },
        ],
    }
    target = EVIDENCE / "RESOURCE-MANIFEST.json"
    target.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"manifest={target} changed={len(changed)} evidence={len(evidence_files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
