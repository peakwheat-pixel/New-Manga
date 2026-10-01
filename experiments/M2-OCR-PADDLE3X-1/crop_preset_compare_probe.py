"""Quick A/B: default FULL-preprocessing vs trimmed engine on one small crop.

Isolates why a 185x88 crop returns zero lines through the production default
construction while the same-size crop succeeded in the AC1 diagnosis engine
(which disables doc-orientation/unwarping/textline-orientation). Prints one
comparison record per construction; no file output (exploratory).
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

from paddleocr import PaddleOCR

IMAGE = (
    "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/"
    "02_public_ground_truth_peppercarrot/ep04/"
    "kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg"
)
# box A from the AC1 diagnosis (99x42 text line '당근아?'), padded by 8px
BOX = (54, 0, 169, 58)


def texts_of(engine, arr):
    results = engine.predict(arr)
    out = []
    for res in results:
        payload = res if isinstance(res, dict) else getattr(res, "json", {})
        body = payload.get("res", payload) if isinstance(payload, dict) else {}
        if isinstance(body, dict):
            out.extend(str(t) for t in (body.get("rec_texts", []) or []))
    return out


def main() -> int:
    data = np.fromfile(IMAGE, dtype=np.uint8)
    page = cv2.imdecode(data, cv2.IMREAD_COLOR)
    x1, y1, x2, y2 = BOX
    crop = page[max(0, y1):y2, max(0, x1):x2]
    ok, enc = cv2.imencode(".png", crop)
    crop_bytes = enc.tobytes()
    decoded = cv2.imdecode(np.frombuffer(crop_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    print(f"crop_shape={crop.shape} bytes={len(crop_bytes)} decode_ok={decoded is not None}")

    constructions = {
        "full_default_plus_mkldnn_off": dict(lang="korean", enable_mkldnn=False),
        "trimmed_plus_mkldnn_off": dict(
            lang="korean",
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            enable_mkldnn=False,
        ),
    }
    for name, kwargs in constructions.items():
        engine = PaddleOCR(**kwargs)
        texts = texts_of(engine, decoded)
        print(f"construction={name} n_texts={len(texts)} texts={texts[:5]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
