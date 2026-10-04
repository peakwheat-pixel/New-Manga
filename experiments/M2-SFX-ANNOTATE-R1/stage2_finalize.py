"""M2-SFX-ANNOTATE-R1 阶段二收尾（T1b stage-2）：AC3 裁决回填 + AC4 三集导出 + AC5 合成并入。

编排裁定（2026-10-04，user 全权授权编排会话；本脚本只实现裁定，不重新裁定）：

- AC3 判定来源 = AI 代审替代用户逐条审核：codex+agy 双评审共识（judgments/consensus.json，
  397 单元）+ 分歧单元第三方仲裁（judgments/arbiter/batch-*.json，16 单元），覆盖
  conf>=0.5 全部 413 单元；残留（conf<0.5 与 ref 无 conf，393 单元）单列
  judgments/user-residual.json 交用户，留后续扩标（编排裁定范围外）。
- 回填口径：worksheet verdict 列 = 最终 verdict；user_rationale 列 =
  「reviewer=codex+agy-consensus|arbiter」+ rationale（裁决依据全文，不截断）。
- manifest：有正判定（confirm/correct）且非回放页的样本 pseudo→complete；provenance
  如实补 ai-consensus/arbiter 判定链（human_review=false，不谎称人工）；verdict=delete
  的框从正集 GT 排除并在 provenance 留痕；无判定框同样不入正集 GT 并留痕。
- 域内回放 5 页（stage-1 selection.replay = BJ06+J38/J41/J43/J51）保持 pseudo 不入本轮
  训练集（含 BJ06 的 8 个 confirm——BJ06 在合同 AC2 中身份即回放页）。
- AC5：synthetic/ 324 样本（T1a 渲染管线参数网格，stage2_synth_batch.py 产物）读其
  manifest 以 pinned 组并入 train，不入 test。
- AC4：T1a 拆分器组隔离（assign_splits：作品组不跨集 + BJ13/14/15 挑战集单列 +
  seed=20261004 冻结）→ train/val/test manifest + split 指纹；YOLO seg 导出
  （dataset.yaml names 顺序逐字 = SFX_CLASS_MAP，T0 P3-6 硬约束，写后读回断言）。
- train/val 图像导出走 TrainingSetBuilder（T1a 设计：训练构建器不可读 test/challenge）；
  test/challenge 走独立导出路径。

纪律：零 src 修改（生产 SFX_CLASS_MAP 经 sys.path 只读 import）；素材树只读；T1a
工具链（schema/atomicio/splits/TrainingSetBuilder）只读复用不重造。数据本体落
training_data/sfx-v1/annotate-r1/final/（gitignored），Git 只进摘要。

步骤（--step）：backfill → manifest → split → yolo → summary（all 依序全跑）。
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

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r1"
JUDG_DIR = OUT_DIR / "judgments"
WORKSHEET_JSON = OUT_DIR / "worksheet" / "worksheet.json"
WORKSHEET_MD = OUT_DIR / "worksheet" / "worksheet.md"
PREANNOTATE_JSON = OUT_DIR / "preannotate" / "manifest.json"
SYNTH_MANIFEST = OUT_DIR / "synthetic" / "manifest.json"
FINAL_DIR = OUT_DIR / "final"
YAML_DIR = FINAL_DIR / "yolo"
RESIDUAL_JSON = JUDG_DIR / "user-residual.json"
SUMMARY_JSON = FINAL_DIR / "export-summary.json"
GIT_SUMMARY = REPO_ROOT / "verification" / "M2-SFX-ANNOTATE-R1" / "stage2-final-summary.json"

SEED = SEED_DEFAULT  # 20261004（沿 T1a splits.SEED_DEFAULT，seed 冻结）
# 合成组钉 train（沿 T1a cli.PINNED_GROUPS 先例：单一大合成组不参与比例切片；
# 编排裁定 AC5：合成入 train 不入 test）
SYNTH_GROUP = "synthetic/annotate-r1"
PINNED_GROUPS = {SYNTH_GROUP: "train"}
REVIEWER_CONSENSUS = "codex+agy-consensus"
REVIEWER_ARBITER = "arbiter"
KEEP_VERDICTS = ("confirm", "correct")
# 域内回放 5 页 = stage-1 selection.replay（合同 AC2「域内回放 BJ06+J 系 ≥5 页」）；
# 编排裁定：保持 pseudo 不入本轮训练集（编排裁定范围外，留后续扩标）。
REPLAY_CASE_IDS = ("BJ06", "J38", "J41", "J43", "J51")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 判定装载：consensus + arbiter → unit_id → {verdict, reviewer, rationale}
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
        "units_total_conf_ge_0p5": len(units),
        "consensus": len(cons),
        "divergence_arbitrated": n_arb_used,
        "verdict_dist": dict(Counter(v["verdict"] for v in vmap.values())),
        "reviewer_dist": dict(Counter(v["reviewer"] for v in vmap.values())),
    }
    return vmap, stats


# ---------------------------------------------------------------------------
# backfill：worksheet（json+md）回填 + 残留清单
# ---------------------------------------------------------------------------


def _rationale_text(v: dict) -> str:
    return f"reviewer={v['reviewer']}；{v['rationale']}"


def cmd_backfill() -> int:
    vmap, stats = load_final_verdicts()
    ws = _read_json(WORKSHEET_JSON)
    units = ws["units"]

    n_backfilled = 0
    residual: list[dict] = []
    for u in units:
        j = vmap.get(u["unit_id"])
        if j is None:
            conf = u.get("ai_conf")
            if isinstance(conf, (int, float)) and conf >= 0.5:
                tier = "conf_0.5_to_1.0"
            elif isinstance(conf, (int, float)) and conf >= 0.2:
                tier = "conf_0.2_to_0.5"
            elif isinstance(conf, (int, float)):
                tier = "conf_lt_0.2"
            else:
                tier = "ref_no_conf"
            u.setdefault("review_tier", tier)
            residual.append(
                {
                    "unit_id": u["unit_id"],
                    "domain": u["domain"],
                    "case_id": u["case_id"],
                    "conf": conf,
                    "review_tier": tier,
                    "xyxy": u["xyxy"],
                    "preview_file": u["preview_file"],
                    "sources": u.get("sources", []),
                }
            )
            continue
        u["verdict"] = j["verdict"]
        u["user_rationale"] = _rationale_text(j)
        u["review_tier"] = "conf_ge_0.5_ai_reviewed"
        n_backfilled += 1

    residual_replay = [r for r in residual if r["case_id"] in REPLAY_CASE_IDS]
    residual_out = {
        "purpose": "AC3 未判定单元残留清单（交用户；本轮 AI 代审范围=conf>=0.5，编排裁定：其余 conf 层与回放页保持 pseudo 不入本轮训练集，留后续扩标）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step backfill",
        "review_scope": {
            "judged": n_backfilled,
            "reviewer_map": {"consensus": REVIEWER_CONSENSUS, "divergence": REVIEWER_ARBITER},
            "verdict_dist_judged": stats["verdict_dist"],
        },
        "residual_total": len(residual),
        "residual_by_tier": dict(Counter(r["review_tier"] for r in residual)),
        "residual_by_domain": dict(Counter(r["domain"] for r in residual)),
        "replay_pages_kept_pseudo": {
            "case_ids": list(REPLAY_CASE_IDS),
            "note": "合同 AC2 域内回放 5 页（BJ06+J38/J41/J43/J51）；即使其单元在本轮获得判定（BJ06 8 confirm），样本仍保持 pseudo 不入本轮训练集",
            "residual_units_on_replay_pages": len(residual_replay),
        },
        "user_action_guide": "逐单元回填 worksheet.json 的 verdict 列（confirm/correct/delete）与 user_rationale 列；页级漏标用 miss+框坐标补记（worksheet.md 页小节）；完成后重跑 stage2_finalize.py --step manifest --step split --step yolo --step summary 即可扩集",
        "units": residual,
    }
    atomic_write_json(RESIDUAL_JSON, residual_out)

    # worksheet.json：顶层加 backfill 元数据（units 原地已回填）
    ws["backfill"] = {
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step backfill",
        "mode": "ai-review-backfill（编排裁定：codex+agy 共识 + 分歧仲裁替代用户逐条审核；human_review=false，不谎称人工）",
        "judgments_sources": ["judgments/consensus.json", "judgments/divergence.json",
                              "judgments/arbiter/batch-*.json"],
        "backfilled_units": n_backfilled,
        "verdict_dist": stats["verdict_dist"],
        "residual_file": "judgments/user-residual.json",
        "residual_total": len(residual),
    }
    atomic_write_json(WORKSHEET_JSON, ws)

    # worksheet.md：逐行回填表格最后两列（页级表 7 列 / ogkalu 表 6 列，均按 unit_id 定位）
    n_md = 0
    md_lines = WORKSHEET_MD.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(md_lines):
        m = re.match(r"^\|\s*(R1-[A-Za-z0-9_\-]+B\d+)\s*\|", line)
        if not m:
            continue
        uid = m.group(1)
        j = vmap.get(uid)
        if j is None:
            continue
        cells = line.split("|")
        if len(cells) < 4:
            continue
        # 尾两列 = 用户裁决 / user_rationale（行尾以 | 结束 → cells[-1] 为空串）
        conf_s = ""
        u = next(x for x in units if x["unit_id"] == uid)
        if isinstance(u.get("ai_conf"), (int, float)):
            conf_s = f"{u['ai_conf']:.2f}"
        cells[-3] = f" {j['verdict']} "
        cells[-2] = f" {conf_s}｜{_rationale_text(j)} "
        md_lines[i] = "|".join(cells)
        n_md += 1
    md_lines += [
        "",
        "---",
        "",
        f"## 回填记录（stage-2，{now_iso()}）",
        "",
        f"- 回填 {n_backfilled}/{ws['n_units']} 单元（范围=conf>=0.5；reviewer={REVIEWER_CONSENSUS}"
        f" 共识 {stats['consensus']} + {REVIEWER_ARBITER} 仲裁 {stats['divergence_arbitrated']}）",
        f"- 最终 verdict 分布：{json.dumps(stats['verdict_dist'], ensure_ascii=False)}",
        f"- 残留 {len(residual)} 单元（conf<0.5 与 ref 无 conf）→ judgments/user-residual.json，交用户后续扩标",
        f"- reviewer 标识即裁决来源：{REVIEWER_CONSENSUS}=codex+agy 双评审共识；{REVIEWER_ARBITER}=分歧第三方仲裁（human_review=false，不谎称人工）",
        "",
    ]
    WORKSHEET_MD.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"[backfill] worksheet units backfilled={n_backfilled} residual={len(residual)} md_rows={n_md}")
    print(f"[backfill] verdict dist: {json.dumps(stats['verdict_dist'], ensure_ascii=False)}")
    return 0


# ---------------------------------------------------------------------------
# manifest：判定回填进 T1a manifest（pseudo→complete / delete 排除留痕）
# ---------------------------------------------------------------------------


def _units_for_sample(m: dict) -> list[str]:
    prov = m["provenance"]
    if prov["type"] == "asset_case":
        prefix = f"R1-{prov['case_id']}-"
    elif prov["type"] == "external_model":
        prefix = f"R1-OGK-{prov['region_key']}-"
    else:
        return []
    return [f"{prefix}B{i:02d}" for i in range(len(m["boxes"]))]


def cmd_manifest() -> int:
    vmap, _stats = load_final_verdicts()
    ws = _read_json(WORKSHEET_JSON)
    unit_by_id = {u["unit_id"]: u for u in ws["units"]}
    man = _read_json(PREANNOTATE_JSON)

    changed = 0
    action_counter: Counter = Counter()
    for m in man:
        prov = m["provenance"]
        uids = _units_for_sample(m)
        if not uids:
            prov["stage2"] = {
                "action": "kept_pseudo_zero_box_negative_evidence",
                "note": "零检出负证据样本（T1a schema 允许 pseudo 空框），无审核单元",
                "human_review": False,
            }
            action_counter[prov["stage2"]["action"]] += 1
            continue
        cid = prov.get("case_id", "")
        verdicts = [vmap.get(uid) for uid in uids]

        if cid in REPLAY_CASE_IDS:
            # 编排裁定：回放 5 页保持 pseudo 不入本轮训练集；回填结果仅在 worksheet 留痕
            n_judged = sum(1 for v in verdicts if v)
            n_keep = sum(1 for v in verdicts if v and v["verdict"] in KEEP_VERDICTS)
            prov["stage2"] = {
                "action": "kept_pseudo_replay_page",
                "note": ("域内回放页（合同 AC2 域内回放 5 页之一）：编排裁定保持 pseudo 不入本轮训练集；"
                         "本页单元判定结果仅回填 worksheet 留痕，manifest 框列表未改动"),
                "reviewed_units": n_judged,
                "would_keep_units": n_keep,
                "human_review": False,
            }
            action_counter["kept_pseudo_replay_page"] += 1
            continue

        keep_idx = [i for i, v in enumerate(verdicts) if v and v["verdict"] in KEEP_VERDICTS]
        del_idx = [i for i, v in enumerate(verdicts) if v and v["verdict"] == "delete"]
        unj_idx = [i for i, v in enumerate(verdicts) if v is None]

        if not keep_idx:
            prov["stage2"] = {
                "action": "kept_pseudo_no_positive_verdict",
                "note": "本轮判定无 confirm/correct（全部 delete 或未判定）：样本保持 pseudo 不入正集；框列表未改动",
                "reviewed_units": len(verdicts) - len(unj_idx),
                "excluded_delete_units": [uids[i] for i in del_idx],
                "unjudged_units": [uids[i] for i in unj_idx],
                "human_review": False,
            }
            action_counter["kept_pseudo_no_positive_verdict"] += 1
            continue

        # 正集样本：boxes 只留判定保留框；boxes_meta 同步对齐（T1a 索引对齐约束）
        meta = prov.get("boxes_meta", [{}] * len(m["boxes"]))
        new_boxes, new_meta, excluded, unjudged, corrections = [], [], [], [], []
        for i, (b, bm) in enumerate(zip(m["boxes"], meta)):
            uid = uids[i]
            v = verdicts[i]
            if v is None:
                unjudged.append({"unit_id": uid, "conf": bm.get("conf"),
                                 "note": "conf<0.5 未判定（编排裁定：保持 pseudo 不入本轮训练集）"})
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
                # AC3「修正行记 revision 链」：本轮 AI 仲裁判定保留为 SFX 但框需修；
                # 无新坐标（人工补画属后续扩标），坐标未动、修正需求如实留痕。
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
        prov["boxes_meta"] = new_meta
        m["annotation_status"] = "complete"
        prov["stage"] = "annotate-r1-stage2"
        prov["quality_note"] = (
            "AI 代审正集样本（编排裁定 2026-10-04）：boxes=conf>=0.5 判定保留框"
            "（codex+agy 共识 + 分歧仲裁），provenance.stage2 留判定链；human_review=false，"
            "不谎称人工；未判定候选框不入正集 GT（见 stage2.unjudged_boxes）"
        )
        prov["stage2"] = {
            "action": "completed",
            "mode": "ai-review-backfill",
            "judgments_sources": ["judgments/consensus.json", "judgments/divergence.json",
                                  "judgments/arbiter/batch-*.json"],
            "reviewed_units": len(verdicts) - len(unj_idx),
            "kept_units": len(new_boxes),
            "excluded_delete_boxes": excluded,
            "unjudged_boxes": unjudged,
            "correction_notes": corrections,
            "human_review": False,
        }
        action_counter["completed"] += 1
        changed += 1

    # 全量 schema 校验 + boxes/boxes_meta 索引对齐校验
    for m in man:
        rec = SampleRecord.from_dict(m)
        errors = rec.validate()
        if errors:
            raise ValueError(f"{m['sample_id']}: {errors}")
        prov = m["provenance"]
        if prov["type"] == "asset_case" and prov.get("boxes_meta") is not None:
            if len(prov["boxes_meta"]) != len(m["boxes"]):
                raise ValueError(f"{m['sample_id']}: boxes_meta 与 boxes 索引失配")
        st = (prov.get("stage2") or {}).get("action")
        if st == "completed" and not m["boxes"]:
            raise ValueError(f"{m['sample_id']}: completed 样本不允许空框")

    atomic_write_json(PREANNOTATE_JSON, man)
    print(f"[manifest] samples={len(man)} updated_to_complete={changed}")
    print(f"[manifest] actions: {json.dumps(dict(action_counter), ensure_ascii=False)}")
    return 0


# ---------------------------------------------------------------------------
# split：T1a 拆分器组隔离 + 合成并入（pinned train）
# ---------------------------------------------------------------------------


def _load_pos_samples() -> list[SampleRecord]:
    man = _read_json(PREANNOTATE_JSON)
    out = []
    for m in man:
        if (m["provenance"].get("stage2") or {}).get("action") == "completed":
            out.append(SampleRecord.from_dict(m))
    return out


def _load_synth_samples() -> list[SampleRecord]:
    raw = _read_json(SYNTH_MANIFEST)
    return [SampleRecord.from_dict(d) for d in raw]


def cmd_split() -> int:
    pos = _load_pos_samples()
    synth = _load_synth_samples()
    if not synth:
        raise ValueError("synthetic manifest 为空：AC5 并入无从执行")
    all_samples = pos + synth

    group_split = assign_splits(all_samples, seed=SEED, force=True, pinned=PINNED_GROUPS)
    fingerprint = split_fingerprint(all_samples, SEED)
    by_split = Counter(s.split for s in all_samples)

    # 校验：合成全落 train（AC5：不入 test）
    synth_splits = Counter(s.split for s in synth)
    if set(synth_splits) - {"train"}:
        raise ValueError(f"合成样本落入非 train split: {dict(synth_splits)}")
    # 校验：真实页组不跨集
    by_group_split: dict[str, set[str]] = {}
    for s in all_samples:
        by_group_split.setdefault(s.group, set()).add(s.split)
    cross = {g: sp for g, sp in by_group_split.items() if len(sp) > 1 and g != SYNTH_GROUP}
    if cross:
        raise ValueError(f"组跨集违例: {cross}")

    lock = {
        "seed": SEED,
        "method": "group-hash-rank-v2（T1a splits.assign_splits）",
        "pinned_groups": dict(PINNED_GROUPS),
        "fingerprint": fingerprint,
        "frozen_at": now_iso(),
        "challenge_single_bucket": sorted(CHALLENGE_CASE_IDS),
        "challenge_note": (
            "本轮正集无 BJ13/14/15 complete 样本：BJ13 唯一 conf>=0.5 判定单元被判 delete、"
            "BJ14/BJ15 无 conf>=0.5 判定单元（三页框均 conf<0.5 未判定，编排裁定不入本轮正集），"
            "故 challenge split 空集；BJ13/14/15 页级样本保持 pseudo 留待用户扩标。"
            "挑战集正框补齐后重跑 split+yolo 即自动单列。"
        ),
    }
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest(FINAL_DIR / "manifest.r1.json", all_samples, seed=SEED, extra={"lock": lock})

    for sp in ("train", "val", "test", "challenge"):
        subset = [s for s in all_samples if s.split == sp]
        write_manifest(
            FINAL_DIR / f"manifest.{sp}.json",
            subset,
            seed=SEED,
            extra={"split": sp,
                   **({"note": "空集（见 manifest.r1.json lock.challenge_note）"} if not subset else {}),
                   "fingerprint": fingerprint},
        )
    print(f"[split] pos={len(pos)} synth={len(synth)} by_split={json.dumps(dict(by_split), ensure_ascii=False)}")
    print(f"[split] group_split={json.dumps(group_split, ensure_ascii=False)}")
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
    return p if p.is_absolute() else (OUT_DIR / p)


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
        "# M2-SFX-ANNOTATE-R1 stage-2 YOLO seg export（training_data/sfx-v1/annotate-r1/final/yolo）",
        f"# 生成：{now_iso()} ｜ T1b AC4 ｜ names 顺序逐字 = SFX_CLASS_MAP"
        "（src/infrastructure/providers/detection_sfx.py:137，T0 P3-6 硬约束；写后读回断言）",
        "# 多边形 = T1a 实例包络口径（非字形像素 mask）；cls 恒 2=sfx（本轮唯一 GT 类）",
        f"# seed={SEED} 冻结；挑战集说明见 manifest.r1.json lock.challenge_note",
        "path: .",
        "train: images/train",
        "val: images/val",
    ]
    if "test" in splits_present:
        lines.append("test: images/test")
    lines += [
        "# challenge：本轮空集（BJ13/14/15 无 complete 样本），不写入 ultralytics 键；",
        "# 补齐后由 stage2_finalize.py --step yolo 重新导出。",
        "names:",
    ]
    for k in sorted(SFX_CLASS_MAP):
        lines.append(f"  {k}: {SFX_CLASS_MAP[k]}")
    yaml_path = YAML_DIR / "dataset.yaml"
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def _assert_names_literal(yaml_path: Path) -> dict:
    """写后读回断言：names 顺序逐字 == SFX_CLASS_MAP（与生产 detection_sfx 同一断言形态：
    detection_sfx.py:436 parsed != {str(k): v for k, v in SFX_CLASS_MAP.items()} 即 refuse）。"""
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
    # 顺序逐字复核：yaml 中出现顺序 == SFX_CLASS_MAP 键升序（0,1,2,3）
    order = [int(k) for k in parsed]
    if order != sorted(SFX_CLASS_MAP):
        raise AssertionError(f"names 顺序漂移：{order} != {sorted(SFX_CLASS_MAP)}")
    return {"parsed": parsed, "expected_literal": expected, "order": order, "assert": "PASS"}


def cmd_yolo() -> int:
    container, records = load_manifest(FINAL_DIR / "manifest.r1.json")
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
    names_check = _assert_names_literal(yaml_path)

    # 导出后校验：labels 行数/cls/坐标域与 manifest 一致
    for st in stats:
        sp = st["split"]
        if not st.get("images"):
            continue
        lbls = sorted((YAML_DIR / "labels" / sp).glob("*.txt"))
        imgs = sorted([p for p in (YAML_DIR / "images" / sp).iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")])
        if len(lbls) != len(imgs) or len(lbls) != st["images"]:
            raise AssertionError(f"{sp}: images/labels 数不一致 {len(imgs)}/{len(lbls)} vs {st['images']}")
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
    print(f"[yolo] names assert: {json.dumps(names_check, ensure_ascii=False)}")
    print(f"[yolo] builder excluded_negative={excluded_neg}")
    (YAML_DIR / "_export_stats.json").write_text(
        json.dumps({"generated_at_utc": now_iso(), "seed": SEED,
                    "fingerprint": (container.get("lock") or {}).get("fingerprint"),
                    "splits": stats, "names_check": names_check,
                    "builder_excluded_negative_ids": excluded_neg,
                    "copied_images": copied}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return 0


# ---------------------------------------------------------------------------
# summary：数据树内 export-summary + Git 内摘要（相对路径 + sha256）
# ---------------------------------------------------------------------------


def cmd_summary() -> int:
    container, records = load_manifest(FINAL_DIR / "manifest.r1.json")
    lock = container.get("lock") or {}
    vmap, judge_stats = load_final_verdicts()
    residual = _read_json(RESIDUAL_JSON)
    synth = _read_json(SYNTH_MANIFEST)
    ws = _read_json(WORKSHEET_JSON)

    real = [s for s in records if s.annotation_status == "complete"]
    synth_recs = [s for s in records if s.annotation_status == "synthetic"]
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
    names_check = yolo_stats.get("names_check", {})
    yolo_splits = yolo_stats.get("splits", [])

    correct_units = sorted(uid for uid, v in vmap.items() if v["verdict"] == "correct")

    summary = {
        "task": "M2-SFX-ANNOTATE-R1 stage-2（AC3 回填 + AC4 三集导出 + AC5 合成并入）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-ANNOTATE-R1/stage2_finalize.py --step summary",
        "mode": "ai-review-backfill（编排裁定 2026-10-04：codex+agy 共识 + 分歧仲裁替代用户逐条审核；human_review=false，不谎称人工）",
        "ac3_backfill": {
            "units_conf_ge_0p5": judge_stats["units_total_conf_ge_0p5"],
            "consensus_units": judge_stats["consensus"],
            "arbitrated_units": judge_stats["divergence_arbitrated"],
            "final_verdict_dist": judge_stats["verdict_dist"],
            "worksheet_backfilled": True,
            "correct_units_revision_notes": correct_units,
            "residual": {
                "file": "judgments/user-residual.json",
                "total": residual["residual_total"],
                "by_tier": residual["residual_by_tier"],
                "by_domain": residual["residual_by_domain"],
                "disposition": "交用户后续扩标（编排裁定范围外）；回放页与其余 conf 层保持 pseudo 不入本轮训练集",
            },
        },
        "manifest": {
            "file": "preannotate/manifest.json",
            "samples_total": len(_read_json(PREANNOTATE_JSON)),
            "units_total_worksheet": ws["n_units"],
        },
        "ac4_splits": {
            "seed": lock.get("seed"),
            "method": lock.get("method"),
            "pinned_groups": lock.get("pinned_groups"),
            "fingerprint": lock.get("fingerprint"),
            "by_split": {sp: split_detail(sp) for sp in ("train", "val", "test", "challenge")},
            "manifest_files": ["manifest.r1.json", "manifest.train.json", "manifest.val.json",
                               "manifest.test.json", "manifest.challenge.json"],
            "challenge_empty_reason": lock.get("challenge_note"),
            "group_isolation_verified": "assign_splits 组不跨集断言通过（split 步内硬校验）",
        },
        "ac5_synthetic": {
            "source": "synthetic/manifest.json（stage2_synth_batch.py 产物，T1a 渲染管线只读复用）",
            "samples": len(synth),
            "pinned_group": SYNTH_GROUP,
            "splits_landed": dict(Counter(s.split for s in synth_recs)),
            "in_test": sum(1 for s in synth_recs if s.split == "test"),
        },
        "ac4_yolo": {
            "root": "final/yolo",
            "dataset_yaml": "final/yolo/dataset.yaml",
            "names_literal_check": names_check,
            "per_split": yolo_splits,
            "polygon_caliber": "T1a 实例包络（归一化，cls 恒 2=sfx）",
            "train_builder": "train/val 经 TrainingSetBuilder（不可读 test/challenge）；test/challenge 独立导出路径",
            "excluded_negative_ids": yolo_stats.get("builder_excluded_negative_ids", []),
        },
        "kept_pseudo_dispositions": {
            "replay_pages": list(REPLAY_CASE_IDS),
            "negative_evidence_zero_box": "保持 pseudo（T1a schema 负证据样本）",
            "no_positive_verdict": "保持 pseudo 不入正集",
        },
        "artifacts_sha256": {},
    }
    for rel in ["preannotate/manifest.json", "worksheet/worksheet.json", "worksheet/worksheet.md",
                "judgments/user-residual.json", "final/manifest.r1.json", "final/manifest.train.json",
                "final/manifest.val.json", "final/manifest.test.json", "final/manifest.challenge.json",
                "final/yolo/dataset.yaml", "final/yolo/_export_stats.json"]:
        p = OUT_DIR / rel
        summary["artifacts_sha256"][rel] = sha256_file(p) if p.is_file() else None

    atomic_write_json(SUMMARY_JSON, summary)

    # Git 内摘要：不写本机绝对路径（沿 T1a r1 P2-13 惯例）
    git_summary = json.loads(json.dumps(summary))  # deep copy
    git_summary["data_root_gitignored"] = "training_data/sfx-v1/annotate-r1/（repo 同级 gitignored 外部树；本摘要内路径均相对该根）"
    git_summary["yolo_layout"] = {
        "images": "final/yolo/images/{train,val,test}/（challenge 空集未导出）",
        "labels": "final/yolo/labels/{train,val,test}/（YOLO seg 归一化多边形，cls=2）",
        "stem_rule": "sample_id 中 '/' 替换为 '__'（synth-r1/synth-… → synth-r1__synth-…）",
    }
    atomic_write_json(GIT_SUMMARY, git_summary)
    print(f"[summary] wrote {SUMMARY_JSON}")
    print(f"[summary] wrote {GIT_SUMMARY}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True,
                        choices=["backfill", "manifest", "split", "yolo", "summary", "all"])
    args = parser.parse_args()
    steps = [args.step] if args.step != "all" else ["backfill", "manifest", "split", "yolo", "summary"]
    for s in steps:
        rc = {"backfill": cmd_backfill, "manifest": cmd_manifest, "split": cmd_split,
              "yolo": cmd_yolo, "summary": cmd_summary}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
