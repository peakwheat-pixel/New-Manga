"""Qt image compositor: page render + single-region composition (§8.2).

Assertions are pixel-level against decoded PNGs — no visual judgement
is fabricated: ink must appear inside the target box and untouched
pixels must compare equal to the base outside it.
"""

from __future__ import annotations

import helpers  # noqa: F401  (sys.path injection)

import pytest

from application.rendering.style import TextDirection
from ports.rendering.ports import DrawItem, RenderOp


def decode(png: bytes):
    from PySide6.QtGui import QImage

    image = QImage.fromData(png)
    assert not image.isNull()
    return image


def solid_png(width: int, height: int, color: str) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(color)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def ink_pixels(image, box: tuple[int, int, int, int]) -> int:
    x, y, w, h = box
    count = 0
    for row in range(y, min(y + h, image.height())):
        for col in range(x, min(x + w, image.width())):
            color = image.pixelColor(col, row)
            if (color.red(), color.green(), color.blue()) != (255, 255, 255):
                count += 1
    return count


def boxes_equal(a, b, box: tuple[int, int, int, int]) -> bool:
    x, y, w, h = box
    for row in range(y, min(y + h, a.height())):
        for col in range(x, min(x + w, a.width())):
            if a.pixel(col, row) != b.pixel(col, row):
                return False
    return True


def op(**overrides) -> RenderOp:
    defaults = dict(
        items=(DrawItem("译文", 0.0, 20.0, per_char=False),),
        region_x=40,
        region_y=30,
        region_width=120,
        region_height=80,
        font_family="Microsoft YaHei",
        font_size=24.0,
        text_color="#000000",
        stroke_enabled=True,
        stroke_color="#FFFFFF",
        stroke_width=3.0,
        direction=TextDirection.HORIZONTAL,
    )
    defaults.update(overrides)
    return RenderOp(**defaults)


@pytest.fixture()
def compositor(qapp):
    from infrastructure.rendering.qt_compositor import QtImageCompositor

    return QtImageCompositor()


REGION = (40, 30, 120, 80)


class TestComposePage:
    def test_text_drawn_inside_region(self, compositor) -> None:
        base = solid_png(320, 200, "#FFFFFF")
        result = compositor.compose_page(base, [op()])
        image = decode(result)
        assert ink_pixels(image, REGION) > 50

    def test_outside_region_unchanged(self, compositor) -> None:
        base = solid_png(320, 200, "#FFFFFF")
        # mark a sentinel pixel far away from the region
        result = compositor.compose_page(base, [op()])
        image = decode(result)
        assert boxes_equal(image, decode(base), (0, 0, 320, 25))
        assert boxes_equal(image, decode(base), (0, 130, 320, 70))

    def test_stroke_color_visible_around_glyphs(self, compositor) -> None:
        # black text, thick yellow stroke on a mid-gray base so both colors
        # are distinguishable from the background
        from PySide6.QtGui import QImage

        base_image = QImage(320, 200, QImage.Format_ARGB32)
        base_image.fill("#808080")
        from PySide6.QtCore import QBuffer, QIODevice

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        base_image.save(buffer, "PNG")
        base = bytes(buffer.data())

        result = compositor.compose_page(
            base,
            [op(stroke_color="#FFFF00", text_color="#000000", stroke_width=4.0)],
        )
        image = decode(result)
        colors = set()
        x, y, w, h = REGION
        for row in range(y, y + h):
            for col in range(x, x + w):
                color = image.pixelColor(col, row)
                colors.add((color.red(), color.green(), color.blue()))
        assert (0, 0, 0) in colors  # fill
        assert (255, 255, 0) in colors  # stroke

    def test_vertical_op_draws_upright_chars(self, compositor) -> None:
        base = solid_png(320, 200, "#FFFFFF")
        items = tuple(
            DrawItem(ch, 30.0, 20.0 + index * 26.0, per_char=True)
            for index, ch in enumerate("纵排")
        )
        result = compositor.compose_page(base, [op(items=items, direction=TextDirection.VERTICAL)])
        assert ink_pixels(decode(result), REGION) > 30


class TestComposeRegion:
    def test_region_restored_from_clean_then_redrawn(self, compositor) -> None:
        # base carries an old translation (red) inside and outside the box
        base_image = decode(solid_png(320, 200, "#FF0000"))
        clean = solid_png(320, 200, "#FFFFFF")
        from PySide6.QtCore import QBuffer, QIODevice

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        base_image.save(buffer, "PNG")
        base = bytes(buffer.data())

        result = compositor.compose_region(base, clean, REGION, op())
        image = decode(result)
        # inside the box: clean background restored + new dark text ink
        assert ink_pixels(image, REGION) > 50
        # outside the box: the base's red pixels survive untouched
        assert image.pixel(10, 10) == decode(base).pixel(10, 10)
        assert boxes_equal(image, decode(base), (0, 130, 320, 70))

    def test_compose_region_keeps_neighbour_regions(self, compositor) -> None:
        base = decode(solid_png(320, 200, "#FFFFFF"))
        from PySide6.QtCore import QBuffer, QIODevice
        from PySide6.QtGui import QPainter

        painter = QPainter(base)
        painter.setPen("#0000FF")
        painter.drawRect(180, 30, 40, 40)  # a neighbouring region's content
        painter.end()
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        base.save(buffer, "PNG")
        base_png = bytes(buffer.data())

        clean = solid_png(320, 200, "#FFFFFF")
        result = compositor.compose_region(base_png, clean, REGION, op())
        image = decode(result)
        # neighbour content identical after the region composition
        assert boxes_equal(image, decode(base_png), (180, 30, 40, 40))
