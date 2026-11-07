"""Generate RESOURCE-MANIFEST.json for FEA-11-L-R11-GATE-UNIFY-1.

Generation-time snapshot of the tracked delivery tree (delivery_head
86cd1d124): changed files with per-file sha256, the evidence tree, the
preserved out-of-repo scratch workspace, and the worktree disposition. The
manifest itself is the container and is deliberately NOT hashed inside its own
file list.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

REPO = pathlib.Path(r"G:\CODEX\New Manga")
EVIDENCE = REPO / "verification" / "FEA-11-L-R11-GATE-UNIFY-1"
SCRATCH = pathlib.Path(r"G:\CODEX\New Manga.workspace\FEA-11-L-R11-GATE-UNIFY-1")
DELIVERY_HEAD = "86cd1d124"
DELIVERY_COMMITS = ["1c1c9ca2f", "86cd1d124"]
GENERATED_AT = "2026-11-08T00:45:00+08:00"


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True
    ).stdout.strip()


CHANGED = [
    ("1c1c9ca2f", "src/infrastructure/sqlite/source_sync.py"),
    ("1c1c9ca2f", "src/bootstrap/core_assembly.py"),
    ("1c1c9ca2f", "src/bootstrap/core_service.py"),
    ("86cd1d124", "tests/fea11/test_source_gate_unify.py"),
]

NOTE = (
    "FEA-11-L-R11-GATE-UNIFY-1 delivery: the Core-internal publication gate is "
    "unified into the ONE predicate `source_sync.SourceSyncStore."
    "publication_gate_of_page` (verdicts open/pending/unavailable/corrupt_chain; "
    "healthy binding + publication row state + WHOLE previous-chain walk). "
    "`core_assembly.read_gate` (Run target admission / commit guard / provider) "
    "maps corrupt_chain onto the frozen three-state `unavailable`; "
    "`core_service._assert_source_sync_gate` (resolve/reader) delegates and "
    "raises the existing SOURCE_ACCESS_DENIED family; AuthorizeSourceReadForRun "
    "keeps consuming the same injected predicate. Legacy v7/imported bindings "
    "whose whole chain never published stay open (C-16 v1.7 §2.4); a new sync "
    "chain with a missing publication row fails closed (C-17 §3.3), including "
    "two-hop chains. Zero contract byte change (pins 18/18), zero schema/"
    "migration, zero wire/command/capability/error-code/PROTOCOL_MINOR, zero "
    "dependency, zero apps change. L-R11-a (relation='added' missing-row / plan "
    "receipt), L-R11-b (write/chapter faces stay pending-only), L-R11-c (no "
    "dedicated diagnostic code), L-R11-d (no auto-repair) and L-R11-e (real "
    "v7->v8 migration fixture) remain as documented limitations: this is NOT "
    "'C-17 §3.3 fully implemented' and NOT 'L-R11 fully closed'. This is a "
    "GENERATION-TIME snapshot of the tracked delivery tree; the manifest itself "
    "is the container and is deliberately NOT hashed inside its own file list."
)


def main() -> int:
    evidence_files = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file():
            continue
        if path == EVIDENCE / "RESOURCE-MANIFEST.json":
            continue
        evidence_files.append(
            {
                "path": path.relative_to(REPO).as_posix(),
                "sha256": sha(path),
            }
        )
    changed_files = [
        {
            "commit": commit,
            "path": rel,
            "sha256": sha(REPO / rel),
        }
        for commit, rel in CHANGED
    ]
    manifest = {
        "schema_version": 1,
        "task_id": "FEA-11-L-R11-GATE-UNIFY-1",
        "generated_at": GENERATED_AT,
        "generated_by": "l-r11-impl (DSH Agent Teams teammate; Lead `lead`)",
        "delivery_head": DELIVERY_HEAD,
        "delivery_commits": DELIVERY_COMMITS,
        "repo_head_at_generation": git_head(),
        "note": NOTE,
        "resources": [
            {
                "resource_type": "worktree",
                "source_path": (
                    "NOT_APPLICABLE（main worktree; delivery head 86cd1d124）"
                ),
                "disposition": "NOT_APPLICABLE",
                "destination_path": "NOT_APPLICABLE",
                "process_check": (
                    "未创建 linked worktree（任务要求显式不建）；实施全部在 main "
                    "工作树的 allowed_paths 内，未 push。"
                ),
            },
            {
                "resource_type": "temp_workspace",
                "source_path": str(SCRATCH),
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "process_check": (
                    "任务隔离根（仓外派生产物）：`baseline/` 为判别性破坏前的 "
                    "source_sync.py / core_service.py / core_assembly.py 字节快照；"
                    "`mutate.py` 为判别性破坏→RED→复原→复绿脚本。未清理、未被 "
                    "Git 跟踪、无 tracked 副作用。"
                ),
            },
            {
                "resource_type": "repository",
                "source_path": "G:\\CODEX\\New Manga (main)",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "file_count": len(changed_files),
                "changed_files": changed_files,
            },
            {
                "resource_type": "evidence_tree",
                "source_path": "verification/FEA-11-L-R11-GATE-UNIFY-1",
                "disposition": "PRESERVE_REFERENCED",
                "destination_path": "Same source location",
                "file_count": len(evidence_files) + 1,
                "files": evidence_files,
            },
        ],
    }
    target = EVIDENCE / "RESOURCE-MANIFEST.json"
    target.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"wrote {target} ({len(evidence_files) + 1} evidence files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
