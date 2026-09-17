"""Production entry assembly (TASK-030).

唯一入口：在真实数据根上打开并迁移 SQLite，构造生产服务栈
（``SqliteLibraryRepository``、``ManagedFileStorage``、``QtImageDecoder``、
  ``ManagedCopyStoreAdapter``、``ImportImagesUseCase``、``LibraryService``、
  生产 Pipeline、Region 编辑和导航/书架/工作台 ViewModel），通过
  ``setContextProperty`` 注入 QML 后加载
``Main.qml``（它只负责挂载 ``shell/AppShell.qml``）。

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
import json
import os
from pathlib import Path
import sqlite3
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
from application.importing.images.service import ImportImagesUseCase
from application.library.service import LibraryService
from application.tasks.service import PipelineService
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.importing import ManagedCopyStoreAdapter, QtImageDecoder
from infrastructure.pipeline.assembly import build_production_pipeline
from infrastructure.providers.handlers import (
    RegionMaskGeometry,
    build_production_handlers,
)
from infrastructure.providers.runtime import build_provider_runtime
from infrastructure.providers.step_writes import ArtifactStepWriter, RegionStepWriter
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations
from infrastructure.transport.stdlib import StdlibTransport
from ports.inpaint.ports import ImageFrame
from ports.providers.errors import ProviderInputError
from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel
from ui.viewmodels.navigation.viewmodel import NavigationViewModel
from ui.viewmodels.workbench.viewmodel import WorkbenchViewModel

QML_PATH = Path(__file__).resolve().parents[1] / "ui" / "qml" / "Main.qml"


class _ManagedPageCatalog:
    """Expose SQLite pages and immutable Managed Copy URLs to the Viewer."""

    def __init__(self, repository: SqliteLibraryRepository, storage: ManagedFileStorage) -> None:
        self._repository = repository
        self._storage = storage

    def list_pages(self, chapter_id: str):
        return self._repository.list_pages(chapter_id)

    def image_url(self, page_id: str, mode: str) -> str:
        if mode != "original":
            return ""
        page = self._repository.get_page(page_id)
        if page is None or not page.managed_original_ref:
            return ""
        root = self._storage.root.resolve()
        path = Path(self._storage.absolute_path(page.managed_original_ref)).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return ""
        return path.as_uri() if path.is_file() else ""


class _ManagedPageImageSource:
    """Pixel access for provider steps (D06 §6/§7 input, D07 §37).

    Only the immutable Managed Copy is read; a missing or undecodable file is a
    typed provider-input failure, never an empty image.
    """

    def __init__(
        self,
        repository: SqliteLibraryRepository,
        storage: ManagedFileStorage,
        regions: SqliteRegionRepository,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._regions = regions

    def _page_image(self, page_id: str):
        from PySide6.QtGui import QImage

        page = self._repository.get_page(page_id)
        if page is None or not page.managed_original_ref:
            raise ProviderInputError(
                f"page {page_id!r} has no managed original", stage="image-source"
            )
        root = self._storage.root.resolve()
        path = Path(self._storage.absolute_path(page.managed_original_ref)).resolve()
        try:
            path.relative_to(root)
        except ValueError as error:
            raise ProviderInputError(
                f"managed original for {page_id!r} escapes the data root",
                stage="image-source",
            ) from error
        if not path.is_file():
            raise ProviderInputError(
                f"managed original is missing: {path}", stage="image-source"
            )
        image = QImage(str(path))
        if image.isNull():
            raise ProviderInputError(
                f"managed original is not decodable: {path}", stage="image-source"
            )
        return image

    def page_frame(self, page_id: str) -> ImageFrame:
        from PySide6.QtGui import QImage

        image = self._page_image(page_id).convertToFormat(QImage.Format.Format_RGB32)
        width, height = image.width(), image.height()
        return ImageFrame(width, height, "rgb32", bytes(image.constBits()))

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        from PySide6.QtCore import QBuffer, QIODevice, QRect
        from PySide6.QtGui import QImage

        page = self._repository.get_page(page_id)
        if page is None:
            raise ProviderInputError(
                f"page {page_id!r} is not available", stage="image-source"
            )
        region = self._regions.get_region(region_id)
        if region is None:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage="image-source"
            )
        image = self._page_image(page_id)
        bbox = region.geometry.bbox
        rect = QRect(bbox.x, bbox.y, bbox.width, bbox.height).intersected(
            QRect(0, 0, image.width(), image.height())
        )
        if rect.isEmpty():
            raise ProviderInputError(
                f"region {region_id!r} lies outside the page", stage="image-source"
            )
        crop = image.copy(rect).convertToFormat(QImage.Format.Format_RGB888)
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not crop.save(buffer, "PNG"):
            raise ProviderInputError(
                "region crop could not be encoded", stage="image-source"
            )
        return bytes(buffer.data()), crop.width(), crop.height()


class _RegionGeometrySource:
    """Region geometry as mask primitives (D06 §19 Segment input)."""

    def __init__(self, regions: SqliteRegionRepository) -> None:
        self._regions = regions

    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        region = self._regions.get_region(region_id)
        if region is None or region.deleted:
            raise ProviderInputError(
                f"region {region_id!r} is not available", stage="segment"
            )
        bbox = region.geometry.bbox
        boxes = ((bbox.x, bbox.y, bbox.x + bbox.width, bbox.y + bbox.height),)
        return RegionMaskGeometry(boxes=boxes, polygons=(region.geometry.polygon,) if region.geometry.polygon else ())


def _load_pipeline_settings(conn: sqlite3.Connection) -> dict:
    """Read the persisted pipeline defaults (empty when never configured)."""
    try:
        row = conn.execute(
            "SELECT settings_json FROM pipeline_defaults WHERE defaults_id = 1"
        ).fetchone()
    except sqlite3.Error:
        return {}
    if row is None or not row[0]:
        return {}
    try:
        loaded = json.loads(row[0])
    except (ValueError, TypeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _credential_resolver() -> Callable[[str], str | None] | None:
    """Resolve provider credentials from the Windows vault, best effort.

    A vault that cannot be opened must not stop the app from starting
    (AC-OPTIONAL-001); the providers that need a credential then report
    Not-Ready with ``MISSING_CREDENTIAL`` instead.
    """
    try:
        from infrastructure.credentials.windows import WindowsCredentialStore

        store = WindowsCredentialStore()
    except Exception:
        return None

    def resolve(ref: str) -> str | None:
        try:
            return store.resolve_credential(ref).reveal()
        except Exception:
            return None

    return resolve


@dataclass
class AppServices:
    """Fully wired production stack; QML receives the page viewmodels.

    ``conn`` is exposed so the entry can close the SQLite connection before
    temp-root cleanup — the last writer holds the Windows file lock.
    """

    conn: sqlite3.Connection
    repository: SqliteLibraryRepository
    storage: ManagedFileStorage
    importer: ImportImagesUseCase
    library: LibraryService
    pipeline: PipelineService
    editing: RegionEditingService
    providers: object
    navigation: NavigationViewModel
    bookshelf: BookshelfViewModel
    workbench: WorkbenchViewModel


def default_data_root() -> Path:
    root = os.environ.get("NEWMANGA_DATA_ROOT")
    if root:
        return Path(root)
    local_app_data = os.environ.get("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home()
    return base / "New Manga"


def assemble_services(db_path: str | Path, managed_root: str | Path) -> AppServices:
    """Open + migrate the SQLite library and build every production service.

    Refuses to run against a database written by a newer schema (AC-DB-005):
    ``open_database`` reopens it ``query_only`` and this assembly fails fast
    instead of blind-writing.
    """
    migrations = default_migrations()
    latest_known = max(migration.schema_version for migration in migrations)
    conn, opened = open_database(db_path, latest_known_schema_version=latest_known)
    try:
        if not opened.writable:
            raise RuntimeError(
                f"database schema v{opened.schema_version} is newer than this "
                f"application knows (v{latest_known}); refusing to run"
            )
        MigrationRunner(conn, migrations).apply_pending()

        repository = SqliteLibraryRepository(conn)
        storage = ManagedFileStorage(managed_root)
        storage.ensure_layout()
        library = LibraryService(repository)
        regions = SqliteRegionRepository(conn)

        def book_id_for_chapter(chapter_id: str) -> str:
            # Real Chapter→Book lookup for the D03 §18 managed layout; an
            # unknown chapter fails the copy, so no page can be written.
            chapter = repository.get_chapter(chapter_id)
            if chapter is None:
                raise ValueError(f"unknown chapter: {chapter_id!r}")
            return chapter.book_id

        importer = ImportImagesUseCase(
            QtImageDecoder(),
            ManagedCopyStoreAdapter(storage, book_id_for_chapter),
            repository,
        )
        # TASK-019: the production Pipeline receives real handlers built from
        # the provider runtime. Nothing is wired when no provider is ready:
        # the step then fails with PROVIDER_UNAVAILABLE / Not-Ready instead of
        # inventing a deterministic placeholder.
        provider_runtime = build_provider_runtime(
            settings=_load_pipeline_settings(conn),
            transport=StdlibTransport(),
            credential_resolver=_credential_resolver(),
        )
        handlers = build_production_handlers(
            registry=provider_runtime.registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=_ManagedPageImageSource(repository, storage, regions),
            geometry=_RegionGeometrySource(regions),
            retry_policy=provider_runtime.retry_policy,
            heavy_runner=provider_runtime.heavy_runner,
            route_policy=provider_runtime.route_policy,
        )
        pipeline = build_production_pipeline(conn, handlers=handlers)
        editing = RegionEditingService(regions)
        navigation = NavigationViewModel()
        bookshelf = BookshelfViewModel(
            library=library, importer=importer, navigation=navigation
        )
        workbench = WorkbenchViewModel(
            pipeline=pipeline,
            page_catalog=_ManagedPageCatalog(repository, storage),
            region_catalog=editing,
            translation_editor=editing,
            navigation=navigation,
        )

        def sync_workbench_context() -> None:
            context = navigation.get_workbench_context()
            chapter_id = context.get("chapter_id")
            if not chapter_id:
                workbench.clearContext()
                return
            chapter = library.get_chapter(chapter_id)
            book = library.get_book(chapter.book_id)
            if context.get("book_id") != book.book_id:
                raise ValueError("workbench context book does not own chapter")
            workbench.setContext(
                book.book_id, chapter.chapter_id, book.title, chapter.title
            )

        navigation.workbenchContextChanged.connect(sync_workbench_context)
        return AppServices(
            conn=conn,
            repository=repository,
            storage=storage,
            importer=importer,
            library=library,
            pipeline=pipeline,
            editing=editing,
            providers=provider_runtime,
            navigation=navigation,
            bookshelf=bookshelf,
            workbench=workbench,
        )
    except Exception:
        conn.close()
        raise


def assemble_engine(services: AppServices) -> QQmlApplicationEngine:
    """Inject the viewmodels as context properties and load Main.qml."""
    engine = QQmlApplicationEngine()
    root_context = engine.rootContext()
    root_context.setContextProperty("navigationViewModel", services.navigation)
    root_context.setContextProperty("bookshelfViewModel", services.bookshelf)
    root_context.setContextProperty("workbenchViewModel", services.workbench)
    engine.load(QUrl.fromLocalFile(str(QML_PATH)))
    if not engine.rootObjects():
        raise RuntimeError(f"Failed to load QML: {QML_PATH}")
    return engine


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
            services.conn.close()
        if temp_root is not None:
            temp_root.cleanup()
        print(f"bootstrap failed: {error}", file=sys.stderr)
        return 1

    window = engine.rootObjects()[0]

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
    services.conn.close()
    if temp_root is not None:
        temp_root.cleanup()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
