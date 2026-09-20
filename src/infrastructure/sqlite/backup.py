"""SQLite backup service writing BackupRecord metadata (D03 §34.3)."""

from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.schema import default_migrations


_BACKUP_ID = re.compile(r"[0-9a-f]{32}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SqliteBackupService:
    """Creates consistent backups via the SQLite backup API (D07 §48)."""

    def __init__(
        self,
        conn: sqlite3.Connection,
        backup_root: str | Path,
        *,
        managed_root: str | Path | None = None,
    ) -> None:
        self._conn = conn
        self._backup_root = Path(backup_root)
        self._backup_root.mkdir(parents=True, exist_ok=True)
        # AC 2: with a managed root configured, restore() can assert the
        # DB/Managed Copy consistency (revision managed paths vs files).
        self._managed_root = Path(managed_root) if managed_root is not None else None

    def create_backup(
        self,
        backup_type: str,
        source_reason: str,
        *,
        app_version: str | None = None,
    ) -> str:
        if backup_type not in {"automatic", "manual", "pre_migration", "pre_restore"}:
            raise ValueError(f"unsupported backup_type: {backup_type}")
        backup_id = uuid.uuid4().hex
        target = self._backup_root / f"{backup_id}.db"
        temporary = self._backup_root / f".{backup_id}.tmp-{uuid.uuid4().hex}.db"
        # managed_path is the storage-relative managed path (D03 §34.3), not
        # a bare file name, so later restore/cleanup slices can resolve it.
        managed_path = f"{self._backup_root.name}/{target.name}"
        completed = False
        try:
            destination = sqlite3.connect(str(temporary))
            try:
                self._conn.backup(destination)
                destination.commit()
            finally:
                destination.close()
            schema_version = verify_backup_file(temporary)
            created_at = _utc_now()
            size_bytes = temporary.stat().st_size
            database_hash = sha256_file(temporary)
            temporary_sidecar = write_sidecar(
                temporary,
                schema_version=schema_version,
                database_hash=database_hash,
                app_version=app_version,
                created_at=created_at,
            )
            os.replace(temporary_sidecar, _sidecar_path(target))
            os.replace(temporary, target)
            if not self._backup_records_table_exists():
                # The v0 → v1 pre-migration backup runs before any schema exists,
                # so there is nowhere to record metadata yet; the backup file
                # plus its self-describing sidecar remain the deliverable.
                completed = True
                return backup_id
            with self._conn:
                self._conn.execute(
                    "INSERT INTO backup_records (backup_id, backup_type, managed_path, status,"
                    " app_version, schema_version, database_hash, size_bytes, created_at,"
                    " completed_at, source_reason)"
                    " VALUES (?, ?, ?, 'completed', ?, ?, ?, ?, ?, ?, ?)",
                    (
                        backup_id,
                        backup_type,
                        managed_path,
                        app_version,
                        schema_version,
                        database_hash,
                        size_bytes,
                        created_at,
                        _utc_now(),
                        source_reason,
                    ),
                )
            completed = True
            return backup_id
        except (BackupVerificationError, OSError, sqlite3.Error) as error:
            raise BackupVerificationError("BACKUP_CREATE_FAILED", str(error)) from error
        finally:
            if not completed:
                for candidate in (temporary, target):
                    for artifact in (candidate, _sidecar_path(candidate)):
                        try:
                            artifact.unlink(missing_ok=True)
                        except OSError:
                            pass

    def _backup_records_table_exists(self) -> bool:
        row = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='backup_records'"
        ).fetchone()
        return row is not None

    def restore_backup(self, backup_id: str) -> dict:
        """Restore the main database from a recorded backup (AC 2: the
        semantics are **overwrite** — the backup API replaces every page of
        the live database with the backup's).

        Order of operations (AC 3: no half-finished state, AC 4: typed):

        1. resolve the record (typed ``BACKUP_UNKNOWN``);
        2. verify the file: exists, sidecar hash matches, integrity ok
           (all typed) — before anything is written;
        3. take an automatic ``pre_restore`` backup (file + sidecar survive
           the overwrite even though the ``backup_records`` row of the live
           database does not — the sidecar is what makes that backup
           recoverable);
        4. run the SQLite backup API backup-file -> live connection;
        5. report the post-restore schema version and, when a managed root
           is configured, the DB/Managed Copy consistency report.
        """
        if _BACKUP_ID.fullmatch(backup_id) is None:
            raise BackupVerificationError("BACKUP_UNKNOWN", backup_id)
        target = (self._backup_root / f"{backup_id}.db").resolve()
        if target.parent != self._backup_root.resolve():
            raise BackupVerificationError("BACKUP_UNKNOWN", backup_id)
        row = self._conn.execute(
            "SELECT managed_path, database_hash, schema_version FROM backup_records"
            " WHERE backup_id = ? AND status = 'completed'",
            (backup_id,),
        ).fetchone()
        if row is None:
            # Overwrite semantics: after a restore the live database's
            # backup_records revert to the backup point, which may predate
            # the requested id entirely (e.g. restoring twice). The
            # self-describing sidecar is the fallback authority then; a
            # missing file is still typed.
            if not target.is_file():
                raise BackupVerificationError("BACKUP_UNKNOWN", backup_id)
            recorded_hash = read_sidecar(target)["database_hash"]
        else:
            recorded_hash = row["database_hash"]
            expected_path = Path(self._backup_root.name) / target.name
            if Path(row["managed_path"]) != expected_path:
                raise BackupVerificationError(
                    "BACKUP_PATH_INVALID", str(row["managed_path"])
                )
        target_schema = verify_backup_file(target)
        sidecar = read_sidecar(target)
        try:
            sidecar_schema = int(sidecar["schema_version"])
            recorded_schema = (
                int(row["schema_version"]) if row is not None else target_schema
            )
        except (KeyError, TypeError, ValueError) as error:
            raise BackupVerificationError(
                "SCHEMA_MISMATCH", f"{target.name}: invalid schema metadata"
            ) from error
        if sidecar_schema != target_schema or recorded_schema != target_schema:
            raise BackupVerificationError(
                "SCHEMA_MISMATCH", f"{target.name}: database/metadata disagree"
            )
        latest_known = default_migrations()[-1].schema_version
        if target_schema > latest_known:
            raise BackupVerificationError(
                "SCHEMA_TOO_NEW",
                f"backup schema v{target_schema} is newer than known v{latest_known}",
            )
        if sidecar["database_hash"] != recorded_hash:
            raise BackupVerificationError(
                "SIDECAR_MISMATCH",
                f"{target.name}: sidecar hash != recorded hash",
            )
        actual_hash = sha256_file(target)
        if actual_hash != recorded_hash:
            raise BackupVerificationError(
                "HASH_MISMATCH",
                f"{target.name}: file hash != recorded hash",
            )

        pre_restore_id = self.create_backup(
            "pre_restore", f"automatic before restore of {backup_id}"
        )
        pre_restore_target = self._backup_root / f"{pre_restore_id}.db"

        try:
            self._restore_database(target)
            if target_schema < latest_known:
                MigrationRunner(self._conn, default_migrations()).apply_pending()
            (integrity,) = self._conn.execute("PRAGMA integrity_check").fetchone()
            if integrity != "ok":
                raise BackupVerificationError("INTEGRITY_FAILED", str(integrity))
            restored_version = read_schema_version(self._conn)
            if restored_version != latest_known:
                raise BackupVerificationError(
                    "SCHEMA_MISMATCH",
                    f"restored schema v{restored_version} != known v{latest_known}",
                )
            report = {
                "restored_from": backup_id,
                "pre_restore_backup_id": pre_restore_id,
                "schema_version": restored_version,
                "expected_schema_version": latest_known,
            }
            report["managed_consistency"] = self.managed_consistency_report()
            return report
        except Exception as error:
            try:
                self._restore_database(pre_restore_target)
            except Exception as rollback_error:
                raise BackupVerificationError(
                    "RESTORE_ROLLBACK_FAILED",
                    f"pre_restore={pre_restore_id}; restore={error}; "
                    f"rollback={rollback_error}",
                ) from error
            raise BackupVerificationError(
                "RESTORE_FAILED",
                f"{error}; pre_restore={pre_restore_id}; rollback=completed",
            ) from error

    def _restore_database(self, target: Path) -> None:
        """Copy one verified SQLite file into the current thread's live DB."""
        source = sqlite3.connect(str(target))
        try:
            # The restore gate guarantees that this real connection is idle.
            source.backup(self._conn._current())
        finally:
            source.close()

    def managed_consistency_report(self) -> dict:
        """AC 2 assertion face: every revision ``managed_path`` recorded in
        the restored database must exist inside the managed root. Missing
        files are listed (never repaired); no managed root configured means
        the check is skipped with a reason."""
        if self._managed_root is None:
            return {"checked": 0, "missing": [], "skipped": "no managed root configured"}
        rows = self._conn.execute(
            "SELECT managed_path FROM artifact_revisions"
        ).fetchall()
        missing = []
        for row in rows:
            candidate = self._managed_root / Path(row["managed_path"])
            if not candidate.is_file():
                missing.append(row["managed_path"])
        return {"checked": len(rows), "missing": missing, "skipped": ""}



class BackupVerificationError(RuntimeError):
    """Typed backup/restore failure (TASK-057 AC 4): ``code`` is the
    machine-readable reason, ``detail`` the human one."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _sidecar_path(target: Path) -> Path:
    return target.with_name(target.name + ".manifest.json")


def write_sidecar(
    target: Path,
    *,
    schema_version: int,
    database_hash: str,
    app_version: str | None,
    created_at: str,
) -> Path:
    """Self-describing sidecar next to the backup file (AC 1): the record
    survives even when the *backed-up* database (which holds
    ``backup_records``) is later overwritten by a restore."""
    import json
    import os
    import uuid

    payload = {
        "schema_version": schema_version,
        "database_hash": database_hash,
        "app_version": app_version,
        "created_at": created_at,
    }
    sidecar = _sidecar_path(target)
    temp = sidecar.with_name(f".{sidecar.name}.tmp-{uuid.uuid4().hex}")
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False, indent=2))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, sidecar)
    except OSError:
        try:
            temp.unlink()
        except OSError:
            pass
        raise
    return sidecar


def read_sidecar(target: Path) -> dict:
    import json

    sidecar = _sidecar_path(target)
    try:
        payload = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise BackupVerificationError(
            "SIDECAR_UNREADABLE", f"{sidecar.name}: {error}"
        ) from error
    if not isinstance(payload, dict) or "database_hash" not in payload:
        raise BackupVerificationError(
            "SIDECAR_UNREADABLE", f"{sidecar.name}: missing database_hash"
        )
    return payload


def verify_backup_file(target: Path) -> int:
    """AC 1 read-back check: integrity + readable schema version.
    Raises :class:`BackupVerificationError`; returns the schema version."""
    if not target.is_file():
        raise BackupVerificationError("BACKUP_FILE_MISSING", str(target.name))
    check = sqlite3.connect(str(target))
    try:
        (result,) = check.execute("PRAGMA integrity_check").fetchone()
        if result != "ok":
            raise BackupVerificationError("INTEGRITY_FAILED", str(result))
        try:
            version = read_schema_version(check)
        except sqlite3.Error as error:
            raise BackupVerificationError(
                "SCHEMA_UNREADABLE", str(error)
            ) from error
    except sqlite3.DatabaseError as error:
        # "file is not a database" and friends are integrity failures too
        raise BackupVerificationError("INTEGRITY_FAILED", str(error)) from error
    finally:
        check.close()
    return int(version or 0)
