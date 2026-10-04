"""M2-SFX-TRAIN-V1 AC4：directional 评测（BJ challenge 主考卷 + KO 不回退检查）。

口径（T2 合同 AC4 + ask）：
- 新模型 = AC3 导出 best.onnx（sha256 fb60b460…，进程内重指生产 pin，src 零改动），
  推理走生产 SfxDetectionProvider.detect 全序列（letterbox 1024/生产解析链/类无关
  NMS IoU 0.7/sfx 类过滤——detection_sfx.py _sfx_boxes 原样），conf≥0.50 生产冻结口径
  与 conf≥0.20 宽松口径各一版。
- GT = train-v1 manifest（challenge 5 框 / val 53 框 / test 5 框，IoU≥0.5 匹配）。
- chiqui7 对照 = R1/R2 预标注引用（不重跑现役模型）：
  · BJ challenge：R2 worksheet/worksheet-bj-new.json 的 BJ17/BJ18 候选框（xyxy 原页
    坐标系 + ai_conf）；
  · KO 页（pre-k01/02/08/09）：R1 worksheet/worksheet.json domain=ko 单元
    （sources=["chiqui7-scan"]）；
  · imp-ogkalu-*（val 2 样本 2 框）：预标注源=ogkalu rt-detr（非 chiqui7）——chiqui7
    基线不可得，如实登记；chiqui7 汇总对照分母=KO 页 GT（56 框）。
- 匹配：box 级 IoU≥0.5，预测按 conf 降序贪心（每 GT 至多一预测、每预测至多一 GT）；
  recall=matched/|GT|；precision=matched/|preds|（preds=0 时记 null 如实）。
- 统计功效低：全部结论 directional（合同措辞纪律，禁用「显著」）；0 也如实。

证据：verification/M2-SFX-TRAIN-V1/raw/eval-challenge.json + eval-kodelta.json。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

TRAIN_V1 = REPO / "training_data" / "sfx-v1" / "train-v1"
DATASET = TRAIN_V1 / "dataset"
BEST_ONNX = TRAIN_V1 / "weights" / "best.onnx"
R2_WS_BJ = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1"
    r"/annotate-r2/worksheet/worksheet-bj-new.json"
)
R1_WS = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode/training_data/sfx-v1"
    r"/annotate-r1/worksheet/worksheet.json"
)
RAW_OUT = REPO / "verification" / "M2-SFX-TRAIN-V1" / "raw"

CONFS = (0.5, 0.2)
IOU_MATCH = 0.5


def iou_xyxy(a, b) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    inter = iw * ih
    if inter <= 0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def poly_to_xyxy(polygon) -> list[float]:
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


def match_gt(gt_boxes: list[list[float]], preds: list[tuple[list[float], float]]) -> dict:
    """贪心匹配：preds 按 conf 降序，每 GT 至多一预测。返回明细+R/P。"""
    gt_matched = [None] * len(gt_boxes)  # matched pred index or None
    pred_used: set[int] = set()
    order = sorted(range(len(preds)), key=lambda i: -preds[i][1])
    pairs = []
    for pi in order:
        pxyxy, pconf = preds[pi]
        best = (-1.0, -1)
        for gi, g in enumerate(gt_boxes):
            if gt_matched[gi] is not None:
                continue
            v = iou_xyxy(pxyxy, g)
            if v >= IOU_MATCH and v > best[0]:
                best = (v, gi)
        if best[1] >= 0:
            gt_matched[best[1]] = pi
            pred_used.add(pi)
            pairs.append({"gt_index": best[1], "pred_index": pi, "iou": round(best[0], 4),
                          "pred_conf": round(pconf, 4)})
    matched = sum(1 for m in gt_matched if m is not None)
    return {
        "n_gt": len(gt_boxes),
        "n_pred": len(preds),
        "matched": matched,
        "recall": round(matched / len(gt_boxes), 4) if gt_boxes else None,
        "precision": round(matched / len(preds), 4) if preds else None,
        "pairs": pairs,
        "gt_matched_flags": [m is not None for m in gt_matched],
    }


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_manifest(split: str) -> list[dict]:
    return json.loads((TRAIN_V1 / f"manifest.{split}.json").read_text(encoding="utf-8"))["samples"]


def main() -> int:
    from PIL import Image
    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import SfxDetectionProvider
    from ports.detection.ports import DetectionRequest

    assert BEST_ONNX.is_file(), f"missing AC3 artifact: {BEST_ONNX}"
    onnx_sha = sha256_file(BEST_ONNX)
    dsfx.SFX_WEIGHTS_SHA256 = onnx_sha  # 进程内重指（src 零改动；生产 pin 不变）
    providers = {c: SfxDetectionProvider(weights_path=BEST_ONNX, conf_threshold=c) for c in CONFS}

    def infer(sample: dict, stem_dir: str) -> dict[str, list]:
        img_path = DATASET / "images" / stem_dir / f"{sample['sample_id']}.png"
        page = Image.open(img_path).convert("RGB")
        w, h = page.size
        assert (w, h) == (sample["image"]["width"], sample["image"]["height"]), \
            f"{sample['sample_id']}: 图像尺寸 {w}x{h} != manifest"
        req = DetectionRequest(page_id=sample["sample_id"],
                               image_bytes=numpy.asarray(page, dtype=numpy.uint8).tobytes(),
                               width=w, height=h)
        out = {}
        for c in CONFS:
            res = providers[c].detect(req)
            out[str(c)] = [(list(map(float, (cd.polygon[0][0], cd.polygon[0][1],
                                             cd.polygon[2][0], cd.polygon[2][1]))),
                            float(cd.confidence)) for cd in res.candidates]
        return out

    import numpy  # noqa: F401（detect 内部 lazy import；此处仅保证已装）

    # ---- chiqui7 预标注引用表 ----
    ws_bj = json.loads(R2_WS_BJ.read_text(encoding="utf-8"))["units"]
    chiqui7_bj: dict[str, list] = {}  # case_id -> [(xyxy, conf)]
    for u in ws_bj:
        if u["case_id"] in ("BJ17", "BJ18"):
            chiqui7_bj.setdefault(u["case_id"], []).append(
                ([float(v) for v in u["xyxy"]], float(u["ai_conf"]), u["unit_id"]))
    ws_r1 = json.loads(R1_WS.read_text(encoding="utf-8"))["units"]
    chiqui7_ko: dict[str, list] = {}  # case_id -> [(xyxy, conf, unit_id)]（仅 chiqui7-scan 源）
    for u in ws_r1:
        if u["domain"] == "ko" and "chiqui7-scan" in (u.get("sources") or []):
            chiqui7_ko.setdefault(u["case_id"], []).append(
                ([float(v) for v in u["xyxy"]], float(u["ai_conf"]), u["unit_id"]))

    def chiqui7_at(pool: list, conf_thr: float) -> list[tuple[list[float], float]]:
        return [(b, c) for b, c, _ in pool if c >= conf_thr]

    # ======================================================================
    # AC4a：BJ challenge（主考卷）
    # ======================================================================
    challenge = load_manifest("challenge")
    assert len(challenge) == 2 and sum(len(s["boxes"]) for s in challenge) == 5
    detail = []
    totals = {"new": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
              "chiqui7": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS}}
    for s in challenge:
        case = s["provenance"]["case_id"]
        gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
        gt_meta = [{"unit_id": (s["provenance"].get("boxes_meta") or [{}])[i].get("unit_id"),
                    "conf": (s["provenance"].get("boxes_meta") or [{}])[i].get("conf")} for i in range(len(gts))]
        preds = infer(s, "challenge")
        pool = chiqui7_bj.get(case, [])
        entry = {"sample_id": s["sample_id"], "case_id": case,
                 "page": Path(s["image"]["path"]).name, "gt": gt_meta, "sides": {}}
        for c in CONFS:
            ck = str(c)
            m_new = match_gt(gts, preds[ck])
            m_chi = match_gt(gts, chiqui7_at(pool, c))
            entry["sides"][ck] = {
                "new_model": {"preds": [{"xyxy": [round(v, 1) for v in b], "conf": round(cf, 4)}
                                        for b, cf in preds[ck]], **m_new},
                "chiqui7_prelabel": {"preds": [{"unit_id": uid, "xyxy": [round(v, 1) for v in b],
                                                "conf": round(cf, 4)} for b, cf, uid in pool if cf >= c],
                                     **m_chi},
            }
            totals["new"][ck]["gt"] += len(gts)
            totals["new"][ck]["matched"] += m_new["matched"]
            totals["new"][ck]["pred"] += m_new["n_pred"]
            totals["chiqui7"][ck]["gt"] += len(gts)
            totals["chiqui7"][ck]["matched"] += m_chi["matched"]
            totals["chiqui7"][ck]["pred"] += m_chi["n_pred"]
        detail.append(entry)

    challenge_summary = {}
    for side in ("new", "chiqui7"):
        challenge_summary[side] = {
            ck: {"recall": f'{v["matched"]}/{v["gt"]}',
                 "recall_rate": round(v["matched"] / v["gt"], 4) if v["gt"] else None,
                 "precision": round(v["matched"] / v["pred"], 4) if v["pred"] else None,
                 "n_pred": v["pred"]}
            for ck, v in totals[side].items()}

    eval_challenge = {
        "task": "M2-SFX-TRAIN-V1 AC4a BJ challenge 召回（directional；主攻形态考卷）",
        "new_model": {"onnx": str(BEST_ONNX), "sha256": onnx_sha,
                      "inference": "生产 SfxDetectionProvider.detect 全序列（letterbox 1024/类无关 NMS 0.7/sfx 过滤）",
                      "confs": list(CONFS)},
        "chiqui7_baseline": {"source": "R2 worksheet/worksheet-bj-new.json（预标注候选框+ai_conf 原页坐标系，不重跑现役模型）",
                             "pool_sizes": {k: len(v) for k, v in chiqui7_bj.items()}},
        "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心（每 GT 至多一预测）",
        "summary": challenge_summary,
        "per_sample": detail,
        "wording_discipline": "directional 评测，统计功效低；结论禁用「显著」；0 也如实",
    }
    RAW_OUT.mkdir(parents=True, exist_ok=True)
    (RAW_OUT / "eval-challenge.json").write_text(
        json.dumps(eval_challenge, ensure_ascii=False, indent=1), encoding="utf-8")
    print("[eval-challenge] " + json.dumps(challenge_summary, ensure_ascii=False))

    # ======================================================================
    # AC4b：KO 不回退（val 4 样本 53 框 + test 2 样本 5 框）
    # ======================================================================
    ko_detail = []
    ko_totals = {"new": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
                 "chiqui7": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
                 "new_kopage_only": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
                 "chiqui7_kopage_only": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS}}
    for split, split_dir in (("val", "val"), ("test", "test")):
        for s in load_manifest(split):
            case = s["provenance"]["case_id"]
            is_ko_page = s["sample_id"].startswith("pre-k")
            gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
            preds = infer(s, split_dir)
            pool = chiqui7_ko.get(case, [])
            entry = {"sample_id": s["sample_id"], "case_id": case, "split": split,
                     "kind": "ko_page" if is_ko_page else "ogkalu_crop_no_chiqui7_baseline",
                     "n_gt": len(gts), "sides": {}}
            for c in CONFS:
                ck = str(c)
                m_new = match_gt(gts, preds[ck])
                entry["sides"][ck] = {"new_model": {
                    "preds": [{"xyxy": [round(v, 1) for v in b], "conf": round(cf, 4)}
                              for b, cf in preds[ck]],
                    "recall": m_new["recall"], "precision": m_new["precision"],
                    "matched": m_new["matched"], "n_pred": m_new["n_pred"],
                    "pairs": m_new["pairs"]}}
                if is_ko_page:
                    m_chi = match_gt(gts, chiqui7_at(pool, c))
                    entry["sides"][ck]["chiqui7_prelabel"] = {
                        "n_pool": len(pool),
                        "preds": [{"unit_id": uid, "conf": round(cf, 4)}
                                  for b, cf, uid in pool if cf >= c],
                        "recall": m_chi["recall"], "precision": m_chi["precision"],
                        "matched": m_chi["matched"], "n_pred": m_chi["n_pred"],
                        "pairs": m_chi["pairs"]}
                    for tag, tot in (("new", ko_totals["new"]), ("chiqui7", ko_totals["chiqui7"]),
                                     ("new", ko_totals["new_kopage_only"]),
                                     ("chiqui7", ko_totals["chiqui7_kopage_only"])):
                        m = m_new if tag == "new" else m_chi
                        tot[ck]["gt"] += len(gts)
                        tot[ck]["matched"] += m["matched"]
                        tot[ck]["pred"] += m["n_pred"]
                else:
                    # imp 区域图：chiqui7 预标注不可得（域源=ogkalu rt-detr），只算新模型
                    tot = ko_totals["new"]
                    tot[ck]["gt"] += len(gts)
                    tot[ck]["matched"] += m_new["matched"]
                    tot[ck]["pred"] += m_new["n_pred"]
            ko_detail.append(entry)

    def summarize(tot: dict) -> dict:
        return {ck: {"recall": f'{v["matched"]}/{v["gt"]}',
                     "recall_rate": round(v["matched"] / v["gt"], 4) if v["gt"] else None,
                     "precision": round(v["matched"] / v["pred"], 4) if v["pred"] else None,
                     "n_pred": v["pred"]}
                for ck, v in tot.items()}

    ko_summary = {
        "val_test_all_6_samples_58gt_new_model": summarize(ko_totals["new"]),
        "chiqui7_baseline_scope_note": ("chiqui7 预标注引用仅覆盖 KO 页 4 样本（56 框 GT）；"
                                        "val 的 imp-ogkalu-* 2 样本（2 框）预标注源=ogkalu rt-detr "
                                        "（R1 worksheet domain=ko-ogkalu-crop sources=ogkalu-text），"
                                        "chiqui7 基线不可得，如实登记"),
        "ko_page_only_4_samples_56gt": {"new_model": summarize(ko_totals["new_kopage_only"]),
                                        "chiqui7": summarize(ko_totals["chiqui7_kopage_only"])},
    }
    eval_ko = {
        "task": "M2-SFX-TRAIN-V1 AC4b KO 不回退检查（directional；统计功效低）",
        "new_model": {"onnx": str(BEST_ONNX), "sha256": onnx_sha},
        "chiqui7_baseline": {"source": "R1 worksheet/worksheet.json domain=ko（sources=chiqui7-scan，原页坐标系+ai_conf）",
                             "pool_sizes": {k: len(v) for k, v in sorted(chiqui7_ko.items())}},
        "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心",
        "summary": ko_summary,
        "per_sample": ko_detail,
        "wording_discipline": "directional；禁用「显著」；0 也如实；小样本差值不构成不回退证明",
    }
    (RAW_OUT / "eval-kodelta.json").write_text(
        json.dumps(eval_ko, ensure_ascii=False, indent=1), encoding="utf-8")
    print("[eval-kodelta] " + json.dumps(ko_summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
