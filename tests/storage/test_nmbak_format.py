"""FEA-13-BK2-1: backup/2 write-end + version negotiation + backup/1 read-only adapter.

Covers C-09 SC-B07 (write v2 only; backup/1 read-only, never upgraded in place)
and ADJ-2026-11-09 D1 literals:

* backup/1 = ``format:"nm-backup"`` + ``format_version:1`` (read only)
* backup/2 = ``format:"nmbak"`` + ``version:2`` (the only thing the writer emits)
* anything else -> typed ``BACKUP_FORMAT_UNSUPPORTED`` with zero side effects
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.sqlite.nmbak import (  # noqa: E402
    MANIFEST_NAME,
    NmbakBackupError,
    NmbakBackupService,
)

NOW = "2026-11-09T12:00:00+00:00"


def _books(conn) -> list[str]:
    return [row["book_id"] for row in conn.execute("SELECT book_id FROM books")]


def _package_snapshot(package: Path) -> tuple[str, int]:
    return (
        hashlib.sha256(package.read_bytes()).hexdigest(),
        package.stat().st_mtime_ns,
    )


def _rewrite_manifest(package: Path, mutate) -> None:
    """Rewrite only ``manifest.json`` inside the zip, preserving every member."""
    with zipfile.ZipFile(package) as archive:
        entries = [(info, archive.read(info.filename)) for info in archive.infolist()]
    temporary = package.with_name(f".{package.name}.rewrite-test")
    try:
        with zipfile.ZipFile(
            temporary, "w", zipfile.ZIP_DEFLATED, allowZip64=True
        ) as archive:
            for info, data in entries:
                if info.filename == MANIFEST_NAME:
                    payload = json.loads(data.decode("utf-8"))
                    mutate(payload)
                    data = json.dumps(payload, ensure_ascii=False, indent=2).encode(
                        "utf-8"
                    )
                archive.writestr(info, data)
        os.replace(temporary, package)
    finally:
        temporary.unlink(missing_ok=True)


def _to_legacy_v1(payload: dict) -> None:
    payload.pop("version", None)
    payload.pop("database_id", None)
    payload["format"] = "nm-backup"
    payload["format_version"] = 1


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
    service = NmbakBackupService(conn, backup_root, managed_root, app_version="0.1.0")

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


def test_writer_emits_v2_and_legacy_v1_restores_without_touching_the_package(workspace):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    service = workspace["service"]
    created = service.create("manual", "v2 writer")
    package = workspace["backup_root"] / f"{created['backup_id']}.nmbak"

    with zipfile.ZipFile(package) as archive:
        written = json.loads(archive.read(MANIFEST_NAME))
    assert written["format"] == "nmbak"
    assert written["version"] == 2
    assert "format_version" not in written
    assert written["database_id"] is None

    # Turn the package into a real legacy backup/1 byte layout.
    _rewrite_manifest(package, _to_legacy_v1)
    before = _package_snapshot(package)

    # A restore must overwrite the live DB with the package content...
    with workspace["conn"]:
        workspace["conn"].execute(
            "INSERT OR IGNORE INTO books (book_id, title, created_at, updated_at)"
            " VALUES ('book-2', 'LATER', ?, ?)",
            (NOW, NOW),
        )
    assert "book-2" in _books(workspace["conn"])

    report = service.restore(created["backup_id"], confirm_restore=True)
    assert report["restored_from"] == created["backup_id"]
    assert "book-2" not in _books(workspace["conn"])

    # ...while the legacy package itself stays byte-identical (no in-place upgrade).
    assert _package_snapshot(package) == before


def test_unsupported_v2_major_version_is_typed_and_has_zero_side_effects(workspace):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    service = workspace["service"]
    created = service.create("manual", "future version")
    package = workspace["backup_root"] / f"{created['backup_id']}.nmbak"
    _rewrite_manifest(package, lambda payload: payload.__setitem__("version", 3))
    before_package = _package_snapshot(package)
    before_books = _books(workspace["conn"])
    before_packages = sorted(p.name for p in workspace["backup_root"].iterdir())
    before_managed = {
        path.relative_to(workspace["managed_root"]).as_posix(): path.read_bytes()
        for path in workspace["managed_root"].rglob("*")
        if path.is_file()
    }

    with pytest.raises(NmbakBackupError) as caught:
        service.restore(created["backup_id"], confirm_restore=True)

    assert caught.value.code == "BACKUP_FORMAT_UNSUPPORTED"
    # Zero side effects: DB, managed bytes, package bytes, and no pre_restore.
    assert _books(workspace["conn"]) == before_books
    assert _package_snapshot(package) == before_package
    assert sorted(p.name for p in workspace["backup_root"].iterdir()) == before_packages
    assert {
        path.relative_to(workspace["managed_root"]).as_posix(): path.read_bytes()
        for path in workspace["managed_root"].rglob("*")
        if path.is_file()
    } == before_managed


def test_unknown_format_is_the_same_typed_code_not_corruption(workspace):
    workspace["seed_page"]("page-1", b"PAGE-ONE")
    service = workspace["service"]
    created = service.create("manual", "unknown format")
    package = workspace["backup_root"] / f"{created['backup_id']}.nmbak"
    _rewrite_manifest(
        package, lambda payload: payload.__setitem__("format", "future-format")
    )

    with pytest.raises(NmbakBackupError) as caught:
        service.restore(created["backup_id"], confirm_restore=True)

    assert caught.value.code == "BACKUP_FORMAT_UNSUPPORTED"
    assert caught.value.code != "BACKUP_CORRUPT"


def test_format_error_is_registered_as_validation_not_retryable():
    from bootstrap.core_service import _BACKUP_ERROR_RULES

    assert _BACKUP_ERROR_RULES["BACKUP_FORMAT_UNSUPPORTED"] == ("validation", False)
