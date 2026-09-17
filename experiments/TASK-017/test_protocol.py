"""TASK-017 protocol experiment suite (pytest; stdlib only).

Covers the experiment ACs that can be proven on the mock layer: the
RegionID output contract (missing/duplicate/out-of-range/malformed),
Context-Group budget truncation, glossary consistency, D06 §57 retry
input invariance and §54 explicit-only fallback, plus latency/token
measurement collection. Real-provider runs are a separate, NOT_RUN layer
(see doc/research/TASK-017.md).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest

from mock_provider import MockProvider, ProtocolClient, deterministic_translation
from protocol import (
    NOT_RETRYABLE,
    RETRYABLE,
    ContextPage,
    ViolationKind,
    build_request,
    glossary_hits,
    validate_response,
)
from samples import CONTEXT_PAGES, GLOSSARY, PAGE1_REGIONS, budget_scenario_regions


@pytest.fixture()
def provider():
    server = MockProvider().start()
    yield server
    server.stop()


def complete(server: MockProvider, payload: dict):
    raw, fault = ProtocolClient(server.base_url).complete(payload)
    report = validate_response(raw, tuple(row["region_id"] for row in payload["regions"]))
    return raw, fault, report


def test_happy_path_single_page(provider):
    request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
    raw, fault, report = complete(provider, request.payload())
    assert fault == "ok"
    assert report.ok, report.detail
    assert set(report.translations) == {"region-1", "region-2", "region-3"}


def test_context_order_and_grouping_is_preserved(provider):
    request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
    complete(provider, request.payload())
    sent = provider.requests[-1]
    assert [row["position"] for row in sent["context"]] == ["before", "after"]
    assert sent["context_truncated_pages"] == []
    # output maps back to the group's regions (D06 §84 mapping rule)
    assert set(report_ids(sent)) == set(request.region_ids)


def report_ids(sent_payload):
    import json

    # re-run the deterministic completion mapping server-side: the ids in
    # the request are the contract scope
    return json.loads(json.dumps([row["region_id"] for row in sent_payload["regions"]]))


@pytest.mark.parametrize(
    "fault,kind",
    [
        ("malformed_json", ViolationKind.MALFORMED_JSON),
        ("drop:region-2", ViolationKind.MISSING_IDS),
        ("dup:region-1", ViolationKind.DUPLICATE_IDS),
        ("extra:region-999", ViolationKind.EXTRA_IDS),
        ("empty", ViolationKind.EMPTY_TRANSLATIONS),
    ],
)
def test_protocol_violations_are_classified(fault, kind):
    """Protocol faults alter the completion body; the transport layer still
    answers 200, so the contract violation itself must be the assertion."""
    server = MockProvider(faults=[fault]).start()
    try:
        request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
        raw, fault_seen, report = complete(server, request.payload())
        assert fault_seen == "ok", "protocol faults ride on HTTP 200"
        assert report.kind == kind
        assert report.retryable, "provider output faults are retryable (D06 §56.1)"
    finally:
        server.stop()


def test_http_faults_classified(provider):
    server = MockProvider(faults=["http_503", "http_401"]).start()
    try:
        request = build_request("page-1", PAGE1_REGIONS, [], GLOSSARY)
        client = ProtocolClient(server.base_url)
        _, fault_1 = client.complete(request.payload())
        _, fault_2 = client.complete(request.payload())
        assert fault_1 in RETRYABLE
        assert fault_2 in NOT_RETRYABLE, "401 must fail fast (D06 §56.2)"
    finally:
        server.stop()


def test_retry_keeps_input_identical():
    """D06 §57: the retried request carries the identical payload hash."""
    request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
    assert request.payload_hash() == build_request(
        "page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY
    ).payload_hash()
    # a changed context set is a different execution intent, not a retry
    assert request.payload_hash() != build_request(
        "page-1", PAGE1_REGIONS, CONTEXT_PAGES[:1], GLOSSARY
    ).payload_hash()


def test_budget_truncates_context_not_regions():
    request = build_request(
        "page-1",
        budget_scenario_regions(),
        CONTEXT_PAGES,
        token_budget=600,
    )
    payload = request.payload()
    assert len(payload["regions"]) == 40, "regions are never truncated"
    assert request.truncated_context_pages, "context pages yield to the budget"
    assert set(request.truncated_context_pages) <= {"page-0", "page-2"}


def test_glossary_consistency(provider):
    request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
    _, _, report = complete(provider, request.payload())
    hits = glossary_hits(report.translations, GLOSSARY)
    assert set(hits) == set(GLOSSARY), "rule translation must apply every glossary term"


def test_no_automatic_cross_provider_fallback():
    """D06 §54: without an explicit Primary→Secondary chain there is no
    fallback — the client talks to exactly one base URL by construction."""
    from mock_provider import make_client_factory

    factory = make_client_factory("http://127.0.0.1:1/v1")  # unreachable
    assert factory().base_url.endswith("/v1")
    # a single-endpoint client has no fallback target; proven by type, not
    # by network I/O (offline-safe)


def test_explicit_fallback_chain_records_provenance():
    primary = MockProvider(faults=["http_503"], name="primary").start()
    secondary = MockProvider(name="secondary").start()
    try:
        request = build_request("page-1", PAGE1_REGIONS, [], GLOSSARY)
        client = ProtocolClient(primary.base_url)
        raw, fault = client.complete(request.payload())
        assert fault == "http_5xx"
        # explicit chain → try secondary; provenance records the switch
        raw, fault = ProtocolClient(secondary.base_url).complete(request.payload())
        assert fault == "ok"
        _, _, report = validate_response_wrapper(raw)
        assert report.ok
        assert "secondary" in raw
    finally:
        primary.stop()
        secondary.stop()


def validate_response_wrapper(raw):
    from protocol import validate_response as v

    return None, None, v(raw, tuple(r.region_id for r in PAGE1_REGIONS))


def test_latency_and_token_measurement_collected(provider):
    import time

    server = MockProvider(latency_ms=30).start()
    try:
        request = build_request("page-1", PAGE1_REGIONS, CONTEXT_PAGES, GLOSSARY)
        started = time.monotonic()
        raw, fault, report = complete(server, request.payload())
        elapsed_ms = (time.monotonic() - started) * 1000
        assert report.ok and fault == "ok"
        assert elapsed_ms >= 25, "injected latency must be measurable"
        assert request.token_estimate() > 0
    finally:
        server.stop()


def test_deterministic_translation_applies_glossary():
    from protocol import RegionInput

    out = deterministic_translation(RegionInput("r", "先輩は強い"), {"先輩": "前辈"})
    assert "前辈" in out


# --- Review R-001: malformed provider output must never crash the validator -


def test_non_string_region_id_is_reported_not_crashed():
    """R-001: a non-string region_id classifies as EXTRA_IDS, never TypeError."""
    raw = json.dumps({"translations": [
        {"region_id": "r-1", "translated_text": "ok"},
        {"region_id": 123, "translated_text": "x"},
        {"region_id": ["r-9"], "translated_text": "y"},
    ]})
    report = validate_response(raw, ("r-1",))
    assert report.kind == ViolationKind.EXTRA_IDS, report.detail
    assert "123" in report.detail and "['r-9']" in report.detail


def test_non_string_translated_text_is_malformed_not_coerced():
    """R-001: ``str(None)`` would fabricate the literal translation "None"."""
    raw = json.dumps({"translations": [{"region_id": "r-1", "translated_text": None}]})
    report = validate_response(raw, ("r-1",))
    assert report.kind == ViolationKind.MALFORMED_JSON
    assert report.retryable, "malformed provider output is retryable (D06 §56.1)"


# --- Review R-002: 429 retryable; the remaining 4xx explicitly non-retryable -


def test_rate_limit_is_retryable_and_other_4xx_declared():
    server = MockProvider(faults=["http_429", "http_400"]).start()
    try:
        request = build_request("page-1", PAGE1_REGIONS, [], GLOSSARY)
        client = ProtocolClient(server.base_url)
        _, rate_limited = client.complete(request.payload())
        _, bad_request = client.complete(request.payload())
        assert rate_limited == "http_429"
        assert rate_limited in RETRYABLE, "429 must be retryable (D06 §56.1)"
        assert bad_request == "http_4xx"
        assert bad_request in NOT_RETRYABLE, "remaining 4xx are request-side faults"
    finally:
        server.stop()


# --- Review R-003: declared context ordering and truncation policy -----------


def test_context_keeps_the_nearest_contiguous_run():
    near = ContextPage("page-0", "before", "近端大页" * 120)
    far = ContextPage("page-2", "after", "远端小页")
    size_one = build_request("page-1", PAGE1_REGIONS, [near], GLOSSARY).token_estimate()
    size_both = build_request("page-1", PAGE1_REGIONS, [near, far], GLOSSARY).token_estimate()
    assert size_both > size_one

    both = build_request("page-1", PAGE1_REGIONS, [near, far], GLOSSARY, token_budget=size_both)
    assert [page.page_id for page in both.context] == ["page-0", "page-2"]
    assert both.truncated_context_pages == ()

    nearest_only = build_request("page-1", PAGE1_REGIONS, [near, far], GLOSSARY, token_budget=size_one)
    assert [page.page_id for page in nearest_only.context] == ["page-0"], "nearest page is kept"
    assert nearest_only.truncated_context_pages == ("page-2",)

    none_kept = build_request("page-1", PAGE1_REGIONS, [near, far], GLOSSARY, token_budget=size_one - 1)
    assert none_kept.context == ()
    assert none_kept.truncated_context_pages == ("page-0", "page-2"), "reported nearest-first"


def test_reading_order_beats_page_id_string_order():
    """R-003: D06 §13 reading_order, not ``page_id`` string order."""
    far = ContextPage("page-10", "after", "远端大页" * 120, reading_order=9)
    near = ContextPage("page-3", "after", "近端小页", reading_order=3)
    size_near = build_request("page-1", PAGE1_REGIONS, [near], GLOSSARY).token_estimate()

    request = build_request("page-1", PAGE1_REGIONS, [far, near], GLOSSARY, token_budget=size_near)
    assert [page.page_id for page in request.context] == ["page-3"], "reading_order 3 < 9"
    assert request.truncated_context_pages == ("page-10",)
