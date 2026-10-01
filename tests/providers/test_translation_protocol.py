"""RegionID protocol classifier (TASK-017 absorbed: R-001/R-002/R-003)."""

from __future__ import annotations

import json

import pytest

from ports.translation.ports import require_valid_response
from ports.translation.protocol import (
    ProtocolReport,
    RETRYABLE_VIOLATIONS,
    ViolationKind,
    build_request_payload,
    glossary_hits,
    validate_response,
)
from ports.providers.errors import ProviderInputError, ProviderInvalidOutput


def _completion(translations) -> str:
    return json.dumps({"translations": translations}, ensure_ascii=False)


def test_valid_completion_maps_every_requested_region() -> None:
    report = validate_response(
        _completion(
            [
                {"region_id": "r1", "translated_text": "Hello"},
                {"region_id": "r2", "translated_text": "World"},
            ]
        ),
        ("r1", "r2"),
    )
    assert report.ok is True
    assert report.translations == {"r1": "Hello", "r2": "World"}
    assert report.retryable is False


@pytest.mark.parametrize(
    "raw,kind",
    [
        ("not json at all", ViolationKind.MALFORMED_JSON),
        ('{"translations": {}}', ViolationKind.MALFORMED_JSON),
        ('{"translations": []}', ViolationKind.EMPTY_TRANSLATIONS),
        ('{"translations": [{"region_id": "r1"}]}', ViolationKind.MALFORMED_JSON),
        (
            '{"translations": [{"region_id": "r1", "translated_text": "x"}]}',
            ViolationKind.MISSING_IDS,
        ),
    ],
)
def test_malformed_completions_are_classified_and_retryable(raw: str, kind: str) -> None:
    report = validate_response(raw, ("r1", "r2"))
    assert report.kind == kind
    assert report.retryable is True
    assert kind in RETRYABLE_VIOLATIONS


def test_duplicate_and_out_of_range_ids_are_rejected() -> None:
    duplicate = validate_response(
        _completion(
            [
                {"region_id": "r1", "translated_text": "a"},
                {"region_id": "r1", "translated_text": "b"},
                {"region_id": "r2", "translated_text": "c"},
            ]
        ),
        ("r1", "r2"),
    )
    assert duplicate.kind == ViolationKind.DUPLICATE_IDS
    assert duplicate.retryable is True

    extra = validate_response(
        _completion(
            [
                {"region_id": "r1", "translated_text": "a"},
                {"region_id": "r2", "translated_text": "b"},
                {"region_id": "context-9", "translated_text": "c"},
            ]
        ),
        ("r1", "r2"),
    )
    assert extra.kind == ViolationKind.EXTRA_IDS
    assert "context-9" in extra.detail


def test_r001_non_string_ids_are_reported_never_coerced() -> None:
    """R-001: a non-string id must not raise while the report is built."""
    report = validate_response(
        _completion(
            [
                {"region_id": 7, "translated_text": "a"},
                {"region_id": "r1", "translated_text": "b"},
            ]
        ),
        ("r1",),
    )
    assert report.kind == ViolationKind.EXTRA_IDS
    assert "7" in report.detail

    coercion = validate_response(
        _completion([{"region_id": "r1", "translated_text": None}]),
        ("r1",),
    )
    assert coercion.kind == ViolationKind.MALFORMED_JSON
    assert "None" in coercion.detail
    assert coercion.translations == {}


def test_r002_http_codes_are_explicitly_classified() -> None:
    assert ProtocolReport("http_429").retryable is True
    assert ProtocolReport("http_5xx").retryable is True
    assert ProtocolReport("read_timeout").retryable is True
    assert ProtocolReport("http_401").retryable is False
    assert ProtocolReport("http_403").retryable is False
    assert ProtocolReport("http_4xx").retryable is False
    assert ProtocolReport("invalid_input").retryable is False


def test_require_valid_response_maps_retryable_and_non_retryable() -> None:
    with pytest.raises(ProviderInvalidOutput) as retryable:
        require_valid_response(ProtocolReport(ViolationKind.MISSING_IDS, detail="x"))
    assert retryable.value.retryable is True

    with pytest.raises(ProviderInputError):
        require_valid_response(ProtocolReport("invalid_input", detail="bad request"))

    assert require_valid_response(ProtocolReport(ViolationKind.OK, {"r1": "ok"})) == {
        "r1": "ok"
    }


def test_glossary_hits_reports_applied_terms() -> None:
    assert glossary_hits({"r1": "Hero 登場"}, {"hero": "Hero"}) == ["hero"]
    assert glossary_hits({"r1": "x"}, {"hero": "Hero"}) == []


# --- M2-SFX-SEM-1: RegionInput.region_type widening -------------------------


def test_region_input_defaults_to_speech() -> None:
    """Widening compatibility (M2-FIX-LISTBOOKS rev-1.2 precedent): the old
    two-argument construction keeps its meaning — it is a speech region."""
    from ports.translation.protocol import DEFAULT_REGION_TYPE, RegionInput

    legacy = RegionInput("r1", "こんにちは")
    assert legacy.region_type == DEFAULT_REGION_TYPE == "speech"
    payload = build_request_payload("page-1", [legacy])
    assert payload.regions[0].region_type == "speech"


def test_region_type_values_match_domain_enum():
    """Cross-layer consistency (r2 R3): the local value set must track the domain enum."""
    from domain.regions.entities import RegionType

    assert set(REGION_TYPE_VALUES) == {t.value for t in RegionType}


def test_payload_accepts_every_region_type_value() -> None:
    from ports.translation.protocol import REGION_TYPE_VALUES, RegionInput

    regions = [
        RegionInput(f"r-{value}", "x", region_type=value)
        for value in sorted(REGION_TYPE_VALUES)
    ]
    payload = build_request_payload("page-1", regions)
    assert {region.region_type for region in payload.regions} == REGION_TYPE_VALUES


def test_payload_rejects_unknown_region_type() -> None:
    """Fail-closed: a region_type outside the value set is a typed request
    error, never silently forwarded to a provider."""
    from ports.translation.protocol import RegionInput

    with pytest.raises(ProviderInputError) as excinfo:
        build_request_payload(
            "page-1", [RegionInput("r1", "ドガ", region_type="onomatopoeia")]
        )
    assert excinfo.value.stage == "translate"


def test_payload_serializes_region_type() -> None:
    from ports.translation.protocol import RegionInput

    payload = build_request_payload(
        "page-1",
        [RegionInput("r1", "ドガ", region_type="sfx")],
    )
    body = json.loads(payload.payload_json())
    assert body["regions"] == [
        {"region_id": "r1", "text": "ドガ", "region_type": "sfx"}
    ]
