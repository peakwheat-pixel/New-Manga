"""RegionID translation output protocol (D06 §18/§56/§84, TASK-017 absorbed).

This is the production copy of the TASK-017 experiment classifier
(``experiments/TASK-017/protocol.py``, reviewed head ``971efe6``). The
experiment module is not importable from production; its verified rules are
re-implemented here verbatim in behaviour, including the three Review fixes:

- **R-001** — non-string ``region_id`` is reported as out-of-range and a
  non-string ``translated_text`` fails the response; nothing is coerced with
  ``str()`` (``str(None)`` used to fabricate the literal translation "None");
- **R-002** — HTTP 429 is explicitly retryable, every remaining 4xx is
  explicitly non-retryable request-side input instead of falling through;
- **R-003** — context ordering uses ``reading_order`` (D06 §13) or the page
  ordinal as a declared fallback, never raw ``page_id`` string order, and
  truncation keeps the nearest contiguous run.

Every output item must map back onto the RegionIDs of the request; context
regions are never write targets (D06 §14/§18).
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, field

from ports.providers.errors import ProviderInputError, is_retryable


def estimate_tokens(text: str) -> int:
    """Cheap CJK-aware estimate (≈0.5–1 char per token); protocol-grade."""
    return max(1, sum(2 if ord(char) > 0x2E80 else 1 for char in text) // 2)


@dataclass(frozen=True)
class RegionInput:
    region_id: str
    text: str


@dataclass(frozen=True)
class ContextPage:
    page_id: str
    position: str  # "before" | "after" relative to the target page
    text: str
    #: D06 §13 reading order; ``None`` falls back to the page ordinal (R-003).
    reading_order: int | None = None


@dataclass(frozen=True)
class TranslationRequestPayload:
    """One Context Group request (D06 §18.1 input, §84 grouping)."""

    page_id: str
    regions: tuple[RegionInput, ...]
    context: tuple[ContextPage, ...] = ()
    glossary: dict[str, str] = field(default_factory=dict)
    truncated_context_pages: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.regions:
            raise ProviderInputError(
                "a Context Group needs at least one region", stage="translate"
            )
        for region in self.regions:
            if not isinstance(region.region_id, str) or not region.region_id:
                raise ProviderInputError(
                    f"invalid region_id in request: {region.region_id!r}",
                    stage="translate",
                )

    def payload(self) -> dict:
        return {
            "page_id": self.page_id,
            "regions": [
                {"region_id": region.region_id, "text": region.text}
                for region in self.regions
            ],
            "context": [
                {
                    "page_id": page.page_id,
                    "position": page.position,
                    "text": page.text,
                }
                for page in self.context
            ],
            "glossary": dict(self.glossary),
            "context_truncated_pages": list(self.truncated_context_pages),
        }

    def payload_json(self) -> str:
        return json.dumps(self.payload(), ensure_ascii=False, sort_keys=True)

    def payload_hash(self) -> str:
        """D06 §57: a retry must carry the byte-identical request payload."""
        return hashlib.sha256(self.payload_json().encode("utf-8")).hexdigest()

    @property
    def region_ids(self) -> tuple[str, ...]:
        return tuple(region.region_id for region in self.regions)

    @property
    def context_pages(self) -> tuple[str, ...]:
        return tuple(page.page_id for page in self.context)

    def token_estimate(self) -> int:
        return estimate_tokens(self.payload_json())


def _page_ordinal(page_id: str) -> int:
    """Trailing integer of a page id (``"page-12"`` → ``12``); 0 when absent."""
    digits = ""
    for char in reversed(page_id):
        if not char.isdigit():
            break
        digits = char + digits
    return int(digits) if digits else 0


def _context_sort_key(page: ContextPage) -> tuple[int, int, str]:
    """Nearest-first context ordering (TASK-017 R-003)."""
    if page.position not in {"before", "after"}:
        raise ProviderInputError(
            f"context position must be 'before'/'after': {page.position!r}",
            stage="translate",
        )
    ordinal = (
        page.reading_order
        if page.reading_order is not None
        else _page_ordinal(page.page_id)
    )
    return (0 if page.position == "before" else 1, ordinal, page.page_id)


def build_request_payload(
    page_id: str,
    regions: list[RegionInput] | tuple[RegionInput, ...],
    context_pages: Iterable[ContextPage] = (),
    glossary: dict[str, str] | None = None,
    token_budget: int | None = None,
) -> TranslationRequestPayload:
    """Group one page's regions with as much context as the budget allows.

    Truncation policy (declared, TASK-017 R-003): pages are considered
    nearest-first and kept while the request still fits; the first page that
    does not fit is dropped together with every farther page, so the kept set
    is always the nearest contiguous run. Region texts and glossary are never
    truncated (D06 §84).
    """
    ordered = sorted(context_pages, key=_context_sort_key)
    kept: list[ContextPage] = []
    truncated: list[str] = []

    def size_of(items: list[ContextPage]) -> int:
        probe = TranslationRequestPayload(
            page_id, tuple(regions), tuple(items), glossary or {}
        )
        return probe.token_estimate()

    for index, page in enumerate(ordered):
        if token_budget is not None and size_of([*kept, page]) > token_budget:
            truncated.extend(candidate.page_id for candidate in ordered[index:])
            break
        kept.append(page)
    return TranslationRequestPayload(
        page_id=page_id,
        regions=tuple(regions),
        context=tuple(kept),
        glossary=dict(glossary or {}),
        truncated_context_pages=tuple(truncated),
    )


class ViolationKind:
    """Stable classification of one provider completion."""

    OK = "ok"
    MALFORMED_JSON = "malformed_json"
    MISSING_IDS = "missing_ids"
    DUPLICATE_IDS = "duplicate_ids"
    EXTRA_IDS = "extra_ids"
    EMPTY_TRANSLATIONS = "empty_translations"


#: Retryable violations (D06 §56.1 / TASK-017 R-002).
RETRYABLE_VIOLATIONS = frozenset(
    {
        ViolationKind.MALFORMED_JSON,
        ViolationKind.MISSING_IDS,
        ViolationKind.DUPLICATE_IDS,
        ViolationKind.EXTRA_IDS,
        ViolationKind.EMPTY_TRANSLATIONS,
    }
)

#: Explicitly declared non-retryable transport codes (TASK-017 R-002).
NOT_RETRYABLE_HTTP_CODES = frozenset({"http_401", "http_403", "http_4xx"})
RETRYABLE_HTTP_CODES = frozenset({"http_429", "http_5xx", "read_timeout"})


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
        if self.kind in RETRYABLE_VIOLATIONS:
            return True
        if self.kind in NOT_RETRYABLE_HTTP_CODES:
            return False
        if self.kind in RETRYABLE_HTTP_CODES:
            return True
        return is_retryable(self.kind)

    def error_code(self) -> str:
        return "PROVIDER_INVALID_OUTPUT" if self.retryable else "INVALID_INPUT"


def _format_ids(values: Iterable[object]) -> str:
    """Render region ids for reports without assuming strings (R-001)."""
    return ", ".join(
        repr(value) if not isinstance(value, str) else value for value in values
    )


def validate_response(raw_text: str, expected_ids: tuple[str, ...]) -> ProtocolReport:
    """Validate one completion against the RegionID contract.

    Contract: the completion carries JSON
    ``{"translations": [{"region_id", "translated_text"}]}``; every requested
    id appears exactly once and no unknown id appears.
    """
    expected = list(expected_ids)
    try:
        data = json.loads(raw_text)
    except (ValueError, TypeError):
        return ProtocolReport(
            ViolationKind.MALFORMED_JSON, detail="response is not valid JSON"
        )
    if not isinstance(data, dict) or not isinstance(data.get("translations"), list):
        return ProtocolReport(
            ViolationKind.MALFORMED_JSON, detail="missing translations[]"
        )
    items = data["translations"]
    if not items:
        return ProtocolReport(
            ViolationKind.EMPTY_TRANSLATIONS, detail="no translations returned"
        )

    mapping: dict[str, str] = {}
    duplicates: list[str] = []
    extra: list[object] = []
    for item in items:
        if (
            not isinstance(item, dict)
            or "region_id" not in item
            or "translated_text" not in item
        ):
            return ProtocolReport(
                ViolationKind.MALFORMED_JSON, detail=f"bad item: {item!r}"
            )
        region_id = item["region_id"]
        if not isinstance(region_id, str):
            # R-001: a non-string id is out of range; record it, never raise
            # while the report is being built.
            extra.append(region_id)
            continue
        if not isinstance(item["translated_text"], str):
            # R-001: never coerce — str(None) would fabricate "None".
            return ProtocolReport(
                ViolationKind.MALFORMED_JSON,
                translations=mapping,
                detail=(
                    f"non-string translated_text for {region_id!r}:"
                    f" {item['translated_text']!r}"
                ),
            )
        if region_id not in expected:
            extra.append(region_id)
            continue
        if region_id in mapping:
            duplicates.append(region_id)
            continue
        mapping[region_id] = item["translated_text"]

    missing = [region_id for region_id in expected if region_id not in mapping]
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
    """Terminology consistency report: which glossary terms were applied."""
    hits = []
    for source, target in glossary.items():
        if any(target in translated for translated in translations.values()):
            hits.append(source)
    return sorted(hits)
