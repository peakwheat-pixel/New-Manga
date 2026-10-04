"""AC4：合成渲染 PoC——几何与标注由同一渲染参数直接产生=精确 GT。

管线（点与像素走同一几何函数，保证标注↔图像↔参数三方一致）：
  1) 文字图层：font 渲染 text 到 RGBA layer，anchor box=字形包络（渲染前坐标系）；
  2) arc 弯曲：逐列垂直位移 dy(x)=A·sin(π(x−ax0)/(ax1−ax0))，像素=整列 np.roll，
     点=连续公式（离散差 ≤0.5px，断言容差覆盖）；
  3) rotate：绕 anchor 中心 R(θ)。像素=Image.transform(AFFINE, Rᵀ 逆映射)，
     输出原点=旋转后 16 采样点 bounding 的 −min（记 off）；点=同一 R 与同一 off；
  4) perspective+平移：src=旋转后四角（含 off），dst=forward(corners4)——
     dst 由纯函数 forward_transform_points 给出（梯形位移 s+平移 (tx,ty)），
     H=solve(src4,dst4)。像素=transform(PERSPECTIVE, H⁻¹)，点=H；
  5) GT 包络 = forward(anchor 采样点)；遮挡贴片绘制在文字上方，GT 包络保持
     完整（口径冻结：sfx 实例包络含遮挡推断）。

AI 整图生成不在本 PoC 内；若后续引入，annotation_status 必须标 `pseudo` 且不入 GT
（schema 枚举已冻结该语义）。
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

SYNTH_SEED = 20261004
POC_SAMPLE_COUNT = 24

# 系统字体候选（回退位）。毛笔/手写风字体经 discover_fonts 的 extra_dirs /
# NEWMANGA_SFX_SYNTH_FONTS 提供（r2 接入 TanukiMagic=たぬき油性マジック，OFL），
# 名字命中关键词者优先级高于系统字体——AC4"毛笔体/艺术字字体"由此满足。
_FONT_CANDIDATES = (
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
    r"C:\Windows\Fonts\YuGothR.ttc",
    r"C:\Windows\Fonts\malgun.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\ariblk.ttf",
)

# r2 新-5：收窄启发式——"pen"/"hand"/"magic" 会误命中 opensans 等普通字体
_BRUSHY_NAME_HINTS = ("tanuki", "brush", "fude", "kouzan")

_POC_TEXTS = ("ドン", "ゴゴゴ", "バーン", "ザッ", "オギャァ", "メキメキ", "ズシャア", "ビシッ")

# anchor 边界采样密度：每边 15 个中间点（arc 大曲率下折线弦差 <<1px）
_EDGE_SAMPLES = 15
# 路径序中四个角点的索引：tl / tr / br / bl（每边 _EDGE_SAMPLES 个中间点 + 1 角）
ANCHOR_CORNER_IDX = (0, _EDGE_SAMPLES + 1, 2 * (_EDGE_SAMPLES + 1), 3 * (_EDGE_SAMPLES + 1))


def discover_fonts(limit: int = 4, extra_dirs: Optional[list] = None) -> list[str]:
    """返回可用字体路径：毛笔/手写风优先，回退系统字体。

    extra_dirs 与环境变量 NEWMANGA_SFX_SYNTH_FONTS（os.pathsep 分隔）目录下的
    .ttf/.otf/.ttc，文件名命中 _BRUSHY_NAME_HINTS 者排到系统字体之前。
    """
    import os
    from pathlib import Path

    dirs = list(extra_dirs or [])
    env = os.environ.get("NEWMANGA_SFX_SYNTH_FONTS", "")
    if env:
        dirs.extend(s for s in env.split(os.pathsep) if s)

    brushy: list[str] = []
    plain: list[str] = []
    for d in dirs:
        try:
            dp = Path(d)
            if not dp.is_dir():
                continue
            for f in sorted(dp.iterdir()):
                if f.suffix.lower() not in (".ttf", ".otf", ".ttc"):
                    continue
                target = brushy if any(h in f.stem.lower() for h in _BRUSHY_NAME_HINTS) else plain
                target.append(str(f))
        except OSError:
            continue
    for p in _FONT_CANDIDATES:
        try:
            if Path(p).exists():
                plain.append(p)
        except OSError:
            continue
    out = (brushy + plain)[:limit]
    if not out:
        raise RuntimeError("系统字体目录无可字体，无法渲染 PoC")
    return out


@dataclass
class RenderParams:
    sample_name: str
    text: str
    font_path: str
    font_size: int
    canvas_w: int
    canvas_h: int
    rotation_deg: float
    arc_curvature_px: float
    perspective_shift_px: float
    tx: float
    ty: float
    text_color: tuple = (17, 17, 17)
    stroke_width: int = 0
    stroke_fill: tuple = (255, 255, 255)
    occlusion: Optional[dict] = None  # {'shape':'rect','box':[x0,y0,x1,y1]} canvas 坐标
    seed: int = SYNTH_SEED


@dataclass
class RenderResult:
    image: Image.Image
    gt_polygon: list[list[float]]
    glyph_mask_pre_occlusion: np.ndarray
    visible_glyph_mask: np.ndarray


# ---------------------------------------------------------------- 几何（纯函数）


def measure_anchor_box(params: RenderParams) -> tuple[float, float, float, float]:
    """文字图层中字形包络 anchor box（渲染前坐标系，与 render 同一测量）。"""
    font = ImageFont.truetype(params.font_path, params.font_size)
    probe = Image.new("L", (8, 8))
    d = ImageDraw.Draw(probe)
    bbox = d.textbbox((0, 0), params.text, font=font, stroke_width=params.stroke_width)
    return (float(bbox[0]), float(bbox[1]), float(bbox[2]), float(bbox[3]))


def anchor_points(params: RenderParams) -> np.ndarray:
    """anchor 边界采样点，路径序（tl→上边→tr→右边→br→下边→bl→左边）。

    路径序保证该点列可直接作为非自交多边形用于 GT 包络填充/面积计算；
    forward∘inverse 对全部点列数值精确可逆（互算断言用全量点）。
    """
    x0, y0, x1, y1 = measure_anchor_box(params)
    ts = [i / (_EDGE_SAMPLES + 1) for i in range(1, _EDGE_SAMPLES + 1)]
    pts: list[list[float]] = [[x0, y0]]
    pts += [[x0 + (x1 - x0) * t, y0] for t in ts]  # 上边
    pts += [[x1, y0]]
    pts += [[x1, y0 + (y1 - y0) * t] for t in ts]  # 右边
    pts += [[x1, y1]]
    pts += [[x0 + (x1 - x0) * t, y1] for t in reversed(ts)]  # 下边（反向）
    pts += [[x0, y1]]
    pts += [[x0, y0 + (y1 - y0) * t] for t in reversed(ts)]  # 左边（反向）
    return np.asarray(pts, dtype=np.float64)


def _arc_dy(x: float, params: RenderParams, anchor: tuple) -> float:
    x0, _, x1, _ = anchor
    if x1 <= x0:
        return 0.0
    return params.arc_curvature_px * math.sin(math.pi * (x - x0) / (x1 - x0))


def _rot_matrix(theta_deg: float) -> np.ndarray:
    t = math.radians(theta_deg)
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s], [s, c]], dtype=np.float64)


def _homography_from_correspondences(src4: np.ndarray, dst4: np.ndarray) -> np.ndarray:
    """4 点精确单应求解（DLT）。"""
    rows = []
    for (x, y), (u, v) in zip(src4, dst4):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    a = np.asarray(rows, dtype=np.float64)
    _, _, vt = np.linalg.svd(a)
    h = vt[-1].reshape(3, 3)
    return h / h[2, 2]


def _rotate_stage(params: RenderParams, pts: np.ndarray):
    """arc→rotate（无出界平移）。返回 (arc 后点, 旋转后点, anchor)。"""
    anchor = measure_anchor_box(params)
    s1 = pts.copy()
    s1[:, 1] += np.array([_arc_dy(float(x), params, anchor) for x in s1[:, 0]])
    cx, cy = (anchor[0] + anchor[2]) / 2.0, (anchor[1] + anchor[3]) / 2.0
    r = _rot_matrix(params.rotation_deg)
    s2 = (r @ (s1 - np.array([cx, cy])).T).T + np.array([cx, cy])
    return s1, s2, (anchor, np.array([cx, cy]), r)


def forward_transform_points(params: RenderParams, pts) -> np.ndarray:
    """正向几何纯函数：arc→rotate→perspective+translate（canvas 坐标）。

    dst4 = 旋转后四角施加梯形位移（±s/2）+ 平移 (tx,ty)；单应 H 由
    (旋转后四角 → dst4) 精确构造，对所有点生效。
    """
    pts = np.asarray(pts, dtype=np.float64)
    if pts.ndim == 1:
        pts = pts[None, :]
    corners = anchor_points(params)
    _, s2c, _ = _rotate_stage(params, corners)
    s = params.perspective_shift_px
    dst4 = s2c[list(ANCHOR_CORNER_IDX)].copy()
    dst4[0, 0] -= s / 2.0
    dst4[1, 0] += s / 2.0
    dst4[2, 0] += s / 2.0
    dst4[3, 0] -= s / 2.0
    dst4[:, 0] += params.tx
    dst4[:, 1] += params.ty
    h = _homography_from_correspondences(s2c[list(ANCHOR_CORNER_IDX)], dst4)
    # 输入点必须走同一 arc→rotate 前段，再套 H
    _, s_pts, _ = _rotate_stage(params, pts)
    ones = np.concatenate([s_pts, np.ones((len(s_pts), 1))], axis=1)
    out = (h @ ones.T).T
    return out[:, :2] / out[:, 2:3]


def inverse_transform_points(params: RenderParams, pts) -> np.ndarray:
    """反向几何：H⁻¹→rotate⁻¹→arc⁻¹（数值上精确可逆，供 GT↔参数互算）。"""
    pts = np.asarray(pts, dtype=np.float64)
    if pts.ndim == 1:
        pts = pts[None, :]
    corners = anchor_points(params)
    _, s2, (anchor, center, r) = _rotate_stage(params, corners)
    s = params.perspective_shift_px
    dst4 = s2[list(ANCHOR_CORNER_IDX)].copy()
    dst4[0, 0] -= s / 2.0
    dst4[1, 0] += s / 2.0
    dst4[2, 0] += s / 2.0
    dst4[3, 0] -= s / 2.0
    dst4[:, 0] += params.tx
    dst4[:, 1] += params.ty
    h = _homography_from_correspondences(s2[list(ANCHOR_CORNER_IDX)], dst4)
    hinv = np.linalg.inv(h)
    ones = np.concatenate([pts, np.ones((len(pts), 1))], axis=1)
    s2p = (hinv @ ones.T).T
    s2p = s2p[:, :2] / s2p[:, 2:3]
    s1 = (r.T @ (s2p - center).T).T + center
    out = s1.copy()
    out[:, 1] -= np.array([_arc_dy(float(x), params, anchor) for x in out[:, 0]])
    return out


# ---------------------------------------------------------------- 图像管线


def _warp_affine(layer: Image.Image, r: np.ndarray, center: np.ndarray, off: np.ndarray, out_size) -> Image.Image:
    """旋转 warp。点正向 p'=R(p−c)+c+off ⇒ 输出→输入逆映射 p_in=Rᵀ(p_out−off−c)+c。"""
    rinv = r.T
    a, b = float(rinv[0, 0]), float(rinv[0, 1])
    d, e = float(rinv[1, 0]), float(rinv[1, 1])
    shift = center + off
    tx = -(a * shift[0] + b * shift[1]) + float(center[0])
    ty = -(d * shift[0] + e * shift[1]) + float(center[1])
    coeffs = (a, b, tx, d, e, ty)
    return layer.transform(out_size, Image.AFFINE, coeffs, resample=Image.BICUBIC)


def _warp_homography(layer: Image.Image, h: np.ndarray, out_size) -> Image.Image:
    hinv = np.linalg.inv(h)
    hinv = hinv / hinv[2, 2]
    coeffs = (hinv[0, 0], hinv[0, 1], hinv[0, 2], hinv[1, 0], hinv[1, 1], hinv[1, 2], hinv[2, 0], hinv[2, 1])
    return layer.transform(out_size, Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC)


def _solve_h_full(params: RenderParams, s2p4: np.ndarray) -> np.ndarray:
    """像素管线第二段 H：src=旋转后四角（含 off），dst=forward 四角。"""
    corners = anchor_points(params)[list(ANCHOR_CORNER_IDX)]
    dst4 = forward_transform_points(params, corners)
    return _homography_from_correspondences(s2p4, dst4)


def render_sample(params: RenderParams) -> RenderResult:
    """渲染单样本：几何与 GT 同源生成。"""
    w, hgt = params.canvas_w, params.canvas_h
    font = ImageFont.truetype(params.font_path, params.font_size)

    # 1) 文字图层（透明底）
    layer = Image.new("RGBA", (w, hgt), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text((0, 0), params.text, font=font, fill=params.text_color,
           stroke_width=params.stroke_width, stroke_fill=params.stroke_fill)
    if not (np.asarray(layer)[:, :, 3] > 0).any():
        raise RuntimeError(f"{params.sample_name}: 文字渲染为空（font/text 不兼容）")

    # 2) arc：整列位移（文字只占 anchor 列，列外为透明，roll 无害）
    anchor = measure_anchor_box(params)
    arr = np.asarray(layer).copy()
    for x in range(max(int(math.floor(anchor[0])), 0), min(int(math.ceil(anchor[2])), w)):
        shift = int(round(_arc_dy(float(x), params, anchor)))
        if shift:
            arr[:, x] = np.roll(arr[:, x], shift, axis=0)
    layer = Image.fromarray(arr)

    # 3) rotate：off=旋转后采样点 bounding 的 −min（与点函数一致）
    pts = anchor_points(params)
    _, s2, (anchor, center, r) = _rotate_stage(params, pts)
    off = -np.minimum(s2.min(axis=0), 0.0)
    size_rot = (int(math.ceil((s2[:, 0] + off[0]).max())) + 2,
                int(math.ceil((s2[:, 1] + off[1]).max())) + 2)
    layer = _warp_affine(layer, r, center, off, size_rot)

    # 4) perspective+translate：src=含 off 四角，dst=forward 四角
    h_full = _solve_h_full(params, s2[list(ANCHOR_CORNER_IDX)] + off)
    layer = _warp_homography(layer, h_full, (w, hgt))

    # 5) GT 包络（与像素同一 forward 纯函数）
    fwd = forward_transform_points(params, pts)
    gt_polygon = [[float(x), float(y)] for x, y in fwd]

    # 6) 底图合成（浅噪底，rng 用 params.seed 保证确定性渲染）
    canvas = Image.new("RGB", (w, hgt), (245, 245, 245))
    rng_np = np.random.default_rng(params.seed)
    noise_arr = rng_np.integers(0, 256, size=(hgt, w), dtype=np.uint8)
    noise = Image.fromarray(noise_arr, "L")
    canvas = Image.blend(canvas, Image.merge("RGB", (noise, noise, noise)), 0.10)
    glyph_mask_pre = np.zeros((hgt, w), dtype=bool)
    glyph_mask_pre |= np.asarray(layer)[:, :, 3] > 0
    canvas = Image.alpha_composite(canvas.convert("RGBA"), layer).convert("RGB")

    # 7) 遮挡贴片（画在文字上方；GT 包络保持完整=包络含遮挡推断）
    visible = glyph_mask_pre.copy()
    if params.occlusion is not None:
        occ = params.occlusion
        if occ.get("shape") != "rect":
            raise ValueError(f"暂只支持 rect 遮挡: {occ}")
        bx0, by0, bx1, by1 = (int(v) for v in occ["box"])
        ImageDraw.Draw(canvas).rectangle([bx0, by0, bx1, by1], fill=(255, 255, 255),
                                         outline=(30, 30, 30), width=3)
        visible[max(by0 - 1, 0): min(by1 + 2, hgt), max(bx0 - 1, 0): min(bx1 + 2, w)] = False

    return RenderResult(
        image=canvas,
        gt_polygon=gt_polygon,
        glyph_mask_pre_occlusion=glyph_mask_pre,
        visible_glyph_mask=visible,
    )


# ---------------------------------------------------------------- 参数集


def default_poc_params(
    seed: int = SYNTH_SEED, count: int = POC_SAMPLE_COUNT, fonts: Optional[list] = None
) -> list[RenderParams]:
    """冻结 seed 的 PoC 参数组合（1/3 含遮挡贴片）。

    fonts 不传时自动发现（毛笔/手写风优先）；cli 传入 data_root/fonts 的发现
    结果以保证管线调用与字体目录约定一致。
    """
    rng = random.Random(seed)
    fonts = fonts if fonts is not None else discover_fonts()
    out: list[RenderParams] = []
    for i in range(count):
        text = _POC_TEXTS[i % len(_POC_TEXTS)]
        font = fonts[i % len(fonts)]
        p = RenderParams(
            sample_name=f"synth-{i:02d}-{text}",
            text=text,
            font_path=font,
            font_size=rng.randint(44, 92),
            canvas_w=rng.randint(320, 480),
            canvas_h=rng.randint(220, 360),
            rotation_deg=rng.uniform(-25.0, 25.0),
            arc_curvature_px=0.0 if rng.random() < 0.15 else rng.uniform(-35.0, 35.0),
            perspective_shift_px=0.0 if rng.random() < 0.25 else rng.uniform(8.0, 48.0),
            tx=0.0,
            ty=0.0,
            stroke_width=rng.choice([0, 0, 1, 2]),
            seed=seed + i,
        )
        # 居中平移：先零平移 forward 求 bounding，再回填 tx/ty（参数仍是冻结值）
        c = anchor_points(p)
        raw = forward_transform_points(p, c)
        lo, hi = raw.min(axis=0), raw.max(axis=0)
        p.tx = float((p.canvas_w - (hi[0] - lo[0])) / 2.0 - lo[0])
        p.ty = float((p.canvas_h - (hi[1] - lo[1])) / 2.0 - lo[1])
        if i % 3 == 0:
            bb = forward_transform_points(p, c)
            x0, y0 = bb[:, 0].min(), bb[:, 1].min()
            x1, y1 = bb[:, 0].max(), bb[:, 1].max()
            p.occlusion = {
                "shape": "rect",
                "box": [float(x0 - 6), float((y0 + y1) / 2.0 - 4), float(x0 + (x1 - x0) * 0.55), float(y1 + 8)],
            }
        out.append(p)
    return out
