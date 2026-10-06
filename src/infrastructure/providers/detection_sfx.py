"""Standalone SFX (sound-effect) detection adapter — local train-v2b ONNX.

User rulings: 2026-10-01 (M2-SFX-PROD-1, verbatim) "要做 / chiqui7 能用，
不在乎 / 路线 A" established the standalone-SFX-provider route; 2026-10-05
(M2-SFX-T4-SWITCH, verbatim) "三件都同意" switched the pinned weights to the
LOCAL train-v2b release (G1/G2/G5/G8 all-hard-gate pass at the M2-SFX-GATE-T3
evaluation gate; G7 deep-call smoke precondition = M2-SFX-T4-SWITCH AC1
PASS). The rollback is the pin single-value restore to the previous
production chiqui7 weights (kept in place; T3 §7.4 / AC4 drill).

Model: the LOCAL train-v2b ONNX export (M2-SFX-TRAIN-V2, B-variant
fine-tune; NOT an HF release) — ONNX metadata names
``{0: bubble, 1: panel, 2: sfx, 3: text}`` (asserted at load against the
production class surface, R8 discipline; T3 G5 names/imgsz 5/5 PASS).
This provider produces **sfx-class candidates only**;
every other class is dropped (the class map is asserted
against the ONNX metadata at load, so a silent class-surface drift fails
loudly instead of mislabeling detections — the eval script's R8 discipline).

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
LIGHTWEIGHT route (no torch). The execution provider is CONFIGURED since
M2-SFX-GPU-EP-1 (user ruling 2026-10-06: deployment form = GPU):
``NEWMANGA_SFX_EP`` (``dml`` default | ``cpu``) selects DmlExecutionProvider
(the onnxruntime-directml wheel) or the pre-GPU CPUExecutionProvider behavior;
a DML init failure falls back to the CPU EP automatically with the degradation
audit-visible in the detect options (never silent). Weights stay bundled
(release-form out-of-the-box per user ruling 3).

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
import os
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

#: The pinned weights identity (M2-SFX-T4-SWITCH switch, user ruling
#: 2026-10-05 "三件都同意"). The weights live on local / gitignored paths
#: only — never committed, never downloaded at run time.
#:
#: Source fields — LOCAL RELEASE CHANNEL REGISTRATION (V2 report §7.2.3):
#: train-v2b is a LOCAL training product (M2-SFX-TRAIN-V2), not an HF
#: release, so ``SFX_HF_REPO``/``SFX_HF_REVISION`` no longer name an HF
#: repo/revision. They are REGISTRARIAL pointers into the local release
#: chain: the training task / variant, and the direct upstream checkpoint
#: (best.pt). Full deployment chain sha256 (T3 §4.8-2 verified, no break):
#:   base .pt  1f0fd609e7dc29c831255db67586ed5623f9bebae6a1e29fae197c1c6d7b77e0
#:   best.pt   c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08
#:   best.onnx 944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d
#: Rollback = restore the previous single pin value ``d87389af…b646``
#: (chiqui7/yolo11-manga-seg @ 7f5f5c0464f2eeb57282f16da760eb8828a8716a)
#: with the chiqui7 weights file still in place (AC4 drill proves it).
SFX_HF_REPO = "local-release:sfx-train-v2/v2b"
SFX_HF_REVISION = "c22f0175ffe7b453fd660161831aa9fce2a736fc32d29e574650ba9731131c08"
SFX_WEIGHTS_FILENAME = "yolo11s-seg.onnx"
SFX_WEIGHTS_SHA256 = (
    "944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d"
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

#: Detect-options ``imgsz_source`` states (DSH r1 R4): the letterbox size is
#: either the parsed ONNX metadata value or the frozen default because the
#: metadata text was absent/unparseable — provenance keeps the two
#: distinguishable instead of recording only the final number.
SFX_IMGSZ_SOURCE_METADATA = "metadata_parsed"
SFX_IMGSZ_SOURCE_FALLBACK = "fallback"

#: ONNX metadata class surface (asserted at load; drift fails loudly — the
#: eval script's R8 discipline). sfx = class 2.
SFX_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
SFX_CLASS_ID = 2

#: Anonymous label prefix (``ports.detection`` has no type slot — contract
#: zero-change ruling; the assembly dispatches this prefix to
#: ``RegionType.SFX``).
SFX_LABEL_PREFIX = "sfx-"


# ---------------------------------------------------------------------------
# Cross-provider overlap arbitration (M2-REGION-OVERLAP-ARBITRATION)
#
# The structural gap (DOMAIN-EXT-DIAG report §4/§5, user ruling 3): the
# composite CONCATENATES the two candidate sets and region creation treats
# every candidate independently, so an SFX shape that the primary detector
# mislabels as text still flows into the dialogue chain and its OCR garbage
# is translated into the rendered page (BJ13 regions #1/#3).
#
# Arbitration semantics (frozen here): when an sfx-provider candidate
# near-duplicates a primary candidate — bbox IoU >= the frozen threshold —
# that primary candidate is RELABELED to the ``sfx-arb-`` prefix. The prefix
# deliberately reuses the ``sfx-`` startswith contract, so the assembly's
# ``_detected_region_type`` dispatches it to ``RegionType.SFX`` with ZERO
# core_assembly changes and the SfxPolicy gate (default SKIP) takes over.
# Geometry, reading order and confidence stay verbatim: the relabel is a
# type decision, not a re-detection.
#
# Frozen default threshold — AC1 calibration over the committed raw data
# (``verification/M2-SFX-E2E-MATERIAL/``, ``verification/M2-SFX-E2E-MATERIAL/
# bj06-run/summaries/qual-BJ06.json``):
#
# - BJ06 (in-domain control, 8 sfx x 9 speech candidate pairs): the WORST
#   in-domain overlap is the '！！！' double-detection pair (sfx 2eeaa2c4 x
#   speech 5b76a907) at IoU = 0.8862; the other intersecting pairs are
#   0.870 / 0.728. In-domain SFX art text and neighbouring dialogue overlap
#   MORE than the misroute shape does — a naive "catch BJ13" threshold
#   would relabel real dialogue first. The default therefore sits ABOVE the
#   in-domain maximum: every BJ06 pair stays untouched (AC3 zero-change by
#   construction).
# - BJ13 (the misroute case): ogkalu text regions vs the visual SFX
#   reference boxes measure IoU 0.452/0.544 (E2E diagnosis caliber) /
#   0.490/0.550 (production-region caliber). With today's weights the sfx
#   channel has ZERO response there (pre-NMS peak 0.0855, DOMAIN-EXT-DIAG
#   L1), so there is no sfx candidate to arbitrate with at all — the
#   misroute is UNREACHABLE for any overlap arbitration and this Task does
#   not fabricate coverage: the near-miss overlap is recorded in the detect
#   options (``sfx_arbitration_partial_overlap``) so the unreachable shape
#   is typed-diagnosable (AC4). A future recall-restoring slice (e.g. a
#   fine-tuned sfx detector) produces real sfx candidates; near-duplicate
#   double detections (the shape this rule closes) then relabel into the
#   SFX gate instead of leaving both a translated dialogue region AND an
#   sfx region on the same artwork.
#
# The env channel follows the TILING precedent (``NEWMANGA_DETECTOR_TILING_*``):
# absent variables mean the frozen defaults; an empty or illegal value is a
# fail-fast ``ValueError`` naming the variable — never a silent default.
ARBITRATION_ENV_MODE = "NEWMANGA_SFX_ARBITRATION"
ARBITRATION_ENV_IOU = "NEWMANGA_SFX_ARBITRATION_IOU"

#: Frozen default threshold: BJ06 in-domain worst pair (0.8862) + margin.
ARBITRATION_IOU = 0.9

#: The arbitrated label prefix. ``startswith("sfx-")`` holds BY CONSTRUCTION
#: (the assembly dispatch matrix is prefix-based), so a relabeled candidate
#: lands in ``RegionType.SFX`` without touching core_assembly.
ARBITRATED_LABEL_PREFIX = "sfx-arb-"


# ---------------------------------------------------------------------------
# KO long-strip tile routing (M2-SFX-T5-TILE-KO)
#
# The structural fact (T3 / M2-KO-TILE-CALIB, three weights all-zero): KO
# long-strip pages — 600/690 px wide, aspect (h/w) 30.7-145.6 — sub-pixelize
# under the whole-page letterbox, so the sfx class has ZERO response there
# and tile-ing the inference sequence is the only route from zero to sfx
# candidates. This section routes those pages through the FROZEN tile
# caliber (KO-TILE proposal §3, the numbers the T3 evaluation matrix and the
# KO acceptance are pegged to); every other page keeps the letterbox path
# byte-for-byte.
#
# Implementation equivalence contract (AC3): the production tile branch
# replicates ``experiments/M2-SFX-GATE-T3/eval_gate_t3.py`` ``run_tile`` /
# ``tile_calib.py`` ``run_tile_caliber`` verbatim — per-tile the production
# letterbox+boxes sequence itself (``_letterbox`` + ``_sfx_boxes``), ``+y0``
# translation back into page coordinates, then the page-level cross-tile
# dedup (conf-descending stable greedy, IoU >= 0.5 drops the newcomer) with
# the final ``(-conf, xyxy)`` ordering. Bit-parity with the T3 matrix
# (v2b 35/56+48/135, chiqui7 56/56+41/135 at conf 0.5) is the acceptance
# evidence.
#
# The env channel follows the ARBITRATION/TILING precedent: absent variables
# mean the frozen defaults; an empty or illegal value is a fail-fast
# ``ValueError`` naming the variable — read BEFORE any inference/weights
# resolution, never a silent default, never a half-detected page.
# ---------------------------------------------------------------------------

#: Frozen tile caliber (K_TILE_H / K_TILE_OVERLAP / TILE_PAGE_NMS_IOU in the
#: lines of record). Changing any of these is a new slice with re-run KO
#: evidence — the T3 numbers do not transfer across calibers.
SFX_TILE_HEIGHT = 1024
SFX_TILE_OVERLAP = 128  # step = HEIGHT - OVERLAP = 896
SFX_TILE_NMS_IOU = 0.5

#: Route thresholds — the AC1 implementation-discretion constants, frozen
#: here with their registration basis: the KO domain's observed long-strip
#: pages are 600/690 px wide with aspect 30.7-145.6 (T3 raw ``page_size``);
#: ordinary pages run near aspect 1.4. The width cap 690 is the largest
#: observed KO width inclusive; the aspect floor 8.0 sits more than 3.8x
#: below the smallest observed KO aspect and more than 5.7x above ordinary
#: pages, so neither domain can cross into the other by rounding. Registered
#: coverage gap (KO-TILE §9): a KO-shaped page whose width is neither 600 nor
#: 690 is parameterized by these constants, not re-calibrated per width.
SFX_TILE_ROUTE_MAX_PAGE_W = 690
SFX_TILE_ROUTE_MIN_ASPECT = 8.0

TILE_ENV_MODE = "NEWMANGA_SFX_TILE"
TILE_ENV_ROUTE_MAX_PAGE_W = "NEWMANGA_SFX_TILE_ROUTE_MAX_PAGE_W"
TILE_ENV_ROUTE_MIN_ASPECT = "NEWMANGA_SFX_TILE_ROUTE_MIN_ASPECT"
TILE_ENV_HEIGHT = "NEWMANGA_SFX_TILE_HEIGHT"
TILE_ENV_OVERLAP = "NEWMANGA_SFX_TILE_OVERLAP"
TILE_ENV_NMS_IOU = "NEWMANGA_SFX_TILE_NMS_IOU"


@dataclass(frozen=True)
class _TileConfig:
    """Resolved tile-routing configuration (frozen defaults or env overrides)."""

    enabled: bool
    route_max_page_w: float
    route_min_aspect: float
    tile_h: int
    overlap: int
    nms_iou: float


def _tile_config() -> _TileConfig:
    """Read ONLY the tile env overrides (the ``_arbitration_config``
    testability pattern; the fail-fast discipline).

    Absent variables mean the frozen defaults; ``NEWMANGA_SFX_TILE`` accepts
    ``on|off`` (default on — the ruling that authorized this Task; ``off``
    restores the pre-T5 letterbox behavior byte-for-byte). An empty or
    illegal value anywhere is a ``ValueError`` naming the variable.
    """
    raw_mode = os.environ.get(TILE_ENV_MODE)
    if raw_mode is not None:
        mode = raw_mode.strip().lower()
        if mode not in ("on", "off"):
            raise ValueError(
                f"{TILE_ENV_MODE}: unsupported value {raw_mode!r} (use on|off)"
            )
        enabled = mode == "on"
    else:
        enabled = True

    def _positive_float(name: str, default: float) -> float:
        raw = os.environ.get(name)
        if raw is None:
            return default
        try:
            value = float(raw.strip())
        except ValueError as error:
            raise ValueError(f"{name}: not a number: {raw!r}") from error
        if not value > 0.0:
            raise ValueError(f"{name}: must be > 0, got {value!r}")
        return value

    route_max_page_w = _positive_float(TILE_ENV_ROUTE_MAX_PAGE_W, float(SFX_TILE_ROUTE_MAX_PAGE_W))
    route_min_aspect = _positive_float(TILE_ENV_ROUTE_MIN_ASPECT, float(SFX_TILE_ROUTE_MIN_ASPECT))

    raw_h = os.environ.get(TILE_ENV_HEIGHT)
    if raw_h is None:
        tile_h = SFX_TILE_HEIGHT
    else:
        try:
            tile_h = int(raw_h.strip())
        except ValueError as error:
            raise ValueError(f"{TILE_ENV_HEIGHT}: not an integer: {raw_h!r}") from error
        if tile_h <= 0:
            raise ValueError(f"{TILE_ENV_HEIGHT}: must be > 0, got {tile_h!r}")

    raw_overlap = os.environ.get(TILE_ENV_OVERLAP)
    if raw_overlap is None:
        overlap = SFX_TILE_OVERLAP
    else:
        try:
            overlap = int(raw_overlap.strip())
        except ValueError as error:
            raise ValueError(f"{TILE_ENV_OVERLAP}: not an integer: {raw_overlap!r}") from error
        if not 0 < overlap < tile_h:
            raise ValueError(
                f"{TILE_ENV_OVERLAP}: must be in (0, {TILE_ENV_HEIGHT}) exclusive "
                f"so the step {tile_h}-{overlap} stays >= 1, got {overlap!r}"
            )

    raw_iou = os.environ.get(TILE_ENV_NMS_IOU)
    if raw_iou is None:
        nms_iou = float(SFX_TILE_NMS_IOU)
    else:
        try:
            nms_iou = float(raw_iou.strip())
        except ValueError as error:
            raise ValueError(f"{TILE_ENV_NMS_IOU}: not a number: {raw_iou!r}") from error
        if not 0.0 < nms_iou <= 1.0:
            raise ValueError(f"{TILE_ENV_NMS_IOU}: must be in (0, 1], got {nms_iou!r}")

    return _TileConfig(
        enabled=enabled,
        route_max_page_w=route_max_page_w,
        route_min_aspect=route_min_aspect,
        tile_h=tile_h,
        overlap=overlap,
        nms_iou=nms_iou,
    )


# ---------------------------------------------------------------------------
# Execution-provider selection (M2-SFX-GPU-EP-1, user ruling 2026-10-06 GPU)
#
# T5-TILE-KO's deployment-form data (verification/M2-SFX-T5-TILE-KO): KO
# long-strip pages measured 10.46 s/page on the CPU EP vs 1.08 s/page on the
# DML EP (onnxruntime-directml 1.24.4, RTX 5070 Ti) — the user ruled the
# deployment form GPU and this section turns the hardcoded
# ``CPUExecutionProvider`` into a configured value.
#
# ``NEWMANGA_SFX_EP`` accepts ``dml`` (DEFAULT — the ruling) or ``cpu`` (the
# pre-GPU behavior verbatim). The env follows the ARBITRATION/TILE
# discipline: an absent variable means the default; an empty or illegal value
# is a fail-fast ``ValueError`` naming the variable, raised BEFORE any
# weights resolution or inference (never a half-configured engine).
#
# DML init failure semantics (Owner discretion, registered in the Task
# report; r1 P1-1 mechanism corrected): a machine without a DX12 GPU / with
# a broken driver / running the CPU-only wheel cannot use a DML session.
# The MECHANISM matters: onnxruntime's own Python wrapper
# (``InferenceSession.__init__``, ``enable_fallback=True`` by default)
# SWALLOWS (ValueError, RuntimeError) from the requested EP, rebuilds on
# ["CPUExecutionProvider"] and returns NORMALLY — so the usual fallback
# shape is NOT an exception here. The effective EP is therefore read back
# off the session via ``get_providers()``: requested dml + a session whose
# first provider is not DmlExecutionProvider = the wrapper-level fallback.
# Either way (wrapper fallback, or the defensive exception-driven retry for
# the shapes that DO raise) the degradation is recorded in the detect
# options — ``device`` carries the EFFECTIVE EP, ``sfx_ep`` the EP that was
# requested at engine-build time, ``sfx_ep_fallback`` the reason —
# availability first, the behavior stays usable everywhere, the fallback is
# never silent. ``device`` is the SFX provider's EXECUTION-PROVIDER key: it
# shares its NAME with the manga/doctr torch-device ``device`` options key
# but records an onnxruntime provider there (r1 P4-3 note; no consumer in
# src/ or apps/ branches on either value). The EP is NOT part of the
# supply-chain security surface (the SHA-256 weights gate runs before any
# runtime import and is unaffected by the EP choice). An EXPLICIT ``cpu``
# request whose session build fails stays a typed ``ProviderError`` — no
# fallback out of an explicit request. The fallback above covers INIT only
# (r2 N-P3-1 narrowing): the wrapper ALSO retries internally at run() time —
# an ``ORT EPFail`` mid-inference is caught by ``InferenceSession.run``
# (wrapper ``:278-305``), which calls ``set_providers(
# self._fallback_providers)`` (a CPU list for a dml request), disables the
# fallback (it fires ONCE per session) and re-runs on CPU, returning
# NORMALLY — no exception reaches the caller, only two stdout ``print``
# lines that the frozen face drops (r2 N-P4-2). That run-time channel is
# audited SINCE M2-SFX-EPFAIL-AUDIT-1: the wrapper's ``set_providers`` call
# rewrites the session's provider list, and that change is observable
# through the PUBLIC ``get_providers()`` read-back (wrapper :214-216 — a
# pure Python attribute read, measured 0.03 us/call on the production wheel
# + v2b weights, DML and CPU sessions alike; a DML session's post-build
# read-back is ``[Dml, CPU]``, after the run-time fallback ``[CPU]``). Every
# detect reads the providers back ONCE and compares the first name against
# the ENGINE-BUILD effective name: unchanged = steady state, nothing is
# added; changed = the key ``sfx_ep_runtime_check`` joins the options
# ("session providers changed at run time: <built> -> <now> (ORT wrapper
# run-time EPFail fallback)"). The silent-success shape is observed on the
# SAME page (the read-back happens after run); a re-run that also fails
# keeps the existing typed detect-time failure (no options that page) and
# the changed provider list is observed on the NEXT successful detect —
# session state, not a per-page event. The three-key provenance above keeps
# its ENGINE-BUILD semantics and write point verbatim (``device``/``sfx_ep``
# /``sfx_ep_fallback`` are NOT rewritten to the run-time state; the runtime
# key is additive). A session object without a provider read-back face (a
# bare test double) skips the runtime check — the build gate already
# requires the same surface on every real session, so the audit never
# becomes a new failure point. Rejected designs are registered in the Task
# deploy record (exception-triggered read-back misses the silent-success
# shape; sampled read-back adds an env knob for no gain at 0.03 us/call;
# private-attribute probing rides wrapper internals the public API already
# exposes).
#
# Cache semantics: the EP is an ENGINE-level property (providers are fixed at
# InferenceSession construction), so the resolved env rides the first
# ``_engine_or_raise`` call and the cached engine keeps it for the provider
# instance's lifetime — same lifetime discipline as the ``conf_threshold``
# field; a different EP means a new provider instance or process. The
# fail-fast env read itself happens on EVERY detect, so an illegal value
# never slips through on a warm engine either. Corollary (r1 P4-4): on a
# warm engine a LATER env change is deliberately NOT reflected in the
# options — ``sfx_ep`` records what was requested at ENGINE-BUILD time, the
# fail-fast read only guards the legality of the env, never re-resolves the
# engine.
# ---------------------------------------------------------------------------

#: The env name. Values: ``dml`` (default) | ``cpu``.
SFX_ENV_EP = "NEWMANGA_SFX_EP"
SFX_EP_DML = "dml"
SFX_EP_CPU = "cpu"
#: The deployment-form default = the user ruling 2026-10-06 (GPU).
SFX_EP_DEFAULT = SFX_EP_DML

#: The provider-name strings as onnxruntime spells them.
_EP_PROVIDER_NAMES = {
    SFX_EP_DML: "DmlExecutionProvider",
    SFX_EP_CPU: "CPUExecutionProvider",
}
#: Reverse lookup for the get_providers() read-back (r1 P1-1): a provider
#: name -> the ``dml``/``cpu`` audit token; an unknown name is recorded
#: as-is (the audit value follows the runtime, never a guess).
_EP_MODE_BY_PROVIDER_NAME = {
    name: mode for mode, name in _EP_PROVIDER_NAMES.items()
}


def _ep_config() -> str:
    """Read the EP env override (the ``_tile_config``/``_arbitration_config``
    testability pattern; the fail-fast discipline)."""
    raw = os.environ.get(SFX_ENV_EP)
    if raw is None:
        return SFX_EP_DEFAULT
    mode = raw.strip().lower()
    if mode not in (SFX_EP_DML, SFX_EP_CPU):
        raise ValueError(
            f"{SFX_ENV_EP}: unsupported value {raw!r} (use dml|cpu)"
        )
    return mode


@dataclass(frozen=True)
class _EpProvenance:
    """The execution-provider provenance riding the engine to the detect
    options (the DSH r1 R4 imgsz-provenance pattern): what was REQUESTED via
    the env, what is EFFECTIVE (differs only on the DML->CPU fallback), and
    the fallback reason when there is one."""

    requested: str
    effective: str
    fallback_reason: str | None = None


def _runtime_ep_audit(
    session: Any, ep_prov: _EpProvenance
) -> tuple[tuple[str, str], ...]:
    """The run-time EPFail channel audit (M2-SFX-EPFAIL-AUDIT-1, AC1).

    The ORT wrapper's ``InferenceSession.run`` catches ``C.EPFail``,
    switches the session to its CPU fallback list via ``set_providers`` and
    re-runs, returning NORMALLY (no exception reaches the caller; its only
    own signal is two stdout lines the frozen face drops — r2 N-P4-2). The
    observable face is therefore the session's provider list itself: the
    public ``get_providers()`` read-back (a pure Python attribute read,
    measured 0.03 us/call on the production wheel — negligible against the
    1%-per-page latency budget) shows ``[Dml, CPU]`` after a dml build and
    ``[CPU]`` once the wrapper's run-time fallback has fired.

    Returns an EMPTY tuple in the steady state (the read-back still matches
    the engine-build effective provider) — the detect options stay
    byte-identical to the pre-audit form — and a single
    ``sfx_ep_runtime_check`` entry when the session's first provider no
    longer matches the build: the silent-success shape is observed on the
    same page (the read-back runs after ``run``), a failed re-run surfaces
    through the next successful detect (session state persists). The
    three-key provenance keeps its engine-build semantics and write point;
    this key is ADDITIVE. A session without a ``get_providers`` face (a
    bare test double) skips the check — never a new failure point.
    """
    read_back = getattr(session, "get_providers", None)
    if read_back is None:
        return ()
    providers = read_back()
    if not providers:
        return ()
    built_name = _EP_PROVIDER_NAMES.get(ep_prov.effective, ep_prov.effective)
    current_name = providers[0]
    if current_name == built_name:
        return ()
    current_token = _EP_MODE_BY_PROVIDER_NAME.get(current_name, current_name)
    return (
        (
            "sfx_ep_runtime_check",
            "session providers changed at run time: "
            f"{ep_prov.effective} -> {current_token} "
            "(ORT wrapper run-time EPFail fallback)",
        ),
    )


def _routes_to_tile(page_w: int, page_h: int, cfg: _TileConfig) -> bool:
    """The AC1 routing predicate: a long-strip page at or below the width cap
    with aspect at or above the floor goes to tiles; everything else keeps
    the letterbox path verbatim."""
    if page_w > cfg.route_max_page_w:
        return False
    return (page_h / page_w) >= cfg.route_min_aspect


def _tile_ys(page_h: int, tile_h: int, overlap: int) -> list[int]:
    """The tile y-anchor sequence — ``tile_calib.py`` / ``eval_gate_t3.py``
    ``tile_ys`` verbatim (stage1_preannotate.py lineage): step
    ``tile_h - overlap`` from 0, plus the trailing ``page_h - tile_h``
    anchor whenever the regular sequence leaves the page bottom uncovered.

    The T4-inherited review item r1 P3-2 (tile-caliber run-time assertion)
    closes here: the frozen caliber is asserted on EVERY call via
    ``_assert_tile_caliber`` — a typed raise, stronger than the ``assert``
    statement (never stripped under ``python -O``).
    """
    ys = list(range(0, max(page_h - tile_h, 0) + 1, tile_h - overlap))
    if not ys:
        ys = [0]
    if ys[-1] + tile_h < page_h:
        ys.append(page_h - tile_h)
    _assert_tile_caliber(ys, page_h, tile_h, overlap)
    return ys


def _assert_tile_caliber(
    ys: list[int], page_h: int, tile_h: int, overlap: int
) -> None:
    """r1 P3-2 closure — the frozen tile caliber as a run-time gate.

    Asserts (typed ``ProviderInvalidOutput``, not ``assert``): non-empty
    sequence anchored at 0; every adjacent gap is either the frozen step
    ``tile_h - overlap`` or the trailing page-bottom anchor
    ``page_h - tile_h``; the last anchor's tile covers the page bottom; every
    anchor yields a non-degenerate tile. A drift in any frozen number fails
    loudly at detect time instead of silently re-calibrating the KO domain.
    """
    step = tile_h - overlap
    bottom_anchor = page_h - tile_h
    if not ys:
        raise ProviderInvalidOutput(
            f"sfx tile caliber assertion failed: empty anchor sequence "
            f"(page_h={page_h}, tile_h={tile_h})",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )
    if ys[0] != 0:
        raise ProviderInvalidOutput(
            f"sfx tile caliber assertion failed: first anchor {ys[0]} != 0",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )
    for prev, cur in zip(ys, ys[1:]):
        if cur - prev != step and cur != bottom_anchor:
            raise ProviderInvalidOutput(
                f"sfx tile caliber assertion failed: anchor gap {cur - prev} "
                f"is neither the frozen step {step} nor the page-bottom "
                f"anchor {bottom_anchor} (page_h={page_h}, tile_h={tile_h}, "
                f"overlap={overlap})",
                provider_id=PROVIDER_SFX,
                stage="detection",
            )
    if ys[-1] + tile_h < page_h:
        raise ProviderInvalidOutput(
            f"sfx tile caliber assertion failed: last anchor {ys[-1]} + "
            f"tile_h {tile_h} does not cover the page bottom {page_h}",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )
    if any(y < 0 or y + tile_h <= y for y in ys):
        raise ProviderInvalidOutput(
            f"sfx tile caliber assertion failed: degenerate anchor in {ys!r}",
            provider_id=PROVIDER_SFX,
            stage="detection",
        )


def _tile_page_nms(
    boxes: list[tuple[list[float], float]], iou_thr: float
) -> list[tuple[float, float, float, float, float]]:
    """Page-level cross-tile sfx dedup — ``dedup_boxes`` semantics verbatim
    (the R1 ``_dedup_boxes`` lineage): conf-descending STABLE greedy sort,
    a box is dropped when it overlaps any kept box at IoU >= threshold;
    the kept ordering is ``(-conf, xyxy)`` exactly as the T3 ``run_tile``
    leaves it. Stable sorting keeps the tile-collection order on confidence
    ties — deliberate bit-parity with the evaluation implementation."""
    ordered = sorted(boxes, key=lambda entry: entry[1], reverse=True)
    kept: list[tuple[list[float], float]] = []
    for box, confidence in ordered:
        if any(_iou(box, kept_box[0]) >= iou_thr for kept_box in kept):
            continue
        kept.append((box, confidence))
    kept.sort(key=lambda entry: (-entry[1], entry[0]))
    return [
        (box[0], box[1], box[2], box[3], confidence)
        for box, confidence in kept
    ]


def _arbitration_config() -> tuple[bool, float]:
    """Read ONLY the arbitration env overrides (module-level, the
    ``_detected_region_type`` testability pattern; the TILING fail-fast
    discipline).

    Returns ``(enabled, threshold)``. An absent ``NEWMANGA_SFX_ARBITRATION``
    means ON (the ruling that authorized this Task); ``off`` restores the
    pre-arbitration composite byte-for-byte. An empty or non-enumerated mode
    and an empty / non-numeric / out-of-(0, 1]-range threshold raise
    ``ValueError`` naming the variable.
    """
    raw_mode = os.environ.get(ARBITRATION_ENV_MODE)
    if raw_mode is not None:
        mode = raw_mode.strip().lower()
        if mode not in ("on", "off"):
            raise ValueError(
                f"{ARBITRATION_ENV_MODE}: unsupported value {raw_mode!r} "
                "(use on|off)"
            )
        enabled = mode == "on"
    else:
        enabled = True
    raw_iou = os.environ.get(ARBITRATION_ENV_IOU)
    threshold = float(ARBITRATION_IOU)
    if raw_iou is not None:
        try:
            threshold = float(raw_iou.strip())
        except ValueError as error:
            raise ValueError(
                f"{ARBITRATION_ENV_IOU}: not a number: {raw_iou!r}"
            ) from error
        if not 0.0 < threshold <= 1.0:
            raise ValueError(
                f"{ARBITRATION_ENV_IOU}: must be in (0, 1], got {threshold!r}"
            )
    return enabled, threshold


def _bbox(polygon: tuple[tuple[float, float], ...]) -> tuple[float, float, float, float]:
    """The candidate's bbox as ``(x0, y0, x1, y1)`` — the same min/max
    caliber the assembly's ``RegionGeometry`` uses, so the arbitration sees
    the geometry the region will be created with."""
    xs = [point[0] for point in polygon]
    ys = [point[1] for point in polygon]
    return (min(xs), min(ys), max(xs), max(ys))


def _bbox_iou(
    a: tuple[tuple[float, float], ...], b: tuple[tuple[float, float], ...]
) -> float:
    """IoU of two candidates' bboxes (the E2E/DOMAIN-EXT-DIAG caliber the
    threshold was calibrated against)."""
    ax0, ay0, ax1, ay1 = _bbox(a)
    bx0, by0, bx1, by1 = _bbox(b)
    inter_w = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    inter_h = max(0.0, min(ay1, by1) - max(ay0, by0))
    inter = inter_w * inter_h
    area_a = (ax1 - ax0) * (ay1 - ay0)
    area_b = (bx1 - bx0) * (by1 - by0)
    union = area_a + area_b - inter
    return inter / union if union > 0.0 else 0.0


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
        # Fail-fast BEFORE any inference or weights resolution (the
        # ARBITRATION/TILING discipline): an illegal tile env must not
        # produce a half-detected page.
        tile_cfg = _tile_config()
        # Same discipline for the EP env (M2-SFX-GPU-EP-1): the illegal
        # NEWMANGA_SFX_EP raises here, before the engine/weights resolution.
        ep_cfg = _ep_config()
        session, imgsz, imgsz_source, imgsz_raw, ep_prov = self._engine_or_raise(ep_cfg)
        numpy = _lazy_import("numpy", "detection")
        rgb = self._frame_pixels(request)
        page_h, page_w = int(rgb.shape[0]), int(rgb.shape[1])
        route = "tile" if (
            tile_cfg.enabled and _routes_to_tile(page_w, page_h, tile_cfg)
        ) else "letterbox"
        route_options: tuple[tuple[str, str], ...] = (("sfx_route", route),)
        if route == "tile":
            boxes, n_tiles = self._detect_tiles(
                session, imgsz, rgb, page_w=page_w, page_h=page_h, cfg=tile_cfg
            )
            route_options = route_options + (
                ("tile_h", str(tile_cfg.tile_h)),
                ("tile_overlap", str(tile_cfg.overlap)),
                ("tile_nms_iou", str(tile_cfg.nms_iou)),
                ("tile_count", str(n_tiles)),
            )
        else:
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
        # DSH r1 R4: the imgsz provenance is two-state (metadata_parsed /
        # fallback) and a fallback additionally carries the raw metadata text,
        # so "metadata said 1024" and "metadata unparseable, defaulted 1024"
        # stay distinguishable in the audit trail.
        imgsz_options: tuple[tuple[str, str], ...] = (
            ("imgsz", str(imgsz)),
            ("imgsz_source", imgsz_source),
        )
        if imgsz_source == SFX_IMGSZ_SOURCE_FALLBACK and imgsz_raw:
            imgsz_options = imgsz_options + (("imgsz_metadata_raw", imgsz_raw),)
        # M2-SFX-EPFAIL-AUDIT-1: the run-time EPFail channel read-back —
        # steady state adds NOTHING, a wrapper run-time fallback adds the
        # single ``sfx_ep_runtime_check`` key (the three-key provenance above
        # keeps its engine-build values verbatim).
        runtime_options = _runtime_ep_audit(session, ep_prov)
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
                ("device", ep_prov.effective),
                ("sfx_ep", ep_prov.requested),
                *(
                    (("sfx_ep_fallback", ep_prov.fallback_reason),)
                    if ep_prov.fallback_reason
                    else ()
                ),
                *runtime_options,
                ("conf_threshold", str(self.conf_threshold)),
                ("nms_iou", str(SFX_NMS_IOU)),
                *imgsz_options,
                ("class_filter", "sfx"),
                *route_options,
            ),
            elapsed_ms=elapsed_ms,
        )

    # -- KO long-strip tile branch (M2-SFX-T5-TILE-KO) -----------------------

    def _detect_tiles(
        self,
        session: Any,
        imgsz: int,
        rgb: Any,
        *,
        page_w: int,
        page_h: int,
        cfg: _TileConfig,
    ) -> tuple[list[tuple[float, float, float, float, float]], int]:
        """The frozen tile caliber over one long-strip page — the T3
        evaluation ``run_tile`` verbatim, on the production sequence itself:

        - anchors from ``_tile_ys`` (step ``tile_h - overlap`` from 0, the
          trailing ``page_h - tile_h`` anchor covering the page bottom, the
          P3-2 run-time caliber assertion on every call);
        - per tile: the native-width crop, the production ``_letterbox`` +
          ``_sfx_boxes`` sequence UNCHANGED (conf filter -> class-agnostic
          NMS 0.7 -> sfx class -> /scale mapping clipped to the TILE bounds),
          then the ``+y0`` translation into page coordinates;
        - page level: ``_tile_page_nms`` (conf-descending stable greedy,
          IoU >= the frozen 0.5 drops the newcomer) with the final
          ``(-conf, xyxy)`` ordering.

        Tile width is the native page width by construction — the caliber's
        only resize is the per-tile letterbox to the model ``imgsz``.
        Returns ``(boxes_in_page_pixels, n_tiles)``.
        """
        numpy = _lazy_import("numpy", "detection")
        ys = _tile_ys(page_h, cfg.tile_h, cfg.overlap)
        collected: list[tuple[list[float], float]] = []
        for y0 in ys:
            y1 = min(y0 + cfg.tile_h, page_h)
            tile = numpy.ascontiguousarray(rgb[y0:y1, 0:page_w])
            tile_h_px = y1 - y0
            inp, scale = _letterbox(numpy, tile, imgsz)
            raw = _sfx_boxes(
                session,
                inp,
                scale,
                self.conf_threshold,
                page_w=float(page_w),
                page_h=float(tile_h_px),
            )
            for bx0, by0, bx1, by1, confidence in raw:
                collected.append(([bx0, by0 + y0, bx1, by1 + y0], confidence))
        return _tile_page_nms(collected, cfg.nms_iou), len(ys)

    # -- engine lifecycle ---------------------------------------------------

    def _engine_or_raise(
        self, ep_mode: str
    ) -> tuple[Any, int, str, str | None, _EpProvenance]:
        """The engine is built ONCE per provider instance with the EP the
        first detect resolved (providers are fixed at session construction —
        an engine-level property); the fail-fast env read in ``detect`` keeps
        guarding every call regardless of the cache."""
        if self._engine is None:
            self._engine = _build_engine(self.weights_path, ep_mode)
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


def _build_engine(
    weights_path: Path, ep_mode: str | None = None
) -> tuple[Any, int, str, str | None, _EpProvenance]:
    """Load the pinned ONNX without touching the network. Check order matters:

    1. the EP env is resolved and fail-fast validated FIRST (``None`` means
       "read the env now" for direct callers) — an illegal
       ``NEWMANGA_SFX_EP`` never reaches the weights resolution;
    2. the weights *file* must exist — probed next with zero dependencies;
    3. its SHA-256 must match the pin — verified BEFORE any runtime import, so
       a corrupted/substituted artifact is ``PROVIDER_FAILED`` even on a
       machine that never installed onnxruntime;
    4. onnxruntime must import — the typed dependency gap otherwise;
    5. the session builds (the EP from ``NEWMANGA_SFX_EP`` — default dml =
       the GPU deployment ruling; a DML init failure falls back to the CPU EP
       with the degradation recorded in the returned provenance; an explicit
       cpu failure is typed);
    6. the metadata ``names`` must equal the asserted class map (R8 discipline)
       and the metadata ``imgsz`` (when parseable) drives the letterbox size —
       returned as ``(session, imgsz, source, raw_text, ep_provenance)`` so the
       caller can record the two-state provenance (DSH r1 R4) and the EP
       provenance (M2-SFX-GPU-EP-1).
    """
    if ep_mode is None:
        ep_mode = _ep_config()
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
    requested_provider = _EP_PROVIDER_NAMES[ep_mode]
    prov: _EpProvenance
    try:
        session = onnxruntime.InferenceSession(
            str(weights_path), providers=[requested_provider]
        )
    except Exception as requested_error:  # noqa: BLE001 - any build failure is typed
        if ep_mode != SFX_EP_DML:
            # An EXPLICIT cpu request that fails is a typed failure — no
            # fallback out of an explicit request (the registered semantics).
            raise ProviderError(
                f"sfx detector engine failed to load from {weights_path}: "
                f"{requested_error!r}",
                stage="detection",
            ) from requested_error
        # Defensive retry (r1 P1-1 role clarification): the onnxruntime
        # PYTHON WRAPPER usually handles the DML failure itself and returns
        # NORMALLY (see the get_providers() read-back below), so this branch
        # is NOT the primary fallback path — it only fires when an exception
        # escapes the wrapper (a non-(ValueError, RuntimeError) failure, or
        # a build with fallback disabled). The explicit CPU rebuild keeps
        # the behavior usable in exactly those shapes, with the degradation
        # carried in the provenance (never silent).
        try:
            session = onnxruntime.InferenceSession(
                str(weights_path),
                providers=[_EP_PROVIDER_NAMES[SFX_EP_CPU]],
            )
        except Exception as error:  # noqa: BLE001 - any build failure is typed
            raise ProviderError(
                f"sfx detector engine failed to load from {weights_path}: "
                f"{error!r}",
                stage="detection",
            ) from error
        prov = _EpProvenance(
            requested=ep_mode,
            effective=SFX_EP_CPU,
            fallback_reason=(
                "dml init failed; fell back to cpu "
                f"({type(requested_error).__name__})"
            ),
        )
    else:
        # r1 P1-1: the wrapper's InferenceSession.__init__ has
        # enable_fallback=True BY DEFAULT and SWALLOWS (ValueError,
        # RuntimeError) from the requested EP — it rebuilds on
        # ["CPUExecutionProvider"] and returns NORMALLY (r2 N-P4-2: depending on
        # the failure shape the wrapper either prints an "EP Error" banner on
        # STDOUT, or the unavailable provider is dropped by the native layer
        # with only a UserWarning — both shapes end in "constructor returns
        # normally with a CPU session"). A DML init failure (no DX12 GPU /
        # broken driver / CPU-only wheel) therefore usually does NOT raise
        # here at
        # all: the session in hand IS the CPU session. The authoritative
        # effective EP is read back OFF the session — a requested dml whose
        # first provider is not DmlExecutionProvider is the wrapper-level
        # fallback, and it gets the SAME three-key audit (sfx_ep / device /
        # sfx_ep_fallback): never silent, never a wrong "dml".
        effective_providers = session.get_providers()
        effective_name = (
            effective_providers[0] if effective_providers else requested_provider
        )
        if effective_name == requested_provider:
            prov = _EpProvenance(requested=ep_mode, effective=ep_mode)
        else:
            prov = _EpProvenance(
                requested=ep_mode,
                effective=_EP_MODE_BY_PROVIDER_NAME.get(
                    effective_name, effective_name
                ),
                fallback_reason=(
                    f"requested {ep_mode} but onnxruntime built the session "
                    f"on {effective_name} (wrapper-level fallback/EP "
                    f"unavailable)"
                ),
            )
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
    imgsz, imgsz_source = _parse_imgsz(meta.get("imgsz"))
    return session, imgsz, imgsz_source, meta.get("imgsz"), prov


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


def _parse_imgsz(raw: str | None) -> tuple[int, str]:
    """Metadata imgsz wins when parseable; otherwise the eval's 1024.

    Returns ``(size, source)`` — source is ``"metadata_parsed"`` (the
    metadata value drove the letterbox) or ``"fallback"`` (the metadata text
    is absent or unparseable and ``SFX_DEFAULT_IMGSZ`` was used). The REAL
    chiqui7 export records imgsz as a stringified JSON list —
    ``"[1024, 1024]"`` (the Ultralytics export shape, unlike a bare
    ``int(raw)``-parseable ``"768"``) — so the list form is parsed element by
    element and its primary (first) value taken (DSH r1 R4: the previous
    int-only parse silently fell back on every real export, and the options
    could not distinguish "metadata said 1024" from "metadata unparseable,
    defaulted 1024"). A fallback only degrades letterbox fidelity, it cannot
    mislabel a class — hence a default instead of a failure (unlike the
    ``names`` gate above); the caller records the source (and, on a fallback,
    the raw metadata text) in the detect options.
    """
    if raw:
        text = raw.strip()
        try:
            return int(text), SFX_IMGSZ_SOURCE_METADATA
        except ValueError:
            pass
        if text.startswith("[") and text.endswith("]"):
            values: list[int] = []
            for part in text[1:-1].split(","):
                try:
                    values.append(int(part.strip()))
                except ValueError:
                    break
            if values and len(values) == len(text[1:-1].split(",")):
                return values[0], SFX_IMGSZ_SOURCE_METADATA
    return SFX_DEFAULT_IMGSZ, SFX_IMGSZ_SOURCE_FALLBACK


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
        # Fail-fast BEFORE any inference (the TILING env discipline): an
        # illegal arbitration env must not produce a half-detected page.
        arb_enabled, arb_threshold = _arbitration_config()
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
        # Overlap arbitration: relabel primary candidates near-duplicated by
        # an sfx candidate into the ``sfx-arb-`` prefix (RegionType.SFX via
        # the existing prefix dispatch -> SfxPolicy gate). Directional by
        # design — the sfx provider is the SFX-specialist signal; the
        # sfx candidates themselves are never touched. Below-threshold
        # overlaps are diagnosed, not applied (the BJ13 misroute shape is
        # honestly unreachable until sfx recall exists).
        arbitration_options: tuple[tuple[str, str], ...] = (
            ("sfx_arbitration", "on" if arb_enabled else "off"),
        )
        primary_candidates = result.candidates
        if arb_enabled and sfx_candidates and primary_candidates:
            relabeled_count = 0
            max_partial = 0.0
            arbitrated_candidates: list[RegionCandidate] = []
            for candidate in primary_candidates:
                overlap = max(
                    _bbox_iou(candidate.polygon, sfx.polygon)
                    for sfx in sfx_candidates
                )
                if overlap >= arb_threshold:
                    relabeled_count += 1
                    arbitrated_candidates.append(
                        replace(
                            candidate,
                            provider_label=(
                                f"{ARBITRATED_LABEL_PREFIX}"
                                f"{candidate.provider_label}"
                            ),
                        )
                    )
                else:
                    if overlap > 0.0:
                        max_partial = max(max_partial, overlap)
                    arbitrated_candidates.append(candidate)
            arbitration_options = arbitration_options + (
                ("sfx_arbitration_threshold", str(arb_threshold)),
            )
            if relabeled_count:
                primary_candidates = tuple(arbitrated_candidates)
                arbitration_options = arbitration_options + (
                    ("sfx_arbitration_relabels", str(relabeled_count)),
                )
            elif max_partial > 0.0:
                arbitration_options = arbitration_options + (
                    (
                        "sfx_arbitration_partial_overlap",
                        f"{max_partial:.4f}",
                    ),
                )
        primary_elapsed = result.elapsed_ms or 0
        sfx_elapsed = sfx_result.elapsed_ms or 0
        return replace(
            result,
            candidates=primary_candidates + sfx_candidates,
            options=result.options
            + arbitration_options
            + (
                ("sfx_provider", sfx_result.provider_id),
                ("sfx_candidates", str(len(sfx_candidates))),
                ("sfx_conf_threshold", str(self.sfx.conf_threshold)),
            ),
            elapsed_ms=(primary_elapsed + sfx_elapsed) or None,
        )
