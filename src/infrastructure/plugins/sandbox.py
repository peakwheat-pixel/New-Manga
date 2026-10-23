"""Windows AppContainer sandbox for plugin hook subprocesses (PLUGIN-RUNTIME-SANDBOX-1).

Design (user authorization 2026-10-23, option 1; accepted approach A):

* every plugin gets its OWN AppContainer profile by default
  (``NewMangaPlugin-<sha256(plugin_id)[:12]>``), so plugin A cannot read plugin
  B's directory even if B's directory was granted earlier; the read-only
  interpreter ACL is granted once per profile SID (cached); a shared profile is
  available only as an explicit opt-in (``shared_profile=True``) for low-cost
  scenarios;
* the container is granted read/execute on that plugin's directory and on the
  Python interpreter runtime only (read-only), plus traverse-only grants on the
  ancestors of the data root so the process can reach its own directory;
* the hook subprocess is started inside the container via ``CreateProcessW``
  with ``PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES``; a Job Object with
  ``KILL_ON_JOB_CLOSE`` owns the process tree;
* with no capability SIDs the container has NO network access and NO file
  access outside the explicitly granted ACLs (verified by
  ``tests/infrastructure/test_plugin_sandbox.py``);
* optional capability SIDs (``internetClient``) are only attached when a future
  release starts loading plugins with declared ``network`` permission — the
  manifest layer still rejects every non-empty ``permissions`` list.

Any failure to set up or launch the sandbox is FAIL-CLOSED: ``SandboxError`` is
raised and the caller turns it into ``PLUGIN_HOOK_UNAVAILABLE``; a hook is never
executed unsandboxed by accident.
"""

from __future__ import annotations

import ctypes
import ctypes.wintypes as w
import hashlib
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

_IS_WINDOWS = os.name == "nt"

if _IS_WINDOWS:  # pragma: no branch - import-time platform switch
    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _userenv = ctypes.WinDLL("userenv", use_last_error=True)
    _advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)

    _PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES = 0x20009
    _EXTENDED_STARTUPINFO_PRESENT = 0x00080000
    _CREATE_NO_WINDOW = 0x08000000
    _CREATE_UNICODE_ENVIRONMENT = 0x00000400
    _CREATE_SUSPENDED = 0x00000004
    _INFINITE = 0xFFFFFFFF
    _WAIT_TIMEOUT = 258
    _STD_INPUT_HANDLE = -10
    _STD_OUTPUT_HANDLE = -11
    _STARTF_USESTDHANDLES = 0x00000100
    _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9
    _SE_GROUP_ENABLED = 0x00000004
    _LMEM_FIXED = 0x0040
    _ERROR_ALREADY_EXISTS_HRESULT = -2147024713  # 0x800700B7

    class _SID_AND_ATTRIBUTES(ctypes.Structure):
        _fields_ = [("Sid", ctypes.c_void_p), ("Attributes", w.DWORD)]

    class _SECURITY_CAPABILITIES(ctypes.Structure):
        _fields_ = [
            ("AppContainerSid", ctypes.c_void_p),
            ("Capabilities", ctypes.POINTER(_SID_AND_ATTRIBUTES)),
            ("CapabilityCount", w.DWORD),
            ("Reserved", w.DWORD),
        ]

    class _STARTUPINFOW(ctypes.Structure):
        _fields_ = [
            ("cb", w.DWORD),
            ("lpReserved", w.LPWSTR),
            ("lpDesktop", w.LPWSTR),
            ("lpTitle", w.LPWSTR),
            ("dwX", w.DWORD),
            ("dwY", w.DWORD),
            ("dwXSize", w.DWORD),
            ("dwYSize", w.DWORD),
            ("dwXCountChars", w.DWORD),
            ("dwYCountChars", w.DWORD),
            ("dwFillAttribute", w.DWORD),
            ("dwFlags", w.DWORD),
            ("wShowWindow", w.WORD),
            ("cbReserved2", w.WORD),
            ("lpReserved2", ctypes.c_void_p),
            ("hStdInput", w.HANDLE),
            ("hStdOutput", w.HANDLE),
            ("hStdError", w.HANDLE),
        ]

    class _STARTUPINFOEXW(ctypes.Structure):
        _fields_ = [
            ("StartupInfo", _STARTUPINFOW),
            ("lpAttributeList", ctypes.c_void_p),
        ]

    class _PROCESS_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("hProcess", w.HANDLE),
            ("hThread", w.HANDLE),
            ("dwProcessId", w.DWORD),
            ("dwThreadId", w.DWORD),
        ]

    class _JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", w.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", w.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", w.DWORD),
            ("SchedulingClass", w.DWORD),
        ]

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class _JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _JOBOBJECT_BASIC_LIMIT_INFORMATION),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    _k32.ConvertStringSidToSidW = _advapi32.ConvertStringSidToSidW
    _k32.LocalAlloc.restype = ctypes.c_void_p
    _k32.LocalAlloc.argtypes = [w.DWORD, ctypes.c_size_t]
    _k32.LocalFree.restype = ctypes.c_void_p
    _k32.LocalFree.argtypes = [ctypes.c_void_p]
    _k32.CreateProcessW.restype = w.BOOL
    _k32.CreateProcessW.argtypes = [
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
        w.BOOL,
        w.DWORD,
        ctypes.c_void_p,
        ctypes.c_wchar_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    _k32.CreateAppContainerProfile = _userenv.CreateAppContainerProfile
    _k32.CreateAppContainerProfile.restype = ctypes.c_long
    _k32.CreateAppContainerProfile.argtypes = [
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_wchar_p,
        ctypes.c_void_p,
        w.DWORD,
        ctypes.POINTER(ctypes.c_void_p),
    ]
    _derive = _userenv.DeriveAppContainerSidFromAppContainerName
    _derive.restype = ctypes.c_long
    _derive.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_void_p)]


CAPABILITY_SIDS = {
    "network": "S-1-15-3-1",  # internetClient
}

MAX_PROFILES = 64
_PROFILE_NAME_PREFIX = "NewMangaPlugin"


class SandboxError(RuntimeError):
    """Typed, non-sensitive sandbox failure (fail-closed callers)."""


@dataclass
class SandboxResult:
    returncode: int
    stdout: bytes
    timed_out: bool = False


@dataclass
class _GrantCache:
    """Per-process cache of granted paths so repeated hooks stay cheap."""

    granted: set[tuple[str, str]] = field(default_factory=set)


class AppContainerSandbox:
    """AppContainer + Job Object execution for hook subprocesses (Windows only)."""

    def __init__(
        self,
        *,
        interpreter: str | None = None,
        anchors: tuple[str, ...] = (),
        capability_names: tuple[str, ...] = (),
        shared_profile: bool = False,
    ) -> None:
        self._interpreter = interpreter or sys.executable
        self._anchors = tuple(str(item) for item in anchors if item)
        self._capability_names = tuple(capability_names)
        self._shared_profile = shared_profile
        self._profiles: dict[str, str] = {}
        self._grants = _GrantCache()
        self._interpreter_sids: set[str] = set()
        self._closed = False

    @property
    def shared_profile(self) -> bool:
        """True when every plugin shares one AppContainer (opt-in only)."""
        return self._shared_profile

    # -- capability ---------------------------------------------------------
    @property
    def available(self) -> bool:
        if not _IS_WINDOWS or self._closed:
            return False
        return Path(self._interpreter).is_file()

    @property
    def capabilities(self) -> tuple[str, ...]:
        return self._capability_names

    # -- profile / ACL ------------------------------------------------------
    def _profile_name(self, plugin_id: str) -> str:
        if self._shared_profile:
            return _PROFILE_NAME_PREFIX + "Sandbox"
        # Per-plugin container: plugin A's SID never appears in plugin B's ACLs,
        # so a compromised plugin cannot read a sibling's directory.
        digest = hashlib.sha256(plugin_id.encode("utf-8")).hexdigest()[:12]
        return f"{_PROFILE_NAME_PREFIX}-{digest}"

    def _ensure_profile(self, plugin_id: str) -> str:
        cache_key = "__shared__" if self._shared_profile else plugin_id
        if cache_key in self._profiles:
            return self._profiles[cache_key]
        if len(self._profiles) >= MAX_PROFILES:
            raise SandboxError("too many plugin sandbox profiles")
        name = self._profile_name(plugin_id)
        sid = ctypes.c_void_p()
        hr = _userenv.CreateAppContainerProfile(
            ctypes.c_wchar_p(name),
            ctypes.c_wchar_p(name),
            ctypes.c_wchar_p("New Manga plugin sandbox"),
            None,
            w.DWORD(0),
            ctypes.byref(sid),
        )
        if hr == _ERROR_ALREADY_EXISTS_HRESULT:
            sid = ctypes.c_void_p()
            hr = _derive(ctypes.c_wchar_p(name), ctypes.byref(sid))
        if hr != 0 or not sid:
            raise SandboxError("cannot create the plugin AppContainer profile")
        out = ctypes.c_wchar_p()
        if not _advapi32.ConvertSidToStringSidW(sid, ctypes.byref(out)):
            raise SandboxError("cannot resolve the plugin AppContainer SID")
        self._profiles[cache_key] = out.value
        return out.value

    def _grant(self, path: str, sid: str, rights: str) -> None:
        key = (path, sid)
        if key in self._grants.granted:
            return
        completed = subprocess.run(
            ["icacls", path, "/grant", f"*{sid}:{rights}"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise SandboxError(f"cannot grant sandbox access to {Path(path).name}")
        self._grants.granted.add(key)

    @staticmethod
    def _traversal_chain(plugin_root: Path) -> tuple[Path, ...]:
        """Directories that need traverse/read so the child can reach its own
        folder. Deliberately stops at the data root's parent: probing showed
        that granting ACLs on the users directory or the drive root needs
        elevated rights and would hang the hook; AppContainer already has
        default traversal there.
        """
        chain: list[Path] = []
        current = plugin_root.parent
        for _ in range(2):  # data root + its immediate parent
            if current.parent == current:
                break
            chain.append(current)
            current = current.parent
        return tuple(chain)

    def _prepare_interpreter(self, sid: str) -> None:
        if sid in self._interpreter_sids:
            return
        interpreter = Path(self._interpreter).resolve()
        root = interpreter.parent
        self._grant(str(interpreter), sid, "(RX)")
        self._grant(str(root), sid, "(OI)(CI)(RX)")
        for sub in ("DLLs", "Lib"):
            candidate = root / sub
            if candidate.is_dir():
                self._grant(str(candidate), sid, "(OI)(CI)(RX)")
        self._interpreter_sids.add(sid)

    def prepare_plugin(
        self,
        plugin_id: str,
        plugin_root: str | Path,
        *,
        runner_path: str | Path | None = None,
        interpreter: str | None = None,
    ) -> None:
        """Idempotently grant the container access to its own plugin files.

        Only the plugin directory (RX, recursive), the Python runtime (RX) and
        the runner *file* (RX, no directory grant) are exposed; ancestors of the
        plugin directory get traverse-only ACLs so the child can reach its own
        directory without listing sibling folders.
        """
        if interpreter is not None:
            self._interpreter = interpreter
        if not self.available:
            raise SandboxError("sandbox is unavailable")
        sid = self._ensure_profile(plugin_id)
        root = Path(plugin_root).resolve()
        self._prepare_interpreter(sid)
        self._grant(str(root), sid, "(OI)(CI)(RX)")
        for ancestor in self._traversal_chain(root):
            self._grant(str(ancestor), sid, "(X)")
        for anchor in self._anchors:
            self._grant(anchor, sid, "(X)")
        if runner_path is not None:
            self._grant(str(Path(runner_path).resolve()), sid, "(RX)")

    # -- execution ----------------------------------------------------------
    def run(
        self,
        plugin_id: str,
        argv: list[str],
        *,
        cwd: str | Path,
        payload: bytes,
        timeout_seconds: float,
        max_output_bytes: int,
        interpreter: str | None = None,
        capabilities: tuple[str, ...] = (),
    ) -> SandboxResult:
        if not self.available:
            raise SandboxError("sandbox is unavailable")
        if interpreter is not None:
            self._interpreter = interpreter
        sid = self._ensure_profile(plugin_id)
        self._prepare_interpreter(sid)
        _k32.CreatePipe.restype = w.BOOL
        read_stdin, write_stdin = w.HANDLE(), w.HANDLE()
        read_stdout, write_stdout = w.HANDLE(), w.HANDLE()
        security = ctypes.c_void_p(0)
        if not _k32.CreatePipe(ctypes.byref(read_stdin), ctypes.byref(write_stdin), security, 0):
            raise SandboxError("cannot create the sandbox stdin pipe")
        if not _k32.CreatePipe(ctypes.byref(read_stdout), ctypes.byref(write_stdout), security, 0):
            raise SandboxError("cannot create the sandbox stdout pipe")
        _k32.SetHandleInformation(read_stdin, 1, 1)  # HANDLE_FLAG_INHERIT
        _k32.SetHandleInformation(write_stdout, 1, 1)

        job = _k32.CreateJobObjectW(None, None)
        if not job:
            raise SandboxError("cannot create the sandbox job object")
        # The job handle must NOT be inherited by the child: an inherited job
        # handle keeps the job alive after the Core closes its own handle and
        # would defeat KILL_ON_JOB_CLOSE (the whole tree must die on close).
        _k32.SetHandleInformation(job, 1, 0)
        limits = _JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        limits.BasicLimitInformation.LimitFlags = _JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if not _k32.SetInformationJobObject(
            job,
            _JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(limits),
            ctypes.sizeof(limits),
        ):
            raise SandboxError("cannot configure the sandbox job object")

        si = _STARTUPINFOEXW()
        si.StartupInfo.cb = ctypes.sizeof(_STARTUPINFOEXW)
        size = ctypes.c_size_t(0)
        _k32.InitializeProcThreadAttributeList(None, 1, 0, ctypes.byref(size))
        buffer = ctypes.create_string_buffer(max(size.value, 1))
        attribute_list = ctypes.cast(buffer, ctypes.c_void_p)
        if not _k32.InitializeProcThreadAttributeList(
            attribute_list, 1, 0, ctypes.byref(size)
        ):
            raise SandboxError("cannot initialize the sandbox process attributes")
        security_capabilities, cleanup_pointers = _build_security_capabilities(
            self._sid_pointer(sid), capabilities
        )
        capabilities = security_capabilities
        if not _k32.UpdateProcThreadAttribute(
            attribute_list,
            0,
            _PROC_THREAD_ATTRIBUTE_SECURITY_CAPABILITIES,
            ctypes.byref(capabilities),
            ctypes.sizeof(capabilities),
            None,
            None,
        ):
            raise SandboxError("cannot attach the AppContainer capability")
        si.lpAttributeList = attribute_list
        si.StartupInfo.dwFlags = _STARTF_USESTDHANDLES
        si.StartupInfo.hStdInput = read_stdin
        si.StartupInfo.hStdOutput = write_stdout
        si.StartupInfo.hStdError = write_stdout

        process_info = _PROCESS_INFORMATION()
        command_line = ctypes.c_wchar_p(_command_line(argv))
        environment_block = _environment_block(_child_environment())
        environment_pointer = ctypes.cast(environment_block, ctypes.c_void_p)
        created = _k32.CreateProcessW(
            ctypes.c_wchar_p(argv[0]),
            command_line,
            None,
            None,
            True,
            _EXTENDED_STARTUPINFO_PRESENT | _CREATE_NO_WINDOW | _CREATE_UNICODE_ENVIRONMENT | _CREATE_SUSPENDED,
            environment_pointer,
            ctypes.c_wchar_p(str(cwd)),
            ctypes.byref(si),
            ctypes.byref(process_info),
        )
        for pointer in cleanup_pointers:
            _k32.LocalFree(ctypes.c_void_p(pointer))
        cleanup_pointers = []
        if not created:
            raise SandboxError(
                f"cannot start the sandboxed hook process (WinError {ctypes.get_last_error()})"
            )
        _k32.CloseHandle(read_stdin)
        _k32.CloseHandle(write_stdout)
        if not _k32.AssignProcessToJobObject(job, process_info.hProcess):
            _k32.TerminateProcess(process_info.hProcess, 1)
            _k32.CloseHandle(process_info.hProcess)
            _k32.CloseHandle(process_info.hThread)
            _k32.CloseHandle(job)
            raise SandboxError("cannot attach the hook process to the sandbox job")
        # The process was created suspended so nothing (including grandchildren)
        # can start before it is inside the job; resume once attached.
        _k32.ResumeThread(process_info.hThread)

        timed_out = False
        stdout = b""
        try:
            # Non-blocking pump: stdin first (small payload), then poll stdout
            # with PeekNamedPipe so a silent/hanging child can never block the
            # Core's reader thread past the timeout.
            try:
                if payload:
                    _write_all(write_stdin, payload)
            except SandboxError:
                pass
            _k32.CloseHandle(write_stdin)
            deadline = time.monotonic() + max(0.1, timeout_seconds)
            limited = 0
            chunks: list[bytes] = []
            while True:
                while True:
                    available = w.DWORD(0)
                    if not _k32.PeekNamedPipe(
                        read_stdout, None, 0, None, ctypes.byref(available), None
                    ):
                        break
                    if available.value == 0:
                        break
                    size_read = w.DWORD(0)
                    buffer_out = ctypes.create_string_buffer(65536)
                    if not _k32.ReadFile(
                        read_stdout,
                        buffer_out,
                        65536,
                        ctypes.byref(size_read),
                        None,
                    ):
                        break
                    if size_read.value == 0:
                        break
                    limited += size_read.value
                    if limited > max_output_bytes:
                        _k32.TerminateProcess(process_info.hProcess, 1)
                        raise SandboxError("hook output exceeded the sandbox limit")
                    chunks.append(buffer_out.raw[: size_read.value])
                exited = _k32.WaitForSingleObject(process_info.hProcess, 0) == 0
                if exited:
                    # drain whatever is left in the pipe after exit
                    while True:
                        available = w.DWORD(0)
                        if not _k32.PeekNamedPipe(
                            read_stdout, None, 0, None, ctypes.byref(available), None
                        ):
                            break
                        if available.value == 0:
                            break
                        size_read = w.DWORD(0)
                        buffer_out = ctypes.create_string_buffer(65536)
                        if not _k32.ReadFile(
                            read_stdout,
                            buffer_out,
                            65536,
                            ctypes.byref(size_read),
                            None,
                        ):
                            break
                        if size_read.value == 0:
                            break
                        limited += size_read.value
                        if limited > max_output_bytes:
                            raise SandboxError("hook output exceeded the sandbox limit")
                        chunks.append(buffer_out.raw[: size_read.value])
                    break
                if time.monotonic() >= deadline:
                    timed_out = True
                    _k32.TerminateProcess(process_info.hProcess, 1)
                    _k32.WaitForSingleObject(process_info.hProcess, 5000)
                    break
                time.sleep(0.01)
            code = w.DWORD(0)
            _k32.GetExitCodeProcess(process_info.hProcess, ctypes.byref(code))
            stdout = b"".join(chunks)
            return SandboxResult(returncode=int(code.value), stdout=stdout, timed_out=timed_out)
        finally:
            try:
                _k32.CloseHandle(write_stdin)
            except Exception:  # noqa: BLE001 - best-effort cleanup
                pass
            try:
                _k32.CloseHandle(read_stdout)
            except Exception:  # noqa: BLE001
                pass
            _k32.CloseHandle(process_info.hThread)
            _k32.CloseHandle(process_info.hProcess)
            _k32.CloseHandle(job)

    def _sid_pointer(self, sid: str) -> int:
        sid_ptr = ctypes.c_void_p()
        if not _advapi32.ConvertStringSidToSidW(
            ctypes.c_wchar_p(sid), ctypes.byref(sid_ptr)
        ):
            raise SandboxError("cannot parse the plugin AppContainer SID")
        return int(sid_ptr.value)

    def close(self) -> None:
        self._closed = True

    def __enter__(self) -> "AppContainerSandbox":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


#: The only variables a hook child may inherit: everything else (data root,
#: proxy, DSH/M2RC1/test vars, user profile, tokens) stays inside the Core.
_CHILD_ENVIRONMENT_KEYS = ("SYSTEMROOT", "PYTHONIOENCODING", "PYTHONDONTWRITEBYTECODE")


def _child_environment() -> dict[str, str]:
    environment = {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    # Empirical minimum for CreateProcessW + AppContainer: LOCALAPPDATA is
    # required by the container launch path (removing it yields WinError 203);
    # every other user/test/proxy variable is dropped.
    for key in ("SYSTEMROOT", "SYSTEMDRIVE", "LOCALAPPDATA"):
        value = os.environ.get(key)
        if value:
            environment[key] = value
    return environment


def _environment_block(environment: dict[str, str]) -> ctypes.Array:
    """Build the ``KEY=VALUE\0...\0\0`` UTF-16 block CreateProcessW expects."""
    encoded = "".join(f"{key}={value}\0" for key, value in environment.items())
    encoded += "\0"
    data = encoded.encode("utf-16-le")
    buffer = ctypes.create_string_buffer(data, len(data) + 2)
    return buffer


def _capability_sid(name: str) -> ctypes.c_void_p:
    sid_string = CAPABILITY_SIDS.get(name)
    if sid_string is None:
        raise SandboxError(f"unknown capability {name!r}")
    sid = ctypes.c_void_p()
    if not _advapi32.ConvertStringSidToSidW(
        ctypes.c_wchar_p(sid_string), ctypes.byref(sid)
    ):
        raise SandboxError(f"cannot resolve the capability SID for {name!r}")
    return sid


def _build_security_capabilities(
    app_container_sid_pointer: int, capability_names: tuple[str, ...]
) -> tuple[_SECURITY_CAPABILITIES, list[int]]:
    """Build SECURITY_CAPABILITIES with an enabled capability SID array.

    Returns the structure plus the LocalAlloc'd pointers the caller must free
    after CreateProcessW (the kernel copies them before returning).
    """
    structure = _SECURITY_CAPABILITIES()
    structure.AppContainerSid = ctypes.c_void_p(app_container_sid_pointer)
    structure.CapabilityCount = 0
    structure.Capabilities = None
    if not capability_names:
        return structure, []
    block_size = ctypes.sizeof(_SID_AND_ATTRIBUTES) * len(capability_names)
    block = _k32.LocalAlloc(_LMEM_FIXED, block_size)
    if not block:
        raise SandboxError("cannot allocate the capability SID array")
    array = ctypes.cast(block, ctypes.POINTER(_SID_AND_ATTRIBUTES))
    pointers: list[int] = [block]
    for index, name in enumerate(capability_names):
        sid = _capability_sid(name)
        pointers.append(int(sid.value))
        array[index] = _SID_AND_ATTRIBUTES(sid, _SE_GROUP_ENABLED)
    structure.Capabilities = array
    structure.CapabilityCount = len(capability_names)
    return structure, pointers


def _command_line(argv: list[str]) -> str:
    """Quote one command line (CreateProcessW takes a single string)."""

    return subprocess.list2cmdline(list(argv))


def _write_all(handle: int, payload: bytes) -> None:
    written = w.DWORD(0)
    offset = 0
    while offset < len(payload):
        chunk = payload[offset : offset + 65536]
        if not _k32.WriteFile(handle, chunk, len(chunk), ctypes.byref(written), None):
            raise SandboxError("cannot write the hook payload to the sandbox")
        offset += written.value
