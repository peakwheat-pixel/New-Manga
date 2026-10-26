"""Region model, geometry round-trip, merge/split, reading order, restart
persistence (AC-REGION-001~004)."""

import pytest

from application.editing.service import EditingSession, RegionEditingService
from domain.regions.entities import BBox, RegionGeometry, RegionType

from region_helpers import InMemoryRegionRepository


def _geometry(x=10, y=20, w=100, h=50, polygon=()):
    return RegionGeometry(bbox=BBox(x, y, w, h), polygon=polygon)


def test_create_region_sets_first_revision_and_defaults(service, repo, page_id):
    region = service.create_region(page_id, _geometry())
    assert region.reading_order == 1  # auto-incremented per page
    # TASK-002 §2.1: current pointer is non-null at creation.
    assert region.current_revision_id is not None
    revisions = repo.list_revisions(region.region_id)
    assert [r.revision_no for r in revisions] == [1]

    second = service.create_region(page_id, _geometry())
    assert second.reading_order == 2


def test_geometry_roundtrip_through_snapshot(service, repo, page_id):
    polygon = ((0, 0), (40, 0), (40, 30))
    region = service.create_region(page_id, _geometry(polygon=polygon))

    snapshot = region.snapshot_state()
    restored_geometry = RegionGeometry.from_jsonable(snapshot["geometry"])
    assert restored_geometry.bbox.as_tuple() == (10, 20, 100, 50)
    assert restored_geometry.polygon == polygon
    assert RegionGeometry.from_jsonable(
        RegionGeometry.from_jsonable(snapshot["geometry"]).as_jsonable()
    ) == restored_geometry


def test_geometry_edit_move_scale_polygon_creates_revision(service, repo, page_id):
    region = service.create_region(page_id, _geometry())
    outcome = service.save_geometry(region.region_id, _geometry(30, 40, 80, 60))
    assert outcome.status.value == "applied"
    assert outcome.revision_no == 2

    region = service.get_region(region.region_id)
    assert region.geometry.bbox.as_tuple() == (30, 40, 80, 60)
    assert [r.revision_no for r in repo.list_revisions(region.region_id)] == [1, 2]

    # Region type + SFX policy are settable on the unified model (AC-REGION-004).
    region.apply_type(RegionType.SFX)
    assert region.region_type is RegionType.SFX


def test_merge_regions_unifies_geometry_and_soft_deletes_sources(service, repo, page_id):
    a = service.create_region(page_id, _geometry(0, 0, 50, 40))
    b = service.create_region(page_id, _geometry(30, 10, 60, 50))
    a_text = service.get_region(a.region_id)
    a_text.text.apply_ocr("Hello")
    repo.update_region(a_text)

    merged, deleted = service.merge_regions(page_id, [a.region_id, b.region_id])
    assert deleted == (a.region_id, b.region_id)
    # Covering bbox of (0,0,50,40) and (30,10,60,50).
    assert merged.geometry.bbox.as_tuple() == (0, 0, 90, 60)
    assert merged.text.ocr_text == "Hello"
    # Soft-deleted sources are hidden from the service but traceable in the repo.
    assert repo.get_region(a.region_id).deleted
    assert repo.get_region(b.region_id).deleted
    assert [r.region_id for r in service.list_regions(page_id)] == [merged.region_id]
    # The merged region has its own first revision.
    assert repo.list_revisions(merged.region_id)[0].revision_no == 1


def test_split_region_creates_protected_parts(service, repo, page_id):
    region = service.create_region(page_id, _geometry(0, 0, 100, 50))
    service.save_manual_translation(region.region_id, "人工译文")

    parts = [_geometry(0, 0, 50, 50), _geometry(50, 0, 50, 50)]
    created = service.split_region(region.region_id, parts)
    assert len(created) == 2
    assert repo.get_region(region.region_id).deleted
    for index, part in enumerate(created):
        assert part.geometry.bbox.as_tuple() == (50 * index, 0, 50, 50)
        # Manual protection carries over to the split parts.
        assert part.text.translation_locked is True
        assert part.text.manual_edited is True
        assert part.text.ocr_text == "人工译文" or part.text.ocr_text == ""


def test_reading_order_manual_adjustment_and_context_order(service, repo, page_id):
    first = service.create_region(page_id, _geometry())
    second = service.create_region(page_id, _geometry(200, 0))
    third = service.create_region(page_id, _geometry(400, 0))

    service.reorder_regions(page_id, [third.region_id, first.region_id, second.region_id])
    context_order = service.reading_order_for_context(page_id)
    # Translation context uses the final manual order (D03 §6.5).
    assert [r.region_id for r in context_order] == [
        third.region_id, first.region_id, second.region_id,
    ]
    assert [r.reading_order for r in context_order] == [1, 2, 3]


def test_geometry_and_regions_survive_simulated_restart(service, page_id):
    # AC-REGION-002: 保存后重启应用仍存在 — fresh service over the same repo.
    repo = InMemoryRegionRepository()
    first = RegionEditingService(repo)
    region = first.create_region(page_id, _geometry(5, 5, 70, 90))
    first.save_manual_translation(region.region_id, "保存的译文")
    first.save_geometry(region.region_id, _geometry(9, 9, 70, 90))

    restarted = RegionEditingService(repo)
    loaded = restarted.get_region(region.region_id)
    assert loaded.geometry.bbox.as_tuple() == (9, 9, 70, 90)
    assert loaded.text.edited_translation == "保存的译文"
    assert loaded.current_revision_id == region.current_revision_id
    assert [r.revision_no for r in repo.list_revisions(region.region_id)] == [1, 2, 3]


def test_dirty_session_flush_before_switch(service, page_id):
    # AC3: 明确保存或获批 autosave 在切换前 flush — staged edits are lost
    # unless flushed, and flush persists them as revisions.
    session = EditingSession(service, page_id)
    region = service.create_region(page_id, _geometry())

    session.stage_geometry(region.region_id, _geometry(1, 1, 10, 10))
    session.stage_manual_translation(region.region_id, "未保存草稿")
    assert session.has_unsaved_changes
    assert region.region_id in session.dirty_region_ids

    saved = session.flush()
    assert saved[region.region_id] > 0
    assert not session.has_unsaved_changes

    persisted = service.get_region(region.region_id)
    assert persisted.geometry.bbox.as_tuple() == (1, 1, 10, 10)
    assert persisted.text.edited_translation == "未保存草稿"
    assert persisted.text.translation_locked is True

    # Explicit discard throws the staged edit away instead of flushing.
    session2 = EditingSession(service, page_id)
    session2.stage_manual_translation(region.region_id, "将被丢弃")
    session2.discard(region.region_id)
    assert not session2.has_unsaved_changes
    assert service.get_region(region.region_id).text.edited_translation == "未保存草稿"
