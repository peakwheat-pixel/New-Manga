"""Standalone packaged SFX-detect probe (M2-PROD-SFX-PROBE-1).

The fifth frozen sidecar entry (``sfx_detect_probe.exe`` in the packaged
onedir; dev form ``python -m bootstrap.sfx_detect_probe``). One-shot,
non-interactive, NOT part of the frozen stdio command surface — the
``bootstrap.core_service`` command dispatch table is untouched; this module
is reached only by running this entry directly, exactly like the launcher-side
``infrastructure.resource_channel.catalog_loader`` seeding CLI (the released
"standalone frozen entry exe, zero product command-surface extension"
precedent).

Purpose — the M2-PROD-DETECT-2 ruling ⑥ NOT_RUN slice: run ONE real,
production ``SfxDetectionProvider.detect`` (the SAME provider class the
``core.detect`` handler and the pipeline detect step resolve, assembly
semantics included: lazy runtime, SHA-256 supply-chain gate, typed
fail-closed) **inside the frozen process** against the in-bundle v2b weights
and print the audit JSON: candidate count, elapsed ms and the
``device`` / ``sfx_ep`` / ``sfx_ep_fallback`` provenance keys (the
M2-SFX-GPU-EP-1 three-key audit — expected release form is ``device=dml``
with no fallback; a wrapper-level CPU fallback, when it happens, is recorded
in the JSON verbatim and evaluated by the outer runner, never silently).

Weight resolution mirrors the production lookup order as far as a probe
without a data root can (``core_assembly._resolve_detector_weights_path``
order: explicit arg > ``NEWMANGA_SFX_WEIGHTS`` env (non-empty taken as-is,
the released override contract) > the frozen in-bundle copy
``Path(sys.executable).parent/models/detector/yolo11s-seg.onnx`` probed only
under ``sys.frozen``). A dev-form invocation without arg/env is a config
error, NOT a guess. A resolved-but-missing path is handed to the provider
verbatim so its own typed ``PROVIDER_NOT_CONFIGURED`` fail-closed semantics
surface through the probe JSON unchanged.

Input page: a programmatic synthetic comic page (zero assets, nothing on
disk, nothing in git) by default, or ``--page <png>`` to inject a real page
(the M2-SFX-T4-SWITCH v2b anchor page K07_R123 is the known-good candidate;
real pages stay in the gitignored task-envs tree — never copied into the
repository). The page is converted to the production raw-pixel ``page_frame``
contract (rgb24 bytes) exactly like the manga probe driver did.

Output contract (machine-readable): exactly one stdout line starting with
the marker ``SFX_PROBE_JSON: `` followed by compact JSON; human-readable
progress lines print before it. ``--out <path>`` additionally writes the
same JSON pretty-printed. Exit codes: ``0`` = the detect call completed and
the result JSON was produced (ANY candidate count is exit 0 — evaluating the
count is the outer runner's job, the probe never hides a zero); ``1`` = the
probe could not run (config error) or detect failed typed/untyped — the
error JSON carries the class / ``error_code`` / message head.

Build-tooling boundary: this module ships inside the frozen closure (the
spec pins ``onnxruntime`` for this entry and asserts the pyd + DirectML.dll
binaries at BUILD time); the probe adds no IPC command, touches no Tauri
surface and no contract DTO.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from infrastructure.providers.detection_manga import sha256_file
from infrastructure.providers.detection_sfx import (
    SFX_WEIGHTS_FILENAME,
    SFX_WEIGHTS_SHA256,
    SfxDetectionProvider,
)
from ports.detection.ports import DetectionRequest
from ports.providers.errors import ProviderError

PROBE_ID = "m2-prod-sfx-probe-1.sfx_detect_probe"
#: The single machine-readable stdout line marker (compact JSON follows).
JSON_MARKER = "SFX_PROBE_JSON: "

#: Frozen default conf threshold — the probe deliberately does NOT accept a
#: conf override: the release form always runs the production default
#: (``SFX_CONF_THRESHOLD`` = 0.5, precision-first ruling), and a probe that
#: could lower the gate would stop being evidence about the release form.

_SFX_ENV_WEIGHTS = "NEWMANGA_SFX_WEIGHTS"


class ProbeConfigError(Exception):
    """The probe invocation itself is unusable (no resolvable weights in the
    dev form) — an honest config error, distinct from a provider failure."""


# ---------------------------------------------------------------------------
# weight resolution (production order, probe-bounded)
# ---------------------------------------------------------------------------


def resolve_weights(
    explicit: str | None,
    env_value: str | None,
    frozen: bool,
) -> tuple[Path, str]:
    """Production lookup order, bounded to what a data-root-less probe can
    probe. Returns ``(path, resolved_from)`` with ``resolved_from`` in
    ``arg`` | ``env`` | ``bundle_probe``. The returned path MAY not exist —
    the provider's own typed fail-closed (``PROVIDER_NOT_CONFIGURED``) is the
    designed surfacing for that, verbatim from the release form. Only the
    dev form with NO arg and NO env raises :class:`ProbeConfigError` (the
    probe refuses to invent a data-root guess the production lookup would
    never take in this shape)."""
    if explicit:
        return Path(explicit), "arg"
    if env_value and env_value.strip():
        return Path(env_value), "env"
    bundle_candidate = (
        Path(sys.executable).resolve().parent / "models" / "detector" / SFX_WEIGHTS_FILENAME
    )
    if frozen:
        # Probed like the frozen assembly: when the in-bundle copy is absent
        # the candidate is still returned (resolved_from=bundle_probe) so the
        # provider's typed NOT_CONFIGURED — with its placement guidance — is
        # what the JSON records, exactly like the released lookup degrades.
        return bundle_candidate, "bundle_probe"
    raise ProbeConfigError(
        "no sfx weights resolvable for the probe: pass --weights, set "
        f"{_SFX_ENV_WEIGHTS} (non-empty), or run the frozen entry (the "
        "packaged onedir probes the in-bundle copy)"
    )


# ---------------------------------------------------------------------------
# input page (synthetic by default; zero assets in the repo)
# ---------------------------------------------------------------------------


def make_synthetic_page() -> tuple[bytes, int, int]:
    """A programmatic comic page with drawn sfx-like lettering: white
    background, panel borders and three large slanted "double-stroked"
    onomatopoeia blocks (the shape class the sfx detector is trained on:
    big, bold, jagged, stylized). Pure PIL, deterministic, no fonts on disk,
    nothing committed. Structural smoke input only — whether the v2b weights
    fire on a synthetic page is RECORDED, never asserted, by the runner
    (the synthetic page is outside the training distribution; the real-page
    scenario is the evidence face for the candidate count)."""
    from PIL import Image, ImageDraw, ImageFont

    width, height = 900, 1300
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    # panel frame, speech bubbles: shape context the detector sees in training
    draw.rectangle((40, 40, width - 40, height - 40), outline="black", width=6)
    draw.ellipse((120, 120, 420, 260), outline="black", width=6)
    draw.ellipse((480, 200, 780, 340), outline="black", width=6)
    try:
        font = ImageFont.load_default(size=110)
    except TypeError:  # Pillow < 10.1 fallback
        font = ImageFont.load_default()
    # three sfx-like blocks: slanted, double-stroked (fake bold via offsets),
    # varying rotation simulated by drawing per-x-line sheared text columns.
    for index, (label, cx, cy, shear) in enumerate(
        (("GOOO", 300, 620, 0.45), ("DOOOOON", 560, 900, -0.35), ("BAAAM", 380, 1130, 0.5)),
        start=1,
    ):
        bbox = draw.textbbox((0, 0), label, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # shear by drawing the text in one-pixel-tall columns offset per row
        # (PIL has no per-draw rotation; the shear reads as the stylized
        # sfx lettering silhouette)
        step = shear / max(th, 1)
        for offset in range(6):  # double-stroke: 6 offset passes = bold outline
            dx, dy = offset // 3, offset % 3
            for row in range(0, th, 2):
                x_shift = int((row - th / 2) * step)
                draw.text(
                    (cx - tw / 2 + x_shift + dx, cy - th / 2 + row + dy),
                    label,
                    fill="black",
                    font=font,
                )
    rgb = image.convert("RGB")
    return rgb.tobytes(), rgb.size[0], rgb.size[1]


def load_injected_page(page_path: Path) -> tuple[bytes, int, int]:
    """Read ``--page <png>`` into the production raw-pixel rgb24 contract."""
    from PIL import Image

    with Image.open(page_path) as im:
        rgb = im.convert("RGB")
        width, height = rgb.size
        return rgb.tobytes(), width, height


# ---------------------------------------------------------------------------
# provider construction seam (tests inject a fake-engine provider here)
# ---------------------------------------------------------------------------


def build_provider(weights_path: Path) -> SfxDetectionProvider:
    """The production provider construction — lazy runtime, SHA-256 gate and
    typed fail-closed semantics are all the provider's own; the probe adds
    nothing. (Injectable seam: tests monkeypatch this to hand back a
    provider whose ``_engine`` slot carries a fake session.)"""
    return SfxDetectionProvider(weights_path=weights_path)


# ---------------------------------------------------------------------------
# JSON plumbing
# ---------------------------------------------------------------------------


def _error_payload(error: BaseException) -> dict:
    """One failure shape for every error path: typed provider errors carry
    their ``error_code`` (``PROVIDER_NOT_CONFIGURED`` / ``PROVIDER_FAILED`` /
    ...); everything else records the exception class. Never a bare traceback
    as the only output — the JSON is the contract, the traceback (if any)
    rides stderr."""
    return {
        "class": type(error).__name__,
        "error_code": getattr(error, "error_code", None),
        "message_head": str(error)[:400],
    }


def _sha256_or_none(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return sha256_file(path)
    except OSError:
        return None


def run_probe(
    *,
    weights_path: Path,
    weights_source: str,
    page_bytes: bytes,
    page_width: int,
    page_height: int,
    page_source: str,
    page_path: Path | None,
    label: str,
) -> dict:
    """Run ONE production detect and build the probe JSON payload. Raises on
    provider failure — ``main`` turns that into the error JSON."""
    started = time.perf_counter()
    provider = build_provider(weights_path)
    request = DetectionRequest(
        page_id="sfx-probe-page",
        image_bytes=page_bytes,
        width=page_width,
        height=page_height,
    )
    result = provider.detect(request)
    wall_ms = int((time.perf_counter() - started) * 1000)
    options = dict(result.options)
    return {
        "probe": PROBE_ID,
        "label": label,
        "python": {"frozen": bool(getattr(sys, "frozen", False)), "executable": str(sys.executable)},
        "page": {
            "source": page_source,
            "path": str(page_path) if page_path else None,
            "width": page_width,
            "height": page_height,
            "sha256": hashlib.sha256(page_bytes).hexdigest(),
        },
        "weights": {
            "path": str(weights_path),
            "exists": weights_path.is_file(),
            "resolved_from": weights_source,
            "sha256": _sha256_or_none(weights_path),
            "expected_sha256": SFX_WEIGHTS_SHA256,
        },
        "provider": {
            "id": result.provider_id,
            "type": result.provider_type,
            "model": result.model,
            "conf_threshold": options.get("conf_threshold"),
        },
        "result": {
            "n_candidates": len(result.candidates),
            "elapsed_ms": result.elapsed_ms,
            "wall_ms_incl_provider_build": wall_ms,
            # the three-key EP audit (M2-SFX-GPU-EP-1) — the release-form
            # expectation is device=dml and NO sfx_ep_fallback key; a
            # wrapper-level CPU fallback records its reason here verbatim.
            "device": options.get("device"),
            "sfx_ep": options.get("sfx_ep"),
            "sfx_ep_fallback": options.get("sfx_ep_fallback"),
            "confidences": [candidate.confidence for candidate in result.candidates],
            "labels": [candidate.provider_label for candidate in result.candidates],
            "options": options,
        },
        "error": None,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sfx_detect_probe",
        description=(
            "One-shot frozen-process SFX detect probe (M2-PROD-SFX-PROBE-1): "
            "one production SfxDetectionProvider.detect against the in-bundle "
            "v2b weights, audit JSON on stdout."
        ),
    )
    parser.add_argument(
        "--page",
        type=Path,
        default=None,
        help="inject a real page (png/jpg) instead of the builtin synthetic page",
    )
    parser.add_argument(
        "--weights",
        default=None,
        help="explicit weights path (else NEWMANGA_SFX_WEIGHTS, else the frozen in-bundle probe)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="also write the probe JSON pretty-printed to this path",
    )
    parser.add_argument(
        "--label",
        default="synthetic",
        help="free-form label for the outer runner (e.g. synthetic | injected-real-page)",
    )
    args = parser.parse_args(argv)

    try:
        weights_path, weights_source = resolve_weights(
            args.weights, os.environ.get(_SFX_ENV_WEIGHTS), bool(getattr(sys, "frozen", False))
        )
        if args.page is not None:
            page_bytes, page_width, page_height = load_injected_page(args.page)
            page_source = "injected"
            page_path: Path | None = args.page
        else:
            page_bytes, page_width, page_height = make_synthetic_page()
            page_source = "builtin_synthetic"
            page_path = None
        payload = run_probe(
            weights_path=weights_path,
            weights_source=weights_source,
            page_bytes=page_bytes,
            page_width=page_width,
            page_height=page_height,
            page_source=page_source,
            page_path=page_path,
            label=args.label,
        )
        exit_code = 0
    except Exception as error:  # noqa: BLE001 - the probe's ONE failure shape
        payload = {
            "probe": PROBE_ID,
            "label": args.label,
            "python": {"frozen": bool(getattr(sys, "frozen", False)), "executable": str(sys.executable)},
            "page": None,
            "weights": None,
            "provider": None,
            "result": None,
            "error": _error_payload(error),
        }
        exit_code = 1
        print(
            f"sfx_detect_probe: FAILED ({payload['error']['class']}) — detail in the JSON line; "
            "traceback follows on stderr",
            file=sys.stderr,
        )
        import traceback

        traceback.print_exc()

    line = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    print(JSON_MARKER + line)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
