"""M2-SFX-E2E-MATERIAL AC3: full-chain run for NEW pooled SFX-rich pages.

Reuses the VERIFIED qualification harness (experiments/M2-TA3-B/
run_qualification.py::run_case) verbatim — the new asset cases are passed
as manifest-style dicts whose ``page_path`` points at THIS worktree's
gitignored suite copy (BJ13/BJ14/BJ15, rendered by render_vol_pages.py at
DPI 150 from the TA2B official volume03.pdf, sha256 pinned below).

Differences from run_qualification.main():
  - case source: inline NEW_ASSET_CASES (not case-selection.json, which is
    a delivered M2-TA3-B artifact and stays read-only);
  - --sfx-policy translate + --meter-translation are FORCED (the task's
    user-ruling-4 configuration), so every run exercises the SFX gate
    release path end to end;
  - the determinism-track declaration is validated with the same
    fail-closed rule (quality-thresholds §5 / CALIB r1 R9).

Pixel discipline: same as the harness — crops/exports go to the
git-external pixel root (task-envs/M2-SFX-E2E-MATERIAL/pixels-new-assets),
never into the repo.  Key discipline: TA3B_TRANSLATE_API_KEY enters via
env only and is scrubbed from every persisted record (scrub_secrets).

Exit codes: 0 = all runs completed; 1 = at least one failure.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_HERE = Path(__file__).resolve().parent
_TA3B = REPO_ROOT / "experiments" / "M2-TA3-B"
for p in (str(REPO_ROOT / "src"), str(_TA3B), str(_HERE)):
    if p not in sys.path:
        sys.path.insert(0, p)

from run_qualification import (  # noqa: E402
    PIXEL_ROOT_DEFAULT,
    infer_determinism_track,
    dump_json,
    run_case,
)

PAGE_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official" / "vol03" / "pages"

#: SFX-rich pages selected in AC2 (visual scan 2026-10-02, see
#: verification/M2-SFX-E2E-MATERIAL/material-inventory.json):
#:   p0048  第19話 lead page — two huge handwritten vertical phone-ring SFX ピ一一ーン！
#:   p0060  第24話 lead page — three vertical newborn-cry SFX オギャァ (fragmented layout)
#:   p0159  第24話 follow-up — two vertical cry SFX (オギャァ x2, zoom-confirmed) + normal dialogue
NEW_ASSET_CASES = [
    {
        "case_id": "BJ13",
        "language": "ja",
        "family": "manual_source_page",
        "source_id": "vol03_p0048",
        "text_type": "sfx_dominant_unverified",
        "page_path": str(PAGE_ROOT / "vol03_p0048.png"),
        "page_sha256": "86eeb6c228b79765939de51959c56e0c5ecce9390a3884515f6e8a8cc04371d9",
        "tags": ["fragmented_sfx", "huge_text", "vertical_text", "complex_background"],
        "layout_type": "paged_manga",
        "reading_direction": "right_to_left",
    },
    {
        "case_id": "BJ14",
        "language": "ja",
        "family": "manual_source_page",
        "source_id": "vol03_p0060",
        "text_type": "sfx_dominant_unverified",
        "page_path": str(PAGE_ROOT / "vol03_p0060.png"),
        "page_sha256": "61dfeb2ff0fb765ffbb3186797c8973f2f2c762b0c4062a2c189777f3a545c27",
        "tags": ["fragmented_sfx", "huge_text", "vertical_text", "complex_background"],
        "layout_type": "paged_manga",
        "reading_direction": "right_to_left",
    },
    {
        "case_id": "BJ15",
        "language": "ja",
        "family": "manual_source_page",
        "source_id": "vol03_p0159",
        "text_type": "mixed_unverified",
        "page_path": str(PAGE_ROOT / "vol03_p0159.png"),
        "page_sha256": "3af0054184bacabf73baa140382ab087e8d668babc04cd74ac57d5a36c45a040",
        "tags": ["fragmented_sfx", "vertical_text", "low_contrast", "normal_dialogue", "multi_speaker"],
        "layout_type": "paged_manga",
        "reading_direction": "right_to_left",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", help="run only these case ids (repeatable)")
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    parser.add_argument(
        "--out-dir", dest="out_dir",
        default=str(REPO_ROOT / "verification" / "M2-SFX-E2E-MATERIAL" / "new-assets-run" / "summaries"),
    )
    parser.add_argument(
        "--pixel-root", default=str(PIXEL_ROOT_DEFAULT.parent / "M2-SFX-E2E-MATERIAL" / "pixels-new-assets"),
    )
    args = parser.parse_args()

    declared = "remote"
    inferred = infer_determinism_track()
    if declared != inferred:  # fail-closed BEFORE any setup (§5 / CALIB r1 R9)
        print(
            f"FATAL: declared track {declared!r} contradicts translate binding "
            f"(inferred {inferred!r})", file=sys.stderr,
        )
        return 2
    track_record = {
        "declared": declared,
        "inferred": inferred,
        "rule": "quality-thresholds §5 footnote / CALIB r1 R9 (fail-closed)",
    }

    if not os.environ.get("TA3B_TRANSLATE_API_KEY"):
        print("FATAL: TA3B_TRANSLATE_API_KEY not set (env only, never a file)", file=sys.stderr)
        return 2

    cases = NEW_ASSET_CASES
    if args.case:
        wanted = set(args.case)
        cases = [c for c in cases if c["case_id"] in wanted]
        missing = wanted - {c["case_id"] for c in cases}
        if missing:
            print(f"FATAL: unknown case ids: {sorted(missing)}", file=sys.stderr)
            return 2

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pixel_root = Path(args.pixel_root)
    pixel_root.mkdir(parents=True, exist_ok=True)

    failures = 0
    report = {
        "task": "M2-SFX-E2E-MATERIAL",
        "deliverable": "AC3 new-asset end-to-end (chiqui7 detect -> sfx gate translate -> DeepSeek -> DB)",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "device": args.device,
        "sfx_policy": "translate (forced; user ruling 2026-10-02 item 4)",
        "determinism_track": track_record,
        "harness": "experiments/M2-TA3-B/run_qualification.py::run_case (reused verbatim)",
        "cases": [],
    }
    for case in cases:
        print(f"[{case['case_id']}] start", flush=True)
        try:
            summary = run_case(
                case,
                pixel_root=pixel_root,
                device=args.device,
                max_regions=None,
                sfx_policy="translate",
                meter_translation=True,
                determinism_track=track_record,
            )
        except Exception as exc:  # noqa: BLE001
            import traceback

            summary = {
                "task": "M2-SFX-E2E-MATERIAL",
                "case_id": case["case_id"],
                "status": "HARNESS_EXCEPTION",
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(limit=5),
            }
            failures += 1
        pipeline_completed = (
            summary.get("run2", {}).get("status") == "completed"
            and summary.get("export", {}).get("status") == "OK"
        )
        if not pipeline_completed:
            failures += 1
        summary["pipeline_completed"] = pipeline_completed
        summary_path = out_dir / f"qual-{case['case_id']}.json"
        summary_path.write_text(dump_json(summary), encoding="utf-8")
        print(f"[{case['case_id']}] summary -> {summary_path}", flush=True)
        report["cases"].append(
            {
                "case_id": case["case_id"],
                "pipeline_completed": pipeline_completed,
                "region_count": len(summary.get("regions", [])),
                "sfx_region_count": sum(
                    1 for r in summary.get("regions", []) if r.get("region_type") == "sfx"
                ),
                "n_translated": sum(
                    1 for d in summary.get("translate_details", [])
                    if (d.get("translated_text") or "").strip()
                ),
                "export": summary.get("export", {}).get("status"),
                "attribution": summary.get("attribution", []),
                "wall_s": summary.get("wall_s"),
            }
        )

    report["failures"] = failures
    report["finished_at_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (out_dir / "new-asset-report.json").write_text(dump_json(report), encoding="utf-8")
    print(f"report -> {out_dir / 'new-asset-report.json'}")
    print(f"SUMMARY cases={len(cases)} failures={failures}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
