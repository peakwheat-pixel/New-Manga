"""M2-SFX-T5-TILE-KO AC3: production tile-branch bit-parity verification.

Goal (Task AC3, the implementation-equivalence hard evidence): the
PRODUCTION SfxDetectionProvider.detect tile branch (src/infrastructure/
providers/detection_sfx.py) reproduces the T3 evaluation matrix numbers
bit-for-bit on the KO 4-page exam —

- v2b     35/56 (derived GT)  + 48/135 (non-derived npd GT)
- chiqui7 56/56 (derived GT)  + 41/135 (non-derived npd GT)

plus the letterbox zero-change proof: the BJ exam pages (pre-bj17/pre-bj18,
chiqui7 pin) re-run through the production letterbox path reproduce the T3
raw eval-chiqui7-bj-exam.json predictions verbatim (round-precision, the
precision the T3 raw JSON was written at).

Data loading and matching replicate eval_gate_t3.py verbatim (read-only
blueprint): load_ko_pages (R2 final manifest val/test, sha/size assertions,
npd crosscheck), match_gt / iou_xyxy / poly_to_xyxy (eval_v2.py lineage).
The script is self-contained by the tile_calib discipline — no import across
worktrees; the production module is imported from THIS worktree's src.

Weights (Task contract: no weight change in this Task):
- v2b     : the production pin (944e8114...) AS-IS, weights-v2b path;
- chiqui7 : the rollback weights at weights/yolo11s-seg.onnx (sha d87389af...
            asserted BEFORE load), run through the in-process pin re-point
            (eval_v2.py:179 / tile_calib.py:374-382 / eval_gate_t3.py
            precedent): assert-then-repoint, finally-restore, zero src/env
            changes.

Performance (AC2 CPU face) rides the same run: every detect's elapsed_ms is
recorded (CPUExecutionProvider, the production EP).

Output: verification/M2-SFX-T5-TILE-KO/raw/parity-{side}.json per weight +
parity-summary.json (the matrix with matched numbers, parity flags and
per-page timings).

Wording discipline: directional evidence, low statistical power; the word
"significant" is banned; zeros are recorded as zeros.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RAW_OUT = REPO / "verification" / "M2-SFX-T5-TILE-KO" / "raw"

#: Production weights (v2b pin, AS-IS) and the chiqui7 rollback file.
V2B_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
CHIQUI7_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx"
)
PROD_PIN_SHA = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)
CHIQUI7_PIN_SHA = (
    "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"
)

#: GT / page data (gitignored external trees; T3 eval reading, verbatim).
R2_FINAL = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data"
    r"/sfx-v1/annotate-r2/final"
)
NPD_GT = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode/training_data"
    r"/sfx-v1/gate-t3/npd-gt.json"
)
TRAIN_V4 = Path(
    r"G:/CODEX/New Manga.worktrees/M2-SFX-GATE-T3-zcode/training_data"
    r"/sfx-v1/train-v4"
)
#: The T3 raw evidence this run must reproduce (committed in THIS repo).
T3_RAW = REPO / "verification" / "M2-SFX-GATE-T3" / "raw"

KO_IDS = ("pre-k01", "pre-k02", "pre-k08", "pre-k09")
EXPECT_KO_DERIVED_BOXES = 56
EXPECT_NPD_BOXES = 135
EXAM_IDS = ("pre-bj17", "pre-bj18")

#: The T3 matrix numbers to reproduce bit-for-bit (conf 0.5 main caliber).
EXPECTED = {
    "v2b": {"ko-tile": 35, "ko-npd": 48},
    "chiqui7": {"ko-tile": 56, "ko-npd": 41},
}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Matching caliber — eval_gate_t3.py verbatim (eval_v2.py lineage)
# --------------------------------------------------------------------------


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


IOU_MATCH = 0.5


def match_gt(gt_boxes, preds) -> dict:
    """Greedy: preds conf-descending, each GT at most one pred, each pred at
    most one GT, IoU >= 0.5 — eval_gate_t3.py match_gt verbatim."""
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
            pairs.append(
                {
                    "gt_index": best[1],
                    "pred_index": pi,
                    "iou": round(best[0], 4),
                    "pred_conf": round(pconf, 4),
                }
            )
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


# --------------------------------------------------------------------------
# Data loading — eval_gate_t3.py load_ko_pages / load_bj_pages verbatim
# --------------------------------------------------------------------------


def load_ko_pages() -> list[dict]:
    import numpy
    from PIL import Image
    from ports.detection.ports import DetectionRequest

    npd = _read(NPD_GT)
    cc = npd["derived_gt_crosscheck"]["per_page"]
    npd_boxes = {
        pid: [b["xyxy"] for b in npd["pages"][pid]["boxes"]] for pid in npd["pages"]
    }
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
            assert sha256_file(p) == img["sha256"], (
                f"{s['sample_id']}: 图像 sha256 与 manifest 不一致"
            )
            rgb_t = Image.open(p).convert("RGB")
            w, h = rgb_t.size
            assert (w, h) == (img["width"], img["height"]), (
                f"{s['sample_id']}: 尺寸 {w}x{h} != manifest"
            )
            rgb_t.close()
            sid = s["sample_id"]
            assert cc[sid]["page_wh"] == [w, h], f"{sid}: npd crosscheck page_wh"
            gts = [poly_to_xyxy(b["polygon"]) for b in s["boxes"]]
            n_boxes += len(gts)
            pages.append(
                {
                    "sample_id": sid,
                    "split": split,
                    "img": p,
                    "w": w,
                    "h": h,
                    "request": DetectionRequest(
                        page_id=sid,
                        image_bytes=numpy.asarray(
                            Image.open(p).convert("RGB"), dtype=numpy.uint8
                        ).tobytes(),
                        width=w,
                        height=h,
                    ),
                    "gts": gts,
                    "gts_npd": npd_boxes[sid],
                }
            )
    ids = [p["sample_id"] for p in pages]
    assert sorted(ids) == sorted(KO_IDS), f"KO 页集合不符：{ids}"
    assert n_boxes == EXPECT_KO_DERIVED_BOXES, f"KO 派生 GT {n_boxes} != 56"
    return pages


def load_exam_pages() -> list[dict]:
    """BJ exam pages (pre-bj17/pre-bj18) from the train-v4 challenge tree,
    sha-asserted against the manifest (load_bj_pages exam face)."""
    import numpy
    from PIL import Image
    from ports.detection.ports import DetectionRequest

    chal = _read(TRAIN_V4 / "manifest.challenge.json")
    pages = []
    for s in chal["samples"]:
        if s["sample_id"] not in EXAM_IDS:
            continue
        img_path = None
        for ext in (".png", ".jpg", ".jpeg"):
            p = TRAIN_V4 / "dataset" / "images" / s["split"] / f"{s['sample_id']}{ext}"
            if p.is_file():
                img_path = p
                break
        assert img_path is not None, f"{s['sample_id']}: train-v4 树无页图"
        assert sha256_file(img_path) == s["image"]["sha256"], (
            f"{s['sample_id']}: dataset 页图 sha 失配"
        )
        rgb = Image.open(img_path).convert("RGB")
        w, h = rgb.size
        pages.append(
            {
                "sample_id": s["sample_id"],
                "img": img_path,
                "w": w,
                "h": h,
                "request": DetectionRequest(
                    page_id=s["sample_id"],
                    image_bytes=numpy.asarray(rgb, dtype=numpy.uint8).tobytes(),
                    width=w,
                    height=h,
                ),
            }
        )
        rgb.close()
    ids = sorted(p["sample_id"] for p in pages)
    assert ids == sorted(EXAM_IDS), f"考卷页集合不符：{ids}"
    return pages


def t3_preds(side: str, ds: str, sample_id: str) -> list[dict]:
    """The T3 raw per-sample predictions at the written precision
    (xyxy round 0.1, conf round 4) — the parity target."""
    doc = _read(T3_RAW / f"eval-{side}-{ds}.json")
    for entry in doc["per_sample"]:
        if entry["sample_id"] == sample_id:
            return entry["sides"]["0.5"]["preds"]
    raise AssertionError(f"T3 raw {side}/{ds} 无 {sample_id}")


def production_preds(result) -> list[dict]:
    """Production candidates at the SAME written precision as the T3 raw."""
    out = []
    for cd in result.candidates:
        xs = [p[0] for p in cd.polygon]
        ys = [p[1] for p in cd.polygon]
        out.append(
            {
                "xyxy": [round(min(xs), 1), round(min(ys), 1),
                         round(max(xs), 1), round(max(ys), 1)],
                "conf": round(float(cd.confidence), 4),
            }
        )
    return out


def full_precision_preds(result) -> list[tuple[list[float], float]]:
    return [
        (
            [min(p[0] for p in cd.polygon), min(p[1] for p in cd.polygon),
             max(p[0] for p in cd.polygon), max(p[1] for p in cd.polygon)],
            float(cd.confidence),
        )
        for cd in result.candidates
    ]


def main() -> int:
    import numpy  # noqa: F401  (DetectionRequest 装载依赖前置自检)
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None  # KO 超长 webtoon ~69MP（T3/tile_calib 先例）

    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    print(f"[parity] start {now_iso()}", flush=True)

    # 权重先验断言（加载前；tile_calib/eval_gate_t3 纪律）
    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha == PROD_PIN_SHA, f"v2b sha {v2b_sha[:12]} != 生产 pin"
    chiqui7_sha = sha256_file(CHIQUI7_ONNX)
    assert chiqui7_sha == CHIQUI7_PIN_SHA, (
        f"chiqui7 sha {chiqui7_sha[:12]} != 回滚 pin"
    )
    print(f"[parity] v2b sha {v2b_sha[:12]}（生产 pin 原样）", flush=True)
    print(f"[parity] chiqui7 sha {chiqui7_sha[:12]}（进程内重指窗口）", flush=True)

    ko_pages = load_ko_pages()
    exam_pages = load_exam_pages()
    print(
        f"[parity] 数据装载：KO {len(ko_pages)} 页 56 档派生 GT + 135 框 npd GT"
        f"｜考卷 {len(exam_pages)} 页", flush=True
    )

    RAW_OUT.mkdir(parents=True, exist_ok=True)
    pin_backup = dsfx.SFX_WEIGHTS_SHA256
    summary: dict = {
        "task": "M2-SFX-T5-TILE-KO AC3 production tile-branch parity",
        "generated_at_utc": now_iso(),
        "generated_from": "experiments/M2-SFX-T5-TILE-KO/verify_tile_parity.py",
        "weights": {
            "v2b": {"onnx": str(V2B_ONNX), "sha256": v2b_sha, "pin": "as-is"},
            "chiqui7": {"onnx": str(CHIQUI7_ONNX), "sha256": chiqui7_sha,
                        "pin": "in-process re-point (assert-then-run, finally restore)"},
        },
        "caliber": ("生产 SfxDetectionProvider.detect tile 分支 conf 0.5"
                    "（CPUExecutionProvider）vs T3 raw eval JSON 逐位（xyxy 0.1/"
                    "conf 4 位=T3 写盘精度）+ match_gt 复算全精度"),
        "expected": EXPECTED,
        "sides": {},
        "wording_discipline": "directional 证据，统计功效低；禁用「显著」；0 也如实",
    }
    try:
        for side, onnx in (("v2b", V2B_ONNX), ("chiqui7", CHIQUI7_ONNX)):
            if side == "chiqui7":
                dsfx.SFX_WEIGHTS_SHA256 = chiqui7_sha  # 重指窗口（tile_calib 先例）
            try:
                provider = SfxDetectionProvider(weights_path=onnx, conf_threshold=0.5)
                doc = {"side": side, "ko": [], "per_ds": {}}
                for ds_name, gt_key, expect in (
                    ("ko-tile", "gts", EXPECTED[side]["ko-tile"]),
                    ("ko-npd", "gts_npd", EXPECTED[side]["ko-npd"]),
                ):
                    t_ds = time.perf_counter()
                    per_page = []
                    total_gt = total_matched = 0
                    for p in ko_pages:
                        t0 = time.perf_counter()
                        result = provider.detect(p["request"])
                        elapsed = round(time.perf_counter() - t0, 1)
                        options = dict(result.options)
                        assert options["sfx_route"] == "tile", (
                            f"{p['sample_id']}: 未路由 tile（{options['sfx_route']}）"
                        )
                        preds = full_precision_preds(result)
                        m = match_gt(p[gt_key], preds)
                        total_gt += m["n_gt"]
                        total_matched += m["matched"]
                        written = production_preds(result)
                        t3 = t3_preds(side, ds_name, p["sample_id"])
                        bit_equal = written == t3
                        per_page.append(
                            {
                                "sample_id": p["sample_id"],
                                "page_size": [p["w"], p["h"]],
                                "matched": m["matched"],
                                "n_gt": m["n_gt"],
                                "n_pred": m["n_pred"],
                                "t3_matched": t3_preds_total(side, ds_name, p["sample_id"], "matched"),
                                "t3_n_pred": t3_preds_total(side, ds_name, p["sample_id"], "n_pred"),
                                "bit_parity_vs_t3_raw": bit_equal,
                                "elapsed_s": elapsed,
                                "elapsed_ms_provider": result.elapsed_ms,
                                "pairs": m["pairs"],
                            }
                        )
                        print(
                            f"[parity] {side}/{ds_name} {p['sample_id']}: "
                            f"{m['matched']}/{m['n_gt']} bit_parity={bit_equal} "
                            f"({elapsed}s)", flush=True
                        )
                    ok = total_matched == expect and total_gt == (
                        EXPECT_KO_DERIVED_BOXES if ds_name == "ko-tile" else EXPECT_NPD_BOXES
                    )
                    cell = {
                        "matched": f"{total_matched}/{total_gt}",
                        "expected": f"{expect}/{total_gt}",
                        "bit_reproduction": ok,
                        "elapsed_s": round(time.perf_counter() - t_ds, 1),
                    }
                    doc["per_ds"][ds_name] = cell
                    doc["ko"].append({"ds": ds_name, "per_page": per_page})
                    print(
                        f"[parity] {side}/{ds_name}: {cell['matched']} "
                        f"(expected {cell['expected']}) bit={ok}", flush=True
                    )
                    assert ok, f"{side}/{ds_name}: {cell['matched']} != {cell['expected']}"
                summary["sides"][side] = {
                    "ko-tile": doc["per_ds"]["ko-tile"],
                    "ko-npd": doc["per_ds"]["ko-npd"],
                }
                (RAW_OUT / f"parity-{side}.json").write_text(
                    json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8"
                )
            finally:
                dsfx.SFX_WEIGHTS_SHA256 = pin_backup

        # ---- BJ 考卷 letterbox 零变化实证（chiqui7 pin，重指窗口）----
        dsfx.SFX_WEIGHTS_SHA256 = chiqui7_sha
        try:
            provider = SfxDetectionProvider(
                weights_path=CHIQUI7_ONNX, conf_threshold=0.5
            )
            bj = []
            for p in exam_pages:
                t0 = time.perf_counter()
                result = provider.detect(p["request"])
                elapsed = round(time.perf_counter() - t0, 1)
                options = dict(result.options)
                assert options["sfx_route"] == "letterbox", (
                    f"{p['sample_id']}: 考卷页误路由 tile"
                )
                written = production_preds(result)
                t3 = t3_preds("chiqui7", "bj-exam", p["sample_id"])
                bit_equal = written == t3
                bj.append(
                    {
                        "sample_id": p["sample_id"],
                        "page_size": [p["w"], p["h"]],
                        "sfx_route": options["sfx_route"],
                        "n_pred": len(written),
                        "bit_parity_vs_t3_raw": bit_equal,
                        "elapsed_s": elapsed,
                    }
                )
                print(
                    f"[parity] chiqui7/bj-exam {p['sample_id']}: n_pred="
                    f"{len(written)} bit_parity={bit_equal} ({elapsed}s)", flush=True
                )
            assert all(b["bit_parity_vs_t3_raw"] for b in bj), "BJ letterbox 零变化破"
            summary["bj_exam_letterbox_zero_change"] = {
                "pages": bj,
                "verdict": "PASS: 考卷页 letterbox 路径 preds 与 T3 raw 逐位一致",
            }
        finally:
            dsfx.SFX_WEIGHTS_SHA256 = pin_backup

        (RAW_OUT / "parity-summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"[parity] wrote {RAW_OUT / 'parity-summary.json'}", flush=True)
        print("[parity] ALL PARITY CHECKS PASSED", flush=True)
        return 0
    except AssertionError as error:
        summary["failure"] = str(error)
        (RAW_OUT / "parity-summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"[parity] FAILED: {error}", flush=True)
        return 1


def t3_preds_total(side: str, ds: str, sample_id: str, key: str) -> int:
    doc = _read(T3_RAW / f"eval-{side}-{ds}.json")
    for entry in doc["per_sample"]:
        if entry["sample_id"] == sample_id:
            return int(entry["sides"]["0.5"][key])
    raise AssertionError(f"T3 raw {side}/{ds} 无 {sample_id}")


if __name__ == "__main__":
    raise SystemExit(main())
