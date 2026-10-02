"""M2-SFX-E2E-MATERIAL: register the three new pooled pages as cases.

Reads the AC3 run summaries (verification/M2-SFX-E2E-MATERIAL/
new-assets-run/summaries/qual-BJ1{3,4,5}.json) and appends BJ13/BJ14/BJ15
to test_assets/comic_golden_suite/manifests/cases.json — APPEND ONLY
(existing 97 entries are byte-untouched; suite-level header keys are not
modified).  pipeline_status is derived from the ACTUAL run outcome per
stage (honest registration, not aspiration).

File-format discipline: the existing file is CRLF + 2-space indent with a
trailing newline; the rewritten file keeps exactly that shape.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_PATH = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
SUMMARIES = REPO_ROOT / "verification" / "M2-SFX-E2E-MATERIAL" / "new-assets-run" / "summaries"

NEW = [
    {
        "case_id": "BJ13",
        "source_id": "vol03_p0048",
        "pdf_page_number": 48,
        "file": "pages/vol03_p0048.png",
        "sha256": "86eeb6c228b79765939de51959c56e0c5ecce9390a3884515f6e8a8cc04371d9",
        "text_type": "sfx_dominant_unverified",
        "tags": ["fragmented_sfx", "huge_text", "vertical_text", "complex_background"],
        "feature_notes": (
            "第19話 lead page: two huge handwritten vertical phone-ring SFX "
            "(ピ一一ーン！ x2, independent of balloons), chapter title block, no "
            "dialogue balloons. Selected 2026-10-02 (M2-SFX-E2E-MATERIAL AC2) for "
            "SFX-translation end-to-end coverage; tags from agent visual inspection "
            "(directional, single annotator)."
        ),
    },
    {
        "case_id": "BJ14",
        "source_id": "vol03_p0060",
        "pdf_page_number": 60,
        "file": "pages/vol03_p0060.png",
        "sha256": "61dfeb2ff0fb765ffbb3186797c8973f2f2c762b0c4062a2c189777f3a545c27",
        "text_type": "sfx_dominant_unverified",
        "tags": ["fragmented_sfx", "huge_text", "vertical_text", "complex_background"],
        "feature_notes": (
            "第24話 lead page: three vertical brush-style newborn-cry SFX (オギャァ x3, "
            "fragmented placement across the nursery spread), chapter title block, no "
            "dialogue balloons. Selected 2026-10-02 (M2-SFX-E2E-MATERIAL AC2); tags "
            "from agent visual inspection (directional, single annotator)."
        ),
    },
    {
        "case_id": "BJ15",
        "source_id": "vol03_p0159",
        "pdf_page_number": 159,
        "file": "pages/vol03_p0159.png",
        "sha256": "3af0054184bacabf73baa140382ab087e8d668babc04cd74ac57d5a36c45a040",
        "text_type": "mixed_unverified",
        "tags": ["fragmented_sfx", "vertical_text", "low_contrast", "normal_dialogue", "multi_speaker"],
        "feature_notes": (
            "第24話 follow-up: two vertical brush-style newborn-cry SFX (オギャァ x2, "
            "zoom-confirmed) plus normal multi-speaker dialogue — SFX and speech on "
            "the SAME page (gate routing contrast case). Selected 2026-10-02 "
            "(M2-SFX-E2E-MATERIAL AC2); tags from agent visual inspection (directional)."
        ),
    },
]

LICENSE_TEXT = (
    "Author's free-use terms: commercial/non-commercial use permitted, attribution "
    "mandatory (title + 佐藤秀峰), e-mail report to info@densho810.com within 1 month "
    "of public use; no Kindle store distribution"
)
ATTRIBUTION_NOTE = (
    "Mandatory attribution per the author's free-license terms (densho810.com): "
    "title + author exactly as published; free for commercial and non-commercial "
    "use; report to info@densho810.com within 1 month of public use."
)


def pipeline_status_of(summary: dict) -> dict[str, str]:
    """Derive the honest per-stage status from the AC3 run summary."""
    run1_ok = summary.get("run1", {}).get("status") == "completed"
    run2 = summary.get("run2", {})
    run2_ok = run2.get("status") == "completed"
    export_ok = summary.get("export", {}).get("status") == "OK"
    n_translated = sum(
        1 for d in summary.get("translate_details", []) if (d.get("translated_text") or "").strip()
    )
    translated = n_translated > 0 and export_ok
    status = {
        "ocr": "PASS" if (run2_ok and n_translated > 0) or run2_ok else "FAIL",
        "text_detection": "PASS" if summary.get("regions") else "FAIL",
        "region": "PASS" if summary.get("regions") else "FAIL",
        "reading_order": "PASS" if run1_ok else "NOT_RUN",
        "sfx": "PASS" if any(
            r.get("region_type") == "sfx" and (r.get("sfx_policy") == "translate")
            for r in summary.get("regions", [])
        ) else "NOT_RUN",
        "speaker_attribution": "NOT_RUN",
        "translation": "PASS" if translated else ("FAIL" if run2_ok else "NOT_RUN"),
        "inpainting": "PASS" if run2_ok else "NOT_RUN",
        "typesetting": "PASS" if run2_ok else "NOT_RUN",
        "manga_page_render": "PASS" if export_ok else "NOT_RUN",
    }
    return status


def main() -> int:
    raw = CASES_PATH.read_bytes()
    crlf = b"\r\n" in raw
    data = json.loads(raw)
    cases = data["cases"]
    existing_ids = {c["case_id"] for c in cases}
    clash = [c["case_id"] for c in NEW if c["case_id"] in existing_ids]
    if clash:
        print(f"FATAL: case ids already exist (append-only violated): {clash}", file=sys.stderr)
        return 2

    for spec in NEW:
        summary_path = SUMMARIES / f"qual-{spec['case_id']}.json"
        if not summary_path.is_file():
            print(f"FATAL: missing AC3 summary {summary_path}", file=sys.stderr)
            return 2
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        entry = {
            "case_id": spec["case_id"],
            "language": "ja",
            "source": "https://densho810.com/free/",
            "source_id": spec["source_id"],
            "source_type": "official_free_manga_page",
            "layout_type": "paged_manga",
            "reading_direction": "right_to_left",
            "text_type": spec["text_type"],
            "orientation": "vertical",
            "difficulty": "unassessed",
            "tags": spec["tags"],
            "source_category": "01_black_jack_official",
            "local_path": "日漫_JA/01_black_jack_official/vol03/pages",
            "license_class": "commercial_use_permitted_attribution",
            "redistributable": True,
            "expected_pipeline": [
                "ocr", "text_detection", "region", "reading_order", "sfx",
                "speaker_attribution", "translation", "inpainting", "typesetting",
                "manga_page_render",
            ],
            "ground_truth_available": "none",
            "levels": ["regression", "full"],
            "asset_status": "READY",
            "asset_profile": {"kind": "manual_source_page"},
            "source_name": "Black Jack Official Free (Sato Manga Seisakusho)",
            "asset_type": "manual_source_page",
            "source_url": "https://densho810.com/free/",
            "license": LICENSE_TEXT,
            "ground_truth_types": [],
            "pipeline_status": pipeline_status_of(summary),
            "image_available": True,
            "annotation_available": False,
            "attribution": "ブラックジャックによろしく　佐藤秀峰",
            "volume": 3,
            "pdf_page_number": spec["pdf_page_number"],
            "page_file": spec["file"],
            "page_sha256": spec["sha256"],
            "render_dpi": 150,
            "feature_notes": spec["feature_notes"],
            "attribution_note": ATTRIBUTION_NOTE,
            "registration_note": (
                "Pooled by M2-SFX-E2E-MATERIAL (2026-10-02, user ruling 4 full "
                "authority): SFX-rich page selection, license snapshot and checksums "
                "in verification/M2-SFX-E2E-MATERIAL/material-inventory.json; pixels "
                "stay in the gitignored suite directory."
            ),
        }
        cases.append(entry)
        print(f"appended {spec['case_id']}: pipeline_status={entry['pipeline_status']}")

    out = json.dumps(data, ensure_ascii=False, indent=2)
    if crlf:
        out = out.replace("\n", "\r\n")
    out += "\r\n" if crlf else "\n"
    CASES_PATH.write_bytes(out.encode("utf-8"))
    print(f"cases.json now has {len(cases)} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main())
