"""Direction resolution (pure) and the Qt layout engine (real fonts)."""

from __future__ import annotations

import rendering_helpers  # noqa: F401  (sys.path injection)

import pytest

from application.rendering.layout import resolve_direction
from application.rendering.style import TextDirection
from ports.rendering.ports import LayoutRequest, SourceStyle


class TestResolveDirection:
    def test_explicit_setting_wins(self) -> None:
        assert (
            resolve_direction(TextDirection.VERTICAL, 400, 100) is TextDirection.VERTICAL
        )
        assert (
            resolve_direction(TextDirection.HORIZONTAL, 100, 400)
            is TextDirection.HORIZONTAL
        )

    def test_source_hint_used_under_auto(self) -> None:
        hint = SourceStyle(
            detected_source_font_size=None,
            source_font_size_confidence=0.0,
            direction_hint=TextDirection.VERTICAL,
        )
        assert (
            resolve_direction(TextDirection.AUTO, 400, 100, hint)
            is TextDirection.VERTICAL
        )

    def test_aspect_ratio_tall_region_defaults_vertical(self) -> None:
        assert resolve_direction(TextDirection.AUTO, 100, 200) is TextDirection.VERTICAL

    def test_aspect_ratio_wide_region_defaults_horizontal(self) -> None:
        assert (
            resolve_direction(TextDirection.AUTO, 200, 100) is TextDirection.HORIZONTAL
        )


# ---------------------------------------------------------------------------
# Qt layout engine (real font metrics)
# ---------------------------------------------------------------------------

INSTALLED_CJK = "Microsoft YaHei"


@pytest.fixture()
def engine(qapp):  # noqa: F811 - fixture dependency
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine
    from infrastructure.rendering.font_catalog import QtFontCatalog

    return QtTextLayoutEngine(QtFontCatalog())


def request(**overrides) -> LayoutRequest:
    defaults = dict(
        text="测试文本",
        font_family=INSTALLED_CJK,
        font_size=26.0,
        direction=TextDirection.HORIZONTAL,
        box_width=300,
        box_height=200,
        stroke_width=3.0,
        line_spacing=1.0,
    )
    defaults.update(overrides)
    return LayoutRequest(**defaults)


class TestHorizontalLayout:
    def test_short_text_fits_single_line(self, engine) -> None:
        result = engine.layout(request(text="短文"))
        assert result.fits
        assert not any(item.per_char for item in result.items)
        assert len(result.items) == 1

    def test_long_text_wraps_within_box(self, engine) -> None:
        text = "一二三四五六七八九十" * 6  # 60 chars
        result = engine.layout(request(text=text, box_width=260, box_height=300))
        assert result.fits
        assert len(result.items) > 1
        assert result.extents_width <= 260 - 2 * 3.0
        assert result.extents_height <= 300 - 2 * 3.0

    def test_latin_words_are_not_split(self, engine) -> None:
        words = "hello wonderful translation".split(" ")
        result = engine.layout(request(text=" ".join(words), box_width=120, box_height=300))
        lines = [item.text for item in result.items]
        # every emitted line is composed of whole words only
        for line in lines:
            assert all(word in words for word in line.split(" ") if word)
        # and no word is lost
        joined = " ".join(lines).split(" ")
        assert sorted(w for w in joined if w) == sorted(words)

    def test_line_spacing_increases_extents_height(self, engine) -> None:
        text = "一二三四五六七八九十"
        tight = engine.layout(request(text=text, box_width=120, line_spacing=1.0))
        loose = engine.layout(request(text=text, box_width=120, line_spacing=1.5))
        assert loose.extents_height == pytest.approx(
            tight.extents_height * 1.5, rel=0.02
        )

    def test_unfittable_box_reports_not_fits(self, engine) -> None:
        result = engine.layout(request(text="一二三四五六七八九十", box_width=40, box_height=30))
        assert not result.fits


class TestVerticalLayout:
    def test_tall_text_lays_out_right_to_left_columns(self, engine) -> None:
        text = "一二三四五六七八九十"  # 10 chars, 5 per column
        result = engine.layout(
            request(text=text, direction=TextDirection.VERTICAL, box_width=200, box_height=200)
        )
        assert result.fits
        assert all(item.per_char for item in result.items)
        # columns proceed right-to-left: the first char has the largest x
        assert result.items[0].x > result.items[-1].x
        # inside one column, y increases char by char
        first_col = [item for item in result.items if item.x == result.items[0].x]
        ys = [item.y for item in first_col]
        assert ys == sorted(ys)

    def test_vertical_fits_box(self, engine) -> None:
        text = "縦書きのテスト" * 3
        result = engine.layout(
            request(text=text, direction=TextDirection.VERTICAL, box_width=200, box_height=150)
        )
        assert result.fits
        assert result.extents_width <= 200 - 6.0
        assert result.extents_height <= 150 - 6.0


class TestFontAvailability:
    def test_missing_font_falls_back_and_is_reported(self, engine) -> None:
        result = engine.layout(request(font_family="NoSuchFont-ZZZ", text="缺字体"))
        assert result.font_available is False
        assert result.resolved_family  # some installed family
        assert result.items  # layout still produced

    def test_installed_font_is_reported_available(self, engine) -> None:
        result = engine.layout(request(text="正常"))
        assert result.font_available is True
        assert result.resolved_family == INSTALLED_CJK


class TestResolutionIntegration:
    def test_shrink_to_fit_with_real_metrics(self, engine) -> None:
        from application.rendering.style import RenderTextStyle, resolve_font_size

        style = RenderTextStyle(font_family=INSTALLED_CJK)
        text = "这是一段很长的译文文本，需要缩小字号才能放进区域里。"

        def fits(size: float) -> bool:
            result = engine.layout(
                request(text=text, font_size=size, box_width=150, box_height=60)
            )
            return result.fits

        assert not fits(26.0)
        resolution = resolve_font_size(style, fits)
        assert resolution.shrunk
        assert resolution.final_font_size < 26.0
        assert fits(resolution.final_font_size)
