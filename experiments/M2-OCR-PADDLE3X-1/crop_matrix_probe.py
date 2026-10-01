"""Decisive matrix: which crops predict non-empty via the production engine?

Rows: top-confidence page-level lines (from the production adapter itself).
Columns: (a) raw ndarray crop straight into predict, (b) the exact adapter
path (PNG bytes -> np.frombuffer+imdecode -> predict).
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

from infrastructure.providers.ocr_local import PaddleKoreanOcrProvider
from ports.ocr.ports import (
    OcrRequest,
    SCRIPT_KOREAN,
    TEXT_DIRECTION_HORIZONTAL,
)

IMAGE = (
    "G:/CODEX/New Manga/test_assets/comic_golden_suite/韩漫_KO/"
    "02_public_ground_truth_peppercarrot/ep04/"
    "kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg"
)
PROBE_BOX = (562, 1421, 685, 1486)  # x1,y1,x2,y2 — the probe's exact crop
DIAG_BOX = (54, 0, 169, 58)  # box A + pad8, known-good in the A/B compare


def crop(page, box, pad=0):
    x1, y1, x2, y2 = box
    x1, y1 = max(0, x1 - pad), max(0, y1 - pad)
    x2, y2 = min(page.shape[1], x2 + pad), min(page.shape[0], y2 + pad)
    return page[y1:y2, x1:x2]


def main() -> int:
    data = np.fromfile(IMAGE, dtype=np.uint8)
    page = cv2.imdecode(data, cv2.IMREAD_COLOR)
    provider = PaddleKoreanOcrProvider()  # the production engine, one instance

    page_result = provider.recognize(
        OcrRequest(
            region_id="m",
            page_id="m",
            image_bytes=__import__("pathlib").Path(IMAGE).read_bytes(),
            width=page.shape[1],
            height=page.shape[0],
            script=SCRIPT_KOREAN,
            direction=TEXT_DIRECTION_HORIZONTAL,
        )
    )
    ranked = sorted(
        (line for line in page_result.lines if line.confidence is not None),
        key=lambda line: line.confidence,
        reverse=True,
    )[:4]

    cases = [("diag_box_A_pad8", crop(page, DIAG_BOX))]
    for i, line in enumerate(ranked):
        xs = [p[0] for p in line.polygon]
        ys = [p[1] for p in line.polygon]
        box = (int(min(xs)), int(min(ys)), int(max(xs)) + 1, int(max(ys)) + 1)
        cases.append((f"topconf{i}_c{line.confidence:.2f}_{line.text[:8]}", crop(page, box, pad=8)))
    cases.append(("probe_box_exact", crop(page, PROBE_BOX)))

    engine = provider._engine_or_raise()
    for name, arr in cases:
        ok, enc = cv2.imencode(".png", arr)
        png_bytes = enc.tobytes()
        decoded = cv2.imdecode(np.frombuffer(png_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        direct = engine.predict(arr)
        via_png = engine.predict(decoded)

        def texts(results):
            out = []
            for res in results:
                payload = res if isinstance(res, dict) else getattr(res, "json", {})
                body = payload.get("res", payload) if isinstance(payload, dict) else {}
                if isinstance(body, dict):
                    out.extend(str(t) for t in (body.get("rec_texts", []) or []))
            return out

        t_direct, t_png = texts(direct), texts(via_png)
        print(
            f"{name}: shape={arr.shape} direct_n={len(t_direct)} {t_direct[:3]} | "
            f"png_n={len(t_png)} {t_png[:3]}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
