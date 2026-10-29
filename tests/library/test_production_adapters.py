"""Production image import adapters (TASK-031; CORE-SLIM-1: Pillow decoder)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.importing import (  # noqa: E402
    ManagedCopyStoreAdapter,
    PillowImageDecoder,
)
from application.importing.images.ports import ImageDecodeError  # noqa: E402
from application.importing.images.service import ImportImagesUseCase  # noqa: E402
from application.importing.images.sorting import sources_from_selection  # noqa: E402

from helpers import InMemoryPageSink, make_png, make_source, make_thin_png  # noqa: E402


def test_pillow_image_decoder_reports_dimensions_and_mime_type():
    decoded = PillowImageDecoder().decode(make_png(11, 7))

    assert (decoded.width, decoded.height) == (11, 7)
    assert decoded.mime_type == "image/png"


def test_pillow_image_decoder_rejects_invalid_bytes():
    with pytest.raises(ImageDecodeError):
        PillowImageDecoder().decode(b"not-an-image")


def test_pillow_image_decoder_uses_safe_mime_fallback(monkeypatch):
    # A format Pillow can decode but the product surface declares no MIME for
    # must fall back to application/octet-stream — the same safe default the
    # replaced Qt reader had when its plugin reported an empty format name.
    import infrastructure.importing as importing

    monkeypatch.setattr(importing, "_MIME_BY_IMAGE_FORMAT", {})

    decoded = PillowImageDecoder().decode(make_png(2, 2))

    assert decoded.mime_type == "application/octet-stream"


# ----------------------------------------------------------------------
# M2-IMPORT-ALLOC-LIMIT: the replaced Qt reader's built-in 256 MiB decode
# allocation limit silently rejected webtoon long-strips in the product
# domain (TA3-B2 F2: K07 690x131289 = ~345.6 MiB decoded). CORE-SLIM-1
# keeps the documented 2047 MiB ceiling, enforced against the DECLARED size
# before any pixel buffer is materialised, and keeps oversized payloads
# fail-closed.
# ----------------------------------------------------------------------


@pytest.mark.slow  # real 289.5 MiB decode (dsh r1 R9)
def test_pillow_image_decoder_imports_webtoon_long_strip_beyond_qt_default_cap():
    # A 690x110000 RGBA page decodes to ~289.5 MiB: over the old Qt default
    # (256), far inside the product domain (K07 is ~345.6 MiB). The file
    # itself stays tiny via make_thin_png.
    data = make_thin_png(690, 110_000)
    assert len(data) < 1_000_000  # small on disk, huge decoded

    decoded = PillowImageDecoder().decode(data)

    assert (decoded.width, decoded.height) == (690, 110_000)
    assert decoded.mime_type == "image/png"


def test_pillow_image_decoder_ceiling_is_checked_before_pixels_are_loaded(monkeypatch):
    # The ceiling must decide BEFORE the pixel buffer exists (the old Qt reader
    # checked the declared IHDR size the same way): with ``Image.load`` made
    # fatal, a declared-2048-MiB payload must still fail as a typed
    # ImageDecodeError raised by the ceiling, never by the loader.
    from PIL import Image

    import infrastructure.importing as importing

    def _explode(self):  # pragma: no cover - only reached on a regression
        raise AssertionError("pixel buffer was materialised above the ceiling")

    monkeypatch.setattr(Image.Image, "load", _explode)

    with pytest.raises(ImageDecodeError) as excinfo:
        PillowImageDecoder().decode(make_thin_png(8192, 65536, rows=1))

    assert "decode ceiling" in str(excinfo.value)
    assert importing._ALLOCATION_LIMIT_MIB > 256, (
        "ceiling must exceed the old Qt default that broke webtoons"
    )
    assert importing._ALLOCATION_LIMIT_MIB > 0, (
        "a zero ceiling would disable the bound entirely (unbounded OOM risk)"
    )


def test_pillow_image_decoder_allocation_limit_decides_accept_or_reject(monkeypatch):
    # Mechanism lock (dsh r1 R1): one complete, valid, small image. The very
    # same bytes must decode under the production limit and must be rejected
    # under a 1 MiB limit — the allocation limit itself (not payload
    # truncation or any other decode failure mode) is the deciding variable.
    import infrastructure.importing as importing

    data = make_thin_png(690, 4000)  # full payload: 690x4000 RGBA ~= 10.5 MiB

    decoded = PillowImageDecoder().decode(data)  # production limit: must pass
    assert (decoded.width, decoded.height) == (690, 4000)

    monkeypatch.setattr(importing, "_ALLOCATION_LIMIT_MIB", 1)
    with pytest.raises(ImageDecodeError):  # 1 MiB limit: same bytes, must fail
        PillowImageDecoder().decode(data)


def test_pillow_image_decoder_fail_closed_above_limit_with_reader_error_text():
    # Declared 8192x65536 RGBA decodes to exactly 2048 MiB: above the
    # decoder's own 2047 MiB bound, so the fix must NOT swallow it — typed
    # failure with the reader's own error text, never a process kill.
    # Qt checks the limit against the declared IHDR size *before*
    # allocating, so a single IDAT scanline exercises the real rejection
    # while the factory stays tiny (M2-IMPORT-ALLOC-LIMIT).
    data = make_thin_png(8192, 65536, rows=1)

    with pytest.raises(ImageDecodeError) as excinfo:
        PillowImageDecoder().decode(data)

    detail = str(excinfo.value)
    assert detail.strip(), "per-file failure detail must not be an empty string (r1 R4)"
    assert len(detail) <= 400  # bounded for UI/log surfaces


def test_pillow_image_decoder_truncates_very_long_reader_errors():
    import infrastructure.importing as importing

    # r1 R8: one pathological decoder message may be 5000 chars long; the
    # surfaced detail must be bounded and carry the truncation marker.
    truncated = importing._bounded_detail("x" * 5000)
    assert truncated.startswith("x" * 100)  # carries the decoder's own text
    assert truncated.endswith("...")  # truncation marker
    assert len(truncated) == importing._ERROR_DETAIL_MAX_CHARS + 3  # 300 + "..."

    # ...while garbage bytes still fail closed with a non-empty bounded detail
    # (r1 R4): never an empty string on UI/log surfaces.
    with pytest.raises(ImageDecodeError) as excinfo:
        PillowImageDecoder().decode(b"plugin-data")

    detail = str(excinfo.value)
    assert detail.strip()
    assert len(detail) <= importing._ERROR_DETAIL_MAX_CHARS + 3


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
    use_case = ImportImagesUseCase(PillowImageDecoder(), copy_store, sink)
    data = make_png(9, 6)

    report = use_case.import_files("chapter-7", [make_source("page.png", data)])

    assert len(report.imported) == 1
    page = report.imported[0].page
    assert (page.width, page.height) == (9, 6)
    assert Path(storage.absolute_path(page.managed_original_ref)).read_bytes() == data


def test_production_core_assembly_imports_real_dimensions_and_keeps_source(tmp_path):
    from bootstrap.core_service import assemble_production_core

    data_root = tmp_path / "core"
    source_root = tmp_path / "选定 📚 (原图)"
    source_root.mkdir()
    source = source_root / "漫画 １.png"
    data = make_png(17, 23)
    source.write_bytes(data)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    core = assemble_production_core(data_root)
    try:
        book = core.library.create_book("P09 production image")
        chapter = core.library.create_chapter(book.book_id, "第 1 話")
        report = core.importer.import_files(
            chapter.chapter_id,
            sources_from_selection(source_root, [source]),
        )

        assert report.failed == () and len(report.imported) == 1
        page = report.imported[0].page
        assert page.source_filename == source.name
        assert (page.source_order, page.sort_order) == (1, 1)
        assert page.source_hash == source_hash
        assert (page.width, page.height) == (17, 23)
        assert Path(core.storage.absolute_path(page.managed_original_ref)).read_bytes() == data
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    finally:
        core.conn.close()


def test_production_copy_failure_creates_no_page(tmp_path, monkeypatch):
    storage = ManagedFileStorage(tmp_path / "managed")

    def fail_publish(temp_handle, relative_path):
        del temp_handle, relative_path
        raise OSError("injected publish failure")

    monkeypatch.setattr(storage, "publish", fail_publish)
    copy_store = ManagedCopyStoreAdapter(storage, lambda chapter_id: "book-42")
    sink = InMemoryPageSink()
    use_case = ImportImagesUseCase(PillowImageDecoder(), copy_store, sink)

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
