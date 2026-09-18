"""Does the PDF import path swap red and blue? (DSH external review; bug-lens ISSUE 2)"""
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
sys.path.insert(0, str(REPO / "src"))

def red_pdf() -> bytes:
    content = b"1 0 0 rg 0 0 100 100 re f\n"
    objs = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 100 100]/Contents 4 0 R>>",
        b"<</Length " + str(len(content)).encode() + b">>\nstream\n" + content + b"endstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objs, start=1):
        offsets.append(len(out))
        out += str(i).encode() + b" 0 obj\n" + body + b"\nendobj\n"
    xref_at = len(out)
    out += b"xref\n0 " + str(len(objs) + 1).encode() + b"\n0000000000 65535 f \n"
    for off in offsets:
        out += ("%010d 00000 n \n" % off).encode()
    out += (b"trailer\n<</Size " + str(len(objs) + 1).encode() + b"/Root 1 0 R>>\nstartxref\n"
            + str(xref_at).encode() + b"\n%%EOF\n")
    return bytes(out)

data = red_pdf()
from PySide6.QtGui import QGuiApplication, QImage
app = QGuiApplication.instance() or QGuiApplication([])
from infrastructure.importing import PdfiumDocumentRaster

handle = PdfiumDocumentRaster(scale=2.0).open(data)
page = handle.render_page(0)
png = QImage.fromData(page.png)
center = png.pixelColor(png.width() // 2, png.height() // 2)
print(f"rendered {page.width}x{page.height} png={png.width()}x{png.height()} format={png.format()}")
print(f"centre pixel RGBA = ({center.red()}, {center.green()}, {center.blue()}, {center.alpha()})")
print("source PDF paints pure RED (1 0 0 rg)")
print("VERDICT:", "RED preserved" if center.red() > 200 and center.blue() < 60
      else ("RED->BLUE SWAP (RGB888 used for a BGR buffer)" if center.blue() > 200 and center.red() < 60
            else "unexpected"))

# control: raw pdfium buffer mode + what BGR888 would give
from pypdfium2 import PdfDocument
bmp = PdfDocument(data)[0].render(scale=2.0)
print("pdfium mode:", bmp.mode, "stride:", bmp.stride, "w*3:", bmp.width * 3)
raw = bytes(bmp.buffer)
px = raw[(bmp.height // 2) * bmp.stride + (bmp.width // 2) * 3:][:3]
print("raw centre bytes:", tuple(px), "(B,G,R order if pdfium native)")
