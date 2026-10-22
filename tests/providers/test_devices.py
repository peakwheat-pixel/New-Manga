"""Device selection, single-concurrency and OOM isolation (AC-GPU-001~003)."""

from __future__ import annotations

import threading
import time

import pytest

from infrastructure.devices.manager import (
    DEVICE_CPU,
    DEVICE_GPU,
    GPU_AVAILABLE,
    GPU_UNAVAILABLE,
    DeviceManager,
    HeavyJobGate,
    looks_like_oom,
)
from ports.providers.errors import DeviceUnavailable, ProviderOutOfMemory

from tests.providers.env_sim import gpu_state


def test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented() -> None:
    """The no-runtime path, forced rather than assumed.

    This used to read the real machine and assert no GPU was there. It passed on
    CI and failed on any workstation with a CUDA card, which says nothing about
    DeviceManager. The absence is now simulated so the path is exercised
    everywhere.
    """
    with gpu_state(available=False):
        manager = DeviceManager()
        info = manager.gpu_info()
        assert info.state == GPU_UNAVAILABLE
        assert info.available is False
        assert "torch" in info.detail
        # AC-GPU-003: no silent downgrade when the provider cannot run on CPU.
        with pytest.raises(DeviceUnavailable):
            manager.plan(requires_gpu=True, supports_cpu_fallback=False)


def test_gpu_is_reported_available_when_a_runtime_is_present() -> None:
    """The other side, which nothing used to cover.

    Without this, a change that made _probe_gpu always report unavailable would
    keep every test green on a machine without a GPU.
    """
    with gpu_state(available=True, name="Simulated GPU", total_memory_mb=12288):
        manager = DeviceManager()
        info = manager.gpu_info()
        assert info.state == GPU_AVAILABLE
        assert info.available is True
        assert info.name == "Simulated GPU"
        assert info.total_memory_mb == 12288


def test_plan_uses_the_gpu_when_one_is_available_and_does_not_fall_back() -> None:
    """A reachable GPU must not be reported as a fallback to CPU."""
    with gpu_state(available=True):
        manager = DeviceManager()
        plan = manager.plan(requires_gpu=True, supports_cpu_fallback=True)
        assert plan.device == DEVICE_GPU
        assert plan.fell_back is False
        assert plan.as_provenance()["device_fell_back"] is False


def test_cpu_fallback_only_when_the_provider_declares_it() -> None:
    with gpu_state(available=False):
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


# ---------------------------------------------------------------------------
# SETTINGS-OPEN-B-1 AC2: an explicit Run device preference is planned first
#
# ``auto`` (``preferred_device`` omitted) must keep the historical code path
# untouched -- no ``plan()`` call at all -- while an explicit ``cpu`` / ``gpu``
# is validated by ``DeviceManager.plan`` with the D06 §82 fallback pair (the
# user switch ANDs with the provider declaration).
# ---------------------------------------------------------------------------


def test_run_guarded_gpu_preference_raises_when_no_fallback_is_available() -> None:
    """GPU preference + GPU unavailable + user denies fallback -> typed refusal."""
    calls: list[str] = []

    with gpu_state(available=False):
        manager = DeviceManager()
        with pytest.raises(DeviceUnavailable):
            manager.run_guarded(
                requires_gpu=True,
                call=lambda: calls.append("called"),
                preferred_device=DEVICE_GPU,
                allow_cpu_fallback=False,
                supports_cpu_fallback=True,
            )

    # the call never ran: the typed refusal happens before the provider.
    assert calls == []


@pytest.mark.parametrize(
    "allow_cpu_fallback,supports_cpu_fallback",
    [
        (False, True),  # the user disabled the fallback
        (True, False),  # the provider cannot run on CPU
        (False, False),
    ],
)
def test_run_guarded_gpu_preference_requires_both_fallback_halves(
    allow_cpu_fallback: bool, supports_cpu_fallback: bool
) -> None:
    calls: list[str] = []

    with gpu_state(available=False):
        manager = DeviceManager()
        with pytest.raises(DeviceUnavailable):
            manager.run_guarded(
                requires_gpu=True,
                call=lambda: calls.append("called"),
                preferred_device=DEVICE_GPU,
                allow_cpu_fallback=allow_cpu_fallback,
                supports_cpu_fallback=supports_cpu_fallback,
            )

    assert calls == []


def test_run_guarded_gpu_preference_falls_back_when_both_halves_allow() -> None:
    calls: list[str] = []

    def call() -> str:
        calls.append("called")
        return "executed"

    with gpu_state(available=False):
        manager = DeviceManager()
        assert (
            manager.run_guarded(
                requires_gpu=True,
                call=call,
                preferred_device=DEVICE_GPU,
                allow_cpu_fallback=True,
                supports_cpu_fallback=True,
            )
            == "executed"
        )

    assert calls == ["called"]


def test_run_guarded_gpu_preference_runs_on_an_available_gpu() -> None:
    with gpu_state(available=True):
        manager = DeviceManager()
        assert (
            manager.run_guarded(
                requires_gpu=True,
                call=lambda: "executed",
                preferred_device=DEVICE_GPU,
                allow_cpu_fallback=False,
                supports_cpu_fallback=False,
            )
            == "executed"
        )


def test_run_guarded_cpu_preference_returns_normally_without_a_gpu() -> None:
    """An explicit CPU preference is honoured without probing for a GPU."""
    with gpu_state(available=False):
        manager = DeviceManager()
        assert (
            manager.run_guarded(
                requires_gpu=False,
                call=lambda: "executed",
                preferred_device=DEVICE_CPU,
                allow_cpu_fallback=False,
                supports_cpu_fallback=False,
            )
            == "executed"
        )
        # ``plan`` answers a CPU request directly: no GPU probe was needed.
        assert manager._gpu_info is None


def test_run_guarded_auto_never_calls_plan(monkeypatch) -> None:
    """Zero behaviour change for ``auto``: the historical path never plans."""
    manager = DeviceManager()

    def forbidden(**kwargs):  # pragma: no cover - only runs on a regression
        raise AssertionError("auto must not call DeviceManager.plan")

    monkeypatch.setattr(manager, "plan", forbidden)

    assert manager.run_guarded(requires_gpu=False, call=lambda: "executed") == (
        "executed"
    )


def test_run_guarded_auto_keeps_the_unplanned_gpu_path() -> None:
    """Historical behaviour: without a preference the GPU is not planned.

    ``run_guarded`` never did a device downgrade decision of its own; an
    unavailable GPU only surfaced through the provider itself. This pins that
    the B-1 change did not retrofit planning onto the ``auto`` path.
    """
    with gpu_state(available=False):
        manager = DeviceManager()
        assert manager.run_guarded(requires_gpu=True, call=lambda: "executed") == (
            "executed"
        )


def test_run_guarded_preference_keeps_oom_isolation() -> None:
    with gpu_state(available=True):
        manager = DeviceManager()

        def boom():
            raise RuntimeError("CUDA error: out of memory")

        with pytest.raises(ProviderOutOfMemory):
            manager.run_guarded(
                requires_gpu=True,
                call=boom,
                preferred_device=DEVICE_GPU,
                allow_cpu_fallback=False,
                supports_cpu_fallback=False,
            )
