"""M2-SFX-GATE-T3 AC2：train-v4 重切 + YOLO 数据集重建（沿 prepare_dataset_v2.py 模式）。

底册装载 = train-v3 全量 manifest（912，R3 出厂态只读引用）+ manifest.r4 新转正
BJ32-35 四页（complete，ai-direct-annotation）。BJ36/37 终裁零框留底册不入
（schema.py:88-89 + R2 pre-bj25 零框负证据先例）。

组级指派 = 选项 A：T1a assign_splits(force=True, pinned=…) 函数参数传参重算（不改
T1a 交付物；沿 V2/R3 先例）。pinned：synthetic/annotate-r1→train、densho810/vol05→
challenge（考卷组不变，vol05 组新转正页 BJ32 随组入 challenge——gate-definition
§4.G1「challenge 侧（含 vol05 组转正扩展框）」预见性表述；ask 表述「BJ26-37 钉
train」与 G3 组隔离硬门（challenge 仅 vol05 组+组原子性）冲突，按冻结 Gate 语义
执行并如实登记）、own-manga 六组→train。组 rank=sha256(seed:group) 只依赖组名，
新样本入已有组 → 非 vol05 组 349+ 零漂移（断言 A1）。

断言（G3 六断言 + 重切先例全收编）：
  A1 零漂移：train-v3 912 样本 split 重算后逐样本不变
  A2 challenge=pre-bj17/18/32 恰 3 页 8 框（2+3+3），仅 densho810/vol05 组
  A3 考卷原始 5 框坐标逐位=R2 final 出厂（BJ17×2+BJ18×3）
  A4 考卷零重叠三层：own vs densho810 组名/样本 id/页图 sha256 零交集
  A5 组隔离全量 0 违例（916 group→set(split)）
  A6 期望分集：train 907/2323、val 4/53、test 2/5、challenge 3/8（全量 916）
  A7 schema from_dict+validate 全量 0 错误；BJ32-35 框=manifest.r4 逐位一致
  A8 train-v3 共同样本框几何逐位不变（重切不动框几何）
  A9 own/synthetic 全 train（pinned 语义）
YOLO：train-v4/dataset/{images,labels}/{train,val,test,challenge}/+dataset.yaml；
  R3 912 从 R3 yolo 树复制+label 逐字节交叉比对；BJ32-35 从 image.path 复制+自洽
  校验；names 双通道（手写解析+pyyaml）+ultralytics check_det_dataset 扫描冒烟。
纪律：零 src；R1-R3 数据树与脚本、T1a 模块只读；数据落 training_data/（gitignored）。
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "experiments" / "M2-SFX-DATA-INFRA"))
sys.path.insert(0, str(REPO / "src"))
from sfx_data_infra.atomicio import write_manifest  # noqa: E402
from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import SampleRecord  # noqa: E402
from sfx_data_infra.splits import (  # noqa: E402
    SEED_DEFAULT, assign_splits, split_fingerprint,
)
from infrastructure.providers.detection_sfx import SFX_CLASS_MAP  # noqa: E402  （生产类表只读 import）

R3W = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R3-zcode")
R3_FULL = R3W / "training_data" / "sfx-v1" / "train-v3" / "manifest.train-v3.json"
R3_YOLO = R3W / "training_data" / "sfx-v1" / "train-v3" / "dataset"
R2_R2 = Path(r"G:/CODEX/New Manga.worktrees/M2-SFX-ANNOTATE-R2-zcode/training_data/sfx-v1/annotate-r2/final/manifest.r2.json")
R4M = REPO / "training_data" / "sfx-v1" / "annotate-r4" / "manifest.r4.json"

OUT_DIR = REPO / "training_data" / "sfx-v1" / "train-v4"
YAML_DIR = OUT_DIR / "dataset"
GIT_SUMMARY = REPO / "verification" / "M2-SFX-GATE-T3" / "prepare-train-v4-summary.json"

SEED = SEED_DEFAULT  # 20261004
CHALLENGE_GROUP = "densho810/vol05"
SYNTH_GROUP = "synthetic/annotate-r1"
OWN_GROUPS = tuple(f"own-manga/{v}" for v in ("v01", "v02s", "v12", "v13", "v15", "v16"))
PINNED: dict[str, str] = {
    SYNTH_GROUP: "train",
    CHALLENGE_GROUP: "challenge",
    **{g: "train" for g in OWN_GROUPS},
}
NEW_IDS = ("pre-bj32", "pre-bj33", "pre-bj34", "pre-bj35")
EXPECTED_CHALLENGE = {"pre-bj17": 2, "pre-bj18": 3, "pre-bj32": 3}
EXPECTED_SPLITS = {"train": (907, 2323), "val": (4, 53), "test": (2, 5), "challenge": (3, 8)}
EXPECTED_TOTAL = 916

TRAIN_VENV_DEFAULT = Path(r"G:/CODEX/New Manga.task-envs/M2-SFX-FINETUNE-gpu-py312/Scripts/python.exe")

_state: dict = {}


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _yolo_stem(sid: str) -> str:
    return sid.replace("/", "__")


def _poly_xyxy(b: dict) -> list[float]:
    p = b["polygon"]
    return [p[0][0], p[0][1], p[2][0], p[2][1]]


def cmd_reassign() -> int:
    r3_full = _read(R3_FULL)
    assert r3_full["sample_count"] == 912, f"train-v3 全量 {r3_full['sample_count']} != 912"
    r4 = _read(R4M)
    r4_by = {s["sample_id"]: s for s in r4}
    assert len(r4_by) == 94

    # 装载 912 + 4（BJ32-35 从 r4；split 置 unassigned 由 assign_splits 重算）
    raw = list(r3_full["samples"])
    seen = {m["sample_id"] for m in raw}
    for sid in NEW_IDS:
        assert sid not in seen
        m = dict(r4_by[sid])
        assert m["annotation_status"] == "complete" and len(m["boxes"]) > 0
        m["split"] = "unassigned"
        raw.append(m)
    assert len(raw) == EXPECTED_TOTAL

    records: list[SampleRecord] = []
    errors: list[str] = []
    for m in raw:
        rec = SampleRecord.from_dict(m)
        errors += [f"{rec.sample_id}: {e}" for e in rec.validate()]
        records.append(rec)
    assert not errors, f"schema 校验失败 {len(errors)}: {errors[:5]}"

    # A8：train-v3 共同样本框几何逐位不变（对照 train-v3 manifest 原貌）
    r3_by = {s["sample_id"]: s for s in r3_full["samples"]}
    drift_boxes = []
    for m in r3_full["samples"]:
        new = next(x for x in raw if x["sample_id"] == m["sample_id"])
        if json.dumps(m["boxes"], sort_keys=True) != json.dumps(new["boxes"], sort_keys=True):
            drift_boxes.append(m["sample_id"])
    assert not drift_boxes, f"重切动了框几何: {drift_boxes[:5]}"

    # A7b：BJ32-35 框=manifest.r4 逐位一致
    for sid in NEW_IDS:
        a = r4_by[sid]["boxes"]
        b = next(x for x in raw if x["sample_id"] == sid)["boxes"]
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), f"{sid} 框与 r4 不一致"

    v3_split = {s.sample_id: s.split for s in records if s.sample_id in r3_by}

    # 选项 A：pinned 重算
    assign_splits(records, seed=SEED, force=True, pinned=dict(PINNED))

    # A1 零漂移（train-v3 912 样本逐样本）
    drift = [(s.sample_id, v3_split[s.sample_id], s.split) for s in records
             if s.sample_id in v3_split and s.split != v3_split[s.sample_id]]
    assert not drift, f"重算对 train-v3 样本产生 {len(drift)} 漂移: {drift[:10]}"

    # A2 challenge 成员与框数
    chal = sorted((s for s in records if s.split == "challenge"), key=lambda x: x.sample_id)
    assert [s.sample_id for s in chal] == sorted(EXPECTED_CHALLENGE), \
        f"challenge 成员 {[s.sample_id for s in chal]}"
    for s in chal:
        assert len(s.boxes) == EXPECTED_CHALLENGE[s.sample_id]
        assert s.group == CHALLENGE_GROUP
    # A3 考卷 5 框逐位=R2 出厂
    r2_by = {s["sample_id"]: s for s in _read(R2_R2)["samples"]}
    for sid in ("pre-bj17", "pre-bj18"):
        new = next(s for s in records if s.sample_id == sid)
        old = r2_by[sid]
        assert len(new.boxes) == len(old["boxes"])
        for nb, ob in zip(new.boxes, old["boxes"]):
            assert [[round(v, 1) for v in pt] for pt in nb.polygon] == \
                   [[round(v, 1) for v in pt] for pt in ob["polygon"]], \
                f"{sid} 考卷框漂移"
    # A4 考卷零重叠三层
    own_recs = [s for s in records if s.group.startswith("own-manga/")]
    densho_recs = [s for s in records if s.group.startswith("densho810/")]
    assert {s.group for s in own_recs}.isdisjoint({s.group for s in densho_recs})
    assert not ({s.sample_id for s in own_recs} & {s.sample_id for s in densho_recs})
    assert not ({s.image.sha256 for s in own_recs} & {s.image.sha256 for s in densho_recs})
    # A5 组隔离
    by_group: dict[str, set] = {}
    for s in records:
        by_group.setdefault(s.group, set()).add(s.split)
    cross = {g: sorted(sp) for g, sp in by_group.items() if len(sp) > 1}
    assert not cross, f"组隔离违例: {cross}"
    # A9 pinned 语义
    for s in records:
        if s.group in PINNED:
            assert s.split == PINNED[s.group], f"{s.sample_id}: pinned {s.group}→{PINNED[s.group]} 违例"
    # A6 期望分集
    by_split = Counter(s.split for s in records)
    boxes_by_split: Counter = Counter()
    for s in records:
        boxes_by_split[s.split] += len(s.boxes)
    for sp, (es, eb) in EXPECTED_SPLITS.items():
        actual = (by_split.get(sp, 0), boxes_by_split.get(sp, 0))
        assert actual == (es, eb), f"分集 {sp} 实测 {actual} != 期望 {(es, eb)}"

    fp = split_fingerprint(records, SEED)
    lock = {
        "seed": SEED,
        "method": ("group-hash-rank-v2（T1a splits.assign_splits(force=True, pinned=…) 函数参数传参）"
                   "+ BJ32-35 转正并入（ai-direct-annotation 首例）+ own-manga 六组/synthetic 钉 train "
                   "+ vol05 组钉 challenge"),
        "pinned_groups": dict(sorted(PINNED.items())),
        "fingerprint": fp,
        "frozen_at": now_iso(),
        "challenge_group": CHALLENGE_GROUP,
        "challenge_members": [s.sample_id for s in chal],
        "challenge_note": (
            "challenge=densho810/vol05 组（考卷组不变）：pre-bj17（2 框 R2 出厂逐位）+"
            "pre-bj18（3 框 R2 出厂逐位）+pre-bj32（3 框 BJ 转正页随组入 challenge——"
            "gate-definition §4.G1 预见性表述「challenge 侧（含 vol05 组转正扩展框）」。"
            "G1 主判据数据=原始 5 框不变（BJ32 扩展框只入 directional 扩展集）。"
            "BJ37（同组转正判定零 SFX 0 框）因 schema.py:88-89 禁止 complete 空框、"
            "沿 pre-bj25 零框负证据先例保持 pseudo 不在本 manifest，如实登记。"),
        "bj32_37_pin_note": (
            "ask 表述「own/synthetic/BJ26-37 钉 train」中 BJ32/37 属 densho810/vol05 考卷组："
            "与 G3 组隔离硬门（challenge 仅 vol05 组+组原子性 0 违例）冲突，按 gate-definition "
            "v1.0 冻结语义执行——BJ32 随组入 challenge、BJ33-35（vol03 组）入 train、BJ36 "
            "（vol03 组）0 框留底册不入、BJ37（vol05 组）0 框留底册不入。G1 主判据 5 框不受影响。"),
        "ai_direct_annotation": {
            "mode": "ai-direct-annotation",
            "first_case": "R4-BJ32-35（R3-MISS 补画：无模型预标，双 AI 独立看图+IoU 比对+仲裁）",
            "boxes": sum(len(s.boxes) for s in records if s.sample_id in NEW_IDS),
            "ref": "training_data/sfx-v1/annotate-r4/judgments/（consensus+divergence+arbiter）",
        },
        "r3_base_ref": str(R3_FULL),
        "r4_base_ref": str(R4M),
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_manifest(OUT_DIR / "manifest.train-v4.json", records, seed=SEED, extra={"lock": lock})
    for sp in ("train", "val", "test", "challenge"):
        subset = [s for s in records if s.split == sp]
        write_manifest(OUT_DIR / f"manifest.{sp}.json", subset, seed=SEED,
                       extra={"split": sp, "fingerprint": fp})

    _state.update({"records": records, "fingerprint": fp, "lock": lock,
                   "by_split": dict(by_split), "boxes_by_split": dict(boxes_by_split),
                   "chal": [s.sample_id for s in chal]})
    print(f"[reassign] total=916 by_split={dict(by_split)} "
          f"boxes={dict(boxes_by_split)} drift=0 challenge={_state['chal']}")
    print(f"[reassign] fingerprint={fp}")
    return 0


def _copy_image(s: SampleRecord, r3_split: str | None) -> Path:
    if r3_split is not None:
        src = None
        for ext in (".png", ".jpg", ".jpeg"):
            p = R3_YOLO / "images" / r3_split / f"{_yolo_stem(s.sample_id)}{ext}"
            if p.is_file():
                src = p
                break
        if src is None:
            raise FileNotFoundError(f"{s.sample_id}: R3 yolo 树无图")
    else:
        src = Path(s.image.path)
        if not src.is_file():
            raise FileNotFoundError(f"{s.sample_id}: 素材图不在盘 {src}")
    dst = YAML_DIR / "images" / s.split / f"{_yolo_stem(s.sample_id)}{src.suffix.lower()}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists() or dst.stat().st_size != src.stat().st_size:
        shutil.copy2(src, dst)
    assert dst.stat().st_size == src.stat().st_size
    return dst


def _export_label(s: SampleRecord) -> int:
    lbl_dir = YAML_DIR / "labels" / s.split
    lbl_dir.mkdir(parents=True, exist_ok=True)
    w, h = s.image.width, s.image.height
    cls_id = next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx")
    lines = []
    for b in s.boxes:
        assert b.cls == "sfx"
        pts = []
        for x, y in b.polygon:
            nx, ny = min(max(x / w, 0.0), 1.0), min(max(y / h, 0.0), 1.0)
            pts.append(f"{nx:.6f} {ny:.6f}")
        assert len(pts) >= 3
        lines.append(f"{cls_id} " + " ".join(pts))
    (lbl_dir / f"{_yolo_stem(s.sample_id)}.txt").write_text(
        "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    return len(lines)


def _write_yaml() -> Path:
    lines = [
        "# M2-SFX-GATE-T3 train-v4 YOLO seg dataset（training_data/sfx-v1/train-v4/dataset）",
        f"# 生成：{now_iso()} ｜ T3 AC2（BJ32-35 转正 4 页 15 框 ai-direct-annotation 首例 + train-v3 912 重切）",
        "# names 顺序逐字 = SFX_CLASS_MAP（src/infrastructure/providers/detection_sfx.py:137）；双通道校验",
        "# 底册=train-v3 全量 912（R3 出厂零漂移重算）+ manifest.r4 BJ32-35 转正；BJ36/37 零框负证据留底册",
        "# challenge=densho810/vol05 组：pre-bj17×2+pre-bj18×3（R2 出厂逐位考卷）+pre-bj32×3（转正扩展）",
        f"# seed={SEED} 冻结；指纹见 manifest.train-v4.json lock",
        f"path: {YAML_DIR.as_posix()}",
        "train: images/train",
        "val: images/val",
        "test: images/test",
        "challenge: images/challenge",
        "names:",
    ]
    for k in sorted(SFX_CLASS_MAP):
        lines.append(f"  {k}: {SFX_CLASS_MAP[k]}")
    p = YAML_DIR / "dataset.yaml"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return p


def _names_channel1(p: Path) -> dict:
    parsed, in_names = {}, False
    for line in p.read_text(encoding="utf-8").splitlines():
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
    assert parsed == expected, f"names 通道1 漂移: {parsed!r}"
    assert [int(k) for k in parsed] == sorted(SFX_CLASS_MAP)
    return {"parsed": parsed, "assert": "PASS"}


def _names_channel2(p: Path) -> dict:
    import yaml
    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    expected = {int(k): v for k, v in SFX_CLASS_MAP.items()}
    assert raw.get("names") == expected, f"names 通道2 漂移: {raw.get('names')!r}"
    assert list(raw["names"].keys()) == sorted(expected)
    for key in ("train", "val", "test", "challenge"):
        assert raw.get(key), f"pyyaml: {key} 键缺失"
    return {"parsed": {str(k): v for k, v in raw["names"].items()},
            "parser": f"pyyaml {yaml.__version__}", "assert": "PASS"}


_ULTRA_SNIPPET = r"""
import json, sys
from pathlib import Path
from ultralytics.data.utils import check_det_dataset
yml = Path(sys.argv[1]).resolve()
d = check_det_dataset(yml, autodownload=False)
base = yml.parent
def _cnt(p):
    q = Path(str(p))
    if not q.is_absolute():
        q = base / q
    return len([x for x in q.iterdir() if x.suffix.lower() in (".png", ".jpg", ".jpeg")]) if q.is_dir() else 0
out = {"names": {str(k): v for k, v in d["names"].items()}, "nc": d.get("nc"),
       "dir_image_counts": {sp: _cnt(d.get(sp)) for sp in ("train", "val", "test", "challenge")}}
print("__ULTRA_RESULT__" + json.dumps(out, ensure_ascii=False))
"""


def cmd_yolo(ultra_python: str | None) -> int:
    records: list[SampleRecord] = _state["records"]
    r3_by = {s["sample_id"]: s for s in _read(R3_FULL)["samples"]}
    if YAML_DIR.exists():
        shutil.rmtree(YAML_DIR)
    stats, copied, cross = [], {}, {"checked": 0, "mismatch": [], "new_selfcheck": 0}
    sha_new_verified = []
    for sp in ("train", "val", "test", "challenge"):
        subset = sorted((s for s in records if s.split == sp), key=lambda x: x.sample_id)
        n_boxes = 0
        for s in subset:
            orig = r3_by[s.sample_id]["split"] if s.sample_id in r3_by else None
            dst = _copy_image(s, orig)
            copied[s.sample_id] = f"images/{sp}/{dst.name}"
            n_boxes += _export_label(s)
            if orig is not None:
                old = R3_YOLO / "labels" / orig / f"{_yolo_stem(s.sample_id)}.txt"
                new = YAML_DIR / "labels" / sp / f"{_yolo_stem(s.sample_id)}.txt"
                assert old.is_file(), f"{s.sample_id}: R3 树无对照 label"
                cross["checked"] += 1
                if old.read_bytes() != new.read_bytes():
                    cross["mismatch"].append(s.sample_id)
            else:
                cross["new_selfcheck"] += 1
                if s.sample_id in NEW_IDS:
                    d = sha256_file(dst)
                    assert d == sha256_file(Path(s.image.path)) == s.image.sha256, \
                        f"{s.sample_id}: sha 三方不一致"
                    sha_new_verified.append(s.sample_id)
        stats.append({"split": sp, "images": len(subset), "boxes": n_boxes})
    assert not cross["mismatch"], f"label 交叉比对失配: {cross['mismatch'][:5]}"

    yaml_path = _write_yaml()
    n1 = _names_channel1(yaml_path)
    n2 = _names_channel2(yaml_path)
    ultra = {"assert": "NOT_RUN"}
    if ultra_python and Path(ultra_python).is_file():
        import subprocess
        expect = {st["split"]: st["images"] for st in stats}
        proc = subprocess.run([ultra_python, "-c", _ULTRA_SNIPPET, str(yaml_path)],
                              capture_output=True, text=True, encoding="utf-8",
                              timeout=600, cwd=str(YAML_DIR))
        assert proc.returncode == 0, f"ultralytics 冒烟失败:\n{proc.stdout[-1500:]}\n{proc.stderr[-1500:]}"
        line = next(ln for ln in proc.stdout.splitlines() if ln.startswith("__ULTRA_RESULT__"))
        out = json.loads(line[len("__ULTRA_RESULT__"):])
        assert out["names"] == {str(k): v for k, v in SFX_CLASS_MAP.items()}
        assert out["nc"] == len(SFX_CLASS_MAP)
        for sp, n in expect.items():
            assert out["dir_image_counts"][sp] == n, \
                f"ultralytics {sp} 计数 {out['dir_image_counts'][sp]} != {n}"
        ultra = {"assert": "PASS", "ultralytics_python": str(ultra_python),
                 "dir_image_counts": out["dir_image_counts"], "nc": out["nc"]}
    else:
        ultra = {"assert": "NOT_RUN", "note": "训练 venv 不可达，如实登记"}

    # 导出后自洽校验（全 916）
    stem_mismatch = 0
    for st in stats:
        sp = st["split"]
        lbls = sorted((YAML_DIR / "labels" / sp).glob("*.txt"))
        imgs = sorted(p for p in (YAML_DIR / "images" / sp).iterdir()
                      if p.suffix.lower() in (".png", ".jpg", ".jpeg"))
        assert len(lbls) == len(imgs) == st["images"], f"{sp}: 数不一致"
        mm = {p.stem for p in lbls} ^ {p.stem for p in imgs}
        stem_mismatch += len(mm)
        assert not mm, f"{sp}: stem 失配 {sorted(mm)[:5]}"
        n_lines = 0
        cls_id = str(next(int(k) for k, v in SFX_CLASS_MAP.items() if v == "sfx"))
        for lf in lbls:
            for ln in lf.read_text(encoding="utf-8").splitlines():
                if not ln.strip():
                    continue
                parts = ln.split()
                assert parts[0] == cls_id, f"{lf.name}: cls {parts[0]}"
                vals = [float(v) for v in parts[1:]]
                assert len(vals) >= 6 and len(vals) % 2 == 0
                assert all(0.0 <= v <= 1.0 for v in vals), f"{lf.name}: 坐标越界"
                n_lines += 1
        assert n_lines == st["boxes"], f"{sp}: 行数 {n_lines} != {st['boxes']}"

    _state.update({"yolo_stats": stats, "names": {"channel1": n1, "channel2": n2},
                   "ultra": ultra, "cross": cross, "sha_new": sha_new_verified})
    print(f"[yolo] stats={json.dumps(stats)} names=ch1:PASS/ch2:{n2['parser']} "
          f"ultra={ultra['assert']} cross_checked={cross['checked']} mismatch=0 "
          f"new_selfcheck={cross['new_selfcheck']} sha_new={sha_new_verified}")
    return 0


def cmd_summary() -> int:
    records = _state["records"]
    st = {
        "task": "M2-SFX-GATE-T3 AC2 train-v4 重切（BJ32-35 转正并入 ai-direct-annotation 首例）",
        "generated_at_utc": now_iso(),
        "tool": "experiments/M2-SFX-GATE-T3/prepare_dataset_v4.py --step all",
        "base": {"train_v3_full": str(R3_FULL), "r3_count": 912,
                 "r4_manifest": str(R4M), "new_ids": list(NEW_IDS),
                 "bj36_37_note": "双 AI 终裁零 SFX（0 框）留底册 pseudo 不入（schema.py:88-89+pre-bj25 先例）"},
        "assign_splits": {
            "method": "选项 A：assign_splits(force=True, pinned=…) 函数参数（沿 V2/R3）",
            "pinned": dict(sorted(PINNED.items())),
            "drift_vs_train_v3": 0,
            "group_isolation_violations": 0,
            "fingerprint": _state["fingerprint"],
            "challenge_members": _state["chal"],
            "challenge_boxes": 8,
            "exam_5box_untouched": "pre-bj17×2+pre-bj18×3 逐位=R2 final 出厂（断言 A3）",
            "bj3237_pin_divergence": _state["lock"]["bj32_37_pin_note"],
        },
        "expected_vs_actual": {
            "expected": EXPECTED_SPLITS, "total": EXPECTED_TOTAL,
            "actual": {sp: {"samples": _state["by_split"][sp],
                            "boxes": _state["boxes_by_split"][sp]}
                       for sp in ("train", "val", "test", "challenge")},
        },
        "splits_detail": {
            sp: {
                "samples": _state["by_split"][sp], "boxes": _state["boxes_by_split"][sp],
                "complete": sum(1 for s in records if s.split == sp and s.annotation_status == "complete"),
                "partial": sum(1 for s in records if s.split == sp and s.annotation_status == "partial"),
                "pseudo": sum(1 for s in records if s.split == sp and s.annotation_status == "pseudo"),
                "synthetic": sum(1 for s in records if s.split == sp and s.annotation_status == "synthetic"),
            } for sp in ("train", "val", "test", "challenge")},
        "yolo": {"root": "training_data/sfx-v1/train-v4/dataset",
                 "per_split": _state["yolo_stats"],
                 "names_dual_channel": _state["names"],
                 "ultralytics_scan": _state["ultra"],
                 "label_crosscheck_vs_r3": {**_state["cross"], "scope": (
                     "R3 912 与 R3 yolo 树原分集同名 label 逐字节比对（重切不动框几何）；"
                     "BJ32-35 新页导出自洽校验+sha256 三方抽验")},
                 "sha256_new_verified": _state["sha_new"]},
        "honest_notes": [
            "BJ32/37 属 densho810/vol05 考卷组：BJ32（3 框）随组入 challenge（gate-definition §4.G1 "
            "「challenge 侧含 vol05 组转正扩展框」）；BJ37 双 AI 终裁零 SFX 0 框，schema.py:88-89 "
            "禁止 complete 空框 → 沿 pre-bj25 零框负证据先例保持 pseudo 留底册，不入本 manifest。",
            "ask 表述「BJ26-37 钉 train」与 G3 组隔离硬门冲突处按冻结 Gate 语义执行（BJ33-35 "
            "vol03 组入 train；BJ26/27/30/31 仍 pseudo 不入），G1 主判据 5 框不受影响。",
            "BJ32-35 框=双 AI consensus union + arbiter keep 终裁（ai-direct-annotation 首例，"
            "conf=null 概念不适用）；BJ 扩展集 directional 侧 12 页 33 框（challenge 3 页 8 框+train 9 页 25 框）。",
            "BJ36（vol03 组）0 框负证据留底册不入训练 manifest——与 own-manga pseudo 0 框页入 train "
            "的处置不同（own pseudo=模型产出弱负样本既定入册先例；BJ36=人工判定零 SFX 的负证据留痕，"
            "沿 BJ25 先例不入），处置差异如实登记。",
        ],
    }
    GIT_SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    GIT_SUMMARY.write_text(json.dumps(st, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[summary] wrote {GIT_SUMMARY}")
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", required=True, choices=["reassign", "yolo", "summary", "all"])
    ap.add_argument("--ultralytics-python", default=str(TRAIN_VENV_DEFAULT))
    args = ap.parse_args()
    ultra = args.ultralytics_python if Path(args.ultralytics_python).is_file() else None
    steps = ["reassign", "yolo", "summary"] if args.step == "all" else [args.step]
    for s in steps:
        rc = {"reassign": cmd_reassign, "yolo": lambda: cmd_yolo(ultra), "summary": cmd_summary}[s]()
        if rc:
            return rc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
