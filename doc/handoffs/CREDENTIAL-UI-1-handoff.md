---
task_id: CREDENTIAL-UI-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 6f6e4a678
delivery_head: 5b5d67fc5a248f1081cab4dca49faa2d85d71f97
status: ready-for-integration
---

# Handoff：CREDENTIAL-UI-1（设置页凭据 UI：安全输入 → credential_put/clear）

## 交付结果

实现提交 **`5b5d67fc5a248f1081cab4dca49faa2d85d71f97`**（branch `task/CREDENTIAL-UI-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1`，base `6f6e4a678`）；本 Handoff 与任务卡 pin 在后续文档提交中记录。未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；未写真实 Windows 凭据库、未触碰真实 `%APPDATA%`（真机截图用隔离 `NEWMANGA_DATA_ROOT`）。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 安全输入 | **MET** | 设置页「凭据」区块：目标选择 + `SecretTextBox` 掩码输入 + 保存（`credential_put` create/replace）/清除（`credential_clear`）/刷新；typed 成功与失败提示。 |
| AC2 状态显示 | **MET** | 目标行 `configured / missing`（无 secret）；`CREDENTIAL_CONFLICT` 明确提示 +「确认替换/取消」二次确认，确认前零命令。 |
| AC3 安全 | **MET** | 掩码 + 无 value 的 automation peer + 复制快捷键拦截 + 关闭清空；253 文件扫描 0 命中。 |
| AC4 测试 | **MET** | 9 项 headless（put 参数/clear/冲突/已配置先确认/payload 契约/HostLocal 路由/接线/关闭清空/可见性回归）+ 真机截图 `real-app-masked.png`。 |
| AC5 回归/门禁 | **MET** | test.ps1 **198/198**（61/53/84）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）；check PASS；18 条 64-hex pin。 |

## UI 结构（`Views/CredentialSection.cs`，SettingsPage 右侧首卡）

```
凭据 · Credential
选择 provider / proxy 目标后输入 API Key 或代理密码；掩码显示，保存后立即清空。
目标                [ComboBox: "Provider API Key · <profile> · missing|configured" / "代理密码 · <network> · …"]
目标状态：…          （selected target 的 configured/missing；替换需二次确认）
凭据内容（掩码，不可复制明文）
                    [SecretTextBox  PasswordChar='●'  Watermark=粘贴或输入 API Key / 代理密码（掩码输入）]
[保存凭据] [清除凭据] [刷新状态]
状态/错误行          （typed code + 中文提示）
冲突确认行           [确认替换] [取消]     ← CREDENTIAL_CONFLICT / configured 目标时出现
```

调用链：`SettingsPage → IHostController（HostController）→ HostRuntime.Commands（HostCommandDispatcher）→ credential_put / credential_clear（HostLocal，CREDENTIAL-PORT-1 实现）`；状态读取 `settings_provider_profiles_list` / `settings_network_profiles_list` 的 `credential_state`，**未新增/修改任何 Host 命令**。

## Record Decision（安全输入与覆盖策略）

1. **输入控件**：自定义 `SecretTextBox : TextBox`——`PasswordChar='●'`、`ContextMenu/ContextFlyout=null`、`IsUndoEnabled=false`；`CredentialSection` 以 Tunnel 处理器吞掉 Ctrl+C / Ctrl+X / Ctrl+Insert；**不使用明文 TextBox**。
2. **真机截图发现的真实缺陷（值得记录）**：派生 `TextBox` 未覆盖 `StyleKeyOverride => typeof(TextBox)` 时，Avalonia 按自身类型找控件主题失败 → 测量 0×0，输入框完全不可见；headless 逻辑测试（直接设 `.Text` + 点击）全部通过也发现不了。已修复，并新增 headless 可见性回归测试（`masked-input-visible.json`：高 32 px）——这是 AC4「真机截图一次」的直接价值。
3. **intent 策略**：目标 missing → `credential_put intent="create"`；目标 configured → UI 先二次确认，确认后 `intent="replace"`；Host/Core 仍独立校验，冲突为 typed `CREDENTIAL_CONFLICT`（UI 同样显示确认行，确认后再发 replace）。
4. **状态来源**：复用 P15 profile list 的 `credential_state`（configured/missing），不新增命令、不改 Host 契约。
5. **secret 生命周期**：仅存在于掩码框 Text（提交瞬间读取并清空）、一次 dispatcher 的临时 payload、替换确认期间的 `_pendingSecret`（不渲染）；清除点=成功/失败/取消/切换目标/刷新/窗口关闭；从不写日志、证据、DB 或 automation 属性。
6. **失败呈现**：`CredentialOperationResult` typed 结果（Conflict/NotFound/InvalidArguments/Unavailable/NotReady/Failed），控制器层 catches 全部异常，不向 UI 抛出；错误行只显示 code + 中文提示。
7. **测试边界**：UI 测试用 fake 凭据端口（内存记录 put/clear 参数），**不写真实 Windows 凭据库**；真实 vault 两阶段由 CREDENTIAL-PORT-1 `CredentialPortTests` 覆盖；真机截图只键入非真实示范值、不点保存。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 put 参数 | `CredentialSection_Save_Create_SendsExactPutArguments_AndClearsMaskedInput` | Avalonia Headless 11.3.22；fake 端口 | (provider_api, profile-1, create, 22 字符) 精确；控件清空；状态 configured；peer 无 secret | `credential-ui/put-create.json` |
| AC1 clear | `CredentialSection_Clear_SendsExactClearArguments_AndShowsMissing` | 同上 | (proxy_auth, network-1)；状态 missing；列表刷新 | `credential-ui/clear.json` |
| AC2 冲突 | `CredentialSection_Conflict_ShowsTypedPrompt_AndReplaceNeedsSecondConfirmation` | 同上 | 1 次 create 得 CREDENTIAL_CONFLICT → 确认行 → 第 2 次 replace 同 secret | `credential-ui/conflict-replace.json` |
| AC2 先确认 | `CredentialSection_ConfiguredTarget_AsksBeforeSending_AndCancelSendsNothing` | 同上 | 确认前 0 调用；取消后 0 调用 | `credential-ui/configured-target-confirm.json` |
| AC1/AC3 契约 | `CopyShortcuts_AreBlocked_AndPayloadsMatchTheHostContract`、`Dispatcher_RoutesCredentialPutClear_ToTheHostLocalHandler...` | 无 UI / 无 sidecar | payload 键与 CREDENTIAL-PORT-1 契约一致；HostLocal 路由正确 | `credential-ui/payload-contract.json`、`test/results-app.trx` |
| AC1/AC2 接线 | `SettingsPage_WiresCredentialBlock_ToTheInjectedController` | FakeHostController | 2 目标、2 行、UI put 到 controller seam | `credential-ui/settings-wiring.json` |
| AC3 关闭清空 | `MainWindow_Closing_ClearsTheMaskedPlaintext` | Headless Window | Close 后掩码/待确认 secret 均空 | `credential-ui/window-close-clears.json` |
| AC4 真机截图 | Debug `NewManga.App.exe`（隔离数据根）→ 设置页 → 键入非真实示范值 | Windows 10.0.26300；1278×818 | 22 圆点掩码；UIA 仅 `Edit "凭据密码（掩码输入，不暴露明文）"`；未点保存 | `real-app-masked.png`、`real-app-screenshot.json`、`real-app-uia-observation.txt` |
| AC3 泄漏扫描 | 扫描 task-env evidence、`verification/CREDENTIAL-UI-1`、`%APPDATA%/com.newmanga.desktop/logs` | 253 文件 | 0 命中（marker 以 sha256 记录） | `security-scan.json` |
| AC5 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **198/198**（61/53/84），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC5 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2772P/9S（同一组 3 失败） | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CREDENTIAL-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/CREDENTIAL-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1`；delivery head `5b5d67fc5`。
- 复现：`verification/CREDENTIAL-UI-1/REPORT.md §6`。
- 前置：无 sidecar 需求（headless）；真机截图需桌面会话，用隔离 `NEWMANGA_DATA_ROOT`，不要点保存。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 重跑 test.ps1 复核（198/198，注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）→ 集成 → closeout。并发说明：本卡只改 `NewManga.App`（其它任务在 Host/CoreClient/Python），与 EXPORT-E2E-CLOSE-1 无文件冲突。

## 下一任务建议（必填）

- Task ID / 标题：**无必须由我立即释放的实现任务**；建议 DSH 释放「设置页 profile 管理 UI」（provider/network profile 的创建/编辑/删除表单），凭据区块已就绪、缺 profile 时当前只能提示先创建。
- 推荐 Agent / Reviewer：实现 = saber-ui-spec（Avalonia UI）；Reviewer = 未参与实现的 ZCode/Antigravity/Codex（DSH 排班）。
- 推荐原因与前置依赖：CREDENTIAL-UI-1 已完成凭据输入/清除，但没有 profile 管理入口时真实用户无法在 UI 内创建目标；依赖 P15 profile 命令面（已 66/0 全部实现）。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `5b5d67fc5`；base `6f6e4a678`。
- 允许修改路径：`apps/desktop-avalonia/**`、新任务卡、STATUS/PLAN/LEDGER、`verification/<新任务>/**`。
- 禁止范围：不改 Core 语义/协议/Host 契约/旧壳；不写真实 vault；不 push/gc/prune。
- 交付物：profile 管理 UI + headless 测试 + 真实截图 + 证据 + Handoff。
- 验证命令与完成 Gate：test.ps1 全绿（≥198）、vitest 60/567、pytest 无新增失败、`check.ps1 -TaskPath` PASS、64-hex pin、独立 Review。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 CREDENTIAL-UI-1（delivery 5b5d67fc5，walkthrough 见 doc/handoffs/CREDENTIAL-UI-1-handoff.md 与 verification/CREDENTIAL-UI-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 18 条 pin（sha256 与文件一致）；检查凭据区块只使用 SecretTextBox（无明文 TextBox）、automation peer 无 value、复制快捷键被拦、close/提交后明文清空；重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 198/198，注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 dotnet test --filter FullyQualifiedName~CredentialUiTests（应 9/9）；确认 evidence/log 扫描 0 命中、真机截图显示掩码圆点且未点保存；给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. **真实 vault 提交未在 UI 层真机执行**（卡面禁令）；真实两阶段由 CREDENTIAL-PORT-1 Host 测试覆盖；UI→Host 链路由 payload 契约 + HostLocal 路由测试钉住。
2. **真机截图时 Host 未就绪**：Debug 构建无 sidecars → 目标列表为空；掩码与安全属性已验证；配置真实 profile 后列表会显示 configured/missing（逻辑由 headless + P15 profile list 覆盖）。
3. **profile 管理 UI 缺失**：创建/编辑 provider/network profile 的表单属后续 Task。
4. **系统级 CredUI 未复刻**：采用页内掩码输入；若产品需要系统凭据 UI，另开 Task。
5. 需独立 Review（Owner 不得自审）。
