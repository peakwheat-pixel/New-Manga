"""Production entry assembly (TASK-030) — Legacy Qt side of the M2-I1 seam.

The Qt-free Python Core services (SQLite + migrations, Managed Copy,
providers, pipeline, diagnostics, reading/export) are assembled by
:mod:`bootstrap.core_assembly`, which never imports ``PySide6`` or
``src/ui``.  This module keeps the historical entry contract: it builds
the Qt imaging/rendering adapters, injects them into the Core assembly,
layers the QObject viewmodels on top
(:class:`ui.viewmodels...`), and through ``setContextProperty`` injects
them into QML before loading ``Main.qml`` (it only mounts
``shell/AppShell.qml``).

不变量（AC-IMPORT-002/003, D07 §37~39, D05 §60）：
- QML 不接触数据库与文件系统——页面只消费三个 ViewModel 上下文属性；
- 导入始终经 ``ImportImagesUseCase``：Managed Copy 成功后才写 Page，
  源文件只读；Managed Copy 的 Chapter→Book 解析绑定真实仓储查询
  （``book_id_for_chapter``），不硬编码 book id。

数据根默认 ``%LOCALAPPDATA%/New Manga``（``library.db`` + ``managed/``），
可用 ``--data-root`` 或环境变量 ``NEWMANGA_DATA_ROOT`` 覆盖；正式的路径
设置 UI 属 TASK-022。``--smoke-test`` 与 ``--screenshot`` 在临时数据根上
装配完整栈，不触碰真实用户数据。
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from dataclasses import dataclass
import os
from pathlib import Path
import sys
import tempfile

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
# Imported before the engine wraps Main.qml's ApplicationWindow so
# rootObjects()[0] is normally a strongly typed QQuickWindow. The
# _grab_and_quit path below re-wraps the native handle as a second safeguard.
from PySide6.QtQuick import QQuickWindow  # noqa: F401

from application.editing.service import RegionEditingService
from application.export import (
    ExportPage,
    ExportService,
    file_bytes_provider,
)
from application.importing.documents import ImportDocumentsUseCase
from application.importing.images.service import ImportImagesUseCase
from application.library.service import LibraryService
from application.maintenance import TrashService
from application.maintenance.diagnostics import DiagnosticsService
from application.reading.service import ReadingService
from application.rendering.service import RenderService
from application.tasks.service import PipelineService
from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    assemble_core_services,
    default_data_root,
)
# Re-exported for the historical assembly consumers (tests observe these
# seams through ``bootstrap.app``); the implementations live in the
# Qt-free Core assembly now.
from bootstrap.core_assembly import (  # noqa: F401
    CoreServices,
    _ManagedPageCatalog,
    _ManagedPageImageSource,
    _ManagedReaderCatalog,
    _RegionGeometrySource,
    _credential_resolver,
    _credential_store,
    _load_pipeline_defaults,
    _render_content_decoder,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.importing import QtImageDecoder
from infrastructure.rendering.font_catalog import QtFontCatalog
from infrastructure.rendering.pixel_source_style import PixelSourceStyleAnalyzer
from infrastructure.rendering.qt_compositor import QtImageCompositor
from infrastructure.rendering.qt_layout import QtTextLayoutEngine
from infrastructure.sqlite.connection import ThreadRoutedConnection
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.transport.stdlib import StdlibTransport
from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel
from ui.viewmodels.export.viewmodel import ExportViewModel
from ui.viewmodels.navigation.viewmodel import NavigationViewModel
from ui.viewmodels.reader.viewmodel import ReaderViewModel
from ui.viewmodels.settings.viewmodel import SettingsViewModel
from ui.viewmodels.workbench.viewmodel import WorkbenchViewModel

def _resolve_resource_root() -> Path:
    """Return the source or PyInstaller onedir root that contains bundled QML."""
    if getattr(sys, "frozen", False):
        bundle_root = getattr(sys, "_MEIPASS", None)
        if not bundle_root:
            raise RuntimeError("Frozen package is missing PyInstaller resource root")
        return Path(bundle_root).resolve()
    return Path(__file__).resolve().parents[1]


_RESOURCE_ROOT = _resolve_resource_root()
QML_PATH = _RESOURCE_ROOT / "ui" / "qml" / "Main.qml"


@dataclass
class AppServices:
    """Fully wired production stack; QML receives the page viewmodels.

    ``conn`` is the thread-routed SQLite facade exposed so the entry can close
    every per-thread connection before temp-root cleanup — the last writer
    holds the Windows file lock.
    """

    conn: ThreadRoutedConnection
    repository: SqliteLibraryRepository
    storage: ManagedFileStorage
    importer: ImportImagesUseCase
    document_importer: ImportDocumentsUseCase
    trash: TrashService
    reading: ReadingService
    export_service: ExportService
    diagnostics: DiagnosticsService
    reader: ReaderViewModel
    library: LibraryService
    pipeline: PipelineService
    pipeline_defaults: "PipelineDefaultsService"
    editing: RegionEditingService
    render: RenderService
    providers: object
    navigation: NavigationViewModel
    bookshelf: BookshelfViewModel
    workbench: WorkbenchViewModel
    #: Returns the export controller for the *standalone* export window
    #: (TASK-038 AC ② path B); ``None`` when no chapter context is active.
    export_viewmodel: Callable[[], ExportViewModel | None]
    #: Injected by ``assemble_engine`` so a live engine re-publishes the
    #: ``exportViewModel`` context property when the workbench context moves.
    set_export_context_updater: Callable[[Callable], None]
    #: T1.2.1: the settings page controller. ``None`` keeps the page inert
    #: (headless AppServices constructions carry no settings stack).
    settings_vm: "SettingsViewModel | None" = None
    #: T1.2.1 B-003 (R5): the production transport. Exposed so assembly
    #: tests and probes can observe the credential store actually injected
    #: into it; ``None`` on headless constructions that predate the field.
    transport: "StdlibTransport | None" = None


def assemble_services(db_path: str | Path, managed_root: str | Path) -> AppServices:
    """Assemble the full production stack: Qt adapters → Core services →
    QObject viewmodels (M2-I1).

    The Core assembly owns every persistence side effect in its historical
    order (schema check → migrations → managed layout → provider settings →
    ``recover_running_runs`` → diagnostics store → legacy JSON import); this
    Qt layer only constructs the Qt adapter implementations and the
    viewmodels, which are side-effect-free, after the Core stack exists.
    """
    # TASK-033: the Qt-based rendering adapters need a QGuiApplication
    # instance, which the entry creates before calling this; pure headless
    # consumers assemble the Core with their own (Qt-free) adapters.
    font_catalog = QtFontCatalog()
    core = assemble_core_services(
        db_path,
        managed_root,
        image_decoder=QtImageDecoder(),
        font_catalog=font_catalog,
        layout_engine=QtTextLayoutEngine(font_catalog),
        compositor=QtImageCompositor(),
        source_styles=SourceStyleService(PixelSourceStyleAnalyzer()),
    )

    try:
        return _assemble_legacy_qt_layer(core)
    except Exception:
        # P-01 (M2-I1 Review): the historical assemble_services covered its
        # whole body with close-on-error. The Core assembly closes its own
        # span; this restores the remaining span — a failure while building
        # the Qt viewmodels or their signal wiring must not leak the SQLite
        # connection (and its Windows file lock).
        core.conn.close()
        raise


def _assemble_legacy_qt_layer(core: CoreServices) -> AppServices:
    """Build the QObject viewmodels and signal wiring over ``CoreServices``.

    Runs inside :func:`assemble_services`' close-on-error span: any failure
    here closes ``core.conn`` before propagating.
    """
    # --- Legacy Qt / QML assembly: QObject viewmodels over the Core stack ---
    navigation = NavigationViewModel()

    # T1.2.1: the settings page stack — JSON-backed profile stores (the
    # durable ports adapters stay a later coordinated slice; same
    # JSON-interim as progress/export history), the OS credential vault
    # and the settings viewmodel. Secrets go straight to the vault;
    # only credential_ref strings cross the stores (AC-SEC-001~003).
    # The vault is the same best-effort instance the transport and the
    # provider resolver share (B-003): one construction, one fallback.
    from application.settings.network import NetworkProfileService
    from infrastructure.settings.json_profile_stores import (
        JsonNetworkProfileStore,
        JsonProviderProfileStore,
    )

    settings_dir = core.data_root / "settings"
    settings_vm = SettingsViewModel(
        provider_store=JsonProviderProfileStore(settings_dir),
        network_service=NetworkProfileService(
            JsonNetworkProfileStore(settings_dir)
        ),
        credential_store=core.credential_store,
        pipeline_defaults=core.pipeline_defaults,
    )

    reader = ReaderViewModel(
        core.reading,
        core.reader_catalog,
        export_service=core.export_service,
        tile_factory=core.tile_factory,
    )

    def _open_reader_chapter() -> None:
        # AC-NAV-003: entering the reader page carries the chapter the
        # shelf/workbench action selected; without one the reader stays
        # on its empty state.
        context = navigation.get_reader_context()
        chapter_id = context.get("chapter_id")
        if not chapter_id:
            return
        chapter = core.library.get_chapter(chapter_id)
        if chapter is None:
            return
        if not core.page_catalog.list_pages(chapter_id):
            # nothing to read yet: keep the reader's empty state instead
            # of failing the navigation signal handler
            return
        reader.openChapter(
            chapter.book_id,
            chapter.chapter_id,
            chapter.title,
            chapter.chapter_type.value,
            chapter.reading_direction.value,
            True,
        )

    navigation.readerContextChanged.connect(_open_reader_chapter)

    # DIAG-READING-EXPORT-001-FIX-C: the reader heartbeat's production
    # leave-endpoint.  Navigating away from the reader page (any target
    # other than "reader" while a chapter is open) closes the reader —
    # flushing progress and stopping the 5 s heartbeat — so no leaked
    # timer can later fire against a torn-down store (DIAG symptom B's
    # production face).  Entering the reader emits page "reader", which
    # never closes; closeReader is a no-op without an open chapter.
    def _close_reader_when_leaving(page: str) -> None:
        if page != "reader" and reader.hasChapter:
            reader.closeReader()

    navigation.currentPageChanged.connect(_close_reader_when_leaving)

    # TASK-038 AC ② path B: the standalone export window controller
    # follows the workbench chapter context (reader-initiated exports go
    # through ``readerViewModel.exportController`` — path A).
    export_state: dict = {"vm": None, "updater": None}

    def _chapter_export_pages(chapter_id: str) -> list:
        return [
            ExportPage(
                page_id=page.page_id,
                filename=page.filename,
                source_provider=file_bytes_provider(page.original_path),
                translated_provider=(
                    file_bytes_provider(page.translated_path)
                    if page.translated_path
                    else None
                ),
                translated_revision_id=page.translated_revision_id,
                current_translated_revision_id=page.current_translated_revision_id,
                text=page.text,
            )
            for page in core.page_catalog.list_pages(chapter_id)
        ]

    def _rebuild_export_viewmodel(book, chapter) -> None:
        view_model = ExportViewModel(
            core.export_service,
            lambda: _chapter_export_pages(chapter.chapter_id),
            book_id=book.book_id,
            chapter_id=chapter.chapter_id,
            output_dir=str(core.data_root / "exports"),
        )
        export_state["vm"] = view_model
        updater = export_state["updater"]
        if callable(updater):
            updater(view_model)

    bookshelf = BookshelfViewModel(
        library=core.library,
        importer=core.importer,
        document_importer=core.document_importer,
        navigation=navigation,
    )
    workbench = WorkbenchViewModel(
        pipeline=core.pipeline,
        page_catalog=core.page_catalog,
        region_catalog=core.editing,
        translation_editor=core.editing,
        region_creator=core.editing,
        region_deleter=core.editing,
        navigation=navigation,
    )

    def sync_workbench_context() -> None:
        context = navigation.get_workbench_context()
        chapter_id = context.get("chapter_id")
        if not chapter_id:
            workbench.clearContext()
            export_state["vm"] = None
            updater = export_state["updater"]
            if callable(updater):
                updater(None)
            return
        chapter = core.library.get_chapter(chapter_id)
        book = core.library.get_book(chapter.book_id)
        if context.get("book_id") != book.book_id:
            raise ValueError("workbench context book does not own chapter")
        workbench.setContext(
            book.book_id, chapter.chapter_id, book.title, chapter.title
        )
        _rebuild_export_viewmodel(book, chapter)

    navigation.workbenchContextChanged.connect(sync_workbench_context)
    return AppServices(
        conn=core.conn,
        repository=core.repository,
        storage=core.storage,
        importer=core.importer,
        document_importer=core.document_importer,
        trash=core.trash,
        reading=core.reading,
        export_service=core.export_service,
        diagnostics=core.diagnostics,
        reader=reader,
        library=core.library,
        pipeline=core.pipeline,
        pipeline_defaults=core.pipeline_defaults,
        editing=core.editing,
        render=core.render,
        providers=core.providers,
        navigation=navigation,
        bookshelf=bookshelf,
        workbench=workbench,
        export_viewmodel=lambda: export_state["vm"],
        set_export_context_updater=lambda updater: export_state.update(
            updater=updater
        ),
        settings_vm=settings_vm,
        transport=core.transport,
    )


def assemble_engine(services: AppServices) -> QQmlApplicationEngine:
    """Inject the viewmodels as context properties and load Main.qml.

    Registration names and their two export paths (TASK-038 AC ②):

    - ``readerViewModel`` — the reader page's controller. Reader-initiated
      exports go through ``readerViewModel.exportController`` (built lazily
      by the ViewModel from the same ``ExportService``); ReaderView.qml's
      export window consumes exactly that property.
    - ``exportViewModel`` — the *standalone* export window controller for the
      current workbench chapter; rebuilt by the assembly whenever the
      workbench context moves. ``None`` while no chapter is active.
    """
    engine = QQmlApplicationEngine()
    root_context = engine.rootContext()
    root_context.setContextProperty("navigationViewModel", services.navigation)
    root_context.setContextProperty("bookshelfViewModel", services.bookshelf)
    root_context.setContextProperty("workbenchViewModel", services.workbench)
    root_context.setContextProperty("readerViewModel", services.reader)
    root_context.setContextProperty("exportViewModel", services.export_viewmodel())
    root_context.setContextProperty("settingsViewModel", services.settings_vm)
    services.set_export_context_updater(
        lambda view_model: root_context.setContextProperty(
            "exportViewModel", view_model
        )
    )
    engine.load(QUrl.fromLocalFile(str(QML_PATH)))
    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load QML: {QML_PATH}")
    return engine


def _shutdown_services(services: AppServices) -> None:
    """Drain the workbench run thread, then close the connection — only
    if the drain finished.

    TASK-060 Q-003: ``RunController.shutdown``'s wait budget is a wall
    clock, not a completion guarantee — on timeout the worker thread is
    still alive and writing.  Closing the connection under an active
    writer (TASK-048's shared-handle era) or a per-thread writer
    (TASK-060) would truncate the run's final writes, so close() is
    skipped and the abandoned drain is reported on stderr instead of
    failing silently.  WAL is crash-safe: the OS reclaims the handle at
    process exit and the next startup's ``recover_running_runs()`` reaps
    the abandoned run to ``interrupted``.
    """
    drained = services.workbench.shutdown()
    if drained:
        services.conn.close()
    else:
        print(
            "shutdown: workbench drain timed out; connection left open "
            "(worker thread still writing)",
            file=sys.stderr,
        )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bootstrap.app")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="assemble the full stack on a temp data root, then exit 0",
    )
    parser.add_argument(
        "--screenshot",
        metavar="PATH",
        default=None,
        help="start the real shell, save a window grab to PATH and exit",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=1.0,
        help="Qt scale factor applied before the GUI application starts (DPI probe)",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=None,
        help="directory holding library.db and managed/ (default: %%LOCALAPPDATA%%/New Manga)",
    )
    options = parser.parse_args(argv)

    if options.scale != 1.0:
        # Must be set before QGuiApplication exists to affect the DPI policy.
        os.environ["QT_SCALE_FACTOR"] = str(options.scale)

    application = QGuiApplication([sys.argv[0]])

    temp_root: tempfile.TemporaryDirectory[str] | None = None
    services: AppServices | None = None
    try:
        if options.data_root is not None:
            # An explicit data root wins, even in probe modes — callers
            # that named a directory own what gets written there.
            data_root = options.data_root
        elif options.smoke_test or options.screenshot is not None:
            temp_root = tempfile.TemporaryDirectory(prefix="newmanga-probe-")
            data_root = Path(temp_root.name)
        else:
            data_root = default_data_root()
        services = assemble_services(
            data_root / "library.db", data_root / "managed"
        )
        engine = assemble_engine(services)
    except Exception as error:
        if services is not None:
            _shutdown_services(services)
        if temp_root is not None:
            temp_root.cleanup()
        print(f"bootstrap failed: {error}", file=sys.stderr)
        return 1

    window = engine.rootObjects()[0]

    # DIAG-READING-EXPORT-001-FIX-C: quit endpoint — stop the reader
    # heartbeat (flushing progress) via aboutToQuit, while the connection
    # is still alive (exec returns before _shutdown_services closes it).
    application.aboutToQuit.connect(services.reader.closeReader)

    if options.smoke_test:
        QTimer.singleShot(0, application.quit)
        exit_code = application.exec()
    elif options.screenshot:
        window.show()

        def _grab_and_quit() -> None:
            # The created ApplicationWindow can come back typed as a plain
            # QWindow wrapper (no grabWindow); downcast to QQuickWindow and
            # render a frame offscreen — QScreen.grabWindow returns an
            # empty image on headless/virtual displays.
            import shiboken6
            from PySide6.QtQuick import QQuickWindow

            try:
                quick_window = shiboken6.Shiboken.wrapInstance(
                    shiboken6.getCppPointer(window)[0], QQuickWindow
                )
                image = quick_window.grabWindow()
                if image.isNull():
                    raise RuntimeError("window grab produced an empty image")
                if not image.save(options.screenshot):
                    raise RuntimeError(f"could not save {options.screenshot}")
            except Exception:
                import traceback

                traceback.print_exc()
                nonlocal_exit[0] = 1
            application.quit()

        nonlocal_exit = [0]
        QTimer.singleShot(300, _grab_and_quit)
        exit_code = application.exec()
        if nonlocal_exit[0]:
            exit_code = nonlocal_exit[0]
    else:
        exit_code = application.exec()

    # Close SQLite before temp-root cleanup: the connection holds the
    # Windows file lock on library.db.
    _shutdown_services(services)
    if temp_root is not None:
        temp_root.cleanup()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
