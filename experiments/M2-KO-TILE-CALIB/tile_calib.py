"""M2-KO-TILE-CALIB：KO 长条页推理口径校准实验（AC1+AC2：2 权重 × 2 口径）。

背景（T2-V2 结构性发现，merge 784e585b）：KO 长条 webtoon 页（690×51971~100480
与 600×18401，aspect 1:31~1:146）在整页 letterbox 1024 生产序列下 SFX 亚像素化，
三方权重全 0/56 含现役 chiqui7——瓶颈=推理序列口径（tile 切块 vs letterbox）
非模型权重。本实验量化该差异，供 AC3 KO 域 Gate 评测口径提案（T3 采信）。

四组（2 权重 × 2 口径）：

  权重  chiqui7 现役 = 生产 pin d87389af… 所指
        G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx
        （sha 先验断言逐字等于 pin，零重指）
        v2b = M2-SFX-TRAIN-V2 产物
        G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1/
        train-v2/weights/v2b/best.onnx（sha 先验断言前缀 944e8114，
        进程内重指 pin 沿 eval_v2.py:179 先例，src 零改动）
  口径  letterbox = 生产序列原样（SfxDetectionProvider.detect 全序列，
        逐字沿 eval_v2.py:197-201 的调用方式；基线=已知 0/56）
        tile = 沿 R1 scan_mode=tile_690x1024_overlap128
        （experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py:238-251 只读
        复刻）：tile 宽=页宽原生无缩放、tile 高 1024、重叠 128（步长 896）、
        末尾补 page_h-1024 保证覆盖页底；每 tile 经生产序列推理
        （dsfx._letterbox + dsfx._sfx_boxes，conf 过滤口径先于类无关 NMS 0.7、
        sfx 类后过滤、/scale 映射+clip——与 letterbox 口径唯一差异=成像口径），
        框映射回原页坐标（y+y0 平移，R1 先例逐字），页级跨 tile IoU 0.5
        conf 降序贪心 NMS 去重（R1 _dedup_boxes 逐字，stage1_preannotate.py:
        172-191）。

预处理逐字对照（生命线，登记于 verification/M2-KO-TILE-CALIB/
preprocess-caliber-table.md）：letterbox 语义（min-scale/round/PIL BILINEAR/
top-left paste 114 灰/非居中）、归一化（/255 float32 CHW）、RGB 顺序
（PIL convert("RGB")）、conf 语义（cls_scores post-sigmoid 无激活、argmax/
max）全部复用生产模块函数本体（dsfx._letterbox/_sfx_boxes），不做第二实现。

匹配：conf≥0.5（生产冻结）/≥0.2（宽松）双口径，每口径独立完整推理序列
（生产语义：conf filter 在 NMS 竞争集之前，沿 eval_v2.py per-conf provider
先例），box IoU≥0.5 conf 降序贪心（match_gt 逐字沿 eval_v2.py:68-97）。

GT：M2-SFX-ANNOTATE-R2 final manifest.{val,test}.json（只读）KO 4 页
pre-k01/k02/k08/k09 共 56 框；逐页图像 sha256 对 manifest 断言。

产物：verification/M2-KO-TILE-CALIB/raw/eval-{chiqui7,v2b}-{letterbox,tile}.json
（逐框明细）+ eval-matrix.json（四组矩阵）+ preprocess-caliber-table.md +
ko-caliber-proposal.md（AC3）。零 src：生产模块只读 import，进程内重指 pin
为 eval_v2.py 先例形态。

纪律：directional 评测，统计功效低，禁用「显著」；0 也如实。
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

R2_FINAL = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode"
    r"/training_data/sfx-v1/annotate-r2/final"
)
PROD_ONNX = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx")
PROD_PIN_SHA = "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"
V2B_ONNX = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode/training_data/sfx-v1"
    r"/train-v2/weights/v2b/best.onnx"
)
V2B_SHA_PREFIX = "944e8114"

RAW_OUT = REPO / "verification" / "M2-KO-TILE-CALIB" / "raw"
OUT_JSON_MATRIX = REPO / "verification" / "M2-KO-TILE-CALIB" / "eval-matrix.json"
OUT_CALIBER_TABLE = (
    REPO / "verification" / "M2-KO-TILE-CALIB" / "preprocess-caliber-table.md"
)
OUT_PROPOSAL = REPO / "verification" / "M2-KO-TILE-CALIB" / "ko-caliber-proposal.md"
SMOKE_OUT = REPO / "training_data" / "sfx-v1" / "ko-tile-calib" / "smoke"

KO_SAMPLE_IDS = ("pre-k01", "pre-k02", "pre-k08", "pre-k09")
EXPECTED_GT_BOXES = 56

# R1 tile 几何（experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py:156-157）
K_TILE_H = 1024
K_TILE_OVERLAP = 128
# 页级跨 tile 去重阈值（R1 _dedup_boxes 默认 iou_thr=0.5，同文件 :172）
TILE_PAGE_NMS_IOU = 0.5

CONFS = (0.5, 0.2)
IOU_MATCH = 0.5


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

    逐字复刻 R1 experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py:172-191
    （_dedup_boxes，只读引用；本实验脚本自包含，不 import 跨 worktree 模块）。
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


def tile_ys(page_h: int) -> list[int]:
    """R1 tile y 锚点序列，逐字复刻 stage1_preannotate.py:240-245：
    步长 K_TILE_H-K_TILE_OVERLAP，末尾补 page_h-K_TILE_H 保证覆盖页底。
    """
    ys = list(range(0, max(page_h - K_TILE_H, 0) + 1, K_TILE_H - K_TILE_OVERLAP))
    if not ys:
        ys = [0]
    if ys[-1] + K_TILE_H < page_h:
        ys.append(page_h - K_TILE_H)
    return ys


def load_gt_pages() -> list[dict]:
    """R2 final manifest.{val,test}.json 只读加载 KO 4 页（GT 56 框）。

    逐页断言：图像存在、尺寸与 manifest 一致、图像 sha256 与 manifest 一致。
    """
    import numpy
    from PIL import Image
    from ports.detection.ports import DetectionRequest

    pages: list[dict] = []
    n_boxes = 0
    for split in ("val", "test"):
        m = json.loads((R2_FINAL / f"manifest.{split}.json").read_text(encoding="utf-8"))
        for s in m["samples"]:
            if s["sample_id"] not in KO_SAMPLE_IDS:
                continue
            img = s["image"]
            p = Path(img["path"])
            assert p.is_file(), f"{s['sample_id']}: 页面缺失 {p}"
            assert sha256_file(p) == img["sha256"], f"{s['sample_id']}: 图像 sha256 与 manifest 不一致"
            rgb_t = Image.open(p).convert("RGB")
            w, h = rgb_t.size
            assert (w, h) == (img["width"], img["height"]), \
                f"{s['sample_id']}: 尺寸 {w}x{h} != manifest {img['width']}x{img['height']}"
            rgb_t.close()
            gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
            n_boxes += len(gts)
            pages.append({
                "sample_id": s["sample_id"],
                "case_id": s["provenance"].get("case_id"),
                "split": split,
                "img": p,
                "w": w, "h": h,
                "request": DetectionRequest(
                    page_id=s["sample_id"],
                    image_bytes=numpy.asarray(
                        Image.open(p).convert("RGB"), dtype=numpy.uint8).tobytes(),
                    width=w, height=h),
                "gts": gts,
                "gt_meta": [
                    {"unit_id": (s["provenance"].get("boxes_meta") or [{}])[i].get("unit_id"),
                     "conf": (s["provenance"].get("boxes_meta") or [{}])[i].get("conf")}
                    for i in range(len(gts))],
            })
    ids = [p["sample_id"] for p in pages]
    assert sorted(ids) == sorted(KO_SAMPLE_IDS), f"KO 页集合不符：{ids}"
    assert n_boxes == EXPECTED_GT_BOXES, f"GT 总框数 {n_boxes} != {EXPECTED_GT_BOXES}"
    return pages


def run_letterbox_caliber(provider_factory, page: dict, conf: float) -> list[tuple[list[float], float]]:
    """口径①整页 letterbox：生产序列原样（SfxDetectionProvider.detect）。

    逐字沿 eval_v2.py:197-201 的调用与坐标提取方式。
    """
    provider = provider_factory(conf)
    res = provider.detect(page["request"])
    return [(list(map(float, (cd.polygon[0][0], cd.polygon[0][1],
                              cd.polygon[2][0], cd.polygon[2][1]))),
             float(cd.confidence)) for cd in res.candidates]


def run_tile_caliber(dsfx, session, imgsz, page: dict, conf: float, log) -> tuple[
        list[tuple[list[float], float]], dict]:
    """口径②tile 切块：R1 tile 几何 + 每 tile 生产序列推理 + 页级跨 tile NMS。

    - tile 几何：stage1_preannotate.py:238-251 逐字（tile 宽=页宽原生、
      高 1024、步长 896、末尾补页底锚点、y+y0 平移回页坐标）；
    - 每 tile 推理 = 生产序列本体（dsfx._letterbox + dsfx._sfx_boxes，
      conf 过滤口径先于类无关 NMS 0.7、sfx 类后过滤、/scale 映射+clip 到
      tile 界）——与 letterbox 口径唯一差异=成像口径本身；
    - 页级：dedup_boxes（R1 _dedup_boxes 逐字，IoU 0.5 conf 降序贪心）。
    """
    import numpy
    from PIL import Image

    page_w, page_h = page["w"], page["h"]
    ys = tile_ys(page_h)
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


def summarize_cell(per_page_cells: list[dict]) -> dict:
    gt = sum(c["n_gt"] for c in per_page_cells)
    matched = sum(c["matched"] for c in per_page_cells)
    n_pred = sum(c["n_pred"] for c in per_page_cells)
    return {"matched": f"{matched}/{gt}",
            "recall_rate": round(matched / gt, 4) if gt else None,
            "precision": round(matched / n_pred, 4) if n_pred else None,
            "n_pred": n_pred}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true",
                        help="冒烟：仅 pre-k02（最小页 21 tiles），产物落 gitignored smoke 目录")
    args = parser.parse_args()
    out_dir = SMOKE_OUT if args.smoke else RAW_OUT
    out_matrix = (SMOKE_OUT / "eval-matrix.json") if args.smoke else OUT_JSON_MATRIX

    import numpy
    from PIL import Image

    # 受控本地素材（超长 webtoon 最大 ~69MP）显式解除 PIL 警戒线（R1 先例
    # stage1_preannotate.py:37-38）并留痕。
    Image.MAX_IMAGE_PIXELS = None

    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    print(f"[tile-calib] start {now_iso()} mode={'smoke' if args.smoke else 'full'}", flush=True)

    # 权重先验断言（加载前）
    prod_sha = sha256_file(PROD_ONNX)
    assert prod_sha == PROD_PIN_SHA, f"chiqui7 权重 sha {prod_sha} != 生产 pin {PROD_PIN_SHA}"
    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha.startswith(V2B_SHA_PREFIX), \
        f"v2b 权重 sha {v2b_sha} 前缀 != {V2B_SHA_PREFIX}"
    print(f"[tile-calib] chiqui7 onnx sha256={prod_sha}（== 生产 pin，零重指）", flush=True)
    print(f"[tile-calib] v2b onnx sha256={v2b_sha}（前缀 {V2B_SHA_PREFIX} 断言过）", flush=True)

    pages = load_gt_pages()
    if args.smoke:
        pages = [p for p in pages if p["sample_id"] == "pre-k02"]
        assert len(pages) == 1
    for p in pages:
        print(f"[tile-calib] page {p['sample_id']} ({p['split']}) {p['w']}x{p['h']} "
              f"gt={len(p['gts'])} tiles={len(tile_ys(p['h']))}", flush=True)

    # 两个 session 各建一次（metadata names/imgsz 断言在 _build_engine 内逐权重执行）。
    # chiqui7：pin 原样零重指；v2b：进程内重指 pin（eval_v2.py:179 先例），用后恢复。
    engines: dict[str, dict] = {}
    engines["chiqui7"] = {
        "onnx": PROD_ONNX, "sha": prod_sha,
        "note": "生产现役权重（pin d87389af… 逐字核对），pin 原样零重指",
        **dict(zip(("session", "imgsz", "imgsz_source", "imgsz_raw"),
                   dsfx._build_engine(PROD_ONNX))),
    }
    pin_backup = dsfx.SFX_WEIGHTS_SHA256
    try:
        dsfx.SFX_WEIGHTS_SHA256 = v2b_sha  # 进程内重指（eval_v2.py:179 先例；src 零改动）
        engines["v2b"] = {
            "onnx": V2B_ONNX, "sha": v2b_sha,
            "note": "T2-V2 产物 best.onnx（sha 前缀 944e8114 断言过），进程内重指 pin",
            **dict(zip(("session", "imgsz", "imgsz_source", "imgsz_raw"),
                       dsfx._build_engine(V2B_ONNX))),
        }
    finally:
        dsfx.SFX_WEIGHTS_SHA256 = pin_backup
    for side, e in engines.items():
        print(f"[tile-calib] engine {side}: imgsz={e['imgsz']} ({e['imgsz_source']})", flush=True)

    sides = ("chiqui7", "v2b")
    calibers = ("letterbox", "tile")
    matrix: dict[str, dict[str, dict]] = {s: {c: {} for c in calibers} for s in sides}
    detail: dict[str, dict[str, dict]] = {s: {c: {} for c in calibers} for s in sides}

    for side in sides:
        e = engines[side]
        if side == "v2b":
            dsfx.SFX_WEIGHTS_SHA256 = v2b_sha
        try:
            for caliber in calibers:
                t_cal = time.perf_counter()
                per_conf_pages: dict[str, list[dict]] = {str(c): [] for c in CONFS}
                for p in pages:
                    for c in CONFS:
                        ck = str(c)
                        if caliber == "letterbox":
                            provider_factory = (
                                lambda conf, _onnx=e["onnx"]:
                                SfxDetectionProvider(weights_path=_onnx, conf_threshold=conf))
                            t0 = time.perf_counter()
                            preds = run_letterbox_caliber(provider_factory, p, c)
                            stats = None
                        else:
                            t0 = time.perf_counter()
                            preds, stats = run_tile_caliber(
                                dsfx, e["session"], e["imgsz"], p, c, print)
                        m = match_gt(p["gts"], preds)
                        elapsed = round(time.perf_counter() - t0, 1)
                        cell = {"sample_id": p["sample_id"],
                                "n_gt": len(p["gts"]), "n_pred": m["n_pred"],
                                "matched": m["matched"], "recall": m["recall"],
                                "precision": m["precision"], "inference_s": elapsed}
                        if stats is not None:
                            cell["tile_stats"] = {k: v for k, v in stats.items() if k != "per_tile"}
                            cell["tile_stats"]["n_tiles_conf_runs"] = stats["n_tiles"]
                        per_conf_pages[ck].append(cell)
                        print(f"[tile-calib] {side}/{caliber}/conf{ck} {p['sample_id']}: "
                              f"matched={m['matched']}/{len(p['gts'])} n_pred={m['n_pred']} "
                              f"{elapsed}s", flush=True)
                        detail[side][caliber].setdefault(ck, {"per_page": []})["per_page"].append({
                            "sample_id": p["sample_id"],
                            "gt": p["gt_meta"],
                            "gt_matched_flags": m["gt_matched_flags"],
                            "pairs": m["pairs"],
                            "preds": [{"xyxy": [round(v, 1) for v in b],
                                       "conf": round(cf, 4)} for b, cf in preds],
                            **({"tile_stats": stats} if stats is not None else {}),
                        })
                for ck in per_conf_pages:
                    matrix[side][caliber][ck] = summarize_cell(per_conf_pages[ck])
                print(f"[tile-calib] {side}/{caliber}: " +
                      json.dumps({ck: matrix[side][caliber][ck] for ck in matrix[side][caliber]},
                                 ensure_ascii=False) +
                      f" ({round(time.perf_counter() - t_cal, 1)}s)", flush=True)
        finally:
            dsfx.SFX_WEIGHTS_SHA256 = pin_backup

    out = {
        "task": "M2-KO-TILE-CALIB AC1+AC2（KO 长条页 tile vs letterbox 口径对照）",
        "generated_at_utc": now_iso(),
        "mode": "smoke" if args.smoke else "full",
        "gt_source": {
            "manifests": [str(R2_FINAL / f"manifest.{s}.json") for s in ("val", "test")],
            "pages": {p["sample_id"]: {"split": p["split"], "size": [p["w"], p["h"]],
                                       "n_gt": len(p["gts"]),
                                       "aspect": f"1:{round(p['h'] / p['w'])}"}
                      for p in pages},
            "n_gt_total": sum(len(p["gts"]) for p in pages),
            "image_sha256_asserted": True,
        },
        "weights": {side: {"onnx": str(e["onnx"]), "sha256": e["sha"], "note": e["note"],
                           "imgsz": e["imgsz"], "imgsz_source": e["imgsz_source"]}
                    for side, e in engines.items()},
        "calibers": {
            "letterbox": "生产序列原样 SfxDetectionProvider.detect（letterbox 1024/类无关 NMS 0.7/sfx 过滤/CPUExecutionProvider）",
            "tile": f"R1 tile_690x1024_overlap128 复刻：tile 宽=页宽原生无缩放、高 {K_TILE_H}、重叠 {K_TILE_OVERLAP}（步长 {K_TILE_H - K_TILE_OVERLAP}、末尾补页底锚点）；每 tile 生产序列本体推理（dsfx._letterbox+_sfx_boxes）；页级跨 tile IoU {TILE_PAGE_NMS_IOU} conf 降序贪心 NMS（R1 _dedup_boxes 逐字）",
        },
        "matching": f"box IoU>={IOU_MATCH}，pred conf 降序贪心（每 GT 至多一预测；沿 eval_v2.py match_gt 逐字）",
        "confs": {"0.5": "生产冻结", "0.2": "宽松口径"},
        "matrix": matrix,
        "wording_discipline": "directional 评测，统计功效低；结论禁用「显著」；0 也如实",
    }
    for side in sides:
        for caliber in calibers:
            doc = dict(out)
            doc["side"] = side
            doc["caliber"] = caliber
            doc["matrix_cell"] = matrix[side][caliber]
            doc["per_sample"] = detail[side][caliber]
            fname = f"eval-{side}-{caliber}.json"
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / fname).write_text(
                json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"[tile-calib] wrote {out_dir / fname}", flush=True)

    out_matrix.parent.mkdir(parents=True, exist_ok=True)
    out_matrix.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[tile-calib] wrote {out_matrix}", flush=True)
    print(f"[tile-calib] MATRIX " + json.dumps(matrix, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
