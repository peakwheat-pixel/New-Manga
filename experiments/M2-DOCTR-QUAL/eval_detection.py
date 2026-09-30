"""Run real docTR Detection over the qualification eval manifest and score it.

The engine is built with the exact production call sequence
(``src/infrastructure/providers/detection_doctr.py::_build_engine``):
``fast_base(pretrained=False)`` + ``load_pretrained_params(local pin)`` +
``detection_predictor(assume_straight_pages=True, batch_size=1)`` — no
runtime download, SHA-256 checked before the model is built.

Three scoring layers against the manifest GT (granularity contract: docTR
raw output is word-level, GT is block-level, so strict IoU at word
granularity systematically underestimates and is DIAGNOSTIC ONLY — never
judged):
- ``raw_strict``: docTR detection instances vs IoU >= threshold (diagnostic);
- ``block_strict``: production merged blocks vs IoU >= threshold (strict
  block-level diagnostic);
- ``block_coverage`` (PRIMARY judging layer): production merged blocks vs
  ``intersection/gt_area >= threshold``, one-to-one greedy. The primary
  layer/criterion contract lives in thresholds.json (``primary_layer`` /
  ``judging_criterion``) and is subject to the pending qualification ruling.

Matching: one-to-one greedy by descending confidence. Recognition is never
consulted. Usage:

  PYTHONPATH=src python experiments/M2-DOCTR-QUAL/eval_detection.py \
      --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
      --weights "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt" \
      --arch fast_base --device cuda \
      --out verification/M2-DOCTR-QUAL/results-fast_base-cuda-seg05.json
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
THRESHOLDS = json.loads((Path(__file__).parent / "thresholds.json").read_text(encoding="utf-8"))

#: Weight pins. fast_base = production pin (detection_doctr.py
#: DOCTR_WEIGHTS_SHA256, also in verification/.../weights-manifest.json);
#: db_resnet50 = measured in this task, snapshotted in the same manifest.
#: Three references on purpose: a drift breaks loudly here.
EXPECTED_SHA256 = {
    "fast_base": "688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace",
    "db_resnet50": "79bd7d702506703b89cf11afa42d12aebf5cf25c3618e6ffd5f85772240ca483",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_engine(weights_path: Path, arch: str, device: str):
    """Mirror the production adapter's frozen load sequence for ``arch``."""
    if sha256_file(weights_path) != EXPECTED_SHA256[arch]:
        raise SystemExit(f"weights sha256 mismatch for {weights_path}")
    import torch
    import importlib
    import doctr.models

    # attribute access on doctr.models.utils is shadowed by
    # doctr.models.recognition.utils; resolve the real module like the
    # production adapter's _lazy_import does.
    doctr_utils = importlib.import_module("doctr.models.utils")

    if device not in ("cpu", "cuda"):
        raise SystemExit(f"unsupported device {device}")
    if device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("cuda requested but torch.cuda.is_available() is False")

    model = doctr.models.detection.__dict__[arch](pretrained=False)
    doctr_utils.load_pretrained_params(model, str(weights_path))
    model.eval()
    if device == "cuda":
        model = model.cuda()
    predictor = doctr.models.detection_predictor(
        arch=model,
        pretrained=False,
        assume_straight_pages=True,
        batch_size=1,
    )
    return predictor


def iou(a, b) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    denom = area_a + area_b - inter
    return inter / denom if denom > 0.0 else 0.0


def match_greedy(dets, gts, thr, criterion="iou"):
    """dets: [(box, conf)], gts: [box]; returns (tp pairs, n_fp, matched scores).

    criterion='iou': Jaccard IoU >= thr (strict). criterion='coverage':
    intersection/gt_area >= thr (detection must cover the GT block; forgives
    block-boundary differences between merged word boxes and cleaning masks).
    """
    order = sorted(range(len(dets)), key=lambda i: -dets[i][1])
    taken = [False] * len(gts)
    pairs, fp, matched_scores = [], 0, []

    def score(dbox, gbox):
        ix0, iy0 = max(dbox[0], gbox[0]), max(dbox[1], gbox[1])
        ix1, iy1 = min(dbox[2], gbox[2]), min(dbox[3], gbox[3])
        inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
        if inter <= 0.0:
            return 0.0
        if criterion == "coverage":
            area_g = max(0.0, gbox[2] - gbox[0]) * max(0.0, gbox[3] - gbox[1])
            return inter / area_g if area_g > 0.0 else 0.0
        return iou(dbox, gbox)

    for di in order:
        dbox = dets[di][0]
        best, best_score = -1, 0.0
        for gi, gbox in enumerate(gts):
            if taken[gi]:
                continue
            v = score(dbox, gbox)
            if v >= thr and v > best_score:
                best, best_score = gi, v
        if best >= 0:
            taken[best] = True
            pairs.append((di, best))
            matched_scores.append(best_score)
        else:
            fp += 1
    return pairs, fp, matched_scores


def blocks_to_rects(blocks, shrink_pad=0.0):
    """rects from block polygons; ``shrink_pad`` pulls each side back in
    (sensitivity control for the production MERGE_PAD_PX growth, which pads
    candidates by 6px on every side before we compare them to unpadded GT)."""
    rects = []
    for polygon, conf in blocks:
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        rects.append(
            (
                [
                    min(xs) + shrink_pad,
                    min(ys) + shrink_pad,
                    max(xs) - shrink_pad,
                    max(ys) - shrink_pad,
                ],
                conf,
            )
        )
    return rects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--arch", choices=sorted(EXPECTED_SHA256), default="fast_base")
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None, help="first N regions (smoke)")
    parser.add_argument("--previews", type=int, default=12, help="annotated preview count")
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=Path(r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/previews"),
    )
    parser.add_argument(
        "--strip-block-pad",
        type=float,
        default=0.0,
        help="shrink each merged block by this many px per side before "
        "matching (sensitivity control for the production MERGE_PAD_PX=6 "
        "growth; 0 keeps the production-faithful path)",
    )
    parser.add_argument(
        "--task",
        default="M2-DOCTR-QUAL-PREFLIGHT",
        help="label written into the results payload 'task' field "
        "(default keeps the preflight value; the formal qualification run "
        "passes M2-DOCTR-QUAL-RUN). Metadata only — no metric impact.",
    )
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    regions = manifest["regions"]
    if args.limit:
        regions = regions[: args.limit]

    predictor = build_engine(args.weights, args.arch, args.device)
    try:
        cluster_words_into_blocks = importlib.import_module(
            "infrastructure.providers.detection_doctr"
        ).cluster_words_into_blocks
        block_policy = "production cluster_words_into_blocks (PYTHONPATH=src)"
    except ImportError:
        cluster_words_into_blocks = None
        block_policy = "UNAVAILABLE (run with PYTHONPATH=src for the block layer)"

    import numpy as np
    from PIL import Image, ImageDraw

    thr = THRESHOLDS["iou_match_threshold"]
    min_gt_severe = THRESHOLDS["severe_page_miss_min_gt"]
    args.preview_dir.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    per_region = []
    agg = {
        key: {"n_det": 0, "n_gt": 0, "tp": 0, "fp": 0, "score_sum": 0.0}
        for key in ("raw_strict", "block_strict", "block_coverage")
    }
    severe = {"regions_with_gt": 0, "severe_miss": 0}
    fp_attr = {
        "fp_total": 0,
        "with_text_evidence": 0,
        "pure": 0,
        "attribution_available": None,
    }
    supp_iou_thr = 0.3
    preview_written = 0
    started = time.perf_counter()

    for entry in regions:
        img = Image.open(entry["image"]).convert("RGB")
        rgb = np.asarray(img, dtype=np.uint8)
        if (rgb.shape[1], rgb.shape[0]) != (entry["width"], entry["height"]):
            raise SystemExit(f"region image size mismatch: {entry['image']}")
        result = predictor([rgb])
        words = result[0]["words"] if isinstance(result[0], dict) else result[0]
        np_mod = np
        arr = np_mod.asarray(words, dtype=float).reshape(-1, 5)
        w, h = float(entry["width"]), float(entry["height"])
        raw_boxes = [
            (
                [
                    min(max(r[0] * w, 0.0), w),
                    min(max(r[1] * h, 0.0), h),
                    min(max(r[2] * w, 0.0), w),
                    min(max(r[3] * h, 0.0), h),
                ],
                float(r[4]),
            )
            for r in arr
        ]

        gts = entry["gt_boxes"]
        if cluster_words_into_blocks is not None:
            blocks = cluster_words_into_blocks(
                [b[0] for b in raw_boxes], [b[1] for b in raw_boxes], page_size=(w, h)
            )
            block_rects = blocks_to_rects(blocks, shrink_pad=args.strip_block_pad)
        else:
            block_rects = []

        # Granularity contract: GT boxes are BLOCK-level (dataset cleaning
        # masks) while docTR raw output is word-level; strict IoU at word
        # granularity systematically underestimates and is diagnostic only.
        # The production merge policy produces block-level candidates, which
        # is the layer the application consumes and the layer we judge.
        runs = {
            "raw_strict": (raw_boxes, "iou"),
            "block_strict": (block_rects, "iou"),
            "block_coverage": (block_rects, "coverage"),
        }

        record = {
            "case_id": entry["case_id"],
            "region_index": entry["region_index"],
            "n_gt": len(gts),
            "n_det_raw": len(raw_boxes),
            "n_det_block": len(block_rects),
        }
        if gts:
            severe["regions_with_gt"] += 1
        block_coverage_fp_boxes = []
        for key, (det_list, criterion) in runs.items():
            pairs, fp, matched_scores = match_greedy(det_list, gts, thr, criterion)
            agg[key]["n_det"] += len(det_list)
            agg[key]["n_gt"] += len(gts)
            agg[key]["tp"] += len(pairs)
            agg[key]["fp"] += fp
            agg[key]["score_sum"] += sum(matched_scores)
            record[f"tp_{key}"] = len(pairs)
            record[f"fn_{key}"] = len(gts) - len(pairs)
            if key == "block_coverage":
                matched_di = {di for di, _ in pairs}
                block_coverage_fp_boxes = [
                    det_list[di][0]
                    for di in range(len(det_list))
                    if di not in matched_di
                ]
        if gts and len(gts) >= min_gt_severe and record["tp_block_coverage"] == 0:
            severe["severe_miss"] += 1
        # FP attribution: how many block-coverage FPs overlap auxiliary text
        # evidence outside the GT subset (GT coverage gap) vs none at all.
        # Only meaningful when the manifest carries supplementary_boxes
        # (union mode); without them attribution would be structurally all-
        # pure, so we mark it unavailable instead of reporting a constant.
        supp = entry.get("supplementary_boxes")
        attribution_available = supp is not None
        if fp_attr["attribution_available"] is None:
            fp_attr["attribution_available"] = attribution_available
        for box in block_coverage_fp_boxes:
            fp_attr["fp_total"] += 1
            if attribution_available:
                best = max((iou(box, s) for s in supp), default=0.0) if supp else 0.0
                if best >= supp_iou_thr:
                    fp_attr["with_text_evidence"] += 1
                else:
                    fp_attr["pure"] += 1
        per_region.append(record)

        if preview_written < args.previews and gts:
            canvas = img.copy()
            draw = ImageDraw.Draw(canvas)
            for gbox in gts:
                draw.rectangle(gbox, outline=(0, 200, 0), width=3)
            for box, _conf in raw_boxes:
                draw.rectangle(box, outline=(255, 0, 0), width=2)
            preview_name = f"{entry['case_id']}_R{entry['region_index']:03d}.png"
            canvas.save(args.preview_dir / preview_name, format="PNG")
            preview_written += 1

    elapsed = time.perf_counter() - started
    summary = {}
    for key, a in agg.items():
        tp, fp, n_gt = a["tp"], a["fp"], a["n_gt"]
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / n_gt if n_gt else 0.0
        mean_score = a["score_sum"] / tp if tp else 0.0
        severe_rate = (
            severe["severe_miss"] / severe["regions_with_gt"]
            if severe["regions_with_gt"]
            else 0.0
        )
        metric_name = "mean_matched_iou" if key.endswith("strict") else "mean_matched_coverage"
        summary[key] = {
            "n_det": a["n_det"],
            "n_gt": n_gt,
            "tp": tp,
            "fp": fp,
            "fn": n_gt - tp,
            "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            metric_name: mean_score,
            "severe_page_miss": {
                # primary-layer statistic, repeated across the three layer
                # summaries for reference only — computed on block_coverage
                "layer": "block_coverage",
                "definition": THRESHOLDS["severe_page_miss_definition"],
                "regions_with_gt": severe["regions_with_gt"],
                "severe_miss_regions": severe["severe_miss"],
                "rate": severe_rate,
            },
        }

    primary = summary["block_coverage"]
    severe_rate = primary["severe_page_miss"]["rate"]
    # Frozen contract (thresholds.json, user ruling 2026-09-30): gates live
    # under "gates" and Precision is a non-gate observation. Flat preflight
    # files (no "gates" key, flat "min_precision") keep the legacy 4-gate
    # behavior. Everything above is metric computation and is untouched —
    # this block only maps the frozen gate set onto the computed summary.
    gates = THRESHOLDS.get("gates", THRESHOLDS)
    min_recall = gates["min_recall"]
    min_mean_cov = gates.get("min_mean_coverage", gates.get("min_mean_iou"))
    max_severe = gates["max_severe_page_miss_rate"]
    verdict = {
        "judging_layer": (
            "block_coverage (production merged blocks vs block-level GT, "
            "coverage = intersection/gt_area >= 0.5); raw_strict kept for "
            "granularity diagnosis only, never judged"
        ),
        "recall": {
            "threshold": min_recall,
            "value": primary["recall"],
            "pass": primary["recall"] >= min_recall,
        },
    }
    if "min_precision" in gates:
        verdict["precision"] = {
            "threshold": gates["min_precision"],
            "value": primary["precision"],
            "pass": primary["precision"] >= gates["min_precision"],
        }
    else:
        verdict["precision"] = {
            "gate": False,
            "value": primary["precision"],
            "reference": THRESHOLDS.get("non_gate_observations", {}).get(
                "min_precision_reference"
            ),
            "note": (
                "pollution-bounded lower bound (GT blind spot: SFX / "
                "background text unannotated); NOT a gate — user ruling "
                "2026-09-30"
            ),
        }
    verdict["mean_coverage"] = {
        "threshold": min_mean_cov,
        "value": primary["mean_matched_coverage"],
        "pass": primary["mean_matched_coverage"] >= min_mean_cov,
    }
    verdict["severe_page_miss_rate"] = {
        "threshold": max_severe,
        "value": severe_rate,
        "pass": severe_rate <= max_severe,
    }
    verdict["all_pass"] = all(v["pass"] for v in verdict.values() if isinstance(v, dict) and "pass" in v)

    import hashlib as _hashlib

    manifest_sha256 = _hashlib.sha256(args.manifest.read_bytes()).hexdigest()
    out_payload = {
        "schema": "m2-doctr-qual/eval-results@2",
        "task": args.task,
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(timespec="seconds"),
        "arch": args.arch,
        "device": args.device,
        "weights": {
            "path": str(args.weights),
            "sha256": EXPECTED_SHA256[args.arch],
        },
        "manifest": str(args.manifest),
        "manifest_sha256": manifest_sha256,
        "manifest_gt_mode": manifest.get("gt_mode"),
        "manifest_n_gt_boxes": manifest.get("n_gt_boxes"),
        "manifest_n_regions": manifest.get("n_regions"),
        "manifest_gt_provenance": manifest.get("gt_provenance"),
        "block_policy": block_policy,
        "strip_block_pad": args.strip_block_pad,
        "thresholds": THRESHOLDS,
        "iou_match_threshold": thr,
        "n_regions_evaluated": len(per_region),
        "elapsed_seconds": round(elapsed, 2),
        "summary": summary,
        "fp_attribution_block_coverage": {
            "attribution_available": fp_attr["attribution_available"],
            "note": (
                "FPs scored against manifest supplementary_boxes (auxiliary "
                "text evidence outside the GT subset); Jaccard IoU>=0.3 "
                "counts as GT-coverage FP, otherwise pure. Only union-mode "
                "manifests carry supplementary_boxes; without them "
                "attribution is unavailable (not 'all pure')."
            ),
            **fp_attr,
        },
        "verdict_vs_default_thresholds": verdict,
        "per_region": per_region,
    }
    def _py(obj):
        """JSON-safe: numpy scalars (np.bool_/np.float64) are not serializable."""
        if isinstance(obj, dict):
            return {k: _py(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_py(v) for v in obj]
        if hasattr(obj, "item") and not isinstance(obj, (str, bytes)):
            return obj.item()
        return obj

    out_payload = _py(out_payload)
    args.out.write_text(json.dumps(out_payload, indent=1, ensure_ascii=False), encoding="utf-8")

    s = summary["block_coverage"]
    print(f"arch={args.arch} device={args.device} regions={len(per_region)} elapsed={elapsed:.1f}s")
    print(
        f"PRIMARY block_coverage: precision={s['precision']:.4f} "
        f"recall={s['recall']:.4f} meanCov={s['mean_matched_coverage']:.4f} "
        f"severe_miss_rate={severe_rate:.4f}"
    )
    bs = summary["block_strict"]
    print(
        f"diag block_strict:      precision={bs['precision']:.4f} "
        f"recall={bs['recall']:.4f} meanIoU={bs['mean_matched_iou']:.4f}"
    )
    rs = summary["raw_strict"]
    print(
        f"diag raw_strict (word granularity, NOT judged): recall={rs['recall']:.4f}"
    )
    if fp_attr["attribution_available"]:
        if fp_attr["fp_total"]:
            cov = fp_attr["with_text_evidence"] / fp_attr["fp_total"]
            print(
                f"FP attribution: {fp_attr['fp_total']} block_coverage FPs -> "
                f"{fp_attr['with_text_evidence']} with text evidence "
                f"({cov:.1%}, GT coverage gap) / {fp_attr['pure']} pure"
            )
    else:
        print(
            "FP attribution: UNAVAILABLE (manifest has no supplementary_boxes; "
            "run --gt-mode union manifest for the evidence layer)"
        )
    print(f"verdict all_pass={verdict['all_pass']}")
    print(f"results -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
