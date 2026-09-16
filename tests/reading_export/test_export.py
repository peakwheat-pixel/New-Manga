"""ExportService tests (TASK-015).

Covers AC-EXPORT-001 (five formats), AC-EXPORT-002 (history fields),
AC-EXPORT-003 (stale prompt semantics), scope/order, Unicode and hostile
filenames, the three overwrite policies, cancellation/failure protection
(既有目标文件与源文件不动), and 使用相同设置再次导出. PDF runs on a
deterministic stub composer; the real Qt composer has its own test.
"""

from __future__ import annotations

import json
import re
import zipfile

import pytest
from reading_export_helpers import to_export_pages, make_pages, make_service

from application.export import (
    ExportCancelledError,
    ExportError,
    ExportFormat,
    ExportPage,
    ExportRequest,
    ExportValidationError,
    OverwritePolicy,
    PdfUnavailableError,
    StaleExportError,
    StalePolicy,
    file_bytes_provider,
)


class StubPdfComposer:
    """Deterministic composer: magic + per-page length headers."""

    def compose(self, images):
        import hashlib

        payload = b"%PDF-STUB" + b"".join(
            hashlib.sha256(image).digest() for image in images
        )
        return payload + b"\n%%EOF"


@pytest.fixture()
def service(tmp_path):
    return make_service(tmp_path)


@pytest.fixture()
def pages(tmp_path):
    return to_export_pages(make_pages(tmp_path / "src", count=3, translated=True))


def _request(tmp_path, pages, fmt=ExportFormat.ZIP, **kwargs):
    defaults = dict(
        book_id="b",
        chapter_id="c",
        format=fmt,
        output_path=tmp_path / f"out.{fmt.value}",
        pages=tuple(pages),
        mode="original",
    )
    defaults.update(kwargs)
    return ExportRequest(**defaults)


# ----------------------------------------------------------------------
# AC-EXPORT-001: five formats, content, order, re-readability (产物重读)
# ----------------------------------------------------------------------


def test_zip_keeps_scope_order_and_unicode_names(tmp_path, service, pages):
    result = service.export(_request(tmp_path, pages))
    assert result.status.value == "completed"
    with zipfile.ZipFile(result.output_path) as archive:
        names = archive.namelist()
        assert names == ["0001_page_00_第0页.png", "0002_page_01_第1页.png", "0003_page_02_第2页.png"]
        assert archive.read(names[0]) == b"PNG-orig-0"
        assert archive.testzip() is None  # artifact re-reads cleanly


def test_zip_translated_mode_uses_translated_bytes(tmp_path, service, pages):
    result = service.export(_request(tmp_path, pages, mode="translated"))
    with zipfile.ZipFile(result.output_path) as archive:
        assert archive.read("0001_page_00_第0页.png") == b"PNG-trans-0"


def test_cbz_stores_pages_in_order(tmp_path, service, pages):
    result = service.export(_request(tmp_path, pages, fmt=ExportFormat.CBZ))
    with zipfile.ZipFile(result.output_path) as archive:
        assert archive.namelist()[0] == "0001_page_00_第0页.png"


def test_single_image_requires_exactly_one_page(tmp_path, service, pages):
    result = service.export(_request(tmp_path, pages[:1], fmt=ExportFormat.SINGLE_IMAGE))
    assert result.output_path.read_bytes() == b"PNG-orig-0"
    with pytest.raises(ExportValidationError):
        service.export(_request(tmp_path, pages, fmt=ExportFormat.SINGLE_IMAGE))


def test_single_image_translated_without_render_is_refused(tmp_path, service):
    plain = to_export_pages(make_pages(tmp_path / "plain", count=1))
    with pytest.raises(StaleExportError):
        service.export(_request(tmp_path, plain, fmt=ExportFormat.SINGLE_IMAGE, mode="translated"))


def test_text_export_carries_page_texts_in_order(tmp_path, service, pages):
    result = service.export(_request(tmp_path, pages, fmt=ExportFormat.TEXT))
    body = result.output_path.read_text(encoding="utf-8")
    assert "【page_00_第0页.png】" in body
    assert "第 0 页译文" in body
    assert "第 2 页译文" in body
    assert body.index("第 0 页译文") < body.index("第 2 页译文")


def test_pdf_without_composer_fails_loudly(tmp_path, service, pages):
    with pytest.raises(PdfUnavailableError):
        service.export(_request(tmp_path, pages, fmt=ExportFormat.PDF))
    # the failure is recorded but nothing was written
    assert not (tmp_path / "out.pdf").exists()


def test_pdf_with_stub_composer(tmp_path, pages):
    from application.export import ExportService

    service = ExportService(make_service(tmp_path)._store, pdf_composer=StubPdfComposer())
    result = service.export(_request(tmp_path, pages, fmt=ExportFormat.PDF))
    payload = result.output_path.read_bytes()
    assert payload.startswith(b"%PDF-STUB")
    assert payload.rstrip().endswith(b"%%EOF")


# ----------------------------------------------------------------------
# scope / order / naming
# ----------------------------------------------------------------------


def test_scope_subset_exports_only_selected_pages_in_given_order(tmp_path, service, pages):
    reordered = [pages[2], pages[0]]
    result = service.export(_request(tmp_path, reordered))
    with zipfile.ZipFile(result.output_path) as archive:
        assert archive.namelist() == [
            "0001_page_02_第2页.png",
            "0002_page_00_第0页.png",
        ]
    assert result.page_ids == ("p2", "p0")


def test_hostile_filename_sanitized_for_windows(tmp_path, service):
    hostile = ExportPage(
        page_id="px",
        filename='..\\..\\evil<>:"|?.png',
        source_provider=lambda: b"PNG-x",
    )
    result = service.export(_request(tmp_path, [hostile]))
    with zipfile.ZipFile(result.output_path) as archive:
        name = archive.namelist()[0]
        assert name.startswith("0001_")
        assert ".." not in name
        assert not any(ch in name for ch in '<>:"|?')


def test_empty_scope_rejected(tmp_path, service):
    with pytest.raises(ExportValidationError):
        service.export(_request(tmp_path, []))


def test_output_path_without_filename_rejected(tmp_path, service, pages):
    target = tmp_path / "subdir"
    target.mkdir()
    with pytest.raises(ExportError):
        service.export(_request(tmp_path, pages, output_path=target))


def test_output_into_missing_directory_is_created(tmp_path, service, pages):
    result = service.export(
        _request(tmp_path, pages, output_path=tmp_path / "deep" / "nested" / "out.zip")
    )
    assert result.output_path.exists()


# ----------------------------------------------------------------------
# overwrite policies (已有目标文件)
# ----------------------------------------------------------------------


def test_overwrite_policy_replaces_existing_target(tmp_path, service, pages):
    target = tmp_path / "out.txt"
    target.write_bytes(b"OLD")
    service.export(_request(tmp_path, pages, fmt=ExportFormat.TEXT, output_path=target))
    assert b"OLD" not in target.read_bytes()


def test_skip_policy_keeps_existing_target_and_records_skipped(tmp_path, service, pages):
    target = tmp_path / "out.txt"
    target.write_bytes(b"OLD")
    result = service.export(
        _request(
            tmp_path,
            pages,
            fmt=ExportFormat.TEXT,
            output_path=target,
            overwrite_policy=OverwritePolicy.SKIP,
        )
    )
    assert target.read_bytes() == b"OLD"
    assert result.status.value == "skipped"
    assert result.output_path == target
    assert result.file_hash is None
    statuses = [record.status for record in service.history()]
    assert statuses[0] == "skipped"


def test_auto_rename_policy_writes_first_free_name(tmp_path, service, pages):
    target = tmp_path / "book.zip"
    target.write_bytes(b"OLD")
    result = service.export(
        _request(tmp_path, pages, output_path=target, overwrite_policy=OverwritePolicy.AUTO_RENAME)
    )
    assert target.read_bytes() == b"OLD"
    assert result.output_path.name == "book (1).zip"
    assert result.status.value == "completed"


# ----------------------------------------------------------------------
# stale / missing (AC-EXPORT-003, 缺译图)
# ----------------------------------------------------------------------


def _stale_and_missing(pages):
    stale = ExportPage(
        page_id=pages[0].page_id,
        filename=pages[0].filename,
        source_provider=pages[0].source_provider,
        translated_provider=pages[0].translated_provider,
        translated_revision_id="rev-old",
        current_translated_revision_id="rev-new",
        text=pages[0].text,
    )
    missing = ExportPage(
        page_id=pages[1].page_id,
        filename=pages[1].filename,
        source_provider=pages[1].source_provider,
        translated_provider=None,
        text=pages[1].text,
    )
    return [stale, missing]


def test_translated_export_with_stale_pages_is_refused_by_default(tmp_path, service, pages):
    with pytest.raises(StaleExportError) as excinfo:
        service.export(_request(tmp_path, _stale_and_missing(pages), mode="translated"))
    error = excinfo.value
    assert error.stale_page_ids == ("p0",)
    assert error.missing_page_ids == ("p1",)
    assert "重新渲染" in str(error)
    assert "继续导出现有版本" in str(error)
    assert not (tmp_path / "out.zip").exists()


def test_translated_export_can_explicitly_continue_with_existing_versions(
    tmp_path, service, pages
):
    result = service.export(
        _request(
            tmp_path,
            _stale_and_missing(pages),
            mode="translated",
            stale_policy=StalePolicy.CONTINUE,
        )
    )
    assert result.included_stale_page_ids == ("p0",)
    assert result.included_missing_page_ids == ("p1",)
    with zipfile.ZipFile(result.output_path) as archive:
        # stale keeps its (old) render; missing falls back to the original
        assert archive.read("0001_page_00_第0页.png") == b"PNG-trans-0"
        assert archive.read("0002_page_01_第1页.png") == b"PNG-orig-1"


def test_original_mode_never_triggers_stale_check(tmp_path, service, pages):
    result = service.export(_request(tmp_path, _stale_and_missing(pages), mode="original"))
    assert result.included_stale_page_ids == ()
    assert result.included_missing_page_ids == ()


# ----------------------------------------------------------------------
# cancellation & failure protection (取消/失败不得破坏目标与源文件)
# ----------------------------------------------------------------------


def test_cancel_before_replace_publishes_nothing(tmp_path, service, pages):
    target = tmp_path / "cancelled.zip"
    target.write_bytes(b"OLD-TARGET")
    calls = {"n": 0}

    def cancel() -> bool:
        calls["n"] += 1
        return calls["n"] > 1  # first check passes, next (mid-archive) cancels

    with pytest.raises(ExportCancelledError):
        service.export(_request(tmp_path, pages, output_path=target, cancel=cancel))
    assert target.read_bytes() == b"OLD-TARGET"
    assert not list(tmp_path.glob(".cancelled.zip*")), "temp file left behind"
    assert service.history()[0].status == "cancelled"


def test_failure_mid_export_keeps_old_target_and_records_failed(tmp_path, service, pages):
    target = tmp_path / "fail.zip"
    target.write_bytes(b"OLD-TARGET")

    def broken_provider():
        raise OSError("disk full while reading source")

    broken = ExportPage(
        page_id=pages[1].page_id,
        filename=pages[1].filename,
        source_provider=broken_provider,
    )
    with pytest.raises(OSError):
        service.export(_request(tmp_path, [pages[0], broken], output_path=target))
    assert target.read_bytes() == b"OLD-TARGET"
    assert not list(tmp_path.glob(".fail.zip*")), "temp file left behind"
    failed = service.history()[0]
    assert failed.status == "failed"
    assert "OSError" in failed.detail


def test_source_files_are_never_modified(tmp_path, service, pages):
    from reading_export_helpers import make_pages

    raw = make_pages(tmp_path / "src", count=3, translated=True)
    before = {path: path.read_bytes() for path in sorted((tmp_path / "src").iterdir())}
    service.export(_request(tmp_path, to_export_pages(raw), mode="translated"))
    after = {path: path.read_bytes() for path in sorted((tmp_path / "src").iterdir())}
    assert before == after


def test_disk_error_on_final_write_keeps_target(tmp_path, service, pages, monkeypatch):
    target = tmp_path / "out.zip"
    target.write_bytes(b"OLD-TARGET")

    def broken_write(self, payload):
        raise OSError("disk full")

    monkeypatch.setattr("pathlib.Path.write_bytes", broken_write)
    with pytest.raises(OSError):
        service.export(_request(tmp_path, pages, fmt=ExportFormat.TEXT, output_path=target))
    assert target.read_bytes() == b"OLD-TARGET"
    assert not list(tmp_path.glob(".out.zip.*")), "temp file left behind"


# ----------------------------------------------------------------------
# history (AC-EXPORT-002) & repeat (使用相同设置再次导出)
# ----------------------------------------------------------------------


def test_history_row_carries_d03_31_fields(tmp_path, service, pages):
    result = service.export(
        _request(
            tmp_path,
            pages,
            pipeline_run_id="run-1",
            render_profile_snapshot={"font": "Noto Sans CJK", "auto_size": True},
        )
    )
    record = service.find_export(result.export_id)
    assert record is not None
    assert record.book_id == "b"
    assert record.chapter_id == "c"
    assert record.pipeline_run_id == "run-1"
    assert record.export_type == "zip"
    scope = json.loads(record.scope_snapshot_json)
    assert scope["page_ids"] == ["p0", "p1", "p2"]
    assert scope["mode"] == "original"
    assert record.output_path.endswith(".zip")
    assert json.loads(record.render_profile_snapshot_json)["font"] == "Noto Sans CJK"
    assert record.status == "completed"
    assert len(record.file_hash) == 64
    assert record.created_at <= record.completed_at
    # history listing is most-recent-first
    assert service.history()[0].export_id == result.export_id


def test_repeat_exports_same_settings_with_fresh_bytes(tmp_path, service, pages):
    first = service.export(_request(tmp_path, pages, fmt=ExportFormat.ZIP))
    # source data changed after the first export
    (tmp_path / "src" / "page_00_第0页.png").write_bytes(b"PNG-orig-0-EDITED")
    pages_by_id = {page.page_id: page for page in pages}
    second = service.repeat(
        first.export_id, pages_by_id, overwrite_policy=OverwritePolicy.AUTO_RENAME
    )
    assert second.format is ExportFormat.ZIP
    assert second.mode == "original"
    assert second.page_ids == first.page_ids
    assert second.output_path != first.output_path
    assert second.status.value == "completed"
    with zipfile.ZipFile(second.output_path) as archive:
        assert archive.read("0001_page_00_第0页.png") == b"PNG-orig-0-EDITED"


def test_repeat_unknown_export_rejected(tmp_path, service, pages):
    with pytest.raises(ExportError):
        service.repeat("missing-id", {page.page_id: page for page in pages})


def test_history_survives_service_restart(tmp_path, service, pages):
    first = service.export(_request(tmp_path, pages))
    reloaded = make_service(tmp_path)
    assert reloaded.find_export(first.export_id).status == "completed"


# ----------------------------------------------------------------------
# real Qt PDF composer (runs only where PySide6 exists)
# ----------------------------------------------------------------------


def test_qt_pdf_composer_produces_re_readable_pdf(tmp_path):
    """QtImagePdfComposer 产物回读：结构级验证页数与 PDF 完整性（外部阅读器的像素级验收 NOT_RUN，环境无 QtPdf/阅读器）。"""
    pyside6 = pytest.importorskip("PySide6", reason="PySide6 not installed")
    from PySide6.QtGui import QGuiApplication, QImage, QColor

    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841
    from application.export import ExportService
    from application.export.pdf_qt import QtImagePdfComposer

    source = tmp_path / "src"
    source.mkdir()
    raw_pages = make_pages(source, count=2, translated=True)
    # replace the fake bytes with real decodable PNGs
    for index, page in enumerate(raw_pages):
        image = QImage(64, 96, QImage.Format.Format_RGB32)
        image.fill(QColor(60 * index + 30, 90, 120))
        assert image.save(page.original_path)
    pages = to_export_pages(raw_pages)

    service = ExportService(make_service(tmp_path)._store, pdf_composer=QtImagePdfComposer())
    result = service.export(_request(tmp_path, pages, fmt=ExportFormat.PDF))
    payload = result.output_path.read_bytes()
    assert payload.startswith(b"%PDF-") and payload.rstrip().endswith(b"%%EOF")

    # Structural re-read (PySide6 Essentials ships no QtPdf reader):
    # exactly one /Type /Page object per scope page, intact xref/EOF.
    page_objects = re.findall(rb"/Type /Page(?!s)", payload)
    assert len(page_objects) == 2, "one PDF page per scope page"
    assert b"/Count 2" in payload
    startxref = payload.rindex(b"startxref")
