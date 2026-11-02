"""Test configuration and path setup for the export suite.

Mirrors tests/packaging/conftest.py: put src/ on sys.path so this suite can be
run on its own. Without it, `python -m pytest tests/export` fails to collect
unless PYTHONPATH happens to be set - and the full run only passed by
collection order, which is luck, not design. Flagged by ZCode review P2-2.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
