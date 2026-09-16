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

from helpers import InMemoryPageSink, make_png, make_source  # noqa: E402


def test_qt_image_decoder_reports_dimensions_and_mime_type():
    decoded = QtImageDecoder().decode(make_png(11, 7))

    assert (decoded.width, decoded.height) == (11, 7)
    assert decoded.mime_type == "image/png"


def test_qt_image_decoder_rejects_invalid_bytes():
    with pytest.raises(ImageDecodeError):
        QtImageDecoder().decode(b"not-an-image")


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
