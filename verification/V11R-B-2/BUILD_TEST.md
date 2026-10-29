# V11R-B-2 构建与测试记录（I1/INT-0 共享基础设施后的复跑）

执行目录：`apps/desktop-avalonia`；证据文件：`build.log`、`test.log`（命令原样输出）。

## 1. 构建

```
dotnet build NewManga.sln -warnaserror --nologo
```

- exit code：**0**；`0 个警告，0 个错误`

## 2. 测试

```
dotnet test NewManga.sln -m:1 --no-build --nologo
```

- exit code：**0**
- 说明：`-m:1` 串行化测试项目。并行运行多个测试项目时，既有的 Host/CoreClient 集成测试会偶发争用同一临时目录的 SQLite `-shm` 文件（`IOException: 另一个程序已锁定文件的一部分`，非本任务改动引入；单项目/串行运行稳定通过）。串行运行是本仓库唯一可复现的绿色基线。

| 测试项目 | 通过 | 跳过 | 失败 | 总计 |
|---|---|---|---|---|
| NewManga.Host.Tests | 42 | 24 | 0 | 66 |
| NewManga.DesignSystem.Tests | 67 | 0 | 0 | 67 |
| NewManga.ThemeEngine.Tests | 229 | 0 | 0 | 229 |
| NewManga.App.Tests | 254 | 6 | 0 | 260 |
| NewManga.CoreClient.Tests | 42 | 25 | 0 | 67 |

跳过项为既有环境依赖用例（真实 sidecar / 冻结二进制），与本次改动无关。

## 3. 本任务测试（11 条，全部通过）

`tests/NewManga.App.Tests/V2ConsoleUiTests.cs`：

| 测试 | 覆盖 |
|---|---|
| `Console_HasNineSections_FiveRealAndFourHonestlyNotWired` | 9 分区、5 真实/4 待接入、待接入文案必含「能力待接入」、ConsoleView 真实在视觉树 |
| `Providers_CreateAndEdit_UseTheRealIpcDraft` | Provider 列表真实读取、创建走 `SaveProviderProfileAsync`、draft 字段/能力正确、刷新后行数 |
| `Credentials_DisplayStateOnly_AndTheSecretIsClearedAndNeverExposed` | 状态只显示已保存/未保存；保存调用一次后输入清空；**反射扫描所有 public string 属性不含 secret** |
| `DeleteProvider_RequiresConfirmation_AndCancelWritesNothing` | 删除需确认、影响面文案；取消/ Esc 不写；确认才调用 Host |
| `Network_TestAndDefault_UseTheRealHostSeams` | 网络测试传入 network/provider id、默认网络设置、TLS 关闭未确认时本地拒绝且零写入 |
| `NotWiredSections_ShowHonestBanner_AndBlockedDangerActionsAreCancelable` | ⑤⑥ 待接入 banner、危险确认可取消、阻断确认不执行 |
| `Appearance_TogglesRealDesignTokens_AndOpensThemeStudioSurface` | 深浅外观真实切换令牌、主题工作室入口打开真实表面、Esc 关闭 |
| `Diagnostics_ShowsHostFacts_AndExportHistoryWithoutPaths` | Host 事实、导出历史、揭示目录真实调用、不含 OS 路径 |
| `Console_FailedSave_RendersTypedCodeOnly_NoPathOrSecretInNotice` | 注入含路径+假 secret 的 Core Message，通知只含 typed code |
| `Tasks_LoadsRealRunSnapshotAndProjection_AndHonorsRunControlRules` | 真实快照/投影（状态/命令/作用域/进度/计数/阶段/任务行）；Restart 缺幂等键零调用；有键才调用；Stop 需确认、取消不写、确认执行；R-24：Console 与 StatusBand 共享 `RunStatusMonitor`，LoadRun 只产生 1 次快照/投影读取 |
| `Tasks_WithoutRunId_DoesNotFabricateAnything` | 无 run_id 时零 Host 调用、无伪造行、给出提示 |

## 4. 证据生成

```
# R-19：仓库证据唯一入口（脚本内部显式 NEWMANGA_EVIDENCE_SYNC=1）
pwsh -NoProfile -File ../../verification/V11R-B-2/curate.ps1
```

- 生成 8 张截图（R-19 唯一命名 `<TestName>--<name>.png`）；`conformance/v2-tokens-and-classes.json` 保留自 B-1 的静态扫描产物（B-2 无独立 conformance 测试）。
- 普通测试只写 `%TEMP%/newmanga-evidence/V11R-B-2/`，镜像仓库需显式 `NEWMANGA_EVIDENCE_SYNC=1`/`NEWMANGA_EVIDENCE_DIR`。

## 5. NOT RUN（环境限制）

| 项 | 原因 |
|---|---|
| 真实 Python Core sidecar 端到端（凭据入 OS vault、网络真实外网探针、Run 真实执行） | 本机无可用 Core sidecar/隔离数据根；UI 用 `FakeHostController`（真实 DTO 与命令记录）覆盖，IPC 调用参数/次数均有断言 |
| `MainWindow` 承载 Console 的启动截图 | 归 V11R-INT-1；`ConsoleView` 已在真实窗口 headless 渲染并经外壳 Ctrl+3 路由 |
| 真实逐个分区 DPI（125/150/200%）验证 | 需真实桌面；发布/INT-1 阶段覆盖 |
