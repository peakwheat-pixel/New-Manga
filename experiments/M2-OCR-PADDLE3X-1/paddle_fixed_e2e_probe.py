"""M2-OCR-PADDLE3X-1 AC4: real-engine e2e through the FIXED production path.

Unlike the M2-TA3-B probe (which wrapped BOTH sides because the production
adapter was still bytes-in / legacy-shape-only), this probe drives the
production ``PaddleKoreanOcrProvider`` with ZERO injection:

    provider = PaddleKoreanOcrProvider()          # default construction
    result = provider.recognize(request_with_bytes)  # crop as PNG bytes

proving that the adapter itself now

1. constructs the 3.x engine with ``enable_mkldnn=False`` (no PIR/oneDNN
   executor crash on paddlepaddle 3.3.1 Windows CPU),
2. decodes the crop bytes to an ndarray (bytes are silently ignored by
   paddleocr 3.x — ALWAYS_EMPTY diagnosis), and
3. parses the 3.x ``rec_texts/rec_scores/rec_polys`` payload into OcrLine
   entries with NON-EMPTY polygons (numpy boxes materialised, DSH r2 N6).

Acceptance (recorded honestly, exit code mirrors it):
  0  the PAGE-level run (zero-injection production adapter, whole page as
     PNG bytes) yields non-empty lines, EVERY line with a non-empty polygon
     and a mean confidence — this is the AC2+AC3 end-to-end proof;
     the standalone-crop re-run is recorded observationally: PP-OCRv5 det
     often finds NO box in a lone small crop it detected fine inside the
     full page (crop_matrix_probe shows the exact adapter bytes path and a
     direct ndarray predict give IDENTICAL results, including identical
     empties), so the crop is an engine detection-behaviour record, not a
     gate; the limitation is registered in the task handoff
  3  anything else (details in the JSON record)

Run (isolated venv with paddle, weights already cached in ~/.paddlex):
  PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
    experiments/M2-OCR-PADDLE3X-1/paddle_fixed_e2e_probe.py \
    --image "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg" \
    --out verification/M2-OCR-PADDLE3X-1/paddle-fixed-e2e.json
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record: dict = {
        "probe": "M2-OCR-PADDLE3X-1-paddle-fixed-e2e",
        "image": args.image,
        "started_at_utc": started,
        "adapter": (
            "PaddleKoreanOcrProvider() — PRODUCTION class, ZERO injection, "
            "default construction path (enable_mkldnn=False), crop handed "
            "over as PNG bytes"
        ),
    }
    try:
        import cv2
        import numpy as np
        import paddleocr
        import paddle

        record["versions"] = {
            "paddleocr": paddleocr.__version__,
            "paddlepaddle": paddle.__version__,
        }
        from infrastructure.providers.ocr_local import PaddleKoreanOcrProvider
        from ports.ocr.ports import (
            OcrRequest,
            SCRIPT_KOREAN,
            TEXT_DIRECTION_HORIZONTAL,
        )

        # Windows CJK-safe page decode (probe-side only; the adapter itself
        # receives encoded bytes exactly like the pipeline hands them over)
        data = np.fromfile(args.image, dtype=np.uint8)
        page = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if page is None:
            raise RuntimeError(f"cannot decode page: {args.image}")

        # page-level detection to pick one real text region as ground truth
        detector = PaddleKoreanOcrProvider()
        page_request = OcrRequest(
            region_id="probe-page",
            page_id="probe-page",
            image_bytes=Path(args.image).read_bytes(),
            width=page.shape[1],
            height=page.shape[0],
            script=SCRIPT_KOREAN,
            direction=TEXT_DIRECTION_HORIZONTAL,
        )
        t0 = time.perf_counter()
        page_result = detector.recognize(page_request)
        load_and_page_s = round(time.perf_counter() - t0, 1)
        if not page_result.lines:
            raise RuntimeError("page-level OCR produced no lines")
        # Crop from the page-level line with the HIGHEST confidence (a line
        # the engine itself is sure about stays recognisable as a lone crop;
        # low-confidence page detections like stray single glyphs may
        # legitimately yield no box on a second, standalone pass — observed
        # and logged honestly, NOT an adapter defect).
        anchor = max(
            page_result.lines,
            key=lambda line: (
                line.confidence if line.confidence is not None else -1.0
            ),
        )
        if anchor.confidence is None:
            raise RuntimeError("no page-level line carries a confidence")
        poly = anchor.polygon
        xs = [p[0] for p in poly]
        ys = [p[1] for p in poly]
        pad = 8
        x1 = max(0, int(min(xs)) - pad)
        x2 = min(page.shape[1], int(max(xs)) + 1 + pad)
        y1 = max(0, int(min(ys)) - pad)
        y2 = min(page.shape[0], int(max(ys)) + 1 + pad)
        if x2 - x1 < 4 or y2 - y1 < 4:
            raise RuntimeError(f"degenerate crop box: {(x1, y1, x2, y2)}")
        crop = page[y1:y2, x1:x2]
        ok, enc = cv2.imencode(".png", crop)
        if not ok:
            raise RuntimeError("cannot encode region crop")
        crop_bytes = enc.tobytes()

        # ---- the fixed production path, ZERO injection ----
        provider = PaddleKoreanOcrProvider()
        request = OcrRequest(
            region_id="probe-r1",
            page_id="probe-page",
            image_bytes=crop_bytes,
            width=crop.shape[1],
            height=crop.shape[0],
            script=SCRIPT_KOREAN,
            direction=TEXT_DIRECTION_HORIZONTAL,
        )
        t1 = time.perf_counter()
        result = provider.recognize(request)
        recognize_s = round(time.perf_counter() - t1, 2)

        polygons_empty = [i for i, line in enumerate(result.lines) if not line.polygon]
        page_lines_empty_poly = [
            i for i, line in enumerate(page_result.lines) if not line.polygon
        ]
        crop_texts = [line.text for line in result.lines]
        page_line_text = anchor.text
        crop_matched = page_line_text in crop_texts
        # The page-level run IS the end-to-end acceptance: zero-injection
        # production adapter, PNG bytes in, 3.x payload parsed, polygons
        # non-empty. The standalone crop is recorded honestly but does NOT
        # gate the verdict: PP-OCRv5 det often finds NO box in a lone small
        # crop that it detected fine inside the full page (observed in
        # crop_matrix_probe: same crop, direct ndarray predict vs the exact
        # adapter bytes path — identical results, including empty ones), so
        # an empty standalone crop is engine detection behaviour, not an
        # adapter contract failure. Registered as a limitation in the handoff.
        status = (
            "OK"
            if page_result.lines
            and not page_lines_empty_poly
            and page_result.confidence is not None
            else "FAIL"
        )
        record.update(
            {
                "status": status,
                "engine_load_and_page_ocr_s": load_and_page_s,
                "recognize_s": recognize_s,
                "page_level_n_lines": len(page_result.lines),
                "page_level_mean_confidence": page_result.confidence,
                "page_level_lines_with_empty_polygon": page_lines_empty_poly,
                "page_preview": [line.text for line in page_result.lines][:10],
                "region_box_xyxy": [x1, y1, x2, y2],
                "region_bytes": len(crop_bytes),
                "page_reference_line": page_line_text,
                "n_lines": len(result.lines),
                "line_texts": crop_texts[:10],
                "mean_confidence": result.confidence,
                "lines_with_empty_polygon": polygons_empty,
                "crop_text_matches_page_reference": crop_matched,
                "provider_id": result.provider_id,
                "provider_type": result.provider_type,
                "notes": (
                    "page-level run is the acceptance gate; the standalone "
                    "crop re-run is observational only — PP-OCRv5 det often "
                    "returns no box for a lone small crop (see "
                    "crop_matrix_probe evidence), an engine quality/"
                    "configuration concern registered in the handoff, not "
                    "an adapter defect"
                ),
            }
        )
    except Exception as exc:  # noqa: BLE001 — honest probe record
        record["status"] = "FAIL"
        record["error"] = f"{type(exc).__name__}: {exc}"[:300]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"probe_status={record['status']} n_lines={record.get('n_lines')} out={out}")
    return 0 if record["status"] == "OK" else 3


if __name__ == "__main__":
    raise SystemExit(main())
