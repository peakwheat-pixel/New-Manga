"""REALUSE-DATA-SAFETY-1 AC2: automatic ``.nmbak`` coverage before it is needed.

Before this change the production assembly passed no backup provider to
``MigrationRunner`` and the Host-side first-run backup only copied the derived
catalog, so an existing user library (``library.db`` + 100 MB managed copies)
had no rollback point at all. These tests pin the two automatic paths:

- a verified ``pre_migration`` package before pending DDL on a library that
  already has schema history (a brand-new root must not litter ``backups/``);
- a verified ``automatic`` package on the first writable start of a library
  that already contains books, idempotent afterwards.
"""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_assembly import _NmbakMigrationBackup  # noqa: E402
from bootstrap.core_service import (  # noqa: E402
    _ensure_automatic_backup,
    assemble_production_core,
)
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

NOW = "2026-10-30T00:00:00+00:00"


def _migrations():
    return default_migrations()


def _latest_version() -> int:
    return max(migration.schema_version for migration in _migrations())


def _open(data_root: Path):
    db_path = data_root / "library.db"
    data_root.mkdir(parents=True, exist_ok=True)
    return open_database(db_path, latest_known_schema_version=_latest_version())


def _provider(conn, data_root: Path) -> _NmbakMigrationBackup:
    return _NmbakMigrationBackup(
        conn, data_root / "backups", data_root / "managed", app_version="test"
    )


def _manifest(package: Path) -> dict:
    with zipfile.ZipFile(package) as archive:
        return json.loads(archive.read("manifest.json"))


def test_pre_migration_backup_is_created_before_pending_ddl(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    conn, _opened = _open(data_root)
    migrations = _migrations()
    try:
        MigrationRunner(conn, migrations[:1]).apply_pending()  # bind only v1
        backups = data_root / "backups"
        assert not list(backups.glob("*.nmbak")) if backups.exists() else True

        applied = MigrationRunner(
            conn, migrations, backup_provider=_provider(conn, data_root)
        ).apply_pending()

        packages = sorted(backups.glob("*.nmbak"))
        assert applied, "expected pending migrations after the v1 bootstrap"
        assert len(packages) == len(applied)
        manifest = _manifest(packages[0])
        assert manifest["backup_type"] == "pre_migration"
        assert manifest["verified"] is True
        assert manifest["source_reason"].startswith("before schema_version=")
        with zipfile.ZipFile(packages[0]) as archive:
            assert "library.db" in archive.namelist()
            assert "manifest.json" in archive.namelist()
    finally:
        conn.close()


def test_fresh_library_gets_no_pre_migration_backup(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    conn, _opened = _open(data_root)
    try:
        applied = MigrationRunner(
            conn, _migrations(), backup_provider=_provider(conn, data_root)
        ).apply_pending()
        assert applied, "a fresh root must still be migrated"
        assert not list((data_root / "backups").glob("*.nmbak"))
    finally:
        conn.close()


def test_first_run_backup_covers_existing_library_and_is_idempotent(tmp_path: Path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        backups = Path(core.data_root) / "backups"
        assert not list(backups.glob("*.nmbak"))

        with core.conn as conn:
            conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b1', '家族战记', ?, ?)",
                (NOW, NOW),
            )

        _ensure_automatic_backup(core)
        packages = sorted(backups.glob("*.nmbak"))
        assert len(packages) == 1
        manifest = _manifest(packages[0])
        assert manifest["backup_type"] == "automatic"
        assert manifest["verified"] is True
        with zipfile.ZipFile(packages[0]) as archive:
            assert "library.db" in archive.namelist()

        # A verified package already covers the root: no second package.
        _ensure_automatic_backup(core)
        assert len(list(backups.glob("*.nmbak"))) == 1
    finally:
        core.conn.close()


def test_empty_library_gets_no_first_run_backup(tmp_path: Path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        _ensure_automatic_backup(core)
        assert not list((Path(core.data_root) / "backups").glob("*.nmbak"))
    finally:
        core.conn.close()


def test_automatic_backups_are_pruned_but_manual_ones_are_kept(tmp_path: Path) -> None:
    core = assemble_production_core(tmp_path / "data")
    try:
        backups = Path(core.data_root) / "backups"
        service = core.backup
        with core.conn as conn:
            conn.execute(
                "INSERT INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('b1', 'x', ?, ?)",
                (NOW, NOW),
            )

        manual = service.create("manual", "user made this")
        created = [service.create("automatic", f"auto {index}")["backup_id"] for index in range(7)]
        assert len(created) == 7

        from bootstrap.core_service import _AUTOMATIC_BACKUP_KEEP

        _ensure_automatic_backup(core)

        remaining = {item["backup_id"] for item in service.list_backups()}
        assert manual["backup_id"] in remaining, "manual packages are never pruned"
        automatic_left = [
            item for item in service.list_backups()
            if item.get("backup_type") == "automatic"
        ]
        assert len(automatic_left) <= _AUTOMATIC_BACKUP_KEEP
        assert len(list(backups.glob("*.nmbak"))) >= len(automatic_left)
    finally:
        core.conn.close()
