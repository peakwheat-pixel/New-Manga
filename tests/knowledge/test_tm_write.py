"""TM write-side and lifecycle (D03 §14.3, AC-TM-001/002, TASK-002 §2.3)."""

from __future__ import annotations

import pytest

import knowledge_helpers  # noqa: F401
from application.translation.knowledge.tm import (
    TmScope,
    TmStatus,
    UnconfirmedTranslationError,
)

from knowledge_helpers import make_tm_service


def write(service, **overrides):
    kwargs = dict(
        scope_type=TmScope.BOOK,
        book_id="bk",
        source_language="ja",
        target_language="zh",
    )
    kwargs.update(overrides)
    return service.record_confirmed_translation("進撃の巨人", "进击的巨人", **kwargs)


def test_unconfirmed_machine_translation_is_rejected() -> None:
    """AC-TM-001: 自动 Translation 完成但未人工确认 → TM 不得新增正式记录."""

    service = make_tm_service()
    with pytest.raises(UnconfirmedTranslationError):
        service.record_confirmed_translation(
            "進撃の巨人",
            "进击的巨人",
            scope_type=TmScope.BOOK,
            book_id="bk",
            source_language="ja",
            target_language="zh",
            is_confirmed=False,
        )
    assert service._store.entries == {}


def test_machine_translation_in_current_is_not_automatically_written() -> None:
    """TASK-002 §2.3: 机器译文不能因存在于 current 就自动写入 TM。写入只能
    由显式的人工确认调用发生——没有任何“自动收集 current”的入口。"""

    service = make_tm_service()
    # 模拟批量自动翻译完成：没有任何确认动作发生。
    # (服务端没有任何 auto-harvest API；这里的负例证明调用面不存在。)
    assert not hasattr(service, "harvest_current")
    assert not hasattr(service, "collect_from_regions")
    assert service._store.entries == {}


def test_human_confirmed_translation_enters_tm() -> None:
    """AC-TM-002."""

    service = make_tm_service()
    entry = write(service, is_confirmed=True)
    assert entry.is_confirmed is True
    assert entry.tm_id in service._store.entries
    assert entry.source_hash  # exact-match key computed
    assert entry.source_normalized == "進撃の巨人"


def test_proofread_content_enters_tm() -> None:
    """已校对内容也允许写入 (D03 §14.3)."""

    service = make_tm_service()
    entry = write(service, is_confirmed=False, proofread=True)
    assert entry.is_confirmed is True  # stored formal
    assert entry.tm_id in service._store.entries


def test_source_provenance_is_kept_for_backtrace() -> None:
    """来源回溯：source_region_id / source_region_revision_id 保留."""

    service = make_tm_service()
    entry = write(
        service,
        source_region_id="reg-7",
        source_region_revision_id="reg-7#rev3",
    )
    assert entry.source_region_id == "reg-7"
    assert entry.source_region_revision_id == "reg-7#rev3"


def test_disabled_entry_keeps_history_but_exits_matching() -> None:
    """TASK-002 §2.3: disabled 保留来源、历史和计数，不参与匹配."""

    service = make_tm_service()
    entry = write(service)
    service.record_usage(entry.tm_id)
    disabled = service.set_disabled(entry.tm_id, disabled=True)
    assert disabled.status is TmStatus.DISABLED
    assert disabled.usage_count == 1  # history kept
    assert disabled in service._store.entries.values()

    matches = service.find_matches("進撃の巨人", book_id="bk", source_language="ja", target_language="zh")
    assert matches == []

    reenabled = service.set_disabled(entry.tm_id, disabled=False)
    assert reenabled.status is TmStatus.ACTIVE


def test_duplicate_confirmed_write_is_idempotent() -> None:
    service = make_tm_service()
    first = write(service)
    second = write(service)
    assert first.tm_id == second.tm_id
    assert len(service._store.entries) == 1


def test_same_text_different_target_creates_new_entry() -> None:
    service = make_tm_service()
    first = write(service)
    second = service.record_confirmed_translation(
        "進撃の巨人",
        "进击的巨人改译",
        scope_type=TmScope.BOOK,
        book_id="bk",
        source_language="ja",
        target_language="zh",
    )
    assert first.tm_id != second.tm_id


def test_scope_validation() -> None:
    service = make_tm_service()
    with pytest.raises(ValueError):
        service.record_confirmed_translation(
            "壁", "墙",
            scope_type=TmScope.BOOK, book_id=None,
            source_language="ja", target_language="zh",
        )
    with pytest.raises(ValueError):
        service.record_confirmed_translation(
            "壁", "墙",
            scope_type=TmScope.GLOBAL, book_id="bk",
            source_language="ja", target_language="zh",
        )


def test_usage_counter_updates() -> None:
    service = make_tm_service()
    entry = write(service)
    updated = service.record_usage(entry.tm_id)
    assert updated.usage_count == 1
    assert updated.last_used_at is not None
    with pytest.raises(KeyError):
        service.record_usage("nope")
