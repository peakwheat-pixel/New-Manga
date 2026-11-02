"""P09 Managed Copy safety gates that do not require the optional Qt runtime."""

from __future__ import annotations

import hashlib
import json
import sqlite3
import struct
from pathlib import Path

import pytest

from application.importing.images.ports import DecodedImage
from application.importing.images.sorting import sources_from_selection
from application.importing.images.service import DuplicatePolicy
from helpers import make_thin_png


class _PngFixtureDecoder:
    """Read dimensions from the known-valid PNG fixtures built below."""

    def decode(self, data: bytes) -> DecodedImage:
        if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
            raise ValueError("invalid fixture PNG")
        width, height = struct.unpack(">II", data[16:24])
        return DecodedImage(width, height, "image/png")


def _production_core(data_root: Path):
    from bootstrap.core_service import assemble_production_core

    core = assemble_production_core(data_root)
    # Keep the storage/database safety tests independent of Qt decoding.
    core.importer._decoder = _PngFixtureDecoder()
    return core


@pytest.mark.parametrize("failure_point", ["publish", "page_insert"])
def test_copy_or_page_failure_never_leaves_a_page_without_a_managed_original(
    tmp_path, monkeypatch, failure_point
):
    core = _production_core(tmp_path / "core")
    source_root = tmp_path / "selected"
    source_root.mkdir()
    source = source_root / "page.png"
    data = make_thin_png(8, 6)
    source.write_bytes(data)
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    try:
        book = core.library.create_book("P09 interruption")
        chapter = core.library.create_chapter(book.book_id, "chapter")
        if failure_point == "publish":
            def interrupt_publish(temp_handle, relative_path):
                del relative_path
                Path(temp_handle).write_bytes(b"partial copy")
                raise OSError("injected copy interruption")

            monkeypatch.setattr(core.storage, "publish", interrupt_publish)
        else:
            def interrupt_page_insert(page):
                del page
                raise sqlite3.OperationalError("injected Page transaction failure")

            monkeypatch.setattr(core.repository, "add_page", interrupt_page_insert)

        if failure_point == "page_insert":
            with pytest.raises(sqlite3.OperationalError):
                core.importer.import_files(
                    chapter.chapter_id, sources_from_selection(source_root, [source])
                )
            report = None
        else:
            report = core.importer.import_files(
                chapter.chapter_id, sources_from_selection(source_root, [source])
            )

        assert core.repository.list_pages(chapter.chapter_id) == []
        originals = list((tmp_path / "core" / "managed" / "books").rglob("*.png"))
        if failure_point == "publish":
            assert report is not None
            assert report.failed[0].reason == "COPY_FAILED"
            assert originals == []
            assert list((tmp_path / "core" / "managed" / "temp").iterdir()) == []
        else:
            assert len(originals) == 1
            assert originals[0].read_bytes() == data
        assert hashlib.sha256(source.read_bytes()).hexdigest() == source_hash
    finally:
        core.conn.close()


def test_source_hash_survives_import_hide_and_permanent_page_purge(tmp_path):
    core = _production_core(tmp_path / "core")
    source_root = tmp_path / "selected"
    source_root.mkdir()
    source = source_root / "source.png"
    source.write_bytes(make_thin_png(6, 4))
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    stages = {"before_import": source_hash}
    try:
        book = core.library.create_book("P09 source protection")
        chapter = core.library.create_chapter(book.book_id, "chapter")
        report = core.importer.import_files(
            chapter.chapter_id, sources_from_selection(source_root, [source])
        )
        page = report.imported[0].page
        stages["after_import"] = hashlib.sha256(source.read_bytes()).hexdigest()

        core.library.delete_book(book.book_id)
        stages["after_project_hide"] = hashlib.sha256(source.read_bytes()).hexdigest()
        batch = core.trash.soft_delete_pages(chapter.chapter_id, [page.page_id])
        stages["after_page_delete"] = hashlib.sha256(source.read_bytes()).hexdigest()
        core.trash.purge_batch(batch.batch_id)
        stages["after_permanent_managed_page_purge"] = hashlib.sha256(
            source.read_bytes()
        ).hexdigest()

        assert set(stages.values()) == {source_hash}
        assert source.is_file()
        (tmp_path / "source-hash-evidence.json").write_text(
            json.dumps(
                {"source": str(source), "sha256_by_stage": stages},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    finally:
        core.conn.close()


def test_source_hash_survives_translation_repair_and_rerender(tmp_path):
    from bootstrap.acceptance_bridge import assemble_acceptance_core
    from domain.regions.entities import BBox, RegionGeometry, RegionOrigin
    from domain.tasks.models import CommandType, PipelineScope, ScopeType

    source_root = tmp_path / "selected"
    source_root.mkdir()
    source = source_root / "source.png"
    source.write_bytes(make_thin_png(64, 64))
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    stages = {"before_import": source_hash}
    core = assemble_acceptance_core(
        tmp_path / "core" / "library.db", tmp_path / "core" / "managed"
    )
    try:
        book = core.library.create_book("P09 source protection workflows")
        chapter = core.library.create_chapter(book.book_id, "chapter")
        report = core.importer.import_files(
            chapter.chapter_id, sources_from_selection(source_root, [source])
        )
        assert report.failed == () and len(report.imported) == 1
        page = report.imported[0].page
        stages["after_import"] = hashlib.sha256(source.read_bytes()).hexdigest()
        region = core.editing.create_region(
            page.page_id,
            RegionGeometry(
                bbox=BBox(8, 8, 40, 30),
                polygon=((8, 8), (48, 8), (48, 38), (8, 38)),
            ),
            reading_order=1,
            origin=RegionOrigin.USER,
        )
        core.pipeline_defaults.save_provider_binding("ocr", "m2ac1-mock-ocr")
        core.pipeline_defaults.save_provider_binding(
            "translate", "m2ac1-mock-translate"
        )

        def run(command, scope):
            result = core.pipeline.create_run(command, scope)
            core.pipeline.plan_run(result.run_id)
            result = core.pipeline.execute_run(result.run_id)
            if result.status == "blocked":
                core.pipeline.plan_run(result.run_id, mode="resume_blocked")
                result = core.pipeline.execute_run(result.run_id)
            assert result.status == "completed", (command.value, result.status)
            return result

        translated = run(
            CommandType.TRANSLATE_ALL,
            PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
        )
        assert any(
            step.step_type == "translate" and step.status.value == "completed"
            for step in translated.step_runs
        )
        stages["after_translation"] = hashlib.sha256(source.read_bytes()).hexdigest()
        repaired = run(
            CommandType.REINPAINT_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=(region.region_id,)),
        )
        assert any(
            step.step_type == "inpaint" and step.status.value == "completed"
            for step in repaired.step_runs
        )
        stages["after_repair"] = hashlib.sha256(source.read_bytes()).hexdigest()
        rerendered = run(
            CommandType.RERENDER_SINGLE,
            PipelineScope(ScopeType.PAGE, selected_ids=(page.page_id,)),
        )
        assert any(
            step.step_type == "render" and step.status.value == "completed"
            for step in rerendered.step_runs
        )
        stages["after_rerender"] = hashlib.sha256(source.read_bytes()).hexdigest()

        assert set(stages.values()) == {source_hash}
        assert source.is_file()
        (tmp_path / "source-hash-workflows.json").write_text(
            json.dumps(
                {
                    "source": str(source),
                    "sha256_by_stage": stages,
                    "operations": ["TRANSLATE_ALL", "REINPAINT_REGION", "RERENDER_SINGLE"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
    finally:
        core.conn.close()


def test_unicode_folder_paths_import_all_supported_name_categories(tmp_path):
    core = _production_core(tmp_path / "core")
    source_root = tmp_path / "漫画 日本語 한국어 😀 (spaces and parentheses)"
    source_root.mkdir()
    dimensions_by_name = {}
    for index, label in enumerate(("中文", "日本語", "한국어", "😀 Emoji", "spaces (1)")):
        name = f"page{index + 1}-{label}.png"
        data = make_thin_png(index + 3, index + 5)
        (source_root / name).write_bytes(data)
        dimensions_by_name[name] = (index + 3, index + 5)
    try:
        book = core.library.create_book("P09 Unicode")
        chapter = core.library.create_chapter(book.book_id, "chapter")
        report = core.importer.import_files(
            chapter.chapter_id, sources_from_selection(source_root)
        )

        assert report.failed == () and len(report.imported) == len(dimensions_by_name)
        assert {
            item.page.source_filename: (item.page.width, item.page.height)
            for item in report.imported
        } == dimensions_by_name
    finally:
        core.conn.close()


def test_duplicate_images_are_hash_skipped_unless_explicitly_imported_as_new(tmp_path):
    core = _production_core(tmp_path / "core")
    source_root = tmp_path / "selected"
    source_root.mkdir()
    original = source_root / "original.png"
    duplicate = source_root / "renamed copy.png"
    data = make_thin_png(9, 7)
    original.write_bytes(data)
    duplicate.write_bytes(data)
    try:
        book = core.library.create_book("P09 duplicate")
        chapter = core.library.create_chapter(book.book_id, "chapter")
        first = core.importer.import_files(
            chapter.chapter_id, sources_from_selection(source_root, [original])
        )
        first_page = first.imported[0].page
        original_copy = Path(core.storage.absolute_path(first_page.managed_original_ref))
        first_copy_bytes = original_copy.read_bytes()

        skipped = core.importer.import_files(
            chapter.chapter_id, sources_from_selection(source_root, [duplicate])
        )
        assert skipped.imported == ()
        assert skipped.skipped_duplicates == (duplicate.name,)
        assert original_copy.read_bytes() == first_copy_bytes
        assert len(core.repository.list_pages(chapter.chapter_id)) == 1

        copied_as_new = core.importer.import_files(
            chapter.chapter_id,
            sources_from_selection(source_root, [duplicate]),
            duplicate_policy=DuplicatePolicy.IMPORT_AS_NEW,
        )
        second_page = copied_as_new.imported[0].page
        assert second_page.page_id != first_page.page_id
        assert second_page.source_hash == first_page.source_hash
        assert second_page.managed_original_ref != first_page.managed_original_ref
        assert original_copy.read_bytes() == first_copy_bytes
        assert len(core.repository.list_pages(chapter.chapter_id)) == 2
    finally:
        core.conn.close()


def test_corrupt_pdf_is_rejected_before_managed_copy_or_page_write(tmp_path):
    core = _production_core(tmp_path / "core")
    source_root = tmp_path / "selected"
    source_root.mkdir()
    broken = source_root / "damaged.pdf"
    broken.write_bytes(b"%PDF-1.7\nthis is not a valid PDF")
    try:
        book = core.library.create_book("P09 corrupt PDF")
        chapter = core.library.create_chapter(book.book_id, "chapter")
        report = core.document_importer.import_documents(
            chapter.chapter_id, sources_from_selection(source_root, [broken])
        )

        assert report.imported == ()
        assert len(report.failed) == 1
        assert report.failed[0].reason == "INVALID_DOCUMENT"
        assert core.repository.list_pages(chapter.chapter_id) == []
        managed = tmp_path / "core" / "managed"
        assert not list((managed / "books").rglob("*.png"))
        assert list((managed / "temp").iterdir()) == []
    finally:
        core.conn.close()
