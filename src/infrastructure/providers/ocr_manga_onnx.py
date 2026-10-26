"""Japanese manga OCR over ONNX Runtime (CORE-SLIM-2).

``MangaOcrProvider`` (``ocr_local.py``) drives the third-party ``manga_ocr``
package, which requires torch/transformers — the chain CORE-SLIM-2 removes from
the packaged Core closure. This module ships the SAME model as two ONNX graphs
(encoder + decoder, Apache-2.0 weights) and keeps the autoregressive decode in
Python, exactly as INFER-BASELINE-EP-1 measured: encoder/decoder ONNX produced
character-identical text to torch on 10/10 pages (charAcc 1.0).

Contract compatibility (recognition-only, one Region crop per call):

- provider id ``manga-ocr`` / script Japanese, ``needs_detection = False`` —
  the adapter never fabricates detection boxes;
- the request carries an ENCODED crop (PNG bytes); it is decoded with Pillow
  and preprocessed exactly like the torch model (224x224 BILINEAR,
  ``/255``, ``(x-0.5)/0.5`` — the checkpoint's ViTFeatureExtractor config);
- output text is built from the decoder's argmax token ids against the pinned
  ``vocab.txt`` (special tokens stripped), confidence stays ``None`` (manga-ocr
  reports none; nothing is invented);
- weights are local + SHA-256 pinned, never downloaded; a missing/invalid
  bundle is ``PROVIDER_NOT_CONFIGURED``/``PROVIDER_FAILED``;
- OCR stays on the CPU execution provider by default: the INFER baseline
  measured DML 97.87 ms vs CUDA 23.17 ms vs CPU (the GPU gain is only real for
  CUDA, which the shipped ``onnxruntime-directml`` wheel cannot offer), so a
  GPU is never assumed. ``NEWMANGA_OCR_DEVICE`` may opt in explicitly.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from infrastructure.providers.onnx_sessions import (create_session, resolve_execution_provider)
from infrastructure.providers.ocr_local import PROVIDER_MANGA_OCR
from ports.ocr.ports import (
    OcrLine,
    OcrRequest,
    OcrResult,
    SCRIPT_JAPANESE,
)
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
)

#: Weights directory layout (bundled under ``models/ocr/manga-ocr-onnx/``).
MANGA_OCR_ONNX_DIRNAME = "manga-ocr-onnx"
MANGA_OCR_ENCODER_FILENAME = "encoder_model.onnx"
MANGA_OCR_DECODER_FILENAME = "decoder_model.onnx"
MANGA_OCR_VOCAB_FILENAME = "vocab.txt"
MANGA_OCR_GENERATION_FILENAME = "generation_config.json"

#: Per-file SHA-256 pins (the exact artifacts INFER-BASELINE-EP-1 measured).
MANGA_OCR_ENCODER_SHA256 = (
    "15fa8155fe9bc1a7d25d9bb353debaa4def033d0174e907dbd2dd6d995def85f"
)
MANGA_OCR_DECODER_SHA256 = (
    "ef7765261e9d1cdc34d89356986c2bbc2a082897f753a89605ae80fdfa61f5e8"
)
MANGA_OCR_VOCAB_SHA256 = (
    "5cb5c5586d98a2f331d9f8828e4586479b0611bfba5d8c3b6dadffc84d6a36a3"
)

#: Preprocessing constants (checkpoint preprocessor_config.json:
#: size 224x224, resample BILINEAR, rescale 1/255, mean/std 0.5).
MANGA_OCR_INPUT_SIZE = 224
MANGA_OCR_MEAN = 0.5
MANGA_OCR_STD = 0.5

#: Decode defaults; the generation_config.json values (2/[SEP]=3) are used when
#: the file is present. ``max_len`` mirrors the INFER baseline's verified loop
#: (greedy argmax, Python-side decode, no KV cache in the shipped graph).
MANGA_OCR_START_TOKEN_ID = 2
MANGA_OCR_EOS_TOKEN_ID = 3
MANGA_OCR_MAX_LEN = 24

#: Tokens the tokenizer would skip (``skip_special_tokens=True`` semantics of
#: the torch manga-ocr adapter): a junk/empty region must never leak special
#: tokens into the rendered text.
MANGA_OCR_SPECIAL_TOKENS = frozenset({"[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"})

MANGA_OCR_WEIGHTS_ENV = "NEWMANGA_MANGA_OCR_WEIGHTS"
MANGA_OCR_DEVICE_ENV = "NEWMANGA_OCR_DEVICE"


def _lazy_import(module_name: str, stage: str = "ocr") -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"optional runtime {module_name!r} is not installed: {error}",
            stage=stage,
        ) from error


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve_weights_dir(weights_dir: Path | None) -> Path:
    """Resolve the local ONNX OCR bundle directory (never downloads).

    Order: explicit argument > ``NEWMANGA_MANGA_OCR_WEIGHTS`` > the frozen
    bundle copy (``<exe dir>/models/ocr/manga-ocr-onnx``) > the data root >
    the per-user default data root. The result is returned even when nothing
    exists — the engine raises the typed gap with the full candidate list.
    """
    if weights_dir is not None:
        return Path(weights_dir)
    env = os.environ.get(MANGA_OCR_WEIGHTS_ENV)
    if env:
        return Path(env)
    candidates: list[Path] = []
    if getattr(sys, "frozen", False):
        candidates.append(
            Path(sys.executable).resolve().parent
            / "models"
            / "ocr"
            / MANGA_OCR_ONNX_DIRNAME
        )
    data_root = os.environ.get("NEWMANGA_DATA_ROOT")
    if data_root:
        candidates.append(Path(data_root) / "models" / "ocr" / MANGA_OCR_ONNX_DIRNAME)
    local_appdata = os.environ.get("LOCALAPPDATA") or str(Path.home())
    candidates.append(
        Path(local_appdata) / "New Manga" / "models" / "ocr" / MANGA_OCR_ONNX_DIRNAME
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return candidates[0]


@dataclass
class MangaOcrOnnxProvider:
    """``OcrProvider`` over the pinned manga-ocr encoder/decoder ONNX pair."""

    weights_dir: Path | None = None
    device: str = "cpu"
    provider_id: str = PROVIDER_MANGA_OCR
    provider_type: str = "local-manga-ocr-onnx"
    model: str = "manga-ocr-base-onnx"
    engine_factory: Callable[[Path], Any] | None = None
    languages: frozenset[str] = frozenset({SCRIPT_JAPANESE})
    needs_detection: bool = False
    requirements: tuple[str, ...] = ("onnxruntime", "PIL")

    _engine: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._engine = None

    def _engine_or_raise(self) -> Any:
        if self._engine is None:
            directory = resolve_weights_dir(self.weights_dir)
            factory = self.engine_factory
            self._engine = (
                factory(directory) if factory is not None else _MangaOcrOnnxEngine(directory, self.device)
            )
        return self._engine

    def recognize(self, request: OcrRequest) -> OcrResult:
        if request.script not in self.languages:
            raise ProviderInputError(
                f"{self.provider_id} does not support script {request.script!r}",
                provider_id=self.provider_id,
                stage="ocr",
            )
        if not request.image_bytes:
            raise ProviderInputError(
                "no image bytes were supplied for the region crop",
                provider_id=self.provider_id,
                stage="ocr",
            )
        engine = self._engine_or_raise()
        image = _pil_image(request.image_bytes, self.provider_id)
        # Injection contract (same as the torch adapter): the engine receives
        # the decoded PIL crop, never raw bytes.
        text = engine(image)
        if not isinstance(text, str):
            raise ProviderError(
                f"manga-ocr ONNX engine returned {type(text).__name__}, expected str",
                provider_id=self.provider_id,
                stage="ocr",
            )
        lines = (OcrLine(text=text),) if text else ()
        return OcrResult(
            region_id=request.region_id,
            text=text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            confidence=None,  # manga-ocr reports no confidence; never invented
            script=request.script,
            direction=request.direction,
            lines=lines,
            options=request.options,
        )


def _pil_image(image_bytes: bytes, provider_id: str) -> Any:
    module = _lazy_import("PIL.Image")
    import io

    try:
        return module.open(io.BytesIO(image_bytes))
    except Exception as error:  # noqa: BLE001 - reported as typed provider input
        raise ProviderInputError(
            f"region crop is not a decodable image: {error!r}",
            provider_id=provider_id,
            stage="ocr",
        ) from error


class _MangaOcrOnnxEngine:
    """Encoder + decoder ONNX pair with a Python-side greedy decode loop."""

    def __init__(self, weights_dir: Path, device: str = "cpu") -> None:
        self.weights_dir = Path(weights_dir)
        self.device = device
        self.encoder: Any = None
        self.decoder: Any = None
        self.vocab: tuple[str, ...] = ()
        self.start_id = MANGA_OCR_START_TOKEN_ID
        self.eos_id = MANGA_OCR_EOS_TOKEN_ID
        self.max_len = MANGA_OCR_MAX_LEN
        self.encoder_input = "pixel_values"
        self.decoder_ids_input = "input_ids"
        self.decoder_hidden_input = "encoder_hidden_states"

    # -- loading (lazy, on first OCR call) ---------------------------------

    def __call__(self, image: Any) -> str:
        self._ensure_loaded()
        numpy = _lazy_import("numpy")
        tensor = self._preprocess(image, numpy)
        hidden = self.encoder.run(
            None, {self.encoder_input: tensor}
        )[0]
        ids = [self.start_id]
        for _ in range(self.max_len):
            logits = self.decoder.run(
                None,
                {
                    self.decoder_ids_input: numpy.asarray([ids], dtype=numpy.int64),
                    self.decoder_hidden_input: hidden,
                },
            )[0]
            next_id = int(logits[0, -1].argmax())
            if next_id == self.eos_id:
                break
            ids.append(next_id)
        return "".join(
            self.vocab[token]
            for token in ids[1:]
            if 0 <= token < len(self.vocab)
            and self.vocab[token] not in MANGA_OCR_SPECIAL_TOKENS
        )

    def _ensure_loaded(self) -> None:
        if self.encoder is not None:
            return
        directory = self.weights_dir
        if not directory.is_dir():
            raise ProviderNotConfigured(
                f"manga-ocr ONNX weights are not installed: directory "
                f"{directory} is missing (place the pinned "
                f"{MANGA_OCR_ONNX_DIRNAME} bundle there — {MANGA_OCR_ENCODER_FILENAME} "
                f"/ {MANGA_OCR_DECODER_FILENAME} / {MANGA_OCR_VOCAB_FILENAME} — or "
                f"set {MANGA_OCR_WEIGHTS_ENV}; weights are never downloaded at "
                "run time)",
                stage="ocr",
            )
        pinned = (
            (MANGA_OCR_ENCODER_FILENAME, MANGA_OCR_ENCODER_SHA256),
            (MANGA_OCR_DECODER_FILENAME, MANGA_OCR_DECODER_SHA256),
            (MANGA_OCR_VOCAB_FILENAME, MANGA_OCR_VOCAB_SHA256),
        )
        for filename, _pin in pinned:
            candidate = directory / filename
            if not candidate.is_file():
                raise ProviderNotConfigured(
                    f"manga-ocr ONNX weights are not installed: {candidate} is missing",
                    stage="ocr",
                )
        resolve_execution_provider(self.device, "ocr")
        for filename, pin in pinned:
            actual = _sha256_file(directory / filename)
            if actual != pin:
                raise ProviderError(
                    f"manga-ocr ONNX weights file {directory / filename} has "
                    f"sha256 {actual}, expected {pin}; refusing to run "
                    "unverified weights",
                    stage="ocr",
                )
        self._load_generation_config(directory / MANGA_OCR_GENERATION_FILENAME)
        self.vocab = tuple(
            (directory / MANGA_OCR_VOCAB_FILENAME)
            .read_text(encoding="utf-8")
            .splitlines()
        )
        self.encoder = create_session(
            directory / MANGA_OCR_ENCODER_FILENAME, device=self.device, stage="ocr"
        )
        self.decoder = create_session(
            directory / MANGA_OCR_DECODER_FILENAME, device=self.device, stage="ocr"
        )
        self.encoder_input = self.encoder.get_inputs()[0].name
        decoder_inputs = self.decoder.get_inputs()
        if len(decoder_inputs) < 2:
            raise ProviderError(
                "manga-ocr decoder ONNX exposes fewer than two inputs",
                stage="ocr",
            )
        self.decoder_ids_input = decoder_inputs[0].name
        self.decoder_hidden_input = decoder_inputs[1].name

    def _load_generation_config(self, path: Path) -> None:
        if not path.is_file():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as error:  # noqa: BLE001 - malformed config is typed
            raise ProviderError(
                f"manga-ocr generation config is malformed: {error!r}", stage="ocr"
            ) from error
        start = payload.get("decoder_start_token_id")
        eos = payload.get("eos_token_id")
        if isinstance(start, int):
            self.start_id = start
        if isinstance(eos, int):
            self.eos_id = eos

    # -- preprocessing -----------------------------------------------------

    def _preprocess(self, image: Any, numpy: Any) -> Any:
        """The checkpoint's ViTFeatureExtractor pipeline, exactly."""
        pillow = _lazy_import("PIL.Image")
        if getattr(image, "mode", "RGB") != "RGB":
            image = image.convert("RGB")
        resized = image.resize(
            (MANGA_OCR_INPUT_SIZE, MANGA_OCR_INPUT_SIZE),
            pillow.Resampling.BILINEAR,
        )
        array = numpy.asarray(resized, dtype=numpy.float32) / 255.0
        array = (array - MANGA_OCR_MEAN) / MANGA_OCR_STD
        return numpy.ascontiguousarray(array.transpose(2, 0, 1)[None])
