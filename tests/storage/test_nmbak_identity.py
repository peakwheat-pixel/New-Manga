"""FEA-13-ID-3: DatabaseId primitive + manifest/list identity + restore gate.

C-01b SC-18 semantics: one UUID4 in ``application_metadata``, atomic and
idempotent; a legacy library reads as unknown until the back-fill; a package
from a *different known* database is rejected before anything is touched, while
an unknown identity never blocks a restore.
"""

from __future__ import annotations

import hashlib
import sys
import uuid
import zipfile
import json
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.identity import (  # noqa: E402
    DATABASE_ID_KEY,
    ensure_database_id,
    read_database_id,
)
from infrastructure.sqlite.nmbak import (  # noqa: E402
    MANIFEST_NAME,
    NmbakBackupError,
    NmbakBackupService,
)

NOW = "2026-11-09T14:00:00+00:00"


def _open(tmp_path: Path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    data_root = tmp_path / "data"
    managed_root = data_root / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    conn, _opened = open_database(
        data_root / "library.db",
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    return conn, data_root, managed_root


def _service(conn, data_root, managed_root, *, reader):
    return NmbakBackupService(
        conn,
        data_root / "backups",
        managed_root,
        app_version="0.1.0",
        data_root=data_root,
        database_id_reader=reader,
    )


def test_ensure_creates_a_uuid_and_is_idempotent(tmp_path):
    conn, _data_root, _managed = _open(tmp_path)

    assert read_database_id(conn) is None
    first = ensure_database_id(conn)
    second = ensure_database_id(conn)

    assert first == second
    assert uuid.UUID(first)  # parses as UUID4
    assert read_database_id(conn) == first


def test_legacy_library_backfills_only_on_ensure(tmp_path):
    conn, _data_root, _managed = _open(tmp_path)
    # A legacy library simply has no row; reading is unknown, not a fake value.
    assert read_database_id(conn) is None
    assert (
        conn.execute(
            "SELECT COUNT(*) FROM application_metadata WHERE metadata_key = ?",
            (DATABASE_ID_KEY,),
        ).fetchone()[0]
        == 0
    )

    value = ensure_database_id(conn)

    assert (
        conn.execute(
            "SELECT COUNT(*) FROM application_metadata WHERE metadata_key = ?",
            (DATABASE_ID_KEY,),
        ).fetchone()[0]
        == 1
    )
    assert read_database_id(conn) == value


def test_manifest_carries_the_library_identity(tmp_path):
    conn, data_root, managed = _open(tmp_path)
    identity = ensure_database_id(conn)
    service = _service(conn, data_root, managed, reader=lambda: read_database_id(conn))

    created = service.create("manual", "identity")
    package = data_root / "backups" / f"{created['backup_id']}.nmbak"
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read(MANIFEST_NAME))

    assert manifest["database_id"] == identity
    listed = service.list_backups()
    assert listed[0]["database_id"] == identity


def test_unknown_identity_creates_a_package_that_says_unknown(tmp_path):
    conn, data_root, managed = _open(tmp_path)
    service = _service(conn, data_root, managed, reader=lambda: None)

    created = service.create("manual", "unknown identity")
    package = data_root / "backups" / f"{created['backup_id']}.nmbak"
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read(MANIFEST_NAME))

    assert manifest["database_id"] is None
    assert service.list_backups()[0]["database_id"] is None


def test_restore_rejects_a_package_from_another_database(tmp_path):
    # Database A produces a package.
    conn_a, data_root_a, managed_a = _open(tmp_path / "a")
    identity_a = ensure_database_id(conn_a)
    service_a = _service(conn_a, data_root_a, managed_a, reader=lambda: read_database_id(conn_a))
    created = service_a.create("manual", "database A")

    # Database B has its own identity.
    conn_b, data_root_b, managed_b = _open(tmp_path / "b")
    identity_b = ensure_database_id(conn_b)
    assert identity_b != identity_a
    package_a = data_root_a / "backups" / f"{created['backup_id']}.nmbak"
    target = data_root_b / "backups" / package_a.name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(package_a.read_bytes())
    package_bytes = hashlib.sha256(target.read_bytes()).hexdigest()
    service_b = _service(conn_b, data_root_b, managed_b, reader=lambda: read_database_id(conn_b))

    with pytest.raises(NmbakBackupError) as caught:
        service_b.restore(target.stem, confirm_restore=True)

    assert caught.value.code == "BACKUP_DATABASE_MISMATCH"
    # Zero side effects: no pre_restore package, package bytes untouched.
    assert sorted(path.name for path in (data_root_b / "backups").iterdir()) == [target.name]
    assert hashlib.sha256(target.read_bytes()).hexdigest() == package_bytes


def test_restore_allows_unknown_identity_on_either_side(tmp_path):
    # Unknown current identity + known package identity must not block (legacy).
    conn, data_root, managed = _open(tmp_path)
    service_known = _service(conn, data_root, managed, reader=lambda: "known-a")
    created = service_known.create("manual", "known")
    service_unknown = _service(conn, data_root, managed, reader=lambda: None)

    report = service_unknown.restore(created["backup_id"], confirm_restore=True)

    assert report["restored_from"] == created["backup_id"]


def test_pre_migration_package_carries_the_existing_identity(tmp_path):
    """R-001: the migration hook is a real backup service; its packages must
    name the library identity instead of silently writing ``null``."""
    from bootstrap.core_assembly import _NmbakMigrationBackup

    conn, data_root, managed = _open(tmp_path)
    identity = ensure_database_id(conn)
    backup_root = data_root / "backups"
    hook = _NmbakMigrationBackup(
        conn, backup_root, managed, app_version="0.1.0"
    )

    backup_id = hook.create_backup("pre_migration", "test pre-migration")

    assert backup_id
    package = backup_root / f"{backup_id}.nmbak"
    with zipfile.ZipFile(package) as archive:
        manifest = json.loads(archive.read(MANIFEST_NAME))
    assert manifest["database_id"] == identity


def test_v1_package_without_identity_is_unknown_and_still_restores(tmp_path):
    """R-005: a legacy package has no database_id key -> unknown -> not blocked."""
    conn, data_root, managed = _open(tmp_path)
    identity = ensure_database_id(conn)
    service = _service(
        conn, data_root, managed, reader=lambda: read_database_id(conn)
    )
    created = service.create("manual", "legacy shape")
    package = data_root / "backups" / f"{created['backup_id']}.nmbak"

    with zipfile.ZipFile(package) as archive:
        infos = archive.infolist()
        payloads = {info.filename: archive.read(info.filename) for info in infos}
    manifest = json.loads(payloads[MANIFEST_NAME])
    manifest.pop("database_id", None)
    manifest.pop("version", None)
    manifest["format"] = "nm-backup"
    manifest["format_version"] = 1
    payloads[MANIFEST_NAME] = json.dumps(manifest, ensure_ascii=False).encode("utf-8")
    temporary = package.with_name(".legacy.nmbak")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for info in infos:
            archive.writestr(info, payloads[info.filename])
    temporary.replace(package)

    assert identity  # the current library DOES have an identity
    report = service.restore(package.stem, confirm_restore=True)
    assert report["restored_from"] == package.stem
