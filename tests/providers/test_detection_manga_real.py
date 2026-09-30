"""M2-PROD-DETECT-1: real manga-domain inference through the production
adapter.

Skips are environmental only: the torch/transformers runtime must be
installed and the pinned snapshot must exist on a local (never downloaded)
path. The weights live in the gitignored task-env tree; point
``NEW_MANGA_MANGA_WEIGHTS`` at a snapshot directory or rely on the known
local qualification snapshot.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytest.importorskip("torch", reason="torch is not installed")
pytest.importorskip("transformers", reason="transformers is not installed")

#: env override first, then the local C4 qualification snapshot (gitignored
#: task-env tree; never committed, never fetched at test time).
_WEIGHT_CANDIDATES = [
    os.environ.get("NEW_MANGA_MANGA_WEIGHTS", ""),
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/ogkalu-comic-text-and-bubble-detector",
]
_weights = next(
    (Path(candidate) for candidate in _WEIGHT_CANDIDATES if candidate and Path(candidate).is_dir()),
    None,
)
if _weights is None:
    pytest.skip(
        "manga detector snapshot not found: set NEW_MANGA_MANGA_WEIGHTS to "
        "the pinned ogkalu-comic-text-and-bubble-detector directory "
        "(model.safetensors / config.json / preprocessor_config.json)",
        allow_module_level=True,
    )


def _provider():
    from infrastructure.providers.detection_manga import MangaDetectionProvider

    return MangaDetectionProvider(weights_dir=_weights, device="cpu")


def _comic_page_bytes(width: int = 900, height: int = 1300) -> bytes:
    """rgb32 BGRA pixels of a synthetic manga page — exactly what the
    production page_frame hands over. Same bubble geometry as the released
    T1.1.1 seam samples; the pinned model detected 3/3 text boxes at
    conf >= 0.93 in the AC3 gate run."""
    import numpy
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 44)
    for cx, cy, rx, ry, text in (
        (450, 300, 240, 130, "これはテストです"),
        (300, 750, 200, 110, "こんにちは"),
        (620, 1050, 220, 120, "検出の確認"),
    ):
        draw.ellipse(
            (cx - rx, cy - ry, cx + rx, cy + ry),
            fill="white",
            outline="black",
            width=4,
        )
        text_width = draw.textlength(text, font=font)
        draw.text((cx - text_width / 2, cy - font.size / 2), text, fill="black", font=font)
    rgb = numpy.asarray(image, dtype=numpy.uint8)
    bgra = numpy.dstack(
        (rgb[:, :, ::-1], numpy.full((height, width, 1), 255, dtype=numpy.uint8))
    )
    return bgra.tobytes()


def _blank_page_bytes(width: int = 800, height: int = 1100) -> bytes:
    import numpy
    from PIL import Image

    rgb = numpy.asarray(Image.new("RGB", (width, height), "white"), dtype=numpy.uint8)
    bgra = numpy.dstack(
        (rgb[:, :, ::-1], numpy.full((height, width, 1), 255, dtype=numpy.uint8))
    )
    return bgra.tobytes()


def test_real_detection_returns_block_candidates() -> None:
    from ports.detection.ports import DetectionRequest

    result = _provider().detect(
        DetectionRequest(
            page_id="page-1",
            image_bytes=_comic_page_bytes(),
            width=900,
            height=1300,
        )
    )
    assert result.provider_id == "local-manga"
    assert result.provider_type == "local-manga"
    assert result.model == "manga/ogkalu-comic-text-and-bubble-detector"
    assert result.coordinate_space == "page-global"
    assert len(result.candidates) >= 1
    for index, candidate in enumerate(result.candidates, start=1):
        assert candidate.reading_order == index
        assert candidate.provider_label == f"manga-{index}"
        assert candidate.confidence is not None and 0.0 <= candidate.confidence <= 1.0
        assert len(candidate.polygon) == 4
        for x, y in candidate.polygon:
            assert 0 <= x <= 900
            assert 0 <= y <= 1300
    provenance = result.provenance()
    assert provenance["candidate_count"] == len(result.candidates)
    assert provenance["elapsed_ms"] is not None


def test_real_blank_page_yields_zero_candidates() -> None:
    """The adapter stays honest on a text-free page: zero candidates, no
    padding boxes. The typed INVALID_INPUT lives in the handler (covered by
    the seam tests' no-text case)."""
    from ports.detection.ports import DetectionRequest

    result = _provider().detect(
        DetectionRequest(
            page_id="page-2",
            image_bytes=_blank_page_bytes(),
            width=800,
            height=1100,
        )
    )
    assert result.candidates == ()
