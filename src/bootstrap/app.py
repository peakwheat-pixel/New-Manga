"""Production entry assembly (TASK-030).

唯一入口：在真实数据根上打开并迁移 SQLite，构造生产服务栈
（``SqliteLibraryRepository``、``ManagedFileStorage``、``QtImageDecoder``、
``ManagedCopyStoreAdapter``、``ImportImagesUseCase``、``LibraryService``、
导航/书架 ViewModel），通过 ``setContextProperty`` 注入 QML 后加载
``Main.qml``（它只负责挂载 ``shell/AppShell.qml``）。

不变量（AC-IMPORT-002/003, D07 §37~39, D05 §60）：
- QML 不接触数据库与文件系统——页面只消费两个 ViewModel 上下文属性；
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
from collections.abc import Sequence
from dataclasses import dataclass
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

from application.importing.images.service import ImportImagesUseCase
from application.library.service import LibraryService
from infrastructure.filesystem.managed_storage import ManagedFileStorage
from infrastructure.importing import ManagedCopyStoreAdapter, QtImageDecoder
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.library import SqliteLibraryRepository
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.schema import default_migrations
from ui.viewmodels.bookshelf.viewmodel import BookshelfViewModel
from ui.viewmodels.navigation.viewmodel import NavigationViewModel

QML_PATH = Path(__file__).resolve().parents[1] / "ui" / "qml" / "Main.qml"


@dataclass
class AppServices:
    """Fully wired production stack; QML receives only the two viewmodels.

    ``conn`` is exposed so the entry can close the SQLite connection before
    temp-root cleanup — the last writer holds the Windows file lock.
    """

    conn: sqlite3.Connection
    repository: SqliteLibraryRepository
    storage: ManagedFileStorage
    importer: ImportImagesUseCase
    library: LibraryService
    navigation: NavigationViewModel
    bookshelf: BookshelfViewModel


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
        navigation = NavigationViewModel()
        bookshelf = BookshelfViewModel(
            library=library, importer=importer, navigation=navigation
        )
        return AppServices(
            conn=conn,
            repository=repository,
            storage=storage,
            importer=importer,
            library=library,
            navigation=navigation,
            bookshelf=bookshelf,
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
