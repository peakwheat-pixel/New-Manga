"""R5b P1 #1 reproduction: remove_managed is redirected AFTER its checks pass.

R5b reported this and said it reproduced it. Reading the code agrees: line 187 calls
Path.is_file() and line 188 calls absolute.unlink() - two separate resolutions of the
same name, with room between them to repoint the directory. The lexical baseline fix
several rounds ago does not close that, because it only changes how the BOUND is
computed, not how many times the path is walked.

The race is won by hooking Path.is_file, which is the check immediately before the
delete. The hook returns the real answer and swaps the parent directory for a
junction to an outside tree, so the check saw a plain file inside the root and the
unlink then resolves the name somewhere else.

injection_fired is printed separately from outside_survived, so a hook that fails to
fire can never be read as a defended attack.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1")
sys.path.insert(0, str(REPO / "src"))

from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402

WS = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1\verification\P09-MANAGED-READ-ROOT-TRUST-1\_scratch\p1-race")
if WS.exists():
    for child in WS.iterdir():
        if child.is_dir() and child.is_symlink():
            child.unlink()
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

root = WS / "managed"
(root / "pages").mkdir(parents=True)
(root / "pages" / "page-original-p1.png").write_bytes(b"INSIDE")

outside = WS / "outside"
outside.mkdir(parents=True)
(outside / "page-original-p1.png").write_bytes(b"OUTSIDE - must survive")

storage = ManagedFileStorage(root)
print("root               =", root)
print("relative target    = pages/page-original-p1.png")

injected: list[str] = []
orig_is_file = Path.is_file
victim = outside / "page-original-p1.png"


def hooked_is_file(self: Path) -> bool:  # type: ignore[override]
    result = orig_is_file(self)
    if not injected and self.name == "page-original-p1.png" and os.sep + "managed" in str(self):
        injected.append(str(self))
        shutil.rmtree(root / "pages")
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(root / "pages"), str(outside)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not (root / "pages").is_dir():
            raise SystemExit("INJECTION FAILED (junction): %s" % (proc.stdout or proc.stderr))
        if not (root / "pages" / "page-original-p1.png").is_file():
            raise SystemExit("INJECTION FAILED: junction does not expose the outside file")
    return result


Path.is_file = hooked_is_file  # type: ignore[assignment]
try:
    raised = "NO_EXCEPTION"
    try:
        storage.remove_managed("pages/page-original-p1.png")
    except Exception as error:  # noqa: BLE001
        raised = type(error).__name__
finally:
    Path.is_file = orig_is_file  # type: ignore[assignment]

survived = orig_is_file(victim)
print("injection_fired    =", bool(injected))
print("outcome            =", raised)
print("outside_survived   =", survived)
if not injected:
    print("RESULT             = INCONCLUSIVE (attack never ran)")
else:
    print("RESULT             =", "SAFE" if survived else "VULNERABLE")
