"""M2-SFX-ANNOTATE-R2 阶段二收尾（Task 合同 AC5）：R2 判定并入 + 三集扩集重导出。

沿 R1 stage2_finalize.py 复制适配（T1b-R2 合同：重跑 split/yolo/summary，组隔离
seed 冻结沿 R1 口径，names 硬约束双通道校验）。与 R1 的差异：

- 判定源 = R2 judgments（units.json 19 单元：①AC2 BJ 低置信层=0 如实空集+
  ②AC3 回放 6 单元+③AC4 BJ16-25 新页 13 单元；consensus 18+divergence 1→arbiter）。
- 底册 = R1 manifest（72 样本 450 框，含 R1 判定链 provenance.stage2；R1 底册
  本身只读不改）+ R2 BJ 新页 manifest-bj-new.json（10 样本 29 框）→
  preannotate/manifest.r2.json（82 样本）。
- R1 样本更新语义同构 R1 stage2（provenance.stage2r2，不覆盖 R1 的 stage2 判定
  链）：confirm 保持并升级 complete（全框判定完时）/correct 走 revision 链留痕/
  delete 排除留痕；本轮 R1 侧判定仅回放页 6 单元全 delete——回放页仍保持 pseudo
  不入训练集（R1 合同），delete 框从框列表排除并在 stage2r2 留痕。
- BJ16-25 新页样本按其判定新增：confirm 框→complete 样本（正集 GT 只含判定
  保留框；conf<0.2 未入本轮判定范围的候选框不入 GT 并留痕）；全框 delete→空框
  pseudo 负证据；无判定单元页保持 pseudo 原样。
- human_review=false 保真（AI 代审，不谎称人工）。
- 三集：T1a assign_splits 组隔离（组不跨集+challenge=BJ13/14/15 单列+
  seed=20261004 冻结）+ synthetic 324 pinned train（读 R1 synthetic/manifest.json
  并入，不入 test）。BJ13 本轮无新判定（判定仍=R1 的 delete，未翻案）→
  challenge 空集如实登记（AC5 验收判据允许分支）。
- YOLO：names 逐字=SFX_CLASS_MAP 双通道校验（①脚本写后读回断言；②pyyaml
  独立解析复核）；labels cls 恒 2、坐标∈[0,1]、images/labels stem 0 失配。

纪律：零 src 修改（生产 SFX_CLASS_MAP 经 sys.path 只读 import）；素材树与 R1
数据树只读；T1a 工具链（schema/atomicio/splits/TrainingSetBuilder）只读复用。
数据本体落 training_data/sfx-v1/annotate-r2/（gitignored），Git 只进摘要。

步骤（--step）：manifest → split → yolo → summary（all 依序全跑）。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
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

# 生产类表只读 import（零 src：不改动，仅读取常量）。
# 来源 src/infrastructure/providers/detection_sfx.py:137
#   SFX_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
from infrastructure.providers.detection_sfx import SFX_CLASS_MAP  # noqa: E402

R1_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R1-zcode")
R1_ANNOTATE = R1_WORKTREE / "training_data" / "sfx-v1" / "annotate-r1"

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r2"
JUDG_DIR = OUT_DIR / "judgments"
R1_MANIFEST = R1_ANNOTATE / "preannotate" / "manifest.json"  # R1 底册（只读）
R2_BJ_NEW_JSON = OUT_DIR / "preannotate" / "manifest-bj-new.json"  # R2 新页底册
R2_MANIFEST = OUT_DIR / "preannotate" / "manifest.r2.json"  # R2 合成底册（本轮产物）
SYNTH_MANIFEST = R1_ANNOTATE / "synthetic" / "manifest.json"  # R1 合成（只读并入）
SYNTH_IMG_ROOT = R1_ANNOTATE  # 合成 image.path 相对基准（R1 目录布局）
FINAL_DIR = OUT_DIR / "final"
YAML_DIR = FINAL_DIR / "yolo"
SUMMARY_JSON = FINAL_DIR / "export-summary.json"
GIT_SUMMARY = REPO_ROOT / "verification" / "M2-SFX-ANNOTATE-R2" / "stage-r2-final-summary.json"

SEED = SEED_DEFAULT  # 20261004（沿 T1a splits.SEED_DEFAULT，seed 冻结沿 R1 口径）
SYNTH_GROUP = "synthetic/annotate-r1"
PINNED_GROUPS = {SYNTH_GROUP: "train"}
REVIEWER_CONSENSUS = "codex+agy-consensus"
REVIEWER_ARBITER = "arbiter"
KEEP_VERDICTS = ("confirm", "correct")
# 域内回放 5 页（R1 合同 AC2 selection.replay）：保持 pseudo 不入训练集（R1 口径沿袭）
REPLAY_CASE_IDS = ("BJ06", "J38", "J41", "J43", "J51")
JUDG_SOURCES = ["judgments/consensus.json", "judgments/divergence.json",
                "judgments/arbiter/batch-*.json"]


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 判定装载：R2 consensus + arbiter → unit_id → {verdict, reviewer, rationale}
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
            # 双评审共识：双方 rationale 全文保留（裁决依据不丢失）
            "rationale": f"codex: {c['rationale_codex']} ｜ agy: {c['rationale_agy']}",
        }
    arb_by_id = {j["id"]: j for j in arb}
    n_arb_used = 0
    for d in div:
        j = arb_by_id.get(d["id"])
        if j is None:
            raise ValueError(f"divergence 单元 {d['id']} 无对应仲裁判定（arbiter/batch-*.json）")
        vmap[d["id"]] = {
            "verdict": j["verdict"],
            "reviewer": REVIEWER_ARBITER,
            "rationale": j["rationale"],
        }
        n_arb_used += 1
    unused_arb = sorted(set(arb_by_id) - {d["id"] for d in div})
    if unused_arb:
        raise ValueError(f"仲裁判定含 divergence 之外的单元: {unused_arb}")

    units = _read_json(JUDG_DIR / "units.json")["units"]
    covered = {u["id"] for u in units}
    if set(vmap) != covered:
        raise ValueError(
            f"判定覆盖不一致：units 有而 vmap 无 {sorted(covered - set(vmap))}；"
            f"vmap 有而 units 无 {sorted(set(vmap) - covered)}"
        )
    stats = {
        "units_total": len(units),
        "units_by_part": dict(Counter(u["part"] for u in units)),
        "consensus": len(cons),
        "divergence_arbitrated": n_arb_used,
        "verdict_dist": dict(Counter(v["verdict"] for v in vmap.values())),
        "reviewer_dist": dict(Counter(v["reviewer"] for v in vmap.values())),
    }
    return vmap, stats


# ---------------------------------------------------------------------------
# manifest：R2 判定并入 → preannotate/manifest.r2.json（R1 底册 72 + BJ 新页 10）
# ---------------------------------------------------------------------------


def _units_for_sample(m: dict, rnd: str) -> list[str]:
    """样本框列表 → 单元 id 列表（R1/R2 命名同构：{RND}-{CASE}-B{nn}）。"""
    prov = m["provenance"]
    if prov["type"] == "asset_case":
        prefix = f"{rnd}-{prov['case_id']}-"
    elif prov["type"] == "external_model":
        prefix = f"{rnd}-OGK-{prov['region_key']}-"
    else:
        return []
    return [f"{prefix}B{i:02d}" for i in range(len(m["boxes"]))]


def _apply_r2_verdicts_to_r1_sample(m: dict, vmap: dict[str, dict]) -> bool:
    """R1 底册样本：把本轮（R2）获得的判定并入，写 provenance.stage2r2。

    本轮 R1 侧判定单元仅回放页 6 单元（全 delete）。语义：回放页样本保持 pseudo
    不入训练集（R1 合同沿袭）；delete 框从框列表排除并在 stage2r2 留痕。
    无本轮判定的样本原样返回（不写 stage2r2，R1 判定链 provenance.stage2 保留）。
    """
    prov = m["provenance"]
    uids = _units_for_sample(m, "R1")
    if not uids:
        return False
    verdicts = [vmap.get(uid) for uid in uids]
    judged = [(i, v) for i, v in enumerate(verdicts) if v is not None]
    if not judged:
        return False

    del_idx = [i for i, v in judged if v["verdict"] == "delete"]
    keep_idx = [i for i, v in judged if v["verdict"] in KEEP_VERDICTS]
    if keep_idx:
        raise ValueError(
            f"{m['sample_id']}: R2 对 R1 样本出现 confirm/correct（{[uids[i] for i in keep_idx]}）——"
            "本脚本按合同范围仅预期回放页 delete；如范围变化需先扩合同再改此处"
        )

    # delete 框排除留痕（boxes/boxes_meta 索引同步对齐）
    meta = prov.get("boxes_meta") or [{}] * len(m["boxes"])
    new_boxes, new_meta, excluded = [], [], []
    for i, (b, bm) in enumerate(zip(m["boxes"], meta)):
        if i in del_idx:
            v = verdicts[i]
            excluded.append({"unit_id": uids[i], "verdict": "delete",
                             "reviewer": v["reviewer"], "rationale": v["rationale"]})
            continue
        new_boxes.append(dict(b))
        new_meta.append(dict(bm))
    m["boxes"] = new_boxes
    if prov.get("boxes_meta") is not None:
        prov["boxes_meta"] = new_meta

    prov["stage2r2"] = {
        "action": "kept_pseudo_replay_page_delete_excluded",
        "note": ("域内回放页（R1 合同 AC2 域内回放 5 页之一）：保持 pseudo 不入训练集"
                 "（R1 口径沿袭）；本轮 R2 扩审对其单元新判 delete，该框已从框列表排除"
                 "并在此留痕；R1 判定链见 provenance.stage2（未改动）"),
        "mode": "ai-review-backfill",
        "judgments_sources": JUDG_SOURCES,
        "reviewed_units": len(judged),
        "excluded_delete_units": excluded,
        "human_review": False,
    }
    return True


def _apply_r2_verdicts_to_bj_new(m: dict, vmap: dict[str, dict]) -> None:
    """R2 BJ 新页样本：confirm 框→complete 样本；全 delete→空框负证据；无判定→原样。"""
    prov = m["provenance"]
    uids = _units_for_sample(m, "R2")
    verdicts = [vmap.get(uid) for uid in uids]
    judged = [(i, v) for i, v in enumerate(verdicts) if v is not None]
    meta = prov.get("boxes_meta") or [{}] * len(m["boxes"])

    if not judged:
        prov["stage2r2"] = {
            "action": "kept_pseudo_no_judged_units_this_round",
            "note": ("本页候选框全部 conf<0.2 未入本轮判定范围（R2 单元口径=conf≥0.2，"
                     "见 judgments/units.json 与 worksheet/worksheet-bj-new.json 留痕）；"
                     "样本保持 pseudo 原样，候选框留给后续扩标轮"),
            "human_review": False,
        }
        return

    keep_idx = [i for i, v in judged if v["verdict"] in KEEP_VERDICTS]
    del_idx = [i for i, v in judged if v["verdict"] == "delete"]
    unj_idx = [i for i, v in enumerate(verdicts) if v is None]

    if not keep_idx:
        # 全判定且无保留：空框 pseudo 负证据（T1a schema 允许 pseudo 空框）
        if unj_idx:
            raise ValueError(f"{m['sample_id']}: 无保留判定但存在未判定框，处置歧义")
        excluded = [{"unit_id": uids[i], "verdict": "delete",
                     "reviewer": verdicts[i]["reviewer"],
                     "rationale": verdicts[i]["rationale"]} for i in del_idx]
        m["boxes"] = []
        if prov.get("boxes_meta") is not None:
            prov["boxes_meta"] = []
        prov["stage2r2"] = {
            "action": "kept_pseudo_zero_box_negative_evidence",
            "note": ("本轮判定无 confirm/correct（唯一候选框判 delete）：样本保持 pseudo"
                     "空框负证据；delete 框已从框列表排除并在此留痕"),
            "mode": "ai-review-backfill",
            "judgments_sources": JUDG_SOURCES,
            "reviewed_units": len(judged),
            "kept_units": 0,
            "excluded_delete_boxes": excluded,
            "human_review": False,
        }
        return

    # 正集样本：boxes 只留判定保留框；boxes_meta 同步对齐（T1a 索引对齐约束）
    new_boxes, new_meta, excluded, unjudged, corrections = [], [], [], [], []
    for i, (b, bm) in enumerate(zip(m["boxes"], meta)):
        uid = uids[i]
        v = verdicts[i]
        if v is None:
            unjudged.append({"unit_id": uid, "conf": (bm or {}).get("conf"),
                             "note": "conf<0.2 未入本轮判定范围，不入正集 GT（候选留后续扩标）"})
            continue
        if v["verdict"] == "delete":
            excluded.append({"unit_id": uid, "verdict": "delete", "reviewer": v["reviewer"],
                             "rationale": v["rationale"]})
            continue
        nb = dict(b)
        nbm = dict(bm)
        nbm["unit_id"] = uid
        nbm["verdict"] = v["verdict"]
        nbm["reviewer"] = v["reviewer"]
        nbm["rationale"] = v["rationale"]
        if v["verdict"] == "correct":
            nb["occluded"] = bool(nb.get("occluded", False))
            nbm["revision"] = {
                "type": "correction_note",
                "needs_fix": True,
                "note": v["rationale"],
                "reviewer": v["reviewer"],
                "coordinates_changed": False,
            }
            corrections.append({"unit_id": uid, "note": v["rationale"]})
        new_boxes.append(nb)
        new_meta.append(nbm)

    m["boxes"] = new_boxes
    if prov.get("boxes_meta") is not None:
        prov["boxes_meta"] = new_meta
    m["annotation_status"] = "complete"
    prov["stage"] = "annotate-r2-stage2"
    prov["quality_note"] = (
        "AI 代审正集样本（R2 扩标轮 2026-10-04）：boxes=本轮判定保留框"
        "（codex+agy 共识 + 分歧仲裁），provenance.stage2r2 留判定链；human_review=false，"
        "不谎称人工；conf<0.2 未判定候选框不入正集 GT（见 stage2r2.unjudged_boxes）"
    )
    prov["stage2r2"] = {
        "action": "completed",
        "mode": "ai-review-backfill",
        "judgments_sources": JUDG_SOURCES,
        "reviewed_units": len(judged),
        "kept_units": len(new_boxes),
        "excluded_delete_boxes": excluded,
        "unjudged_boxes": unjudged,
        "correction_notes": corrections,
        "human_review": False,
    }


def cmd_manifest() -> int:
    vmap, _stats = load_final_verdicts()
    r1_man = _read_json(R1_MANIFEST)
    bj_new = _read_json(R2_BJ_NEW_JSON)

    # 底册合流前守卫：sample_id 无冲突（R1 pre-* 与 R2 pre-bj16-25）
    r1_ids = [m["sample_id"] for m in r1_man]
    bj_ids = [m["sample_id"] for m in bj_new]
    dup = sorted(set(r1_ids) & set(bj_ids))
    if dup:
        raise ValueError(f"sample_id 冲突: {dup}")

    n_r1_touched = 0
    for m in r1_man:
        if _apply_r2_verdicts_to_r1_sample(m, vmap):
            n_r1_touched += 1

    n_bj_completed = 0
    for m in bj_new:
        before = m["annotation_status"]
        _apply_r2_verdicts_to_bj_new(m, vmap)
        if m["annotation_status"] != before:
            n_bj_completed += 1

    man = r1_man + bj_new

    # 全量 schema 校验 + boxes/boxes_meta 索引对齐校验（T1a schema 工具，逐样本）
    for m in man:
        rec = SampleRecord.from_dict(m)
        errors = rec.validate()
        if errors:
            raise ValueError(f"{m['sample_id']}: {errors}")
        prov = m["provenance"]
        if prov["type"] == "asset_case" and prov.get("boxes_meta") is not None:
            if len(prov["boxes_meta"]) != len(m["boxes"]):
                raise ValueError(f"{m['sample_id']}: boxes_meta 与 boxes 索引失配")
        for key in ("stage2", "stage2r2"):
            st = (prov.get(key) or {}).get("action")
            if st == "completed" and not m["boxes"]:
                raise ValueError(f"{m['sample_id']}: {key}=completed 样本不允许空框")

    atomic_write_json(R2_MANIFEST, man)
    print(f"[manifest] samples={len(man)} (r1={len(r1_man)} + bj_new={len(bj_new)})")
    print(f"[manifest] r1_touched={n_r1_touched} bj_new_to_complete={n_bj_completed}")
    acts = Counter((m["provenance"].get("stage2r2") or {}).get("action", "—") for m in man)
    print(f"[manifest] stage2r2 actions: {json.dumps(dict(acts), ensure_ascii=False)}")
    return 0


# ---------------------------------------------------------------------------
# split：T1a 拆分器组隔离 + R1 合成并入（pinned train）
# ---------------------------------------------------------------------------


def _load_pos_samples() -> list[SampleRecord]:
    """正集 = annotation_status == 'complete'（合并底册统一口径：R1 底册 KO 22 样本
    的 complete 由 R1 写入（判定链 provenance.stage2），R2 新页 5 样本由本轮写入
    （判定链 provenance.stage2r2）——正集判定不看单一轮次键，看 schema 状态字段）。"""
    man = _read_json(R2_MANIFEST)
    return [SampleRecord.from_dict(m) for m in man if m["annotation_status"] == "complete"]


def _load_synth_samples() -> list[SampleRecord]:
    raw = _read_json(SYNTH_MANIFEST)
    return [SampleRecord.from_dict(d) for d in raw]


def cmd_split() -> int:
    pos = _load_pos_samples()
    synth = _load_synth_samples()
    if not synth:
        raise ValueError("synthetic manifest 为空：并入无从执行")
    all_samples = pos + synth

    group_split = assign_splits(all_samples, seed=SEED, force=True, pinned=PINNED_GROUPS)
    fingerprint = split_fingerprint(all_samples, SEED)
    by_split = Counter(s.split for s in all_samples)

    # 校验：合成全落 train（AC5 沿 R1：不入 test）
    synth_splits = Counter(s.split for s in synth)
    if set(synth_splits) - {"train"}:
        raise ValueError(f"合成样本落入非 train split: {dict(synth_splits)}")
    # 校验：真实页组不跨集（pinned 组整组单侧，同样天然不跨集；一并纳入断言）
    by_group_split: dict[str, set[str]] = {}
    for s in all_samples:
        by_group_split.setdefault(s.group, set()).add(s.split)
    cross = {g: sp for g, sp in by_group_split.items() if len(sp) > 1}
    if cross:
        raise ValueError(f"组跨集违例: {cross}")
    # 校验：挑战集单列语义——pos 中 BJ13/14/15 必须全在 challenge
    for s in pos:
        if s.provenance.get("case_id") in CHALLENGE_CASE_IDS and s.split != "challenge":
            raise ValueError(f"{s.sample_id}: 挑战集 case 未单列")

    lock = {
        "seed": SEED,
        "method": "group-hash-rank-v2（T1a splits.assign_splits）",
        "pinned_groups": dict(PINNED_GROUPS),
        "fingerprint": fingerprint,
        "frozen_at": now_iso(),
        "challenge_single_bucket": sorted(CHALLENGE_CASE_IDS),
        "challenge_note": (
            "R2 轮正集仍无 BJ13/14/15 complete 样本：本轮判定范围（judgments/units.json "
            "19 单元）不含 BJ13/14/15 任何单元（AC2 BJ conf 0.2-0.5 层经 units.json 核对"
            "为空集；BJ13 唯一 conf≥0.5 判定=R1 的 delete，本轮无新判定未翻案），"
            "故 challenge split 空集如实登记（AC5 验收判据允许分支：BJ13 判定仍=delete 时"
            "如实登记并交编排裁决）；BJ13/14/15 页级样本保持 pseudo 留待扩标。"
            "挑战集正框补齐后重跑 split+yolo 即自动单列。"
        ),
    }
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest(FINAL_DIR / "manifest.r2.json", all_samples, seed=SEED, extra={"lock": lock})

    for sp in ("train", "val", "test", "challenge"):
        subset = [s for s in all_samples if s.split == sp]
        write_manifest(
            FINAL_DIR / f"manifest.{sp}.json",
            subset,
            seed=SEED,
            extra={"split": sp,
                   "fingerprint": fingerprint,
                   **({"note": "空集（见 manifest.r2.json lock.challenge_note）"} if not subset else {})},
        )
    print(f"[split] pos={len(pos)} synth={len(synth)} by_split={json.dumps(dict(by_split), ensure_ascii=False)}")
    print(f"[split] fingerprint={fingerprint}")
    return 0


# ---------------------------------------------------------------------------
# yolo：YOLO seg 导出（train/val 经 TrainingSetBuilder；test/challenge 独立路径）
# ---------------------------------------------------------------------------

CLS_SFX_ID = next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx")


def _yolo_stem(sample_id: str) -> str:
    return sample_id.replace("/", "__")


def _resolve_image_path(s: SampleRecord) -> Path:
    p = Path(s.image.path)
    if p.is_absolute():
        return p
    # 相对路径两种基准：合成样本相对 R1 annotate-r1 目录；其余相对 R2 OUT_DIR
    if s.annotation_status == "synthetic":
        return SYNTH_IMG_ROOT / p
    return OUT_DIR / p


def _export_split(samples: list[SampleRecord], split: str, copied: dict[str, str]) -> dict:
    img_dir = YAML_DIR / "images" / split
    lbl_dir = YAML_DIR / "labels" / split
    img_dir.mkdir(parents=True, exist_ok=True)
    lbl_dir.mkdir(parents=True, exist_ok=True)
    n_boxes = 0
    for s in samples:
        stem = _yolo_stem(s.sample_id)
        src = _resolve_image_path(s)
        if not src.is_file():
            raise FileNotFoundError(f"{s.sample_id}: 图像不在盘 {src}")
        ext = src.suffix.lower()
        dst = img_dir / f"{stem}{ext}"
        if not dst.exists() or sha256_file(dst) != sha256_file(src):
            shutil.copy2(src, dst)
        copied[s.sample_id] = f"images/{split}/{dst.name}"
        w, h = s.image.width, s.image.height
        lines = []
        for b in s.boxes:
            if b.cls != "sfx":
                raise ValueError(f"{s.sample_id}: 非 sfx 框 cls={b.cls!r} 不在本轮导出口径")
            pts = []
            for x, y in b.polygon:
                nx, ny = min(max(x / w, 0.0), 1.0), min(max(y / h, 0.0), 1.0)
                pts.append(f"{nx:.6f} {ny:.6f}")
            if len(pts) < 3:
                raise ValueError(f"{s.sample_id}: 多边形点数 {len(pts)} <3")
            lines.append(f"{CLS_SFX_ID} " + " ".join(pts))
            n_boxes += 1
        (lbl_dir / f"{stem}.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return {"split": split, "images": len(samples), "boxes": n_boxes}


def _write_dataset_yaml(splits_present: list[str]) -> Path:
    lines = [
        "# M2-SFX-ANNOTATE-R2 stage-2 YOLO seg export（training_data/sfx-v1/annotate-r2/final/yolo）",
        f"# 生成：{now_iso()} ｜ T1b-R2 AC5 ｜ names 顺序逐字 = SFX_CLASS_MAP"
        "（src/infrastructure/providers/detection_sfx.py:137，T0 P3-6 硬约束；双通道校验："
        "脚本写后读回断言 + pyyaml 独立解析）",
        "# 多边形 = T1a 实例包络口径（非字形像素 mask）；cls 恒 2=sfx（本轮唯一 GT 类）",
        f"# seed={SEED} 冻结（沿 R1 口径）；挑战集说明见 manifest.r2.json lock.challenge_note",
        "path: .",
        "train: images/train",
        "val: images/val",
    ]
    if "test" in splits_present:
        lines.append("test: images/test")
    lines += [
        "# challenge：R2 轮仍空集（BJ13/14/15 无 complete 样本，见 lock.challenge_note），",
        "# 不写入 ultralytics 键；补齐后由 stage2_finalize_r2.py --step yolo 重新导出。",
        "names:",
    ]
    for k in sorted(SFX_CLASS_MAP):
        lines.append(f"  {k}: {SFX_CLASS_MAP[k]}")
    yaml_path = YAML_DIR / "dataset.yaml"
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def _assert_names_literal_channel1(yaml_path: Path) -> dict:
    """通道 1：写后读回断言（R1 同款手写解析器）。names 顺序逐字 == SFX_CLASS_MAP
    （与生产 detection_sfx 同一断言形态：detection_sfx.py:436 parsed != expected 即 refuse）。"""
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
        raise AssertionError(f"dataset.yaml names 漂移：{parsed!r} != expected {expected!r}；拒绝导出")
    order = [int(k) for k in parsed]
    if order != sorted(SFX_CLASS_MAP):
        raise AssertionError(f"names 顺序漂移：{order} != {sorted(SFX_CLASS_MAP)}")
    return {"parsed": parsed, "expected_literal": expected, "order": order, "assert": "PASS"}


def _assert_names_literal_channel2(yaml_path: Path) -> dict:
    """通道 2：pyyaml 独立解析复核（与通道 1 解析器实现独立，防同一解析 bug 双过）。"""
    import yaml  # pyyaml（venv T1.1.1-impl-py312）

    raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssertionError("pyyaml 解析 dataset.yaml 非 mapping")
    names = raw.get("names")
    expected = {int(k): v for k, v in SFX_CLASS_MAP.items()}
    if names != expected:
        raise AssertionError(f"pyyaml names 漂移：{names!r} != {expected!r}")
    if list(names.keys()) != sorted(expected):
        raise AssertionError(f"pyyaml names 键序漂移：{list(names.keys())}")
    return {"parsed": {str(k): v for k, v in names.items()},
            "expected_literal": {str(k): v for k, v in expected.items()},
            "parser": f"pyyaml {yaml.__version__}", "assert": "PASS"}


def cmd_yolo() -> int:
    container, records = load_manifest(FINAL_DIR / "manifest.r2.json")
    by_split: dict[str, list[SampleRecord]] = {}
    for s in records:
        by_split.setdefault(s.split, []).append(s)

    # train/val 经 TrainingSetBuilder（T1a：训练构建器不可读 test/challenge）
    builder = TrainingSetBuilder(records, allowed_splits=("train", "val"))
    excluded_neg = list(builder.excluded_negative_ids)
    train_val = builder.samples

    if YAML_DIR.exists():
        shutil.rmtree(YAML_DIR)
    copied: dict[str, str] = {}
    stats = []
    stats.append(_export_split([s for s in train_val if s.split == "train"], "train", copied))
    stats.append(_export_split([s for s in train_val if s.split == "val"], "val", copied))
    # test/challenge：独立导出路径（评估脚本路径，不与 TrainingSetBuilder 共享读取）
    for sp in ("test", "challenge"):
        if by_split.get(sp):
            stats.append(_export_split(by_split[sp], sp, copied))
        else:
            stats.append({"split": sp, "images": 0, "boxes": 0, "note": "空集（见 lock.challenge_note）"})

    yaml_path = _write_dataset_yaml([st["split"] for st in stats if st.get("images")])
    names_check = {
        "channel1_readback": _assert_names_literal_channel1(yaml_path),
        "channel2_pyyaml": _assert_names_literal_channel2(yaml_path),
    }

    # 导出后校验：images/labels 数、cls、坐标域、行数、stem 0 失配
    stem_mismatch_total = 0
    for st in stats:
        sp = st["split"]
        if not st.get("images"):
            continue
        lbls = sorted((YAML_DIR / "labels" / sp).glob("*.txt"))
        imgs = sorted([p for p in (YAML_DIR / "images" / sp).iterdir()
                       if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
        if len(lbls) != len(imgs) or len(lbls) != st["images"]:
            raise AssertionError(f"{sp}: images/labels 数不一致 {len(imgs)}/{len(lbls)} vs {st['images']}")
        lbl_stems = {p.stem for p in lbls}
        img_stems = {p.stem for p in imgs}
        mismatch = sorted(lbl_stems ^ img_stems)
        stem_mismatch_total += len(mismatch)
        if mismatch:
            raise AssertionError(f"{sp}: images/labels stem 失配 {mismatch[:5]}")
        n_lines = 0
        for lf in lbls:
            for ln in lf.read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                parts = ln.split()
                if parts[0] != str(CLS_SFX_ID):
                    raise AssertionError(f"{lf.name}: cls={parts[0]} != {CLS_SFX_ID}")
                vals = [float(v) for v in parts[1:]]
                if len(vals) < 6 or len(vals) % 2:
                    raise AssertionError(f"{lf.name}: 多边形坐标数非法 {len(vals)}")
                if any(v < 0.0 or v > 1.0 for v in vals):
                    raise AssertionError(f"{lf.name}: 坐标越界")
                n_lines += 1
        if n_lines != st["boxes"]:
            raise AssertionError(f"{sp}: label 行数 {n_lines} != manifest 框数 {st['boxes']}")

    print(f"[yolo] split stats: {json.dumps(stats, ensure_ascii=False)}")
    print(f"[yolo] names 双通道: {json.dumps(names_check, ensure_ascii=False)}")
    print(f"[yolo] builder excluded_negative={excluded_neg}")
    print(f"[yolo] stem_mismatch_total={stem_mismatch_total}")
    (YAML_DIR / "_export_stats.json").write_text(
        json.dumps({"generated_at_utc": now_iso(), "seed": SEED,
                    "fingerprint": (container.get("lock") or {}).get("fingerprint"),
                    "splits": stats, "names_check": names_check,
                    "stem_mismatch_total": stem_mismatch_total,
                    "builder_excluded_negative_ids": excluded_neg,
                    "copied_images": copied}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return 0


# ---------------------------------------------------------------------------
# summary：数据树内 export-summary + Git 内摘要（相对路径 + sha256 + §8.1 对照）
# ---------------------------------------------------------------------------


def cmd_summary() -> int:
    container, records = load_manifest(FINAL_DIR / "manifest.r2.json")
    lock = container.get("lock") or {}
    vmap, judge_stats = load_final_verdicts()
    synth = _read_json(SYNTH_MANIFEST)
    r1_man = _read_json(R1_MANIFEST)
    bj_new = _read_json(R2_BJ_NEW_JSON)
    r2_man = _read_json(R2_MANIFEST)

    by_split: dict[str, list[SampleRecord]] = {}
    for s in records:
        by_split.setdefault(s.split, []).append(s)

    def split_detail(sp: str) -> dict:
        subset = by_split.get(sp, [])
        return {
            "samples": len(subset),
            "boxes": sum(len(s.boxes) for s in subset),
            "real": sum(1 for s in subset if s.annotation_status == "complete"),
            "synthetic": sum(1 for s in subset if s.annotation_status == "synthetic"),
            "groups": sorted({s.group for s in subset}),
            "images": len({s.image.sha256 for s in subset}),
        }

    export_stats_path = YAML_DIR / "_export_stats.json"
    yolo_stats = _read_json(export_stats_path) if export_stats_path.is_file() else {}

    # BJ 域正集（本轮核心目标）：complete 样本中 review_domain=bj 的页数与框数（如实报数）
    r2_complete = [m for m in r2_man if m["annotation_status"] == "complete"]
    bj_positive = [m for m in r2_complete if m["provenance"].get("review_domain") == "bj"]
    bj_positive_detail = [
        {"sample_id": m["sample_id"], "case_id": m["provenance"]["case_id"],
         "group": m["group"], "boxes": len(m["boxes"]),
         "kept_units": [b.get("unit_id") for b in (m["provenance"].get("boxes_meta") or [])
                        if b.get("verdict") in KEEP_VERDICTS]}
        for m in bj_positive
    ]
    # BJ 正集中的竖排/毛笔形态覆盖（主攻形态=A′ 毛笔竖排召回）：按判定 rationale 人工口径登记
    bj_groups = sorted({m["group"] for m in bj_positive})

    # 组隔离复核（split 步已断言，此处独立复核出数）
    by_group_split: dict[str, set[str]] = {}
    for s in records:
        by_group_split.setdefault(s.group, set()).add(s.split)
    cross = {g: sp for g, sp in by_group_split.items() if len(sp) > 1}

    # R1 三集对照（R1 final 数字，只读 R1 树）
    r1_final: dict = {}
    r1_final_path = R1_ANNOTATE / "final" / "export-summary.json"
    if r1_final_path.is_file():
        r1_final = _read_json(r1_final_path)

    # 五 manifest 指纹（sha256）
    artifacts: dict[str, str | None] = {}
    for rel in ["preannotate/manifest.r2.json",
                "final/manifest.r2.json", "final/manifest.train.json",
                "final/manifest.val.json", "final/manifest.test.json",
                "final/manifest.challenge.json",
                "final/yolo/dataset.yaml", "final/yolo/_export_stats.json"]:
        p = OUT_DIR / rel
        artifacts[rel] = sha256_file(p) if p.is_file() else None

    # R1 §8.1 对照表数字回填（R2 后新状态，如实登记）
    section81 = {
        "source": "verification/M2-SFX-ANNOTATE-R1/stage2-report.md §8.1（R1 时点状态）",
        "r1_then": {
            "bj_real_pages_annotated": 15,
            "ko_real_pages_annotated": 10,
            "bj_positive_samples": 0,
            "challenge": "空集",
            "synthetic": 324,
        },
        "r2_now": {
            "bj_real_pages_annotated": "在册（cases.json+落位）25 页（AC1 补齐 BJ16-25）；其中经预标注判定覆盖 19 页（BJ01-15 R1 预标注+BJ16-25 R2 预标注），本轮判定入正集 5 页",
            "ko_real_pages_annotated": ("在册 15 页（AC5 复核对账：R1 已标注 K01-10 页图按 R1 manifest "
                                        "引用路径在盘核实 10/10；R2 新落 K13/K15/K18/K19/K24 按 "
                                        "cases.json+resolve_asset_roots(+R2 素材根) 可解析 5/5，见 "
                                        "selection/material-selection.json ko_selected）。其中经预标注"
                                        "+判定 10 页（K01-10）；R2 新 5 页素材在册未标注（本轮判定范围"
                                        "不含 KO 新页，如实登记）"),
            "bj_positive_samples": {
                "pages": len(bj_positive),
                "boxes": sum(len(m["boxes"]) for m in bj_positive),
                "cases": [m["provenance"]["case_id"] for m in bj_positive],
                "groups": bj_groups,
                "detail": bj_positive_detail,
                "note": ("本轮 11 confirm 框判定 rationale 主体为竖排/斜排毛笔假名与艺术化"
                         "字形（codex/agy 双评审原文见 judgments/consensus.json）——A′ 主攻"
                         "毛笔竖排形态获得首批真实正样本；量级仍小（5 页 11 框），如实登记"),
            },
            "challenge": "仍空集（BJ13 本轮无新判定，R1 delete 未翻案；AC5 验收判据允许分支，如实登记交编排裁决）",
            "synthetic": len(synth),
            "replay_pages": "R1 C4 偏差部分闭合：回放 6 单元本轮全判 delete（判定链留痕 stage2r2）——回放页仍无训练正例，按判定如实排除（delete 框已出框列表）",
        },
    }

    summary = {
        "task": "M2-SFX-ANNOTATE-R2 stage-2（AC5：R2 判定并入 + 三集扩集重导出 + YOLO + 验证）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-ANNOTATE-R2/stage2_finalize_r2.py --step summary",
        "mode": ("ai-review-backfill（沿 R1 口径：codex+agy 共识 + 分歧仲裁；"
                 "human_review=false，不谎称人工；provenance.stage2r2 留判定链）"),
        "r2_judgments": {
            "units_total": judge_stats["units_total"],
            "units_by_part": judge_stats["units_by_part"],
            "consensus_units": judge_stats["consensus"],
            "arbitrated_units": judge_stats["divergence_arbitrated"],
            "final_verdict_dist": judge_stats["verdict_dist"],
            "reviewer_dist": judge_stats["reviewer_dist"],
            "ac2_bj_lowconf_note": ("units.json notes：R1 残留 BJ 域 11 单元中 conf∈[0.2,0.5) "
                                    "为 0——AC2 扩审部分为空集，如实登记"),
        },
        "manifest_merge": {
            "r1_base": "annotate-r1/preannotate/manifest.json（72 样本 450 框，只读；R1 判定链 provenance.stage2 保留）",
            "r2_bj_new": "annotate-r2/preannotate/manifest-bj-new.json（10 样本 29 框，BJ16-25）",
            "r2_merged": "annotate-r2/preannotate/manifest.r2.json",
            "samples_total": len(r2_man),
            "r1_samples_touched_by_r2": sum(1 for m in r2_man if m["provenance"].get("stage2r2") and m["sample_id"].startswith(("pre-bj0", "pre-j", "pre-k", "imp-"))),
            "r1_samples_untouched": len(r2_man) - len(bj_new) - sum(1 for m in r2_man if m["provenance"].get("stage2r2") and not any(m is x for x in bj_new)),
            "bj_new_to_complete": len(bj_positive),
            "stage2r2_actions": dict(Counter((m["provenance"].get("stage2r2") or {}).get("action", "—") for m in r2_man)),
        },
        "ac5_splits": {
            "seed": lock.get("seed"),
            "method": lock.get("method"),
            "pinned_groups": lock.get("pinned_groups"),
            "fingerprint": lock.get("fingerprint"),
            "by_split": {sp: split_detail(sp) for sp in ("train", "val", "test", "challenge")},
            "manifest_files": ["manifest.r2.json", "manifest.train.json", "manifest.val.json",
                               "manifest.test.json", "manifest.challenge.json"],
            "challenge_empty_reason": lock.get("challenge_note"),
            "group_isolation_violations": cross,
            "group_isolation_verified": len(cross) == 0,
        },
        "ac5_bj_positive": section81["r2_now"]["bj_positive_samples"],
        "ac5_synthetic": {
            "source": "annotate-r1/synthetic/manifest.json（R1 渲染产物只读并入；图像从 R1 数据树复制）",
            "samples": len(synth),
            "pinned_group": SYNTH_GROUP,
            "in_test": sum(1 for s in records if s.annotation_status == "synthetic" and s.split == "test"),
        },
        "ac5_yolo": {
            "root": "final/yolo",
            "dataset_yaml": "final/yolo/dataset.yaml",
            "names_dual_channel_check": yolo_stats.get("names_check", {}),
            "per_split": yolo_stats.get("splits", []),
            "stem_mismatch_total": yolo_stats.get("stem_mismatch_total"),
            "polygon_caliber": "T1a 实例包络（归一化，cls 恒 2=sfx）",
            "train_builder": "train/val 经 TrainingSetBuilder（不可读 test/challenge）；test/challenge 独立导出路径",
            "excluded_negative_ids": yolo_stats.get("builder_excluded_negative_ids", []),
        },
        "section81_vs_r1": section81,
        "r1_baseline_for_diff": {
            "export_summary_file": "annotate-r1/final/export-summary.json",
            "r1_by_split": (r1_final.get("ac4_splits") or {}).get("by_split"),
            "r1_fingerprint": (r1_final.get("ac4_splits") or {}).get("fingerprint"),
        },
        "artifacts_sha256": artifacts,
        "honest_notes": [
            "AC2 BJ 低置信层为空集（R1 残留 BJ 单元无一落在 conf 0.2-0.5），未产生新正样本",
            "challenge 仍空集：BJ13/14/15 本轮零新判定，未翻案未凑数",
            "K11-15 素材在册未标注（本轮判定范围不含 KO 新页）；BJ19/20/21/22/25 页候选框 conf<0.2 或全 delete，保持 pseudo",
            "R1 底册只读：R2 判定链写在 provenance.stage2r2，不覆盖 R1 provenance.stage2",
            "worksheet-bj-new.json 的 verdict 列回填不在本轮 ask 范围：判定留痕以 judgments/* 与 manifest.r2.json stage2r2 为准",
        ],
    }
    # 修正 r1_touched 统计（上面的推导式过度复杂，直接按 stage2r2 存在且非 bj_new 样本计）
    bj_ids = {m["sample_id"] for m in bj_new}
    touched = [m for m in r2_man if m["provenance"].get("stage2r2") and m["sample_id"] not in bj_ids]
    summary["manifest_merge"]["r1_samples_touched_by_r2"] = len(touched)
    summary["manifest_merge"]["r1_samples_untouched"] = len(r2_man) - len(bj_new) - len(touched)

    atomic_write_json(SUMMARY_JSON, summary)

    # Git 内摘要：不写本机绝对路径（沿 T1a/T1b 惯例）
    git_summary = json.loads(json.dumps(summary))
    git_summary["data_root_gitignored"] = (
        "training_data/sfx-v1/annotate-r2/（repo gitignored 外部树；annotate-r1/ 同理在 R1 worktree）；"
        "本摘要内路径均相对 training_data/sfx-v1/ 根")
    git_summary["yolo_layout"] = {
        "images": "annotate-r2/final/yolo/images/{train,val,test}/（challenge 空集未导出）",
        "labels": "annotate-r2/final/yolo/labels/{train,val,test}/（YOLO seg 归一化多边形，cls=2）",
        "stem_rule": "sample_id 中 '/' 替换为 '__'（synth-r1/synth-… → synth-r1__synth-…）",
    }
    atomic_write_json(GIT_SUMMARY, git_summary)
    print(f"[summary] wrote {SUMMARY_JSON}")
    print(f"[summary] wrote {GIT_SUMMARY}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True,
                        choices=["manifest", "split", "yolo", "summary", "all"])
    args = parser.parse_args()
    steps = [args.step] if args.step != "all" else ["manifest", "split", "yolo", "summary"]
    for s in steps:
        rc = {"manifest": cmd_manifest, "split": cmd_split,
              "yolo": cmd_yolo, "summary": cmd_summary}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
