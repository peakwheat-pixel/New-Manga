"""Layer 4: the real packaged ``core-sidecar`` Python runtime.

The shipped sidecar cannot rely on the host Python. This layer proves the real
bundle directory contains a working ``python/python.exe`` and that the plugin
Hook path executes inside the AppContainer with that interpreter.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import sys

from tools.smoke import util
from tools.smoke.model import (
    CheckResult,
    CheckSpec,
    RunOptions,
    SmokeFailure,
    SmokeSkip,
    all_blocked,
    run_checks,
)

util.ensure_src_on_path()

from infrastructure.plugins.sandbox import AppContainerSandbox  # noqa: E402
from infrastructure.plugins.service import PluginService  # noqa: E402
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402

CHECKS: tuple[CheckSpec, ...] = (
    CheckSpec("PACKAGED-BUNDLE-FILES", "真实 core-sidecar bundle 的 Python 运行时布局完整"),
    CheckSpec("PACKAGED-RUNTIME-SMOKE", "bundle 解释器在最小 PATH 下启动并导入 Hook 所需标准库"),
    CheckSpec("PACKAGED-FROZEN-RESOLVE", "模拟 frozen sidecar 时 _hook_interpreter() 解析到 bundle 解释器"),
    CheckSpec("PACKAGED-SANDBOX-HOOK", "bundle 解释器在真实 AppContainer 中执行插件 Hook"),
    CheckSpec("PACKAGED-REPACK-VERIFY", "--repack：复用 verify_bundled_python.ps1 复验复制与 Hook"),
)

_APP_VERSION = "0.1.0"
_BUNDLE_DIR = (
    util.REPO_ROOT
    / "apps"
    / "desktop"
    / "src-tauri"
    / "target"
    / "core-sidecar"
    / "core-sidecar"
)
_BUNDLED_PYTHON = _BUNDLE_DIR / "python" / "python.exe"


@dataclass
class _PackagedContext:
    bundle_dir: Path
    python: Path
    logs: Path
    run_root: Path
    repack: bool


def run(options: RunOptions) -> list[CheckResult]:
    if not _BUNDLED_PYTHON.is_file():
        return all_blocked(
            CHECKS,
            "PACKAGED-BUNDLE-MISSING",
            f"未找到真实 core-sidecar bundle 解释器：{_BUNDLED_PYTHON.relative_to(util.REPO_ROOT)}",
        )
    context = _PackagedContext(
        bundle_dir=_BUNDLE_DIR,
        python=_BUNDLED_PYTHON,
        logs=options.logs_dir,
        run_root=options.run_root,
        repack=options.repack,
    )
    try:
        return run_checks(_ENTRIES, context)
    finally:
        pass


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _check_bundle_files(context: _PackagedContext) -> dict:
    required = (
        "python/python.exe",
        "python/plugin-python.txt",
        "python/Lib/os.py",
        "python/DLLs",
    )
    missing = [
        relative
        for relative in required
        if not (context.bundle_dir / relative).exists()
    ]
    if missing:
        raise SmokeFailure(
            "PACKAGED_LAYOUT_INCOMPLETE",
            f"bundle 运行时布局不完整，缺少：{missing}",
        )
    return {
        "bundle": "apps/desktop/src-tauri/target/core-sidecar/core-sidecar",
        "interpreter": "python/python.exe",
        "required": list(required),
    }


def _check_runtime_smoke(context: _PackagedContext) -> dict:
    env = os.environ.copy()
    env["PATH"] = f"{os.environ.get('SystemRoot', 'C:/Windows')}/System32;{os.environ.get('SystemRoot', 'C:/Windows')}"
    result = util.run_command(
        [
            str(context.python),
            "-I",
            "-c",
            "import socket, ssl, sqlite3, json, hashlib; print('bundled-runtime-ok')",
        ],
        cwd=context.bundle_dir,
        timeout=120,
        log_path=context.logs / "packaged-runtime-smoke.log",
        env=env,
    )
    if result.timed_out:
        raise SmokeFailure("PACKAGED_RUNTIME_TIMEOUT", "bundle 解释器启动超过 120s")
    if result.exit_code != 0 or "bundled-runtime-ok" not in result.combined:
        raise SmokeFailure(
            "PACKAGED_RUNTIME_FAILED",
            f"bundle 解释器最小 PATH 启动失败（exit={result.exit_code}）：{util.tail(result.combined)}",
        )
    return {"duration_ms": result.duration_ms}


def _check_frozen_resolve(context: _PackagedContext) -> dict:
    script_path = context.run_root / "packaged" / "frozen_resolve_check.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    expected = context.python
    sidecar = context.bundle_dir / "core_service.exe"
    script = (
        "import sys\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {str(util.SRC_ROOT)!r})\n"
        "sys.frozen = True\n"
        f"sys.executable = {str(sidecar)!r}\n"
        "from infrastructure.plugins.service import _hook_interpreter\n"
        "resolved = _hook_interpreter()\n"
        f"expected = {str(expected)!r}\n"
        "assert Path(resolved) == Path(expected), "
        "f'unexpected interpreter: {resolved!r} (expected {expected!r})'\n"
        "print('frozen-resolution-ok:', resolved)\n"
    )
    script_path.write_text(script, encoding="utf-8")
    result = util.run_command(
        [sys.executable, "-I", str(script_path)],
        cwd=util.REPO_ROOT,
        timeout=120,
        log_path=context.logs / "packaged-frozen-resolve.log",
    )
    if result.timed_out:
        raise SmokeFailure("PACKAGED_FROZEN_TIMEOUT", "frozen 解析检查超过 120s")
    if result.exit_code != 0 or "frozen-resolution-ok" not in result.combined:
        raise SmokeFailure(
            "PACKAGED_FROZEN_FAILED",
            f"frozen 解析失败（exit={result.exit_code}）：{util.tail(result.combined)}",
        )
    return {"resolved": "python/python.exe"}


def _check_sandbox_hook(context: _PackagedContext) -> dict:
    data_root = context.run_root / "packaged-data"
    plugin_root = data_root / "plugins"
    plugin = plugin_root / "smoke-bundled"
    plugin.mkdir(parents=True, exist_ok=True)
    (plugin / "plugin.py").write_text(
        "def after_detect(payload):\n    return {'bundled': True}\n", encoding="utf-8"
    )
    (plugin / "manifest.json").write_text(
        json.dumps(
            {
                "id": "smoke-bundled",
                "name": "smoke-bundled",
                "version": "1.0.0",
                "entry": "plugin.py",
                "hooks": ["after_detect"],
                "permissions": [],
            }
        ),
        encoding="utf-8",
    )
    conn, _opened = open_database(
        data_root / "library.db",
        latest_known_schema_version=max(m.schema_version for m in default_migrations()),
    )
    sandbox = AppContainerSandbox(interpreter=str(context.python))
    # The tool process itself is the source interpreter, so _hook_interpreter()
    # would return that unless the frozen branch is simulated. The separate
    # PACKAGED-FROZEN-RESOLVE check proves the real frozen resolution; here we
    # pin the resolved interpreter to the bundle so this check really executes
    # the Hook with bundle python/python.exe.
    import infrastructure.plugins.service as service_module

    original_interpreter = service_module._hook_interpreter
    service_module._hook_interpreter = lambda: str(context.python)
    try:
        MigrationRunner(conn, default_migrations()).apply_pending()
        service = PluginService(
            conn,
            plugin_root,
            app_version=_APP_VERSION,
            sandbox=sandbox,
            allow_unsandboxed=False,
        )
        service.set_global_enabled(True)
        service.set_plugin_enabled("smoke-bundled", True)
        outcome = service.run_hook("after_detect", {})
        if outcome.get("applied") is not True:
            raise SmokeFailure(
                "PACKAGED_HOOK_FAILED",
                f"bundle 解释器 AppContainer Hook 未执行：{outcome.get('errors')}",
            )
        result = outcome["results"][0]["result"]
        if result != {"bundled": True}:
            raise SmokeFailure(
                "PACKAGED_HOOK_RESULT", f"bundle Hook 返回不符合预期：{result!r}"
            )
        return {"hook": "after_detect", "result": result, "interpreter": "bundle python.exe"}
    finally:
        service_module._hook_interpreter = original_interpreter
        sandbox.close()
        conn.close()


def _check_repack(context: _PackagedContext) -> dict:
    # Reuse the canonical packaging verification script when explicitly asked;
    # this is intentionally opt-in because it copies a full Python runtime.
    if not context.repack:
        raise SmokeSkip("EXPECTED_REPACK_DISABLED", "未传 --repack，跳过打包脚本复验")
    shell = util.find_executable(("pwsh", "powershell"))
    if shell is None:
        raise SmokeFailure("PACKAGED_NO_POWERSHELL", "找不到 pwsh/powershell")
    script = util.REPO_ROOT / "packaging" / "m2ac5" / "verify_bundled_python.ps1"
    if not script.is_file():
        raise SmokeFailure("PACKAGED_VERIFY_SCRIPT_MISSING", "找不到 verify_bundled_python.ps1")
    out_dir = context.run_root / "repack-verify"
    result = util.run_command(
        [
            shell,
            "-NoProfile",
            "-File",
            str(script),
            "-PythonRuntime",
            sys.base_prefix,
            "-OutDir",
            str(out_dir),
        ],
        cwd=util.REPO_ROOT,
        timeout=300,
        log_path=context.logs / "packaged-repack-verify.log",
    )
    if result.timed_out:
        raise SmokeFailure("PACKAGED_REPACK_TIMEOUT", "verify_bundled_python.ps1 超过 300s")
    if result.exit_code != 0 or "verify_bundled_python: OK" not in result.combined:
        raise SmokeFailure(
            "PACKAGED_REPACK_FAILED",
            f"verify_bundled_python.ps1 失败（exit={result.exit_code}）：{util.tail(result.combined)}",
        )
    return {"script": "packaging/m2ac5/verify_bundled_python.ps1", "exit": result.exit_code}


_ENTRIES = (
    (CHECKS[0], _check_bundle_files),
    (CHECKS[1], _check_runtime_smoke),
    (CHECKS[2], _check_frozen_resolve),
    (CHECKS[3], _check_sandbox_hook),
    (CHECKS[4], _check_repack),
)
