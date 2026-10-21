"""N-002 reproduction probe: replace the parent directory between check and unlink.

Run inside an isolated root.  Prints three facts so the race is either observed
or not - never assumed:

    race_hook_fired         did the hook get to swap the directory in time
    unlink_returned         what the helper reported
    outside_survived        is the file OUTSIDE the root still there

The file outside the root is the one that must never be touched.  If it is gone,
the helper deleted something the catalog entry never referred to.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1") / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import infrastructure.sqlite.library as lib  # noqa: E402

root = Path(os.environ["N002_ROOT"]).resolve()
outside = Path(os.environ["N002_OUTSIDE"]).resolve()

target_dir = root / "pages"
target_dir.mkdir(parents=True, exist_ok=True)
(target_dir / "page-original.png").write_bytes(b"inside bytes")

outside.mkdir(parents=True, exist_ok=True)
(outside / "page-original.png").write_bytes(b"OUTSIDE BYTES - must survive")

fired: list[str] = []
victim_ok = {"exists": True}

orig_is_file = Path.is_file


def hooked_is_file(self: Path) -> bool:  # type: ignore[override]
    """Swap the parent for a junction right after the last check passes.

    is_file() is the last path resolution before unlink(), so returning its real
    answer while replacing the directory reproduces the window exactly: the check
    saw a plain file under root, the unlink resolves the path again and lands
    wherever the junction now points.
    """
    result = orig_is_file(self)
    if not fired and self.name == "page-original.png" and "pages" in str(self):
        fired.append(str(self))
        victim_ok["exists"] = orig_is_file(outside / "page-original.png")
        shutil.rmtree(target_dir)
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target_dir), str(outside)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print("junction_failed:", proc.stdout.strip(), proc.stderr.strip())
    return result


Path.is_file = hooked_is_file  # type: ignore[assignment]
try:
    returned = lib.unlink_preview_without_following("pages/page-original.png", root)
finally:
    Path.is_file = orig_is_file  # type: ignore[assignment]

survived = orig_is_file(outside / "page-original.png")
print("race_hook_fired   =", bool(fired))
print("unlink_returned   =", returned)
print("outside_survived  =", survived)
print("RESULT            =", "VULNERABLE" if not survived else "SAFE")
