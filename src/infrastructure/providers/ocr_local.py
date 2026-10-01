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
Injection contract (DSH r1 R2): an injected engine receives the decoded
BGR ``numpy.ndarray`` crop through ``ocr`` — NOT raw bytes. handing raw
bytes to the engine is never the caller's job again.

PaddleOCR 3.x adaptation (M2-OCR-PADDLE3X-1, evidence in
``verification/M2-OCR-PADDLE3X-1/``):

- OBSERVATION (M2-TA3-B phase 1): paddleocr 3.x returned an exception-free
  EMPTY result for ``engine.ocr(<raw bytes>)``.
- MECHANISM (AC1 diagnosis, settled with two different regions back-to-back
  on the production-default construction): ALWAYS_EMPTY, not stale-reuse —
  3.x rejects bytes at the INPUT-TYPE CHECK layer (engine log: "Not
  supported input data type! Only `numpy.ndarray` and `str` are supported!
  So has been ignored"), never invokes an executor, and returns an empty
  list. No wrong-text surface ever existed; the risk was silent empty OCR.
  Hence the adapter decodes the encoded crop to a BGR ndarray (numpy +
  OpenCV, in-memory ``np.frombuffer`` — no CJK filesystem round-trip) and
  hands the ndarray to the engine.
- The default engine construction pins ``enable_mkldnn=False``:
  paddlepaddle 3.3.1 Windows CPU crashes on the default MKLDNN path with a
  PIR/oneDNN executor bug (``ConvertPirAttribute2RuntimeAttribute``
  NotImplementedError). The flag is accepted by 2.x as well, so the
  default path stays version-agnostic.
- OUTPUT shape: both documented shapes are normalised — the 2.x legacy
  ``[[ [box, (text, score)], ... ]]`` nesting AND the 3.x payload
  (``rec_texts`` / ``rec_scores`` / ``rec_polys`` | ``rec_boxes``, reached
  via the result object's ``.json`` under the ``res`` key). Boxes are
  materialised to plain Python point lists first: numpy arrays are NOT
  ``collections.abc.Sequence`` and were silently dropped to ``()`` (DSH r2
  N6). Anything still unrecognised raises :class:`ProviderInvalidOutput` —
  fail-closed semantics are unchanged, nothing is guessed.
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
            self._engine = (
                factory()
                if factory is not None
                else engine_class(lang="korean", enable_mkldnn=False)
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
        # paddleocr 3.x silently ignores bytes input (diagnosed ALWAYS_EMPTY,
        # verification/M2-OCR-PADDLE3X-1): decode to a BGR ndarray first.
        image = _ndarray_from_bytes(request.image_bytes, self.provider_id)
        lines = _parse_paddle_output(engine.ocr(image), self.provider_id)
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


def _ndarray_from_bytes(image_bytes: bytes, provider_id: str) -> Any:
    """Decode an encoded region crop into the BGR ndarray the engine reads.

    PaddleOCR 3.x accepts only ``str`` paths and ndarrays and SILENTLY
    ignores everything else (ALWAYS_EMPTY diagnosis,
    ``verification/M2-OCR-PADDLE3X-1/diagnosis.json``). The crop is decoded
    in memory (``np.frombuffer`` + ``cv2.imdecode``) — no filesystem
    round-trip, so the Windows CJK path caveat of ``np.fromfile`` does not
    even apply. numpy/OpenCV are hard transitive dependencies of paddleocr,
    but a broken environment fails typed, never with a bare ImportError.
    """
    numpy = _lazy_import("numpy")
    cv2 = _lazy_import("cv2")
    try:
        buffer = numpy.frombuffer(image_bytes, dtype=numpy.uint8)
        image = cv2.imdecode(buffer, cv2.IMREAD_COLOR)
    except Exception as error:  # noqa: BLE001 - reported as typed provider input
        raise ProviderInputError(
            f"region crop is not a decodable image: {error!r}",
            provider_id=provider_id,
            stage="ocr",
        ) from error
    if image is None:
        raise ProviderInputError(
            "region crop is not a decodable image",
            provider_id=provider_id,
            stage="ocr",
        )
    return image


def _paddle3x_payload(page: Any) -> dict[str, Any] | None:
    """Return the ``rec_*`` body of a 3.x result page, else None (legacy).

    A 3.x page is either a plain dict or a result object exposing ``.json``;
    the recognition body lives under the ``res`` key (M2-TA3-B wrapper,
    end-to-end verified). Legacy 2.x pages are lists and never carry
    ``rec_texts``.
    """
    payload = page if isinstance(page, dict) else getattr(page, "json", None)
    if not isinstance(payload, dict):
        return None
    body = payload.get("res", payload)
    if isinstance(body, dict) and "rec_texts" in body:
        return body
    return None


def _parse_paddle_output(raw: Any, provider_id: str) -> tuple[OcrLine, ...]:
    """Normalise PaddleOCR output; anything unrecognised is a typed failure.

    PaddleOCR's return shape differs between versions and BOTH documented
    shapes are accepted:

    - 2.x legacy: ``[[ [box, (text, score)], ... ]]`` nesting;
    - 3.x: one result object/dict per image whose payload carries
      ``rec_texts`` / ``rec_scores`` and ``rec_polys`` (or ``rec_boxes``).

    Everything else is refused rather than guessed (TASK-016 protocol
    discipline; fail-closed semantics unchanged by the 3.x adaptation).
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
        body = _paddle3x_payload(page)
        if body is not None:
            lines.extend(_lines_from_paddle3x(body, provider_id))
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


def _lines_from_paddle3x(body: dict[str, Any], provider_id: str) -> list[OcrLine]:
    """Map one 3.x ``rec_*`` body onto legacy-equivalent OcrLine entries.

    ``rec_scores`` and ``rec_polys``/``rec_boxes`` are optional and may be
    shorter than ``rec_texts``; missing values stay ``None`` / empty instead
    of being invented (same discipline as the manga-ocr confidence).
    """
    # explicit None checks (DSH r1 R3): a len>1 ndarray payload would crash
    # a truthiness test with "truth value of an array is ambiguous" — the
    # same function already accepts ndarray boxes, so keep one stance.
    texts = body.get("rec_texts")
    scores = body.get("rec_scores")
    texts = [] if texts is None else texts
    scores = [] if scores is None else scores
    polys = body.get("rec_polys", None)
    if polys is None:
        polys = body.get("rec_boxes", None)
    lines: list[OcrLine] = []
    for index, text in enumerate(texts):
        if not isinstance(text, str):
            raise ProviderInvalidOutput(
                "paddleocr text is not a string", provider_id=provider_id, stage="ocr"
            )
        score = _float_or_none(scores[index]) if index < len(scores) else None
        box = _box_at(polys, index)
        lines.append(
            OcrLine(
                text=text,
                confidence=score,
                polygon=_polygon_of(box, provider_id),
            )
        )
    return lines


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _box_at(polys: Any, index: int) -> Any:
    """One box of the 3.x batch (whole-batch ndarray or per-line sequence)."""
    if polys is None or isinstance(polys, (str, bytes)):
        return None
    try:
        if index >= len(polys):
            return None
        return polys[index]
    except (TypeError, IndexError, KeyError):
        return None


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
    if hasattr(box, "tolist"):
        # numpy arrays (3.x rec_polys rows, whole rec_boxes batches) are NOT
        # collections.abc.Sequence — without materialisation the polygon
        # would be silently dropped to () below (DSH r2 N6).
        box = box.tolist()
    if not isinstance(box, Sequence) or isinstance(box, (str, bytes)):
        return ()
    points: list[tuple[float, float]] = []
    try:
        if len(box) == 4 and all(isinstance(v, (int, float)) for v in box):
            x1, y1, x2, y2 = box  # rec_boxes xyxy rectangle -> 4-point polygon
            box = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
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
