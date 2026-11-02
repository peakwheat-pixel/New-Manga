"""Qt image compositor (D06 §23, TASK-002 §8.2).

Page render draws every resolved RenderOp onto the base (Clean) image.
Single-region composition first restores the target box from the Clean
image — erasing that region's previous translation without touching
anything else on the page — then draws the new op.

Text is rendered through a QPainterPath so the stroke (D03 §11.5 描边)
wraps the glyph outline: stroked first with the stroke color, then
filled with the text color.
"""

from __future__ import annotations

from typing import Sequence

from PySide6.QtCore import QBuffer, QIODevice, QRect, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
)

from ports.rendering.ports import ImageCompositor, RenderOp
from ports.rendering.direction import TextDirection


def _to_png(image: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


class QtImageCompositor(ImageCompositor):
    def compose_page(self, base_png: bytes, ops: Sequence[RenderOp]) -> bytes:
        image = QImage.fromData(base_png)
        if image.isNull():
            raise ValueError("base image could not be decoded")
        image = image.convertToFormat(QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        try:
            for render_op in ops:
                self._draw_op(painter, render_op)
        finally:
            painter.end()
        return _to_png(image)

    def compose_region(
        self,
        base_png: bytes,
        clean_png: bytes,
        box: tuple[int, int, int, int],
        op: RenderOp,
    ) -> bytes:
        base = QImage.fromData(base_png)
        clean = QImage.fromData(clean_png)
        if base.isNull() or clean.isNull():
            raise ValueError("base/clean image could not be decoded")
        base = base.convertToFormat(QImage.Format.Format_ARGB32)
        clean = clean.convertToFormat(QImage.Format.Format_ARGB32)

        x, y, w, h = box
        target = QRect(x, y, w, h) & base.rect()
        if target.isEmpty():
            raise ValueError(f"composition box {box} outside the page image")
        painter = QPainter(base)
        painter.drawImage(target, clean, target)  # §8.2: restore from Clean
        painter.end()
        return self.compose_page(_to_png(base), (op,))

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _draw_op(self, painter: QPainter, render_op: RenderOp) -> None:
        font = QFont(render_op.font_family)
        font.setPixelSize(max(1, round(render_op.font_size)))
        metrics = QFontMetrics(font)

        extents_w, extents_h = self._extents(render_op, metrics)
        origin_x, origin_y = self._origin(render_op, extents_w, extents_h)

        path = QPainterPath()
        for item in render_op.items:
            draw_x = origin_x + item.x
            draw_y = origin_y + item.y
            path.addText(draw_x, draw_y, font, item.text)

        if render_op.stroke_enabled and render_op.stroke_width > 0:
            pen = QPen(QColor(render_op.stroke_color))
            pen.setWidthF(render_op.stroke_width)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(render_op.text_color))
        painter.drawPath(path)

    def _extents(
        self, render_op: RenderOp, metrics: QFontMetrics
    ) -> tuple[float, float]:
        if render_op.direction is TextDirection.VERTICAL:
            right = max((item.x for item in render_op.items), default=0.0)
            column_width = max(
                (metrics.horizontalAdvance(item.text) for item in render_op.items),
                default=0.0,
            )
            bottom = max(
                (item.y for item in render_op.items),
                default=0.0,
            )
            return right + column_width, bottom
        right = max(
            (
                item.x + metrics.horizontalAdvance(item.text)
                for item in render_op.items
            ),
            default=0.0,
        )
        bottom = max((item.y for item in render_op.items), default=0.0)
        descent = metrics.descent()
        return right, bottom + descent

    def _origin(
        self, render_op: RenderOp, extents_w: float, extents_h: float
    ) -> tuple[float, float]:
        free_w = render_op.region_width - extents_w
        free_h = render_op.region_height - extents_h
        if render_op.text_align == "center":
            offset_x = max(0.0, free_w / 2)
        else:  # D03 §11.6 default align: start
            offset_x = 0.0
        offset_y = max(0.0, free_h / 2)  # vertically center inside the region
        return (
            render_op.region_x + offset_x,
            render_op.region_y + offset_y,
        )
