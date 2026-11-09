"""``.nmbak`` backup package: writes backup/2, reads backup/1 read-only.

One backup = one zip container holding the whole recoverable state:

    <backup_id>.nmbak
    ├── manifest.json            # format/version/generation info/file digest
    ├── library.db               # SQLite consistent backup (backup API)
    ├── library.db.sidecar.json  # self-describing sidecar (schema + sha256)
    └── managed/...              # managed copies referenced by current/pinned
                                 # artifact revisions (storage-relative paths)

Frozen semantics this module owns (design §3.1–§3.5, C-09 SC-B07, FEA-13-BK2-1):

- **create** writes the zip atomically (temp file + ``os.replace``), reads it
  back and only reports ``verified=True`` when the read-back digest matches;
  the writer emits **backup/2** only (``format:"nmbak"``, ``version:2``);
- **version negotiation** accepts backup/1 (``format:"nm-backup"``,
  ``format_version:1``) read-only — a legacy package is restored byte-for-byte
  and never upgraded in place; any other format/version is the typed,
  non-retryable ``BACKUP_FORMAT_UNSUPPORTED`` (a newer package is not corrupt);
- **list** is a pure directory scan; a package whose manifest cannot be read is
  still listed with ``verified=False`` (hiding it would look like "the backup
  vanished");
- **restore** is overwrite-only, always preceded by a ``pre_restore`` package
  (a restore without a rollback point is refused), refuses to run while a
  pipeline Run is active (``BACKUP_RESTORE_BUSY``), and validates the package
  (``BACKUP_CORRUPT`` / ``BACKUP_FORMAT_UNSUPPORTED``) before touching anything;
- every failure is typed (``NmbakBackupError.code``).

The service never touches user source files (they are outside the managed
root) and never accepts a path from the caller: only a 32-hex ``backup_id``
resolved inside the configured backup root.
"""

from __future__ import annotations

import hashlib
import shutil
import json
import os
import re
import sqlite3
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from infrastructure.sqlite.backup import sha256_file, verify_backup_file
from infrastructure.sqlite.migrator import MigrationRunner, read_schema_version
from infrastructure.sqlite.schema import default_migrations


MANIFEST_NAME = "manifest.json"
DB_NAME = "library.db"
SIDECAR_NAME = "library.db.sidecar.json"
MANAGED_PREFIX = "managed/"
# backup/1 legacy literal -- READ-ONLY compatibility path (ADJ-2026-11-09 D1).
FORMAT_NAME = "nm-backup"
FORMAT_VERSION = 1
# backup/2 write-end literal: the writer only ever emits v2 (C-09 SC-B07).
FORMAT_NAME_V2 = "nmbak"
FORMAT_VERSION_V2 = 2
BACKUP_TYPES = frozenset({"manual", "automatic", "pre_migration", "pre_restore"})

# FEA-13-COV-2 (C-09 SC-B01a): every covered category is copied under this
# package prefix and validated member-by-member on restore.
EXTRAS_PREFIX = "extras/"
SETTINGS_CATEGORY = "settings"
DRAFTS_CATEGORY = "drafts"
PLUGINS_CATEGORY = "plugins"
TRASH_MANIFEST_CATEGORY = "trash-manifest"
EXTRAS_CATEGORIES = frozenset(
    {SETTINGS_CATEGORY, DRAFTS_CATEGORY, PLUGINS_CATEGORY, TRASH_MANIFEST_CATEGORY}
)
SETTINGS_FILES = (
    "provider_profiles.json",
    "network_profiles.json",
    "provider_capability_bindings.json",
)
#: Categories that are deliberately NOT packaged, each with the honest reason
#: (the manifest records this list so a restore never silently "loses" them).
EXCLUDED_CATEGORIES = (
    {"category": "catalog", "reason": "catalog.sqlite is rebuildable from library.db"},
    {"category": "derived", "reason": "derived cache is rebuildable"},
    {
        "category": "external_source_files",
        "reason": "referenced sources live outside the data root",
    },
    {
        "category": "os_credential_vault",
        "reason": "OS-managed secrets never enter a package",
    },
)
_BACKUP_ID = re.compile(r"[0-9a-f]{32}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class NmbakBackupError(RuntimeError):
    """Typed backup failure: ``code`` is the wire-facing reason."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _managed_relative_path(value: object, *, context: str, code: str = "BACKUP_CORRUPT") -> Path:
    """REALUSE-DATA-SAFETY-1 review M1: keep every managed path inside its root.

    ``Path(root) / Path(x)`` silently DISCARDS ``root`` when ``x`` is absolute
    (``C:\\Windows\\...``, ``/etc/...``, ``\\\\server\\share``) and happily walks
    out through ``..``. Both directions were reachable:

    - create: a dirty/edited ``pages.managed_original_ref`` row;
    - restore/verify: a tampered ``.nmbak`` manifest.

    The result was an out-of-root read on create and an arbitrary-path write on
    restore. Every entry point now funnels through this check and fails closed.
    """

    raw = "" if value is None else str(value).strip()
    if not raw:
        raise NmbakBackupError(code, f"{context}: empty managed path")
    if (
        Path(raw).is_absolute()
        or raw.startswith(("/", "\\"))
        or re.match(r"^[A-Za-z]:", raw)
    ):
        raise NmbakBackupError(code, f"{context}: absolute managed path {raw!r}")
    relative = Path(raw)
    if any(part in {"..", ""} for part in relative.parts):
        raise NmbakBackupError(code, f"{context}: unsafe managed path {raw!r}")
    return relative


def _resolve_within(root: Path, relative: Path, *, context: str, code: str = "BACKUP_CORRUPT") -> Path:
    """Second guard: the resolved candidate must still live under ``root``.

    Symlinks/junctions can defeat the lexical check above, so the create and
    restore paths also verify the resolved location.
    """

    candidate = root / relative
    try:
        resolved_root = root.resolve()
        resolved = candidate.resolve()
    except OSError as error:
        raise NmbakBackupError(code, f"{context}: {error}") from error
    if resolved != resolved_root and resolved_root not in resolved.parents:
        raise NmbakBackupError(code, f"{context}: managed path escapes its root {relative}")
    return candidate


class NmbakBackupService:
    """Backup/restore over ``<data_root>/backups/*.nmbak``."""

    def __init__(
        self,
        conn,
        backup_root: str | Path,
        managed_root: str | Path,
        *,
        app_version: str | None = None,
        is_run_active: Callable[[], bool] | None = None,
        data_root: Path | None = None,
        database_id_reader: Callable[[], str | None] | None = None,
    ) -> None:
        self._conn = conn
        self._backup_root = Path(backup_root)
        self._backup_root.mkdir(parents=True, exist_ok=True)
        self._managed_root = Path(managed_root)
        self._app_version = app_version
        self._is_run_active = is_run_active or (lambda: False)
        # ``<data_root>/backups`` is the default layout, so the parent of the
        # backup root is the data root unless the caller says otherwise.
        self._data_root = Path(data_root) if data_root else self._backup_root.parent
        # FEA-13-ID-3: the library identity is read lazily, never cached here --
        # a pre-migration backup honestly reports unknown before the back-fill.
        self._database_id_reader = database_id_reader

    @property
    def connection(self):
        """The live library connection (used by the merge-restore planner)."""
        return self._conn

    # ------------------------------------------------------------------
    # queries
    # ------------------------------------------------------------------
    def list_backups(self) -> list[dict]:
        entries: list[dict] = []
        for path in sorted(self._backup_root.glob("*.nmbak")):
            try:
                manifest = self._read_manifest(path)
            except NmbakBackupError:
                entries.append(
                    {
                        "backup_id": path.stem,
                        "backup_type": "unknown",
                        "created_at": "",
                        "size_bytes": path.stat().st_size,
                        "schema_version": 0,
                        "verified": False,
                    }
                )
                continue
            entries.append(
                {
                    "backup_id": path.stem,
                    "backup_type": manifest.get("backup_type", "unknown"),
                    "created_at": manifest.get("created_at", ""),
                    "size_bytes": path.stat().st_size,
                    "schema_version": int(manifest.get("schema_version") or 0),
                    "verified": bool(manifest.get("verified")),
                    "database_id": manifest.get("database_id"),
                }
            )
        return entries

    # ------------------------------------------------------------------
    # create
    # ------------------------------------------------------------------
    def create(self, backup_type: str, source_reason: str = "") -> dict:
        if backup_type not in BACKUP_TYPES:
            raise NmbakBackupError(
                "BACKUP_CREATE_FAILED", f"unsupported backup_type: {backup_type}"
            )
        backup_id = uuid.uuid4().hex
        target = self._backup_root / f"{backup_id}.nmbak"
        temporary = self._backup_root / f".{backup_id}.tmp-{uuid.uuid4().hex}.nmbak"
        workdir = Path(tempfile.mkdtemp(prefix=f".nmbak-{backup_id}-", dir=self._backup_root))
        try:
            self._write_database(workdir / DB_NAME)
            schema_version = verify_backup_file(workdir / DB_NAME)
            created_at = _utc_now()
            database_sha = sha256_file(workdir / DB_NAME)
            sidecar = {
                "schema_version": schema_version,
                "database_hash": database_sha,
                "app_version": self._app_version,
                "created_at": created_at,
            }
            (workdir / SIDECAR_NAME).write_text(
                json.dumps(sidecar, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            revision_refs = self._revision_refs()
            # REALUSE-DATA-SAFETY-1 AC2: imported page originals live in
            # ``pages.managed_original_ref`` -- NOT in ``artifact_revisions``
            # (a library that never ran a pipeline has zero artifact rows but
            # 100 MB of managed originals). Backing up only revision_refs
            # produced a "verified" package that silently lost every original
            # page, which is exactly the user data the product promises to keep.
            page_original_refs = self._page_original_refs()
            managed_files = self._copy_managed_files(
                workdir, revision_refs + page_original_refs
            )
            extras = self._collect_extras()
            extras_written = self._copy_extras(workdir, extras)
            # R-001 (FEA-13-COV-2 review): a category root that exists but holds
            # zero files is a NORMAL state (``drafts/`` survives a clean
            # shutdown; ``plugins/`` may be empty). It is still "included";
            # only a real read/collect error fails the create.
            present_categories = self._present_categories()
            manifest = {
                "format": FORMAT_NAME_V2,
                "version": FORMAT_VERSION_V2,
                # FEA-13-ID-3: the package names the library it belongs to;
                # ``None`` means the identity was still unknown at create time.
                "database_id": self._current_database_id(),
                "app_version": self._app_version,
                "schema_version": schema_version,
                "created_at": created_at,
                "backup_type": backup_type,
                "source_reason": source_reason,
                "database_sha256": database_sha,
                "managed_file_count": len(managed_files),
                "managed_total_bytes": sum(item["size_bytes"] for item in managed_files),
                "revision_refs": revision_refs,
                "page_original_refs": page_original_refs,
                "page_original_count": len(page_original_refs),
                "page_original_total_bytes": sum(
                    item["size_bytes"] for item in page_original_refs
                ),
                "included_categories": present_categories,
                # Present-but-empty roots (a clean-shutdown ``drafts/``) are
                # still covered; they simply have no member to copy.
                "empty_categories": [
                    category
                    for category in present_categories
                    if category
                    not in {item["category"] for item in extras_written}
                ],
                "skipped_categories": [],
                "excluded_categories": [dict(item) for item in EXCLUDED_CATEGORIES],
                "extras": extras_written,
                "extras_total_bytes": sum(
                    item["size_bytes"] for item in extras_written
                ),
                "verified": False,
            }
            (workdir / MANIFEST_NAME).write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            self._zip_directory(workdir, temporary)
            # AC1 read-back self check: the package must pass exactly the same
            # validation a restore performs (`_verify_package`), so a package
            # we cannot verify can never be reported as a usable backup. A
            # missing current/pinned managed source already fails below in
            # `_copy_managed_files`; this catches every other drift (digest,
            # manifest/member mismatch, unexpected managed members).
            try:
                self._verify_package(temporary)
            except NmbakBackupError as error:
                raise NmbakBackupError(
                    "BACKUP_CREATE_FAILED",
                    f"read-back verification failed: {error.detail}",
                ) from error
            verified_manifest = self._read_manifest(temporary)
            verified_manifest["verified"] = True
            self._rewrite_manifest(temporary, verified_manifest)
            os.replace(temporary, target)
            return {
                "backup_id": backup_id,
                "path": target.name,
                "size_bytes": target.stat().st_size,
                "created_at": created_at,
                "verified": True,
            }
        except NmbakBackupError:
            raise
        except (OSError, sqlite3.Error, zipfile.BadZipFile, ValueError) as error:
            raise NmbakBackupError("BACKUP_CREATE_FAILED", str(error)) from error
        finally:
            for artifact in (temporary,):
                try:
                    artifact.unlink(missing_ok=True)
                except OSError:
                    pass
            self._remove_tree(workdir)

    # ------------------------------------------------------------------
    # restore
    # ------------------------------------------------------------------
    def restore(self, backup_id: str, *, confirm_restore: bool = False) -> dict:
        if not confirm_restore:
            raise NmbakBackupError(
                "BACKUP_RESTORE_REQUIRES_CONFIRMATION", "confirm_restore must be true"
            )
        target = self._resolve(backup_id)
        if not target.is_file():
            raise NmbakBackupError("BACKUP_NOT_FOUND", backup_id)
        if self._is_run_active():
            raise NmbakBackupError(
                "BACKUP_RESTORE_BUSY", "a pipeline run is active; restore refused"
            )
        manifest = self._verify_package(target)
        package_database_id = manifest.get("database_id")
        current_database_id = self._current_database_id()
        package_identity = str(package_database_id).strip() if package_database_id else None
        current_identity = str(current_database_id).strip() if current_database_id else None
        if (
            package_identity
            and current_identity
            and package_identity != current_identity
        ):
            raise NmbakBackupError(
                "BACKUP_DATABASE_MISMATCH",
                "backup belongs to a different database: "
                f"{package_database_id} != {current_database_id}",
            )
        pre_restore = self.create(
            "pre_restore", f"automatic before restore of {backup_id}"
        )
        restore_dir = Path(
            tempfile.mkdtemp(prefix=f".nmbak-restore-{backup_id}-", dir=self._backup_root)
        )
        try:
            self._extract_package(target, restore_dir)
            try:
                restored_schema = self._restore_database(restore_dir / DB_NAME, manifest)
            except NmbakBackupError as error:
                if error.code == "BACKUP_RESTORE_INCOMPLETE":
                    raise NmbakBackupError(
                        error.code,
                        error.detail.replace(
                            "rollback package: pre_restore",
                            f"rollback package: {pre_restore['backup_id']}",
                        ),
                    ) from error
                raise
            self._restore_managed(restore_dir, manifest)
            consistency = self.managed_consistency_report()
            report = {
                "restored_from": backup_id,
                "pre_restore_backup_id": pre_restore["backup_id"],
                "schema_versions": {
                    "backup": manifest.get("schema_version"),
                    "restored": restored_schema,
                },
                "managed_consistency": consistency,
                "deferred_categories": sorted(
                    {item.get("category") for item in manifest.get("extras") or []}
                ),
            }
            missing = len(consistency.get("missing") or [])
            if missing:
                # Design §3.3(4): the DB is already overwritten (rollback is
                # the pre_restore package); report the affected revisions
                # instead of pretending the restore was complete.
                raise NmbakBackupError(
                    "BACKUP_RESTORE_INCOMPLETE",
                    f"restored from {backup_id}, but {missing} revision refs are missing "
                    f"from the managed root; rollback package: {pre_restore['backup_id']}",
                )
            return report
        finally:
            self._remove_tree(restore_dir)

    # ------------------------------------------------------------------
    # merge-restore planning support (FEA-13-RESTORE-4)
    # ------------------------------------------------------------------
    def extract_for_plan(self, backup_id: str) -> dict:
        """Extract a verified package for read-only planning.

        The caller owns the returned ``workdir`` (delete it when done). This
        method never touches the live database or the package bytes: it only
        verifies and unpacks into a fresh temporary directory.
        """
        target = self._resolve(backup_id)
        if not target.is_file():
            raise NmbakBackupError("BACKUP_NOT_FOUND", backup_id)
        manifest = self._verify_package(target)
        workdir = Path(
            tempfile.mkdtemp(prefix=f".nmbak-plan-{backup_id}-", dir=self._backup_root)
        )
        try:
            self._extract_package(target, workdir)
        except Exception:
            self._remove_tree(workdir)
            raise
        entries: dict[str, str] = {}
        for ref in manifest.get("revision_refs") or []:
            entries[str(ref["managed_path"])] = str(ref["sha256"])
        for entry in manifest.get("page_original_refs") or []:
            entries[str(entry["managed_path"])] = str(entry["sha256"])
        return {
            "backup_id": backup_id,
            "workdir": workdir,
            "database_path": workdir / DB_NAME,
            "managed_entries": entries,
            "manifest": manifest,
            "package_sha256": sha256_file(target),
        }

    def plan_undo_root(self, backup_id: str) -> Path:
        """Where UseBackup preserves the live value before overwriting it."""
        root = self._backup_root / "restore-undo" / backup_id
        root.mkdir(parents=True, exist_ok=True)
        return root

    @staticmethod
    def cleanup_plan(context: dict) -> None:
        workdir = context.get("workdir")
        if workdir is not None:
            try:
                NmbakBackupService._remove_tree(Path(workdir))
            except OSError:
                pass

    # ------------------------------------------------------------------
    # delete
    # ------------------------------------------------------------------
    def delete(self, backup_id: str) -> dict:
        target = self._resolve(backup_id)
        if not target.is_file():
            raise NmbakBackupError("BACKUP_NOT_FOUND", backup_id)
        try:
            target.unlink()
        except OSError as error:
            raise NmbakBackupError("BACKUP_DELETE_FAILED", str(error)) from error
        return {"removed": True}

    # ------------------------------------------------------------------
    # consistency
    # ------------------------------------------------------------------
    def managed_consistency_report(self) -> dict:
        rows = self._conn.execute(
            "SELECT artifact_revision_id, managed_path FROM artifact_revisions"
        ).fetchall()
        missing = []
        for row in rows:
            candidate = self._managed_root / Path(row["managed_path"])
            if not candidate.is_file():
                missing.append(
                    {
                        "revision_id": row["artifact_revision_id"],
                        "managed_path": row["managed_path"],
                    }
                )
        # REALUSE-DATA-SAFETY-1 AC2: imported page originals are user content
        # too; a restore that could not write them back must not report a
        # clean consistency pass.
        try:
            page_rows = self._conn.execute(
                "SELECT page_id, managed_original_ref FROM pages"
                " WHERE managed_original_ref IS NOT NULL AND managed_original_ref <> ''"
            ).fetchall()
        except sqlite3.OperationalError:
            page_rows = []
        for row in page_rows:
            candidate = self._managed_root / Path(row["managed_original_ref"])
            if not candidate.is_file():
                missing.append(
                    {
                        "revision_id": f"page-original:{row['page_id']}",
                        "managed_path": row["managed_original_ref"],
                    }
                )
        return {
            "checked": len(rows) + len(page_rows),
            "missing": missing,
            "skipped": "",
        }

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------
    def _resolve(self, backup_id: str) -> Path:
        if not isinstance(backup_id, str) or _BACKUP_ID.fullmatch(backup_id) is None:
            raise NmbakBackupError("BACKUP_NOT_FOUND", str(backup_id)[:64])
        target = (self._backup_root / f"{backup_id}.nmbak").resolve()
        if target.parent != Path(os.path.abspath(str(self._backup_root))):
            raise NmbakBackupError("BACKUP_NOT_FOUND", backup_id)
        return target

    def _write_database(self, destination: Path) -> None:
        """SQLite consistent backup of the live library into ``destination``."""
        out = sqlite3.connect(str(destination))
        try:
            self._conn._current().backup(out)
            out.commit()
        finally:
            out.close()

    def _page_original_refs(self) -> list[dict]:
        """Managed originals of imported pages (``pages.managed_original_ref``).

        These are user content (the Managed Copy of the source images), not
        derived artifacts, so they are backed up as their own manifest
        population instead of being disguised as artifact revisions. Older
        packages simply have no such key and restore exactly as before.
        """

        try:
            rows = self._conn.execute(
                "SELECT page_id, managed_original_ref FROM pages"
                " WHERE managed_original_ref IS NOT NULL AND managed_original_ref <> ''"
            ).fetchall()
        except sqlite3.OperationalError:
            return []
        refs: list[dict] = []
        for row in rows:
            managed_path = str(row["managed_original_ref"])
            relative = _managed_relative_path(
                managed_path,
                context=f"page {row['page_id']}",
                code="BACKUP_CREATE_FAILED",
            )
            source = _resolve_within(
                self._managed_root,
                relative,
                context=f"page {row['page_id']}",
                code="BACKUP_CREATE_FAILED",
            )
            if not source.is_file():
                raise NmbakBackupError(
                    "BACKUP_CREATE_FAILED",
                    f"managed original missing for page {row['page_id']}: {managed_path}",
                )
            refs.append(
                {
                    "page_id": row["page_id"],
                    # Store the validated, normalised form: the manifest must never
                    # carry a path that the restore side would have to trust.
                    "managed_path": relative.as_posix(),
                    "sha256": sha256_file(source),
                    "size_bytes": source.stat().st_size,
                }
            )
        return refs

    def _revision_refs(self) -> list[dict]:
        rows = self._conn.execute(
            "SELECT r.artifact_revision_id, r.artifact_id, r.managed_path,"
            " r.file_hash, r.size_bytes, r.is_pinned,"
            " CASE WHEN a.current_revision_id = r.artifact_revision_id THEN 1 ELSE 0 END"
            " FROM artifact_revisions r"
            " JOIN media_artifacts a ON a.artifact_id = r.artifact_id"
            " WHERE a.current_revision_id = r.artifact_revision_id OR r.is_pinned = 1"
        ).fetchall()
        refs = []
        for row in rows:
            managed_path = row["managed_path"]
            relative = _managed_relative_path(
                managed_path,
                context=f"revision {row['artifact_revision_id']}",
                code="BACKUP_CREATE_FAILED",
            )
            source = _resolve_within(
                self._managed_root,
                relative,
                context=f"revision {row['artifact_revision_id']}",
                code="BACKUP_CREATE_FAILED",
            )
            if not source.is_file():
                raise NmbakBackupError(
                    "BACKUP_CREATE_FAILED",
                    f"managed file missing for revision ref: {managed_path}",
                )
            # The manifest digest describes the BYTES IN THIS PACKAGE (what a
            # restore verifies), not the database's historical file_hash: a
            # live managed file may have drifted from the row (external edit,
            # partial write), and the pre_restore package must still snapshot
            # the real bytes so the restore keeps a valid rollback point.
            refs.append(
                {
                    "revision_id": row["artifact_revision_id"],
                    # Frozen field (design §3.1). Page artifact revisions are
                    # not owned by a Region (regions snapshot text/layout and
                    # have no managed image), so the field is present but null;
                    # keeping the key keeps the manifest schema closed.
                    "region_id": None,
                    "artifact_id": row["artifact_id"],
                    "managed_path": relative.as_posix(),
                    "sha256": sha256_file(source),
                    "size_bytes": source.stat().st_size,
                    "pinned": bool(row["is_pinned"] or row[6]),
                }
            )
        return refs

    def _copy_managed_files(self, workdir: Path, revision_refs: list[dict]) -> list[dict]:
        copied: list[dict] = []
        seen: set[str] = set()
        for ref in revision_refs:
            managed_path = ref["managed_path"]
            if managed_path in seen:
                continue
            seen.add(managed_path)
            relative = _managed_relative_path(
                managed_path,
                context=f"package revision {ref.get('revision_id')}",
                code="BACKUP_CREATE_FAILED",
            )
            source = _resolve_within(
                self._managed_root,
                relative,
                context=f"package revision {ref.get('revision_id')}",
                code="BACKUP_CREATE_FAILED",
            )
            if not source.is_file():
                # Design §3.1: every revision_ref must be backed by a managed
                # file with a matching digest. Silently dropping it would
                # produce a "verified" package that a restore must reject.
                raise NmbakBackupError(
                    "BACKUP_CREATE_FAILED",
                    f"managed file missing for revision ref: {managed_path}",
                )
            # The staging write stays inside the package workdir: ``relative`` was
            # already proven free of absolute/``..`` components, and WORKDIR is a
            # fresh temp directory, so no path can escape it.
            destination = workdir / MANAGED_PREFIX / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
            copied.append(
                {
                    "managed_path": relative.as_posix(),
                    "sha256": sha256_file(destination),
                    "size_bytes": destination.stat().st_size,
                }
            )
        return copied

    # ------------------------------------------------------------------
    # coverage extras (C-09 SC-B01a; FEA-13-COV-2)
    # ------------------------------------------------------------------
    def _collect_extras(self) -> list[tuple[str, str, Path]]:
        """Every covered non-managed file as (category, package-relative, absolute).

        Coverage follows C-09 SC-B01a: Core ``<data_root>/settings`` provider/
        network/binding JSON (the appearance settings under
        ``%APPDATA%/NewManga`` are deliberately OUT -- ADJ-2026-11-09 D3),
        ``<data_root>/drafts/**``, ``<data_root>/plugins/**`` and the managed
        ``trash-manifest.json``. Absent paths are simply not covered; a present
        category that cannot be collected fails the whole create.
        """
        collected: list[tuple[str, str, Path]] = []
        settings_dir = self._data_root / SETTINGS_CATEGORY
        for name in SETTINGS_FILES:
            candidate = settings_dir / name
            if candidate.is_file():
                collected.append((SETTINGS_CATEGORY, name, candidate))
        for category in (DRAFTS_CATEGORY, PLUGINS_CATEGORY):
            directory = self._data_root / category
            if directory.is_dir():
                for path in sorted(directory.rglob("*")):
                    # R-002: the running journal's `.lock/` is transient process
                    # state, never user data; `.tmp` files are in-flight writes.
                    relative = path.relative_to(directory)
                    if any(part == ".lock" for part in relative.parts):
                        continue
                    if path.name.endswith(".tmp"):
                        continue
                    # R-008: never follow links/junctions out of the category
                    # root. ``Path.is_symlink()`` is False for a Windows
                    # directory junction, so every path component is checked
                    # for a reparse point before a file is collected.
                    if path.is_symlink() or not path.is_file():
                        continue
                    if self._crosses_reparse_point(directory, relative):
                        continue
                    collected.append((category, relative.as_posix(), path))
        trash = self._managed_root / "trash-manifest.json"
        if trash.is_file():
            collected.append((TRASH_MANIFEST_CATEGORY, "trash-manifest.json", trash))
        return collected

    @staticmethod
    def _crosses_reparse_point(root: Path, relative: Path) -> bool:
        """True when any component below ``root`` is a symlink/junction."""
        current = root
        for part in relative.parts:
            current = current / part
            try:
                if current.is_symlink():
                    return True
                is_junction = getattr(current, "is_junction", None)
                if callable(is_junction) and is_junction():
                    return True
            except OSError:
                return True
        return False

    def _copy_extras(
        self,
        workdir: Path,
        entries: list[tuple[str, str, Path]],
    ) -> list[dict]:
        written: list[dict] = []
        for category, relative, absolute in entries:
            member = f"{EXTRAS_PREFIX}{category}/{relative}"
            destination = workdir / member
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(absolute, destination)
            written.append(
                {
                    "category": category,
                    "relative_path": relative,
                    "sha256": sha256_file(destination),
                    "size_bytes": destination.stat().st_size,
                }
            )
        return written

    def _current_database_id(self) -> str | None:
        reader = self._database_id_reader
        if reader is None:
            return None
        try:
            value = reader()
        except Exception:  # pragma: no cover - identity read must never fail a backup
            return None
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    def _present_categories(self) -> list[str]:
        """Every category root that exists in the data root (0 files allowed)."""
        present: list[str] = []
        if (self._data_root / SETTINGS_CATEGORY).is_dir():
            present.append(SETTINGS_CATEGORY)
        for category in (DRAFTS_CATEGORY, PLUGINS_CATEGORY):
            if (self._data_root / category).is_dir():
                present.append(category)
        if (self._managed_root / "trash-manifest.json").is_file():
            present.append(TRASH_MANIFEST_CATEGORY)
        return sorted(present)

    def _zip_directory(self, workdir: Path, target: Path) -> None:
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
            for path in sorted(workdir.rglob("*")):
                if path.is_file():
                    archive.write(path, path.relative_to(workdir).as_posix())

    def _rewrite_manifest(self, package: Path, manifest: dict) -> None:
        temp = package.with_name(f".{package.name}.rewrite-{uuid.uuid4().hex}")
        try:
            with zipfile.ZipFile(package, "r") as source, zipfile.ZipFile(
                temp, "w", zipfile.ZIP_DEFLATED, allowZip64=True
            ) as archive:
                for item in source.infolist():
                    data = source.read(item.filename)
                    if item.filename == MANIFEST_NAME:
                        data = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
                    archive.writestr(item, data)
            os.replace(temp, package)
        finally:
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass

    def _read_manifest(self, package: Path) -> dict:
        try:
            with zipfile.ZipFile(package, "r") as archive:
                payload = json.loads(archive.read(MANIFEST_NAME).decode("utf-8"))
        except (KeyError, OSError, zipfile.BadZipFile, json.JSONDecodeError) as error:
            raise NmbakBackupError("BACKUP_CORRUPT", f"{package.name}: {error}") from error
        if not isinstance(payload, dict):
            raise NmbakBackupError(
                "BACKUP_CORRUPT", f"{package.name}: manifest is not an object"
            )
        return self._negotiate_manifest(package, payload)

    def _negotiate_manifest(self, package: Path, payload: dict) -> dict:
        """C-09 SC-B07 version negotiation (write-end v2, backup/1 read-only).

        ADJ-2026-11-09 D1 fixes the literals: backup/1 is
        ``format:"nm-backup" + format_version:1`` and backup/2 is
        ``format:"nmbak" + version:2``.

        Two failure classes are kept distinct:

        * a well-formed package whose integer format/version is simply not
          supported by this build -> ``BACKUP_FORMAT_UNSUPPORTED`` (typed,
          non-retryable; the package is intact, just newer than us);
        * a manifest that is missing the version field or stores it as a
          non-integer -> ``BACKUP_CORRUPT`` (the manifest is malformed).
        """
        name = package.name
        fmt = payload.get("format")
        if fmt == FORMAT_NAME_V2:
            version = payload.get("version")
            if not isinstance(version, int) or isinstance(version, bool):
                raise NmbakBackupError(
                    "BACKUP_CORRUPT",
                    f"{name}: backup/2 manifest has no integer version",
                )
            if version != FORMAT_VERSION_V2:
                raise NmbakBackupError(
                    "BACKUP_FORMAT_UNSUPPORTED",
                    f"{name}: backup/2 version {version} is not supported",
                )
            return payload
        if fmt == FORMAT_NAME:
            legacy = payload.get("format_version")
            if not isinstance(legacy, int) or isinstance(legacy, bool):
                raise NmbakBackupError(
                    "BACKUP_CORRUPT",
                    f"{name}: backup/1 manifest has no integer format_version",
                )
            if legacy != FORMAT_VERSION:
                raise NmbakBackupError(
                    "BACKUP_FORMAT_UNSUPPORTED",
                    f"{name}: backup/1 format_version {legacy} is not supported",
                )
            return payload
        raise NmbakBackupError(
            "BACKUP_FORMAT_UNSUPPORTED",
            f"{name}: unknown backup format {fmt!r}",
        )

    def _verify_package(self, package: Path) -> dict:
        """Full validation before restore (§3.1 rules).

        Structural failures raise ``BACKUP_CORRUPT``; an intact package in a
        format/version this build does not support raises
        ``BACKUP_FORMAT_UNSUPPORTED`` (negotiation happens in
        :meth:`_negotiate_manifest`).
        """
        manifest = self._read_manifest(package)
        database_sha = str(manifest.get("database_sha256") or "")
        try:
            with zipfile.ZipFile(package, "r") as archive:
                names = set(archive.namelist())
                if DB_NAME not in names:
                    raise NmbakBackupError(
                        "BACKUP_CORRUPT", f"{package.name}: missing {DB_NAME}"
                    )
                actual_sha = hashlib.sha256(archive.read(DB_NAME)).hexdigest()
                if actual_sha != database_sha:
                    raise NmbakBackupError(
                        "BACKUP_CORRUPT",
                        f"{package.name}: database sha256 mismatch",
                    )
                # The frozen manifest is the ONLY allowed population of the
                # package: every listed managed file must exist with its
                # digest, and an unlisted managed member is corruption (a
                # tampered package must never write files the manifest does
                # not name).
                # `revision_refs` + `page_original_refs` are the authoritative
                # populations: a `managed_files` entry may only describe a path
                # already in one of them, so a tampered manifest cannot
                # self-authorize extra files.
                allowed: set[str] = set()
                for ref in manifest.get("revision_refs") or []:
                    relative = _managed_relative_path(
                        ref.get("managed_path"),
                        context=f"{package.name}: revision_ref",
                    )
                    member = MANAGED_PREFIX + relative.as_posix()
                    allowed.add(member)
                    if member not in names:
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: missing managed file {ref.get('managed_path')}",
                        )
                    if hashlib.sha256(archive.read(member)).hexdigest() != ref.get("sha256"):
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: managed sha256 mismatch {ref.get('managed_path')}",
                        )
                for entry in manifest.get("page_original_refs") or []:
                    # Never trust a manifest path: validate before using it as a
                    # zip member name (a tampered package must fail here, not at
                    # restore time).
                    relative = _managed_relative_path(
                        entry.get("managed_path"),
                        context=f"{package.name}: page original",
                    )
                    member = MANAGED_PREFIX + relative.as_posix()
                    allowed.add(member)
                    if member not in names:
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: missing page original {entry.get('managed_path')}",
                        )
                    if hashlib.sha256(archive.read(member)).hexdigest() != entry.get("sha256"):
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: page original sha256 mismatch {entry.get('managed_path')}",
                        )
                for item in manifest.get("managed_files") or []:
                    relative = _managed_relative_path(
                        item.get("managed_path"),
                        context=f"{package.name}: managed_files entry",
                    )
                    member = MANAGED_PREFIX + relative.as_posix()
                    if member not in allowed:
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: managed_files entry not in revision_refs {item.get('managed_path')}",
                        )
                # FEA-13-COV-2: extras members are validated member-by-member
                # (digest + size) and an unexpected extras member is corruption.
                allowed_extras: set[str] = set()
                for item in manifest.get("extras") or []:
                    category = str(item.get("category") or "")
                    if category not in EXTRAS_CATEGORIES:
                        raise NmbakBackupError(
                            "BACKUP_FORMAT_UNSUPPORTED",
                            f"{package.name}: unsupported extras category {category!r}",
                        )
                    relative = _managed_relative_path(
                        item.get("relative_path"),
                        context=f"{package.name}: extras",
                    )
                    member = f"{EXTRAS_PREFIX}{category}/{relative.as_posix()}"
                    allowed_extras.add(member)
                    if member not in names:
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: missing extras member {member}",
                        )
                    extra_bytes = archive.read(member)
                    if hashlib.sha256(extra_bytes).hexdigest() != item.get("sha256"):
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: extras sha256 mismatch {member}",
                        )
                    if len(extra_bytes) != item.get("size_bytes"):
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: extras size mismatch {member}",
                        )
                for member_name in names:
                    if (
                        member_name.startswith(EXTRAS_PREFIX)
                        and member_name not in allowed_extras
                    ):
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: unexpected extras member {member_name}",
                        )
                # R-007: the declared category sets must agree with the members
                # actually listed, and a verified package never reports a skip.
                declared_included = manifest.get("included_categories")
                if declared_included is not None:
                    included_set = {str(item) for item in declared_included}
                    actual_categories = {
                        str(item.get("category")) for item in manifest.get("extras") or []
                    }
                    empty_categories = {
                        str(item) for item in manifest.get("empty_categories") or []
                    }
                    if (
                        actual_categories - included_set
                        or empty_categories - included_set
                        or (actual_categories & empty_categories)
                        or (actual_categories | empty_categories) != included_set
                    ):
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: category declarations do not match extras",
                        )
                if manifest.get("skipped_categories"):
                    raise NmbakBackupError(
                        "BACKUP_CORRUPT",
                        f"{package.name}: skipped_categories must be empty in a verified package",
                    )
                for name in names:
                    if name.startswith(MANAGED_PREFIX) and name not in allowed:
                        raise NmbakBackupError(
                            "BACKUP_CORRUPT",
                            f"{package.name}: unexpected managed member {name}",
                        )
        except zipfile.BadZipFile as error:
            raise NmbakBackupError("BACKUP_CORRUPT", f"{package.name}: {error}") from error
        return manifest

    def _extract_package(self, package: Path, directory: Path) -> None:
        try:
            with zipfile.ZipFile(package, "r") as archive:
                archive.extractall(directory)
        except (OSError, zipfile.BadZipFile) as error:
            raise NmbakBackupError("BACKUP_CORRUPT", f"{package.name}: {error}") from error

    def _restore_database(self, source_path: Path, manifest: dict) -> int:
        source = sqlite3.connect(str(source_path))
        try:
            schema_version = verify_backup_file(source_path)
            source.backup(self._conn._current())
        finally:
            source.close()
        latest_known = default_migrations()[-1].schema_version
        if schema_version < latest_known:
            MigrationRunner(self._conn, default_migrations()).apply_pending()
        restored = read_schema_version(self._conn)
        if restored != latest_known:
            raise NmbakBackupError(
                "BACKUP_RESTORE_INCOMPLETE",
                f"restored schema v{restored} != known v{latest_known}; "
                f"rollback package: pre_restore",
            )
        return int(restored)

    def _restore_managed(self, restore_dir: Path, manifest: dict) -> None:
        # Only the authoritative populations are written back (the verifier
        # already rejected unlisted managed members and any managed_files entry
        # outside them): artifact revisions plus imported page originals.
        #
        # REALUSE-DATA-SAFETY-1 review M1: restore is the dangerous direction --
        # a crafted manifest used to reach any path on disk. Every entry is now
        # validated lexically AND resolved against the managed root before a
        # single byte is written.
        relatives: dict[str, Path] = {}
        for entry in (
            (manifest.get("revision_refs") or [])
            + (manifest.get("page_original_refs") or [])
        ):
            relative = _managed_relative_path(
                entry.get("managed_path"),
                context="restore entry",
            )
            relatives[relative.as_posix()] = relative
        for key in sorted(relatives):
            relative = relatives[key]
            source = restore_dir / MANAGED_PREFIX / relative
            if not source.is_file():
                continue
            destination = _resolve_within(
                self._managed_root,
                relative,
                context=f"restore {key}",
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())

    @staticmethod
    def _remove_tree(path: Path) -> None:
        shutil.rmtree(path, ignore_errors=True)
