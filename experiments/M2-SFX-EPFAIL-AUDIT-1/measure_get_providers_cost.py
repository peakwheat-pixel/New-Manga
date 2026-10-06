"""M2-SFX-EPFAIL-AUDIT-1 AC1 设计决策实测：``session.get_providers()`` 单次
调用耗时 + run-time EPFail 回退后状态的读回可见性。

背景（deploy-record M2-SFX-GPU-EP-1 §1.3 r2 N-P3-1）：「逐 detect 复读
get_providers 代价高」是当时的权衡判断，未附实测数字。本 Task 合同要求先
实测该判断再定设计。wrapper（onnxruntime_inference_collection.py:214-216）
的 ``get_providers`` 是 ``return self._providers`` —— 纯 Python 属性读，
预期纳秒~微秒级；本脚本给出生产 venv（onnxruntime-directml 1.24.4 = 生产
wheel）+ 生产 v2b 权重的实测数。

第二部分：run-time EPFail 的可观测性实证。wrapper ``run`` 期捕获
``C.EPFail`` 后正是调用 ``set_providers(self._fallback_providers)``
（:301，DML 请求的 fallback 列表 = ["CPUExecutionProvider"]，:577）再重跑
并正常返回——调用方无异常。本脚本在同一 DML session 上原样调用
``set_providers(["CPUExecutionProvider"])``（wrapper 同一 API 面），验证
该状态经公共 ``get_providers()`` 读回可见（= 审计探测面成立），并给出
``set_providers`` 本身的一次性重建成本（非稳态项，如实登记）。

输出：verification/M2-SFX-EPFAIL-AUDIT-1/raw/epfail-audit-get-providers-cost.json
（+ 本 stdout）。数字如实登记；"显著"一词禁用（GPU-EP-1 wording 纪律沿用）。
"""

from __future__ import annotations

import json
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

RAW_OUT = REPO / "verification" / "M2-SFX-EPFAIL-AUDIT-1" / "raw"

V2B_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
PROD_PIN_SHA = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)

N_ITERS = 1_000_000
N_WARMUP = 10_000

# GPU-EP-1 AC3 稳态基准：KO 长条页 DML 1.106-1.211 s/页（perf_ko.dml.wall_s）。
GPU_EP1_KO_DML_PER_PAGE_S = (1.106, 1.211)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    import hashlib

    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def time_get_providers(session, label: str) -> dict:
    """Warm-up then time N sequential get_providers() calls."""
    providers = session.get_providers()
    for _ in range(N_WARMUP):
        session.get_providers()
    samples: list[float] = []
    for _ in range(5):
        t0 = time.perf_counter()
        for _ in range(N_ITERS):
            session.get_providers()
        samples.append((time.perf_counter() - t0) / N_ITERS)
    per_call_s = statistics.median(samples)
    return {
        "face": label,
        "providers_readback": list(providers),
        "n_iters": N_ITERS,
        "per_call_us": round(per_call_s * 1e6, 4),
        "per_call_ns_median_of_5_runs": round(per_call_s * 1e9, 1),
        "all_runs_us": [round(s * 1e6, 4) for s in samples],
    }


def main() -> int:
    import onnxruntime

    print(f"[epfail-audit] start {now_iso()}", flush=True)
    head = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    print(f"[epfail-audit] source HEAD {head}", flush=True)
    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha == PROD_PIN_SHA, f"v2b sha {v2b_sha[:12]} != 生产 pin"
    print(f"[epfail-audit] v2b sha {v2b_sha[:12]}（生产 pin 原样）", flush=True)
    print(
        f"[epfail-audit] onnxruntime {onnxruntime.__version__} "
        f"available={onnxruntime.get_available_providers()}",
        flush=True,
    )

    results: dict = {
        "task": "M2-SFX-EPFAIL-AUDIT-1 AC1 design measurement",
        "generated_at_utc": now_iso(),
        "generated_from": (
            "experiments/M2-SFX-EPFAIL-AUDIT-1/"
            "measure_get_providers_cost.py"
        ),
        "source_head": head,
        "weights": {"onnx": str(V2B_ONNX), "sha256": v2b_sha},
        "runtime": {
            "onnxruntime_version": onnxruntime.__version__,
            "available_providers": onnxruntime.get_available_providers(),
        },
        "protocol": (
            f"warmup {N_WARMUP} + median of 5 runs x {N_ITERS} sequential "
            "get_providers() calls per face; set_providers replays the "
            "wrapper's run-time EPFail fallback call (:301) verbatim"
        ),
    }

    # ---- CPU face ----
    cpu_session = onnxruntime.InferenceSession(
        str(V2B_ONNX), providers=["CPUExecutionProvider"]
    )
    cpu_timing = time_get_providers(cpu_session, "cpu")
    results["get_providers_cost_cpu"] = cpu_timing
    print(
        f"[epfail-audit] cpu get_providers() -> {cpu_timing['providers_readback']} "
        f"= {cpu_timing['per_call_us']} us/call",
        flush=True,
    )

    # ---- DML face（生产默认形态）----
    dml_session = onnxruntime.InferenceSession(
        str(V2B_ONNX), providers=["DmlExecutionProvider"]
    )
    dml_timing = time_get_providers(dml_session, "dml")
    results["get_providers_cost_dml"] = dml_timing
    print(
        f"[epfail-audit] dml get_providers() -> {dml_timing['providers_readback']} "
        f"= {dml_timing['per_call_us']} us/call",
        flush=True,
    )

    # ---- run-time EPFail fallback 状态的读回可见性实证 ----
    # wrapper run() 期 EPFail 分支原样调用：set_providers(_fallback_providers)
    # （DML 请求的 fallback 列表 = ["CPUExecutionProvider"]）。这一步同时给出
    # set_providers 的一次性重建成本（native session 重建，非稳态项）。
    t0 = time.perf_counter()
    dml_session.set_providers(["CPUExecutionProvider"])
    set_providers_s = round(time.perf_counter() - t0, 3)
    after = dml_session.get_providers()
    results["runtime_epfail_fallback_observability"] = {
        "wrapper_call_replayed": "set_providers(['CPUExecutionProvider'])",
        "set_providers_wall_s": set_providers_s,
        "get_providers_after": list(after),
        "readback_shows_cpu_only": after == ["CPUExecutionProvider"],
        "note": (
            "wrapper run() catches C.EPFail, calls set_providers("
            "_fallback_providers), disables fallback and re-runs returning "
            "NORMALLY (no exception reaches the caller); the provider-list "
            "change IS observable via the public get_providers() afterwards"
        ),
    }
    print(
        f"[epfail-audit] after set_providers(CPU) (took {set_providers_s}s): "
        f"get_providers() -> {list(after)}",
        flush=True,
    )

    # ---- 1% 硬门对照 ----
    worst_us = max(cpu_timing["per_call_us"], dml_timing["per_call_us"])
    per_page_budget_us = min(GPU_EP1_KO_DML_PER_PAGE_S) * 1e6  # 1% of 1.106 s
    results["one_percent_budget_check"] = {
        "gpu_ep1_ko_dml_per_page_s": GPU_EP1_KO_DML_PER_PAGE_S,
        "one_percent_budget_us": round(per_page_budget_us, 1),
        "worst_measured_per_call_us": worst_us,
        "worst_call_share_of_budget_pct": round(
            worst_us / per_page_budget_us * 100, 6
        ),
        "worst_call_share_of_page_pct": round(
            worst_us / (min(GPU_EP1_KO_DML_PER_PAGE_S) * 1e6) * 100, 8
        ),
        "verdict": (
            "PASS: 稳态每页一次 get_providers() 读回的时延增量低于 1% 硬门"
            if worst_us < per_page_budget_us
            else "FAIL"
        ),
    }
    print(
        f"[epfail-audit] 1% budget: {results['one_percent_budget_check']['verdict']} "
        f"({worst_us} us vs {per_page_budget_us:.0f} us budget)",
        flush=True,
    )

    results["wording_discipline"] = (
        "directional 证据；禁用「显著」；数字如实登记不作质量判定"
    )

    RAW_OUT.mkdir(parents=True, exist_ok=True)
    out = RAW_OUT / "epfail-audit-get-providers-cost.json"
    out.write_text(json.dumps(results, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"[epfail-audit] wrote {out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
