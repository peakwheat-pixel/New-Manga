"""Batch-A ``typeset`` defaults merge into one prepared region (AC2, review B1).

Review r1 blocker B1: the old merge priority silently discarded 7 of the 11
``typeset`` keys on both render paths, because it used the *synthesised*
``RenderTextStyle`` (``from_domain``) as if it were persisted Region state.
These tests run the REAL ``RenderService._prepare_region`` (the port adapters
are deterministic fakes, so the assertions are exact) and pin:

- a Region with no persisted style inherits every applicable ``typeset``
  default into the final ``RenderOp`` / layout request;
- a Region that DID persist a style keeps winning over the defaults
  (D03 §11.4), including persisted-only ``text_color``;
- ``style_defaults=None`` keeps the historical ``from_domain`` behaviour.

They fail on the pre-r2 implementation of ``_merge_defaults`` (evidence kept in
``verification/SETTINGS-OPEN-A-1/core-r2-b1-old-impl-failure.txt``).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.rendering.service import RenderService  # noqa: E402
from application.rendering.style import RenderTextStyle  # noqa: E402
from domain.regions.entities import (  # noqa: E402
    BBox,
    Region,
    RegionGeometry,
    TextStyle,
)
from ports.rendering.direction import TextDirection  # noqa: E402
from ports.rendering.ports import LayoutRequest, LayoutResult, ResolvedFont  # noqa: E402


class _RecordingLayoutEngine:
    """Deterministic text engine: always fits, records every request."""

    def __init__(self) -> None:
        self.requests: list[LayoutRequest] = []

    def layout(self, request: LayoutRequest) -> LayoutResult:
        self.requests.append(request)
        return LayoutResult(
            items=(),
            extents_width=0.0,
            extents_height=0.0,
            fits=True,
            font_available=True,
            resolved_family=request.font_family,
        )


class _FixedFontCatalog:
    def resolve(self, family: str) -> ResolvedFont:
        return ResolvedFont(
            requested_family=family, resolved_family=family, available=True
        )


def _service() -> tuple[RenderService, _RecordingLayoutEngine]:
    engine = _RecordingLayoutEngine()
    service = RenderService(
        region_repo=None,
        locator=None,
        artifacts=None,
        storage=None,
        layout_engine=engine,
        compositor=None,
        source_styles=None,
        font_catalog=_FixedFontCatalog(),
    )
    return service, engine


def _region(style: TextStyle | None = None) -> Region:
    region = Region(
        region_id="region-typeset-merge",
        page_id="page-typeset-merge",
        geometry=RegionGeometry(bbox=BBox(10, 20, 220, 120)),
        style=style or TextStyle(),
    )
    region.text.machine_translation = "译文"
    region.text.refresh_final()
    return region


def _typeset_defaults(**overrides) -> RenderTextStyle:
    values = dict(
        text_color="#112233",
        stroke_enabled=False,
        stroke_color="#0000FF",
        stroke_width=4.0,
        line_spacing=2.0,
        text_align="center",
        text_direction=TextDirection.VERTICAL,
        font_size_offset=-2,
        auto_font_size_enabled=True,
        manual_font_size=None,
    )
    values.update(overrides)
    return RenderTextStyle(**values)


def _prepare(service: RenderService, region: Region, defaults):
    return service._prepare_region(region, None, defaults, allow_sfx=True)


def test_default_region_inherits_every_typeset_default_into_the_render_op() -> None:
    """B1: a brand-new Region (no persisted style) must render with the
    ``typeset`` defaults, not with the synthesised zero-stroke snapshot."""
    service, engine = _service()

    prepared = _prepare(service, _region(), _typeset_defaults())

    assert prepared.op is not None, prepared.report.skip_reason
    op = prepared.op
    assert op.text_color == "#112233"
    assert op.stroke_enabled is False
    assert op.stroke_color == "#0000FF"
    assert op.stroke_width == 4.0
    assert op.text_align == "center"
    assert op.direction is TextDirection.VERTICAL
    assert op.font_size == 24.0  # fallback 26 + font_size_offset(-2)
    assert prepared.report.resolution is not None
    assert prepared.report.resolution.font_size_offset == -2

    # line_spacing is a layout request input (RenderOp has no such field).
    assert engine.requests, "the font-size probe must have measured the text"
    assert all(request.line_spacing == 2.0 for request in engine.requests)
    assert all(request.direction is TextDirection.VERTICAL for request in engine.requests)


def test_region_persisting_only_text_color_keeps_every_other_default() -> None:
    """Old implementation leaked ``stroke_width=0.0``/``offset=0`` from the
    synthesised snapshot even when only one field was really persisted."""
    service, _engine = _service()

    prepared = _prepare(
        service, _region(TextStyle(text_color="#ABCDEF")), _typeset_defaults()
    )

    assert prepared.op is not None
    assert prepared.op.text_color == "#ABCDEF"  # persisted Region value wins
    assert prepared.op.stroke_enabled is False  # default applies
    assert prepared.op.stroke_color == "#0000FF"
    assert prepared.op.stroke_width == 4.0
    assert prepared.op.text_align == "center"
    assert prepared.op.direction is TextDirection.VERTICAL
    assert prepared.op.font_size == 24.0


def test_persisted_region_style_overrides_typeset_defaults() -> None:
    """D03 §11.4 reverse case: every domain TextStyle field the Region really
    persisted wins over the global defaults."""
    service, _engine = _service()
    persisted = TextStyle(
        font_family="Persisted Font",
        font_size=30,
        text_color="#ABCDEF",
        stroke_color="#123456",
        stroke_width=2.0,
        auto_font_size_enabled=False,
    )

    prepared = _prepare(service, _region(persisted), _typeset_defaults())

    assert prepared.op is not None
    op = prepared.op
    assert op.font_family == "Persisted Font"
    assert op.text_color == "#ABCDEF"
    assert op.stroke_enabled is True  # a persisted stroke width means enabled
    assert op.stroke_color == "#123456"
    assert op.stroke_width == 2.0
    assert op.font_size == 30.0  # manual size (auto_font_size_enabled=False)
    assert prepared.report.resolution is not None
    assert prepared.report.resolution.auto is False

    # Fields the domain snapshot cannot express always inherit the defaults.
    assert op.text_align == "center"
    assert op.direction is TextDirection.VERTICAL


def test_without_defaults_the_historical_style_is_kept() -> None:
    """``style_defaults=None`` keeps the byte-for-byte historical behaviour."""
    service, engine = _service()

    prepared = _prepare(service, _region(), None)

    assert prepared.op is not None
    op = prepared.op
    assert op.text_color == "#000000"
    assert op.stroke_enabled is True
    assert op.stroke_color == "#FFFFFF"
    assert op.stroke_width == 0.0
    assert op.text_align == "start"
    assert op.direction is TextDirection.HORIZONTAL
    assert op.font_size == 26.0  # D03 fallback size, no offset
    assert all(request.line_spacing == 1.0 for request in engine.requests)
