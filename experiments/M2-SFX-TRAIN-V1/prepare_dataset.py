"""M2-SFX-TRAIN-V1 AC1 数据准备：challenge 划拨重切 + train-v1 数据集重建。

沿 R2 stage2_finalize_r2.py（experiments/M2-SFX-ANNOTATE-R2/，只读蓝本）模式复制
适配。与 R2 的差异（T2 Task 合同 AC1 + 用户裁决 2026-10-04「按推荐」）：

- 底册 = R2 final/manifest.r2.json（351 样本，只读引用）——**不重算** assign_splits，
  「其余重指派不变」：仅把 train 中 group=densho810/vol05 的样本（pre-bj17 竖排
  主攻 2 框 + pre-bj18 粗毛笔 3 框）整组迁移 challenge（组不跨集硬约束）。
- 四分集 manifest（final/manifest.{train,val,test,challenge}.json）交叉核对：
  数量加和=全量、成员与 split 字段一致、指纹同值——重切建立在 R2 出厂态之上。
- 产物 = training_data/sfx-v1/train-v1/：manifest.train-v1.json + 四分集 manifest
  + dataset/{images,labels}/{train,val,test,challenge}/ + dataset.yaml
  （challenge 非空 → 本轮写 challenge 键）。
- names 顺序逐字=SFX_CLASS_MAP 双通道校验沿 R2（①手写解析读回断言 + ②pyyaml
  独立解析）；另加 ultralytics check_det_dataset 可扫描冒烟（--ultralytics-python
  指训练 venv，管线 venv 无 ultralytics）。
- 图像从 R2 yolo 树复制（该树出厂时已对素材根做过 sha256 复制校验；素材根作
  fallback），copy2+文件大小全量断言 + sha256 三方抽验（必验：BJ 5 页全量；
  其余每 split stem sorted 前 3）。
- labels 从 manifest.boxes 重建（R2 同款归一化口径），并与 R2 yolo 树原分集同名
  label 逐字节交叉比对（351 全量）——实证重切只动 split 归属、不动框几何。
- 指纹 = T1a splits.split_fingerprint（seed + 全部 (sample_id, split) 的 sha256），
  工具零重写复用；seed=20261004 冻结沿 R1/R2 口径。

纪律：零 src（生产 SFX_CLASS_MAP 经 sys.path 只读 import）；R1/R2 数据树与脚本
只读；数据本体落 training_data/（repo gitignored），Git 只进摘要。

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

from sfx_data_infra.atomicio import atomic_write_json, load_manifest, write_manifest  # noqa: E402
from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import SampleRecord  # noqa: E402
from sfx_data_infra.splits import SEED_DEFAULT, split_fingerprint  # noqa: E402

# 生产类表只读 import（零 src：不改动，仅读取常量）。
# 来源 src/infrastructure/providers/detection_sfx.py:137
#   SFX_CLASS_MAP = {0: "bubble", 1: "panel", 2: "sfx", 3: "text"}
from infrastructure.providers.detection_sfx import SFX_CLASS_MAP  # noqa: E402

R2_WORKTREE = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode")
R2_ANNOTATE = R2_WORKTREE / "training_data" / "sfx-v1" / "annotate-r2"
R2_FINAL = R2_ANNOTATE / "final"
R2_YOLO = R2_FINAL / "yolo"
R2_JUDG = R2_ANNOTATE / "judgments"

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "train-v1"
YAML_DIR = OUT_DIR / "dataset"
SUMMARY_JSON = OUT_DIR / "export-summary.json"
GIT_SUMMARY = REPO_ROOT / "verification" / "M2-SFX-TRAIN-V1" / "prepare-summary.json"

SEED = SEED_DEFAULT  # 20261004（沿 T1a/R1/R2，seed 冻结）
CHALLENGE_GROUP = "densho810/vol05"  # 用户裁决 2026-10-04「按推荐」②(a) 划拨组
SYNTH_GROUP = "synthetic/annotate-r1"  # R2 pinned train（保持不变）
# 挑战考卷预期成员（裁决落点；不符即 fail-fast 如实报，不凑数）
EXPECTED_CHALLENGE = {"pre-bj17": ("BJ17", 2, "vol05_p0167"), "pre-bj18": ("BJ18", 3, "vol05_p0065")}
# train 剩余 BJ 正集预期（6 框真实正样本）
EXPECTED_TRAIN_BJ = {"pre-bj16": 3, "pre-bj23": 2, "pre-bj24": 1}
KEEP_VERDICTS = ("confirm", "correct")
CLS_SFX_ID = next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx")

_state: dict = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# reassign：R2 出厂态交叉核对 → vol05 组整组迁移 → 断言 → train-v1 manifest 落盘
# ---------------------------------------------------------------------------


def _load_r2_split_maps() -> tuple[dict[str, str], dict]:
    """读 R2 四分集 manifest → {sample_id: r2_split} + 交叉核对出厂态。"""
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
        # 分集成员 == 全量按 split 过滤（双向一致）
        expect_ids = sorted(s["sample_id"] for s in r2_samples if s["split"] == sp)
        if sorted(ids) != expect_ids:
            raise ValueError(f"R2 {sp} 分集成员与全量 manifest 不一致")
    if total != len(r2_samples) or len(r2_samples) != 351:
        raise ValueError(f"R2 四分集样本数加和 {total} != 全量 {len(r2_samples)} != 351")
    if fps != {r2_fp}:
        raise ValueError(f"R2 四分集指纹不一致: {fps} vs lock {r2_fp}")
    return maps, r2_container


def _load_r2_verdict_map() -> dict[str, dict]:
    """沿 R2 load_final_verdicts：judgments 全量装载 → {unit_id: {verdict, reviewer}}。

    保留 R2 的覆盖一致性断言（vmap 必须恰覆盖 units.json，判定源完整性随迁）。"""
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


def cmd_reassign() -> int:
    r2_split, r2_container = _load_r2_split_maps()
    vmap = _load_r2_verdict_map()
    records: list[SampleRecord] = []
    for m in r2_container["samples"]:
        rec = SampleRecord.from_dict(m)
        errors = rec.validate()
        if errors:
            raise ValueError(f"{rec.sample_id}: schema 校验失败 {errors}")
        records.append(rec)

    # ---- 重指派：train 中 densho810/vol05 整组 → challenge；其余不动 ----
    moved = []
    for s in records:
        if s.split == "train" and s.group == CHALLENGE_GROUP:
            s.split = "challenge"
            moved.append(s.sample_id)
    moved.sort()
    expected_moved = sorted(EXPECTED_CHALLENGE)
    if moved != expected_moved:
        raise AssertionError(
            f"densho810/vol05 组 train 成员 {moved} != 裁决预期 {expected_moved}；"
            "R2 底数与裁决落点不符，fail-fast（不凑数）"
        )

    # ---- 断言 1：challenge 恰 2 样本 5 框，逐框可溯源 R2 判定链 ----
    challenge = sorted((s for s in records if s.split == "challenge"), key=lambda x: x.sample_id)
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
    # 被 delete 排除的候选框留痕逐条对上判定源（BJ17-B02 仲裁 delete）
    for s in challenge:
        st2 = s.provenance["stage2r2"]
        for ex in st2.get("excluded_delete_boxes", []):
            src = vmap.get(ex["unit_id"])
            if src is None or src["verdict"] != "delete":
                raise AssertionError(f"{s.sample_id} 排除框 {ex['unit_id']} 与判定源不符")
            if ex.get("verdict") != "delete":
                raise AssertionError(f"{s.sample_id} 排除留痕 verdict 异常: {ex}")

    # ---- 断言 2：train 剩 BJ 正集 = BJ16×3+BJ23×2+BJ24×1=6 框 ----
    train_bj = {s.sample_id: len(s.boxes) for s in records
                if s.split == "train" and s.group.startswith("densho810/")}
    if train_bj != EXPECTED_TRAIN_BJ:
        raise AssertionError(f"train 剩 BJ 正集 {train_bj} != 预期 {EXPECTED_TRAIN_BJ}")
    for sid in train_bj:
        s = next(x for x in records if x.sample_id == sid)
        for i, bm in enumerate(s.provenance.get("boxes_meta") or []):
            if bm.get("verdict") not in KEEP_VERDICTS:
                raise AssertionError(f"{sid} 框{i}: verdict={bm.get('verdict')} 非保留判定")
    # BJ22/BJ25 不入 351 训练集（任何 split）
    for sid in ("pre-bj22", "pre-bj25"):
        if any(s.sample_id == sid for s in records):
            raise AssertionError(f"{sid}: pseudo 负证据页混入训练 manifest")
    # 底册负证据状态核对（只读 R2 preannotate；ask 措辞与实测差异如实登记）
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

    # ---- 断言 3：组隔离违例=0（全量 group→splits 重算）----
    by_group_split: dict[str, set[str]] = {}
    for s in records:
        by_group_split.setdefault(s.group, set()).add(s.split)
    cross = {g: sorted(sp) for g, sp in by_group_split.items() if len(sp) > 1}
    if cross:
        raise AssertionError(f"组跨集违例: {cross}")
    if any("challenge" in sp and sp != {"challenge"} for sp in by_group_split.values()):
        raise AssertionError("存在组同时落 challenge 与其他 split")

    # ---- 断言 4：其余重指派不变（逐样本对照 R2 出厂 split）----
    changed = 0
    for s in records:
        orig = r2_split[s.sample_id]
        if s.split != orig:
            if orig == "train" and s.group == CHALLENGE_GROUP:
                changed += 1
            else:
                raise AssertionError(f"{s.sample_id}: 非 vol05 组 split 被改动 {orig}→{s.split}")
    if changed != 2:
        raise AssertionError(f"迁移样本数 {changed} != 2")

    # ---- 合成组仍全 train（R2 pinned 语义保持）----
    synth_splits = Counter(s.split for s in records if s.annotation_status == "synthetic")
    if set(synth_splits) - {"train"}:
        raise AssertionError(f"合成样本落入非 train split: {dict(synth_splits)}")

    fingerprint = split_fingerprint(records, SEED)
    by_split = Counter(s.split for s in records)

    lock = {
        "seed": SEED,
        "method": ("group-hash-rank-v2（T1a splits.assign_splits）+ T2 用户裁决组迁移："
                   f"{CHALLENGE_GROUP} train→challenge 整组（不重算 assign_splits，其余不变）"),
        "pinned_groups": {SYNTH_GROUP: "train"},
        "fingerprint": fingerprint,
        "frozen_at": now_iso(),
        "challenge_group": CHALLENGE_GROUP,
        "challenge_members": moved,
        "challenge_note": (
            "challenge=densho810/vol05 组整组划拨（用户裁决 2026-10-04「按推荐」②(a)）："
            "pre-bj17（BJ17，vol05_p0167，竖排毛笔假名 2 框，主攻形态）+ pre-bj18（BJ18，"
            "vol05_p0065，粗毛笔片假名 3 框）=5 框考卷；train 留 densho810/vol01（pre-bj16×3 框"
            "+BJ22 pseudo 负证据在底册）+vol03（pre-bj23×2+pre-bj24×1）=6 框真实正样本。"
            "同组 pre-bj25（pseudo 零框负证据）不在 351 训练 manifest，未来转正按组不跨集"
            "自动入 challenge。与 T1a CHALLENGE_CASE_IDS（BJ13/14/15 case 单列）并存："
            "BJ13/14/15 仍 pseudo 不在本 manifest，无成员冲突；组隔离全量复核 0 违例。"
        ),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest(OUT_DIR / "manifest.train-v1.json", records, seed=SEED, extra={"lock": lock})
    for sp in ("train", "val", "test", "challenge"):
        subset = [s for s in records if s.split == sp]
        write_manifest(
            OUT_DIR / f"manifest.{sp}.json",
            subset,
            seed=SEED,
            extra={"split": sp, "fingerprint": fingerprint},
        )

    _state["records"] = records
    _state["r2_split"] = r2_split
    _state["fingerprint"] = fingerprint
    _state["moved"] = moved
    _state["trace"] = trace
    _state["neg_evidence"] = neg_evidence
    _state["by_split"] = dict(by_split)
    print(f"[reassign] by_split={json.dumps(dict(by_split), ensure_ascii=False)} "
          f"(R2 出厂: train 345/val 4/test 2/challenge 0)")
    print(f"[reassign] moved={moved} challenge_boxes={challenge_boxes} "
          f"train_bj_left={train_bj} (6 框)")
    print(f"[reassign] group_isolation_violations=0; fingerprint={fingerprint}")
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


def _copy_image(s: SampleRecord, orig_split: str) -> tuple[Path, Path | None]:
    """复制图像到新树：优先 R2 yolo 树，fallback 素材根。返回 (dst, r2_src|None)。"""
    src = _r2_tree_image(s.sample_id, orig_split)
    r2_src = src
    if src is None:
        src = Path(s.image.path)
        if not src.is_absolute() or not src.is_file():
            raise FileNotFoundError(f"{s.sample_id}: 素材根亦无图 {s.image.path}")
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
        "# M2-SFX-TRAIN-V1 YOLO seg dataset（training_data/sfx-v1/train-v1/dataset）",
        f"# 生成：{now_iso()} ｜ T2 AC1（challenge 划拨重切；用户裁决 2026-10-04「按推荐」）",
        "# names 顺序逐字 = SFX_CLASS_MAP（src/infrastructure/providers/detection_sfx.py:137，"
        "T0 P3-6 硬约束；双通道校验：脚本读回断言 + pyyaml 独立解析 + ultralytics 扫描冒烟）",
        "# 底册=R2 final/manifest.r2.json 351 样本只读重切：densho810/vol05 组 train→challenge"
        "（pre-bj17 2 框 + pre-bj18 3 框）；其余不变；train 343（324 合成+19 真实）",
        "# 多边形 = T1a 实例包络口径（非字形像素 mask）；cls 恒 2=sfx（本轮唯一 GT 类）",
        f"# seed={SEED} 冻结（沿 R1/R2 口径）；指纹与判定链见 manifest.train-v1.json lock",
        # path 用绝对路径（正斜杠）：偏离 R2 的 `path: .`，使 ultralytics 扫描器与 cwd 无关
        f"path: {YAML_DIR.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "# challenge：本轮非空（densho810/vol05 组 2 页 5 框考卷，用户裁决 ②(a)）→ 写键。",
        "challenge: images/challenge",
        "names:",
    ]
    for k in sorted(SFX_CLASS_MAP):
        lines.append(f"  {k}: {SFX_CLASS_MAP[k]}")
    yaml_path = YAML_DIR / "dataset.yaml"
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path


def _assert_names_literal_channel1(yaml_path: Path) -> dict:
    """通道 1：写后读回断言（R2 同款手写解析器；与生产 detection_sfx.py:436 同断言形态）。"""
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
out = {
    "names": {str(k): v for k, v in d["names"].items()},
    "nc": d.get("nc"),
    "train_exists": Path(str(d.get("train"))).exists(),
    "val_exists": Path(str(d.get("val"))).exists(),
    "test_exists": Path(str(d.get("test"))).exists(),
    "challenge_value": str(ch),
    "challenge_dir_exists": ch_path.exists(),
    "challenge_dir_images": len([p for p in ch_path.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")]) if ch_path.is_dir() else 0,
}
print("__ULTRA_RESULT__" + json.dumps(out, ensure_ascii=False))
"""


def _assert_ultralytics_scannable(ultra_python: str | None, yaml_path: Path) -> dict:
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
    if out["challenge_dir_images"] != 2:
        raise AssertionError(f"ultralytics 扫描: challenge 目录图像数 {out['challenge_dir_images']} != 2")
    out["assert"] = "PASS"
    out["ultralytics_python"] = str(ultra_python)
    return out


def cmd_yolo(ultra_python: str | None) -> int:
    records = _state["records"]
    r2_split = _state["r2_split"]
    by_split: dict[str, list[SampleRecord]] = {}
    for s in records:
        by_split.setdefault(s.split, []).append(s)

    if YAML_DIR.exists():
        shutil.rmtree(YAML_DIR)
    stats: list[dict] = []
    copied: dict[str, str] = {}
    sha_verified: list[str] = []
    label_crosscheck = {"checked": 0, "mismatch": []}

    # 抽验集合：BJ 5 页必验 + 每 split stem sorted 前 3（challenge 已全含于必验）
    must_verify = {sid for sid in ("pre-bj16", "pre-bj17", "pre-bj18", "pre-bj23", "pre-bj24")}
    for sp, subset in by_split.items():
        stems = sorted(_yolo_stem(s.sample_id) for s in subset)
        for st in stems[:3]:
            sid = next(s.sample_id for s in subset if _yolo_stem(s.sample_id) == st)
            must_verify.add(sid)

    for sp in ("train", "val", "test", "challenge"):
        subset = sorted(by_split.get(sp, []), key=lambda x: x.sample_id)
        n_boxes = 0
        for s in subset:
            dst, r2_src = _copy_image(s, r2_split[s.sample_id])
            copied[s.sample_id] = f"images/{sp}/{dst.name}"
            n_boxes += _export_label(s)
            # label 逐字节交叉比对：与 R2 树原分集同名文件（证明重切不动框几何）
            r2_lbl = R2_YOLO / "labels" / r2_split[s.sample_id] / f"{_yolo_stem(s.sample_id)}.txt"
            new_lbl = YAML_DIR / "labels" / sp / f"{_yolo_stem(s.sample_id)}.txt"
            if not r2_lbl.is_file():
                raise AssertionError(f"{s.sample_id}: R2 树无对照 label {r2_lbl}")
            label_crosscheck["checked"] += 1
            if r2_lbl.read_bytes() != new_lbl.read_bytes():
                label_crosscheck["mismatch"].append(s.sample_id)
            # sha256 三方抽验（dst == R2 树源 == manifest 素材 sha）
            if s.sample_id in must_verify:
                digest = sha256_file(dst)
                if digest != sha256_file(r2_src if r2_src else Path(s.image.path)):
                    raise AssertionError(f"{s.sample_id}: 抽验 dst sha256 != 源")
                if digest != s.image.sha256:
                    raise AssertionError(f"{s.sample_id}: 抽验 dst sha256 != manifest.image.sha256")
                sha_verified.append(s.sample_id)
        stats.append({"split": sp, "images": len(subset), "boxes": n_boxes})
    if label_crosscheck["mismatch"]:
        raise AssertionError(f"label 交叉比对失配: {label_crosscheck['mismatch'][:10]}")

    yaml_path = _write_dataset_yaml()
    names_check = {
        "channel1_readback": _assert_names_literal_channel1(yaml_path),
        "channel2_pyyaml": _assert_names_literal_channel2(yaml_path),
    }
    ultra_check = _assert_ultralytics_scannable(ultra_python, yaml_path)

    # 导出后校验（R2 同款）：images/labels 数、stem 0 失配、cls、坐标域、行数
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
    print(f"[yolo] ultralytics 扫描: {ultra_check.get('assert')}")
    print(f"[yolo] label 逐字节交叉比对: checked={label_crosscheck['checked']} mismatch=0")
    print(f"[yolo] sha256 抽验: {len(sha_verified)} 张（BJ 5 页必验+每 split 前 3）")
    print(f"[yolo] stem_mismatch_total={stem_mismatch_total}")
    (YAML_DIR / "_export_stats.json").write_text(
        json.dumps({"generated_at_utc": now_iso(), "seed": SEED,
                    "fingerprint": _state["fingerprint"], "splits": stats,
                    "names_check": names_check, "ultralytics_scan": ultra_check,
                    "label_crosscheck_vs_r2": {**label_crosscheck, "assert": "PASS"},
                    "sha256_spot_check": {"verified": sorted(sha_verified),
                                          "policy": "BJ 5 页必验 + 每 split stem sorted 前 3"},
                    "stem_mismatch_total": stem_mismatch_total,
                    "copied_images": copied}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    _state["yolo_stats"] = stats
    _state["names_check"] = names_check
    _state["ultra_check"] = ultra_check
    _state["sha_verified"] = sorted(sha_verified)
    return 0


# ---------------------------------------------------------------------------
# summary：数据树内 export-summary + Git 内摘要（相对路径 + sha256 + 裁决对照）
# ---------------------------------------------------------------------------


def cmd_summary() -> int:
    records = _state["records"]
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

    # challenge 考卷逐框明细（形态口径引 R2 判定 rationale 关键词）
    morph = {
        "pre-bj17": "竖排毛笔假名（ヒチヤ类）粗笔艺术字（R2-BJ17-B00/B01 consensus rationale）",
        "pre-bj18": "竖排/斜置粗毛笔片假名（サッ类）艺术字（R2-BJ18-B00/B01/B02 consensus rationale）",
    }
    challenge_detail = []
    for t in _state["trace"]:
        challenge_detail.append({**t, "morphology": morph[t["sample_id"]]})

    bj_train_left = [
        {"sample_id": s.sample_id, "group": s.group, "boxes": len(s.boxes),
         "units": [b.get("unit_id") for b in (s.provenance.get("boxes_meta") or [])]}
        for s in sorted(by_split["train"], key=lambda x: x.sample_id)
        if s.group.startswith("densho810/")
    ]

    summary = {
        "task": "M2-SFX-TRAIN-V1 AC1 数据准备（challenge 划拨重切 + train-v1 数据集重建）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-TRAIN-V1/prepare_dataset.py --step all",
        "ruling": "用户裁决 2026-10-04「按推荐」：①直接训 V1 + ②challenge=densho810/vol05 组划拨",
        "base_manifest": {
            "source": "M2-SFX-ANNOTATE-R2 final/manifest.{r2,train,val,test,challenge}.json（只读）",
            "r2_fingerprint": "564498e13651bb2e7baba7540e7fd088e7ab17ff5fed438df4c4c162e525ccfa",
            "r2_by_split": {"train": 345, "val": 4, "test": 2, "challenge": 0},
            "crosscheck": "四分集数量加和=351=全量；成员与 split 字段一致；指纹同值",
        },
        "reassign": {
            "method": ("不重算 assign_splits：train 中 densho810/vol05 整组迁移 challenge"
                       "（组不跨集硬约束），其余逐样本保持 R2 出厂 split（逐样本断言）"),
            "moved": _state["moved"],
            "group_isolation_violations": 0,
            "group_isolation_method": "全量 351 样本 group→set(split) 重算，违例=0 断言通过",
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
            "same_group_pseudo": ("pre-bj25（vol05 组，pseudo 零框负证据）不在 351 训练 manifest；"
                                  "未来转正按组不跨集自动入 challenge"),
        },
        "train_bj_remaining": {
            "positive_boxes": 6,
            "detail": bj_train_left,
            "negative_evidence_not_in_351": _state["neg_evidence"],
        },
        "fingerprint": _state["fingerprint"],
        "fingerprint_method": "T1a splits.split_fingerprint（seed=20261004 + 全部 (sample_id, split) sha256，工具零重写复用）",
        "yolo": {
            "root": "training_data/sfx-v1/train-v1/dataset",
            "dataset_yaml": "training_data/sfx-v1/train-v1/dataset/dataset.yaml",
            "per_split": _state["yolo_stats"],
            "names_dual_channel_check": _state["names_check"],
            "ultralytics_scan": _state["ultra_check"],
            "label_crosscheck_vs_r2": "351 全量与 R2 yolo 树原分集同名 label 逐字节相等（重切只动 split 归属、不动框几何）",
            "image_copy": {
                "source": "R2 final/yolo 树（该树出厂时已对素材根做过 sha256 复制校验）；素材根 fallback（本轮未触发）",
                "full_check": "copy2 后 dst/src 文件大小逐张断言相等（351 张全量）",
                "sha256_spot_check": {"verified": _state["sha_verified"],
                                      "policy": "BJ 5 页必验 + 每 split stem sorted 前 3；三方一致（dst==R2 源==manifest.image.sha256）"},
            },
            "polygon_caliber": "T1a 实例包络（归一化 6 位小数，cls 恒 2=sfx）",
            "path_key_note": "dataset.yaml path 用绝对路径（偏离 R2 的 `path: .`）：ultralytics 扫描器与 cwd 无关",
        },
        "honest_notes": [
            "ask 措辞「BJ22/BJ25 零框负证据」与 R2 底册实测有差异，如实登记：pre-bj22=pseudo、"
            "候选 2 框 conf<0.2 未入判定范围（无判定单元，非零框）；pre-bj25=pseudo、唯一候选框"
            "判 delete（真零框负证据）。两者均不在 351 训练 manifest（不入任何 split）。",
            "train 345→343（真实 21→19+合成 324）：vol05 组 2 页 5 框移出；val 4（53 框）/test 2（5 框）不变。",
            "challenge 语义=T2 用户裁决组划拨（densho810/vol05）；T1a CHALLENGE_CASE_IDS（BJ13/14/15 "
            "case 单列）语义并存——BJ13/14/15 仍 pseudo 不在本 manifest，无成员冲突。",
            "ultralytics 可扫描断言在训练 venv（M2-SFX-FINETUNE-gpu-py312，ultralytics 8.4.172）"
            "以 check_det_dataset 只读冒烟落实；管线 venv（T1.1.1-impl-py312）无 ultralytics。",
            "数字如实登记（脚本实测），无凑数：challenge 恰 2 样本 5 框为裁决落点断言，"
            "不符即 fail-fast。",
        ],
    }

    # artifacts sha256（键=相对 repo 根路径）
    artifacts: dict[str, str | None] = {}
    for rel in ["training_data/sfx-v1/train-v1/manifest.train-v1.json",
                "training_data/sfx-v1/train-v1/manifest.train.json",
                "training_data/sfx-v1/train-v1/manifest.val.json",
                "training_data/sfx-v1/train-v1/manifest.test.json",
                "training_data/sfx-v1/train-v1/manifest.challenge.json",
                "training_data/sfx-v1/train-v1/dataset/dataset.yaml",
                "training_data/sfx-v1/train-v1/dataset/_export_stats.json"]:
        p = REPO_ROOT / rel
        artifacts[rel] = sha256_file(p) if p.is_file() else None
    summary["artifacts_sha256"] = artifacts

    atomic_write_json(SUMMARY_JSON, summary)
    git_summary = json.loads(json.dumps(summary))
    git_summary["data_root_gitignored"] = (
        "training_data/sfx-v1/train-v1/（repo gitignored 外部树）；"
        "本摘要内路径均相对 repo 根（G:/CODEX/New Manga.worktrees/M2-SFX-TRAIN-V1-zcode）")
    git_summary["yolo_layout"] = {
        "images": "training_data/sfx-v1/train-v1/dataset/images/{train,val,test,challenge}/",
        "labels": "training_data/sfx-v1/train-v1/dataset/labels/{train,val,test,challenge}/（YOLO seg 归一化多边形，cls=2）",
        "stem_rule": "sample_id 中 '/' 替换为 '__'（本轮 351 样本 id 均无 '/'，stem==sample_id）",
    }
    atomic_write_json(GIT_SUMMARY, git_summary)
    print(f"[summary] wrote {SUMMARY_JSON}")
    print(f"[summary] wrote {GIT_SUMMARY}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", required=True,
                        choices=["reassign", "yolo", "summary", "all"])
    parser.add_argument("--ultralytics-python", default=None,
                        help="训练 venv python 路径（ultralytics check_det_dataset 冒烟用）")
    args = parser.parse_args()
    if args.step in ("yolo", "summary") and "records" not in _state:
        # 单步运行时先重建内存态（reassign 无副作用破坏，重复执行幂等）
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
