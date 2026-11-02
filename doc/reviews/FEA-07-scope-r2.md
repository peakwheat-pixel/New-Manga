---
task_id: FEA-07
reviewer: codex-cli
reviewer_kind: agent
author: dsh-lead
base_commit: 682fe17ae94ddce5740aa0a2a4a74bde19057024
reviewed_head: cbfb7bbc92d489541a24290038eae2117f8aa1ce
decision: approved
counts:
  P0: 0
  P1: 0
  P2: 1
---

# FEA-07 Scope Review r2

## Reviewer 与固定范围

- **Reviewer 身份与来源**：Codex CLI 独立 fresh session（`codex-cli`，`reviewer_kind: agent`）；当前执行上下文未参与 FEA-07 起草、r1 范围处置或实现，也不会实现 FEA-07。此执行界面未提供可核验的 session ID。
- **被审对象**：`main` 上 `cbfb7bbc92d489541a24290038eae2117f8aa1ce`；base 为 `682fe17ae94ddce5740aa0a2a4a74bde19057024`。初始 `git status --short` 为空。
- **审查边界**：只核 r1 处置是否闭环、是否产生新问题；不重开原范围的全量审查，不审未编写的实现。行号按 reviewed head 实测。

## 结论

**Decision: `approved` — P0=0 / P1=0 / P2=1。** r1 六条 P1 均闭环；没有新 P0/P1，也未发现 AC 与禁止范围、W-1 写域边界、H3 假设之间的新矛盾。P2-1 只完成了部分收窄，作为非阻塞残余保留（见下表）；本结论不表示 Task 已进入 `ready`。

## r1 findings 闭环表

| r1 finding | 状态 | 复核证据与判断 |
|---|---|---|
| P1-1 App 无法消费新模块 | **已闭环** | `allowed_paths` 已包含 `NewManga.App.csproj`（[FEA-07.md:26](../tasks/FEA-07.md#L26)）；处置记录将该文件用途限于接入 Presentation，且 W-6 允许 App→Presentation、禁止反向层依赖，TFM 不变（[FEA-07.md:64](../tasks/FEA-07.md#L64)、[FEA-07.md:112](../tasks/FEA-07.md#L112)）。未因此新增其他项目写域。 |
| P1-2 A03/§15.5 保护与回滚断言不足 | **已闭环** | AC1 明确旧结果仅为 candidate，DB 文本、current/pinned revision、Lock、源文件、candidate 零变化；列明 layout/Loaded/Render/有效几何失败注入、不 commit、回滚到旧 UI，并恢复 window 材质、bounds、焦点、输入路由和旧资源（[FEA-07.md:87](../tasks/FEA-07.md#L87)）。AC3 明确暂停期间配置/源/Lock 变化采用最新保护状态（[FEA-07.md:89](../tasks/FEA-07.md#L89)）。 |
| P1-3 A08/H2 双屏、拔屏及 DPI | **已闭环** | AC5 明列 100/125/150/200% DPI、拔屏时第二窗口内容回主窗对应页面、未 flush 编辑态 fail-closed 留在主窗缓冲、混合 DPI 提交/恢复、实际 PerMonitorV2 manifest 与不得以 headless 替代的原生验收（[FEA-07.md:91](../tasks/FEA-07.md#L91)）。第二窗口只读/独立会话及同一 `(SessionId, RegionId)` 单一写入 owner 明列于 AC2（[FEA-07.md:88](../tasks/FEA-07.md#L88)）；这两项虽落在 AC2 而非 AC5，任务验收覆盖完整。 |
| P1-4 隔离、测试项目与启动矩阵 | **已闭环** | AC1–AC3 测试行要求 App.Tests 与 Presentation.Avalonia.Tests，并将 data/theme/journal 放入测试临时根（[FEA-07.md:121](../tasks/FEA-07.md#L121)）；AC4 启动测试要求隔离根，W-9 对所有 data/theme/journal 路径作临时根约束（[FEA-07.md:115](../tasks/FEA-07.md#L115)、[FEA-07.md:122](../tasks/FEA-07.md#L122)）。AC7 列默认 Current V2、`--frontend` 覆盖、未知值 fallback、`--shell=legacy`，并要求记录 pass/fail/skip 与原因及 1034/0/57 基线（[FEA-07.md:93](../tasks/FEA-07.md#L93)）。 |
| P1-5 W-6 无机械依赖门禁 | **已闭环** | AC7 要求 project-reference graph 机械检查：允许 App→Presentation，禁止 Host/Core/ApplicationCore→Presentation/UI，既有 TFM 不变（[FEA-07.md:93](../tasks/FEA-07.md#L93)）；与 W-6 一致（[FEA-07.md:112](../tasks/FEA-07.md#L112)）。 |
| P1-6 W-5 性能门槛未冻结 | **已闭环** | AC6/W-5 冻结热切换 p95 ≤1000 ms，固定机器与合成规模，冷/热分开记录，超预算不通过，除非 DSH 书面登记 waiver（[FEA-07.md:92](../tasks/FEA-07.md#L92)、[FEA-07.md:111](../tasks/FEA-07.md#L111)）。该数值与方案 H3 的候选热切换 p95 ≤1s 一致，没有降低判据。 |
| P2-1 写域过宽 | **部分闭环；保留 1 项 P2** | 已移除 `Directory.Build.props`、`NewManga.Appearance/**`、`NewManga.DesignSystem/**`、`Appearance.Tests/**`；新增 Presentation 与相应测试路径有任务需要。但 `App/Views/**`、`ViewModels/**`、`Shell/**`、`Services/**`、`Controls/**`、`Styles/**` 仍是整目录授权（[FEA-07.md:30](../tasks/FEA-07.md#L30)–[FEA-07.md:38](../tasks/FEA-07.md#L38)）。W-1 限定实际用途且禁止视觉/唯一写者变更（[FEA-07.md:107](../tasks/FEA-07.md#L107)、[FEA-07.md:98](../tasks/FEA-07.md#L98)、[FEA-07.md:101](../tasks/FEA-07.md#L101)），降低了越界风险，但没有把 r1 要求的 App 写域缩到实现必要的具体文件/子目录。建议 DSH 在实现前缩小这些 glob，或逐项记录其对稳定窗口/内容树接线的必要性；此 P2 不阻断本轮批准。 |
| P2-2 恢复指针与 ready 前元数据 | **已闭环（ready 前动作已登记）** | STATUS rolling checkpoint 已改指向 `GOAL-PROGRESS-2026-11-02`（[STATUS.md:8](../STATUS.md#L8)），该 checkpoint 已写入 r1 处置和 scope-r2 下一步（[GOAL-PROGRESS-2026-11-02.md:283](../checkpoints/GOAL-PROGRESS-2026-11-02.md#L283)–[GOAL-PROGRESS-2026-11-02.md:288](../checkpoints/GOAL-PROGRESS-2026-11-02.md#L288)）。W-3 记 owner=DSH，W-8 明列置 ready 时刷新 base/owner/branch/worktree 与 checkpoint（[FEA-07.md:109](../tasks/FEA-07.md#L109)、[FEA-07.md:114](../tasks/FEA-07.md#L114)）；W-7 明确方案 §12.1 的 ZCode 行为 `superseded`（[FEA-07.md:113](../tasks/FEA-07.md#L113)）。这些 Task 元数据目前仍待 W-8 阶段执行，符合当前 proposed 状态。 |

## 新问题与一致性

- **未发现新 P0/P1。** 此轮处置差异为任务/治理文档，没有生产源码改动；AC1/AC3 数据保护与回滚断言未触及禁止范围；W-1 对 App 的用途限制与允许路径本身没有形成直接矛盾。P2-1 是 r1 已指出但尚未完全收窄的残余，不是本轮新增问题。
- **架构面**：Presentation→ApplicationCore/Appearance/DesignSystem 与禁止 Host/Core/ApplicationCore→Presentation/UI 的方向在 W-6、AC7 中一致；禁止范围继续保护 Core、契约、schema、生成物、冻结设计及 `AppearanceCoordinator` 唯一写者。
- **验证面**：所要求的 build、test、governance 与 pins 命令全部完成且通过；未执行原生双屏验收或未来 AC 实现测试，本轮也未把这些 `NOT_RUN` 事项当作已通过。

## Verification

| 场景 | 命令或手工步骤 | 结果 | 证据 |
|---|---|---|---|
| 固定 head 与工作区 | `git rev-parse HEAD`; `git status --short` | PASS | HEAD=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`；初始工作区 clean。 |
| 分支与变更历史 | `git log --oneline -6`; `git show --stat 0b7fe7318`; `git diff --stat 682fe17ae..cbfb7bbc9` | PASS | `main`；r1 处置 commit 改 Task、STATUS、checkpoint、r1 报告；base 到 reviewed head 的变更均为文档。 |
| Solution build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | PASS, EXIT 0 | 0 warnings / 0 errors。 |
| 全量 test | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | PASS, EXIT 0 | 1034 passed / 0 failed / 57 skipped；计数与 1034/0/57 基线一致。AC7 仍要求实施交付时逐项记录 skip 原因并比较基线。 |
| Governance | `pwsh -NoProfile -File tools\governance\check.ps1` | PASS | PASS（3 warnings）：10 个非终态 Task；STATUS 3193 bytes / 29 lines 与 Plan 4523 bytes / 64 lines 达到预算 80%。 |
| Pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | PASS | 15/15 pins。 |

## 是否可置 ready 与剩余动作

评审 Gate 已通过，且 P2-1 不属于阻断项；**当前 Task 尚不能直接置为 `ready`**，因为仍为 `proposed`，W-8 元数据尚未落入 Task。置 ready 前 DSH 需：

1. 将 `base_commit` 刷新到本次冻结 head `cbfb7bbc92d489541a24290038eae2117f8aa1ce`，写入 `owner: dsh`、`branch: main`、`worktree: G:\CODEX\New Manga`，并完成 Task 所需 Reviewer Appointment。
2. 按协作协议同步 STATUS、REBASELINE_PLAN、TASK_LEDGER 的状态/当前指针，然后运行 `pwsh -NoProfile -File tools\governance\check.ps1` 核对权威指针。
3. 处置 P2-1 残余：缩小未必要的 App 目录 glob，或在 Task 中逐项写明其对应实现需求与保留理由。该 P2 不改变本报告的批准结论。

## 边界声明

本报告只对 `base_commit=682fe17ae94ddce5740aa0a2a4a74bde19057024` 与 `reviewed_head=cbfb7bbc92d489541a24290038eae2117f8aa1ce` 之间的 FEA-07 r1 处置有效；不批准实现、不替代 DSH 的 ready 决定或集成验证，也不改变用户/DSH 的任务授权。
