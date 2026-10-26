"""Windows Credential Manager adapter (D07 §69, AC-SEC-003).

Secrets are stored as generic credentials (``CRED_TYPE_GENERIC``) via
``advapi32!CredReadW/CredWriteW/CredDeleteW`` — the OS-protected vault
TASK-004's packaging experiment validated on this platform. The
database keeps only the ``credential_ref`` target name.

The adapter never writes secrets to disk itself: persistence and
encryption belong to the OS vault. ``SecretValue`` redaction keeps
accidental ``repr`` leakage out of logs (AC-SEC-002).

Note: ``CredWriteW`` cannot atomically distinguish create vs overwrite,
so ``store_credential`` checks existence first (``has_credential``);
the pair is not atomic against concurrent writers, which is acceptable
for single-instance desktop use (D07 §79 single-user model).
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import sys

from ports.providers.credentials import SecretValue

CRED_TYPE_GENERIC = 1
CRED_PERSIST_LOCAL_MACHINE = 2
ERROR_NOT_FOUND = 1168
ERROR_ALREADY_EXISTS = 1316


class CredentialNotFoundError(KeyError):
    """Raised when a credential ref does not exist in the vault."""


class WindowsCredentialError(RuntimeError):
    """Vault call failed with an unexpected Win32 error code."""


class _CREDENTIALW(ctypes.Structure):
    _fields_ = [
        ("Flags", wt.DWORD),
        ("Type", wt.DWORD),
        ("TargetName", wt.LPWSTR),
        ("Comment", wt.LPWSTR),
        ("LastWritten", wt.FILETIME),
        ("CredentialBlobSize", wt.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
        ("Persist", wt.DWORD),
        ("AttributeCount", wt.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wt.LPWSTR),
        ("UserName", wt.LPWSTR),
    ]


def _advapi32():
    return ctypes.WinDLL("advapi32", use_last_error=True)


def _raise_for_error(proc, what: str) -> None:
    code = ctypes.get_last_error()
    if code == ERROR_NOT_FOUND:
        raise CredentialNotFoundError(what)
    raise WindowsCredentialError(f"{what} failed with Win32 error {code}")


class WindowsCredentialStore:
    """``CredentialStore`` backed by Windows Credential Manager."""

    def __init__(self) -> None:
        if sys.platform != "win32":  # pragma: no cover - platform guard
            raise WindowsCredentialError(
                "WindowsCredentialStore requires win32; use another vault adapter"
            )
        self._dll = _advapi32()

    # -- helpers -------------------------------------------------------

    def _read_raw(self, ref: str) -> bytes:
        cred_ptr = ctypes.POINTER(_CREDENTIALW)()
        ok = self._dll.CredReadW(
            ctypes.c_wchar_p(ref), CRED_TYPE_GENERIC, 0, ctypes.byref(cred_ptr)
        )
        if not ok:
            _raise_for_error(self._dll, f"CredReadW({ref})")
        try:
            cred = cred_ptr.contents
            size = cred.CredentialBlobSize
            blob = ctypes.string_at(cred.CredentialBlob, size) if size else b""
            return blob
        finally:
            self._dll.CredFree(cred_ptr)

    def _write(self, ref: str, secret: SecretValue, *, overwrite: bool) -> None:
        blob = secret.reveal().encode("utf-16-le")  # vault convention for strings
        buf = (ctypes.c_byte * len(blob)).from_buffer_copy(blob) if blob else None
        cred = _CREDENTIALW()
        cred.Flags = 0
        cred.Type = CRED_TYPE_GENERIC
        cred.TargetName = ctypes.c_wchar_p(ref)
        cred.Comment = None
        cred.CredentialBlobSize = len(blob)
        cred.CredentialBlob = ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)) if buf else None
        cred.Persist = CRED_PERSIST_LOCAL_MACHINE
        cred.AttributeCount = 0
        cred.Attributes = None
        cred.TargetAlias = None
        cred.UserName = None
        ok = self._dll.CredWriteW(ctypes.byref(cred), 0)
        if not ok:
            code = ctypes.get_last_error()
            if not overwrite and code == ERROR_ALREADY_EXISTS:
                raise KeyError(f"credential already exists: {ref}")
            raise WindowsCredentialError(f"CredWriteW({ref}) failed with Win32 error {code}")

    # -- CredentialStore ----------------------------------------------

    def store_credential(self, ref: str, secret: SecretValue) -> None:
        if self.has_credential(ref):
            raise KeyError(f"credential already exists: {ref}")
        self._write(ref, secret, overwrite=False)

    def resolve_credential(self, ref: str) -> SecretValue:
        try:
            raw = self._read_raw(ref)
        except CredentialNotFoundError:
            raise
        except WindowsCredentialError:
            raise
        return SecretValue(raw.decode("utf-16-le", errors="replace"))

    def update_credential(self, ref: str, secret: SecretValue) -> None:
        if not self.has_credential(ref):
            raise CredentialNotFoundError(ref)
        self._write(ref, secret, overwrite=True)

    def delete_credential(self, ref: str) -> None:
        ok = self._dll.CredDeleteW(
            ctypes.c_wchar_p(ref), CRED_TYPE_GENERIC, 0
        )
        if not ok:
            _raise_for_error(self._dll, f"CredDeleteW({ref})")

    def has_credential(self, ref: str) -> bool:
        cred_ptr = ctypes.POINTER(_CREDENTIALW)()
        ok = self._dll.CredReadW(
            ctypes.c_wchar_p(ref), CRED_TYPE_GENERIC, 0, ctypes.byref(cred_ptr)
        )
        if ok:
            self._dll.CredFree(cred_ptr)
            return True
        if ctypes.get_last_error() == ERROR_NOT_FOUND:
            return False
        _raise_for_error(self._dll, f"CredReadW({ref})")
        return False  # unreachable
