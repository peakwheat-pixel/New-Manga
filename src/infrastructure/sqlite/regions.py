"""SQLite adapter for regions and their revision history (TASK-029, per the
frozen TASK-028 design §3.4/§4.2).

``commit_region_revision`` is the atomic "region state + revision + current
pointer" seam: one ``BEGIN IMMEDIATE`` re-reads current and the locks,
compares the caller's expectation, inserts the immutable revision, syncs the
revision-owned region state from its snapshot and updates the pointer —
rolling back entirely on mismatch or database failure. ``set_revision_pinned``
is a separate single-statement transaction that touches ``is_pinned`` only.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone

from application.editing.ports import (
    RegionCommitResult,
    RegionCommitStatus,
    RegionLockSnapshot,
)
from domain.regions.entities import (
    Region,
    RegionGeometry,
    RegionOrigin,
    RegionRevision,
    RegionText,
    RegionType,
    ReviewState,
    SfxPolicy,
    TextStyle,
)

_REGION_COLUMNS = (
    "region_id, page_id, region_type, reading_order, geometry_json, text_json,"
    " style_json, sfx_policy, region_locked, translation_locked, inpaint_locked,"
    " current_revision_id, created_at, updated_at, deleted_at"
)


class SqliteRegionRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # row mapping
    # ------------------------------------------------------------------

    def _region_from_row(self, row: sqlite3.Row) -> Region:
        region = Region(
            region_id=row["region_id"],
            page_id=row["page_id"],
            region_type=RegionType(row["region_type"]),
            reading_order=row["reading_order"],
            sfx_policy=SfxPolicy(row["sfx_policy"]),
            region_locked=bool(row["region_locked"]),
            translation_locked=bool(row["translation_locked"]),
            inpaint_locked=bool(row["inpaint_locked"]),
            current_revision_id=row["current_revision_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"],
        )
        region.geometry = RegionGeometry.from_jsonable(json.loads(row["geometry_json"]))
        text_state = json.loads(row["text_json"])
        region.text = RegionText(
            ocr_text=text_state["ocr_text"],
            machine_translation=text_state["machine_translation"],
            edited_translation=text_state["edited_translation"],
            final_translation=text_state["final_translation"],
            final_source=text_state["final_source"],
            edited_confirmed=text_state["edited_confirmed"],
            manual_edited=text_state["manual_edited"],
            translation_locked=text_state["translation_locked"],
        )
        region.style = TextStyle.from_jsonable(json.loads(row["style_json"]))
        return region

    def _revision_from_row(self, row: sqlite3.Row) -> RegionRevision:
        return RegionRevision(
            region_revision_id=row["region_revision_id"],
            region_id=row["region_id"],
            revision_no=row["revision_no"],
            snapshot=json.loads(row["snapshot_json"]),
            origin=RegionOrigin(row["origin"]),
            review_state=ReviewState(row["review_state"]),
            is_pinned=bool(row["is_pinned"]),
            source_run_id=row["source_run_id"],
            source_step_run_id=row["source_step_run_id"],
            restored_from_revision_id=row["restored_from_revision_id"],
            created_at=row["created_at"],
        )

    @staticmethod
    def _region_write_values(region: Region) -> tuple:
        """Revision-owned state, serialized from the snapshot contract."""
        snapshot = region.snapshot_state()
        return (
            region.page_id,
            snapshot["region_type"],
            snapshot["reading_order"],
            json.dumps(snapshot["geometry"], ensure_ascii=False, sort_keys=True),
            json.dumps(snapshot["text"], ensure_ascii=False, sort_keys=True),
            json.dumps(snapshot["style"], ensure_ascii=False, sort_keys=True),
            snapshot["sfx_policy"],
            int(snapshot["region_locked"]),
            int(snapshot["translation_locked"]),
            int(snapshot["inpaint_locked"]),
        )

    # ------------------------------------------------------------------
    # RegionRepository
    # ------------------------------------------------------------------

    def add_region(self, region: Region) -> None:
        with self._conn:
            self._conn.execute(
                "INSERT INTO regions (" + _REGION_COLUMNS + ")"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    region.region_id, region.page_id, region.region_type.value,
                    region.reading_order,
                    json.dumps(region.geometry.as_jsonable(), ensure_ascii=False, sort_keys=True),
                    json.dumps(_text_jsonable(region.text), ensure_ascii=False, sort_keys=True),
                    json.dumps(region.style.as_jsonable(), ensure_ascii=False, sort_keys=True),
                    region.sfx_policy.value, int(region.region_locked),
                    int(region.translation_locked), int(region.inpaint_locked),
                    region.current_revision_id, region.created_at,
                    region.updated_at, region.deleted_at,
                ),
            )

    def get_region(self, region_id: str) -> Region | None:
        row = self._conn.execute(
            "SELECT " + _REGION_COLUMNS + " FROM regions WHERE region_id = ?",
            (region_id,),
        ).fetchone()
        return self._region_from_row(row) if row else None

    def list_regions(self, page_id: str) -> list[Region]:
        rows = self._conn.execute(
            "SELECT " + _REGION_COLUMNS + " FROM regions WHERE page_id = ?",
            (page_id,),
        ).fetchall()
        return [self._region_from_row(row) for row in rows]

    def update_region(self, region: Region) -> None:
        """Non-revision-owned region writes (soft delete timestamps)."""
        with self._conn:
            self._conn.execute(
                "UPDATE regions SET deleted_at = ?, updated_at = ? WHERE region_id = ?",
                (region.deleted_at, region.updated_at, region.region_id),
            )

    def soft_delete_region(self, region_id: str) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE regions SET deleted_at = ? WHERE region_id = ?",
                (_utc_now(), region_id),
            )

    def add_revision(self, revision: RegionRevision) -> None:
        """Explicit new-history insert only; never touches the pointer."""
        with self._conn:
            self._insert_revision(revision)

    def list_revisions(self, region_id: str) -> list[RegionRevision]:
        rows = self._conn.execute(
            "SELECT * FROM region_revisions WHERE region_id = ? ORDER BY revision_no",
            (region_id,),
        ).fetchall()
        return [self._revision_from_row(row) for row in rows]

    def get_revision(self, region_id: str, revision_no: int) -> RegionRevision | None:
        row = self._conn.execute(
            "SELECT * FROM region_revisions WHERE region_id = ? AND revision_no = ?",
            (region_id, revision_no),
        ).fetchone()
        return self._revision_from_row(row) if row else None

    def set_revision_pinned(self, region_id: str, revision_no: int, pinned: bool) -> None:
        """TASK-028 §4.2: pin touches is_pinned only — no same-id upsert of
        the immutable snapshot."""
        with self._conn:
            cursor = self._conn.execute(
                "UPDATE region_revisions SET is_pinned = ?"
                " WHERE region_id = ? AND revision_no = ?",
                (int(pinned), region_id, revision_no),
            )
            if cursor.rowcount == 0:
                raise LookupError(
                    f"revision {revision_no} not found for region {region_id}"
                )

    # ------------------------------------------------------------------
    # atomic seam (TASK-028 §4.2)
    # ------------------------------------------------------------------

    def commit_region_revision(
        self,
        region: Region,
        revision: RegionRevision,
        *,
        expected_current_revision_id: str | None = None,
        lock_snapshot: RegionLockSnapshot | None = None,
    ) -> RegionCommitResult:
        conn = self._conn
        # TASK-060 Q-002: BEGIN IMMEDIATE sits inside the try so a lock or
        # transaction failure (busy_timeout exhaustion, another writer's
        # IMMEDIATE) surfaces as the typed DB_FAILED result instead of a
        # raw sqlite3.OperationalError reaching the VM/QML.
        try:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT current_revision_id, region_locked, translation_locked,"
                " inpaint_locked FROM regions WHERE region_id = ?",
                (region.region_id,),
            ).fetchone()
            if row is None:
                conn.rollback()
                return RegionCommitResult(
                    RegionCommitStatus.DB_FAILED,
                    detail=f"region {region.region_id} disappeared mid-commit",
                )

            current = row["current_revision_id"]
            if (
                expected_current_revision_id is not None
                and current != expected_current_revision_id
            ):
                conn.rollback()
                return RegionCommitResult(
                    RegionCommitStatus.INPUT_REVISION_CHANGED,
                    detail=(
                        f"expected current {expected_current_revision_id!r},"
                        f" stored current {current!r}"
                    ),
                )

            if lock_snapshot is not None:
                stored = RegionLockSnapshot(
                    region_locked=bool(row["region_locked"]),
                    translation_locked=bool(row["translation_locked"]),
                    inpaint_locked=bool(row["inpaint_locked"]),
                )
                if stored != lock_snapshot:
                    conn.rollback()
                    return RegionCommitResult(
                        RegionCommitStatus.LOCK_CHANGED,
                        detail=f"locks changed: stored {stored} vs expected {lock_snapshot}",
                    )

            revision_no = (
                conn.execute(
                    "SELECT COALESCE(MAX(revision_no), 0) + 1 AS next_no"
                    " FROM region_revisions WHERE region_id = ?",
                    (region.region_id,),
                ).fetchone()["next_no"]
            )
            stored_revision = replace(revision, revision_no=revision_no)
            self._insert_revision(stored_revision)

            # Revision-owned state is synced from the snapshot contract only.
            values = self._region_write_values(region)
            conn.execute(
                "UPDATE regions SET page_id = ?, region_type = ?, reading_order = ?,"
                " geometry_json = ?, text_json = ?, style_json = ?, sfx_policy = ?,"
                " region_locked = ?, translation_locked = ?, inpaint_locked = ?,"
                " current_revision_id = ?, updated_at = ? WHERE region_id = ?",
                (*values, stored_revision.region_revision_id, region.updated_at,
                 region.region_id),
            )
            conn.commit()
        except Exception as error:
            # F-02: non-sqlite3 failures (e.g. serialization) must also
            # release the IMMEDIATE transaction before surfacing.
            conn.rollback()
            return RegionCommitResult(
                RegionCommitStatus.DB_FAILED, detail=repr(error)
            )
        # Carry the new pointer back on the caller's object; the service
        # layer (_sync_region_state) finalises the full object view.
        region.current_revision_id = stored_revision.region_revision_id
        return RegionCommitResult(
            RegionCommitStatus.APPLIED, revision_no=stored_revision.revision_no
        )

    def _insert_revision(self, revision: RegionRevision) -> None:
        self._conn.execute(
            "INSERT INTO region_revisions (region_revision_id, region_id, revision_no,"
            " snapshot_json, origin, review_state, is_pinned, source_run_id,"
            " source_step_run_id, restored_from_revision_id, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                revision.region_revision_id, revision.region_id,
                revision.revision_no,
                json.dumps(revision.snapshot, ensure_ascii=False, sort_keys=True),
                revision.origin.value, revision.review_state.value,
                int(revision.is_pinned), revision.source_run_id,
                revision.source_step_run_id, revision.restored_from_revision_id,
                revision.created_at,
            ),
        )


# ----------------------------------------------------------------------
# small local helpers
# ----------------------------------------------------------------------

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def _text_jsonable(text: RegionText) -> dict:
    return {
        "ocr_text": text.ocr_text,
        "machine_translation": text.machine_translation,
        "edited_translation": text.edited_translation,
        "final_translation": text.final_translation,
        "final_source": text.final_source,
        "edited_confirmed": text.edited_confirmed,
        "manual_edited": text.manual_edited,
        "translation_locked": text.translation_locked,
    }
