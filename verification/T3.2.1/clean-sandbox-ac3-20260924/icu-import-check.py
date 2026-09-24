from pathlib import Path
import hashlib
import pefile
import sys

package = Path(sys.argv[1])
poppler = Path(sys.argv[2])
system32 = Path(sys.argv[3])
qtcore = package / "_internal" / "PySide6" / "Qt6Core.dll"
pe = pefile.PE(str(qtcore), fast_load=True)
pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]])
icu = next(item for item in pe.DIRECTORY_ENTRY_IMPORT if item.dll.lower() == b"icuuc.dll")
required = [item.name.decode("ascii", "replace") for item in icu.imports if item.name]
print(f"Qt6Core.dll={qtcore}")
print(f"Qt6Core_ICU_import_count={len(required)}")
print("Qt6Core_ICU_imports=" + ", ".join(required))
for label, path in (("package", package / "_internal" / "icuuc.dll"), ("host_poppler_PATH", poppler), ("Windows_System32", system32)):
    dep = pefile.PE(str(path), fast_load=True)
    dep.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    exports = {item.name for item in dep.DIRECTORY_ENTRY_EXPORT.symbols if item.name}
    missing = [name for name in required if name.encode() not in exports]
    digest = hashlib.sha256(path.read_bytes()).hexdigest().upper()
    print(f"{label}_path={path}")
    print(f"{label}_sha256={digest}")
    print(f"{label}_export_count={len(exports)}")
    print(f"{label}_missing_required={len(missing)}: {', '.join(missing)}")
