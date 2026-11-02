"""Shared ONNX Runtime session policy for the Core inference providers.

CORE-SLIM-2 moved the detection/OCR chains from torch/transformers onto ONNX
Runtime so the packaged Core closure no longer carries torch (≈365 MiB), cv2,
scipy, transformers and their transitive stack. This module is the ONE place
that decides how an ORT session is created, which execution provider is used
and how failures are typed:

- the shipped wheel is ``onnxruntime-directml`` (same import name ``onnxruntime``
  as the CPU wheel; Dml + CPU providers). An environment without ORT reports
  ``PROVIDER_DEPENDENCY_MISSING`` — never a bare ImportError;
- ``device`` is a *policy*, not a promise: ``cpu``/``dml``/``cuda``/``auto``.
  ``auto`` prefers DirectML when the wheel exposes it and falls back to CPU.
  An explicitly requested provider that the installed wheel cannot offer is a
  typed ``PROVIDER_UNAVAILABLE`` (no silent CPU downgrade);
- ORT silently falls back to CPU when an EP fails to initialize (the INFER
  baseline hit this with ``onnxruntime-gpu`` 1.31 + a missing cublasLt DLL).
  The baseline harness hard-asserted that the wanted EP is actually active —
  this module keeps that guard: a session whose active provider list lost the
  requested EP raises ``PROVIDER_FAILED`` instead of reporting a CPU number as
  GPU.

Weights are never downloaded here; callers pass a local model path whose
SHA-256 they pinned themselves (the detector/OCR modules own their pins).
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from ports.providers.errors import (
    ProviderDependencyMissing,
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
    ProviderUnavailable,
)

EP_CPU = "CPUExecutionProvider"
EP_DML = "DmlExecutionProvider"
EP_CUDA = "CUDAExecutionProvider"

#: The accepted ``device`` policy values -> execution provider.
_DEVICE_TO_EP = {
    "auto": "auto",
    "cpu": EP_CPU,
    "dml": EP_DML,
    "directml": EP_DML,
    "cuda": EP_CUDA,
    "gpu": EP_CUDA,
}

#: The default graph optimisation level (ORT's highest).
_OPT_LEVEL = "ORT_ENABLE_ALL"


def _onnxruntime(stage: str) -> Any:
    try:
        return importlib.import_module("onnxruntime")
    except ImportError as error:
        raise ProviderDependencyMissing(
            f"ONNX Runtime is not installed ({error}); the packaged Core ships "
            "onnxruntime-directml (CORE-SLIM-2 detection/OCR runtime)",
            stage=stage,
        ) from error


def available_providers(stage: str = "inference") -> tuple[str, ...]:
    """The execution providers the installed ORT wheel can offer."""
    ort = _onnxruntime(stage)
    try:
        return tuple(ort.get_available_providers())
    except Exception as error:  # noqa: BLE001 - a broken ORT install is typed
        raise ProviderError(
            f"ONNX Runtime failed to enumerate execution providers: {error!r}",
            stage=stage,
        ) from error


def resolve_execution_provider(device: str, stage: str = "inference") -> str:
    """Map the ``device`` policy onto a concrete ORT execution provider.

    ``auto`` -> DirectML when available, else CPU. An explicit ``cuda``/``dml``
    request that this wheel cannot serve raises ``PROVIDER_UNAVAILABLE`` —
    never a silent CPU downgrade (the INFER baseline's EP_NOT_ACTIVE rule).
    """
    key = (device or "auto").strip().lower()
    if key not in _DEVICE_TO_EP:
        raise ProviderInputError(
            f"unsupported ONNX Runtime device {device!r} (use cpu|dml|cuda|auto)",
            stage=stage,
        )
    requested = _DEVICE_TO_EP[key]
    providers = available_providers(stage)
    if requested == "auto":
        return EP_DML if EP_DML in providers else EP_CPU
    if requested == EP_CPU:
        return EP_CPU
    if requested not in providers:
        raise ProviderUnavailable(
            f"{requested} was requested but the installed ONNX Runtime wheel "
            f"only offers {list(providers)}; install onnxruntime-directml "
            "(DML) or the matching onnxruntime-gpu (CUDA) package",
            stage=stage,
        )
    return requested


def create_session(
    model_path: Path,
    *,
    device: str = "auto",
    stage: str = "inference",
    log_severity: int = 3,
    intra_op_threads: int | None = None,
) -> Any:
    """Create one verified ORT session for a local model file.

    Check order (part of the contract): the file must exist first
    (``PROVIDER_NOT_CONFIGURED`` with placement guidance), then ORT must
    import (``PROVIDER_DEPENDENCY_MISSING``), then the device policy is
    resolved (``PROVIDER_UNAVAILABLE`` on a wheel mismatch), then the session
    is created and its ACTIVE provider list is verified
    (``PROVIDER_FAILED`` on an ORT-internal EP fallback).
    """
    path = Path(model_path)
    if not path.is_file():
        raise ProviderNotConfigured(
            f"ONNX model is not installed: {path} is missing "
            "(weights are never downloaded at run time)",
            stage=stage,
        )
    ort = _onnxruntime(stage)
    expected = resolve_execution_provider(device, stage)
    options = ort.SessionOptions()
    options.log_severity_level = log_severity
    try:
        options.graph_optimization_level = getattr(
            ort.GraphOptimizationLevel, _OPT_LEVEL
        )
    except AttributeError:  # pragma: no cover - exotic ORT forks
        pass
    if intra_op_threads is not None:
        if intra_op_threads < 1:
            raise ProviderInputError(
                f"intra_op_threads must be >= 1, got {intra_op_threads}", stage=stage
            )
        options.intra_op_num_threads = intra_op_threads
    try:
        session = ort.InferenceSession(
            str(path), options, providers=[expected, EP_CPU]
        )
    except Exception as error:  # noqa: BLE001 - session build failures are typed
        raise ProviderError(
            f"ONNX Runtime failed to load {path.name}: {error!r}", stage=stage
        ) from error
    active = tuple(session.get_providers())
    if expected != EP_CPU and expected not in active:
        raise ProviderError(
            f"ONNX Runtime fell back to {list(active)} for {path.name}: the "
            f"requested {expected} is not active (silent EP fallback is never "
            "accepted)",
            stage=stage,
        )
    return session


def session_providers(session: Any) -> tuple[str, ...]:
    """The active execution providers of a session (audit helper)."""
    try:
        return tuple(session.get_providers())
    except Exception:  # noqa: BLE001 - audit helper must not raise
        return ()
