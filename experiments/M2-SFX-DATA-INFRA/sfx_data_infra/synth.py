"""AC4：合成渲染 PoC——参数↔GT 同步生成（桩——红绿纪律先红后绿）。"""

from __future__ import annotations

SYNTH_SEED = 20261004
POC_SAMPLE_COUNT = 24


def measure_anchor_box(params):
    """文字图层中字形包络 anchor box（渲染前坐标系）。"""
    raise NotImplementedError


def forward_transform_points(params, pts):
    """arc→rotate→perspective→translate 正向几何（与图像管线同一实现）。"""
    raise NotImplementedError


def inverse_transform_points(params, pts):
    """反向几何：translate→perspective⁻¹→rotate⁻¹→arc⁻¹。"""
    raise NotImplementedError


def render_sample(params):
    """渲染单样本，返回 (image, gt_polygon, glyph_mask_pre_occlusion, visible_glyph_mask)。"""
    raise NotImplementedError


def default_poc_params(seed: int = SYNTH_SEED, count: int = POC_SAMPLE_COUNT):
    """冻结 seed 的 ≥count 个 PoC 参数组合。"""
    raise NotImplementedError
