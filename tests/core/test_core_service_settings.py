"""Settings IPC channel over the production Core service (M2-SETTINGS-IPC-CHANNEL).

Exercises the two new stdio JSON-lines commands (``settings.get`` /
``settings.update_section``, contract M2-C1 rev 1.3 §5.3) at the
``dispatch_request`` level on a real production assembly:

- read: full projection + by-section, with the frozen None channel (an unset
  section reads as JSON ``null``, distinguishable from a written ``{}``);
- write: upsert through ``PipelineDefaultsService.save_settings_section``
  (the same channel/row as the ``ocr.script`` key);
- write-side validation, typed fail-closed BEFORE any persistence
  (M2-SFX-ENTRY r1 R4 lesson): ``sfx.policy`` three-value gate as the first
  instance, structural shapes for everything else -- an illegal value must
  never reach the store.

The real subprocess round trip (React → Tauri → this sidecar) is covered on
the Rust side (``real_core_sidecar_settings_round_trip``); the envelope
protocol minor bump 1 -> 2 is pinned here and in the Rust suite.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)


@pytest.fixture()
def server(tmp_path: Path):
    """One real production assembly on a temp root + its stdio server."""
    core = assemble_production_core(tmp_path / "data")
    try:
        yield CoreServiceServer(core)
    finally:
        core.conn.close()


def _request(server: CoreServiceServer, command: str, payload: dict) -> dict:
    line = json.dumps({
        "protocol": "new-manga.core",
        "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
        "request_id": "req-settings-1",
        "command": command,
        "payload": payload,
    })
    response, exit_flag = server.dispatch_request(line)
    assert not exit_flag
    return response


# ---------------------------------------------------------------------------
# protocol version (minor bump with the new command surface)
# ---------------------------------------------------------------------------


def test_protocol_minor_tracks_the_current_command_surface(server) -> None:
    # M2-SETTINGS-IPC-CHANNEL: 1 -> 2 (same backwards-compatible widening
    # precedent as M2-PROD-DETECT-3's core.detect bump; the pre-existing
    # command semantics are pinned unchanged by the existing suite).
    # M2-REGION-RETYPE-CORE: 2 -> 3 (set_region_type/list_regions added;
    # same widening precedent, contract rev 1.4 §5.4 -- this file pins the
    # settings pair's own semantics against the CURRENT envelope).
    # M2-PAGE-RESOURCE-RESOLVE-1: 4 -> 5 (resolve_page_resource added).
    assert (PROTOCOL_MAJOR, PROTOCOL_MINOR) == (2, 2)
    response = _request(server, "core.ping", {})
    assert response["error"] is None
    assert response["result"]["protocol_version"] == {"major": 2, "minor": 2}


# ---------------------------------------------------------------------------
# settings.get
# ---------------------------------------------------------------------------


def test_settings_get_full_projection_round_trip(server) -> None:
    written = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"policy": "translate"}},
    )
    assert written["error"] is None
    assert written["result"]["settings"]["sfx"] == {"policy": "translate"}

    read = _request(server, "settings.get", {})
    assert read["error"] is None
    assert read["result"]["settings"]["sfx"] == {"policy": "translate"}


def test_settings_get_by_section_unset_reads_null_not_empty(server) -> None:
    # frozen None channel: an unset section is JSON null (unknown/never
    # written), distinguishable from a written empty object.
    unset = _request(server, "settings.get", {"section": "sfx"})
    assert unset["error"] is None
    assert unset["result"] == {"settings": {"sfx": None}}

    _request(server, "settings.update_section", {"section": "ocr", "values": {}})
    written_empty = _request(server, "settings.get", {"section": "ocr"})
    assert written_empty["result"] == {"settings": {"ocr": {}}}
    assert written_empty["result"] != unset["result"]


def test_settings_get_empty_section_name_typed_rejected(server) -> None:
    for bad in ("", "   "):
        response = _request(server, "settings.get", {"section": bad})
        assert response["result"] is None
        assert response["error"]["code"] == "INVALID_REQUEST"
        assert response["error"]["category"] == "validation"
        assert response["error"]["retryable"] is False


# ---------------------------------------------------------------------------
# settings.update_section -- legal writes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("policy", ["skip", "translate", "manual"])
def test_settings_update_section_three_legal_policy_values(server, policy) -> None:
    response = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"policy": policy}},
    )
    assert response["error"] is None
    assert response["result"]["settings"]["sfx"] == {"policy": policy}


def test_settings_update_section_other_sections_pass_through(server) -> None:
    # the ocr.script precedent: non-sfx sections ride the same channel with
    # structural validation only (no key whitelist is invented here)
    response = _request(
        server, "settings.update_section",
        {"section": "ocr", "values": {"script": "large"}},
    )
    assert response["error"] is None
    assert response["result"]["settings"]["ocr"] == {"script": "large"}


def test_settings_update_section_sfx_without_policy_key_passes_through(server) -> None:
    # the gate fires on the policy KEY only; other sfx keys are transparent
    response = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"future_key": "x"}},
    )
    assert response["error"] is None
    assert response["result"]["settings"]["sfx"] == {"future_key": "x"}


# ---------------------------------------------------------------------------
# settings.update_section -- write-side validation (R4 lesson: typed
# fail-closed BEFORE persistence)
# ---------------------------------------------------------------------------


def test_settings_update_section_illegal_policy_typed_rejected_and_not_persisted(server) -> None:
    response = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"policy": "bogus"}},
    )
    assert response["result"] is None
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["error"]["category"] == "validation"
    assert response["error"]["retryable"] is False

    # the R4 core assertion: the store still holds the previous state -- an
    # illegal write can never surface as an assembly-time startup block
    read = _request(server, "settings.get", {"section": "sfx"})
    assert read["result"] == {"settings": {"sfx": None}}


def test_settings_update_section_illegal_policy_keeps_previous_legal_value(server) -> None:
    _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"policy": "manual"}},
    )
    rejected = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"policy": "auto"}},
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    read = _request(server, "settings.get", {"section": "sfx"})
    assert read["result"]["settings"]["sfx"] == {"policy": "manual"}


@pytest.mark.parametrize("bad_policy", [1, None, True, ["skip"], {"policy": "skip"}])
def test_settings_update_section_non_string_policy_typed_rejected(server, bad_policy) -> None:
    response = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": {"policy": bad_policy}},
    )
    assert response["result"] is None
    assert response["error"]["code"] == "INVALID_REQUEST"


@pytest.mark.parametrize("bad_section", ["", "   ", 1, None, ["sfx"]])
def test_settings_update_section_bad_section_typed_rejected(server, bad_section) -> None:
    response = _request(
        server, "settings.update_section",
        {"section": bad_section, "values": {"policy": "skip"}},
    )
    assert response["result"] is None
    assert response["error"]["code"] == "INVALID_REQUEST"
    assert response["error"]["category"] == "validation"


@pytest.mark.parametrize("bad_values", ["policy", 7, None, ["skip"], True])
def test_settings_update_section_non_object_values_typed_rejected(server, bad_values) -> None:
    response = _request(
        server, "settings.update_section",
        {"section": "sfx", "values": bad_values},
    )
    assert response["result"] is None
    assert response["error"]["code"] == "INVALID_REQUEST"


def test_settings_unknown_command_still_typed(server) -> None:
    # the widening adds exactly two commands; a near-miss name must stay the
    # existing UNKNOWN_COMMAND surface, not fall into the settings branches
    response = _request(server, "settings.update", {"section": "sfx"})
    assert response["error"]["code"] == "UNKNOWN_COMMAND"
