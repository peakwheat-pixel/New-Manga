"""M2-I1 Core Assembly Seam tests.

判别探针（I1-AC1/AC6）：在子进程里用 ``sys.meta_path`` blocker 拒绝
``PySide6``/``shiboken6``/``ui``，``bootstrap.core_assembly`` 必须可按
模块名导入且不拉起任何 Qt 模块；同一 blocker 下 Legacy 装配根
``bootstrap.app`` 必须失败——这个对照证明 blocker 有效，Core Assembly
的通过是 seam 真实存在，而不是探针失效。

装配 seam（I1-AC4）：Qt 适配器只经 keyword-only 参数注入 Core；本模块
用 AST 静态判别 + 运行期 identity 断言两种方式验证 Core 从不构造
``QtImageDecoder``/``QtFontCatalog``/``QtTextLayoutEngine``/
``QtImageCompositor`` 或 QObject viewmodel。

层守卫（I1-AC2）：``src/domain``、``src/ports``、``src/application``
的模块导入期不得出现 PySide6（函数体内的惰性导入是 M2-D1 M2D1-04
已记录的 DECOUPLE 形态，不在此守卫范围）。
"""

from __future__ import annotations

import ast
import inspect
import os
from pathlib import Path
import subprocess
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

pytest.importorskip("PySide6")

DOMAIN_ROOT = SRC_ROOT / "domain"
PORTS_ROOT = SRC_ROOT / "ports"
APPLICATION_ROOT = SRC_ROOT / "application"
CORE_ASSEMBLY_PATH = SRC_ROOT / "bootstrap" / "core_assembly.py"

_QT_ROOTS = frozenset({"PySide6", "shiboken6"})
_UI_ROOTS = frozenset({"ui"})
#: AC4 names the Core assembly must never construct (or import).
_QT_ADAPTER_CLASSES = frozenset(
    {
        "QtImageDecoder",
        "QtFontCatalog",
        "QtTextLayoutEngine",
        "QtImageCompositor",
        "PixelSourceStyleAnalyzer",
    }
)
_QOBJECT_VIEWMODEL_CLASSES = frozenset(
    {
        "NavigationViewModel",
        "BookshelfViewModel",
        "WorkbenchViewModel",
        "ReaderViewModel",
        "SettingsViewModel",
        "ExportViewModel",
    }
)

#: Subprocess probe: install a meta-path blocker first, then run the
#: caller's statements. Importing anything under the blocked roots raises
#: ImportError("BLOCKED-IMPORT: <module>"), so a pass/fail flip between
#: two modules proves the probe discriminates.
_BLOCKER_PREAMBLE = """\
import sys

_BLOCKED = {"PySide6", "shiboken6", "ui"}

class _ImportBlocker:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".", 1)[0] in _BLOCKED:
            raise ImportError(f"BLOCKED-IMPORT: {fullname}")
        return None

sys.meta_path.insert(0, _ImportBlocker())
"""


def _run_blocker_probe(statements: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC_ROOT)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-c", _BLOCKER_PREAMBLE + statements],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env=env,
    )


# ---------------------------------------------------------------------------
# I1-AC1 / I1-AC6 — discriminating import probes (no Qt, no src/ui)
# ---------------------------------------------------------------------------


def test_core_assembly_imports_when_qt_and_ui_are_blocked() -> None:
    result = _run_blocker_probe(
        "import bootstrap.core_assembly\n"
        "leaked = [m for m in sys.modules"
        " if m.split('.', 1)[0] in {'PySide6', 'shiboken6', 'ui'}]\n"
        "assert not leaked, f'Qt/UI leaked into sys.modules: {leaked}'\n"
        "print('CORE-ASSEMBLY-IMPORT-OK')\n"
    )
    assert result.returncode == 0, (
        f"core assembly must import without PySide6/src/ui;\n"
        f"stdout={result.stdout}\nstderr={result.stderr}"
    )
    assert "CORE-ASSEMBLY-IMPORT-OK" in result.stdout


def test_legacy_app_import_fails_under_the_same_blocker() -> None:
    # 对照（I1-AC6）：同一 blocker 下 Legacy Qt 装配根必须被拦截。
    # 它失败而 core assembly 通过，证明 blocker 有判别力，前一个测试
    # 的通过不是探针失效。
    result = _run_blocker_probe("import bootstrap.app\n")
    assert result.returncode != 0, (
        "the blocker probe is broken: bootstrap.app imported despite the"
        " PySide6 block"
    )
    assert "BLOCKED-IMPORT: PySide6" in result.stderr


# ---------------------------------------------------------------------------
# I1-AC4 — adapter injection seam
# ---------------------------------------------------------------------------


def test_core_assembly_exposes_keyword_only_adapter_injection() -> None:
    import bootstrap.core_assembly as core_assembly

    signature = inspect.signature(core_assembly.assemble_core_services)
    required = {
        "image_decoder",
        "font_catalog",
        "layout_engine",
        "compositor",
        "source_styles",
    }
    for name in required | {"content_decoder"}:
        assert name in signature.parameters, f"missing injection seam: {name}"
        assert (
            signature.parameters[name].kind is inspect.Parameter.KEYWORD_ONLY
        ), f"{name} must be keyword-only so the seam is explicit"
    for name in required:
        assert signature.parameters[name].default is inspect.Parameter.empty, (
            f"{name} must be required: the Core cannot fall back to"
            f" constructing a Qt implementation"
        )
    assert signature.parameters["content_decoder"].default is None


def test_core_assembly_module_scope_has_no_qt_or_ui_imports() -> None:
    # 模块导入期（顶层与类体；函数体内的惰性导入是 M2-D1 记录的
    # DECOUPLE 形态）不得出现 PySide6/shiboken6/ui。
    violations = _module_scope_imports(ast.parse(_core_source()))
    offenders = [
        f"line {lineno}: {module}"
        for lineno, module in violations
        if module.lstrip(".").split(".", 1)[0] in (_QT_ROOTS | _UI_ROOTS)
    ]
    assert not offenders, "\n".join(offenders)


def test_core_assembly_never_imports_or_constructs_qt_adapters() -> None:
    # ``src/ui`` must never be imported in any form (module scope or lazy):
    # the Core assembly has no UI responsibility at all. The named Qt
    # adapter/viewmodel classes must never be constructed anywhere. Lazy
    # ``from PySide6... import`` inside the pixel helpers is the M2-D1
    # (M2D1-15) catalogued DECOUPLE form — module-scope PySide6 is the one
    # prohibited by the previous test.
    tree = ast.parse(_core_source())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".", 1)[0] not in _UI_ROOTS, (
                    f"line {node.lineno}: import {alias.name}"
                )
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".", 1)[0]
            assert root not in _UI_ROOTS, (
                f"line {node.lineno}: from {node.module} import ..."
            )
        elif isinstance(node, ast.Call):
            func = node.func
            name = (
                func.id
                if isinstance(func, ast.Name)
                else func.attr if isinstance(func, ast.Attribute) else None
            )
            assert name not in (_QT_ADAPTER_CLASSES | _QOBJECT_VIEWMODEL_CLASSES), (
                f"line {node.lineno}: the Core assembly constructs {name}"
            )


def test_core_assembly_uses_injected_adapters_verbatim(tmp_path: Path) -> None:
    # 运行期判别：identity 断言证明注入对象被原样使用——若 Core 忽略
    # 注入、自行构造 Qt 实现，这里立即失败。
    from application.translation.color.service import SourceStyleService
    from bootstrap.core_assembly import assemble_core_services
    from infrastructure.rendering.pixel_source_style import (
        PixelSourceStyleAnalyzer,
    )

    decoder = _PassthroughDecoder()
    marker_font_catalog = object()
    marker_layout = object()
    marker_compositor = object()
    core = assemble_core_services(
        tmp_path / "library.db",
        tmp_path / "managed",
        image_decoder=decoder,
        font_catalog=marker_font_catalog,
        layout_engine=marker_layout,
        compositor=marker_compositor,
        source_styles=SourceStyleService(PixelSourceStyleAnalyzer()),
    )
    try:
        assert core.importer._decoder is decoder
        assert core.render._font_catalog is marker_font_catalog
        assert core.render._layout_engine is marker_layout
        assert core.render._compositor is marker_compositor
    finally:
        core.conn.close()


def test_legacy_assembly_injects_the_qt_adapters_into_the_core(
    tmp_path: Path,
) -> None:
    # 生产路径（I1-AC3/AC4）：Legacy Qt 装配构造 Qt 适配器并注入 Core；
    # 组合后的 AppServices 持有的正是这些 Qt 实例。
    from bootstrap.app import assemble_services
    from infrastructure.importing import QtImageDecoder
    from infrastructure.rendering.font_catalog import QtFontCatalog
    from infrastructure.rendering.qt_compositor import QtImageCompositor
    from infrastructure.rendering.qt_layout import QtTextLayoutEngine

    services = assemble_services(tmp_path / "library.db", tmp_path / "managed")
    try:
        assert isinstance(services.importer._decoder, QtImageDecoder)
        assert isinstance(services.render._font_catalog, QtFontCatalog)
        assert isinstance(services.render._layout_engine, QtTextLayoutEngine)
        assert isinstance(services.render._compositor, QtImageCompositor)
    finally:
        services.conn.close()


# ---------------------------------------------------------------------------
# I1-AC2 — no module-scope PySide6 in the Core layers
# ---------------------------------------------------------------------------


def test_domain_ports_application_have_no_module_scope_pyside6() -> None:
    offenders: list[str] = []
    for root in (DOMAIN_ROOT, PORTS_ROOT, APPLICATION_ROOT):
        for path in sorted(root.rglob("*.py")):
            for lineno, module in _module_scope_imports(
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            ):
                if module.lstrip(".").split(".", 1)[0] in _QT_ROOTS:
                    offenders.append(f"{path}:{lineno}: {module}")
    assert not offenders, (
        "the Python Core layers must not gain PySide6 dependencies:\n"
        + "\n".join(offenders)
    )


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _core_source() -> str:
    return CORE_ASSEMBLY_PATH.read_text(encoding="utf-8")


def _module_scope_imports(tree: ast.Module) -> list[tuple[int, str]]:
    """Imports that execute when the module is imported.

    Walks the module body and class bodies, but stops at function/lambda
    boundaries: an import inside a function body is the lazy form M2-D1
    already catalogued (e.g. ``application/export/pdf_qt.py``), which does
    not make the *import* of the module depend on Qt.
    """
    found: list[tuple[int, str]] = []

    def visit(nodes: list[ast.stmt]) -> None:
        for node in nodes:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                continue
            if isinstance(node, ast.Import):
                for alias in node.names:
                    found.append((node.lineno, alias.name))
            elif isinstance(node, ast.ImportFrom):
                prefix = "." * node.level
                module = f"{prefix}{node.module}" if node.module else prefix
                found.append((node.lineno, module))
            visit(
                [
                    child
                    for child in ast.iter_child_nodes(node)
                    if isinstance(child, ast.stmt)
                ]
            )

    visit(tree.body)
    return found


class _PassthroughDecoder:
    """Injection marker only — this test never imports a page."""

    def decode(self, data: bytes):  # pragma: no cover - never called
        raise AssertionError("the identity test does not import pages")
