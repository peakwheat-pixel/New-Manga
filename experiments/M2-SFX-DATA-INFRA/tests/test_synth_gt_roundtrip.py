"""AC4 红绿测试：合成渲染 GT 往返一致。

合同测试表场景「AC4 GT 互算」：渲染参数↔标注往返一致断言。
三条独立验证路径：
  A 前向：渲染字形像素全部落在 GT 包络内（图像↔标注一致）；
  B 反向：GT 包络经逆几何还原 anchor box（标注↔参数互算）；
  C 遮挡推断：遮挡样本 GT 包络 > 可见字形 bbox（包络含遮挡推断口径）。
"""

from __future__ import annotations

import numpy as np
import pytest

from sfx_data_infra.synth import (
    POC_SAMPLE_COUNT,
    anchor_points,
    default_poc_params,
    forward_transform_points,
    inverse_transform_points,
    measure_anchor_box,
    render_sample,
)


def polygon_mask_contains(polygon, xy, tol=2.0, canvas=(640, 640)):
    """PIL polygon fill raster + tol px 邻域膨胀：字形像素是否都在多边形内。"""
    from PIL import Image, ImageDraw

    w = int(max(x for x, _ in polygon) + canvas[0])
    h = int(max(y for _, y in polygon) + canvas[1])
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon([tuple(pt) for pt in polygon], fill=1)
    m = np.asarray(mask, dtype=bool)
    ys, xs = xy[:, 1].astype(int), xy[:, 0].astype(int)
    if tol > 0:
        # 容差：邻域 (2*tol+1)^2 内任一像素在多边形内即算覆盖
        acc = m.copy()
        for dy in range(-int(tol), int(tol) + 1):
            for dx in range(-int(tol), int(tol) + 1):
                acc |= np.roll(np.roll(m, dy, axis=0), dx, axis=1)
        m = acc
    return m[ys, xs]


@pytest.fixture(scope="module")
def poc():
    params = default_poc_params()
    results = [render_sample(p) for p in params]
    return params, results


def test_at_least_20_poc_samples(poc):
    params, results = poc
    assert len(params) >= 20
    assert len(results) == len(params)


def test_forward_glyph_pixels_inside_gt_envelope(poc):
    """断言 A：字形像素 ⊆ GT 包络（容差 2px）。"""
    params, results = poc
    for p, r in zip(params, results):
        mask = r.glyph_mask_pre_occlusion
        ys, xs = np.nonzero(mask)
        assert len(xs) > 0, f"样本 {p.sample_name} 字形 mask 为空"
        xy = np.stack([xs, ys], axis=1).astype(np.float64)
        inside = polygon_mask_contains(r.gt_polygon, xy, tol=2.0)
        bad = int((~inside).sum())
        assert bad == 0, f"样本 {p.sample_name}: {bad} 个字形像素落在 GT 包络外"


def test_inverse_transform_recovers_anchor_box(poc):
    """断言 B：GT 包络全部采样点逆变换 → anchor 点列（标注↔参数互算，≤1.5px）。"""
    params, results = poc
    for p, r in zip(params, results):
        anchor = anchor_points(p)
        assert len(r.gt_polygon) == len(anchor), "GT 包络点数必须与 anchor 采样点数一致"
        recovered = inverse_transform_points(p, np.asarray(r.gt_polygon, dtype=np.float64))
        err = np.abs(recovered - anchor).max()
        assert err <= 1.5, f"样本 {p.sample_name}: 逆变换点列误差 {err:.3f}px > 1.5px"


def test_occluded_samples_keep_full_envelope(poc):
    """断言 C（包络含遮挡推断口径）：
    C1 遮挡确实削减可见字形（可见 px < 遮挡前 px，且仍有剩余）；
    C2 GT 包络与无遮挡 forward 逐点一致——标注不因遮挡改变，完整覆盖真实字形。
    """
    import copy as _copy

    from sfx_data_infra.synth import forward_transform_points, anchor_points

    params, results = poc
    occ_pairs = [(p, r) for p, r in zip(params, results) if p.occlusion is not None]
    assert occ_pairs, "参数集必须包含遮挡样本"
    for p, r in occ_pairs:
        pre_px = int(r.glyph_mask_pre_occlusion.sum())
        vis_px = int(r.visible_glyph_mask.sum())
        assert vis_px < pre_px, f"样本 {p.sample_name}: 遮挡未削减可见字形 ({vis_px}/{pre_px})"
        assert vis_px > 0, f"样本 {p.sample_name}: 遮挡后应仍有可见字形"
        # C2：包络不依赖遮挡（同参数 occlusion=None 的 forward 逐点一致）
        q = _copy.deepcopy(p)
        q.occlusion = None
        expect = forward_transform_points(q, anchor_points(q))
        got = np.asarray(r.gt_polygon, dtype=np.float64)
        assert np.abs(got - expect).max() <= 1e-9, f"样本 {p.sample_name}: GT 包络被遮挡改变（违反包络口径）"


def test_render_deterministic_same_seed():
    from sfx_data_infra.synth import default_poc_params, render_sample

    p = default_poc_params(count=1)[0]
    r1 = render_sample(p)
    r2 = render_sample(p)
    a1, a2 = np.asarray(r1.image), np.asarray(r2.image)
    assert np.array_equal(a1, a2), "同参数渲染必须逐像素一致（seed 冻结）"
