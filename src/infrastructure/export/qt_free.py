"""Qt-free PNG and PDF encoders for the Core export wire."""

from __future__ import annotations

import io
import struct
import zlib
from pathlib import Path

from PIL import Image, ImageFont


def encode_png(payload: bytes) -> bytes:
    with Image.open(io.BytesIO(payload)) as image:
        image.load()
        if image.mode not in ("RGB", "RGBA", "L", "LA", "I;16"):
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        output = io.BytesIO()
        options = {key: image.info[key] for key in ("icc_profile", "dpi") if key in image.info}
        image.save(output, format="PNG", **options)
        return output.getvalue()


class QtFreePdfComposer:
    def compose(self, images) -> bytes:
        return _compose_pdf(images, None)

    def compose_searchable(self, images, regions_by_page) -> bytes:
        return _compose_pdf(images, regions_by_page)


def _compose_pdf(images, regions_by_page):
    decoded = []
    strings = []
    for index, payload in enumerate(images):
        with Image.open(io.BytesIO(payload)) as image:
            image.load()
            rgba = image.convert("RGBA")
            decoded.append((rgba.width, rgba.height, rgba.tobytes(), image.info.get("icc_profile")))
        regions = regions_by_page[index] if regions_by_page is not None else ()
        strings.append(tuple(_region_lines(item) for item in regions))

    font = _embedded_font(" ".join(text for page in strings for pair in page for text in pair)) if regions_by_page is not None else None
    objects: list[bytes | None] = [None]

    def add(data: bytes) -> int:
        objects.append(data)
        return len(objects) - 1

    catalog_id, pages_id = add(b""), add(b"")
    font_refs = None
    cid_by_char = {}
    if font is not None:
        font_bytes, glyphs, widths, bbox, ascent, descent, chars = font
        cid_by_char = {char: index for index, char in enumerate(chars, start=1)}
        font_file = add(_stream(b"/Length1 " + str(len(font_bytes)).encode(), zlib.compress(font_bytes)))
        descriptor = add(
            f"<< /Type /FontDescriptor /FontName /P16ExportFont /Flags 32 /FontBBox [{bbox[0]} {bbox[1]} {bbox[2]} {bbox[3]}] /ItalicAngle 0 /Ascent {ascent} /Descent {descent} /CapHeight {ascent} /StemV 80 /FontFile2 {font_file} 0 R >>".encode()
        )
        cidmap = b"\0\0" + b"".join(struct.pack(">H", glyph) for glyph in glyphs)
        cidmap_id = add(_stream(b"", zlib.compress(cidmap)))
        to_unicode = add(_stream(b"", zlib.compress(_unicode_cmap(chars).encode("ascii"))))
        widths_text = " ".join(str(value) for value in widths)
        cidfont = add(
            f"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /P16ExportFont /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> /FontDescriptor {descriptor} 0 R /CIDToGIDMap {cidmap_id} 0 R /DW 1000 /W [1 [{widths_text}]] >>".encode()
        )
        type0 = add(
            f"<< /Type /Font /Subtype /Type0 /BaseFont /P16ExportFont /Encoding /Identity-H /DescendantFonts [{cidfont} 0 R] /ToUnicode {to_unicode} 0 R >>".encode()
        )
        font_refs = type0

    page_ids = []
    for index, (width, height, rgba, icc_profile) in enumerate(decoded):
        rgb = bytearray(width * height * 3)
        alpha = bytearray(width * height)
        for pixel in range(width * height):
            r, g, b, a = rgba[pixel * 4:pixel * 4 + 4]
            rgb[pixel * 3:pixel * 3 + 3] = bytes((r, g, b))
            alpha[pixel] = a
        mask_id = add(_stream(b"/Type /XObject /Subtype /Image /Width " + str(width).encode() + b" /Height " + str(height).encode() + b" /ColorSpace /DeviceGray /BitsPerComponent 8", zlib.compress(bytes(alpha))))
        image_id = add(_stream(b"/Type /XObject /Subtype /Image /Width " + str(width).encode() + b" /Height " + str(height).encode() + b" /ColorSpace /DeviceRGB /BitsPerComponent 8 /SMask " + str(mask_id).encode() + b" 0 R", zlib.compress(bytes(rgb))))
        content = [f"q {width} 0 0 {height} 0 0 cm /Im0 Do Q\n"]
        if font_refs is not None:
            for region_index, region in enumerate(strings[index]):
                region_obj = (regions_by_page[index] or ())[region_index]
                bbox_data = region_obj.get("geometry", {}).get("bbox", [0, 0, width, height])
                if isinstance(bbox_data, dict):
                    x, y = float(bbox_data.get("x", 0)), float(bbox_data.get("y", 0))
                elif isinstance(bbox_data, (list, tuple)) and len(bbox_data) == 4:
                    x, y = float(bbox_data[0]), float(bbox_data[1])
                else:
                    x, y = 0.0, 0.0
                for line_no, text in enumerate(region):
                    encoded = _cid_text(text, cid_by_char)
                    if encoded:
                        content.append(f"BT /F0 10 Tf 3 Tr 1 0 0 1 {x:g} {max(0, height-y-line_no*10):g} Tm <{encoded}> Tj ET\n")
        # PDF-STREAM-FIX-1: _stream's contract is "you pass compressed data, I
        # declare /Filter /FlateDecode". Every other call site passes
        # zlib.compress(...); this one used to pass plain ASCII, so the content
        # stream declared a filter its bytes did not have. Readers could not
        # inflate it, skipped the stream, and never ran the "q ... /Im0 Do Q"
        # that paints the page - every exported PDF rendered blank while
        # page_count, rect sizes and get_images() all reported correctly.
        content_id = add(
            _stream(b"", zlib.compress("".join(content).encode("ascii")))
        )
        font_resource = f" /Font << /F0 {font_refs} 0 R >>" if font_refs is not None else ""
        page_id = add(
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {width} {height}] /Resources << /XObject << /Im0 {image_id} 0 R >>{font_resource} >> /Contents {content_id} 0 R >>".encode()
        )
        page_ids.append(page_id)
    objects[catalog_id] = f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode()
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects[pages_id] = f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode()
    return _pdf_file(objects)


def _region_lines(region: dict) -> tuple[str, ...]:
    return tuple(text for text in (str(region.get("ocr_text", "")), str(region.get("translated_text", ""))) if text)


def _embedded_font(text: str):
    font_dir = Path(__import__("os").environ.get("WINDIR", r"C:\Windows")) / "Fonts"
    # SEARCHABLE-PDF-CJK-1: msyh.ttc carries CJK ideographs and kana but no
    # Hangul, so a Korean page raised ValueError and Korean comics could not
    # produce a searchable PDF at all. malgun.ttf is the Windows Korean UI font:
    # measured cmap coverage ja+ko (no zh), fsType 0x0008 Editable, subsetting
    # permitted. Order below only decides which font wins when several cover the
    # text - the predicate is "does this candidate cover every character".
    candidates = [
        font_dir / "msyh.ttc",
        font_dir / "malgun.ttf",
        font_dir / "malgunbd.ttf",
        font_dir / "arial.ttf",
    ]
    for path in candidates:
        if not path.is_file():
            continue
        raw, tables, cmap = _load_ttf(path)
        if all(ord(char) in cmap for char in text if not char.isspace()):
            units = struct.unpack_from(">H", tables[b"head"], 18)[0]
            bbox = struct.unpack_from(">hhhh", tables[b"head"], 36)
            ascent, descent = struct.unpack_from(">hh", tables[b"hhea"], 4)
            font = ImageFont.truetype(str(path), 1000, index=0)
            chars = list(dict.fromkeys(text))
            glyphs = [cmap[ord(char)] for char in chars]
            widths = [round(font.getlength(char)) for char in chars]
            return raw, glyphs, widths, bbox, round(ascent * 1000 / units), round(descent * 1000 / units), chars
    raise ValueError("no installed embeddable font covers searchable PDF text")


def _load_ttf(path: Path):
    raw = path.read_bytes()
    if raw[:4] == b"ttcf":
        face_offset = struct.unpack_from(">I", raw, 12)[0]
        raw, tables = _extract_ttc_face(raw, face_offset)
    else:
        tables = _sfnt_tables(raw, 0, use_absolute=False)
    cmap_table = tables[b"cmap"]
    cmap = _parse_cmap(cmap_table)
    return raw, tables, cmap


def _sfnt_tables(raw: bytes, offset: int, *, use_absolute: bool) -> dict[bytes, bytes]:
    count = struct.unpack_from(">H", raw, offset + 4)[0]
    tables = {}
    for index in range(count):
        pos = offset + 12 + index * 16
        tag, _, table_offset, length = struct.unpack_from(">4sIII", raw, pos)
        tables[tag] = raw[table_offset:table_offset + length] if use_absolute else raw[offset + table_offset:offset + table_offset + length]
    return tables


def _extract_ttc_face(raw: bytes, face_offset: int):
    count = struct.unpack_from(">H", raw, face_offset + 4)[0]
    entries = []
    for index in range(count):
        tag, checksum, offset, length = struct.unpack_from(">4sIII", raw, face_offset + 12 + index * 16)
        entries.append((tag, checksum, raw[offset:offset + length]))
    num = len(entries)
    power = 1 << (num.bit_length() - 1)
    out = bytearray(struct.pack(">IHHHH", struct.unpack_from(">I", raw, face_offset)[0], num, power * 16, power.bit_length() - 1, num * 16 - power * 16))
    directory_at = len(out)
    out.extend(b"\0" * (num * 16))
    records = []
    for tag, checksum, data in entries:
        while len(out) % 4:
            out.append(0)
        offset = len(out)
        out.extend(data)
        out.extend(b"\0" * ((4 - len(out) % 4) % 4))
        records.append((tag, checksum, offset, len(data)))
    for index, record in enumerate(records):
        struct.pack_into(">4sIII", out, directory_at + index * 16, *record)
    head = next(offset for tag, _, offset, _ in records if tag == b"head")
    struct.pack_into(">I", out, head + 8, 0)
    adjustment = (0xB1B0AFBA - sum(struct.unpack(f">{len(out)//4}I", out[:len(out)//4*4])) % 0x100000000) % 0x100000000
    struct.pack_into(">I", out, head + 8, adjustment)
    return bytes(out), {tag: data for tag, _, data in entries}


def _parse_cmap(table: bytes) -> dict[int, int]:
    count = struct.unpack_from(">H", table, 2)[0]
    subtables = []
    for index in range(count):
        platform, encoding, offset = struct.unpack_from(">HHI", table, 4 + index * 8)
        fmt = struct.unpack_from(">H", table, offset)[0]
        subtables.append((platform, encoding, fmt, offset))
    for platform, encoding, fmt, offset in subtables:
        if fmt == 12 and (platform == 3 or platform == 0):
            length, _, groups = struct.unpack_from(">III", table, offset + 4)
            result = {}
            for index in range(groups):
                start, end, glyph = struct.unpack_from(">III", table, offset + 16 + index * 12)
                for code in range(start, end + 1):
                    result[code] = glyph + code - start
            return result
    for platform, encoding, fmt, offset in subtables:
        if fmt != 4 or platform not in (0, 3):
            continue
        seg_count = struct.unpack_from(">H", table, offset + 6)[0] // 2
        pos = offset + 14
        end_codes = struct.unpack_from(f">{seg_count}H", table, pos)
        pos += seg_count * 2 + 2
        starts = struct.unpack_from(f">{seg_count}H", table, pos)
        pos += seg_count * 2
        deltas = struct.unpack_from(f">{seg_count}h", table, pos)
        pos += seg_count * 2
        range_pos = pos
        ranges = struct.unpack_from(f">{seg_count}H", table, pos)
        result = {}
        for i, (start, end, delta, ro) in enumerate(zip(starts, end_codes, deltas, ranges)):
            for code in range(start, min(end, 0xFFFF) + 1):
                if ro == 0:
                    glyph = (code + delta) & 0xFFFF
                else:
                    glyph_at = range_pos + i * 2 + ro + (code - start) * 2
                    glyph = struct.unpack_from(">H", table, glyph_at)[0]
                    if glyph:
                        glyph = (glyph + delta) & 0xFFFF
                if glyph:
                    result[code] = glyph
        return result
    return {}


def _cid_text(text: str, cid_by_char: dict[str, int]) -> str:
    return "".join(f"{cid_by_char[char]:04X}" for char in text if char in cid_by_char)


def _unicode_cmap(chars: list[str]) -> str:
    lines = ["/CIDInit /ProcSet findresource begin", "12 dict begin", "begincmap", "/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def", "/CMapName /P16Unicode def", "/CMapType 2 def", "1 begincodespacerange", "<0000> <FFFF>", "endcodespacerange"]
    for start in range(0, len(chars), 100):
        part = chars[start:start + 100]
        lines.append(f"{len(part)} beginbfchar")
        for index, char in enumerate(part, start=start + 1):
            encoded = char.encode("utf-16-be").hex().upper()
            lines.append(f"<{index:04X}> <{encoded}>")
        lines.append("endbfchar")
    lines.extend(["endcmap", "CMapName currentdict /CMap defineresource pop", "end", "end"])
    return "\n".join(lines)


def _stream(dictionary: bytes, payload: bytes) -> bytes:
    prefix = b"<< " + dictionary + b" /Filter /FlateDecode /Length " + str(len(payload)).encode() + b" >>\nstream\n"
    return prefix + payload + b"\nendstream"


def _pdf_file(objects: list[bytes | None]) -> bytes:
    out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for index, obj in enumerate(objects[1:], start=1):
        if obj is None:
            raise ValueError("incomplete PDF object table")
        offsets.append(len(out))
        out.extend(f"{index} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref = len(out)
    out.extend(f"xref\n0 {len(objects)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        out.extend(f"{offset:010d} 00000 n \n".encode())
    out.extend(f"trailer\n<< /Size {len(objects)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode())
    return bytes(out)


