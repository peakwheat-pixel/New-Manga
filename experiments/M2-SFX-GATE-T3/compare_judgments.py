"""M2-SFX-GATE-T3 AC2/AC3 双 AI judgment 比对（IoU>=0.5 贪心匹配）。

沿 gate-definition.md §3.1 匹配口径（IoU>=0.5、conf 降序贪心——本场景无 conf，
按框面积降序贪心确定性匹配）；复用 R3 divergence.json/consensus.json 同格式。
输入（只读）：
  annotate-r4/judgments/{a,b}/BJ32-37.json   （R3-MISS 补画，双 AI 独立整页标注）
  gate-t3/npd-judgments/{a,b}/pre-k{01,02,08,09}.json （KO 非派生，隔离纪律标注）
输出（R3 同格式，落各自 judgments 目录旁）：
  annotate-r4/judgments/{consensus.json,divergence.json}
  gate-t3/npd-judgments/{consensus.json,divergence.json}

比对语义（AC2 首例，无模型预标——单元由比对产生）：
  matched (IoU>=0.5)  -> consensus 单元：入册框=双方框的并集（union，实例包络语义，
                         覆盖双 AI 各自认定的字形范围；偏差如实登记在 pair 记录）
  unmatched           -> divergence 单元：单方候选，交第三方仲裁（重看图逐个终裁）

零 src：仅读 training_data 与 json，不触碰 src/**。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R4J = REPO / "training_data" / "sfx-v1" / "annotate-r4" / "judgments"
NPJ = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-judgments"
IOU_MATCH = 0.5  # gate-definition.md §3.1（eval_v2.py:47 同值）

PAGES_BJ = [f"BJ{i}" for i in range(32, 38)]
PAGES_NPD = ["pre-k01", "pre-k02", "pre-k08", "pre-k09"]


def load_boxes(p: Path) -> list[dict]:
    d = json.loads(p.read_text(encoding="utf-8"))
    out = []
    for i, b in enumerate(d["boxes"]):
        x1, y1, x2, y2 = b["xyxy"]
        out.append({"idx": i, "xyxy": [float(x1), float(y1), float(x2), float(y2)],
                    "rationale": b.get("rationale", ""), "area": (x2 - x1) * (y2 - y1)})
    return out


def iou(a: list[float], b: list[float]) -> float:
    ix1, iy1 = max(a[0], b[0]), max(a[1], b[1])
    ix2, iy2 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    if inter <= 0.0:
        return 0.0
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def union(a: list[float], b: list[float]) -> list[float]:
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def match_page(boxes_a: list[dict], boxes_b: list[dict]) -> tuple[list[dict], list[dict], list[dict]]:
    """面积降序贪心配对（确定性）；返回 (pairs, only_a, only_b)。"""
    pairs: list[dict] = []
    used_a: set[int] = set()
    used_b: set[int] = set()
    cand = []
    for ia in range(len(boxes_a)):
        for ib in range(len(boxes_b)):
            v = iou(boxes_a[ia]["xyxy"], boxes_b[ib]["xyxy"])
            if v >= IOU_MATCH:
                cand.append((v, boxes_a[ia]["area"], ia, ib))
    cand.sort(key=lambda t: (-t[0], -t[1]))  # IoU 降序、面积降序（确定性）
    for v, _ar, ia, ib in cand:
        if ia in used_a or ib in used_b:
            continue
        used_a.add(ia)
        used_b.add(ib)
        ba, bb = boxes_a[ia], boxes_b[ib]
        pairs.append({
            "iou": round(v, 4),
            "union_xyxy": [round(x, 1) for x in union(ba["xyxy"], bb["xyxy"])],
            "a_xyxy": ba["xyxy"], "b_xyxy": bb["xyxy"],
            "rationale_a": ba["rationale"], "rationale_b": bb["rationale"],
        })
    only_a = [boxes_a[i] for i in range(len(boxes_a)) if i not in used_a]
    only_b = [boxes_b[i] for i in range(len(boxes_b)) if i not in used_b]
    return pairs, only_a, only_b


def _div_id(pg: str, counter: list[int]) -> str:
    """分歧单元统一连续编号（先 a 后 b 共用一个计数器，防 D00 重号）。"""
    counter[0] += 1
    return f"R4-{pg}-D{counter[0] - 1:02d}"


def compare(pages: list[str], jdir: Path, purpose: str) -> dict:
    """对一组页做 a/b 比对；返回 R3 同格式 consensus+divergence 两个 dict。"""
    cons: list[dict] = []
    div: list[dict] = []
    per_page = {}
    for pg in pages:
        ba = load_boxes(jdir / "a" / f"{pg}.json")
        bb = load_boxes(jdir / "b" / f"{pg}.json")
        pairs, only_a, only_b = match_page(ba, bb)
        per_page[pg] = {"a": len(ba), "b": len(bb), "matched": len(pairs),
                        "only_a": len(only_a), "only_b": len(only_b)}
        for k, p in enumerate(pairs):
            cons.append({
                "id": f"R4-{pg}-C{k:02d}",
                "page": pg,
                "verdict": "keep-union",
                "iou_ab": p["iou"],
                "union_xyxy": p["union_xyxy"],
                "rationale_codex": p["rationale_a"],
                "rationale_agy": p["rationale_b"],
                "a_xyxy": p["a_xyxy"], "b_xyxy": p["b_xyxy"],
            })
        counter = [0]  # 每页统一连续编号（先 a 后 b）
        for o in only_a:
            div.append({
                "id": _div_id(pg, counter),
                "page": pg, "proposer": "a",
                "verdict_codex": "keep", "verdict_agy": None,
                "xyxy": o["xyxy"],
                "rationale_codex": o["rationale"], "rationale_agy": "(单方候选，b 未提出)",
                "status": "pending-arbiter",
            })
        for o in only_b:
            div.append({
                "id": _div_id(pg, counter),
                "page": pg, "proposer": "b",
                "verdict_codex": None, "verdict_agy": "keep",
                "xyxy": o["xyxy"],
                "rationale_codex": "(单方候选，a 未提出)", "rationale_agy": o["rationale"],
                "status": "pending-arbiter",
            })
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    consensus = {
        "purpose": purpose,
        "generated_at_utc": now,
        "tool": "experiments/M2-SFX-GATE-T3/compare_judgments.py",
        "matching": {"rule": "box IoU>=0.5 贪心（gate-definition §3.1 同值 0.5；无 conf，"
                             "IoU 降序+面积降序确定性配对）",
                     "iou_threshold": IOU_MATCH,
                     "union_rule": "consensus 入册框=双方框并集（实例包络语义，AC2 首例登记）"},
        "inputs": {"a": "judgments/a/", "b": "judgments/b/", "pages": pages,
                   "per_page": per_page},
        "n_consensus": len(cons),
        "verdict_dist": {"keep-union": len(cons)},
        "consensus": cons,
    }
    divergence = {
        "purpose": purpose + "（分歧清单：单方候选交第三方仲裁，R3 divergence.json 同格式）",
        "generated_at_utc": now,
        "tool": "experiments/M2-SFX-GATE-T3/compare_judgments.py",
        "n_divergence": len(div),
        "divergence": div,
    }
    return {"consensus": consensus, "divergence": divergence}


def main() -> int:
    out_bj = compare(
        PAGES_BJ, R4J,
        "M2-SFX-GATE-T3 AC2 R3-MISS 补画（BJ32-37）双 AI 独立整页标注比对——"
        "无模型预标首例（conf 概念不适用），单元由比对产生")
    (R4J / "consensus.json").write_text(
        json.dumps(out_bj["consensus"], ensure_ascii=False, indent=1), encoding="utf-8")
    (R4J / "divergence.json").write_text(
        json.dumps(out_bj["divergence"], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[BJ32-37] per_page={json.dumps(out_bj['consensus']['inputs']['per_page'])}")
    print(f"[BJ32-37] consensus={out_bj['consensus']['n_consensus']} "
          f"divergence={out_bj['divergence']['n_divergence']}")

    out_np = compare(
        PAGES_NPD, NPJ,
        "M2-SFX-GATE-T3 AC3 KO 非派生切片（pre-k01/02/08/09）双 AI 独立整页标注比对——"
        "隔离纪律：任务书零既有坐标（无模型输出/预标注/既有 GT 引用）")
    (NPJ / "consensus.json").write_text(
        json.dumps(out_np["consensus"], ensure_ascii=False, indent=1), encoding="utf-8")
    (NPJ / "divergence.json").write_text(
        json.dumps(out_np["divergence"], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[npd] per_page={json.dumps(out_np['consensus']['inputs']['per_page'])}")
    print(f"[npd] consensus={out_np['consensus']['n_consensus']} "
          f"divergence={out_np['divergence']['n_divergence']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
