"""T1.1.1: the docTR ``DetectionProvider`` adapter, without the heavy runtime.

Every fail-closed rung is exercised here against *lightweight* fixtures —
no torch, no docTR, no real weights. Real-inference behavior is covered by
``test_detection_doctr_real.py`` and the seam tests; nothing here pretends
to run a model.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from infrastructure.providers.detection_doctr import (
    DOCTR_WEIGHTS_SHA256,
    MERGE_HORIZONTAL_TOLERANCE_PX,
    MERGE_PAD_PX,
    PROVIDER_DOCTR,
    DoctrDetectionProvider,
    cluster_words_into_blocks,
    sha256_file,
)
from ports.detection.ports import DetectionRequest
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
)

WEIGHTS = Path("does-not-exist/fast_base-688a8b34.pt")


def _provider(**overrides) -> DoctrDetectionProvider:
    defaults = dict(weights_path=WEIGHTS, device="cpu")
    defaults.update(overrides)
    return DoctrDetectionProvider(**defaults)


def _request(image_bytes: bytes = b"", width: int = 0, height: int = 0) -> DetectionRequest:
    return DetectionRequest(page_id="page-1", image_bytes=image_bytes, width=width, height=height)


def _frame_bytes(width: int = 4, height: int = 4, mode: str = "rgb24") -> bytes:
    """A raw pixel frame — the production ``page_frame`` contract.

    All-zero pixels are fine: the fail-closed scenarios never reach
    inference, and this keeps the unit tests free of any heavy runtime.
    """
    return b"\x00" * (width * height * (3 if mode == "rgb24" else 4))


# ---------------------------------------------------------------------------
# frozen merge policy
# ---------------------------------------------------------------------------


class TestMergePolicy:
    def test_words_on_one_line_merge_into_one_block(self):
        # gap 8px <= tolerance max(19 * 0.7, 8) = 13.3px: one line, one block
        rects = [(10.0, 10.0, 40.0, 30.0), (48.0, 11.0, 90.0, 29.0)]
        blocks = cluster_words_into_blocks(rects, [0.9, 0.7])
        assert len(blocks) == 1
        polygon, confidence = blocks[0]
        assert confidence == pytest.approx(0.8)
        assert len(polygon) == 4
        xs = [p[0] for p in polygon]
        ys = [p[1] for p in polygon]
        assert min(xs) == pytest.approx(10.0 - MERGE_PAD_PX)
        assert max(xs) == pytest.approx(90.0 + MERGE_PAD_PX)
        assert min(ys) == pytest.approx(10.0 - MERGE_PAD_PX)
        assert max(ys) == pytest.approx(30.0 + MERGE_PAD_PX)

    def test_far_apart_words_stay_separate_blocks(self):
        rects = [(10.0, 10.0, 40.0, 30.0), (10.0, 400.0, 40.0, 420.0)]
        blocks = cluster_words_into_blocks(rects, [0.9, 0.9])
        assert len(blocks) == 2

    def test_blocks_are_ordered_top_to_bottom(self):
        rects = [
            (10.0, 400.0, 40.0, 420.0),
            (10.0, 10.0, 40.0, 30.0),
            (50.0, 200.0, 80.0, 220.0),
        ]
        blocks = cluster_words_into_blocks(rects, [0.5, 0.5, 0.5])
        tops = [min(y for _, y in polygon) for polygon, _ in blocks]
        assert tops == sorted(tops)

    def test_policy_is_deterministic(self):
        rects = [(10.0, 10.0, 40.0, 30.0), (55.0, 11.0, 90.0, 29.0), (10.0, 400.0, 40.0, 420.0)]
        confs = [0.9, 0.7, 0.8]
        first = cluster_words_into_blocks(rects, confs)
        second = cluster_words_into_blocks(list(reversed(rects)), list(reversed(confs)))
        assert first == second

    def test_empty_input_yields_no_blocks(self):
        assert cluster_words_into_blocks([], []) == []

    def test_rect_confidence_divergence_is_typed(self):
        with pytest.raises(ProviderInputError):
            cluster_words_into_blocks([(0.0, 0.0, 1.0, 1.0)], [])

    def test_frozen_constants_match_the_released_evaluation(self):
        # T1.1.1 gate: these are the exact values the 22/22 evaluation
        # harness ran with; changing them is a contract change.
        assert MERGE_HORIZONTAL_TOLERANCE_PX == 8.0
        assert MERGE_PAD_PX == 6.0
        assert DOCTR_WEIGHTS_SHA256.startswith("688a8b34")


# ---------------------------------------------------------------------------
# request validation
# ---------------------------------------------------------------------------


class TestRequestValidation:
    def test_empty_frame_is_typed(self):
        with pytest.raises(ProviderInputError):
            _provider().detect(_request())

    def test_byte_count_mismatch_is_typed(self):
        with pytest.raises(ProviderInputError, match="byte count"):
            _provider().detect(_request(b"\x00" * 6, width=2, height=2))

    def test_declared_size_mismatch_is_typed(self):
        # a real 4x4 rgb24 frame declared as 8x8 cannot be reshaped safely
        with pytest.raises(ProviderInputError, match="byte count"):
            _provider().detect(_request(_frame_bytes(4, 4), width=8, height=8))


# ---------------------------------------------------------------------------
# fail-closed engine resolution (no heavy runtime needed)
# ---------------------------------------------------------------------------


class TestFailClosedEngine:
    def test_missing_weights_are_not_configured(self, tmp_path: Path):
        provider = _provider(weights_path=tmp_path / "absent.pt")
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderNotConfigured, match="weights are not installed"):
            provider.detect(request)

    def test_corrupted_weights_fail_closed(self, tmp_path: Path):
        # this rung sits *after* the torch probe (check order is the
        # contract), so it is only reachable with the heavy runtime installed
        pytest.importorskip("torch", reason="torch is not installed")
        bad = tmp_path / "fast_base-688a8b34.pt"
        bad.write_bytes(b"not real weights")
        provider = _provider(weights_path=bad)
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderError, match="sha256"):
            provider.detect(request)

    def test_missing_torch_is_dependency_missing(self, tmp_path: Path, monkeypatch):
        import importlib

        real_import = importlib.import_module

        def fake_import(name, *args, **kwargs):
            if name == "torch":
                raise ImportError("no torch in this scenario")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", fake_import)
        # a *present* weights file: the assembly-gap check (zero-dependency)
        # passes, and the typed dependency gap is what surfaces next
        stub = tmp_path / "stub-fast_base.pt"
        stub.write_bytes(b"stub")
        provider = _provider(weights_path=stub)
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderDependencyMissing):
            provider.detect(request)

    def test_unsupported_device_is_typed(self, tmp_path: Path):
        # device resolution needs torch, so this rung is also post-probe
        pytest.importorskip("torch", reason="torch is not installed")
        stub = tmp_path / "stub-fast_base.pt"
        stub.write_bytes(b"stub")
        provider = _provider(weights_path=stub, device="tpu")
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderInputError, match="device"):
            provider.detect(request)


# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------


def test_provider_identity_matches_the_contract():
    provider = _provider()
    assert provider.provider_id == PROVIDER_DOCTR == "local-doctr"
    assert provider.provider_type == "local-doctr"
    assert provider.model == "doctr/fast_base"


def test_sha256_file_helper(tmp_path: Path):
    target = tmp_path / "blob.bin"
    target.write_bytes(b"abc")
    import hashlib

    assert sha256_file(target) == hashlib.sha256(b"abc").hexdigest()
