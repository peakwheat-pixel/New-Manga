---
task_id: task-15
document_id: FEA-02-CORE-r1
kind: independent_review
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate task-15"
reviewer_independent: true
reviewed_by_implementer: false
author: codex（实现）；DSH 集成（Lead / Architect / Integrator）
base_commit: 2546410c4
reviewed_head: 5efb8f58c
reviewed_head_full: 5efb8f58c88e1acb11eaf53b1eab9135f26f29db
handoff_commit: 8166782cc
reviewed_head_note: "复核对象 = 固定实现提交 5efb8f58c（父 2546410c4）；交接提交 8166782cc 仅改文档（PLAN/STATUS/LEDGER/checkpoint/handoff/card），未改被测实现——已用 `git diff --name-status 5efb8f58c 8166782cc` 确认"
repository: G:/CODEX/New Manga（主仓库 HEAD 2546410c4 未被改动）
source_branch: feat/fea-02-core（worktree G:/CODEX/New Manga.workspace/FEA-02-CORE，HEAD 8166782cc，dirty=0）
scope: "FEA-02-CORE 实现交付：范围/AC1–AC7/L 判定/证据可复现/卡与 handoff 一致性；并在干净 TEMP 下独立复跑全量 solution 与基线对照，裁定那 3 项 Host 失败的根因与 AC5 口径"
decision: approved
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 4
independent_runs:
  delivery_5efb8f58c: "908 passed / 0 failed / 60 skipped（EXIT=0）"
  baseline_2546410c4: "883 passed / 0 failed / 60 skipped（EXIT=0）"
  application_core_only: "25 passed / 0 failed / 0 skipped（EXIT=0）"
  clean_env: "自建 `git archive` 快照于 G:/CODEX/New Manga.workspace/task-envs/c01b-reviewer/{new,base}，TEMP 指向私有目录"
checkps1: "主仓库默认：PASS（2 warnings，STATUS 2970 B），EXIT=0；worktree 内 `-TaskPath doc/tasks/FEA-02-CORE.md`：PASS（2 warnings），EXIT=0"
verifypins: "PASS (all 15)，EXIT=0；本次交付不触碰 14 份冻结契约 + FEA-01（pin 不变）"
ac5_ruling: >-
  AC5 可判 **MET**（干净环境口径）：新增 25/25 全绿、既有 883 项 outcome 零变化、结构断言（diff 不触 NewManga.App/**）成立。
  那 3 项 Host 失败经**两次独立干净环境全量复跑（DSH 883/0/60 与 908/0/60；我 883/0/60 与 908/0/60）**均不可复现 → **环境相关 flaky（Host junction 清理，共享/残留 TEMP）**，
  非本 Task 引入、非基线代码缺陷、**不阻塞 done**。但卡与 handoff 把其表述为「与基线相同/基线已有」→ 必须在集成收口时更正（P2-001 + 条件 C1）。
root_cause_3_failures: >-
  `NewManga.Host.Tests.TileChannelTests` 与 `D4SecurityHarnessTests` 各自在 `Path.GetTempPath()` 下建根目录、用 `cmd /c mklink /J` 建 junction，
  并在 `Dispose()` 里 `Directory.Delete(_root, recursive: true)`；失败时间戳（Host.Tests 0.52–0.70 s）落在清理阶段，符合共享/残留 TEMP 中 reparse point 删除被拒（UnauthorizedAccessException）。
  隔离运行 7/7 通过、干净环境全量 0 失败 → 不是断言失败，是清理阶段的环境敏感。
approval_conditions: >-
  C1（必须）：集成收口时更正 AC5 的归因表述 + 把 AC5/AC7 置 MET（写法见报告末节）；
  C2（必须）：done 时补 `canonical_evidence_status: complete` 与 `resource_closeout_status: complete`，并新增 DSH 自己的干净环境证据行；
  C3（建议）：把「Host 测试 junction 清理在共享 TEMP 下不稳」登记为独立 P2 债务（不属本 Task 范围）。
same_defect_check: >-
  无 P0/P1。P2-001 是**归因表述**问题（把环境 flaky 说成基线属性），方向上是"少报通过"（保守），
  没有把未执行/失败的内容标成通过；且可由集成收口一次更正，故不判 P1。
independence_note: >-
  本复核与被审产出为不同上下文（Codex 实现，DSH 派独立 reviewer）；我只读主仓库与 Codex worktree，未修改任何被审文件、未 commit、未 push；
  测试在自建临时快照里跑（不污染主仓库与 Codex worktree，跑完已清理）。
captured_at: 2026-11-01T20:19:21+08:00
captured_by: c01b-reviewer
---

# Review：FEA-02-CORE 实现（固定提交 5efb8f58c）

## 范围与依据

被审：`2546410c4`（release）→ **`5efb8f58c`**（实现，23 文件 / +12028 −0）→ `8166782cc`（handoff，仅文档）。

**依据**：Task 卡（分支 `in_review`）的范围/AC/L 判定；方案 §15.6 FEA-02-CORE 行；`FEA-01` 冻结（pin `0370c189…`）；`FEA-C11_IMPL_PREREQS.md` §0 禁则；handoff `doc/handoffs/FEA-02-CORE-5efb8f58c.md`；`check.ps1` 的 AC 标记与证据规则、`verify_pins.ps1`。

**先确认基本事实**：主仓库 HEAD = `2546410c4` 未变、`git status` clean；Codex worktree HEAD = `8166782cc`、`git status` clean（我未在 worktree 内跑任何写操作）。

## A. 范围与越界（AC 前置）

| # | 检查 | 实测 | 结论 |
|---|---|---|---|
| A1 | diff 是否全在允许写域 | `git diff --name-status 2546410c4 5efb8f58c` = 1 个 sln（M）+ ApplicationCore 源/测试（A）+ `verification/FEA-02-CORE/**`（A），共 23 文件 | **PASS** |
| A2 | sln 只新增两条项目条目 | 逐一读 diff：2 个 `Project(...) … EndProject` 块（`NewManga.ApplicationCore` / `.Tests`）+ 各 12 行配置 + 各 1 行 NestedProjects 映射；**既有项目与平台配置 0 改动** | **PASS** |
| A3 | 无 Current 接线 / 双调度 / 组合根改动 | 除 test 项目外无任何 csproj 引用 ApplicationCore（`Select-String … *.csproj -Pattern ApplicationCore` 只命中测试项目自身）；diff 不触 `NewManga.App/**`、`CoreClient/**`、`**/*.sln` 之外的项目文件 | **PASS** |
| A4 | 无 wire 码/错误映射（L-2）、无 schema/恢复（L-1/L-5） | 生产源码只 `using System.Collections.ObjectModel`（其余为 SDK 隐式 using）；关键字扫描 `TRASH_/RUN_*/allowedRunErrorCodes/SQLite/migration/schema/restore/backup/ServiceProvider` **0 命中**（2 处命中是注释文本） | **PASS** |
| A5 | 无代码外改动 | 无 `tests/**` 既有文件被改（只新增目录）、无 `.gitignore`/props/其它 Task/契约改动；worktree 内 `git diff --quiet 2546410c4 -- doc/plan` 由 `verify-boundaries.ps1` 断言并通过 | **PASS** |

## B. AC 逐条核对（含我自己的复跑）

| AC | 判据 | 我的实测/证据 | 结论 |
|---|---|---|---|
| **AC1** 无 Avalonia | 项目不引用 Avalonia（程序集/包/资产） | ①`dotnet list package` → 「[net9.0]: **未找到此框架的任何包**」；②构建产物目录 DLL 总数 = **1**（`NewManga.ApplicationCore.dll`），`Avalonia*` **0**；③`obj/project.assets.json` 的 `libraries` **为空**；④测试 `Assembly_has_no_presentation_transport_or_storage_dependency` 断言 `GetReferencedAssemblies()` 全为 `System*`（25/25 通过） | **MET** |
| **AC2** N 观察者一次轮询 | 32 观察者订阅同一 Run → 底层查询调用计数 = 1，观察者收到**同一快照实例**；下一 tick 才 +1 | `Many_observers_share_one_query_and_the_same_snapshot_then_one_next_tick`：`calls==1`、`Assert.Same(refreshes[0], task)`、`Assert.Same(value, observations[0].Snapshot!.Value)`、`Assert.Same(result, observations[0].Request)`、`Assert.Same(observations[0].Snapshot, State.GetSnapshot("run-a"))`、`Advance(Interval)` 后 `calls==2` 且 `Version==2` → **非空转**（断言了调用次数与实例同一性） | **MET** |
| **AC3** 同意图重试不重复启动 | 64 并发同 key → 1 次启动、共享同一 Task/结果；完成后允许新意图且 RequestId 不同；超时释放 flight、迟到回复不污染下一个意图 | `Concurrent_retries_of_pending_intent_share_one_start_task_and_result`（`calls==1`、`Assert.Same(pending[0], task)`、新意图 `calls==2`、`RequestId` 不同）、`Completed_flight_is_released_but_original_key_is_forwarded_…`、`Shared_timeout_releases_flight_and_late_reply_does_not_complete_next_intent`（超时后同一 flight 返回同一结果；`late.SetResult(1)` 后下一次意图仍 `99`）、`Cancelling_one_waiter_does_not_cancel_shared_start_or_other_waiter` | **MET** |
| **AC4** 请求错误互不串扰 | 并发请求其一失败（含超时/取消）→ 错误只属该请求；其它请求结果/状态不受影响；失败不覆盖最后一次成功快照 | `Concurrent_fault_is_request_local_and_does_not_replace_success`、`Precancelled_request_does_not_invoke_adapter`、`Cancellation_finishes_even_if_adapter_ignores_token_and_late_fault_is_isolated`、`Timeout_uses_injected_clock_and_cancels_only_its_operation`、`Concurrent_success_retains_its_result_when_another_request_fails`（Faulted/Cancelled/TimedOut 三组 Theory）、`Failure_keeps_last_success_and_does_not_contaminate_another_run`、`Timeout_or_cancellation_does_not_replace_a_successful_snapshot` | **MET** |
| **AC5** Current 非回归 | ①基线非回归 ②结构断言 ③无双调度（接线后验） | ①**我独立复跑**：base `2546410c4` = **883 passed / 0 failed / 60 skipped**（EXIT=0）；delivery `5efb8f58c` = **908 passed / 0 failed / 60 skipped**（EXIT=0）；差值恰为新增 25 项 → **既有 883 项 outcome 零变化**；Current `App.Tests` 396/7 与基线一致。②结构：本卡 diff 对 `NewManga.App/**` **0 命中**。③按设计不接线 | **MET（干净环境口径）**——见 P2-001 的表述更正要求 |
| **AC6** L-1/L-2/L-5 判 N/A 仍成立 | 结合实现实际 import/依赖 | 生产代码无 DB/schema/wire/恢复相关引用（见 A4）；实现只做内存状态、轮询合并、意图去重、请求级结果；卡内三项 N/A 与再触发条件未被本实现触发 | **MET** |
| **AC7** 独立复核 | 报告判 approved（P0/P1=0） | 本报告 `doc/reviews/FEA-02-CORE-r1.md` | **MET**（由本报告成立） |

**测试质量抽查（是否"空转通过"）**：抽查 25 项中 12 项的断言体——全部断言**可观察计数/实例同一性/错误归属/代际守卫**（如 `calls==1`、`Assert.Same`、`Assert.NotEqual(RequestId)`、`Assert.False(channel.Reader.TryRead(out _))`），且有负向对照（`Precancelled_request_does_not_invoke_adapter`、`Different_intents_have_independent_failures_…`）；使用 `ManualTimeProvider` 注入虚拟时钟，不依赖真实 sleep。**未发现空转断言**。

## C. 全量测试与那 3 项 Host 失败的根因裁定

**1) 我的独立复跑（干净快照 + 私有 TEMP）**

| 对象 | 命令 | 结果 |
|---|---|---|
| ApplicationCore.Tests | `dotnet test …/NewManga.ApplicationCore.Tests.csproj --no-build` | **25 passed / 0 failed / 0 skipped**，EXIT=0 |
| delivery 全量 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build`（5efb8f58c 快照） | **908 passed / 0 failed / 60 skipped**，EXIT=0（Host.Tests 51/0/28、App 396/0/7、CoreClient 116/0/25、ThemeEngine 235/0/0、DesignSystem 85/0/0、ApplicationCore 25/0/0） |
| baseline 全量 | 同上（2546410c4 快照） | **883 passed / 0 failed / 60 skipped**，EXIT=0（Host.Tests **51/0/28**、App 396/7、CoreClient 116/25、ThemeEngine 235、DesignSystem 85） |

→ 与我拿到 DSH 的对照一致（DSH：base 883/0/60、delivery 908/0/60）。**Codex 报的 905/3/60 与 880/3/60 在其环境内自洽（差额都是那 3 项），但在干净环境不可复现。**

**2) 根因判定：环境相关 flaky（Host junction 清理），非本 Task 引入、非基线代码缺陷**

- 失败项固定为 `NewManga.Host.Tests.TileChannelTests.Containment_OutsideRoot_And_Junction_Rejected`、`D4SecurityHarnessTests.D4_3_Escape_RejectedAtReadTime_AfterPathReplacement`、`D4SecurityHarnessTests.D4_3_Escape_RejectedAtIssue`。
- 源码事实：两个测试类都在 `Path.GetTempPath()` 下建根目录、用 `cmd.exe /c mklink /J` 建 junction，`Dispose()` 里 `Directory.Delete(_root, recursive: true)`；Codex 日志里失败出现在 **Host.Tests 启动后 0.5–0.7 s**（清理阶段），与"reparse point 被占用/被拒删除（UnauthorizedAccessException）"一致，而不是断言失败。
- 对照链：①Codex 环境内 **基线** 也失败同样 3 项（其 `baseline-standard-test.log` 我抽验 sha 与卡一致）；②只跑这 3 项（过滤）→ 7/0 通过；③两个独立干净环境全量 → 基线 0 失败、交付 0 失败。**三者合并只能得出"环境（共享 TEMP/残留 junction/并发）敏感"**。
- 归属：与本 Task 改动无因果（新项目零依赖、不触 Host/App）；也**不能**表述为"基线稳定失败"。

**3) 是否阻塞 done**：**不阻塞**。AC5 的实质要求是"Current 非回归 + 无接线/双调度"，在干净环境下已被证明（883→908 只多 25 项、0 失败）；那 3 项属既有 Host 测试的环境敏感，应登记为**已知环境限制**，而非本 Task 债务。

## D. 证据可复现性与治理

| # | 检查 | 结果 |
|---|---|---|
| D1 | 证据 sha256 抽验（5 条） | **PASS**：`README.md` `96a0663f…`、`test-summary.json` `5cbbb116…`、`boundaries.log` `0aaa1a39…`、`final-test.log` `b04fbe7e…`、`baseline-standard-test.log` `188843c9…` 全部与工作区实测一致 |
| D2 | `test-summary.json` 自洽 | **PASS（数字）**：各项目合计 905/3/60 与其 `delivery` 字段一致；`limitation` 明写"全量未通过 + Dispose 失败 + 未改/未排除既有测试"；60 个 skip 逐项带原因。**但 `changed_existing_test_outcomes` 为空值**（P2-002） |
| D3 | `verify-boundaries.ps1` 是否真能挡越界 | **PASS（实质）**：保护 `NewManga.App`/`CoreClient`/`src`/`contracts` 与**既有测试**；机械剥离两条新项目行后与基线 sln 做 `-cne` 全等比较；断言 ApplicationCore 无 ProjectReference/PackageReference、无其它 csproj 引用；最后逐条比对 changed+untracked 路径在授权前缀内（依赖 `rg`，P2-004） |
| D4 | 治理命令 | **PASS**：主仓库 `check.ps1` PASS(2w，STATUS 2970 B)/EXIT=0；worktree 内 `check.ps1 -TaskPath doc/tasks/FEA-02-CORE.md` PASS(2w)/EXIT=0；`verify_pins.ps1` **15/15**/EXIT=0（无冻结契约改动 → 无需 UNFREEZE） |
| D5 | 卡与 handoff 一致性 / 无"未执行标通过" | **PASS（诚实）**：卡 `in_review`、AC1–AC4/AC6 `<<MET>>`（有 25/25 与 build 证据）、AC5 `[ ] <<PARTIAL: …>>`、AC7 `[ ] <<BLOCKED: 待 DSH 安排复核>>`；handoff §"未满足项与风险"明写"未 approved、未集成、未 done"。**未见把未执行内容标通过**。唯一问题是 AC5 的**归因表述**（P2-001） |

## Findings

| ID | 级别 | 位置 | 问题 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| FEA02-P2-001 | **P2（非阻断；集成收口必须更正）** | 分支卡 `:55`（AC5 理由）、`:124`（Closeout）、handoff `:12`/`:39`/`:59`/`:73`；证据表 `BASE-TEST` 行说明 | 把 3 项 Host 失败表述为「**与基线相同**」「全 solution 仍 FAIL（**同基线 3 项**）」→ 会被读成"基线本来就有 3 项失败"。经两次独立干净环境全量（DSH 883/0/60 与我 883/0/60；交付 908/0/60 与 908/0/60）证明：**基线在干净环境 0 失败**，该 3 项是环境敏感 flaky。这会形成"基线不稳"的错误共识，未来可能掩盖真回归 | 本报告 C 节；codex `baseline-standard-test.log` 3 条 FAIL；我的 base 全量 0 失败 | 集成收口时：①卡 AC5 改 `[x] <<MET>>`（无 reason）+ 重写理由为"干净 TEMP：908/0/60；基线 883/0/60；结构断言 0 命中；本卡不接线"；②Closeout 加一条更正：「3 项 Host 失败 = 环境相关 flaky（junction 清理），干净环境不可复现，非基线缺陷、非本 Task 引入」；③`BASE-TEST` 行说明改为「同一环境下的失败；干净环境 0 失败（见 BASE-CLEAN）」。**handoff 原字节建议保留**（作为当时环境快照），由卡/checkpoint 承接更正 | open |
| FEA02-P2-002 | P2（非阻断） | `verification/FEA-02-CORE/test-summary.json` | `changed_existing_test_outcomes` 为空值——该字段本意是"既有测试 outcome 变化"，但未给出 943 项对照结论（handoff `:58` 说"outcome 变化 0"）；且其 `baseline` 字段反映的是**污染环境**结果 | D2 | done 时由 DSH 用自己干净环境的 TRX 补 `BASE-CLEAN`/`DELIVERY-CLEAN` 两条证据，并把该字段填成"0 变化（干净环境全量对照，见两行证据）" | open |
| FEA02-P2-003 | P2（非阻断） | `verification/FEA-02-CORE/test-summary.json`（10,223 行） | 单文件嵌入全部逐项 outcome，体积大、难审计；TRX 只保留在 workspace（`build/FEA-02-CORE/**`），未入库 | 文件行数 | 后续 Task 建议：JSON 只写汇总 + 失败/skip 清单，TRX 作为独立证据入库或列 SOURCE_PIN；本次不阻塞 | open |
| FEA02-P2-004 | P2（非阻断） | `verification/FEA-02-CORE/verify-boundaries.ps1:37` | 依赖 `rg`（ripgrep）；缺失时虽因 `$ErrorActionPreference='Stop'` 会显式失败（不会静默放行），但边界门禁无法在无 rg 的机器上复核 | 脚本原文 | 建议改为 `Select-String` 或加 `Get-Command rg` 的前置检查与明确报错 | open |

**P0：0。P1：0。** 4 条 P2 非阻断。

## 结论

**decision：`approved`**（P0 × 0 / P1 × 0 / P2 × 4，均非阻断，其中 P2-001 需在集成收口时更正表述）。

- **范围**：23 文件全部在授权写域；sln 仅两条项目条目 + 其自有配置/嵌套行；主仓库 HEAD 未变；无接线、无双调度、无组合根、无 wire 码/映射搬入、无 schema/恢复逻辑。
- **AC1–AC4、AC6**：**MET**，实测证据充分（AC1 为"零包依赖 + 产物仅自身 dll + 资产 libraries 空 + 程序集引用断言"四重证据）。
- **AC5**：**MET（干净环境口径）**——新增 25/25 全绿、既有 883 项零变化、结构断言成立；3 项 Host 失败为环境相关 flaky，不阻塞。
- **AC7**：本报告成立 → 可置 MET。
- 治理：两路 `check.ps1` PASS、`verify_pins.ps1` 15/15、无需 UNFREEZE。

### DSH 集成收口精确步骤（含 AC5 写法）

1. **在分支 `feat/fea-02-core`（worktree）内改卡**，一次提交：
   - AC5 → `- [x] **AC5 保留 Current 入口（非回归）**：… <<MET>>`（**MET 不得附 reason**，checker 会报错）；理由移入 Closeout 或脚注。
   - AC7 → `- [x] **AC7 独立复核**：`doc/reviews/FEA-02-CORE-r1.md` 判 `approved`（P0/P1 = 0）。 <<MET>>`。
   - Closeout 追加三条：①「复跑证据：干净 TEMP 下交付 908/0/60、基线 883/0/60（命令：`dotnet test apps/desktop-avalonia/NewManga.sln --no-build`，TEMP 指向私有空目录）；②「3 项 Host 失败 = 环境相关 flaky（junction 清理），干净环境不可复现，**非基线缺陷、非本 Task 引入**」；③「集成：`integration_commit: <合并提交>`、`delivery_head: 5efb8f58c`」。
   - Canonical Evidence **新增 3 行**（sha 用最终字节）：
     `DELIVERY-CLEAN | AC5 | verification/FEA-02-CORE/delivery-clean-env-test.log | <integration> | <sha256> | CANONICAL`
     `BASE-CLEAN | AC5 | verification/FEA-02-CORE/baseline-clean-env-test.log | 2546410c4 | <sha256> | CANONICAL`
     `REVIEW-R1 | AC7 | doc/reviews/FEA-02-CORE-r1.md | - | <sha256> | CANONICAL`
     （把 DSH 自己两次干净环境跑的输出落成这两个 log；注意 TEMP 前置条件写进 README/卡）
   - `canonical_evidence_status: complete`；`resource_closeout_status: complete`（Manifest 现有 6 行 disposition 合法：worktree/build/agent-output `PRESERVE_REFERENCED`、task-env/bin-obj `PRESERVE_UNKNOWN`（destination 均存在）、user-data `NOT_APPLICABLE`；**不要删这些目录**，或按 Workspace Governance 另行裁决）。
2. **合并到主仓库**：`git -C "G:/CODEX/New Manga" merge --no-ff feat/fea-02-core`（或 cherry-pick `5efb8f58c`+卡提交）→ 用合并提交 sha 作 `integration_commit`；`delivery_head: 5efb8f58c`。
3. **主仓库元数据提交**：卡 `status: done`；PLAN（FEA-02-CORE → done，移除 READY 节点或写入下一个候选）；STATUS `:7`/`:11`；checkpoint 队列加一行；`python tools/governance/task_ledger.py --write`。
4. **自检**：`check.ps1`（默认 + `-TaskPath doc/tasks/FEA-02-CORE.md`）PASS；`verify_pins.ps1` **15/15**；主仓库 `git status` clean。
5. **不需要补测试、不需要 UNFREEZE**（未触碰任何冻结契约字节；本次交付 `doc/plan/` diff 为空）。
6. **建议另立 P2 债务**（可选）：「Host 测试 junction 清理在共享/残留 TEMP 下不稳定（`Directory.Delete` 对 reparse point 抛 UnauthorizedAccessException）」——它会让全量测试结果反复被污染；属既有 Host 测试的健壮性改进，**不属 FEA-02-CORE 范围**，登记即可。
7. **注意 STATUS 预算**：主仓库 STATUS 现 2970/3200 B（余 230 B），本次 done 收口改 `:7`/`:11` 需注意不要撞 3200。

—— 报告结束（`decision: approved`；AC1–AC4/AC6 MET、AC5 MET（干净环境）、AC7 成立；3 项 Host 失败裁定为环境相关 flaky，不阻塞 done；P2×4 非阻断）。
