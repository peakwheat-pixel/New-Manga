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
    default_poc_params,
    forward_transform_points,
    inverse_transform_points,
    measure_anchor_box,
    render_sample,
)


def polygon_mask_contains(polygon, xy, tol=2.0):
    """射线法+外扩容差：判断点集是否都在多边形内（含 tol px 缓冲）。"""
    poly = np.asarray(polygon, dtype=np.float64)
    cx, cy = poly[:, 0].mean(), poly[:, 1].mean()
    # 外扩：顶点沿远离质心方向推 tol
    vec = poly - np.array([cx, cy])
    norm = np.linalg.norm(vec, axis=1, keepdims=True)
    norm[norm == 0] = 1.0
    grown = poly + vec / norm * tol
    inside = np.ones(len(xy), dtype=bool)
    n = len(grown)
    for i in range(n):
        x1, y1 = grown[i]
        x2, y2 = grown[(i + 1) % n]
        cond = ((x2 - x1) * (xy[:, 1] - y1) - (y2 - y1) * (xy[:, 0] - x1)) > 0
        # 统一环绕方向
        if i == 0 and cond.sum() < len(cond) / 2:
            cond = ~cond
            flip = True
        elif i == 0:
            flip = False
        if flip:
            cond = ~cond
        inside &= cond
    return inside


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
    """断言 B：GT 包络逆变换 → anchor box（标注↔参数互算，≤1.5px）。"""
    params, results = poc
    for p, r in zip(params, results):
        anchor = np.asarray(measure_anchor_box(p), dtype=np.float64)  # 4 角
        corners = np.asarray(r.gt_polygon[:4], dtype=np.float64)
        recovered = inverse_transform_points(p, corners)
        err = np.abs(recovered - anchor).max()
        assert err <= 1.5, f"样本 {p.sample_name}: 逆变换角点误差 {err:.3f}px > 1.5px"


def test_occluded_samples_keep_full_envelope(poc):
    """断言 C：遮挡样本 GT 包络面积 > 可见字形 bbox 面积（遮挡推断）。"""
    params, results = poc
    occ_pairs = [(p, r) for p, r in zip(params, results) if p.occlusion is not None]
    assert occ_pairs, "参数集必须包含遮挡样本"
    for p, r in occ_pairs:
        mask = r.visible_glyph_mask
        ys, xs = np.nonzero(mask)
        assert len(xs) > 0, f"样本 {p.sample_name} 遮挡后应仍有可见字形"
        vis_bbox_area = (xs.max() - xs.min() + 1) * (ys.max() - ys.min() + 1)
        poly = np.asarray(r.gt_polygon, dtype=np.float64)
        gt_area = 0.5 * abs(
            np.dot(poly[:, 0], np.roll(poly[:, 1], -1)) - np.dot(poly[:, 1], np.roll(poly[:, 0], -1))
        )
        assert gt_area > vis_bbox_area, (
            f"样本 {p.sample_name}: GT 面积 {gt_area:.0f} 应大于可见字形 bbox 面积 {vis_bbox_area}"
        )


def test_render_deterministic_same_seed():
    from sfx_data_infra.synth import default_poc_params, render_sample

    p = default_poc_params(count=1)[0]
    r1 = render_sample(p)
    r2 = render_sample(p)
    a1, a2 = np.asarray(r1.image), np.asarray(r2.image)
    assert np.array_equal(a1, a2), "同参数渲染必须逐像素一致（seed 冻结）"
