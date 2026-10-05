"""M2-SFX-T4-SWITCH AC1: compare the v2b arm against the chiqui7 control arm.

Reads the two run_qualification summaries (same page BJ06, same arguments,
same harness; the only difference is the SFX weights inside the repoint
window) and produces the AC1 verdict artifact:

- pipeline completion / stage statuses on both arms;
- **new-failure count** (the AC1 hard assertion): failures/defect
  attributions present on the v2b arm but ABSENT on the chiqui7 arm — must
  be 0;
- box-set differences are reported as DIRECTIONAL evidence only (single
  page, no SFX GT — the E2E-MATERIAL evidence caliber applies);
- chain-contract sanity: the detect->translate chain stays fail-closed
  legal (a zero-candidate page would be a legal empty input, not a crash).

Usage: python compare_g7_arms.py  (paths are the fixed AC1 layout)
Exit 0 = new-failure count 0 and both arms pipeline-completed; 1 otherwise.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAW = Path(__file__).resolve().parents[2] / "verification" / "M2-SFX-T4-SWITCH" / "raw"


def load_summary(side: str) -> dict:
    path = RAW / f"g7-smoke-{side}" / "summaries" / "qual-BJ06.json"
    return json.loads(path.read_text(encoding="utf-8"))


def load_report(side: str) -> dict:
    path = RAW / f"g7-smoke-{side}" / "summaries" / "qual-report.json"
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    chiq = load_summary("chiqui7")
    v2b = load_summary("v2b")

    def stage_stats(summary: dict) -> dict:
        stages = summary.get("stages", {})
        return {name: entry.get("status") for name, entry in stages.items()}

    def attributions(summary: dict) -> set[str]:
        return {a for a in summary.get("attribution", []) if isinstance(a, str)}

    def sfx_and_speech(summary: dict) -> tuple[int, int, list[dict]]:
        regions = summary.get("regions", [])
        sfx = [r for r in regions if str(r.get("region_type", "")).lower() == "sfx" or str(r.get("label", "")).startswith("sfx-")]
        return len(regions), len(sfx), regions

    def translate_stats(summary: dict) -> dict:
        details = summary.get("translate_details", [])
        n_nonempty = sum(1 for d in details if str(d.get("translated_text", "")).strip())
        sfx_rows = [d for d in details if str(d.get("region_type", "")).lower() == "sfx" or str(d.get("label", "")).startswith("sfx-")]
        return {
            "rows": len(details),
            "nonempty_translations": n_nonempty,
            "sfx_rows": len(sfx_rows),
            "sfx_nonempty": sum(1 for d in sfx_rows if str(d.get("translated_text", "")).strip()),
        }

    chiq_stages, v2b_stages = stage_stats(chiq), stage_stats(v2b)
    chiq_attr, v2b_attr = attributions(chiq), attributions(v2b)
    new_failures = sorted(v2b_attr - chiq_attr)
    resolved = sorted(chiq_attr - v2b_attr)

    chiq_n, chiq_sfx, chiq_regions = sfx_and_speech(chiq)
    v2b_n, v2b_sfx, v2b_regions = sfx_and_speech(v2b)

    # directional box-set difference: match regions by IoU-free label/type
    # multiset first, then per-type counts (no GT — nothing here is a quality
    # gate, per the T3 directional discipline).
    def type_counts(regions: list[dict]) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in regions:
            t = str(r.get("region_type", r.get("label", "?")))
            out[t] = out.get(t, 0) + 1
        return dict(sorted(out.items()))

    comparison = {
        "task": "M2-SFX-T4-SWITCH",
        "ac": "AC1 G7 compare: v2b repoint arm vs chiqui7 control arm (BJ06, policy=translate)",
        "arms": {
            "chiqui7": {
                "summary": str(RAW / "g7-smoke-chiqui7" / "summaries" / "qual-BJ06.json"),
                "pipeline_completed": chiq.get("pipeline_completed"),
                "stages": chiq_stages,
                "region_count": chiq_n,
                "sfx_region_count": chiq_sfx,
                "region_type_counts": type_counts(chiq_regions),
                "translate": translate_stats(chiq),
                "export": chiq.get("export", {}),
                "attribution": sorted(chiq_attr),
            },
            "v2b": {
                "summary": str(RAW / "g7-smoke-v2b" / "summaries" / "qual-BJ06.json"),
                "pipeline_completed": v2b.get("pipeline_completed"),
                "stages": v2b_stages,
                "region_count": v2b_n,
                "sfx_region_count": v2b_sfx,
                "region_type_counts": type_counts(v2b_regions),
                "translate": translate_stats(v2b),
                "export": v2b.get("export", {}),
                "attribution": sorted(v2b_attr),
            },
        },
        "verdict": {
            "new_failures_v2b_vs_chiqui7": new_failures,
            "new_failure_count": len(new_failures),
            "resolved_attributions": resolved,
            "both_pipeline_completed": bool(chiq.get("pipeline_completed") and v2b.get("pipeline_completed")),
            "fail_closed_chain_legal": "defect:detect-crash" not in v2b_attr
            and v2b.get("run2", {}).get("status") in ("completed", "SKIPPED"),
            "box_set_difference_caliber": "directional (single page, no SFX GT; E2E-MATERIAL evidence caliber)",
        },
    }
    out_path = RAW / "g7-compare.json"
    out_path.write_text(json.dumps(comparison, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(comparison["verdict"], ensure_ascii=False, indent=2))
    print(f"compare -> {out_path}")
    ok = (
        comparison["verdict"]["new_failure_count"] == 0
        and comparison["verdict"]["both_pipeline_completed"]
        and comparison["verdict"]["fail_closed_chain_legal"]
    )
    print("AC1 COMPARE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
