from __future__ import annotations

import ast
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DOMAIN_ROOT = REPO_ROOT / "src" / "domain"
UI_ROOT = REPO_ROOT / "src" / "ui"
APPLICATION_ROOT = REPO_ROOT / "src" / "application"

DOMAIN_FORBIDDEN = frozenset(
    {"PySide6", "sqlite3", "torch", "transformers", "onnxruntime"}
)
UI_FORBIDDEN = frozenset({"infrastructure"})
APPLICATION_FORBIDDEN = frozenset({"infrastructure"})

#: Calls that import a module from a literal name at runtime (TASK-034 AC ②:
#: the old line-prefix guard could not see these).
_DYNAMIC_IMPORT_CALLS = frozenset({"import_module", "__import__"})


def _dynamic_import_target(node: ast.Call) -> str | None:
    """Return the literal module name of ``import_module``/``__import__``."""
    func = node.func
    name = getattr(func, "attr", None) or getattr(func, "id", None)
    if name not in _DYNAMIC_IMPORT_CALLS or not node.args:
        return None
    argument = node.args[0]
    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
        return argument.value
    return None


def find_forbidden_imports(
    root: Path, forbidden_roots: frozenset[str]
) -> list[str]:
    """Report static *and* literal dynamic imports of a forbidden root.

    Static: ``import x.y`` / ``from x import y`` (including relative forms).
    Dynamic: ``importlib.import_module("x.y")`` / ``__import__("x.y")`` with a
    literal name — the gap the TASK-019 line-prefix guard left open
    (TASK-034 AC ②).
    """
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
            elif isinstance(node, ast.Call):
                dynamic = _dynamic_import_target(node)
                if dynamic is not None and dynamic.split(".", 1)[0] in forbidden_roots:
                    violations.append(
                        f"{path}:{node.lineno}: forbidden dynamic import {dynamic}"
                    )
                continue
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


# ---------------------------------------------------------------------------
# TASK-034 AC ②: the application → infrastructure guard lives here now, uses
# the AST implementation above, and also sees literal dynamic imports (the old
# line-prefix scan in tests/providers could not).
# ---------------------------------------------------------------------------


def test_application_layer_does_not_import_infrastructure() -> None:
    """Standards S-1 (TASK-019) + T-4 (TASK-034): the layer direction holds.

    ``doc/02_TECHNICAL_ARCHITECTURE_.md`` §架构方向 requires
    ``QML/UI → Application → Domain/Ports → Infrastructure Adapters``. The
    Inpaint Step once imported the route policy, route table and non-target
    protection rule from ``infrastructure.providers``; those live in the
    application layer now, and this guard keeps the inversion from coming back
    — including via ``importlib.import_module("infrastructure…")``.
    """
    violations = find_forbidden_imports(APPLICATION_ROOT, APPLICATION_FORBIDDEN)
    assert not violations, "application layer must not import infrastructure:\n" + "\n".join(
        violations
    )


def test_dynamic_import_of_a_forbidden_root_is_detected(tmp_path: Path) -> None:
    """AC ② discriminative unit: a literal dynamic import must be reported.

    The previous guard scanned lines for the prefixes ``from infrastructure`` /
    ``import infrastructure``, so both statements below slipped through.
    """
    source = tmp_path / "dynamic_ui.py"
    source.write_text(
        "import importlib\n"
        'importlib.import_module("infrastructure.providers.registry")\n'
        'module = __import__("infrastructure.sqlite.pipeline")\n'
        'importlib.import_module("application.tasks.service")\n',
        encoding="utf-8",
    )
    assert find_forbidden_imports(tmp_path, UI_FORBIDDEN) == [
        f"{source}:2: forbidden dynamic import infrastructure.providers.registry",
        f"{source}:3: forbidden dynamic import infrastructure.sqlite.pipeline",
    ]


def test_non_literal_dynamic_import_is_not_a_false_positive(tmp_path: Path) -> None:
    """A computed module name cannot be judged statically — stay silent."""
    source = tmp_path / "computed_ui.py"
    source.write_text(
        "import importlib\n"
        'name = "infrastructure.providers.registry"\n'
        "importlib.import_module(name)\n",
        encoding="utf-8",
    )
    assert find_forbidden_imports(tmp_path, UI_FORBIDDEN) == []
