---
task_id: P15-CORE-1B
author: Codex
recipient: DeepSeek Harness
base_commit: c279659117db56b93d5676e5bb39fd8453b0d385
delivery_head: 6cf3c820990591cf6e7581db1ae38eea54d14fdc
status: in_review
---

# Handoff：P15-CORE-1B

## 交付结果

在 Core 的 P15 dispatcher 中新增 G23 Network Profile CRUD、全局默认选择与解析命令，以及 G22 `BindProfileCredential` / `ClearProfileCredential` 受信 Host→Core 命令。复用 `P15SettingsCommands.handle`、`_P15_SETTINGS_COMMANDS`、minor 7 门控和 §9 的四字段安全错误投影。

G22 凭据命令只存在于 Core 私有 stdio dispatcher；`verification/P15-CORE-1B/webview-route-scan.txt` 记录了 Tauri 源码无这两个命令的扫描结果。没有修改 `apps/desktop/**`。Core Assembly 已提供 `credential_store` 与 `network_profile_store`，本 Task 复用现有装配，无需改 `core_assembly.py`。

实现包括严格模式/endpoint 校验、TLS 关闭确认、默认 fallback=false、Provider→Global→System→Direct 解析、引用命名空间与 Credential Store 存在性校验、失败绑定清理新引用并保留旧绑定、清除撤销当前引用、以及对 Provider/全局/Run Snapshot 所引用 Network Profile 的删除保护。Profile/错误返回不包含 `CredentialRef` 或 Secret。

交付命令：

- `settings_network_profiles_list`
- `settings_network_profiles_create`
- `settings_network_profiles_update`
- `settings_network_profiles_delete`
- `settings_network_profile_default_set`
- `settings_network_profile_default_clear`
- `settings_network_profile_resolve`
- `BindProfileCredential`
- `ClearProfileCredential`

协议声明：所有新增 P15 Core 命令均使用 `{ major: 2, minor: 7 }`。既有 Core 命令仍为 minor 3。未实现 `settings_network_profiles_test`、G21 或 G24。

变更路径：

- `src/bootstrap/core_service.py`
- `src/bootstrap/settings_commands.py`
- `src/infrastructure/settings/json_profile_stores.py`
- `tests/core/test_p15_core_settings.py`
- `doc/tasks/P15-CORE-1B.md`
- `doc/handoffs/P15-CORE-1B-6cf3c820.md`
- `verification/P15-CORE-1B/**`

实现交付 commit（本 Handoff 的 `delivery_head`）：

```text
6cf3c820990591cf6e7581db1ae38eea54d14fdc
```

该值是在提交实现与测试后以 `git rev-parse HEAD` 取得；Handoff 和 Task 证据作为后续文档提交，不自引用。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1–AC4、反例与回归 | `& 'G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe' -m pytest tests/core -q -p no:cacheprovider` | Python 3.12.3，Windows，worktree `codex/P15-CORE-1B`，delivery head `6cf3c820990591cf6e7581db1ae38eea54d14fdc` | **440 passed / 0 skipped / exit 0**；基线 420，新增 20。1 个既有 Pillow `Image.getdata` 弃用 warning | `verification/P15-CORE-1B/pytest-core.log`、`pytest-core.exit-code.txt`、`pytest-core.command.txt`、`pytest-core.environment.txt` |
| Proxy failure must not retry Direct | 将 `StdlibTransport._send_once` 注入一次代理连接失败，断言异常传播且只尝试代理路由一次 | 同上 | PASS；无真实网络请求 | `tests/core/test_p15_core_settings.py::test_proxy_failure_does_not_retry_direct_by_default` |
| WebView 凭据路由排除 | 在 `apps/desktop/src-tauri/src` 搜索私有凭据命令与 1C 命令 | base `c279659117db56b93d5676e5bb39fd8453b0d385` | PASS；无 Tauri 源码注册命中 | `verification/P15-CORE-1B/webview-route-scan.txt` |
| 首次完整回归诊断 | 相同全量 pytest 命令 | 首次修正前 | 436 passed / 1 failed；仅失败于测试固定读取随机排序列表第一项。断言已改为按 `profile_id` 查找，后续最终回归全绿 | `verification/P15-CORE-1B/pytest-core-first-attempt.log`、`pytest-core-first-attempt.exit-code.txt` |

未运行真实代理/Provider 网络请求，也未运行 `settings_network_profiles_test`；后者属于 1C，本 Task 明确排除。没有安装或变更依赖。没有启动独立 Review。

## 接收方式

- 仓库：`G:/CODEX/New Manga`
- branch：`codex/P15-CORE-1B`
- worktree：`G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B`
- base：`c279659117db56b93d5676e5bb39fd8453b0d385`
- 固定被审查 head：`6cf3c820990591cf6e7581db1ae38eea54d14fdc`
- 复现：使用上表 Python 解释器与全量 pytest 命令。
- 无 Schema、migration、依赖或桌面 Host 修改。

## 下一任务建议

- Task：P15-CORE-1B 的独立只读 Review；先决条件为 Reviewer 固定本 Handoff 的 `delivery_head`。
- 推荐 Agent / Reviewer：DeepSeek Harness（`dsh`），Owner Codex，不得由 Owner 自审。
- Recovery point：主仓库 `G:/CODEX/New Manga`；branch `codex/P15-CORE-1B`；worktree `G:/CODEX/New Manga.workspace/worktrees/P15-CORE-1B`；base `c279659117db56b93d5676e5bb39fd8453b0d385`；被审 head `6cf3c820990591cf6e7581db1ae38eea54d14fdc`。独立 Review worktree 尚未创建，待 Codex 创建。
- 允许路径：Review 报告写入 `verification/P15-CORE-1B/**`；生产源码、契约、Host、Schema 与依赖只读。
- 交付物：按 AC1–AC6、冻结 wire、Secret 投影、旧命令零变化、测试与证据验证的 Review 报告；发现项附文件、行号、复现或证据。
- Gate：独立 Reviewer 固定 commit；完成报告后由 Codex 处理 finding 与集成，不在本 Handoff 中预判批准。
- 可直接转发指令：

  > 请对 `P15-CORE-1B` 的固定实现 head `6cf3c820990591cf6e7581db1ae38eea54d14fdc` 做独立只读 Review。按 Task AC1–AC6 和 P15 rev 2.7 / P10 契约检查 Network CRUD、模式与 endpoint 校验、TLS 确认、默认与 Provider→Global→System→Direct 解析、代理失败不静默直连、凭据引用归属/替换/清除、§9 错误投影、Tauri WebView 排除、旧命令零变化及证据完整性。不要改生产源码或契约；报告写入 `verification/P15-CORE-1B/`，逐项附证据和严重级别。

## 风险与遗留

- 没有真实代理/Provider 连接诊断；`settings_network_profiles_test` 留给 P15-CORE-1C。
- Provider 与 proxy CredentialRef 使用现有 `NewManga/{kind}/{target_id}` 归属命名空间；Host 若做替换，应在该命名空间下提供新的唯一引用。
- `doc/STATUS.md` 与 `doc/REBASELINE_PLAN.md` 未修改；P15-CORE-1C 仍须等本 Task Review 与集成 Gate。
- 未触碰主仓库 dirty 文件；未 push、merge、reset；未自行发起独立 Review。
