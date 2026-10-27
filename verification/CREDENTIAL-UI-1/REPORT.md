# CREDENTIAL-UI-1 验证报告（设置页凭据 UI：安全输入 → credential_put/clear）

- Task：`doc/tasks/CREDENTIAL-UI-1.md`（team task-44）
- Branch / worktree：`task/CREDENTIAL-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/CREDENTIAL-UI-1`
- Base：`6f6e4a678`（卡面 `77eb7cfd6`，按 DSH 指令用当前 HEAD）
- 未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；未写真实 Windows 凭据库、未触碰真实 `%APPDATA%`（真机截图用隔离 `NEWMANGA_DATA_ROOT`）。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 安全输入 | **MET** | 设置页新增「凭据 · Credential」区块：目标选择（provider API / 代理密码，来自 Core profile list 的 `credential_state`）+ 掩码输入（Avalonia `TextBox.PasswordChar='●'`，无明文 TextBox）+「保存凭据」调 `credential_put`、「清除凭据」调 `credential_clear`、「刷新状态」；成功/失败为 typed 提示（configured/missing、`CREDENTIAL_CONFLICT`、`CREDENTIAL_STORE_UNAVAILABLE`、`INVALID_ARGUMENTS`、`CREDENTIAL_NOT_FOUND`、`HOST_NOT_READY`）。Headless 断言 put 参数 = kind/owner/intent/secret 精确匹配。 |
| AC2 状态显示 | **MET** | 目标行显示 `configured / missing`（不显示 secret）；`CREDENTIAL_CONFLICT` 有明确中文提示 + 二次确认（确认替换 / 取消），确认前不发任何命令。 |
| AC3 安全 | **MET** | 掩码框为 `SecretTextBox`（`PasswordChar='●'`、无 context menu/flyout、Ctrl+C/Ctrl+X/Ctrl+Insert 被隧道拦截、无 undo 历史）；自定义 automation peer **不暴露 ValuePattern / value**，真机 UIA 树只见 `Edit "凭据密码（掩码输入，不暴露明文）"`；提交/清除/切换目标/取消/窗口关闭均清空明文与待确认 secret；253 个证据/日志文件扫描 0 命中（marker 仅以 sha256 记录）。 |
| AC4 测试 | **MET** | Headless 9 项（输入→put 参数、清除→clear、冲突二次确认、已配置先确认/取消零调用、复制快捷键策略、payload 契约、dispatcher HostLocal 路由、SettingsPage 接线、窗口关闭清空、掩码框可见性回归）；**真机截图** `real-app-masked.png`（22 个圆点掩码 + UIA 观察）。 |
| AC5 回归/门禁 | **MET** | `scripts/test.ps1` **198/198 passed, 0 skipped**（coreclient 61 / host 53 / app 84）；vitest **60 files / 567 tests**；pytest **3F/2772P/9S**（与基线同一组 3 个失败，0 新增；pass 数随 HEAD 增长）；`check.ps1 -TaskPath` PASS；10 条 64-hex pin；Handoff 含 Record Decision。 |

## 2. UI 结构与安全设计

### 2.1 结构（`Views/CredentialSection.cs`，嵌入 `SettingsPage` 右侧首卡）

```
凭据 · Credential
选择 provider / proxy 目标后输入 API Key 或代理密码；掩码显示，保存后立即清空。
目标              [ComboBox: "Provider API Key · DeepSeek · missing" / "代理密码 · 公司代理 · configured"]
目标状态：…       （selected target 的 configured/missing；替换需二次确认时明确提示）
凭据内容（掩码，不可复制明文）
                  [SecretTextBox  PasswordChar='●'  Watermark=粘贴或输入…]
[保存凭据] [清除凭据] [刷新状态]
状态/错误行       （typed code + 中文说明）
冲突确认行        [确认替换] [取消]        ← 仅 CREDENTIAL_CONFLICT / configured 目标时出现
```

### 2.2 控制流（key 代码）

| 动作 | 行为 |
|---|---|
| 保存（target=misisng） | 读掩码框 → 立即清空控件 → `credential_put {target, intent:"create", secret}` → 成功则刷新列表显示 configured |
| 保存（target=configured） | 不发命令，先显示二次确认；用户点「确认替换」才发 `intent:"replace"`；取消则丢弃 secret、零调用 |
| Host 返回 `CREDENTIAL_CONFLICT` | 明确提示 code + `确认替换/取消`；确认后发 `intent:"replace"` |
| 清除 | `credential_clear {target}` → 成功刷新为 missing；失败 typed 提示 |
| 关闭窗口/离开/切换目标 | `ClearSecrets()` 清空掩码框、`_pendingSecret=null`、关掉确认行 |

### 2.3 安全核对（AC3）

- **无明文 TextBox**：凭据 UI 唯一输入控件是 `SecretTextBox`（`PasswordChar='●'`）；代码中不存在把 secret 绑定到普通 `TextBlock`/`TextBox` 的路径。
- **不可复制明文**：`ContextFlyout=null`、`ContextMenu=null`；`CredentialSection` 以 Tunnel 处理器吞掉 Ctrl+C / Ctrl+X / Ctrl+Insert（有 headless 单测 `CopyShortcuts_AreBlocked_...`）。
- **不进 UI 自动化树**：`SecretTextBox.OnCreateAutomationPeer()` 返回自定义 `ControlAutomationPeer`（无 `IValueProvider`）；真机 UIA 观察确认 Edit 仅暴露固定名称、无 value；`type_text` 探测也因无 ValuePattern 无法回读（日志原文见 `real-app-uia-observation.txt`）。
- **不进日志/DB/证据**：Evidence 只写布尔/长度/code；扫描 253 个文件 0 命中；Host 侧 `HostCredentialCoordinator` 本就只写 `owner_hash` 证据（CREDENTIAL-PORT-1 已验证）。
- **关闭后不留明文引用**：`SettingsPage.ClearCredentialSecrets()` 在 `MainWindow.OnClosed` 调用；掩码框 Text 立即清空；待确认 secret 置 null；headless 窗口关闭测试断言。

### 2.4 状态来源（不改 Host 契约）

`configured / missing` 直接读既有命令 `settings_provider_profiles_list` / `settings_network_profiles_list` 的 `credential_state` 字段（Core P15 面，minor 7）。本卡**没有新增/修改任何 Host 命令**，`credential_put`/`credential_clear` 仍是 CREDENTIAL-PORT-1 的 HostLocal 实现；UI 只负责构造与 CREDENTIAL-PORT-1 `CredentialPortTests` 完全一致的 payload（headless payload 契约测试 + dispatcher fake hostLocal 路由测试双重锁定）。

## 3. Record Decision（安全输入与覆盖策略）

| 项 | 决定 | 依据 |
|---|---|---|
| 输入控件 | 自定义 `SecretTextBox : TextBox`（PasswordChar 掩码 + 自定义 peer + 复制拦截），不用明文 TextBox | AC1/AC3 |
| 掩码框 theme | 覆盖 `StyleKeyOverride => typeof(TextBox)` | **真机截图发现**：不覆盖时派生控件解析不到 TextBox 控件主题，测量为 0×0 完全不可见；headless 逻辑测试发现不了。已加 headless 可见性回归测试 `masked-input-visible.json` |
| 保存 intent | 目标 missing → `create`；目标 configured → 先二次确认再 `replace`；Host 仍会独立校验 intent/状态，冲突为 typed `CREDENTIAL_CONFLICT` | 与旧壳两阶段一致，state 以 Core 为准 |
| 替换确认 | UI 内二次确认（确认替换/取消），非系统模态框 | AC2；不新增系统对话框依赖，便于 headless 覆盖 |
| 秘密生命周期 | 只存在于掩码框 Text（提交瞬间读取并清空）、一次 dispatcher payload（Host 需要）、替换确认期间的 `_pendingSecret`；清除点=成功/失败/取消/切换目标/关闭窗口；不写日志/证据/自动化属性 | AC3 |
| 目标列表 | 复用 P15 profile list（provider + network），不新增命令 | 不改 Host 契约 |
| 测试边界 | UI 用 fake 凭据端口（不写真实 vault）；真实 vault 端到端由 CREDENTIAL-PORT-1 `CredentialPortTests` 覆盖；真机截图**不点击保存**，只用非真实示范值验证掩码显示 | 卡面「测试用 fake store，不要写真实 Windows 凭据库」 |
| 失败呈现 | 全部映射为 typed 结果（`CredentialOperationResult`），从不向 UI 抛异常；错误行只显示 code + 中文提示，不含 secret | AC1 typed 提示 |

## 4. 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 输入→put | `[AvaloniaFact] CredentialSection_Save_Create_SendsExactPutArguments...` | Avalonia.Headless 11.3.22；fake 端口 | put 参数 (provider_api, profile-1, create, 22 字符) 精确匹配；掩码框提交后为空；状态 configured | `credential-ui/put-create.json` |
| AC1 清除→clear | `CredentialSection_Clear_SendsExactClearArguments_AndShowsMissing` | 同上 | clear 参数 (proxy_auth, network-1)；状态 missing；列表刷新 | `credential-ui/clear.json` |
| AC1/AC2 冲突 | `CredentialSection_Conflict_ShowsTypedPrompt_AndReplaceNeedsSecondConfirmation` | 同上 | 第一次 put=create 得 `CREDENTIAL_CONFLICT` → 确认行可见 → 第二次 put=replace 同 secret | `credential-ui/conflict-replace.json` |
| AC2 已配置先确认 | `CredentialSection_ConfiguredTarget_AsksBeforeSending_AndCancelSendsNothing` | 同上 | 确认前 0 次调用；取消后 0 次调用 | `credential-ui/configured-target-confirm.json` |
| AC3 复制/契约 | `CopyShortcuts_AreBlocked_AndPayloadsMatchTheHostContract` | 无 UI | Ctrl+C/X/Insert 拦；put/clear payload 与 Host 契约一致；typed 映射 | `credential-ui/payload-contract.json` |
| AC3 dispatch 路由 | `Dispatcher_RoutesCredentialPutClear_ToTheHostLocalHandler...` | 无 sidecar | `credential_put`/`credential_clear` 均路由 HostLocal 且 payload 正确 | `test/results-app.trx` |
| AC1/AC2 接线 | `SettingsPage_WiresCredentialBlock_ToTheInjectedController` | FakeHostController | 2 个目标、2 行列表、UI put 到达 controller seam | `credential-ui/settings-wiring.json` |
| AC3 关闭清空 | `MainWindow_Closing_ClearsTheMaskedPlaintext` | Headless Window | Close 后掩码框空、pending secret 清空 | `credential-ui/window-close-clears.json` |
| 可见性回归 | `SecretTextBox_RendersThroughTheTextBoxTheme_NotCollapsed` | Headless Window measure | 掩码框 ≥ 24 px 高（防 0×0 复归） | `credential-ui/masked-input-visible.json` |
| AC4 真机截图 | Debug 构建 `NewManga.App.exe`（隔离 `NEWMANGA_DATA_ROOT`），导航设置页，键入非真实示范值 | Windows 10.0.26300；核心 1278×818 | 掩码 22 圆点；UIA 仅 `Edit "凭据密码（掩码输入，不暴露明文）"`；未点击保存 | `real-app-masked.png`、`real-app-screenshot.json`、`real-app-uia-observation.txt` |
| AC3 泄漏扫描 | 扫描 task-env evidence、`verification/CREDENTIAL-UI-1`、`%APPDATA%/com.newmanga.desktop/logs` | 253 文件 | **0 命中**（marker 以 sha256 记录） | `security-scan.json` |
| AC5 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **198/198**（61/53/84） | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC5 vitest | `cd apps/desktop/frontend && npm test`（主仓；旧壳未改） | 旧壳未改 | **60 files / 567 tests** | `test/vitest.log` |
| AC5 pytest | `PYTHONPATH=src python -m pytest -q`（worktree，未改 Python） | 未改 Core | **3F/2772P/9S**（与基线同一组 3 个失败，0 新增） | `test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CREDENTIAL-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 5. 遗留 / 未关闭项（记录不阻塞）

1. **真实 Windows vault 提交未在 UI 层真机执行**：按卡面禁令，测试与截图都不写真实凭据库；两阶段真实 vault 端到端由 CREDENTIAL-PORT-1 `CredentialPortTests`（随机 marker + finally 删除）覆盖。UI→Host 的真实链路由 payload 契约 + dispatcher HostLocal 路由测试钉住。
2. **真机截图时 Host 未就绪**：Debug 构建未携带 sidecars，真实 Host 启动失败 → 目标列表为空（界面显示「未发现可配置的 provider / proxy 目标」）。目标是验证掩码显示与安全属性，不涉及真实 vault；配置真实 profile 后列表会显示 configured/missing（逻辑由 headless + P15 profile list 覆盖）。
3. **profile 管理 UI 仍缺**：本卡只做凭据输入/清除；创建/编辑 provider/network profile 的表单属后续设置页 Task。
4. **代理密码目标**：选择 proxy target 后走同一 `credential_put`（target.kind=proxy_auth）；真实代理认证链路由既有导出/网络面覆盖，本卡未新增网络调用。
5. **系统级 CredUI**：未复刻旧壳 CredUI 对话框；采用页内掩码输入（更可控、可 headless 验证）。若产品需要系统凭据 UI，另开 Task。
6. 需独立 Review（Owner 不自审）。

## 6. 复现

```pwsh
# 1) 全量回归（198 项，含 9 项凭据 UI headless）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\CREDENTIAL-UI-1\evidence

# 2) 只看凭据 UI 测试
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~CredentialUiTests"

# 3) 真机截图复现
$env:NEWMANGA_DATA_ROOT='G:\CODEX\New Manga.workspace\task-envs\CREDENTIAL-UI-1\screenshot-root'
Start-Process apps/desktop-avalonia/src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe
# 导航「设置」→ 凭据区块 → 在掩码框键入任意非真实值（不要点保存）
```
