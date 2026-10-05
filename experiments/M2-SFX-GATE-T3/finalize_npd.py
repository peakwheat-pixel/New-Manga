"""M2-SFX-GATE-T3 AC3 npd 定稿：分歧仲裁回写 + npd-gt.json + 派生 GT 交集/差集统计。

仲裁者=入册会话独立标准（逐单元叠框预览+原页实看），判据四条（不引用任何既有 GT 坐标）：
  ①字形艺术化/效果字形态（vs 规整印刷+语法句）
  ②容器语义内容（对白气泡/解说带/物件）→ 非 SFX
  ③画面线稿/动作线（无字形结构）→ 非 SFX
  ④实例粒度（连续紧贴字串=一实例；一框多独立实例=粒度错误）
处置枚举：
  keep            单方候选指向真实 SFX，框入册
  keep-merged     与对方单元同目标 IoU<0.5 配对失败（小框敏感/粒度差），定稿框入册
                  （定稿框=union 或 correct 指定框），对方记 delete-duplicate
  delete-duplicate 同目标冗余（对方框/合并框已承接）
  delete          非 SFX（判据①②③）或框内无字形
  correct         是 SFX 但框需修（定稿框=修正框）

仲裁终裁档案（DSH r1 P2-1）：51 单元 verdict/final_xyxy/rationale 全文在
npd-judgments/arbiter/batch-1.json（与 AC2 annotate-r4/judgments/arbiter/batch-1.json
同构）；本脚本只读取该档案并断言其与 divergence 记录逐单元一致，不再内嵌终裁常量。
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NPJ = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-judgments"
GT_OUT = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-gt.json"
R3M = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode/training_data/sfx-v1/annotate-r3/preannotate/manifest.r3.json")
IOU_MATCH = 0.5

# ---------------------------------------------------------------------------
# 仲裁终裁表已导出为独立档案：npd-judgments/arbiter/batch-1.json（51 单元
# verdict/final_xyxy/rationale，与 AC2 annotate-r4/judgments/arbiter/batch-1.json 同构）。
# 本脚本只读取该档案并断言其与 divergence 记录逐单元一致（DSH r1 P2-1），
# 不再内嵌终裁常量。
# ---------------------------------------------------------------------------

# keep-merged 配对表（定稿框并入方 ← 被承接方）
MERGE_PAIRS = [
    ("R4-pre-k01-D00", "R4-pre-k01-D08"), ("R4-pre-k01-D01", "R4-pre-k01-D10"),
    ("R4-pre-k01-D02", "R4-pre-k01-D11"), ("R4-pre-k01-D04", "R4-pre-k01-D13"),
    ("R4-pre-k02-D00", "R4-pre-k02-D03"), ("R4-pre-k02-D01", "R4-pre-k02-D04"),
    ("R4-pre-k02-D02", "R4-pre-k02-D05"), ("R4-pre-k08-D00", "R4-pre-k08-D03"),
    ("R4-pre-k09-D00", "R4-pre-k09-D09"),
]


def iou(a, b) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua


def main() -> int:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    div = json.loads((NPJ / "divergence.json").read_text(encoding="utf-8"))
    cons = json.loads((NPJ / "consensus.json").read_text(encoding="utf-8"))

    # 1) 仲裁终裁档案装载+断言（对齐 stage_r4_manifest.py:52/67-68 模式）
    arb = json.loads((NPJ / "arbiter" / "batch-1.json").read_text(encoding="utf-8"))
    arb_by_id = {j["id"]: j for j in arb["judgments"]}
    assert len(arb_by_id) == len(arb["judgments"]), "arbiter batch-1 ID 重号"
    ids = [u["id"] for u in div["divergence"]]
    assert len(set(ids)) == len(ids), "divergence ID 重号"
    assert set(arb_by_id) == set(ids), (
        f"仲裁档案与分歧单元失配: 缺 {set(ids)-set(arb_by_id)} 多 {set(arb_by_id)-set(ids)}")
    for pair in MERGE_PAIRS:
        assert arb_by_id[pair[0]]["verdict"] == "keep-merged"
        assert arb_by_id[pair[1]]["verdict"] == "delete-duplicate"
    for u in div["divergence"]:
        a = arb_by_id[u["id"]]
        assert a["page"] == u["page"] and a["proposer"] == u["proposer"], u["id"]
        assert a["xyxy"] == u["xyxy"], f"{u['id']}: arbiter xyxy 与 divergence 不一致"
        if u.get("status", "").startswith("arbiter-"):  # 已回写态（重跑）：逐单元一致
            assert a["verdict"] == u["status"].removeprefix("arbiter-"), u["id"]
            assert a["rationale"] == u["arbiter_rationale"], u["id"]
            assert a.get("final_xyxy") == u.get("final_xyxy"), u["id"]

    # 2) 回写 divergence 状态 + 仲裁 rationale（终裁唯一来源=arbiter/batch-1.json）
    for u in div["divergence"]:
        v = arb_by_id[u["id"]]
        u["status"] = "arbiter-" + v["verdict"]
        u["arbiter_rationale"] = v["rationale"]
        if "final_xyxy" in v:
            u["final_xyxy"] = v["final_xyxy"]
    div["n_arbitrated"] = len(arb_by_id)
    div["arbiter"] = ("入册会话独立标准（逐单元叠框预览/高清复核+原页实看；判据=字形艺术化/"
                      "容器语义/画面线稿/实例粒度四条，不引用任何既有 GT 坐标；"
                      "R3 仲裁先例容器判例沿用）；npd-judgments/arbiter/batch-1.json")
    div["arbitrated_at_utc"] = now
    (NPJ / "divergence.json").write_text(
        json.dumps(div, ensure_ascii=False, indent=1), encoding="utf-8")

    # 3) npd-gt.json：共识 union 框 + 分歧定稿框（keep/keep-merged/correct）
    pages: dict[str, dict] = {}
    for c in cons["consensus"]:
        pg = pages.setdefault(c["page"], {"boxes": []})
        pg["boxes"].append({
            "xyxy": c["union_xyxy"],
            "rationale": f"consensus IoU={c['iou_ab']}｜a: {c['rationale_codex']}｜b: {c['rationale_agy']}",
            "chain": f"{c['id']}=keep-union",
        })
    for u in div["divergence"]:
        if u["status"] in ("arbiter-keep", "arbiter-keep-merged", "arbiter-correct"):
            pg = pages.setdefault(u["page"], {"boxes": []})
            pg["boxes"].append({
                "xyxy": arb_by_id[u["id"]]["final_xyxy"],
                "rationale": (f"divergence({u['proposer']})｜{arb_by_id[u['id']]['rationale']}"),
                "chain": f"{u['id']}={u['status']}",
            })
    dist = Counter(u["status"] for u in div["divergence"])

    # 4) 派生 GT 交集/差集统计（IoU>=0.5 同页贪心）
    m3 = json.loads(R3M.read_text(encoding="utf-8"))
    by_sid = {s["sample_id"]: s for s in m3}
    stats: dict[str, dict] = {}
    tot = Counter()
    for pg, d in sorted(pages.items()):
        s = by_sid[pg]
        assert s["annotation_status"] == "complete" and s["provenance"]["type"] == "asset_case"
        derived = [[b["polygon"][0][0], b["polygon"][0][1],
                    b["polygon"][2][0], b["polygon"][2][1]] for b in s["boxes"]]
        npd = [b["xyxy"] for b in d["boxes"]]
        pairs, only_der, only_npd = _match(derived, npd)
        stats[pg] = {
            "page_wh": [s["image"]["width"], s["image"]["height"]],
            "derived_gt": len(derived), "npd_gt": len(npd),
            "matched_iou05": len(pairs),
            "derived_only": len(only_der), "npd_only": len(npd) - len(pairs),
            "matched_iou_mean": round(sum(p[0] for p in pairs) / len(pairs), 4) if pairs else 0.0,
            "matched_pairs": [{"iou": round(v, 4), "derived_xyxy": dv, "npd_xyxy": nv}
                              for v, dv, nv in pairs],
            "derived_only_xyxy": [dv for _v, dv in only_der],
            "npd_only_xyxy": [nv for _v, nv in only_npd],
        }
        tot["derived"] += len(derived)
        tot["npd"] += len(npd)
        tot["matched"] += len(pairs)
    summary = {
        "derived_total": tot["derived"], "npd_total": tot["npd"],
        "matched": tot["matched"],
        "derived_only": tot["derived"] - tot["matched"],
        "npd_only": tot["npd"] - tot["matched"],
        "note": ("交集=双方各自独立标注在同一视觉目标上命中（IoU>=0.5）；"
                 "差集两向=GT 偏差度量（derived_only=AI 直接标注发现派生 GT 之外的目标 "
                 "或派生检出粒度/定位差；npd_only 同理反向）"),
    }

    gt_doc = {
        "kind": "sfx-gate-t3/npd-gt@1",
        "purpose": ("AC3 KO 非派生 GT 切片定稿：双 AI 独立整页标注（隔离纪律：任务书零既有"
                    "坐标，无模型输出/预标注/既有 GT 引用）→IoU>=0.5 比对→分歧第三方仲裁"
                    "（重看图）→本文件为唯一非派生 GT 事实源"),
        "generated_at_utc": now,
        "tool": "experiments/M2-SFX-GATE-T3/{compare_judgments.py,finalize_npd.py}",
        "isolation_discipline": {
            "task_brief_leak_check": "PASS（标注任务书不含任何既有框坐标）",
            "arbiter_independence": "仲裁判据四条不含既有 GT 坐标引用（见 tool docstring）",
            "coincidence_evidence": ("pre-k08 D00=a 框 [235,6048,326,6300] 与 R2 confirm 派生框 "
                                     "[233.4,6046.4,330.9,6301.1] 独立重合（IoU≈0.92）、pre-k08 D07=b 框与"
                                     "派生框 [609.4,44114,645.9,44213.6] 独立重合——可读作双 AI 独立标注"
                                     "客观性旁证亦可读作泄漏信号，双向解释、决定性不足；隔离判定以 "
                                     "task_brief_leak_check（作者自查）+复核产物级间接验证为准"
                                     "（交集统计自然体现，未参与判定）"),
        },
        "verdict_dist_divergence": dict(sorted(dist.items())),
        "consensus_boxes": cons["n_consensus"],
        "arbitrated_kept": (dist["arbiter-keep"] + dist["arbiter-keep-merged"]
                            + dist["arbiter-correct"]),
        "arbitrated_removed": dist["arbiter-delete"] + dist["arbiter-delete-duplicate"],
        "total_boxes": sum(len(d["boxes"]) for d in pages.values()),
        "pages": dict(sorted(pages.items())),
        "derived_gt_crosscheck": {"per_page": stats, "summary": summary,
                                  "derived_source": "manifest.r3.json pre-k01/02/08/09（chiqui7-scan 采集口径，R2 confirm 判定链）"},
    }
    GT_OUT.write_text(json.dumps(gt_doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[npd-gt] pages={sorted(pages)} boxes/page="
          f"{ {k: len(v['boxes']) for k, v in sorted(pages.items())} } "
          f"total={gt_doc['total_boxes']}")
    print(f"[npd-gt] verdict_dist={dict(sorted(dist.items()))}")
    print(f"[crosscheck] {json.dumps(summary, ensure_ascii=False)}")
    return 0


def _match(a_list, b_list):
    """面积降序贪心（确定性）。返回 (pairs, only_a, only_b)。"""
    pairs, used_a, used_b = [], set(), set()
    cand = [(iou(a, b), (a[2]-a[0])*(a[3]-a[1]), i, j)
            for i, a in enumerate(a_list) for j, b in enumerate(b_list)]
    cand.sort(key=lambda t: (-t[0], -t[1]))
    for v, _ar, i, j in cand:
        if v < IOU_MATCH or i in used_a or j in used_b:
            continue
        used_a.add(i)
        used_b.add(j)
        pairs.append((v, a_list[i], b_list[j]))
    return (pairs, [(iou(a_list[i], [0, 0, 0, 0]), a_list[i]) for i in range(len(a_list)) if i not in used_a],
            [(0.0, b_list[j]) for j in range(len(b_list)) if j not in used_b])


if __name__ == "__main__":
    raise SystemExit(main())
