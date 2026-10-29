"""V11R-A-3: build doc/contracts/V11R_COMMAND_CONTRACT_V1.md from extracted facts.

Input:  verification/V11R-A-3/contract-facts.json (extract_contract_facts.py)
Output: doc/contracts/V11R_COMMAND_CONTRACT_V1.md

The document is generated (not hand-maintained) so every row keeps a mechanical link to the
registry / dispatcher / Core source line numbers and to one real sample. Narrative sections
(envelope, error families, minor compatibility, C067-C076 PENDING) are template text in this
script and must be reviewed when the contract changes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[3]
APP = WORKTREE / "apps" / "desktop-avalonia"
FACTS = WORKTREE / "verification" / "V11R-A-3" / "contract-facts.json"
OUT = WORKTREE / "doc" / "contracts" / "V11R_COMMAND_CONTRACT_V1.md"
DISPATCHER = APP / "src" / "NewManga.CoreClient" / "Commands" / "HostCommandDispatcher.cs"
CORE = WORKTREE / "src" / "bootstrap" / "core_service.py"

DOMAIN_ORDER = ["Settings", "Library", "Region", "Reader", "Resource", "Workbench"]

# Core dispatch refs that the generic scanner cannot resolve (constants/handlers elsewhere).
CORE_REF_OVERRIDES = {
    "C036": ("src/bootstrap/core_service.py:3531（handle_create_book 调用；校验 :921-941）", None),
    "C037": ("src/bootstrap/core_service.py:3533（handle_create_chapter 调用；校验 :921-941）", "handle_create_chapter"),
    "C040": ("src/bootstrap/core_service.py:3577-3578（handle_permanently_delete_book）", None),
    "C041": ("src/bootstrap/core_service.py:3579-3580（handle_permanently_delete_books）", None),
    "C056": ("src/bootstrap/core_service.py:3256（_dispatch_run_command）; :3273-3300（StartRun 分支）", None),
    "C057": ("src/bootstrap/core_service.py:3256; :3301-3321（ControlRun 分支）", None),
    "C058": ("src/bootstrap/core_service.py:3256; :3322-3326（ResumeBlockedRun 分支）", None),
    "C059": ("src/bootstrap/core_service.py:3256; :3327-3350（GetRunSnapshot 分支）", None),
    "C060": ("src/bootstrap/core_service.py:3256; :3351-3354（GetTaskProjection 分支）", None),
    "C061": ("src/bootstrap/core_service.py:3256; :3355-3364（RetryFailedTargets 分支）", None),
    "C055": ("src/bootstrap/core_service.py:3610-3613（core.ping 分支）", None),
    "C063": ("src/bootstrap/core_service.py:3677-3680（GetExportHistory 分支）", None),
    "C064": ("src/bootstrap/core_service.py:3657-3658（handle_start_export）", None),
    "C065": ("src/bootstrap/core_service.py:3668-3676（CancelExport 分支）", None),
    "C066": ("src/bootstrap/core_service.py:3659-3667（GetExportSnapshot 分支）", None),
    "C050": ("src/bootstrap/core_service.py:3653-3654（handle_get_reader_projection）", None),
    "C051": ("src/bootstrap/core_service.py:3655-3656（handle_save_reading_progress）", None),
    "C034": ("src/bootstrap/core_service.py:3783-3806（ListBooks 分支）", None),
    "C035": ("src/bootstrap/core_service.py:3733-3760（ListRecycleBinBooks 分支）", None),
    "C048": ("src/bootstrap/core_service.py:4334-4350（list_chapters 分支）", None),
    "C049": ("src/bootstrap/core_service.py:4334-4360（list_chapter_pages 分支）", None),
}

# Commands whose Core payload is a strict key set validated by Core (create/delete faces).
STRICT_CORE_SCHEMAS = {
    "C036": "`{title!}`（Core `_CREATE_FIELDS`，:244-247）",
    "C037": "`{book_id!, title!, chapter_number?}`（Core `_CREATE_FIELDS`，:244-247）",
    "C040": "`{book_id!, confirm_permanent_delete!}`（core_service.py:1341-1352）",
    "C041": "`{book_ids!, confirmed_book_ids!, confirm_count!, confirm_permanent_delete!}`（core_service.py:1360+）",
}

# C# typed result shapes where the stored sample is a test assertion instead of a wire response.
RESULT_OVERRIDES = {
    "C038": "`ImportOutcome{ok, message, error_code, imported_files, skipped_files}`（App/Services/ImportExportContracts.cs:27）",
    "C039": "`ImportOutcome{...}`（同上）",
    "C052": "`{id, size}`（HostCommandDispatcher.cs:118-124）",
    "C053": "`{revoked:true}`（HostCommandDispatcher.cs:135-140）",
    "C054": "`{revoked_count}`（HostCommandDispatcher.cs:151-156）",
    "C062": "`bool`（HostGrantCoordinator.RevealExportFolderAsync）",
    "C064": "`ExportStartInfo{export_id,status,page_count}`（App/Services/ImportExportContracts.cs:52）",
    "C065": "`ExportSnapshotInfo{...}`（App/Services/ImportExportContracts.cs:71）",
    "C066": "`ExportSnapshotInfo{...}`（同上）",
    "C014": "`HostCommandResult`（shell 动作成功/typed 拒绝；HostGrantCoordinator.cs:343）",
    "C056": "`RunStartInfo{run_id,status}`（App/Services/RunContracts.cs）",
    "C057": "`RunControlInfo{run_id,status,new_run_id?,new_run_status?}`（RunContracts.cs）",
    "C058": "`RunControlInfo{run_id,status}`（RunContracts.cs）",
    "C059": "`RunSnapshotInfo{run_id,command,scope,status,targets[]}`（RunContracts.cs）",
    "C060": "`TaskProjectionInfo{run_id,run_status,run_title,overall_progress,current_page_id,current_step_type,step_flow[],rows[],tasks[],counts,blocked_reasons[],controls}`（RunContracts.cs）",
    "C061": "`RunControlInfo{run_id,status}`（RunContracts.cs）",
    "C032": "`CredentialOperationResult`（HostCredentialCoordinator.cs:26；secret 不回显）",
    "C033": "`CredentialOperationResult`（HostCredentialCoordinator.cs:27）",
}

# Status overrides (default: FROZEN when registry+core+sample resolved; see classify()).
STATUS_OVERRIDES = {
    "C001": ("PARTIAL", "Dispatcher 未约束入参（透传），结果投影未在 C# 类型化；已实测成功样例，错误码集未逐条运行核实"),
    "C003": ("PARTIAL", "Dispatcher 未约束入参（透传），结果未在 C# 类型化；错误码集未逐条运行核实"),
    "C007": ("PARTIAL", "Dispatcher 未约束入参（透传），结果未在 C# 类型化；错误码集未逐条运行核实"),
    "C010": ("PARTIAL", "Dispatcher 未约束入参（透传），结果未在 C# 类型化；错误码集未逐条运行核实"),
    "C039": ("PARTIAL", "Host-local 文件夹导入无自动化集成样例（仅实现源码定位），需补 E2E 证据"),
    "C014": ("PARTIAL", "Host-local shell 动作无自动化样例（仅实现源码定位 + 人工调用路径）"),
    "C062": ("PARTIAL", "Host-local shell 动作无自动化成功样例（仅实现源码 + 未知导出 id 的 typed 拒绝测试）"),
    "C008": ("PARTIAL", "仅记录到错误样例（BACKUP_RESTORE_REQUIRES_CONFIRMATION）；成功响应外形未实证（见 Core handle_backup_restore 源码）"),
    "C012": ("PARTIAL", "仅记录到错误样例（PLUGIN_NOT_FOUND）；成功响应外形未实证（见 Core handle_plugins_set_plugin_enabled 源码）"),
    "C016": ("PARTIAL", "仅有 Dispatcher 约束 + Core handler 源码 + 集成 basis=success 请求，无响应外形样例"),
    "C017": ("PARTIAL", "同 C016：无响应外形样例"),
    "C018": ("PARTIAL", "同 C016：无响应外形样例"),
    "C019": ("PARTIAL", "同 C016：无响应外形样例"),
    "C022": ("PARTIAL", "同 C016：无响应外形样例（需真实 run 才能实证）"),
    "C027": ("PARTIAL", "同 C016：无响应外形样例（需 network/profile 配置才能实证）"),
    "C030": ("PARTIAL", "同 C016：无响应外形样例"),
    "C041": ("PARTIAL", "仅有 Dispatcher 约束 + Core 源码 + 集成 basis=success 请求，无响应外形样例"),
}

SAMPLE_OVERRIDES = {
    "C014": ("test", "apps/desktop-avalonia/tests/NewManga.Host.Tests/GrantIssuerTests.cs:215"),
    "C062": ("test", "apps/desktop-avalonia/tests/NewManga.Host.Tests/GrantIssuerTests.cs:255"),
}

ERROR_FAMILY = {
    "settings-generic": "通用应用 envelope：`INVALID_REQUEST` / `PROTOCOL_VERSION_UNSUPPORTED` / `UNKNOWN`（core_service.py:3589+）；命令特定码见 §5.1",
    "p15": "P15 settings：`SETTINGS_INVALID_INPUT` / `SETTINGS_NOT_FOUND` / `SETTINGS_CONFLICT` / `SETTINGS_UNAVAILABLE`（core_service.py:3372-3388、3706-3731；settings_commands.py:106-112）",
    "create": "创建面：`PROTOCOL_VERSION_UNSUPPORTED` / `INVALID_REQUEST`(+details) / `TARGET_NOT_FOUND` / `LIBRARY_WRITE_FAILED` / `UNKNOWN`（core_service.py:3504-3559、921-941）",
    "delete": "删除面：`PROTOCOL_VERSION_UNSUPPORTED` / `INVALID_REQUEST` / `TARGET_NOT_FOUND` / `UNKNOWN`（core_service.py:3561-3587、1341-1400）",
    "run": "Run 面：`INVALID_REQUEST` / `TARGET_NOT_FOUND` / `IDEMPOTENCY_KEY_REUSED` / `INVALID_RUN_TRANSITION`（core_service.py:3389-3411）",
    "reader-export": "阅读/导出面：`INVALID_REQUEST` / `EXPORT_NOT_FOUND` / `EXPORT_INPUT_UNAVAILABLE` / `EXPORT_PATH_UNAVAILABLE` / `UNKNOWN`（core_service.py:3648-3695）",
    "region": "Region/Reader 写面：`INVALID_REQUEST` / `TARGET_NOT_FOUND` / `LOCK_CHANGED` / `UNKNOWN`（core_service.py:4160-4300）",
    "host-local": "Host-local：`HOST_READ_ONLY` / `INVALID_ARGUMENTS` / typed `ShellActionException`（HostGrantCoordinator / HostCredentialCoordinator）",
    "bridge": "HostBridge：`SidecarException` typed code（资源 grant 拒绝/撤销，HostCommandDispatcher.cs:96-162）",
}

COMMAND_ERROR_FAMILY = {}
for fact_id in ("C002", "C004", "C005", "C006", "C008", "C009", "C011", "C012", "C013"):
    COMMAND_ERROR_FAMILY[fact_id] = "settings-generic"
for index in range(15, 32):
    COMMAND_ERROR_FAMILY[f"C{index:03d}"] = "p15"
for fact_id in ("C036", "C037"):
    COMMAND_ERROR_FAMILY[fact_id] = "create"
for fact_id in ("C040", "C041"):
    COMMAND_ERROR_FAMILY[fact_id] = "delete"
for index in range(56, 62):
    COMMAND_ERROR_FAMILY[f"C{index:03d}"] = "run"
for fact_id in ("C050", "C051", "C063", "C064", "C065", "C066"):
    COMMAND_ERROR_FAMILY[fact_id] = "reader-export"
for fact_id in ("C042", "C043", "C044", "C045", "C046", "C047"):
    COMMAND_ERROR_FAMILY[fact_id] = "region"
for fact_id in ("C014", "C032", "C033", "C038", "C039", "C062"):
    COMMAND_ERROR_FAMILY[fact_id] = "host-local"
for fact_id in ("C052", "C053", "C054"):
    COMMAND_ERROR_FAMILY[fact_id] = "bridge"
for fact_id in ("C034", "C035", "C048", "C049", "C055"):
    COMMAND_ERROR_FAMILY[fact_id] = "settings-generic"


def load_facts() -> list[dict]:
    data = json.loads(FACTS.read_text(encoding="utf-8"))
    return data["facts"]


def dispatcher_schema(front: str) -> tuple[str | None, int | None]:
    """Parse the dispatcher case block for one command and return (schema, line)."""
    lines = DISPATCHER.read_text(encoding="utf-8").splitlines()
    start = None
    for index, line in enumerate(lines, start=1):
        if re.search(rf'case\s+"{re.escape(front)}":', line):
            start = index
            break
    if start is None:
        return None, None

    block: list[str] = []
    for line in lines[start:]:
        if block and re.search(r'^\s*(case\s+"|default:)', line):
            break
        if block and re.search(r"^\s{8,}break;\s*$", line):
            break
        block.append(line)

    text = "\n".join(block)
    required: list[str] = []
    optional: list[str] = []
    patterns = [
        (r"RequireString\([^;]*?\"(?P<key>[a-z_]+)\"\)", "required-string"),
        (r"RequireBool\([^;]*?\"(?P<key>[a-z_]+)\"\)", "required-bool"),
        (r"RequireInt64\([^;]*?\"(?P<key>[a-z_]+)\"\)", "required-int"),
        (r"RequireObject\([^;]*?\"(?P<key>[a-z_]+)\"\)", "required-object"),
        (r"WriteRequiredStringArray\([^;]*?\"(?P<key>[a-z_]+)\"", "required-string[]"),
        (r"OptionalString\([^;]*?\"(?P<key>[a-z_]+)\"\)", "optional-string"),
        (r"WriteOptionalString\([^;]*?\"(?P<key>[a-z_]+)\"\)", "optional-string"),
        (r"WriteNullableString\([^;]*?\"(?P<key>[a-z_]+)\"\)", "nullable-string"),
        (r"WriteOptionalBool\([^;]*?\"(?P<key>[a-z_]+)\"\)", "optional-bool"),
        (r"WriteOptionalInt\([^;]*?\"(?P<key>[a-z_]+)\"\)", "optional-int"),
        (r"WriteOptionalInt64\([^;]*?\"(?P<key>[a-z_]+)\"\)", "optional-int"),
        (r"WriteOptionalDouble\([^;]*?\"(?P<key>[a-z_]+)\"\)", "optional-double"),
        (r"WriteStringArray\([^;]*?\"(?P<key>[a-z_]+)\"", "string[]"),
    ]
    for pattern, kind in patterns:
        for match in re.finditer(pattern, text):
            key = match.group("key")
            entry = f"`{key}{'!' if kind.startswith('required') else '?'}: {kind.removeprefix('required-').removeprefix('optional-')}`"
            target = required if kind.startswith("required") else optional
            if entry not in target:
                target.append(entry)
    if "WriteStartRunOverrides" in text and not any("overrides" in item for item in required + optional):
        optional.append("`overrides?: object`")
    if not required and not optional:
        if re.search(r"Legacy signatures take no arguments|break;", text):
            return "`{}`（无参数；Dispatcher 丢弃输入）", start
        return "透传（Core 校验）", start
    schema = " ".join(required + optional)
    if "discard" in text or "丢弃" in text:
        schema += "（Dispatcher 丢弃输入）"
    return schema, start


def sample_payload_keys(fact: dict) -> list[str]:
    sample = fact.get("sample") or {}
    request = sample.get("request")
    if isinstance(request, dict):
        payload = request.get("payload")
        if isinstance(payload, dict):
            return list(payload.keys())
    return []


def result_shape(fact: dict) -> str:
    override = RESULT_OVERRIDES.get(fact["id"])
    if override:
        return override
    sample = fact.get("sample") or {}
    response = sample.get("response")
    if isinstance(response, dict):
        error = response.get("error")
        result = response.get("result")
        if isinstance(error, dict) and error.get("code"):
            return f"错误样例：`error.code={error['code']}`（成功外形见 Core handler）"
        if isinstance(result, dict):
            keys = sorted(result.keys())
            return "`{" + ", ".join(keys) + "}`"
        if isinstance(result, list):
            if result and isinstance(result[0], dict):
                keys = sorted(result[0].keys())
                return "`[{ " + ", ".join(keys) + " }]`"
            return "`[array]`"
        if result is None:
            return "`null`"
        return f"`{type(result).__name__}`"
    return "见样例（测试断言）"


def schema_for(fact: dict) -> str:
    if fact["id"] in STRICT_CORE_SCHEMAS:
        return STRICT_CORE_SCHEMAS[fact["id"]]
    schema, _ = dispatcher_schema(fact["front"])
    if schema:
        return schema
    keys = sample_payload_keys(fact)
    if keys:
        return "透传（Core 校验；实测 payload：`{" + ", ".join(keys) + "}`）"
    if fact["channel"] == "bridge":
        return "见 Dispatcher bridge 分支（HostCommandDispatcher.cs:96-162）"
    if fact["channel"] == "host-local":
        return "见 Host 实现（Host-local 参数校验）"
    return "透传（Core 校验；实测空 payload）"


def core_ref(fact: dict) -> str:
    override = CORE_REF_OVERRIDES.get(fact["id"])
    if override:
        return override[0]
    if fact["channel"] != "core":
        return "—（无 Core 路由）"
    route = fact["route"]
    refs = []
    if fact.get("core_handler") and fact.get("core_handler_line"):
        refs.append(f"src/bootstrap/core_service.py:{fact['core_handler_line']}（{fact['core_handler']}）")
    dispatch_line = fact.get("core_dispatch_line")
    # Lines below 3500 are the protocol-constant / command-set tables, not a dispatch branch: only
    # keep a dispatch line when it is a real branch line or no handler definition was found.
    if dispatch_line and (dispatch_line > 3500 or not fact.get("core_handler")):
        refs.append(f"src/bootstrap/core_service.py:{dispatch_line}")
    if fact["route"] and fact["route"] in {"settings.get", "settings.update_section"}:
        refs.append("core_service.py:3927-3960（settings 分支）")
    return "；".join(dict.fromkeys(refs)) or "src/bootstrap/core_service.py（路由存在，行号待补）"


def dispatcher_ref(fact: dict) -> str:
    if fact.get("dispatcher_line"):
        return f"HostCommandDispatcher.cs:{fact['dispatcher_line']}"
    if fact.get("dispatcher_passthrough_line"):
        return f"HostCommandDispatcher.cs:{fact['dispatcher_passthrough_line']}（default 透传）"
    return "—"


def status_of(fact: dict) -> tuple[str, str]:
    if fact["id"] in STATUS_OVERRIDES:
        return STATUS_OVERRIDES[fact["id"]]
    if fact["channel"] in ("bridge", "host-local"):
        return ("FROZEN", "—") if fact.get("impl_ref") and fact.get("sample") else ("PARTIAL", "缺少实现引用或样例")
    missing = []
    if not fact.get("route"):
        missing.append("无 Core 路由")
    if fact.get("minor") is None:
        missing.append("无注册 minor")
    if not fact.get("core_dispatch_line") and fact["id"] not in CORE_REF_OVERRIDES:
        missing.append("Core 源码未定位")
    if not fact.get("sample"):
        missing.append("无真实样例/测试断言")
    return ("PARTIAL", "；".join(missing)) if missing else ("FROZEN", "—")


def evidence_cell(fact: dict, status: str) -> str:
    parts = [f"registry:{fact.get('registry_line') or '—'}", dispatcher_ref(fact), core_ref(fact)]
    sample = fact.get("sample") or {}
    kind = fact.get("sample_kind")
    source = sample.get("source") if isinstance(sample, dict) else None
    if status == "FROZEN":
        parts.append(f"样例({kind}): `{source}`" if source else "样例：—")
    else:
        parts.append(f"样例参考: `{source}`" if source else "样例：缺")
    return " · ".join(parts)


def render_row(fact: dict) -> str:
    status, gap = status_of(fact)
    fact["_status"] = status
    fact["_gap"] = gap
    family = COMMAND_ERROR_FAMILY.get(fact["id"], "settings-generic")
    return "| {id} | {front} | {route} | {channel} | {minor} | {schema} | {result} | {family} | {consumer} | **{status}** | {evidence} |".format(
        id=fact["id"],
        front=f"`{fact['front']}`",
        route=f"`{fact['route']}`" if fact.get("route") else "—",
        channel={"core": "core", "host-local": "host-local", "bridge": "bridge", "unbound": "—"}[fact["channel"]],
        minor=fact.get("minor") if fact.get("minor") is not None else "—",
        schema=schema_for(fact),
        result=result_shape(fact),
        family=f"§5.{list(ERROR_FAMILY).index(family) + 1}" if family in ERROR_FAMILY else "—",
        consumer=fact["consumer"] or "—",
        status=status,
        evidence=evidence_cell(fact, status),
    )


def main() -> int:
    facts = load_facts()
    facts_by_id = {fact["id"]: fact for fact in facts}
    assert len(facts_by_id) == 66, len(facts_by_id)

    rows = [render_row(fact) for fact in facts]
    frozen = sum(1 for fact in facts if fact["_status"] == "FROZEN")
    partial = sum(1 for fact in facts if fact["_status"] == "PARTIAL")
    gap = sum(1 for fact in facts if fact["_status"] == "GAP")

    tables = []
    for domain in DOMAIN_ORDER:
        domain_facts = [fact for fact in facts if fact["domain"] == domain]
        table = [
            "| ID | 前端命令 | 路由目标 | 通道 | minor | 入参（校验/实测） | 结果外形（实测/类型） | 错误码族 | UI 消费者 | 状态 | 源码引用 · 样例 |",
            "|---|---|---|---|:--:|---|---|---|---|---|---|",
        ]
        table.extend(render_row(fact) for fact in domain_facts)
        tables.append(f"### 4.{DOMAIN_ORDER.index(domain) + 1} {domain}（{len(domain_facts)} 条）\n\n" + "\n".join(table))

    partial_rows = [
        f"| {fact['id']} | `{fact['front']}` | {fact['_gap']} |" for fact in facts if fact["_status"] != "FROZEN"
    ]

    narrative = f"""# V11R 命令契约 V1（C001–C066 基线 + C067–C076 增量 PENDING）

状态：`ISSUED`（2026-10-30，DSH 委派 `core-bridge` 起草；独立 Reviewer 待指派）。
基线：`c73239999`（审计快照 `clean-snapshot-20261029@22de860` 的 66 条 Host 命令静态清册）。
上游：`doc/plan/V11R_AVALONIA_CONTRACT.md`（FROZEN）、审计附件
`G:/CODEX/New Manga.workspace/tasks/AUDIT-V11-INTAKE-1/命令清册_C001-C066.csv`。
生成器：`verification/V11R-A-3/tools/extract_contract_facts.py` +
`verification/V11R-A-3/tools/build_contract_doc.py`（行号/样例可机械复现；改契约后重新生成）。

> 本契约**不是** OpenAPI：它签发的是"当前真实注册表 + Dispatcher + Core 源码 + 真实样例"三者一致的
> 可验证边界。`FROZEN` 只表示该行的路由/通道/minor/入参校验/成功结果外形/至少一个真实样例已核实；
> 它**不**表示每条错误分支都已运行验证（逐条见 §6 缺口）。`PARTIAL` 明确写出缺口，`GAP` 表示不可核实。
> **禁止**把 Dispatcher 透传当作"已冻结 schema"——透传行一律按 §6 标注。

## 1. 使用方式与状态语义

| 状态 | 含义 | 可依赖的内容 |
|---|---|---|
| `FROZEN` | 注册表绑定 + Dispatcher 参数约束（或 Core 严格 key 集校验）+ Core 源码行 + 至少一个真实请求/响应样例（或等价测试断言）全部可核实 | 路由、通道、protocol minor、入参键集、成功结果外形、已定位错误码族 |
| `PARTIAL` | 上述证据链有一项缺失（典型：Dispatcher 透传未约束入参；Host-local 无自动化样例；结果未在 C# 类型化） | 仅可依赖已写明的部分；缺口列在 §6 |
| `GAP` | 无注册绑定或无法核实 | 不得据此实现 UI |
| `PENDING(...)` | 尚未合入的增量命令（C067–C076，来自 V11R-F0-1） | **不得**当作已冻结契约使用 |

权威顺序：**Core 源码 / 真实 wire 样例 > `HostCommandRegistry` > `HostCommandDispatcher` > 审计静态清册**。
审计附件是线索，不是事实来源；本契约每条都以仓库源码行号与证据文件锚定。

## 2. 共享信封与协议

应用通道（`core_service`，JSON-lines）：

```json
{{"protocol":"new-manga.core","version":{{"major":2,"minor":<N>}},"request_id":"...","command":"<route>","payload":{{...}}}}
```

响应：`{{"protocol","version","request_id","result":<object|array|null>,"error":<null|{{code,category,message,retryable,details?}}>}}`。
异步事件帧混在 stdout（`event_type`/`event_id`，无 `request_id`），客户端必须过滤（`CoreProtocol.IsEventFrame`）。

| minor | 用途 | 约束 |
|---:|---|---|
| 3 | 默认应用命令（读、settings 基础、cleanup/backup/plugin、Region/Reader、Run/Export） | 请求 `minor` 必须等于 3（`_P15_SETTINGS_COMMANDS`/`_RUN_COMMANDS` 之外按 3 校验） |
| 7 | P15 settings / provider / network / credential 面（C015–C031） | Core 拒绝 minor≠7（`core_service.py:3706-3711`） |
| 8 | `CreateBook` / `CreateChapter`（C036/C037） | Core 拒绝 minor≠8（`core_service.py:240,3504-3518`） |
| 10 | `PermanentlyDeleteBook(s)`（C040/C041） | Core 拒绝 minor≠10（`core_service.py:241,3561-3575`） |

Host-local 与 HostBridge 命令没有 Core minor（表中记 `—`）。

## 3. 命令总表（按域）

共 66 条：Settings 33 / Library 8 / Region 6 / Reader 4 / Resource 3 / Workbench 12。
统计：**FROZEN {frozen} 条 · PARTIAL {partial} 条 · GAP {gap} 条**。

## 4. 逐条清册

""" + "\n\n".join(tables) + """

## 5. 错误码族（源码定位）

| 族 | 错误码集 | 源码 |
|---|---|---|
""" + "\n".join(
        f"| §5.{index + 1} `{name}` | {text} | 见族内引用 |" for index, (name, text) in enumerate(ERROR_FAMILY.items())
    ) + f"""

> 说明：以上是**源码定位**到的错误码集；除 A-1/A-2 已运行验证的 CreateChapter / Run 面之外，
> 各命令的错误分支未逐条注入运行。§6 已按命令记录状态。

## 6. 缺口清单（PARTIAL / GAP 逐条）

| ID | 命令 | 缺口 |
|---|---|---|
""" + "\n".join(partial_rows) + """

## 7. 关键兼容边界：`library_start_run` minor=3 vs Core 2.6 provider overrides

**结论：当前命令路径（C056 `library_start_run` → Core `StartRun`，注册 minor=3）无法通过
`overrides.provider_profiles`；该参数只有请求 `minor=7` 时 Core 才接受。因此"新增 Provider 覆盖参数
能经现有命令路径通过"这一假设不成立，不能按 UI 设置等同 Run 成功。**

依据（`src/bootstrap/core_service.py`）：

- `_dispatch_run_command` 把请求 version 的 minor 传入（`:3697-3703`）；
- `StartRun` 分支：`if "provider_profiles" in overrides and protocol_minor != _P15_PROTOCOL_MINOR: raise PipelineError("INVALID_REQUEST", "provider profile overrides require Core 2.6")`（`:3283-3284`，`_P15_PROTOCOL_MINOR=7`，`:239`）；
- 只有 `protocol_minor == 7` 时才调用 `P15SettingsCommands.prepare_run_snapshot(scope, overrides)` 生成快照（`:3287-3290`）；
- `HostCommandRegistry` 的 `library_start_run` 注册为 minor=3（`HostCommandRegistry.cs:147`），Dispatcher 只写 `command/scope/overrides/idempotency_key`，不改 minor（`HostCommandDispatcher.cs:198-206`）。

验证方法（已复跑，证据 `verification/V11R-A-3/minor-compat/start-run-minor-probe.json`，
脚本 `verification/V11R-A-3/tools/probe_start_run_minor.py`，冻结 sidecar + BOOK-FIXTURE 副本，
四条 StartRun 使用同一有效 book scope 对照）：

| 变体 | 请求 minor | overrides | 实测响应 |
|---|---:|---|---|
| (a) 普通 overrides | 3 | `provider_bindings` | `{"run_id":"run-44e5…","status":"pending"}` → 成功 |
| (b) Provider 覆盖 | 3 | `provider_profiles` | `INVALID_REQUEST`（"Run request is invalid"；Core 源码 :3283-3284 的 minor 门拒绝） |
| (c) Provider 覆盖 | 7 | `provider_profiles` | `INVALID_REQUEST` + `details={phase:"binding",action:"select_profile",message_key:"SETTINGS_INVALID_INPUT"}` → 已进入 P15 `prepare_run_snapshot`，需要有效 provider profile 配置才可能成功 |
| (d) 普通 overrides | 7 | `provider_bindings` | `{"run_id":"run-431c…","status":"pending"}` → 成功（证明 minor=7 本身被接受） |

结论补充：(a) 成功而 (b) 在同一 book scope 下失败，差异只可能来自 `provider_profiles` 的 minor 门；
(c) 证明 minor=7 能进入 P15 解析路径（当前配置下返回 SETTINGS_INVALID_INPUT，属 P15 配置态而非协议拒绝）；
(d) 证明 minor=7 的普通 overrides 可成功。因此"把 `library_start_run` 升到 minor=7 就能透传 provider overrides"
只是必要条件，不是充分条件：还必须 P15 provider profile/binding 配置有效。
UI 侧结论：在命令路径升级为 minor=7 之前，`IRunController.StartRunAsync` 只承诺
`provider_bindings` 等普通 overrides；`provider_profiles` 应视为未支持的边界并在 UI 禁用/提示。

## 8. C067–C076 增量命令（PENDING, V11R-F0-1；另预留 C077 占位）

`V11R-F0-1`（core-writer）正在为 Region 写面新增 10 条 Host 命令，命令总数将从 66 增至 76；另有 1 条 Region 文本投影读命令（C077）合入后为 77，本表预留占位。
这些命令**尚未合入本分支/注册表**，因此全部标 `PENDING(V11R-F0-1)`，**不得**当作已冻结契约。
上游契约（core-writer 产出，合入后本表可升级为 `FROZEN`）：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`。

| ID | 前端命令（待合入） | 域 | 预期通道 | minor | 参数外形（待 core-writer 契约确认） | 状态 |
|---|---|---|---|---|---|---|
| C067 | `create_region` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C068 | `delete_region` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C069 | `save_region_geometry` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C070 | `merge_regions` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C071 | `split_region` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C072 | `reorder_regions` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C073 | `save_manual_translation` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C074 | `confirm_region_final` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C075 | `set_region_lock` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C076 | `pin_revision` | Region | core | 3（zero protocol bump，Lead 裁定） | `PENDING(V11R-F0-1)` |
| C077 | （命令名待 core-writer 确认）Region 文本投影（读） | Region | core | 待定（读命令，预期 3） | `PENDING(V11R-F0-1)` |

约束：`C067–C076` 在 `V11R_REGION_WRITE_CONTRACT.md` 合入并由 DSH 签发前，任何一方不得在 UI 中
把它们当稳定契约消费；`CommandContractV11RTests` 会断言这 10 条不进入"已冻结集合"。

## 9. 已知偏差与后续

1. **`plugins_open_directory` / `library_import_folder` / `library_reveal_export_folder`** 为 Host-local 面，
   无完整自动化成功样例（前两者仅实现源码定位；`reveal` 只有未知 id 的 typed 拒绝测试）→ `PARTIAL`。
2. **`settings_get` / `cleanup_preview` / `backup_list` / `plugins_list`** 是 Dispatcher 透传读，
   结果未在 C# 类型化 → `PARTIAL`；补证方式：为每个命令补一条真实 probe 样例 + C# 投影类型。
3. **错误分支未逐条注入运行**：§5 的码集来自源码定位；若某命令错误码需要签发级保证，需新增
   negative probe（建议纳入 `V11R-A-4` 快照 CI）。
4. **`core.ping`** 在 Host 侧作为启动探针（`HostCommandRegistry.cs:119`），其 `capabilities` 只有
   `library.list_books`，不代表全部命令可用性。
5. **`abandon`**：Core `ControlRun` 支持 `abandon`（中断处置），但冻结的 `RunControlAction` 只暴露
   4 个动作（`doc/plan/V11R_AVALONIA_CONTRACT.md` §5.2）→ UI 契约 GAP，留待中断恢复任务补齐。

## 10. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-10-30 | 初版：C001–C066 逐条签发（FROZEN {frozen} / PARTIAL {partial} / GAP {gap}）+ C067–C076 PENDING + minor 兼容结论 | core-bridge（V11R-A-3） |
"""

    OUT.write_text(narrative, encoding="utf-8")
    print("wrote", OUT.relative_to(WORKTREE), "| FROZEN", frozen, "PARTIAL", partial, "GAP", gap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




