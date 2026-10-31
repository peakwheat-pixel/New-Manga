---
document_id: REALUSE-DATA-SAFETY-9-review
kind: independent_review
task_id: REALUSE-DATA-SAFETY-9
reviewer: safety9-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context task-7（独立上下文子 agent，未参与实现、返修或证据撰写）"
reviewer_independent: true
author: dsh-lead
base_commit: 5b888cd70
reviewed_head: 40d286e8506b9c7ee66bd2107d2641bc33bf27e6
delivery_head: dcce29a13
verdict: approved
p0: 0
p1: 0
p2: 1
captured_at: 2026-11-01T02:27:00+08:00
---

# Review：REALUSE-DATA-SAFETY-9（上下文独立审查）

> 本报告只对 `base_commit = 5b888cd70`、`reviewed_head = 40d286e85`（分支 `task/REALUSE-DATA-SAFETY-9`，worktree `G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-9`）有效。审查者只读该 head；**仓库内唯一写入即本文件**。负向对照与全部复跑均在仓外副本 `G:\CODEX\New Manga.workspace\tmp\safety9-review\` 执行，仓库内未做 `checkout`/`stash`/`apply`/`commit`/`push`，生产源码零改动。

## 1. 结论

**verdict: approved。** P0 = 0，P1 = 0，P2 = 1。

- **AC1（R-002 判别性断言）MET**：新增的 `Assert.Equal(3, library.Reader.PageIndex)` **真正判别 F-005 门禁**。仓外副本把生产文件换成 `bb7cbda1d` 的 pre-F-005 版本（blob `5333b66b5`，`_isClosing` 出现 0 次）后，该用例 **FAIL / EXIT=1**，失败点正是新增断言 `LibraryProgressRefreshTests.cs:328`（`Expected: 3 / Actual: 5`）；交付版 **PASS / EXIT=0**，恢复交付版后再次 PASS。
- **AC1 附带（角色标注）准确**：`verification/REALUSE-DATA-SAFETY-8/ac3-closing-gate.md:43-45` 把 `PageIndex` 断言标为**判别性断言**、把 `ReaderLoadCount == loadsBefore + 1` / `IsOpen == false` / `LastSaveResult == Saved` 标为**回归栅栏断言**，与实测行为一致（后三条在 pre-F-005 上同样成立）。
- **AC2（R-003 措辞修正）MET**：`verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md:72-75` 不再含"未发生事件"的断言，只记录已发生的两份 Review 结论，且引用路径与 commit（`2a0528851`、`5bea0ce4b`）真实可查、均为 `reviewed_head` 的祖先。
- **回归复跑全部吻合预期**：build `0 警告 / 0 错误 EXIT=0`；filtered `7/7 EXIT=0`；全量 `396 通过 / 0 失败 / 7 跳过 = 403 EXIT=0`；`check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-9.md` → `PASS (3 warnings) EXIT=0`。
- **数据安全**：分支相对 base 的 `apps/desktop-avalonia/src/**` diff 为空（本 Task 只改测试 + 证据/文档）；无用户数据访问；未 push（无 remote-tracking ref）。

唯一的 P2 是**负向对照证据的记录精度**（`ac1-discriminating.md` 是精简转录，缺执行位置/命令/断言失败明细），不改变 AC1 的成立，本 Review 已独立复现其实质结论，故不阻断批准。

## 2. 被审对象与事实

| 事项 | 事实 |
|---|---|
| 分支 / HEAD | `task/REALUSE-DATA-SAFETY-9` / `40d286e8506b9c7ee66bd2107d2641bc33bf27e6` |
| 提交 | `dcce29a13`（测试 + 证据措辞）、`407d3b1d8`（证据 pin + resource manifest）、`40d286e85`（manifest pin 登记） |
| `dcce29a13 --stat` | `LibraryProgressRefreshTests.cs` +14/-2；`doc/REBASELINE_PLAN.md`、`doc/tasks/REALUSE-DATA-SAFETY-9.md`、`verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md`、`verification/REALUSE-DATA-SAFETY-8/ac3-closing-gate.md`、`verification/REALUSE-DATA-SAFETY-9/{README,ac1-discriminating,ac1-fix-tests,ac2-wording}`；**无生产源码** |
| `git diff --stat 5b888cd70..40d286e85 -- apps/desktop-avalonia/src` | 空 → 生产代码零改动 |
| 工作树 | `git status --porcelain` 无输出（审查前后均干净） |
| 生产文件 blob | `40d286e85:…/ReaderOverlayViewModel.cs` = `98451f079c951ad035817b0958ef867875c7c238`；工作树 sha256 `665d653c…8955`（含 `_isClosing` 6 次） |
| pre-F-005 目标 | `bb7cbda1d:…/ReaderOverlayViewModel.cs` = `5333b66b5312ba2d3195b5307774e0b8a4c945fb`（与 SAFETY-8 Review 记录的 `60056d353^` blob 一致） |
| 测试文件关键行 | `LibraryProgressRefreshTests.cs:320`（首次导航后的 PageIndex 健全性断言）、`:328`（close 窗口内判别性断言）、`:330`（`gate.SetResult(true)` 释放前） |

## 3. AC1（R-002）：判别性断言 —— MET

### 3.1 断言位置与 async 语义（不依赖时序侥幸）

`GoToAsync` 是 `async Task` 方法，调用方在方法**返回 Task 之前**就会执行其同步段（第一个未完成的 `await` 之前）。

- 交付版（`ReaderOverlayViewModel.cs:334-352`）：`if (_isClosing || Pages.Count == 0) { return; }` 位于**第一个 `await` 之前**（首个 `await` 在 `:350`）。close 窗口内 `_isClosing == true`，`PageIndex` 完全不被写入，保持 3。
- pre-F-005（`bb7cbda1d` 版本）：`GoToAsync` 无 `_isClosing` 判据，`PageIndex = clamped` 同样在第一个 `await` 之前同步执行，`PageIndex` 变为 5。

因此 `GoToAsync(5)` 返回后读取 `PageIndex` 的结果在两种代码下都是**确定的同步结果**，与 `LoadCurrentImageAsync` / `SaveProgressAsync` 是否同步完成、线程池调度、gate 何时释放均无关：`SaveGate` 只控制**首个保存在 Host 内**的恢复时刻，判别性断言发生在 gate 释放（`:330`）之前，不受其影响。

断言放置位置正确：`CloseAsync()`（`:322`，同步段置 `_isClosing = true` 后停在等待在途保存）→ `GoToAsync(5)`（`:325`）→ `Assert.Equal(3, PageIndex)`（`:328`）→ `gate.SetResult(true)`（`:330`）。即断言确在 **close 窗口内、gate 释放前**。`:320` 的健全性断言（首次导航后 `PageIndex == 3`）不引入额外时序依赖。

### 3.2 负向对照（仓外副本，本 Review 独立复现）

方法：`robocopy` 复制 `apps/desktop-avalonia`（排除 `bin/obj/.vs`）+ `doc/design/redesign-v1/40-fusion/tokens.json` 到 `G:\CODEX\New Manga.workspace\tmp\safety9-review\negctl`；用 `git -C <worktree> cat-file blob bb7cbda1d:<path>` 取**原始 blob 字节**覆盖副本生产文件（`hash-object --no-filters` = `5333b66b5`，`rev-parse` 一致；`_isClosing` 出现 **0** 次）。两次覆盖后的构建均加 `--no-incremental`，排除"文件 mtime 旧于输出 DLL 导致增量构建跳过重编译"的伪结果。

| 步骤 | 生产文件 | 构建 | filtered 用例结果 |
|---|---|---|---|
| 1 交付版（基准） | 交付字节（`_isClosing`×6） | `0 警告 / 0 错误 EXIT=0` | **通过 1 / 失败 0，EXIT=0** |
| 2 pre-F-005 | `5333b66b5`（`_isClosing`×0） | `0 警告 / 0 错误 EXIT=0` | **失败 1 / 通过 0，EXIT=1** |
| 3 恢复交付版 | 交付字节（`_isClosing`×6） | `0 警告 / 0 错误 EXIT=0` | **通过 1 / 失败 0，EXIT=0** |

步骤 2 的失败明细（证明失败来自**新增判别性断言**而非其它断言）：

```
[xUnit.net]  ...ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread [FAIL]
   Assert.Equal() Failure: Values differ
   Expected: 3
   Actual:   5
   at ...LibraryProgressRefreshTests.cs:line 328
测试运行失败。 测试总数: 1  失败数: 1
TEST-PRE-F005 EXIT=1
```

结论：`Assert.Equal(3, library.Reader.PageIndex)` 在旧代码（`bb7cbda1d`）上失败、在交付版上通过 → **判别性成立**；断言不依赖时序侥幸（§3.1 的同步段论证 + 实测失败点固定在 `:328`、`Actual: 5`）。

> 复现备注：第一次尝试时用 `Copy-Item` 恢复交付文件后未强制重建，因复制保留了旧 mtime 导致 MSBuild 复用 pre-F-005 的 DLL，出现一次"交付版假失败"；改为 `--no-incremental` 后三种状态结果稳定。这属复现手法问题，不是被审对象缺陷。

### 3.3 `ac3-closing-gate.md` 角色标注（AC1 附带）—— 准确

`verification/REALUSE-DATA-SAFETY-8/ac3-closing-gate.md:43-45`：

- 把 `PageIndex` 保持 3 标为 **判别性断言（R-002 补强）**，并声明"该断言在旧代码上失败"，指向 `verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md`；
- 把 `ReaderLoadCount == loadsBefore + 1`、`IsOpen == false`、`LastSaveResult == Saved` 标为 **回归栅栏断言**。

这与实测一致：后三条在 pre-F-005 上同样成立（SAFETY-8 Review 已实测，本 Review 的 pre-F-005 运行也只在 `:328` 失败），所以它们确实只是回归栅栏；标注按"断言粒度"而非"用例粒度"给出，比把整条用例笼统称为判别性或回归栅栏更精确，不构成过度声明。用例注释（`LibraryProgressRefreshTests.cs:299-307`）与 `ac1-discriminating.md:30` 的角色说明一致。

## 4. AC2（R-003）：证据措辞 —— MET

`verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md:72-75` 现文：

> SAFETY-7 的独立 Review 已按此方式复核并全部一致（SAFETY-6 12/12、SAFETY-7 10/10，见 `doc/reviews/REALUSE-DATA-SAFETY-7-review.md`）；SAFETY-8 的独立 Review 也已按同一方式复核（12/12 一致、变化恰为 5 条，见 `doc/reviews/REALUSE-DATA-SAFETY-8-review.md`）。本段只记录**已发生**的审查结论；任何新 Review 的结论须在其报告落盘后再回填。

逐项核对：

| 检查项 | 结果 |
|---|---|
| 是否仍有"未发生事件"的断言 | **无**。两处均指向已落盘报告；末句是回填规则而非事件断言 |
| 引用路径真实 | `doc/reviews/REALUSE-DATA-SAFETY-7-review.md`、`doc/reviews/REALUSE-DATA-SAFETY-8-review.md` 均在 `reviewed_head` 树内 |
| 引用 commit 真实 | `2a0528851`（SAFETY-7 Review 入库）、`5bea0ce4b`（SAFETY-8 Review 入库）`git cat-file -t` → `commit`；均 `git merge-base --is-ancestor … 40d286e85` = 0（祖先） |
| 引述结论是否与报告一致 | SAFETY-7 Review `:27`：「SAFETY-6 12/12 条 pin 与对应 commit 的 blob 一致、SAFETY-7 10/10 条 pin 一致」；SAFETY-8 Review `:61`/`:82-88`：「新 pin 12/12 与 blob SHA-256 一致；实际变化恰为 5 条」「SAFETY-8 卡自身 10 条：10/10 全部一致」→ 引述准确 |

R-003 的两种修复路径（"改为可供独立 Review 复核"或"复审后回填结论"）中，本 Task 选择了后者且只回填已发生的事实，符合 SAFETY-8 Review `:43` 的建议。

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-101 | P2 | `verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md:34-47` | **负向对照证据是精简转录，缺可核性要素。** `:34` 写"用 `bb7cbda1d` 的 pre-F-005 生产文件覆盖工作树"——未说明是**仓外副本**还是仓内工作树原地覆盖（Task 禁止范围明确"不改生产代码"，若按字面理解为仓内覆盖则与禁止范围冲突，尽管交付 head 无残留）；`:36-40` 只有 `[xUnit.net] … [FAIL]` 与 `失败!/EXIT=1` 三行，**无** shell/host 头、命令与 cwd、**无断言失败明细**（`Expected: 3 / Actual: 5`、失败行 `:328`），也未记录恢复方式。后果：仅凭该证据无法判断失败来自新增的判别性断言（`:328`）还是 `:320` 那条同为 `Expected: 3` 的健全性断言，也不符合仓库既有的 Q-009 证据纪律（运行日志须带 EXIT 与 shell/venv 头、可复现命令）。实质结论已由本 Review 在仓外独立复现（失败点确为 `:328`、`Actual: 5`），故不改变 AC1 的成立 | 本 Review 在 `tmp/safety9-review/negctl` 复现：交付版 `1/0 PASS EXIT=0` → pre-F-005 `0/1 FAIL EXIT=1`（`Expected: 3 / Actual: 5`，栈顶 `LibraryProgressRefreshTests.cs:line 328`）→ 恢复后 `1/0 PASS EXIT=0`（见 §3.2） | 在证据中补齐：执行位置（仓外副本路径）、取字节命令 `git cat-file blob 5333b66b5`、`dotnet build/test` 与 cwd、失败输出原文（含断言明细与行号）、恢复方式（字节还原而非 `git checkout`） | open |

**P0 / P1：无。**

## 6. 验证（实际执行与结果）

环境：worktree `G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-9`，`dotnet 10.0.401`（SDK），目标框架 `net9.0`，`pwsh 7.6.8`，Windows；构建/测试 cwd = `…/apps/desktop-avalonia`。日志原文：`tmp/safety9-review/regression.log`、`negctl-forced.log`。

| 场景 | 命令 | 结果 | EXIT |
|---|---|---|---|
| 构建 | `dotnet build NewManga.sln -v q --nologo` | 已成功生成；**0 个警告 / 0 个错误**（3.90s） | **0** |
| filtered | `dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q --filter "FullyQualifiedName~LibraryProgressRefreshTests"` | 已通过：失败 0 / **通过 7** / 跳过 0，总计 7（89 ms） | **0** |
| 全量 | `dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q` | 已通过：失败 0 / **通过 396** / **跳过 7** / 总计 **403**（56 s） | **0** |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-9.md` | **Governance check: PASS (3 warnings)**（7 个非终态 Task；`doc/STATUS.md` 80% 预算 2989B/31 行；`doc/REBASELINE_PLAN.md` 80% 预算 6632B/63 行——与 SAFETY-8 Review `:103` 记录的同类 warning 一致） | **0** |
| 跨任务回归 | `check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-7.md` | PASS (4 warnings，新增 1 条为既有 worktree 同源解释) | **0** |
| 跨任务回归 | `check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-8.md` | PASS (4 warnings) | **0** |
| 证据 pin 复核 | 对卡内 8 条 pin 逐条 `git cat-file blob <commit>:<path>` → SHA-256 | **8/8 MATCH**（`E-AC1-TEST`、`E-AC1-DOC`、`E-AC1-LOG`、`E-AC2-DOC`、`E-AC2-PIN-DOC`、`E-AC1-GATE-DOC`、`E-EVIDENCE-INDEX`@`dcce29a13`；`E-RESOURCE-MANIFEST`@`407d3b1d8`） | — |
| 负向对照 | 仓外副本 + `--no-incremental`（三步互换） | 交付 PASS / pre-F-005 **FAIL**（`:328`，Expected 3 / Actual 5）/ 恢复 PASS | 0 / **1** / 0 |

> 说明：`check.ps1` 的 Canonical Evidence 逐条校验分支只对 `in_review/approved/done/closed_with_limitations` 生效（`tools/governance/check.ps1:660`；任务卡当前 `status: in_progress`），因此 PASS **不能替代** pin 复核——上表第 7 行是本 Review 自行完成的复核。另：修改 `verification/REALUSE-DATA-SAFETY-7|8/**` 后，SAFETY-7/8 的 `check.ps1` 仍 PASS，证明检查器按"工作树不匹配→回退 pin 所指 commit blob"实现了历史 pin 稳定性（`check.ps1:698-713`），历史证据未被破坏。

## 7. 数据安全与资源

- **生产代码零改动**：`git diff --stat 5b888cd70..40d286e85 -- apps/desktop-avalonia/src` 为空；`git show dcce29a13 --stat` 只有测试 + 文档/证据。
- **无用户数据**：diff 不涉及 `data/**`、SQLite、Python、迁移、安装脚本；未读取或写入任何用户库/样本。
- **未 push**：`git for-each-ref refs/remotes` 无 `SAFETY-9` 相关 ref；分支无 upstream；`reflog` 无该分支 push 记录；本 Review 未执行任何网络写操作。
- **资源 manifest 可核**：`verification/REALUSE-DATA-SAFETY-9/resource-manifest.json` 声明 `tmp/safety9-negctl.txt` 已删除（`deleted: true`）——实测 `Test-Path` = **False**，声明成立（对照 SAFETY-8 R-001：`tmp/safety8-negctl.log` 现 `Test-Path` = False，SAFETY-8 Review 的 R-001 已闭环）；worktree 条目 `PRESERVE_REFERENCED` 与事实一致。
- **审查侧写入**：仓库内仅本文件（新建）；破坏性实验只在 `G:\CODEX\New Manga.workspace\tmp\safety9-review\` 的仓外副本内进行。

## 8. 非阻断观察（不列为 finding，供 DSH 处置参考）

1. **STATUS / TASK_LEDGER 指针滞后**：`doc/STATUS.md:7` 与 `doc/TASK_LEDGER.md:44` 仍写 SAFETY-9 `ready`，而任务卡 `status: in_progress`、`REBASELINE_PLAN` 已写 `in_progress`。这与 SAFETY-8 同期做法一致（`60056d353` 时任务卡 `in_progress`、ledger 仍 `ready`），`check.ps1` 只校验 ledger 计数不校验逐行状态，故 PASS。建议在 closeout 时用 `tools/governance/task_ledger.py --write` 与 STATUS 一并刷新。
2. **AC2 措辞可更完整**：`ac2-eol-pin.md:73-74` 只写 SAFETY-8 Review「12/12 一致、变化恰为 5 条」，未提其同时复核 SAFETY-8 卡自身 10/10（SAFETY-8 Review `:88`）。不是不实陈述，只是读者需要回看报告才能知道完整范围。
3. **判别力覆盖面**：新断言判别的是 F-005 的 `GoToAsync` 早退分支；`SaveProgressAsync` 的 `_isClosing && !isClosing` 分支与 `CloseAsync` 的等待循环仍只由回归栅栏断言（`loadsBefore + 1` 等）间接约束。这与 AC1 原文一致，不构成缺陷；若日后需更强判别力，可再加"`ProgressSaveCalls` 未增"的断言（SAFETY-8 Review R-002 建议的反例即含此项）。
4. **格式**：`doc/REBASELINE_PLAN.md` 的 diff 在文件末尾新增一个空行（cosmetic，属 allowed_paths）。
5. **交接项**：任务卡 `delivery_head`/`reviewer` 仍为 null，`doc/handoffs/REALUSE-DATA-SAFETY-9-handoff.md` 未生成——与 SAFETY-7/8 同期做法一致，属 DSH 治理/交接职责，不影响本次交付内容。

## 9. NOT_RUN

- **Release 配置**复跑（只跑 Debug/`net9.0`，与 Task 证据同口径）。
- 解决方案其余测试项目（`NewManga.CoreClient.Tests`、`NewManga.Host.Tests`、`NewManga.DesignSystem.Tests`、`NewManga.ThemeEngine.Tests`）的全量复跑——本 Task 未改这些项目，按 Task 口径只跑 `NewManga.App.Tests`（403 条）。
- `SaveProgressAsync` 的 `_isClosing && !isClosing` 分支的独立探针实验（未做增量注入实验，只读回归栅栏断言）。
- 干净 clone / 非 Windows / `core.autocrlf=false` 环境复现（本任务不涉及行尾 pin 变更）。
- SAFETY-7/8 报告内 22 条历史 pin 的逐条重算（只核对两份报告的结论文本与其 commit/路径真实性，以及 SAFETY-9 自身的 8 条 pin）。
- 仓内原地负向对照（按要求只读，未在仓库内覆盖生产文件）。

## 10. 独立性声明

- 审查者是 Team Lead 派发的**独立上下文子 agent**（Agent Teams `task-7`，会话名 `safety9-reviewer`），**未参与** REALUSE-DATA-SAFETY-9 的实现、返修、证据撰写或提交；审查期间只读 `reviewed_head = 40d286e85`。
- 符合 2026-10-31 用户裁决的"上下文独立"口径（同一 Agent 会话/实例不得自审；作者可派发独立上下文子 agent 审查）。
- 本 Review 未修改任何代码、任务卡、STATUS、PLAN、LEDGER、`.gitattributes`；仓库内唯一写入为本文件；未 commit / checkout / stash / merge / push。
- 本报告只对上述 `base_commit`/`reviewed_head` 有效；head 改变或出现新 Review 后自动降为历史记录。
