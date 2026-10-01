"""Register the external (gitignored) evidence tree for review (R11, DSH r1).

The frame-level visual verdicts in ``sfx-spot-check-verdicts.json`` depend
on preview images that live OUTSIDE the repo (gitignored task-env tree);
weights and the eval manifest live there too. This script walks those
paths, hashes every file and writes the inventory JSON committed under
``verification/M2-SFX-DETECT-EVAL/`` so a reviewer can (a) verify the
evidence exists and is unchanged, (b) re-hash after any env move.

If the previews are lost, the per-frame agent verdicts CANNOT be
independently re-inspected (only recomputed geometry would remain) — this
is recorded in the inventory payload.

Usage (from the worktree root):

  python experiments/M2-SFX-DETECT/inventory_external_evidence.py \
      --worktree-root . \
      --task-env "G:/CODEX/New Manga.task-envs" \
      --out verification/M2-SFX-DETECT-EVAL/external-evidence-inventory.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def collect(root: Path, sub: str) -> list[dict]:
    base = root / sub
    rows = []
    if not base.is_dir():
        return rows
    for p in sorted(base.rglob("*")):
        if p.is_file():
            rows.append(
                {
                    "path": str(p),
                    "bytes": p.stat().st_size,
                    "sha256": sha256_file(p),
                }
            )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree-root", type=Path, default=Path("."))
    parser.add_argument("--task-env", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    env = args.task_env
    groups = {
        "previews_ogkalu_grid": collect(env / "M2-SFX-DETECT" / "previews", ""),
        "previews_onnx_grid": collect(env / "M2-SFX-DETECT" / "previews-onnx", ""),
        "weights_onnx_candidates": collect(env / "M2-SFX-DETECT" / "weights", ""),
        "weights_ogkalu_production_pinned": collect(
            env / "M2-DOCTR-QUAL-C4" / "weights" / "ogkalu-comic-text-and-bubble-detector", ""
        ),
        "eval_manifest_frozen": collect(env / "M2-DOCTR-QUAL-work", ""),
        "license_evidence_raw_snapshots": collect(
            env / "M2-SFX-DETECT" / "license-evidence", ""
        ),
        "c4_gpu_venv_interpreter": [
            {
                "path": str(env / "M2-DOCTR-QUAL-C4-gpu-py312" / "Scripts" / "python.exe"),
                "bytes": (env / "M2-DOCTR-QUAL-C4-gpu-py312" / "Scripts" / "python.exe").stat().st_size,
                "sha256": sha256_file(
                    env / "M2-DOCTR-QUAL-C4-gpu-py312" / "Scripts" / "python.exe"
                ),
            }
        ],
    }
    # keep only the frozen seg05 manifest in the manifest group (noise filter)
    groups["eval_manifest_frozen"] = [
        r for r in groups["eval_manifest_frozen"]
        if r["path"].endswith(("eval-manifest.full.seg05.json", "eval-manifest.full.union.json"))
    ]

    counts = {k: len(v) for k, v in groups.items()}
    total = sum(counts.values())
    payload = {
        "schema": "m2-sfx-detect/external-evidence-inventory@1",
        "task": "M2-SFX-DETECT-EVAL",
        "purpose": (
            "R11 (DSH r1): register the gitignored external evidence tree "
            "with sha256 so reviewers can verify existence/integrity; "
            "WARNING: if previews_* are lost, the per-frame agent verdicts "
            "in sfx-spot-check-verdicts.json cannot be independently "
            "re-inspected (visual basis gone); geometry remains recomputable "
            "from the committed JSON payloads"
        ),
        "worktree_root": str(args.worktree_root.resolve()),
        "task_env_root": str(env),
        "group_file_counts": counts,
        "total_files": total,
        "groups": groups,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    print(f"inventory: {total} files ({counts}) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
