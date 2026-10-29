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
- V11R-F0-1: every user write accepts the optional keyword-only
  ``expected_revision_no`` optimistic guard (stale -> typed
  ``RegionRevisionChanged`` with ZERO write, wire INPUT_REVISION_CHANGED);
  multi-region writes take ``expected_revisions``. ``set_locks`` is the thin
  use case for the three explicit user locks (the domain setters existed,
  the application-layer use case did not), still routed through the same
  atomic commit seam.
"""

from __future__ import annotations

import uuid
from dataclasses import replace

from application.editing.errors import (
    GuardStatus,
    GuardedWriteOutcome,
    RegionNotFound,
    RegionRevisionChanged,
    RegionRevisionNotFound,
)
from application.editing.ports import (
    RegionCommitResult,
    RegionCommitStatus,
    RegionLockSnapshot,
    RegionRepository,
    RegionRevisionCommitter,
)
from application.editing.region_canvas import page_geometry_to_normalized
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


def effective_sfx_policy(
    region_type: RegionType, global_policy: str | SfxPolicy
) -> SfxPolicy:
    """EV-8 shared rule for BOTH region write paths (creation and retype):
    only an SFX-typed region carries the configured global policy; every
    other type forces SKIP so the policy can never leak onto non-SFX
    regions (M2-C1 rev 1.4 §5.4; core_assembly creation precedent)."""
    if region_type is RegionType.SFX:
        return SfxPolicy(global_policy)
    return SfxPolicy.SKIP


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
        if committer is not None:
            self._committer = committer
        elif hasattr(repository, "commit_region_revision"):
            # F-01: a repository that implements the atomic seam IS the
            # correct committer for itself. Falling back to the in-memory
            # committer against SQLite would insert revisions while silently
            # skipping the revision-owned state/pointer update (SQLite's
            # update_region only writes soft-delete metadata).
            self._committer = repository
        else:
            self._committer = InMemoryRegionCommitter(repository)

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
        expected_current_revision_id: str | None = None,
    ) -> RegionRevision:
        """User-initiated writes: a database failure surfaces as an exception
        instead of a silent no-op.

        V11R-F0-1: the optional ``expected_current_revision_id`` is the
        optimistic guard (the caller resolved it from the ``expected_revision``
        revision number). The commit seam re-checks it inside its transaction
        and a mismatch is a typed :class:`RegionRevisionChanged` with ZERO
        write -- never a silently swallowed conflict.
        """
        revision = self._build_revision(
            staged, origin, review_state,
            restored_from_revision_id=restored_from_revision_id,
        )
        result = self._committer.commit_region_revision(
            staged,
            revision,
            expected_current_revision_id=expected_current_revision_id,
        )
        if result.status is RegionCommitStatus.APPLIED:
            _sync_region_state(region, staged)
            return replace(revision, revision_no=result.revision_no or 0)
        if (
            result.status is RegionCommitStatus.INPUT_REVISION_CHANGED
            and expected_current_revision_id is not None
        ):
            raise RegionRevisionChanged()
        raise RuntimeError(f"region revision commit failed: {result.detail}")

    # ------------------------------------------------------------------
    # optimistic-guard helpers (V11R-F0-1)
    # ------------------------------------------------------------------

    def _resolve_expected_current(
        self,
        region: Region,
        expected_revision_no: int | None,
        expected_current_revision_id: str | None = None,
    ) -> str | None:
        """Translate a caller-visible revision NUMBER into the opaque
        revision id the commit seam compares.

        Follows the frozen ``set_region_type``/``restore_region_revision``
        semantics: an unknown revision number or a number that is not the
        current pointer is a stale expectation -> ``RegionRevisionChanged``
        (wire: INPUT_REVISION_CHANGED/conflict) with zero write. ``None``
        keeps the historical unguarded behaviour for pre-V11R callers.
        """
        if expected_revision_no is None:
            return expected_current_revision_id
        expected = self._repo.get_revision(region.region_id, expected_revision_no)
        if (
            expected is None
            or region.current_revision_id != expected.region_revision_id
        ):
            raise RegionRevisionChanged()
        return expected.region_revision_id

    def _assert_current_revision(
        self, region: Region, expected_revision_no: int | None
    ) -> None:
        """Guard a write that does not pass through the commit seam (soft
        delete / pin). The Core sidecar serves requests serially, so the
        read-check-write window is bounded by the single request loop; the
        mutation itself never rewrites revision-owned state."""
        self._resolve_expected_current(region, expected_revision_no)

    def _expected_current_ids(
        self,
        regions: list[Region],
        expected_revisions: dict[str, int] | None,
    ) -> dict[str, str]:
        """Resolve the per-region optimistic guards of a multi-region write.

        ``None`` keeps the unguarded behaviour. Otherwise every affected
        region is compared BEFORE any mutation of the batch; a stale or
        unknown expectation aborts the whole batch with zero write.
        (Coverage of exactly the affected region ids is validated by the
        command layer, which owns the wire request shape.)
        """
        if expected_revisions is None:
            return {}
        resolved: dict[str, str] = {}
        for region in regions:
            revision_no = expected_revisions.get(region.region_id)
            if revision_no is None:
                raise RegionRevisionChanged()
            resolved[region.region_id] = self._resolve_expected_current(
                region, revision_no
            )  # type: ignore[assignment]
        return resolved

    def current_revision(self, region_id: str) -> RegionRevision:
        """The immutable revision the current pointer targets (raises when the
        TASK-002 §2.1 pointer does not resolve instead of fabricating one).

        Read helper for the write-side wire projections (V11R-F0-1): the
        post-write effective state is read back from the SAME authoritative
        objects, no second query path is invented."""
        region = self._require_region(region_id)
        for revision in self._repo.list_revisions(region_id):
            if revision.region_revision_id == region.current_revision_id:
                return revision
        raise RuntimeError(
            f"current revision pointer of region {region_id} does not resolve"
        )

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

    def delete_region(
        self, region_id: str, *, expected_revision_no: int | None = None
    ) -> None:
        """Soft-delete one region (V11R-F0-1 guard added).

        Deletion is NOT a revision-owned write: the region row keeps its
        current/pinned revision and history untouched, only ``deleted_at`` is
        set, so the deletion itself creates no revision. The optional
        ``expected_revision_no`` is the caller-visible optimistic guard
        (stale -> :class:`RegionRevisionChanged`, zero write).
        """
        region = self._require_region(region_id)
        self._assert_current_revision(region, expected_revision_no)
        region.soft_delete()
        self._repo.update_region(region)

    # ------------------------------------------------------------------
    # region retype (M2-REGION-RETYPE-CORE, contract M2-C1 rev 1.4 §5.4)
    # ------------------------------------------------------------------

    def set_region_type(
        self,
        region_id: str,
        new_region_type: str | RegionType,
        *,
        current_global_sfx_policy: str | SfxPolicy,
        expected_revision_no: int | None = None,
    ) -> GuardedWriteOutcome:
        """Retype one region (contract M2-C1 rev 1.4 §5.4): exactly ONE new
        revision through the existing commit seam, ``origin`` always USER,
        ``review_state`` UNREVIEWED (a type decision never signals a text
        proofreading need).

        EV-8 (RULED): retyping TO sfx re-snapshots ``sfx_policy`` from the
        GLOBAL configuration at retype time (the caller passes the current
        global value; creation-time semantics, core_assembly.py precedent);
        retyping to any NON-sfx type forces SKIP so the policy can never
        leak onto non-SFX regions. The snapshot delta against the previous
        revision is therefore region_type + sfx_policy ONLY — text, style,
        locks, reading_order and geometry are preserved verbatim (§10
        manual-edit protection; no confirmed translation falls back to
        needs-review).

        ``expected_revision_no`` is the optional optimistic guard (C4): a
        mismatch is a typed INPUT_REVISION_CHANGED with zero write; the
        matching id is re-checked inside the commit seam, the same
        double-check the guarded machine writes get (D06 §90)."""
        region = self._require_region(region_id)
        expected_current_revision_id: str | None = None
        if expected_revision_no is not None:
            expected_revision = self._repo.get_revision(region_id, expected_revision_no)
            if (
                expected_revision is None
                or region.current_revision_id != expected_revision.region_revision_id
            ):
                return GuardedWriteOutcome(
                    GuardStatus.INPUT_REVISION_CHANGED,
                    conflicts=(region_id,),
                    detail=(
                        f"expected current revision {expected_revision_no},"
                        f" current pointer targets a different revision"
                    ),
                )
            expected_current_revision_id = expected_revision.region_revision_id
        target_type = RegionType(new_region_type)
        staged = _clone_region(region)
        staged.apply_type(target_type)
        staged.apply_sfx_policy(
            effective_sfx_policy(target_type, current_global_sfx_policy)
        )
        revision = self._build_revision(
            staged, RegionOrigin.USER, ReviewState.UNREVIEWED
        )
        result = self._commit(
            region, staged, revision,
            expected_current_revision_id=expected_current_revision_id,
        )
        if result.status is not RegionCommitStatus.APPLIED:
            if result.status is RegionCommitStatus.INPUT_REVISION_CHANGED:
                # C4: the seam-side guard lost — typed conflict outcome with
                # zero write, same semantics as the pre-seam guard above.
                return GuardedWriteOutcome(
                    _guard_status_of(result), detail=result.detail
                )
            # r1 P2-2 (rev 1.4 §5.4): a human retype never degrades into a
            # machine write candidate. DB_FAILED is a persistence fault and
            # LOCK_CHANGED cannot legitimately gate the user channel (the
            # user path passes no lock snapshot into the seam); both escalate
            # fail-loud (core_service maps RuntimeError to UNKNOWN/internal),
            # matching _commit_user_or_raise semantics.
            raise RuntimeError(
                f"region retype commit failed: {result.status.value}:"
                f" {result.detail}"
            )
        return GuardedWriteOutcome(
            GuardStatus.APPLIED, revision_no=result.revision_no
        )

    def list_region_summaries(
        self, page_id: str, *, page_size: tuple[int, int] | None = None
    ) -> list[dict[str, object]]:
        """RegionListSummary read channel (contract M2-C1 §5.4 ListRegions):
        the minimal retype-decision DTO per live region, in
        ``reading_order`` ascending. ``origin``/``revision_no`` come from the
        revision the current pointer targets, so machine pens and human
        retypes stay distinguishable (UI design A7). No text or annotation
        semantics ride this face.

        ``page_size`` (M2-WORKBENCH-REACT-1, contract rev 1.5 additive
        widening): when the caller injects the page's ``(width, height)``
        pixel extent, each summary row gains an OPTIONAL normalized
        ``geometry`` field (the D5 read-face gap; ``application/
        editing/region_canvas.py`` owns the single reverse mapping). Omitting
        it keeps the frozen five-field shape verbatim -- strictly additive,
        pre-existing callers are untouched."""
        summaries: list[dict[str, object]] = []
        for region in self.list_regions(page_id):
            current = next(
                (
                    rev
                    for rev in self._repo.list_revisions(region.region_id)
                    if rev.region_revision_id == region.current_revision_id
                ),
                None,
            )
            if current is None:
                # TASK-002 §2.1 invariant broken: fail loudly instead of
                # fabricating a plausible summary row.
                raise RuntimeError(
                    f"current revision pointer of region {region.region_id}"
                    " does not resolve"
                )
            summary: dict[str, object] = {
                "region_id": region.region_id,
                "region_type": region.region_type.value,
                "sfx_policy": region.sfx_policy.value,
                "origin": current.origin.value,
                "revision_no": current.revision_no,
            }
            if page_size is not None:
                page_w, page_h = page_size
                summary["geometry"] = page_geometry_to_normalized(
                    region.geometry, page_w, page_h
                )
            summaries.append(summary)
        return summaries

    def list_revision_summaries(self, region_id: str) -> dict[str, object]:
        """Return the frozen, read-only revision history projection."""
        region = self._require_region(region_id)
        revisions = self._repo.list_revisions(region_id)
        current = next(
            (rev for rev in revisions if rev.region_revision_id == region.current_revision_id),
            None,
        )
        if current is None:
            raise RuntimeError("current region revision pointer does not resolve")
        return {
            "region_id": region_id,
            "current_revision_no": current.revision_no,
            "revisions": [
                {
                    "region_revision_id": rev.region_revision_id,
                    "revision_no": rev.revision_no,
                    "origin": rev.origin.value,
                    "review_state": rev.review_state.value,
                    "is_pinned": rev.is_pinned,
                    "restored_from_revision_id": rev.restored_from_revision_id,
                    "created_at": rev.created_at,
                    "region_type": rev.snapshot["region_type"],
                    "sfx_policy": rev.snapshot["sfx_policy"],
                    "is_current": rev.region_revision_id == region.current_revision_id,
                }
                for rev in revisions
            ],
        }

    # ------------------------------------------------------------------
    # geometry (AC-REGION-002, D06 §87 "Geometry 保存")
    # ------------------------------------------------------------------

    def save_geometry(
        self,
        region_id: str,
        geometry: RegionGeometry,
        *,
        expected_current_revision_id: str | None = None,
        expected_revision_no: int | None = None,
    ) -> GuardedWriteOutcome:
        region = self._require_region(region_id)
        expected_current_revision_id = self._resolve_expected_current(
            region, expected_revision_no, expected_current_revision_id
        )
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
        self,
        page_id: str,
        region_ids: list[str],
        *,
        expected_revisions: dict[str, int] | None = None,
    ) -> tuple[Region, tuple[str, ...]]:
        """Merge regions of one page into a new region (D03 §6.4).

        Geometry: covering bbox + concatenated polygons. Text: OCR text and
        machine translation join with a separator; manual protection from
        any source carries over (the merged region still needs its own
        confirmation). Old regions are soft-deleted; the merged region
        starts its own revision history with reading_order = min.

        V11R-F0-1 optimistic guard: ``expected_revisions`` maps every source
        region id to the revision number the caller observed. Every entry is
        compared BEFORE the first write; a stale expectation aborts the
        whole merge with zero write (:class:`RegionRevisionChanged`).
        """
        if len(region_ids) < 2:
            raise ValueError("merge needs at least two regions")
        regions = [self._require_region(rid) for rid in region_ids]
        if any(region.page_id != page_id for region in regions):
            raise ValueError("merge is limited to regions of one page")
        self._expected_current_ids(regions, expected_revisions)

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
        *,
        expected_revision_no: int | None = None,
    ) -> tuple[Region, ...]:
        """Split a region into caller-supplied geometries (editor owns the
        interactive cut). The source region is soft-deleted; each part starts
        a fresh revision history; manual protection carries over.

        V11R-F0-1 optimistic guard: ``expected_revision_no`` is checked
        before the first part is created (stale -> zero write)."""
        source = self._require_region(region_id)
        if len(parts) < 2:
            raise ValueError("split needs at least two parts")
        self._assert_current_revision(source, expected_revision_no)
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

    def reorder_regions(
        self,
        page_id: str,
        ordered_region_ids: list[str],
        *,
        expected_revisions: dict[str, int] | None = None,
    ) -> list[Region]:
        """reading_order is revision-owned state: every changed region gets a
        new user revision through the atomic seam (TASK-028 §3.4).

        V11R-F0-1 optimistic guard: ``expected_revisions`` maps every ordered
        region id to the revision number the caller observed; every entry is
        checked BEFORE the first revision is committed, and each committed
        region additionally carries its expected revision id into the seam's
        in-transaction re-check (zero write on any stale entry)."""
        regions = {region.region_id: region for region in self.list_regions(page_id)}
        missing = [rid for rid in ordered_region_ids if rid not in regions]
        if missing:
            raise RegionNotFound(missing[0])
        expected_ids = self._expected_current_ids(
            [regions[rid] for rid in ordered_region_ids], expected_revisions
        )
        reordered = []
        for position, region_id in enumerate(ordered_region_ids, start=1):
            region = regions[region_id]
            if region.reading_order == position:
                reordered.append(region)
                continue
            staged = _clone_region(region)
            staged.reading_order = position
            self._commit_user_or_raise(
                region,
                staged,
                RegionOrigin.USER,
                ReviewState.UNREVIEWED,
                expected_current_revision_id=expected_ids.get(region_id),
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

    def save_manual_translation(
        self,
        region_id: str,
        edited: str,
        *,
        expected_revision_no: int | None = None,
    ) -> int:
        """User save → new user revision; arms manual protection (§8.4).

        V11R-F0-1: the optional ``expected_revision_no`` guards the write
        (stale -> :class:`RegionRevisionChanged`, zero write). The save is
        intentionally append-only: saving the same text twice still creates
        two revisions (history is never rewritten)."""
        region = self._require_region(region_id)
        expected_current_revision_id = self._resolve_expected_current(
            region, expected_revision_no
        )
        staged = _clone_region(region)
        staged.text.save_manual_translation(edited)
        revision = self._commit_user_or_raise(
            region,
            staged,
            RegionOrigin.USER,
            ReviewState.NEEDS_REVIEW,
            expected_current_revision_id=expected_current_revision_id,
        )
        return revision.revision_no

    def confirm_final(
        self, region_id: str, *, expected_revision_no: int | None = None
    ) -> int:
        """Explicit proofread confirmation → confirmed revision (D06 §87).
        A non-blank edited text becomes the confirmed final (D03 §8.3);
        confirming a region without manual text just locks the review state.

        V11R-F0-1: ``expected_revision_no`` is the same optimistic guard as
        the other user writes (zero write on a stale expectation)."""
        region = self._require_region(region_id)
        expected_current_revision_id = self._resolve_expected_current(
            region, expected_revision_no
        )
        staged = _clone_region(region)
        if staged.text.edited_translation.strip():
            staged.text.confirm_edited_translation()
        else:
            staged.text.refresh_final()
        revision = self._commit_user_or_raise(
            region,
            staged,
            RegionOrigin.USER,
            ReviewState.CONFIRMED,
            expected_current_revision_id=expected_current_revision_id,
        )
        return revision.revision_no

    def set_locks(
        self,
        region_id: str,
        *,
        region_locked: bool | None = None,
        translation_locked: bool | None = None,
        inpaint_locked: bool | None = None,
        expected_revision_no: int | None = None,
    ) -> int:
        """Explicit user lock change → ONE new user revision (D06 §87).

        V11R-F0-1 GAP FILL: the domain exposes the three lock setters but the
        application layer had no use case that persists them through the
        atomic commit seam (the only lock write before this task was the
        implicit arm inside :meth:`save_manual_translation`). This method is
        the thin composition of the EXISTING domain operations and commit
        seam -- no new lock semantics are invented:

        - ``region_locked`` / ``inpaint_locked`` call the existing
          ``Region.set_region_locked`` / ``Region.set_inpaint_locked``;
        - ``translation_locked`` calls ``RegionText.lock_translation`` /
          ``RegionText.unlock_translation`` (the manual-protection flag) AND
          mirrors the value onto ``Region.set_translation_locked`` so the
          region-level lock snapshot the pipeline reads observes the explicit
          user lock too -- the two persisted projections never diverge on
          this path;
        - the revision snapshot therefore carries the lock state exactly like
          every other revision-owned write, and the commit seam's in-
          transaction lock comparison stays available for machine writes
          (the user path passes no lock expectation, same as every other
          user write).

        ``None`` leaves that lock untouched; at least one lock must be
        provided (the command layer enforces the wire shape). Lock changes are
        append-only: every call creates a revision even when the value is
        unchanged (D06 §87 treats the explicit user action as a save)."""
        if region_locked is None and translation_locked is None and inpaint_locked is None:
            raise ValueError("set_locks needs at least one lock")
        region = self._require_region(region_id)
        expected_current_revision_id = self._resolve_expected_current(
            region, expected_revision_no
        )
        staged = _clone_region(region)
        if region_locked is not None:
            staged.set_region_locked(region_locked)
        if inpaint_locked is not None:
            staged.set_inpaint_locked(inpaint_locked)
        if translation_locked is not None:
            if translation_locked:
                staged.text.lock_translation()
            else:
                staged.text.unlock_translation()
            # Keep the region-level projection (the pipeline lock snapshot)
            # in sync with the manual-protection flag (see the docstring).
            staged.set_translation_locked(translation_locked)
        revision = self._commit_user_or_raise(
            region,
            staged,
            RegionOrigin.USER,
            ReviewState.UNREVIEWED,
            expected_current_revision_id=expected_current_revision_id,
        )
        return revision.revision_no

    # ------------------------------------------------------------------
    # revisions: restore / pin (AC-REV-003/004)
    # ------------------------------------------------------------------

    def restore_revision(self, region_id: str, revision_no: int) -> Region:
        """AC-REV-004: copy the snapshot into a NEW revision with provenance;
        current then points at the restored copy, history stays intact. The
        observed current id is always passed into the atomic seam, including
        for legacy callers that do not supply an explicit expected revision."""
        region, _revision_no = self.restore_revision_with_number(region_id, revision_no)
        return region

    def restore_revision_with_number(
        self,
        region_id: str,
        revision_no: int,
        *,
        expected_revision_no: int | None = None,
    ) -> tuple[Region, int]:
        """Restore a snapshot and return the committed number for its new copy."""
        region = self._require_region(region_id)
        revisions = self._repo.list_revisions(region_id)
        current = next(
            (rev for rev in revisions if rev.region_revision_id == region.current_revision_id),
            None,
        )
        if current is None:
            raise RuntimeError("current region revision pointer does not resolve")
        if expected_revision_no is not None and current.revision_no != expected_revision_no:
            raise RegionRevisionChanged()
        source = self._repo.get_revision(region_id, revision_no)
        if source is None:
            raise RegionRevisionNotFound()
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
        result = self._committer.commit_region_revision(
            staged,
            revision,
            expected_current_revision_id=current.region_revision_id,
            lock_snapshot=RegionLockSnapshot(
                region_locked=region.region_locked,
                translation_locked=region.translation_locked,
                inpaint_locked=region.inpaint_locked,
            ),
        )
        if result.status in (
            RegionCommitStatus.INPUT_REVISION_CHANGED,
            RegionCommitStatus.LOCK_CHANGED,
        ):
            raise RegionRevisionChanged()
        if result.status is not RegionCommitStatus.APPLIED:
            raise RuntimeError(f"region revision commit failed: {result.detail}")
        _sync_region_state(region, staged)
        return region, result.revision_no or 0

    def set_revision_pinned(
        self,
        region_id: str,
        revision_no: int,
        pinned: bool,
        *,
        expected_revision_no: int | None = None,
    ) -> None:
        """AC-REV-003: pin is a dedicated single-purpose transaction that
        only flips is_pinned — immutable history is never upserted.

        V11R-F0-1: pinning never rewrites revision-owned state, so it creates
        no revision (the flag lives on the immutable row itself). The optional
        ``expected_revision_no`` guards that the CURRENT pointer is still the
        revision the caller saw; an unknown target revision is the typed
        :class:`RegionRevisionNotFound`."""
        region = self._require_region(region_id)
        self._assert_current_revision(region, expected_revision_no)
        try:
            self._repo.set_revision_pinned(region_id, revision_no, pinned)
        except LookupError as error:
            raise RegionRevisionNotFound(
                f"revision {revision_no} not found for region {region_id}"
            ) from error


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
