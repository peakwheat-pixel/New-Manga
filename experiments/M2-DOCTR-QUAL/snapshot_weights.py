"""Snapshot and verify the controlled docTR detection weights (AC1).

The ONLY sanctioned way to obtain the weights is the production flow
(``verification/T1.1.1/scripts/fetch_doctr_weights.py``); the production
adapter never downloads. This script copies already-fetched files from the
local docTR cache into the task snapshot directory, verifies SHA-256 against
the expected pins, and regenerates ``verification/M2-DOCTR-QUAL/
weights-manifest.json`` with the verification command recorded.

Usage (any Python with stdlib):
  python experiments/M2-DOCTR-QUAL/snapshot_weights.py
  python experiments/M2-DOCTR-QUAL/snapshot_weights.py --cache-dir <dir>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

WEIGHTS = [
    {
        "filename": "fast_base-688a8b34.pt",
        "role": "primary (production-pinned detection weights, T1.1.1)",
        "source_url": "https://doctr-static.mindee.com/models?id=v0.8.1/fast_base-688a8b34.pt&src=0",
        "artifact_version": "doctr-static v0.8.1",
        "expected_sha256": "688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace",
        "official_anchor": "doctr 1.1.0 default_cfgs url (doctr/models/detection/fast/pytorch.py:42) and production pin (src/infrastructure/providers/detection_doctr.py)",
    },
    {
        "filename": "db_resnet50-79bd7d70.pt",
        "role": "comparison detection weights (official docTR artifact)",
        "source_url": "https://doctr-static.mindee.com/models?id=v0.7.0/db_resnet50-79bd7d70.pt&src=0",
        "artifact_version": "doctr-static v0.7.0",
        "expected_sha256": "79bd7d702506703b89cf11afa42d12aebf5cf25c3618e6ffd5f85772240ca483",
        "official_anchor": "doctr 1.1.0 default_cfgs url (doctr/models/detection/differentiable_binarization/pytorch.py:31); filename embeds the official content hash prefix",
    },
]
LICENSE = (
    "Apache-2.0 (docTR project, MINDEE, https://github.com/mindee/doctr/blob/"
    "main/LICENSE); artifacts distributed via doctr-static.mindee.com without "
    "a separate license file and follow the project license"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path.home() / ".cache" / "doctr" / "models",
    )
    parser.add_argument(
        "--snapshot-dir",
        type=Path,
        default=Path(r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights"),
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "verification" / "M2-DOCTR-QUAL" / "weights-manifest.json",
    )
    args = parser.parse_args()

    args.snapshot_dir.mkdir(parents=True, exist_ok=True)
    command = (
        "python experiments/M2-DOCTR-QUAL/snapshot_weights.py "
        f"--cache-dir {args.cache_dir} --snapshot-dir {args.snapshot_dir}"
    )
    entries = []
    for spec in WEIGHTS:
        src = args.cache_dir / spec["filename"]
        if not src.is_file():
            raise SystemExit(
                f"missing {src}; fetch it first via "
                "verification/T1.1.1/scripts/fetch_doctr_weights.py"
            )
        size = src.stat().st_size
        digest = sha256_file(src)
        if digest != spec["expected_sha256"]:
            raise SystemExit(
                f"{src}: sha256 {digest} != expected "
                f"{spec['expected_sha256']}; refusing to snapshot"
            )
        dst = args.snapshot_dir / spec["filename"]
        changed = not dst.is_file() or sha256_file(dst) != digest
        if changed:
            shutil.copy2(src, dst)
        if sha256_file(dst) != spec["expected_sha256"]:
            raise SystemExit(f"snapshot byte mismatch after copy: {dst}")
        entries.append(
            {
                "filename": spec["filename"],
                "role": spec["role"],
                "source_url": spec["source_url"],
                "artifact_version": spec["artifact_version"],
                "framework": "PyTorch (python-doctr==1.1.0 default_cfgs url anchor)",
                "license": LICENSE,
                "size_bytes": size,
                "sha256": digest,
                "expected_sha256": spec["expected_sha256"],
                "sha256_verified": True,
                "official_anchor": spec["official_anchor"],
                "snapshot_path": str(dst),
                "cache_origin": str(src),
            }
        )
        print(f"{spec['filename']}: {size} B sha256 verified -> {dst}")

    manifest = {
        "schema": "m2-doctr-qual/weights-manifest@2",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "purpose": "M2-DOCTR-QUAL-PREFLIGHT AC1 controlled weights",
        "verified_by": "ZCode (M2-DOCTR-QUAL-PREFLIGHT owner)",
        "command": command,
        "verification": "sha256 recomputed from snapshot bytes after copy; mismatch aborts",
        "weights": entries,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"manifest -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
