import zipfile
from pathlib import Path

import pytest

from application.export.service import ExportFormat, ExportPage, ExportRequest, ExportService


def _pages(tmp_path: Path):
    first = tmp_path / "一.png"
    second = tmp_path / "二.png"
    first.write_bytes(b"one")
    second.write_bytes(b"two")
    return [
        ExportPage("p1", "一.png", first, "text one", "r1", "r1"),
        ExportPage("p2", "二.png", second, "text two", "r2", "r2"),
    ]


@pytest.mark.parametrize("fmt", [ExportFormat.ZIP, ExportFormat.CBZ])
def test_archive_export_preserves_requested_order_and_unicode_names(tmp_path: Path, fmt):
    target = tmp_path / f"成果.{fmt.value}"
    result = ExportService(tmp_path / "history.json").export(
        ExportRequest("book", "chapter", fmt, target, _pages(tmp_path))
    )
    assert result.path == target
    with zipfile.ZipFile(target) as archive:
        assert archive.namelist() == ["一.png", "二.png"]
        assert archive.read("一.png") == b"one"


def test_all_formats_and_text_contents_are_readable(tmp_path: Path):
    pages = _pages(tmp_path)
    service = ExportService(tmp_path / "history.json")
    for fmt in (ExportFormat.IMAGE, ExportFormat.PDF, ExportFormat.TEXT):
        target = tmp_path / f"output-{fmt.value}"
        result = service.export(ExportRequest("b", "c", fmt, target, pages[:1]))
        assert result.path.read_bytes()
        if fmt is ExportFormat.PDF:
            assert result.path.read_bytes().startswith(b"%PDF-")
        if fmt is ExportFormat.TEXT:
            assert result.path.read_text(encoding="utf-8") == "text one\n"
    assert len(service.history()) == 3


def test_stale_abort_and_failed_or_cancelled_export_keep_existing_target(tmp_path: Path):
    pages = _pages(tmp_path)
    stale = [ExportPage("p1", "x.png", pages[0].source_path, "x", "old", "new")]
    target = tmp_path / "existing.zip"
    target.write_bytes(b"keep")
    service = ExportService(tmp_path / "history.json")
    with pytest.raises(ValueError, match="stale"):
        service.export(ExportRequest("b", "c", ExportFormat.ZIP, target, stale, mode="translated"))
    with pytest.raises(FileExistsError):
        service.export(ExportRequest("b", "c", ExportFormat.ZIP, target, pages))
    with pytest.raises(RuntimeError, match="cancel"):
        service.export(ExportRequest("b", "c", ExportFormat.ZIP, target, pages, overwrite=True, cancel=lambda: True))
    assert target.read_bytes() == b"keep"


def test_archive_rejects_path_traversal_filename(tmp_path: Path):
    pages = _pages(tmp_path)
    pages[0] = ExportPage("p1", "../escape.png", pages[0].source_path, "text", "r", "r")
    with pytest.raises(ValueError, match="invalid archive filename"):
        ExportService(tmp_path / "history.json").export(
            ExportRequest("b", "c", ExportFormat.ZIP, tmp_path / "x.zip", pages)
        )
