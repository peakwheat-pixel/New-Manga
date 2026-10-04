"""M2-SFX-ANNOTATE-R1 阶段一（T1b stage-1）：AC1 预标注合并 + AC2 审核工作表。

三步（--step）：

  scan      chiqui7 SFX 密度扫描：BJ 域 11 个新页整页 letterbox（BJ06/13/14/15
            复用既有 DOMAIN-EXT L1 raw，不重扫）、K 域 10 页原生分辨率 tile
            （webtoon 宽 690 超长条，整页 letterbox 会把宽缩到 172px 丢失细节，
            故 690x1024 无缩放 tile、重叠 128）、J 域 15 个在盘 peppercarrot
            页整页。需 onnxruntime venv（M2-DOCTR-QUAL-C4-gpu-py312）。
  assemble  三源合并去重 → preannotate manifest（T1a schema，全标 pseudo）+ 页面
            选取（密度排序、seed 冻结、承诺缺口如实登记）。dev venv 可跑。
  worksheet 每候选框裁切预览（20% 边距上下文，沿 C1 先例形态）+ 页级清单
            （JSON + 人类可读 md，AI 预判列预填、用户裁决列/user_rationale 列
            留空）+ Git 内摘要。dev venv 可跑。

纪律：零 src 修改（生产推理序列经 conf_scan_diag 只读 import 复用）；素材树
只读；T1a 工具链（schema/importers/splits）只读复用不重造。产出数据本体落
training_data/sfx-v1/annotate-r1/（gitignored），Git 只进清单摘要。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
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
from sfx_data_infra.importers import (  # noqa: E402
    _CASES_JSON,
    import_ogkalu,
    load_cases_index,
    resolve_asset_roots,
    xyxy_to_polygon,
)
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord  # noqa: E402
from sfx_data_infra.splits import SEED_DEFAULT, derive_group_key_from_case  # noqa: E402

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r1"
SCAN_JSON = OUT_DIR / "scan" / "density-scan.json"
PREANNOTATE_JSON = OUT_DIR / "preannotate" / "manifest.json"
SELECTION_JSON = OUT_DIR / "selection" / "selection.json"
WORKSHEET_JSON = OUT_DIR / "worksheet" / "worksheet.json"
WORKSHEET_MD = OUT_DIR / "worksheet" / "worksheet.md"
PREVIEW_DIR = OUT_DIR / "previews"
SUMMARY_JSON = REPO_ROOT / "verification" / "M2-SFX-ANNOTATE-R1" / "stage1-manifest-summary.json"

_L1_JSON = REPO_ROOT / "verification" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "raw" / "l1-fullpage-conf-scan.json"
_L3_JSON = REPO_ROOT / "verification" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "raw" / "l3-reference-crops.json"
_BJ06_JSON = REPO_ROOT / "verification" / "M2-SFX-E2E-MATERIAL" / "bj06-run" / "summaries" / "qual-BJ06.json"

SEED = SEED_DEFAULT  # 20261004，沿 T1a splits.SEED_DEFAULT（seed 冻结、可复现）
IOU_MERGE = 0.5      # 跨源同框合并阈值
PREVIEW_MAX_EDGE = 640
PREVIEW_MARGIN = 0.20  # 合同：裁切预览含 20% 边距上下文
PREVIEW_MARGIN_MIN_PX = 24

# 合同 AC2 承诺量（A′ 采纳条件）：BJ ≥25 页 + KO ≥15 页 + 域内回放 ≥5 页。
COMMIT_BJ_PAGES = 25
COMMIT_KO_PAGES = 15
COMMIT_REPLAY_PAGES = 5

SOURCE_PRIORITY = {"bj06-qual": 0, "l3-ref": 1, "chiqui7-l1": 2, "chiqui7-scan": 3}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def deterministic_rank(key: str, seed: int = SEED) -> str:
    """密度并列时的确定性决胜键（与 T1a 排序切片同款 sha256(seed:key)）。"""
    return hashlib.sha256(f"{seed}:{key}".encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 页解析：BJ 用 T1a 解析器；K/J 磁盘布局与 T1a 假定不同，就地扩展（不改动 T1a）。
# ---------------------------------------------------------------------------


def resolve_pages() -> dict[str, dict]:
    """cases.json 全量 case → {case_id: {path, domain, status}}。

    status: ok / missing。BJ01-15、K01-K10、J38-J52（peppercarrot）在盘；
    K11-K25（cases.json local_path 指向 韩漫_KO/02_public_ground_truth_peppercarrot，
    三个素材根均不存在）与 J01-J37（manga109，磁盘无页）登记 missing。
    """
    idx = load_cases_index()
    roots = resolve_asset_roots()
    out: dict[str, dict] = {}
    for cid in sorted(idx):
        case = idx[cid]
        if cid.startswith("BJ"):
            domain = "bj"
        elif cid.startswith("K"):
            domain = "ko"
        elif cid.startswith("J"):
            domain = "replay-j"
        else:  # O 系等 cases.json 其余 case（O01-08 亦 KO 域 peppercarrot，磁盘全缺）
            domain = "other"
        path: Path | None = None
        if cid.startswith("BJ"):
            for root in roots:
                cand = root / Path(case["local_path"]) / f"{case['source_id']}.png"
                if cand.is_file():
                    path = cand
                    break
        elif cid.startswith("K"):
            for root in roots:
                # cases.json local_path 已含目录段（…/K01_724815_1），页文件 = base.png
                cand = root / Path(case["local_path"]) / "base.png"
                if cand.is_file():
                    path = cand
                    break
        else:  # J 系
            src = str(case["source_id"])
            if src.startswith("E") and "P" in src:  # peppercarrot E04P02 形态
                m_ep = src.split("P")[0].lower().removeprefix("e")
                for root in roots:
                    cand = (
                        root
                        / Path(case["local_path"]).parent
                        / f"ep{m_ep}"
                        / f"ja_Pepper-and-Carrot_by-David-Revoy_{src}.jpg"
                    )
                    if cand.is_file():
                        path = cand
                        break
            # manga109（J01-J37）：磁盘无页，不发明文件名解析，如实 missing
        out[cid] = {
            "path": str(path) if path else None,
            "domain": domain,
            "status": "ok" if path else "missing",
            "local_path": case["local_path"],
            "source_id": case["source_id"],
            "group": derive_group_key_from_case(case),
        }
    return out


# ---------------------------------------------------------------------------
# scan：chiqui7 密度扫描（onnxruntime venv 运行）
# ---------------------------------------------------------------------------

K_TILE_H = 1024
K_TILE_OVERLAP = 128


def _load_scan_engine():
    """只读 import 复用 conf_scan_diag（其内部复用生产 detection_sfx 序列）。"""
    spec = importlib.util.spec_from_file_location(
        "conf_scan_diag",
        REPO_ROOT / "experiments" / "M2-SFX-DETECT-DOMAIN-EXT-DIAG" / "conf_scan_diag.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["conf_scan_diag"] = mod
    spec.loader.exec_module(mod)
    return mod


def _dedup_boxes(boxes: list[dict], iou_thr: float = 0.5) -> list[dict]:
    """跨 tile/来源 sfx 框去重（贪心 NMS，按 conf 降序）。"""

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

    pages = resolve_pages()
    scan_pages = {cid: info for cid, info in pages.items() if info["status"] == "ok"}
    # BJ06/13/14/15 复用既有 l1 raw（合同：用既有 raw），不重扫
    reuse_l1 = {"BJ06", "BJ13", "BJ14", "BJ15"}

    out = {
        "tool": "experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step scan",
        "generated_at_utc": now_iso(),
        "weights": str(mod.SFX_WEIGHTS_DEFAULT),
        "imgsz": imgsz,
        "imgsz_source": imgsz_source,
        "conf_floor": 0.01,
        "note": "SFX 密度扫描：只保留 sfx 类框详情（全类计数保留）；K 域=690x1024 无缩放 tile 重叠 128（原生分辨率保真），BJ/J 域=整页 letterbox（与 l1 同形态）；BJ06/13/14/15 复用 DOMAIN-EXT L1 raw 不重扫",
        "seed": SEED,
        "pages": {},
    }

    t_all = time.perf_counter()
    for cid in sorted(scan_pages):
        info = scan_pages[cid]
        if cid in reuse_l1:
            out["pages"][cid] = {
                "case_id": cid,
                "domain": info["domain"],
                "page": None,
                "scan_mode": "reused_l1_raw",
                "note": "复用 verification/M2-SFX-DETECT-DOMAIN-EXT-DIAG/raw/l1-fullpage-conf-scan.json，assemble 时读取",
            }
            print(f"scan {cid}: reused L1 raw")
            continue
        page_path = Path(info["path"])
        with Image.open(page_path) as im:
            rgb = im.convert("RGB")
        page_w, page_h = rgb.size
        sfx_boxes: list[dict] = []
        count_by_class_total: dict[str, int] = {}
        n_tiles = 0
        t0 = time.perf_counter()
        if info["domain"] == "ko":
            tile_w = page_w
            ys = list(range(0, max(page_h - K_TILE_H, 0) + 1, K_TILE_H - K_TILE_OVERLAP))
            if not ys:
                ys = [0]
            if ys[-1] + K_TILE_H < page_h:
                ys.append(page_h - K_TILE_H)
            for y0 in ys:
                y1 = min(y0 + K_TILE_H, page_h)
                tile = rgb.crop((0, y0, tile_w, y1))
                boxes, _scale, _shape = run_inference(
                    session, __import__("numpy").asarray(tile), imgsz, float(tile_w), float(y1 - y0)
                )
                n_tiles += 1
                for b in boxes:
                    count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
                    if b["cls"] == "sfx":
                        sfx_boxes.append(
                            {
                                "xyxy": [round(b["xyxy"][0], 1), round(b["xyxy"][1] + y0, 1),
                                         round(b["xyxy"][2], 1), round(b["xyxy"][3] + y0, 1)],
                                "conf": b["conf"],
                                "source": "chiqui7-scan",
                            }
                        )
        else:  # bj / replay-j 整页 letterbox
            boxes, _scale, _shape = run_inference(
                session, __import__("numpy").asarray(rgb), imgsz, float(page_w), float(page_h)
            )
            n_tiles = 1
            for b in boxes:
                count_by_class_total[b["cls"]] = count_by_class_total.get(b["cls"], 0) + 1
                if b["cls"] == "sfx":
                    sfx_boxes.append({"xyxy": b["xyxy"], "conf": b["conf"], "source": "chiqui7-scan"})

        sfx_kept = _dedup_boxes(sfx_boxes)
        elapsed = round(time.perf_counter() - t0, 1)
        out["pages"][cid] = {
            "case_id": cid,
            "domain": info["domain"],
            "page": str(page_path),
            "page_size": [page_w, page_h],
            "scan_mode": "tile_690x1024_overlap128" if info["domain"] == "ko" else "fullpage_letterbox",
            "n_tiles": n_tiles,
            "inference_s": elapsed,
            "count_by_class_all": count_by_class_total,
            "sfx_box_count_raw": len(sfx_boxes),
            "sfx_boxes": sfx_kept,
        }
        print(f"scan {cid}: {page_w}x{page_h} tiles={n_tiles} sfx_raw={len(sfx_boxes)} kept={len(sfx_kept)} {elapsed}s")
        rgb.close()

    SCAN_JSON.parent.mkdir(parents=True, exist_ok=True)
    SCAN_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"wrote {SCAN_JSON} ({round(time.perf_counter() - t_all, 1)}s total)")
    return 0


# ---------------------------------------------------------------------------
# assemble：三源合并去重 → T1a schema（全 pseudo）+ 页面选取（seed 冻结）
# ---------------------------------------------------------------------------


def _merge_page_boxes(cands: list[dict]) -> list[dict]:
    """页级候选去重合并：优先级高者坐标保留，conf 取 max，sources 合并。"""
    ordered = sorted(cands, key=lambda c: (SOURCE_PRIORITY.get(c["source"], 9), -(c["conf"] or 0.0)))
    merged: list[dict] = []

    def iou(a, b):
        ix = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
        iy = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = ix * iy
        if inter <= 0.0:
            return 0.0
        area_a = (a[2] - a[0]) * (a[3] - a[1])
        area_b = (b[2] - b[0]) * (b[3] - b[1])
        return inter / (area_a + area_b - inter)

    for c in ordered:
        hit = next((m for m in merged if iou(m["xyxy"], c["xyxy"]) >= IOU_MERGE), None)
        if hit is None:
            merged.append(
                {
                    "xyxy": [float(v) for v in c["xyxy"]],
                    "conf": c["conf"],
                    "sources": [c["source"]],
                    "texts": [c["text"]] if c.get("text") else [],
                }
            )
        else:
            hit["conf"] = max(hit["conf"], c["conf"])
            if c["source"] not in hit["sources"]:
                hit["sources"].append(c["source"])
            if c.get("text") and c["text"] not in hit["texts"]:
                hit["texts"].append(c["text"])
    merged.sort(key=lambda m: (-(m["conf"] or 0.0), m["xyxy"]))
    return merged


def cmd_assemble() -> int:
    pages = resolve_pages()
    scan = json.loads(SCAN_JSON.read_text(encoding="utf-8")) if SCAN_JSON.is_file() else {"pages": {}}
    l1 = json.loads(_L1_JSON.read_text(encoding="utf-8"))
    l3 = json.loads(_L3_JSON.read_text(encoding="utf-8"))
    bj06 = json.loads(_BJ06_JSON.read_text(encoding="utf-8"))
    cases_index = load_cases_index()
    roots = resolve_asset_roots()
    stamp = now_iso()

    # --- 页级候选（源① chiqui7 l1 + 源①扩展 chiqui7-scan + ③ bj06-qual/l3-ref）---
    page_cands: dict[str, list[dict]] = {}
    for cid, pd in l1["pages"].items():
        for b in pd["by_rung"]["0.01"]["boxes"]:
            if b["cls"] == "sfx":
                page_cands.setdefault(cid, []).append(
                    {"xyxy": b["xyxy"], "conf": b["conf"], "source": "chiqui7-l1"}
                )
    for cid, sd in scan["pages"].items():
        for b in sd.get("sfx_boxes", []):
            page_cands.setdefault(cid, []).append(
                {"xyxy": b["xyxy"], "conf": b["conf"], "source": "chiqui7-scan"}
            )
    for r in bj06["regions"]:
        if r.get("region_type") == "sfx":
            bb = r["bbox"]
            page_cands.setdefault("BJ06", []).append(
                {
                    "xyxy": [bb["x"], bb["y"], bb["x"] + bb["width"], bb["y"] + bb["height"]],
                    "conf": 1.0,  # 自证框（生产检出+人工核验），合并排序置顶
                    "source": "bj06-qual",
                }
            )
    for cid, entries in l3["crops"].items():
        for e in entries:
            page_cands.setdefault(cid, []).append(
                {"xyxy": e["ref"]["approx_xyxy"], "conf": None, "source": "l3-ref", "text": e["ref"]["text"]}
            )

    # --- 密度表（全部在盘页）→ 页面选取 → 页级样本（仅入选页；零检出页=pseudo 空框负证据样本）---
    density: dict[str, int] = {}
    merged_by_page: dict[str, list[dict]] = {}
    for cid in sorted({c for c in pages if pages[c]["status"] == "ok"} | set(page_cands)):
        info = pages.get(cid)
        if not info or info["status"] != "ok":
            continue
        merged = _merge_page_boxes(page_cands.get(cid, []))
        density[cid] = len(merged)
        merged_by_page[cid] = merged

    # --- 页面选取（密度排序取 top，seed 冻结；池 < 承诺时全选并登记缺口）---
    all_ok = {cid: info for cid, info in pages.items() if info["status"] == "ok"}
    bj_pool = sorted(c for c in all_ok if c.startswith("BJ"))
    ko_pool = sorted(c for c in all_ok if c.startswith("K"))
    j_pool = sorted(c for c in all_ok if c.startswith("J"))

    def sel_key(cid: str):
        return (-density.get(cid, 0), deterministic_rank(cid))

    bj_selected = sorted(bj_pool, key=sel_key)
    ko_selected = sorted(ko_pool, key=sel_key)
    # 回放域：BJ06 固定 + J 系按密度 top 补足 ≥5（J 候选池即 15 个在盘 peppercarrot 页）
    replay_selected = ["BJ06"] + sorted(j_pool, key=sel_key)[: max(COMMIT_REPLAY_PAGES - 1, 0)]
    replay_selected = sorted(set(replay_selected))
    selected_pages = set(bj_selected) | set(ko_selected) | set(replay_selected)

    page_records: list[SampleRecord] = []
    for cid in sorted(selected_pages):
        info = pages[cid]
        merged = merged_by_page.get(cid, [])
        page_path = Path(info["path"])
        with Image.open(page_path) as im:
            w, h = im.size
        case = cases_index[cid]
        rec = SampleRecord(
            sample_id=f"pre-{cid.lower()}",
            image=ImageRef(path=str(page_path), sha256=sha256_file(page_path), width=w, height=h),
            boxes=[
                BoxAnnotation(
                    polygon=xyxy_to_polygon(*m["xyxy"]),
                    cls="sfx",
                    text=m["texts"][0] if m["texts"] else None,
                )
                for m in merged
            ],
            annotation_status="pseudo",
            provenance={
                "type": "asset_case",
                "case_id": cid,
                "source_url": case["source"],
                "source_id": case["source_id"],
                "stage": "annotate-r1-stage1",
                "review_domain": info["domain"],
                "boxes_meta": [
                    {"conf": m["conf"], "sources": m["sources"], "texts": m["texts"]} for m in merged
                ],
                "quality_note": "AI 预标注合并草稿（三源去重，全 pseudo）；阶段二用户逐条裁决",
                "evidence": "l1-fullpage-conf-scan.json + density-scan.json + qual-BJ06.json + l3-reference-crops.json",
            },
            group=info["group"],
            created_at=stamp,
        )
        page_records.append(rec)

    # --- ogkalu 43 region 样本（源②/③，T1a import_ogkalu 复用）---
    ogkalu_records = import_ogkalu(cases_index, roots, stamp)
    for rec in ogkalu_records:
        rec.provenance["stage"] = "annotate-r1-stage1"
        rec.provenance["review_domain"] = "ko-ogkalu-crop"

    selection = {
        "tool": "experiments/M2-SFX-ANNOTATE-R1/stage1_preannotate.py --step assemble",
        "generated_at_utc": stamp,
        "seed": SEED,
        "seed_note": "沿 T1a splits.SEED_DEFAULT=20261004；密度并列时按 sha256(seed:case_id) 升序决胜（与 T1a 排序切片同款，可复现）",
        "rule": "按页 sfx 合并候选框数降序取 top；BJ/K 域候选池小于承诺量时全选并如实登记缺口，不凑数",
        "commitment": {"bj_pages": COMMIT_BJ_PAGES, "ko_pages": COMMIT_KO_PAGES, "replay_pages": COMMIT_REPLAY_PAGES},
        "density": density,
        "selected": {"bj": bj_selected, "ko": ko_selected, "replay": replay_selected},
        "gaps": {
            "bj": {"selected": len(bj_selected), "committed": COMMIT_BJ_PAGES,
                   "note": f"cases.json BJ 组仅 {len(bj_pool)} case 在盘（BJ01-15），素材树无更多 BJ 页，缺口 {COMMIT_BJ_PAGES - len(bj_selected)} 页待素材扩充"},
            "ko": {"selected": len(ko_selected), "committed": COMMIT_KO_PAGES,
                   "note": f"cases.json K 组 25 case，在盘 {len(ko_pool)}（K01-K10，base.png 布局）；K11-K25 的 local_path 韩漫_KO/02_public_ground_truth_peppercarrot 三个素材根均不存在，缺口 {COMMIT_KO_PAGES - len(ko_selected)} 页 MISSING"},
        },
        "missing_pages": {cid: pages[cid]["local_path"] for cid in sorted(pages) if pages[cid]["status"] == "missing"},
    }

    # --- manifest 落盘（T1a schema：页级 + ogkalu）---
    manifest = [r.to_dict() for r in page_records + ogkalu_records]
    PREANNOTATE_JSON.parent.mkdir(parents=True, exist_ok=True)
    PREANNOTATE_JSON.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    SELECTION_JSON.parent.mkdir(parents=True, exist_ok=True)
    SELECTION_JSON.write_text(json.dumps(selection, ensure_ascii=False, indent=1), encoding="utf-8")

    n_boxes = sum(len(r.boxes) for r in page_records)
    n_ogk = sum(len(r.boxes) for r in ogkalu_records)
    print(f"page samples: {len(page_records)} | page boxes: {n_boxes} | ogkalu: {len(ogkalu_records)} samples / {n_ogk} boxes")
    print(f"selected bj={len(bj_selected)} ko={len(ko_selected)} replay={len(replay_selected)}")
    print(f"wrote {PREANNOTATE_JSON}")
    print(f"wrote {SELECTION_JSON}")
    return 0


# ---------------------------------------------------------------------------
# worksheet：预览裁切 + 页级清单（JSON+md）+ Git 内摘要
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
    """预览下采样 + AI 框描边 + unit_id/conf 标注（沿 C1 预览带 AI 框先例）。"""
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
    selection = json.loads(SELECTION_JSON.read_text(encoding="utf-8"))
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    WORKSHEET_JSON.parent.mkdir(parents=True, exist_ok=True)
    stamp = now_iso()

    units: list[dict] = []
    zero_box_pages: list[dict] = []  # 零 AI 检出的入选页（负证据页，用户直接补画）
    page_cache: dict[str, Image.Image] = {}

    def get_image(path_str: str) -> Image.Image:
        if path_str not in page_cache:
            page_cache.clear()  # K 域超长图逐页处理，控制内存峰值
            page_cache[path_str] = Image.open(Path(path_str)).convert("RGB")
        return page_cache[path_str]

    page_samples = [m for m in manifest if m["provenance"]["type"] == "asset_case"]
    ogkalu_samples = [m for m in manifest if m["provenance"]["type"] == "external_model"]

    # 页级样本 → 每框一个单元
    for m in page_samples:
        prov = m["provenance"]
        cid = prov["case_id"]
        meta = prov.get("boxes_meta", [{}] * len(m["boxes"]))
        if not m["boxes"]:
            zero_box_pages.append({"case_id": cid, "domain": prov["review_domain"],
                                   "page_file": Path(m["image"]["path"]).name})
            continue
        im = get_image(m["image"]["path"])
        for i, (b, bm) in enumerate(zip(m["boxes"], meta)):
            unit_id = f"R1-{cid}-B{i:02d}"
            xyxy = [b["polygon"][0][0], b["polygon"][0][1], b["polygon"][2][0], b["polygon"][2][1]]
            preview_name = f"{unit_id}__{cid}.png"
            pv = _annotate_preview(_crop_with_margin(im, xyxy), unit_id, bm.get("conf"), bm.get("sources", []))
            pv.save(PREVIEW_DIR / preview_name)
            units.append(
                {
                    "unit_id": unit_id,
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

    # ogkalu region 样本 → 每检出框一个单元（预览从 region crop 裁）
    for m in ogkalu_samples:
        prov = m["provenance"]
        key = prov["region_key"]
        im = get_image(m["image"]["path"])
        for i, (b, dm) in enumerate(zip(m["boxes"], prov.get("detection_conf_stats", [{}] * len(m["boxes"])))):
            unit_id = f"R1-OGK-{key}-B{i:02d}"
            xyxy = [b["polygon"][0][0], b["polygon"][0][1], b["polygon"][2][0], b["polygon"][2][1]]
            preview_name = f"{unit_id}.png"
            pv = _annotate_preview(_crop_with_margin(im, xyxy), unit_id, dm.get("conf"), ["ogkalu-text"])
            pv.save(PREVIEW_DIR / preview_name)
            units.append(
                {
                    "unit_id": unit_id,
                    "kind": "ogkalu_crop_box",
                    "domain": "ko-ogkalu-crop",
                    "case_id": prov["case_id"],
                    "region_key": key,
                    "region_crop": m["image"]["path"],
                    "box_index": i,
                    "xyxy": [round(v, 1) for v in xyxy],
                    "box_size": [round(xyxy[2] - xyxy[0], 1), round(xyxy[3] - xyxy[1], 1)],
                    "ai_cls": b["cls"],
                    "ai_conf": dm.get("conf"),
                    "conf_ge_primary": dm.get("conf_ge_primary"),
                    "sources": ["ogkalu-text"],
                    "ai_text": None,
                    "preview_file": f"previews/{preview_name}",
                    "verdict": "",
                    "user_rationale": "",
                }
            )
    page_cache.clear()

    # --- 人类可读 md（按域→页/region 分组；裁决列留空）---
    domains = {"bj": "BJ 域（毛笔竖排）", "ko": "KO 域（彩色艺术字，整页）",
               "replay-j": "域内回放（J 系）", "ko-ogkalu-crop": "KO 域（ogkalu region crop）"}
    lines = [
        "# M2-SFX-ANNOTATE-R1 阶段一 · 用户审核工作表",
        "",
        f"- 生成：{stamp} | seed={SEED}（冻结）",
        "- 裁决枚举（verdict 列）：`confirm`（确认是 SFX，框可接受）/ `correct`（是 SFX 但框需修）/ `delete`（非 SFX）/ `miss`（页级漏标，在页小节末尾补记框坐标）",
        "- 每行附预览裁切图（20% 边距上下文，红框=AI 候选框，顶部条=unit_id/conf/来源）",
        "- `user_rationale` 列：填写裁决依据（可空）；沿 C1 先例，AI 预判已预填，采纳即确认",
        "",
    ]
    for dom, dom_title in domains.items():
        dom_units = [u for u in units if u["domain"] == dom]
        if not dom_units:
            continue
        lines += [f"## {dom_title}（{len(dom_units)} 候选框）", ""]
        if dom == "ko-ogkalu-crop":
            by_region: dict[str, list[dict]] = {}
            for u in dom_units:
                by_region.setdefault(u["region_key"], []).append(u)
            for key in sorted(by_region):
                lines += [f"### {key}", "", "| unit_id | conf | xyxy | 预览 | 用户裁决 | user_rationale |", "|---|---|---|---|---|---|"]
                for u in by_region[key]:
                    conf_s = f"{u['ai_conf']:.2f}" if isinstance(u["ai_conf"], (int, float)) else "-"
                    lines.append(f"| {u['unit_id']} | {conf_s} | {u['xyxy']} | {Path(u['preview_file']).name} |  |  |")
                lines.append("")
        else:
            by_page: dict[str, list[dict]] = {}
            for u in dom_units:
                by_page.setdefault(u["case_id"], []).append(u)
            zero_in_dom = [z for z in zero_box_pages if z["domain"] == dom]
            for cid in sorted(set(by_page) | {z["case_id"] for z in zero_in_dom}):
                us = by_page.get(cid, [])
                if not us:
                    lines += [
                        f"### {cid}（0 AI 候选框——负证据页：模型在该页无 SFX 检出，chiqui7 对 BJ 域存在已知盲区）",
                        "",
                        f"→ 请用户直接补画漏标 SFX 框（`miss` + 框坐标，页文件：{next(z['page_file'] for z in zero_in_dom if z['case_id'] == cid)}）",
                        "",
                    ]
                    continue
                lines += [f"### {cid}（{len(us)} 候选框；页级漏标补记：`miss` + 框坐标）", "",
                          "| unit_id | conf | 来源 | xyxy | 预览 | 用户裁决 | user_rationale |", "|---|---|---|---|---|---|---|"]
                for u in us:
                    conf_s = f"{u['ai_conf']:.2f}" if isinstance(u["ai_conf"], (int, float)) else "ref"
                    lines.append(
                        f"| {u['unit_id']} | {conf_s} | {'/'.join(u['sources'])} | {u['xyxy']} | {Path(u['preview_file']).name} |  |  |"
                    )
                lines.append("")

    WORKSHEET_JSON.write_text(
        json.dumps({"generated_at_utc": stamp, "seed": SEED, "n_units": len(units), "units": units},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    WORKSHEET_MD.write_text("\n".join(lines), encoding="utf-8")

    # --- Git 内摘要 ---
    per_dom = {}
    for u in units:
        per_dom.setdefault(u["domain"], 0)
        per_dom[u["domain"]] += 1
    # conf 分层（页级候选框）：用户可选 conf 阈值缩减审核量的决策数据（不擅自裁剪）
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
    summary = {
        "task": "M2-SFX-ANNOTATE-R1 stage-1",
        "generated_at_utc": stamp,
        "seed": SEED,
        "pages_selected": selection["selected"],
        "page_box_counts": selection["density"],
        "commitment_gaps": selection["gaps"],
        "missing_pages": selection["missing_pages"],
        "units_total": len(units),
        "units_by_domain": per_dom,
        "conf_tiers_all_units": conf_tiers,
        "zero_box_pages": zero_box_pages,
        "duration_estimate": _duration_estimate(len(units)),
        "artifacts": {
            "preannotate_manifest": str(PREANNOTATE_JSON),
            "selection": str(SELECTION_JSON),
            "worksheet_json": str(WORKSHEET_JSON),
            "worksheet_md": str(WORKSHEET_MD),
            "preview_dir": str(PREVIEW_DIR),
            "scan_raw": str(SCAN_JSON),
        },
        "artifact_sha256": {
            "preannotate_manifest": sha256_file(PREANNOTATE_JSON),
            "worksheet_json": sha256_file(WORKSHEET_JSON),
            "worksheet_md": sha256_file(WORKSHEET_MD),
            "selection": sha256_file(SELECTION_JSON),
        },
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"units: {len(units)} | by domain: {per_dom}")
    print(f"wrote {WORKSHEET_JSON}")
    print(f"wrote {WORKSHEET_MD}")
    print(f"wrote {SUMMARY_JSON}")
    return 0


def _duration_estimate(n_units: int) -> dict:
    """按 C1 实测速率估用户审核时长。

    依据：M2-DOCTR-QUAL-C1（doc/tasks/M2-DOCTR-QUAL-C1.md:25）n=50 单元逐条人工
    审核 = 「小时级人工抽检」→ 约 1-2 分钟/单元（region 语境看图+裁决）。
    本次为框级裁切预览（上下文更小），取同区间作估算带。
    """
    return {
        "basis": "C1 先例 n=50 单元=小时级（doc/tasks/M2-DOCTR-QUAL-C1.md:25）→ 1-2 分钟/单元",
        "units": n_units,
        "minutes_low": n_units * 1,
        "minutes_high": n_units * 2,
        "hours_low": round(n_units / 60, 1),
        "hours_high": round(n_units * 2 / 60, 1),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True, choices=["scan", "assemble", "worksheet", "all"])
    args = parser.parse_args()
    steps = [args.step] if args.step != "all" else ["scan", "assemble", "worksheet"]
    for s in steps:
        rc = {"scan": cmd_scan, "assemble": cmd_assemble, "worksheet": cmd_worksheet}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
