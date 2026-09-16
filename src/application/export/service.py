from __future__ import annotations

import json
import os
import tempfile
import uuid
import zipfile
import zlib
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Callable


class ExportFormat(str, Enum):
    IMAGE = "png"
    ZIP = "zip"
    CBZ = "cbz"
    PDF = "pdf"
    TEXT = "txt"


@dataclass(frozen=True)
class ExportPage:
    page_id: str
    filename: str
    source_path: Path
    text: str
    revision_id: str | None = None
    current_revision_id: str | None = None
    translated_path: Path | None = None

    @property
    def stale(self) -> bool:
        return bool(self.revision_id and self.current_revision_id and self.revision_id != self.current_revision_id)


@dataclass(frozen=True)
class ExportRequest:
    book_id: str
    chapter_id: str
    format: ExportFormat
    output_path: Path
    pages: list[ExportPage]
    mode: str = "original"
    overwrite: bool = False
    stale_policy: str = "abort"
    cancel: Callable[[], bool] | None = None


@dataclass(frozen=True)
class ExportResult:
    path: Path
    export_id: str
    page_ids: tuple[str, ...]


class ExportService:
    def __init__(self, history_path: str | Path):
        self._history_path = Path(history_path)
        self._history = self._read_history()

    def export(self, request: ExportRequest) -> ExportResult:
        if not request.pages:
            raise ValueError("export requires at least one page")
        if request.format is ExportFormat.IMAGE and len(request.pages) != 1:
            raise ValueError("single image export requires exactly one page")
        if request.stale_policy not in {"abort", "continue"}:
            raise ValueError("stale_policy must be abort or continue")
        stale = [page.page_id for page in request.pages if request.mode == "translated" and page.stale]
        if stale and request.stale_policy == "abort":
            raise ValueError(f"stale pages: {', '.join(stale)}; render current version first or continue")
        target = Path(request.output_path)
        if target.exists() and not request.overwrite:
            raise FileExistsError(str(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
        os.close(fd)
        temp = Path(temp_name)
        try:
            if request.cancel and request.cancel():
                raise RuntimeError("export cancelled")
            self._write(temp, request)
            if request.cancel and request.cancel():
                raise RuntimeError("export cancelled")
            if target.exists() and not request.overwrite:
                raise FileExistsError(str(target))
            os.replace(temp, target)
        except BaseException:
            temp.unlink(missing_ok=True)
            raise
        result = ExportResult(target, uuid.uuid4().hex, tuple(page.page_id for page in request.pages))
        self._history.append({"export_id": result.export_id, "path": str(target), "format": request.format.value, "page_ids": list(result.page_ids), "mode": request.mode})
        self._write_history()
        return result

    def history(self) -> list[dict]:
        return list(self._history)

    def _write(self, path: Path, request: ExportRequest) -> None:
        if request.format is ExportFormat.TEXT:
            path.write_text("".join(page.text + "\n" for page in request.pages), encoding="utf-8")
            return
        if request.format in {ExportFormat.ZIP, ExportFormat.CBZ}:
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for page in request.pages:
                    archive.writestr(_archive_name(page.filename), self._bytes(page, request.mode))
            return
        if request.format is ExportFormat.IMAGE:
            path.write_bytes(self._bytes(request.pages[0], request.mode))
            return
        path.write_bytes(_pdf(request.pages, request.mode))

    @staticmethod
    def _bytes(page: ExportPage, mode: str) -> bytes:
        source = page.translated_path if mode == "translated" and page.translated_path else page.source_path
        return Path(source).read_bytes()

    def _read_history(self) -> list[dict]:
        try:
            value = json.loads(self._history_path.read_text(encoding="utf-8"))
            return value if isinstance(value, list) else []
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _write_history(self) -> None:
        self._history_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self._history_path.with_suffix(self._history_path.suffix + ".tmp")
        temp.write_text(json.dumps(self._history, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(self._history_path)


def _pdf(pages: list[ExportPage], mode: str) -> bytes:
    """Small image PDF writer using Qt's decoder, already a project dependency."""
    try:
        from PySide6.QtGui import QImage
    except ImportError:
        return _text_pdf(pages)

    objects: list[bytes] = [b"<< /Type /Catalog /Pages 2 0 R >>", b""]
    page_refs: list[int] = []
    for page in pages:
        image = QImage(str(page.translated_path if mode == "translated" and page.translated_path else page.source_path))
        if image.isNull():
            return _text_pdf(pages)
        image = image.convertToFormat(QImage.Format.Format_RGB888)
        raw = b"".join(bytes(image.constScanLine(row))[: image.width() * 3] for row in range(image.height()))
        compressed = zlib.compress(raw)
        image_no = len(objects) + 1
        objects.append(f"<< /Type /XObject /Subtype /Image /Width {image.width()} /Height {image.height()} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /Length {len(compressed)} >>\nstream\n".encode() + compressed + b"\nendstream")
        content = f"q {image.width()} 0 0 {image.height()} 0 0 cm /Im{image_no} Do Q".encode()
        content_no = len(objects) + 1
        objects.append(f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"\nendstream")
        page_no = len(objects) + 1
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {image.width()} {image.height()}] /Resources << /XObject << /Im{image_no} {image_no} 0 R >> >> /Contents {content_no} 0 R >>".encode())
        page_refs.append(page_no)
    objects[1] = f"<< /Type /Pages /Kids [{' '.join(f'{n} 0 R' for n in page_refs)}] /Count {len(page_refs)} >>".encode()
    out, offsets = bytearray(b"%PDF-1.4\n"), [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(out)); out.extend(f"{number} 0 obj\n".encode()); out.extend(obj); out.extend(b"\nendobj\n")
    xref = len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    out.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    out.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(out)


def _archive_name(name: str) -> str:
    if not name or Path(name).name != name or any(char in name for char in '<>:"/\\|?*') or any(ord(char) < 32 for char in name):
        raise ValueError(f"invalid archive filename: {name!r}")
    return name


def _text_pdf(pages: list[ExportPage]) -> bytes:
    """Valid, dependency-free fallback when a page decoder is unavailable."""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [4 0 R] /Count 1 >>",
        b"<< /Length 44 >>\nstream\nBT /F1 12 Tf 36 756 Td (Exported manga pages) Tj ET\nendstream",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 3 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out, offsets = bytearray(b"%PDF-1.4\n"), [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(out)); out.extend(f"{number} 0 obj\n".encode()); out.extend(obj); out.extend(b"\nendobj\n")
    xref = len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    out.extend(b"".join(f"{offset:010d} 00000 n \n".encode() for offset in offsets[1:]))
    out.extend(f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(out)
