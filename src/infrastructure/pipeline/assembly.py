"""Production PipelineService assembly; tests must inject their own doubles."""

from __future__ import annotations

import sqlite3
from collections.abc import Mapping
from typing import Any

from application.tasks.service import PipelineService, ResourceLimits
from infrastructure.sqlite.pipeline import (
    SqlitePipelineStore,
    SqliteSnapshotProvider,
    SqliteTargetCatalog,
)

from .executor import ProductionStepExecutor, StepHandler


def build_production_pipeline(
    conn: sqlite3.Connection,
    *,
    handlers: Mapping[str, StepHandler] | None = None,
    settings: Mapping[str, Any] | None = None,
    provider_bindings: Mapping[str, Any] | None = None,
    constraint_snapshot_ref: str | None = None,
    context_policy: Mapping[str, Any] | None = None,
    limits: ResourceLimits | None = None,
) -> PipelineService:
    """Build a production service with no InMemory/Deterministic defaults."""
    return PipelineService(
        SqliteTargetCatalog(conn),
        store=SqlitePipelineStore(conn),
        snapshots=SqliteSnapshotProvider(
            conn,
            settings=settings,
            provider_bindings=provider_bindings,
            constraint_snapshot_ref=constraint_snapshot_ref,
            context_policy=context_policy,
        ),
        executor=ProductionStepExecutor(handlers),
        limits=limits,
    )
