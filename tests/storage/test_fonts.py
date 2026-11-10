"""FEA-14-FONT-1: schema v11 font assets (import/list/delete/refresh)."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3
import sys

import pytest

THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.fonts.service import FontLibraryError, FontLibraryService  # noqa: E402
from infrastructure.sqlite.fonts import SqliteFontAssetStore  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

MIGRATIONS = default_migrations()
LATEST = MIGRATIONS[-1].schema_version


def _connect(tmp_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(tmp_path / "library.db")


def _migrate(conn: sqlite3.Connection) -> None:
    MigrationRunner(conn, MIGRATIONS).apply_pending()


def _font_file(tmp_path: Path, name: str = "MyFont-Regular.ttf") -> Path:
    path = tmp_path / name
    path.write_bytes(b"\x00\x01\x00\x00" + b"FONT" * 8)
    return path


def _service(tmp_path: Path):
    conn = _connect(tmp_path)
    _migrate(conn)
    data_root = tmp_path / "data"
    return conn, FontLibraryService(SqliteFontAssetStore(conn), data_root)


def test_v11_creates_font_assets_table(tmp_path):
    conn = _connect(tmp_path)
    _migrate(conn)
    assert read_schema_version(conn) == LATEST == 11
    tables = {row[0] for row in conn.execute("select name from sqlite_master where type='table'")}
    assert "font_assets" in tables


def test_import_copies_to_managed_root_and_is_idempotent(tmp_path):
    conn, service = _service(tmp_path)
    source = _font_file(tmp_path)
    asset = service.import_asset(str(source), "open-font-license")
    assert asset["state"] == "active"
    assert asset["format"] == "ttf"
    assert asset["family"] == "MyFont"
    assert asset["license_note"] == "open-font-license"
    managed = service.fonts_root / asset["managed_path"]
    assert managed.is_file()
    assert asset["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()

    again = service.import_asset(str(source))
    assert again["asset_id"] == asset["asset_id"]
    assert len(service.list_assets()) == 1


def test_import_rejects_invalid_sources(tmp_path):
    conn, service = _service(tmp_path)
    with pytest.raises(FontLibraryError) as caught:
        service.import_asset(str(tmp_path / "missing.ttf"))
    assert caught.value.code == "FONT_SOURCE_INVALID"

    bad = tmp_path / "bad.png"
    bad.write_bytes(b"\x89PNG\r\n\x1a\n")
    with pytest.raises(FontLibraryError) as caught:
        service.import_asset(str(bad))
    assert caught.value.code == "FONT_FORMAT_UNSUPPORTED"


def test_delete_is_soft_and_keeps_source_file(tmp_path):
    conn, service = _service(tmp_path)
    source = _font_file(tmp_path)
    asset = service.import_asset(str(source))
    assert service.delete_asset(asset["asset_id"]) is True
    assert service.delete_asset(asset["asset_id"]) is False
    assert source.is_file(), "the user's source font file must never be deleted"
    listed = {item["asset_id"]: item for item in service.list_assets()}
    assert listed[asset["asset_id"]]["state"] == "deleted"


def test_refresh_reports_available_and_missing(tmp_path):
    conn, service = _service(tmp_path)
    asset = service.import_asset(str(_font_file(tmp_path)))
    report = service.refresh_assets()
    assert report["available"] >= 1
    assert report["failed"] == []

    (service.fonts_root / asset["managed_path"]).unlink()
    report = service.refresh_assets()
    assert {"path": asset["managed_path"], "code": "FONT_FILE_MISSING"} in report["failed"]
