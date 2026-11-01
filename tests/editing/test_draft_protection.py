from __future__ import annotations

from pathlib import Path
import json
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.errors import DraftError
from bootstrap.core_service import assemble_production_core
from domain.regions.entities import BBox, RegionGeometry
from infrastructure.filesystem.draft_journal import DraftJournalError

NOW = "2026-11-02T00:00:00.000+00:00"


def _close(core) -> None:
    if core.drafts is not None:
        core.drafts.journal.close()
    core.conn.close()


def _seed_page(core, page_id: str = "page-draft") -> str:
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id,title,created_at,updated_at) VALUES ('book-draft','b',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id,book_id,title,created_at,updated_at) VALUES ('chapter-draft','book-draft','c',?,?)",
            (NOW, NOW),
        )
        core.conn.execute(
            "INSERT INTO pages (page_id,chapter_id,sort_order,created_at,updated_at,width,height) VALUES (?, 'chapter-draft',0,?,?,800,1200)",
            (page_id, NOW, NOW),
        )
    return page_id


def _new_region(core, page_id: str, region_id: str):
    del region_id
    return core.editing.create_region(
        page_id, RegionGeometry(bbox=BBox(10, 20, 100, 80))
    )


def _open_and_patch(core, page_id: str, region_id: str, text: str = "draft text"):
    service = core.drafts
    region = core.editing.get_region(region_id)
    lease = service.open_draft(
        "session-1", page_id, region_id,
        base_revision_id=region.current_revision_id,
        page_binding_version=913,
    )
    service.patch_draft(
        lease.draft.draft_id, "session-1", {"text": {"edited_translation": text}},
        schedule_flush=False,
    )
    return lease.draft.draft_id, service.issue_edit_token(lease.draft.draft_id)


@pytest.fixture()
def core(tmp_path: Path):
    assembled = assemble_production_core(tmp_path / "data")
    _seed_page(assembled)
    try:
        yield assembled
    finally:
        _close(assembled)


def test_production_assembly_candidate_only_apply_receipt_replay_and_legacy_append(core) -> None:
    region = _new_region(core, "page-draft", "region-candidate")
    before = core.editing.get_region(region.region_id).current_revision_id
    draft_id, token = _open_and_patch(core, "page-draft", region.region_id)
    candidate = core.drafts.prepare_candidate(
        region.region_id, {"text": {"edited_translation": "draft text"}},
        origin="user", draft_id=draft_id,
    )
    assert set(candidate.to_json()) == {"candidateId", "RegionId", "BaseRevisionId", "origin"}
    assert core.editing.get_region(region.region_id).current_revision_id == before
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
    ).fetchone()[0] == 1

    applied = core.drafts.apply_candidates(token, [candidate.candidate_id])
    assert set(applied) == {region.region_id}
    assert core.editing.get_region(region.region_id).current_revision_id == applied[region.region_id]
    assert core.drafts.apply_candidates(token) == applied
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
    ).fetchone()[0] == 2

    # R-LEGACY: the old path remains append-only for identical content.
    core.editing.save_manual_translation(region.region_id, "same text")
    core.editing.save_manual_translation(region.region_id, "same text")
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
    ).fetchone()[0] == 4


def test_same_token_different_content_is_rejected_before_stale_check(core) -> None:
    region = _new_region(core, "page-draft", "region-token-reused")
    draft_id, token = _open_and_patch(core, "page-draft", region.region_id)
    first = core.drafts.prepare_candidate(
        region.region_id, {"text": {"edited_translation": "first"}},
        origin="user", draft_id=draft_id,
    )
    second = core.drafts.prepare_candidate(
        region.region_id, {"text": {"edited_translation": "different"}},
        origin="user", draft_id=draft_id,
    )
    core.drafts.apply_candidates(token, [first.candidate_id])
    with pytest.raises(DraftError) as error:
        core.drafts.apply_candidates(token, [second.candidate_id])
    assert error.value.code == "EDIT_TOKEN_REUSED"
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
    ).fetchone()[0] == 2


def test_expired_token_is_checked_before_receipt_replay(core) -> None:
    region = _new_region(core, "page-draft", "region-expired")
    draft_id, _token = _open_and_patch(core, "page-draft", region.region_id)
    token = core.drafts.issue_edit_token(draft_id, ttl_seconds=-1)
    candidate = core.drafts.prepare_candidate(
        region.region_id, {"style": {"text_color": "#abc"}},
        origin="user", draft_id=draft_id,
    )
    with pytest.raises(DraftError) as error:
        core.drafts.apply_candidates(token, [candidate.candidate_id])
    assert error.value.code == "EDIT_TOKEN_EXPIRED"
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
    ).fetchone()[0] == 1


def test_multi_region_stale_third_target_rolls_back_first_two(core) -> None:
    regions = [_new_region(core, "page-draft", f"region-batch-{i}") for i in range(3)]
    lease = core.drafts.open_draft(
        "session-batch", "page-draft", None,
        base_revision_id=None, page_binding_version=7,
    )
    candidates = [
        core.drafts.prepare_candidate(
            region.region_id, {"style": {"text_color": f"#00{i}"}},
            origin="user", draft_id=lease.draft.draft_id,
        )
        for i, region in enumerate(regions)
    ]
    token = lease.token
    before = {
        region.region_id: core.editing.get_region(region.region_id).current_revision_id
        for region in regions
    }
    core.editing.apply_ocr_result(regions[2].region_id, "concurrent")
    counts_before_apply = {
        region.region_id: core.conn.execute(
            "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
        ).fetchone()[0]
        for region in regions
    }
    with pytest.raises(DraftError) as error:
        core.drafts.apply_candidates(token, [item.candidate_id for item in candidates])
    assert error.value.code == "STALE_BASE_REVISION"
    for region in regions[:2]:
        assert core.editing.get_region(region.region_id).current_revision_id == before[region.region_id]
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (regions[0].region_id,)
    ).fetchone()[0] == counts_before_apply[regions[0].region_id]
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (regions[1].region_id,)
    ).fetchone()[0] == counts_before_apply[regions[1].region_id]


@pytest.mark.parametrize("changed", [
    "region_locked", "translation_locked", "inpaint_locked",
    "text_translation_locked", "manual_edited",
])
def test_any_protection_bit_change_rejects_candidate(core, changed: str) -> None:
    region = _new_region(core, "page-draft", f"region-lock-{changed}")
    draft_id, token = _open_and_patch(core, "page-draft", region.region_id)
    candidate = core.drafts.prepare_candidate(
        region.region_id, {"style": {"text_color": "#abcdef"}},
        origin="user", draft_id=draft_id,
    )
    if changed in {"region_locked", "translation_locked", "inpaint_locked"}:
        with core.conn:
            core.conn.execute(
                f"UPDATE regions SET {changed}=1 WHERE region_id=?", (region.region_id,)
            )
    else:
        row = core.conn.execute(
            "SELECT text_json FROM regions WHERE region_id=?", (region.region_id,)
        ).fetchone()
        text = json.loads(row["text_json"])
        text["translation_locked" if changed == "text_translation_locked" else changed] = True
        with core.conn:
            core.conn.execute(
                "UPDATE regions SET text_json=? WHERE region_id=?",
                (json.dumps(text, sort_keys=True), region.region_id),
            )
    with pytest.raises(DraftError) as error:
        core.drafts.apply_candidates(token, [candidate.candidate_id])
    assert error.value.code == "LOCK_CHANGED"
    assert core.conn.execute(
        "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
    ).fetchone()[0] == 1


def test_lock_matrix_and_style_whitelist(core) -> None:
    region = _new_region(core, "page-draft", "region-lock-matrix")
    with core.conn:
        core.conn.execute("UPDATE regions SET region_locked=1 WHERE region_id=?", (region.region_id,))
    with pytest.raises(DraftError) as locked:
        core.drafts.prepare_candidate(
            region.region_id, {"style": {"font_size": 13}}, origin="user"
        )
    assert locked.value.code == "LOCK_CHANGED"

    with core.conn:
        core.conn.execute(
            "UPDATE regions SET region_locked=0, translation_locked=1 WHERE region_id=?",
            (region.region_id,),
        )
        row = core.conn.execute("SELECT text_json FROM regions WHERE region_id=?", (region.region_id,)).fetchone()
        text = json.loads(row["text_json"])
        text["translation_locked"] = True
        core.conn.execute(
            "UPDATE regions SET text_json=? WHERE region_id=?",
            (json.dumps(text, sort_keys=True), region.region_id),
        )
    with pytest.raises(DraftError) as text_locked:
        core.drafts.prepare_candidate(
            region.region_id, {"text": {"edited_translation": "no"}}, origin="user"
        )
    assert text_locked.value.code == "LOCK_CHANGED"
    # Translation Lock leaves style editable; inpaint_lock has no TextStyle key.
    with core.conn:
        core.conn.execute("UPDATE regions SET inpaint_locked=1 WHERE region_id=?", (region.region_id,))
    candidate = core.drafts.prepare_candidate(
        region.region_id, {"style": {"font_size": 13, "text_color": "#ddd"}}, origin="user"
    )
    assert candidate.origin == "user"
    with pytest.raises(DraftError) as style_key:
        core.drafts.prepare_candidate(
            region.region_id, {"style": {"customFoo": 1}}, origin="user"
        )
    assert style_key.value.code == "STYLE_KEY_NOT_ALLOWED"
    assert "customFoo" in str(style_key.value)


def test_same_session_shares_draft_and_cross_session_transfer_conflicts_text(core) -> None:
    region = _new_region(core, "page-draft", "region-owner")
    base = core.editing.get_region(region.region_id).current_revision_id
    first = core.drafts.open_draft(
        "owner-1", "page-draft", region.region_id,
        base_revision_id=base, page_binding_version=2,
    )
    repeated = core.drafts.open_draft(
        "owner-1", "page-draft", region.region_id,
        base_revision_id=base, page_binding_version=2,
    )
    assert first.draft.draft_id == repeated.draft.draft_id
    core.drafts.patch_draft(first.draft.draft_id, "owner-1", {"text": {"edited_translation": "old"}}, schedule_flush=False)
    read_only = core.drafts.open_draft(
        "owner-2", "page-draft", region.region_id,
        base_revision_id=base, page_binding_version=2,
    )
    assert not read_only.can_edit
    assert read_only.draft.draft_id == first.draft.draft_id

    core.drafts.transfer_owner(
        "page-draft", region.region_id, from_session_id="owner-1", to_session_id="owner-2"
    )
    second = core.drafts.open_draft(
        "owner-2", "page-draft", region.region_id,
        base_revision_id=base, page_binding_version=2,
    )
    candidate = core.drafts.prepare_candidate(
        region.region_id, {"style": {"text_color": "#abc"}},
        origin="user", draft_id=second.draft.draft_id,
    )
    with pytest.raises(DraftError) as conflict:
        core.drafts.patch_draft(
            second.draft.draft_id, "owner-2",
            {"text": {"edited_translation": "new"}}, schedule_flush=False,
        )
    assert conflict.value.code == "DRAFT_TEXT_CONFLICT"
    with pytest.raises(DraftError) as blocked:
        core.drafts.apply_candidates(second.token, [candidate.candidate_id])
    assert blocked.value.code == "DRAFT_CANDIDATE_INVALID"
    assert core.drafts.get_draft(first.draft.draft_id).status.value == "conflicted"
    assert core.drafts.get_draft(second.draft.draft_id).status.value == "conflicted"
    with pytest.raises(DraftError) as former_owner:
        core.drafts.resolve_text_conflict(first.draft.draft_id, "owner-1", "late edit")
    assert former_owner.value.code == "DRAFT_READ_ONLY"


def test_all_forced_flush_points_persist_and_failed_flush_keeps_memory(core) -> None:
    lease = core.drafts.open_draft(
        "flush-session", "page-draft", None,
        base_revision_id=None, page_binding_version=1,
    )
    for index, trigger in enumerate(("page_change", "workspace_switch", "exit", "window_close", "run_submit")):
        core.drafts.patch_draft(
            lease.draft.draft_id, "flush-session", {"style": {"size": index}},
            schedule_flush=False,
        )
        core.drafts.force_flush(lease.draft.draft_id, trigger)
        stored = core.drafts.journal.read_draft_record(lease.draft.draft_id)
        assert stored["DraftSequence"] == index + 1
        assert stored["patch"]["style"]["size"] == index

    core.drafts.patch_draft(
        lease.draft.draft_id, "flush-session", {"text": {"value": "still here"}},
        schedule_flush=False,
    )
    original = core.drafts.journal.write_draft
    core.drafts.journal.write_draft = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        DraftJournalError("DRAFT_JOURNAL_UNWRITABLE", "injected")
    )
    with pytest.raises(DraftError) as error:
        core.drafts.flush_draft(lease.draft.draft_id)
    assert error.value.code == "DRAFT_FLUSH_FAILED"
    in_memory = core.drafts.get_draft(lease.draft.draft_id)
    assert in_memory.status.value == "conflicted"
    assert in_memory.patch["text"]["value"] == "still here"
    core.drafts.journal.write_draft = original


def test_unwritable_journal_keeps_draft_editable_in_memory(core) -> None:
    core.drafts.journal.available = False
    lease = core.drafts.open_draft(
        "memory-session", "page-draft", None,
        base_revision_id=None, page_binding_version=11,
    )
    assert lease.draft.status.value == "conflicted"
    draft = core.drafts.patch_draft(
        lease.draft.draft_id, "memory-session",
        {"text": {"edited_translation": "memory survives"}}, schedule_flush=False,
    )
    assert draft.draft_sequence == 1
    with pytest.raises(DraftError) as error:
        core.drafts.flush_draft(draft.draft_id)
    assert error.value.code == "DRAFT_FLUSH_FAILED"
    assert core.drafts.get_draft(draft.draft_id).patch["text"]["edited_translation"] == "memory survives"


def test_session_end_cleans_journal_and_orphan_is_discarded(core) -> None:
    lease = core.drafts.open_draft(
        "ending-session", "page-draft", None,
        base_revision_id=None, page_binding_version=3,
    )
    registered = core.drafts.journal.read_draft_record(lease.draft.draft_id)
    assert registered is not None
    assert registered["status"] == "active"
    core.drafts.patch_draft(
        lease.draft.draft_id, "ending-session", {"geometry": {"x": 8}},
        schedule_flush=False,
    )
    core.drafts.journal.write_receipt({
        "tokenId": "keep", "DraftId": lease.draft.draft_id, "DraftSequence": 1,
        "revisionIds": {}, "contentDigests": {}, "committedAt": NOW,
    })
    core.drafts.end_session("ending-session")
    assert not (core.drafts.journal.root / f"{lease.draft.draft_id}.json").exists()
    assert core.drafts.journal.read_receipt(lease.draft.draft_id, 1) is not None

    orphan = core.drafts.open_draft(
        "orphan-session", "page-draft", None,
        base_revision_id=None, page_binding_version=3,
    )
    core.drafts.flush_draft(orphan.draft.draft_id)
    assert core.drafts.discard_orphans(set()) == [orphan.draft.draft_id]
    assert core.drafts.get_draft(orphan.draft.draft_id).status.value == "discarded"


def test_receipt_intent_recovers_after_restart_when_receipt_write_crashes(tmp_path: Path) -> None:
    root = tmp_path / "data"
    core = assemble_production_core(root)
    _seed_page(core)
    region = _new_region(core, "page-draft", "region-intent-recovery")
    draft_id, token = _open_and_patch(core, "page-draft", region.region_id)
    candidate = core.drafts.prepare_candidate(
        region.region_id, {"text": {"edited_translation": "recover me"}},
        origin="user", draft_id=draft_id,
    )
    core.drafts.journal.write_receipt = lambda _receipt: (_ for _ in ()).throw(
        DraftJournalError("DRAFT_JOURNAL_UNWRITABLE", "injected receipt failure")
    )
    with pytest.raises(DraftError) as error:
        core.drafts.apply_candidates(token, [candidate.candidate_id])
    assert error.value.code == "DRAFT_JOURNAL_UNWRITABLE"
    revision_id = core.editing.get_region(region.region_id).current_revision_id
    assert revision_id != candidate.base_revision_id
    _close(core)

    recovered = assemble_production_core(root)
    try:
        receipt = recovered.drafts.journal.read_receipt(draft_id, token.draft_sequence)
        assert receipt is not None
        assert receipt["revisionIds"][region.region_id] == revision_id
        assert recovered.drafts.apply_candidates(token) == receipt["revisionIds"]
        assert recovered.conn.execute(
            "SELECT COUNT(*) FROM region_revisions WHERE region_id=?", (region.region_id,)
        ).fetchone()[0] == 2
    finally:
        _close(recovered)

def test_machine_result_candidate_prepare_keeps_pointer(tmp_path: Path) -> None:
    """V13 (AC6): a machine result becomes a RegionCandidate and never writes
    ``current_revision_id`` during prepare (C-13 SC-D06/SC-D07)."""
    core = assemble_production_core(tmp_path / "data")
    try:
        page_id = _seed_page(core, "page-machine")
        region = _new_region(core, page_id, "region-machine")
        before = core.editing.get_region(region.region_id).current_revision_id
        candidate = core.drafts.prepare_candidate(
            region.region_id,
            {"text": {"edited_translation": "machine result"}},
            origin="machine",
        )
        assert candidate.origin == "machine"
        assert core.editing.get_region(region.region_id).current_revision_id == before
    finally:
        _close(core)