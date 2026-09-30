"""M2-TA3-A: backfill pipeline_status for the five smoke cases.

Only the five delivered cases are touched, and only the keys this Task
actually exercised. Values come from the recorded smoke results:
every stage of the production chain completed (see
verification/M2-TA3-A/summaries/smoke-report.json). Keys outside the
exercised chain stay NOT_RUN. Provider identity is NOT part of this
field's vocabulary; it is recorded in the verification summaries.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

MANIFEST = Path("test_assets/comic_golden_suite/manifests/cases.json")
SMOKE_CASES = ["BJ02", "BJ06", "K01", "K02", "K11"]

#: Keys this Task exercised end-to-end on every case (run1 + per-region
#: run2 chain, all steps completed in the pipeline tables).
PASSED_KEYS = [
    "text_detection",
    "region",
    "reading_order",
    "ocr",
    "translation",
    "inpainting",
    "typesetting",
    "manga_page_render",
]


def main() -> int:
    raw = MANIFEST.read_text(encoding="utf-8")
    manifest = json.loads(raw)
    touched = 0
    for case in manifest["cases"]:
        if case["case_id"] not in SMOKE_CASES:
            continue
        pipeline = case["pipeline_status"]
        for key in pipeline:
            if key in PASSED_KEYS:
                pipeline[key] = "PASS"
            # everything else (bubble_detection, sfx, speaker_attribution,
            # webtoon_slice_reassemble) stays NOT_RUN — not part of this
            # Task's exercised chain.
        touched += 1
    if touched != len(SMOKE_CASES):
        print(f"FATAL: expected {len(SMOKE_CASES)} cases, touched {touched}", file=sys.stderr)
        return 2
    text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    if text == raw:
        print("FATAL: manifest unchanged — backfill produced no delta", file=sys.stderr)
        return 2
    MANIFEST.write_text(text, encoding="utf-8")
    # sanity: schema must still load (same import pattern as fetch_bj.py)
    sys.path.insert(0, str(MANIFEST.parent.parent / "tools"))
    import assets

    assets.load_manifest()
    print(f"backfilled pipeline_status for {touched} cases; manifest schema OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
