"""Compare named imports with candidate exports using the existing build-env pefile."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import pefile

bundle = Path(sys.argv[1]).resolve()
assert "M2-PACKAGED-AC1-DLL-DIAG" in bundle.parts and "lab" in bundle.parts
report = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(), "command": sys.argv, "pefile_version": pefile.__version__, "bundle": str(bundle), "note": "Static candidate symbol matching; no loader search/forwarder claim", "binaries": []}
dirs = [bundle / "_internal/PySide6", bundle / "_internal", bundle / "_internal/shiboken6", Path(os.environ["SystemRoot"]) / "System32"]
for rel in ["_internal/PySide6/Qt6Core.dll", "_internal/PySide6/Qt6Gui.dll"]:
    path = bundle / rel
    binary = pefile.PE(str(path), fast_load=True)
    binary.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
    row = {"binary": rel, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "dependencies": []}
    for desc in getattr(binary, "DIRECTORY_ENTRY_IMPORT", []):
        name = desc.dll.decode("ascii")
        candidate = next((d / name for d in dirs if (d / name).is_file()), None)
        edge = {"dll": name, "candidate": str(candidate) if candidate else None}
        if candidate:
            exports = pefile.PE(str(candidate), fast_load=True)
            exports.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
            symbols = getattr(exports, "DIRECTORY_ENTRY_EXPORT", None)
            names = {s.name for s in symbols.symbols if s.name} if symbols else set()
            ordinals = {s.ordinal for s in symbols.symbols} if symbols else set()
            missing = [i.name.decode("ascii") if i.name else "ordinal:" + str(i.ordinal) for i in desc.imports if (i.name not in names if i.name else i.ordinal not in ordinals)]
            edge.update(sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(), imported=len(desc.imports), missing_symbols=missing)
            exports.close()
        row["dependencies"].append(edge)
    binary.close()
    report["binaries"].append(row)
Path(sys.argv[2]).write_text(json.dumps(report, indent=2), encoding="utf-8")
for row in report["binaries"]:
    for edge in row["dependencies"]:
        if edge.get("missing_symbols"):
            print(row["binary"], edge["dll"], len(edge["missing_symbols"]), edge["missing_symbols"][:5])
