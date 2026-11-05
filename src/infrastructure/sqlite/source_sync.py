"""FEA-11 SQLite storage for the C-17 v8 source-sync tables.

Everything the application service needs from the four v8 tables plus the
read/re-read projections the CAS guards compare against:

* ``source_sync_plans`` / ``source_operations`` lifecycle rows,
* ``source_binding_publications`` (durable read gates),
* ``source_revision_lineage``,
* the frozen reference-set / PageBase / region / run projections (§6.1),
* the low-level binding/page/version writers the single apply transaction
  composes (never called outside that transaction).

Every mutation here runs inside the caller's transaction; nothing commits on
its own.
"""

from __future__ import annotations

import json
import sqlite3
from typing import Any, Iterable, Sequence

from application.sources.lineage import RevisionLineageStanding
from application.sources.model import (
    digest_of,
    manual_digest_of,
    now_millis,
    reference_set_digest_of,
    run_input_digest_of,
)


def _rows(cursor: sqlite3.Cursor) -> list[dict[str, Any]]:
    return [dict(row) for row in cursor.fetchall()]


def _row(cursor: sqlite3.Cursor) -> dict[str, Any] | None:
    row = cursor.fetchone()
    return dict(row) if row is not None else None


class SourceSyncStore:
    """C-17 v8 table gateway; one instance wraps one live connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------- plans
    def insert_plan(
        self,
        *,
        plan_id: str,
        source_id: str,
        kind: str,
        plan_digest: str,
        body_json: str,
        created_at: str,
        expires_at: str,
    ) -> None:
        self._conn.execute(
            "INSERT INTO source_sync_plans (plan_id, source_id, kind, state,"
            " plan_digest, body_json, created_at, expires_at)"
            " VALUES (?, ?, ?, 'draft', ?, ?, ?, ?)",
            (plan_id, source_id, kind, plan_digest, body_json, created_at, expires_at),
        )

    def get_plan(self, plan_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT plan_id, source_id, kind, state, plan_digest, body_json,"
                " created_at, expires_at, previewed_at, confirmed_at, applied_at,"
                " stale_reason FROM source_sync_plans WHERE plan_id = ?",
                (plan_id,),
            )
        )

    def _advance_plan(
        self, plan_id: str, *, expected_state: str, sets: str, params: Sequence
    ) -> None:
        cursor = self._conn.execute(
            f"UPDATE source_sync_plans SET {sets} WHERE plan_id = ? AND state = ?",
            (*params, plan_id, expected_state),
        )
        if cursor.rowcount != 1:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "source sync plan state transition was rejected",
                details={"plan_id": plan_id},
            )

    def mark_previewed(self, plan_id: str, at: str) -> None:
        self._advance_plan(
            plan_id, expected_state="draft",
            sets="state = 'previewed', previewed_at = ?", params=(at,),
        )

    def mark_confirmed(self, plan_id: str, at: str) -> None:
        self._advance_plan(
            plan_id, expected_state="previewed",
            sets="state = 'confirmed', confirmed_at = ?", params=(at,),
        )

    def mark_applied(self, plan_id: str, at: str) -> None:
        self._advance_plan(
            plan_id, expected_state="confirmed",
            sets="state = 'applied', applied_at = ?", params=(at,),
        )

    def mark_stale(self, plan_id: str, reason: str, at: str) -> None:
        from application.sources.errors import SourceSyncError

        row = self.get_plan(plan_id)
        if row is None:
            raise SourceSyncError(
                "SOURCE_OPERATION_NOT_FOUND",
                "source sync plan was not found",
                details={"plan_id": plan_id},
            )
        if row["state"] == "applied":
            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "an applied plan cannot be invalidated",
                details={"plan_id": plan_id},
            )
        if row["state"] == "stale":
            return
        self._conn.execute(
            "UPDATE source_sync_plans SET state = 'stale', stale_reason = ?"
            " WHERE plan_id = ?",
            (reason, plan_id),
        )
        del at

    # -------------------------------------------------------- operations
    def find_operation(self, operation_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT operation_id, plan_id, plan_digest, kind, request_digest,"
                " state, authorization_digest, authorization_json,"
                " host_receipt_id, commit_receipt_json, commit_digest,"
                " error_code, retryable, created_at, updated_at, committed_at,"
                " acknowledged_at FROM source_operations WHERE operation_id = ?",
                (operation_id,),
            )
        )

    def find_operation_by_plan(self, plan_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT operation_id, plan_id, plan_digest, kind, request_digest,"
                " state, authorization_digest, authorization_json,"
                " host_receipt_id, commit_receipt_json, commit_digest,"
                " error_code, retryable, created_at, updated_at, committed_at,"
                " acknowledged_at FROM source_operations WHERE plan_id = ?",
                (plan_id,),
            )
        )

    def insert_operation(
        self,
        *,
        operation_id: str,
        plan_id: str,
        plan_digest: str,
        kind: str,
        request_digest: str,
        authorization_digest: str,
        authorization_json: str,
        host_receipt_id: str,
        now: str,
    ) -> None:
        self._conn.execute(
            "INSERT INTO source_operations (operation_id, plan_id, plan_digest,"
            " kind, request_digest, state, authorization_digest,"
            " authorization_json, host_receipt_id, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, 'host-authorized', ?, ?, ?, ?, ?)",
            (
                operation_id, plan_id, plan_digest, kind, request_digest,
                authorization_digest, authorization_json, host_receipt_id,
                now, now,
            ),
        )

    def commit_operation(
        self,
        operation_id: str,
        *,
        commit_receipt_json: str,
        commit_digest: str,
        now: str,
    ) -> None:
        """host-authorized → core-committed (inside the apply transaction)."""
        cursor = self._conn.execute(
            "UPDATE source_operations SET state = 'core-committed',"
            " commit_receipt_json = ?, commit_digest = ?, committed_at = ?,"
            " updated_at = ? WHERE operation_id = ? AND state = 'host-authorized'",
            (commit_receipt_json, commit_digest, now, now, operation_id),
        )
        if cursor.rowcount != 1:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "operation commit transition was rejected",
                details={"operation_id": operation_id},
            )

    def acknowledge_operation(self, operation_id: str, now: str) -> None:
        cursor = self._conn.execute(
            "UPDATE source_operations SET state = 'acknowledged',"
            " acknowledged_at = ?, updated_at = ? WHERE operation_id = ?"
            " AND state = 'core-committed'",
            (now, now, operation_id),
        )
        if cursor.rowcount != 1:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "operation acknowledge transition was rejected",
                details={"operation_id": operation_id},
            )

    def recover_operation(self, operation_id: str, now: str) -> None:
        cursor = self._conn.execute(
            "UPDATE source_operations SET state = 'recovered',"
            " acknowledged_at = ?, error_code = NULL, retryable = 0,"
            " updated_at = ? WHERE operation_id = ?"
            " AND state IN ('core-committed', 'failed')",
            (now, now, operation_id),
        )
        if cursor.rowcount != 1:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "operation recovery transition was rejected",
                details={"operation_id": operation_id},
            )

    def fail_operation(
        self, operation_id: str, *, code: str, retryable: bool, now: str
    ) -> None:
        cursor = self._conn.execute(
            "UPDATE source_operations SET state = 'failed', error_code = ?,"
            " retryable = ?, updated_at = ? WHERE operation_id = ?"
            " AND state IN ('core-committed', 'host-authorized')",
            (code, 1 if retryable else 0, now, operation_id),
        )
        if cursor.rowcount != 1:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "operation failure transition was rejected",
                details={"operation_id": operation_id},
            )

    # ------------------------------------------------------ publications
    def insert_publication(
        self,
        *,
        binding_id: str,
        operation_id: str,
        previous_binding_id: str | None,
        relation: str,
    ) -> None:
        self._conn.execute(
            "INSERT INTO source_binding_publications (binding_id, operation_id,"
            " previous_binding_id, relation, read_gate) VALUES (?, ?, ?, ?,"
            " 'pending')",
            (binding_id, operation_id, previous_binding_id, relation),
        )

    def open_gates(self, operation_id: str, now: str) -> int:
        cursor = self._conn.execute(
            "UPDATE source_binding_publications SET read_gate = 'open',"
            " opened_at = ? WHERE operation_id = ? AND read_gate = 'pending'",
            (now, operation_id),
        )
        return cursor.rowcount

    def gate_of_binding(self, binding_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT binding_id, operation_id, previous_binding_id, relation,"
                " read_gate, opened_at FROM source_binding_publications"
                " WHERE binding_id = ?",
                (binding_id,),
            )
        )

    def pending_gate_pages(self, page_ids: Iterable[str]) -> set[str]:
        """Pages whose current binding still has a pending read gate."""
        ids = list(page_ids)
        if not ids:
            return set()
        marks = ",".join("?" for _ in ids)
        rows = _rows(
            self._conn.execute(
                "SELECT b.page_id AS page_id FROM page_bindings b"
                " JOIN source_binding_publications p"
                " ON p.binding_id = b.binding_id"
                f" WHERE b.page_id IN ({marks}) AND p.read_gate = 'pending'"
                " AND b.status <> 'superseded'",
                ids,
            )
        )
        return {row["page_id"] for row in rows}

    # ---------------------------------------------------------- lineage
    def insert_lineage(
        self,
        *,
        revision_id: str,
        region_id: str,
        binding_id: str | None,
        provenance: str,
        from_revision_id: str | None = None,
        operation_id: str | None = None,
        now: str | None = None,
    ) -> None:
        self._conn.execute(
            "INSERT INTO source_revision_lineage (revision_id, region_id,"
            " binding_id, provenance, from_revision_id, operation_id, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                revision_id, region_id, binding_id, provenance,
                from_revision_id, operation_id, now or now_millis(),
            ),
        )

    def lineage_of_revision(self, revision_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT revision_id, region_id, binding_id, provenance,"
                " from_revision_id, operation_id, created_at"
                " FROM source_revision_lineage WHERE revision_id = ?",
                (revision_id,),
            )
        )

    def lineage_for_binding(self, binding_id: str) -> list[dict[str, Any]]:
        return _rows(
            self._conn.execute(
                "SELECT revision_id, region_id, provenance, from_revision_id,"
                " operation_id FROM source_revision_lineage"
                " WHERE binding_id = ? ORDER BY region_id, revision_id",
                (binding_id,),
            )
        )

    def lineage_exists_for_regions(self, region_ids: Sequence[str]) -> set[str]:
        if not region_ids:
            return set()
        marks = ",".join("?" for _ in region_ids)
        rows = _rows(
            self._conn.execute(
                "SELECT region_id FROM source_revision_lineage"
                f" WHERE region_id IN ({marks})",
                list(region_ids),
            )
        )
        return {row["region_id"] for row in rows}

    def sync_managed_page_ids(self) -> list[str]:
        """Pages whose binding chain carries a sync publication (C-17 §7.1
        "本卡涉及的同步页"). The first sync switch creates the publication
        row; imported-but-never-synced pages have none."""
        return [
            row["page_id"]
            for row in _rows(
                self._conn.execute(
                    "SELECT DISTINCT b.page_id AS page_id FROM page_bindings b"
                    " JOIN source_binding_publications p"
                    " ON p.binding_id = b.binding_id"
                    " ORDER BY b.page_id"
                )
            )
        ]

    #: FEA-11-LINEAGE-1: chunk bound for the backfill IN-list.
    _BACKFILL_CHUNK = 500

    def backfill_legacy_unverified_lineage(self, *, now: str | None = None) -> int:
        """Stock backfill: every revision WITHOUT a lineage row on an
        already-synced page becomes ``legacy_unverified`` (binding NULL).

        Rules (C-17 §7.1 / r1 P0-1):
        * never guesses an attribution — no ``captured_v7``/``native`` is
          fabricated, only the honest "unverified" row;
        * no-op for the same rows on every call (idempotent);
        * limited to pages that already carry publication history: a page
          that has NOT been switched yet must keep its missing rows so the
          first switch can still capture its current revision as
          ``captured_v7`` inside that switch transaction.

        Runs inside the caller's transaction; returns the inserted row count.
        """
        page_ids = self.sync_managed_page_ids()
        if not page_ids:
            return 0
        created_at = now or now_millis()
        inserted = 0
        for start in range(0, len(page_ids), self._BACKFILL_CHUNK):
            chunk = page_ids[start : start + self._BACKFILL_CHUNK]
            marks = ",".join("?" for _ in chunk)
            cursor = self._conn.execute(
                "INSERT INTO source_revision_lineage (revision_id, region_id,"
                " binding_id, provenance, from_revision_id, operation_id,"
                " created_at)"
                " SELECT rr.region_revision_id, rr.region_id, NULL,"
                " 'legacy_unverified', NULL, NULL, ?"
                " FROM region_revisions rr"
                " JOIN regions r ON r.region_id = rr.region_id"
                f" WHERE r.page_id IN ({marks})"
                " AND NOT EXISTS (SELECT 1 FROM source_revision_lineage l"
                " WHERE l.revision_id = rr.region_revision_id)",
                (created_at, *chunk),
            )
            inserted += cursor.rowcount
        return inserted

    # -------------------------------------------- reference projections
    def list_source_references(
        self, source_id: str, project_ids: Sequence[str] | None = None
    ) -> list[dict[str, Any]]:
        """The frozen reference set (C-17 §5.3): every non-superseded binding
        of ``source_id``, soft-deleted pages included. ``project_ids=None``
        returns the whole-source set (the scope=all digest universe); a
        sequence narrows it for the decision scope."""
        if project_ids is not None and not project_ids:
            return []
        columns = (
            "SELECT b.project_id AS project, b.page_id AS page,"
            " b.binding_id AS binding, b.accepted_source_version AS version,"
            " b.status AS status,"
            " CASE WHEN p.deleted_at IS NULL THEN 0 ELSE 1 END AS deleted,"
            " b.binding_version AS binding_version, b.entry_id AS entry_id,"
            " b.previous_binding_id AS previous_binding_id,"
            " b.authorization_generation AS authorization_generation,"
            " b.verified_digest AS verified_digest"
            " FROM page_bindings b JOIN pages p ON p.page_id = b.page_id"
            " WHERE b.source_id = ? AND b.status <> 'superseded'"
        )
        if project_ids is None:
            return _rows(
                self._conn.execute(
                    columns + " ORDER BY b.project_id, p.sort_order, b.page_id",
                    (source_id,),
                )
            )
        marks = ",".join("?" for _ in project_ids)
        return _rows(
            self._conn.execute(
                columns
                + f" AND b.project_id IN ({marks})"
                + " ORDER BY b.project_id, p.sort_order, b.page_id",
                (source_id, *project_ids),
            )
        )

    @staticmethod
    def reference_set_digest(references: list[dict[str, Any]]) -> str:
        rows = [
            {
                "project": row["project"],
                "page": row["page"],
                "binding": row["binding"],
                "version": row["version"],
                "status": row["status"],
                "deleted": bool(row["deleted"]),
            }
            for row in references
        ]
        return reference_set_digest_of(rows)

    def page_base_row(self, page_id: str) -> dict[str, Any] | None:
        """The PageBase projection for one referenced page (§5.2)."""
        return _row(
            self._conn.execute(
                "SELECT p.page_id AS page_id, b.project_id AS project_id,"
                " p.chapter_id AS chapter_id, b.binding_id AS binding_id,"
                " b.binding_version AS binding_version, b.source_id AS source_id,"
                " b.accepted_source_version AS version_id, b.entry_id AS entry_id,"
                " p.source_order AS source_order, p.sort_order AS sort_order,"
                " CASE WHEN p.deleted_at IS NULL THEN 0 ELSE 1 END AS deleted,"
                " b.status AS binding_status"
                " FROM pages p JOIN page_bindings b ON b.page_id = p.page_id"
                " WHERE p.page_id = ? AND b.status <> 'superseded'",
                (page_id,),
            )
        )

    def regions_manual_projection(self, page_id: str) -> list[dict[str, Any]]:
        """C-17 §6.1 manual-digest material for every region of one page."""
        return _rows(
            self._conn.execute(
                "SELECT r.region_id AS region_id, r.current_revision_id"
                " AS current_revision_id, rr.revision_no AS revision_no,"
                " r.geometry_json AS geometry_json, r.text_json AS text_json,"
                " r.style_json AS style_json, r.deleted_at AS deleted_at,"
                " r.region_locked AS region_locked,"
                " r.translation_locked AS translation_locked,"
                " r.inpaint_locked AS inpaint_locked, p.page_locked AS page_locked"
                " FROM regions r"
                " LEFT JOIN region_revisions rr"
                " ON rr.region_revision_id = r.current_revision_id"
                " JOIN pages p ON p.page_id = r.page_id"
                " WHERE r.page_id = ? ORDER BY r.region_id",
                (page_id,),
            )
        )

    @staticmethod
    def manual_digest(rows: list[dict[str, Any]]) -> str:
        material = [
            {
                "region_id": row["region_id"],
                "current_revision_id": row["current_revision_id"],
                "revision_no": row["revision_no"],
                "geometry_json": row["geometry_json"],
                "text_json": row["text_json"],
                "style_json": row["style_json"],
                "deleted_at": row["deleted_at"],
            }
            for row in rows
        ]
        return manual_digest_of(material)

    @staticmethod
    def protection_digest(rows: list[dict[str, Any]]) -> str:
        material = [
            {
                "region_id": row["region_id"],
                "region_locked": row["region_locked"],
                "translation_locked": row["translation_locked"],
                "inpaint_locked": row["inpaint_locked"],
                "page_locked": row["page_locked"],
                "current_revision_id": row["current_revision_id"],
                "deleted_at": row["deleted_at"],
            }
            for row in rows
        ]
        return digest_of(material)

    def run_projection(self, page_ids: Sequence[str]) -> list[dict[str, Any]]:
        """In-flight/queued run targets bound to the given pages."""
        if not page_ids:
            return []
        marks = ",".join("?" for _ in page_ids)
        return _rows(
            self._conn.execute(
                "SELECT t.pipeline_run_id AS run_id, t.page_id AS target_page_id,"
                " r.status AS status FROM pipeline_run_targets t"
                " JOIN pipeline_runs r ON r.run_id = t.pipeline_run_id"
                f" WHERE t.page_id IN ({marks}) ORDER BY t.pipeline_run_id,"
                " t.page_id",
                list(page_ids),
            )
        )

    @staticmethod
    def runs_digest(rows: list[dict[str, Any]]) -> str:
        return run_input_digest_of(
            [
                {
                    "run_id": row["run_id"],
                    "target_page_id": row["target_page_id"],
                    "status": row["status"],
                }
                for row in rows
            ]
        )

    def drafts_projection(self, page_ids: Sequence[str]) -> list[dict[str, Any]]:
        """Draft journal projection: open step-result candidates bound to the
        plan's pages (the durable in-flight work the Core can see)."""
        if not page_ids:
            return []
        marks = ",".join("?" for _ in page_ids)
        return _rows(
            self._conn.execute(
                "SELECT candidate_id, page_id, status, reason,"
                " base_revision_id, created_at FROM step_result_candidates"
                f" WHERE page_id IN ({marks}) AND resolved_at IS NULL"
                " ORDER BY candidate_id",
                list(page_ids),
            )
        )

    @staticmethod
    def drafts_digest(rows: list[dict[str, Any]]) -> str:
        material = [
            {
                "candidate_id": row["candidate_id"],
                "page_id": row["page_id"],
                "status": row["status"],
                "base_revision_id": row["base_revision_id"],
            }
            for row in rows
        ]
        return digest_of(material)

    # ------------------------------------------------- binding re-reads
    def get_binding(self, binding_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT binding_id, page_id, project_id, binding_version,"
                " source_id, entry_id, accepted_source_version, status,"
                " previous_binding_id, authorization_generation,"
                " authorized_at, verified_digest, created_at, updated_at"
                " FROM page_bindings WHERE binding_id = ?",
                (binding_id,),
            )
        )

    def current_binding_of_page(self, page_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT binding_id, page_id, project_id, binding_version,"
                " source_id, entry_id, accepted_source_version, status,"
                " previous_binding_id, authorization_generation,"
                " authorized_at, verified_digest FROM page_bindings"
                " WHERE page_id = ? AND status <> 'superseded'",
                (page_id,),
            )
        )

    def get_source_version_row(
        self, source_id: str, version_id: str
    ) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT version_id, source_id, location_id, content_digest,"
                " size_bytes, observed_at, superseded_at FROM source_versions"
                " WHERE source_id = ? AND version_id = ?",
                (source_id, version_id),
            )
        )

    def latest_source_version(self, source_id: str) -> dict[str, Any] | None:
        """The source's newest observed version (current content identity)."""
        return _row(
            self._conn.execute(
                "SELECT version_id, source_id, location_id, content_digest,"
                " size_bytes, observed_at, superseded_at FROM source_versions"
                " WHERE source_id = ? ORDER BY observed_at DESC, created_at"
                " DESC LIMIT 1",
                (source_id,),
            )
        )

    def get_source_location_current(self, source_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT location_id, source_id, registry_id,"
                " authorization_generation, content_digest, volume_serial,"
                " file_id, size_bytes, mtime_hint, observed_at"
                " FROM source_locations WHERE source_id = ? AND is_current = 1",
                (source_id,),
            )
        )

    def list_entries_of_version(self, version_id: str) -> list[dict[str, Any]]:
        return _rows(
            self._conn.execute(
                "SELECT source_id, version_id, entry_id, locator, ordinal,"
                " stable_sort_key, content_digest_kind, content_digest,"
                " encoded_digest, pixel_digest, pixel_digest_algorithm,"
                " size_bytes, mime_type, width, height, orientation,"
                " decoder_name, decoder_version, decoder_params_json"
                " FROM source_entries WHERE version_id = ? ORDER BY ordinal",
                (version_id,),
            )
        )

    # -------------------------------------------------------- writers
    def supersede_binding(self, binding_id: str, now: str) -> None:
        self._conn.execute(
            "UPDATE page_bindings SET status = 'superseded', updated_at = ?"
            " WHERE binding_id = ? AND status <> 'superseded'",
            (now, binding_id),
        )

    def mark_binding_missing(self, binding_id: str, now: str) -> None:
        cursor = self._conn.execute(
            "UPDATE page_bindings SET status = 'missing', updated_at = ?"
            " WHERE binding_id = ? AND status NOT IN ('superseded', 'missing')",
            (now, binding_id),
        )
        if cursor.rowcount != 1:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_SYNC_STATE_CONFLICT",
                "binding missing transition was rejected",
            )

    def insert_page(self, page: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename,"
            " source_order, sort_order, source_hash, source_size_bytes, width,"
            " height, managed_original_ref, page_locked, review_state,"
            " overall_status, created_at, updated_at, deleted_at, source_mode,"
            " integrity_status)"
            " VALUES (:page_id, :chapter_id, :source_filename, :source_order,"
            " :sort_order, :source_hash, :source_size_bytes, :width, :height,"
            " :managed_original_ref, :page_locked, :review_state,"
            " :overall_status, :created_at, :updated_at, :deleted_at,"
            " :source_mode, :integrity_status)",
            page,
        )

    def insert_binding(self, binding: dict[str, Any]) -> None:
        """Insert a binding with the frozen book-ownership guard."""
        row = _row(
            self._conn.execute(
                "SELECT c.book_id FROM pages p JOIN chapters c"
                " ON c.chapter_id = p.chapter_id WHERE p.page_id = ?",
                (binding["page_id"],),
            )
        )
        if row is None or row["book_id"] != binding["project_id"]:
            from application.sources.errors import SourceSyncError

            raise SourceSyncError(
                "SOURCE_PROJECT_MISMATCH",
                "page->chapter->book does not match the binding project",
            )
        self._conn.execute(
            "INSERT INTO page_bindings (binding_id, page_id, project_id,"
            " binding_version, source_id, entry_id, accepted_source_version,"
            " status, previous_binding_id, authorization_generation,"
            " authorized_at, verified_digest, created_at, updated_at)"
            " VALUES (:binding_id, :page_id, :project_id, :binding_version,"
            " :source_id, :entry_id, :accepted_source_version, :status,"
            " :previous_binding_id, :authorization_generation, :authorized_at,"
            " :verified_digest, :created_at, :updated_at)",
            binding,
        )

    def insert_source_version_row(self, version: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO source_versions (version_id, source_id, location_id,"
            " content_digest, size_bytes, observed_at, created_at)"
            " VALUES (:version_id, :source_id, :location_id, :content_digest,"
            " :size_bytes, :observed_at, :created_at)",
            version,
        )

    def insert_source_entry_rows(self, entries: Sequence[dict[str, Any]]) -> None:
        self._conn.executemany(
            "INSERT INTO source_entries (source_id, version_id, entry_id,"
            " locator, ordinal, stable_sort_key, content_digest_kind,"
            " content_digest, encoded_digest, pixel_digest,"
            " pixel_digest_algorithm, size_bytes, mime_type, width, height,"
            " orientation, decoder_name, decoder_version, decoder_params_json,"
            " created_at) VALUES (:source_id, :version_id, :entry_id, :locator,"
            " :ordinal, :stable_sort_key, :content_digest_kind,"
            " :content_digest, :encoded_digest, :pixel_digest,"
            " :pixel_digest_algorithm, :size_bytes, :mime_type, :width,"
            " :height, :orientation, :decoder_name, :decoder_version,"
            " :decoder_params_json, :created_at)",
            [dict(entry) for entry in entries],
        )

    def insert_source_location_row(self, location: dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO source_locations (location_id, source_id, registry_id,"
            " authorization_generation, content_digest, volume_serial, file_id,"
            " size_bytes, mtime_hint, observed_at, created_at)"
            " VALUES (:location_id, :source_id, :registry_id,"
            " :authorization_generation, :content_digest, :volume_serial,"
            " :file_id, :size_bytes, :mtime_hint, :observed_at, :created_at)",
            location,
        )

    def update_page_order(
        self, page_id: str, *, source_order: int, sort_order: int, now: str
    ) -> None:
        self._conn.execute(
            "UPDATE pages SET source_order = ?, sort_order = ?, updated_at = ?"
            " WHERE page_id = ?",
            (source_order, sort_order, now, page_id),
        )

    def max_sort_order(self, chapter_id: str) -> int:
        row = _row(
            self._conn.execute(
                "SELECT COALESCE(MAX(sort_order), -1) AS value FROM pages"
                " WHERE chapter_id = ?",
                (chapter_id,),
            )
        )
        return int(row["value"]) if row is not None else -1

    # -------------------------------------------------- revision migration
    def get_region(self, region_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT region_id, page_id, region_type, reading_order,"
                " geometry_json, text_json, style_json, sfx_policy,"
                " region_locked, translation_locked, inpaint_locked,"
                " current_revision_id, created_at, updated_at, deleted_at"
                " FROM regions WHERE region_id = ?",
                (region_id,),
            )
        )

    def get_revision(self, revision_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT region_revision_id, region_id, revision_no,"
                " snapshot_json, origin, review_state, is_pinned, source_run_id,"
                " source_step_run_id, restored_from_revision_id, created_at"
                " FROM region_revisions WHERE region_revision_id = ?",
                (revision_id,),
            )
        )

    def next_revision_no(self, region_id: str) -> int:
        row = _row(
            self._conn.execute(
                "SELECT COALESCE(MAX(revision_no), 0) + 1 AS value"
                " FROM region_revisions WHERE region_id = ?",
                (region_id,),
            )
        )
        return int(row["value"])

    def insert_migrated_revision(
        self,
        *,
        revision_id: str,
        region_id: str,
        revision_no: int,
        snapshot_json: str,
        now: str,
    ) -> None:
        """Insert the migrated copy of an old current revision (C-17 §7.1:
        new revision row, old row untouched)."""
        self._conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id,"
            " revision_no, snapshot_json, origin, review_state, is_pinned,"
            " created_at) VALUES (?, ?, ?, ?, 'imported', 'confirmed', 0, ?)",
            (revision_id, region_id, revision_no, snapshot_json, now),
        )

    def set_region_current_revision(
        self, region_id: str, revision_id: str, now: str
    ) -> None:
        self._conn.execute(
            "UPDATE regions SET current_revision_id = ?, updated_at = ?"
            " WHERE region_id = ?",
            (revision_id, now, region_id),
        )

    # ------------------------------------------------------- diagnostics
    def tombstone_pages_of_source(
        self, source_id: str, project_ids: Sequence[str]
    ) -> list[dict[str, Any]]:
        """Diagnostic projection: pages of this source whose binding is
        missing (AC11-7) — management-facing, does not change visibility."""
        if not project_ids:
            return []
        marks = ",".join("?" for _ in project_ids)
        return _rows(
            self._conn.execute(
                "SELECT b.page_id, b.project_id, b.binding_id, b.status,"
                " p.deleted_at FROM page_bindings b"
                " JOIN pages p ON p.page_id = b.page_id"
                " WHERE b.source_id = ? AND b.status = 'missing'"
                f" AND b.project_id IN ({marks})",
                [source_id, *project_ids],
            )
        )


class SourceSyncLineageFacts:
    """FEA-11-LINEAGE-1: the C-17 §7.1 facts the isolation guard consumes.

    One instance wraps one live connection; every query is read-only and
    observes the caller's open transaction, so the guard can run INSIDE the
    revision commit transaction (a concurrent sync switch cannot slip
    between the check and the lineage write).
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def page_binding(self, page_id: str) -> str | None:
        row = _row(
            self._conn.execute(
                "SELECT binding_id FROM page_bindings WHERE page_id = ?"
                " AND status <> 'superseded'",
                (page_id,),
            )
        )
        return row["binding_id"] if row is not None else None

    def page_is_sync_managed(self, page_id: str) -> bool:
        """True when any binding of the page's own chain has a publication."""
        binding_id = self.page_binding(page_id)
        seen: set[str] = set()
        while binding_id is not None and binding_id not in seen:
            seen.add(binding_id)
            if self._publication_of(binding_id) is not None:
                return True
            row = _row(
                self._conn.execute(
                    "SELECT previous_binding_id FROM page_bindings"
                    " WHERE binding_id = ?",
                    (binding_id,),
                )
            )
            binding_id = row["previous_binding_id"] if row is not None else None
        return False

    def revision_lineages(
        self, revision_ids: Sequence[str]
    ) -> dict[str, RevisionLineageStanding]:
        ids = list(dict.fromkeys(revision_id for revision_id in revision_ids if revision_id))
        if not ids:
            return {}
        marks = ",".join("?" for _ in ids)
        rows = _rows(
            self._conn.execute(
                "SELECT revision_id, region_id, binding_id, provenance"
                " FROM source_revision_lineage"
                f" WHERE revision_id IN ({marks})",
                ids,
            )
        )
        return {
            row["revision_id"]: RevisionLineageStanding(
                binding_id=row["binding_id"],
                provenance=row["provenance"],
                # FEA-11-LINEAGE-1 r3 (R2-05): the row's own region attribution.
                region_id=row["region_id"],
            )
            for row in rows
        }

    def same_content_reachable(
        self, current_binding_id: str, ancestor_binding_id: str
    ) -> bool:
        """Walk ``publication.previous`` crossing ``same_content`` edges only.

        ``changed`` / ``repoint`` / ``missing`` cut the walk (C-17 §7.1).
        """
        binding_id: str | None = current_binding_id
        seen: set[str] = set()
        while binding_id is not None and binding_id not in seen:
            if binding_id == ancestor_binding_id:
                return True
            seen.add(binding_id)
            publication = self._publication_of(binding_id)
            if publication is None or publication["relation"] != "same_content":
                return False
            binding_id = publication["previous_binding_id"]
        return False

    def _publication_of(self, binding_id: str) -> dict[str, Any] | None:
        return _row(
            self._conn.execute(
                "SELECT binding_id, previous_binding_id, relation"
                " FROM source_binding_publications WHERE binding_id = ?",
                (binding_id,),
            )
        )


def decode_json(text: str) -> Any:
    return json.loads(text)
