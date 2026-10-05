"""M2-SFX-ANNOTATE-R3 阶段二收尾（合同 AC3）：R3 判定并入 + manifest.r3 + train-v3 重建。

复合蓝本（均只读）：R2 stage2_finalize_r2.py（判定并入+provenance.stage3r3 语义）+
V2 prepare_dataset_v2.py（own-manga 并入+pinned 重切+YOLO 重建+双通道校验）。

- 判定源 = R3 judgments（units.json 22 单元：bj_new 6+bj_lowconf_leftover 16；
  consensus 19+divergence 3→arbiter 终裁；final=confirm 6+correct 1+delete 15）。
- 底册 = R2 preannotate/manifest.r2.json（82 样本=27 complete+55 pseudo，只读；
  **口径登记**：ask 字面「final manifest 82 样本」与文件事实不符——R2 final/
  manifest.r2.json 实为 351 样本（27 complete+324 synthetic），82 样本的底册本体是
  preannotate/manifest.r2.json；遗留 16 单元的判定更新对象（pre-bj19/20/21/22
  pseudo 页）只存在于该 82 样本底册，且「provenance.stage3r3 沿 R2 stage2r2 语义」
  的 R2 stage2 底册正是此文件，故按 preanimate 82 底册执行，全链摘要如实登记）。
- 遗留 16 单元判定更新（stage3r3，human_review=false）：
  pre-bj16 +B04/B05/B06 confirm 回填（R2 unjudged 框转正，坐标取 units.json）→
  complete 6 框；pre-bj17/18 判定全 delete→考卷框不动留痕；pre-bj19/20/21 全
  delete→空框 pseudo 负证据；pre-bj22 B00 confirm+B01 correct（框保留原坐标+
  revision 留痕，沿 R2 correct 口径）→complete 2 框。
- 新 12 页（manifest-bj-new.json）：BJ28/29 confirm→complete 各 1 框；
  BJ26/27/30/31 唯一框 delete→空框 pseudo 负证据；BJ32-37 零候选→pseudo 零框
  负证据（chiqui7 盲区页，AC1 目检确认含毛笔 SFX，留 miss 通道）。
- manifest.r3.json = R2 底册 82（更新后）+ BJ26-37 12 = real 94 样本（T1a schema
  逐样本校验 0 错误；R2 判定链 stage2r2 不覆盖，R3 判定链写 stage3r3）。
- train-v3 = pos 30（complete）+synth 324（R1 synthetic 只读，pinned train）+
  own-manga 558（入册包只读，六组 pinned train）=912 全量；
  assign_splits(force=True, pinned=…) 重算：synthetic/annotate-r1→train、
  densho810/vol05→challenge（考卷组不动）、own-manga 六组→train。
  断言：考卷 5 框不动（challenge 2 样本框数与坐标逐位=R2 出厂）+R2 非 vol05 组
  349 样本零漂移+考卷零重叠（组名/id/页图 sha256 三层）+组隔离 0 违例+
  challenge 5 框逐框溯源 R2 判定链。
- YOLO：train-v3/dataset/{images,labels}/{train,val,test,challenge}/+dataset.yaml；
  names 双通道（读回断言+pyyaml）+ultralytics check_det_dataset 扫描冒烟；
  label 与 R2 出厂逐字节交叉比对（pre-bj16 例外=R2 原内容+3 行新增，特判比对）。

纪律：零 src（生产 SFX_CLASS_MAP 只读 import）；R2/R1 数据树、T1a 模块、
own-manga 入册包只读；数据本体落 training_data/（gitignored），Git 只进摘要。

步骤（--step）：manifest → reassign → yolo → summary（all 依序全跑）。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA"))
sys.path.insert(0, str(REPO_ROOT / "src"))

from sfx_data_infra.atomicio import atomic_write_json, load_manifest, write_manifest  # noqa: E402
from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import SampleRecord  # noqa: E402
from sfx_data_infra.splits import (  # noqa: E402
    CHALLENGE_CASE_IDS,
    SEED_DEFAULT,
    TrainingSetBuilder,
    assign_splits,
    split_fingerprint,
)
from sfx_data_infra.importers import xyxy_to_polygon  # noqa: E402

# 生产类表只读 import（零 src：不改动，仅读取常量）。
# 来源 src/infrastructure/providers/detection_sfx.py:137
#   SFX_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
from infrastructure.providers.detection_sfx import SFX_CLASS_MAP  # noqa: E402

R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
R2_ANNOTATE = R2_WORKTREE / "training_data" / "sfx-v1" / "annotate-r2"
R2_BASE_MANIFEST = R2_ANNOTATE / "preannotate" / "manifest.r2.json"  # R2 底册 82（只读）
R2_FINAL = R2_ANNOTATE / "final"
R2_YOLO = R2_FINAL / "yolo"
R1_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode")
R1_ANNOTATE = R1_WORKTREE / "training_data" / "sfx-v1" / "annotate-r1"
SYNTH_MANIFEST = R1_ANNOTATE / "synthetic" / "manifest.json"  # R1 合成 324（只读并入）
SYNTH_IMG_ROOT = R1_ANNOTATE

OWN_INGEST_DIR = Path(r"G:/CODEX/New Manga.task-envs/sfx-synth-exp/own-manga-ingest")
OWN_PACKAGE = OWN_INGEST_DIR / "own_manga_manifest_records.json"

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r3"
JUDG_DIR = OUT_DIR / "judgments"
R3_BJ_NEW_JSON = OUT_DIR / "preannotate" / "manifest-bj-new.json"
R3_MANIFEST = OUT_DIR / "preannotate" / "manifest.r3.json"  # real 94（本轮产物）

TRAIN3_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "train-v3"
YAML_DIR = TRAIN3_DIR / "dataset"
SUMMARY_JSON = TRAIN3_DIR / "export-summary.json"
GIT_SUMMARY = REPO_ROOT / "verification" / "M2-SFX-ANNOTATE-R3" / "stage-r3-summary.json"

SEED = SEED_DEFAULT  # 20261004（沿 T1a/R1/R2/V1，seed 冻结）
CHALLENGE_GROUP = "densho810/vol05"  # 考卷组不动（沿 V1/V2）
SYNTH_GROUP = "synthetic/annotate-r1"
OWN_GROUPS = tuple(f"own-manga/{v}" for v in ("v01", "v02s", "v12", "v13", "v15", "v16"))
PINNED: dict[str, str] = {
    SYNTH_GROUP: "train",
    CHALLENGE_GROUP: "challenge",
    **{g: "train" for g in OWN_GROUPS},
}
EXPECTED_CHALLENGE = {"pre-bj17": ("BJ17", 2, "vol05_p0167"), "pre-bj18": ("BJ18", 3, "vol05_p0065")}
KEEP_VERDICTS = ("confirm", "correct")
CLS_SFX_ID = next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx")
JUDG_SOURCES = ["judgments/consensus.json", "judgments/divergence.json",
                "judgments/arbiter/batch-*.json"]
REVIEWER_CONSENSUS = "codex+agy-consensus"
REVIEWER_ARBITER = "arbiter"
EXPECTED_OWN_PAGES = {"own-manga/v01": 125, "own-manga/v02s": 103, "own-manga/v12": 88,
                      "own-manga/v13": 105, "own-manga/v15": 53, "own-manga/v16": 84}
EXPECTED_OWN_TOTAL = (558, 1738)
ANNOTATION_GRADE_EXPECTED = {"partial": 140, "pseudo": 418}
TRAIN_VENV_DEFAULT = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/Scripts/python.exe")

BJ22_CORRECT_FIX_HINT = [1840, 60, 2100, 570]  # 仲裁 rationale 的重框参考区域（仅留痕，不改坐标）

_state: dict = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 判定装载（沿 R2 load_final_verdicts）
# ---------------------------------------------------------------------------


def load_final_verdicts() -> tuple[dict[str, dict], dict]:
    cons = _read_json(JUDG_DIR / "consensus.json")["consensus"]
    div = _read_json(JUDG_DIR / "divergence.json")["divergence"]
    arb: list[dict] = []
    for p in sorted((JUDG_DIR / "arbiter").glob("batch-*.json")):
        arb.extend(_read_json(p)["judgments"])

    vmap: dict[str, dict] = {}
    for c in cons:
        vmap[c["id"]] = {
            "verdict": c["verdict"],
            "reviewer": REVIEWER_CONSENSUS,
            "rationale": f"codex: {c['rationale_codex']} ｜ agy: {c['rationale_agy']}",
        }
    arb_by_id = {j["id"]: j for j in arb}
    n_arb_used = 0
    for d in div:
        j = arb_by_id.get(d["id"])
        if j is None:
            raise ValueError(f"divergence 单元 {d['id']} 无对应仲裁判定（arbiter/batch-*.json）")
        vmap[d["id"]] = {"verdict": j["verdict"], "reviewer": REVIEWER_ARBITER, "rationale": j["rationale"]}
        n_arb_used += 1
    unused_arb = sorted(set(arb_by_id) - {d["id"] for d in div})
    if unused_arb:
        raise ValueError(f"仲裁判定含 divergence 之外的单元: {unused_arb}")

    units = _read_json(JUDG_DIR / "units.json")["units"]
    covered = {u["id"] for u in units}
    if set(vmap) != covered:
        raise ValueError(f"判定覆盖不一致: units−vmap={sorted(covered - set(vmap))} vmap−units={sorted(set(vmap) - covered)}")
    stats = {
        "units_total": len(units),
        "units_by_part": dict(Counter(u["part"] for u in units)),
        "consensus": len(cons),
        "divergence_arbitrated": n_arb_used,
        "verdict_dist": dict(Counter(v["verdict"] for v in vmap.values())),
        "reviewer_dist": dict(Counter(v["reviewer"] for v in vmap.values())),
    }
    return vmap, stats


def _units_by_id() -> dict[str, dict]:
    return {u["id"]: u for u in _read_json(JUDG_DIR / "units.json")["units"]}


def _unit_box(unit: dict) -> dict:
    """units.json xyxy → T1a 框（polygon=实例包络）。"""
    x0, y0, x1, y1 = unit["xyxy"]
    return {"polygon": xyxy_to_polygon(x0, y0, x1, y1), "cls": "sfx", "text": None}


# ---------------------------------------------------------------------------
# step manifest：R2 底册判定更新（stage3r3）+ BJ26-37 → manifest.r3.json（real 94）
# ---------------------------------------------------------------------------


def _units_for_sample(m: dict, rnd: str) -> list[str]:
    prov = m["provenance"]
    if prov["type"] == "asset_case":
        prefix = f"{rnd}-{prov['case_id']}-"
        return [f"{prefix}B{i:02d}" for i in range(len(m["boxes"]))]
    return []


def _xyxy_close(a: list[float], b: list[float], tol: float = 0.15) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def _apply_r3_to_r2_sample(m: dict, vmap: dict[str, dict], units: dict[str, dict]) -> bool:
    """R2 底册样本的 R3 遗留单元判定更新（provenance.stage3r3，不覆盖 stage2r2）。

    单元 id 对应口径：R3 判定单元 id 编号基于 R2 worksheet 原预标注框索引
    （如 BJ16 候选 7 框=B00-06），而 R2 底册 complete 样本只保留 R2 判定保留框
    （pre-bj16 现 3 框=B00-02）——故本函数按 case 从 vmap 直接取判定单元并用
    **原预标注索引**对照底册框数区分「原框处理」与「unjudged 回填」。
    """
    prov = m["provenance"]
    case = prov["case_id"]
    judged = sorted(
        (int(uid.rsplit("-B", 1)[1]), uid, vmap[uid]) for uid in vmap if uid.startswith(f"R2-{case}-")
    )
    if not judged:
        return False
    orig_boxes = m["boxes"]
    orig_meta = prov.get("boxes_meta") or [{}] * len(orig_boxes)
    n_orig = len(orig_boxes)

    excluded = [{"unit_id": uid, "verdict": "delete", "reviewer": v["reviewer"],
                 "rationale": v["rationale"]} for _i, uid, v in judged if v["verdict"] == "delete"]
    keep_judged = [(i, uid, v) for i, uid, v in judged if v["verdict"] in KEEP_VERDICTS]

    if not keep_judged:
        if m["annotation_status"] == "complete":
            # complete 样本（含 challenge 考卷页 pre-bj17/18）：遗留单元全 delete，框列表不动仅留痕
            prov["stage3r3"] = {
                "action": "kept_complete_delete_leftovers_excluded",
                "note": ("complete 样本本轮遗留单元判定全 delete：无回填无剔除，框列表保持不变"
                         "（challenge 考卷页内容零改动，考卷 5 框不动断言的留痕依据）；"
                         "R2 判定链 stage2r2 未改动"),
                "mode": "ai-review-backfill",
                "judgments_sources": JUDG_SOURCES,
                "reviewed_units": len(judged),
                "excluded_delete_units": excluded,
                "human_review": False,
            }
            return True
        # pseudo 页全部候选框 delete：空框 pseudo 负证据
        m["boxes"] = []
        if prov.get("boxes_meta") is not None:
            prov["boxes_meta"] = []
        prov["stage3r3"] = {
            "action": "kept_pseudo_zero_box_negative_evidence",
            "note": ("R2 conf<0.2 遗留候选框本轮扩审全 delete：样本保持 pseudo 空框负证据；"
                     "delete 框已从框列表排除并在此留痕；R2 判定链 stage2r2 未改动"),
            "mode": "ai-review-backfill",
            "judgments_sources": JUDG_SOURCES,
            "reviewed_units": len(judged),
            "excluded_delete_units": excluded,
            "human_review": False,
        }
        return True

    # keep 情形：原框（idx<n_orig）按判定保留/修正；unjudged（idx>=n_orig）confirm 回填
    new_boxes, new_meta, corrections, added = [], [], [], []
    for i in range(n_orig):
        j = next((x for x in keep_judged if x[0] == i), None)
        d = next((x for x in judged if x[0] == i and x[2]["verdict"] == "delete"), None)
        if d is not None:
            continue  # 原框被 R3 判 delete：排除留痕
        b = orig_boxes[i]
        bm = dict(orig_meta[i] or {})
        if j is not None:
            _i, uid, v = j
            bm.update({"unit_id": uid, "verdict": v["verdict"],
                       "reviewer": v["reviewer"], "rationale": v["rationale"]})
            if v["verdict"] == "correct":
                b = dict(b)
                b["occluded"] = bool(b.get("occluded", False))
                bm["revision"] = {
                    "type": "correction_note",
                    "needs_fix": True,
                    "note": v["rationale"],
                    "fix_hint_xyxy_page": BJ22_CORRECT_FIX_HINT if uid == "R2-BJ22-B01" else None,
                    "reviewer": v["reviewer"],
                    "coordinates_changed": False,
                }
                corrections.append({"unit_id": uid, "note": v["rationale"]})
        new_boxes.append(b)
        new_meta.append(bm)
    for _i, uid, v in keep_judged:
        if _i < n_orig:
            continue  # 原框，已在上方处理
        unit = units[uid]
        nb = _unit_box(unit)
        nbm = {"conf": unit["conf"], "sources": [unit["source"]], "texts": [],
               "unit_id": uid, "verdict": v["verdict"], "reviewer": v["reviewer"],
               "rationale": v["rationale"],
               "backfill_note": ("R2 unjudged 框（conf<0.2 未入 R2 正集 GT）本轮扩审 confirm 回填，"
                                 "坐标=units.json")}
        new_boxes.append(nb)
        new_meta.append(nbm)
        added.append({"unit_id": uid, "conf": unit["conf"], "xyxy": unit["xyxy"]})

    m["boxes"] = new_boxes
    if prov.get("boxes_meta") is not None:
        prov["boxes_meta"] = new_meta
    m["annotation_status"] = "complete"
    prov["quality_note"] = (
        "AI 代审正集样本（R3 扩标轮 2026-10-05）：boxes=R2 判定保留框+R3 遗留单元判定保留框"
        "（codex+agy 共识+分歧仲裁），判定链 provenance.stage2r2（R2）+stage3r3（R3）；"
        "human_review=false，不谎称人工"
    )
    prov["stage3r3"] = {
        "action": "completed",
        "mode": "ai-review-backfill",
        "judgments_sources": JUDG_SOURCES,
        "reviewed_units": len(judged),
        "kept_units": len(new_boxes),
        "added_units": added,
        "excluded_delete_units": excluded,
        "correction_notes": corrections,
        "human_review": False,
    }
    return True


def _apply_r3_to_bj_new(m: dict, vmap: dict[str, dict]) -> bool:
    """BJ26-37 新页样本按 R3 判定更新（stage3r3）。"""
    prov = m["provenance"]
    uids = _units_for_sample(m, "R3")
    judged = [(i, vmap[uid]) for i, uid in enumerate(uids) if uid in vmap]
    if not judged:
        if m["boxes"]:
            raise ValueError(f"{m['sample_id']}: 有候选框却无判定单元（口径错误）")
        prov["stage3r3"] = {
            "action": "kept_pseudo_zero_candidates_negative_evidence",
            "note": ("chiqui7 整页 letterbox 零候选框（负证据页）：该页经 AC1 目检确认含毛笔竖排 SFX"
                     "（selection/material-selection-r3.json visual_adjudication），chiqui7 对 BJ 域"
                     "毛笔形态盲区的实证；样本保持 pseudo 零框，SFX 标注留给判定轮 miss 补画通道"),
            "human_review": False,
        }
        return True

    meta = prov.get("boxes_meta") or [{}] * len(m["boxes"])
    keep_idx = [i for i, v in judged if v["verdict"] in KEEP_VERDICTS]
    excluded = [{"unit_id": uids[i], "verdict": "delete", "reviewer": v["reviewer"],
                 "rationale": v["rationale"]} for i, v in judged if v["verdict"] == "delete"]
    if not keep_idx:
        m["boxes"] = []
        if prov.get("boxes_meta") is not None:
            prov["boxes_meta"] = []
        prov["stage3r3"] = {
            "action": "kept_pseudo_zero_box_negative_evidence",
            "note": "本轮判定无 confirm/correct（全部候选框 delete）：pseudo 空框负证据留痕",
            "mode": "ai-review-backfill",
            "judgments_sources": JUDG_SOURCES,
            "reviewed_units": len(judged),
            "excluded_delete_boxes": excluded,
            "human_review": False,
        }
        return True

    new_boxes, new_meta = [], []
    for i, v in judged:
        if v["verdict"] in KEEP_VERDICTS:
            b = m["boxes"][i]
            bm = dict(meta[i] or {})
            bm.update({"unit_id": uids[i], "verdict": v["verdict"],
                       "reviewer": v["reviewer"], "rationale": v["rationale"]})
            new_boxes.append(b)
            new_meta.append(bm)
    m["boxes"] = new_boxes
    if prov.get("boxes_meta") is not None:
        prov["boxes_meta"] = new_meta
    m["annotation_status"] = "complete"
    prov["quality_note"] = (
        "AI 代审正集样本（R3 扩标轮 2026-10-05）：boxes=本轮判定保留框"
        "（codex+agy 共识+分歧仲裁），provenance.stage3r3 留判定链；human_review=false"
    )
    prov["stage3r3"] = {
        "action": "completed",
        "mode": "ai-review-backfill",
        "judgments_sources": JUDG_SOURCES,
        "reviewed_units": len(judged),
        "kept_units": len(new_boxes),
        "excluded_delete_boxes": excluded,
        "correction_notes": [],
        "human_review": False,
    }
    return True


def cmd_manifest() -> int:
    vmap, _ = load_final_verdicts()
    units = _units_by_id()
    base = _read_json(R2_BASE_MANIFEST)
    base_samples = base["samples"] if isinstance(base, dict) else base
    if len(base_samples) != 82:
        raise RuntimeError(f"R2 底册 {len(base_samples)} 样本 != 82")
    bj_new = _read_json(R3_BJ_NEW_JSON)

    dup = sorted({m["sample_id"] for m in base_samples} & {m["sample_id"] for m in bj_new})
    if dup:
        raise ValueError(f"sample_id 冲突: {dup}")

    # 底册遗留判定对应的框坐标核对（pseudo 页框序=R2 worksheet 单元序）
    for m in base_samples:
        prov = m["provenance"]
        if prov.get("case_id") not in ("BJ19", "BJ20", "BJ21", "BJ22"):
            continue
        uids = _units_for_sample(m, "R2")
        for i, uid in enumerate(uids):
            if uid in units and i < len(m["boxes"]):
                b = m["boxes"][i]
                bx = [round(b["polygon"][0][0], 1), round(b["polygon"][0][1], 1),
                      round(b["polygon"][2][0], 1), round(b["polygon"][2][1], 1)]
                if not _xyxy_close(bx, units[uid]["xyxy"]):
                    raise ValueError(f"{m['sample_id']} 框{i} 与 {uid} xyxy 失配: {bx} vs {units[uid]['xyxy']}")

    n_touched = 0
    for m in base_samples:
        if _apply_r3_to_r2_sample(m, vmap, units):
            n_touched += 1
    n_new_completed = 0
    for m in bj_new:
        before = m["annotation_status"]
        _apply_r3_to_bj_new(m, vmap)
        if m["annotation_status"] != before:
            n_new_completed += 1

    man = base_samples + bj_new
    for m in man:
        rec = SampleRecord.from_dict(m)
        errors = rec.validate()
        if errors:
            raise ValueError(f"{m['sample_id']}: {errors}")
        prov = m["provenance"]
        if prov["type"] == "asset_case" and prov.get("boxes_meta") is not None:
            if len(prov["boxes_meta"]) != len(m["boxes"]):
                raise ValueError(f"{m['sample_id']}: boxes_meta 与 boxes 索引失配")
        for key in ("stage2", "stage2r2", "stage3r3"):
            st = (prov.get(key) or {}).get("action")
            if st == "completed" and not m["boxes"]:
                raise ValueError(f"{m['sample_id']}: {key}=completed 样本不允许空框")

    atomic_write_json(R3_MANIFEST, man)
    status = Counter(m["annotation_status"] for m in man)
    bj_pos = [m for m in man if m["annotation_status"] == "complete"
              and m["provenance"].get("review_domain") == "bj"]
    print(f"[manifest] samples={len(man)} (r2_base=82 + bj_new=12) status={dict(status)}")
    print(f"[manifest] r2_touched={n_touched} bj_new_to_complete={n_new_completed}")
    print(f"[manifest] BJ 正集: {len(bj_pos)} 页 {sum(len(m['boxes']) for m in bj_pos)} 框 "
          f"({[m['provenance']['case_id'] for m in bj_pos]})")
    return 0


# ---------------------------------------------------------------------------
# step reassign：pos 30 + synth 324 + own 558 → pinned 重算 → train-v3 manifest
# ---------------------------------------------------------------------------


def _load_own_records() -> tuple[list[SampleRecord], dict]:
    container = _read_json(OWN_PACKAGE)
    for key in ("schema_version", "material_root", "record_count", "box_count",
                "generated_at", "records"):
        if key not in container:
            raise ValueError(f"own-manga 入册包缺顶层字段 {key}")
    if container["schema_version"] != "sfx-data-infra/sample@1":
        raise ValueError(f"包 schema_version={container['schema_version']!r} 异常")
    raw = container["records"]
    if container["record_count"] != len(raw):
        raise ValueError(f"包 record_count={container['record_count']} != records 长度")

    def _checked(m: dict, tag: str) -> SampleRecord:
        rec = SampleRecord.from_dict(m)
        errors = rec.validate()
        if errors:
            raise AssertionError(f"{tag} {rec.sample_id}: validate 错误 {errors}")
        return rec

    sample3 = sorted(raw, key=lambda m: m["sample_id"])[:3]
    for m in sample3:
        _checked(m, "抽样")
    records = [_checked(m, f"records[{i}]") for i, m in enumerate(raw)]
    if len(records) != EXPECTED_OWN_TOTAL[0]:
        raise AssertionError(f"own-manga 样本数 {len(records)} != {EXPECTED_OWN_TOTAL[0]}")
    total_boxes = sum(len(r.boxes) for r in records)
    if total_boxes != EXPECTED_OWN_TOTAL[1] or container["box_count"] != EXPECTED_OWN_TOTAL[1]:
        raise AssertionError(f"own-manga 总框数 {total_boxes} != {EXPECTED_OWN_TOTAL[1]}")
    pages = Counter(r.group for r in records)
    if dict(pages) != EXPECTED_OWN_PAGES:
        raise AssertionError(f"own-manga 分组页数 {dict(pages)} != {EXPECTED_OWN_PAGES}")
    status = Counter(r.annotation_status for r in records)
    if dict(status) != ANNOTATION_GRADE_EXPECTED:
        raise AssertionError(f"own-manga status {dict(status)} != {ANNOTATION_GRADE_EXPECTED}")
    if any(r.split != "unassigned" for r in records):
        raise AssertionError("own-manga 包内 split 非 unassigned")
    sha_seen: dict[str, str] = {}
    for r in records:
        if r.image.sha256 in sha_seen:
            raise AssertionError(f"own-manga 页图 sha256 重复: {r.sample_id}")
        sha_seen[r.image.sha256] = r.sample_id
    missing = [r.sample_id for r in records if not Path(r.image.path).is_file()]
    if missing:
        raise FileNotFoundError(f"own-manga 页图不在盘 {len(missing)} 张: {missing[:5]}")
    meta = {"package_sha256": sha256_file(OWN_PACKAGE), "material_root": container["material_root"],
            "pages_by_group": dict(sorted(pages.items())),
            "boxes_by_group": {g: sum(len(r.boxes) for r in records if r.group == g) for g in sorted(OWN_GROUPS)},
            "status": dict(status), "validate": {"total": len(records), "errors": 0}}
    print(f"[own] {len(records)} records validate 0 错误; boxes={total_boxes}; 页图全在盘")
    return records, meta


def cmd_reassign() -> int:
    vmap, judge_stats = load_final_verdicts()
    r3_man = _read_json(R3_MANIFEST)
    r3_samples = r3_man["samples"] if isinstance(r3_man, dict) else r3_man
    pos_raw = [m for m in r3_samples if m["annotation_status"] == "complete"]
    pos = [SampleRecord.from_dict(m) for m in pos_raw]

    # R2 出厂基准（考卷不动断言 + 零漂移断言的基准）
    r2_container = _read_json(R2_FINAL / "manifest.r2.json")
    r2_samples_raw = r2_container["samples"]
    r2_by_id = {s["sample_id"]: s for s in r2_samples_raw}
    r2_split = {s["sample_id"]: s["split"] for s in r2_samples_raw}

    # 断言：考卷 5 框不动（R3 manifest 中 pre-bj17/18 与 R2 出厂逐位一致）
    exam_report = []
    for sid, (case, n_box, page) in EXPECTED_CHALLENGE.items():
        r3_m = next(m for m in r3_samples if m["sample_id"] == sid)
        r2_m = r2_by_id[sid]
        if len(r3_m["boxes"]) != n_box or len(r2_m["boxes"]) != n_box:
            raise AssertionError(f"{sid}: 考卷框数变动 r3={len(r3_m['boxes'])} r2={len(r2_m['boxes'])} != {n_box}")
        for b3, b2 in zip(r3_m["boxes"], r2_m["boxes"]):
            if b3["polygon"] != b2["polygon"]:
                raise AssertionError(f"{sid}: 考卷框坐标变动（考卷 5 框不动断言失败）")
        st3 = r3_m["provenance"]["stage3r3"]
        if not st3.get("excluded_delete_units"):
            raise AssertionError(f"{sid}: 考卷页 R3 判定留痕缺失（excluded_delete_units 空）")
        exam_report.append({"sample_id": sid, "case_id": case, "boxes": len(r3_m["boxes"]),
                            "r3_deleted_leftover_units": [e["unit_id"] for e in st3.get("excluded_delete_units", [])]})
    exam_boxes = sum(e["boxes"] for e in exam_report)
    if exam_boxes != 5:
        raise AssertionError(f"考卷总框数 {exam_boxes} != 5")
    print(f"[reassign] 考卷 5 框不动断言 PASS: {exam_report}")

    synth_raw = _read_json(SYNTH_MANIFEST)
    synth = [SampleRecord.from_dict(d) for d in synth_raw]
    if len(synth) != 324:
        raise AssertionError(f"synthetic {len(synth)} != 324")
    own, own_meta = _load_own_records()

    # T1a 挑战单列规则（BJ13/14/15）本集零命中（沿 V2 语义）
    rule_hits = [s.sample_id for s in pos + synth + own
                 if s.provenance.get("case_id") in CHALLENGE_CASE_IDS or s.provenance.get("challenge") is True]
    if rule_hits:
        raise AssertionError(f"挑战单列规则意外命中 {rule_hits}")

    all_records = pos + synth + own
    assign_splits(all_records, seed=SEED, force=True, pinned=dict(PINNED))

    # 断言 A1：R2 非 vol05 组 349 样本零漂移（重算复现 R2 出厂）
    drift = []
    for s in pos + synth:
        if s.sample_id in r2_split and s.group != CHALLENGE_GROUP and s.split != r2_split[s.sample_id]:
            drift.append((s.sample_id, r2_split[s.sample_id], s.split))
    if drift:
        raise AssertionError(f"重算对 R2 非 vol05 组产生 {len(drift)} 处漂移: {drift[:10]}")
    # 断言 A2：vol05 组 challenge 恰 pre-bj17/pre-bj18
    moved = sorted(s.sample_id for s in pos if s.group == CHALLENGE_GROUP and s.split == "challenge")
    if moved != sorted(EXPECTED_CHALLENGE):
        raise AssertionError(f"vol05 组 challenge 成员 {moved} != {sorted(EXPECTED_CHALLENGE)}")
    # 断言 A3：新 complete 3 样本（pre-bj22/28/29）落 train（densho810/vol01|vol03 组）
    new_pos = {s.sample_id: s.split for s in pos if s.sample_id in ("pre-bj22", "pre-bj28", "pre-bj29")}
    if set(new_pos.values()) != {"train"}:
        raise AssertionError(f"R3 新正集样本 split {new_pos} != 全 train")
    # 断言 A4：own/synth 全 train
    if {s.split for s in own} != {"train"}:
        raise AssertionError("own-manga 未全落 train")
    if {s.split for s in synth} != {"train"}:
        raise AssertionError("synthetic 未全落 train")

    # 断言 B：考卷零重叠（own vs R2 系：组名/id/页图 sha256 三层）
    own_groups = {s.group for s in own}
    densho_groups = {s.group for s in pos if s.group.startswith("densho810/")}
    if not own_groups.isdisjoint(densho_groups):
        raise AssertionError("own 与 densho 组名交集非空")
    if {s.sample_id for s in own} & {s.sample_id for s in pos}:
        raise AssertionError("own 与 pos 样本 id 交集非空")
    own_sha = {s.image.sha256 for s in own}
    pos_sha = {s.image.sha256 for s in pos}
    if own_sha & pos_sha:
        raise AssertionError(f"页图 sha256 碰撞 {len(own_sha & pos_sha)}")
    challenge_sha = {s.image.sha256 for s in pos if s.split == "challenge"}
    if challenge_sha & own_sha:
        raise AssertionError("考卷页图出现在 own-manga")

    # 断言 C：组隔离全量 0 违例
    by_group_split: dict[str, set[str]] = {}
    for s in all_records:
        by_group_split.setdefault(s.group, set()).add(s.split)
    cross = {g: sorted(sp) for g, sp in by_group_split.items() if len(sp) > 1}
    if cross:
        raise AssertionError(f"组跨集违例: {cross}")
    if any("challenge" in sp and sp != {"challenge"} for sp in by_group_split.values()):
        raise AssertionError("存在组同时落 challenge 与其他 split")

    # 断言 D：期望分集 = V2 基准（train-v2 出厂 901/2304、4/53、2/5、2/5，见
    # M2-SFX-TRAIN-V2 prepare-summary）+ Δ（R3 判定并入 train +3 样本 +7 框；
    # val/test/challenge 不变）。附 R2 出厂↔V2 基准自洽断言（R2 real train 21 中
    # vol05 组 2 样本 5 框由 V2 迁 challenge → V2 train real 19；324 synth 不变）。
    r2_boxes_by_split = Counter()
    for s in r2_samples_raw:
        r2_boxes_by_split[s["split"]] += len(s["boxes"])
    r2_real_by_split = Counter(s["split"] for s in r2_samples_raw if s["annotation_status"] != "synthetic")
    r2_vol05_train = [s for s in r2_samples_raw
                      if s["group"] == CHALLENGE_GROUP and s["split"] == "train"]
    if len(r2_vol05_train) != 2 or sum(len(s["boxes"]) for s in r2_vol05_train) != 5:
        raise AssertionError(f"R2 出厂 vol05 组 train 成员异常: {[(s['sample_id'], len(s['boxes'])) for s in r2_vol05_train]}")
    v2_baseline = {"train": (901, 2304), "val": (4, 53), "test": (2, 5), "challenge": (2, 5)}
    if (r2_real_by_split.get("train", 0) - 2 + 324 + 558 != v2_baseline["train"][0]
            or sum(1 for s in r2_samples_raw if s["annotation_status"] == "synthetic") != 324):
        raise AssertionError(f"R2 出厂↔V2 基准自洽失败: real_train={r2_real_by_split.get('train')}")
    by_split = Counter(s.split for s in all_records)
    boxes_by_split = Counter()
    for s in all_records:
        boxes_by_split[s.split] += len(s.boxes)
    expected = {"train": (v2_baseline["train"][0] + 3, v2_baseline["train"][1] + 7),
                "val": v2_baseline["val"], "test": v2_baseline["test"], "challenge": v2_baseline["challenge"]}
    for sp, (es, eb) in expected.items():
        actual = (by_split.get(sp, 0), boxes_by_split.get(sp, 0))
        if actual != (es, eb):
            raise AssertionError(f"分集 {sp} 实测 {actual} != 期望 {es}/{eb}（V2 基准+Δ）")
    if sum(by_split.values()) != 912:
        raise AssertionError(f"全量 {sum(by_split.values())} != 912")

    fingerprint = split_fingerprint(all_records, SEED)
    lock = {
        "seed": SEED,
        "method": ("group-hash-rank-v2（T1a splits.assign_splits(force=True, pinned=…) 函数参数传参）"
                   "+ R3 判定并入（BJ 正集 +3 页 +7 框）+ own-manga 六组/synthetic 钉 train + vol05 组钉 challenge"),
        "pinned_groups": dict(sorted(PINNED.items())),
        "fingerprint": fingerprint,
        "frozen_at": now_iso(),
        "challenge_group": CHALLENGE_GROUP,
        "challenge_members": moved,
        "challenge_note": (
            "challenge=densho810/vol05 组 5 框考卷不动（pre-bj17×2+pre-bj18×3，坐标逐位=R2 出厂；"
            "本组 R3 遗留单元 BJ17×2/BJ18×1 全 delete 已留痕不入考卷）；own-manga 六组与 densho810 "
            "异源异页（组名/id/页图 sha256 三层零重叠断言通过）；BJ13/14/15 挑战单列规则本集零命中。"
        ),
        "own_manga_ingest": {
            "package": str(OWN_PACKAGE), "package_sha256": own_meta["package_sha256"],
            "material_root": own_meta["material_root"], "groups": own_meta["pages_by_group"],
            "license": "source=user-own-manga（2026-10-04 用户裁决备案）",
        },
        "r3_verdicts_ref": "training_data/sfx-v1/annotate-r3/judgments/（consensus+divergence+arbiter）",
    }
    TRAIN3_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest(TRAIN3_DIR / "manifest.train-v3.json", all_records, seed=SEED, extra={"lock": lock})
    for sp in ("train", "val", "test", "challenge"):
        subset = [s for s in all_records if s.split == sp]
        write_manifest(TRAIN3_DIR / f"manifest.{sp}.json", subset, seed=SEED,
                       extra={"split": sp, "fingerprint": fingerprint})

    _state.update({
        "records": all_records, "own_ids": {s.sample_id for s in own},
        "r2_split": r2_split, "fingerprint": fingerprint, "moved": moved,
        "by_split": dict(by_split), "boxes_by_split": dict(boxes_by_split),
        "own_meta": own_meta, "own_sha": own_sha, "judge_stats": judge_stats,
        "exam_report": exam_report, "drift_count": len(drift),
        "new_pos_splits": new_pos,
    })
    print(f"[reassign] by_split={json.dumps(dict(by_split))} boxes={json.dumps(dict(boxes_by_split))}")
    print(f"[reassign] fingerprint={fingerprint}")
    return 0


# ---------------------------------------------------------------------------
# step yolo：train-v3/dataset 导出（图像复制+label 重建+R2 逐字节交叉比对+双通道）
# ---------------------------------------------------------------------------


def _yolo_stem(sample_id: str) -> str:
    return sample_id.replace("/", "__")


def _r2_tree_image(sid: str, orig_split: str) -> Path | None:
    stem = _yolo_stem(sid)
    for ext in (".png", ".jpg", ".jpeg"):
        p = R2_YOLO / "images" / orig_split / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def _resolve_r3_real_image(s: SampleRecord) -> Path:
    """pos 30 图像源：优先 R2 yolo 树（出厂分集），素材根 fallback（新 complete 3 样本）。"""
    r2_sp = _state["r2_split"].get(s.sample_id)
    if r2_sp is not None:
        src = _r2_tree_image(s.sample_id, r2_sp)
        if src is not None:
            return src
    p = Path(s.image.path)
    if not p.is_absolute() or not p.is_file():
        raise FileNotFoundError(f"{s.sample_id}: 图像不在盘（R2 yolo 树与素材根均无）{s.image.path}")
    return p


def _export_label(s: SampleRecord) -> int:
    lbl_dir = YAML_DIR / "labels" / s.split
    lbl_dir.mkdir(parents=True, exist_ok=True)
    w, h = s.image.width, s.image.height
    lines = []
    for b in s.boxes:
        if b.cls != "sfx":
            raise ValueError(f"{s.sample_id}: 非 sfx 框 cls={b.cls!r}")
        pts = []
        for x, y in b.polygon:
            nx, ny = min(max(x / w, 0.0), 1.0), min(max(y / h, 0.0), 1.0)
            pts.append(f"{nx:.6f} {ny:.6f}")
        if len(pts) < 3:
            raise ValueError(f"{s.sample_id}: 多边形点数 {len(pts)} <3")
        lines.append(f"{CLS_SFX_ID} " + " ".join(pts))
    (lbl_dir / f"{_yolo_stem(s.sample_id)}.txt").write_text(
        "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return len(lines)


def _write_dataset_yaml() -> Path:
    lines = [
        "# M2-SFX-ANNOTATE-R3 train-v3 YOLO seg dataset（training_data/sfx-v1/train-v3/dataset）",
        f"# 生成：{now_iso()} ｜ T1b-R3 AC3（R3 判定并入 BJ 正集 +3 页 +7 框 + train-v2 底册重切）",
        "# names 顺序逐字 = SFX_CLASS_MAP（src/infrastructure/providers/detection_sfx.py:137，"
        "双通道校验：脚本读回断言+pyyaml 独立解析+ultralytics 扫描冒烟）",
        "# 底册=R3 real 94（R2 82+BJ26-37 12，判定链 stage3r3）+ synthetic 324 + own-manga 558 = 912",
        "# train 904（324 合成+22 R2/R3 真实+558 own）；val 4/test 2/challenge 2 不变（考卷 5 框不动）",
        "# 多边形 = T1a 实例包络口径；cls 恒 2=sfx；seed=20261004 冻结",
        f"path: {YAML_DIR.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "challenge: images/challenge",
        "names:",
    ]
    for k in sorted(SFX_CLASS_MAP):
        lines.append(f"  {k}: {SFX_CLASS_MAP[k]}")
    yaml_path = YAML_DIR / "dataset.yaml"
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def _assert_names_channel1(yaml_path: Path) -> dict:
    parsed: dict[str, str] = {}
    in_names = False
    for line in yaml_path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^names:\s*$", line):
            in_names = True
            continue
        if in_names:
            if not line.strip():
                continue
            m = re.match(r"^  (\d+):\s*(\S+)\s*$", line)
            if m:
                parsed[m.group(1)] = m.group(2)
            else:
                in_names = False
    expected = {str(k): v for k, v in SFX_CLASS_MAP.items()}
    if parsed != expected:
        raise AssertionError(f"names 漂移：{parsed!r} != {expected!r}")
    if [int(k) for k in parsed] != sorted(SFX_CLASS_MAP):
        raise AssertionError("names 顺序漂移")
    return {"assert": "PASS", "parsed": parsed}


def _assert_names_channel2(yaml_path: Path) -> dict:
    import yaml

    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    names = raw.get("names")
    expected = {int(k): v for k, v in SFX_CLASS_MAP.items()}
    if names != expected:
        raise AssertionError(f"pyyaml names 漂移：{names!r}")
    for key in ("train", "val", "test", "challenge"):
        if not raw.get(key):
            raise AssertionError(f"pyyaml: {key} 键缺失")
    return {"assert": "PASS", "parser": f"pyyaml {yaml.__version__}"}


_ULTRA_SNIPPET = r"""
import json, sys
from pathlib import Path
from ultralytics.data.utils import check_det_dataset
yaml_path = Path(sys.argv[1]).resolve()
d = check_det_dataset(yaml_path, autodownload=False)
base = yaml_path.parent
def _count(p):
    q = Path(str(p))
    if not q.is_absolute():
        q = base / q
    return len([x for x in q.iterdir() if x.suffix.lower() in (".png", ".jpg", ".jpeg")]) if q.is_dir() else 0
out = {
    "names": {str(k): v for k, v in d["names"].items()},
    "nc": d.get("nc"),
    "dir_image_counts": {sp: _count(d.get(sp)) for sp in ("train", "val", "test", "challenge")},
}
print("__ULTRA_RESULT__" + json.dumps(out, ensure_ascii=False))
"""


def _assert_ultralytics(ultra_python: str | None, yaml_path: Path, expect_counts: dict) -> dict:
    if not ultra_python:
        return {"assert": "NOT_RUN", "note": "未提供 --ultralytics-python；如实登记"}
    proc = subprocess.run([ultra_python, "-c", _ULTRA_SNIPPET, str(yaml_path)],
                          capture_output=True, text=True, encoding="utf-8", timeout=300, cwd=str(YAML_DIR))
    if proc.returncode != 0:
        raise AssertionError(f"ultralytics 冒烟失败:\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}")
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("__ULTRA_RESULT__")), None)
    if line is None:
        raise AssertionError("ultralytics 冒烟无结果行")
    out = json.loads(line[len("__ULTRA_RESULT__"):])
    if out["names"] != {str(k): v for k, v in SFX_CLASS_MAP.items()}:
        raise AssertionError(f"ultralytics names 漂移: {out['names']}")
    if out.get("nc") != len(SFX_CLASS_MAP):
        raise AssertionError(f"ultralytics nc={out.get('nc')}")
    for sp, n in expect_counts.items():
        if out["dir_image_counts"].get(sp) != n:
            raise AssertionError(f"ultralytics 扫描: {sp} 图像数 {out['dir_image_counts'].get(sp)} != {n}")
    out["assert"] = "PASS"
    return out


def cmd_yolo(ultra_python: str | None) -> int:
    records = _state["records"]
    r2_split = _state["r2_split"]
    own_ids = _state["own_ids"]
    by_split: dict[str, list[SampleRecord]] = {}
    for s in records:
        by_split.setdefault(s.split, []).append(s)

    if YAML_DIR.exists():
        shutil.rmtree(YAML_DIR)
    stats, copied = [], {}
    sha_verified = set()
    # sha 抽验政策：BJ 正集 8 页必验 + 每 split real 子集 stem sorted 前 3 + own 每卷 1 张
    must_verify = {s.sample_id for s in records
                   if s.group.startswith("densho810/")}  # densho 全量（BJ 正集 8 页+考卷 2 页）
    for sp, subset in by_split.items():
        real = [s for s in subset if s.sample_id not in own_ids]
        for sid in sorted(s.sample_id for s in real)[:3]:
            must_verify.add(sid)
    must_verify_own = set()
    for g in OWN_GROUPS:
        grp = sorted((s for s in records if s.group == g), key=lambda x: x.sample_id)
        if grp:
            must_verify_own.add(grp[0].sample_id)

    crosscheck = {"checked": 0, "mismatch": [], "bj16_suffix_checked": False,
                  "scope": ("R2 出厂 351 中入 train-v3 的 351−0 全部（own 558 除外）与 R2 yolo 树"
                            "原分集同名 label 逐字节比对；pre-bj16 例外=R3 判定 +3 框（原 3 行"
                            "逐字节前缀+3 行新增特判）；新 complete pre-bj22/28/29 无出厂对照，"
                            "走导出后自洽校验")}
    for sp in ("train", "val", "test", "challenge"):
        subset = sorted(by_split.get(sp, []), key=lambda x: x.sample_id)
        n_boxes = 0
        for s in subset:
            if s.sample_id in own_ids:
                src = Path(s.image.path)
            else:
                src = _resolve_r3_real_image(s)
            ext = src.suffix.lower()
            dst = YAML_DIR / "images" / sp / f"{_yolo_stem(s.sample_id)}{ext}"
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists() or dst.stat().st_size != src.stat().st_size:
                shutil.copy2(src, dst)
            if dst.stat().st_size != src.stat().st_size:
                raise AssertionError(f"{s.sample_id}: 复制后大小失配")
            copied[s.sample_id] = f"images/{sp}/{dst.name}"
            n_boxes += _export_label(s)
            if s.sample_id in must_verify:
                if sha256_file(dst) != sha256_file(src) or sha256_file(dst) != s.image.sha256:
                    raise AssertionError(f"{s.sample_id}: sha256 三方校验失败")
                sha_verified.add(s.sample_id)
            if s.sample_id in must_verify_own:
                if sha256_file(dst) != sha256_file(src) or sha256_file(dst) != s.image.sha256:
                    raise AssertionError(f"{s.sample_id}: own sha256 三方校验失败")
                sha_verified.add(s.sample_id)
            # R2 出厂 label 交叉比对（own 除外；pre-bj16 特判）
            if s.sample_id in r2_split:
                r2_lbl = R2_YOLO / "labels" / r2_split[s.sample_id] / f"{_yolo_stem(s.sample_id)}.txt"
                new_lbl = YAML_DIR / "labels" / sp / f"{_yolo_stem(s.sample_id)}.txt"
                if not r2_lbl.is_file():
                    raise AssertionError(f"{s.sample_id}: R2 树无对照 label {r2_lbl}")
                crosscheck["checked"] += 1
                if s.sample_id == "pre-bj16":
                    old = r2_lbl.read_text(encoding="utf-8").splitlines()
                    new = new_lbl.read_text(encoding="utf-8").splitlines()
                    if new[:len(old)] != old or len(new) != len(old) + 3:
                        raise AssertionError(f"pre-bj16 label 特判失败: 原 {len(old)} 行 新 {len(new)} 行")
                    crosscheck["bj16_suffix_checked"] = True
                elif r2_lbl.read_bytes() != new_lbl.read_bytes():
                    crosscheck["mismatch"].append(s.sample_id)
    if crosscheck["mismatch"]:
        raise AssertionError(f"label 交叉比对失配: {crosscheck['mismatch'][:10]}")
    if not crosscheck["bj16_suffix_checked"]:
        raise AssertionError("pre-bj16 label 特判未执行")
    real_verified = sha_verified - must_verify_own
    if len(real_verified) != len(must_verify):
        raise AssertionError(f"sha 抽验覆盖不全: real {len(real_verified)}/{len(must_verify)}")
    own_verified = sha_verified & must_verify_own
    if len(own_verified) != len(must_verify_own):
        raise AssertionError(f"own 抽验覆盖不全: {len(own_verified)}/{len(must_verify_own)}")

    yaml_path = _write_dataset_yaml()
    names_check = {"channel1_readback": _assert_names_channel1(yaml_path),
                   "channel2_pyyaml": _assert_names_channel2(yaml_path)}
    ultra_check = _assert_ultralytics(ultra_python, yaml_path,
                                      {sp: st for sp, st in _state["by_split"].items()})

    stem_mismatch_total = 0
    for sp in ("train", "val", "test", "challenge"):
        lbls = sorted((YAML_DIR / "labels" / sp).glob("*.txt"))
        imgs = sorted(p for p in (YAML_DIR / "images" / sp).iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
        if len(lbls) != len(imgs) or len(lbls) != _state["by_split"][sp]:
            raise AssertionError(f"{sp}: images/labels 数不一致")
        mismatch = sorted({p.stem for p in lbls} ^ {p.stem for p in imgs})
        stem_mismatch_total += len(mismatch)
        if mismatch:
            raise AssertionError(f"{sp}: stem 失配 {mismatch[:5]}")
        n_lines = 0
        for lf in lbls:
            for ln in lf.read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                parts = ln.split()
                if parts[0] != str(CLS_SFX_ID):
                    raise AssertionError(f"{lf.name}: cls 漂移")
                vals = [float(v) for v in parts[1:]]
                if len(vals) < 6 or len(vals) % 2 or any(v < 0.0 or v > 1.0 for v in vals):
                    raise AssertionError(f"{lf.name}: 坐标非法")
                n_lines += 1
        if n_lines != _state["boxes_by_split"][sp]:
            raise AssertionError(f"{sp}: label 行数 {n_lines} != manifest 框数 {_state['boxes_by_split'][sp]}")

    print(f"[yolo] splits={json.dumps([{'split': sp, 'images': _state['by_split'][sp],
          'boxes': _state['boxes_by_split'][sp]} for sp in ('train','val','test','challenge')])}")
    print(f"[yolo] names 双通道 PASS + ultralytics={ultra_check.get('assert')} "
          f"dir_counts={ultra_check.get('dir_image_counts')}")
    print(f"[yolo] label 交叉比对 checked={crosscheck['checked']} mismatch=0 bj16_suffix=True; "
          f"sha 抽验 {len(sha_verified)} 张（densho 全量+每 split 前 3+own 每卷 1）")
    (YAML_DIR / "_export_stats.json").write_text(json.dumps({
        "generated_at_utc": now_iso(), "seed": SEED, "fingerprint": _state["fingerprint"],
        "splits": [{"split": sp, "images": _state["by_split"][sp], "boxes": _state["boxes_by_split"][sp]}
                   for sp in ("train", "val", "test", "challenge")],
        "names_check": names_check, "ultralytics_scan": ultra_check,
        "label_crosscheck_vs_r2": {**crosscheck, "assert": "PASS"},
        "sha256_spot_check": {"verified": sorted(sha_verified),
                              "policy": "densho810 全量（BJ 正集 8+考卷 2）+每 split real 前 3+own 每卷 1；三方一致"},
        "stem_mismatch_total": stem_mismatch_total, "copied_images": copied,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    _state["yolo_meta"] = {"names_check": names_check, "ultra_check": ultra_check,
                           "crosscheck": crosscheck, "sha_verified": sorted(sha_verified),
                           "stem_mismatch_total": stem_mismatch_total}
    return 0


# ---------------------------------------------------------------------------
# step summary：train-v3/export-summary + verification stage-r3-summary
# ---------------------------------------------------------------------------


def cmd_summary() -> int:
    container, records = load_manifest(TRAIN3_DIR / "manifest.train-v3.json")
    lock = container.get("lock") or {}
    judge_stats = _state["judge_stats"]
    r3_man = _read_json(R3_MANIFEST)
    r3_samples = r3_man["samples"] if isinstance(r3_man, dict) else r3_man
    bj_new = _read_json(R3_BJ_NEW_JSON)

    by_split: dict[str, list[SampleRecord]] = {}
    for s in records:
        by_split.setdefault(s.split, []).append(s)

    def split_detail(sp: str) -> dict:
        subset = by_split.get(sp, [])
        return {"samples": len(subset), "boxes": sum(len(s.boxes) for s in subset),
                "real": sum(1 for s in subset if s.annotation_status == "complete"),
                "partial": sum(1 for s in subset if s.annotation_status == "partial"),
                "pseudo": sum(1 for s in subset if s.annotation_status == "pseudo"),
                "synthetic": sum(1 for s in subset if s.annotation_status == "synthetic"),
                "groups": sorted({s.group for s in subset}),
                "images": len({s.image.sha256 for s in subset})}

    # BJ 正集前后对照（合同 AC3：R2 5 页 11 框→R3 实测）
    bj_complete = [m for m in r3_samples if m["annotation_status"] == "complete"
                   and m["provenance"].get("review_domain") == "bj"]
    bj_detail = [{"sample_id": m["sample_id"], "case_id": m["provenance"]["case_id"],
                  "group": m["group"], "boxes": len(m["boxes"]),
                  "split": next(s.split for s in records if s.sample_id == m["sample_id"]),
                  "units_kept": [b.get("unit_id") for b in (m["provenance"].get("boxes_meta") or [])
                                 if b.get("verdict") in KEEP_VERDICTS]}
                 for m in sorted(bj_complete, key=lambda x: x["sample_id"])]
    bj_train = [d for d in bj_detail if d["split"] == "train"]
    bj_challenge = [d for d in bj_detail if d["split"] == "challenge"]

    morph = {
        "pre-bj16": "斜向粗毛笔片假名（シャ/ゴ类）+R3 回填 3 框（R2-BJ16-B04/05/06 consensus confirm）",
        "pre-bj22": "手术室潦草拟声（R2-BJ22-B00 consensus confirm + R2-BJ22-B01 arbiter correct）",
        "pre-bj28": "竖排字块（R3-BJ28-B00 consensus confirm）",
        "pre-bj29": "竖排拟声（R3-BJ29-B00 consensus confirm）",
        "pre-bj17": "竖排毛笔假名（考卷不动）",
        "pre-bj18": "竖排/斜置粗毛笔片假名（考卷不动）",
    }
    for d in bj_detail:
        d["morphology"] = morph.get(d["sample_id"], "—")

    yolo_meta = _state["yolo_meta"]
    own_meta = _state["own_meta"]

    summary = {
        "task": "M2-SFX-ANNOTATE-R3 stage-2（AC2 后半判定并入+仲裁 / AC3 manifest.r3+train-v3 重建）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-ANNOTATE-R3/stage2_finalize_r3.py --step all",
        "mode": "ai-review-backfill（codex+agy 共识 19+分歧仲裁 3；human_review=false，不谎称人工）",
        "r3_judgments": {
            "units_total": judge_stats["units_total"],
            "units_by_part": judge_stats["units_by_part"],
            "consensus_units": judge_stats["consensus"],
            "arbitrated_units": judge_stats["divergence_arbitrated"],
            "final_verdict_dist": judge_stats["verdict_dist"],
            "reviewer_dist": judge_stats["reviewer_dist"],
            "arbiter_note": "仲裁=编排会话逐图实看终裁（预览+原页上下文；rationale 全文在 judgments/arbiter/batch-1.json）",
        },
        "manifest_merge": {
            "r2_base": "annotate-r2/preannotate/manifest.r2.json（82 样本，只读；R2 判定链 stage2r2 未覆盖）",
            "base_manifest_caliber_note": (
                "ask 字面「R2 final manifest 82 样本」与文件事实不符：R2 final/manifest.r2.json 实为 "
                "351 样本（27 complete+324 synthetic）；82 样本底册本体=preannotate/manifest.r2.json"
                "（27 complete+55 pseudo）。遗留 16 单元判定更新对象 pre-bj19/20/21/22 pseudo 页只在该"
                "82 底册，且 R2 stage2r2 语义的底册正是此文件——按 preanimate 82 底册执行，此处如实登记。"),
            "r3_bj_new": "annotate-r3/preannotate/manifest-bj-new.json（BJ26-37 12 样本）",
            "r3_merged": "annotate-r3/preannotate/manifest.r3.json",
            "samples_total": len(r3_samples),
            "stage3r3_actions": dict(Counter((m["provenance"].get("stage3r3") or {}).get("action", "—") for m in r3_samples)),
        },
        "bj_positive": {
            "r2_then": {"pages": 5, "boxes": 11,
                        "detail": "BJ16×3+BJ17×2+BJ18×3+BJ23×2+BJ24×1（train 6 框+challenge 考卷 5 框）"},
            "r3_now": {"pages": len(bj_detail), "boxes": sum(d["boxes"] for d in bj_detail),
                       "train_pages": len(bj_train), "train_boxes": sum(d["boxes"] for d in bj_train),
                       "challenge_boxes": sum(d["boxes"] for d in bj_challenge),
                       "detail": bj_detail,
                       "delta": "+3 页 +7 框（pre-bj16 +3 回填、pre-bj22 +2 新 complete、pre-bj28/29 +1×2）；考卷 5 框不动"},
        },
        "train_v3": {
            "seed": lock.get("seed"), "method": lock.get("method"),
            "pinned_groups": lock.get("pinned_groups"),
            "fingerprint": lock.get("fingerprint"),
            "by_split": {sp: split_detail(sp) for sp in ("train", "val", "test", "challenge")},
            "vs_v2_baseline": {
                "v2_train": {"samples": 901, "boxes": 2304},
                "v3_train": {"samples": _state["by_split"]["train"], "boxes": _state["boxes_by_split"]["train"]},
                "delta": "+3 样本 +7 框（R3 判定并入）；val/test/challenge 不变",
                "zero_drift_vs_r2_factory": _state["drift_count"] == 0,
            },
            "group_isolation_violations": 0,
            "exam_dossier": {
                "group": CHALLENGE_GROUP, "samples": 2, "boxes": 5,
                "unchanged_assert": "PASS（框数+坐标逐位=R2 出厂）",
                "r3_deleted_leftover_units": _state["exam_report"],
            },
            "exam_zero_overlap": "组名/id/页图 sha256 三层零交集断言 PASS（own 558 vs pos 30 全量比对）",
            "yolo": {
                "root": "training_data/sfx-v1/train-v3/dataset",
                "names_dual_channel_check": yolo_meta["names_check"],
                "ultralytics_scan": yolo_meta["ultra_check"],
                "label_crosscheck_vs_r2": yolo_meta["crosscheck"],
                "sha256_spot_check": {"verified_count": len(yolo_meta["sha_verified"])},
                "stem_mismatch_total": yolo_meta["stem_mismatch_total"],
            },
            "own_manga_ingest": {"package": str(OWN_PACKAGE), **own_meta,
                                 "license": "source=user-own-manga（2026-10-04 用户裁决备案）"},
        },
        "artifacts": {},
        "honest_notes": [
            "BJ26-37 六页（BJ32-37，AC1 目检确认含毛笔竖排 SFX）chiqui7 零候选：保持 pseudo 零框负证据，"
            "SFX 标注留 miss 补画通道（chiqui7 BJ 盲区实证三连：R2 conf 天然低→R3 密度全≤1→毛笔页零检出）",
            "BJ19/20/21 遗留候选全 delete→空框 pseudo 负证据留痕（R3 扩审关闭该三页的低置信候选）",
            "R2-BJ22-B01 correct：框保留原坐标+revision 留痕（R2 stage2r2 correct 口径），重框参考区域在 revision.fix_hint_xyxy_page",
            "底册口径差异如实登记（manifest_merge.base_manifest_caliber_note）：ask「final 82」实为 preanimate 82/final 351",
            "own-manga 框坐标=chiqui7 模型输出未手工收紧（V2 边界沿袭）；partial 140/pseudo 418 分级如实",
            "pre-bj16 label 与 R2 出厂比对走特判（原 3 行逐字节前缀一致+3 行新增）；其余 R2 出厂 348 入集样本逐字节一致",
            "challenge 考卷页的 R3 遗留单元（BJ17×2/BJ18×1）全 delete 已留痕：考卷内容零改动",
        ],
    }
    for rel in ["training_data/sfx-v1/annotate-r3/preannotate/manifest.r3.json",
                "training_data/sfx-v1/train-v3/manifest.train-v3.json",
                "training_data/sfx-v1/train-v3/dataset/dataset.yaml",
                "training_data/sfx-v1/train-v3/dataset/_export_stats.json"]:
        p = REPO_ROOT / rel
        summary["artifacts"][rel] = sha256_file(p) if p.is_file() else None

    atomic_write_json(SUMMARY_JSON, summary)
    git_summary = json.loads(json.dumps(summary))
    git_summary["data_root_gitignored"] = (
        "training_data/sfx-v1/{annotate-r3,train-v3}/（repo gitignored）；R2/R1 树在本 worktree 外只读；"
        "own-manga 入册包在 task-envs 外部树只读")
    git_summary["yolo_layout"] = {
        "images": "training_data/sfx-v1/train-v3/dataset/images/{train,val,test,challenge}/",
        "labels": "training_data/sfx-v1/train-v3/dataset/labels/{train,val,test,challenge}/（YOLO seg 归一化多边形，cls=2）",
        "stem_rule": "sample_id 中 '/' 替换为 '__'",
    }
    atomic_write_json(GIT_SUMMARY, git_summary)
    print(f"[summary] wrote {SUMMARY_JSON}")
    print(f"[summary] wrote {GIT_SUMMARY}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True, choices=["manifest", "reassign", "yolo", "summary", "all"])
    parser.add_argument("--ultralytics-python", default=str(TRAIN_VENV_DEFAULT))
    args = parser.parse_args()
    if not Path(args.ultralytics_python).is_file():
        args.ultralytics_python = None
    if args.step in ("yolo", "summary") and "records" not in _state:
        cmd_reassign()  # 单步运行先重建内存态（reassign 幂等，重复执行无副作用破坏）
    if args.step == "summary" and "yolo_meta" not in _state:
        cmd_yolo(args.ultralytics_python)  # summary 依赖 yolo 统计（yolo 幂等，重导出前清树）
    steps = [args.step] if args.step != "all" else ["manifest", "reassign", "yolo", "summary"]
    for s in steps:
        rc = {"manifest": cmd_manifest, "reassign": cmd_reassign,
              "yolo": lambda: cmd_yolo(args.ultralytics_python), "summary": cmd_summary}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
