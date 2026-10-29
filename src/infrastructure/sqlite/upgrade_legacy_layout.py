"""One-shot migration of the pre-AD-002 data-root layout (UPGRADE-LEGACY-LAYOUT-1).

Older builds stored the library database and its managed copies under a
``data/`` sub-directory of the data root::

    <root>/data/library.db
    <root>/data/library.db-wal      (possibly)
    <root>/data/library.db-journal  (possibly)
    <root>/data/managed/...
    <root>/data/backups/...

Current builds read ``<root>/library.db``, ``<root>/managed/`` and
``<root>/backups/`` (see ``bootstrap.core_service.assemble_production_core``).
``migrate_legacy_layout`` runs once at Core start-up, *copies* the legacy files
into the current layout and reports what it did.  It never deletes or moves the
old ``data/`` tree, so the migration is idempotent and the user can roll back by
discarding the new files.

Safety rules:
- The current layout wins: an existing ``<root>/library.db`` is never
  overwritten; legacy ``managed/``/``backups/`` directories are only filled in
  when the corresponding current directory is missing (this also repairs a
  partially-completed earlier migration).
- The legacy database is verified (``PRAGMA integrity_check``) on the staging
  copy before anything is promoted.
- **Atomic promotion**: the database and the managed/backups trees are copied
  into ``<root>/.upgrade-legacy-staging`` first; only when every copy succeeded
  are they renamed into place (directories first, database last).  A failure
  leaves the data root untouched and raises :class:`LegacyLayoutError`; all
  I/O errors (locked files, permissions) are wrapped into it so start-up can
  report the problem instead of crashing.
"""

from __future__ import annotations

import logging
import os
import shutil
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

LEGACY_DATA_DIR = "data"
LEGACY_DB_NAME = "library.db"
_SQLITE_SIDECAR_SUFFIXES = ("-wal", "-shm", "-journal")
_SUBDIRECTORIES = ("managed", "backups")


class LegacyLayoutError(Exception):
    """The legacy ``data/`` layout was found but cannot be safely migrated."""


@dataclass(frozen=True)
class MigrationResult:
    """Outcome of one :func:`migrate_legacy_layout` run."""

    migrated: bool
    copied: tuple[str, ...] = field(default_factory=tuple)
    skipped_reason: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {
            "migrated": self.migrated,
            "copied": list(self.copied),
            "skipped_reason": self.skipped_reason,
        }


def _sqlite_sidecars(db_path: Path) -> tuple[Path, ...]:
    return tuple(
        db_path.with_name(db_path.name + suffix) for suffix in _SQLITE_SIDECAR_SUFFIXES
    )


def _existing_sidecars(db_path: Path) -> tuple[Path, ...]:
    return tuple(sidecar for sidecar in _sqlite_sidecars(db_path) if sidecar.is_file())


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _verify_database(staged_db: Path) -> None:
    """Raise :class:`LegacyLayoutError` unless *staged_db* is a healthy SQLite file."""
    try:
        connection = sqlite3.connect(f"file:{staged_db}?mode=ro", uri=True)
        try:
            row = connection.execute("PRAGMA integrity_check").fetchone()
        finally:
            connection.close()
    except sqlite3.Error as exc:  # pragma: no cover - depends on host I/O
        raise LegacyLayoutError(f"legacy library.db is not readable: {exc}") from exc
    if not row or row[0] != "ok":
        detail = row[0] if row else "no integrity result"
        raise LegacyLayoutError(f"legacy library.db failed integrity_check: {detail}")


def _stage_database(legacy_db: Path, staging_dir: Path) -> list[Path]:
    """Copy the legacy database + its existing SQLite sidecars into staging."""
    staged_db = staging_dir / LEGACY_DB_NAME
    _copy_file(legacy_db, staged_db)
    staged: list[Path] = [staged_db]
    for sidecar in _existing_sidecars(legacy_db):
        suffix = sidecar.name[len(legacy_db.name):]
        target = staged_db.with_name(staged_db.name + suffix)
        _copy_file(sidecar, target)
        staged.append(target)
    _verify_database(staged_db)
    return staged


def _stage_directory(legacy_dir: Path, staging_dir: Path) -> Path | None:
    """Copy a legacy sub-directory into staging; ``None`` when absent."""
    if not legacy_dir.is_dir():
        return None
    staged = staging_dir / legacy_dir.name
    shutil.copytree(legacy_dir, staged)
    return staged


def _promote_file(staged: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staged, target)


def _promote_directory(staged: Path, target: Path) -> None:
    # ``os.replace`` cannot move onto an existing directory; the caller only
    # passes this when the current directory is absent.
    target.parent.mkdir(parents=True, exist_ok=True)
    os.replace(staged, target)


def _append_log(data_root: Path, line: str) -> None:
    try:
        log_dir = data_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "upgrade-legacy.log", "a", encoding="utf-8") as handle:
            handle.write(line.rstrip() + "\n")
    except OSError:  # pragma: no cover - logging must never break start-up
        logger.warning("upgrade_legacy_layout: could not write data-root log", exc_info=True)


def migrate_legacy_layout(data_root: Path) -> MigrationResult:
    """Migrate ``<root>/data/*`` (pre-AD-002) into the current data-root layout.

    Safe to call on every start-up: it is a no-op for current layouts, never
    overwrites a current library database, and repairs a partially-completed
    earlier migration (missing managed/backups trees).
    """
    data_root = Path(data_root).expanduser()
    legacy_dir = data_root / LEGACY_DATA_DIR
    legacy_db = legacy_dir / LEGACY_DB_NAME
    current_db = data_root / LEGACY_DB_NAME

    staging_dir = data_root / ".upgrade-legacy-staging"
    try:
        if staging_dir.exists():
            shutil.rmtree(staging_dir, ignore_errors=True)

        current_exists = current_db.exists()
        legacy_subdirs = {
            name: legacy_dir / name
            for name in _SUBDIRECTORIES
            if (legacy_dir / name).is_dir()
        }
        if not legacy_db.is_file() and not legacy_subdirs:
            return MigrationResult(
                False, skipped_reason="legacy data/library.db not found"
            )

        staging_dir.mkdir(parents=True, exist_ok=True)
        # 1) Stage everything first; nothing in the data root is touched yet.
        #    When the current database already exists only the legacy
        #    sub-directories are considered - a broken/locked legacy DB must not
        #    block filling in missing managed/backups trees.
        staged_db_files = (
            _stage_database(legacy_db, staging_dir)
            if (not current_exists and legacy_db.is_file())
            else []
        )
        staged_dirs = {
            name: staged
            for name, staged in (
                (name, _stage_directory(path, staging_dir))
                for name, path in legacy_subdirs.items()
            )
            if staged is not None
        }

        # 2) Decide what to promote.  The current database wins; missing
        #    current sub-directories are filled in (also repairs partial runs).
        promote_db = (not current_exists) and bool(staged_db_files)
        promote_dirs = {
            name: staged
            for name, staged in staged_dirs.items()
            if not (data_root / name).exists()
        }
        if not promote_db and not promote_dirs:
            return MigrationResult(
                False,
                skipped_reason=(
                    "current layout already present; legacy data left untouched"
                    if current_exists
                    else "nothing to migrate"
                ),
            )

        copied: list[str] = []
        # Directories first, database last: a failure before the database is
        # promoted leaves the old root readable on the next start-up, and the
        # retry is idempotent because already-migrated directories are skipped.
        for name, staged in promote_dirs.items():
            _promote_directory(staged, data_root / name)
            copied.append(name + "/")
        if promote_db:
            # WAL/SHM/journal sidecars are promoted before the main database:
            # if a sidecar rename fails the root still has no library.db (so the
            # next start-up retries the whole promotion) instead of a database
            # stripped of its un-checkpointed WAL content.
            sidecars = [item for item in staged_db_files if item.name != LEGACY_DB_NAME]
            databases = [item for item in staged_db_files if item.name == LEGACY_DB_NAME]
            for staged in sidecars:
                suffix = staged.name[len(LEGACY_DB_NAME):]
                _promote_file(staged, current_db.with_name(current_db.name + suffix))
            for staged in databases:
                _promote_file(staged, current_db)
            copied.append(current_db.name)

        result = MigrationResult(True, copied=tuple(copied))
        _append_log(data_root, f"[upgrade-legacy] migrated from data/: {', '.join(copied)}")
        logger.info("upgrade_legacy_layout: migrated %s", ", ".join(copied))
        return result
    except LegacyLayoutError as exc:
        _append_log(data_root, f"[upgrade-legacy] refused: {exc}")
        raise
    except OSError as exc:
        message = f"filesystem error while migrating legacy layout: {exc}"
        _append_log(data_root, f"[upgrade-legacy] refused: {message}")
        raise LegacyLayoutError(message) from exc
    finally:
        shutil.rmtree(staging_dir, ignore_errors=True)
