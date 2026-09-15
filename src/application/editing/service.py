"""Region editing use cases: geometry ops, revisions, manual protection.

Frozen rules implemented here:
- TASK-002 §2.1: a region's current_revision_id is set at creation (the
  first revision is created in the same use-case step) and is never NULL
  afterwards; restoring creates a NEW revision with provenance instead of
  repointing history.
- D06 §87: revisions are created on OCR save, accepted machine result,
  manual save, final confirmation, geometry/style save and lock changes.
- D06 §89/§90: automatic writes go through the atomic commit seam, which
  re-checks the current revision and the locks inside the transaction; on
  mismatch nothing is overwritten and the payload is reported for
  StepResultCandidate persistence (TASK-011).
- TASK-028 §3.4/§4.2: revision-owned state is only synced through
  ``commit_region_revision`` (so reordering creates user revisions), pin is
  a dedicated single-purpose repository call, and no path upserts immutable
  history.
- D03 §8.3/§8.4: confirmed non-blank manual text wins as final; a manual
  save arms manual_edited + translation_locked automatically.
"""

from __future__ import annotations

import uuid
from dataclasses import replace

from application.editing.errors import (
    GuardStatus,
    GuardedWriteOutcome,
    RegionNotFound,
)
from application.editing.ports import (
    RegionCommitResult,
    RegionCommitStatus,
    RegionLockSnapshot,
    RegionRepository,
    RegionRevisionCommitter,
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
    utc_now,
)


def _new_id() -> str:
    return uuid.uuid4().hex


def _clone_region(region: Region) -> Region:
    """Deep copy for optimistic writes: on conflict the caller's object
    stays exactly as it was."""
    clone = Region(
        region_id=region.region_id,
        page_id=region.page_id,
        created_at=region.created_at,
        updated_at=region.updated_at,
        deleted_at=region.deleted_at,
    )
    clone.restore_from_snapshot(region.snapshot_state())
    clone.current_revision_id = region.current_revision_id
    return clone


def _sync_region_state(region: Region, staged: Region) -> None:
    """Copy committed staged state back onto the caller's object."""
    region.restore_from_snapshot(staged.snapshot_state())
    region.current_revision_id = staged.current_revision_id
    region.updated_at = staged.updated_at


def _guard_status_of(result: RegionCommitResult) -> GuardStatus:
    return {
        RegionCommitStatus.LOCK_CHANGED: GuardStatus.LOCK_CHANGED,
    }.get(result.status, GuardStatus.INPUT_REVISION_CHANGED)


class InMemoryRegionCommitter:
    """Contract-faithful committer for in-memory repositories: same guard
    order and pointer semantics as the SQLite seam, without transactions."""

    def __init__(self, repository: RegionRepository) -> None:
        self._repo = repository

    def commit_region_revision(
        self,
        region: Region,
        revision: RegionRevision,
        *,
        expected_current_revision_id: str | None = None,
        lock_snapshot: RegionLockSnapshot | None = None,
    ) -> RegionCommitResult:
        stored = self._repo.get_region(region.region_id)
        if stored is None:
            return RegionCommitResult(
                RegionCommitStatus.DB_FAILED,
                detail=f"region {region.region_id} is not persisted",
            )
        if (
            expected_current_revision_id is not None
            and stored.current_revision_id != expected_current_revision_id
        ):
            return RegionCommitResult(
                RegionCommitStatus.INPUT_REVISION_CHANGED,
                detail=(
                    f"expected current {expected_current_revision_id!r},"
                    f" stored current {stored.current_revision_id!r}"
                ),
            )
        if lock_snapshot is not None:
            stored_locks = RegionLockSnapshot(
                region_locked=stored.region_locked,
                translation_locked=stored.translation_locked,
                inpaint_locked=stored.inpaint_locked,
            )
            if stored_locks != lock_snapshot:
                return RegionCommitResult(
                    RegionCommitStatus.LOCK_CHANGED,
                    detail=(
                        f"locks changed: stored {stored_locks} vs expected {lock_snapshot}"
                    ),
                )

        revision_no = max(
            (rev.revision_no for rev in self._repo.list_revisions(region.region_id)),
            default=0,
        ) + 1
        stored_revision = replace(revision, revision_no=revision_no)
        self._repo.add_revision(stored_revision)
        # Sync revision-owned state INTO the stored object itself: replacing
        # the repository's object reference would orphan the caller's region
        # and break subsequent reads (reference stability). The staged view
        # also carries the new pointer back to the service.
        stored.restore_from_snapshot(region.snapshot_state())
        stored.current_revision_id = stored_revision.region_revision_id
        stored.updated_at = revision.created_at
        region.current_revision_id = stored_revision.region_revision_id
        region.updated_at = revision.created_at
        self._repo.update_region(stored)
        return RegionCommitResult(
            RegionCommitStatus.APPLIED, revision_no=stored_revision.revision_no
        )


class RegionEditingService:
    def __init__(
        self,
        repository: RegionRepository,
        committer: RegionRevisionCommitter | None = None,
    ) -> None:
        self._repo = repository
        self._committer: RegionRevisionCommitter = (
            committer if committer is not None else InMemoryRegionCommitter(repository)
        )

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _require_region(self, region_id: str) -> Region:
        region = self._repo.get_region(region_id)
        if region is None or region.deleted:
            raise RegionNotFound(region_id)
        return region

    def _build_revision(
        self,
        staged: Region,
        origin: RegionOrigin,
        review_state: ReviewState,
        *,
        source_run_id: str | None = None,
        source_step_run_id: str | None = None,
        restored_from_revision_id: str | None = None,
    ) -> RegionRevision:
        return RegionRevision(
            region_revision_id=_new_id(),
            region_id=staged.region_id,
            revision_no=0,  # assigned inside the commit seam transaction
            snapshot=staged.snapshot_state(),
            origin=origin,
            review_state=review_state,
            source_run_id=source_run_id,
            source_step_run_id=source_step_run_id,
            restored_from_revision_id=restored_from_revision_id,
        )

    def _commit(
        self,
        region: Region,
        staged: Region,
        revision: RegionRevision,
        *,
        expected_current_revision_id: str | None = None,
        lock_snapshot: RegionLockSnapshot | None = None,
    ) -> RegionCommitResult:
        """Single commit path for every revision write (TASK-028 §4.2)."""
        result = self._committer.commit_region_revision(
            staged,
            revision,
            expected_current_revision_id=expected_current_revision_id,
            lock_snapshot=lock_snapshot,
        )
        if result.status is RegionCommitStatus.APPLIED:
            _sync_region_state(region, staged)
        return result

    def _commit_user_or_raise(
        self,
        region: Region,
        staged: Region,
        origin: RegionOrigin,
        review_state: ReviewState,
        *,
        restored_from_revision_id: str | None = None,
    ) -> RegionRevision:
        """User-initiated writes: no optimistic expectation; a database
        failure surfaces as an exception instead of a silent no-op."""
        revision = self._build_revision(
            staged, origin, review_state,
            restored_from_revision_id=restored_from_revision_id,
        )
        result = self._committer.commit_region_revision(staged, revision)
        if result.status is not RegionCommitStatus.APPLIED:
            raise RuntimeError(f"region revision commit failed: {result.detail}")
        _sync_region_state(region, staged)
        return replace(revision, revision_no=result.revision_no or 0)

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
        # TASK-002 §2.1: first revision + pointer in one atomic commit.
        staged = _clone_region(region)
        self._commit_user_or_raise(
            region, staged, RegionOrigin(origin), ReviewState.UNREVIEWED
        )
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
        staged = _clone_region(region)
        staged.geometry = geometry
        revision = self._build_revision(staged, RegionOrigin.USER, ReviewState.UNREVIEWED)
        result = self._commit(
            region, staged, revision,
            expected_current_revision_id=expected_current_revision_id,
        )
        if result.status is not RegionCommitStatus.APPLIED:
            return GuardedWriteOutcome(
                _guard_status_of(result), detail=result.detail
            )
        return GuardedWriteOutcome(
            GuardStatus.APPLIED, revision_no=result.revision_no
        )

    def merge_regions(
        self, page_id: str, region_ids: list[str]
    ) -> tuple[Region, tuple[str, ...]]:
        """Merge regions of one page into a new region (D03 §6.4).

        Geometry: covering bbox + concatenated polygons. Text: OCR text and
        machine translation join with a separator; manual protection from
        any source carries over (the merged region still needs its own
        confirmation). Old regions are soft-deleted; the merged region
        starts its own revision history with reading_order = min.
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
            # Preserve the strongest protection across the merged set; the
            # confirmation state itself is re-earned on the merged region.
            merged.text.manual_edited = True
            merged.text.translation_locked = True
            manuals = [r.text.edited_translation for r in regions if r.text.edited_translation]
            merged.text.edited_translation = " ".join(manuals)
        merged.text.refresh_final()

        self._repo.add_region(merged)
        staged = _clone_region(merged)
        self._commit_user_or_raise(
            merged, staged, RegionOrigin.USER, ReviewState.UNREVIEWED
        )
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
            part.text = RegionText(
                ocr_text=source.text.ocr_text,
                manual_edited=source.text.manual_edited,
                translation_locked=source.text.translation_locked,
            )
            part.text.refresh_final()
            self._repo.add_region(part)
            staged = _clone_region(part)
            self._commit_user_or_raise(
                part, staged, RegionOrigin.USER, ReviewState.UNREVIEWED
            )
            created.append(part)
        source.soft_delete()
        self._repo.update_region(source)
        return tuple(created)

    # ------------------------------------------------------------------
    # reading order (AC-REGION-003, TASK-028 §3.4)
    # ------------------------------------------------------------------

    def reorder_regions(self, page_id: str, ordered_region_ids: list[str]) -> list[Region]:
        """reading_order is revision-owned state: every changed region gets a
        new user revision through the atomic seam (TASK-028 §3.4)."""
        regions = {region.region_id: region for region in self.list_regions(page_id)}
        missing = [rid for rid in ordered_region_ids if rid not in regions]
        if missing:
            raise RegionNotFound(missing[0])
        reordered = []
        for position, region_id in enumerate(ordered_region_ids, start=1):
            region = regions[region_id]
            if region.reading_order == position:
                reordered.append(region)
                continue
            staged = _clone_region(region)
            staged.reading_order = position
            self._commit_user_or_raise(
                region, staged, RegionOrigin.USER, ReviewState.UNREVIEWED
            )
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
        staged = _clone_region(region)
        changed = staged.text.apply_ocr(ocr_text)
        revision = self._build_revision(
            staged, RegionOrigin.MACHINE, ReviewState.NEEDS_REVIEW,
            source_run_id=source_run_id, source_step_run_id=source_step_run_id,
        )
        result = self._commit(region, staged, revision)
        if result.status is not RegionCommitStatus.APPLIED:
            return GuardedWriteOutcome(
                _guard_status_of(result), detail=result.detail
            )
        return GuardedWriteOutcome(
            GuardStatus.APPLIED,
            revision_no=result.revision_no,
            # AC-OCR-002: changed source text with a manual译文 → hint.
            retranslate_hint=changed and staged.text.manual_edited,
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
        staged = _clone_region(region)
        # D06 §90 order: a stale revision expectation outranks the lock.
        if (
            expected_current_revision_id is not None
            and staged.current_revision_id != expected_current_revision_id
        ):
            return GuardedWriteOutcome(
                GuardStatus.INPUT_REVISION_CHANGED,
                conflicts=(region.region_id,),
            )
        if staged.text.translation_locked or staged.region_locked:
            # D06 §89: saved as candidate/provenance only, never overwrite.
            return GuardedWriteOutcome(
                GuardStatus.LOCK_CHANGED,
                detail="translation_locked — persist as StepResultCandidate (TASK-011)",
            )
        staged.text.apply_machine_translation(translation)
        revision = self._build_revision(
            staged, RegionOrigin.MACHINE, ReviewState.NEEDS_REVIEW,
            source_run_id=source_run_id, source_step_run_id=source_step_run_id,
        )
        # Carry the locks observed now; the seam re-reads them in-transaction.
        lock_snapshot = RegionLockSnapshot(
            region_locked=staged.region_locked,
            translation_locked=staged.translation_locked,
            inpaint_locked=staged.inpaint_locked,
        )
        result = self._commit(
            region, staged, revision,
            expected_current_revision_id=expected_current_revision_id,
            lock_snapshot=lock_snapshot,
        )
        if result.status is not RegionCommitStatus.APPLIED:
            return GuardedWriteOutcome(
                _guard_status_of(result), detail=result.detail
            )
        return GuardedWriteOutcome(
            GuardStatus.APPLIED, revision_no=result.revision_no
        )

    def save_manual_translation(self, region_id: str, edited: str) -> int:
        """User save → new user revision; arms manual protection (§8.4)."""
        region = self._require_region(region_id)
        staged = _clone_region(region)
        staged.text.save_manual_translation(edited)
        revision = self._commit_user_or_raise(
            region, staged, RegionOrigin.USER, ReviewState.NEEDS_REVIEW
        )
        return revision.revision_no

    def confirm_final(self, region_id: str) -> int:
        """Explicit proofread confirmation → confirmed revision (D06 §87).
        A non-blank edited text becomes the confirmed final (D03 §8.3);
        confirming a region without manual text just locks the review state."""
        region = self._require_region(region_id)
        staged = _clone_region(region)
        if staged.text.edited_translation.strip():
            staged.text.confirm_edited_translation()
        else:
            staged.text.refresh_final()
        revision = self._commit_user_or_raise(
            region, staged, RegionOrigin.USER, ReviewState.CONFIRMED
        )
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
        staged = _clone_region(region)
        staged.restore_from_snapshot(dict(source.snapshot))
        revision = RegionRevision(
            region_revision_id=_new_id(),
            region_id=region_id,
            revision_no=0,  # assigned by the seam transaction
            snapshot=dict(source.snapshot),
            origin=RegionOrigin.RESTORED,
            review_state=ReviewState.NEEDS_REVIEW,
            restored_from_revision_id=source.region_revision_id,
        )
        result = self._committer.commit_region_revision(staged, revision)
        if result.status is not RegionCommitStatus.APPLIED:
            raise RuntimeError(f"region revision commit failed: {result.detail}")
        _sync_region_state(region, staged)
        return region

    def set_revision_pinned(self, region_id: str, revision_no: int, pinned: bool) -> None:
        """AC-REV-003: pin is a dedicated single-purpose transaction that
        only flips is_pinned — immutable history is never upserted."""
        self._repo.set_revision_pinned(region_id, revision_no, pinned)


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
