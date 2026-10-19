"""N-002 reproduction probe against the handle chain.

The first version hooked ``Path.is_file`` because that was the last path
resolution before ``unlink()`` in the old implementation.  Once the delete goes
through handles, ``is_file`` is never called, the hook never fires, and a SAFE
result would prove nothing - the attack simply did not run.

So the injection point moved to ``_open_relative``: after the subdirectory handle
is obtained, the directory on disk is swapped for a junction to an outside folder.
That is a genuinely adversarial moment - the chain has already resolved and
verified ``pages`` once, and now the name points somewhere else.  If the design is
right, the delete still acts on the handle it already holds and the outside file
survives.

Prints the same three facts as before, plus whether the injection actually
happened, so a non-firing hook can never be mistaken for a defended attack.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

import infrastructure.filesystem.win_unlink as w  # noqa: E402
import infrastructure.sqlite.library as lib  # noqa: E402

root = Path(os.environ["N002_ROOT"]).resolve()
outside = Path(os.environ["N002_OUTSIDE"]).resolve()

target_dir = root / "pages"
target_dir.mkdir(parents=True, exist_ok=True)
(target_dir / "page-original.png").write_bytes(b"inside bytes")

outside.mkdir(parents=True, exist_ok=True)
(outside / "page-original.png").write_bytes(b"OUTSIDE BYTES - must survive")

injected: list[str] = []
orig_open_relative = w._open_relative


def hooked_open_relative(parent: int, name: str, *, directory: bool) -> int | None:
    """Swap the directory for a junction right after its handle is opened."""
    handle = orig_open_relative(parent, name, directory=directory)
    if handle is not None and name == "pages" and not injected:
        injected.append(name)
        shutil.rmtree(target_dir)
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target_dir), str(outside)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            print("junction_failed:", proc.stdout.strip(), proc.stderr.strip())
    return handle


w._open_relative = hooked_open_relative  # type: ignore[assignment]
try:
    returned = lib.unlink_preview_without_following("pages/page-original.png", root)
finally:
    w._open_relative = orig_open_relative  # type: ignore[assignment]

survived = (outside / "page-original.png").is_file()
print("injection_fired   =", bool(injected))
print("unlink_returned   =", returned)
print("outside_survived  =", survived)
if not injected:
    print("RESULT            = INCONCLUSIVE (attack never ran)")
else:
    print("RESULT            =", "SAFE" if survived else "VULNERABLE")
