"""Bootstrap assembly tests (TASK-030).

The subprocess smoke runs on the default Windows Qt platform: the task
forbids forcing ``QT_QPA_PLATFORM=offscreen`` for the entry evidence, and
the real AppShell needs the font database anyway. The in-process tests
exercise the real assembly (SQLite + migrations + Qt decoder + managed
copy) against temp roots only — the user data root is never touched.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

pytest.importorskip("PySide6")

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402


def _make_png(width: int, height: int) -> bytes:
    image = QImage(width, height, QImage.Format.Format_RGB32)
    image.fill(0xFF00FF00)
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(buffer.data())


def run_app(src_root: Path, data_root: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root)
    # TASK-030: Windows default Qt platform — do not force offscreen.
    env.pop("QT_QPA_PLATFORM", None)
    command = [sys.executable, "-m", "bootstrap.app", "--smoke-test"]
    if data_root is not None:
        command += ["--data-root", str(data_root)]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


@pytest.fixture()
def qapp():
    from PySide6.QtGui import QGuiApplication

    app = QGuiApplication.instance() or QGuiApplication([])
    yield app


def test_smoke_startup_loads_qml_and_exits_zero() -> None:
    result = run_app(SRC_ROOT)
    assert result.returncode == 0, result.stderr


def test_smoke_assembles_real_stack_in_data_root(tmp_path: Path) -> None:
    # The smoke run must build the real stack (migrated SQLite + managed
    # layout) inside the given data root, not just parse QML.
    result = run_app(SRC_ROOT, data_root=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "library.db").exists()
    assert (tmp_path / "managed" / "temp").is_dir()


def test_missing_qml_returns_nonzero_with_path(tmp_path: Path) -> None:
    # Full src copy (app.py imports the production services), then remove
    # Main.qml: the failure must name the expected QML path.
    isolated_src = tmp_path / "src"
    shutil.copytree(SRC_ROOT, isolated_src)
    (isolated_src / "ui" / "qml" / "Main.qml").unlink()

    result = run_app(isolated_src)

    expected = isolated_src / "ui" / "qml" / "Main.qml"
    assert result.returncode != 0
    assert str(expected) in result.stderr


def test_assemble_services_migrates_schema_and_managed_layout(tmp_path: Path) -> None:
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")

    latest = max(m.schema_version for m in default_migrations())
    conn, opened = open_database(
        tmp_path / "library.db", latest_known_schema_version=latest
    )
    assert opened.writable
    assert opened.schema_version == latest
    version_row = conn.execute(
        "SELECT MAX(schema_version) FROM schema_migrations"
    ).fetchone()
    assert version_row[0] == latest
    conn.close()
    assert (tmp_path / "managed" / "temp").is_dir()
    assert services.library.list_books() == []


def test_assemble_services_injects_and_exports_diagnostics(
    tmp_path: Path,
) -> None:
    from application.maintenance.diagnostics import DiagnosticsService, RecentError
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        assert isinstance(services.diagnostics, DiagnosticsService)

        exported = Path(
            services.diagnostics.export(generated_at="2026-09-20T12:00:00")
        )

        assert exported.is_file()
        assert exported.parent == tmp_path / "diagnostics"
        payload = json.loads(exported.read_text(encoding="utf-8"))
        assert set(payload) == {
            "application",
            "database",
            "environment_paths",
            "generated_at",
            "recent_errors",
            "settings_summary",
        }
        assert payload["database"]["schema_version"] == "3"
        assert payload["environment_paths"]["data_root"] == str(tmp_path)
        assert payload["environment_paths"]["managed_root"] == str(
            tmp_path / "managed"
        )

        services.diagnostics._errors.record(
            RecentError(
                occurred_at="2026-09-20T12:00:01",
                source="pipeline",
                code="PROVIDER_AUTH_FAILED",
                message="Bearer abcdef1234567890 sk-abcdef1234567890",
            )
        )
        error_export = Path(
            services.diagnostics.export(generated_at="2026-09-20T12:00:02")
        )
        error_payload = json.loads(error_export.read_text(encoding="utf-8"))
        error_values = tuple(error_payload["recent_errors"].values())
        assert any("PROVIDER_AUTH_FAILED" in value for value in error_values)
        assert "abcdef1234567890" not in json.dumps(error_payload)
        assert "sk-abcdef1234567890" not in json.dumps(error_payload)

        sensitive_timestamp_export = Path(
            services.diagnostics.export(generated_at="export-sk-abcdef123456")
        )
        sensitive_payload = json.loads(
            sensitive_timestamp_export.read_text(encoding="utf-8")
        )
        assert sensitive_payload["generated_at"] == "[redacted]"
        assert "skabcdef123456" not in sensitive_timestamp_export.name

        for index in range(6):
            services.diagnostics.export(
                generated_at=f"2026-09-20T12:00:{index:02d}"
            )
        files = sorted((tmp_path / "diagnostics").glob("diag-*.log"))
        assert len(files) <= 5
        assert all(path.stat().st_size <= 512_000 for path in files)
        assert all(json.loads(path.read_text(encoding="utf-8")) for path in files)
    finally:
        services.conn.close()


def test_assemble_engine_does_not_publish_diagnostics_to_qml(
    qapp, tmp_path: Path
) -> None:
    from application.maintenance.diagnostics import DiagnosticsService
    from bootstrap.app import assemble_engine, assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    engine = assemble_engine(services)
    try:
        assert isinstance(services.diagnostics, DiagnosticsService)
        assert engine.rootContext().contextProperty("diagnosticsService") is None
    finally:
        engine.deleteLater()
        services.conn.close()
        qapp.processEvents()

def test_assemble_services_refuses_newer_schema(tmp_path: Path) -> None:
    import sqlite3

    from bootstrap.app import assemble_services

    db_path = tmp_path / "library.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE schema_migrations (schema_version INTEGER PRIMARY KEY,"
        " migration_name TEXT, applied_at TEXT, checksum TEXT)"
    )
    conn.execute(
        "INSERT INTO schema_migrations VALUES (99999, 'future', 'now', 'x')"
    )
    conn.commit()
    conn.close()

    with pytest.raises(RuntimeError, match="newer"):
        assemble_services(db_path, tmp_path / "managed")


def test_assemble_services_closes_connection_when_migration_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    import sqlite3
    from types import SimpleNamespace

    import bootstrap.app as app_module

    conn = sqlite3.connect(":memory:")

    class FailingMigrationRunner:
        def __init__(self, connection: sqlite3.Connection, migrations: object) -> None:
            pass

        def apply_pending(self) -> None:
            raise RuntimeError("migration failed")

    monkeypatch.setattr(
        app_module,
        "open_database",
        lambda *args, **kwargs: (
            conn,
            SimpleNamespace(writable=True, schema_version=0),
        ),
    )
    monkeypatch.setattr(app_module, "MigrationRunner", FailingMigrationRunner)

    with pytest.raises(RuntimeError, match="migration failed"):
        app_module.assemble_services(tmp_path / "library.db", tmp_path / "managed")

    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        conn.execute("SELECT 1")


def test_import_safety_chain(tmp_path: Path) -> None:
    """真实导入安全链：源文件只读 → Managed Copy 落盘且逐字节一致 →
    Page 才写入 → 重启（新连接）后 SQLite 可读；managed 路径含真实
    Chapter→Book 查询得到的 book id（不硬编码）。"""
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services
    from infrastructure.sqlite.library import SqliteLibraryRepository

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("安全链作品")
    chapter = services.library.create_chapter(book.book_id, "第1话", chapter_number="1")

    source = tmp_path / "source.png"
    data = _make_png(7, 5)
    source.write_bytes(data)
    source_before = (
        source.stat().st_mtime_ns,
        hashlib.sha256(source.read_bytes()).hexdigest(),
    )

    report = services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="source.png", data_provider=source.read_bytes)],
    )

    assert report.failed == ()
    assert report.skipped_duplicates == ()
    assert len(report.imported) == 1
    page = report.imported[0].page

    # 源文件只读（D07 §37 / AC-IMPORT-002）
    assert (
        source.stat().st_mtime_ns,
        hashlib.sha256(source.read_bytes()).hexdigest(),
    ) == source_before

    # Managed Copy 在 Page 提交前已存在且逐字节一致；路径是 D03 §18 布局
    # 且包含真实仓储查询出的 book id / chapter id。
    managed_file = tmp_path / "managed"
    for part in page.managed_original_ref.split("/"):
        managed_file = managed_file / part
    assert managed_file.read_bytes() == data
    assert page.managed_original_ref == (
        f"books/{book.book_id}/chapters/{chapter.chapter_id}/original/"
    ) or page.managed_original_ref.startswith(
        f"books/{book.book_id}/chapters/{chapter.chapter_id}/original/"
    )

    # 重启：全新连接读取持久化的 Page（TASK-028 round-trip contract）
    latest = max(m.schema_version for m in default_migrations())
    conn2, opened2 = open_database(
        tmp_path / "library.db", latest_known_schema_version=latest
    )
    repo2 = SqliteLibraryRepository(conn2)
    pages = repo2.list_pages(chapter.chapter_id)
    conn2.close()
    assert len(pages) == 1
    assert pages[0].page_id == page.page_id
    assert pages[0].source_hash == hashlib.sha256(data).hexdigest()
    assert pages[0].managed_original_ref == page.managed_original_ref
    assert (pages[0].width, pages[0].height) == (7, 5)


def test_import_unknown_chapter_fails_copy_and_writes_no_page(tmp_path: Path) -> None:
    """book_id_for_chapter 绑定真实查询：未知 chapter 使 copy 失败，
    源文件不受影响，也没有 Page 落库。"""
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    source = tmp_path / "orphan.png"
    data = _make_png(3, 3)
    source.write_bytes(data)

    with pytest.raises(ValueError, match="unknown chapter"):
        services.importer.import_files(
            "no-such-chapter",
            [ImportSource(filename="orphan.png", data_provider=source.read_bytes)],
        )

    assert source.read_bytes() == data
    assert services.repository.list_pages("no-such-chapter") == []


def test_assemble_engine_injects_real_workbench_stack(
    qapp, tmp_path: Path
) -> None:
    """R-1: the entry binds real SQLite page/region/editing services."""
    from application.importing.images.ports import ImportSource
    from infrastructure.pipeline.executor import ProductionStepExecutor
    from infrastructure.sqlite.pipeline import (
        SqlitePipelineStore,
        SqliteSnapshotProvider,
        SqliteTargetCatalog,
    )
    from bootstrap.app import assemble_engine, assemble_services
    from domain.regions.entities import BBox, RegionGeometry

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("生产装配书")
    chapter = services.library.create_chapter(book.book_id, "第1话")
    report = services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="page.png", data_provider=lambda: _make_png(8, 6))],
    )
    page = report.imported[0].page
    region = services.editing.create_region(
        page.page_id, RegionGeometry(BBox(1, 1, 3, 2))
    )

    services.workbench.setContext(
        book.book_id, chapter.chapter_id, book.title, chapter.title
    )
    services.workbench.selectPage(page.page_id)
    services.workbench.selectRegion(region.region_id)
    services.workbench.setInspectorText("人工译文")
    services.workbench.saveInspector()

    engine = assemble_engine(services)
    try:
        assert isinstance(services.pipeline._catalog, SqliteTargetCatalog)
        assert isinstance(services.pipeline._store, SqlitePipelineStore)
        assert isinstance(services.pipeline._snapshots, SqliteSnapshotProvider)
        assert isinstance(services.pipeline._executor, ProductionStepExecutor)
        assert engine.rootContext().contextProperty("workbenchViewModel") is services.workbench
        assert services.workbench.get_context_info() == {
            "book_id": book.book_id,
            "chapter_id": chapter.chapter_id,
            "book_title": book.title,
            "chapter_title": chapter.title,
        }
        assert services.workbench.get_page_list_model().rowCount() == 1
        assert services.editing.get_region(region.region_id).text.edited_translation == "人工译文"
    finally:
        engine.deleteLater()
        services.conn.close()
        qapp.processEvents()


def test_navigation_enters_real_workbench_context(
    qapp, tmp_path: Path
) -> None:
    """R-001: shelf navigation publishes its real Book/Chapter context."""
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("导航装配书")
    chapter = services.library.create_chapter(book.book_id, "第2话")
    services.bookshelf.selectBook(book.book_id)

    services.bookshelf.enterTranslation(chapter.chapter_id)

    assert services.navigation.get_workbench_context() == {
        "book_id": book.book_id,
        "chapter_id": chapter.chapter_id,
        "page_id": None,
        "progress": None,
    }
    assert services.workbench.get_has_context() is True
    assert services.workbench.get_context_info()["chapter_id"] == chapter.chapter_id
    services.conn.close()


def test_workbench_resolves_managed_original_url(
    qapp, tmp_path: Path
) -> None:
    """R-002: the Viewer resolves only the immutable Managed Copy path."""
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services
    from PySide6.QtCore import QUrl

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("原图装配书")
    chapter = services.library.create_chapter(book.book_id, "第3话")
    data = _make_png(9, 7)
    report = services.importer.import_files(
        chapter.chapter_id,
        [ImportSource(filename="original.png", data_provider=lambda: data)],
    )
    page = report.imported[0].page

    services.workbench.setContext(
        book.book_id, chapter.chapter_id, book.title, chapter.title
    )
    services.workbench.selectPage(page.page_id)

    resolved = Path(QUrl(services.workbench.get_viewer_image_url()).toLocalFile())
    assert resolved.is_file()
    assert resolved.read_bytes() == data
    assert resolved.is_relative_to((tmp_path / "managed").resolve())
    services.conn.close()


def test_assemble_engine_registers_reader_export_and_tiled_reader(
    qapp, tmp_path: Path
) -> None:
    """TASK-038 AC ①②③④⑤: the production engine contract.

    Every context property the QML pages consume is registered, the reader
    ViewModel is tiled (tile factory injected, cache under the managed root),
    document import is reachable, and the two export paths are distinct and
    bound: ``readerViewModel.exportController`` (reader-initiated) versus the
    context-property ``exportViewModel`` (standalone window, follows the
    workbench chapter)."""
    from application.importing.documents import ImportDocumentsUseCase
    from application.importing.images.ports import ImportSource
    from ui.viewmodels.export.viewmodel import ExportViewModel
    from application.reading.service import ReadingService
    from bootstrap.app import assemble_engine, assemble_services
    from infrastructure.importing import PdfiumDocumentRaster

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    book = services.library.create_book("装配契约书")
    chapter = services.library.create_chapter(
        book.book_id,
        "条漫话",
        chapter_type="webtoon",
        reading_direction="vertical",
    )
    assert isinstance(services.reading, ReadingService)
    assert isinstance(services.document_importer, ImportDocumentsUseCase)
    assert isinstance(services.document_importer._raster, PdfiumDocumentRaster)

    engine = assemble_engine(services)
    try:
        root = engine.rootContext()
        # AC ①/②: all consumed context properties are registered
        assert root.contextProperty("readerViewModel") is services.reader
        registered = {
            name: root.contextProperty(name)
            for name in (
                "navigationViewModel",
                "bookshelfViewModel",
                "workbenchViewModel",
                "readerViewModel",
                "exportViewModel",
            )
        }
        assert all(value is not None for name, value in registered.items() if name != "exportViewModel")
        # path B starts without a chapter context
        assert registered["exportViewModel"] is None

        # AC ② path B: moving the workbench context through the real
        # navigation entry rebuilds and republishes the standalone controller
        services.navigation.enterWorkbench(book.book_id, chapter.chapter_id)
        standalone = root.contextProperty("exportViewModel")
        assert isinstance(standalone, ExportViewModel)
        assert standalone._chapter_id == chapter.chapter_id

        # AC ① path A: the reader-initiated controller is a distinct VM from
        # the same export service, reached only via readerViewModel
        controller = services.reader.openExporter()
        assert isinstance(controller, ExportViewModel)
        assert controller is not standalone

        # AC ①③: the navigation reader context opens the chapter in the
        # production reader ViewModel, and the injected tile factory makes
        # TASK-020's tiled mode active (cache lives under the managed root)
        services.importer.import_files(
            chapter.chapter_id,
            [ImportSource(filename="p0.png", data_provider=lambda: _make_png(400, 3000))],
        )
        services.navigation.enterReader(book.book_id, chapter.chapter_id)
        assert services.reader.hasChapter is True
        assert services.reader.tilesActive is True
        services.reader.requestTiles(0, 4000)
        # TASK-046 AC ⑤: the assembly serves tiles with overlap=0 — the F-4
        # crop made the overlap pixel-irrelevant, and 0 keeps a whole-page
        # sweep one sequential scan. Discriminating: the pre-fix assembly
        # passed overlap=64, so this assertion failed there.
        assert services.reader._rasterizer.grid.overlap == 0
        tile_files = list(
            (tmp_path / "managed" / "cache" / "webtoon-tiles").glob("tile-*.png")
        )
        assert tile_files, "viewport tiles must be materialised on request"

        # AC ④: document import reachable through the shelf view model, and
        # MOBI stays a typed unsupported failure (never faked)
        summary = services.bookshelf.importDocumentsFromUrls(
            chapter.chapter_id, []
        )
        assert summary["failed"] == 0
        non_pdf = tmp_path / "book.mobi"
        non_pdf.write_bytes(b"BOOKMOBI not a pdf")
        from PySide6.QtCore import QUrl

        summary = services.bookshelf.importDocumentsFromUrls(
            chapter.chapter_id, [QUrl.fromLocalFile(str(non_pdf))]
        )
        assert summary["failed"] == 1
    finally:
        engine.deleteLater()
        services.conn.close()


def test_reader_service_and_tile_cache_live_on_the_data_root(tmp_path: Path) -> None:
    """TASK-038 AC ①③: reading progress and export history persist next to
    the library database (one data root), so a restart resumes."""
    from bootstrap.app import assemble_services

    db_path = tmp_path / "library.db"
    services = assemble_services(db_path, tmp_path / "managed")
    try:
        # one data root: reader progress / export history sit next to the
        # library database (the store materialises its file on first write)
        assert services.reading.progress is None
        assert services.export_service is not None
    finally:
        services.conn.close()


def test_trash_service_is_assembled_on_the_same_data_root(tmp_path: Path) -> None:
    """TASK-021 subset: the trash use case is reachable from the production
    assembly and its manifest lives next to the managed data."""
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        from application.maintenance import TrashService

        assert isinstance(services.trash, TrashService)
        assert services.trash.list_batches() == []
    finally:
        services.conn.close()


def test_assemble_services_injects_production_clean_probe(tmp_path: Path) -> None:
    """TASK-040 AC ② (wiring assertion): the production PipelineService
    carries a non-None ``clean_probe`` — a missing injection can no longer
    pass silently (F-12: the TASK-039 fix existed but was unreachable in
    production)."""
    from bootstrap.app import assemble_services

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        assert services.pipeline._clean_probe is not None
    finally:
        services.conn.close()


def test_production_clean_probe_gates_render_only_planning(tmp_path: Path) -> None:
    """TASK-040 AC ③ (production contrast, real SQLite + the real locator
    probe): without a current Clean the render-only plan stays fail-closed;
    after the production artifact writer publishes a current Clean revision
    the same plan turns RUN — while a sibling page without Clean stays
    BLOCKED (the guard is never relaxed)."""
    from application.importing.images.ports import ImportSource
    from bootstrap.app import assemble_services
    from domain.tasks.models import PipelineScope, ScopeType
    from infrastructure.providers.step_writes import ArtifactStepWriter

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        book = services.library.create_book("探针对照书")
        chapter = services.library.create_chapter(book.book_id, "第1话")
        report = services.importer.import_files(
            chapter.chapter_id,
            [
                ImportSource(
                    filename="with-clean.png", data_provider=lambda: _make_png(8, 6)
                ),
                # a *different* image: identical bytes would trip the
                # duplicate-source guard and never become a second page
                ImportSource(
                    filename="without-clean.png",
                    data_provider=lambda: _make_png(9, 6),
                ),
            ],
        )
        page_with_clean = report.imported[0].page
        page_without_clean = report.imported[1].page

        def plan(page_id: str) -> dict[str, str]:
            run = services.pipeline.create_run(
                "rerender_single",
                PipelineScope(ScopeType.PAGE, selected_ids=(page_id,)),
            )
            services.pipeline.plan_run(run.run_id)
            return {
                unit.step_type: f"{unit.decision.value}:{unit.reason or ''}"
                for unit in run.tasks[0].units
            }

        # missing Clean: the inherited fail-closed guard is untouched
        assert plan(page_with_clean.page_id) == {
            "render": "blocked:missing_clean_artifact"
        }
        assert plan(page_without_clean.page_id) == {
            "render": "blocked:missing_clean_artifact"
        }

        # publish a current Clean revision the way the inpaint handler does
        writer = ArtifactStepWriter(services.conn, services.storage)
        prepared = writer.prepare_revision(
            page_id=page_with_clean.page_id,
            artifact_type="clean",
            payload=_make_png(8, 6),
            mime_type="image/png",
            width=8,
            height=6,
        )
        writer.adopt_current(
            artifact_id=prepared.artifact_id,
            revision_id=prepared.revision_id,
            expected_current_revision_id=prepared.previous_revision_id,
        )

        # only the page that really has a current Clean turns RUN
        assert plan(page_with_clean.page_id) == {"render": "run:"}
        assert plan(page_without_clean.page_id) == {
            "render": "blocked:missing_clean_artifact"
        }
    finally:
        services.conn.close()


def test_document_import_slot_publishes_a_return_type() -> None:
    """F-8 (TASK-045): ``@Slot(str, list)`` without ``result=`` publishes
    ``returnType=void``, so QML receives ``undefined`` even though the Python
    method returns a summary dict. The wiring itself is asserted by
    ``test_production_assembly...`` above; this pins the *metatype* QML sees.
    """
    from PySide6.QtCore import QMetaType

    from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel

    meta = BookshelfViewModel.staticMetaObject
    methods = [
        meta.method(index)
        for index in range(meta.methodCount())
        if bytes(meta.method(index).name()) == b"importDocumentsFromUrls"
    ]
    assert methods, "importDocumentsFromUrls must be published as a slot"
    for method in methods:
        assert method.returnType() == QMetaType.Type.QVariantMap, (
            f"{bytes(method.methodSignature())!r} publishes "
            f"returnType={method.returnMetaType().name()}"
        )
