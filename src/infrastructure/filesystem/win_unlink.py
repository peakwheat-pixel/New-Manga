"""N-002: delete a file through a handle chain instead of a path.

``unlink()`` takes a *name*.  Between the moment a path is checked and the moment
it is used, any directory component can be replaced - with a junction, say - and
the delete lands wherever the name now points.  Checking more carefully cannot fix
that, because the check and the use are two different resolutions of the same
name.  The only way to close the window is to stop using names: open each
component relative to a handle obtained from its parent, verify the *object* that
handle refers to, and delete through the handle.

`CreateFileW` is not enough for the intermediate steps.  Its
``FILE_FLAG_OPEN_REPARSE_POINT`` applies to the final component only, so a
replaced middle directory is still traversed and the flag protects nothing.  This
module therefore uses ``NtCreateFile`` with ``OBJECT_ATTRIBUTES.RootDirectory``,
which opens a child *relative to a parent handle* and never re-resolves the full
path.

Every step is verified on the opened object:

* intermediate components must be directories without a reparse attribute
* the final component must be a plain file without a reparse attribute

Failure at any step closes every handle opened so far and returns False.  The
caller keeps its "refused" semantics; what changes is that a refusal can no
longer happen after the delete has already gone somewhere else.

Windows-only.  On other platforms :func:`unlink_by_handle` returns ``None`` so the
caller can fall back to its previous behaviour rather than silently doing nothing.
"""
from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from pathlib import Path

_FILE_ATTRIBUTE_DIRECTORY = 0x00000010
_FILE_ATTRIBUTE_REPARSE_POINT = 0x00000400
_FILE_ATTRIBUTE_NORMAL = 0x00000080

_DELETE = 0x00010000
_FILE_READ_ATTRIBUTES = 0x00000080
_SYNCHRONIZE = 0x00100000
# A relative open needs the PARENT handle to hold FILE_TRAVERSE.
_FILE_TRAVERSE = 0x00000020
_FILE_SHARE_ALL = 0x00000001 | 0x00000002 | 0x00000004
_OBJ_CASE_INSENSITIVE = 0x00000040
_FILE_OPEN = 0x00000001
# N-005 (Codex R3): FILE_OPEN_IF creates a missing component.  This helper
# is a delete path, so a component that is not there must be a refusal - with
# OPEN_IF the chain quietly created the missing directory and then created and
# removed the leaf, returning success for a path that never existed.
_FILE_OPEN_IF = 0x00000003  # kept for reference; not used on the delete path
_FILE_DIRECTORY_FILE = 0x00000001
_FILE_NON_DIRECTORY_FILE = 0x00000040
_FILE_OPEN_REPARSE_POINT = 0x00200000
_FILE_SYNCHRONOUS_IO_NONALERT = 0x00000020
_OPEN_EXISTING = 3
_FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
_FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000

_STATUS_SUCCESS = 0
_FILE_DISPOSITION_INFO_CLASS = 4
_INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value


class _UNICODE_STRING(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.USHORT),
        ("MaximumLength", wintypes.USHORT),
        ("Buffer", wintypes.LPWSTR),
    ]


class _OBJECT_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Length", wintypes.ULONG),
        ("RootDirectory", wintypes.HANDLE),
        ("ObjectName", ctypes.POINTER(_UNICODE_STRING)),
        ("Attributes", wintypes.ULONG),
        ("SecurityDescriptor", ctypes.c_void_p),
        ("SecurityQualityOfService", ctypes.c_void_p),
    ]


class _IO_STATUS_BLOCK(ctypes.Structure):
    _fields_ = [("Status", ctypes.c_void_p), ("Information", ctypes.c_void_p)]


class _FILE_DISPOSITION_INFO(ctypes.Structure):
    _fields_ = [("DeleteFile", wintypes.BOOL)]


class _FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = [("FileAttributes", wintypes.DWORD), ("ReparseTag", wintypes.DWORD)]


_ntdll = ctypes.WinDLL("ntdll", use_last_error=True) if os.name == "nt" else None
_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True) if os.name == "nt" else None

if _ntdll is not None:
    _ntdll.NtCreateFile.restype = ctypes.c_long
    _ntdll.NtCreateFile.argtypes = [
        ctypes.POINTER(wintypes.HANDLE), wintypes.ULONG,
        ctypes.POINTER(_OBJECT_ATTRIBUTES), ctypes.POINTER(_IO_STATUS_BLOCK),
        ctypes.c_void_p, wintypes.ULONG, wintypes.ULONG, wintypes.ULONG,
        wintypes.ULONG, ctypes.c_void_p, wintypes.ULONG,
    ]
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.GetFileInformationByHandleEx.restype = wintypes.BOOL
    _kernel32.GetFileInformationByHandleEx.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]
    _kernel32.CreateFileW.restype = wintypes.HANDLE
    _kernel32.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.c_void_p,
        wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
    ]
    _kernel32.SetFileInformationByHandle.restype = wintypes.BOOL
    _kernel32.SetFileInformationByHandle.argtypes = [
        wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD,
    ]


def _status_ok(status: int) -> bool:
    return status == _STATUS_SUCCESS


def _open_anchor(root: Path) -> tuple[int, list[str]] | None:
    """Open the drive root and return the segments left to walk.

    N-004 (Codex R3): opening the root by its full path still re-resolves its
    ancestors, so replacing one of them with a junction sends the delete outside.
    The chain verified everything below the root while assuming the root could not
    move.  Starting at the drive root removes that assumption - a volume's root has
    no ancestor to swap - and every component below is opened relative to its
    parent's handle.

    A volume handle such as the C: device form was measured and refused the relative open with
    STATUS_INVALID_PARAMETER, so the drive root is used instead; it also needs no
    privilege, which a volume handle generally does.

    UNC paths have no drive root, so they are refused rather than opened by path -
    a fallback there would reintroduce the hole being closed.
    """
    drive, tail = os.path.splitdrive(str(root))
    if not drive or drive.startswith("\\\\") or not tail:
        return None
    handle = _kernel32.CreateFileW(
        drive + "\\",
        _FILE_READ_ATTRIBUTES | _SYNCHRONIZE | _FILE_TRAVERSE,
        _FILE_SHARE_ALL,
        None,
        _OPEN_EXISTING,
        _FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if not handle or handle == _INVALID_HANDLE_VALUE:
        return None
    segments = [part for part in tail.replace("/", "\\").split("\\") if part]
    if not segments:
        _kernel32.CloseHandle(wintypes.HANDLE(handle))
        return None
    return handle, segments


def _open_root(root: Path) -> int | None:
    """Open ``root`` through an anchor chain, verifying every component."""
    anchor = _open_anchor(root)
    if anchor is None:
        return None
    handle, segments = anchor
    opened: list[int] = [handle]
    current = handle
    try:
        for index, segment in enumerate(segments):
            last = index == len(segments) - 1
            # Every segment here is a directory, INCLUDING the last one: this
            # opens a chain down to the root, and the root is a directory.  Passing
            # directory=not last asked for the final one as a file, and it failed
            # with no error text because the mismatch surfaces as an NTSTATUS.
            # DELETE is likewise never requested - there is nothing to delete at
            # the end of a directory chain, and asking for it on a directory
            # conflicts with other opens (STATUS_SHARING_VIOLATION).
            child = _open_relative(current, segment, directory=True)
            if child is None:
                return None
            opened.append(child)
            tag = _attribute_tag(child)
            if tag is None:
                return None
            attributes, _reparse = tag
            if attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
                return None
            if not last and not attributes & _FILE_ATTRIBUTE_DIRECTORY:
                return None
            current = child
        opened.pop()
        return current
    finally:
        for item in reversed(opened):
            _kernel32.CloseHandle(wintypes.HANDLE(item))


def _open_relative(parent: int, name: str, *, directory: bool, want_delete: bool = False) -> int | None:
    """Open ``name`` relative to ``parent`` without following reparse points.

    The name is a single component.  ``RootDirectory`` makes the kernel resolve it
    against the parent handle, so no component of the original path is walked a
    second time.
    """
    encoded = name.encode("utf-16-le")
    buffer = ctypes.create_unicode_buffer(name)
    us = _UNICODE_STRING(
        Length=len(encoded),
        MaximumLength=len(encoded) + 2,
        Buffer=ctypes.cast(buffer, wintypes.LPWSTR),
    )
    attrs = _OBJECT_ATTRIBUTES(
        Length=ctypes.sizeof(_OBJECT_ATTRIBUTES),
        RootDirectory=wintypes.HANDLE(parent),
        ObjectName=ctypes.pointer(us),
        Attributes=_OBJ_CASE_INSENSITIVE,
        SecurityDescriptor=None,
        SecurityQualityOfService=None,
    )
    iosb = _IO_STATUS_BLOCK()
    handle = wintypes.HANDLE()
    options = _FILE_OPEN_REPARSE_POINT | _FILE_SYNCHRONOUS_IO_NONALERT
    options |= _FILE_DIRECTORY_FILE if directory else _FILE_NON_DIRECTORY_FILE
    status = _ntdll.NtCreateFile(
        ctypes.byref(handle),
        # DELETE only for the FINAL component.  Requesting it on an
        # intermediate directory conflicts with other opens of that directory and
        # the kernel answers STATUS_SHARING_VIOLATION (0xC0000043).  Measured, not
        # guessed: on C:\Users every mask without DELETE succeeds and every mask
        # with it fails; an intermediate segment only needs to be traversable.
        ((_DELETE if want_delete else 0)
         | _FILE_READ_ATTRIBUTES | _SYNCHRONIZE | _FILE_TRAVERSE),
        ctypes.byref(attrs),
        ctypes.byref(iosb),
        None,
        _FILE_ATTRIBUTE_NORMAL,
        _FILE_SHARE_ALL,
        _FILE_OPEN,
        options,
        None,
        0,
    )
    # Keep the buffer alive until the call returns: the kernel reads the name
    # during NtCreateFile, and a collected buffer would leave it dangling.
    del buffer, us, attrs, iosb
    if not _status_ok(status):
        return None
    return handle.value


def _attribute_tag(handle: int) -> tuple[int, int] | None:
    info = _FILE_ATTRIBUTE_TAG_INFO()
    ok = _kernel32.GetFileInformationByHandleEx(
        wintypes.HANDLE(handle), 9, ctypes.byref(info), ctypes.sizeof(info)
    )
    if not ok:
        return None
    return info.FileAttributes, info.ReparseTag


def _delete_on_handle(handle: int) -> bool:
    info = _FILE_DISPOSITION_INFO(DeleteFile=True)
    return bool(
        _kernel32.SetFileInformationByHandle(
            wintypes.HANDLE(handle),
            _FILE_DISPOSITION_INFO_CLASS,
            ctypes.byref(info),
            ctypes.sizeof(info),
        )
    )


def unlink_by_handle(root: Path, segments: list[str]) -> bool | None:
    """Delete ``root / segments[0] / ...`` through a handle chain.

    Returns True when a plain file was deleted, False when the chain refused -
    a missing component, a reparse point, or the wrong object type - and ``None``
    on platforms where this implementation does not apply, so the caller can fall
    back rather than guess.
    """
    if _ntdll is None or not segments:
        return None

    opened: list[int] = []
    try:
        root_handle = _open_root(root)
        if root_handle is None:
            return False
        opened.append(root_handle)

        current = root_handle
        for index, segment in enumerate(segments):
            last = index == len(segments) - 1
            child = _open_relative(current, segment, directory=not last, want_delete=last)
            if child is None:
                return False
            opened.append(child)
            tag = _attribute_tag(child)
            if tag is None:
                return False
            attributes, _reparse_tag = tag
            if attributes & _FILE_ATTRIBUTE_REPARSE_POINT:
                # The object we opened is itself a link: refuse rather than
                # operate on whatever it points at.
                return False
            if last and attributes & _FILE_ATTRIBUTE_DIRECTORY:
                return False
            current = child

        return _delete_on_handle(current)
    finally:
        for handle in reversed(opened):
            _kernel32.CloseHandle(wintypes.HANDLE(handle))
