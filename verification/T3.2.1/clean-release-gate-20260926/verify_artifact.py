"""Verify the frozen package manifest, QML closure, exclusions, and optional deps."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_manifest(path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            digest, relative = line.split("  ", 1)
        except ValueError as exc:
            raise ValueError(f"Malformed manifest line {line_no}") from exc
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"Invalid SHA-256 on manifest line {line_no}")
        if relative in entries:
            raise ValueError(f"Duplicate manifest path: {relative}")
        entries[relative] = digest
    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-head", required=True)
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--qml-source", type=Path, required=True)
    args = parser.parse_args()

    package = args.package.resolve()
    entries = parse_manifest(args.manifest)
    actual_files = {
        path.relative_to(package).as_posix(): path
        for path in package.rglob("*")
        if path.is_file()
    }
    unlisted = sorted(set(actual_files) - set(entries))
    missing = sorted(set(entries) - set(actual_files))
    hash_mismatches = [
        relative
        for relative, path in actual_files.items()
        if relative in entries and sha256(path) != entries[relative]
    ]

    required_files = [
        "NewManga.exe",
        "_internal/PySide6/Qt6Core.dll",
        "_internal/PySide6/Qt6Gui.dll",
        "_internal/PySide6/Qt6Qml.dll",
        "_internal/PySide6/Qt6Quick.dll",
        "_internal/PySide6/Qt6QuickControls2.dll",
        "_internal/PySide6/plugins/platforms/qwindows.dll",
    ]
    absent_required = [relative for relative in required_files if relative not in entries]

    qml_files = sorted(path for path in args.qml_source.rglob("*") if path.is_file())
    qml_mismatches: list[str] = []
    for source in qml_files:
        relative = source.relative_to(args.qml_source).as_posix()
        package_relative = f"_internal/ui/qml/{relative}"
        if package_relative not in entries:
            qml_mismatches.append(f"missing:{package_relative}")
        elif sha256(source) != entries[package_relative]:
            qml_mismatches.append(f"hash:{package_relative}")

    route_files = [
        "bookshelf/BookshelfView.qml",
        "workbench/WorkbenchView.qml",
        "reader/ReaderView.qml",
        "settings/SettingsView.qml",
    ]
    for relative in route_files:
        packaged = f"_internal/ui/qml/{relative}"
        if packaged not in entries:
            qml_mismatches.append(f"route:{packaged}")

    qml_imports = sorted(
        {
            match.group(1)
            for source in qml_files
            if source.suffix == ".qml"
            for match in re.finditer(
                r"^\s*import\s+(Qt[A-Za-z0-9_.]+)",
                source.read_text(encoding="utf-8"),
                flags=re.MULTILINE,
            )
        }
    )
    missing_qmldirs = [
        module
        for module in qml_imports
        if f"_internal/PySide6/qml/{module.replace('.', '/')}/qmldir" not in entries
    ]

    forbidden_segments = {
        "tests",
        ".git",
        ".pytest_cache",
        "__pycache__",
        "src",
        ".venv",
        "venv",
        "managed",
    }
    forbidden_paths = [
        relative
        for relative in entries
        if any(part.lower() in forbidden_segments for part in Path(relative).parts)
        or relative.lower().endswith((".sqlite", ".sqlite3", ".db"))
    ]
    optional_dependency_names = (
        "torch",
        "torchvision",
        "doctr",
        "cv2",
        "scipy",
        "onnx",
        "shapely",
    )
    optional_dependency_paths = [
        relative
        for relative in entries
        if any(
            re.search(rf"(^|/){re.escape(name)}(/|\.|$)", relative, flags=re.IGNORECASE)
            for name in optional_dependency_names
        )
    ]

    report = {
        "source_head": args.source_head,
        "package": str(package),
        "manifest": str(args.manifest.resolve()),
        "manifest_entries": len(entries),
        "package_file_count": len(actual_files),
        "package_total_bytes": sum(path.stat().st_size for path in actual_files.values()),
        "exe_sha256": sha256(package / "NewManga.exe"),
        "required_runtime_files": required_files,
        "qml_source_file_count": len(qml_files),
        "qml_imports": qml_imports,
        "qt_qmldirs_missing": missing_qmldirs,
        "package_excluded_tests_cache_source_user_data": forbidden_paths,
        "optional_heavy_dependencies_absent": not optional_dependency_paths,
        "optional_heavy_dependency_paths": optional_dependency_paths,
        "checks": {
            "manifest_matches_package_file_set": not unlisted and not missing,
            "manifest_hashes_match_package": not hash_mismatches,
            "required_qt_runtime_files_present": not absent_required,
            "all_production_qml_and_qmldir_files_match_source": not qml_mismatches,
            "all_imported_qt_qmldirs_present": not missing_qmldirs,
            "tests_cache_source_and_user_data_excluded": not forbidden_paths,
            "optional_model_dependencies_excluded": not optional_dependency_paths,
        },
        "details": {
            "unlisted_package_files": unlisted,
            "missing_manifest_files": missing,
            "manifest_hash_mismatches": hash_mismatches,
            "required_files_missing": absent_required,
            "qml_mismatches": qml_mismatches,
        },
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if all(report["checks"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
