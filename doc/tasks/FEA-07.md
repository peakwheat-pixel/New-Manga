---
id: FEA-07
title: 运行期切换与窗口（双 UI 切换、WindowBroker、switch journal、安全启动）
kind: implementation
governance_version: 3
status: in_progress
approval: scope_review_r2_approved_2026-11-02
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-00A-IMPL-1
  - FEA-04
  - FEA-05-PORT-1
  - FEA-06
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07
allowed_paths:
  - doc/tasks/FEA-07.md
  - apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj
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

## 验收标准

- [ ] **AC1（A01/A02/A03/A05/§15.5）**：Current↔Fluent 往返 100 次（含草稿/Reader/Run）：同一 Host/sidecar、相同 Session/Draft/Run/Intent，原生主窗标识不变；未失焦 IME/文本不丢不误提交；**旧结果仅 candidate**，且断言 **DB 文本/current/pinned revision/Lock/源文件/candidate 零变化**；ACK 丢失/重连后同 Intent 不双启动；**逐阶段注入失败（layout/Loaded/Render/有效几何）→ 不 commit → 回滚到旧 UI**，恢复 window 材质/bounds/焦点/输入路由/旧资源，未保存状态保留。 `<<TODO>>`
- [ ] **AC2**：WindowBroker 主窗/弹窗/浮窗归属正确；第二窗口仅承载只读或独立会话内容，同一 `(SessionId, RegionId)` 草稿保持单一写入 owner；关闭/重建不 Dispose Host、不隐式 Start；退出协调归进程级 ExitCoordinator。 `<<TODO>>`
- [ ] **AC3（A06）**：switch journal 崩溃恢复；暂停/进程中断后无部分切换状态、未完成步骤可追溯、interrupted 不自动执行；**暂停期间配置/源/Lock 变化后采用最新保护状态**（不漂移、不覆盖）。 `<<TODO>>`
- [ ] **AC4（A07）**：safe startup 可诊断（trace/用户可见提示）；坏设置/坏包/未知 frontend/theme/scale 均 fail-safe 到 Current V2，保留有效设置且不硬套不兼容几何。 `<<TODO>>`
- [ ] **AC5（A08/H2）**：原生双屏/拔屏/DPI 矩阵（**100/125/150/200%**、换主屏、拔副屏、全屏切换）：主窗+Inspector 浮窗归属与可见可操作、不丢屏外、目标不支持浮动则安全停靠、快捷键不重复执行；**拔屏时第二窗口内容回到主窗对应页面，未 flush 编辑态 fail-closed 留在主窗缓冲**；混合 DPI 各 Window 的提交/恢复正确；发布 manifest 实际启用 PerMonitorV2；**原生桌面验收（不得以 headless 断言代替）**。 `<<TODO>>`
- [ ] **AC6（H3/W-5）**：热切换性能报告（固定机器 + 合成规模；p50/p95/峰值、最大 UI 冻结时长、内存/句柄变化；冷/热分开记录）：**热切换 p95 ≤ 1000 ms**；超预算 = AC6 不通过（除非 DSH 书面 waiver 登记）。 `<<TODO>>`
- [ ] **AC7（回归/启动/依赖门禁）**：全量 sln 不退化（基线 **1034/0/57**，记录 pass/fail/skip 与原因）；启动兼容矩阵：默认 Current V2、`--frontend` 覆盖、未知 `--frontend` fallback、`--shell=legacy` 均行为正确；**project-reference graph 机械检查**：允许 App→Presentation，禁止 Host/Core/ApplicationCore→Presentation/UI，既有项目 TFM 不变。 `<<TODO>>`
- [ ] **AC8（隔离/证据）**：所有 data/theme/journal 路径限定在测试临时根，断言不触真实 `%APPDATA%`/真实用户数据；证据含 headless 故障/切换矩阵日志、原生双屏/拔屏/DPI 截图与矩阵、性能报告、全量 build/test、两生成物 `--check`、治理与 pins 输出。 `<<TODO>>`

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
| AC1–AC3 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests` + `NewManga.Presentation.Avalonia.Tests`（切换/回滚/故障注入，合成数据；data/theme/journal 临时根） | .NET 9 / Avalonia.Headless + Host（`NEWMANGA_CORECLIENT_SIDECAR_DIR`） | NOT_RUN | 待补 |
| AC4 | 启动矩阵：默认/`--frontend` 覆盖/未知值 fallback/`--shell=legacy`/坏设置/坏包（隔离根） | Windows 11 / .NET 9 | NOT_RUN | 待补 |
| AC5 | 原生双屏/拔屏/DPI 矩阵（100/125/150/200%、换主屏、拔副屏、全屏） | Windows 11 原生桌面；隔离 `--data-root`/`--theme-home` | NOT_RUN | 待补 |
| AC6 | 热切换性能 baseline（p50/p95/峰值、冻结时长、内存/句柄；冷/热分开） | 固定机器 + 合成规模数据 | NOT_RUN | 待补 |
| AC7 | 全量 sln + 两 `--check` + `check.ps1`/`verify_pins` + project-reference graph 检查 | 全量 | NOT_RUN | 待补 |
| AC8 | 证据归档（日志/截图/矩阵/性能报告/SHA-256 索引） | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA07-SLICE1 | AC1–AC3/AC8 | `verification/FEA-07/slice-1-verification.log` | `-` | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` | CANONICAL |
| EV-FEA07-SLICE2 | AC1/AC2/AC8 | `verification/FEA-07/slice-2-verification.log` | `-` | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` | CANONICAL |
| EV-FEA07-SLICE2B | AC1/AC2/AC8 | `verification/FEA-07/slice-2b-verification.log` | `-` | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` | CANONICAL |
| EV-FEA07-SLICE2C1 | AC1/AC2/AC8 | `verification/FEA-07/slice-2c-part1-verification.log` | `-` | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` | CANONICAL |
| EV-FEA07-SLICE2C2 | AC1/AC4/AC8 | `verification/FEA-07/slice-2c-part2-verification.log` | `-` | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` | CANONICAL |

## Closeout Record

- 待关闭时填写。
