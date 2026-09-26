"""Shared helpers for the M2-S1 isolated resource-channel probes.

Scope discipline
----------------
This module is a *research instrument*, not product code. It is deliberately
standalone: no import from ``src/**``, no dependency beyond the CPython
standard library, and no knowledge of the product database, repository or
managed layout. It exists so the Reviewer can re-run the same measurements.

Everything it measures is synthetic: PNG fixtures generated on demand into a
temporary lab directory, and a research-prototype "capability token" whose
only purpose is to expose permission/lifecycle behaviour.

Labels used in the results
--------------------------
``MEASURED``   the number came from this run on this host.
``PROPOSAL``   a design prototype implemented here only to be measurable.
``UNVERIFIED`` not exercised (say why in ``notes``).

The controlled rejection limit below is a *probe configuration*, not a product
threshold. The user has not supplied a large-media size budget, so no PASS
threshold is invented from it: exceeding it must produce a typed rejection
with bounded memory, and that is all it proves.
"""

from __future__ import annotations

import base64
import ctypes
import ctypes.wintypes as w
import hashlib
import hmac
import json
import os
import random
import struct
import sys
import time
import zlib
from pathlib import Path

# --------------------------------------------------------------------------
# status vocabulary
# --------------------------------------------------------------------------

PASS = "PASS"
FAIL = "FAIL"
BLOCKED = "BLOCKED"
NOT_RUN = "NOT_RUN"

#: Probe-configured controlled rejection limit (64 MiB). NOT a product
#: threshold; the user has not supplied a large-media size budget.
MEDIA_LIMIT_BYTES = 64 * 1024 * 1024

DEFAULT_LAB = Path(os.environ.get("TEMP", ".")) / "m2s1-lab"


class ProbeError(RuntimeError):
    """Typed probe failure. ``code`` is the stable selector, never the text."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# memory / time measurement
# --------------------------------------------------------------------------


class _PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", w.DWORD),
        ("PageFaultCount", w.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


_K32 = ctypes.WinDLL("kernel32", use_last_error=True)
_K32.GetCurrentProcess.restype = w.HANDLE
_K32.GetCurrentProcess.argtypes = []
_PSAPI = ctypes.WinDLL("psapi", use_last_error=True)
_PSAPI.GetProcessMemoryInfo.argtypes = [
    w.HANDLE,
    ctypes.POINTER(_PROCESS_MEMORY_COUNTERS),
    w.DWORD,
]
_PSAPI.GetProcessMemoryInfo.restype = w.BOOL


def memory_counters() -> dict:
    """Self-reported working-set/peak values for *this* process, in MiB.

    ``GetProcessMemoryInfo`` is used instead of WMI/CIM because CIM access is
    denied inside this workspace's file sandbox.
    """

    counters = _PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    ok = _PSAPI.GetProcessMemoryInfo(
        _K32.GetCurrentProcess(), ctypes.byref(counters), counters.cb
    )
    if not ok:
        raise ProbeError("MEMINFO_FAILED", f"GetProcessMemoryInfo error={ctypes.get_last_error()}")
    return {
        "working_set_mb": round(counters.WorkingSetSize / 1048576, 3),
        "peak_working_set_mb": round(counters.PeakWorkingSetSize / 1048576, 3),
        "pagefile_usage_mb": round(counters.PagefileUsage / 1048576, 3),
        "peak_pagefile_usage_mb": round(counters.PeakPagefileUsage / 1048576, 3),
    }


def peak_working_set_mb() -> float:
    return memory_counters()["peak_working_set_mb"]


class Timer:
    """Wall-clock stopwatch (perf_counter)."""

    def __enter__(self) -> "Timer":
        self._t0 = time.perf_counter()
        self.seconds = 0.0
        return self

    def __exit__(self, *exc: object) -> bool:
        self.seconds = time.perf_counter() - self._t0
        return False


# --------------------------------------------------------------------------
# hashing / formatting
# --------------------------------------------------------------------------


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def human_bytes(count: int) -> str:
    value = float(count)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.2f}{unit}"
        value /= 1024
    raise AssertionError("unreachable")


def base64_encoded_size(raw_size: int) -> int:
    """Exact base64 length (with padding) of ``raw_size`` bytes."""

    return 4 * ((raw_size + 2) // 3)


# --------------------------------------------------------------------------
# synthetic PNG fixtures (pure stdlib, deterministic)
# --------------------------------------------------------------------------


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + tag
        + data
        + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    )


def write_png(
    path: str | Path,
    width: int,
    height: int,
    *,
    channels: int = 3,
    seed: int = 0,
    level: int = 6,
) -> dict:
    """Write a deterministic RGB noise PNG (deliberately incompressible).

    Synthetic noise is the worst case for byte volume; a real scanned manga
    page compresses better, so the byte counts below are an *upper bound*
    relative to raw pixels rather than a claim about real page sizes.
    """

    if channels not in (3, 4):
        raise ProbeError("FIXTURE_UNSUPPORTED_CHANNELS", f"channels={channels}")
    colour_type = 2 if channels == 3 else 6
    rng = random.Random(seed)
    stride = width * channels
    compressor = zlib.compressobj(level)
    parts: list[bytes] = []
    for _ in range(height):
        parts.append(compressor.compress(b"\x00" + rng.randbytes(stride)))
    parts.append(compressor.flush())
    idat = b"".join(parts)
    del parts
    payload = b"".join(
        (
            b"\x89PNG\r\n\x1a\n",
            _png_chunk(
                b"IHDR",
                struct.pack(">IIBBBBB", width, height, 8, colour_type, 0, 0, 0),
            ),
            _png_chunk(b"IDAT", idat),
            _png_chunk(b"IEND", b""),
        )
    )
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return {
        "path": str(target),
        "width": width,
        "height": height,
        "channels": channels,
        "raw_pixel_bytes": width * height * channels,
        "png_bytes": len(payload),
        "sha256": sha256_bytes(payload),
    }


# --------------------------------------------------------------------------
# capability-scoped resource reference / token  (research prototype)
# --------------------------------------------------------------------------

_TOKEN_VERSION = "m2s1"


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def mint_token(
    secret: bytes,
    *,
    resource_id: str,
    rel_path: str,
    scope: str,
    expires_at: float,
    mode: str = "read",
) -> str:
    """Mint an opaque, signed, scoped, expiring resource reference.

    PROPOSAL only: the wire shape is a research prototype so the permission
    and lifecycle behaviour can be measured. It is not an M2-C1 Contract
    decision and no product runtime implements it.
    """

    payload = {
        "v": 1,
        "rid": resource_id,
        "rel": rel_path,
        "scope": scope,
        "exp": round(expires_at, 3),
        "mode": mode,
    }
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret, body, hashlib.sha256).digest()
    return f"{_TOKEN_VERSION}.{_b64url(body)}.{_b64url(signature)}"


def read_token(secret: bytes, token: str) -> dict:
    """Verify structure + signature; return the payload."""

    parts = token.split(".")
    if len(parts) != 3 or parts[0] != _TOKEN_VERSION:
        raise ProbeError("REF_MALFORMED")
    try:
        body = _b64url_decode(parts[1])
        signature = _b64url_decode(parts[2])
    except Exception as error:  # noqa: BLE001 - any decode failure is malformed
        raise ProbeError("REF_MALFORMED", str(error)) from error
    expected = hmac.new(secret, body, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ProbeError("REF_SIGNATURE_INVALID")
    try:
        payload = json.loads(body.decode("utf-8"))
    except Exception as error:  # noqa: BLE001
        raise ProbeError("REF_MALFORMED", str(error)) from error
    return payload


def _is_reparse_point(stat_result: os.stat_result) -> bool:
    attributes = getattr(stat_result, "st_file_attributes", 0)
    if attributes:
        return bool(attributes & 0x400)  # FILE_ATTRIBUTE_REPARSE_POINT
    return False


class ScopedResourceResolver:
    """Resolve a scoped token to a file path, enforcing the scope boundary.

    Order of checks is deliberate and is itself part of the measurement:
    structure -> signature -> expiry -> revocation -> scope class -> mode ->
    lexical safety -> containment -> reparse walk -> existence.
    """

    #: Scope classes this resolver is willing to serve. ``user-source`` is
    #: deliberately absent: a real user source file is a different lifecycle
    #: and security class and must never be reachable through the media
    #: channel's reference type.
    ALLOWED_SCOPES = ("derived-read-only", "managed-read-only")

    def __init__(
        self,
        scope_root: str | Path,
        secret: bytes,
        *,
        revoked: set[str] | None = None,
        clock=time.time,
        allowed_scopes: tuple[str, ...] | None = None,
    ) -> None:
        self.root = Path(scope_root).resolve()
        self.secret = secret
        self.revoked = set(revoked or ())
        self.clock = clock
        self.allowed_scopes = tuple(allowed_scopes or self.ALLOWED_SCOPES)
        self.trace: list[str] = []

    def issue(self, resource_id: str, rel_path: str, *, ttl_seconds: float, mode: str = "read") -> str:
        return mint_token(
            self.secret,
            resource_id=resource_id,
            rel_path=rel_path,
            scope="derived-read-only",
            expires_at=self.clock() + ttl_seconds,
            mode=mode,
        )

    def resolve(self, token: str, *, mode: str = "read") -> Path:
        payload = read_token(self.secret, token)
        self.trace.append(f"payload={payload}")
        if float(payload.get("exp", 0)) <= self.clock():
            raise ProbeError("REF_EXPIRED")
        if payload.get("rid") in self.revoked:
            raise ProbeError("REF_REVOKED")
        if payload.get("scope") not in self.allowed_scopes:
            raise ProbeError("REF_SCOPE_DENIED", f"scope={payload.get('scope')!r}")
        if payload.get("mode") != "read" or mode != "read":
            raise ProbeError("REF_READ_ONLY", f"token_mode={payload.get('mode')} request_mode={mode}")
        rel = str(payload.get("rel", ""))
        if not rel:
            raise ProbeError("REF_MALFORMED", "empty rel")
        if Path(rel).is_absolute() or (len(rel) > 1 and rel[1] == ":"):
            raise ProbeError("REF_OUT_OF_SCOPE", f"absolute={rel!r}")
        # lexical check before touching the filesystem
        segments = rel.replace("\\", "/").split("/")
        if any(segment in ("", ".", "..") for segment in segments):
            raise ProbeError("REF_OUT_OF_SCOPE", f"lexical_traversal={rel!r}")
        candidate = (self.root / Path(*segments)).resolve()
        try:
            candidate.relative_to(self.root)
        except ValueError as error:
            raise ProbeError("REF_OUT_OF_SCOPE", f"containment={candidate}") from error
        # reparse walk on the *unresolved* path (junction/symlink escape)
        probe = self.root
        for segment in segments:
            probe = probe / segment
            try:
                stat_result = probe.lstat()
            except OSError:
                break
            if _is_reparse_point(stat_result):
                raise ProbeError("REF_REPARSE_POINT", f"at {probe}")
        if not candidate.is_file():
            raise ProbeError("REF_NOT_FOUND", str(candidate))
        return candidate


def read_file_bounded(path: str | Path, limit: int = MEDIA_LIMIT_BYTES) -> tuple[bytes, dict]:
    """Read a file only if its size is within the controlled limit.

    The size is checked *before* allocation so an over-limit resource is
    rejected without allocating its bytes (AC3 "controlled rejection").
    """

    size = os.path.getsize(path)
    if size > limit:
        raise ProbeError(
            "MEDIA_TOO_LARGE",
            f"size={size} limit={limit}",
        )
    with open(path, "rb") as handle:
        return handle.read(), {"size": size, "limit": limit}


# --------------------------------------------------------------------------
# Windows section / handle primitives (ctypes)
# --------------------------------------------------------------------------

INVALID_HANDLE_VALUE = w.HANDLE(-1).value
PAGE_READWRITE = 0x04
FILE_MAP_READ = 0x0004
FILE_MAP_WRITE = 0x0002
FILE_MAP_ALL_ACCESS = 0x000F001F
PROCESS_DUP_HANDLE = 0x0040
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
DUPLICATE_SAME_ACCESS = 0x00000002
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
ERROR_ACCESS_DENIED = 5
ERROR_ALREADY_EXISTS = 183

_K32.CreateFileMappingW.restype = w.HANDLE
_K32.CreateFileMappingW.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD, w.DWORD, w.DWORD, w.LPCWSTR]
_K32.OpenFileMappingW.restype = w.HANDLE
_K32.OpenFileMappingW.argtypes = [w.DWORD, w.BOOL, w.LPCWSTR]
_K32.MapViewOfFile.restype = ctypes.c_void_p
_K32.MapViewOfFile.argtypes = [w.HANDLE, w.DWORD, w.DWORD, w.DWORD, ctypes.c_size_t]
_K32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
_K32.UnmapViewOfFile.restype = w.BOOL
_K32.CloseHandle.argtypes = [w.HANDLE]
_K32.CloseHandle.restype = w.BOOL
_K32.OpenProcess.restype = w.HANDLE
_K32.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
_K32.DuplicateHandle.argtypes = [
    w.HANDLE,
    w.HANDLE,
    w.HANDLE,
    ctypes.POINTER(w.HANDLE),
    w.DWORD,
    w.BOOL,
    w.DWORD,
]
_K32.DuplicateHandle.restype = w.BOOL
_K32.CreateFileW.restype = w.HANDLE
_K32.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, ctypes.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
_K32.WriteFile.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD), ctypes.c_void_p]
_K32.WriteFile.restype = w.BOOL
_K32.ReadFile.argtypes = [w.HANDLE, ctypes.c_void_p, w.DWORD, ctypes.POINTER(w.DWORD), ctypes.c_void_p]
_K32.ReadFile.restype = w.BOOL
_K32.GetCurrentProcessId.restype = w.DWORD


def create_section(size: int, *, name: str | None = None) -> int:
    """Create a pagefile-backed section (anonymous when ``name`` is None)."""

    handle = _K32.CreateFileMappingW(
        w.HANDLE(INVALID_HANDLE_VALUE), None, PAGE_READWRITE, size >> 32, size & 0xFFFFFFFF, name
    )
    if not handle:
        raise ProbeError("SECTION_CREATE_FAILED", f"error={ctypes.get_last_error()} name={name!r}")
    return int(handle)


def open_section(name: str, access: int = FILE_MAP_READ) -> int:
    handle = _K32.OpenFileMappingW(access, False, name)
    if not handle:
        raise ProbeError("SECTION_OPEN_FAILED", f"error={ctypes.get_last_error()} name={name!r}")
    return int(handle)


def map_section(handle: int, access: int = FILE_MAP_ALL_ACCESS) -> int:
    pointer = _K32.MapViewOfFile(w.HANDLE(handle), access, 0, 0, 0)
    if not pointer:
        raise ProbeError("SECTION_MAP_FAILED", f"error={ctypes.get_last_error()}")
    return int(pointer)


def unmap_section(pointer: int) -> None:
    _K32.UnmapViewOfFile(ctypes.c_void_p(pointer))


def close_handle(handle: int) -> None:
    _K32.CloseHandle(w.HANDLE(handle))


def open_process(pid: int, access: int = PROCESS_DUP_HANDLE) -> int:
    handle = _K32.OpenProcess(access, False, pid)
    if not handle:
        raise ProbeError("OPEN_PROCESS_DENIED", f"error={ctypes.get_last_error()} pid={pid} access={access}")
    return int(handle)


def duplicate_from_process(source_pid: int, source_handle: int, access: int = PROCESS_DUP_HANDLE) -> int:
    """Duplicate a handle *out of* ``source_pid`` into this process."""

    process = open_process(source_pid, access)
    new_handle = w.HANDLE()
    ok = _K32.DuplicateHandle(
        w.HANDLE(process),
        w.HANDLE(source_handle),
        _K32.GetCurrentProcess(),
        ctypes.byref(new_handle),
        0,
        False,
        DUPLICATE_SAME_ACCESS,
    )
    error = ctypes.get_last_error()
    close_handle(process)
    if not ok:
        raise ProbeError("DUPLICATE_HANDLE_FAILED", f"error={error}")
    return int(new_handle.value)


def duplicate_into_process(target_pid: int, handle: int, access: int = PROCESS_DUP_HANDLE) -> int:
    """Duplicate *this* process's ``handle`` into ``target_pid``.

    This is the direction a resource-owning Core would use to hand a section
    to a host: the returned value is valid in the target's handle table.
    """

    target = open_process(target_pid, access)
    new_handle = w.HANDLE()
    ok = _K32.DuplicateHandle(
        _K32.GetCurrentProcess(),
        w.HANDLE(handle),
        w.HANDLE(target),
        ctypes.byref(new_handle),
        0,
        False,
        DUPLICATE_SAME_ACCESS,
    )
    error = ctypes.get_last_error()
    close_handle(target)
    if not ok:
        raise ProbeError("DUPLICATE_INTO_TARGET_FAILED", f"error={error}")
    return int(new_handle.value)


def section_write(pointer: int, payload: bytes) -> None:
    ctypes.memmove(ctypes.c_void_p(pointer), payload, len(payload))


def section_read(pointer: int, length: int, offset: int = 0) -> bytes:
    return ctypes.string_at(ctypes.c_void_p(pointer + offset), length)


def read_only_handle_write_probe(path: str | Path) -> dict:
    """Open a file with GENERIC_READ only and try to write through the handle.

    This is a real Windows access-mode check (not a Python-level guard): it
    shows the OS refuses a write through a read-only handle. It does *not*
    prove source-file protection, because the same user can open the same
    file writable -- see the research report's threat model.
    """

    handle = _K32.CreateFileW(
        str(path),
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if not handle:
        raise ProbeError("CREATE_FILE_FAILED", f"error={ctypes.get_last_error()}")
    written = w.DWORD(0)
    payload = b"denied"
    ok = _K32.WriteFile(w.HANDLE(handle), payload, len(payload), ctypes.byref(written), None)
    error = ctypes.get_last_error()
    close_handle(int(handle))
    return {
        "read_only_handle_created": True,
        "write_via_read_only_handle_ok": bool(ok),
        "write_error_code": error if not ok else 0,
        "write_error_is_access_denied": (not ok) and error == ERROR_ACCESS_DENIED,
    }


def readonly_mmap_write_probe(path: str | Path) -> dict:
    """Attempt a write through a read-only file mapping."""

    import mmap as _mmap

    result: dict = {}
    with open(path, "rb") as handle:
        mapping = _mmap.mmap(handle.fileno(), 0, access=_mmap.ACCESS_READ)
        try:
            mapping[0:1] = b"x"
            result["write_via_readonly_mapping_ok"] = True
            result["error_type"] = None
        except Exception as error:  # noqa: BLE001 - the exception type is the datum
            result["write_via_readonly_mapping_ok"] = False
            result["error_type"] = type(error).__name__
            result["error_text"] = str(error)
        finally:
            mapping.close()
    return result


# --------------------------------------------------------------------------
# json plumbing
# --------------------------------------------------------------------------


def emit(result: dict, out_path: str | Path | None = None) -> int:
    text = json.dumps(result, indent=2, ensure_ascii=False)
    print(text)
    if out_path:
        target = Path(out_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    return 0


def lab_root(override: str | None = None) -> Path:
    root = Path(override) if override else DEFAULT_LAB
    root.mkdir(parents=True, exist_ok=True)
    return root


def probe_error_result(error: ProbeError, stage: str) -> dict:
    return {
        "status": FAIL,
        "stage": stage,
        "error_code": error.code,
        "error_message": error.message,
    }


def python_exe() -> str:
    return sys.executable
