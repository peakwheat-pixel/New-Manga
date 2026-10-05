"""Extract the v2b real-weights regression anchor for K07_R123.

M2-SFX-T4-SWITCH AC2 follow-up: the real-weights test anchor moves with the
production pin. The old anchor (experiments/M2-SFX-DETECT/onnx-sfx-frames.json,
``chiqui7_yolo11s_seg``) belongs to the chiqui7 era and does not carry across
weights. This script re-runs the exact production call path the test uses —
``SfxDetectionProvider.detect`` on the deployed v2b weights file — and records
the resulting sfx detections (conf >= 0.5) as the new anchor JSON.

Run with the inference venv (onnxruntime present):
    "G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/Scripts/python.exe" \
        experiments/M2-SFX-T4-SWITCH/extract_v2b_anchor.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.providers.detection_sfx import SfxDetectionProvider  # noqa: E402
from ports.detection.ports import DetectionRequest  # noqa: E402

WEIGHTS = Path("G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx")
FRAME = Path("G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png")
EXPECTED_WEIGHTS_SHA256 = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
)
OUT = Path(__file__).resolve().parent / "v2b-k07-r123-anchor.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    from PIL import Image

    weights_sha = sha256_file(WEIGHTS)
    if weights_sha != EXPECTED_WEIGHTS_SHA256:
        print(f"FATAL: weights sha mismatch: {weights_sha}")
        return 2

    with Image.open(FRAME) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        frame_bytes = rgb.tobytes()

    provider = SfxDetectionProvider(weights_path=WEIGHTS)
    result = provider.detect(
        DetectionRequest(
            page_id="K07_R123",
            image_bytes=frame_bytes,
            width=width,
            height=height,
        )
    )

    detections = []
    for candidate in result.candidates:
        conf = candidate.confidence
        if conf is None or conf < 0.5:
            continue
        if not candidate.provider_label.startswith("sfx-"):
            continue
        xs = [point[0] for point in candidate.polygon]
        ys = [point[1] for point in candidate.polygon]
        detections.append(
            {
                "cls": "sfx",
                "conf": float(conf),
                "box_xyxy": [
                    round(min(xs), 1),
                    round(min(ys), 1),
                    round(max(xs), 1),
                    round(max(ys), 1),
                ],
            }
        )
    detections.sort(key=lambda det: -det["conf"])

    payload = {
        "schema": "m2-sfx-t4-switch/real-anchor@1",
        "task": "M2-SFX-T4-SWITCH",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "extraction": "SfxDetectionProvider.detect — same call path as tests/providers/test_detection_sfx.py",
        "weights": str(WEIGHTS),
        "weights_sha256": weights_sha,
        "frame": str(FRAME),
        "frame_sha256": sha256_file(FRAME),
        "conf_threshold": 0.5,
        "detections": detections,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"anchor written: {OUT}")
    for det in detections:
        print(f"  {det['cls']} conf={det['conf']:.4f} box={det['box_xyxy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
