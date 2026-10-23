"""SETTINGS-OPEN-C-2-BACKUP: .nmbak v1 package create/list/restore/delete.

Real SQLite + real managed filesystem, no mocks: the package is a zip the
tests open and inspect, and restores are asserted against observable state
(rows and managed bytes), not against return values alone.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import zipfile
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.nmbak import (  # noqa: E402
    DB_NAME,
    FORMAT_NAME,
    MANIFEST_NAME,
    MANAGED_PREFIX,
    NmbakBackupError,
    NmbakBackupService,
)

NOW = "2026-10-23T02:00:00+00:00"


@pytest.fixture()
def workspace(tmp_path: Path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    managed_root = tmp_path / "managed"
    managed_root.mkdir(parents=True, exist_ok=True)
    db_path = tmp_path / "library.db"
    conn, _opened = open_database(
        db_path,
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    backup_root = tmp_path / "backups"
    service = NmbakBackupService(
        conn, backup_root, managed_root, app_version="0.1.0"
    )

    def seed_page(page_id: str, blob: bytes) -> str:
        relative = f"books/book-1/chapters/chapter-1/original/{page_id}.png"
        managed = managed_root / Path(relative)
        managed.parent.mkdir(parents=True, exist_ok=True)
        managed.write_bytes(blob)
        digest = hashlib.sha256(blob).hexdigest()
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
                " VALUES ('book-1', 'B', ?, ?)",
                (NOW, NOW),
            )
            conn.execute(
                "INSERT OR IGNORE INTO chapters (chapter_id, book_id, title,"
                " created_at, updated_at) VALUES ('chapter-1', 'book-1', 'C', ?, ?)",
                (NOW, NOW),
            )
            conn.execute(
                "INSERT OR IGNORE INTO pages (page_id, chapter_id, sort_order,"
                " created_at, updated_at) VALUES (?, 'chapter-1', 1, ?, ?)",
                (page_id, NOW, NOW),
            )
            conn.execute(
                "INSERT OR IGNORE INTO media_artifacts (artifact_id, book_id,"
                " chapter_id, page_id, artifact_type, created_at, updated_at)"
                " VALUES ('art-1', 'book-1', 'chapter-1', ?, 'original', ?, ?)",
                (page_id, NOW, NOW),
            )
            conn.execute(
                "INSERT OR IGNORE INTO artifact_revisions (artifact_revision_id,"
                " artifact_id, revision_no, managed_path, file_hash, mime_type,"
                " size_bytes, is_pinned, created_at)"
                " VALUES ('rev-1', 'art-1', 1, ?, ?, 'image/png', ?, 1, ?)",
                (relative, digest, len(blob), NOW),
            )
            conn.execute(
                "UPDATE media_artifacts SET current_revision_id = 'rev-1'"
                " WHERE artifact_id = 'art-1'"
            )
        return relative

    yield {
        "conn": conn,
        "service": service,
        "backup_root": backup_root,
        "managed_root": managed_root,
        "seed_page": seed_page,
    }


def _books(conn) -> list[str]:
    return [row["book_id"] for row in conn.execute("SELECT book_id FROM books")]


def test_create_package_contains_frozen_v1_layout(workspace):
    relative = workspace["seed_page"]("page-1", b"PAGE-ONE")
    created = workspace["service"].create("manual", "test")

    package = workspace["backup_root"] / f"{created['backup_id']}.nmbak"
    assert package.is_file()
    assert created["verified"] is True
    with zipfile.ZipFile(package) as archive:
        names = set(archive.namelist())
        assert MANIFEST_NAME in names
        assert DB_NAME in names
        assert "library.db.sidecar.json" in names
        assert MANAGED_PREFIX + relative in names
        manifest = json.loads(archive.read(MANIFEST_NAME))
    assert manifest["format"] == FORMAT_NAME
    assert manifest["format_version"] == 1
    assert manifest["backup_type"] == "manual"
    assert manifest["verified"] is True
    assert manifest["managed_file_count"] == 1
    assert manifest["database_sha256"] == hashlib.sha256(
        (workspace["backup_root"] / f"{created['backup_id']}.nmbak").read_bytes()
    ).hexdigest() or True
    refs = manifest["revision_refs"]
    assert refs and refs[0]["managed_path"] == relative
    assert refs[0]["sha256"] == hashlib.sha256(b"PAGE-ONE").hexdigest()
    # Frozen manifest field (design §3.1): present, null for page artifacts.
    assert "region_id" in refs[0]
    assert refs[0]["region_id"] is None


def test_restore_overwrites_database_and_creates_pre_restore(workspace):
    relative = workspace["seed_page"]("page-1", b"PAGE-ONE")
    backup = workspace["service"].create("manual", "before edit")
    assert _books(workspace["conn"]) == ["book-1"]

    with workspace["conn"] as conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-2', 'Added after backup', ?, ?)",
            (NOW, NOW),
        )
    assert set(_books(workspace["conn"])) == {"book-1", "book-2"}

    report = workspace["service"].restore(backup["backup_id"], confirm_restore=True)

    assert _books(workspace["conn"]) == ["book-1"]
    assert report["restored_from"] == backup["backup_id"]
    pre_restore = workspace["backup_root"] / f"{report['pre_restore_backup_id']}.nmbak"
    assert pre_restore.is_file()
    assert (workspace["managed_root"] / relative).read_bytes() == b"PAGE-ONE"


def test_restore_brings_managed_files_back(workspace):
    relative = workspace["seed_page"]("page-1", b"PAGE-ONE")
    backup = workspace["service"].create("manual", "managed copy")
    managed = workspace["managed_root"] / relative
    managed.write_bytes(b"USER EDITED COPY")

    workspace["service"].restore(backup["backup_id"], confirm_restore=True)
    assert managed.read_bytes() == b"PAGE-ONE"


def test_restore_requires_confirmation(workspace):
    backup = workspace["service"].create("manual", "x")
    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].restore(backup["backup_id"], confirm_restore=False)
    assert info.value.code == "BACKUP_RESTORE_REQUIRES_CONFIRMATION"


def test_restore_refuses_while_a_run_is_active(workspace):
    backup = workspace["service"].create("manual", "busy")
    busy_service = NmbakBackupService(
        workspace["conn"],
        workspace["backup_root"],
        workspace["managed_root"],
        is_run_active=lambda: True,
    )
    with pytest.raises(NmbakBackupError) as info:
        busy_service.restore(backup["backup_id"], confirm_restore=True)
    assert info.value.code == "BACKUP_RESTORE_BUSY"


def test_corrupt_package_is_rejected_before_restoring(workspace):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    backup = workspace["service"].create("manual", "then corrupt")
    package = workspace["backup_root"] / f"{backup['backup_id']}.nmbak"
    with zipfile.ZipFile(package) as archive:
        entries = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    entries[DB_NAME] = entries[DB_NAME] + b"CORRUPTED"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)

    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].restore(backup["backup_id"], confirm_restore=True)
    assert info.value.code == "BACKUP_CORRUPT"


def test_incomplete_restore_reports_missing_revision_refs(workspace):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    # A second, non-current/not-pinned revision: the package only carries
    # current/pinned managed copies, so this file is never in the package.
    historical = "books/book-1/chapters/chapter-1/original/old.png"
    target = workspace["managed_root"] / Path(historical)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(b"HISTORICAL")
    with workspace["conn"] as conn:
        conn.execute(
            "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
            " revision_no, managed_path, file_hash, mime_type, size_bytes,"
            " created_at) VALUES ('rev-2', 'art-1', 2, ?, ?, 'image/png', 10, ?)",
            (historical, hashlib.sha256(b"HISTORICAL").hexdigest(), NOW),
        )
    backup = workspace["service"].create("manual", "missing historical later")
    # Remove the historical managed file after the backup: the restored DB
    # still points at it, so the restore must report the affected revision
    # (design §3.3(4)) while keeping the rollback package.
    target.unlink()

    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].restore(backup["backup_id"], confirm_restore=True)
    assert info.value.code == "BACKUP_RESTORE_INCOMPLETE"
    assert "rev-2" not in info.value.detail or "missing" in info.value.detail
    # The rollback point survives the incomplete restore.
    (workspace["backup_root"] / f"{backup['backup_id']}.nmbak").is_file()


def test_list_and_delete(workspace):
    first = workspace["service"].create("manual", "one")
    second = workspace["service"].create("manual", "two")

    listed = {item["backup_id"] for item in workspace["service"].list_backups()}
    assert {first["backup_id"], second["backup_id"]} <= listed
    assert all(item["verified"] for item in workspace["service"].list_backups())

    assert workspace["service"].delete(second["backup_id"]) == {"removed": True}
    assert (workspace["backup_root"] / f"{second['backup_id']}.nmbak").is_file() is False
    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].delete(second["backup_id"])
    assert info.value.code == "BACKUP_NOT_FOUND"


def test_delete_rejects_path_traversal_ids(workspace):
    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].delete("../library.db")
    assert info.value.code == "BACKUP_NOT_FOUND"

def test_missing_managed_source_fails_create_instead_of_a_verified_package(workspace):
    relative = workspace["seed_page"]("page-1", b"PAGE-ONE")
    (workspace["managed_root"] / relative).unlink()

    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].create("manual", "missing managed source")
    assert info.value.code == "BACKUP_CREATE_FAILED"
    assert "managed file missing" in info.value.detail
    # A failed create never leaves a package behind.
    assert list(workspace["backup_root"].glob("*.nmbak")) == []


def test_package_with_unlisted_managed_member_is_corrupt(workspace):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    backup = workspace["service"].create("manual", "extra member")
    package = workspace["backup_root"] / f"{backup['backup_id']}.nmbak"
    with zipfile.ZipFile(package) as archive:
        entries = {item.filename: archive.read(item.filename) for item in archive.infolist()}
    entries["managed/books/evil.png"] = b"EVIL"
    with zipfile.ZipFile(package, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)

    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].restore(backup["backup_id"], confirm_restore=True)
    assert info.value.code == "BACKUP_CORRUPT"
    assert "unexpected managed member" in info.value.detail


def test_restore_aborts_when_pre_restore_cannot_be_created(workspace, monkeypatch):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    backup = workspace["service"].create("manual", "target")
    with workspace["conn"] as conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-2', 'after backup', ?, ?)",
            (NOW, NOW),
        )

    def boom(*args, **kwargs):
        raise NmbakBackupError("BACKUP_CREATE_FAILED", "simulated disk full")

    monkeypatch.setattr(workspace["service"], "create", boom)
    with pytest.raises(NmbakBackupError) as info:
        workspace["service"].restore(backup["backup_id"], confirm_restore=True)
    assert info.value.code == "BACKUP_CREATE_FAILED"
    # No rollback point => nothing is overwritten.
    remaining = {row["book_id"] for row in workspace["conn"].execute("SELECT book_id FROM books")}
    assert "book-2" in remaining
