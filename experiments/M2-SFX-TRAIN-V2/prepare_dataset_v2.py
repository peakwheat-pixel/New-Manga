"""M2-SFX-TRAIN-V2 AC1 数据准备：own-manga 冻结池接入 + train-v2 重切 + 数据集重建。

沿 V1 prepare_dataset.py（experiments/M2-SFX-TRAIN-V1/，只读蓝本）模式复制适配。
与 V1 的差异（T2 Task 合同 AC1 + 用户指令 2026-10-05 按 ingest_notes 步骤 1-3）：

- 底册 = R2 final/manifest.{r2,train,val,test,challenge}.json（351 样本，只读引用，
  出厂态交叉核对沿 V1）+ own-manga 入册包（外部树 task-envs/sfx-synth-exp/
  own-manga-ingest/own_manga_manifest_records.json，558 页/1738 框，只读）：
  抽 3 条先行 from_dict+validate，再全量 558 条断言 0 错误（T1a schema 只读 import）。
- 组级指派 = **选项 A：T1a assign_splits(force=True, pinned=…) 函数参数传参重算**
  （不改 T1a splits.py 交付物；登记理由：合同 AC1 指定 pinned 走函数参数；R2 出厂
  lock.method=group-hash-rank-v2(assign_splits)+seed=20261004 冻结 → 重算可复现
  R2 出厂分桶，同时实证 pinned 的组隔离语义——若非目标组出现任何漂移即 fail-fast）。
  pinned 表：synthetic/annotate-r1→train（沿 R2 先例）、densho810/vol05→challenge
  （沿 V1 考卷不变）、own-manga/{v01,v02s,v12,v13,v15,v16}→train（ingest_notes
  建议 1，六组全钉）；其余组交算法（实测 349/349 零漂移复现 R2 出厂）。
- 断言：考卷零重叠（own-manga 六组与 densho810 组名/样本 id 无交集 + 558 vs 351
  页图 sha256 全量零碰撞）；validate 558/558；组隔离全量 0 违例；期望分集
  train 901 页/2304 框、val 4/53、test 2/5、challenge 2/5（合同 AC1；V1 实测
  train=566 框为底数，566+1738=2304；合同括号「629」为笔误，如实登记）。
- 产物 = training_data/sfx-v1/train-v2/：manifest.train-v2.json + 四分集 manifest
  + dataset/{images,labels}/{train,val,test,challenge}/ + dataset.yaml。
- 图像：R2 351 从 R2 yolo 树复制（素材根 fallback，沿 V1）；own-manga 558 从
  record.image.path（material_root=sfx-synth-exp 绝对路径，.jpg）复制。
  copy2+文件大小全量断言；sha256 抽验：R2 侧 BJ 5 页必验+每 split 前 3（沿 V1），
  own 侧每卷 1 张共 6 张（≥ask 要求 5 张，三方 dst==源==manifest.image.sha256）。
- labels 从 manifest.boxes 重建（R2 同款归一化口径，cls 恒 2）；R2 351 与 R2 树
  原分集同名 label 逐字节交叉比对（重切不动框几何）；own-manga 无出厂对照树，
  走导出后自洽校验（行数==框数/cls/坐标域全量）。
- names 双通道校验 + ultralytics check_det_dataset 扫描冒烟沿 V1（训练 venv
  M2-SFX-FINETUNE-gpu-py312，ultralytics 8.4.172；管线 venv 无 ultralytics）；
  扫描断言扩展为四分集目录图像计数（901/4/2/2）。
- challenge 考卷逐框溯源 R2 判定链沿 V1（judgments 只读）。

纪律：零 src（生产 SFX_CLASS_MAP 经 sys.path 只读 import）；R1/R2 数据树与脚本、
T1a 模块、own-manga 入册包只读；数据本体落 training_data/（repo gitignored），
Git 只进摘要（verification/M2-SFX-TRAIN-V2/prepare-summary.json）。

步骤（--step）：reassign → yolo → summary（all 依序全跑）。
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

from sfx_data_infra.atomicio import atomic_write_json, write_manifest  # noqa: E402
from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import SampleRecord  # noqa: E402
from sfx_data_infra.splits import (  # noqa: E402
    CHALLENGE_CASE_IDS,
    SEED_DEFAULT,
    assign_splits,
    split_fingerprint,
)

# 生产类表只读 import（零 src：不改动，仅读取常量）。
# 来源 src/infrastructure/providers/detection_sfx.py:137
#   SFX_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
from infrastructure.providers.detection_sfx import SFX_CLASS_MAP  # noqa: E402

R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
R2_ANNOTATE = R2_WORKTREE / "training_data" / "sfx-v1" / "annotate-r2"
R2_FINAL = R2_ANNOTATE / "final"
R2_YOLO = R2_FINAL / "yolo"
R2_JUDG = R2_ANNOTATE / "judgments"

OWN_INGEST_DIR = Path(r"G:/CODEX/New Manga.task-envs/sfx-synth-exp/own-manga-ingest")
OWN_PACKAGE = OWN_INGEST_DIR / "own_manga_manifest_records.json"

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "train-v2"
YAML_DIR = OUT_DIR / "dataset"
SUMMARY_JSON = OUT_DIR / "export-summary.json"
GIT_SUMMARY = REPO_ROOT / "verification" / "M2-SFX-TRAIN-V2" / "prepare-summary.json"

SEED = SEED_DEFAULT  # 20261004（沿 T1a/R1/R2/V1，seed 冻结）
CHALLENGE_GROUP = "densho810/vol05"  # 沿 V1 考卷不变（用户裁决 2026-10-04「按推荐」②(a)）
SYNTH_GROUP = "synthetic/annotate-r1"  # R2 pinned train（保持不变）
OWN_GROUPS = tuple(f"own-manga/{v}" for v in ("v01", "v02s", "v12", "v13", "v15", "v16"))
# 组级钉扎表（选项 A：assign_splits pinned= 函数参数，不改 T1a splits.py 交付物）
PINNED: dict[str, str] = {
    SYNTH_GROUP: "train",
    CHALLENGE_GROUP: "challenge",
    **{g: "train" for g in OWN_GROUPS},
}
# 挑战考卷预期成员（沿 V1 裁决落点；不符即 fail-fast 如实报，不凑数）
EXPECTED_CHALLENGE = {"pre-bj17": ("BJ17", 2, "vol05_p0167"), "pre-bj18": ("BJ18", 3, "vol05_p0065")}
# train 剩余 BJ 正集预期（6 框真实正样本）
EXPECTED_TRAIN_BJ = {"pre-bj16": 3, "pre-bj23": 2, "pre-bj24": 1}
KEEP_VERDICTS = ("confirm", "correct")
CLS_SFX_ID = next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx")

# 合同 AC1 期望分集（页级样本数, 框数）——不符即 fail-fast 如实报，不凑数。
# 底数核对：V1 实测 train=343 页/566 框（V1 prepare-summary.json），566+1738=2304；
# 合同括号「629+1738 框」中 629 为笔误（2304 与「约 2304 框」自洽），honest_notes 登记。
EXPECTED_SPLITS: dict[str, tuple[int, int]] = {
    "train": (901, 2304),
    "val": (4, 53),
    "test": (2, 5),
    "challenge": (2, 5),
}
# own-manga 交接数字核对（ingest_notes.md 分组页数；总页/框=合同与包 record/box_count）
EXPECTED_OWN_PAGES = {"own-manga/v01": 125, "own-manga/v02s": 103, "own-manga/v12": 88,
                      "own-manga/v13": 105, "own-manga/v15": 53, "own-manga/v16": 84}
EXPECTED_OWN_TOTAL = (558, 1738)
# own-manga annotation_status 分级快照（ingest_notes：partial 140 / pseudo 418）
ANNOTATION_GRADE_EXPECTED = {"partial": 140, "pseudo": 418}

# ultralytics 冒烟默认训练 venv（--ultralytics-python 可覆盖）
TRAIN_VENV_DEFAULT = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/Scripts/python.exe")

_state: dict = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 底册装载：R2 出厂态交叉核对（沿 V1）+ own-manga 入册包校验（抽 3 + 全量 558）
# ---------------------------------------------------------------------------


def _load_r2_split_maps() -> tuple[dict[str, str], dict]:
    """读 R2 四分集 manifest → {sample_id: r2_split} + 交叉核对出厂态（沿 V1）。"""
    r2_container = _read_json(R2_FINAL / "manifest.r2.json")
    r2_samples = r2_container["samples"]
    r2_fp = (r2_container.get("lock") or {}).get("fingerprint")
    by_id = {s["sample_id"]: s for s in r2_samples}
    if len(by_id) != len(r2_samples):
        raise ValueError("R2 全量 manifest 内 sample_id 重复")
    if r2_container["sample_count"] != len(r2_samples):
        raise ValueError("R2 全量 sample_count 与 samples 长度不一致")

    maps: dict[str, str] = {}
    fps = set()
    total = 0
    for sp in ("train", "val", "test", "challenge"):
        cont = _read_json(R2_FINAL / f"manifest.{sp}.json")
        ids = [s["sample_id"] for s in cont["samples"]]
        total += cont["sample_count"]
        if cont.get("fingerprint"):
            fps.add(cont["fingerprint"])
        for sid in ids:
            if by_id[sid]["split"] != sp:
                raise ValueError(f"{sid}: 分集文件 {sp} 与样本 split={by_id[sid]['split']} 不一致")
            if sid in maps:
                raise ValueError(f"{sid}: 出现在多个 R2 分集 manifest（泄漏）")
            maps[sid] = sp
        expect_ids = sorted(s["sample_id"] for s in r2_samples if s["split"] == sp)
        if sorted(ids) != expect_ids:
            raise ValueError(f"R2 {sp} 分集成员与全量 manifest 不一致")
    if total != len(r2_samples) or len(r2_samples) != 351:
        raise ValueError(f"R2 四分集样本数加和 {total} != 全量 {len(r2_samples)} != 351")
    if fps != {r2_fp}:
        raise ValueError(f"R2 四分集指纹不一致: {fps} vs lock {r2_fp}")
    return maps, r2_container


def _load_r2_verdict_map() -> dict[str, dict]:
    """沿 R2 load_final_verdicts：judgments 全量装载 → {unit_id: {verdict, reviewer}}。"""
    cons = _read_json(R2_JUDG / "consensus.json")["consensus"]
    div = _read_json(R2_JUDG / "divergence.json")["divergence"]
    arb: list[dict] = []
    for p in sorted(R2_JUDG.glob("arbiter/batch-*.json")):
        arb.extend(_read_json(p)["judgments"])

    vmap: dict[str, dict] = {}
    for c in cons:
        vmap[c["id"]] = {"verdict": c["verdict"], "reviewer": "codex+agy-consensus"}
    arb_by_id = {j["id"]: j for j in arb}
    for d in div:
        j = arb_by_id.get(d["id"])
        if j is None:
            raise ValueError(f"divergence 单元 {d['id']} 无对应仲裁判定")
        vmap[d["id"]] = {"verdict": j["verdict"], "reviewer": "arbiter"}
    unused = sorted(set(arb_by_id) - {d["id"] for d in div})
    if unused:
        raise ValueError(f"仲裁判定含 divergence 之外的单元: {unused}")
    units = _read_json(R2_JUDG / "units.json")["units"]
    if set(vmap) != {u["id"] for u in units}:
        raise ValueError("judgments vmap 与 units.json 覆盖不一致")
    return vmap


def _load_own_records() -> tuple[list[SampleRecord], dict]:
    """装载 own-manga 入册包：抽 3 条先行 → 全量 558 from_dict+validate 0 错误。

    包级断言：record/box_count、六组页数（ingest_notes 交接数字）、总框数加和、
    status 分级快照（partial/pseudo）、split 全 unassigned、包内页图 sha256 无重复、
    558 页图全部在盘（material_root 指 sfx-synth-exp，image.path 绝对路径）。
    """
    container = _read_json(OWN_PACKAGE)
    for key in ("schema_version", "material_root", "record_count", "box_count",
                "generated_at", "records"):
        if key not in container:
            raise ValueError(f"own-manga 入册包缺顶层字段 {key}")
    if container["schema_version"] != "sfx-data-infra/sample@1":
        raise ValueError(f"包 schema_version={container['schema_version']!r} != sfx-data-infra/sample@1")
    raw = container["records"]
    if container["record_count"] != len(raw):
        raise ValueError(f"包 record_count={container['record_count']} != records 长度 {len(raw)}")

    def _from_dict_checked(m: dict, tag: str) -> SampleRecord:
        rec = SampleRecord.from_dict(m)  # 内嵌 validate，失败抛 SchemaError
        errors = rec.validate()  # 防御性再验（应为空）
        if errors:
            raise AssertionError(f"{tag} {rec.sample_id}: validate 残留错误 {errors}")
        return rec

    # 抽 3 条先行（sample_id sorted 前 3，确定性抽样；ask 要求）
    sample3 = sorted(raw, key=lambda m: m["sample_id"])[:3]
    sample3_detail = []
    for m in sample3:
        rec = _from_dict_checked(m, "抽样")
        sample3_detail.append({
            "sample_id": rec.sample_id, "group": rec.group,
            "annotation_status": rec.annotation_status, "boxes": len(rec.boxes),
            "image_on_disk": Path(rec.image.path).is_file(),
            "image_sha256_head": rec.image.sha256[:8],
        })
    print(f"[own] 抽样 3 条（sample_id sorted 前 3）from_dict+validate 全过: "
          f"{json.dumps(sample3_detail, ensure_ascii=False)}")

    # 全量 558
    records: list[SampleRecord] = []
    for i, m in enumerate(raw):
        records.append(_from_dict_checked(m, f"records[{i}]"))
    if len(records) != EXPECTED_OWN_TOTAL[0]:
        raise AssertionError(f"own-manga 样本数 {len(records)} != 期望 {EXPECTED_OWN_TOTAL[0]}")
    total_boxes = sum(len(r.boxes) for r in records)
    if total_boxes != EXPECTED_OWN_TOTAL[1]:
        raise AssertionError(f"own-manga 总框数 {total_boxes} != 期望 {EXPECTED_OWN_TOTAL[1]}")
    if container["box_count"] != EXPECTED_OWN_TOTAL[1]:
        raise AssertionError(f"包 box_count={container['box_count']} != {EXPECTED_OWN_TOTAL[1]}")

    pages = Counter(r.group for r in records)
    if dict(pages) != EXPECTED_OWN_PAGES:
        raise AssertionError(f"own-manga 分组页数 {dict(pages)} != 交接数字 {EXPECTED_OWN_PAGES}")
    if {r.group for r in records} != set(OWN_GROUPS):
        raise AssertionError(f"own-manga 组集合 {sorted({r.group for r in records})} != {sorted(OWN_GROUPS)}")
    status = Counter(r.annotation_status for r in records)
    if dict(status) != ANNOTATION_GRADE_EXPECTED:
        raise AssertionError(f"own-manga status 分级 {dict(status)} != 交接 {ANNOTATION_GRADE_EXPECTED}")
    bad_split = [r.sample_id for r in records if r.split != "unassigned"]
    if bad_split:
        raise AssertionError(f"own-manga 包内 split 非 unassigned: {bad_split[:5]}")
    sha_seen: dict[str, str] = {}
    for r in records:
        if r.image.sha256 in sha_seen:
            raise AssertionError(f"own-manga 包内页图 sha256 重复: {r.sample_id} vs {sha_seen[r.image.sha256]}")
        sha_seen[r.image.sha256] = r.sample_id
    missing = [r.sample_id for r in records if not Path(r.image.path).is_file()]
    if missing:
        raise FileNotFoundError(f"own-manga 页图不在盘 {len(missing)} 张，例: {missing[:5]}")
    meta = {
        "package": OWN_PACKAGE,
        "package_sha256": sha256_file(OWN_PACKAGE),
        "material_root": container["material_root"],
        "generated_at": container["generated_at"],
        "record_count": container["record_count"],
        "box_count": container["box_count"],
        "pages_by_group": dict(sorted(pages.items())),
        "boxes_by_group": {g: sum(len(r.boxes) for r in records if r.group == g)
                           for g in sorted(OWN_GROUPS)},
        "status": dict(status),
        "validate": {"total": len(records), "errors": 0, "sample3": sample3_detail},
    }
    print(f"[own] 全量 {len(records)}/{len(records)} from_dict+validate 0 错误; "
          f"boxes={total_boxes}; groups={dict(pages)}; status={dict(status)}; 页图全在盘")
    return records, meta


# ---------------------------------------------------------------------------
# reassign：R2 出厂态 + own-manga 校验 → assign_splits pinned 重算 → 断言 → 落盘
# ---------------------------------------------------------------------------


def cmd_reassign() -> int:
    r2_split, r2_container = _load_r2_split_maps()
    vmap = _load_r2_verdict_map()
    r2_records: list[SampleRecord] = []
    for m in r2_container["samples"]:
        rec = SampleRecord.from_dict(m)
        errors = rec.validate()
        if errors:
            raise ValueError(f"{rec.sample_id}: schema 校验失败 {errors}")
        r2_records.append(rec)
    own_records, own_meta = _load_own_records()

    # ---- 防御：T1a 挑战单列规则（BJ13/14/15）在本集零命中（沿 V1 语义：BJ13/14/15
    #      仍 pseudo 不在 351；own-manga 为 external_model 无 case_id）----
    rule_hits = [s.sample_id for s in r2_records + own_records
                 if s.provenance.get("case_id") in CHALLENGE_CASE_IDS
                 or s.provenance.get("challenge") is True]
    if rule_hits:
        raise AssertionError(f"挑战单列规则意外命中 {rule_hits}（预期零命中）；人工裁决后再跑")

    # ---- 选项 A：assign_splits(force=True, pinned=PINNED) 全量 909 重算 ----
    all_records = r2_records + own_records
    group_split = assign_splits(all_records, seed=SEED, force=True, pinned=dict(PINNED))

    # 断言 A1（复现）：R2 非 vol05 组 349 样本 split 与出厂逐样本一致（零漂移）
    drift = [(s.sample_id, r2_split[s.sample_id], s.split) for s in r2_records
             if s.group != CHALLENGE_GROUP and s.split != r2_split[s.sample_id]]
    if drift:
        raise AssertionError(
            f"assign_splits 重算对 R2 非 vol05 组产生 {len(drift)} 处漂移（预期 0）："
            f"{drift[:10]}；出厂态与重算不符，fail-fast（不静默改走手动重指派）")
    # 断言 A2（迁移）：densho810/vol05 组 train→challenge 恰 2 样本（沿 V1 考卷）
    moved = sorted(s.sample_id for s in r2_records
                   if s.group == CHALLENGE_GROUP and r2_split[s.sample_id] == "train"
                   and s.split == "challenge")
    expected_moved = sorted(EXPECTED_CHALLENGE)
    if moved != expected_moved:
        raise AssertionError(f"vol05 组迁移成员 {moved} != 裁决预期 {expected_moved}")
    # 断言 A3（pinned 语义）：own-manga 六组全 train
    own_by_split = Counter(s.split for s in own_records)
    if set(own_by_split) != {"train"} or own_by_split["train"] != len(own_records):
        raise AssertionError(f"own-manga 未全落 train: {dict(own_by_split)}（pinned 语义违例）")
    # 断言 A4（合成组仍全 train，沿 V1）
    synth_splits = Counter(s.split for s in all_records if s.annotation_status == "synthetic")
    if set(synth_splits) - {"train"}:
        raise AssertionError(f"合成样本落入非 train split: {dict(synth_splits)}")

    # ---- 断言 B：challenge 恰 2 样本 5 框，逐框可溯源 R2 判定链（沿 V1）----
    challenge = sorted((s for s in all_records if s.split == "challenge"), key=lambda x: x.sample_id)
    if [s.sample_id for s in challenge] != expected_moved:
        raise AssertionError(f"challenge 成员 {[s.sample_id for s in challenge]} != {expected_moved}")
    challenge_boxes = 0
    trace = []
    for s in challenge:
        case, n_box, page = EXPECTED_CHALLENGE[s.sample_id]
        if s.provenance.get("case_id") != case:
            raise AssertionError(f"{s.sample_id}: case_id={s.provenance.get('case_id')} != {case}")
        if not str(s.image.path).replace("\\", "/").endswith(page + ".png"):
            raise AssertionError(f"{s.sample_id}: 图像页不符 {s.image.path}")
        if len(s.boxes) != n_box:
            raise AssertionError(f"{s.sample_id}: 框数 {len(s.boxes)} != {n_box}")
        meta = s.provenance.get("boxes_meta") or []
        if len(meta) != len(s.boxes):
            raise AssertionError(f"{s.sample_id}: boxes_meta {len(meta)} 与 boxes 索引失配")
        st2 = s.provenance.get("stage2r2") or {}
        if st2.get("action") != "completed":
            raise AssertionError(f"{s.sample_id}: stage2r2.action={st2.get('action')!r} != completed")
        for i, (b, bm) in enumerate(zip(s.boxes, meta)):
            uid = f"R2-{case}-B{i:02d}"
            if bm.get("unit_id") != uid:
                raise AssertionError(f"{s.sample_id} 框{i}: unit_id={bm.get('unit_id')} != {uid}")
            if bm.get("verdict") not in KEEP_VERDICTS:
                raise AssertionError(f"{uid}: verdict={bm.get('verdict')} 不在保留判定 {KEEP_VERDICTS}")
            src = vmap.get(uid)
            if src is None:
                raise AssertionError(f"{uid}: R2 judgments 判定源中无此单元（溯源断链）")
            if src["verdict"] != bm["verdict"]:
                raise AssertionError(f"{uid}: manifest verdict={bm['verdict']} != 判定源 {src['verdict']}")
            if b.cls != "sfx":
                raise AssertionError(f"{uid}: cls={b.cls!r} != 'sfx'")
            challenge_boxes += 1
            trace.append({"sample_id": s.sample_id, "case_id": case, "page": page,
                          "unit_id": uid, "conf": bm.get("conf"), "verdict": bm["verdict"],
                          "reviewer": bm.get("reviewer")})
    if challenge_boxes != 5:
        raise AssertionError(f"challenge 总框数 {challenge_boxes} != 5（BJ17×2+BJ18×3）")
    for s in challenge:
        st2 = s.provenance["stage2r2"]
        for ex in st2.get("excluded_delete_boxes", []):
            src = vmap.get(ex["unit_id"])
            if src is None or src["verdict"] != "delete":
                raise AssertionError(f"{s.sample_id} 排除框 {ex['unit_id']} 与判定源不符")
            if ex.get("verdict") != "delete":
                raise AssertionError(f"{s.sample_id} 排除留痕 verdict 异常: {ex}")

    # ---- 断言 C：train 剩 BJ 正集 = BJ16×3+BJ23×2+BJ24×1=6 框（沿 V1）----
    train_bj = {s.sample_id: len(s.boxes) for s in all_records
                if s.split == "train" and s.group.startswith("densho810/")}
    if train_bj != EXPECTED_TRAIN_BJ:
        raise AssertionError(f"train 剩 BJ 正集 {train_bj} != 预期 {EXPECTED_TRAIN_BJ}")
    for sid in train_bj:
        s = next(x for x in all_records if x.sample_id == sid)
        for i, bm in enumerate(s.provenance.get("boxes_meta") or []):
            if bm.get("verdict") not in KEEP_VERDICTS:
                raise AssertionError(f"{sid} 框{i}: verdict={bm.get('verdict')} 非保留判定")
    for sid in ("pre-bj22", "pre-bj25"):
        if any(s.sample_id == sid for s in all_records):
            raise AssertionError(f"{sid}: pseudo 负证据页混入训练 manifest")
    base = _read_json(R2_ANNOTATE / "preannotate" / "manifest.r2.json")
    neg_evidence = {}
    for m in base["samples"] if isinstance(base, dict) else base:
        if m["sample_id"] in ("pre-bj22", "pre-bj25"):
            st2 = m["provenance"].get("stage2r2") or {}
            neg_evidence[m["sample_id"]] = {
                "group": m["group"], "status": m["annotation_status"],
                "candidate_boxes_kept_out": len(m["boxes"]),
                "stage2r2_action": st2.get("action"),
                "note": ("BJ22：候选框 conf<0.2 未入本轮判定范围，无判定单元，保持 pseudo"
                         "（候选框留底册非零框）" if m["sample_id"] == "pre-bj22" else
                         "BJ25：唯一候选框判 delete，零框负证据留痕"),
            }
    if set(neg_evidence) != {"pre-bj22", "pre-bj25"}:
        raise AssertionError(f"R2 底册缺 BJ22/BJ25: {sorted(neg_evidence)}")

    # ---- 断言 D：考卷零重叠（own-manga 与 densho810 异源 + 页图 sha256 零碰撞）----
    own_groups = {s.group for s in own_records}
    densho_groups = {s.group for s in r2_records if s.group.startswith("densho810/")}
    if not own_groups.isdisjoint(densho_groups):
        raise AssertionError(f"组名交集非空: {own_groups & densho_groups}")
    if any(not g.startswith("own-manga/") for g in own_groups):
        raise AssertionError(f"own-manga 组前缀异常: {own_groups}")
    own_ids = {s.sample_id for s in own_records}
    r2_ids = {s.sample_id for s in r2_records}
    if own_ids & r2_ids:
        raise AssertionError(f"样本 id 交集非空: {sorted(own_ids & r2_ids)[:5]}")
    own_sha = {s.image.sha256 for s in own_records}
    r2_sha = {s.image.sha256 for s in r2_records}
    sha_overlap = own_sha & r2_sha
    if sha_overlap:
        raise AssertionError(f"页图 sha256 碰撞 {len(sha_overlap)} 张: {sorted(sha_overlap)[:5]}")
    challenge_pages = {s.image.sha256: s.sample_id for s in challenge}
    leaked = sorted(set(challenge_pages) & own_sha)
    if leaked:
        raise AssertionError(f"challenge 考卷页图出现在 own-manga: {leaked}")

    # ---- 断言 E：组隔离全量 0 违例（909 样本 group→set(split) 重算）----
    by_group_split: dict[str, set[str]] = {}
    for s in all_records:
        by_group_split.setdefault(s.group, set()).add(s.split)
    cross = {g: sorted(sp) for g, sp in by_group_split.items() if len(sp) > 1}
    if cross:
        raise AssertionError(f"组跨集违例: {cross}")
    if any("challenge" in sp and sp != {"challenge"} for sp in by_group_split.values()):
        raise AssertionError("存在组同时落 challenge 与其他 split")

    # ---- 断言 F：期望分集数字（合同 AC1；不符 fail-fast 如实报，不凑数）----
    by_split = Counter(s.split for s in all_records)
    boxes_by_split: Counter = Counter()
    for s in all_records:
        boxes_by_split[s.split] += len(s.boxes)
    for sp, (es, eb) in EXPECTED_SPLITS.items():
        actual = (by_split.get(sp, 0), boxes_by_split.get(sp, 0))
        if actual != (es, eb):
            raise AssertionError(
                f"分集 {sp} 实测 {actual[0]} 页/{actual[1]} 框 != 合同期望 {es}/{eb}；"
                "底数与合同不符，fail-fast（如实报，不凑数）")

    fingerprint = split_fingerprint(all_records, SEED)

    lock = {
        "seed": SEED,
        "method": ("group-hash-rank-v2（T1a splits.assign_splits(force=True, pinned=…) "
                   "函数参数传参，不改 T1a 交付物）+ own-manga 六组全钉 train"),
        "pinned_groups": dict(sorted(PINNED.items())),
        "pinned_note": ("选项 A 登记理由：合同 AC1 指定 pinned 走 assign_splits 函数参数；"
                        "R2 出厂 lock.method=group-hash-rank-v2+seed 冻结 → pinned 重算在非 "
                        "目标组 349/349 逐样本零漂移复现 R2 出厂（断言 A1），同时实证 pinned "
                        "组隔离语义；vol05 组 train→challenge 沿 V1 考卷不变"),
        "fingerprint": fingerprint,
        "frozen_at": now_iso(),
        "challenge_group": CHALLENGE_GROUP,
        "challenge_members": moved,
        "challenge_note": (
            "challenge=densho810/vol05 组（沿 V1 考卷不变）：pre-bj17（BJ17，vol05_p0167，"
            "2 框）+ pre-bj18（BJ18，vol05_p0065，3 框）=5 框考卷；own-manga 六组与 "
            "densho810 异源异页（组名/id/页图 sha256 三层零重叠断言通过），结构性无泄漏。"
            "同组 pre-bj25（pseudo 零框负证据）不在训练 manifest，未来转正按组不跨集"
            "自动入 challenge。BJ13/14/15（T1a CHALLENGE_CASE_IDS）仍 pseudo 不在本 "
            "manifest，挑战单列规则本集零命中，无成员冲突。"
        ),
        "own_manga_ingest": {
            "package": str(OWN_PACKAGE),
            "package_sha256": own_meta["package_sha256"],
            "material_root": own_meta["material_root"],
            "record_count": own_meta["record_count"],
            "box_count": own_meta["box_count"],
            "groups": own_meta["pages_by_group"],
            "license": "source=user-own-manga（2026-10-04 用户裁决备案）",
            "isolation": "训练运行期间不改已集成 manifest；本包独立文件（ingest_notes 步骤 3）",
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest(OUT_DIR / "manifest.train-v2.json", all_records, seed=SEED, extra={"lock": lock})
    for sp in ("train", "val", "test", "challenge"):
        subset = [s for s in all_records if s.split == sp]
        write_manifest(
            OUT_DIR / f"manifest.{sp}.json",
            subset,
            seed=SEED,
            extra={"split": sp, "fingerprint": fingerprint},
        )

    _state.update({
        "records": all_records,
        "own_ids": own_ids,
        "r2_split": r2_split,
        "fingerprint": fingerprint,
        "moved": moved,
        "trace": trace,
        "neg_evidence": neg_evidence,
        "by_split": dict(by_split),
        "boxes_by_split": dict(boxes_by_split),
        "group_split": group_split,
        "own_meta": own_meta,
        "own_sha": own_sha,
        "r2_sha_count": len(r2_sha),
        "drift_count": len(drift),
    })
    print(f"[reassign] by_split={json.dumps(dict(by_split), ensure_ascii=False)} "
          f"boxes={json.dumps(dict(boxes_by_split), ensure_ascii=False)} "
          f"(R2 出厂: train 345/val 4/test 2/challenge 0)")
    print(f"[reassign] moved={moved} drift_non_vol05=0 own_train={own_by_split['train']} "
          f"train_bj_left={train_bj} (6 框)")
    print(f"[reassign] 零重叠: 组交集=0 id交集=0 页sha交集=0 (own {len(own_sha)} vs r2 "
          f"{len(r2_sha)}); group_isolation_violations=0; fingerprint={fingerprint}")
    return 0


# ---------------------------------------------------------------------------
# yolo：YOLO seg 树重建（图像复制+label 重建+R2 逐字节交叉比对+双通道+可扫描断言）
# ---------------------------------------------------------------------------


def _yolo_stem(sample_id: str) -> str:
    return sample_id.replace("/", "__")


def _r2_tree_image(sid: str, orig_split: str) -> Path | None:
    stem = _yolo_stem(sid)
    d = R2_YOLO / "images" / orig_split
    for ext in (".png", ".jpg", ".jpeg"):
        p = d / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def _copy_image(s: SampleRecord, orig_split: str | None) -> tuple[Path, Path | None]:
    """复制图像到新树：R2 样本优先 R2 yolo 树（素材根 fallback，沿 V1）；
    own-manga 样本从 record.image.path（material_root 绝对路径）。返回 (dst, r2_src|None)。"""
    r2_src = None
    if orig_split is not None:
        src = _r2_tree_image(s.sample_id, orig_split)
        r2_src = src
        if src is None:
            src = Path(s.image.path)
            if not src.is_absolute() or not src.is_file():
                raise FileNotFoundError(f"{s.sample_id}: 素材根亦无图 {s.image.path}")
    else:
        src = Path(s.image.path)
        if not src.is_absolute() or not src.is_file():
            raise FileNotFoundError(f"{s.sample_id}: own-manga 页图不在盘 {s.image.path}")
    ext = src.suffix.lower()
    dst = YAML_DIR / "images" / s.split / f"{_yolo_stem(s.sample_id)}{ext}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_size != src.stat().st_size:
        shutil.copy2(src, dst)
    if dst.stat().st_size != src.stat().st_size:
        raise AssertionError(f"{s.sample_id}: 复制后大小失配 {dst.name}")
    return dst, r2_src


def _export_label(s: SampleRecord) -> int:
    """沿 R2 口径重建 label（cls 恒 2、归一化 6 位小数、点数>=3）。返回框数。"""
    lbl_dir = YAML_DIR / "labels" / s.split
    lbl_dir.mkdir(parents=True, exist_ok=True)
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
    (lbl_dir / f"{_yolo_stem(s.sample_id)}.txt").write_text(
        "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return len(lines)


def _write_dataset_yaml() -> Path:
    lines = [
        "# M2-SFX-TRAIN-V2 YOLO seg dataset（training_data/sfx-v1/train-v2/dataset）",
        f"# 生成：{now_iso()} ｜ T2-V2 AC1（own-manga 冻结池接入 558 页 + R2 351 重切；"
        "用户指令 2026-10-05 按 ingest_notes 步骤 1-3）",
        "# names 顺序逐字 = SFX_CLASS_MAP（src/infrastructure/providers/detection_sfx.py:137，"
        "T0 P3-6 硬约束；双通道校验：脚本读回断言 + pyyaml 独立解析 + ultralytics 扫描冒烟）",
        "# 底册=R2 final/manifest.r2.json 351（challenge=densho810/vol05 组划拨沿 V1）"
        "+ own-manga 冻结池 558 页/1738 框（六组全钉 train，assign_splits pinned= 传参）",
        "# train 901（324 合成+19 R2 真实+558 own-manga）；val 4/test 2/challenge 2 沿 R2/V1 不变",
        "# 多边形 = T1a 实例包络口径（非字形像素 mask）；cls 恒 2=sfx（本轮唯一 GT 类）",
        "# own-manga 框坐标=模型输出（chiqui7）未手工收紧；边界见 verification 摘要 honest_notes",
        f"# seed={SEED} 冻结（沿 R1/R2/V1 口径）；指纹与判定链见 manifest.train-v2.json lock",
        # path 用绝对路径（正斜杠）：ultralytics 扫描器与 cwd 无关（沿 V1）
        f"path: {YAML_DIR.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "# challenge：非空（densho810/vol05 组 2 页 5 框考卷）→ 写键",
        "challenge: images/challenge",
        "names:",
    ]
    for k in sorted(SFX_CLASS_MAP):
        lines.append(f"  {k}: {SFX_CLASS_MAP[k]}")
    yaml_path = YAML_DIR / "dataset.yaml"
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def _assert_names_literal_channel1(yaml_path: Path) -> dict:
    """通道 1：写后读回断言（R2/V1 同款手写解析器；与生产 detection_sfx.py:436 同形态）。"""
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
    for key in ("train", "val", "test", "challenge"):
        if not raw.get(key):
            raise AssertionError(f"pyyaml: {key} 键缺失（challenge 本轮非空必须写键）")
    return {"parsed": {str(k): v for k, v in names.items()},
            "expected_literal": {str(k): v for k, v in expected.items()},
            "parser": f"pyyaml {yaml.__version__}", "assert": "PASS"}


_ULTRA_SNIPPET = r"""
import json, sys
from pathlib import Path
from ultralytics.data.utils import check_det_dataset
yaml_path = Path(sys.argv[1]).resolve()
d = check_det_dataset(yaml_path, autodownload=False)
base = yaml_path.parent
ch = d.get("challenge")
ch_path = Path(str(ch))
if not ch_path.is_absolute():
    ch_path = (base / ch_path)

def _count(p):
    q = Path(str(p))
    if not q.is_absolute():
        q = base / q
    return len([x for x in q.iterdir() if x.suffix.lower() in (".png", ".jpg", ".jpeg")]) if q.is_dir() else 0

out = {
    "names": {str(k): v for k, v in d["names"].items()},
    "nc": d.get("nc"),
    "train_exists": Path(str(d.get("train"))).exists(),
    "val_exists": Path(str(d.get("val"))).exists(),
    "test_exists": Path(str(d.get("test"))).exists(),
    "challenge_value": str(ch),
    "challenge_dir_exists": ch_path.exists(),
    "dir_image_counts": {"train": _count(d.get("train")), "val": _count(d.get("val")),
                         "test": _count(d.get("test")), "challenge": _count(ch)},
}
print("__ULTRA_RESULT__" + json.dumps(out, ensure_ascii=False))
"""


def _assert_ultralytics_scannable(ultra_python: str | None, yaml_path: Path,
                                  expect_counts: dict[str, int]) -> dict:
    """ultralytics check_det_dataset 官方扫描冒烟（训练 venv 子进程、只读）。"""
    if not ultra_python:
        return {"assert": "NOT_RUN",
                "note": "未提供 --ultralytics-python；管线 venv 无 ultralytics，如实登记"}
    cmd = [ultra_python, "-c", _ULTRA_SNIPPET, str(yaml_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          timeout=300, cwd=str(YAML_DIR))
    if proc.returncode != 0:
        raise AssertionError(
            "ultralytics check_det_dataset 冒烟失败（EXIT!=0）：\n"
            f"stdout={proc.stdout[-2000:]}\nstderr={proc.stderr[-2000:]}")
    line = next((ln for ln in proc.stdout.splitlines() if ln.startswith("__ULTRA_RESULT__")), None)
    if line is None:
        raise AssertionError(f"ultralytics 冒烟无结果行：{proc.stdout[-2000:]}")
    out = json.loads(line[len("__ULTRA_RESULT__"):])
    expected_names = {str(k): v for k, v in SFX_CLASS_MAP.items()}
    if out["names"] != expected_names:
        raise AssertionError(f"ultralytics 解析 names 漂移: {out['names']}")
    if out.get("nc") != len(SFX_CLASS_MAP):
        raise AssertionError(f"ultralytics nc={out.get('nc')} != {len(SFX_CLASS_MAP)}")
    for key in ("train_exists", "val_exists", "test_exists", "challenge_dir_exists"):
        if not out[key]:
            raise AssertionError(f"ultralytics 扫描: {key}=False（目录不可扫描）")
    for sp, n in expect_counts.items():
        got = out["dir_image_counts"].get(sp)
        if got != n:
            raise AssertionError(f"ultralytics 扫描: {sp} 目录图像数 {got} != {n}")
    out["assert"] = "PASS"
    out["ultralytics_python"] = str(ultra_python)
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
    stats: list[dict] = []
    copied: dict[str, str] = {}
    sha_verified: list[str] = []
    own_sha_verified: list[str] = []
    label_crosscheck = {"checked": 0, "mismatch": [],
                        "scope": ("R2 351 全量与 R2 yolo 树原分集同名 label 逐字节比对"
                                  "（重切不动框几何）；own-manga 无出厂对照树，"
                                  "走导出后自洽校验")}

    # 抽验集合：R2 侧 BJ 5 页必验 + 每 split（R2 子集）stem sorted 前 3（沿 V1 政策）
    must_verify = {sid for sid in ("pre-bj16", "pre-bj17", "pre-bj18", "pre-bj23", "pre-bj24")}
    for sp, subset in by_split.items():
        r2_subset = [s for s in subset if s.sample_id not in own_ids]
        stems = sorted(_yolo_stem(s.sample_id) for s in r2_subset)
        for st in stems[:3]:
            sid = next(s.sample_id for s in r2_subset if _yolo_stem(s.sample_id) == st)
            must_verify.add(sid)
    # own-manga 抽验：每卷 1 张（组内 sample_id sorted 首 1）共 6 张（≥ask 要求 5 张）
    must_verify_own: set[str] = set()
    for g in OWN_GROUPS:
        grp = sorted((s for s in records if s.group == g), key=lambda x: x.sample_id)
        if grp:
            must_verify_own.add(grp[0].sample_id)

    for sp in ("train", "val", "test", "challenge"):
        subset = sorted(by_split.get(sp, []), key=lambda x: x.sample_id)
        n_boxes = 0
        for s in subset:
            orig = None if s.sample_id in own_ids else r2_split[s.sample_id]
            dst, r2_src = _copy_image(s, orig)
            copied[s.sample_id] = f"images/{sp}/{dst.name}"
            n_boxes += _export_label(s)
            # R2 351：label 逐字节交叉比对（与 R2 树原分集同名文件）
            if orig is not None:
                r2_lbl = R2_YOLO / "labels" / orig / f"{_yolo_stem(s.sample_id)}.txt"
                new_lbl = YAML_DIR / "labels" / sp / f"{_yolo_stem(s.sample_id)}.txt"
                if not r2_lbl.is_file():
                    raise AssertionError(f"{s.sample_id}: R2 树无对照 label {r2_lbl}")
                label_crosscheck["checked"] += 1
                if r2_lbl.read_bytes() != new_lbl.read_bytes():
                    label_crosscheck["mismatch"].append(s.sample_id)
            # sha256 抽验（dst == 源 == manifest 素材 sha）
            if s.sample_id in must_verify:
                digest = sha256_file(dst)
                src_ref = r2_src if r2_src else Path(s.image.path)
                if digest != sha256_file(src_ref):
                    raise AssertionError(f"{s.sample_id}: 抽验 dst sha256 != 源")
                if digest != s.image.sha256:
                    raise AssertionError(f"{s.sample_id}: 抽验 dst sha256 != manifest.image.sha256")
                sha_verified.append(s.sample_id)
            if s.sample_id in must_verify_own:
                digest = sha256_file(dst)
                if digest != sha256_file(Path(s.image.path)):
                    raise AssertionError(f"{s.sample_id}: own 抽验 dst sha256 != 源")
                if digest != s.image.sha256:
                    raise AssertionError(f"{s.sample_id}: own 抽验 dst sha256 != manifest.image.sha256")
                own_sha_verified.append(s.sample_id)
        stats.append({"split": sp, "images": len(subset), "boxes": n_boxes})
    if label_crosscheck["mismatch"]:
        raise AssertionError(f"label 交叉比对失配: {label_crosscheck['mismatch'][:10]}")
    if len(own_sha_verified) != len(must_verify_own):
        raise AssertionError(f"own 抽验覆盖不全: {len(own_sha_verified)}/{len(must_verify_own)}")

    yaml_path = _write_dataset_yaml()
    names_check = {
        "channel1_readback": _assert_names_literal_channel1(yaml_path),
        "channel2_pyyaml": _assert_names_literal_channel2(yaml_path),
    }
    ultra_check = _assert_ultralytics_scannable(
        ultra_python, yaml_path,
        {sp: st["images"] for sp, st in zip((s["split"] for s in stats), stats)})

    # 导出后校验（R2/V1 同款，扩至 own-manga 全量 909）：images/labels 数、stem 0 失配、
    # cls、坐标域、行数==manifest 框数（own-manga 自洽校验在此落实）
    stem_mismatch_total = 0
    for st in stats:
        sp = st["split"]
        if not st["images"]:
            continue
        lbls = sorted((YAML_DIR / "labels" / sp).glob("*.txt"))
        imgs = sorted(p for p in (YAML_DIR / "images" / sp).iterdir()
                      if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
        if len(lbls) != len(imgs) or len(lbls) != st["images"]:
            raise AssertionError(f"{sp}: images/labels 数不一致 {len(imgs)}/{len(lbls)} vs {st['images']}")
        mismatch = sorted({p.stem for p in lbls} ^ {p.stem for p in imgs})
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
    print(f"[yolo] names 双通道: channel1=PASS channel2={names_check['channel2_pyyaml']['parser']}")
    print(f"[yolo] ultralytics 扫描: {ultra_check.get('assert')} "
          f"dir_counts={ultra_check.get('dir_image_counts')}")
    print(f"[yolo] label 逐字节交叉比对: checked={label_crosscheck['checked']} mismatch=0")
    print(f"[yolo] sha256 抽验: R2 侧 {len(sha_verified)} 张（BJ 5 页必验+每 split 前 3）"
          f" + own 侧 {len(own_sha_verified)} 张（每卷 1 张）")
    print(f"[yolo] stem_mismatch_total={stem_mismatch_total}")
    (YAML_DIR / "_export_stats.json").write_text(
        json.dumps({"generated_at_utc": now_iso(), "seed": SEED,
                    "fingerprint": _state["fingerprint"], "splits": stats,
                    "names_check": names_check, "ultralytics_scan": ultra_check,
                    "label_crosscheck_vs_r2": {**label_crosscheck, "assert": "PASS"},
                    "sha256_spot_check": {
                        "r2_verified": sorted(sha_verified),
                        "r2_policy": "BJ 5 页必验 + 每 split（R2 子集）stem sorted 前 3",
                        "own_verified": sorted(own_sha_verified),
                        "own_policy": "每卷 1 张（组内 sample_id sorted 首 1）共 6 张（≥ask 要求 5 张）；三方一致（dst==源==manifest.image.sha256）"},
                    "stem_mismatch_total": stem_mismatch_total,
                    "copied_images": copied}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    _state["yolo_stats"] = stats
    _state["names_check"] = names_check
    _state["ultra_check"] = ultra_check
    _state["sha_verified"] = sorted(sha_verified)
    _state["own_sha_verified"] = sorted(own_sha_verified)
    return 0


# ---------------------------------------------------------------------------
# summary：数据树内 export-summary + Git 内摘要（相对路径 + sha256 + honest_notes）
# ---------------------------------------------------------------------------


def cmd_summary() -> int:
    records = _state["records"]
    own_ids = _state["own_ids"]
    by_split: dict[str, list[SampleRecord]] = {}
    for s in records:
        by_split.setdefault(s.split, []).append(s)

    def split_detail(sp: str) -> dict:
        subset = by_split.get(sp, [])
        return {
            "samples": len(subset),
            "boxes": sum(len(s.boxes) for s in subset),
            "real": sum(1 for s in subset if s.annotation_status == "complete"),
            "partial": sum(1 for s in subset if s.annotation_status == "partial"),
            "pseudo": sum(1 for s in subset if s.annotation_status == "pseudo"),
            "synthetic": sum(1 for s in subset if s.annotation_status == "synthetic"),
            "groups": sorted({s.group for s in subset}),
            "images": len({s.image.sha256 for s in subset}),
        }

    morph = {
        "pre-bj17": "竖排毛笔假名（ヒチヤ类）粗笔艺术字（R2-BJ17-B00/B01 consensus rationale）",
        "pre-bj18": "竖排/斜置粗毛笔片假名（サッ类）艺术字（R2-BJ18-B00/B01/B02 consensus rationale）",
    }
    challenge_detail = [{**t, "morphology": morph[t["sample_id"]]} for t in _state["trace"]]

    bj_train_left = [
        {"sample_id": s.sample_id, "group": s.group, "boxes": len(s.boxes),
         "units": [b.get("unit_id") for b in (s.provenance.get("boxes_meta") or [])]}
        for s in sorted(by_split["train"], key=lambda x: x.sample_id)
        if s.group.startswith("densho810/")
    ]
    own_meta = _state["own_meta"]

    summary = {
        "task": "M2-SFX-TRAIN-V2 AC1 数据准备（own-manga 冻结池接入 + train-v2 重切 + 数据集重建）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-TRAIN-V2/prepare_dataset_v2.py --step all",
        "directive": "用户指令 2026-10-05：own-manga 冻结池按 ingest_notes 步骤 1-3 接入并重训 V2",
        "base_manifest": {
            "source": "M2-SFX-ANNOTATE-R2 final/manifest.{r2,train,val,test,challenge}.json（只读）",
            "r2_fingerprint": "564498e13651bb2e7baba7540e7fd088e7ab17ff5fed438df4c4c162e525ccfa",
            "r2_by_split": {"train": 345, "val": 4, "test": 2, "challenge": 0},
            "crosscheck": "四分集数量加和=351=全量；成员与 split 字段一致；指纹同值",
        },
        "own_manga_ingest": {
            "package": str(OWN_PACKAGE),
            "package_sha256": own_meta["package_sha256"],
            "material_root": own_meta["material_root"],
            "generated_at": own_meta["generated_at"],
            "record_count": own_meta["record_count"],
            "box_count": own_meta["box_count"],
            "pages_by_group": own_meta["pages_by_group"],
            "boxes_by_group": own_meta["boxes_by_group"],
            "annotation_status": own_meta["status"],
            "validate": own_meta["validate"],
            "images_on_disk": "558/558 在盘（.jpg，六卷抽验+全量存在性断言）",
            "license": "source=user-own-manga（2026-10-04 用户裁决备案，ingest_notes）",
        },
        "reassign": {
            "method": ("选项 A：T1a assign_splits(force=True, pinned=…) 函数参数传参对全量 909 "
                       "重算（不改 T1a splits.py 交付物）。登记理由：合同 AC1 指定 pinned 走函数"
                       "参数；R2 出厂 lock.method=group-hash-rank-v2+seed=20261004 冻结 → 重算"
                       "可复现 R2 出厂分桶，同时实证 pinned 组隔离语义"),
            "pinned_groups": dict(sorted({
                "synthetic/annotate-r1": "train",
                "densho810/vol05": "challenge",
                **{g: "train" for g in OWN_GROUPS},
            }.items())),
            "moved": _state["moved"],
            "drift_non_vol05": _state["drift_count"],
            "drift_check": "R2 非 vol05 组 349 样本 split 与出厂逐样本一致（零漂移断言通过）",
            "own_train": _state["by_split"].get("train", 0) - 343,
            "group_isolation_violations": 0,
            "group_isolation_method": "全量 909 样本 group→set(split) 重算，违例=0 断言通过",
            "assign_group_split": _state["group_split"],
            "exam_zero_overlap": {
                "group_name_intersection": 0,
                "sample_id_intersection": 0,
                "page_sha256_intersection": 0,
                "scope": f"own-manga {len(_state['own_sha'])} 页 sha vs R2 {_state['r2_sha_count']} 页 sha 全量比对（含 challenge 考卷 2 页专项）",
                "assert": "PASS",
            },
        },
        "expected_vs_actual": {
            "expected_splits": {sp: {"samples": e[0], "boxes": e[1]}
                                for sp, e in EXPECTED_SPLITS.items()},
            "actual_splits": {sp: {"samples": _state["by_split"][sp],
                                   "boxes": _state["boxes_by_split"][sp]}
                              for sp in ("train", "val", "test", "challenge")},
            "note": ("合同 AC1 期望全数命中（fail-fast 断言通过）；合同括号「629+1738 框」中 "
                     "629 为笔误：V1 实测 train=566 框，566+1738=2304 与合同「约 2304 框」自洽"),
        },
        "splits": {sp: split_detail(sp) for sp in ("train", "val", "test", "challenge")},
        "challenge_dossier": {
            "group": CHALLENGE_GROUP,
            "samples": 2,
            "boxes": 5,
            "per_sample": {"pre-bj17": 2, "pre-bj18": 3},
            "pages": ["vol05_p0167.png", "vol05_p0065.png"],
            "per_box_trace": challenge_detail,
            "excluded_delete_boxes_traced": [
                {"unit_id": "R2-BJ17-B02", "verdict": "delete", "reviewer": "arbiter",
                 "note": "气泡对白非 SFX（仲裁判定），已在 pre-bj17 stage2r2 留痕并核对判定源"},
            ],
            "same_group_pseudo": ("pre-bj25（vol05 组，pseudo 零框负证据）不在训练 manifest；"
                                  "未来转正按组不跨集自动入 challenge"),
            "zero_overlap_vs_ownmanga": "考卷页图 sha256 与 own-manga 558 页零交集（断言通过）",
        },
        "train_bj_remaining": {
            "positive_boxes": 6,
            "detail": bj_train_left,
            "negative_evidence_not_in_manifest": _state["neg_evidence"],
        },
        "fingerprint": _state["fingerprint"],
        "fingerprint_method": "T1a splits.split_fingerprint（seed=20261004 + 全部 909 (sample_id, split) sha256，工具零重写复用）",
        "yolo": {
            "root": "training_data/sfx-v1/train-v2/dataset",
            "dataset_yaml": "training_data/sfx-v1/train-v2/dataset/dataset.yaml",
            "per_split": _state["yolo_stats"],
            "names_dual_channel_check": _state["names_check"],
            "ultralytics_scan": _state["ultra_check"],
            "label_crosscheck_vs_r2": "R2 351 全量与 R2 yolo 树原分集同名 label 逐字节相等（重切只动 split 归属、不动框几何）；own-manga 558 走导出后自洽校验（行数==框数/cls/坐标域）",
            "image_copy": {
                "source": ("R2 351：R2 final/yolo 树（出厂时已对素材根做过 sha256 复制校验），"
                           "素材根 fallback；own-manga 558：record.image.path"
                           "（material_root=sfx-synth-exp，.jpg）"),
                "full_check": "copy2 后 dst/src 文件大小逐张断言相等（909 张全量）",
                "sha256_spot_check": {
                    "r2_verified": _state["sha_verified"],
                    "r2_policy": "BJ 5 页必验 + 每 split（R2 子集）stem sorted 前 3；三方一致",
                    "own_verified": _state["own_sha_verified"],
                    "own_policy": "每卷 1 张共 6 张（≥ask 要求 5 张）；三方一致（dst==源==manifest.image.sha256）",
                },
            },
            "polygon_caliber": "T1a 实例包络（归一化 6 位小数，cls 恒 2=sfx）",
            "path_key_note": "dataset.yaml path 用绝对路径（沿 V1）：ultralytics 扫描器与 cwd 无关",
        },
        "honest_notes": [
            "own-manga 框坐标=模型输出（chiqui7/yolo11s-seg.onnx，0.1px）未手工收紧——定位"
            "精度受 chiqui7 上限约束；partial 140 页=用户核验 SFX 存在性（annotation_grade="
            "human-verified-existence）但框未手工收紧，不冒充 complete；pseudo 418 页=模型"
            "产出+AI 内容复核过滤，无逐框人工确认。标签噪声影响 V2 不做 partial/pseudo 分层"
            "消融（合同时间盒裁量），如实登记为边界。",
            "chiqui7 同源性边界（沿 ingest_notes）：own-manga 候选框全部源自 chiqui7 检出"
            "（AI 复核过滤假阳但覆盖不了 chiqui7 漏检类型）；chiqui7 弱项（毛笔竖排漏检）"
            "需独立补框通道，本包不覆盖；BJ 主攻形态（考卷 BJ17/18 竖排毛笔）不在本包覆盖内。",
            "考卷零重叠实证：own-manga 六组（own-manga/*）与 densho810 组异源异页，组名/样本 "
            "id/页图 sha256 三层零交集断言通过（558 vs 351 全量比对），challenge 考卷 2 页"
            "专项复核无泄漏。",
            "组级指派=选项 A（assign_splits pinned= 函数参数，不改 T1a splits.py）：重算对 "
            "R2 非 vol05 组 349/349 逐样本零漂移（复现 R2 出厂分桶），vol05 组 train→challenge "
            "恰 2 样本沿 V1 考卷不变，own-manga 六组全钉 train（ingest_notes 建议 1）。",
            "合同 AC1 括号「629+1738 框」中 629 为笔误：V1 实测 train=566 框（V1 "
            "prepare-summary.json），566+1738=2304 与合同「约 2304 框」自洽；本轮实测 "
            "train=901 页/2304 框与期望全数一致（fail-fast 断言通过，无凑数）。",
            "own-manga 558 页为 .jpg，与 R2 系 .png 混树（YOLO 按文件扫描，无影响）；"
            "own-manga pseudo 含空框页（负证据），label 导出为空文件（YOLO 背景图惯例）。",
            "v15 组改钉 val 的裁量（ingest_notes 建议 3）本轮不做（合同裁量点：val 保持 KO 4 "
            "样本不动，近域 val 归 T3）。",
            "627 个被复核剔除的误检框未入册（ingest_notes）；难负样本使用属显式决策，不默认掺入。",
            "ultralytics 可扫描断言在训练 venv（M2-SFX-FINETUNE-gpu-py312，ultralytics "
            "8.4.172）以 check_det_dataset 只读冒烟落实（四分集目录图像计数 901/4/2/2 断言）；"
            "管线 venv（T1.1.1-impl-py312）无 ultralytics。",
        ],
    }

    artifacts: dict[str, str | None] = {}
    for rel in ["training_data/sfx-v1/train-v2/manifest.train-v2.json",
                "training_data/sfx-v1/train-v2/manifest.train.json",
                "training_data/sfx-v1/train-v2/manifest.val.json",
                "training_data/sfx-v1/train-v2/manifest.test.json",
                "training_data/sfx-v1/train-v2/manifest.challenge.json",
                "training_data/sfx-v1/train-v2/dataset/dataset.yaml",
                "training_data/sfx-v1/train-v2/dataset/_export_stats.json"]:
        p = REPO_ROOT / rel
        artifacts[rel] = sha256_file(p) if p.is_file() else None
    summary["artifacts_sha256"] = artifacts

    atomic_write_json(SUMMARY_JSON, summary)
    git_summary = json.loads(json.dumps(summary))
    git_summary["data_root_gitignored"] = (
        "training_data/sfx-v1/train-v2/（repo gitignored 外部树，.gitignore:13 /training_data/）；"
        "own-manga 入册包在 task-envs 外部树（只读引用）；本摘要内 repo 相对路径均相对 "
        "G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V2-zcode")
    git_summary["yolo_layout"] = {
        "images": "training_data/sfx-v1/train-v2/dataset/images/{train,val,test,challenge}/",
        "labels": "training_data/sfx-v1/train-v2/dataset/labels/{train,val,test,challenge}/（YOLO seg 归一化多边形，cls=2）",
        "stem_rule": "sample_id 中 '/' 替换为 '__'（909 样本 id 均无 '/'，stem==sample_id）",
    }
    atomic_write_json(GIT_SUMMARY, git_summary)
    print(f"[summary] wrote {SUMMARY_JSON}")
    print(f"[summary] wrote {GIT_SUMMARY}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True,
                        choices=["reassign", "yolo", "summary", "all"])
    parser.add_argument("--ultralytics-python", default=str(TRAIN_VENV_DEFAULT),
                        help="训练 venv python 路径（ultralytics check_det_dataset 冒烟用；"
                             "默认 M2-SFX-FINETUNE-gpu-py312）")
    args = parser.parse_args()
    if not Path(args.ultralytics_python).is_file():
        args.ultralytics_python = None  # 训练 venv 不可达 → 冒烟 NOT_RUN 如实登记
    if args.step in ("yolo", "summary") and "records" not in _state:
        # 单步运行时先重建内存态（reassign 幂等，重复执行无副作用破坏）
        cmd_reassign()
    steps = [args.step] if args.step != "all" else ["reassign", "yolo", "summary"]
    for s in steps:
        rc = {"reassign": cmd_reassign, "yolo": lambda: cmd_yolo(args.ultralytics_python),
              "summary": cmd_summary}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    sys.exit(main())
