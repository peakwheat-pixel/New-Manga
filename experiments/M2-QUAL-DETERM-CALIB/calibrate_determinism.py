"""M2-QUAL-DETERM-CALIB: reading_order-aligned translation-similarity calibration (F5).

Calibrates the redefined determinism gate adopted by user ruling 2026-10-01
(all four proceed): "export hash bitwise equality" is superseded for remote
translation chains; the new gate measures TRANSLATION STABILITY as the
distribution of per-region text similarity between two independent runs of
the same input, aligned by reading_order (methodological fact registered by
M2-TA3-B2 r1 R1: region_id is regenerated every run).

Inputs (READ-ONLY, produced by M2-TA3-B2 run_qualification.py):
  - verification/M2-TA3-B/phase2/summaries/qual-K11.json      (+ .rerun.json)
  - verification/M2-TA3-B/phase2/summaries/qual-BJ02.json     (+ .rerun.json)
  Region translations come from each summary's translate_details[] joined to
  regions[] via region_id -> reading_order.

What this script does (standard library only, no new dependencies):
  1. Aligns the two runs' region translations by reading_order, one pair
     per region; reports both "first" (qual-<case>.json, Run2-after DB text)
     and "second" (qual-<case>.rerun.json).
  2. Computes per-pair normalized similarity = 1 - Levenshtein/max_len
     (character level; stdlib implementation replicated from
     experiments/M2-TA3-B/measure_cer.py) under TWO scalings:
       - raw         : the translated_text strings verbatim (this reproduces
                       the quality-report F5 observation "7/11 non-empty
                       pairs float" for K11);
       - normalized  : quality-thresholds.md §0 normalization (strip ALL
                       whitespace incl. newlines/full-width spaces, …≡...,
                       latin casefold) — same normalization the project
                       already uses for CER, so line-break/spacing-level
                       rendering differences do not count as translation
                       instability.
  3. Empty-translation pair rule (registered, not improvised):
       - both sides empty  -> similarity 1.0 (status empty_both; two runs
         agree that the region has no translation — behaviour matches);
       - one side empty    -> similarity 0.0 (status empty_one_side; a
         run-level behaviour change, maximally unstable). Does not occur in
         the calibration data but the rule is part of the gate definition.
  4. Distribution per case and aggregate: per-pair list, identical/variant
     counts, min/median/P10, on both scalings, over all pairs and over the
     non-empty subset (the quality-report's 7/11 denominator).
  5. Gate threshold evaluation with synthetic contrast probes: the observed
     run-pair distribution must PASS the proposed gate while synthetic
     character-level corruptions of the observed translations (drift
     proxies, deterministic seeded perturbations) must FAIL, demonstrating
     discriminative power without inventing FAIL evidence.
  6. Emits machine-readable verification/M2-QUAL-DETERM-CALIB/calibration.json
     and the human report calibration.md.

Semantic boundary (binding wording for AC2/AC3): this gate measures
TRANSLATION STABILITY under re-run with a stochastic remote provider.  It is
NOT a render/export reproducibility metric.  The "export bytes bitwise
equal" criterion remains valid and enforced for mock/deterministic provider
chains (BJ02 Run1 page-render bitwise equality stays the upper-bound
reference).  K11's export hash mismatch has its root cause in the Run1 stage
(never isolated layer-by-layer) and is OUT OF SCOPE here — this task
calibrates the translation-stability metric only.

All numbers are DIRECTIONAL (n=2 calibration cases from the first quality
run; no production conclusions may be drawn from them).
"""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SUMMARIES_DIR = REPO_ROOT / "verification" / "M2-TA3-B" / "phase2" / "summaries"
OUT_DIR = REPO_ROOT / "verification" / "M2-QUAL-DETERM-CALIB"

#: The only two M2-TA3-B2 cases that have a run+rerun summary pair with
#: non-trivial region translations (K01 has region_count=0 on both sides).
CALIBRATION_CASES = ["K11", "BJ02"]

#: Proposed gate (AC2), anchored on the measured distribution — see
#: threshold_evaluation() and calibration.md for the reasoning.
PROPOSED_GATE = {"metric": "similarity_normalized", "median_min": 0.95, "min_min": 0.70}

#: Seeded substitution pool for synthetic drift probes (deterministic).
SUB_POOL = "嗎克啊乐欧课咯"
SYNTHETIC_SEED = 20261001

DIRECTIONAL_DISCLAIMER = (
    "directional evidence only: n=2 calibration cases from the first quality "
    "run (M2-TA3-B2), remote DeepSeek provider, 2026-10-01; not a production "
    "determinism conclusion"
)


# ---------------------------------------------------------------------------
# text metric — stdlib, replicated from experiments/M2-TA3-B/measure_cer.py
# (kept local on purpose: experiment dirs are independent deliverables and
# M2-TA3-B is outside this task's allowed modification surface)
# ---------------------------------------------------------------------------


def normalize(text: str) -> str:
    """quality-thresholds §0 normalization (identical to measure_cer.py)."""
    if not text:
        return ""
    text = text.replace("…", "...").replace("\u22ef", "...")
    text = "".join(text.split())  # strips ALL whitespace incl. \n and \u3000
    return text.casefold()


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def similarity(a: str, b: str) -> float:
    """1 - Levenshtein/max_len at character level.

    Empty-pair rule (registered gate definition, see module docstring):
    both empty -> 1.0; exactly one empty -> 0.0.
    """
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


# ---------------------------------------------------------------------------
# alignment
# ---------------------------------------------------------------------------


def translations_by_reading_order(summary: dict) -> dict[int, dict]:
    """Join translate_details to regions via region_id -> reading_order.

    Each entry carries the run's own bbox for that reading_order so the
    caller can cross-check geometric identity between the two runs
    (dsh r1 R1: reading_order stability across runs is an *assumption* —
    the key-set equality check alone cannot detect a permutation).
    """
    order = {r["region_id"]: r["reading_order"] for r in summary["regions"]}
    types = {r["region_id"]: r.get("region_type", "") for r in summary["regions"]}
    bboxes = {r["region_id"]: r.get("bbox") for r in summary["regions"]}
    out: dict[int, dict] = {}
    for detail in summary.get("translate_details", []):
        rid = detail["region_id"]
        if rid not in order:
            # r1 R7: a translate_detail pointing outside regions[] is a
            # summary inconsistency — fail-closed with the FATAL channel,
            # never a bare KeyError traceback.
            raise SystemExit(
                f"FATAL: translate_detail region_id {rid!r} not present in "
                "regions[] — summary is internally inconsistent"
            )
        ro = order[rid]
        out[ro] = {
            "reading_order": ro,
            "region_type": detail.get("region_type", "") or types[rid],
            "source_text": detail.get("source_text", "") or "",
            "translated_text": detail.get("translated_text", "") or "",
            "bbox": bboxes.get(rid),
        }
    return out


def pair_status(first: str, second: str) -> str:
    # r1 R6: emptiness basis unified with the similarity() empty-pair rule —
    # a side is empty iff its §0-normalized form is "" (not raw .strip()),
    # so status and similarity can never disagree on whitespace-only text.
    # (No behavioral change on the calibration data: the empty pairs are
    # exactly "" on both sides.) identical/variant remain a raw comparison.
    nf, ns = normalize(first), normalize(second)
    if not nf and not ns:
        return "empty_both"
    if not nf or not ns:
        return "empty_one_side"
    return "identical" if first == second else "variant"


def is_nonempty(pair: dict) -> bool:
    """r1 R6: the single non-empty-pair predicate shared by the case-level
    and aggregate subsets (excludes empty_both AND empty_one_side; a side
    is empty iff normalized to "")."""
    return bool(normalize(pair["text_first"]) or normalize(pair["text_second"]))


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------


def percentile(sorted_values: list[float], p: float) -> float | None:
    """Linear-interpolation percentile (p in [0, 1])."""
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_values[int(k)]
    return sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f)


def distribution(values: list[float]) -> dict:
    ordered = sorted(values)
    return {
        "n": len(values),
        "n_identical": sum(1 for v in values if v == 1.0),
        "n_variant": sum(1 for v in values if v < 1.0),
        "min": round(min(values), 4) if values else None,
        "median": round(statistics.median(values), 4) if values else None,
        "p10": round(percentile(ordered, 0.10), 4) if values else None,
        "max": round(max(values), 4) if values else None,
    }


# ---------------------------------------------------------------------------
# synthetic drift probes (discriminative-power demonstration, AC2)
# ---------------------------------------------------------------------------


def perturb(text: str, n_chars: int, rng: random.Random) -> str:
    """Deterministically substitute n_chars positions with pool characters."""
    if not text:
        return text
    positions = rng.sample(range(len(text)), min(n_chars, len(text)))
    chars = list(text)
    for p in positions:
        chars[p] = rng.choice(SUB_POOL)
    return "".join(chars)


def synthetic_probes(texts: list[str]) -> list[dict]:
    """Corrupt observed translations at graded magnitudes and score them.

    Probes (each demonstrates a different gate dimension):
      - single_char_ge4 : 1 char on len>=4 texts == the observed float
        magnitude (all observed variant pairs are 1-edit differences on
        4..15-char strings). Expected: every pair stays >= the min gate
        (0.75 >= 0.70 -> min-gate PASS, i.e. the threshold tolerates the
        observed sampling-float magnitude), but because the probe forces
        EVERY pair to float, the full gate (median leg) FAILs — which is
        the median leg's discriminative-power demonstration: a run where
        all regions float is systematic change, not benign sampling.
      - drift_40        : ~40% of characters replaced -> drift proxy,
        expected to FAIL on both legs (min drops to 0.5);
      - drift_70        : ~70% replaced -> severe drift proxy, expected to
        FAIL on both legs.
    """
    rng = random.Random(SYNTHETIC_SEED)
    probes: list[dict] = []
    for name, picker in (
        ("single_char_ge4", lambda t: 1 if len(normalize(t)) >= 4 else 0),
        ("drift_40", lambda t: max(1, round(len(normalize(t)) * 0.40))),
        ("drift_70", lambda t: max(1, round(len(normalize(t)) * 0.70))),
    ):
        sims: list[float] = []
        for text in texts:
            base = normalize(text)
            if not base:
                continue
            n_chars = picker(text)
            if n_chars <= 0:
                continue
            sims.append(similarity(base, normalize(perturb(base, n_chars, rng))))
        entry = {"probe": name, **distribution(sims)}
        entry["min_gate_verdict"] = (
            "PASS"
            if entry["min"] is not None and entry["min"] >= PROPOSED_GATE["min_min"]
            else "FAIL"
        )
        entry["gate_verdict"] = gate_verdict(entry["median"], entry["min"])
        probes.append(entry)
    return probes


def gate_verdict(median: float | None, minimum: float | None) -> str:
    """Apply the proposed gate: median >= median_min AND min >= min_min."""
    if median is None or minimum is None:
        return "NO_DATA"
    ok = median >= PROPOSED_GATE["median_min"] and minimum >= PROPOSED_GATE["min_min"]
    return "PASS" if ok else "FAIL"


# ---------------------------------------------------------------------------
# calibration core
# ---------------------------------------------------------------------------


def case_gate_verdict(pairs: list[dict]) -> str:
    """Gate verdict for one case with the coverage precondition (dsh r1 R2).

    The similarity gate alone would PASS an all-empty rerun pair trivially
    (every pair empty_both -> 1.0): at least one non-empty pair is required,
    otherwise NO_DATA — translation *coverage* failures are caught by the
    §7 translate scoring gate, not here. Zero-pair cases (e.g. a
    region_count=0 case on both sides, R11 zero-region exemption caliber)
    land here too: they do not block the overall gate but are registered
    individually (dsh r1 R3).
    """
    if not any(is_nonempty(p) for p in pairs):
        return "NO_DATA"
    values = [p["similarity_normalized"] for p in pairs]
    return gate_verdict(
        round(statistics.median(values), 4), round(min(values), 4)
    )


def build_pairs(case_id: str) -> dict:
    first = json.loads((SUMMARIES_DIR / f"qual-{case_id}.json").read_text(encoding="utf-8"))
    second = json.loads(
        (SUMMARIES_DIR / f"qual-{case_id}.rerun.json").read_text(encoding="utf-8")
    )
    t1 = translations_by_reading_order(first)
    t2 = translations_by_reading_order(second)
    ros1 = {r["reading_order"] for r in first["regions"]}
    ros2 = {r["reading_order"] for r in second["regions"]}
    if set(t1) != set(t2):
        raise SystemExit(
            f"FATAL: {case_id} reading_order sets differ between runs "
            f"{sorted(set(t1) ^ set(t2))} — alignment impossible"
        )
    # r1 R7: every region of a run must have a translate_detail (no silent
    # pair dropping — a dropped region would shrink n_pairs in the
    # fail-open direction). The dropped reading_orders are printed in the
    # FATAL channel.
    if set(t1) != ros1 or set(t2) != ros2:
        raise SystemExit(
            f"FATAL: {case_id} translate_details do not cover all regions — "
            f"run1 dropped={sorted(ros1 - set(t1))}, "
            f"run2 dropped={sorted(ros2 - set(t2))}"
        )
    pairs = []
    for ro in sorted(t1):
        a, b = t1[ro], t2[ro]
        # r1 R1: geometric cross-check of the alignment assumption. Set
        # equality of reading_orders cannot detect a permutation; bbox
        # identity per reading_order can (region geometry is regenerate-
        # stable across runs — verified 13/13 on K11, 5/5 on BJ02).
        if a["bbox"] != b["bbox"]:
            raise SystemExit(
                f"FATAL: {case_id} reading_order {ro} bbox differs between "
                f"runs {a['bbox']} != {b['bbox']} — reading_order alignment "
                "assumption violated, pairs would be silently misaligned"
            )
        text_first, text_second = a["translated_text"], b["translated_text"]
        status = pair_status(text_first, text_second)
        pairs.append(
            {
                "case_id": case_id,
                "reading_order": ro,
                "region_type": a["region_type"],
                "source_text": a["source_text"],
                "text_first": text_first,
                "text_second": text_second,
                "similarity_raw": round(similarity(text_first, text_second), 4),
                "similarity_normalized": round(
                    similarity(normalize(text_first), normalize(text_second)), 4
                ),
                "status": status,
            }
        )
    nonempty = [p for p in pairs if is_nonempty(p)]
    # floating-pair subsets are defined PER SCALING as similarity < 1.0 —
    # NOT via status=="variant" (that is a raw-string comparison; ro=5/10
    # are raw-variant but normalize to 1.0 and must not enter the
    # normalized floating subset)
    variant_raw = [p for p in pairs if p["similarity_raw"] < 1.0]
    variant_norm = [p for p in pairs if p["similarity_normalized"] < 1.0]
    return {
        "case_id": case_id,
        "language": first["language"],
        "source_sha256": first.get("source_sha256", ""),
        "n_pairs": len(pairs),
        "n_pairs_nonempty": len(nonempty),
        # r1 R7: coverage bookkeeping — dropped regions are impossible by
        # the fail-closed check above, recorded here so the artifact shows
        # the completeness basis of n_pairs.
        "n_regions_run1": len(first["regions"]),
        "n_regions_run2": len(second["regions"]),
        "n_translate_details_run1": len(first.get("translate_details", [])),
        "n_translate_details_run2": len(second.get("translate_details", [])),
        "n_dropped_regions": (len(ros1) - len(t1)) + (len(ros2) - len(t2)),
        "pairs": pairs,
        "stats": {
            "raw_all_pairs": distribution([p["similarity_raw"] for p in pairs]),
            "raw_nonempty": distribution([p["similarity_raw"] for p in nonempty]),
            "normalized_all_pairs": distribution(
                [p["similarity_normalized"] for p in pairs]
            ),
            "normalized_nonempty": distribution(
                [p["similarity_normalized"] for p in nonempty]
            ),
            # the floating-pair subset itself (similarity < 1.0): the AC2
            # anchor — the gate min must sit BELOW this measured worst float
            "raw_variant_only": distribution([p["similarity_raw"] for p in variant_raw]),
            "normalized_variant_only": distribution(
                [p["similarity_normalized"] for p in variant_norm]
            ),
        },
        # r1 R2: coverage precondition applied — an all-empty case would
        # otherwise PASS trivially (every pair empty_both -> 1.0).
        "gate_verdict_normalized": case_gate_verdict(pairs),
    }


def flatten_pairs(cases: list[dict]) -> list[dict]:
    return [p for case in cases for p in case["pairs"]]


# ---------------------------------------------------------------------------
# report rendering
# ---------------------------------------------------------------------------


def fmt_row(pair: dict) -> str:
    a = pair["text_first"].replace("\n", "\\n") or "(空)"
    b = pair["text_second"].replace("\n", "\\n") or "(空)"
    flag = "" if pair["similarity_normalized"] == 1.0 else " **浮动**"
    return (
        f"| {pair['reading_order']} | {pair['region_type']} | {a} | {b} "
        f"| {pair['similarity_raw']:.4f} | {pair['similarity_normalized']:.4f}{flag} |"
    )


def render_markdown(payload: dict) -> str:
    cases = payload["cases"]
    agg = payload["aggregate"]
    gate = payload["threshold_evaluation"]
    lines: list[str] = []
    lines.append("# M2-QUAL-DETERM-CALIB：reading_order 对齐译文相似度校准报告（F5）")
    lines.append("")
    lines.append(
        "- Task：[M2-QUAL-DETERM-CALIB](../../doc/tasks/M2-QUAL-DETERM-CALIB.md) · 分支 "
        "`agent/zcode/M2-QUAL-DETERM-CALIB` · 日期 2026-10-01"
    )
    lines.append(
        "- 生成方式：`experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py`（stdlib，确定性）"
        "——本报告与 `calibration.json` 均为脚本产物"
    )
    lines.append(
        "- 数据源（只读）：`verification/M2-TA3-B/phase2/summaries/qual-K11{,.rerun}.json、"
        "qual-BJ02{,.rerun}.json`（各 run 的 translate_details × regions，Run2 后 DB 译文）"
    )
    lines.append(f"- 证据强度：**{DIRECTIONAL_DISCLAIMER}**")
    lines.append(
        "- 口径修订来源：M2-QUAL-DETERM-CALIB + 用户裁决 2026-10-01（全部进行）"
    )
    lines.append("")
    lines.append("## 1. 方法（Gate 定义）")
    lines.append("")
    lines.append(
        "1. **对齐键 = reading_order**（方法学事实，TA3-B2 r1 R1 登记：region_id 每 run 重新生成，"
        "同 bbox 两轮 uuid 不同；region_id 只用于把 translate_details 关联到本 run 的 regions[].reading_order）。"
        "两次 run 的 reading_order 集合不一致时脚本 fail-closed 退出。"
        "**对齐假设交叉校验（dsh r1 R1）**：逐 reading_order 断言两 run 的 bbox 逐字段一致"
        "（region 几何跨 run 再生稳定——K11 13/13、BJ02 5/5 实测一致），不一致视为对齐假设被破坏"
        "（同集合置换无法被键集合相等检查发现），fail-closed 退出；translate_details 覆盖 regions[]"
        "亦为 fail-closed（缺失 region 的 reading_order 列表落盘于 FATAL 消息）。"
    )
    lines.append(
        "2. **相似度 = 1 − Levenshtein/max_len（字符级，stdlib）**；Levenshtein 与归一化复刻自项目既有 "
        "`experiments/M2-TA3-B/measure_cer.py`（不跨目录 import，M2-TA3-B 在本 Task 禁改面）。"
    )
    lines.append(
        "3. **双口径**：`raw`（译文原串，复现 quality-report F5 的 K11 \"7/11 非空对浮动\"观察）与 "
        "`normalized`（quality-thresholds §0 归一化：去全部空白、…≡...、casefold——与项目 CER 同口径，"
        "换行/空格级差异不计入翻译不稳定）。**Gate 口径 = normalized**，raw 作附报。"
        "空对判定基准统一为 normalize 后空串（dsh r1 R6），status 与 similarity 不会在仅空白差异上互相矛盾。"
    )
    lines.append(
        "4. **空译文对规则（登记口径，非临时约定）**：双方空 → 相似度 1.0（`empty_both`，两次 run 行为一致：都无译文）；"
        "单方空 → 相似度 0.0（`empty_one_side`，run 级行为变化=最大不稳定）。"
        "实测数据中仅出现前者（K11 ro=9 OCR 空文本、ro=13 SFX SKIP，两次 run 双侧均空）。"
        "**覆盖前置（dsh r1 R2）**：非空对 n≥1 方可判定，否则 **NO_DATA**——全空跑（如 provider 整体失效返回空译文）"
        "在相似度口径下会平凡 PASS（全部 empty_both=1.0），翻译覆盖度由 §7 translate 评分 Gate 兜底，"
        "相似度 Gate 不对覆盖度负责；region_count=0 的 case（如 K01 两侧均 0 region）贡献 0 对，"
        "按同一 NO_DATA 口径豁免、不阻断整体 Gate 但单独登记（dsh r1 R3，与 R11 零 region 豁免同口径）。"
    )
    lines.append(
        "5. **语义边界（绑定表述）**：本 Gate 度量的是**翻译稳定性**（同输入同模型重跑下译文的词汇级一致性），"
        "**不是渲染/导出复现性**。K11 export 字节差异的根因在 Run1 层（未逐层隔离），不在本度量范围内；"
        "「export 字节逐位一致」对 mock/deterministic provider 场景仍然有效并继续执行（BJ02 Run1 渲染产物两次逐位一致为上界参照）。"
    )
    lines.append("")
    lines.append("## 2. 实测分布")
    lines.append("")
    lines.append("| case | 对数 | 非空对 | 口径 | 相同对 | 浮动对 | min | median | P10 | Gate 判定 |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for case in cases:
        s = case["stats"]
        vn = case["gate_verdict_normalized"]
        lines.append(
            f"| {case['case_id']} | {case['n_pairs']} | {case['n_pairs_nonempty']} "
            f"| raw(全部) | {s['raw_all_pairs']['n_identical']} | {s['raw_all_pairs']['n_variant']} "
            f"| {s['raw_all_pairs']['min']} | {s['raw_all_pairs']['median']} | {s['raw_all_pairs']['p10']} | — |"
        )
        lines.append(
            f"| {case['case_id']} | {case['n_pairs']} | {case['n_pairs_nonempty']} "
            f"| normalized(全部，Gate 口径) | {s['normalized_all_pairs']['n_identical']} "
            f"| {s['normalized_all_pairs']['n_variant']} | {s['normalized_all_pairs']['min']} "
            f"| {s['normalized_all_pairs']['median']} | {s['normalized_all_pairs']['p10']} | **{vn}** |"
        )
    lines.append(
        f"| 合并（K11+BJ02） | {agg['n_pairs']} | {agg['n_pairs_nonempty']} | raw(非空) "
        f"| {agg['raw_nonempty']['n_identical']} | {agg['raw_nonempty']['n_variant']} "
        f"| {agg['raw_nonempty']['min']} | {agg['raw_nonempty']['median']} | {agg['raw_nonempty']['p10']} | — |"
    )
    lines.append(
        f"| 合并（K11+BJ02） | {agg['n_pairs']} | {agg['n_pairs_nonempty']} | normalized(非空) "
        f"| {agg['normalized_nonempty']['n_identical']} | {agg['normalized_nonempty']['n_variant']} "
        f"| {agg['normalized_nonempty']['min']} | {agg['normalized_nonempty']['median']} "
        f"| {agg['normalized_nonempty']['p10']} | — |"
    )
    lines.append("")
    k11 = cases[0]
    bj02 = cases[1]
    k11_v = k11["stats"]["normalized_variant_only"]
    bj02_v = bj02["stats"]["normalized_variant_only"]
    agg_v = agg["normalized_variant_only"]
    lines.append(
        f"关键读数：**浮动对（normalized，Gate 口径）K11 n={k11_v['n']}、min={k11_v['min']}、median={k11_v['median']}；"
        f"BJ02 n={bj02_v['n']}（min=median={bj02_v['min']}）；合并 n={agg_v['n']}、min={agg_v['min']}、median={agg_v['median']}**"
        f"——实测浮动幅度全部落在 [{agg_v['min']}, {agg_v['max']}]，是 min 阈值（{PROPOSED_GATE['min_min']}）的锚。"
        f"全部对口径：K11 raw 浮动 {cases[0]['stats']['raw_all_pairs']['n_variant']}/"
        f"{cases[0]['n_pairs_nonempty']} 非空对（复现 quality-report F5 已登记的 7/11 观察；"
        f"normalized 降为 {k11['stats']['normalized_all_pairs']['n_variant']}/{cases[0]['n_pairs_nonempty']}"
        f"——ro=5 换行位移、ro=10 空格差异被 §0 归一化吸收，浮动对全部为 1 编辑差）；"
        f"**BJ02（该样本两次 Run1 渲染产物逐位相同=上界参照）Run2 译文仍有 {bj02_v['n']} 对浮动**"
        "（`所谓强大`→`所谓强啊`，similarity 0.75）——Run1 渲染逐位与 Run2 译文浮动是两个独立层，"
        "与 quality-report §5 机制结论一致。"
    )
    lines.append("")
    lines.append("## 3. 逐对清单（normalized < 1.0 标 **浮动**）")
    lines.append("")
    for case in cases:
        lines.append(f"### {case['case_id']}（{case['language']}，n={case['n_pairs']}）")
        lines.append("")
        lines.append("| reading_order | type | 译文（首跑） | 译文（复跑） | sim(raw) | sim(normalized) |")
        lines.append("|---|---|---|---|---|---|")
        for pair in case["pairs"]:
            lines.append(fmt_row(pair))
        lines.append("")
    lines.append(
        "注：所有实测浮动对均为 **1 次编辑差**（单字替换或插入，如 `胡萝卜？`→`小萝卜？`、`所谓强大`→`所谓强啊`），"
        "无结构性语义漂移样本——这是 n=2 校准的核心局限（见 §6）。"
    )
    lines.append("")
    lines.append("## 4. Gate 阈值建议（AC2）")
    lines.append("")
    lines.append(
        f"**建议 Gate（normalized 口径）：`median ≥ {PROPOSED_GATE['median_min']}` 且 `min ≥ {PROPOSED_GATE['min_min']}`**"
        "（同 case 两次 run 全部对齐对，含空对规则）。"
    )
    lines.append("")
    lines.append("推理链（全部锚定实测分布，非拍脑袋）：")
    lines.append("")
    lines.append(
        f"1. **min ≥ {PROPOSED_GATE['min_min']}**：实测最坏浮动对 = {agg['normalized_all_pairs']['min']}"
        "（4 字译文单字替换，K11 ro=1/2/8 与 BJ02 ro=4）。同输入同模型重跑必须 PASS → 阈值须 ≤0.75；"
        "取 0.75 − 0.05 = **0.70**，**0.05 为绝对值余量**（dsh r1 R4，与 thresholds 写法统一——"
        "不是「一个字符」：4 字锚串上 1 编辑差=0.25，0.05 仅为其 1/5；对 20 字译文 1 编辑差才恰为 0.05）。"
        f"反向锚：40% 字符替换的合成漂移相似度 ≈{gate['synthetic_probes']['drift_40']['median']}"
        f"（min {gate['synthetic_probes']['drift_40']['min']}）→ FAIL；"
        "3 字及以下译文的单字浮动（2/3≈0.667）也会 FAIL——fail-closed 方向，见 §6 局限。"
    )
    lines.append(
        f"2. **median ≥ {PROPOSED_GATE['median_min']}**：实测 median = "
        f"{agg['normalized_all_pairs']['median']}（同输入同模型重跑下多数 region 译文逐位相同）。"
        "0.95 的语义 = 允许少量采样浮动存在、但多数 region 浮动（系统性漂移，如 prompt/provider 变更）即 FAIL。"
        "18 对分布下的精确边界（以实测浮动幅度 [0.75, 0.875] 计，**在本校准样本的译文长度分布下**——"
        "浮动串长 4–16 字，dsh r1 R5）：浮动 ≤8 对（<50%）时 median 恒=1.0（PASS）；"
        "浮动 ≥9 对（≥50%）时 median ≤(0.875+1)/2=0.9375 <0.95（恒 FAIL）——即约半数 region 浮动即触发 median gate。"
        "该边界不外推到显著更长的译文：长译文 1 编辑差相似度更高（20 字串 1 编辑=0.95），"
        "median 腿对低幅系统性漂移的分辨力随译文长度下降（§6 局限）。"
    )
    lines.append(
        "3. **判别力合成对照（无自然 FAIL 样本的替代证据）**：对实测译文施加确定性字符扰动"
        f"（seed={SYNTHETIC_SEED}，非 FAIL 实证、仅演示阈值判别力）。三个探针各演示一个维度："
        "**single_char_ge4**（实测量级浮动：每串 1 编辑差）逐对全部 ≥0.75 → min gate 不触发"
        "（阈值容纳实测浮动幅度），但因探针强制全部对浮动，median=0.857 → 完整 gate FAIL"
        "（即「全部 region 系统性浮动」被 median leg 抓住）；**drift_40/drift_70**（漂移代理）"
        "min 跌破 0.70 → min gate 抓住结构性漂移："
    )
    lines.append("")
    lines.append("| 合成对照 | n | min | median | min-gate(≥0.70) | 完整 gate | 演示结论 |")
    lines.append("|---|---|---|---|---|---|---|")
    probe_conclusion = {
        "single_char_ge4": "实测浮动量级逐对 PASS；全 region 浮动 → median leg FAIL",
        "drift_40": "~40% 字符替换（漂移代理）→ min leg FAIL",
        "drift_70": "严重漂移 → 双维度 FAIL",
    }
    for probe in gate["synthetic_probes_list"]:
        lines.append(
            f"| {probe['probe']} | {probe['n']} | {probe['min']} | {probe['median']} "
            f"| **{probe['min_gate_verdict']}** | **{probe['gate_verdict']}** "
            f"| {probe_conclusion[probe['probe']]} |"
        )
    lines.append("")
    lines.append(
        "与实测分布合起来的判别力闭环：实测「少数对浮动」（K11 5/13、BJ02 1/5）→ 完整 gate PASS"
        "（同输入重跑必须 PASS 的要求满足）；「全部对 1 编辑浮动」（系统性轻微变化）→ median leg FAIL；"
        "「结构性漂移」→ min leg FAIL。"
    )
    lines.append("")
    lines.append(
        f"4. **对实测分布的判定**：K11 → **{cases[0]['gate_verdict_normalized']}**；"
        f"BJ02 → **{cases[1]['gate_verdict_normalized']}**（上界参照：其 Run1 渲染产物逐位一致）。"
        "即：已知的「同输入同模型重跑」在该 Gate 下 PASS；「明显漂移」（合成 40%+ 字符替换）FAIL。"
    )
    lines.append("")
    lines.append("## 5. 语义边界与双轨表述（绑定）")
    lines.append("")
    lines.append(
        "- 本 Gate（相似度）适用于 **remote/随机采样翻译 provider** 的确定性验收；"
        "度量翻译稳定性，不度量渲染/导出复现性。"
    )
    lines.append(
        "- **mock/deterministic provider 场景维持 export 字节逐位一致**（TA3-A 框架原口径不变）；"
        "BJ02 两次 Run1 渲染产物逐位相同是该口径的实际先例与相似度度量的上界参照"
        "（Run1 渲染逐位 ≠ Run2 译文逐位——BJ02 自身 Run2 译文仍有浮动对）。"
    )
    lines.append(
        "- K11 export 哈希不一致（Run1 层根因未逐层隔离）**不**由本 Gate 解释或修复；"
        "Run1 层确定性属后续独立问题（§6 局限）。"
    )
    lines.append("")
    lines.append("## 6. 局限登记（AC4）")
    lines.append("")
    lines.append(
        "1. **n=2 case 校准**：仅 K11（ko 13 region）与 BJ02（ja 5 region）一组重跑对；"
        "阈值 0.70/0.95 锚定在 18 对实测分布上，样本量不支持外推生产结论；后续 qualification run 应同时落盘逐对相似度以滚动校准。"
    )
    lines.append(
        "2. **无自然 FAIL 样本**：实测浮动全部为 1 编辑差（无结构性漂移），判别力只能用合成对照演示"
        "（§4.3），不是漂移场景的实证。"
    )
    lines.append(
        "3. **极短译文粒度边界（长度相关悬崖，dsh r1 R4）**：min 阈值对编辑数的容忍度与译文长度强相关——"
        "同一「多 1 编辑」在 4 字串上跌 0.25、在 20 字串上只跌 0.05：3 字译文单字浮动（≈0.667）会被 min≥0.70 判 FAIL"
        "（fail-closed 方向可接受，但会把「良性的单字采样差」误报为漂移）；4 字反例（实测锚串）：2 次编辑即 2/4=0.5 → FAIL，"
        "即 0.05 的绝对值余量在锚长度上容不下第二个编辑差；实测最短浮动串为 4 字。"
    )
    lines.append(
        "4. **Run1 层相似度未测**：K11 export 差异根因在 Run1（批量翻译/inpaint/render，未逐层隔离，scratch db 已清理）；"
        "本 Gate 只覆盖 Run2 后 DB 译文层的稳定性。"
    )
    lines.append(
        "5. **归一化口径依赖**：normalized 口径吸收换行/空格差异（K11 浮动 7→5）；"
        "若产品语义认为换行位置也是译文的一部分，应引用 raw 口径附报。"
    )
    lines.append(
        "6. **覆盖前置与全空跑盲点（dsh r1 R2/R3）**：空对规则下全空跑（两次 run 译文全空，如 provider 整体失效）"
        "相似度全部 1.0、可平凡 PASS 相似度 Gate——故 Gate 定义加非空对 n≥1 的覆盖前置（否则 NO_DATA）；"
        "翻译覆盖度（该译的没译）由 §7 translate 评分 Gate 兜底，相似度 Gate 不对覆盖度负责；"
        "region_count=0 的 case（本次校准集中的 K01 两侧均 0 region）贡献 0 对、按 NO_DATA 豁免，"
        "不阻断整体 Gate 但须单独登记——**ko webtoon 家族因此未被本次校准覆盖**（K11=ko P&C、BJ02=ja BJ）。"
    )
    lines.append(
        "7. **median 腿分辨力随译文长度下降（dsh r1 R5）**：§4.2 的「浮动 ≥9 对恒 FAIL」边界以实测浮动幅度 [0.75, 0.875]"
        "（串长 4–16 字）为条件；更长译文上 1 编辑差的相似度更高（20 字串=0.95≥阈值），"
        "「全部 region 低幅浮动」的场景 median 腿可能 PASS——结构性漂移仍由 min 腿兜底，"
        "但 median 腿不是长度无关的系统性漂移检测器。"
    )
    lines.append(
        "8. **词面口径的固有误报方向（dsh r1 R8）**：字符级相似度度量的是词面一致，不是语义等价——"
        "语义等价的合法重译（同义改写/整段重译）会被判低相似度 FAIL，而 remote 采样漂移的主形态恰是同义改写；"
        "即本 Gate 在「假 FAIL」（保守）方向系统性偏置，不会漏报词面漂移但会误报合法重译。"
        "未加同义改写代理探针：词面框架内无法可靠构造语义等价改写的确定性代理（任何字面扰动都改变词面），"
        "该维度的验证需语义度量（如回译/向量相似度），属后续独立工作、此处仅登记。"
    )
    lines.append("")
    lines.append(f"> **声明**：{DIRECTIONAL_DISCLAIMER}。")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> int:
    global SUMMARIES_DIR, OUT_DIR
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summaries-dir", default=str(SUMMARIES_DIR))
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    SUMMARIES_DIR = Path(args.summaries_dir)
    OUT_DIR = Path(args.out_dir)

    cases = [build_pairs(case_id) for case_id in CALIBRATION_CASES]
    all_pairs = flatten_pairs(cases)
    nonempty_pairs = [p for p in all_pairs if is_nonempty(p)]
    variant_raw_pairs = [p for p in all_pairs if p["similarity_raw"] < 1.0]
    variant_norm_pairs = [p for p in all_pairs if p["similarity_normalized"] < 1.0]

    agg = {
        "n_pairs": len(all_pairs),
        "n_pairs_nonempty": len(nonempty_pairs),
        "raw_all_pairs": distribution([p["similarity_raw"] for p in all_pairs]),
        "raw_nonempty": distribution([p["similarity_raw"] for p in nonempty_pairs]),
        "normalized_all_pairs": distribution(
            [p["similarity_normalized"] for p in all_pairs]
        ),
        "normalized_nonempty": distribution(
            [p["similarity_normalized"] for p in nonempty_pairs]
        ),
        "raw_variant_only": distribution(
            [p["similarity_raw"] for p in variant_raw_pairs]
        ),
        "normalized_variant_only": distribution(
            [p["similarity_normalized"] for p in variant_norm_pairs]
        ),
    }

    probes = synthetic_probes([p["text_first"] for p in nonempty_pairs])
    agg_norm = agg["normalized_all_pairs"]
    threshold_evaluation = {
        "gate": PROPOSED_GATE,
        "observed": {
            "K11": cases[0]["gate_verdict_normalized"],
            "BJ02": cases[1]["gate_verdict_normalized"],
        },
        "synthetic_probes_list": probes,
        "synthetic_probes": {p["probe"]: p for p in probes},
        "reasoning": (
            "min gate 0.70 = measured floating-pair band [0.75, 0.875] minus "
            "a 0.05 ABSOLUTE margin (not 'one character': on the 4-char anchor "
            "strings one edit is 0.25, so the margin is a fifth of an edit; "
            "r1 R4): every observed same-input rerun float stays above it "
            "(single-char probes: per-pair PASS) while 40%+ character drift "
            "(probe min 0.5) must FAIL. median gate 0.95: under THIS "
            "calibration sample's translation-length distribution (float "
            "strings 4-16 chars, 1-edit magnitude [0.75, 0.875]), <=8/18 "
            "floating pairs keeps median=1.0 (PASS), >=9/18 forces "
            "median<=0.9375 (FAIL) — i.e. systematic change fails, benign "
            "sparse sampling float passes; on longer translations the "
            "median leg's resolution of low-magnitude systematic drift "
            "decreases (1 edit on a 20-char string = 0.95), registered as "
            "a limitation (r1 R5). Coverage precondition (r1 R2): an "
            "all-empty rerun pair passes similarity trivially -> NO_DATA "
            "without >=1 non-empty pair; translation coverage is the §7 "
            "translate scoring gate's job. Anchored on the measured 18-pair "
            "distribution (n=2 cases, directional)."
        ),
    }

    payload = {
        "task": "M2-QUAL-DETERM-CALIB",
        "measure": "reading_order-aligned translation similarity (F5 determinism gate, redefined per user ruling 2026-10-01)",
        "calibration_source": {
            # r1 R13: repo-root-relative so the committed artifact is
            # reproducible across checkouts (no machine-specific path).
            "summaries_dir": (
                str(SUMMARIES_DIR.relative_to(REPO_ROOT))
                if SUMMARIES_DIR.is_relative_to(REPO_ROOT)
                else str(SUMMARIES_DIR)
            ),
            "cases": CALIBRATION_CASES,
            "text_layer": "translate_details.translated_text (Run2-after DB text), joined to regions[].reading_order via region_id",
        },
        "method": {
            "alignment_key": "reading_order (region_id regenerated every run, TA3-B2 r1 R1); cross-checked by per-reading_order bbox identity between the two runs, fail-closed on mismatch — key-set equality alone cannot detect a permutation (dsh r1 R1); translate_details must cover all regions (no silent pair dropping, dropped reading_orders in the FATAL message, dsh r1 R7)",
            "similarity": "1 - Levenshtein/max_len (character level, stdlib; replicated from experiments/M2-TA3-B/measure_cer.py)",
            "scalings": {
                "raw": "translated_text verbatim (reproduces quality-report F5 K11 7/11 observation)",
                "normalized": "quality-thresholds §0: strip all whitespace, …≡..., casefold (same as project CER normalization); GATE SCALING",
            },
            "empty_pair_rule": {
                "both_empty": "similarity 1.0 (status empty_both; runs agree: no translation either time)",
                "one_side_empty": "similarity 0.0 (status empty_one_side; run-level behaviour change)",
                "emptiness_basis": "normalized-empty (r1 R6): a side is empty iff its §0-normalized form is \"\" — status and similarity share one basis",
                "coverage_precondition": ">=1 non-empty pair required, else NO_DATA (an all-empty rerun passes similarity trivially; coverage is the §7 translate scoring gate's job; region_count=0 cases are NO_DATA-exempt and registered individually, r1 R2/R3)",
                "observed": "only empty_both occurs (K11 ro=9 OCR-empty, ro=13 SFX SKIP)",
            },
            "semantic_boundary": (
                "gate measures TRANSLATION STABILITY under rerun with a stochastic "
                "remote provider; NOT render/export reproducibility. 'export bytes "
                "bitwise equal' remains valid for mock/deterministic provider chains "
                "(BJ02 Run1 page render = upper-bound reference). K11 export mismatch "
                "root cause sits in the Run1 stage (never layer-isolated) and is out "
                "of scope."
            ),
        },
        "cases": cases,
        "aggregate": agg,
        "threshold_evaluation": threshold_evaluation,
        "limitations": [
            "n=2 calibration cases (K11 13 regions, BJ02 5 regions) — thresholds are directional, re-calibrate on future qualification runs which should persist per-pair similarities",
            "no natural FAIL sample: all observed floats are 1-edit differences; discriminative power shown by deterministic synthetic probes only",
            "very-short-translation granularity, length-dependent cliff (r1 R4): min-gate edit tolerance scales with length — the same extra edit costs 0.25 on a 4-char anchor but 0.05 on a 20-char text; 3-char single-char float (~0.667) fails min>=0.70 (fail-closed direction), and 2 edits on the 4-char anchor = 0.5 -> FAIL, so the 0.05 absolute margin does not absorb a second edit at anchor length",
            "Run1-stage similarity unmeasured (K11 export root cause not layer-isolated); this gate covers the Run2-after DB text layer only",
            "normalized scaling absorbs line-break/spacing differences (K11 floats 7 raw -> 5 normalized); quote raw if line breaks are part of the product semantics",
            "coverage precondition / all-empty blind spot (r1 R2/R3): under the empty-pair rule an all-empty rerun (provider down) passes the similarity gate trivially (all empty_both = 1.0), so the gate requires >=1 non-empty pair else NO_DATA; translation COVERAGE is enforced by the §7 translate scoring gate, not here; region_count=0 cases (K01 in this set, both sides 0 regions) contribute 0 pairs and are NO_DATA-exempt — they do not block the overall gate but are registered individually, so the ko webtoon family is NOT covered by this calibration (K11=ko P&C, BJ02=ja BJ)",
            "median-leg resolution of low-magnitude systematic drift decreases with translation length (r1 R5): the '>=9/18 floats always FAIL' boundary holds for THIS sample's length distribution (float strings 4-16 chars, magnitude [0.75, 0.875]); on longer texts a 1-edit float scores >=0.95 (20-char string), so an all-regions-low-magnitude-float scenario can PASS the median leg — the min leg still catches structural drift, but the median leg is not a length-independent systematic-drift detector",
            "lexical-caliber false-FAIL direction (r1 R8): character-level similarity measures surface agreement, not semantic equivalence — a legitimate retranslation (synonym rewording / full-paragraph rewrite) is judged low-similarity FAIL, and synonym rewording is exactly the dominant remote-sampling drift morphology; the gate is thus biased in the conservative (false-FAIL) direction. No synonym-rewrite proxy probe is added: within a lexical framework a deterministic semantic-equivalence proxy cannot be constructed faithfully (any literal perturbation changes the surface); validating that dimension needs semantic metrics (back-translation / embedding similarity) as separate future work — registered, not implemented",
        ],
        "directional_disclaimer": DIRECTIONAL_DISCLAIMER,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = OUT_DIR / "calibration.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    md_path = OUT_DIR / "calibration.md"
    md_path.write_text(render_markdown(payload), encoding="utf-8")

    print(f"pairs: K11 n={cases[0]['n_pairs']} BJ02 n={cases[1]['n_pairs']} total={agg['n_pairs']}")
    for name, dist in (
        ("raw/all", agg["raw_all_pairs"]),
        ("raw/nonempty", agg["raw_nonempty"]),
        ("norm/all", agg["normalized_all_pairs"]),
        ("norm/nonempty", agg["normalized_nonempty"]),
    ):
        print(
            f"[{name:14}] variant={dist['n_variant']:2}/{dist['n']:2} "
            f"min={dist['min']} median={dist['median']} p10={dist['p10']}"
        )
    print("gate verdicts:", threshold_evaluation["observed"])
    for probe in probes:
        print(f"probe {probe['probe']:16} min={probe['min']} median={probe['median']} -> {probe['gate_verdict']}")
    print(f"calibration.json -> {json_path}")
    print(f"calibration.md   -> {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
