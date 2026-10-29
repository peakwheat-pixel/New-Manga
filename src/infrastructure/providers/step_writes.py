"""Prepare-only writes that cooperate with the TASK-013 pipeline seam.

The pipeline's optimistic commit (``SqliteTargetCatalog.commit_step``) expects
a handler to **prepare** content revisions and then let the seam flip the
current pointer inside its guarded transaction. Two primitives are missing
from the frozen layers this Task may not modify, so they are provided here:

- :class:`RegionStepWriter` inserts the new ``region_revisions`` row and
  updates ``regions.text_json`` **without** touching ``current_revision_id``;
- :class:`ArtifactStepWriter` publishes immutable bytes and inserts the
  ``artifact_revisions`` row **without** touching the artifact pointer.

Both keep the seam authoritative for pointers and stage states:

* a page/region target returns the new revision ids in ``StepResult`` and the
  seam performs the compare-and-set current-pointer write;
* a *region*-scoped unit cannot express a page artifact pointer in
  ``StepResult.revision_updates`` (the seam only accepts ``"region"`` for a
  region target), so :meth:`ArtifactStepWriter.adopt_current` performs the same
  compare-and-set itself and the handler returns no revision update.

Domain rules are reused, not re-implemented: OCR/translation text changes go
through :class:`~domain.regions.entities.RegionText`, so the AC-OCR-002 manual
protection (``edited_translation``/``final_translation`` stay) is the domain's
decision, not this adapter's.
"""

from __future__ import annotations

import copy
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from application.editing.ports import RegionRepository
from domain.regions.entities import (
    Region,
    RegionOrigin,
    RegionRevision,
    ReviewState,
)
from ports.ocr.ports import PreparedTextWrite
from ports.providers.errors import (
    LockBlocked,
    ProviderInputError,
    ProviderUnavailable,
)
from ports.repositories.storage import ManagedFileStoragePort
from ports.translation.ports import PreparedTranslationWrite


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


class _Unchecked:
    """Sentinel: "no expectation supplied" is different from "expect NULL"."""

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return "UNCHECKED"


UNCHECKED = _Unchecked()


def _text_jsonable(region: Region) -> dict:
    """Serialize the region text block exactly as the region table stores it."""
    text = region.text
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


def _revision_snapshot(region: Region) -> dict:
    """Reuse the domain snapshot contract (D03 §15.1), not a private copy."""
    return region.snapshot_state()


@dataclass
class RegionStepWriter:
    """Prepare region text revisions; the pipeline seam flips the pointer."""

    conn: sqlite3.Connection
    repository: RegionRepository

    # ------------------------------------------------------------------
    # public API (the ports' writer protocols)
    # ------------------------------------------------------------------

    def prepare_ocr_text(
        self,
        region_id: str,
        ocr_text: str,
        *,
        provider_id: str = "",
        model: str = "",
        options: dict[str, str] | None = None,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
        expected_current_revision_id: str | None | _Unchecked = UNCHECKED,
    ) -> PreparedTextWrite:
        if not isinstance(ocr_text, str):
            raise ProviderInputError(
                "OCR text must be a string", provider_id=provider_id, stage="ocr"
            )
        staged = self._staged_region(region_id, provider_id=provider_id, stage="ocr")
        if staged.region_locked:
            raise LockBlocked(
                "region is locked", provider_id=provider_id, stage="ocr"
            )
        changed = staged.text.apply_ocr(ocr_text)
        revision_id, revision_no = self._persist(
            staged,
            source_run_id=source_run_id,
            source_step_run_id=source_step_run_id,
            expected_current_revision_id=expected_current_revision_id,
            provider_id=provider_id,
        )
        return PreparedTextWrite(
            region_id=region_id,
            revision_id=revision_id,
            revision_no=revision_no,
            changed=changed,
            # AC-OCR-002 hint: a changed source text with a manual translation.
            retranslate_hint=changed and staged.text.manual_edited,
        )

    def prepare_machine_translation(
        self,
        region_id: str,
        translation: str,
        *,
        provider_id: str = "",
        model: str = "",
        options: dict[str, str] | None = None,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
        expected_current_revision_id: str | None | _Unchecked = UNCHECKED,
    ) -> PreparedTranslationWrite:
        if not isinstance(translation, str):
            raise ProviderInputError(
                "translation must be a string",
                provider_id=provider_id,
                stage="translate",
            )
        staged = self._staged_region(region_id, provider_id=provider_id, stage="translate")
        if staged.translation_locked or staged.region_locked or staged.text.translation_locked:
            # D06 §89: a locked region keeps its text; the machine result may
            # only survive as a candidate, never as the current revision.
            raise LockBlocked(
                "region is translation/region locked",
                provider_id=provider_id,
                stage="translate",
            )
        staged.text.apply_machine_translation(translation)
        revision_id, revision_no = self._persist(
            staged,
            source_run_id=source_run_id,
            source_step_run_id=source_step_run_id,
            expected_current_revision_id=expected_current_revision_id,
            provider_id=provider_id,
        )
        return PreparedTranslationWrite(
            region_id=region_id,
            revision_id=revision_id,
            revision_no=revision_no,
            final_source=staged.text.final_source,
        )

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _staged_region(self, region_id: str, *, provider_id: str = "", stage: str = "") -> Region:
        region = self.repository.get_region(region_id)
        if region is None or region.deleted:
            raise ProviderUnavailable(
                f"region {region_id!r} is not available",
                provider_id=provider_id,
                stage=stage or "region-write",
            )
        return copy.deepcopy(region)

    def _persist(
        self,
        staged: Region,
        *,
        source_run_id: str | None,
        source_step_run_id: str | None,
        expected_current_revision_id: str | None | _Unchecked = UNCHECKED,
        provider_id: str = "",
    ) -> tuple[str, int]:
        revision_id = uuid.uuid4().hex
        now = _utc_now()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            row = self.conn.execute(
                "SELECT current_revision_id FROM regions WHERE region_id = ?"
                " AND deleted_at IS NULL",
                (staged.region_id,),
            ).fetchone()
            if row is None:
                raise ProviderUnavailable(
                    f"region {staged.region_id!r} disappeared",
                    provider_id=provider_id,
                    stage="region-write",
                )
            if (
                not isinstance(expected_current_revision_id, _Unchecked)
                and row["current_revision_id"] != expected_current_revision_id
            ):
                # Same guard the pipeline seam applies, checked *before* any
                # write so a stale attempt cannot mutate the region text.
                raise LockBlocked(
                    "region current revision changed during the step"
                    f" (expected {expected_current_revision_id!r},"
                    f" found {row['current_revision_id']!r})",
                    provider_id=provider_id,
                    stage="region-write",
                )
            revision_no = self.conn.execute(
                "SELECT COALESCE(MAX(revision_no), 0) + 1 AS next_no"
                " FROM region_revisions WHERE region_id = ?",
                (staged.region_id,),
            ).fetchone()["next_no"]
            revision = RegionRevision(
                region_revision_id=revision_id,
                region_id=staged.region_id,
                revision_no=revision_no,
                snapshot=_revision_snapshot(staged),
                origin=RegionOrigin.MACHINE,
                review_state=ReviewState.NEEDS_REVIEW,
                source_run_id=source_run_id,
                source_step_run_id=source_step_run_id,
                created_at=now,
            )
            self.conn.execute(
                "INSERT INTO region_revisions (region_revision_id, region_id,"
                " revision_no, snapshot_json, origin, review_state, is_pinned,"
                " source_run_id, source_step_run_id, restored_from_revision_id,"
                " created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    revision.region_revision_id,
                    revision.region_id,
                    revision.revision_no,
                    json.dumps(revision.snapshot, ensure_ascii=False, sort_keys=True),
                    revision.origin.value,
                    revision.review_state.value,
                    int(revision.is_pinned),
                    revision.source_run_id,
                    revision.source_step_run_id,
                    revision.restored_from_revision_id,
                    revision.created_at,
                ),
            )
            # Text state is region-owned; the *pointer* stays behind for the
            # pipeline seam so its optimistic guard remains authoritative.
            self.conn.execute(
                "UPDATE regions SET text_json = ?, updated_at = ? WHERE region_id = ?",
                (
                    json.dumps(_text_jsonable(staged), ensure_ascii=False, sort_keys=True),
                    now,
                    staged.region_id,
                ),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return revision_id, revision_no


@dataclass(frozen=True)
class PreparedArtifact:
    artifact_id: str
    revision_id: str
    revision_no: int
    artifact_type: str
    managed_path: str
    file_hash: str
    size_bytes: int
    is_first_revision: bool = False
    previous_revision_id: str | None = None


@dataclass
class ArtifactStepWriter:
    """Publish immutable artifact revisions without moving the pointer."""

    conn: sqlite3.Connection
    storage: ManagedFileStoragePort

    def prepare_revision(
        self,
        *,
        page_id: str,
        artifact_type: str,
        payload: bytes,
        mime_type: str,
        suffix: str = ".png",
        width: int | None = None,
        height: int | None = None,
        provider_profile_id: str | None = None,
        model_name: str | None = None,
        options_json: str | None = None,
        source_artifact_revision_id: str | None = None,
        pipeline_run_id: str | None = None,
        step_run_id: str | None = None,
        provenance_json: str | None = None,
        expected_current_revision_id: str | None | _Unchecked = UNCHECKED,
    ) -> PreparedArtifact:
        context = self._page_context(page_id)
        artifact_id, is_first = self._artifact_id(page_id, artifact_type, context)
        previous_revision_id = self.current_revision_id(artifact_id)
        if (
            not isinstance(expected_current_revision_id, _Unchecked)
            and previous_revision_id != expected_current_revision_id
        ):
            # The page-target branch of the pipeline seam owns this pointer;
            # checking it here keeps an orphan revision row from being written.
            raise LockBlocked(
                "artifact current revision changed during the step"
                f" (expected {expected_current_revision_id!r},"
                f" found {previous_revision_id!r})",
                stage="artifact-write",
            )
        revision_id = uuid.uuid4().hex
        relative_path = self.storage.new_revision_relative_path(
            context["book_id"], context["chapter_id"], artifact_type, revision_id, suffix
        )
        temp_handle = self.storage.write_temp(payload)
        try:
            integrity = self.storage.verify_temp(temp_handle)
            if integrity.size_bytes != len(payload):
                raise ProviderInputError(
                    "staged artifact size does not match the payload",
                    stage="artifact-write",
                )
            self.storage.publish(temp_handle, relative_path)
            temp_handle = None
        finally:
            if temp_handle is not None:
                self.storage.discard_temp(temp_handle)

        now = _utc_now()
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            revision_no = self.conn.execute(
                "SELECT COALESCE(MAX(revision_no), 0) + 1 AS next_no"
                " FROM artifact_revisions WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()["next_no"]
            self.conn.execute(
                "INSERT INTO artifact_revisions (artifact_revision_id, artifact_id,"
                " revision_no, managed_path, file_hash, mime_type, width, height,"
                " size_bytes, integrity_status, last_verified_at, provider_profile_id,"
                " model_name, options_json, source_artifact_revision_id,"
                " pipeline_run_id, step_run_id, provenance_json, is_pinned, created_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    revision_id,
                    artifact_id,
                    revision_no,
                    relative_path,
                    integrity.sha256,
                    mime_type,
                    width,
                    height,
                    len(payload),
                    "valid",
                    now,
                    provider_profile_id,
                    model_name,
                    options_json,
                    source_artifact_revision_id,
                    pipeline_run_id,
                    step_run_id,
                    provenance_json,
                    0,
                    now,
                ),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return PreparedArtifact(
            artifact_id=artifact_id,
            revision_id=revision_id,
            revision_no=revision_no,
            artifact_type=artifact_type,
            managed_path=relative_path,
            file_hash=integrity.sha256,
            size_bytes=len(payload),
            is_first_revision=is_first,
            previous_revision_id=previous_revision_id,
        )

    def current_revision_id(self, artifact_id: str) -> str | None:
        row = self.conn.execute(
            "SELECT current_revision_id FROM media_artifacts WHERE artifact_id = ?",
            (artifact_id,),
        ).fetchone()
        if row is None:
            raise ProviderUnavailable(
                f"artifact {artifact_id!r} is not available", stage="artifact-write"
            )
        return row["current_revision_id"]

    def adopt_current(
        self,
        *,
        artifact_id: str,
        revision_id: str,
        expected_current_revision_id: str | None,
    ) -> None:
        """Compare-and-set the artifact pointer (region-scoped units only).

        Mirrors the TASK-002 §8.1 guard: a mismatch leaves the previous current
        revision untouched and fails the step, so no clean image can be
        published over a concurrent edit.
        """
        try:
            self.conn.execute("BEGIN IMMEDIATE")
            row = self.conn.execute(
                "SELECT current_revision_id FROM media_artifacts WHERE artifact_id = ?",
                (artifact_id,),
            ).fetchone()
            if row is None:
                raise ProviderUnavailable(
                    f"artifact {artifact_id!r} disappeared", stage="artifact-write"
                )
            current = row["current_revision_id"]
            if current != expected_current_revision_id:
                raise LockBlocked(
                    "artifact current revision changed during the step"
                    f" (expected {expected_current_revision_id!r}, found {current!r})",
                    stage="artifact-write",
                )
            self.conn.execute(
                "UPDATE media_artifacts SET current_revision_id = ?, updated_at = ?"
                " WHERE artifact_id = ?",
                (revision_id, _utc_now(), artifact_id),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def artifact_for(self, page_id: str, artifact_type: str) -> str | None:
        row = self.conn.execute(
            "SELECT artifact_id FROM media_artifacts WHERE page_id = ? AND artifact_type = ?",
            (page_id, artifact_type),
        ).fetchone()
        return row["artifact_id"] if row else None

    def read_path(self, relative_path: str) -> Path:
        return Path(self.storage.absolute_path(relative_path))

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _page_context(self, page_id: str) -> dict[str, str]:
        row = self.conn.execute(
            "SELECT p.page_id, p.chapter_id, c.book_id FROM pages p"
            " JOIN chapters c ON c.chapter_id = p.chapter_id WHERE p.page_id = ?",
            (page_id,),
        ).fetchone()
        if row is None:
            raise ProviderUnavailable(
                f"page {page_id!r} is not available", stage="artifact-write"
            )
        return {
            "page_id": row["page_id"],
            "chapter_id": row["chapter_id"],
            "book_id": row["book_id"],
        }

    def _artifact_id(
        self, page_id: str, artifact_type: str, context: dict[str, str]
    ) -> tuple[str, bool]:
        existing = self.artifact_for(page_id, artifact_type)
        if existing is not None:
            return existing, False
        artifact_id = uuid.uuid4().hex
        now = _utc_now()
        self.conn.execute(
            "INSERT INTO media_artifacts (artifact_id, book_id, chapter_id, page_id,"
            " artifact_type, current_revision_id, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, NULL, ?, ?)",
            (
                artifact_id,
                context["book_id"],
                context["chapter_id"],
                page_id,
                artifact_type,
                now,
                now,
            ),
        )
        self.conn.commit()
        return artifact_id, True


def artifact_payload_from_frame(
    frame: Any, *, extra: dict | None = None
) -> tuple[bytes, str, int, int]:
    """Serialize an :class:`~ports.inpaint.ports.ImageFrame` for storage.

    Uses a tiny, self-describing container instead of a PNG encoder so the
    provider layer stays free of Qt/numpy. The container is
    ``b"NMFR"`` + JSON header + raw pixels; the MIME type names it so a reader
    can never mistake it for a shareable image format.
    """
    from ports.inpaint.ports import ImageFrame

    if not isinstance(frame, ImageFrame):
        raise ProviderInputError("expected an ImageFrame", stage="artifact-write")
    header = {
        "mode": frame.mode,
        "width": frame.width,
        "height": frame.height,
        "bytes_per_pixel": len(frame.data) // max(1, frame.width * frame.height),
    }
    if extra:
        header.update(extra)
    encoded = json.dumps(header, sort_keys=True).encode("utf-8")
    payload = b"NMFR" + len(encoded).to_bytes(4, "big") + encoded + frame.data
    return payload, "application/x-newmanga-frame", frame.width, frame.height


def decode_frame_payload(payload: bytes) -> tuple[dict, bytes]:
    """Inverse of :func:`artifact_payload_from_frame` (used by tests/readers)."""
    if not payload.startswith(b"NMFR") or len(payload) < 8:
        raise ProviderInputError("not a managed frame payload", stage="artifact-write")
    header_length = int.from_bytes(payload[4:8], "big")
    header = json.loads(payload[8 : 8 + header_length].decode("utf-8"))
    return header, payload[8 + header_length :]


def mask_payload(mask: Any) -> tuple[bytes, str, int, int]:
    """Serialize a :class:`~ports.inpaint.ports.BooleanMask` for storage.

    Bit-packed rows with an explicit header, so the persisted Mask Revision
    can be read back byte-for-byte (AC-INPAINT-001) without an image codec.
    """
    from ports.inpaint.ports import BooleanMask

    if not isinstance(mask, BooleanMask):
        raise ProviderInputError("expected a BooleanMask", stage="artifact-write")
    bits = bytearray()
    current = 0
    bit_index = 0
    for row in mask.rows:
        for cell in row:
            if cell:
                current |= 1 << (7 - bit_index)
            bit_index += 1
            if bit_index == 8:
                bits.append(current)
                current = 0
                bit_index = 0
    if bit_index:
        bits.append(current)
    header = json.dumps(
        {"width": mask.width, "height": mask.height, "area": mask.area, "format": "bitmap-msb"},
        sort_keys=True,
    ).encode("utf-8")
    payload = b"NMK1" + len(header).to_bytes(4, "big") + header + bytes(bits)
    return payload, "application/x-newmanga-mask", mask.width, mask.height


def decode_mask_payload(payload: bytes) -> tuple[dict, Any]:
    """Inverse of :func:`mask_payload`; returns ``(header, BooleanMask)``."""
    from ports.inpaint.ports import BooleanMask

    if not payload.startswith(b"NMK1") or len(payload) < 8:
        raise ProviderInputError("not a managed mask payload", stage="read")
    header_length = int.from_bytes(payload[4:8], "big")
    header = json.loads(payload[8 : 8 + header_length].decode("utf-8"))
    bits = payload[8 + header_length :]
    width = int(header["width"])
    height = int(header["height"])
    rows: list[tuple[bool, ...]] = []
    bit_index = 0
    for _ in range(height):
        row: list[bool] = []
        for _ in range(width):
            byte = bits[bit_index // 8]
            row.append(bool(byte & (1 << (7 - (bit_index % 8)))))
            bit_index += 1
        rows.append(tuple(row))
    return header, BooleanMask(width, height, tuple(rows))
