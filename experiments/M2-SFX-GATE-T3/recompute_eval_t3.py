"""M2-SFX-GATE-T3 AC4 数字复算核验（验收判据：数字从盘上产物复算，与 raw 一致）。

沿 M2-KO-TILE-CALIB recompute_matrix.py 先例：从盘上两源独立复算并逐格对
eval-matrix.json 断言（本文件独立重实现 iou/greedy_match，不 import 评测脚本——
独立复算而非同码重跑）：
  源① GT = manifest.r2.json（考卷 5 框出厂）/ manifest.train-v4.json（BJ complete
       12 页 33 框）/ R2 final manifest.{val,test}.json（KO 派生 56 框）/
       gate-t3/npd-gt.json（KO 非派生 135 框）；
  源② preds = verification/M2-SFX-GATE-T3/raw/eval-{side}-{ds}.json 的
       per_sample[].sides.{conf}.preds（tile 主格）与 .letterbox_control.preds
       （KO letterbox 对照格）。
覆盖：3 权重 × 4 数据集主格（conf0.5/conf0.2）= 24 格 + KO 双数据集 letterbox
对照格（conf0.5/conf0.2）× 3 权重 = 12 格，共 36 格。
"""

from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRAIN_V4 = REPO / "training_data" / "sfx-v1" / "train-v4"
R2_FINAL = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1"
    r"/annotate-r2/final"
)
NPD_GT = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-gt.json"
RAW = REPO / "verification" / "M2-SFX-GATE-T3" / "raw"
MATRIX = REPO / "verification" / "M2-SFX-GATE-T3" / "eval-matrix.json"

SIDES = ("chiqui7", "v2a", "v2b")
DS_BJ = ("bj-exam", "bj-ext")
DS_KO = ("ko-tile", "ko-npd")
EXAM_IDS = ("pre-bj17", "pre-bj18")
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
    """每 GT 至多一预测、每预测至多一 GT，pred conf 降序贪心，IoU>=0.5（独立实现）。"""
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
    return sum(hit)


def poly_to_xyxy(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return [min(xs), min(ys), max(xs), max(ys)]


def _read(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def load_gt() -> dict[str, dict[str, list]]:
    """每数据集：{sample_id: [xyxy,...]}（全部从盘上权威源重读）。"""
    gt: dict[str, dict[str, list]] = {}

    r2 = _read(R2_FINAL / "manifest.r2.json")
    by = {s["sample_id"]: s for s in r2["samples"]}
    gt["bj-exam"] = {sid: [poly_to_xyxy(b["polygon"]) for b in by[sid]["boxes"]]
                     for sid in EXAM_IDS}
    assert sum(len(v) for v in gt["bj-exam"].values()) == 5

    full = _read(TRAIN_V4 / "manifest.train-v4.json")
    gt["bj-ext"] = {s["sample_id"]: [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
                    for s in full["samples"]
                    if s["group"].startswith("densho810/") and s["annotation_status"] == "complete"}
    assert len(gt["bj-ext"]) == 12
    assert sum(len(v) for v in gt["bj-ext"].values()) == 33

    gt["ko-tile"] = {}
    for split in ("val", "test"):
        m = _read(R2_FINAL / f"manifest.{split}.json")
        for s in m["samples"]:
            if s["sample_id"] in KO_IDS:
                gt["ko-tile"][s["sample_id"]] = [
                    poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
    assert sorted(gt["ko-tile"]) == sorted(KO_IDS)
    assert sum(len(v) for v in gt["ko-tile"].values()) == 56

    npd = _read(NPD_GT)
    gt["ko-npd"] = {pid: [b["xyxy"] for b in npd["pages"][pid]["boxes"]]
                    for pid in npd["pages"]}
    assert sum(len(v) for v in gt["ko-npd"].values()) == 135
    return gt


def check_cell(cell, matched: int, n_gt: int, n_pred: int, failures: list, label: str) -> None:
    expect = {
        "matched": f"{matched}/{n_gt}",
        "recall_rate": round(matched / n_gt, 4) if n_gt else None,
        "precision": round(matched / n_pred, 4) if n_pred else None,
        "n_pred": n_pred,
    }
    ok = all((cell.get(k) is None and expect[k] is None) or cell.get(k) == expect[k]
             for k in expect)
    print(f"recompute {label}: {expect} {'== matrix OK' if ok else '!= matrix MISMATCH '
          + json.dumps(cell)}", flush=True)
    if not ok:
        failures.append(label)


def main() -> int:
    gt = load_gt()
    matrix = _read(MATRIX)["matrix"]
    failures: list[str] = []
    for side in SIDES:
        for ds in DS_BJ + DS_KO:
            raw = _read(RAW / f"eval-{side}-{ds}.json")
            per_sample = raw["per_sample"]
            n_gt_ds = sum(len(v) for v in gt[ds].values())
            assert {e["sample_id"] for e in per_sample} == set(gt[ds]), \
                f"{side}/{ds}: raw 页集与 GT 源不一致"
            for conf in CONFS:
                matched = n_pred = 0
                lb_matched = lb_pred = 0
                for entry in per_sample:
                    gts = gt[ds][entry["sample_id"]]
                    # tile 主格 preds（bj 数据集同为 letterbox 主格，字段同名）
                    preds = [([p["xyxy"][0], p["xyxy"][1], p["xyxy"][2], p["xyxy"][3]],
                              p["conf"]) for p in entry["sides"][conf]["preds"]]
                    matched += greedy_match(gts, preds)
                    n_pred += len(preds)
                    if ds in DS_KO:
                        # letterbox 对照格并行复算（逐页累加，聚合后比对 matrix cell）
                        lb = entry["sides"][conf]["letterbox_control"]
                        lb_preds = [([p["xyxy"][0], p["xyxy"][1], p["xyxy"][2], p["xyxy"][3]],
                                     p["conf"]) for p in lb["preds"]]
                        lb_matched += greedy_match(gts, lb_preds)
                        lb_pred += len(lb_preds)
                cell = matrix[side][ds][conf]
                check_cell(cell, matched, n_gt_ds, n_pred, failures, f"{side}/{ds}/conf{conf}")
                if ds in DS_KO:
                    lb_cell = matrix[side][ds]["letterbox_control"][conf]
                    check_cell(lb_cell, lb_matched, n_gt_ds, lb_pred, failures,
                               f"{side}/{ds}/letterbox/conf{conf}")
    if failures:
        print(f"FAIL: {failures}")
        return 1
    print("ALL CELLS RECOMPUTED == eval-matrix.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
