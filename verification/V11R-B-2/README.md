# V11R-B-2 证据：Console 空间（设置中心 9 分区）

- Task: `doc/tasks/V11R-B-2.md`（task-6，Owner `ui-shell`）
- 更新：2026-10-30（B-2-I2 收口：R-24 轮询恢复、R-23 中性词表、证据重生成）
- Branch: `v11r/ui-shell`；已合入 `main`（V11R-A-2 `IRunController`、V11R-A-1 `CreateChapterAsync`、V11R-D-1 M0、V11R-INT-0/INT-1）
- 视觉权威：DESIGN_SYSTEM.md + tokens.json（经 `NewManga.DesignSystem`）；屏幕规格：SCREEN_SPECS §5
- 渲染方式：Avalonia Headless + Skia（`UseHeadlessDrawing=false`），`[AvaloniaFact]` 真窗口 `CaptureRenderedFrame()`（每张 PNG > 4KB 断言）

## 1. 交付内容

| 文件 | 说明 |
|---|---|
| `ViewModels/V2/Console/ConsoleItems.cs` | 分区项、Provider/Network/凭据/能力绑定/导出历史行、Run 阶段与任务行、状态词表映射 |
| `ViewModels/V2/Console/ConsoleViewModel.cs` | 9 分区状态机；Provider/Network/凭据/绑定/导出历史真实 IPC；Run 快照/投影（`IRunController`，经壳共享 `RunStatusMonitor`；R-24：与 StatusBand 同源、单一 poller，不再私有 timer）；危险动作确认；凭据遮蔽；诚实未接入文案 |
| `Views/V2/Console/ConsoleView.axaml(.cs)` | 左 9 分区索引 + 右内容：①Run 表 ②Provider 与凭据 ③网络与代理 ④--⑦能力待接入 ⑧诊断与日志 ⑨外观入口 |
| 壳接线（同 Owner 的 B-1 工作域） | `ViewModels/V2/Shell/AppShellViewModel.cs`（Console VM 单例、进入惰性加载、控制台面包屑/分区导航）、`Views/V2/Shell/V2WorkspaceHost.axaml`（真实 ConsoleView 替换占位） |
| `Shell/V2/Statuses.cs` | Lead 裁决：`queued` 符号 = `·`（DESIGN_SYSTEM §2.2 权威） |

### 九个分区与真实度

| # | 分区 | 真实数据源 | 状态 |
|---|---|---|---|
| 01 | 任务与队列 | `IRunController.GetRunSnapshotAsync` / `GetTaskProjectionAsync`（V11R-A-2）+ 控制/恢复/重试（`ControlRunAsync`/`ResumeBlockedRunAsync`/`RetryFailedTargetsAsync`） | 真实；契约无「List Run」，必须显式输入 run_id；由壳 `RunStatusMonitor` 单一 poller 统一快照/投影（R-24，与 StatusBand 共享） |
| 02 | Provider 与凭据 | `ListProviderProfilesAsync`/`SaveProviderProfileAsync`/`DeleteProviderProfileAsync`；`ListCredentialTargetsAsync`/`PutCredentialAsync`/`ClearCredentialAsync`；`SetProviderBindingAsync`/`ClearProviderBindingAsync`/`ResolveProviderBindingAsync` | 真实 |
| 03 | 网络与代理 | `ListNetworkProfilesAsync`/`SaveNetworkProfileAsync`/`DeleteNetworkProfileAsync`/`SetNetworkDefaultAsync`/`TestNetworkProfileAsync`/`ResolveNetworkProfileAsync` | 真实（含 TLS 关闭确认规则） |
| 04 | 模型与设备 | 无 Host 设备命令（打包 VERSION.json 由 Host 拥有，UI 不直读文件） | 能力待接入 |
| 05 | 缓存与版本清理 | `cleanup_preview`/`cleanup_run` 在命令注册表但 `IHostController` 无方法 | 能力待接入 + 危险确认（确认禁用、原因可见） |
| 06 | 备份与恢复 | `backup_list`/`backup_create` 同上 | 能力待接入 + 创建/删除确认（可取消、确认禁用） |
| 07 | 插件与 Hooks | `plugins_list`/`plugins_set_enabled` 同上 | 能力待接入，无假开关 |
| 08 | 诊断与日志 | Host `Snapshot`（状态/模式/错误码/帧数）+ `GetExportHistoryAsync` + `RevealExportFolderAsync` | 真实；日志查看/诊断包导出能力待接入 |
| 09 | 外观 | `DesignSystemThemeManager` 深浅切换真实生效；主题工作室入口打开真实表面栈（内容属 V11R-C-2） | 真实入口 |

## 2. 安全属性（AC1 重点）

1. **凭据永不回显 secret**：UI 只保存/显示 Core 的 `credential_state`（已保存/未保存）；输入框为 `PasswordChar="*"` 的瞬态值，保存成功后立即清空；错误仅显示 typed code。测试 `Credentials_DisplayStateOnly_AndTheSecretIsClearedAndNeverExposed` 通过反射遍历行与 VM 的所有 public string 属性断言不含 secret 原文。
2. **错误文本不含路径/secret**：保存/控制失败只渲染 `SettingsProfileStatus`/`CredentialOperationStatus` 映射 + typed code；测试 `Console_FailedSave_RendersTypedCodeOnly_NoPathOrSecretInNotice` 注入含 `C:\...` 与假 secret 的 Core Message，断言通知里两者都不出现。诊断区明确说明「不渲染可能含路径的原始错误文本」。
3. **危险动作二次确认可取消**：删除 Provider/网络配置、清除密钥、停止 Run、清理缓存（阻断态）、创建/删除备份（阻断态）全部走壳层 `ConfirmRequest`：默认焦点在「取消」，写明后果与影响面（如「能力绑定会立即失效」「不可撤销」「未完成页需重跑」），阻断态确认按钮禁用并给出原因且不产生任何写入。测试覆盖取消/ Esc / 确认三条路径。
4. **不做假开关**：未接入分区无 toggle，只显示 `AlertBanner` + 前置条件；阻断态危险按钮点击只弹确认（禁用确认）并提示「能力待接入，未执行任何删除」。
5. **R-08 幂等键**：Restart / 重试失败目标必须由操作方填写幂等键；缺失时本地拒绝并提示，UI 不静默生成（测试断言缺失时零 Host 调用）。

## 3. 截图（`screens/`，真实 headless 渲染）

| 文件 | 证明 |
|---|---|
| `<TestName>--01-console-providers.png` | 9 分区索引 + Provider 列表 + 凭据（掩码输入、只显示已保存/未保存）+ 能力绑定 |
| `<TestName>--02-console-credentials-state-only.png` | 凭据状态行（保存后状态变为已保存，secret 已清空） |
| `<TestName>--03-console-network.png` | 网络配置行（模式/端点/TLS/默认）+ 真实连通测试结果 + 默认网络解析 + TLS 关闭确认规则 |
| `<TestName>--04-console-storage-not-wired.png` | 能力待接入 banner + 接入前置条件 + 阻断态危险按钮 |
| `<TestName>--05-console-appearance-light.png` | 外观真实切换为浅色（整窗令牌切换）+ 主题工作室表面入口 |
| `<TestName>--06-console-diagnostics.png` | Host 状态事实（真实）+ 导出历史（真实）+ 日志/诊断包能力待接入 |
| `<TestName>--07-console-tasks-run.png` | 真实 Run 状态/计数/阶段流/任务行 + 控制按钮可用性 + 幂等键 |
| `<TestName>--08-console-danger-confirm-blocked.png` | 危险确认（阻断态）：写明影响面、确认禁用、原因「能力待接入」 |

> 实际文件名带 R-19 唯一化前缀 `<TestName>--`。壳入口（Ctrl+3 进入控制台）截图由 B-1/INT-0 证据覆盖，B-2 不再重复。

## 4. 命令

```
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror          # 见 BUILD_TEST.md
dotnet test NewManga.sln -m:1 --no-build        # 见 BUILD_TEST.md（串行避免既有测试临时目录争用）

# R-19：仓库证据唯一入口（脚本内部显式 NEWMANGA_EVIDENCE_SYNC=1）
pwsh -NoProfile -File ../../verification/V11R-B-2/curate.ps1
```

| 证据 | 内容 |
|---|---|
| `BUILD_TEST.md` + `build.log` + `test.log` | 命令、exit code、汇总（含 I1/INT-0 后全量计数） |
| `curate.ps1` | R-19 唯一证据生成入口（8 张截图） |
| `conformance/v2-tokens-and-classes.json` | 全部 `Nm.*` 键（含 Console 新增）与 Classes 词表（静态扫描生成） |
| `NOT_WIRED.md` | 未接入能力清单（4 个分区 + 细节） |
| `DEVIATIONS.md` | 与规格偏差及理由 |
| `AC_COVERAGE.md` | AC1–AC7 → 代码/测试/截图映射 |

## 5. 测试（`tests/NewManga.App.Tests/V2ConsoleUiTests.cs`，13 条全绿）

分区真实度（5 真实/4 待接入）、Provider 创建走真实 draft、凭据不回显 + 反射扫描、删除 Provider 取消/ Esc / 确认三条路径、网络测试+默认+ TLS 规则、未接分区阻断危险确认、外观真实切换+主题工作室表面、诊断 Host 事实+导出历史+揭示目录、失败保存只渲染 typed code、Run 快照/投影+控制规则、无 run_id 不伪造。

I2 新增：
- `R24_ConsoleRunPolling_PausesOnLeave_AndResumesOnReentry`：加载 Run → 离开 Console 暂停共享 poller → 切回恢复订阅并立即产生一次共享快照/投影读取（可观测计数器，无 sleep 竞态）。
- `R23_WiringAndSavedStates_UseNeutralVocabulary_NotSevenStateStatus`：分区「已接入/待接入」、凭据「已保存/未保存」、能力绑定「已绑定/未绑定」均为中性 metadata；API 上已移除 `Status`/`StateStatus`/`BindingStatus`，文本不落入七态词表。

另 B-1/INT-0 全部回归通过（V2 合计 145 条）。
