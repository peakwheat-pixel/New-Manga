"""Four-level text, final resolution, manual protection, re-OCR hints,
optimistic write guard and revision restore/pin (AC-OCR-002, AC-TRANS-001/
002, AC-REV-003/004, D06 §87~90)."""

import pytest

from application.editing.errors import GuardStatus
from domain.regions.entities import RegionOrigin, ReviewState


def test_four_level_text_fields_exist(service, page_id):
    region = service.create_region(page_id, _geo())
    service.apply_ocr_result(region.region_id, "こんにちは")
    service.apply_machine_translation(region.region_id, "你好")
    # AC-TRANS-001: all four levels distinguishable on one model.
    assert region.text.ocr_text == "こんにちは"
    assert region.text.machine_translation == "你好"
    assert region.text.edited_translation == ""
    # D03 §8.3: no confirmed manual edit → final falls back to machine.
    assert region.text.final_translation == "你好"
    assert region.text.final_source == "machine"


def _geo():
    from domain.regions.entities import BBox, RegionGeometry

    return RegionGeometry(bbox=BBox(0, 0, 10, 10))


def test_final_resolution_rules(service, page_id):
    region = service.create_region(page_id, _geo())
    service.apply_ocr_result(region.region_id, "原文")

    # 空白 edited 且无机器译文 → final 为空（none）。
    region.text.edited_translation = "   "
    region.text.refresh_final()
    assert region.text.final_translation == ""
    assert region.text.final_source == "none"

    # 机器译文存在但 edited 未确认 → machine wins（AC-TRANS-001 提示场景）。
    service.apply_machine_translation(region.region_id, "机译")
    region.text.edited_translation = "人工未确认"
    region.text.refresh_final()
    assert region.text.final_translation == "机译"
    assert region.text.final_source == "machine"

    # 人工确认 → edited wins (D03 §8.3)。
    service.save_manual_translation(region.region_id, "人工译文")
    service.confirm_final(region.region_id)
    assert region.text.final_translation == "人工译文"
    assert region.text.final_source == "edited"

    # Nothing at all → empty final.
    empty = service.create_region(page_id, _geo())
    empty.text.refresh_final()
    assert empty.text.final_translation == "" and empty.text.final_source == "none"


def test_manual_save_arms_protection(service, page_id):
    region = service.create_region(page_id, _geo())
    service.apply_ocr_result(region.region_id, "原文")
    service.save_manual_translation(region.region_id, "我的译文")

    # AC-TRANS-002: manual_edited + translation_locked set automatically.
    assert region.text.manual_edited is True
    assert region.text.translation_locked is True

    # Explicit unlock is the only automatic-free path (D03 §8.4).
    region.text.unlock_translation()
    assert region.text.translation_locked is False


def test_reocr_keeps_manual_translation_and_hints(service, page_id):
    region = service.create_region(page_id, _geo())
    service.apply_ocr_result(region.region_id, "旧原文")
    service.save_manual_translation(region.region_id, "人工定稿")
    manual_before = region.text.edited_translation
    final_before = region.text.final_translation
    current_before = region.current_revision_id

    outcome = service.apply_ocr_result(region.region_id, "新原文")
    # AC-OCR-002: ocr updated, manual译文/final preserved, hint raised.
    assert outcome.status is GuardStatus.APPLIED
    assert outcome.retranslate_hint is True
    assert region.text.ocr_text == "新原文"
    assert region.text.edited_translation == manual_before
    assert region.text.final_translation == final_before
    assert region.current_revision_id != current_before

    # Unchanged source text produces no hint.
    outcome = service.apply_ocr_result(region.region_id, "新原文")
    assert outcome.retranslate_hint is False


def test_machine_translation_blocked_by_translation_lock(service, page_id):
    region = service.create_region(page_id, _geo())
    service.save_manual_translation(region.region_id, "人工")

    outcome = service.apply_machine_translation(region.region_id, "机器译文")
    assert outcome.status is GuardStatus.LOCK_CHANGED
    assert region.text.machine_translation == ""
    assert region.text.edited_translation == "人工"

    region.text.unlock_translation()
    outcome = service.apply_machine_translation(region.region_id, "机器译文")
    assert outcome.status is GuardStatus.APPLIED
    assert region.text.machine_translation == "机器译文"
    assert region.text.edited_translation == "人工"  # manual edit survives


def test_background_result_rejected_when_revision_advanced(service, page_id):
    """D06 §90 / 契约 V01: step starts at revision 10; user saves revision 12;
    the background write must not overwrite — current stays at 12."""
    region = service.create_region(page_id, _geo())
    stale_view = region.current_revision_id  # step started here ("revision 10")
    service.save_manual_translation(region.region_id, "人工12")  # user saves 12
    guard_no = region.current_revision_id

    outcome = service.apply_machine_translation(
        region.region_id,
        "后台结果",
        expected_current_revision_id=stale_view,
    )
    assert outcome.status is GuardStatus.INPUT_REVISION_CHANGED
    assert outcome.conflicts == (region.region_id,)
    # Current untouched; manual content intact; machine text not applied.
    assert region.current_revision_id == guard_no
    assert region.text.edited_translation == "人工12"
    assert region.text.machine_translation == ""

    # Even with a matching expectation the armed translation lock wins (§89);
    # only after the user releases the lock can a machine result apply.
    stale_outcome = service.apply_machine_translation(
        region.region_id,
        "后台结果",
        expected_current_revision_id=region.current_revision_id,
    )
    assert stale_outcome.status is GuardStatus.LOCK_CHANGED

    region.text.unlock_translation()
    outcome = service.apply_machine_translation(
        region.region_id,
        "后台结果",
        expected_current_revision_id=region.current_revision_id,
    )
    assert outcome.status is GuardStatus.APPLIED
    assert region.text.machine_translation == "后台结果"


def test_restore_revision_creates_new_revision_with_provenance(service, repo, page_id):
    region = service.create_region(page_id, _geo())
    service.apply_ocr_result(region.region_id, "v2原文")
    service.save_manual_translation(region.region_id, "v3人工")

    history = repo.list_revisions(region.region_id)
    assert [r.revision_no for r in history] == [1, 2, 3]

    # AC-REV-004: restore → tracked record → current points at the restored copy.
    restored = service.restore_revision(region.region_id, 1)
    revisions = repo.list_revisions(region.region_id)
    assert [r.revision_no for r in revisions] == [1, 2, 3, 4]
    restore_record = revisions[-1]
    assert restore_record.origin is RegionOrigin.RESTORED
    assert restore_record.restored_from_revision_id == history[0].region_revision_id
    assert restored.current_revision_id == restore_record.region_revision_id
    assert restored.text.ocr_text == ""  # snapshot of revision 1

    # History is never rewritten: revision 3 still holds the manual text.
    assert "v3人工" in revisions[2].snapshot["text"]["edited_translation"]


def test_pin_revision_flag(service, repo, page_id):
    region = service.create_region(page_id, _geo())
    service.save_manual_translation(region.region_id, "重要")

    service.set_revision_pinned(region.region_id, 2, True)
    assert repo.get_revision(region.region_id, 2).is_pinned is True
    # AC-REV-003: pinned survives cleanup semantics (cleanup itself is TASK-021).
    service.set_revision_pinned(region.region_id, 2, False)
    assert repo.get_revision(region.region_id, 2).is_pinned is False


def test_review_states_flow(service, repo, page_id):
    region = service.create_region(page_id, _geo())
    first = repo.list_revisions(region.region_id)[0]
    assert first.review_state is ReviewState.UNREVIEWED

    outcome = service.apply_ocr_result(region.region_id, "ocr")
    machine_revision = repo.get_revision(region.region_id, outcome.revision_no)
    # Machine writes default to needs_review (D03 §6.6).
    assert machine_revision.review_state is ReviewState.NEEDS_REVIEW
    assert machine_revision.origin is RegionOrigin.MACHINE

    confirmed_no = service.confirm_final(region.region_id)
    confirmed = repo.get_revision(region.region_id, confirmed_no)
    assert confirmed.review_state is ReviewState.CONFIRMED
