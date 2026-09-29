"""Build the Real docTR qualification eval manifest from comic_golden_suite.

Read-only over ``test_assets/comic_golden_suite``: region crops and the eval
manifest are written OUTSIDE the repository (default under task-envs) so no
copyrighted pixels land in git. The manifest records the exact GT provenance
(dataset auxiliary ``text_seg`` annotations filtered by score) so the metric
scope is auditable. Requires Pillow for the region crops (manifest metadata
computation alone is stdlib).

GT model (KO Cleaned Webtoon ``info.json``):
- ``text_seg`` boxes carry usable confidence (median ~0.9); this is the GT
  source for the judging mode, filtered by ``--gt-min-score`` (default 0.5).
- ``text_ctd`` boxes score median ~0.06 on this dataset and are excluded
  from the judging GT (they only feed the union evidence layer).
- ``uncleaned_boxes`` are cleaning-residual bookkeeping, not scored GT.

A GT box belongs to the region that contains its center point (regions are
asserted full-width and non-overlapping in y); boxes whose center falls
outside every region are counted per case as ``gt_centers_outside_regions``.
Boxes assigned to a region are clamped to the region rectangle; crossing
boxes therefore appear truncated exactly as the detector sees them.

Usage:
  python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --level full --gt-mode seg05
  python experiments/M2-DOCTR-QUAL/build_eval_manifest.py --cases K01 --cases K02
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUITE = REPO_ROOT / "test_assets" / "comic_golden_suite"
CASES_JSON = SUITE / "manifests" / "cases.json"
DEFAULT_WORK = Path(r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="manifest path")
    parser.add_argument(
        "--work", type=Path, default=DEFAULT_WORK, help="region crop output dir"
    )
    parser.add_argument(
        "--cases",
        action="append",
        default=None,
        help="explicit case ids (repeatable); default: all Cleaned Webtoon cases",
    )
    parser.add_argument(
        "--level",
        choices=["smoke", "full"],
        default="full",
        help="smoke = first 2 cases, full = every Cleaned Webtoon case",
    )
    parser.add_argument("--gt-min-score", type=float, default=0.5)
    parser.add_argument(
        "--gt-mode",
        choices=["seg05", "union"],
        default="seg05",
        help="seg05 = text_seg only (conservative GT-A); union = merged "
        "text_seg(>=0.3) + text_ctd + uncleaned_boxes (coverage GT-B, "
        "merged greedily at IoU>=0.5)",
    )
    args = parser.parse_args()

    catalog = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    ko_cases = [
        c
        for c in catalog["cases"]
        if c.get("source_name") == "Cleaned Webtoon Dataset"
        and c.get("asset_status") == "READY"
    ]
    ko_cases.sort(key=lambda c: c["case_id"])
    if args.cases:
        wanted = set(args.cases)
        selected = [c for c in ko_cases if c["case_id"] in wanted]
        missing = wanted - {c["case_id"] for c in selected}
        if missing:
            raise SystemExit(f"unknown or not-ready case ids: {sorted(missing)}")
    elif args.level == "smoke":
        selected = ko_cases[:2]
    else:
        selected = ko_cases

    regions_dir = args.work / "regions"
    regions_dir.mkdir(parents=True, exist_ok=True)

    from PIL import Image

    def assert_regions_sane(regions, strip_w):
        """GT assignment rule assumes full-width, y-disjoint regions; make
        that explicit instead of implicit (D-side review P2-3)."""
        spans = sorted((r["y0"], r["y1"]) for r in regions)
        for (a0, a1), (b0, b1) in zip(spans, spans[1:]):
            if b0 < a1:
                raise SystemExit(f"overlapping region y-spans: {a0}-{a1} vs {b0}-{b1}")
        for r in regions:
            if r["x0"] != 0 or r["x1"] != strip_w:
                raise SystemExit(
                    f"non-full-width region {r}: assignment rule assumes "
                    "full-width slices"
                )

    def merge_boxes(boxes):
        """Greedy union merge: sort by score desc, absorb IoU>=0.5 overlaps."""
        merged = []
        for box in sorted(boxes, key=lambda b: -b[4]):
            absorbed = False
            for m in merged:
                if iou_tuple(m, box) >= 0.5:
                    m[0], m[1] = min(m[0], box[0]), min(m[1], box[1])
                    m[2], m[3] = max(m[2], box[2]), max(m[3], box[3])
                    m[4] = max(m[4], box[4])
                    absorbed = True
                    break
            if not absorbed:
                merged.append(list(box))
        return merged

    def iou_tuple(a, b):
        ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
        ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
        inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
        if inter <= 0.0:
            return 0.0
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        denom = area_a + area_b - inter
        return inter / denom if denom > 0.0 else 0.0

    entries: list[dict] = []
    case_summary: list[dict] = []
    for case in selected:
        case_dir = SUITE / case["local_path"]
        info = json.loads((case_dir / "info.json").read_text(encoding="utf-8"))
        strip_w, strip_h = info["strip_width"], info["strip_height"]
        seg_all = [
            (b["x1"], b["y1"], b["x2"], b["y2"], float(b["score"]))
            for b in info.get("text_boxes", [])
            if b.get("model") == "text_seg"
        ]
        ctd_all = [
            (b["x1"], b["y1"], b["x2"], b["y2"], float(b["score"]))
            for b in info.get("text_boxes", [])
            if b.get("model") == "text_ctd"
        ]
        uncleaned = [
            (b["x1"], b["y1"], b["x2"], b["y2"], 0.4)
            for b in info.get("uncleaned_boxes", [])
        ]
        gt_strip = (
            [b for b in seg_all if b[4] >= args.gt_min_score]
            if args.gt_mode == "seg05"
            else merge_boxes(
                [b for b in seg_all if b[4] >= 0.3] + ctd_all + uncleaned
            )
        )
        n_gt_total = len(gt_strip)
        regions = sorted(info["approved_regions"], key=lambda r: r["y0"])
        assert_regions_sane(regions, strip_w)

        with Image.open(case_dir / "base.png") as strip:
            if strip.size != (strip_w, strip_h):
                raise SystemExit(
                    f"{case['case_id']}: strip size {strip.size} != manifest "
                    f"{strip_w}x{strip_h}"
                )
            assigned = 0
            for region in regions:
                rx0, ry0, rx1, ry1 = (
                    region["x0"],
                    region["y0"],
                    region["x1"],
                    region["y1"],
                )
                local_gt = []
                for (gx0, gy0, gx1, gy1, score) in gt_strip:
                    cx, cy = (gx0 + gx1) / 2.0, (gy0 + gy1) / 2.0
                    if not (ry0 <= cy < ry1):
                        continue
                    lx0 = min(max(gx0 - rx0, 0), rx1 - rx0)
                    ly0 = min(max(gy0 - ry0, 0), ry1 - ry0)
                    lx1 = min(max(gx1 - rx0, 0), rx1 - rx0)
                    ly1 = min(max(gy1 - ry0, 0), ry1 - ry0)
                    if lx1 <= lx0 or ly1 <= ly0:
                        continue
                    local_gt.append([lx0, ly0, lx1, ly1])
                    assigned += 1
                image_name = f"{case['case_id']}_R{region['index']:03d}.png"
                crop = strip.crop((rx0, ry0, rx1, ry1))
                crop.save(regions_dir / image_name, format="PNG")
                entry = {
                    "case_id": case["case_id"],
                    "region_index": region["index"],
                    "image": str((regions_dir / image_name).resolve()),
                    "width": rx1 - rx0,
                    "height": ry1 - ry0,
                    "n_gt": len(local_gt),
                    "gt_boxes": local_gt,
                }
                if args.gt_mode == "union":
                    # supplementary evidence = all auxiliary annotations that
                    # are NOT already GT; used by eval to attribute FPs to GT
                    # coverage gaps instead of detector error
                    supp = []
                    for (gx0, gy0, gx1, gy1, _s) in seg_all + ctd_all + uncleaned:
                        cx, cy = (gx0 + gx1) / 2.0, (gy0 + gy1) / 2.0
                        if not (ry0 <= cy < ry1):
                            continue
                        lx0 = min(max(gx0 - rx0, 0), rx1 - rx0)
                        ly0 = min(max(gy0 - ry0, 0), ry1 - ry0)
                        lx1 = min(max(gx1 - rx0, 0), rx1 - rx0)
                        ly1 = min(max(gy1 - ry0, 0), ry1 - ry0)
                        if lx1 <= lx0 or ly1 <= ly0:
                            continue
                        box = [lx0, ly0, lx1, ly1]
                        if not any(
                            iou_tuple(box, g) >= 0.5 for g in local_gt
                        ):
                            supp.append(box)
                    entry["supplementary_boxes"] = supp
                entries.append(entry)
        case_summary.append(
            {
                "case_id": case["case_id"],
                "local_path": case["local_path"],
                "strip": [strip_w, strip_h],
                "n_regions": len(regions),
                "n_gt_text_seg_ge_score": n_gt_total,
                "gt_assigned_to_regions": assigned,
                "gt_centers_outside_regions": n_gt_total - assigned,
                "license_class": case.get("license_class"),
            }
        )
        print(
            f"{case['case_id']}: {len(regions)} regions, GT(n)={n_gt_total} "
            f"assigned={assigned} outside={n_gt_total - assigned}"
        )

    manifest = {
        "schema": "m2-doctr-qual/eval-manifest@2",
        "generated_at": "2026-09-29",
        "task": "M2-DOCTR-QUAL-PREFLIGHT",
        "suite_manifest": str(CASES_JSON),
        "gt_mode": args.gt_mode,
        "union_params": {
            "text_seg_min_score": 0.3,
            "text_ctd": "all boxes included",
            "uncleaned_boxes": "included with pseudo-score 0.4",
            "merge_rule": "greedy union merge at IoU>=0.5, score-descending",
        }
        if args.gt_mode == "union"
        else None,
        "gt_provenance": (
            "dataset auxiliary annotations (pseudo-GT, not human annotation). "
            "seg05/GT-A: info.json text_boxes where model=='text_seg' and "
            f"score>={args.gt_min_score}. union/GT-B: merged text_seg(>=0.3) "
            "+ text_ctd + uncleaned_boxes, greedy union merge at IoU>=0.5. "
            "union manifests also carry supplementary_boxes = auxiliary text "
            "evidence outside GT for FP attribution."
        ),
        "gt_min_score": args.gt_min_score,
        "region_assignment_rule": "GT box follows its center point; assigned boxes clamp to the region rectangle",
        "n_cases": len(selected),
        "n_regions": len(entries),
        "n_gt_boxes": sum(e["n_gt"] for e in entries),
        "case_summary": case_summary,
        "regions": entries,
    }
    out = args.out or (args.work / f"eval-manifest.{args.level}.{args.gt_mode}.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False), encoding="utf-8")
    print(
        f"manifest: {out} cases={manifest['n_cases']} "
        f"regions={manifest['n_regions']} gt={manifest['n_gt_boxes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
