---
task_id: SETTINGS-PROFILE-UI-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 327aa8526
delivery_head: f2cf8734325c2597d46c064e36b7824bb4cfe2ec
status: ready-for-integration
---

# Handoff：SETTINGS-PROFILE-UI-1（设置页 profile 管理 UI）

## 交付结果

实现提交 **`f2cf8734325c2597d46c064e36b7824bb4cfe2ec`**（branch `task/SETTINGS-PROFILE-UI-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1`；卡面 base `dde7f50ee`，按 DSH 指令从当前 HEAD `327aa8526` 建分支）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；未显示/记录任何 credential secret；未伪造 test 诊断结果。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 provider profile | **MET** | Provider Profile 管理卡：列表 + 新建/编辑/删除（P15 schema：display_name/provider_id/capabilities/endpoint/model/network_profile/enabled）+ typed 提示 + 空态。 |
| AC2 network profile | **MET** | Network Profile 管理卡：列表 + CRUD + 测试网络（Core 真实 6 段诊断结果）+ 解析网络（network_profile_id/mode/source）+ 设默认/清默认。 |
| AC3 绑定/默认 | **MET** | Provider 绑定 slot 卡：scope(global/book/chapter)+capability+profile → bindings set/clear/resolve；network default set/clear 在 network 卡。 |
| AC4 测试 | **MET** | 10 项 headless（CRUD 精确参数/typed 错误/空态/test-resolve 渲染/TLS 确认/bindings scope/页面接线/payload 契约）+ 真机截图 2 张。 |
| AC5 回归/门禁 | **MET** | test.ps1 **210/210**（61/55/94，0 skipped）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）；check PASS；19 条 64-hex pin。 |

## UI 结构（SettingsPage，凭据卡之后）

| 卡片 | 内容 |
|---|---|
| Provider Profile 管理 | 列表；显示名称、Provider 类型（创建后不可改）、能力复选框（OCR/Translation/Inpaint/Detection/Rendering）、Endpoint、模型、绑定 network profile、启用；新建 / 新建并保存 / 保存修改 / 删除 / 刷新；状态行 |
| Network Profile 管理 | 列表；显示名称、模式（Direct/System/HTTP/HTTPS/SOCKS5）、代理地址（HTTP/HTTPS/SOCKS5 必填；Direct/System 禁用并要求留空）、校验 TLS、确认关闭 TLS 校验、代理失败回退直连；新建/保存/删除/刷新、设为默认/清除默认；provider 选择 + 测试网络/解析网络 → 诊断/解析结果文本 |
| Provider 绑定（slot） | Scope 类型（global/book/chapter，book/chapter 显示 id 输入）、能力、Provider profile；绑定/清除绑定/解析当前绑定/刷新；状态行 + 解析结果 |

调用链：`SettingsPage → IHostController（HostController）→ HostRuntime.Commands（HostCommandDispatcher）→ settings_provider_profiles_* / settings_network_profiles_* / settings_network_profile_* / settings_provider_bindings_*`；**未新增/修改任何 Host 命令**。

## Record Decision

1. **Schema 逐一对照 Core 校验**（`src/bootstrap/settings_commands.py`）：capabilities 必须非空且 ∈ CAPABILITY_NAMES；mode ∈ Direct/System/HTTP/HTTPS/SOCKS5；HTTP/HTTPS/SOCKS5 必须有合法 proxy_endpoint（scheme 匹配），Direct/System 必须为 null；provider update 不带 provider_id（Core 保留原 provider_type）；network create 的 verify_tls/allow_fallback 可选，update 必填；关闭 TLS 校验需 `confirm_disable_tls_verification=true`，否则 Core 返回 `TLS_CONFIRMATION_REQUIRED`（UI 显示明确提示，不自动替用户确认）。
2. **payload 精确性**：App 层 `SettingsProfilePayload` 用 `Utf8JsonWriter` 显式构造所有 15 条命令的 payload，键与 `HostCommandDispatcher` 一致（可空字段显式 null；binding scope 只含 kind[/book_id|chapter_id]）；headless `PayloadContract_MatchesTheDispatcherKeys` 逐键断言，UI 调用参数由 fake 端口逐字段断言（CRUD 的 profile_id/network_profile_id/scope 均覆盖）。
3. **空态与不可用**：列表为空显示空态文案；`test/resolve` 在 Host/Core 不可用或无结果时显示「不可用（未伪造结果）」；只有真实返回才渲染 `status=passed` / failed_stage / stages / source。卡面「不得伪造 test 诊断结果」在 UI 层与测试层双重保证。
4. **错误呈现**：`SETTINGS_ITEM_NOT_FOUND` → 目标不存在；`SETTINGS_CONFLICT` → 仍被绑定/运行引用需先清绑定；`SETTINGS_INVALID_INPUT` → 参数无效；`TLS_CONFIRMATION_REQUIRED` → 需勾选确认；`SETTINGS_UNAVAILABLE` → 服务不可用；`HOST_NOT_READY` → 等待 Host。映射不抛异常进 UI。
5. **页面可达性（真机截图发现的真实缺陷）**：新增三卡后设置页高度超过窗口，原实现无滚动 → 下方卡片被裁切不可达；已将内容行改为 `ScrollViewer`（禁用横向滚动），真机截图证明可滚动到 Network 卡。
6. **测试边界**：UI 用 `FakeHostController` 记录精确参数（不写真实 `%APPDATA%`）；真实 Core 链路（profile CRUD/test/resolve 的 wire 行为）由既有 NS-WIRE-B2/NS-WIRE-B1 对冻结 sidecar 的测试覆盖，本卡不重复创建真实 profile。
7. **并发 flake 记录**：App.Tests 既有 `ShellCommandCatalog.WriteEvidence` 在同进程并发写同一证据文件时偶发 `File.Create` 冲突（与本卡无关；单跑与标准 gate 均通过）；未修改该测试基建（超出本卡范围），如实记录供 DSH 决定是否另开清理 Task。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 CRUD 参数 | `ProviderSection_EmptyState_ThenCreate_SendsExactDraft`、`ProviderSection_UpdateAndDelete_SendProfileId` | Avalonia Headless 11.3.22 + FakeHostController | create 无 profile_id、字段精确；update 带 profile_id；delete 记录 id；空态出现/消失 | `settings-profile-ui/provider-create.json`、`provider-update-delete.json` |
| AC1 typed 错误 | `ProviderSection_TypedError_AndLocalValidation_AreRendered` | 同上 | `SETTINGS_CONFLICT` 中文提示；本地缺字段 → INVALID_ARGUMENTS 且零调用 | `provider-error-feedback.json` |
| AC2 CRUD/模式规则 | `NetworkSection_EmptyState_Create_SendsExactDraft` | 同上 | HTTPS+endpoint 精确；HTTP 缺 endpoint 拒绝；Direct 发送 proxy_endpoint=null | `network-create.json` |
| AC2 test/resolve | `NetworkSection_TestAndResolve_RenderCoreResult_AndNeverFabricate` | 同上 | 无结果 → 「不可用」；Core 结果 → status/failed_stage/stages 渲染；resolve → id/mode/source | `network-test-resolve.json` |
| AC2 TLS/默认/删除 | `NetworkSection_TlsConfirmationRequired_IsRendered`、`NetworkSection_Delete_And_DefaultSetClear` | 同上 | TLS_CONFIRMATION_REQUIRED 提示；default set/clear、delete 参数正确 | `network-tls-confirmation.json`、`network-default-delete.json` |
| AC3 bindings | `BindingsSection_SetClear_WithGlobalAndBookScopes_SendExactArguments` | 同上 | global/book/book clear 精确 | `bindings-set-clear.json` |
| AC4 页面接线 | `SettingsPage_WiresAllProfileSections_ToTheController` | 同上 | 三卡列表与回填正确 | `settings-wiring.json` |
| AC4 payload 契约 | `PayloadContract_MatchesTheDispatcherKeys` | 无 UI | 15 条命令 payload 键集与 dispatcher 一致 | `payload-contract.json` |
| AC4 真机截图 | Debug `NewManga.App.exe`（隔离 `NEWMANGA_DATA_ROOT`）→ 设置页 → 滚动 | Windows 10.0.26300；1278×818 | provider/network 卡片与表单完整可见；未做任何写操作 | `real-app-provider-profile.png`、`real-app-network-profile.png`、`real-app-screenshots.json` |
| AC5 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **210/210**（61/55/94），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC5 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2772P/9S（0 新增失败） | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/SETTINGS-PROFILE-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/SETTINGS-PROFILE-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/SETTINGS-PROFILE-UI-1`；delivery head `f2cf87343`。
- 复现：`verification/SETTINGS-PROFILE-UI-1/REPORT.md §7`。
- 前置：无 sidecar 需求（headless）；真机截图需桌面会话 + 隔离 `NEWMANGA_DATA_ROOT`，不要做 profile 写操作。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 重跑 test.ps1 复核（210/210；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）→ 集成 → closeout。
- 并发：本卡只改 `NewManga.App`（其它任务在 Host/CoreClient/Python），无文件冲突。

## 下一任务建议（必填）

- Task ID / 标题：**无必须由我立即释放的实现任务**；可选后续（由 DSH 裁决）：
  1. `SETTINGS-PROFILE-UI-2`：book/chapter scope 的 id 选择器（接书架/阅读器）与 provider 类型建议列表；
  2. `APP-TEST-EVIDENCE-FLAKE-1`：App.Tests 证据文件并发写 flake 清理（小改动，需 DSH 判断是否值得）。
- 推荐 Agent / Reviewer：UI 后续 = saber-ui-spec；flake 清理 = Antigravity/Codex；Reviewer = 未参与实现者（DSH 排班）。
- 推荐原因与前置依赖：profile 管理已可用，book/chapter scope 目前手填 id 是主要体验缺口；flake 影响 gate 稳定性但与本卡无关。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `f2cf87343`；base `327aa8526`。
- 允许修改路径：`apps/desktop-avalonia/**`、新任务卡、STATUS/PLAN/LEDGER、`verification/<新任务>/**`。
- 禁止范围：不改 Core 语义/协议/Host 契约/旧壳；不写真实 vault/%APPDATA%；不 push/gc/prune。
- 交付物：后续实现 + headless 测试 + 真机截图（如涉及 UI）+ 证据 + Handoff。
- 验证命令与完成 Gate：test.ps1 全绿（≥210）、vitest 60/567、pytest 无新增失败、`check.ps1 -TaskPath` PASS、64-hex pin、独立 Review。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 SETTINGS-PROFILE-UI-1（delivery f2cf87343，walkthrough 见 doc/handoffs/SETTINGS-PROFILE-UI-1-handoff.md 与 verification/SETTINGS-PROFILE-UI-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 19 条 pin（sha256 与文件一致）；抽查 UI→IHostController→HostCommandDispatcher 的 payload 键（provider create/update/delete、network create/update/delete/test/resolve/default、bindings set/clear/resolve 与 dispatcher 一致）；确认空态与「不可用（不伪造诊断）」行为、TLS_CONFIRMATION_REQUIRED 提示、ScrollViewer 可达性；重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 210/210；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 dotnet test --filter FullyQualifiedName~SettingsProfileUiTests（应 10/10）；给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. 真实 Host 全链未在本卡 UI 测试中执行（卡面要求不写真实数据）；由既有冻结 sidecar 测试覆盖。
2. 真机截图时 Host 未就绪（Debug 无 sidecars）→ 列表空态；表单/空态/滚动已验证。
3. provider_id/endpoint/model 自由文本，无建议/校验列表（Core 负责 URL 与必填校验）。
4. book/chapter scope 的 id 为文本框；未接书籍/章节选择器。
5. network test 的 ProviderAuth 阶段依赖 provider 已配置凭据；UI 只显示真实结果。
6. App.Tests 既有 evidence 并发写 flake（与本卡无关，已记录）。
7. 需独立 Review（Owner 不得自审）。
