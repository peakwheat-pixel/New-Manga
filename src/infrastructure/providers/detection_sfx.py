"""Standalone SFX (sound-effect) detection adapter — chiqui7 ONNX (M2-SFX-PROD-1).

User ruling 2026-10-01 (M2-SFX-PROD-1, verbatim): "要做 / chiqui7 能用，不在乎 /
路线 A" — the chiqui7/yolo11-manga-seg weights are bundled for production use;
the Ultralytics AGPL-metadata vs HF MIT-tag dispute is accepted by that ruling
(license-evidence chain: ``verification/M2-SFX-DETECT-EVAL/license-evidence.md``).

Model: ``chiqui7/yolo11-manga-seg`` @ ``7f5f5c04`` (HF tag: MIT), the ONLY
surveyed candidate with a dedicated SFX class — ONNX metadata names
``{0: bubble, 1: panel, 2: sfx, 3: text}`` (M2-SFX-DETECT-EVAL, directional
evidence: sfx class 11/29 instances @0.5, ogkalu hard-blind partial
intersection 6/7). This provider produces **sfx-class candidates only**;
every other class is dropped (the class map is asserted against the ONNX
metadata at load, so a silent class-surface drift fails loudly instead of
mislabeling detections — the eval script's R8 discipline).

Inference caliber — this module replicates the evaluation pipeline
(``experiments/M2-SFX-DETECT/eval_sfx_mangabubble.py``, read-only blueprint)
line by line so the report's numbers transfer structurally:

- letterbox per the ONNX metadata ``imgsz`` (chiqui7 = 1024): aspect-preserving
  scale, PIL BILINEAR resize, **top-left paste** onto a 114-gray canvas (NOT
  the Ultralytics centered letterbox), /255, CHW;
- output0 ``(1, 40, N)``: rows are ``[xywh(4), cls_scores(4), mask(32)]``^T;
  class scores are POST-SIGMOID in this export (verified empirically in the
  eval: raw range 0-0.956, no activation applied); conf filter -> xywh -> xyxy
  -> **class-agnostic NMS IoU 0.7** (NOT class-aware) over ALL classes, then
  the sfx class is taken — the filter order matches the eval script exactly;
- coordinates map back by dividing by the letterbox scale (self-consistent
  with the top-left paste).

Registered deviations from the eval script (production hardening only; the
mapping arithmetic itself is untouched):

- the input is the production RAW pixel buffer (rgb24/rgb32, the same
  ``page_frame`` contract as the manga adapter), not a PIL-decoded file;
- mapped-back boxes are clipped to the page bounds and a non-finite geometry
  is a typed ``PROVIDER_INVALID_OUTPUT`` (the manga adapter's R9 discipline);
- a degenerate (empty) box after mapping is skipped;
- the conf threshold IS the harvest filter (eval harvested at 0.25 and flagged
  ``conf_ge_primary``; production freezes 0.5 — precision-first ruling, since
  the SfxPolicy default is SKIP and a false sfx label silently drops dialogue
  translation). Boxes between 0.25 and the threshold therefore neither
  surface nor join the NMS competition set; the threshold is env-overridable
  (``NEWMANGA_SFX_CONF_THRESHOLD``, default 0.5) and retuning is a new slice.

Fail-closed — the exact four disciplines of the manga/docTR adapters:

- **no run-time download**: the weights file is resolved by the assembly to a
  local path (default ``<data root>/models/detector/yolo11s-seg.onnx``,
  override ``NEWMANGA_SFX_WEIGHTS``); a missing file is
  ``PROVIDER_NOT_CONFIGURED`` with placement guidance, never a fetch;
- **supply-chain integrity**: the file is SHA-256-checked against the pinned
  value BEFORE any runtime import; a mismatch is ``PROVIDER_FAILED``;
- **no fabricated output**: anonymous ``sfx-<n>`` labels; the caller assigns
  ids (``ports.detection``); a page with no sfx yields ZERO candidates (the
  handler decides what that means for the whole page — this provider alone
  never invents a padding box);
- **lazy runtime**: onnxruntime/numpy/PIL import on first use — a machine
  without the stack still boots and fails typed at detect time.

Boundary: sfx candidates do NOT enter the frozen word-to-block MERGE_* dialogue
merge (that is the word-level dialogue caliber); they are block-level art-text
candidates flowing beside the manga candidates into region creation, where the
assembly dispatches the ``sfx-`` label prefix to ``RegionType.SFX`` and the
existing SfxPolicy gate takes over. The onnxruntime stack is deliberately the
LIGHTWEIGHT route (no torch) — CPU EP, 41 MB weights bundled (release-form
out-of-the-box per user ruling 3).

The parallel assembly form lives here too:
:class:`MangaSfxParallelDetectionProvider` composes the primary (manga) provider
with this sfx provider for the pipeline ``detect`` step without touching either
provider's behavior: manga candidates keep their reading order untouched, sfx
candidates are appended past the manga maximum, the composite reports the
primary's provenance identity (it is an assembly form, not a third provider),
and a TYPED sfx failure degrades safely — the manga chain (the product's core
detection path) lives on with the degradation recorded in the detect
provenance/options, never silently.
"""

from __future__ import annotations

import importlib
import math
import sys
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from infrastructure.providers.detection_manga import sha256_file
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
)

PROVIDER_SFX = "local-sfx"

#: The pinned weights identity (M2-SFX-DETECT-EVAL §3.1; HF revision
#: ``7f5f5c0464f2eeb57282f16da760eb8828a8716a``). The weights live on local /
#: gitignored paths only — never committed, never downloaded at run time.
SFX_HF_REPO = "chiqui7/yolo11-manga-seg"
SFX_HF_REVISION = "7f5f5c0464f2eeb57282f16da760eb8828a8716a"
SFX_WEIGHTS_FILENAME = "yolo11s-seg.onnx"
SFX_WEIGHTS_SHA256 = (
    "d87389af4350954143a216bcfe40fd2ad93312cb136534e6073c9c740d98b646"
)

#: Frozen conf threshold (user ruling: precision-first — SfxPolicy default is
#: SKIP, a false sfx label silently drops dialogue translation). Env
#: ``NEWMANGA_SFX_CONF_THRESHOLD`` may override the default; retuning is a
#: new slice with re-run evidence.
SFX_CONF_THRESHOLD = 0.5

#: Class-agnostic NMS IoU — the eval caliber, frozen.
SFX_NMS_IOU = 0.7

#: Letterbox canvas gray + the metadata imgsz fallback (chiqui7's recorded
#: imgsz; the metadata value wins when present).
SFX_LETTERBOX_GRAY = 114
SFX_DEFAULT_IMGSZ = 1024

#: ONNX metadata class surface (asserted at load; drift fails loudly — the
#: eval script's R8 discipline). sfx = class 2.
SFX_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
SFX_CLASS_ID = 2

#: Anonymous label prefix (``ports.detection`` has no type slot — contract
#: zero-change ruling; the assembly dispatches this prefix to
#: ``RegionType.SFX``).
SFX_LABEL_PREFIX = "sfx-"


@dataclass
class SfxDetectionProvider:
    """``DetectionProvider`` over a locally pinned chiqui7 ONNX (sfx class only)."""

    weights_path: Path
    conf_threshold: float = SFX_CONF_THRESHOLD
    provider_id: str = PROVIDER_SFX
    provider_type: str = "local-sfx"
    model: str = f"sfx/{SFX_WEIGHTS_FILENAME}"
    requirements: tuple[str, ...] = ("onnxruntime", "numpy", "PIL")

    _engine: Any = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        if not isinstance(self.conf_threshold, (int, float)) or not (
            0.0 < float(self.conf_threshold) <= 1.0
        ):
            raise ValueError(
                f"sfx conf threshold must be in (0, 1], got {self.conf_threshold!r}"
            )
        self.conf_threshold = float(self.conf_threshold)

    def detect(self, request: DetectionRequest) -> DetectionResult:
        started = time.perf_counter()
        self._validate_request(request)
        session, imgsz = self._engine_or_raise()
        numpy = _lazy_import("numpy", "detection")
        rgb = self._frame_pixels(request)
        inp, scale = _letterbox(numpy, rgb, imgsz)
        boxes = _sfx_boxes(
            session,
            inp,
            scale,
            self.conf_threshold,
            page_w=float(rgb.shape[1]),
            page_h=float(rgb.shape[0]),
        )
        candidates = tuple(
            RegionCandidate(
                polygon=((x0, y0), (x1, y0), (x1, y1), (x0, y1)),
                reading_order=index,
                confidence=confidence,
                provider_label=f"{SFX_LABEL_PREFIX}{index}",
            )
            for index, (x0, y0, x1, y1, confidence) in enumerate(boxes, start=1)
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
                ("arch", "yolo11s_seg_onnx"),
                ("device", "cpu"),
                ("conf_threshold", str(self.conf_threshold)),
                ("nms_iou", str(SFX_NMS_IOU)),
                ("imgsz", str(imgsz)),
                ("class_filter", "sfx"),
            ),
            elapsed_ms=elapsed_ms,
        )

    # -- engine lifecycle ---------------------------------------------------

    def _engine_or_raise(self) -> tuple[Any, int]:
        if self._engine is None:
            self._engine = _build_engine(self.weights_path)
        return self._engine

    @staticmethod
    def _validate_request(request: DetectionRequest) -> None:
        """Pure-Python input gate: runs before any dependency is touched.

        Same production ``page_frame`` contract as the manga adapter: a raw
        pixel buffer (rgb32 BGRA or rgb24), never an encoded file.
        """
        if not request.image_bytes:
            raise ProviderInputError(
                "no image bytes were supplied for sfx detection",
                provider_id=PROVIDER_SFX,
                stage="detection",
            )
        if request.width <= 0 or request.height <= 0:
            raise ProviderInputError(
                f"invalid frame size {request.width}x{request.height}",
                provider_id=PROVIDER_SFX,
                stage="detection",
            )
        expected = request.width * request.height
        if len(request.image_bytes) not in (expected * 3, expected * 4):
            raise ProviderInputError(
                f"frame byte count {len(request.image_bytes)} does not match "
                f"{request.width}x{request.height} rgb32 or rgb24 pixels",
                provider_id=PROVIDER_SFX,
                stage="detection",
            )

    @staticmethod
    def _frame_pixels(request: DetectionRequest) -> Any:
        """Decode the frame buffer into an HxWx3 uint8 RGB array (manga semantics)."""
        numpy = _lazy_import("numpy", "detection")
        raw = numpy.frombuffer(request.image_bytes, dtype=numpy.uint8)
        expected = request.width * request.height
        if raw.size == expected * 4:  # rgb32: BGRA in memory, alpha forced 0xff
            bgra = raw.reshape(request.height, request.width, 4)
            return bgra[:, :, :3][:, :, ::-1].copy()
        # rgb24: hand downstream ops a writable contiguous copy (manga semantics).
        return raw.reshape(request.height, request.width, 3).copy()


def _build_engine(weights_path: Path) -> tuple[Any, int]:
    """Load the pinned ONNX without touching the network. Check order matters:

    1. the weights *file* must exist — probed first with zero dependencies;
    2. its SHA-256 must match the pin — verified BEFORE any runtime import, so
       a corrupted/substituted artifact is ``PROVIDER_FAILED`` even on a
       machine that never installed onnxruntime;
    3. onnxruntime must import — the typed dependency gap otherwise;
    4. the session builds (CPU EP — the lightweight-stack ruling);
    5. the metadata ``names`` must equal the asserted class map (R8 discipline)
       and the metadata ``imgsz`` (when present) drives the letterbox size.
    """
    if not weights_path.is_file():
        raise ProviderNotConfigured(
            f"sfx detector weights are not installed: file {weights_path} is "
            f"missing (place the pinned ONNX export of {SFX_HF_REPO} @ "
            f"{SFX_HF_REVISION[:8]} there — {SFX_WEIGHTS_FILENAME}, sha256 "
            f"pinned in src/infrastructure/providers/detection_sfx.py; "
            f"weights are never downloaded at run time; or point "
            f"NEWMANGA_SFX_WEIGHTS at the file, or set "
            f"NEWMANGA_SFX_DETECTION=off to skip sfx detection)",
            stage="detection",
        )
    actual = sha256_file(weights_path)
    if actual != SFX_WEIGHTS_SHA256:
        raise ProviderError(
            f"sfx detector weights file {weights_path} has sha256 {actual}, "
            f"expected {SFX_WEIGHTS_SHA256}; refusing to run unverified weights",
            stage="detection",
        )
    onnxruntime = _lazy_import("onnxruntime", "detection")
    try:
        session = onnxruntime.InferenceSession(
            str(weights_path), providers=["CPUExecutionProvider"]
        )
    except Exception as error:  # noqa: BLE001 - any session-build failure is typed
        raise ProviderError(
            f"sfx detector engine failed to load from {weights_path}: {error!r}",
            stage="detection",
        ) from error
    meta = session.get_modelmeta().custom_metadata_map
    names_raw = meta.get("names", "")
    parsed = _parse_names_metadata(names_raw)
    if parsed != {str(key): value for key, value in SFX_CLASS_MAP.items()}:
        raise ProviderInvalidOutput(
            f"sfx detector class surface drift: ONNX metadata names "
            f"{names_raw!r} != expected {SFX_CLASS_MAP!r}; refusing to "
            f"mislabel detections",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )
    return session, _parse_imgsz(meta.get("imgsz"))


def _parse_names_metadata(raw: str) -> dict[str, str]:
    """Parse the ONNX metadata ``names`` string (eval-script parse, verbatim).

    A missing or malformed ``names`` is a typed invalid output — the class
    assertion is the load-time gate, never a silent pass.
    """
    if not raw:
        raise ProviderInvalidOutput(
            "sfx detector ONNX metadata carries no 'names' entry; the class "
            "surface cannot be asserted",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )
    try:
        out: dict[str, str] = {}
        for part in raw.strip("{}").split(","):
            key, value = part.split(":")
            out[key.strip().strip("'")] = value.strip().strip("'")
    except ValueError as error:
        raise ProviderInvalidOutput(
            f"sfx detector ONNX metadata 'names' is malformed: {raw!r} "
            f"({error!r})",
            provider_id=PROVIDER_SFX,
            stage="detection",
        ) from error
    return out


def _parse_imgsz(raw: str | None) -> int:
    """Metadata imgsz wins when parseable; otherwise the eval's 1024.

    A missing/unparseable imgsz only degrades letterbox fidelity (recorded in
    the detect options by the caller), it cannot mislabel a class — hence a
    default instead of a failure (unlike the ``names`` gate above).
    """
    if raw:
        try:
            return int(raw)
        except ValueError:
            pass
    return SFX_DEFAULT_IMGSZ


# ---------------------------------------------------------------------------
# Inference caliber (eval-script blueprint — line-aligned, see module docstring)
# ---------------------------------------------------------------------------


def _letterbox(numpy: Any, rgb: Any, size: int) -> tuple[Any, float]:
    """Aspect-preserving resize + TOP-LEFT paste onto a 114-gray canvas.

    Eval blueprint: ``min(size/w, size/h)`` scale, PIL BILINEAR (NOT cv2),
    rounded target size, paste at (0, 0) (NOT centered), /255 float32, CHW.
    Returns (input tensor, scale) — the scale is the ONLY mapping constant
    (top-left paste <-> divide by scale, self-consistent).
    """
    height, width = rgb.shape[:2]
    scale = min(size / width, size / height)
    new_w, new_h = int(round(width * scale)), int(round(height * scale))
    pil = _lazy_import("PIL", "detection")
    image = pil.Image.fromarray(rgb).resize((new_w, new_h), pil.Image.BILINEAR)
    canvas = pil.Image.new("RGB", (size, size), (114, 114, 114))
    canvas.paste(image, (0, 0))
    arr = numpy.asarray(canvas, dtype=numpy.float32) / 255.0
    return numpy.ascontiguousarray(arr.transpose(2, 0, 1)[None]), scale


def _sfx_boxes(
    session: Any,
    inp: Any,
    scale: float,
    conf_threshold: float,
    *,
    page_w: float,
    page_h: float,
) -> list[tuple[float, float, float, float, float]]:
    """Run one letterboxed page; return sfx-class boxes in source pixels.

    The eval sequence, verbatim: conf filter (all classes) -> xywh -> xyxy ->
    class-agnostic NMS IoU 0.7 over ALL classes -> take the sfx class only ->
    map back by /scale. Keeping the NMS competition all-class is load-bearing:
    filtering to sfx BEFORE NMS would change which boxes survive.
    """
    out = session.run(None, {"images": inp})[0]  # (1, 40, N)
    preds = out[0].T  # (N, 40)
    boxes_xywh = preds[:, :4]
    # Post-sigmoid in this export (eval-verified empirically, no activation).
    cls_scores = preds[:, 4:8]
    cls_ids = cls_scores.argmax(axis=1)
    confs = cls_scores.max(axis=1)
    numpy = _lazy_import("numpy", "detection")
    cand: list[tuple[list[float], float, int]] = []
    for i in numpy.where(confs >= conf_threshold)[0]:
        x, y, w, h = boxes_xywh[i]
        cand.append(
            (
                [x - w / 2, y - h / 2, x + w / 2, y + h / 2],
                float(confs[i]),
                int(cls_ids[i]),
            )
        )
    keep = _nms(
        [entry[0] for entry in cand],
        numpy.array([entry[1] for entry in cand]),
        SFX_NMS_IOU,
    )
    boxes: list[tuple[float, float, float, float, float]] = []
    for i in keep:
        box, confidence, cls_id = cand[i]
        if cls_id != SFX_CLASS_ID:
            continue
        if not 0.0 <= confidence <= 1.0:
            raise ProviderInvalidOutput(
                f"sfx detector confidence out of range: {confidence}",
                provider_id=PROVIDER_SFX,
                stage="detection",
            )
        x0, y0, x1, y1 = _map_back(box, scale, page_w=page_w, page_h=page_h)
        if x1 <= x0 or y1 <= y0:
            continue  # degenerate after mapping: no polygon to create
        boxes.append((x0, y0, x1, y1, confidence))
    return boxes


def _nms(boxes: list[list[float]], scores: Any, iou_thr: float) -> list[int]:
    """Greedy NMS; eval-script algorithm verbatim (``np.argsort`` descending)."""
    numpy = _lazy_import("numpy", "detection")
    order = numpy.argsort(scores)[::-1]
    keep: list[int] = []
    for i in order:
        if all(_iou(boxes[i], boxes[k]) < iou_thr for k in keep):
            keep.append(int(i))
    return keep


def _map_back(
    box: list[float], scale: float, *, page_w: float, page_h: float
) -> tuple[float, float, float, float]:
    """Letterboxed pixels -> source pixels (/scale), clipped to the page.

    The clip is production hardening (manga-adapter semantics) — the mapping
    arithmetic itself is the eval's verbatim ``/scale``. NaN survives
    min/max clipping, so it is rejected BEFORE the degeneracy skip (R9).
    """
    x0, y0, x1, y1 = (float(value) / scale for value in box)
    if not all(math.isfinite(value) for value in (x0, y0, x1, y1)):
        raise ProviderInvalidOutput(
            f"sfx detector box geometry is not finite after mapping: "
            f"{box!r} (scale={scale})",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )
    return (
        min(max(x0, 0.0), page_w),
        min(max(y0, 0.0), page_h),
        min(max(x1, 0.0), page_w),
        min(max(y1, 0.0), page_h),
    )


def _iou(a: list[float], b: list[float]) -> float:
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    if ix1 <= ix0 or iy1 <= iy0:
        return 0.0
    inter = (ix1 - ix0) * (iy1 - iy0)
    area_a = (a[2] - a[0]) * (a[3] - a[1])
    area_b = (b[2] - b[0]) * (b[3] - b[1])
    return inter / (area_a + area_b - inter)


def _lazy_import(module_name: str, stage: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"sfx detector runtime {module_name!r} is not installed: {error}",
            provider_id=PROVIDER_SFX,
            stage=stage,
        ) from error


# ---------------------------------------------------------------------------
# Parallel assembly form (M2-SFX-PROD-1 proxy ruling 1)
# ---------------------------------------------------------------------------


@dataclass
class MangaSfxParallelDetectionProvider:
    """The primary (manga) provider with the sfx provider running beside it.

    Assembly form, NOT a third provider: provenance identity (provider_id /
    provider_type / model) stays the primary's verbatim so every manga-face
    consumer sees the same fields; the sfx participation is carried in the
    ``options`` tail instead.

    - candidates: the primary's verbatim (reading orders untouched — the
      manga word/block sequence is load-bearing), then the sfx candidates
      appended with reading orders offset past the primary's maximum;
    - the sfx provider's TYPED failures (``ProviderError`` family) degrade
      safely: the manga chain is the product's core detection path, and the
      safe direction for a missing/broken OPTIONAL detector is "fall back to
      the pre-SFX status quo" — the degradation is recorded in the detect
      options (audit-visible) plus one stderr line, never silent. Non-typed
      exceptions (programming errors) propagate untouched;
    - zero primary candidates + zero sfx candidates stays zero candidates —
      the handler's ``INVALID_INPUT`` semantics are unchanged.
    """

    primary: Any
    sfx: Any

    @property
    def provider_id(self) -> str:
        return self.primary.provider_id

    @property
    def provider_type(self) -> str:
        return self.primary.provider_type

    @property
    def model(self) -> str:
        return self.primary.model

    def detect(self, request: DetectionRequest) -> DetectionResult:
        result = self.primary.detect(request)
        try:
            sfx_result = self.sfx.detect(request)
        except ProviderError as error:
            print(
                "WARNING: sfx detection degraded; manga candidates continue "
                f"({error})",
                file=sys.stderr,
            )
            return replace(
                result,
                options=result.options
                + (("sfx_provider_status", f"degraded: {error.error_code}"),),
            )
        offset = max(
            (candidate.reading_order for candidate in result.candidates),
            default=0,
        )
        sfx_candidates = tuple(
            RegionCandidate(
                polygon=candidate.polygon,
                reading_order=offset + candidate.reading_order,
                confidence=candidate.confidence,
                provider_label=candidate.provider_label,
            )
            for candidate in sfx_result.candidates
        )
        primary_elapsed = result.elapsed_ms or 0
        sfx_elapsed = sfx_result.elapsed_ms or 0
        return replace(
            result,
            candidates=result.candidates + sfx_candidates,
            options=result.options
            + (
                ("sfx_provider", sfx_result.provider_id),
                ("sfx_candidates", str(len(sfx_candidates))),
                ("sfx_conf_threshold", str(self.sfx.conf_threshold)),
            ),
            elapsed_ms=(primary_elapsed + sfx_elapsed) or None,
        )
