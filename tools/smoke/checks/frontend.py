"""Layer 3: the existing frontend type-check and Vitest suites.

This layer deliberately runs the repository's own UI tests instead of a second
DOM/pixel harness: after an intentional UI/UX change, the tests are updated with
it, while the wire layer (layer 2) keeps the backend contract fixed.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import shutil

from tools.smoke import util
from tools.smoke.model import (
    CheckResult,
    CheckSpec,
    RunOptions,
    SmokeFailure,
    all_blocked,
    run_checks,
)

CHECKS: tuple[CheckSpec, ...] = (
    CheckSpec("FRONTEND-TSC", "前端 TypeScript 类型检查（tsc --noEmit）"),
    CheckSpec("FRONTEND-VITEST", "前端全量 Vitest 通过（UI/UX 契约）"),
)

_TEST_FILES_PATTERN = re.compile(r"Test Files\s+(\d+)\s+passed")
_TESTS_PATTERN = re.compile(r"Tests\s+(\d+)\s+passed")
_FAILED_PATTERN = re.compile(r"(?:Tests|Test Files)\s+\d+\s+failed")


@dataclass
class _FrontendContext:
    frontend: Path
    node: str
    tsc: Path
    vitest: Path
    logs: Path


def run(options: RunOptions) -> list[CheckResult]:
    frontend = util.REPO_ROOT / "apps" / "desktop" / "frontend"
    node = shutil.which("node")
    tsc = frontend / "node_modules" / "typescript" / "bin" / "tsc"
    vitest = frontend / "node_modules" / "vitest" / "vitest.mjs"
    if node is None:
        return all_blocked(
            CHECKS,
            "FRONTEND-NODE-MISSING",
            "node 不在 PATH 中，无法执行前端类型检查与测试",
        )
    if not frontend.is_dir() or not tsc.is_file() or not vitest.is_file():
        return all_blocked(
            CHECKS,
            "FRONTEND-DEPS-MISSING",
            "apps/desktop/frontend/node_modules 或 tsc/vitest 入口缺失；先执行 npm ci",
        )
    context = _FrontendContext(
        frontend=frontend,
        node=node,
        tsc=tsc,
        vitest=vitest,
        logs=options.logs_dir,
    )
    return run_checks(_ENTRIES, context)


def _check_tsc(context: _FrontendContext) -> dict:
    result = util.run_command(
        [
            context.node,
            str(context.tsc),
            "--noEmit",
            "-p",
            str(context.frontend / "tsconfig.json"),
        ],
        cwd=context.frontend,
        timeout=180,
        log_path=context.logs / "frontend-tsc.log",
        env=_frontend_environment(),
    )
    if result.timed_out:
        raise SmokeFailure("FRONTEND_TSC_TIMEOUT", "tsc --noEmit 超过 180s", {"log": str(result.log_path)})
    if result.exit_code != 0:
        raise SmokeFailure(
            "FRONTEND_TSC_FAILED",
            f"tsc --noEmit 退出码 {result.exit_code}：{util.tail(result.combined)}",
            {"log": str(result.log_path)},
        )
    return {"duration_ms": result.duration_ms}


def _check_vitest(context: _FrontendContext) -> dict:
    result = util.run_command(
        [context.node, str(context.vitest), "run"],
        cwd=context.frontend,
        timeout=240,
        log_path=context.logs / "frontend-vitest.log",
        env=_frontend_environment(),
    )
    if result.timed_out:
        raise SmokeFailure("FRONTEND_VITEST_TIMEOUT", "Vitest 超过 240s", {"log": str(result.log_path)})
    if result.exit_code != 0:
        raise SmokeFailure(
            "FRONTEND_VITEST_FAILED",
            f"Vitest 退出码 {result.exit_code}：{util.tail(result.combined)}",
            {"log": str(result.log_path)},
        )
    files_match = _TEST_FILES_PATTERN.search(result.combined)
    tests_match = _TESTS_PATTERN.search(result.combined)
    if files_match is None or tests_match is None:
        raise SmokeFailure(
            "FRONTEND_VITEST_OUTPUT",
            f"无法从 Vitest 输出解析通过数：{util.tail(result.combined)}",
            {"log": str(result.log_path)},
        )
    if _FAILED_PATTERN.search(result.combined):
        raise SmokeFailure(
            "FRONTEND_VITEST_FAILED_COUNT",
            f"Vitest 输出包含失败计数：{util.tail(result.combined)}",
            {"log": str(result.log_path)},
        )
    files = int(files_match.group(1))
    tests = int(tests_match.group(1))
    if files <= 0 or tests <= 0:
        raise SmokeFailure(
            "FRONTEND_VITEST_EMPTY",
            "Vitest 没有运行任何测试文件，不能当作通过",
            {"log": str(result.log_path)},
        )
    return {"test_files": files, "tests": tests, "duration_ms": result.duration_ms}


def _frontend_environment() -> dict[str, str]:
    env = os.environ.copy()
    env["CI"] = "1"
    env["NO_COLOR"] = "1"
    env["FORCE_COLOR"] = "0"
    return env


_ENTRIES = ((CHECKS[0], _check_tsc), (CHECKS[1], _check_vitest))
