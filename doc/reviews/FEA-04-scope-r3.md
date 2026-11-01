---
review_id: FEA-04-scope-r3
task: FEA-04
kind: scope-review
base_commit: 55543c10d
reviewed_head: 7a9135260
review_round: 3
reviewer: fea04-scope-reviewer
reviewer_source: DSH fresh 独立上下文派发（Team Lead=lead；同一独立席位续审，未参与 FEA-04 起草/实现/返修）
review_appointment: doc/tasks/FEA-04.md（frontmatter `review_appointment`，:21）
date: 2026-11-02
timezone: Asia/Shanghai
conclusion: changes_requested
counts: { P0: 0, P1: 1, P2: 10, total: 11 }
r2_disposition: { closed: 11, partial: 3, open: 1 }
scope: 仅范围冻结复核（不构成实现验收）
---

# FEA-04 范围冻结复核 r3（v3）

**结论：`changes_requested`（P0 = 0、P1 = 1、P2 = 10）**

**r2 的 3 个 P1 全部真实闭环**：R2-01（AC2 命令已换成可执行的 sln 形式）、R2-02（Q-20 五谓词 + `PreflightBlocker` 形状冻结，五个 Code 全部落到实测存在的状态位）、R2-03（写域已收窄）。r2 的 12 项 P2 中 **8 项 closed、3 项 partial、1 项 open**。**无新增 P0**。

唯一 P1 是**授权记录缺失**（非范围设计问题）：v3 新引入的 **Q-20** 被卡内当作"DSH 裁决/冻结依据"，但 `GOAL-PROGRESS-2026-11-02.md` 的 Q 表**没有 Q-20 行**（止于 Q-18，Q-19 并入 Q-15 行），全 `doc/**` grep `Q-20` 仅命中 FEA-04.md 自身 5 处自述；且卡 `:7` 的 `approval: dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q19` 未覆盖 Q-20。**一行补记 + 改 approval 字符串即可闭环，无需再改任何规则或写域。**

## 审查基线

| 项 | 值 | 证据 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | — |
| **HEAD** | **`7a91352609d3336c9256fd77e572c0786107d950`**（`docs(fea-04): 范围冻结 v3 …`） | `git rev-parse HEAD`；`git cat-file -t 7a9135260` → `commit`（可解析，上一轮笔误已更正） |
| 工作区 | clean（审查前后 porcelain 均空） | `git status --porcelain` |
| v3 提交内容 | 5 文件：`FEA-04.md` +98/−52、`FEA-04-scope-r2.md`（179 行，r2 报告入库）、STATUS、PLAN、GOAL-PROGRESS | `git show --stat HEAD` |
| 治理检查器 | **PASS**（2 警告：11 个非终态 Task；STATUS 3187 bytes/38 lines＝预算 80%） | `check.ps1` |
| 冻结 pin | **PASS 15/15** | `verify_pins.ps1` |

**未执行**：`dotnet build`/`dotnet test`/`pytest`/真机运行；任何被审文件写入；任何 commit/push。`check.ps1`/`verify_pins.ps1` 为只读运行。本报告所有行号基于 `7a9135260` 实测。

---

## 1. r2 findings 逐项 disposition（15/15）

| r2 编号 | r2 级别 | 处置 | 证据（v3） |
|---|---|---|---|
| **R2-01** AC2 命令不可执行（实测 MSB1003） | P1 | **closed** | `:58`/`:86` 改为 `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`。可行性实测：sln 存在；`tests/NewManga.runsettings` 存在且为合法 `RunSettings`（`MaxCpuCount=1`，`:2-13`）；`--settings` 为 `dotnet test` 合法开关；`--no-build` 需前置 build（见 R3-06） |
| **R2-02** AC5「有损」谓词 / blocker 形状未定义 | P1 | **closed** | Q-20 落 R-STATE-2 `:63` + AC5 `:89`：`PreflightBlocker(Code, Source, Detail)`，五 Code 全部映射到实测存在的状态位（`PENDING_REGION_TYPE`←`StudioInspectorViewModel.cs:195`；`PENDING_CONFIRMATION`←`StudioPageViewModel.cs:257` + `Shell/V2/ConfirmRequest.cs`；`UNFLUSHED_RUN_KEY`←`StudioBatchViewModel.cs:329`；`UNMAPPED_READER_ANCHOR`←`ReaderOverlayViewModel.cs:48-57`；`UNMAPPED_SHELL_STATE`←`ShellState.cs:119-139` + ThemeStudio editor draft）→ 可机械判定，AC5 要求五个 blocker 各有用例 ✓ |
| **R2-03** `tests/**` 写域过宽 | P1 | **closed** | `:34-35` 收窄为 `tests/NewManga.App.Tests/**` + `tests/NewManga.ApplicationCore.Tests/**`；其余测试工程不再有写权（AC2 仍全 sln 只读运行，二者不冲突 ✓） |
| **R2-04** AC6 `ReferenceEquals(host, host)` 同义反复 | P2 | **closed** | `:90` 改为 `ReferenceEquals(hostBefore, hostAfter)` + 计数不增 ✓ |
| **R2-05** Q-16 口径绝对化 + 虚构类型名 | P2 | **closed** | `:48`（S4 经既有 `IHostController` 读接口 + 不新增命令）、`:62`、`:76`（`DraftBuffer`+`DraftId`）、`:78`（`IntentCoordinator.ExecuteAsync(intentKey)` + 既有 `IDEMPOTENCY_KEY_REUSED`）、`:79`（既有只读投影）、`:81`（S6 preflight 只读）——全部改指实有成员 ✓。残留：`:62` 的摘要把 S2/S6 也归入 ApplicationCore → R3-03 |
| **R2-06** 禁止范围误标 FEA-05 / S6 未限只读 | P2 | **closed（措辞可再收）** | S6 已加 `preflight 只读`（`:81`、`:106`）；FEA-05 表述仍为"FEA-05 起的 UI 功能"（`:106`），但 S6→Appearance 越界口子已被"仅 preflight 只读"堵住，实质风险已消 |
| **R2-07** FEA-02-BRIDGE 依赖边无书面处置 | P2 | **partial（并引入事实错误）** | `:46` 已加书面处置，但内容与方案不符 → R3-02 |
| **R2-08** §15.3 引用行号偏一行 | P2 | **closed** | `:45` 改为 `§15.3 :880-887` ✓（与表体实测一致） |
| **R2-09** AC3 静态检查无口径 / AC1 缺机械点 | P2 | **partial** | AC3 口径已补（R-STATE-3 `:64`「新增私有缓存/registry 字段须在 Handoff 说明且不得作为读取权威」+ AC3 `:87`）✓；AC1 仍缺「公开成员变更 = 0」Handoff 必填行 → R3-08 |
| **R2-10** AC8 硬编码 r2 / review_appointment 陈旧 | P2 | **closed** | AC8 `:92` → 「范围复核 r3 approved」；`review_appointment` `:21` 已更新（含 r1、r2 与"Review 由该席位写，不在本卡 allowed_paths"）。硬编码轮次的模式性风险见 R3-10 |
| **R2-11** route adapter 无承载 | P2 | **partial** | `:50` 已定落点 `Views/V2/Route/`（在 `:31` 写域内，目录当前不存在＝纯新增 ✓）；但职责边界与 `Shell/V2/ShellDeepLink` 的分工、以及与 R-SWITCH-3「不改运行期路由」的界线未写 → R3-05 |
| **R2-12** AC4 缺未迁出登记 | P2 | **closed** | `:88` 恢复「**未迁出项必须在 Handoff 明确登记**（不得静默省略）」✓ |
| **R2-13** `doc/reviews/**` 写权主体未区分 | P2 | **closed** | `:105`「`doc/reviews/**` 由 Review 席位写（不在本卡写域）」；`:21` 亦写明 ✓ |
| **R2-14** GOAL-PROGRESS 指针 stale | P2 | **closed** | `GOAL-PROGRESS:3-4` 已更新为 v3/r3；`:30` 下一动作改为 r3 → ready ✓（"当前 HEAD" 落后一轮的问题并入 R3-10） |
| **R2-15** S5 legacy `RunStatusMonitor` 去留未写 | P2 | **open** | `:80` 仍只写"单例 `RunMonitor` + 会话筛选"，未处置 legacy `Shell/V2/RunStatusMonitor`（`ConsoleViewModel.cs:21/103/113` 仍在用）→ R3-09 |

**汇总：closed 11 / partial 3 / open 1（合计 15）。**

---

## 2. 逐项核查（按派发核查点 1–5）

### 核查-1（R2-01 / AC2 命令）——**闭环，命令可执行**

| 组成 | 实测 |
|---|---|
| `apps/desktop-avalonia/NewManga.sln` | 存在（16 个工程，含 `ApplicationCore` 与 6 个测试工程） |
| `--settings apps/desktop-avalonia/tests/NewManga.runsettings` | 文件存在，合法 `<RunSettings>`，`<MaxCpuCount>1</MaxCpuCount>`（注释说明并行 SQLite 竞争，`:4-11`） |
| `--no-build` | 需要**先** build；卡内未写前置 build 命令 → R3-06 |
| 逐工程计数 | `dotnet test <sln>` 会按测试工程各出一份摘要 → "逐工程通过计数"取自原始输出，可满足 ✓ |

上一轮的 `MSB1003` 是**目录**路径导致的工程解析失败；v3 用的是 sln 文件，不再触发。判定：**可执行**。

### 核查-2（R2-02 / Q-20 blocker）——**可机械验证**

五个 Code 与状态位的映射（全部本席位实测存在）：

| Code | 状态位 | 证据 |
|---|---|---|
| `PENDING_REGION_TYPE` | `_pendingRegionType` | `ViewModels/V2/Studio/StudioInspectorViewModel.cs:195`（暴露 `:282`） |
| `PENDING_CONFIRMATION` | `_pendingNavigation` + 确认模态 | `StudioPageViewModel.cs:257`；`Shell/V2/ConfirmRequest.cs` |
| `UNFLUSHED_RUN_KEY` | `_intentIdempotencyKey` | `StudioBatchViewModel.cs:329`（赋值 `:1079`、清空 `:1139`） |
| `UNMAPPED_READER_ANCHOR` | reader 的 book/index/mode/direction/scroll | `ReaderOverlayViewModel.cs:48-57` |
| `UNMAPPED_SHELL_STATE` | `ShellState` + `SpaceViewState` + ThemeStudio editor draft | `Shell/V2/ShellState.cs:119-139`、`ViewModels/V2/ThemeStudio/ThemeStudioEditorViewModel.cs` |

「任一存在即 `allowed=false`」+「五个各有用例」（`:89`）→ 可机械判定 ✓。`PreflightBlocker`/五 Code 在代码中**不存在**（grep 0 命中）＝本卡新增，符合"适配层增量"与写域（`Shell/V2/**`/`Views/V2/Route/**`）。残留：落点未指定 + `Source` 取值域未定义 + S5 无 blocker 未说明 → R3-04；"零副作用"断言机制未给 → R3-07。

### 核查-3（R2-03 / 写域）——**闭环**

`tests/NewManga.App.Tests/**` + `tests/NewManga.ApplicationCore.Tests/**`（`:34-35`）。AC3 的边界测试可落 App.Tests（在域内）；AC2 的 sln 全量运行只需**读/运行**，不需要写其它测试工程 → 自洽 ✓。残留：ApplicationCore.Tests 的写权理由未写（该目录是 FEA-02-CORE 的冻结测试面）→ R3-11。

### 核查-4（P2 批修）——**8/12 到位，3 项 partial、1 项 open**

已核实到位：AC6 `hostBefore/hostAfter`（`:90`）、R-STATE-1/S4 经既有 `IHostController`（`:48`/`:62`/`:79`，接口成员 `Services/IHostController.cs:161` `LoadReaderBookAsync`、`:106` `SaveReadingProgressAsync`）、S1/S3 类型更正（`:76`/`:78`）、S6 preflight 只读（`:81`/`:106`）、§15.3 `:880-887`（`:45`）、AC4 未迁出登记（`:88`）、AC8→r3（`:92`）、route 落点（`:50`）、`doc/reviews` 写权（`:105`）、GOAL-PROGRESS 指针（`:3-4`/`:30`）。
未到位/新问题：R3-02（BRIDGE 陈述错误）、R3-03（R-STATE-1 摘要自相冲突）、R3-05（route 职责边界）、R3-08（AC1 机械点）、R3-09（legacy monitor）、R3-10（指针记账）、R3-11（写域理由）。

### 核查-5（是否仍有 open 的 P1/P2；是否引入新问题）——**有 1 项新 P1、10 项 P2**

**新 P1（R3-01）＝Q-20 无书面裁决记录（授权追溯缺口）**。这一项是 v3 新引入的：卡 `:47` 以 `[GOAL-PROGRESS](…/GOAL-PROGRESS-2026-11-02.md)` 为引用，写「Q-12/Q-16…Q-20」；`:52` 称「**Q-20**：…冻结」；`:63`「**R-STATE-2（Q-20，冻结）**」；`:137` Closeout 亦以 Q-20 记账。但：
- `GOAL-PROGRESS-2026-11-02.md` 的 Q 表实测止于 **Q-18**（`:20-26`；Q-19 并入 `:23` 的 Q-15/Q-19 行），**无 Q-20 行**；
- 全 `doc/**/*.md` grep `Q-20` → **仅命中 `doc/tasks/FEA-04.md` 的 5 处自述**，无任何外部裁决记录；
- 卡 `:7` `approval: dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q19` **未覆盖 Q-20**。

对照：r2 时本席位对 Q-16/Q-17/Q-18 的正面核查依据正是"`GOAL-PROGRESS` 有对应行 + `approval` 字段同步"（v2 已满足）。v3 的 Q-20 不满足同一标准，而它恰是 R-STATE-2 与 AC5 两个核心新增交付的冻结依据 → 按同一口径必须记为 P1（**行政补记即可，不涉及范围设计**）。

其他新问题：R3-02（`:46` 对 FEA-02-BRIDGE 的陈述与方案 `:922`/§15.5 `:910` 不符，属 v3 新引入）、R3-03（`:62` 摘要把 S2/S6 归入 ApplicationCore，与 `:81` 及 R-STATE-3 冲突）。其余为 r2 残留。

---

## 3. 放行条件

**一处补记即可 approved**（不涉及范围、写域或规则的任何改动）：

1. **R3-01（P1）**：在 `GOAL-PROGRESS-2026-11-02.md` 的 Q 表增一行 Q-20（内容照卡 `:52`/`:63` 原文：`PreflightBlocker(Code,Source,Detail)` 五 Code、任一存在即 fail-closed）；并把卡 `:7` `approval` 改为 `dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q20`。

若 DSH 认为该项属"实现前补齐的行政记录"、希望不再开 r4：可在同一提交补记后由 DSH 判定该 P1 已闭合并直接置 `ready`（此时请把"Q-20 已登记 + approval 已更新"写入 Closeout Record，便于实现复核席位核验）。**本席位不预批**：在补记落地前，结论维持 `changes_requested`。

10 项 P2 建议同批修（均为单句/单词级），但不阻塞 `ready`。

---

## 4. Findings

| 编号 | 级别 | 位置（v3 = `7a9135260`） | 问题 | 最小修法 |
|---|---|---|---|---|
| **R3-01** | **P1** | 卡 `:47`、`:52`、`:63`、`:89`、`:137`；`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:20-26`；卡 `:7` | **Q-20 无书面裁决记录，approval 未覆盖。** 卡以 `GOAL-PROGRESS` 为引用称 Q-20 为 DSH 冻结裁决，但该文件 Q 表无 Q-20 行（止于 Q-18；Q-19 并入 Q-15 行），全 `doc/**` 仅 FEA-04.md 自述；`approval` 字符串仍为 `…_Q16_Q19`。R-STATE-2/AC5 两个核心新增交付的冻结依据因此不可追溯 | GOAL-PROGRESS Q 表增 Q-20 行（照卡 `:52`/`:63` 原文）；卡 `:7` → `dsh_ruling_2026-11-02_GOAL_FEA04_Q16_Q20`；Closeout 记"Q-20 已登记" |
| **R3-02** | P2 | 卡 `:46` | **FEA-02-BRIDGE 的陈述与方案不符（v3 新引入）。** 卡写「FEA-02-BRIDGE 为 FEA-02 内子切片（ApplicationCore draft buffer，FEA-03 已交付 `DraftBuffer.cs`）」；方案 `:922` 定义的 FEA-02-BRIDGE 写域是 `NewManga.App/Services/` + 批准的 CoreClient 子文件，出口是 **Host 生命周期/退出断言**（§15.5 `:910` 的 `ExitCoordinator`）。"ApplicationCore 本地缓冲"是 **FEA-03 自己的 BRIDGE 收窄切片**（`doc/tasks/FEA-03.md:65` Q-8、`:109`、`:141`）。实测 `ExitCoordinator` 全库仍 **0 命中**，legacy 关闭仍 Dispose Host（`Views/MainWindow.axaml.cs:852`）→ 该句会把未交付的 BRIDGE 记为已交付 | 改为：「FEA-02-BRIDGE 的**收窄切片**（ApplicationCore 本地草稿缓冲）由 FEA-03 交付，本卡只消费 `DraftBuffer`；其 Host 生命周期/`ExitCoordinator` 部分未实施，本卡**不依赖**，按 R-STATE-4 维持既有装配」 |
| **R3-03** | P2 | 卡 `:62`（R-STATE-1 摘要） | 摘要写「S1–S3/S6 为 ApplicationCore 本地对象」，但 S2/S6 的目标列是**会话 UI memento**（`:77`/`:81`），R-STATE-3 `:64` 也把 memento 归为"允许的 UI 私有状态"。同一卡内三种口径 | 改为「S1/S3/S5 为 ApplicationCore 本地对象（`DraftBuffer`/`IntentCoordinator`/`RunMonitor`）；S2/S6 为 UI memento（**不是**业务权威）；S4 为既有 `IHostController` 只读投影」 |
| **R3-04** | P2 | 卡 `:52`、`:63`、`:89` | `PreflightBlocker` 的**落点**与 `Source` 取值域未定义；且 Q-20 只给 S1/S2/S3/S4/S6 五个 Code，**S5 无对应 blocker** 未作说明（读者会问"为什么五项而不是六项"） | 补：类型落 `Shell/V2/Frontends/PreflightBlocker.cs`（写域内）；`Source ∈ {S1,S2,S3,S4,S6}`；一句「S5 的 monitor/筛选属可重建的 UI 态，不构成有损编辑态 → 无 blocker」 |
| **R3-05** | P2 | 卡 `:50`（route 落 `Views/V2/Route/`）、`:70`（R-SWITCH-3） | route adapter 的**职责边界**未写：与 `Shell/V2/ShellDeepLink`（`:28 TryParse`/`:122 ToQuery`）的分工、与 R-SWITCH-3「不改运行期路由」的界线都不清楚；且该适配器落在 Views 层而非 Shell 层，需说明理由 | 补一句职责定义：「`Views/V2/Route/` 只做**既有深链/页面标识的只读映射**（与 `ShellDeepLink` 同语义），不实现路由切换、不改路由格式（R-SWITCH-3）」；或改落 `Shell/V2/` 与 `ShellDeepLink` 同层 |
| **R3-06** | P2 | 卡 `:58`、`:86`（AC2） | 证据粒度与测量程序不完整：`--no-build` 缺前置 build；"逐工程计数"未区分 `passed/failed/skipped`，**skip 漂移可掩盖断言弱化**（R-CURRENT-2 已禁弱化，但无量化口径）；基线在 `91be6c134` 测量需隔离检出，未写机制 | 补：①先 `dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror`；②基线在 `G:\CODEX\New Manga.workspace\` 的隔离 worktree 检出 `91be6c134` 测量（不在主工作树 checkout）；③每工程记 `passed/failed/skipped/total`，判据 `failed=0`、`passed ≥ 基线`、`skipped ≤ 基线` |
| **R3-07** | P2 | 卡 `:68`（R-SWITCH-1）、`:89`（AC5） | AC5 要求「零 Host/Core 副作用」但未给**断言机制**（AC6 已给计数机制，AC5 未引用） | 补：断言 preflight 前后 `FakeHostController.StartCalls`（`tests/NewManga.App.Tests/FakeHostController.cs:17`）、`LifecycleLog`（`:19`/`:49`）、请求计数与 `HostController.StartRequests`（`Services/HostController.cs:67`）均不变 |
| **R3-08** | P2 | 卡 `:85`（AC1） | AC1 仍缺 r2 建议的机械检查点：Handoff 必填行「公开成员变更 = 0」（AC3 的静态检查口径已由 `:64` 补 ✓，仅 AC1 缺） | AC1 补：「Handoff 必列公开成员变更清单，应为 0；非 0 需逐项说明并说明为何不属于 R-CURRENT-1 违约」 |
| **R3-09** | P2 | 卡 `:80`（S5 目标列）、`:62` | legacy `Shell/V2/RunStatusMonitor` 的去留仍未写（`ConsoleViewModel.cs:21/103/113` 在用；该文件 `:7-8` 自述"ONE shared Run-status source"），与 S5 目标"单例 `RunMonitor`"并存即成过渡期双实现（r2 R2-15 未闭环） | S5 补：「Console 的 Run 投影切到 `RunMonitor<T>`；legacy `RunStatusMonitor` 降为 dispatcher 薄适配（或保留并登记为未迁出项 + 原因 + 后续 Task）」+ 单轮每 Run ≤1 次 snapshot/projection 查询的调用计数断言 |
| **R3-10** | P2 | 卡 `:14`（`base_commit: 55543c10d`）、`:92`（AC8）；`GOAL-PROGRESS:3` | 指针记账差一轮：`base_commit` 指向 v2 提交（当前冻结为 v3 `7a9135260`）；`GOAL-PROGRESS:3` 在 v3 提交内写"当前 HEAD `55543c10d`"（实际 HEAD 已是 `7a9135260`）；AC8 硬编码「r3」（若本轮未 approved，r4 时再次不可满足——该模式已连续三轮出现） | `ready` 时把 `base_commit` 重钉为最终冻结/`ready` 提交；GOAL-PROGRESS 的 HEAD 行改为"本卡 v3 提交 `7a9135260`"或去掉该行；AC8 改「最后一次范围复核 approved（P0/P1=0），报告路径记入 `review_appointment`」 |
| **R3-11** | P2 | 卡 `:35`（`tests/NewManga.ApplicationCore.Tests/**`） | 该目录是 FEA-02-CORE 的冻结测试面（`NewManga.ApplicationCore/README.md` 表明其测试为纯 .NET 无 Avalonia）；本卡写权扩展到此处，理由未写，且与 AC3 的边界测试需求（可只落 App.Tests）不必然相关 | 补一句用途（如"仅新增消费侧 seam/适配计数用例，不改既有 ApplicationCore 用例"），否则收窄回仅 `tests/NewManga.App.Tests/**` |

---

## 5. 边界声明

本报告**只审范围冻结**（Task 卡 v3 + 其引用的方案/授权/前置/代码事实），**不构成实现验收**，不构成设计或契约批准。`approved`/`changes_requested` 仅针对"范围文本是否可执行、可机械验证、与方案和治理指针一致"。

本席位**未参与** FEA-04 的起草、实现或返修；**未修改**任何被审文件、卡、STATUS、PLAN、LEDGER、checkpoint 或源码；**未** commit/push；**未执行**构建/测试/真机运行（仅 `check.ps1`、`verify_pins.ps1` 只读运行与若干只读 grep/文件读取）。所有行号基于 `7a9135260` 实测；行号存在性不证明调用链完整。
