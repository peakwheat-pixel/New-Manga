"""TASK-055 diagnostics tests: self-contained suite directory.

Adds ``src`` to ``sys.path`` the same way the other suites do, so
collection order cannot matter."""

from __future__ import annotations

import sys
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
