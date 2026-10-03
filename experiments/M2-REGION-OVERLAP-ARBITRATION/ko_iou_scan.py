"""M2-REGION-OVERLAP-ARBITRATION r1 P1-2: KO-domain evidence sweep.

DSH r1 requires the KO qualification family (the 10 KO cases of the
M2-TA3-B case-selection: K01 K02 K04 K05 K07 K08 K09 K10 K11 K19) to be
swept at the DETECT layer with the production composite
(ogkalu primary + chiqui7 sfx), twice per case (arbitration OFF vs ON):

  - the sfx x primary candidate IoU distribution upper bound per case (a
    pair >= the frozen 0.90 would be a STOP condition — threshold domain
    must be re-audited);
  - the OFF/ON candidate fingerprint must be bit-identical per case.

Pages resolve through ``experiments/M2-TA3-B/case-selection.json``
(``page_path``; legacy main-repo paths fall back to the
M2-TA2B-OPEN-ASSETS worktree root, verified by the recorded page sha256).
K01-K10 are webtoon long strips (production tiling path), K11/K19 are
paged webcomics. Each case result is persisted to
``verification/M2-REGION-OVERLAP-ARBITRATION/raw/ko-scan/<case>.json``
so interrupted runs resume without re-paying finished inference.
"""

from __future__ import annotations

import hashlib
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
)
from ports.detection.ports import DetectionRequest  # noqa: E402

OGKALU_WEIGHTS_DIR = Path(
    "G:/CODEX/New Manga.task-envs/M2-DOCTR-QUAL-C4/weights/"
    "ogkalu-comic-text-and-bubble-detector"
)
SFX_WEIGHTS = Path(
    "G:/CODEX/New Manga.task-envs/M2-SFX-DETECT/weights/yolo11s-seg.onnx"
)
SELECTION = REPO_ROOT / "experiments/M2-TA3-B/case-selection.json"
ASSET_FALLBACK_ROOT = Path(
    "G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode/"
    "test_assets/comic_golden_suite"
)
RAW_DIR = REPO_ROOT / "verification/M2-REGION-OVERLAP-ARBITRATION/raw/ko-scan"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_page(entry: dict) -> tuple[Path, bool]:
    """Resolve the case page; legacy main-repo paths fall back to the
    open-assets worktree (same relative tail), sha256-verified."""
    raw = Path(entry["page_path"])
    if raw.is_file():
        return raw, _sha256(raw) == entry["page_sha256"]
    marker = "test_assets" + os.sep + "comic_golden_suite" + os.sep
    text = str(raw)
    if marker in text:
        tail = text.split(marker, 1)[1]
        candidate = ASSET_FALLBACK_ROOT / tail
        if candidate.is_file():
            return candidate, _sha256(candidate) == entry["page_sha256"]
    raise FileNotFoundError(f"page for {entry['case_id']} not resolvable: {raw}")


def _request(png: Path, page_id: str) -> DetectionRequest:
    from PIL import Image

    Image.MAX_IMAGE_PIXELS = None  # K01/K07 long strips exceed the default guard
    with Image.open(png) as image:
        rgb = image.convert("RGB")
        width, height = rgb.size
        data = rgb.tobytes()
    return DetectionRequest(
        page_id=page_id, image_bytes=data, width=width, height=height
    )


def _fingerprint(result) -> list[dict]:
    return [
        {
            "label": c.provider_label,
            "reading_order": c.reading_order,
            "confidence": c.confidence,
            "polygon": [[x, y] for x, y in c.polygon],
        }
        for c in result.candidates
    ]


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


def scan_case(composite, case_id: str, png: Path, sha_ok: bool) -> dict:
    request = _request(png, case_id)
    os.environ["NEWMANGA_SFX_ARBITRATION"] = "off"
    t0 = time.perf_counter()
    result_off = composite.detect(request)
    elapsed_off = round(time.perf_counter() - t0, 1)
    os.environ.pop("NEWMANGA_SFX_ARBITRATION", None)
    t0 = time.perf_counter()
    result_on = composite.detect(request)
    elapsed_on = round(time.perf_counter() - t0, 1)

    fp_off, fp_on = _fingerprint(result_off), _fingerprint(result_on)
    primary = [c for c in result_on.candidates if c.provider_label.startswith("manga-")]
    sfx = [c for c in result_on.candidates if c.provider_label.startswith("sfx-")]
    pairs = []
    for s in sfx:
        sb = _poly_bbox(s.polygon)
        for p in primary:
            iou = _iou(sb, _poly_bbox(p.polygon))
            if iou > 0.0:
                pairs.append(round(iou, 4))
    pairs.sort(reverse=True)
    options_on = dict(result_on.options)
    return {
        "case_id": case_id,
        "page": str(png),
        "page_sha256_match": sha_ok,
        "page_size": [request.width, request.height],
        "tiling": options_on.get("tiling"),
        "tiling_tiles": options_on.get("tiling_tiles"),
        "elapsed_off_s": elapsed_off,
        "elapsed_on_s": elapsed_on,
        "candidates_off": len(fp_off),
        "candidates_on": len(fp_on),
        "bit_identical": fp_off == fp_on,
        "primary_count": len(primary),
        "sfx_count": len(sfx),
        "sfx_x_primary_max_iou": pairs[0] if pairs else 0.0,
        "sfx_x_primary_top5": pairs[:5],
        "sfx_x_primary_intersecting_pairs": len(pairs),
        "threshold_violation_ge_090": bool(pairs and pairs[0] >= ARBITRATION_IOU),
        "options_on_sfx_arbitration": options_on.get("sfx_arbitration"),
        "options_on_relabels": options_on.get("sfx_arbitration_relabels"),
    }


def main() -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(SELECTION, encoding="utf-8") as handle:
        selection = json.load(handle)
    ko = [e for e in selection["cases"] if e["case_id"].startswith("K")]
    ko.sort(key=lambda e: (e["layout_type"] != "paged_webcomic", e["case_id"]))
    composite = MangaSfxParallelDetectionProvider(
        primary=MangaDetectionProvider(weights_dir=OGKALU_WEIGHTS_DIR, device="cpu"),
        sfx=SfxDetectionProvider(weights_path=SFX_WEIGHTS),
    )
    summary = {"cases": [], "started_at_utc": datetime.now(timezone.utc).isoformat()}
    for entry in ko:
        case_id = entry["case_id"]
        out = RAW_DIR / f"{case_id}.json"
        if out.is_file():
            with open(out, encoding="utf-8") as handle:
                record = json.load(handle)
            print(f"[{case_id}] cached (skip)", flush=True)
        else:
            png, sha_ok = _resolve_page(entry)
            record = scan_case(composite, case_id, png, sha_ok)
            with open(out, "w", encoding="utf-8") as handle:
                json.dump(record, handle, ensure_ascii=False, indent=1)
        summary["cases"].append(record["case_id"])
        print(
            f"[{record['case_id']}] off={record['candidates_off']} "
            f"on={record['candidates_on']} identical={record['bit_identical']} "
            f"sfx={record['sfx_count']} primary={record['primary_count']} "
            f"max_iou={record['sfx_x_primary_max_iou']} "
            f"tiling={record.get('tiling')}/{record.get('tiling_tiles')} "
            f"({record['elapsed_off_s']}s/{record['elapsed_on_s']}s)",
            flush=True,
        )
        if record["threshold_violation_ge_090"]:
            print(
                f"STOP CONDITION: {case_id} has an sfx x primary pair >= "
                f"{ARBITRATION_IOU} — threshold domain must be re-audited",
                flush=True,
            )
    with open(RAW_DIR / "summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=1)
    print("ko-scan complete ->", RAW_DIR, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
