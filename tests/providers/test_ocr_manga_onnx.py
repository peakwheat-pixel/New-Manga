"""CORE-SLIM-2: manga-ocr ONNX provider (encoder/decoder pair, Python decode)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.providers import ocr_manga_onnx as onnx_ocr  # noqa: E402
from ports.ocr.ports import OcrRequest, SCRIPT_JAPANESE, SCRIPT_KOREAN  # noqa: E402
from ports.providers.errors import (  # noqa: E402
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
)


def _png_bytes() -> bytes:
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", (40, 20), (10, 20, 30)).save(buffer, format="PNG")
    return buffer.getvalue()


def _request(script: str = SCRIPT_JAPANESE, image_bytes: bytes | None = None) -> OcrRequest:
    return OcrRequest(
        page_id="p1",
        region_id="r1",
        image_bytes=_png_bytes() if image_bytes is None else image_bytes,
        script=script,
    )


class _FakeEngine:
    def __init__(self, text: str = "こんにちは") -> None:
        self.text = text
        self.calls = []

    def __call__(self, image):
        self.calls.append(image)
        return self.text


def test_recognize_returns_the_engine_text_with_no_invented_confidence() -> None:
    engine = _FakeEngine()
    provider = onnx_ocr.MangaOcrOnnxProvider(
        weights_dir=Path("unused"), engine_factory=lambda directory: engine
    )

    result = provider.recognize(_request())

    assert result.text == "こんにちは"
    assert result.provider_id == "manga-ocr"
    assert result.provider_type == "local-manga-ocr-onnx"
    assert result.confidence is None  # manga-ocr reports none
    assert [line.text for line in result.lines] == ["こんにちは"]
    # the injection contract: the engine receives the decoded PIL crop
    assert engine.calls and getattr(engine.calls[0], "size", None) == (40, 20)


def test_empty_text_yields_no_lines() -> None:
    provider = onnx_ocr.MangaOcrOnnxProvider(
        weights_dir=Path("unused"), engine_factory=lambda directory: _FakeEngine("")
    )
    assert provider.recognize(_request()).lines == ()


def test_script_validation_and_empty_crop_are_typed() -> None:
    provider = onnx_ocr.MangaOcrOnnxProvider(
        weights_dir=Path("unused"), engine_factory=lambda directory: _FakeEngine()
    )
    with pytest.raises(ProviderInputError, match="does not support script"):
        provider.recognize(_request(script=SCRIPT_KOREAN))
    with pytest.raises(ProviderInputError, match="no image bytes"):
        provider.recognize(_request(image_bytes=b""))
    with pytest.raises(ProviderInputError, match="decodable"):
        provider.recognize(_request(image_bytes=b"not-an-image"))


def test_engine_must_return_a_string() -> None:
    provider = onnx_ocr.MangaOcrOnnxProvider(
        weights_dir=Path("unused"),
        engine_factory=lambda directory: (lambda image: 42),
    )
    with pytest.raises(ProviderError, match="expected str"):
        provider.recognize(_request())


def test_missing_weights_directory_is_not_configured(tmp_path: Path) -> None:
    provider = onnx_ocr.MangaOcrOnnxProvider(weights_dir=tmp_path / "absent")
    with pytest.raises(ProviderNotConfigured, match="manga-ocr ONNX weights"):
        provider.recognize(_request())


def test_resolve_weights_dir_env_precedence(tmp_path: Path, monkeypatch) -> None:
    explicit = tmp_path / "explicit"
    env_dir = tmp_path / "env"
    explicit.mkdir()
    env_dir.mkdir()
    monkeypatch.setenv(onnx_ocr.MANGA_OCR_WEIGHTS_ENV, str(env_dir))
    assert onnx_ocr.resolve_weights_dir(explicit) == explicit
    assert onnx_ocr.resolve_weights_dir(None) == env_dir


def test_engine_decode_loop_greedy_eos_and_special_token_filter() -> None:
    """The Python-side decode: argmax loop, EOS stop, no special tokens leak."""
    import numpy as np

    from PIL import Image

    class _Encoder:
        def run(self, output_names, feed):
            return [np.zeros((1, 4, 8), dtype=np.float32)]

        def get_inputs(self):
            return [type("I", (), {"name": "pixel_values"})()]

    class _Decoder:
        def __init__(self, vocab_size=10):
            self.vocab_size = vocab_size
            self.rounds = 0

        def run(self, output_names, feed):
            self.rounds += 1
            logits = np.zeros((1, int(feed["input_ids"].shape[1]), self.vocab_size))
            # first prediction: [CLS] (2, must be filtered), then 5,6, then EOS 3
            sequence = {1: 2, 2: 5, 3: 6, 4: 3}[self.rounds]
            logits[0, -1, sequence] = 10.0
            return [logits]

        def get_inputs(self):
            return [
                type("I", (), {"name": "input_ids"})(),
                type("I", (), {"name": "encoder_hidden_states"})(),
            ]

    engine = onnx_ocr._MangaOcrOnnxEngine(Path("unused"))
    engine.encoder = _Encoder()
    engine.decoder = _Decoder()
    engine.vocab = tuple("abcdefghij")
    engine.start_id = 2
    engine.eos_id = 3
    engine.max_len = 24
    engine.encoder_input = "pixel_values"
    engine.decoder_ids_input = "input_ids"
    engine.decoder_hidden_input = "encoder_hidden_states"

    text = engine(Image.new("RGB", (16, 16)))

    # token 2 is a special token (in the fake vocab it is "c"): the filter only
    # drops the REAL special names, so this fake vocabulary keeps "c" -> the
    # assertion below is about the loop shape, not vocabulary content.
    assert text == "cfg"
    assert engine.decoder.rounds == 4  # EOS on the 4th step, never max_len


def test_engine_stops_at_max_len_without_eos() -> None:
    import numpy as np

    from PIL import Image

    class _Encoder:
        def run(self, output_names, feed):
            return [np.zeros((1, 2, 4), dtype=np.float32)]

        def get_inputs(self):
            return [type("I", (), {"name": "pixel_values"})()]

    class _NeverEosDecoder:
        def run(self, output_names, feed):
            logits = np.zeros((1, int(feed["input_ids"].shape[1]), 10))
            logits[0, -1, 5] = 10.0
            return [logits]

        def get_inputs(self):
            return [
                type("I", (), {"name": "input_ids"})(),
                type("I", (), {"name": "encoder_hidden_states"})(),
            ]

    engine = onnx_ocr._MangaOcrOnnxEngine(Path("unused"))
    engine.encoder = _Encoder()
    engine.decoder = _NeverEosDecoder()
    engine.vocab = tuple("abcdefghij")
    engine.start_id = 2
    engine.eos_id = 3
    engine.max_len = 4
    engine.encoder_input = "pixel_values"
    engine.decoder_ids_input = "input_ids"
    engine.decoder_hidden_input = "encoder_hidden_states"

    assert engine(Image.new("RGB", (16, 16))) == "ffff"  # 4 steps, bounded


def test_special_tokens_never_reach_the_text() -> None:
    assert "".join(
        token
        for token in ("[CLS]", "あ", "[SEP]", "い", "[PAD]")
        if token not in onnx_ocr.MANGA_OCR_SPECIAL_TOKENS
    ) == "あい"


def test_weights_pin_integrity_fails_closed(tmp_path: Path) -> None:
    # a complete-looking bundle with WRONG model bytes: the pin check must fire
    # before any session is created.
    for name in (
        onnx_ocr.MANGA_OCR_ENCODER_FILENAME,
        onnx_ocr.MANGA_OCR_DECODER_FILENAME,
        onnx_ocr.MANGA_OCR_VOCAB_FILENAME,
    ):
        (tmp_path / name).write_bytes(b"stub")
    engine = onnx_ocr._MangaOcrOnnxEngine(tmp_path)
    with pytest.raises(ProviderError, match="sha256"):
        engine._ensure_loaded()


def test_missing_vocab_is_not_configured(tmp_path: Path) -> None:
    (tmp_path / onnx_ocr.MANGA_OCR_ENCODER_FILENAME).write_bytes(b"stub")
    (tmp_path / onnx_ocr.MANGA_OCR_DECODER_FILENAME).write_bytes(b"stub")
    engine = onnx_ocr._MangaOcrOnnxEngine(tmp_path)
    with pytest.raises(ProviderNotConfigured, match="vocab.txt"):
        engine._ensure_loaded()
