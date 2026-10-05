"""M2-KO-TILE-CALIB 数字复算核验（验收判据：数字从盘上产物复算）。

从盘上两源独立复算四组矩阵并逐格对 eval-matrix.json 断言：
  源① GT = R2 final manifest.{val,test}.json（KO 4 页 56 框，重新 poly_to_xyxy）；
  源② preds = verification/M2-KO-TILE-CALIB/raw/eval-{chiqui7,v2b}-{letterbox,tile}.json
       的 per_sample.{conf}.per_page[].preds（逐框明细）。
匹配算法独立重实现本文件内（iou_xyxy/greedy_match 与 tile_calib.py 同语义，
不 import 其函数——独立复算而非同码重跑）。
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
R2_FINAL = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode"
    r"/training_data/sfx-v1/annotate-r2/final"
)
RAW = REPO / "verification" / "M2-KO-TILE-CALIB" / "raw"
MATRIX = REPO / "verification" / "M2-KO-TILE-CALIB" / "eval-matrix.json"

KO_IDS = ("pre-k01", "pre-k02", "pre-k08", "pre-k09")
CONFS = ("0.5", "0.2")
IOU_MATCH = 0.5


def iou(a, b) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter)


def greedy_match(gts, preds):
    """每 GT 至多一预测、每预测至多一 GT，pred conf 降序贪心，IoU>=0.5。"""
    used = [False] * len(preds)
    hit = [False] * len(gts)
    order = sorted(range(len(preds)), key=lambda i: -preds[i][1])
    for pi in order:
        best = -1.0
        pick = -1
        for gi, g in enumerate(gts):
            if hit[gi]:
                continue
            v = iou(preds[pi][0], g)
            if v >= IOU_MATCH and v > best:
                best, pick = v, gi
        if pick >= 0:
            hit[pick] = True
            used[pi] = True
    return sum(hit)


def poly_to_xyxy(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return [min(xs), min(ys), max(xs), max(ys)]


def main() -> int:
    gts: dict[str, list] = {}
    for split in ("val", "test"):
        m = json.loads((R2_FINAL / f"manifest.{split}.json").read_text(encoding="utf-8"))
        for s in m["samples"]:
            if s["sample_id"] in KO_IDS:
                gts[s["sample_id"]] = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
    assert sorted(gts) == sorted(KO_IDS), sorted(gts)
    n_gt = sum(len(v) for v in gts.values())
    assert n_gt == 56, n_gt

    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))["matrix"]
    failures = []
    for side in ("chiqui7", "v2b"):
        for caliber in ("letterbox", "tile"):
            raw = json.loads(
                (RAW / f"eval-{side}-{caliber}.json").read_text(encoding="utf-8"))
            per_sample = raw["per_sample"]
            for conf in CONFS:
                matched = 0
                n_pred = 0
                per_page_detail = {}
                for entry in per_sample[conf]["per_page"]:
                    sid = entry["sample_id"]
                    preds = [([p["xyxy"][0], p["xyxy"][1], p["xyxy"][2], p["xyxy"][3]],
                              p["conf"]) for p in entry["preds"]]
                    m = greedy_match(gts[sid], preds)
                    matched += m
                    n_pred += len(preds)
                    per_page_detail[sid] = {"matched": m, "n_gt": len(gts[sid]),
                                            "n_pred": len(preds)}
                cell = matrix[side][caliber][conf]
                expect = {
                    "matched": f"{matched}/{n_gt}",
                    "recall_rate": round(matched / n_gt, 4),
                    "precision": round(matched / n_pred, 4) if n_pred else None,
                    "n_pred": n_pred,
                }
                ok = all(
                    (cell.get(k) is None and expect[k] is None) or cell.get(k) == expect[k]
                    for k in expect
                )
                print(f"recompute {side}/{caliber}/conf{conf}: {expect} "
                      f"{'== matrix OK' if ok else '!= matrix MISMATCH ' + json.dumps(cell)}",
                      flush=True)
                if not ok:
                    failures.append(f"{side}/{caliber}/{conf}")
                # 逐页明细登记（报告引用）
                print(f"    per_page: {json.dumps(per_page_detail)}", flush=True)
    if failures:
        print(f"FAIL: {failures}")
        return 1
    print("ALL 8 CELLS RECOMPUTED == eval-matrix.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
