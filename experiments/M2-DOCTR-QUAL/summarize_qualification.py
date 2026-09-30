"""M2-DOCTR-QUAL-RUN: qualification summary + first-run consistency check.

Read-only aggregator for the formal qualification results. Does NOT touch
the integrated evaluation logic in eval_detection.py; it only:

1. loads the three formal results JSONs (main / pad-offset / db_resnet50),
2. field-compares summary and per_region against the preflight first-run
   baselines (determinism check — zero expected differences),
3. derives per-case block_coverage recall and the severe-miss region list,
4. writes a machine-readable evidence JSON for qualification-report.md.

Usage (from the repo root of the task worktree):

    python experiments/M2-DOCTR-QUAL/summarize_qualification.py --out \
        verification/M2-DOCTR-QUAL/qualification/consistency-and-summary.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DEFAULT_BASELINE_DIR = Path(r"G:/CODEX/New Manga/verification/M2-DOCTR-QUAL")
DEFAULT_WORK_DIR = Path(r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _diff(path: str, a, b, out: list) -> None:
    """Recursive field comparison; records every mismatch with both values."""
    if type(a) is not type(b):
        out.append({"field": path, "kind": "type", "formal": repr(a), "baseline": repr(b)})
        return
    if isinstance(a, dict):
        for key in sorted(set(a) & set(b)):
            _diff(f"{path}.{key}", a[key], b[key], out)
        for key in sorted(set(a) - set(b)):
            out.append({"field": f"{path}.{key}", "kind": "only_in_formal"})
        for key in sorted(set(b) - set(a)):
            out.append({"field": f"{path}.{key}", "kind": "only_in_baseline"})
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append({"field": path, "kind": "length", "formal": len(a), "baseline": len(b)})
            return
        for i, (x, y) in enumerate(zip(a, b)):
            _diff(f"{path}[{i}]", x, y, out)
    elif a != b:
        out.append({"field": path, "kind": "value", "formal": a, "baseline": b})


def _compare(formal: dict, baseline: dict) -> dict:
    summary_diffs: list = []
    per_region_diffs: list = []
    _diff("summary", formal["summary"], baseline["summary"], summary_diffs)
    _diff("per_region", formal["per_region"], baseline["per_region"], per_region_diffs)
    return {
        "manifest_sha256_formal": formal["manifest_sha256"],
        "manifest_sha256_baseline": baseline["manifest_sha256"],
        "manifest_sha256_match": formal["manifest_sha256"] == baseline["manifest_sha256"],
        "n_regions_formal": len(formal["per_region"]),
        "n_regions_baseline": len(baseline["per_region"]),
        "summary_diff_count": len(summary_diffs),
        "per_region_diff_count": len(per_region_diffs),
        "summary_diffs": summary_diffs,
        "per_region_diffs": per_region_diffs,
        "deterministic_reproduction": (
            formal["manifest_sha256"] == baseline["manifest_sha256"]
            and not summary_diffs
            and not per_region_diffs
            and len(formal["per_region"]) == len(baseline["per_region"])
        ),
    }


def _per_case(results: dict) -> list:
    agg: dict[str, dict[str, int]] = {}
    for region in results["per_region"]:
        slot = agg.setdefault(region["case_id"], {"n_gt": 0, "tp": 0, "regions_with_gt": 0})
        slot["n_gt"] += region["n_gt"]
        slot["tp"] += region["tp_block_coverage"]
        if region["n_gt"] > 0:
            slot["regions_with_gt"] += 1
    rows = []
    for case_id in sorted(agg):
        slot = agg[case_id]
        recall = slot["tp"] / slot["n_gt"] if slot["n_gt"] else None
        rows.append(
            {
                "case_id": case_id,
                "n_gt": slot["n_gt"],
                "tp_block_coverage": slot["tp"],
                "recall_block_coverage": round(recall, 4) if recall is not None else None,
                "regions_with_gt": slot["regions_with_gt"],
            }
        )
    return rows


def _severe_regions(results: dict, min_gt: int) -> list:
    return [
        {
            "case_id": r["case_id"],
            "region_index": r["region_index"],
            "n_gt": r["n_gt"],
        }
        for r in results["per_region"]
        if r["n_gt"] >= min_gt and r["tp_block_coverage"] == 0
    ]


def _zero_detection_regions(results: dict) -> list:
    return [
        {"case_id": r["case_id"], "region_index": r["region_index"], "n_gt": r["n_gt"]}
        for r in results["per_region"]
        if r["n_gt"] > 0 and r["n_det_block"] == 0
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--qualification-dir",
        type=Path,
        default=Path("verification/M2-DOCTR-QUAL/qualification"),
        help="directory holding the formal results JSONs",
    )
    parser.add_argument("--baseline-dir", type=Path, default=DEFAULT_BASELINE_DIR)
    parser.add_argument("--baseline-work-dir", type=Path, default=DEFAULT_WORK_DIR)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    qdir = args.qual_dir if hasattr(args, "qual_dir") else args.qualification_dir
    formal_main = _load(qdir / "results-formal-fast_base-cuda-seg05.json")
    formal_pad = _load(qdir / "results-formal-fast_base-cuda-seg05-padoffset.json")
    formal_db = _load(qdir / "results-formal-db_resnet50-cuda-seg05.json")

    baseline_fast = _load(args.baseline_dir / "results-fast_base-cuda-seg05.json")
    baseline_db = _load(args.baseline_dir / "results-db_resnet50-cuda-seg05.json")
    baseline_pad = _load(args.baseline_work_dir / "results-fast_base-cuda-seg05-pad0.json")
    union = _load(args.baseline_dir / "results-fast_base-cuda-union.json")

    payload = {
        "schema": "m2-doctr-qual/qualification-summary@1",
        "task": "M2-DOCTR-QUAL-RUN",
        "generated_by": "experiments/M2-DOCTR-QUAL/summarize_qualification.py",
        "gates_applied": {
            "source": "experiments/M2-DOCTR-QUAL/thresholds.json (user ruling 2026-09-30)",
            "primary_layer": "block_coverage",
            "min_recall": 0.92,
            "min_mean_coverage": 0.6,
            "max_severe_page_miss_rate": 0.05,
            "precision": "non-gate observation (pollution-bounded lower bound)",
        },
        "formal_main": {
            "file": "results-formal-fast_base-cuda-seg05.json",
            "verdict": formal_main["verdict_vs_default_thresholds"],
            "summary": formal_main["summary"],
        },
        "formal_pad_offset": {
            "file": "results-formal-fast_base-cuda-seg05-padoffset.json",
            "block_coverage": formal_pad["summary"]["block_coverage"],
            "block_strict": formal_pad["summary"]["block_strict"],
        },
        "formal_db_resnet50": {
            "file": "results-formal-db_resnet50-cuda-seg05.json",
            "verdict": formal_db["verdict_vs_default_thresholds"],
            "block_coverage": formal_db["summary"]["block_coverage"],
            "block_strict": formal_db["summary"]["block_strict"],
            "raw_strict": formal_db["summary"]["raw_strict"],
        },
        "precision_evidence_union": {
            "file": "results-fast_base-cuda-union.json (preflight, FP attribution layer)",
            "fp_attribution": union["fp_attribution_block_coverage"],
        },
        "consistency": {
            "fast_base_vs_first_run": _compare(formal_main, baseline_fast),
            "db_resnet50_vs_first_run": _compare(formal_db, baseline_db),
            "pad_offset_vs_preflight_pad0": _compare(formal_pad, baseline_pad),
        },
        "per_case_block_coverage": _per_case(formal_main),
        "severe_miss_regions_block_coverage": _severe_regions(formal_main, 3),
        "zero_detection_regions": _zero_detection_regions(formal_main),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )

    v = formal_main["verdict_vs_default_thresholds"]
    print(f"consistency-and-summary -> {args.out}")
    print(
        "Gate (block_coverage): "
        f"recall={v['recall']['value']:.4f} (>=0.92 {'PASS' if v['recall']['pass'] else 'FAIL'}), "
        f"meanCov={v['mean_coverage']['value']:.4f} (>=0.60 {'PASS' if v['mean_coverage']['pass'] else 'FAIL'}), "
        f"severe={v['severe_page_miss_rate']['value']:.4f} (<=0.05 {'PASS' if v['severe_page_miss_rate']['pass'] else 'FAIL'}) "
        f"-> all_pass={v['all_pass']}"
    )
    for name, check in payload["consistency"].items():
        print(
            f"consistency {name}: deterministic_reproduction="
            f"{check['deterministic_reproduction']} "
            f"(summary_diff={check['summary_diff_count']}, "
            f"per_region_diff={check['per_region_diff_count']})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
