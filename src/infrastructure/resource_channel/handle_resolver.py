"""Handle-verified resource reading adapter (M2-RC1, infrastructure).

Productisation of the M2-S2 ``HandleVerifiedResolver`` read path (S1-B11
release condition 1): open the target **once**, verify containment, file
identity, issue-time size and the T1 limit **from that handle**, read **only
through that handle**, verify the issue-time content digest, and re-check the
identity after reading. A check-then-use flow must not be the security
boundary.

Error surfaces are stable typed codes from
``application.resource_channel.dto``; messages never carry OS paths or
mapping-table contents (this module's callers log codes, not paths).

The digest layer pins ``resolved == issued`` (M2-S2 §7): the content at issue
time is trusted by the issuing flow; this adapter guarantees what is served
is exactly what was issued.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
from ctypes import wintypes
from pathlib import Path

from application.resource_channel.dto import (
    MAX_RESOURCE_BYTES,
    ResourceFacts,
    TypedResourceChannelError,
    E_DIGEST_MISMATCH,
    E_IDENTITY_CHANGED,
    E_NOT_FOUND,
    E_OPEN_FAILED,
    E_OUT_OF_SCOPE,
    E_REPARSE,
    E_SHARING_VIOLATION,
    E_SIZE_CHANGED,
    E_TOO_LARGE,
)

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
ERROR_SHARING_VIOLATION = 32

_CHUNK = 1 << 20  # 1 MiB streaming blocks; resident buffer stays far below 32 MiB

_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_k32.CreateFileW.restype = wintypes.HANDLE
_k32.CreateFileW.argtypes = [
    wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
    wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
]
_k32.CloseHandle.argtypes = [wintypes.HANDLE]
_k32.CloseHandle.restype = wintypes.BOOL
_k32.ReadFile.argtypes = [
    wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p,
]
_k32.ReadFile.restype = wintypes.BOOL


class _BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", wintypes.DWORD),
        ("ftCreationTime", wintypes.FILETIME),
        ("ftLastAccessTime", wintypes.FILETIME),
        ("ftLastWriteTime", wintypes.FILETIME),
        ("dwVolumeSerialNumber", wintypes.DWORD),
        ("nFileSizeHigh", wintypes.DWORD),
        ("nFileSizeLow", wintypes.DWORD),
        ("nNumberOfLinks", wintypes.DWORD),
        ("nFileIndexHigh", wintypes.DWORD),
        ("nFileIndexLow", wintypes.DWORD),
    ]

    def identity(self) -> tuple[int, int]:
        return (
            int(self.dwVolumeSerialNumber),
            (int(self.nFileIndexHigh) << 32) | int(self.nFileIndexLow),
        )

    def size(self) -> int:
        return (int(self.nFileSizeHigh) << 32) | int(self.nFileSizeLow)


_k32.GetFileInformationByHandle.restype = wintypes.BOOL
_k32.GetFileInformationByHandle.argtypes = [
    wintypes.HANDLE, ctypes.POINTER(_BY_HANDLE_FILE_INFORMATION),
]

_k32.GetFinalPathNameByHandleW.restype = wintypes.DWORD
_k32.GetFinalPathNameByHandleW.argtypes = [
    wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
]


def _open_read_handle(path: Path, *, share_write: bool = False) -> int:
    """Narrow share (default) fails closed against a pre-held writer and
    blocks new writers while held; ``share_write=True`` models the
    availability-first mode (M2-S2 T-16..T-18) where the issue-time digest
    carries the load instead."""

    share = FILE_SHARE_READ | FILE_SHARE_WRITE if share_write else FILE_SHARE_READ
    handle = _k32.CreateFileW(
        str(path), GENERIC_READ, share, None,
        OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, None,
    )
    if not handle or handle == INVALID_HANDLE_VALUE:
        error = ctypes.get_last_error()
        if error == ERROR_SHARING_VIOLATION:
            raise TypedResourceChannelError(
                E_SHARING_VIOLATION, "pre-held writer makes the read open fail closed"
            )
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {error}")
    return int(handle)


def _identity_of(handle: int) -> tuple[int, int]:
    info = _BY_HANDLE_FILE_INFORMATION()
    if not _k32.GetFileInformationByHandle(wintypes.HANDLE(handle), ctypes.byref(info)):
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
    return info.identity()


def _size_of(handle: int) -> int:
    info = _BY_HANDLE_FILE_INFORMATION()
    if not _k32.GetFileInformationByHandle(wintypes.HANDLE(handle), ctypes.byref(info)):
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
    return info.size()


def _attributes_of(handle: int) -> int:
    info = _BY_HANDLE_FILE_INFORMATION()
    if not _k32.GetFileInformationByHandle(wintypes.HANDLE(handle), ctypes.byref(info)):
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
    return int(info.dwFileAttributes)


def _final_path_of(handle: int) -> str:
    length = _k32.GetFinalPathNameByHandleW(wintypes.HANDLE(handle), None, 0, 0)
    if length == 0:
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
    buffer = ctypes.create_unicode_buffer(length + 1)
    written = _k32.GetFinalPathNameByHandleW(
        wintypes.HANDLE(handle), buffer, length + 1, 0
    )
    if written == 0 or written > length:
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
    return buffer.value


def _normalized(path_text: str) -> str:
    if path_text.startswith("\\\\?\\UNC\\"):
        path_text = "\\\\" + path_text[8:]
    elif path_text.startswith("\\\\?\\"):
        path_text = path_text[4:]
    return os.path.normpath(path_text).casefold()


def _preopen_reparse_walk(root: Path, rel_path: str) -> None:
    """Early rejection of a reparse component on the *requested* path.

    CreateFileW traverses reparse points by default, so the pre-open walk is
    the only place a junction/symlink **component** can be named and refused
    before it is followed. It has a check-then-use window of its own; the
    authoritative containment decision is still derived from the opened
    handle (M2-S2 layering).
    """

    probe = root
    for segment in rel_path.replace("\\", "/").split("/"):
        if not segment:
            continue
        probe = probe / segment
        try:
            attributes = os.lstat(probe).st_file_attributes
        except OSError:
            return  # missing components surface as open failures
        if attributes & FILE_ATTRIBUTE_REPARSE_POINT:
            raise TypedResourceChannelError(E_REPARSE)


def _read_all_through(handle: int) -> bytes:
    chunks: list[bytes] = []
    while True:
        buffer = ctypes.create_string_buffer(_CHUNK)
        read = wintypes.DWORD(0)
        ok = _k32.ReadFile(
            wintypes.HANDLE(handle), buffer, _CHUNK, ctypes.byref(read), None
        )
        if not ok:
            raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
        if read.value == 0:
            break
        chunks.append(buffer.raw[: read.value])
    return b"".join(chunks) if len(chunks) > 1 else (chunks[0] if chunks else b"")


def _digest_through(handle: int) -> tuple[str, int]:
    """Stream-hash through the handle without materialising the resource."""

    digest = hashlib.sha256()
    total = 0
    while True:
        buffer = ctypes.create_string_buffer(_CHUNK)
        read = wintypes.DWORD(0)
        ok = _k32.ReadFile(
            wintypes.HANDLE(handle), buffer, _CHUNK, ctypes.byref(read), None
        )
        if not ok:
            raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
        if read.value == 0:
            break
        digest.update(buffer.raw[: read.value])
        total += read.value
    return digest.hexdigest(), total


def _digest_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class HandleVerifiedFileReader:
    """Reads a granted resource through one verified handle (infrastructure
    adapter behind ``application.resource_channel``)."""

    def __init__(self, scope_root: Path, *, limit: int = MAX_RESOURCE_BYTES) -> None:
        self._scope_root = Path(scope_root).resolve()
        self._scope_norm = _normalized(str(self._scope_root))
        self._limit = limit

    # ------------------------------------------------------------- issuing

    def capture_facts(self, rel_path: str) -> ResourceFacts:
        """Issue-time facts for a scope-relative resource (M2-S2: digest pins
        ``resolved == issued``; issue-time content is trusted by the issuing
        flow). Opens once, reads identity/size/digest through that handle."""

        target = self._scope_root.joinpath(*rel_path.replace("\\", "/").split("/"))
        _preopen_reparse_walk(self._scope_root, rel_path)
        try:
            handle = _open_read_handle(target)
        except TypedResourceChannelError as error:
            if error.code == E_OPEN_FAILED:
                raise TypedResourceChannelError(E_NOT_FOUND) from error
            raise
        try:
            identity = _identity_of(handle)
            size = _size_of(handle)
            if _attributes_of(handle) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise TypedResourceChannelError(E_REPARSE)
            digest, streamed = _digest_through(handle)
        finally:
            _k32.CloseHandle(wintypes.HANDLE(handle))
        if streamed != size:
            raise TypedResourceChannelError(E_SIZE_CHANGED)
        return ResourceFacts(
            volume_serial=identity[0],
            file_index=identity[1],
            size=size,
            sha256=digest,
        )

    def issue_digest(self, rel_path: str) -> str:
        return self.capture_facts(rel_path).sha256

    # ----------------------------------------------------------- resolving

    def read(self, grant, opaque_id: str | None = None, *, share_write: bool = False) -> bytes:
        """Open-then-verify-from-handle read of a granted resource.

        ``opaque_id`` is accepted for logging symmetry only; this layer never
        resolves IDs -- the Core already did (control plane).
        """

        del opaque_id
        target = self._scope_root.joinpath(
            *grant.rel_path.replace("\\", "/").split("/")
        )
        _preopen_reparse_walk(self._scope_root, grant.rel_path)
        handle = _open_read_handle(target, share_write=share_write)
        try:
            # containment from the handle: the authoritative path-level check
            final = _final_path_of(handle)
            final_norm = _normalized(final)
            if final_norm != self._scope_norm and not final_norm.startswith(self._scope_norm + "\\"):
                raise TypedResourceChannelError(E_OUT_OF_SCOPE)
            if _attributes_of(handle) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise TypedResourceChannelError(E_REPARSE)

            # identity + size from the handle vs issue-time facts
            if _identity_of(handle) != (grant.facts.volume_serial, grant.facts.file_index):
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
            size = _size_of(handle)
            if size != grant.facts.size:
                raise TypedResourceChannelError(E_SIZE_CHANGED)
            if size > self._limit:
                raise TypedResourceChannelError(
                    E_TOO_LARGE, f"size {size} exceeds limit {self._limit}"
                )

            data = _read_all_through(handle)

            # issue-time digest (catches an equal-size in-place rewrite)
            if _digest_of(data) != grant.facts.sha256:
                raise TypedResourceChannelError(E_DIGEST_MISMATCH)

            # post-read identity re-check
            if _identity_of(handle) != (grant.facts.volume_serial, grant.facts.file_index):
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
            return data
        finally:
            _k32.CloseHandle(wintypes.HANDLE(handle))

    def read_chunks(self, grant, chunk_size: int = 16 * 1024 * 1024, *, share_write: bool = False):
        """Stream a granted resource in bounded chunks through one verified
        handle (no full-resource materialisation; resident buffer == one
        chunk). Product hosts should prefer this over :meth:`read`.

        Each yielded chunk has already passed the same verification sequence
        as :meth:`read` (containment/identity/size are checked before the
        first chunk and identity is re-checked after the last; the issue-time
        digest is verified incrementally over the stream)."""

        target = self._scope_root.joinpath(
            *grant.rel_path.replace("\\", "/").split("/")
        )
        _preopen_reparse_walk(self._scope_root, grant.rel_path)
        handle = _open_read_handle(target, share_write=share_write)
        try:
            final = _final_path_of(handle)
            final_norm = _normalized(final)
            if final_norm != self._scope_norm and not final_norm.startswith(self._scope_norm + "\\"):
                raise TypedResourceChannelError(E_OUT_OF_SCOPE)
            if _attributes_of(handle) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise TypedResourceChannelError(E_REPARSE)
            if _identity_of(handle) != (grant.facts.volume_serial, grant.facts.file_index):
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
            size = _size_of(handle)
            if size != grant.facts.size:
                raise TypedResourceChannelError(E_SIZE_CHANGED)
            if size > self._limit:
                raise TypedResourceChannelError(
                    E_TOO_LARGE, f"size {size} exceeds limit {self._limit}"
                )

            digest = hashlib.sha256()
            served = 0
            while True:
                remaining = size - served
                want = min(chunk_size, remaining, _CHUNK * 16)
                buffer = ctypes.create_string_buffer(want)
                read = wintypes.DWORD(0)
                ok = _k32.ReadFile(
                    wintypes.HANDLE(handle), buffer, want, ctypes.byref(read), None
                )
                if not ok:
                    raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")
                if read.value == 0:
                    break
                block = buffer.raw[: read.value]
                served += read.value
                digest.update(block)
                yield block
            if served != grant.facts.size:
                raise TypedResourceChannelError(E_SIZE_CHANGED)
            if digest.hexdigest() != grant.facts.sha256:
                raise TypedResourceChannelError(E_DIGEST_MISMATCH)
            if _identity_of(handle) != (grant.facts.volume_serial, grant.facts.file_index):
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
        finally:
            _k32.CloseHandle(wintypes.HANDLE(handle))
