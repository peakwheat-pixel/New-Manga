"""AC6：工具 CLI。零 src；数据本体落 gitignored 外部树，Git 只进代码+schema+摘要哈希。

子命令：
  selfcheck      内置自检（schema 往返/dhash/几何互算/原子写恢复 mini 冒烟）
  pipeline       一键：导入三资产+合成 PoC+拆分+去重+训练构建器+摘要
  import-assets  仅导入（7+8+43）
  synth          仅合成渲染 PoC（≥20，seed 冻结）
  split          仅组隔离拆分（seed 冻结+lock）
  dedup          仅双去重
  build-train    训练集构建（设计上不可读 test/challenge）
  summary        产 manifest-summary.json（Git 只进此摘要）
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from sfx_data_infra import MANIFEST_KIND, SCHEMA_VERSION
from sfx_data_infra.atomicio import (
    ManifestValidationError,
    atomic_write_json,
    cleanup_stale_tmp,
    load_manifest,
    write_manifest,
)
from sfx_data_infra.dedup import DedupReport, drop_duplicates, find_duplicates
from sfx_data_infra.hash import box_exact_hash, dhash_image, hamming_distance, sha256_file
from sfx_data_infra.importers import import_all
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord
from sfx_data_infra.splits import (
    SEED_DEFAULT,
    TrainingSetBuilder,
    assign_splits,
    split_fingerprint,
)
from sfx_data_infra.synth import (
    RenderResult,
    anchor_points,
    default_poc_params,
    discover_fonts,
    forward_transform_points,
    inverse_transform_points,
    render_sample,
)

PKG_PARENT = Path(__file__).resolve().parents[1]
REPO_ROOT = PKG_PARENT.parents[1]
DEFAULT_DATA_ROOT = REPO_ROOT / "training_data" / "sfx-v1"
CHALLENGE_IDS = ("BJ13", "BJ14", "BJ15")
# r1 P1-3：合成 PoC 是单一大组，参与比例切片会被整组切进 val（train 零合成、
# val 77% 合成，与"辅助监督"声明矛盾）。显式钉入 train，val 保持真实来源。
PINNED_GROUPS = {"synthetic/poc": "train"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- selfcheck


def cmd_selfcheck(_args: argparse.Namespace) -> int:
    import tempfile

    checks: list[tuple[str, bool, str]] = []

    # 1) schema：dataclass↔dict 往返 + JSON Schema 枚举一致
    from sfx_data_infra.schema import make_json_schema

    js = make_json_schema()
    sample = SampleRecord(
        sample_id="selfcheck-1",
        image=ImageRef(path="x.png", sha256="a" * 64, width=8, height=8),
        boxes=[BoxAnnotation(polygon=[[0, 0], [4, 0], [4, 4], [0, 4]], text="ドン")],
        annotation_status="synthetic",
        provenance={"type": "synthetic_render", "render_seed": 20261004},
        group="synthetic/selfcheck",
        created_at=_now_iso(),
    )
    rt = SampleRecord.from_dict(sample.to_dict())
    checks.append(("schema_roundtrip", rt == sample, "dataclass↔dict 往返一致"))
    checks.append((
        "schema_json_enums",
        js["properties"]["annotation_status"]["enum"] == ["complete", "partial", "pseudo", "synthetic"],
        "JSON Schema 标注状态枚举与 dataclass 一致",
    ))

    # 2) dhash / 框哈希
    rng = np.random.default_rng(0)
    img_a = Image.fromarray(rng.integers(0, 256, (64, 64, 3), dtype=np.uint8), "RGB")
    img_b = Image.fromarray(rng.integers(0, 256, (64, 64, 3), dtype=np.uint8), "RGB")
    ha, hb = dhash_image(img_a), dhash_image(img_b)
    checks.append(("dhash", hamming_distance(ha, ha) == 0 and hamming_distance(ha, hb) > 8,
                   f"d(a,a)=0 d(a,b)={hamming_distance(ha, hb)}"))
    checks.append(("box_hash",
                   box_exact_hash([[0, 0], [1, 0], [1, 1], [0, 1]], "sfx", None, "a" * 64)
                   != box_exact_hash([[0, 0], [1, 0], [1, 1], [0, 1]], "sfx", "ドン", "a" * 64),
                   "文本变化→框哈希变化"))

    # 3) 几何互算：forward∘inverse 精确
    from sfx_data_infra.synth import RenderParams

    p = RenderParams(
        sample_name="selfcheck", text="ドン", font_path=discover_fonts(1)[0], font_size=48,
        canvas_w=320, canvas_h=240, rotation_deg=13.0, arc_curvature_px=-18.0,
        perspective_shift_px=22.0, tx=10.0, ty=6.0,
    )
    pts = anchor_points(p)
    err = float(np.abs(inverse_transform_points(p, forward_transform_points(p, pts)) - pts).max())
    checks.append(("geometry_roundtrip", err < 1e-6, f"forward∘inverse max err={err:.2e}"))

    # 4) 原子写+恢复：round-trip、损坏拒绝、残留 tmp 清理
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        mp = tdp / "m.json"
        write_manifest(mp, [sample], seed=1)
        _, loaded = load_manifest(mp)
        ok1 = len(loaded) == 1
        raw = mp.read_text(encoding="utf-8")
        mp.write_text(raw[: len(raw) // 2], encoding="utf-8")
        try:
            load_manifest(mp)
            ok2 = False
        except ManifestValidationError:
            ok2 = True
        (tdp / "m.json.999.tmp").write_text("stale", encoding="utf-8")
        removed = cleanup_stale_tmp(mp)
        checks.append(("atomic_write_recover", ok1 and ok2 and len(removed) == 1,
                       f"roundtrip={ok1} corrupt_rejected={ok2} stale_tmp_removed={len(removed)}"))

    all_ok = all(ok for _, ok, _ in checks)
    print(f"selfcheck @ {SCHEMA_VERSION}: {'PASS' if all_ok else 'FAIL'}")
    for name, ok, detail in checks:
        print(f"  [{'OK' if ok else 'NG'}] {name}: {detail}")
    return 0 if all_ok else 1


# ---------------------------------------------------------------- pipeline 步骤


def _copy_into_assets(src: Path, data_root: Path, bucket: str) -> str:
    """素材只读复制进外部树（训练树自包含+相对路径引用）。"""
    dst_dir = data_root / "assets" / bucket
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / src.name
    if not dst.exists() or sha256_file(dst) != sha256_file(src):
        shutil.copy2(src, dst)
    return f"assets/{bucket}/{dst.name}".replace("\\", "/")


def step_import(data_root: Path, now_iso: str) -> tuple[list[SampleRecord], dict]:
    """导入三资产：7+8+43=58；素材复制进 assets/，图引用转 data_root 相对路径。"""
    raw = import_all(now_iso)
    # 先收集源路径再改 path：同页多框样本共享 ImageRef 实例，改写须一次完成
    src_by_sha: dict[str, Path] = {}
    for s in raw:
        src_by_sha.setdefault(s.image.sha256, Path(s.image.path))
    rel_names: dict[str, str] = {}
    for s in raw:
        src = src_by_sha[s.image.sha256]
        if s.sample_id.startswith("imp-ogkalu-"):
            bucket = "ogkalu-crops"
        else:
            bucket = f"pages-{s.provenance['case_id'].lower()}"
        rel_names[s.sample_id] = _copy_into_assets(src, data_root, bucket)
    for s in raw:
        s.image.path = rel_names[s.sample_id]
    for s in raw:
        errors = s.validate()
        if errors:
            raise ValueError(f"{s.sample_id}: {errors}")
    n_boxes = sum(len(s.boxes) for s in raw)
    info = {"imported": len(raw), "boxes": n_boxes, "assets_copied": len(set(rel_names.values()))}
    print(f"[import] {json.dumps(info, ensure_ascii=False)}")
    return raw, info


def step_synth(data_root: Path, now_iso: str, count: int = 24) -> tuple[list[SampleRecord], dict]:
    """合成渲染 PoC：PNG 落 synthetic/，synthetic 状态，精确 GT+互算复核。"""
    out_dir = data_root / "synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    all_fonts = discover_fonts(extra_dirs=[data_root / "fonts"])
    # AC4 毛笔域聚焦：data_root/fonts 下命中的手写/毛笔风字体（如 TanukiMagic）
    # 存在时 PoC 独占使用；否则回退系统字体（差距登记见报告）
    import os as _os
    from sfx_data_infra.synth import _BRUSHY_NAME_HINTS

    brushy = [f for f in all_fonts if any(h in Path(f).stem.lower() for h in _BRUSHY_NAME_HINTS)]
    fonts = brushy or all_fonts
    samples: list[SampleRecord] = []
    roundtrip_worst = 0.0
    for p in default_poc_params(count=count, fonts=fonts):
        result: RenderResult = render_sample(p)
        png_name = f"{p.sample_name}.png"
        png_path = out_dir / png_name
        result.image.save(png_path)
        pts = anchor_points(p)
        err = float(np.abs(inverse_transform_points(p, forward_transform_points(p, pts)) - pts).max())
        roundtrip_worst = max(roundtrip_worst, err)
        w, h = result.image.size
        samples.append(
            SampleRecord(
                sample_id=f"synth-{p.sample_name}",
                image=ImageRef(path=f"synthetic/{png_name}", sha256=sha256_file(png_path), width=w, height=h),
                boxes=[BoxAnnotation(
                    polygon=result.gt_polygon, cls="sfx", text=p.text,
                    occluded=p.occlusion is not None,  # r1 P1-4：遮挡标记落地，口径非仅 README
                )],
                annotation_status="synthetic",
                provenance={
                    "type": "synthetic_render",
                    "render_seed": p.seed,
                    "font_path": p.font_path,
                    "font_size": p.font_size,
                    "rotation_deg": round(p.rotation_deg, 4),
                    "arc_curvature_px": round(p.arc_curvature_px, 4),
                    "perspective_shift_px": round(p.perspective_shift_px, 4),
                    "tx": round(p.tx, 4),
                    "ty": round(p.ty, 4),
                    "stroke_width": p.stroke_width,
                    "occlusion": p.occlusion,
                    "gt_basis": "render_params_forward_geometry",
                },
                group="synthetic/poc",
                created_at=now_iso,
            )
        )
    info = {"synth_count": len(samples), "roundtrip_max_err_px": roundtrip_worst}
    print(f"[synth] {json.dumps(info, ensure_ascii=False)}")
    return samples, info


def step_split(samples: list[SampleRecord], seed: int) -> tuple[list[SampleRecord], dict]:
    assign_splits(samples, seed=seed, force=True, pinned=PINNED_GROUPS)
    info = {
        "seed": seed,
        "pinned_groups": dict(PINNED_GROUPS),
        "by_split": dict(Counter(s.split for s in samples)),
    }
    print(f"[split] {json.dumps(info, ensure_ascii=False)}")
    return samples, info


def step_dedup(samples: list[SampleRecord], data_root: Path) -> tuple[list[SampleRecord], DedupReport]:
    def loader(rel: str):
        with Image.open(data_root / rel) as im:
            return im.convert("RGB")

    report = find_duplicates(samples, image_loader=loader)
    kept = drop_duplicates(samples, report)
    info = {
        "exact_pairs": len(report.exact_pairs),
        "box_exact_pairs": len(report.box_exact_pairs),
        "perceptual_pairs": len(report.perceptual_pairs),
        "dropped": len(samples) - len(kept),
        "dhash_errors": report.dhash_errors,
    }
    print(f"[dedup] {json.dumps(info, ensure_ascii=False)}")
    return kept, report


def step_build_train(samples: list[SampleRecord]) -> tuple[list[SampleRecord], dict]:
    builder = TrainingSetBuilder(samples, allowed_splits=("train", "val"))
    info = {
        "train_builder_counts": builder.counts(),
        "excluded_splits": ["test", "challenge"],
        # r1 P1-2：负样本（ogkalu 空框）默认排除出训练集；是否使用弱负样本由 T1b 显式决策
        "excluded_negative_ids": builder.excluded_negative_ids,
        "status_distribution": builder.status_distribution(),
    }
    print(f"[build-train] {json.dumps(info, ensure_ascii=False)}")
    return builder.samples, info


def build_summary(
    data_root: Path,
    samples: list[SampleRecord],
    split_info: dict,
    dedup_report: DedupReport,
    train_info: dict,
    import_info: dict,
    synth_info: dict | None,
    now_iso: str,
) -> dict:
    full_path = data_root / "manifest.full.json"
    train_path = data_root / "manifest.train.json"
    ogkalu = [s for s in samples if s.sample_id.startswith("imp-ogkalu-")]
    ogkalu_negative = [s for s in ogkalu if not s.boxes]
    synth_samples = [s for s in samples if s.annotation_status == "synthetic"]
    synth_by_split = dict(Counter(s.split for s in synth_samples))

    def fsha(p: Path) -> dict:
        return {"sha256": sha256_file(p), "bytes": p.stat().st_size}

    return {
        "task": "M2-SFX-DATA-INFRA",
        "schema_version": SCHEMA_VERSION,
        "manifest_kind": MANIFEST_KIND,
        "generated_at": now_iso,
        # r1 P2-13：入库摘要不写本机绝对路径，只记相对约定
        "data_root_gitignored": "training_data/sfx-v1（repo 同级 gitignored 外部树）",
        "totals": {
            "samples": len(samples),
            "images": len({s.image.sha256 for s in samples}),
            "boxes": sum(len(s.boxes) for s in samples),
            "by_status": dict(Counter(s.annotation_status for s in samples)),
            "by_split": dict(Counter(s.split for s in samples)),
            "by_group": dict(Counter(s.group for s in samples)),
        },
        "import_assets": {
            "l3_reference_boxes": 7,
            "bj06_selfcheck_boxes": 8,
            "ogkalu_regions": len(ogkalu),
            "ogkalu_regions_negative_empty_boxes": len(ogkalu_negative),
            "ogkalu_boxes_total": sum(len(s.boxes) for s in ogkalu),
            **(import_info or {}),
        },
        "synthetic_poc": {
            "count": (synth_info or {}).get("synth_count", len(synth_samples)),
            "gt_roundtrip_max_err_px": (synth_info or {}).get("roundtrip_max_err_px"),
            "annotation_status": "synthetic",
            "ai_fullpage_generation": "not_used（若引入必标 pseudo 不入 GT）",
            # r1 P1-3：合成样本落点必须如实呈现（pinned 后应全部在 train）
            "by_split": synth_by_split,
            "fonts": sorted({s.provenance.get("font_path", "") for s in synth_samples}),
        },
        "split_lock": {
            "seed": split_info["seed"],
            "method": "group-hash-rank-v2",
            "pinned_groups": dict(PINNED_GROUPS),
            "fingerprint": split_info.get("fingerprint", ""),
            "challenge_single_bucket": list(CHALLENGE_IDS),
        },
        "dedup": {
            "exact_pairs": len(dedup_report.exact_pairs),
            "box_exact_pairs": len(dedup_report.box_exact_pairs),
            "perceptual_pairs": len(dedup_report.perceptual_pairs),
            "dhash_errors": dedup_report.dhash_errors,
        },
        "train_builder": train_info,
        "manifest_files": {
            "manifest.full.json": fsha(full_path),
            "manifest.train.json": fsha(train_path),
        },
    }


# ---------------------------------------------------------------- 命令


def cmd_pipeline(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    data_root.mkdir(parents=True, exist_ok=True)
    seed = int(args.seed)
    now_iso = _now_iso()

    cleanup_stale_tmp(data_root / "manifest.full.json")

    imported, import_info = step_import(data_root, now_iso)
    synth, synth_info = step_synth(data_root, now_iso, count=int(args.synth_count))
    all_samples = imported + synth

    all_samples, split_info = step_split(all_samples, seed)
    kept, dedup_report = step_dedup(all_samples, data_root)
    train_samples, train_info = step_build_train(kept)

    # r1 P2-5：fingerprint 以去重后的最终 kept 集计算——lock 描述的必须是
    # 实际落盘产物，而非去重前的中间态
    fingerprint = split_fingerprint(kept, seed)
    split_info["fingerprint"] = fingerprint

    write_manifest(
        data_root / "manifest.full.json",
        kept,
        seed=seed,
        extra={
            "lock": {
                "seed": seed,
                "method": "group-hash-rank-v2",
                "pinned_groups": dict(PINNED_GROUPS),
                "fingerprint": fingerprint,
                "frozen_at": now_iso,
                "challenge_case_ids": list(CHALLENGE_IDS),
            }
        },
    )
    write_manifest(
        data_root / "manifest.train.json",
        train_samples,
        seed=seed,
        extra={"note": "train/val only — test/challenge 与负样本由 TrainingSetBuilder 构造期剔除"},
    )

    summary = build_summary(data_root, kept, split_info, dedup_report, train_info, import_info, synth_info, now_iso)
    summary_path = Path(args.summary_out)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_json(summary_path, summary)
    print(f"[summary] {summary_path}")
    return 0


def cmd_import_assets(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    data_root.mkdir(parents=True, exist_ok=True)
    samples, info = step_import(data_root, _now_iso())
    write_manifest(data_root / "manifest.import.json", samples)
    print(json.dumps(info, ensure_ascii=False))
    return 0


def cmd_synth(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    samples, info = step_synth(data_root, _now_iso(), count=int(args.synth_count))
    write_manifest(data_root / "manifest.synth.json", samples)
    print(json.dumps(info, ensure_ascii=False))
    return 0


def cmd_split(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    container, records = load_manifest(data_root / "manifest.full.json")
    records, info = step_split(records, int(args.seed))
    fingerprint = split_fingerprint(records, int(args.seed))
    info["fingerprint"] = fingerprint
    write_manifest(
        data_root / "manifest.full.json",
        records,
        seed=int(args.seed),
        extra={"lock": {"seed": int(args.seed), "method": "group-hash-rank-v2",
                        "pinned_groups": dict(PINNED_GROUPS),
                        "fingerprint": fingerprint, "frozen_at": _now_iso()}},
    )
    return 0


def cmd_dedup(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    container, records = load_manifest(data_root / "manifest.full.json")
    kept, _report = step_dedup(records, data_root)
    # r1 P2-3：回写必须透传 seed/lock，否则"划分一次冻结"被抹掉
    write_manifest(
        data_root / "manifest.full.json",
        kept,
        seed=container.get("seed"),
        extra={k: container[k] for k in ("lock",) if k in container},
    )
    return 0


def cmd_build_train(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    container, records = load_manifest(data_root / "manifest.full.json")
    train_samples, info = step_build_train(records)
    write_manifest(
        data_root / "manifest.train.json",
        train_samples,
        seed=container.get("seed"),
        extra={"note": "train/val only — test/challenge 与负样本由 TrainingSetBuilder 构造期剔除"},
    )
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    data_root = Path(args.data_root)
    container, records = load_manifest(data_root / "manifest.full.json")
    split_info = {
        "seed": container.get("seed", SEED_DEFAULT),
        "fingerprint": (container.get("lock") or {}).get("fingerprint", ""),
    }
    synth_from_disk = {
        "synth_count": sum(1 for s in records if s.annotation_status == "synthetic"),
    }
    summary = build_summary(
        data_root, records, split_info, DedupReport(),
        {"train_builder_counts": {"note": "见 manifest.train.json"}}, {}, synth_from_disk, _now_iso(),
    )
    summary_path = Path(args.summary_out)
    atomic_write_json(summary_path, summary)
    print(f"[summary] {summary_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sfx_data_infra",
        description="SFX 训练数据基础设施（M2-SFX-DATA-INFRA/T1a）：manifest/拆分/去重/合成 PoC/导入器",
    )
    parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT),
                        help="外部数据树根（gitignored，默认 training_data/sfx-v1）")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("selfcheck", help="内置自检（EXIT=0 即通过）").set_defaults(func=cmd_selfcheck)

    p_pipe = sub.add_parser("pipeline", help="一键：导入+合成+拆分+去重+训练构建+摘要")
    p_pipe.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p_pipe.add_argument("--synth-count", type=int, default=24)
    p_pipe.add_argument("--summary-out", default=str(PKG_PARENT / "manifest_summary.json"))
    p_pipe.set_defaults(func=cmd_pipeline)

    sub.add_parser("import-assets", help="导入三存量资产（7+8+43）").set_defaults(func=cmd_import_assets)
    p_synth = sub.add_parser("synth", help="合成渲染 PoC")
    p_synth.add_argument("--synth-count", type=int, default=24)
    p_synth.set_defaults(func=cmd_synth)
    p_split = sub.add_parser("split", help="组隔离拆分")
    p_split.add_argument("--seed", type=int, default=SEED_DEFAULT)
    p_split.set_defaults(func=cmd_split)
    sub.add_parser("dedup", help="双去重").set_defaults(func=cmd_dedup)
    sub.add_parser("build-train", help="训练集构建（不可读 test/challenge）").set_defaults(func=cmd_build_train)
    p_sum = sub.add_parser("summary", help="产 manifest-summary.json")
    p_sum.add_argument("--summary-out", default=str(PKG_PARENT / "manifest_summary.json"))
    p_sum.set_defaults(func=cmd_summary)
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return int(args.func(args) or 0)


if __name__ == "__main__":
    sys.exit(main())
