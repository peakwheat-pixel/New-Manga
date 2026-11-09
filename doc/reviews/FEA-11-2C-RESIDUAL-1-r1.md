---
task_id: FEA-11-2C-RESIDUAL-1
review_round: r1
reviewer: DSH 主会话 session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发的独立上下文只读子代理（subagent，r1）
reviewer_kind: subagent
author: dsh
base_commit: ac64cb134
reviewed_head: c30c1647e
decision: approved
---

# Review：FEA-11-2C-RESIDUAL-1（2C 残余：预算超限分支保留 typed stop）

## 0. 审查者来源与独立性

- 本报告由 DSH 主会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5` 派发的**独立上下文只读子代理**完成，`reviewer_kind: subagent`。该子代理未参与本 Task 的实现（`a2c4c1d8c`）或 in_review 文档提交（`c30c1647e`），未持有实现会话上下文。
- 全程只写**一个**文件（本报告）：未修改生产源码、测试、任务卡、契约、pins、`verification/**` 既有字节；未 commit / push。
- 唯一一次对生产文件的临时写入是**任务书明文授权的变异实验**（`RunGrantRenewal.cs` 内删除 4 行 Stop 优先分支），已按任务书要求还原并复核字节（见 §6 #5；还原手法与 EOL 说明见 §6 #5 注）。
- 审查开始时 `git status --short --untracked-files=all` 为**干净**（空输出）；结束时除本报告外同样干净。

## 1. 被审 head 与范围

| 项 | 值 |
|---|---|
| 被审 head | `c30c1647e`（docs: in_review）——文档提交，不改代码 |
| 实现 head | `a2c4c1d8c`（fix: 预算超限分支保留 typed stop，+3 判别测试） |
| base | `ac64cb134` |
| 实现 diff | `ac64cb134..a2c4c1d8c`：8 文件 +548/−3（源码 +23/−3、测试 +77、卡 +99、证据 5 份 +362） |
| in_review diff | `a2c4c1d8c..c30c1647e`：5 文件（`STATUS`/`REBASELINE_PLAN`/`TASK_LEDGER`/卡状态/Handoff） |
| `allowed_paths` | 源码 1 文件 + 测试 1 文件 + 卡 + review/handoff glob + `verification/FEA-11-2C-RESIDUAL-1/**` |
| 实测 `out_of_scope` | `git diff --stat ac64cb134..a2c4c1d8c -- doc/plan doc/contracts tools/governance HostRuntime.cs CoreClient *.csproj *.props *.targets src tests` = **空**（EXIT 0） |
| 预算常量 | `DefaultIntervalSeconds=240` / `RoundBudgetSeconds=50` / `DefaultMaxRenewals=12` 在 diff 中**零命中**（未改） |

**生命周期文件说明（非 finding）**：`c30c1647e` 还改写 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`，三者不在卡 `allowed_paths` 内，但属 DSH 生命周期写入，与前一 Task 的收口提交 `7abc9194a`（同样改这三份文件）一致；AC5 的「diff ⊆ allowed_paths」对**实现提交**成立。建议后续卡把三份生命周期文件或「lifecycle carve-out」写进 `allowed_paths`，避免该子句只能靠惯例解释。

## 2. Verdict

**`approved`**：P0 = 0 / P1 = 0 / P2 = 0 / **P3 = 4**。

- 修复口径与卡 §修复口径**逐行一致**，无契约/wire/依赖/常量变更，无 scope creep（`out_of_scope` 实测空 diff）。
- AC1–AC5 **全部 MET**；既有 `Renewal_RoundOverBudget_SkipsTheRoundAndKeepsTracking`（Renewed 路径）仍绿，其余 renewal 用例未受影响（Host.Tests 全量 305/0/72 复跑一致）。
- **变异判别由本审查独立重做**：移除 Stop 优先分支 → `RoundOverBudget` 子集 **2 failed / 2 passed（EXIT 1）**，与入库 `mutation-red.log` 的失败用例、断言行号完全一致；还原后 22/22（EXIT 0）。
- 4 项 P3 均为证据卫生/代码一致性 nit，不改变功能判定；其中 R-01 建议在关账前顺手处置（不改 head 也可，见建议）。

## 3. 修复口径核对（卡 → 实现 → 测试）

| 卡 §修复口径 | 实现（`RunGrantRenewal.cs`，还原后行号） | 判别测试 | 判定 |
|---|---|---|---|
| `Renewed` → `_renewals++` 后 `SkippedBudget`（保留既有语义） | `:379-385`（先计数，再 `BudgetSkip("RENEWAL_ROUND_BUDGET_EXCEEDED", outcome.BoundPages, MintedGrants, SkippedSources)`） | `RunGrantRenewalTests.cs:239-277`（既有，断言 `BudgetSkips=1`、`Renewals=1`、`LastCode=ROUND_BUDGET_EXCEEDED`） | **一致** |
| 任意 Stop 类 → `Stop` 原样，typed code 保留 | `:387-390`（`!outcome.KeepsTracking` → `Stop(runId, outcome)`；`KeepsTracking` 仅 `Renewed/SkippedBudget` 为真，见 `:49-52`） | `:279-306`（`StoppedTyped`/`SOURCE_GRANT_DENIED`）、`:308-328`（`StoppedTerminal`/`RENEWAL_RUN_TERMINAL`） | **一致** |
| `SkippedBudget`（内部已判预算）→ 保留自身 code | `:392-397`（`outcome.Code ?? "RENEWAL_ROUND_BUDGET_EXCEEDED"`） | `:330-354`（`RENEWAL_ROUND_CANCELLED` 保留、`BudgetSkips=1`、`IsTracking=true`） | **一致** |
| 其它 → 通用 `RENEWAL_ROUND_BUDGET_EXCEEDED` | `:399-401` | 无（当前 7 值枚举下不可达，见 R-04） | **一致（防御性，不可达）** |

补充核对：

- 计数语义符合 AC1/AC2：Stop 路径 `_stops++`、`_lastCode = typed code`、`BudgetSkips` 不增（`Stop()` `:447-468`）；Renewed 路径先 `_renewals++` 再 skip（`BudgetSkip()` `:428-445` 只做 `_budgetSkips++`/`_lastCode`）。
- 非超预算分支（`:404-414`）未被改动，两段结构互为镜像，未引入分叉语义。
- 生产 `_renew` 委托 `HostRuntime.RenewRunGrantsAsync`（`HostRuntime.cs:1643-1684`）确实会返回 `StoppedTyped`（`RENEWAL_DISABLED` / `RENEWAL_NOT_AUTHORIZED` / `RENEWAL_NO_TARGETS`），即「超预算 + typed stop」是**真实可达**的生产路径，非纯理论：修复后这类轮次不再被降级为 `SkippedBudget` 并留下继续续期的假象。
- `StoppedRoundsExhausted` / `StoppedLivenessUnknown` / `StoppedNotTracked` 在 `TickAsync` 中于 renew 之前返回（`:295-338`），到达 POST-ROUND 守卫时只会来自自定义 renew 委托；它们与 typed/terminal 走同一 `!KeepsTracking` 分支，未单测但被同一分支覆盖。

## 4. AC 逐项判定

| AC | 判定 | 证据 |
|---|---|---|
| **AC1 停止优先序**：超预算 + Stop 返回原 kind/code；`Stops`+1、`BudgetSkips` 不因此 +1、`LastCode` 为 typed code | **MET** | 代码 `RunGrantRenewal.cs:387-390`；测试 `RunGrantRenewalTests.cs:279-306`（`Kind=StoppedTyped`、`Code=SOURCE_GRANT_DENIED`、`KeepsTracking=false`、`IsTracking=false`、`Stops=1`、`BudgetSkips=0`、`LastCode=SOURCE_GRANT_DENIED`）与本审查实跑（22/22、`RoundOverBudget` 4/4，EXIT 0）一致 |
| **AC2 成功轮计数**：超预算 + Renewed 仍 `Renewals`+1 且返回 `SkippedBudget` | **MET** | 代码 `:379-385`；既有测试 `:239-277` 断言 `Renewals=1`/`BudgetSkips=1`/`LastCode`，本审查实跑仍绿（未回归） |
| **AC3 内部预算 skip 保留自身 code** | **MET** | 代码 `:392-397`；测试 `:330-354`（`Code=RENEWAL_ROUND_CANCELLED`、`KeepsTracking=true`、`IsTracking=true`、`BudgetSkips=1`、`LastCode=RENEWAL_ROUND_CANCELLED`）。仅 `Code=null` 时默认值与常规路径不同（R-03，非本 AC 口径） |
| **AC4 判别测试**：≥3 用例 + 改坏时 ≥1 例 RED（实测） | **MET** | 新增 3 例（`:279-306` typed / `:308-328` terminal / `:330-354` 内部 skip；Renewed 路径由既有 `:239-277` 覆盖）。**本审查独立变异**：删 `:387-390` → 重建（EXIT 0）→ `--filter RoundOverBudget` **2 failed / 2 passed，EXIT 1**（typed@`:297`、terminal@`:324`，与入库日志逐字一致）→ 还原 → 22/22 EXIT 0 |
| **AC5 门禁** | **MET（附注）** | build 0/0（EXIT 0）；Host.Tests 全量 **305/0/72**（EXIT 0，与 `full-solution.log` 一致）；`check.ps1` 默认 + `-TaskPath` **PASS(3 warnings)/EXIT 0**；`verify_pins` **18/18 / EXIT 0**；EV 5 份 sha256 **5/5 一致**；实现 diff ⊆ `allowed_paths`、`out_of_scope` 空（EXIT 0）。附注：全量 .NET 由本审查部分复跑（见 §7 U-1）；head 另含生命周期文档（§1） |

## 5. Findings

| ID | 级别 | 文件:行 | 问题 | 依据 | 建议 |
|---|---|---|---|---|---|
| R-01 | **P3** | `doc/tasks/FEA-11-2C-RESIDUAL-1.md:68-72`；`verification/FEA-11-2C-RESIDUAL-1/README.md`；`.gitattributes` | EV 表 5 行的 `commit` 列均为 `-`，其中 **EV-2C-README 的 pin 只对"当前工作树字节"成立**：README 为 LF（`git ls-files --eol` → `i/lf w/lf attr/`，无 `eol` 规则），而 `.gitattributes` 无 `verification/FEA-11-2C-RESIDUAL-1/** text eol=lf`；`core.autocrlf=true` 下任何重新 checkout/全新 clone 都会把它写成 CRLF，pin 失配且因 `commit` 为空无法走 blob 回退 → 门禁在该场景会报 `Evidence SHA-256 不匹配` | 实测：`git checkout-index -f --prefix=<tmp>/` 模拟全新检出 → README `50f689eb37fb…` ≠ pin `349b524e…`；同一模拟下 4 份 log（`w/crlf`，本审查实跑也复现其 pin 值）`76a55c39…`/`899a31c6…`/`f22c768c…`/`b796cf66…` **逐字节命中**。`check.ps1:698-713` 的 blob 回退仅在 `commit` 非空时启用（`:700`），`:672` 把 `-` 归一为空。现状工作树 `check.ps1` PASS，故非阻塞。先例：`FEA-07-RESIDUAL-4` 的 README/DEFECTS 同为 `w/lf` + `commit=-`，属既有模式而非本卡新引入 | 二选一：①把 5 行 `commit` 填为 `a2c4c1d8c`（该提交确含这些文件，`git cat-file -e` 成立；LF 的 README 走 blob 回退即命中，CRLF 的 log 走工作树命中）；②给 `verification/FEA-11-2C-RESIDUAL-1/** text eol=lf` 并改为按 LF blob 重新钉 5 个哈希（注意会改变 4 份 log 的 pin 值）。两者都只需一次 docs/证据提交，不动实现 |
| R-02 | **P3** | `verification/FEA-11-2C-RESIDUAL-1/logs/{build,full-solution,mutation-red,renewal-tests-green}.log` | 4 份 CANONICAL 证据日志**无 shell/命令头、无时间戳、无 `EXIT=`**（实测 `EXIT` 标记计数 = 0/0/0/0），只有 `dotnet` 原始输出；E1/E2/E3/E4 的命令与退出码只能从卡/Handoff 散文反推，证据本身不自证 | 模板 §验证「证据纪律（2026-09-19，Q-009）」要求运行日志带 EXIT 与 shell/venv 头；上一 Task `FEA-07-RESIDUAL-4-r2.md` 的 P3-04 已对**同尺寸**的 `build.log`(26 行)/`full-solution.log`(265 行) 记过同一问题，本卡重复。影响有限：本审查独立复跑得到**完全相同**的数字（22/22、4/4、2 failed/2 passed、305/0/72、build 0/0），故结论真实，仅审计性不足 | 重生成时在文件头加 `# command: …`/`# shell: pwsh 7.x`/时间戳，尾部 `# EXIT=0`；`mutation-red.log` 请标注「预期 EXIT=1（RED 判别）」以免被误读为失败证据 |
| R-03 | **P3** | `apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs:392-397` vs `:409-414` | 同一 `SkippedBudget` outcome 的 `Code=null` 兜底值在两条路径不同：超预算路径用 `RENEWAL_ROUND_BUDGET_EXCEEDED`，常规路径用 `RENEWAL_ROUND_SKIPPED_BUDGET`。生产工厂 `RunGrantRenewalOutcome.BudgetSkip(code, …)`（`:58-60`）要求非空 code，故仅"直接构造 `new RunGrantRenewalOutcome(Kind: SkippedBudget)`"的自定义 renew 委托可触发；当前无测试覆盖 | 代码阅读 + `grep RENEWAL_ROUND_SKIPPED_BUDGET`（仅 `:412` 一处，无测试引用）。语义上也说得通（该轮确实超了预算），但同一逻辑结果因时序不同而换 code，运维检索会出现两个名字 | 统一为单一兜底常量（或都走 `RENEWAL_ROUND_BUDGET_EXCEEDED` / 都走 `RENEWAL_ROUND_SKIPPED_BUDGET`），并在注释说明取舍；如维持现状，建议加 1 条 `Code=null` 用例锁定行为 |
| R-04 | **P3** | `apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs:399-401` | 兜底 `return BudgetSkip(..., "RENEWAL_ROUND_BUDGET_EXCEEDED")` 在现 7 值枚举下**不可达**：`Renewed` 走 `:379`、`SkippedBudget` 走 `:392`，其余 5 个 Stop 类均 `!KeepsTracking` 走 `:387`，卡表「其它」行当前无实例 | 枚举 `:20-40` + `KeepsTracking` `:52` 穷举；编译器因属性是布尔表达式无法证明不可达，故不会告警 | 保留无害且与卡表一致，但建议改 `switch (outcome.Kind)` 表达式（编译期穷举、读者不会误以为还存在第三种"既续期又非 Renewed"状态），或加一行注释「unreachable today，为未来 kind 预留」。无需为它补测试 |

**无 P0 / P1 / P2。**

## 6. 门禁与复跑（本审查亲自执行，工作目录 `G:\CODEX\New Manga`，`main` @ `c30c1647e`）

| # | 检查 | 命令 / 方法 | 结果 | EXIT |
|---|---|---|---|---|
| 1 | 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Debug --nologo` | 已成功生成，**0 warning / 0 error**，6.23 s | **0** |
| 2 | 定向测试 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj --no-build --nologo --filter "FullyQualifiedName~RunGrantRenewalTests"` | **22 passed / 0 failed / 0 skipped**（236 ms） | **0** |
| 3 | 预算子集 | 同上 `--filter "FullyQualifiedName~RoundOverBudget"` | **4 passed / 0 failed**（含既有 Renewed 用例 + 3 新增） | **0** |
| 4 | Host.Tests 全量 | 同上，无 `--filter` | **305 passed / 0 failed / 72 skipped / 377**（10 s），与 `full-solution.log` 的 305/0/72 一致 | **0** |
| 5 | **变异判别（本审查独立重做）** | ① 删除 `RunGrantRenewal.cs:387-390`（`!KeepsTracking → Stop`）→ ② `dotnet build ...NewManga.Host.Tests.csproj -c Debug --nologo`（0/0，EXIT 0）→ ③ `--filter "FullyQualifiedName~RoundOverBudget"` → ④ `git show a2c4c1d8c:<path>` 覆盖还原 → ⑤ 重建 + 复跑 | ③ **2 failed / 2 passed，EXIT 1**：`Renewal_RoundOverBudget_KeepsTheTypedStopInsteadOfRewritingIt`（`Expected: StoppedTyped / Actual: SkippedBudget`，`:297`）与 `…KeepsATerminalStopInsteadOfRewritingIt`（`:324`）——与入库 `mutation-red.log` **用例、断言、行号、计数逐条一致**；⑤ 还原后 **22/22，EXIT 0**，工作树 sha256 `6DADCBCD09402058…` = `git show a2c4c1d8c:path` 字节 = README 记录值 | ③ **1**；①③⑤其余 **0** |
| 6 | 治理（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**：12 个非终态 Task、STATUS 2915B/29L 80%、PLAN 6722B/63L 80% | **0** |
| 7 | 治理（`-TaskPath`） | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-2C-RESIDUAL-1.md` | **PASS (3 warnings)**，同上 | **0** |
| 8 | 契约 pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，C01b…FEA01 全 OK | **0** |
| 9 | EV 5 个 sha256 | `Get-FileHash -Algorithm SHA256` 逐份比对卡 `:68-72` | **5/5 一致**：README `349b524e…`、mutation-red `f22c768c…`、green `b796cf66…`、full-solution `899a31c6…`、build `76a55c39…` | **0** |
| 10 | 实现 diff 范围 | `git diff --name-only ac64cb134..a2c4c1d8c` | 8 文件全部落在 `allowed_paths` 内（源码/测试/卡/5 份证据） | **0** |
| 11 | `out_of_scope` 探针 | 见 §1 命令 | **空 diff** | **0** |
| 12 | 工作树 | `git status --short --untracked-files=all`（审查开始 / 结束） | 开始**干净**；结束仅本报告为新增未跟踪文件 | **0** |
| 13 | EV 可复现性模拟 | `git checkout-index -f --prefix=<tmp>/ -- <5 份 EV>` | 4 份 log **命中 pin**；README **`50f689eb…` ≠ pin**（见 R-01） | **0** |
| 14 | 全量计数自洽 | 解析 `full-solution.log` 8 个 `总计` 行 | passed 21+72+253+117+31+305+167+836 = **1802**；failed **2**；skipped 72+24+11 = **107**；`App.Tests 836/2/11/849`；与卡/Handoff 一致 | **0** |
| 15 | 既有失败归属 | `full-solution.log` 的 `[FAIL]` 提取 | 2 例 = `V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues`、`FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit`，与 `verification/FEA-07-RESIDUAL-4/DEFECTS.md:20-23` 登记的既有失败**同名同因**；App.Tests 计数 836/2/11 与上一 Task 交付完全一致（本卡零 App diff）→ **不新增失败** | **0** |

**#5 注释（还原手法，供后续审查复用）**：本仓库 `core.autocrlf=true` 且 `.gitattributes` 未对 `apps/**/*.cs` 定规则，因此 `git checkout -- <path>` 会把该文件重写成 **CRLF**（实测 sha256 变为 `161C2157…`，与卡/README 声称的 `6DADCBCD…` 不同）。本审查改用 `git show a2c4c1d8c:<path>` 覆盖还原，得到与 blob 完全一致的 LF 字节（`6DADCBCD…`），再 `git update-index`/`git add` 刷新 stat 缓存，`git status` 恢复干净、`git diff --cached` 为空。该细节同时是 R-01 的同一根因。

## 7. 剩余风险

- **超预算 + Stop 时的预算越界信号不再被计入/告警**：旧路径会给 `BudgetSkips++` 并 `warn "round skipped code=RENEWAL_ROUND_BUDGET_EXCEEDED"`；新路径只留 `warn "stopped code=<typed>"`。按 AC1 这是**刻意**取舍（stop 更可操作），且 stop 后循环即终止、不再续期，故不构成 300 s TTL 风险；仅意味着「这轮超了 50 s 预算」不再单独可观测。若希望保留，可在 `Stop()` 前补一条计数/日志（不在本卡范围）。
- **`KeepsTracking` 作为否定条件**：`:387` 用 `!outcome.KeepsTracking` 而非显式 Stop 类集合。现枚举下等价；若未来新增"既不续期也不属 Stop"的 kind，会被当作 Stop 处理（fail-closed，可接受）；若新增"续期但非 Renewed/SkippedBudget"的 kind，则落到 R-04 的通用 skip。改为 switch 表达式可把这条演化规则显式化。
- **证据 pin 的 EOL 敏感性（R-01）**：只要有人 `git checkout -- verification/FEA-11-2C-RESIDUAL-1/README.md` 或多机 clone，`349b524e…` 就不再匹配工作树字节，`check.ps1` 会在无 `commit` 回退的情况下报错。属证据卫生风险，不是实现风险。
- **`FEA-11-RUN-GRANT-2C-r1.md` 的 R2C-02（P2）仍在**：`RoundBudget` 仍是 `_renew` 返回后的**事后**判定，单轮最多可先跑 8×30 s on-demand 扫描再被判超预算（本卡未触及，卡面亦排除）。本卡只修「停止优先序」，不改变该最坏时延。
- **`Reviewer` 字段**：卡 `:10` 仍为「待指派（必须独立上下文）」，本报告可作为 DSH 登记的输入，但卡内字段与 `reviewer`/`reviewer_kind` 的正式回填由 DSH 在处置时完成。

## 8. 未验证项（NOT_RUN / UNKNOWN）

| ID | 项 | 状态 | 原因 / 替代 |
|---|---|---|---|
| U-1 | 全量 `NewManga.sln`（8 项目、1802/2/107）由本审查重跑 | **NOT_RUN** | `App.Tests` 单项目约 5 m 35 s，超出本轮预算；已改为：Host.Tests **全量**复跑（305/0/72，与日志一致）+ 解析 `full-solution.log` 逐项计数自洽（1802/2/107）+ 2 例失败与既有 DEFECTS 同名同因 + App.Tests 计数与上一 Task 交付逐字相同（836/2/11/849，且本卡 App diff 为零） |
| U-2 | base 侧 `Host.Tests` 302/0/72 的实跑对账 | **UNKNOWN** | 需 checkout/stash base（只读约束禁止）；以算术 305−3=302 与 `full-solution.log` 的 Host.Tests 明细替代印证 |
| U-3 | 真实 Core/IPC/端到端续期 | **NOT_RUN** | 卡面声明本卡只需确定性单测（`TimeProvider`/`renew`/`liveness` 三 seam 注入），未要求真实 IPC；实现路径已由 `HostWiring_*` 三例覆盖生产入口 |
| U-4 | pytest / Python 侧 | **NOT_RUN** | 本卡零 Python diff |
| U-5 | 变异实验的**第二种**破坏方式（例如把 Stop 分支改成 `return NotTracked()` 或只改计数） | **NOT_RUN** | 任务书只要求删除 `if (!outcome.KeepsTracking)` 这一种；已实测 2 例 RED，判别力成立 |
| U-6 | 真实 `%APPDATA%` 写入 delta | **NOT_RUN（N/A）** | 本卡不触碰 App 数据路径；审查只在仓库内构建/测试，未写用户目录 |
| U-7 | `R2C-02` 最坏单轮时延（8×30 s）实测 | **NOT_RUN** | 属来源 Review 的 P2 残余，本卡 `out_of_scope`；未做时延测量 |

## 9. 结论

- 实现与卡 §修复口径**一致**（四行分流逐条对应），AC1–AC5 **全部 MET**；`Renewed` 路径语义保持不变，既有预算用例未回归；`out_of_scope` 与预算常量零改动；无 P0/P1/P2。
- 判别力由本审查**独立变异复现**（2 RED，EXIT 1）并**还原后复绿**（22/22，EXIT 0），入库 `mutation-red.log` 与实测逐条一致。
- 门禁：build 0/0（EXIT 0）、Host.Tests 305/0/72（EXIT 0）、`check.ps1` 两口径 PASS（EXIT 0）、pins 18/18（EXIT 0）、EV 5/5 哈希一致、工作树干净。
- 4 项 **P3** 均为证据卫生/代码一致性：建议关账前顺手处置 **R-01**（填 `commit` 列或加 `eol=lf` 规则）与 **R-02**（日志补命令头/EXIT），二者都只需证据侧一次提交，**不需要改实现 head**；R-03/R-04 可延后或与下次触碰该文件时一并处理。
- **verdict：`approved`**，本报告仅对 `reviewed_head: c30c1647e` 有效；若 DSH 采纳 R-01/R-02 产生新的文档/证据 head，只需对 EV 行与日志字节做增量复核，代码面无需重审。
