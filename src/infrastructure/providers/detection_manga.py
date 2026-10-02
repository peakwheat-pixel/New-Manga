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

Webtoon long-strip tiling (M2-DETECT-WEBTOON-TILING): the whole-page path
above feeds every page through the ``RTDetrImageProcessor`` (size 640x640,
no letterbox), which anisotropically crushes a 690x62133 webtoon strip
~97x vertically — the targets vanish and the model scores collapse below
the production threshold (raw max 0.204 on K01, 0 regions). The frozen
diagnosis (``verification/M2-DETECT-WEBTOON-DIAG/``) proved the repair:
the SAME weights, threshold and post-processing on 1024x1024 tiles with a
128 px overlap recover 193 pre-merge text boxes on that same page (NMS
dedup evidence: 30/33 removals in the overlap bands, mean IoU 0.848).
The tiled path therefore triggers on aspect ratio — ``height/max(width,1)``
strictly above ``TILING_TRIGGER_RATIO`` (4.0 separates the diagnosed long
strips, h/w 30.7-90.0, from every normal page in the suite, h/w <= 1.41,
with a ~20x margin) — and cuts the page into overlapping square tiles
(right/bottom-padded with constant 114 gray to the square, the DIAG
experiment's exact geometry), runs the per-tile production inference
sequence on the SAME loaded engine (never a per-tile rebuild), maps each
text box back to page coordinates (+tile origin, clipped to the tile
bounds by the shared pure filter), and de-duplicates cross-tile repeats
with a confidence-ordered greedy NMS (IoU strictly above the threshold
drops; IoU == threshold is kept). The output is the same absolute-page
``text_boxes`` the whole-page path feeds into the frozen production merge
— the DetectionRequest/Response contract is untouched. The parameters are
env-configurable (``NEWMANGA_DETECTOR_TILING_*``, the SFX conf-threshold
env precedent): an illegal value fails fast, never a silent default, and
a page that does not trigger keeps the byte-identical whole-page behavior.
"""

from __future__ import annotations

import hashlib
import importlib
import math
import os
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


# -- webtoon long-strip tiling (M2-DETECT-WEBTOON-TILING) -------------------

#: Tiling defaults = the DIAG-frozen experiment values
#: (``verification/M2-DETECT-WEBTOON-DIAG/probe-results.json``,
#: ``pages.K01.tile_experiment``): 1024 px square tiles with a 128 px
#: vertical overlap and a page-level NMS at IoU 0.5 recovered 193 pre-merge
#: text boxes where the whole-page path scored 0. Changing them is a new
#: slice with re-run evidence.
TILING_TILE_SIZE = 1024
TILING_OVERLAP_PX = 128
TILING_NMS_IOU = 0.5

#: The trigger is the Owner ruling recorded in the task doc: aspect ratio
#: ``height/max(width, 1)`` STRICTLY above 4.0. The DIAG data fixes the
#: margins: the diagnosed long strips sit at h/w 30.7 (K02) / 40.8 (K04) /
#: 90.0 (K01), while every normal page measured (BJ02 2946x4167, K19
#: 1200x1660) sits at h/w <= 1.41 — a ~20x safety margin on both sides.
TILING_TRIGGER_RATIO = 4.0

#: Square-input padding: a crop narrower/shorter than the tile is padded
#: with constant 114 gray (the DIAG experiment's convention; no upstream
#: citation, carries no text by construction, and its pad bands produced
#: zero detections across all 70 K01 tiles).
TILING_PAD_VALUE = 114

#: The env channel (the ``NEWMANGA_SFX_CONF_THRESHOLD`` precedent): absent
#: variables mean the frozen defaults above; a present-but-illegal value is
#: a fail-fast ``ValueError`` naming the variable — never a silent default.
TILING_ENV_TILE_SIZE = "NEWMANGA_DETECTOR_TILING_TILE_SIZE"
TILING_ENV_OVERLAP = "NEWMANGA_DETECTOR_TILING_OVERLAP"
TILING_ENV_NMS_IOU = "NEWMANGA_DETECTOR_TILING_NMS_IOU"
TILING_ENV_TRIGGER_RATIO = "NEWMANGA_DETECTOR_TILING_TRIGGER_RATIO"


@dataclass(frozen=True)
class TilingConfig:
    """The resolved tiling parameters of one ``detect`` call."""

    trigger_ratio: float = TILING_TRIGGER_RATIO
    tile_size: int = TILING_TILE_SIZE
    overlap: int = TILING_OVERLAP_PX
    nms_iou: float = TILING_NMS_IOU


def _tiling_config() -> TilingConfig:
    """Read the tiling configuration: env overrides or the frozen defaults.

    Fail-fast semantics (the SFX conf env precedent): a non-numeric or
    out-of-range value raises ``ValueError`` naming the env variable. The
    overlap is validated against the EFFECTIVE tile size, so a custom tile
    size below the default overlap must come with its own overlap — the
    error names both variables.

    M2-DETECTION-HYGIENE (TILING r1 R3): an empty or whitespace-only value
    is ALSO rejected (never-silent-default) — ``if raw is not None`` lets
    ``float("")`` fail into the same typed path instead of silently
    falling back to the default.

    M2-DETECTION-HYGIENE (TILING r1 R1): the config is read on EVERY
    ``detect`` call (before the trigger test, which needs the trigger
    ratio), so an ILLEGAL env value fails fast for ordinary pages too —
    the same provider-level semantics as ``NEWMANGA_SFX_CONF_THRESHOLD``.
    The "ordinary pages unchanged" claim is therefore scoped to: env
    unset OR set to legal values.
    """
    raw = os.environ.get(TILING_ENV_TRIGGER_RATIO)
    trigger_ratio = float(TILING_TRIGGER_RATIO)
    if raw is not None:
        try:
            trigger_ratio = float(raw.strip())
        except ValueError as error:
            raise ValueError(
                f"{TILING_ENV_TRIGGER_RATIO}: not a number: {raw!r}"
            ) from error
        if not trigger_ratio > 0.0:
            raise ValueError(
                f"{TILING_ENV_TRIGGER_RATIO}: must be > 0, got {trigger_ratio!r}"
            )

    raw = os.environ.get(TILING_ENV_TILE_SIZE)
    tile_size = TILING_TILE_SIZE
    if raw is not None:
        try:
            tile_size = int(raw.strip())
        except ValueError as error:
            raise ValueError(
                f"{TILING_ENV_TILE_SIZE}: not an integer: {raw!r}"
            ) from error
        if tile_size <= 0:
            raise ValueError(
                f"{TILING_ENV_TILE_SIZE}: must be a positive integer, got {tile_size!r}"
            )

    raw = os.environ.get(TILING_ENV_OVERLAP)
    overlap = TILING_OVERLAP_PX
    if raw is not None:
        try:
            overlap = int(raw.strip())
        except ValueError as error:
            raise ValueError(
                f"{TILING_ENV_OVERLAP}: not an integer: {raw!r}"
            ) from error
    if not 0 <= overlap < tile_size:
        raise ValueError(
            f"{TILING_ENV_OVERLAP}: must be in [0, tile_size) — got {overlap!r} "
            f"with {TILING_ENV_TILE_SIZE}={tile_size}"
        )

    raw = os.environ.get(TILING_ENV_NMS_IOU)
    nms_iou = float(TILING_NMS_IOU)
    if raw is not None:
        try:
            nms_iou = float(raw.strip())
        except ValueError as error:
            raise ValueError(
                f"{TILING_ENV_NMS_IOU}: not a number: {raw!r}"
            ) from error
        if not 0.0 < nms_iou < 1.0:
            raise ValueError(
                f"{TILING_ENV_NMS_IOU}: must be in (0, 1), got {nms_iou!r}"
            )

    return TilingConfig(
        trigger_ratio=trigger_ratio,
        tile_size=tile_size,
        overlap=overlap,
        nms_iou=nms_iou,
    )


def _tiling_triggered(width: float, height: float, trigger_ratio: float) -> bool:
    """True for a webtoon long-strip: ``height/max(width, 1)`` STRICTLY
    above the ratio. The boundary itself (h/w == ratio) stays untiled —
    strictness keeps the trigger from creeping into tall-but-normal pages.
    """
    return height / max(width, 1.0) > trigger_ratio


def _tiling_tiles(
    width: float, height: float, tile_size: int, overlap: int
) -> list[tuple[float, float, float, float]]:
    """The overlapping tile grid as ``(x0, y0, x1, y1)`` page-space rects.

    Per axis the origins step by ``tile_size - overlap`` until a tile
    reaches past the page end, and the last tile is clipped to the page —
    exactly the DIAG stepping (tile 1024 / overlap 128 on the 690x62133
    K01 page yields origins 0, 896, ..., 61824 with a 309 px tail = 70
    tiles). ``tile_size > overlap`` is enforced by ``_tiling_config``, so
    the step is always positive and coverage always holds (each next tile
    starts inside the previous one).
    """
    step = tile_size - overlap

    def origins(total: float) -> list[float]:
        found = [0.0]
        while found[-1] + tile_size < total:
            found.append(found[-1] + step)
        return found

    return [
        (x0, y0, min(x0 + tile_size, width), min(y0 + tile_size, height))
        for y0 in origins(height)
        for x0 in origins(width)
    ]


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
        tiling_config = _tiling_config()
        if _tiling_triggered(width, height, tiling_config.trigger_ratio):
            # webtoon long-strip: tile -> per-tile production inference ->
            # remap -> cross-tile NMS (the DIAG repair; same engine, same
            # threshold, same post-processing as the whole-page path)
            boxes, n_bubble = _detect_text_boxes_tiled(
                model, processor, rgb, width, height, tiling_config
            )
            tiling_options: tuple[tuple[str, str], ...] = (
                ("tiling", "on"),
                (
                    "tiling_tiles",
                    str(
                        len(
                            _tiling_tiles(
                                width,
                                height,
                                tiling_config.tile_size,
                                tiling_config.overlap,
                            )
                        )
                    ),
                ),
            )
        else:
            # normal page: the C4 evaluation's inference sequence, verbatim
            boxes, n_bubble = _detect_text_boxes(
                model, processor, rgb, width, height
            )
            tiling_options = (("tiling", "off"),)
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
                ("text_boxes_pre_merge", str(len(boxes))),
                *tiling_options,
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
    """Run one WHOLE page through the pinned model; return (text_boxes, n_bubble).

    This is the normal-page path (h/w <= trigger ratio) and it is kept
    byte-identical to the pre-tiling implementation: pages that do not
    trigger the tiling gate behave exactly as before M2-DETECT-WEBTOON-TILING
    (long strips go through ``_detect_text_boxes_tiled`` instead).

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


def _pad_tile(crop: Any, tile_size: int) -> Any:
    """Right/bottom-pad a crop to the square ``tile_size`` with constant
    gray (the DIAG experiment's square-input convention; the pad carries no
    text by construction and produced zero detections there).
    """
    numpy = _lazy_import("numpy", "detection")
    tile = numpy.full(
        (tile_size, tile_size, 3), TILING_PAD_VALUE, dtype=numpy.uint8
    )
    tile[: crop.shape[0], : crop.shape[1]] = crop
    return tile


def _tile_inference(
    model: Any, processor: Any, tile_rgb: Any, threshold: float
) -> tuple[list[float], list[int], list[list[float]]]:
    """One production inference sequence on one tile.

    Identical to the whole-page path (``processor -> model ->
    post_process_object_detection``), with the PADDED tile as the
    resize-back target — the raw ``(scores, labels, boxes)`` payload in
    padded tile-local pixels. Text filtering, clipping and validation stay
    in the shared pure filter; the threshold is a parameter so the
    qualification can measure a second curve point without touching the
    production default.
    """
    torch = _lazy_import("torch", "detection")
    try:
        inputs = processor(images=tile_rgb, return_tensors="pt")
        inputs = {key: value.to(model.device) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        target_sizes = torch.tensor(
            [[int(tile_rgb.shape[0]), int(tile_rgb.shape[1])]]
        )
        results = processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=threshold
        )[0]
    except (ProviderDependencyMissing, ProviderError):
        raise
    except Exception as error:  # noqa: BLE001 - inference failures are typed
        raise ProviderError(
            f"manga detection tile inference failed: {error!r}",
            stage="detection",
        ) from error
    try:
        return (
            results["scores"].tolist(),
            results["labels"].tolist(),
            results["boxes"].tolist(),
        )
    except Exception as error:  # noqa: BLE001 - malformed payloads are typed
        raise ProviderInvalidOutput(
            f"manga detector payload is malformed: {error!r}",
            provider_id=PROVIDER_MANGA,
            stage="detection",
        ) from error


def _iou(
    a: tuple[float, float, float, float, float],
    b: tuple[float, float, float, float, float],
) -> float:
    """Intersection-over-union of two ``(x0, y0, x1, y1, conf)`` boxes."""
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    iw, ih = max(0.0, ix1 - ix0), max(0.0, iy1 - iy0)
    intersection = iw * ih
    if intersection <= 0.0:
        return 0.0
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return intersection / (area_a + area_b - intersection)


def _greedy_nms(
    boxes: list[tuple[float, float, float, float, float]], iou_threshold: float
) -> list[tuple[float, float, float, float, float]]:
    """Confidence-ordered greedy NMS over page-global boxes.

    A box is dropped when its best IoU against the already-kept set is
    STRICTLY above the threshold (IoU == threshold is kept) — the DIAG
    dedup semantics, which measured 30/33 removals inside the overlap
    bands with a mean removal IoU of 0.848. Pure and deterministic.
    """
    kept: list[tuple[float, float, float, float, float]] = []
    for box in sorted(boxes, key=lambda b: b[4], reverse=True):
        if any(_iou(box, keeper) > iou_threshold for keeper in kept):
            continue
        kept.append(box)
    return kept


def _detect_text_boxes_tiled(
    model: Any,
    processor: Any,
    rgb: Any,
    width: float,
    height: float,
    config: TilingConfig,
    threshold: float = MANGA_CONF_THRESHOLD,
) -> tuple[list[tuple[float, float, float, float, float]], int]:
    """The webtoon long-strip path: tile, infer, remap, de-duplicate.

    The DIAG repair (M2-DETECT-WEBTOON-TILING), on the SAME loaded engine —
    the model/processor pair is never rebuilt per tile:

    1. cut the page into overlapping tiles (``_tiling_tiles``, the DIAG
       stepping) and pad each crop to the square tile size (right/bottom,
       constant gray);
    2. run the production inference sequence per tile (``_tile_inference``,
       production threshold by default);
    3. filter through the SHARED pure filter (``_text_boxes_from_results``)
       with the tile's real crop size — that clip to the tile bounds is the
       documented pad-band safety (the DIAG pad bands produced zero
       detections, so clipping cannot lose a real box);
    4. remap each box to page coordinates by adding the tile origin;
    5. de-duplicate cross-tile repeats with the confidence-ordered greedy
       NMS (IoU strictly above ``config.nms_iou`` drops).

    Returns ``(text_boxes, n_bubble)`` in absolute page pixels — the exact
    whole-page contract, so the frozen production merge and the
    DetectionResult contract are untouched.
    """
    tiles = _tiling_tiles(width, height, config.tile_size, config.overlap)
    page_boxes: list[tuple[float, float, float, float, float]] = []
    n_bubble = 0
    for (x0, y0, x1, y1) in tiles:
        crop = rgb[int(y0) : int(y1), int(x0) : int(x1)]
        crop_h, crop_w = int(crop.shape[0]), int(crop.shape[1])
        scores, labels, boxes = _tile_inference(
            model, processor, _pad_tile(crop, config.tile_size), threshold
        )
        tile_boxes, tile_bubble = _text_boxes_from_results(
            scores, labels, boxes, float(crop_w), float(crop_h)
        )
        n_bubble += tile_bubble
        for (bx0, by0, bx1, by1, confidence) in tile_boxes:
            # tile-local -> page-global (+origin); the boxes are already
            # clipped to the tile bounds by the shared filter
            page_boxes.append(
                (bx0 + x0, by0 + y0, bx1 + x0, by1 + y0, confidence)
            )
    return _greedy_nms(page_boxes, config.nms_iou), n_bubble


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
