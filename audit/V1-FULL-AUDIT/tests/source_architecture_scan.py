#!/usr/bin/env python3
"""只读盘点当前审计清单中的 Python 语法和项目依赖图。

该扫描器仅使用 Python 标准库；不安装依赖、不改源码、不运行应用。
它报告语法解析错误、静态可见的本地导入/项目引用环及未完成标记计数，
不把文本命中解释为缺陷，也不能解析动态导入或 C# 方法级依赖。
"""
from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "audit/V1-FULL-AUDIT/evidence/source-manifest-segment-b.json"
MARKERS = {
    "TODO": re.compile(r"\bTODO\b", re.IGNORECASE),
    "FIXME": re.compile(r"\bFIXME\b", re.IGNORECASE),
    "NotImplementedError": re.compile(r"\bNotImplementedError\b"),
    "NotImplementedException": re.compile(r"\bNotImplementedException\b"),
}
SOURCE_SUFFIXES = {".py", ".cs", ".axaml", ".xaml", ".csproj", ".ps1"}


def git_head() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()


def strongly_connected_components(graph: dict[str, set[str]]) -> list[list[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlinks: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = index
        lowlinks[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for neighbor in sorted(graph.get(node, set())):
            if neighbor not in graph:
                continue
            if neighbor not in indices:
                visit(neighbor)
                lowlinks[node] = min(lowlinks[node], lowlinks[neighbor])
            elif neighbor in on_stack:
                lowlinks[node] = min(lowlinks[node], indices[neighbor])
        if lowlinks[node] == indices[node]:
            component: list[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node:
                    break
            if len(component) > 1 or node in graph.get(node, set()):
                components.append(sorted(component))

    for item in sorted(graph):
        if item not in indices:
            visit(item)
    return sorted(components)


def nearest_local_module(name: str, modules: set[str]) -> str | None:
    parts = name.split(".") if name else []
    while parts:
        candidate = ".".join(parts)
        if candidate in modules:
            return candidate
        parts.pop()
    return None


def module_name(path: Path, src_root: Path) -> tuple[str, bool]:
    relative = path.relative_to(src_root).with_suffix("")
    is_package = relative.name == "__init__"
    if is_package:
        relative = relative.parent
    return ".".join(relative.parts), is_package


def python_import_graph(paths: list[Path]) -> tuple[dict[str, set[str]], int]:
    src_root = ROOT / "src"
    module_paths = [p for p in paths if p.suffix == ".py" and p.is_relative_to(src_root)]
    names = {p: module_name(p, src_root) for p in module_paths}
    modules = {name for name, _is_package in names.values() if name}
    graph = {name: set() for name in modules}
    dynamic_import_calls = 0

    for path, (current, is_package) in names.items():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError):
            continue
        package = current if is_package else current.rpartition(".")[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    target = nearest_local_module(alias.name, modules)
                    if target and target != current:
                        graph[current].add(target)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    parts = package.split(".") if package else []
                    remove = node.level - 1
                    if remove:
                        parts = parts[:-remove] if remove < len(parts) else []
                    prefix = ".".join(part for part in (".".join(parts), node.module or "") if part)
                else:
                    prefix = node.module or ""
                target = nearest_local_module(prefix, modules)
                if target and target != current:
                    graph[current].add(target)
                for alias in node.names:
                    alias_target = nearest_local_module(
                        ".".join(part for part in (prefix, alias.name) if part), modules
                    )
                    if alias_target and alias_target != current:
                        graph[current].add(alias_target)
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "__import__":
                    dynamic_import_calls += 1
                elif (
                    isinstance(func, ast.Attribute)
                    and func.attr == "import_module"
                ):
                    dynamic_import_calls += 1
    return graph, dynamic_import_calls


def dotnet_project_graph(paths: list[Path]) -> tuple[dict[str, set[str]], list[str]]:
    src_root = ROOT / "apps/desktop-avalonia/src"
    projects = [p for p in paths if p.suffix == ".csproj" and p.is_relative_to(src_root)]
    known = {p.resolve(): p.relative_to(ROOT).as_posix() for p in projects}
    graph = {relative: set() for relative in known.values()}
    missing: list[str] = []
    for path in projects:
        current = path.relative_to(ROOT).as_posix()
        try:
            tree = ET.parse(path)
        except ET.ParseError as error:
            missing.append(f"invalid-project-xml:{current}:{error}")
            continue
        for reference in tree.iter():
            if reference.tag.rsplit("}", 1)[-1] != "ProjectReference":
                continue
            include = reference.attrib.get("Include", "")
            if not include:
                continue
            target_path = (path.parent / include.replace("\\", "/")).resolve()
            target = known.get(target_path)
            if target:
                graph[current].add(target)
            else:
                missing.append(f"unmanifested-project-reference:{current}:{include}")
    return graph, missing


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = [e for e in manifest["entries"] if e.get("class") == "target_source"]
    paths = [ROOT / e["path"] for e in entries]
    missing_paths = [p.relative_to(ROOT).as_posix() for p in paths if not p.is_file()]
    python_paths = [p for p in paths if p.suffix == ".py" and p.is_file()]
    syntax_errors: list[dict[str, object]] = []
    for path in python_paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as error:
            syntax_errors.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "line": error.lineno,
                    "message": error.msg,
                }
            )
        except UnicodeDecodeError as error:
            syntax_errors.append(
                {"path": path.relative_to(ROOT).as_posix(), "message": str(error)}
            )

    py_graph, py_dynamic_calls = python_import_graph(paths)
    cs_graph, cs_missing = dotnet_project_graph(paths)
    marker_counts: Counter[str] = Counter()
    marker_examples: dict[str, list[dict[str, object]]] = {key: [] for key in MARKERS}
    for path in paths:
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(ROOT).as_posix()
        for number, line in enumerate(lines, 1):
            for marker, pattern in MARKERS.items():
                if pattern.search(line):
                    marker_counts[marker] += 1
                    if len(marker_examples[marker]) < 80:
                        marker_examples[marker].append(
                            {"path": relative, "line": number, "text": line.strip()[:240]}
                        )

    report = {
        "generated_head": git_head(),
        "product_base": manifest.get("product_base"),
        "manifest_source_files": len(entries),
        "missing_manifest_paths": missing_paths,
        "python": {
            "source_files": len(python_paths),
            "syntax_errors": syntax_errors,
            "local_modules": len(py_graph),
            "static_local_import_edges": sum(map(len, py_graph.values())),
            "static_import_cycles": strongly_connected_components(py_graph),
            "dynamic_import_call_sites": py_dynamic_calls,
        },
        "dotnet": {
            "source_projects": len(cs_graph),
            "project_reference_edges": sum(map(len, cs_graph.values())),
            "project_reference_cycles": strongly_connected_components(cs_graph),
            "unresolved_or_invalid_references": cs_missing,
        },
        "source_marker_counts": dict(sorted(marker_counts.items())),
        "source_marker_examples_capped_at_80_per_kind": marker_examples,
        "limitations": [
            "Python imports are inferred from AST; dynamic/plugin imports and runtime dispatch are incomplete.",
            "C# graph uses project references only; it does not model method-level calls or assembly reflection.",
            "TODO/FIXME/NotImplemented hits are text markers, not defect findings.",
            "This scanner does not type-check, analyze null flow, or prove runtime/resource behavior.",
        ],
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
