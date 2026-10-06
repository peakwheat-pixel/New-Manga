"""M2-SFX-GPU-EP-1 r1 P1-1 decisive verification: the WRAPPER-LEVEL CPU
fallback audited end-to-end on a REAL CPU-only onnxruntime wheel.

DSH r1 P1-1: onnxruntime's own ``InferenceSession.__init__`` swallows a DML
init failure (``enable_fallback`` defaults True) and returns a CPU session
WITHOUT raising — so an exception-driven fallback branch never runs and the
audit must come from a ``get_providers()`` read-back. This script is the
real-runtime counterpart of the stub test
``test_engine_wrapper_level_cpu_fallback_gets_three_key_audit``:

- the environment is a DEDICATED venv with the CPU-only ``onnxruntime``
  wheel (the production venv's pre-swap state) — no DML provider exists in
  the process at all;
- the production provider runs UNMODIFIED through ``NEWMANGA_SFX_EP``'s
  default (dml) against the pinned v2b weights on a synthetic small page;
- PASS gate: options carry sfx_ep=dml (requested), device=cpu (EFFECTIVE,
  read back via get_providers()), sfx_ep_fallback naming the wrapper-level
  fallback — never a silent or wrong-value audit.

Run (from the repo root, with this script's own venv python):
    <cpu-verify venv>/Scripts/python.exe experiments/M2-SFX-GPU-EP-1/
    verify_wrapper_fallback_cpu_wheel.py

Wording discipline: this verifies the AUDIT SEMANTICS only; detection
quality numbers are out of scope here (AC2 owns them).
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

V2B_ONNX = Path(
    r"G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
PROD_PIN_SHA = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    import numpy
    from PIL import Image

    import onnxruntime

    print(f"[wrapper-fallback] start {now_iso()}", flush=True)
    print(
        f"[wrapper-fallback] onnxruntime {onnxruntime.__version__} "
        f"({Path(onnxruntime.__file__).parent.parent.name})",
        flush=True,
    )
    available = onnxruntime.get_available_providers()
    print(f"[wrapper-fallback] available_providers={available}", flush=True)
    assert "DmlExecutionProvider" not in available, (
        "本验证必须跑在 CPU-only wheel 环境（无 DML provider）——"
        f"实际 available={available}"
    )

    v2b_sha = sha256_file(V2B_ONNX)
    assert v2b_sha == PROD_PIN_SHA, f"v2b sha {v2b_sha[:12]} != 生产 pin"
    print(f"[wrapper-fallback] v2b sha {v2b_sha[:12]}（生产 pin 原样）", flush=True)

    from infrastructure.providers.detection_sfx import SfxDetectionProvider
    from ports.detection.ports import DetectionRequest

    provider = SfxDetectionProvider(
        weights_path=V2B_ONNX, conf_threshold=0.5
    )
    w, h = 300, 400
    frame = numpy.asarray(
        Image.new("RGB", (w, h), (240, 240, 240)), dtype=numpy.uint8
    ).tobytes()
    result = provider.detect(
        DetectionRequest(page_id="wrapper-fallback-probe",
                         image_bytes=frame, width=w, height=h)
    )
    options = dict(result.options)
    print(
        f"[wrapper-fallback] detect OK route={options['sfx_route']} "
        f"n_candidates={len(result.candidates)}",
        flush=True,
    )
    print(
        "[wrapper-fallback] 三键审计: "
        f"sfx_ep={options.get('sfx_ep')!r} device={options.get('device')!r} "
        f"sfx_ep_fallback={options.get('sfx_ep_fallback')!r}",
        flush=True,
    )
    checks = {
        "sfx_ep_requested_dml": options.get("sfx_ep") == "dml",
        "device_effective_cpu": options.get("device") == "cpu",
        "sfx_ep_fallback_present": "sfx_ep_fallback" in options,
        "fallback_names_wrapper_or_cpu": (
            "wrapper-level" in (options.get("sfx_ep_fallback") or "")
            or "CPUExecutionProvider" in (options.get("sfx_ep_fallback") or "")
        ),
    }
    verdict = "PASS" if all(checks.values()) else "FAIL"
    summary = {
        "task": "M2-SFX-GPU-EP-1 r1 P1-1 decisive verification",
        "generated_at_utc": now_iso(),
        "generated_from": (
            "experiments/M2-SFX-GPU-EP-1/verify_wrapper_fallback_cpu_wheel.py"
        ),
        "environment": {
            "onnxruntime_version": onnxruntime.__version__,
            "available_providers": available,
            "note": "CPU-only wheel（生产 venv 换装前状态）；DML 不存在于进程",
        },
        "weights_sha256": v2b_sha,
        "options": {
            "sfx_ep": options.get("sfx_ep"),
            "device": options.get("device"),
            "sfx_ep_fallback": options.get("sfx_ep_fallback"),
        },
        "checks": checks,
        "verdict": verdict,
    }
    out = REPO / "verification" / "M2-SFX-GPU-EP-1" / "raw" / (
        "wrapper-fallback-cpu-wheel.json"
    )
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    print(f"[wrapper-fallback] wrote {out}", flush=True)
    print(f"[wrapper-fallback] VERDICT: {verdict} {json.dumps(checks)}",
          flush=True)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
