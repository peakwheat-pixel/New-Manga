"""N-01 (r4): Host source-sync Core command names must exist in the Core
registration tables (app channel or host-control channel). A drift here is
exactly what r3 P1-01 found: the Host called CamelCase names the Core never
registered, so every plan/query command was UNKNOWN_COMMAND over the Host.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _host_bindings() -> dict[str, str]:
    text = (REPO / "apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs").read_text(encoding="utf-8")
    return dict(re.findall(r'\["(source_[a-z_]+)"\] = new\("([^"]+)", \d+\)', text))


def _core_commands() -> set[str]:
    text = (REPO / "src/bootstrap/core_service.py").read_text(encoding="utf-8")
    app_start = text.index("_SOURCE_SYNC_APP_COMMANDS = frozenset({")
    app_end = text.index("})", app_start)
    host_start = text.index("_HOST_CONTROL_COMMANDS = frozenset({")
    host_end = text.index("})", host_start)
    names = set(re.findall(r'"([A-Za-z0-9_.]+)"', text[app_start:app_end]))
    names |= set(re.findall(r'"([A-Za-z0-9_.]+)"', text[host_start:host_end]))
    return names


def test_host_source_sync_core_commands_are_registered_in_core():
    host = _host_bindings()
    core = _core_commands()
    assert len(host) == 14, host
    missing = {
        host_name: core_name
        for host_name, core_name in host.items()
        if core_name not in core
    }
    assert missing == {}, f"Host calls Core names that Core never registers: {missing}"


def test_host_source_sync_commands_split_across_the_two_core_channels():
    host = _host_bindings()
    text = (REPO / "src/bootstrap/core_service.py").read_text(encoding="utf-8")
    app_start = text.index("_SOURCE_SYNC_APP_COMMANDS = frozenset({")
    app_end = text.index("})", app_start)
    host_start = text.index("_HOST_CONTROL_COMMANDS = frozenset({")
    host_end = text.index("})", host_start)
    app = set(re.findall(r'"([A-Za-z0-9_.]+)"', text[app_start:app_end]))
    hostctl = set(re.findall(r'"([A-Za-z0-9_.]+)"', text[host_start:host_end]))
    write_commands = {
        "source_scan_sync", "source_apply_sync_plan", "source_relink",
        "source_repoint", "source_resync", "source_acknowledge_operation",
        "source_complete_operation_recovery", "source_record_operation_failure",
    }
    read_commands = {
        "source_plan_sync", "source_preview_sync_plan", "source_confirm_sync_plan",
        "source_invalidate_sync_plan", "source_get_operation", "source_cancel_operation",
    }
    for host_name, core_name in host.items():
        if host_name in write_commands:
            assert core_name in hostctl, (host_name, core_name)
        elif host_name in read_commands:
            assert core_name in app, (host_name, core_name)

def test_plan_materialization_command_rides_host_control_only():
    """C-17 v1.2 (FEA-11-HOST-AUTH-3): the read-only projection is host-control.

    It must be in ``_HOST_CONTROL_COMMANDS`` and never on the application
    channel, and it must NOT add a HostCommandRegistry/C-07 entry.
    """
    text = (REPO / "src/bootstrap/core_service.py").read_text(encoding="utf-8")
    app_start = text.index("_SOURCE_SYNC_APP_COMMANDS = frozenset({")
    app_end = text.index("})", app_start)
    host_start = text.index("_HOST_CONTROL_COMMANDS = frozenset({")
    host_end = text.index("})", host_start)
    app = set(re.findall(r'"([A-Za-z0-9_.]+)"', text[app_start:app_end]))
    hostctl = set(re.findall(r'"([A-Za-z0-9_.]+)"', text[host_start:host_end]))

    assert "GetSourceSyncPlanMaterialized" in hostctl
    assert "GetSourceSyncPlanMaterialized" not in app
    host = _host_bindings()
    assert "GetSourceSyncPlanMaterialized" not in host.values(), (
        "the projection is Host-internal; it must not become a C-07/UI command"
    )
