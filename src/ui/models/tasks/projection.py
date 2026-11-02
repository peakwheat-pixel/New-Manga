"""Backward-compatibility shim for task projection (M2-I2).

Authoritative location: application.tasks.projection.
This module is preserved as a non-authoritative compatibility shim for legacy
consumers. All domain/application logic resides in application.tasks.projection.
"""

from __future__ import annotations

from application.tasks.projection import (
    PageProjectionRow,
    STATUS_BLOCKED,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_PROCESSING,
    STATUS_SKIPPED,
    STATUS_WAITING,
    TaskProjection,
    build_projection,
    command_label,
    run_title,
    step_label,
)

__all__ = [
    "PageProjectionRow",
    "STATUS_BLOCKED",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_PROCESSING",
    "STATUS_SKIPPED",
    "STATUS_WAITING",
    "TaskProjection",
    "build_projection",
    "command_label",
    "run_title",
    "step_label",
]
