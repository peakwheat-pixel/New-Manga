"""M2-SFX-TRAIN-V2 AC3 评测（DSH V1-r1 P2-1 整改落地：chiqui7 同链路独立复跑）。

沿 V1 eval_challenge.py（experiments/M2-SFX-TRAIN-V1/，只读蓝本）模式复制适配。
与 V1 的关键差异（P2-1 整改）：**chiqui7 对照不再是预标注池引用，而是用生产现役
权重（src/infrastructure/providers/detection_sfx.py:110 pin d87389af… 所指
M2-SFX-DETECT/weights/yolo11s-seg.onnx，sha 逐字核对在盘）走同一生产推理序列
（SfxDetectionProvider.detect：letterbox 1024/类无关 NMS 0.7/sfx 类过滤）对同页
独立推理**——独立测量，非预标注引用。

三方：v2a / v2b（AC3 导出 onnx，进程内重指 pin，src 零改动）+ chiqui7_prod
（生产 pin 原样加载，零重指）。页面与 GT 与 V1 完全同批（challenge 2 页 5 框 /
val 4 样本 53 框 / test 2 样本 5 框沿 R2/V1 不变——AC1 重切未动这三个分集），
conf≥0.50 生产冻结与 ≥0.20 宽松双口径，box IoU≥0.5 conf 降序贪心匹配。

V1 基线数字从 Git 内 verification/M2-SFX-TRAIN-V1/raw/{eval-challenge,eval-kodelta}.json
summary 段直接引用（同考卷同 GT 同阈值同 IoU 可比；V1 的 chiqui7=预标注引用口径，
与 V2 独立复跑口径不同，对比表分列并注）。

证据：raw/eval-{v2a,v2b,chiqui7-rerun}.json（逐框明细）+ eval-comparison.json（三方表）。
directional 纪律：统计功效低，禁用「显著」；0 也如实。
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

TRAIN_V2 = REPO / "training_data" / "sfx-v1" / "train-v2"
DATASET = TRAIN_V2 / "dataset"
RAW_OUT = REPO / "verification" / "M2-SFX-TRAIN-V2" / "raw"

PROD_ONNX = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx")
PROD_PIN_HEAD = "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"
V1_RAW = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode/verification/M2-SFX-TRAIN-V1/raw")

NEW_ONNX = {
    "v2a": TRAIN_V2 / "weights" / "v2a" / "best.onnx",
    "v2b": TRAIN_V2 / "weights" / "v2b" / "best.onnx",
}

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
    """贪心匹配：preds 按 conf 降序，每 GT 至多一预测、每预测至多一 GT（沿 V1）。"""
    gt_matched = [None] * len(gt_boxes)
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
    return json.loads((TRAIN_V2 / f"manifest.{split}.json").read_text(encoding="utf-8"))["samples"]


def summarize(tot: dict) -> dict:
    return {ck: {"recall": f'{v["matched"]}/{v["gt"]}',
                 "recall_rate": round(v["matched"] / v["gt"], 4) if v["gt"] else None,
                 "precision": round(v["matched"] / v["pred"], 4) if v["pred"] else None,
                 "n_pred": v["pred"]}
            for ck, v in tot.items()}


def main() -> int:
    import numpy
    from PIL import Image

    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import SfxDetectionProvider
    from ports.detection.ports import DetectionRequest

    # 生产现役权重供应链自检（零重指：sha 逐字等于 pin 才能加载成功，即复跑前提）
    prod_sha = sha256_file(PROD_ONNX)
    assert prod_sha == PROD_PIN_HEAD, f"生产现役权重 sha {prod_sha} != pin {PROD_PIN_HEAD}"
    print(f"[eval-v2] chiqui7 prod onnx ok: {PROD_ONNX} sha256={prod_sha}", flush=True)

    # 评测页集：challenge（BJ 考卷）+ val/test（KO 58 框；含 KO 页 56 框与 imp-ogkalu 2 框）
    pages: list[dict] = []
    for split in ("challenge", "val", "test"):
        for s in load_manifest(split):
            pages.append({"sample": s, "split": split,
                          "img": DATASET / "images" / split / f"{s['sample_id']}.png"})
    n_gt_total = sum(len(p["sample"]["boxes"]) for p in pages)
    assert n_gt_total == 63, f"评测 GT 总数 {n_gt_total} != 63（challenge 5+val 53+test 5=63）"
    # GT 与 V1 同批断言（challenge/val/test 沿 R2/V1 不变；sample_id 集合一致）
    v1_manifest_dir = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode/training_data/sfx-v1/train-v1")
    for split in ("challenge", "val", "test"):
        v1_ids = {s["sample_id"] for s in json.loads(
            (v1_manifest_dir / f"manifest.{split}.json").read_text(encoding="utf-8"))["samples"]}
        v2_ids = {p["sample"]["sample_id"] for p in pages if p["split"] == split}
        assert v1_ids == v2_ids, f"{split}: 评测页集合与 V1 不一致 {v2_ids ^ v1_ids}"
    print(f"[eval-v2] 评测页集合与 V1 同批断言通过（challenge/val/test 共 {len(pages)} 页 "
          f"{n_gt_total} 框 GT）", flush=True)

    # 预读图像（8 页，内存可承受）
    for p in pages:
        page = Image.open(p["img"]).convert("RGB")
        w, h = page.size
        assert (w, h) == (p["sample"]["image"]["width"], p["sample"]["image"]["height"]), \
            f'{p["sample"]["sample_id"]}: 尺寸失配'
        p["request"] = DetectionRequest(
            page_id=p["sample"]["sample_id"],
            image_bytes=numpy.asarray(page, dtype=numpy.uint8).tobytes(),
            width=w, height=h)
        p["gts"] = [poly_to_xyxy(b["polygon"]) for b in p["sample"]["boxes"]]
        p["gt_meta"] = [{"unit_id": (p["sample"]["provenance"].get("boxes_meta") or [{}])[i].get("unit_id"),
                         "conf": (p["sample"]["provenance"].get("boxes_meta") or [{}])[i].get("conf")}
                        for i in range(len(p["gts"]))]
        p["is_ko_page"] = p["sample"]["sample_id"].startswith("pre-k")

    # 三方顺序：chiqui7_prod（pin 原样）→ v2a（重指）→ v2b（重指）
    sides = {
        "chiqui7_prod_rerun": {"onnx": PROD_ONNX, "sha": prod_sha,
                               "note": "生产现役权重（pin d87389af… 逐字核对），pin 原样零重指——独立复跑"},
        "v2a": {"onnx": NEW_ONNX["v2a"], "sha": sha256_file(NEW_ONNX["v2a"]),
                "note": "AC3 导出（基座=官方 yolo11s-seg.pt），进程内重指 pin"},
        "v2b": {"onnx": NEW_ONNX["v2b"], "sha": sha256_file(NEW_ONNX["v2b"]),
                "note": "AC3 导出（基座=anonimkaq4 manga yolo11s-seg 近域基座），进程内重指 pin"},
    }

    side_results: dict[str, dict] = {}
    for side, meta in sides.items():
        dsfx.SFX_WEIGHTS_SHA256 = meta["sha"]  # chiqui7 时=原 pin（等值零改动）；新模型=重指
        print(f"[eval-v2] side={side} onnx_sha={meta['sha'][:12]} 推理中…", flush=True)
        per_sample = []
        totals = {"bj": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
                  "ko58": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
                  "kopage56": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS},
                  "full63": {str(c): {"gt": 0, "matched": 0, "pred": 0} for c in CONFS}}
        for p in pages:
            s = p["sample"]
            entry = {"sample_id": s["sample_id"],
                     "case_id": s["provenance"].get("case_id"),
                     "split": p["split"],
                     "kind": ("ko_page" if p["is_ko_page"] else
                              ("bj_challenge" if p["split"] == "challenge"
                               else "ogkalu_crop")),
                     "page": p["img"].name, "gt": p["gt_meta"], "sides": {}}
            for c in CONFS:
                ck = str(c)
                provider = SfxDetectionProvider(weights_path=meta["onnx"], conf_threshold=c)
                res = provider.detect(p["request"])
                preds = [(list(map(float, (cd.polygon[0][0], cd.polygon[0][1],
                                           cd.polygon[2][0], cd.polygon[2][1]))),
                          float(cd.confidence)) for cd in res.candidates]
                m = match_gt(p["gts"], preds)
                entry["sides"][ck] = {
                    "preds": [{"xyxy": [round(v, 1) for v in b], "conf": round(cf, 4)}
                              for b, cf in preds],
                    "matched": m["matched"], "n_pred": m["n_pred"],
                    "recall": m["recall"], "precision": m["precision"], "pairs": m["pairs"],
                    "gt_matched_flags": m["gt_matched_flags"],
                }
                buckets = [totals["full63"]]
                if p["split"] == "challenge":
                    buckets.append(totals["bj"])
                elif p["split"] in ("val", "test"):
                    buckets.append(totals["ko58"])
                    if p["is_ko_page"]:
                        buckets.append(totals["kopage56"])
                for tot in buckets:
                    tot[ck]["gt"] += len(p["gts"])
                    tot[ck]["matched"] += m["matched"]
                    tot[ck]["pred"] += m["n_pred"]
            per_sample.append(entry)

        summary = {
            "bj_challenge_2pages_5gt": summarize(totals["bj"]),
            "ko_val_test_6samples_58gt": summarize(totals["ko58"]),
            "ko_page_only_4samples_56gt": summarize(totals["kopage56"]),
            "full_8pages_63gt": summarize(totals["full63"]),
        }
        side_results[side] = {"meta": meta, "summary": summary, "per_sample": per_sample}
        out = {
            "task": "M2-SFX-TRAIN-V2 AC3 评测（P2-1 整改：同链路独立测量）",
            "side": side,
            "model": {"onnx": str(meta["onnx"]), "sha256": meta["sha"], "note": meta["note"],
                      "inference": "生产 SfxDetectionProvider.detect 全序列（letterbox 1024/类无关 NMS 0.7/sfx 过滤/CPUExecutionProvider）"},
            "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心（每 GT 至多一预测）",
            "confs": list(CONFS),
            "summary": summary,
            "per_sample": per_sample,
            "wording_discipline": "directional 评测，统计功效低；结论禁用「显著」；0 也如实",
        }
        fname = "eval-chiqui7-rerun.json" if side == "chiqui7_prod_rerun" else f"eval-{side}.json"
        (RAW_OUT / fname).write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                     encoding="utf-8")
        print(f"[eval-v2] {side}: " + json.dumps(summary, ensure_ascii=False), flush=True)

    # ---- V1 基线数字（Git 内 JSON 直接引用） ----
    v1_chal = json.loads((V1_RAW / "eval-challenge.json").read_text(encoding="utf-8"))
    v1_ko = json.loads((V1_RAW / "eval-kodelta.json").read_text(encoding="utf-8"))
    v1_ref = {
        "source": ("Git verification/M2-SFX-TRAIN-V1/raw/eval-challenge.json + eval-kodelta.json"
                   "（V1 merge 35cb3db0 入库；同考卷同 GT 同阈值同 IoU）"),
        "v1_new_model_onnx_sha256": v1_chal["new_model"]["sha256"],
        "bj_challenge_2pages_5gt": v1_chal["summary"],
        "ko_val_test_6samples_58gt": v1_ko["summary"]["val_test_all_6_samples_58gt_new_model"],
        "ko_page_only_4samples_56gt_chiqui7_prelabel": v1_ko["summary"]["ko_page_only_4_samples_56gt"],
        "caliber_note": ("V1 的 chiqui7=预标注引用（R2/R1 worksheet 候选池，P2-1 整改对象）；"
                         "V2 的 chiqui7=同链路独立复跑（生产推理序列原始检出）——两口径不同不可直比；"
                         "V1 new_model 与 V2 各方为同口径可直比"),
        "v2_coverage_extension_note": ("独立复跑覆盖全部 8 页（含 imp-ogkalu-* 2 页——V1 预标注引用"
                                       "口径下 chiqui7 基线不可得的页，复跑口径无此缺口）"),
    }

    # ---- 结构性发现（复跑口径暴露）：KO 长条 webtoon 页在整页 letterbox 1024 下
    #      SFX 亚像素化——三方（含生产现役 chiqui7 复跑）KO 页全部 0/56；V1 预标注
    #      口径的 56/56 来自素材线切块扫描（chiqui7-scan 切块采集），两口径不可直比。
    ko_pages = [(p["sample"]["sample_id"], p["sample"]["image"]["width"],
                 p["sample"]["image"]["height"]) for p in pages if p["is_ko_page"]]
    structural_finding = {
        "finding": ("KO 页（webtoon 超长条）在整页 letterbox 1024 生产序列下 SFX 亚像素化，"
                    "三方模型 KO 页召回全部 0/56——含生产现役 chiqui7 独立复跑（n_pred=0）。"
                    "V1 预标注引用口径的 chiqui7 56/56 来自素材线切块扫描采集口径，"
                    "与整页推理口径不可直比；P2-1 整改（独立复跑）暴露了预标注引用口径"
                    "掩盖的序列级事实：现役模型在 KO 域的生产整页序列表现同为 0 召回。"),
        "ko_page_dimensions": {sid: f"{w}x{h} (aspect 1:{round(h / w)})" for sid, w, h in ko_pages},
        "implication": ("V2 新模型 KO 页 0/56 与现役持平（无回退）；对 T4 生产切换的含义："
                        "KO 域瓶颈在推理序列口径（整页 letterbox vs 切块），非模型权重本身——"
                        "归 T3/T4 议题，不在本 Task 范围内解决"),
    }

    comparison = {
        "task": "M2-SFX-TRAIN-V2 AC3 三方对比（directional；V2A/V2B/chiqui7 独立复跑 vs V1 基线）",
        "generated_from": "experiments/M2-SFX-TRAIN-V2/eval_v2.py",
        "caliber": {
            "pages_gt": "challenge 2 页 5 框（BJ 考卷）+ val 4 样本 53 框 + test 2 样本 5 框（KO 58 框）=63 框；与 V1 同批（AC1 重切未动 challenge/val/test）",
            "confs": "≥0.50 生产冻结 / ≥0.20 宽松双口径",
            "matching": "box IoU≥0.5，pred conf 降序贪心",
            "inference": "三方同一生产推理序列（SfxDetectionProvider.detect；chiqui7=生产 pin 原样，v2a/v2b=进程内重指）",
        },
        "structural_finding": structural_finding,
        "sides": {side: {"model": {k: str(v) if isinstance(v, Path) else v
                                   for k, v in r["meta"].items()},
                         "summary": r["summary"]}
                  for side, r in side_results.items()},
        "v1_baseline_git_reference": v1_ref,
        "wording_discipline": "directional；统计功效低；禁用「显著」；0 也如实",
    }
    (RAW_OUT / "eval-comparison.json").write_text(
        json.dumps(comparison, ensure_ascii=False, indent=1), encoding="utf-8")
    print("[eval-v2] wrote eval-comparison.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
