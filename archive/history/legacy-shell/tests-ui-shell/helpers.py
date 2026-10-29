"""Shared test helpers for the ui_shell suite.

Injects ``src`` into sys.path first (same convention as tests/editing and
tests/rendering). The module name is intentionally *not* ``helpers``-only:
other suites own that bare name, so imports here are always
``import helpers`` from within tests/ui_shell where conftest has already
put this directory first on sys.path — the editing suite's region_helpers
pattern. To avoid the cross-suite clash seen in TASK-014, this file is
named ``helpers.py`` but only imported as a *relative sibling* by ui_shell
modules after conftest prepends THIS directory to sys.path.
"""

from __future__ import annotations

import sys
from pathlib import Path

# This directory first, then src — siblings import bare module names.
THIS_DIR = Path(__file__).resolve().parent
SRC_ROOT = THIS_DIR.parents[1] / "src"
for entry in (str(THIS_DIR), str(SRC_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)
