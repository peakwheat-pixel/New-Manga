"""M2-SFX-EPFAIL-AUDIT-1 AC3: GPU(DML) vs CPU parity 抽 1 页复核——结论
相对 GPU-EP-1 基准不变，且新审计在真实稳态下零输出变化。

沿用 verify_gpu_ep_parity_perf.py（M2-SFX-GPU-EP-1 AC2+AC3）的形态与比较
核心（diff_preds / match_gt / 双 EP face 走生产 env 门），抽 KO pre-k01
页（tile 路由、GPU-EP-1 基准行 bit_identical=false 但漂移 1e-06/0.0001px、
gate_flips=0、双 GT 口径 matched set equal）复核：

1. 数值面：本 Task HEAD 下 CPU vs DML 的漂移量级与基准行同形态（浮点漂移
   而非门翻转；matched set equal 不变）——GPU-EP-1 结论不被本 Task 改变；
2. 审计面：真实稳态（无 EPFail 发生）下两 face 的 options 均无
   ``sfx_ep_runtime_check`` 键，三键（device/sfx_ep/sfx_ep_fallback）与
   GPU-EP-1 交付语义逐字一致——审计在稳态零输出变化；
3. 时延面：DML face 单页 wall/provider_ms 如实登记（directional，对照
   GPU-EP-1 perf_ko.dml 区间 min 0.333 / mean 1.211 / max 2.325 s）。

输出：verification/M2-SFX-EPFAIL-AUDIT-1/raw/epfail-audit-parity-prek01.json
（+ 本 stdout）。禁用「显著」；数字如实登记。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "experiments" / "M2-SFX-T5-TILE-KO"))

RAW_OUT = REPO / "verification" / "M2-SFX-EPFAIL-AUDIT-1" / "raw"

V2B_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
PROD_PIN_SHA = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)

GPU_EP1_BASELINE_JSON = Path(
    r"G:/CODEX/New Manga/verification/M2-SFX-GPU-EP-1/raw/gpu-ep-parity-perf.json"
)
SAMPLE_ID = "pre-k01"
SFX_ENV_EP = "NEWMANGA_SFX_EP"

from verify_tile_parity import (  # noqa: E402
    load_ko_pages,
    match_gt,
    sha256_file,
)


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


def diff_preds(cpu: list, gpu: list) -> dict:
    """GPU-EP-1 verify_gpu_ep_parity_perf.diff_preds verbatim（ranked zip，
    无重排比较；gate flip = 预测只在单侧存在）。"""
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


def detect_timed(provider, page):
    """Warm-up（不计）+ timed detect；返回 (preds, wall_s, provider_ms,
    options)。"""
    provider.detect(page["request"])  # warm-up
    t0 = time.perf_counter()
    result = provider.detect(page["request"])
    wall_s = round(time.perf_counter() - t0, 3)
    return (
        full_precision_preds(result),
        wall_s,
        result.elapsed_ms,
        dict(result.options),
    )


def main() -> int:
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    import onnxruntime

    print(f"[epfail-parity] start {now_iso()}", flush=True)
    head = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"[epfail-parity] source HEAD {head}", flush=True)
    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha == PROD_PIN_SHA, f"v2b sha {v2b_sha[:12]} != 生产 pin"
    print(f"[epfail-parity] v2b sha {v2b_sha[:12]}（生产 pin 原样）", flush=True)
    print(
        f"[epfail-parity] onnxruntime {onnxruntime.__version__} "
        f"providers={onnxruntime.get_available_providers()}",
        flush=True,
    )

    page = next(p for p in load_ko_pages() if p["sample_id"] == SAMPLE_ID)
    print(
        f"[epfail-parity] 抽页 {SAMPLE_ID}: {page['w']}x{page['h']}"
        f"（tile 路由域，GPU-EP-1 基准行漂移 1e-06/0.0001px/gate_flips=0）",
        flush=True,
    )
    RAW_OUT.mkdir(parents=True, exist_ok=True)

    # ---- CPU face（生产 env 门，无旁路）----
    os.environ[SFX_ENV_EP] = "cpu"
    try:
        cpu_provider = SfxDetectionProvider(
            weights_path=V2B_ONNX, conf_threshold=0.5
        )
        cpu_preds, cpu_wall, cpu_ms, cpu_options = detect_timed(
            cpu_provider, page
        )
    finally:
        os.environ[SFX_ENV_EP] = "dml"
    print(
        f"[epfail-parity] cpu: n_pred={len(cpu_preds)} wall={cpu_wall}s "
        f"provider_ms={cpu_ms}",
        flush=True,
    )

    # ---- DML face（生产默认）----
    dml_provider = SfxDetectionProvider(
        weights_path=V2B_ONNX, conf_threshold=0.5
    )
    dml_preds, dml_wall, dml_ms, dml_options = detect_timed(dml_provider, page)
    print(
        f"[epfail-parity] dml: n_pred={len(dml_preds)} wall={dml_wall}s "
        f"provider_ms={dml_ms}",
        flush=True,
    )

    # ---- 审计面：真实稳态断言（无 EPFail 发生 → 零新键，三键照常）----
    audit_check = {
        "cpu": {
            "device": cpu_options["device"],
            "sfx_ep": cpu_options["sfx_ep"],
            "sfx_ep_fallback_present": "sfx_ep_fallback" in cpu_options,
            "sfx_ep_runtime_check_present": (
                "sfx_ep_runtime_check" in cpu_options
            ),
        },
        "dml": {
            "device": dml_options["device"],
            "sfx_ep": dml_options["sfx_ep"],
            "sfx_ep_fallback_present": "sfx_ep_fallback" in dml_options,
            "sfx_ep_runtime_check_present": (
                "sfx_ep_runtime_check" in dml_options
            ),
        },
    }
    steady = (
        audit_check["cpu"] == {
            "device": "cpu", "sfx_ep": "cpu",
            "sfx_ep_fallback_present": False,
            "sfx_ep_runtime_check_present": False,
        }
        and audit_check["dml"] == {
            "device": "dml", "sfx_ep": "dml",
            "sfx_ep_fallback_present": False,
            "sfx_ep_runtime_check_present": False,
        }
    )
    print(
        f"[epfail-parity] 审计稳态（两 face 零新键、三键照常）: "
        f"{'PASS' if steady else 'FAIL'} — {json.dumps(audit_check)}",
        flush=True,
    )
    assert steady, f"稳态审计面漂移: {audit_check}"

    # ---- 数值面：与 GPU-EP-1 基准行同形态 ----
    row = diff_preds(cpu_preds, dml_preds)
    for gt_key, name in (("gts", "derived"), ("gts_npd", "npd")):
        m_cpu = match_gt(page[gt_key], cpu_preds)
        m_dml = match_gt(page[gt_key], dml_preds)
        row[f"matched_{name}"] = (
            f'{m_cpu["matched"]}/{m_cpu["n_gt"]} -> '
            f'{m_dml["matched"]}/{m_dml["n_gt"]}'
        )
        row[f"matched_set_equal_{name}"] = (
            matched_pairs(m_cpu) == matched_pairs(m_dml)
        )
    print(f"[epfail-parity] parity: {json.dumps(row)}", flush=True)

    baseline_row = None
    if GPU_EP1_BASELINE_JSON.is_file():
        base = json.loads(
            GPU_EP1_BASELINE_JSON.read_text(encoding="utf-8")
        )
        baseline_row = next(
            r for r in base["ko_pages"] if r["sample_id"] == SAMPLE_ID
        )
    same_shape = (
        baseline_row is not None
        and row["n_pred_cpu"] == row["n_pred_gpu"]
        and row["gate_flips"] == 0 == baseline_row["gate_flips"]
        and row["matched_set_equal_derived"]
        and row["matched_set_equal_npd"]
        and baseline_row["matched_set_equal_derived"]
        and baseline_row["matched_set_equal_npd"]
        and row["max_abs_dconf"] <= 1e-05  # 基准 1e-06 同量级（浮点漂移域）
        and row["max_abs_dxyxy_px"] <= 0.001  # 基准 0.0001px 同量级
    )
    print(
        f"[epfail-parity] 结论不变判定: {'PASS' if same_shape else 'FAIL'}"
        f"（基准 gate_flips={baseline_row['gate_flips'] if baseline_row else '?'}"
        f" dconf={baseline_row['max_abs_dconf'] if baseline_row else '?'}"
        f" dxyxy={baseline_row['max_abs_dxyxy_px'] if baseline_row else '?'}）",
        flush=True,
    )

    summary = {
        "task": "M2-SFX-EPFAIL-AUDIT-1 AC3 parity one-page recheck",
        "generated_at_utc": now_iso(),
        "generated_from": (
            "experiments/M2-SFX-EPFAIL-AUDIT-1/verify_epfail_audit_parity.py"
        ),
        "source_head": head,
        "weights": {"onnx": str(V2B_ONNX), "sha256": v2b_sha},
        "runtime": {
            "onnxruntime_version": onnxruntime.__version__,
            "available_providers": onnxruntime.get_available_providers(),
        },
        "sample_id": SAMPLE_ID,
        "page_size": [page["w"], page["h"]],
        "parity_this_task": row,
        "gpu_ep1_baseline_row": baseline_row,
        "audit_steady_state": {"faces": audit_check, "verdict": "PASS" if steady else "FAIL"},
        "perf": {
            "cpu_wall_s": cpu_wall, "cpu_provider_ms": cpu_ms,
            "dml_wall_s": dml_wall, "dml_provider_ms": dml_ms,
            "gpu_ep1_perf_ko_dml_reference": (
                "min 0.333 / mean 1.211 / max 2.325 s（4 页区间，directional）"
            ),
        },
        "verdict": {
            "steady_state_audit_silent": steady,
            "conclusion_unchanged_vs_gpu_ep1": same_shape,
        },
        "wording_discipline": (
            "directional 证据，统计功效低；禁用「显著」；数字如实登记不作质量判定"
        ),
    }
    out = RAW_OUT / "epfail-audit-parity-prek01.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"[epfail-parity] wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
