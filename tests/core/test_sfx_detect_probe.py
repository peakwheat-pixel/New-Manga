"""Standalone SFX-detect probe tests (M2-PROD-SFX-PROBE-1).

The probe (``bootstrap.sfx_detect_probe``) is a one-shot frozen-process
entry: one production ``SfxDetectionProvider.detect`` + an audit JSON line.
These tests cover the probe's own contract WITHOUT real weights:

- the synthetic page contract (rgb24 byte count, deterministic, drawn);
- the weight resolution order (arg > env > frozen in-bundle probe; the dev
  form without arg/env is a config error, never a guess);
- the JSON output contract: exit 0 + three-key EP provenance on success
  (fake engine injection, no weights needed), exit 1 + typed error payload
  (``PROVIDER_NOT_CONFIGURED``) when the resolved weights are missing;
- the ``--page`` injection face (a real page file read into rgb24).

Real-weights frozen evidence itself lives in
``verification/M2-PROD-SFX-PROBE-1/`` (the packaged probe runner) — this
suite needs no onnxruntime and no weights file.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap import sfx_detect_probe as probe
from infrastructure.providers import detection_sfx as dsfx
from infrastructure.providers.detection_sfx import (
    SFX_DEFAULT_IMGSZ,
    SfxDetectionProvider,
)
from ports.detection.ports import DetectionRequest

PAGE_W, PAGE_H = 1000, 2000
JSON_MARKER = probe.JSON_MARKER


def _parse_probe_json(capsys) -> dict:
    out = capsys.readouterr().out
    lines = [line for line in out.splitlines() if line.startswith(JSON_MARKER)]
    assert lines, f"no {JSON_MARKER.strip()} line on stdout: {out[-400:]}"
    assert len(lines) == 1, "exactly ONE machine-readable JSON line expected"
    return json.loads(lines[0][len(JSON_MARKER):])


def _fake_session(rows: list[tuple[tuple[float, float, float, float], list[float]]]):
    """Same fake onnxruntime session shape as tests/providers/
    test_detection_sfx.py: output0 (1, 40, N), rows = (xywh, cls_scores[4])."""
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


def _provider_with_engine(rows) -> SfxDetectionProvider:
    provider = SfxDetectionProvider(weights_path=Path("unused.onnx"))
    provider._engine = (
        _fake_session(rows),
        SFX_DEFAULT_IMGSZ,
        "metadata_parsed",
        "[1024, 1024]",
        dsfx._EpProvenance(requested="dml", effective="dml"),
    )
    return provider


# ---------------------------------------------------------------------------
# synthetic page contract
# ---------------------------------------------------------------------------


def test_synthetic_page_rgb24_contract():
    page_bytes, width, height = probe.make_synthetic_page()
    assert (width, height) == (900, 1300)
    # the production rgb24 page_frame contract: exactly 3 bytes per pixel
    assert len(page_bytes) == width * height * 3
    # deterministic (same pixels on every call — the JSON page sha256 is
    # comparable across probe runs)
    again, w2, h2 = probe.make_synthetic_page()
    assert (again, w2, h2) == (page_bytes, width, height)
    assert hashlib.sha256(again).hexdigest() == hashlib.sha256(page_bytes).hexdigest()
    # NOT a blank page: the drawn panels/lettering produce dark pixels
    arr = np.frombuffer(page_bytes, dtype=np.uint8).reshape(height, width, 3)
    assert (arr < 128).sum() > 10_000


def test_injected_page_reads_rgb24_and_records_sha(tmp_path):
    page_path = tmp_path / "page.png"
    Image.new("RGB", (320, 240), (200, 30, 30)).save(page_path, "PNG")
    page_bytes, width, height = probe.load_injected_page(page_path)
    assert (width, height) == (320, 240)
    assert len(page_bytes) == width * height * 3
    arr = np.frombuffer(page_bytes, dtype=np.uint8).reshape(height, width, 3)
    assert arr[0, 0, 0] == 200  # RGB channel order preserved


# ---------------------------------------------------------------------------
# weight resolution (production order, probe-bounded)
# ---------------------------------------------------------------------------


def test_resolve_weights_arg_beats_env(tmp_path):
    weights = tmp_path / "arg.onnx"
    path, source = probe.resolve_weights(str(weights), "G:/env/ignored.onnx", frozen=False)
    assert (path, source) == (weights, "arg")


def test_resolve_weights_env_used_when_no_arg():
    path, source = probe.resolve_weights(None, "G:/env/from-env.onnx", frozen=False)
    assert (path, source) == (Path("G:/env/from-env.onnx"), "env")


def test_resolve_weights_empty_env_falls_through():
    # the released override contract: an EMPTY value falls through (never
    # taken as-is) — dev form (frozen=False) then has nothing left to probe,
    # so the honest config error is the outcome
    with pytest.raises(probe.ProbeConfigError):
        probe.resolve_weights(None, "   ", frozen=False)


def test_resolve_weights_dev_form_without_arg_env_is_config_error():
    with pytest.raises(probe.ProbeConfigError) as excinfo:
        probe.resolve_weights(None, None, frozen=False)
    assert "NEWMANGA_SFX_WEIGHTS" in str(excinfo.value)


def test_resolve_weights_frozen_probes_bundle(monkeypatch, tmp_path):
    fake_exe = tmp_path / "sfx_detect_probe.exe"
    monkeypatch.setattr(
        sys, "executable", str(fake_exe)
    )
    path, source = probe.resolve_weights(None, None, frozen=True)
    assert source == "bundle_probe"
    assert path == tmp_path / "models" / "detector" / "yolo11s-seg.onnx"


# ---------------------------------------------------------------------------
# probe run contract (fake engine — no weights, no onnxruntime)
# ---------------------------------------------------------------------------


SFX_ROWS = [
    # letterbox coordinates for a 1000x2000 page (scale 0.512, top-left
    # paste): the usable x range is 0-512 — both boxes stay inside it so the
    # /scale mapping lands non-degenerately on the page
    ((256.0, 256.0, 51.2, 102.4), [0.05, 0.05, 0.90, 0.00]),
    ((300.0, 768.0, 51.2, 102.4), [0.05, 0.05, 0.65, 0.00]),
]


def test_probe_success_json_carries_three_keys(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        probe, "build_provider", lambda weights_path: _provider_with_engine(SFX_ROWS)
    )
    weights = tmp_path / "yolo11s-seg.onnx"
    weights.write_bytes(b"unused (fake engine)")
    exit_code = probe.main(
        ["--weights", str(weights), "--out", str(tmp_path / "probe.json")]
    )
    assert exit_code == 0
    payload = _parse_probe_json(capsys)
    assert payload["error"] is None
    assert payload["result"]["n_candidates"] == 2
    assert payload["result"]["labels"] == ["sfx-1", "sfx-2"]
    # the three-key EP audit rides the probe JSON verbatim from the options
    assert payload["result"]["device"] == "dml"
    assert payload["result"]["sfx_ep"] == "dml"
    assert payload["result"]["sfx_ep_fallback"] is None
    assert payload["result"]["elapsed_ms"] >= 0
    assert payload["weights"]["resolved_from"] == "arg"
    assert payload["weights"]["exists"] is True
    assert payload["page"]["source"] == "builtin_synthetic"
    # the full options dict stays in the payload for the audit trail
    assert payload["result"]["options"]["conf_threshold"] == "0.5"
    # --out wrote the same payload pretty-printed
    out_payload = json.loads((tmp_path / "probe.json").read_text(encoding="utf-8"))
    assert out_payload == payload


def test_probe_missing_weights_reports_typed_not_configured(capsys, tmp_path):
    exit_code = probe.main(["--weights", str(tmp_path / "nope.onnx")])
    assert exit_code == 1
    payload = _parse_probe_json(capsys)
    assert payload["result"] is None
    assert payload["error"]["error_code"] == "PROVIDER_NOT_CONFIGURED"
    assert payload["error"]["class"] == "ProviderNotConfigured"


def test_probe_injected_page_face(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(
        probe, "build_provider", lambda weights_path: _provider_with_engine(SFX_ROWS[:1])
    )
    page_path = tmp_path / "real-page.png"
    Image.new("RGB", (640, 480), "white").save(page_path, "PNG")
    exit_code = probe.main(
        [
            "--weights",
            str(tmp_path / "unused.onnx"),
            "--page",
            str(page_path),
            "--label",
            "injected-real-page",
        ]
    )
    assert exit_code == 0
    payload = _parse_probe_json(capsys)
    assert payload["label"] == "injected-real-page"
    assert payload["page"]["source"] == "injected"
    assert (payload["page"]["width"], payload["page"]["height"]) == (640, 480)
    assert payload["result"]["n_candidates"] == 1


def test_probe_dev_form_without_weights_is_config_error(capsys, monkeypatch):
    monkeypatch.delenv("NEWMANGA_SFX_WEIGHTS", raising=False)
    exit_code = probe.main([])
    assert exit_code == 1
    payload = _parse_probe_json(capsys)
    assert payload["result"] is None
    assert payload["error"]["class"] == "ProbeConfigError"


def test_probe_detect_request_uses_production_page_frame_contract(monkeypatch, tmp_path):
    """The probe hands the provider the raw rgb24 buffer + declared size —
    the same page_frame contract the core.detect handler validates (probe
    never bypasses the provider's own input gate)."""
    seen: dict = {}

    class _RecordingProvider(SfxDetectionProvider):
        def detect(self, request: DetectionRequest):  # noqa: D102 - test double
            seen["request"] = request
            return _provider_with_engine(SFX_ROWS).detect(request)

    monkeypatch.setattr(probe, "build_provider", lambda weights_path: _RecordingProvider(weights_path=weights_path))
    weights = tmp_path / "yolo11s-seg.onnx"
    weights.write_bytes(b"unused (fake engine)")
    assert probe.main(["--weights", str(weights)]) == 0
    request = seen["request"]
    page_bytes, width, height = probe.make_synthetic_page()
    assert request.image_bytes == page_bytes
    assert (request.width, request.height) == (width, height)
