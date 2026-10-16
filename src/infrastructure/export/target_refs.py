"""Core side of the one-use, host-issued export destination reference."""

from __future__ import annotations

import base64
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import hmac
import math
import os
from pathlib import Path
import re
import threading
import time


class ExportTargetRefError(Exception):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass
class _Grant:
    grant_id: str
    session_id: str
    target: Path
    format: str
    replace_existing: bool
    expires_at: float
    signing_key: bytes
    signature: str
    revoked: bool = False
    consumed: bool = False


class ResolvedExportTarget:
    """A consumed exact-file write capability; never constructed from StartExport."""

    def __init__(self, target: Path, replace_existing: bool) -> None:
        self.path = target
        self.replace_existing = replace_existing

    @contextmanager
    def hold_parent(self):
        parent = self.path.parent.resolve(strict=True)
        if not parent.is_dir() or self.path.name in ("", ".", ".."):
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        _reject_reparse_components(parent)
        handle = None
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CreateFileW.restype = wintypes.HANDLE
            kernel32.CreateFileW.argtypes = [
                wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
                wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
            ]
            kernel32.GetFinalPathNameByHandleW.restype = wintypes.DWORD
            kernel32.GetFinalPathNameByHandleW.argtypes = [
                wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
            ]
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            handle = kernel32.CreateFileW(
                str(parent), 0x80000000, 0x1 | 0x2, None, 3, 0x02000000, None
            )
            if not handle or handle == ctypes.c_void_p(-1).value:
                raise ExportTargetRefError("REF_SCOPE_DENIED")
            length = kernel32.GetFinalPathNameByHandleW(handle, None, 0, 0)
            buffer = ctypes.create_unicode_buffer(length + 1)
            written = kernel32.GetFinalPathNameByHandleW(handle, buffer, length + 1, 0)
            if not written or _normalized_path(Path(buffer.value)) != _normalized_path(parent):
                kernel32.CloseHandle(handle)
                raise ExportTargetRefError("REF_SCOPE_DENIED")
        try:
            _validate_target_entry(self.path, self.replace_existing)
            yield self
            _validate_published_entry(self.path, parent)
        finally:
            if handle is not None:
                kernel32.CloseHandle(handle)

    def publish(self, temporary: Path) -> None:
        if temporary.parent.resolve(strict=True) != self.path.parent.resolve(strict=True):
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        _validate_target_entry(self.path, self.replace_existing)
        os.replace(temporary, self.path)


class ExportTargetGrantRegistry:
    """Validates registered host grants and atomically consumes each ref once.

    ``register`` is an internal trusted-host injection seam. The stdio
    registration method is only callable by the Tauri host; the WebView never
    receives this capability or its mapped path.
    """

    _TOKEN = re.compile(r"^etref1\.([A-Za-z0-9_-]{16,128})\.([A-Za-z0-9_-]{43})$")

    def __init__(self, *, clock=time.time) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._grants: dict[str, _Grant] = {}
        self._session_id: str | None = None

    def register(
        self, *, grant_id: str, session_id: str, target_path: str,
        format: str, replace_existing: bool, expires_at: float,
        signing_key: bytes, signature: str,
    ) -> None:
        if (
            not isinstance(grant_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", grant_id)
            or not isinstance(session_id, str) or not session_id
            or not isinstance(target_path, str) or not target_path
            or format not in {"png", "zip", "cbz", "pdf", "text"}
            or not isinstance(replace_existing, bool)
            or isinstance(expires_at, bool) or not isinstance(expires_at, (int, float))
            or not math.isfinite(expires_at)
            or not isinstance(signing_key, bytes) or len(signing_key) < 32
            or not isinstance(signature, str)
        ):
            raise ExportTargetRefError("REF_MALFORMED")
        now = self._clock()
        if expires_at <= now or expires_at > now + 300:
            raise ExportTargetRefError("REF_EXPIRED")
        target = Path(target_path)
        if not target.is_absolute() or not target.name:
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        expected = _signature(signing_key, grant_id, session_id, target, format, replace_existing, expires_at)
        if not hmac.compare_digest(signature, expected):
            raise ExportTargetRefError("REF_SIGNATURE_INVALID")
        _validate_target_entry(target, replace_existing)
        with self._lock:
            if self._session_id is None:
                self._session_id = session_id
            elif self._session_id != session_id:
                raise ExportTargetRefError("REF_SCOPE_DENIED")
            if grant_id in self._grants:
                raise ExportTargetRefError("REF_UNKNOWN_ID")
            self._grants[grant_id] = _Grant(
                grant_id, session_id, target, format, replace_existing,
                float(expires_at), signing_key, signature,
            )

    def revoke(self, grant_id: str) -> None:
        with self._lock:
            grant = self._grants.get(grant_id)
            if grant is None:
                raise ExportTargetRefError("REF_UNKNOWN_ID")
            grant.revoked = True

    def resolve_and_consume(self, reference: object, format: str) -> ResolvedExportTarget:
        if not isinstance(reference, str):
            raise ExportTargetRefError("REF_MALFORMED")
        match = self._TOKEN.fullmatch(reference)
        if match is None:
            raise ExportTargetRefError("REF_MALFORMED")
        grant_id, signature = match.groups()
        with self._lock:
            grant = self._grants.get(grant_id)
            if grant is None:
                raise ExportTargetRefError("REF_UNKNOWN_ID")
            expected = _signature(
                grant.signing_key, grant.grant_id, grant.session_id, grant.target,
                grant.format, grant.replace_existing, grant.expires_at,
            )
            if not hmac.compare_digest(signature, expected) or not hmac.compare_digest(signature, grant.signature):
                raise ExportTargetRefError("REF_SIGNATURE_INVALID")
            if grant.session_id != self._session_id or grant.format != format:
                raise ExportTargetRefError("REF_SCOPE_DENIED")
            if grant.expires_at <= self._clock():
                raise ExportTargetRefError("REF_EXPIRED")
            if grant.revoked:
                raise ExportTargetRefError("REF_REVOKED")
            if grant.consumed:
                raise ExportTargetRefError("REF_ALREADY_CONSUMED")
            _validate_target_entry(grant.target, grant.replace_existing)
            grant.consumed = True
            return ResolvedExportTarget(grant.target, grant.replace_existing)


def _signature(key: bytes, grant_id: str, session_id: str, target: Path,
               fmt: str, replace_existing: bool, expires_at: float) -> str:
    payload = "\0".join((grant_id, session_id, str(target), fmt,
                         "1" if replace_existing else "0", f"{expires_at:.6f}")).encode()
    return base64.urlsafe_b64encode(hmac.new(key, payload, hashlib.sha256).digest()).decode().rstrip("=")


def _validate_target_entry(target: Path, replace_existing: bool) -> None:
    try:
        _reject_reparse_components(target.parent.absolute())
        parent = target.parent.resolve(strict=True)
        _reject_reparse_components(parent)
        if not parent.is_dir() or target.is_dir() or target.is_symlink():
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        if target.exists() and not replace_existing:
            raise ExportTargetRefError("REF_SCOPE_DENIED")
    except ExportTargetRefError:
        raise
    except OSError as error:
        raise ExportTargetRefError("REF_SCOPE_DENIED") from error


def _validate_published_entry(target: Path, authorized_parent: Path) -> None:
    try:
        parent = target.parent.resolve(strict=True)
        if _normalized_path(parent) != _normalized_path(authorized_parent):
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        _reject_reparse_components(parent)
        _reject_reparse_components(target)
        if target.is_symlink() or not target.is_file():
            raise ExportTargetRefError("REF_SCOPE_DENIED")
    except ExportTargetRefError:
        raise
    except OSError as error:
        raise ExportTargetRefError("REF_SCOPE_DENIED") from error


def _reject_reparse_components(path: Path) -> None:
    probe = Path(path.anchor)
    for part in path.parts[1:]:
        probe /= part
        if not probe.exists():
            raise ExportTargetRefError("REF_SCOPE_DENIED")
        info = os.lstat(probe)
        if os.path.islink(probe) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ExportTargetRefError("REF_SCOPE_DENIED")


def _normalized_path(path: Path) -> str:
    value = str(path)
    if value.startswith("\\\\?\\"):
        value = value[4:]
    return os.path.normcase(os.path.normpath(value))
