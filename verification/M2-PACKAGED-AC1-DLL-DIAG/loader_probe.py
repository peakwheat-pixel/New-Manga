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
if len(sys.argv) > 3 and sys.argv[3] == "system-icu":
    system_icu = Path(os.environ["SystemRoot"]) / "System32/icuuc.dll"
    preloaded = ctypes.WinDLL(str(system_icu))
    result["preloaded_system_icu"] = str(system_icu)
try:
    lib = ctypes.WinDLL(str(path))
    result.update(loaded=True)
    if path.name == "Qt6Core.dll":
        api = ctypes.WinDLL("kernel32", use_last_error=True).GetProcAddress
        api.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        api.restype = ctypes.c_void_p
        names = [b"?width@QSize@@QEBAHXZ", b"?writeQSizeType@QDataStream@@CA_NAEAV1@_J@Z"]
        result["native_export_lookup"] = {n.decode(): bool(api(lib._handle, n)) for n in names}
except OSError as exc:
    result.update(loaded=False, winerror=exc.winerror, detail=str(exc))
print(json.dumps(result, ensure_ascii=True))
