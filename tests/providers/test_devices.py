"""Device selection, single-concurrency and OOM isolation (AC-GPU-001~003)."""

from __future__ import annotations

import threading
import time

import pytest

from infrastructure.devices.manager import (
    DEVICE_CPU,
    DEVICE_GPU,
    GPU_UNAVAILABLE,
    DeviceManager,
    HeavyJobGate,
    looks_like_oom,
)
from ports.providers.errors import DeviceUnavailable, ProviderOutOfMemory


def test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented() -> None:
    manager = DeviceManager()
    info = manager.gpu_info()
    assert info.state == GPU_UNAVAILABLE
    assert info.available is False
    assert "torch" in info.detail
    # AC-GPU-003: no silent downgrade when the provider cannot run on CPU.
    with pytest.raises(DeviceUnavailable):
        manager.plan(requires_gpu=True, supports_cpu_fallback=False)


def test_cpu_fallback_only_when_the_provider_declares_it() -> None:
    manager = DeviceManager()
    plan = manager.plan(requires_gpu=True, supports_cpu_fallback=True)
    assert plan.device == DEVICE_CPU
    assert plan.requested_device == DEVICE_GPU
    assert plan.fell_back is True
    assert "gpu_unavailable" in plan.fallback_reason
    provenance = plan.as_provenance()
    assert provenance["device_fell_back"] is True
    assert provenance["device"] == DEVICE_CPU

    plain = manager.plan(requires_gpu=False, supports_cpu_fallback=False)
    assert plain.device == DEVICE_CPU
    assert plain.fell_back is False


def test_oom_is_typed_and_does_not_escape(monkeypatch) -> None:
    manager = DeviceManager()

    def boom():
        raise RuntimeError("CUDA error: out of memory")

    with pytest.raises(ProviderOutOfMemory):
        manager.run_guarded(requires_gpu=True, call=boom)

    # Non-OOM exceptions keep their identity.
    def other():
        raise ValueError("bad geometry")

    with pytest.raises(ValueError):
        manager.run_guarded(requires_gpu=True, call=other)


@pytest.mark.parametrize(
    "error,expected",
    [
        (MemoryError("nope"), True),
        (RuntimeError("CUDA out of memory. Tried to allocate"), True),
        (RuntimeError("OutOfMemoryError"), True),
        (RuntimeError("connection reset"), False),
    ],
)
def test_oom_marker_detection(error, expected) -> None:
    assert looks_like_oom(error) is expected


def test_heavy_gate_serialises_to_one_slot_by_default() -> None:
    gate = HeavyJobGate()
    assert gate.capacity == 1
    order: list[str] = []
    barrier = threading.Barrier(2)

    def worker(name: str) -> None:
        with gate.slot():
            order.append(f"{name}-in")
            time.sleep(0.05)
            order.append(f"{name}-out")

    threads = [threading.Thread(target=worker, args=(name,)) for name in ("a", "b")]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert gate.max_observed == 1
    assert gate.serialised_count >= 1
    # The first worker finished before the second entered.
    assert order[1].endswith("-out")
    assert order[2].endswith("-in")


def test_gate_capacity_must_be_positive() -> None:
    with pytest.raises(ValueError):
        HeavyJobGate(0)
