"""``.nmbak`` backup package v1 (SETTINGS-OPEN-C-2-BACKUP, design §3).

One backup = one zip container holding the whole recoverable state:

    <backup_id>.nmbak
    ├── manifest.json            # format/version/generation info/file digest
    ├── library.db               # SQLite consistent backup (backup API)
    ├── library.db.sidecar.json  # self-describing sidecar (schema + sha256)
    └── managed/...              # managed copies referenced by current/pinned
                                 # artifact revisions (storage-relative paths)

Frozen semantics this module owns (design §3.1–§3.5):

- **create** writes the zip atomically (temp file + ``os.replace``), reads it
  back and only reports ``verified=True`` when the read-back digest matches;
- **list** is a pure directory scan; a package whose manifest cannot be read is
  still listed with ``verified=False`` (hiding it would look like "the backup
  vanished");
- **restore** is overwrite-only, always preceded by a ``pre_restore`` package
  (a restore without a rollback point is refused), refuses to run while a
  pipeline Run is active (``BACKUP_RESTORE_BUSY``), and validates the package
  (``BACKUP_CORRUPT``) before touching anything;
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
FORMAT_NAME = "nm-backup"
FORMAT_VERSION = 1
BACKUP_TYPES = frozenset({"manual", "automatic", "pre_migration", "pre_restore"})
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
    ) -> None:
        self._conn = conn
        self._backup_root = Path(backup_root)
        self._backup_root.mkdir(parents=True, exist_ok=True)
        self._managed_root = Path(managed_root)
        self._app_version = app_version
        self._is_run_active = is_run_active or (lambda: False)

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
            manifest = {
                "format": FORMAT_NAME,
                "format_version": FORMAT_VERSION,
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
        if not isinstance(payload, dict) or payload.get("format") != FORMAT_NAME:
            raise NmbakBackupError("BACKUP_CORRUPT", f"{package.name}: not a nm-backup")
        return payload

    def _verify_package(self, package: Path) -> dict:
        """Full validation before restore (§3.1 rules); raises BACKUP_CORRUPT."""
        manifest = self._read_manifest(package)
        try:
            format_version = int(manifest.get("format_version"))
            database_sha = str(manifest.get("database_sha256") or "")
        except (TypeError, ValueError) as error:
            raise NmbakBackupError("BACKUP_CORRUPT", f"{package.name}: bad manifest") from error
        if format_version != FORMAT_VERSION:
            raise NmbakBackupError(
                "BACKUP_CORRUPT",
                f"{package.name}: unsupported format_version {format_version}",
            )
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
