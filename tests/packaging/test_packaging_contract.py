"""Contract tests for Windows packaging engineering (T3.2.1 Task 1)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_spec_owns_real_entry_and_qml_tree():
    spec_path = ROOT / "packaging" / "new_manga.spec"
    assert spec_path.is_file(), f"Spec file missing: {spec_path}"
    spec = spec_path.read_text(encoding="utf-8")
    assert "src/bootstrap/app.py" in spec
    assert "src/ui/qml" in spec
    # Ensure test directories are not packaged into datas or pathex (R-009)
    assert '("tests"' not in spec
    assert '("tests/' not in spec
    assert "src/tests" not in spec
    assert ".pytest_cache" not in spec
    assert '"tests"' in spec  # explicitly in excludes list


def test_build_script_requires_explicit_output_directory():
    script_path = ROOT / "packaging" / "build.ps1"
    assert script_path.is_file(), f"Build script missing: {script_path}"
    script = script_path.read_text(encoding="utf-8")
    assert "OutputDir" in script
    assert "manifest" in script.lower()
    assert "pyinstaller" in script.lower()
    # Contract requirements for T3.2.1-REPAIR-9
    assert "Sanitized build PATH" in script
    assert "check_qt_closure.py" in script
    assert "PYINSTALLER_CONFIG_DIR" in script
    assert "status --porcelain=v1" in script
    assert "Refusing to reuse an existing output/work/config directory" in script
    assert "New Manga.task-envs" not in script
    assert "Remove-Item -Recurse" not in script


def test_spec_filters_incompatible_icu_binaries():
    """Verify new_manga.spec contains binary filtering against incompatible ICU libraries (T3.2.1-REPAIR-9)."""
    spec_path = ROOT / "packaging" / "new_manga.spec"
    assert spec_path.is_file(), f"Spec file missing: {spec_path}"
    spec = spec_path.read_text(encoding="utf-8")
    assert "check_qt_closure.py" in spec
    assert "icuuc.dll" in spec
    assert "filtered_binaries" in spec


def test_manifest_generator_exists_and_hashes_reproducibly(tmp_path):
    manifest_py = ROOT / "packaging" / "manifest.py"
    assert manifest_py.is_file(), f"Manifest script missing: {manifest_py}"

    # Verify manifest generation contract on a dummy tree
    dummy_dir = tmp_path / "dummy_dist"
    dummy_dir.mkdir()
    (dummy_dir / "b.txt").write_text("content-b", encoding="utf-8")
    (dummy_dir / "a.txt").write_text("content-a", encoding="utf-8")
    sub = dummy_dir / "subdir"
    sub.mkdir()
    (sub / "c.txt").write_text("content-c", encoding="utf-8")

    import subprocess
    import sys

    manifest_out = tmp_path / "manifest.sha256"
    cmd = [
        sys.executable,
        str(manifest_py),
        "--root",
        str(dummy_dir),
        "--output",
        str(manifest_out),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"manifest.py failed: {res.stderr}"
    lines = manifest_out.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3
    # Check ordering: stable sorted relative paths (forward slashes)
    rel_paths = [line.split("  ", 1)[1] for line in lines]
    assert rel_paths == ["a.txt", "b.txt", "subdir/c.txt"]
