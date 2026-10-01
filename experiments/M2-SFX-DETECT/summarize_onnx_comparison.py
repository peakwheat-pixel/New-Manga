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
                    "sfx_desc": inst["desc"],
                    "sfx_box_xyxy": box,
                    "frame_verdict_ogkalu": frame["frame_verdict"],
                    "chiqui7_sfx_class": {
                        "coverage_of_sfx": round(cov_c_sfx, 3),
                        "conf": det_c_sfx["conf"] if det_c_sfx else None,
                        "conf_ge_primary": (
                            det_c_sfx["conf_ge_primary"] if det_c_sfx else None
                        ),
                        "det_box_xyxy": det_c_sfx["box_xyxy"] if det_c_sfx else None,
                    },
                    "chiqui7_any_class": {
                        "coverage_of_sfx": round(cov_c_any, 3),
                        "conf": det_c_any["conf"] if det_c_any else None,
                        "cls": det_c_any["cls"] if det_c_any else None,
                    },
                    "kiuyha_text_class": {
                        "coverage_of_sfx": round(cov_k_text, 3),
                        "conf": det_k_text["conf"] if det_k_text else None,
                        "conf_ge_primary": (
                            det_k_text["conf_ge_primary"] if det_k_text else None
                        ),
                    },
                    "ogkalu_baseline": {
                        "coverage_of_sfx": round(cov_o_any, 3),
                        "conf": det_o_any["conf"] if det_o_any else None,
                        "hit_at_primary_cut": o_primary,
                    },
                }
            )

    n = len(rows)
    sfx_cov = [r["chiqui7_sfx_class"]["coverage_of_sfx"] for r in rows]
    sfx_ge_primary = sum(
        1
        for r in rows
        if r["chiqui7_sfx_class"]["conf_ge_primary"]
        and r["chiqui7_sfx_class"]["coverage_of_sfx"] >= 0.5
    )
    sfx_any = sum(1 for c in sfx_cov if c >= 0.5)
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
        "schema": "m2-sfx-detect/onnx-sfx-comparison@1",
        "task": "M2-SFX-DETECT-EVAL",
        "evidence_strength": (
            "DIRECTIONAL — instance boxes are agent visual estimates; "
            "whether an sfx-class box is a true SFX hit is the agent's "
            "visual call (see report comparison table)"
        ),
        "inputs": {
            "verdicts": str(args.verdicts),
            "onnx": str(args.onnx),
            "ogkalu": str(args.ogkalu),
        },
        "instance_summary": {
            "n_sfx_instances": n,
            "chiqui7_sfx_class_any_conf": {
                "instances_with_overlap>=0.5": sfx_any,
                "instances_with_overlap>=0.3": sum(1 for c in sfx_cov if c >= 0.3),
                "fraction_ge_0.5": round(sfx_any / n, 4) if n else None,
                "fraction_ge_0.3": round(sum(1 for c in sfx_cov if c >= 0.3) / n, 4) if n else None,
            },
            "chiqui7_sfx_class_conf>=0.5_and_overlap>=0.5": {
                "instances": sfx_ge_primary,
                "fraction": round(sfx_ge_primary / n, 4) if n else None,
            },
            "kiuyha_text_class_overlap>=0.5": {
                "instances": sum(1 for c in k_cov if c >= 0.5),
                "instances_with_overlap>=0.3": sum(1 for c in k_cov if c >= 0.3),
                "fraction_ge_0.5": round(sum(1 for c in k_cov if c >= 0.5) / n, 4) if n else None,
            },
            "ogkalu_overlap>=0.5": {
                "instances": sum(1 for c in o_cov if c >= 0.5),
                "instances_with_overlap>=0.3": sum(1 for c in o_cov if c >= 0.3),
                "fraction_ge_0.5": round(sum(1 for c in o_cov if c >= 0.5) / n, 4) if n else None,
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
    print(f"instances: {n}")
    print(
        f"chiqui7 sfx class: overlap>=0.5 {sfx_any}/{n} "
        f"(conf>=0.5: {sfx_ge_primary}/{n}); "
        f"frames {len(frames_with_sfxcls)}/{n_frames} any-conf, "
        f"{len(frames_with_sfxcls_primary)}/{n_frames} conf>=0.5"
    )
    print(
        f"kiuyha text class overlap>=0.5: "
        f"{sum(1 for c in k_cov if c >= 0.5)}/{n}"
    )
    print(f"ogkalu overlap>=0.5: {sum(1 for c in o_cov if c >= 0.5)}/{n}")
    print(f"comparison -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
