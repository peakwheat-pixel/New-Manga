"""Bootstrap assembly tests (TASK-030).

The subprocess smoke runs on the default Windows Qt platform: the task
forbids forcing ``QT_QPA_PLATFORM=offscreen`` for the entry evidence, and
the real AppShell needs the font database anyway. The in-process tests
exercise the real assembly (SQLite + migrations + Qt decoder + managed
copy) against temp roots only — the user data root is never touched.
"""

from __future__ import annotations

import hashlib
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
