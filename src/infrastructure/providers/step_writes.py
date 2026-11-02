"""Prepare-only region/artifact writes coordinated by the SQLite commit seam.

Region and artifact writers create durable ``prepared`` candidates. Region text,
revision rows, artifact pointers, stage state, candidate resolution and final
artifact publication are committed by ``SqliteTargetCatalog.commit_step``.

The domain rules remain centralized in ``RegionText``: OCR and translation
updates preserve manually edited translation fields according to the existing
domain policy.
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
        if not source_run_id or not source_step_run_id:
            raise ProviderInputError(
                "pipeline run and step identifiers are required for staged region writes",
                provider_id=provider_id,
                stage="region-write",
            )
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
            payload = {
                "revision_id": revision_id,
                "revision_no": revision_no,
                "snapshot": _revision_snapshot(staged),
                "text_json": _text_jsonable(staged),
                "origin": RegionOrigin.MACHINE.value,
                "review_state": ReviewState.NEEDS_REVIEW.value,
                "is_pinned": False,
                "source_run_id": source_run_id,
                "source_step_run_id": source_step_run_id,
                "restored_from_revision_id": None,
                "created_at": now,
            }
            self.conn.execute(
                "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id,"
                " step_run_id, target_id, page_id, region_id, result_kind,"
                " base_revision_id, payload_json, reason, status, created_at, resolved_at)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'prepared', ?, NULL)",
                (
                    revision_id, source_run_id, source_step_run_id, staged.region_id,
                    staged.page_id, staged.region_id, "region", row["current_revision_id"],
                    json.dumps(payload, ensure_ascii=False, sort_keys=True), "prepared", now,
                ),
            )
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise
        return revision_id, revision_no


@dataclass(frozen=True)
class PreparedArtifact:
    artifact_id: str | None
    revision_id: str
    revision_no: int | None
    artifact_type: str
    managed_path: str
    file_hash: str
    size_bytes: int
    is_first_revision: bool = False
    previous_revision_id: str | None = None


@dataclass
class ArtifactStepWriter:
    """Stage artifact bytes and candidate metadata for the commit seam."""

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
        if not pipeline_run_id or not step_run_id:
            raise ProviderInputError(
                "pipeline run and step identifiers are required for staged artifact writes",
                stage="artifact-write",
            )
        if not isinstance(mime_type, str) or not mime_type.strip():
            raise ProviderInputError("mime_type is required", stage="artifact-write")
        context = self._page_context(page_id)
        artifact_id = self.artifact_for(page_id, artifact_type)
        previous_revision_id = (
            self.current_revision_id(artifact_id) if artifact_id is not None else None
        )
        if (
            not isinstance(expected_current_revision_id, _Unchecked)
            and previous_revision_id != expected_current_revision_id
        ):
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
        candidate_persisted = False
        try:
            integrity = self.storage.verify_temp(temp_handle)
            if integrity.size_bytes != len(payload):
                raise ProviderInputError(
                    "staged artifact size does not match the payload",
                    stage="artifact-write",
                )
            now = _utc_now()
            candidate_payload = {
                "temp_handle": temp_handle,
                "relative_path": relative_path,
                "artifact_type": artifact_type,
                "page_id": page_id,
                "book_id": context["book_id"],
                "chapter_id": context["chapter_id"],
                "base_revision_id": previous_revision_id,
                "sha256": integrity.sha256,
                "size": integrity.size_bytes,
                "mime_type": mime_type,
                "content_format": Path(relative_path).suffix.lstrip("."),
                # Optional artifact-revision metadata remains in the staged
                # snapshot so moving it to the seam does not drop provenance.
                "width": width,
                "height": height,
                "provider_profile_id": provider_profile_id,
                "model_name": model_name,
                "options_json": options_json,
                "source_artifact_revision_id": source_artifact_revision_id,
                "provenance_json": provenance_json,
            }
            if artifact_id is not None:
                candidate_payload["artifact_id"] = artifact_id
            self.conn.execute("BEGIN IMMEDIATE")
            latest = self.conn.execute(
                "SELECT current_revision_id FROM media_artifacts"
                " WHERE page_id = ? AND artifact_type = ? ORDER BY created_at, artifact_id LIMIT 1",
                (page_id, artifact_type),
            ).fetchone()
            latest_revision_id = latest["current_revision_id"] if latest else None
            if latest_revision_id != previous_revision_id:
                raise LockBlocked(
                    "artifact current revision changed during prepare",
                    stage="artifact-write",
                )
            self.conn.execute(
                "INSERT INTO step_result_candidates (candidate_id, pipeline_run_id,"
                " step_run_id, target_id, page_id, region_id, result_kind,"
                " base_revision_id, payload_json, reason, status, created_at, resolved_at)"
                " VALUES (?, ?, ?, ?, ?, NULL, ?, ?, ?, ?, 'prepared', ?, NULL)",
                (
                    revision_id,
                    pipeline_run_id,
                    step_run_id,
                    page_id,
                    page_id,
                    artifact_type,
                    previous_revision_id,
                    json.dumps(candidate_payload, ensure_ascii=False, sort_keys=True),
                    "prepared",
                    now,
                ),
            )
            self.conn.commit()
            candidate_persisted = True
        except Exception:
            self.conn.rollback()
            raise
        finally:
            if not candidate_persisted:
                self.storage.discard_temp(temp_handle)
        return PreparedArtifact(
            artifact_id=artifact_id,
            revision_id=revision_id,
            revision_no=None,
            artifact_type=artifact_type,
            managed_path=relative_path,
            file_hash=integrity.sha256,
            size_bytes=integrity.size_bytes,
            is_first_revision=artifact_id is None,
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

    def artifact_for(self, page_id: str, artifact_type: str) -> str | None:
        row = self.conn.execute(
            "SELECT artifact_id FROM media_artifacts WHERE page_id = ? AND artifact_type = ?"
            " ORDER BY created_at, artifact_id LIMIT 1",
            (page_id, artifact_type),
        ).fetchone()
        return row["artifact_id"] if row else None

    def read_path(self, relative_path: str) -> Path:
        return Path(self.storage.absolute_path(relative_path))

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
