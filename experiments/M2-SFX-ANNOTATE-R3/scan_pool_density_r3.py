"""M2-SFX-ANNOTATE-R3 AC1：BJ 候选池 44 页 chiqui7 SFX 密度扫描（生产推理序列）。

沿 R2 material_scan_density.py 口径（experiments/M2-SFX-ANNOTATE-R2/
material_scan_density.py 只读模式复刻，targeted 到 R3 候选池）：

- 候选池 = R2 素材树 54 张渲染页中未入池的 44 张（vol01 16 / vol03 15 /
  vol05 13，M2-SFX-ANNOTATE-R3 合同已核实口径）。池定义就地推导：R2 素材根
  pages/ 全量 54 张 − cases.json（本仓库）已登记 BJ16-25 的 10 张 source_id；
  推导结果与 R2 selection material-selection.json 的 bj_runner_up_pool
  （44 项，只读对照）断言逐项一致后才使用。
- BJ 候选整页 letterbox（R1/R2 BJ 域同口径）；密度 = 去重后 sfx 类框数
  （R1 _dedup_boxes 同款贪心 NMS IoU 0.5）；conf floor 0.01。
- 推理引擎只读 import 复用本仓库 experiments/M2-SFX-DETECT-DOMAIN-EXT-DIAG/
  conf_scan_diag.py（其内部复用生产 src/infrastructure/providers/detection_sfx
  序列；权重 G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx）。

产出 training_data/sfx-v1/annotate-r3/scan/density-scan-pool.json（候选页排序
证据；非 top 页留池）。运行环境：M2-SFX-FINETUNE-gpu-py312 venv
（onnxruntime）。

纪律：零 src 修改；R2/R1 worktree 与数据只读引用；素材树只读（本轮 PNG 由
material_select_r3.py 复制落位，本脚本不写素材树）；产出数据本体落
training_data/sfx-v1/annotate-r3/（gitignored），Git 只进脚本与 cases.json
追加。
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
BJ_ASSET_ROOT_R2 = (
    R2_WORKTREE / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
)
CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
R2_MATERIAL_SELECTION = (
    R2_WORKTREE / "training_data" / "sfx-v1" / "annotate-r2" / "selection" / "material-selection.json"
)
OUT_JSON = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / "scan" / "density-scan-pool.json"

SEED = 20261004  # splits.SEED_DEFAULT（R1/R2/R3 冻结同款）
CONF_FLOOR = 0.01

EXPECTED_POOL = {"vol01": 16, "vol03": 15, "vol05": 13}
REGISTERED_BJ_16_25 = [f"BJ{i:02d}" for i in range(16, 26)]


def load_scan_engine():
    """只读 import 复用本仓库 conf_scan_diag（其内部复用生产 detection_sfx 序列）。"""
    spec = importlib.util.spec_from_file_location(
        "conf_scan_diag",
        REPO_ROOT / "experiments" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "conf_scan_diag.py",
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


def build_pool() -> list[str]:
    """候选池就地推导：R2 素材根 54 张 − cases.json 已登记 BJ16-25 的 10 张 = 44 张。"""
    cases = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    registered = {c["source_id"] for c in cases["cases"] if c["case_id"] in REGISTERED_BJ_16_25}
    if len(registered) != 10:
        raise RuntimeError(f"cases.json BJ16-25 登记数异常: {len(registered)} != 10")

    all_pages: list[str] = []
    for volume in (1, 3, 5):
        pages_dir = BJ_ASSET_ROOT_R2 / f"vol{volume:02d}" / "pages"
        found = sorted(p.stem for p in pages_dir.glob("vol*_p*.png"))
        all_pages.extend(found)
    pool = sorted(s for s in all_pages if s not in registered)

    by_vol: dict[str, int] = {}
    for s in pool:
        by_vol[s[:5]] = by_vol.get(s[:5], 0) + 1
    if by_vol != EXPECTED_POOL:
        raise RuntimeError(f"候选池 vol 分布异常: {by_vol} != {EXPECTED_POOL}")

    r2_sel = json.loads(R2_MATERIAL_SELECTION.read_text(encoding="utf-8"))
    r2_pool = sorted(e["source_id"] for e in r2_sel["bj_runner_up_pool"])
    if pool != r2_pool:
        missing = set(r2_pool) - set(pool)
        extra = set(pool) - set(r2_pool)
        raise RuntimeError(f"候选池与 R2 bj_runner_up_pool 不一致: missing={missing} extra={extra}")
    print(f"pool OK: {len(pool)} pages {by_vol}（与 R2 bj_runner_up_pool 44 项逐项一致）")
    return pool


def main() -> int:
    mod = load_scan_engine()
    run_inference = mod.run_inference
    session, imgsz, imgsz_source, _raw = mod._build_engine(Path(mod.SFX_WEIGHTS_DEFAULT))
    print(f"engine OK imgsz={imgsz} ({imgsz_source}) weights={mod.SFX_WEIGHTS_DEFAULT}")

    pool = build_pool()
    out = {
        "tool": "experiments/M2-SFX-ANNOTATE-R3/scan_pool_density_r3.py",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "weights": str(mod.SFX_WEIGHTS_DEFAULT),
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "conf_floor": CONF_FLOOR,
        "seed": SEED,
        "note": "R3 AC1 候选池密度扫描：44 张未入池页（R2 素材树 54 张 − BJ16-25 已入池 10 张；与 R2 "
                "material-selection.json bj_runner_up_pool 逐项对照一致）整页 letterbox（R1/R2 BJ 域同口径）；"
                "密度=去重后 sfx 框数；排序=密度降序 → sha256(seed:source_id) 升序决胜，密度并列组另做目检"
                "毛笔形态二次决胜（material_select_r3.py 登记理由）",
        "pages": {},
    }
    t_all = time.perf_counter()
    for source_id in pool:
        page_path = BJ_ASSET_ROOT_R2 / source_id[:5] / "pages" / f"{source_id}.png"
        with Image.open(page_path) as im:
            rgb = im.convert("RGB")
        page_w, page_h = rgb.size
        t0 = time.perf_counter()
        boxes_raw, _scale, _shape = run_inference(session, np.asarray(rgb), imgsz, float(page_w), float(page_h))
        elapsed = round(time.perf_counter() - t0, 1)
        sfx_boxes: list[dict] = []
        count_by_class_total: dict[str, int] = {}
        for b in boxes_raw:
            count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
            if b["cls"] == "sfx":
                sfx_boxes.append({"xyxy": b["xyxy"], "conf": b["conf"]})
        kept = dedup_boxes(sfx_boxes)
        out["pages"][source_id] = {
            "source_id": source_id,
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "scan_mode": "fullpage_letterbox",
            "n_tiles": 1,
            "inference_s": elapsed,
            "count_by_class_all": count_by_class_total,
            "sfx_box_count_raw": len(sfx_boxes),
            "sfx_density_kept": len(kept),
            "sfx_boxes_kept": kept,
        }
        print(f"scan {source_id}: {page_w}x{page_h} sfx_raw={len(sfx_boxes)} kept={len(kept)} {elapsed}s")
        rgb.close()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

    rank = sorted(
        (
            (v["sfx_density_kept"], hashlib.sha256(f"{SEED}:{k}".encode("utf-8")).hexdigest(), k)
            for k, v in out["pages"].items()
        ),
        reverse=False,
    )
    rank.sort(key=lambda t: (-t[0], t[1]))
    print("\n=== candidate pool density ranking (44, seed-tiebreak) ===")
    for i, (d, h, k) in enumerate(rank, 1):
        print(f"{i:02d}\t{k}\tkept={d}\ttiebreak={h[:12]}")
    print(f"\nwrote {OUT_JSON} ({round(time.perf_counter() - t_all, 1)}s total)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
