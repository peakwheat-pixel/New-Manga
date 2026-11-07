"""FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A) resource manifest generator.

Hashes the canonical evidence files plus every repository file changed by the
delivery commits and writes ``RESOURCE-MANIFEST.json`` next to ``EV.md``.  The
manifest itself is not hashed (it is the container); ``EV.md`` references it by
path.

Usage (repo root), after the delivery commits exist:
  C:/Python314/python.exe verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/tools/gen_manifest.py \
      --commits <sha1>,<sha2>
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
EVIDENCE = REPO / "verification" / "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1"


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
    args = parser.parse_args()
    commits = [item.strip() for item in args.commits.split(",") if item.strip()]
    head = _git("rev-parse", "HEAD").strip()

    changed: list[dict] = []
    for commit in commits:
        names = [
            name.strip()
            for name in _git("show", "--pretty=format:", "--name-only", commit)
            .splitlines()
            if name.strip()
        ]
        for name in names:
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
        "task_id": "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "l-s4-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": commits[-1],
        "delivery_commits": commits,
        "repo_head_at_generation": head,
        "note": (
            "FEA-11-L-S4-LOCATION-AUTH-REFRESH-1 (A) delivery: the ONE in-place "
            "location-auth refresh (C-15 §2/§3.3 conformance, zero contract "
            "change) wired into the C-17 apply face and the referenced-import "
            "reuse/skip paths, plus its discriminating tests and evidence. "
            "No linked worktree, no push, no user data, no schema/migration/"
            "dependency change; the frozen contract bytes were NOT modified "
            "(pin audit is the proof). This is a GENERATION-TIME snapshot of "
            "the tracked delivery tree."
        ),
        "resources": [
            {
                "resource_type": "worktree",
                "source_path": (
                    "NOT_APPLICABLE（main worktree; delivery head "
                    f"{commits[-1]}）"
                ),
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "未创建 linked worktree（任务要求显式不建）；实施全部在 "
                    "main 工作树 src/tests/verification/doc 内，未 push。"
                ),
            },
            {
                "resource_type": "temp_workspace",
                "source_path": (
                    "G:\\CODEX\\New Manga.workspace\\FEA-11-L-S4-"
                    "LOCATION-AUTH-REFRESH-1"
                ),
                "disposition": "NOT_CREATED_NO_SCRATCH",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "本卡未产生仓外 scratch/临时产物；pytest 临时文件位于系统 "
                    "tmp_path 与既有共享 fixture 根 "
                    "G:/CODEX/New Manga.workspace/FEA-11/fixtures/（测试既有约定），"
                    "不属本卡交付资源。"
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
                "source_path": "verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1",
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
