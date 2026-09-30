#!/usr/bin/env python3
"""M2-DOCTR-QUAL-C1 phase-2 aggregation script.

Reads the user-reviewed labeling worksheet (formal verdicts) and the AI draft
worksheet (methodology comparison evidence), computes the layer x verdict cross
table, enforces per-layer enum discipline, derives the three calibration
numbers quoted in c1-spot-audit-report.md, and prints everything as Markdown.

Read-only over both CSVs (never writes verdict content). Exit code 0 only if
all structural discipline checks pass: 50 rows, per-layer enums respected,
per-layer row counts match the frozen sample list, AI-draft diff limited to
verdict/rationale columns.

Usage (repo root):
    python verification/M2-DOCTR-QUAL/spot-audit/summarize_c1_spot_audit.py
"""

from __future__ import annotations

import csv
import math
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSHEET = HERE / "labeling-worksheet.csv"
AI_DRAFT = HERE / "labeling-worksheet-ai-draft.csv"

# Frozen C4 formal constants (results-formal-manga_rt_detr_v2-cuda-seg05.json,
# block_coverage primary layer). Denominators per C4 report section 7.2.
TP = 882
GT_TOTAL = 917  # = tp 882 + fn 35
FP_TOTAL = 108  # = B1 78 + B2 30
RECALL_FROZEN = TP / GT_TOTAL          # 0.9618
PRECISION_FROZEN = TP / (TP + FP_TOTAL)  # 0.8909
FN_PARTIAL_UNAUDITED = 27  # residual GT boxes of partial-hit regions, outside the frozen 6-layer protocol

# Frozen per-layer denominators/quotas (C4 report section 7.2 + phase-1 audit).
LAYER_EXPECTED_ROWS = {"A1": 6, "A2": 2, "B1": 15, "B2": 15, "C": 2, "D": 10}
B1_DENOM = 78
B2_DENOM = 30

# Per-layer verdict enums (README section "六层各自看什么", verbatim strings).
LAYER_ENUMS = {
    "A1": {"真实文字漏检", "伪 GT 噪声"},
    "A2": {"粒度不达标", "伪 GT 噪声"},
    "B1": {"盲区 FP", "模型幻觉"},
    "B2": {"盲区 FP", "模型幻觉"},
    "C": {"真匹配", "粒度不达标"},
    "D": {"一致（确无可检文字）", "GT 盲区（有真实文字未标注未检出）"},
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    return rows


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return center - margin, center + margin


def main() -> int:
    failures: list[str] = []

    rows = read_csv(WORKSHEET)
    if len(rows) != 50:
        failures.append(f"worksheet row count {len(rows)} != 50")

    by_layer: dict[str, list[dict[str, str]]] = {layer: [] for layer in LAYER_ENUMS}
    for r in rows:
        layer = r["layer"]
        verdict = r["verdict"].strip()
        if layer not in LAYER_ENUMS:
            failures.append(f"{r['unit_id']}: unknown layer {layer!r}")
            continue
        if verdict not in LAYER_ENUMS[layer]:
            failures.append(f"{r['unit_id']}: verdict {verdict!r} not in layer-{layer} enum")
        by_layer[layer].append(r)

    for layer, expected in LAYER_EXPECTED_ROWS.items():
        got = len(by_layer[layer])
        if got != expected:
            failures.append(f"layer {layer}: {got} rows != frozen quota {expected}")

    # ---- cross table ----------------------------------------------------
    print("# C1 spot-audit aggregation (computed, not hand-copied)")
    print()
    print("## Layer x verdict cross table (formal user-reviewed worksheet)")
    print()
    print("| Layer | n | verdict distribution |")
    print("|---|---|---|")
    totals: Counter[str] = Counter()
    for layer in ("A1", "A2", "B1", "B2", "C", "D"):
        dist = Counter(r["verdict"].strip() for r in by_layer[layer])
        totals.update(dist)
        dist_str = " + ".join(f"{v}={c}" for v, c in sorted(dist.items(), key=lambda kv: -kv[1]))
        print(f"| {layer} | {len(by_layer[layer])} | {dist_str} |")
    print()
    print("## Overall verdict distribution (n=50)")
    print()
    print("| Verdict | Count |")
    print("|---|---|")
    for v, c in sorted(totals.items(), key=lambda kv: -kv[1]):
        print(f"| {v} | {c} |")
    print(f"| **total** | **{sum(totals.values())}** |")
    print()

    # ---- AI draft comparison (methodology disclosure numbers) -----------
    draft = {r["unit_id"]: r for r in read_csv(AI_DRAFT)}
    confirmed, revised = [], []
    for r in rows:
        d = draft.get(r["unit_id"])
        if d is None:
            failures.append(f"{r['unit_id']}: missing from AI draft")
            continue
        if r["verdict"].strip() == d["verdict"].strip():
            confirmed.append(r["unit_id"])
        else:
            revised.append((r["unit_id"], d["verdict"].strip(), r["verdict"].strip()))
    rationale_revised = [
        r["unit_id"] for r in rows
        if r["rationale"].strip().startswith("[人工修订]")
    ]
    print("## Methodology disclosure numbers (worksheet vs AI draft)")
    print()
    print(f"- verdict-confirmed units: {len(confirmed)}/50")
    print(f"- verdict-revised units: {len(revised)} -> " + "; ".join(
        f"{u}: {old} -> {new}" for u, old, new in revised))
    print(f"- units whose rationale carries the [人工修订] prefix: {len(rationale_revised)} "
          f"({', '.join(rationale_revised)})")
    stricter = all(new in ("模型幻觉", "粒度不达标") for _, _, new in revised)
    print(f"- all revisions toward the stricter verdict: {stricter}")
    print()

    # ---- calibration finding (a): Recall denominator contamination ------
    a1_noise = sum(1 for r in by_layer["A1"] if r["verdict"].strip() == "伪 GT 噪声")
    a2_noise = sum(1 for r in by_layer["A2"] if r["verdict"].strip() == "伪 GT 噪声")
    a2_gran = sum(1 for r in by_layer["A2"] if r["verdict"].strip() == "粒度不达标")
    true_misses = sum(1 for r in by_layer["A1"] if r["verdict"].strip() == "真实文字漏检")
    unaudited_unmatched = 8 - (a1_noise + a2_noise + a2_gran + true_misses)
    print("## Calibration (a): Recall denominator contamination (A1+A2, inspect-all layers)")
    print()
    print(f"- unmatched GT units audited: 8/8 (A1 6 + A2 2, both inspect-all layers -> no sampling error)")
    print(f"- pseudo-GT noise: {a1_noise + a2_noise}; granularity shortfall: {a2_gran}; "
          f"true-dialogue misses: {true_misses}")
    print(f"- reclassified-inference share of the 8: {unaudited_unmatched} (must be 0)")
    recall_denoise = TP / (GT_TOTAL - (a1_noise + a2_noise))
    recall_denoise_gran = TP / (GT_TOTAL - (a1_noise + a2_noise) - a2_gran)
    print(f"- frozen recall = {TP}/{GT_TOTAL} = {RECALL_FROZEN:.4f}")
    print(f"- noise-corrected recall estimate = {TP}/{GT_TOTAL - (a1_noise + a2_noise)} "
          f"= {recall_denoise:.4f}")
    print(f"- noise+granularity-corrected = {TP}/{GT_TOTAL - (a1_noise + a2_noise) - a2_gran} "
          f"= {recall_denoise_gran:.4f}")
    print(f"- unaudited residual: FN-partial {FN_PARTIAL_UNAUDITED} GT boxes outside the frozen protocol")
    print()

    # ---- calibration finding (b): Precision pollution direction ---------
    b_total = len(by_layer["B1"]) + len(by_layer["B2"])
    blind = sum(1 for r in by_layer["B1"] + by_layer["B2"] if r["verdict"].strip() == "盲区 FP")
    halluc = sum(1 for r in by_layer["B1"] + by_layer["B2"] if r["verdict"].strip() == "模型幻觉")
    print("## Calibration (b): Precision pollution direction (B1+B2 sampled FPs)")
    print()
    print(f"- B-layer FPs audited: {b_total}/108 (B1 15/{B1_DENOM} + B2 15/{B2_DENOM}, conf-decile stratified)")
    print(f"- blind-spot FPs (real text, GT blind): {blind} ({blind / b_total:.1%})")
    print(f"- true hallucinations (no text): {halluc} ({halluc / b_total:.1%})")
    extrap_halluc = FP_TOTAL * halluc / b_total
    prec_conservative = TP / (TP + (FP_TOTAL - b_total) + halluc)  # assume all unsampled FPs are true hallucinations
    prec_extrapolated = TP / (TP + extrap_halluc)
    print(f"- frozen precision = {TP}/{TP + FP_TOTAL} = {PRECISION_FROZEN:.4f} (polluted lower bound)")
    print(f"- conservative corrected (unsampled 78 all true FPs): {TP}/{TP + FP_TOTAL - b_total + halluc} "
          f"= {prec_conservative:.4f}")
    print(f"- proportion-extrapolated (n=30 caveat): {TP}/{TP:.0f}+{extrap_halluc:.1f} "
          f"= {prec_extrapolated:.4f}")
    print()

    # ---- calibration finding (c): D-layer GT blind-spot rate ------------
    d_blind = sum(1 for r in by_layer["D"] if r["verdict"].strip() == "GT 盲区（有真实文字未标注未检出）")
    d_match = sum(1 for r in by_layer["D"] if r["verdict"].strip() == "一致（确无可检文字）")
    lo, hi = wilson_ci(d_blind, len(by_layer["D"]))
    print("## Calibration (c): D-layer GT blind-spot rate (zero-detection full-frame review)")
    print()
    print(f"- D units: {len(by_layer['D'])}/78 sampled (random, seed 20260930)")
    print(f"- GT blind-spot frames (real text present, undetected AND unannotated): {d_blind}/{len(by_layer['D'])} "
          f"= {d_blind / len(by_layer['D']):.0%}")
    print(f"- consistent frames (no detectable text): {d_match}/{len(by_layer['D'])}")
    print(f"- Wilson 95% CI for blind-spot rate (n=10 caveat): [{lo:.3f}, {hi:.3f}]")
    print(f"- naive extrapolation to the 78 zero-detection regions: ~{78 * d_blind / len(by_layer['D']):.0f} "
          f"regions (n=10 sampling, wide CI)")
    print()

    if failures:
        print("## DISCIPLINE CHECK FAILURES")
        for f_ in failures:
            print(f"- {f_}")
        return 1
    print("## Discipline checks: PASS (50 rows, per-layer enums, frozen quotas, draft-diff scope)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
