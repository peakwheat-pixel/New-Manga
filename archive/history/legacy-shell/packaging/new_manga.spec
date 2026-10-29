# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for New Manga Windows onedir distribution (T3.2.1)."""

from pathlib import Path
import os
import sys

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Resolve repository paths from spec location
SPEC_PATH = Path(SPEC).resolve()
SPEC_DIR = SPEC_PATH.parent
REPO_ROOT = SPEC_DIR.parent
SRC_DIR = REPO_ROOT / "src"

block_cipher = None

# Ensure src is in sys.path during spec execution
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Define source tree and relative asset paths
# Entry point: src/bootstrap/app.py
# QML asset tree: src/ui/qml
ENTRY_POINT = str(REPO_ROOT / "src/bootstrap/app.py")
QML_DIR = str(REPO_ROOT / "src/ui/qml")

# Collect project QML tree into 'ui/qml'
datas = [
    (QML_DIR, "ui/qml"),
]

# Collect complete PySide6 data files including plugins and QML modules
datas += collect_data_files("PySide6", include_py_files=False)

hiddenimports = [
    "PySide6.QtCore",
    "PySide6.QtGui",
    "PySide6.QtQml",
    "PySide6.QtQuick",
    "PySide6.QtQuickControls2",
    "shiboken6",
]

# Collect all project internal submodules
for pkg in ["application", "domain", "infrastructure", "ports", "ui"]:
    hiddenimports += collect_submodules(pkg)

# Exclude testing framework modules and test packages (F-012, R-009).
# Note: tests reside outside SRC_DIR and are never included in datas or pathex.
excludes = [
    "pytest",
    "_pytest",
    "tests",
]

a = Analysis(
    [ENTRY_POINT],
    pathex=[str(SRC_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# T3.2.1-REPAIR-9: Sanitize binaries against incompatible ICU injection from host PATH.
# Safely inspect any candidate icuuc.dll collected from host PATH and verify its exports
# satisfy all Qt6Core.dll import requirements. Reject if symbols are missing.
checker_script = SPEC_DIR / "check_qt_closure.py"
qt_closure_checker = None
if checker_script.is_file():
    import importlib.util
    chk_spec = importlib.util.spec_from_file_location("spec_qt_closure_checker", str(checker_script))
    if chk_spec and chk_spec.loader:
        qt_closure_checker = importlib.util.module_from_spec(chk_spec)
        chk_spec.loader.exec_module(qt_closure_checker)

filtered_binaries = []
for item in a.binaries:
    dest, src, type_ = item
    dest_name = Path(dest).name.lower()
    if dest_name in ("icuuc.dll", "icuin.dll"):
        is_compatible = False
        if qt_closure_checker and dest_name == "icuuc.dll":
            qt_core_src = next((s for d, s, t in a.binaries if Path(d).name.lower() == "qt6core.dll"), None)
            if qt_core_src:
                try:
                    needed = qt_closure_checker.get_qt_core_icu_imports(Path(qt_core_src))
                    exports = qt_closure_checker.get_pe_exports(Path(src))
                    missing = [sym for sym in needed if sym not in exports]
                    if not missing:
                        is_compatible = True
                    else:
                        print(f"[spec] Excluding incompatible ICU binary from distribution (missing {len(missing)} symbols): {src}")
                except Exception as exc:
                    print(f"[spec] Warning: Failed to verify ICU binary compatibility ({exc}); excluding: {src}")
        if not is_compatible:
            print(f"[spec] Filtering out candidate ICU DLL: {dest} (source: {src})")
            continue
    filtered_binaries.append(item)
a.binaries = filtered_binaries

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NewManga",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    # Architectural trade-off (F-011): console is kept True during Milestone 3 to capture
    # stdout/stderr diagnostics when running in CLI/smoke mode (--smoke-test, --data-root)
    # on clean machines. Can be toggled to False for final desktop release.
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="NewManga",
)
