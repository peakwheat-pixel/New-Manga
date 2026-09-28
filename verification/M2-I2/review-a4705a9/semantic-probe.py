from __future__ import annotations

import ast
import itertools
import subprocess
import sys
import tempfile
import types
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "6a68fdeb92d8a1c7903166a8076d6260bf8fa79a"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests" / "workbench"))
sys.path.insert(0, str(ROOT))

from domain.tasks.models import (
    PipelineRunStatus,
    PipelineScope,
    PipelineTaskStatus,
    ScopeType,
    StepRun,
    StepRunStatus,
)
from application.tasks import projection as new_projection
from application.editing import region_canvas as new_canvas
from workbench_helpers import make_pipeline
from tests.core.test_architecture import (
    APPLICATION_FORBIDDEN,
    QT_FORBIDDEN,
    find_forbidden_imports,
)


def git_source(path: str) -> str:
    return subprocess.run(
        ["git", "show", f"{BASE}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True, encoding="utf-8",
    ).stdout


def load_source(name: str, path: str, source: str):
    module = types.ModuleType(name)
    module.__file__ = path
    sys.modules[name] = module
    exec(compile(source, path, "exec"), module.__dict__)
    return module


def ast_without_docstring(source: str) -> str:
    tree = ast.parse(source)
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        tree.body.pop(0)
    return ast.dump(tree, include_attributes=False)


old_projection_source = git_source("src/ui/models/tasks/projection.py")
old_canvas_source = git_source("src/ui/viewmodels/workbench/region_canvas.py")
old_projection = load_source(
    "review_old_projection",
    "base:src/ui/models/tasks/projection.py",
    old_projection_source,
)
old_canvas = load_source(
    "review_old_canvas",
    "base:src/ui/viewmodels/workbench/region_canvas.py",
    old_canvas_source,
)

assert ast_without_docstring(old_projection_source) == ast_without_docstring(
    (ROOT / "src/application/tasks/projection.py").read_text(encoding="utf-8")
)
assert ast_without_docstring(old_canvas_source) == ast_without_docstring(
    (ROOT / "src/application/editing/region_canvas.py").read_text(encoding="utf-8")
)
print("AST compatibility after module docstring removal: projection=IDENTICAL; region_canvas=IDENTICAL")

projection_cases = 0
for status in PipelineRunStatus:
    for has_failures in (False, True):
        assert old_projection._button_enablement(status, has_failures) == (
            new_projection._button_enablement(status, has_failures)
        )
        projection_cases += 1

service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
run = service.create_run(
    "translate_all", PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
)
service.plan_run(run.run_id)
meta = {"p1": (1, "001.png", False), "p2": (2, "002.png", True)}


def compare_projection(label: str, sample) -> None:
    old_value = old_projection.build_projection(sample, meta)
    new_value = new_projection.build_projection(sample, meta)
    assert asdict(old_value) == asdict(new_value), label
    print(f"projection scenario {label}: IDENTICAL")


compare_projection("pending", run)

service_done, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
done = service_done.create_run(
    "translate_all", PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
)
service_done.plan_run(done.run_id)
service_done.execute_run(done.run_id)
compare_projection("completed", done)

blocked_service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
blocked = blocked_service.create_run(
    "translate_all", PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
)
blocked_service.plan_run(blocked.run_id)
blocked.tasks[0].status = PipelineTaskStatus.BLOCKED
blocked.tasks[0].error_code = "MISSING_REQUIRED_INPUT"
blocked.status = PipelineRunStatus.BLOCKED
compare_projection("blocked", blocked)

focused_service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
focused = focused_service.create_run(
    "translate_all", PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
)
focused_service.plan_run(focused.run_id)
focused.status = PipelineRunStatus.RUNNING
focused.tasks[0].status = PipelineTaskStatus.RUNNING
focused.tasks[1].status = PipelineTaskStatus.PENDING
focused.step_runs.append(
    StepRun(
        step_run_id="review-s1",
        task_id=focused.tasks[0].task_id,
        target_id="p1",
        page_id="p1",
        region_id=None,
        step_type="ocr",
        status=StepRunStatus.RUNNING,
    )
)
compare_projection("running_focus_step_flow", focused)

failed_service, _ = make_pipeline(pages=[("p1", 1), ("p2", 2)])
failed = failed_service.create_run(
    "translate_all", PipelineScope(ScopeType.CHAPTER, chapter_id="chapter-1")
)
failed_service.plan_run(failed.run_id)
failed.tasks[0].status = PipelineTaskStatus.FAILED
failed.tasks[0].error_code = "REVIEW_FAILURE"
failed.status = PipelineRunStatus.COMPLETED_WITH_FAILURES
compare_projection("failed_page", failed)

page_statuses = [
    PipelineTaskStatus.FAILED,
    PipelineTaskStatus.RUNNING,
    PipelineTaskStatus.BLOCKED,
    PipelineTaskStatus.COMPLETED,
    PipelineTaskStatus.SKIPPED,
    PipelineTaskStatus.PENDING,
]
for mask in range(1 << len(page_statuses)):
    group = []
    for index, status in enumerate(page_statuses):
        if mask & (1 << index):
            group.append(types.SimpleNamespace(status=status, error_code=status.value))
    assert old_projection._classify_page(group) == new_projection._classify_page(group)
    projection_cases += 1
print("projection page-status sets compared: 64")
print(f"projection precedence/button checks passed: {projection_cases}")

geometry_cases = [
    ([(0.125, 0.625), (0.5, 0.5)], 100, 100, "half_up"),
    ([(0.125, 1 / 6), (0.625, 2 / 3)], 800, 1200, "normalized_rectangle"),
    ([(0.75, 0.5), (0.25, 0.25)], 800, 1200, "rectangle_reverse_corners"),
    ([(0.0, 0.0), (0.5, 0.0), (0.5, 1.0)], 800, 1200, "triangle"),
    ([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)], 500, 500, "polygon"),
    ([(-0.2, -0.1), (1.4, 1.2)], 100, 100, "clamped"),
    ([], 100, 100, "too_few_empty"),
    ([(0.1, 0.1)], 100, 100, "too_few_single"),
    ([(0.1, 0.1), (0.1, 0.5)], 100, 100, "zero_width"),
    ([(0.1, 0.1), (0.5, 0.1)], 100, 100, "zero_height"),
    ([(0.1, 0.1), (0.5, 0.5), (0.9, 0.9)], 100, 100, "collinear"),
    ([(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.1)], 100, 100, "zero_area_ring"),
    ([(0.1, 0.1), (0.9, 0.9)], 0, 100, "invalid_width"),
    ([(0.1, 0.1), (0.9, 0.9)], 100, -1, "invalid_height"),
]


def geometry_result(function, points, width, height):
    try:
        geometry = function(points, width, height)
        return (
            "ok",
            asdict(geometry.bbox),
            geometry.polygon,
        )
    except Exception as error:
        return (
            "error",
            type(error).__name__,
            getattr(error, "code", None),
            getattr(error, "detail", None),
            str(error),
        )


for points, width, height, label in geometry_cases:
    old_result = geometry_result(old_canvas.normalized_to_page_geometry, points, width, height)
    new_result = geometry_result(new_canvas.normalized_to_page_geometry, points, width, height)
    assert old_result == new_result, (label, old_result, new_result)
print(f"region_canvas output/error contract comparisons passed: {len(geometry_cases)}")
assert new_canvas._to_pixels(0.125, 100) == 13
assert new_canvas._to_pixels(0.625, 100) == 63
print("half-up exact tie check: floor(n * size + 0.5) yields 13 and 63")

with tempfile.TemporaryDirectory(prefix="m2-i2-review-negative-") as directory:
    app_root = Path(directory) / "src" / "application"
    projection_path = app_root / "tasks" / "projection.py"
    projection_path.parent.mkdir(parents=True)
    projection_path.write_text(
        "from ui.models.tasks.projection import build_projection\n",
        encoding="utf-8",
    )
    violations_a = find_forbidden_imports(app_root, APPLICATION_FORBIDDEN)
    assert violations_a and "ui.models.tasks.projection" in violations_a[0]
    print(f"Negative A (application -> ui import) detected: {violations_a[0]}")

    mutant_qt_path = app_root / "editing" / "region_canvas.py"
    mutant_qt_path.parent.mkdir(parents=True)
    mutant_qt_path.write_text(
        (ROOT / "src/application/editing/region_canvas.py").read_text(encoding="utf-8")
        + "\nimport PySide6\n",
        encoding="utf-8",
    )
    violations_b = find_forbidden_imports(mutant_qt_path, QT_FORBIDDEN)
    assert violations_b and "PySide6" in violations_b[0]
    print(f"Negative B (PySide6 in copied application seam) detected: {violations_b[0]}")

priority_cases = [
    ("failed", [PipelineTaskStatus.FAILED, PipelineTaskStatus.RUNNING, PipelineTaskStatus.BLOCKED, PipelineTaskStatus.COMPLETED, PipelineTaskStatus.SKIPPED, PipelineTaskStatus.PENDING]),
    ("processing", [PipelineTaskStatus.RUNNING, PipelineTaskStatus.BLOCKED, PipelineTaskStatus.COMPLETED, PipelineTaskStatus.SKIPPED, PipelineTaskStatus.PENDING]),
    ("blocked", [PipelineTaskStatus.BLOCKED, PipelineTaskStatus.COMPLETED, PipelineTaskStatus.SKIPPED, PipelineTaskStatus.PENDING]),
    ("completed", [PipelineTaskStatus.COMPLETED]),
    ("skipped", [PipelineTaskStatus.SKIPPED]),
    ("waiting", [PipelineTaskStatus.PENDING]),
]
for expected, statuses in priority_cases:
    tasks = [types.SimpleNamespace(status=status, error_code=status.value) for status in statuses]
    result = new_projection._classify_page(tasks)
    assert result[0] == expected, (expected, result)
print("required precedence failed > processing > blocked > completed > skipped > waiting: PASS")

with tempfile.TemporaryDirectory(prefix="m2-i2-review-dynamic-all-") as directory:
    dynamic_shim = Path(directory) / "projection.py"
    dynamic_shim.write_text(
        "from application.tasks.projection import TaskProjection\n"
        "__all__ = (lambda: ['TaskProjection'])()\n",
        encoding="utf-8",
    )
    dynamic_violations = __import__(
        "tests.core.test_architecture",
        fromlist=["find_shim_violations"],
    ).find_shim_violations(
        dynamic_shim,
        allowed_seam="application.tasks.projection",
    )
    assert not dynamic_violations
    print("R-003 dynamic __all__ expression bypass reproduced: Guard violations: []")

print("RESULT: PASS")


