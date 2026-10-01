"""M2-TA3-B2 phase-2: independent verification of the Git-free pixel tree.

R7 + R8 (DSH r1): the delivered artifacts previously had no generator script
and no per-file inventory, so "independent recompute" was not reproducible
and the external tree had no tamper-evidence.  This script closes both:

  1. export-hash-recompute.json — recompute sha256/size of EVERY OK export
     recorded by the runner (main pass AND ``.rerun`` exports), from the
     pixel files themselves + the case summaries; records the pixel file's
     path RELATIVE to the pixel root so the manifest and the recompute
     cross-reference each other.
  2. pixels-manifest.json — full inventory of the pixel root: every file's
     relative path + size + sha256.  This is the review precondition for
     "external evidence stays auditable" (M2-SFX-DETECT-EVAL DSH r1 R11
     precedent): without it a change outside the repo tree is invisible.

Standard library only; reads the pixel files and the summaries, nothing
else (runner-independent by construction).  Idempotent: rerunning after an
unchanged pixel tree must produce identical JSON apart from timestamps.

Run:
  python experiments/M2-TA3-B/verify_exports.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE2 = REPO_ROOT / "verification" / "M2-TA3-B" / "phase2"
PIXEL_ROOT_DEFAULT = Path(r"G:/CODEX/New Manga.task-envs/M2-TA3-B/phase2-pixels")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify_exports(summaries_dir: Path, pixel_root: Path) -> dict:
    """Recompute every OK export recorded in the case summaries."""
    records = []
    for path in sorted(summaries_dir.glob("qual-*.json")):
        if path.name.startswith("qual-report"):
            continue
        summary = json.loads(path.read_text(encoding="utf-8"))
        export = summary.get("export") or {}
        if export.get("status") != "OK":
            continue
        pixel_path = Path(export["pixel_path"])
        rel = pixel_path.relative_to(pixel_root).as_posix()
        actual = pixel_path.read_bytes()
        recomputed = hashlib.sha256(actual).hexdigest()
        records.append(
            {
                "case_id": summary["case_id"],
                "rerun": bool(summary.get("rerun_suffix")),
                "summary_file": f"summaries/{path.name}",
                "pixel_relative_path": rel,
                "summary_sha256": export.get("sha256", ""),
                "recomputed_sha256": recomputed,
                "match": export.get("sha256", "") == recomputed,
                "size_bytes_recorded": export.get("size"),
                "size_bytes_actual": len(actual),
                "size_match": export.get("size") == len(actual),
            }
        )
    return {
        "task": "M2-TA3-B2",
        "generated_at_utc": _now_utc(),
        "method": (
            "independent recompute (stdlib hashlib) of every OK export "
            "recorded by the runner — main pass AND .rerun exports (R7, DSH "
            "r1); runner-independent by construction (this script only "
            "reads the pixel files and the summaries); generator script "
            "checked in at experiments/M2-TA3-B/verify_exports.py"
        ),
        "pixel_root": str(pixel_root),
        "n_ok_exports": len(records),
        "all_match": all(r["match"] and r["size_match"] for r in records),
        "records": records,
    }


def build_pixels_manifest(pixel_root: Path) -> dict:
    """Full inventory of the pixel tree (relative path + size + sha256)."""
    files = []
    for path in sorted(pixel_root.rglob("*")):
        if path.is_file():
            files.append(
                {
                    "path": path.relative_to(pixel_root).as_posix(),
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    return {
        "task": "M2-TA3-B2",
        "generated_at_utc": _now_utc(),
        "purpose": (
            "audit preconditions for the Git-free pixel tree (R8, DSH r1): "
            "the pixel root is a sibling directory of the repository tree "
            "(invisible to Git by construction, no .gitignore involved), so "
            "this manifest is the only tamper-evidence for the crops and "
            "export PNGs cited by the summaries and worksheets"
        ),
        "pixel_root": str(pixel_root),
        "n_files": len(files),
        "total_bytes": sum(f["size_bytes"] for f in files),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summaries-dir", default=str(PHASE2 / "summaries"))
    parser.add_argument("--pixel-root", default=str(PIXEL_ROOT_DEFAULT))
    parser.add_argument(
        "--skip-manifest", action="store_true",
        help="only recompute the export hashes (skip the full-tree manifest)",
    )
    args = parser.parse_args()

    summaries_dir = Path(args.summaries_dir)
    pixel_root = Path(args.pixel_root)
    if not pixel_root.is_dir():
        print(f"FATAL: pixel root missing: {pixel_root}", file=__import__("sys").stderr)
        return 2

    out_dir = PHASE2 / "export"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = verify_exports(summaries_dir, pixel_root)
    report_path = out_dir / "export-hash-recompute.json"
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"export recompute: n={report['n_ok_exports']} all_match={report['all_match']} -> {report_path}")

    if not args.skip_manifest:
        manifest = build_pixels_manifest(pixel_root)
        manifest_path = PHASE2 / "pixels-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"pixels manifest: n={manifest['n_files']} files "
            f"({manifest['total_bytes']} bytes) -> {manifest_path}"
        )
    return 0 if report["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
