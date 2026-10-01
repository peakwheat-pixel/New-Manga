"""M2-OCR-PADDLE3X-1 AC1: settle R10 — bytes path ALWAYS-EMPTY vs STALE-REUSE.

M2-TA3-B phase-1 observed (ocr_smoke.py ``adapter_seam_ocr_bytes``) that
``PaddleOCR.ocr(<raw bytes>)`` on paddleocr 3.x returns an exception-free
EMPTY result, but the underlying mechanism was left UNVERIFIED (DSH r1 R10):

- ``ALWAYS_EMPTY``: 3.x rejects/ignores the bytes input outright — silent
  empty OCR, bad but recoverable (typed failure surfaces once the adapter
  stops feeding bytes);
- ``STALE_REUSE``: the engine ignores the bytes argument and re-emits the
  PREVIOUS inference result — silent WRONG TEXT, a far more severe risk
  surface (historical outputs could have carried another region's text).

Probe design (exactly two DIFFERENT regions on the bytes path):

1. ``engine_ref``  — PaddleOCR(lang="korean", enable_mkldnn=False, ...):
   full-page ndarray inference to locate text boxes, then crop TWO regions
   with DIFFERENT text and run each crop as ndarray to fix ground truth
   (GT_A, GT_B). ``enable_mkldnn=False`` is needed only because ndarray
   inference hits the paddlepaddle 3.3.1 Windows CPU PIR/oneDNN bug; the
   bytes-path input-type rejection happens BEFORE any executor is invoked,
   so it cannot be affected by that switch (TA3-B phase-1 observed the same
   EMPTY seam result on this very construction).
2. ``engine_prod`` — PaddleOCR(lang="korean"): mirrors the production
   adapter default construction in ``ocr_local.PaddleKoreanOcrProvider``
   exactly (no mkldnn argument).
3. bytes path, back-to-back: ``engine_prod.ocr(A_bytes)`` then
   ``engine_prod.ocr(B_bytes)``; extract rec_texts from each raw payload.

Verdict matrix (recorded honestly, exit code 0 for every settled verdict —
a settled verdict IS the deliverable; 3 only on probe failure):
  T1 empty  and T2 empty            -> ALWAYS_EMPTY
  T2 non-empty and T2 matches GT_B  -> BYTES_OK (contradicts phase-1; flagged)
  T2 non-empty and T2 differs GT_B  -> STALE_REUSE (wrong-text risk flagged)
  anything else                     -> MIXED (both step records kept)

Run (isolated venv with paddle, weights already cached in ~/.paddlex):
  PYTHONPATH=src "G:/CODEX/New Manga.task-envs/M2-TA3-B-ocr/Scripts/python.exe" \
    experiments/M2-OCR-PADDLE3X-1/diagnose_bytes_path.py \
    --image "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg" \
    --out verification/M2-OCR-PADDLE3X-1/diagnosis.json
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def extract_texts(results: any) -> list[str]:  # noqa: ANN401 - raw engine payload
    """Pull rec_texts out of a 3.x predict/ocr return (same as TA3-B smoke)."""
    texts: list[str] = []
    for res in results or []:
        payload = res if isinstance(res, dict) else getattr(res, "json", {})
        body = payload.get("res", payload) if isinstance(payload, dict) else {}
        if isinstance(body, dict):
            texts.extend(str(t) for t in (body.get("rec_texts", []) or []))
    return texts


def texts_match(a: list[str], b: list[str]) -> bool:
    return [str(t) for t in a] == [str(t) for t in b]


def run_ndarray(engine: any, image: any) -> tuple[list[str], list]:  # noqa: ANN401
    """One ndarray inference; return (rec_texts, rec_polys|rec_boxes raw)."""
    results = engine.predict(image)
    texts: list[str] = []
    polys: any = None  # noqa: ANN401
    for res in results:
        payload = res if isinstance(res, dict) else getattr(res, "json", {})
        body = payload.get("res", payload) if isinstance(payload, dict) else {}
        if not isinstance(body, dict):
            continue
        texts.extend(str(t) for t in (body.get("rec_texts", []) or []))
        polys = body.get("rec_polys", None)
        if polys is None:
            polys = body.get("rec_boxes", None)
    return texts, polys


def crop_region(image: any, poly: any):  # noqa: ANN401
    """Crop one box to a region array; boxes may be 4-point polys or xyxy."""
    import numpy as np

    pts = poly.tolist() if hasattr(poly, "tolist") else [list(p) for p in poly]
    if len(pts) == 4 and all(isinstance(v, (int, float)) for v in pts):
        xs, ys = [pts[0], pts[2]], [pts[1], pts[3]]  # xyxy
    else:
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x1, x2 = max(0, int(min(xs))), min(image.shape[1], int(max(xs)) + 1)
    y1, y2 = max(0, int(min(ys))), min(image.shape[0], int(max(ys)) + 1)
    if x2 - x1 < 4 or y2 - y1 < 4:
        raise RuntimeError(f"degenerate crop box: {(x1, y1, x2, y2)}")
    return image[y1:y2, x1:x2], (x1, y1, x2, y2)


def bytes_step(engine: any, name: str, region_bytes: bytes) -> dict:  # noqa: ANN401
    """One production-faithful bytes call; never raises past extraction."""
    record: dict = {"step_region": name, "input": "bytes", "input_len": len(region_bytes)}
    try:
        raw = engine.ocr(region_bytes)
        record["raw_type"] = type(raw).__name__
        record["raw_len"] = len(raw) if isinstance(raw, (list, tuple)) else None
        extracted = extract_texts(raw)
        record["extracted_texts"] = extracted[:10]
        record["n_texts"] = len(extracted)
        record["empty"] = not extracted
    except Exception as exc:  # noqa: BLE001 — honest probe record
        record["empty"] = None
        record["error"] = f"{type(exc).__name__}: {exc}"[:300]
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--image", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    started = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    record: dict = {
        "probe": "M2-OCR-PADDLE3X-1-diagnose-bytes-path",
        "image": args.image,
        "started_at_utc": started,
    }
    try:
        import cv2
        import numpy as np
        import paddleocr
        import paddle

        record["versions"] = {
            "paddleocr": paddleocr.__version__,
            "paddlepaddle": paddle.__version__,
            "numpy": np.__version__,
            "opencv": cv2.__version__,
        }
        from paddleocr import PaddleOCR

        # ---- step 0: decode page (Windows CJK-safe: np.fromfile+imdecode) ----
        data = np.fromfile(args.image, dtype=np.uint8)
        page = cv2.imdecode(data, cv2.IMREAD_COLOR)
        if page is None:
            raise RuntimeError(f"cannot decode page: {args.image}")

        # ---- engine_ref: ndarray ground truth (mkldnn off: 3.3.1 PIR bug) ----
        engine_ref = PaddleOCR(
            lang="korean",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
        )
        record["engine_ref_construction"] = (
            "PaddleOCR(lang='korean', use_doc_orientation_classify=False, "
            "use_doc_unwarping=False, use_textline_orientation=False, enable_mkldnn=False)"
        )
        page_texts, polys = run_ndarray(engine_ref, page)
        if polys is None or not len(polys) or not page_texts:
            raise RuntimeError(f"reference run found no text: keys/len={len(page_texts)}")
        if len(page_texts) != len(polys):
            raise RuntimeError("texts/polys length mismatch in reference run")

        # pick TWO regions with DIFFERENT text (first index pair that differs)
        ia, ib = 0, -1
        for j in range(1, len(page_texts)):
            if page_texts[j] != page_texts[ia]:
                ib = j
                break
        if ib < 0:
            raise RuntimeError("page has no two text lines that differ; probe needs 2 regions")

        regions: dict[str, dict] = {}
        region_arrays: dict[str, tuple] = {}
        for name, idx in (("A", ia), ("B", ib)):
            arr, xyxy = crop_region(page, polys[idx])
            gt_texts, _ = run_ndarray(engine_ref, arr)  # crop-level ground truth
            regions[name] = {
                "page_line_index": idx,
                "box_xyxy": list(xyxy),
                "page_line_text": page_texts[idx],
                "gt_texts_ndarray_crop": gt_texts[:10],
            }
            ok, enc = cv2.imencode(".png", arr)
            if not ok:
                raise RuntimeError(f"cannot encode region {name}")
            region_arrays[name] = (enc.tobytes(), gt_texts)
        record["regions"] = regions

        # ---- engine_prod: EXACT production default construction ----
        engine_prod = PaddleOCR(lang="korean")
        record["engine_prod_construction"] = (
            "PaddleOCR(lang='korean')  # pre-fix production default; post-fix default adds enable_mkldnn=False (no effect on the bytes type rejection, which happens at input validation)"
        )

        # ---- the actual diagnosis: two DIFFERENT regions, back-to-back bytes ----
        steps: list[dict] = []
        a_bytes = region_arrays["A"][0]
        b_bytes = region_arrays["B"][0]
        steps.append(bytes_step(engine_prod, "A", a_bytes))
        steps.append(bytes_step(engine_prod, "B", b_bytes))
        record["bytes_path_steps"] = steps

        t1, t2 = steps[0], steps[1]
        gt_a, gt_b = region_arrays["A"][1], region_arrays["B"][1]
        t2_empty = t2.get("empty")
        t2_texts = t2.get("extracted_texts", [])
        if t2_empty is None or t1.get("empty") is None:
            verdict = "FAIL"
        elif not t2_empty and not texts_match(t2_texts, gt_b):
            # second region produced text that is NOT its own -> misattribution
            verdict = "STALE_REUSE"
        elif not t2_empty:
            verdict = "BYTES_OK"
        elif t1.get("empty"):
            verdict = "ALWAYS_EMPTY"
        else:
            verdict = "MIXED"

        record["verdict"] = verdict
        record["t2_matches_gt_a"] = texts_match(t2_texts, gt_a) if t2_texts else None
        record["wrong_text_risk"] = verdict == "STALE_REUSE"
        record["notes"] = {
            "ALWAYS_EMPTY": "bytes input silently ignored; empty OCR without exception",
            "STALE_REUSE": (
                "bytes input ignored while a PREVIOUS result is re-emitted: silent "
                "wrong-text surface — any historical bytes-path OCR output could have "
                "carried another region's text; flagged prominently per task AC1"
            ),
            "BYTES_OK": "contradicts M2-TA3-B phase-1 EMPTY_RESULT observation; re-check",
            "MIXED": "first/second bytes calls disagree; inspect steps",
        }.get(verdict, "probe error — see step records")
    except Exception as exc:  # noqa: BLE001 — honest probe record
        record["verdict"] = "FAIL"
        record["error"] = f"{type(exc).__name__}: {exc}"[:300]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"probe_verdict={record['verdict']} out={out}")
    if record["verdict"] == "STALE_REUSE":
        print(
            "WARNING: STALE_REUSE — bytes path re-emits a PREVIOUS region's text "
            "(silent wrong-text risk; must be flagged in the fix task report)"
        )
    return 0 if record["verdict"] != "FAIL" else 3


if __name__ == "__main__":
    raise SystemExit(main())
