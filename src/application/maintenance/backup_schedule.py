"""Backup scheduling and retention policy (FEA-13-SCHED-5).

Pure, clock-injectable model: the Core owns execution (there is no Host timer),
so every scheduling decision is a deterministic function of ``(now, last)``.
Configuration lives in the existing ``application_metadata`` table -- no DDL.

ADJ-2026-11-09 D4 (retention): a manual package is an explicit user intent and is
never pruned automatically; the newest verified package and the ``pre_restore``
package of the most recent restore are protected from rotation as well.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

SCHEDULE_DAILY = "daily"
SCHEDULE_WEEKLY = "weekly"
SCHEDULE_CUSTOM_HOURS = "custom_hours"
SCHEDULE_DISABLED = "disabled"
SCHEDULE_KINDS = frozenset(
    {SCHEDULE_DAILY, SCHEDULE_WEEKLY, SCHEDULE_CUSTOM_HOURS, SCHEDULE_DISABLED}
)

DEFAULT_KIND = SCHEDULE_DAILY
DEFAULT_CUSTOM_HOURS = 24
DEFAULT_KEEP = 5
DEFAULT_MAX_FAILURES = 3


@dataclass(frozen=True)
class BackupSchedule:
    kind: str = DEFAULT_KIND
    hours: int = DEFAULT_CUSTOM_HOURS
    weekday: int | None = None  # 0=Monday .. 6=Sunday (weekly only)

    @property
    def enabled(self) -> bool:
        return self.kind != SCHEDULE_DISABLED

    def interval_hours(self) -> int:
        if self.kind == SCHEDULE_WEEKLY:
            return 7 * 24
        if self.kind == SCHEDULE_CUSTOM_HOURS:
            # ``0`` is legal here: the Core maps a zero legacy refresh window
            # to "anything already written is stale" (rotated on next start).
            return max(0, int(self.hours))
        return DEFAULT_CUSTOM_HOURS  # daily

    def due(self, now: datetime, last: datetime | None) -> bool:
        """True when a new automatic package is due at ``now``."""
        if not self.enabled:
            return False
        if last is None:
            return True
        return (now - last) >= timedelta(hours=self.interval_hours())


def parse_schedule(payload: object) -> BackupSchedule:
    """Never raise: an unknown/invalid shape degrades to the safe default."""
    if not isinstance(payload, dict):
        return BackupSchedule()
    kind = payload.get("kind")
    if kind not in SCHEDULE_KINDS:
        return BackupSchedule()
    hours = payload.get("hours", DEFAULT_CUSTOM_HOURS)
    if not isinstance(hours, int) or isinstance(hours, bool) or hours < 1:
        hours = DEFAULT_CUSTOM_HOURS
    weekday = payload.get("weekday")
    if (
        not isinstance(weekday, int)
        or isinstance(weekday, bool)
        or not 0 <= weekday <= 6
    ):
        weekday = None
    return BackupSchedule(kind=kind, hours=hours, weekday=weekday)


def parse_keep(value: object, default: int = DEFAULT_KEEP) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        return default
    return value


def parse_enabled(value: object, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    return default


def parse_max_failures(value: object, default: int = DEFAULT_MAX_FAILURES) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        return default
    return value


def next_due(now: datetime, schedule: BackupSchedule) -> datetime | None:
    """When the next automatic package becomes due (``None`` when disabled)."""
    if not schedule.enabled:
        return None
    return now + timedelta(hours=schedule.interval_hours())


def select_prunable(
    entries: list[dict],
    keep: int,
    protected_ids: set[str],
) -> list[dict]:
    """Automatic packages that may be rotated away.

    Manual packages are never candidates, and neither are protected ids (the
    newest verified package and the last restore's ``pre_restore`` -- D4).
    """
    automatic = [
        entry for entry in entries if entry.get("backup_type") == "automatic"
    ]
    automatic.sort(key=lambda entry: str(entry.get("created_at") or ""), reverse=True)
    # The newest ``keep`` packages are retained; a protected package that falls
    # outside that window is retained on top of the quota (D4 forbids deleting
    # the recovery chain), which is why the quota is a floor, never a ceiling
    # breach of protected data.
    retained = {str(entry.get("backup_id")) for entry in automatic[:keep]}
    retained.update(protected_ids)
    return [
        entry
        for entry in automatic
        if str(entry.get("backup_id")) not in retained
    ]
