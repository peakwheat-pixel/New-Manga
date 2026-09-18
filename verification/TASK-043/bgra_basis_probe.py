"""TASK-043 AC ① supporting evidence: why ``Format_ARGB32`` is the right
mapping for pdfium's ``BGRA`` bitmaps.

The ``BGRA`` branch is not reachable through the production binding on this
machine (pdfium renders with ``mode == "BGR"``; see probe-prereq.txt), so its
correctness cannot be shown end-to-end here. It can still be pinned directly:
a buffer whose bytes are B,G,R,A must decode to the *same* colour when read as
``Format_ARGB32`` — that is the little-endian layout ``0xAARRGGBB``, which is
exactly what Qt documents for that format, and Windows x86-64 is little-endian.
"""

from __future__ import annotations

from PySide6.QtGui import QImage

# (B, G, R, A) in memory, as pdfium's "BGRA" guarantees.
cases = {
    "red   (B=0,G=0,R=255)": (0, 0, 255, 255),
    "green (B=0,G=255,R=0)": (0, 255, 0, 255),
    "blue  (B=255,G=0,R=0)": (255, 0, 0, 255),
}
expected = {
    "red   (B=0,G=0,R=255)": (255, 0, 0, 255),
    "green (B=0,G=255,R=0)": (0, 255, 0, 255),
    "blue  (B=255,G=0,R=0)": (0, 0, 255, 255),
}

for label, (b, g, r, a) in cases.items():
    # two 32-bit pixels: bytesPerLine must be 2 * 4, not 4 (a too-small
    # stride makes QImage null and every read black — the first version of
    # this probe had exactly that bug, see bgra-basis-diag.txt).
    raw = bytes((b, g, r, a, b, g, r, a))
    image = QImage(raw, 2, 1, 8, QImage.Format.Format_ARGB32)
    assert not image.isNull(), "probe built a null QImage (bad stride/format)"
    colour = image.pixelColor(0, 0)
    got = (colour.red(), colour.green(), colour.blue(), colour.alpha())
    verdict = "OK" if got == expected[label] else "MISMATCH"
    print(
        f"BGRA bytes (B={b},G={g},R={r},A={a}) -> Format_ARGB32 pixelColor "
        f"RGBA {got}  [{verdict}]"
    )
