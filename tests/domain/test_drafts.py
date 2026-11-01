from __future__ import annotations

from domain.drafts.entities import Draft, DraftSequence, DraftStatus


def make_draft() -> Draft:
    return Draft(
        draft_id="draft-a",
        session_id="session-a",
        page_id="page-a",
        region_id=None,
        base_revision_id=None,
        page_binding_version=-918,
    )


def test_draft_has_eleven_fields_and_zero_based_monotonic_sequence() -> None:
    draft = make_draft()
    assert draft.sequence == DraftSequence(0)
    assert len(draft.to_json()) == 11
    assert draft.status is DraftStatus.ACTIVE
    assert draft.page_binding_version == -918

    for index in range(3):
        draft.apply_patch({"text": {"edited_translation": f"line-{index}"}})
        assert draft.draft_sequence == index + 1
    assert draft.sequence == DraftSequence(3)


def test_patch_merges_geometry_and_style_keys_but_replaces_text_domain() -> None:
    draft = make_draft()
    draft.apply_patch({
        "text": {"edited_translation": "first"},
        "geometry": {"x": 1, "y": 2},
        "style": {"font_size": 12, "text_color": "#fff"},
    })
    draft.apply_patch({
        "text": {"edited_translation": "later"},
        "geometry": {"x": 9},
        "style": {"font_size": 14},
    })
    assert draft.patch == {
        "text": {"edited_translation": "later"},
        "geometry": {"x": 9, "y": 2},
        "style": {"font_size": 14, "text_color": "#fff"},
    }
    assert draft.draft_sequence == 2


def test_draft_json_projection_has_exact_c13_field_names() -> None:
    assert set(make_draft().to_json()) == {
        "DraftId", "SessionId", "PageId", "RegionId", "BaseRevisionId",
        "PageBindingVersion", "DraftSequence", "patch", "undoCursor", "savedAt", "status",
    }
