"""TA3-A 前置探测：docTR CPU 对正常页与 webtoon 长条的真实行为。"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, "src")
os.environ.setdefault(
    "NEWMANGA_DETECTOR_WEIGHTS",
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL/weights/fast_base-688a8b34.pt",
)

import numpy as np
from PIL import Image

from infrastructure.providers.detection_doctr import DoctrDetectionProvider
from ports.detection.ports import DetectionRequest

PROVIDER = DoctrDetectionProvider(
    weights_path=Path(os.environ["NEWMANGA_DETECTOR_WEIGHTS"]), device="cpu"
)


def probe(name: str, path: str) -> None:
    im = Image.open(path).convert("RGB")
    rgb = np.asarray(im)
    req = DetectionRequest(
        page_id=f"probe-{name}",
        image_bytes=rgb.tobytes(),
        width=im.width,
        height=im.height,
    )
    started = time.perf_counter()
    try:
        result = PROVIDER.detect(req)
        print(
            f"{name}\t{im.width}x{im.height}\tOK\tcandidates={len(result.candidates)}\t"
            f"elapsed_ms={result.elapsed_ms}\twall_s={time.perf_counter() - started:.1f}",
            flush=True,
        )
    except Exception as exc:  # noqa: BLE001
        print(
            f"{name}\t{im.width}x{im.height}\tFAIL\t{type(exc).__name__}: "
            f"{str(exc)[:300]}\twall_s={time.perf_counter() - started:.1f}",
            flush=True,
        )


probe("K11-pc-kr", "test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg")
probe("K02-webtoon-600x18401", "test_assets/comic_golden_suite/韩漫_KO/01_real_webtoon_cleaned_dataset/K02_651664_112/base.png")
