"""Small real-image checks for the headless Pillow render adapters."""

from __future__ import annotations

import io

from PIL import Image, ImageChops

from infrastructure.rendering.pillow_rendering import (
    PillowFontCatalog,
    PillowImageCompositor,
    PillowTextLayoutEngine,
    decode_nmfr_frame,
)
from ports.rendering.direction import TextDirection
from ports.rendering.ports import LayoutRequest, RenderOp
from ports.inpaint.ports import ImageFrame
from infrastructure.providers.step_writes import artifact_payload_from_frame


def _layout(text, *, width=100, height=100, direction=TextDirection.HORIZONTAL, stroke=0):
    catalog = PillowFontCatalog()
    return PillowTextLayoutEngine(catalog).layout(
        LayoutRequest(
            text=text,
            font_family="Arial",
            font_size=18,
            direction=direction,
            box_width=width,
            box_height=height,
            stroke_width=stroke,
            line_spacing=1.0,
            text_align="center",
        )
    )


def test_pillow_layout_handles_explicit_lines_wrap_vertical_and_fit():
    explicit = _layout("ONE\nTWO", width=120, height=80)
    assert len(explicit.items) == 2
    assert [item.text for item in explicit.items] == ["ONE", "TWO"]
    assert explicit.fits

    wrapped = _layout("ONE TWO THREE FOUR", width=65, height=120, stroke=2)
    assert len(wrapped.items) > 1
    assert all(item.text for item in wrapped.items)
    assert wrapped.fits

    vertical = _layout("縦書", width=80, height=35, direction=TextDirection.VERTICAL)
    assert all(item.per_char for item in vertical.items)
    assert len(vertical.items) >= 2
    assert not _layout("TOO TALL", width=36, height=12, stroke=3).fits


def test_pillow_compositor_draws_centered_stroked_text_into_real_png():
    catalog = PillowFontCatalog()
    layout = PillowTextLayoutEngine(catalog).layout(
        LayoutRequest(
            text="A\nB",
            font_family="Arial",
            font_size=24,
            direction=TextDirection.HORIZONTAL,
            box_width=100,
            box_height=70,
            stroke_width=1,
            text_align="center",
        )
    )
    op = RenderOp(
        items=layout.items,
        region_x=20,
        region_y=10,
        region_width=100,
        region_height=70,
        font_family=layout.resolved_family,
        font_size=24,
        text_color="#111111",
        stroke_enabled=True,
        stroke_color="#ff0000",
        stroke_width=1,
        direction=TextDirection.HORIZONTAL,
        text_align="center",
    )
    output = PillowImageCompositor(catalog).compose_page(
        _white_png(),
        [op],
    )
    with Image.open(io.BytesIO(output)) as image:
        assert ImageChops.difference(
            image.convert("RGB"), Image.new("RGB", image.size, "white")
        ).getbbox()
        red_pixels = sum(
            1
            for red, green, blue, _alpha in image.getdata()
            if red > 180 and green < 80 and blue < 80
        )
        assert red_pixels > 0


def test_nmfr_decoder_preserves_rgb32_channel_order_and_rejects_invalid_frames():
    frame = ImageFrame(1, 1, "rgb32", b"\x20\x40\xf0\xff")
    payload, _, _, _ = artifact_payload_from_frame(frame)
    decoded = decode_nmfr_frame("clean/frame.bin", payload)
    with Image.open(io.BytesIO(decoded)) as image:
        assert image.convert("RGBA").getpixel((0, 0)) == (240, 64, 32, 255)

    malformed = b"NMFR" + (2).to_bytes(4, "big") + b"{}" + b"short"
    try:
        decode_nmfr_frame("clean/frame.bin", malformed)
    except (KeyError, ValueError):
        pass
    else:
        raise AssertionError("truncated NMFR frame must fail closed")


def _white_png() -> bytes:
    image = Image.new("RGBA", (160, 100), "white")
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()
