"""R5 P1 reproduction: remove_managed() redirected by an ancestor junction.

Codex R5 read the code and described this; nobody has run it. The claim:

  managed_storage.py:147  absolute = Path(self.absolute_path(rel)).resolve()
  managed_storage.py:148  root     = self._root.resolve()
  managed_storage.py:150  absolute.relative_to(root)          <- containment
  managed_storage.py:167  probe = self._root                  <- UNRESOLVED
  managed_storage.py:171  probe.lstat()                       <- reparse walk

Both guards are sound on their own, but one uses resolved paths and the other uses
the raw root. With a junction ABOVE the root, resolve() puts both the target and the
root under the junction's destination, so containment passes; and the reparse walk
starts at the unresolved root, so the junction is an ancestor of everything it walks
and never appears on a segment it inspects.

Fixture is created under the workspace per the path rules. Nothing in the repo is
modified.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga")
sys.path.insert(0, str(REPO / "src"))

from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402

ws = Path(r"G:\CODEX\New Manga.workspace\agent-output\coordinator\p1-repro")
if ws.exists():
    for child in ws.iterdir():
        if child.is_dir() and child.is_symlink():
            child.unlink()
    shutil.rmtree(ws, ignore_errors=True)
ws.mkdir(parents=True)

# The managed root lives OUTSIDE the junction target, so a correct implementation
# must refuse to touch the outside file.
trusted = ws / "trusted"
managed_root = trusted / "derived"
(managed_root / "pages").mkdir(parents=True)
(manged := managed_root / "pages" / "page-original.png").write_bytes(b"INSIDE - may be deleted")

outside = ws / "outside"
(outside / "derived" / "pages").mkdir(parents=True)
outside_file = outside / "derived" / "pages" / "page-original.png"
outside_file.write_bytes(b"OUTSIDE - must survive")

storage = ManagedFileStorage(managed_root)
print("managed_root       =", managed_root)
print("inside file exists =", manged.is_file())

# Replace the ANCESTOR of the managed root with a junction to `outside`.
shutil.rmtree(trusted)
proc = subprocess.run(
    ["cmd", "/c", "mklink", "/J", str(trusted), str(outside)],
    capture_output=True, text=True,
)
if proc.returncode != 0 or not trusted.is_dir():
    raise SystemExit("INJECTION FAILED: junction not created: %s" % (proc.stdout or proc.stderr))
if not (trusted / "derived" / "pages" / "page-original.png").is_file():
    raise SystemExit("INJECTION FAILED: junction does not expose the outside file")
print("injection          = ancestor 'trusted' is now a junction to 'outside'")
print("resolve(root)      =", managed_root.resolve())

result = "NOT_RAISED"
try:
    storage.remove_managed("pages/page-original.png")
except Exception as error:  # noqa: BLE001 - the refusal is the safe outcome
    result = "%s: %s" % (type(error).__name__, error)

survived = outside_file.is_file()
print("remove_managed     =", result)
print("outside_survived   =", survived)
print("RESULT             =", "SAFE" if survived else "VULNERABLE")
