"""Streaming PNG band reader for oversized webtoon pages (TASK-042).

Reads a horizontal band of scanlines out of a PNG without ever
materialising the whole image — the fix for the TASK-020 finding that the
Qt PNG handler allocates the full rgb32 buffer before clipping and therefore
fails above ~300 MB (1600x200000 = 1.28 GB).

Format coverage (deliberately narrow, per TASK-042 AC ③ — everything else
fails **typed**, never silently):

- 8-bit depth, colour types 0 (grey) / 2 (RGB) / 4 (grey+alpha) / 6 (RGBA);
- non-interlaced only (Adam7 → typed reject);
- palette (colour type 3, or a PLTE chunk) → typed reject; non-PNG input →
  typed reject; truncated data → typed reject;
- all five scanline filters (None/Sub/Up/Average/Paeth) are honoured —
  unfiltering is sequential by design (Up/Left/Paeth depend on the previous
  reconstructed row), so the reader is a **one-way cursor**: rows are
  produced in order and ``rewind()`` restarts from row 0.

Band reads never store more than one scanline pair plus the requested band,
so peak memory is bounded by ``band_height x stride`` + two rows — measured
in the TASK-042 tests, never asserted as a budget.
"""

from __future__ import annotations

import struct
import zlib
from itertools import accumulate

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

_IHDR = b"IHDR"
_IDAT = b"IDAT"
_IEND = b"IEND"
_PLTE = b"PLTE"

_CHANNELS = {0: 1, 2: 3, 4: 2, 6: 4}


class StreamingPngError(ValueError):
    """Typed, diagnosable failure for unsupported PNG variants or damage.

    ``reason`` is a stable code: ``NOT_PNG`` / ``INVALID_PNG`` /
    ``TRUNCATED`` / ``INTERLACED`` / ``UNSUPPORTED_BIT_DEPTH`` /
    ``PALETTED`` / ``REWIND_REQUIRED`` / ``OUT_OF_RANGE``.
    """

    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(f"{reason}: {detail}" if detail else reason)
        self.reason = reason
        self.detail = detail


class StreamingPngReader:
    """One-way-cursor band reader over PNG bytes."""

    def __init__(self, data: bytes) -> None:
        self._data = data
        self._parse_headers()
        self.rewind()

    # ------------------------------------------------------------------
    # header parsing (signature + chunk walk)
    # ------------------------------------------------------------------

    def _parse_headers(self) -> None:
        data = self._data
        if data[:8] != PNG_SIGNATURE:
            raise StreamingPngError("NOT_PNG", "missing PNG signature")
        offset = 8
        self._idat_spans: list[tuple[int, int]] = []
        saw_ihdr = False
        while offset + 8 <= len(data):
            length = struct.unpack_from(">I", data, offset)[0]
            chunk_type = data[offset + 4 : offset + 8]
            body_start = offset + 8
            body_end = body_start + length
            if body_end + 4 > len(data):
                raise StreamingPngError("TRUNCATED", "chunk extends past end of data")
            if chunk_type == _IHDR:
                if saw_ihdr or length != 13:
                    raise StreamingPngError("INVALID_PNG", "bad IHDR")
                (
                    self.width,
                    self.height,
                    bit_depth,
                    colour_type,
                    compression,
                    filter_method,
                    interlace,
                ) = struct.unpack_from(">IIBBBBB", data, body_start)
                if compression != 0 or filter_method != 0:
                    raise StreamingPngError(
                        "INVALID_PNG", "unsupported compression/filter method"
                    )
                if interlace != 0:
                    raise StreamingPngError(
                        "INTERLACED",
                        "Adam7 interlacing is not supported by the band reader",
                    )
                if bit_depth != 8:
                    raise StreamingPngError(
                        "UNSUPPORTED_BIT_DEPTH",
                        f"bit depth {bit_depth} is not supported (8 only)",
                    )
                if colour_type == 3:
                    raise StreamingPngError(
                        "PALETTED",
                        "palette images are not supported by the band reader",
                    )
                if colour_type not in _CHANNELS:
                    raise StreamingPngError(
                        "INVALID_PNG", f"unknown colour type {colour_type}"
                    )
                self.channels = _CHANNELS[colour_type]
                self._bpp = self.channels
                saw_ihdr = True
            elif chunk_type == _PLTE:
                raise StreamingPngError(
                    "PALETTED", "PLTE chunk present (palette images unsupported)"
                )
            elif chunk_type == _IDAT:
                if not saw_ihdr:
                    raise StreamingPngError("INVALID_PNG", "IDAT before IHDR")
                self._idat_spans.append((body_start, length))
            elif chunk_type == _IEND:
                break
            offset = body_end + 4
        if not saw_ihdr:
            raise StreamingPngError("INVALID_PNG", "no IHDR")
        if not self._idat_spans:
            raise StreamingPngError("TRUNCATED", "no IDAT chunks")
        if self.width <= 0 or self.height <= 0:
            raise StreamingPngError("INVALID_PNG", "zero page dimension")
        self._stride = self.width * self._bpp
        self._row_bytes = self._stride + 1

    # ------------------------------------------------------------------
    # cursor control
    # ------------------------------------------------------------------

    @property
    def cursor_row(self) -> int:
        """Next row index the cursor will produce."""
        return self._next_row

    def rewind(self) -> None:
        """Restart sequential reading from row 0 (re-opens the zlib stream)."""
        self._decompressor = zlib.decompressobj()
        self._idat_index = 0
        self._unconsumed: bytes = b""
        self._pending = bytearray()
        self._zlib_done = False
        self._prev: bytes | None = None
        self._next_row = 0

    # ------------------------------------------------------------------
    # band reads
    # ------------------------------------------------------------------

    @property
    def bytes_per_pixel(self) -> int:
        return self._bpp

    def read_band(self, start_row: int, band_height: int) -> tuple[bytes, int, int, int]:
        """Return ``(raw_rows, width, height, channels)`` for the band
        ``[start_row, start_row + band_height)``; ``raw_rows`` is the
        concatenation of the reconstructed scanlines (``stride`` bytes each).

        The cursor only moves forward; a ``start_row`` behind it raises
        ``REWIND_REQUIRED`` (callers restart with :meth:`rewind`).
        """
        start_row = int(start_row)
        band_height = int(band_height)
        if start_row < self._next_row:
            raise StreamingPngError(
                "REWIND_REQUIRED",
                f"band starts at row {start_row}, cursor is already at {self._next_row}",
            )
        if start_row + band_height > self.height:
            band_height = self.height - start_row
        if band_height <= 0:
            raise StreamingPngError("OUT_OF_RANGE", "empty band request")
        raw = bytearray()
        while self._next_row < start_row + band_height:
            row = self._advance_one_row()
            if self._next_row > start_row:
                raw += row
        return (bytes(raw), self.width, band_height, self.channels)

    # ------------------------------------------------------------------
    # internals
    # ------------------------------------------------------------------

    def _advance_one_row(self) -> bytes:
        while len(self._pending) < self._row_bytes and not self._zlib_done:
            if not self._pump(self._row_bytes - len(self._pending)):
                break
        if len(self._pending) < self._row_bytes:
            raise StreamingPngError(
                "TRUNCATED",
                f"image data ended at row {self._next_row} of {self.height}",
            )
        filter_type = self._pending[0]
        filtered = bytes(self._pending[1 : self._row_bytes])
        del self._pending[: self._row_bytes]
        row = self._unfilter(filter_type, bytearray(filtered), self._prev)
        self._prev = row
        self._next_row += 1
        return row

    def _pump(self, wanted: int) -> bool:
        """Feed the zlib stream until ``wanted`` decompressed bytes are
        pending, the stream ends, or the IDAT chunks run out. Returns False
        when no progress is possible any more."""
        produced = 0
        while len(self._pending) < wanted and not self._zlib_done:
            if self._unconsumed:
                chunk, self._unconsumed = self._unconsumed, b""
            elif self._idat_index < len(self._idat_spans):
                start, length = self._idat_spans[self._idat_index]
                self._idat_index += 1
                chunk = self._data[start : start + length]
            else:
                self._zlib_done = True
                break
            out = self._decompressor.decompress(chunk, wanted - len(self._pending))
            self._pending += out
            produced += len(out)
            if self._decompressor.eof:
                self._zlib_done = True
            else:
                self._unconsumed = self._decompressor.unconsumed_tail
        return produced > 0

    def _unfilter(self, filter_type: int, cur: bytearray, prev: bytes | None) -> bytes:
        """Reconstruct one scanline. Sub uses a C-level prefix accumulation;
        Up is an independent per-byte modular add; Average/Paeth walk the row
        (their reconstruction depends on the just-reconstructed left byte)."""
        bpp = self._bpp
        n = len(cur)
        if filter_type == 0:
            return bytes(cur)
        if filter_type == 1:  # Sub: recon[i] = filt[i] + recon[i-bpp]
            # the row splits into `bpp` independent chains (one per channel
            # byte position); each chain is a modular prefix sum
            out = bytearray(n)
            for offset in range(bpp):
                out[offset::bpp] = accumulate(
                    cur[offset::bpp], lambda a, b: (a + b) & 0xFF
                )
            return bytes(out)
        if filter_type == 2:  # Up: recon[i] = filt[i] + recon_above[i]
            if prev is None:
                return bytes(cur)
            return bytes(
                map(lambda pair: (pair[0] + pair[1]) & 0xFF, zip(cur, prev))
            )
        if filter_type == 3:  # Average
            for i in range(n):
                left = cur[i - bpp] if i >= bpp else 0
                up = prev[i] if prev is not None else 0
                cur[i] = (cur[i] + ((left + up) >> 1)) & 0xFF
            return bytes(cur)
        if filter_type == 4:  # Paeth
            for i in range(n):
                a = cur[i - bpp] if i >= bpp else 0
                b = prev[i] if prev is not None else 0
                c = prev[i - bpp] if (prev is not None and i >= bpp) else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                cur[i] = (cur[i] + pred) & 0xFF
            return bytes(cur)
        raise StreamingPngError("INVALID_PNG", f"unknown scanline filter {filter_type}")


__all__ = ["StreamingPngError", "StreamingPngReader"]
