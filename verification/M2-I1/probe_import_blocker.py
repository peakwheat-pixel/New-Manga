"""M2-I1 import-blocker probe (I1-AC1/AC6).

Runs ``import <module>`` in a subprocess whose ``sys.meta_path`` finder
raises ImportError for any ``PySide6`` / ``shiboken6`` / ``ui`` import,
then reports one PASS/FAIL line per module on stdout.

Discriminating usage (run on BOTH trees):

    python probe_import_blocker.py <src-root> bootstrap.core_assembly bootstrap.app

- delivery tree: ``bootstrap.core_assembly`` imports OK (the seam exists
  and is Qt-free at module scope); ``bootstrap.app`` is blocked on
  PySide6 (the blocker works — the pass above is not a broken probe).
- fixed base tree (6a68fde): ``bootstrap.core_assembly`` fails with
  ModuleNotFoundError (the module does not exist before M2-I1) while
  ``bootstrap.app`` is blocked identically — the before/after flip on
  core_assembly is the discrimination evidence.

The probe itself always exits 0; conclusions are carried by stdout.
"""

from __future__ import annotations

import os
import subprocess
import sys

_BLOCKED = {"PySide6", "shiboken6", "ui"}

_PREAMBLE = """\
import sys

_BLOCKED = {"PySide6", "shiboken6", "ui"}

class _ImportBlocker:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".", 1)[0] in _BLOCKED:
            raise ImportError(f"BLOCKED-IMPORT: {fullname}")
        return None

sys.meta_path.insert(0, _ImportBlocker())
"""


def probe(src_root: str, module: str) -> None:
    code = _PREAMBLE + (
        f"import {module}\n"
        "leaked = [m for m in sys.modules"
        " if m.split('.', 1)[0] in {'PySide6', 'shiboken6', 'ui'}]\n"
        "assert not leaked, f'Qt/UI leaked into sys.modules: {leaked}'\n"
        f"print('IMPORT-OK: {module}')\n"
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = src_root
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )
    if result.returncode == 0:
        print(f"PASS {module} (no PySide6/shiboken6/ui import)")
        return
    stderr_tail = result.stderr.strip().splitlines()
    reason = next(
        (line for line in reversed(stderr_tail) if line.strip()),
        "<no stderr>",
    )
    print(f"FAIL {module}: {reason}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(0)
    print(f"python: {sys.executable}")
    print(f"version: {sys.version.split()[0]}")
    print(f"src_root: {sys.argv[1]}")
    print(f"blocked roots: {sorted(_BLOCKED)}")
    for module_name in sys.argv[2:]:
        probe(sys.argv[1], module_name)
    sys.exit(0)
