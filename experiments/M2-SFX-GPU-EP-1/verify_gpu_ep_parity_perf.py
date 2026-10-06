"""M2-SFX-GPU-EP-1 AC2+AC3: GPU(DML) vs CPU numeric parity + production-path
performance, over the production code itself.

AC2 (the numeric hard gate): the CURRENT v2b production weights (pin
944e8114) detected through the PRODUCTION SfxDetectionProvider.detect —
once with NEWMANGA_SFX_EP=cpu (the baseline face) and once with
NEWMANGA_SFX_EP=dml (the new deployment default) — compared per page:

- KO 4 long-strip exam pages (pre-k01/02/08/09; the tile route),
- BJ exam 2 pages (pre-bj17/18; the ordinary letterbox route),

full-precision conf/xyxy. Bit-identical pages are registered as such; pages
with float drift are QUANTIFIED (max |dconf| / max per-coordinate |dxyxy|),
the conf>=0.5 gate is re-evaluated per prediction (a "gate flip" = a
prediction present on one face only — the threshold changed sides), and the
GT matched set (derived GT + npd GT, KO pages) is compared as an index set.
"No numbers, no verdict" — the Task contract.

AC3 (production-path performance): the same run records per-page wall clock
+ provider elapsed_ms for BOTH faces (protocol: one warm-up detect not
counted, then the timed detect). KO GPU is compared against the T5 reported
1.08 s/page; the BJ ordinary pages give the small-page GPU vs CPU
comparison recorded as-is (a GPU gain is NOT assumed on small pages).

Data loading and GT matching reuse verify_tile_parity.py verbatim (the T3
caliber; same worktree, in-repo import). The EP faces go through the
production env gate itself — no session swapping, no bypass: this IS the
AC1 configuration exercised.

Output: verification/M2-SFX-GPU-EP-1/raw/gpu-ep-parity-perf.json (+ this
stdout). Wording discipline: directional evidence, low statistical power;
the word "significant" is banned; numbers are recorded as facts.
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "M2-SFX-T5-TILE-KO"))

RAW_OUT = REPO / "verification" / "M2-SFX-GPU-EP-1" / "raw"

V2B_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
PROD_PIN_SHA = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)

from verify_tile_parity import (  # noqa: E402
    load_exam_pages,
    load_ko_pages,
    match_gt,
    sha256_file,
)

SFX_ENV_EP = "NEWMANGA_SFX_EP"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def full_precision_preds(result) -> list[tuple[list[float], float]]:
    return [
        (
            [min(p[0] for p in cd.polygon), min(p[1] for p in cd.polygon),
             max(p[0] for p in cd.polygon), max(p[1] for p in cd.polygon)],
            float(cd.confidence),
        )
        for cd in result.candidates
    ]


def detect_face(provider, page):
    """Warm-up detect (not counted) then the timed detect; returns
    (preds, wall_s, provider_ms, route)."""
    provider.detect(page["request"])  # warm-up
    t0 = time.perf_counter()
    result = provider.detect(page["request"])
    wall_s = round(time.perf_counter() - t0, 3)
    route = dict(result.options)["sfx_route"]
    return full_precision_preds(result), wall_s, result.elapsed_ms, route


def diff_preds(cpu: list, gpu: list) -> dict:
    """Quantify the drift between two faces' predictions.

    Pairing: sort both sides by (-conf, xyxy) (the production final order)
    and zip — a reorder-free comparison of the two ranked lists. Gate flips
    = predictions that exist on exactly one side (the conf>=0.5 gate or the
    NMS competition changed sides).
    """
    cpu_sorted = sorted(cpu, key=lambda p: (-p[1], p[0]))
    gpu_sorted = sorted(gpu, key=lambda p: (-p[1], p[0]))
    n = min(len(cpu_sorted), len(gpu_sorted))
    max_dconf = 0.0
    max_dxyxy = 0.0
    for i in range(n):
        (c0, c1, c2, c3), cf = cpu_sorted[i]
        (g0, g1, g2, g3), gf = gpu_sorted[i]
        max_dconf = max(max_dconf, abs(cf - gf))
        max_dxyxy = max(max_dxyxy, abs(c0 - g0), abs(c1 - g1),
                        abs(c2 - g2), abs(c3 - g3))
    return {
        "n_pred_cpu": len(cpu_sorted),
        "n_pred_gpu": len(gpu_sorted),
        "bit_identical": cpu_sorted == gpu_sorted,
        "max_abs_dconf": round(max_dconf, 6),
        "max_abs_dxyxy_px": round(max_dxyxy, 4),
        "gate_flips": abs(len(cpu_sorted) - len(gpu_sorted))
        + sum(
            1
            for i in range(n)
            if (cpu_sorted[i][1] >= 0.5) != (gpu_sorted[i][1] >= 0.5)
        ),
    }


def matched_pairs(match: dict) -> set[tuple[int, int]]:
    return {(p["gt_index"], p["pred_index"]) for p in match["pairs"]}


def run_face(provider, pages, label: str, log) -> dict:
    """One EP face over all pages: per-page timed detect (+ preds), then a
    THIRD detect for the GPU run-to-run bit-stability check."""
    rows: dict[str, dict] = {}
    for p in pages:
        preds, wall_s, provider_ms, route = detect_face(provider, p)
        rows[p["sample_id"]] = {
            "preds": preds,
            "wall_s": wall_s,
            "provider_ms": provider_ms,
            "sfx_route": route,
        }
        log(f"[{label}] {p['sample_id']}: n_pred={len(preds)} wall={wall_s}s "
            f"provider_ms={provider_ms} route={route}", flush=True)
    return rows


def main() -> int:
    import numpy  # noqa: F401
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None  # KO 超长 webtoon（T3/tile_calib 先例）

    import onnxruntime
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    print(f"[gpu-ep] start {now_iso()}", flush=True)
    # r1 gate: evidence reruns must be bound to the exact source commit.
    import subprocess

    head = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"[gpu-ep] source HEAD {head}", flush=True)
    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha == PROD_PIN_SHA, f"v2b sha {v2b_sha[:12]} != 生产 pin"
    print(f"[gpu-ep] v2b sha {v2b_sha[:12]}（生产 pin 原样）", flush=True)
    print(f"[gpu-ep] onnxruntime {onnxruntime.__version__} "
          f"providers={onnxruntime.get_available_providers()}", flush=True)

    ko_pages = load_ko_pages()
    exam_pages = load_exam_pages()
    print(
        f"[gpu-ep] 数据装载：KO {len(ko_pages)} 页（56 档派生 GT + 135 框 npd GT）"
        f"｜BJ 考卷 {len(exam_pages)} 页", flush=True
    )

    RAW_OUT.mkdir(parents=True, exist_ok=True)

    def log(*args, **kwargs):
        print(*args, **kwargs)

    # ---- 两个 EP face，都走生产 env 门 + 生产 detect（无旁路）----
    os.environ[SFX_ENV_EP] = "cpu"
    try:
        cpu_provider = SfxDetectionProvider(
            weights_path=V2B_ONNX, conf_threshold=0.5
        )
        cpu_ko = run_face(cpu_provider, ko_pages, "cpu", log)
        cpu_bj = run_face(cpu_provider, exam_pages, "cpu", log)
    finally:
        os.environ[SFX_ENV_EP] = "dml"
    dml_provider = SfxDetectionProvider(
        weights_path=V2B_ONNX, conf_threshold=0.5
    )
    dml_ko = run_face(dml_provider, ko_pages, "dml", log)
    dml_bj = run_face(dml_provider, exam_pages, "dml", log)

    # GPU run-to-run bit stability: a third detect, bitwise vs the timed one.
    gpu_stability = {}
    for p in ko_pages + exam_pages:
        face = dml_ko if p in ko_pages else dml_bj
        again = full_precision_preds(dml_provider.detect(p["request"]))
        gpu_stability[p["sample_id"]] = (
            sorted(again, key=lambda q: (-q[1], q[0]))
            == sorted(face[p["sample_id"]]["preds"], key=lambda q: (-q[1], q[0]))
        )

    # ---- AC2: 逐页数值对比（KO 双 GT 口径 matched set + 量化漂移）----
    ko_rows = []
    for p in ko_pages:
        sid = p["sample_id"]
        c, g = cpu_ko[sid], dml_ko[sid]
        row = {
            "sample_id": sid,
            "page_size": [p["w"], p["h"]],
            "sfx_route": c["sfx_route"],
            **diff_preds(c["preds"], g["preds"]),
            "gpu_run_to_run_bit_stable": gpu_stability[sid],
        }
        for gt_key, name in (("gts", "derived"), ("gts_npd", "npd")):
            m_cpu = match_gt(p[gt_key], c["preds"])
            m_gpu = match_gt(p[gt_key], g["preds"])
            row[f"matched_{name}"] = (
                f'{m_cpu["matched"]}/{m_cpu["n_gt"]} -> '
                f'{m_gpu["matched"]}/{m_gpu["n_gt"]}'
            )
            row[f"matched_set_equal_{name}"] = (
                matched_pairs(m_cpu) == matched_pairs(m_gpu)
            )
        ko_rows.append(row)
        log(f"[ac2] KO {sid}: bit={row['bit_identical']} "
            f"dconf={row['max_abs_dconf']} dxyxy={row['max_abs_dxyxy_px']}px "
            f"gate_flips={row['gate_flips']} "
            f"derived={row['matched_derived']} set_eq={row['matched_set_equal_derived']} "
            f"npd={row['matched_npd']} set_eq={row['matched_set_equal_npd']}",
            flush=True)

    bj_rows = []
    for p in exam_pages:
        sid = p["sample_id"]
        c, g = cpu_bj[sid], dml_bj[sid]
        row = {
            "sample_id": sid,
            "page_size": [p["w"], p["h"]],
            "sfx_route": c["sfx_route"],
            **diff_preds(c["preds"], g["preds"]),
            "gpu_run_to_run_bit_stable": gpu_stability[sid],
        }
        bj_rows.append(row)
        log(f"[ac2] BJ {sid}: bit={row['bit_identical']} "
            f"dconf={row['max_abs_dconf']} dxyxy={row['max_abs_dxyxy_px']}px "
            f"gate_flips={row['gate_flips']}", flush=True)

    # ---- AC3: 汇总（对照 T5 呈报 KO GPU 1.08s/页）----
    def face_stats(rows: list[dict], key: str) -> dict:
        vals = [r[key] for r in rows]
        return {
            "pages": len(vals),
            "mean": round(statistics.mean(vals), 3),
            "min": round(min(vals), 3),
            "max": round(max(vals), 3),
        }

    summary = {
        "task": "M2-SFX-GPU-EP-1 AC2 numeric parity + AC3 production-path perf",
        "generated_at_utc": now_iso(),
        "generated_from": (
            "experiments/M2-SFX-GPU-EP-1/verify_gpu_ep_parity_perf.py"
        ),
        "source_head": head,
        "weights": {
            "onnx": str(V2B_ONNX),
            "sha256": v2b_sha,
            "pin": "as-is（生产 pin 944e8114）",
        },
        "runtime": {
            "onnxruntime_version": onnxruntime.__version__,
            "available_providers": onnxruntime.get_available_providers(),
            "faces": "NEWMANGA_SFX_EP=cpu / =dml 经生产 env 门（无 session swap 旁路）",
        },
        "protocol": (
            "每页 warm-up 1 次（不计）+ 计测 1 次（preds=AC2 对比面+AC3 时延）；"
            "GPU 面第 3 次 detect 做 run-to-run 逐位稳定性登记；"
            "KO 页双 GT 口径（derived 56 档 + npd 135 框）matched 集按 (gt,pred) 索引对比较"
        ),
        "t5_reference": "KO GPU DML 1.08s/页（T5 perf_tile_dual.py 独立 venv 呈报）",
        "ko_pages": ko_rows,
        "bj_pages": bj_rows,
    }
    # perf faces（KO 与 BJ，双 EP，wall+provider_ms）
    for label, pages, cpu_face, gpu_face in (
        ("ko", ko_pages, cpu_ko, dml_ko),
        ("bj", exam_pages, cpu_bj, dml_bj),
    ):
        summary[f"perf_{label}"] = {
            "cpu": {
                "wall_s": face_stats(
                    [{"v": cpu_face[p["sample_id"]]["wall_s"]} for p in pages], "v"
                ),
                "provider_ms": face_stats(
                    [{"v": cpu_face[p["sample_id"]]["provider_ms"]} for p in pages], "v"
                ),
            },
            "dml": {
                "wall_s": face_stats(
                    [{"v": gpu_face[p["sample_id"]]["wall_s"]} for p in pages], "v"
                ),
                "provider_ms": face_stats(
                    [{"v": gpu_face[p["sample_id"]]["provider_ms"]} for p in pages], "v"
                ),
            },
        }
    summary["wording_discipline"] = (
        "directional 证据，统计功效低；禁用「显著」；数字如实登记不作质量判定"
    )

    all_bit = all(r["bit_identical"] for r in ko_rows + bj_rows)
    summary["verdict"] = {
        "all_pages_bit_identical": all_bit,
        "ko_all_matched_sets_equal": all(
            r["matched_set_equal_derived"] and r["matched_set_equal_npd"]
            for r in ko_rows
        ),
        "ko_max_abs_dconf": max(r["max_abs_dconf"] for r in ko_rows),
        "ko_max_abs_dxyxy_px": max(r["max_abs_dxyxy_px"] for r in ko_rows),
        "bj_max_abs_dconf": max(r["max_abs_dconf"] for r in bj_rows),
        "bj_max_abs_dxyxy_px": max(r["max_abs_dxyxy_px"] for r in bj_rows),
        "gate_flips_total": sum(
            r["gate_flips"] for r in ko_rows + bj_rows
        ),
        "gpu_run_to_run_all_bit_stable": all(gpu_stability.values()),
    }
    out = RAW_OUT / "gpu-ep-parity-perf.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"[gpu-ep] wrote {out}", flush=True)
    print(f"[gpu-ep] verdict: {json.dumps(summary['verdict'])}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
