"""M2-DETECT-WEBTOON-DIAG adapter-level observability probe (AC1 + AC2).

ZERO src/tests changes: the production provider is imported and constructed
EXACTLY as the production assembly does (``bootstrap.core_assembly`` builds
``MangaDetectionProvider(weights_dir=..., device=...)``); every line of new
code for this diagnosis lives in this experiments directory. The probe is
directional evidence for the M2-TA3-B2 F1 root-cause ruling (ogkalu returns
0 candidates on webtoon long-strips) — it never mutates production code.

What it records, per page (AC1):

- the page size and its sha256 (cross-checked against the TA3-B
  case-selection manifest so the probe is provably the same pixels that
  produced the 0-candidate evidence);
- the production-path ``provider.detect`` result (region count, elapsed);
- raw observability that production never surfaces:
  * the image-processor rescale target (``preprocessor_config.json`` size
    and the actual ``pixel_values`` tensor shape fed to the model);
  * the raw logits shape and the FULL score distribution over all queries
    (max, top-k, and counts at 0.5 / 0.3 / 0.1 / 0.01 — production only ever
    sees the >= 0.5 slice via ``MANGA_CONF_THRESHOLD``);
  * class-wise counts (0=bubble / 1=text_bubble / 2=text_free).
- BJ02 (a normally-proportioned manga page) is the probe self-check: the
  probe must see detections there, or the probe itself is invalid.

Tile-level experiment (AC2), only if the full-page rescale hypothesis holds
(it is always run here and judged from the numbers): K01 is cut into
1024x1024 tiles with a 128 px (12.5%) vertical overlap (the webtoon width
690 < 1024 is right-padded with constant 114 gray to keep the model's square
input assumption), each tile runs the SAME production inference sequence,
and detections are mapped back to page coordinates (pad-region hits dropped)
and de-duplicated with a greedy confidence-ordered NMS. Tile detections
recovered on the page that scored 0 end-to-end are the direct feasibility
evidence for a tiling fix. Tiles are cropped in memory only — nothing is
written to disk and no pixels enter Git.

Probe schema v2 (DSH review r1 rework, R3a + R9): the tile experiment now
persists the FULL pre-NMS and post-NMS box coordinates plus every NMS
removal decision, and adds overlap-band (bottom 128 px of each non-final
tile) vs non-band detection-density / duplicate-pair statistics, so the
"226 -> 193, NMS removed overlap duplicates" claim is independently
recomputable from the JSON alone. The preprocessor keep-list also records
``shortest_edge`` so its absence is provable from the artifact. Counts are
at the PRE-MERGE text-box level (``cluster_words_into_blocks`` is not
applied in the tile path; production regions are post-merge blocks).

Run (main venv, CPU — the device is registered in the output JSON):

  "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
    experiments/M2-DETECT-WEBTOON-DIAG/diagnose_webtoon_detect.py \
    --output verification/M2-DETECT-WEBTOON-DIAG/probe-results.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

import numpy as np  # noqa: E402  (venv guarantees the torch stack)
from PIL import Image  # noqa: E402

from infrastructure.providers.detection_manga import (  # noqa: E402
    MANGA_CONF_THRESHOLD,
    MANGA_CONFIG_SHA256,
    MANGA_MODEL_SHA256,
    MANGA_PREPROCESSOR_SHA256,
    MangaDetectionProvider,
    sha256_file,
)
from ports.detection.ports import DetectionRequest  # noqa: E402

#: The TA3-B manifest that carries the exact page paths + sha256 pins of the
#: 0-candidate evidence (read-only reference; the probe never writes there).
CASE_SELECTION = (
    REPO_ROOT / "experiments" / "M2-TA3-B" / "case-selection.json"
)
PROBE_CASES = ("K01", "K02", "K04", "BJ02")
TILE_CASE = "K01"

#: The local pinned snapshot (sha256-verified against the production pins by
#: the provider loader itself — a mismatch is a typed PROVIDER_FAILED, so a
#: silently wrong snapshot can never reach the probe numbers).
DEFAULT_WEIGHTS_DIR = Path(
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights"
    "/ogkalu-comic-text-and-bubble-detector"
)

#: AC2 tile geometry: 1024x1024 squares (mandated by the task AC2), 128 px
#: vertical overlap — an EXPERIMENT-CHOSEN value (the task doc specifies no
#: overlap band); rationale: a multiple of the RT-DETR stride 32 and 12.5%
#: of the tile height. Webtoon width 690 < 1024 -> right/bottom padding with
#: constant 114 gray (a conventional detection padding constant, no upstream
#: citation; it carries no text by construction).
TILE_SIZE = 1024
TILE_OVERLAP = 128
TILE_PAD_VALUE = 114


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_page_rgb(path: Path) -> tuple[np.ndarray, str]:
    """Decode one page to an HxWx3 uint8 RGB array + its file sha256."""
    raw = path.read_bytes()
    digest = sha256_bytes(raw)
    with Image.open(path) as im:
        rgb = np.asarray(im.convert("RGB"))
    return rgb, digest


def production_detect(
    provider: MangaDetectionProvider, rgb: np.ndarray, page_id: str
) -> dict:
    """The production detect path, byte-for-byte the assembly construction.

    ``DetectionRequest`` takes raw pixels (rgb24) — exactly what the
    production handler hands over for a page frame.
    """
    height, width = int(rgb.shape[0]), int(rgb.shape[1])
    request = DetectionRequest(
        page_id=page_id,
        image_bytes=np.ascontiguousarray(rgb).tobytes(),
        width=width,
        height=height,
    )
    started = time.perf_counter()
    result = provider.detect(request)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    return {
        "region_count": len(result.candidates),
        "elapsed_ms": elapsed_ms,
        "provider_id": result.provider_id,
        "model": result.model,
        "conf_threshold": MANGA_CONF_THRESHOLD,
        "options": dict(result.options),
        "confidences": [
            float(c.confidence) for c in result.candidates if c.confidence is not None
        ],
    }


def raw_observability(
    model, processor, torch, rgb: np.ndarray
) -> dict:
    """Replay the production inference sequence and surface what production
    never records: the rescaled tensor, the raw logits, and the FULL score
    distribution below the production threshold."""
    height, width = int(rgb.shape[0]), int(rgb.shape[1])
    started = time.perf_counter()
    inputs = processor(images=rgb, return_tensors="pt")
    process_ms = int((time.perf_counter() - started) * 1000)
    pixel_shape = [int(v) for v in inputs["pixel_values"].shape]
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    infer_started = time.perf_counter()
    with torch.no_grad():
        outputs = model(**inputs)
    infer_ms = int((time.perf_counter() - infer_started) * 1000)
    logits_shape = [int(v) for v in outputs.logits.shape]
    n_queries = logits_shape[1]

    # FULL distribution, computed straight off the raw logits: sigmoid
    # (RT-DETR's focal-loss head) then the per-query best class over ALL
    # n_queries — the honest "what was actually there" numbers production
    # throws away at conf 0.5. (The transformers-5.17 processor signature
    # has no top-k knob; the manual reduction below is the equivalent full
    # distribution and is cross-checked against the official post_process
    # at the production threshold.)
    probs = torch.sigmoid(outputs.logits)[0]  # [n_queries, n_classes]
    best_scores, best_labels = probs.max(dim=-1)
    scores_all = [float(s) for s in best_scores.tolist()]
    labels_all = [int(l) for l in best_labels.tolist()]

    # Cross-check at the production threshold: the official post_process
    # must agree with the manual reduction's >= 0.5 count (same focal head).
    target_sizes = torch.tensor([[height, width]])
    results_prod = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=MANGA_CONF_THRESHOLD
    )[0]
    official_ge_05 = len(results_prod["scores"].tolist())

    def count_at(threshold: float) -> int:
        return sum(1 for s in scores_all if s >= threshold)

    class_wise: dict[str, dict] = {}
    for class_id in (0, 1, 2):
        cls_scores = [s for s, l in zip(scores_all, labels_all) if l == class_id]
        class_wise[str(class_id)] = {
            "count_ge_0_5": sum(1 for s in cls_scores if s >= 0.5),
            "count_ge_0_1": sum(1 for s in cls_scores if s >= 0.1),
            "max": max(cls_scores) if cls_scores else 0.0,
        }

    top10 = sorted(scores_all, reverse=True)[:10]
    return {
        "process_ms": process_ms,
        "infer_ms": infer_ms,
        "model_input_shape": pixel_shape,
        "logits_shape": logits_shape,
        "n_queries": n_queries,
        "score_max": max(scores_all) if scores_all else 0.0,
        "score_top10": top10,
        "counts_ge": {
            "0.5": count_at(0.5),
            "0.3": count_at(0.3),
            "0.1": count_at(0.1),
            "0.01": count_at(0.01),
            "0.0": count_at(0.0),
        },
        "official_post_process_ge_0_5": official_ge_05,
        "class_wise": class_wise,
    }


def _pad_tile(crop: np.ndarray) -> np.ndarray:
    """Right/bottom-pad a crop to TILE_SIZE x TILE_SIZE with constant gray."""
    tile = np.full(
        (TILE_SIZE, TILE_SIZE, 3), TILE_PAD_VALUE, dtype=np.uint8
    )
    h, w = crop.shape[:2]
    tile[:h, :w] = crop
    return tile


def run_tile_inference(model, processor, torch, tile_rgb: np.ndarray) -> list:
    """One production inference sequence on a tile; returns raw text-class
    boxes in tile-local coordinates (conf 0.5, the production threshold)."""
    inputs = processor(images=tile_rgb, return_tensors="pt")
    inputs = {key: value.to(model.device) for key, value in inputs.items()}
    with torch.no_grad():
        outputs = model(**inputs)
    target_sizes = torch.tensor(
        [[int(tile_rgb.shape[0]), int(tile_rgb.shape[1])]]
    )
    results = processor.post_process_object_detection(
        outputs, target_sizes=target_sizes, threshold=MANGA_CONF_THRESHOLD
    )[0]
    boxes = []
    for score, label, box in zip(
        results["scores"].tolist(),
        results["labels"].tolist(),
        results["boxes"].tolist(),
    ):
        if int(label) not in (1, 2):  # MANGA_TEXT_CLASSES, verbatim filter
            continue
        boxes.append(
            (float(box[0]), float(box[1]), float(box[2]), float(box[3]), float(score))
        )
    return boxes


def _iou(a: tuple, b: tuple) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def greedy_nms(boxes: list, iou_threshold: float = 0.5) -> tuple:
    """Confidence-ordered greedy NMS over page-global boxes (directional
    de-duplication of the overlap bands only — this is experiment-side
    accounting, never a production merge).

    Returns ``(kept_indices, removed)`` where ``removed`` records every
    removal decision as ``(removed_index, kept_index, iou)`` — with the full
    box coordinates persisted, the 226 -> 193 dedup is independently
    recomputable (DSH r1 R3a). Keep/drop semantics are unchanged from v1.
    """
    order = sorted(range(len(boxes)), key=lambda i: boxes[i][4], reverse=True)
    kept: list = []
    removed: list = []
    for i in order:
        best_keeper, best_iou = -1, 0.0
        for k in kept:
            iou = _iou(boxes[i], boxes[k])
            if iou > best_iou:
                best_keeper, best_iou = k, iou
        if best_keeper >= 0 and best_iou > iou_threshold:
            removed.append((i, best_keeper, best_iou))
        else:
            kept.append(i)
    return kept, removed


def overlap_band_stats(
    page_boxes: list, removed: list, bands: list, width: int, height: int
) -> dict:
    """DSH r1 R3a evidence: overlap-band vs non-band detection density and
    duplicate-pair accounting, so "NMS removed overlap duplicates" is a
    measured statement rather than an assertion.

    - a box belongs to the overlap band when its CENTER y falls inside one of
      the per-tile bottom bands (``[origin+step, origin+TILE_SIZE)`` of each
      non-final tile); bands are disjoint because step (896) > band (128);
    - duplicate pairs = pre-NMS box pairs with IoU > 0.5, split by whether
      the two boxes come from different tiles (true cross-tile duplication
      candidates) or the same tile;
    - removal accounting: how many NMS-removed boxes had their center in a
      band, how many were removed by a keeper from ANOTHER tile (the classic
      straddling-object duplicate), and the IoU distribution of removals.
    """

    def band_of(center_y: float) -> int:
        for bi, (b0, b1) in enumerate(bands):
            if b0 <= center_y < b1:
                return bi
        return -1

    box_band = [band_of((b[1] + b[3]) / 2.0) for b in page_boxes]
    band_area = sum(b1 - b0 for b0, b1 in bands) * width
    non_band_area = width * height - band_area
    n_in = sum(1 for b in box_band if b >= 0)
    n_out = len(page_boxes) - n_in

    pairs_total = pairs_cross = pairs_same = pairs_outside = 0
    n = len(page_boxes)
    for a in range(n):
        for b in range(a + 1, n):
            if _iou(page_boxes[a], page_boxes[b]) > 0.5:
                pairs_total += 1
                if page_boxes[a][5] != page_boxes[b][5]:
                    pairs_cross += 1
                else:
                    pairs_same += 1
                if box_band[a] < 0 and box_band[b] < 0:
                    pairs_outside += 1

    removed_ious = [r[2] for r in removed]
    return {
        "band_height_px": TILE_OVERLAP,
        "n_bands": len(bands),
        "band_y_ranges_px": "@@COMPACT:bands@@",
        "band_area_px2": band_area,
        "non_band_area_px2": non_band_area,
        "pre_nms_boxes_in_bands": n_in,
        "pre_nms_boxes_outside_bands": n_out,
        "pre_nms_density_per_mpx_in_bands": (
            round(n_in / band_area * 1e6, 2) if band_area else 0.0
        ),
        "pre_nms_density_per_mpx_outside": (
            round(n_out / non_band_area * 1e6, 2) if non_band_area else 0.0
        ),
        "duplicate_pairs_iou_gt_0_5_total": pairs_total,
        "duplicate_pairs_cross_tile": pairs_cross,
        "duplicate_pairs_same_tile": pairs_same,
        "duplicate_pairs_both_centers_outside_bands": pairs_outside,
        "nms_removed_total": len(removed),
        "nms_removed_center_in_band": sum(
            1 for r in removed if box_band[r[0]] >= 0
        ),
        "nms_removed_by_cross_tile_keeper": sum(
            1 for r in removed if page_boxes[r[0]][5] != page_boxes[r[1]][5]
        ),
        "nms_removed_iou_min": min(removed_ious) if removed_ious else 0.0,
        "nms_removed_iou_max": max(removed_ious) if removed_ious else 0.0,
        "nms_removed_iou_mean": (
            round(sum(removed_ious) / len(removed_ious), 4) if removed_ious else 0.0
        ),
    }


def tile_experiment(model, processor, torch, rgb: np.ndarray) -> dict:
    """AC2: cut the page into overlapping tiles, run the production
    sequence per tile, map detections back to page coordinates.

    Metric level (DSH r1 R2): the counts here are PRE-MERGE text-class boxes
    — the production ``cluster_words_into_blocks`` step is deliberately NOT
    applied in the tile path, so these numbers are not production region
    counts (post-merge blocks).
    """
    height, width = int(rgb.shape[0]), int(rgb.shape[1])
    step = TILE_SIZE - TILE_OVERLAP
    tiles: list[dict] = []
    page_boxes: list = []  # (x0, y0, x1, y1, score, tile_index), page coords
    bands: list = []  # (y0, y1) overlap band of each non-final tile
    started = time.perf_counter()
    tile_index = 0
    y = 0
    while y < height:
        y1 = min(y + TILE_SIZE, height)
        crop = rgb[y:y1]
        tile_rgb = _pad_tile(crop)
        tile_boxes = run_tile_inference(model, processor, torch, tile_rgb)
        mapped, dropped_in_pad = [], 0
        for x0, y0, x1, y1b, score in tile_boxes:
            page_box = (x0, y0 + y, x1, y1b + y, score, tile_index)
            center_x = (page_box[0] + page_box[2]) / 2.0
            if center_x > width:  # center in the right pad band: not page content
                dropped_in_pad += 1
                continue
            mapped.append(page_box)
        page_boxes.extend(mapped)
        tiles.append(
            {
                "tile_index": tile_index,
                "origin_y": y,
                "crop_h": int(y1 - y),
                "n_boxes_raw": len(tile_boxes),
                "n_boxes_mapped": len(mapped),
                "n_dropped_center_in_pad": dropped_in_pad,
                "confidences": [round(b[4], 4) for b in mapped],
            }
        )
        if y1 < height:  # non-final tile: its bottom band overlaps the next tile
            bands.append((y + step, y + TILE_SIZE))
        tile_index += 1
        if y1 >= height:
            break
        y += step
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    kept_indices, removed = greedy_nms(page_boxes)
    deduped = [page_boxes[i] for i in kept_indices]
    confs = [b[4] for b in deduped]
    widths = [b[2] - b[0] for b in deduped]
    heights = [b[3] - b[1] for b in deduped]
    ys = [b[1] for b in deduped]
    stats = overlap_band_stats(page_boxes, removed, bands, width, height)

    _COMPACT_BLOCKS.clear()
    _COMPACT_BLOCKS["pre_nms_boxes"] = (
        [
            [round(b[0], 1), round(b[1], 1), round(b[2], 1), round(b[3], 1),
             round(b[4], 4), int(b[5])]
            for b in page_boxes
        ],
        10,
        8,
    )
    _COMPACT_BLOCKS["post_nms_boxes"] = (
        [
            [round(b[0], 1), round(b[1], 1), round(b[2], 1), round(b[3], 1),
             round(b[4], 4), int(b[5])]
            for b in (page_boxes[i] for i in sorted(kept_indices))
        ],
        10,
        8,
    )
    _COMPACT_BLOCKS["nms_removed"] = (
        [[int(r[0]), int(r[1]), round(r[2], 4)] for r in removed],
        10,
        8,
    )
    _COMPACT_BLOCKS["bands"] = (
        [[int(b0), int(b1)] for b0, b1 in bands],
        12,
        10,
    )
    return {
        "metric_level": "pre-merge text-class boxes (cluster_words_into_blocks NOT applied; production regions are post-merge blocks)",
        "tile_size": TILE_SIZE,
        "overlap_px": TILE_OVERLAP,
        "n_tiles": len(tiles),
        "elapsed_ms": elapsed_ms,
        "total_raw_detections": sum(t["n_boxes_raw"] for t in tiles),
        "total_mapped_detections": len(page_boxes),
        "deduped_detections": len(deduped),
        "deduped_conf": {
            "max": max(confs) if confs else 0.0,
            "mean": round(sum(confs) / len(confs), 4) if confs else 0.0,
            "min": min(confs) if confs else 0.0,
        },
        "deduped_geometry_px": {
            "median_box_w": round(sorted(widths)[len(widths) // 2], 1) if widths else 0.0,
            "median_box_h": round(sorted(heights)[len(heights) // 2], 1) if heights else 0.0,
            "y_range": [round(min(ys), 1), round(max(ys), 1)] if ys else [0.0, 0.0],
        },
        "tiles": tiles,
        "overlap_band_stats": stats,
        # Full coordinates (v2, DSH r1 R3a): format per row is
        # [x0, y0, x1, y1, score, tile_index] in page pixels; nms_removed rows
        # are [removed_index, kept_index, iou] indexing into pre_nms_boxes.
        "pre_nms_boxes": "@@COMPACT:pre_nms_boxes@@",
        "post_nms_boxes": "@@COMPACT:post_nms_boxes@@",
        "nms_removed": "@@COMPACT:nms_removed@@",
    }


#: Large box-coordinate blocks are persisted one-box-per-line (compact JSON)
#: so the artifact stays reviewable; these placeholders are rendered by
#: ``dump_report`` at write time (DSH r1 R3a). Values are
#: ``(rows, element_indent, close_indent)`` to match the json indent=2 depth
#: each block sits at.
_COMPACT_BLOCKS: dict[str, tuple] = {}


def _render_compact(rows: list, elem_indent: int, close_indent: int) -> str:
    if not rows:
        return "[]"
    pad = " " * elem_indent
    body = ",\n".join(pad + json.dumps(row) for row in rows)
    return "[\n" + body + "\n" + " " * close_indent + "]"


def dump_report(report: dict, output_path: Path) -> None:
    text = json.dumps(report, indent=2, ensure_ascii=False)
    for name, (rows, elem_indent, close_indent) in _COMPACT_BLOCKS.items():
        marker = f'"@@COMPACT:{name}@@"'
        if marker not in text:
            raise ValueError(f"compact block {name} has no placeholder in report")
        text = text.replace(
            marker, _render_compact(rows, elem_indent, close_indent)
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(text + "\n", encoding="utf-8")


def load_preprocessor_config(weights_dir: Path) -> dict:
    config = json.loads((weights_dir / "preprocessor_config.json").read_text("utf-8"))
    keep = (
        "image_processor_type",
        "size",
        "shortest_edge",
        "do_resize",
        "do_rescale",
        "do_normalize",
        "do_pad",
        "resample",
        "rescale_factor",
        "image_mean",
        "image_std",
        "pad_size",
    )
    return {key: config.get(key) for key in keep if key in config}


def verify_weights(weights_dir: Path) -> dict:
    pins = {
        "model.safetensors": MANGA_MODEL_SHA256,
        "config.json": MANGA_CONFIG_SHA256,
        "preprocessor_config.json": MANGA_PREPROCESSOR_SHA256,
    }
    files = {}
    for filename, pin in pins.items():
        actual = sha256_file(weights_dir / filename)
        files[filename] = {"sha256": actual, "pin_match": actual == pin}
    return {
        "dir": str(weights_dir),
        "all_pins_match": all(f["pin_match"] for f in files.values()),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--weights-dir",
        default=os.environ.get("NEWMANGA_DETECTOR_WEIGHTS", str(DEFAULT_WEIGHTS_DIR)),
        help="pinned ogkalu snapshot directory (env NEWMANGA_DETECTOR_WEIGHTS)",
    )
    parser.add_argument("--device", default="cpu", help="cpu (GPU optional)")
    parser.add_argument(
        "--output",
        default=str(
            REPO_ROOT
            / "verification" / "M2-DETECT-WEBTOON-DIAG" / "probe-results.json"
        ),
    )
    args = parser.parse_args()

    weights_dir = Path(args.weights_dir)
    if not weights_dir.is_dir():
        print(f"FATAL: weights dir missing: {weights_dir}", file=sys.stderr)
        return 2

    import torch

    print(f"[probe] torch {torch.__version__} device={args.device}", flush=True)
    weights_report = verify_weights(weights_dir)
    if not weights_report["all_pins_match"]:
        print("FATAL: weights sha256 pin mismatch — refusing to probe "
              "unverified weights (production fail-closed semantics).",
              file=sys.stderr)
        return 2

    # Production construction, verbatim (bootstrap.core_assembly):
    # MangaDetectionProvider(weights_dir=..., device=...) — the engine load
    # re-enforces the three-file pins itself (defence in depth).
    provider = MangaDetectionProvider(weights_dir=weights_dir, device=args.device)
    model, processor = provider._engine_or_raise()
    preprocessor_config = load_preprocessor_config(weights_dir)
    print(f"[probe] weights OK: {weights_dir}", flush=True)
    print(f"[probe] preprocessor: {json.dumps(preprocessor_config)}", flush=True)

    selection = json.loads(CASE_SELECTION.read_text("utf-8"))
    cases = {c["case_id"]: c for c in selection["cases"]}

    report: dict = {
        "task": "M2-DETECT-WEBTOON-DIAG",
        "probe_schema_version": 2,
        "r1_revision": {
            "rerun_reason": (
                "DSH review r1 R3(a): persist full pre/post-NMS box coordinates "
                "plus NMS removal decisions and overlap-band duplicate statistics "
                "so '226 -> 193, NMS removed overlap duplicates' is independently "
                "recomputable; R9: shortest_edge added to the preprocessor "
                "keep-whitelist (absence of the key below proves absence in the "
                "config file)."
            ),
            "previous_json": (
                "schema v1 @ git b311f52f "
                "(verification/M2-DETECT-WEBTOON-DIAG/probe-results.json, "
                "generated_at_utc=2026-10-01T11:43:32Z)"
            ),
            "schema_delta": [
                "tile_experiment: full pre_nms_boxes / post_nms_boxes / "
                "nms_removed / overlap_band_stats (deduped_boxes_sample(40) "
                "replaced by the full post_nms_boxes)",
                "preprocessor keep-whitelist now records shortest_edge",
            ],
        },
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "device": args.device,
            "transformers": __import__("transformers").__version__,
            "numpy": np.__version__,
        },
        "weights": weights_report,
        "preprocessor_config": preprocessor_config,
        "conf_threshold_production": MANGA_CONF_THRESHOLD,
        "case_selection_manifest": str(CASE_SELECTION),
        "pages": {},
    }

    for case_id in PROBE_CASES:
        case = cases[case_id]
        page_path = Path(case["page_path"])
        print(f"[probe] {case_id}: {page_path}", flush=True)
        rgb, digest = load_page_rgb(page_path)
        sha_match = digest == case["page_sha256"]
        print(
            f"[probe]   size={rgb.shape[1]}x{rgb.shape[0]} "
            f"sha256_match={sha_match}",
            flush=True,
        )
        page_report = {
            "source_path": str(page_path),
            "source_sha256": digest,
            "source_sha256_matches_manifest": sha_match,
            "size_wh": [int(rgb.shape[1]), int(rgb.shape[0])],
            "layout_type": case["layout_type"],
            "tags": case["tags"],
        }
        if not sha_match:
            page_report["skipped_reason"] = "sha256 mismatch vs manifest"
            report["pages"][case_id] = page_report
            continue
        page_report["provider_detect"] = production_detect(
            provider, rgb, page_id=case_id
        )
        page_report["raw_observability"] = raw_observability(
            model, processor, torch, rgb
        )
        print(
            f"[probe]   provider regions={page_report['provider_detect']['region_count']} "
            f"raw max_conf={page_report['raw_observability']['score_max']:.4f} "
            f"counts_ge={page_report['raw_observability']['counts_ge']}",
            flush=True,
        )
        if case_id == TILE_CASE:
            print(f"[probe]   tile experiment ({TILE_SIZE}px, overlap {TILE_OVERLAP}px)...",
                  flush=True)
            page_report["tile_experiment"] = tile_experiment(
                model, processor, torch, rgb
            )
            tile_report = page_report["tile_experiment"]
            print(
                f"[probe]   tiles={tile_report['n_tiles']} "
                f"raw_dets={tile_report['total_raw_detections']} "
                f"deduped={tile_report['deduped_detections']} "
                f"max_conf={tile_report['deduped_conf']['max']}",
                flush=True,
            )
        report["pages"][case_id] = page_report

    output_path = Path(args.output)
    dump_report(report, output_path)
    print(f"[probe] wrote {output_path}", flush=True)

    # Probe self-check (AC1): the normally-proportioned control page must
    # produce detections, or the probe itself is invalid.
    bj02 = report["pages"].get("BJ02", {})
    control_ok = bj02.get("provider_detect", {}).get("region_count", 0) > 0
    print(
        f"[probe] control BJ02 regions="
        f"{bj02.get('provider_detect', {}).get('region_count', 'n/a')} "
        f"-> probe {'VALID' if control_ok else 'INVALID'}",
        flush=True,
    )
    return 0 if control_ok else 3


if __name__ == "__main__":
    sys.exit(main())
