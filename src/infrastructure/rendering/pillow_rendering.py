"""Small Pillow adapters for the headless production Core renderer."""

from __future__ import annotations

import io
import os
import re
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFont

from ports.rendering.direction import TextDirection
from ports.rendering.ports import (
    DrawItem,
    FontCatalog,
    ImageCompositor,
    LayoutRequest,
    LayoutResult,
    RenderOp,
    ResolvedFont,
    TextLayoutEngine,
)

_FALLBACK_CHAIN = (
    "Source Han Sans K Bold",
    "Source Han Sans Bold",
    "Source Han Sans SC Bold",
    "Microsoft YaHei",
    "SimSun",
    "Arial",
)
_WORD_RE = re.compile(r"\S+|\s")


def _tokenize(text: str) -> list[tuple[str, bool]]:
    tokens: list[tuple[str, bool]] = []
    for chunk in _WORD_RE.findall(text):
        if chunk.strip() and chunk.isascii():
            tokens.append((chunk, bool(tokens)))
        elif not chunk.strip() and chunk.isascii():
            continue
        else:
            tokens.extend((character, False) for character in chunk)
    return tokens


class PillowFontCatalog(FontCatalog):
    """Resolve installed Windows families, with the renderer's existing fallback order."""

    def __init__(self) -> None:
        self._font_dir = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
        self._families: dict[str, Path] | None = None
        self._resolved: dict[str, ResolvedFont] = {}

    def _index(self) -> dict[str, Path]:
        if self._families is None:
            families: dict[str, Path] = {}
            if self._font_dir.is_dir():
                for path in self._font_dir.iterdir():
                    if path.suffix.lower() not in (".ttf", ".ttc", ".otf"):
                        continue
                    try:
                        family = ImageFont.truetype(str(path), 12, index=0).getname()[0]
                    except (OSError, ValueError):
                        continue
                    families.setdefault(family.casefold(), path)
            self._families = families
        return self._families

    def resolve(self, family: str) -> ResolvedFont:
        requested = family or ""
        cached = self._resolved.get(requested.casefold())
        if cached is not None:
            return cached
        families = self._index()
        if requested.casefold() in families:
            result = ResolvedFont(requested, requested, True)
        else:
            fallback = next(
                (name for name in _FALLBACK_CHAIN if name.casefold() in families),
                "Pillow Default",
            )
            result = ResolvedFont(requested, fallback, False)
        self._resolved[requested.casefold()] = result
        return result

    def load(self, family: str, size: float):
        resolved = self.resolve(family)
        path = self._index().get(resolved.resolved_family.casefold())
        if path is not None:
            return ImageFont.truetype(str(path), max(1, round(size)), index=0)
        try:
            return ImageFont.load_default(size=max(1, round(size)))
        except TypeError:  # Pillow versions before scalable built-in fonts
            return ImageFont.load_default()


class PillowTextLayoutEngine(TextLayoutEngine):
    def __init__(self, catalog: PillowFontCatalog) -> None:
        self._catalog = catalog

    def layout(self, request: LayoutRequest) -> LayoutResult:
        resolved = self._catalog.resolve(request.font_family)
        font = self._catalog.load(resolved.resolved_family, request.font_size)
        ascent, descent = font.getmetrics()
        line_height = max(1, ascent + descent)
        spacing = max(0.1, float(request.line_spacing))
        pad = max(0.0, request.stroke_width)
        usable_w = request.box_width - 2 * pad
        usable_h = request.box_height - 2 * pad
        if usable_w <= 0 or usable_h <= 0:
            return LayoutResult((), 0, 0, False, resolved.available, resolved.resolved_family)
        if request.direction is TextDirection.VERTICAL:
            items, width, height = self._vertical(
                request.text, font, ascent, line_height, usable_w, usable_h, spacing
            )
        else:
            items, width, height = self._horizontal(
                request.text, font, ascent, line_height, usable_w, spacing
            )
        return LayoutResult(
            items,
            width,
            height,
            width <= usable_w and height <= usable_h,
            resolved.available,
            resolved.resolved_family,
        )

    @staticmethod
    def _horizontal(text, font, ascent, line_height, usable_w, spacing):
        space_w = font.getlength(" ")
        lines: list[list[tuple[str, bool]]] = []
        for hard_line in text.split("\n"):
            tokens = [token for token in _tokenize(hard_line) if token[0].strip()]
            tokens = tokens or [("", False)]
            current: list[tuple[str, bool]] = []
            current_w = 0.0
            for token, space_before in tokens:
                advance = font.getlength(token)
                separator = space_w if (space_before and current) else 0.0
                if current and current_w + separator + advance > usable_w:
                    lines.append(current)
                    current, current_w = [(token, False)], advance
                else:
                    current.append((token, space_before and bool(current)))
                    current_w += separator + advance
            if current:
                lines.append(current)
        items: list[DrawItem] = []
        max_width = 0.0
        for index, words in enumerate(lines):
            line = "".join((" " if space else "") + word for word, space in words)
            max_width = max(max_width, font.getlength(line))
            items.append(DrawItem(line, 0, ascent + index * line_height * spacing))
        return tuple(items), max_width, len(lines) * line_height * spacing

    @staticmethod
    def _vertical(text, font, ascent, line_height, usable_w, usable_h, spacing):
        chars = [character for character in text if not character.isspace()] or [""]
        cell = max(1, line_height)
        column_width = max((font.getlength(char) for char in chars), default=cell)
        pitch = column_width * spacing
        per_column = max(1, int(usable_h // cell))
        columns = [chars[index:index + per_column] for index in range(0, len(chars), per_column)]
        items: list[DrawItem] = []
        for column_index, column in enumerate(columns):
            x = (len(columns) - 1 - column_index) * pitch
            for row_index, character in enumerate(column):
                items.append(DrawItem(character, x, ascent + row_index * cell, per_char=True))
        return tuple(items), len(columns) * pitch, min(len(chars), per_column) * cell


class PillowImageCompositor(ImageCompositor):
    def __init__(self, catalog: PillowFontCatalog) -> None:
        self._catalog = catalog

    def compose_page(self, base_png: bytes, ops: Sequence[RenderOp]) -> bytes:
        image = self._open(base_png)
        draw = ImageDraw.Draw(image)
        for op in ops:
            self._draw_op(draw, op)
        return self._png(image)

    def compose_region(self, base_png, clean_png, box, op):
        base = self._open(base_png)
        clean = self._open(clean_png)
        if base.size != clean.size:
            raise ValueError("base and restore image dimensions differ")
        x, y, width, height = box
        left, top = max(0, x), max(0, y)
        right, bottom = min(base.width, x + width), min(base.height, y + height)
        if right <= left or bottom <= top:
            raise ValueError("composition box is outside the page image")
        base.paste(clean.crop((left, top, right, bottom)), (left, top))
        return self.compose_page(self._png(base), (op,))

    @staticmethod
    def _open(payload: bytes) -> Image.Image:
        try:
            with Image.open(io.BytesIO(payload)) as source:
                source.load()
                return source.convert("RGBA")
        except (OSError, ValueError) as error:
            raise ValueError("image could not be decoded") from error

    @staticmethod
    def _png(image: Image.Image) -> bytes:
        output = io.BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()

    def _draw_op(self, draw: ImageDraw.ImageDraw, op: RenderOp) -> None:
        font = self._catalog.load(op.font_family, op.font_size)
        ascent, descent = font.getmetrics()
        items = op.items
        if op.direction is TextDirection.VERTICAL:
            extents_w = max((item.x for item in items), default=0) + max(
                (font.getlength(item.text) for item in items), default=0
            )
            extents_h = max((item.y for item in items), default=0)
        else:
            extents_w = max((item.x + font.getlength(item.text) for item in items), default=0)
            extents_h = max((item.y for item in items), default=0) + descent
        free_w, free_h = op.region_width - extents_w, op.region_height - extents_h
        origin_x = op.region_x + (max(0, free_w / 2) if op.text_align == "center" else 0)
        origin_y = op.region_y + max(0, free_h / 2)
        stroke_width = max(0, round(op.stroke_width)) if op.stroke_enabled else 0
        for item in items:
            draw.text(
                (origin_x + item.x, origin_y + item.y - ascent),
                item.text,
                font=font,
                fill=op.text_color,
                stroke_width=stroke_width,
                stroke_fill=op.stroke_color,
            )


def decode_nmfr_frame(relative_path: str, payload: bytes) -> bytes:
    """Decode the existing RGB32 frame container without importing Qt."""
    del relative_path
    if not payload.startswith(b"NMFR"):
        return payload
    from infrastructure.providers.step_writes import decode_frame_payload

    header, raw = decode_frame_payload(payload)
    if header.get("mode") != "rgb32":
        raise ValueError("unsupported clean frame mode")
    width, height = int(header["width"]), int(header["height"])
    if width <= 0 or height <= 0 or len(raw) != width * height * 4:
        raise ValueError("invalid clean frame dimensions")
    image = Image.frombytes("RGBA", (width, height), raw, "raw", "BGRA")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


__all__ = [
    "PillowFontCatalog",
    "PillowImageCompositor",
    "PillowTextLayoutEngine",
    "decode_nmfr_frame",
]
