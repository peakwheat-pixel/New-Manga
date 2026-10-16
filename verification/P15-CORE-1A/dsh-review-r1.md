# P15-CORE-1A 独立 Review（R1，Coordinator 路由的 Reviewer=dsh）

| 项 | 值 |
|---|---|
| Task | P15-CORE-1A（设置面 Core 实现 A：G21 Provider 面 + G24 覆盖解析） |
| Owner | Codex（`/codex-dispatch` CLI，`danger-full-access`） |
| Reviewer | **dsh**（本会话，`route-agent.py` 路由；Owner 已机器排除） |
| 交付 | 实现 `9232802c0`；HEAD `3f11a8d52`（证据 + Handoff） |
| 基线 | `b1f4d08c7` |
| 结论 | **approved（附 1 项合并期契约对齐，见 §3）** |

## 1. 我**亲自复跑**

| 套件 | 我的实测 |
|---|---|
| `python -m pytest tests/core -q -p no:cacheprovider`（py312 venv） | **420 passed, 1 warning** ✓（基线 **407** → **+13** 新测试全通过，零回归） |

## 2. 逐项验证

| # | 验证项 | 方法 | 结果 |
|---|---|---|---|
| V1 | 范围 | `git diff --name-only` | **PASS**：9 个 `src/**`/`tests/core/**` 文件 + Handoff + 6 份证据；**无越界**（未改契约/apps/Schema/依赖） |
| V2 | **命令名与契约逐字一致** | 集合比对 | **PASS**：契约 9 条命令**全部实现**；代码中其余"疑似新命令"实为 **§9 message key**（`SETTINGS_*`）与 **§9 phase 名**（`settings_resolution`），**非命令** → **无发明 wire** |
| V3 | **分发接入** | 读实现 | **PASS**：`settings_commands.py` 导出 `P15SettingsCommands`/`SettingsSurfaceError`/`P15_SNAPSHOT_KEY`；`core_service.py` 定义 `_P15_SETTINGS_COMMANDS`（9 条）并在 **L2671 分发**、**L3247 门控协议**——与既有 `settings_get`/`settings_update_section` **同一机制** |
| V4 | **处置语义真的落地** | 读实现 + 测试 | **PASS**：Snapshot 返回 **`{"frozen": True}`**（L273）且绑定按 run 冻结；`_scope_context`/`_validated_context` 实现 **scope 层级校验**；测试名逐条对应 AC——`allows_same_provider`（**多 Profile 同 Provider**）、`resolution_priority_and_no_fallback`（**解析优先级 + 不隐式回退**）、`run_snapshot_freezes_profile_and_setting_provenance_without_references`（**冻结 + 来源 + 无引用**）、`override_layers_and_unsupported_value_fail_closed`（**覆盖分层 + 不支持值 fail-closed**） |
| V5 | **§9 封闭投影** | 读实现 | **PASS**：`SettingsSurfaceError` 只含 **category/phase/action/message_key** 四字段，**不透传底层异常或原始响应** |
| V6 | **Secret/路径边界** | 检索泄露模式 | **PASS**：未发现 `response.text`/`raw_response`/`headers[...]`/`output_path`/`str(exc)` 等模式；唯一 `password` 命中是 **L801 `parts.password is not None`**——**拒绝 endpoint 内嵌凭据**（契约要求），**安全正向** |
| V7 | **既有命令未改变** | diff | **PASS**：`core_service.py` 的改动为**新增分发与门控**，既有 `settings_get`/`settings_update_section` 语义未变；`test_new_settings_wire_requires_26_and_old_surface_keeps_23` 亦断言旧面保持 **2.3** |
| V8 | 证据 | 逐条核验 | **PASS**：**14 条证据行**，按**文件×AC 精细映射**（REGISTRY-FACT/COMMANDS/DISPATCH/ASSEMBLY/START-RUN/SETTINGS-STORE/PROFILE-STORE/SQLITE-SNAPSHOT/CAPABILITY/TESTS/日志/退出码/首跑/资源），提交列均为真实 SHA；**`pytest-core-first-attempt.*` 如实保留**（首跑留档，未掩盖） |

## 3. 需在集成时处理的**契约对齐**（跨任务版本偏移）

**事实**：实现中 `core_service.py:187` 为 **`_P15_PROTOCOL_MINOR = 6`**，测试亦断言 `{major: 2, minor: 6}`；而 **P15-C1-FU1** 已把契约中**全部 P15 Core 命令**的版本定为 **`minor: 7`**（"本 FU1 将 P15 目标 minor 从 `6` 增至 `7`"）。

**根因**：本 Task 基点 `b1f4d08c7` **早于** FU1 的合并（`94197afc9`）→ 实现按其基点时的 2.6 门控。

**判定**：**非实现缺陷，而是合并期版本对齐**（同类先例：跨任务计数断言须按合并后真实值更新）。**契约是权威** → 集成时由 Coordinator 将常量与测试期望对齐为 **7**，并**重跑 Core 套件**验证；该处置记入 closeout（**不得**静默放过，也**不**因此判 Owner 返修）。

## 4. 结论

1A 在**正确的分层**（ports → infrastructure → application → bootstrap）实现了 G21/G24 的冻结命令面，**命令名逐字一致、无发明 wire**、分发接入既有机制、**处置语义有实现与测试双证据**、§9 投影封闭、Secret 边界含**拒绝内嵌凭据**的正向检查、证据精细且如实。**批准集成**；集成时执行 §3 的版本对齐。
