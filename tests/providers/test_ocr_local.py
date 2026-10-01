"""PaddleKoreanOcrProvider PaddleOCR 3.x adaptation (M2-OCR-PADDLE3X-1).

Red-green unit tests for the two production defects evidenced in
M2-TA3-B phase 1, plus the AC1 mechanism diagnosis:

- input side: the adapter used to hand ``image_bytes`` to ``engine.ocr``
  verbatim; paddleocr 3.x silently IGNORES bytes input (diagnosed
  ALWAYS_EMPTY on two different regions —
  ``verification/M2-OCR-PADDLE3X-1/diagnosis.json``: engine logs "Not
  supported input data type ... ignored" and returns an empty list, no
  exception). The adapter now decodes the crop to a BGR ndarray first and
  the tests assert the engine never sees bytes;
- output side: ``_parse_paddle_output`` only accepted the 2.x legacy
  ``[[ [box, (text, score)], ... ]]`` nesting and raised
  ``ProviderInvalidOutput`` on the 3.x ``rec_texts/rec_scores/rec_polys``
  payload; it now accepts BOTH shapes, materialising numpy boxes to plain
  Python point lists first (DSH r2 N6: numpy arrays are not
  ``collections.abc.Sequence`` and were silently dropped to ``()``);
- engine construction: the default path passes ``enable_mkldnn=False``
  (paddlepaddle 3.3.1 Windows CPU PIR/oneDNN executor bug); the
  ``engine_factory`` injection mechanism is untouched, but the
  injected-engine input contract changed to a BGR ndarray (handoff risk
  ①: the TA3-B2 runner wrapper needs a one-line ndarray pass-through
  adaptation after this merges);
- typed failures stay closed: missing paddle runtime ->
  ``PROVIDER_DEPENDENCY_MISSING``; undecodable crop -> ``INVALID_INPUT``;
  unrecognised payload shapes -> ``PROVIDER_INVALID_OUTPUT``.

No test here needs a real paddle runtime — engines are fakes and the
paddleocr module is stubbed where the default construction is exercised.
The real-engine end-to-end run lives in
``experiments/M2-OCR-PADDLE3X-1`` (isolated venv, evidence under
``verification/M2-OCR-PADDLE3X-1``).
"""

from __future__ import annotations

import importlib.util
from types import SimpleNamespace
from typing import Any

import cv2
import numpy as np
import pytest

from infrastructure.providers import ocr_local
from infrastructure.providers.ocr_local import (
    PROVIDER_PADDLE_KOREAN,
    PaddleKoreanOcrProvider,
    _parse_paddle_output,
)
from ports.ocr.ports import (
    SCRIPT_KOREAN,
    TEXT_DIRECTION_HORIZONTAL,
    OcrRequest,
)
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderInputError,
    ProviderInvalidOutput,
)


def _request(image_bytes: bytes) -> OcrRequest:
    return OcrRequest(
        region_id="r-1",
        page_id="page-1",
        image_bytes=image_bytes,
        width=12,
        height=8,
        script=SCRIPT_KOREAN,
        direction=TEXT_DIRECTION_HORIZONTAL,
    )


def _png_bytes(width: int = 12, height: int = 8) -> bytes:
    ok, encoded = cv2.imencode(".png", np.zeros((height, width, 3), dtype=np.uint8))
    assert ok
    return encoded.tobytes()


def _stub_paddleocr_module(
    monkeypatch: pytest.MonkeyPatch, default_calls: list[dict] | None = None
) -> None:
    """Stand in for the paddleocr module on a paddle-free venv.

    The adapter probes the dependency even on the ``engine_factory`` path
    (pre-fix order, kept), so every provider-level test stubs the module
    import; ``default_calls`` records default-constructor kwargs when given.
    """
    real_import = importlib.import_module

    class PaddleOCR:
        def __init__(self, **kwargs: Any) -> None:
            if default_calls is not None:
                default_calls.append(kwargs)

    def fake_import(module_name: str, *args: Any, **kwargs: Any) -> Any:
        if module_name == "paddleocr":
            return SimpleNamespace(PaddleOCR=PaddleOCR)
        return real_import(module_name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import)


class _RecordingEngine:
    """Engine double that records what it was actually handed."""

    def __init__(self, raw: Any) -> None:
        self.raw = raw
        self.seen: Any = None
        self.calls = 0

    def ocr(self, data: Any) -> Any:
        self.calls += 1
        self.seen = data
        return self.raw


def _paddle3x_page(
    rec_texts: list[str],
    rec_scores: list[float],
    *,
    polys: Any = None,
    boxes: Any = None,
    as_object: bool = False,
) -> Any:
    """Forge one 3.x result page: dict payload or result object with .json."""
    body: dict[str, Any] = {"rec_texts": rec_texts, "rec_scores": rec_scores}
    if polys is not None:
        body["rec_polys"] = polys
    if boxes is not None:
        body["rec_boxes"] = boxes
    payload: dict[str, Any] = {"res": body, "input_path": None}
    if as_object:
        return SimpleNamespace(json=payload)
    return payload


_POLY_4PT = np.array([[[10.0, 10.0], [50.0, 10.0], [50.0, 30.0], [10.0, 30.0]]])


# ----------------------------------------------------------------------
# AC4 output side: 3.x rec_* payload parsing (red before the fix)
# ----------------------------------------------------------------------


def test_parse_accepts_paddle3x_dict_payload_with_numpy_polys() -> None:
    raw = [_paddle3x_page(["안녕"], [0.97], polys=_POLY_4PT)]
    lines = _parse_paddle_output(raw, PROVIDER_PADDLE_KOREAN)
    assert len(lines) == 1
    line = lines[0]
    assert line.text == "안녕"
    assert line.confidence == pytest.approx(0.97)
    # numpy boxes must be materialised, never silently dropped to ()
    assert line.polygon == ((10.0, 10.0), (50.0, 10.0), (50.0, 30.0), (10.0, 30.0))


def test_parse_accepts_paddle3x_result_object_payload() -> None:
    raw = [_paddle3x_page(["당근아?"], [0.99], polys=_POLY_4PT, as_object=True)]
    lines = _parse_paddle_output(raw, PROVIDER_PADDLE_KOREAN)
    assert [line.text for line in lines] == ["당근아?"]
    assert lines[0].polygon


def test_parse_accepts_paddle3x_rec_boxes_xyxy() -> None:
    boxes = np.array([[10.0, 10.0, 50.0, 30.0]])
    lines = _parse_paddle_output(
        [_paddle3x_page(["사각"], [0.9], boxes=boxes)], PROVIDER_PADDLE_KOREAN
    )
    assert lines[0].text == "사각"
    # xyxy rectangle is mapped onto the equivalent 4-point polygon
    assert lines[0].polygon == ((10.0, 10.0), (50.0, 10.0), (50.0, 30.0), (10.0, 30.0))


def test_parse_paddle3x_missing_or_short_scores_yield_none_confidence() -> None:
    # scores shorter than texts: never invent a confidence
    raw = [_paddle3x_page(["첫", "둘"], [0.5], polys=_POLY_4PT)]
    lines = _parse_paddle_output(raw, PROVIDER_PADDLE_KOREAN)
    assert [line.confidence for line in lines] == [pytest.approx(0.5), None]
    # scores key absent entirely
    body = {"rec_texts": ["셋"], "rec_polys": _POLY_4PT}
    lines = _parse_paddle_output([{"res": body}], PROVIDER_PADDLE_KOREAN)
    assert [line.confidence for line in lines] == [None]


def test_parse_paddle3x_no_text_lines_yields_empty_tuple() -> None:
    empty_body = {"res": {"rec_texts": [], "rec_scores": [], "rec_polys": _POLY_4PT[:0]}}
    assert _parse_paddle_output([empty_body], PROVIDER_PADDLE_KOREAN) == ()
    # engines may also hand back [None] for an image with no text
    assert _parse_paddle_output([None], PROVIDER_PADDLE_KOREAN) == ()


def test_parse_paddle3x_ndarray_texts_and_scores_do_not_crash() -> None:
    """DSH r1 R3: len>1 ndarray texts/scores must not hit truth-value ambiguity."""
    body = {
        "res": {
            "rec_texts": np.array(["당근", "당근!"]),
            "rec_scores": np.array([0.9, 0.8]),
            "rec_polys": np.repeat(_POLY_4PT, 2, axis=0),
        }
    }
    lines = _parse_paddle_output([body], PROVIDER_PADDLE_KOREAN)
    assert [line.text for line in lines] == ["당근", "당근!"]
    assert [line.confidence for line in lines] == [pytest.approx(0.9), pytest.approx(0.8)]


def test_parse_paddle3x_dict_shaped_polys_missing_index_stays_none() -> None:
    """DSH r1 R3: dict-shaped polys must not leak a bare KeyError from _box_at."""
    body = {
        "res": {
            "rec_texts": ["당근"],
            "rec_scores": [0.9],
            "rec_polys": {"0": [[10.0, 10.0], [50.0, 10.0], [50.0, 30.0], [10.0, 30.0]]},
        }
    }
    lines = _parse_paddle_output([body], PROVIDER_PADDLE_KOREAN)
    assert len(lines) == 1
    assert lines[0].text == "당근"
    # box lookup misses on the string key -> empty polygon, never a crash
    assert lines[0].polygon == ()


def test_parse_still_accepts_legacy_2x_shape() -> None:
    legacy = [
        [
            [
                [[10.0, 10.0], [50.0, 10.0], [50.0, 30.0], [10.0, 30.0]],
                ("텍스트", 0.9),
            ]
        ]
    ]
    lines = _parse_paddle_output(legacy, PROVIDER_PADDLE_KOREAN)
    assert len(lines) == 1
    assert lines[0].text == "텍스트"
    assert lines[0].confidence == pytest.approx(0.9)
    assert len(lines[0].polygon) == 4


def test_parse_rejects_unrecognised_dict_payload() -> None:
    with pytest.raises(ProviderInvalidOutput):
        _parse_paddle_output([{"foo": "bar"}], PROVIDER_PADDLE_KOREAN)


def test_parse_rejects_non_string_3x_text() -> None:
    raw = [_paddle3x_page([42], [0.9], polys=_POLY_4PT)]
    with pytest.raises(ProviderInvalidOutput):
        _parse_paddle_output(raw, PROVIDER_PADDLE_KOREAN)


def test_parse_rejects_top_level_non_sequence() -> None:
    with pytest.raises(ProviderInvalidOutput):
        _parse_paddle_output("not-a-list", PROVIDER_PADDLE_KOREAN)
    with pytest.raises(ProviderInvalidOutput):
        _parse_paddle_output(42, PROVIDER_PADDLE_KOREAN)


# ----------------------------------------------------------------------
# AC4 input side: bytes are decoded before the engine sees them (red
# before the fix — the engine used to receive the raw bytes object)
# ----------------------------------------------------------------------


def test_engine_receives_ndarray_not_bytes(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_paddleocr_module(monkeypatch)
    engine = _RecordingEngine(
        [_paddle3x_page(["안녕"], [0.97], polys=_POLY_4PT)]
    )
    provider = PaddleKoreanOcrProvider(engine_factory=lambda: engine)
    result = provider.recognize(_request(_png_bytes(width=12, height=8)))
    assert engine.calls == 1
    assert isinstance(engine.seen, np.ndarray), (
        "the crop must reach the engine as an ndarray — paddleocr 3.x "
        "silently ignores bytes (ALWAYS_EMPTY diagnosis)"
    )
    assert engine.seen.shape == (8, 12, 3)
    assert engine.seen.dtype == np.uint8
    assert result.lines[0].text == "안녕"
    assert result.lines[0].polygon


def test_undecodable_bytes_fail_typed(monkeypatch: pytest.MonkeyPatch) -> None:
    _stub_paddleocr_module(monkeypatch)
    engine = _RecordingEngine([])
    provider = PaddleKoreanOcrProvider(engine_factory=lambda: engine)
    with pytest.raises(ProviderInputError) as excinfo:
        provider.recognize(_request(b"this is not an image"))
    assert excinfo.value.error_code == "INVALID_INPUT"
    assert excinfo.value.provider_id == PROVIDER_PADDLE_KOREAN
    assert engine.calls == 0  # never reached the engine


def test_empty_bytes_still_fail_typed() -> None:
    provider = PaddleKoreanOcrProvider(engine_factory=lambda: _RecordingEngine([]))
    with pytest.raises(ProviderInputError):
        provider.recognize(_request(b""))


# ----------------------------------------------------------------------
# AC4 engine construction: default path pins enable_mkldnn=False
# ----------------------------------------------------------------------


def test_default_engine_constructed_with_mkldnn_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict] = []

    class PaddleOCR:
        def __init__(self, **kwargs: Any) -> None:
            calls.append(kwargs)

        def ocr(self, data: Any) -> Any:
            return []

    fake_module = SimpleNamespace(PaddleOCR=PaddleOCR)

    def fake_lazy_import(module_name: str) -> Any:
        if module_name == "paddleocr":
            return fake_module
        return importlib.import_module(module_name)

    monkeypatch.setattr(ocr_local, "_lazy_import", fake_lazy_import)
    provider = PaddleKoreanOcrProvider()
    provider.recognize(_request(_png_bytes()))
    assert len(calls) == 1
    assert calls[0]["lang"] == "korean"
    assert calls[0]["enable_mkldnn"] is False, (
        "paddlepaddle 3.3.1 Windows CPU crashes on the default MKLDNN path "
        "(PIR/oneDNN ConvertPirAttribute2RuntimeAttribute)"
    )


def test_engine_factory_injection_path_still_wins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TA3-B2 runner wrapper keeps working: an injected factory is used as-is.

    The default construction is only a fallback — with a factory present the
    ``PaddleOCR`` class is never instantiated (the lazy import still probes
    paddleocr first, mirroring the pre-fix dependency-probe order).
    """
    default_calls: list[dict] = []

    class PaddleOCR:
        def __init__(self, **kwargs: Any) -> None:
            default_calls.append(kwargs)

    fake_module = SimpleNamespace(PaddleOCR=PaddleOCR)
    real_import = importlib.import_module

    def fake_import(module_name: str, *args: Any, **kwargs: Any) -> Any:
        if module_name == "paddleocr":
            return fake_module
        return real_import(module_name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    engine = _RecordingEngine(
        [_paddle3x_page(["주입"], [0.8], polys=_POLY_4PT)]
    )
    provider = PaddleKoreanOcrProvider(engine_factory=lambda: engine)
    result = provider.recognize(_request(_png_bytes()))
    assert result.lines[0].text == "주입"
    assert default_calls == []  # the injected engine won


# ----------------------------------------------------------------------
# AC4 typed dependency-missing discipline (no paddle needed)
# ----------------------------------------------------------------------


def test_missing_paddle_runtime_fails_typed(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = importlib.import_module

    def missing_paddleocr(module_name: str, *args: Any, **kwargs: Any) -> Any:
        if module_name == "paddleocr":
            raise ImportError(f"No module named {module_name!r}")
        return real_import(module_name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", missing_paddleocr)
    provider = PaddleKoreanOcrProvider()
    with pytest.raises(ProviderDependencyMissing) as excinfo:
        provider.recognize(_request(_png_bytes()))
    assert excinfo.value.error_code == "PROVIDER_DEPENDENCY_MISSING"
    assert excinfo.value.stage == "ocr"


def test_missing_opencv_runtime_fails_typed(monkeypatch: pytest.MonkeyPatch) -> None:
    """cv2/numpy decode deps surface as typed dependency failures, not crashes."""
    real_import = importlib.import_module

    def missing_cv2(module_name: str, *args: Any, **kwargs: Any) -> Any:
        if module_name == "cv2":
            raise ImportError(f"No module named {module_name!r}")
        return real_import(module_name, *args, **kwargs)

    monkeypatch.setattr(importlib, "import_module", missing_cv2)
    provider = PaddleKoreanOcrProvider(engine_factory=lambda: _RecordingEngine([]))
    with pytest.raises(ProviderDependencyMissing):
        provider.recognize(_request(_png_bytes()))


@pytest.mark.skipif(
    importlib.util.find_spec("paddleocr") is not None,
    reason="the main test baseline must not depend on paddle; run this "
    "assertion where paddleocr is genuinely absent (e.g. the T1.1.1 venv)",
)
def test_paddle_absent_environment_reports_missing_dependency() -> None:
    """Real-environment probe: no stubs — the absent runtime is reported typed."""
    provider = PaddleKoreanOcrProvider()
    with pytest.raises(ProviderDependencyMissing) as excinfo:
        provider.recognize(_request(_png_bytes()))
    assert excinfo.value.error_code == "PROVIDER_DEPENDENCY_MISSING"
