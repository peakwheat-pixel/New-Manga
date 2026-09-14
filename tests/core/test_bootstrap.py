from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"


def run_app(src_root: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(src_root)
    env["QT_QPA_PLATFORM"] = "offscreen"
    return subprocess.run(
        [sys.executable, "-m", "bootstrap.app", "--smoke-test"],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )


def test_smoke_startup_loads_qml_and_exits_zero() -> None:
    result = run_app(SRC_ROOT)
    assert result.returncode == 0, result.stderr


def test_missing_qml_returns_nonzero_with_path(tmp_path: Path) -> None:
    isolated_src = tmp_path / "src"
    shutil.copytree(SRC_ROOT / "bootstrap", isolated_src / "bootstrap")

    result = run_app(isolated_src)

    expected = isolated_src / "ui" / "qml" / "Main.qml"
    assert result.returncode != 0
    assert str(expected) in result.stderr
