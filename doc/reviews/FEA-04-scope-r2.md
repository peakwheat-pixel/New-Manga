---
review_id: FEA-04-scope-r2
task: FEA-04
kind: scope-review
base_commit: e34796862
reviewed_head: 55543c10d
requested_head: d8d1d3b6a
requested_head_resolution: UNRESOLVABLE（`git cat-file -t d8d1d3b6a` → fatal: Not a valid object name）
review_round: 2
reviewer: fea04-scope-reviewer
reviewer_source: DSH fresh 独立上下文派发（Team Lead=lead；同一独立席位续审，未参与 FEA-04 起草/实现/返修）
review_appointment: doc/tasks/FEA-04.md（frontmatter `review_appointment`，:21）
date: 2026-11-02
timezone: Asia/Shanghai
conclusion: changes_requested
counts: { P0: 0, P1: 3, P2: 12, total: 15 }
r1_disposition: { closed: 7, partial: 5, open: 8 }
scope: 仅范围冻结复核（不构成实现验收）
---

# FEA-04 范围冻结复核 r2（v2）

**结论：`changes_requested`（P0 = 0、P1 = 3、P2 = 12）**

r1 的 **3 个 P0 全部真实闭环**（F-01/F-02/F-03 → Q-16/Q-17/Q-18，裁决有书面记录且已落卡）；r1 的 9 个 P1 中 **2 个 closed**（F-04 switch 收窄、F-07 AC1 改写）、**4 个 partial**、**3 个 open**；**无新增 P0**。剩余 3 项 P1 均为「单行文本即可闭环、不涉及裁决」的类型：①AC2/R-CURRENT-2 的测试命令**实测不可执行**（`MSB1003`，见 §核查-6）；②AC5/R-STATE-2 的「有损编辑态」仍无判定谓词；③`tests/**` 写域仍宽于方案 `:924`「对应 tests」。三项齐修即可进入 `ready`，无需再裁决、无需扩写域。

## 审查基线

| 项 | 值 | 证据 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | — |
| **实际 HEAD** | **`55543c10d3104903550071d5604c2b54614b72dd`**（`docs(fea-04): 范围冻结 v2 …`） | `git rev-parse HEAD`、`git log --oneline -3` |
| 请求 HEAD | `d8d1d3b6a` → **不可解析** | `git cat-file -t d8d1d3b6a`：`fatal: Not a valid object name`；`git rev-parse --disambiguate=d8d1` 空 |
| 工作区 | clean（审查前后均为空 porcelain） | `git status --porcelain` |
| v2 提交内容 | 6 文件：`FEA-04.md`+90/−43、`doc/reviews/FEA-04-scope-r1.md`（230 行，r1 报告已入库）、STATUS/PLAN/LEDGER/GOAL-PROGRESS 指针 | `git show --stat HEAD` |
| 治理检查器 | **PASS**（2 警告：11 个非终态 Task；STATUS 3182 bytes/37 lines＝预算 80%） | `check.ps1` |
| 冻结 pin | **PASS 15/15** | `verify_pins.ps1` |

### 请求指针异常（不计入卡内 findings，须处置）

派发消息中的新 HEAD `d8d1d3b6a` **在本仓库不存在**；实际 v2 提交为 `55543c10d`（其内容与派发描述"范围冻结 v2 + r1 报告入库"完全吻合，应为同一提交的旧哈希/笔误）。本报告以 **`55543c10d`** 为 `reviewed_head` 审查。**影响**：卡 `review_appointment`、Closeout Record 与 evidence pin 若引用 `d8d1d3b6a`，将无法通过 pin 校验 → 请 DSH 在收口时统一钉 `55543c10d`（并在 GOAL-PROGRESS 记录该笔误，避免后续 Task 复用错误哈希）。

**未执行**：`dotnet build`/`dotnet test`/`pytest`/真机运行；任何被审文件写入；任何 commit/push。唯一执行的命令行探测为 **只读 MSBuild 求值**（`dotnet msbuild 'apps/desktop-avalonia/tests' -getProperty:…`，无文件写入，见 §核查-6），以及 `check.ps1`/`verify_pins.ps1` 只读运行。

---

## 1. r1 findings 逐项 disposition（20/20）

| r1 编号 | r1 级别 | 处置 | 证据（v2） |
|---|---|---|---|
| **F-01** wire 归属矛盾（Host/CoreClient 不可写 vs FEA-03 defer wire） | P0 | **closed** | Q-16 书面裁决：[GOAL-PROGRESS:24](../../doc/checkpoints/GOAL-PROGRESS-2026-11-02.md)「否；S1–S3 权威收窄为 ApplicationCore 本地」；卡 `:47`、R-STATE-1 `:60`、AC4 `:86`、L-2 `:97`（含 `blocked` 再触发）、禁止范围 `:102`、新增「契约 deferral 登记」`:108-113` |
| **F-02** App 缺 `ApplicationCore` 引用（DSH 单点、写域外） | P0 | **closed** | `NewManga.App.csproj` 入 allowed_paths `:30`；Q-17 `:48`「唯一单点例外」；禁止范围 `:105`；Handoff 记录要求 `:48`/`:105`。补充核查：`NewManga.sln` 已含 `NewManga.ApplicationCore` 工程（无需改 sln，与 `:103` 不冲突） |
| **F-03** `Frontends.Current` 无合法落点（§4.1 定义新工程 vs §15.6 写域） | P0 | **closed** | Q-18 `:49`「落 `Shell/V2/Frontends/`（in-app），不新建工程、不改 sln」；R-CURRENT-3 `:57`；禁止范围 `:103`；`Shell/V2/**` 在 allowed_paths `:33`；现状该目录不存在（可新增） |
| **F-04** `switch` 入口越界（与 Q-15、方案 `:646` FEA-07 冲突） | P1 | **closed** | R-SWITCH 整节 `:65-68`：preflight-only、`{allowed, blockers}`、零 Host/Core 副作用、R-SWITCH-3 明示不实现执行入口/不启动 Fluent；Q-19 `:50`；`GOAL-PROGRESS:23` Q-15/Q-19 合并行；与方案 `:646`（FEA-07 拥有运行期切换）一致 |
| **F-05** AC6 无断言方式（Host 非进程级单例） | P1 | **partial** | AC6 `:88` 已引 `ReferenceEquals` + `FakeHostController.StartCalls`/`HostController.StartRequests` 计数不增（方向正确）。**残留**：写作 `ReferenceEquals(host, host)` 是同义反复，应 `hostBefore/hostAfter`；未写"现状 V2 本就不 Dispose"基线 → R2-04 |
| **F-06** AC2 命令不合法 + 基线未冻结 | P1 | **open** | 冻结点已改 `91be6c134` ✓（`:56`/`:84`）；但命令 `dotnet test apps/desktop-avalonia/tests` 仍**不可执行**（实测 MSB1003，见 §核查-6）→ R2-01 |
| **F-07** AC1「只增不改」与 S1–S6 自相矛盾 | P1 | **closed** | R-CURRENT-1 `:55`、AC1 `:83` 已降为「公开签名/路由不变；内部实现可改 + 适配层新增；每处 Handoff 说明」 |
| **F-08** AC5「有损编辑态」/结构化错误未定义 | P1 | **partial** | 结构化结果已给 `{allowed, blockers}`（R-SWITCH-1 `:66`）✓；**「有损」判定谓词与 `blockers` 元素类型仍未定义**（`:61`/`:87` 全文无定义）→ R2-02 |
| **F-09** `tests/**` 写域过宽 | P1 | **open** | `:34` 未改，仍覆盖 6 个测试项目 → R2-03 |
| **F-10** S5「一个共享 RunMonitor」双实现歧义 | P1 | **partial** | R-STATE-1 `:60` 限定权威＝ApplicationCore 本地对象 → 权威已隐含为 `RunMonitor<T>` ✓；**legacy `Shell/V2/RunStatusMonitor` 的去留仍未写** → R2-15 |
| **F-11** 禁止范围误标 FEA-05 | P1 | **partial** | `:104` 改为「不实现切换执行入口/不启动 Fluent；不实现 FEA-05 起的 UI 功能」——切换部分已修 ✓；**FEA-05 仍被表述为"UI 功能"主体、S6 Appearance draft 未限 preflight 只读** → R2-06 |
| **F-12** 与方案 DAG 的 FEA-02-BRIDGE 依赖边不符 | P1 | **open** | `depends_on` `:11-13` 未变；PLAN `:16` 未变；R-STATE-4 `:63`「Host 生命周期归既有装配」事实上认定 BRIDGE 非必需，但无书面记录 → R2-07 |
| **P2-1** base_commit 未随冻结提交更新 | P2 | **closed** | `:14 base_commit: e34796862` ✓ |
| **P2-2** §15.3 引用行号偏一行 | P2 | **open** | `:44` 仍为 `§15.3 :876-886`（表体 `:880-887`）→ R2-08 |
| **P2-3** AC3 静态检查无口径/grandfather | P2 | **open** | AC3 `:85` 仍只有「grep 无新增权威副本」→ R2-09 |
| **P2-4** AC8 硬编码 r2 | P2 | **open（且本轮触发）** | AC8 `:90` 仍为「范围复核 r2 approved」；本轮未 approved → 若需 r3，AC8 再次不可满足 → R2-10 |
| **P2-5** §12.1「route adapter」无承载 | P2 | **open** | 标题 `:3`、引用 `:42` 仍含 route；S1–S6/AC1–AC8 无 route → R2-11 |
| **P2-6** AC4 缺具名测试/未迁出登记字段 | P2 | **partial（回退）** | AC4 `:86` 较 v1 `:80` **删去了**「未迁出项明确登记」；deferral 表仅登记契约级 deferral → R2-12 |
| **P2-7** L-2 与 F-01 同源 | P2 | **closed** | L-2 `:97` 已改为「Q-16 明确不触 wire/命令面；若后续需透传 Draft 命令 → `blocked`（转 FEA-05/07 并先完成 M2-C1）」；与 `FEA-C11_IMPL_PREREQS.md:25` 归属（FEA-04 不在列）一致 |
| **P2-8** `doc/reviews/**` 写权主体未区分 | P2 | **open** | 禁止范围 `:103` 未注 → R2-13 |

**汇总：closed 7 / partial 5 / open 8（合计 20）。**

---

## 2. 逐项核查（按派发核查点 1–9）

### 核查-1（Q-16 / F-01）——**闭环成立**

- 裁决书面化：`GOAL-PROGRESS:24` Q-16 行；卡 `:7 approval` 改为 `…_Q16_Q19`。
- 卡内一致性：R-STATE-1 `:60`「权威源限于 ApplicationCore 本地对象（Q-16）」；迁出表目标列全部改写（`:74-78` 加注 `（ApplicationCore）`/`（RunMonitor）`）；L-2 `:97`；禁止范围 `:102`；新增 deferral 表 `:108-113` 承接 FEA-03 `Q-8`/`R-JOURNAL-4③`。
- **可达性实证（关键）**：S1–S3 的目标权威在 ApplicationCore 中**确有能力**，且不需要新 wire：
  - S1：`DraftBuffer`/`DraftSnapshot` 已含 `DraftId`、`SessionId`、`PageId`、`RegionId`、`BaseRevisionId`、`Status`（`src/NewManga.ApplicationCore/DraftBuffer.cs:38-49`），`FlushAsync` 存在（`:151`）→ "未保存 region type 切换前 flush" 可实现。
  - S2/S5：`RunMonitor<T>`（`RunMonitor.cs:13`）、`RunStateStore<T>`（`RunStateStore.cs:10`）可承接共享投影。
  - S3：`IntentCoordinator<T>.ExecuteAsync(string intentKey, …)`（`IntentCoordinator.cs:27`）承接同键合并；且**现有命令面已传意图键**——`StudioBatchViewModel.cs:1088` `StartRunAsync(new RunStartRequest(command, scope, null, _intentIdempotencyKey))`，既有错误码 `IDEMPOTENCY_KEY_REUSED`（`Services/IHostController.cs:34`）→ 「丢 ACK 后重试不二次启动」**无需新 wire 即可满足**。
- 结论：F-01 的 P0 情形（写域不可达）已消除。残留的只是**命名/口径**问题（R2-05），不是阻塞。

### 核查-2（Q-17 / F-02）——**足够，闭环**

`NewManga.App.csproj` 是唯一需要改的工程文件（新增 `<ProjectReference …NewManga.ApplicationCore.csproj />`）；该文件在 `:30` 单列；`:105` 把范围限死为"仅 ApplicationCore 引用单点"，`:48`/`:105` 要求 Handoff 记录。`NewManga.sln` 已含 ApplicationCore 工程，**无需改 sln**，与 `:103`「不改 sln」不冲突。`Shell/V2/Frontends/` 为新增目录，SDK 风格 csproj 自动包含 `**/*.cs`（csproj 内无显式 `<Compile Include>`，已核）→ 无需二次改 csproj。判定：足够。

### 核查-3（Q-18 / F-03）——**闭环**

`Shell/V2/Frontends/` 落在 `Shell/V2/**`（`:33`）；`:103` 禁新建工程/改 sln 与方案 §15.6 `:914`（sln/组合根 DSH 单点）一致；R-CURRENT-3 `:57` 规定门面只转发与状态映射、业务真值留在 Host/Core/ApplicationCore，与 AC3 呼应。现状该目录不存在（`Test-Path` False），属纯新增，符合"适配层只能是增量"。

### 核查-4（Q-19 / F-04）——**与方案一致**

方案 `:646` 把「运行期切换/窗口、switch journal、§12.3 跨 UI/双屏/故障矩阵」归 **FEA-07**；`:376` 的 Preflight 是切换编排第一步；`:878` 把 "switch preflight fail-closed" 写在 FEA-04 语义内。v2 `R-SWITCH-1..3`（`:66-68`）与之逐条对应：只返回 `{allowed, blockers}`、失败零副作用、**不**实现执行入口/不启动 Fluent/不改运行期路由。**一致**。

### 核查-5（AC6 / F-05）——**方向对、措辞需修（R2-04）**

`:88` 现文「`ReferenceEquals(host, host)` 不变」是**同义反复**（同一表达式恒真），不能证明"关闭/重建内容前后同一 Host"。可执行写法：以注入的 `IHostController` 构造 `AppShellV2`（`Shell/V2/AppShellV2.axaml.cs:37` 注入点；`App.axaml.cs:56` 逐进程 `new HostController(...)`，**Host 非进程级单例**），捕获 `hostBefore` → 关闭/重建内容 → `ReferenceEquals(hostBefore, hostAfter)`；并断言 `FakeHostController.StartCalls`（`tests/NewManga.App.Tests/FakeHostController.cs:17`；`LifecycleLog` `:19/:49` 记录 `"start"`）与 `HostController.StartRequests`（`Services/HostController.cs:67`）不增。另建议补基线说明：现状 V2 **本就不 Dispose Host**（V2 侧唯一 `IDisposable` 是 `Shell/V2/RunStatusMonitor.cs:14`；legacy 才在 `Views/MainWindow.axaml.cs:852` 关闭时 Dispose）→ AC6 是防回归而非新增能力。

### 核查-6（AC2 / F-06）——**命令实测不可执行（R2-01，P1）**

- 现文 `:56`/`:84`：`dotnet test apps/desktop-avalonia/tests`。
- 实测（只读 MSBuild 求值）：
  ```
  > dotnet msbuild 'apps/desktop-avalonia/tests' -getProperty:MSBuildProjectFullPath
  MSBUILD : error MSB1003: 请指定项目或解决方案文件。当前工作目录中未包含项目或解决方案文件。
  ```
- 目录内容实测：`apps/desktop-avalonia/tests` 下只有 `NewManga.runsettings`，6 个测试工程在**子目录**中，且无 `.sln`；MSBuild 的目录解析不递归 → 必然 MSB1003。
- 正确写法（方案 `:737-738` 已给）：`dotnet build apps/desktop-avalonia/NewManga.sln -warnaserror` + `dotnet test apps/desktop-avalonia/NewManga.sln --no-build`（如需 runsettings 再加 `--settings apps/desktop-avalonia/tests/NewManga.runsettings`）。
- 冻结点改 `91be6c134` **可接受**（该提交仅治理文档变更，与 `e34796862` 测试面等价；且注明"FEA-03 合并后"）；但 AC2 仍缺**冻结计数**（GOAL-PROGRESS `:13` 有 1052 passed 口径；本席位未运行该命令，不验证现值）。

### 核查-7（AC1 / F-07）——**闭环**

`:55`/`:83` 已把"只增不改"降到**公开签名/路由级**，并允许内部实现改动 + 适配层新增，要求每处改动入 Handoff。可机械判定：`git diff` 路径全部落在 allowed_paths 内 + Handoff 逐处说明 + 公开成员清单零变更。建议在 Handoff 模板要求列"公开成员变更 = 0"的显式行（见 R2-09 合并建议）。

### 核查-8（其余 P1/P2 是否仍有 open）——**仍有 open，共 12 项 P2（R2-04…R2-15）**

逐项与最小修法见 §4 表。要点：
- **写域完整性**：`tests/**`（R2-03，P1）；其余缺口已由 Q-17/Q-18 补齐。
- **S4/S6 可验证性**：S4 目标列写 `ReaderSession`（不存在）但"Core 进度/按书偏好"经**既有** `IHostController.LoadReaderBookAsync`（`:161`）/`SaveReadingProgressAsync`（`:106`）可达 → 只需改指实有成员（R2-05）；S6 目标列含 `Appearance draft` 且未限 preflight 只读（R2-06）。
- **preflight blocker 判定**：R2-02（P1）。
- **L 判定**：L-1 `:96`、L-2 `:97`、L-5 `:98` 与 `FEA-C11_IMPL_PREREQS.md:24-26` 归属表一致（FEA-04 不在任何 L 项归属列）→ **三项判定均成立**，仅 L-2 的 `blocked` 再触发条件已写明 ✓。
- **治理指针**：STATUS `:7`/PLAN `:16`/LEDGER `:46` 均已更新为「范围冻结 v2；待独立复核 r2 → ready」✓；但 **GOAL-PROGRESS `:3-4` 与 `:30-31` 仍写 HEAD=`91be6c134`、范围冻结 v1、下一动作 r1**（R2-14）。

### 核查-9（是否引入新问题）——**引入 2 项新 P2、1 项新 P1 变体**

1. **新 P1 变体（R2-01）**：v1 的错误命令是 glob（`tests/**`），v2 改成"目录"但仍非法——问题未消除而是换了形态（实测证据见核查-6）。
2. **新 P2（R2-05）**：Q-16 的"权威源限于 **ApplicationCore 本地对象**"写成绝对式，与 S4（Core 进度）、S3（Core 幂等）不自洽；R-CURRENT-3 `:57` 仍写"业务真值仍在 Host/Core/ApplicationCore"。同一卡内两种口径。
3. **新 P2（R2-14）**：GOAL-PROGRESS 头部/下一动作未随 v2 更新（指针 stale）。
4. 另：卡 `:44` 的 §15.3 行号、`:34` 的 `tests/**`、`:90` 的 AC8 等 r1 遗留项未修（非新问题，但会累积）。
5. AC2 现文把 `91be6c134` 称"冻结点"而 frontmatter `base_commit` 是 `e34796862`——两者不矛盾（前者是测试基线提交，后者是实现分叉点），但建议在 Handoff 明确区分，避免 evidence pin 混用（并入 R2-10 的轮次/指针记账建议）。

---

## 3. 结论与放行条件

`changes_requested`。r1 的三个 P0 已消除，v2 的框架（wire defer、csproj 单点、Frontends 落点、preflight-only、deferral 登记）**成立且与方案一致**；卡在结构上已经可执行。

放行到 `ready` 只需一轮 v3 处置 **3 项 P1**（全部为文本改动，无需新裁决）：

1. **R2-01**：AC2/`:56` 命令改为 `NewManga.sln` 路径（并可选附 `--settings`）。
2. **R2-02**：R-STATE-2/AC5 冻结「有损」谓词 + `blockers` 元素类型。
3. **R2-03**：`:34` `tests/**` 收窄为 `tests/NewManga.App.Tests/**`（如确需 ApplicationCore 断言则并列 `tests/NewManga.ApplicationCore.Tests/**`，并在卡内写明理由）。

12 项 P2 可与上述同批处置（见 §4），不构成阻塞，但建议一并修以少一轮往复。

---

## 4. Findings

| 编号 | 级别 | 位置（v2 = `55543c10d`） | 问题 | 最小修法 |
|---|---|---|---|---|
| **R2-01** | **P1** | 卡 `:56`（R-CURRENT-2）、`:84`（AC2） | **测试命令不可执行。** `dotnet test apps/desktop-avalonia/tests` 实测 `MSB1003`（该目录只有 `NewManga.runsettings`，6 个工程在子目录且无 sln；MSBuild 目录解析不递归）。AC2 是唯一回归 Gate，命令失效则证据无法按卡产出 | 改为 `dotnet test apps/desktop-avalonia/NewManga.sln --no-build`（前置 `dotnet build …/NewManga.sln -warnaserror`）；如需运行设置加 `--settings apps/desktop-avalonia/tests/NewManga.runsettings`。参照方案 `:737-738` |
| **R2-02** | **P1** | 卡 `:61`（R-STATE-2）、`:87`（AC5） | **「有损编辑态」与 `blockers` 元素无定义**，preflight 的阻断判定不可机械验证（r1 F-08 未闭环）。"未迁出且"这一并列条件亦无判定口径 | 冻结谓词（建议，均实测存在）：S1 `_pendingRegionType != null`（`ViewModels/V2/Studio/StudioInspectorViewModel.cs:195/282`）；S2 `_pendingNavigation != null`（`StudioPageViewModel.cs:257`）；S3 本轮 intent key 未落 receipt（`StudioBatchViewModel.cs:329/1079`）；S6 ThemeStudio editor draft 脏；FEA-03 缓冲 `DraftBufferStatus.{Active,Conflicted}`（`ApplicationCore/DraftBuffer.cs:3-9`）。`blockers` 元素冻结为 `record PreflightBlocker(string Code, string Source /*S1…S6*/, string Detail)`；并写明 Code 只用于 UI/日志、**不进** wire 与 `allowedRunErrorCodes` |
| **R2-03** | **P1** | 卡 `:34`（allowed_paths） | **`tests/**` 仍宽于方案 `:924`「对应 tests」**：覆盖 6 个测试工程 130 个源文件，含 `CoreClient.Tests/Commands/**`（冻结契约对照）、`Host.Tests`、`ThemeEngine.Tests`、`DesignSystem.Tests`——FEA-04 不需要写这些，改动会污染其它线冻结证据（r1 F-09 未闭环） | 收窄为 `apps/desktop-avalonia/tests/NewManga.App.Tests/**`（必要时并列 `…/NewManga.ApplicationCore.Tests/**`）；其余测试工程写明"只读运行，不写" |
| **R2-04** | P2 | 卡 `:88`（AC6） | `ReferenceEquals(host, host)` 为**同义反复**，不能证明前后同一 Host；另缺"现状 V2 本就不 Dispose Host"基线（r1 F-05 残留） | 改为 `ReferenceEquals(hostBefore, hostAfter)`；补基线句；保留 `FakeHostController.StartCalls`(`tests/NewManga.App.Tests/FakeHostController.cs:17`)+`HostController.StartRequests`(`Services/HostController.cs:67`) 计数不增 |
| **R2-05** | P2 | 卡 `:60`（R-STATE-1）、`:85`（AC3）↔ `:57`（R-CURRENT-3）、S1/S3/S4 目标列 `:74/:76/:77` | **Q-16 口径过度绝对化且点名不存在的类型。**（a）"权威源限于 ApplicationCore 本地对象"与 S4（Core 进度/按书偏好）、S3（Core 侧幂等保证）及 `:57`"业务真值仍在 Host/Core/ApplicationCore" 不自洽；（b）`EditingSession`、`session intent store`、`ReaderSession` 在 ApplicationCore 21 个公开类型与全仓源码中**均不存在**（实测 0 命中）→ 实现者会被迫越权写 ApplicationCore 或在 V2 造类型（后者正是 AC3 禁止的第二真值） | 把 R-STATE-1/AC3 改为「权威源 = Host/Core/ApplicationCore 的**既有**对象与命令（本卡不新增命令面）」；目标列改指实有成员：S1→`DraftBuffer`/`DraftSnapshot.DraftId/SessionId`（`DraftBuffer.cs:38-40`）；S2→`RunMonitor<T>`+UI memento；S3→`IntentCoordinator<string>.ExecuteAsync(intentKey)`（`IntentCoordinator.cs:27`）+ 既有 `StartRunAsync` 键透传（`StudioBatchViewModel.cs:1088`）；S4→既有 `IHostController.LoadReaderBookAsync:161`/`SaveReadingProgressAsync:106` |
| **R2-06** | P2 | 卡 `:72-79` 表头、`:104` | FEA-05 仍被表述为"UI 功能"主体（方案 `:644` FEA-05＝三层注册/Appearance，`:645` FEA-06＝Fluent 界面）；S6 的「Appearance draft」未限 preflight 只读，存在越入 FEA-05 的口子（r1 F-11 残留） | 禁止范围改为「不实现 FEA-05 三层注册/Appearance 迁移、不实现 FEA-06 Fluent 界面」；S6 补「Appearance draft 仅作 preflight 只读判定，不实现 registry/scheme/scale/迁移」 |
| **R2-07** | P2 | 卡 `:11-13`（depends_on）、`:63`（R-STATE-4）；`REBASELINE_PLAN.md:16` | 方案 DAG `:666-669` 为 `FEA-02-BRIDGE → FEA-04`，卡/PLAN 均无该节点；R-STATE-4「Host 生命周期归既有装配」事实上认定 BRIDGE 非必需，但无书面记录（r1 F-12 未闭环） | 在「契约 deferral 登记」加一行：「FEA-02-BRIDGE（ExitCoordinator/Host 生命周期）不构成本卡前置；Host 生命周期维持现行装配（`Views/MainWindow.axaml.cs:852` legacy Dispose；V2 无 Dispose）」；或由 DSH 在 PLAN 记 descoped |
| **R2-08** | P2 | 卡 `:44` | `§15.3 :876-886` 仍偏一行：表体实为 `:880-887`（`:876` 是标题，S6 在 `:887`） | 改 `:880-887` |
| **R2-09** | P2 | 卡 `:85`（AC3）、`:83`（AC1） | AC3 静态检查仍无 allowlist/脚本/既有态 grandfather（`RunStatusMonitor._knownRunIds` `Shell/V2/RunStatusMonitor.cs:31`、`ShellState.SpaceViewState` `:119-139` 会被误判）；AC1 的"公开签名不变"缺机械检查点（r1 P2-3 未闭环） | AC3 增：新增 `tests/NewManga.App.Tests/V2BusinessTruthBoundaryTests`（参考先例 `tests/NewManga.ThemeEngine.Tests/DependencyBoundaryTests.cs`）+ Handoff 允许清单 + 既有态 grandfather 逐项；AC1 增 Handoff 必填行「公开成员变更 = 0」 |
| **R2-10** | P2 | 卡 `:90`（AC8）、`:21`（review_appointment） | AC8 仍硬编码「范围复核 **r2** approved」；本轮未 approved → 若走 r3 则 AC8 再次不可满足。`review_appointment` 仍指向 r1 报告 | 改为「最后一次范围复核 approved（P0/P1=0），报告路径记入 `review_appointment`」；`ready` 时把 `review_appointment` 指向最终 approved 报告 |
| **R2-11** | P2 | 卡 `:3`（标题）、`:42`（引用） | §12.1 交付物含「V2 state/**route**/VM adapter」，但 S1–S6/AC1–AC8 无 route 承载；现状 route 面为 `Shell/V2/ShellDeepLink.cs`（`:28 TryParse`/`:122 ToQuery`）（r1 P2-5 未闭环） | R-CURRENT 下加一行：「route 适配限于 `Shell/V2/ShellDeepLink` 的读取/映射；本卡不改其格式」或显式写「route 由 ShellDeepLink 承载，本卡不改」 |
| **R2-12** | P2 | 卡 `:86`（AC4） | 相对 v1 `:80` **回退**：删去「未迁出项明确登记」；deferral 表 `:108-113` 只登记契约级 deferral，未覆盖 S1–S6 迁移状态 | AC4 补：每项四字段 `baseline_evidence(commit:line)` / `new_authority(type/member)` / `assert_test(FQN)` / `status(migrated|deferred)+reason`，以 v-matrix 落 `verification/FEA-04/` |
| **R2-13** | P2 | 卡 `:103` | 「不改 `doc/reviews/**`」未区分写权主体：审查报告由 Review Appointment 的独立上下文审查者写入（如本报告与后续 `FEA-04-r1.md`） | 加一句「`doc/reviews/FEA-04-*.md` 由 Review Appointment 的独立审查者写入，不属实现写域」 |
| **R2-14** | P2 | `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:3-4`、`:30-31` | **治理指针 stale**：仍写「当前 HEAD `91be6c134`」「范围冻结 v1，待独立复核 r1」「下一动作：…派独立复核 r1」，未随 v2（`55543c10d`）更新 | 更新 HEAD/轮次/下一动作；并记录派发哈希笔误（`d8d1d3b6a` → `55543c10d`） |
| **R2-15** | P2 | 卡 `:78`（S5 目标列） | **S5 的 legacy 实现去留未写。** 现状 Console 已注入 legacy `Shell/V2/RunStatusMonitor`（`ViewModels/V2/Console/ConsoleViewModel.cs:21/103/113`；该文件 `:7-8` 自述"ONE shared Run-status source"），而 S5 目标是"一个共享 `RunMonitor`"＝`ApplicationCore.RunMonitor<T>`；两者并存即 AC3 要防的第二真值形态的过渡态，卡内未说明本卡是否移除/降级 legacy 或登记为未迁出（r1 F-10 残留） | S5 补一句：「本卡将 Console 的 Run 投影接到 `RunMonitor<T>`；legacy `RunStatusMonitor` 降为 dispatcher 薄适配（或：保留并在 Handoff 登记为未迁出项 + 原因 + 后继 Task）」；并给出"单轮每 Run 最多一次 snapshot/projection 查询"的调用计数断言（`ApplicationCore/RunMonitor.cs` 头部与 `README.md:12` 已有注入计数先例） |

---

## 5. 边界声明

本报告**只审范围冻结**（Task 卡 v2 + 其引用的方案/授权/前置/代码事实），**不构成实现验收**，不构成设计或契约批准。`approved`/`changes_requested` 仅针对"范围文本是否可执行、可机械验证、与方案和治理指针一致"。本席位**未参与** FEA-04 的起草、实现或返修；**未修改**任何被审文件、卡、STATUS、PLAN、LEDGER、checkpoint 或源码；**未** commit/push；**未执行**构建/测试/真机运行（唯一命令行探测为只读 MSBuild 求值，结论见核查-6）。所有文件行号基于 `55543c10d` 实测；行号存在性不证明调用链完整。

**特别提示**：本报告 `reviewed_head` 为实际 HEAD `55543c10d`，派发请求中的 `d8d1d3b6a` 不可解析（见「请求指针异常」）。若 DSH 的 evidence pin / Closeout Record 引用 `d8d1d3b6a`，pin 校验必失败。
