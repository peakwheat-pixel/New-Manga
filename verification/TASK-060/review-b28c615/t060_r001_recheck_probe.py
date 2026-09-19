"""TASK-060 R-001 re-review probe: does the new component rule at the single
physical removal point close *every* route to a root-internal neighbour, or
only the lexical one?

    python t060_r001_recheck_probe.py <tree_root>

Runs one removal per syntax against a throwaway managed root in %TEMP%, and
reports for each whether the protected neighbour survived.  Read-only w.r.t.
the repository.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "src"))

from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ImmutablePathViolation,
    ManagedFileStorage,
)

print(f"== tree: {ROOT}  head: ", end="")
print(
    subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                   capture_output=True, text=True).stdout.strip()
)

tmp = Path(tempfile.mkdtemp(prefix="t060-r001-"))
storage = ManagedFileStorage(tmp / "managed")
storage.ensure_layout()
revisions = tmp / "managed" / "revisions"
revisions.mkdir(parents=True, exist_ok=True)
(tmp / "managed" / "books").mkdir(parents=True, exist_ok=True)


def neighbour(name: str) -> Path:
    path = revisions / name
    path.write_bytes(b"committed revision - must never be swept")
    return path


def attempt(label: str, target: str, victim: Path) -> None:
    try:
        storage.remove_managed(target)
        outcome = "remove_managed returned normally"
    except ImmutablePathViolation as error:
        outcome = f"refused: {str(error)[:78]}"
    except Exception as error:  # noqa: BLE001
        outcome = f"{type(error).__name__}: {str(error)[:70]}"
    print(
        f"   {label:<26} target={target!r:<46} neighbour survives?"
        f" {victim.exists():<5}  <- {outcome}"
    )


victim1 = neighbour("keep1.png")
attempt("dotdot slash", "books/../revisions/keep1.png", victim1)
victim2 = neighbour("keep2.png")
attempt("dotdot backslash", "books\\..\\revisions\\keep2.png", victim2)
victim3 = neighbour("keep3.png")
attempt("single dot component", "./revisions/keep3.png", victim3)
victim4 = neighbour("keep4.png")
attempt("absolute path in root", str(victim4), victim4)

# reparse route: a directory junction (mklink /J needs no privileges on
# Windows) inside the managed root, so the *lexical* target has no ".."
victim5 = neighbour("keep5.png")
junction = tmp / "managed" / "books" / "j"
result = subprocess.run(
    ["cmd", "/c", "mklink", "/J", str(junction), str(revisions)],
    capture_output=True, text=True,
)
if junction.is_dir():
    attempt("junction (no '..' text)", "books/j/keep5.png", victim5)
else:
    print(f"   junction route unavailable: {result.stdout.strip()!r}"
          f" {result.stderr.strip()!r}")

# file symlink route (needs developer mode / privileges on Windows)
victim6 = neighbour("keep6.png")
link = tmp / "managed" / "books" / "link6.png"
subprocess.run(
    ["cmd", "/c", "mklink", str(link), str(victim6)], capture_output=True
)
if link.is_symlink():
    attempt("file symlink", "books/link6.png", victim6)
else:
    print("   file-symlink route not creatable on this host (needs dev mode)")

print("   note: legit non-traversing managed path must still be removable:")
legit = tmp / "managed" / "books" / "b" / "original" / "p1.png"
legit.parent.mkdir(parents=True, exist_ok=True)
legit.write_bytes(b"x")
try:
    storage.remove_managed("books/b/original/p1.png")
    print(f"      remove_managed('books/b/original/p1.png') -> removed,"
          f" gone={not legit.exists()}")
except Exception as error:  # noqa: BLE001
    print(f"      REGRESSION: {type(error).__name__}: {error}")
