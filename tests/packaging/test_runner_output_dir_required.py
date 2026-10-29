"""Regression tests for M2 runner explicit --output-dir guard (M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD).

Verifies that both verification/M2-RC2/run_e2e.py and packaging/m2ac5/run_clean_start_e2e.py
require an explicit --output-dir argument, rejecting omission with exit code 2 / usage error
before any runner side effect, and accepting explicit isolated paths during argument parsing.
Tests intercept execution immediately after parse_args and never start Gate, build, or installer work.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
RC2_RUNNER = ROOT / "verification" / "M2-RC2" / "run_e2e.py"
AC5_RUNNER = ROOT / "packaging" / "m2ac5" / "run_clean_start_e2e.py"


def load_module_from_path(name: str, path: Path) -> ModuleType:
    m2_conftest_path = ROOT / "tests" / "m2_resource_channel" / "conftest.py"
    m2_conftest_spec = importlib.util.spec_from_file_location("m2_resource_channel_conftest", m2_conftest_path)
    assert m2_conftest_spec is not None and m2_conftest_spec.loader is not None
    m2_conftest = importlib.util.module_from_spec(m2_conftest_spec)
    m2_conftest_spec.loader.exec_module(m2_conftest)

    old_conftest = sys.modules.get("conftest")
    sys.modules["conftest"] = m2_conftest
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        assert spec is not None and spec.loader is not None, f"Could not create spec for {path}"
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old_conftest is not None:
            sys.modules["conftest"] = old_conftest
        else:
            sys.modules.pop("conftest", None)


@pytest.fixture(scope="module")
def rc2_module() -> ModuleType:
    return load_module_from_path("rc2_runner_module", RC2_RUNNER)


@pytest.fixture(scope="module")
def ac5_module() -> ModuleType:
    return load_module_from_path("ac5_runner_module", AC5_RUNNER)


@pytest.mark.parametrize("runner_path", [RC2_RUNNER, AC5_RUNNER], ids=["rc2_run_e2e", "ac5_run_clean_start"])
def test_cli_omission_fails_usage_error_exit_2_subprocess(runner_path: Path):
    """AC1: Invoking runner CLI without --output-dir fails with exit 2 and usage error before work."""
    res = subprocess.run(
        [sys.executable, str(runner_path)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=30,
    )
    assert res.returncode == 2, f"Expected returncode 2, got {res.returncode}. stderr:\n{res.stderr}"
    err = res.stderr.lower()
    assert "--output-dir" in res.stderr
    assert "required" in err


def test_rc2_parser_omission_raises_system_exit_2(rc2_module: ModuleType):
    """AC1: In-process parser rejects missing --output-dir with SystemExit(2)."""
    parser = rc2_module.build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    assert exc_info.value.code == 2


def test_ac5_parser_omission_raises_system_exit_2(ac5_module: ModuleType):
    """AC1: In-process parser rejects missing --output-dir with SystemExit(2)."""
    parser = ac5_module.build_parser()
    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args([])
    assert exc_info.value.code == 2


def test_rc2_parser_accepts_explicit_output_dir(rc2_module: ModuleType, tmp_path: Path):
    """AC2: In-process parser accepts explicit --output-dir and options without starting runner work."""
    parser = rc2_module.build_parser()
    target_dir = tmp_path / "isolated_rc2_raw"
    args = parser.parse_args(["--output-dir", str(target_dir), "--skip-build"])
    assert args.output_dir == target_dir
    assert args.skip_build is True
    assert args.exe is None

    # Custom exe path
    args_exe = parser.parse_args(["--output-dir", str(target_dir), "--exe", "custom_desktop.exe"])
    assert args_exe.output_dir == target_dir
    assert args_exe.exe == "custom_desktop.exe"


def test_ac5_parser_accepts_explicit_output_dir(ac5_module: ModuleType, tmp_path: Path):
    """AC2: In-process parser accepts explicit --output-dir and options without starting runner work."""
    parser = ac5_module.build_parser()
    target_dir = tmp_path / "isolated_ac5_raw"
    args = parser.parse_args(["--output-dir", str(target_dir)])
    assert args.output_dir == target_dir
    assert args.installer == ac5_module.DEFAULT_INSTALLER

    # Custom installer path
    custom_installer = tmp_path / "custom_setup.exe"
    args_installer = parser.parse_args(["--output-dir", str(target_dir), "--installer", str(custom_installer)])
    assert args_installer.output_dir == target_dir
    assert args_installer.installer == custom_installer


def test_rc2_main_interception_after_parse_args(rc2_module: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """AC2/AC4: Intercept main immediately after parse_args succeeds; verifies RAW assignment without work."""
    class InterceptionSentinel(Exception):
        pass

    target_dir = tmp_path / "intercept_rc2_output"

    def stop_before_work(*_args, **_kwargs):
        raise InterceptionSentinel("stopped after parse_args before any runner work")

    # Intercept tempfile.mkdtemp which is called right after RAW = args.output_dir.resolve()
    monkeypatch.setattr("tempfile.mkdtemp", stop_before_work)

    with pytest.raises(InterceptionSentinel):
        rc2_module.main(["--output-dir", str(target_dir)])

    assert rc2_module.RAW == target_dir.resolve()


def test_ac5_main_interception_after_parse_args(ac5_module: ModuleType, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """AC2/AC4: Intercept main immediately after parse_args succeeds; verifies RAW assignment without work."""
    class InterceptionSentinel(Exception):
        pass

    target_dir = tmp_path / "intercept_ac5_output"

    def stop_before_work(*_args, **_kwargs):
        raise InterceptionSentinel("stopped after parse_args before any runner work or directory creation")

    # Intercept Path.mkdir so execution stops before creating directories
    monkeypatch.setattr(Path, "mkdir", stop_before_work)

    with pytest.raises(InterceptionSentinel):
        ac5_module.main(["--output-dir", str(target_dir)])

    assert ac5_module.RAW == target_dir.resolve()
