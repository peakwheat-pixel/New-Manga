"""Optimistic-guard + explicit-lock use cases of the Region write face
(V11R-F0-1), exercised at the application layer with the in-memory repository
(the same contract-faithful fake the editing suite already uses).

These tests pin the semantics the wire tests build on:

- a stale ``expected_revision_no`` / ``expected_revisions`` entry is the typed
  ``RegionRevisionChanged`` with ZERO write (no region deleted, no revision
  committed);
- ``set_locks`` creates exactly ONE user revision through the same commit
  seam, keeps the text-level manual-protection flag and the region-level lock
  projection in sync, and is the thin composition of the existing domain
  setters (the application-layer GAP filled by V11R-F0-1);
- pin never creates a revision and reports an unknown target revision as the
  typed ``RegionRevisionNotFound``.
"""

from __future__ import annotations

import pytest

from application.editing.errors import RegionRevisionChanged, RegionRevisionNotFound
from application.editing.service import RegionEditingService
from domain.regions.entities import BBox, RegionGeometry


def _geometry(x=10, y=20, w=100, h=50):
    return RegionGeometry(bbox=BBox(x, y, w, h))


def test_expected_revision_guard_is_typed_and_zero_write(service, repo, page_id):
    region = service.create_region(page_id, _geometry())
    revisions_before = len(repo.list_revisions(region.region_id))

    with pytest.raises(RegionRevisionChanged):
        service.save_geometry(
            region.region_id, _geometry(30, 40, 80, 60), expected_revision_no=99
        )
    with pytest.raises(RegionRevisionChanged):
        service.save_manual_translation(
            region.region_id, "x", expected_revision_no=99
        )
    with pytest.raises(RegionRevisionChanged):
        service.confirm_final(region.region_id, expected_revision_no=99)
    with pytest.raises(RegionRevisionChanged):
        service.delete_region(region.region_id, expected_revision_no=99)
    with pytest.raises(RegionRevisionChanged):
        service.split_region(
            region.region_id, [_geometry(), _geometry()], expected_revision_no=99
        )

    # zero write: the region is still live, geometry/text untouched, history
    # unchanged.
    stored = service.get_region(region.region_id)
    assert stored.geometry.bbox.as_tuple() == (10, 20, 100, 50)
    assert stored.text.edited_translation == ""
    assert len(repo.list_revisions(region.region_id)) == revisions_before


def test_matching_expected_revision_applies_the_write(service, repo, page_id):
    region = service.create_region(page_id, _geometry())
    outcome = service.save_geometry(
        region.region_id, _geometry(30, 40, 80, 60), expected_revision_no=1
    )
    assert outcome.status.value == "applied"
    assert outcome.revision_no == 2


def test_set_locks_creates_one_revision_and_syncs_both_projections(
    service, repo, page_id
):
    region = service.create_region(page_id, _geometry())
    revision_no = service.set_locks(
        region.region_id,
        region_locked=True,
        translation_locked=True,
        inpaint_locked=True,
    )
    assert revision_no == 2
    stored = service.get_region(region.region_id)
    # Domain-level locks (Region fields) ...
    assert stored.region_locked is True
    assert stored.translation_locked is True
    assert stored.inpaint_locked is True
    # ... and the manual-protection flag the translation step reads.
    assert stored.text.translation_locked is True
    # Lock state rides the revision snapshot (D06 §87).
    snapshot = repo.list_revisions(region.region_id)[-1].snapshot
    assert snapshot["region_locked"] is True
    assert snapshot["translation_locked"] is True
    assert snapshot["inpaint_locked"] is True
    assert snapshot["text"]["translation_locked"] is True


def test_set_locks_unlock_clears_both_translation_projections(
    service, repo, page_id
):
    region = service.create_region(page_id, _geometry())
    service.save_manual_translation(region.region_id, "人工译文")
    assert service.get_region(region.region_id).text.translation_locked is True

    service.set_locks(region.region_id, translation_locked=False)
    stored = service.get_region(region.region_id)
    assert stored.translation_locked is False
    assert stored.text.translation_locked is False
    # Unlocking never rewrites the manual text itself.
    assert stored.text.edited_translation == "人工译文"


def test_set_locks_requires_at_least_one_lock(service, page_id):
    region = service.create_region(page_id, _geometry())
    with pytest.raises(ValueError):
        service.set_locks(region.region_id)
    with pytest.raises(RegionRevisionChanged):
        service.set_locks(
            region.region_id, region_locked=True, expected_revision_no=42
        )


def test_multi_region_guard_aborts_the_whole_batch(service, repo, page_id):
    first = service.create_region(page_id, _geometry(0, 0, 50, 40))
    second = service.create_region(page_id, _geometry(60, 0, 50, 40))

    with pytest.raises(RegionRevisionChanged):
        service.merge_regions(
            page_id,
            [first.region_id, second.region_id],
            expected_revisions={first.region_id: 1, second.region_id: 2},
        )
    # zero write: both sources are still live and their history is unchanged.
    live = {region.region_id for region in service.list_regions(page_id)}
    assert live == {first.region_id, second.region_id}
    assert len(repo.list_revisions(first.region_id)) == 1
    assert len(repo.list_revisions(second.region_id)) == 1

    with pytest.raises(RegionRevisionChanged):
        service.reorder_regions(
            page_id,
            [second.region_id, first.region_id],
            expected_revisions={first.region_id: 9, second.region_id: 1},
        )
    assert len(repo.list_revisions(first.region_id)) == 1
    assert len(repo.list_revisions(second.region_id)) == 1


def test_pin_does_not_create_revision_and_rejects_unknown_target(
    service, repo, page_id
):
    region = service.create_region(page_id, _geometry())
    service.set_revision_pinned(region.region_id, 1, True)
    assert repo.list_revisions(region.region_id)[0].is_pinned is True
    assert len(repo.list_revisions(region.region_id)) == 1

    with pytest.raises(RegionRevisionNotFound):
        service.set_revision_pinned(region.region_id, 99, True)
    with pytest.raises(RegionRevisionChanged):
        service.set_revision_pinned(
            region.region_id, 1, True, expected_revision_no=5
        )
