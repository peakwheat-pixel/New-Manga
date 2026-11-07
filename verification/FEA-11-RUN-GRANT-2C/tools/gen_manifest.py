"""FEA-11-RUN-GRANT-2C resource manifest generator.

Hashes the canonical evidence files plus every repository file changed by the
delivery commits and writes ``RESOURCE-MANIFEST.json`` next to ``EV.md``. The
manifest itself is not hashed (it is the container); ``EV.md`` references it by
path.

Usage (repo root), after the delivery commits exist:
  C:/Python314/python.exe verification/FEA-11-RUN-GRANT-2C/tools/gen_manifest.py \
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
TASK_ID = "FEA-11-RUN-GRANT-2C"
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
        # Review r1 P3-04: pycache byte-code churn is not evidence (and must never enter the manifest).
        if "__pycache__" in relative or relative.endswith(".pyc"):
            continue
        evidence_files.append({"path": relative, "sha256": _sha256(path)})

    manifest = {
        "schema_version": 1,
        "task_id": TASK_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generated_by": "l-s4b1-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": delivery_head,
        "delivery_commits": commits,
        "repo_head_at_generation": head,
        "note": (
            "FEA-11-RUN-GRANT-2C delivery: the Host-only long-Run renewal. While a dispatched Run "
            "is NOT terminal the Host re-mints a NEW grant set for the SAME frozen {command, scope} "
            "and calls AuthorizeSourceReadForRun again (C-06 v1.3 §2.2 / C-16 v1.6 §2.4), so a "
            "multi-step Run stays authorized past the original ≤300 s window. Every round reuses the "
            "same best-effort mint+bind path (Registry.Authorize + physical facts re-checked per "
            "source); a typed refusal / revocation / generation drift / lost root / capability loss / "
            "round-budget breach / terminal Run stops the renewal with no retry and no re-attest, and "
            "no grant is ever extended, no scope widened and no identity rebuilt. Zero Core/Python "
            "change, zero Run-wire change, zero new command/capability/error code, zero App change; "
            "the ONE Python edit is the allowed in-process fake-clock test file. The frozen C-06 v1.3 "
            "and C-16 v1.6 bytes are unchanged (pins 18/18). L-G1 is DOWNGRADED (renewal exists) but "
            "NOT closed: single steps >300 s, renewal failure, L-G2/L-G9/L-R1/L-G16 remain. This is a "
            "GENERATION-TIME snapshot of the tracked delivery tree; the manifest itself is the "
            "container and is deliberately NOT hashed inside its own file list."
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
                    "main 工作树 apps/tests/verification/doc 内，未 push。"
                ),
            },
            {
                "resource_type": "temp_workspace",
                "source_path": "G:\\CODEX\\New Manga.workspace\\FEA-11-RUN-GRANT-2C",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "process_check": (
                    "任务隔离根：gated 真 IPC 的 fixture/证据位于 "
                    "G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-2C/fixtures/ipc-*/；"
                    "Python in-process fake-clock 测试位于 .../fixtures/test_*（仓外派生产物，"
                    "无 tracked 副作用）。未清理。"
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
