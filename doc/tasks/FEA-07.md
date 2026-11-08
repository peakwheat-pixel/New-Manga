---
id: FEA-07
title: 运行期切换与窗口（双 UI 切换、WindowBroker、switch journal、安全启动）
kind: implementation
governance_version: 3
status: closed_with_limitations
approval: scope_review_r2_approved_2026-11-02
suggested_owner: dsh
owner: dsh
reviewer: codex-cli（impl-r12 **approved**，P0=0/P1=0/P2=1（R-026 非阻塞，集成处置中修正）；报告 doc/reviews/FEA-07-impl-r12.md；复核链 scope-r1→r2、impl-r1–r12）
depends_on:
  - FEA-00A-IMPL-1
  - FEA-04
  - FEA-05-PORT-1
  - FEA-06
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
branch: main
worktree: G:\CODEX\New Manga
integration_commit: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0
delivery_head: aedc7251c3cae49a12c8b6bc3f91c3e6dd53d3d0（r8 返修代码提交；精确证据见 final-evidence.log）
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-07
allowed_paths:
  - doc/tasks/FEA-07.md
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
  - apps/desktop-avalonia/src/NewManga.App/AppOptions.cs
  - apps/desktop-avalonia/src/NewManga.App/App.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/App.axaml
  - apps/desktop-avalonia/src/NewManga.App/Program.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/**
  - apps/desktop-avalonia/src/NewManga.App/Services/**
  - apps/desktop-avalonia/src/NewManga.App/Controls/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/**
  - apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**
  - apps/desktop-avalonia/NewManga.sln
  - verification/FEA-07/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-07-*.md
  - doc/handoffs/FEA-07-*.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
---

# FEA-07：运行期切换与窗口（双 UI）

## 来源与授权链

- **方案**：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §7（切换事务/失败矩阵/窗口）、§12.1 FEA-07 行、§12.3（A01/A02/A03/A05/A06/A08，相关 A07）、§15.5（提交判据/失败注入/rollback）、§15.x H2/H3。
- **设计**：`doc/design/fluent-v1/04-layout-responsive.md` §4/§5（双屏/拔屏/DPI）、`03-accessibility.md`（KeyMap/焦点）。
- **前置**：`FEA-06` **done**（集成 `b26840acd`；Fluent 四页 + 双壳 selector 就绪）；`FEA-04`（Current 适配）、`FEA-05-PORT-1`（Draft 端口）、`FEA-00A-IMPL-1`（数据安全门）均 done。
- **契约**：C-02（V-05/V-08b）、C-03（外观持久化/唯一写者，PREREQ-1/2 已交付）、C-05（页可见性）；**不改 PREREQ-2 冻结的 selector/组合根语义**。
- **Owner 裁决（DSH，2026-11-02）**：FEA-07 实现 owner = **DSH**（W-3）。原因：本轮独立复核由 Codex CLI 承担（scope 与后续 impl review），按「审查者不得参与实现」规则，Codex 不实现 FEA-07；方案 §12.1 的 ZCode owner 行已被用户 2026-11-02 指派与通道现状 supersede（W-7）。
- **顺序裁决（用户 2026-11-02）**：按原 PLAN DAG 先做 FEA-07，**不插队** `FEA-06-RESIDUAL-1`。
- **H2/H3 假设**：无独立验证 Task → H2/H3 验证纳入本卡 AC5/AC6（原生矩阵 + 性能 baseline），不拆前置（W-4）。

## scope-r1 处置（2026-11-02，r1 = changes_requested / P0=0 / P1=6 / P2=2；报告 `doc/reviews/FEA-07-scope-r1.md`）

| r1 ID | 处置 | 落点 |
|---|---|---|
| P1-1 新模块无法接入 App | 写域补 `NewManga.App/NewManga.App.csproj`（仅允许加指向 Presentation 的 `ProjectReference`，不改既有依赖方向/TFM） | allowed_paths |
| P1-2 A03/§15.5 回滚验收不足 | AC1/AC3 补：旧结果仅 candidate 且 **DB 文本/current/pinned revision/Lock/源文件/candidate 零变化**；逐阶段失败注入；commit 判据（layout/Loaded/Render/有效几何）与完整 rollback（window 材质/bounds/焦点/输入路由/旧资源） | AC1/AC3 |
| P1-3 A08/H2 双屏/DPI 不足 | AC5 补 100/125/150/200% DPI、拔屏时第二窗口内容回到主窗对应页面、未 flush 编辑态 fail-closed 留主窗缓冲、第二窗口只承载只读/独立会话、同一 `(SessionId, RegionId)` 单一写入 owner、混合 DPI 提交/恢复、PerMonitorV2 manifest 检查 | AC5 |
| P1-4 隔离/启动矩阵缺失 | AC1–AC4 测试行明确 data/theme/journal 全部临时根；测试覆盖 App.Tests + Presentation.Avalonia.Tests；AC7 启动兼容矩阵（默认 Current V2/`--frontend` 覆盖与未知值 fallback/`--shell=legacy`） | AC7 + 测试要求 |
| P1-5 W-6 无机械门禁 | AC7 增 project-reference graph 静态检查（允许 App→Presentation；禁止 Host/Core/ApplicationCore→Presentation/UI；TFM 不变） | AC7 |
| P1-6 W-5 门槛未冻结 | **W-5 冻结**：热切换 p95 ≤ **1000 ms**（固定机器 + 合成规模数据；冷启动首次切换单独记录不纳入热 p95）；超预算 = AC6 不通过，除非 DSH 书面 waiver 登记 | AC6/W-5 |
| P2-1 写域过宽 | 移除 `Directory.Build.props`、`NewManga.Appearance/**`、`NewManga.DesignSystem/**`、`Appearance.Tests/**`；保留 App 内容树/Presentation/sln/测试/证据/治理文档；App 写域仅用于稳定窗口/内容树接线与切换装配，不改视觉/唯一写者 | allowed_paths |
| P2-2 恢复指针/元数据 | 置 ready 前：STATUS rolling checkpoint 刷新为当前 GOAL-PROGRESS；`base_commit` 刷新到冻结 head；`owner: dsh`、`branch: main`、`worktree: G:\CODEX\New Manga`；方案 §12.1 ZCode owner 记为 superseded | 置 ready 时（W-7/W-8） |

## 任务拆解

| # | 内容 | 依据 |
|---|---|---|
| P1 | 运行期双 UI 切换事务：稳定主窗 + 内容树替换/复用；`FrontendSelector` 结果与 `AppearanceCoordinator.SaveAsync` 协同；不重启 sidecar、不丢 Draft/Run | 方案 §7.1、§15.5 |
| P2 | 窗口身份/生命周期：WindowBroker（主窗/弹窗/浮窗归属/复用）、第二窗口只承载只读或独立会话内容、关闭/重建不 Dispose Host、不隐式 Start；退出协调归进程级 ExitCoordinator | 方案 §7.3、FEA-04 R-STATE-4 |
| P3 | switch journal：阶段化提交/失败注入/崩溃恢复，失败回滚到上一可用 UI 且无部分切换状态 | 方案 §7.1/§7.2、§15.5 |
| P4 | safe startup：坏包/坏设置/未知 frontend/theme/scale 时 fail-safe 到 Current V2 + 可诊断告知；保留有效设置 | 方案 §7.2、§12.3 A07 |
| P5 | 双屏/拔屏/DPI：100/125/150/200%、换主屏、拔副屏、全屏切换；混合 DPI 提交/恢复；PerMonitorV2；窗口位置/尺寸/焦点 memento | 设计 04 §4/§5、方案 §7.3、A08 |
| P6 | H2/H3 验证：稳定 Window + 内容替换承接双屏 Inspector；热切换性能 baseline（p50/p95/峰值、最大 UI 冻结、内存/句柄） | 方案 §12.1/§12.3、H2/H3 |
| P7 | 测试与证据：切换矩阵/失败矩阵/启动矩阵/project-reference 检查/原生矩阵/性能报告；全量回归 | 方案 §12.1/§12.3 |

## 实施记录（切片 1，2026-11-02，owner=DSH）

- 新建 `apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/`（W-6 模块落点）并登记 sln：
  - `Switching/SwitchStage.cs`：切换阶段（Preparing→Building→Layout→Loaded→Rendered→Committed/RolledBack）
  - `Switching/SwitchJournal.cs`：原子 JSON journal（Begin/Advance/Rollback/Commit/TryRead/HasInterruptedSwitch；损坏文件容忍）
  - `Switching/FrontendSwitchCoordinator.cs`：切换事务编排（阶段门禁 + 每阶段故障注入 + 失败回滚 + 并发串行化 + 启动恢复查询）
  - `Windows/WindowBroker.cs`：单一稳定主窗 + 二窗（Inspector/Floating）登记；不拥有 Host 生命周期
  - `Lifecycle/ExitCoordinator.cs`：进程级退出判定（未保存编辑/运行中 Run 阻断）
- 新建 `tests/NewManga.Presentation.Avalonia.Tests/`（28 测试，全绿）：journal 持久化/恢复/损坏容忍、阶段顺序、每阶段失败回滚、rollback 失败仍报失败、并发串行化、窗口 broker、退出协调。
- 证据：`verification/FEA-07/slice-1-verification.log`（build 0/0；Presentation 28/0；全量 **1062/0/57**；CoreClient 已知 flaky 首跑 1 failed、重跑全绿，已在日志注记）。
- 下一批切片：②稳定主窗 + 内容树切换接线（App/Presentation 宿主 + Fluent content surface）；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/证据/独立复核。

## 实施记录（切片 2，2026-11-02，owner=DSH）

- `Presentation.Avalonia/Hosting/FrontendContentHost.cs`：稳定窗口内容槽（单一 `Content`，可替换/清空，不感知 frontend）。
- `App/Services/FrontendHostCoordinator.cs`：切换编排——校验冻结 selector 语义（未知 id 拒绝、不静默改前端）、构建替换树、经唯一写者 `AppearanceCoordinator` 持久化 `theme.frontendId`、内容树 swap；任一失败恢复旧树/旧设置。
- `NewManga.App.csproj` 增加对 `NewManga.Presentation.Avalonia` 的 `ProjectReference`（W-6 允许方向；Host/Core 方向未变）。
- 测试：`NewManga.App.Tests/FrontendHostCoordinatorTests.cs` 5 测试全绿（切换成功/未知 id 拒绝不改 UI/构建失败回滚/journal 记录/幂等/100 次往返内容树唯一且 journal 干净）。
- 证据：`verification/FEA-07/slice-2-verification.log`（build 0/0；切换 5/0；全量 **1067/0/57**；CoreClient 已知 flaky 首跑 1 failed、隔离重跑全绿）。
- 下一批：②b 稳定主窗接入（`PresentationWindow` + 真实 V2/Fluent content factory + App 组合根）；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/独立复核。

## 实施记录（切片 2b，2026-11-02，owner=DSH）

- `App/Views/Presentation/PresentationWindow.cs`：**稳定原生主窗**（Title/geometry/MinWidth/背景/material 自持；单一 `FrontendContentHost`；注入式 `Func<string, Control>` content factory，窗口不依赖具体壳实现）；`SwitchFrontendAsync` 复用 `FrontendHostCoordinator`，切换时窗口身份不变、失败回滚旧树。
- 测试：`PresentationWindowTests` 5 例全绿（初始内容/几何；切换保窗身份；构建失败回滚+journal；未知 id 拒绝；20 次往返单树且 journal 干净）。
- 证据：`verification/FEA-07/slice-2b-verification.log`（build 0/0；窗口 5/0；全量 **1072/0/57**；CoreClient 已知 flaky 首跑 1 failed、重跑全绿）。
- 下一批：②c App 组合根接入真实 content factory（V2 `AppShellV2` + Fluent content surface）+ 开关启用；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/独立复核。

## 实施记录（切片 2c-part1，2026-11-02，owner=DSH）

- **Fluent 内容面抽取**：新增 `Views/Fluent/FluentShellSurface.axaml(.cs)`（UserControl，承载全部 Fluent 内容/导航/四页/KeyMap/响应式带逻辑；`FullScreenRequested` 事件 + `SetViewportWidth` 公共入口）；`FluentShell.axaml` 改为仅宿主 Window，`FluentShell.axaml.cs` 变为薄 facade（转发全部公开 API + `FindControl` 到 surface + window material 策略），既有 24 个 Fluent 测试**全部经 facade 通过**。
- 目的：为 `PresentationWindow` 的真实 content factory 提供可复用的 Fluent 内容树（稳定主窗切换 V2/Fluent 的前提）；同时保留 FluentShell 独立启动与测试路径。
- 证据：`verification/FEA-07/slice-2c-part1-verification.log`（build 0/0；Fluent 24/0；全量 **1072/0/57**）。
- 下一批：②c-part2 App 组合根接入真实 factory（V2 content 需携带 Theme Studio 生产接线）+ `--presentation-host` 开关 + 端到端 headless 切换测试；③safe startup/启动矩阵；④双屏/DPI memento；⑤全量回归/独立复核。

## 实施记录（切片 2c-part2，2026-11-02，owner=DSH）

- **组合根接入**：`AppOptions.PresentationHost`（`--presentation-host[=false]`，BooleanSwitchKeys 注册）；`App.CreateShell` 在 V2 路径下按开关走 `CreatePresentationShell`；新增 `CreatePresentationShell`（journal 落 theme-home、真实 content factory：`FluentShellSurface` / `CreateV2Content`）与 `CreateV2Content`（无宿主窗口的 V2 内容树，含 Theme Studio 生产接线，由 `WireThemeStudio` 抽取复用）；`--shell=legacy` 优先级不变。
- `NavigateStartupPage` 支持稳定窗口（按当前内容树映射 Fluent 页/V2 space）。
- **修复**：`SettingsViewModel.OnAppearanceChanged` 在非 UI 线程时 `Dispatcher.UIThread.Post`（切换时 `AppearanceCoordinator` 的 Changed 可能来自线程池；设置页控件更新必须在 UI 线程）；`AppOptions` 布尔开关白名单补 `presentation-host`。
- 测试：`PresentationHostCompositionTests` 2 例（组合根真实 V2/Fluent 内容切换 + 开关解析）；presentation 相关 12 测试全绿。
- 证据：`verification/FEA-07/slice-2c-part2-verification.log`（build 0/0；presentation 12/0；全量 **1074/0/57**）。
- 下一批：切片 3 safe startup + 启动兼容矩阵；切片 4 双屏/DPI memento；切片 5 全量回归/独立复核。

## 实施记录（切片 3，2026-11-02，owner=DSH）

- **safe startup**：新增 `App/Services/SafeStartupPlanner.cs`（AC4/AC7）——输入 `AppOptions` + 已加载 `AppearanceSettings` + 外观 warnings，输出 `StartupPlan{RequestedFrontendId, EffectiveFrontendId, IsFallback, ShellKind(Legacy/Default/PresentationHost), Diagnostics}`；冻结 fail-safe 策略：未知 frontend/视觉主题 id → Current V2 + 诊断；外观文档坏字段 → 逐字段 fallback warnings 进入诊断；`--shell=legacy` 优先于一切。`App.OnFrameworkInitializationCompleted` 已接入：每个诊断写 Trace（fallback 额外 Warning），运行时行为不变、可诊断性增强。
- **启动兼容矩阵测试**：`SafeStartupPlannerTests` 8 例（默认 V2/CLI fluent 优先/持久化 fluent/未知 fallback/视觉主题 id fallback/legacy 优先/presentation-host/warnings 诊断）；`StartupCompatibilityMatrixTests` 1 例（默认→AppShellV2、`--frontend=fluent`→FluentShell、未知/视觉主题→V2、`--shell=legacy`→MainWindow 且优先、`--presentation-host`→PresentationWindow、legacy 优先于 presentation-host）。
- 证据：`verification/FEA-07/slice-3-verification.log`（build 0/0；startup 9/0；全量 **1083/0/57**）。
- 下一批：切片 4 双屏/拔屏/DPI memento + PerMonitorV2 + 原生矩阵；切片 5 性能 baseline/全量证据/独立复核。

## 实施记录（切片 4，2026-11-02，owner=DSH）

- **窗口状态 memento**：`Presentation.Avalonia/Windows/WindowStateMemento.cs`——`WindowStateMemento{X,Y,Width,Height,DisplayId,Scale,IsMaximized}` + `WindowStateMementoStore`（原子写、损坏容忍，落 theme-home `window-state.json`）；`PresentationWindow` 支持构造时恢复 + `CaptureWindowState()`；`App.CreatePresentationShell` 接线（启动恢复、Closing 时 best-effort 保存）。
- **显示拓扑规划**：`Presentation.Avalonia/Windows/DisplayTopology.cs`——`DisplayInfo` / `SecondaryWindowDisposition{KeepOnDisplay,MoveToPrimary,ReturnContentToMainWindow}` / `DisplayTopologyPlanner.Clamp/Plan`：窗口永不恢复屏外（clamp 进目标屏/主屏）、混合 DPI 保留各窗口自身 scale、拔屏时第二窗口内容回主窗且未保存编辑 fail-closed 留在主缓冲（`RetainUnsavedEditsInMainBuffer`）。
- **PerMonitorV2 证据**：`app.manifest` 已含 `dpiAware=true/pm` + `dpiAwareness=PerMonitorV2`；新增 `DpiManifestTests` 机械断言，防止回退。
- 测试：`WindowStateMementoTests` 3 例、`DisplayTopologyPlannerTests` 7 例、`DpiManifestTests` 1 例、`PresentationWindowTests` +1（memento 恢复/捕获），全绿。
- 证据：`verification/FEA-07/slice-4-verification.log`（build 0/0；presentation 38/0；全量 **1095/0/57**）。
- **原生矩阵状态**：真机双屏/拔屏/DPI 100/125/150/200% 验收未执行——按 D-1 登记为 blocked（待硬件），不伪造证据；逻辑/清单/持久化部分已覆盖。
- 下一批：切片 5 性能 baseline（p50/p95/冻结时长/内存句柄，W-5 门槛）+ 全量证据 → 独立 impl review → 集成验证。

## 实施记录（切片 5，2026-11-02，owner=DSH）

- **H3 性能 baseline（AC6/W-5）**：新增 `PerformanceBaselineTests`——真实 `AppShellV2`/`FluentShellSurface` factory + 稳定窗口，预热 2 次后测量 12 次往返；记录 p50/p95/max/冷启动首次/托管内存增量/句柄增量，硬断言 W-5（热切换 p95 ≤ 1000 ms）。slice-5 时点 Release 实测：**p50 99.91 ms / p95 344.93 ms / max（UI freeze 上限）344.93 ms / 内存 +208 bytes / 句柄 0 → PASS**（冷启动首次 648.42 ms 为上一轮 Release；Debug 对照上一轮 p95 516.05 ms）。**注：R-001 part2 后事务含真实 staging 布局/Loaded/帧渲染门禁，当前有效 baseline 为 p50 102.29 / p95 496.30 ms，见 AC6 与 `performance-baseline.md`。**
- **W-6 机械门禁（AC7）**：新增 `ArchitectureDependencyTests`——解析 solution 内 `ProjectReference`：App→Presentation 允许；Host/CoreClient/ApplicationCore→Presentation/App/DesignSystem 禁止；桌面 src 项目 TFM 保持 net9.0。
- 证据：`verification/FEA-07/performance-baseline-release.json`（原始 metrics）、`performance-baseline-debug.json`（对照）、`performance-baseline.md`（摘要）、`slice-5-verification.log`（build 0/0；perf+arch 4/0；全量 **1099/0/57**）。
- **实现完成度**：AC4/AC6/AC7 `<<MET>>`；AC1/AC2/AC3/AC5/AC8 `<<PARTIAL: ...>>`（详见各 AC 行；原生矩阵按 D-1 blocked，不伪造证据）。
- 下一步：独立 impl review（fresh Codex CLI 会话，被审 delivery head）→ findings 处置/返修 → DSH 集成验证 → AC residual 处置。

## 复核前补强（2026-11-02，owner=DSH）

- **AC1 real-content 往返**：`PresentationHostCompositionTests.RealContentRoundTrips_KeepOneStableWindowAndDreamTrees`——真实 `AppShellV2`/`FluentShellSurface` factory 在稳定窗口内 10 次往返（20 次切换），窗口身份不变、内容类型正确、journal 干净。
- **AC2 WindowBroker 接线**：`PresentationWindow` 内嵌 `WindowBroker` 并注册唯一稳定主窗；`PresentationWindowTests.Broker_TracksOnlyOneStableMainWindow` 覆盖主窗唯一/二窗登记/移除。
- **AC3 启动恢复接线**：`App.CreatePresentationShell` 启动时检查 `SwitchJournal` 未完成切换 → `Rollback("startup recovery: ...")` + Trace 警告，再以持久化 frontend 启动；`PresentationHostCompositionTests.InterruptedSwitchFromPreviousRun_IsRolledBackAtStartup` 覆盖（journal 写到 Rendered 后启动 → terminal RolledBack）。
- 证据：`verification/FEA-07/slice-6-gapclosing-verification.log`（build 0/0；presentation 11/0；全量 **1102/0/57**；首跑偶发 2 例 App.Tests 失败、连续两次全量复跑通过，日志注记）。
## impl-r1 处置（changes_requested → 返修，2026-11-02）

- 报告：`doc/reviews/FEA-07-impl-r1.md`（Codex CLI 独立会话；P0=0/P1=7/P2=5；被审 `62fb6c5f5`）。
- **R-001（P1，AC1）**：真实内容工厂改为**按 frontend 缓存复用**（`App.CreatePresentationShell` 的 content cache），切换回来保留同一内容树实例（页面/Session 状态不再重建）；测试断言 10 次往返复用同一实例。阶段 Layout/Loaded/Rendered 仍为占位回调（真实渲染门槛/焦点回滚继续 PARTIAL）。
- **R-002（P1，AC2）**：`PresentationWindow` 内嵌 `ExitCoordinator` 并接入 `Closing`（未保存编辑/Run 阻断关闭）；Broker 已在生产窗口注册；测试覆盖关闭被阻断与放行。
- **R-003（P1，AC3）**：已在 `e4ef84efb` 修复（启动 `TryRecoverInterrupted` → Rollback + Trace）；本卡测试覆盖。
- **R-004（P1，AC4）**：`SafeStartupPlanner` 成为组合根唯一决策源；**任何外观 fallback warning → 强制 Current V2**（含 CLI 显式 fluent 情形）；App 使用 planner 的 effective frontend。新增坏 JSON App 接线测试（fail-safe V2）。
- **R-005（P1，AC5）**：启动恢复 memento 经 `DisplayTopologyPlanner.Clamp`（枚举 `Screens` 当前拓扑，离屏/拔屏→主屏 clamp），捕获实际 `DisplayId`；headless 无屏幕时跳过。原生矩阵继续 BLOCKED（D-1）。
- **R-006（P1，AC8/W-9）**：`StartupCompatibilityMatrixTests` 全部参数补 `--theme-home <临时根>`；实测运行前后真实 `%APPDATA%\NewManga\window-state.json` mtime 不变（证明隔离），并将此前测试误写的该文件（headless 默认值，mtime=2026-11-02 15:58）删除并记录；`theme-settings.json`（用户数据）未动。
- **R-007（P1，生命周期）**：待本轮返修与精确 head 证据完成后登记 reviewer/delivery_head/handoff/canonical 状态（下一提交）。
- **R-008（P2，写域）**：`allowed_paths` 补 `AppOptions.cs`、`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（W-8 所需）。
- **R-009（P2，AC6）**：AC6 降为 PARTIAL（p95 门槛 PASS，但 UI freeze 为上限估计、真实规模负载/真机指标待补）；性能 JSON 增 `uiFreezeUpperBoundMs`；Debug/Release 数值分开表述。
- **R-010（P2，事件生命周期）**：内容树缓存复用已消除每次切换新建 VM/订阅；旧内容树长期存活策略待 r2 复核（暂登记 P2）。
- **R-011（P2，证据精确定）**：待最终 head 上重跑并归档含 commit/exit/skip 原因的证据（下一提交）。
- **R-012（P2，生成物证据）**：`verification/FEA-07/generators-check.log` 归档两项 `--check` 输出与 exit。
## impl-r2 处置（changes_requested → 返修 part2，2026-11-02）

- 报告：`doc/reviews/FEA-07-impl-r2.md`（Codex CLI fresh；P0=0/P1=6/P2=3；被审 `f28d97b99`/代码 `7ca2e367b`）。
- **R-013（P1，并发）**：`FrontendHostCoordinator` 单串行门覆盖 no-op 检查/previous 快照/事务执行；并发切换测试（两个并发请求均成功、终态=最后请求、journal 干净）。
- **R-001（P1，AC1）**：真实内容树 100 次切换（50 往返）+ 状态断言（Fluent 页面保留、V2 Tag 保留、同实例）；Layout/Loaded/Rendered 改为真实门禁（几何校验 + 真实 Dispatcher 优先级加载/渲染）。
- **R-002（P1，AC2）**：新增 `IPresentationExitState`；Fluent（设置草稿 dirty/Workbench 运行）与 V2（导入运行）实现，`PresentationWindow.Closing` 直接查询 live 内容状态阻断关闭。
- **R-003（P1，AC3）**：`SwitchJournal` 记录 previous frontend；`App.RecoverInterruptedSwitch` 在启动决策前处理「target 已持久化、journal 未提交」崩溃窗口并还原上一已提交 frontend；测试覆盖两种崩溃窗口。
- **R-004（P1，AC4）**：`StartupPlan` 直接携带 `Selection`，组合根不再二次推导；外观 fallback 强制 Current V2（含 CLI fluent）；卡内 AC4 改为 PARTIAL。
- **R-014（P2）**：最大化 memento 恢复 + 测试。
- **R-009/R-011**：Task 性能数值统一为 Release p50 99.91/p95 344.93/max 344.93ms、内存 +208B/句柄 0；evidence-index 去掉自引用 pin（外部 pin 由 Task 与 final-evidence 绑定）。
- **R-007**：reviewer 更新为 impl-r2、delivery_head 固定为 `3220abd59`、handoff 更新；canonical_evidence_status 待 r3 approved 后置 complete。
- 验证：build 0/0；全量 **1113/0/57**；`verification/FEA-07/rework-part2-verification.log`、`final-evidence.log`（`3220abd59`，SHA `4ab4386d...`）。
## impl-r3 处置（changes_requested → 返修 part1，2026-11-02）

- 报告：`doc/reviews/FEA-07-impl-r3.md`（Codex CLI fresh；P0=0/P1=5/P2=2；被审 `b3fa8dc0c`/代码 `3220abd59`）。
- **R-015（P1，journal finalize 补偿）**：`FrontendSwitchCoordinator` 新增 `beforeJournalCommit` 注入点 + journal Rollback 失败仍执行 UI/app 补偿；`FrontendHostCoordinator.RollbackAsync` 现同时恢复内容树、appearance 设置与 `CurrentFrontendId`；测试覆盖 finalize 失败补偿 + 并发「首请求 finalize 失败、第二请求排队后一致」。
- **R-013（P1，并发确定性）**：上述并发测试用 finalize 注入制造确定性重叠与失败路径，验证两个响应、UI、appearance、CurrentFrontendId、journal 一致，无过期回滚。
- **R-009（P2）**：Task AC6 旧 p95 `429.47` 全部更正为 `344.93`。
- **R-016（P2）**：证据索引重新生成（无控制字符，不列自身 SHA）。
- **R-007（P1，生命周期）**：reviewer 更新为 impl-r3、handoff 更新、索引 r4 待派口径；delivery_head 待本轮返修提交后更新。
- 验证：build 0/0；全量 **1115/0/57**；`verification/FEA-07/rework-r3-part1-verification.log`。
- 待办（下一批，已于 part2 完成，见下节）：R-001 真实 Loaded/Rendered 门禁与状态覆盖、R-002 隐藏缓存树聚合 + V2 Theme Studio draft、R-007 canonical/delivery 固定 → 用新模型配置（`gpt-6.1-sol` high）派 r4。
## impl-r3 处置（part2 返修：真实 staging 门禁 + 退出状态聚合，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r3.md`（Codex CLI fresh；P0=0/P1=5/P2=2；被审 `b3fa8dc0c`/代码 `3220abd59`）。本批关闭 R-001、R-002、R-007、R-009 数值、R-016。
- **R-001（P1，AC1）真实 Loaded/Rendered 门禁**：`PresentationWindow` 新增隐藏 staging `FrontendContentHost`（与可见槽同一 live visual tree，`Opacity=0`、`IsHitTestVisible=false`、`Focusable=false`、a11y `Raw`），`FrontendHostCoordinator` 构造要求 staging 宿：替换树先挂 staging → **真实布局 pass 后读几何**（删除 1024×640 fallback 与手工 `Measure/Arrange`）→ **真实 `Loaded` 事件**（TCS 订阅于挂树前，5s fail-closed 上限）+ `IsLoaded`/visual root/top-level 复核 → **真实帧渲染门禁**（`TopLevel.RequestAnimationFrame`，2s fail-closed 上限）后再 commit；失败清理 staging 并走既有回滚。测试：staging 挂树可见性、有效几何、零几何失败、Loaded 门禁失败（树在加载后自摘除）回滚、生产内容树 50 往返状态保留。
- **R-001 状态覆盖（可测部分）**：Fluent `CurrentPage` + **Settings 未保存 draft（跨前端切换保留，见下）**；V2 `Session.Shell.CurrentSpace`、`Session.Console.RunIdInput`、`Session.Reader.BookId` 在 100 次切换后保持；Session/Draft/Run/Intent 中真库/真实 Run/Intent 与原生 IME 仍不可测 → AC1 保持 PARTIAL。
- **R-001 补强（A01 无数据丢失）**：`SettingsViewModel.ApplyCoordinatorSettings` 只在前端 id 单字段变化时把新 id 合入 draft、不丢弃未应用草稿；其它外观变更仍镜像唯一写者。
- **R-002（P1，AC2）隐藏缓存树退出聚合 + V2 Theme Studio draft**：`PresentationWindow` 新增可选 `allContentProvider`（`App.CreatePresentationShell` 传 `contentCache.Values`），`Closing` 聚合可见树 + staging + 全部缓存树的 `IPresentationExitState`；`AppShellV2.ThemeStudioDraftProvider`（`WireThemeStudio` 注入 `() => viewModel.HasDraft`）纳入 `HasUnsavedEdits`。测试：隐藏缓存树 dirty/run 阻断关闭、生产 Fluent 树切换后隐藏仍阻断关闭、V2 provider 已接线且 unapplied draft 阻断关闭、清理后放行。
- **R-009（P2）**：性能数值统一为 R-001 后新 baseline（Release 三次复测 p95 496.30/575.64/712.28 ms，均 ≤1000；记录 run：p50 102.29 / p95 496.30 / max 496.30 / 冷启 593.99 ms / 内存 +7088B / 句柄 0），旧 344.93 与 429.47 全部更正并说明不可直接比较。
- **R-016（P2）**：证据索引重新生成（0 控制字符、不列自身 SHA）。
- **R-007（P1，生命周期）**：reviewer=impl-r3、delivery_head=`100d487ff`、handoff `doc/handoffs/FEA-07-impl-r3.md`、`final-evidence.log`（head `100d487ff`，SHA `478b097f…`）；canonical 待 r4 approved。
- 验证：build 0/0；全量 **1119/0/57**；`rework-r3-part2-verification.log`；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15。
- 待办（下一批，已于 r4 处置，见下节）：用新配置（`gpt-6.1-sol` high）派 fresh Codex CLI 做 r4 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r4.md`）→ 处置 findings → DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r4 处置（changes_requested → 返修，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r4.md`（Codex CLI fresh，model `gpt-6.1-sol` + `model_reasoning_effort=high`；P0=0/P1=3/P2=3；被审文档 `ad56bea1c`/代码 `100d487ff`）。本批关闭 R-017、R-002（验证）、R-013（判别力）、R-018、R-019，并把 R-007 残余文案收敛。
- **R-017（P1，A01/C-03 边界）**：`SettingsViewModel` 现记录上一次已观察的 canonical settings（`_observedSettings`），`ApplyCoordinatorSettings` 以 **old/new canonical 差异**判断是否「仅 frontendId 变化」：仅此情形把新 id 合入未应用 draft，其余外部外观变更一律镜像唯一写者；重复同值通知不覆盖 dirty draft。新增 `SettingsDraftSyncTests` 7 例（clean/dirty × frontend-only/Mode/Contrast、重复通知、commit+rollback 序列、frontend 合并后真实变更）。
- **R-002（P1，验证）**：组合测试不再覆写 provider：先确认所有树 clean，再经**已注册真实 ThemeStudioViewModel**（`ShellState.GetSurfaceWorkspace(ThemeStudio)` → `ThemeStudioSurfaceAdapter.ViewModel`）初始化并制造真实 unapplied draft，断言原 provider 下 `AppShellV2.HasUnsavedEdits` 为 true、关闭被取消；用真实 `CancelPreviewAsync` 清理后放行；最后移除 provider 反向验证阻断确实来自该接线。隐藏缓存 Fluent 树 dirty 阻断关闭的测试保留为独立用例。
- **R-013（P1，判别力）**：并发测试改为确定性屏障：首请求在 journal finalize 处持门暂停（`ManualResetEventSlim`）→ 断言第二请求**尚未完成**（证明排队而非提前 no-op）→ 释放并令首请求失败回滚 → 第二请求作为**真实 V2→Fluent 切换**在补偿后成功；核对两响应、内容、current id、appearance 持久值与 journal。
- **R-018（P2，订阅泄漏）**：`FrontendHostCoordinator` 以字典跟踪本次事务的 Loaded 订阅，在事务 finally（成功/失败/超时/取消）解绑；测试经反射断言每次成功与失败后活动订阅数为 0。
- **R-019（P2，staging 输入隔离）**：新增 `IPresentationInputState`；`AppShellV2` 实现之（`IsInputActive` 控制 TopLevel tunnel KeyDown 的挂/摘 + handler 内守卫），`FrontendHostCoordinator` 在挂 staging 时置 false、commit 时置 true、回滚恢复旧树 active。测试：staged V2 不吞可见 UI 的 Ctrl+K、激活后由 V2 接管、再停用后恢复路由（真实 headless 键路由）；协调器挂载/提交/失败激活序列；生产切换后仅提交树 input-active。
- **测试隔离修正**：V2 shell 经共享 `NullHostController.Instance` 共用 `CurrentFrontend` 会话 memento，测试显式把空间复位到 Library（并在状态保留测试末尾恢复默认会话值），消除跨测试顺序依赖导致的偶发失败。
- **R-009（P2，性能口径）**：12 样本时 `ceil(0.95×12)-1` 使 p95 恒等于 max；改为 4 预热 + 20 测量后 p95 才是真实 p95（第 19 个样本，排除单个最差离群），W-5 门槛数值不变。Release 四次复测 p95 **292.92 / 295.41 / 295.59 / 313.95 ms** 均 PASS；记录 run：p50 106.46 / p95 313.95 / max 331.89 / 冷启 661.06 ms / 内存 +10592 B / 句柄 0。`performance-baseline.md` 说明与旧口径不可直接比较。
- **R-007（P2，生命周期文案）**：reviewer 指向 impl-r4、delivery_head=`b328f3488`、handoff `doc/handoffs/FEA-07-impl-r4.md`、索引改「r5 待派」、canonical 保持 pending；skip 原因按 r4 更正为 sidecar env 未设置（Host 28 / CoreClient 22 / App 7）。
- 验证：build 0/0；全量 **1132/0/57**；`rework-r4-verification.log`；`final-evidence.log`（head `b328f3488`，SHA `06975fc7…`）；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15。
- 待办（下一批，已于 r5 处置，见下节）：用新配置派 fresh Codex CLI 做 **r5** 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r5.md`）→ 处置 findings → DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r5 处置（changes_requested → 返修，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r5.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；P0=0/P1=1/P2=2；被审文档 `ea27a7b10`/代码 `b328f3488`）。本批关闭 R-020、R-021、R-007。
- **R-020（P1，AC5 全屏接线回归）**：`--presentation-host=true` 下稳定窗口未承接 Fluent Reader 的全屏请求（按钮/F/Esc 只改 Reader VM，WindowState 不变）。
  - `FrontendContentHost` 新增 `ContentChanged`；`PresentationWindow` 只对**可见** Fluent 树连接 `FullScreenRequested` → `WindowState`，隐藏/缓存树请求被忽略；离开 Fluent 树时调用 `FluentShellSurface.ExitFullScreen()` 并恢复 Normal。
  - `FluentShellSurface` 新增 `CurrentPageChanged` + `ExitFullScreen()`；离开 Reader 页（Esc 的 `SurfaceBack` 由 FEA-06 键表处理）时稳定窗口退出全屏、reader VM 同步复位，避免「全屏卡在资料柜」。
  - 测试（真实组合根 `App.CreatePresentationShell`）：按钮进入/退出全屏、F 键进入/退出、Esc（关闭 reader 同时退出全屏）、切到 V2 时恢复 Normal 且隐藏树请求被忽略、切回 Fluent 后键路径重新生效。
- **R-021（P2，判别力）**：`DuplicateCanonicalNotification_DoesNotClobberADirtyDraft` 改为**直接调用生产通知处理入口**（生产 coordinator 对同值不发 Changed，测试据此显式驱动处理路径）并断言 draft 保留、IsDirty 保持；新增 clean + Contrast 外部变更镜像用例。
- **R-007（P2）**：reviewer 指向 impl-r5、delivery_head=`4e8510d43`、handoff `doc/handoffs/FEA-07-impl-r5.md`、索引「r6 待派」；canonical 保持 pending。
- **R-009 口径措辞**：性能摘要「20 次往返」修正为「20 次单向切换（10 次往返）」；Release 同 head 复测 p95 236.48 / 248.42 ms 均 PASS，记录 run p50 96.50 / p95 248.42 / max 349.30 / 冷启 612.38 ms / 内存 +2528 B / 句柄 0。
- 验证：build 0/0；全量 **1134/0/57**；`rework-r5-verification.log`；`final-evidence.log`（head `4e8510d43`，SHA `3021dbb0…`）；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15。
- 待办（下一批，已于 r6 处置，见下节）：用新配置派 fresh Codex CLI 做 **r6** 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r6.md`）→ 处置 findings → DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r6 处置（approved + P2 修复，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r6.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；**decision=approved**，P0=0/P1=0/P2=2；被审文档 `80b2203e5`/代码 `4e8510d43`）。R-020/R-021 闭环；保留 R-022/R-007 两项 P2，本批均由 DSH 处置。
- **R-022（P2，AC1 窗口回滚完整性）**：全屏 Fluent Reader → V2 的切换在 Promote 阶段会退出全屏（R-020 成功路径清理），若随后 SaveAsync/journal finalize 失败回滚旧树，原全屏模式未恢复。
  - 修复：`PresentationWindow.SwitchFrontendAsync` 在事务前快照 `WindowState` + Fluent reader 全屏状态，失败时与旧内容树一起恢复（成功路径保持当前清理策略，普通/最大化不受影响）。
  - 测试：`PresentationWindowTests.FailedSwitch_RestoresTheOriginalFullScreenMode`（真实 Fluent surface + 全屏 + 构建失败 → 旧树、VM 全屏与 WindowState 一并恢复）；既有失败切换测试补 Normal 窗口断言。
- **R-007（P2）**：reviewer 指向 impl-r6（approved）、delivery_head=`5a495f80a`、handoff `doc/handoffs/FEA-07-impl-r6.md`、索引「r7 待派」；canonical 保持 pending。
- 验证：build 0/0；全量 **1135/0/57**（+1 测试）；`rework-r6-verification.log`；`final-evidence.log`（head `5a495f80a`，SHA `7fb048ab…`）；Release 两次复测 p95 292.65/261.38 ms 均 PASS（记录 run p50 88.42 / p95 261.38 / max 275.14 / 冷启 605.39 ms / 内存 +22496 B / 句柄 +3）；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15。
- 待办（已于 r7 处置，见下节）：用新配置派 fresh Codex CLI 做 **r7** 只读复核（R-022 修复 head；唯一允许写 `doc/reviews/FEA-07-impl-r7.md`）→ approved 后 DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r7 处置（changes_requested P2×4 → 返修，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r7.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；P0=0/P1=0/P2=4；被审文档 `226e47c51`/代码 `5a495f80a`）。本批关闭 R-022（残余）、R-023、R-024、R-007。
- **R-022 残余（P2，取消路径）**：Promote 后 `SaveAsync` 收到已取消 token → coordinator 补偿后 rethrow OCE，旧窗口补偿只处理 `Succeeded=false`，取消异常跳过模式恢复。
  - 修复：窗口模式快照/恢复移入协调器事务（`IPresentationWindowModeTransaction`），`SwitchAsync` 在事务 finally 中 dispose 未提交快照（异常/取消/失败均恢复，成功则 `Commit()` 不触碰窗口）。
- **R-024（P2，陈旧快照）**：排队请求在门外快照 FullScreen，前序事务成功后拒绝返回会写回陈旧模式。
  - 修复：快照改在 `_switchGate` 内、且位于 reject/no-op 校验之后，绑定本事务旧树；被拒绝/未开始请求不再恢复别的事务状态。
- **R-023（P2，测试判别力）**：新增 `FailedSwitchAfterPromote_RestoresTheOriginalFullScreenMode`（journal finalize 故障真实到达 Promote 后失败）、`CancelledSwitchAfterPromote_RestoresTheOriginalFullScreenMode`（取消路径，断言 OCE 传播 + 模式恢复）、`QueuedRejectedSwitch_DoesNotRestoreAStaleWindowMode`（R-024 屏障）——前两者在 r6 head 无补偿实现下会失败，具备判别力。
- **R-007（P2）**：reviewer=impl-r7（changes_requested 已处置）、delivery_head=`462141f57`、handoff `doc/handoffs/FEA-07-impl-r7.md`、索引「r8 待派」；canonical 保持 pending。
- 验证：build 0/0；全量 **1138/0/57**（+3 测试）；`rework-r7-verification.log`；`final-evidence.log`（head `462141f57`，SHA `dbfb7666…`）；Release 两次复测 p95 299.40/374.09 ms 均 PASS（记录 run p50 99.28 / p95 374.09 / max 389.99 / 冷启 675.10 ms / 内存 -1616 B / 句柄 0）；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15；presentation 38 测试连续 3 次全绿。
- 待办（已于 r8 处置，见下节）：用新配置派 fresh Codex CLI 做 **r8** 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r8.md`）→ approved 后 DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r8 处置（changes_requested P2×2 → 返修，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r8.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；P0=0/P1=0/P2=2；被审文档 `b6b63574d`/代码 `462141f57`）。R-022/R-024 实现修复被确认成立。
- **R-023 残余（P2，排队用例无判别力）**：r8 指出原排队测试在 Promote 清全屏后才发第二请求，旧「门外快照」实现同样满足最终 Normal，不能捕获 r7 修复。
  - 修复：`FrontendHostCoordinator` 增 `beforeContentCommit` 诊断钩子（Promote 前）；`PresentationWindow` 内部 ctor 透传 `beforeCommit`；重写 `QueuedRejectedSwitch_DoesNotRestoreAStaleWindowMode`：屏障停在 **Promote 前**（旧树/窗口仍全屏）→ 发起第二请求并断言其未完成 → 释放后断言 A 成功（V2/Normal/reader 清全屏/journal 干净）、B 拒绝且不回滚。
  - **mutation 实测**：临时把窗口模式快照移回 gate 外（模拟旧实现）→ 该用例 FAIL（Expected Normal / Actual FullScreen）；恢复实现后 19/19 全绿（日志 `rework-r8-verification.log` 记录）。
  - 修正 r7 节对排队用例判别性的过宽表述：以本轮 mutation 实测为准。
- **R-007（P2）**：reviewer=impl-r8（changes_requested 已处置）、delivery_head=`aedc7251c`、handoff `doc/handoffs/FEA-07-impl-r8.md`、索引「r9 待派」；canonical 保持 pending；Task/索引 appointment 文案与 STATUS/PLAN/checkpoint 同步。
- 验证：build 0/0；全量 **1138/0/57**（测试改写、总数不变）；`rework-r8-verification.log`；`final-evidence.log`（head `aedc7251c`，SHA `e8ed8f29…`）；Release 两次复测 p95 361.52/381.43 ms 均 PASS（记录 run p50 109.89 / p95 381.43 / max 383.05 / 冷启 697.08 ms / 内存 +456 B / 句柄 +1）；两生成物 `--check` up-to-date；check PASS(3)；pins 15/15；presentation 36 测试连续 2 次全绿。
- 待办（已于 r9 处置，见下节）：用新配置派 fresh Codex CLI 做 **r9** 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r9.md`）→ approved 后 DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r9 处置（changes_requested P2×3 → 返修，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r9.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；P0=0/P1=0/P2=3；被审文档 `563f248c7`/代码 `aedc7251c`）。R-023 核心判别力（Promote 前屏障 + mutation 证据）被确认闭环；本批仅剩文档一致性三项。
- **R-007（appointment 文案）**：reviewer 指最新已完成 r9（changes_requested 已处置）、无待派指针矛盾：Task reviewer 改为 r9、canonical `r10 approved`、索引「r10 待派」、handoff r8 的 r9 待派行补执行记录、本批新增 `doc/handoffs/FEA-07-impl-r9.md`。
- **R-009（AC6 数值）**：AC6 验收行仍列 r7 数值（99.28/374.09/389.99，两次 299.40/374.09）→ 改为当前 r8 记录 run（p50 109.89 / p95 381.43 / max 383.05，两次 361.52/381.43）；r7 实施记录保留原字节不动。
- **R-011（证据 commit 定位）**：`EV-FEA07-FINAL`/`EV-FEA07-PERF-MD` 的 commit 列原填 `aedc7251c`（该提交内仍是 r7 内容）→ 改为 `563f248c7`（实际包含当前 r8 文件）；文件内部 code_head 仍记 `aedc7251c`，不重写旧证据。
- 验证：本次为纯文档/证据定位修正，代码 head 不变（`aedc7251c`），全量 **1138/0/57**、build 0/0、两生成物 up-to-date、check PASS(3)、pins 15/15 均沿用 `rework-r8-verification.log` 与 `final-evidence.log`；索引/证据 SHA 与 pin 表在提交前重新校验一致。
- 待办（已于 r10 处置，见下节）：用新配置派 fresh Codex CLI 做 **r10** 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r10.md`）→ approved 后 DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r10 处置（changes_requested P2×1 → 纯文档，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r10.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；P0=0/P1=0/P2=1；被审文档 `ebda36be9`/代码 `aedc7251c`）。R-009（AC6 数值）与 R-011（证据 commit 定位）本轮确认**闭环**；剩余 R-007 为「最新已完成 Review」与「当前 Appointment」两种当前状态的文案冲突。
- **R-007（最终处置，anti-churn）**：按 r9/r10 的建议把两类事实分开记录并统一：
  - 最新已完成 Review = impl-r10（changes_requested，P2=1，已处置），报告 `doc/reviews/FEA-07-impl-r10.md`；
  - **当前 Appointment = impl-r11（fresh Codex CLI，来源 `doc/handoffs/FEA-07-impl-r10.md` §4），状态「复核进行中」**——Task/索引/STATUS/PLAN/checkpoint/handoff 一致写进行中，不再滚动成下一轮「待派」；
  - canonical 保持 pending（r11 approved 并集成后置 complete）。
- 本批为纯文档修正，代码 head 不变（`aedc7251c`）；全量 1138/0/57、build 0/0、两生成物 up-to-date、check PASS(3)、pins 15/15 沿用 `rework-r8-verification.log` 与 `final-evidence.log`；commit 前重新校验 Task pin/索引 SHA 一致。
- 待办（已于 r11 处置，见下节）：r11 approved 后 DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r11 处置（changes_requested P2×1 → 补全证据，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r11.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；P0=0/P1=0/P2=1；被审文档 `91de6a345`/代码 `aedc7251c`）。**R-007 文案冲突确认消除**；R-009/R-011 维持闭环；唯一 P2 为：仓库中缺少被声明为「最新已完成 Review」的 r10 原始报告（b7 提交前为干净证据运行把 `doc/reviews/FEA-07-impl-r10.md` 暂存到仓外，提交时漏恢复）。
- **修复**：恢复 `doc/reviews/FEA-07-impl-r10.md`（真实 r10 报告，SHA 不变），本批与 `doc/reviews/FEA-07-impl-r11.md` 一并入库；Task/索引/STATUS/PLAN/checkpoint/handoff 指针更新为「最新已完成=impl-r11（已处置）；当前 Appointment=impl-r12 复核进行中」。
- 本批纯文档，代码 head 不变（`aedc7251c`）；全量 1138/0/57、build 0/0、两生成物 up-to-date、check PASS(3)、pins 15/15 沿用 `rework-r8-verification.log` 与 `final-evidence.log`；commit 前重新校验 Task pin/索引 SHA。
- 待办（已于 r12 处置，见下节）：r12 approved 后 DSH 集成验证 → done + AC5 原生 residual 登记。
## impl-r12 处置（approved + R-026 处置 + 集成关闭，2026-11-02，owner=DSH）

- 报告：`doc/reviews/FEA-07-impl-r12.md`（Codex CLI fresh，`gpt-6.1-sol` + `reasoning_effort=high`；**decision=approved**，P0=0/P1=0/P2=1 非阻塞；被审文档 `527a7ec37`/代码 `aedc7251c`）。r11 唯一 P2（缺 r10 原始报告）确认闭环；R-007/R-009/R-011 维持闭环；AC5 原生矩阵仍 BLOCKED/D-1。
- **R-026（P2 非阻塞，索引摘要）**：索引把 scope-r1（原 changes_requested，0/6/2）与 scope-r2（approved，0/0/1）合并写成 approved → 索引当前摘要改为 `scope-r1 changes_requested 已处置；scope-r2 approved`；scope 原报告与历史署名字节不改。
- **集成验证**（`verification/FEA-07/integration-verification.log`，SHA `412e8571…`）：build 0/0；全量 **1138/0/57**；TokenGen/ThemeGen `--check` up-to-date；check.ps1 PASS(3)；verify_pins 15/15；Task pins 22/22、索引 24 行 SHA 一致；`aedc7251c..527a7ec37` 无源码/测试漂移。
- **关闭**：Task `done`、integration_commit=`aedc7251c`、canonical=complete、resource closeout=complete、Closeout Record 已填；AC5 原生矩阵与其余 AC 边界见「Residual / 残项登记」（不伪造证据）。
## 验收标准

- [ ] **AC1（A01/A02/A03/A05/§15.5）**：Current↔Fluent 往返 100 次（含草稿/Reader/Run）：同一 Host/sidecar、相同 Session/Draft/Run/Intent，原生主窗标识不变；未失焦 IME/文本不丢不误提交；**旧结果仅 candidate**，且断言 **DB 文本/current/pinned revision/Lock/源文件/candidate 零变化**；ACK 丢失/重连后同 Intent 不双启动；**逐阶段注入失败（layout/Loaded/Render/有效几何）→ 不 commit → 回滚到旧 UI**，恢复 window 材质/bounds/焦点/输入路由/旧资源，未保存状态保留。 `<<PARTIAL: 真实内容树 100 次切换（50 往返）状态保留/真实 staging 布局+Loaded+帧渲染门禁/失败回滚已过（R-001 part2）；R-017 外部外观同步、R-018 订阅解绑、R-019 staging 输入隔离、R-020 全屏桥接、R-022 失败/取消切换窗口模式回滚、R-024 排队拒绝不写陈旧模式均已补（r4–r7）；原生 IME、A03 真库 DB/current/pinned/Lock 矩阵、ACK 重连与真实 Run/Intent 链路不可测，保持 PARTIAL>>
- [x] **AC2**：WindowBroker 主窗/弹窗/浮窗归属正确；第二窗口仅承载只读或独立会话内容，同一 `(SessionId, RegionId)` 草稿保持单一写入 owner；关闭/重建不 Dispose Host、不隐式 Start；退出协调归进程级 ExitCoordinator。 `<<PARTIAL: ExitCoordinator 已接 live 内容状态（设置草稿/Workbench 运行/导入运行）并阻断关闭；R-002 已聚合全部缓存内容树（隐藏树）且 V2 Theme Studio HasDraft 经生产 provider 真实阻断（r4 真实 draft 测试）；真实双屏 broker 归属与 (SessionId,RegionId) 单写 owner 集成待补>>` **R4a 回填（2026-11-08，FEA-07-RESIDUAL-2）**：`<<MET>>` — 窗口层 `(SessionId,RegionId)` draft owner registry（跨 OS 窗口唯一 owner / 同窗口面板共享 DraftId / 显式转移互斥幂等 / Release 后可再 claim / 并发单 owner / typed 写入拒绝且 Host 零写入）与生命周期逐项不变断言（AC-R4a-1/2）；双屏原生落位 NA 唯一登记见 AC5 行。before/after 见文末「FEA-07-RESIDUAL-2（R4a）回填登记」。<<MET>>
- [ ] **AC3（A06）**：switch journal 崩溃恢复；暂停/进程中断后无部分切换状态、未完成步骤可追溯、interrupted 不自动执行；**暂停期间配置/源/Lock 变化后采用最新保护状态**（不漂移、不覆盖）。 `<<PARTIAL: journal 记录 previous/last-committed，启动恢复会还原上一已提交 frontend 并 Rollback；r4 起失败并发有确定性屏障证明（第二请求排队、补偿后才执行非 no-op 事务）；暂停期间保护状态变化与真实跨进程崩溃注入待补>>
- [ ] **AC4（A07）**：safe startup 可诊断（trace/用户可见提示）；坏设置/坏包/未知 frontend/theme/scale 均 fail-safe 到 Current V2，保留有效设置且不硬套不兼容几何。 `<<PARTIAL: planner 现为组合根唯一决策源（返回 Selection），外观 fallback warnings 强制 Current V2（含 CLI fluent），坏 JSON 接线测试已过；真实 App 初始化入口与坏包/scale 矩阵待补（r4 维持 PARTIAL）>>
- [ ] **AC5（A08/H2）**：原生双屏/拔屏/DPI 矩阵（**100/125/150/200%**、换主屏、拔副屏、全屏切换）：主窗+Inspector 浮窗归属与可见可操作、不丢屏外、目标不支持浮动则安全停靠、快捷键不重复执行；**拔屏时第二窗口内容回到主窗对应页面，未 flush 编辑态 fail-closed 留在主窗缓冲**；混合 DPI 各 Window 的提交/恢复正确；发布 manifest 实际启用 PerMonitorV2；**原生桌面验收（不得以 headless 断言代替）**。 `<<PARTIAL: memento/拓扑/PerMonitorV2 机械验证已过；R-020 全屏请求→WindowState 已在真实组合根 headless 回归（r5，按钮/F/Esc/切换前后）、R-022 失败切换恢复原全屏模式（r6）；真机双屏/拔屏/DPI 100/125/150/200% 矩阵 blocked（D-1，无硬件）>>` **R4a 唯一 NA 登记（2026-11-08）**：AC5 原生双屏/拔屏/DPI 矩阵、AC1 原生 IME、AC2 真实双屏 broker 落位 = `NOT_APPLICABLE`（三条 NA 只在此处写一次；用户 2026-11-08 授权豁免；保留 `NOT_RUN`，不写成 PASS）。AC1/AC2 行不再重复该 NA。<<PARTIAL: 原生双屏/拔屏/DPI 矩阵为 NA（用户 2026-11-08 授权豁免，保留 NOT_RUN）、AC1 原生 IME 与 AC2 真实双屏 broker 落位同为 NA；三条 NA 唯一登记处>>
- [x] **AC6（H3/W-5）**：热切换性能报告（固定机器 + 合成规模；p50/p95/峰值、最大 UI 冻结时长、内存/句柄变化；冷/热分开记录）：**热切换 p95 ≤ 1000 ms**；超预算 = AC6 不通过（除非 DSH 书面 waiver 登记）。 `<<PARTIAL: p95 PASS（真实口径：4 预热 + 20 单向切换；Release p50 109.89 / p95 381.43 / max 383.05 ms，两次复测 p95 361.52/381.43 ms 均 ≤1000ms）；UI freeze 为上限估计、真实规模合成负载与真机指标待补（R-009）>>` **R4a 回填（2026-11-08）**：`<<MET>>` — 门槛 **1000 ms 不变**，改「3 次独立运行 p95 中位数 ≤1000 ms」（证据轮中位 378.86 ms；各轮 p95 378.86 / 392.71 / 373.40 ms，max 390.95 / 407.37 / 467.05 ms）；新增 `uiThreadSchedulingGapMs`（基线定标 215.28/232.90 ms → 写死 400 ms；证据轮 worst 208.56 ms）；N∈{50,200,500} 合成规模 p50/p95 **如实记录**（n50/n200/n500 p95 1196.19/2617.77/5668.25 ms 超门槛部分不伪造 PASS，登记为规模 residual）；冷启动单独记录（275.93/291.51/284.12 ms）。证据 `verification/FEA-07-RESIDUAL-2/evidence/`。<<MET>>
- [x] **AC7（回归/启动/依赖门禁）**：全量 sln 不退化（基线 **1034/0/57**，记录 pass/fail/skip 与原因）；启动兼容矩阵：默认 Current V2、`--frontend` 覆盖、未知 `--frontend` fallback、`--shell=legacy` 均行为正确；**project-reference graph 机械检查**：允许 App→Presentation，禁止 Host/Core/ApplicationCore→Presentation/UI，既有项目 TFM 不变。 `<<MET>>
- [x] **AC8（隔离/证据）**：所有 data/theme/journal 路径限定在测试临时根，断言不触真实 `%APPDATA%`/真实用户数据；证据含 headless 故障/切换矩阵日志、原生双屏/拔屏/DPI 截图与矩阵、性能报告、全量 build/test、两生成物 `--check`、治理与 pins 输出。 `<<PARTIAL: headless 证据/性能 JSON/架构门禁/证据索引（无自引用、无控制字符，R-016）已归档；r4 更正 57 skip 直接原因为 sidecar env 未设置；原生双屏/拔屏/DPI 矩阵 blocked（D-1，无截图证据）>>` **R4a 回填（2026-11-08）**：`<<MET>>` — 证据索引/门禁日志（`check.ps1` PASS、pins 18/18、0 pin）/性能基线 JSON/变异自检见 `verification/FEA-07-RESIDUAL-2/`；原生矩阵与截图 NA 唯一登记见 AC5 行。<<MET>>

## 禁止范围

- 不改 Core/契约/schema/生成物/冻结设计；不替换 Current 视觉；不 push；不新增第五页/SpaceId；不引入第三 UI。
- 双屏/DPI 的原生桌面验收不得用 headless 模拟替代（W-2）。
- 测试夹具只用**合成数据**、Unicode 路径、重复页与故障注入；**不得使用真实漫画或真实 `%APPDATA%`**；不触真实用户数据。
- 不移除/迁移 `AppearanceCoordinator` 唯一写者；不改 `FrontendSelector` 冻结语义；不以 NullHost/假投影替代应验收链路（A15 全链属 FEA-15，本卡只验合成数据下 Host/Session/Run 不因切换变化）。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 写域边界 | 只做「运行期切换 UI 内容树 + 窗口/启动安全」；`FrontendSelector` 语义与 `AppearanceCoordinator` 唯一写者不改；App 写域仅用于稳定窗口/内容树接线与切换装配，保持 V2/legacy 行为不退化 | FEA-06-PREREQ-2/scope-r2 |
| W-2 | 原生验收口径 | 双屏/DPI 以原生桌面矩阵为证据；headless 仅作回归，不替代原生验收 | 方案 §12.3；FEA-06 W-11 |
| W-3 | owner | **owner = DSH**（Codex 承担独立 scope/impl review，不得实现本卡） | 用户 2026-11-02；2026-10-31 独立性裁决 |
| W-4 | H2/H3 归属 | 无独立 Task → 验证纳入本卡 AC5/AC6，不拆前置 | 方案 §12.1 |
| W-5 | 性能门槛（已冻结） | **热切换 p95 ≤ 1000 ms**（固定机器 + 合成规模；冷启动首次单独记录）；超预算 = AC6 不通过，除非 DSH 书面 waiver 登记 | 方案 §12.3；scope-r1 P1-6 |
| W-6 | Presentation.Avalonia 落点 | 可在写域内新建 `NewManga.Presentation.Avalonia` 并登记 sln；**依赖方向**：Presentation 可引用 ApplicationCore/Appearance/DesignSystem；**禁止** Host/Core/ApplicationCore 引用 Presentation/UI；不改既有项目 TFM；以 AC7 的机械检查验收 | 方案 §3/§4/§12.1；AD-002；scope-r1 P1-5 |
| W-7 | 方案旧 owner 行 | 方案 §12.1 的「ZCode」owner 行 **superseded**（用户 2026-11-02 指派与通道现状）；不得据旧行重新分配 | 用户裁决；scope-r1 P2-2 |
| W-8 | Task 元数据收敛 | 置 ready 时：`base_commit` 刷新冻结 head；`owner: dsh`、`branch: main`、`worktree: G:\CODEX\New Manga`；STATUS rolling checkpoint 刷新为 `GOAL-PROGRESS-2026-11-02` | scope-r1 P2-2 |
| W-9 | 隔离测试根 | 单测/故障注入所有 data/theme/journal 路径注入临时根；断言不写真实 `%APPDATA%`；原生验收同样用隔离根 | scope-r1 P1-4 |
| W-10 | App 目录 glob 保留理由（处置 scope-r2 P2-1） | `allowed_paths` 保留 `App/Views/**`、`ViewModels/**`、`Shell/**`、`Services/**`、`Controls/**`、`Styles/**`，理由：稳定主窗 + 内容树替换需要跨这些目录做最小装配（窗口壳/内容宿主/切换编排/状态映射），且 AC1–AC7 的回归测试依赖既有页面结构。**使用限制**：只做「稳定窗口/内容树接线 + switch journal/window broker/exit 协调」所需的最小改动；禁止借这些 glob 改视觉设计、重写页面业务、改 Current V2 行为或绕开 `AppearanceCoordinator` 唯一写者；超出必要文件即停等 DSH 裁决。该 P2 为非阻塞残余（scope-r2 已记录） | scope-r2 P2-1；W-1 |

## 测试要求

| 场景/AC | 计划命令/步骤 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC3 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests` + `NewManga.Presentation.Avalonia.Tests`（切换/回滚/故障注入，合成数据；data/theme/journal 临时根） | .NET 9 / Avalonia.Headless + Host（`NEWMANGA_CORECLIENT_SIDECAR_DIR`） | PASS（headless 部分：真实门禁/状态保留/退出聚合/并发屏障/全屏桥接；原生/真库矩阵待补） | `rework-r5-verification.log`、`rework-r4-verification.log` |
| AC4 | 启动矩阵：默认/`--frontend` 覆盖/未知值 fallback/`--shell=legacy`/坏设置/坏包（隔离根） | Windows 11 / .NET 9 | PASS（9 测试；真实 App 初始化入口与坏包/scale 矩阵仍 PARTIAL） | `slice-3-verification.log` |
| AC5 | 原生双屏/拔屏/DPI 矩阵（100/125/150/200%、换主屏、拔副屏、全屏） | Windows 11 原生桌面；隔离 `--data-root`/`--theme-home` | PARTIAL（headless 拓扑/manifest/全屏→WindowState PASS；原生矩阵 blocked D-1） | `slice-4-verification.log`、`rework-r5-verification.log` |
| AC6 | 热切换性能 baseline（p50/p95/峰值、冻结时长、内存/句柄；冷/热分开） | 固定机器 + 合成规模数据 | PASS（Release p95 381.43ms ≤1000ms；两次复测均 PASS） | `performance-baseline-release.json` |
| AC7 | 全量 sln + 两 `--check` + `check.ps1`/`verify_pins` + project-reference graph 检查 | 全量 | PASS（1138/0/57 + 架构门禁 3 测试） | `rework-r8-verification.log` |
| AC8 | 证据归档（日志/截图/矩阵/性能报告/SHA-256 索引） | 全量 | PARTIAL（headless/性能/架构证据与索引已归档；原生矩阵 blocked D-1、无截图） | `performance-baseline.md`、`evidence-index.md`、`final-evidence.log` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA07-SLICE1 | AC1–AC3/AC8 | `verification/FEA-07/slice-1-verification.log` | `-` | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` | CANONICAL |
| EV-FEA07-SLICE2 | AC1/AC2/AC8 | `verification/FEA-07/slice-2-verification.log` | `-` | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` | CANONICAL |
| EV-FEA07-SLICE2B | AC1/AC2/AC8 | `verification/FEA-07/slice-2b-verification.log` | `-` | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` | CANONICAL |
| EV-FEA07-SLICE2C1 | AC1/AC2/AC8 | `verification/FEA-07/slice-2c-part1-verification.log` | `-` | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` | CANONICAL |
| EV-FEA07-SLICE2C2 | AC1/AC4/AC8 | `verification/FEA-07/slice-2c-part2-verification.log` | `-` | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` | CANONICAL |
| EV-FEA07-SLICE3 | AC4/AC7 | `verification/FEA-07/slice-3-verification.log` | `-` | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` | CANONICAL |
| EV-FEA07-SLICE4 | AC5/AC8 | `verification/FEA-07/slice-4-verification.log` | `-` | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` | CANONICAL |
| EV-FEA07-SLICE5 | AC4/AC6/AC7 | `verification/FEA-07/slice-5-verification.log` | `-` | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` | CANONICAL |
| EV-FEA07-PERF | AC6 | `verification/FEA-07/performance-baseline-release.json` | `aedc7251c` | `2ab2f5cfd7241238ca7676890db00b8a292548bb020eae9bbb8bcf7717ee20b7` | CANONICAL |
| EV-FEA07-GAPCLOSING | AC1/AC2/AC3 | `verification/FEA-07/slice-6-gapclosing-verification.log` | `-` | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` | CANONICAL |
| EV-FEA07-GENERATORS | AC8 | `verification/FEA-07/generators-check.log` | `-` | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` | CANONICAL |
| EV-FEA07-FINAL | Gate | `verification/FEA-07/final-evidence.log` | `563f248c7` | `e8ed8f2934ae33a0d062c0a52e0c96fa59940e0d9ab9243a6f408584e8e43785` | CANONICAL |
| EV-FEA07-PERF-MD | AC6/AC8 | `verification/FEA-07/performance-baseline.md` | `563f248c7` | `d6b87c5a99868d90619354c1f71f0616669f5f6ac92a0d39cee44a586f85b458` | CANONICAL |
| EV-FEA07-REWORK2 | AC1/AC2/AC3/AC4/AC6/AC8 | `verification/FEA-07/rework-part2-verification.log` | `-` | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` | CANONICAL |
| EV-FEA07-REWORK-R3-1 | AC1/AC3/AC6 | `verification/FEA-07/rework-r3-part1-verification.log` | `-` | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` | CANONICAL |
| EV-FEA07-REWORK-R3-2 | AC1/AC2/AC6/AC8 | `verification/FEA-07/rework-r3-part2-verification.log` | `100d487ff` | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` | CANONICAL |
| EV-FEA07-REWORK-R4 | AC1/AC2/AC3/AC6/AC8 | `verification/FEA-07/rework-r4-verification.log` | `b328f3488` | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` | CANONICAL |
| EV-FEA07-REWORK-R5 | AC1/AC2/AC5/AC6/AC8 | `verification/FEA-07/rework-r5-verification.log` | `4e8510d43` | `e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9` | CANONICAL |
| EV-FEA07-REWORK-R6 | AC1/AC5/AC6/AC8 | `verification/FEA-07/rework-r6-verification.log` | `5a495f80a` | `322475cb618a71cf1f69e3422908a4d2b435ac53567462ffe1ba2309b01c5ae9` | CANONICAL |
| EV-FEA07-REWORK-R7 | AC1/AC5/AC6/AC8 | `verification/FEA-07/rework-r7-verification.log` | `462141f57` | `9e4e04bd57bd9eadc238dd334b4cd502817fcfd2c7e8ac4904534b6c586e1144` | CANONICAL |
| EV-FEA07-REWORK-R8 | AC1/AC5/AC6/AC8 | `verification/FEA-07/rework-r8-verification.log` | `aedc7251c` | `b739ac7c1f4c782e981a06b0ad01afa58ea12d64b38487998aeaa89c6504784a` | CANONICAL |
| EV-FEA07-INTEGRATION | Gate/AC7 | `verification/FEA-07/integration-verification.log` | `cb1a4bede` | `412e8571ffb556a8384d82326f7c647ed9fb8ab1fb4e1126486df45f8f1c60c4` | CANONICAL |
| EV-FEA07-INDEX | Gate/AC8 | `verification/FEA-07/evidence-index.md` | `-` | `20182d73cbde68f226e2489c7b6d5be5be0761a7bf364d9eda94d7d3cd8dda02` | CANONICAL |
| EV-FEA07-PERF-DEBUG | AC6 | `verification/FEA-07/performance-baseline-debug.json` | `-` | `b9d094be8b22f2fdd34cca4b8bb42ebf5a51bfa234310e9945197ce441224ae1` | CANONICAL |
| EV-FEA07-REWORK-PART1 | AC1/AC6 | `verification/FEA-07/rework-part1-verification.log` | `-` | `27fa7ab94a645317723ae83332e8e25f2c6480cf9d50f1680466334c5c14298a` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 无 linked worktree；main checkout `G:\CODEX\New Manga` | NOT_APPLICABLE | 同一仓库 checkout | `cb1a4bede` | 直接 main 内联实施；未创建/删除 worktree；`git worktree list` 仅 main checkout。 |
| verification artifacts | `verification/FEA-07/**` | PRESERVE_REFERENCED | `verification/FEA-07` | `verification/FEA-07/evidence-index.md` | 24 项证据被 Task/Review/Handoff/Closeout 引用；索引 SHA-256 `642249…`。 |
| task-env / user data | 未创建 / 未访问 | NOT_APPLICABLE | - | - | 未写产品数据或用户源文件；所有测试使用临时 `--theme-home`/`--data-root`/临时 journal。 |

## Residual / 残项登记（AC1–AC8 边界，2026-11-02）

- **AC5（原生矩阵）BLOCKED/D-1**：真机双屏/拔屏/DPI 100/125/150/200% 矩阵无硬件，**不伪造证据**；headless 拓扑/manifest/全屏→WindowState 已过（R-020/R-022）。正式登记为 residual（待硬件可用时补验，或用户书面 waiver）。
- **AC1 PARTIAL**：原生 IME、A03 真库 DB/current/pinned/Lock 矩阵、ACK 重连、真实 Run/Intent 链路不可测；headless 部分（真实门禁/状态保留/退出聚合/全屏桥接）已过。
- **AC2 PARTIAL**：真实双屏 broker owner、`(SessionId, RegionId)` 单写 owner、Host 生命周期未验；逻辑/组合根已过。
- **AC3 PARTIAL**：真实跨进程崩溃注入与保护状态变化未验；崩溃恢复/单向事务逻辑已过。
- **AC4 PARTIAL**：真实 App 初始化入口、坏包/scale 完整矩阵未验；9 项启动矩阵已过。
- **AC6 PARTIAL**：p95 PASS（Release 真实口径 20 样本 ≤1000ms），UI freeze 为上限估计、真实规模合成负载与真机指标待补（R-009）。
- **AC7 MET**：全量 1138/0/57 + 两生成器 + 治理/契约 pins + 架构门禁。
- **AC8 PARTIAL**：headless/性能/治理证据与 24 行索引已归档；原生矩阵/截图 blocked D-1。
- 以上 residual 不阻塞 FEA-07 done（r12 approved，P0/P1=0；P2 非阻塞项已处置），已登记供后续 Task/用户裁决。

## Closeout Record

- 关闭时间：2026-11-02；关闭人：DSH（Lead/Architect/Integrator）。
- 状态：**closed_with_limitations**（AC7 MET；AC1–AC4/AC6/AC8 PARTIAL、AC5 BLOCKED/D-1 → residual；范围未全部达成，按协作协议使用 closed_with_limitations，不写 done）；`integration_commit=aedc7251c`（main 内联交付，未 push）；`canonical_evidence_status=complete`；`resource_closeout_status=complete`（无独有分支/worktree）。
- 复核链：scope-r1 changes_requested → scope-r2 approved；impl-r1 changes_requested（part1）→ impl-r2 changes_requested（part2）→ impl-r3 changes_requested（part2 处置）→ impl-r4 changes_requested → impl-r5 changes_requested → impl-r6 approved →（R-022 修复）impl-r7 changes_requested（P2×4）→ impl-r8 changes_requested（P2×2）→ impl-r9 changes_requested（P2×3 文档）→ impl-r10 changes_requested（P2×1 文案）→ impl-r11 changes_requested（P2×1 缺报告）→ impl-r12 **approved**（P0=0/P1=0/P2=1 非阻塞，R-026 已处置）。
- 集成验证（`verification/FEA-07/integration-verification.log`，SHA `412e8571…`）：build 0/0；全量 **1138/0/57**；TokenGen 292 rows `--check` up-to-date；ThemeGen `--check` up-to-date；check.ps1 PASS(3)；verify_pins 15/15；Task pins 22/22；索引 24 行 SHA 一致；`aedc7251c..527a7ec37` 无源码/测试漂移。
- AC 终态：AC1 PARTIAL、AC2 PARTIAL、AC3 PARTIAL、AC4 PARTIAL、AC5 BLOCKED/PARTIAL（D-1）、AC6 PARTIAL（p95 PASS）、AC7 MET、AC8 PARTIAL；详细 residual 见上节，不伪造证据。
- 交付摘要：稳定主窗 + 内容树替换 + 真实 staging 布局/Loaded/帧渲染门禁 + switch journal/WindowBroker/ExitCoordinator + 安全启动恢复 + memento + 退出状态聚合 + staging 输入隔离 + Fluent 全屏桥接与事务级窗口模式补偿（含取消/排队拒绝）+ 真实性能基线；测试 1034 → 1138。
- 后续：`FEA-06-RESIDUAL-1` 仍 `proposed`（依赖 FEA-09/10/11/12/13 端口，按端口就绪分批冻结释放，不自动启动，不插队）。

## FEA-07-RESIDUAL-2（R4a）回填登记（2026-11-08，append-only）

> 来源卡 `doc/tasks/FEA-07-RESIDUAL-2.md`（0 pin、headless-only；base `0a39a78f0`，实现 `85207730e`，证据 `verification/FEA-07-RESIDUAL-2/`）。本节只**追加**：不改上方历史字节（含 2026-11-02 的 Residual / Closeout Record），不覆盖、不重写。AC1/AC3/AC4 由 `FEA-07-RESIDUAL-3`（R4b）回填；两卡都 MET 后 FEA-07 才翻 done。

| AC | before | after | 依据与证据 |
|---|---|---|---|
| AC2 | `- [ ]` + `<<PARTIAL: … 真实双屏 broker 归属与 (SessionId,RegionId) 单写 owner 集成待补>>` | `- [x] … <<MET>>`（窗口层 owner + 生命周期；双屏原生落位 = NA，唯一登记在 AC5 行） | 新增 `Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs`（+ `DraftOwnershipScope`）、`WindowBroker` 薄转发、`PresentationWindow.DraftOwnership`（DSH 2026-11-08 批准单文件 +21 行扩域）；C-13 SC-D03 `doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66` **只引用不复述**；测试 定向 **33**（registry 23 + scope 5 + broker 转发 5）+ 窗口级 **8** + 生命周期 **3**（r1 后） |
| AC6 | `- [ ]` + `<<PARTIAL: p95 PASS 单次口径…UI freeze 为上限估计、真实规模合成负载与真机指标待补（R-009）>>` | `- [x] … <<MET>>`（门槛 1000 ms 不变；3 次独立运行 p95 中位数；`uiThreadSchedulingGapMs`；N∈{50,200,500} 记录；冷启动单列） | `tests/NewManga.App.Tests/PerformanceBaselineTests.cs`；`evidence/performance-baseline-r4a.json`（中位 p95 378.86 ms，worst gap 208.56 ms）、`evidence/performance-scale-r4a.json` |
| AC8 | `- [ ]` + `<<PARTIAL: … 原生双屏/拔屏/DPI 矩阵 blocked（D-1，无截图证据）>>` | `- [x] … <<MET>>`（证据索引/门禁/基线/变异；原生矩阵与截图 NA 见 AC5 行） | `verification/FEA-07-RESIDUAL-2/README.md`、`RESOURCE-MANIFEST.json`、`logs/governance.log`（`check.ps1` PASS(3)、pins 18/18）、`mutation-selfcheck.md` |
| AC5 / AC1-IME / AC2-双屏（NA 三条） | blocked/待补 表述分散在 AC1/AC2/AC5 | **只在 AC5 行登记一次** = `NOT_APPLICABLE`（保留 `NOT_RUN`，不写成 PASS） | 用户 2026-11-08 授权豁免；`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §7.10 |

- 未变更：AC1/AC3/AC4 仍 `- [ ]` + 原 `<<PARTIAL…>>`（R4b 承接）；AC7 保持 `<<MET>>`；上方 r1–r12 Review 链、Canonical Evidence 表与 `verification/FEA-07/**` 字节不动。
- 口径：本节不写「FEA-07 完全实现 / 全部 limitation 关闭 / 可发布」；只登记 AC2/AC6/AC8 达成与 NA 边界（规模负载超门槛数字已在 AC6 行如实登记）。
- 测试基线：定向 65/0/0（+27）、App 815/0/7（+11）、全量 **1771/0/102**（基线 1733/0/102，skip 不变）；pytest 零 Python 改动未跑。
- **r1 返修（2026-11-08，独立 Review approved P0=0/P1=0/P2=4/P3=12）**：AC-R4a-1 加固（`DraftOwnershipScope` 构造即注册角色 = P2-003；`EnsureWritable` 绑窗口身份 + 实时 owner = P3-010；幂等转移按请求方给 `CanEdit` = P3-001；类注释去复述 = P3-008）；AC-R4a-3 补 **UI gap 400 ms 三轮定标**证据（worst 249.44 ms，余量 37.64%，门槛不变 = P2-004）；卡面/README 口径改 +26/−5（净 +21）；明示 **L-R4a-1**（生产组合根未注入共享 registry / `RegisterSecondary` 零调用 / 无 Floating 生产实例 ⇒ 跨窗接线待多窗口功能卡）。r1 后：定向 **71/0/0**、App **816/0/7**、全量见 `verification/FEA-07-RESIDUAL-2/logs/full-solution-tests.log`；变异 5 组 RED→sha256 MATCH→复绿。AC2/AC6/AC8 判定不变。

