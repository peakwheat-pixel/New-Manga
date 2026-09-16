"""Qt-backed PDF composer for image exports (TASK-015, D06 §96).

The only module in the export slice that touches PySide6, and it does so
lazily inside ``compose`` so the rest of the application (and every
non-GUI test run) never needs the toolkit installed. Pages are decoded
from image bytes with ``QImage`` and painted onto a ``QPdfWriter`` page
sized to the image, preserving each page's pixel dimensions.
"""

from __future__ import annotations

from collections.abc import Sequence


class QtImagePdfComposer:
    """PdfComposer binding that renders pages through Qt."""

    def compose(self, images: Sequence[bytes]) -> bytes:
        from PySide6.QtCore import QBuffer, QIODevice, QSizeF
        from PySide6.QtGui import QImage, QPainter, QPageSize, QPdfWriter

        decoded: list[QImage] = []
        for index, payload in enumerate(images, start=1):
            image = QImage.fromData(payload)
            if image.isNull():
                raise ValueError(f"page {index}: undecodable image data")
            decoded.append(image)

        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.ReadWrite)
        writer = QPdfWriter(buffer)
        writer.setResolution(72)
        painter = QPainter(writer)
        try:
            for index, image in enumerate(decoded):
                # 1 px = 1 pt at 72 dpi: the page exactly fits the image.
                writer.setPageSize(
                    QPageSize(QSizeF(image.width(), image.height()), QPageSize.Unit.Point)
                )
                painter.drawImage(0, 0, image)
                if index < len(decoded) - 1:
                    writer.newPage()
        finally:
            painter.end()
        return bytes(buffer.data())
