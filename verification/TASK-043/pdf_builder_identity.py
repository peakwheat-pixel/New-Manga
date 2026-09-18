"""TASK-043 evidence: the ``_assemble_pdf`` extraction is output-preserving.

Loads the *committed* (base) ``tests/import_formats/test_document_import.py``
and the working-tree one as two independent modules and compares the bytes
produced by ``minimal_pdf`` — so the F-3/F-9 additions cannot have changed
the fixture every existing TASK-023 test depends on.

Usage: python pdf_builder_identity.py <path-to-base-copy-of-the-test-file>

The base copy is produced by:
    git show HEAD:tests/import_formats/test_document_import.py > <path>
"""

from __future__ import annotations

import hashlib
import importlib.util
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[2]
for entry in (str(WORKTREE / "src"), str(WORKTREE / "tests" / "import_formats")):
    if entry not in sys.path:
        sys.path.insert(0, entry)


def _load(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


base_path = Path(sys.argv[1]).resolve()
old = _load("base_test_document_import", base_path)
new = _load("worktree_test_document_import", WORKTREE / "tests" / "import_formats" / "test_document_import.py")

print("base module :", base_path)
print("worktree    :", WORKTREE / "tests" / "import_formats" / "test_document_import.py")
identical = True
for n_pages in (1, 2, 3, 5, 8):
    old_bytes = old.minimal_pdf(n_pages)
    new_bytes = new.minimal_pdf(n_pages)
    same = old_bytes == new_bytes
    identical = identical and same
    print(
        f"minimal_pdf({n_pages}): len={len(new_bytes)} "
        f"base_sha256={hashlib.sha256(old_bytes).hexdigest()[:16]} "
        f"worktree_sha256={hashlib.sha256(new_bytes).hexdigest()[:16]} "
        f"identical={same}"
    )
print("ALL IDENTICAL:", identical)
