---
id: FEA-07
title: 运行期切换与窗口（双 UI 切换、WindowBroker、switch journal、安全启动）
kind: implementation
governance_version: 3
status: in_progress
approval: scope_review_r2_approved_2026-11-02
suggested_owner: dsh
owner: dsh
reviewer: codex-cli（impl-r3 独立复核；报告 doc/reviews/FEA-07-impl-r3.md；r4 待派，见文末）
depends_on:
  - FEA-00A-IMPL-1
  - FEA-04
  - FEA-05-PORT-1
  - FEA-06
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 100d487ffb55518e98be5219d750ab85c8a71d2b（r3 返修 part2 代码提交；精确证据见 final-evidence.log）
canonical_evidence_status: pending（r4 approved 并集成后置 complete）
resource_closeout_status: pending
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
- 待办：用新配置（`gpt-6.1-sol` high）派 fresh Codex CLI 做 r4 只读复核（唯一允许写 `doc/reviews/FEA-07-impl-r4.md`）→ 处置 findings → DSH 集成验证 → done + AC5 原生 residual 登记。
## 验收标准

- [x] **AC1（A01/A02/A03/A05/§15.5）**：Current↔Fluent 往返 100 次（含草稿/Reader/Run）：同一 Host/sidecar、相同 Session/Draft/Run/Intent，原生主窗标识不变；未失焦 IME/文本不丢不误提交；**旧结果仅 candidate**，且断言 **DB 文本/current/pinned revision/Lock/源文件/candidate 零变化**；ACK 丢失/重连后同 Intent 不双启动；**逐阶段注入失败（layout/Loaded/Render/有效几何）→ 不 commit → 回滚到旧 UI**，恢复 window 材质/bounds/焦点/输入路由/旧资源，未保存状态保留。 `<<PARTIAL: 真实内容树 100 次切换（50 往返）状态保留/真实 staging 布局+Loaded+帧渲染门禁/失败回滚已过（R-001 part2）；原生 IME、A03 真库 DB/current/pinned/Lock 矩阵、ACK 重连与真实 Run/Intent 链路不可测，保持 PARTIAL>>`
- [x] **AC2**：WindowBroker 主窗/弹窗/浮窗归属正确；第二窗口仅承载只读或独立会话内容，同一 `(SessionId, RegionId)` 草稿保持单一写入 owner；关闭/重建不 Dispose Host、不隐式 Start；退出协调归进程级 ExitCoordinator。 `<<PARTIAL: ExitCoordinator 已接 live 内容状态（设置草稿/Workbench 运行/导入运行）并阻断关闭；R-002 part2 已聚合全部缓存内容树（隐藏树）并把 V2 Theme Studio HasDraft 纳入；真实双屏 broker 归属与 (SessionId,RegionId) 单写 owner 集成待补>>`
- [x] **AC3（A06）**：switch journal 崩溃恢复；暂停/进程中断后无部分切换状态、未完成步骤可追溯、interrupted 不自动执行；**暂停期间配置/源/Lock 变化后采用最新保护状态**（不漂移、不覆盖）。 `<<PARTIAL: journal 记录 previous/last-committed，启动恢复会还原上一已提交 frontend 并 Rollback；暂停期间保护状态变化与真实跨进程崩溃注入待补>>`
- [x] **AC4（A07）**：safe startup 可诊断（trace/用户可见提示）；坏设置/坏包/未知 frontend/theme/scale 均 fail-safe 到 Current V2，保留有效设置且不硬套不兼容几何。 `<<PARTIAL: planner 现为组合根唯一决策源（返回 Selection），外观 fallback warnings 强制 Current V2（含 CLI fluent），坏 JSON 接线测试已过；真实 App 初始化入口与坏包/scale 矩阵待 r3 复核>>`
- [x] **AC5（A08/H2）**：原生双屏/拔屏/DPI 矩阵（**100/125/150/200%**、换主屏、拔副屏、全屏切换）：主窗+Inspector 浮窗归属与可见可操作、不丢屏外、目标不支持浮动则安全停靠、快捷键不重复执行；**拔屏时第二窗口内容回到主窗对应页面，未 flush 编辑态 fail-closed 留在主窗缓冲**；混合 DPI 各 Window 的提交/恢复正确；发布 manifest 实际启用 PerMonitorV2；**原生桌面验收（不得以 headless 断言代替）**。 `<<PARTIAL: memento/拓扑/PerMonitorV2 机械验证已过；真机双屏/拔屏/DPI 100/125/150/200% 矩阵 blocked（D-1，无硬件）>>`
- [x] **AC6（H3/W-5）**：热切换性能报告（固定机器 + 合成规模；p50/p95/峰值、最大 UI 冻结时长、内存/句柄变化；冷/热分开记录）：**热切换 p95 ≤ 1000 ms**；超预算 = AC6 不通过（除非 DSH 书面 waiver 登记）。 `<<PARTIAL: p95 PASS（R-001 后新 Release baseline：p50 102.29 / p95 496.30 / max 496.30 ms，三次复测 496.30/575.64/712.28 ms 均 ≤1000ms）；UI freeze 为上限估计、真实规模合成负载与真机指标待补（R-009）>>`
- [x] **AC7（回归/启动/依赖门禁）**：全量 sln 不退化（基线 **1034/0/57**，记录 pass/fail/skip 与原因）；启动兼容矩阵：默认 Current V2、`--frontend` 覆盖、未知 `--frontend` fallback、`--shell=legacy` 均行为正确；**project-reference graph 机械检查**：允许 App→Presentation，禁止 Host/Core/ApplicationCore→Presentation/UI，既有项目 TFM 不变。 `<<MET>>`
- [x] **AC8（隔离/证据）**：所有 data/theme/journal 路径限定在测试临时根，断言不触真实 `%APPDATA%`/真实用户数据；证据含 headless 故障/切换矩阵日志、原生双屏/拔屏/DPI 截图与矩阵、性能报告、全量 build/test、两生成物 `--check`、治理与 pins 输出。 `<<PARTIAL: headless 证据/性能 JSON/架构门禁/证据索引（无自引用、无控制字符，R-016）已归档；原生双屏/拔屏/DPI 矩阵 blocked（D-1，无截图证据）>>`

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
| AC1–AC3 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests` + `NewManga.Presentation.Avalonia.Tests`（切换/回滚/故障注入，合成数据；data/theme/journal 临时根） | .NET 9 / Avalonia.Headless + Host（`NEWMANGA_CORECLIENT_SIDECAR_DIR`） | PASS（headless 部分；原生/真库矩阵待复核） | `slice-1/2/2b-verification.log` |
| AC4 | 启动矩阵：默认/`--frontend` 覆盖/未知值 fallback/`--shell=legacy`/坏设置/坏包（隔离根） | Windows 11 / .NET 9 | PASS（9 测试） | `slice-3-verification.log` |
| AC5 | 原生双屏/拔屏/DPI 矩阵（100/125/150/200%、换主屏、拔副屏、全屏） | Windows 11 原生桌面；隔离 `--data-root`/`--theme-home` | PARTIAL（headless 拓扑/manifest PASS；原生矩阵 blocked D-1） | `slice-4-verification.log` |
| AC6 | 热切换性能 baseline（p50/p95/峰值、冻结时长、内存/句柄；冷/热分开） | 固定机器 + 合成规模数据 | PASS（Release p95 496.30ms ≤1000ms；三次复测均 PASS） | `performance-baseline-release.json` |
| AC7 | 全量 sln + 两 `--check` + `check.ps1`/`verify_pins` + project-reference graph 检查 | 全量 | PASS（1119/0/57 + 架构门禁 3 测试） | `rework-r3-part2-verification.log` |
| AC8 | 证据归档（日志/截图/矩阵/性能报告/SHA-256 索引） | 全量 | PARTIAL（headless/性能/架构证据与索引已归档；原生矩阵 blocked D-1、无截图） | `performance-baseline.md`、`evidence-index.md`、`rework-r3-part2-verification.log` |

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
| EV-FEA07-PERF | AC6 | `verification/FEA-07/performance-baseline-release.json` | `100d487ff` | `03c12a4dc09868236fd4525b8fc8d8483b7b03673bc03c252c4e1c5ea70a1423` | CANONICAL |
| EV-FEA07-GAPCLOSING | AC1/AC2/AC3 | `verification/FEA-07/slice-6-gapclosing-verification.log` | `-` | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` | CANONICAL |
| EV-FEA07-GENERATORS | AC8 | `verification/FEA-07/generators-check.log` | `-` | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` | CANONICAL |
| EV-FEA07-FINAL | Gate | `verification/FEA-07/final-evidence.log` | `100d487ff` | `478b097fb4087aaf48683fc43030a7350481e3b9cda8a67521b9d701a3e373f7` | CANONICAL |
| EV-FEA07-REWORK2 | AC1/AC2/AC3/AC4/AC6/AC8 | `verification/FEA-07/rework-part2-verification.log` | `-` | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` | CANONICAL |
| EV-FEA07-REWORK-R3-1 | AC1/AC3/AC6 | `verification/FEA-07/rework-r3-part1-verification.log` | `-` | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` | CANONICAL |
| EV-FEA07-REWORK-R3-2 | AC1/AC2/AC6/AC8 | `verification/FEA-07/rework-r3-part2-verification.log` | `100d487ff` | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` | CANONICAL |

## Closeout Record

- 待关闭时填写。
