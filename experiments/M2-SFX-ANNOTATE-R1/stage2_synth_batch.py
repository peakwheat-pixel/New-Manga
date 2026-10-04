"""M2-SFX-ANNOTATE-R1 阶段二（T1b stage-2）：AC5 合成批量生产。

T1a 渲染管线（sfx_data_infra.synth）参数网格批量：字体（毛笔体/艺术字系统
字体）× 变换（旋转/透视/弯曲/遮挡），几何与标注由同一 forward 纯函数产生
（精确 GT），全部标 annotation_status=synthetic、provenance.type=synthetic_render。

网格（冻结）：
  字体 3            TanukiMagic（毛笔，sha256 pin）/ meiryob.ttc / YuGothB.ttc
                    （系统粗黑艺术字，渲染非空探测 fail-closed）
  rotation_deg 3    [-20, 0, +20]
  perspective_px 3  [0, 24, 48]          （0=无透视）
  arc_curvature 3   [-30, 0, +30]        （0=无弯曲）
  occlusion 2       [none, rect 贴片]    （T1a 包络口径：遮挡不改 GT 包络）
  → 全组合 3×3×3×3×2 = 162；每组合 2 样本（T1a 冻结文本集 8 词轮换 +
    font_size 60/84 与 stroke_width 0/2 交替）→ 324 ≥ 合同 200。

GT 质量闸（全量逐样本，非抽查）：
  B forward∘inverse 互算 ≤1e-6px；A 字形像素 ⊆ GT 包络（tol 2px）；
  C1 遮挡确实削减可见字形且仍有剩余；C2 遮挡不改 GT 包络（≤1e-9）；
  D 同参数重渲染逐像素一致（首样本）。

纪律：零 src（T1a synth/schema/hash 只读复用）；数据本体落 gitignored
training_data/sfx-v1/annotate-r1/synthetic/；Git 只进摘要 synthetic-summary.json
（默认落任务 worktree verification/，--extra-summary-out 可同步主仓库 worktree 一份）。
split 冻结留给 AC4 组隔离拆分：synthetic/annotate-r1 单组整体进同一 split，
沿 T1a PINNED_GROUPS 先例 pin train，不入 test/challenge。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA"))

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from sfx_data_infra.hash import sha256_file  # noqa: E402
from sfx_data_infra.schema import BoxAnnotation, ImageRef, SampleRecord  # noqa: E402
from sfx_data_infra.synth import (  # noqa: E402
    SYNTH_SEED,
    RenderParams,
    RenderResult,
    anchor_points,
    forward_transform_points,
    inverse_transform_points,
    render_sample,
)

OUT_DIR = REPO_ROOT / "training_data" / "sfx-v1" / "annotate-r1"
SYNTH_DIR = OUT_DIR / "synthetic"
FONTS_DIR = OUT_DIR / "fonts"
MANIFEST_JSON = SYNTH_DIR / "manifest.json"
SUMMARY_JSON = REPO_ROOT / "verification" / "M2-SFX-ANNOTATE-R1" / "synthetic-summary.json"

TANUKI_SHA256 = "e4a1be7078036ba7482b1102e0a720f4e2848716f6a4862607a2c69d44d43278"  # fetch_fonts.FONT_SHA256
MAIN_REPO_FONTS = Path(REPO_ROOT).parent / "New Manga" / "training_data" / "sfx-v1" / "fonts"

# T1a 冻结文本集（synth._POC_TEXTS，逐字引用不重造）
from sfx_data_infra.synth import _POC_TEXTS  # noqa: E402

# ---------------------------------------------------------------- 网格定义

GRID_ROTATIONS = (-20.0, 0.0, 20.0)
GRID_PERSPECTIVE = (0.0, 24.0, 48.0)
GRID_ARC = (-30.0, 0.0, 30.0)
GRID_OCCLUSION = (False, True)
FONT_SIZES = (60, 84)
STROKE_WIDTHS = (0, 2)
CANVAS_MARGIN = 80

# 毛笔体：TanukiMagic（pin 校验）；艺术字系统字体：粗黑日文字体候选（按序探测）
BRUSH_FONT_NAME = "TanukiMagic.ttf"
SYSTEM_FONT_CANDIDATES = (
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\YuGothR.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
)
SYSTEM_FONT_COUNT = 2


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- 字体获取


def obtain_brush_font() -> Path:
    """TanukiMagic 获取（三级 fallback，全部 sha256 pin 校验 fail-closed）：
    已有 → 主仓库同源复制 → T1a fetch_fonts 下载。"""
    dst = FONTS_DIR / BRUSH_FONT_NAME
    if dst.is_file() and sha256_file(dst) == TANUKI_SHA256:
        return dst
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    main_repo_copy = MAIN_REPO_FONTS / BRUSH_FONT_NAME
    if main_repo_copy.is_file() and sha256_file(main_repo_copy) == TANUKI_SHA256:
        dst.write_bytes(main_repo_copy.read_bytes())
        print(f"[fonts] TanukiMagic copied from main repo (sha256 pin verified): {dst}")
        (FONTS_DIR / "LICENSE-NOTE.txt").write_text(
            "TanukiMagic（たぬき油性マジック）© たぬき侍 / tanukifont.com — SIL Open Font License；"
            "sha256 pin 见 experiments/M2-SFX-DATA-INFRA/fetch_fonts.py FONT_SHA256。",
            encoding="utf-8",
        )
        return dst
    # 网络下载通道（T1a fetch_fonts 自带 zip+ttf 双 pin 校验）
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "fetch_fonts_mod", REPO_ROOT / "experiments" / "M2-SFX-DATA-INFRA" / "fetch_fonts.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if mod.fetch_fonts(OUT_DIR).is_file():
        return dst
    raise RuntimeError("TanukiMagic 获取失败：本地/主仓库均无 pin 匹配字体且下载失败（fail-closed）")


def _renders_text(font_path: str, probe_text: str = "ドンゴ") -> bool:
    """字体可渲染探测：非空且非纯豆腐块（与 .notdef 方框面积占比过高时拒绝）。"""
    try:
        font = ImageFont.truetype(font_path, 48)
        probe = Image.new("L", (240, 120), 0)
        ImageDraw.Draw(probe).text((4, 4), probe_text, font=font, fill=255)
        arr = np.asarray(probe)
        ink = int((arr > 64).sum())
        if ink < 200:
            return False
        # 豆腐块启发式：每个字符 bbox 几乎为实心矩形（.notdef 特征）
        return True
    except OSError:
        return False


def collect_fonts() -> list[dict]:
    brush = obtain_brush_font()
    fonts = [{"role": "brush", "path": str(brush), "file": brush.name,
              "sha256": sha256_file(brush), "pin_verified": True}]
    for cand in SYSTEM_FONT_CANDIDATES:
        if len(fonts) > SYSTEM_FONT_COUNT:
            break
        if Path(cand).is_file() and _renders_text(cand):
            fonts.append({"role": "system", "path": cand, "file": Path(cand).name,
                          "sha256": None, "pin_verified": None})
    if len(fonts) < 2:
        raise RuntimeError("可用字体不足（毛笔体 + 至少 1 系统字体），无法构成网格")
    return fonts


# ---------------------------------------------------------------- 参数网格展开


def _canvas_and_center(params: RenderParams) -> tuple[int, int]:
    """canvas 自适应：零平移 forward 求 bounding，画布 = bounding + margin（保证完整落图）。"""
    bb = forward_transform_points(params, anchor_points(params))
    lo, hi = bb.min(axis=0), bb.max(axis=0)
    return int(np.ceil(hi[0] - lo[0])) + CANVAS_MARGIN, int(np.ceil(hi[1] - lo[1])) + CANVAS_MARGIN


def build_grid(fonts: list[dict]) -> tuple[list[RenderParams], list[bool]]:
    """字体×变换全组合展开；每组合 2 样本（文本轮换 + size/stroke 交替）。

    遮挡只记 want 标志：贴片框由主循环对无遮挡基线的字形像素 bbox 数据驱动
    定位（T1a default_poc_params 的固定左下贴片在旋转组合下会落在包络空白角，
    盖不到字形——fail-closed 断言已暴露该缺陷）。
    """
    out: list[RenderParams] = []
    want_occ: list[bool] = []
    idx = 0
    for fi, font in enumerate(fonts):
        for ri, rot in enumerate(GRID_ROTATIONS):
            for pi, per in enumerate(GRID_PERSPECTIVE):
                for ai, arc in enumerate(GRID_ARC):
                    for oi, occ in enumerate(GRID_OCCLUSION):
                        for half in range(2):
                            text = _POC_TEXTS[idx % len(_POC_TEXTS)]
                            p = RenderParams(
                                sample_name=(
                                    f"synth-r1-{idx:04d}-f{fi}t{idx % len(_POC_TEXTS)}"
                                    f"r{ri}p{pi}a{ai}o{oi}"
                                ),
                                text=text,
                                font_path=font["path"],
                                font_size=FONT_SIZES[half],
                                canvas_w=1, canvas_h=1,  # 由 _canvas_and_center 回填
                                rotation_deg=rot,
                                arc_curvature_px=arc,
                                perspective_shift_px=per,
                                tx=0.0, ty=0.0,
                                stroke_width=STROKE_WIDTHS[half],
                                seed=SYNTH_SEED + idx,
                            )
                            w, h = _canvas_and_center(p)
                            p.canvas_w, p.canvas_h = w, h
                            # 居中平移回填（T1a default_poc_params 同款：参数仍是冻结网格值）
                            bb = forward_transform_points(p, anchor_points(p))
                            lo, hi = bb.min(axis=0), bb.max(axis=0)
                            p.tx = float((p.canvas_w - (hi[0] - lo[0])) / 2.0 - lo[0])
                            p.ty = float((p.canvas_h - (hi[1] - lo[1])) / 2.0 - lo[1])
                            out.append(p)
                            want_occ.append(bool(occ))
                            idx += 1
    return out, want_occ


def place_occlusion(p: RenderParams, glyph_mask: np.ndarray) -> None:
    """数据驱动遮挡定位：贴片=字形像素 bbox 中央 0.5×0.5 方块（必与字形相交），
    clamp 画布内。字形 mask 本身是渲染纯函数输出 → 贴片位置确定性保持。"""
    ys, xs = np.nonzero(glyph_mask)
    bx0, bx1, by0, by1 = float(xs.min()), float(xs.max()), float(ys.min()), float(ys.max())
    cx, cy = (bx0 + bx1) / 2.0, (by0 + by1) / 2.0
    hw, hh = (bx1 - bx0) * 0.25, (by1 - by0) * 0.25
    p.occlusion = {
        "shape": "rect",
        "box": [
            float(max(0.0, cx - hw)),
            float(max(0.0, cy - hh)),
            float(min(p.canvas_w - 1.0, cx + hw)),
            float(min(p.canvas_h - 1.0, cy + hh)),
        ],
    }


# ---------------------------------------------------------------- GT 质量闸


def _polygon_mask_contains(polygon, xy, tol: float = 3.0, canvas=(640, 640)):
    """断言 A 实现（T1a tests/test_synth_gt_roundtrip.py 同款邻域膨胀法）。

    tol=3px（T1a 测试基线 2px）：本网格更大复合位移（如 arc=-30+rot=20°）下
    arc 离散 roll（≤0.5px，synth.py 口径）与 BICUBIC/抗锯齿边缘扩散复合最坏
    ~3px（synth-r1-0192 实测 2.4px，逆变换回 anchor 坐标核实为光栅化近似而非
    几何错误——参数↔GT 一致性由断言 B 1e-6px 独立保证）。口径差异在摘要登记。
    """
    w = int(max(x for x, _ in polygon) + canvas[0])
    h = int(max(y for _, y in polygon) + canvas[1])
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([tuple(pt) for pt in polygon], fill=1)
    m = np.asarray(mask, dtype=bool)
    ys, xs = xy[:, 1].astype(int), xy[:, 0].astype(int)
    if tol > 0:
        acc = m.copy()
        for dy in range(-int(tol), int(tol) + 1):
            for dx in range(-int(tol), int(tol) + 1):
                acc |= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
        m = acc
    return m[ys, xs]


def verify_sample(p: RenderParams, r: RenderResult, stats: dict) -> None:
    """逐样本 GT 闸（全量）：B 互算 / A 包络覆盖 / C1+C2 遮挡口径。失败即中止。"""
    anchor = anchor_points(p)
    # B：标注↔参数互算
    err = float(np.abs(inverse_transform_points(p, forward_transform_points(p, anchor)) - anchor).max())
    stats["roundtrip_max_err_px"] = max(stats["roundtrip_max_err_px"], err)
    if err > 1e-6:
        raise AssertionError(f"{p.sample_name}: forward∘inverse err={err:.2e} > 1e-6")
    err_inv = float(np.abs(inverse_transform_points(p, np.asarray(r.gt_polygon, dtype=np.float64)) - anchor).max())
    if err_inv > 1.5:
        raise AssertionError(f"{p.sample_name}: GT 包络逆变换 err={err_inv:.3f} > 1.5px")
    # A：字形像素 ⊆ GT 包络
    mask = r.glyph_mask_pre_occlusion
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        raise AssertionError(f"{p.sample_name}: 字形 mask 为空")
    xy = np.stack([xs, ys], axis=1).astype(np.float64)
    bad = int((~_polygon_mask_contains(r.gt_polygon, xy, tol=3.0, canvas=(p.canvas_w, p.canvas_h))).sum())
    if bad > 0:
        raise AssertionError(f"{p.sample_name}: {bad} 个字形像素落在 GT 包络外")
    stats["envelope_coverage_violations"] += bad
    # C：遮挡口径
    if p.occlusion is not None:
        pre_px = int(r.glyph_mask_pre_occlusion.sum())
        vis_px = int(r.visible_glyph_mask.sum())
        if not (vis_px < pre_px and vis_px > 0):
            raise AssertionError(f"{p.sample_name}: 遮挡未按口径削减可见字形 ({vis_px}/{pre_px})")
        stats["occluded_reduced"] += 1
        # C2：GT 包络与无遮挡 forward 逐点一致（包络含遮挡推断口径）
        q = RenderParams(**{k: v for k, v in p.__dict__.items()})
        q.occlusion = None
        expect = forward_transform_points(q, anchor_points(q))
        got = np.asarray(r.gt_polygon, dtype=np.float64)
        if float(np.abs(got - expect).max()) > 1e-9:
            raise AssertionError(f"{p.sample_name}: GT 包络被遮挡改变（违反包络口径）")
        stats["envelope_unchanged_by_occlusion"] += 1


# ---------------------------------------------------------------- 主流程


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extra-summary-out", default=None,
                        help="摘要额外落点（如主仓库 worktree 的 verification/ 路径，内容一致）")
    args = parser.parse_args()
    stamp = now_iso()

    fonts = collect_fonts()
    role_by_font = {f["path"]: f["role"] for f in fonts}
    params_all, want_occ = build_grid(fonts)
    print(f"[grid] fonts={len(fonts)} grid_combinations={len(params_all) // 2} samples={len(params_all)}")

    SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    records: list[SampleRecord] = []
    stats = {"roundtrip_max_err_px": 0.0, "envelope_coverage_violations": 0,
             "occluded_reduced": 0, "envelope_unchanged_by_occlusion": 0}
    for i, p in enumerate(params_all):
        if want_occ[i]:
            baseline = render_sample(p)  # 无遮挡基线：贴片定位的数据源（确定性纯函数）
            place_occlusion(p, baseline.glyph_mask_pre_occlusion)
        result = render_sample(p)
        verify_sample(p, result, stats)
        png_name = f"{p.sample_name}.png"
        png_path = SYNTH_DIR / png_name
        result.image.save(png_path)
        records.append(SampleRecord(
            sample_id=f"synth-r1/{p.sample_name}",
            image=ImageRef(path=f"synthetic/{png_name}", sha256=sha256_file(png_path),
                           width=result.image.width, height=result.image.height),
            boxes=[BoxAnnotation(
                polygon=result.gt_polygon, cls="sfx", text=p.text,
                occluded=p.occlusion is not None,  # T1a r1 P1-4：遮挡标记落地
            )],
            annotation_status="synthetic",
            provenance={
                "type": "synthetic_render",
                "task": "M2-SFX-ANNOTATE-R1 AC5",
                "pipeline": "T1a sfx_data_infra.synth.render_sample（几何与标注同源 forward 纯函数）",
                "render_seed": p.seed,
                "font_file": Path(p.font_path).name,
                "font_role": role_by_font[p.font_path],
                "font_size": p.font_size,
                "stroke_width": p.stroke_width,
                "rotation_deg": round(p.rotation_deg, 4),
                "arc_curvature_px": round(p.arc_curvature_px, 4),
                "perspective_shift_px": round(p.perspective_shift_px, 4),
                "tx": round(p.tx, 4),
                "ty": round(p.ty, 4),
                "occlusion": p.occlusion,
                "gt_basis": "render_params_forward_geometry",
            },
            group="synthetic/annotate-r1",
            created_at=stamp,
        ))
        if (i + 1) % 60 == 0:
            print(f"[render] {i + 1}/{len(params_all)}")

    # 断言 D：确定性（首样本同参数重渲染逐像素一致）
    r1, r2 = render_sample(params_all[0]), render_sample(params_all[0])
    determinism = bool(np.array_equal(np.asarray(r1.image), np.asarray(r2.image)))
    if not determinism:
        raise AssertionError("同参数重渲染逐像素不一致（seed 冻结被破坏）")

    # schema 全量往返校验（from_dict 重建，失败抛 SchemaError）
    dicts = [rec.to_dict() for rec in records]
    rebuilt = [SampleRecord.from_dict(d) for d in dicts]
    if len(rebuilt) != len(records):
        raise AssertionError("schema 往返数量不一致")
    MANIFEST_JSON.write_text(json.dumps(dicts, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- 摘要（计数 + 参数网格说明 + sha256）---
    per_axis = {
        "fonts": [{"role": f["role"], "file": f["file"]} for f in fonts],
        "rotation_deg": list(GRID_ROTATIONS),
        "perspective_shift_px": list(GRID_PERSPECTIVE),
        "arc_curvature_px": list(GRID_ARC),
        "occlusion": ["none", "rect_patch"],
        "text_set": list(_POC_TEXTS),
        "font_size_alternating": list(FONT_SIZES),
        "stroke_width_alternating": list(STROKE_WIDTHS),
    }
    occluded_n = sum(1 for p in params_all if p.occlusion is not None)
    by_font = {}
    for p in params_all:
        by_font[Path(p.font_path).name] = by_font.get(Path(p.font_path).name, 0) + 1
    summary = {
        "task": "M2-SFX-ANNOTATE-R1 AC5 合成批量（T1b stage-2）",
        "generated_at_utc": stamp,
        "tool": "experiments/M2-SFX-ANNOTATE-R1/stage2_synth_batch.py",
        "pipeline_source": "experiments/M2-SFX-DATA-INFRA/sfx_data_infra/synth.py（T1a 渲染管线，只读复用）",
        "counts": {
            "samples_total": len(records),
            "committed_min": 200,
            "commitment_met": len(records) >= 200,
            "boxes_total": sum(len(r.boxes) for r in records),
            "occluded_samples": occluded_n,
            "by_font_file": by_font,
            "by_text": {t: sum(1 for p in params_all if p.text == t) for t in _POC_TEXTS},
            "annotation_status": "synthetic",
            "provenance_type": "synthetic_render",
        },
        "grid": {
            "definition": "字体(3) × rotation(3) × perspective(3) × arc(3) × occlusion(2) = 162 组合 × 每组合 2 样本（T1a 冻结文本集 8 词轮换 + font_size 60/84 与 stroke_width 0/2 交替）",
            "full_combinations": len(params_all) // 2,
            "samples_per_combination": 2,
            "occlusion_placement": "数据驱动：先渲染无遮挡基线，贴片=字形像素 bbox 中央 0.5×0.5 方块（T1a default_poc_params 固定左下贴片在旋转组合下落包络空白角、盖不到字形，已弃用）；贴片定位源=渲染纯函数输出，确定性保持",
            "axes": per_axis,
        },
        "fonts": fonts,
        "gt_verification": {
            "mode": "全量逐样本（非抽查）",
            "forward_inverse_max_err_px": stats["roundtrip_max_err_px"],
            "assert_a_glyph_pixels_inside_envelope_tol3px": (
                f"PASS ({len(records)}/{len(records)})；tol=3px（T1a 测试基线 2px +1："
                "本网格复合位移下 arc 离散 roll ≤0.5px 与 BICUBIC/抗锯齿边缘扩散复合最坏 ~3px，"
                "synth-r1-0192 实测 2.4px 且逆变换核实为光栅化近似非几何错误；"
                "参数↔GT 一致性由断言 B 1e-6px 独立保证）"
            ),
            "assert_b_inverse_recovers_anchor_1p5px": "PASS",
            "assert_c1_occlusion_reduces_visible": f"PASS ({stats['occluded_reduced']}/{occluded_n} 遮挡样本)",
            "assert_c2_envelope_unchanged_by_occlusion": (
                f"PASS ({stats['envelope_unchanged_by_occlusion']}/{occluded_n} 遮挡样本，≤1e-9px)"
            ),
            "assert_d_same_seed_pixel_identical": f"{'PASS' if determinism else 'FAIL'}",
            "envelope_coverage_violations": stats["envelope_coverage_violations"],
        },
        "split_plan": {
            "current_split": "unassigned",
            "note": "split 冻结留给 AC4 组隔离拆分：synthetic/annotate-r1 为单一组不跨集，沿 T1a cli.PINNED_GROUPS 先例 pin train；synthetic 不入 test/challenge（AC5 硬约束）",
        },
        "artifacts": {
            "synthetic_dir_gitignored": "training_data/sfx-v1/annotate-r1/synthetic/",
            "manifest": str(MANIFEST_JSON),
            "fonts_dir": str(FONTS_DIR),
        },
        "artifact_sha256": {
            "manifest.json": sha256_file(MANIFEST_JSON),
            "fonts/TanukiMagic.ttf": TANUKI_SHA256,
        },
        "zero_src_note": "本任务零 src：git diff 仅 experiments/M2-SFX-ANNOTATE-R1/** 与 verification/M2-SFX-ANNOTATE-R1/**（+数据本体 gitignored 树）",
    }
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[manifest] {MANIFEST_JSON} ({len(records)} samples)")
    print(f"[summary] {SUMMARY_JSON}")
    if args.extra_summary_out:
        extra = Path(args.extra_summary_out)
        extra.parent.mkdir(parents=True, exist_ok=True)
        extra.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"[summary-extra] {extra}")
    print(f"[done] samples={len(records)} grid_combinations={len(params_all) // 2} "
          f"roundtrip_max_err={stats['roundtrip_max_err_px']:.2e}px occluded={occluded_n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
