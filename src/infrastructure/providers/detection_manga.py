"""Local manga-domain RT-DETR-v2 text-detection adapter (M2-PROD-DETECT-1).

Selected by the C4 qualification (Gate all PASS: Recall 0.9618 on seg05) and
the C1 spot-audit calibration (0 real dialogue misses; precision reported as
a pollution-bounded directional lower bound) — see
``verification/M2-DOCTR-QUAL/``. Model: ``ogkalu/comic-text-and-bubble-detector``
(HuggingFace, RT-DETR-v2, **Apache-2.0**, pinned revision ``16e8a622``).

Fail-closed rules — the exact four disciplines of the docTR adapter
(``detection_doctr.py``, T1.1.1), applied to a directory-pinned snapshot:

- **no run-time download**: the weights are resolved by the assembly
  (``bootstrap.core_assembly``) to a *local directory* (default
  ``<data root>/models/detector/ogkalu-comic-text-and-bubble-detector/``,
  override ``NEWMANGA_DETECTOR_WEIGHTS``); a missing directory or file is
  ``PROVIDER_NOT_CONFIGURED`` with configuration guidance, never a network
  fetch and never a silent fallback. ``from_pretrained`` is called with
  ``local_files_only=True`` so the hub can never be reached even online;
- **supply-chain integrity**: each of the three snapshot files
  (``model.safetensors`` / ``config.json`` / ``preprocessor_config.json``)
  is SHA-256-checked against its pinned value before the model is built; a
  mismatch is ``PROVIDER_FAILED`` (corrupted or substituted artifact),
  never a warning;
- **no fabricated output**: the model never names a Region — text boxes
  become anonymous ``provider_label``s (``manga-<n>``) and the caller
  assigns ids (``ports.detection``). The model emits three classes
  (0=bubble, 1=text_bubble, 2=text_free); only the TEXT classes (1, 2)
  become candidates — the ``bubble`` class is the speech-balloon shape,
  not a text box, and is dropped (the C4 granularity mapping, frozen);
- a page with no text yields zero candidates and the *handler* turns that
  into the typed ``INVALID_INPUT`` (adapter stays honest, no padding boxes).

Granularity + merge: each kept text box plays the "word" role and enters
the **frozen production word-to-block merge** — the exact constants of
``detection_doctr.py`` (T1.1.1 gate) are IMPORTED here, never copied and
never re-tuned, so the C4/C1 evidence numbers (which were measured against
the production merge) carry over structurally: any drift upstream is
impossible to miss because this module shares the same objects.

The torch/transformers stack is imported lazily on first use, so a machine
without the heavy runtime still boots the app; the first ``detect`` reports
the typed dependency gap instead (same lazy pattern as the docTR adapter).
"""

from __future__ import annotations

import hashlib
import importlib
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from infrastructure.providers.detection_doctr import (
    MERGE_HORIZONTAL_TOLERANCE_PX,
    MERGE_MIN_TOLERANCE_PX,
    MERGE_PAD_PX,
    MERGE_VERTICAL_FACTOR,
    cluster_words_into_blocks,
)
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
    ProviderUnavailable,
)

PROVIDER_MANGA = "local-manga"

#: The pinned snapshot identity (M2-DOCTR-QUAL-C4 weights manifest; HF
#: revision 16e8a622). Weights live on local/gitignored paths only — they
#: are never committed and never downloaded at run time.
MANGA_HF_REPO = "ogkalu/comic-text-and-bubble-detector"
MANGA_HF_REVISION = "16e8a622"
MANGA_WEIGHTS_DIRNAME = MANGA_HF_REPO.replace("/", "-")
MANGA_MODEL_FILENAME = "model.safetensors"
MANGA_CONFIG_FILENAME = "config.json"
MANGA_PREPROCESSOR_FILENAME = "preprocessor_config.json"

#: Per-file SHA-256 pins (all three files, individually).
MANGA_MODEL_SHA256 = (
    "037930a861e67870eb345be01b28cc70d7e2b7956528e48ee0ebdb0c093df80d"
)
MANGA_CONFIG_SHA256 = (
    "b6d707933e12e9593a7025604be1c95add70a6db371fdd1532e8854e2256e072"
)
MANGA_PREPROCESSOR_SHA256 = (
    "7e9e2245806aa3ef068a5321f5eebee3116fa4cec560173231954ffaca930eca"
)

#: The C4 formal run's post_process score threshold (cuda conf 0.5). Frozen
#: so production sees exactly what the qualification measured; retuning is a
#: new slice with re-run evidence.
MANGA_CONF_THRESHOLD = 0.5

#: Model classes: 0=bubble (balloon shape, dropped), 1=text_bubble,
#: 2=text_free. Only the TEXT classes become detection candidates (C4
#: granularity mapping, frozen).
MANGA_TEXT_CLASSES = (1, 2)
MANGA_BUBBLE_CLASS = 0

#: The frozen word-to-block merge policy (T1.1.1 gate) is IMPORTED from the
#: docTR adapter above — this tuple keeps the shared constants referenced so
#: "imported, not copied" is enforced by the module itself (tests assert
#: identity with ``detection_doctr``).
MERGE_POLICY_CONSTANTS = (
    MERGE_VERTICAL_FACTOR,
    MERGE_MIN_TOLERANCE_PX,
    MERGE_HORIZONTAL_TOLERANCE_PX,
    MERGE_PAD_PX,
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class MangaDetectionProvider:
    """``DetectionProvider`` over a locally pinned manga-domain RT-DETR-v2."""

    weights_dir: Path
    device: str = "cpu"
    provider_id: str = PROVIDER_MANGA
    provider_type: str = "local-manga"
    model: str = f"manga/{MANGA_WEIGHTS_DIRNAME}"
    requirements: tuple[str, ...] = ("transformers", "torch")

    _engine: Any = field(default=None, init=False, repr=False)

    def detect(self, request: DetectionRequest) -> DetectionResult:
        started = time.perf_counter()
        self._validate_request(request)
        model, processor = self._engine_or_raise()
        rgb = self._frame_pixels(request)
        width, height = float(rgb.shape[1]), float(rgb.shape[0])
        boxes, n_bubble = _detect_text_boxes(
            model, processor, rgb, width, height
        )
        blocks = cluster_words_into_blocks(
            [(b[0], b[1], b[2], b[3]) for b in boxes],
            [b[4] for b in boxes],
            page_size=(width, height),
        )
        candidates = tuple(
            RegionCandidate(
                polygon=tuple(polygon),
                reading_order=index,
                confidence=confidence,
                provider_label=f"manga-{index}",
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
            options=(
                ("arch", "rt_detr_v2"),
                ("device", self.device),
                ("conf_threshold", str(MANGA_CONF_THRESHOLD)),
                ("bubble_class_dropped", str(n_bubble)),
            ),
            elapsed_ms=elapsed_ms,
        )

    # -- engine lifecycle ---------------------------------------------------

    def _engine_or_raise(self) -> tuple[Any, Any]:
        if self._engine is None:
            self._engine = _build_engine(self.weights_dir, self.device)
        return self._engine

    @staticmethod
    def _validate_request(request: DetectionRequest) -> None:
        """Pure-Python input gate: runs before any dependency is touched.

        Same production ``page_frame`` contract as the docTR adapter: a raw
        pixel buffer (rgb32 BGRA or rgb24), never an encoded file.
        """
        if not request.image_bytes:
            raise ProviderInputError(
                "no image bytes were supplied for detection",
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )
        if request.width <= 0 or request.height <= 0:
            raise ProviderInputError(
                f"invalid frame size {request.width}x{request.height}",
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )
        expected = request.width * request.height
        if len(request.image_bytes) not in (expected * 3, expected * 4):
            raise ProviderInputError(
                f"frame byte count {len(request.image_bytes)} does not match "
                f"{request.width}x{request.height} rgb32 or rgb24 pixels",
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )

    @staticmethod
    def _frame_pixels(request: DetectionRequest) -> Any:
        """Decode the frame buffer into an HxWx3 uint8 RGB array.

        Runs after the engine is built, so numpy — a hard torch/transformers
        dependency — is guaranteed present here.
        """
        numpy = _lazy_import("numpy", "detection")
        raw = numpy.frombuffer(request.image_bytes, dtype=numpy.uint8)
        expected = request.width * request.height
        if raw.size == expected * 4:  # rgb32: BGRA in memory, alpha forced 0xff
            bgra = raw.reshape(request.height, request.width, 4)
            return bgra[:, :, :3][:, :, ::-1].copy()
        # rgb24: frombuffer hands out a read-only view; the image processor
        # hands tensors to torch, so hand it a writable contiguous copy.
        return raw.reshape(request.height, request.width, 3).copy()


def _build_engine(weights_dir: Path, device: str) -> tuple[Any, Any]:
    """Load the pinned snapshot without touching the network.

    Check order matters and is part of the contract (mirrors the docTR
    adapter):

    1. the snapshot *directory* and each of its three files must exist —
       probed first with zero dependencies (no torch, no numpy);
    2. the heavy runtime must import (torch first, then transformers) — a
       machine that fetched weights but never installed the stack gets the
       typed dependency gap;
    3. the device must resolve;
    4. the SHA-256 of each file must match its pin — a corrupted or
       substituted artifact is ``PROVIDER_FAILED``, never a warning;
    5. ``from_pretrained(local dir, local_files_only=True)`` builds the
       processor and the model — the hub branch is never entered.
    """
    if not weights_dir.is_dir():
        raise ProviderNotConfigured(
            f"manga detector weights are not installed: directory {weights_dir} "
            f"is missing (place the pinned snapshot of {MANGA_HF_REPO} @ "
            f"{MANGA_HF_REVISION} there — {MANGA_MODEL_FILENAME} / "
            f"{MANGA_CONFIG_FILENAME} / {MANGA_PREPROCESSOR_FILENAME}, sha256 "
            f"pinned in src/infrastructure/providers/detection_manga.py; "
            f"weights are never downloaded at run time; if "
            f"NEWMANGA_DETECTOR_WEIGHTS still points at the docTR fast_base "
            f".pt file instead, set NEWMANGA_DETECTOR_BACKEND=doctr)",
            stage="detection",
        )
    pinned = (
        (MANGA_MODEL_FILENAME, MANGA_MODEL_SHA256),
        (MANGA_CONFIG_FILENAME, MANGA_CONFIG_SHA256),
        (MANGA_PREPROCESSOR_FILENAME, MANGA_PREPROCESSOR_SHA256),
    )
    for filename, _pin in pinned:
        candidate = weights_dir / filename
        if not candidate.is_file():
            raise ProviderNotConfigured(
                f"manga detector weights are not installed: {candidate} is "
                f"missing (the snapshot of {MANGA_HF_REPO} @ "
                f"{MANGA_HF_REVISION} needs all three files)",
                stage="detection",
            )
    torch = _lazy_import("torch", "detection")
    resolved = _resolve_device(torch, device)
    for filename, pin in pinned:
        actual = sha256_file(weights_dir / filename)
        if actual != pin:
            raise ProviderError(
                f"manga detector weights file {weights_dir / filename} has "
                f"sha256 {actual}, expected {pin}; refusing to run "
                f"unverified weights",
                stage="detection",
            )
    transformers = _lazy_import("transformers", "detection")
    try:
        processor = transformers.RTDetrImageProcessor.from_pretrained(
            str(weights_dir), local_files_only=True
        )
        model = transformers.RTDetrV2ForObjectDetection.from_pretrained(
            str(weights_dir), local_files_only=True
        )
        model.eval()
        if resolved == "cuda":
            model = model.cuda()
        return model, processor
    except (ProviderNotConfigured, ProviderDependencyMissing, ProviderError):
        raise
    except Exception as error:  # noqa: BLE001 - any model-build failure is typed
        raise ProviderError(
            f"manga detector engine failed to load from {weights_dir}: {error!r}",
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
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )
        return "cuda"
    if device == "cpu":
        return "cpu"
    raise ProviderInputError(
        f"unsupported detector device {device!r} (use cpu|cuda|auto)",
        provider_id=PROVIDER_MANGA,
        stage="detection",
    )


def _detect_text_boxes(
    model: Any, processor: Any, rgb: Any, width: float, height: float
) -> tuple[list[tuple[float, float, float, float, float]], int]:
    """Run one page through the pinned model; return (text_boxes, n_bubble).

    ``text_boxes`` is the union of the TEXT classes only, in absolute source
    pixels — the "word"-role input of the frozen production merge. The
    bubble class is counted (surfaced in ``options`` for audit), never kept.
    This is the C4 evaluation's inference sequence, verbatim:
    ``processor(...) -> model(...) -> post_process_object_detection`` with
    the source size as the resize-back target.
    """
    torch = _lazy_import("torch", "detection")
    try:
        inputs = processor(images=rgb, return_tensors="pt")
        inputs = {key: value.to(model.device) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        target_sizes = torch.tensor([[int(height), int(width)]])
        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=MANGA_CONF_THRESHOLD
        )[0]
    except (ProviderDependencyMissing, ProviderError):
        raise
    except Exception as error:  # noqa: BLE001 - inference failures are typed
        raise ProviderError(
            f"manga detection inference failed: {error!r}",
            stage="detection",
        ) from error
    try:
        scores = results["scores"].tolist()
        labels = results["labels"].tolist()
        boxes = results["boxes"].tolist()
    except Exception as error:  # noqa: BLE001 - malformed payloads are typed
        raise ProviderInvalidOutput(
            f"manga detector payload is malformed: {error!r}",
            provider_id=PROVIDER_MANGA,
            stage="detection",
        ) from error
    return _text_boxes_from_results(scores, labels, boxes, width, height)


def _text_boxes_from_results(
    scores: list[float],
    labels: list[int],
    boxes: list[list[float]],
    width: float,
    height: float,
) -> tuple[list[tuple[float, float, float, float, float]], int]:
    """Pure filter: keep TEXT classes, drop the bubble class, clip, validate.

    Returns (text_boxes, n_bubble_dropped). Degenerate boxes (post-clip
    empty) are skipped; a NaN geometry (±inf is clipped to finite bounds by
    the existing clip semantics) or an out-of-range confidence is a typed
    invalid output, never coerced.
    """
    text_boxes: list[tuple[float, float, float, float, float]] = []
    n_bubble = 0
    for score, label, box in zip(scores, labels, boxes):
        label_id = int(label)
        if label_id not in MANGA_TEXT_CLASSES:
            n_bubble += 1
            continue
        if len(box) != 4:
            raise ProviderInvalidOutput(
                f"manga detector box is not (x0, y0, x1, y1): {box!r}",
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )
        confidence = float(score)
        if not 0.0 <= confidence <= 1.0:
            raise ProviderInvalidOutput(
                f"manga detector confidence out of range: {confidence}",
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )
        x0 = min(max(float(box[0]), 0.0), width)
        y0 = min(max(float(box[1]), 0.0), height)
        x1 = min(max(float(box[2]), 0.0), width)
        y1 = min(max(float(box[3]), 0.0), height)
        if not (
            math.isfinite(x0)
            and math.isfinite(y0)
            and math.isfinite(x1)
            and math.isfinite(y1)
        ):
            # NaN survives min/max clipping (every comparison is False), so
            # it must be rejected BEFORE the degeneracy check below — a NaN
            # polygon is malformed model output, never a zero-area box to
            # silently skip (DSH r1 R9).
            raise ProviderInvalidOutput(
                f"manga detector box geometry is not finite: {box!r}",
                provider_id=PROVIDER_MANGA,
                stage="detection",
            )
        if x1 <= x0 or y1 <= y0:
            continue
        text_boxes.append((x0, y0, x1, y1, confidence))
    return text_boxes, n_bubble


def _lazy_import(module_name: str, stage: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"detector runtime {module_name!r} is not installed: {error}",
            provider_id=PROVIDER_MANGA,
            stage=stage,
        ) from error
