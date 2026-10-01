"""Production image import adapters (TASK-031)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.importing import (  # noqa: E402
    ManagedCopyStoreAdapter,
    QtImageDecoder,
)
from application.importing.images.ports import ImageDecodeError  # noqa: E402
from application.importing.images.service import ImportImagesUseCase  # noqa: E402

from helpers import InMemoryPageSink, make_png, make_source, make_thin_png  # noqa: E402


def test_qt_image_decoder_reports_dimensions_and_mime_type():
    decoded = QtImageDecoder().decode(make_png(11, 7))

    assert (decoded.width, decoded.height) == (11, 7)
    assert decoded.mime_type == "image/png"


def test_qt_image_decoder_rejects_invalid_bytes():
    with pytest.raises(ImageDecodeError):
        QtImageDecoder().decode(b"not-an-image")


def test_qt_image_decoder_uses_safe_mime_fallback(monkeypatch):
    from PySide6.QtGui import QImage

    class UnknownFormatReader:
        def __init__(self, device):
            del device

        @staticmethod
        def setAllocationLimit(megabytes):
            del megabytes

        def format(self):
            return b""

        def read(self):
            return QImage(2, 2, QImage.Format.Format_RGB32)

        def errorString(self):
            return ""

    monkeypatch.setattr("PySide6.QtGui.QImageReader", UnknownFormatReader)

    decoded = QtImageDecoder().decode(b"plugin-data")

    assert decoded.mime_type == "application/octet-stream"


# ----------------------------------------------------------------------
# M2-IMPORT-ALLOC-LIMIT: Qt's built-in 256 MiB decode allocation limit
# silently rejects webtoon long-strips in the product domain
# (TA3-B2 F2: K07 690x131289 = ~345.6 MiB decoded). The decoder must raise
# the cap to a documented bound and keep oversized payloads fail-closed.
# ----------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _restore_qt_allocation_limit():
    """The allocation limit is process-global; leave it as we found it."""
    from PySide6.QtGui import QImageReader

    before = QImageReader.allocationLimit()
    yield
    QImageReader.setAllocationLimit(before)


def test_qt_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap():
    from PySide6.QtGui import QImageReader

    # A 690x110000 RGBA page decodes to ~289.5 MiB: over Qt's built-in
    # default (256), far inside the product domain (K07 is ~345.6 MiB).
    # The file itself stays tiny via make_thin_png.
    data = make_thin_png(690, 110_000)
    assert len(data) < 1_000_000  # small on disk, huge decoded

    QImageReader.setAllocationLimit(256)  # Qt default: the unfixed behaviour
    decoded = QtImageDecoder().decode(data)

    assert (decoded.width, decoded.height) == (690, 110_000)
    assert decoded.mime_type == "image/png"


def test_qt_image_decoder_raises_allocation_limit_above_qt_default(monkeypatch):
    from PySide6.QtGui import QImageReader

    import infrastructure.importing as importing

    calls = []
    monkeypatch.setattr(
        QImageReader, "setAllocationLimit", lambda mb: calls.append(mb)
    )

    QtImageDecoder().decode(make_png())

    assert calls, "decoder must assert the allocation limit before decoding"
    limit = calls[-1]
    assert limit == importing._ALLOCATION_LIMIT_MIB
    assert limit > 256, "limit must exceed the Qt default that broke webtoons"
    assert limit > 0, "0 disables the check entirely (unbounded OOM risk)"


def test_qt_image_decoder_fail_closed_above_limit_with_reader_error_text():
    # Declared 8192x65536 RGBA decodes to exactly 2048 MiB: above the
    # decoder's own 2047 MiB bound, so the fix must NOT swallow it — typed
    # failure with the reader's own error text, never a process kill.
    # Qt checks the limit against the declared IHDR size *before*
    # allocating, so a single IDAT scanline exercises the real rejection
    # while the factory stays tiny (M2-IMPORT-ALLOC-LIMIT).
    data = make_thin_png(8192, 65536, rows=1)

    with pytest.raises(ImageDecodeError) as excinfo:
        QtImageDecoder().decode(data)

    detail = str(excinfo.value)
    assert detail.strip(), "per-file failure detail must not be an empty string (r1 R4)"
    assert len(detail) <= 400  # bounded for UI/log surfaces


def test_qt_image_decoder_truncates_very_long_reader_errors(monkeypatch):
    from PySide6.QtGui import QImage

    class LongErrorReader:
        def __init__(self, device):
            del device

        @staticmethod
        def setAllocationLimit(megabytes):
            del megabytes

        def format(self):
            return b"png"

        def read(self):
            return QImage()  # null image -> decode failure path

        def errorString(self):
            return "x" * 5000

    monkeypatch.setattr("PySide6.QtGui.QImageReader", LongErrorReader)

    with pytest.raises(ImageDecodeError) as excinfo:
        QtImageDecoder().decode(b"plugin-data")

    detail = str(excinfo.value)
    assert detail.startswith("x" * 100)  # carries the reader's own text
    assert len(detail) <= 400


def test_managed_copy_adapter_publishes_verbatim_d03_original(tmp_path):
    storage = ManagedFileStorage(tmp_path / "managed")
    adapter = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    data = make_png(5, 3)
    source_hash = hashlib.sha256(data).hexdigest()

    relative = adapter.store_original("chapter-7", "page 001.png", data, source_hash)

    assert relative.startswith("books/book-42/chapters/chapter-7/original/")
    assert relative.endswith(".png")
    assert (tmp_path / "managed" / Path(relative.replace("/", "\\"))).read_bytes() == data
    assert list((tmp_path / "managed" / "temp").iterdir()) == []


def test_production_adapters_drive_import_use_case(tmp_path):
    storage = ManagedFileStorage(tmp_path / "managed")
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    sink = InMemoryPageSink()
    use_case = ImportImagesUseCase(QtImageDecoder(), copy_store, sink)
    data = make_png(9, 6)

    report = use_case.import_files("chapter-7", [make_source("page.png", data)])

    assert len(report.imported) == 1
    page = report.imported[0].page
    assert (page.width, page.height) == (9, 6)
    assert Path(storage.absolute_path(page.managed_original_ref)).read_bytes() == data


def test_production_copy_failure_creates_no_page(tmp_path, monkeypatch):
    storage = ManagedFileStorage(tmp_path / "managed")

    def fail_publish(temp_handle, relative_path):
        del temp_handle, relative_path
        raise OSError("injected publish failure")

    monkeypatch.setattr(storage, "publish", fail_publish)
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    sink = InMemoryPageSink()
    use_case = ImportImagesUseCase(QtImageDecoder(), copy_store, sink)

    report = use_case.import_files(
        "chapter-7", [make_source("page.png", make_png(3, 2))]
    )

    assert report.failed[0].reason == "COPY_FAILED"
    assert sink.pages == []
    assert list((tmp_path / "managed" / "temp").iterdir()) == []


def test_managed_copy_adapter_cleans_temp_on_integrity_failure(tmp_path):
    storage = ManagedFileStorage(tmp_path / "managed")
    adapter = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")

    with pytest.raises(OSError, match="source hash"):
        adapter.store_original("chapter-7", "page.png", b"payload", "wrong")

    assert list((tmp_path / "managed" / "temp").iterdir()) == []
    assert not list((tmp_path / "managed" / "books").rglob("*"))


def test_managed_copy_adapter_rejects_path_like_source_names(tmp_path):
    storage = ManagedFileStorage(tmp_path / "managed")
    adapter = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    data = make_png()
    source_hash = hashlib.sha256(data).hexdigest()

    with pytest.raises(ValueError, match="source filename"):
        adapter.store_original("chapter-7", "..\\escape.png", data, source_hash)
