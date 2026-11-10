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
    assert read_schema_version(conn) == LATEST >= 11
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

    # R1-001: renaming arbitrary bytes to .ttf must NOT pass the magic check.
    disguised = tmp_path / "disguised.ttf"
    disguised.write_bytes(b"NOT-A-FONT-PAYLOAD")
    with pytest.raises(FontLibraryError) as caught:
        service.import_asset(str(disguised))
    assert caught.value.code == "FONT_FORMAT_UNSUPPORTED"


def test_delete_removes_managed_copy_and_keeps_source_file(tmp_path):
    conn, service = _service(tmp_path)
    source = _font_file(tmp_path)
    asset = service.import_asset(str(source))
    managed = service.fonts_root / asset["managed_path"]
    assert managed.is_file()
    assert service.delete_asset(asset["asset_id"]) is True
    assert source.is_file(), "the user's source font file must never be deleted"
    assert not managed.exists(), "the managed copy is library data and is removed"
    listed = {item["asset_id"]: item for item in service.list_assets()}
    assert asset["asset_id"] not in listed, "deleted assets are not listed"
    with pytest.raises(FontLibraryError) as caught:
        service.delete_asset(asset["asset_id"])
    assert caught.value.code == "FONT_NOT_FOUND"


def test_refresh_reports_available_and_missing(tmp_path):
    conn, service = _service(tmp_path)
    asset = service.import_asset(str(_font_file(tmp_path)))
    report = service.refresh_assets()
    assert report["available"] >= 1
    assert report["failed"] == []

    (service.fonts_root / asset["managed_path"]).unlink()
    report = service.refresh_assets()
    assert {"path": asset["managed_path"], "code": "FONT_FILE_MISSING"} in report["failed"]


def test_delete_reports_typed_failure_when_managed_copy_is_stuck(tmp_path):
    conn, service = _service(tmp_path)
    asset = service.import_asset(str(_font_file(tmp_path)))
    managed = service.fonts_root / asset["managed_path"]
    # R2-002: a read-only managed copy cannot be removed on Windows.
    managed.chmod(0o444)
    try:
        with pytest.raises(FontLibraryError) as caught:
            service.delete_asset(asset["asset_id"])
        assert caught.value.code == "FONT_DELETE_FAILED"
        # R3-001: the row stays active so the delete can be retried.
        assert service.list_assets() and service.list_assets()[0]["asset_id"] == asset["asset_id"]
    finally:
        try:
            managed.chmod(0o666)
        except OSError:
            pass
    assert service.delete_asset(asset["asset_id"]) is True
    assert service.list_assets() == []
