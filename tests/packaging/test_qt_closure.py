"""Contract and discrimination tests for Qt6Core.dll ICU dependency closure verification (T3.2.1-REPAIR-9)."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER_PATH = ROOT / "packaging" / "check_qt_closure.py"

# Safely load packaging/check_qt_closure.py avoiding collision with site-packages 'packaging'
spec = importlib.util.spec_from_file_location("check_qt_closure_module", str(CHECKER_PATH))
assert spec is not None and spec.loader is not None
checker = importlib.util.module_from_spec(spec)
sys.modules["check_qt_closure_module"] = checker
spec.loader.exec_module(checker)

ICUSymbolClosureError = checker.ICUSymbolClosureError
get_pe_exports = checker.get_pe_exports
get_qt_core_icu_imports = checker.get_qt_core_icu_imports
verify_qt_icu_closure = checker.verify_qt_icu_closure


def find_system_qt6_core() -> Path:
    """Find Qt6Core.dll in the current python environment."""
    import PySide6

    pyside_dir = Path(PySide6.__file__).parent
    qt_core = pyside_dir / "Qt6Core.dll"
    if not qt_core.is_file():
        pytest.skip(f"Qt6Core.dll not found in PySide6 directory: {pyside_dir}")
    return qt_core


def test_qt6_core_imports_icu_symbols():
    """Verify Qt6Core imports icuuc.dll symbols dynamically."""
    qt_core = find_system_qt6_core()
    imports = get_qt_core_icu_imports(qt_core)
    assert len(imports) > 0, "Qt6Core.dll should import ICU symbols"
    # Verify core well-known ICU symbols are present
    assert "ucnv_open" in imports
    assert "ucnv_close" in imports
    assert "ucnv_reset" in imports


def test_positive_verification_with_system_icu():
    """Verify that current system ICU satisfies Qt6Core import requirements."""
    qt_core = find_system_qt6_core()
    result = verify_qt_icu_closure(qt_core_path=qt_core)
    assert result["status"] == "passed"
    assert result["missing_symbols_count"] == 0
    assert len(result["missing_symbols"]) == 0
    assert result["icu_source_type"] == "windows_system32"


def test_negative_discrimination_missing_symbols(monkeypatch):
    """Negative test: verify that missing even one ICU symbol triggers ICUSymbolClosureError."""
    qt_core = find_system_qt6_core()
    imports = get_qt_core_icu_imports(qt_core)
    assert len(imports) >= 2

    # Simulate an ICU export set missing 'ucnv_open'
    incomplete_exports = set(imports) - {"ucnv_open"}

    monkeypatch.setattr(checker, "get_pe_exports", lambda p: incomplete_exports)

    with pytest.raises(ICUSymbolClosureError) as exc_info:
        verify_qt_icu_closure(qt_core_path=qt_core)

    err = exc_info.value
    assert "ucnv_open" in err.missing_symbols
    assert "FAILED" in str(err)


def test_negative_discrimination_empty_exports(monkeypatch):
    """Negative test: verify that candidate ICU exporting no matching symbols triggers failure."""
    qt_core = find_system_qt6_core()

    # Simulate a third-party renamed ICU (like Poppler's _78 renamed symbols)
    monkeypatch.setattr(
        checker, "get_pe_exports", lambda p: {"ucnv_open_78", "ucnv_close_78"}
    )

    with pytest.raises(ICUSymbolClosureError) as exc_info:
        verify_qt_icu_closure(qt_core_path=qt_core)

    err = exc_info.value
    assert len(err.missing_symbols) == len(get_qt_core_icu_imports(qt_core))
    assert "ucnv_open" in err.missing_symbols


def test_negative_discrimination_cli_subprocess(tmp_path):
    """Negative test via CLI: packaging/check_qt_closure.py must exit non-zero when candidate is invalid."""
    qt_core = find_system_qt6_core()

    # Find a valid PE file in Python's DLLs that does NOT export ICU symbols (e.g. _asyncio.pyd or unicodedata.pyd)
    py_dir = Path(sys.executable).parent
    pe_candidates = list(py_dir.glob("DLLs/*.pyd")) + list(py_dir.glob("*.dll"))
    if not pe_candidates:
        # Fallback to invalid file
        invalid_candidate = tmp_path / "fake_icu.dll"
        invalid_candidate.write_bytes(b"INVALID_PE_HEADER")
    else:
        invalid_candidate = pe_candidates[0]

    cmd = [
        sys.executable,
        str(CHECKER_PATH),
        "--qt-core",
        str(qt_core),
        "--icu-candidate",
        str(invalid_candidate),
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode != 0, f"Expected non-zero exit code for invalid ICU, got {res.returncode}"
    assert "FAILED" in res.stderr or "ERROR" in res.stderr
