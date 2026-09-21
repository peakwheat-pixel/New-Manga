"""Local docTR text-detection adapter (T1.1.1, REBASELINE_PLAN order 2).

Selected in ``doc/research/T1.1.1-detector-evaluation.md``: docTR's
``fast_base`` (FAST) detector — Apache-2.0, pip-installable, verified on
Windows / Python 3.12, weights pinned and hash-checked offline.

Fail-closed rules (T1.1.1 acceptance):

- **no run-time download**: the weights file is resolved by the assembly
  (``bootstrap.app``), and this adapter only ever loads a *local file*;
  a missing file is ``PROVIDER_NOT_CONFIGURED`` — the same diagnosable gap
  the unwired ``detector=None`` produced, never a network fetch and never a
  silent fallback;
- **supply-chain integrity**: the weights file's SHA-256 is checked against
  the pinned value below before the model is built; a mismatch is
  ``PROVIDER_FAILED`` (corrupted or substituted artifact), never a warning;
- **no fabricated output**: the docTR model never names a Region — word
  boxes become anonymous ``provider_label``s and the caller assigns ids
  (``ports.detection``);
- a page with no text yields zero candidates and the *handler* turns that
  into the typed ``INVALID_INPUT`` (adapter stays honest, no padding boxes).

The word-to-block merge policy below is **frozen** (T1.1.1 gate): the
constants are the exact values the released evaluation harness ran at 22/22
(see ``doc/research/T1.1.1-detector-evaluation.md`` §7.2). Changing them is a
contract change and needs its own slice with re-run evidence.

The docTR/torch stack is imported lazily on first use, so a machine without
the heavy runtime still boots the app; the first ``detect`` reports the
typed dependency gap instead.
"""

from __future__ import annotations

import hashlib
import importlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
    ProviderUnavailable,
)

PROVIDER_DOCTR = "local-doctr"

#: The pinned detection architecture and its weights artifact (T1.1.1).
DOCTR_ARCH = "fast_base"
DOCTR_WEIGHTS_FILENAME = "fast_base-688a8b34.pt"
DOCTR_WEIGHTS_SHA256 = (
    "688a8b3489e9f5d0290c476c6272ec3b18de3ee646c8a0dc158203b1a9c62ace"
)
DOCTR_WEIGHTS_URL = (
    "https://doctr-static.mindee.com/models?id=v0.8.1/fast_base-688a8b34.pt&src=0"
)

# --- frozen word-to-block merge policy (do not tune without a new slice) ----
#: word boxes whose vertical centers are within ``factor × median word
#: height`` (at least ``MIN_TOLERANCE_PX``) belong to the same block.
MERGE_VERTICAL_FACTOR = 0.7
MERGE_MIN_TOLERANCE_PX = 8.0
#: horizontal gap up to ``tolerance`` px still merges (word spacing).
MERGE_HORIZONTAL_TOLERANCE_PX = 8.0
#: candidate rectangles are grown by this padding on every side.
MERGE_PAD_PX = 6.0
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class DoctrDetectionProvider:
    """``DetectionProvider`` over a locally pinned docTR FAST detector."""

    weights_path: Path
    device: str = "cpu"
    provider_id: str = PROVIDER_DOCTR
    provider_type: str = "local-doctr"
    model: str = f"doctr/{DOCTR_ARCH}"
    requirements: tuple[str, ...] = ("doctr", "torch")

    _engine: Any = field(default=None, init=False, repr=False)

    def detect(self, request: DetectionRequest) -> DetectionResult:
        started = time.perf_counter()
        self._validate_request(request)
        model = self._engine_or_raise()
        rgb = self._frame_pixels(request)
        raw = _run_detection(model, rgb)

        width, height = float(rgb.shape[1]), float(rgb.shape[0])
        boxes = _boxes_from_doctr(raw, width, height)
        blocks = cluster_words_into_blocks(
            [(b[0], b[1], b[2], b[3]) for b in boxes],
            [b[4] for b in boxes],
        )
        candidates = tuple(
            RegionCandidate(
                polygon=tuple(polygon),
                reading_order=index,
                confidence=confidence,
                provider_label=f"doctr-{index}",
            )
            for index, (polygon, confidence) in enumerate(blocks, start=1)
        )
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        return DetectionResult(
            page_id=request.page_id,
            candidates=candidates,
            coordinate_space="page-global",
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model=self.model,
            options=(("arch", DOCTR_ARCH), ("device", self.device)),
            elapsed_ms=elapsed_ms,
        )

    # -- engine lifecycle ---------------------------------------------------

    def _engine_or_raise(self) -> Any:
        if self._engine is None:
            self._engine = _build_engine(self.weights_path, self.device)
        return self._engine

    @staticmethod
    def _validate_request(request: DetectionRequest) -> None:
        """Pure-Python input gate: runs before any dependency is touched."""
        if not request.image_bytes:
            raise ProviderInputError(
                "no image bytes were supplied for detection",
                provider_id=PROVIDER_DOCTR,
                stage="detection",
            )
        if request.width <= 0 or request.height <= 0:
            raise ProviderInputError(
                f"invalid frame size {request.width}x{request.height}",
                provider_id=PROVIDER_DOCTR,
                stage="detection",
            )
        expected = request.width * request.height
        if len(request.image_bytes) not in (expected * 3, expected * 4):
            raise ProviderInputError(
                f"frame byte count {len(request.image_bytes)} does not match "
                f"{request.width}x{request.height} rgb32 or rgb24 pixels",
                provider_id=PROVIDER_DOCTR,
                stage="detection",
            )

    @staticmethod
    def _frame_pixels(request: DetectionRequest) -> Any:
        """Decode the frame buffer into an HxWx3 uint8 RGB array.

        The production ``page_frame`` contract (``bootstrap.app``,
        ``ports.inpaint``) hands over a *raw pixel buffer*, never an encoded
        file: ``rgb32`` (QImage Format_RGB32, little-endian BGRA in memory)
        or ``rgb24``. Runs after the engine is built, so numpy — a hard
        docTR dependency — is guaranteed present here.
        """
        numpy = _lazy_import("numpy", "detection")
        raw = numpy.frombuffer(request.image_bytes, dtype=numpy.uint8)
        expected = request.width * request.height
        if raw.size == expected * 4:  # rgb32: BGRA in memory, alpha forced 0xff
            bgra = raw.reshape(request.height, request.width, 4)
            return bgra[:, :, :3][:, :, ::-1].copy()
        return raw.reshape(request.height, request.width, 3)


def _build_engine(weights_path: Path, device: str) -> Any:
    """Load the pinned weights into docTR without touching the network.

    Check order matters and is part of the contract:

    1. the weights *file* must exist — its absence is the same diagnosable
       assembly gap the unwired ``detector=None`` produced, so it is probed
       first with zero dependencies (no torch, no numpy);
    2. the heavy runtime must import — a machine that fetched weights but
      never installed torch gets the typed dependency gap;
    3. the device must resolve;
    4. the SHA-256 must match the pin — a corrupted or substituted artifact
       is ``PROVIDER_FAILED``, never a warning.

    ``fast_base(pretrained=False)`` builds a randomly initialised model and
    ``load_pretrained_params`` takes a *local path* — docTR's URL/download
    branch is never entered, so detection cannot silently fetch anything.
    """
    if not weights_path.is_file():
        raise ProviderNotConfigured(
            f"docTR weights are not installed: {weights_path} is missing "
            f"(fetch {DOCTR_WEIGHTS_URL} and verify sha256 "
            f"{DOCTR_WEIGHTS_SHA256})",
            stage="detection",
        )
    torch = _lazy_import("torch", "detection")
    resolved = _resolve_device(torch, device)
    actual = sha256_file(weights_path)
    if actual != DOCTR_WEIGHTS_SHA256:
        raise ProviderError(
            f"docTR weights at {weights_path} have sha256 {actual}, expected "
            f"{DOCTR_WEIGHTS_SHA256}; refusing to run unverified weights",
            stage="detection",
        )
    doctr_models = _lazy_import("doctr.models", "detection")
    doctr_utils = _lazy_import("doctr.models.utils", "detection")
    try:
        model = doctr_models.fast_base(pretrained=False)
        doctr_utils.load_pretrained_params(model, str(weights_path))
        model.eval()
        if resolved == "cuda":
            model = model.cuda()
        from doctr.models import detection_predictor

        predictor = detection_predictor(
            arch=model,
            pretrained=False,
            assume_straight_pages=True,
            batch_size=1,
        )
        return predictor
    except (ProviderNotConfigured, ProviderDependencyMissing, ProviderError):
        raise
    except Exception as error:  # noqa: BLE001 - any model-build failure is typed
        raise ProviderError(
            f"docTR engine failed to load from {weights_path}: {error!r}",
            stage="detection",
        ) from error


def _resolve_device(torch: Any, device: str) -> str:
    """Resolve the requested device; ``auto`` prefers CUDA when present."""
    if device == "auto":
        return "cuda" if getattr(torch.cuda, "is_available", lambda: False)() else "cpu"
    if device == "cuda":
        if not getattr(torch.cuda, "is_available", lambda: False)():
            raise ProviderUnavailable(
                "cuda was requested for the detector but is not available",
                stage="detection",
            )
        return "cuda"
    if device == "cpu":
        return "cpu"
    raise ProviderInputError(
        f"unsupported detector device {device!r} (use cpu|cuda|auto)",
        provider_id=PROVIDER_DOCTR,
        stage="detection",
    )


def _run_detection(predictor: Any, rgb: Any) -> Any:
    try:
        result = predictor([rgb])
    except Exception as error:  # noqa: BLE001 - inference failures are typed
        raise ProviderError(
            f"docTR detection inference failed: {error!r}",
            stage="detection",
        ) from error
    if not result:
        raise ProviderInvalidOutput(
            "docTR returned no page result", provider_id=PROVIDER_DOCTR, stage="detection"
        )
    page = result[0]
    if not isinstance(page, dict) or "words" not in page:
        raise ProviderInvalidOutput(
            f"docTR page payload is malformed: {type(page).__name__}",
            provider_id=PROVIDER_DOCTR,
            stage="detection",
        )
    return page["words"]


def _boxes_from_doctr(
    raw: Any, width: float, height: float
) -> list[tuple[float, float, float, float, float]]:
    """docTR straight-page output is (N, 5) = xmin, ymin, xmax, ymax, conf in
    page-relative coordinates; anything else is a typed invalid output."""
    numpy = _lazy_import("numpy", "detection")
    try:
        boxes = numpy.asarray(raw, dtype=float).reshape(-1, 5)
    except ValueError as error:
        raise ProviderInvalidOutput(
            f"docTR boxes are not (N, 5) straight boxes: {error!r}",
            provider_id=PROVIDER_DOCTR,
            stage="detection",
        ) from error
    scaled: list[tuple[float, float, float, float, float]] = []
    for row in boxes:
        xmin = min(max(float(row[0]) * width, 0.0), width)
        ymin = min(max(float(row[1]) * height, 0.0), height)
        xmax = min(max(float(row[2]) * width, 0.0), width)
        ymax = min(max(float(row[3]) * height, 0.0), height)
        confidence = float(row[4])
        if xmax < xmin or ymax < ymin:
            continue
        if not 0.0 <= confidence <= 1.0:
            raise ProviderInvalidOutput(
                f"docTR confidence out of range: {confidence}",
                provider_id=PROVIDER_DOCTR,
                stage="detection",
            )
        scaled.append((xmin, ymin, xmax, ymax, confidence))
    return scaled


def cluster_words_into_blocks(
    rects: list[tuple[float, float, float, float]],
    confidences: list[float],
) -> list[tuple[list[tuple[float, float]], float]]:
    """Frozen word-to-block merge policy (T1.1.1).

    Word boxes whose vertical centers are within
    ``max(MERGE_VERTICAL_FACTOR × median height, MERGE_MIN_TOLERANCE_PX)``
    and whose horizontal gap is at most ``MERGE_HORIZONTAL_TOLERANCE_PX`` are
    merged into one block rectangle, padded by ``MERGE_PAD_PX``; blocks are
    ordered top-to-bottom, left-to-right. Block confidence is the mean word
    confidence. Deterministic and side-effect free.
    """
    if not rects:
        return []
    if len(rects) != len(confidences):
        raise ProviderInputError(
            "word boxes and confidences diverge",
            provider_id=PROVIDER_DOCTR,
            stage="detection",
        )
    heights = [r[3] - r[1] for r in rects]
    ordered = sorted(heights)
    middle = len(ordered) // 2
    median_h = (
        float(ordered[middle])
        if len(ordered) % 2 == 1
        else (float(ordered[middle - 1]) + float(ordered[middle])) / 2.0
    )
    tolerance = max(median_h * MERGE_VERTICAL_FACTOR, MERGE_MIN_TOLERANCE_PX)

    remaining = sorted(range(len(rects)), key=lambda i: (rects[i][1], rects[i][0]))
    blocks: list[tuple[list[tuple[float, float]], float]] = []
    while remaining:
        group = [remaining.pop(0)]
        changed = True
        while changed:
            changed = False
            for idx in list(remaining):
                r = rects[idx]
                for g in group:
                    gr = rects[g]
                    v_close = abs((r[1] + r[3]) / 2 - (gr[1] + gr[3]) / 2) <= tolerance
                    h_near = min(r[2], gr[2]) - max(r[0], gr[0]) >= -tolerance
                    if v_close and h_near:
                        group.append(idx)
                        remaining.remove(idx)
                        changed = True
                        break
        xs0 = [rects[i][0] for i in group]
        ys0 = [rects[i][1] for i in group]
        xs1 = [rects[i][2] for i in group]
        ys1 = [rects[i][3] for i in group]
        x0, y0, x1, y1 = min(xs0), min(ys0), max(xs1), max(ys1)
        polygon = [
            (x0 - MERGE_PAD_PX, y0 - MERGE_PAD_PX),
            (x1 + MERGE_PAD_PX, y0 - MERGE_PAD_PX),
            (x1 + MERGE_PAD_PX, y1 + MERGE_PAD_PX),
            (x0 - MERGE_PAD_PX, y1 + MERGE_PAD_PX),
        ]
        confidence = sum(confidences[i] for i in group) / len(group)
        blocks.append((polygon, confidence))
    blocks.sort(key=lambda item: (min(y for _, y in item[0]), min(x for x, _ in item[0])))
    return blocks


def _lazy_import(module_name: str, stage: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"detector runtime {module_name!r} is not installed: {error}",
            provider_id=PROVIDER_DOCTR,
            stage=stage,
        ) from error
