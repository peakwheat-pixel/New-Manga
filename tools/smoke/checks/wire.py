"""Layer 2: the real Core stdio wire that Tauri/React consume.

This layer starts a *real* ``python -m bootstrap.core_service`` subprocess and
drives the exact JSON-lines envelopes the desktop shell round-trips. It is the
stable seam for future UI/UX work: it never inspects the DOM or pixels.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import queue
import subprocess
import sys
import time
from pathlib import Path
import threading

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
    CheckSpec("WIRE-PING", "真实 Core 子进程启动并响应 core.ping"),
    CheckSpec("WIRE-PLUGINS-LIST", "plugins.list 默认关闭、拒绝语义与投影字段"),
    CheckSpec("WIRE-PLUGINS-STATE", "plugins.set_enabled / set_plugin_enabled 状态往返"),
    CheckSpec("WIRE-PLUGINS-ERRORS", "类型化错误信封：拒绝/未知/畸形请求"),
    CheckSpec("WIRE-PLUGINS-AUDIT", "plugins.audit_list 账本形状与事件"),
    CheckSpec("WIRE-SHUTDOWN", "core.shutdown 正常退出且无残留进程"),
)

_PROTOCOL = "new-manga.core"
_VERSION = {"major": 2, "minor": 3}


class _CoreProcess:
    """Line-buffered JSON-lines client with bounded waits and stderr capture."""

    def __init__(self, process: subprocess.Popen) -> None:
        self.process = process
        self._lines: queue.Queue[str | None] = queue.Queue()
        self._stderr: list[str] = []
        self._sequence = 0
        threading.Thread(target=self._pump_stdout, daemon=True).start()
        threading.Thread(target=self._pump_stderr, daemon=True).start()

    def _pump_stdout(self) -> None:
        assert self.process.stdout is not None
        try:
            for line in self.process.stdout:
                self._lines.put(line)
        except Exception:  # noqa: BLE001 - process teardown
            pass
        finally:
            self._lines.put(None)

    def _pump_stderr(self) -> None:
        assert self.process.stderr is not None
        try:
            for line in self.process.stderr:
                self._stderr.append(line)
                if len(self._stderr) > 400:
                    self._stderr = self._stderr[-400:]
        except Exception:  # noqa: BLE001
            pass

    def stderr_tail(self) -> str:
        return util.tail("".join(self._stderr), 1200)

    def request(self, command: str, payload: dict | list | None = None, timeout: float = 60) -> dict:
        self._sequence += 1
        request_id = f"smoke-{self._sequence}"
        request = {
            "protocol": _PROTOCOL,
            "version": dict(_VERSION),
            "request_id": request_id,
            "command": command,
            "payload": {} if payload is None else payload,
        }
        assert self.process.stdin is not None
        try:
            self.process.stdin.write(json.dumps(request, ensure_ascii=False) + "\n")
            self.process.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            raise SmokeFailure(
                "WIRE_PROCESS_EXITED",
                f"Core 子进程已退出，无法发送 {command}（{error}）；stderr={self.stderr_tail()}",
            ) from None
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise SmokeFailure(
                    "WIRE_TIMEOUT",
                    f"{command} 在 {timeout}s 内没有响应；stderr={self.stderr_tail()}",
                )
            try:
                line = self._lines.get(timeout=remaining)
            except queue.Empty:
                continue
            if line is None:
                raise SmokeFailure(
                    "WIRE_PROCESS_EXITED",
                    f"Core 子进程在 {command} 响应前退出；stderr={self.stderr_tail()}",
                )
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(response, dict):
                continue
            if response.get("request_id") != request_id:
                raise SmokeFailure(
                    "WIRE_REQUEST_ID",
                    f"{command} 响应的 request_id 不匹配：{response.get('request_id')!r}",
                )
            return response

    def wait_exit(self, timeout: float = 10) -> int | None:
        try:
            return self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            return None

    def terminate(self) -> None:
        if self.process.poll() is None:
            try:
                self.process.terminate()
            except OSError:
                pass
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                self.process.kill()
            except OSError:
                pass
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass


@dataclass
class _WireContext:
    client: _CoreProcess
    data_root: Path


def run(options: RunOptions) -> list[CheckResult]:
    try:
        context = _prepare(options)
    except Exception as error:  # noqa: BLE001 - setup failure is BLOCKED, not a crash
        return all_blocked(
            CHECKS,
            "WIRE-SETUP-FAILED",
            f"Wire 层初始化失败：{type(error).__name__}: {error}",
        )
    try:
        return run_checks(_ENTRIES, context)
    finally:
        _cleanup(context)


# ---------------------------------------------------------------------------
# setup / cleanup
# ---------------------------------------------------------------------------
def _write_plugin(root: Path, plugin_id: str, permissions: tuple[str, ...]) -> None:
    directory = root / plugin_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "plugin.py").write_text(
        "def after_detect(payload):\n    return {'ok': True}\n", encoding="utf-8"
    )
    (directory / "manifest.json").write_text(
        json.dumps(
            {
                "id": plugin_id,
                "name": plugin_id,
                "version": "1.0.0",
                "entry": "plugin.py",
                "hooks": ["after_detect"],
                "permissions": list(permissions),
                "description": "TOOL-SOFTWARE-SMOKE-1 wire fixture",
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _prepare(options: RunOptions) -> _WireContext:
    data_root = options.run_root / "wire-data"
    plugin_root = data_root / "plugins"
    plugin_root.mkdir(parents=True, exist_ok=True)
    _write_plugin(plugin_root, "smoke-wire-ok", ())
    _write_plugin(plugin_root, "smoke-wire-bad", ("files_read",))
    env = util.child_environment(data_root=data_root)
    process = subprocess.Popen(
        [sys.executable, "-m", "bootstrap.core_service"],
        cwd=str(util.REPO_ROOT),
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )
    return _WireContext(client=_CoreProcess(process), data_root=data_root)


def _cleanup(context: _WireContext) -> None:
    if context.client.process.poll() is None:
        try:
            context.client.request("core.shutdown", {}, timeout=10)
        except Exception:  # noqa: BLE001 - best effort during teardown
            pass
    context.client.terminate()


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------
def _check_ping(context: _WireContext) -> dict:
    response = context.client.request("core.ping", {})
    _require_envelope(response)
    result = response.get("result")
    _require(isinstance(result, dict), "WIRE_PING_SHAPE", "core.ping 结果不是对象")
    _require(result.get("status") == "ready", "WIRE_PING_STATUS", f"Core 未就绪：{result!r}")
    version = result.get("protocol_version") or {}
    _require(
        version.get("major") == 2 and isinstance(version.get("minor"), int),
        "WIRE_PING_VERSION",
        f"协议版本不符合预期：{version!r}",
    )
    capabilities = result.get("capabilities") or []
    _require(
        "library.list_books" in capabilities,
        "WIRE_PING_CAPABILITY",
        f"capabilities 缺少 library.list_books：{capabilities!r}",
    )
    return {"status": result.get("status"), "protocol_version": version}


def _check_list(context: _WireContext) -> dict:
    response = context.client.request("plugins.list", {})
    result = _result(response)
    _require(result.get("global_enabled") is False, "WIRE_LIST_GLOBAL", "plugins.list 全局开关默认应为关闭")
    _require("plugin_root" not in result, "WIRE_LIST_ROOT", "plugins.list 不应投影绝对插件根路径")
    by_id = {item["plugin_id"]: item for item in result.get("plugins") or []}
    ok = by_id.get("smoke-wire-ok")
    bad = by_id.get("smoke-wire-bad")
    _require(ok is not None, "WIRE_LIST_MISSING", "plugins.list 缺少 smoke-wire-ok")
    _require(bad is not None, "WIRE_LIST_MISSING", "plugins.list 缺少 smoke-wire-bad")
    _require(ok.get("status") == "disabled", "WIRE_LIST_STATUS", f"合法插件状态应为 disabled：{ok!r}")
    _require(ok.get("permissions") == [], "WIRE_LIST_PERMISSIONS", f"无权限插件权限数据应为 []：{ok!r}")
    _require(bad.get("status") == "rejected", "WIRE_LIST_REJECTED", f"files_read 插件应被拒绝：{bad!r}")
    _require(
        str(bad.get("reason") or "").startswith("PLUGIN_PERMISSIONS_UNSUPPORTED"),
        "WIRE_LIST_REASON",
        f"拒绝原因不符合预期：{bad.get('reason')!r}",
    )
    return {"plugins": len(by_id)}


def _check_state(context: _WireContext) -> dict:
    on = _result(context.client.request("plugins.set_enabled", {"enabled": True}))
    _require(on.get("global_enabled") is True, "WIRE_STATE_GLOBAL", f"set_enabled 结果不符合预期：{on!r}")
    enabled = _result(
        context.client.request(
            "plugins.set_plugin_enabled", {"plugin_id": "smoke-wire-ok", "enabled": True}
        )
    )
    _require(
        enabled == {"plugin_id": "smoke-wire-ok", "enabled": True},
        "WIRE_STATE_PLUGIN",
        f"set_plugin_enabled 结果不符合预期：{enabled!r}",
    )
    listed = _result(context.client.request("plugins.list", {}))
    _require(listed.get("global_enabled") is True, "WIRE_STATE_LIST_GLOBAL", "列表未反映全局启用")
    by_id = {item["plugin_id"]: item for item in listed.get("plugins") or []}
    _require(by_id["smoke-wire-ok"]["status"] == "enabled", "WIRE_STATE_LIST_PLUGIN", "列表未反映插件启用")
    off = _result(
        context.client.request(
            "plugins.set_plugin_enabled", {"plugin_id": "smoke-wire-ok", "enabled": False}
        )
    )
    _require(off.get("enabled") is False, "WIRE_STATE_PLUGIN_OFF", f"插件禁用结果不符合预期：{off!r}")
    return {"global": True, "plugin": "smoke-wire-ok"}


def _check_errors(context: _WireContext) -> dict:
    rejected = context.client.request(
        "plugins.set_plugin_enabled", {"plugin_id": "smoke-wire-bad", "enabled": True}
    )
    _require_error(rejected, "PLUGIN_NOT_LOADED", "validation")
    missing = context.client.request(
        "plugins.set_plugin_enabled", {"plugin_id": "smoke-wire-absent", "enabled": True}
    )
    _require_error(missing, "PLUGIN_NOT_FOUND", "not_found")
    malformed = context.client.request("plugins.list", [1, 2, 3])
    _require_error(malformed, "PLUGIN_INVALID_REQUEST", "validation")
    bad_limit = context.client.request("plugins.audit_list", {"limit": 0})
    _require_error(bad_limit, "PLUGIN_INVALID_REQUEST", "validation")
    return {"codes": ["PLUGIN_NOT_LOADED", "PLUGIN_NOT_FOUND", "PLUGIN_INVALID_REQUEST"]}


def _check_audit(context: _WireContext) -> dict:
    events = _result(context.client.request("plugins.audit_list", {"limit": 50}))
    _require(isinstance(events, list) and bool(events), "WIRE_AUDIT_SHAPE", "audit_list 结果应为非空数组")
    types = {event.get("event_type") for event in events}
    required = {"load_ok", "load_rejected", "enabled"}
    missing = sorted(required - types)
    _require(not missing, "WIRE_AUDIT_EVENTS", f"审计缺少事件：{missing}")
    for event in events:
        _require(
            {"event_id", "plugin_id", "event_type", "hook_name", "detail", "occurred_at"}
            <= set(event),
            "WIRE_AUDIT_FIELDS",
            "审计事件字段不完整",
        )
        _require(isinstance(event.get("detail"), dict), "WIRE_AUDIT_DETAIL", "审计 detail 应为对象")
        _require(isinstance(event.get("occurred_at"), str), "WIRE_AUDIT_TIME", "审计 occurred_at 应为字符串")
    return {"events": len(events), "types": sorted(types)}


def _check_shutdown(context: _WireContext) -> dict:
    response = context.client.request("core.shutdown", {})
    result = _result(response)
    _require(result == {"status": "stopped"}, "WIRE_SHUTDOWN_RESULT", f"shutdown 结果不符合预期：{result!r}")
    exit_code = context.client.wait_exit(10)
    _require(exit_code is not None, "WIRE_SHUTDOWN_HANG", "core.shutdown 后进程未在 10s 内退出")
    _require(exit_code == 0, "WIRE_SHUTDOWN_EXIT", f"core.shutdown 退出码应为 0，实际 {exit_code}")
    return {"exit_code": exit_code}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _require_envelope(response: dict) -> None:
    _require(
        response.get("protocol") == _PROTOCOL,
        "WIRE_ENVELOPE_PROTOCOL",
        f"响应 protocol 不符合预期：{response.get('protocol')!r}",
    )
    version = response.get("version") or {}
    _require(version.get("major") == 2, "WIRE_ENVELOPE_VERSION", f"响应版本不符合预期：{version!r}")
    _require("result" in response and "error" in response, "WIRE_ENVELOPE_SHAPE", "响应缺少 result/error 字段")


def _result(response: dict) -> object:
    _require_envelope(response)
    error = response.get("error")
    _require(error is None, "WIRE_UNEXPECTED_ERROR", f"命令返回错误：{error!r}")
    return response.get("result")


def _require_error(response: dict, code: str, category: str) -> None:
    _require_envelope(response)
    error = response.get("error")
    _require(isinstance(error, dict), "WIRE_ERROR_MISSING", f"期望 {code} 错误，实际 success")
    _require(error.get("code") == code, "WIRE_ERROR_CODE", f"错误码应为 {code}，实际 {error.get('code')!r}")
    _require(
        error.get("category") == category,
        "WIRE_ERROR_CATEGORY",
        f"错误分类应为 {category}，实际 {error.get('category')!r}",
    )
    _require(error.get("retryable") is False, "WIRE_ERROR_RETRYABLE", "该错误应为不可重试")


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise SmokeFailure(code, message)


_ENTRIES = (
    (CHECKS[0], _check_ping),
    (CHECKS[1], _check_list),
    (CHECKS[2], _check_state),
    (CHECKS[3], _check_errors),
    (CHECKS[4], _check_audit),
    (CHECKS[5], _check_shutdown),
)
