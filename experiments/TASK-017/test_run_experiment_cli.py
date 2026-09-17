import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_cli_summary_is_safe_on_ascii_stdout(tmp_path: Path) -> None:
    source_dir = Path(__file__).parent
    run_dir = tmp_path / "TASK-017"
    run_dir.mkdir()
    for name in ("run_experiment.py", "mock_provider.py", "protocol.py", "samples.py"):
        shutil.copy2(source_dir / name, run_dir / name)

    script = run_dir / "run_experiment.py"
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "ascii"

    completed = subprocess.run(
        [sys.executable, str(script)],
        cwd=run_dir,
        env=env,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr.decode("ascii", errors="replace")
    completed.stdout.decode("ascii")
