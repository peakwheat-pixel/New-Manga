"""Translation Memory knowledge layer (D03 §14, D06 §12, TASK-002 §2.3).

The TM lives at the application layer: its record model and store contract
are consumer-side ports, persistence lands in a later infrastructure slice.
Only human-confirmed or proofread content may enter the TM (AC-TM-001/002);
queries walk 当前作品 Exact → 当前作品 Fuzzy → 全局 Exact / Fuzzy (AC-TM-003)
and return reference matches only — nothing here ever touches a Region's
final translation (AC-TM-004).
"""

from __future__ import annotations

import difflib
import hashlib
from dataclasses import dataclass, replace
from enum import Enum
from typing import Protocol

from domain.constraints.entities import normalize_term


class TmScope(str, Enum):
    """D03 §14.2: 作品 TM 优先于全局 TM，允许跨作品共享."""

    BOOK = "book"
    GLOBAL = "global"


class TmStatus(str, Enum):
    """Frozen by TASK-002 §2.3: ``active | disabled`` only; disabled records
    keep history and counters but never participate in matching."""

    ACTIVE = "active"
    DISABLED = "disabled"


class UnconfirmedTranslationError(Exception):
    """Machine output without human confirmation must not pollute the TM
    (D03 §14.3, AC-TM-001)."""


@dataclass(frozen=True)
class TranslationMemoryEntry:
    """D03 §14.5. ``is_confirmed`` must be true for formal TM records."""

    tm_id: str
    scope_type: TmScope
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    source_normalized: str = ""
    source_hash: str = ""
    book_id: str | None = None
    source_region_id: str | None = None
    source_region_revision_id: str | None = None
    is_confirmed: bool = True
    status: TmStatus = TmStatus.ACTIVE
    usage_count: int = 0
    last_used_at: str | None = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "scope_type", TmScope(self.scope_type))
        object.__setattr__(self, "status", TmStatus(self.status))
        if self.scope_type is TmScope.BOOK and not self.book_id:
            raise ValueError("book-scoped TM entries require a book_id")
        if self.scope_type is TmScope.GLOBAL and self.book_id:
            raise ValueError("global TM entries must not carry a book_id")
        if not self.source_text.strip():
            raise ValueError("TM entry requires non-blank source_text")
        if not self.target_text.strip():
            raise ValueError("TM entry requires non-blank target_text")
        if not self.source_normalized:
            object.__setattr__(self, "source_normalized", normalize_term(self.source_text))
        if not self.source_hash:
            object.__setattr__(self, "source_hash", tm_source_hash(self.source_normalized))


def tm_source_hash(source_normalized: str) -> str:
    """Exact-match key (D03 §14.5 ``source_hash``)."""

    return hashlib.sha256(source_normalized.encode("utf-8")).hexdigest()


class TranslationMemoryStore(Protocol):
    """Persistence contract consumed by the TM services (consumer-side)."""

    def add(self, entry: TranslationMemoryEntry) -> None: ...

    def get(self, tm_id: str) -> TranslationMemoryEntry | None: ...

    def find_by_source_hash(
        self, source_hash: str, *, scope_type: TmScope, book_id: str | None
    ) -> list[TranslationMemoryEntry]: ...

    def list_entries(self, *, scope_type: TmScope, book_id: str | None) -> list[TranslationMemoryEntry]: ...

    def update(self, entry: TranslationMemoryEntry) -> None: ...


@dataclass(frozen=True)
class TmMatch:
    """A query hit; reference-only context for translation (AC-TM-004)."""

    entry: TranslationMemoryEntry
    match_type: str  # exact | fuzzy
    similarity: float


class TranslationMemoryService:
    """Write-side and lookup-side TM operations (D03 §14.3/14.4, D06 §12)."""

    #: 相似度下限 for Fuzzy Match; the approved spec fixes Exact + Fuzzy and
    #: forbids Embedding/RAG but names no numeric value, so callers may
    #: override this default.
    DEFAULT_FUZZY_THRESHOLD = 0.80

    def __init__(self, store: TranslationMemoryStore, *, clock, id_factory) -> None:
        """``clock`` returns an ISO timestamp; ``id_factory`` yields tm ids."""

        self._store = store
        self._clock = clock
        self._id_factory = id_factory

    # ------------------------------------------------------------------
    # write side (D03 §14.3)
    # ------------------------------------------------------------------

    def record_confirmed_translation(
        self,
        source_text: str,
        target_text: str,
        *,
        scope_type: TmScope,
        book_id: str | None = None,
        source_language: str,
        target_language: str,
        is_confirmed: bool = True,
        proofread: bool = False,
        source_region_id: str | None = None,
        source_region_revision_id: str | None = None,
    ) -> TranslationMemoryEntry:
        """Persist a TM entry from human-confirmed or proofread content.

        Anything else raises :class:`UnconfirmedTranslationError` — 未经确认
        的机器翻译不得自动污染 TM (AC-TM-001); 人工确认 final 后允许写入
        (AC-TM-002). Source provenance (region + revision) is kept for
        回溯 (D03 §14.5).
        """

        if not is_confirmed and not proofread:
            raise UnconfirmedTranslationError(
                "unconfirmed machine translation must not enter the TM (AC-TM-001)"
            )
        now = self._clock()
        existing = self._find_duplicate(
            source_text,
            scope_type=scope_type,
            book_id=book_id,
            source_language=source_language,
            target_language=target_language,
        )
        if existing is not None and existing.target_text == target_text:
            return existing
        entry = TranslationMemoryEntry(
            tm_id=self._id_factory(),
            scope_type=scope_type,
            book_id=book_id,
            source_language=source_language,
            target_language=target_language,
            source_text=source_text,
            target_text=target_text,
            source_region_id=source_region_id,
            source_region_revision_id=source_region_revision_id,
            is_confirmed=True,
            status=TmStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        self._store.add(entry)
        return entry

    def _find_duplicate(
        self,
        source_text: str,
        *,
        scope_type: TmScope,
        book_id: str | None,
        source_language: str,
        target_language: str,
    ) -> TranslationMemoryEntry | None:
        key = tm_source_hash(normalize_term(source_text))
        for entry in self._store.find_by_source_hash(key, scope_type=scope_type, book_id=book_id):
            if (
                entry.source_language == source_language
                and entry.target_language == target_language
            ):
                return entry
        return None

    def set_disabled(self, tm_id: str, *, disabled: bool) -> TranslationMemoryEntry:
        """批准的禁用操作 (TASK-010 AC): disabled keeps history and counters
        (TASK-002 §2.3) but drops out of every query."""

        entry = self._store.get(tm_id)
        if entry is None:
            raise KeyError(f"unknown tm_id: {tm_id}")
        updated = replace(
            entry,
            status=TmStatus.DISABLED if disabled else TmStatus.ACTIVE,
            updated_at=self._clock(),
        )
        self._store.update(updated)
        return updated

    def record_usage(self, tm_id: str) -> TranslationMemoryEntry:
        """Hit consumed as translation context → usage_count/last_used_at."""

        entry = self._store.get(tm_id)
        if entry is None:
            raise KeyError(f"unknown tm_id: {tm_id}")
        updated = replace(
            entry,
            usage_count=entry.usage_count + 1,
            last_used_at=self._clock(),
            updated_at=self._clock(),
        )
        self._store.update(updated)
        return updated

    # ------------------------------------------------------------------
    # query side (D06 §12)
    # ------------------------------------------------------------------

    def find_matches(
        self,
        source_text: str,
        *,
        book_id: str | None = None,
        source_language: str,
        target_language: str,
        fuzzy_threshold: float | None = None,
    ) -> list[TmMatch]:
        """当前作品 Exact → 当前作品 Fuzzy → 全局 Exact / Fuzzy (D06 §12).

        Only ``active`` + ``is_confirmed`` entries match (TASK-002 §2.3).
        Returns best-first: scope (book first), match type (exact first),
        similarity descending, tm_id ascending for determinism. The result
        is reference data only — callers decide what to do with it.
        """

        threshold = (
            self.DEFAULT_FUZZY_THRESHOLD if fuzzy_threshold is None else fuzzy_threshold
        )
        query = normalize_term(source_text)
        if not query:
            return []
        query_hash = tm_source_hash(query)

        scopes = [(TmScope.BOOK, book_id), (TmScope.GLOBAL, None)] if book_id else [
            (TmScope.GLOBAL, None)
        ]
        matches: list[TmMatch] = []
        seen_ids: set[str] = set()
        for scope_type, scope_book_id in scopes:
            candidates = [
                entry
                for entry in self._store.list_entries(scope_type=scope_type, book_id=scope_book_id)
                if entry.status is TmStatus.ACTIVE
                and entry.is_confirmed
                and entry.source_language == source_language
                and entry.target_language == target_language
            ]
            exact, fuzzy = [], []
            for entry in candidates:
                if entry.tm_id in seen_ids:
                    continue
                if entry.source_hash == query_hash:
                    exact.append(TmMatch(entry, "exact", 1.0))
                    seen_ids.add(entry.tm_id)
                elif threshold < 1.0:
                    similarity = self._similarity(query, entry.source_normalized)
                    if similarity >= threshold:
                        fuzzy.append(TmMatch(entry, "fuzzy", similarity))
                        seen_ids.add(entry.tm_id)
            fuzzy.sort(key=lambda match: (-match.similarity, match.entry.tm_id))
            matches.extend(exact)
            matches.extend(fuzzy)
        return matches

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        return difflib.SequenceMatcher(None, a, b).ratio()
