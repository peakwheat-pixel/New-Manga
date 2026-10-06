"""Standalone SFX detection provider tests (M2-SFX-PROD-1 AC1/AC5).

Matrix:

- fail-closed: missing weights = typed ``PROVIDER_NOT_CONFIGURED``; sha256
  mismatch = typed ``PROVIDER_FAILED`` — the hash gate runs BEFORE any
  onnxruntime import, so the mismatch test works on a junk file alone;
- inference caliber over a FAKE session (the provider's ``_engine`` slot is
  injectable, no weights needed): sfx-class-only filter, conf threshold,
  class-agnostic NMS competition (a higher-scoring non-sfx box suppresses an
  overlapping sfx box — the eval-script filter order, load-bearing),
  /scale coordinate mapping, anonymous ``sfx-<n>`` labels, zero-candidate
  page, NaN geometry + out-of-range confidence typed rejections, rgb32/rgb24
  input faces;
- engine build gate: ONNX metadata ``names`` drift fails loudly (R8
  discipline, exercised through a stubbed onnxruntime module + a stubbed
  hash), imgsz comes from the metadata, session-build failures are typed;
- the parallel composite: primary provenance verbatim, sfx appended past the
  primary reading-order max, TYPED sfx failure degrades with audit-visible
  options, non-typed exceptions propagate.

REAL-weights tests run only when the pinned ONNX exists on this machine
(gitignored task-envs tree, never committed) and assert the eval payload
numbers (K07_R123, the highest-confidence sfx frame of the M2-SFX-DETECT-EVAL
sample) are reproduced by the production provider.
"""

from __future__ import annotations

import io
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.providers import detection_sfx as dsfx
from infrastructure.providers.detection_sfx import (
    SFX_CLASS_MAP,
    SFX_DEFAULT_IMGSZ,
    SFX_LABEL_PREFIX,
    SFX_TILE_HEIGHT,
    SFX_TILE_NMS_IOU,
    SFX_TILE_OVERLAP,
    SFX_TILE_ROUTE_MAX_PAGE_W,
    SFX_TILE_ROUTE_MIN_ASPECT,
    SFX_WEIGHTS_SHA256,
    MangaSfxParallelDetectionProvider,
    SfxDetectionProvider,
    _assert_tile_caliber,
    _parse_imgsz,
    _parse_names_metadata,
    _routes_to_tile,
    _tile_config,
    _tile_page_nms,
    _tile_ys,
)
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Real pinned weights (gitignored task-envs tree). M2-SFX-T4-SWITCH moved the
#: production pin to v2b (sha 944e8114…) — the real-weights anchor file moves
#: with the pin; the chiqui7 file at weights/yolo11s-seg.onnx is the rollback
#: weights and is refused by the SHA gate under the new pin (by design).
REAL_WEIGHTS = Path(
    "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights-v2b/yolo11s-seg.onnx"
)
#: The M2-SFX-DETECT-EVAL frame with the highest-confidence sfx detection in
#: both eras (K07_R123). Expected values come from the v2b anchor JSON
#: (M2-SFX-T4-SWITCH, conf 0.9047); the chiqui7-era anchor
#: (experiments/M2-SFX-DETECT/onnx-sfx-frames.json, conf 0.9313) stays on disk
#: as eval history but no longer matches the production pin.
REAL_FRAME = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
)
V2B_ANCHOR = (
    REPO_ROOT / "experiments" / "M2-SFX-T4-SWITCH" / "v2b-k07-r123-anchor.json"
)
REAL_SKIP = pytest.mark.skipif(
    not REAL_WEIGHTS.is_file() or not REAL_FRAME.is_file(),
    reason="real v2b weights / eval frame not present on this machine",
)

PAGE_W, PAGE_H = 1000, 2000
#: letterbox scale for a 1000x2000 page at imgsz 1024 (top-left paste).
SCALE = 1024 / PAGE_H


def _rgb24_bytes(width: int = PAGE_W, height: int = PAGE_H, fill: int = 255) -> bytes:
    image = Image.new("RGB", (width, height), (fill, fill, fill))
    return image.tobytes()


def _request(
    rgb: bytes | None = None, width: int = PAGE_W, height: int = PAGE_H
) -> DetectionRequest:
    return DetectionRequest(
        page_id="page-1",
        image_bytes=rgb if rgb is not None else _rgb24_bytes(width, height),
        width=width,
        height=height,
    )


def _fake_session(rows: list[tuple[tuple[float, float, float, float], list[float]]]):
    """A fake onnxruntime session emitting the eval output0 shape (1, 40, N).

    Each row is (xywh, cls_scores[4]) — exactly what ``_sfx_boxes`` unpacks.
    """
    n = len(rows)
    out = np.zeros((1, 40, n), dtype=np.float32)
    for i, (xywh, cls_scores) in enumerate(rows):
        out[0, :4, i] = xywh
        out[0, 4:8, i] = cls_scores

    class _FakeSession:
        def run(self, _, feeds):  # noqa: ANN001 - test double
            assert set(feeds) == {"images"}
            return (out,)

    return _FakeSession()


def _provider_with_engine(rows, conf_threshold: float = 0.5) -> SfxDetectionProvider:
    provider = SfxDetectionProvider(weights_path=Path("unused.onnx"), conf_threshold=conf_threshold)
    # Engine tuple = (session, imgsz, imgsz_source, imgsz_raw, ep_provenance) —
    # DSH r1 R4's two-state provenance and M2-SFX-GPU-EP-1's EP provenance
    # ride the engine to the detect options.
    provider._engine = (
        _fake_session(rows),
        SFX_DEFAULT_IMGSZ,
        "metadata_parsed",
        "[1024, 1024]",
        dsfx._EpProvenance(requested="dml", effective="dml"),
    )
    return provider


def _labels(result: DetectionResult) -> list[str]:
    return [candidate.provider_label for candidate in result.candidates]


# ---------------------------------------------------------------------------
# fail-closed (weights resolution + supply chain)
# ---------------------------------------------------------------------------


def test_missing_weights_fail_closed_typed(tmp_path):
    provider = SfxDetectionProvider(weights_path=tmp_path / "nope.onnx")
    with pytest.raises(ProviderNotConfigured) as excinfo:
        provider.detect(_request())
    message = str(excinfo.value)
    assert "never downloaded" in message
    assert "NEWMANGA_SFX_WEIGHTS" in message
    assert "NEWMANGA_SFX_DETECTION=off" in message


def test_hash_mismatch_fails_before_any_runtime_import(tmp_path):
    junk = tmp_path / "yolo11s-seg.onnx"
    junk.write_bytes(b"definitely not an onnx model")
    provider = SfxDetectionProvider(weights_path=junk)
    # The sha256 gate runs before the onnxruntime import by design, so this
    # typed failure is independent of the runtime being installed.
    with pytest.raises(ProviderError) as excinfo:
        provider.detect(_request())
    message = str(excinfo.value)
    assert "sha256" in message and SFX_WEIGHTS_SHA256[:12] in message


def test_input_gate_rejects_empty_and_mismatched_buffers():
    provider = SfxDetectionProvider(weights_path=Path("unused.onnx"))
    with pytest.raises(ProviderInputError):
        provider.detect(DetectionRequest(page_id="p", image_bytes=b"", width=2, height=2))
    with pytest.raises(ProviderInputError):
        provider.detect(
            DetectionRequest(page_id="p", image_bytes=b"12345", width=2, height=2)
        )


def test_conf_threshold_default_frozen_and_range_gated():
    assert SfxDetectionProvider(weights_path=Path("x.onnx")).conf_threshold == 0.5
    with pytest.raises(ValueError):
        SfxDetectionProvider(weights_path=Path("x.onnx"), conf_threshold=0.0)
    with pytest.raises(ValueError):
        SfxDetectionProvider(weights_path=Path("x.onnx"), conf_threshold=1.5)


# ---------------------------------------------------------------------------
# inference caliber (fake session — the eval-script path, no weights)
# ---------------------------------------------------------------------------


def test_sfx_class_only_filter_and_anonymous_labels():
    # One sfx box (0.9) + one bubble box (0.85) + one text box (0.99), all
    # spatially disjoint — only the sfx class may become a candidate.
    rows = [
        ((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.90, 0.00]),
        ((768.0, 256.0, 51.2, 102.4), [0.85, 0.05, 0.05, 0.05]),
        ((256.0, 768.0, 51.2, 102.4), [0.05, 0.05, 0.05, 0.99]),
    ]
    result = _provider_with_engine(rows).detect(_request())
    assert _labels(result) == ["sfx-1"]
    candidate = result.candidates[0]
    # xywh center (256, 256) size 51.2x102.4 -> letterbox xyxy
    # (230.4, 204.8, 281.6, 307.2) -> /SCALE == (450, 400, 550, 600).
    assert len(candidate.polygon) == 4
    xs = [point[0] for point in candidate.polygon]
    ys = [point[1] for point in candidate.polygon]
    assert min(xs) == pytest.approx(450.0, abs=1e-3)
    assert max(xs) == pytest.approx(550.0, abs=1e-3)
    assert min(ys) == pytest.approx(400.0, abs=1e-3)
    assert max(ys) == pytest.approx(600.0, abs=1e-3)
    assert candidate.confidence == pytest.approx(0.90, abs=1e-3)
    assert candidate.reading_order == 1
    assert result.coordinate_space == "page-global"
    assert result.provider_id == "local-sfx"


def test_rgb32_bgra_input_face_matches_rgb24():
    rows = [((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.90, 0.00])]
    rgb24 = np.asarray(Image.new("RGB", (PAGE_W, PAGE_H), "white"), dtype=np.uint8)
    bgra = np.dstack(
        [rgb24[:, :, ::-1], np.full((PAGE_H, PAGE_W, 1), 255, dtype=np.uint8)]
    )
    expected = _provider_with_engine(rows).detect(_request(_rgb24_bytes()))
    actual = _provider_with_engine(rows).detect(
        _request(bgra.tobytes(), PAGE_W, PAGE_H)
    )
    assert [c.provider_label for c in actual.candidates] == [
        c.provider_label for c in expected.candidates
    ]
    for got, want in zip(actual.candidates, expected.candidates):
        for got_point, want_point in zip(got.polygon, want.polygon):
            assert got_point == pytest.approx(want_point, abs=1e-3)


def test_class_agnostic_nms_suppresses_sfx_behind_higher_non_sfx_box():
    # A bubble box (0.95) overlapping the sfx box (0.9) with IoU ~ 0.96:
    # class-aware NMS would keep BOTH; the eval caliber (class-agnostic,
    # all classes compete) suppresses the sfx box -> zero candidates. The
    # filter order (conf filter -> NMS -> class filter) is load-bearing.
    overlapping = (256.0, 256.0, 51.2, 102.4)
    rows = [
        (overlapping, [0.05, 0.05, 0.90, 0.00]),
        (overlapping, [0.95, 0.00, 0.00, 0.00]),
    ]
    result = _provider_with_engine(rows).detect(_request())
    assert result.candidates == ()


def test_below_threshold_boxes_neither_surface_nor_compete():
    # sfx 0.49 (below the frozen 0.5) + a disjoint bubble 0.6: the sfx box
    # must not surface even though NMS would not suppress it anyway.
    rows = [
        ((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.49, 0.00]),
        ((768.0, 768.0, 51.2, 102.4), [0.60, 0.00, 0.00, 0.00]),
    ]
    result = _provider_with_engine(rows).detect(_request())
    assert result.candidates == ()
    # And at an env-style lowered threshold the same page yields the sfx box.
    lowered = _provider_with_engine(rows, conf_threshold=0.25)
    assert _labels(lowered.detect(_request())) == ["sfx-1"]


def test_empty_page_yields_zero_candidates():
    rows = [
        ((256.0, 256.0, 51.2, 102.4), [0.01, 0.01, 0.01, 0.01]),
        ((768.0, 768.0, 51.2, 102.4), [0.0, 0.0, 0.0, 0.0]),
    ]
    result = _provider_with_engine(rows).detect(_request())
    assert result.candidates == ()
    assert result.page_id == "page-1"
    assert result.options and dict(result.options)["class_filter"] == "sfx"


def test_nan_geometry_is_typed_invalid_output():
    rows = [((float("nan"), 256.0, 51.2, 102.4), [0.05, 0.05, 0.90, 0.00])]
    with pytest.raises(ProviderInvalidOutput, match="not finite"):
        _provider_with_engine(rows).detect(_request())


def test_confidence_out_of_range_is_typed_invalid_output():
    rows = [((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 1.20, 0.00])]
    with pytest.raises(ProviderInvalidOutput, match="out of range"):
        _provider_with_engine(rows).detect(_request())


# ---------------------------------------------------------------------------
# engine build gate (stubbed onnxruntime + stubbed hash — no weights needed)
# ---------------------------------------------------------------------------


def _install_fake_onnxruntime(monkeypatch, metadata: dict, session=None):
    calls = {"built": 0}

    class _FakeMeta:
        custom_metadata_map = metadata

    class _FakeSession:
        def __init__(self, path, providers=None):  # noqa: ANN001
            calls["built"] += 1
            calls["path"] = path
            calls["providers"] = providers
            if session is not None:
                self._delegate = session

        def get_modelmeta(self):
            return _FakeMeta()

        # P1-1 (DSH r1): the production _build_engine reads the effective EP
        # back off the session via get_providers() (the wrapper's CPU
        # fallback makes the constructor return NORMALLY on a DML failure,
        # so the read-back is the only authoritative signal). This stub
        # models the NORMAL shape: the built session runs exactly the
        # providers that were requested.
        def get_providers(self):
            return list(calls["providers"] or [])

        def run(self, _, feeds):  # noqa: ANN001
            return self._delegate.run(_, feeds)

    fake = types.ModuleType("onnxruntime")
    fake.InferenceSession = _FakeSession  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "onnxruntime", fake)
    return calls


def test_engine_names_drift_fails_loudly(tmp_path, monkeypatch):
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    drifted = dict(SFX_CLASS_MAP)
    drifted[2], drifted[3] = drifted[3], drifted[2]  # sfx/text swapped
    metadata = {
        "names": ", ".join(f"'{k}': '{v}'" for k, v in drifted.items()),
        "imgsz": "1024",
    }
    _install_fake_onnxruntime(monkeypatch, metadata)
    provider = SfxDetectionProvider(weights_path=junk)
    with pytest.raises(ProviderInvalidOutput, match="drift"):
        provider.detect(_request())


def test_engine_imgsz_comes_from_metadata(tmp_path, monkeypatch):
    """The REAL metadata shape is a stringified JSON list — ``"[1024, 1024]"``
    (Ultralytics export, `experiments/M2-SFX-DETECT/onnx-sfx-frames.json`) —
    and it must parse to its primary value with the two-state provenance
    ``imgsz_source=metadata_parsed`` (DSH r1 R4: the previous int-only parse
    silently fell back on every real export)."""
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    metadata = {
        "names": ", ".join(f"'{k}': '{v}'" for k, v in SFX_CLASS_MAP.items()),
        "imgsz": "[1024, 1024]",
    }
    # A session whose run returns an all-zero output0 (no detections).
    zeros = np.zeros((1, 40, 4), dtype=np.float32)

    class _ZeroSession:
        def get_modelmeta(self):  # noqa: ANN202
            class _Meta:
                custom_metadata_map = metadata

            return _Meta()

        def run(self, _, feeds):  # noqa: ANN001
            return (zeros,)

    _install_fake_onnxruntime(monkeypatch, metadata, session=_ZeroSession())
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    options = dict(result.options)
    assert options["imgsz"] == "1024"
    assert options["imgsz_source"] == "metadata_parsed"
    assert result.candidates == ()


def test_engine_imgsz_unparseable_falls_back_with_options_record(
    tmp_path, monkeypatch
):
    """An unparseable metadata imgsz falls back to the eval's 1024 AND the
    detect options carry the two-state provenance (``imgsz_source=fallback``)
    plus the raw metadata text, so the degradation is audit-visible instead
    of indistinguishable from a metadata-driven 1024 (DSH r1 R4)."""
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    metadata = {
        "names": ", ".join(f"'{k}': '{v}'" for k, v in SFX_CLASS_MAP.items()),
        "imgsz": "not-a-size",
    }
    zeros = np.zeros((1, 40, 4), dtype=np.float32)

    class _ZeroSession:
        def get_modelmeta(self):  # noqa: ANN202
            class _Meta:
                custom_metadata_map = metadata

            return _Meta()

        def run(self, _, feeds):  # noqa: ANN001
            return (zeros,)

    _install_fake_onnxruntime(monkeypatch, metadata, session=_ZeroSession())
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    options = dict(result.options)
    assert options["imgsz"] == str(SFX_DEFAULT_IMGSZ)
    assert options["imgsz_source"] == "fallback"
    assert options["imgsz_metadata_raw"] == "not-a-size"
    assert result.candidates == ()


def test_engine_session_failure_is_typed(tmp_path, monkeypatch):
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )

    class _BrokenSession:
        def __init__(self, path, providers=None):  # noqa: ANN001
            raise RuntimeError("boom")

    _install_fake_onnxruntime(monkeypatch, {}, session=None)
    # Replace InferenceSession with the broken constructor.
    sys.modules["onnxruntime"].InferenceSession = _BrokenSession
    provider = SfxDetectionProvider(weights_path=junk)
    with pytest.raises(ProviderError, match="failed to load"):
        provider.detect(_request())


def test_parse_names_metadata_matrix():
    assert _parse_names_metadata("{0: 'bubble', 1: 'panel', 2: 'sfx', 3: 'text'}") == {
        "0": "bubble",
        "1": "panel",
        "2": "sfx",
        "3": "text",
    }
    with pytest.raises(ProviderInvalidOutput):
        _parse_names_metadata("")
    with pytest.raises(ProviderInvalidOutput):
        _parse_names_metadata("garbage without a colon")


def test_parse_imgsz_matrix():
    """Two-state provenance (DSH r1 R4): a parseable plain int OR the real
    stringified-JSON-list shape yields (value, metadata_parsed); anything
    absent/unparseable yields the frozen default with source=fallback."""
    assert _parse_imgsz(None) == (SFX_DEFAULT_IMGSZ, "fallback")
    assert _parse_imgsz("") == (SFX_DEFAULT_IMGSZ, "fallback")
    assert _parse_imgsz("bogus") == (SFX_DEFAULT_IMGSZ, "fallback")
    assert _parse_imgsz("not-a-size") == (SFX_DEFAULT_IMGSZ, "fallback")
    assert _parse_imgsz("[not, numbers]") == (SFX_DEFAULT_IMGSZ, "fallback")
    assert _parse_imgsz("768") == (768, "metadata_parsed")
    # The REAL chiqui7 export shape (stringified JSON list, primary value).
    assert _parse_imgsz("[1024, 1024]") == (1024, "metadata_parsed")
    assert _parse_imgsz(" [1024,1024] ") == (1024, "metadata_parsed")


# ---------------------------------------------------------------------------
# parallel composite (assembly form)
# ---------------------------------------------------------------------------


class _FakeProvider:
    def __init__(self, candidates, error: Exception | None = None):
        self.candidates = candidates
        self.error = error
        self.provider_id = "local-manga"
        self.provider_type = "local-manga"
        self.model = "manga/fake"

    def detect(self, request):  # noqa: ANN001
        if self.error is not None:
            raise self.error
        return DetectionResult(
            page_id=request.page_id,
            candidates=tuple(self.candidates),
            coordinate_space="page-global",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            options=(("device", "cpu"),),
            elapsed_ms=10,
        )


def _sfx_candidates():
    return [
        RegionCandidate(
            polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)),
            reading_order=1,
            confidence=0.93,
            provider_label="sfx-1",
        ),
        RegionCandidate(
            polygon=((20.0, 0.0), (30.0, 0.0), (30.0, 10.0), (20.0, 10.0)),
            reading_order=2,
            confidence=0.55,
            provider_label="sfx-2",
        ),
    ]


def test_composite_appends_sfx_past_primary_reading_order_max():
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=((0.0, 0.0), (5.0, 0.0), (5.0, 5.0)),
                reading_order=1,
                provider_label="manga-1",
            ),
            RegionCandidate(
                polygon=((6.0, 0.0), (9.0, 0.0), (9.0, 5.0)),
                reading_order=2,
                provider_label="manga-2",
            ),
        ]
    )
    sfx = SfxDetectionProvider(weights_path=Path("x.onnx"))
    composite = MangaSfxParallelDetectionProvider(primary=primary, sfx=sfx)
    # Inject a fake engine so no weights are touched (engine tuple = session,
    # imgsz, imgsz_source, imgsz_raw, ep_provenance — DSH r1 R4's provenance
    # form + M2-SFX-GPU-EP-1's EP provenance).
    sfx._engine = (
        _fake_session(
            [((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.93, 0.00])]
        ),
        SFX_DEFAULT_IMGSZ,
        "metadata_parsed",
        "[1024, 1024]",
        dsfx._EpProvenance(requested="dml", effective="dml"),
    )
    result = composite.detect(_request())
    assert [c.provider_label for c in result.candidates] == [
        "manga-1",
        "manga-2",
        "sfx-1",
    ]
    assert [c.reading_order for c in result.candidates] == [1, 2, 3]
    assert result.provider_id == "local-manga"  # primary identity verbatim
    assert result.model == "manga/fake"
    options = dict(result.options)
    assert options["sfx_provider"] == "local-sfx"
    assert options["sfx_candidates"] == "1"
    assert options["sfx_conf_threshold"] == "0.5"
    # Composite timing covers BOTH detects (primary reported 10 ms).
    assert result.elapsed_ms is not None and result.elapsed_ms >= 10


def test_composite_typed_sfx_failure_degrades_safely(capsys):
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=((0.0, 0.0), (5.0, 0.0), (5.0, 5.0)),
                reading_order=1,
                provider_label="manga-1",
            )
        ]
    )
    broken = SfxDetectionProvider(weights_path=Path("x.onnx"))
    composite = MangaSfxParallelDetectionProvider(primary=primary, sfx=broken)
    result = composite.detect(_request())
    assert [c.provider_label for c in result.candidates] == ["manga-1"]
    options = dict(result.options)
    assert options["sfx_provider_status"] == "degraded: PROVIDER_NOT_CONFIGURED"
    stderr = capsys.readouterr().err
    assert "sfx detection degraded" in stderr


def test_composite_propagates_non_typed_errors():
    primary = _FakeProvider([])
    broken = _FakeProvider([], error=RuntimeError("programming bug"))
    composite = MangaSfxParallelDetectionProvider(primary=primary, sfx=broken)
    with pytest.raises(RuntimeError, match="programming bug"):
        composite.detect(_request())


# ---------------------------------------------------------------------------
# overlap arbitration (M2-REGION-OVERLAP-ARBITRATION)
#
# The composite is the ONE place both provider candidate sets coexist, so the
# arbitrated relabel lives here (AC1 placement): an sfx-provider candidate
# near-duplicating a primary candidate (bbox IoU >= the frozen threshold)
# flips that primary candidate's label to the ``sfx-arb-`` prefix — which the
# assembly's ``_detected_region_type`` startswith("sfx-") contract already
# dispatches to RegionType.SFX, so the SfxPolicy gate (default SKIP) takes
# over. Threshold evidence (AC1 calibration over the committed raw):
#   - BJ06 in-domain worst case (the '！！！' double-detection pair,
#     qual-BJ06 speech 5b76a907 x sfx 2eeaa2c4) IoU = 0.8862 — MUST stay
#     untouched (AC3 zero-change), so the frozen default sits ABOVE it;
#   - BJ13 misroute shape IoU 0.490-0.550 (region caliber) / 0.452-0.544
#     (E2E diagnosis caliber) — BELOW the frozen domain, i.e. NOT reachable
#     until sfx recall is restored (registered honestly, never fabricated).
# ---------------------------------------------------------------------------


def _rect(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1))


class _FakeSfxProvider:
    """A stand-in sfx provider emitting the given candidates (no engine)."""

    def __init__(self, candidates):
        self.candidates = candidates
        self.provider_id = "local-sfx"
        self.provider_type = "local-sfx"
        self.model = "sfx/fake"
        self.conf_threshold = 0.5

    def detect(self, request):  # noqa: ANN001
        return DetectionResult(
            page_id=request.page_id,
            candidates=tuple(self.candidates),
            coordinate_space="page-global",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            options=(("conf_threshold", "0.5"),),
            elapsed_ms=5,
        )


def test_arbitration_relabels_near_duplicate_primary_candidate(monkeypatch):
    """AC2 green semantics: a primary candidate near-duplicated by an sfx
    candidate (IoU >= threshold) is relabeled into the SFX gate; a
    non-overlapping primary candidate is untouched."""
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION", raising=False)
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION_IOU", raising=False)
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 10.0),
                reading_order=1,
                confidence=0.9,
                provider_label="manga-1",
            ),
            RegionCandidate(
                polygon=_rect(50.0, 0.0, 60.0, 10.0),
                reading_order=2,
                confidence=0.8,
                provider_label="manga-2",
            ),
        ]
    )
    sfx = _FakeSfxProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 10.0),  # IoU 1.0 with manga-1
                reading_order=1,
                confidence=0.93,
                provider_label="sfx-1",
            )
        ]
    )
    result = MangaSfxParallelDetectionProvider(
        primary=primary, sfx=sfx
    ).detect(_request())
    labels = [c.provider_label for c in result.candidates]
    assert labels == ["sfx-arb-manga-1", "manga-2", "sfx-1"]
    # The relabel flips ONLY the label: geometry, order, confidence verbatim
    # (the region creator consumes the same polygon either way).
    arb = result.candidates[0]
    assert arb.polygon == _rect(0.0, 0.0, 10.0, 10.0)
    assert arb.reading_order == 1
    assert arb.confidence == 0.9
    options = dict(result.options)
    assert options["sfx_arbitration"] == "on"
    assert options["sfx_arbitration_relabels"] == "1"


def test_arbitration_partial_overlap_below_threshold_is_diagnosed_not_applied(
    monkeypatch,
):
    """The BJ13 misroute shape (IoU ~0.55): below the frozen conservative
    domain the relabel must NOT fire, and the near-miss overlap is recorded
    as a typed diagnostic (AC4 — the arbitration-unreachable face)."""
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION", raising=False)
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION_IOU", raising=False)
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 20.0),  # area 200
                reading_order=1,
                confidence=0.744,
                provider_label="manga-1",
            )
        ]
    )
    sfx = _FakeSfxProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 11.0),  # area 110, inside
                reading_order=1,
                confidence=0.93,
                provider_label="sfx-1",
            )
        ]
    )
    result = MangaSfxParallelDetectionProvider(
        primary=primary, sfx=sfx
    ).detect(_request())
    # IoU = 110/200 = 0.55 < 0.9 -> untouched, diagnosed. (result.candidates
    # carries the appended sfx candidate after the primary slice.)
    assert [c.provider_label for c in result.candidates] == ["manga-1", "sfx-1"]
    options = dict(result.options)
    assert "sfx_arbitration_relabels" not in options
    assert options["sfx_arbitration_partial_overlap"] == "0.5500"


def test_arbitration_bj06_in_domain_worst_pair_stays_untouched(monkeypatch):
    """AC3 anchor, replicating the committed BJ06 numbers: the worst
    in-domain sfx x speech pair (qual-BJ06 sfx 2eeaa2c4 bbox (1534,3517,
    223,395) x speech 5b76a907 bbox (1540,3500,222,425)) has IoU 0.8862 —
    the frozen default 0.9 sits above every in-domain pair, so the domain
    run is bit-identical (the '！！！' dialogue region is NOT relabeled)."""
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION", raising=False)
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION_IOU", raising=False)
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(1540.0, 3500.0, 1762.0, 3925.0),
                reading_order=9,
                confidence=0.9,
                provider_label="manga-9",
            )
        ]
    )
    sfx = _FakeSfxProvider(
        [
            RegionCandidate(
                polygon=_rect(1534.0, 3517.0, 1757.0, 3912.0),
                reading_order=1,
                confidence=0.93,
                provider_label="sfx-1",
            )
        ]
    )
    result = MangaSfxParallelDetectionProvider(
        primary=primary, sfx=sfx
    ).detect(_request())
    assert [c.provider_label for c in result.candidates] == ["manga-9", "sfx-1"]
    options = dict(result.options)
    assert options["sfx_arbitration_partial_overlap"] == "0.8862"
    assert "sfx_arbitration_relabels" not in options


def test_arbitration_env_off_disables_the_semantics(monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_ARBITRATION", "off")
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 10.0),
                reading_order=1,
                confidence=0.9,
                provider_label="manga-1",
            )
        ]
    )
    sfx = _FakeSfxProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 10.0),
                reading_order=1,
                confidence=0.93,
                provider_label="sfx-1",
            )
        ]
    )
    result = MangaSfxParallelDetectionProvider(
        primary=primary, sfx=sfx
    ).detect(_request())
    assert [c.provider_label for c in result.candidates] == ["manga-1", "sfx-1"]
    assert dict(result.options)["sfx_arbitration"] == "off"


def test_arbitration_env_threshold_override_expands_the_domain(monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_ARBITRATION_IOU", "0.3")
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 20.0),
                reading_order=1,
                confidence=0.744,
                provider_label="manga-1",
            )
        ]
    )
    sfx = _FakeSfxProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 11.0),  # IoU 0.55 >= 0.3
                reading_order=1,
                confidence=0.93,
                provider_label="sfx-1",
            )
        ]
    )
    result = MangaSfxParallelDetectionProvider(
        primary=primary, sfx=sfx
    ).detect(_request())
    assert [c.provider_label for c in result.candidates] == [
        "sfx-arb-manga-1",
        "sfx-1",
    ]
    options = dict(result.options)
    assert options["sfx_arbitration_threshold"] == "0.3"
    assert options["sfx_arbitration_relabels"] == "1"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("NEWMANGA_SFX_ARBITRATION", ""),
        ("NEWMANGA_SFX_ARBITRATION", "auto"),
        ("NEWMANGA_SFX_ARBITRATION_IOU", ""),
        ("NEWMANGA_SFX_ARBITRATION_IOU", "abc"),
        ("NEWMANGA_SFX_ARBITRATION_IOU", "0"),
        ("NEWMANGA_SFX_ARBITRATION_IOU", "1.5"),
        ("NEWMANGA_SFX_ARBITRATION_IOU", "-0.1"),
    ],
)
def test_arbitration_env_illegal_value_fails_fast_before_any_detect(
    monkeypatch, name, value
):
    """AC4, the TILING discipline: an empty or illegal arbitration env is a
    fail-fast ValueError naming the variable — raised BEFORE the primary
    runs, never a silent default (an illegal config must not produce a
    half-detected page)."""
    sentinel_primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 1.0, 1.0),
                reading_order=1,
                provider_label="manga-1",
            )
        ]
    )
    composite = MangaSfxParallelDetectionProvider(
        primary=sentinel_primary, sfx=_FakeSfxProvider([])
    )
    monkeypatch.setenv(name, value)
    with pytest.raises(ValueError, match=name):
        composite.detect(_request())
    # The sentinel primary produced no detect call: its fake detect would
    # have appended candidates/options regardless of the env — the typed
    # rejection happens before any inference (asserted in depth by the
    # dedicated probe test below).


def test_arbitration_env_illegal_value_never_runs_the_primary(monkeypatch):
    """The explicit fail-fast face of the test above: the primary detect is
    not invoked at all when the arbitration env is illegal."""
    calls = []

    class _ProbePrimary:
        provider_id = "local-manga"
        provider_type = "local-manga"
        model = "manga/fake"

        def detect(self, request):  # noqa: ANN001
            calls.append(request.page_id)
            raise AssertionError("primary must not run on an illegal env")

    composite = MangaSfxParallelDetectionProvider(
        primary=_ProbePrimary(), sfx=_FakeSfxProvider([])
    )
    monkeypatch.setenv("NEWMANGA_SFX_ARBITRATION_IOU", "abc")
    with pytest.raises(ValueError, match="NEWMANGA_SFX_ARBITRATION_IOU"):
        composite.detect(_request())
    assert calls == []


def test_arbitration_config_defaults_are_frozen(monkeypatch):
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION", raising=False)
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION_IOU", raising=False)
    from infrastructure.providers.detection_sfx import _arbitration_config

    assert _arbitration_config() == (True, 0.9)


def test_arbitration_degraded_sfx_provider_skips_arbitration(monkeypatch):
    """The typed-degradation path keeps its pre-arbitration shape verbatim:
    no sfx candidates -> nothing to arbitrate against, no arbitration
    options, manga candidates live on."""
    monkeypatch.delenv("NEWMANGA_SFX_ARBITRATION", raising=False)
    primary = _FakeProvider(
        [
            RegionCandidate(
                polygon=_rect(0.0, 0.0, 10.0, 10.0),
                reading_order=1,
                confidence=0.9,
                provider_label="manga-1",
            )
        ]
    )
    broken = SfxDetectionProvider(weights_path=Path("x.onnx"))
    composite = MangaSfxParallelDetectionProvider(primary=primary, sfx=broken)
    result = composite.detect(_request())
    assert [c.provider_label for c in result.candidates] == ["manga-1"]
    options = dict(result.options)
    assert options["sfx_provider_status"] == "degraded: PROVIDER_NOT_CONFIGURED"
    assert "sfx_arbitration" not in options


# ---------------------------------------------------------------------------
# real weights (conditional)
# ---------------------------------------------------------------------------


@REAL_SKIP
@pytest.mark.parametrize("rgb32", [False, True], ids=["rgb24", "rgb32"])
def test_real_weights_reproduce_eval_payload(rgb32):
    """The production provider reproduces the M2-SFX-T4-SWITCH v2b anchor on
    K07_R123 (conf 0.9047) — the pinned-weights regression anchor, end to end.
    The anchor JSON carries the weights sha it was extracted with; if the pin
    moves again, re-extract the anchor (experiments/M2-SFX-T4-SWITCH/
    extract_v2b_anchor.py) — the SHA gate makes stale weights fail closed."""
    payload = json.loads(V2B_ANCHOR.read_text(encoding="utf-8"))
    assert payload["weights_sha256"] == SFX_WEIGHTS_SHA256, (
        "v2b anchor was extracted from weights that no longer match the "
        "production pin — re-run extract_v2b_anchor.py"
    )
    expected = [
        detection
        for detection in payload["detections"]
        if detection["cls"] == "sfx" and detection["conf"] >= 0.5
    ]
    assert expected, "v2b anchor lost its K07_R123 sfx detection"

    with Image.open(REAL_FRAME) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        if rgb32:
            arr = np.asarray(rgb, dtype=np.uint8)
            bgra = np.dstack(
                [arr[:, :, ::-1], np.full((height, width, 1), 255, dtype=np.uint8)]
            )
            frame_bytes = bgra.tobytes()
        else:
            frame_bytes = rgb.tobytes()

    provider = SfxDetectionProvider(weights_path=REAL_WEIGHTS)
    result = provider.detect(_request(frame_bytes, width, height))
    candidates = result.candidates
    assert candidates, "real weights produced no sfx candidates on K07_R123"
    best = max(candidates, key=lambda candidate: candidate.confidence or 0.0)
    assert best.confidence == pytest.approx(expected[0]["conf"], abs=1e-3)
    xs = [point[0] for point in best.polygon]
    ys = [point[1] for point in best.polygon]
    x0, y0, x1, y1 = expected[0]["box_xyxy"]
    assert min(xs) == pytest.approx(x0, abs=1.0)
    assert min(ys) == pytest.approx(y0, abs=1.0)
    assert max(xs) == pytest.approx(x1, abs=1.0)
    assert max(ys) == pytest.approx(y1, abs=1.0)
    assert all(0 <= x <= width and 0 <= y <= height for x, y in best.polygon)


@REAL_SKIP
def test_real_weights_blank_page_structurally_valid():
    """A blank page must run the real engine without crashing; every emitted
    candidate keeps the anonymous label/geometry contract (zero candidates is
    the expected outcome, the structure assertion is the fail-closed face)."""
    image = Image.new("RGB", (800, 1200), (255, 255, 255))
    provider = SfxDetectionProvider(weights_path=REAL_WEIGHTS)
    result = provider.detect(_request(image.tobytes(), 800, 1200))
    for candidate in result.candidates:
        assert candidate.provider_label.startswith(SFX_LABEL_PREFIX)
        assert len(candidate.polygon) == 4
        assert 0.0 <= (candidate.confidence or 0.0) <= 1.0
    assert dict(result.options)["conf_threshold"] == "0.5"


# ---------------------------------------------------------------------------
# KO long-strip tile routing (M2-SFX-T5-TILE-KO)
#
# The KO long-strip pages (600/690 px wide, aspect 1:30.7-1:145.6) sub-pixelize
# under the whole-page letterbox (zero sfx response — T3/KO-TILE structural
# fact), so the frozen tile caliber is the only KO-domain route from zero to
# sfx candidates: tile width = the native page width, tile_h 1024, step
# 1024-128=896, trailing page-bottom anchor, per-tile production sequence
# verbatim (letterbox + sfx boxes), page-level cross-tile NMS IoU 0.5
# conf-descending greedy. The production branch replicates the T3 evaluation
# tile implementation (eval_gate_t3.py run_tile / tile_calib.py) — AC3
# bit-parity with the T3 matrix (v2b 35/56+48/135, chiqui7 56/56+41/135) is
# the implementation-equivalence evidence.
# ---------------------------------------------------------------------------

_TILE_ENV_NAMES = (
    "NEWMANGA_SFX_TILE",
    "NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W",
    "NEWMANGA_SFX_TILE_ROUTE_MIN_ASPECT",
    "NEWMANGA_SFX_TILE_HEIGHT",
    "NEWMANGA_SFX_TILE_OVERLAP",
    "NEWMANGA_SFX_TILE_NMS_IOU",
)


def _tile_defaults(monkeypatch) -> None:
    for name in _TILE_ENV_NAMES:
        monkeypatch.delenv(name, raising=False)


def test_tile_constants_are_frozen():
    """The frozen caliber numbers, verbatim from the KO-TILE proposal §3
    (eval_gate_t3.py / tile_calib.py lines of record)."""
    assert SFX_TILE_HEIGHT == 1024
    assert SFX_TILE_OVERLAP == 128
    assert SFX_TILE_NMS_IOU == 0.5
    assert SFX_TILE_ROUTE_MAX_PAGE_W == 690
    assert SFX_TILE_ROUTE_MIN_ASPECT == 8.0


def test_tile_ys_frozen_caliber_matches_t3_tile_counts():
    """The anchor sequence over the four KO exam page heights reproduces the
    T3 tile counts (58/112/70/21) — the frozen caliber's geometry face."""
    assert len(_tile_ys(51971, SFX_TILE_HEIGHT, SFX_TILE_OVERLAP)) == 58
    assert len(_tile_ys(100480, SFX_TILE_HEIGHT, SFX_TILE_OVERLAP)) == 112
    assert len(_tile_ys(62133, SFX_TILE_HEIGHT, SFX_TILE_OVERLAP)) == 70
    assert len(_tile_ys(18401, SFX_TILE_HEIGHT, SFX_TILE_OVERLAP)) == 21


def test_tile_ys_step_anchors_and_bottom_coverage():
    assert _tile_ys(2048, 1024, 128) == [0, 896, 1024]  # step + trailing anchor
    assert _tile_ys(1024, 1024, 128) == [0]  # page exactly one tile
    assert _tile_ys(800, 1024, 128) == [0]  # page shorter than a tile
    assert _tile_ys(1025, 1024, 128) == [0, 1]  # 1px overflow -> bottom anchor


def test_tile_caliber_assertion_rejects_broken_geometry():
    """T4-承接 r1 P3-2 closure: the frozen caliber (step / first anchor /
    page-bottom coverage) is asserted at run time via a typed raise —
    stronger than the ``assert`` statement, never stripped under ``-O``."""
    _assert_tile_caliber([0, 896, 1024], 2048, 1024, 128)  # well-formed
    with pytest.raises(ProviderInvalidOutput, match="step"):
        _assert_tile_caliber([0, 800, 1024], 2048, 1024, 128)
    with pytest.raises(ProviderInvalidOutput, match="page bottom"):
        _assert_tile_caliber([0, 896], 2048, 1024, 128)
    with pytest.raises(ProviderInvalidOutput, match="first anchor"):
        _assert_tile_caliber([512, 1408], 2048, 1024, 128)
    with pytest.raises(ProviderInvalidOutput, match="empty"):
        _assert_tile_caliber([], 2048, 1024, 128)
    # DSH r1 P3-3: the degenerate branch (y + tile_h <= y, i.e. tile_h <= 0)
    # must also raise. It is deliberately defensive — with tile_h > 0 and the
    # first-anchor/step checks passing, no _tile_ys output can reach it — so
    # the case is synthetic; constant freezing itself is pinned by
    # test_tile_constants_are_frozen above.
    with pytest.raises(ProviderInvalidOutput, match="degenerate"):
        _assert_tile_caliber([0], 0, 0, 0)


def test_tile_config_defaults_are_frozen(monkeypatch):
    _tile_defaults(monkeypatch)
    cfg = _tile_config()
    assert cfg.enabled is True
    assert cfg.route_max_page_w == 690.0
    assert cfg.route_min_aspect == 8.0
    assert cfg.tile_h == 1024
    assert cfg.overlap == 128
    assert cfg.nms_iou == 0.5


def test_tile_route_decision_boundaries(monkeypatch):
    _tile_defaults(monkeypatch)
    cfg = _tile_config()
    assert _routes_to_tile(690, 51971, cfg)  # KO pre-k08
    assert _routes_to_tile(600, 18401, cfg)  # KO pre-k02
    assert not _routes_to_tile(691, 100000, cfg)  # width above the route cap
    assert not _routes_to_tile(690, 3000, cfg)  # aspect below the route floor
    assert _routes_to_tile(690, 5520, cfg)  # aspect == 8.0 boundary -> tile
    assert not _routes_to_tile(1100, 1600, cfg)  # ordinary page


def test_tile_env_off_routes_long_strip_page_back_to_letterbox(monkeypatch):
    """The kill switch: NEWMANGA_SFX_TILE=off restores the pre-T5 letterbox
    behavior for a page whose shape would otherwise route to tiles (600x4800
    = the aspect-8.0 route boundary)."""
    monkeypatch.setenv("NEWMANGA_SFX_TILE", "off")
    rows = [((345.0, 55.0, 200.0, 90.0), [0.05, 0.05, 0.90, 0.00])]
    result = _provider_with_engine(rows).detect(_request(width=600, height=4800))
    options = dict(result.options)
    assert options["sfx_route"] == "letterbox"
    assert "tile_count" not in options


def test_tile_env_override_expands_the_route_domain(monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W", "800")
    monkeypatch.setenv("NEWMANGA_SFX_TILE_ROUTE_MIN_ASPECT", "4.0")
    cfg = _tile_config()
    assert cfg.route_max_page_w == 800.0
    assert cfg.route_min_aspect == 4.0
    assert _routes_to_tile(800, 10000, cfg)


def test_tile_env_override_tile_geometry_records_in_options(monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_TILE_HEIGHT", "512")
    monkeypatch.setenv("NEWMANGA_SFX_TILE_OVERLAP", "64")
    monkeypatch.setenv("NEWMANGA_SFX_TILE_NMS_IOU", "0.4")
    rows = [((345.0, 55.0, 200.0, 90.0), [0.05, 0.05, 0.90, 0.00])]
    # 690x5520 routes (aspect 8.0); tile_h 512 / overlap 64 -> step 448,
    # anchors [0,448,...,4928] + trailing 5008 = 13 tiles.
    result = _provider_with_engine(rows).detect(_request(width=690, height=5520))
    options = dict(result.options)
    assert options["sfx_route"] == "tile"
    assert options["tile_h"] == "512"
    assert options["tile_overlap"] == "64"
    assert options["tile_nms_iou"] == "0.4"
    assert options["tile_count"] == "13"


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("NEWMANGA_SFX_TILE", ""),
        ("NEWMANGA_SFX_TILE", "auto"),
        ("NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W", ""),
        ("NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W", "abc"),
        ("NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W", "0"),
        ("NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W", "-5"),
        ("NEWMANGA_SFX_TILE_ROUTE_MIN_ASPECT", ""),
        ("NEWMANGA_SFX_TILE_ROUTE_MIN_ASPECT", "abc"),
        ("NEWMANGA_SFX_TILE_ROUTE_MIN_ASPECT", "0"),
        ("NEWMANGA_SFX_TILE_HEIGHT", ""),
        ("NEWMANGA_SFX_TILE_HEIGHT", "abc"),
        ("NEWMANGA_SFX_TILE_HEIGHT", "0"),
        ("NEWMANGA_SFX_TILE_OVERLAP", ""),
        ("NEWMANGA_SFX_TILE_OVERLAP", "abc"),
        ("NEWMANGA_SFX_TILE_OVERLAP", "0"),
        ("NEWMANGA_SFX_TILE_OVERLAP", "1024"),  # must stay < tile_h (step >= 1)
        ("NEWMANGA_SFX_TILE_NMS_IOU", ""),
        ("NEWMANGA_SFX_TILE_NMS_IOU", "abc"),
        ("NEWMANGA_SFX_TILE_NMS_IOU", "0"),
        ("NEWMANGA_SFX_TILE_NMS_IOU", "1.5"),
    ],
)
def test_tile_env_illegal_value_fails_fast_before_any_inference(
    monkeypatch, name, value
):
    """The TILING/ARBITRATION fail-fast discipline: an empty or illegal
    ``NEWMANGA_SFX_TILE_*`` env is a ValueError naming the variable, raised
    BEFORE the weights file is even resolved (the provider below carries a
    missing-weights path that would type PROVIDER_NOT_CONFIGURED if the env
    gate did not fire first) — never a silent default, never a half-detected
    page. (The provider below carries a missing-weights path that would type
    PROVIDER_NOT_CONFIGURED if the env gate did not fire first.)"""
    monkeypatch.setenv(name, value)
    provider = SfxDetectionProvider(weights_path=Path("missing.onnx"))
    with pytest.raises(ValueError, match=name):
        provider.detect(_request())


def test_tile_detect_translates_tiles_and_merges_page_level():
    """End-to-end tile face over a fake session: a 600x4800 page sits exactly
    on the aspect-8.0 route boundary; anchors [0, 896, 1792, 2688, 3584,
    3776], each tile runs the production letterbox+boxes sequence, the
    per-tile results are translated by +y0 into page coordinates and survive
    the page-level cross-tile NMS (the same tile-local box from different
    anchors lands on disjoint page rows here — the +y0 caliber is the
    assertion target)."""
    # Tile 600x1024 -> letterbox scale 1.0; box letterbox xyxy
    # (245,10)-(445,100), sfx conf 0.9.
    rows = [((345.0, 55.0, 200.0, 90.0), [0.05, 0.05, 0.90, 0.00])]
    result = _provider_with_engine(rows).detect(_request(width=600, height=4800))
    options = dict(result.options)
    assert options["sfx_route"] == "tile"
    assert options["tile_count"] == "6"
    assert options["tile_h"] == "1024"
    assert options["tile_overlap"] == "128"
    assert options["tile_nms_iou"] == "0.5"
    assert _labels(result) == [f"sfx-{i}" for i in range(1, 7)]
    for candidate, y0 in zip(result.candidates, (0, 896, 1792, 2688, 3584, 3776)):
        xs = [point[0] for point in candidate.polygon]
        page_ys = [point[1] for point in candidate.polygon]
        assert min(xs) == pytest.approx(245.0, abs=1e-3)
        assert max(xs) == pytest.approx(445.0, abs=1e-3)
        assert min(page_ys) == pytest.approx(10.0 + y0, abs=1e-3)
        assert max(page_ys) == pytest.approx(100.0 + y0, abs=1e-3)
        assert candidate.confidence == pytest.approx(0.90, abs=1e-3)


def test_tile_page_nms_suppresses_cross_tile_duplicates():
    """Page-level cross-tile dedup, dedup_boxes semantics verbatim: conf
    descending stable greedy, IoU >= threshold drops the newcomer, the kept
    ordering is (-conf, xyxy)."""
    boxes = [
        ([10.0, 1024.0, 100.0, 1124.0], 0.80),  # trailing-anchor tile's copy
        ([10.0, 1000.0, 100.0, 1100.0], 0.90),  # overlapping-region tile, wins
        ([500.0, 10.0, 590.0, 100.0], 0.60),  # disjoint, keeps its slot
    ]
    assert _tile_page_nms(boxes, 0.5) == [
        (10.0, 1000.0, 100.0, 1100.0, 0.90),
        (500.0, 10.0, 590.0, 100.0, 0.60),
    ]


def test_ordinary_page_routes_letterbox_verbatim():
    """An ordinary page takes the letterbox path with the candidate surface
    unchanged (the pre-T5 anchor numbers from
    test_sfx_class_only_filter_and_anonymous_labels) and the route recorded."""
    rows = [
        ((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.90, 0.00]),
        ((768.0, 256.0, 51.2, 102.4), [0.85, 0.05, 0.05, 0.05]),
        ((256.0, 768.0, 51.2, 102.4), [0.05, 0.05, 0.05, 0.99]),
    ]
    result = _provider_with_engine(rows).detect(_request())
    assert dict(result.options)["sfx_route"] == "letterbox"
    assert _labels(result) == ["sfx-1"]
    candidate = result.candidates[0]
    xs = [point[0] for point in candidate.polygon]
    ys = [point[1] for point in candidate.polygon]
    assert min(xs) == pytest.approx(450.0, abs=1e-3)
    assert max(xs) == pytest.approx(550.0, abs=1e-3)
    assert min(ys) == pytest.approx(400.0, abs=1e-3)
    assert max(ys) == pytest.approx(600.0, abs=1e-3)


# ---------------------------------------------------------------------------
# execution-provider selection (M2-SFX-GPU-EP-1)
#
# User ruling 2026-10-06: the deployment form is GPU — onnxruntime-directml
# + NEWMANGA_SFX_EP (dml|cpu, default dml; illegal value fail-fast BEFORE any
# weights resolution, the T5 env discipline). A DML init failure (no DX12
# GPU / missing driver / CPU-only wheel) falls back to the CPU EP WITH a
# visible audit key (sfx_ep_fallback in the detect options) — availability
# first, never a silent degradation; an explicit cpu request that fails is a
# typed ProviderError (fail-closed, no fallback out of an explicit request).
# All semantics are exercised through the STUBBED onnxruntime module, so the
# matrix is green on any machine regardless of its GPU; the real DML numbers
# live in the AC2/AC3 experiment evidence.
# ---------------------------------------------------------------------------


def test_ep_config_defaults_to_dml(monkeypatch):
    monkeypatch.delenv("NEWMANGA_SFX_EP", raising=False)
    assert dsfx._ep_config() == "dml"


def test_ep_config_accepts_explicit_values_case_insensitive(monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_EP", "cpu")
    assert dsfx._ep_config() == "cpu"
    monkeypatch.setenv("NEWMANGA_SFX_EP", " CPU ")
    assert dsfx._ep_config() == "cpu"
    monkeypatch.setenv("NEWMANGA_SFX_EP", "DML")
    assert dsfx._ep_config() == "dml"


def test_ep_config_illegal_value_fails_fast_before_weights_resolution(
    monkeypatch, tmp_path
):
    """The fail-fast fires BEFORE the weights file is even probed: the
    missing-weights path would raise the typed ProviderNotConfigured, so a
    ValueError here proves the EP env gate runs first (never a half-configured
    engine, the T5 env discipline)."""
    monkeypatch.setenv("NEWMANGA_SFX_EP", "cuda")
    provider = SfxDetectionProvider(weights_path=tmp_path / "missing.onnx")
    with pytest.raises(ValueError, match="NEWMANGA_SFX_EP"):
        provider.detect(_request())


def test_ep_config_empty_value_fails_fast(monkeypatch):
    monkeypatch.setenv("NEWMANGA_SFX_EP", "")
    with pytest.raises(ValueError, match="NEWMANGA_SFX_EP"):
        dsfx._ep_config()


def _ep_metadata() -> dict:
    return {
        "names": ", ".join(f"'{k}': '{v}'" for k, v in SFX_CLASS_MAP.items()),
        "imgsz": "[1024, 1024]",
    }


def _zero_run_session(metadata: dict):
    """A session whose run() returns an all-zero output0 (no detections) and
    whose metadata carries the asserted class surface."""
    zeros = np.zeros((1, 40, 2), dtype=np.float32)

    class _ZeroSession:
        def get_modelmeta(self):  # noqa: ANN202
            class _Meta:
                custom_metadata_map = metadata

            return _Meta()

        def run(self, _, feeds):  # noqa: ANN001
            return (zeros,)

    return _ZeroSession()


def test_engine_build_defaults_to_dml_provider(tmp_path, monkeypatch):
    """Env absent -> the session is built with DmlExecutionProvider (the
    user's GPU deployment ruling is the DEFAULT, not an opt-in)."""
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    calls = _install_fake_onnxruntime(
        monkeypatch, _ep_metadata(), session=_zero_run_session(_ep_metadata())
    )
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    assert calls["providers"] == ["DmlExecutionProvider"]
    options = dict(result.options)
    assert options["sfx_ep"] == "dml"
    assert options["device"] == "dml"
    assert "sfx_ep_fallback" not in options
    assert result.candidates == ()


def test_engine_build_cpu_env_requests_cpu_provider(tmp_path, monkeypatch):
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    calls = _install_fake_onnxruntime(
        monkeypatch, _ep_metadata(), session=_zero_run_session(_ep_metadata())
    )
    monkeypatch.setenv("NEWMANGA_SFX_EP", "cpu")
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    assert calls["providers"] == ["CPUExecutionProvider"]
    options = dict(result.options)
    assert options["sfx_ep"] == "cpu"
    assert options["device"] == "cpu"
    assert "sfx_ep_fallback" not in options


def _install_dml_failing_onnxruntime(monkeypatch, metadata: dict) -> dict:
    """A stub whose InferenceSession RAISES when asked for the DML provider
    (the no-DX12-GPU / missing-driver / CPU-only-wheel shape) and succeeds
    for the CPU provider — the automatic-fallback semantics' test double."""
    calls = {"providers": []}

    class _FakeMeta:
        custom_metadata_map = metadata

    class _FakeSession:
        def __init__(self, path, providers=None):  # noqa: ANN001
            calls["providers"].append(list(providers or []))
            if providers and "DmlExecutionProvider" in providers:
                raise RuntimeError("Unable to create DML device: no DX12")

        def get_modelmeta(self):
            return _FakeMeta()

        def run(self, _, feeds):  # noqa: ANN001
            return (np.zeros((1, 40, 2), dtype=np.float32),)

    fake = types.ModuleType("onnxruntime")
    fake.InferenceSession = _FakeSession  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "onnxruntime", fake)
    return calls


def test_engine_dml_failure_falls_back_to_cpu_with_audit(tmp_path, monkeypatch):
    """DML init failure (no DX12 GPU machine) -> the CPU EP session is built
    and the degradation is AUDIT-VISIBLE in the detect options: device=cpu
    (the effective EP), sfx_ep=dml (what was requested), sfx_ep_fallback
    carrying the reason. Availability first, never a silent fallback."""
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    calls = _install_dml_failing_onnxruntime(monkeypatch, _ep_metadata())
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    assert calls["providers"] == [
        ["DmlExecutionProvider"],
        ["CPUExecutionProvider"],
    ]
    options = dict(result.options)
    assert options["sfx_ep"] == "dml"
    assert options["device"] == "cpu"
    assert "DML" in options["sfx_ep_fallback"] or "dml" in options["sfx_ep_fallback"]
    assert result.candidates == ()


def test_engine_cpu_failure_is_typed_no_fallback(tmp_path, monkeypatch):
    """An EXPLICIT cpu request whose session build fails is a typed
    ProviderError — there is no "fall back" out of an explicit request."""
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )

    class _BrokenSession:
        def __init__(self, path, providers=None):  # noqa: ANN001
            raise RuntimeError("boom")

    _install_fake_onnxruntime(monkeypatch, {}, session=None)
    sys.modules["onnxruntime"].InferenceSession = _BrokenSession
    monkeypatch.setenv("NEWMANGA_SFX_EP", "cpu")
    provider = SfxDetectionProvider(weights_path=junk)
    with pytest.raises(ProviderError, match="failed to load"):
        provider.detect(_request())


def test_engine_wrapper_level_cpu_fallback_gets_three_key_audit(
    tmp_path, monkeypatch
):
    """P1-1 (DSH r1) THE REAL FAILURE SHAPE: onnxruntime's
    ``InferenceSession.__init__`` carries its own CPU fallback
    (``enable_fallback`` defaults to True in
    ``onnxruntime_inference_collection.py``) — a DML init failure (no DX12
    GPU / broken driver / CPU-only wheel) is SWALLOWED as
    (ValueError, RuntimeError), the wrapper rebuilds on
    ["CPUExecutionProvider"] and returns NORMALLY (an "EP Error" banner on
    stderr only). The constructor does NOT raise, so an exception-driven
    fallback branch never runs and there is NO second construction.

    The three-key audit (sfx_ep / device / sfx_ep_fallback) must therefore
    be driven by a get_providers() READ-BACK: requested dml + a session
    whose first provider is not DmlExecutionProvider = the wrapper-level
    fallback, audited with device=cpu (the EFFECTIVE EP) — never a silent
    wrong "dml"."""
    calls = {"providers": []}
    metadata = _ep_metadata()

    class _FakeMeta:
        custom_metadata_map = metadata

    class _WrapperFallbackSession:
        """Models the wrapper after its internal fallback: built once for
        DML, returned as a CPU-only session, never raising."""

        def __init__(self, path, providers=None):  # noqa: ANN001
            calls["providers"].append(list(providers or []))

        def get_modelmeta(self):
            return _FakeMeta()

        def get_providers(self):
            # The wrapper already fell back internally: the session's
            # effective provider list carries CPU only.
            return ["CPUExecutionProvider"]

        def run(self, _, feeds):  # noqa: ANN001
            return (np.zeros((1, 40, 2), dtype=np.float32),)

    fake = types.ModuleType("onnxruntime")
    fake.InferenceSession = _WrapperFallbackSession  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "onnxruntime", fake)
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    monkeypatch.delenv("NEWMANGA_SFX_EP", raising=False)  # default dml
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    # Exactly ONE construction: the wrapper handled the fallback internally.
    assert calls["providers"] == [["DmlExecutionProvider"]]
    options = dict(result.options)
    assert options["sfx_ep"] == "dml"
    assert options["device"] == "cpu"
    assert "dml" in options["sfx_ep_fallback"]
    assert "CPUExecutionProvider" in options["sfx_ep_fallback"]
    assert result.candidates == ()


# ---------------------------------------------------------------------------
# run-time EPFail channel audit (M2-SFX-EPFAIL-AUDIT-1)
#
# GPU-EP-1's three-key audit covers INIT only (r2 N-P3-1): the ORT wrapper's
# ``InferenceSession.run`` ALSO catches ``C.EPFail`` mid-inference, calls
# ``set_providers(self._fallback_providers)`` (a CPU list for a dml request),
# disables the fallback (it fires ONCE per session) and re-runs on CPU,
# returning NORMALLY — no exception reaches the caller, only two stdout
# ``print`` lines the frozen face drops (r2 N-P4-2, banned as a signal
# source). The observable face is the session's provider list itself: the
# public ``get_providers()`` read-back (wrapper :214-216, a pure Python
# attribute read — measured 0.03 us/call on the production wheel + v2b
# weights, negligible against the 1%-per-page latency budget) shows
# ``[Dml, CPU]`` after a dml build and ``[CPU]`` once the run-time fallback
# has fired. Every detect reads the providers back once; unchanged = steady
# state (options byte-identical to the pre-audit form), changed = the
# additive ``sfx_ep_runtime_check`` key. The three-key provenance keeps its
# ENGINE-BUILD semantics and write point verbatim.
# ---------------------------------------------------------------------------


def test_runtime_epfail_silent_rerun_gets_runtime_audit_key(
    tmp_path, monkeypatch
):
    """THE registered unaudited channel (GPU-EP-1 deploy-record §1.3, r2
    N-P3-1), now audited: the stub replays the wrapper's run-time fallback
    shape EXACTLY — a post-build DML session (read-back ``[Dml, CPU]``, the
    measured real form) whose FIRST ``run()`` flips the provider list to
    ``[CPU]`` inside the wrapper and re-runs successfully; the caller gets a
    normal result and NO exception (the silent-success shape).

    The detect options must carry the additive ``sfx_ep_runtime_check`` key
    (dml -> cpu, run-time channel) while the three-key provenance keeps its
    ENGINE-BUILD semantics verbatim: device/sfx_ep stay "dml" (the BUILD had
    no fallback) and no ``sfx_ep_fallback`` appears. A SECOND page on the
    now-CPU session still reports the runtime key — the change is session
    state, not a per-page event."""
    calls = {"providers": [], "runtime_fell_back": False}
    metadata = _ep_metadata()

    class _FakeMeta:
        custom_metadata_map = metadata

    class _RuntimeEpfailSession:
        """A real DML session as the wrapper presents it post-build, whose
        first ``run()`` triggers the wrapper-internal EPFail fallback:
        ``set_providers(['CPUExecutionProvider'])`` rewrites the provider
        list, the CPU retry succeeds, and the caller observes NOTHING (the
        wrapper's only own signal is two stdout lines the frozen face
        drops)."""

        def __init__(self, path, providers=None):  # noqa: ANN001
            calls["providers"].append(list(providers or []))
            self._providers = [
                "DmlExecutionProvider",
                "CPUExecutionProvider",
            ]

        def get_modelmeta(self):
            return _FakeMeta()

        def get_providers(self):
            return list(self._providers)

        def run(self, _, feeds):  # noqa: ANN001
            if not calls["runtime_fell_back"]:
                calls["runtime_fell_back"] = True
                self._providers = ["CPUExecutionProvider"]
            return (np.zeros((1, 40, 2), dtype=np.float32),)

    fake = types.ModuleType("onnxruntime")
    fake.InferenceSession = _RuntimeEpfailSession  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "onnxruntime", fake)
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    monkeypatch.delenv("NEWMANGA_SFX_EP", raising=False)  # default dml
    provider = SfxDetectionProvider(weights_path=junk)

    # Page 1: the run-time fallback fires mid-detect; the result flows
    # normally and the audit key reports the provider-list change.
    result = provider.detect(_request())
    options = dict(result.options)
    # The three-key provenance keeps its ENGINE-BUILD semantics verbatim.
    assert options["device"] == "dml"
    assert options["sfx_ep"] == "dml"
    assert "sfx_ep_fallback" not in options
    # The run-time channel is the additive key.
    assert options["sfx_ep_runtime_check"] == (
        "session providers changed at run time: dml -> cpu "
        "(ORT wrapper run-time EPFail fallback)"
    )
    assert result.candidates == ()

    # Page 2: the session stays on CPU (the wrapper's fallback fires ONCE);
    # the runtime key persists — session state, not a per-page event.
    again = dict(provider.detect(_request()).options)
    assert again["device"] == "dml"  # engine-build semantics, unchanged
    assert again["sfx_ep_runtime_check"] == options["sfx_ep_runtime_check"]


def test_runtime_steady_state_adds_no_runtime_key(tmp_path, monkeypatch):
    """Steady state: a session whose provider list never changes after the
    build produces detect options WITHOUT the runtime key — the audit
    surface stays byte-identical to the pre-M2-SFX-EPFAIL-AUDIT-1 form (the
    AC3 zero-change face; the full regression stays an equal count plus the
    new cases only because of this)."""
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    calls = _install_fake_onnxruntime(
        monkeypatch, _ep_metadata(), session=_zero_run_session(_ep_metadata())
    )
    monkeypatch.delenv("NEWMANGA_SFX_EP", raising=False)  # default dml
    provider = SfxDetectionProvider(weights_path=junk)
    result = provider.detect(_request())
    assert calls["providers"] == ["DmlExecutionProvider"]
    options = dict(result.options)
    assert "sfx_ep_runtime_check" not in options
    assert options["device"] == "dml"
    assert options["sfx_ep"] == "dml"
    assert "sfx_ep_fallback" not in options


def test_runtime_audit_skips_sessions_without_readback_face(tmp_path):
    """A session object without a ``get_providers`` face (a bare test double
    injected straight into the engine tuple) SKIPS the run-time check: the
    audit never becomes a new failure point, and the engine-riding three-key
    provenance is written unchanged (real ORT sessions always carry the
    face — the build gate already calls it)."""
    provider = SfxDetectionProvider(
        weights_path=Path("unused.onnx"), conf_threshold=0.5
    )
    provider._engine = (
        _fake_session([((10, 10, 20, 20), [0.1, 0.8, 0.05, 0.05])]),
        SFX_DEFAULT_IMGSZ,
        "metadata_parsed",
        "[1024, 1024]",
        dsfx._EpProvenance(requested="dml", effective="dml"),
    )
    result = provider.detect(_request())
    options = dict(result.options)
    assert "sfx_ep_runtime_check" not in options
    assert options["device"] == "dml"
    assert options["sfx_ep"] == "dml"
