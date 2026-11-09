"""FEA-13-SCHED-5: the pure schedule/retention model."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.maintenance.backup_schedule import (  # noqa: E402
    BackupSchedule,
    next_due,
    parse_enabled,
    parse_keep,
    parse_max_failures,
    parse_schedule,
    select_prunable,
)

NOW = datetime(2026, 11, 9, 12, 0, tzinfo=timezone.utc)


def test_daily_schedule_due_after_its_interval() -> None:
    schedule = BackupSchedule("daily")
    assert schedule.due(NOW, None) is True
    assert schedule.due(NOW, NOW - timedelta(hours=25)) is True
    assert schedule.due(NOW, NOW - timedelta(hours=23)) is False


def test_weekly_and_custom_intervals() -> None:
    weekly = BackupSchedule("weekly", weekday=0)
    assert weekly.interval_hours() == 7 * 24
    assert weekly.due(NOW, NOW - timedelta(hours=7 * 24 + 1)) is True
    custom = BackupSchedule("custom_hours", hours=6)
    assert custom.interval_hours() == 6
    assert custom.due(NOW, NOW - timedelta(hours=5)) is False
    assert custom.due(NOW, NOW - timedelta(hours=7)) is True


def test_disabled_never_becomes_due() -> None:
    schedule = BackupSchedule("disabled")
    assert schedule.enabled is False
    assert schedule.due(NOW, None) is False
    assert next_due(NOW, schedule) is None


def test_parse_degrades_invalid_shapes_to_the_default() -> None:
    assert parse_schedule(None) == BackupSchedule()
    assert parse_schedule({"kind": "nonsense"}) == BackupSchedule()
    assert parse_schedule({"kind": "custom_hours", "hours": 0}) == BackupSchedule(
        "custom_hours", hours=24
    )
    assert parse_schedule({"kind": "weekly", "weekday": 9}) == BackupSchedule(
        "weekly", weekday=None
    )
    assert parse_keep("5") == 5
    assert parse_keep(0) == 5
    assert parse_enabled("yes") is True
    assert parse_enabled(False) is False
    assert parse_max_failures(-1) == 3


def test_select_prunable_never_touches_manual_or_protected_packages() -> None:
    entries = [
        {"backup_id": "a1", "backup_type": "automatic", "created_at": "2026-11-09T01:00:00+00:00"},
        {"backup_id": "a2", "backup_type": "automatic", "created_at": "2026-11-09T02:00:00+00:00"},
        {"backup_id": "a3", "backup_type": "automatic", "created_at": "2026-11-09T03:00:00+00:00"},
        {"backup_id": "m1", "backup_type": "manual", "created_at": "2026-11-09T04:00:00+00:00"},
        {"backup_id": "p1", "backup_type": "pre_restore", "created_at": "2026-11-09T05:00:00+00:00"},
    ]

    prunable = select_prunable(entries, keep=1, protected_ids={"a3"})

    assert [entry["backup_id"] for entry in prunable] == ["a2", "a1"]


def test_select_prunable_covers_core_package_types_except_manual() -> None:
    entries = [
        {"backup_id": "m1", "backup_type": "manual", "created_at": "2026-11-09T06:00:00+00:00"},
        {"backup_id": "pm1", "backup_type": "pre_migration", "created_at": "2026-11-09T01:00:00+00:00"},
        {"backup_id": "pr1", "backup_type": "pre_restore", "created_at": "2026-11-09T02:00:00+00:00"},
        {"backup_id": "a1", "backup_type": "automatic", "created_at": "2026-11-09T03:00:00+00:00"},
        {"backup_id": "a2", "backup_type": "automatic", "created_at": "2026-11-09T04:00:00+00:00"},
    ]

    prunable = select_prunable(entries, keep=2, protected_ids={"pr1"})

    ids = [entry["backup_id"] for entry in prunable]
    assert "m1" not in ids, "manual packages are never pruned"
    assert "pr1" not in ids, "the last restore's pre_restore is protected"
    assert ids == ["pm1"]
