---
review_id: FEA-04-scope-r1
task: FEA-04
kind: scope-review
base_commit: e34796862
reviewed_head: e34796862
reviewer: fea04-scope-reviewer
reviewer_source: DSH fresh 独立上下文派发（Team Lead=lead；spawn_teammate 子 agent，独立上下文、只读被审 head）
reviewer_participation: 未参与 FEA-04 的起草、实现或返修
review_appointment: doc/tasks/FEA-04.md（frontmatter `review_appointment`，:21）
date: 2026-11-02
timezone: Asia/Shanghai
conclusion: changes_requested
counts: { P0: 3, P1: 9, P2: 8, total: 20 }
scope: 仅范围冻结复核（不构成实现验收）
---

# FEA-04 范围冻结复核 r1

**结论：`changes_requested`（P0 × 3、P1 × 9、P2 × 8；findings F-01–F-12 + P2-1–P2-8 共 20 条）**

范围骨架（R-CURRENT / R-STATE / R-SWITCH、S1–S6、AC1–AC8、L 判定）与方案 §12.1 `:642`、§15.3 `:880-887`、§15.6 `:924` 的**逐行文本映射是准确的**；S1–S6 六行与方案原文逐字一致，§12.1 三项验收均有 R/AC 承载。**不能批准的原因是范围不可执行**：三处硬阻塞使被审卡在「禁令 ↔ 前置 deferral ↔ 写域」之间自相矛盾或缺少落点，按现文 ZCode/Codex 无法直接开工（详见 F-01/F-02/F-03）。共 9 项 P1 均可通过改卡解决，无需新增契约冻结；F-01 需 DSH 二选一裁决。

## 审查基线

| 项 | 值 | 证据 |
|---|---|---|
| 仓库 | `G:\CODEX\New Manga` | — |
| HEAD / 分支 / 工作区 | `e34796862473eeaae4896db283d701326efb7b8d` / `main` / clean | `git rev-parse HEAD`、`git status --porcelain`（空） |
| 被审 head 提交 | `e34796862 docs(fea-04): 释放并冻结范围 v1…` | `git log --oneline -1` |
| 卡 frontmatter `base_commit` | `91be6c134`（FEA-03 done 收口，为本卡父提交） | `doc/tasks/FEA-04.md:14`；`git merge-base --is-ancestor 91be6c134 HEAD` = 真 |
| 治理检查器 | **PASS**（2 警告：11 个非终态 Task；STATUS 达预算 80%＝3159 bytes/36 lines） | `pwsh -NoProfile -File tools/governance/check.ps1` |
| 冻结 pin 校验 | **PASS 15/15**（C01b–C14、FEA01） | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` |

**未执行（明确声明）**：`dotnet build`、`dotnet test`、`python -m pytest`、真机/UI 运行、任何源码或卡的写入、任何 commit/push。本报告只读被审材料；`check.ps1` 与 `verify_pins.ps1` 为只读执行，其结果不替代本复核。

---

## 1. 范围与方案一致性

### 1.1 §12.1 三项验收的 R/AC 承载（成立）

方案 `doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md:642` 出口为「当前可用行为不退化；无 VM 私有第二份业务真值；关闭/重建内容不 Dispose Host，不隐式 Start」。三项均有承载：

| §12.1 出口 | 承载 R | 承载 AC | 判定 |
|---|---|---|---|
| 当前可用行为不退化 | R-CURRENT-1/2（`:50-51`） | AC1/AC2（`:77-78`） | 有承载，但 AC1/AC2 文本需修（F-07/F-06） |
| 无 VM 私有第二份业务真值 | R-CURRENT-3（`:52`）、R-STATE-3（`:57`） | AC3（`:79`） | 有承载，AC3 缺机械口径（P2-3：静态检查无 allowlist/脚本/既有态 grandfather） |
| 关闭/重建不 Dispose Host、不隐式 Start | R-STATE-4（`:58`） | AC6（`:82`） | 有承载，AC6 缺断言方式（F-05） |

方案 `:642` 的交付物「`Frontends.Current`、V2 **state/route/VM** adapter；保留旧入口」中 **`route` 无对应 R/S/AC**（P2-5）；`Frontends.Current` 落点未定（F-03）。

### 1.2 §15.3 六项逐行落表（成立，逐字一致）

方案 `:882-887` 六行与卡 `:68-73` 的 S1–S6 **逐格一致**（现有源/字段、目标权威、迁出/验收三列均原文照录），可逐项追溯。仅引用区间标错一行（P2-2：实际表体 `:880-887`，`:876` 是标题行）。

### 1.3 与方案 DAG / 依赖静默偏差（F-12）

方案 §12.1 DAG `:666-669`：`P2[FEA-02-BRIDGE] --> P4[FEA-04 Current]`、`P3[FEA-03] --> P4`。卡 `depends_on` 只有 `FEA-02-CORE`、`FEA-03`（`:11-13`）；`doc/REBASELINE_PLAN.md:12-16` **无 FEA-02-BRIDGE 节点**。BRIDGE 的关键交付 `ExitCoordinator` 全库不存在（对 `apps/`、`src/` grep `ExitCoordinator|ExitLifecycle` **0 命中**），Host 仍由 legacy `Views/MainWindow.axaml.cs:852` 在关闭时 `_controller.DisposeAsync()`。方案 `:910` 明确该项归 FEA-02（BRIDGE）。见 F-12。

---

## 2. 写域完整性

卡 `allowed_paths`（`:23-34`）＝ `doc/tasks/FEA-04.md`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/checkpoints/**`、`doc/handoffs/FEA-04-*.md`、`Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**`、`apps/desktop-avalonia/tests/**`、`verification/FEA-04/**`。

**已覆盖（实测存在，130 个测试源 .cs／6 个测试项目）**：`Views/V2/{Console,Library,Shell,Studio,ThemeStudio}`、`ViewModels/V2/{Console,Library,Shell,Studio,ThemeStudio}`、`Shell/V2/{ShellState,RunStatusMonitor,ShellDeepLink,Studio,ThemeStudio}` 均在域内。

**写域缺口（按必需性排序）**：

| 缺口 | 事实 | 必需原因 | 处置 |
|---|---|---|---|
| `apps/desktop-avalonia/src/NewManga.Host/**`、`NewManga.CoreClient/**` | `NewManga.Host`/`NewManga.CoreClient` 全库对 `draft` **0 命中**；`Services/IHostController.cs` 方法清单（`:106-422`）**无任何 Draft/Journal/EditToken 方法** | S1 目标权威写「Core journal」、S2「意图 receipt」、S3「session intent store」——Core 侧 journal 已存在（`src/infrastructure/filesystem/draft_journal.py`、`src/application/editing/drafts.py`、`src/domain/drafts/entities.py`）但**未进入命令面** | F-01（P0） |
| `NewManga.App.csproj` | 仅引用 Host/ThemeEngine/DesignSystem（`:36-42`），**无 ApplicationCore**；App 源码对 `ApplicationCore`/`DraftBuffer`/`IntentCoordinator` **0 命中**（唯一 `RunMonitor` 命中是 legacy `Shell/V2/RunStatusMonitor.cs`） | S1/S2/S3/S5 新权威与 AC3 全部在 `NewManga.ApplicationCore`；按方案 `:914` 该 csproj 属 **DSH 单点提交** | F-02（P0） |
| `NewManga.Frontends.Current/`（新项目） | 方案 §4.1 `:129` 定义为项目、`:120` 明示"项目尚不存在"；§15.6 `:924` 给 FEA-04 的写域**不含**该路径；`NewManga.sln` 内无该工程（16 个工程已核），且 sln 属 DSH 单点（`:914`） | R-CURRENT-3 / AC1 / AC4 要求交付 `Frontends.Current` 门面 | F-03（P0） |
| `apps/desktop-avalonia/src/NewManga.App/Services/**` | 方案 §15.6 将 `Services/` 划给 FEA-02-BRIDGE（`:922`），卡内不含 | 仅当 switch preflight 需要注入时钟/Host 生命周期适配时才需要；按 P1-1 收窄后可**不需要**（推荐保持不开放） | 见 F-04 |

**`tests/**` 过宽（F-10 / P1）**：`:33` 覆盖 `NewManga.App.Tests`、`ApplicationCore.Tests`、`CoreClient.Tests`（含 `Commands/**` 冻结契约对照）、`DesignSystem.Tests`、`Host.Tests`、`ThemeEngine.Tests`。FEA-04 只需 App 测试；其余写权会与其它线（Host/CoreClient/ThemeEngine 已冻结契约的对照测试）冲突，且 `CoreClient.Tests/Commands/CommandContractV11RTests.cs` 类测试被改动会污染契约证据。

**`Frontends.Current` 落点回答（被问项）**：现有目录中**没有任何**对应目录；`Views/V2/**`、`ViewModels/V2/**`、`Shell/V2/**` 三者中，`Shell/V2/` 是唯一的「门面/装配」语义位置（同目录已有 `ShellState`、`RunStatusMonitor`、`ThemeStudioSurfaceAdapter` 等跨 VM 装配物）。建议落 `Shell/V2/Frontends/`（in-app 命名空间，零 csproj/sln 变更），并在 R-CURRENT-3 写明"FEA-04 不新建独立工程；独立 `NewManga.Frontends.Current` 工程随 FEA-06/07 的迁移再议"。

---

## 3. AC 可验证性逐条判定

| AC | 可机械判定？ | 依据/缺口 |
|---|---|---|
| AC1 旧入口保留 | **部分** | 「`git diff` 只增不改」与 S1–S6 必然产生的修改自相矛盾（F-07）；入口名/启动路径可机械核（`App.axaml.cs:56-62`、`AppShellV2.axaml.cs:31-55`、`Shell/V2/ShellDeepLink.cs`） |
| AC2 行为基线 | **否（命令不合法）** | `dotnet test apps/desktop-avalonia/tests/**` 不是合法 test 目标；应为 `NewManga.sln`（方案 `:737-738`）；且基线计数未冻结（F-06） |
| AC3 无第二真值 | **否（口径缺失）** | 无 allowlist、无检查脚本、无基准（P2-3）；仓库已有可复用先例 `tests/NewManga.ThemeEngine.Tests/DependencyBoundaryTests.cs` |
| AC4 六项迁出 | **是（补字段后）** | 三列证据格式已定；建议加 `assert_test(FQN)` 与 `status(migrated/deferred)`（P2-6） |
| AC5 fail-closed | **否（谓词缺失）** | 「有损编辑态」无定义、结构化错误无形状（F-08） |
| AC6 生命周期 | **否（断言未定义）** | 见 F-05 |
| AC7 证据入盘 | 是 | `verification/FEA-04/**` 在域内 |
| AC8 独立复核 | 是 | 但硬编码 r2 轮次（P2-4） |

### AC6「Host 对象身份前后不变」的可执行断言方式（被问项）

**先纠正前提：Host 不是进程级单例。** `App.axaml.cs:56` 逐进程 `new HostController(options.ToHostOptions())`，随后以 `IHostController` 注入（`Shell/V2/AppShellV2.axaml.cs:37`；V2 根由 `App.axaml.cs:94-96` 创建）。因此「对象身份不变」只能定义为**注入引用不变**，不能定义为"静态单例不变"。

现成可执行断言（三项，全部已存在于仓库，无需新增基础设施）：

1. **注入引用不变**：以同一 `IHostController` 实例构造 `AppShellV2`，捕获引用 → 关闭/重建内容 → `ReferenceEquals(controllerBefore, controllerAfter)` 为真。测试路径：`tests/NewManga.App.Tests/`（在域内）。
2. **未隐式 Start**：`FakeHostController.StartCalls`（`tests/NewManga.App.Tests/FakeHostController.cs:17`，另有 `LifecycleLog` `:19`、`:49` 记录 `"start"`）与生产 `HostController.StartRequests`（`src/NewManga.App/Services/HostController.cs:67`）在关闭/重建前后**计数不变**。
3. **未 Dispose Host**：`RunStatusMonitor` 是 V2 侧唯一 `IDisposable`（`Shell/V2/RunStatusMonitor.cs:14`）；V2 无其他 Dispose 路径，legacy 才是 `Views/MainWindow.axaml.cs:852` 的关闭 Dispose。断言「重建后 controller 仍可响应一次真实读（`RefreshBooksAsync` 成功）」即可证未 Dispose。

**并须写明基线（防 AC 虚过）**：现状 V2 **本就不 Dispose Host**（上一条已核），故 AC6 是**防回归**而非新增能力；卡内应写此基线，否则无工作量的实现也能满足 AC6。

### AC3「无第二份业务真值」的静态检查口径（被问项）

建议把 AC3 从"grep 私有 registry/缓存"改为两条可判定物：

1. **新增边界测试**（域内可写）：在 `tests/NewManga.App.Tests/` 加 `V2BusinessTruthBoundaryTests`，断言 V2 `ViewModels/**`、`Shell/**` 不出现「第二调度/第二真值」形态——至少（a）代码中无 `new RunStatusMonitor(`（除单一装配点）、（b）无 `new DispatcherTimer(` 承担 Run 轮询、（c）`ShellState` 之外的 `ShellSelection` 副本。参考先例：`tests/NewManga.ThemeEngine.Tests/DependencyBoundaryTests.cs`（已用反射/IL 断言依赖方向）。
2. **Handoff 允许清单 + grandfather 说明**：既有私有态必须逐项登记并写明"UI 态/业务态"，例如 `Shell/V2/RunStatusMonitor.cs:31` `_knownRunIds`（注释 `:24-30` 自述为「本会话真实见过的 run id，非伪造列表」）、`ShellState.SpaceViewState`（`ShellState.cs:119-139`，滚动/搜索/排序/筛选＝UI memento）。**不 grandfather 就无法 P0/P1=0**：这些不是本卡引入的。

---

## 4. fail-closed 语义（R-STATE-2 / AC5）

**结论：方向正确，不可判定。**

R-STATE-2（`:56`）与 AC5（`:81`）只说"未迁出且有损编辑态"，方案 `:878` 亦只说「未知或未迁移的有损编辑态导致 switch preflight fail-closed，保留原树及缓冲」。缺两件可执行物：

- **「有损」谓词**：建议冻结为显式集合（下列均为实测存在的状态位）：
  - S1：`StudioInspectorViewModel._pendingRegionType != null`（`ViewModels/V2/Studio/StudioInspectorViewModel.cs:195`，暴露于 `:282` `PendingRegionType`）
  - S2：`StudioPageViewModel._pendingNavigation != null`（`StudioPageViewModel.cs:257`，赋值点 `:1013`/`:1032`）
  - S3：`StudioBatchViewModel._intentIdempotencyKey != null` 且该轮未落 receipt（`StudioBatchViewModel.cs:329`、`:1079`、`:1139`）
  - S6：ThemeStudio editor draft 脏（`ViewModels/V2/ThemeStudio/ThemeStudioEditorViewModel.cs`）
  - FEA-03 草稿缓冲非 Flushed：`DraftBufferStatus.{Active,Conflicted}`（`src/NewManga.ApplicationCore/DraftBuffer.cs:3-9`）
- **结构化错误形状**：必须是 **App 层只读结果**，例如 `SwitchPreflightResult(bool Allowed, string Code, IReadOnlyList<string> Blockers)`，`Code` 仅用于 UI 呈现与日志；**不得**写入 Host 错误码表 / `allowedRunErrorCodes` / wire——否则即触发卡自身 L-2 的 `blocked`（`:91`）与禁止范围 `:96`。同时须说明与既有错误面 `HostViewSnapshot.LastError`（`Services/IHostController.cs:39`，注释 `:33-38` 明确其为 typed code 通道）的关系：preflight 结果不得覆盖该字段。

非投影语义（R-SWITCH-2 `:62`）可验证：以 `FakeHostController.StartCalls`/`LifecycleLog` 断言 preflight 前后无 `start` 事件、Run 投影读取计数不增。

---

## 5. L 判定（L-1 / L-2 / L-5）

依据 `doc/plan/FEA-C11_IMPL_PREREQS.md:24-26` 的归属表：L-1 归属 `FEA-03 / FEA-02-CORE / FEA-13 / FEA-11`；L-2 归属 `FEA-12-CORE / FEA-10 / FEA-13`；L-5 归属 `FEA-13 / FEA-12-CORE`——**FEA-04 均不在任何一列**。

| 项 | 卡内判定 | 复核结论 |
|---|---|---|
| L-1 四表 DDL | NOT_APPLICABLE（`:90`） | **成立**。本卡不触 Source 四表，写域无 `src/infrastructure/sqlite/**`；归属表亦未列 FEA-04 |
| L-5 整库恢复锁 | NOT_APPLICABLE（`:92`） | **成立**。不触 backup/restore；归属表未列 FEA-04 |
| L-2 M2-C1 字节修订 | NOT_APPLICABLE（`:91`） | **条件成立**：仅在「不新增 Host/Core 命令或 wire 码」前提下成立。但 FEA-03 冻结范围把 wire 接线明确 defer 给 FEA-04（`doc/tasks/FEA-03.md:65` Q-8「wire 由 FEA-04 承担」、`:82` R-JOURNAL-4③「Host 只读策略下的 UI 提示由 FEA-04 承担」），与卡 `:91`/`:96` 直接冲突 → **F-01（P0）**。若 DSH 裁决"扩写域+新增命令面"，本行须翻为 `blocked` 并先做 M2-C1 类字节修订 |
| 是否触 wire 码 | 卡称不触 | 按卡文本**不触**；按 FEA-03 deferral **要求触**。二者不可同时为真（F-01） |

---

## 6. 与 FEA-05 / FEA-06 的边界

卡 `:98`「不实现 FEA-05（Fluent 独立界面）与 FEA-06 起的 UI 功能」有两处偏差：

1. **误标 FEA-05**：方案 `:644` FEA-05 = 三层注册与资源隔离（Appearance / scheme·theme·scale registry / 设置迁移 / preview sink）；`:645` FEA-06 = Fluent 独立界面。卡把 FEA-05 描述为"Fluent 独立界面"。
2. **S6 与 FEA-05 相邻**：S6 目标含「Appearance draft」（`:73`），而 Appearance 的三层注册/迁移正是 FEA-05 出口。若 S6 实现到 draft 持久化/迁移，即越界。需在 R-STATE/禁止范围把 S6 的 Appearance 部分限定为**preflight 只读判定**。

**`switch` 只做 preflight 与方案是否冲突？（被问项）**
只做 preflight **不冲突**：方案 `:646` 把「运行期切换/窗口、switch journal、§12.3 跨 UI/双屏/故障矩阵」归 FEA-07；`:376` 的 Preflight 是切换编排的第一步；`:878` 把 "switch preflight fail-closed" 明确写在 FEA-04 的逐项迁出语义里。**冲突的是现卡写法**：R-SWITCH-1（`:61`）「`switch` 入口（Current ↔ Fluent）……由显式命令触发」＝本卡**实现切换入口**，与 GOAL-PROGRESS `:23` Q-15 裁决「FEA-04 切换是否本卡实现＝**否**，仅 preflight + fail-closed；Fluent 入口在 FEA-05」矛盾 → **F-04（P1）**。另：禁止范围用「FEA-05 起」表述不足以防越界——它把 FEA-05 内容说错，且未覆盖 S6→Appearance、`route` adapter 等相邻面。

---

## 7. 治理指针一致性

| 指针 | 内容 | 与卡一致？ |
|---|---|---|
| `doc/STATUS.md:7` | 当前 Task `[FEA-04](tasks/FEA-04.md)` `proposed`（范围冻结 v1，待独立复核 → ready；owner=ZCode） | **一致** |
| `doc/REBASELINE_PLAN.md:16` | `FEA-04 \| FEA-02-CORE、FEA-03 \| proposed（…范围冻结 v1；待独立复核 r1 → ready；owner=ZCode）` | **一致**（含同一 F-12 依赖偏差） |
| `doc/TASK_LEDGER.md:46` | `\| FEA-04 \| proposed \| own row \|` | **一致** |
| `check.ps1` | **PASS**（2 警告：11 个非终态 Task；STATUS 已用预算 80%＝3159 bytes/36 lines） | 警告为既有治理债，非本卡引入 |
| `verify_pins.ps1` | **PASS 15/15** | 与 STATUS `:15` 声称一致 |
| 卡 frontmatter `base_commit` | `91be6c134`（父提交，早于冻结提交 `e34796862`） | **不一致**（P2-1） |
| 卡 `review_appointment:21` | 指向本文件 `doc/reviews/FEA-04-scope-r1.md` | **一致**（本报告即该 appointment 的产出） |

---

## 8. 可执行性（按现文能否直接开工）

**不能直接开工。** 三条 P0 中任何一条都会让实现者在「遵守卡」与「满足 AC」之间二选一。建议 DSH 按下列顺序处置，最小成本路线（不新增契约冻结、不扩 wire）：

1. **裁决 F-03**（`Frontends.Current` 落点）：推荐 in-app `Shell/V2/Frontends/`，R-CURRENT-3 增一句"本卡不新建独立工程"。
2. **裁决 F-01**（wire 归属）：推荐**收窄**——S1 目标权威改为「ApplicationCore `DraftBuffer`（FEA-03 已交付）+ 可注入 seam」，S2/S3 同理改为 ApplicationCore `IntentCoordinator`/`RunMonitor`，把 Host/IPC 接线与本卡内显式 `defer` 到 FEA-02-BRIDGE（或 FEA-07），并在 Handoff 记录 FEA-03 `Q-8` deferral 的承接指针；禁止范围维持"不改 Host/CoreClient"不变。**替代**方案（扩写域 + 新命令面）成本高：需新契约字节修订，且 PLAN 需补 FEA-02-BRIDGE 节点，不建议在本卡内做。
3. **DSH 单点提交 F-02**（`NewManga.App.csproj` 增 `NewManga.ApplicationCore` 引用，如需再增 `NewManga.App.Tests.csproj`），并在卡内记一行"该文件由 DSH 单点提交"。
4. **按本报告 F-04…F-12 修卡**：重写 AC1/AC2/AC5/AC6 + R-SWITCH-1/2 + 禁止范围 + tests 收窄 + `base_commit` 重钉。
5. 派范围复核 **r2**；P0/P1=0 后才置 `ready`。

---

## Findings

| 编号 | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **F-01** | **P0** | 卡 `:96`、`:91`、`:23-34` ↔ `doc/tasks/FEA-03.md:65`、`:82` | **wire 接线归属自相矛盾，且写域不可达。** FEA-03 冻结范围明确把「wire 由 FEA-04 承担」（Q-8）与「Host 只读策略下的 UI 提示由 FEA-04 承担」（R-JOURNAL-4③）defer 给本卡；本卡 禁止范围「不改 Host/Core/CoreClient 公开契约与命令面；不新增 wire 码」、L-2「若需新命令/码 → blocked」、`allowed_paths` 不含 Host/CoreClient。事实：`Services/IHostController.cs` 无任何 Draft/Journal/EditToken 方法（`:106-422` 方法清单已逐条核）；`NewManga.Host`/`NewManga.CoreClient` 对 `draft` **0 命中**；Core 侧 journal 已存在（`src/infrastructure/filesystem/draft_journal.py` 等）但未进命令面。→ S1/S2/S3 目标权威（Core journal / 意图 receipt / session intent store）在本卡写域内不可达 | DSH 二选一：(a) **推荐**收窄 S1–S3 目标为 ApplicationCore 本地权威（`DraftBuffer`/`IntentCoordinator`/`RunMonitor`，FEA-03 已交付）+ 可注入 seam，Host/IPC 接线在本卡内显式 `defer` 到 FEA-02-BRIDGE/FEA-07 并在 Handoff 记承接指针；(b) 扩写域至 Host/CoreClient 并解除"不新增命令面"，此时 L-2 翻 `blocked` 且需新契约字节修订（不建议在本卡做） |
| **F-02** | **P0** | `apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj:36-42`；卡 `:23-34`、`:79` | **App 无 `NewManga.ApplicationCore` 引用，AC3/S1–S3/S5 的"经 ApplicationCore"在生产装配上不可达。** App.csproj 仅引用 Host/ThemeEngine/DesignSystem；App 源码对 `ApplicationCore`/`DraftBuffer`/`IntentCoordinator` **0 命中**；`NewManga.App.Tests.csproj` 也只引用 App。该 csproj 依方案 `:914` 属 **DSH 单点提交**，且不在 allowed_paths | 在 `ready` 前由 DSH 单点提交 App.csproj（+ 必要时 App.Tests.csproj）加引用；卡内写明"该文件由 DSH 单点提交，Owner 出 patch/需求"；否则 AC3 无法成立 |
| **F-03** | **P0** | 卡 `:52`、`:77`、`:80`、`:23-34` ↔ 方案 `:120`、`:129`、`:924`、`:914` | **`Frontends.Current` 无合法落点。** 方案 §4.1 把它定义为**新工程** `NewManga.Frontends.Current/`（`:120` 明示项目尚不存在），而 §15.6 给 FEA-04 的写域只有三个 V2 子目录 + tests，不含新工程路径；`NewManga.sln`（16 个工程已核）无该工程且属 DSH 单点。按现文无法在不越权的前提下交付本卡头号交付物 | 裁决为 **in-app 命名空间** 落 `Shell/V2/Frontends/`（推荐，零 csproj/sln 变更），R-CURRENT-3 补"本卡不新建独立工程；独立工程随 FEA-06/07 再议"；或增写域 + DSH 单点提交 sln/csproj |
| **F-04** | P1 | 卡 `:61`（R-SWITCH-1）、`:62` | **`switch` 入口越界，与 Q-15 裁决和方案归属矛盾。** R-SWITCH-1 写"`switch` 入口……由显式命令触发"＝本卡实现切换入口；GOAL-PROGRESS `:23` Q-15 裁决"FEA-04 切换是否本卡实现＝**否**，仅 preflight + fail-closed；Fluent 入口在 FEA-05"；方案 `:646` 把运行期切换/switch journal 归 FEA-07，`:717-718`（A01/A02）是 FEA-07 出口 | 改为：R-SWITCH-1＝「只实现 **preflight 判定与只读结果**，不实现 switch 执行入口、不新增用户可见命令」；R-SWITCH-2＝「preflight 前后 Run/reader 投影来自同一共享源，preflight 不触发新 Run」 |
| **F-05** | P1 | 卡 `:82`（AC6）、`:58`（R-STATE-4） | **AC6 无断言方式，"Host 对象身份"前提亦错。** Host **非**进程级单例：`App.axaml.cs:56` 逐进程 `new HostController(...)`，注入为 `IHostController`（`AppShellV2.axaml.cs:37`）。V2 侧无 Dispose 路径（仅 `RunStatusMonitor.cs:14` 实现 IDisposable），legacy 才在 `Views/MainWindow.axaml.cs:852` 关闭时 Dispose → 现状本就不 Dispose，AC6 是防回归 | 冻结三项断言：①`ReferenceEquals` 注入引用不变；②`FakeHostController.StartCalls`(`tests/NewManga.App.Tests/FakeHostController.cs:17`，`LifecycleLog` `:19/:49`) 与 `HostController.StartRequests`(`Services/HostController.cs:67`) 前后不变；③重建后 controller 仍可完成一次真实读。并写明"现状 V2 本就不 Dispose Host"的基线 |
| **F-06** | P1 | 卡 `:78`（AC2） | **AC2 命令不合法且基线未冻结。** `dotnet test apps/desktop-avalonia/tests/**` 不是合法 test 目标（目录通配）；方案 `:737-738` 给的是 `dotnet build .../NewManga.sln -warnaserror` + `dotnet test .../NewManga.sln --no-build`。基线计数只在 GOAL-PROGRESS `:13` 有"1052 passed"（FEA-03 集成口径），卡内未冻结 | 改确切命令；冻结基线 `1052 passed @ 76d947923`（**本席位未执行 dotnet test，未验证该计数在当前 head 仍成立**）；Handoff 按测试项目分列前后计数 |
| **F-07** | P1 | 卡 `:77`（AC1） | **「git diff 只增不改」与 S1–S6 自相矛盾。** S1–S6 必然修改现有 VM/Shell 文件（`StudioInspectorViewModel.cs:195`、`StudioPageViewModel.cs:257-259`、`StudioBatchViewModel.cs:314/316/329`、`ConsoleViewModel.cs:21/103/113`、`ReaderOverlayViewModel.cs:48-57`、`ShellState.cs`），这些都在 allowed_paths 内 | 把 AC1 降到入口级：「既有入口**注册点/公开入口名/启动路径**不改名不删除（`App.axaml.cs:56-62`、`AppShellV2.axaml.cs:31-55`）；其余改动限于 allowed_paths 且在 Handoff 逐处列明」 |
| **F-08** | P1 | 卡 `:56`（R-STATE-2）、`:81`（AC5） | **「有损编辑态」与「结构化错误」均未定义。** 无法机械判定，且"结构化错误"若落到 Host 错误码面会撞 L-2/禁止范围（见 F-01） | 冻结有损集合（S1 `_pendingRegionType != null`；S2 `_pendingNavigation != null`；S3 未落 receipt 的 intent key；S6 editor draft 脏；FEA-03 缓冲 `DraftBufferStatus.{Active,Conflicted}`，`ApplicationCore/DraftBuffer.cs:3-9`）+ 错误形状 `SwitchPreflightResult(bool Allowed, string Code, IReadOnlyList<string> Blockers)`，并写明 Code **不进** wire/`allowedRunErrorCodes`、不覆盖 `HostViewSnapshot.LastError`（`Services/IHostController.cs:39`） |
| **F-09** | P1 | 卡 `:33`（`tests/**`） | **写域过宽。** 覆盖 6 个测试项目 130 个源文件，含 `CoreClient.Tests/Commands/**`（冻结契约对照）、`Host.Tests`、`ThemeEngine.Tests`、`DesignSystem.Tests`——与本卡无关，且改这些测试会污染其它线的冻结证据 | 收窄为 `tests/NewManga.App.Tests/**`（必要时 + `tests/NewManga.ApplicationCore.Tests/**`）；其余测试项目写明"只读运行，不写" |
| **F-10** | P1 | 卡 `:72`（S5）↔ `Shell/V2/RunStatusMonitor.cs:7-8`、`ApplicationCore/RunMonitor.cs:13`、`ApplicationCore/README.md:3` | **S5「一个共享 RunMonitor」存在两套同名职责实现，未指明权威。** 现状 Console 已注入 legacy `RunStatusMonitor`（`ConsoleViewModel.cs:21/103/113`；该文件自述"ONE shared Run-status source"）；FEA-02-CORE 的 `ApplicationCore.RunMonitor<T>` 尚未接入 Current（README `:3`「本 Task 不接入 Current」）。歧义本身就是 AC3 要防的第二真值形态 | S5 明确：目标权威＝`ApplicationCore.RunMonitor<T>`；legacy `RunStatusMonitor` 的去留写清（本卡内降为薄适配，或保留并登记为"未迁出 + 原因"）；给出"单轮每 Run 最多一次 snapshot/projection 查询"的调用计数断言（`ApplicationCore/RunMonitor.cs` 头部与 README `:16` 已有注入计数先例） |
| **F-11** | P1 | 卡 `:98`、`:73`（S6） | **禁止范围把 FEA-05 说错，且未覆盖 S6→Appearance 相邻面。** 方案 `:644` FEA-05＝三层注册/Appearance、`:645` FEA-06＝Fluent 界面；卡写「不实现 FEA-05（Fluent 独立界面）」。S6 目标含「Appearance draft」，实现到持久化/迁移即越 FEA-05 | 改为「不实现 FEA-05 三层注册/Appearance 迁移与 FEA-06 Fluent 界面；S6 的 Appearance draft 仅作 preflight 只读判定，不实现 registry/scheme/scale」 |
| **F-12** | P1 | 卡 `:11-13` ↔ 方案 `:666-669`、`:910`；`doc/REBASELINE_PLAN.md:12-16` | **依赖与方案 DAG 不符。** 方案 DAG 为 `FEA-02-BRIDGE → FEA-04`；卡 depends_on 仅 FEA-02-CORE/FEA-03；PLAN 无 FEA-02-BRIDGE 节点。BRIDGE 的 `ExitCoordinator` 全库 0 命中，Host 生命周期仍由 legacy `Views/MainWindow.axaml.cs:852` 决定。FEA-04 的 R-STATE-4/AC6 依赖该生命周期语义的稳定前提 | DSH 显式裁决该边：或记 FEA-02-BRIDGE descoped 并说明 AC6/R-STATE-4 由 Current 现状兜底（推荐，与 F-01 方案 (a) 一致），或在 PLAN/卡内补该依赖；避免未来 BRIDGE 在同一 `Services/` 面与 FEA-04 冲突 |
| **P2-1** | P2 | 卡 `:14` `base_commit: 91be6c134` | 未随范围冻结提交更新（父提交，早于 `e34796862`）。FEA-03 惯例为范围冻结提交（FEA-03 v2 冻结 `dfa70c002` 即其 `base_commit`） | `ready` 时重钉为最终范围冻结/`ready` 提交，避免实现从缺卡的提交分叉 |
| **P2-2** | P2 | 卡 `:43` `§15.3 :876-886` | 行号偏一行：表体实为 `:880-887`（`:876` 是标题，S6 行在 `:887`） | 改 `:880-887`（卡内 S1–S6 文案本身与方案逐字一致，仅引用区间需更正） |
| **P2-3** | P2 | 卡 `:79`（AC3） | 静态检查无 allowlist / 无检查脚本 / 无 grandfather 基准（既有 `RunStatusMonitor._knownRunIds`、`ShellState.SpaceViewState` 会被误判） | 见正文 §3「AC3 口径」：新增 `V2BusinessTruthBoundaryTests`（参考 `tests/NewManga.ThemeEngine.Tests/DependencyBoundaryTests.cs`）+ Handoff 允许清单 + 既有态逐项 grandfather |
| **P2-4** | P2 | 卡 `:84`（AC8） | 硬编码「范围复核 **r2** approved」；若 r1 直接 approved 则 AC8 不可满足 | 改为「最后一次范围复核 approved（P0/P1=0），报告路径记入 `review_appointment`」 |
| **P2-5** | P2 | 卡 `:41`、`:50-52` | §12.1 的「V2 **route** adapter」无任何 S/AC 承载；现状 route 面为 `Shell/V2/ShellDeepLink.cs`（`:28 TryParse`、`:122 ToQuery`） | R-CURRENT 下补一行明确 route 适配范围，或显式写"route 由 `ShellDeepLink` 承载，本卡不改" |
| **P2-6** | P2 | 卡 `:80`（AC4） | 三列证据未要求具名测试与未迁出登记字段 | 冻结每项四字段：`baseline_evidence(commit:line)`、`new_authority(type/member)`、`assert_test(FQN)`、`status(migrated/deferred)+reason`；以 v-matrix 落 `verification/FEA-04/` |
| **P2-7** | P2 | 卡 `:91`（L-2） | L-2 判定"只看现有命令面"本身可辩护，但与被 FEA-03 defer 的 wire 义务冲突（同 F-01 根因），需联动修改 | 随 F-01 裁决同步：选 (a) 保持 NOT_APPLICABLE 并在卡内写明"FEA-03 defer 的 wire 承接指针已移至 <目标 Task>"；选 (b) 翻 `blocked` 并先做 M2-C1 类字节修订 |
| **P2-8** | P2 | 卡 `:97`（禁止范围） | 「不改 `doc/reviews/**`」对实现者为真，但本报告与后续 `doc/reviews/FEA-04-r1.md` 由 Review Appointment 的审查者写入，卡内未区分写权主体，易被实现者误读为"复审报告也不许写" | 加一句「`doc/reviews/FEA-04-*.md` 由 Review Appointment 的上下文独立审查者写入，不属实现写域」 |

---

## 最小修改清单（可直接照改，供 DSH 处置参考）

1. `:23-34`：`tests/**` → `tests/NewManga.App.Tests/**`（+ 可选 `tests/NewManga.ApplicationCore.Tests/**`）。
2. `:52`（R-CURRENT-3）：补「本卡不新建独立工程；`Frontends.Current` 落 `Shell/V2/Frontends/`」。
3. `:56`/`:81`：补有损集合谓词 + `SwitchPreflightResult` 形状 + "Code 不进 wire" 约束。
4. `:58`/`:82`：补 AC6 三项可执行断言 + "现状 V2 本就不 Dispose" 基线。
5. `:61`/`:62`：R-SWITCH-1 收窄为 preflight-only；R-SWITCH-2 改为"preflight 不触发新 Run/新投影源"。
6. `:77`/`:78`：AC1 降为入口级；AC2 改 `NewManga.sln` 命令 + 冻结 1052 基线。
7. `:68-73`：S1–S3 目标权威改为 ApplicationCore 本地权威 + 显式 defer wire（随 DSH 裁决 F-01）。
8. `:96-98`：禁止范围改写（F-01/F-11），并写明 `NewManga.App.csproj`/`NewManga.sln`/`App.axaml.cs` 的 DSH 单点提交规则。
9. `:14`/`:43`/`:84`/`:91`：`base_commit` 重钉、行号更正、AC8 去轮次、L-2 联动。

---

## 边界声明

本报告**只审范围冻结**（Task 卡 + 其引用的方案/授权/前置/代码事实），**不构成实现验收**，也不构成任何设计或契约批准。结论中的"通过/不通过"仅指范围冻结文本是否可执行、可机械验证、与方案和治理指针一致；实现期的一切 AC 仍需按卡的独立实现复核与 DSH 集成验证。本席位**未参与** FEA-04 的起草、实现或返修，**未执行**构建/测试/真机运行，**未修改**任何被审文件、卡、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内所有代码行号基于 `e34796862` 实测，行号存在性不证明调用链完整。
