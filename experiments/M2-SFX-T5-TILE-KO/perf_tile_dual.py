"""M2-SFX-T5-TILE-KO AC2: tile dual-track performance measurement.

Deployment-form timing data over the four KO exam pages (58-112 tiles per
page), the production tile caliber (v2b pin, conf 0.5):

- CPU face: the production engine AS-IS (``_build_engine``,
  CPUExecutionProvider) — the deployment form the lightweight-stack ruling
  froze;
- GPU face: the same ONNX on ``DmlExecutionProvider`` (onnxruntime-directml,
  separate task-env venv; RTX 5070 Ti). The production engine is frozen to
  the CPU EP by the ruling, so the GPU face builds its own session and swaps
  ONLY the session inside the provider engine tuple — the tile sequence
  (``_detect_tiles`` / ``_letterbox`` / ``_sfx_boxes``) is the production
  code verbatim, which is what makes the two faces comparable.

chiqui7 rides the GPU face for weight-context (in-process pin re-point,
tile_calib precedent; the CPU face for chiqui7 already ran inside the AC3
parity run and is cited from there).

Protocol: per page a warm-up detect (not counted — GPU graph/DML kernel
preparation) then one timed detect; the reported number is the timed pass,
the provider's own ``elapsed_ms`` recorded alongside the wall clock.

Output: verification/M2-SFX-T5-TILE-KO/raw/perf-summary.json (+ per-face
rows). Wording discipline: directional evidence, low statistical power; the
word "significant" is banned; numbers are recorded as facts without quality
judgment; deployment-form choice stays a user ruling.
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

RAW_OUT = REPO / "verification" / "M2-SFX-T5-TILE-KO" / "raw"

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

#: AC3 parity run log — cited for the chiqui7 CPU face instead of re-running.
PARITY_SUMMARY = RAW_OUT / "parity-summary.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_tile_parity import load_ko_pages, sha256_file  # noqa: E402


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def gpu_swap_session(provider, onnx: Path) -> None:
    """Swap ONLY the session inside the provider engine tuple to a
    DmlExecutionProvider build (imgsz provenance from the same metadata;
    the CPU session is built first via the production engine path so the
    metadata imgsz face is identical)."""
    import onnxruntime

    _, imgsz, imgsz_source, imgsz_raw = provider._engine_or_raise()
    gpu_session = onnxruntime.InferenceSession(
        str(onnx), providers=["DmlExecutionProvider"]
    )
    provider._engine = (gpu_session, imgsz, imgsz_source, imgsz_raw)


def time_face(provider, pages, label: str, log) -> list[dict]:
    rows = []
    for p in pages:
        provider.detect(p["request"])  # warm-up, not counted
        t0 = time.perf_counter()
        result = provider.detect(p["request"])
        wall_s = round(time.perf_counter() - t0, 2)
        options = dict(result.options)
        n_tiles = int(options.get("tile_count", "0"))
        rows.append(
            {
                "sample_id": p["sample_id"],
                "page_size": [p["w"], p["h"]],
                "sfx_route": options.get("sfx_route"),
                "tile_count": n_tiles,
                "wall_s": wall_s,
                "provider_elapsed_ms": result.elapsed_ms,
            }
        )
        log(
            f"[perf] {label} {p['sample_id']} tiles={n_tiles} "
            f"wall={wall_s}s provider_ms={result.elapsed_ms}",
            flush=True,
        )
    return rows


def face_stats(rows: list[dict]) -> dict:
    walls = [r["wall_s"] for r in rows]
    return {
        "pages": len(rows),
        "total_s": round(sum(walls), 2),
        "mean_s": round(statistics.mean(walls), 2),
        "max_s": round(max(walls), 2),
        "min_s": round(min(walls), 2),
    }


def main() -> int:
    import numpy  # noqa: F401
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None

    from infrastructure.providers import detection_sfx as dsfx
    from infrastructure.providers.detection_sfx import SfxDetectionProvider

    print(f"[perf] start {now_iso()}", flush=True)
    assert sha256_file(V2B_ONNX) == PROD_PIN_SHA, "v2b sha != 生产 pin"
    assert sha256_file(CHIQUI7_ONNX) == CHIQUI7_PIN_SHA, "chiqui7 sha != 回滚 pin"

    pages = load_ko_pages()
    print(f"[perf] KO {len(pages)} 页装载完成", flush=True)

    RAW_OUT.mkdir(parents=True, exist_ok=True)
    summary = {
        "task": "M2-SFX-T5-TILE-KO AC2 tile dual-track performance",
        "generated_at_utc": now_iso(),
        "generated_from": "experiments/M2-SFX-T5-TILE-KO/perf_tile_dual.py",
        "protocol": "每页 warm-up 1 次不计 + 计测 1 次；tile 冻结口径 conf 0.5",
        "env": {"host_gpu": "NVIDIA GeForce RTX 5070 Ti",
                "gpu_ep_package": "onnxruntime-directml (DmlExecutionProvider)"},
        "faces": {},
        "wording_discipline": (
            "directional 数据如实登记不作质量判定；部署形态终选=用户裁决收口呈报项"
        ),
    }
    pin_backup = dsfx.SFX_WEIGHTS_SHA256

    # ---- CPU face: the production engine AS-IS, v2b (deployment form) ----
    provider = SfxDetectionProvider(weights_path=V2B_ONNX, conf_threshold=0.5)
    rows = time_face(provider, pages, "cpu/v2b", print)
    summary["faces"]["cpu_v2b"] = {
        "ep": "CPUExecutionProvider (生产 _build_engine 原样)",
        "weights": "v2b (生产 pin 944e8114)",
        "rows": rows,
        "stats": face_stats(rows),
    }

    # ---- GPU face: DmlExecutionProvider, v2b + chiqui7 ----
    provider = SfxDetectionProvider(weights_path=V2B_ONNX, conf_threshold=0.5)
    gpu_swap_session(provider, V2B_ONNX)
    rows = time_face(provider, pages, "gpu/v2b", print)
    summary["faces"]["gpu_v2b"] = {
        "ep": "DmlExecutionProvider (session swap, tile 序列=生产代码逐字)",
        "weights": "v2b (生产 pin 944e8114)",
        "rows": rows,
        "stats": face_stats(rows),
    }

    dsfx.SFX_WEIGHTS_SHA256 = CHIQUI7_PIN_SHA  # 重指窗口（tile_calib 先例）
    try:
        provider = SfxDetectionProvider(weights_path=CHIQUI7_ONNX, conf_threshold=0.5)
        gpu_swap_session(provider, CHIQUI7_ONNX)
        rows = time_face(provider, pages, "gpu/chiqui7", print)
        summary["faces"]["gpu_chiqui7"] = {
            "ep": "DmlExecutionProvider (session swap, tile 序列=生产代码逐字)",
            "weights": "chiqui7 (回滚 pin d87389af, 进程内重指)",
            "rows": rows,
            "stats": face_stats(rows),
        }
    finally:
        dsfx.SFX_WEIGHTS_SHA256 = pin_backup

    if PARITY_SUMMARY.is_file():
        summary["cited_chiqui7_cpu_from_ac3_parity"] = (
            "verification/M2-SFX-T5-TILE-KO/raw/parity-chiqui7.json per_page "
            "elapsed_s（CPU 生产 EP，等价性运行顺带测量）"
        )
    (RAW_OUT / "perf-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"[perf] wrote {RAW_OUT / 'perf-summary.json'}", flush=True)
    for name, face in summary["faces"].items():
        print(f"[perf] {name}: {face['stats']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
