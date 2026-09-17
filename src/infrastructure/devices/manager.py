"""Device capability and heavy-job scheduling (D06 §80~§82, AC-GPU-001~003).

TASK-019 runs in an environment without ``torch``/``numpy``: GPU existence is
**not** device availability. This module therefore never invents a device:

- a GPU is reported available only when a real runtime for it is installed
  and importable (``torch.cuda`` today); otherwise the state is
  ``unavailable`` with a typed reason and the model provider is Not-Ready;
- CPU fallback happens only when the provider declares
  ``supports_cpu_fallback`` (D06 §82, AC-GPU-003) and the fallback is recorded
  in provenance — it is never presented as GPU execution;
- GPU-heavy work is serialised behind a single-slot gate by default
  (AC-GPU-002); a provider that explicitly allows concurrency may exceed it;
- an OOM inside a provider is isolated into a typed failure: the slot is
  released, the model is marked unloaded and the application keeps running
  (AC-GPU-001).
"""

from __future__ import annotations

import importlib.util
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
        if not _module_present("torch"):
            return DeviceInfo(
                kind=DEVICE_GPU,
                state=GPU_UNAVAILABLE,
                error_code=DeviceUnavailable.error_code,
                detail="no GPU runtime installed (torch is absent)",
            )
        try:  # pragma: no cover - requires torch, absent in this environment
            import torch  # type: ignore

            if not torch.cuda.is_available():
                return DeviceInfo(
                    kind=DEVICE_GPU,
                    state=GPU_UNAVAILABLE,
                    error_code=DeviceUnavailable.error_code,
                    detail="torch reports no CUDA device",
                )
            properties = torch.cuda.get_device_properties(0)
            return DeviceInfo(
                kind=DEVICE_GPU,
                index=0,
                name=str(properties.name),
                total_memory_mb=int(properties.total_memory // (1024 * 1024)),
                state=GPU_AVAILABLE,
            )
        except Exception as error:  # pragma: no cover - defensive
            return DeviceInfo(
                kind=DEVICE_GPU,
                state=GPU_UNKNOWN,
                error_code=DeviceUnavailable.error_code,
                detail=f"GPU probe failed: {error!r}",
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

    def run_guarded(self, *, requires_gpu: bool, call):
        """Run ``call`` under the heavy gate with OOM isolation (AC-GPU-001/002).

        The OOM is converted into a typed :class:`ProviderOutOfMemory`; the
        gate slot is released by the context manager and the caller can mark
        the model unloaded and continue the Run.
        """
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
