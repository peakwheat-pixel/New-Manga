"""Font-size resolution chain (D03 §11.1, AC-STYLE-001..005, D06 §23).

All cases run against the deterministic FixedMetricsProbe so fits are
exact; the real Qt layout engine is exercised in test_layout_qt.py.
"""

from __future__ import annotations

import pytest

import helpers  # noqa: F401  (sys.path injection)

from application.rendering.style import (
    DEFAULT_FALLBACK_FONT_SIZE,
    RELIABLE_SOURCE_SIZE_CONFIDENCE,
    RenderTextStyle,
    StyleResolutionError,
    resolve_font_size,
)
from helpers import make_probe


def style(**overrides) -> RenderTextStyle:
    defaults = dict(
        detected_source_font_size=26.0,
        source_font_size_confidence=0.9,
    )
    defaults.update(overrides)
    return RenderTextStyle(**defaults)


class TestOffsetRange:
    def test_offset_boundaries_are_inclusive(self) -> None:
        assert RenderTextStyle(font_size_offset=-5).font_size_offset == -5
        assert RenderTextStyle(font_size_offset=5).font_size_offset == 5

    @pytest.mark.parametrize("bad", [-6, 6, -100, 100])
    def test_offset_out_of_range_is_rejected(self, bad: int) -> None:
        with pytest.raises(ValueError, match="font_size_offset"):
            RenderTextStyle(font_size_offset=bad)


class TestAutoBase:
    def test_reliable_source_size_is_used_as_base(self) -> None:
        # D03 §11.2 example shape: base + offset = candidate.
        probe = make_probe("短", box_w=200, box_h=200)
        result = resolve_font_size(style(detected_source_font_size=28.0, font_size_offset=3), probe)
        assert result.base_font_size == 28.0
        assert result.final_font_size == 31.0
        assert not result.used_fallback

    def test_unreliable_confidence_falls_back_to_26(self) -> None:
        probe = make_probe("短", box_w=200, box_h=200)
        result = resolve_font_size(
            style(detected_source_font_size=40.0, source_font_size_confidence=0.1), probe
        )
        assert result.base_font_size == DEFAULT_FALLBACK_FONT_SIZE
        assert result.used_fallback
        assert result.final_font_size == DEFAULT_FALLBACK_FONT_SIZE

    def test_missing_detection_falls_back_to_26(self) -> None:
        probe = make_probe("短", box_w=200, box_h=200)
        result = resolve_font_size(style(detected_source_font_size=None), probe)
        assert result.used_fallback
        assert result.base_font_size == DEFAULT_FALLBACK_FONT_SIZE

    def test_confidence_threshold_is_inclusive(self) -> None:
        probe = make_probe("短", box_w=200, box_h=200)
        result = resolve_font_size(
            style(source_font_size_confidence=RELIABLE_SOURCE_SIZE_CONFIDENCE), probe
        )
        assert not result.used_fallback


class TestNoAutoEnlarge:
    def test_short_text_never_exceeds_candidate(self) -> None:
        probe = make_probe("猫", box_w=500, box_h=500)
        result = resolve_font_size(style(detected_source_font_size=20.0), probe)
        # Short text must not push the size above base (no auto-enlarge).
        assert result.final_font_size == 20.0
        assert not result.shrunk


class TestShrinkToFit:
    def test_overflowing_text_is_shrunk_until_it_fits(self) -> None:
        # box 100x100: at size 26 -> 3 chars/line, 2 lines * 26 = 52 <= 100 fits.
        # Use a long text so 26 overflows: 12 chars -> 3 lines at 26 = 78 fits...
        # pick text/box so only shrinking helps: 12 chars, box 60x40.
        # size 26: chars/line=2, lines=6, height=156 > 40 -> shrink
        # size 13: chars/line=4, lines=3, height=39 <= 40 -> fits
        probe = make_probe("一二三四五六七八九十百千", box_w=60, box_h=40)
        result = resolve_font_size(style(detected_source_font_size=26.0), probe)
        assert result.shrunk
        assert result.final_font_size < 26.0
        # verify the reported size actually fits under the model
        assert probe(result.final_font_size)
        # shrink keeps text inside, never returns an overflowing size
        assert result.final_font_size <= 26.0

    def test_shrink_prefers_the_largest_fitting_size(self) -> None:
        probe = make_probe("一二三四五六七八九十百千", box_w=60, box_h=40)
        result = resolve_font_size(style(detected_source_font_size=26.0), probe)
        # nothing between final and candidate may fit (maximality)
        for size in (result.final_font_size + 0.5, 26.0):
            assert not probe(size) or size <= result.final_font_size

    def test_unfittable_text_raises_a_diagnosable_error(self) -> None:
        # 8 chars, box 4x4: even at size 1 -> 4 chars/line, 2 lines * 1.0 = 2
        # height fits, but pick a box where nothing fits: 3x1.
        probe = make_probe("一二三四五六七八", box_w=3, box_h=1)
        with pytest.raises(StyleResolutionError, match="cannot fit"):
            resolve_font_size(style(detected_source_font_size=26.0), probe)


class TestManualMode:
    def test_disabled_auto_uses_manual_size_directly(self) -> None:
        probe = make_probe("长" * 40, box_w=30, box_h=30)
        result = resolve_font_size(
            style(auto_font_size_enabled=False, manual_font_size=42.0), probe
        )
        # AC-STYLE-005: manual size is kept, explicitly allowed to break the
        # automatic limits (no shrink applied even though it cannot fit).
        assert result.final_font_size == 42.0
        assert not result.shrunk
        assert not result.auto

    def test_disabled_auto_without_manual_size_is_diagnosed(self) -> None:
        probe = make_probe("文", box_w=100, box_h=100)
        with pytest.raises(StyleResolutionError, match="manual"):
            resolve_font_size(style(auto_font_size_enabled=False), probe)

    def test_negative_manual_size_is_rejected_at_construction(self) -> None:
        with pytest.raises(ValueError, match="manual_font_size"):
            RenderTextStyle(manual_font_size=0)


class TestDefaultsFromDomain:
    def test_defaults_match_d03_11_6(self) -> None:
        base = RenderTextStyle()
        assert base.auto_font_size_enabled is True
        assert base.text_color == "#000000"
        assert base.fill_color == "#FFFFFF"
        assert base.stroke_enabled is True
        assert base.stroke_color == "#FFFFFF"
        assert base.stroke_width == 3.0
        assert base.line_spacing == 1.0
        assert base.text_align == "start"
        assert base.overflow_policy == "shrink_to_fit"

    def test_from_domain_carries_task008_snapshot_fields(self) -> None:
        from domain.regions.entities import TextStyle

        domain_style = TextStyle(
            font_family="MyFont",
            font_size=None,
            text_color="#123456",
            stroke_color="#abcdef",
            stroke_width=2.5,
            auto_font_size_enabled=False,
        )
        merged = RenderTextStyle.from_domain(domain_style)
        assert merged.font_family == "MyFont"
        assert merged.text_color == "#123456"
        assert merged.stroke_color == "#abcdef"
        assert merged.stroke_width == 2.5
        assert merged.auto_font_size_enabled is False
        # fields absent from the domain snapshot keep D03 defaults
        assert merged.stroke_enabled is True
        assert merged.line_spacing == 1.0
