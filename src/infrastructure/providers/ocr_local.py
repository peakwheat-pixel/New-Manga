"""Local OCR adapters: manga-ocr (recognition-only) and PaddleOCR Korean.

Both adapters are *fail-closed*:

- their requirements are probed before resolution, so an absent module shows
  as ``missing_dependency`` (AC-OPTIONAL-002) instead of a crash
  (AC-OPTIONAL-001);
- the engine is imported lazily inside the call, and an import failure is
  re-raised as a typed :class:`ProviderDependencyMissing`;
- ``manga-ocr`` declares ``needs_detection = False`` and is therefore only
  ever handed a single Region crop — it must not fabricate detection boxes
  (TASK-016 conclusion).

The engine is injectable so the adapter's request/response mapping can be
tested without a model. That tests the *adapter*, never OCR quality: no
quality number is produced in this environment and none is claimed.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from ports.ocr.ports import (
    OcrLine,
    OcrRequest,
    OcrResult,
    SCRIPT_JAPANESE,
    SCRIPT_KOREAN,
    SCRIPT_LATIN,
)
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderInputError,
    ProviderInvalidOutput,
)

PROVIDER_MANGA_OCR = "manga-ocr"
PROVIDER_PADDLE_KOREAN = "paddleocr-korean"


def _lazy_import(module_name: str) -> Any:
    """Import an optional runtime, mapping failure onto the closed taxonomy."""
    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"optional runtime {module_name!r} is not installed: {error}",
            stage="ocr",
        ) from error


@dataclass
class MangaOcrProvider:
    """Japanese manga recognition on one Region crop (TASK-016 candidate)."""

    provider_id: str = PROVIDER_MANGA_OCR
    provider_type: str = "local-manga-ocr"
    model: str = "manga-ocr-base"
    engine_factory: Callable[[], Any] | None = None
    languages: frozenset[str] = frozenset({SCRIPT_JAPANESE})
    needs_detection: bool = False
    #: ``manga-ocr`` reads files/images through Pillow; both are probed.
    requirements: tuple[str, ...] = ("manga_ocr", "PIL")

    def __post_init__(self) -> None:
        self._engine: Any | None = None

    def _engine_or_raise(self) -> Any:
        if self._engine is None:
            factory = self.engine_factory
            if factory is None:
                module = _lazy_import("manga_ocr")
                engine_class = getattr(module, "MangaOcr", None)
                if engine_class is None:
                    raise ProviderDependencyMissing(
                        "manga_ocr exposes no MangaOcr class", stage="ocr"
                    )
                factory = engine_class
            self._engine = factory()
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
        # ``manga-ocr`` accepts a file path or a PIL image; the crop is handed
        # over as a PIL image built from the encoded bytes, never as a page.
        image = _pil_image(request.image_bytes, self.provider_id)
        text = engine(image)
        if not isinstance(text, str):
            raise ProviderInvalidOutput(
                f"manga-ocr returned {type(text).__name__}, expected str",
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


@dataclass
class PaddleKoreanOcrProvider:
    """Korean Webtoon OCR: shared detector + Korean/English recognition.

    D06 §7.2 route target for Korean Webtoon; a Vision fallback is only ever
    used when it is explicitly configured on the binding.
    """

    provider_id: str = PROVIDER_PADDLE_KOREAN
    provider_type: str = "local-paddleocr"
    model: str = "korean_PP-OCRv5_mobile_rec"
    engine_factory: Callable[[], Any] | None = None
    languages: frozenset[str] = frozenset({SCRIPT_KOREAN, SCRIPT_LATIN})
    needs_detection: bool = True
    requirements: tuple[str, ...] = ("paddleocr", "paddle")

    def __post_init__(self) -> None:
        self._engine: Any | None = None

    def _engine_or_raise(self) -> Any:
        if self._engine is None:
            module = _lazy_import("paddleocr")
            engine_class = getattr(module, "PaddleOCR", None)
            if engine_class is None:
                raise ProviderDependencyMissing(
                    "paddleocr exposes no PaddleOCR class", stage="ocr"
                )
            factory = self.engine_factory
            self._engine = factory() if factory is not None else engine_class(lang="korean")
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
        lines = _parse_paddle_output(
            engine.ocr(request.image_bytes), self.provider_id
        )
        text = "\n".join(line.text for line in lines)
        confidences = [line.confidence for line in lines if line.confidence is not None]
        return OcrResult(
            region_id=request.region_id,
            text=text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            confidence=(sum(confidences) / len(confidences) if confidences else None),
            script=request.script,
            direction=request.direction,
            lines=lines,
            options=request.options,
        )


def _parse_paddle_output(raw: Any, provider_id: str) -> tuple[OcrLine, ...]:
    """Normalise PaddleOCR output; anything unrecognised is a typed failure.

    PaddleOCR's return shape differs between versions, so the adapter accepts
    the documented ``[[ [box, (text, score)], ... ]]`` nesting and refuses
    everything else rather than guessing (TASK-016 protocol discipline).
    """
    if raw is None:
        return ()
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        raise ProviderInvalidOutput(
            f"paddleocr returned {type(raw).__name__}, expected a list",
            provider_id=provider_id,
            stage="ocr",
        )
    lines: list[OcrLine] = []
    for page in raw:
        if page is None:
            continue
        if not isinstance(page, Sequence) or isinstance(page, (str, bytes)):
            raise ProviderInvalidOutput(
                "paddleocr page payload is not a list", provider_id=provider_id, stage="ocr"
            )
        for item in page:
            if not isinstance(item, Sequence) or len(item) < 2:
                raise ProviderInvalidOutput(
                    f"paddleocr item is malformed: {item!r}",
                    provider_id=provider_id,
                    stage="ocr",
                )
            box, recognition = item[0], item[1]
            text, score = _split_recognition(recognition, provider_id)
            lines.append(
                OcrLine(
                    text=text,
                    confidence=score,
                    polygon=_polygon_of(box, provider_id),
                )
            )
    return tuple(lines)


def _split_recognition(recognition: Any, provider_id: str) -> tuple[str, float | None]:
    if isinstance(recognition, (list, tuple)) and len(recognition) >= 2:
        text, score = recognition[0], recognition[1]
        if not isinstance(text, str):
            raise ProviderInvalidOutput(
                "paddleocr text is not a string", provider_id=provider_id, stage="ocr"
            )
        try:
            confidence = float(score)
        except (TypeError, ValueError):
            confidence = None
        return text, confidence
    if isinstance(recognition, str):
        return recognition, None
    raise ProviderInvalidOutput(
        f"paddleocr recognition payload is malformed: {recognition!r}",
        provider_id=provider_id,
        stage="ocr",
    )


def _polygon_of(box: Any, provider_id: str) -> tuple[tuple[float, float], ...]:
    if not isinstance(box, Sequence) or isinstance(box, (str, bytes)):
        return ()
    points: list[tuple[float, float]] = []
    try:
        for point in box:
            x, y = point[0], point[1]
            points.append((float(x), float(y)))
    except (TypeError, ValueError, IndexError):
        raise ProviderInvalidOutput(
            f"paddleocr polygon is malformed: {box!r}",
            provider_id=provider_id,
            stage="ocr",
        ) from None
    return tuple(points)
