"""Compute the AC3 cross-model comparison (geometry, not judgment).

For every primary-frame SFX instance (agent-estimated boxes from
``sfx-spot-check-verdicts.json``) this script computes, from committed
inference payloads only:

- chiqui7 yolo11s-seg: best ``sfx``-class box (coverage of the SFX box +
  conf), and best any-class box;
- Kiuyha yolo26n: best ``text``-class box (coverage + conf);
- ogkalu baseline: best text-class box (coverage + conf) at harvest and
  whether any box met the primary 0.5 cut (from the AC2 payload).

The script computes geometry ONLY — whether an sfx-class box is a TRUE
SFX hit is the agent's visual call, recorded separately in the eval
report's comparison table (e.g. the K09_R071 sfx-class box on a HAND is
a false positive). Directional evidence, no formal GT.

Usage:

  python experiments/M2-SFX-DETECT/summarize_onnx_comparison.py \
      --verdicts experiments/M2-SFX-DETECT/sfx-spot-check-verdicts.json \
      --onnx experiments/M2-SFX-DETECT/onnx-sfx-frames.json \
      --ogkalu experiments/M2-SFX-DETECT/ogkalu-sfx-frames.json \
      --out experiments/M2-SFX-DETECT/onnx-sfx-comparison.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def coverage(det_box, sfx_box) -> float:
    if det_box is None:
        return 0.0
    ix0 = max(det_box[0], sfx_box[0])
    iy0 = max(det_box[1], sfx_box[1])
    ix1 = min(det_box[2], sfx_box[2])
    iy1 = min(det_box[3], sfx_box[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area = (sfx_box[2] - sfx_box[0]) * (sfx_box[3] - sfx_box[1])
    return inter / area if area else 0.0


def iou(a, b) -> float:
    if a is None or b is None:
        return 0.0
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


# R1 (DSH r1): three-way provenance of the REFERENCE (SFX) box, so the
# ogkalu column can never silently compare the detector against its own
# detection boxes (self-referential coverage inflates the baseline).
# - ogkalu_self_prior : reference coords ARE an ogkalu detection box
#   (6 C1-audited blind-spot FP units — the audited box IS the C4-run
#   ogkalu detection; 5 stratum-B FP priors)
# - c1_adjudicated    : reference coords are C1-user-adjudicated but NOT
#   an ogkalu detection (A1-U06: the pseudo-GT box around 끌끌..)
# - agent_estimated   : agent visual estimate on grid previews
C1_AUDITED_OGKALU_DETECTION_UNITS = {
    "B1-U09", "B1-U12", "B1-U13", "B2-U12", "B2-U14", "B2-U15"
}


def provenance_of(inst: dict, frame: dict) -> str:
    bp = inst.get("box_provenance") or ""
    if "ogkalu FP prior" in bp:
        return "ogkalu_self_prior"
    if "agent_estimate" in bp:
        return "agent_estimated"
    if frame.get("unit_id") in C1_AUDITED_OGKALU_DETECTION_UNITS:
        return "ogkalu_self_prior"  # audited box = C4-run ogkalu detection
    if frame.get("unit_id") == "A1-U06":
        return "c1_adjudicated"  # audited pseudo-GT box, not a detection
    return "agent_estimated"


def best(dets, cls_filter, sfx_box):
    best_cov, best_det = 0.0, None
    for d in dets:
        if cls_filter is not None and d["cls"] != cls_filter:
            continue
        cov = coverage(d["box_xyxy"], sfx_box)
        if cov > best_cov:
            best_cov, best_det = cov, d
    return best_cov, best_det


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verdicts", type=Path, required=True)
    parser.add_argument("--onnx", type=Path, required=True)
    parser.add_argument("--ogkalu", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    verdicts = json.loads(args.verdicts.read_text(encoding="utf-8"))
    onnx = json.loads(args.onnx.read_text(encoding="utf-8"))
    ogkalu = json.loads(args.ogkalu.read_text(encoding="utf-8"))

    rows = []
    for frame in verdicts["primary_frames"]:
        key = frame["region_key"]
        c = onnx["regions"][key]["chiqui7_yolo11s_seg"]["detections"]
        k = onnx["regions"][key]["kiuyha_manga_bubble_yolo"]["detections"]
        o = frame["ogkalu_detections_all"]
        for inst in frame["sfx_instances"]:
            box = inst["box_xyxy"]
            cov_c_sfx, det_c_sfx = best(c, "sfx", box)
            cov_c_any, det_c_any = best(c, None, box)
            cov_k_text, det_k_text = best(k, "text", box)
            cov_o_any, det_o_any = best(o, None, box)
            o_primary = any(
                coverage(d["box_xyxy"], box) >= 0.5 and d["conf_ge_primary"]
                for d in o
            )
            rows.append(
                {
                    "region_key": key,
                    "sample_id": frame["sample_id"],
                    "stratum": frame["stratum"],
                    "unit_id": frame.get("unit_id"),
                    "sfx_desc": inst["desc"],
                    "sfx_box_xyxy": box,
                    "reference_box_provenance": provenance_of(inst, frame),
                    "frame_verdict_ogkalu": frame["frame_verdict"],
                    "chiqui7_sfx_class": {
                        "coverage_of_sfx": round(cov_c_sfx, 3),
                        "iou": round(iou(det_c_sfx["box_xyxy"], box), 3) if det_c_sfx else 0.0,
                        "conf": det_c_sfx["conf"] if det_c_sfx else None,
                        "conf_ge_primary": (
                            det_c_sfx["conf_ge_primary"] if det_c_sfx else None
                        ),
                        "det_box_xyxy": det_c_sfx["box_xyxy"] if det_c_sfx else None,
                    },
                    "chiqui7_any_class": {
                        "coverage_of_sfx": round(cov_c_any, 3),
                        "iou": round(iou(det_c_any["box_xyxy"], box), 3) if det_c_any else 0.0,
                        "conf": det_c_any["conf"] if det_c_any else None,
                        "cls": det_c_any["cls"] if det_c_any else None,
                        "note": (
                            "single-side coverage criterion — dominated by "
                            "panel-class page-size boxes; NOT used for conclusions"
                        ),
                    },
                    "kiuyha_text_class": {
                        "coverage_of_sfx": round(cov_k_text, 3),
                        "iou": round(iou(det_k_text["box_xyxy"], box), 3) if det_k_text else 0.0,
                        "conf": det_k_text["conf"] if det_k_text else None,
                        "conf_ge_primary": (
                            det_k_text["conf_ge_primary"] if det_k_text else None
                        ),
                    },
                    "ogkalu_baseline": {
                        "coverage_of_sfx": round(cov_o_any, 3),
                        "iou": round(iou(det_o_any["box_xyxy"], box), 3) if det_o_any else 0.0,
                        "conf": det_o_any["conf"] if det_o_any else None,
                        "hit_at_primary_cut": o_primary,
                    },
                }
            )

    n = len(rows)
    n_self = sum(1 for r in rows if r["reference_box_provenance"] == "ogkalu_self_prior")
    non_self = [r for r in rows if r["reference_box_provenance"] != "ogkalu_self_prior"]
    n_ns = len(non_self)

    def bucket(rs, key, thr):
        return sum(1 for r in rs if r[key]["coverage_of_sfx"] >= thr)

    sfx_cov = [r["chiqui7_sfx_class"]["coverage_of_sfx"] for r in rows]
    sfx_ge_primary = sum(
        1
        for r in rows
        if r["chiqui7_sfx_class"]["conf_ge_primary"]
        and r["chiqui7_sfx_class"]["coverage_of_sfx"] >= 0.5
    )
    k_cov = [r["kiuyha_text_class"]["coverage_of_sfx"] for r in rows]
    o_cov = [r["ogkalu_baseline"]["coverage_of_sfx"] for r in rows]

    frames_with_sfxcls = {
        r["region_key"]
        for r in rows
        if r["chiqui7_sfx_class"]["coverage_of_sfx"] >= 0.5
    }
    frames_with_sfxcls_primary = {
        r["region_key"]
        for r in rows
        if r["chiqui7_sfx_class"]["conf_ge_primary"]
        and r["chiqui7_sfx_class"]["coverage_of_sfx"] >= 0.5
    }
    n_frames = len({r["region_key"] for r in rows})

    payload = {
        "schema": "m2-sfx-detect/onnx-sfx-comparison@2",
        "task": "M2-SFX-DETECT-EVAL",
        "evidence_strength": (
            "DIRECTIONAL — instance boxes are agent visual estimates / C1 "
            "user-adjudicated boxes; whether an sfx-class box is a true SFX "
            "hit is the agent's visual call (see report comparison table)"
        ),
        "reference_box_provenance_definition": {
            "ogkalu_self_prior": (
                "reference coords ARE an ogkalu detection box (6 C1-audited "
                "blind-spot FP units + 5 stratum-B FP priors) — ogkalu "
                "coverage on these is SELF-REFERENTIAL and excluded from "
                "the non-self subset"
            ),
            "c1_adjudicated": (
                "reference coords C1-user-adjudicated but NOT an ogkalu "
                "detection (A1-U06 pseudo-GT box around 끌끌..)"
            ),
            "agent_estimated": "agent visual estimate on grid previews",
        },
        "inputs": {
            "verdicts": str(args.verdicts),
            "onnx": str(args.onnx),
            "ogkalu": str(args.ogkalu),
        },
        "instance_summary": {
            "n_sfx_instances": n,
            "provenance_counts": {
                "ogkalu_self_prior": n_self,
                "non_self_referential": n_ns,
                "c1_adjudicated": sum(
                    1 for r in rows if r["reference_box_provenance"] == "c1_adjudicated"
                ),
                "agent_estimated": sum(
                    1 for r in rows if r["reference_box_provenance"] == "agent_estimated"
                ),
            },
            "ALL_instances": {
                "chiqui7_sfx_class_overlap>=0.5": bucket(rows, "chiqui7_sfx_class", 0.5),
                "chiqui7_sfx_class_overlap>=0.3": bucket(rows, "chiqui7_sfx_class", 0.3),
                "chiqui7_sfx_class_conf>=0.5_and_overlap>=0.5": sfx_ge_primary,
                "kiuyha_text_class_overlap>=0.5": bucket(rows, "kiuyha_text_class", 0.5),
                "kiuyha_text_class_overlap>=0.3": bucket(rows, "kiuyha_text_class", 0.3),
                "ogkalu_overlap>=0.5_SELF_REFERENTIAL": bucket(rows, "ogkalu_baseline", 0.5),
                "ogkalu_overlap>=0.3_SELF_REFERENTIAL": bucket(rows, "ogkalu_baseline", 0.3),
            },
            "NON_SELF_subset (R1)": {
                "n_instances": n_ns,
                "chiqui7_sfx_class_overlap>=0.5": bucket(non_self, "chiqui7_sfx_class", 0.5),
                "chiqui7_sfx_class_overlap>=0.3": bucket(non_self, "chiqui7_sfx_class", 0.3),
                "kiuyha_text_class_overlap>=0.5": bucket(non_self, "kiuyha_text_class", 0.5),
                "kiuyha_text_class_overlap>=0.3": bucket(non_self, "kiuyha_text_class", 0.3),
                "ogkalu_overlap>=0.5": bucket(non_self, "ogkalu_baseline", 0.5),
                "ogkalu_overlap>=0.3": bucket(non_self, "ogkalu_baseline", 0.3),
                "note": (
                    "fair-comparison subset; ogkalu 7/18 vs chiqui7 11/29 "
                    "reverses the headline direction (self-referential "
                    "inflation removed)"
                ),
            },
        },
        "frame_summary": {
            "n_primary_frames": n_frames,
            "frames_with_chiqui7_sfx_class_overlap>=0.5_any_conf": {
                "frames": len(frames_with_sfxcls),
                "fraction": round(len(frames_with_sfxcls) / n_frames, 4),
            },
            "frames_with_chiqui7_sfx_class_conf>=0.5": {
                "frames": len(frames_with_sfxcls_primary),
                "fraction": round(len(frames_with_sfxcls_primary) / n_frames, 4),
            },
        },
        "instances": rows,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8"
    )
    print(f"instances: {n} (self-referential {n_self}, non-self {n_ns})")
    print(
        f"chiqui7 sfx class: overlap>=0.5 {bucket(rows, 'chiqui7_sfx_class', 0.5)}/{n} "
        f"(conf>=0.5: {sfx_ge_primary}/{n}); "
        f"frames {len(frames_with_sfxcls)}/{n_frames} any-conf, "
        f"{len(frames_with_sfxcls_primary)}/{n_frames} conf>=0.5"
    )
    print(
        f"NON-SELF subset (n={n_ns}): ogkalu "
        f"{bucket(non_self, 'ogkalu_baseline', 0.5)}/{n_ns} vs chiqui7 sfx "
        f"{bucket(non_self, 'chiqui7_sfx_class', 0.5)}/{n} (all instances)"
    )
    print(
        f"kiuyha text class overlap>=0.5: "
        f"{bucket(rows, 'kiuyha_text_class', 0.5)}/{n}"
    )
    print(f"ogkalu overlap>=0.5 (SELF-REFERENTIAL): {bucket(rows, 'ogkalu_baseline', 0.5)}/{n}")
    print(f"comparison -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
