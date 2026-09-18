"""Diagnose the Format_ARGB32 / BGRA basis probe (TASK-043 AC ① note).

The first version of bgra_basis_probe.py read black for every case, which is
either a PySide6 buffer-lifetime artefact or a real byte-order mismatch. This
script separates the two by comparing bytes vs bytearray sources, stride
variants and both ``pixelColor`` and ``pixel`` readers.
"""

from __future__ import annotations

from PySide6.QtGui import QImage

# two pixels, BGRA bytes: red, blue
raw_bytes = bytes((0, 0, 255, 255, 255, 0, 0, 255))
raw_bytearray = bytearray(raw_bytes)

for label, buf in (("bytes", raw_bytes), ("bytearray", raw_bytearray)):
    # stride 8 (= 2 pixels * 4 bytes). The buggy first probe passed 4, which
    # makes QImage null (Format_Invalid) and silently reads black.
    image = QImage(buf, 2, 1, 8, QImage.Format.Format_ARGB32)
    print(
        f"[{label}] ARGB32 isNull={image.isNull()} format={image.format().name} "
        f"bytesPerLine={image.bytesPerLine()} sizeInBytes={image.sizeInBytes()}"
    )
    print(
        f"[{label}]   pixel(0,0)=0x{image.pixel(0, 0):08x} pixel(1,0)=0x{image.pixel(1, 0):08x}"
    )
    for x in (0, 1):
        colour = image.pixelColor(x, 0)
        print(
            f"[{label}]   pixelColor({x},0) RGBA "
            f"({colour.red()},{colour.green()},{colour.blue()},{colour.alpha()})"
        )

# control: the 3-channel formats from probe-prereq.txt, same two-pixel shape
ctrl = bytes((0, 0, 255, 0, 0, 255))
for name in ("Format_BGR888", "Format_RGB888"):
    image = QImage(ctrl, 2, 1, 6, getattr(QImage.Format, name))
    colour = image.pixelColor(0, 0)
    print(
        f"[control] {name} pixelColor(0,0) RGBA "
        f"({colour.red()},{colour.green()},{colour.blue()},{colour.alpha()})"
    )
