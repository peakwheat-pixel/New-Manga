"""FEA-09 test fixture generators for encrypted archives (test-only).

``make_zipcrypto_zip`` builds a real ZipCrypto-encrypted ZIP/CBZ with the
traditional PKWARE stream cipher (the only encrypted sub-format the stdlib
can decrypt — C-16 §3), and ``make_aes_zip`` builds a container whose
member advertises compression method 99 (WinZip AES) which the product must
classify as typed-unsupported without ever decrypting.

These are test tools, not product code: they exist so the fixture set has
deterministic bytes we can pin by SHA-256 in the handoff.
"""

from __future__ import annotations

import struct
import zlib

_KEY_SEED = (0x12345678, 0x23456789, 0x34567890)
_CRC_TABLE: list[int] | None = None


def _crc_table() -> list[int]:
    global _CRC_TABLE
    if _CRC_TABLE is None:
        table = []
        for i in range(256):
            c = i
            for _ in range(8):
                c = (c >> 1) ^ (0xEDB88320 if c & 1 else 0)
            table.append(c)
        _CRC_TABLE = table
    return _CRC_TABLE


def _crc32_byte(crc: int, byte: int) -> int:
    return ((_crc_table()[(crc ^ byte) & 0xFF] ^ (crc >> 8)) & 0xFFFFFFFF)


def _update_keys(keys: list[int], byte: int) -> None:
    keys[0] = _crc32_byte(keys[0], byte)
    keys[1] = (keys[1] + (keys[0] & 0xFF)) & 0xFFFFFFFF
    keys[1] = (keys[1] * 134775813 + 1) & 0xFFFFFFFF
    keys[2] = _crc32_byte(keys[2], (keys[1] >> 24) & 0xFF)


def _stream_byte(keys: list[int]) -> int:
    temp = (keys[2] | 2) & 0xFFFF
    return ((temp * (temp ^ 1)) >> 8) & 0xFF


def zipcrypt(plaintext: bytes, password: bytes, check_byte: int) -> bytes:
    """Encrypt with the ZipCrypto stream cipher (12-byte header included)."""
    keys = list(_KEY_SEED)
    for ch in password:
        _update_keys(keys, ch)
    header = bytes(range(1, 12)) + bytes([check_byte & 0xFF])  # deterministic
    out = bytearray()
    for byte in bytes(header) + plaintext:
        out.append(byte ^ _stream_byte(keys))
        _update_keys(keys, byte)
    return bytes(out)


def _dword(value: int) -> bytes:
    return struct.pack("<I", value & 0xFFFFFFFF)


def _word(value: int) -> bytes:
    return struct.pack("<H", value & 0xFFFF)


def make_zipcrypto_zip(members: list[tuple[str, bytes]], password: str) -> bytes:
    """Build a ZipCrypto ZIP (stored members, encrypted, flag bit 0 set)."""
    locals_: list[bytes] = []
    centrals: list[bytes] = []
    offset = 0
    for name, data in members:
        crc = zlib.crc32(data) & 0xFFFFFFFF
        body = zipcrypt(data, password.encode("utf-8"), (crc >> 24) & 0xFF)
        local = b"PK\x03\x04" + _word(20) + _word(0x0001) + _word(0) + _word(0) + \
            _word(0) + _dword(crc) + _dword(len(body)) + _dword(len(data)) + \
            _word(len(name)) + _word(0) + name.encode("utf-8")
        central = b"PK\x01\x02" + _word(20) + _word(20) + _word(0x0001) + _word(0) + \
            _word(0) + _word(0) + _dword(crc) + _dword(len(body)) + \
            _dword(len(data)) + _word(len(name)) + _word(0) + _word(0) + \
            _word(0) + _word(0) + _dword(0) + _dword(offset) + name.encode("utf-8")
        locals_.append(local + body)
        centrals.append(central)
        offset += len(local) + len(body)
    cd = b"".join(centrals)
    eocd = b"PK\x05\x06" + _word(0) + _word(0) + _word(len(members)) + \
        _word(len(members)) + _dword(len(cd)) + _dword(offset) + _word(0)
    return b"".join(locals_) + cd + eocd


def make_aes_zip(members: list[tuple[str, bytes]]) -> bytes:
    """Build a ZIP advertising compression method 99 (WinZip AES).

    The member payload is irrelevant — the product must refuse on the
    advertised method before any decryption attempt (C-16 §3).
    """
    locals_: list[bytes] = []
    centrals: list[bytes] = []
    offset = 0
    for name, data in members:
        crc = zlib.crc32(data) & 0xFFFFFFFF
        local = b"PK\x03\x04" + _word(51) + _word(0x0001) + _word(99) + \
            _word(0) + _word(0) + _dword(crc) + _dword(len(data) + 28) + \
            _dword(len(data)) + _word(len(name)) + _word(0) + name.encode("utf-8")
        central = b"PK\x01\x02" + _word(51) + _word(51) + _word(0x0001) + \
            _word(99) + _word(0) + _word(0) + _dword(crc) + \
            _dword(len(data) + 28) + _dword(len(data)) + _word(len(name)) + \
            _word(0) + _word(0) + _word(0) + _word(0) + _dword(0) + \
            _dword(offset) + name.encode("utf-8")
        locals_.append(local + b"\x00" * (len(data) + 28))
        centrals.append(central)
        offset += len(local) + len(data) + 28
    cd = b"".join(centrals)
    eocd = b"PK\x05\x06" + _word(0) + _word(0) + _word(len(members)) + \
        _word(len(members)) + _dword(len(cd)) + _dword(offset) + _word(0)
    return b"".join(locals_) + cd + eocd


# A minimal, valid, unencrypted single-page PDF (612x792pt / letter) used by
# the PDF scan fixtures; pypdfium2 parses it and reports one page.
MINIMAL_PDF = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << >> >>
endobj
4 0 obj
<< /Length 44 >>
stream
1 0 0 1 100 700 cm
0 0 200 100 re S
endstream
endobj
trailer
<< /Root 1 0 R /Size 5 >>
%%EOF
"""


def make_flat_pdf(page_count: int = 1, width: float = 612.0, height: float = 792.0) -> bytes:
    """Deterministic multi-page PDF (MediaBox only, no rendering needed)."""
    pages = []
    kids = " ".join(f"{3 + i * 2} 0 R" for i in range(page_count))
    out = [b"%PDF-1.4"]
    out.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    out.append(
        f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {page_count} >>\nendobj".encode()
    )
    for i in range(page_count):
        page_no = 3 + i * 2
        content_no = page_no + 1
        out.append(
            f"{page_no} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} {height}]"
            f" /Contents {content_no} 0 R /Resources << >> >>\nendobj".encode()
        )
        stream = b"0 0 1 1 re S"
        out.append(
            f"{content_no} 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode()
            + stream + b"\nendstream\nendobj"
        )
    out.append(f"trailer\n<< /Root 1 0 R /Size {3 + page_count * 2} >>\n%%EOF".encode())
    return b"\n".join(out)
