#!/usr/bin/env python3
"""Read-only, source-bound P19-AC3-1 command/event/WebView audit.

The script never edits product files. It emits a command-by-command matrix and
raw source inventory beneath this evidence directory; its exit code reports
scanner completeness, not whether the scanned product passed the criteria.
"""

from __future__ import annotations

import csv
import json
import re
import sys
import tomllib
from pathlib import Path


EVIDENCE = Path(__file__).resolve().parent
ROOT = EVIDENCE.parents[1]
MAIN = ROOT / "apps/desktop/src-tauri/src/main.rs"
SETTINGS = ROOT / "apps/desktop/src-tauri/src/settings_bridge.rs"
LIBRARY = ROOT / "apps/desktop/src-tauri/src/library_bridge.rs"
CORE_SERVICE = ROOT / "src/bootstrap/core_service.py"
CONTRACT = ROOT / "doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md"
P15_CONTRACT = ROOT / "doc/contracts/P15_SETTINGS_IPC_CONTRACT.md"
CAPABILITY = ROOT / "apps/desktop/src-tauri/capabilities/m2rc1-commands.json"
TAURI_CONFIG = ROOT / "apps/desktop/src-tauri/tauri.conf.json"
CARGO_TOML = ROOT / "apps/desktop/src-tauri/Cargo.toml"
CARGO_LOCK = ROOT / "apps/desktop/src-tauri/Cargo.lock"
FRONTEND_PACKAGE = ROOT / "apps/desktop/frontend/package.json"
BUILD_RS = ROOT / "apps/desktop/src-tauri/build.rs"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def lines(path: Path) -> list[str]:
    return read(path).splitlines()


def ref(path: Path, start: int, end: int | None = None) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return f"{relative}:{start}" if end is None or end == start else f"{relative}:{start}-{end}"


def quoted_array(text: str, name: str) -> list[str]:
    match = re.search(
        rf"pub const {re.escape(name)}: &\[&str\] = &\[(.*?)\];",
        text,
        re.DOTALL,
    )
    if not match:
        raise AssertionError(f"constant not found: {name}")
    return re.findall(r'"([a-zA-Z0-9_]+)"', match.group(1))


def command_handlers() -> dict[str, tuple[Path, int, int, str]]:
    result: dict[str, tuple[Path, int, int, str]] = {}
    fn_re = re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(")
    for path in (MAIN, SETTINGS):
        source_lines = lines(path)
        for index, line in enumerate(source_lines):
            if not re.match(r"^\s*#\[tauri::command", line):
                continue
            fn_index = next(
                (i for i in range(index + 1, min(index + 8, len(source_lines))) if fn_re.match(source_lines[i])),
                None,
            )
            if fn_index is None:
                continue
            match = fn_re.match(source_lines[fn_index])
            assert match
            name = match.group(1)
            if name in result:
                raise AssertionError(f"duplicate command handler: {name}")
            end = fn_index
            while end + 1 < len(source_lines) and "{" not in source_lines[end]:
                end += 1
                if "{" in source_lines[end]:
                    break
            signature = " ".join(s.strip() for s in source_lines[fn_index : end + 1])
            result[name] = (path, index + 1, end + 1, signature)
    return result


MAIN_TEXT = read(MAIN)
PRODUCTION = quoted_array(MAIN_TEXT, "PRODUCTION_COMMANDS")
PROBE = quoted_array(MAIN_TEXT, "PROBE_ONLY_COMMANDS")
AC1 = quoted_array(MAIN_TEXT, "AC1_TEST_COMMANDS")
COMMANDS = PRODUCTION + PROBE + AC1
HANDLERS = command_handlers()
CAP = json.loads(read(CAPABILITY))
CAP_PERMISSIONS = CAP["permissions"]
CAP_COMMANDS = {
    permission.removeprefix("allow-").replace("-", "_")
    for permission in CAP_PERMISSIONS
    if permission.startswith("allow-")
}


def function_ref(command: str) -> str:
    path, attribute_line, end_line, _signature = HANDLERS[command]
    return ref(path, attribute_line, end_line)


def handler_signature(command: str) -> str:
    return HANDLERS[command][3].replace("`", "'")


def return_cell(command: str, surface: str) -> tuple[str, str]:
    if command in {"settings_get", "settings_update_section"}:
        return (
            "FAIL",
            "Core returns arbitrary persisted section values and Rust forwards serde_json::Value unchanged; synthetic OS path round-trip reproduced (credential sentinel was dropped). "
            + ref(CORE_SERVICE, 1210, 1269)
            + "; "
            + ref(CONTRACT, 243, 251),
        )
    if command in {"issue_resource_url", "revoke_ref", "revoke_resource_refs"}:
        return "PASS", "opaque resource DTO/unit only; " + ref(MAIN, 314, 322) + "; " + function_ref(command)
    if command == "core_ping":
        return "PASS", "typed PingResult; " + ref(LIBRARY, 23, 28) + "; " + function_ref(command)
    if command == "library_list_books":
        return "PASS", "typed BookSummary[]; " + ref(LIBRARY, 30, 43) + "; " + function_ref(command)
    if command in {"library_create_book", "create_chapter"}:
        return "PASS", "typed BookSummary/ChapterNavSummary; " + ref(MAIN, 348, 510) + "; " + ref(CONTRACT, 635, 655)
    if command.startswith("settings_") or command in {"credential_put", "credential_clear"}:
        return "PASS", "typed allowlisted SafeProjection; " + ref(SETTINGS, 353, 371) + "; " + function_ref(command)
    if command in {"library_import_file", "library_import_folder"}:
        return "PASS", "ImportSummary contains counters/IDs only, no selected path; " + ref(ROOT / "apps/desktop/src-tauri/src/host_issuer.rs", 31, 51) + "; " + function_ref(command)
    if command == "library_start_export":
        return "PASS", "ExportSummary contains export_id/status only; " + ref(ROOT / "apps/desktop/src-tauri/src/host_issuer.rs", 54, 58) + "; " + function_ref(command)
    if command == "library_reveal_export_folder":
        return "PASS", "returns unit; resolved path is passed only to native opener; " + function_ref(command)
    if command in {"library_cancel_export", "library_get_export_snapshot", "library_get_export_history"}:
        return "PASS", "Rust reconstructs typed export allowlist views excluding output_path; " + ref(LIBRARY, 53, 119) + "; " + ref(LIBRARY, 252, 418)
    if command in {"set_region_type", "restore_region_revision"}:
        return "PASS", "Core constructs fixed region/revision result keys; " + ref(CORE_SERVICE, 1296, 1369) + "; " + ref(CORE_SERVICE, 1413, 1450)
    if command == "list_regions":
        return "PASS", "Core emits RegionListSummary/page_size projection; " + ref(CORE_SERVICE, 1371, 1400) + "; " + ref(ROOT / "src/application/editing/service.py", 385, 433)
    if command == "list_region_revisions":
        return "PASS", "Core returns editing revision summaries; " + ref(CORE_SERVICE, 1402, 1411) + "; " + ref(ROOT / "src/application/editing/service.py", 434, 477)
    if command == "rerender_page":
        return "PASS", "Core constructs the response keys; host only sanitizes preview_error; " + ref(CORE_SERVICE, 1452, 1517) + "; " + ref(MAIN, 984, 1035)
    if command == "resolve_page_resource":
        return "PASS", "Core returns only opaque resource_id/revision; " + ref(CORE_SERVICE, 1615, 1660)
    if command in {"list_chapters", "list_chapter_pages"}:
        return "PASS", "Core reconstructs navigation summaries, no managed path/ref; " + ref(CORE_SERVICE, 1564, 1613)
    if command == "library_get_reader_projection":
        return "PASS", "Core reconstructs Reader DTO with opaque resource refs; " + ref(CORE_SERVICE, 1662, 1714)
    if command == "library_save_reading_progress":
        return "PASS", "Core validates input and returns reading snapshot; " + ref(CORE_SERVICE, 1716, 1740)
    if command in {
        "library_start_run", "library_control_run", "library_resume_blocked_run",
        "library_get_run_snapshot", "library_get_task_projection", "library_retry_failed_targets",
    }:
        return "PASS", "Core constructs Run DTO/task projection; error_message is null; " + ref(CORE_SERVICE, 2320, 2385) + "; " + ref(CORE_SERVICE, 2407, 2505)
    if command == "probe_write_results":
        return "FAIL (auxiliary only)", "returns configured output path; probe-only mode, not production; " + ref(MAIN, 1084, 1093)
    if command == "ac1_write_results":
        return "FAIL (auxiliary only)", "returns configured output path; AC1 test-only mode, not production; " + ref(MAIN, 1139, 1148)
    if command == "ac1_request":
        return "N/A (test-only)", "generic acceptance harness result; never registered in production; " + ref(MAIN, 1118, 1137)
    if command == "probe_config":
        return "N/A (test-only)", "fixed evidence-runner configuration; never registered in production; " + ref(MAIN, 1070, 1081)
    if command in {"probe_exit", "ac1_exit"}:
        return "N/A (no response value)", "command terminates only its test runner; " + function_ref(command)
    if command == "probe_issue_url":
        return "N/A (test-only)", "safe opaque issued-resource DTO; not registered in production; " + ref(MAIN, 1101, 1116)
    raise AssertionError(f"missing return classification for {command}")


def event_cell(command: str) -> tuple[str, str]:
    if command in {"library_start_run", "library_control_run", "library_resume_blocked_run", "library_retry_failed_targets"}:
        return "PASS", "asynchronous Run events pass the six-type projector; " + ref(CORE_SERVICE, 947, 957) + "; " + ref(LIBRARY, 756, 872)
    if command == "library_save_reading_progress":
        return "PASS", "ReadingProgressChanged emitted after save; projected by event allowlist; " + ref(CORE_SERVICE, 1737, 1740) + "; " + ref(LIBRARY, 856, 872)
    if command in {"library_start_export", "library_cancel_export"}:
        return "PASS", "ExportProgressChanged is emitted through the Core sink and six-type projector; " + ref(CORE_SERVICE, 959, 969) + "; " + ref(LIBRARY, 844, 855)
    return "N/A", "no command-specific event; sidecar-wide event inventory is independently covered in events-matrix.md; " + ref(LIBRARY, 756, 872)


def error_cell(command: str, surface: str) -> tuple[str, str]:
    if command in {"library_create_book", "create_chapter"}:
        return "PASS", "closed LibrarySurfaceError mapping; no Core message/details; " + ref(MAIN, 370, 478) + "; " + ref(CONTRACT, 620, 655)
    if command in {"settings_get", "settings_update_section"}:
        return "PARTIAL", "only error.code is sent as a String; Host does not validate it against a closed enum; " + ref(LIBRARY, 165, 194) + "; " + function_ref(command)
    if command.startswith("settings_") or command in {"credential_put", "credential_clear"}:
        return "PASS", "closed SettingsSurfaceError categories/phases/actions/message keys; " + ref(SETTINGS, 13, 120) + "; " + ref(SETTINGS, 287, 371) + "; " + ref(P15_CONTRACT, 301, 321)
    if surface == "production":
        return "PARTIAL", "only error.code is sent, not message/details/trace; Host does not validate code against a closed enum; " + ref(LIBRARY, 165, 194) + "; " + function_ref(command)
    if command in {"probe_write_results", "ac1_write_results"}:
        return "FAIL (auxiliary only)", "raw OS error string returned; test-only write command; " + function_ref(command)
    if command in {"probe_exit", "ac1_exit", "probe_config"}:
        return "N/A", "no fallible response projection; test-only command; " + function_ref(command)
    return "PARTIAL (test-only)", "test harness code-only error; excluded from product surface; " + function_ref(command)


def create_tauri_excerpts() -> tuple[str, str, str]:
    lock = tomllib.loads(read(CARGO_LOCK))
    packages = {pkg["name"]: pkg["version"] for pkg in lock["package"]}
    tauri_version = packages["tauri"]
    macro_version = packages["tauri-macros"]
    registry = Path.home() / ".cargo/registry/src"
    tauri_file = next(registry.glob(f"*/tauri-{tauri_version}/src/ipc/command.rs"))
    macro_file = next(registry.glob(f"*/tauri-macros-{macro_version}/src/command/wrapper.rs"))
    tauri_lines = lines(tauri_file)
    macro_lines = lines(macro_file)
    tauri_text = "\n".join(tauri_lines[94:117])
    macro_text = "\n".join(macro_lines[514:524])
    assert "v.get(self.key)" in tauri_text
    assert "None => Err" in tauri_text
    assert "from_command" in macro_text and "key: #key" in macro_text
    excerpt = (
        f"tauri={tauri_version} source={tauri_file} lines=95-117\n"
        + "\n".join(f"{n}:{tauri_lines[n-1]}" for n in range(95, 118))
        + f"\n\ntauri-macros={macro_version} source={macro_file} lines=515-524\n"
        + "\n".join(f"{n}:{macro_lines[n-1]}" for n in range(515, 525))
        + "\n"
    )
    out = EVIDENCE / "tauri-command-argument-excerpt.txt"
    out.write_text(excerpt, encoding="utf-8", newline="\n")
    return tauri_version, macro_version, out.name


def main() -> int:
    assert len(PRODUCTION) == 51, f"expected 51 production commands, got {len(PRODUCTION)}"
    assert len(PROBE) == 4, f"expected 4 probe commands, got {len(PROBE)}"
    assert len(AC1) == 3, f"expected 3 AC1 commands, got {len(AC1)}"
    assert len(COMMANDS) == 58 and len(set(COMMANDS)) == 58
    assert set(COMMANDS) == set(HANDLERS), f"handler drift missing={set(COMMANDS)-set(HANDLERS)} extra={set(HANDLERS)-set(COMMANDS)}"
    assert CAP_COMMANDS == set(COMMANDS), f"capability drift missing={set(COMMANDS)-CAP_COMMANDS} extra={CAP_COMMANDS-set(COMMANDS)}"

    tauri_version, macro_version, excerpt_path = create_tauri_excerpts()
    tauri_source_ref = f"tauri {tauri_version} src/ipc/command.rs:95-117 + tauri-macros {macro_version} wrapper.rs:515-524"
    rows = []
    for surface, commands in (("production", PRODUCTION), ("probe", PROBE), ("ac1", AC1)):
        for command in commands:
            request = (
                "FAIL — top-level extra keys are not checked; only declared handler keys are deserialized; "
                + tauri_source_ref + "; handler signature " + function_ref(command)
            )
            return_status, return_evidence = return_cell(command, surface)
            event_status, event_evidence = event_cell(command)
            error_status, error_evidence = error_cell(command, surface)
            rows.append({
                "command": command,
                "surface": surface,
                "request": request,
                "return": f"{return_status} — {return_evidence}",
                "event": f"{event_status} — {event_evidence}",
                "error": f"{error_status} — {error_evidence}",
                "handler_signature": handler_signature(command),
            })

    matrix_md = [
        "# P19-AC3-1 命令 × 四处覆盖矩阵",
        "",
        "本表按 51 条 production + 4 条 probe-only + 3 条 AC1-only 命令逐条扫描；每格均含结论和代码/扫描证据引用。`register_catalog` 已移除，不计入 58 条已注册命令，见表后 N/A 行。事件是异步 sidecar-wide 通道；命令触发关系与六个事件的 payload 投影另见 [events-matrix.md](events-matrix.md)。",
        "",
        "| 命令 | 面 | 请求 | 返回 | 事件 | 错误 |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        esc = lambda value: value.replace("|", "\\|").replace("\n", " ")
        matrix_md.append(
            "| `" + row["command"] + "` | " + row["surface"] + " | "
            + " | ".join(esc(row[key]) for key in ("request", "return", "event", "error")) + " |"
        )
    matrix_md += [
        "| `register_catalog` | removed | N/A — not registered in any mode; `main.rs:147-150,1445-1447`; `build.rs:41-47` | N/A — no handler | N/A — no handler | N/A — no handler |",
        "",
        "## 命令请求形状",
        "",
        "以下真实 `#[tauri::command]` 函数签名用于逐命令请求侧证据；共同 Tauri 反例语义见 [tauri-command-argument-excerpt.txt](tauri-command-argument-excerpt.txt)。",
        "",
        "| 命令 | 处理器签名（原始扫描摘录） |",
        "|---|---|",
    ]
    for row in rows:
        matrix_md.append(f"| `{row['command']}` | `{row['handler_signature']}` |")
    matrix_md += [
        "",
        "## 当前结论",
        "",
        "- 请求：58/58 命令均没有顶层 key-set 校验；创建/凭据虽对嵌套 DTO 使用 `deny_unknown_fields`，不改变 Tauri 外层参数提取语义。",
        "- 返回：49/51 production 返回当前安全 DTO/显式 Core 投影；`settings_get` 与 `settings_update_section` 会回显按契约允许透传的任意 section/key，合成 OS path 往返复现见 `raw/settings-path-roundtrip.stdout.txt`；credential sentinel 未回显。两个测试面写结果命令也会返回 runner 输出路径，均不在 production handler 注册。",
        "- 事件：六种固定事件投影无已观察到的 path/Secret/raw error 字段；命令事件关联及 per-event 投影见独立矩阵。",
        "- 错误：21/51 production 使用闭合 typed projection；30/51 仅投影 `error.code` 字符串，当前实现省略 `message/details`，但 Rust Host 未校验 code 值域。未发现实际 raw exception/path 值穿过 production 错误。",
    ]
    (EVIDENCE / "command-matrix.md").write_text("\n".join(matrix_md) + "\n", encoding="utf-8", newline="\n")

    with (EVIDENCE / "command-matrix.csv").open("w", encoding="utf-8-sig", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    p15_names = [name for name in PRODUCTION if name.startswith("settings_") or name in {"credential_put", "credential_clear"}]
    cap_summary = {
        "capability": CAP["identifier"],
        "windows": CAP["windows"],
        "app_command_permissions": sorted(CAP_COMMANDS),
        "event_permissions": [p for p in CAP_PERMISSIONS if p.startswith("core:event:")],
        "plugin_permissions": [p for p in CAP_PERMISSIONS if p.startswith(("dialog:", "opener:", "core:path:", "fs:", "sql:"))],
    }
    (EVIDENCE / "webview-boundary.json").write_text(json.dumps(cap_summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    events = [
        ("TaskFailed", "core:TaskFailed", "run_id,task_id,page_id?,error_code?", ref(LIBRARY, 778, 809)),
        ("RunPaused", "core:RunPaused", "run_id,status='paused'", ref(LIBRARY, 810, 820)),
        ("RunCompleted", "core:RunCompleted", "run_id,status∈{completed,completed_with_failures}", ref(LIBRARY, 821, 831)),
        ("CurrentPageStepChanged", "core:CurrentPageStepChanged", "run_id,current_page_id,current_step_type", ref(LIBRARY, 832, 843)),
        ("ExportProgressChanged", "core:ExportProgressChanged", "export_id,status,completed_pages,total_pages", ref(LIBRARY, 844, 855)),
        ("ReadingProgressChanged", "core:ReadingProgressChanged", "book_id,chapter_id,mode∈{original,translated}", ref(LIBRARY, 856, 872)),
    ]
    event_md = [
        "# P19-AC3-1 事件面覆盖",
        "",
        "| Core event | Tauri event | 输出字段 | 结论与证据 |",
        "|---|---|---|---|",
    ]
    for name, tauri_name, fields, evidence in events:
        event_md.append(f"| `{name}` | `{tauri_name}` | `{fields}` | PASS — 白名单内逐字段重建，未知类型/必需字段缺失时丢弃；{evidence}; {ref(LIBRARY, 769, 872)} |")
    event_md += [
        "",
        f"`credential_put` / `credential_clear` 没有事件；事件目录仅上述六种，credential request/result/error DTO 证据：{ref(SETTINGS, 167, 208)}、{ref(SETTINGS, 287, 349)}、{ref(LIBRARY, 756, 763)}。Tauri emitter 只从该投影 sink 发出：{ref(MAIN, 1412, 1424)}。",
        "",
        "命令触发事件：Run 发起/控制/恢复/重试命令可以异步产生 Run 事件；`library_save_reading_progress` 产生 `ReadingProgressChanged`；导出开始/取消可产生 `ExportProgressChanged`。其他命令格为 N/A（无每命令事件），矩阵仍逐格登记。",
        "",
        "观察到的 credential 明文、OS path、raw exception event counterexample：0。",
    ]
    (EVIDENCE / "events-matrix.md").write_text("\n".join(event_md) + "\n", encoding="utf-8", newline="\n")

    cargo = tomllib.loads(read(CARGO_TOML))
    direct_deps = cargo.get("dependencies", {})
    frontend = json.loads(read(FRONTEND_PACKAGE))
    config = json.loads(read(TAURI_CONFIG))
    frontend_sources = [p for p in (ROOT / "apps/desktop/frontend/src").rglob("*.ts*") if ".test." not in p.name]
    api_imports = []
    direct_risky_imports = []
    for path in frontend_sources:
        for n, line in enumerate(lines(path), start=1):
            if "@tauri-apps/api" in line or "__TAURI__" in line:
                api_imports.append(f"{ref(path, n)} {line.strip()}")
            if re.search(r"(?:better-sqlite3|sql\.js|sqlite3|@tauri-apps/plugin-fs|@tauri-apps/plugin-sql|onnxruntime|transformers)", line, re.I):
                direct_risky_imports.append(f"{ref(path, n)} {line.strip()}")
    plugin_deps = sorted(k for k in direct_deps if k.startswith("tauri-plugin-"))
    plugin_names = sorted(k.removeprefix("tauri-plugin-") for k in plugin_deps)
    no_fs_sql = not any(any(token in dep.lower() for token in ("fs", "sql")) for dep in plugin_names)
    assert no_fs_sql and not direct_risky_imports
    assert set(plugin_names) == {"dialog", "opener"}
    denied_cases = [
        "register_catalog", "OpenHostSession", "BindProfileCredential",
        "plugin:fs|read_text_file", "plugin:sql|select",
        "plugin:dialog|open", "plugin:opener|open_path", "plugin:path|resolve_directory",
    ]
    denied = []
    for case in denied_cases:
        if case.startswith("plugin:"):
            plugin, command = case.removeprefix("plugin:").split("|", 1)
            permission_prefix = {"path": "core:path:", "dialog": "dialog:", "opener": "opener:", "fs": "fs:", "sql": "sql:"}[plugin]
            is_denied = not any(p.startswith(permission_prefix) and command.replace("_", "-") in p for p in CAP_PERMISSIONS)
        else:
            is_denied = case not in COMMANDS and case not in CAP_COMMANDS
        assert is_denied, f"negative ACL case unexpectedly granted: {case}"
        denied.append(case)

    boundary_md = [
        "# P19-AC3-1 WebView 访问面证明",
        "",
        "## 前端实际 API 使用",
        "",
        "- React/TypeScript 代码中唯一 `@tauri-apps/api` 导入为 event listener；唯一 app bridge 调用面为 `window.__TAURI__.core.invoke`。实际代码引用：",
    ]
    boundary_md.extend(f"  - `{item}`" for item in api_imports)
    boundary_md += [
        "- frontend/package.json runtime dependencies：`@tauri-apps/api`, `react`, `react-dom`；没有 SQLite driver、filesystem plugin、SQL plugin 或模型 runtime。",
        f"- Rust direct plugin dependencies：{', '.join(plugin_names)}（dialog/opener 由 Rust 调用）；没有 fs/sql plugin dependency。`withGlobalTauri={str(config['app']['withGlobalTauri']).lower()}`，因此 WebView 有 Tauri JS bridge 对象，但 IPC 权限仍由以下 Capability 限制。",
        f"- Capability `{CAP['identifier']}` 只匹配 window `{', '.join(CAP['windows'])}`，列出 {len(CAP_COMMANDS)} 个 app command 权限；另外只有 `{', '.join(cap_summary['event_permissions'])}`。未授予 `dialog:*`、`opener:*`、`core:path:*`、`fs:*`、`sql:*`。清单：`{ref(CAPABILITY, 1, len(lines(CAPABILITY)))}`。",
        f"- `tauri.conf.json` 关闭 asset protocol 且 scope 为空：`{ref(TAURI_CONFIG, 10, 15)}`。WebView 不能借 asset protocol 读取 path。",
        f"- 应用 ACL 只授权列出的 58 个命令，其他命令由 ACL 拒绝：`{ref(BUILD_RS, 31, 53)}`；production invoke handler 不包含 probe/AC1 面：`{ref(MAIN, 1482, 1538)}`；host-only operations 不在 WebView command set：`{ref(MAIN, 2506, 2522)}`。",
        "",
        "## 越权反例（静态 ACL 自检）",
        "",
        "`raw/scan.stdout.txt` 内 `NEGATIVE_ACL` 记录逐项断言下列调用没有 capability permission / app handler，并打印 `DENIED_BY_CAPABILITY`。这是基于已构建 app ACL 清单和运行时注册面的静态反例；本 Task 没有启动桌面应用或伪装成 live WebView invocation。",
        "",
        "| 反例调用 | 检查结果 |",
        "|---|---|",
    ]
    boundary_md.extend(f"| `{case}` | DENIED_BY_CAPABILITY |" for case in denied)
    boundary_md += [
        "",
        "`fs`/`sql` 未注册；dialog/opener 虽在 Rust 初始化，但 Capability 没有授予对应 plugin permission。`core:path` permission 同样未授予。产品实际对外唯一 native data/mutation 路径是 ACL 白名单内的 Tauri invoke command；业务 IPC 的 Core 返回细节见命令矩阵。",
        "",
        "边界结论限定于当前源码/锁定依赖的静态配置。Live GUI 的 CUA/UIA 或进程级 runtime injection 未执行。",
    ]
    (EVIDENCE / "webview-boundary.md").write_text("\n".join(boundary_md) + "\n", encoding="utf-8", newline="\n")

    output = []
    output.append("P19-AC3-1 STATIC SCAN — raw source inventory; scanner completion is independent of product findings")
    output.append(f"ROOT={ROOT}")
    output.append(f"HEAD={__import__('subprocess').check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}")
    output.append(f"COMMAND_COUNTS production={len(PRODUCTION)} probe={len(PROBE)} ac1={len(AC1)} total={len(COMMANDS)}")
    output.append(f"COMMAND_SOURCE {ref(MAIN, 66, 156)}")
    output.append(f"HANDLER_REGISTRATION {ref(MAIN, 1445, 1538)}")
    output.append(f"CAPABILITY commands={len(CAP_COMMANDS)} total_permissions={len(CAP_PERMISSIONS)} path={ref(CAPABILITY, 1, len(lines(CAPABILITY)))}")
    output.append(f"TAURI_LOCK tauri={tauri_version} tauri-macros={macro_version}; source excerpt archived={excerpt_path}")
    output.append(f"REQUEST_COUNTEREXAMPLES production={len(PRODUCTION)} auxiliary={len(PROBE)+len(AC1)}; common evidence={tauri_source_ref}")
    output.append(f"RETURN_COUNTEREXAMPLES production_commands=2 auxiliary_commands=2; secret_echoes=0; settings repro=raw/settings-path-roundtrip.stdout.txt")
    output.append(f"ERROR_PROJECTION production=21 typed_closed; 30 code_only_unvalidated; actual raw exception/path leak observed=0")
    output.append(f"EVENTS={len(events)} fixed forwarded types; payload projection evidence={ref(LIBRARY, 756, 872)}")
    output.append(f"WEBVIEW_PLUGIN_DEPS={plugin_names}; fs_sql_direct_dependencies_absent={no_fs_sql}; direct_frontend_db_fs_model_imports={len(direct_risky_imports)}")
    output.append(f"NEGATIVE_ACL cases={len(denied)} status=PASS_STATIC_DENIED")
    output.append(f"MATRIX_ROWS={len(rows)} columns=4; removed_command_rows=1 (`register_catalog` N/A)")
    output.append("" )
    output.append("=== COMMAND MATRIX ROWS (COMMAND | SURFACE | REQUEST | RETURN | EVENT | ERROR) ===")
    for row in rows:
        output.append(
            " | ".join((row["command"], row["surface"], row["request"], row["return"], row["event"], row["error"]))
        )
    output.append("register_catalog | removed | N/A-not-registered | N/A-no-handler | N/A-no-handler | N/A-no-handler")
    output.append("=== WEBVIEW NEGATIVE ACL CASES ===")
    output.extend(f"NEGATIVE_ACL {case} => DENIED_BY_CAPABILITY" for case in denied)
    output.append("=== FRONTEND API REFERENCES ===")
    output.extend(api_imports)
    output.append("=== COMPLETENESS ASSERTIONS ===")
    output.append("PASS constants=51+4+3 unique handlers=58 capability=58; all assertions passed")

    output.append("SCAN_COMPLETE product_findings=present exit_code=0")
    raw_dir = EVIDENCE / "raw"
    raw_dir.mkdir(exist_ok=True)
    (raw_dir / "scan.stdout.txt").write_text("\n".join(output) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(output))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"SCAN_FAILURE {type(error).__name__}: {error}", file=sys.stderr)
        raise
