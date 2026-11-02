"""CORE-SLIM-2: RT-DETR-v2 ONNX detection adapter (no model download)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.providers import detection_manga_onnx as onnx_det  # noqa: E402
from infrastructure.providers.detection_manga import (  # noqa: E402
    MANGA_CONF_THRESHOLD,
)
from ports.detection.ports import DetectionRequest  # noqa: E402
from ports.providers.errors import (  # noqa: E402
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
)


def _frame(width: int = 8, height: int = 6) -> bytes:
    return bytes(width * height * 3)


def _request(width: int = 8, height: int = 6) -> DetectionRequest:
    return DetectionRequest(
        page_id="p1", image_bytes=_frame(width, height), width=width, height=height
    )


class _FakeSession:
    def __init__(self, logits, boxes, providers=("DmlExecutionProvider",)):
        self._logits = logits
        self._boxes = boxes
        self._providers = list(providers)
        self.calls = []

    def run(self, output_names, feed):
        self.calls.append(feed)
        return [self._logits, self._boxes]

    def get_providers(self):
        return list(self._providers)


def _synthetic_outputs(queries: int = 3):
    import numpy as np

    logits = np.full((1, queries, 3), -10.0, dtype=np.float32)
    boxes = np.zeros((1, queries, 4), dtype=np.float32)
    # query 0: class 1 (text_bubble) at score 0.9
    logits[0, 0, 1] = 2.2
    boxes[0, 0] = [0.5, 0.5, 0.2, 0.1]
    # query 1: bubble class at score 0.9 (must be counted, never kept)
    logits[0, 1, 0] = 2.2
    boxes[0, 1] = [0.2, 0.2, 0.1, 0.1]
    # query 2: below threshold
    logits[0, 2, 2] = -3.0
    boxes[0, 2] = [0.9, 0.9, 0.05, 0.05]
    return logits, boxes


def test_preprocess_is_fixed_640_square_chw_scaled() -> None:
    import numpy as np

    rgb = np.zeros((30, 40, 3), dtype=np.uint8)
    rgb[..., 0] = 255  # pure red
    tensor = onnx_det.preprocess_rgb(rgb)

    assert tensor.shape == (1, 3, onnx_det.MANGA_ONNX_INPUT_SIZE, onnx_det.MANGA_ONNX_INPUT_SIZE)
    assert tensor.dtype == np.float32
    assert tensor[0, 0, 0, 0] == pytest.approx(1.0)  # R channel rescaled 1/255
    assert tensor[0, 1, 0, 0] == pytest.approx(0.0)
    assert tensor[0, 2, 0, 0] == pytest.approx(0.0)


def test_postprocess_sigmoid_threshold_and_scale_to_page() -> None:
    import numpy as np

    logits, boxes = _synthetic_outputs()
    scores, labels, kept = onnx_det.postprocess_outputs(
        [logits, boxes], width=100, height=200, threshold=MANGA_CONF_THRESHOLD
    )

    # query 2 is below threshold; queries 0 and 1 stay (class filtering is the
    # SHARED filter's job, so the bubble class is still reported here).
    assert len(scores) == 2
    assert labels == [1, 0]
    assert scores[0] > 0.85
    # cxcywh 0.5,0.5,0.2,0.1 on a 100x200 page -> 40x20 box centered
    assert kept[0] == pytest.approx([40.0, 90.0, 60.0, 110.0])


def test_detect_uses_the_shared_filter_and_merge(monkeypatch) -> None:
    import numpy as np

    logits, boxes = _synthetic_outputs()
    session = _FakeSession(logits, boxes)
    monkeypatch.setattr(
        onnx_det, "_build_engine", lambda weights_path, device: session
    )
    provider = onnx_det.MangaDetectionOnnxProvider(
        weights_path=Path("unused.onnx"), device="dml"
    )

    result = provider.detect(_request(width=100, height=200))

    options = dict(result.options)
    assert options["backend"] == "onnx"
    assert options["arch"] == "rt_detr_v2"
    assert options["inference_ep"] == "DmlExecutionProvider"
    assert options["conf_threshold"] == str(MANGA_CONF_THRESHOLD)
    # 2 boxes above threshold; the bubble class is dropped by the shared filter
    assert options["text_boxes_pre_merge"] == "1"
    assert options["bubble_class_dropped"] == "1"
    assert len(result.candidates) == 1
    assert result.candidates[0].provider_label == "manga-1"
    # every candidate polygon lives in page-global absolute pixels
    assert all(0.0 <= x <= 100.0 and 0.0 <= y <= 200.0 for x, y in result.candidates[0].polygon)


def test_request_validation_is_the_frozen_page_frame_contract() -> None:
    provider = onnx_det.MangaDetectionOnnxProvider(weights_path=Path("unused.onnx"))
    with pytest.raises(ProviderInputError, match="no image bytes"):
        provider.detect(DetectionRequest(page_id="p", image_bytes=b"", width=4, height=4))
    with pytest.raises(ProviderInputError, match="byte count"):
        provider.detect(
            DetectionRequest(page_id="p", image_bytes=b"\x00" * 4, width=4, height=4)
        )


def test_missing_model_is_not_configured_with_backend_guidance(tmp_path: Path) -> None:
    provider = onnx_det.MangaDetectionOnnxProvider(weights_path=tmp_path / "absent")
    with pytest.raises(ProviderNotConfigured) as excinfo:
        provider.detect(_request())
    assert "NEWMANGA_DETECTOR_BACKEND=torch" in str(excinfo.value)


def test_sha256_pin_rejects_a_substituted_model(tmp_path: Path) -> None:
    model = tmp_path / "rtdetr-v2-fixed.onnx"
    model.write_bytes(b"not-the-pinned-graph")
    with pytest.raises(ProviderError, match="sha256"):
        onnx_det._build_engine(model, "cpu")


def test_resolve_model_path_accepts_a_weights_directory(tmp_path: Path) -> None:
    directory = tmp_path / "weights" / "manga"
    directory.mkdir(parents=True)
    assert (
        onnx_det.resolve_onnx_model_path(directory)
        == directory / onnx_det.MANGA_ONNX_FILENAME
    )
    explicit = tmp_path / "custom.onnx"
    assert onnx_det.resolve_onnx_model_path(explicit) == explicit


def test_pin_is_a_64_hex_literal() -> None:
    pin = onnx_det.MANGA_ONNX_SHA256
    assert len(pin) == 64
    assert all(character in "0123456789abcdef" for character in pin)
    # the same pin is duplicated as a literal in the build script (a PowerShell
    # script cannot import src/**): keep the two in lockstep.
    script = Path(__file__).resolve().parents[2] / "packaging" / "m2ac5" / "build_sidecar.ps1"
    assert pin in script.read_text(encoding="utf-8")
