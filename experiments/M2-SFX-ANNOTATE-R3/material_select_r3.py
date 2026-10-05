"""M2-SFX-ANNOTATE-R3 AC1：候选池排序 → top-12 落位 + cases.json 登记 BJ26-BJ37。

输入：training_data/sfx-v1/annotate-r3/scan/density-scan-pool.json
（scan_pool_density_r3.py 产物，44 页候选池）。

排序规则（沿 R1/R2 selection 同款 seed 冻结可复现 + R3 合同新增目检二次决胜）：
  1. 机械序：密度（去重后 sfx 框数）降序 → sha256(f"{SEED}:{source_id}") 升序决胜；
  2. 密度并列组内目检毛笔形态二次决胜（R3 合同：chiqui7 对毛笔竖排弱，kept=0
     组 38 页全并列，AI 目检 contact sheet + 原图复核，毛笔/书法拟声竖排形态
     优先；结论在 VISUAL_* 常量内联登记，逐页证据+复核淘汰记录）。

本轮密度分布（扫描实测）：kept=1 仅 6 页（rank1-6，无并列直接入选）；
kept=0 有 38 页（全并列，目检决胜区）→ 每组各取 6 页 = top-12。

动作：
  1. top-12 页 PNG 从 R2 素材根（只读）复制落本仓库正式素材位
     日漫_JA/01_black_jack_official/volXX/pages/（gitignored，与 R2 落位同构），
     PIL verify + sha256 + pixel_size。
  2. cases.json 追加 BJ26-BJ37（字段沿 BJ16-25 先例 make_bj_entry 同构，含
     pixel_size/page_sha256/feature_notes 选页理由；只增不改不删既有 110 条，
     写后深度校验；格式 UTF-8 raw、indent 2、CRLF 沿 R2）。
  3. 选取证据 JSON 落 training_data/sfx-v1/annotate-r3/selection/
     material-selection-r3.json（机械序全 44 页 + 目检决胜记录 + cases_json
     before/after）。

纪律：零 src；R2 素材根只读；数据本体 gitignored，Git 只进脚本与 cases.json
追加。
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
R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
BJ_ASSET_ROOT_R2 = (
    R2_WORKTREE / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
)
BJ_ASSET_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"
SCAN_JSON = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / "scan" / "density-scan-pool.json"
CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
SELECTION_JSON = (
    REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / "selection" / "material-selection-r3.json"
)
SEED = 20261004  # splits.SEED_DEFAULT（R1/R2/R3 冻结同款）

N_TOP = 12

# ---------------------------------------------------------------------------
# 目检毛笔形态二次决胜（kept=0 并列组 38 页；contact sheet 5 批 + 原图复核，
# 参照 REF=BJ16/17/18/23/24 R2 confirm 毛笔竖排正样本校准形态标准）
# ---------------------------------------------------------------------------

VISUAL_SELECTED = [
    {"rank": 7, "source_id": "vol05_p0026", "tier": "strong",
     "evidence": "彩色扉页：巨大「あぎゃぁぁぁぁ＋ぉぉぉ」婴儿哭声毛笔书法竖排＋尖刺冲击框（全池最强毛笔形态；chiqui7 kept=0 完全盲区的典型例证）"},
    {"rank": 8, "source_id": "vol03_p0117", "tier": "strong",
     "evidence": "中部大分镜左缘「ハィィィ！！」黑底书法粗字（无对话框，毛笔竖排大喊形态）＋左上分镜「ミシッ」细字"},
    {"rank": 9, "source_id": "vol03_p0175", "tier": "medium",
     "evidence": "第3分镜（婴儿趴卧）周围 4×「ア！」竖排细长拟声小框（fragmented 小型，哭声）"},
    {"rank": 10, "source_id": "vol03_p0094", "tier": "medium",
     "evidence": "第1/3分镜（患者面部）周围 5+×「ィ！」尖刺竖排拟声块（fragmented，形态同 REF-BJ17 确认页）"},
    {"rank": 11, "source_id": "vol03_p0140", "tier": "weak",
     "evidence": "右上分镜右缘 2×小型竖排拟声「ハァ」（呼吸/叹息）；全页其余为对话"},
    {"rank": 12, "source_id": "vol05_p0103", "tier": "weak",
     "evidence": "第3分镜（月夜）左侧 2×细长竖排效果字（シクシク 类哭泣拟声）；其余为对话/旁白"},
]
# 原图复核淘汰记录（contact sheet 低分辨率下疑似、复核确认非 SFX）——登记留痕
VISUAL_REJECTED_CHECKED = [
    {"source_id": "vol03_p0209", "sheet_impression": "左上大字块疑 SFX", "recheck": "实为对话框台词「ダウン症だ」，无 SFX"},
    {"source_id": "vol05_p0192", "sheet_impression": "「ギュッ」竖排疑 SFX", "recheck": "实为对话框台词「ギャンブルの……」，无 SFX"},
    {"source_id": "vol05_p0230", "sheet_impression": "第2分镜左缘竖排块疑 SFX", "recheck": "实为对话框台词，无 SFX"},
    {"source_id": "vol05_p0218", "sheet_impression": "黑底竖排拟声（脚步）疑 SFX", "recheck": "实为旁白框文字，无 SFX"},
    {"source_id": "vol01_p0078", "sheet_impression": "教室嘈杂拟声疑 SFX", "recheck": "全部为对话框台词，无 SFX"},
    {"source_id": "vol03_p0140", "note": "弱确认入选（见 VISUAL_SELECTED）"},
    {"source_id": "vol01_p0100", "sheet_impression": "右缘细长竖排疑 SFX", "recheck": "实为对话框，无 SFX"},
    {"source_id": "vol05_p0179", "sheet_impression": "第1分镜左下块疑 SFX", "recheck": "实为对话框台词，无 SFX"},
    {"source_id": "vol03_p0036", "sheet_impression": "左上小竖排疑 SFX", "recheck": "全部为对话框台词，无 SFX"},
    {"source_id": "vol05_p0103", "note": "弱确认入选（见 VISUAL_SELECTED）"},
]
# 无 SFX 页结构性记录（近全白过渡页/扉页/章节标题页——非台词误判）
VISUAL_NO_SFX_STRUCTURAL = [
    {"source_id": "vol03_p0024", "note": "近全白过渡页（地平线细纹理），无文字无 SFX"},
    {"source_id": "vol01_p0110", "note": "近全白过渡页，无 SFX"},
    {"source_id": "vol01_p0165", "note": "近全白过渡页，无 SFX"},
    {"source_id": "vol05_p0090", "note": "近全白过渡页，无 SFX"},
    {"source_id": "vol01_p0187", "note": "近全白过渡页，无 SFX"},
    {"source_id": "vol01_p0143", "note": "近全白过渡页，无 SFX"},
    {"source_id": "vol03_p0070", "note": "彩色扉页（第20话标题），无拟声 SFX"},
    {"source_id": "vol03_p0198", "note": "黑底毛笔大字为章节标题「21（ニジュウイチ）/ダウン症」——标题字非拟声 SFX，不入正集（防止标题字污染 SFX 域）"},
]

BJ_TEXT_TYPE = "sfx_dominant_unverified"
BJ_TAGS = ["fragmented_sfx", "huge_text", "vertical_text", "complex_background"]
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


def rank_key(density: int, source_id: str):
    return (-density, hashlib.sha256(f"{SEED}:{source_id}".encode("utf-8")).hexdigest())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def make_bj_entry(case_id: str, source_id: str, png: Path, density: int,
                  selection_basis: str, stamp: str) -> dict:
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
        "text_type": BJ_TEXT_TYPE,
        "orientation": "vertical",
        "difficulty": "unassessed",
        "tags": list(BJ_TAGS),
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
            f"M2-SFX-ANNOTATE-R3 AC1 material round (registered {stamp}): selected from the 44-page "
            f"unpooled candidate pool (R2 54-page uniform pool minus BJ16-25) by chiqui7 SFX density scan "
            f"(fullpage letterbox, conf>=0.01, dedup kept={density}); "
            f"{selection_basis} Pixel dimensions {width}x{height} @150 DPI."
        ),
        "attribution_note": BJ_ATTRIBUTION_NOTE,
        "registration_note": (
            "Pooled by M2-SFX-ANNOTATE-R3 (2026-10-05, user ruling 按推荐 T3释放): density scan evidence in "
            "training_data/sfx-v1/annotate-r3/scan/density-scan-pool.json and selection evidence in "
            "selection/material-selection-r3.json (kept=0 tie group visually adjudicated for vertical "
            "brush-lettered SFX form per R3 contract, AI inspection with reference pages BJ16/17/18/23/24); "
            "pixels stay in the gitignored suite directory; report obligation window to info@densho810.com "
            "per M2-SFX-E2E-MATERIAL context."
        ),
    }


def main() -> int:
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    pages = scan["pages"]
    if len(pages) != 44:
        raise RuntimeError(f"scan pool size {len(pages)} != 44")

    # --- 机械序：密度降序 → sha256(seed:source_id) 升序 ---
    mech = sorted(pages.values(), key=lambda p: rank_key(p["sfx_density_kept"], p["source_id"]))
    kept1 = [p for p in mech if p["sfx_density_kept"] >= 1]
    kept0 = [p for p in mech if p["sfx_density_kept"] == 0]
    if len(kept1) != 6 or len(kept0) != 38:
        raise RuntimeError(f"密度分布与扫描不符: kept>=1={len(kept1)} kept0={len(kept0)}（预期 6/38）")

    visual_by_sid = {e["source_id"]: e for e in VISUAL_SELECTED}
    if len(visual_by_sid) != 6:
        raise RuntimeError("VISUAL_SELECTED 必须恰 6 页")
    for e in VISUAL_SELECTED:
        if e["source_id"] not in {p["source_id"] for p in kept0}:
            raise RuntimeError(f"目检入选页不在 kept=0 组: {e['source_id']}")

    # --- top-12：kept>=1 组（rank1-6，无并列直接入选）+ kept=0 目检决胜 6 页 ---
    top = [p["source_id"] for p in kept1] + [e["source_id"] for e in sorted(VISUAL_SELECTED, key=lambda x: x["rank"])]
    assert len(top) == N_TOP

    # --- PNG 落位：R2 素材根 → 本仓库正式素材位 ---
    placed: dict[str, dict] = {}
    for sid in top:
        src = BJ_ASSET_ROOT_R2 / sid[:5] / "pages" / f"{sid}.png"
        dest = BJ_ASSET_ROOT / sid[:5] / "pages" / f"{sid}.png"
        if not src.is_file():
            raise FileNotFoundError(f"源页不在盘: {src}")
        if dest.exists():
            raise RuntimeError(f"目标已存在（防重复落位）: {dest}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
        with Image.open(dest) as im:
            im.verify()
        with Image.open(dest) as im:
            size = im.size
        if sha256_file(src) != sha256_file(dest):
            raise RuntimeError(f"复制后 sha256 不一致: {sid}")
        placed[sid] = {"density": pages[sid]["sfx_density_kept"], "pixel_size": list(size),
                       "sha256": sha256_file(dest)}
        print(f"PLACED {sid}: {size[0]}x{size[1]} kept={placed[sid]['density']} PIL-verify OK")

    # --- cases.json 追加 BJ26-BJ37（只增不改不删 + 写后深度校验）---
    manifest = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    before = json.loads(json.dumps(manifest["cases"], ensure_ascii=False))
    if len(before) != 110:
        raise RuntimeError(f"cases.json 现有 {len(before)} 条 != 110")
    existing_ids = {c["case_id"] for c in before}
    new_entries = []
    for i, sid in enumerate(top, start=26):
        case_id = f"BJ{i:02d}"
        if case_id in existing_ids:
            raise RuntimeError(f"{case_id} already exists")
        if sid in visual_by_sid:
            e = visual_by_sid[sid]
            basis = (f"kept=0 density-tie group: visually adjudicated in favor of vertical brush-lettered SFX "
                     f"form (tier={e['tier']}) per R3 contract second-stage tiebreak — {e['evidence']}.")
        else:
            basis = "density kept>=1 group (rank 1-6, no tie): selected by mechanical density ranking."
        dest = BJ_ASSET_ROOT / sid[:5] / "pages" / f"{sid}.png"
        new_entries.append(make_bj_entry(case_id, sid, dest, placed[sid]["density"], basis, stamp))
    manifest["cases"].extend(new_entries)
    raw = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    CASES_JSON.write_bytes(raw.replace("\n", "\r\n").encode("utf-8"))

    # 校验：合法 JSON + 既有 110 条逐条不变 + 新增 12 条
    reloaded = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    if reloaded["cases"][:110] != before:
        raise RuntimeError("existing 110 entries changed")
    if len(reloaded["cases"]) != 122 or [c["case_id"] for c in reloaded["cases"][110:]] != [e["case_id"] for e in new_entries]:
        raise RuntimeError("unexpected new-entry layout")
    print(f"cases.json OK: 110 -> {len(reloaded['cases'])} entries; existing 110 deep-compare identical; "
          f"appended {', '.join(e['case_id'] for e in new_entries)}")

    # --- 选取证据 ---
    SELECTION_JSON.parent.mkdir(parents=True, exist_ok=True)
    SELECTION_JSON.write_text(json.dumps({
        "tool": "experiments/M2-SFX-ANNOTATE-R3/material_select_r3.py",
        "generated_at_utc": stamp,
        "seed": SEED,
        "rule": "密度(去重 sfx 框数)降序 → sha256(seed:source_id) 升序决胜（R1/R2 同款）；密度并列组内 AI 目检"
                "毛笔竖排形态二次决胜（R3 合同新增；contact sheet 分批+原图复核，REF=BJ16/17/18/23/24 校准）",
        "candidate_pool": {"bj": len(pages), "note": "R2 素材根 54 张 − BJ16-25 已入池 10 张；与 R2 material-selection.json bj_runner_up_pool 逐项一致"},
        "density_distribution": {"kept_ge_1": len(kept1), "kept_0": len(kept0),
                                 "note": "本轮密度分布极稀：kept=1 仅 6 页（chiqui7 对 BJ 域盲区，R2 已实证），kept=0 组 38 页全并列进入目检决胜"},
        "bj_selected": [
            {"rank": i + 1, "source_id": sid, "density": placed[sid]["density"],
             "selection_basis": ("density_kept_ge_1_no_tie" if i < 6 else f"visual_tiebreak_tier={visual_by_sid[sid]['tier']}"),
             "visual_evidence": visual_by_sid[sid]["evidence"] if sid in visual_by_sid else None,
             "pixel_size": placed[sid]["pixel_size"], "sha256": placed[sid]["sha256"]}
            for i, sid in enumerate(top)
        ],
        "visual_adjudication": {
            "method": "AI 目检：scan_pool_density_r3.py 排序 → make_contact_sheet.py 分批 sheet（REF 行校准）→ 疑似页原图复核",
            "sheets": "training_data/sfx-v1/annotate-r3/selection/inspect-batch-1..5.png",
            "selected": VISUAL_SELECTED,
            "rejected_checked": VISUAL_REJECTED_CHECKED,
            "structural_no_sfx": VISUAL_NO_SFX_STRUCTURAL,
        },
        "bj_runner_up_pool": [{"source_id": p["source_id"], "density": p["sfx_density_kept"]}
                              for p in mech if p["source_id"] not in top],
        "cases_json": {"before": 110, "after": len(reloaded["cases"]), "appended": [e["case_id"] for e in new_entries]},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {SELECTION_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
