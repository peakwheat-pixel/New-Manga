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

from infrastructure.providers.detection_sfx import (
    SFX_CLASS_MAP,
    SFX_DEFAULT_IMGSZ,
    SFX_LABEL_PREFIX,
    SFX_WEIGHTS_SHA256,
    MangaSfxParallelDetectionProvider,
    SfxDetectionProvider,
    _parse_imgsz,
    _parse_names_metadata,
)
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Real pinned weights (gitignored task-envs tree).
REAL_WEIGHTS = Path(
    "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx"
)
#: The M2-SFX-DETECT-EVAL frame with the highest-confidence sfx detection
#: (K07_R123, conf 0.9313 — the payload line the real test reproduces).
REAL_FRAME = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-work/regions/K07_R123.png"
)
EVAL_PAYLOAD = (
    REPO_ROOT / "experiments" / "M2-SFX-DETECT" / "onnx-sfx-frames.json"
)
REAL_SKIP = pytest.mark.skipif(
    not REAL_WEIGHTS.is_file() or not REAL_FRAME.is_file(),
    reason="real chiqui7 weights / eval frame not present on this machine",
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
    provider._engine = (_fake_session(rows), SFX_DEFAULT_IMGSZ)
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
    junk = tmp_path / "weights.onnx"
    junk.write_bytes(b"junk")
    monkeypatch.setattr(
        "infrastructure.providers.detection_sfx.sha256_file",
        lambda _: SFX_WEIGHTS_SHA256,
    )
    metadata = {
        "names": ", ".join(f"'{k}': '{v}'" for k, v in SFX_CLASS_MAP.items()),
        "imgsz": "768",
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
    assert dict(result.options)["imgsz"] == "768"
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
    assert _parse_imgsz(None) == SFX_DEFAULT_IMGSZ
    assert _parse_imgsz("") == SFX_DEFAULT_IMGSZ
    assert _parse_imgsz("bogus") == SFX_DEFAULT_IMGSZ
    assert _parse_imgsz("768") == 768


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
    # Inject a fake engine so no weights are touched.
    sfx._engine = (
        _fake_session(
            [((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.93, 0.00])]
        ),
        SFX_DEFAULT_IMGSZ,
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
# real weights (conditional)
# ---------------------------------------------------------------------------


@REAL_SKIP
@pytest.mark.parametrize("rgb32", [False, True], ids=["rgb24", "rgb32"])
def test_real_weights_reproduce_eval_payload(rgb32):
    """The production provider reproduces the M2-SFX-DETECT-EVAL K07_R123
    sfx detection (conf 0.9313) — the eval-caliber replication, end to end."""
    payload = json.loads(EVAL_PAYLOAD.read_text(encoding="utf-8"))
    region = payload["regions"]["K07_R123"]
    expected = [
        detection
        for detection in region["chiqui7_yolo11s_seg"]["detections"]
        if detection["cls"] == "sfx" and detection["conf"] >= 0.5
    ]
    assert expected, "eval payload lost its K07_R123 sfx anchor"

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
