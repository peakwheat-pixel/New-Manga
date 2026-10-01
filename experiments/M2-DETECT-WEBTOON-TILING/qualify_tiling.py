"""M2-DETECT-WEBTOON-TILING qualification (AC3, the DIAG frozen criteria).

Runs the PRODUCTION ``MangaDetectionProvider.detect`` — the tiled path
landed in ``src/infrastructure/providers/detection_manga.py`` — over the
five ``webtoon_long_strip`` pages of the TA3-B selection (K01/K02/K04/
K05/K08) with the real pinned ogkalu weights, and records:

- **Gate**: every webtoon page must produce region_count > 0 at the
  production level (post-merge ``candidates`` of ``provider.detect``);
  the pre-merge text-box count rides along in the detect ``options``
  (``text_boxes_pre_merge``) so both levels are reported from ONE
  production call;
- the CPU latency of that production call against the budget K01 <= 25 s /
  K02 <= 10 s / K04 <= 15 s (a budget overrun is REGISTERED as a number,
  never judged FAIL here — the budget is release-shape input);
- the >= 2 threshold-point candidate curve (conf 0.5 = production vs
  0.4): the 0.5 point is the production detect itself; the 0.4 point
  reuses the same tiled code with ``threshold=0.4`` and reports both the
  pre-merge box count and the post-merge region count (the production
  ``cluster_words_into_blocks``, applied to the threshold-0.4 boxes);
- the 690x690 native-scale control on K01 (~1.0x resampling, ~1.6x the
  tiles): if native-scale tiles recover detections in the same order of
  magnitude as the 1024 tiles, the resolution hypothesis (the whole-page
  640x640 crush, not the content, killed the signal) is confirmed;
- K19 (a text-free paged_webcomic page): still 0 candidates — the
  correct adapter behavior (the typed INVALID_INPUT lives in the
  handler; the F4 caliber defect is registered adjacent, NOT fixed here);
- BJ02 (the normal-page control): region count identical to the DIAG
  probe (5) and ``tiling=off`` — normal pages are byte-identical.

Zero ``src``/``tests`` changes: the production provider is imported and
constructed exactly as the assembly does. Weights are verified against
the production sha256 pins before anything runs (fail-closed). Tiles are
cropped in memory only — nothing is written but the JSON report.

Run (main venv, CPU):

  "G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe" \
    experiments/M2-DETECT-WEBTOON-TILING/qualify_tiling.py \
    --output verification/M2-DETECT-WEBTOON-TILING/qualification-results.json
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

import numpy as np  # noqa: E402  (venv guarantees the torch stack)
from PIL import Image  # noqa: E402

from infrastructure.providers.detection_doctr import (  # noqa: E402
    cluster_words_into_blocks,
)
from infrastructure.providers.detection_manga import (  # noqa: E402
    MANGA_CONF_THRESHOLD,
    MANGA_CONFIG_SHA256,
    MANGA_MODEL_SHA256,
    MANGA_PREPROCESSOR_SHA256,
    MangaDetectionProvider,
    TilingConfig,
    _detect_text_boxes_tiled,
    _tiling_tiles,
    sha256_file,
)
from ports.detection.ports import DetectionRequest  # noqa: E402

#: The TA3-B manifest carrying the exact page paths + sha256 pins.
CASE_SELECTION = (
    REPO_ROOT / "experiments" / "M2-TA3-B" / "case-selection.json"
)

#: The AC3 Gate pages (webtoon_long_strip) + the two controls.
GATE_CASES = ("K01", "K02", "K04", "K05", "K08")
NATIVE_SCALE_CASE = "K01"  # the 690x690 control runs on this page only
K19_CASE = "K19"  # text-free control: 0 candidates is CORRECT here
BJ02_CASE = "BJ02"  # normal-page control: must equal the DIAG probe

#: CPU latency budgets (release-shape input; an overrun is registered,
#: never judged FAIL by this script).
LATENCY_BUDGET_S = {"K01": 25.0, "K02": 10.0, "K04": 15.0}

#: The second curve point (the production threshold 0.5 is the other).
CURVE_THRESHOLD_ALT = 0.4

#: The native-scale control tile size = the K01 page width (690): the
#: horizontal resampling becomes ~1.0x instead of 640/1024 = 0.625x.
NATIVE_SCALE_TILE = 690

#: The local pinned snapshot (the DIAG probe's path; sha256-verified
#: against the production pins by the provider loader itself).
DEFAULT_WEIGHTS_DIR = Path(
    r"G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights"
    "/ogkalu-comic-text-and-bubble-detector"
)


def load_page_rgb(path: Path) -> tuple[np.ndarray, str]:
    """Decode one page to an HxWx3 uint8 RGB array + its file sha256."""
    import hashlib

    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    with Image.open(path) as im:
        rgb = np.asarray(im.convert("RGB"))
    return rgb, digest


def production_detect(
    provider: MangaDetectionProvider, rgb: np.ndarray, page_id: str
) -> tuple[dict, object]:
    """One production ``provider.detect`` call (the Gate measurement)."""
    height, width = int(rgb.shape[0]), int(rgb.shape[1])
    request = DetectionRequest(
        page_id=page_id,
        image_bytes=np.ascontiguousarray(rgb).tobytes(),
        width=width,
        height=height,
    )
    started = time.perf_counter()
    result = provider.detect(request)
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    options = dict(result.options)
    report = {
        "region_count": len(result.candidates),
        "elapsed_ms": elapsed_ms,
        "text_boxes_pre_merge": int(options.get("text_boxes_pre_merge", "-1")),
        "tiling": options.get("tiling"),
        "tiling_tiles": options.get("tiling_tiles"),
        "conf_threshold": options.get("conf_threshold"),
        "bubble_class_dropped": options.get("bubble_class_dropped"),
        "confidences": [
            float(c.confidence) for c in result.candidates if c.confidence is not None
        ],
    }
    return report, result


def curve_point(
    model, processor, rgb: np.ndarray, threshold: float, config: TilingConfig
) -> dict:
    """One threshold curve point at the pre-merge AND post-merge level.

    The 0.4 point reuses the production tiled code with a lower threshold;
    the post-merge count applies the production ``cluster_words_into_blocks``
    to the resulting boxes — the same merge the 0.5 detect ran internally.
    """
    height, width = int(rgb.shape[0]), int(rgb.shape[1])
    started = time.perf_counter()
    boxes, n_bubble = _detect_text_boxes_tiled(
        model,
        processor,
        rgb,
        float(width),
        float(height),
        config,
        threshold=threshold,
    )
    elapsed_ms = int((time.perf_counter() - started) * 1000)
    blocks = cluster_words_into_blocks(
        [(b[0], b[1], b[2], b[3]) for b in boxes],
        [b[4] for b in boxes],
        page_size=(float(width), float(height)),
    )
    confs = [b[4] for b in boxes]
    return {
        "threshold": threshold,
        "text_boxes_pre_merge": len(boxes),
        "region_count_post_merge": len(blocks),
        "n_bubble_dropped": n_bubble,
        "elapsed_ms": elapsed_ms,
        "conf_max": max(confs) if confs else 0.0,
        "conf_min": min(confs) if confs else 0.0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--weights-dir",
        default=os.environ.get("NEWMANGA_DETECTOR_WEIGHTS", str(DEFAULT_WEIGHTS_DIR)),
        help="pinned ogkalu snapshot directory (env NEWMANGA_DETECTOR_WEIGHTS)",
    )
    parser.add_argument("--device", default="cpu", help="cpu (GPU optional)")
    parser.add_argument(
        "--output",
        default=str(
            REPO_ROOT
            / "verification"
            / "M2-DETECT-WEBTOON-TILING"
            / "qualification-results.json"
        ),
    )
    args = parser.parse_args()

    weights_dir = Path(args.weights_dir)
    if not weights_dir.is_dir():
        print(f"FATAL: weights dir missing: {weights_dir}", file=sys.stderr)
        return 2

    import torch

    pins = {
        "model.safetensors": MANGA_MODEL_SHA256,
        "config.json": MANGA_CONFIG_SHA256,
        "preprocessor_config.json": MANGA_PREPROCESSOR_SHA256,
    }
    files = {}
    for filename, pin in pins.items():
        actual = sha256_file(weights_dir / filename)
        files[filename] = {"sha256": actual, "pin_match": actual == pin}
    weights_report = {
        "dir": str(weights_dir),
        "all_pins_match": all(f["pin_match"] for f in files.values()),
        "files": files,
    }
    if not weights_report["all_pins_match"]:
        print(
            "FATAL: weights sha256 pin mismatch — refusing to qualify "
            "unverified weights (production fail-closed semantics).",
            file=sys.stderr,
        )
        return 2

    # Production construction, verbatim (bootstrap.core_assembly); the env
    # tiling channel stays untouched — the defaults ARE the DIAG values.
    provider = MangaDetectionProvider(weights_dir=weights_dir, device=args.device)
    model, processor = provider._engine_or_raise()
    print(f"[qualify] torch {torch.__version__} device={args.device}", flush=True)
    print(f"[qualify] weights OK: {weights_dir}", flush=True)
    print(
        f"[qualify] tiling defaults: tile=1024 overlap=128 nms_iou=0.5 "
        f"trigger_ratio=4.0 (DIAG-frozen); conf {MANGA_CONF_THRESHOLD}",
        flush=True,
    )

    selection = json.loads(CASE_SELECTION.read_text("utf-8"))
    cases = {c["case_id"]: c for c in selection["cases"]}

    report: dict = {
        "task": "M2-DETECT-WEBTOON-TILING",
        "generated_at_utc": datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "torch": torch.__version__,
            "cuda_available": bool(torch.cuda.is_available()),
            "device": args.device,
            "transformers": __import__("transformers").__version__,
            "numpy": np.__version__,
        },
        "weights": weights_report,
        "case_selection_manifest": str(CASE_SELECTION),
        "conf_threshold_production": MANGA_CONF_THRESHOLD,
        "latency_budget_s": LATENCY_BUDGET_S,
        "curve_threshold_alt": CURVE_THRESHOLD_ALT,
        "native_scale_tile": NATIVE_SCALE_TILE,
        "gate": {},
        "pages": {},
    }

    # -- Gate: the five webtoon long-strip pages ---------------------------
    for case_id in GATE_CASES:
        case = cases[case_id]
        page_path = Path(case["page_path"])
        rgb, digest = load_page_rgb(page_path)
        sha_match = digest == case["page_sha256"]
        print(
            f"[qualify] {case_id}: {page_path.name} "
            f"{rgb.shape[1]}x{rgb.shape[0]} sha_match={sha_match}",
            flush=True,
        )
        page_report: dict = {
            "source_path": str(page_path),
            "source_sha256": digest,
            "source_sha256_matches_manifest": sha_match,
            "size_wh": [int(rgb.shape[1]), int(rgb.shape[0])],
            "layout_type": case["layout_type"],
        }
        if not sha_match:
            page_report["skipped_reason"] = "sha256 mismatch vs manifest"
            report["pages"][case_id] = page_report
            report["gate"][case_id] = "BLOCKED"
            continue

        detect_report, _result = production_detect(provider, rgb, case_id)
        page_report["provider_detect"] = detect_report
        region_count = detect_report["region_count"]
        budget = LATENCY_BUDGET_S.get(case_id)
        page_report["latency_budget_s"] = budget
        page_report["latency_within_budget"] = (
            None if budget is None else detect_report["elapsed_ms"] <= budget * 1000
        )
        page_report["gate_region_gt_0"] = region_count > 0
        report["pages"][case_id] = page_report
        report["gate"][case_id] = "PASS" if region_count > 0 else "FAIL"
        print(
            f"[qualify]   regions={region_count} "
            f"pre_merge_boxes={detect_report['text_boxes_pre_merge']} "
            f"tiles={detect_report['tiling_tiles']} "
            f"elapsed={detect_report['elapsed_ms']}ms "
            f"budget={'n/a' if budget is None else f'{budget}s'}",
            flush=True,
        )

        # threshold curve: 0.5 = the production detect above (from options)
        # + 0.4 = the same tiled code at the lower threshold
        alt = curve_point(
            model,
            processor,
            rgb,
            CURVE_THRESHOLD_ALT,
            TilingConfig(),  # the frozen defaults
        )
        page_report["curve"] = {
            "0.5": {
                "text_boxes_pre_merge": detect_report["text_boxes_pre_merge"],
                "region_count_post_merge": region_count,
                "source": "production provider.detect",
            },
            str(CURVE_THRESHOLD_ALT): alt,
        }
        print(
            f"[qualify]   curve: conf 0.5 -> boxes={detect_report['text_boxes_pre_merge']} "
            f"regions={region_count} | conf {CURVE_THRESHOLD_ALT} -> "
            f"boxes={alt['text_boxes_pre_merge']} "
            f"regions={alt['region_count_post_merge']}",
            flush=True,
        )

        if case_id == NATIVE_SCALE_CASE:
            tiles_native = _tiling_tiles(
                float(rgb.shape[1]), float(rgb.shape[0]), NATIVE_SCALE_TILE, 128
            )
            native = curve_point(
                model,
                processor,
                rgb,
                MANGA_CONF_THRESHOLD,
                TilingConfig(tile_size=NATIVE_SCALE_TILE, overlap=128),
            )
            native["n_tiles"] = len(tiles_native)
            page_report["native_scale_control"] = native
            print(
                f"[qualify]   690x690 control: tiles={native['n_tiles']} "
                f"boxes={native['text_boxes_pre_merge']} "
                f"regions={native['region_count_post_merge']} "
                f"elapsed={native['elapsed_ms']}ms",
                flush=True,
            )

    # -- K19: the text-free control (0 candidates is CORRECT) --------------
    case = cases[K19_CASE]
    rgb, digest = load_page_rgb(Path(case["page_path"]))
    detect_report, _result = production_detect(provider, rgb, K19_CASE)
    report["pages"][K19_CASE] = {
        "source_path": case["page_path"],
        "source_sha256": digest,
        "size_wh": [int(rgb.shape[1]), int(rgb.shape[0])],
        "layout_type": case["layout_type"],
        "provider_detect": detect_report,
        "expected_zero_candidates": True,
        "f4_note": (
            "0 candidates on a text-free page is the correct adapter "
            "behavior; the handler turning it into step=failed/"
            "INVALID_INPUT is the F4 caliber defect — registered "
            "adjacent, NOT fixed by this task."
        ),
    }
    print(
        f"[qualify] K19 (text-free): regions={detect_report['region_count']} "
        f"tiling={detect_report['tiling']}",
        flush=True,
    )

    # -- BJ02: the normal-page control (must equal the DIAG probe) ---------
    case = cases[BJ02_CASE]
    rgb, digest = load_page_rgb(Path(case["page_path"]))
    detect_report, _result = production_detect(provider, rgb, BJ02_CASE)
    diag_reference_region_count = 5
    report["pages"][BJ02_CASE] = {
        "source_path": case["page_path"],
        "source_sha256": digest,
        "size_wh": [int(rgb.shape[1]), int(rgb.shape[0])],
        "layout_type": case["layout_type"],
        "provider_detect": detect_report,
        "diag_probe_region_count": diag_reference_region_count,
        "matches_diag_probe": (
            detect_report["region_count"] == diag_reference_region_count
            and detect_report["tiling"] == "off"
        ),
    }
    print(
        f"[qualify] BJ02 (control): regions={detect_report['region_count']} "
        f"tiling={detect_report['tiling']} "
        f"matches_diag={report['pages'][BJ02_CASE]['matches_diag_probe']}",
        flush=True,
    )

    gate_values = list(report["gate"].values())
    overall = (
        "PASS"
        if gate_values and all(v == "PASS" for v in gate_values)
        else "FAIL"
    )
    report["gate"]["overall"] = overall
    report["gate"]["controls"] = {
        "K19_zero_candidates": report["pages"][K19_CASE][
            "provider_detect"
        ]["region_count"]
        == 0,
        "BJ02_unchanged": report["pages"][BJ02_CASE]["matches_diag_probe"],
    }

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[qualify] wrote {output_path}", flush=True)
    print(
        f"[qualify] GATE {overall}: "
        + ", ".join(f"{k}={v}" for k, v in report["gate"].items() if k != "overall"),
        flush=True,
    )
    return 0 if overall == "PASS" else 3


if __name__ == "__main__":
    sys.exit(main())
