"""M2-REGION-OVERLAP-ARBITRATION: AC2 red/green + AC3 zero-change evidence.

Read-only driver over the PRODUCTION detect chain (zero src changes; the
arbitration under test lives in ``MangaSfxParallelDetectionProvider.detect``):

  1. BJ13 real rerun (ogkalu primary + chiqui7 sfx, real pinned weights) —
     the RED face: the misrouted text candidates that become SPEECH regions
     (qual-BJ13 ffed29e8/de83b0c4, the "いやー、" / "Ｗｉｆｉｘ" garbage
     translation path) plus the honest UNREACHABLE evidence: today's sfx
     channel has zero candidates near the SFX shapes, so no overlap
     arbitration can fire (DOMAIN-EXT-DIAG: the out-of-domain root cause is
     recall, NOT this Task's scope).
  2. Synthetic recall-restored calibers on the REAL BJ13 candidates (zero
     extra inference — the real candidate sets are replayed through the
     composite with a stand-in sfx provider):
       - caliber A (visual reference boxes = restored sfx candidates): the
         honest partial-overlap outcome — IoU 0.49-0.55 stays below the
         frozen 0.9 domain, diagnosed, NOT relabeled;
       - caliber B (near-duplicate double detection, the shape the frozen
         domain closes): the GREEN face — the primary candidate is relabeled
         to ``sfx-arb-`` and the production label dispatch lands it in
         RegionType.SFX, where the SfxPolicy gate (default SKIP) governs.
  3. BJ06 zero-change: the composite run with arbitration OFF vs ON must
     produce a bit-identical candidate set (in-domain worst pair 0.8862 is
     below the frozen 0.9), aligned against the committed qual-BJ06 run.
  4. BJ14/BJ15: the bubble-dominant and carrier-less unreachable shapes,
     registered from the same real rerun (no fabricated coverage).

Outputs land in verification/M2-REGION-OVERLAP-ARBITRATION/raw/.
"""

from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from infrastructure.providers.detection_manga import (  # noqa: E402
    MangaDetectionProvider,
)
from infrastructure.providers.detection_sfx import (  # noqa: E402
    ARBITRATION_IOU,
    MangaSfxParallelDetectionProvider,
    SfxDetectionProvider,
    _arbitration_config,
)
from bootstrap.core_assembly import _detected_region_type  # noqa: E402
from ports.detection.ports import (  # noqa: E402
    DetectionRequest,
    DetectionResult,
    RegionCandidate,
)

OGKALU_WEIGHTS_DIR = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/"
    "ogkalu-comic-text-and-bubble-detector"
)
SFX_WEIGHTS = Path(
    "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx"
)

#: Committed qualification runs (the production baseline each rerun aligns to).
QUAL = {
    "BJ13": REPO_ROOT
    / "verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/qual-BJ13.json",
    "BJ14": REPO_ROOT
    / "verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/qual-BJ14.json",
    "BJ15": REPO_ROOT
    / "verification/M2-SFX-E2E-MATERIAL/new-assets-run/summaries/qual-BJ15.json",
    "BJ06": REPO_ROOT
    / "verification/M2-SFX-E2E-MATERIAL/bj06-run/summaries/qual-BJ06.json",
}

#: Visual SFX reference boxes (DOMAIN-EXT-DIAG / diagnose_sfx_detect.py —
#: zoom-confirmed approximations in source pixels).
REFERENCE_SFX = {
    "BJ13": [(2210, 240, 2560, 1000), (420, 2560, 760, 3400)],
    "BJ14": [(1230, 300, 1520, 950), (400, 1900, 700, 2560), (1900, 2260, 2200, 2900)],
    "BJ15": [(1600, 200, 1900, 800), (900, 1650, 1150, 2200)],
}

RAW_DIR = REPO_ROOT / "verification" / "M2-REGION-OVERLAP-ARBITRATION" / "raw"


def _page_request(png: Path, page_id: str) -> DetectionRequest:
    from PIL import Image

    with Image.open(png) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        data = rgb.tobytes()
    return DetectionRequest(
        page_id=page_id, image_bytes=data, width=width, height=height
    )


def _cand_dump(candidate: RegionCandidate) -> dict:
    xs = [p[0] for p in candidate.polygon]
    ys = [p[1] for p in candidate.polygon]
    return {
        "label": candidate.provider_label,
        "reading_order": candidate.reading_order,
        "confidence": candidate.confidence,
        "bbox": [
            round(min(xs), 1),
            round(min(ys), 1),
            round(max(xs), 1),
            round(max(ys), 1),
        ],
        "polygon": [
            [round(x, 1), round(y, 1)] for x, y in candidate.polygon
        ],
    }


def _poly_bbox(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return (min(xs), min(ys), max(xs), max(ys))


def _iou(a, b) -> float:
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b
    iw = max(0.0, min(ax1, bx1) - max(ax0, bx0))
    ih = max(0.0, min(ay1, by1) - max(ay0, by0))
    inter = iw * ih
    union = (ax1 - ax0) * (ay1 - ay0) + (bx1 - bx0) * (by1 - by0) - inter
    return inter / union if union > 0 else 0.0


class _ReplayPrimary:
    """Replays a cached real primary result (zero inference)."""

    def __init__(self, result):
        self.result = result
        self.provider_id = result.provider_id
        self.provider_type = result.provider_type
        self.model = result.model

    def detect(self, request):
        return self.result


class _ReplaySfx:
    """Replays a cached real sfx result merged with EXTRA synthetic
    candidates (stand-in for a restored sfx channel; zero inference)."""

    def __init__(self, result, extra):
        self.result = result
        self.provider_id = result.provider_id
        self.provider_type = result.provider_type
        self.model = result.model
        self.conf_threshold = 0.5

    def detect(self, request):
        return self.result


def _regions_summary(qual_path: Path) -> dict:
    with open(qual_path, encoding="utf-8") as handle:
        data = json.load(handle)
    regions = data["regions"]
    return {
        "count": len(regions),
        "sfx": sum(1 for r in regions if r["region_type"] == "sfx"),
        "speech": sum(1 for r in regions if r["region_type"] == "speech"),
        "bboxes": [
            [r["bbox"]["x"], r["bbox"]["y"], r["bbox"]["width"], r["bbox"]["height"]]
            for r in regions
        ],
    }


def main() -> int:
    started = time.perf_counter()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "task": "M2-REGION-OVERLAP-ARBITRATION",
        "script": "experiments/M2-REGION-OVERLAP-ARBITRATION/arbitrate_bj13.py",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_arbitration_iou": ARBITRATION_IOU,
        "arbitration_config_default": list(_arbitration_config()),
        "weights": {
            "ogkalu_dir": str(OGKALU_WEIGHTS_DIR),
            "chiqui7": str(SFX_WEIGHTS),
        },
        "pages": {},
    }
    page_pngs = {}
    for case, qual_path in QUAL.items():
        with open(qual_path, encoding="utf-8") as handle:
            page_pngs[case] = json.load(handle)["source_path"]

    providers = MangaSfxParallelDetectionProvider(
        primary=MangaDetectionProvider(weights_dir=OGKALU_WEIGHTS_DIR, device="cpu"),
        sfx=SfxDetectionProvider(weights_path=SFX_WEIGHTS),
    )

    raw_results: dict[str, dict] = {}

    # -- 1/3/4: one real composite run per page (arbitration env: unset=on) --
    for case in ("BJ13", "BJ14", "BJ15", "BJ06"):
        png = page_pngs[case]
        request = _page_request(Path(png), case)
        t0 = time.perf_counter()
        result = providers.detect(request)
        elapsed = round(time.perf_counter() - t0, 1)
        primary = [c for c in result.candidates if c.provider_label.startswith("manga-")]
        sfx = [c for c in result.candidates if c.provider_label.startswith("sfx-")]
        options = dict(result.options)
        primary_bboxes = [_poly_bbox(c.polygon) for c in primary]
        entry: dict = {
            "source": png,
            "page_size": [request.width, request.height],
            "detect_elapsed_s": elapsed,
            "options": options,
            "primary_count": len(primary),
            "sfx_count": len(sfx),
            "candidates": [_cand_dump(c) for c in result.candidates],
            "qual_baseline": _regions_summary(QUAL[case]),
        }
        # Misroute / reference-box overlap analysis against the visual
        # reference boxes (the honest unreachable evidence).
        refs = REFERENCE_SFX.get(case, [])
        ref_analysis = []
        for ri, ref in enumerate(refs, start=1):
            best = None
            for cand in primary:
                iou = _iou(ref, _poly_bbox(cand.polygon))
                if best is None or iou > best[0]:
                    best = (iou, cand.provider_label)
            ref_analysis.append(
                {
                    "ref_index": ri,
                    "ref_xyxy": list(ref),
                    # P4-4: a zero-intersection reference box carries an
                    # explicit null label (no best candidate exists), not a
                    # falsy-value coercion of the IoU float.
                    "best_primary_label": best[1] if best and best[0] > 0.0 else None,
                    "best_iou": round(best[0], 4) if best else 0.0,
                }
            )
        entry["reference_overlap"] = ref_analysis
        # In-domain calibration face (BJ06): worst sfx x primary IoU.
        sfx_bboxes = [_poly_bbox(c.polygon) for c in sfx]
        pairs = [
            round(_iou(s, p), 4) for s in sfx_bboxes for p in primary_bboxes
        ]
        entry["sfx_x_primary_max_iou"] = max(pairs, default=0.0)
        entry["sfx_x_primary_intersecting_pairs"] = sum(1 for v in pairs if v > 0)
        raw_results[case] = entry
        manifest["pages"][case] = {
            "detect_elapsed_s": elapsed,
            "primary": len(primary),
            "sfx": len(sfx),
            "sfx_arbitration": options.get("sfx_arbitration"),
            "sfx_arbitration_relabels": options.get("sfx_arbitration_relabels"),
            "sfx_arbitration_partial_overlap": options.get(
                "sfx_arbitration_partial_overlap"
            ),
        }
        print(
            f"[{case}] primary={len(primary)} sfx={len(sfx)} "
            f"arb={options.get('sfx_arbitration')} "
            f"relabels={options.get('sfx_arbitration_relabels')} "
            f"partial={options.get('sfx_arbitration_partial_overlap')} "
            f"({elapsed}s)",
            flush=True,
        )

    # -- 2: BJ13 synthetic calibers on the REAL candidate sets (no inference)
    bj13 = raw_results["BJ13"]
    real_primary = [
        c for c in bj13["candidates"] if c["label"].startswith("manga-")
    ]
    real_sfx_result_candidates = [
        c for c in bj13["candidates"] if c["label"].startswith("sfx-")
    ]
    # Rebuild RegionCandidate objects from the dump (polygons are verbatim).
    def _from_dump(dump):
        return RegionCandidate(
            polygon=tuple(tuple(p) for p in dump["polygon"]),
            reading_order=dump["reading_order"],
            confidence=dump["confidence"],
            provider_label=dump["label"],
        )

    primary_cands = [_from_dump(d) for d in real_primary]
    sfx_cands_real = [_from_dump(d) for d in real_sfx_result_candidates]

    def _replay_sfx_with(extra_cands) -> _ReplaySfx:
        merged = DetectionResult(
            page_id="BJ13",
            candidates=tuple(sfx_cands_real + extra_cands),
            coordinate_space="page-global",
            provider_id="local-sfx",
            provider_type="local-sfx",
            model="sfx/yolo11s-seg.onnx",
            options=(("conf_threshold", "0.5"),),
            elapsed_ms=0,
        )
        return _ReplaySfx(merged, [])

    synthetic: dict[str, dict] = {}

    # Caliber A: visual reference boxes as the restored sfx candidates.
    ref_cands = [
        RegionCandidate(
            polygon=(
                (float(r[0]), float(r[1])),
                (float(r[2]), float(r[1])),
                (float(r[2]), float(r[3])),
                (float(r[0]), float(r[3])),
            ),
            reading_order=i + 1,
            confidence=0.99,
            provider_label=f"sfx-ref{i + 1}",
        )
        for i, r in enumerate(REFERENCE_SFX["BJ13"])
    ]
    os.environ.pop("NEWMANGA_SFX_ARBITRATION", None)
    os.environ.pop("NEWMANGA_SFX_ARBITRATION_IOU", None)
    replay_primary = DetectionResult(
        page_id="BJ13",
        candidates=tuple(primary_cands),
        coordinate_space="page-global",
        provider_id="local-manga",
        provider_type="local-manga",
        model="manga/ogkalu-comic-text-and-bubble-detector",
        options=(("replay", "real-bj13-primary"),),
        elapsed_ms=0,
    )
    # Two INDEPENDENT composite instances (P4-2): each caliber gets its own
    # stand-in sfx provider; no shared mutable replay state.
    caliber_a_composite = MangaSfxParallelDetectionProvider(
        primary=_ReplayPrimary(replay_primary),
        sfx=_replay_sfx_with(ref_cands),
    )
    result_a = caliber_a_composite.detect(
        DetectionRequest(page_id="BJ13", image_bytes=b"", width=2946, height=4167)
    )
    a_labels = [c.provider_label for c in result_a.candidates]
    a_options = dict(result_a.options)
    synthetic["caliber_A_reference_boxes"] = {
        "note": (
            "visual reference boxes as restored sfx candidates: the honest "
            "partial-overlap outcome (IoU 0.49-0.55 below the frozen 0.9)"
        ),
        "labels": a_labels,
        "relabels": a_options.get("sfx_arbitration_relabels"),
        "partial_overlap": a_options.get("sfx_arbitration_partial_overlap"),
    }

    # Caliber B: near-duplicate double detection (the frozen domain's shape).
    # For each primary candidate a co-located sfx candidate at 95% scale
    # (IoU ~0.90+) — what a restored sfx channel sees on a double-detected
    # artwork text.
    near_cands = []
    for i, dump in enumerate(real_primary[:3], start=1):
        x0, y0, x1, y1 = dump["bbox"]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        sx, sy = (x1 - x0) * 0.475, (y1 - y0) * 0.475
        near_cands.append(
            RegionCandidate(
                polygon=(
                    (cx - sx, cy - sy),
                    (cx + sx, cy - sy),
                    (cx + sx, cy + sy),
                    (cx - sx, cy + sy),
                ),
                reading_order=i,
                confidence=0.99,
                provider_label=f"sfx-near{i}",
            )
        )
    caliber_b_composite = MangaSfxParallelDetectionProvider(
        primary=_ReplayPrimary(replay_primary),
        sfx=_replay_sfx_with(near_cands),
    )
    result_b = caliber_b_composite.detect(
        DetectionRequest(page_id="BJ13", image_bytes=b"", width=2946, height=4167)
    )
    b_labels = [c.provider_label for c in result_b.candidates]
    b_options = dict(result_b.options)
    region_types_b = [
        {
            "label": c.provider_label,
            "region_type": _detected_region_type(c.provider_label).value,
        }
        for c in result_b.candidates
    ]
    synthetic["caliber_B_near_duplicate"] = {
        "note": (
            "near-duplicate double detections (IoU ~0.9+): the GREEN face — "
            "relabeled into the sfx- prefix, dispatched RegionType.SFX"
        ),
        "labels": b_labels,
        "relabels": b_options.get("sfx_arbitration_relabels"),
        "partial_overlap": b_options.get("sfx_arbitration_partial_overlap"),
        "region_types": region_types_b,
    }
    manifest["bj13_synthetic_calibers"] = synthetic

    # -- 3: BJ06 arbitration OFF vs ON bit-identical candidates --
    os.environ["NEWMANGA_SFX_ARBITRATION"] = "off"
    request_bj06 = _page_request(Path(page_pngs["BJ06"]), "BJ06-off")
    t0 = time.perf_counter()
    result_off = providers.detect(request_bj06)
    elapsed_off = round(time.perf_counter() - t0, 1)
    os.environ.pop("NEWMANGA_SFX_ARBITRATION", None)
    request_bj06_on = _page_request(Path(page_pngs["BJ06"]), "BJ06-on")
    result_on = providers.detect(request_bj06_on)

    def _fingerprint(res):
        return [
            {
                "label": c.provider_label,
                "reading_order": c.reading_order,
                "confidence": c.confidence,
                "polygon": [[x, y] for x, y in c.polygon],
            }
            for c in res.candidates
        ]

    fp_off, fp_on = _fingerprint(result_off), _fingerprint(result_on)
    identical = fp_off == fp_on
    manifest["bj06_zero_change"] = {
        "off_elapsed_s": elapsed_off,
        "candidates_off": len(fp_off),
        "candidates_on": len(fp_on),
        "bit_identical_candidates": identical,
        "options_off_sfx_arbitration": dict(result_off.options).get(
            "sfx_arbitration"
        ),
        "options_on_sfx_arbitration": dict(result_on.options).get(
            "sfx_arbitration"
        ),
        "options_on_partial_overlap": dict(result_on.options).get(
            "sfx_arbitration_partial_overlap"
        ),
        "qual_alignment": {
            "qual_count": raw_results["BJ06"]["qual_baseline"]["count"],
            "rerun_candidates": len(fp_on),
        },
    }
    print(
        f"[BJ06 zero-change] off={len(fp_off)} on={len(fp_on)} "
        f"identical={identical}",
        flush=True,
    )
    with open(RAW_DIR / "bj06-on-off-candidates.json", "w", encoding="utf-8") as h:
        json.dump(
            {"off": fp_off, "on": fp_on}, h, ensure_ascii=False, indent=1
        )

    # Full per-page dumps + manifest.
    with open(RAW_DIR / "arbitrate-pages.json", "w", encoding="utf-8") as h:
        json.dump(raw_results, h, ensure_ascii=False, indent=1)
    manifest["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest["wall_s"] = round(time.perf_counter() - started, 1)
    with open(RAW_DIR / "arbitrate-manifest.json", "w", encoding="utf-8") as h:
        json.dump(manifest, h, ensure_ascii=False, indent=1)
    print("manifest ->", RAW_DIR / "arbitrate-manifest.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
