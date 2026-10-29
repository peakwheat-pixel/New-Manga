"""TM query priority (D06 §12, AC-TM-003) and reference-only semantics
(AC-TM-004)."""

from __future__ import annotations

import knowledge_helpers  # noqa: F401
from application.translation.knowledge.tm import TmMatch, TmScope

from knowledge_helpers import make_tm_service


def add(service, tm_id_source: str, target: str, *, scope: TmScope, book_id=None, source=None):
    counter = len(service._store.entries) + 1
    return service.record_confirmed_translation(
        source or tm_id_source,
        target,
        scope_type=scope,
        book_id=book_id,
        source_language="ja",
        target_language="zh",
    )


def test_book_exact_wins_over_global_exact() -> None:
    service = make_tm_service()
    book_entry = add(service, "進撃の巨人", "进击的巨人", scope=TmScope.BOOK, book_id="bk")
    global_entry = add(service, "進撃の巨人", "全局译法", scope=TmScope.GLOBAL)
    matches = service.find_matches("進撃の巨人", book_id="bk", source_language="ja", target_language="zh")
    assert [m.entry.tm_id for m in matches] == [book_entry.tm_id, global_entry.tm_id]
    assert all(m.match_type == "exact" for m in matches)


def test_book_fuzzy_wins_over_global_exact() -> None:
    """D06 §12 order: 当前作品 Exact → 当前作品 Fuzzy → 全局 Exact/Fuzzy."""

    service = make_tm_service()
    book_fuzzy = add(
        service, "unused", "作品内模糊",
        scope=TmScope.BOOK, book_id="bk", source="進撃の巨人は始まる",
    )
    global_exact = add(service, "進撃の巨人は始まった", "全局精确", scope=TmScope.GLOBAL)
    matches = service.find_matches(
        "進撃の巨人は始まった", book_id="bk", source_language="ja", target_language="zh"
    )
    assert matches[0].entry.tm_id == book_fuzzy.tm_id
    assert matches[0].match_type == "fuzzy"
    assert matches[1].entry.tm_id == global_exact.tm_id
    assert matches[1].match_type == "exact"


def test_fuzzy_below_threshold_is_not_returned() -> None:
    service = make_tm_service()
    add(service, "全く関係のない文章です", "无关", scope=TmScope.BOOK, book_id="bk")
    matches = service.find_matches(
        "進撃の巨人", book_id="bk", source_language="ja", target_language="zh"
    )
    assert matches == []


def test_fuzzy_threshold_is_configurable() -> None:
    service = make_tm_service()
    add(service, "進撃の巨人が始まる", "近似", scope=TmScope.BOOK, book_id="bk")
    loose = service.find_matches(
        "進撃の巨人", book_id="bk", source_language="ja", target_language="zh", fuzzy_threshold=0.1
    )
    strict = service.find_matches(
        "進撃の巨人", book_id="bk", source_language="ja", target_language="zh", fuzzy_threshold=0.99
    )
    assert loose and not strict


def test_language_pair_must_match() -> None:
    service = make_tm_service()
    entry = add(service, "進撃の巨人", "进击的巨人", scope=TmScope.BOOK, book_id="bk")
    # 保存的是 ja→zh；用 en→zh 查询不得命中。
    other_pair = service.find_matches(
        "進撃の巨人", book_id="bk", source_language="en", target_language="zh"
    )
    assert other_pair == []
    assert entry.source_language == "ja"


def test_book_query_without_book_id_only_sees_global() -> None:
    service = make_tm_service()
    add(service, "進撃の巨人", "作品内", scope=TmScope.BOOK, book_id="bk")
    global_entry = add(service, "進撃の巨人", "全局", scope=TmScope.GLOBAL)
    matches = service.find_matches(
        "進撃の巨人", book_id=None, source_language="ja", target_language="zh"
    )
    assert [m.entry.tm_id for m in matches] == [global_entry.tm_id]


def test_unconfirmed_entries_never_match() -> None:
    """Store 里即使存在 is_confirmed=False 的记录（如管理员导入草稿），
    查询也只返回正式 TM (TASK-002 §2.3)."""

    from application.translation.knowledge.tm import TranslationMemoryEntry

    service = make_tm_service()
    draft = TranslationMemoryEntry(
        tm_id="tm-draft",
        scope_type=TmScope.BOOK,
        book_id="bk",
        source_language="ja",
        target_language="zh",
        source_text="進撃の巨人",
        target_text="草稿",
        is_confirmed=False,
    )
    service._store.add(draft)
    matches = service.find_matches("進撃の巨人", book_id="bk", source_language="ja", target_language="zh")
    assert matches == []


def test_matches_are_reference_only() -> None:
    """AC-TM-004: 查询结果不写任何 Region/final；usage 只在消费方显式
    record_usage 时增加."""

    service = make_tm_service()
    entry = add(service, "進撃の巨人", "进击的巨人", scope=TmScope.BOOK, book_id="bk")
    before = service._store.get(entry.tm_id)
    matches = service.find_matches("進撃の巨人", book_id="bk", source_language="ja", target_language="zh")
    assert matches and all(isinstance(m, TmMatch) for m in matches)
    after = service._store.get(entry.tm_id)
    assert after.usage_count == before.usage_count == 0
    assert after.last_used_at == before.last_used_at


def test_deterministic_ordering_within_group() -> None:
    service = make_tm_service()
    a = add(service, "進撃の巨人が始まる", "甲", scope=TmScope.BOOK, book_id="bk")
    b = add(service, "進撃の巨人が終わる", "乙", scope=TmScope.BOOK, book_id="bk")
    matches = service.find_matches(
        "進撃の巨人が続く", book_id="bk", source_language="ja", target_language="zh", fuzzy_threshold=0.3
    )
    fuzzies = [m for m in matches if m.match_type == "fuzzy"]
    assert {m.entry.tm_id for m in fuzzies} == {a.tm_id, b.tm_id}
    similarities = [m.similarity for m in fuzzies]
    assert similarities == sorted(similarities, reverse=True)
