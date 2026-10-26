"""Backup/restore use-case contracts (TASK-021 frozen subset 3, TASK-057).

Consumer-side protocol for the library backup ledger. The semantics this
slice fixes:

- a backup = database file + self-describing sidecar (schema version,
  content hash) + a ``backup_records`` row (when the schema is present),
  verified readable after the write (AC 1);
- restore = **overwrite** of the live database from a verified backup,
  always preceded by an automatic ``pre_restore`` backup file (so the
  restore itself is rollback-able), followed by the DB/Managed Copy
  consistency report (AC 2/3);
- every failure is typed (AC 4).
"""

from __future__ import annotations

from typing import Protocol


class BackupLedger(Protocol):
    """Backup/restore face consumed by the application layer."""

    def create_backup(
        self,
        backup_type: str,
        source_reason: str,
        *,
        app_version: str | None = None,
    ) -> str: ...

    def restore_backup(self, backup_id: str) -> dict:
        """Overwrite-restore; returns a report dict (restored-from id,
        pre-restore backup id, schema versions, managed-consistency)."""
        ...

    def managed_consistency_report(self) -> dict:
        """Revision ``managed_path`` vs managed-root file existence."""
        ...
