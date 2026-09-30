"""M2-PROD-DETECT-1: the manga-domain ``DetectionProvider``, without the
heavy runtime.

Every fail-closed rung is exercised here against *lightweight* fixtures —
no torch, no transformers, no real weights — plus the pure bubble-filter
and the assembly backend selector. Real-inference behavior is covered by
``test_detection_manga_real.py``; nothing here pretends to run a model.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from infrastructure.providers import detection_doctr
from infrastructure.providers.detection_manga import (
    MANGA_CONFIG_SHA256,
    MANGA_MODEL_SHA256,
    MANGA_PREPROCESSOR_SHA256,
    MERGE_POLICY_CONSTANTS,
    PROVIDER_MANGA,
    MangaDetectionProvider,
    _text_boxes_from_results,
)
from ports.detection.ports import DetectionRequest
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
)

WEIGHTS_DIR = Path("does-not-exist/ogkalu-comic-text-and-bubble-detector")

PINS = {
    "model.safetensors": MANGA_MODEL_SHA256,
    "config.json": MANGA_CONFIG_SHA256,
    "preprocessor_config.json": MANGA_PREPROCESSOR_SHA256,
}


def _provider(**overrides) -> MangaDetectionProvider:
    defaults = dict(weights_dir=WEIGHTS_DIR, device="cpu")
    defaults.update(overrides)
    return MangaDetectionProvider(**defaults)


def _request(image_bytes: bytes = b"", width: int = 0, height: int = 0) -> DetectionRequest:
    return DetectionRequest(page_id="page-1", image_bytes=image_bytes, width=width, height=height)


def _frame_bytes(width: int = 4, height: int = 4, mode: str = "rgb24") -> bytes:
    """A raw pixel frame — the production ``page_frame`` contract.

    All-zero pixels are fine: the fail-closed scenarios never reach
    inference, and this keeps the unit tests free of any heavy runtime.
    """
    return b"\x00" * (width * height * (3 if mode == "rgb24" else 4))


def _snapshot_files(tmp_path: Path) -> Path:
    """A directory holding the three snapshot filenames, wrong content."""
    directory = tmp_path / "ogkalu-comic-text-and-bubble-detector"
    directory.mkdir()
    for filename in PINS:
        (directory / filename).write_bytes(b"stub")
    return directory


# ---------------------------------------------------------------------------
# frozen merge policy: imported, never copied
# ---------------------------------------------------------------------------


class TestMergePolicyImported:
    def test_constants_are_the_doctr_objects_themselves(self):
        # MERGE_* must be shared by identity, not re-declared: the C4/C1
        # evidence numbers were measured against the production merge, so a
        # copy here could silently diverge.
        assert MERGE_POLICY_CONSTANTS == (
            detection_doctr.MERGE_VERTICAL_FACTOR,
            detection_doctr.MERGE_MIN_TOLERANCE_PX,
            detection_doctr.MERGE_HORIZONTAL_TOLERANCE_PX,
            detection_doctr.MERGE_PAD_PX,
        )

    def test_detect_merges_text_boxes_through_the_production_policy(self, monkeypatch):
        # two text boxes on one line (gap 8px <= tolerance) merge into ONE
        # block candidate — proof the production cluster_words_into_blocks
        # runs, not a private re-implementation.
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes",
            lambda model, processor, rgb, w, h: (
                [(10.0, 10.0, 40.0, 30.0, 0.9), (48.0, 11.0, 90.0, 29.0, 0.7)],
                0,
            ),
        )
        provider = _provider()
        provider._engine = (object(), object())  # engine pre-built, never used
        result = provider.detect(_request(_frame_bytes(100, 100), width=100, height=100))
        assert len(result.candidates) == 1
        assert result.candidates[0].confidence == pytest.approx(0.8)
        assert min(x for x, _ in result.candidates[0].polygon) == pytest.approx(
            10.0 - detection_doctr.MERGE_PAD_PX
        )


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
        with pytest.raises(ProviderInputError, match="byte count"):
            _provider().detect(_request(_frame_bytes(4, 4), width=8, height=8))


# ---------------------------------------------------------------------------
# fail-closed engine resolution (no heavy runtime needed)
# ---------------------------------------------------------------------------


class TestFailClosedEngine:
    def test_missing_directory_is_not_configured(self, tmp_path: Path):
        provider = _provider(weights_dir=tmp_path / "absent")
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderNotConfigured, match="weights are not installed"):
            provider.detect(request)

    def test_directory_missing_one_file_is_not_configured(self, tmp_path: Path):
        directory = _snapshot_files(tmp_path)
        (directory / "preprocessor_config.json").unlink()
        provider = _provider(weights_dir=directory)
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderNotConfigured, match="preprocessor_config.json"):
            provider.detect(request)

    def test_missing_torch_is_dependency_missing(self, tmp_path: Path, monkeypatch):
        real_import = importlib.import_module

        def fake_import(name, *args, **kwargs):
            if name == "torch":
                raise ImportError("no torch in this scenario")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", fake_import)
        # a *complete* snapshot directory: the zero-dependency existence
        # probe passes, and the typed dependency gap is what surfaces next
        provider = _provider(weights_dir=_snapshot_files(tmp_path))
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderDependencyMissing):
            provider.detect(request)

    def test_corrupted_weights_fail_closed(self, tmp_path: Path):
        # this rung sits *after* the torch probe (check order is the
        # contract), so it is only reachable with the heavy runtime installed
        pytest.importorskip("torch", reason="torch is not installed")
        provider = _provider(weights_dir=_snapshot_files(tmp_path))
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderError, match="sha256"):
            provider.detect(request)

    def test_missing_transformers_is_dependency_missing(self, tmp_path: Path, monkeypatch):
        # this rung sits after the hash gate, so the hash helper is stubbed
        # to the pins: the scenario isolates the lazy transformers import
        # (a machine with weights but without the runtime).
        pytest.importorskip("torch", reason="torch is not installed")
        import infrastructure.providers.detection_manga as manga

        monkeypatch.setattr(manga, "sha256_file", lambda path: PINS[path.name])
        real_import = importlib.import_module

        def fake_import(name, *args, **kwargs):
            if name == "transformers":
                raise ImportError("no transformers in this scenario")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(importlib, "import_module", fake_import)
        provider = _provider(weights_dir=_snapshot_files(tmp_path))
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderDependencyMissing, match="transformers"):
            provider.detect(request)

    def test_unsupported_device_is_typed(self, tmp_path: Path):
        pytest.importorskip("torch", reason="torch is not installed")
        provider = _provider(weights_dir=_snapshot_files(tmp_path), device="tpu")
        request = _request(_frame_bytes(4, 4), width=4, height=4)
        with pytest.raises(ProviderInputError, match="device"):
            provider.detect(request)


# ---------------------------------------------------------------------------
# pure bubble filter (the C4 granularity mapping)
# ---------------------------------------------------------------------------


class TestTextBoxesFromResults:
    def test_bubble_class_is_dropped_and_counted(self):
        boxes, n_bubble = _text_boxes_from_results(
            scores=[0.9, 0.8, 0.7],
            labels=[1, 0, 2],  # text_bubble, bubble (dropped), text_free
            boxes=[
                [10.0, 10.0, 40.0, 30.0],
                [50.0, 10.0, 90.0, 30.0],
                [100.0, 10.0, 130.0, 30.0],
            ],
            width=200.0,
            height=100.0,
        )
        assert n_bubble == 1
        assert len(boxes) == 2
        assert boxes[0][:4] == (10.0, 10.0, 40.0, 30.0)
        assert boxes[1][:4] == (100.0, 10.0, 130.0, 30.0)

    def test_boxes_are_clipped_to_the_page(self):
        boxes, _ = _text_boxes_from_results(
            scores=[0.9],
            labels=[1],
            boxes=[[-5.0, -5.0, 1005.0, 105.0]],
            width=100.0,
            height=50.0,
        )
        assert boxes[0][:4] == (0.0, 0.0, 100.0, 50.0)

    def test_degenerate_boxes_are_skipped(self):
        boxes, n_bubble = _text_boxes_from_results(
            scores=[0.9, 0.8],
            labels=[1, 1],
            boxes=[[10.0, 10.0, 10.0, 30.0], [20.0, 10.0, 5.0, 30.0]],
            width=100.0,
            height=50.0,
        )
        assert boxes == []
        assert n_bubble == 0

    def test_out_of_range_confidence_is_typed(self):
        from ports.providers.errors import ProviderInvalidOutput

        with pytest.raises(ProviderInvalidOutput, match="confidence"):
            _text_boxes_from_results(
                scores=[1.5], labels=[1], boxes=[[1.0, 1.0, 2.0, 2.0]],
                width=10.0, height=10.0,
            )

    def test_malformed_box_is_typed(self):
        from ports.providers.errors import ProviderInvalidOutput

        with pytest.raises(ProviderInvalidOutput, match="box"):
            _text_boxes_from_results(
                scores=[0.9], labels=[1], boxes=[[1.0, 1.0, 2.0]],
                width=10.0, height=10.0,
            )

    def test_empty_page_yields_no_boxes(self):
        boxes, n_bubble = _text_boxes_from_results([], [], [], 100.0, 100.0)
        assert boxes == []
        assert n_bubble == 0


# ---------------------------------------------------------------------------
# detect path honesty (engine stubbed, no model)
# ---------------------------------------------------------------------------


class TestDetectPathHonesty:
    def test_empty_detection_yields_zero_candidates(self, monkeypatch):
        """A text-free page stays honest: zero candidates, no padding boxes.
        The typed INVALID_INPUT lives in the handler (seam-tested)."""
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes",
            lambda model, processor, rgb, w, h: ([], 0),
        )
        provider = _provider()
        provider._engine = (object(), object())
        result = provider.detect(_request(_frame_bytes(20, 10), width=20, height=10))
        assert result.candidates == ()

    def test_detect_never_returns_polygons_past_the_page(self, monkeypatch):
        """A text box hugging the page edge must come back clipped: the
        padded block polygon stays inside the decoded page bounds."""
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes",
            lambda model, processor, rgb, w, h: (
                [(0.0, 0.0, 19.5, 9.7, 0.93)],
                0,
            ),
        )
        provider = _provider()
        provider._engine = (object(), object())
        result = provider.detect(_request(_frame_bytes(20, 10), width=20, height=10))
        assert len(result.candidates) == 1
        for x, y in result.candidates[0].polygon:
            assert 0.0 <= x <= 20.0
            assert 0.0 <= y <= 10.0

    def test_result_provenance_and_anonymous_labels(self, monkeypatch):
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes",
            lambda model, processor, rgb, w, h: (
                [(5.0, 5.0, 15.0, 9.0, 0.88), (60.0, 40.0, 90.0, 60.0, 0.77)],
                2,
            ),
        )
        provider = _provider()
        provider._engine = (object(), object())
        result = provider.detect(_request(_frame_bytes(100, 80), width=100, height=80))
        assert result.provider_id == PROVIDER_MANGA == "local-manga"
        assert result.provider_type == "local-manga"
        assert result.coordinate_space == "page-global"
        for index, candidate in enumerate(result.candidates, start=1):
            assert candidate.reading_order == index
            assert candidate.provider_label == f"manga-{index}"
        provenance = result.provenance()
        assert provenance["candidate_count"] == len(result.candidates)
        assert provenance["elapsed_ms"] is not None
        assert dict(result.options)["bubble_class_dropped"] == "2"
        assert dict(result.options)["conf_threshold"] == "0.5"


# ---------------------------------------------------------------------------
# identity
# ---------------------------------------------------------------------------


def test_provider_identity_matches_the_contract():
    provider = _provider()
    assert provider.provider_id == PROVIDER_MANGA == "local-manga"
    assert provider.provider_type == "local-manga"
    assert provider.model == "manga/ogkalu-comic-text-and-bubble-detector"
    assert provider.requirements == ("transformers", "torch")


def test_sha256_pins_match_the_c4_weights_manifest():
    # The three-file pins are the C4 weights-manifest values (HF revision
    # 16e8a622); changing a pin without a new qualification slice is a
    # contract break.
    assert MANGA_MODEL_SHA256.startswith("037930a8")
    assert MANGA_CONFIG_SHA256.startswith("b6d70793")
    assert MANGA_PREPROCESSOR_SHA256.startswith("7e9e2245")


# ---------------------------------------------------------------------------
# assembly backend selection (Qt-free production assembly)
# ---------------------------------------------------------------------------


class _HeadlessDecoder:
    def decode(self, payload: bytes):
        del payload

        from application.importing.images.ports import DecodedImage

        return DecodedImage(width=1, height=1, mime_type="image/png")


class _HeadlessStyleAnalyzer:
    def analyze_pixel_styles(self, image):
        del image
        return []


def _assemble(data_root: Path, *, mock_local_providers: bool = False):
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services

    return assemble_core_services(
        data_root / "library.db",
        data_root / "managed",
        image_decoder=_HeadlessDecoder(),
        font_catalog=object(),  # type: ignore[arg-type]
        layout_engine=object(),  # type: ignore[arg-type]
        compositor=object(),  # type: ignore[arg-type]
        source_styles=SourceStyleService(_HeadlessStyleAnalyzer()),
        mock_local_providers=mock_local_providers,
    )


def _wired_detector(core):
    """Reach the assembled detector through the ``_typed`` wrapper closure
    (same technique as ``test_detector_assembly.py``)."""
    handlers = core.pipeline._executor._handlers
    assert "detect" in handlers
    handler = handlers["detect"]
    for cell in handler.__closure__ or ():
        try:
            inner = cell.cell_contents
        except ValueError:  # empty cell
            continue
        bound = getattr(inner, "__self__", None)
        detector = getattr(getattr(bound, "deps", None), "detector", None)
        if detector is not None:
            return detector
    raise AssertionError("detect handler does not expose a wired detector")


@pytest.fixture()
def _clean_detector_env(monkeypatch):
    monkeypatch.delenv("NEWMANGA_DETECTOR_BACKEND", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_DEVICE", raising=False)


class TestAssemblyBackendSelection:
    def test_default_backend_is_manga(self, tmp_path: Path, _clean_detector_env):
        from infrastructure.providers.detection_manga import MANGA_WEIGHTS_DIRNAME

        core = _assemble(tmp_path / "data-root")
        try:
            detector = _wired_detector(core)
            assert isinstance(detector, MangaDetectionProvider)
            assert detector.provider_id == "local-manga"
            assert detector.weights_dir == (
                tmp_path / "data-root" / "models" / "detector" / MANGA_WEIGHTS_DIRNAME
            )
        finally:
            core.conn.close()

    def test_doctr_backend_switch_keeps_the_released_path(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "doctr")
        monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
        from infrastructure.providers.detection_doctr import (
            DOCTR_WEIGHTS_FILENAME,
            DoctrDetectionProvider,
        )

        core = _assemble(tmp_path / "data-root")
        try:
            detector = _wired_detector(core)
            assert isinstance(detector, DoctrDetectionProvider)
            assert detector.provider_id == "local-doctr"
            assert detector.weights_path == (
                tmp_path
                / "data-root"
                / "models"
                / "detector"
                / DOCTR_WEIGHTS_FILENAME
            )
        finally:
            core.conn.close()

    def test_weights_override_stays_backend_specific(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "manga")
        override = tmp_path / "manga-snapshot"
        override.mkdir()
        monkeypatch.setenv("NEWMANGA_DETECTOR_WEIGHTS", str(override))
        core = _assemble(tmp_path / "data-root")
        try:
            detector = _wired_detector(core)
            assert isinstance(detector, MangaDetectionProvider)
            assert detector.weights_dir == override
        finally:
            core.conn.close()

    def test_unknown_backend_fails_the_assembly(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "sam")
        with pytest.raises(ValueError, match="NEWMANGA_DETECTOR_BACKEND"):
            _assemble(tmp_path / "data-root")

    def test_mock_path_is_unaffected_by_the_backend(self, tmp_path: Path, monkeypatch):
        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "manga")
        from infrastructure.providers.mock_local import MockLocalDetectionProvider

        core = _assemble(tmp_path / "data-root", mock_local_providers=True)
        try:
            assert isinstance(_wired_detector(core), MockLocalDetectionProvider)
        finally:
            core.conn.close()
