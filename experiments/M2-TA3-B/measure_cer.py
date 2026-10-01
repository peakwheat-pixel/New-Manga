"""M2-TA3-B2 phase-2: automatic CER measurement (AC2) + SFX stats.

Inputs (all produced by run_qualification.py / extract_svg_gt.py):
  - phase2/summaries/qual-<case>.json  (per-region ``ocr_details``/``translate_details``)
  - phase2/ocr/svg-gt-<case>.json      (official SVG text layer, geometry kept)

What this script does (standard library only, no new dependencies):
  1. G1 alignment: SVG text elements (canvas coords, scaled by
     source_width / canvas_width) are matched to detected region bboxes by
     geometric intersection — text anchors fall inside the bbox, flowRoot
     bounding polygons overlap it.  This is the mechanised part of the
     ``present-but-unaligned`` human alignment work (r2 N1); the human
     spot-check of the alignment stays mandatory (thresholds §5 risk 2).
  2. region-level CER with the §0 normalization (strip ALL whitespace,
     ``…`` ≡ ``...``, latin casefold; ``ー`` is NOT folded into ``-``) and
     a stdlib Levenshtein; auto-scored denominator = the G1 regions that
     survive the §5 risk-2 exclusions (NOT all detected regions — R5,
     DSH r1); every excluded row is recorded in ``excluded[]`` with its
     reason and, where computable, the hypothetical CER if it had been
     scored (multi-element GT rows are concatenations, not true text, so
     treat those numbers as bounds, not measurements).
  3. Per-language G1 summary (median / P90 / CER=0 share / CER<=0.5 share).
  4. SFX translation stats across the 20 cases (thresholds §3.1): with the
     production default ``SfxPolicy.SKIP`` every SFX region takes the
     production ``skip_policy`` gate, so n is expected to be 0 and the
     n<15 rule (R13) applies — distribution only, no Gate.
  5. region_count=0 cases are exempted (R11) and recorded as such.

NOT produced here (R15, DSH r1): the layered OCR spot-check worksheet
skeleton and the dialogue/SFX human worksheets are built by
``build_worksheets.py`` (the earlier docstring wrongly claimed this script
emitted an n=30 worksheet, and the layered-tag constants below were dead
code copied from it — both removed).

All numbers are DIRECTIONAL (DeepSeek/first quality run; no production
conclusions may be drawn from them).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PHASE2 = REPO_ROOT / "verification" / "M2-TA3-B" / "phase2"


def normalize(text: str) -> str:
    """quality-thresholds §0 normalization."""
    if not text:
        return ""
    text = text.replace("…", "...").replace("\u22ef", "...")
    text = "".join(text.split())  # strips ALL whitespace incl. \u3000
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
            curr.append(
                min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb))
            )
        prev = curr
    return prev[-1]


def cer(gt: str, hyp: str) -> float:
    return levenshtein(gt, hyp) / max(len(gt), 1)


def load_summaries(summaries_dir: Path) -> list[dict]:
    out = []
    for path in sorted(summaries_dir.glob("qual-*.json")):
        if ".rerun" in path.name or path.name.startswith("qual-report"):
            continue
        out.append(json.loads(path.read_text(encoding="utf-8")))
    return out


def bbox_overlap_area(a: dict, b: tuple[float, float, float, float]) -> float:
    ax1, ay1 = a["x"], a["y"]
    ax2, ay2 = a["x"] + a["width"], a["y"] + a["height"]
    bx1, by1, bx2, by2 = b
    ix = max(0.0, min(ax2, bx2) - max(ax1, bx1))
    iy = max(0.0, min(ay2, by2) - max(ay1, by1))
    return ix * iy


def align_svg_to_regions(case_summary: dict, svg_gt: dict) -> tuple[dict, list[dict]]:
    """Match SVG text elements to detected regions geometrically.

    Returns {region_id: aligned_text} plus a per-element trace (for the
    human alignment audit).
    """
    try:
        canvas_w = float(str(svg_gt["canvas_wh"][0]).replace("px", ""))
        canvas_h = float(str(svg_gt["canvas_wh"][1]).replace("px", ""))
    except (TypeError, ValueError):
        canvas_w = canvas_h = 0.0
    source_w = case_summary.get("source_size", [0, 0])[0] or 0
    scale = (source_w / canvas_w) if (canvas_w and source_w) else 0.0

    regions = case_summary.get("regions", [])
    matched: dict[str, list[str]] = {}
    trace: list[dict] = []
    for elem in svg_gt.get("text_elements", []):
        hit_region = None
        if scale:
            if elem["kind"] == "text":
                ax, ay = elem["anchor"]
                px, py = ax * scale, ay * scale
                for region in regions:
                    b = region["bbox"]
                    if b["x"] - 8 <= px <= b["x"] + b["width"] + 8 and b["y"] - 8 <= py <= b["y"] + b["height"] + 8:
                        hit_region = region["region_id"]
                        break
            else:  # flowRoot: polygon overlap with region bbox
                poly = elem["polygon"]
                xs = [p[0] * scale for p in poly]
                ys = [p[1] * scale for p in poly]
                box = (min(xs), min(ys), max(xs), max(ys))
                best = 0.0
                for region in regions:
                    area = bbox_overlap_area(region["bbox"], box)
                    if area > best:
                        best = area
                        hit_region = region["region_id"]
        trace.append(
            {
                "text": elem["text"][:60],
                "kind": elem["kind"],
                "anchor_canvas": elem["anchor"],
                "matched_region_id": hit_region,
            }
        )
        if hit_region:
            matched.setdefault(hit_region, []).append(elem["text"])
    return matched, trace


def pct(value: float, total: int) -> str:
    return f"{(100.0 * value / total):.1f}%" if total else "n/a"


def char_overlap(gt_norm: str, hyp_norm: str) -> float:
    """Share of GT characters present in the hypothesis (alignment sanity)."""
    if not gt_norm:
        return 0.0
    gt_chars = set(gt_norm)
    if not gt_chars:
        return 0.0
    hyp_chars = set(hyp_norm)
    return len(gt_chars & hyp_chars) / len(gt_chars)


#: rows with these gt_source values never enter the automatic CER denominator
#: (thresholds §5 risk 2); R5 (DSH r1) requires them recorded with a reason and
#: the hypothetical CER they would have contributed.
AUTO_SCORED_SOURCES = {"G1:svg_native", "G2:pending_human_worksheet"}


def reason_category(gt_source: str) -> str:
    if gt_source == "UNALIGNED_G1_CASE":
        return "unaligned"
    if gt_source == "MANUAL_REVIEW:empty-ocr":
        return "empty-ocr"
    if gt_source.startswith("MANUAL_REVIEW:") and gt_source.endswith("-svg-elements"):
        return "multi-element"
    return "low-char-overlap"  # SUSPECT_MISMATCH:text-family


def excluded_entry(row: dict, gt_raw: str, hyp_raw: str) -> dict:
    gt_norm, hyp_norm = normalize(gt_raw), normalize(hyp_raw)
    hypothetical = None
    if gt_norm:
        # meaningful whenever the GT side exists; an empty OCR side yields
        # 1.0 (a true full miss — R5: the exclusion rule must not hide these)
        hypothetical = round(cer(gt_norm, hyp_norm), 4)
    return {
        "unit_id": row["unit_id"],
        "language": row["language"],
        "case_id": row["case_id"],
        "region_id": row["region_id"],
        "reason": row["gt_source"],
        "reason_category": reason_category(row["gt_source"]),
        "gt_text": row["gt_text"],
        "ocr_text": row["ocr_text"],
        "hypothetical_cer_if_scored": hypothetical,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summaries-dir", default=str(PHASE2 / "summaries"))
    parser.add_argument("--ocr-dir", default=str(PHASE2 / "ocr"))
    args = parser.parse_args()

    summaries_dir = Path(args.summaries_dir)
    ocr_dir = Path(args.ocr_dir)
    ocr_dir.mkdir(parents=True, exist_ok=True)
    summaries = load_summaries(summaries_dir)
    if not summaries:
        print("FATAL: no qual-*.json summaries found", file=__import__("sys").stderr)
        return 2

    svg_gts: dict[str, dict] = {}
    for case_id in ("J46", "J47", "K11", "K19"):
        path = ocr_dir / f"svg-gt-{case_id}.json"
        if path.is_file():
            svg_gts[case_id] = json.loads(path.read_text(encoding="utf-8"))

    rows: list[dict] = []
    excluded_rows: list[dict] = []
    exempt_cases: list[dict] = []
    per_language: dict[str, list[float]] = {"ja": [], "ko": []}
    alignment_notes: dict[str, dict] = {}

    for summary in summaries:
        case_id = summary["case_id"]
        language = summary["language"]
        details = summary.get("ocr_details", [])
        if summary.get("run2", {}).get("status") == "SKIPPED" or not details:
            exempt_cases.append(
                {
                    "case_id": case_id,
                    "reason": "region_count=0 (R11 exemption, data:no-regions-detected)",
                    "attribution": summary.get("attribution", []),
                }
            )
            continue
        g1_texts: dict[str, list[str]] = {}
        if case_id in svg_gts:
            aligned, trace = align_svg_to_regions(summary, svg_gts[case_id])
            g1_texts = {k: v for k, v in aligned.items()}
            alignment_notes[case_id] = {
                "svg_elements_total": svg_gts[case_id]["n_text_elements"],
                "svg_elements_matched": sum(1 for t in trace if t["matched_region_id"]),
                "regions_matched": len(g1_texts),
                "regions_total": len(details),
                "alignment_method": "geometric (anchor-in-bbox / flowRoot-polygon-overlap); excluded from automatic CER: multi-element matches, low char_overlap (<0.3) matches, UNALIGNED (0-element) regions and empty-OCR regions — all left to the human worksheet (thresholds §5 risk 2 / §2.2; R5, DSH r1: the two UNALIGNED/empty-OCR classes are now named explicitly)",
                "trace": trace,
            }
        for detail in details:
            hyp_raw = detail.get("ocr_text", "")
            gt_source = ""
            gt_raw = ""
            if case_id in svg_gts:
                hits = g1_texts.get(detail["region_id"], [])
                n_hits = len(hits)
                gt_raw = "\n".join(hits)
                if n_hits == 0:
                    gt_source = "UNALIGNED_G1_CASE"
                elif n_hits > 1:
                    # several SVG boxes fell into one region: the mapping is
                    # ambiguous -> human arbitration, never auto CER
                    gt_source = f"MANUAL_REVIEW:{n_hits}-svg-elements"
                elif not hyp_raw.strip():
                    # single GT element but empty OCR: could be an alignment
                    # miss or a true OCR miss -> human arbitration
                    gt_source = "MANUAL_REVIEW:empty-ocr"
                elif char_overlap(normalize(gt_raw), normalize(hyp_raw)) < 0.3:
                    # GT text family and OCR text family do not correspond
                    # (e.g. SVG credits vs balloon dialogue) -> suspect
                    gt_source = "SUSPECT_MISMATCH:text-family"
                else:
                    gt_source = "G1:svg_native"
            else:
                gt_source = "G2:pending_human_worksheet"
            row = {
                "unit_id": f"{case_id}:{detail['region_id'][:8]}",
                "language": language,
                "case_id": case_id,
                "region_id": detail["region_id"],
                "region_type": detail.get("region_type", ""),
                "gt_source": gt_source,
                "gt_text": gt_raw.replace("\n", " "),
                "ocr_text": hyp_raw.replace("\n", " "),
                "cer": "",
            }
            if gt_source == "G1:svg_native":
                value = cer(normalize(gt_raw), normalize(hyp_raw))
                row["cer"] = f"{value:.4f}"
                per_language.setdefault(language, []).append(value)
            if gt_source not in AUTO_SCORED_SOURCES:
                excluded_rows.append(excluded_entry(row, gt_raw, hyp_raw))
            rows.append(row)

    # ---- language-level G1 summaries ---------------------------------------
    summary_json: dict = {
        "task": "M2-TA3-B2",
        "measure": "G1 native-GT CER (directional)",
        "normalization": "strip-all-whitespace; …≡...; latin casefold; ー not folded (thresholds §0)",
        "denominator": (
            "auto-scored subset of G1-case regions AFTER the thresholds §5 "
            "risk-2 exclusions (R5, DSH r1): ko K11 13 regions -> 6 "
            "auto-scored + 7 excluded; ja J46/J47 -> 0 auto-scored + 6 "
            "excluded; every excluded row is listed in excluded[] with its "
            "reason and (where computable) the hypothetical CER it would "
            "have contributed. The earlier wording 'all detected regions of "
            "the G1 cases' was wrong."
        ),
        "languages": {},
        "exempt_cases": exempt_cases,
        "excluded": excluded_rows,
        "alignment_notes": {
            k: {kk: vv for kk, vv in v.items() if kk != "trace"} for k, v in alignment_notes.items()
        },
        "sfx_translation_stats": {},
        "directional_disclaimer": "first quality run; single automatic metric on an un-audited alignment; numbers are directional evidence only",
    }
    gate_proposal = {"ja": 0.10, "ko": 0.20}  # thresholds §2.3 G1 subset medians
    for language, values in sorted(per_language.items()):
        values_sorted = sorted(values)
        n = len(values)
        p90 = values_sorted[min(n - 1, math.ceil(0.9 * n) - 1)] if n else float("nan")
        entry = {
            "n_regions": n,
            "cer_median": round(statistics.median(values), 4) if values else None,
            "cer_p90": round(p90, 4) if values else None,
            "cer_zero_share": pct(sum(1 for v in values if v == 0), n),
            "cer_le_05_share": pct(sum(1 for v in values if v <= 0.5), n),
            "proposal_gate_median": gate_proposal.get(language),
            "gate_verdict": (
                "PASS"
                if values and statistics.median(values) <= gate_proposal[language]
                else ("FAIL" if values else "NO_GT_REGIONS")
            ),
        }
        summary_json["languages"][language] = entry

    # ---- SFX translation stats (§3.1) ---------------------------------------
    sfx_total = 0
    sfx_translated = 0
    sfx_examples: list[dict] = []
    for summary in summaries:
        for detail in summary.get("translate_details", []):
            if detail.get("region_type") != "sfx":
                continue
            sfx_total += 1
            if (detail.get("translated_text") or "").strip():
                sfx_translated += 1
                sfx_examples.append(
                    {
                        "case_id": summary["case_id"],
                        "region_id": detail["region_id"],
                        "source": detail.get("source_text", "")[:40],
                        "translated": detail.get("translated_text", "")[:40],
                    }
                )
    summary_json["sfx_translation_stats"] = {
        "n_sfx_regions": sfx_total,
        "n_translated": sfx_translated,
        "note": (
            "production SfxPolicy default SKIP: every SFX region takes the "
            "production gate decision skip_policy/sfx_skip, so the run "
            "yields no automatic SFX translations; thresholds §3.1 n<15 "
            "rule (R13) applies - distribution registered, no Gate"
            if sfx_translated < 15
            else "n>=15: score per thresholds §3.1"
        ),
        "examples": sfx_examples[:10],
    }

    # ---- outputs ------------------------------------------------------------
    csv_path = ocr_dir / "cer-regions.csv"
    cols = ["unit_id", "language", "case_id", "region_id", "region_type", "gt_source", "gt_text", "ocr_text", "cer"]
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        fh.write(",".join(cols) + "\n")
        for row in rows:
            fh.write(
                ",".join(
                    '"' + str(row[c]).replace('"', '""') + '"' for c in cols
                )
                + "\n"
            )
    summary_path = ocr_dir / "cer-summary.json"
    summary_path.write_text(
        json.dumps(summary_json, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    trace_path = ocr_dir / "svg-alignment-trace.json"
    trace_path.write_text(
        json.dumps(alignment_notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"regions csv  -> {csv_path} ({len(rows)} rows)")
    for language, entry in summary_json["languages"].items():
        print(
            f"[{language}] G1 n={entry['n_regions']} median={entry['cer_median']} "
            f"p90={entry['cer_p90']} zero={entry['cer_zero_share']} "
            f"gate({entry['proposal_gate_median']})={entry['gate_verdict']}"
        )
    print(f"SFX: n={sfx_total} translated={sfx_translated}")
    print(f"excluded from auto CER: {len(excluded_rows)} rows (see cer-summary.json excluded[])")
    print(f"summary -> {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
