"""M2-SFX-TILE-WIDTH-CALIB-1 AC2: directional per-width tile vs letterbox eval.

For EVERY registered width bin (INPUTS.md §2) run the PRODUCTION
SfxDetectionProvider.detect (src/infrastructure/providers/detection_sfx.py,
imported from THIS worktree) twice:

- tile caliber   : default env (NEWMANGA_SFX_TILE absent -> frozen default on)
- letterbox      : NEWMANGA_SFX_TILE=off (pre-T5 behavior restored byte-for-byte)

plus a conf-0.2 reference face (KO-TILE-CALIB dual-caliber precedent) — the
production main caliber stays conf 0.5. Out-of-domain bins (width > 690) have
no tile face: at conf 0.5 they run the default env only and assert
sfx_route == "letterbox" (predicate routing); at conf 0.2 they run
NEWMANGA_SFX_TILE=off (path-identical letterbox for them — recorded as such).

Anchors: the native W690/W600 pages at conf 0.5 tile must reproduce the T5
parity raw numbers per page (parity-v2b.json, ko-tile derived GT) — a
self-check that the harness measures the production sequence faithfully.

Matching caliber: eval_gate_t3.py match_gt verbatim (greedy conf-descending,
IoU >= 0.5, each GT at most one pred). Weights: v2b production pin AS-IS,
sha asserted BEFORE load; no weight re-point in this Task.

Output: verification/M2-SFX-TILE-WIDTH-CALIB-1/raw/width-eval.json (per
page, per caliber: n_pred / matched / recall / precision / wall seconds /
provider ms / tile count) — directional evidence, low statistical power;
zeros are recorded as zeros; the word "significant" is banned.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RAW_OUT = REPO / "verification" / "M2-SFX-TILE-WIDTH-CALIB-1" / "raw"

#: Production weights (v2b pin, AS-IS — no re-point in this Task).
V2B_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
PROD_PIN_SHA = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)

#: Prepared pages manifest (gitignored external tree; prepare_pages.py output).
PAGES_MANIFEST = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-TILE-WIDTH-CALIB-1/pages-manifest.json"
)

#: T5 parity raw (committed evidence) — the native-bin anchor numbers.
T5_PARITY = REPO / "verification" / "M2-SFX-T5-TILE-KO" / "raw" / "parity-v2b.json"

#: Width bins in measurement order (anchors first). Domain flag: in_tile
#: (width <= 690) runs tile AND letterbox; out_of_domain (width > 690) runs
#: the default env only (letterbox route under the frozen predicate).
BIN_ORDER = [
    "W690", "W600",                       # native anchors
    "W640", "W480", "W320",               # resampled in-domain
    "SYNTH-384", "SYNTH-560", "SYNTH-680",  # synthesized in-domain
    "W800", "W1024",                      # out-of-domain (letterbox route)
]


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
    }


# --------------------------------------------------------------------------
# Page loading (sha-asserted) and width-bin assignment
# --------------------------------------------------------------------------


def width_bin_for(page: dict) -> str:
    w = page["width"]
    if page["page_id"].startswith("synth-"):
        return f"SYNTH-{w}"
    return f"W{w}"


def domain_for(page: dict) -> str:
    return "out_of_domain" if page["width"] > 690 else "in_tile"


def load_pages() -> list[dict]:
    import numpy
    from PIL import Image
    from ports.detection.ports import DetectionRequest

    Image.MAX_IMAGE_PIXELS = None
    doc = _read(PAGES_MANIFEST)
    pages = []
    for entry in doc["pages"]:
        p = Path(entry["path"])
        assert p.is_file(), f"{entry['page_id']}: 页面缺失 {p}"
        assert sha256_file(p) == entry["sha256"], (
            f"{entry['page_id']}: 页图 sha256 与 prepared manifest 不一致"
        )
        rgb = Image.open(p).convert("RGB")
        w, h = rgb.size
        assert (w, h) == (entry["width"], entry["height"]), (
            f"{entry['page_id']}: 尺寸 {w}x{h} != manifest"
        )
        pages.append(
            {
                "page_id": entry["page_id"],
                "gt_type": entry["gt_type"],
                "source": entry["source"],
                "provenance": entry["provenance"],
                "width": w,
                "height": h,
                "gts": [list(map(float, b)) for b in entry["boxes"]],
                "request": DetectionRequest(
                    page_id=entry["page_id"],
                    image_bytes=numpy.asarray(rgb, dtype=numpy.uint8).tobytes(),
                    width=w,
                    height=h,
                ),
            }
        )
        rgb.close()
    ids = [p["page_id"] for p in pages]
    assert len(ids) == len(set(ids)), "prepared manifest 页 id 重复"
    print(f"[eval] 页装载 {len(pages)} 页: {', '.join(ids)}", flush=True)
    return pages


def t5_anchor_numbers() -> dict[str, tuple[int, int]]:
    """T5 parity per-page matched/n_gt on the derived GT (ko-tile face)."""
    doc = _read(T5_PARITY)
    per_page = doc["ko"][0]["per_page"]
    return {
        e["sample_id"]: (e["matched"], e["n_gt"]) for e in per_page
    }


def full_precision_preds(result) -> list[tuple[list[float], float]]:
    return [
        (
            [min(p[0] for p in cd.polygon), min(p[1] for p in cd.polygon),
             max(p[0] for p in cd.polygon), max(p[1] for p in cd.polygon)],
            float(cd.confidence),
        )
        for cd in result.candidates
    ]


def run_face(provider, page: dict, expect_route: str | None) -> dict:
    t0 = time.perf_counter()
    result = provider.detect(page["request"])
    elapsed = round(time.perf_counter() - t0, 3)
    options = dict(result.options)
    route = options["sfx_route"]
    if expect_route is not None:
        assert route == expect_route, (
            f"{page['page_id']}: sfx_route={route} != 期望 {expect_route}"
        )
    preds = full_precision_preds(result)
    m = match_gt(page["gts"], preds)
    return {
        "sfx_route": route,
        "tile_count": int(options.get("tile_count", "0")),
        "tile_h": options.get("tile_h"),
        "n_pred": m["n_pred"],
        "n_gt": m["n_gt"],
        "matched": m["matched"],
        "recall": m["recall"],
        "precision": m["precision"],
        "elapsed_s": elapsed,
        "elapsed_ms_provider": result.elapsed_ms,
        "ms_per_tile": (
            round(result.elapsed_ms / int(options["tile_count"]), 1)
            if options.get("tile_count") and int(options["tile_count"]) > 0
            else None
        ),
        "pairs": m["pairs"],
    }


def main() -> int:
    import numpy  # noqa: F401  (DetectionRequest 装载依赖前置自检)
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    print(f"[eval] start {now_iso()}", flush=True)

    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha == PROD_PIN_SHA, (
        f"v2b sha {v2b_sha[:12]} != 生产 pin（拒绝在未验证权重上运行）"
    )
    print(f"[eval] v2b sha {v2b_sha[:12]}（生产 pin 原样，零重指）", flush=True)

    pages = load_pages()
    anchors = t5_anchor_numbers()
    print(f"[eval] T5 锚点数字: {anchors}", flush=True)

    RAW_OUT.mkdir(parents=True, exist_ok=True)

    providers = {
        0.5: SfxDetectionProvider(weights_path=V2B_ONNX, conf_threshold=0.5),
        0.2: SfxDetectionProvider(weights_path=V2B_ONNX, conf_threshold=0.2),
    }

    summary: dict = {
        "task": "M2-SFX-TILE-WIDTH-CALIB-1 AC2 per-width tile vs letterbox",
        "generated_at_utc": now_iso(),
        "generated_from": "experiments/M2-SFX-TILE-WIDTH-CALIB-1/eval_tile_width.py",
        "weights": {"v2b": {"onnx": str(V2B_ONNX), "sha256": v2b_sha, "pin": "as-is"}},
        "caliber": (
            "生产 SfxDetectionProvider.detect（DmlExecutionProvider）；主口径 conf 0.5"
            " + 参考 conf 0.2；tile=默认 env（NEWMANGA_SFX_TILE 缺省=on），"
            "letterbox=NEWMANGA_SFX_TILE=off；匹配=eval_gate_t3.py match_gt 逐字"
            "（IoU>=0.5 conf 降序贪心）；页图=prepare_pages.py 外部树 sha 断言"
        ),
        "t5_anchors": {k: list(v) for k, v in anchors.items()},
        "width_bins": {},
        "wording_discipline": (
            "directional 证据，统计功效低；禁用「显著」；0 也如实登记"
        ),
    }

    env_backup = os.environ.get("NEWMANGA_SFX_TILE")
    anchor_checked = False
    try:
        # warm-up 协议（deploy-report §1：warm-up 1 次不计 + 计测）——每 provider
        # 首跑前用最小 tile 页（pre-k02@600，21 tiles）跑 1 次，不计入统计。
        warm = next(p for p in pages if p["page_id"] == "pre-k02@600")
        for conf, provider in providers.items():
            os.environ.pop("NEWMANGA_SFX_TILE", None)
            provider.detect(warm["request"])
            os.environ["NEWMANGA_SFX_TILE"] = "off"
            provider.detect(warm["request"])
            print(f"[eval] warm-up done conf={conf}", flush=True)

        for bin_name in BIN_ORDER:
            bin_pages = [p for p in pages if width_bin_for(p) == bin_name]
            assert bin_pages, f"宽度档 {bin_name} 无页"
            per_page = []
            agg = {
                "tile_conf0.5": {"n_gt": 0, "matched": 0, "n_pred": 0, "elapsed_s": 0.0},
                "letterbox_conf0.5": {"n_gt": 0, "matched": 0, "n_pred": 0, "elapsed_s": 0.0},
                "tile_conf0.2": {"n_gt": 0, "matched": 0, "n_pred": 0, "elapsed_s": 0.0},
                "letterbox_conf0.2": {"n_gt": 0, "matched": 0, "n_pred": 0, "elapsed_s": 0.0},
            }
            for page in bin_pages:
                domain = domain_for(page)
                runs = {}
                for conf, provider in providers.items():
                    # tile 面（默认 env）
                    if domain == "in_tile":
                        os.environ.pop("NEWMANGA_SFX_TILE", None)
                        runs[f"tile_conf{conf}"] = run_face(provider, page, "tile")
                    # letterbox 面（env off；域外档默认 env 即 letterbox）
                    if domain == "out_of_domain" and conf == 0.5:
                        os.environ.pop("NEWMANGA_SFX_TILE", None)
                        runs[f"letterbox_conf{conf}"] = run_face(
                            provider, page, "letterbox"
                        )
                        runs[f"letterbox_conf{conf}"]["note"] = (
                            "out-of-domain default env routes letterbox; "
                            "NEWMANGA_SFX_TILE=off is path-identical here"
                        )
                    else:
                        os.environ["NEWMANGA_SFX_TILE"] = "off"
                        runs[f"letterbox_conf{conf}"] = run_face(
                            provider, page, "letterbox"
                        )
                # 原生锚点自检（tile conf 0.5 与 T5 parity raw 逐页一致；
                # 仅 native 页页 id（pre-kXX@690/@600）参与——重采样页 source
                # 同名但图已变，matched 数字不同是本 Task 的测量对象）
                if page["page_id"] in ("pre-k08@690", "pre-k09@690", "pre-k02@600") and domain == "in_tile":
                    exp_m, exp_gt = anchors[page["source"]]
                    got = runs["tile_conf0.5"]
                    assert got["matched"] == exp_m and got["n_gt"] == exp_gt, (
                        f"{page['page_id']}: 锚点失配 {got['matched']}/{got['n_gt']}"
                        f" != T5 {exp_m}/{exp_gt}"
                    )
                    runs["tile_conf0.5"]["t5_anchor"] = f"{exp_m}/{exp_gt} MATCH"
                    anchor_checked = True
                per_page.append(
                    {
                        "page_id": page["page_id"],
                        "source": page["source"],
                        "gt_type": page["gt_type"],
                        "provenance": page["provenance"],
                        "page_size": [page["width"], page["height"]],
                        "domain": domain,
                        "n_gt": len(page["gts"]),
                        "runs": runs,
                    }
                )
                for face, r in runs.items():
                    if face in agg:
                        agg[face]["n_gt"] += r["n_gt"]
                        agg[face]["matched"] += r["matched"]
                        agg[face]["n_pred"] += r["n_pred"]
                        agg[face]["elapsed_s"] += r["elapsed_s"]
                def _fmt(face: str) -> str:
                    r = runs.get(face)
                    return (
                        f"{r['matched']}/{r['n_gt']} (n_pred {r['n_pred']})"
                        if r else "n/a (out-of-domain: no tile face)"
                    )

                print(
                    f"[eval] {bin_name} {page['page_id']}: "
                    f"tile@0.5 {_fmt('tile_conf0.5')} | "
                    f"lb@0.5 {_fmt('letterbox_conf0.5')} | "
                    f"tile@0.2 {_fmt('tile_conf0.2')} | "
                    f"lb@0.2 {_fmt('letterbox_conf0.2')}",
                    flush=True,
                )
            for face, a in agg.items():
                a["recall"] = round(a["matched"] / a["n_gt"], 4) if a["n_gt"] else None
            summary["width_bins"][bin_name] = {
                "pages": bin_pages and [p["page_id"] for p in bin_pages],
                "gt_types": sorted({p["gt_type"] for p in bin_pages}),
                "aggregate": agg,
                "per_page": per_page,
            }

        assert anchor_checked, "原生锚点自检未执行（评测集缺原生档？）"

        (RAW_OUT / "width-eval.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"[eval] wrote {RAW_OUT / 'width-eval.json'}", flush=True)

        # 控制台汇总表（directional）
        print("\n[eval] === 逐宽汇总（conf 0.5 主口径）===", flush=True)
        for bin_name, doc in summary["width_bins"].items():
            a05 = doc["aggregate"]["tile_conf0.5"]
            l05 = doc["aggregate"]["letterbox_conf0.5"]
            print(
                f"{bin_name:10s} tile {a05['matched']}/{a05['n_gt']} "
                f"(pred {a05['n_pred']}, {a05['elapsed_s']:.1f}s) | "
                f"letterbox {l05['matched']}/{l05['n_gt']} "
                f"(pred {l05['n_pred']}, {l05['elapsed_s']:.1f}s)",
                flush=True,
            )
        print("[eval] DONE", flush=True)
        return 0
    except AssertionError as error:
        summary["failure"] = str(error)
        (RAW_OUT / "width-eval.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(f"[eval] FAILED: {error}", flush=True)
        return 1
    finally:
        # env 恢复对齐合同字面与 T5 先例（DSH r1 P3-10）：成功/失败/异常路径均恢复；
        # 控制流收拢，无数字路径变化，raw 证据不重跑。
        os.environ.pop("NEWMANGA_SFX_TILE", None)
        if env_backup is not None:
            os.environ["NEWMANGA_SFX_TILE"] = env_backup


if __name__ == "__main__":
    raise SystemExit(main())
