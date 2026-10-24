"""PLUGIN-RUNTIME-PACKAGED-PYTHON-1: packaged hook interpreter resolution."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from infrastructure.plugins.service import PluginError, _hook_interpreter  # noqa: E402

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows packaging")


def _fake_frozen(monkeypatch, executable: Path) -> None:
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(executable), raising=False)


def test_source_runs_use_the_running_interpreter(monkeypatch) -> None:
    monkeypatch.delattr(sys, "frozen", raising=False)
    assert _hook_interpreter() == sys.executable


def test_environment_override_wins(monkeypatch, tmp_path) -> None:
    sidecar = tmp_path / "sidecar" / "core-sidecar.exe"
    sidecar.parent.mkdir(parents=True)
    sidecar.write_bytes(b"stub")
    bundled = tmp_path / "python" / "python.exe"
    bundled.parent.mkdir(parents=True)
    shutil.copy2(sys.executable, bundled)
    _fake_frozen(monkeypatch, sidecar)
    monkeypatch.setenv("NEWMANGA_PLUGIN_PYTHON", str(bundled))
    assert _hook_interpreter() == str(bundled)


def test_missing_environment_override_fails_closed(monkeypatch, tmp_path) -> None:
    sidecar = tmp_path / "core-sidecar.exe"
    sidecar.write_bytes(b"stub")
    _fake_frozen(monkeypatch, sidecar)
    monkeypatch.setenv("NEWMANGA_PLUGIN_PYTHON", str(tmp_path / "missing" / "python.exe"))
    with pytest.raises(PluginError) as excinfo:
        _hook_interpreter()
    assert excinfo.value.code == "PLUGIN_HOOK_UNAVAILABLE"


def test_sibling_interpreter_is_found(monkeypatch, tmp_path) -> None:
    sidecar = tmp_path / "core-sidecar.exe"
    sidecar.write_bytes(b"stub")
    sibling = tmp_path / "python.exe"
    shutil.copy2(sys.executable, sibling)
    _fake_frozen(monkeypatch, sidecar)
    monkeypatch.delenv("NEWMANGA_PLUGIN_PYTHON", raising=False)
    assert _hook_interpreter() == str(sibling)


def test_bundled_python_directory_is_found(monkeypatch, tmp_path) -> None:
    sidecar = tmp_path / "core-sidecar.exe"
    sidecar.write_bytes(b"stub")
    bundled = tmp_path / "python" / "python.exe"
    bundled.parent.mkdir(parents=True)
    shutil.copy2(sys.executable, bundled)
    _fake_frozen(monkeypatch, sidecar)
    monkeypatch.delenv("NEWMANGA_PLUGIN_PYTHON", raising=False)
    assert _hook_interpreter() == str(bundled)


def test_no_interpreter_fails_closed_without_system_fallback(monkeypatch, tmp_path) -> None:
    sidecar = tmp_path / "core-sidecar.exe"
    sidecar.write_bytes(b"stub")
    _fake_frozen(monkeypatch, sidecar)
    monkeypatch.delenv("NEWMANGA_PLUGIN_PYTHON", raising=False)
    with pytest.raises(PluginError) as excinfo:
        _hook_interpreter()
    assert excinfo.value.code == "PLUGIN_HOOK_UNAVAILABLE"
