"""T1.1.1: real docTR inference through the production adapter.

Skips are environmental only: the docTR runtime must be installed and the
pinned weights must have been fetched (never downloaded by the adapter).
"""

from __future__ import annotations

import pytest

pytest.importorskip("doctr", reason="docTR (python-doctr) is not installed")

from t111_support import detector_device, locate_doctr_weights  # noqa: E402

_weights = locate_doctr_weights()
if _weights is None:
    pytest.skip(
        "T1.1.1 weights not fetched: run "
        "python verification/T1.1.1/scripts/fetch_doctr_weights.py "
        "(fast_base-688a8b34.pt) or set NEW_MANGA_DOCTR_WEIGHTS",
        allow_module_level=True,
    )


def _provider():
    from infrastructure.providers.detection_doctr import DoctrDetectionProvider

    return DoctrDetectionProvider(weights_path=_weights, device=detector_device())


def _text_page_bytes(width: int = 640, height: int = 400) -> bytes:
    """rgb32 BGRA pixels, exactly what the production page_frame hands over."""
    import numpy
    from PIL import Image, ImageDraw, ImageFont

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 48)
    draw.text((80, 160), "DETECT ME", fill="black", font=font)
    rgb = numpy.asarray(image, dtype=numpy.uint8)
    bgra = numpy.dstack(
        (rgb[:, :, ::-1], numpy.full((height, width, 1), 255, dtype=numpy.uint8))
    )
    return bgra.tobytes()


def _blank_page_bytes(width: int = 640, height: int = 400) -> bytes:
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
            image_bytes=_text_page_bytes(),
            width=640,
            height=400,
        )
    )
    assert result.provider_id == "local-doctr"
    assert result.provider_type == "local-doctr"
    assert result.model == "doctr/fast_base"
    assert result.coordinate_space == "page-global"
    assert len(result.candidates) >= 1
    for index, candidate in enumerate(result.candidates, start=1):
        assert candidate.reading_order == index
        assert candidate.provider_label == f"doctr-{index}"
        assert candidate.confidence is not None and 0.0 <= candidate.confidence <= 1.0
        assert len(candidate.polygon) == 4
        for x, y in candidate.polygon:
            assert 0 <= x <= 640
            assert 0 <= y <= 400
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
            width=640,
            height=400,
        )
    )
    assert result.candidates == ()
