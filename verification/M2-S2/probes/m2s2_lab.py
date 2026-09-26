"""Shared helpers for the M2-S2 isolated security-verification probes.

Scope discipline
----------------
Research instrument, not product code: no import from ``src/**``, no
dependency beyond the CPython standard library, no product database, no user
library, no credentials, no model cache. Everything runs against synthetic
fixtures sealed to a temporary lab directory.

What this module prototypes (M2-S2 release, base ``67c3d56e``)
--------------------------------------------------------------
1. **S2-AC2 / S1-B11 release-condition (1)** -- a *reference resolver* that
   opens the file **once** and verifies identity + size + containment **from
   that handle** (``GetFileInformationByHandle`` / ``GetFinalPathNameByHandle``),
   then reads **only through that handle**. This is the open-then-verify
   direction M2-S1 §8.2 S1-B11 condition (1) asks for. It is a PROPOSAL-grade
   isolated prototype, **not** a product guarantee and **not** a product
   implementation (no IPC runtime, no Tauri command, no React consumer).
2. **S2-AC4 / S1-B12** -- a Core-side *random mapping-ID authority*: the
   caller-visible reference is an opaque random ID; only the Core table maps
   ID -> (scope, relative path). The table, its keys and the mapped paths must
   never appear in errors, logs or telemetry (threshold ruling T5.4).

Known limits (must be quoted with any PASS)
-------------------------------------------
- The handle identity used here is (volume serial, file index). On NTFS the
  file index can in principle be reused after deletion; the content digest
  check (signed at issue time, verified from the same handle) is the
  defence-in-depth layer that also covers an *in-place* equal-size rewrite by
  an adversary that already held a write handle (which identity and size
  alone cannot detect).
- The pre-open reparse walk is an early rejection with a check-then-use
  window of its own; the authoritative containment decision is derived from
  the opened handle, not from the walk.
- Everything is measured on one Windows host with Python↔Python probes. No
  Tauri/WebView, no MSIX/AppContainer packaging (S1-B8), no DACL/integrity
  level model (S1-B3) is exercised here -- those stay NOT_RUN/UNVERIFIED.
- ``TOCTOU_LIMIT_BYTES`` below is a *probe configuration* (like M2-S1's
  64 MiB), not a product threshold.
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
import secrets
import struct
import subprocess
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

#: M2-S1 probe limit kept for parity (NOT a product threshold).
MEDIA_LIMIT_BYTES = 64 * 1024 * 1024

#: Probe-configured controlled rejection limit for the TOCTOU resolver
#: scenarios (NOT a product threshold; chosen small so the over-limit
#: fixture is cheap). Product-level size budgets are ruled separately
#: (threshold ruling T1) and verified by runtime tasks.
TOCTOU_LIMIT_BYTES = 8 * 1024 * 1024

DEFAULT_LAB = Path(os.environ.get("TEMP", ".")) / "m2s2-lab"

SYNC_TIMEOUT_SECONDS = 30.0


class ProbeError(RuntimeError):
    """Typed probe/resolver failure. ``code`` is the stable selector."""

    def __init__(self, code: str, message: str = "") -> None:
        super().__init__(message or code)
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# deterministic synthetic fixtures (pure stdlib; method follows M2-S1)
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
    """Write a deterministic RGB noise PNG (deliberately incompressible)."""

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


def make_same_size_variant(source: Path, target: Path) -> dict:
    """Copy ``source`` then flip bytes, keeping the byte size identical (F-06 method)."""

    import shutil

    shutil.copyfile(source, target)
    with open(target, "r+b") as handle:
        head = bytearray(handle.read(4096))
        for index in range(0, len(head), 4):
            head[index] ^= 0xA5
        handle.seek(0)
        handle.write(bytes(head))
    source_size = source.stat().st_size
    target_size = target.stat().st_size
    return {
        "source_bytes": source_size,
        "variant_bytes": target_size,
        "same_size": source_size == target_size,
        "variant_sha256": sha256_file(target),
        "source_sha256": sha256_file(source),
    }


# --------------------------------------------------------------------------
# hashing
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


# --------------------------------------------------------------------------
# signed reference token (same wire family as M2-S1 route A, extended)
# --------------------------------------------------------------------------

_TOKEN_VERSION = "m2s2"


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
    expected_identity: list[int] | None = None,
    expected_size: int | None = None,
    expected_sha256: str | None = None,
) -> str:
    """Mint a signed, scoped, expiring resource reference.

    Wire form: ``m2s2.<base64url(json)>.<base64url(hmac-sha256)>``. As in
    M2-S1 F-01/R-002 this token is **signed but not opaque** -- the payload is
    readable without the key. Path confidentiality is *not* a property of this
    token; that requirement is served by the separate mapping-ID prototype
    (``MappingIdAuthority``) per threshold ruling T5.4.

    The ``expected_*`` fields record the file facts the Core captured at issue
    time; the handle-verified resolver re-checks them from the opened handle
    (S1-B11 release condition 1).
    """

    payload = {
        "v": 1,
        "rid": resource_id,
        "rel": rel_path,
        "scope": scope,
        "exp": round(expires_at, 3),
        "mode": mode,
        "ident": expected_identity,
        "size": expected_size,
        "sha256": expected_sha256,
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


# --------------------------------------------------------------------------
# Win32 primitives (ctypes, kernel32)
# --------------------------------------------------------------------------

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_DELETE = 0x00000004
OPEN_EXISTING = 3
FILE_FLAG_BACKUP_SEMANTICS = 0x02000000
FILE_FLAG_OPEN_REPARSE_POINT = 0x00200000
FILE_ATTRIBUTE_REPARSE_POINT = 0x400
INVALID_HANDLE_VALUE = w.HANDLE(-1).value
ERROR_SHARING_VIOLATION = 32
ERROR_ACCESS_DENIED = 5
ERROR_CANT_ACCESS_FILE = 1920

_K32 = ctypes.WinDLL("kernel32", use_last_error=True)
_K32.CreateFileW.restype = w.HANDLE
_K32.CreateFileW.argtypes = [
    w.LPCWSTR,
    w.DWORD,
    w.DWORD,
    ctypes.c_void_p,
    w.DWORD,
    w.DWORD,
    w.HANDLE,
]
_K32.CloseHandle.argtypes = [w.HANDLE]
_K32.CloseHandle.restype = w.BOOL
_K32.ReadFile.argtypes = [
    w.HANDLE,
    ctypes.c_void_p,
    w.DWORD,
    ctypes.POINTER(w.DWORD),
    ctypes.c_void_p,
]
_K32.ReadFile.restype = w.BOOL


class _BY_HANDLE_FILE_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("dwFileAttributes", w.DWORD),
        ("ftCreationTime", w.FILETIME),
        ("ftLastAccessTime", w.FILETIME),
        ("ftLastWriteTime", w.FILETIME),
        ("dwVolumeSerialNumber", w.DWORD),
        ("nFileSizeHigh", w.DWORD),
        ("nFileSizeLow", w.DWORD),
        ("nNumberOfLinks", w.DWORD),
        ("nFileIndexHigh", w.DWORD),
        ("nFileIndexLow", w.DWORD),
    ]


_K32.GetFileInformationByHandle.restype = w.BOOL
_K32.GetFileInformationByHandle.argtypes = [
    w.HANDLE,
    ctypes.POINTER(_BY_HANDLE_FILE_INFORMATION),
]


class _FILE_ATTRIBUTE_TAG_INFO(ctypes.Structure):
    _fields_ = [
        ("FileAttributes", w.DWORD),
        ("ReparseTag", w.DWORD),
    ]


_K32.GetFileInformationByHandleEx.restype = w.BOOL
_K32.GetFileInformationByHandleEx.argtypes = [
    w.HANDLE,
    w.DWORD,  # FileInformationClass
    ctypes.c_void_p,
    w.DWORD,
]

_FILE_ATTRIBUTE_TAG_INFO_CLASS = 9  # FileAttributeTagInfo
_K32.GetFinalPathNameByHandleW.restype = w.DWORD
_K32.GetFinalPathNameByHandleW.argtypes = [
    w.HANDLE,
    ctypes.c_wchar_p,
    w.DWORD,
    w.DWORD,
]


def win32_open_read(path: str | Path, *, share_mode: int = FILE_SHARE_READ) -> int:
    """Open ``path`` once with GENERIC_READ and the given share mode.

    Default share mode deliberately excludes FILE_SHARE_WRITE and
    FILE_SHARE_DELETE: after this open succeeds, a *new* writer open must fail
    with a sharing violation and the file cannot be renamed/replaced while
    held; an adversary that *already* holds a write handle makes this open
    fail closed (ERROR_SHARING_VIOLATION). Passing ``FILE_SHARE_WRITE`` models
    the availability-first mode (CRT ``open()`` parity, as in M2-S1 probe F)
    where an existing writer can keep writing -- the content digest layer must
    cover that window.
    """

    handle = _K32.CreateFileW(
        str(path),
        GENERIC_READ,
        share_mode,
        None,
        OPEN_EXISTING,
        FILE_FLAG_BACKUP_SEMANTICS,
        None,
    )
    if not handle or handle == INVALID_HANDLE_VALUE:
        error = ctypes.get_last_error()
        if error == ERROR_SHARING_VIOLATION:
            raise ProbeError("OPEN_FAILED_SHARING_VIOLATION", f"win32_error={error} path={path}")
        raise ProbeError("OPEN_FAILED", f"win32_error={error} path={path}")
    return int(handle)


def win32_open_write(path: str | Path, *, share_mode: int = 0) -> tuple[int | None, int]:
    """Try to open ``path`` for writing; return (handle|None, win32_error).

    ``share_mode`` lets an adversary pre-hold a write handle that still allows
    the resolver's read open (FILE_SHARE_READ | FILE_SHARE_WRITE) -- the
    worst-case window the content digest layer must cover.
    """

    handle = _K32.CreateFileW(
        str(path),
        GENERIC_WRITE,
        share_mode,
        None,
        OPEN_EXISTING,
        0,
        None,
    )
    if not handle or handle == INVALID_HANDLE_VALUE:
        return None, ctypes.get_last_error()
    return int(handle), 0


def win32_close(handle: int) -> None:
    _K32.CloseHandle(w.HANDLE(handle))


def win32_read_all(handle: int, *, on_first_block=None, block_size: int = 1 << 20) -> bytes:
    """Read the whole file through the given Win32 handle only."""

    chunks: list[bytes] = []
    read = w.DWORD(0)
    first = True
    while True:
        buffer = ctypes.create_string_buffer(block_size)
        ok = _K32.ReadFile(w.HANDLE(handle), buffer, block_size, ctypes.byref(read), None)
        if not ok:
            raise ProbeError("READ_FAILED", f"win32_error={ctypes.get_last_error()}")
        if read.value == 0:
            break
        chunks.append(buffer.raw[: read.value])
        if first and on_first_block is not None:
            on_first_block()
            first = False
    return b"".join(chunks)


def win32_write(handle: int, payload: bytes, offset: int = 0) -> None:
    """Write ``payload`` through ``handle`` at ``offset`` (attacker tooling)."""

    _K32.SetFilePointer.restype = ctypes.c_long
    _K32.SetFilePointer.argtypes = [w.HANDLE, ctypes.c_long, ctypes.c_void_p, w.DWORD]
    _K32.SetFilePointer(w.HANDLE(handle), offset, None, 0)  # FILE_BEGIN
    written = w.DWORD(0)
    ok = _K32.WriteFile(
        w.HANDLE(handle), payload, len(payload), ctypes.byref(written), None
    )
    if not ok:
        raise ProbeError("WRITE_FAILED", f"win32_error={ctypes.get_last_error()}")


def handle_identity(handle: int) -> dict:
    """(volume serial, file index) + size + attributes, from the handle."""

    info = _BY_HANDLE_FILE_INFORMATION()
    if not _K32.GetFileInformationByHandle(w.HANDLE(handle), ctypes.byref(info)):
        raise ProbeError("HANDLE_INFO_FAILED", f"win32_error={ctypes.get_last_error()}")
    return {
        "key": "volume_serial+file_index",
        "value": [
            int(info.dwVolumeSerialNumber),
            (int(info.nFileIndexHigh) << 32) | int(info.nFileIndexLow),
        ],
        "size": (int(info.nFileSizeHigh) << 32) | int(info.nFileSizeLow),
        "attributes": int(info.dwFileAttributes),
    }


def handle_final_path(handle: int) -> str:
    """Final (reparse-resolved) NT path of the object behind the handle."""

    length = _K32.GetFinalPathNameByHandleW(w.HANDLE(handle), None, 0, 0)
    if length == 0:
        raise ProbeError("FINAL_PATH_FAILED", f"win32_error={ctypes.get_last_error()}")
    buffer = ctypes.create_unicode_buffer(length + 1)
    written = _K32.GetFinalPathNameByHandleW(w.HANDLE(handle), buffer, length + 1, 0)
    if written == 0 or written > length:
        raise ProbeError("FINAL_PATH_FAILED", f"win32_error={ctypes.get_last_error()}")
    return buffer.value


def handle_is_reparse_point(handle: int) -> bool:
    tag_info = _FILE_ATTRIBUTE_TAG_INFO()
    ok = _K32.GetFileInformationByHandleEx(
        w.HANDLE(handle),
        _FILE_ATTRIBUTE_TAG_INFO_CLASS,
        ctypes.byref(tag_info),
        ctypes.sizeof(tag_info),
    )
    if not ok:
        raise ProbeError("HANDLE_TAG_FAILED", f"win32_error={ctypes.get_last_error()}")
    return bool(tag_info.FileAttributes & FILE_ATTRIBUTE_REPARSE_POINT)


def path_identity(path: str | Path) -> dict:
    """Snapshot identity/size/hash of a path (issue-time facts)."""

    handle = win32_open_read(path)
    try:
        identity = handle_identity(handle)
    finally:
        win32_close(handle)
    identity["sha256"] = sha256_file(path)
    return identity


# --------------------------------------------------------------------------
# open-then-verify-from-handle reference resolver (S2-AC2 / S1-B11 cond. 1)
# --------------------------------------------------------------------------


def _is_reparse_point_stat(stat_result: os.stat_result) -> bool:
    attributes = getattr(stat_result, "st_file_attributes", 0)
    return bool(attributes & FILE_ATTRIBUTE_REPARSE_POINT)


def normalized_windows_path(path: str | Path) -> str:
    """Casefolded, \\\\?\\-stripped absolute path for containment comparison."""

    text = str(path)
    if text.startswith("\\\\?\\UNC\\"):
        text = "\\\\" + text[8:]
    elif text.startswith("\\\\?\\"):
        text = text[4:]
    return os.path.normpath(text).casefold()


class HandleVerifiedResolver:
    """Resolve a signed reference by opening once and verifying from the handle.

    Verification order (deliberate, and itself part of the measurement):

    1. token: structure -> signature -> expiry -> revocation -> scope -> mode
       -> lexical safety -> pre-open reparse walk (early rejection, has its
       own race window);
    2. **open once** (GENERIC_READ / share mode per ``share_write`` /
       FILE_FLAG_BACKUP_SEMANTICS);
    3. verify **from that handle**: containment via
       ``GetFinalPathNameByHandle`` (path-level escape) -> file identity ->
       size (issue-time size, then probe limit) -> handle reparse tag;
    4. read **only through that handle**;
    5. content digest check against the issue-time digest (catches an
       equal-size in-place rewrite that identity+size cannot see);
    6. post-read identity re-check (file index must not have changed while
       the handle was held).

    PROPOSAL-grade isolated prototype for M2-S2 (S1-B11 release condition 1).
    Not a product implementation, not a product guarantee: packaging/sandbox
    (S1-B8) and DACL/integrity-level design (S1-B3) are outside this module.
    """

    #: Scope classes this resolver is willing to serve. ``user-source`` is
    #: deliberately absent (never reachable through the media channel).
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
        self.root_resolved = Path(scope_root).resolve()
        self.root_norm = normalized_windows_path(self.root_resolved)
        self.secret = secret
        self.revoked = set(revoked or ())
        self.clock = clock
        self.allowed_scopes = tuple(allowed_scopes or self.ALLOWED_SCOPES)
        self.trace: list[str] = []

    def issue(self, resource_id: str, rel_path: str, *, ttl_seconds: float, mode: str = "read") -> str:
        """Capture issue-time file facts and sign them into the reference."""

        rel_norm = rel_path.replace("\\", "/")
        target = self.root_resolved.joinpath(*rel_norm.split("/"))
        facts = path_identity(target)
        return mint_token(
            self.secret,
            resource_id=resource_id,
            rel_path=rel_path,
            scope="derived-read-only",
            expires_at=self.clock() + ttl_seconds,
            mode=mode,
            expected_identity=facts["value"],
            expected_size=facts["size"],
            expected_sha256=facts["sha256"],
        )

    def _lexical_checks(self, rel: str) -> list[str]:
        if Path(rel).is_absolute() or (len(rel) > 1 and rel[1] == ":"):
            raise ProbeError("REF_OUT_OF_SCOPE", "absolute path in reference")
        segments = rel.replace("\\", "/").split("/")
        if not segments or any(segment in ("", ".", "..") for segment in segments):
            raise ProbeError("REF_OUT_OF_SCOPE", "lexical traversal")
        return segments

    def _preopen_reparse_walk(self, segments: list[str]) -> None:
        """Early rejection of visible reparse components (has a race window;
        the authoritative containment check happens on the opened handle)."""

        probe = self.root_resolved
        for segment in segments:
            probe = probe / segment
            try:
                stat_result = probe.lstat()
            except OSError:
                return  # missing components: open will fail with REF_NOT_FOUND
            if _is_reparse_point_stat(stat_result):
                raise ProbeError("REF_REPARSE_POINT", "pre-open walk")

    def resolve_and_read(
        self,
        token: str,
        *,
        mode: str = "read",
        limit: int = TOCTOU_LIMIT_BYTES,
        hooks: dict[str, object] | None = None,
        share_write: bool = False,
    ) -> dict:
        """Open-then-verify-from-handle resolve + bounded read.

        ``share_write=False`` (default) opens with FILE_SHARE_READ only: an
        adversary already holding a write handle makes the open fail closed
        (OPEN_FAILED_SHARING_VIOLATION), and once open, no new writer can get
        in. ``share_write=True`` models the availability-first mode where a
        pre-existing writer may keep writing during the read -- the issue-time
        size/digest checks must then carry the load (T-16..T-18).
        """

        hooks = hooks or {}
        payload = read_token(self.secret, token)
        self.trace.append("token_ok")
        if float(payload.get("exp", 0)) <= self.clock():
            raise ProbeError("REF_EXPIRED")
        if payload.get("rid") in self.revoked:
            raise ProbeError("REF_REVOKED")
        if payload.get("scope") not in self.allowed_scopes:
            raise ProbeError("REF_SCOPE_DENIED", f"scope={payload.get('scope')!r}")
        if payload.get("mode") != "read" or mode != "read":
            raise ProbeError("REF_READ_ONLY")
        rel = str(payload.get("rel", ""))
        if not rel:
            raise ProbeError("REF_MALFORMED", "empty rel")
        segments = self._lexical_checks(rel)
        expected_identity = payload.get("ident")
        expected_size = payload.get("size")
        expected_sha256 = payload.get("sha256")
        if expected_identity is None or expected_size is None or expected_sha256 is None:
            raise ProbeError("REF_MALFORMED", "missing issue-time facts")
        self._preopen_reparse_walk(segments)
        candidate = self.root_resolved.joinpath(*segments)

        hook = hooks.get("before_open")
        if callable(hook):
            hook({"stage": "before_open", "rel": rel})

        open_share = FILE_SHARE_READ | FILE_SHARE_WRITE if share_write else FILE_SHARE_READ
        handle = win32_open_read(candidate, share_mode=open_share)
        try:
            hook = hooks.get("after_open_before_verify")
            if callable(hook):
                hook({"stage": "after_open_before_verify", "rel": rel})

            # containment first (path-level escape, e.g. a swapped junction),
            # then identity (file-level replacement), then size.
            final_path = handle_final_path(handle)
            final_norm = normalized_windows_path(final_path)
            if final_norm != self.root_norm and not final_norm.startswith(self.root_norm + os.sep):
                raise ProbeError("REF_OUT_OF_SCOPE", "containment from handle")

            observed = handle_identity(handle)
            if observed["value"] != list(expected_identity):
                raise ProbeError(
                    "FILE_IDENTITY_CHANGED",
                    f"expected={expected_identity} observed={observed['value']}",
                )
            if observed["size"] != int(expected_size):
                raise ProbeError(
                    "FILE_SIZE_CHANGED",
                    f"expected={expected_size} observed={observed['size']}",
                )
            if observed["size"] > limit:
                raise ProbeError(
                    "MEDIA_TOO_LARGE_BY_HANDLE",
                    f"size={observed['size']} limit={limit}",
                )
            if handle_is_reparse_point(handle):
                raise ProbeError("REF_REPARSE_POINT", "handle reparse tag")

            digest = hashlib.sha256()
            first = {"fired": False}

            def after_first_block() -> None:
                if first["fired"]:
                    return
                first["fired"] = True
                hook = hooks.get("during_read")
                if callable(hook):
                    hook({"stage": "during_read", "rel": rel})

            payload_bytes = win32_read_all(handle, on_first_block=after_first_block)
            total = len(payload_bytes)
            digest.update(payload_bytes)

            if total != int(expected_size):
                raise ProbeError(
                    "FILE_SIZE_CHANGED",
                    f"read_bytes={total} expected={expected_size}",
                )
            actual_sha256 = digest.hexdigest()
            if actual_sha256 != expected_sha256:
                raise ProbeError(
                    "CONTENT_DIGEST_MISMATCH",
                    f"expected={expected_sha256} observed={actual_sha256}",
                )
            post = handle_identity(handle)
            if post["value"] != observed["value"]:
                raise ProbeError("FILE_IDENTITY_CHANGED", "post-read re-check")
            return {
                "sha256": actual_sha256,
                "bytes_read": total,
                "identity": observed,
                "final_path": final_path,
                "expected_sha256": expected_sha256,
            }
        finally:
            win32_close(handle)


# --------------------------------------------------------------------------
# junction / symlink helpers
# --------------------------------------------------------------------------


def make_junction(link: Path, target: Path) -> dict:
    """Create a directory junction via ``mklink /J`` (no admin rights needed)."""

    if link.exists() or link.is_symlink():
        os.rmdir(link)
    created = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(link), str(target)],
        capture_output=True,
        timeout=30,
    )
    return {
        "link": str(link),
        "target": str(target),
        "created": created.returncode == 0 and link.exists(),
        "output": (created.stdout + created.stderr).decode("utf-8", errors="replace")[:200],
    }


def try_make_symlink_dir(link: Path, target: Path) -> dict:
    """Try to create a directory symbolic link; report (do not assume) availability."""

    if link.exists() or link.is_symlink():
        os.rmdir(link)
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        available = link.exists()
        error = None
    except OSError as error:
        available = False
        error = f"{error.winerror}: {error.strerror}" if hasattr(error, "winerror") else str(error)
    return {"link": str(link), "target": str(target), "created": available, "error": error}


# --------------------------------------------------------------------------
# Core-side random mapping-ID authority (S2-AC4 / S1-B12 / ruling T5.4)
# --------------------------------------------------------------------------


class MappingIdAuthority:
    """Issue opaque random IDs; resolve them from an internal table only.

    The caller-visible reference is ``m2id.v1.<192-bit random>``. It carries
    **no** path, resource-id, scope or payload bytes; only this table (Core
    side) maps an ID back to an entry. Per ruling T5.4 the ID is what the
    WebView layer would see; the Core<->host trusted-layer format is out of
    scope here.

    Redaction discipline (S1-B12 release condition): errors, the in-module
    log stream and telemetry events never contain the mapped relative path,
    the resource id, or the table contents. ``resource_id`` is treated as a
    resource identifier that must not be recoverable from caller-visible
    material either.

    PROPOSAL-grade isolated prototype. Not a product runtime component.
    """

    ID_PREFIX = "m2id"
    ID_RANDOM_BYTES = 24  # 192 bits of randomness

    def __init__(self, *, clock=time.time, default_ttl_seconds: float = 300.0) -> None:
        self.clock = clock
        self.default_ttl_seconds = default_ttl_seconds
        self._table: dict[str, dict] = {}
        # caller-visible surfaces the probes sweep for leakage
        self.visible_log: list[str] = []
        self.telemetry: list[dict] = []

    def issue(
        self,
        *,
        scope: str,
        rel_path: str,
        resource_id: str,
        ttl_seconds: float | None = None,
    ) -> str:
        opaque = f"{self.ID_PREFIX}.v1.{secrets.token_urlsafe(self.ID_RANDOM_BYTES)}"
        if opaque in self._table:  # pragma: no cover - 192-bit collision
            raise ProbeError("ID_COLLISION")
        self._table[opaque] = {
            "scope": scope,
            "rel": rel_path,
            "rid": resource_id,
            "expires_at": self.clock() + (ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds),
            "revoked": False,
        }
        self.visible_log.append(f"issue ttl={ttl_seconds if ttl_seconds is not None else self.default_ttl_seconds}")
        self.telemetry.append({"event": "mapping_issued"})
        return opaque

    def touch(self, opaque: str) -> None:
        """Sliding renewal (ruling T6): active consumption extends the TTL."""

        entry = self._table.get(opaque)
        if entry is None:
            raise ProbeError("REF_UNKNOWN_ID")
        entry["expires_at"] = self.clock() + self.default_ttl_seconds
        self.visible_log.append("touch ok")
        self.telemetry.append({"event": "mapping_touched"})

    def revoke(self, opaque: str) -> None:
        entry = self._table.get(opaque)
        if entry is None:
            raise ProbeError("REF_UNKNOWN_ID")
        entry["revoked"] = True
        self.visible_log.append("revoke ok")
        self.telemetry.append({"event": "mapping_revoked"})

    def resolve(self, opaque: str, *, mode: str = "read") -> dict:
        """Resolve an ID; raises typed errors that carry no mapping data."""

        entry = self._table.get(opaque)
        if entry is None:
            self.visible_log.append("resolve miss REF_UNKNOWN_ID")
            self.telemetry.append({"event": "mapping_resolve_failed", "code": "REF_UNKNOWN_ID"})
            raise ProbeError("REF_UNKNOWN_ID")
        if entry["revoked"]:
            self.visible_log.append("resolve REF_REVOKED")
            self.telemetry.append({"event": "mapping_resolve_failed", "code": "REF_REVOKED"})
            raise ProbeError("REF_REVOKED")
        if entry["expires_at"] <= self.clock():
            self.visible_log.append("resolve REF_EXPIRED")
            self.telemetry.append({"event": "mapping_resolve_failed", "code": "REF_EXPIRED"})
            raise ProbeError("REF_EXPIRED")
        if mode != "read":
            self.visible_log.append("resolve REF_READ_ONLY")
            self.telemetry.append({"event": "mapping_resolve_failed", "code": "REF_READ_ONLY"})
            raise ProbeError("REF_READ_ONLY")
        self.visible_log.append("resolve ok")
        self.telemetry.append({"event": "mapping_resolved"})
        # Return a copy that includes the mapping *to Core callers only*.
        return {
            "scope": entry["scope"],
            "rel": entry["rel"],
            "rid": entry["rid"],
            "expires_at": entry["expires_at"],
        }

    def table_size(self) -> int:
        return len(self._table)


# --------------------------------------------------------------------------
# result plumbing
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


def summary_of(results: list[dict]) -> dict:
    return {
        "pass": sum(1 for r in results if r["status"] == PASS),
        "fail": sum(1 for r in results if r["status"] == FAIL),
        "blocked": sum(1 for r in results if r["status"] == BLOCKED),
        "not_run": sum(1 for r in results if r["status"] == NOT_RUN),
    }
