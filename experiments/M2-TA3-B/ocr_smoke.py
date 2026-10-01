"""M2-TA3-B AC2: OCR install smoke — one real page per engine, EXIT=0 on success.

Phase-1 deliverable only: proves the isolated venv can import each optional
OCR runtime, download its weights on first run, and produce real text output
on one page. No quality claim is made here (quality thresholds are defined in
verification/M2-TA3-B/quality-thresholds.md and measured in phase 2).

Engines:
  manga-ocr   recognition-only (needs_detection=False in the production
              adapter): fed a whole page for smoke, which is NOT the
              production usage (production hands it a Region crop).
  paddleocr   detector+recognizer, lang="korean"; the smoke also probes the
              adapter seam (engine.ocr on raw bytes) vs the 3.x predict API
              and records both honestly — PaddleOCR 3.x changed its API and
              the production adapter (ocr_local.py) predates it.

Weights stay in the isolated venv/HF cache outside Git (AC5: zero weights in
the repository).
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def smoke_manga_ocr(image_path: Path) -> dict:
    t0 = time.perf_counter()
    import manga_ocr  # noqa: F401  (import probe first, mirrors the adapter)

    from manga_ocr import MangaOcr

    engine = MangaOcr()  # first run downloads kha-white/manga-ocr-base
    load_s = round(time.perf_counter() - t0, 1)

    from PIL import Image

    with Image.open(image_path) as im:
        image = im.convert("RGB")
    t1 = time.perf_counter()
    text = engine(image)
    infer_s = round(time.perf_counter() - t1, 2)
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"manga-ocr returned no text: {text!r}")
    return {
        "engine": "manga-ocr",
        "model": "kha-white/manga-ocr-base",
        "status": "OK",
        "weights_load_s": load_s,
        "first_inference_s": infer_s,
        "text_preview": text[:200],
        "text_length": len(text),
    }


def smoke_paddleocr(image_path: Path) -> dict:
    import numpy as np

    t0 = time.perf_counter()
    import paddleocr  # noqa: F401  (import probe first, mirrors the adapter)

    from paddleocr import PaddleOCR

    # enable_mkldnn=False: paddlepaddle 3.3.1 Windows CPU hits a PIR/oneDNN
    # executor bug (ConvertPirAttribute2RuntimeAttribute NotImplementedError)
    # with the default MKLDNN path — recorded honestly in the smoke evidence.
    engine = PaddleOCR(
        lang="korean",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False,
    )  # first run downloads korean PP-OCRv5 mobile det+rec
    load_s = round(time.perf_counter() - t0, 1)

    # Windows-safe decode (CJK path): np.fromfile + cv2.imdecode
    import cv2

    data = np.fromfile(str(image_path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"cannot decode image: {image_path}")

    t1 = time.perf_counter()
    results = engine.predict(img)
    infer_s = round(time.perf_counter() - t1, 2)
    texts: list[str] = []
    scores: list[float] = []
    for res in results:
        payload = res if isinstance(res, dict) else getattr(res, "json", {})
        data_obj = payload.get("res", payload) if isinstance(payload, dict) else {}
        texts.extend(data_obj.get("rec_texts", []) or [])
        scores.extend(data_obj.get("rec_scores", []) or [])
    # adapter seam probe: engine.ocr on raw bytes (production ocr_local.py
    # passes image_bytes straight through) — an exception-free return is NOT
    # proof: PaddleOCR 3.x logs "Not supported input data type ... ignored"
    # and silently reuses the previous input. Verify the semantics by
    # comparing the extracted text against the ndarray run.
    seam_status = "NOT_PROBED"
    seam_error = ""
    try:
        raw_bytes = image_path.read_bytes()
        seam_results = engine.ocr(raw_bytes)
        seam_texts: list[str] = []
        for res in seam_results:
            payload = res if isinstance(res, dict) else getattr(res, "json", {})
            data_obj = payload.get("res", payload) if isinstance(payload, dict) else {}
            seam_texts.extend(data_obj.get("rec_texts", []) or [])
        if not seam_texts:
            seam_status = "EMPTY_RESULT"
        elif [str(t) for t in seam_texts[:len(texts)]] != [str(t) for t in texts[:len(seam_texts)]]:
            seam_status = "MISMATCH_VS_NDARRAY"
        else:
            seam_status = "OK_TEXT_MATCHES_NDARRAY"
    except Exception as exc:  # noqa: BLE001 — honest probe record
        seam_status = "FAIL"
        seam_error = f"{type(exc).__name__}: {exc}"[:200]
    if not texts:
        raise RuntimeError(f"paddleocr returned no text lines (seam={seam_status} {seam_error})")
    return {
        "engine": "paddleocr",
        "model": "korean_PP-OCRv5_mobile_rec (PP-OCRv5 mobile det+rec)",
        "status": "OK",
        "weights_load_s": load_s,
        "first_inference_s": infer_s,
        "text_lines": len(texts),
        "mean_confidence": round(sum(scores) / len(scores), 4) if scores else None,
        "text_preview": " | ".join(str(t) for t in texts[:10])[:200],
        "adapter_seam_ocr_bytes": {"status": seam_status, "error": seam_error},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", required=True, choices=["manga-ocr", "paddleocr"])
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", required=True, help="result JSON path")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_file():
        print(f"FATAL: image missing: {image_path}", file=sys.stderr)
        return 2

    started = utc_now()
    t0 = time.perf_counter()
    try:
        result = smoke_manga_ocr(image_path) if args.engine == "manga-ocr" else smoke_paddleocr(image_path)
        exit_code = 0
    except Exception as exc:  # noqa: BLE001 — smoke records failures honestly
        result = {
            "engine": args.engine,
            "status": "FAIL",
            "error": f"{type(exc).__name__}: {exc}",
        }
        exit_code = 1
    result.update(
        {
            "image": str(image_path),
            "image_sha256": sha256_file(image_path),
            "started_at_utc": started,
            "wall_s": round(time.perf_counter() - t0, 2),
        }
    )
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"result -> {out_path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
