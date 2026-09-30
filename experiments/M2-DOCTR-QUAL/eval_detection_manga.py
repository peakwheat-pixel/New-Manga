"""Manga-domain detector qualification eval (M2-DOCTR-QUAL-C4).

Loads an OFF-THE-SHELF manga-domain text detector (NOT docTR) and scores it
with the SAME frozen pipeline as ``eval_detection.py``: the production
``cluster_words_into_blocks`` merge (``MERGE_PAD_PX=6``), the three scoring
layers (``raw_strict`` / ``block_strict`` diagnostic, ``block_coverage``
primary), one-to-one greedy matching and the frozen ``thresholds.json``
verdict. The integrated eval files are reused strictly by import — this
script changes zero bytes of them.

Candidate (AC1 selection, see the C4 report for the full survey):

- ``ogkalu/comic-text-and-bubble-detector`` (HuggingFace) — RT-DETR-v2
  (backbone ``rt_detr_resnet`` per the pinned ``config.json``; "r50vd,
  42.9M params" is the model-card wording, corroborated by HF API
  safetensors metadata ``F32=42,861,209`` — integration note per DSH r2
  N4/R11), license **Apache-2.0**, trained on
  ~11k manga / webtoon / manhua / western-comic images. Weights are
  downloaded once into the gitignored task-env tree and pinned by SHA-256
  before use (controlled-weight discipline; never committed).

Granularity mapping decision (frozen for this eval, disclosed in the C4
report):

- The model emits three classes: ``0=bubble``, ``1=text_bubble``,
  ``2=text_free``. Only the TEXT classes (1, 2) become detection
  candidates. The ``bubble`` class is the speech-balloon shape, not a
  text box; feeding it in would inflate the coverage criterion
  (``intersection/gt_area``) with non-text area, so it is dropped and the
  drop is counted per region.
- Each kept text box plays the "word" role, exactly like a docTR word box
  in ``eval_detection.py``; the frozen production merge then produces the
  judged block layer. fast_base / db_resnet50 and this candidate thus run
  the identical merge + scoring code path (single-variable detector swap),
  but the actual merge workload is NOT equivalent: this model's raw output
  is already block-level (1021 raw boxes -> 990 merged vs 917 GT), so the
  production merge is near a no-op for it, while docTR's word->block merge
  is load-bearing (DSH r1 R3; see the C4 report §4/§7 for the PASS
  semantics under the production block-consumption criterion).
- The model's own ``preprocessor_config.json`` (resize to 640x640) is used
  as-is: this is an off-the-shelf evaluation, no dataset-specific adapter
  tuning. GT boxes are absolute-pixel seg05 windows; ``post_process`` maps
  predictions back to source pixels before the merge.

Precision is reported ONLY as a pollution-bounded lower bound (GT blind
spot: SFX / background text unannotated) and is not a gate, per the frozen
thresholds.json contract.

Isolated environment (no dependency bleed into the docTR GPU venv):
``G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312``
(torch 2.11.0+cu128, transformers >= 5.17, safetensors).

Usage (from the worktree root):

  PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
      experiments/M2-DOCTR-QUAL/eval_detection_manga.py \
      --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
      --weights-dir "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector" \
      --device cuda --conf-threshold 0.5 \
      --out verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json

Variants for the C4 report: ``--strip-block-pad 6`` (pad offset, reported
as supplementary), ``--conf-threshold 0.3`` (sensitivity, supplementary).

Frame/pair export (M2-DOCTR-QUAL-C1 spot audit, N2 closure): the optional
``--export-frames <path>`` / ``--export-pairs <path>`` flags additionally
write, WITHOUT touching any judging or scoring path, (a) every block-layer
FP box and every unmatched GT box (xyxy + conf + class + layer attribution
+ region id, block layer authoritative with the raw-layer trace attached)
and (b) every ``block_coverage`` matched pair (gt_box, det_box, coverage).
Omitting both flags reproduces the pre-C1 behavior exactly: no extra
files, no extra stdout lines, byte-identical results payload fields.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

# Reuse the integrated evaluation harness BY IMPORT ONLY (zero-change rule).
_HARNESS = importlib.util.spec_from_file_location(
    "eval_detection",
    Path(__file__).resolve().parent / "eval_detection.py",
)
_eval_detection = importlib.util.module_from_spec(_HARNESS)
sys.modules["eval_detection"] = _eval_detection
_HARNESS.loader.exec_module(_eval_detection)

sha256_file = _eval_detection.sha256_file
match_greedy = _eval_detection.match_greedy
blocks_to_rects = _eval_detection.blocks_to_rects
THRESHOLDS = _eval_detection.THRESHOLDS

#: Candidate identity, pinned in the results payload alongside the weights
#: hash (controlled-weight discipline, M2-DOCTR-QUAL-C4 task contract).
CANDIDATE = {
    "kind": "ogkalu/comic-text-and-bubble-detector",
    "arch": "rt_detr_v2_r50vd",
    "license": "apache-2.0",
    "source_url": "https://huggingface.co/ogkalu/comic-text-and-bubble-detector",
    "weights_file": "model.safetensors",
    "classes": {"0": "bubble", "1": "text_bubble", "2": "text_free"},
    "text_classes_used": [1, 2],
}


def load_model(weights_dir: Path, device: str):
    """Load the off-the-shelf RT-DETR-v2 detector from a local pinned dir."""
    import torch
    from transformers import RTDetrImageProcessor, RTDetrV2ForObjectDetection

    if device not in ("cpu", "cuda"):
        raise SystemExit(f"unsupported device {device}")
    if device == "cuda" and not torch.cuda.is_available():
        raise SystemExit("cuda requested but torch.cuda.is_available() is False")

    weights_file = weights_dir / CANDIDATE["weights_file"]
    if not weights_file.is_file():
        raise SystemExit(f"missing pinned weights file: {weights_file}")
    weights_sha256 = sha256_file(weights_file)

    processor = RTDetrImageProcessor.from_pretrained(str(weights_dir))
    model = RTDetrV2ForObjectDetection.from_pretrained(str(weights_dir))
    model.eval()
    if device == "cuda":
        model = model.cuda()
    return model, processor, weights_sha256


def detect_text_boxes(
    model, processor, rgb, width: float, height: float, conf_threshold: float,
    class_sink: list | None = None,
):
    """Run one region; return (text_boxes, n_bubble_dropped).

    text_boxes: [([x0, y0, x1, y1], conf)] in absolute source pixels — the
    union of classes 1+2 only; the bubble class is counted, not kept.
    ``class_sink`` is an OPTIONAL spot-audit export channel (C1): when a
    list is passed, the kept label ids are appended in box order. It never
    participates in detection or scoring; the default None keeps the C4
    behavior byte-identical.
    """
    import torch

    inputs = processor(images=rgb, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    target_sizes = torch.tensor([[int(height), int(width)]])
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=conf_threshold
    )[0]
    text_boxes = []
    n_bubble = 0
    for score, label, box in zip(
        results["scores"].tolist(), results["labels"].tolist(), results["boxes"].tolist()
    ):
        if label not in CANDIDATE["text_classes_used"]:
            n_bubble += 1
            continue
        x0, y0, x1, y1 = box
        x0, y0 = max(0.0, x0), max(0.0, y0)
        x1, y1 = min(width, x1), min(height, y1)
        if x1 <= x0 or y1 <= y0:
            continue
        text_boxes.append(([x0, y0, x1, y1], float(score)))
        if class_sink is not None:
            class_sink.append(int(label))
    return text_boxes, n_bubble


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--weights-dir", type=Path, required=True)
    parser.add_argument("--device", choices=["cpu", "cuda"], default="cuda")
    parser.add_argument("--conf-threshold", type=float, default=0.5,
                        help="post_process score threshold (0.5 is a "
                        "CONSERVATIVE choice for the PASS direction — a "
                        "lower threshold can only raise recall, so 0.5 "
                        "understates the recall ceiling; 0.3 is shipped as "
                        "the sensitivity variant. Lower values are "
                        "supplementary only, never the formal result)")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=None, help="first N regions (smoke)")
    parser.add_argument("--previews", type=int, default=12, help="annotated preview count")
    parser.add_argument(
        "--preview-dir",
        type=Path,
        default=Path(r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/previews"),
    )
    parser.add_argument(
        "--strip-block-pad",
        type=float,
        default=0.0,
        help="shrink each merged block by this many px per side before "
        "matching (pad-offset supplementary variant for the production "
        "MERGE_PAD_PX=6 growth; 0 keeps the production-faithful path)",
    )
    parser.add_argument(
        "--task",
        default="M2-DOCTR-QUAL-C4",
        help="label written into the results payload 'task' field",
    )
    parser.add_argument(
        "--export-frames",
        type=Path,
        default=None,
        help="optional spot-audit frame export (M2-DOCTR-QUAL-C1 / N2): "
        "write every block-layer FP box and every unmatched GT box "
        "(xyxy+conf+class+layer attribution+region id, raw-layer trace "
        "attached) to this JSON path. Additive only: no judging or scoring "
        "path is touched",
    )
    parser.add_argument(
        "--export-pairs",
        type=Path,
        default=None,
        help="optional spot-audit matched-pair export (M2-DOCTR-QUAL-C1 / "
        "N2): write every block_coverage matched pair (gt_box, det_box, "
        "coverage) to this JSON path. Additive only: no judging or scoring "
        "path is touched",
    )
    args = parser.parse_args()

    import numpy as np
    from PIL import Image, ImageDraw

    # Same import surface as eval_detection.py: the production merge is
    # available under PYTHONPATH=src; without it the block layer cannot be
    # built and the run aborts loudly (never silently judges raw only).
    try:
        cluster_words_into_blocks = importlib.import_module(
            "infrastructure.providers.detection_doctr"
        ).cluster_words_into_blocks
        block_policy = "production cluster_words_into_blocks (PYTHONPATH=src)"
    except ImportError:
        raise SystemExit(
            "production merge unavailable: re-run with PYTHONPATH=src "
            "(the block_coverage primary layer requires it)"
        )

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    regions = manifest["regions"]
    if args.limit is not None:
        regions = regions[: args.limit]

    model, processor, weights_sha256 = load_model(args.weights_dir, args.device)

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
    supp_iou_thr = THRESHOLDS["fp_attribution_iou_threshold"]
    preview_written = 0
    n_bubble_dropped_total = 0
    started = time.perf_counter()
    # Spot-audit export state (C1). Purely additive: when both export flags
    # are absent, `export_on` is False and every guarded block below is
    # skipped, leaving the C4 behavior untouched.
    export_on = args.export_frames is not None or args.export_pairs is not None
    matched_di_by_layer: dict[str, set[int]] = {}
    export_frame_rows: list[dict] = []
    export_pair_rows: list[dict] = []

    for entry in regions:
        img = Image.open(entry["image"]).convert("RGB")
        rgb = np.asarray(img, dtype=np.uint8)
        if (rgb.shape[1], rgb.shape[0]) != (entry["width"], entry["height"]):
            raise SystemExit(f"region image size mismatch: {entry['image']}")
        w, h = float(entry["width"]), float(entry["height"])
        raw_classes: list[int] = []
        raw_boxes, n_bubble_dropped = detect_text_boxes(
            model, processor, rgb, w, h, args.conf_threshold,
            class_sink=raw_classes if export_on else None,
        )
        n_bubble_dropped_total += n_bubble_dropped

        gts = entry["gt_boxes"]
        blocks = cluster_words_into_blocks(
            [b[0] for b in raw_boxes], [b[1] for b in raw_boxes], page_size=(w, h)
        )
        block_rects = blocks_to_rects(blocks, shrink_pad=args.strip_block_pad)

        # Granularity contract: identical to eval_detection.py — GT boxes are
        # BLOCK-level, the judged layer is the production-merged block layer;
        # raw boxes are kept for granularity diagnosis only.
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
            "n_bubble_dropped": n_bubble_dropped,
            "n_det_block": len(block_rects),
        }
        if gts:
            severe["regions_with_gt"] += 1
        block_coverage_fp_boxes = []
        bc_matched_gi: set[int] = set()
        for key, (det_list, criterion) in runs.items():
            pairs, fp, matched_scores = match_greedy(det_list, gts, thr, criterion)
            if export_on:
                # additive read-only snapshot for the spot-audit exports
                matched_di_by_layer[key] = {di for di, _ in pairs}
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
                if export_on:
                    bc_matched_gi = {gi for _, gi in pairs}
                    for (di, gi), cov in zip(pairs, matched_scores):
                        export_pair_rows.append(
                            {
                                "case_id": entry["case_id"],
                                "region_index": entry["region_index"],
                                "gt_index": gi,
                                "det_index": di,
                                "gt_box_xyxy": [float(v) for v in gts[gi]],
                                "det_box_xyxy": [float(v) for v in det_list[di][0]],
                                "det_conf": float(det_list[di][1]),
                                "coverage": float(cov),
                            }
                        )
        if gts and len(gts) >= min_gt_severe and record["tp_block_coverage"] == 0:
            severe["severe_miss"] += 1
        # FP attribution mirrors eval_detection.py; seg05 manifests carry no
        # supplementary_boxes, so attribution is structurally unavailable and
        # is reported as such (not as 'all pure').
        supp = entry.get("supplementary_boxes")
        attribution_available = supp is not None
        if fp_attr["attribution_available"] is None:
            fp_attr["attribution_available"] = attribution_available
        for box in block_coverage_fp_boxes:
            fp_attr["fp_total"] += 1
            if attribution_available:
                best = max((_eval_detection.iou(box, s) for s in supp), default=0.0) if supp else 0.0
                if best >= supp_iou_thr:
                    fp_attr["with_text_evidence"] += 1
                else:
                    fp_attr["pure"] += 1
        per_region.append(record)

        if export_on and args.export_frames is not None:
            # Spot-audit frame rows: block layer authoritative (B1/B2 FPs),
            # unmatched GT boxes attributed A1 (region with zero raw
            # detections) / A2 (fully-missed region that HAS detections) /
            # FN-partial (partially matched multi-GT region — outside the
            # frozen 6-layer protocol, exported for completeness only).
            # Purely additive reads of variables computed above.
            region_context = {
                "n_gt": record["n_gt"],
                "n_det_raw": record["n_det_raw"],
                "n_det_block": record["n_det_block"],
                "tp_block_coverage": record["tp_block_coverage"],
                "n_bubble_dropped": record["n_bubble_dropped"],
            }
            is_a2_region = (
                bool(gts)
                and record["tp_block_coverage"] == 0
                and record["n_det_block"] > 0
            )
            for di in range(len(block_rects)):
                if di in matched_di_by_layer["block_coverage"]:
                    continue
                box = block_rects[di][0]
                raw_trace = []
                for ri, (rbox, rconf) in enumerate(raw_boxes):
                    # Overlap attribution (geometric, deterministic): a raw
                    # box is listed when its area overlap with the block
                    # rectangle is positive. The production merge is near a
                    # no-op (1021 raw -> 990 blocks) so traces are almost
                    # always single-member; this is an audit aid, NOT a
                    # re-derivation of merge membership.
                    ix0, iy0 = max(box[0], rbox[0]), max(box[1], rbox[1])
                    ix1, iy1 = min(box[2], rbox[2]), min(box[3], rbox[3])
                    if ix1 - ix0 <= 0.0 or iy1 - iy0 <= 0.0:
                        continue
                    raw_trace.append(
                        {
                            "raw_index": ri,
                            "box_xyxy": [float(v) for v in rbox],
                            "conf": float(rconf),
                            "cls": CANDIDATE["classes"][str(raw_classes[ri])],
                            "raw_strict_matched": ri in matched_di_by_layer["raw_strict"],
                        }
                    )
                export_frame_rows.append(
                    {
                        "kind": "fp_block",
                        "layer": "B1" if gts else "B2",
                        "audit_layer_hint": "A2" if is_a2_region else None,
                        "case_id": entry["case_id"],
                        "region_index": entry["region_index"],
                        "det_index": di,
                        "box_xyxy": [float(v) for v in box],
                        "conf": float(block_rects[di][1]),
                        "cls": "merged_block",
                        "classes_in_block": sorted(
                            {t["cls"] for t in raw_trace}
                        ),
                        "region_context": region_context,
                        "raw_trace": raw_trace,
                    }
                )
            for gi, gbox in enumerate(gts):
                if gi in bc_matched_gi:
                    continue
                if record["n_det_raw"] == 0:
                    gt_layer = "A1"
                elif is_a2_region:
                    gt_layer = "A2"
                else:
                    gt_layer = "FN-partial"
                export_frame_rows.append(
                    {
                        "kind": "gt_unmatched",
                        "layer": gt_layer,
                        "audit_layer_hint": None,
                        "case_id": entry["case_id"],
                        "region_index": entry["region_index"],
                        "gt_index": gi,
                        "box_xyxy": [float(v) for v in gbox],
                        "conf": None,
                        "cls": "gt",
                        "region_context": region_context,
                        "raw_trace": [],
                    }
                )

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
                "layer": "block_coverage",
                "definition": THRESHOLDS["severe_page_miss_definition"],
                "regions_with_gt": severe["regions_with_gt"],
                "severe_miss_regions": severe["severe_miss"],
                "rate": severe_rate,
            },
        }

    # Same frozen verdict mapping as eval_detection.py (thresholds.json,
    # user ruling 2026-09-30): block_coverage primary, precision non-gate.
    primary = summary["block_coverage"]
    severe_rate = primary["severe_page_miss"]["rate"]
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
    verdict["all_pass"] = all(
        v["pass"] for v in verdict.values() if isinstance(v, dict) and "pass" in v
    )

    manifest_sha256 = sha256_file(args.manifest)
    export_flags = ""
    if args.export_frames is not None:
        export_flags += f" --export-frames {args.export_frames}"
    if args.export_pairs is not None:
        export_flags += f" --export-pairs {args.export_pairs}"
    reproduce_command = (
        'PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/'
        'Scripts/python.exe" experiments/M2-DOCTR-QUAL/eval_detection_manga.py '
        f'--manifest "{args.manifest}" --weights-dir "{args.weights_dir}" '
        f"--device {args.device} --conf-threshold {args.conf_threshold} "
        f"--strip-block-pad {args.strip_block_pad} --task {args.task} --out {args.out}"
        f"{export_flags}"
    )
    out_payload = {
        "schema": "m2-doctr-qual/eval-results@2",
        "variant": "m2-doctr-qual-c4/manga-domain-detector@1",
        "task": args.task,
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(timespec="seconds"),
        "candidate": {**CANDIDATE, "weights_sha256": weights_sha256},
        "arch": CANDIDATE["arch"],
        "device": args.device,
        "conf_threshold": args.conf_threshold,
        "classes_used": CANDIDATE["text_classes_used"],
        "n_bubble_class_dropped": n_bubble_dropped_total,
        "granularity_mapping": (
            "model text classes (text_bubble+text_free) -> one merge input "
            "each ('word' role) -> frozen production cluster_words_into_blocks"
            " (MERGE_PAD_PX=6) -> judged block layer; bubble class dropped "
            "(balloon shape, not text); identical merge+scoring path as the "
            "fast_base / db_resnet50 baselines"
        ),
        "weights_dir": str(args.weights_dir),
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
        "reproduce_command": reproduce_command,
        "summary": summary,
        "fp_attribution_block_coverage": {
            "attribution_available": fp_attr["attribution_available"],
            "note": (
                "FPs scored against manifest supplementary_boxes (auxiliary "
                "text evidence outside the GT subset); Jaccard IoU>=0.3 "
                "counts as GT-coverage FP, otherwise pure. seg05 manifests "
                "carry no supplementary_boxes, so attribution is "
                "unavailable (not 'all pure')."
            ),
            **fp_attr,
        },
        "verdict_vs_default_thresholds": verdict,
        "per_region": per_region,
    }

    def _py(obj):
        if isinstance(obj, dict):
            return {k: _py(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [_py(v) for v in obj]
        if hasattr(obj, "item") and not isinstance(obj, (str, bytes)):
            return obj.item()
        return obj

    out_payload = _py(out_payload)
    args.out.write_text(json.dumps(out_payload, indent=1, ensure_ascii=False), encoding="utf-8")

    if export_on:
        export_meta = {
            "task": args.task,
            "source_results": str(args.out),
            "manifest": str(args.manifest),
            "manifest_sha256": manifest_sha256,
            "weights_sha256": weights_sha256,
            "conf_threshold": args.conf_threshold,
            "strip_block_pad": args.strip_block_pad,
            "n_regions_evaluated": len(per_region),
            "layer_definition_note": (
                "block layer authoritative; B1=FP in a region with GT, "
                "B2=FP in a region without GT; unmatched GT = A1 (region "
                "has zero raw detections) / A2 (fully-missed region with "
                "detections) / FN-partial (partially matched region, "
                "outside the frozen 6-layer protocol, exported for "
                "completeness only); raw_trace is geometric overlap "
                "attribution, not merge membership"
            ),
        }
        if args.export_frames is not None:
            b1_rows = [r for r in export_frame_rows if r["layer"] == "B1"]
            b2_rows = [r for r in export_frame_rows if r["layer"] == "B2"]
            a1_rows = [r for r in export_frame_rows if r["layer"] == "A1"]
            a2_gt_rows = [r for r in export_frame_rows if r["layer"] == "A2"]
            a2_regions = sorted(
                {
                    (r["case_id"], r["region_index"])
                    for r in export_frame_rows
                    if r["layer"] == "A2" or r.get("audit_layer_hint") == "A2"
                }
            )
            fnp_rows = [r for r in export_frame_rows if r["layer"] == "FN-partial"]
            d_regions = sum(1 for r in per_region if r["n_det_block"] == 0)
            frames_payload = {
                "schema": "m2-doctr-qual/spot-audit-frames@1",
                **export_meta,
                "layer_denominators": {
                    "A1_frames": len(a1_rows),
                    "A1_regions": len({(r["case_id"], r["region_index"]) for r in a1_rows}),
                    "A2_regions": len(a2_regions),
                    "A2_det_frames_in_region": sum(
                        1
                        for r in export_frame_rows
                        if r["kind"] == "fp_block" and r.get("audit_layer_hint") == "A2"
                    ),
                    "B1_frames": len(b1_rows),
                    "B1_regions": len({(r["case_id"], r["region_index"]) for r in b1_rows}),
                    "B2_frames": len(b2_rows),
                    "B2_regions": len({(r["case_id"], r["region_index"]) for r in b2_rows}),
                    "FN_partial_frames_outside_protocol": len(fnp_rows),
                    "FN_partial_regions_outside_protocol": len(
                        {(r["case_id"], r["region_index"]) for r in fnp_rows}
                    ),
                    "D_zero_det_block_regions": d_regions,
                },
                "frames": export_frame_rows,
            }
            args.export_frames.parent.mkdir(parents=True, exist_ok=True)
            args.export_frames.write_text(
                json.dumps(frames_payload, indent=1, ensure_ascii=False), encoding="utf-8"
            )
        if args.export_pairs is not None:
            covs = [p["coverage"] for p in export_pair_rows]
            pairs_payload = {
                "schema": "m2-doctr-qual/spot-audit-pairs@1",
                **export_meta,
                "n_pairs": len(export_pair_rows),
                "coverage_bucket_denominators": {
                    "C_pool_in_[0.5,0.7)": sum(1 for c in covs if 0.5 <= c < 0.7),
                    "ge_0.7": sum(1 for c in covs if c >= 0.7),
                    "lt_0.5": sum(1 for c in covs if c < 0.5),
                    "min": min(covs) if covs else None,
                    "max": max(covs) if covs else None,
                },
                "pairs": export_pair_rows,
            }
            args.export_pairs.parent.mkdir(parents=True, exist_ok=True)
            args.export_pairs.write_text(
                json.dumps(pairs_payload, indent=1, ensure_ascii=False), encoding="utf-8"
            )

    s = summary["block_coverage"]
    print(
        f"candidate={CANDIDATE['kind']} device={args.device} conf={args.conf_threshold} "
        f"regions={len(per_region)} elapsed={elapsed:.1f}s"
    )
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
        f"diag raw_strict (text-box granularity, NOT judged): recall={rs['recall']:.4f}"
    )
    print(
        f"bubble-class detections dropped (not a text box): {n_bubble_dropped_total}"
    )
    print(f"verdict all_pass={verdict['all_pass']}")
    print(f"results -> {args.out}")
    if args.export_frames is not None:
        print(f"frames export -> {args.export_frames} ({len(export_frame_rows)} rows)")
    if args.export_pairs is not None:
        print(f"pairs export -> {args.export_pairs} ({len(export_pair_rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
