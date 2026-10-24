"""Batch-A settings sections: write validation + typeset render defaults.

SETTINGS-OPEN-A-1 AC1/AC2, ``doc/design/SETTINGS_SECTION_SCHEMAS.md``
§2/§3.1-§3.5. Two faces:

- the Core settings wire (``settings.update_section`` through the real
  production assembly): the frozen batch-A white-list and value domains, typed
  ``INVALID_REQUEST`` BEFORE persistence, normalization, and the historical
  pass-through for sections whose schema is not frozen yet;
- the render consumer seam: ``ProductionHandlers.handle_render`` derives
  ``RenderTextStyle`` from the Run's frozen ``typeset`` snapshot and
  ``RenderService.rerender_region(style_defaults=...)`` forwards it into
  ``_prepare_region`` (same D03 §11.4 merge semantics as ``rerender_page``).
"""

from __future__ import annotations

import json
import itertools
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.rendering.service import RenderOutcome, RenderService, RenderStatus
from application.rendering.style import RenderTextStyle
from bootstrap.core_service import (
    PROTOCOL_MAJOR,
    PROTOCOL_MINOR,
    CoreServiceServer,
    assemble_production_core,
)
from bootstrap.settings_sections import (
    SettingsSectionError,
    validate_settings_section,
)
from domain.books.entities import ReadingDirection
from domain.pages.entities import Page
from domain.tasks.models import CommandType, PipelineScope, ScopeType
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    typeset_style_defaults,
)
from ports.rendering.direction import TextDirection
from ports.repositories.artifacts import ArtifactType


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
    request_id: str = "req-settings-a",
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
# the frozen batch-A value domains (design §3.1-§3.4)
# ---------------------------------------------------------------------------

_LEGAL_VALUES = {
    "ocr": {"script": "korean", "direction": "vertical"},
    "translate": {"context_pages": 3, "context_token_budget": 4096},
    "inpaint": {
        "preferred_quality": "quality",
        "background_complexity": "high",
        "dilate_radius": 4,
        "erode_radius": 1,
    },
    "typeset": {
        "text_color": "#112233",
        "stroke_enabled": False,
        "stroke_color": "#000000",
        "stroke_width": 3,
        "line_spacing": 2,
        "text_align": "center",
        "text_direction": "vertical",
        "auto_font_size": False,
        "font_size_offset": -2,
        "manual_font_size": 24,
    },
}

_NORMALIZED_VALUES = {
    "ocr": {"script": "korean", "direction": "vertical"},
    "translate": {"context_pages": 3, "context_token_budget": 4096},
    "inpaint": {
        "preferred_quality": "quality",
        "background_complexity": "high",
        "dilate_radius": 4,
        "erode_radius": 1,
    },
    "typeset": {
        "text_color": "#112233",
        "stroke_enabled": False,
        "stroke_color": "#000000",
        "stroke_width": 3.0,
        "line_spacing": 2.0,
        "text_align": "center",
        "text_direction": "vertical",
        "auto_font_size": False,
        "font_size_offset": -2,
        "manual_font_size": 24.0,
    },
}


# ---------------------------------------------------------------------------
# validator unit face
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("section", sorted(_LEGAL_VALUES))
def test_legal_section_values_are_accepted_and_normalized(section: str) -> None:
    normalized = validate_settings_section(section, _LEGAL_VALUES[section])
    assert normalized == _NORMALIZED_VALUES[section]
    assert set(normalized or {}) == set(_LEGAL_VALUES[section])


def test_json_numbers_are_normalized_to_their_schema_types() -> None:
    normalized = validate_settings_section(
        "typeset",
        {"stroke_width": 3, "line_spacing": 2, "manual_font_size": 24},
    )
    assert isinstance(normalized["stroke_width"], float)
    assert isinstance(normalized["line_spacing"], float)
    assert isinstance(normalized["manual_font_size"], float)
    integers = validate_settings_section("translate", {"context_pages": 3})
    assert type(integers["context_pages"]) is int


def test_manual_font_size_accepts_null() -> None:
    assert validate_settings_section("typeset", {"manual_font_size": None}) == {
        "manual_font_size": None
    }


@pytest.mark.parametrize(
    "values",
    [
        # review r1 M1: manual mode without a manual size makes every render
        # fail closed (StyleResolutionError), so the write is rejected.
        {"auto_font_size": False},
        {"auto_font_size": False, "manual_font_size": None},
        {"auto_font_size": False, "text_color": "#112233"},
    ],
)
def test_typeset_manual_mode_requires_a_manual_font_size(values: dict) -> None:
    with pytest.raises(SettingsSectionError) as raised:
        validate_settings_section("typeset", values)
    message = str(raised.value)
    assert "manual_font_size" in message
    assert "auto_font_size" in message


def test_typeset_auto_mode_allows_a_null_manual_font_size() -> None:
    assert validate_settings_section(
        "typeset", {"auto_font_size": True, "manual_font_size": None}
    ) == {"auto_font_size": True, "manual_font_size": None}


def test_typeset_manual_mode_with_a_size_is_accepted() -> None:
    values = {"auto_font_size": False, "manual_font_size": 24}
    assert validate_settings_section("typeset", values) == {
        "auto_font_size": False,
        "manual_font_size": 24.0,
    }


@pytest.mark.parametrize("section", sorted(_LEGAL_VALUES))
def test_empty_values_are_accepted_for_every_batch_a_section(section: str) -> None:
    assert validate_settings_section(section, {}) == {}


@pytest.mark.parametrize(
    "section", ["providers", "reading", "translation", "sfx", "future_section"]
)
def test_unknown_section_returns_none_for_passthrough(section: str) -> None:
    # design §3.5: sections whose schema is not frozen yet keep the historical
    # pass-through instead of inventing a whitelist.
    assert validate_settings_section(section, {"anything": {"nested": 1}}) is None


_UNKNOWN_KEYS = [
    ("ocr", {"lang": "japanese"}),
    ("translate", {"glossary": {"term": "x"}}),
    ("inpaint", {"route_policy": "auto"}),
    ("typeset", {"font_family": "Arial"}),
    # review r1 B2: fill_color has no consumer (RenderOp/layout/compositor do
    # not read it), so it was removed from the batch-A whitelist.
    ("typeset", {"fill_color": "#FFFFFF"}),
    ("typeset", {"definitely_not_a_key": True}),
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
    ("ocr", {"script": "large"}),
    ("ocr", {"direction": "up"}),
    ("translate", {"context_pages": 0}),
    ("translate", {"context_pages": 6}),
    ("translate", {"context_token_budget": 199}),
    ("translate", {"context_token_budget": 8001}),
    ("translate", {"context_pages": "3"}),
    ("inpaint", {"preferred_quality": "slow"}),
    ("inpaint", {"background_complexity": "extreme"}),
    ("inpaint", {"dilate_radius": -1}),
    ("inpaint", {"dilate_radius": 11}),
    ("inpaint", {"erode_radius": 11}),
    ("typeset", {"text_color": "red"}),
    ("typeset", {"stroke_color": "#1234567"}),
    ("typeset", {"text_color": "#GGGGGG"}),
    ("typeset", {"stroke_width": -0.1}),
    ("typeset", {"stroke_width": 20.1}),
    ("typeset", {"line_spacing": 0.9}),
    ("typeset", {"line_spacing": 3.1}),
    ("typeset", {"text_align": "justify"}),
    # review r1 M2: ``right`` is not implemented by either compositor.
    ("typeset", {"text_align": "right"}),
    ("typeset", {"text_direction": "diagonal"}),
    ("typeset", {"font_size_offset": -6}),
    ("typeset", {"font_size_offset": 6}),
    ("typeset", {"manual_font_size": 0}),
    ("typeset", {"manual_font_size": 500.1}),
    ("typeset", {"manual_font_size": "24"}),
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
        # ``bool`` is an ``int`` subclass: JSON booleans must never become
        # integer settings (nor the reverse).
        ("translate", "context_pages", True),
        ("translate", "context_pages", False),
        ("translate", "context_token_budget", True),
        ("inpaint", "dilate_radius", True),
        ("inpaint", "erode_radius", False),
        ("typeset", "font_size_offset", True),
        ("typeset", "stroke_width", True),
        ("typeset", "line_spacing", False),
        ("typeset", "manual_font_size", True),
        ("typeset", "stroke_enabled", 1),
        ("typeset", "auto_font_size", 0),
        ("ocr", "script", 1),
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


def test_four_sections_legal_write_round_trip_and_projection(server) -> None:
    for section, values in _LEGAL_VALUES.items():
        written = _request(
            server,
            "settings.update_section",
            {"section": section, "values": values},
        )
        assert written["error"] is None
        assert written["result"]["settings"][section] == _NORMALIZED_VALUES[section]

        read = _request(server, "settings.get", {"section": section})
        assert read["result"] == {
            "settings": {section: _NORMALIZED_VALUES[section]}
        }

    stored = server._core.pipeline_defaults.read().settings
    for section, expected in _NORMALIZED_VALUES.items():
        assert stored[section] == expected


@pytest.mark.parametrize(
    "section,key,bad",
    [
        ("ocr", "script", "large"),
        ("ocr", "direction", "up"),
        ("translate", "context_pages", 0),
        ("translate", "context_token_budget", 8001),
        ("inpaint", "preferred_quality", "slow"),
        ("inpaint", "dilate_radius", 11),
        ("typeset", "text_color", "red"),
        ("typeset", "stroke_width", 21),
        ("typeset", "font_size_offset", 6),
        ("typeset", "manual_font_size", 0),
        ("typeset", "text_align", "right"),
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

    # the R4 core assertion: the rejected write never reached the store
    read = _request(server, "settings.get", {"section": section})
    assert read["result"] == {
        "settings": {section: _NORMALIZED_VALUES[section]}
    }
    assert server._core.pipeline_defaults.read().settings[section] == (
        _NORMALIZED_VALUES[section]
    )


def test_wire_illegal_write_keeps_an_unset_section_unset(server) -> None:
    rejected = _request(
        server,
        "settings.update_section",
        {"section": "translate", "values": {"context_pages": 0}},
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    assert _request(server, "settings.get", {"section": "translate"})["result"] == {
        "settings": {"translate": None}
    }


def test_wire_typeset_manual_mode_without_size_rejected_and_not_persisted(
    server,
) -> None:
    """review r1 M1: the render-blocking combination never reaches the store."""
    for values in (
        {"auto_font_size": False},
        {"auto_font_size": False, "manual_font_size": None},
    ):
        rejected = _request(
            server,
            "settings.update_section",
            {"section": "typeset", "values": values},
        )
        assert rejected["result"] is None
        assert rejected["error"]["code"] == "INVALID_REQUEST"
        assert "manual_font_size" in rejected["error"]["message"]
        assert (
            server._core.pipeline_defaults.read().settings.get("typeset") is None
        )


@pytest.mark.parametrize(
    "section,values",
    [
        ("ocr", {"lang": "japanese"}),
        ("translate", {"glossary": {"term": "x"}}),
        ("inpaint", {"route_policy": "auto"}),
        ("typeset", {"font_family": "Arial"}),
        ("typeset", {"fill_color": "#FFFFFF"}),
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


def test_wire_bool_is_not_accepted_as_int(server) -> None:
    rejected = _request(
        server,
        "settings.update_section",
        {"section": "translate", "values": {"context_pages": True}},
    )
    assert rejected["result"] is None
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    assert "context_pages" in rejected["error"]["message"]
    assert server._core.pipeline_defaults.read().settings.get("translate") is None


def test_wire_unknown_section_still_passes_through(server) -> None:
    response = _request(
        server,
        "settings.update_section",
        {"section": "providers", "values": {"future_key": "x"}},
    )
    assert response["error"] is None
    assert response["result"]["settings"]["providers"] == {"future_key": "x"}


def test_wire_rejection_never_echoes_path_like_input(server) -> None:
    windows_path = r"C:\Users\settings-secret-agent\script.bin"
    rejected = _request(
        server,
        "settings.update_section",
        {"section": "ocr", "values": {"script": windows_path}},
    )
    assert rejected["error"]["code"] == "INVALID_REQUEST"
    serialized = json.dumps(rejected)
    assert windows_path not in serialized
    assert "settings-secret-agent" not in serialized


def _seed_page(core) -> str:
    """Create one book/chapter/page and return the page id."""
    suffix = next(_PAGE_COUNTER)
    book = core.library.create_book(
        f"设置书-{suffix}", default_reading_direction=ReadingDirection.LTR
    )
    chapter = core.library.create_chapter(book.book_id, f"第{suffix}话")
    page_id = f"page-settings-a-{suffix}"
    core.repository.add_page(
        Page(
            page_id=page_id,
            chapter_id=chapter.chapter_id,
            source_filename="page.png",
            source_order=1,
            sort_order=1,
            source_hash=f"hash-settings-a-{suffix}",
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


def test_saved_typeset_section_freezes_into_the_next_run_snapshot(server) -> None:
    """AC2 pre-condition: a saved section is what the NEXT Run snapshots and
    what ``handle_render`` therefore reads (the Run snapshot is frozen)."""
    written = _request(
        server,
        "settings.update_section",
        {"section": "typeset", "values": _LEGAL_VALUES["typeset"]},
    )
    assert written["error"] is None

    snapshot = _next_run_settings_snapshot(server)
    assert snapshot["typeset"] == _NORMALIZED_VALUES["typeset"]


def test_saved_translate_budget_freezes_into_the_next_run_snapshot(server) -> None:
    """SETTINGS-OPEN-A-1 §3.2 + Lead ruling 2026-10-22: the ordinary integer
    ``context_token_budget`` must survive the settings store's secret scrubber
    and therefore reach the next Run snapshot (and the translate handler)."""
    values = {"context_pages": 3, "context_token_budget": 4096}
    written = _request(
        server, "settings.update_section", {"section": "translate", "values": values}
    )
    assert written["error"] is None
    assert written["result"]["settings"]["translate"] == {
        "context_pages": 3,
        "context_token_budget": 4096,
    }

    snapshot = _next_run_settings_snapshot(server)
    assert snapshot["translate"] == {
        "context_pages": 3,
        "context_token_budget": 4096,
    }


# ---------------------------------------------------------------------------
# manual page rerender (command ``rerender_page``) applies the CURRENT global
# typeset settings immediately -- it has no Run snapshot to freeze
# ---------------------------------------------------------------------------


def _record_manual_rerender(server: CoreServiceServer) -> dict:
    """Replace the RenderService page entry with a recorder for this test."""
    recorded: dict = {}

    def fake_rerender_page(target_page_id: str, *, style_defaults=None):
        recorded["page_id"] = target_page_id
        recorded["style_defaults"] = style_defaults
        return RenderOutcome(
            status=RenderStatus.COMMITTED,
            artifact_id="artifact-manual-render",
            revision_no=1,
            managed_path="managed/translated.png",
            provenance_json=json.dumps({"ai_invoked": False}),
        )

    server._core.render.rerender_page = fake_rerender_page
    return recorded


def test_manual_rerender_page_uses_the_persisted_typeset_defaults(server) -> None:
    """AC2 second render path: no Run -> read the CURRENT global settings."""
    written = _request(
        server,
        "settings.update_section",
        {"section": "typeset", "values": _LEGAL_VALUES["typeset"]},
    )
    assert written["error"] is None
    page_id = _seed_page(server._core)
    recorded = _record_manual_rerender(server)

    response = _request(server, "rerender_page", {"page_id": page_id})

    assert response["error"] is None
    assert recorded["page_id"] == page_id
    style = recorded["style_defaults"]
    assert isinstance(style, RenderTextStyle)
    assert style.text_color == "#112233"
    assert style.stroke_enabled is False
    assert style.stroke_color == "#000000"
    assert style.stroke_width == 3.0
    assert style.line_spacing == 2.0
    assert style.text_align == "center"
    assert style.text_direction is TextDirection.VERTICAL
    assert style.auto_font_size_enabled is False
    assert style.font_size_offset == -2
    assert style.manual_font_size == 24.0


def test_manual_rerender_page_without_typeset_keeps_the_default_style(
    server,
) -> None:
    page_id = _seed_page(server._core)
    recorded = _record_manual_rerender(server)

    response = _request(server, "rerender_page", {"page_id": page_id})

    assert response["error"] is None
    assert recorded["style_defaults"] is None


# ---------------------------------------------------------------------------
# render consumer seam: handle_render -> rerender_region(style_defaults=...)
# ---------------------------------------------------------------------------


class _StubRegionRepository:
    def __init__(self, region) -> None:
        self._region = region

    def get_region(self, region_id: str):
        return self._region if region_id == self._region.region_id else None


class _StubArtifactLocator:
    def __init__(self, clean) -> None:
        self._clean = clean

    def locate_current(self, page_id: str, artifact_type):
        return self._clean if artifact_type is ArtifactType.CLEAN else None


class _StubStorage:
    def __init__(self, clean_path: Path) -> None:
        self._clean_path = clean_path

    def absolute_path(self, relative_path: str) -> str:
        return str(self._clean_path)


def _probe_region():
    return SimpleNamespace(
        region_id="r-style-probe",
        page_id="page-style-probe",
        deleted=False,
        region_locked=False,
        current_revision_id="rev-style-probe",
        region_type=SimpleNamespace(value="speech"),
        sfx_policy=SimpleNamespace(value="skip"),
        text=SimpleNamespace(final_translation="译文"),
        geometry=SimpleNamespace(bbox=SimpleNamespace(as_tuple=lambda: (0, 0, 10, 10))),
    )


def _probe_service(tmp_path: Path, captured: list) -> RenderService:
    clean_path = tmp_path / "clean.bin"
    clean_path.write_bytes(b"clean artifact bytes")
    service = RenderService(
        region_repo=_StubRegionRepository(_probe_region()),
        locator=_StubArtifactLocator(
            (
                SimpleNamespace(book_id="book-probe"),
                SimpleNamespace(managed_path="clean.bin"),
            )
        ),
        artifacts=None,
        storage=_StubStorage(clean_path),
        layout_engine=None,
        compositor=None,
        source_styles=None,
        font_catalog=None,
    )

    def fake_prepare(region, original_bytes, style_defaults, *, allow_sfx):
        captured.append(style_defaults)
        # Stop before composition: this test only owns the forwarded value.
        return SimpleNamespace(
            op=None, report=SimpleNamespace(skip_reason="style_probe")
        )

    service._prepare_region = fake_prepare
    return service


def test_rerender_region_forwards_style_defaults_to_prepare_region(
    tmp_path: Path,
) -> None:
    captured: list = []
    service = _probe_service(tmp_path, captured)
    defaults = RenderTextStyle(text_color="#112233", text_align="center")

    outcome = service.rerender_region("r-style-probe", style_defaults=defaults)

    assert outcome.status is RenderStatus.BLOCKED
    assert outcome.detail == "style_probe"
    assert captured == [defaults]

    # backward compatibility: the omitted keyword still forwards None
    service.rerender_region("r-style-probe")
    assert captured[-1] is None


class _RecordingRenderService:
    def __init__(self) -> None:
        self.calls: list[tuple[str, RenderTextStyle | None]] = []

    def rerender_region(self, region_id: str, *, style_defaults=None):
        self.calls.append((region_id, style_defaults))
        return RenderOutcome(
            status=RenderStatus.COMMITTED,
            artifact_id="artifact-translated",
            revision_no=1,
            managed_path="managed/translated.png",
            provenance_json=json.dumps({"ai_invoked": False}),
        )


def _render_call(settings_snapshot: dict) -> RenderTextStyle | None:
    recorded = _RecordingRenderService()
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=None,
            regions=None,
            region_writer=None,
            artifacts=None,
            images=None,
            geometry=None,
            render_service=recorded,
        )
    )
    unit = SimpleNamespace(
        target_id="r-render", region_id="r-render", step_type="render"
    )
    run = SimpleNamespace(settings_snapshot=settings_snapshot)
    handlers.handle_render(SimpleNamespace(), unit, run)
    assert len(recorded.calls) == 1
    region_id, style_defaults = recorded.calls[0]
    assert region_id == "r-render"
    return style_defaults


def test_handle_render_maps_the_typeset_whitelist_from_the_run_snapshot() -> None:
    style = _render_call({"typeset": _LEGAL_VALUES["typeset"]})
    assert isinstance(style, RenderTextStyle)
    assert style.text_color == "#112233"
    assert style.stroke_enabled is False
    assert style.stroke_color == "#000000"
    assert style.stroke_width == 3.0
    assert style.line_spacing == 2.0
    assert style.text_align == "center"
    assert style.text_direction is TextDirection.VERTICAL
    assert style.auto_font_size_enabled is False
    assert style.font_size_offset == -2
    assert style.manual_font_size == 24.0
    # font_family is deliberately NOT in the batch-A white-list: default kept.
    assert style.font_family == RenderTextStyle().font_family
    # fill_color has no consumer (review r1 B2) and is not mapped: a legacy
    # snapshot carrying it must not resurrect the fake control.
    assert "fill_color" not in _LEGAL_VALUES["typeset"]
    assert style.fill_color == RenderTextStyle().fill_color


@pytest.mark.parametrize(
    "snapshot",
    [
        {},
        {"typeset": None},
        {"typeset": "not-a-mapping"},
        {"typeset": []},
        {"typeset": {}},
    ],
)
def test_handle_render_passes_none_without_a_usable_typeset_section(
    snapshot: dict,
) -> None:
    assert _render_call(snapshot) is None


def test_typeset_style_defaults_is_defensive_against_corrupt_values() -> None:
    style = typeset_style_defaults(
        {
            "typeset": {
                "text_color": "#112233",
                # corrupted / legacy values are skipped, defaults kept
                "stroke_width": 99,
                "line_spacing": 0.1,
                "text_align": "right",
                "text_direction": "diagonal",
                "font_size_offset": 99,
                "manual_font_size": 10000,
            }
        }
    )
    assert isinstance(style, RenderTextStyle)
    assert style.text_color == "#112233"
    assert style.fill_color == RenderTextStyle().fill_color
    assert style.stroke_width == RenderTextStyle().stroke_width
    assert style.line_spacing == RenderTextStyle().line_spacing
    assert style.text_align == RenderTextStyle().text_align
    assert style.text_direction is TextDirection.AUTO
    assert style.font_size_offset == 0
    assert style.manual_font_size is None


def test_typeset_style_defaults_returns_none_when_nothing_is_usable() -> None:
    assert (
        typeset_style_defaults(
            {"typeset": {"font_family": "Some Font", "unknown": 1}}
        )
        is None
    )
