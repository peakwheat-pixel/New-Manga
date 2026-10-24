"""Test configuration and path setup for packaging test suite (T3.2.1-REPAIR-10)."""

from pathlib import Path
import sys

# Ensure src/ is on sys.path so packaging tests do not depend on external PYTHONPATH (F-3(b))
ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
