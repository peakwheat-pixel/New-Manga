"""M2-SFX-GATE-T3 AC4 正式评测：三方权重 × 四数据集（沿 V2 eval_v2.py 模式扩展）。

模式来源（只读蓝本）：letterbox 口径+匹配沿 experiments/M2-SFX-TRAIN-V2/eval_v2.py
（match_gt/iou_xyxy/poly_to_xyxy 逐字，provider.detect 调用沿 :197-201）；KO tile
口径沿 experiments/M2-KO-TILE-CALIB/tile_calib.py tile 实现逐字复刻（tile_ys/
dedup_boxes/每 tile 生产序列本体 dsfx._letterbox+_sfx_boxes）。

三方权重（Task AC4 合同；gate-definition §3.3 基线口径=同链路独立复跑）：
  chiqui7 : 生产现役 pin d87389af… 所指 PROD_ONNX（sha 逐字断言，pin 原样零重指）
  v2a     : M2-SFX-TRAIN-V2 weights/v2a/best.onnx（sha 先验前缀 27d162e9，进程内重指）
  v2b     : M2-SFX-TRAIN-V2 weights/v2b/best.onnx（sha 先验前缀 944e8114，进程内重指）
  重指纪律沿 eval_v2.py:179 / tile_calib.py:374-382 先例：运行前先证 sha 断言，
  finally 恢复原 pin；src/env/registry 零改动。

四数据集（每格与 GT 均标派生属性；gate-definition §4.G1/G2 数据构成）：
  ① bj-exam : BJ 考卷 vol05 组原始 5 框（pre-bj17×2+pre-bj18×3），坐标=R2 出厂
              （manifest.r2.json）逐位，并断言与 train-v4 challenge manifest 逐位
              一致（G3-S4 口径本轮复算）；整页 letterbox 现行口径（G1 主判据数据；
              gt_attr=derived——GT⊂chiqui7 扫描候选池循环性，G1 限制①）
  ② bj-ext  : BJ 扩集=R3-MISS 补画后 BJ 域（densho810 组）全部 complete 页
              （train-v4 dataset 口径，manifest.train-v4.json）12 页 33 框
              （challenge 3 页 8 框+train 9 页 25 框分列：challenge 侧=泛化考题、
              train 侧=记忆性指标，G1 directional 扩展集）；letterbox 口径；
              gt_attr：R2/R3 判定链 8 页 18 框=derived，R4 补画 4 页 15 框
              =ai-direct（ai-direct-annotation 首例，G1 限制④/G6）
  ③ ko-tile : KO 4 页（pre-k01/k02/k08/k09）chiqui7 派生 GT 56 框（R2 final
              val/test manifest），tile_ov128 冻结口径（tile_calib.py tile 实现
              逐字：tile 宽=页宽原生、高 1024、重叠 128、末尾补页底锚点、页级跨
              tile IoU 0.5 conf 降序贪心 NMS）+letterbox 整页对照并行（G2 冻结
              口径「letterbox 整页对照口径并行跑」）；gt_attr=derived
              （采集一致性 directional，G2-A）
  ④ ko-npd  : KO 4 页非派生切片（npd-gt.json，AC3 双 AI 独立标注定稿 135 框），
              同 tile_ov128 口径+letterbox 对照；gt_attr=non-derived（模型质量
              属性，G2-B 硬判据载体：候选权重 recall ≥ chiqui7 同切片同口径）

口径：conf≥0.50 主口径（生产冻结 SFX_CONF_THRESHOLD=0.5）/conf≥0.20 宽松仅诊断
（gate-definition §3.2）；box IoU≥0.5 pred conf 降序贪心每 GT 至多一预测；
tile 序列每 conf 独立完整复跑（conf 过滤先于类无关 NMS 0.7，tile_calib.py 先例）。

产物：verification/M2-SFX-GATE-T3/raw/eval-{weight}-{ds}.json 逐框明细（12 文件，
ko 格内含 letterbox 对照段与 tile_stats）+ eval-matrix.json 汇总矩阵（3×4，每格
conf0.5 主+conf0.2 诊断+GT 属性标注）。--smoke 只跑 chiqui7×bj-exam 且产物落
gitignored smoke 目录（tile_calib.py --smoke 先例）。
零 src：生产模块只读 import。纪律：directional 评测，统计功效低，禁用「显著」；
0 也如实。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RAW_OUT = REPO / "verification" / "M2-SFX-GATE-T3" / "raw"
OUT_MATRIX = REPO / "verification" / "M2-SFX-GATE-T3" / "eval-matrix.json"
SMOKE_OUT = REPO / "training_data" / "sfx-v1" / "gate-t3" / "smoke"

TRAIN_V2_W = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1"
    r"/train-v2/weights"
)
PROD_ONNX = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx")
PROD_PIN_SHA = "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"

TRAIN_V4 = REPO / "training_data" / "sfx-v1" / "train-v4"
R2_FINAL = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1"
    r"/annotate-r2/final"
)
NPD_GT = REPO / "training_data" / "sfx-v1" / "gate-t3" / "npd-gt.json"

SIDES: dict[str, dict] = {
    "chiqui7": {
        "onnx": PROD_ONNX, "sha_prefix": None, "pin": "asis",
        "note": "生产现役权重（pin d87389af… 逐字核对），pin 原样零重指——同链路独立复跑",
    },
    "v2a": {
        "onnx": TRAIN_V2_W / "v2a" / "best.onnx", "sha_prefix": "27d162e9", "pin": "repoint",
        "note": "M2-SFX-TRAIN-V2 v2a best.onnx（sha 前缀 27d162e9 断言过），进程内重指 pin",
    },
    "v2b": {
        "onnx": TRAIN_V2_W / "v2b" / "best.onnx", "sha_prefix": "944e8114", "pin": "repoint",
        "note": "M2-SFX-TRAIN-V2 v2b best.onnx（sha 前缀 944e8114 断言过），进程内重指 pin",
    },
}

KO_IDS = ("pre-k01", "pre-k02", "pre-k08", "pre-k09")
EXPECT_KO_DERIVED_BOXES = 56
EXPECT_NPD_BOXES = 135
# AC2 冻结产物：R4 补画转正四页（ai-direct-annotation 首例）——bj-ext 每页 GT 属性分流
AI_DIRECT_IDS = {"pre-bj32", "pre-bj33", "pre-bj34", "pre-bj35"}
EXAM_IDS = ("pre-bj17", "pre-bj18")
EXPECT_EXAM_BOXES = 5
EXPECT_BJ_EXT_PAGES, EXPECT_BJ_EXT_BOXES = 12, 33

# tile_ov128 冻结口径（KO-TILE 提案 §3.1-3.3；tile_calib.py:87-90 逐字）
K_TILE_H = 1024
K_TILE_OVERLAP = 128
TILE_PAGE_NMS_IOU = 0.5

CONFS = (0.5, 0.2)
IOU_MATCH = 0.5

GT_ATTR = {
    "bj-exam": {"kind": "derived",
                "note": ("GT⊂chiqui7 整页扫描候选池（R2 判定链 confirm）——chiqui7 召回=数学必然"
                         "自洽上界（gate-definition §3.5/G1 限制①），非独立性能")},
    "bj-ext": {"kind": "mixed: derived + ai-direct",
               "note": ("R2/R3 判定链页=derived（循环性同 bj-exam）；R4-BJ32-35=ai-direct"
                        "（无模型预标，ai-direct-annotation 首例，G1 限制④/G6 归因）")},
    "ko-tile": {"kind": "derived",
                "note": ("chiqui7 派生 56 框=采集一致性属性（directional，G2-A）；56/56 基线="
                         "同源复现上界非独立性能（gate-definition §4.G2 已知限制①）")},
    "ko-npd": {"kind": "non-derived",
               "note": ("AC3 双 AI 独立整页标注（任务书零既有坐标，隔离纪律 PASS）定稿切片="
                        "模型质量属性，G2-B 硬判据载体（相对不回退判据）")},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def iou_xyxy(a, b) -> float:
    """逐字沿 eval_v2.py:50-59。"""
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
    """逐字沿 eval_v2.py:62-65。"""
    xs = [p[0] for p in polygon]
    ys = [p[1] for p in polygon]
    return [min(xs), min(ys), max(xs), max(ys)]


def match_gt(gt_boxes: list[list[float]], preds: list[tuple[list[float], float]]) -> dict:
    """贪心匹配：preds 按 conf 降序，每 GT 至多一预测、每预测至多一 GT。

    逐字沿 eval_v2.py:68-97（IoU>=0.5，conf 降序贪心）。
    """
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


def dedup_boxes(boxes: list[dict], iou_thr: float = 0.5) -> list[dict]:
    """页级跨 tile sfx 框去重（贪心 NMS，按 conf 降序）。

    逐字复刻 R1 _dedup_boxes（tile_calib.py:163-185 同文，冻结口径 §3.3）。
    """
    def iou(a, b):
        ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = ix * iy
        if inter <= 0.0:
            return 0.0
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        return inter / (area_a + area_b - inter)

    ordered = sorted(boxes, key=lambda b: b["conf"], reverse=True)
    kept: list[dict] = []
    for b in ordered:
        if any(iou(b["xyxy"], k["xyxy"]) >= iou_thr for k in kept):
            continue
        kept.append(b)
    return kept


def tile_ys(page_h: int, overlap: int = K_TILE_OVERLAP) -> list[int]:
    """R1 tile y 锚点序列，逐字复刻 stage1_preannotate.py:240-245（tile_calib.py:188-198 同文）：
    步长 K_TILE_H-overlap，末尾补 page_h-K_TILE_H 保证覆盖页底。"""
    ys = list(range(0, max(page_h - K_TILE_H, 0) + 1, K_TILE_H - overlap))
    if not ys:
        ys = [0]
    if ys[-1] + K_TILE_H < page_h:
        ys.append(page_h - K_TILE_H)
    return ys


def summarize_cell(per_page_cells: list[dict]) -> dict:
    """沿 tile_calib.py:306-313。"""
    gt = sum(c["n_gt"] for c in per_page_cells)
    matched = sum(c["matched"] for c in per_page_cells)
    n_pred = sum(c["n_pred"] for c in per_page_cells)
    return {"matched": f"{matched}/{gt}",
            "recall_rate": round(matched / gt, 4) if gt else None,
            "precision": round(matched / n_pred, 4) if n_pred else None,
            "n_pred": n_pred}


# --------------------------------------------------------------------------
# 数据装载
# --------------------------------------------------------------------------

def _read(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def load_bj_pages() -> list[dict]:
    """BJ 域 complete 页 12 页 33 框（train-v4 dataset 口径）+ 考卷 5 框出厂逐位断言。

    - bj-ext GT=train-v4 manifest（densho810/vol05 complete 全量）；
    - bj-exam GT=manifest.r2.json 出厂坐标（pre-bj17×2+pre-bj18×3），断言与
      train-v4 challenge manifest round(v,1) 逐位一致（G3-S4 口径本轮复算）；
    - 页图=train-v4 dataset 树，逐页 sha256 对 manifest.image.sha256 断言
      （R2 出厂页另断言与 manifest.r2.json image.sha256 同值）。
    """
    import numpy
    from PIL import Image
    from ports.detection.ports import DetectionRequest

    full = _read(TRAIN_V4 / "manifest.train-v4.json")
    chal_v4 = _read(TRAIN_V4 / "manifest.challenge.json")
    v4_chal_by = {s["sample_id"]: s for s in chal_v4["samples"]}

    bj = [s for s in full["samples"] if s["group"].startswith("densho810/")]
    bj = [s for s in bj if s["annotation_status"] == "complete"]
    bj.sort(key=lambda s: s["sample_id"])
    assert len(bj) == EXPECT_BJ_EXT_PAGES, f"BJ complete 页 {len(bj)} != {EXPECT_BJ_EXT_PAGES}"
    n_boxes = sum(len(s["boxes"]) for s in bj)
    assert n_boxes == EXPECT_BJ_EXT_BOXES, f"BJ complete 框 {n_boxes} != {EXPECT_BJ_EXT_BOXES}"
    chal_ids = sorted(s["sample_id"] for s in bj if s["split"] == "challenge")
    train_ids = sorted(s["sample_id"] for s in bj if s["split"] == "train")
    assert chal_ids == ["pre-bj17", "pre-bj18", "pre-bj32"], f"challenge 成员 {chal_ids}"
    assert len(train_ids) == 9, f"train 侧 BJ 页 {len(train_ids)} != 9"

    # 考卷 5 框出厂逐位（manifest.r2.json 出厂 ↔ train-v4 challenge）
    r2 = _read(R2_FINAL / "manifest.r2.json")
    r2_by = {s["sample_id"]: s for s in r2["samples"]}
    r2_exam_boxes: dict[str, list[list[float]]] = {}
    for sid in EXAM_IDS:
        old = r2_by[sid]
        assert len(old["boxes"]) == (2 if sid == "pre-bj17" else 3), f"{sid} 出厂框数漂移"
        new = v4_chal_by[sid]
        assert len(new["boxes"]) == len(old["boxes"])
        for nb, ob in zip(new["boxes"], old["boxes"]):
            a = [[round(v, 1) for v in pt] for pt in nb["polygon"]]
            b = [[round(v, 1) for v in pt] for pt in ob["polygon"]]
            assert a == b, f"{sid} 考卷框与 R2 出厂漂移: {a} vs {b}"
        assert new["image"]["sha256"] == old["image"]["sha256"], \
            f"{sid} 页图 sha 与 R2 出厂不一致"
        r2_exam_boxes[sid] = [poly_to_xyxy(bb["polygon"]) for bb in old["boxes"]]
    n_exam = sum(len(v) for v in r2_exam_boxes.values())
    assert n_exam == EXPECT_EXAM_BOXES, f"考卷框 {n_exam} != {EXPECT_EXAM_BOXES}"

    pages: list[dict] = []
    for s in bj:
        sid = s["sample_id"]
        img_path = None
        for ext in (".png", ".jpg", ".jpeg"):
            p = TRAIN_V4 / "dataset" / "images" / s["split"] / f"{sid}{ext}"
            if p.is_file():
                img_path = p
                break
        assert img_path is not None, f"{sid}: train-v4 dataset 树无页图"
        assert sha256_file(img_path) == s["image"]["sha256"], f"{sid}: dataset 页图 sha 失配"
        rgb = Image.open(img_path).convert("RGB")
        w, h = rgb.size
        assert (w, h) == (s["image"]["width"], s["image"]["height"]), f"{sid}: 尺寸失配"
        meta_boxes = s["provenance"].get("boxes_meta") or [{}]
        if sid in EXAM_IDS:
            gts = r2_exam_boxes[sid]  # 考卷 GT=R2 出厂逐位（bj-exam 主判据数据）
        else:
            gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
        pages.append({
            "sample_id": sid,
            "case_id": s["provenance"].get("case_id"),
            "split": s["split"],
            "gt_attr": ("ai-direct" if sid in AI_DIRECT_IDS else "derived"),
            "img": img_path, "w": w, "h": h,
            "request": DetectionRequest(
                page_id=sid,
                image_bytes=numpy.asarray(rgb, dtype=numpy.uint8).tobytes(),
                width=w, height=h),
            "gts": gts,
            "gt_meta": [
                {"unit_id": meta_boxes[i].get("unit_id"),
                 "conf": meta_boxes[i].get("conf"),
                 "gt_attr": ("ai-direct" if sid in AI_DIRECT_IDS else "derived")}
                for i in range(len(gts))],
        })
        rgb.close()
    return pages


def load_ko_pages() -> list[dict]:
    """KO 4 页（R2 final val/test，chiqui7 派生 GT 56 框）——沿 tile_calib.py:201-248 逐字
    （页 sha/尺寸断言），另断言 npd-gt crosscheck page_wh 与 manifest 一致。"""
    import numpy
    from PIL import Image
    from ports.detection.ports import DetectionRequest

    npd = _read(NPD_GT)
    cc = npd["derived_gt_crosscheck"]["per_page"]
    npd_boxes = {pid: [b["xyxy"] for b in npd["pages"][pid]["boxes"]] for pid in npd["pages"]}
    n_npd = sum(len(v) for v in npd_boxes.values())
    assert n_npd == EXPECT_NPD_BOXES, f"npd GT {n_npd} != {EXPECT_NPD_BOXES}"

    pages: list[dict] = []
    n_boxes = 0
    for split in ("val", "test"):
        m = _read(R2_FINAL / f"manifest.{split}.json")
        for s in m["samples"]:
            if s["sample_id"] not in KO_IDS:
                continue
            img = s["image"]
            p = Path(img["path"])
            assert p.is_file(), f"{s['sample_id']}: 页面缺失 {p}"
            assert sha256_file(p) == img["sha256"], \
                f"{s['sample_id']}: 图像 sha256 与 manifest 不一致"
            rgb_t = Image.open(p).convert("RGB")
            w, h = rgb_t.size
            assert (w, h) == (img["width"], img["height"]), \
                f"{s['sample_id']}: 尺寸 {w}x{h} != manifest {img['width']}x{img['height']}"
            rgb_t.close()
            sid = s["sample_id"]
            assert cc[sid]["page_wh"] == [w, h], \
                f"{sid}: npd crosscheck page_wh {cc[sid]['page_wh']} != manifest {[w, h]}"
            gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
            n_boxes += len(gts)
            pages.append({
                "sample_id": sid,
                "case_id": s["provenance"].get("case_id"),
                "split": split,
                "img": p, "w": w, "h": h,
                "request": DetectionRequest(
                    page_id=sid,
                    image_bytes=numpy.asarray(
                        Image.open(p).convert("RGB"), dtype=numpy.uint8).tobytes(),
                    width=w, height=h),
                "gts": gts,
                "gts_npd": npd_boxes[sid],
                "gt_meta": [
                    {"unit_id": (s["provenance"].get("boxes_meta") or [{}])[i].get("unit_id"),
                     "conf": (s["provenance"].get("boxes_meta") or [{}])[i].get("conf"),
                     "gt_attr": "derived"}
                    for i in range(len(gts))],
                "gt_meta_npd": [
                    {"chain": b.get("chain"), "gt_attr": "non-derived"}
                    for b in npd["pages"][sid]["boxes"]],
            })
    ids = [p["sample_id"] for p in pages]
    assert sorted(ids) == sorted(KO_IDS), f"KO 页集合不符：{ids}"
    assert n_boxes == EXPECT_KO_DERIVED_BOXES, f"KO 派生 GT {n_boxes} != {EXPECT_KO_DERIVED_BOXES}"
    return pages


# --------------------------------------------------------------------------
# 推理口径
# --------------------------------------------------------------------------

def run_letterbox(provider_factory, page: dict, conf: float) -> list[tuple[list[float], float]]:
    """整页 letterbox 生产序列原样，逐字沿 eval_v2.py:197-201 提取方式
    （tile_calib.py:251-260 同文）。"""
    provider = provider_factory(conf)
    res = provider.detect(page["request"])
    return [(list(map(float, (cd.polygon[0][0], cd.polygon[0][1],
                              cd.polygon[2][0], cd.polygon[2][1]))),
             float(cd.confidence)) for cd in res.candidates]


def run_tile(dsfx, session, imgsz, page: dict, conf: float, log) -> tuple[
        list[tuple[list[float], float]], dict]:
    """tile_ov128 冻结口径，逐字复刻 tile_calib.py:263-303（tile 宽=页宽原生、高 1024、
    重叠 128、末尾补页底锚点、y+y0 平移回页坐标、页级跨 tile NMS 0.5）。"""
    import numpy
    from PIL import Image

    page_w, page_h = page["w"], page["h"]
    ys = tile_ys(page_h, K_TILE_OVERLAP)
    with Image.open(page["img"]) as im:
        rgb = im.convert("RGB")
    sfx_boxes: list[dict] = []
    per_tile_counts: list[dict] = []
    for t_idx, y0 in enumerate(ys):
        y1 = min(y0 + K_TILE_H, page_h)
        tile = rgb.crop((0, y0, page_w, y1))
        th = y1 - y0
        inp, scale = dsfx._letterbox(numpy, numpy.asarray(tile), imgsz)
        raw = dsfx._sfx_boxes(session, inp, scale, conf, page_w=float(page_w), page_h=float(th))
        mapped = [{"xyxy": [b[0], b[1] + y0, b[2], b[3] + y0], "conf": b[4]}
                  for b in raw]
        sfx_boxes.extend(mapped)
        per_tile_counts.append({"tile_index": t_idx, "y0": y0, "y1": y1,
                                "sfx_raw": len(mapped)})
        if (t_idx + 1) % 20 == 0 or t_idx + 1 == len(ys):
            log(f"    tile {t_idx + 1}/{len(ys)} (y0={y0}) sfx_raw_cum={len(sfx_boxes)}")
    rgb.close()
    kept = dedup_boxes(sfx_boxes, TILE_PAGE_NMS_IOU)
    kept.sort(key=lambda b: (-b["conf"], b["xyxy"]))
    stats = {"n_tiles": len(ys), "sfx_raw": len(sfx_boxes),
             "sfx_after_page_nms": len(kept), "page_nms_iou": TILE_PAGE_NMS_IOU,
             "per_tile": per_tile_counts}
    return [(b["xyxy"], b["conf"]) for b in kept], stats


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------

def write_raw(out_dir: Path, side: str, ds: str, doc: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    p = out_dir / f"eval-{side}-{ds}.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[gate-t3] wrote {p}", flush=True)
    return p


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true",
                        help="冒烟：仅 chiqui7×bj-exam，产物落 gitignored smoke 目录")
    args = parser.parse_args()
    out_dir = SMOKE_OUT if args.smoke else RAW_OUT
    out_matrix = SMOKE_OUT / "eval-matrix.json" if args.smoke else OUT_MATRIX

    import numpy  # noqa: F401  (DetectionRequest 装载依赖前置自检)
    from PIL import Image

    # 受控本地素材（KO 超长 webtoon 最大 ~69MP）显式解除 PIL 警戒线（R1/tile_calib 先例）
    Image.MAX_IMAGE_PIXELS = None

    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    print(f"[gate-t3] start {now_iso()} mode={'smoke' if args.smoke else 'full'}", flush=True)

    # 权重先验断言（加载前；gate-definition §3.3/§4.G5-① 语义）
    shas: dict[str, str] = {}
    for side, meta in SIDES.items():
        shas[side] = sha256_file(meta["onnx"])
        if side == "chiqui7":
            assert shas[side] == PROD_PIN_SHA, \
                f"chiqui7 权重 sha {shas[side]} != 生产 pin {PROD_PIN_SHA}"
        else:
            assert shas[side].startswith(meta["sha_prefix"]), \
                f"{side} 权重 sha {shas[side]} 前缀 != {meta['sha_prefix']}"
        print(f"[gate-t3] {side} onnx sha256={shas[side]}（先验断言过）", flush=True)

    bj_pages = load_bj_pages()
    ko_pages = load_ko_pages()
    exam_pages = [p for p in bj_pages if p["sample_id"] in EXAM_IDS]
    assert len(exam_pages) == 2 and sum(len(p["gts"]) for p in exam_pages) == 5
    if args.smoke:
        bj_pages, ko_pages = exam_pages, []  # 冒烟只跑 BJ 考卷 2 页（bj-exam+bj-ext 同页集）
    n_bj = sum(len(p["gts"]) for p in bj_pages)
    n_ko = sum(len(p["gts"]) for p in ko_pages)
    n_npd = sum(len(p["gts_npd"]) for p in ko_pages)
    print(f"[gate-t3] 数据装载：BJ {len(bj_pages)} 页 {n_bj} 框（考卷 {len(exam_pages)} 页 5 框）"
          f"｜KO 派生 {len(ko_pages)} 页 {n_ko} 框｜KO 非派生 {n_npd} 框", flush=True)

    # 每 side tile session 各建一次（metadata names/imgsz 断言在 _build_engine 内逐权重执行；
    # v2a/v2b 构建窗口=进程内重指，chiqui7 pin 原样——tile_calib.py:365-384 先例）。
    engines: dict[str, dict] = {}
    pin_backup = dsfx.SFX_WEIGHTS_SHA256
    build_sides = ["chiqui7"] if args.smoke else list(SIDES)
    try:
        for side in build_sides:
            meta = SIDES[side]
            if meta["pin"] == "repoint":
                dsfx.SFX_WEIGHTS_SHA256 = shas[side]
            engines[side] = {
                "onnx": meta["onnx"], "sha": shas[side], "note": meta["note"],
                **dict(zip(("session", "imgsz", "imgsz_source", "imgsz_raw"),
                           dsfx._build_engine(meta["onnx"]))),
            }
            print(f"[gate-t3] engine {side}: imgsz={engines[side]['imgsz']} "
                  f"({engines[side]['imgsz_source']})", flush=True)
    finally:
        dsfx.SFX_WEIGHTS_SHA256 = pin_backup

    sides = list(SIDES)
    if args.smoke:
        sides = ["chiqui7"]
    matrix: dict[str, dict] = {s: {} for s in sides}

    for side in sides:
        e = engines[side]
        meta = SIDES[side]
        if meta["pin"] == "repoint":
            dsfx.SFX_WEIGHTS_SHA256 = shas[side]  # 重指窗口（letterbox provider 构建校验需要）
        try:
            # ---- ① bj-exam / ② bj-ext：整页 letterbox 现行口径 ----
            for ds_name, pages in (("bj-exam", exam_pages), ("bj-ext", bj_pages)):
                if not pages:
                    continue
                t_ds = time.perf_counter()
                per_conf_cells: dict[str, list] = {str(c): [] for c in CONFS}
                per_sample: list[dict] = []
                for p in pages:
                    entry = {"sample_id": p["sample_id"], "case_id": p["case_id"],
                             "split": p["split"], "kind": "bj_letterbox",
                             "gt_attr": p["gt_attr"], "page": Path(p["img"]).name,
                             "gt": p["gt_meta"], "sides": {}}
                    for c in CONFS:
                        ck = str(c)
                        t0 = time.perf_counter()
                        preds = run_letterbox(
                            lambda conf, _onnx=meta["onnx"]:
                                SfxDetectionProvider(weights_path=_onnx, conf_threshold=conf),
                            p, c)
                        m = match_gt(p["gts"], preds)
                        elapsed = round(time.perf_counter() - t0, 1)
                        per_conf_cells[ck].append(
                            {"sample_id": p["sample_id"], "split_tag": p["split"],
                             "n_gt": len(p["gts"]),
                             "n_pred": m["n_pred"], "matched": m["matched"],
                             "recall": m["recall"], "precision": m["precision"],
                             "inference_s": elapsed})
                        entry["sides"][ck] = {
                            "preds": [{"xyxy": [round(v, 1) for v in b], "conf": round(cf, 4)}
                                      for b, cf in preds],
                            "matched": m["matched"], "n_pred": m["n_pred"],
                            "recall": m["recall"], "precision": m["precision"],
                            "pairs": m["pairs"], "gt_matched_flags": m["gt_matched_flags"]}
                    per_sample.append(entry)
                    print(f"[gate-t3] {side}/{ds_name} {p['sample_id']}: "
                          + ", ".join(f"conf{c}={entry['sides'][str(c)]['matched']}"
                                      f"/{len(p['gts'])}" for c in CONFS)
                          + f" ({round(time.perf_counter() - t0, 1)}s)", flush=True)
                cell = {
                    "caliber": "letterbox-1024 生产序列原样（SfxDetectionProvider.detect）",
                    "gt_attr": GT_ATTR[ds_name],
                    "0.5": summarize_cell(per_conf_cells["0.5"]),
                    "0.2": summarize_cell(per_conf_cells["0.2"]),
                }
                if ds_name == "bj-ext":
                    # G1 directional 扩展集：challenge 侧=泛化考题 / train 侧=记忆性指标分列
                    cell["split_buckets"] = {
                        ck: {sp: summarize_cell([x for x in per_conf_cells[ck]
                                                 if x["split_tag"] == sp])
                             for sp in ("challenge", "train")}
                        for ck in per_conf_cells}
                matrix[side][ds_name] = cell
                write_raw(out_dir, side, ds_name, {
                    "task": "M2-SFX-GATE-T3 AC4 正式评测（三方×四数据集）",
                    "side": side, "dataset": ds_name,
                    "model": {"onnx": str(meta["onnx"]), "sha256": shas[side],
                              "note": meta["note"],
                              "inference": "生产 SfxDetectionProvider.detect 全序列"
                                           "（letterbox 1024/类无关 NMS 0.7/sfx 过滤/"
                                           "CPUExecutionProvider）"},
                    "caliber": cell["caliber"], "gt_attr": GT_ATTR[ds_name],
                    "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心（每 GT 至多一预测；"
                                "沿 eval_v2.py match_gt 逐字）",
                    "confs": {"0.5": "主口径（生产冻结）", "0.2": "宽松口径（仅诊断）"},
                    "summary": {"0.5": cell["0.5"], "0.2": cell["0.2"],
                                **({"split_buckets": cell["split_buckets"]}
                                   if "split_buckets" in cell else {})},
                    "per_sample": per_sample,
                    "wording_discipline": "directional 评测，统计功效低；结论禁用「显著」；0 也如实",
                })
                print(f"[gate-t3] {side}/{ds_name}: conf0.5={cell['0.5']} "
                      f"({round(time.perf_counter() - t_ds, 1)}s)", flush=True)

            # ---- ③ ko-tile / ④ ko-npd：tile_ov128 冻结口径 + letterbox 对照 ----
            for ds_name, gt_key, meta_key in (("ko-tile", "gts", "gt_meta"),
                                              ("ko-npd", "gts_npd", "gt_meta_npd")):
                if not ko_pages:
                    continue
                t_ds = time.perf_counter()
                per_conf_cells: dict[str, list] = {str(c): [] for c in CONFS}
                lb_cells: dict[str, list] = {str(c): [] for c in CONFS}
                per_sample: list[dict] = []
                for p in ko_pages:
                    gts = p[gt_key]
                    entry = {"sample_id": p["sample_id"], "case_id": p["case_id"],
                             "split": p["split"],
                             "kind": ("ko_tile_derived" if ds_name == "ko-tile"
                                      else "ko_tile_npd"),
                             "page": Path(p["img"]).name,
                             "page_size": [p["w"], p["h"]],
                             "gt": p[meta_key], "sides": {}}
                    for c in CONFS:
                        ck = str(c)
                        # tile 冻结口径（每 conf 独立完整序列，conf 过滤先于页级 NMS）
                        t0 = time.perf_counter()
                        preds, stats = run_tile(dsfx, e["session"], e["imgsz"], p, c, print)
                        m = match_gt(gts, preds)
                        elapsed = round(time.perf_counter() - t0, 1)
                        per_conf_cells[ck].append(
                            {"sample_id": p["sample_id"], "n_gt": len(gts),
                             "n_pred": m["n_pred"], "matched": m["matched"],
                             "recall": m["recall"], "precision": m["precision"],
                             "inference_s": elapsed,
                             "tile_stats": {k: v for k, v in stats.items()
                                            if k != "per_tile"}})
                        # letterbox 整页对照（G2 冻结口径并行；复现零输出结构性事实）
                        t0 = time.perf_counter()
                        lb_preds = run_letterbox(
                            lambda conf, _onnx=meta["onnx"]:
                                SfxDetectionProvider(weights_path=_onnx, conf_threshold=conf),
                            p, c)
                        lb_m = match_gt(gts, lb_preds)
                        lb_elapsed = round(time.perf_counter() - t0, 1)
                        lb_cells[ck].append(
                            {"sample_id": p["sample_id"], "n_gt": len(gts),
                             "n_pred": lb_m["n_pred"], "matched": lb_m["matched"],
                             "recall": lb_m["recall"], "precision": lb_m["precision"],
                             "inference_s": lb_elapsed})
                        entry["sides"][ck] = {
                            "preds": [{"xyxy": [round(v, 1) for v in b], "conf": round(cf, 4)}
                                      for b, cf in preds],
                            "matched": m["matched"], "n_pred": m["n_pred"],
                            "recall": m["recall"], "precision": m["precision"],
                            "pairs": m["pairs"], "gt_matched_flags": m["gt_matched_flags"],
                            "tile_stats": stats,
                            "letterbox_control": {
                                "preds": [{"xyxy": [round(v, 1) for v in b],
                                           "conf": round(cf, 4)} for b, cf in lb_preds],
                                "matched": lb_m["matched"], "n_pred": lb_m["n_pred"],
                                "recall": lb_m["recall"], "precision": lb_m["precision"],
                                "gt_matched_flags": lb_m["gt_matched_flags"]}}
                    per_sample.append(entry)
                    print(f"[gate-t3] {side}/{ds_name} {p['sample_id']}: "
                          + ", ".join(
                              f"conf{c}=tile {entry['sides'][str(c)]['matched']}"
                              f"/{len(gts)} (lb {entry['sides'][str(c)]['letterbox_control']['matched']})"
                              for c in CONFS)
                          + f" ({round(time.perf_counter() - t_ds, 1)}s)", flush=True)
                cell = {
                    "caliber": ("tile_ov128 冻结口径（tile 宽=页宽原生/高 1024/重叠 128/"
                                "末尾补页底锚点/页级跨 tile IoU 0.5 conf 降序贪心 NMS；"
                                "tile_calib.py tile 实现逐字）+ letterbox 整页对照并行"),
                    "gt_attr": GT_ATTR[ds_name],
                    "0.5": summarize_cell(per_conf_cells["0.5"]),
                    "0.2": summarize_cell(per_conf_cells["0.2"]),
                    "letterbox_control": {
                        "0.5": summarize_cell(lb_cells["0.5"]),
                        "0.2": summarize_cell(lb_cells["0.2"]),
                        "note": ("G2 冻结口径「letterbox 整页对照口径并行跑」；KO-TILE 结构性"
                                 "事实=整页 letterbox 下 SFX 亚像素化（0 召回复现预期）")},
                    "tile_stats_total": {
                        ck: {"n_tiles": sum(x["tile_stats"]["n_tiles"] for x in per_conf_cells[ck]),
                             "sfx_raw": sum(x["tile_stats"]["sfx_raw"] for x in per_conf_cells[ck]),
                             "sfx_after_page_nms": sum(x["tile_stats"]["sfx_after_page_nms"]
                                                       for x in per_conf_cells[ck])}
                        for ck in per_conf_cells},
                }
                matrix[side][ds_name] = cell
                write_raw(out_dir, side, ds_name, {
                    "task": "M2-SFX-GATE-T3 AC4 正式评测（三方×四数据集）",
                    "side": side, "dataset": ds_name,
                    "model": {"onnx": str(meta["onnx"]), "sha256": shas[side],
                              "note": meta["note"],
                              "inference": ("tile=生产序列本体（dsfx._letterbox+_sfx_boxes）"
                                            "每 tile；letterbox 对照=SfxDetectionProvider.detect"
                                            " 全序列")},
                    "caliber": cell["caliber"], "gt_attr": GT_ATTR[ds_name],
                    "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心（每 GT 至多一预测；"
                                "沿 eval_v2.py match_gt 逐字）",
                    "confs": {"0.5": "主口径（生产冻结）", "0.2": "宽松口径（仅诊断）"},
                    "summary": {"0.5": cell["0.5"], "0.2": cell["0.2"],
                                "letterbox_control": cell["letterbox_control"],
                                "tile_stats_total": cell["tile_stats_total"]},
                    "per_sample": per_sample,
                    "wording_discipline": "directional 评测，统计功效低；结论禁用「显著」；0 也如实",
                })
                print(f"[gate-t3] {side}/{ds_name}: conf0.5={cell['0.5']} "
                      f"lb={cell['letterbox_control']['0.5']} "
                      f"({round(time.perf_counter() - t_ds, 1)}s)", flush=True)
        finally:
            dsfx.SFX_WEIGHTS_SHA256 = pin_backup

    gt_counts = {
        "bj-exam": {"pages": len(exam_pages), "n_gt": 5},
        "bj-ext": {"pages": len(bj_pages), "n_gt": n_bj,
                   "attr_mix": {"derived": "8 页 18 框（R2/R3 判定链）",
                                "ai-direct": "4 页 15 框（R4-BJ32-35 补画）"}},
        "ko-tile": {"pages": len(ko_pages), "n_gt": n_ko},
        "ko-npd": {"pages": len(ko_pages), "n_gt": n_npd},
    }
    out = {
        "task": "M2-SFX-GATE-T3 AC4 正式评测（三方×四数据集矩阵）",
        "generated_at_utc": now_iso(),
        "generated_from": "experiments/M2-SFX-GATE-T3/eval_gate_t3.py",
        "mode": "smoke" if args.smoke else "full",
        "gate_ref": "verification/M2-SFX-GATE-T3/gate-definition.md v1.0-frozen §3/§4.G1/§4.G2",
        "weights": {side: {"onnx": str(m["onnx"]), "sha256": shas[side], "note": m["note"],
                           "imgsz": engines[side]["imgsz"] if side in engines else None,
                           "imgsz_source": engines[side]["imgsz_source"] if side in engines else None}
                    for side, m in SIDES.items()},
        "datasets": {
            "bj-exam": {**gt_counts["bj-exam"],
                        "caliber": "letterbox 现行口径（G1 主判据数据，考卷原始 5 框）",
                        "gt_attr": GT_ATTR["bj-exam"]},
            "bj-ext": {**gt_counts["bj-ext"],
                       "caliber": "letterbox 现行口径（G1 directional 扩展集；challenge/train 分列）",
                       "gt_attr": GT_ATTR["bj-ext"]},
            "ko-tile": {**gt_counts["ko-tile"],
                        "caliber": "tile_ov128 冻结口径+letterbox 对照（G2-A 采集一致性）",
                        "gt_attr": GT_ATTR["ko-tile"]},
            "ko-npd": {**gt_counts["ko-npd"],
                       "caliber": "tile_ov128 冻结口径+letterbox 对照（G2-B 模型质量）",
                       "gt_attr": GT_ATTR["ko-npd"]},
        },
        "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心（每 GT 至多一预测；"
                    "沿 eval_v2.py:68-97 逐字）",
        "confs": {"0.5": "主口径（生产冻结 SFX_CONF_THRESHOLD=0.5）",
                  "0.2": "宽松口径（仅诊断，不作硬 Gate 判据）"},
        "matrix": matrix,
        "npd_gt_source": {"path": str(NPD_GT), "total_boxes": n_npd,
                          "isolation_discipline": "任务书零既有坐标（npd-gt.json isolation_discipline PASS）"},
        "wording_discipline": "directional 评测，统计功效低；结论禁用「显著」；0 也如实",
    }
    out_matrix.parent.mkdir(parents=True, exist_ok=True)
    out_matrix.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[gate-t3] wrote {out_matrix}", flush=True)
    print("[gate-t3] MATRIX " + json.dumps(matrix, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
