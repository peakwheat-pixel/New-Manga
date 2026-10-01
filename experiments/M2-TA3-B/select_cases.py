"""M2-TA3-B AC3: 20-case feature-matrix selection (deterministic, reproducible).

Reads the golden-suite cases.json, resolves each selected case's real page
file across the two suite locations (TA2B worktree suite for BJ/JA-P&C/K19,
main checkout suite for K01-K10/K11 — same source TA3-A used), verifies
existence + SHA-256 (BJ pages cross-checked against cases.json page_sha256),
and emits experiments/M2-TA3-B/case-selection.json.

Selection policy (frozen in this script; rationale per case in the output):
- ja 10: BJ first (8 of 12 — richest human-inspected tags) + P&C ja 2
  (J46/J47 = the ONLY ja pages with an official partial SVG text layer,
  i.e. the only native-OCR-GT ja cases).
- ko 10: webtoon K01-K10 minus the two untagged (K03/K06) + P&C ko K11/K19.
- Superset: all 5 TA3-A cases (BJ02/BJ06/K01/K02/K11) are included.

No pixels are copied; the manifest references gitignored suite files by
absolute path, exactly like experiments/M2-TA3-A/run_smoke.py.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"

TA2B_SUITE = Path(
    r"G:/CODEX/New Manga.worktrees/M2-TA2B-OPEN-ASSETS-zcode"
    "/test_assets/comic_golden_suite"
)
MAIN_SUITE = Path(r"G:/CODEX/New Manga/test_assets/comic_golden_suite")

TA3A_CASES = ["BJ02", "BJ06", "K01", "K02", "K11"]

# (case_id, absolute page path, selection rationale)
SELECTION: list[tuple[str, Path, str]] = [
    # ---- ja 10 -----------------------------------------------------------
    ("BJ02", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol01/pages/vol01_p0053.png",
     "TA3-A case (superset); vertical_text+normal_dialogue+multi_speaker+complex_background"),
    ("BJ03", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol01/pages/vol01_p0105.png",
     "narration+complex_background; BJ 印刷漫标准竖排对白页"),
    ("BJ04", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol01/pages/vol01_p0209.png",
     "low_contrast+huge_text+horizontal_text; 唯一 BJ 横排 tag 页"),
    ("BJ05", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol03/pages/vol03_p0001.png",
     "rotated_text 唯一覆盖页+huge_text+complex_background"),
    ("BJ06", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol03/pages/vol03_p0056.png",
     "TA3-A case (superset); fragmented_sfx+dense_dialogue+tiny_text — ja 侧 SFX/小字核心 case"),
    ("BJ08", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol03/pages/vol03_p0221.png",
     "low_contrast+huge_text 第二覆盖页"),
    ("BJ10", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol05/pages/vol05_p0061.png",
     "tags 最全 BJ 页（fragmented_sfx/dense_dialogue/narration/multi_speaker/tiny_text/complex_background）"),
    ("BJ11", TA2B_SUITE / "日漫_JA/01_black_jack_official/vol05/pages/vol05_p0122.png",
     "normal_dialogue+dense_dialogue+multi_speaker; 纯对白密度 case"),
    ("J46", TA2B_SUITE / "日漫_JA/02_open_ground_truth_peppercarrot/ep20/ja_Pepper-and-Carrot_by-David-Revoy_E20P06.jpg",
     "ja 唯二官方 partial SVG text layer 页之一（E20P06）= ja native OCR GT；horizontal_text"),
    ("J47", TA2B_SUITE / "日漫_JA/02_open_ground_truth_peppercarrot/ep20/ja_Pepper-and-Carrot_by-David-Revoy_E20P07.jpg",
     "ja 唯二官方 partial SVG text layer 页之二（E20P07）= ja native OCR GT；horizontal_text+tiny_text"),
    # ---- ko 10 -----------------------------------------------------------
    ("K01", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K01_724815_1/base.png",
     "TA3-A case (superset); normal_dialogue; C1 抽检同源 case（检测口径连续性）"),
    ("K02", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K02_651664_112/base.png",
     "TA3-A case (superset); dense_dialogue+tiny_text — ko 侧小字核心 case"),
    ("K04", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K04_670145_145/base.png",
     "narration 覆盖页"),
    ("K05", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K05_131385_302/base.png",
     "complex_background 覆盖页"),
    ("K07", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K07_641253_141/base.png",
     "multi_speaker 覆盖页"),
    ("K08", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K08_701535_160/base.png",
     "rotated_text 覆盖页; C1 抽检中切分粒度案例同源（K08 r3），阶段二可对照"),
    ("K09", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K09_717481_124/base.png",
     "complex_background 第二覆盖页"),
    ("K10", MAIN_SUITE / "韩漫_KO/01_real_webtoon_cleaned_dataset/K10_730656_11/base.png",
     "normal_dialogue 第二覆盖页"),
    ("K11", MAIN_SUITE / "韩漫_KO/02_public_ground_truth_peppercarrot/ep04/kr_Pepper-and-Carrot_by-David-Revoy_E04P02.jpg",
     "TA3-A case (superset); P&C ko = native SVG text layer OCR GT; OCR 冒烟同页"),
    ("K19", TA2B_SUITE / "韩漫_KO/02_public_ground_truth_peppercarrot/ep20/kr_Pepper-and-Carrot_by-David-Revoy_E20P01.jpg",
     "P&C ko ep20 首页 = native SVG text layer OCR GT（ep20 家族首个 case）"),
]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    catalog = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    by_id = {c["case_id"]: c for c in catalog["cases"]}

    entries = []
    failures = []
    for case_id, page_path, reason in SELECTION:
        meta = by_id.get(case_id)
        if meta is None:
            failures.append(f"{case_id}: not in cases.json")
            continue
        if meta.get("asset_status") != "READY":
            failures.append(f"{case_id}: asset_status={meta.get('asset_status')}")
        if not page_path.is_file():
            failures.append(f"{case_id}: page missing: {page_path}")
            continue
        actual_sha = sha256_file(page_path)
        expected_sha = meta.get("page_sha256")
        sha_match = True if expected_sha is None else (actual_sha == expected_sha)
        if not sha_match:
            failures.append(f"{case_id}: sha256 mismatch vs cases.json")
        language = meta["language"]
        family = meta.get("asset_type", "")
        native_gt = (
            "svg_text_layer_official"
            if "peppercarrot" in str(page_path).lower() or case_id in ("J46", "J47", "K11", "K19")
            else "none"
        )
        entries.append(
            {
                "case_id": case_id,
                "language": language,
                "family": family,
                "source_id": meta.get("source_id", ""),
                "page_path": str(page_path),
                "page_sha256": actual_sha,
                "sha256_matches_cases_json": sha_match,
                "tags": meta.get("tags", []),
                "layout_type": meta.get("layout_type", ""),
                "reading_direction": meta.get("reading_direction", ""),
                "native_ocr_gt": native_gt,
                "asset_location": "ta2b_worktree_suite" if TA2B_SUITE in page_path.parents else "main_checkout_suite",
                "license_class": meta.get("license_class", ""),
                "ta3a_superset": case_id in TA3A_CASES,
                "selected_reason": reason,
            }
        )

    ja = [e for e in entries if e["language"] == "ja"]
    ko = [e for e in entries if e["language"] == "ko"]
    superset_ok = all(
        cid in {x["case_id"] for x in entries} for cid in TA3A_CASES
    )

    tag_matrix: dict[str, int] = {}
    for e in entries:
        for tag in e["tags"]:
            tag_matrix[tag] = tag_matrix.get(tag, 0) + 1

    report = {
        "schema_version": 1,
        "task": "M2-TA3-B",
        "deliverable": "AC3 20-case selection manifest",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_catalog": "test_assets/comic_golden_suite/manifests/cases.json",
        "selection_policy": {
            "ja_10": "BJ 8 (of 12, richest human-inspected tags) + P&C ja 2 (J46/J47, the only official partial SVG text layer ja pages = native OCR GT)",
            "ko_10": "webtoon K01-K10 minus untagged K03/K06 (8) + P&C ko K11/K19 (native SVG text layer)",
            "ta3a_relation": "SUPERSET — all 5 TA3-A cases (BJ02/BJ06/K01/K02/K11) included",
            "excluded_and_why": {
                "BJ01/BJ07/BJ09/BJ12": "BJ 名额 8 个，保留 tags 覆盖最大化的 8 页（BJ01 为封面 credits 页、BJ07 无 tags、BJ09 与 BJ05 tags 重复、BJ12 与 BJ08 tags 重复）",
                "K03/K06": "无 tags（unassessed），名额让给 tagged 页",
                "J38-J45/J48-J52": "P&C ja 名额给仅有的 native GT 页 J46/J47",
                "K12-K18/K20-K25": "P&C ko 名额 2 个（K11 为 TA3-A 超集义务，K19 引入 ep20 家族）；其余页 tags 未标注且与已选页同族",
            },
        },
        "counts": {
            "total": len(entries),
            "ja": len(ja),
            "ko": len(ko),
            "ta3a_superset_included": superset_ok,
            "native_ocr_gt_cases": sum(1 for e in entries if e["native_ocr_gt"] != "none"),
        },
        "tag_coverage": dict(sorted(tag_matrix.items(), key=lambda kv: -kv[1])),
        "cases": entries,
        "verification_failures": failures,
    }

    out_path = Path(__file__).resolve().parent / "case-selection.json"
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["counts"], ensure_ascii=False))
    print("tag_coverage:", json.dumps(report["tag_coverage"], ensure_ascii=False))
    if failures:
        print("FAILURES:", failures, file=sys.stderr)
        return 1
    print(f"ok -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
