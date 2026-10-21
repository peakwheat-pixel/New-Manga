"""R5 P1: cleanup_book_files must refuse when a junction sits at the managed root.

library.py:1149-1168 guards permanent deletion of a book's managed files. It builds
books_base as the bound and resolved_dir as the candidate and requires resolved_dir
to be inside books_base, not equal to it, to exist, and not itself a reparse point.
The guard was defeated by the same thing as N-004: the bound was resolved, so a
junction above the managed root moved bound and candidate together.

An earlier version of this probe swapped an ancestor of the managed root and failed
with WinError 32 - library.db lives in that ancestor and SQLite holds it open, so the
directory cannot be replaced. The junction therefore goes at the managed root itself,
which contains no open files and which exercises the same containment comparison:
the candidate resolves through the junction into the outside tree while the bound
stays where it was configured.

Fixtures live under the workspace; nothing in the repo is modified.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1")
sys.path.insert(0, str(REPO / "src"))

from bootstrap.core_service import assemble_production_core  # noqa: E402

WS = Path(r"G:\CODEX\New Manga.workspace\worktrees\P09-MANAGED-READ-ROOT-TRUST-1\verification\P09-MANAGED-READ-ROOT-TRUST-1\_scratch\p1-cleanup")
if WS.exists():
    for child in WS.iterdir():
        if child.is_dir() and child.is_symlink():
            child.unlink()
    shutil.rmtree(WS, ignore_errors=True)
WS.mkdir(parents=True)

# The database lives in WS/data; the managed root is WS/data/managed.
data_root = WS / "data"
data_root.mkdir(parents=True)
core = assemble_production_core(data_root)
storage = core.storage
managed = Path(storage.root)
print("storage.root       =", managed)

rel = "books/b1/pages/page-original-p1.png"
(managed / rel).parent.mkdir(parents=True, exist_ok=True)
(managed / rel).write_bytes(b"INSIDE - controlled copy")

# Outside tree mirrors what the junction will expose, including the junction target's
# own name under WS so the two paths differ only by the link.
outside = WS / "outside"
outside.mkdir(parents=True)
(outside / rel).parent.mkdir(parents=True, exist_ok=True)
(outside / rel).write_bytes(b"OUTSIDE - must survive")

# Replace the managed root itself with a junction. Its parent holds library.db, which
# is open, so only the managed directory may move.
real_managed = WS / "managed-real"
os.rename(managed, real_managed)
proc = subprocess.run(["cmd", "/c", "mklink", "/J", str(managed), str(outside)],
                      capture_output=True, text=True)
if proc.returncode != 0 or not managed.is_dir():
    raise SystemExit("INJECTION FAILED (junction): %s" % (proc.stdout or proc.stderr))
if not (managed / rel).is_file():
    raise SystemExit("INJECTION FAILED: junction does not expose the outside file")
print("injection          = managed root is now a junction to 'outside'")
print("bound (abspath)    =", Path(os.path.abspath(str(managed))) / "books")
print("candidate resolve  =", (managed / rel).parent.resolve())

deleted = core.library._repo.cleanup_book_files("b1", [rel], storage)

survived = (outside / rel).is_file()
print("cleanup returned   =", deleted)
print("outside_survived   =", survived)
print("RESULT             =", "SAFE" if survived else "VULNERABLE")
