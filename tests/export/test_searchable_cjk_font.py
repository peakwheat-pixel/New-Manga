"""SEARCHABLE-PDF-CJK-1 AC1/AC2: Korean pages can carry a searchable text layer.

Before this change _embedded_font tried only msyh.ttc and arial.ttf. Neither
carries Hangul, so a Korean page raised

    ValueError: no installed embeddable font covers searchable PDF text

and Korean comics could not export a searchable PDF at all, while Japanese and
Chinese could. P18's acceptance scope includes KO, so that was a functional gap.

The first version of this file skipped when no font covered Hangul, reasoning
that a machine without a Korean font cannot be blamed. Restoring the defect to
check - 2 passed, 2 skipped, nothing failed - showed why that was wrong. The
skip fired precisely because the defect was present, so the guard went quiet at
the exact moment it had something to say. A missing Korean font is either a
broken environment or a broken implementation, and both should be red.

So there is no skip any more. If this host cannot cover Hangul, the test fails
and says the font inventory needs looking at.
"""

from __future__ import annotations

import pytest

from infrastructure.export.qt_free import _embedded_font


def test_korean_text_embeds() -> None:
    """AC1: pure Korean must produce an embedded font, not a ValueError."""
    font = _embedded_font("안녕하세요")
    raw, glyphs, widths, bbox, ascent, descent, chars = font
    assert len(raw) > 10_000, "an embedded font that small is suspicious"
    assert len(chars) == len(dict.fromkeys("안녕하세요")), (
        "every distinct character must map to a glyph"
    )
    assert len(glyphs) == len(chars)
    assert all(width > 0 for width in widths), (
        "a zero width means the glyph was not really found: %r" % (widths,)
    )


def test_korean_and_japanese_together() -> None:
    """A page can carry both, and the kana are covered by the same font.

    malgun.ttf measured as ja+ko. A font covering only Hangul fails here.
    """
    chars = _embedded_font("안녕 こんにちは")[6]
    assert "안" in chars and "こ" in chars, (
        "expected one font to cover Korean and Japanese kana; got %r" % (chars,)
    )


def test_the_existing_languages_are_unchanged() -> None:
    """AC5: adding a candidate must not change which font wins for ja/zh/latin."""
    for text in ("こんにちは世界", "你好世界", "hello"):
        raw = _embedded_font(text)[0]
        # msyh.ttc is 19.5 MB, malgun.ttf is 13.5 MB. If the Korean candidate
        # started winning for CJK ideographs the size would drop, which would
        # mean the coverage check got weaker rather than the fonts got better.
        assert len(raw) > 15_000_000, (
            "%r changed font: embedded %d bytes" % (text, len(raw))
        )


def test_a_character_nobody_covers_still_fails_closed() -> None:
    """The guard must stay a guard.

    Without this, a change that returned the first available font
    unconditionally would pass every test above.
    """
    with pytest.raises(ValueError, match="no installed embeddable font"):
        _embedded_font("\U0010ffff")


def test_korean_does_not_fall_back_to_a_font_without_hangul() -> None:
    """Pins the actual defect: coverage must decide, not candidate order.

    msyh.ttc is listed first. If the predicate ever degraded to "does the font
    exist", Korean would silently embed msyh.ttc and produce a PDF whose text
    layer renders boxes - which is worse than raising, because it looks like it
    worked.
    """
    hangul_only = _embedded_font("안녕하세요")[0]
    cjk_routine = _embedded_font("你好世界")[0]
    assert hangul_only != cjk_routine, (
        "Korean and Chinese selected the same font; the coverage predicate is "
        "no longer deciding"
    )
