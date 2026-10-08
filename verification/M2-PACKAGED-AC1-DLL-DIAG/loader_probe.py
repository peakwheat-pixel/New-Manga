"""Load one hash-recorded candidate per isolated subprocess; never patch binaries."""
import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys

bundle = Path(sys.argv[1]).resolve()
assert "M2-PACKAGED-AC1-DLL-DIAG" in bundle.parts and "lab" in bundle.parts
path = (bundle / sys.argv[2]).resolve()
assert path.is_relative_to(bundle)
handles = [os.add_dll_directory(str(d)) for d in [bundle / "_internal", bundle / "_internal/PySide6", bundle / "_internal/shiboken6"]]
with path.open("rb") as f:
    sha = hashlib.file_digest(f, "sha256").hexdigest()
result = {"path": str(path), "sha256": sha, "python": sys.executable, "dll_dirs": [str(bundle / p) for p in ["_internal", "_internal/PySide6", "_internal/shiboken6"]]}
try:
    lib = ctypes.WinDLL(str(path))
    result.update(loaded=True)
except OSError as exc:
    result.update(loaded=False, winerror=exc.winerror, detail=str(exc))
print(json.dumps(result, ensure_ascii=True))
