"""M2-SFX-ANNOTATE-R2 AC1：候选密度排序 → KO top-5 落位 + cases.json 登记 BJ16-BJ25。

输入：training_data/sfx-v1/annotate-r2/scan/density-scan-material.json
（material_scan_density.py 产物）。

排序规则（沿 R1 selection 同款，seed 冻结可复现）：
  密度（去重后 sfx 框数）降序 → sha256(f"{SEED}:{source_id}") 升序决胜
  （splits.SEED_DEFAULT=20261004）。

动作：
  1. KO top-5：候选 PNG 复制到正式素材位
     韩漫_KO/02_public_ground_truth_peppercarrot/epXX/<source_id>.png，
     PIL 逐张验证可开（cases.json K11-K25 条目已存在，无需新增登记）。
  2. BJ top-10：页已在正式素材位（material_bj_render.py 直落
     日漫_JA/01_black_jack_official/volXX/pages/），计算 sha256。
  3. cases.json 追加 BJ16-BJ25（BJ13 字段口径同构；只增不改不删既有 100
     条，写后深度校验）。文件格式保持原样：UTF-8 raw、indent 2、CRLF。
  4. 选取证据 JSON 落 training_data/sfx-v1/annotate-r2/selection/。
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_JSON = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "scan" / "density-scan-material.json"
CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
KO_ASSET_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "韩漫_KO" / "02_public_ground_truth_peppercarrot"
KO_CAND_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "ko-candidates"
BJ_ASSET_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
SELECTION_JSON = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2" / "selection" / "material-selection.json"
SEED = 20261004  # splits.SEED_DEFAULT（R1/R2 冻结同款）

N_BJ = 10
N_KO = 5

BJ13_TEXT_TYPE = "sfx_dominant_unverified"
BJ13_TAGS = ["fragmented_sfx", "huge_text", "vertical_text", "complex_background"]
BJ_LICENSE = (
    "Author's free-use terms: commercial/non-commercial use permitted, attribution mandatory "
    "(title + 佐藤秀峰), e-mail report to info@densho810.com within 1 month of public use; "
    "no Kindle store distribution"
)
BJ_ATTRIBUTION_NOTE = (
    "Mandatory attribution per the author's free-license terms (densho810.com): title + author "
    "exactly as published; free for commercial and non-commercial use; report to info@densho810.com "
    "within 1 month of public use."
)
BJ_EXPECTED_PIPELINE = [
    "ocr", "text_detection", "region", "reading_order", "sfx",
    "speaker_attribution", "translation", "inpainting", "typesetting", "manga_page_render",
]


def rank_key(scan: dict, source_id: str):
    density = scan["pages"][source_id]["sfx_density_kept"]
    return (-density, hashlib.sha256(f"{SEED}:{source_id}".encode("utf-8")).hexdigest())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def make_bj_entry(case_id: str, source_id: str, png: Path, density: int, stamp: str) -> dict:
    volume = int(source_id[3:5])
    page_number = int(source_id[7:11])
    with Image.open(png) as im:
        im.verify()  # 可开性验证（结构层）
    with Image.open(png) as im:
        width, height = im.size
    return {
        "case_id": case_id,
        "language": "ja",
        "source": "https://densho810.com/free/",
        "source_id": source_id,
        "source_type": "official_free_manga_page",
        "layout_type": "paged_manga",
        "reading_direction": "right_to_left",
        "text_type": BJ13_TEXT_TYPE,
        "orientation": "vertical",
        "difficulty": "unassessed",
        "tags": list(BJ13_TAGS),
        "source_category": "01_black_jack_official",
        "local_path": f"日漫_JA/01_black_jack_official/vol{volume:02d}/pages",
        "license_class": "commercial_use_permitted_attribution",
        "redistributable": True,
        "expected_pipeline": list(BJ_EXPECTED_PIPELINE),
        "ground_truth_available": "none",
        "levels": ["regression", "full"],
        "asset_status": "READY",
        "asset_profile": {"kind": "manual_source_page"},
        "source_name": "Black Jack Official Free (Sato Manga Seisakusho)",
        "asset_type": "manual_source_page",
        "source_url": "https://densho810.com/free/",
        "license": BJ_LICENSE,
        "ground_truth_types": [],
        "pipeline_status": {k: "NOT_RUN" for k in BJ_EXPECTED_PIPELINE},
        "image_available": True,
        "annotation_available": False,
        "attribution": "ブラックジャックによろしく　佐藤秀峰",
        "volume": volume,
        "pdf_page_number": page_number,
        "page_file": f"pages/{source_id}.png",
        "page_sha256": sha256_file(png),
        "render_dpi": 150,
        "pixel_size": [width, height],
        "feature_notes": (
            f"M2-SFX-ANNOTATE-R2 AC1 material round (registered {stamp}): selected by chiqui7 SFX "
            f"density scan (fullpage letterbox, conf>=0.01, dedup kept={density}) ranking top-{N_BJ} "
            f"of a 54-page uniform-candidate pool across vol01/03/05 (18 sampled pages per volume, "
            f"BJ01-15 pages excluded); vertical brush-lettered SFX form preferred per A' gap. "
            f"Pixel dimensions {width}x{height} @150 DPI."
        ),
        "attribution_note": BJ_ATTRIBUTION_NOTE,
        "registration_note": (
            "Pooled by M2-SFX-ANNOTATE-R2 (2026-10-04, user ruling option a 补齐再训): density-ranked "
            "candidate pool, scan evidence in training_data/sfx-v1/annotate-r2/scan/density-scan-material.json "
            "and selection/material-selection.json; pixels stay in the gitignored suite directory; "
            "report obligation window to info@densho810.com ends 2026-11-02 (per M2-SFX-E2E-MATERIAL context)."
        ),
    }


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8"))

    bj_ids = sorted((k for k, v in scan["pages"].items() if v["mode"] == "bj_fullpage"), key=lambda k: rank_key(scan, k))
    ko_ids = sorted((k for k, v in scan["pages"].items() if v["mode"] == "ko_tile"), key=lambda k: rank_key(scan, k))
    bj_top, ko_top = bj_ids[:N_BJ], ko_ids[:N_KO]
    print("BJ top-10:", bj_top)
    print("KO top-5:", ko_top)

    # --- KO 落位 ---
    ko_placed: dict[str, dict] = {}
    for key in ko_top:
        cand = KO_CAND_DIR / f"{key}.png"
        if not cand.is_file():
            print(f"KO\tFAILED\tmissing candidate {cand}", file=sys.stderr)
            return 1
        case_id, source_id = key.split("_", 1)
        ep = source_id.split("P")[0].lower().removeprefix("e")
        dest = KO_ASSET_ROOT / f"ep{ep}" / f"{source_id}.png"
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copyfile(cand, dest)
        with Image.open(dest) as im:
            im.verify()
        with Image.open(dest) as im:
            size = im.size
        ko_placed[key] = {"case_id": case_id, "source_id": source_id, "dest": str(dest),
                          "sha256": sha256_file(dest), "pixel_size": list(size),
                          "density": scan["pages"][key]["sfx_density_kept"]}
        print(f"KO\tPLACED\t{dest.relative_to(REPO_ROOT)} {size[0]}x{size[1]} PIL-verify OK")

    # --- BJ 汇总 ---
    bj_placed: dict[str, dict] = {}
    for source_id in bj_top:
        png = BJ_ASSET_ROOT / f"{source_id[:5]}" / "pages" / f"{source_id}.png"
        if not png.is_file():
            print(f"BJ\tFAILED\tmissing page {png}", file=sys.stderr)
            return 1
        bj_placed[source_id] = {"density": scan["pages"][source_id]["sfx_density_kept"]}

    # --- cases.json 登记 BJ16-BJ25（只增不改不删 + 写后深度校验）---
    manifest = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    before = json.loads(json.dumps(manifest["cases"], ensure_ascii=False))
    existing_ids = {c["case_id"] for c in manifest["cases"]}
    new_entries = []
    for i, source_id in enumerate(bj_top, start=16):
        case_id = f"BJ{i:02d}"
        if case_id in existing_ids:
            print(f"cases.json\tFAILED\t{case_id} already exists", file=sys.stderr)
            return 1
        png = BJ_ASSET_ROOT / f"{source_id[:5]}" / "pages" / f"{source_id}.png"
        new_entries.append(make_bj_entry(case_id, source_id, png, bj_placed[source_id]["density"], stamp))
    manifest["cases"].extend(new_entries)
    raw = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    CASES_JSON.write_bytes(raw.replace("\n", "\r\n").encode("utf-8"))

    # 校验：合法 JSON + 既有 100 条逐条不变 + 新增 10 条
    reloaded = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    if reloaded["cases"][:100] != before:
        print("cases.json\tFAILED\texisting 100 entries changed", file=sys.stderr)
        return 1
    if len(reloaded["cases"]) != 110 or [c["case_id"] for c in reloaded["cases"][100:]] != [e["case_id"] for e in new_entries]:
        print("cases.json\tFAILED\tunexpected new-entry layout", file=sys.stderr)
        return 1
    print(f"cases.json\tOK\t100 -> {len(reloaded['cases'])} entries; existing 100 byte-identical (deep-compare); "
          f"appended {', '.join(e['case_id'] for e in new_entries)}")

    # --- 选取证据 ---
    SELECTION_JSON.parent.mkdir(parents=True, exist_ok=True)
    SELECTION_JSON.write_text(json.dumps({
        "tool": "experiments/M2-SFX-ANNOTATE-R2/material_finalize.py",
        "generated_at_utc": stamp,
        "seed": SEED,
        "rule": "密度(去重 sfx 框数)降序 → sha256(seed:source_id) 升序决胜（R1 selection 同款）",
        "candidate_pool": {"bj": len(bj_ids), "ko": len(ko_ids)},
        "bj_selected": [{"rank": i + 1, "source_id": s, "density": bj_placed[s]["density"]} for i, s in enumerate(bj_top)],
        "ko_selected": [{"rank": i + 1, **ko_placed[k]} for i, k in enumerate(ko_top)],
        "bj_runner_up_pool": [{"source_id": s, "density": scan["pages"][s]["sfx_density_kept"]} for s in bj_ids[N_BJ:]],
        "ko_runner_up_pool": [{"source_id": s, "density": scan["pages"][s]["sfx_density_kept"]} for s in ko_ids[N_KO:]],
        "cases_json": {"before": 100, "after": len(reloaded["cases"]), "appended": [e["case_id"] for e in new_entries]},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {SELECTION_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
