"""M2-SFX-GATE-T3 AC2：manifest.r4 入册（R3 底册只读 + BJ32-37 终裁框集并入）。

底册 = M2-SFX-ANNOTATE-R3 preannotate/manifest.r3.json（94 样本，只读）。
并入 = BJ32-35 四页 complete + 终裁框（consensus keep-union + arbiter keep）；
       BJ36/37 双 AI 终裁零 SFX（0 框）——schema.py:88-89 禁止 complete 空框，
       沿 R2 pre-bj25「零框负证据留痕」先例保持 pseudo 留底册不入 train-v4，
       判定闭环留痕 provenance.stage4t3（如实登记，0 也如实）。
新口径 = provenance.mode=ai-direct-annotation（Task AC2：非模型预标，conf 概念不适用，
       boxes_meta[].conf=null 显式登记——AI 直接标注首例）。
断言：94 样本 id 集不变；BJ32-37 底册原貌（pseudo/0 框）先断言后改写；
       终裁框与 judgments/consensus.json+arbiter/batch-1.json 逐位一致；
       全量 from_dict+validate 0 错误（BJ36/37 pseudo 0 框合法）。
产物 = training_data/sfx-v1/annotate-r4/manifest.r4.json（list 94，沿底册形态）。
"""
from __future__ import annotations

import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "experiments" / "M2-SFX-DATA-INFRA"))
from sfx_data_infra.schema import SampleRecord  # noqa: E402  （T1a 只读 import）

R3M = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode/training_data/sfx-v1/annotate-r3/preannotate/manifest.r3.json")
R4J = REPO / "training_data" / "sfx-v1" / "annotate-r4" / "judgments"
OUT = REPO / "training_data" / "sfx-v1" / "annotate-r4" / "manifest.r4.json"

KEEP_VERDICTS = ("keep-union", "keep")
PAGES = ["BJ32", "BJ33", "BJ34", "BJ35", "BJ36", "BJ37"]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def xyxy_to_polygon(v: list[float]) -> list[list[float]]:
    x1, y1, x2, y2 = v
    return [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]


def main() -> int:
    r3 = json.loads(R3M.read_text(encoding="utf-8"))
    assert isinstance(r3, list) and len(r3) == 94, f"底册形态异常: {type(r3)} len={len(r3)}"
    by_id = {s["sample_id"]: s for s in r3}
    assert len(by_id) == 94

    # 1) 终裁框集装载（consensus + arbiter）
    cons = json.loads((R4J / "consensus.json").read_text(encoding="utf-8"))
    arb = json.loads((R4J / "arbiter" / "batch-1.json").read_text(encoding="utf-8"))
    arb_by_id = {j["id"]: j for j in arb["judgments"]}

    final: dict[str, list[dict]] = {}  # page -> [meta]
    for c in cons["consensus"]:
        assert c["verdict"] == "keep-union" and c["iou_ab"] >= 0.5
        final.setdefault(c["page"], []).append({
            "unit_id": c["id"], "verdict": "keep-union", "reviewer": "codex+agy-consensus",
            "conf": None, "iou_ab": c["iou_ab"], "xyxy": c["union_xyxy"],
            "rationale": f"a: {c['rationale_codex']} ｜ b: {c['rationale_agy']}",
        })
    for d in json.loads((R4J / "divergence.json").read_text(encoding="utf-8"))["divergence"]:
        assert d["status"].startswith("arbiter-")
        vid = d["id"]
        a = arb_by_id[vid]
        assert a["verdict"] == d["status"].removeprefix("arbiter-")
        assert a["xyxy"] == d["xyxy"], f"{vid}: arbiter xyxy 与 divergence 不一致"
        if a["verdict"] == "keep":
            final.setdefault(d["page"], []).append({
                "unit_id": vid, "verdict": "keep", "reviewer": "arbiter",
                "conf": None, "xyxy": a["xyxy"], "rationale": a["rationale"],
            })
        else:
            final.setdefault(d["page"], []).append({
                "unit_id": vid, "verdict": a["verdict"], "reviewer": "arbiter",
                "conf": None, "xyxy": a["xyxy"], "rationale": a["rationale"],
            })
    # 页内序：按 unit_id（与判定文件可对读）
    for pg in final:
        final[pg].sort(key=lambda m: m["unit_id"])

    expected_boxes = {"BJ32": 3, "BJ33": 3, "BJ34": 3, "BJ35": 6, "BJ36": 0, "BJ37": 0}
    kept = {pg: [m for m in final.get(pg, []) if m["verdict"] in KEEP_VERDICTS]
            for pg in PAGES}
    for pg, n in expected_boxes.items():
        assert len(kept[pg]) == n, f"{pg}: 入册框 {len(kept[pg])} != 期望 {n}"

    # 2) 底册原貌断言（BJ32-37 当前=pseudo 0 框 asset_case）
    for pg in PAGES:
        s = by_id[f"pre-{pg.lower()}"]
        assert s["annotation_status"] == "pseudo" and len(s["boxes"]) == 0, f"{pg} 底册非 pseudo 0 框"
        assert s["provenance"]["type"] == "asset_case"

    # 3) 改写 BJ32-35 complete；BJ36/37 pseudo 留痕
    r4 = copy.deepcopy(r3)
    for pg in PAGES:
        s = next(x for x in r4 if x["sample_id"] == f"pre-{pg.lower()}")
        prov = s["provenance"]
        s["provenance"]["mode"] = "ai-direct-annotation"  # 新口径顶层字段（ask 指定名）
        s["provenance"]["quality_note"] = (
            "AI 直接标注首例（R3-MISS 补画，T3 AC2 2026-10-05）：双 AI 独立看整页画 SFX 框"
            "（无模型预标，conf 概念不适用）→IoU>=0.5 比对→分歧第三方仲裁（重看图）→终裁框集。"
            "human_review=false 沿 R3 口径。")
        s["provenance"]["stage4t3"] = {
            "action": "completed",
            "mode": "ai-direct-annotation",
            "judgments_sources": ["judgments/a/", "judgments/b/", "judgments/consensus.json",
                                  "judgments/divergence.json", "judgments/arbiter/batch-1.json"],
            "matching": "IoU>=0.5 贪心（gate-definition §3.1 同值）；consensus 入册框=双方框并集",
            "verdict_dist": {k: sum(1 for m in final.get(pg, []) if m["verdict"] == k)
                             for k in ("keep-union", "keep", "delete")},
            "pages_note": {
                "BJ36": "双 AI 独立标注+仲裁闭环判定全页零 SFX（b 2 框均判 delete：规整竖椭圆"
                        "气泡内规整细笔ハァ，R2-BJ17-B02 容器判例）——0 框负证据。",
                "BJ37": "双 AI 独立标注共识零 SFX（a/b 均 0 框）——0 框负证据。",
            },
            "zero_box_note": ("BJ36/37 终裁 0 框：schema.py:88-89 仅 pseudo 允许空框，沿 R2 "
                              "pre-bj25 零框负证据先例保持 pseudo 留底册、不入 train-v4 训练 "
                              "manifest；complete 空框不可表达为 schema 如实登记。"),
        }
        if pg in ("BJ32", "BJ33", "BJ34", "BJ35"):
            s["annotation_status"] = "complete"
            s["boxes"] = [{"polygon": xyxy_to_polygon(m["xyxy"]), "cls": "sfx",
                           "text": None, "occluded": False} for m in kept[pg]]
            prov["boxes_meta"] = [
                {"unit_id": m["unit_id"], "conf": m["conf"], "sources": ["ai-direct"],
                 "texts": [], "verdict": m["verdict"], "reviewer": m["reviewer"],
                 "rationale": m["rationale"],
                 **({"iou_ab": m["iou_ab"]} if "iou_ab" in m else {})}
                for m in kept[pg]]
        else:
            prov["stage4t3"]["action"] = "completed-zero-box"

    # 4) schema 全量校验（94 from_dict+validate 0 错误）
    errors = []
    for m in r4:
        rec = SampleRecord.from_dict(m)
        errors += [f"{rec.sample_id}: {e}" for e in rec.validate()]
    assert not errors, f"schema 校验失败 {len(errors)} 项: {errors[:5]}"
    # BJ32-35 单独复核 complete 非空
    for pg in ("BJ32", "BJ33", "BJ34", "BJ35"):
        rec = SampleRecord.from_dict(next(x for x in r4 if x["sample_id"] == f"pre-{pg.lower()}"))
        assert rec.annotation_status == "complete" and len(rec.boxes) > 0

    OUT.write_text(json.dumps(r4, ensure_ascii=False, indent=1), encoding="utf-8")
    n_complete = sum(1 for x in r4 if x["annotation_status"] == "complete")
    n_boxes = sum(len(x["boxes"]) for x in r4)
    print(f"[manifest.r4] 94 样本写入 {OUT}")
    print(f"[manifest.r4] BJ32-35 complete（{sum(len(kept[p]) for p in ('BJ32','BJ33','BJ34','BJ35'))} 框）"
          f"+ BJ36/37 pseudo 零框负证据留痕；全册 complete={n_complete} 总框={n_boxes}")
    print(f"[manifest.r4] schema from_dict+validate 94/94 0 错误")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
