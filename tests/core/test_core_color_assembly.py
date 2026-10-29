"""CORE-PIPELINE-FIX-1 AC1 (wiring half): production assembly wires the real analyzer.

``handle_color`` calls ``SourceStyleService.extract`` → ``analyzer.analyze(...)``.
Before the fix the production assembly injected ``_StubStyleAnalyzer`` (only
``analyze_pixel_styles``), so every color unit failed with ``AttributeError``
and a text-free run could never reach translate/render. This test pins the
replacement at the *assembly* seam — not just at the handler seam — so a future
refactor cannot silently swap the stub back in.
"""

from __future__ import annotations

import io

from application.translation.color.service import SourceStyleService
from bootstrap.core_service import assemble_production_core
from infrastructure.rendering.pillow_source_style import PillowSourceStyleAnalyzer


def _page_png() -> bytes:
    from PIL import Image, ImageDraw

    image = Image.new("RGB", (60, 40), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for top in (6, 16, 26):
        draw.rectangle((4, top, 55, top + 6), fill=(16, 16, 16))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_production_assembly_wires_a_working_source_style_analyzer(tmp_path):
    core = assemble_production_core(tmp_path / "data")
    try:
        service = core.render._source_styles
        assert isinstance(service, SourceStyleService)
        assert isinstance(service._analyzer, PillowSourceStyleAnalyzer)

        # the wired pair must actually answer the call the color step makes
        result = service.extract(_page_png(), (2, 4, 40, 32))
        assert result.style.text_color is not None
        assert result.style.detected_source_font_size is not None
    finally:
        core.conn.close()
