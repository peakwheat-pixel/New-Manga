"""FEA-11 assembly ports (C-17 §0 layering).

The application package never imports infrastructure directly: the bootstrap
hands it a ``SourceSyncStorage`` (the SQLite v8 gateway) and the live
``SourceReadGrantRegistry`` access port. This module declares the two
structural protocols and the single composition entry the bootstrap calls.
"""

from __future__ import annotations

from typing import Any, Protocol


class SourceGrantAccess(Protocol):
    """The live source-read grant registry face the sync stack uses."""

    def resolve(self, grant_id: str) -> Any: ...


class SourceSyncStorage(Protocol):
    """Structural subset of the v8 store the application stack relies on."""

    def get_plan(self, plan_id: str) -> Any: ...


def build_source_sync_stack(
    *,
    store,
    access,
    repository,
    pdf_open=None,
    clock=None,
) -> dict:
    """Compose scanner/planner/service/operations over one store+access.

    Returns the facade dict the bootstrap pins on the core bundle; the wire
    layer routes every C-17 command into it. One stack per process shares
    the in-memory live-scan registry (TTL-bounded)."""
    import time

    from application.sources.planner import SourceSyncPlanner
    from application.sources.runtime import SourceSyncOperations
    from application.sources.scanner import SourceScanner
    from application.sources.service import SourceSyncService

    tick = clock or time.time
    scanner = SourceScanner(
        store=store, access=access, pdf_open=pdf_open, clock=tick
    )
    planner = SourceSyncPlanner(store=store, scanner=scanner, clock=tick)
    service = SourceSyncService(
        store=store,
        scanner=scanner,
        planner=planner,
        access=access,
        repository=repository,
        pdf_open=pdf_open,
        clock=tick,
    )
    operations = SourceSyncOperations(store=store, access=access, clock=tick)
    return {
        "scanner": scanner,
        "planner": planner,
        "service": service,
        "operations": operations,
        "store": store,
    }
