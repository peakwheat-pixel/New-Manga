"""FEA-12 D-flow simulation slice: isolated fixtures.

Every fixture stays under pytest's ``tmp_path`` (ADJ-2026-11-05 §D7 item 3:
pytest ``tmp_path`` or the workload temp root are the only allowed scratch
roots).  The simulated recycle bin is only ever constructed over a dedicated
``isolated-root`` directory inside that temp tree, and the runtime sentinel
tree lives *outside* it as a sibling — no user data, no system folder and no
real recycle-bin location is referenced anywhere.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture()
def isolated_root(tmp_path: Path) -> Path:
    """The only directory the simulated recycle bin is allowed to touch."""
    root = tmp_path / "isolated-root"
    root.mkdir()
    return root


@pytest.fixture()
def outside_tree(tmp_path: Path) -> Path:
    """Runtime sentinel outside the isolated root: must never change."""
    outside = tmp_path / "outside-root"
    (outside / "user-sources").mkdir(parents=True)
    (outside / "user-sources" / "chapter-01.png").write_bytes(
        b"ORIGINAL PIXELS 01"
    )
    (outside / "user-sources" / "chapter-02.png").write_bytes(
        b"ORIGINAL PIXELS 02"
    )
    (outside / "notes.txt").write_text("keep me verbatim", encoding="utf-8")
    return outside
