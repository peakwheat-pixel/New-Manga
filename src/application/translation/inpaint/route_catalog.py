"""Declared inpaint routes and the fail-closed route gate (D06 §21).

This is **declaration + policy**, not mechanism: the route table says which
routes exist, which are implemented and what each one requires; the raster
implementations live in ``infrastructure/providers/inpaint_routes.py``.

It sits in the application layer (not next to the adapters) so that the
Inpaint Step can consume the policy without importing infrastructure —
``doc/02_TECHNICAL_ARCHITECTURE_.md`` §架构方向 requires
``QML/UI → Application → Domain/Ports → Infrastructure Adapters`` with no
reverse dependency (Standards finding S-1/S-2 of the TASK-019 review).

TASK-018 R-007 is the governing rule: the table is an **explicit** mapping, and
a route with no implementation is ``not_implemented`` even when every
dependency is satisfied. Two routes are implemented today (Simple Fill, Edge
Bleed); the learned routes (Manga LaMa, AOT-GAN, BrushNet/PowerPaint, FLUX
Fill) are declared but unimplemented in this build — their quality/perf
evidence stays BLOCKED rather than being simulated.
"""

from __future__ import annotations

from dataclasses import dataclass

from ports.inpaint.ports import (
    IMPLEMENTED,
    LEARNED_ROUTES,
    NOT_IMPLEMENTED,
    ROUTE_EDGE_BLEED,
    ROUTE_SIMPLE_FILL,
)
from ports.providers.errors import ProviderNotImplemented


@dataclass(frozen=True)
class RouteRecord:
    """The declared state of one route — dependency satisfaction is separate."""

    route: str
    state: str
    reason: str
    requires_gpu: bool = False
    dependency_free: bool = False
    #: Provider registry id that implements this route ("" when none exists).
    provider_id: str = ""

    @property
    def runnable(self) -> bool:
        return self.state == IMPLEMENTED

    def as_dict(self) -> dict:
        return {
            "route": self.route,
            "state": self.state,
            "reason": self.reason,
            "requires_gpu": self.requires_gpu,
            "dependency_free": self.dependency_free,
            "provider_id": self.provider_id,
        }


#: Explicit route table (TASK-018 R-007). Absent route -> error by design.
ROUTE_TABLE: dict[str, RouteRecord] = {
    ROUTE_SIMPLE_FILL: RouteRecord(
        ROUTE_SIMPLE_FILL,
        IMPLEMENTED,
        "dependency-free baseline",
        dependency_free=True,
        provider_id="inpaint-simple-fill",
    ),
    ROUTE_EDGE_BLEED: RouteRecord(
        ROUTE_EDGE_BLEED,
        IMPLEMENTED,
        "dependency-free structural baseline (not a learned model)",
        dependency_free=True,
        provider_id="inpaint-edge-bleed",
    ),
    "manga-lama": RouteRecord(
        "manga-lama",
        NOT_IMPLEMENTED,
        "not implemented: no learned runtime/weights in this build",
        requires_gpu=True,
        provider_id="inpaint-manga-lama",
    ),
    "aot-gan": RouteRecord(
        "aot-gan",
        NOT_IMPLEMENTED,
        "not implemented: no learned runtime/weights in this build",
        requires_gpu=True,
        provider_id="inpaint-aot-gan",
    ),
    "brushnet": RouteRecord(
        "brushnet",
        NOT_IMPLEMENTED,
        "not implemented: no learned runtime/weights in this build",
        requires_gpu=True,
        provider_id="inpaint-brushnet",
    ),
    "flux-fill": RouteRecord(
        "flux-fill",
        NOT_IMPLEMENTED,
        "not implemented: no learned runtime/weights in this build",
        requires_gpu=True,
        provider_id="inpaint-flux-fill",
    ),
}


def route_record(route: str) -> RouteRecord:
    """Look up a route; an unregistered name is a hard error (R-007)."""
    try:
        return ROUTE_TABLE[route]
    except KeyError:
        raise ProviderNotImplemented(
            f"unknown inpaint route: {route!r}", stage="inpaint"
        ) from None


def provider_id_for_route(route: str) -> str:
    """Registry id implementing one route; empty when no provider exists."""
    return route_record(route).provider_id


def route_gate(
    route: str,
    *,
    requirements_satisfied: bool = True,
) -> RouteRecord:
    """Decide runnability: implementation first, then dependencies (R-007)."""
    record = route_record(route)
    if not record.runnable:
        return record
    if not requirements_satisfied:
        return RouteRecord(
            record.route,
            NOT_IMPLEMENTED,
            "required runtime/weights are missing",
            requires_gpu=record.requires_gpu,
            dependency_free=record.dependency_free,
        )
    return record


def describe_routes() -> tuple[RouteRecord, ...]:
    return tuple(ROUTE_TABLE[route] for route in sorted(ROUTE_TABLE))


def learned_routes_declared() -> frozenset[str]:
    """Guard: the learned set and the unimplemented set must stay in sync."""
    return frozenset(
        route for route, record in ROUTE_TABLE.items() if not record.runnable
    ) & LEARNED_ROUTES
