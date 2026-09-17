"""Real bootstrap assembly with failed-closed providers (AC-OPTIONAL-001/002).

This is the end-to-end proof for the environment registered as BLOCKED: the
production stack starts with no heavy runtime installed, reports every
unavailable provider as Not-Ready, and a Run against an unconfigured provider
fails the step with a typed code instead of crashing the app or inventing a
result.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from application.importing.images.ports import ImportSource  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
from infrastructure.sqlite.regions import SqliteRegionRepository  # noqa: E402


def _png(width: int = 24, height: int = 24) -> bytes:
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFFE0E0E0)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "PNG")
    return bytes(buffer.data())


def test_production_stack_starts_without_heavy_runtimes(tmp_path: Path) -> None:
    """AC-OPTIONAL-001/002: missing models must not stop the application."""
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        status = services.providers.status()
        states = {
            entry["provider_id"]: entry["state"] for entry in status["providers"]
        }
        assert states["manga-ocr"] == "missing_dependency"
        assert states["paddleocr-korean"] == "missing_dependency"
        assert states["openai-vision-ocr"] == "not_configured"
        assert states["inpaint-simple-fill"] == "ready"
        assert states["inpaint-edge-bleed"] == "ready"
        assert states["inpaint-manga-lama"] == "not_ready"
        assert status["gpu"]["state"] == "unavailable"
        assert status["models"] == []
    finally:
        services.conn.close()


def test_run_with_unconfigured_provider_fails_closed(tmp_path: Path) -> None:
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        book = services.library.create_book("OCR 失败关闭")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        report = services.importer.import_files(
            chapter.chapter_id,
            [ImportSource(filename="page.png", data_provider=lambda: _png())],
        )
        page = report.imported[0].page
        region = services.editing.create_region(
            page.page_id, RegionGeometry(BBox(2, 2, 6, 6))
        )

        run = services.pipeline.create_run(
            CommandType.OCR_REGION,
            PipelineScope(ScopeType.REGION, selected_ids=(region.region_id,)),
        )
        services.pipeline.plan_run(run.run_id)
        executed = services.pipeline.execute_run(run.run_id)

        assert executed.status in {
            PipelineRunStatus.BLOCKED,
            PipelineRunStatus.COMPLETED_WITH_FAILURES,
        }
        assert all(step.status is not StepRunStatus.COMPLETED for step in executed.step_runs)
        codes = {
            step.error_code for step in executed.step_runs if step.error_code
        } | {
            unit.reason or "" for unit in executed.tasks[0].units if unit.reason
        }
        assert codes & {"PROVIDER_NOT_CONFIGURED", "PROVIDER_UNAVAILABLE"}, codes

        stored = services.editing.get_region(region.region_id)
        assert stored.text.ocr_text == ""
        # The app is still usable after the failed Run.
        assert services.library.list_books()[0].book_id == book.book_id
    finally:
        services.conn.close()


def test_ocr_handler_uses_the_managed_original_and_writes_one_region(
    tmp_path: Path,
) -> None:
    """The region crop path is real Qt decoding of the Managed Copy."""
    from bootstrap.app import _ManagedPageImageSource, _RegionGeometrySource
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        book = services.library.create_book("裁剪")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        report = services.importer.import_files(
            chapter.chapter_id,
            [ImportSource(filename="page.png", data_provider=lambda: _png(30, 20))],
        )
        page = report.imported[0].page
        region = services.editing.create_region(
            page.page_id, RegionGeometry(BBox(4, 5, 8, 6))
        )

        source = _ManagedPageImageSource(
            services.repository, services.storage, SqliteRegionRepository(services.conn)
        )
        page_frame = source.page_frame(page.page_id)
        assert (page_frame.width, page_frame.height) == (30, 20)
        crop, width, height = source.region_crop(page.page_id, region.region_id)
        assert crop.startswith(b"\x89PNG")
        assert (width, height) == (8, 6)

        geometry = _RegionGeometrySource(
            SqliteRegionRepository(services.conn)
        ).mask_geometry(region.region_id)
        assert geometry.boxes == ((4, 5, 12, 11),)

        text = json.loads(
            services.conn.execute(
                "SELECT text_json FROM regions WHERE region_id = ?",
                (region.region_id,),
            ).fetchone()["text_json"]
        )
        assert text["ocr_text"] == ""
    finally:
        services.conn.close()
