"""SFX policy settings channel (M2-SFX-TRANSLATE-ENTRY AC1/AC2/AC3).

The production detect chain used to land every SFX region at the domain
default SKIP (``models.py`` snapshot default; no configuration entry at
region creation), which kept the translation gate's translate path
production-unreachable (TA3-B2: 9/9 SFX regions skipped, SFX translation
evaluation n=0). The user ruling adds a *settings* entry:

- the policy is read at ASSEMBLY time from the persisted pipeline defaults
  row — ``settings["sfx"]["policy"]``, the same channel and row as the
  ``ocr.script`` key (``PipelineDefaultsService.save_settings_section``);
- the default (unconfigured install) stays SKIP — zero behavior change;
  precision-first stands until the user explicitly opts in;
- only SFX-typed detected candidates carry the configured policy; every
  other region type keeps SKIP regardless of configuration;
- an illegal value fails the assembly fast (the NEWMANGA_SFX_DETECTION /
  _CONF_THRESHOLD env-gate precedent), in the mock acceptance form too;
- a settings change takes effect on the NEXT assembly (re-assemble
  semantics, the pipeline-defaults row is the single source of truth —
  same as every other persisted key; no live reload).

The translate gate itself (``decide_sfx_translation``) already implements
the three-value semantics (M2-SFX-SEM-1) and is NOT modified here; these
tests pin the wiring that finally makes its translate path reachable.

Qt-free throughout: the mock assembly never executes the pixel/render
surface, so the matrix below runs on any interpreter. The full-chain
end-to-end (detect -> gate -> persisted translation) lives in
``tests/core/test_sfx_policy_end_to_end.py`` (Qt-backed, offscreen).
"""

from __future__ import annotations

from pathlib import Path
import sys

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.translation.color.service import SourceStyleService
from bootstrap.core_assembly import (
    _sfx_policy_from_settings,
    assemble_core_services,
)
from bootstrap.core_service import _PassthroughImageDecoder, _StubStyleAnalyzer
from domain.regions.entities import SfxPolicy


# ---------------------------------------------------------------------------
# fixtures / helpers
# ---------------------------------------------------------------------------


@pytest.fixture()
def assembled(tmp_path, monkeypatch):
    """One real production assembly on a temp root + env control (the same
    shape tests/core/test_sfx_assembly.py uses)."""
    for name in (
        "NEWMANGA_SFX_DETECTION",
        "NEWMANGA_SFX_WEIGHTS",
        "NEWMANGA_SFX_CONF_THRESHOLD",
        "NEWMANGA_DETECTOR_WEIGHTS",
    ):
        monkeypatch.delenv(name, raising=False)

    def _build(**kwargs):
        return assemble_core_services(
            tmp_path / "data",
            tmp_path / "managed",
            image_decoder=_PassthroughImageDecoder(),
            font_catalog=object(),  # type: ignore[arg-type]
            layout_engine=object(),  # type: ignore[arg-type]
            compositor=object(),  # type: ignore[arg-type]
            source_styles=SourceStyleService(_StubStyleAnalyzer()),
            **kwargs,
        )

    return _build


def _detect_deps(core):
    """The detect handler's dependencies behind the REAL assembly — the
    closure-unwrapping seam tests/core/test_core_detect.py established for
    the DSH r1 R9 wiring pin. ``deps.region_creator`` IS the assembly's own
    ``_create_detected_region`` closure."""
    wrapped = core.pipeline._executor._handlers["detect"]
    bound = next(
        cell.cell_contents
        for cell in (wrapped.__closure__ or [])
        if hasattr(cell.cell_contents, "__self__")
    )
    return bound.__self__.deps


def _seed_page(core, page_id: str = "page-1") -> None:
    """One book/chapter/page row set for the region creator to write against."""
    now = "2026-10-01T00:00:00Z"
    with core.conn:
        core.conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at)"
            " VALUES (?, ?, ?, ?)",
            ("book-1", "Book", now, now),
        )
        core.conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at,"
            " updated_at) VALUES (?, ?, ?, ?, ?)",
            ("chapter-1", "book-1", "Chapter", now, now),
        )
        core.conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename,"
            " source_order, sort_order, source_hash, source_size_bytes, width,"
            " height, managed_original_ref, created_at, updated_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                page_id, "chapter-1", "001.png", 0, 0, "hash", 3, 32, 16,
                "original/001.png", now, now,
            ),
        )


def _create_via_assembly(core, provider_label: str, reading_order: int):
    """Drive the assembly's own region-creator closure exactly the way the
    detect handler does (``region_creator(page_id, polygon, reading_order,
    provenance, provider_label)`` — infrastructure/providers/handlers.py)."""
    polygon = ((1.0, 1.0), (21.0, 1.0), (21.0, 11.0), (1.0, 11.0))
    region_id = _detect_deps(core).region_creator(
        "page-1", polygon, reading_order, {"provenance": "test"}, provider_label
    )
    return core.editing.get_region(region_id)


# ---------------------------------------------------------------------------
# pure-function policy selection (AC1: default / domain / fail-fast)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("settings", "expected"),
    [
        ({}, SfxPolicy.SKIP),  # unconfigured install: zero behavior change
        # other sections only (e.g. the ocr.script key) never touch the policy
        ({"ocr": {"script": "japanese"}}, SfxPolicy.SKIP),
        ({"sfx": {}}, SfxPolicy.SKIP),  # section present, key absent
        ({"sfx": {"policy": None}}, SfxPolicy.SKIP),  # explicit null = unset
        ({"sfx": {"policy": "skip"}}, SfxPolicy.SKIP),
        ({"sfx": {"policy": "translate"}}, SfxPolicy.TRANSLATE),
        ({"sfx": {"policy": "manual"}}, SfxPolicy.MANUAL),
        # normalized like the env gates (strip + lower) before validation
        ({"sfx": {"policy": "  TRANSLATE "}}, SfxPolicy.TRANSLATE),
        ({"sfx": {"policy": "Manual"}}, SfxPolicy.MANUAL),
    ],
)
def test_sfx_policy_from_settings_matrix(settings, expected):
    assert _sfx_policy_from_settings(settings) is expected


@pytest.mark.parametrize(
    "settings",
    [
        {"sfx": {"policy": "bogus"}},
        {"sfx": {"policy": "on"}},  # an env-gate word is not a policy value
        # present-but-blank is a configuration error, not a silent default
        {"sfx": {"policy": ""}},
        {"sfx": {"policy": "   "}},
        {"sfx": {"policy": 7}},  # not a string
        {"sfx": "translate"},  # malformed section shape
    ],
)
def test_sfx_policy_from_settings_illegal_fails_fast(settings):
    with pytest.raises(ValueError, match="sfx.policy"):
        _sfx_policy_from_settings(settings)


# ---------------------------------------------------------------------------
# assembly wiring (AC2: assemble reads the settings -> the region creator)
# ---------------------------------------------------------------------------


def test_default_assembly_creator_keeps_skip(assembled):
    """Zero behavior change: with no settings at all the REAL assembly's own
    region creator still lands SFX candidates at the domain SKIP default and
    speech candidates untouched."""
    core = assembled(mock_local_providers=True)
    try:
        _seed_page(core)
        sfx = _create_via_assembly(core, "sfx-1", 1)
        speech = _create_via_assembly(core, "manga-1", 2)
        assert sfx.region_type.value == "sfx"
        assert sfx.sfx_policy is SfxPolicy.SKIP
        assert speech.region_type.value == "speech"
        assert speech.sfx_policy is SfxPolicy.SKIP
    finally:
        core.conn.close()


def test_settings_policy_translate_reaches_the_creator(assembled):
    """The write/read round trip: ``save_settings_section("sfx", ...)`` ->
    re-assemble -> the SFX candidates carry the configured policy while
    speech candidates never do (non-SFX stays untouched by configuration)."""
    core = assembled(mock_local_providers=True)
    core.pipeline_defaults.save_settings_section("sfx", {"policy": "translate"})
    core.conn.close()

    core = assembled(mock_local_providers=True)  # re-assemble semantics
    try:
        _seed_page(core)
        sfx = _create_via_assembly(core, "sfx-1", 1)
        speech = _create_via_assembly(core, "manga-1", 2)
        assert sfx.region_type.value == "sfx"
        assert sfx.sfx_policy is SfxPolicy.TRANSLATE
        assert speech.region_type.value == "speech"
        assert speech.sfx_policy is SfxPolicy.SKIP
    finally:
        core.conn.close()


def test_settings_policy_manual_reaches_the_creator(assembled):
    core = assembled(mock_local_providers=True)
    core.pipeline_defaults.save_settings_section("sfx", {"policy": "manual"})
    core.conn.close()

    core = assembled(mock_local_providers=True)
    try:
        _seed_page(core)
        sfx = _create_via_assembly(core, "sfx-1", 1)
        assert sfx.sfx_policy is SfxPolicy.MANUAL
    finally:
        core.conn.close()


def test_settings_policy_illegal_fails_the_assembly(assembled):
    """Fail-fast at assembly (the env-gate precedent), in the mock
    acceptance form too — never a silent fallback to the default."""
    core = assembled(mock_local_providers=True)
    core.pipeline_defaults.save_settings_section("sfx", {"policy": "bogus"})
    core.conn.close()

    with pytest.raises(ValueError, match="sfx.policy"):
        assembled(mock_local_providers=True)
