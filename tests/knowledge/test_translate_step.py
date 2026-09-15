"""Translate Step (D06 §18) and the write-scope output guard
(AC-TRANS-003, TASK-002 §4)."""

from __future__ import annotations

import pytest

import knowledge_helpers  # noqa: F401
from application.translation.context.builder import ContextBuilder, PageContextInput
from application.translation.context.snapshot import freeze_constraints
from application.translation.context.step import (
    OutputMappingError,
    TranslationRequest,
    build_provider_request,
    execute_translate_step,
    map_provider_output,
)
from application.translation.knowledge.tm import TmMatch
from domain.constraints.entities import ConstraintKind, ConstraintScope

from knowledge_helpers import make_constraint, make_region, make_tm_service

builder = ContextBuilder()


def speech_page():
    return PageContextInput(
        page_id="p1",
        sort_order=0,
        regions=(
            make_region("r1", 1, ocr_text="目標文", region_type="speech"),
            make_region("r2", 2, ocr_text="効果音", region_type="sfx", sfx_policy="skip"),
            make_region("r3", 3, ocr_text="手動SFX", region_type="sfx", sfx_policy="manual"),
            make_region("r4", 4, ocr_text="訳すSFX", region_type="sfx", sfx_policy="translate"),
            make_region("ctx", 5, ocr_text="前のページ", region_type="speech"),
        ),
    )


def frozen_snapshot():
    constraints = [
        make_constraint("c1", source_term="巨人", target_term="巨人译名"),
        make_constraint(
            "c2", source_term="Sasha", kind=ConstraintKind.DO_NOT_TRANSLATE,
            scope_type=ConstraintScope.BOOK, scope_id="bk",
        ),
    ]
    return freeze_constraints(constraints, run_id="run-1", frozen_at="t0",
                              book_id="bk", chapter_id="ch")


def request_bundle():
    return builder.build_single_page(
        [speech_page()],
        target_page_id="p1",
        target_region_ids=["r1", "r2", "r3", "r4"],
    )


def test_provider_request_carries_glossary_provenance_and_targets() -> None:
    request = build_provider_request(
        bundle=request_bundle(), snapshot=frozen_snapshot(), model="test-model"
    )
    assert isinstance(request, TranslationRequest)
    assert request.model == "test-model"
    glossary = {item["normalized_key"]: item for item in request.term_glossary}
    assert glossary["巨人"]["target_term"] == "巨人译名"
    assert request.do_not_translate == frozenset({"sasha"})
    assert {slot.region_id for slot in request.targets} == {"r1", "r2", "r3", "r4"}
    assert "巨人" not in request.prompt  # glossary travels separately
    assert request.context_provenance["mode"] == "single_page"


def test_provider_request_includes_tm_references() -> None:
    service = make_tm_service()
    entry = service.record_confirmed_translation(
        "目標文", "目标的旧译文",
        scope_type="book", book_id="bk",
        source_language="ja", target_language="zh",
    )
    matches = service.find_matches(
        "目標文", book_id="bk", source_language="ja", target_language="zh"
    )
    request = build_provider_request(
        bundle=request_bundle(),
        snapshot=frozen_snapshot(),
        tm_matches=tuple(
            TmMatch(m.entry, m.match_type, m.similarity) for m in matches
        ),
    )
    assert request.tm_references == (
        {
            "source_text": entry.source_text,
            "target_text": "目标的旧译文",
            "match_type": "exact",
            "similarity": 1.0,
        },
    )


def test_out_of_scope_output_is_rejected() -> None:
    """AC-TRANS-003: Provider 输出映射到 Context Region → 拒绝."""

    request = build_provider_request(
        bundle=builder.build_single_page(
            [speech_page()], target_page_id="p1", target_region_ids=["r1"]
        ),
        snapshot=frozen_snapshot(),
    )
    with pytest.raises(OutputMappingError):
        map_provider_output(request, {"r1": "OK", "ctx": "越界输出"})
    with pytest.raises(OutputMappingError):
        map_provider_output(request, {"r1": "OK", "r2": "不在目标里"})


def test_missing_output_is_rejected() -> None:
    request = build_provider_request(
        bundle=builder.build_single_page(
            [speech_page()], target_page_id="p1", target_region_ids=["r1", "r4"]
        ),
        snapshot=frozen_snapshot(),
    )
    with pytest.raises(OutputMappingError):
        map_provider_output(request, {"r1": "OK"})  # r4 missing


def test_targets_outside_bundle_are_rejected_upfront() -> None:
    from application.translation.context.step import TargetSlot

    with pytest.raises(OutputMappingError):
        build_provider_request(
            bundle=request_bundle(),
            snapshot=frozen_snapshot(),
            targets=(TargetSlot("p1", "somewhere-else"),),
        )


def test_step_skips_sfx_and_translates_the_rest() -> None:
    """AC-SFX-001/003 in step composition: default-skip and manual SFX never
    reach the provider; translate-policy SFX does (AC-SFX-002)."""

    calls = []

    def provider_call(request: TranslationRequest):
        calls.append(request)
        return {slot.region_id: f"译({slot.region_id})" for slot in request.targets}

    result = execute_translate_step(
        bundle=request_bundle(),
        snapshot=frozen_snapshot(),
        provider_call=provider_call,
        model="m",
    )
    assert calls and {slot.region_id for slot in calls[0].targets} == {"r1", "r4"}
    assert {(s.region_id, s.reason) for s in result.skipped} == {
        ("r2", "sfx_skip"), ("r3", "sfx_skip"),
    }
    assert result.translations == {"r1": "译(r1)", "r4": "译(r4)"}
    assert result.model == "m"
    assert result.context_provenance["mode"] == "single_page"
    assert result.term_provenance  # glossary provenance travels with the result


def test_step_fails_without_touching_current_pointers_on_bad_output() -> None:
    """TASK-002 §4: mapping mismatch fails the step; nothing here writes a
    Region anyway — the guard is the last line before a caller would."""

    def bad_provider(request: TranslationRequest):
        return {"r1": "OK", "ctx": "should not happen"}

    with pytest.raises(OutputMappingError):
        execute_translate_step(
            bundle=builder.build_single_page(
                [speech_page()], target_page_id="p1", target_region_ids=["r1"]
            ),
            snapshot=frozen_snapshot(),
            provider_call=bad_provider,
        )


def test_tm_matches_never_write_final_translation() -> None:
    """AC-TM-004: step returns reference data; no TM hit becomes a final."""

    service = make_tm_service()
    service.record_confirmed_translation(
        "目標文", "旧译文",
        scope_type="book", book_id="bk",
        source_language="ja", target_language="zh",
    )
    matches = service.find_matches(
        "目標文", book_id="bk", source_language="ja", target_language="zh"
    )
    result = execute_translate_step(
        bundle=builder.build_single_page(
            [speech_page()], target_page_id="p1", target_region_ids=["r1"]
        ),
        snapshot=frozen_snapshot(),
        tm_matches=tuple(matches),
        provider_call=lambda request: {"r1": "新译文"},
    )
    assert result.translation_for("r1") == "新译文"
    stored = service._store.get(matches[0].entry.tm_id)
    assert stored.usage_count == 0  # usage is recorded by the consumer, if at all
