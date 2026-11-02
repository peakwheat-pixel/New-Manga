"""Term candidate extraction for the ``term_extract`` pipeline step
(D06 §12 knowledge layer; TASK-033 AC ②).

The step sits between OCR and Translate and prepares *candidates only*:

- it never writes the formal glossary or the TM (AC-TM-001/002 are write
  guards in :mod:`application.translation.knowledge.tm`; this module does not
  even import the write-side service);
- it never issues a network request or loads a model — the whole extraction
  is local text matching, so ``ai_invoked`` is structurally ``False``;
- an absent knowledge source is not an error: the text heuristic below still
  produces repetition-based candidates, and the assembled service itself is
  the capability boundary (a missing assembly fails the step closed in the
  handler, TASK-033 AC ②).

Candidate sources, in priority order:

1. **glossary** — settings-provided source→target pairs whose source key
   occurs in the OCR text (``suggested_target`` from the glossary);
2. **tm** — read-only :class:`~application.translation.knowledge.tm.TranslationMemoryStore`
   scan when a store is assembled (production has no TM store yet, so this
   source reports ``tm_consulted: false`` until one exists);
3. **text** — repetition heuristic: normalised n-grams (n=2..4) occurring at
   least twice, capped, as "worth a translator's attention" candidates.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol

from application.translation.knowledge.tm import TmScope, TranslationMemoryEntry
from domain.constraints.entities import normalize_term

_MAX_CANDIDATES = 20
_MAX_TEXT_NGRAM_CANDIDATES = 10
_MIN_TERM_LEN = 2


@dataclass(frozen=True)
class TermCandidate:
    """One extractable term candidate; never persisted by this module."""

    term: str
    source: str  # "glossary" | "tm" | "text"
    occurrences: int
    suggested_target: str | None = None


@dataclass(frozen=True)
class TermExtractionResult:
    candidates: tuple[TermCandidate, ...]
    provenance: Mapping[str, object] = field(default_factory=dict)


class _ReadOnlyTmStore(Protocol):
    """The read-only slice of the TM store contract this module may use."""

    def list_entries(
        self, *, scope_type: TmScope, book_id: str | None
    ) -> list[TranslationMemoryEntry]: ...


class TermExtractionService:
    """Local, write-free term candidate extraction (D06 §12, TASK-033 AC ②)."""

    def __init__(self, tm_store: _ReadOnlyTmStore | None = None) -> None:
        self._tm_store = tm_store

    def extract(
        self,
        ocr_text: str,
        *,
        glossary: Mapping[str, str] | None = None,
        book_id: str | None = None,
    ) -> TermExtractionResult:
        candidates: list[TermCandidate] = []
        seen: set[str] = set()
        sources: list[str] = []

        normalized_text = normalize_term(ocr_text)

        glossary_map = dict(glossary or {})
        if glossary_map:
            sources.append("glossary")
            for source_term, target_term in sorted(glossary_map.items()):
                key = normalize_term(source_term)
                if not key or key in seen:
                    continue
                if key in normalized_text:
                    seen.add(key)
                    candidates.append(
                        TermCandidate(
                            term=source_term,
                            source="glossary",
                            occurrences=normalized_text.count(key),
                            suggested_target=target_term,
                        )
                    )

        if self._tm_store is not None:
            sources.append("tm")
            entries = self._tm_store.list_entries(
                scope_type=TmScope.BOOK, book_id=book_id
            ) + self._tm_store.list_entries(scope_type=TmScope.GLOBAL, book_id=None)
            for entry in entries:
                key = entry.source_normalized or normalize_term(entry.source_text)
                if not key or key in seen or key not in normalized_text:
                    continue
                seen.add(key)
                candidates.append(
                    TermCandidate(
                        term=entry.source_text,
                        source="tm",
                        occurrences=normalized_text.count(key),
                        suggested_target=entry.target_text,
                    )
                )

        sources.append("text")
        for ngram, count in self._repeated_ngrams(normalized_text):
            if ngram in seen:
                continue
            seen.add(ngram)
            candidates.append(
                TermCandidate(term=ngram, source="text", occurrences=count)
            )

        ordered = tuple(candidates[:_MAX_CANDIDATES])
        provenance = {
            "step": "term_extract",
            "ai_invoked": False,  # structural: local text matching only
            "sources": sources,
            "glossary_size": len(glossary_map),
            "tm_consulted": self._tm_store is not None,
            "candidate_count": len(ordered),
            "truncated": len(candidates) > len(ordered),
        }
        return TermExtractionResult(candidates=ordered, provenance=provenance)

    @staticmethod
    def _repeated_ngrams(normalized_text: str) -> list[tuple[str, int]]:
        """Normalised n-grams (n=2..4) occurring at least twice, most frequent
        first; deterministic order for identical inputs."""
        if len(normalized_text) < 2 * _MIN_TERM_LEN:
            return []
        counts: Counter[str] = Counter()
        for size in range(_MIN_TERM_LEN, 5):
            for start in range(0, len(normalized_text) - size + 1):
                counts[normalized_text[start : start + size]] += 1
        repeated = [
            (ngram, count)
            for ngram, count in counts.items()
            if count >= 2 and len(ngram) >= _MIN_TERM_LEN
        ]
        repeated.sort(key=lambda item: (-item[1], item[0]))
        return repeated[:_MAX_TEXT_NGRAM_CANDIDATES]
