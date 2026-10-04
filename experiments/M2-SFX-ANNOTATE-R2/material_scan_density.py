"""M2-SFX-ANNOTATE-R2 AC1：BJ/KO 候选页 chiqui7 SFX 密度扫描（生产推理序列）。

推理引擎只读复用 M2-SFX-ANNOTATE-R1 stage1_preannotate 的同款入口
（experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/conf_scan_diag.py，其内部复用
生产 src/infrastructure/providers/detection_sfx 序列；权重
M2-SFX-DETECT/weights/yolo11s-seg.onnx）。扫描口径沿 R1 scan：

- BJ 候选（R2 素材树 vol01/03/05/pages/ 均匀采样 54 页）：整页 letterbox；
- KO 候选（K11-K25 下载 15 页）：全宽 1024 高 tile、重叠 128（R1 K 域同款，
  对 1200x1660 页即 1-2 tile，无缩放原生分辨率）。

密度 = 去重后 sfx 类框数（R1 _dedup_boxes 同款贪心 NMS）。产出
training_data/sfx-v1/annotate-r2/scan/density-scan-material.json（候选页
排序证据；非 top 页留候选池）。

运行环境：M2-DOCTR-QUAL-C4-gpu-py312（onnxruntime）。
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

import numpy as np

R1_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode")
REPO_ROOT = Path(__file__).resolve().parents[2]
BJ_PAGES_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
KO_CAND_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "ko-candidates"
OUT_JSON = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "scan" / "density-scan-material.json"

K_TILE_H = 1024
K_TILE_OVERLAP = 128
CONF_FLOOR = 0.01


def load_scan_engine():
    spec = importlib.util.spec_from_file_location(
        "conf_scan_diag",
        R1_WORKTREE / "experiments" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "conf_scan_diag.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conf_scan_diag"] = mod
    spec.loader.exec_module(mod)
    return mod


def dedup_boxes(boxes: list[dict], iou_thr: float = 0.5) -> list[dict]:
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


def scan_page(run_inference, session, imgsz, rgb, mode: str) -> dict:
    page_w, page_h = rgb.size
    sfx_boxes: list[dict] = []
    count_by_class_total: dict[str, int] = {}
    n_tiles = 0
    t0 = time.perf_counter()
    if mode == "tile":
        ys = list(range(0, max(page_h - K_TILE_H, 0) + 1, K_TILE_H - K_TILE_OVERLAP))
        if not ys:
            ys = [0]
        if ys[-1] + K_TILE_H < page_h:
            ys.append(page_h - K_TILE_H)
        for y0 in ys:
            y1 = min(y0 + K_TILE_H, page_h)
            tile = rgb.crop((0, y0, page_w, y1))
            boxes, _scale, _shape = run_inference(session, np.asarray(tile), imgsz, float(page_w), float(y1 - y0))
            n_tiles += 1
            for b in boxes:
                count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
                if b["cls"] == "sfx":
                    sfx_boxes.append(
                        {"xyxy": [round(b["xyxy"][0], 1), round(b["xyxy"][1] + y0, 1),
                                  round(b["xyxy"][2], 1), round(b["xyxy"][3] + y0, 1)],
                         "conf": b["conf"]}
                    )
    else:  # fullpage letterbox
        boxes, _scale, _shape = run_inference(session, np.asarray(rgb), imgsz, float(page_w), float(page_h))
        n_tiles = 1
        for b in boxes:
            count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
            if b["cls"] == "sfx":
                sfx_boxes.append({"xyxy": b["xyxy"], "conf": b["conf"]})
    kept = dedup_boxes(sfx_boxes)
    return {
        "page_size": [page_w, page_h],
        "scan_mode": "tile_1024_overlap128" if mode == "tile" else "fullpage_letterbox",
        "n_tiles": n_tiles,
        "inference_s": round(time.perf_counter() - t0, 1),
        "count_by_class_all": count_by_class_total,
        "sfx_box_count_raw": len(sfx_boxes),
        "sfx_density_kept": len(kept),
        "sfx_boxes_kept": kept,
    }


def main() -> int:
    mod = load_scan_engine()
    run_inference = mod.run_inference
    session, imgsz, imgsz_source, _raw = mod._build_engine(Path(mod.SFX_WEIGHTS_DEFAULT))
    print(f"engine OK imgsz={imgsz} ({imgsz_source}) weights={mod.SFX_WEIGHTS_DEFAULT}")

    targets: list[tuple[str, str, Path]] = []  # (source_id, mode, path)
    for volume in (1, 3, 5):
        pages_dir = BJ_PAGES_ROOT / f"vol{volume:02d}" / "pages"
        for p in sorted(pages_dir.glob("vol*_p*.png")):
            targets.append((p.stem, "bj_fullpage", p))
    for p in sorted(KO_CAND_DIR.glob("K*_*.png")):
        targets.append((p.stem, "ko_tile", p))
    print(f"scan targets: {len(targets)} ({sum(1 for t in targets if t[1] == 'bj_fullpage')} BJ + "
          f"{sum(1 for t in targets if t[1] == 'ko_tile')} KO)")

    out = {
        "tool": "experiments/M2-SFX-ANNOTATE-R2/material_scan_density.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "weights": str(mod.SFX_WEIGHTS_DEFAULT),
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "conf_floor": CONF_FLOOR,
        "note": "R2 AC1 素材候选池密度扫描：BJ=整页 letterbox（R1 BJ 域同口径），KO=全宽 1024 tile 重叠 128（R1 K 域同口径）；密度=去重后 sfx 框数",
        "pages": {},
    }
    t_all = time.perf_counter()
    for source_id, mode, path in targets:
        with Image.open(path) as im:
            rgb = im.convert("RGB")
        result = scan_page(run_inference, session, imgsz, rgb, "tile" if mode == "ko_tile" else "fullpage")
        result["source_id"] = source_id
        result["mode"] = mode
        result["page"] = str(path)
        out["pages"][source_id] = result
        print(f"scan {source_id}: {result['page_size'][0]}x{result['page_size'][1]} tiles={result['n_tiles']} "
              f"sfx_raw={result['sfx_box_count_raw']} kept={result['sfx_density_kept']} {result['inference_s']}s")
        rgb.close()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    bj_rank = sorted(((v["sfx_density_kept"], k) for k, v in out["pages"].items() if v["mode"] == "bj_fullpage"),
                     reverse=True)
    ko_rank = sorted(((v["sfx_density_kept"], k) for k, v in out["pages"].items() if v["mode"] == "ko_tile"),
                     reverse=True)
    print("\n=== BJ density ranking (top 15) ===")
    for d, k in bj_rank[:15]:
        print(f"{k}\tkept={d}")
    print("\n=== KO density ranking (all 15) ===")
    for d, k in ko_rank:
        print(f"{k}\tkept={d}")
    print(f"\nwrote {OUT_JSON} ({round(time.perf_counter() - t_all, 1)}s total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
