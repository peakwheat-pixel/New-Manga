"""M2-TA3-B phase-2 step-0 probe (DSH r1 R6 / integration closure item 5).

Drives the PRODUCTION adapter ``PaddleKoreanOcrProvider`` end-to-end on one
real region crop through a phase-2 wrapper that adapts BOTH sides:

- input side:  image bytes -> ndarray (cv2.imdecode), engine built with
  ``enable_mkldnn=False`` (paddlepaddle 3.3.1 Windows CPU PIR/oneDNN bug),
- output side: PaddleOCR 3.x ``rec_texts/rec_scores/rec_polys`` mapped back
  to the legacy nested shape ``[[ [box, (text, score)], ... ]]`` that
  ``_parse_paddle_output`` accepts. Boxes are materialised as plain Python
  lists on purpose: ``_polygon_of`` silently returns ``()`` for non-Sequence
  boxes, and numpy arrays are not ``collections.abc.Sequence`` (DSH r2 N6).

Acceptance (recorded honestly, exit code mirrors it):
  0  lines non-empty AND every line has a non-empty polygon
  2  adapter raised (expected pre-wrapper behaviour is NOT re-tested here;
     this probe only proves the wrapper path works)
  3  anything else failed

Run (isolated venv with paddle):
  PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
    experiments/M2-TA3-B/paddle_e2e_probe.py \
    --image "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg" \
    --out verification/M2-TA3-B/paddle-e2e-probe.json
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path


def build_wrapper(image_bytes: bytes):
    """Return an engine-like object whose ``ocr(bytes)`` maps 3.x -> legacy."""
    import cv2
    import numpy as np

    from paddleocr import PaddleOCR

    class Paddle3xToLegacyWrapper:
        """Phase-2 §2.2 wrapper sketch: bytes->ndarray in, legacy shape out."""

        def __init__(self) -> None:
            self._engine = PaddleOCR(
                lang="korean",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                enable_mkldnn=False,
            )

        def ocr(self, data: bytes):  # noqa: A002 - mirror adapter signature
            arr = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
            if arr is None:
                raise ValueError("cannot decode region crop bytes")
            results = self._engine.predict(arr)
            page: list[list] = []
            for res in results:
                payload = res if isinstance(res, dict) else getattr(res, "json", {})
                body = payload.get("res", payload) if isinstance(payload, dict) else {}
                texts = body.get("rec_texts", []) or []
                scores = body.get("rec_scores", []) or []
                polys = body.get("rec_polys", None)
                if polys is None:
                    polys = body.get("rec_boxes", None)
                if polys is None:
                    polys = [None] * len(texts)
                polys = _materialise_polys(polys)
                for i, text in enumerate(texts):
                    score = float(scores[i]) if i < len(scores) else 0.0
                    box = polys[i] if i < len(polys) else []
                    # legacy item: [box, (text, score)] — plain python only
                    page.append([box, (str(text), score)])
            return [page] if page else [None]

    def _materialise_polys(raw):  # numpy arrays -> plain lists (r2 N6)
        try:
            import numpy as _np

            if isinstance(raw, _np.ndarray):
                raw = raw.tolist()
        except Exception:  # noqa: BLE001
            pass
        out: list = []
        for item in raw:
            if hasattr(item, "tolist"):
                item = item.tolist()
            if item is None:
                out.append([])
            elif len(item) == 4 and all(isinstance(v, (int, float)) for v in item):
                x1, y1, x2, y2 = item  # xyxy box -> 4-point polygon
                out.append([[x1, y1], [x2, y1], [x2, y2], [x1, y2]])
            else:
                out.append(item)
        return out

    return Paddle3xToLegacyWrapper()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record: dict = {
        "probe": "paddle-e2e-step0",
        "image": args.image,
        "started_at_utc": started,
    }
    try:
        import cv2
        import numpy as np

        from infrastructure.providers.ocr_local import PaddleKoreanOcrProvider
        from ports.ocr.ports import (
            OcrRequest,
            SCRIPT_KOREAN,
            TEXT_DIRECTION_HORIZONTAL,
        )

        data = np.fromfile(args.image, dtype=np.uint8)
        page = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if page is None:
            raise RuntimeError(f"cannot decode page: {args.image}")

        t0 = time.perf_counter()
        wrapper = build_wrapper(page.tobytes())
        load_s = round(time.perf_counter() - t0, 1)

        # one real region crop: take the largest text-line box the engine just
        # found on the full page, crop it from the page, keep the PNG bytes
        results = wrapper._engine.predict(page)
        body = {}
        for res in results:
            payload = res if isinstance(res, dict) else getattr(res, "json", {})
            body = payload.get("res", payload) if isinstance(payload, dict) else body
        polys = body.get("rec_polys") or body.get("rec_boxes")
        texts = body.get("rec_texts", []) or []
        if polys is None or not len(polys):
            raise RuntimeError(f"engine found no text boxes on the page: keys={sorted(body)}")
        poly0 = polys[0].tolist() if hasattr(polys[0], "tolist") else list(polys[0])
        if len(poly0) == 4 and all(isinstance(v, (int, float)) for v in poly0):
            xs = [poly0[0], poly0[2]]
            ys = [poly0[1], poly0[3]]
        else:
            xs = [p[0] for p in poly0]
            ys = [p[1] for p in poly0]
        x1, x2 = max(0, int(min(xs))), min(page.shape[1], int(max(xs)) + 1)
        y1, y2 = max(0, int(min(ys))), min(page.shape[0], int(max(ys)) + 1)
        crop = page[y1:y2, x1:x2]
        ok, enc = cv2.imencode(".png", crop)
        if not ok:
            raise RuntimeError("cannot encode region crop")
        crop_bytes = enc.tobytes()

        provider = PaddleKoreanOcrProvider(engine_factory=lambda: build_wrapper(crop_bytes))
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
        infer_s = round(time.perf_counter() - t1, 2)

        polygons_empty = [i for i, line in enumerate(result.lines) if not line.polygon]
        record.update(
            {
                "status": "OK" if result.lines and not polygons_empty else "FAIL",
                "engine_load_s": load_s,
                "recognize_s": infer_s,
                "region_box_xyxy": [x1, y1, x2, y2],
                "region_bytes": len(crop_bytes),
                "n_lines": len(result.lines),
                "line_texts": [line.text for line in result.lines][:10],
                "mean_confidence": result.confidence,
                "lines_with_empty_polygon": polygons_empty,
                "page_reference_text_line0": str(texts[0]) if texts else "",
                "adapter": "PaddleKoreanOcrProvider(engine_factory=wrapper) — PRODUCTION class",
                "notes": "3.x->legacy dual-side wrapper; boxes materialised to plain lists (r2 N6)",
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
