"""M2-TA3-B2-KO-RERUN AC4: reading_order-aligned translation-similarity gate.

Determinism companion for the ko qualification rerun.  The project gate for
REMOTE translation chains is the similarity gate redefined by
M2-QUAL-DETERM-CALIB + user ruling 2026-10-01 (quality-thresholds.md §5
dual-track caliber): export-hash bitwise equality applies to mock /
deterministic chains only.  This script replicates the CALIB method
(experiments/M2-QUAL-DETERM-CALIB/calibrate_determinism.py, kept local on
purpose — that task's dir is outside this Task's allowed surface) for ONE
ko-rerun case pair (qual-<case>.json vs qual-<case>.rerun.json):

  1. align the two runs' translations by reading_order (region_id is
     regenerated every run — M2-TA3-B2 r1 R1); fail-closed when the
     reading_order sets differ, when translate_details do not cover all
     regions, or when a per-reading_order bbox pair differs (permutation
     guard, CALIB dsh r1 R1);
  2. per-pair similarity = 1 - Levenshtein/max_len (character level;
     stdlib implementations replicated from experiments/M2-TA3-B/
     measure_cer.py) on the raw strings and under the quality-thresholds
     §0 normalization (GATE scaling);
  3. empty-pair rule (registered, CALIB): both empty = 1.0, exactly one
     empty = 0.0; coverage precondition: >=1 non-empty pair else NO_DATA;
  4. gate verdict (normalized): median >= 0.95 AND min >= 0.70.

All numbers are DIRECTIONAL (single rerun pair, remote DeepSeek provider).
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

GATE = {"metric": "similarity_normalized", "median_min": 0.95, "min_min": 0.70}

# §5 dual-track discrimination (CALIB r1 R9): the track is inferred from the
# summaries' translate provider binding; an explicit --determinism-track
# declaration that contradicts it fails closed.  Markers mirror the runner
# (run_qualification.py::infer_determinism_track).
_REMOTE_BINDING_MARKERS = ("deepseek", "openai-compatible")
_MOCK_BINDING_MARKERS = ("mock", "deterministic", "stub", "fake")


def infer_track_from_summary(binding_text: str) -> str:
    """Infer the §5 track from a summary's provider_policy.translate text."""
    lowered = (binding_text or "").lower()
    if any(marker in lowered for marker in _MOCK_BINDING_MARKERS):
        return "mock"
    if any(marker in lowered for marker in _REMOTE_BINDING_MARKERS):
        return "remote"
    return "unknown"


def normalize(text: str) -> str:
    """quality-thresholds §0 normalization (identical to measure_cer.py)."""
    if not text:
        return ""
    text = text.replace("…", "...").replace("\u22ef", "...")
    text = "".join(text.split())
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
    """1 - Levenshtein/max_len; empty-pair rule: both empty=1.0, one empty=0.0."""
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return 1.0 - levenshtein(a, b) / max(len(a), len(b))


def translations_by_reading_order(summary: dict) -> dict[int, dict]:
    order = {r["region_id"]: r["reading_order"] for r in summary["regions"]}
    types = {r["region_id"]: r.get("region_type", "") for r in summary["regions"]}
    bboxes = {r["region_id"]: r.get("bbox") for r in summary["regions"]}
    out: dict[int, dict] = {}
    for detail in summary.get("translate_details", []):
        rid = detail["region_id"]
        if rid not in order:
            raise SystemExit(
                f"FATAL: translate_detail region_id {rid!r} not present in regions[] "
                "- summary is internally inconsistent"
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


def percentile(sorted_values: list[float], p: float) -> float | None:
    if not sorted_values:
        return None
    if len(sorted_values) == 1:
        return sorted_values[0]
    k = (len(sorted_values) - 1) * p
    f, c = math.floor(k), math.ceil(k)
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


def gate_verdict(median: float | None, minimum: float | None) -> str:
    if median is None or minimum is None:
        return "NO_DATA"
    return (
        "PASS"
        if median >= GATE["median_min"] and minimum >= GATE["min_min"]
        else "FAIL"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True)
    parser.add_argument(
        "--summaries-dir",
        default=str(REPO_ROOT / "verification/M2-TA3-B/phase2/ko-rerun/summaries"),
    )
    parser.add_argument(
        "--out-dir",
        default=str(REPO_ROOT / "verification/M2-TA3-B/phase2/ko-rerun/determinism"),
    )
    parser.add_argument(
        "--determinism-track", default="", choices=["", "remote", "mock"],
        help="explicit quality-thresholds §5 track declaration (CALIB r1 R9); "
        "fails closed when it contradicts the summaries' translate provider "
        "binding; empty default records the inferred track only",
    )
    args = parser.parse_args()

    summaries_dir = Path(args.summaries_dir)
    first = json.loads((summaries_dir / f"qual-{args.case}.json").read_text(encoding="utf-8"))
    second = json.loads(
        (summaries_dir / f"qual-{args.case}.rerun.json").read_text(encoding="utf-8")
    )
    # §5 dual-track control (CALIB r1 R9): fail-closed track check BEFORE any
    # scoring.  The gate caliber below is only valid when both runs bound the
    # same, remotely-sampling translate provider.
    binding_first = (first.get("provider_policy", {}) or {}).get("translate", "")
    binding_second = (second.get("provider_policy", {}) or {}).get("translate", "")
    inferred_first = infer_track_from_summary(binding_first)
    inferred_second = infer_track_from_summary(binding_second)
    if inferred_first == "unknown" or inferred_first != inferred_second:
        raise SystemExit(
            f"FATAL: {args.case} determinism track not determinable from the "
            f"summaries' translate bindings (first={inferred_first!r}, "
            f"second={inferred_second!r}) - refusing to score "
            "(quality-thresholds §5 dual-track rule: fail-closed)"
        )
    if args.determinism_track and args.determinism_track != inferred_first:
        raise SystemExit(
            f"FATAL: --determinism-track {args.determinism_track!r} contradicts "
            f"the summaries' translate binding (inferred {inferred_first!r}) "
            "(quality-thresholds §5 dual-track rule, CALIB r1 R9: fail-closed)"
        )
    t1 = translations_by_reading_order(first)
    t2 = translations_by_reading_order(second)
    ros1 = {r["reading_order"] for r in first["regions"]}
    ros2 = {r["reading_order"] for r in second["regions"]}
    if set(t1) != set(t2):
        raise SystemExit(
            f"FATAL: {args.case} reading_order sets differ between runs "
            f"{sorted(set(t1) ^ set(t2))} - alignment impossible"
        )
    if set(t1) != ros1 or set(t2) != ros2:
        raise SystemExit(
            f"FATAL: {args.case} translate_details do not cover all regions - "
            f"run1 dropped={sorted(ros1 - set(t1))}, run2 dropped={sorted(ros2 - set(t2))}"
        )
    pairs = []
    for ro in sorted(t1):
        a, b = t1[ro], t2[ro]
        if a["bbox"] != b["bbox"]:
            raise SystemExit(
                f"FATAL: {args.case} reading_order {ro} bbox differs between runs "
                f"{a['bbox']} != {b['bbox']} - alignment assumption violated"
            )
        tf, ts = a["translated_text"], b["translated_text"]
        nf, ns = normalize(tf), normalize(ts)
        status = (
            "empty_both" if not nf and not ns
            else "empty_one_side" if not nf or not ns
            else ("identical" if tf == ts else "variant")
        )
        pairs.append(
            {
                "reading_order": ro,
                "region_type": a["region_type"],
                "source_text": a["source_text"],
                "text_first": tf,
                "text_second": ts,
                "similarity_raw": round(similarity(tf, ts), 4),
                "similarity_normalized": round(similarity(nf, ns), 4),
                "status": status,
            }
        )
    nonempty = [p for p in pairs if p["status"] not in ("empty_both", "empty_one_side")]
    if not nonempty:
        verdict = "NO_DATA"
        stats_norm_all = distribution([p["similarity_normalized"] for p in pairs])
        stats_norm_ne = {"n": 0, "min": None, "median": None}
    else:
        stats_norm_all = distribution([p["similarity_normalized"] for p in pairs])
        stats_norm_ne = distribution([p["similarity_normalized"] for p in nonempty])
        verdict = gate_verdict(stats_norm_all["median"], stats_norm_all["min"])
    payload = {
        "task": "M2-TA3-B2-KO-RERUN",
        "measure": "reading_order-aligned translation similarity (remote-chain determinism gate, quality-thresholds §5 dual-track)",
        "case_id": args.case,
        "language": first["language"],
        "gate": GATE,
        "n_pairs": len(pairs),
        "n_pairs_nonempty": len(nonempty),
        "pairs": pairs,
        "stats": {
            "normalized_all_pairs": stats_norm_all,
            "normalized_nonempty": stats_norm_ne,
        },
        "gate_verdict_normalized": verdict,
        "determinism_track": {
            "declared": args.determinism_track or None,
            "inferred": inferred_first,
            "binding_first": binding_first,
            "binding_second": binding_second,
            "rule": (
                "quality-thresholds §5 footnote / CALIB r1 R9: remote sampling "
                "provider -> similarity track; mock/deterministic provider -> "
                "export sha bitwise track; declaration/binding mismatch -> fail-closed"
            ),
        },
        "export_sha_first": (first.get("export", {}) or {}).get("sha256", ""),
        "export_sha_second": (second.get("export", {}) or {}).get("sha256", ""),
        "export_sha_match": (
            bool((first.get("export", {}) or {}).get("sha256", ""))
            and (first.get("export", {}) or {}).get("sha256", "")
            == (second.get("export", {}) or {}).get("sha256", "")
        ),
        "note_export_track": (
            "export sha bitwise equality is the MOCK/DETERMINISTIC-track caliber; "
            "this run binds the REMOTE track (see determinism_track above, checked "
            "fail-closed against the provider binding) so the similarity gate above "
            "is the gate caliber and the export sha is recorded as supplementary data only"
        ),
        "directional_disclaimer": (
            "directional evidence: one rerun pair, remote DeepSeek provider, "
            "M2-TA3-B2-KO-RERUN; not a production determinism conclusion"
        ),
    }
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.case}-similarity.json"
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"[{args.case}] pairs={len(pairs)} nonempty={len(nonempty)} "
        f"norm(all) variant={stats_norm_all['n_variant']} min={stats_norm_all['min']} "
        f"median={stats_norm_all['median']} -> gate={verdict}"
    )
    print(
        f"[{args.case}] export sha match={payload['export_sha_match']} "
        "(supplementary; remote track gates on similarity)"
    )
    print(f"out -> {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
