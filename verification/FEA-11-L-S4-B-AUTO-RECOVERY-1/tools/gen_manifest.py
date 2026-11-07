"""FEA-11-L-S4-B-AUTO-RECOVERY-1 resource manifest generator.

Hashes the canonical evidence files plus every repository file changed by the
delivery commits and writes ``RESOURCE-MANIFEST.json`` next to ``EV.md``. The
manifest itself is not hashed (it is the container); ``EV.md`` references it by
path.

Usage (repo root), after the delivery commits exist:
  C:/Python314/python.exe verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/gen_manifest.py \
      --commits <sha1>,<sha2>,<sha3>,<sha4>
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
TASK_ID = "FEA-11-L-S4-B-AUTO-RECOVERY-1"
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
        "generated_by": "l-s4b-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": delivery_head,
        "delivery_commits": commits,
        "repo_head_at_generation": head,
        "note": (
            "FEA-11-L-S4-B-AUTO-RECOVERY-1 (L-S4-B) delivery: the C-16 v1.5 §2.5 "
            "conditional single-row ReattestSourceLocation fact propagation "
            "(two auth columns only, last_verified_at preserved, single reused SQL, "
            "zero write on every refusal) plus the Host capability-gated exact "
            "re-attest planner/enumerator pre-pass and the App B1 explicit-action "
            "success-branch trigger of the EXISTING scan refresh. No linked "
            "worktree, no push, no user data; no library.py/schema/dependency "
            "change; the frozen C-16 v1.5 bytes were NOT modified (pin audit is "
            "the proof). This is a GENERATION-TIME snapshot of the tracked "
            "delivery tree; the manifest itself is the container and is "
            "deliberately NOT hashed inside its own file list."
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
                    "main 工作树 src/apps/tests/verification/doc 内，未 push。"
                ),
            },
            {
                "resource_type": "temp_workspace",
                "source_path": (
                    "G:\\CODEX\\New Manga.workspace\\"
                    "FEA-11-L-S4-B-AUTO-RECOVERY-1"
                ),
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "process_check": (
                    "任务隔离根：pytest 的 scratch DB/zip 位于 "
                    "G:/CODEX/New Manga.workspace/FEA-11-L-S4-B-AUTO-RECOVERY-1/"
                    "fixtures/**；gated 真 IPC 沿用既有 FEA-11 fixtures 根 "
                    "G:/CODEX/New Manga.workspace/FEA-11/fixtures/scan-*/"
                    "（测试既有约定）。均为仓外派生产物，不属仓库交付；未清理。"
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
