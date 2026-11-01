---
task_id: FEA-04
review_id: FEA-04-r3
kind: implementation-review
reviewer: fea04-impl-reviewer
reviewer_kind: subagent
reviewer_source: DSH fresh 独立上下文派发（同一复核席位续审；未参与 FEA-04 的起草、实现或返修，只读被审 head）
base_commit: ccca5ec59
reviewed_head: af9625e7e
date: 2026-11-02
timezone: Asia/Shanghai
conclusion: approved
counts: { P0: 0, P1: 0, P2_new: 7, r1_P2_residual_accepted: 14 }
scope: 仅实现交付复核 r3（r2 findings disposition + 新 head 验证）；不构成集成批准
---

# FEA-04 实现复核 r3（r2 disposition + 新 head）

**结论：`approved`（P0 = 0、P1 = 0；本轮新发现/残留 P2 = 7，另 r1 遗留 P2 14 项维持“接受遗留”）**

**一句话理由**：r2 的 2 个 P1 均已实质闭合——Handoff `:162-171` 新增「未迁出登记」（S3/S5 逐项现状/原因/后续，`:171` 明确覆盖 Codex 段相反表述，满足 AC4），AC7 证据收口（`build-test-raw.log` 入库、matrix 状态更新、sln 命令恢复冻结形式、`git diff --check` rc=0）；r2 的 4 个 P2 中 2 个 closed（baseline 语义恢复、`ApplyRunProjection` Raise）、1 个 partial（baseline 证据仍含算术/控制字符瑕疵）、1 个接受遗留（用例命名）；本轮 head 的 build/test 由本席位独立复跑（**931/0/60**、0 failed，FEA-04 17/17），未引入新 P0/P1。剩余 7 项均为文档/证据卫生级 P2，不阻断。

## 审查基线

| 项 | 值 | 证据 |
|---|---|---|
| 主仓库 | `G:\CODEX\New Manga`（main；仅写本报告） | `git rev-parse --short HEAD` → `c6f9a2944`（未变） |
| worktree / 分支 | `G:\CODEX\New Manga.workspace\FEA-04` / `feat/fea-04` | `git rev-parse HEAD` → `af9625e7e376035d82496b630c0fe61663075e3f` |
| 被审 base / head | `ccca5ec59` / `af9625e7e` | `git log --oneline -2` → `af9625e7e`、`ccca5ec59` |
| 本轮 diff | 6 文件，+227 / −17（新增 `verification/FEA-04/build-test-raw.log`） | `git diff --stat ccca5ec59..af9625e7e` |
| 相对卡基线累计 | 40 文件，+2070 / −195 | `git diff --shortstat 68c72ba57..af9625e7e` |
| worktree 状态 | 审查/构建/测试前后 `git status --short` 均空 | `git status --porcelain` |
| 环境 | Windows；.NET SDK 10.0.401；`net9.0`；runsettings MaxCpuCount=1 | `dotnet --version` |
| 本轮执行 | `dotnet build`（restore 探测）+ 卡内 sln 测试复跑 + `git diff --check` + 证据逐文件字节核对；**未** checkout 其它 commit、未改源码/文档 | 见 §4/§5 |

**视角声明**：Architecture / Verification / Spec 均 executed；未执行：基线 commit 复测（沿用 r2 已核数据）、UI/真机、任何 commit/push/merge。

---

## 1. r2 findings 逐项 disposition（8 项）

| r2 ID | 级别 | r3 实测 | 处置 |
|---|---|---|---|
| **R2-P1-01** IMPL-01 未迁出登记缺失 | P1 | **HANDOFF 新增段已可见**：`git diff 8777b74f7..af9625e7e -- doc/handoffs/FEA-04-68c72ba57.md` 显示 AC1/AC2/AC7/AC8 行改写 + `:162-183` 新增三段；`handoff:166-169` 为「未迁出登记」表——S3 投影读取（现状=Batch 走 Host `IRunController.GetTaskProjectionAsync`、`_projection` 为 Batch 已应用投影；原因=接 ApplicationCore `RunMonitor` 会绕过 Host 投影契约并导致 16 个既有 Batch 用例失败；后续=FEA-05/FEA-07），intent key 注明已迁；S5 共享读取（`RunStatusMonitor` 保持 Host 轮询单例、Batch 自身 `DispatcherTimer`；原因=未接线到 ApplicationCore monitor、双 timer 属基线同构；后续=FEA-05）；`handoff:171` 明确“Codex 段相反表述以本登记为准”。AC4“未迁出项必须在 Handoff 明确登记（不得静默省略）”满足 | **CLOSED**（残留 P2：Codex 段 `:71/:73/:83/:84` 仍有旧表述，未 inline 改写，仅由 `:171` 覆盖——见 R3-P2-04；`_runProjection` 未进 AC3 清单） |
| **R2-P1-02** AC7 证据未收口 | P1 | `build-test-raw.log` 已入库（176 行：build 段 1-24 行、test 段 26-176 行，六工程 `已通过!` 行与 931/0/60 一致）；`preflight-blocker-matrix.md:7-11` 五行改为“已执行并通过（DSH r2 实测）”；`sln-test-results.md:3` 命令已恢复冻结形式（去 `--blame-hang`）；Handoff `:173-179` 新增证据清单；`git diff --check 68c72ba57..af9625e7e` → **rc=0**（本席位复验） | **CLOSED**（残留 P2：raw log 生成时点/参数与冻结命令不完全对应，matrix `:13/:21` 仍有“未执行”字样，AC3–AC6 行未更新——见 R3-P2-02/03/04） |
| R2-P2-01 baseline 证据陈旧/数字错误/控制字符 | P2 | 表已改 931/420（`baseline-comparison.md:27-28`）✔；但 **`:32` 仍写“App.Tests 419 = 基线 403 + 新增 17 项”**（403+17=420，且实现值已是 420）；**`:17` 标题仍含 `0x0C`**（字节 offset 758，渲染为“eat/fea-04”）；Handoff `:151` 仍有 1 个游离 CR（“改 \r eturn await” 文本损坏）。Lead 所述“控制字符检查为 0”**未被 head 证实** | **PARTIAL → 仍开放 P2（R3-P2-01/05）** |
| R2-P2-02 `RefreshRunProjectionAsync` 不清 `_runProjection` | P2 | **已恢复基线语义（逐段核对）**：head `StudioPageViewModel.cs:1328-1343` 与基线 `68c72ba57:...:1277-1290` 的 try/catch + `RunSource.IsWired ? await RunSource.GetProjectionAsync(_chapterId, …) : null` + `RefreshPipelineBand()` **一致**，并在 `:1342` 追加 `Raise(nameof(RunProjection))`；`LoadAsync`（`:879`）调用它 → `RunSource` 未接线时清空 push 缓存，不再残留旧投影 | **CLOSED** |
| R2-P2-03 `ApplyRunProjection` 未 Raise `RunProjection` | P2 | head `:1374-1381`：先 `_runProjection = projection`（`:1377`），再 `Raise(nameof(RunProjection))`（`:1378`），再 `RefreshPipelineBand()`；推送现在会通知 `RunProjection` 消费者 | **CLOSED** |
| R2-P2-04 用例名 “never drops” 名不副实 | P2 | 未改；该用例仍只覆盖“push→立即读取”（`FEA04CurrentAdapterTests.cs:376-393`），未覆盖随后 `LoadAsync/RefreshRunProjectionAsync` 的语义（现为基线语义：整页加载会清 `_runProjection` 并以 RunSource 结果覆盖）。行为本身已由 `V2StudioPageTests`/`LoadAsync` 路径与本席位复跑覆盖 | **P2 接受遗留（R3-P2-06）**：建议改名（如 `Page_pipeline_band_uses_the_batch_push`）或补“Load 后按基线语义重置”用例 |

**r2 遗留补充**：r1 的 14 项 P2（IMPL-05/06/07/08/09/10/11/12/13/14/15/18/19 除去已关的 17）在本轮无代码变更，**维持 r2 disposition（接受遗留，不重复计为新增）**。

## 2. 新 head 变更核查（派发 Q1/Q3/Q5）

- **范围**：本轮 6 文件全部在 `allowed_paths`（`ViewModels/V2/Studio/StudioPageViewModel.cs`、`doc/handoffs/FEA-04-*.md`、`verification/FEA-04/**` 含新增 `build-test-raw.log`）；**0 越界**；禁改面 0 命中（无 Host/Core/CoreClient、`*.sln`、`schema.py`、`doc/contracts/**`）。
- **AC1 不受影响**：源码仅 `RefreshRunProjectionAsync` 方法体（`async` 关键字恢复、与基线一致）与 `ApplyRunProjection` 追加一行 `Raise`；公开签名不变，无新增/删除公开成员（机械扫描仅命中既有方法的换写行）。
- **R2-P2-02/03 修复正确**：`RefreshRunProjectionAsync` 与基线的实现逐段一致（除多一行 `Raise`），`_chapterId` 在调用点前已赋值（`:841` → `:879`）；生产 `RunSource` 为 `NotWired` 时立即置 `null`、无 await 取消路径；`ApplyRunProjection` 覆盖写 + 通知正确。
- **未引入新问题**：push（`_runProjection`）与 `_current.GetRun(...)` fallback 的优先级未变（push 优先、monitor 兜底且生产无消费者）；`LoadAsync` 清 push 属基线语义，IMPL-02 回归用例仍通过；`RefreshPipelineBand` 中 `ApplyRunProjection` 的三处重复 Raise 是基线遗留（非新增）。
- **证据时点（重要发现）**：`build-test-raw.log` 的 mtime 为 `03:56:26`，**早于** 被审源码最后修改 `03:56:53`（`StudioPageViewModel.cs`）；且日志含 8 处“数据收集器‘Blame’消息”，说明该次测试仍带 Blame collector（`--blame-hang`），而 `sln-test-results.md:3` 记录的命令已不含该参数。即：该 raw log 是 r3 代码变更前（约 `ccca5ec59` 时点）的运行输出，且与记录命令不完全对应 → R3-P2-02（本席位已在 head 独立复跑，见 §4）。

## 3. 回归复跑（派发 Q4）

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| Build | `dotnet build apps/desktop-avalonia/NewManga.sln` | **EXIT=0；0 warnings / 0 errors**（3.7 s，含 App 重编译） | `%TEMP%\FEA04-r3-build.log` |
| sln 全量测试 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | **EXIT=0；931 passed / 0 failed / 60 skipped（991）** | `%TEMP%\FEA04-r3-test.log` |
| 逐工程 | 同上 | Host 51/0/28=79；ThemeEngine 235/0/0=235；DesignSystem 85/0/0=85；CoreClient 116/0/25=141；ApplicationCore 31/0/0=31；App **413/0/7=420** | 同上 |
| FEA-04 用例 | 同上过滤 | **17/17 passed**（含 `Page_pipeline_band_uses_the_batch_push_and_never_drops_it`） | 同上 |
| 格式 | `git diff --check 68c72ba57..af9625e7e` | **rc=0** | 本次会话输出 |
| 工作树 | `git status --short` | 空（构建产物被忽略） | 本次会话输出 |

与 DSH 声明一致（931/0/60、App 413/420、0 failed、EXIT=0、diff-check rc=0）；AC2 结论（各工程 passed ≥ 基线 914、failed=0、skipped 不变）在 head 复跑中成立。

## 4. 证据逐项核对

| 证据 | r3 核对 | 判定 |
|---|---|---|
| `handoff:162-171` 未迁出登记 | 表内 S3/S5 均有“现状/未迁出原因/后续”；`:171` 明确覆盖 Codex 段相反表述；与 head 实现一致（Host `GetTaskProjectionAsync` + `RunStatusMonitor` Host 轮询 + Batch `DispatcherTimer`） | **满足 AC4** |
| `handoff:93-100` AC 表 | AC1/AC2/AC7 = MET、AC8 = IN REVIEW；**AC3–AC6 仍 PARTIAL 且写“需要 build 可用后跑测试/执行验证未跑/测试未执行”**，与已跑通的 931/0/60 矛盾 | R3-P2-04 |
| `handoff:173-179` 证据清单 | 列出 baseline/sln/raw log/lifecycle/matrix/diff-check，与目录一致（`build-test-raw.log` 存在） | 满足；raw log 见 R3-P2-02 |
| `verification/FEA-04/build-test-raw.log` | 176 行、6 个 `已通过!` 行、0 失败；**无 build 命令头/EXIT 行/shell 头**；含 Blame collector 消息（与记录命令不符）；生成时点早于最终源码修改 | R3-P2-02 |
| `preflight-blocker-matrix.md:7-11,17` | 五行与副作用计数已改“已执行并通过（DSH r2 实测）” | 满足；但 `:13` Clear path 仍“未执行”、`:21` “当前限制”仍写“独立编译、测试结果与实现 Review 尚待……” | R3-P2-03 |
| `sln-test-results.md:3,6,16,18` | 命令已无 `--blame-hang`；931/0/60、App 413/420、baseline 914 行均正确 | 满足（命令与 raw log 参数不一致见 R3-P2-02） |
| `baseline-comparison.md` | 表已更新 931/420；`:32` 算术仍写 419；`:17` 仍含 `0x0C` 控制字符（标题“eat/fea-04”） | R3-P2-01 |
| `lifecycle-assertions.md` | 未变（r2 已按 head 修正“保持既有 Host 轮询”；`:3` 的 ReferenceEquals/Dispose 记录表述仍高估） | r1 IMPL-05 遗留维持接受 |
| Handoff 卫生 | `:151` 仍含 1 个游离 CR（“改 \r eturn await”），文件末尾无换行 | R3-P2-05 |
| Task 卡 / GOAL 指针 | `doc/tasks/FEA-04.md:14-19,140` 仍为旧值；`GOAL-PROGRESS-2026-11-02.md:3` 仍写 `55543c10d` | R3-P2-07（DSH 生命周期收口责任） |

## 5. Findings（r3：仅 P2，均不阻断）

| 编号 | 级别 | 位置（head `af9625e7e`） | 问题 | 建议 |
|---|---|---|---|---|
| R3-P2-01 | P2 | `verification/FEA-04/baseline-comparison.md:17,32` | 算术仍错（“App.Tests 419 = 基线 403 + 17”，实际 420）；`:17` 标题 `0x0C` 控制字符致 “feat” 渲染损坏 | 改为 420 并清除控制字符（重写该行为 “## 实现 head（`ccca5ec59`/`af9625e7e`）” 并注明实测口径） |
| R3-P2-02 | P2 | `verification/FEA-04/build-test-raw.log`（mtime 03:56:26 vs 源码 03:56:53）；`sln-test-results.md:3` | raw log 生成于最终源码变更前，且含 Blame collector 消息（说明实际带 `--blame-hang`，与记录的冻结命令不符）；无 build 命令头/EXIT/shell 头（Q-009 格式） | 在 head 用冻结命令重跑 `dotnet build` + `dotnet test`，把**带命令头与 EXIT** 的完整原始日志入库并删除/标注旧 log |
| R3-P2-03 | P2 | `verification/FEA-04/preflight-blocker-matrix.md:13,21` | Clear path 用例仍写“未执行”；“当前限制”仍称“独立编译、测试结果与实现 Review 尚待……” | 更新为已执行（App.Tests 413/420 含 FEA-04 17 项）并删除过期限制 |
| R3-P2-04 | P2 | `doc/handoffs/FEA-04-68c72ba57.md:71,73,83,84,95-98` | Codex 段 S3/S5/VM 审计旧表述未 inline 改写（仅 `:171` 覆盖）；AC3–AC6 仍写“未执行/执行验证未跑”，与 AC1/AC2/AC7 MET 自相矛盾 | inline 修正或加显式“见 :162 登记”指针；AC3–AC6 改按实测结果（AC3/AC5/AC6 可记 PARTIAL/MET 并引证据；AC4 指向 `:162`） |
| R3-P2-05 | P2 | `doc/handoffs/FEA-04-68c72ba57.md:151`（及文件尾） | 1 个游离 CR 造成“改 \r eturn await”文本损坏；文件末尾无换行（`git diff --check` 仍 rc=0，属卫生问题） | 删除游离 CR、补文件尾换行 |
| R3-P2-06 | P2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs:376-393` | “never drops it” 仍未覆盖随后 `LoadAsync/RefreshRunProjectionAsync` 的基线重置语义（用例只验证 push→立即读取） | 改名为 `…_uses_the_batch_push`，或补“Load 后按基线语义重置/不残留”用例（接受遗留亦可） |
| R3-P2-07 | P2 | `doc/tasks/FEA-04.md:14-19,140`；`doc/checkpoints/GOAL-PROGRESS-2026-11-02.md:3` | Task 卡 `branch/worktree/delivery_head` 未回填、Closeout 未记 r1–r3 disposition；GOAL 当前 HEAD 仍 `55543c10d` | 由 DSH 在集成/收口时更新（属生命周期责任，不属实现代码） |

**r1 遗留 P2（14 项）**：IMPL-05（AC6 断言机制缺 Dispose spy，lifecycle 文档仍高估）、IMPL-06（signals 公开绕过）、IMPL-07（S5 去重用例名）、IMPL-08（route TrimStart）、IMPL-09（清 Run 残留 `_projection`）、IMPL-10（死代码）、IMPL-11（debounce 30 天参数）、IMPL-12（S1 flush 语义）、IMPL-13（intent key 永久保留）、IMPL-14（memento 线程/事件）、IMPL-15（静态 Active）、IMPL-16（Handoff 旧表/AC3 清单/卡片指针同步——未迁出登记部分已随 R2-P1-01 关闭，其余以 R3-P2-04/07 跟踪）、IMPL-18（S4 锚点/滚动）、IMPL-19（S6 dirty≡unmapped）——**维持“接受遗留”，本轮无代码变更**；IMPL-17 已在 r2 关闭。

## 6. 结论与复审

- **对 reviewed_head `af9625e7e` 的判定：`approved`（P0 = 0、P1 = 0；本轮 P2 = 7，另 r1 遗留 P2 14 项维持接受）。** 依据：AC1–AC7 在 head 均有实测/证据支撑（本席位独立复跑 931/0/60、0 failed；diff-check rc=0；范围与禁改面 0 违规）；AC4 的 S3/S5 偏差已按卡允许的“未迁出登记”方式在 Handoff `:162-171` 明确登记（含原因与后续 FEA-05/07），满足 AC4 文义；AC8 由本报告关闭实现复核条件。
- **集成侧条件（非实现缺陷，需 DSH 承接）**：①在 Task Closeout / GOAL-PROGRESS 记录 S3/S5 的 R-STATE-1 deferral（本卡登记已给出，但权威指针需同步）；②R3-P2-02 建议在集成验证时用冻结命令重跑并把带命令头/EXIT 的原始日志入库（本报告的 head 复跑可作为过渡证据）；③其余 R3-P2-01/03/04/05/06 建议随收口一并修，不阻断。
- **边界声明**：本报告只审 implementation 交付与 r2 处置，**不构成集成批准**，也不构成对方案/契约/范围的再批准；`approved` 仅针对 `ccca5ec59..af9625e7e` 的实现内容，且不覆盖 A0/B 类未执行项（UI/真机/真实 sidecar）。本席位未参与 FEA-04 的起草、实现或返修；未修改任何被审源码/文档（仅写本报告）；未 commit/push/merge；未切换被审 worktree。所有行号基于 `af9625e7e` 实测；reviewer 复跑日志位于 `%TEMP%\FEA04-r3-build.log`、`%TEMP%\FEA04-r3-test.log`。
