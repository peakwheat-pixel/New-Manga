"""PLUGIN-RUNTIME-1: local plugin discovery, manifest v1, default-off gating,
isolated hook invocation and the ``plugin_events`` audit ledger.

Real filesystem + real subprocesses (no mocks): every hook runs in a separate
``python -I`` interpreter, so these tests also prove that a crashed or slow
plugin cannot take the caller down.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.plugins.manifest import (  # noqa: E402
    HOOK_NAMES,
    ManifestError,
    parse_manifest,
)
from infrastructure.plugins.service import PluginError, PluginService  # noqa: E402

VALID_ENTRY = (
    "def after_detect(payload):\n"
    "    return {'seen': payload}\n"
    "\n"
    "def before_detect(payload):\n"
    "    return {'pages': payload.get('pages', [])}\n"
)

CRASHING_ENTRY = (
    "def after_detect(payload):\n"
    "    raise RuntimeError('boom')\n"
)

SLOW_ENTRY = (
    "import time\n"
    "def after_detect(payload):\n"
    "    time.sleep(3)\n"
    "    return {}\n"
)


@pytest.fixture()
def runtime(tmp_path: Path):
    from infrastructure.sqlite.connection import open_database
    from infrastructure.sqlite.migrator import MigrationRunner
    from infrastructure.sqlite.schema import default_migrations

    db_path = tmp_path / "library.db"
    conn, _opened = open_database(
        db_path,
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    plugin_root = tmp_path / "plugins"
    plugin_root.mkdir(parents=True, exist_ok=True)
    service = PluginService(
        conn, plugin_root, app_version="0.1.0", hook_timeout_seconds=5
    )
    try:
        yield {"conn": conn, "root": plugin_root, "service": service}
    finally:
        conn.close()


def write_plugin(
    plugin_root: Path,
    plugin_id: str,
    *,
    hooks: tuple[str, ...] = ("after_detect",),
    permissions: tuple[str, ...] = (),
    entry_source: str = VALID_ENTRY,
    manifest_overrides: dict | None = None,
) -> Path:
    directory = plugin_root / plugin_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "plugin.py").write_text(entry_source, encoding="utf-8")
    manifest = {
        "id": plugin_id,
        "name": f"Plugin {plugin_id}",
        "version": "1.0.0",
        "entry": "plugin.py",
        "hooks": list(hooks),
        "permissions": list(permissions),
    }
    manifest.update(manifest_overrides or {})
    (directory / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return directory


# ---------------------------------------------------------------------------
# manifest v1
# ---------------------------------------------------------------------------
def test_valid_manifest_parses_and_round_trips_frozen_fields(tmp_path: Path) -> None:
    directory = write_plugin(tmp_path, "acme-detect", hooks=("before_detect", "after_detect"))
    manifest = parse_manifest(directory, app_version="0.1.0")
    assert manifest.plugin_id == "acme-detect"
    assert manifest.hooks == ("before_detect", "after_detect")
    assert manifest.permissions == ()
    assert manifest.entry_path.is_file()
    assert set(HOOK_NAMES) >= set(manifest.hooks)


@pytest.mark.parametrize(
    ("plugin_id", "overrides", "permissions", "expected_code"),
    [
        ("acme-unknown-hook", {"hooks": ["before_unknown"]}, (), "PLUGIN_UNKNOWN_HOOK"),
        ("acme-unknown-perm", {}, ("shell",), "PLUGIN_UNKNOWN_PERMISSION"),
        ("acme-permissions", {}, ("files_read",), "PLUGIN_PERMISSIONS_UNSUPPORTED"),
        ("acme-bad-id", {"id": "other-id"}, (), "PLUGIN_ID_MISMATCH"),
        ("acme-missing-entry", {"entry": "nope.py"}, (), "PLUGIN_ENTRY_INVALID"),
        ("acme-escape-entry", {"entry": "../escape.py"}, (), "PLUGIN_ENTRY_INVALID"),
        ("acme-bad-version", {"version": "1.0"}, (), "PLUGIN_MANIFEST_INVALID"),
        ("acme-long-name", {"name": "x" * 81}, (), "PLUGIN_MANIFEST_INVALID"),
        ("acme-unknown-key", {"evil_unknown": True}, (), "PLUGIN_MANIFEST_INVALID"),
        ("acme-min-app", {"min_app_version": "9.9.9"}, (), "PLUGIN_MIN_APP_VERSION"),
    ],
)
def test_manifest_rejections_are_typed(
    tmp_path: Path, plugin_id: str, overrides: dict, permissions: tuple[str, ...], expected_code: str
) -> None:
    directory = write_plugin(tmp_path, plugin_id, permissions=permissions, manifest_overrides=overrides)
    with pytest.raises(ManifestError) as info:
        parse_manifest(directory, app_version="0.1.0")
    assert info.value.code == expected_code


# ---------------------------------------------------------------------------
# discovery + default-off gating
# ---------------------------------------------------------------------------
def test_discovery_lists_plugins_and_junk_is_rejected(runtime) -> None:
    root = runtime["root"]
    write_plugin(root, "acme-detect")
    write_plugin(root, "acme-broken", entry_source="def nope():\n    return 1\n")
    (root / "acme-bad-json").mkdir()
    (root / "acme-bad-json" / "manifest.json").write_text("{", encoding="utf-8")
    (root / ".hidden").mkdir()

    snapshot = runtime["service"].list_plugins()
    assert snapshot["global_enabled"] is False
    assert "plugin_root" not in snapshot
    statuses = {item["plugin_id"]: item["status"] for item in snapshot["plugins"]}
    assert statuses == {"acme-detect": "disabled", "acme-broken": "disabled", "acme-bad-json": "rejected"}
    rejected = [item for item in snapshot["plugins"] if item["plugin_id"] == "acme-bad-json"][0]
    assert rejected["reason"].startswith("PLUGIN_MANIFEST_INVALID")

    events = runtime["service"].audit_list(20)
    event_types = {event["event_type"] for event in events}
    assert "load_ok" in event_types
    assert "load_rejected" in event_types


def test_global_switch_defaults_off_and_gates_every_hook(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    write_plugin(root, "acme-detect")

    disabled = service.run_hook("after_detect", {"pages": []})
    assert disabled["applied"] is False
    assert disabled["reason"] == "plugins_disabled"

    service.set_global_enabled(True)
    # Global on but the plugin itself is still disabled by default.
    still_off = service.run_hook("after_detect", {"pages": []})
    assert still_off["applied"] is False

    service.set_plugin_enabled("acme-detect", True)
    applied = service.run_hook("after_detect", {"pages": ["p1"]})
    assert applied["applied"] is True
    assert applied["results"][0]["plugin_id"] == "acme-detect"
    seen = applied["results"][0]["result"]["seen"]
    assert seen["pages"] == ["p1"]
    # D3: every hook payload carries the versioned schema marker.
    assert seen["schema_ref"] == "nm-plugin-hook/1"


def test_rejected_plugin_cannot_be_enabled_and_unknown_id_is_not_found(runtime) -> None:
    root = runtime["root"]
    write_plugin(root, "acme-permissions", permissions=("files_read",))
    with pytest.raises(PluginError) as not_loaded:
        runtime["service"].set_plugin_enabled("acme-permissions", True)
    assert not_loaded.value.code == "PLUGIN_NOT_LOADED"
    with pytest.raises(PluginError) as missing:
        runtime["service"].set_plugin_enabled("acme-absent", True)
    assert missing.value.code == "PLUGIN_NOT_FOUND"


# ---------------------------------------------------------------------------
# isolated hook invocation
# ---------------------------------------------------------------------------
def test_crashing_hook_is_audited_and_never_raises(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    write_plugin(root, "acme-crash", entry_source=CRASHING_ENTRY)
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-crash", True)

    outcome = service.run_hook("after_detect", {"pages": []})
    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_FAILED"
    error_events = [
        event for event in service.audit_list(20) if event["event_type"] == "plugin_error"
    ]
    assert error_events and error_events[0]["plugin_id"] == "acme-crash"


def test_slow_hook_times_out_without_blocking_the_caller(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    write_plugin(root, "acme-slow", entry_source=SLOW_ENTRY)
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-slow", True)
    runtime["service"]._hook_timeout_seconds = 1  # type: ignore[attr-defined]

    outcome = service.run_hook("after_detect", {"pages": []})
    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_TIMEOUT"


def test_unknown_hook_and_bad_payload_are_typed_requests(runtime) -> None:
    service = runtime["service"]
    with pytest.raises(PluginError) as unknown:
        service.run_hook("before_nope")
    assert unknown.value.code == "PLUGIN_HOOK_UNKNOWN"
    with pytest.raises(PluginError) as bad_payload:
        service.run_hook("after_detect", [1, 2])  # type: ignore[arg-type]
    assert bad_payload.value.code == "PLUGIN_INVALID_REQUEST"


def test_audit_list_is_newest_first_and_validates_limit(runtime) -> None:
    service = runtime["service"]
    service.set_global_enabled(True)
    events = service.audit_list(10)
    assert events and events[0]["event_type"] == "enabled"
    assert events[0]["plugin_id"] == "__global__"
    with pytest.raises(PluginError) as bad_limit:
        service.audit_list(0)
    assert bad_limit.value.code == "PLUGIN_INVALID_REQUEST"

# ---------------------------------------------------------------------------
# review r1 security boundary (trusted code) and v6 schema
# ---------------------------------------------------------------------------
def test_v6_tables_start_empty_and_are_indexed(runtime) -> None:
    conn = runtime["conn"]
    assert conn.execute("SELECT COUNT(*) FROM plugin_state").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM plugin_events").fetchone()[0] == 0
    indexes = {
        row["name"]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'plugin_events'"
        )
    }
    assert "idx_plugin_events_plugin" in indexes
    assert "idx_plugin_events_type" in indexes


def test_hook_subprocess_gets_no_core_environment_or_path(runtime, monkeypatch) -> None:
    root = runtime["root"]
    service = runtime["service"]
    monkeypatch.setenv("NEWMANGA_DATA_ROOT", "G:/secret/data-root")
    monkeypatch.setenv("M2RC1_PYTHON", "G:/secret/python.exe")
    probe = (
        "import os, sys\n"
        "def after_detect(payload):\n"
        "    return {'env': sorted(os.environ), 'sys_path': sys.path}\n"
    )
    write_plugin(root, "acme-env", entry_source=probe)
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-env", True)
    outcome = service.run_hook("after_detect", {"pages": []})
    assert outcome["applied"] is True
    env = outcome["results"][0]["result"]["env"]
    # Trusted-code boundary: no Core configuration leaks into the child.
    assert "NEWMANGA_DATA_ROOT" not in env
    assert "M2RC1_PYTHON" not in env
    assert "PYTHONPATH" not in env
    # -I keeps the child off sys.path entries that would expose Core modules.
    for entry in outcome["results"][0]["result"]["sys_path"]:
        assert "New Manga" not in entry


def test_hook_subprocess_cannot_import_core_modules(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    entry = (
        "def after_detect(payload):\n"
        "    import infrastructure.sqlite.nmbak\n"
        "    return {'leaked': True}\n"
    )
    write_plugin(root, "acme-import", entry_source=entry)
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-import", True)
    outcome = service.run_hook("after_detect", {"pages": []})
    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_FAILED"


def test_hook_output_is_capped(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    # Multi-byte payload: 100k CJK chars ~= 300KB UTF-8, so the byte cap (not
    # a character count) must trip.
    entry = (
        "def after_detect(payload):\n"
        "    return {'blob': '\u4e2d' * 100000}\n"
    )
    write_plugin(root, "acme-loud", entry_source=entry)
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-loud", True)
    outcome = service.run_hook("after_detect", {"pages": []})
    assert outcome["applied"] is False
    assert outcome["errors"][0]["code"] == "PLUGIN_HOOK_FAILED"


def test_discovery_audit_is_state_driven_not_repeated(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    write_plugin(root, "acme-detect")
    service.list_plugins()
    service.list_plugins()
    events = service.audit_list(50)
    load_events = [event for event in events if event["event_type"] == "load_ok"]
    assert len(load_events) == 1

def test_enable_does_not_duplicate_load_ok(runtime) -> None:
    root = runtime["root"]
    service = runtime["service"]
    write_plugin(root, "acme-detect")
    service.list_plugins()
    service.set_global_enabled(True)
    service.set_plugin_enabled("acme-detect", True)
    service.list_plugins()
    service.list_plugins()
    load_events = [
        event for event in service.audit_list(50) if event["event_type"] == "load_ok"
    ]
    assert len(load_events) == 1
