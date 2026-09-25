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
# M2-I2: application layer must not import infrastructure or UI presentation
APPLICATION_FORBIDDEN = frozenset({"infrastructure", "ui"})
QT_FORBIDDEN = frozenset({"PySide6"})
M2_I2_QT_FREE_MODULES = (
    APPLICATION_ROOT / "tasks" / "projection.py",
    APPLICATION_ROOT / "editing" / "region_canvas.py",
)
LEGACY_UI_SHIM_SEAMS = {
    UI_ROOT / "models" / "tasks" / "projection.py": "application.tasks.projection",
    UI_ROOT / "viewmodels" / "workbench" / "region_canvas.py": "application.editing.region_canvas",
}
LEGACY_UI_SHIMS = tuple(LEGACY_UI_SHIM_SEAMS.keys())

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
    """Report static *and* literal dynamic imports of a forbidden root or module path.

    Static: ``import x.y`` / ``from x import y`` (including relative forms).
    Dynamic: ``importlib.import_module("x.y")`` / ``__import__("x.y")`` with a
    literal name — the gap the TASK-019 line-prefix guard left open
    (TASK-034 AC ②).
    """
    violations: list[str] = []
    paths = [root] if root.is_file() else sorted(root.rglob("*.py"))
    for path in paths:
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
                if dynamic is not None:
                    dyn_clean = dynamic.lstrip(".")
                    for fb in forbidden_roots:
                        if (
                            dyn_clean == fb
                            or dyn_clean.startswith(fb + ".")
                            or ("." not in fb and dyn_clean.split(".", 1)[0] == fb)
                        ):
                            violations.append(
                                f"{path}:{node.lineno}: forbidden dynamic import {dynamic}"
                            )
                            break
                continue
            else:
                continue

            for module in modules:
                mod_clean = module.lstrip(".")
                for fb in forbidden_roots:
                    if (
                        mod_clean == fb
                        or mod_clean.startswith(fb + ".")
                        or ("." not in fb and mod_clean.split(".", 1)[0] == fb)
                    ):
                        violations.append(
                            f"{path}:{node.lineno}: forbidden import {module}"
                        )
                        break
    return sorted(violations)


def find_shim_violations(path: Path, allowed_seam: str | None = None) -> list[str]:
    """Report any local definition, non-application import, or logic in a pure re-export shim.

    Legacy UI modules must only act as non-authoritative shims delegating to their
    respective application seam and re-exporting symbols via __all__.
    """
    if allowed_seam is None:
        allowed_seam = LEGACY_UI_SHIM_SEAMS.get(path)

    violations: list[str] = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            violations.append(
                f"{path}:{node.lineno}: forbidden local definition in legacy shim: {node.name}"
            )
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod == "__future__":
                continue
            if allowed_seam is not None and (mod != allowed_seam or node.level != 0):
                violations.append(
                    f"{path}:{node.lineno}: forbidden import in legacy shim: {mod} (only {allowed_seam} allowed)"
                )
            elif allowed_seam is None and (mod.startswith("ui") or mod.startswith(".ui")):
                violations.append(
                    f"{path}:{node.lineno}: forbidden import in legacy shim: {mod}"
                )
        elif isinstance(node, ast.Import):
            for alias in node.names:
                violations.append(
                    f"{path}:{node.lineno}: forbidden import in legacy shim: {alias.name}"
                )
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            # docstring or string constant
            continue
        elif isinstance(node, ast.Assign):
            # allow __all__ assignment
            targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if targets == ["__all__"]:
                continue
            violations.append(
                f"{path}:{node.lineno}: forbidden assignment in legacy shim: {','.join(targets)}"
            )
        else:
            violations.append(
                f"{path}:{node.lineno}: forbidden statement in legacy shim: {type(node).__name__}"
            )
    return violations


def find_shim_local_definitions(path: Path, allowed_seam: str | None = None) -> list[str]:
    """Backward-compatible alias for find_shim_violations."""
    return find_shim_violations(path, allowed_seam=allowed_seam)



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


def test_application_layer_does_not_import_infrastructure_or_ui() -> None:
    """Standards S-1 (TASK-019) + T-4 (TASK-034) + M2-I2: layer direction holds.

    ``doc/02_TECHNICAL_ARCHITECTURE_.md`` §架构方向 requires
    ``QML/UI → Application → Domain/Ports → Infrastructure Adapters``. The
    application layer must not import infrastructure nor UI presentation modules.
    This guard prevents architecture inversion and keeps logic from flowing back to UI.
    """
    violations = find_forbidden_imports(APPLICATION_ROOT, APPLICATION_FORBIDDEN)
    assert not violations, "application layer must not import infrastructure or ui:\n" + "\n".join(
        violations
    )


def test_migrated_application_modules_are_qt_free() -> None:
    """M2-I2 AC3/AC4: migrated application modules must be completely Qt-free."""
    violations: list[str] = []
    for module_path in M2_I2_QT_FREE_MODULES:
        assert module_path.is_file(), f"missing migrated module: {module_path}"
        violations.extend(find_forbidden_imports(module_path, QT_FORBIDDEN))
    assert not violations, "migrated application modules must not import Qt:\n" + "\n".join(
        violations
    )


def test_workbench_ui_consumers_import_from_application_seams() -> None:
    """M2-I2 AC2/AC4: legacy UI consumers must consume projection and region canvas via application seams.

    Prevents reversal of authoritative logic into UI by asserting that consumer
    modules do not import from the non-authoritative legacy shims.
    """
    page_list_model = UI_ROOT / "models" / "tasks" / "page_list_model.py"
    workbench_vm = UI_ROOT / "viewmodels" / "workbench" / "viewmodel.py"
    legacy_shims = frozenset({
        "ui.models.tasks.projection",
        "ui.viewmodels.workbench.region_canvas",
    })
    for path in (page_list_model, workbench_vm):
        assert path.is_file(), f"missing consumer file: {path}"
        violations = find_forbidden_imports(path, legacy_shims)
        assert not violations, (
            f"{path} must not import from legacy UI logic modules:\n" + "\n".join(violations)
        )


def test_legacy_ui_shims_contain_no_authoritative_logic() -> None:
    """M2-I2 AC2/AC4: legacy UI shims must remain pure re-export shims from application seams.

    Prevents revived or reversed business logic in UI shims by asserting that no local
    function/class definitions or assignments exist, and imports strictly originate only
    from each shim's corresponding application seam.
    """
    violations: list[str] = []
    for shim_path, allowed_seam in LEGACY_UI_SHIM_SEAMS.items():
        assert shim_path.is_file(), f"missing legacy shim: {shim_path}"
        violations.extend(find_shim_violations(shim_path, allowed_seam=allowed_seam))
    assert not violations, (
        "legacy UI shims must not contain authoritative business logic or non-application imports:\n"
        + "\n".join(violations)
    )



def test_application_ui_violation_reports_file_line_and_module(tmp_path: Path) -> None:
    """M2-I2 AC4 discriminative probe: application importing ui must be caught."""
    source = tmp_path / "bad_app.py"
    source.write_text(
        "from ui.models.tasks.projection import TaskProjection\n",
        encoding="utf-8",
    )
    assert find_forbidden_imports(tmp_path, APPLICATION_FORBIDDEN) == [
        f"{source}:1: forbidden import ui.models.tasks.projection"
    ]


def test_qt_free_application_violation_reports_pyside6(tmp_path: Path) -> None:
    """M2-I2 AC4 discriminative probe: PySide6 import in qt-free module must be caught."""
    source = tmp_path / "bad_qt_free.py"
    source.write_text(
        "from PySide6.QtCore import QObject\n",
        encoding="utf-8",
    )
    assert find_forbidden_imports(tmp_path, QT_FORBIDDEN) == [
        f"{source}:1: forbidden import PySide6.QtCore"
    ]


def test_reversal_guard_reports_legacy_ui_import(tmp_path: Path) -> None:
    """M2-I2 AC4 discriminative probe: legacy shim imports must be reported."""
    source = tmp_path / "bad_consumer.py"
    source.write_text(
        "from ui.models.tasks.projection import build_projection\n"
        "from ui.viewmodels.workbench.region_canvas import normalized_to_page_geometry\n",
        encoding="utf-8",
    )
    forbidden = frozenset({
        "ui.models.tasks.projection",
        "ui.viewmodels.workbench.region_canvas",
    })
    assert find_forbidden_imports(tmp_path, forbidden) == [
        f"{source}:1: forbidden import ui.models.tasks.projection",
        f"{source}:2: forbidden import ui.viewmodels.workbench.region_canvas",
    ]


def test_reversal_guard_reports_local_definitions_in_legacy_shims(tmp_path: Path) -> None:
    """M2-I2 AC4 discriminative probe: function or class defined in shim must be caught."""
    source = tmp_path / "mutant_shim.py"
    source.write_text(
        '"""Legacy shim."""\n'
        "from application.tasks.projection import TaskProjection\n"
        "def revived_business_rule():\n"
        "    return 42\n"
        "class RevivedModel:\n"
        "    pass\n",
        encoding="utf-8",
    )
    violations = find_shim_violations(source, allowed_seam="application.tasks.projection")
    assert violations == [
        f"{source}:3: forbidden local definition in legacy shim: revived_business_rule",
        f"{source}:5: forbidden local definition in legacy shim: RevivedModel",
    ]


def test_reversal_guard_reports_ui_imports_in_legacy_shims(tmp_path: Path) -> None:
    """M2-I2 AC4 discriminative probe: import from ui.* in legacy shim must be caught."""
    source = tmp_path / "mutant_ui_shim.py"
    source.write_text(
        '"""Legacy shim with forbidden ui import."""\n'
        "from ui.models.tasks.page_list_model import PageListModel\n"
        "import ui.viewmodels.workbench.viewmodel\n",
        encoding="utf-8",
    )
    violations = find_shim_violations(source, allowed_seam="application.tasks.projection")
    assert violations == [
        f"{source}:2: forbidden import in legacy shim: ui.models.tasks.page_list_model (only application.tasks.projection allowed)",
        f"{source}:3: forbidden import in legacy shim: ui.viewmodels.workbench.viewmodel",
    ]



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
