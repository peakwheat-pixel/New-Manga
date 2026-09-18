"""TASK-051 AC ①②③: the workbench viewer resolves translated/compare.

``compare`` is the D05 §20.1 side-by-side: the left pane is the original
Managed Copy and the right pane is the translated variant — so the
catalog resolves ``translated`` through the *same* artifact locator the
reader uses (AC ② pins the same revision), and every failure stays ""
for QML while :meth:`image_state` carries the typed reason (AC ③).
Before TASK-051 both modes returned "" unconditionally (the P-6 probe).
"""

from __future__ import annotations

from urllib.request import url2pathname
from urllib.parse import urlparse

from application.importing.images.ports import ImportSource
from bootstrap.app import (
    _ManagedReaderCatalog,
    _ManagedPageCatalog,
    assemble_services,
)
from infrastructure.providers.step_writes import ArtifactStepWriter
from ports.repositories.artifacts import ArtifactType
from infrastructure.rendering.locator import SqlitePageArtifactLocator

from tests.core.test_bootstrap import _make_png


def _uri_path(url: str):
    return url2pathname(urlparse(url).path)


def _import_pages(services, chapter_id: str, count: int = 2):
    report = services.importer.import_files(
        chapter_id,
        [
            ImportSource(
                filename=f"p{i}.png",
                data_provider=lambda i=i: _make_png(40 + i, 60),
            )
            for i in range(count)
        ],
    )
    return [row.page for row in report.imported]


def _publish_translated(services, page_id: str) -> None:
    writer = ArtifactStepWriter(services.conn, services.storage)
    prepared = writer.prepare_revision(
        page_id=page_id,
        artifact_type="translated",
        payload=_make_png(41, 61),
        mime_type="image/png",
        width=41,
        height=61,
    )
    writer.adopt_current(
        artifact_id=prepared.artifact_id,
        revision_id=prepared.revision_id,
        expected_current_revision_id=prepared.previous_revision_id,
    )


def test_translated_and_compare_resolve_like_the_reader(tmp_path) -> None:
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        book = services.library.create_book("三档书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        page_a, page_b = _import_pages(services, chapter.chapter_id)
        _publish_translated(services, page_a.page_id)

        vm = services.workbench
        vm._apply_viewer_page(page_a.page_id)
        translated_url = vm.viewerImageUrlFor("translated")
        assert translated_url.startswith("file:"), translated_url

        # AC ②: the very same revision the reader catalog resolves
        reader = _ManagedReaderCatalog(
            services.repository,
            services.storage,
            SqlitePageArtifactLocator(services.conn),
        )
        reader_page = next(
            row
            for row in reader.list_pages(chapter.chapter_id)
            if row.page_id == page_a.page_id
        )
        assert reader_page.translated_path is not None
        assert _uri_path(translated_url) == str(reader_page.translated_path)

        # AC ①: compare shows the side-by-side left pane = the original
        assert vm.viewerImageUrlFor("compare") == vm.viewerImageUrlFor("original")
        assert vm.viewerImageStateFor("original") == "ok"
        assert vm.viewerImageStateFor("translated") == "ok"
        assert vm.viewerImageStateFor("compare") == "ok"

        # the sibling page has no translated data at all
        vm._apply_viewer_page(page_b.page_id)
        assert vm.viewerImageUrlFor("translated") == ""
        assert vm.viewerImageUrlFor("compare") != ""  # original pane still shows
        assert vm.viewerImageStateFor("translated") == "missing"

        # clean stays out of this slice's scope (not a silent wrong image)
        assert vm.viewerImageUrlFor("clean") == ""
    finally:
        services.conn.close()


def test_invalid_paths_stay_diagnosable_not_silent(tmp_path) -> None:
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        book = services.library.create_book("失效书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        (page,) = _import_pages(services, chapter.chapter_id, count=1)
        _publish_translated(services, page.page_id)

        vm = services.workbench
        vm._apply_viewer_page(page.page_id)
        assert vm.viewerImageStateFor("translated") == "ok"

        # the managed file vanishes: "invalid", not "missing"
        located = SqlitePageArtifactLocator(services.conn).locate_current(
            page.page_id, ArtifactType.TRANSLATED
        )
        assert located is not None
        _record, revision = located
        (tmp_path / "managed" / revision.managed_path).unlink()
        assert vm.viewerImageStateFor("translated") == "invalid"
        assert vm.viewerImageUrlFor("translated") == ""
        assert vm.viewerImageStateFor("original") == "ok"
    finally:
        services.conn.close()


def test_page_catalog_degrades_without_a_locator(tmp_path) -> None:
    """The catalog contract never regresses the original-mode behaviour a
    caller assembled before TASK-051 could have relied on."""
    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        book = services.library.create_book("契约书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        (page,) = _import_pages(services, chapter.chapter_id, count=1)
        legacy = _ManagedPageCatalog.__new__(_ManagedPageCatalog)
        legacy._repository = services.repository
        legacy._storage = services.storage
        legacy._locator = SqlitePageArtifactLocator(services.conn)
        url = legacy.image_url(page.page_id, "original")
        assert url.startswith("file:")
        assert legacy.image_url(page.page_id, "nonsense") == ""
    finally:
        services.conn.close()
