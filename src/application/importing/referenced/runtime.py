"""FEA-09 referenced-import operation runtime (C-16 §4 frozen state machine).

``accepted → running → completed | cancelled | failed`` with per-page commit
units, the replay matrix, the per-book single-flight lock and the frozen
receipt shape/counts. Receipts are session state only — nothing here is
persisted; committed pages are the only durable outcome (C-16 §4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from contextlib import nullcontext
from datetime import datetime, timezone
import hashlib
import io
import re
import threading
import time
import uuid
import zipfile

from domain.pages.entities import Page
from application.importing.referenced.errors import SourceImportError
from application.importing.referenced.model import ResolvedSourceRead, canonical_json
from application.importing.referenced.scanner import (
    ordered_archive_members,
    read_verified_bytes,
    scan_source,
)
from application.importing.referenced.planner import PlanRecord, PlannedSource

#: C-16 §4 receipt count fields (frozen names, plural = aggregation).
COUNT_FIELDS = (
    "imported_pages",
    "skipped_pages",
    "skipped_sources",
    "failed_sources",
    "unsupported_entries",
    "pending_pages",
)

_OPERATION_ID = re.compile(r"^[A-Za-z0-9_-]{16,128}$")
#: R1-I010: known transactional storage guards mapped onto frozen reasons.
_STORAGE_ERROR_CODES = {
    "SourceProjectMismatch": "SOURCE_PROJECT_MISMATCH",
}
TERMINAL_STATES = ("completed", "cancelled", "failed")
DECODER_NAME = "referenced-import/1"
DECODER_VERSION = "1"


def _empty_counts() -> dict[str, int]:
    return {name: 0 for name in COUNT_FIELDS}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@dataclass
class _SourceProgress:
    source: PlannedSource
    outcome: str = "pending"
    reason_code: str | None = None
    committed_pages: int = 0
    committed_entries: int = 0
    pages: list[dict] = field(default_factory=list)
    counts: dict = field(default_factory=_empty_counts)

    def item(self) -> dict:
        return {
            "source_index": self.source.source_index,
            "source_name": self.source.source_name,
            "source_kind": self.source.source_kind,
            "outcome": self.outcome,
            "reason_code": self.reason_code,
            "committed_pages": self.committed_pages,
            "remaining_pages": self.counts["pending_pages"],
            "committed_entries": self.committed_entries,
            "pages": list(self.pages),
            "counts": dict(self.counts),
        }


@dataclass
class _Operation:
    operation_id: str
    fingerprint: str
    chapter_id: str
    plan_id: str
    plan_digest: str
    grant_ids: list[str]
    duplicate_policy: str
    book_id: str
    state: str = "accepted"
    cancel_requested: bool = False
    progress: list[_SourceProgress] = field(default_factory=list)


class _HaltOperation(Exception):
    """Internal control flow: stop all further commit units."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class ReferencedImportRuntime:
    """Async accept→poll face for referenced imports (Export precedent)."""

    def __init__(
        self,
        *,
        repository,
        access,
        planner,
        project_of_chapter,
        image_decoder,
        pdf_open,
        clock=time.time,
        secret_reader=None,
        enabled=None,
    ) -> None:
        self._repository = repository
        self._access = access
        self._planner = planner
        self._project_of_chapter = project_of_chapter
        self._image_decoder = image_decoder
        self._pdf_open = pdf_open
        self._clock = clock
        self._secret_reader = secret_reader
        self._enabled = enabled
        self._lock = threading.RLock()
        self._operations: dict[str, _Operation] = {}
        self._active_books: dict[str, str] = {}  # book_id -> operation_id
        # Consecutive password failures per physical source (C-16 §3: >=3
        # failures -> the source fails, skipping stays allowed).
        self._password_failures: dict[str, int] = {}

    # ---------------------------------------------------------------- start
    def start(
        self,
        *,
        chapter_id: str,
        plan_id: str,
        plan_digest: str,
        grants: list[str],
        duplicate_policy: str,
        operation_id: str,
        secret_ref: object = None,
    ) -> dict:
        if self._enabled is not None and not self._enabled():
            raise SourceImportError(
                "SOURCE_ACCESS_DENIED", "referenced import is disabled"
            )
        if (
            not isinstance(chapter_id, str) or not chapter_id
            or not isinstance(plan_id, str) or not plan_id
            or not isinstance(plan_digest, str) or not plan_digest
            or not isinstance(grants, list) or not grants
            or duplicate_policy not in ("skip", "import_as_new")
            or not isinstance(operation_id, str)
            or not _OPERATION_ID.fullmatch(operation_id)
        ):
            raise SourceImportError(
                "SOURCE_OPERATION_CONFLICT", "import start request is invalid"
            )
        if self._repository.get_chapter(chapter_id) is None:
            raise SourceImportError(
                "SOURCE_OPERATION_NOT_FOUND", "import chapter was not found"
            )
        fingerprint = hashlib.sha256(
            canonical_json(
                {
                    "chapter_id": chapter_id,
                    "plan_id": plan_id,
                    "plan_digest": plan_digest,
                    "grants": list(grants),
                    "duplicate_policy": duplicate_policy,
                }
            ).encode("utf-8")
        ).hexdigest()

        with self._lock:
            existing = self._operations.get(operation_id)
            if existing is not None:
                if existing.fingerprint != fingerprint:
                    raise SourceImportError(
                        "SOURCE_OPERATION_CONFLICT",
                        "operation id is bound to a different request",
                    )
                # Replay: same id + same fingerprint -> current state, the
                # terminal receipt is never re-run (C-16 §4). Checked before
                # the plan is taken/consumed — a replay never re-confirms.
                return {
                    "operation_id": operation_id,
                    "accepted": True,
                    "plan_digest": existing.plan_digest,
                    "state": existing.state,
                }

        record = self._planner.take_for_start(plan_id=plan_id, plan_digest=plan_digest)
        if record.chapter_id != chapter_id or record.grant_ids != list(grants):
            raise SourceImportError(
                "SOURCE_PLAN_STALE", "import plan does not match the request"
            )
        book_id = self._project_of_chapter(chapter_id)
        if book_id is None:
            raise SourceImportError(
                "SOURCE_PROJECT_MISMATCH", "import chapter has no project"
            )
        # R1-I009: the plan is bound to its original project + duplicate policy.
        if record.book_id != book_id or record.duplicate_policy != duplicate_policy:
            raise SourceImportError(
                "SOURCE_PLAN_STALE",
                "import plan project or duplicate policy changed since planning",
            )
        with self._lock:
            holder = self._active_books.get(book_id)
            if (
                holder is not None
                and self._operations.get(holder) is not None
                and self._operations[holder].state not in TERMINAL_STATES
            ):
                raise SourceImportError(
                    "SOURCE_IMPORT_BUSY",
                    "another import is active for this project",
                )
            operation = _Operation(
                operation_id=operation_id,
                fingerprint=fingerprint,
                chapter_id=chapter_id,
                plan_id=plan_id,
                plan_digest=plan_digest,
                grant_ids=list(grants),
                duplicate_policy=duplicate_policy,
                book_id=book_id,
            )
            for source in record.sources:
                progress = _SourceProgress(source=source)
                # Participating pages exclude only already-referenced skips;
                # unsupported members stay in `planned` per C-16 §4.
                progress.counts["pending_pages"] = sum(
                    1 for page in source.pages if not page["already_referenced"]
                ) if source.status in {"ok", "encrypted"} else 0
                operation.progress.append(progress)
            self._operations[operation_id] = operation
            # Atomic per-book reservation BEFORE accepted is observable.
            self._active_books[book_id] = operation_id

        # Single confirmation: consume the plan so a duplicate/stale confirm
        # cannot restart it (C-16 §5).
        self._planner.consume(plan_id)

        worker = threading.Thread(
            target=self._run_operation,
            args=(operation, record),
            kwargs={"secret_ref": secret_ref},
            name=f"fea09-import-{operation_id[:16]}",
            daemon=True,
        )
        with self._lock:
            if operation.state == "cancelled":
                # Cancelled between reservation and worker start.
                self._release_book(operation)
                return {
                    "operation_id": operation_id,
                    "accepted": True,
                    "plan_digest": plan_digest,
                    "state": operation.state,
                }
        worker.start()
        return {
            "operation_id": operation_id,
            "accepted": True,
            "plan_digest": plan_digest,
        }

    # -------------------------------------------------------------- receipt
    def receipt(self, operation_id: str) -> dict:
        with self._lock:
            operation = self._operations.get(operation_id)
            if operation is None:
                raise SourceImportError(
                    "SOURCE_OPERATION_NOT_FOUND", "import operation was not found"
                )
            return self._receipt_locked(operation)

    def _receipt_locked(self, operation: _Operation) -> dict:
        items = [progress.item() for progress in operation.progress]
        totals = _empty_counts()
        for item in items:
            for name in COUNT_FIELDS:
                totals[name] += item["counts"][name]
        return {
            "operation_id": operation.operation_id,
            "chapter_id": operation.chapter_id,
            "plan_id": operation.plan_id,
            "plan_digest": operation.plan_digest,
            "state": operation.state,
            "cancel_requested": operation.cancel_requested,
            "committed_boundary": sum(item["committed_pages"] for item in items),
            "items": items,
            "totals": totals,
        }

    # --------------------------------------------------------------- cancel
    def cancel(self, operation_id: str) -> dict:
        with self._lock:
            operation = self._operations.get(operation_id)
            if operation is None:
                raise SourceImportError(
                    "SOURCE_OPERATION_NOT_FOUND", "import operation was not found"
                )
            if operation.state in TERMINAL_STATES:
                return {
                    "operation_id": operation_id,
                    "accepted": False,
                    "state": operation.state,
                }
            operation.cancel_requested = True
            if operation.state == "accepted":
                # Accepted-phase cancel never starts the work (C-16 §4 ①).
                operation.state = "cancelled"
                self._release_book(operation)
            return {
                "operation_id": operation_id,
                "accepted": True,
                "state": operation.state,
            }

    def _release_book(self, operation: _Operation) -> None:
        if self._active_books.get(operation.book_id) == operation.operation_id:
            self._active_books.pop(operation.book_id, None)

    # --------------------------------------------------------------- worker
    def _run_operation(
        self, operation: _Operation, record: PlanRecord, *, secret_ref: object
    ) -> None:
        with self._lock:
            if operation.state != "accepted":
                # Cancelled (or otherwise final) before the work started.
                return
            operation.state = "running"
        failed = False
        try:
            for progress in list(operation.progress):
                try:
                    self._process_source(operation, progress, record, secret_ref)
                except _HaltOperation as halt:
                    if not operation.cancel_requested:
                        if progress.outcome == "pending":
                            progress.outcome = "failed"
                            progress.reason_code = halt.code
                            progress.counts["failed_sources"] = 1
                        failed = True
                    break
                except Exception as error:  # noqa: BLE001 - typed storage reasons
                    # R1-I010: known storage guards (e.g. SourceProjectMismatch)
                    # must surface as frozen reason codes instead of a bare
                    # null-reason failure; pending/failed counts stay visible.
                    reason = _STORAGE_ERROR_CODES.get(type(error).__name__)
                    if reason is None:
                        raise
                    if progress.outcome == "pending":
                        progress.outcome = "failed"
                        progress.reason_code = reason
                        progress.counts["failed_sources"] = 1
                    failed = True
                    break
                if progress.outcome == "failed":
                    failed = True
        except Exception:  # noqa: BLE001 - the worker always reaches a state
            failed = True
        with self._lock:
            if operation.cancel_requested:
                operation.state = "cancelled"
            elif failed:
                operation.state = "failed"
            else:
                operation.state = "completed"
            self._release_book(operation)

    def _process_source(
        self,
        operation: _Operation,
        progress: _SourceProgress,
        record: PlanRecord,
        secret_ref: object,
    ) -> None:
        source = progress.source
        if source.status in {"unsupported", "error"}:
            progress.outcome = "unsupported" if source.status == "unsupported" else "failed"
            progress.reason_code = source.reason_code
            progress.counts["failed_sources"] = 1 if source.status == "error" else 0
            progress.counts["pending_pages"] = 0
            return
        if (
            source.status == "ok"
            and source.already_referenced
            and source.will_import == 0
            and operation.duplicate_policy == "skip"
        ):
            # Whole-source skip only when EVERY importable page is bound
            # (R1-I003). A partially imported source enters the per-entry loop
            # so the remaining pages are still imported (counts unchanged).
            progress.outcome = "skipped"
            progress.counts["skipped_sources"] = 1
            progress.counts["pending_pages"] = 0
            return
        progress.counts["skipped_pages"] = 0  # accumulated per entry below

        password: bytes | None = None
        try:
            resolved = self._access.resolve(source.grant_id)
        except SourceImportError as error:
            progress.outcome = "failed"
            progress.reason_code = error.code
            progress.counts["failed_sources"] = 1
            return
        if source.status == "encrypted":
            password = self._obtain_password(resolved, source, secret_ref, progress)
            if password is None and progress.outcome == "failed":
                return

        try:
            scanned = scan_source(resolved, pdf_open=self._pdf_open, password=password)
        except SourceImportError as error:
            if error.code == "SOURCE_PASSWORD_INVALID":
                # The secret decrypted but the archive rejected the password:
                # this attempt counts toward the per-source failure budget.
                key = f"{resolved.registry_id}:{source.container_digest}"
                self._password_failures[key] = (
                    self._password_failures.get(key, 0) + 1
                )
            progress.outcome = "failed"
            progress.reason_code = error.code
            progress.counts["failed_sources"] = 1
            return

        if source.status != "encrypted":
            plan_pairs = [
                (page["locator"], page["ordinal"], page["content_digest"])
                for page in source.pages
            ]
            rescan_pairs = [
                (entry.locator, entry.ordinal, entry.content_digest)
                for entry in scanned.entries
            ]
            if plan_pairs != rescan_pairs:
                # Container changed between plan and start (C-16 §5).
                progress.outcome = "failed"
                progress.reason_code = "SOURCE_PLAN_STALE"
                progress.counts["failed_sources"] = 1
                return

        existing_source_id, existing_version_id = self._existing_metadata(scanned, resolved)
        if source.status == "encrypted":
            # R1-I004: the encrypted plan is structural-only (no entries). After
            # the password-authorized rescan the decrypted entries become the
            # participants; pending counts reflect them.
            participants = self._encrypted_participants(
                scanned, existing_source_id, existing_version_id, operation
            )
            progress.counts["pending_pages"] = sum(
                1 for page in participants if not page["already_referenced"]
            )
        else:
            participants = source.pages
        source_id = existing_source_id or f"src-{uuid.uuid4().hex}"
        version_id = existing_version_id or f"sv-{uuid.uuid4().hex}"
        metadata_committed = existing_version_id is not None
        # Entry ids for a freshly created version are allocated once so the
        # metadata rows inserted with the first page unit are exactly the
        # rows every later binding references (FK-stable within the version).
        fresh_entry_ids: dict[int, str] = {}
        if not metadata_committed:
            for item in scanned.entries:
                fresh_entry_ids[item.ordinal] = f"se-{uuid.uuid4().hex}"
        else:
            # Reusing a committed version: every participating page must map
            # to an existing entry row (natural-key retry, C-16 §4).
            for page in participants:
                if (
                    not page["already_referenced"]
                    and not page["unsupported"]
                    and page.get("entry_id") is None
                ):
                    progress.outcome = "failed"
                    progress.reason_code = "SOURCE_PLAN_STALE"
                    progress.counts["failed_sources"] = 1
                    return
        next_order = self._repository.max_source_order(operation.chapter_id)
        first_page = True
        entries_by_key = {(entry.ordinal, entry.locator): entry for entry in scanned.entries}
        for plan_page in participants:
            entry = entries_by_key.get(
                (plan_page["ordinal"], plan_page["locator"])
            )
            if entry is None:
                progress.outcome = "failed"
                progress.reason_code = "SOURCE_PLAN_STALE"
                progress.counts["failed_sources"] = 1
                return
            if plan_page["unsupported"]:
                progress.counts["pending_pages"] -= 1
                progress.counts["unsupported_entries"] += 1
                continue
            if plan_page["already_referenced"]:
                # Already excluded from the pending window at reservation
                # time; only the skip counter moves (C-16 §4 planned pages).
                progress.counts["skipped_pages"] += 1
                continue
            with self._lock:
                if operation.cancel_requested:
                    raise _HaltOperation("SOURCE_OPERATION_CANCELLED")
            try:
                # Commit-unit boundary: re-verify the grant right before the
                # page transaction (C-06 v1.1 constraint 11).
                self._access.verify_before_commit(source.grant_id)
            except SourceImportError as error:
                raise _HaltOperation(error.code) from error
            try:
                width, height, mime_type = self._probe_entry(resolved, entry, password)
            except SourceImportError as error:
                if error.code in {"SOURCE_FORMAT_UNSUPPORTED", "SOURCE_BUDGET_EXCEEDED"}:
                    progress.counts["pending_pages"] -= 1
                    progress.counts["unsupported_entries"] += 1
                    continue
                progress.outcome = "failed"
                progress.reason_code = error.code
                progress.counts["failed_sources"] = 1
                return
            next_order += 1
            final_entry_id = (
                plan_page.get("entry_id")
                if existing_version_id is not None
                else fresh_entry_ids.get(entry.ordinal)
            )
            guard = getattr(self._access, "commit_guard", None)
            try:
                with guard(source.grant_id) if guard else nullcontext():
                    self._access.verify_before_commit(source.grant_id)
                    page_id, bound_entry_id = self._commit_page_unit(
                        operation=operation,
                        resolved=resolved,
                        scanned=scanned,
                        entry=entry,
                        entry_digest=entry.content_digest,
                        width=width,
                        height=height,
                        mime_type=mime_type,
                        source_order=next_order,
                        source_id=source_id,
                        version_id=version_id,
                        insert_source=first_page and existing_source_id is None,
                        insert_metadata=first_page and existing_version_id is None,
                        fresh_entry_ids=fresh_entry_ids,
                        bound_entry_id=final_entry_id,
                    )
            except SourceImportError as error:
                raise _HaltOperation(error.code) from error
            first_page = False
            # R1-I002: bind the imported ids to the grant so the read face can
            # authorize exactly this (source, version, entry) — no path or
            # identity fallback.
            bind_entry = getattr(self._access, "bind_imported_entry", None)
            if bind_entry is not None:
                bind_entry(source.grant_id, source_id, version_id, bound_entry_id)
            progress.committed_pages += 1
            progress.committed_entries += 1
            progress.counts["pending_pages"] -= 1
            progress.counts["imported_pages"] += 1
            progress.pages.append(
                {
                    "page_id": page_id,
                    "entry_id": bound_entry_id,
                    "source_order": next_order,
                    "source_hash": entry.content_digest,
                }
            )

        if progress.outcome == "pending":
            if progress.counts["imported_pages"] > 0:
                progress.outcome = "imported"
            elif progress.counts["unsupported_entries"] > 0:
                progress.outcome = "unsupported"  # C-16 §4 ④
            else:
                progress.outcome = "skipped"  # every page already referenced

    # ------------------------------------------------------------ internals
    def _existing_metadata(self, scanned, resolved):
        if scanned.container_digest is None:
            return None, None
        existing = self._repository.find_source_by_physical_identity(
            scanned.container_digest,
            _volume_serial(resolved),
            _file_id(resolved),
        )
        if existing is None:
            return None, None
        version = self._repository.get_source_version_by_digest(
            existing["source_id"], scanned.container_digest
        )
        if version is None:
            return existing["source_id"], None
        return existing["source_id"], version["version_id"]

    def _encrypted_participants(
        self, scanned, existing_source_id, existing_version_id, operation
    ) -> list[dict]:
        """R1-I004: decrypted entries for an encrypted source (plan is empty).

        On a retry the committed version supplies entry ids; a changed entry
        set stays a typed plan-stale refusal (no silent re-import).
        """
        entry_ids: dict[int, str] = {}
        if existing_source_id is not None and existing_version_id is not None:
            for row in self._repository.list_source_entries(existing_version_id):
                entry_ids[row["ordinal"]] = row["entry_id"]
        participants: list[dict] = []
        for entry in scanned.entries:
            entry_id = entry_ids.get(entry.ordinal)
            if existing_version_id is not None and entry_id is None:
                raise SourceImportError(
                    "SOURCE_PLAN_STALE",
                    "encrypted source entries changed since the plan",
                )
            already = False
            if entry_id is not None and existing_source_id is not None:
                already = (
                    self._repository.find_current_binding_for_entry(
                        operation.book_id, existing_source_id, entry_id
                    )
                    is not None
                )
            participants.append(
                {
                    "locator": entry.locator,
                    "ordinal": entry.ordinal,
                    "size_bytes": entry.size_bytes,
                    "content_digest": entry.content_digest,
                    "content_digest_kind": entry.content_digest_kind,
                    "encrypted": entry.encrypted,
                    "entry_id": entry_id,
                    "source_id": existing_source_id,
                    "already_referenced": already,
                    "unsupported": entry.content_digest is None
                    and not entry.encrypted,
                }
            )
        return participants

    def _obtain_password(
        self,
        resolved: ResolvedSourceRead,
        source: PlannedSource,
        secret_ref: object,
        progress: _SourceProgress,
    ) -> bytes | None:
        key = f"{resolved.registry_id}:{source.container_digest}"
        if self._password_failures.get(key, 0) >= 3:
            progress.outcome = "failed"
            progress.reason_code = "SOURCE_PASSWORD_INVALID"
            progress.counts["failed_sources"] = 1
            return None
        if self._secret_reader is None or secret_ref is None:
            progress.outcome = "failed"
            progress.reason_code = "SOURCE_PASSWORD_REQUIRED"
            progress.counts["failed_sources"] = 1
            return None
        try:
            return self._secret_reader(secret_ref)
        except SourceImportError as error:
            self._password_failures[key] = self._password_failures.get(key, 0) + 1
            progress.outcome = "failed"
            progress.reason_code = error.code
            progress.counts["failed_sources"] = 1
            return None

    def _probe_entry(self, resolved, entry, password: bytes | None):
        """Decode-probe one entry for width/height/mime (no byte copies)."""
        from application.importing.referenced.reader import check_decode_budget

        if resolved.source_kind == "pdf":
            data = read_verified_bytes(
                resolved.container_path,
                resolved.container_facts,
                max_bytes=resolved.budget.max_bytes,
            )
            handle = self._pdf_open(data, password)
            try:
                width, height = handle.page_size(entry.ordinal)
                # R1-I007: budget is checked from page dimensions before any
                # raster buffer is allocated.
                check_decode_budget(resolved, int(width), int(height))
                return int(width), int(height), "application/pdf"
            finally:
                handle.close()
        payload = self._read_entry_bytes(resolved, entry, password)
        from PIL import Image

        try:
            with Image.open(io.BytesIO(payload)) as header:
                width, height = header.size
        except Exception as error:  # noqa: BLE001 - typed refusal
            raise SourceImportError(
                "SOURCE_FORMAT_UNSUPPORTED", "entry image could not be decoded"
            ) from error
        check_decode_budget(resolved, int(width), int(height))
        decoded = self._image_decoder.decode(payload)
        return decoded.width, decoded.height, decoded.mime_type

    def _read_entry_bytes(self, resolved, entry, password: bytes | None) -> bytes:
        from application.importing.referenced.reader import read_entry_bytes

        return read_entry_bytes(resolved, entry, password)

    def _commit_page_unit(
        self,
        *,
        operation,
        resolved,
        scanned,
        entry,
        entry_digest,
        width,
        height,
        mime_type,
        source_order,
        source_id,
        version_id,
        insert_source,
        insert_metadata,
        fresh_entry_ids,
        bound_entry_id,
    ):
        """One page = one SQLite transaction (C-15 §6.4 commit unit)."""
        now = _utc_now()
        final_entry_id = bound_entry_id or f"se-{uuid.uuid4().hex}"
        page_id = uuid.uuid4().hex

        entries: list[dict] | None = None
        if insert_metadata:
            entries = [
                self._entry_row(
                    source_id=source_id,
                    version_id=version_id,
                    item=item,
                    now=now,
                    bound=(item.ordinal == entry.ordinal),
                    entry_id=fresh_entry_ids.get(item.ordinal, final_entry_id),
                    container_digest=scanned.container_digest,
                    width=width,
                    height=height,
                    mime_type=mime_type,
                )
                for item in scanned.entries
            ]

        self._repository.commit_referenced_page_unit(
            page=Page(
                page_id=page_id,
                chapter_id=operation.chapter_id,
                source_filename=_safe_basename(entry.locator),
                source_order=source_order,
                sort_order=source_order,
                source_hash=entry_digest,
                source_size_bytes=entry.size_bytes,
                width=width,
                height=height,
                managed_original_ref=None,
                source_mode="referenced",
                integrity_status="complete",
                created_at=now,
                updated_at=now,
            ),
            binding={
                "binding_id": f"pb-{uuid.uuid4().hex}",
                "page_id": page_id,
                "project_id": operation.book_id,
                "binding_version": 1,
                "source_id": source_id,
                "entry_id": final_entry_id,
                "accepted_source_version": version_id,
                "status": "healthy",
                "previous_binding_id": None,
                "authorization_generation": resolved.generation,
                "authorized_at": now,
                "verified_digest": entry_digest,
                "created_at": now,
                "updated_at": now,
            },
            source=None
            if not insert_source
            else {
                "source_id": source_id,
                "source_kind": scanned.source_kind,
                "display_name": scanned.source_name[:512],
                "created_at": now,
                "updated_at": now,
            },
            location=None
            if not insert_source
            else {
                "source_id": source_id,
                "registry_id": resolved.registry_id,
                "authorization_generation": resolved.generation,
                "content_digest": scanned.container_digest,
                "volume_serial": _volume_serial(resolved),
                "file_id": _file_id(resolved),
                "size_bytes": _container_size(resolved),
                "observed_at": now,
                "created_at": now,
            },
            version=None
            if not insert_metadata
            else {
                "version_id": version_id,
                "source_id": source_id,
                "content_digest": scanned.container_digest,
                "size_bytes": _container_size(resolved),
                "observed_at": now,
                "created_at": now,
            },
            entries=entries,
        )
        return page_id, final_entry_id

    @staticmethod
    def _entry_row(
        *,
        source_id,
        version_id,
        item,
        now,
        bound,
        entry_id,
        container_digest,
        width,
        height,
        mime_type,
    ) -> dict:
        digest = item.content_digest or _synthetic_digest_placeholder(
            container_digest, item.ordinal
        )
        return {
            "source_id": source_id,
            "version_id": version_id,
            "entry_id": entry_id if entry_id else f"se-{uuid.uuid4().hex}",
            "locator": item.locator,
            "ordinal": item.ordinal,
            "stable_sort_key": _stable_key(item.locator, item.ordinal),
            "content_digest_kind": item.content_digest_kind,
            "content_digest": digest,
            "encoded_digest": digest if item.content_digest_kind == "encoded" else None,
            "pixel_digest": None,
            "pixel_digest_algorithm": None,
            "size_bytes": item.size_bytes,
            "mime_type": mime_type if bound else None,
            "width": width if bound else None,
            "height": height if bound else None,
            "orientation": None,
            "decoder_name": DECODER_NAME if bound else "",
            "decoder_version": DECODER_VERSION if bound else "",
            "decoder_params_json": "{}",
            "created_at": now,
        }

def _open_archive(data: bytes) -> zipfile.ZipFile:
    try:
        return zipfile.ZipFile(io.BytesIO(data))
    except Exception as error:  # noqa: BLE001 - container-level typed refusal
        raise SourceImportError(
            "SOURCE_FORMAT_UNSUPPORTED", "archive container is invalid"
        ) from error


def _volume_serial(resolved: ResolvedSourceRead) -> int:
    if resolved.container_facts is not None:
        return resolved.container_facts.volume_serial
    if resolved.folder_entries:
        return resolved.folder_entries[0][1].volume_serial
    return 0


def _file_id(resolved: ResolvedSourceRead) -> int:
    if resolved.container_facts is not None:
        return resolved.container_facts.file_id
    if resolved.folder_entries:
        return resolved.folder_entries[0][1].file_id
    return 0


def _container_size(resolved: ResolvedSourceRead) -> int:
    if resolved.container_facts is not None:
        return resolved.container_facts.size
    return sum(facts.size for _path, facts in resolved.folder_entries)


def _stable_key(locator: str, ordinal: int) -> str:
    from application.importing.referenced.model import stable_sort_key

    return stable_sort_key(locator, ordinal)


def _synthetic_digest_placeholder(container_digest: str | None, ordinal: int) -> str:
    """Digest placeholder for entries not decodable in this pass.

    Used only for entries the plan marked unsupported/encrypted-preview so
    the version's metadata rows stay complete; such entries never receive a
    binding and therefore never a page.
    """
    material = f"pending\0{container_digest}\0{ordinal}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def _safe_basename(locator: str) -> str:
    base = locator.rsplit("/", 1)[-1] or "entry"
    return base[:255]


def _folder_rel(path: str, root: str) -> str:
    import os

    return os.path.relpath(path, root).replace(os.sep, "/")
