
import json, sys, time
from pathlib import Path

src_root, weights_dir, page_path, out_path = sys.argv[1:5]
sys.path.insert(0, src_root)

import importlib.metadata as md
versions = {}
for dist in ("torch", "torchvision", "transformers", "safetensors", "python-doctr", "tokenizers"):
    try:
        versions[dist] = md.version(dist)
    except Exception:
        versions[dist] = None

from infrastructure.providers.detection_manga import MangaDetectionProvider
from ports.detection.ports import DetectionRequest

from PIL import Image
import io

# The production page_frame contract (same as the docTR adapter): the
# request carries a RAW pixel buffer (rgb24/rgb32), never an encoded file.
with Image.open(page_path) as im:
    rgb = im.convert("RGB")
    width, height = rgb.size
    frame = rgb.tobytes()

provider = MangaDetectionProvider(weights_dir=Path(weights_dir), device="cpu")
request = DetectionRequest(page_id="probe-page", image_bytes=frame, width=width, height=height)

# cold pass (engine build + weights load + one inference), then steady-state
# passes so the recorded latency separates one-off loading from per-page cost.
started = time.perf_counter()
result = provider.detect(request)
cold_ms = int((time.perf_counter() - started) * 1000)
warm_ms = []
for _ in range(3):
    started = time.perf_counter()
    result = provider.detect(request)
    warm_ms.append(int((time.perf_counter() - started) * 1000))
payload = {
    "exit": 0,
    "versions": versions,
    "provider_id": result.provider_id,
    "model": result.model,
    "n_candidates": len(result.candidates),
    "confidences": [c.confidence for c in result.candidates],
    "cold_elapsed_ms_incl_engine_build": cold_ms,
    "warm_elapsed_ms": warm_ms,
    "warm_avg_ms": sum(warm_ms) // len(warm_ms),
    "detect_reported_ms": result.elapsed_ms,
}
Path(out_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
