"""CORE-PIPELINE-FIX-1 AC1: the color step runs on the real Pillow analyzer.

The pre-fix assembly wired ``_StubStyleAnalyzer`` (only ``analyze_pixel_styles``)
while ``SourceStyleService.extract`` calls ``analyzer.analyze(...)``, so every
color unit died with ``AttributeError`` → ``PROVIDER_FAILED``. These tests pin
both halves of the fix:

* the wired analyzer is the real :class:`PillowSourceStyleAnalyzer` and the color
  handler returns a style for a decodable crop;
* a genuinely missing analyzer still fails **typed** (``PROVIDER_NOT_CONFIGURED``),
  never with an ``AttributeError``-shaped crash.
"""

from __future__ import annotations

import io
from types import SimpleNamespace

import pytest
from application.translation.color.service import SourceStyleService
from domain.regions.entities import BBox, RegionGeometry
from domain.tasks.models import PlanDecision, PlanUnit, StageState
from infrastructure.providers.handlers import (
    HandlerDependencies,
    ProductionHandlers,
    STEP_COLOR,
)
from infrastructure.providers.registry import ProviderRegistry
from infrastructure.rendering.pillow_source_style import PillowSourceStyleAnalyzer

PAGE_ID = "page-1"
REGION_ID = "region-1"


def _page_png() -> bytes:
    """White page with three dark horizontal bands inside the region box."""
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (60, 40), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for top in (6, 16, 26):
        draw.rectangle((4, top, 55, top + 6), fill=(16, 16, 16))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


class _FakeRegions:
    def get_region(self, region_id: str):
        if region_id != REGION_ID:
            return None
        return SimpleNamespace(
            region_id=REGION_ID,
            deleted=False,
            geometry=RegionGeometry(bbox=BBox(2, 4, 40, 32)),
            region_type="speech",
        )


class _FakeImages:
    def page_png(self, page_id: str) -> bytes:
        assert page_id == PAGE_ID
        return _page_png()


def _unit() -> PlanUnit:
    return PlanUnit(
        unit_id=f"unit:{REGION_ID}:{STEP_COLOR}",
        task_id="task-1",
        target_id=REGION_ID,
        page_id=PAGE_ID,
        region_id=REGION_ID,
        step_type=STEP_COLOR,
        decision=PlanDecision.RUN,
    )


def _handlers(*, source_styles) -> ProductionHandlers:
    return ProductionHandlers(
        HandlerDependencies(
            registry=ProviderRegistry(),
            regions=_FakeRegions(),
            region_writer=None,  # unused by the color step
            artifacts=None,  # unused by the color step
            images=_FakeImages(),
            geometry=None,  # unused by the color step
            source_styles=source_styles,
        )
    )


def test_color_step_succeeds_with_the_pillow_analyzer():
    """AC1: a wired Pillow analyzer produces a SourceStyle (was: AttributeError)."""
    handlers = _handlers(
        source_styles=SourceStyleService(PillowSourceStyleAnalyzer())
    )

    result = handlers.as_mapping()[STEP_COLOR](None, _unit(), None)

    style = result.outputs["source_style"]
    assert style["text_color"] is not None
    assert style["detected_source_font_size"] is not None
    assert 0.0 <= style["source_font_size_confidence"] <= 1.0
    assert result.outputs["needs_fallback"] in (True, False)
    assert result.outputs["provenance"]["step"] == STEP_COLOR
    assert result.outputs["provenance"]["ai_invoked"] is False
    # A judgement-only step never moves a revision pointer.
    assert result.revision_updates == {}
    assert result.next_stage_states == {STEP_COLOR: StageState.COMPLETED}


def test_color_step_without_analyzer_fails_typed():
    """AC1: a missing analyzer stays a typed capability gap (not a crash)."""
    from application.translation.pipeline.executor import StepExecutionError

    handlers = _handlers(source_styles=None)

    with pytest.raises(StepExecutionError) as excinfo:
        handlers.as_mapping()[STEP_COLOR](None, _unit(), None)

    assert excinfo.value.code == "PROVIDER_NOT_CONFIGURED"
    assert "source style analyzer" in excinfo.value.detail


def test_color_step_keeps_provider_errors_typed():
    """AC1: a decoder failure inside the analyzer is still a typed step error."""
    from application.translation.pipeline.executor import StepExecutionError

    class _BrokenAnalyzer:
        def analyze(self, original_png, box):  # noqa: ANN001, ANN201
            raise ValueError("original image could not be decoded")

    handlers = _handlers(
        source_styles=SourceStyleService(_BrokenAnalyzer())
    )

    with pytest.raises(StepExecutionError) as excinfo:
        handlers.as_mapping()[STEP_COLOR](None, _unit(), None)

    # ProviderError wrapping keeps a diagnosable code instead of a bare ValueError.
    assert excinfo.value.code == "PROVIDER_FAILED"
    assert "source style analysis failed" in excinfo.value.detail
