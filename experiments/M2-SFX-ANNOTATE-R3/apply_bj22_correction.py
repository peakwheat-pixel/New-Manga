"""Apply DSH r1 C1 correction: R2-BJ22-B01 (pre-bj22 box1) polygon -> arbiter fix_hint.

仲裁终裁 correct：候选宽框 [1052.8,0.3,1863.4,559.0] 只碰到椭圆左缘，真实 SFX 主体
x≈1840-2100，fix_hint_xyxy_page=[1840,60,2100,570]。本脚本把该落框应用到
manifest.r3.json（DSH r1 P2-1 条件 C1 处置①），随后由 stage2_finalize_r3.py
--step split/yolo/summary 重出数据集。留痕：boxes_meta.quality_note +
provenance.stage3r3.correction_applied。可重复执行（幂等）。
"""
from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path("training_data/sfx-v1/annotate-r3/preannotate/manifest.r3.json")
FIX_HINT = [1840.0, 60.0, 2100.0, 570.0]  # arbiter fix_hint_xyxy_page（x0,y0,x1,y1）


def main() -> None:
    samples = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hit = 0
    for s in samples:
        if s.get("sample_id") != "pre-bj22":
            continue
        poly = [[FIX_HINT[0], FIX_HINT[1]], [FIX_HINT[2], FIX_HINT[1]],
                [FIX_HINT[2], FIX_HINT[3]], [FIX_HINT[0], FIX_HINT[3]]]
        applied = False
        for i, b in enumerate(s["boxes"]):
            if b.get("polygon") == [[1052.8, 0.3], [1863.4, 0.3], [1863.4, 559.0], [1052.8, 559.0]]:
                b["polygon"] = poly
                applied = True
                meta = (s.get("boxes_meta") or [{}] * len(s["boxes"]))[i]
                meta["quality_note"] = (
                    "DSH r1 C1 落框：仲裁 fix_hint [1840,60,2100,570] 应用（原候选宽框仅碰椭圆左缘，"
                    "宽向交集 23px，框内主体为手术室场景）；coordinates_changed=true"
                )
                if s.get("boxes_meta"):
                    s["boxes_meta"][i] = meta
        pr = s.setdefault("provenance", {}).setdefault("stage3r3", {})
        pr["correction_applied"] = {
            "unit_id": "R2-BJ22-B01",
            "fix_hint_xyxy_page": FIX_HINT,
            "applied_by": "experiments/M2-SFX-ANNOTATE-R3/apply_bj22_correction.py（DSH r1 P2-1 条件 C1 处置①）",
            "applied": applied,
        }
        if s.get("revision"):
            s["revision"]["correction_applied"] = True
        hit += 1 if applied else 0
    MANIFEST.write_text(json.dumps(samples, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"pre-bj22 correction applied boxes={hit}")


if __name__ == "__main__":
    main()
