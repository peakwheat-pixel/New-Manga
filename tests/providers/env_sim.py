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

Codex's r42 adjudication required both sides to be covered deterministically and that
no production seam be added for the purpose. Everything below patches only
test-visible lookups, so nothing in src/ learns about tests.

GPU-ORT-PROBE-1 (2026-10-27): the GPU probe authority moved from ``torch.cuda``
to ONNX Runtime's execution-provider list, so the simulation patches that list
(plus the name/memory supplements) instead of installing a fake torch.

The two seams used:

  ``infrastructure.providers.dependencies.probe_module``
      called by ``evaluate_requirements`` at call time through module globals,
      so patching it changes provider readiness for the duration of a test.

  ``infrastructure.devices.manager._onnxruntime_providers`` /
  ``_windows_gpu_name`` / ``_torch_supplement``
      called by ``DeviceManager._probe_gpu``; the first answers "which execution
      providers exist", the other two supply the display name/memory only.
"""

from __future__ import annotations

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
    "onnxruntime",
    "manga_ocr",
    "paddleocr",
    "paddle",
    "torch",
    "diffusers",
    "numpy",
    # PIL is not an optional runtime in spirit, but manga-ocr declares it as a
    # requirement next to manga_ocr, so leaving it on the real probe made the
    # "runtimes present" side depend on a host fact the test never stated.
    "PIL",
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
    """Force ``DeviceManager`` to see, or not see, a GPU execution provider.

    The available side reports the DirectML provider (the release form) and a
    deterministic adapter name/memory; the unavailable side reports CPU only.
    All three probe seams are restored afterwards.
    """
    real_providers = manager_module._onnxruntime_providers
    real_adapter = manager_module._windows_gpu_name
    real_supplement = manager_module._torch_supplement

    if available:
        manager_module._onnxruntime_providers = lambda: (
            "DmlExecutionProvider",
            "CPUExecutionProvider",
        )
        manager_module._windows_gpu_name = lambda: (name, total_memory_mb)
    else:
        manager_module._onnxruntime_providers = lambda: ("CPUExecutionProvider",)
        manager_module._windows_gpu_name = lambda: None
    manager_module._torch_supplement = lambda: (None, None)

    try:
        yield
    finally:
        manager_module._onnxruntime_providers = real_providers
        manager_module._windows_gpu_name = real_adapter
        manager_module._torch_supplement = real_supplement
