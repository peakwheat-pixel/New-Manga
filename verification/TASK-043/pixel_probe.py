"""TASK-043 / F-1 pixel probe — run against ONE src tree at a time.

The script deliberately does **not** touch ``sys.path`` (a per-tree
``PYTHONPATH`` is the only thing that selects the tree; this is the isolation
lesson from TASK-042) and prints the resolved ``infrastructure.importing``
file first, so an "after" run can never silently reuse the "before" tree.

It renders a known solid-colour PDF through the *production*
``PdfiumDocumentRaster`` and decodes the resulting PNG, reporting the centre
pixel. Pre-fix: red -> blue. Post-fix: red -> red.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtGui import QImage

import infrastructure.importing as importing_module
from infrastructure.importing import PdfiumDocumentRaster

print("python     :", sys.executable)
print("PYTHONPATH :", os.environ.get("PYTHONPATH", ""))
print("using tree :", Path(importing_module.__file__).resolve())
print("adapter    :", PdfiumDocumentRaster.__module__)


def solid_pdf(red: int, green: int, blue: int, size: int = 100) -> bytes:
    stream = f"{red} {green} {blue} rg 0 0 {size} {size} re f".encode()
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {size} {size}] "
            f"/Contents 4 0 R >>"
        ).encode(),
        4: b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"\nendstream",
    }
    out = bytearray(b"%PDF-1.4\n")
    offsets: dict[int, int] = {}
    for obj_id in sorted(objects):
        offsets[obj_id] = len(out)
        out += f"{obj_id} 0 obj\n".encode() + objects[obj_id] + b"\nendobj\n"
    xref_pos = len(out)
    count = max(objects) + 1
    out += f"xref\n0 {count}\n".encode()
    out += b"0000000000 65535 f \n"
    for obj_id in range(1, count):
        out += f"{offsets[obj_id]:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {count} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n"
    ).encode()
    return bytes(out)


raster = PdfiumDocumentRaster()
for fill in ((255, 0, 0), (0, 255, 0), (0, 0, 255)):
    handle = raster.open(solid_pdf(*fill))
    rendered = handle.render_page(0)
    handle.close()
    image = QImage.fromData(rendered.png, "PNG")
    colour = image.pixelColor(image.width() // 2, image.height() // 2)
    verdict = "OK" if (colour.red(), colour.green(), colour.blue()) == fill else "SWAPPED"
    print(
        f"PDF fill {fill} -> PNG {rendered.width}x{rendered.height} centre pixel "
        f"RGBA ({colour.red()},{colour.green()},{colour.blue()},{colour.alpha()})  "
        f"[{verdict}]"
    )
