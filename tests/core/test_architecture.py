from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = REPO_ROOT / "src" / "domain"
UI_ROOT = REPO_ROOT / "src" / "ui"

DOMAIN_FORBIDDEN = frozenset(
    {"PySide6", "sqlite3", "torch", "transformers", "onnxruntime"}
)
UI_FORBIDDEN = frozenset({"infrastructure"})


def find_forbidden_imports(
    root: Path, forbidden_roots: frozenset[str]
) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                prefix = "." * node.level
                modules = (
                    [f"{prefix}{node.module}"]
                    if node.module
                    else [f"{prefix}{alias.name}" for alias in node.names]
                )
            else:
                continue

            for module in modules:
                if module.lstrip(".").split(".", 1)[0] in forbidden_roots:
                    violations.append(
                        f"{path}:{node.lineno}: forbidden import {module}"
                    )
    return sorted(violations)


def test_source_packages_exist_and_respect_boundaries() -> None:
    assert DOMAIN_ROOT.is_dir(), f"missing package boundary: {DOMAIN_ROOT}"
    assert UI_ROOT.is_dir(), f"missing package boundary: {UI_ROOT}"
    violations = find_forbidden_imports(DOMAIN_ROOT, DOMAIN_FORBIDDEN)
    violations += find_forbidden_imports(UI_ROOT, UI_FORBIDDEN)
    assert not violations, "\n".join(violations)


def test_domain_violation_reports_file_line_and_module(tmp_path: Path) -> None:
    source = tmp_path / "bad_domain.py"
    source.write_text("\nfrom PySide6.QtCore import QObject\n", encoding="utf-8")
    assert find_forbidden_imports(tmp_path, DOMAIN_FORBIDDEN) == [
        f"{source}:2: forbidden import PySide6.QtCore"
    ]


def test_ui_violation_reports_file_line_and_module(tmp_path: Path) -> None:
    source = tmp_path / "bad_ui.py"
    source.write_text("import infrastructure.sqlite_repository\n", encoding="utf-8")
    assert find_forbidden_imports(tmp_path, UI_FORBIDDEN) == [
        f"{source}:1: forbidden import infrastructure.sqlite_repository"
    ]


def test_relative_from_import_reports_forbidden_alias(tmp_path: Path) -> None:
    source = tmp_path / "relative_ui.py"
    source.write_text(
        "from . import infrastructure\nfrom .. import infrastructure\n",
        encoding="utf-8",
    )
    assert find_forbidden_imports(tmp_path, UI_FORBIDDEN) == [
        f"{source}:1: forbidden import .infrastructure",
        f"{source}:2: forbidden import ..infrastructure",
    ]
