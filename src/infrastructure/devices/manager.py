"""Device capability and heavy-job scheduling (D06 §80~§82, AC-GPU-001~003).

TASK-019 runs in an environment without ``torch``/``numpy``: GPU existence is
**not** device availability. This module therefore never invents a device:

- a GPU is reported available only when a real inference runtime for it is
  installed and enumerable — the authority is ONNX Runtime's execution-provider
  list (``onnxruntime.get_available_providers()``); ``torch`` is only a
  development-time supplement (device name/memory) and never the main verdict;
- CPU fallback happens only when the provider declares
  ``supports_cpu_fallback`` (D06 §82, AC-GPU-003) and the fallback is recorded
  in provenance — it is never presented as GPU execution;
- GPU-heavy work is serialised behind a single-slot gate by default
  (AC-GPU-002); a provider that explicitly allows concurrency may exceed it;
- an OOM inside a provider is isolated into a typed failure: the slot is
  released, the model is marked unloaded and the application keeps running
  (AC-GPU-001).

GPU-ORT-PROBE-1 (2026-10-27): the release closure is torch-free and ships
ONNX Runtime with the DirectML provider, so torch-based probing reported the
GPU unavailable in packaged builds. The probe now reads the ORT EP list and
uses the Windows display-adapter registry (and torch, when importable) only as
a name/memory supplement.
"""

from __future__ import annotations

import importlib.util
import sys
import threading
from dataclasses import dataclass, field

from ports.providers.errors import (
    DeviceUnavailable,
    ProviderOutOfMemory,
)

DEVICE_GPU = "gpu"
DEVICE_CPU = "cpu"

GPU_AVAILABLE = "available"
GPU_UNAVAILABLE = "unavailable"
GPU_UNKNOWN = "unknown"

#: ONNX Runtime execution providers that mean "this machine has a GPU EP".
#: Ordered by preference; only labels/names here, never an import.
_GPU_EXECUTION_PROVIDERS = (
    ("DmlExecutionProvider", "DirectML"),
    ("CUDAExecutionProvider", "CUDA"),
    ("ROCMExecutionProvider", "ROCm"),
    ("MIGraphXExecutionProvider", "MIGraphX"),
    ("TensorrtExecutionProvider", "TensorRT"),
)

#: Substrings that identify an out-of-memory failure across runtimes without
#: importing any of them (torch/cuda/numpy all phrase it differently).
_OOM_MARKERS = (
    "out of memory",
    "outofmemory",
    "cuda error: out of memory",
    "cuda_error_out_of_memory",
    "not enough memory",
    "insufficient memory",
    "memoryerror",
)


def _module_present(name: str) -> bool:
    """True when an importable module exists — no import side effects."""
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ValueError):
        return False


def _onnxruntime_providers() -> tuple[str, ...]:
    """The execution providers the installed ONNX Runtime reports (empty when absent).

    This is the AC1 authority for "is there a usable GPU runtime": the release
    closure ships ``onnxruntime-directml`` and no torch, so the EP list is the
    only honest answer available inside the packaged process. Import errors and
    unusual runtimes fail closed to "no providers".
    """
    try:
        import onnxruntime  # type: ignore
    except Exception:  # noqa: BLE001 - optional runtime, any import failure means absent
        return ()
    try:
        providers = onnxruntime.get_available_providers()
    except Exception:  # noqa: BLE001 - a broken runtime must not break device probing
        return ()
    if not providers:
        return ()
    return tuple(str(provider) for provider in providers)


def _windows_gpu_name() -> tuple[str, int | None] | None:
    """Best-effort display-adapter name/size from the Windows registry (stdlib only).

    ONNX Runtime enumerates *providers*, not adapters; the settings page wants a
    human name. The display-adapter class key carries ``DriverDesc`` and (for
    real GPUs) ``HardwareInformation.qwMemorySize``. Virtual display adapters are
    present on this machine, so the adapter with the largest reported memory
    wins. Never raises: the registry is a supplement, not the verdict.
    """
    if sys.platform != "win32":
        return None
    try:
        import winreg
    except ImportError:  # pragma: no cover - Windows always has winreg
        return None
    base = (
        r"SYSTEM\CurrentControlSet\Control\Class"
        r"\{4d36e968-e325-11ce-bfc1-08002be10318}"
    )
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base) as root:
            best: tuple[str, int | None] | None = None
            for index in range(64):
                try:
                    subkey = winreg.EnumKey(root, index)
                except OSError:
                    break
                if subkey in ("Configuration", "Properties"):
                    continue
                try:
                    with winreg.OpenKey(root, subkey) as adapter:
                        try:
                            desc, _ = winreg.QueryValueEx(adapter, "DriverDesc")
                        except OSError:
                            desc = None
                        try:
                            qword, _ = winreg.QueryValueEx(
                                adapter, "HardwareInformation.qwMemorySize"
                            )
                        except OSError:
                            qword = None
                except OSError:
                    continue
                if not isinstance(desc, str) or not desc:
                    continue
                memory = (
                    int(qword) // (1024 * 1024)
                    if isinstance(qword, int) and qword > 0
                    else None
                )
                if best is None or (memory or 0) > (best[1] or 0):
                    best = (desc, memory)
            return best
    except OSError:
        return None


def _torch_supplement() -> tuple[str | None, int | None]:
    """Development-time name/memory supplement (never the availability verdict)."""
    if not _module_present("torch"):
        return None, None
    try:  # pragma: no cover - requires a CUDA torch, absent in the release closure
        import torch  # type: ignore

        if not torch.cuda.is_available():
            return None, None
        properties = torch.cuda.get_device_properties(0)
        return str(properties.name), int(properties.total_memory // (1024 * 1024))
    except Exception:  # pragma: no cover - defensive
        return None, None


def probe_snapshot(manager: "DeviceManager | None" = None) -> dict:
    """The probe result as a JSON-ready dict (device probe evidence / package metadata).

    Same fields as ``DeviceInfo.as_dict()`` plus the raw ORT EP list, so a
    packaged build can record what its closure actually supports.
    """
    probe = (manager or DeviceManager()).gpu_info()
    return {
        "onnxruntime_providers": list(_onnxruntime_providers()),
        "gpu": probe.as_dict(),
    }


def looks_like_oom(error: BaseException) -> bool:
    """Classify an exception as OOM without requiring a specific runtime."""
    if isinstance(error, MemoryError):
        return True
    text = f"{type(error).__name__}: {error}".lower()
    return any(marker in text for marker in _OOM_MARKERS)


@dataclass(frozen=True)
class DeviceInfo:
    kind: str
    index: int = 0
    name: str = ""
    total_memory_mb: int | None = None
    state: str = GPU_UNKNOWN
    error_code: str = ""
    detail: str = ""

    @property
    def available(self) -> bool:
        return self.state == GPU_AVAILABLE

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "index": self.index,
            "name": self.name,
            "total_memory_mb": self.total_memory_mb,
            "state": self.state,
            "error_code": self.error_code,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class DevicePlan:
    """The device one provider execution will actually use."""

    device: str
    requested_device: str
    fallback_reason: str = ""
    device_info: DeviceInfo | None = None

    @property
    def fell_back(self) -> bool:
        return bool(self.fallback_reason)

    def as_provenance(self) -> dict:
        record = {
            "device": self.device,
            "requested_device": self.requested_device,
            "device_fallback_reason": self.fallback_reason,
            "device_fell_back": self.fell_back,
        }
        if self.device_info is not None:
            record["device_info"] = self.device_info.as_dict()
        return record


class HeavyJobGate:
    """A counting gate that serialises GPU-heavy providers (AC-GPU-002).

    Default capacity is 1. ``capacity`` above 1 must be requested explicitly
    by a provider whose descriptor allows concurrency; the gate records the
    configured capacity so the scheduler's behaviour is auditable.
    """

    def __init__(self, capacity: int = 1) -> None:
        if capacity < 1:
            raise ValueError("gate capacity must be >= 1")
        self._capacity = capacity
        self._semaphore = threading.BoundedSemaphore(capacity)
        self._mutex = threading.Lock()
        self._in_flight = 0
        self._max_observed = 0
        self._serialised = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def in_flight(self) -> int:
        with self._mutex:
            return self._in_flight

    @property
    def max_observed(self) -> int:
        with self._mutex:
            return self._max_observed

    @property
    def serialised_count(self) -> int:
        """How often a caller had to wait for the slot."""
        with self._mutex:
            return self._serialised

    class _Lease:
        def __init__(self, gate: "HeavyJobGate") -> None:
            self._gate = gate

        def __enter__(self) -> None:
            if not self._gate._semaphore.acquire(blocking=False):
                with self._gate._mutex:
                    self._gate._serialised += 1
                self._gate._semaphore.acquire()
            with self._gate._mutex:
                self._gate._in_flight += 1
                self._gate._max_observed = max(
                    self._gate._max_observed, self._gate._in_flight
                )
            return None

        def __exit__(self, *_exc_info) -> None:
            with self._gate._mutex:
                self._gate._in_flight -= 1
            self._gate._semaphore.release()

    def slot(self) -> "HeavyJobGate._Lease":
        return HeavyJobGate._Lease(self)


@dataclass
class DeviceManager:
    """Resolve the device for one provider execution and isolate OOM."""

    heavy_gate: HeavyJobGate = field(default_factory=HeavyJobGate)
    _gpu_info: DeviceInfo | None = field(default=None, init=False, repr=False)

    def gpu_info(self) -> DeviceInfo:
        """Probe the GPU once per manager instance (no runtime invented)."""
        if self._gpu_info is None:
            self._gpu_info = self._probe_gpu()
        return self._gpu_info

    def _probe_gpu(self) -> DeviceInfo:
        providers = _onnxruntime_providers()
        execution_provider = next(
            (label for name, label in _GPU_EXECUTION_PROVIDERS if name in providers),
            None,
        )
        torch_name, torch_memory = _torch_supplement()
        adapter = _windows_gpu_name()
        if execution_provider is None:
            if providers:
                detail = (
                    "onnxruntime has no GPU execution provider "
                    f"(providers={list(providers)})"
                )
            else:
                detail = "onnxruntime is not installed (no execution providers)"
            if torch_name:
                detail += (
                    f"; torch supplement: {torch_name} "
                    "(development-only, not the inference runtime)"
                )
            return DeviceInfo(
                kind=DEVICE_GPU,
                state=GPU_UNAVAILABLE,
                error_code=DeviceUnavailable.error_code,
                detail=detail,
            )

        name = torch_name or (adapter[0] if adapter else None) or execution_provider
        memory = torch_memory or (adapter[1] if adapter else None)
        return DeviceInfo(
            kind=DEVICE_GPU,
            index=0,
            name=name,
            total_memory_mb=memory,
            state=GPU_AVAILABLE,
            detail=(
                f"onnxruntime providers={list(providers)}; "
                f"execution_provider={execution_provider}"
            ),
        )

    def plan(
        self,
        *,
        requires_gpu: bool,
        supports_cpu_fallback: bool,
        preferred_device: str | None = None,
    ) -> DevicePlan:
        """Choose the device, refusing to silently downgrade (D06 §82).

        A GPU-requiring provider without CPU support and without an available
        GPU raises :class:`DeviceUnavailable`; it is never quietly run on CPU.
        """
        requested = preferred_device or (DEVICE_GPU if requires_gpu else DEVICE_CPU)
        if requested == DEVICE_GPU:
            info = self.gpu_info()
            if info.available:
                return DevicePlan(DEVICE_GPU, requested, device_info=info)
            if not supports_cpu_fallback:
                raise DeviceUnavailable(
                    f"GPU required but unavailable: {info.detail}",
                    provider_id="",
                    stage="device",
                )
            return DevicePlan(
                DEVICE_CPU,
                requested,
                fallback_reason=f"gpu_unavailable: {info.detail}",
                device_info=info,
            )
        return DevicePlan(DEVICE_CPU, requested)

    def run_guarded(
        self,
        *,
        requires_gpu: bool,
        call,
        preferred_device: str | None = None,
        allow_cpu_fallback: bool = True,
        supports_cpu_fallback: bool = False,
    ):
        """Run ``call`` under the heavy gate with OOM isolation (AC-GPU-001/002).

        The OOM is converted into a typed :class:`ProviderOutOfMemory`; the
        gate slot is released by the context manager and the caller can mark
        the model unloaded and continue the Run.

        SETTINGS-OPEN-B-1 AC2 (design §4.1): an explicit Run preference
        (``preferred_device`` not ``None``) is validated through
        :meth:`plan` first — a GPU preference that the user did not allow to
        fall back (or a provider that cannot run on CPU) surfaces as the typed
        :class:`DeviceUnavailable` *before* the call starts, and a CPU
        preference is honoured as such. :meth:`plan` is the single device
        authority; this method does not second-guess its outcome. With
        ``preferred_device`` ``None`` (``auto``, every pre-B-1 caller) the
        historical code path runs unchanged: no planning, same gate, same OOM
        isolation.
        """
        if preferred_device is not None:
            # D06 §82: the user switch ANDs with the provider declaration.
            self.plan(
                requires_gpu=requires_gpu,
                supports_cpu_fallback=(
                    supports_cpu_fallback and allow_cpu_fallback
                ),
                preferred_device=preferred_device,
            )
        if requires_gpu:
            with self.heavy_gate.slot():
                return self._invoke(call)
        return self._invoke(call)

    @staticmethod
    def _invoke(call):
        try:
            return call()
        except ProviderOutOfMemory:
            raise
        except BaseException as error:  # noqa: BLE001 - re-raised typed below
            if looks_like_oom(error):
                raise ProviderOutOfMemory(
                    f"{type(error).__name__}: {error}", stage="device"
                ) from error
            raise
