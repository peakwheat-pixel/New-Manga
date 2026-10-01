"""Build the SFX spot-check candidate sample list (M2-SFX-DETECT-EVAL AC2).

Stratified, seeded, fully disclosed sampling of KO-webtoon regions for the
ogkalu SFX status-quo spot check. READ-ONLY inputs (C1/C4 evidence, eval
manifest); the only output is the candidate list JSON.

Strata:
- A: SFX frames already CONFIRMED by the C1 user audit (11 frames, exact
  evidence boxes from spot-audit-sample.json) — 6 detected-as-FP frames
  (B1-U09/U12/U13, B2-U12/U14/U15) + 5 zero-detection frames (A1-U06
  onomatopoeia inside a pseudo-GT box + D-U01/07/08/09).
- B: UNAUDITED block-layer FP boxes from frames-export.json (78 boxes;
  the C1 audit sampled 30 of 108, of which 6 were SFX). Candidates where a
  detection landed on real unannotated text — prime SFX suspects. Seeded
  per-case selection, spread across all 10 cases.
- C: UNAUDITED zero-detection regions from the frozen C4 formal results
  (78 regions with n_det_block==0, minus the 10 D-layer audited; 62
  remain). Seeded per-case selection.

The candidate list is a SUPERSET: the final >=20-frame sample is frozen
only after the agent's visual confirmation pass (previews + grid overlay);
skipped candidates keep their skip reason in the verdict file. All counts
are directional (single AI annotator, no formal SFX GT).

Usage (from the worktree root):

  python experiments/M2-SFX-DETECT/build_sfx_sample.py \
      --frames-export "G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode/verification/M2-DOCTR-QUAL/spot-audit/data/frames-export.json" \
      --audit-sample "G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode/verification/M2-DOCTR-QUAL/spot-audit/spot-audit-sample.json" \
      --c4-results "G:/CODEX/New Manga.worktrees/M2-SFX-EVAL-zcode/verification/M2-DOCTR-QUAL/qualification/results-formal-manga_rt_detr_v2-cuda-seg05.json" \
      --manifest "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/eval-manifest.full.seg05.json" \
      --out experiments/M2-SFX-DETECT/sfx-sample-candidates.json
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

SEED = 20261001

# C1 user-audited SFX units (labeling-worksheet.csv verdict = SFX blind spot
# / GT blind spot with onomatopoeia content; see c1-spot-audit-report.md §1).
STRATUM_A_UNITS = [
    "B1-U09",  # K07 R007 저벅저벅 (footsteps) — detected as FP
    "B1-U12",  # K08 R025 푸흡 (panting, vertical) — detected as FP
    "B1-U13",  # K09 R071 하하 (laughter) — detected as FP
    "B2-U12",  # K07 R059 싸—아 (group shout) — detected as FP
    "B2-U14",  # K07 R107 덜컹 (clunk, partial letters) — detected as FP
    "B2-U15",  # K07 R123 뒤적뒤적 (rummaging) — detected as FP
    "A1-U06",  # K09 R014 끌끌.. (snicker) inside pseudo-GT box — zero raw det
    "D-U01",   # K03 R135 빠걸 x3 (whirr) — zero-det region
    "D-U07",   # K08 R041 빠악 (smash) — zero-det region
    "D-U08",   # K08 R047 콰직 (crunch, handwritten style) — zero-det region
    "D-U09",   # K08 R057 투두 (falling) — zero-det region
]

# Per-case quotas for strata B/C (10 KO cases; spread, SFX-plausible cases
# weighted by candidate counts: K01 poster-heavy, K03/K07/K08/K09 high).
STRATUM_B_QUOTA = {
    "K01": 3, "K02": 1, "K03": 3, "K04": 1, "K05": 1,
    "K06": 2, "K07": 3, "K08": 1, "K09": 2, "K10": 2,
}  # = 19
STRATUM_C_QUOTA = {
    "K01": 1, "K03": 2, "K05": 2, "K06": 1, "K07": 2,
    "K08": 2, "K09": 2, "K10": 2,
}  # = 14


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames-export", type=Path, required=True)
    parser.add_argument("--audit-sample", type=Path, required=True)
    parser.add_argument("--c4-results", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    fe = json.loads(args.frames_export.read_text(encoding="utf-8"))
    sa = json.loads(args.audit_sample.read_text(encoding="utf-8"))
    c4 = json.loads(args.c4_results.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    img_by_region = {
        (e["case_id"], e["region_index"]): e["image"] for e in manifest["regions"]
    }

    units_by_id = {u["unit_id"]: u for u in sa["units"]}

    def region_dir(case_id: str, region_index: int) -> str:
        return img_by_region[(case_id, region_index)]

    samples: list[dict] = []

    # --- Stratum A: C1 user-confirmed SFX frames -------------------------
    for uid in STRATUM_A_UNITS:
        u = units_by_id[uid]
        samples.append(
            {
                "sample_id": f"A__{uid}",
                "stratum": "A",
                "stratum_note": (
                    "C1 user-audited SFX frame (formal verdict in "
                    "labeling-worksheet.csv; directional evidence per C1 r2)"
                ),
                "unit_id": uid,
                "case_id": u["case_id"],
                "region_index": u["region_index"],
                "image": region_dir(u["case_id"], u["region_index"]),
                "sfx_prior_box_xyxy": u["review_box_xyxy"],
                "prior_box_provenance": (
                    "C1 spot-audit-sample.json review_box (user-audited)"
                ),
                "c1_expected": u["description"],
            }
        )

    # --- Stratum B: unaudited FP-box candidates --------------------------
    audited_boxes = {
        (u["case_id"], u["region_index"], tuple(round(v, 1) for v in u["review_box_xyxy"]))
        for u in sa["units"]
        if u["layer"] in ("B1", "B2")
    }
    fp_rows = [
        r for r in fe["frames"] if r["kind"] == "fp_block"
    ]
    cand_b = [
        r for r in fp_rows
        if (r["case_id"], r["region_index"], tuple(round(v, 1) for v in r["box_xyxy"]))
        not in audited_boxes
    ]
    by_case: dict[str, list[dict]] = {}
    for r in cand_b:
        by_case.setdefault(r["case_id"], []).append(r)
    rng = random.Random(SEED)
    picked_b: list[dict] = []
    for case_id in sorted(STRATUM_B_QUOTA):
        pool = by_case.get(case_id, [])
        rng.shuffle(pool)
        picked_b.extend(pool[: STRATUM_B_QUOTA[case_id]])
    for r in picked_b:
        samples.append(
            {
                "sample_id": f"B__{r['case_id']}_R{r['region_index']:03d}_d{r['det_index']}",
                "stratum": "B",
                "stratum_note": (
                    "unaudited block-layer FP box (frames-export.json); if the "
                    "box lands on SFX lettering visually -> blind-spot SFX "
                    "detection sample; otherwise skipped with reason"
                ),
                "unit_id": None,
                "case_id": r["case_id"],
                "region_index": r["region_index"],
                "image": region_dir(r["case_id"], r["region_index"]),
                "sfx_prior_box_xyxy": r["box_xyxy"],
                "prior_box_provenance": (
                    "ogkalu FP box (block layer, C4 formal run conf=0.5); "
                    "prior only, visual pass decides"
                ),
                "c1_expected": None,
                "fp_conf": r["conf"],
                "fp_layer": r["layer"],
            }
        )

    # --- Stratum C: unaudited zero-detection regions ---------------------
    d_audited = {
        (u["case_id"], u["region_index"]) for u in sa["units"] if u["layer"] == "D"
    }
    zero = [
        (p["case_id"], p["region_index"])
        for p in c4["per_region"]
        if p["n_det_block"] == 0 and (p["case_id"], p["region_index"]) not in d_audited
    ]
    by_case_c: dict[str, list] = {}
    for case_id, region_index in zero:
        by_case_c.setdefault(case_id, []).append((case_id, region_index))
    picked_c: list = []
    for case_id in sorted(STRATUM_C_QUOTA):
        pool = by_case_c.get(case_id, [])
        rng.shuffle(pool)
        picked_c.extend(pool[: STRATUM_C_QUOTA[case_id]])
    for case_id, region_index in picked_c:
        samples.append(
            {
                "sample_id": f"C__{case_id}_R{region_index:03d}",
                "stratum": "C",
                "stratum_note": (
                    "unaudited zero-detection region (C4 formal run "
                    "n_det_block==0); if visible SFX lettering exists -> "
                    "status-quo miss sample; otherwise skipped with reason"
                ),
                "unit_id": None,
                "case_id": case_id,
                "region_index": region_index,
                "image": region_dir(case_id, region_index),
                "sfx_prior_box_xyxy": None,
                "prior_box_provenance": None,
                "c1_expected": None,
            }
        )

    payload = {
        "schema": "m2-sfx-detect/sample-candidates@1",
        "task": "M2-SFX-DETECT-EVAL",
        "seed": SEED,
        "stratum_definition": {
            "A": "C1 user-audited SFX frames (11, exact evidence boxes)",
            "B": "unaudited block-layer FP boxes, seeded per-case quota",
            "C": "unaudited zero-detection regions, seeded per-case quota",
        },
        "quotas": {"B": STRATUM_B_QUOTA, "C": STRATUM_C_QUOTA},
        "inputs": {
            "frames_export": str(args.frames_export),
            "audit_sample": str(args.audit_sample),
            "c4_results": str(args.c4_results),
            "manifest": str(args.manifest),
        },
        "note": (
            "candidate superset; final >=20-frame SFX sample frozen after the "
            "agent visual confirmation pass; directional evidence only"
        ),
        "candidates": samples,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    n_by = {}
    for s in samples:
        n_by[s["stratum"]] = n_by.get(s["stratum"], 0) + 1
    print(f"candidates: {len(samples)} ({n_by}) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
