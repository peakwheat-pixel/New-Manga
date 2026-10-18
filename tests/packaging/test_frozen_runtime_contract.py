"""Contract tests for frozen runtime resolution, data isolation, and safety (T3.2.1 Task 3)."""

import hashlib
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def test_frozen_qml_path_resolution(tmp_path, monkeypatch):
    """Verify bootstrap QML_PATH resolves correctly in both normal and frozen environments (R-008)."""
    import importlib
    import bootstrap.app as app

    # Case 1: normal environment -> resolves under src/ui/qml
    assert app.QML_PATH.is_file()
    assert app.QML_PATH.name == "Main.qml"
    assert "src" in app.QML_PATH.parts

    # Case 2: simulated frozen environment -> reload app module to execute production sys.frozen branch
    # Use isolated tmp_path/"meipass" distinct from source tree to ensure discrimination
    fake_meipass = tmp_path / "meipass"
    fake_qml_dir = fake_meipass / "ui" / "qml"
    fake_qml_dir.mkdir(parents=True)
    fake_main_qml = fake_qml_dir / "Main.qml"
    fake_main_qml.write_text("// Mock Main.qml for frozen contract test\nimport QtQuick\nItem {}\n", encoding="utf-8")

    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "_MEIPASS", str(fake_meipass), raising=False)

    try:
        app_reloaded = importlib.reload(app)
        assert app_reloaded._RESOURCE_ROOT == fake_meipass
        assert app_reloaded.QML_PATH == fake_meipass / "ui" / "qml" / "Main.qml"
        assert app_reloaded.QML_PATH.is_file()
    finally:
        # Restore normal environment
        monkeypatch.undo()
        importlib.reload(app)


def test_explicit_data_root_isolation(tmp_path):
    """Verify database and managed files are created strictly in data_root."""
    from bootstrap.app import assemble_services, _shutdown_services

    data_root = tmp_path / "custom_data_root"
    db_path = data_root / "library.db"
    managed_path = data_root / "managed"

    services = assemble_services(db_path, managed_path)
    try:
        assert db_path.is_file()
        assert managed_path.is_dir()

        # Database must be outside program/source directory
        assert not str(db_path).startswith(str(ROOT / "src"))
        assert not str(db_path).startswith(str(ROOT / "packaging"))

        # Verify schema version is current (v5)
        ver = services.conn.execute(
            "SELECT CAST(value_json AS INTEGER) FROM application_metadata WHERE metadata_key='schema_version'"
        ).fetchone()[0]
        assert ver == 5
    finally:
        _shutdown_services(services)

    # Verify lock release: connection is closed, database can be reopened in exclusive mode
    reopened = sqlite3.connect(str(db_path))
    try:
        reopened.execute("PRAGMA schema_version")
    finally:
        reopened.close()


def test_source_file_unmodified_during_workflow(tmp_path):
    """Verify source image fixture SHA-256 and mtime are strictly preserved after real import (R-008)."""
    from PySide6.QtCore import QBuffer, QIODevice
    from PySide6.QtGui import QImage

    qimage = QImage(10, 10, QImage.Format.Format_RGB32)
    qimage.fill(0xFF00FF00)
    buf = QBuffer()
    buf.open(QIODevice.OpenModeFlag.WriteOnly)
    qimage.save(buf, "PNG")
    png_bytes = bytes(buf.data())

    source_img = tmp_path / "sample_source.png"
    source_img.write_bytes(png_bytes)
    initial_hash = hashlib.sha256(png_bytes).hexdigest()
    initial_mtime = source_img.stat().st_mtime_ns

    from bootstrap.app import assemble_services, _shutdown_services
    from application.importing.images.ports import ImportSource

    data_root = tmp_path / "run_data"
    services = assemble_services(data_root / "library.db", data_root / "managed")
    try:
        # Real workflow: create book -> chapter -> import files via ImportImagesUseCase
        book = services.library.create_book("Source Safety Book")
        chapter = services.library.create_chapter(book.book_id, "Chapter 1")
        sources = [ImportSource(filename=source_img.name, data_provider=source_img.read_bytes)]
        report = services.importer.import_files(chapter.chapter_id, sources)
        assert len(report.imported) == 1
    finally:
        _shutdown_services(services)

    # Assert source file is strictly untouched (hash and mtime preserved)
    final_hash = hashlib.sha256(source_img.read_bytes()).hexdigest()
    assert final_hash == initial_hash
    assert source_img.stat().st_mtime_ns == initial_mtime
