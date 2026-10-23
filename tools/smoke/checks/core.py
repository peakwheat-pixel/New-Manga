"""Layer 1: real production assembly + real Windows AppContainer checks.

Everything here runs against the *production* assembly (``assemble_production_core``)
and is isolated under ``options.run_root``; nothing touches the user's data root.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
import time

from tools.smoke import util
from tools.smoke.model import (
    CheckResult,
    CheckSpec,
    RunOptions,
    SmokeFailure,
    all_blocked,
    run_checks,
)

util.ensure_src_on_path()

from bootstrap.core_service import assemble_production_core  # noqa: E402
import infrastructure.plugins.service as plugin_service_module  # noqa: E402
from infrastructure.plugins.manifest import parse_manifest  # noqa: E402
from infrastructure.plugins.sandbox import AppContainerSandbox, SandboxError  # noqa: E402
from infrastructure.plugins.service import (  # noqa: E402
    PluginError,
    PluginService,
    resolve_hook_interpreter,
)

_APP_VERSION = "0.1.0"
_SECRET = "TOP-SECRET-SMOKE"

_NET_PROBE = """import socket
def after_detect(payload):
    try:
        sock = socket.create_connection(('1.1.1.1', 443), timeout=4)
        sock.close()
        return {'net': 'OK'}
    except OSError as error:
        return {'net': 'BLOCKED', 'kind': type(error).__name__}
"""

_FS_PROBE = """import os
def after_detect(payload):
    here = os.path.dirname(os.path.abspath(__file__))
    secret = os.path.join(os.path.dirname(here), 'secret.txt')
    try:
        data = open(secret, encoding='utf-8').read()
        return {'fs': 'READ_OK', 'data': data}
    except OSError as error:
        return {'fs': 'BLOCKED', 'winerror': getattr(error, 'winerror', None)}
"""

_TREE_HANG = """import subprocess, sys, time
def after_detect(payload):
    child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
    print(child.pid, flush=True)
    time.sleep(60)
    return {'ok': True}
"""

#: id -> (source, permissions)
_PLUGIN_FIXTURES: dict[str, tuple[str, tuple[str, ...]]] = {
    "smoke-load-ok": ("def after_detect(payload):\n    return {'ok': True}\n", ()),
    "smoke-rejected-files": (
        "def after_detect(payload):\n    return {'ok': True}\n",
        ("files_read",),
    ),
    "smoke-benign": (
        "def after_detect(payload):\n"
        "    return {'pages': len(payload.get('pages', [])),"
        " 'schema_ref': payload.get('schema_ref')}\n",
        (),
    ),
    "smoke-fs-read": (_FS_PROBE, ()),
    "smoke-net-none": (_NET_PROBE, ()),
    "smoke-net-ok": (_NET_PROBE, ("network",)),
    "smoke-hang": (
        "import time\n"
        "def after_detect(payload):\n"
        "    time.sleep(60)\n"
        "    return {'ok': True}\n",
        (),
    ),
    "smoke-tree-hang": (_TREE_HANG, ()),
}

CHECKS: tuple[CheckSpec, ...] = (
    CheckSpec("CORE-PRODUCTION-WIRING", "生产装配挂载真实 AppContainer，而非静默无沙箱"),
    CheckSpec("CORE-DISCOVERY", "插件发现、permissions 拒绝语义与权限徽标数据"),
    CheckSpec("CORE-STATE", "全局开关与插件启用/禁用往返，拒绝插件不可启用"),
    CheckSpec("CORE-BENIGN-HOOK", "无权限插件 Hook 正常执行并返回 schema_ref"),
    CheckSpec("CORE-FS-DENY", "插件根外读被 AppContainer 拒绝"),
    CheckSpec("CORE-NET-DENY", "无权限插件的网络栈被拒绝（PermissionError）"),
    CheckSpec("CORE-NET-ALLOW", "network 权限插件不被网络栈拒绝"),
    CheckSpec("CORE-TIMEOUT", "Hook 超时返回 PLUGIN_HOOK_TIMEOUT，不中断调用方"),
    CheckSpec("CORE-TREE-KILL", "超时后 Hook 子进程树被 Job Object 清理"),
    CheckSpec("CORE-FAIL-CLOSED", "无沙箱/沙箱损坏时 fail-closed 返回 PLUGIN_HOOK_UNAVAILABLE"),
    CheckSpec("CORE-AUDIT", "审计账本包含稳定事件类型且不写入 Hook 载荷"),
)


@dataclass
class _CoreContext:
    core: object
    service: PluginService
    data_root: Path
    plugin_root: Path
    interpreter: str
    runner: Path


def run(options: RunOptions) -> list[CheckResult]:
    if sys.platform != "win32":
        return all_blocked(
            CHECKS,
            "CORE-WINDOWS-ONLY",
            "真实 AppContainer 仅在 Windows 上可用",
        )
    try:
        context = _prepare(options)
    except Exception as error:  # noqa: BLE001 - a broken setup must not crash the report
        return all_blocked(
            CHECKS,
            "CORE-SETUP-FAILED",
            f"Core 层初始化失败：{type(error).__name__}: {error}",
        )
    try:
        return run_checks(_ENTRIES, context)
    finally:
        _cleanup(context)


# ---------------------------------------------------------------------------
# setup / cleanup
# ---------------------------------------------------------------------------
def _write_plugin(
    root: Path, plugin_id: str, source: str, permissions: tuple[str, ...]
) -> None:
    directory = root / plugin_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "plugin.py").write_text(source, encoding="utf-8")
    manifest = {
        "id": plugin_id,
        "name": plugin_id,
        "version": "1.0.0",
        "entry": "plugin.py",
        "hooks": ["after_detect"],
        "permissions": list(permissions),
        "description": "TOOL-SOFTWARE-SMOKE-1 fixture",
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False), encoding="utf-8"
    )


def _prepare(options: RunOptions) -> _CoreContext:
    data_root = options.run_root / "core-data"
    plugin_root = data_root / "plugins"
    plugin_root.mkdir(parents=True, exist_ok=True)
    (data_root / "secret.txt").write_text(_SECRET, encoding="utf-8")
    for plugin_id, (source, permissions) in _PLUGIN_FIXTURES.items():
        _write_plugin(plugin_root, plugin_id, source, permissions)

    core = assemble_production_core(data_root)
    service = getattr(core, "plugins", None)
    if service is None:
        raise SmokeFailure("CORE-PLUGIN-SERVICE-MISSING", "生产装配没有 PluginService")
    runner = Path(plugin_service_module.__file__).with_name("_hook_runner.py")
    if not runner.is_file():
        raise SmokeFailure("CORE-RUNNER-MISSING", "找不到 _hook_runner.py")
    return _CoreContext(
        core=core,
        service=service,
        data_root=data_root,
        plugin_root=plugin_root,
        interpreter=resolve_hook_interpreter(),
        runner=runner,
    )


def _cleanup(context: _CoreContext) -> None:
    sandbox = getattr(context.service, "_sandbox", None)
    if sandbox is not None:
        try:
            sandbox.close()
        except Exception:  # noqa: BLE001
            pass
    try:
        context.core.conn.close()
    except Exception:  # noqa: BLE001
        pass


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _check_wiring(context: _CoreContext) -> dict:
    sandbox = getattr(context.service, "_sandbox", None)
    if sandbox is None:
        raise SmokeFailure("CORE_SANDBOX_MISSING", "生产装配的 PluginService 没有沙箱")
    if not sandbox.available:
        raise SmokeFailure("CORE_SANDBOX_UNAVAILABLE", "AppContainer 沙箱不可用")
    if getattr(sandbox, "shared_profile", False):
        raise SmokeFailure(
            "CORE_SANDBOX_SHARED_PROFILE", "生产装配不应使用共享 AppContainer profile"
        )
    if getattr(context.service, "_allow_unsandboxed", None) is not False:
        raise SmokeFailure(
            "CORE_SANDBOX_NOT_REQUIRED",
            "生产装配必须设置 allow_unsandboxed=False（缺沙箱时 fail-closed）",
        )
    interpreter = Path(context.interpreter)
    if not interpreter.is_file():
        raise SmokeFailure(
            "CORE_INTERPRETER_MISSING", "Hook 解释器路径不存在（fail-closed 前置）"
        )
    return {
        "sandbox": type(sandbox).__name__,
        "shared_profile": False,
        "interpreter": interpreter.name,
    }


def _check_discovery(context: _CoreContext) -> dict:
    snapshot = context.service.list_plugins()
    _require(snapshot.get("global_enabled") is False, "CORE_GLOBAL_NOT_DEFAULT_OFF", "全局开关默认应为关闭")
    by_id = {item["plugin_id"]: item for item in snapshot["plugins"]}
    expected = set(_PLUGIN_FIXTURES)
    _require(expected <= set(by_id), "CORE_DISCOVERY_INCOMPLETE", "未发现全部夹具插件")
    _require(
        by_id["smoke-load-ok"]["status"] == "disabled",
        "CORE_DISCOVERY_STATUS",
        "合法插件初始状态应为 disabled",
    )
    rejected = by_id["smoke-rejected-files"]
    _require(rejected["status"] == "rejected", "CORE_REJECTION_STATUS", "files_read 插件应被拒绝")
    reason = rejected.get("reason") or ""
    _require(
        reason.startswith("PLUGIN_PERMISSIONS_UNSUPPORTED"),
        "CORE_REJECTION_REASON",
        f"拒绝原因应以 PLUGIN_PERMISSIONS_UNSUPPORTED 开头，实际 {reason!r}",
    )
    _require(
        by_id["smoke-net-ok"]["permissions"] == ["network"],
        "CORE_PERMISSION_BADGE",
        "network 插件的权限徽标数据应为 ['network']",
    )
    _require(
        by_id["smoke-load-ok"]["permissions"] == [],
        "CORE_PERMISSION_BADGE",
        "无权限插件的权限徽标数据应为 []",
    )
    audit_types = {event["event_type"] for event in context.service.audit_list(100)}
    _require("load_ok" in audit_types, "CORE_DISCOVERY_AUDIT", "审计缺少 load_ok")
    _require("load_rejected" in audit_types, "CORE_DISCOVERY_AUDIT", "审计缺少 load_rejected")
    return {
        "plugins": len(by_id),
        "rejected": rejected["plugin_id"],
        "audit_types": sorted(audit_types),
    }


def _check_state(context: _CoreContext) -> dict:
    service = context.service
    _enable_only(service, "smoke-benign")
    listed = {item["plugin_id"]: item for item in service.list_plugins()["plugins"]}
    _require(listed["smoke-benign"]["status"] == "enabled", "CORE_STATE_ENABLE", "启用后状态应为 enabled")
    _require(listed["smoke-benign"]["enabled"] is True, "CORE_STATE_ENABLE", "启用后 enabled 应为 true")

    service.set_plugin_enabled("smoke-benign", False)
    listed = {item["plugin_id"]: item for item in service.list_plugins()["plugins"]}
    _require(listed["smoke-benign"]["status"] == "disabled", "CORE_STATE_DISABLE", "禁用后状态应为 disabled")

    try:
        service.set_plugin_enabled("smoke-rejected-files", True)
    except PluginError as error:
        _require(error.code == "PLUGIN_NOT_LOADED", "CORE_STATE_REJECTED_ENABLE", f"拒绝插件启用错误码应为 PLUGIN_NOT_LOADED，实际 {error.code}")
    else:
        raise SmokeFailure("CORE_STATE_REJECTED_ENABLE", "被拒绝的插件不应能被启用")

    try:
        service.set_plugin_enabled("smoke-does-not-exist", True)
    except PluginError as error:
        _require(error.code == "PLUGIN_NOT_FOUND", "CORE_STATE_UNKNOWN", f"未知插件错误码应为 PLUGIN_NOT_FOUND，实际 {error.code}")
    else:
        raise SmokeFailure("CORE_STATE_UNKNOWN", "未知插件不应能被启用")

    service.set_global_enabled(False)
    outcome = service.run_hook("after_detect", {})
    _require(
        outcome.get("applied") is False and outcome.get("reason") == "plugins_disabled",
        "CORE_GLOBAL_KILL_SWITCH",
        "全局关闭时 run_hook 应为静默 no-op（applied=False, reason=plugins_disabled）",
    )
    service.set_global_enabled(True)
    return {"global_kill_switch": "plugins_disabled"}


def _check_benign(context: _CoreContext) -> dict:
    service = context.service
    _enable_only(service, "smoke-benign")
    outcome = service.run_hook("after_detect", {"pages": [1, 2, 3]})
    _require(outcome.get("applied") is True, "CORE_BENIGN_NOT_APPLIED", f"合法 Hook 未执行：{outcome.get('errors')}")
    _require(not outcome.get("errors"), "CORE_BENIGN_ERRORS", f"合法 Hook 出现错误：{outcome.get('errors')}")
    result = outcome["results"][0]["result"]
    _require(
        result == {"pages": 3, "schema_ref": "nm-plugin-hook/1"},
        "CORE_BENIGN_RESULT",
        f"Hook 返回不符合预期：{result!r}",
    )
    events = context.service.audit_list(100)
    _require(
        any(
            event["event_type"] == "hook_invoked"
            and event["plugin_id"] == "smoke-benign"
            and event["hook_name"] == "after_detect"
            for event in events
        ),
        "CORE_BENIGN_AUDIT",
        "审计缺少 smoke-benign 的 hook_invoked",
    )
    return {"result": result}


def _check_fs_deny(context: _CoreContext) -> dict:
    service = context.service
    _enable_only(service, "smoke-fs-read")
    outcome = service.run_hook("after_detect", {})
    _require(outcome.get("applied") is True, "CORE_FS_NOT_APPLIED", f"根外读插件 Hook 未执行：{outcome.get('errors')}")
    result = outcome["results"][0]["result"]
    _require(result.get("fs") == "BLOCKED", "CORE_FS_NOT_BLOCKED", f"根外读未被拒绝：{result!r}")
    _require("data" not in result, "CORE_FS_SECRET_LEAK", "根外读结果泄露了文件内容")
    _require(_SECRET not in json.dumps(result, ensure_ascii=False), "CORE_FS_SECRET_LEAK", "根外读结果包含秘密内容")
    return {"fs": result.get("fs"), "winerror": result.get("winerror")}


def _check_net_deny(context: _CoreContext) -> dict:
    service = context.service
    _enable_only(service, "smoke-net-none")
    outcome = service.run_hook("after_detect", {})
    _require(outcome.get("applied") is True, "CORE_NET_DENY_NOT_APPLIED", f"无权限网络插件 Hook 未执行：{outcome.get('errors')}")
    result = outcome["results"][0]["result"]
    _require(result.get("net") == "BLOCKED", "CORE_NET_DENY_FAILED", f"无权限插件网络未被拒绝：{result!r}")
    _require(result.get("kind") == "PermissionError", "CORE_NET_DENY_KIND", f"期望 PermissionError，实际 {result.get('kind')!r}")
    return {"net": result.get("net"), "kind": result.get("kind")}


def _check_net_allow(context: _CoreContext) -> dict:
    service = context.service
    _enable_only(service, "smoke-net-ok")
    outcome = service.run_hook("after_detect", {})
    _require(outcome.get("applied") is True, "CORE_NET_ALLOW_NOT_APPLIED", f"network 插件 Hook 未执行：{outcome.get('errors')}")
    result = outcome["results"][0]["result"]
    _require(
        result.get("kind") != "PermissionError",
        "CORE_NET_ALLOW_DENIED",
        f"network 插件仍被网络栈拒绝：{result!r}",
    )
    _require(
        result.get("net") in ("OK", "BLOCKED"),
        "CORE_NET_ALLOW_RESULT",
        f"network 插件返回了意外结果：{result!r}",
    )
    return {"net": result.get("net"), "kind": result.get("kind")}


def _check_timeout(context: _CoreContext) -> dict:
    short = PluginService(
        context.core.conn,
        context.plugin_root,
        app_version=_APP_VERSION,
        hook_timeout_seconds=1,
        sandbox=context.service._sandbox,
    )
    _enable_only(short, "smoke-hang")
    started = time.perf_counter()
    outcome = short.run_hook("after_detect", {})
    elapsed = time.perf_counter() - started
    _require(outcome.get("applied") is False, "CORE_TIMEOUT_APPLIED", "超时 Hook 不应算作 applied")
    errors = outcome.get("errors") or []
    _require(bool(errors), "CORE_TIMEOUT_NO_ERROR", "超时 Hook 应返回 typed error")
    _require(
        errors[0].get("code") == "PLUGIN_HOOK_TIMEOUT",
        "CORE_TIMEOUT_CODE",
        f"超时错误码应为 PLUGIN_HOOK_TIMEOUT，实际 {errors[0].get('code')}",
    )
    _require(elapsed < 15, "CORE_TIMEOUT_SLOW", f"超时清理耗时 {elapsed:.1f}s，超过 15s")
    return {"elapsed_ms": int(elapsed * 1000)}


def _check_tree_kill(context: _CoreContext) -> dict:
    manifest = parse_manifest(
        context.plugin_root / "smoke-tree-hang", app_version=_APP_VERSION
    )
    sandbox = context.service._sandbox
    sandbox.prepare_plugin(
        manifest.plugin_id,
        manifest.root,
        runner_path=context.runner,
        interpreter=context.interpreter,
    )
    payload = json.dumps({"schema_ref": "nm-plugin-hook/1"}).encode("utf-8")
    outcome = sandbox.run(
        manifest.plugin_id,
        [
            context.interpreter,
            "-I",
            str(context.runner),
            str(manifest.entry_path),
            "after_detect",
        ],
        cwd=manifest.root,
        payload=payload,
        timeout_seconds=1,
        max_output_bytes=256 * 1024,
        interpreter=context.interpreter,
        capabilities=manifest.permissions,
    )
    _require(outcome.timed_out is True, "CORE_TREE_NO_TIMEOUT", "子进程树夹具应触发超时")
    pid = _first_pid(outcome.stdout)
    _require(pid > 0, "CORE_TREE_NO_CHILD_PID", f"插件未输出孙进程 pid（stdout={outcome.stdout[:80]!r}）")
    _require(
        util.wait_pid_gone(pid, 5.0),
        "CORE_TREE_STILL_ALIVE",
        f"超时后孙进程 {pid} 仍存活，Job Object 未清理进程树",
    )
    return {"grandchild_pid": pid, "timed_out": True}


def _check_fail_closed(context: _CoreContext) -> dict:
    no_sandbox = PluginService(
        context.core.conn,
        context.plugin_root,
        app_version=_APP_VERSION,
        sandbox=None,
        allow_unsandboxed=False,
    )
    _enable_only(no_sandbox, "smoke-benign")
    outcome = no_sandbox.run_hook("after_detect", {})
    _require_no_sandbox_failure(outcome, "无沙箱实例")

    class _BrokenSandbox(AppContainerSandbox):
        def prepare_plugin(self, *args, **kwargs):  # type: ignore[override]
            raise SandboxError("cannot grant sandbox access")

    broken = PluginService(
        context.core.conn,
        context.plugin_root,
        app_version=_APP_VERSION,
        sandbox=_BrokenSandbox(),
    )
    _enable_only(broken, "smoke-benign")
    outcome = broken.run_hook("after_detect", {})
    _require_no_sandbox_failure(outcome, "沙箱授权失败实例")

    events = broken.audit_list(100)
    _require(
        any(event["event_type"] == "plugin_error" for event in events),
        "CORE_FAIL_CLOSED_AUDIT",
        "fail-closed 未写入 plugin_error 审计",
    )
    return {"sandbox_modes": ["none", "broken"]}


def _check_audit(context: _CoreContext) -> dict:
    events = context.service.audit_list(200)
    _require(bool(events), "CORE_AUDIT_EMPTY", "审计账本为空")
    types = {event["event_type"] for event in events}
    required = {"load_ok", "load_rejected", "enabled", "hook_invoked", "plugin_error"}
    missing = sorted(required - types)
    _require(not missing, "CORE_AUDIT_EVENTS_MISSING", f"缺少审计事件：{missing}")
    for event in events:
        _require(
            {"event_id", "plugin_id", "event_type", "hook_name", "detail", "occurred_at"}
            <= set(event),
            "CORE_AUDIT_SHAPE",
            "审计事件字段不完整",
        )
        _require(isinstance(event["detail"], dict), "CORE_AUDIT_DETAIL", "审计 detail 应为对象")
        text = json.dumps(event["detail"], ensure_ascii=False)
        _require(_SECRET not in text, "CORE_AUDIT_SECRET", "审计 detail 包含秘密内容")
        _require(len(text) < 2000, "CORE_AUDIT_PAYLOAD", "审计 detail 疑似写入 Hook 载荷")
    try:
        context.service.audit_list(0)
    except PluginError as error:
        _require(error.code == "PLUGIN_INVALID_REQUEST", "CORE_AUDIT_LIMIT", f"非法 limit 应被拒绝，实际 {error.code}")
    else:
        raise SmokeFailure("CORE_AUDIT_LIMIT", "audit_list(0) 应被拒绝")
    return {"events": len(events), "types": sorted(types)}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _enable_only(service: PluginService, target: str) -> None:
    service.set_global_enabled(True)
    snapshot = service.list_plugins()
    for item in snapshot["plugins"]:
        if item["status"] == "rejected":
            continue
        service.set_plugin_enabled(item["plugin_id"], item["plugin_id"] == target)


def _first_pid(stdout: bytes) -> int:
    text = stdout.decode("utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if line.isdigit():
            return int(line)
    return 0


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise SmokeFailure(code, message)


def _require_no_sandbox_failure(outcome: dict, label: str) -> None:
    errors = outcome.get("errors") or []
    _require(outcome.get("applied") is False, "CORE_FAIL_CLOSED_APPLIED", f"{label}：Hook 不应被执行")
    _require(bool(errors), "CORE_FAIL_CLOSED_NO_ERROR", f"{label}：缺少 typed error")
    _require(
        errors[0].get("code") == "PLUGIN_HOOK_UNAVAILABLE",
        "CORE_FAIL_CLOSED_CODE",
        f"{label}：错误码应为 PLUGIN_HOOK_UNAVAILABLE，实际 {errors[0].get('code')}",
    )


_ENTRIES = (
    (CHECKS[0], _check_wiring),
    (CHECKS[1], _check_discovery),
    (CHECKS[2], _check_state),
    (CHECKS[3], _check_benign),
    (CHECKS[4], _check_fs_deny),
    (CHECKS[5], _check_net_deny),
    (CHECKS[6], _check_net_allow),
    (CHECKS[7], _check_timeout),
    (CHECKS[8], _check_tree_kill),
    (CHECKS[9], _check_fail_closed),
    (CHECKS[10], _check_audit),
)
