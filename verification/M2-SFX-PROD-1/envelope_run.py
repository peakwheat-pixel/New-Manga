"""M2-SFX-PROD-1 AC6 envelope: CPU ms/page for the SFX provider (n>=3).

Measures the PRODUCTION provider (``src/infrastructure/providers/
detection_sfx.py``) over the evaluation sample frames (the same KO webtoon
regions the M2-SFX-DETECT-EVAL measured) plus a synthetic page, on the CPU
ExecutionProvider. Cold = first detect (includes onnxruntime session build +
the 41 MB weight sha256 verification); warm = subsequent detects.

Usage (from the repository root):
  "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
      verification/M2-SFX-PROD-1/envelope_run.py --out <results.json>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import time
from pathlib import Path

import numpy as np
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
sys_root = REPO_ROOT / "src"

import sys

if str(sys_root) not in sys.path:
    sys.path.insert(0, str(sys_root))

from infrastructure.providers.detection_sfx import (  # noqa: E402
    SFX_WEIGHTS_SHA256,
    SfxDetectionProvider,
)
from ports.detection.ports import DetectionRequest  # noqa: E402

REAL_WEIGHTS = Path(
    "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx"
)
FRAMES = [
    ("K07_R123", Path("G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png")),
    ("K07_R121", Path("G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R121.png")),
    ("K08_R019", Path("G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K08_R019.png")),
]
WARM_RUNS = 5


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    assert sha256_file(REAL_WEIGHTS) == SFX_WEIGHTS_SHA256, "weights pin mismatch"
    provider = SfxDetectionProvider(weights_path=REAL_WEIGHTS)

    pages = []
    for name, path in FRAMES:
        with Image.open(path) as image:
            rgb = image.convert("RGB")
        pages.append((name, rgb.tobytes(), rgb.size[0], rgb.size[1]))
    # The synthetic probe page (same generator shape as the DETECT-2/3 probes).
    synth = Image.new("RGB", (900, 1300), "white")
    pages.append(("synthetic-900x1300", synth.tobytes(), 900, 1300))

    results = {}
    for name, data, width, height in pages:
        request = DetectionRequest(
            page_id=name, image_bytes=data, width=width, height=height
        )
        cold = provider.detect(request)
        warm_ms = []
        n_candidates = len(cold.candidates)
        for _ in range(WARM_RUNS):
            started = time.perf_counter()
            warm = provider.detect(request)
            warm_ms.append((time.perf_counter() - started) * 1000)
            assert len(warm.candidates) == n_candidates
        results[name] = {
            "page_size": f"{width}x{height}",
            "candidates": n_candidates,
            "provider_elapsed_ms_cold": cold.elapsed_ms,
            "wall_ms_warm": [round(value, 1) for value in warm_ms],
            "wall_ms_warm_median": round(statistics.median(warm_ms), 1),
            "wall_ms_warm_mean": round(statistics.mean(warm_ms), 1),
        }
        print(
            f"{name}: {width}x{height} candidates={n_candidates} "
            f"cold={cold.elapsed_ms}ms warm_median={statistics.median(warm_ms):.1f}ms"
        )

    payload = {
        "schema": "m2-sfx-prod-1/envelope@1",
        "task": "M2-SFX-PROD-1",
        "date": "2026-10-01",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "onnxruntime": __import__("onnxruntime").__version__,
        "execution_provider": "CPUExecutionProvider",
        "weights": str(REAL_WEIGHTS),
        "weights_sha256": SFX_WEIGHTS_SHA256,
        "weights_bytes": REAL_WEIGHTS.stat().st_size,
        "conf_threshold": 0.5,
        "warm_runs": WARM_RUNS,
        "pages": results,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"envelope -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
