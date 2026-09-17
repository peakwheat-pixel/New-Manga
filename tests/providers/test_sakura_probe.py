"""Sakura health/readiness probe (AC-EXT-SAKURA-001, U-6 scope)."""

from __future__ import annotations

import json

from infrastructure.providers.openai_client import default_network_profile
from infrastructure.providers.sakura_probe import (
    HEALTH_INFO_NOTE,
    REASON_INVALID_RESPONSE,
    REASON_NOT_CONFIGURED,
    REASON_NOT_READY,
    REASON_READY,
    REASON_UNREACHABLE,
    SakuraProbe,
)
from ports.network.transport import TransportTimeoutError

from conftest import FakeTransport

BASE = "http://127.0.0.1:8080/v1"


def _models_body(*ids: str) -> bytes:
    return json.dumps({"object": "list", "data": [{"id": i} for i in ids]}).encode()


def test_ready_when_service_serves_a_model(fake_transport) -> None:
    fake_transport.responses[f"{BASE}/models"] = (200, _models_body("sakura-1.5"))
    probe = SakuraProbe(transport=fake_transport)
    report = probe.probe(BASE, network_profile=default_network_profile())
    assert report.healthy is True
    assert report.ready is True
    assert report.reason_code == REASON_READY
    assert report.models == ("sakura-1.5",)
    assert report.summary().startswith("ready")


def test_probe_only_reads_health_and_readiness_endpoints(fake_transport) -> None:
    """U-6: the connection test must not collect VRAM/load/throughput."""
    fake_transport.responses[f"{BASE}/models"] = (503, b"")
    fake_transport.responses[f"{BASE}/health"] = (200, b"ok")
    probe = SakuraProbe(transport=fake_transport)
    report = probe.probe(BASE, network_profile=default_network_profile())
    # Structured scope check: only the two health endpoints were touched, the
    # report carries no metric field, and no URL asks for deep telemetry.
    assert fake_transport.urls == [f"{BASE}/models", f"{BASE}/health"]
    assert report.reason_code == REASON_NOT_READY
    assert report.healthy is True
    assert report.ready is False

    assert set(report.as_dict()) == {
        "provider_id",
        "endpoint",
        "healthy",
        "ready",
        "reason_code",
        "detail",
        "http_status",
        "ready_endpoint",
        "health_endpoint",
        "models",
        "elapsed_ms",
        "scope_note",
    }
    for url in fake_transport.urls:
        assert not any(
            token in url for token in ("vram", "stats", "metric", "load", "queue")
        )
    assert report.scope_note == HEALTH_INFO_NOTE


def test_not_ready_when_service_serves_no_model(fake_transport) -> None:
    fake_transport.responses[f"{BASE}/models"] = (200, _models_body())
    probe = SakuraProbe(transport=fake_transport)
    report = probe.probe(BASE, network_profile=default_network_profile())
    assert (report.healthy, report.ready) == (True, False)
    assert report.reason_code == REASON_NOT_READY
    assert "no model" in report.detail


def test_invalid_payload_is_reported_as_an_invalid_response(fake_transport) -> None:
    fake_transport.responses[f"{BASE}/models"] = (200, b"<html>oops</html>")
    report = SakuraProbe(transport=fake_transport).probe(
        BASE, network_profile=default_network_profile()
    )
    assert report.reason_code == REASON_INVALID_RESPONSE
    assert report.healthy is True and report.ready is False


def test_connection_failure_reports_unreachable_with_reason(fake_transport) -> None:
    fake_transport.error = TransportTimeoutError("connect timed out")
    report = SakuraProbe(transport=fake_transport).probe(
        BASE, network_profile=default_network_profile()
    )
    assert (report.healthy, report.ready) == (False, False)
    assert report.reason_code == REASON_UNREACHABLE
    assert "timed out" in report.detail


def test_unconfigured_profile_fails_closed_without_any_request(fake_transport) -> None:
    report = SakuraProbe(transport=fake_transport).probe(
        "  ", network_profile=default_network_profile()
    )
    assert report.reason_code == REASON_NOT_CONFIGURED
    assert fake_transport.calls == []
