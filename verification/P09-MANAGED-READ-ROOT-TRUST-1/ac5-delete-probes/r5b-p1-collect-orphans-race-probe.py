"""R5b P1 #2 reproduction: collect_orphans deletes through a repointed directory.

render_preview.collect_orphans enumerates root/previews, checks the directory is
inside the derived root, then unlinks files inside it. R5b reported that replacing
`previews` with a junction after the containment check still deletes an outside file.

Both windows are real in the code: the containment check resolves the directory
(line 178), the enumeration walks that resolved path (line 181), and each unlink
resolves the name again (line 185). N-002's handle chain was never wired here.

The hook wins the race at Path.is_file, the check immediately before unlink. It
returns the real answer while swapping `previews` for a junction, so the check saw a
plain file inside the tree and the unlink resolves outside it.

injection_fired is reported separately, so a hook that fails to fire cannot be read
as a defended attack. Fixtures are under the workspace.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1")
sys.path.insert(0, str(REPO / "src"))

from infrastructure.resource_channel.render_preview import RenderPreviewPublisher  # noqa: E402

WS = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1\verification\P09-MANAGED-READ-ROOT-TRUST-1\_scratch\p1-orphan")
if WS.exists():
    for child in WS.iterdir():
        if child.is_dir() and child.is_symlink():
            child.unlink()
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

derived_root = WS / "derived"
(derived_root / "previews").mkdir(parents=True)
orphan = derived_root / "previews" / "orphan-1.png"
orphan.write_bytes(b"INSIDE ORPHAN")

outside = WS / "outside"
outside.mkdir(parents=True)
victim = outside / "orphan-1.png"
victim.write_bytes(b"OUTSIDE - must survive")


class _Catalog:
    """Minimal catalog: no entries, so every file under previews is an orphan."""

    def entries(self):
        return []

    def remove(self, resource_id: str) -> bool:
        return False


publisher = RenderPreviewPublisher(derived_root, _Catalog())
print("derived_root       =", derived_root)
print("orphan file        = previews/orphan-1.png")

injected: list[str] = []
orig_is_file = Path.is_file


def hooked_is_file(self: Path) -> bool:  # type: ignore[override]
    result = orig_is_file(self)
    if not injected and self.name == "orphan-1.png" and "previews" in str(self).replace("\\", "/"):
        injected.append(str(self))
        shutil.rmtree(derived_root / "previews")
        proc = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(derived_root / "previews"), str(outside)],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or not (derived_root / "previews").is_dir():
            raise SystemExit("INJECTION FAILED (junction): %s" % (proc.stdout or proc.stderr))
        if not (derived_root / "previews" / "orphan-1.png").is_file():
            raise SystemExit("INJECTION FAILED: junction does not expose the outside file")
    return result


Path.is_file = hooked_is_file  # type: ignore[assignment]
try:
    outcome = "NO_EXCEPTION"
    result = None
    try:
        result = publisher.collect_orphans()
    except Exception as error:  # noqa: BLE001
        outcome = "%s: %s" % (type(error).__name__, error)
finally:
    Path.is_file = orig_is_file  # type: ignore[assignment]

survived = orig_is_file(victim)
print("injection_fired    =", bool(injected))
print("outcome            =", outcome)
print("collect returned   =", result)
print("outside_survived   =", survived)
if not injected:
    print("RESULT             = INCONCLUSIVE (attack never ran)")
else:
    print("RESULT             =", "SAFE" if survived else "VULNERABLE")
