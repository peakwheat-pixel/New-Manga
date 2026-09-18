"""TASK-043 prerequisite probes (no product code touched).

P1: does this PySide6 expose QImage.Format_BGR888 / Format_BGR888 semantics?
P2: is a 0-page PDF reachable through the production PDFium binding
    (i.e. can the F-3 empty-document branch be exercised end-to-end)?
P3: what byte order does pdfium hand back for a known solid-colour page,
    and what does the *pre-fix* mapping produce?
"""

from __future__ import annotations

import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "src"))

from PySide6.QtGui import QImage  # noqa: E402

print("PySide6 QImage.Format_BGR888 present:", hasattr(QImage.Format, "Format_BGR888"))
print("PySide6 QImage.Format_RGB888  present:", hasattr(QImage.Format, "Format_RGB888"))
print("Format_BGR888 value:", QImage.Format.Format_BGR888.value)
print("Format_RGB888  value:", QImage.Format.Format_RGB888.value)

# ---- P1b: semantics of the two enum members on the same raw buffer ----------
# A 2x1 buffer whose bytes are B,G,R = (0, 0, 255) must read back as RED when
# interpreted as BGR888 and as BLUE when (mis)interpreted as RGB888.
raw = bytes((0, 0, 255, 0, 0, 255))
for name in ("Format_BGR888", "Format_RGB888"):
    fmt = getattr(QImage.Format, name)
    img = QImage(raw, 2, 1, 6, fmt)
    px = img.pixelColor(0, 0)
    print(
        f"{name}: raw bytes (0,0,255) -> pixelColor RGBA "
        f"({px.red()},{px.green()},{px.blue()},{px.alpha()})"
    )

# ---- P2: 0-page PDF through pypdfium2 --------------------------------------


def empty_pdf() -> bytes:
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [] /Count 0 >>",
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


import pypdfium2 as pdfium  # noqa: E402

print(
    "pypdfium2 version:",
    getattr(pdfium, "V_PYPDFIUM2", None) or getattr(pdfium, "__version__", "unknown"),
)

data = empty_pdf()
try:
    doc = pdfium.PdfDocument(data)
    print("0-page PDF opened, page_count =", len(doc))
    doc.close()
except Exception as error:  # noqa: BLE001 - probe
    print(f"0-page PDF refused by pdfium: {type(error).__name__}: {error}")

# ---- P3: solid-colour page raw bytes + pre-fix mapping ---------------------


def solid_pdf(r: int, g: int, b: int, size: int = 100) -> bytes:
    stream = f"{r} {g} {b} rg 0 0 {size} {size} re f".encode()
    objects = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
        2: b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        3: (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {size} {size}] "
            f"/Contents 4 0 R >>"
        ).encode(),
        4: b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n"
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


from infrastructure.importing import PdfiumDocumentRaster  # noqa: E402

raster = PdfiumDocumentRaster()
for (r, g, b) in ((255, 0, 0), (0, 255, 0), (0, 0, 255)):
    handle = raster.open(solid_pdf(r, g, b))
    rendered = handle.render_page(0)
    handle.close()
    img = QImage.fromData(rendered.png, "PNG")
    px = img.pixelColor(img.width() // 2, img.height() // 2)
    print(
        f"PDF fill ({r},{g},{b}) size={rendered.width}x{rendered.height} "
        f"-> production PNG centre pixel RGBA "
        f"({px.red()},{px.green()},{px.blue()},{px.alpha()})"
    )
