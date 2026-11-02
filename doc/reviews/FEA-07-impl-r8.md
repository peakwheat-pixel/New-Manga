---
task_id: FEA-07
reviewer: Codex CLI（fresh independent context r8；model gpt-6.1-sol, reasoning effort high）
reviewer_kind: agent
author: DSH
base_commit: cbfb7bbc92d489541a24290038eae2117f8aa1ce
reviewed_head: b6b63574d（文档/证据 head；代码 head 462141f57）
code_head: 462141f57f7b00b34577dbf04d8415be7ab5fe95
decision: changes_requested
counts:
  P0: 0
  P1: 0
  P2: 2
---

# Review：FEA-07 第 8 轮实现复核（impl-r8）

## Reviewer 身份与来源

本报告由用户本轮明确委派的 fresh Codex CLI 独立上下文执行，未参与 FEA-07 的设计、实现或返修。来源为本轮只读委派、`doc/handoffs/FEA-07-impl-r7.md` §4、当前 rolling checkpoint §65；不以自报 session ID 代替独立性依据。主会话执行 Git/调用链/测试/证据核对及报告落盘。`code-review` skill 辅助只读审查来源为 `/root/standards`（Standards/Architecture）及 `/root/spec`（Spec/Verification），均未写文件、运行测试、参与实现或进入其他 worktree。Architecture、Verification、Standards、Spec 四个视角均为 **executed**。

唯一主动交付写入为本报告；未修改代码、测试、Task、STATUS、既有证据、历史 Review 或用户数据，未 commit/push，未进入其他 worktree。按用户要求执行的 build/test/生成器检查产生常规忽略构建输出和测试自带临时夹具；全量性能用例另写其固有 `%TEMP%/nm-fea07-performance-baseline.json`，未回写 canonical JSON。未启动连接真实用户数据的产品，未写真实 `%APPDATA%/NewManga`。未修改旧实现或另建文件做 mutation test。

## 范围与 Reality Check

- 起始及报告写入前：`HEAD=b6b63574dad55ac1db30e483e2a2ed07f081dada`、branch `main`、common dir `.git`、工作路径 `G:\CODEX\New Manga`，`git status --short` 为空。**RESUME_SAFE**：Git 与用户固定 head、Task、STATUS、PLAN、checkpoint §64–65 一致。
- 已实跑 `git rev-parse HEAD`、`git status --short`、`git log --oneline -6`、`git diff --stat cbfb7bbc9..HEAD`、`git diff --name-only cbfb7bbc9..HEAD`。累计 **86 files changed / 8842 insertions(+) / 562 deletions(-)**；逐条按 Task `allowed_paths` glob 核对，**86/86 合法，越界 0**。three-dot diff stat 与此相同。
- `462141f57..b6b63574d` 仅 9 个 docs/evidence 文件：PLAN、STATUS、rolling checkpoint、impl-r7 handoff、impl-r7 Review、Task、index、final log、性能摘要。`git diff --quiet 462141f57 b6b63574d -- apps/desktop-avalonia` **exit 0**；两端源码树均为 `5e2329bfe4c6a239621905bc8aa55bae61753a61`。
- 本轮代码增量 `git diff 5a495f80a 462141f57 -- apps` 仅四个文件：`FrontendHostCoordinator.cs`（+19/-2）、`IPresentationWindowModeTransaction.cs`（+15）、`PresentationWindow.cs`（+76/-16）、`PresentationWindowTests.cs`（+176）。没有新增依赖、Core/schema/冻结契约/生成物变更。
- 读取用户指定 r7/r6 Review、Task、STATUS、PLAN、final/index/rework-r7/handoff，并按引用读取当前 checkpoint、性能摘要/JSON、AD-002 当前有效边界（含 AD-003 修订提示）、协作协议 §4/§5.1 与 Review 模板。未扫描其他 Task 或无关历史 verification。

实际 `git log --oneline -6`（exit 0）：

```text
b6b63574d docs(fea-07): impl-r7 处置 + 返修证据/索引 + delivery/生命周期固定（head 462141f57；全量 1138/0/57）
462141f57 fix(fea-07): r7 返修（R-022 取消路径窗口模式补偿 / R-024 门内快照防陈旧恢复 / R-023 判别性测试）；全量 1138/0/57
226e47c51 docs(fea-07): impl-r6 approved + R-022 修复处置/证据/索引（head 5a495f80a；全量 1135/0/57）
5a495f80a fix(fea-07): r6 R-022 失败切换恢复原窗口全屏模式（含回归测试）；全量 1135/0/57
80b2203e5 docs(fea-07): impl-r5 处置 + 返修证据/索引 + delivery/生命周期固定（head 4e8510d43；全量 1134/0/57）
4e8510d43 fix(fea-07): r5 返修（R-020 Fluent 全屏桥接到稳定窗口 / R-021 重复通知测试判别力 / 性能口径措辞）；全量 1134/0/57
```

下文源码行号均以 **`462141f57`** 为准，文档行号以 **`b6b63574d`** 为准。源码简称相对于 `apps/desktop-avalonia/src/NewManga.App/`；`FrontendSwitchCoordinator.cs` 位于 `src/NewManga.Presentation.Avalonia/Switching/`；同名测试位于 `tests/NewManga.App.Tests/`。

## r7 findings 闭环表

| ID | r7 状态 | r8 Verdict | 依据与边界 |
|---|---|---|---|
| R-022 残余 | P2 open，取消遗漏 | **实现闭环，当前故障用例 PASS** | 模式快照在 coordinator gate 内生成，失败返回/异常/取消均经 finally Dispose，发生在释放 gate 前；成功且 journal finalize 完成后才 Commit。两个真实全屏 Promote 后故障用例全量及定向均通过，取消继续传播 OCE。 |
| R-024 | P2 open，门外陈旧快照 | **实现闭环；对应回归判别力未闭环，计入 R-023** | reject/no-op 先于快照，`previous` 与模式快照属于同一持门事务；排队后拒绝没有快照可恢复。新增测试屏障设在 Promote 后，不能捕获原陈旧 FullScreen，详见 finding。 |
| R-023 | P2 open，故障测试无判别力 | **Promote 后失败/取消部分闭环；排队用例仍 open/P2** | finalize fault 能确认已完成 Promote；正常故障覆盖树/VM/Window/journal，取消覆盖 OCE/树/VM/Window。排队测试在 FullScreen 已变 Normal 后才调用第二请求，旧门外快照同样满足最终 Normal。 |
| R-007 | P2 open，appointment 文案 | **交付关联正确，文案仍 open/P2** | reviewer 记录最新已完成 r7，delivery 精确为 `462141f57`，handoff/final/index 相符，canonical=pending 正确；Task/索引仍写 r8 待派，与 STATUS/PLAN/checkpoint 和本次已执行不一致。 |

更早 findings 状态：R-001–R-006、R-008–R-021 维持 r6/r7 已记录的闭环或有边界的闭环，不因本轮新增模式事务重新打开。具体包括：真实 staging/缓存状态保留（R-001）、全 cache 与生产 Theme Studio draft 退出聚合（R-002）、启动恢复/planner 单源（R-003/004）、拓扑接线但原生未验（R-005）、临时根/写域（R-006/008）、性能数值及其 PARTIAL 边界（R-009）、缓存/pins/生成物（R-010–012）、同门串行化（R-013）、memento（R-014）、finalize settings/id/UI 补偿（R-015）、索引完整性（R-016）、canonical/draft 同步（R-017）、Loaded 解绑（R-018）、staging 输入隔离（R-019）、全屏接线及重复通知判别力（R-020/021）。本轮增量未改这些行为；全量相关回归通过。它们不等于 AC1–AC8 已完整验收，原 PARTIAL/D-1 继续保留。

## 本轮重点实现判断

### 窗口模式事务与补偿顺序

`Services/FrontendHostCoordinator.cs:93–116` 先取得 `_switchGate`，随后做未知 frontend 拒绝、同 frontend no-op，才取 `previous`；`:184` 将同一旧树传给 `_windowModeSnapshot`。`Views/Presentation/PresentationWindow.cs:290–293` 同时保存 WindowState、旧 Fluent surface 身份及 reader VM 全屏值。没有门外快照，也没有在 coordinator 返回之后恢复的窗口。

switcher 完成全部提交步骤及 journal finalize 后才返回成功（`FrontendSwitchCoordinator.cs:104–115`），coordinator 才调用模式 `Commit()`（`:186–193`）。普通失败先恢复内容/settings/id（`:167–178`）；取消由 switcher `:135–147` 回滚后重抛。两者及其他异常都进入 coordinator finally：先解绑 Loaded，再 Dispose 模式，最后释放门（`:197–204`）。因此在现有调用链中，旧树先恢复，模式补偿后完成，下一个请求才可能取得 gate；拒绝/no-op 请求未生成事务，不会写回前一事务模式。等待 gate 时取消直接传播，也没有快照或本次 UI 修改需要恢复。

`PresentationWindow.cs:296–306` 仅对仍可见的同一 Fluent 树恢复 VM，WindowState 有差异才赋值；没有调用 `FullScreenRequested`。`FluentPageViewModels.cs:885` 的 setter 只做 Set/属性通知，不重新请求全屏，不递归切换。事务 `:329–339` 的 Commit/Dispose 共用 `_completed`；Dispose 在恢复前置完成标志，重复 Dispose 不再恢复，成功后 Dispose 不触窗口。快照只活在当前事务局部变量，没有新增事件订阅或长期保留集合，未发现有据的泄漏/覆盖后续事务问题。

成功离开 Fluent 仍走 `PresentationWindow.cs:212–223`：清 reader 全屏，仅当窗口原来 FullScreen 时改 Normal；Commit 后不恢复快照，R-020 策略保持。原 Normal/Maximized 不被该分支无条件改为 Normal；失败补偿恢复所捕获的枚举。现有 Normal 失败/memento 最大化用例通过；**没有新增 Promote 后 Maximized 故障矩阵实跑**，不把 memento 测试当作该矩阵证据。

### 三个新测试的阶段、断言与反事实

`PresentationWindowTests.cs:373–399` 用真实 Fluent surface、真实 reader 全屏按钮和稳定 Window；目标 V2 为普通 Control 夹具。`:380` 的 `beforeJournalCommit` 只在 CommitAsync 已 Promote、保存设置并更新 frontend id 后执行（switcher `:113`，coordinator `:147–164`）。因此 `Assert.Contains("finalize failed", result.Failure)` 排除了 Building 提前失败后误过；`:390–394` 覆盖原树、VM、Window、RolledBack journal。它确实能捕获 r6 报告所审的 **`4e8510d43` 无补偿实现**；`5a495f80a` 已修普通失败，该用例在此版本通过是合理的。

取消用例 `:408–435` 在同一 finalize seam 先取消本次 token，再抛 OCE；`:426–431` 验证 OCE 传播及原树/VM/Window。旧 `5a495f80a` 的 wrapper 只处理返回失败，会跳过该恢复，因而这次断言有判别力。取消用例未断言 journal、frontend/settings；普通故障也未重读持久设置，settings/id 补偿由既有 coordinator finalize 测试和本轮调用链补充，不能称三个新测试逐项全覆盖。**旧 head/mutation 的实际反向执行为 NOT_RUN**，以上为明确的静态反事实，过程证据也未提供反向实跑 artefact。

排队用例 `:444–480` 在 finalize 阻塞第一事务，确实可使第二请求等待 gate；但该时点已经 Promote，旧 Fluent 全屏已被清成 Normal，`:468` 才发起第二请求。旧门外快照此时也只能取 Normal，所以它同样通过 `:476`。这证明队列可以运行，不能证明 R-024 的陈旧 FullScreen 已受回归保护。屏障比 sleep 有确定性，但 `Wait(10s)` 返回值未断言、未断言第二任务尚未完成，也未在 finally 释放屏障；本轮全量与定向均通过，未观察到 hang/flaky，不把这些清理细节单列代码缺陷。关键问题是阶段选择，见 R-023 残余。

### 兼容与回归

本轮四文件增量未修改 standalone FluentShell、V2/输入、关闭路径或 appearance 唯一写者。standalone `FluentShell.axaml.cs:43–45` 继续将 surface 请求接到自己的 Window；稳定宿主的可见树事件与隐藏请求守卫 `PresentationWindow.cs:193–252` 保留。全量包含真实组合根全屏按钮/F/Esc、缓存树退出、V2 键路由、staging 输入隔离和既有 Fluent facade 回归。没有证据支持新增重复订阅、递归全屏或 Host 生命周期回归；原生焦点/IME/多屏仍未验。

## Standards

**executed；0 个新增问题。** 辅助 `/root/standards` 未发现本轮增量违反 Task W-6/W-10、AD-002 分层/依赖方向、唯一写者或源数据保护约束；App 内模式 seam 没有改变共享契约。gate、恢复顺序及幂等性符合事务边界。没有以 Fowler smell 判断项新增纯风格 finding。

## Spec

**executed；1 个验证残余（R-023）。** 辅助 `/root/spec` 按原顺序指出：排队测试在 Promote 后才捕获第二请求，旧门外快照实现也可通过；普通故障/取消用例真实到达 Promote 后且有对应模式判别力；R-022/R-024 实现与 Task AC1 的恢复/串行化要求相符，无新增范围扩张。该验证残余只计一次；R-007 由主会话核对。

## Findings

本轮仍需处置：**P0=0 / P1=0 / P2=2**。R-024 实现本身不重新计缺陷；未将如实登记的原生 D-1 与其他既有 PARTIAL 重复计为新增 finding。

| ID | 级别 | 文件/行 | 触发、影响与依据 | 复现证据 | 最小建议 | 状态 |
|---|---|---|---|---|---|---|
| R-023 残余 | **P2** | `PresentationWindowTests.cs:453–476`；coordinator `:147–164`；switcher `:113`；`PresentationWindow.cs:212–223` | Task AC1/r7 R-024 要求覆盖 staging 期间排队、第二请求旧 FullScreen 被错误写回。新增用例等 finalize 已清全屏后才发起第二请求；旧门外快照此时为 Normal，仍满足最终 Normal。测试不能捕获刚修复的并发回归，Task/handoff 的判别性闭环声明过宽。 | 当前全量及定向均 PASS；静态核对旧 `5a495f80a` wrapper 与新测试调用顺序确认反事实。未改代码执行 mutation，反向实跑 **NOT_RUN**。 | 将第一事务屏障移至 Promote 前，确认旧树/VM/Window 仍全屏时发起 B；证明 B 尚未完成，再释放 A。断言 A 成功、B 拒绝且未回滚、最终目标树/旧 VM 清全屏/Window Normal、frontend/settings/journal 保留 A 提交。提供能区分门外快照旧实现的证据，失败路径释放屏障。 | open；普通失败/取消测试部分已闭环 |
| R-007 | **P2** | `doc/tasks/FEA-07.md:10,253,255`；`verification/FEA-07/evidence-index.md:9` | Task/索引仍称 r8 待派，而 STATUS `:7,10`、PLAN `:21,39`、checkpoint §65 及本次实际执行均为 r8 已派。delivery/handoff/最新已完成 r7 关联正确，canonical=pending 正确；问题仅为当前 appointment 文案。 | 本次派发及仓库文本直接核对；无交付 SHA 失配。 | DSH 接收报告时统一 r8 reviewer/source/实际结果、handoff/索引及当前指针；历史 Review 保持原字节，未集成/残余处置前继续 pending/in_progress。 | open，r7 文案残余 |

## AC 逐条 Verdict

| AC | r8 Verdict | 依据与剩余边界 |
|---|---|---|
| AC1 | **PARTIAL** | 真实树/草稿/会话、staging 门禁、输入及普通故障/取消窗口补偿通过；R-024 门内实现成立，但对应排队测试判别力残余 R-023。原生 IME、真库 DB/current/pinned/Lock/source/candidate 零变化、ACK 重连及真实 Run/Intent 仍未验。 |
| AC2 | **PARTIAL** | visible/staging/cache 退出聚合、生产 Theme Studio draft 与关闭阻断回归通过；真实双窗归属、Session/Region 单写 owner、完整 Host 生命周期集成未补。 |
| AC3 | **PARTIAL** | journal/启动恢复/finalize 补偿与本轮取消传播通过；真实跨进程 kill、暂停期间保护状态变化未验，排队模式测试边界见 R-023。 |
| AC4 | **PARTIAL** | planner 单源、fallback warnings、隔离启动兼容矩阵回归通过；真实 App 初始化与坏包/scale 完整矩阵仍缺。 |
| AC5 | **BLOCKED / D-1（原生矩阵）** | headless 全屏主路径、普通故障/取消补偿、memento/topology/PerMonitorV2 机械验证通过。原生双屏/拔屏/换主屏/混合 DPI 100/125/150/200%、第二窗回迁 **NOT_RUN**，保持 BLOCKED，不能由 headless 替代。 |
| AC6 | **PARTIAL；W-5 PASS** | canonical p50 99.28 / p95 374.09 / max 389.99ms，记录两次 p95 299.40/374.09；本轮全量 Debug 性能用例 p95 466.34ms≤1000。UI freeze 仍是事务时长上限，真实规模 workload/原生冻结采样未补。 |
| AC7 | **MET（已列机械/headless 范围）** | 本轮 build 0/0、全量 1138/0/57；startup/依赖方向/net9.0 门禁通过。57 skipped 的真实 sidecar 链路不能当已验。 |
| AC8 | **PARTIAL** | 临时根、20/20 Task pins、15/15契约 pins、两生成器/治理通过；R-023 排队判别证据与 R-007 appointment 残余、原生截图/矩阵仍缺。 |

## 证据与治理核对

以下为本轮 **executed**，除明确 NOT_RUN/BLOCKED 项。执行 shell：PowerShell **7.6.8**；OS：Windows NT **10.0.26300.0**；SDK：**10.0.401**；测试 runtime：**.NET 9.0.11**。HEAD 为 `b6b63574dad55ac1db30e483e2a2ed07f081dada`，源码等同固定 code head；结果直接记录于本报告，不覆盖已有 verification 日志。

| 场景 | 本轮命令/步骤 | EXIT / 结果 | 关键输出与边界 |
|---|---|---|---|
| Git/写域 | 前述五项 Git 命令及 branch/common-dir、glob 核对 | **0 / PASS** | main/.git、起始干净；86/86 合法，源码树两端相同。 |
| Build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | **0 / PASS** | **0 warnings / 0 errors**，6.12s。 |
| 全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | **0 / PASS** | **1138 passed / 0 failed / 57 skipped**；App 2m41s，计数见下表。 |
| 新用例定向 | 下列完整定向命令 | **0 / PASS，3/0/0** | finalize failed 631ms；queued rejected 127ms；cancelled after promote 131ms。当前 PASS 不替代旧实现判别。 |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | **0 / PASS** | 292 rows；every generated artifact matches frozen token source byte-for-byte。 |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | **0 / PASS** | generated theme artifacts match frozen token source byte-for-byte。 |
| 治理 | `pwsh -NoProfile -File tools\governance\check.ps1` | **0 / PASS，3 warnings** | 15 current documents；10 个非终态 Task、STATUS 3138 bytes/29 lines、PLAN 4759 bytes/64 lines 的既有告警。机械通过不替代语义批准。 |
| 契约 pins | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | **0 / PASS，15/15** | 14 契约 + FEA-01；与 Task artifact pins 分开核对。 |
| Task pins | 解析 Canonical Evidence 20 行，Get-FileHash SHA256，与索引对应唯一路径行三方核对 | **0 / PASS，20/20** | 19 CANONICAL + 1 SUPPORTING；索引非法控制字符 0，自引用 SHA 表行 0，完整 SHA 见附录。 |
| final evidence | head/实际 SHA/Task/index 对照 | **PASS** | head=`462141f57f7b00b34577dbf04d8415be7ab5fe95`；SHA=`dbfb7666ec8ab29dcc9685b5f0a687fc4deecc6c7e80d7512a9ea699c5650bb3`。 |
| 过程/handoff | rework-r7、final、Task、handoff 对照 | **PASS（交付关联）；文案有 R-007** | rework 为 `226e47c51 + uncommitted rework`，final 单独绑定提交后 head；1138/0/57、两次性能值一致。未将过程日志冒充精确已提交 head。 |
| 性能一致性 | JSON样本排序重算，核对摘要/Task/index/handoff/rework | **PASS；W-5 PASS** | 20 样本第10项99.28、第19项374.09、max389.99ms；4预热+20单向切换；两次复测299.40/374.09ms。 |
| 本轮性能 | 全量 Debug 中 `PerformanceBaselineTests.HotSwitch_P95_StaysWithinTheFrozenW5Budget` | **PASS** | 临时 JSON：p50 156.76 / p95 466.34 / max480.45ms，冷首次326.54ms，内存-76760B，handles +1。独立 Debug 数值不替换 canonical Release，也不证明长期泄漏趋势。 |
| 反向判别 | 旧 head/mutation 执行 | **NOT_RUN** | 只读边界下未修改实现/测试、未进入其他 worktree；静态反事实与当前 PASS 分开记录。 |
| 原生矩阵 | 双屏/拔屏/换主屏/混合 DPI 100/125/150/200% | **BLOCKED / D-1；NOT_RUN** | 未执行原生硬件验收，不签发该验收。 |

定向命令（exit 0；普通 `|` 为 VSTest filter OR）：

```powershell
dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter 'FullyQualifiedName~FailedSwitchAfterPromote_RestoresTheOriginalFullScreenMode|FullyQualifiedName~CancelledSwitchAfterPromote_RestoresTheOriginalFullScreenMode|FullyQualifiedName~QueuedRejectedSwitch_DoesNotRestoreAStaleWindowMode' --logger 'console;verbosity=normal'
```

### 全量计数与 skip 直接原因

| 项目 | passed | failed | skipped | 原因 |
|---|---:|---:|---:|---|
| Appearance | 21 | 0 | 0 | 无。 |
| Presentation.Avalonia | 38 | 0 | 0 | 无。 |
| Host | 51 | 0 | 28 | HostFixture sidecar 前置未满足。 |
| ThemeEngine | 253 | 0 | 0 | 无。 |
| DesignSystem | 87 | 0 | 0 | 无。 |
| ApplicationCore | 31 | 0 | 0 | 无。 |
| CoreClient | 128 | 0 | 22 | SidecarFixture sidecar 前置未满足。 |
| App | 529 | 0 | 7 | CreateChapterHostIntegration 2、RunControllerHostIntegration 3、WritePolicyUiIntegration 1、StartupSelfCheckUi 1，sidecar 前置未满足。 |
| **总计** | **1138** | **0** | **57** | **1195 tests；28+22+7=57**。 |

实测环境变量 `NEWMANGA_CORECLIENT_SIDECAR_DIR` **UNSET**。Host `Support/HostFixture.cs:13–20`、CoreClient `Support/SidecarFixture.cs:28–35` 先于目录/可执行文件及其他夹具检查返回 skip；App 的 CreateChapterSidecarFixture、RunFixture 与 WritePolicySidecarFact 走同一变量前置（`ChapterCreationTests.cs:274` 起、`RunControllerTests.cs:480` 起、`WritePolicyUiTests.cs:132` 起）。直接原因不是 BOOK/S4 等后续 fixture；未设置变量或伪造夹具转成 PASS。相对 r7 的1135/0/57增加3 passed，相对Task基线1034/0/57增加104 passed，fail/skip不增。

性能口径限制继续保留：20 单向切换等于10次往返，nearest-rank 第19项为p95；历史12样本的p95取max同样是合法小样本分位数。摘要“才是真正的p95”仍是不严谨的历史措辞，已由前轮记录，不重复新增 finding。事务总时长仅为 UI freeze 上限，不能宣称完成真实规模/原生冻结采样。

## Architecture 与 Verification 结论

**Architecture：本轮实现修复成立。** R-022 取消/异常模式补偿与 R-024 门内快照、成功路径清理、幂等性在现有调用链下符合事务要求，未发现本轮新增分层/依赖/唯一写者/数据保护越界。Normal/Maximized 的静态恢复语义保留；原生矩阵及完整窗口故障矩阵未据此升级。

**Verification：指定机械检查全过，关键并发回归的判别力仍缺。** 普通故障/取消用例已真实达到 Promote 后；排队用例仍无法捕获 R-024 原缺陷。依 Review 模板“P0/P1 未解决或关键验证缺失时不可批准”，不以1138/0/57、当前用例PASS或静态实现正确代替该关键验证。R-007 为非阻塞文案残余；AC1/2/3/4/6/8 保持 PARTIAL、AC7 限定范围 MET、AC5 原生 BLOCKED/D-1。

## 结论与复审

**Decision：`changes_requested`（P0=0 / P1=0 / P2=2）。** R-022/R-024 实现问题闭环；最小返修落在 R-023 排队测试判别力及 R-007 当前 appointment 文案，不要求重写模式事务。此报告不是 Task done、集成或 push 授权，不撤改历史 r6 approved/r7 changes_requested。

最小返修集：

1. DSH 修正排队测试的 **Promote 前**屏障和排队未完成断言，补最终树/VM/窗口/提交状态断言与安全释放；以门外快照旧实现不能通过为判别标准，记录真实反向证据或明确 NOT_RUN，不能继续以当前全绿宣称已证。
2. DSH 更新 r8 reviewer/source/结果及 Task/handoff/index 的 appointment；固定新交付 head，刷新精确 head final/index/Task pins。历史 Review 保持原字节；原生 D-1 与既有 PARTIAL 继续明确登记。
3. 重跑本报告 build、全量、两 `--check`、check/pins、20项Task SHA和性能一致性，fresh上下文复审后由DSH决定集成/生命周期；不得自动释放 proposed 的 FEA-06-RESIDUAL-1。

推荐下一步：**DSH 继续当前 FEA-07 验证返修与复审**；接收本报告并 Reality Check 后即可在已冻结 Task 范围内处理。Recovery point 为 `G:\CODEX\New Manga`、main/.git、base `cbfb7bbc92d489541a24290038eae2117f8aa1ce`、文档 head `b6b63574dad55ac1db30e483e2a2ed07f081dada`、代码 head `462141f57f7b00b34577dbf04d8415be7ab5fe95`。允许 Task allowed_paths 内必要测试与交付/治理文档；生产代码如无需修改应保持当前实现，不扩大共享接口/schema/依赖授权，不动 Core/冻结契约/生成物/真实用户数据/其他worktree。本次不关闭整个Task。

可直接转发给 DSH：

> 在 `G:\CODEX\New Manga`、main、common dir `.git` 继续 FEA-07；base=`cbfb7bbc92d489541a24290038eae2117f8aa1ce`，文档head=`b6b63574dad55ac1db30e483e2a2ed07f081dada`，代码head=`462141f57f7b00b34577dbf04d8415be7ab5fe95`。先核对Git并保护dirty及本报告原文。按 `doc/reviews/FEA-07-impl-r8.md` 处理R-023残余：把排队拒绝测试屏障放到Promote前，先确认旧树/VM/Window仍FullScreen，再发起并证明B排队，释放A后检查A成功/B拒绝、最终树/VM/窗口及frontend/settings/journal不受B覆盖，提供旧门外快照的判别证据并安全释放屏障。R-022/R-024实现已闭环，无需扩大实现；同时统一R-007的r8 appointment/source/结果及Task/handoff/index。只在Task allowed_paths内改必要测试/交付文档，不改Core/schema/冻结契约/生成物/共享依赖/真实用户数据，不进入其他worktree。交付固定commit、测试及反向判别结果、handoff、精确head final/index/pins。执行本报告完整build/test（当前1138/0/57，新增另计）、两--check、check/verify_pins、Task20项SHA核对与W-5 p95≤1000ms检查，逐项记录skip/BLOCKED/NOT_RUN。保留AC5原生BLOCKED/D-1及其他PARTIAL，完成后Appointment fresh只读复审，再做集成与closeout；不自动释放FEA-06-RESIDUAL-1。

## 附录：20 项 Task evidence SHA-256 三方核对

逐项实测 SHA 均与 Task Canonical Evidence 及索引对应唯一路径行相同，**20/20 PASS**。PERF-MD 为 SUPPORTING，其余19项为 CANONICAL。索引自身 SHA 仅在本报告外部记录：`3afe473f35b8eeeb87643fe907810f44ccf10472c40dae8c1593720f34f16ba6`，没有写回索引自 pin。

| evidence_id（EV-FEA07-） | 实测 sha256 |
|---|---|
| SLICE1 | `a63982423ba6e79f96f76bacc27049a2bba18506fdf9411c13df0c5f13dac78d` |
| SLICE2 | `55fd5e5fb1c5a9a146e3cda5e5a8087ebff4beeee9a5c480e81d539d6bbfe771` |
| SLICE2B | `2c281f288af106ed5391eea065aaac25f8f6543063a5aecab0f7ec11a4cee88b` |
| SLICE2C1 | `d835a23daf53d64d90fbe026f3307570b74df6778a7f1c50f61e60cfe63ee7f1` |
| SLICE2C2 | `7b848ca1a773e82e0b1faa1ee3e1a7f2d54f8ca49f2e0b3faaa80702ecb75973` |
| SLICE3 | `bb11ca80e77ad3345a7410c5b0b8a7818a2df0f2ce329460d4007cc9e1886b26` |
| SLICE4 | `3197f8b536114bfd7c78c45ab362bf85a62edd0b370363cce03a30ec204b4ed0` |
| SLICE5 | `098d9991a0d0c7303ce7c6093b45179c4b16ccbf7516583a655257b906478ed9` |
| PERF | `26eb150a100904fbabe4708c71ac3cb8040cb7e4012e2c19a6eaaa8048c480bf` |
| GAPCLOSING | `29e10eff99acb7beee864e316c0171d09f196ef51fa41a4c7e5ea73c3ffe3230` |
| GENERATORS | `c14b314350fdb2fd9d88cfa9df4cd5f46e236d3f41964c25ca1252545b48c921` |
| FINAL | `dbfb7666ec8ab29dcc9685b5f0a687fc4deecc6c7e80d7512a9ea699c5650bb3` |
| PERF-MD | `a1559f8595570d5f3688568150faf56c34aea291bc6d9fd4fe1777cbd94dc84f` |
| REWORK2 | `725ec7f6e4d6295f386d0bb08a65771158536fc7fa02e7a4f640a713f38eaa01` |
| REWORK-R3-1 | `c6eefffef4fa6a2f9d7e0afa1b91f2ddff8110da2aa2b3c965293095c4e696a9` |
| REWORK-R3-2 | `aacf4ce239fb978d614dc4d958454fde084ed219d9d806940a7225743aaf3b28` |
| REWORK-R4 | `f0cb74032c50e3b24fede26b59d053beef07f9a8a337fd7ec52bacd27c5a4c3b` |
| REWORK-R5 | `e773a93def145d258ff09f8cb02ae9783823e7588e06443de28ba3381a3619b9` |
| REWORK-R6 | `322475cb618a71cf1f69e3422908a4d2b435ac53567462ffe1ba2309b01c5ae9` |
| REWORK-R7 | `9e4e04bd57bd9eadc238dd334b4cd502817fcfd2c7e8ac4904534b6c586e1144` |

落盘后复核：`check.ps1` 再跑 exit 0 / PASS（同3个告警）；HEAD 未变，`git status --short` 唯一条目为 `?? doc/reviews/FEA-07-impl-r8.md`，无其他 tracked/untracked 改动；报告附录20项SHA均与Task一致。未提交或推送。
