from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

COMMIT = "b03bf0d87bf8eae31650c36b2cc0d995236eaa8b"
ROOT = Path(__file__).resolve().parents[2]

files = subprocess.run(
    ["git", "-C", str(ROOT), "diff-tree", "--no-commit-id", "--name-only", "-r", COMMIT],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()
if len(files) != 12:
    raise SystemExit(f"expected 12 files in implementation commit, found {len(files)}")

print(f"commit={COMMIT}")
print("method=SHA256 of raw Git blob bytes from git cat-file (checkout-EOL independent)")
for path in files:
    blob = subprocess.run(
        ["git", "-C", str(ROOT), "cat-file", "blob", f"{COMMIT}:{path}"],
        check=True,
        capture_output=True,
    ).stdout
    print(f"{hashlib.sha256(blob).hexdigest()}  {path}")
