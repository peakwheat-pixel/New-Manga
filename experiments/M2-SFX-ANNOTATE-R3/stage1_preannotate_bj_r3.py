"""M2-SFX-ANNOTATE-R3 阶段一（targeted）：BJ 新页 BJ26-37 预标注 + 审核工作表
+ 判定单元合并（bj_new + bj_lowconf_leftover）+ 双审批次切分（≤20/批）。

R2 同款工具（experiments/M2-SFX-ANNOTATE-R2/stage1_preannotate_bj_new.py）
的 targeted 变体：只处理 R3 AC1 新入池的 12 个 BJ 页（BJ26-BJ37），不触碰
R1/R2 已有页。步骤（--step）：

  scan      chiqui7 SFX 密度扫描：BJ26-37 整页 letterbox（R1/R2 BJ 域同口径）。
            需 onnxruntime venv（M2-SFX-FINETUNE-gpu-py312）。
  assemble  页级候选 → preannotate manifest（T1a schema，全标 pseudo）+
            selection 登记页固定 = AC1 落位 BJ26-37（cases.json 已登记，
            本工具不重新选取）。
  worksheet 每候选框裁切预览（20% 边距上下文，R2 同款）+ 页级清单（JSON +
            md，AI 预判列预填、判定列留空）。
  units     判定单元合并 + 批次切分（≤20/批）：
            ① part="bj_new"：BJ26-37 全部检出候选——R3 合同明确不设 conf
              门槛（R2 教训=BJ 候选 conf 天然低，R2 conf<0.2 的 16 单元因
              门槛被遗留）；
            ② part="bj_lowconf_leftover"：R2 worksheet-bj-new.json conf<0.2
              遗留 16 单元（BJ16×4/BJ17×2/BJ18×1/BJ19×3/BJ20×2/BJ21×2/
              BJ22×2，R2 无判定），unit_id 沿 R2 原值，preview/page 引 R2
              worktree 绝对路径（跨 worktree 引用，不复制）；
            → judgments/units.json + judgments/batch-list/batch-N.json
            （每批 ≤20 单元，内嵌判定标准说明沿 R2 JUDGE_STD 口径）。

与 R2 的差异（targeted 语义，均在产物 JSON 内登记）：
  - 页面选取不重跑：BJ26-37 固定 = AC1 material_select_r3.py 落位 + cases.json
    登记（密度 top-6 无并列 + kept=0 目检毛笔形态决胜 6 页）。
  - cases.json 已含 BJ26-37（R3 AC1 纯追加 commit 579af8a5）：case 元数据
    与登记条目对齐（source/source_id/local_path/pixel_size 同源）。
  - 候选单源（chiqui7-scan）；新页候选全量入审（无 conf 门槛）。

纪律：零 src 修改（生产推理序列经 conf_scan_diag 只读 import 复用）；素材树
只读；R1/R2 数据只读引用；T1a 工具链（schema/splits/hash）只读复用不重造。
产出数据本体落 training_data/sfx-v1/annotate-r3/（gitignored），Git 只进脚本
与摘要。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA"))

from PIL import Image  # noqa: E402

# 受控本地素材（webtoon 长条最大 ~90.6MP）仅略超 PIL 默认警戒线；显式解除并留痕。
Image.MAX_IMAGE_PIXELS = None

from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord  # noqa: E402
from sfx_data_infra.splits import SEED_DEFAULT, derive_group_key_from_case  # noqa: E402
from sfx_data_infra.importers import xyxy_to_polygon  # noqa: E402

R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3"
SCAN_JSON = OUT_DIR / "preannotate" / "scan-bj-new.json"
PREANNOTATE_JSON = OUT_DIR / "preannotate" / "manifest-bj-new.json"
SELECTION_JSON = OUT_DIR / "preannotate" / "selection-bj-new.json"
WORKSHEET_JSON = OUT_DIR / "worksheet" / "worksheet-bj-new.json"
WORKSHEET_MD = OUT_DIR / "worksheet" / "worksheet-bj-new.md"
PREVIEW_DIR = OUT_DIR / "previews"
JUDGMENTS_DIR = OUT_DIR / "judgments"
UNITS_JSON = JUDGMENTS_DIR / "units.json"
BATCH_LIST_DIR = JUDGMENTS_DIR / "batch-list"
PREP_SUMMARY_JSON = REPO_ROOT / "experiments" / "M2-SFX-ANNOTATE-R3" / "prep-summary.json"

R2_WORKSHEET_JSON = (
    R2_WORKTREE / "training_data" / "sfx-v1" / "annotate-r2" / "worksheet" / "worksheet-bj-new.json"
)
R2_PREVIEWS_DIR = R2_WORKTREE / "training_data" / "sfx-v1" / "annotate-r2" / "previews"

CASES_JSON = REPO_ROOT / "test_assets" / "comic_golden_suite" / "manifests" / "cases.json"
BJ_ASSET_ROOT = REPO_ROOT / "test_assets" / "comic_golden_suite" / "日漫_JA" / "01_black_jack_official"

SEED = SEED_DEFAULT  # 20261004，沿 T1a splits.SEED_DEFAULT（seed 冻结、可复现）
IOU_MERGE = 0.5      # 跨源同框合并阈值（与 R2 同款；本轮单源，防御性保留）
PREVIEW_MAX_EDGE = 640
PREVIEW_MARGIN = 0.20  # 合同：裁切预览含 20% 边距上下文
PREVIEW_MARGIN_MIN_PX = 24
BATCH_MAX_UNITS = 20  # R3 合同：批次 ≤20 单元/批

LOWCONF_LEFTOVER_PART = "bj_lowconf_leftover"
BJ_NEW_PART = "bj_new"
LEFTOVER_CONF_LT = 0.2  # R2 遗留层定义：conf<0.2 无判定（R2 判定收敛门槛遗留）


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_bj_new_pages() -> list[dict]:
    """AC1 落位 → BJ26-37 页表（cases.json 登记条目对齐，不重新选取）。"""
    cases = json.loads(CASES_JSON.read_text(encoding="utf-8"))
    by_id = {c["case_id"]: c for c in cases["cases"]}
    out = []
    for i in range(26, 38):
        cid = f"BJ{i:02d}"
        case = by_id.get(cid)
        if case is None:
            raise FileNotFoundError(f"cases.json 未登记 {cid}（AC1 material commit 579af8a5 应已追加）")
        sid = case["source_id"]
        path = BJ_ASSET_ROOT / f"vol{int(case['volume']):02d}" / "pages" / f"{sid}.png"
        if not path.is_file():
            raise FileNotFoundError(f"{cid} 页文件不在盘: {path}")
        out.append({
            "case_id": cid,
            "domain": "bj",
            "path": str(path),
            "source_id": sid,
            "density_material_scan": None,
            "material_selection": "AC1 density top-6 no-tie + kept=0 tie group visual brush-form tiebreak "
                                  "(selection/material-selection-r3.json)",
            "group": derive_group_key_from_case(case),
            "case": case,
        })
    return out


# ---------------------------------------------------------------------------
# scan：chiqui7 密度扫描（onnxruntime venv 运行；R1/R2 同款整页 letterbox）
# ---------------------------------------------------------------------------


def _load_scan_engine():
    """只读 import 复用 conf_scan_diag（其内部复用生产 detection_sfx 序列）。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "conf_scan_diag",
        REPO_ROOT / "experiments" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "conf_scan_diag.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conf_scan_diag"] = mod
    spec.loader.exec_module(mod)
    return mod


def _dedup_boxes(boxes: list[dict], iou_thr: float = 0.5) -> list[dict]:
    """同页 sfx 框去重（贪心 NMS，按 conf 降序；R2 同款）。"""

    def iou(a, b):
        ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = ix * iy
        if inter <= 0.0:
            return 0.0
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        return inter / (area_a + area_b - inter)

    ordered = sorted(boxes, key=lambda b: b["conf"], reverse=True)
    kept: list[dict] = []
    for b in ordered:
        if any(iou(b["xyxy"], k["xyxy"]) >= iou_thr for k in kept):
            continue
        kept.append(b)
    return kept


def cmd_scan() -> int:
    mod = _load_scan_engine()
    run_inference = mod.run_inference
    session, imgsz, imgsz_source, _raw = mod._build_engine(Path(mod.SFX_WEIGHTS_DEFAULT))
    print(f"engine OK imgsz={imgsz} ({imgsz_source})")

    pages = load_bj_new_pages()
    out = {
        "tool": "experiments/M2-SFX-ANNOTATE-R3/stage1_preannotate_bj_r3.py --step scan",
        "generated_at_utc": now_iso(),
        "weights": str(mod.SFX_WEIGHTS_DEFAULT),
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "conf_floor": 0.01,
        "note": "R3 targeted BJ 新页密度扫描：BJ26-37 整页 letterbox（R1/R2 BJ 域同口径）；只保留 sfx 类框详情"
                "（全类计数保留）；本轮新页候选全量入审，不设 conf 门槛（R3 合同）",
        "seed": SEED,
        "pages": {},
    }

    import numpy as np

    t_all = time.perf_counter()
    for info in pages:
        page_path = Path(info["path"])
        with Image.open(page_path) as im:
            rgb = im.convert("RGB")
        page_w, page_h = rgb.size
        t0 = time.perf_counter()
        boxes_raw, _scale, _shape = run_inference(
            session, np.asarray(rgb), imgsz, float(page_w), float(page_h)
        )
        elapsed = round(time.perf_counter() - t0, 1)
        sfx_boxes: list[dict] = []
        count_by_class_total: dict[str, int] = {}
        for b in boxes_raw:
            count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
            if b["cls"] == "sfx":
                sfx_boxes.append({"xyxy": b["xyxy"], "conf": b["conf"], "source": "chiqui7-scan"})
        sfx_kept = _dedup_boxes(sfx_boxes)
        out["pages"][info["case_id"]] = {
            "case_id": info["case_id"],
            "domain": "bj",
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "scan_mode": "fullpage_letterbox",
            "n_tiles": 1,
            "inference_s": elapsed,
            "count_by_class_all": count_by_class_total,
            "sfx_box_count_raw": len(sfx_boxes),
            "sfx_boxes": sfx_kept,
        }
        print(
            f"scan {info['case_id']} ({info['source_id']}): {page_w}x{page_h} "
            f"sfx_raw={len(sfx_boxes)} kept={len(sfx_kept)} {elapsed}s"
        )
        rgb.close()

    SCAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    SCAN_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {SCAN_JSON} ({round(time.perf_counter() - t_all, 1)}s total)")
    return 0


# ---------------------------------------------------------------------------
# assemble：页级候选 → T1a schema（全 pseudo）+ 页选取登记
# ---------------------------------------------------------------------------


def cmd_assemble() -> int:
    pages = load_bj_new_pages()
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8"))
    stamp = now_iso()

    records: list[SampleRecord] = []
    density: dict[str, int] = {}
    for info in pages:
        cid = info["case_id"]
        sd = scan["pages"][cid]
        # scan 框形态 {xyxy,conf,source} → merge 形态 {xyxy,conf,sources}（单源，R2 merge 语义的恒等形态）
        merged = sorted(
            ({"xyxy": b["xyxy"], "conf": b["conf"], "sources": [b["source"]]} for b in sd["sfx_boxes"]),
            key=lambda m: (-(m["conf"]), m["xyxy"]),
        )
        density[cid] = len(merged)
        page_path = Path(info["path"])
        with Image.open(page_path) as im:
            w, h = im.size
        case = info["case"]
        rec = SampleRecord(
            sample_id=f"pre-{cid.lower()}",
            image=ImageRef(path=str(page_path), sha256=sha256_file(page_path), width=w, height=h),
            boxes=[
                BoxAnnotation(
                    polygon=xyxy_to_polygon(*m["xyxy"]),
                    cls="sfx",
                    text=None,
                )
                for m in merged
            ],
            annotation_status="pseudo",
            provenance={
                "type": "asset_case",
                "case_id": cid,
                "source_url": case["source"],
                "source_id": case["source_id"],
                "stage": "annotate-r3-stage1-bj-new",
                "review_domain": "bj",
                "boxes_meta": [
                    {"conf": m["conf"], "sources": m["sources"], "texts": []} for m in merged
                ],
                "quality_note": "AI 预标注草稿（chiqui7-scan 单源，全 pseudo）；R3 双 AI 交叉审核逐条判定",
                "evidence": "scan-bj-new.json；页选取 = AC1 material_select_r3.py（density-scan-pool.json + "
                            "material-selection-r3.json：密度 top-6 无并列 + kept=0 目检毛笔形态决胜）",
                "cases_json_note": "BJ26-37 已由 R3 AC1 登记（cases.json 纯追加 commit 579af8a5，"
                                   "page_sha256/volume/pdf_page_number/pixel_size 见该文件）；本工具 case 元数据与登记条目对齐",
            },
            group=info["group"],
            created_at=stamp,
        )
        records.append(rec)

    selection = {
        "tool": "experiments/M2-SFX-ANNOTATE-R3/stage1_preannotate_bj_r3.py --step assemble",
        "generated_at_utc": stamp,
        "seed": SEED,
        "targeted": True,
        "targeted_note": "R3 targeted：BJ26-37 固定 = AC1 落位 12 页（material-selection-r3.json bj_selected；"
                         "cases.json 已登记），本工具不重新选取",
        "pages": [
            {
                "case_id": info["case_id"],
                "source_id": info["source_id"],
                "material_selection": info["material_selection"],
                "density_this_scan": density[info["case_id"]],
                "page": info["path"],
                "group": info["group"],
            }
            for info in pages
        ],
        "density": density,
    }

    PREANNOTATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    PREANNOTATE_JSON.write_text(
        json.dumps([r.to_dict() for r in records], ensure_ascii=False, indent=1), encoding="utf-8"
    )
    SELECTION_JSON.write_text(json.dumps(selection, ensure_ascii=False, indent=1), encoding="utf-8")
    n_boxes = sum(len(r.boxes) for r in records)
    print(f"page samples: {len(records)} | page boxes: {n_boxes}")
    print(f"wrote {PREANNOTATE_JSON}")
    print(f"wrote {SELECTION_JSON}")
    return 0


# ---------------------------------------------------------------------------
# worksheet：预览裁切 + 页级清单（JSON+md）（R2 同款）
# ---------------------------------------------------------------------------


def _crop_with_margin(im: Image.Image, xyxy: list[float]) -> Image.Image:
    x0, y0, x1, y1 = xyxy
    bw, bh = x1 - x0, y1 - y0
    dx = max(bw * PREVIEW_MARGIN, PREVIEW_MARGIN_MIN_PX)
    dy = max(bh * PREVIEW_MARGIN, PREVIEW_MARGIN_MIN_PX)
    W, H = im.size
    box = (max(0, int(x0 - dx)), max(0, int(y0 - dy)), min(W, int(x1 + dx)), min(H, int(y1 + dy)))
    return im.crop(box)


def _annotate_preview(img: Image.Image, unit_id: str, conf, sources: list[str]) -> Image.Image:
    """预览下采样 + AI 框描边 + unit_id/conf 标注（R2 同款）。"""
    from PIL import ImageDraw

    if max(img.size) > PREVIEW_MAX_EDGE:
        s = PREVIEW_MAX_EDGE / max(img.size)
        img = img.resize((max(1, int(img.width * s)), max(1, int(img.height * s))))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, img.width - 1, img.height - 1], outline=(200, 30, 30), width=2)
    conf_s = f"conf={conf:.2f}" if isinstance(conf, (int, float)) else "conf=ref"
    label = f"{unit_id} {conf_s} [{'/'.join(sources)}]"
    draw.rectangle([0, 0, img.width - 1, 14], fill=(0, 0, 0))
    draw.text((3, 2), label, fill=(255, 255, 255))
    return img


def cmd_worksheet() -> int:
    manifest = json.loads(PREANNOTATE_JSON.read_text(encoding="utf-8"))
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    WORKSHEET_JSON.parent.mkdir(parents=True, exist_ok=True)
    stamp = now_iso()

    units: list[dict] = []
    zero_box_pages: list[dict] = []  # 零 AI 检出的入选页（负证据页，判定轮直接补画）
    page_cache: dict[str, Image.Image] = {}

    def get_image(path_str: str) -> Image.Image:
        if path_str not in page_cache:
            page_cache.clear()
            page_cache[path_str] = Image.open(Path(path_str)).convert("RGB")
        return page_cache[path_str]

    for m in manifest:
        prov = m["provenance"]
        cid = prov["case_id"]
        meta = prov.get("boxes_meta", [{}] * len(m["boxes"]))
        if not m["boxes"]:
            zero_box_pages.append({"case_id": cid, "domain": prov["review_domain"],
                                   "page_file": Path(m["image"]["path"]).name})
            continue
        im = get_image(m["image"]["path"])
        for i, (b, bm) in enumerate(zip(m["boxes"], meta)):
            unit_id = f"R3-{cid}-B{i:02d}"
            xyxy = [b["polygon"][0][0], b["polygon"][0][1], b["polygon"][2][0], b["polygon"][2][1]]
            preview_name = f"{unit_id}__{cid}.png"
            pv = _annotate_preview(_crop_with_margin(im, xyxy), unit_id, bm.get("conf"), bm.get("sources", []))
            pv.save(PREVIEW_DIR / preview_name)
            units.append(
                {
                    "unit_id": unit_id,
                    "part": BJ_NEW_PART,
                    "kind": "page_box",
                    "domain": prov["review_domain"],
                    "case_id": cid,
                    "page_file": Path(m["image"]["path"]).name,
                    "page_path": m["image"]["path"],
                    "box_index": i,
                    "xyxy": [round(v, 1) for v in xyxy],
                    "box_size": [round(xyxy[2] - xyxy[0], 1), round(xyxy[3] - xyxy[1], 1)],
                    "ai_cls": b["cls"],
                    "ai_conf": bm.get("conf"),
                    "sources": bm.get("sources", []),
                    "ai_text": b.get("text"),
                    "preview_file": f"previews/{preview_name}",
                    "verdict": "",
                    "user_rationale": "",
                }
            )
    page_cache.clear()

    lines = [
        "# M2-SFX-ANNOTATE-R3 阶段一（targeted BJ 新页 BJ26-37）· 审核工作表（新页部分）",
        "",
        f"- 生成：{stamp} | seed={SEED}（冻结）",
        "- 裁决枚举（verdict 列）：`confirm`（确认是 SFX，框可接受）/ `correct`（是 SFX 但框需修）/ `delete`（非 SFX）/ `miss`（页级漏标，在页小节末尾补记框坐标）",
        "- 每行附预览裁切图（20% 边距上下文，红框=AI 候选框，顶部条=unit_id/conf/来源）",
        "- **不设 conf 门槛**（R3 合同）：R2 教训=BJ 候选 conf 天然低，本轮全部检出候选入审",
        "- BJ 域主攻形态=毛笔/书法竖排效果音（判定标准沿 R2 JUDGE_STD，双 AI 交叉审核口径见 judgments/batch-list/）",
        "",
    ]
    by_page: dict[str, list[dict]] = {}
    for u in units:
        by_page.setdefault(u["case_id"], []).append(u)
    for cid in sorted(set(by_page) | {z["case_id"] for z in zero_box_pages}):
        us = by_page.get(cid, [])
        if not us:
            lines += [
                f"### {cid}（0 AI 候选框——负证据页：模型在该页无 SFX 检出，chiqui7 对 BJ 域存在已知盲区；"
                f"该页经 AC1 目检确认含毛笔竖排 SFX）",
                "",
                f"→ 请判定轮直接补画漏标 SFX 框（`miss` + 框坐标，页文件：{next(z['page_file'] for z in zero_box_pages if z['case_id'] == cid)}）",
                "",
            ]
            continue
        lines += [f"### {cid}（{len(us)} 候选框；页级漏标补记：`miss` + 框坐标）", "",
                  "| unit_id | conf | 来源 | xyxy | 预览 | 判定 | rationale |", "|---|---|---|---|---|---|---|"]
        for u in us:
            conf_s = f"{u['ai_conf']:.2f}" if isinstance(u["ai_conf"], (int, float)) else "ref"
            lines.append(
                f"| {u['unit_id']} | {conf_s} | {'/'.join(u['sources'])} | {u['xyxy']} | {Path(u['preview_file']).name} |  |  |"
            )
        lines.append("")

    WORKSHEET_JSON.write_text(
        json.dumps({"generated_at_utc": stamp, "seed": SEED, "n_units": len(units),
                    "conf_gate": None,
                    "conf_gate_note": "不设 conf 门槛（R3 合同）：全部检出候选入审",
                    "zero_box_pages": zero_box_pages,
                    "zero_box_pages_note": "零 AI 检出页=负证据页（chiqui7 对 BJ 毛笔竖排盲区；该 6 页经 AC1 目检"
                                           "确认含毛笔竖排 SFX），判定轮经 miss 通道直接补画",
                    "units": units},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    WORKSHEET_MD.write_text("\n".join(lines), encoding="utf-8")

    conf_tiers = {"conf_ge_0.5": 0, "conf_0.2_to_0.5": 0, "conf_lt_0.2": 0, "ref_no_conf": 0}
    for u in units:
        c = u.get("ai_conf")
        if not isinstance(c, (int, float)):
            conf_tiers["ref_no_conf"] += 1
        elif c >= 0.5:
            conf_tiers["conf_ge_0.5"] += 1
        elif c >= 0.2:
            conf_tiers["conf_0.2_to_0.5"] += 1
        else:
            conf_tiers["conf_lt_0.2"] += 1
    print(f"units: {len(units)} | conf tiers: {conf_tiers} | zero_box_pages: {zero_box_pages}")
    print(f"wrote {WORKSHEET_JSON}")
    print(f"wrote {WORKSHEET_MD}")
    return 0


# ---------------------------------------------------------------------------
# units + batches：判定单元合并（bj_new + bj_lowconf_leftover）+ ≤20/批切分
# ---------------------------------------------------------------------------

JUDGE_STD = {
    "basis": "沿 R2 双 AI 交叉审核判定口径（R2 judgments/units.json + codex/agy rationale 留痕 + "
             "R2 合同 AC2 JUDGE_STD：含毛笔竖排主攻形态说明）",
    "verdict_enum": {
        "confirm": "确认是 SFX（效果音文字）且框可接受",
        "correct": "是 SFX 但框需修（在 rationale 写明修正方式）",
        "delete": "非 SFX：对话框台词/旁白/章节标题字/画面物体/空白等",
        "miss": "页级漏标（补记框坐标）",
    },
    "bj_focus": "BJ 域主攻形态=毛笔/书法竖排效果音：巨大粗笔画片假名、无对话框，常带尖刺/冲击框或黑底白字形态；"
                "fragmented 小型竖排拟声（「ア！」「ィ！」类尖刺小框）同样确认为 SFX（R2 confirm 判例："
                "「斜向粗毛笔片假名（シャ等）重度艺术字，无气泡，典型效果音」）",
    "negative_examples": "对话框台词（R3 复核判例：vol03_p0209「ダウン症だ」、vol05_p0192「ギャンブルの……」）、"
                         "旁白框（vol05_p0218）、章节标题字（vol03_p0198「21（ニジュウイチ）/ダウン症」——标题字非拟声，"
                         "防污染 SFX 域）、画面物体、空白 → delete",
    "human_review": False,
    "human_review_note": "human_review=false 保真：AI 代审裁决链沿 R1/R2 登记口径，判定链留痕",
}


def review_tier(conf) -> str:
    if not isinstance(conf, (int, float)):
        return "ref_no_conf"
    if conf >= 0.5:
        return "conf_ge_0.5"
    if conf >= 0.2:
        return "conf_0.2_to_0.5"
    return "conf_lt_0.2"


def cmd_units() -> int:
    ws = json.loads(WORKSHEET_JSON.read_text(encoding="utf-8"))
    stamp = now_iso()

    # ① bj_new：新页全部检出候选（无 conf 门槛）
    bj_new_units = []
    for u in ws["units"]:
        bj_new_units.append({
            "id": u["unit_id"],
            "part": BJ_NEW_PART,
            "domain": u["domain"],
            "case_id": u["case_id"],
            "conf": u["ai_conf"],
            "review_tier": review_tier(u["ai_conf"]),
            "xyxy": u["xyxy"],
            "source": (u["sources"] or ["chiqui7-scan"])[0],
            "ai_pred": None,
            "preview": str(REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3" / u["preview_file"]),
        })

    # ② bj_lowconf_leftover：R2 worksheet conf<0.2 遗留单元（R2 无判定层）
    r2_ws = json.loads(R2_WORKSHEET_JSON.read_text(encoding="utf-8"))
    leftover = [u for u in r2_ws["units"]
                if isinstance(u.get("ai_conf"), (int, float)) and u["ai_conf"] < LEFTOVER_CONF_LT]
    leftover.sort(key=lambda u: u["unit_id"])
    bj_leftover_units = []
    for u in leftover:
        preview_abs = R2_PREVIEWS_DIR / Path(u["preview_file"]).name
        if not preview_abs.is_file():
            raise FileNotFoundError(f"R2 遗留单元预览不在盘: {preview_abs}")
        bj_leftover_units.append({
            "id": u["unit_id"],  # 沿 R2 原值（R2-BJ16-B03 等），保持跨轮引用稳定
            "part": LOWCONF_LEFTOVER_PART,
            "domain": u["domain"],
            "case_id": u["case_id"],
            "conf": u["ai_conf"],
            "review_tier": review_tier(u["ai_conf"]),
            "xyxy": u["xyxy"],
            "source": (u["sources"] or ["chiqui7-scan"])[0],
            "ai_pred": None,
            "preview": str(preview_abs).replace("\\", "/"),
            "page_path": u["page_path"].replace("\\", "/"),
            "origin": "M2-SFX-ANNOTATE-R2 worksheet-bj-new.json conf<0.2 无判定层（R2 判定门槛遗留，R3 扩审）",
        })

    all_units = bj_new_units + bj_leftover_units
    from collections import Counter
    by_part = dict(Counter(x["part"] for x in all_units))
    by_tier = dict(Counter(x["review_tier"] for x in all_units))

    units_doc = {
        "purpose": "M2-SFX-ANNOTATE-R3 扩审单元全量清单（①bj_new：BJ26-37 新页全部检出候选，无 conf 门槛；"
                   "②bj_lowconf_leftover：R2 worksheet conf<0.2 遗留 16 单元）；只提取分批，不判定",
        "generated_at_utc": stamp,
        "tool": "experiments/M2-SFX-ANNOTATE-R3/stage1_preannotate_bj_r3.py --step units",
        "inputs": {
            "r3_worksheet_bj_new": str(WORKSHEET_JSON),
            "r3_preannotate_bj_new": str(PREANNOTATE_JSON),
            "r2_worksheet_bj_new": str(R2_WORKSHEET_JSON),
            "cases_json": str(CASES_JSON),
        },
        "counts": {"total": len(all_units), "byPart": by_part, "byReviewTier": by_tier},
        "notes": {
            "bj_new": "BJ26-37 = AC1 落位 12 页（cases.json 已登记）；候选单源 chiqui7-scan（整页 letterbox）；"
                      "R3 合同明确不设 conf 门槛——全部检出候选入审（R2 教训=BJ 候选 conf 天然低）",
            "bj_lowconf_leftover": f"R2 worksheet-bj-new.json conf<{LEFTOVER_CONF_LT} 无判定层 "
                                   f"（BJ16×4/BJ17×2/BJ18×1/BJ19×3/BJ20×2/BJ21×2/BJ22×2=16）；"
                                   "unit_id 沿 R2 原值；preview/page 引 R2 worktree 绝对路径（跨 worktree 引用，不复制）",
            "ai_pred": "AI 预判文字（本轮单元均无文字预判=null）",
            "preview": "绝对路径；bj_new 在本仓库 annotate-r3/previews/，bj_lowconf_leftover 在 R2 worktree（跨 worktree 引用原路径，不复制）",
            "leftover_conf_lt": LEFTOVER_CONF_LT,
        },
        "units": all_units,
    }
    JUDGMENTS_DIR.mkdir(parents=True, exist_ok=True)
    UNITS_JSON.write_text(json.dumps(units_doc, ensure_ascii=False, indent=1), encoding="utf-8")

    # 批次切分：≤20/批，按 part 分组（bj_new 在前；组内保持页序/unit_id 序）——
    # 每批判定上下文与预览位置统一（bj_new 预览在本仓库、leftover 预览在 R2 worktree）
    groups = [bj_new_units, bj_leftover_units]
    batches: list[list[dict]] = []
    for g in groups:
        batches.extend(g[i:i + BATCH_MAX_UNITS] for i in range(0, len(g), BATCH_MAX_UNITS))
    batches = [b for b in batches if b]
    BATCH_LIST_DIR.mkdir(parents=True, exist_ok=True)
    batch_files = []
    for bi, batch in enumerate(batches, start=1):
        batch_doc = {
            "purpose": f"M2-SFX-ANNOTATE-R3 双 AI 交叉审核批次 {bi}/{len(batches)}"
                       f"（bj_new {sum(1 for x in batch if x['part'] == BJ_NEW_PART)}"
                       f" + bj_lowconf_leftover {sum(1 for x in batch if x['part'] == LOWCONF_LEFTOVER_PART)}"
                       f" = {len(batch)} 单元；≤{BATCH_MAX_UNITS}/批）",
            "judge_std": JUDGE_STD,
            "worksheet_refs": {
                BJ_NEW_PART: str(WORKSHEET_JSON),
                LOWCONF_LEFTOVER_PART: str(R2_WORKSHEET_JSON),
            },
            "units": [{k: u[k] for k in ("id", "preview", "conf", "source", "ai_pred", "part")} for u in batch],
        }
        out = BATCH_LIST_DIR / f"batch-{bi}.json"
        out.write_text(json.dumps(batch_doc, ensure_ascii=False, indent=1), encoding="utf-8")
        batch_files.append(str(out))
        print(f"wrote {out} ({len(batch)} units)")

    # prep 摘要（进 git 的审计留痕；数据本体 gitignored）
    summary = {
        "tool": "experiments/M2-SFX-ANNOTATE-R3/stage1_preannotate_bj_r3.py",
        "generated_at_utc": stamp,
        "stage": "annotate-r3-stage1-bj-new (AC2 清单部分：预标注+遗留单元+合并 units+批次切分；判定轮后续执行)",
        "pages": {"bj_new": [info["case_id"] for info in load_bj_new_pages()]},
        "units": {"total": len(all_units), "byPart": by_part, "byReviewTier": by_tier},
        "batches": {"n": len(batches), "max_units_per_batch": BATCH_MAX_UNITS,
                    "sizes": [len(b) for b in batches], "files": [str(Path(f).relative_to(REPO_ROOT)).replace("\\", "/") for f in batch_files]},
        "artifacts_gitignored": {
            "preannotate": ["preannotate/scan-bj-new.json", "preannotate/manifest-bj-new.json", "preannotate/selection-bj-new.json"],
            "worksheet": ["worksheet/worksheet-bj-new.json", "worksheet/worksheet-bj-new.md"],
            "previews": f"previews/*.png（bj_new 裁切预览）",
            "judgments": ["judgments/units.json"] + [str(Path(f).relative_to(REPO_ROOT)).replace("\\", "/") for f in batch_files],
        },
        "judge_std": JUDGE_STD,
        "zero_box_pages": ws.get("zero_box_pages", []),
        "leftover": {"source": str(R2_WORKSHEET_JSON), "conf_lt": LEFTOVER_CONF_LT, "n": len(bj_leftover_units),
                     "by_case": dict(Counter(x["case_id"] for x in bj_leftover_units))},
    }
    PREP_SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {PREP_SUMMARY_JSON}")
    print(f"units: {len(all_units)} byPart={by_part} byTier={by_tier} | batches: {len(batches)} sizes={[len(b) for b in batches]}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True, choices=["scan", "assemble", "worksheet", "units", "all"])
    args = parser.parse_args()
    steps = [args.step] if args.step != "all" else ["scan", "assemble", "worksheet", "units"]
    for s in steps:
        rc = {"scan": cmd_scan, "assemble": cmd_assemble, "worksheet": cmd_worksheet, "units": cmd_units}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
