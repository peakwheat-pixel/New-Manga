"""RegionID translation output protocol (TASK-017 experiment, D06 §18/§84).

Pure-stdlib protocol rules shared by the mock provider, the pytest suite
and the runnable experiment:

- request building with Context Group semantics (D06 §84): context pages
  are truncated first under a token budget; Region payloads are never
  truncated and every output must map back to its Page/Region id;
- response validation classifying missing / duplicate / out-of-range
  RegionIDs and malformed JSON (D08 AC-TRANS fallback input);
- retryability classification per D06 §56: provider-transport faults and
  malformed provider output are retryable; authentication and invalid
  local input are not. Rate limiting (HTTP 429) is retryable (§56.1 names
  ``ProviderRateLimitError``); every other 4xx is declared request-side and
  non-retryable instead of being left undeclared (Review R-002).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field


def estimate_tokens(text: str) -> int:
    """Cheap CJK-aware estimate (≈0.5–1 char per token); experiment-grade."""
    return max(1, sum(2 if ord(ch) > 0x2E80 else 1 for ch in text) // 2)


@dataclass(frozen=True)
class RegionInput:
    region_id: str
    text: str


@dataclass(frozen=True)
class ContextPage:
    page_id: str
    position: str  # "before" | "after" relative to the target page
    text: str
    #: D06 §13 reading order. ``None`` falls back to the page ordinal in
    #: ``page_id`` so synthetic ids keep a deterministic order (Review R-003).
    reading_order: int | None = None


@dataclass(frozen=True)
class TranslationRequest:
    """One Context Group request (D06 §18.1 input, §84 grouping)."""

    page_id: str
    regions: tuple[RegionInput, ...]
    context: tuple[ContextPage, ...]
    glossary: dict[str, str]
    truncated_context_pages: tuple[str, ...] = field(default=())

    def payload(self) -> dict:
        return {
            "page_id": self.page_id,
            "regions": [
                {"region_id": r.region_id, "text": r.text} for r in self.regions
            ],
            "context": [
                {"page_id": c.page_id, "position": c.position, "text": c.text}
                for c in self.context
            ],
            "glossary": dict(self.glossary),
            "context_truncated_pages": list(self.truncated_context_pages),
        }

    def payload_json(self) -> str:
        return json.dumps(self.payload(), ensure_ascii=False, sort_keys=True)

    def payload_hash(self) -> str:
        """D06 §57: a retry must carry the identical request payload."""
        return hashlib.sha256(self.payload_json().encode("utf-8")).hexdigest()

    @property
    def region_ids(self) -> tuple[str, ...]:
        return tuple(r.region_id for r in self.regions)

    def token_estimate(self) -> int:
        body = self.payload_json()
        return estimate_tokens(body)


def _page_ordinal(page_id: str) -> int:
    """Trailing integer of a page id (``"page-12"`` → ``12``); 0 when absent."""
    digits = ""
    for char in reversed(page_id):
        if not char.isdigit():
            break
        digits = char + digits
    return int(digits) if digits else 0


def _context_sort_key(page: ContextPage) -> tuple[int, int, str]:
    """Nearest-first context ordering (Review R-003).

    ``reading_order`` (D06 §13) wins when the caller supplies it; the page
    ordinal is the documented fallback for synthetic ids, so ordering never
    depends on raw ``page_id`` string comparison.
    """
    ordinal = page.reading_order if page.reading_order is not None else _page_ordinal(page.page_id)
    return (0 if page.position == "before" else 1, ordinal, page.page_id)


def _format_ids(values: Iterable[object]) -> str:
    """Render region ids for report details without assuming strings.

    Review R-001: a non-string ``region_id`` must be reported, never raise
    while the detail string is being built.
    """
    return ", ".join(repr(value) if not isinstance(value, str) else value for value in values)


def build_request(
    page_id: str,
    regions: list[RegionInput],
    context_pages: list[ContextPage],
    glossary: dict[str, str] | None = None,
    token_budget: int | None = None,
) -> TranslationRequest:
    """Group one page's regions with as much context as the budget allows.

    Ordering (D06 §13): context pages are ordered by ``reading_order`` when
    the caller supplies it, otherwise by the page ordinal taken from
    ``page_id`` — **never** by raw ``page_id`` string order (Review R-003).

    Truncation policy (declared, Review R-003): pages are considered
    nearest-first and kept while the request still fits the budget; the
    first page that does not fit is dropped together with every farther
    page, so the kept set is always the nearest contiguous run — i.e. the
    farthest pages are dropped first. ``truncated_context_pages`` is
    reported nearest-first. Region texts and glossary are never truncated.
    """
    if not regions:
        raise ValueError("a Context Group needs at least one region")
    ordered = sorted(context_pages, key=_context_sort_key)  # nearest first
    kept: list[ContextPage] = []
    truncated: list[str] = []

    def size_of(items: list[ContextPage]) -> int:
        probe = TranslationRequest(page_id, tuple(regions), tuple(items), glossary or {})
        return probe.token_estimate()

    for index, page in enumerate(ordered):
        if token_budget is not None and size_of([*kept, page]) > token_budget:
            truncated.extend(candidate.page_id for candidate in ordered[index:])
            break
        kept.append(page)
    return TranslationRequest(
        page_id=page_id,
        regions=tuple(regions),
        context=tuple(kept),
        glossary=dict(glossary or {}),
        truncated_context_pages=tuple(truncated),
    )


class ViolationKind:
    OK = "ok"
    MALFORMED_JSON = "malformed_json"
    MISSING_IDS = "missing_ids"
    DUPLICATE_IDS = "duplicate_ids"
    EXTRA_IDS = "extra_ids"
    EMPTY_TRANSLATIONS = "empty_translations"


RETRYABLE = {
    ViolationKind.MALFORMED_JSON,
    ViolationKind.MISSING_IDS,
    ViolationKind.DUPLICATE_IDS,
    ViolationKind.EXTRA_IDS,
    ViolationKind.EMPTY_TRANSLATIONS,
    "http_5xx",
    "http_429",  # ProviderRateLimitError — D06 §56.1 names it retryable (R-002)
    "read_timeout",
}
NOT_RETRYABLE = {
    "http_401",  # ProviderAuthenticationError (D06 §56.2)
    "http_403",
    "http_4xx",  # every remaining 4xx is request-side: declared explicitly
    # instead of falling through by omission (Review R-002)
    "invalid_input",  # our own request was wrong; fix the caller
}


@dataclass
class ProtocolReport:
    kind: str
    translations: dict[str, str] = field(default_factory=dict)
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.kind == ViolationKind.OK

    @property
    def retryable(self) -> bool:
        return self.kind in RETRYABLE


def validate_response(raw_text: str, expected_ids: tuple[str, ...]) -> ProtocolReport:
    """Validate one provider completion against the RegionID contract.

    Contract: the completion carries JSON {"translations":[{"region_id",
    "translated_text"}]}; every requested id appears exactly once; no
    unknown ids. Deviations classify per ViolationKind (D06 §56/§57 feed).
    """
    expected = list(expected_ids)
    try:
        data = json.loads(raw_text)
    except (ValueError, TypeError):
        return ProtocolReport(ViolationKind.MALFORMED_JSON, detail="response is not valid JSON")
    if not isinstance(data, dict) or not isinstance(data.get("translations"), list):
        return ProtocolReport(ViolationKind.MALFORMED_JSON, detail="missing translations[]")
    items = data["translations"]
    if not items:
        return ProtocolReport(ViolationKind.EMPTY_TRANSLATIONS, detail="no translations returned")

    mapping: dict[str, str] = {}
    duplicates: list[str] = []
    extra: list[str] = []
    for item in items:
        if not isinstance(item, dict) or "region_id" not in item or "translated_text" not in item:
            return ProtocolReport(ViolationKind.MALFORMED_JSON, detail=f"bad item: {item!r}")
        rid = item["region_id"]
        if not isinstance(rid, str):
            # R-001: a non-string id is out of range by definition; record it
            # instead of raising while the report is being built.
            extra.append(rid)
            continue
        if not isinstance(item["translated_text"], str):
            # R-001: never coerce — str(None) would fabricate the literal
            # translation "None". Provider output faults are retryable (§56.1).
            return ProtocolReport(
                ViolationKind.MALFORMED_JSON,
                translations=mapping,
                detail=f"non-string translated_text for {rid!r}: {item['translated_text']!r}",
            )
        if rid not in expected:
            extra.append(rid)
            continue
        if rid in mapping:
            duplicates.append(rid)
            continue
        mapping[rid] = item["translated_text"]

    missing = [rid for rid in expected if rid not in mapping]
    if missing:
        return ProtocolReport(
            ViolationKind.MISSING_IDS,
            translations=mapping,
            detail=f"missing: {_format_ids(missing)}",
        )
    if duplicates:
        return ProtocolReport(
            ViolationKind.DUPLICATE_IDS,
            translations=mapping,
            detail=f"duplicated: {_format_ids(duplicates)}",
        )
    if extra:
        return ProtocolReport(
            ViolationKind.EXTRA_IDS,
            translations=mapping,
            detail=f"out-of-range: {_format_ids(extra)}",
        )
    return ProtocolReport(ViolationKind.OK, translations=mapping)


def glossary_hits(translations: dict[str, str], glossary: dict[str, str]) -> list[str]:
    """Terminology consistency check: which glossary terms were applied."""
    hits = []
    for source, target in glossary.items():
        if any(target in translated for translated in translations.values()):
            hits.append(source)
    return sorted(hits)
