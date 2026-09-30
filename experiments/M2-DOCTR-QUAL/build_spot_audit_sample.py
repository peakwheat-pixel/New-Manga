"""Build the frozen 6-layer spot-audit sample list (M2-DOCTR-QUAL-C1, AC2+AC3).

Inputs are the C1 spot-audit exports produced by ``eval_detection_manga.py
--export-frames/--export-pairs`` plus the rerun results JSON and the eval
manifest. The layer protocol, denominators and quotas are FROZEN in the C4
report section 7.2 (with the DSH r2 N3-corrected D denominator); this script
executes them verbatim and never invents sample content.

Frozen protocol (random seed ``20260930``, also frozen in the task file):

- A1 true-miss          : 6 GT boxes (regions with ``n_det_raw == 0``) - inspect all;
- A2 coverage shortfall : 2 regions (``tp_block_coverage == 0`` with
  detections present) - inspect all detections vs their GT;
- B1 FP in GT regions   : denominator 78 boxes / 49 regions -> sample 15,
  stratified proportionally over conf value-range deciles
  ([0.50,0.55) ... [0.95,1.00], largest-remainder quotas);
- B2 FP in GT-less regions: denominator 30 boxes / 23 regions -> sample 15,
  same stratification;
- C coverage-fit pairs  : ``block_coverage`` matched pairs with coverage in
  [0.5, 0.7) -> sample 20, or inspect ALL when the measured denominator is
  below 20 (fallback is part of the frozen protocol);
- D zero-detection calibration: the 78 ``n_det_block == 0`` regions
  (72 ``n_gt == 0`` + 6 A1) -> random 10 full-frame reviews.

Determinism contract: every pool is explicitly sorted, every layer draws
from its own ``random.Random(f"{SEED}/{layer}[...]")`` instance, and the
output payload carries NO timestamp, so same-seed regeneration is
byte-identical (validated by ``--self-check`` and by the committed run
evidence). Reproducibility is guaranteed for the same Python major version
(``random.Random(str)`` and ``random.sample`` are stable within a version).

The labeling worksheet is emitted with EMPTY verdict/rationale columns:
human labeling belongs to the user (phase 2). This script never fills them.

Preview crops (optional ``--previews-out``) are written OUTSIDE the repo
(gitignored task-env tree) because the source region images are copyrighted
material; the sample list references file names only.

Usage (from the worktree root):

  "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4-gpu-py312/Scripts/python.exe" \
      experiments/M2-DOCTR-QUAL/build_spot_audit_sample.py \
      --results verification/M2-DOCTR-QUAL/spot-audit/data/frames-rerun.json \
      --frames verification/M2-DOCTR-QUAL/spot-audit/data/frames-export.json \
      --pairs verification/M2-DOCTR-QUAL/spot-audit/data/pairs-export.json \
      --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
      --formal-results verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json \
      --out-dir verification/M2-DOCTR-QUAL/spot-audit \
      --previews-out "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C1/previews" \
      --self-check
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from pathlib import Path

#: Frozen random seed (task file + C4 report section 7.2 handover).
SEED = 20260930

#: Frozen quotas / denominators from the C4 report section 7.2 table.
B1_QUOTA = 15
B2_QUOTA = 15
C_QUOTA = 20
C_COV_LO, C_COV_HI = 0.5, 0.7
D_QUOTA = 10
EXPECTED = {
    "A1_frames": 6,
    "A2_regions": 2,
    "A2_det_frames_in_region": 4,
    "B1_frames": 78,
    "B1_regions": 49,
    "B2_frames": 30,
    "B2_regions": 23,
    "D_zero_det_block_regions": 78,
}
#: conf value-range deciles over the possible conf window at threshold 0.5.
DECILE_EDGES = [round(0.50 + 0.05 * i, 2) for i in range(11)]

WORKSHEET_COLUMNS = [
    "unit_id",
    "layer",
    "case_id",
    "region_index",
    "description",
    "preview_file",
    "verdict",
    "rationale",
]

DESCRIPTIONS = {
    "A1": "真未检出（region 无任何原始检测框）：判定该 GT 框是真实文字（→真实文字漏检）还是伪 GT 噪声/SFX/背景（→伪 GT 噪声）",
    "A2": "coverage 不达标（region 有检出框但 GT 未达 coverage 0.5）：检出框与 GT 的错位是粒度/边界问题（→粒度不达标）还是 GT 本身噪声（→伪 GT 噪声）",
    "B1": "有 GT region 的 FP：红框=待判定检出框；判定其落在真实但未标注的文字上（→盲区 FP）还是无文字处（→模型幻觉）；绿框=该 region 的 GT（上下文）",
    "B2": "无 GT region 的 FP：同 B1 语义（该层是纯盲区/幻觉判别的最干净样本）：落在真实但未标注文字上（→盲区 FP）还是无文字处（→模型幻觉）",
    "C": "贴合匹配对（coverage∈[0.5,0.7)）：判定真实文字被检出框正确覆盖（→真匹配）还是检出框仅擦边盖住 GT（→粒度不达标）",
    "D": "零检测 region 全帧复核：模型零输出与伪 GT 零标注是否一致；若帧内存在可见真实文字（未检出且未标注）即为 GT 盲区证据",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg: str) -> "SystemExit":
    return SystemExit(f"DENOMINATOR/PROTOCOL MISMATCH (fail-closed): {msg}")


def decile_of(conf: float) -> int:
    """Value-range decile index for a conf in [0.5, 1.0]."""
    idx = int((conf - 0.50) / 0.05)
    return max(0, min(9, idx))


def stratified_sample(rows: list[dict], quota: int, layer: str) -> tuple[list[dict], list[dict]]:
    """Conf-decile proportional sampling with largest-remainder quotas.

    Returns (selected_rows_sorted, per_decile_detail) — the detail list is
    the N7 stratification evidence committed with the sample list.
    """
    by_bin: dict[int, list[dict]] = {}
    for row in rows:
        by_bin.setdefault(decile_of(row["conf"]), []).append(row)
    for pool in by_bin.values():
        pool.sort(key=lambda r: (r["case_id"], r["region_index"], r["det_index"]))

    nonempty = sorted(b for b in by_bin)
    total = len(rows)
    if quota > total:
        raise fail(f"{layer}: quota {quota} exceeds denominator {total}")
    raw = {b: quota * len(by_bin[b]) / total for b in nonempty}
    quotas = {b: int(raw[b]) for b in nonempty}
    remainder = quota - sum(quotas.values())
    order = sorted(nonempty, key=lambda b: (-(raw[b] - quotas[b]), b))
    for b in order[:remainder]:
        quotas[b] += 1

    detail = []
    selected: list[dict] = []
    for b in nonempty:
        pool = by_bin[b]
        take = quotas.get(b, 0)
        if take == 0:
            detail.append(
                {
                    "decile": f"[{DECILE_EDGES[b]:.2f},{DECILE_EDGES[b + 1]:.2f})",
                    "denominator": len(pool),
                    "quota": 0,
                    "selected": [],
                }
            )
            continue
        rng = random.Random(f"{SEED}/{layer}/bin{b:02d}")
        picked = rng.sample(pool, take)
        detail.append(
            {
                "decile": (
                    f"[{DECILE_EDGES[b]:.2f},{DECILE_EDGES[b + 1]:.2f})"
                    if b < 9
                    else f"[{DECILE_EDGES[b]:.2f},{DECILE_EDGES[b + 1]:.2f}]"
                ),
                "denominator": len(pool),
                "quota": take,
                "selected": [r["box_key"] for r in picked],
            }
        )
        selected.extend(picked)
    selected.sort(key=lambda r: (r["case_id"], r["region_index"], r["det_index"]))
    return selected, detail


def build_payload(args: argparse.Namespace) -> dict:
    """Read inputs, fail-closed-verify denominators, sample all six layers."""
    results = json.loads(args.results.read_text(encoding="utf-8"))
    frames = json.loads(args.frames.read_text(encoding="utf-8"))
    pairs = json.loads(args.pairs.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    formal = json.loads(args.formal_results.read_text(encoding="utf-8"))

    # --- 3-source denominator cross-check (fail-closed) ------------------
    if results["per_region"] != formal["per_region"]:
        raise fail("rerun per_region differs from the C4 formal JSON")
    if results["summary"] != formal["summary"]:
        raise fail("rerun summary differs from the C4 formal JSON")
    if frames.get("manifest_sha256") != results.get("manifest_sha256"):
        raise fail("frames export manifest_sha256 differs from results JSON")
    if results.get("manifest_sha256") != sha256_file(args.manifest):
        raise fail("manifest sha256 mismatch: results JSON vs manifest file on disk")

    per_region = results["per_region"]
    meas = dict(frames["layer_denominators"])
    measured = {
        "A1_frames": meas["A1_frames"],
        "A2_regions": meas["A2_regions"],
        "A2_det_frames_in_region": meas["A2_det_frames_in_region"],
        "B1_frames": meas["B1_frames"],
        "B1_regions": meas["B1_regions"],
        "B2_frames": meas["B2_frames"],
        "B2_regions": meas["B2_regions"],
        "D_zero_det_block_regions": meas["D_zero_det_block_regions"],
    }
    for key, expected in EXPECTED.items():
        if measured[key] != expected:
            raise fail(
                f"{key}: C4 report section 7.2 expects {expected}, measured {measured[key]}"
            )

    rows = frames["frames"]
    a1_rows = sorted(
        (r for r in rows if r["layer"] == "A1"),
        key=lambda r: (r["case_id"], r["region_index"], r["gt_index"]),
    )
    b1_pool = [r for r in rows if r["kind"] == "fp_block" and r["layer"] == "B1"]
    b2_pool = [r for r in rows if r["kind"] == "fp_block" and r["layer"] == "B2"]
    for r in rows:
        r["box_key"] = (
            f"{r['case_id']}/R{r['region_index']:03d}"
            f"/{'det' if r['kind'] == 'fp_block' else 'gt'}#{r.get('det_index', r.get('gt_index'))}"
        )
    a2_regions = sorted(
        {
            (r["case_id"], r["region_index"])
            for r in rows
            if r["layer"] == "A2" or r.get("audit_layer_hint") == "A2"
        }
    )
    cov_pool = [
        p
        for p in pairs["pairs"]
        if C_COV_LO <= p["coverage"] < C_COV_HI
    ]
    cov_pool.sort(key=lambda p: (p["case_id"], p["region_index"], p["det_index"], p["gt_index"]))
    d_pool = sorted(
        (r["case_id"], r["region_index"])
        for r in per_region
        if r["n_det_block"] == 0
    )
    if len(d_pool) != EXPECTED["D_zero_det_block_regions"]:
        raise fail("D pool derived from per_region differs from frames denominator")

    # --- sampling ---------------------------------------------------------
    units: list[dict] = []
    b_strata: dict[str, list[dict]] = {}

    for i, r in enumerate(a1_rows, 1):
        units.append(
            {
                "unit_id": f"A1-U{i:02d}",
                "layer": "A1",
                "case_id": r["case_id"],
                "region_index": r["region_index"],
                "unit_kind": "gt_box",
                "review_box_xyxy": r["box_xyxy"],
                "gt_boxes_xyxy": [r["box_xyxy"]],
                "det_boxes_xyxy": [],
                "conf": None,
                "coverage": None,
                "note": "region n_det_raw=0：无红框，绿框=唯一 GT 框",
            }
        )

    for i, (case_id, region_index) in enumerate(a2_regions, 1):
        gt_boxes = [r["box_xyxy"] for r in rows if r["layer"] == "A2" and r["case_id"] == case_id and r["region_index"] == region_index]
        det_boxes = [
            r["box_xyxy"]
            for r in rows
            if r["kind"] == "fp_block" and r.get("audit_layer_hint") == "A2"
            and r["case_id"] == case_id and r["region_index"] == region_index
        ]
        units.append(
            {
                "unit_id": f"A2-U{i:02d}",
                "layer": "A2",
                "case_id": case_id,
                "region_index": region_index,
                "unit_kind": "region",
                "review_box_xyxy": None,
                "gt_boxes_xyxy": gt_boxes,
                "det_boxes_xyxy": det_boxes,
                "conf": None,
                "coverage": None,
                "note": f"region 全查：{len(det_boxes)} 个检出框（红）vs {len(gt_boxes)} 个 GT（绿）",
            }
        )

    for layer, pool, quota in (("B1", b1_pool, B1_QUOTA), ("B2", b2_pool, B2_QUOTA)):
        picked, detail = stratified_sample(pool, quota, layer)
        b_strata[layer] = detail
        # context: all GT boxes and all FP boxes per region for preview drawing
        gt_by_region: dict[tuple, list] = {}
        for r in rows:
            if r["kind"] == "gt_unmatched":
                gt_by_region.setdefault((r["case_id"], r["region_index"]), []).append(r["box_xyxy"])
        for i, r in enumerate(picked, 1):
            units.append(
                {
                    "unit_id": f"{layer}-U{i:02d}",
                    "layer": layer,
                    "case_id": r["case_id"],
                    "region_index": r["region_index"],
                    "unit_kind": "det_box",
                    "review_box_xyxy": r["box_xyxy"],
                    "gt_boxes_xyxy": gt_by_region.get((r["case_id"], r["region_index"]), []),
                    "det_boxes_xyxy": [r["box_xyxy"]],
                    "conf": r["conf"],
                    "coverage": None,
                    "note": (
                        f"conf={r['conf']:.4f}（十分位 "
                        f"{DECILE_EDGES[decile_of(r['conf'])]:.2f}-"
                        f"{DECILE_EDGES[decile_of(r['conf']) + 1]:.2f}）"
                        + ("；该框属 A2 region（K07 r109/K08 r3 框级重叠，A2 层另有 region 级判定单元）" if r.get("audit_layer_hint") == "A2" else "")
                    ),
                }
            )

    c_fallback = len(cov_pool) < C_QUOTA
    if c_fallback:
        c_picked = cov_pool
        c_detail = {
            "mode": "fallback_inspect_all",
            "denominator": len(cov_pool),
            "quota": C_QUOTA,
            "note": "实测分母 < 20，按冻结协议全查（协议内 fallback）",
        }
    else:
        rng = random.Random(f"{SEED}/C")
        c_picked = rng.sample(cov_pool, C_QUOTA)
        c_picked.sort(key=lambda p: (p["case_id"], p["region_index"], p["det_index"], p["gt_index"]))
        c_detail = {"mode": "random_sample", "denominator": len(cov_pool), "quota": C_QUOTA}
    for i, p in enumerate(c_picked, 1):
        units.append(
            {
                "unit_id": f"C-U{i:02d}",
                "layer": "C",
                "case_id": p["case_id"],
                "region_index": p["region_index"],
                "unit_kind": "pair",
                "review_box_xyxy": p["det_box_xyxy"],
                "gt_boxes_xyxy": [p["gt_box_xyxy"]],
                "det_boxes_xyxy": [p["det_box_xyxy"]],
                "conf": p["det_conf"],
                "coverage": p["coverage"],
                "note": f"matched pair coverage={p['coverage']:.4f}∈[0.5,0.7)：绿 GT vs 红 det",
            }
        )

    rng = random.Random(f"{SEED}/D")
    d_picked = rng.sample(d_pool, D_QUOTA)
    d_picked.sort()
    n_gt_by_region = {(r["case_id"], r["region_index"]): r["n_gt"] for r in per_region}
    for i, (case_id, region_index) in enumerate(d_picked, 1):
        units.append(
            {
                "unit_id": f"D-U{i:02d}",
                "layer": "D",
                "case_id": case_id,
                "region_index": region_index,
                "unit_kind": "region_full_frame",
                "review_box_xyxy": None,
                "gt_boxes_xyxy": [],
                "det_boxes_xyxy": [],
                "conf": None,
                "coverage": None,
                "note": f"零检测 region（n_det_block=0，n_gt={n_gt_by_region[(case_id, region_index)]}）全帧复核",
            }
        )

    units.sort(key=lambda u: (["A1", "A2", "B1", "B2", "C", "D"].index(u["layer"]), u["unit_id"]))
    for u in units:
        u["preview_file"] = f"{u['unit_id']}__{u['case_id']}_R{u['region_index']:03d}.png"
        u["description"] = DESCRIPTIONS[u["layer"]]

    manifest_sha = results["manifest_sha256"]
    weights_sha = results["candidate"]["weights_sha256"]
    # The recorded command covers the INPUT side only: the payload must be a
    # pure function of the inputs so same-seed regeneration is byte-identical
    # regardless of output directory or self-check mode (run-mode metadata
    # goes to stdout / run evidence, never into the payload).
    cmd = (
        "python experiments/M2-DOCTR-QUAL/build_spot_audit_sample.py "
        f"--results {args.results} --frames {args.frames} --pairs {args.pairs} "
        f"--manifest {args.manifest} --formal-results {args.formal_results} "
        "[--out-dir <spot-audit> --previews-out <external> --self-check]"
    )
    payload = {
        "schema": "m2-doctr-qual/spot-audit-sample@1",
        "task": "M2-DOCTR-QUAL-C1",
        "protocol": "C4 report section 7.2 (DSH r2 N3-corrected denominators), frozen 2026-09-30",
        "seed": SEED,
        "manifest": str(args.manifest),
        "manifest_sha256": manifest_sha,
        "weights_sha256": weights_sha,
        "conf_threshold": results["conf_threshold"],
        "inputs": {
            name: {"path": str(path), "sha256": sha256_file(path)}
            for name, path in (
                ("results", args.results),
                ("frames", args.frames),
                ("pairs", args.pairs),
                ("formal_results", args.formal_results),
            )
        },
        "generate_command": cmd,
        "denominator_audit": {
            "source_note": "3-source cross-check: rerun results JSON == C4 formal JSON (per_region+summary), frames-export layer_denominators, and the frozen section 7.2 numbers; all must agree or the script aborts",
            "expected_vs_measured": [
                {"layer": k, "expected": EXPECTED[k], "measured": measured[k], "match": True}
                for k in EXPECTED
            ],
            "C_layer": {
                "quota": C_QUOTA,
                "coverage_window": "[0.5,0.7)",
                "measured_pairs": len(cov_pool),
                "fallback_inspect_all_triggered": c_fallback,
                "total_matched_pairs_in_export": pairs["n_pairs"],
                "coverage_distribution": pairs["coverage_bucket_denominators"],
            },
            "FN_partial_outside_protocol": {
                "frames": meas["FN_partial_frames_outside_protocol"],
                "regions": meas["FN_partial_regions_outside_protocol"],
                "note": "未匹配 GT 框中不属于 A1/A2 的部分命中 region 残差；冻结 6 层协议不含该层，仅导出留证，不入清单",
            },
        },
        "b_layer_stratification_N7": {
            "decile_edges": DECILE_EDGES,
            "method": "conf value-range deciles, largest-remainder proportional quotas, per-decile seeded random",
            "B1": b_strata["B1"],
            "B2": b_strata["B2"],
        },
        "sampling_summary": {
            "A1": {"denominator": len(a1_rows), "sampled": len(a1_rows), "mode": "inspect_all"},
            "A2": {"denominator": len(a2_regions), "sampled": len(a2_regions), "mode": "inspect_all"},
            "B1": {"denominator": len(b1_pool), "sampled": B1_QUOTA, "mode": "stratified_random"},
            "B2": {"denominator": len(b2_pool), "sampled": B2_QUOTA, "mode": "stratified_random"},
            "C": {"denominator": len(cov_pool), "sampled": len(c_picked), "mode": c_detail["mode"]},
            "D": {"denominator": len(d_pool), "sampled": D_QUOTA, "mode": "random_sample"},
            "total_units": len(units),
        },
        "verdict_note": "判定列恒为空：人工判定属阶段二用户本人，agent 不预填（hard discipline）",
        "determinism_contract": "same seed + same inputs => byte-identical outputs; payload carries no timestamp and no run-mode metadata; validated by --self-check and by committed run evidence",
        "units": units,
    }
    return payload


def render_previews(payload: dict, results: dict, manifest_path: Path, out_dir: Path) -> int:
    """Draw one annotated crop per sampling unit into the EXTERNAL dir."""
    from PIL import Image, ImageDraw

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    images = {
        (r["case_id"], r["region_index"]): r["image"] for r in manifest["regions"]
    }
    per_region = {(r["case_id"], r["region_index"]): r for r in results["per_region"]}
    out_dir.mkdir(parents=True, exist_ok=True)
    GREEN, RED = (0, 200, 0), (230, 0, 0)
    written = 0
    for unit in payload["units"]:
        key = (unit["case_id"], unit["region_index"])
        img = Image.open(images[key]).convert("RGB")
        scale = 1.0
        if unit["layer"] == "D":
            scale = min(1.0, 1200.0 / max(img.size))
            if scale < 1.0:
                img = img.resize((int(img.width * scale), int(img.height * scale)))
        draw = ImageDraw.Draw(img)
        for gb in unit["gt_boxes_xyxy"]:
            draw.rectangle([c * scale for c in gb], outline=GREEN, width=2)
        for db in unit["det_boxes_xyxy"]:
            draw.rectangle([c * scale for c in db], outline=RED, width=3)
        label = f"{unit['unit_id']} | {unit['case_id']} R{unit['region_index']:03d}"
        if unit["coverage"] is not None:
            label += f" | coverage={unit['coverage']:.3f}"
        if unit["conf"] is not None:
            label += f" | conf={unit['conf']:.3f}"
        label += " | GREEN=GT RED=detection"
        bar_h = 20
        canvas = Image.new("RGB", (img.width, img.height + bar_h), (255, 255, 255))
        canvas.paste(img, (0, bar_h))
        d2 = ImageDraw.Draw(canvas)
        d2.text((4, 4), label, fill=(0, 0, 0))
        canvas.save(out_dir / unit["preview_file"], format="PNG")
        written += 1
    # fail-closed: every referenced preview must exist on disk
    missing = [u["preview_file"] for u in payload["units"] if not (out_dir / u["preview_file"]).is_file()]
    if missing:
        raise SystemExit(f"preview generation incomplete, missing: {missing}")
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True,
                        help="rerun results JSON (frames-rerun.json) — denominator source")
    parser.add_argument("--frames", type=Path, required=True,
                        help="frames export JSON (frames-export.json)")
    parser.add_argument("--pairs", type=Path, required=True,
                        help="matched-pairs export JSON (pairs-export.json)")
    parser.add_argument("--manifest", type=Path, required=True,
                        help="eval manifest (region image paths for previews)")
    parser.add_argument("--formal-results", type=Path, required=True,
                        help="C4 formal results JSON — frozen reference for the 3-source check")
    parser.add_argument("--out-dir", type=Path, required=True,
                        help="spot-audit output dir (sample CSV+JSON + worksheet)")
    parser.add_argument("--previews-out", type=Path, default=None,
                        help="OPTIONAL external (gitignored) dir for preview crops")
    parser.add_argument("--self-check", action="store_true",
                        help="rebuild the payload from disk a second time and "
                        "require byte-identical JSON before writing (same-seed "
                        "determinism evidence)")
    args = parser.parse_args()

    payload = build_payload(args)
    determinism = "not_run (--self-check absent)"
    if args.self_check:
        rebuilt = build_payload(args)
        a = json.dumps(payload, indent=1, ensure_ascii=False).encode("utf-8")
        b = json.dumps(rebuilt, indent=1, ensure_ascii=False).encode("utf-8")
        if a != b:
            raise SystemExit("SELF-CHECK FAILED: same-seed rebuild is not byte-identical")
        determinism = "pass: same-seed rebuild byte-identical"

    args.out_dir.mkdir(parents=True, exist_ok=True)
    sample_json = args.out_dir / "spot-audit-sample.json"
    sample_csv = args.out_dir / "spot-audit-sample.csv"
    worksheet = args.out_dir / "labeling-worksheet.csv"
    sample_json.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    with open(sample_csv, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow([
            "unit_id", "layer", "case_id", "region_index", "unit_kind",
            "conf", "coverage", "review_box_xyxy", "preview_file", "note",
        ])
        for u in payload["units"]:
            w.writerow([
                u["unit_id"], u["layer"], u["case_id"], u["region_index"], u["unit_kind"],
                "" if u["conf"] is None else f"{u['conf']:.4f}",
                "" if u["coverage"] is None else f"{u['coverage']:.4f}",
                json.dumps(u["review_box_xyxy"]) if u["review_box_xyxy"] else "",
                u["preview_file"], u["note"],
            ])
    # The labeling worksheet: verdict/rationale are written EMPTY and stay
    # empty until the user fills them in phase 2. Agent pre-filling is
    # forbidden by the task contract.
    with open(worksheet, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(WORKSHEET_COLUMNS)
        for u in payload["units"]:
            w.writerow([
                u["unit_id"], u["layer"], u["case_id"], u["region_index"],
                u["description"], u["preview_file"], "", "",
            ])

    previews_written = 0
    if args.previews_out is not None:
        results = json.loads(args.results.read_text(encoding="utf-8"))
        previews_written = render_previews(payload, results, args.manifest, args.previews_out)

    s = payload["sampling_summary"]
    print(f"sample list -> {sample_json}")
    print(f"sample csv  -> {sample_csv}")
    print(f"worksheet   -> {worksheet} (verdict/rationale EMPTY — user-only)")
    print(
        "units: "
        + " ".join(f"{k}={s[k]['sampled']}/{s[k]['denominator']}" for k in ("A1", "A2", "B1", "B2", "C", "D"))
        + f" total={s['total_units']}"
    )
    print(f"C fallback inspect-all triggered: {payload['denominator_audit']['C_layer']['fallback_inspect_all_triggered']}")
    print(f"determinism self-check: {determinism}")
    if args.previews_out is not None:
        print(f"previews -> {args.previews_out} ({previews_written} files, external gitignored path)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
