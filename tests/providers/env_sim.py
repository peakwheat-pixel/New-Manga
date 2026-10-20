"""Deterministic simulation of "this machine has / has not got X".

Why this module exists. Four provider tests asserted that optional runtimes are
absent - `manga-ocr` must report `missing_dependency`, the GPU must report
`unavailable`. Those assertions describe a bare CI machine, and they pass there.
On a developer machine with `manga-ocr` installed and a CUDA GPU they fail, not
because anything is broken but because the test never said it was describing a
bare machine.

Two tempting fixes are both wrong:
  - change the expected values to this machine's values, which breaks CI
  - skip when the runtime is present, which leaves the absent path untested on
    every machine that has the runtime and the present path untested everywhere

ZCode's r42 condition was that both sides be covered deterministically and that
no production seam be added for the purpose. Everything below patches only
test-visible lookups, so nothing in src/ learns about tests.

The two seams used:

  ``infrastructure.providers.dependencies.probe_module``
      called by ``evaluate_requirements`` at call time through module globals,
      so patching it changes provider readiness for the duration of a test.

  ``infrastructure.devices.manager._module_present``
      called by ``DeviceManager._probe_gpu``. For the available side a fake
      ``torch`` is also installed in ``sys.modules``, because the probe imports
      torch for real once the module check passes.

Neither is a new interface: both already existed and are already the only places
that answer "is this runtime here?".
"""

from __future__ import annotations

import sys
import types
from contextlib import contextmanager
from typing import Iterator

import infrastructure.devices.manager as manager_module
import infrastructure.providers.dependencies as dependencies_module
from infrastructure.providers.dependencies import (
    KIND_MODULE,
    Requirement,
    RequirementProbe,
)

#: Optional runtimes the provider tests talk about. Listed so a "made absent"
#: test cannot silently pass just because the machine lacks them anyway - the
#: helper reports on these names explicitly either way.
OPTIONAL_PROVIDER_MODULES = (
    "manga_ocr",
    "paddleocr",
    "paddle",
    "torch",
    "diffusers",
    "numpy",
)


@contextmanager
def modules_state(present: frozenset[str] = frozenset(),
                  absent: frozenset[str] = frozenset()) -> Iterator[None]:
    """Force the named modules to probe as present or absent.

    Names in neither set keep their real answer, so a test can pin the runtimes
    it is about without claiming anything about the rest.
    """
    real = dependencies_module.probe_module

    def fake(name: str) -> RequirementProbe:
        requirement = Requirement(KIND_MODULE, name)
        if name in present:
            return RequirementProbe(requirement, True, "")
        if name in absent:
            return RequirementProbe(requirement, False, f"module {name!r} is not installed")
        return real(name)

    dependencies_module.probe_module = fake
    try:
        yield
    finally:
        dependencies_module.probe_module = real


@contextmanager
def with_optional_runtimes(*, available: bool) -> Iterator[None]:
    """All known optional runtimes at once - the two sides the ACs name."""
    names = frozenset(OPTIONAL_PROVIDER_MODULES)
    state = {"present": names, "absent": frozenset()} if available else {
        "present": frozenset(), "absent": names}
    with modules_state(**state):
        yield


@contextmanager
def gpu_state(*, available: bool, name: str = "Simulated GPU",
              total_memory_mb: int = 12288) -> Iterator[None]:
    """Force ``DeviceManager`` to see, or not see, a usable CUDA GPU.

    The available side installs a stand-in ``torch`` in ``sys.modules`` so the
    real ``import torch`` inside the probe resolves to something whose
    ``cuda.is_available()`` we control. The stand-in is removed afterwards, and
    a real installed torch is restored.
    """
    real_present = manager_module._module_present
    had_torch = "torch" in sys.modules
    previous_torch = sys.modules.get("torch")

    if available:
        fake_cuda = types.SimpleNamespace(
            is_available=lambda: True,
            get_device_properties=lambda index: types.SimpleNamespace(
                name=name, total_memory=total_memory_mb * 1024 * 1024),
        )
        fake_torch = types.SimpleNamespace(cuda=fake_cuda)
        manager_module._module_present = lambda module: True
        sys.modules["torch"] = fake_torch  # type: ignore[assignment]
    else:
        manager_module._module_present = lambda module: False

    try:
        yield
    finally:
        manager_module._module_present = real_present
        if available:
            if had_torch:
                sys.modules["torch"] = previous_torch  # type: ignore[assignment]
            else:
                sys.modules.pop("torch", None)


def simulated_gpu_is_reachable() -> bool:
    """True when a real GPU would be visible - used to pick the integration side.

    Not for skipping: the deterministic tests do not call this. It exists so the
    one test that is *about* the real machine can assert the truth instead of an
    assumption.
    """
    import importlib.util

    if importlib.util.find_spec("torch") is None:
        return False
    try:
        import torch  # noqa: PLC0415 - deliberately late, torch is optional
    except Exception:  # noqa: BLE001 - any import failure means "not reachable"
        return False
    try:
        return bool(torch.cuda.is_available())
    except Exception:  # noqa: BLE001
        return False
