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
import json
import os
from ctypes import wintypes
from pathlib import Path
from typing import NamedTuple, Optional

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
    E_SCOPE_DENIED,
    E_SHARING_VIOLATION,
    E_SIZE_CHANGED,
    E_TOO_LARGE,
)

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
CREATE_NEW = 1
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
FILE_ATTRIBUTE_NORMAL = 0x80
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
ERROR_SHARING_VIOLATION = 32
ERROR_FILE_NOT_FOUND = 2
ERROR_PATH_NOT_FOUND = 3

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

_k32.SetFilePointerEx.restype = wintypes.BOOL
_k32.SetFilePointerEx.argtypes = [
    wintypes.HANDLE, ctypes.c_longlong, ctypes.POINTER(ctypes.c_longlong), wintypes.DWORD,
]

_k32.GetFinalPathNameByHandleW.restype = wintypes.DWORD
_k32.GetFinalPathNameByHandleW.argtypes = [
    wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD,
]

_k32.WriteFile.restype = wintypes.BOOL
_k32.WriteFile.argtypes = [
    wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD,
    ctypes.POINTER(wintypes.DWORD), ctypes.c_void_p,
]

_k32.SetFileInformationByHandle.restype = wintypes.BOOL
_k32.SetFileInformationByHandle.argtypes = [
    wintypes.HANDLE, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
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


def _seek_start(handle: int) -> None:
    if not _k32.SetFilePointerEx(wintypes.HANDLE(handle), 0, None, 0):
        raise TypedResourceChannelError(E_OPEN_FAILED, f"win32 error {ctypes.get_last_error()}")


def _digest_of(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class HandleVerifiedFileReader:
    """Reads a granted resource through one verified handle (infrastructure
    adapter behind ``application.resource_channel``)."""

    def __init__(self, scope_root: Path, *, limit: int = MAX_RESOURCE_BYTES) -> None:
        self._scope_root = Path(scope_root).resolve()
        self._scope_norm = _normalized(str(self._scope_root))
        self._limit = limit

    def open_pinned(self, grant, *, share_write: bool = False):
        """Open a file and verify its handle-derived scope, identity and size.

        The caller verifies the digest after opening every requested handle,
        then consumes each source through the same OS handle.
        """
        return _VerifiedFileHandle(self, grant, share_write=share_write)

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


class _VerifiedFileHandle:
    def __init__(self, reader: HandleVerifiedFileReader, grant, *, share_write: bool) -> None:
        self._grant = grant
        self._handle: int | None = None
        self._verified = False
        target = reader._scope_root.joinpath(
            *grant.rel_path.replace("\\", "/").split("/")
        )
        _preopen_reparse_walk(reader._scope_root, grant.rel_path)
        try:
            handle = _open_read_handle(target, share_write=share_write)
        except TypedResourceChannelError as error:
            if error.code == E_OPEN_FAILED:
                raise TypedResourceChannelError(E_NOT_FOUND) from error
            raise
        self._handle = handle
        try:
            final_norm = _normalized(_final_path_of(handle))
            if final_norm != reader._scope_norm and not final_norm.startswith(reader._scope_norm + "\\"):
                raise TypedResourceChannelError(E_OUT_OF_SCOPE)
            if _attributes_of(handle) & FILE_ATTRIBUTE_REPARSE_POINT:
                raise TypedResourceChannelError(E_REPARSE)
            if _identity_of(handle) != (grant.facts.volume_serial, grant.facts.file_index):
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
            size = _size_of(handle)
            if size != grant.facts.size:
                raise TypedResourceChannelError(E_SIZE_CHANGED)
            if size > reader._limit:
                raise TypedResourceChannelError(E_TOO_LARGE)
        except BaseException:
            self.close()
            raise

    def verify(self) -> None:
        if self._handle is None:
            raise OSError("verified source handle is closed")
        handle = self._handle
        digest, streamed = _digest_through(handle)
        if streamed != self._grant.facts.size:
            raise TypedResourceChannelError(E_SIZE_CHANGED)
        if digest != self._grant.facts.sha256:
            raise TypedResourceChannelError(E_DIGEST_MISMATCH)
        if _identity_of(handle) != (
            self._grant.facts.volume_serial, self._grant.facts.file_index
        ):
            raise TypedResourceChannelError(E_IDENTITY_CHANGED)
        _seek_start(handle)
        self._verified = True

    def read(self) -> bytes:
        if self._handle is None:
            raise OSError("verified source handle is closed")
        handle = self._handle
        try:
            if not self._verified:
                self.verify()
            _seek_start(handle)
            data = _read_all_through(handle)
            if len(data) != self._grant.facts.size:
                raise TypedResourceChannelError(E_SIZE_CHANGED)
            if _digest_of(data) != self._grant.facts.sha256:
                raise TypedResourceChannelError(E_DIGEST_MISMATCH)
            if _identity_of(handle) != (
                self._grant.facts.volume_serial, self._grant.facts.file_index
            ):
                raise TypedResourceChannelError(E_IDENTITY_CHANGED)
            return data
        finally:
            self.close()

    def close(self) -> None:
        if self._handle is not None:
            _k32.CloseHandle(wintypes.HANDLE(self._handle))
            self._handle = None


# ---------------------------------------------------------------------------
# M2-DERIVED-GC-2: preview namespace lease + handle-verified deletion.
#
# The namespace lease is a stable Windows kernel file lock anchored at
# ``<derived>/.preview-lifecycle.lock`` (inside the deletion-domain derived
# root, outside the previews//pages/ sweep directories). Every managed
# production Core / resource-channel process holds a SHARED lease for its
# whole business lifetime; the startup GC may take an EXCLUSIVE lease only
# when no shared lease is held anywhere, and holds it until all verdicts,
# unlinks and metadata updates are done. Process death releases the lease by
# the OS. Bindings are {protocol_version, derived root canonical+identity,
# catalog canonical+identity}; all participants verify the same tuple.
# Aliased roots / mixed bindings / unknown history are UNKNOWN and both
# sweeps are skipped -- never a guess-and-delete.
# ---------------------------------------------------------------------------

PREVIEW_LIFECYCLE_PROTOCOL_VERSION = 1
PREVIEW_NAMESPACE_LOCK_NAME = ".preview-lifecycle.lock"

#: M2-S2 keep: read + DELETE with ONLY FILE_SHARE_READ -- an existing reader
#: or writer makes the delete open fail (sharing violation -> retain), and a
#: verified-candidate open blocks new writers until the disposition lands.
FILE_DELETE = 0x00010000
_DELETE_ACCESS = GENERIC_READ | GENERIC_WRITE | FILE_DELETE

_FILE_DISPOSITION_INFO = 4  # FILE_INFO_BY_HANDLE_CLASS.FileDispositionInfo


class FILE_DISPOSITION_INFO(ctypes.Structure):
    _fields_ = [("DeleteFile", wintypes.BOOL)]


class NamespaceBinding(NamedTuple):
    """The frozen four-tuple identity of one preview namespace (design §2.3)."""

    protocol_version: int
    derived_root: str
    derived_identity: tuple[int, int]
    catalog_root: str
    catalog_identity: tuple[int, int]

    def as_dict(self) -> dict:
        return {
            "protocol_version": self.protocol_version,
            "derived_root": self.derived_root,
            "derived_identity": list(self.derived_identity),
            "catalog_root": self.catalog_root,
            "catalog_identity": list(self.catalog_identity),
        }

    @classmethod
    def from_dict(cls, payload) -> "NamespaceBinding":
        if not isinstance(payload, dict):
            raise ValueError("namespace binding must be a JSON object")
        derived_identity = payload["derived_identity"]
        catalog_identity = payload["catalog_identity"]
        binding = cls(
            protocol_version=int(payload["protocol_version"]),
            derived_root=str(payload["derived_root"]),
            derived_identity=(int(derived_identity[0]), int(derived_identity[1])),
            catalog_root=str(payload["catalog_root"]),
            catalog_identity=(int(catalog_identity[0]), int(catalog_identity[1])),
        )
        if binding.protocol_version != PREVIEW_LIFECYCLE_PROTOCOL_VERSION:
            raise ValueError(f"unsupported namespace protocol {binding.protocol_version}")
        return binding


def namespace_unavailable(reason: str) -> TypedResourceChannelError:
    """Typed refusal for namespace bootstrap/lease failures (fail-closed:
    no business access and no sweep ever runs without a verified lease)."""
    return TypedResourceChannelError(
        E_SCOPE_DENIED, f"preview namespace unavailable: {reason}"
    )


def _lstat_reparse_walk(path: Path) -> None:
    """Reject any reparse component from the drive root down to ``path``.

    ``Path.resolve()`` silently traverses junctions/symlinks; this walk is
    what makes a reparse component a typed refusal instead of a silent
    aliasing. A missing tail is left to surface as a typed open failure.
    """
    parts = path.parts
    probe = Path(parts[0])
    for segment in parts[1:]:
        probe = probe / segment
        try:
            attributes = os.lstat(probe).st_file_attributes
        except OSError:
            return
        if attributes & FILE_ATTRIBUTE_REPARSE_POINT:
            raise namespace_unavailable(f"reparse component in namespace path: {segment}")


def _open_directory_handle(resolved: Path) -> int:
    handle = _k32.CreateFileW(
        str(resolved), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, None,
        OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS, None,
    )
    if not handle or handle == INVALID_HANDLE_VALUE:
        raise namespace_unavailable(f"win32 error {ctypes.get_last_error()}")
    return int(handle)


def resolve_namespace_identity(path: Path) -> tuple[str, tuple[int, int]]:
    """Canonical path + volume/file identity of an existing file or directory.

    Refuses reparse components first, then opens the resolved path once and
    re-verifies the final path against what was named -- an aliased identity
    is a namespace refusal, never a guessed match.
    """
    _lstat_reparse_walk(path)
    resolved = path.resolve()
    _lstat_reparse_walk(resolved)
    handle = _open_directory_handle(resolved)
    try:
        identity = _identity_of(handle)
        final = _final_path_of(handle)
        if _normalized(final) != _normalized(str(resolved)):
            raise namespace_unavailable("namespace path resolved to a different identity")
    finally:
        _k32.CloseHandle(wintypes.HANDLE(handle))
    return str(resolved), identity


def _open_lock_handle(derived_root: str, *, exclusive: bool, create_new: bool = False) -> int:
    """The namespace lock file handle itself IS the lease.

    Shared lease: GENERIC_READ with FILE_SHARE_READ|FILE_SHARE_WRITE -- any
    number of managed processes can hold it concurrently. Exclusive lease:
    GENERIC_READ|GENERIC_WRITE with share mode 0 -- it fails with a sharing
    violation while any shared lease is open (non-blocking by construction),
    and no shared lease can be taken while it is held.

    The pre-open lstat walk cannot cover a replacement BETWEEN the walk and
    ``CreateFileW`` (Codex r1 F-02), so the OPENED HANDLE is verified before
    it may count as a lease: no reparse attribute and a final path identical
    to the requested lock path -- anything else is a refused lease, never a
    lock on a different object."""

    lock_path = Path(derived_root) / PREVIEW_NAMESPACE_LOCK_NAME
    _lstat_reparse_walk(lock_path)
    access = (GENERIC_READ | GENERIC_WRITE) if exclusive else GENERIC_READ
    share = 0 if exclusive else (FILE_SHARE_READ | FILE_SHARE_WRITE)
    disposition = CREATE_NEW if create_new else OPEN_EXISTING
    handle = _k32.CreateFileW(
        str(lock_path), access, share, None, disposition, FILE_ATTRIBUTE_NORMAL, None,
    )
    if not handle or handle == INVALID_HANDLE_VALUE:
        error = ctypes.get_last_error()
        if error in (ERROR_FILE_NOT_FOUND, ERROR_PATH_NOT_FOUND):
            raise FileNotFoundError(str(lock_path))
        raise namespace_unavailable(
            f"namespace lock open failed (win32 error {error}, exclusive={exclusive})"
        )
    try:
        if _attributes_of(handle) & FILE_ATTRIBUTE_REPARSE_POINT:
            raise namespace_unavailable("namespace lock path is a reparse point")
        final = _final_path_of(handle)
        if _normalized(final) != _normalized(str(lock_path)):
            raise namespace_unavailable("namespace lock path resolved to a different object")
    except BaseException:
        _k32.CloseHandle(wintypes.HANDLE(handle))
        raise
    return int(handle)


def _write_lock_content(handle: int, binding: NamespaceBinding) -> None:
    payload = (json.dumps(binding.as_dict(), sort_keys=True) + "\n").encode("utf-8")
    written = wintypes.DWORD(0)
    chunk = 1 << 16
    offset = 0
    while offset < len(payload):
        block = payload[offset:offset + chunk]
        ok = _k32.WriteFile(
            wintypes.HANDLE(handle), block, len(block), ctypes.byref(written), None
        )
        if not ok or written.value != len(block):
            raise namespace_unavailable(f"namespace lock write failed (win32 error {ctypes.get_last_error()})")
        offset += written.value


def _read_lock_binding(handle: int) -> NamespaceBinding:
    data = _read_all_through(handle)
    try:
        return NamespaceBinding.from_dict(json.loads(data.decode("utf-8")))
    except (ValueError, KeyError, TypeError, UnicodeDecodeError) as error:
        raise namespace_unavailable(f"namespace lock content unusable: {error}") from error


def _verify_binding(
    binding: NamespaceBinding,
    derived_root: str,
    derived_identity: tuple[int, int],
    expected_catalog_identity: tuple[int, int] | None,
) -> None:
    if binding.derived_root != derived_root or binding.derived_identity != derived_identity:
        raise namespace_unavailable("namespace lock is bound to a different derived root")
    if expected_catalog_identity is not None and binding.catalog_identity != expected_catalog_identity:
        raise namespace_unavailable("namespace lock is bound to a different catalog identity")


class PreviewNamespaceLease:
    """One open kernel handle on the namespace lock file.

    ``release`` closes the handle (the OS drops the lease; a dead process
    never keeps one). A borrowed lease (production Core handing its exclusive
    or shared lease to the store) is closed by its owner, not the store.
    """

    def __init__(self, handle: int, binding: NamespaceBinding, *, exclusive: bool) -> None:
        self._handle: int | None = handle
        self.binding = binding
        self.exclusive = exclusive

    @property
    def held(self) -> bool:
        return self._handle is not None

    def release(self) -> None:
        if self._handle is not None:
            _k32.CloseHandle(wintypes.HANDLE(self._handle))
            self._handle = None

    def __enter__(self) -> "PreviewNamespaceLease":
        return self

    def __exit__(self, *exc_info) -> None:
        self.release()


def acquire_shared_lease(
    derived_root: Path | str, *, expected_catalog_identity: tuple[int, int] | None = None
) -> PreviewNamespaceLease:
    """Shared business lease on a bound namespace (design §2.3 bootstrap:
    the binding read from the lock is re-verified against the actual derived
    root identity before the lease is handed out)."""
    derived_str, derived_identity = resolve_namespace_identity(Path(derived_root))
    handle = _open_lock_handle(derived_str, exclusive=False)
    try:
        binding = _read_lock_binding(handle)
        _verify_binding(binding, derived_str, derived_identity, expected_catalog_identity)
    except BaseException:
        _k32.CloseHandle(wintypes.HANDLE(handle))
        raise
    return PreviewNamespaceLease(handle, binding, exclusive=False)


def try_acquire_exclusive_lease(
    derived_root: Path | str, *, expected_catalog_identity: tuple[int, int] | None = None
) -> Optional[PreviewNamespaceLease]:
    """Non-blocking exclusive lease attempt for the startup GC window.

    ``None`` means a managed peer holds a shared lease: skip both sweeps and
    serve normally under a shared lease -- never wait, never force.
    """
    try:
        derived_str, derived_identity = resolve_namespace_identity(Path(derived_root))
    except TypedResourceChannelError:
        return None
    try:
        handle = _open_lock_handle(derived_str, exclusive=True)
    except (TypedResourceChannelError, FileNotFoundError):
        return None
    try:
        binding = _read_lock_binding(handle)
        _verify_binding(binding, derived_str, derived_identity, expected_catalog_identity)
    except BaseException:
        _k32.CloseHandle(wintypes.HANDLE(handle))
        return None
    return PreviewNamespaceLease(handle, binding, exclusive=True)


def open_exclusive_lock_for_initialize(derived_root: Path | str) -> tuple[int, str, tuple[int, int]]:
    """Exclusively open (creating if absent) the namespace lock for the
    controlled first-bind window. Returns (handle, derived_root, identity);
    the caller owns the handle until the binding is fully registered."""
    derived_str, derived_identity = resolve_namespace_identity(Path(derived_root))
    try:
        handle = _open_lock_handle(derived_str, exclusive=True)
    except FileNotFoundError:
        handle = _open_lock_handle(derived_str, exclusive=True, create_new=True)
    return handle, derived_str, derived_identity


def read_lock_binding_if_any(derived_root: str) -> NamespaceBinding | None:
    """Best-effort read of an existing lock binding (initialize preflight)."""
    try:
        handle = _open_lock_handle(derived_root, exclusive=False)
    except (TypedResourceChannelError, FileNotFoundError):
        return None
    try:
        data = _read_all_through(handle)
    finally:
        _k32.CloseHandle(wintypes.HANDLE(handle))
    if not data.strip():
        return None
    try:
        return NamespaceBinding.from_dict(json.loads(data.decode("utf-8")))
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return None


def read_lock_content_if_any(handle: int) -> NamespaceBinding | None:
    """Best-effort binding read THROUGH an already-held exclusive lock
    handle (the initialize preflight must not open a second, shared handle
    against its own exclusive lease). Empty or unusable content reads as
    ``None`` (a freshly created lock file)."""
    data = _read_all_through(handle)
    if not data.strip():
        return None
    try:
        return NamespaceBinding.from_dict(json.loads(data.decode("utf-8")))
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        return None


def write_lock_content(handle: int, binding: NamespaceBinding) -> None:
    _write_lock_content(handle, binding)


def close_lock_handle(handle: int) -> None:
    _k32.CloseHandle(wintypes.HANDLE(handle))


def handle_verified_delete(
    scope_root: Path,
    rel_path: str,
    *,
    expected_sha256: str,
    expected_size: int,
) -> tuple[bool, str]:
    """Delete a verified derived copy by DELETE DISPOSITION on the same
    handle that proved its identity (design §2.4; no pathname unlink).

    Sequence: the parent-directory handle is taken first and held for the
    whole operation (blocks replace/rename of the directory); the candidate
    is opened once with read+write+DELETE access and FILE_SHARE_READ only --
    a pre-held reader/writer fails the open (sharing violation -> retain)
    and no new writer can open while the handle is held. Identity/size/
    streaming SHA-256 are verified FROM the handle; a reparse attribute, a
    size/hash mismatch or any unexpected error retains the file. Deletion
    happens when the disposition is set and the handle closes; the caller
    re-checks the reported outcome.
    """
    from application.resource_channel.dto import validate_rel_path

    validate_rel_path(rel_path)
    root = Path(scope_root).resolve()
    target = root.joinpath(*rel_path.replace("\\", "/").split("/"))
    _lstat_reparse_walk(target)
    directory = _open_directory_handle(target.parent)
    try:
        dir_final = _final_path_of(directory)
        dir_norm = _normalized(dir_final)
        previews_norm = _normalized(str(root / rel_path.split("/", 1)[0]))
        if dir_norm != previews_norm:
            return False, "parent directory is not the previews scope directory"
        handle = _k32.CreateFileW(
            str(target), _DELETE_ACCESS, FILE_SHARE_READ, None,
            OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, None,
        )
        if not handle or handle == INVALID_HANDLE_VALUE:
            error = ctypes.get_last_error()
            if error == ERROR_SHARING_VIOLATION:
                return False, "sharing violation (in-flight reader/writer retained)"
            if error in (ERROR_FILE_NOT_FOUND, ERROR_PATH_NOT_FOUND):
                return False, "file missing"
            return False, f"win32 error {error}"
        try:
            if _attributes_of(handle) & FILE_ATTRIBUTE_REPARSE_POINT:
                return False, "reparse candidate retained"
            final = _final_path_of(handle)
            final_norm = _normalized(final)
            if final_norm != _normalized(str(target)):
                return False, "final path mismatch"
            size = _size_of(handle)
            if size != expected_size:
                return False, f"size mismatch {size} != {expected_size}"
            digest, streamed = _digest_through(handle)
            if streamed != expected_size or digest != expected_sha256:
                return False, "content hash mismatch (manual modification retained)"
            disposition = FILE_DISPOSITION_INFO(DeleteFile=True)
            ok = _k32.SetFileInformationByHandle(
                wintypes.HANDLE(handle), _FILE_DISPOSITION_INFO,
                ctypes.byref(disposition), ctypes.sizeof(disposition),
            )
            if not ok:
                return False, f"delete disposition refused (win32 error {ctypes.get_last_error()})"
        finally:
            _k32.CloseHandle(wintypes.HANDLE(handle))
    finally:
        _k32.CloseHandle(wintypes.HANDLE(directory))
    if target.exists():
        return False, "file still present after disposition"
    return True, "deleted"
