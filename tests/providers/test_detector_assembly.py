"""T1.1.1: the production bootstrap wires the docTR detector fail-closed.

With weights absent (the default data root before anyone fetches them), the
app must still assemble and boot, and a page-level run must fail at the
``detect`` step with the typed ``PROVIDER_NOT_CONFIGURED`` — exactly the gap
behavior the unwired ``detector=None`` had, never a crash and never a silent
skip.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("PySide6")

from application.importing.images.ports import ImportSource  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)


def _png(width: int = 640, height: int = 400) -> bytes:
    """A plain blank page.

    Content is irrelevant — the wired detector fails closed on the missing
    weights before any inference sees pixels. QPainter *text* would abort the
    process (Qt font database requires a QGuiApplication), so this stays a
    pure QImage fill, same as ``tests/library/helpers.make_png``.
    """
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QColor, QImage

    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(QColor(0xFF, 0xFF, 0xFF))
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, "PNG")
    return bytes(buffer.data())


def _wired_detector(handler):
    """Reach the assembled detector through the ``_typed`` wrapper closure.

    ``ProductionHandlers._typed`` stores plain ``wrapped`` functions in the
    handler mapping, so the bound ``handle_detect`` — and with it the
    assembled detector — lives in closure cells rather than on ``__self__``.
    """
    for cell in handler.__closure__ or ():
        try:
            inner = cell.cell_contents
        except ValueError:  # empty cell
            continue
        bound = getattr(inner, "__self__", None)
        detector = getattr(getattr(bound, "deps", None), "detector", None)
        if detector is not None:
            return detector
    raise AssertionError("detect handler does not expose a wired detector")


def test_detector_is_wired_and_fails_closed_without_weights(
    tmp_path: Path, monkeypatch
) -> None:
    absent_weights = tmp_path / "absent" / "fast_base-688a8b34.pt"
    monkeypatch.setenv("NEWMANGA_DETECTOR_WEIGHTS", str(absent_weights))
    monkeypatch.delenv("NEW_MANGA_DOCTR_WEIGHTS", raising=False)
    from bootstrap.app import assemble_services
    from infrastructure.providers.detection_doctr import DoctrDetectionProvider

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        # wired, not None, and of the selected adapter type
        handlers = services.pipeline._executor._handlers
        assert "detect" in handlers
        detector = _wired_detector(handlers["detect"])
        assert isinstance(detector, DoctrDetectionProvider)
        assert detector.provider_id == "local-doctr"
        assert detector.weights_path == absent_weights

        book = services.library.create_book("检测装配")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        report = services.importer.import_files(
            chapter.chapter_id,
            [ImportSource(filename="page.png", data_provider=lambda: _png())],
        )
        page = report.imported[0].page
        assert services.editing.list_regions(page.page_id) == []

        run = services.pipeline.create_run(
            CommandType.TRANSLATE_ALL,
            PipelineScope(ScopeType.CHAPTER, chapter_id=chapter.chapter_id),
        )
        services.pipeline.plan_run(run.run_id)
        executed = services.pipeline.execute_run(run.run_id)

        assert executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES
        detect_step = executed.step_runs[0]
        assert detect_step.step_type == "detect"
        assert detect_step.status is StepRunStatus.FAILED
        assert detect_step.error_code == "PROVIDER_NOT_CONFIGURED"
        # the failure names the missing weights — proof it was raised by the
        # wired provider, not by an unwired assembly slot (detector=None)
        assert str(absent_weights) in (detect_step.error_detail or "")
        # no machine Region was invented behind the failure
        assert services.editing.list_regions(page.page_id) == []
        # the app is still usable after the failed run
        assert services.library.list_books()[0].book_id == book.book_id
    finally:
        services.conn.close()
