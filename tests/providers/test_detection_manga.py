"""M2-PROD-DETECT-1: the manga-domain ``DetectionProvider``, without the
heavy runtime.

Every fail-closed rung is exercised here against *lightweight* fixtures —
no torch, no transformers, no real weights — plus the pure bubble-filter
and the assembly backend selector. The full-``detect`` cases additionally
need numpy for the frame decode (normally a torch dependency; those cases
skip cleanly without it — DSH r1 R8). Real-inference behavior is covered
by ``test_detection_manga_real.py``; nothing here pretends to run a model.
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from infrastructure.providers import detection_doctr
from infrastructure.providers import detection_manga
from infrastructure.providers.detection_manga import (
    MANGA_CONFIG_SHA256,
    MANGA_MODEL_SHA256,
    MANGA_PREPROCESSOR_SHA256,
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
        # copy here could silently diverge. ``is`` (not ``==``) is the guard
        # a copied float literal cannot pass — value equality would keep
        # passing after a literal copy (DSH r1 R3).
        assert detection_manga.MERGE_VERTICAL_FACTOR is detection_doctr.MERGE_VERTICAL_FACTOR
        assert detection_manga.MERGE_MIN_TOLERANCE_PX is detection_doctr.MERGE_MIN_TOLERANCE_PX
        assert (
            detection_manga.MERGE_HORIZONTAL_TOLERANCE_PX
            is detection_doctr.MERGE_HORIZONTAL_TOLERANCE_PX
        )
        assert detection_manga.MERGE_PAD_PX is detection_doctr.MERGE_PAD_PX
        # the frozen tuple keeps the doctr order as well
        assert detection_manga.MERGE_POLICY_CONSTANTS == (
            detection_doctr.MERGE_VERTICAL_FACTOR,
            detection_doctr.MERGE_MIN_TOLERANCE_PX,
            detection_doctr.MERGE_HORIZONTAL_TOLERANCE_PX,
            detection_doctr.MERGE_PAD_PX,
        )

    def test_detect_merges_text_boxes_through_the_production_policy(self, monkeypatch):
        pytest.importorskip("numpy", reason="numpy is not installed")
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
        with pytest.raises(
            ProviderNotConfigured, match="weights are not installed"
        ) as excinfo:
            provider.detect(request)
        # configuration guidance carries the backend hint for the docTR
        # migration path (DSH r1 R5)
        assert "NEWMANGA_DETECTOR_BACKEND=doctr" in str(excinfo.value)

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

    def test_nan_geometry_is_typed_not_coerced(self):
        # NaN survives the min/max clip (every comparison is False), so it
        # must be rejected before the degeneracy skip — a NaN polygon is
        # malformed model output, never a silently dropped zero-area box
        # (DSH r1 R9).
        from ports.providers.errors import ProviderInvalidOutput

        with pytest.raises(ProviderInvalidOutput, match="not finite"):
            _text_boxes_from_results(
                scores=[0.9],
                labels=[1],
                boxes=[[float("nan"), 10.0, 40.0, 30.0]],
                width=100.0,
                height=50.0,
            )

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
        # detect() decodes the frame through _frame_pixels, which needs numpy
        # (a hard torch dependency) — skip, not error, without it (DSH r1 R8)
        pytest.importorskip("numpy", reason="numpy is not installed")
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
        pytest.importorskip("numpy", reason="numpy is not installed")
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
        pytest.importorskip("numpy", reason="numpy is not installed")
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
# M2-DETECT-WEBTOON-TILING: webtoon long-strip tiling path
# ---------------------------------------------------------------------------

_TILING_ENV_VARS = (
    "NEWMANGA_DETECTOR_TILING_TILE_SIZE",
    "NEWMANGA_DETECTOR_TILING_OVERLAP",
    "NEWMANGA_DETECTOR_TILING_NMS_IOU",
    "NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO",
)


def _clean_tiling_env(monkeypatch) -> None:
    for name in _TILING_ENV_VARS:
        monkeypatch.delenv(name, raising=False)


class TestTilingConfig:
    """The tiling parameters are env-configurable with DIAG-frozen defaults
    (``NEWMANGA_DETECTOR_TILING_*``, the SFX conf-threshold env precedent);
    an illegal value fails fast — never a silent default."""

    def test_defaults_match_the_diagnosed_experiment(self, monkeypatch):
        _clean_tiling_env(monkeypatch)
        config = detection_manga._tiling_config(detection_manga._tiling_trigger_ratio())
        assert config.tile_size == 1024  # the DIAG tile experiment size
        assert config.overlap == 128  # the DIAG overlap band
        assert config.nms_iou == 0.5  # the DIAG cross-tile dedup IoU
        assert config.trigger_ratio == 4.0  # Owner ruling, see task doc

    def test_env_overrides_each_parameter(self, monkeypatch):
        _clean_tiling_env(monkeypatch)
        monkeypatch.setenv("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "512")
        monkeypatch.setenv("NEWMANGA_DETECTOR_TILING_OVERLAP", "64")
        monkeypatch.setenv("NEWMANGA_DETECTOR_TILING_NMS_IOU", "0.6")
        monkeypatch.setenv("NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO", "8")
        config = detection_manga._tiling_config(detection_manga._tiling_trigger_ratio())
        assert config.tile_size == 512
        assert config.overlap == 64
        assert config.nms_iou == 0.6
        assert config.trigger_ratio == 8.0

    @pytest.mark.parametrize(
        ("env_name", "value"),
        [
            ("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "0"),
            ("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "-1024"),
            ("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "10.5"),
            ("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "abc"),
            ("NEWMANGA_DETECTOR_TILING_OVERLAP", "-1"),
            ("NEWMANGA_DETECTOR_TILING_OVERLAP", "1024"),  # >= tile size
            ("NEWMANGA_DETECTOR_TILING_OVERLAP", "abc"),
            ("NEWMANGA_DETECTOR_TILING_NMS_IOU", "0.0"),
            ("NEWMANGA_DETECTOR_TILING_NMS_IOU", "-0.1"),
            ("NEWMANGA_DETECTOR_TILING_NMS_IOU", "1.0"),
            ("NEWMANGA_DETECTOR_TILING_NMS_IOU", "abc"),
            ("NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO", "0"),
            ("NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO", "-4"),
            ("NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO", "abc"),
            # M2-DETECTION-HYGIENE (TILING r1 R3): empty/whitespace values are
            # typed-rejected too (never-silent-default) instead of falling
            # back to the frozen default.
            ("NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO", ""),
            ("NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO", "  "),
            ("NEWMANGA_DETECTOR_TILING_TILE_SIZE", ""),
            ("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "  "),
            ("NEWMANGA_DETECTOR_TILING_OVERLAP", ""),
            ("NEWMANGA_DETECTOR_TILING_OVERLAP", "  "),
            ("NEWMANGA_DETECTOR_TILING_NMS_IOU", ""),
            ("NEWMANGA_DETECTOR_TILING_NMS_IOU", "  "),
        ],
    )
    def test_illegal_values_fail_fast(self, monkeypatch, env_name, value):
        _clean_tiling_env(monkeypatch)
        monkeypatch.setenv(env_name, value)
        if env_name == "NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO":
            # parsed eagerly before the trigger test (r1 R1 lazy split)
            with pytest.raises(ValueError, match=env_name):
                detection_manga._tiling_trigger_ratio()
        else:
            with pytest.raises(ValueError, match=env_name):
                detection_manga._tiling_config(
                    detection_manga._tiling_trigger_ratio()
                )

    def test_unrelated_env_has_no_effect(self, monkeypatch):
        _clean_tiling_env(monkeypatch)
        monkeypatch.setenv("NEWMANGA_SFX_CONF_THRESHOLD", "0.75")
        config = detection_manga._tiling_config(detection_manga._tiling_trigger_ratio())
        assert config.tile_size == 1024


class TestTilingTrigger:
    """Trigger = height/max(width, 1) > trigger_ratio (strict)."""

    def test_k01_long_strip_triggers(self):
        assert detection_manga._tiling_triggered(690.0, 62133.0, 4.0) is True

    def test_k02_and_k04_trigger(self):
        assert detection_manga._tiling_triggered(600.0, 18401.0, 4.0) is True
        assert detection_manga._tiling_triggered(690.0, 28156.0, 4.0) is True

    def test_bj02_normal_page_does_not_trigger(self):
        # 2946x4167 -> h/w = 1.41; the DIAG control page must stay on the
        # byte-identical untiled path.
        assert detection_manga._tiling_triggered(2946.0, 4167.0, 4.0) is False

    def test_boundary_is_strict_greater_than(self):
        # h/w == ratio exactly -> NOT triggered (documented semantics).
        assert detection_manga._tiling_triggered(100.0, 400.0, 4.0) is False
        assert detection_manga._tiling_triggered(100.0, 400.4, 4.0) is True

    def test_zero_width_is_defended(self):
        # max(width, 1) guards the division; request validation rejects
        # width<=0 earlier — this is the pure function's own defence.
        assert detection_manga._tiling_triggered(0.0, 10.0, 4.0) is True

    def test_trigger_follows_the_configured_ratio(self):
        assert detection_manga._tiling_triggered(1000.0, 3999.0, 4.0) is False
        assert detection_manga._tiling_triggered(1000.0, 3999.0, 3.0) is True


class TestTilingTiles:
    """Pure tile geometry: overlapping grid, the DIAG experiment's exact
    stepping (step = tile - overlap, last tile clipped to the page)."""

    def test_k01_geometry_matches_the_diagnosed_experiment(self):
        # DIAG probe-results.json K01.tile_experiment: n_tiles=70, origins
        # 0..61824 step 896, final tile crop_h=309 — the production default
        # config must reproduce this grid exactly.
        tiles = detection_manga._tiling_tiles(690.0, 62133.0, 1024, 128)
        assert len(tiles) == 70
        assert tiles[0] == (0.0, 0.0, 690.0, 1024.0)
        assert tiles[-1] == (0.0, 61824.0, 690.0, 62133.0)
        assert [t[1] for t in tiles] == [float(k * 896) for k in range(70)]

    def test_page_smaller_than_tile_is_one_tile(self):
        tiles = detection_manga._tiling_tiles(690.0, 800.0, 1024, 128)
        assert tiles == [(0.0, 0.0, 690.0, 800.0)]

    def test_exact_fit_does_not_spawn_an_empty_tail_tile(self):
        # height 1792 = 896 + 896: origins 0 and 896 cover it exactly.
        tiles = detection_manga._tiling_tiles(1024.0, 1792.0, 1024, 128)
        assert len(tiles) == 2
        assert tiles[-1] == (0.0, 896.0, 1024.0, 1792.0)

    def test_wide_page_cuts_a_two_dimensional_grid(self):
        # 2000x2000 with tile 1024 overlap 128 -> step 896 -> 3 cols x 3 rows
        # (edge tiles clipped to the page).
        tiles = detection_manga._tiling_tiles(2000.0, 2000.0, 1024, 128)
        assert len(tiles) == 9
        assert sorted({t[0] for t in tiles}) == [0.0, 896.0, 1792.0]
        assert sorted({t[1] for t in tiles}) == [0.0, 896.0, 1792.0]
        for (x0, y0, x1, y1) in tiles:
            assert x1 <= 2000.0 and y1 <= 2000.0

    def test_tiles_cover_the_whole_page_height(self):
        # No uncovered gap between consecutive tiles — the property the DIAG
        # full-page y coverage (156.7..62008.9 over 62133 px) relied on.
        tiles = detection_manga._tiling_tiles(690.0, 5000.0, 1024, 128)
        assert max(t[3] for t in tiles) == 5000.0
        previous_y1 = 0.0
        for (_x0, y0, _x1, y1) in tiles:
            assert y0 <= previous_y1
            previous_y1 = y1


class TestGreedyNms:
    """Confidence-ordered greedy NMS — the DIAG dedup semantics (IoU > t
    drops, IoU == t is kept), as a pure importable function."""

    def test_iou_exactly_at_threshold_is_kept(self):
        # A=(0,0,10,60) and B=(0,20,10,80): intersection 10x40=400, union
        # 600+600-400=800 -> IoU exactly 0.5. At threshold 0.5 both survive.
        boxes = [(0.0, 0.0, 10.0, 60.0, 0.9), (0.0, 20.0, 10.0, 80.0, 0.8)]
        assert detection_manga._iou(boxes[0], boxes[1]) == pytest.approx(0.5)
        kept = detection_manga._greedy_nms(boxes, 0.5)
        assert len(kept) == 2

    def test_iou_above_threshold_drops_the_lower_confidence(self):
        boxes = [(0.0, 0.0, 10.0, 60.0, 0.9), (0.0, 20.0, 10.0, 80.0, 0.8)]
        kept = detection_manga._greedy_nms(boxes, 0.4999)
        assert kept == [(0.0, 0.0, 10.0, 60.0, 0.9)]

    def test_keeper_is_always_the_higher_confidence_box(self):
        # IoU 0.5 (see the exact-0.5 geometry above) with a 0.4 threshold:
        # the drop decision must remove the LOWER-confidence box.
        boxes = [(0.0, 0.0, 10.0, 60.0, 0.7), (0.0, 20.0, 10.0, 80.0, 0.95)]
        kept = detection_manga._greedy_nms(boxes, 0.4)
        assert kept == [(0.0, 20.0, 10.0, 80.0, 0.95)]

    def test_disjoint_boxes_are_never_dropped(self):
        boxes = [
            (0.0, 0.0, 10.0, 20.0, 0.9),
            (100.0, 200.0, 110.0, 220.0, 0.8),
        ]
        assert len(detection_manga._greedy_nms(boxes, 0.0)) == 2

    def test_empty_and_single(self):
        assert detection_manga._greedy_nms([], 0.5) == []
        assert len(detection_manga._greedy_nms([(1.0, 1.0, 2.0, 2.0, 0.5)], 0.5)) == 1


def _stub_tile_inference(per_tile_outputs):
    """A ``_tile_inference`` stand-in yielding one preset payload per tile.

    Each payload is ``(scores, labels, boxes)`` in PADDED tile-local pixels —
    the raw post_process output, before text filtering (the production
    ``_text_boxes_from_results`` still runs per tile inside the tiled path).
    """
    outputs = iter(per_tile_outputs)
    calls = []

    def stub(model, processor, tile_rgb, threshold):
        calls.append(tuple(tile_rgb.shape))
        return next(outputs)

    stub.calls = calls
    return stub


class TestTiledDetectionPath:
    """The tiled orchestration with a stubbed per-tile inference: remap,
    cross-tile NMS dedup, clipping and bubble accounting — no torch.

    Fixture geometry: page 50x400 (h/w = 8, triggers), tile 100 overlap 20
    -> step 80 -> tile origins y = 0, 80, 160, 240, 320 (5 tiles).
    """

    PAGE_W, PAGE_H = 50, 400

    def _run_tiled(self, monkeypatch, per_tile_outputs, config=None, threshold=None):
        pytest.importorskip("numpy", reason="numpy is not installed")
        numpy = pytest.importorskip("numpy")
        _clean_tiling_env(monkeypatch)
        if config is None:
            config = detection_manga.TilingConfig(4.0, 100, 20, 0.5)
        stub = _stub_tile_inference(per_tile_outputs)
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._tile_inference", stub
        )
        rgb = numpy.zeros((self.PAGE_H, self.PAGE_W, 3), dtype=numpy.uint8)
        kwargs = {}
        if threshold is not None:
            kwargs["threshold"] = threshold
        boxes, n_bubble = detection_manga._detect_text_boxes_tiled(
            model=object(),
            processor=object(),
            rgb=rgb,
            width=float(self.PAGE_W),
            height=float(self.PAGE_H),
            config=config,
            **kwargs,
        )
        return boxes, n_bubble, stub

    def test_tiles_are_padded_to_the_square_tile_size(self, monkeypatch):
        # every tile handed to inference is tile_size x tile_size x 3 — the
        # 50-wide page is right/bottom-padded with the constant gray, like
        # the DIAG experiment's square-input assumption.
        _boxes, _n_bubble, stub = self._run_tiled(monkeypatch, [([], [], [])] * 5)
        assert len(stub.calls) == 5
        for shape in stub.calls:
            assert shape == (100, 100, 3)

    def test_boxes_are_remapped_to_page_coordinates(self, monkeypatch):
        # Tile 1 has origin y=80; its local box (5,10,45,30) must land at
        # page (5,90,45,110).
        boxes, n_bubble, _ = self._run_tiled(
            monkeypatch,
            [([], [], [])] + [([0.9], [1], [[5.0, 10.0, 45.0, 30.0]])] + [([], [], [])] * 3,
        )
        assert boxes == [(5.0, 90.0, 45.0, 110.0, pytest.approx(0.9))]
        assert n_bubble == 0

    def test_cross_tile_duplicate_is_deduped_to_the_higher_confidence(self, monkeypatch):
        # The DIAG textbook duplicate: the same balloon detected once per
        # tile in the overlap band. The balloon spans page y 78..98 — fully
        # inside tile 0 (crops 0..100, so no clip: local (5,78,45,98)) and
        # clipped at tile 1's top (origin 80, crops 80..180: local
        # (5,-2,..) clips to 0 -> page (5,80,45,98)). IoU = (40x18) /
        # (2x(40x20)-720) = 720/880 = 0.818 > 0.5 -> the 0.90 one drops.
        boxes, _, _ = self._run_tiled(
            monkeypatch,
            [
                ([0.95], [1], [[5.0, 78.0, 45.0, 98.0]]),
                ([0.90], [1], [[5.0, 0.0, 45.0, 18.0]]),
                ([], [], []),
                ([], [], []),
                ([], [], []),
            ],
        )
        assert boxes == [(5.0, 78.0, 45.0, 98.0, pytest.approx(0.95))]

    def test_distinct_boxes_from_different_tiles_all_survive(self, monkeypatch):
        boxes, _, _ = self._run_tiled(
            monkeypatch,
            [
                ([0.9], [1], [[5.0, 10.0, 45.0, 30.0]]),    # page y 10..30
                ([0.8], [1], [[5.0, 50.0, 45.0, 70.0]]),    # page y 130..150
                ([], [], []),
                ([], [], []),
                ([], [], []),
            ],
        )
        assert len(boxes) == 2
        assert sorted(b[1] for b in boxes) == [pytest.approx(10.0), pytest.approx(130.0)]

    def test_tile_boxes_are_clipped_to_the_tile_bounds(self, monkeypatch):
        # Tile 0 crops 50x100; a box hanging below the tile edge (local
        # y0=90, y1=130) is clipped to the tile bound before remapping —
        # page y 90..100, never past the cropped region.
        boxes, _, _ = self._run_tiled(
            monkeypatch,
            [([0.9], [1], [[5.0, 90.0, 45.0, 130.0]])] + [([], [], [])] * 4,
        )
        assert boxes == [(5.0, 90.0, 45.0, 100.0, pytest.approx(0.9))]

    def test_bubble_count_accumulates_across_tiles(self, monkeypatch):
        # Tile 0: 1 text + 1 bubble; tile 1: 5 texts + 3 bubbles — but all
        # five tile-1 texts are the SAME page box (identical after remap),
        # so the cross-tile NMS keeps one. Bubble counting is untouched by
        # the NMS: 1 + 3 = 4 across tiles.
        boxes, n_bubble, _ = self._run_tiled(
            monkeypatch,
            [
                ([0.9, 0.85], [1, 0], [[5.0, 10.0, 45.0, 30.0], [5.0, 40.0, 45.0, 60.0]]),
                ([0.8, 0.7, 0.6, 0.5, 0.4], [1, 1, 0, 0, 0], [[5.0, 10.0, 45.0, 30.0]] * 5),
                ([], [], []),
                ([], [], []),
                ([], [], []),
            ],
        )
        assert n_bubble == 4
        assert len(boxes) == 2

    def test_production_text_filter_runs_per_tile(self, monkeypatch):
        # The tiled path shares the exact pure filter: a NaN geometry is the
        # typed invalid output, never coerced (DSH r1 R9 semantics).
        from ports.providers.errors import ProviderInvalidOutput

        with pytest.raises(ProviderInvalidOutput, match="not finite"):
            self._run_tiled(
                monkeypatch,
                [([0.9], [1], [[float("nan"), 10.0, 45.0, 30.0]])],
            )

    def test_threshold_is_passed_through_to_tile_inference(self, monkeypatch):
        # The qualification's second curve point (conf 0.4) reuses the same
        # code with a lower threshold — the default stays the production 0.5.
        pytest.importorskip("numpy")
        _clean_tiling_env(monkeypatch)
        seen = []
        numpy = pytest.importorskip("numpy")

        def spy(model, processor, tile_rgb, threshold):
            seen.append(threshold)
            return ([], [], [])

        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._tile_inference", spy
        )
        rgb = numpy.zeros((400, 50, 3), dtype=numpy.uint8)
        detection_manga._detect_text_boxes_tiled(
            object(), object(), rgb, 50.0, 400.0, detection_manga.TilingConfig(4.0, 100, 20, 0.5)
        )
        assert seen == [detection_manga.MANGA_CONF_THRESHOLD] * 5


class TestDetectEndToEndTiled:
    """``detect`` wiring: a long-strip page enters the tiled path, and the
    frozen production merge consumes the deduped page-space boxes."""

    def test_long_strip_page_flows_through_merge_with_tiling_provenance(
        self, monkeypatch
    ):
        pytest.importorskip("numpy", reason="numpy is not installed")
        _clean_tiling_env(monkeypatch)
        monkeypatch.setenv("NEWMANGA_DETECTOR_TILING_TILE_SIZE", "100")
        monkeypatch.setenv("NEWMANGA_DETECTOR_TILING_OVERLAP", "20")

        def forbidden_untiled(*args, **kwargs):
            raise AssertionError("long-strip page must not enter the untiled path")

        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes",
            forbidden_untiled,
        )
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._tile_inference",
            _stub_tile_inference(
                [([0.9], [1], [[5.0, 10.0, 45.0, 30.0]])] + [([], [], [])] * 4
            ),
        )
        provider = _provider()
        provider._engine = (object(), object())
        result = provider.detect(
            _request(_frame_bytes(50, 400), width=50, height=400)  # h/w = 8
        )
        options = dict(result.options)
        assert options["tiling"] == "on"
        assert int(options["tiling_tiles"]) == 5  # origins 0,80,160,240,320
        assert options["conf_threshold"] == "0.5"  # production default unchanged
        assert options["text_boxes_pre_merge"] == "1"
        # the single box went through the frozen production merge (pad grown
        # by MERGE_PAD_PX, then clipped to the page: x0 = 5-6 < 0 -> 0)
        assert len(result.candidates) == 1
        polygon = result.candidates[0].polygon
        assert min(x for x, _ in polygon) == pytest.approx(0.0)
        assert min(y for _x, y in polygon) == pytest.approx(
            10.0 - detection_doctr.MERGE_PAD_PX
        )

    def test_normal_page_records_tiling_off(self, monkeypatch):
        pytest.importorskip("numpy", reason="numpy is not installed")
        _clean_tiling_env(monkeypatch)
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes",
            lambda model, processor, rgb, w, h: ([(10.0, 10.0, 40.0, 30.0, 0.9)], 0),
        )
        provider = _provider()
        provider._engine = (object(), object())
        result = provider.detect(_request(_frame_bytes(100, 100), width=100, height=100))
        assert dict(result.options)["tiling"] == "off"
        assert dict(result.options)["text_boxes_pre_merge"] == "1"


class TestNormalPagePathUnchanged:
    """Ordinary pages must take the byte-identical untiled path."""

    def test_normal_page_never_enters_the_tiled_branch(self, monkeypatch):
        pytest.importorskip("numpy", reason="numpy is not installed")
        _clean_tiling_env(monkeypatch)

        untiled_calls = []

        def fake_untiled(model, processor, rgb, w, h):
            untiled_calls.append((w, h))
            return [(10.0, 10.0, 40.0, 30.0, 0.9)], 0

        def forbidden_tiled(*args, **kwargs):
            raise AssertionError("normal page must not enter the tiled path")

        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes", fake_untiled
        )
        monkeypatch.setattr(
            "infrastructure.providers.detection_manga._detect_text_boxes_tiled",
            forbidden_tiled,
        )
        provider = _provider()
        provider._engine = (object(), object())
        # BJ02 proportions scaled 100x: 2946x4167 -> h/w = 1.41.
        result = provider.detect(_request(_frame_bytes(30, 42), width=30, height=42))
        assert untiled_calls == [(30.0, 42.0)]
        assert dict(result.options)["tiling"] == "off"

    def test_missing_weights_fails_closed_before_tiling(self, tmp_path: Path):
        # The fail-closed order is untouched: a long-strip page without a
        # weights directory still gets the typed PROVIDER_NOT_CONFIGURED —
        # tiling never bypasses the engine gate.
        provider = _provider(weights_dir=tmp_path / "absent")
        request = _request(_frame_bytes(50, 400), width=50, height=400)
        with pytest.raises(ProviderNotConfigured, match="weights are not installed"):
            provider.detect(request)


# ---------------------------------------------------------------------------
# identity
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
    # contract break. Full hex, no prefix — a partial match must not count
    # as a pin assertion (DSH r1 R3).
    assert (
        MANGA_MODEL_SHA256
        == "037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d"
    )
    assert (
        MANGA_CONFIG_SHA256
        == "b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072"
    )
    assert (
        MANGA_PREPROCESSOR_SHA256
        == "7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca"
    )


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
            # M2-SFX-PROD-1: the production assembly (SFX on, the default)
            # wraps the selected primary in the sfx parallel composite; the
            # backend-selection semantics this file pins live on the PRIMARY,
            # so unwrap the composite when present.
            return getattr(detector, "primary", detector)

    raise AssertionError("detect handler does not expose a wired detector")


@pytest.fixture()
def _clean_detector_env(monkeypatch):
    monkeypatch.delenv("NEWMANGA_DETECTOR_BACKEND", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
    monkeypatch.delenv("NEWMANGA_DETECTOR_DEVICE", raising=False)


class TestAssemblyBackendSelection:
    def test_default_backend_is_manga(self, tmp_path: Path, _clean_detector_env):
        # CORE-SLIM-2: the default manga backend is the ONNX Runtime detector
        # (the torch/transformers class is the optional fallback, see
        # test_torch_backend_switch_keeps_the_optional_fallback below).
        from infrastructure.providers.detection_manga_onnx import (
            MANGA_ONNX_FILENAME,
            MangaDetectionOnnxProvider,
        )

        core = _assemble(tmp_path / "data-root")
        try:
            detector = _wired_detector(core)
            assert isinstance(detector, MangaDetectionOnnxProvider)
            assert detector.provider_id == "local-manga"
            assert detector.weights_path == (
                tmp_path / "data-root" / "models" / "detector" / MANGA_ONNX_FILENAME
            )
            # DML-first EP policy by default (falls back to CPU when the wheel
            # exposes no DirectML provider).
            assert detector.device == "auto"
        finally:
            core.conn.close()

    def test_torch_backend_switch_keeps_the_optional_fallback(
        self, tmp_path: Path, monkeypatch
    ):
        """CORE-SLIM-2: the released torch path stays selectable (optional)."""
        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "torch")
        monkeypatch.delenv("NEWMANGA_DETECTOR_WEIGHTS", raising=False)
        from infrastructure.providers.detection_manga import MANGA_WEIGHTS_DIRNAME

        core = _assemble(tmp_path / "data-root")
        try:
            detector = _wired_detector(core)
            assert isinstance(detector, MangaDetectionProvider)
            assert detector.provider_id == "local-manga"
            assert detector.weights_dir == (
                tmp_path / "data-root" / "models" / "detector" / MANGA_WEIGHTS_DIRNAME
            )
            assert detector.device == "cpu"  # released torch default unchanged
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
        from infrastructure.providers.detection_manga_onnx import (
            MangaDetectionOnnxProvider,
        )

        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "manga")
        override = tmp_path / "manga-snapshot"
        override.mkdir()
        monkeypatch.setenv("NEWMANGA_DETECTOR_WEIGHTS", str(override))
        core = _assemble(tmp_path / "data-root")
        try:
            detector = _wired_detector(core)
            # The ONNX provider accepts the released directory-style override
            # and resolves the pinned ONNX file inside it at load time.
            assert isinstance(detector, MangaDetectionOnnxProvider)
            assert detector.weights_path == override
        finally:
            core.conn.close()

    def test_torch_weights_override_stays_backend_specific(
        self, tmp_path: Path, monkeypatch
    ):
        monkeypatch.setenv("NEWMANGA_DETECTOR_BACKEND", "torch")
        override = tmp_path / "torch-snapshot"
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
