"""P-01 exception-cleanup probe (M2-I1 Review R1).

Forces the Qt viewmodel layer to fail right after the Qt-free Core
assembly has returned an open SQLite connection, then reports whether
``assemble_services`` closed that connection (the historical
close-on-error semantics the split must preserve).

Discriminating usage (run on BOTH trees with a PySide6 interpreter):

    python probe_qt_assembly_cleanup.py <src-root>

- unfixed tree (b8741eb / a89447f: Qt layer assembled outside any
  close-on-error span): ``CONNECTION_CLOSED=False`` → FAIL.
- fixed tree (Qt layer wrapped in close-on-error): ``CONNECTION_CLOSED=True``
  → PASS.

The probe itself always exits 0; conclusions are carried by stdout.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile

_CHILD = """\
import shutil
import sys
sys.path.insert(0, sys.argv[1])
from pathlib import Path
import tempfile
import bootstrap.app as app_module
import infrastructure.sqlite.connection as sqlite_connection

closed = []
original_close = sqlite_connection.ThreadRoutedConnection.close

def _recording_close(self):
    closed.append(True)
    original_close(self)

sqlite_connection.ThreadRoutedConnection.close = _recording_close

def _failing_viewmodel():
    raise RuntimeError("forced-ui-assembly-failure")

app_module.NavigationViewModel = _failing_viewmodel

raised = False
root = Path(tempfile.mkdtemp(prefix="m2i1-p01-"))
try:
    app_module.assemble_services(root / "library.db", root / "managed")
except RuntimeError as error:
    raised = "forced-ui-assembly-failure" in str(error)
finally:
    import shutil
    shutil.rmtree(root, ignore_errors=True)

print(f"QT_LAYER_RAISED={raised}")
print(f"CONNECTION_CLOSED={closed[-1] if closed else False}")
verdict = "PASS" if (raised and closed) else "FAIL"
print(f"I1_AC3_AC5_EXCEPTION_CLEANUP= {verdict}")
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 0
    src_root = sys.argv[1]
    print(f"python: {sys.executable}")
    print(f"version: {sys.version.split()[0]}")
    print(f"src_root: {src_root}")
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", _CHILD, src_root],
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
        env=env,
    )
    sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stdout.write(result.stderr[-2000:])
        print(f"CHILD-EXIT={result.returncode}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
