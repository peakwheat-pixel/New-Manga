"""Fixtures/helpers for the document import suite (TASK-023)."""

from __future__ import annotations

import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
SRC_ROOT = TESTS_DIR.parents[1] / "src"
for entry in (str(TESTS_DIR), str(SRC_ROOT)):
    if entry not in sys.path:
        sys.path.insert(0, entry)
