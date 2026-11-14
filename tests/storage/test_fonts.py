"""FEA-14-FONT-1: schema v11 font assets (import/list/delete/refresh)."""

from __future__ import annotations

import hashlib
from pathlib import Path
import sqlite3
import sys
import threading

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
    assert read_schema_version(conn) == LATEST == 14
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


# MAINT-2-C1-BATCH-1 AC3 (C1-3 / L-F1-3): byte-limit boundary. The limit itself is
# patched down so the boundary is exercised exactly (== limit accepted, +1 rejected)
# without writing 50 MB; a separate case proves the PRODUCTION constant is wired.
def test_import_byte_limit_boundary_accepts_exact_and_rejects_beyond(tmp_path, monkeypatch):
    import application.fonts.service as fonts_service
    monkeypatch.setattr(fonts_service, "MAX_FONT_BYTES", 4_096)
    conn, service = _service(tmp_path)

    exact = tmp_path / "Exact-Regular.ttf"
    exact.write_bytes(b"\x00\x01\x00\x00" + b"A" * (4_096 - 4))
    accepted = service.import_asset(str(exact))
    assert accepted["size_bytes"] == 4_096

    too_big = tmp_path / "Big-Regular.ttf"
    too_big.write_bytes(b"\x00\x01\x00\x00" + b"B" * 4_096)
    with pytest.raises(FontLibraryError) as caught:
        service.import_asset(str(too_big))
    assert caught.value.code == "FONT_SOURCE_INVALID"

    empty = tmp_path / "Empty-Regular.ttf"
    empty.write_bytes(b"")
    with pytest.raises(FontLibraryError) as caught_empty:
        service.import_asset(str(empty))
    assert caught_empty.value.code == "FONT_SOURCE_INVALID"

    # Rejected imports must not leave managed copies or rows behind.
    assert [asset["asset_id"] for asset in service.list_assets()] == [accepted["asset_id"]]
    assert sorted(path.name for path in service.fonts_root.iterdir()) == [accepted["managed_path"]]


def test_import_rejects_a_real_oversized_file(tmp_path):
    from application.fonts.service import MAX_FONT_BYTES
    # Sparse file: one byte past the production limit, so the size gate must reject it
    # BEFORE hashing/copying (no 50 MB write, no sha256 of 50 MB).
    sparse = tmp_path / "Huge-Regular.ttf"
    with sparse.open("wb") as handle:
        handle.seek(MAX_FONT_BYTES)
        handle.write(b"\x00")
    assert sparse.stat().st_size == MAX_FONT_BYTES + 1

    conn, service = _service(tmp_path)
    with pytest.raises(FontLibraryError) as caught:
        service.import_asset(str(sparse))
    assert caught.value.code == "FONT_SOURCE_INVALID"
    assert service.list_assets() == []
    assert not service.fonts_root.exists() or list(service.fonts_root.iterdir()) == []




# MAINT-2-C1-BATCH-1 AC3 (C1-3 / L-F1-3): concurrent-import boundary, made DETERMINISTIC.
# A plain thread race on SQLite is slow and flaky (it measures sqlite's locking, not our code),
# so the interleaving is forced: both clients pass the content lookup BEFORE either inserts,
# which is exactly the window where a duplicate row could be created. Invariant under test:
# the same bytes can never become two rows (v11 `idx_font_assets_sha` is UNIQUE), and the loser
# must fail with a DB-level error rather than silently double-inserting.
def _open_client(tmp_path: Path):
    # Each logical client owns its own connection. check_same_thread=False only because this test
    # hands the fixed client to one worker thread (production never shares a connection).
    conn = sqlite3.connect(tmp_path / "library.db", timeout=5.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn, FontLibraryService(SqliteFontAssetStore(conn), tmp_path / "data")


def test_interleaved_same_content_imports_cannot_duplicate_a_row(tmp_path, monkeypatch):
    setup = sqlite3.connect(tmp_path / "library.db")
    _migrate(setup)
    # The invariant below is enforced by this v11 index; if it ever disappears the race test
    # would go red (two rows for the same bytes) instead of silently passing.
    index = setup.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_font_assets_sha'"
    ).fetchone()
    assert index is not None, "v11 unique sha index is missing; dedupe is no longer enforced"
    setup.close()

    source = _font_file(tmp_path, "Shared-Regular.ttf")
    clients = [_open_client(tmp_path), _open_client(tmp_path)]
    barrier = threading.Barrier(2, timeout=10)
    original_find = SqliteFontAssetStore.find_by_sha
    gate = {"calls": 0}
    gate_lock = threading.Lock()

    def gated_find(store, digest):
        found = original_find(store, digest)
        with gate_lock:
            gate["calls"] += 1
            wait_here = gate["calls"] <= 2
        if wait_here:
            barrier.wait()  # both clients have seen "absent"; the insert race is now required
        return found

    monkeypatch.setattr(SqliteFontAssetStore, "find_by_sha", gated_find)

    results: list[str] = []
    failures: list[Exception] = []
    results_lock = threading.Lock()

    def import_once(service: FontLibraryService) -> None:
        try:
            asset_id = service.import_asset(str(source))["asset_id"]
            with results_lock:
                results.append(asset_id)
        except Exception as error:  # noqa: BLE001 - the losing insert is expected to fail
            with results_lock:
                failures.append(error)

    threads = [threading.Thread(target=import_once, args=(service,)) for _, service in clients]
    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    finally:
        for conn, _ in clients:
            conn.close()

    assert results, f"both interleaved imports failed: {failures}"
    assert len(set(results)) == 1, results
    assert len(results) + len(failures) == 2, (results, failures)
    for failure in failures:
        assert isinstance(failure, sqlite3.Error), failure

    reader = sqlite3.connect(tmp_path / "library.db")
    try:
        rows = reader.execute(
            "SELECT asset_id FROM font_assets WHERE state != 'deleted'"
        ).fetchall()
    finally:
        reader.close()
    assert [row[0] for row in rows] == [results[0]], rows
