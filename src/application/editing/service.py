"""Region editing use cases: geometry ops, revisions, manual protection.

Frozen rules implemented here:
- TASK-002 §2.1: a region's current_revision_id is set at creation (the
  first revision is created in the same use-case step) and is never NULL
  afterwards; restoring creates a NEW revision with provenance instead of
  repointing history.
- D06 §87: revisions are created on OCR save, accepted machine result,
  manual save, final confirmation, geometry/style save and lock changes.
- D06 §89/§90: automatic writes re-check the current revision and the
  locks inside the use case; on mismatch nothing is overwritten and the
  payload is reported for StepResultCandidate persistence (TASK-011).
- D03 §8.3/§8.4: confirmed non-blank manual text wins as final; a manual
  save arms manual_edited + translation_locked automatically.
"""

from __future__ import annotations

import uuid

from application.editing.errors import GuardStatus, GuardedWriteOutcome, RegionNotFound
from application.editing.ports import RegionRepository
from domain.regions.entities import (
    Region,
    RegionGeometry,
    RegionOrigin,
    RegionRevision,
    RegionType,
    ReviewState,
    SfxPolicy,
    utc_now,
)


def _new_id() -> str:
    return uuid.uuid4().hex


class RegionEditingService:
    def __init__(self, repository: RegionRepository) -> None:
        self._repo = repository

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _require_region(self, region_id: str) -> Region:
        region = self._repo.get_region(region_id)
        if region is None or region.deleted:
            raise RegionNotFound(region_id)
        return region

    def _next_revision_no(self, region_id: str) -> int:
        revisions = self._repo.list_revisions(region_id)
        return max((rev.revision_no for rev in revisions), default=0) + 1

    def _commit_revision(
        self,
        region: Region,
        origin: RegionOrigin,
        review_state: ReviewState,
        *,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
        restored_from_revision_id: str | None = None,
    ) -> RegionRevision:
        revision_no = self._next_revision_no(region.region_id)
        revision = RegionRevision(
            region_revision_id=_new_id(),
            region_id=region.region_id,
            revision_no=revision_no,
            snapshot=region.snapshot_state(),
            origin=origin,
            review_state=review_state,
            source_run_id=source_run_id,
            source_step_run_id=source_step_run_id,
            restored_from_revision_id=restored_from_revision_id,
        )
        self._repo.add_revision(revision)
        region.current_revision_id = revision.region_revision_id
        region.updated_at = revision.created_at
        self._repo.update_region(region)
        return revision

    # ------------------------------------------------------------------
    # creation / deletion (AC-REGION-001/002)
    # ------------------------------------------------------------------

    def create_region(
        self,
        page_id: str,
        geometry: RegionGeometry,
        *,
        region_type: RegionType = RegionType.SPEECH,
        reading_order: int | None = None,
        sfx_policy: SfxPolicy = SfxPolicy.SKIP,
        origin: RegionOrigin = RegionOrigin.USER,
    ) -> Region:
        if reading_order is None:
            existing = [r for r in self._repo.list_regions(page_id) if not r.deleted]
            reading_order = max((r.reading_order for r in existing), default=0) + 1
        region = Region(
            region_id=_new_id(),
            page_id=page_id,
            region_type=RegionType(region_type),
            reading_order=reading_order,
            geometry=geometry,
            sfx_policy=SfxPolicy(sfx_policy),
        )
        self._repo.add_region(region)
        # TASK-002 §2.1: current pointer must be non-null at creation.
        self._commit_revision(region, RegionOrigin(origin), ReviewState.UNREVIEWED)
        return region

    def get_region(self, region_id: str) -> Region:
        return self._require_region(region_id)

    def list_regions(self, page_id: str) -> list[Region]:
        regions = [r for r in self._repo.list_regions(page_id) if not r.deleted]
        return sorted(regions, key=lambda region: region.reading_order)

    def delete_region(self, region_id: str) -> None:
        region = self._require_region(region_id)
        region.soft_delete()
        self._repo.update_region(region)

    # ------------------------------------------------------------------
    # geometry (AC-REGION-002, D06 §87 "Geometry 保存")
    # ------------------------------------------------------------------

    def save_geometry(
        self,
        region_id: str,
        geometry: RegionGeometry,
        *,
        expected_current_revision_id: str | None = None,
    ) -> GuardedWriteOutcome:
        region = self._require_region(region_id)
        if (
            expected_current_revision_id is not None
            and region.current_revision_id != expected_current_revision_id
        ):
            return GuardedWriteOutcome(
                GuardStatus.INPUT_REVISION_CHANGED,
                detail="geometry edited against a stale current revision",
            )
        region.geometry = geometry
        revision = self._commit_revision(region, RegionOrigin.USER, ReviewState.UNREVIEWED)
        return GuardedWriteOutcome(GuardStatus.APPLIED, revision_no=revision.revision_no)

    def merge_regions(
        self, page_id: str, region_ids: list[str]
    ) -> tuple[Region, tuple[str, ...]]:
        """Merge regions of one page into a new region (D03 §6.4).

        Geometry: covering bbox + concatenated polygons. Text: OCR text and
        machine translation join with a separator; manual edits from any
        source keep protection. Old regions are soft-deleted; the merged
        region starts its own revision history with reading_order = min.
        """
        if len(region_ids) < 2:
            raise ValueError("merge needs at least two regions")
        regions = [self._require_region(rid) for rid in region_ids]
        if any(region.page_id != page_id for region in regions):
            raise ValueError("merge is limited to regions of one page")

        geometry = regions[0].geometry
        for region in regions[1:]:
            geometry = geometry.union(region.geometry)

        merged = Region(
            region_id=_new_id(),
            page_id=page_id,
            region_type=regions[0].region_type,
            reading_order=min(region.reading_order for region in regions),
            geometry=geometry,
            sfx_policy=regions[0].sfx_policy,
        )
        merged.text.ocr_text = " ".join(
            region.text.ocr_text for region in regions if region.text.ocr_text
        )
        merged.text.machine_translation = " ".join(
            region.text.machine_translation for region in regions
            if region.text.machine_translation
        )
        if any(region.text.manual_edited for region in regions):
            # Preserve the strongest protection across the merged set.
            merged.text.manual_edited = True
            merged.text.translation_locked = True
            manuals = [r.text.edited_translation for r in regions if r.text.edited_translation]
            merged.text.edited_translation = " ".join(manuals)
        merged.text.refresh_final()

        self._repo.add_region(merged)
        self._commit_revision(merged, RegionOrigin.USER, ReviewState.UNREVIEWED)
        deleted_ids = []
        for region in regions:
            region.soft_delete()
            self._repo.update_region(region)
            deleted_ids.append(region.region_id)
        return merged, tuple(deleted_ids)

    def split_region(
        self,
        region_id: str,
        parts: list[RegionGeometry],
    ) -> tuple[Region, ...]:
        """Split a region into caller-supplied geometries (editor owns the
        interactive cut). The source region is soft-deleted; each part starts
        a fresh revision history; manual protection carries over."""
        source = self._require_region(region_id)
        if len(parts) < 2:
            raise ValueError("split needs at least two parts")
        created: list[Region] = []
        for index, geometry in enumerate(parts, start=1):
            part = Region(
                region_id=_new_id(),
                page_id=source.page_id,
                region_type=source.region_type,
                reading_order=source.reading_order + index - 1,
                geometry=geometry,
                sfx_policy=source.sfx_policy,
            )
            part.text = type(source.text)(
                ocr_text=source.text.ocr_text,
                manual_edited=source.text.manual_edited,
                translation_locked=source.text.translation_locked,
            )
            part.text.refresh_final()
            self._repo.add_region(part)
            self._commit_revision(part, RegionOrigin.USER, ReviewState.UNREVIEWED)
            created.append(part)
        source.soft_delete()
        self._repo.update_region(source)
        return tuple(created)

    # ------------------------------------------------------------------
    # reading order (AC-REGION-003)
    # ------------------------------------------------------------------

    def reorder_regions(self, page_id: str, ordered_region_ids: list[str]) -> list[Region]:
        regions = {region.region_id: region for region in self.list_regions(page_id)}
        missing = [rid for rid in ordered_region_ids if rid not in regions]
        if missing:
            raise RegionNotFound(missing[0])
        reordered = []
        for position, region_id in enumerate(ordered_region_ids, start=1):
            region = regions[region_id]
            if region.reading_order != position:
                region.reading_order = position
                region.updated_at = utc_now()
                self._repo.update_region(region)
            reordered.append(region)
        return reordered

    def reading_order_for_context(self, page_id: str) -> list[Region]:
        """Translation context must use the final manual reading order
        (D03 §6.5), i.e. exactly the user-facing ordering."""
        return self.list_regions(page_id)

    # ------------------------------------------------------------------
    # text writes (AC-OCR-002, AC-TRANS-001/002, D06 §89/§90)
    # ------------------------------------------------------------------

    def apply_ocr_result(
        self,
        region_id: str,
        ocr_text: str,
        *,
        expected_current_revision_id: str | None = None,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
    ) -> GuardedWriteOutcome:
        region = self._require_region(region_id)
        guard = self._optimistic_guard(region, expected_current_revision_id)
        if guard is not None:
            return guard
        changed = region.text.apply_ocr(ocr_text)
        revision = self._commit_revision(
            region,
            RegionOrigin.MACHINE,
            ReviewState.NEEDS_REVIEW,
            source_run_id=source_run_id,
            source_step_run_id=source_step_run_id,
        )
        return GuardedWriteOutcome(
            GuardStatus.APPLIED,
            revision_no=revision.revision_no,
            # AC-OCR-002: changed source text with a manual译文 → hint.
            retranslate_hint=changed and region.text.manual_edited,
        )

    def apply_machine_translation(
        self,
        region_id: str,
        translation: str,
        *,
        expected_current_revision_id: str | None = None,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
    ) -> GuardedWriteOutcome:
        region = self._require_region(region_id)
        guard = self._optimistic_guard(region, expected_current_revision_id)
        if guard is not None:
            return guard
        if region.text.translation_locked or region.region_locked:
            # D06 §89: saved as candidate/provenance only, never overwrite.
            return GuardedWriteOutcome(
                GuardStatus.LOCK_CHANGED,
                detail="translation_locked — persist as StepResultCandidate (TASK-011)",
            )
        region.text.apply_machine_translation(translation)
        revision = self._commit_revision(
            region,
            RegionOrigin.MACHINE,
            ReviewState.NEEDS_REVIEW,
            source_run_id=source_run_id,
            source_step_run_id=source_step_run_id,
        )
        return GuardedWriteOutcome(GuardStatus.APPLIED, revision_no=revision.revision_no)

    def save_manual_translation(self, region_id: str, edited: str) -> int:
        """User save → new user revision; arms manual protection (§8.4)."""
        region = self._require_region(region_id)
        region.text.save_manual_translation(edited)
        revision = self._commit_revision(region, RegionOrigin.USER, ReviewState.NEEDS_REVIEW)
        return revision.revision_no

    def confirm_final(self, region_id: str) -> int:
        """Explicit proofread confirmation → confirmed revision (D06 §87).
        A non-blank edited text becomes the confirmed final (D03 §8.3);
        confirming a region without manual text just locks the review state."""
        region = self._require_region(region_id)
        if region.text.edited_translation.strip():
            region.text.confirm_edited_translation()
        else:
            region.text.refresh_final()
        revision = self._commit_revision(region, RegionOrigin.USER, ReviewState.CONFIRMED)
        return revision.revision_no

    # ------------------------------------------------------------------
    # revisions: restore / pin (AC-REV-003/004)
    # ------------------------------------------------------------------

    def restore_revision(self, region_id: str, revision_no: int) -> Region:
        """AC-REV-004: copy the snapshot into a NEW revision with provenance;
        current then points at the restored copy, history stays intact."""
        region = self._require_region(region_id)
        source = self._repo.get_revision(region_id, revision_no)
        if source is None:
            raise ValueError(f"revision {revision_no} not found for {region_id}")
        region.restore_from_snapshot(dict(source.snapshot))
        revision = RegionRevision(
            region_revision_id=_new_id(),
            region_id=region_id,
            revision_no=self._next_revision_no(region_id),
            snapshot=dict(source.snapshot),
            origin=RegionOrigin.RESTORED,
            review_state=ReviewState.NEEDS_REVIEW,
            restored_from_revision_id=source.region_revision_id,
        )
        self._repo.add_revision(revision)
        region.current_revision_id = revision.region_revision_id
        region.updated_at = revision.created_at
        self._repo.update_region(region)
        return region

    def set_revision_pinned(self, region_id: str, revision_no: int, pinned: bool) -> None:
        """AC-REV-003: pinned revisions are exempt from future cleanup."""
        revision = self._repo.get_revision(region_id, revision_no)
        if revision is None:
            raise ValueError(f"revision {revision_no} not found for {region_id}")
        updated = RegionRevision(
            region_revision_id=revision.region_revision_id,
            region_id=revision.region_id,
            revision_no=revision.revision_no,
            snapshot=revision.snapshot,
            origin=revision.origin,
            review_state=revision.review_state,
            is_pinned=pinned,
            source_run_id=revision.source_run_id,
            source_step_run_id=revision.source_step_run_id,
            restored_from_revision_id=revision.restored_from_revision_id,
            created_at=revision.created_at,
        )
        self._repo.add_revision(updated)

    # ------------------------------------------------------------------
    # optimistic guard (D06 §90)
    # ------------------------------------------------------------------

    def _optimistic_guard(
        self, region: Region, expected_current_revision_id: str | None
    ) -> GuardedWriteOutcome | None:
        if (
            expected_current_revision_id is not None
            and region.current_revision_id != expected_current_revision_id
        ):
            return GuardedWriteOutcome(
                GuardStatus.INPUT_REVISION_CHANGED,
                detail=(
                    f"step started at revision {expected_current_revision_id!r}, "
                    f"current is {region.current_revision_id!r}"
                ),
                conflicts=(region.region_id,),
            )
        return None


class EditingSession:
    """Stages region edits for one page and flushes them as revisions.

    Switching pages/regions with unsaved edits must go through
    :meth:`flush` (explicit save or approved autosave, TASK-008 AC3) so no
    user input is silently lost; :meth:`discard` is the explicit give-up.
    """

    def __init__(self, service: RegionEditingService, page_id: str) -> None:
        self._service = service
        self._page_id = page_id
        self._staged_geometry: dict[str, RegionGeometry] = {}
        self._staged_text: dict[str, str] = {}

    @property
    def dirty_region_ids(self) -> tuple[str, ...]:
        return tuple({*self._staged_geometry, *self._staged_text})

    @property
    def has_unsaved_changes(self) -> bool:
        return bool(self.dirty_region_ids)

    def stage_geometry(self, region_id: str, geometry: RegionGeometry) -> None:
        self._service.get_region(region_id)  # existence check
        self._staged_geometry[region_id] = geometry

    def stage_manual_translation(self, region_id: str, edited: str) -> None:
        self._service.get_region(region_id)
        self._staged_text[region_id] = edited

    def flush(self) -> dict[str, int]:
        """Apply every staged edit as its own revision; returns revision numbers."""
        saved: dict[str, int] = {}
        for region_id, geometry in self._staged_geometry.items():
            outcome = self._service.save_geometry(region_id, geometry)
            saved[region_id] = outcome.revision_no or 0
        self._staged_geometry.clear()
        for region_id, edited in self._staged_text.items():
            saved[region_id] = self._service.save_manual_translation(region_id, edited)
        self._staged_text.clear()
        return saved

    def discard(self, region_id: str | None = None) -> None:
        if region_id is None:
            self._staged_geometry.clear()
            self._staged_text.clear()
            return
        self._staged_geometry.pop(region_id, None)
        self._staged_text.pop(region_id, None)
