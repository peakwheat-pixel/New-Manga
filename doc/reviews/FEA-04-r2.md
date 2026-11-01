---
task_id: FEA-04
review_id: FEA-04-r2
kind: implementation-review
reviewer: fea04-impl-reviewer
reviewer_kind: subagent
reviewer_source: DSH fresh 独立上下文派发（同一复核席位续审；未参与 FEA-04 的起草、实现或返修，只读被审 head）
base_commit: 8777b74f7
reviewed_head: ccca5ec59
date: 2026-11-02
timezone: Asia/Shanghai
conclusion: changes_requested
counts: { P0: 0, P1: 2, P2_new: 4, r1_P2_residual_accepted: 14 }
scope: 仅实现交付复核 r2（r1 findings disposition + 新 head 验证）；不构成集成批准
---

# FEA-04 实现复核 r2（r1 disposition + 新 head）

**结论：`changes_requested`（P0 = 0、P1 = 2、本轮新增 P2 = 4；r1 遗留 P2 14 项按“接受遗留”处置）**

**一句话理由**：r1 的 **IMPL-02 已真实闭环**（Page 投影恢复 + 判别性回归用例），**IMPL-04 基线已实测且数据自洽**，`git diff --check` 已 `rc=0`（r1 IMPL-17 关闭），**IMPL-03 的“不实陈述”部分修正**；但 **IMPL-01 的「未迁出登记」在 reviewed head 中不存在**——`doc/handoffs/FEA-04-68c72ba57.md` 相对 `8777b74f7` 只有 EOL 变更、内容零差异，S3/S5 行仍称“投影来自 RunMonitor / 单例 Current RunMonitor”，且新增的 `_runProjection` 未进入 AC3 私有状态清单；同时 **AC7 证据仍缺原始运行日志**，`preflight-blocker-matrix.md` 与 Handoff AC 表仍写“未执行 / NOT_RUN”。因此不能写 `approved`。

## 审查基线

| 项 | 值 | 证据 |
|---|---|---|
| 主仓库 | `G:\CODEX\New Manga`（main；本报告仅写 `doc/reviews/`） | `git rev-parse --short HEAD` → `c6f9a2944`（与 r1 相同，未新增提交） |
| worktree / 分支 | `G:\CODEX\New Manga.workspace\FEA-04` / `feat/fea-04` | `git rev-parse HEAD` → `ccca5ec594ee1a3c331bbcde6bab7fdf729ebaa1` |
| 被审 base / head | `8777b74f7` / `ccca5ec59` | `git log --oneline -6`：`ccca5ec59`、`917d9e830`、`b33149e54`、`7ec731336`、`3b805a735`（+ r1 的 `8777b74f7`…） |
| 本轮 diff | 9 文件，+210 / −184 | `git diff --stat 8777b74f7..ccca5ec59` |
| 相对卡基线累计 | 39 文件，+1872 / −207（与 r1 同一 39 文件集合，无新增路径） | `git diff --name-only 68c72ba57..ccca5ec59` |
| worktree 状态 | 审查/构建/测试前后 `git status --short` 均为空 | `git status --porcelain` |
| 环境 | Windows；.NET SDK `10.0.401`；`net9.0`；`runsettings`（MaxCpuCount=1） | `dotnet --version` |
| 本轮执行 | `dotnet build apps/desktop-avalonia/NewManga.sln`（含 restore 探测）+ 卡内 sln `--no-build` 测试复跑 + 新用例单跑 + `git diff --check`；**未** checkout 其它 commit、未改任何源码/文档 | 见 §4 |

**视角声明**：Architecture = executed（S3/S5 权威源、双源、生命周期）；Verification = executed（build/test/diff-check/证据逐文件核对）；Spec（AC 对照）= executed。**未执行**：基线 commit 的复测（不切换 worktree；以 DSH 实测表 + reflog 佐证，见 §5）、UI/真机、任何 commit/push/merge。

---

## 1. r1 P1 逐项处置（4 项）

| r1 ID | r1 要求 | r2 实测（head `ccca5ec59`） | 处置 |
|---|---|---|---|
| **IMPL-01** S3/S5 退化 | 二选一：接线共享 monitor；或按 AC4 在 Handoff 登记未迁出项（S3 投影读取未迁/intent 已迁；S5 legacy monitor + Batch 自有 timer），并修正 AC3/AC4 表述 | **未完成**：① `git diff --ignore-cr-at-eol 8777b74f7..ccca5ec59 -- doc/handoffs/FEA-04-68c72ba57.md` **输出为空** → Handoff 内容与 r1 head 相同，**无「未迁出登记」章节**；② `handoff:71` 仍称 S3“投影来自 RunMonitor StateStore”，`handoff:73` 仍称 S5“单例 Current RunMonitor”，`handoff:83` 仍称“`_projection` 不是旧 `_runProjection`、Run projection 只从 Current RunMonitor 读取”（head 已恢复 `_runProjection` push + Host 读取），`handoff:84` 仍称“投影权威均在 Current 对象”——与 head 相反；③ `handoff:93-100` AC 表仍 `BLOCKED/NOT_RUN`；④ 新私有字段 `StudioPageViewModel._runProjection`（`:246`）未进入 Handoff AC3 清单 | **NOT CLOSED → P1（R2-P1-01）**。**判据补充**：就 AC4 文义而言，**“登记”即可接受、不必接线**——只要 Handoff 逐项写明 `S3：RunId=memento(已迁)、intent key=IntentCoordinator(已迁)、投影读取=Host `IRunController.GetTaskProjectionAsync`(**未迁**，原因：避免 16 个既有 Batch 用例改写/失败)、后续=FEA-07/FEA-05`；`S5：Console/Shell 共用 legacy RunStatusMonitor Host 轮询(**未迁**)、Batch 自带 DispatcherTimer(**未迁**)、原因/后续`，并同步修正 `:71/:73/:83/:84` 与 AC 表，即可判 `closed`（R-STATE-1 的偏差作为 DSH 批准的 deferral 由集成侧承接）。**当前 head 未见该登记，故不能关闭。** |
| **IMPL-02** Page 投影丢失 | 恢复 push→读取，补回归 | **CLOSED**：`StudioPageViewModel.cs:246` 新增 `_runProjection`；`:1366-1374` `ApplyRunProjection` 写回；`:712` `RunProjection => _runProjection ?? _current.GetRun(...)?.StudioProjection`；`StudioWorkspaceView.axaml.cs:206-210` 推送链路重新生效；`StudioExportViewModel.cs:332-336` 导出 preflight 计数随之恢复。回归用例 `FEA04CurrentAdapterTests.cs:376-393`（`Assert.Same` + `PipelineWired`）；单独复跑 `EXIT=0`（1/1 通过，13 ms）。按代码构造，该用例在 r1 head 必失败（当时 `ApplyRunProjection` 丢弃入参、`RunProjection` 读未填充缓存），具判别性。 | **CLOSED**；残余 P2 见 R2-P2-02/03/04（非阻断） |
| **IMPL-03** 证据不实 | 更新 lifecycle/baseline/sln 证据、入库原始日志、统一冻结命令 | **PARTIAL**：lifecycle 的相反陈述已改正（`lifecycle-assertions.md:5` 明确“保持既有 Host 轮询”）；基线实测表已写入；sln 结果已更新 931；diff-check 已 rc=0。**仍缺**：① `verification/FEA-04/` 无任何原始 build/test 日志或 trx（只有汇总 md）；② `preflight-blocker-matrix.md:7-11,17,21` 仍逐行“已新增；未执行（build restore 阻断）/以上断言当前均为未执行状态”；③ Handoff AC 表 `:93-100` 仍 `NOT_RUN/BLOCKED`；④ `sln-test-results.md:3` 命令仍带 `--blame-hang --blame-hang-timeout 120s`，非卡 `:58/:86` 冻结命令 | **PARTIAL → P1（R2-P1-02）** |
| **IMPL-04** 基线未实测 | 同命令在基线 commit 实测并给逐工程对照 | **CLOSED（实质）**：`baseline-comparison.md:3-15` 基线实测 914/0/60（Host 51、ThemeEngine 235、DesignSystem 85、CoreClient 116、AppCore 31、App 396/403）；与 r1 实测 head（930/412/419）之差恰为 16 个 FEA-04 用例，与本轮 head 931/413/420 之差恰为 17，逐工程数据一致；reflog 佐证 `03:45:46 checkout → 68c72ba57`、`03:46:48 checkout 回 feat/fea-04`（62 s 窗口，覆盖 build+全量测试的合理耗时）。AC2 判据（failed=0、passed ≥ 基线、skipped 不变）在本轮复跑中成立。 | **CLOSED**；残余 P2 见 R2-P2-01（实现列陈旧/算术错误/控制字符，无原始日志） |

## 2. r1 P2 逐项 disposition（15 项）

| r1 ID | 主题 | r2 状态 | 依据 |
|---|---|---|---|
| IMPL-05 | AC6 断言空转 | **partial → 接受遗留（P2）** | `lifecycle-assertions.md:3` 改写成“断言 `ReferenceEquals(hostBefore,hostAfter)` 且 `LifecycleLog` 无 Dispose 记录”，但测试实际用 `Assert.Same`、`FakeHostController.DisposeAsync` 仍为 `ValueTask.CompletedTask` 无计数（`:994`）→ 证据**仍高估**了断言强度；机制未变 |
| IMPL-06 | `Preflight(signals)` 公开绕过 | 接受遗留 | 无代码变更 |
| IMPL-07 | S5 去重用例名不副实 | 接受遗留 | 无代码变更；生产 Batch 仍有独立 `DispatcherTimer` 轮询 |
| IMPL-08 | route `ToQuery().TrimStart('?')` 弱化 | 接受遗留 | 无代码变更 |
| IMPL-09 | 清空 Run 后 `_projection` 残留 | 接受遗留 | 无代码变更 |
| IMPL-10 | 死代码/未用字段 | 接受遗留 | 无代码变更；`EnsureRunSubscription`、`CurrentRunDataSource`、`KnownRunIds`、`RunObserved`、`using Avalonia.Threading` 仍为死路径 |
| IMPL-11 | `DraftBuffer` 30 天 debounce 参数误用 | 接受遗留 | 无代码变更 |
| IMPL-12 | S1 flush 语义浅 / fire-and-forget | 接受遗留 | 无代码变更 |
| IMPL-13 | intent key 被 typed rejection 永久保留 | 接受遗留 | 无代码变更 |
| IMPL-14 | memento 无锁 / `RunObserved` 不退订 | 接受遗留 | 无代码变更 |
| IMPL-15 | 静态 `CurrentFrontend.Active` 单点 | 接受遗留 | 无代码变更 |
| IMPL-16 | Handoff/Task 卡/GOAL 指针陈旧 | **partial（并入 R2-P1-01）** | EOL/`diff --check` 子项已修（IMPL-17），但 S1–S6 表、VM 私有状态、AC 表、Task 卡 `:14-19/:140`、`GOAL-PROGRESS:3` 仍为旧状态；「未迁出登记」缺失是 R2-P1-01 的直接内容 |
| IMPL-17 | `git diff --check` 失败（CRLF） | **CLOSED** | `git diff --check 68c72ba57..ccca5ec59` → `rc=0`（本席位实测）；handoff 159 LF/1 游离 CR（见 R2-P2-01 注） |
| IMPL-18 | S4 语义锚点/page ID、滚动只恢复一次 | 接受遗留 | 无代码变更 |
| IMPL-19 | S6 `dirty ≡ unmapped`、无逐项映射 | 接受遗留 | 无代码变更 |

**汇总**：closed 2（IMPL-02、IMPL-04）+ r1 已关的 IMPL-17 = 3；partial 2（IMPL-03→P1、IMPL-16→并入 P1-01）；其余 10 项接受遗留（均为 P2、不阻断）。**无“美化成 closed”的项**。

## 3. 新 head 变更核查（含派发 Q5/Q7）

### 3.1 范围、禁改面、AC1

- 本轮 9 文件全部在卡 `allowed_paths` 前缀内（`ViewModels/V2/Studio/StudioPageViewModel.cs`、`tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs`、`doc/handoffs/FEA-04-*.md`、`verification/FEA-04/**`）；**0 越界**。
- 禁改面 0 命中：无 Host/Core/CoreClient 源码、无 `*.sln`、无 `schema.py`/migrations、无 `doc/contracts/**`。
- **AC1 不受影响**：本轮无公开成员增删；`RunProjection`/`ApplyRunProjection` 签名未变，仅新增私有字段 `_runProjection` 与注释；`ShellDeepLink`/路由零改动。

### 3.2 IMPL-02 修复质量与派发 Q7（双源 / Raise 覆盖）

- **push→读取已复现**：`ApplyRunProjection(pushed)` → `RunProjection` 返回同一引用（`Assert.Same` 通过）；`PipelineWired` 为真。经 `StudioWorkspaceView.SyncBatchAsync`（`:206-210`，触发点 `:225/:246`）的既有推送链路现在真正生效；导出 overlay 的 `FailedPageCount/BlockedPageCount/HasRunProjection`（`StudioExportViewModel.cs:332-336`）随 `RunProjection` 恢复。
- **双源判定**：`_runProjection`（workspace push）优先，`_current.GetRun(...)`（monitor）仅为兜底。生产路径中 monitor 仍无消费者（r1 IMPL-01 未接线），因此**实际仍为单一 push 来源**，不构成新的双权威；风险在“永不失效”而非“双写”。
- **Raise 覆盖**：`ApplyRunProjection` 设置字段后 `RefreshPipelineBand()` 已 Raise `PipelineWired/PipelineHeaderText/PipelineNotWired/PipelineNotWiredNote`，随后又重复 Raise 其中三项（源自基线的冗余）；但**未 Raise `nameof(RunProjection)`**，而 `RefreshRunProjectionAsync`（`:1328-1335`）只 Raise 不写字段。当前 XAML 无 `RunProjection` 绑定、导出 overlay 打开时按需读取，故未造成可观察回归；列为 P2（R2-P2-03）。
- **新问题判定**：**未引入 P0/P1 级新问题**；新引入的 P2 风险为 R2-P2-02（load 不清 `_runProjection`）与 R2-P2-03/04。

### 3.3 新回归用例质量

- 具判别性（r1 head 必失败、现 head 通过）；`[Fact]` 单跑 `EXIT=0`（`%TEMP%\FEA04-r2-pipeline-test.log`）。
- 局限：用例名 “never drops it” 只覆盖“push 后立即读取”，**未覆盖真正的掉落路径**（之后 `LoadAsync`/`RefreshRunProjectionAsync`/换 run）；且绕过 view 的 `SyncBatchAsync` 直接调 `Page.ApplyRunProjection`（可接受，但非端到端）。列为 P2（R2-P2-04）。

## 4. 回归复跑（派发 Q5）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| Build（含 restore 探测） | `dotnet build apps/desktop-avalonia/NewManga.sln` | **EXIT=0**；**0 warnings / 0 errors**（3.7 s，全部工程 up-to-date） | `%TEMP%\FEA04-r2-build.log` |
| sln 全量测试 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | **EXIT=0；931 passed / 0 failed / 60 skipped（991）** | `%TEMP%\FEA04-r2-test.log` |
| 逐工程 | 同上 | Host 51/0/28=79；ThemeEngine 235/0/0=235；DesignSystem 85/0/0=85；CoreClient 116/0/25=141；ApplicationCore 31/0/0=31；**App 413/0/7=420** | 同上 |
| FEA-04 用例 | 同上（过滤 `FEA04CurrentAdapterTests`） | **17/17 passed**（含新 `Page_pipeline_band_…`） | 同上 |
| 新用例单跑 | `dotnet test … --filter FullyQualifiedName~Page_pipeline_band_uses_the_batch_push_and_never_drops_it` | **EXIT=0；1/1 passed（13 ms）** | `%TEMP%\FEA04-r2-pipeline-test.log` |
| 格式 | `git diff --check 68c72ba57..ccca5ec59` | **rc=0** | 本次会话输出 |
| 工作树 | `git status --short` | 空（构建产物被忽略） | 本次会话输出 |

**与 DSH 侧声明一致**：`931/0/60`、`EXIT=0`、`diff --check rc=0`、新用例通过。**AC2 判据成立**：failed=0；各工程 passed ≥ 基线表（914，App 396）；skipped 与基线一致（60）。

## 5. 证据复核（派发 Q3/Q4）

| 证据 | 声明 | r2 核对 | 判定 |
|---|---|---|---|
| `baseline-comparison.md:3-15` | 基线 `68c72ba57` 实测 914/0/60，App 396/403 | 数字与 r1 实测（930/412/419）及本轮（931/413/420）严格差分一致；reflog 显示 03:45:46 checkout 到 `68c72ba57`、03:46:48 切回（62 s 窗口足够 build+全量 test） | **可信（无原始日志）** |
| `baseline-comparison.md:17-28` | 实现 head 表 930/412/419 | **陈旧**：reviewed head 为 931/413/420（已含新增回归用例）；`:32` “App.Tests 419 = 基线 403 + 新增 17 项”算术错误（403+17=420）；`:17` 标题中 “feat/fea-04” 的 `f` 被 `0x0C`（form feed）替换（字节 offset 758），渲染为“eat/fea-04” | **P2（R2-P2-01）** |
| `sln-test-results.md:6,8-16,18-19` | head 931/0/60；基线 914；diff-check rc=0 | 931 表与复跑一致；基线行一致；rc=0 已复验。但 `:3` 命令仍带 `--blame-hang --blame-hang-timeout 120s`（非冻结命令），且无原始日志引用 | **部分**（归入 P1-02） |
| `lifecycle-assertions.md:1-6` | lifecycle 修正为“保持既有 Host 轮询” | `:5` 已与 head 一致（`RunStatusMonitor` Host 轮询、`Dispose` 只停定时器）；但 `:3` 的 `ReferenceEquals`/`LifecycleLog 无 Dispose 记录` 断言在测试中并不存在（fake `DisposeAsync` 无记录） | **部分**（IMPL-05 遗留 P2） |
| `preflight-blocker-matrix.md:7-11,17,21` | 五 blocker 状态 | 仍全部“已新增；未执行（build restore 阻断）”，`:17` “以上断言当前均为未执行状态”，`:21` “独立编译、测试结果…尚待” | **与 head 矛盾 → P1-02 组成项** |
| `doc/handoffs/FEA-04-68c72ba57.md` | 未迁出登记 / 结论表 | **无内容变更**（仅 EOL）；S3/S5 行与 head 相反；AC 表 `NOT_RUN/BLOCKED`；`:151` 存在 1 个游离 CR（“改 \r eturn await”形成 `eturn` 文本损坏） | **P1-01 + P2 卫生** |
| `doc/tasks/FEA-04.md` | Closeout | `:14-19` `branch/worktree/delivery_head` 仍 null；`:140` 仍称 NOT_RUN；未记录 r1 处置/r2 head | **P2（并入 R2-P1-01 的文档同步）** |

## 6. Findings（r2，仅记录未闭合项与新增项）

| 编号 | 级别 | 位置（head = `ccca5ec59`） | 问题 | 建议 |
|---|---|---|---|---|
| **R2-P1-01** | **P1** | `doc/handoffs/FEA-04-68c72ba57.md:71,73,83,84,93-100`（相对 `8777b74f7` **内容零差异**）；`StudioPageViewModel.cs:246`；`doc/tasks/FEA-04.md:14-19,140` | **r1 IMPL-01 未闭合：所称「Handoff 未迁出登记」在 reviewed head 不存在。** `git diff --ignore-cr-at-eol 8777b74f7..ccca5ec59 -- doc/handoffs/...` 为空；S3 仍称“投影来自 RunMonitor StateStore”、S5 仍称“单例 Current RunMonitor”、`:83` 仍称“`_projection` 不是旧 `_runProjection`、Run projection 只从 Current RunMonitor 读取”（head 已恢复 push 字段 + Host 读取，与 head 相反）；AC 表仍 `BLOCKED/NOT_RUN`；本轮新增私有投影缓存 `_runProjection` 未进 AC3 清单；Task 卡未记录 r1 处置 | 一个 docs 提交即可闭合：①在 Handoff 新增「未迁出登记」表（S3：RunId/intentKey 已迁、投影读取未迁=Host `GetTaskProjectionAsync`、原因=避免 16 个既有 Batch 用例改写失败、后续 FEA-07/FEA-05；S5：Console/Shell 共用 legacy `RunStatusMonitor` Host 轮询未迁、Batch 自有 `DispatcherTimer` 未迁、原因/后续）；②修正 `:71/:73/:83/:84` 与 AC 表；③AC3 清单补 `_runProjection`（push 缓存，非业务权威）；④Task 卡 Closeout 记 r1 disposition 与 `delivery_head: ccca5ec59` |
| **R2-P1-02** | **P1** | `verification/FEA-04/preflight-blocker-matrix.md:7-11,17,21`；`doc/handoffs/FEA-04-68c72ba57.md:93-100`；`verification/FEA-04/sln-test-results.md:3`；`verification/FEA-04/`（无原始日志） | **AC7 仍未闭合**：证据目录**没有任何原始 build/test 日志或 trx**（Q-009 判別力 artefact 缺失；931/60 数字无原始日志可回溯）；`preflight-blocker-matrix.md` 仍称“未执行”、Handoff AC 表仍 `NOT_RUN/BLOCKED`，与 head 的 931 全绿矛盾；`sln-test-results.md:3` 记录的命令仍非卡 `:58/:86` 冻结命令。行为本身已由本席位独立复跑证实（931/0/60），但**证据纪律不满足 AC7** | ①用冻结命令重跑实现侧测试，把**原始控制台日志（含 EXIT 与命令头）**入 `verification/FEA-04/`（基线侧同样补一条原始日志）；②更新 matrix 五行为“通过（931 运行）”并删掉“未执行”段；③Handoff AC 表改为实测结果；④`sln-test-results.md:3` 改回冻结命令（如保留 `--blame-hang` 需注明为附加开关） |
| R2-P2-01 | P2 | `baseline-comparison.md:17-28,32`；`doc/handoffs/FEA-04-68c72ba57.md:151` | 证据卫生：实现列表仍为 r1 的 930/412/419（head 931/413/420），`:32` 算术错误（419=403+17 不成立，应为 420）；`:17` 标题含 `0x0C` 控制字符导致 “feat” 渲染损坏；Handoff `:151` 遗留 1 个游离 CR（“eturn await”）。另：两次运行均无原始日志（并入 R2-P1-02） | 用 head 数据刷新实现列并改正算术；清除控制字符/游离 CR；补日志引用 |
| R2-P2-02 | P2 | `StudioPageViewModel.cs:1328-1335,1366-1374`；基线 `:1281` | **修复引入的失效语义**：基线 `RefreshRunProjectionAsync` 在 `RunSource` 未接线时把 `_runProjection` 置 `null`（每次 `LoadAsync` 清空）；新实现只刷新 band、不再清字段 → 换书/换章/换 run 后，Page 管线带会保留上一次 push 的投影，直到再次进入 Batch/点阶段触发 `SyncBatchAsync` | 在 `RefreshRunProjectionAsync`（或 `LoadAsync`）清空 `_runProjection`，或给缓存附带 runId/chapterId 并在读取时校验；补一步“load 后 band 不残留旧投影”用例 |
| R2-P2-03 | P2 | `StudioPageViewModel.cs:1366-1374,1328-1335`；`StudioExportViewModel.cs:437` | **Raise 覆盖不全**：`ApplyRunProjection` 不 Raise `nameof(RunProjection)`（且重复 Raise 三项已在 `RefreshPipelineBand` 内 Raise 的属性）；`RefreshRunProjectionAsync` 的 Raise 与字段写入分离。当前无 XAML 绑定、导出 overlay 打开即读，故未见可见回归；任何未来直接绑定 `RunProjection` 的消费者会拿不到推送通知（`NotifyRunProjectionChanged` 仍无调用者，基线即如此） | 在 `ApplyRunProjection` 末尾补 `Raise(nameof(RunProjection))`（去掉重复 Raise），push 后调用导出 overlay 的 `NotifyRunProjectionChanged()` 或改为属性通知 |
| R2-P2-04 | P2 | `FEA04CurrentAdapterTests.cs:376-393` | 回归用例名 “never drops it” 名不副实：只在一次 push 后立即 `Assert.Same`，未覆盖“之后 `LoadAsync`/`RefreshRunProjectionAsync` 是否仍保留/正确清除”的真实掉落路径（恰是 R2-P2-02 的风险点） | 在用例中追加：push → `await page.RefreshRunProjectionAsync()`/`LoadAsync`（不触发新 push）→ 断言按预期（保留或清除）并可区分两种语义；必要时拆成两个用例 |

**汇总（r2）**：P0 = 0；P1 = 2（R2-P1-01、R2-P1-02）；本轮新增 P2 = 4（R2-P2-01…04）；r1 遗留 P2 14 项 disposition 见 §2（接受遗留/并入 P1-01），不重复计数。**r1 已闭环：IMPL-02、IMPL-04、IMPL-17。**

---

## 7. 结论与复审

- **对 reviewed_head `ccca5ec59` 的判定：`changes_requested`（P0 = 0、P1 = 2）。** 不能写 `approved`：两项 P1 均为**文档/证据闭环缺失**，不是代码缺陷；代码侧 r1 的 P1 已全部实质解决（IMPL-02 closed、IMPL-04 closed、IMPL-03 的虚假陈述改正、IMPL-17 closed），本轮 build/test 全绿且可复现。
- **最小闭环路径（一次 docs/evidence 提交即可进入 r3）**：①补齐 Handoff「未迁出登记」并修正 S3/S5/AC 表 + `_runProjection` 入 AC3 清单（R2-P1-01）；②补两次运行的原始日志、更新 `preflight-blocker-matrix.md` 与 Handoff AC 表、命令恢复冻结形式（R2-P1-02）；③顺手修 R2-P2-01/02/03/04（可选，不阻断）。完成 ①② 后 P0/P1=0，可判 `approved`（届时 R-STATE-1 的 S3/S5 偏差作为已登记 deferral 由 DSH 集成侧承接）。
- **边界声明**：本报告只审 implementation 交付与 r1 处置，**不构成集成批准**，也不构成对方案/契约/范围的再批准；判定仅对 `8777b74f7..ccca5ec59` 有效。本席位未参与 FEA-04 的起草、实现或返修；未修改任何被审源码/文档（仅写本报告）；未 commit/push/merge；未切换 worktree checkout；未执行 UI/真机验证。基线复测未由本席位独立复跑（避免切换被审 worktree），以 DSH 实测表 + reflog + 严格差分一致性作为佐证并已在 §5 标注。所有行号基于 `ccca5ec59` 实测。
