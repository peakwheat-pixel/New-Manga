"""Batch-B1 settings sections: write validation + Run-snapshot projection.

SETTINGS-OPEN-B-1 AC1 (``doc/design/SETTINGS_SECTION_SCHEMAS.md`` §4.1-§4.2):

- the Core write gate ``settings.update_section`` accepts ONLY the frozen
  ``model_gpu`` / ``tasks`` white-list and their value domains, rejecting an
  unknown key or an illegal value with a typed ``INVALID_REQUEST`` BEFORE
  anything is persisted;
- a legal write is stored normalized (JSON numbers become their schema type)
  and is what the NEXT Run freezes into ``settings_snapshot`` -- the exact
  mapping the Run-time consumers (``heavy_runner`` device preference,
  ``_retry_policy_for_run`` retry policy) read. Those consumers are covered in
  ``tests/providers/test_handlers_b1_settings.py``; this module owns the write
  face and the "unset = null = historical behaviour" projection.
"""

from __future__ import annotations

import json
import itertools
from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from bootstrap.core_service import (  # noqa: E402
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from bootstrap.settings_sections import (  # noqa: E402
    SettingsSectionError,
    validate_settings_section,
)
from domain.books.entities import ReadingDirection  # noqa: E402
from domain.pages.entities import Page  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineScope,
    ScopeType,
)


_PAGE_COUNTER = itertools.count(1)


@pytest.fixture()
def server(tmp_path: Path):
    """One real production assembly on a temp root + its stdio server."""
    core = assemble_production_core(tmp_path / "data")
    try:
        yield CoreServiceServer(core)
    finally:
        core.conn.close()


def _request(
    server: CoreServiceServer,
    command: str,
    payload: dict,
    request_id: str = "req-settings-b1",
) -> dict:
    response, exit_flag = server.dispatch_request(
        json.dumps(
            {
                "protocol": "new-manga.core",
                "version": {"major": PROTOCOL_MAJOR, "minor": PROTOCOL_MINOR},
                "request_id": request_id,
                "command": command,
                "payload": payload,
            }
        )
    )
    assert not exit_flag
    return response


# ---------------------------------------------------------------------------
# the frozen batch-B1 value domains (design §4.1-§4.2)
# ---------------------------------------------------------------------------

_LEGAL_VALUES = {
    "model_gpu": {"device_preference": "gpu", "allow_cpu_fallback": False},
    "tasks": {"retry_max_attempts": 2, "retry_backoff_seconds": 2.5},
}

_NORMALIZED_VALUES = {
    "model_gpu": {"device_preference": "gpu", "allow_cpu_fallback": False},
    "tasks": {"retry_max_attempts": 2, "retry_backoff_seconds": 2.5},
}


# ---------------------------------------------------------------------------
# validator unit face
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("section", sorted(_LEGAL_VALUES))
def test_legal_section_values_are_accepted_and_normalized(section: str) -> None:
    normalized = validate_settings_section(section, _LEGAL_VALUES[section])
    assert normalized == _NORMALIZED_VALUES[section]
    assert set(normalized or {}) == set(_LEGAL_VALUES[section])


@pytest.mark.parametrize("preference", ["auto", "cpu", "gpu"])
def test_every_device_preference_is_accepted(preference: str) -> None:
    assert validate_settings_section(
        "model_gpu", {"device_preference": preference}
    ) == {"device_preference": preference}


def test_json_integer_backoff_is_normalized_to_float() -> None:
    normalized = validate_settings_section(
        "tasks", {"retry_backoff_seconds": 3}
    )
    assert normalized == {"retry_backoff_seconds": 3.0}
    assert isinstance(normalized["retry_backoff_seconds"], float)


def test_integer_attempts_stay_integer() -> None:
    normalized = validate_settings_section("tasks", {"retry_max_attempts": 1})
    assert normalized == {"retry_max_attempts": 1}
    assert type(normalized["retry_max_attempts"]) is int


def test_range_boundaries_are_inclusive() -> None:
    assert validate_settings_section(
        "tasks", {"retry_max_attempts": 3, "retry_backoff_seconds": 0.1}
    ) == {"retry_max_attempts": 3, "retry_backoff_seconds": 0.1}
    assert validate_settings_section(
        "tasks", {"retry_max_attempts": 1, "retry_backoff_seconds": 30}
    ) == {"retry_max_attempts": 1, "retry_backoff_seconds": 30.0}


@pytest.mark.parametrize("section", sorted(_LEGAL_VALUES))
def test_empty_values_are_accepted_for_every_b1_section(section: str) -> None:
    assert validate_settings_section(section, {}) == {}


@pytest.mark.parametrize(
    "section",
    # B-2/C sections are still unfrozen: the historical pass-through stays.
    ["cache_revision", "recycle_bin", "backup", "plugins", "future_section"],
)
def test_unknown_section_returns_none_for_passthrough(section: str) -> None:
    assert validate_settings_section(section, {"anything": {"nested": 1}}) is None


_UNKNOWN_KEYS = [
    # §4.1 explicitly keeps GPU concurrency closed (the single-slot gate is a
    # scheduler invariant): no whitelist entry, no fake control.
    ("model_gpu", {"gpu_concurrency": 2}),
    ("model_gpu", {"model_download_path": "C:/models"}),
    ("tasks", {"max_parallel_pages": 4}),
    ("tasks", {"max_parallel_steps": 2}),
    ("tasks", {"definitely_not_a_key": True}),
]


@pytest.mark.parametrize("section,values", _UNKNOWN_KEYS)
def test_unknown_key_rejected_with_field_and_allowed_keys(
    section: str, values: dict
) -> None:
    with pytest.raises(SettingsSectionError) as raised:
        validate_settings_section(section, values)
    message = str(raised.value)
    assert section in message
    assert "does not accept key" in message
    assert next(iter(values)) in message
    assert "allowed keys" in message


_ILLEGAL_VALUES = [
    ("model_gpu", {"device_preference": "tpu"}),
    ("model_gpu", {"device_preference": "GPU"}),
    ("model_gpu", {"device_preference": ""}),
    ("model_gpu", {"device_preference": None}),
    ("model_gpu", {"device_preference": 1}),
    ("model_gpu", {"allow_cpu_fallback": 1}),
    ("model_gpu", {"allow_cpu_fallback": 0}),
    ("model_gpu", {"allow_cpu_fallback": "true"}),
    ("model_gpu", {"allow_cpu_fallback": None}),
    ("tasks", {"retry_max_attempts": 0}),
    ("tasks", {"retry_max_attempts": 4}),
    ("tasks", {"retry_max_attempts": -1}),
    ("tasks", {"retry_max_attempts": "2"}),
    ("tasks", {"retry_max_attempts": 2.0}),
    ("tasks", {"retry_max_attempts": None}),
    ("tasks", {"retry_backoff_seconds": 0.09}),
    ("tasks", {"retry_backoff_seconds": 30.1}),
    ("tasks", {"retry_backoff_seconds": "1"}),
    ("tasks", {"retry_backoff_seconds": None}),
]


@pytest.mark.parametrize("section,values", _ILLEGAL_VALUES)
def test_illegal_value_rejected_with_field_name(section: str, values: dict) -> None:
    with pytest.raises(SettingsSectionError) as raised:
        validate_settings_section(section, values)
    message = str(raised.value)
    assert section in message
    assert next(iter(values)) in message
    assert "must be" in message


@pytest.mark.parametrize(
    "section,key,bad",
    [
        # ``bool`` is an ``int`` subclass: JSON booleans must never become an
        # integer setting (nor the reverse for the two bool keys).
        ("tasks", "retry_max_attempts", True),
        ("tasks", "retry_max_attempts", False),
        ("tasks", "retry_backoff_seconds", True),
        ("model_gpu", "allow_cpu_fallback", 1),
        ("model_gpu", "allow_cpu_fallback", 0),
    ],
)
def test_bool_and_int_are_not_interchangeable(
    section: str, key: str, bad: object
) -> None:
    with pytest.raises(SettingsSectionError):
        validate_settings_section(section, {key: bad})


# ---------------------------------------------------------------------------
# Core wire face: legal writes persist, illegal writes never do
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("section", sorted(_LEGAL_VALUES))
def test_wire_legal_write_round_trip_and_projection(server, section: str) -> None:
    written = _request(
        server,
        "settings.update_section",
        {"section": section, "values": _LEGAL_VALUES[section]},
    )
    assert written["error"] is None
    assert written["result"]["settings"][section] == _NORMALIZED_VALUES[section]

    read = _request(server, "settings.get", {"section": section})
    assert read["result"] == {
        "settings": {section: _NORMALIZED_VALUES[section]}
    }
    assert (
        server._core.pipeline_defaults.read().settings[section]
        == _NORMALIZED_VALUES[section]
    )


@pytest.mark.parametrize(
    "section,key,bad",
    [
        ("model_gpu", "device_preference", "tpu"),
        ("model_gpu", "allow_cpu_fallback", 1),
        ("tasks", "retry_max_attempts", 4),
        ("tasks", "retry_max_attempts", True),
        ("tasks", "retry_backoff_seconds", 0.0),
        ("tasks", "retry_backoff_seconds", 60),
    ],
)
def test_wire_illegal_value_rejected_before_persistence(
    server, section: str, key: str, bad: object
) -> None:
    good = _LEGAL_VALUES[section]
    written = _request(
        server, "settings.update_section", {"section": section, "values": good}
    )
    assert written["error"] is None

    rejected = _request(
        server,
        "settings.update_section",
        {"section": section, "values": {**good, key: bad}},
    )
    assert rejected["result"] is None
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    assert rejected["error"]["category"] == "validation"
    assert rejected["error"]["retryable"] is False
    assert key in rejected["error"]["message"]

    # the core assertion: the rejected write never reached the store
    read = _request(server, "settings.get", {"section": section})
    assert read["result"] == {
        "settings": {section: _NORMALIZED_VALUES[section]}
    }


@pytest.mark.parametrize(
    "section,values",
    [
        ("model_gpu", {"gpu_concurrency": 2}),
        ("model_gpu", {"model_download_path": "C:/models"}),
        ("tasks", {"max_parallel_pages": 4}),
    ],
)
def test_wire_unknown_key_rejected_and_not_persisted(
    server, section: str, values: dict
) -> None:
    rejected = _request(
        server, "settings.update_section", {"section": section, "values": values}
    )
    assert rejected["result"] is None
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    assert next(iter(values)) in rejected["error"]["message"]
    assert server._core.pipeline_defaults.read().settings.get(section) is None


@pytest.mark.parametrize("section", sorted(_LEGAL_VALUES))
def test_wire_unset_section_projects_null(server, section: str) -> None:
    """No write -> the section is absent, and ``settings.get`` projects null.

    This is the "unset" state the consumers must treat as the historical
    behaviour (``auto`` device, assembly-time retry policy), not as a default
    value that silently differs from the pre-B-1 runtime.
    """
    assert server._core.pipeline_defaults.read().settings.get(section) is None
    read = _request(server, "settings.get", {"section": section})
    assert read["result"] == {"settings": {section: None}}
    snapshot = _next_run_settings_snapshot(server)
    assert section not in snapshot


def test_wire_illegal_write_keeps_an_unset_section_unset(server) -> None:
    rejected = _request(
        server,
        "settings.update_section",
        {"section": "tasks", "values": {"retry_max_attempts": 99}},
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    assert server._core.pipeline_defaults.read().settings.get("tasks") is None
    assert _request(server, "settings.get", {"section": "tasks"})["result"] == {
        "settings": {"tasks": None}
    }


# ---------------------------------------------------------------------------
# Run snapshot projection: what the consumers actually read
# ---------------------------------------------------------------------------


def _seed_page(core) -> str:
    """Create one book/chapter/page and return the page id."""
    suffix = next(_PAGE_COUNTER)
    book = core.library.create_book(
        f"B1设置书-{suffix}", default_reading_direction=ReadingDirection.LTR
    )
    chapter = core.library.create_chapter(book.book_id, f"第{suffix}话")
    page_id = f"page-settings-b1-{suffix}"
    core.repository.add_page(
        Page(
            page_id=page_id,
            chapter_id=chapter.chapter_id,
            source_filename="page.png",
            source_order=1,
            sort_order=1,
            source_hash=f"hash-settings-b1-{suffix}",
            source_size_bytes=1,
            width=10,
            height=10,
            managed_original_ref=(
                f"books/{book.book_id}/chapters/{chapter.chapter_id}/page.png"
            ),
        )
    )
    return page_id


def _next_run_settings_snapshot(server: CoreServiceServer) -> dict:
    """Create one real Run over a fresh page and return its frozen snapshot."""
    core = server._core
    page_id = _seed_page(core)
    core.pipeline.set_scheduler_owner(True)
    run = core.pipeline.create_run(
        CommandType.RERENDER_SINGLE,
        PipelineScope(ScopeType.PAGE, selected_ids=(page_id,)),
    )
    return run.settings_snapshot


def test_saved_sections_freeze_into_the_next_run_snapshot(server) -> None:
    """AC2/AC3 pre-condition: the next Run freezes exactly the saved values."""
    for section, values in _LEGAL_VALUES.items():
        written = _request(
            server,
            "settings.update_section",
            {"section": section, "values": values},
        )
        assert written["error"] is None

    snapshot = _next_run_settings_snapshot(server)
    for section, expected in _NORMALIZED_VALUES.items():
        assert snapshot[section] == expected


def test_illegal_write_never_reaches_a_later_run_snapshot(server) -> None:
    """Fail-closed: a rejected write leaves the empty snapshot untouched."""
    rejected = _request(
        server,
        "settings.update_section",
        {"section": "model_gpu", "values": {"device_preference": "tpu"}},
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    rejected = _request(
        server,
        "settings.update_section",
        {"section": "tasks", "values": {"retry_max_attempts": 0}},
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"

    snapshot = _next_run_settings_snapshot(server)
    assert "model_gpu" not in snapshot
    assert "tasks" not in snapshot
