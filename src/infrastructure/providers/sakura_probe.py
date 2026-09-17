"""Sakura health/readiness probe (D08 AC-EXT-SAKURA-001, U-6 scope).

U-6 decision: the Sakura profile connection test reports **health and
readiness only** — no VRAM, no load, no throughput, no queue depth. The probe
therefore touches exactly two endpoints and reads only what is needed to tell
"the service answers and has a model" from "it does not":

1. ``GET {api_root}/models``  — readiness: reachable **and** at least one
   model is served (OpenAI-compatible ``data[]``);
2. ``GET {api_root}/health``  — liveness fallback for builds that do not
   expose ``/models``; a 200 here means healthy but readiness stays *unknown*
   unless ``/models`` also answered.

Every outcome is a typed reason code so the connection test can explain
itself instead of saying "连接失败":

``ready``            service answers and serves at least one model
``not_ready``        service answers but serves no model / non-200
``unreachable``      DNS/TCP/TLS/timeout failure
``invalid_response`` the endpoint answered with something not JSON
``not_configured``   no base_url configured for the profile

The real-service verification stays ``NOT_RUN`` in this environment because no
local Sakura instance runs here; the probe itself is exercised through the
injected transport.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from ports.network.profiles import NetworkProfile
from ports.network.transport import Transport, TransportError, TransportRequest
from ports.providers.errors import ProviderNotConfigured

REASON_READY = "ready"
REASON_NOT_READY = "not_ready"
REASON_UNREACHABLE = "unreachable"
REASON_INVALID_RESPONSE = "invalid_response"
REASON_NOT_CONFIGURED = "not_configured"

PATH_MODELS = "/models"
PATH_HEALTH = "/health"

HEALTH_INFO_NOTE = (
    "U-6 scope: health/readiness only — no VRAM, load or throughput probes"
)


@dataclass(frozen=True)
class SakuraProbeReport:
    """One connection test result for a Sakura profile."""

    provider_id: str
    endpoint: str
    healthy: bool
    ready: bool
    reason_code: str
    detail: str = ""
    http_status: int | None = None
    ready_endpoint: str = ""
    health_endpoint: str = ""
    models: tuple[str, ...] = ()
    elapsed_ms: int | None = None
    scope_note: str = HEALTH_INFO_NOTE

    def as_dict(self) -> dict:
        return {
            "provider_id": self.provider_id,
            "endpoint": self.endpoint,
            "healthy": self.healthy,
            "ready": self.ready,
            "reason_code": self.reason_code,
            "detail": self.detail,
            "http_status": self.http_status,
            "ready_endpoint": self.ready_endpoint,
            "health_endpoint": self.health_endpoint,
            "models": list(self.models),
            "elapsed_ms": self.elapsed_ms,
            "scope_note": self.scope_note,
        }

    def summary(self) -> str:
        state = "ready" if self.ready else ("healthy" if self.healthy else "unhealthy")
        return f"{state} ({self.reason_code}): {self.detail}"


@dataclass
class SakuraProbe:
    """Probe a local Sakura instance through the shared transport."""

    transport: Transport
    provider_id: str = "sakura-local"
    readiness_path: str = PATH_MODELS
    health_path: str = PATH_HEALTH
    requested_requests: list[str] = field(default_factory=list, init=False, repr=False)

    def probe(
        self,
        base_url: str,
        *,
        network_profile: NetworkProfile,
        timeout_seconds: float | None = None,
    ) -> SakuraProbeReport:
        started = time.perf_counter()
        if not base_url or not base_url.strip():
            return SakuraProbeReport(
                provider_id=self.provider_id,
                endpoint="",
                healthy=False,
                ready=False,
                reason_code=REASON_NOT_CONFIGURED,
                detail="no base_url configured for the Sakura profile",
            )
        root = base_url.strip().rstrip("/")
        ready_url = f"{root}{self.readiness_path}"
        health_url = f"{root}{self.health_path}"

        status, body, error = self._get(ready_url, network_profile)
        if error is not None:
            return SakuraProbeReport(
                provider_id=self.provider_id,
                endpoint=ready_url,
                healthy=False,
                ready=False,
                reason_code=_reason_for_error(error),
                detail=str(error),
                ready_endpoint=ready_url,
                health_endpoint=health_url,
                elapsed_ms=_elapsed(started),
            )
        if status != 200:
            # The service answered but is not serving models: a 503 from a
            # loading Sakura build is "not ready", not "unreachable".
            healthy = self._health_check(health_url, network_profile)
            return SakuraProbeReport(
                provider_id=self.provider_id,
                endpoint=ready_url,
                healthy=healthy,
                ready=False,
                reason_code=REASON_NOT_READY,
                detail=f"readiness endpoint answered HTTP {status}",
                http_status=status,
                ready_endpoint=ready_url,
                health_endpoint=health_url,
                elapsed_ms=_elapsed(started),
            )
        models, parse_error = _parse_models(body)
        if parse_error is not None:
            return SakuraProbeReport(
                provider_id=self.provider_id,
                endpoint=ready_url,
                healthy=True,
                ready=False,
                reason_code=REASON_INVALID_RESPONSE,
                detail=parse_error,
                http_status=status,
                ready_endpoint=ready_url,
                health_endpoint=health_url,
                elapsed_ms=_elapsed(started),
            )
        if not models:
            return SakuraProbeReport(
                provider_id=self.provider_id,
                endpoint=ready_url,
                healthy=True,
                ready=False,
                reason_code=REASON_NOT_READY,
                detail="service is up but serves no model",
                http_status=status,
                ready_endpoint=ready_url,
                health_endpoint=health_url,
                elapsed_ms=_elapsed(started),
            )
        return SakuraProbeReport(
            provider_id=self.provider_id,
            endpoint=ready_url,
            healthy=True,
            ready=True,
            reason_code=REASON_READY,
            detail=f"serving {len(models)} model(s)",
            http_status=status,
            ready_endpoint=ready_url,
            health_endpoint=health_url,
            models=models,
            elapsed_ms=_elapsed(started),
        )

    def _get(
        self, url: str, profile: NetworkProfile
    ) -> tuple[int | None, str, Exception | None]:
        self.requested_requests.append(url)
        try:
            outcome = self.transport.send(
                TransportRequest(method="GET", url=url, headers={}), profile
            )
        except TransportError as error:
            return None, "", error
        except OSError as error:  # pragma: no cover - transport normally wraps
            return None, "", error
        return (
            outcome.response.status,
            outcome.response.body.decode("utf-8", errors="replace"),
            None,
        )

    def _health_check(self, url: str, profile: NetworkProfile) -> bool:
        status, _body, error = self._get(url, profile)
        return error is None and status == 200


def _parse_models(body: str) -> tuple[tuple[str, ...], str | None]:
    try:
        data = json.loads(body)
    except (ValueError, TypeError):
        return (), "readiness endpoint did not answer JSON"
    if not isinstance(data, dict) or not isinstance(data.get("data"), list):
        return (), "readiness payload has no data[] array"
    models: list[str] = []
    for item in data["data"]:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            models.append(item["id"])
    return tuple(models), None


def _reason_for_error(error: Exception) -> str:
    if isinstance(error, ProviderNotConfigured):
        return REASON_NOT_CONFIGURED
    return REASON_UNREACHABLE


def _elapsed(started: float) -> int:
    return int((time.perf_counter() - started) * 1000)
