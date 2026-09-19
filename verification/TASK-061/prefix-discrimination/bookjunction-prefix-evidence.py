"""Pre-fix evidence helper (Qoder review request): prove that on the
pre-fix tree the book-level junction traversal (books/book-twin ->
books/book-1) not only is NOT refused but actually deletes the protected
original.  Run against a pre-fix checkout with its ``src`` on sys.path:

    python verification/TASK-061/prefix-discrimination/bookjunction-prefix-evidence.py

It prints the removal outcome and the target's existence — the two lines
Qoder asked to see as an artefact.  It is not a pytest case: the test
case itself keeps its hard ``pytest.raises`` assertion.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src"
sys.path.insert(0, str(SRC))

from infrastructure.filesystem.managed_storage import (  # noqa: E402
    ImmutablePathViolation,
    ManagedFileStorage,
)

tmp = Path(tempfile.mkdtemp(prefix="t061-junction-evidence-"))
storage = ManagedFileStorage(tmp / "managed")
storage.ensure_layout()
protected_rel = "books/book-1/chapters/chapter-1/original/keep.png"
protected = tmp / "managed" / Path(*protected_rel.split("/"))
protected.parent.mkdir(parents=True)
protected.write_bytes(b"PROTECTED ORIGINAL")

twin = tmp / "managed" / "books" / "book-twin"
made = subprocess.run(
    # junction target: the book-1 directory (original's parents[2])
    ["cmd", "/c", "mklink", "/J", str(twin), str(protected.parent.parents[2])],
    capture_output=True,
)
assert made.returncode == 0, made.stderr

try:
    storage.remove_managed("books/book-twin/chapters/chapter-1/original/keep.png")
    print("remove_managed returned normally: NO typed refusal")
except ImmutablePathViolation as error:
    print(f"typed refusal: {error}")
print(f"protected original still exists: {protected.is_file()}")
