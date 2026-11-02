"""Verification tool for Qt6Core.dll and ICU dependency closure (T3.2.1-REPAIR-9).

Statically inspects the PE import directory of Qt6Core.dll, extracts all imported
symbols from icuuc.dll, determines the effective runtime ICU resolution (bundled in
distribution or resolved from Windows System32), and validates that all imported symbols
are present in the effective ICU export table. Exits non-zero if any symbol is missing.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any

import pefile


class ICUSymbolClosureError(Exception):
    """Raised when one or more required ICU symbols cannot be resolved by candidate ICU."""

    def __init__(self, message: str, missing_symbols: list[str] | None = None) -> None:
        super().__init__(message)
        self.missing_symbols = missing_symbols or []


def get_qt_core_icu_imports(qt_core_path: Path) -> list[str]:
    """Parse Qt6Core.dll PE import directory and return all imported symbol names from icuuc.dll."""
    if not qt_core_path.is_file():
        raise FileNotFoundError(f"Qt6Core binary not found: {qt_core_path}")

    try:
        pe = pefile.PE(str(qt_core_path), fast_load=False)
    except pefile.PEFormatError as err:
        raise ValueError(f"Qt6Core is not a valid PE image: {qt_core_path} ({err})") from err

    try:
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_IMPORT"]]
        )
        if not hasattr(pe, "DIRECTORY_ENTRY_IMPORT"):
            raise ValueError(f"No import directory found in PE: {qt_core_path}")

        imported_symbols: list[str] = []
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            dll_name = entry.dll.decode("utf-8", errors="ignore").lower()
            if dll_name == "icuuc.dll":
                for imp in entry.imports:
                    if imp.name:
                        sym_name = imp.name.decode("utf-8", errors="ignore")
                    else:
                        sym_name = f"ordinal_{imp.ordinal}"
                    imported_symbols.append(sym_name)
        return imported_symbols
    finally:
        pe.close()


def get_pe_exports(dll_path: Path) -> set[str]:
    """Parse candidate DLL PE export directory and return set of exported symbol names."""
    if not dll_path.is_file():
        raise FileNotFoundError(f"Candidate DLL not found: {dll_path}")

    try:
        pe = pefile.PE(str(dll_path), fast_load=False)
    except pefile.PEFormatError as err:
        raise ICUSymbolClosureError(
            f"Candidate file is not a valid PE image: {dll_path} ({err})"
        ) from err

    try:
        pe.parse_data_directories(
            directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]]
        )
        if not hasattr(pe, "DIRECTORY_ENTRY_EXPORT") or not pe.DIRECTORY_ENTRY_EXPORT:
            return set()

        exports: set[str] = set()
        for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
            if exp.name:
                exports.add(exp.name.decode("utf-8", errors="ignore"))
        return exports
    finally:
        pe.close()


def find_qt6_core(dist_dir: Path) -> Path | None:
    """Locate Qt6Core.dll inside onedir distribution."""
    candidates = [
        dist_dir / "_internal" / "PySide6" / "Qt6Core.dll",
        dist_dir / "PySide6" / "Qt6Core.dll",
        dist_dir / "_internal" / "Qt6Core.dll",
        dist_dir / "Qt6Core.dll",
    ]
    for c in candidates:
        if c.is_file():
            return c
    # Fallback recursive search
    found = list(dist_dir.rglob("Qt6Core.dll"))
    return found[0] if found else None


def verify_qt_icu_closure(
    dist_dir: Path | None = None,
    qt_core_path: Path | None = None,
    icu_candidate_path: Path | None = None,
) -> dict[str, Any]:
    """Verify Qt6Core.dll ICU import requirements against effective ICU resolution.

    Returns dict of inspection details. Raises ICUSymbolClosureError, FileNotFoundError,
    or ValueError on violation.
    """
    if qt_core_path is None:
        if dist_dir is None:
            raise ValueError("Either dist_dir or qt_core_path must be specified")
        qt_core_path = find_qt6_core(dist_dir)
        if qt_core_path is None:
            raise FileNotFoundError(f"Could not locate Qt6Core.dll within {dist_dir}")

    imported_icu_symbols = get_qt_core_icu_imports(qt_core_path)
    if not imported_icu_symbols:
        return {
            "status": "passed",
            "message": "Qt6Core.dll does not import symbols from icuuc.dll",
            "qt_core_path": str(qt_core_path),
            "effective_icu_path": None,
            "icu_source_type": "none",
            "imported_symbols_count": 0,
            "missing_symbols": [],
        }

    # Determine effective ICU resolution according to Windows DLL search order
    source_type = "unknown"
    if icu_candidate_path is not None:
        effective_icu = icu_candidate_path
        source_type = "explicit_candidate"
    elif dist_dir is not None:
        # Check bundled locations first (application directory takes precedence)
        bundled_candidates = [
            dist_dir / "_internal" / "icuuc.dll",
            dist_dir / "icuuc.dll",
            dist_dir / "_internal" / "PySide6" / "icuuc.dll",
        ]
        bundled_found = next((p for p in bundled_candidates if p.is_file()), None)
        if bundled_found:
            effective_icu = bundled_found
            source_type = "bundled_package"
        else:
            # Fallback to system ICU
            sys_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
            sys_icu = sys_root / "System32" / "icuuc.dll"
            effective_icu = sys_icu
            source_type = "windows_system32"
    else:
        sys_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        effective_icu = sys_root / "System32" / "icuuc.dll"
        source_type = "windows_system32"

    if not effective_icu.is_file():
        raise FileNotFoundError(
            f"Effective ICU dependency not found at: {effective_icu} (source: {source_type})"
        )

    exports = get_pe_exports(effective_icu)
    missing = [sym for sym in imported_icu_symbols if sym not in exports]

    result = {
        "status": "passed" if not missing else "failed",
        "qt_core_path": str(qt_core_path),
        "effective_icu_path": str(effective_icu),
        "icu_source_type": source_type,
        "imported_symbols_count": len(imported_icu_symbols),
        "exported_symbols_count": len(exports),
        "missing_symbols_count": len(missing),
        "missing_symbols": missing,
        "imported_symbols": imported_icu_symbols,
    }

    if missing:
        raise ICUSymbolClosureError(
            f"ICU symbol closure verification FAILED: {len(missing)} of "
            f"{len(imported_icu_symbols)} symbols missing in {effective_icu} "
            f"({source_type}). Missing: {missing}",
            missing_symbols=missing,
        )

    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Qt6Core.dll ICU symbol closure against effective runtime DLL"
    )
    parser.add_argument(
        "--dist-dir",
        type=Path,
        default=None,
        help="Path to built onedir distribution root (e.g. output/NewManga)",
    )
    parser.add_argument(
        "--qt-core",
        type=Path,
        default=None,
        help="Direct path to Qt6Core.dll",
    )
    parser.add_argument(
        "--icu-candidate",
        type=Path,
        default=None,
        help="Direct path to candidate icuuc.dll to inspect",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON result",
    )

    args = parser.parse_args()

    try:
        res = verify_qt_icu_closure(
            dist_dir=args.dist_dir,
            qt_core_path=args.qt_core,
            icu_candidate_path=args.icu_candidate,
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print("=== Qt6Core ICU Symbol Closure Verification: PASSED ===")
            print(f"Qt6Core Path:         {res['qt_core_path']}")
            print(f"Effective ICU Path:   {res['effective_icu_path']} ({res['icu_source_type']})")
            print(f"Imported ICU Symbols: {res['imported_symbols_count']}")
            print(f"Candidate Exports:    {res['exported_symbols_count']}")
            print("All required symbols resolved successfully.")
        return 0
    except (ICUSymbolClosureError, FileNotFoundError, ValueError, pefile.PEFormatError) as err:
        if args.json:
            out = {
                "status": "failed",
                "error": str(err),
                "missing_symbols": getattr(err, "missing_symbols", []),
            }
            print(json.dumps(out, indent=2))
        else:
            print(f"ERROR: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
