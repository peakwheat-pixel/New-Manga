"""FEA-09 password short-lived secret references (C-16 §3).

The Host writes ``"NMSSR1\\0" + DPAPI-CurrentUser(password)`` to
``<DataRoot>/host/source-secrets/<token>.bin`` before dispatching an import
that needs a password. The Core reads it exactly once: validate the magic,
unprotect via ``CryptUnprotectData`` (``CRYPTPROTECT_UI_FORBIDDEN``), then
delete the file (zero-filled) whether or not decryption succeeded. The
plaintext password never leaves local variables — never task state,
snapshots, receipts, exceptions or logs.
"""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import sys

from application.importing.referenced.errors import SourceImportError

MAGIC = b"NMSSR1\x00"

_CRYPTPROTECT_UI_FORBIDDEN = 0x1


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_char)),
    ]


_kernel32 = None
_crypt32 = None


def _load_dlls():
    global _kernel32, _crypt32
    if _crypt32 is None:
        _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        _crypt32 = ctypes.WinDLL("crypt32", use_last_error=True)
        _crypt32.CryptUnprotectData.argtypes = [
            ctypes.POINTER(_DATA_BLOB),
            ctypes.POINTER(ctypes.c_wchar_p),
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DATA_BLOB),
        ]
        _crypt32.CryptUnprotectData.restype = wintypes.BOOL
        _kernel32.LocalFree.argtypes = [wintypes.HLOCAL]
        _kernel32.LocalFree.restype = wintypes.HLOCAL
    return _kernel32, _crypt32


def _blob(data: bytes) -> tuple[_DATA_BLOB, ctypes.Array]:
    buffer = ctypes.create_string_buffer(data, len(data))
    blob = _DATA_BLOB()
    blob.cbData = len(data)
    blob.pbData = ctypes.cast(buffer, ctypes.POINTER(ctypes.c_char))
    return blob, buffer  # keep the backing buffer alive


def _unprotect(ciphertext: bytes) -> bytes:
    kernel32, crypt32 = _load_dlls()
    in_blob, in_keepalive = _blob(ciphertext)
    out_blob = _DATA_BLOB()
    ok = crypt32.CryptUnprotectData(
        ctypes.byref(in_blob), None, None, None, None,
        _CRYPTPROTECT_UI_FORBIDDEN, ctypes.byref(out_blob),
    )
    if not ok:
        raise SourceImportError(
            "SOURCE_PASSWORD_INVALID", "password secret could not be decrypted"
        )
    try:
        return ctypes.string_at(out_blob.pbData, out_blob.cbData)
    finally:
        kernel32.LocalFree(out_blob.pbData)
        del in_keepalive


def _zero_fill_delete(path: Path) -> None:
    """Overwrite the secret file with zeros, then delete it (C-16 §3)."""
    try:
        size = path.stat().st_size
        with open(path, "r+b") as handle:
            handle.write(b"\x00" * size)
            handle.flush()
            os.fsync(handle.fileno())
        path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        # Deleting must be best-effort on the failure path too; never raise
        # past the password handling.
        try:
            path.unlink()
        except OSError:
            pass


def read_secret(secret_ref: object) -> bytes:
    """Read + unprotect + destroy one secret reference.

    ``secret_ref`` is the C-16 shape ``{"token","path","expires_at"}``;
    only ``path`` is consumed here (the Host owns the TTL). Raises
    ``SOURCE_PASSWORD_REQUIRED`` for malformed refs and
    ``SOURCE_PASSWORD_INVALID`` when the payload is not decryptable.
    """
    if (
        not isinstance(secret_ref, dict)
        or set(secret_ref) - {"token", "path", "expires_at"}
        or not isinstance(secret_ref.get("path"), str)
        or not secret_ref["path"]
    ):
        raise SourceImportError(
            "SOURCE_PASSWORD_REQUIRED", "password secret reference is malformed"
        )
    path = Path(secret_ref["path"])
    if not path.is_absolute():
        raise SourceImportError(
            "SOURCE_PASSWORD_REQUIRED", "password secret reference is malformed"
        )
    try:
        payload = path.read_bytes()
    except FileNotFoundError as error:
        raise SourceImportError(
            "SOURCE_PASSWORD_REQUIRED", "password secret is no longer available"
        ) from error
    except OSError as error:
        raise SourceImportError(
            "SOURCE_PASSWORD_REQUIRED", "password secret is unreadable"
        ) from error
    try:
        if not payload.startswith(MAGIC) or len(payload) <= len(MAGIC):
            raise SourceImportError(
                "SOURCE_PASSWORD_INVALID", "password secret payload is invalid"
            )
        if sys.platform != "win32":
            raise SourceImportError(
                "SOURCE_PASSWORD_INVALID",
                "password secrets require the Windows DPAPI provider",
            )
        password = _unprotect(payload[len(MAGIC):])
        if not password:
            raise SourceImportError(
                "SOURCE_PASSWORD_INVALID", "password secret is empty"
            )
        return password
    finally:
        _zero_fill_delete(path)
