"""One-shot migration of the pre-AD-002 data-root layout (UPGRADE-LEGACY-LAYOUT-1).

Older builds stored the library database and its managed copies under a
``data/`` sub-directory of the data root::

    <root>/data/library.db
    <root>/data/library.db-wal      (possibly)
    <root>/data/managed/...
    <root>/data/backups/...

Current builds read ``<root>/library.db``, ``<root>/managed/`` and
``<root>/backups/`` (see ``bootstrap.core_service.assemble_production_core``).
``migrate_legacy_layout`` runs once at Core start-up, *copies* the legacy files
into the current layout and reports what it did.  It never deletes or moves the
old ``data/`` tree, so the migration is idempotent and the user can roll back by
discarding the new files.

Safety rules:
- The current layout wins: if ``<root>/library.db`` already exists the legacy
  database is left untouched (``skipped_reason`` explains why).
- The legacy database is verified (``PRAGMA integrity_check``) on a staging
  copy before it is promoted; a corrupt/stale database raises
  :class:`LegacyLayoutError` instead of replacing a working library.
- All writes go through a temporary staging directory first; a failure leaves
  the data root as it was.
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
_WAL_SUFFIXES = ("-wal", "-shm")


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


def _sidecar_paths(db_path: Path) -> tuple[Path, ...]:
    return tuple(db_path.with_name(db_path.name + suffix) for suffix in _WAL_SUFFIXES)


def _copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def _verify_copy(staging_db: Path) -> None:
    """Raise :class:`LegacyLayoutError` unless *staging_db* is a healthy SQLite file."""
    try:
        connection = sqlite3.connect(f"file:{staging_db}?mode=ro", uri=True)
        try:
            row = connection.execute("PRAGMA integrity_check").fetchone()
        finally:
            connection.close()
    except sqlite3.Error as exc:  # pragma: no cover - depends on host I/O
        raise LegacyLayoutError(f"legacy library.db is not readable: {exc}") from exc
    if not row or row[0] != "ok":
        detail = row[0] if row else "no integrity result"
        raise LegacyLayoutError(f"legacy library.db failed integrity_check: {detail}")


def _promote_database(legacy_db: Path, current_db: Path, staging_root: Path) -> tuple[str, ...]:
    """Copy the legacy database (+ existing WAL/SHM) to staging, verify, then promote it."""
    copied: list[str] = []
    staged_db = staging_root / current_db.name
    source_sidecars = tuple(
        sidecar for sidecar in _sidecar_paths(legacy_db) if sidecar.is_file()
    )
    _copy_file(legacy_db, staged_db)
    for sidecar in source_sidecars:
        _copy_file(sidecar, staged_db.with_name(staged_db.name + sidecar.name[len(legacy_db.name):]))
    _verify_copy(staged_db)
    os.replace(staged_db, current_db)
    copied.append(current_db.name)
    # Promote only the sidecars that existed in the legacy directory; the
    # read-only verification above may create empty WAL/SHM files in staging.
    for sidecar in source_sidecars:
        target = current_db.with_name(current_db.name + sidecar.name[len(legacy_db.name):])
        staged = staged_db.with_name(staged_db.name + sidecar.name[len(legacy_db.name):])
        if staged.is_file():
            os.replace(staged, target)
            copied.append(target.name)
    return tuple(copied)


def _promote_directory(legacy_dir: Path, current_dir: Path) -> str | None:
    """Copy a legacy sub-directory into the current layout unless it already exists."""
    if not legacy_dir.is_dir() or current_dir.exists():
        return None
    shutil.copytree(legacy_dir, current_dir)
    return current_dir.name + "/"


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

    Safe to call on every start-up: it is a no-op for current layouts and never
    overwrites a current library database.
    """
    data_root = Path(data_root).expanduser()
    legacy_dir = data_root / LEGACY_DATA_DIR
    legacy_db = legacy_dir / LEGACY_DB_NAME
    current_db = data_root / LEGACY_DB_NAME

    if not legacy_db.is_file():
        return MigrationResult(False, skipped_reason="legacy data/library.db not found")
    if current_db.exists():
        return MigrationResult(
            False,
            skipped_reason="current library.db already present; legacy data left untouched",
        )

    staging_root = data_root / ".upgrade-legacy-staging"
    if staging_root.exists():
        shutil.rmtree(staging_root, ignore_errors=True)
    staging_root.mkdir(parents=True, exist_ok=True)
    try:
        copied = list(_promote_database(legacy_db, current_db, staging_root))
        for name in ("managed", "backups"):
            promoted = _promote_directory(legacy_dir / name, data_root / name)
            if promoted is not None:
                copied.append(promoted)
        result = MigrationResult(True, copied=tuple(copied))
        _append_log(
            data_root,
            f"[upgrade-legacy] migrated from data/: {', '.join(copied)}",
        )
        logger.info("upgrade_legacy_layout: migrated %s", ", ".join(copied))
        return result
    except LegacyLayoutError as exc:
        _append_log(data_root, f"[upgrade-legacy] refused: {exc}")
        raise
    finally:
        shutil.rmtree(staging_root, ignore_errors=True)
