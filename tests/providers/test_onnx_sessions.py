"""CORE-SLIM-2: ONNX Runtime session policy (shared by detect + OCR)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.providers import onnx_sessions  # noqa: E402
from ports.providers.errors import (  # noqa: E402
    ProviderError,
    ProviderInputError,
    ProviderNotConfigured,
    ProviderUnavailable,
)


class _FakeOptions:
    log_severity_level = 0
    graph_optimization_level = 0
    intra_op_num_threads = 0


class _FakeOrt:
    class GraphOptimizationLevel:
        ORT_ENABLE_ALL = 99

    SessionOptions = _FakeOptions

    def __init__(self, active_providers, available_providers=None):
        self._active = active_providers
        self._available = available_providers or [onnx_sessions.EP_CPU]
        self.last_providers = None

    def get_available_providers(self):
        return list(self._available)

    def InferenceSession(self, path, options, providers):  # noqa: N802 - ORT API
        self.last_providers = list(providers)

        class _Session:
            def __init__(self, active):
                self._active = active

            def get_providers(self):
                return list(self._active)

        return _Session(self._active)


def test_missing_model_file_is_not_configured(tmp_path: Path) -> None:
    with pytest.raises(ProviderNotConfigured, match="never downloaded"):
        onnx_sessions.create_session(tmp_path / "absent.onnx", device="cpu")


def test_unsupported_device_is_typed_input_error(tmp_path: Path) -> None:
    model = tmp_path / "model.onnx"
    model.write_bytes(b"stub")
    with pytest.raises(ProviderInputError, match="unsupported ONNX Runtime device"):
        onnx_sessions.resolve_execution_provider("tpu")
    with pytest.raises(ProviderInputError, match="unsupported ONNX Runtime device"):
        onnx_sessions.create_session(model, device="tpu")


def test_auto_prefers_directml_when_available(monkeypatch) -> None:
    monkeypatch.setattr(
        onnx_sessions,
        "available_providers",
        lambda stage="inference": (onnx_sessions.EP_DML, onnx_sessions.EP_CPU),
    )
    assert onnx_sessions.resolve_execution_provider("auto") == onnx_sessions.EP_DML
    assert onnx_sessions.resolve_execution_provider("cpu") == onnx_sessions.EP_CPU
    assert onnx_sessions.resolve_execution_provider("dml") == onnx_sessions.EP_DML


def test_auto_falls_back_to_cpu_without_directml(monkeypatch) -> None:
    monkeypatch.setattr(
        onnx_sessions,
        "available_providers",
        lambda stage="inference": (onnx_sessions.EP_CPU,),
    )
    assert onnx_sessions.resolve_execution_provider("auto") == onnx_sessions.EP_CPU


def test_explicit_cuda_on_a_dml_wheel_is_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(
        onnx_sessions,
        "available_providers",
        lambda stage="inference": (onnx_sessions.EP_DML, onnx_sessions.EP_CPU),
    )
    with pytest.raises(ProviderUnavailable, match="onnxruntime-directml"):
        onnx_sessions.resolve_execution_provider("cuda")


def test_session_accepts_the_active_expected_ep(tmp_path: Path, monkeypatch) -> None:
    model = tmp_path / "model.onnx"
    model.write_bytes(b"stub")
    fake = _FakeOrt(active_providers=[onnx_sessions.EP_CPU])
    monkeypatch.setattr(onnx_sessions, "_onnxruntime", lambda stage: fake)

    session = onnx_sessions.create_session(model, device="cpu")

    assert session.get_providers() == [onnx_sessions.EP_CPU]
    assert onnx_sessions.session_providers(session) == (onnx_sessions.EP_CPU,)


def test_silent_ep_fallback_fails_the_session(tmp_path: Path, monkeypatch) -> None:
    """The INFER baseline's EP_NOT_ACTIVE rule: no CPU number reported as GPU."""
    model = tmp_path / "model.onnx"
    model.write_bytes(b"stub")
    # ORT was asked for DML but reports CPU-only: this must fail closed.
    fake = _FakeOrt(
        active_providers=[onnx_sessions.EP_CPU],
        available_providers=[onnx_sessions.EP_DML, onnx_sessions.EP_CPU],
    )
    monkeypatch.setattr(onnx_sessions, "_onnxruntime", lambda stage: fake)

    with pytest.raises(ProviderError, match="fell back"):
        onnx_sessions.create_session(model, device="dml")


def test_missing_onnxruntime_is_provider_dependency_missing(monkeypatch) -> None:
    import infrastructure.providers.onnx_sessions as module

    def fake_import(name):
        if name == "onnxruntime":
            raise ImportError("no ORT here")
        return __import__(name)

    monkeypatch.setattr(module.importlib, "import_module", fake_import)
    with pytest.raises(Exception) as excinfo:
        module._onnxruntime("detection")
    assert "onnxruntime-directml" in str(excinfo.value)
