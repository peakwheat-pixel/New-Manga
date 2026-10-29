"""Local manga-domain RT-DETR-v2 text detection over ONNX Runtime (CORE-SLIM-2).

The torch/transformers implementation lives unchanged in
``detection_manga.py`` (optional fallback: ``NEWMANGA_DETECTOR_BACKEND=torch``).
This adapter is the DEFAULT production path: the pinned
``ogkalu/comic-text-and-bubble-detector`` RT-DETR-v2 checkpoint exported to a
fixed-shape ONNX graph (opset 17, input 640x640) and executed through
``onnxruntime-directml`` (DirectML by default when the wheel exposes it).

Why the output is contract-compatible: the INFER-BASELINE-EP-1 measured the
exported graph against the torch model on 10 pages (logits maxAbs 1.46e-4,
boxes maxAbs 2.10e-5, text-box counts identical 10/10). This adapter therefore
reuses the SAME pure post-filters and merge policy as the torch adapter —
imported, never copied — so the region contract (text boxes in page-global
pixels → frozen word-to-block merge → anonymous ``manga-<n>`` candidates)
cannot drift:

- ``_text_boxes_from_results`` keeps TEXT classes (1, 2), drops the bubble
  class (0), clips to the page and rejects non-finite geometry;
- ``cluster_words_into_blocks`` is the frozen T1.1.1 merge;
- the webtoon tiling path (1024 px tiles, 128 px overlap, cross-tile NMS) is
  reused with the same constants and the same pad value.

Pre/post-processing mirrors the exported graph exactly (the checkpoint's
``preprocessor_config.json``: resize 640x640 BILINEAR, rescale 1/255,
``do_normalize: false``). RT-DETR emits per-query logits (sigmoid space) and
normalised cxcywh boxes; both are turned into absolute xyxy here, before the
shared filter runs.

Fail-closed rules (the same four disciplines as the torch adapter):

- no run-time download; a missing file is ``PROVIDER_NOT_CONFIGURED``;
- the ONNX file's SHA-256 is pinned and verified before the session is built;
- no fabricated output: a page with no text yields zero candidates;
- missing ORT is the typed ``PROVIDER_DEPENDENCY_MISSING`` (lazy import).
"""

from __future__ import annotations

import hashlib
import importlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from infrastructure.providers.detection_doctr import cluster_words_into_blocks
from infrastructure.providers.detection_manga import (
    MANGA_CONF_THRESHOLD,
    MANGA_TEXT_CLASSES,
    PROVIDER_MANGA,
    MangaDetectionProvider,
    TilingConfig,
    _greedy_nms,
    _pad_tile,
    _text_boxes_from_results,
    _tiling_config,
    _tiling_tiles,
    _tiling_trigger_ratio,
    _tiling_triggered,
)
from infrastructure.providers.onnx_sessions import (
    create_session,
    session_providers,
)
from ports.detection.ports import DetectionRequest, DetectionResult, RegionCandidate
from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderInvalidOutput,
    ProviderNotConfigured,
)

PROVIDER_MANGA_ONNX = PROVIDER_MANGA

#: The shipped ONNX artifact: RT-DETR-v2 fixed-shape export (opset 17,
#: 1x3x640x640 fp32; outputs logits [1,300,3] + pred_boxes [1,300,4]).
MANGA_ONNX_FILENAME = "rtdetr-v2-fixed.onnx"
MANGA_ONNX_SHA256 = (
    "c7fb5af1a8982416b56955e621c1b10397730807956998066e2fbc132c77bbc3"
)
MANGA_ONNX_INPUT_SIZE = 640
MANGA_ONNX_OPSET = 17

#: The exported graph's tensor names (fixed by ``torch.onnx.export`` in the
#: INFER baseline; asserted by the engine build so a substituted graph fails
#: closed instead of silently feeding the wrong tensors).
MANGA_ONNX_INPUT_NAME = "pixel_values"
MANGA_ONNX_LOGITS_NAME = "logits"
MANGA_ONNX_BOXES_NAME = "pred_boxes"


def resolve_onnx_model_path(weights_path: Path) -> Path:
    """Accept a file path or a weights *directory* holding the ONNX file.

    The released ``NEWMANGA_DETECTOR_WEIGHTS`` contract is directory-based for
    the torch snapshot; the ONNX backend keeps accepting that shape (the
    directory then holds ``rtdetr-v2-fixed.onnx``) and also accepts the file
    path directly, so operators can point at either form.
    """
    candidate = Path(weights_path)
    if candidate.is_dir():
        return candidate / MANGA_ONNX_FILENAME
    return candidate


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass
class MangaDetectionOnnxProvider:
    """``DetectionProvider`` over the pinned RT-DETR-v2 ONNX graph."""

    weights_path: Path
    device: str = "auto"
    provider_id: str = PROVIDER_MANGA_ONNX
    provider_type: str = "local-manga-onnx"
    model: str = f"manga/{MANGA_ONNX_FILENAME}"
    requirements: tuple[str, ...] = ("onnxruntime", "PIL")

    _session: Any = field(default=None, init=False, repr=False)
    _session_ep: str = field(default="", init=False, repr=False)

    # -- public contract ----------------------------------------------------

    def detect(self, request: DetectionRequest) -> DetectionResult:
        started = time.perf_counter()
        self._validate_request(request)
        session = self._session_or_raise()
        # the frozen page_frame decoder is shared with the torch adapter (pure numpy)
        rgb = MangaDetectionProvider._frame_pixels(request)
        width, height = float(rgb.shape[1]), float(rgb.shape[0])
        trigger_ratio = _tiling_trigger_ratio()
        if _tiling_triggered(width, height, trigger_ratio):
            tiling_config = _tiling_config(trigger_ratio)
            boxes, n_bubble = self._detect_tiled(
                session, rgb, width, height, tiling_config
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
            boxes, n_bubble = self._detect_page(session, rgb, width, height)
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
                ("backend", "onnx"),
                ("onnx_opset", str(MANGA_ONNX_OPSET)),
                ("device", self.device),
                ("inference_ep", self._session_ep),
                ("conf_threshold", str(MANGA_CONF_THRESHOLD)),
                ("bubble_class_dropped", str(n_bubble)),
                ("text_boxes_pre_merge", str(len(boxes))),
                *tiling_options,
            ),
            elapsed_ms=elapsed_ms,
        )

    # -- engine lifecycle ---------------------------------------------------

    def _session_or_raise(self) -> Any:
        if self._session is None:
            self._session = _build_engine(self.weights_path, self.device)
            self._session_ep = ",".join(session_providers(self._session))
        return self._session

    @staticmethod
    def _validate_request(request: DetectionRequest) -> None:
        """Pure-Python input gate, identical to the torch adapter's.

        Runs before any dependency is touched; the frozen ``page_frame``
        contract is a raw pixel buffer (rgb32 BGRA or rgb24), never an
        encoded file.
        """
        if not request.image_bytes:
            raise ProviderInputError(
                "no image bytes were supplied for detection",
                provider_id=PROVIDER_MANGA_ONNX,
                stage="detection",
            )
        if request.width <= 0 or request.height <= 0:
            raise ProviderInputError(
                f"invalid frame size {request.width}x{request.height}",
                provider_id=PROVIDER_MANGA_ONNX,
                stage="detection",
            )
        expected = request.width * request.height
        if len(request.image_bytes) not in (expected * 3, expected * 4):
            raise ProviderInputError(
                f"frame byte count {len(request.image_bytes)} does not match "
                f"{request.width}x{request.height} rgb32 or rgb24 pixels",
                provider_id=PROVIDER_MANGA_ONNX,
                stage="detection",
            )

    # -- inference ----------------------------------------------------------

    def _detect_page(
        self, session: Any, rgb: Any, width: float, height: float
    ) -> tuple[list[tuple[float, float, float, float, float]], int]:
        scores, labels, boxes = self._infer(session, rgb, MANGA_CONF_THRESHOLD)
        return _text_boxes_from_results(scores, labels, boxes, width, height)

    def _detect_tiled(
        self,
        session: Any,
        rgb: Any,
        width: float,
        height: float,
        config: TilingConfig,
        threshold: float = MANGA_CONF_THRESHOLD,
    ) -> tuple[list[tuple[float, float, float, float, float]], int]:
        """Webtoon long-strip path: same tiling/NMS constants, ONNX engine."""
        tiles = _tiling_tiles(width, height, config.tile_size, config.overlap)
        page_boxes: list[tuple[float, float, float, float, float]] = []
        n_bubble = 0
        for (x0, y0, x1, y1) in tiles:
            crop = rgb[int(y0) : int(y1), int(x0) : int(x1)]
            crop_h, crop_w = int(crop.shape[0]), int(crop.shape[1])
            scores, labels, boxes = self._infer(
                session, _pad_tile(crop, config.tile_size), threshold
            )
            tile_boxes, tile_bubble = _text_boxes_from_results(
                scores, labels, boxes, float(crop_w), float(crop_h)
            )
            n_bubble += tile_bubble
            for (bx0, by0, bx1, by1, confidence) in tile_boxes:
                page_boxes.append(
                    (bx0 + x0, by0 + y0, bx1 + x0, by1 + y0, confidence)
                )
        return _greedy_nms(page_boxes, config.nms_iou), n_bubble

    def _infer(
        self, session: Any, rgb: Any, threshold: float
    ) -> tuple[list[float], list[int], list[list[float]]]:
        """One ONNX inference: preprocess -> session -> sigmoid/threshold boxes."""
        numpy = _lazy_import("numpy", "detection")
        tensor = preprocess_rgb(rgb)
        height, width = int(rgb.shape[0]), int(rgb.shape[1])
        try:
            outputs = session.run(
                None, {MANGA_ONNX_INPUT_NAME: tensor}
            )
        except Exception as error:  # noqa: BLE001 - inference failures are typed
            raise ProviderError(
                f"manga ONNX detection inference failed: {error!r}",
                stage="detection",
            ) from error
        return postprocess_outputs(
            outputs, width=width, height=height, threshold=threshold, numpy=numpy
        )


def preprocess_rgb(rgb: Any) -> Any:
    """The exported graph's exact preprocessing (fixed 640x640, no normalize).

    ``preprocessor_config.json`` of the pinned checkpoint: ``do_resize`` to
    640x640 with BILINEAR (PIL resample=2), ``do_rescale`` 1/255,
    ``do_normalize: false``. Webtoon tiles arrive pre-padded to a square, so
    the anisotropic-crush problem of the released whole-page path is unchanged
    (the tiling gate handles long strips exactly as before).
    """
    numpy = _lazy_import("numpy", "detection")
    pillow = _lazy_import("PIL.Image", "detection")
    if rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ProviderInvalidOutput(
            f"frame pixels are not HxWx3 RGB (got {rgb.shape})", stage="detection"
        )
    image = pillow.fromarray(rgb)
    resized = image.resize(
        (MANGA_ONNX_INPUT_SIZE, MANGA_ONNX_INPUT_SIZE), pillow.Resampling.BILINEAR
    )
    array = numpy.asarray(resized, dtype=numpy.float32) / 255.0
    return numpy.ascontiguousarray(array.transpose(2, 0, 1)[None])


def postprocess_outputs(
    outputs: Any,
    *,
    width: int,
    height: int,
    threshold: float,
    numpy: Any | None = None,
) -> tuple[list[float], list[int], list[list[float]]]:
    """RT-DETR logits/boxes -> absolute xyxy text-box payload.

    The graph emits raw (sigmoid space) logits ``[1,Q,3]`` and normalised
    cxcywh boxes ``[1,Q,4]``; ``RTDetrImageProcessor.post_process_object_detection``
    does exactly this: sigmoid, per-query best class, score threshold against
    the best class, then cxcywh -> xyxy scaled by the TARGET size (the page).
    Class filtering (TEXT 1/2 vs bubble 0) stays in the shared filter.
    """
    np = numpy
    if np is None:  # pragma: no cover - callers pass numpy
        np = _lazy_import("numpy", "detection")
    try:
        logits = np.asarray(outputs[0])
        boxes = np.asarray(outputs[1])
        if logits.ndim != 3 or boxes.ndim != 3:
            raise ValueError(
                f"unexpected RT-DETR output ranks {logits.shape}/{boxes.shape}"
            )
        scores_all = 1.0 / (1.0 + np.exp(-logits[0].astype(np.float64)))
        best_scores = scores_all.max(axis=1)
        best_classes = scores_all.argmax(axis=1)
        keep = best_scores >= float(threshold)
        kept_boxes = boxes[0][keep].astype(np.float64)
        kept_scores = best_scores[keep]
        kept_classes = best_classes[keep]
        if kept_boxes.shape[0]:
            cx, cy, bw, bh = (
                kept_boxes[:, 0],
                kept_boxes[:, 1],
                kept_boxes[:, 2],
                kept_boxes[:, 3],
            )
            xyxy = np.stack(
                [
                    (cx - bw / 2.0) * float(width),
                    (cy - bh / 2.0) * float(height),
                    (cx + bw / 2.0) * float(width),
                    (cy + bh / 2.0) * float(height),
                ],
                axis=1,
            )
        else:
            xyxy = np.zeros((0, 4), dtype=np.float64)
    except (ProviderError, ProviderInvalidOutput):
        raise
    except Exception as error:  # noqa: BLE001 - malformed payloads are typed
        raise ProviderInvalidOutput(
            f"manga ONNX detector payload is malformed: {error!r}",
            provider_id=PROVIDER_MANGA_ONNX,
            stage="detection",
        ) from error
    return (
        [float(value) for value in kept_scores.tolist()],
        [int(value) for value in kept_classes.tolist()],
        [[float(v) for v in row] for row in xyxy.tolist()],
    )


def _build_engine(weights_path: Path, device: str) -> Any:
    """Verify the pinned ONNX file, then build the ORT session.

    Order (contract): file existence -> sha256 pin -> ORT import/session with
    the requested EP verified active. Every failure is typed; a substitution
    or corruption is ``PROVIDER_FAILED``, never a warning.
    """
    model_path = resolve_onnx_model_path(Path(weights_path))
    if not model_path.is_file():
        raise ProviderNotConfigured(
            f"manga detector ONNX weights are not installed: {model_path} is "
            f"missing (place the pinned {MANGA_ONNX_FILENAME} of the "
            "ogkalu/comic-text-and-bubble-detector RT-DETR-v2 export there — "
            "served from the packaged bundle's models/detector/, or set "
            "NEWMANGA_DETECTOR_WEIGHTS; weights are never downloaded at run "
            "time). To use the torch/transformers snapshot instead, set "
            "NEWMANGA_DETECTOR_BACKEND=torch and place "
            "model.safetensors/config.json/preprocessor_config.json.",
            stage="detection",
        )
    actual = sha256_file(model_path)
    if actual != MANGA_ONNX_SHA256:
        raise ProviderError(
            f"manga detector ONNX weights file {model_path} has sha256 "
            f"{actual}, expected {MANGA_ONNX_SHA256}; refusing to run "
            "unverified weights",
            stage="detection",
        )
    return create_session(model_path, device=device, stage="detection")


def _lazy_import(module_name: str, stage: str) -> Any:
    try:
        return importlib.import_module(module_name)
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"detector runtime {module_name!r} is not installed: {error}",
            provider_id=PROVIDER_MANGA_ONNX,
            stage=stage,
        ) from error
