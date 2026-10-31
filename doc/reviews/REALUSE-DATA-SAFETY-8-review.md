---
document_id: REALUSE-DATA-SAFETY-8-review
kind: independent_review
task_id: REALUSE-DATA-SAFETY-8
reviewer: safety8-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context task-5（独立上下文子 agent，未参与实现、返修或证据撰写）"
reviewer_independent: true
author: dsh-lead
base_commit: bb7cbda1d
reviewed_head: 231ff2ebe403216316e34b6501074265eecbd89d
delivery_head: 60056d353
verdict: approved
captured_at: 2026-11-01T02:08:02+08:00
---

# Review：REALUSE-DATA-SAFETY-8（上下文独立审查）

> 本报告只对 `base_commit = bb7cbda1d`、`reviewed_head = 231ff2ebe`（分支 `task/REALUSE-DATA-SAFETY-8`，worktree `G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-8`）有效。审查者只读该 head；**仓库内唯一写入即本文件**。负向对照、异常探针与判别性实验一律在仓外副本 `G:\CODEX\New Manga.workspace\tmp\safety8-review\negctl` 执行，未在仓库内做任何 `checkout`/`apply`/`commit`/`stash`。

## 1. 结论

**verdict: approved。** P0 = 0，P1 = 0，P2 = 3（`R-001` 资源 manifest 删除声明不实、`R-002` AC3 新用例不判别修复、`R-003` 证据文档提前写入未发生的审查结论）。三条 P2 均不改变 AC1/AC2/AC3 的成立，也不涉及用户数据、冻结契约或产品行为；按仓库门槛可交 DSH 集成，建议在 Closeout 处置或在紧随的治理小项中处置。

- 被审对象：实现提交 `60056d353`（F-001～F-005 修复 + 证据），证据 pin `923f1d5db` / `231ff2ebe`；审查开始时工作树干净（`git status --porcelain` 无输出）。
- 五条 SAFETY-7 P2 全部有对应交付：F-001/F-002/F-003 属证据文档修正，F-004/F-005 属代码健壮性；四项独立复核（12/10 条 pin、AC1 负向对照、F-004 异常探针、F-005 判别性实验）均得到预期结果（§5、§6）。
- 未发现数据安全风险：分支内 13 个文件全为 C# ViewModel/测试 + doc + verification，无 Python Core、无 Schema/迁移、无 `.gitattributes` 改动、无用户数据写、无 push。

## 2. 范围与依据

- 任务卡：`doc/tasks/REALUSE-DATA-SAFETY-8.md`（AC1～AC3、禁止范围、测试要求、Canonical Evidence）。
- 来源 Review：`doc/reviews/REALUSE-DATA-SAFETY-7-review.md:54-58`（F-001～F-005 原文与建议）。
- 实现 diff：`git show 60056d353`（`ReaderOverlayViewModel.cs` 77 行变动、`LibraryProgressRefreshTests.cs` +38、两组证据文档、卡与 Plan；全提交 12 文件 +382/−68）。
- 证据：`verification/REALUSE-DATA-SAFETY-8/*`（5 份 + resource-manifest）、`verification/REALUSE-DATA-SAFETY-7/{ac2-eol-pin.md, ac1-negative-control.md}`。
- 调用链：`AppShellViewModel.cs:1055,1061,1206`（键盘翻页与关闭均 fire-and-forget）→ `ReaderOverlayViewModel` → `LibraryViewModel.OnReaderProgressSavedAsync:1051-1066`（仅 `IsClosing` 才走权威重读）→ `IHostController`。

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `verification/REALUSE-DATA-SAFETY-8/resource-manifest.json:18-25`（条目 `deleted: true`）、`:27-32`（`closeout_counts.deleted: 1`）；`doc/tasks/REALUSE-DATA-SAFETY-8.md:90`（"已删除"） | **资源收口记录与事实不符。** manifest 声明负向对照临时日志 `G:/CODEX/New Manga.workspace/tmp/safety8-negctl.log` 已删除，但该文件在 `reviewed_head` 上仍存在（943 bytes，CreationTime/LastWriteTime 均为 `2026-11-01T01:51:51`），而 manifest 提交于 `01:54:57`，即提交时"已删除"已不成立。对照 SAFETY-7 同类条目 `tmp/safety7-negctl` 实测确实不存在（其声明为真）。影响仅限资源处置记录的可核性，不涉及用户数据。 | 本 Review 实测：`Test-Path 'G:\CODEX\New Manga.workspace\tmp\safety8-negctl.log'` → `True`；`Get-Item` 长度 943、时间 01:51:51；`Test-Path ...\tmp\safety7-negctl` → `False` | 删除该文件以保持 `deleted: true` 成立；或把条目改为 `DELETE_PENDING`/`PRESERVE`，并在 Closeout 记录实际处置 | open |
| R-002 | P2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs:304-331`；被引作证据于 `verification/REALUSE-DATA-SAFETY-8/ac3-closing-gate.md:39-45` | **AC3 新增用例确定性成立，但不判别 F-005 修复。** 用例在 close 窗口内调用 `GoToAsync(5)`，此刻保存 A 仍被 gate 挂起、`_isSaving` 仍为 `true`，因此**即使没有 `_isClosing` 门禁**，旧实现的 `SaveProgressAsync` 也会因 `_isSaving` 早退而不启动第二个保存；断言（`loadsBefore + 1`、`IsOpen == false`、`LastSaveResult == Saved`）在修复前后同样成立。该用例实为防回归栅栏，不能作为 F-005 的证明。 | 仓外副本把生产文件替换为 `60056d353^`（blob `5333b66b5`，实测 `_isClosing` 出现 0 次）后：`dotnet build` 0/0 EXIT=0；`--filter FullyQualifiedName~ClosingWhileSecondSaveRequested` → **1 通过 / 0 失败，EXIT=0**；同一 pre-F-005 代码下 filtered 全套 **7/7 通过**。交付版同样 7/7、单跑 5 次全通过（42–43 ms） | 补一条真正可判别的断言（见下方反例），或在 `ac3-closing-gate.md` 明确标注该用例为回归栅栏而非负向对照 | open |
| R-003 | P2 | `verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md:72` | **证据文档在交付提交中写入尚未发生的审查结论。** 该行原文「SAFETY-7 与 SAFETY-8 的独立 Review 均按此方式复核并全部一致（SAFETY-6 12/12、SAFETY-7 10/10）」由 `60056d353`（`2026-11-01T01:54:27`）新增，而 SAFETY-8 独立 Review 在本提交之后才开始（本 Review 起始 01:55 之后），属对未发生事件的断言——与 F-001 同类（证据文档写不实内容）。结论本身现已被本 Review 证实（12/12 与 10/10 全部一致），故不影响 pin 正确性。 | `git show 60056d353 -- verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md` 该行为 `+` 行；提交时间 01:54:27；本 Review `captured_at` 02:08:02 | 改为「可供独立 Review 按此方式复核（SAFETY-6 12/12、SAFETY-7 10/10）」，或在复审后回填结论 | open |

> 无 P0/P1。三条 P2 均为证据/资源记录的准确性与证据强度问题，未遮蔽任何 AC 结论（本 Review 已逐条独立复核 pin、复跑测试、复现负向对照、并以探针验证 F-004/F-005 的实际行为）。

### 其他观察（非 finding，无需处置或仅记录）

1. `verification/REALUSE-DATA-SAFETY-7/ac1-negative-control.md:15` 把 `$wt` 硬编码为 SAFETY-7 worktree。该 worktree 现存且干净（HEAD `2a0528851`），配方当前可执行；若日后清理该 worktree，配方需改路径。建议参数化 `$wt`（指向任意含 R-001 修复的交付 checkout）。
2. AC1 原文要求附 `exit_code=`，交付文档统一使用 `EXIT=`——与 SAFETY-6/7 已被接受的口径一致，不构成缺口。
3. `doc/REBASELINE_PLAN.md` 补丁在文件尾追加了一个空行（无意义 diff）。检查器预算 6628 bytes / 61 lines 仍在 7000/64 内。
4. 本次 `check.ps1` 的 PASS **未执行** Canonical Evidence 逐条校验分支（`tools/governance/check.ps1:660` 仅对 `in_review/approved/done/closed_with_limitations` 生效，任务卡仍为 `status: in_progress`，与 SAFETY-7 同期做法一致）。因此 PASS 不能替代 pin 复核——本 Review 已自行用 `git cat-file blob` 完成复核（见 §5）。
5. 相对路径命令对 cwd 敏感是 F-003 的原始动机：本 Review 首次误把 `apps/desktop-avalonia/NewManga.sln` 放在 `apps/desktop-avalonia` 下执行即得 `MSB1009`（EXIT=1）。交付日志已按 F-003 逐段记录 cwd，该问题已闭环。

## 4. AC 判定

### AC1（F-001/F-002/F-003 证据文档修正）——MET

| 检查项 | 结论 | 依据 |
|---|---|---|
| `ac2-eol-pin.md` 计数与表格覆盖 12 条 pin / 5 条变化 | **MET** | 文档 `:37-61` 列 4 代码 + 8 证据共 12 行；`:61` 写「12 条 pin；5 条值变化（3 代码 + 2 证据）；7 条不变」。本 Review 用 `git cat-file blob` 逐条核对：新 pin **12/12 与 blob SHA-256 一致**；旧 pin 取 `306ae09ae^` 版本比对，实际变化恰为 5 条（`E-AC1-READER-VM`、`E-AC1-LIBRARY-VM`、`E-AC1-TEST-FAKE`、`E-AC1-LOG`、`E-AC2-DATA`），其余 7 条不变 —— 与文档完全一致。任务卡 `:43` 与 SAFETY-7 卡（`doc/tasks/REALUSE-DATA-SAFETY-7.md` AC2 与测试表）同步改为 12/5，与 diff 一致 |
| `ac1-negative-control.md` 为 post-delivery 配方且可复现 | **MET** | 配方 `:14-31` 为「`git show 29d06c462:<src>` 覆盖 → 在 `apps/desktop-avalonia` 下 build+filtered test → `git checkout HEAD -- <src>` 恢复」，不再是提交前工作树配方；`:33-48` 附原始输出与 `EXIT=`。本 Review 在仓外副本按等价字节级步骤执行：覆盖后文件 SHA-256 = `db99f3eb…`（即 SAFETY-6 `E-AC1-READER-VM` 新 pin，证明取到的就是修复前字节）→ build 0 警告/0 错误 EXIT=0 → `--filter FullyQualifiedName~ClosingWhileSaveInFlight` **1 失败 / 0 通过 / 1 总计，EXIT=1**，与文档 `:43-45` 逐字一致。另：残留于 `tmp/safety8-negctl.log` 的原始日志（943 bytes）内容与文档转录一致（`[FAIL]` 行、36 ms、xUnit 0.63s、EXIT=0/EXIT=1） |
| `ac1-fix-tests.txt` 含 cwd、filtered 段、EXIT | **MET** | 日志 `:5`（build）、`:15`（filtered）、`:23`（全量）三段均带 `cwd=<绝对路径>`；每段结尾有 `EXIT=`；文件头有 `generated_at` 与 host/shell（`:2-3`）。本 Review 复跑结果与日志数值一致（§6） |

### AC2（F-004 异常捕获限定）——MET

- `ReaderOverlayViewModel.cs:456-462`：新增通用 `catch (Exception ex)`，写 `System.Diagnostics.Debug.WriteLine(...)` 并置 `SaveStatusText = "进度：保存失败（内部错误）"` —— **记录 + 可见状态，不再静默**。`SaveStatusText` 走 `Set()`（`:214-218`）会触发 `PropertyChanged`，且视图确实绑定（`apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ReaderOverlay.axaml:118`），所以"可见"成立。
- `ReaderOverlayViewModel.cs:303-306`：`CloseAsync` 的等待 `catch` 已限定为 `InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException`，与 `SaveProgressCoreAsync` 原类型化集合（`:452`）一致，满足「与 core 一致的已知类型」。
- **独立验证（仓外探针）**：在副本里给 `FakeHostController.SaveReadingProgressAsync` 注入 `NotSupportedException`（非类型化）后，`GoToAsync(2)` 不抛出，`SaveStatusText == "进度：保存失败（内部错误）"`，`LastSaveResult == null`（探针 2/2 通过）。同时确认 `SaveProgressCoreAsync` 的 try 覆盖了全部投递与回调，因此保存路径不再产出 faulted task，`CloseAsync` 限定捕获不会把未知异常甩给 fire-and-forget 的 `CloseCommand`（`ReaderOverlayViewModel.cs:82`）。
- 未发现行为回归：类型化状态文案与既有 5 种分支不变；仅新增"内部错误"兜底。

### AC3（F-005 关闭期间保存门禁）——MET（用例判别力见 R-002）

- 门禁实现：`_isClosing` 字段（`:66-71`）、`CloseAsync` 全程 `try/finally` 置位（`:294-327`）、`GoToAsync` 早退（`:336`）、`SaveProgressAsync` 在 `_isClosing && !isClosing` 时早退（`:396-399`）。
- 「恰好一次权威重读」的时序论证（正确）：`SaveProgressCoreAsync` 的 `finally { _isSaving = false; }`（`:463-466`）在任务完成**之前**执行，而 `CloseAsync` 的 `await pending` 续体只在任务完成后才恢复，故循环退出时 `_isSaving` 必为 `false`；循环退出到 `SaveProgressAsync(isClosing: true)` 之间无 `await`，无插入点；closing 期间任何第三方保存都被门禁挡下。因此关闭时恰好一次权威重读成立。循环也不会空转：closing 期间唯一能启动新保存的是 closing 自身，且它在循环之后。重复 `CloseAsync`（命令为 fire-and-forget，双击可触发）同样只产生一次重读（第二次被 `_isSaving` 短路）。
- 新用例确定性：**成立**。单跑 5 次全部通过（42–43 ms），filtered 7/7 稳定，不依赖时序侥幸。
- 新用例判别性：**不成立**（R-002）。仓外已证明存在可判别断言：在 close 窗口内 `GoToAsync(5)` 后立即断言 `PageIndex` 仍为 3 且 `ProgressSaveCalls` 未增 —— 交付版通过，pre-F-005 版实测 `Assert.Equal() Failure: Values differ`（FAIL）。这说明判别性用例是可行的，交付实现只是没写这一条。
- `GoToAsync` 在 closing 时被忽略是否影响正常阅读：**不影响**。门禁仅在 `CloseAsync` 执行期间生效，`finally` 复位；`OpenAsync`/`ToggleLayoutAsync`/`ToggleDirectionAsync` 均不受影响；关闭窗口内的翻页本来就是无意义输入。

## 5. pin 复核（独立执行 `git cat-file blob` → SHA-256）

**SAFETY-6 的 12 条（pin 指向 `doc/tasks/REALUSE-DATA-SAFETY-6.md` 的 Canonical Evidence 表）：12/12 全部一致。**

- 代码证据 4 条（commit `fb5065013`）：`E-AC1-READER-VM` `db99f3eb…b642ef`、`E-AC1-LIBRARY-VM` `bc651c56…66e7`、`E-AC1-TEST` `135de02c…60a2`、`E-AC1-TEST-FAKE` `c0c4822b…6533`。
- 证据文件 8 条：`E-AC1-LOG` `1bb0ac36…466c`、`E-AC1-DOC` `e913e2dd…66e8`、`E-AC2-DOC` `1edb35f1…7c47`、`E-AC2-DATA` `e2106154…5dea`、`E-AC3-DOC` `9c27d477…950b`、`E-EVIDENCE-INDEX` `d199f484…a3ff`、`E-GOV-CHECK`（commit `b94dc3d86`）`bc97d7a7…592e`、`E-RESOURCE-MANIFEST`（commit `82e86e97b`）`133943d7…befd99`（此处为前 8 位/后若干位摘要，逐条比对结果全为 True）。
- 旧 pin 复核：从 `306ae09ae^:doc/tasks/REALUSE-DATA-SAFETY-6.md` 取旧值，与 `ac2-eol-pin.md:41-59` 的「旧 pin」列逐字一致；`306ae09ae` 的卡 diff 恰为 5 行 pin 值变化（3 代码 + 2 证据）。

**SAFETY-8 卡自身 10 条：10/10 全部一致。**（`E-AC2-READER-VM` `f71eed26…64eb`@`60056d353`、`E-AC3-TEST` `b1862e36…ecd2`、`E-AC1-PIN-DOC` `4b7676cf…96f6`、`E-AC1-NEG` `ad1a0fc4…e4b2`、`E-AC1-DOC` `42d5a986…6ec8`、`E-AC2-DOC` `a90521d5…94d0`、`E-AC3-DOC` `6bc65d82…ec01`、`E-TEST-LOG` `713a8e0a…8e06`、`E-EVIDENCE-INDEX` `2df34f82…860d`、`E-RESOURCE-MANIFEST` `3fef751e…3f55`@`923f1d5db`。）

**blob 谱系交叉验证**：`29d06c462` 与 `fb5065013` 的 `ReaderOverlayViewModel.cs` 同为 blob `e4b5152d7`（即 R-001 修复前状态），`60056d353^` 为 `5333b66b5`（有 R-001、无 F-005），`60056d353` 为 `98451f079`（其 SHA-256 `f71eed26…` 正是卡内 pin）—— 三个版本的 pin 互相自洽。

另核对 `ac2-eol-pin.md:33` 引用的检查器机制：`tools/governance/check.ps1:698-713` 确为「先比工作树字节，不匹配再回退到 pin 所指 commit 的 blob 字节」，文档描述准确。

## 6. 复跑结果（真实输出与 EXIT）

工作目录 `G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-8`，pwsh 7.6.8，net9.0。

| 场景 | 命令 | 结果 | EXIT |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -v q --nologo` | 已成功生成。0 个警告 / 0 个错误，已用时间 00:00:03.31 | **0** |
| filtered | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q --filter FullyQualifiedName~LibraryProgressRefreshTests` | 已通过! 失败 0 / 通过 **7** / 跳过 0 / 总计 7，78 ms | **0** |
| 全量 | 同上去掉 `--filter` | 已通过! 失败 0 / 通过 **396** / 跳过 **7** / 总计 **403**，57 s | **0** |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-8.md` | `Governance check: PASS (3 warnings)`；WARN=7 个非终态 Task、`doc/STATUS.md` 80% 预算（3027 B/31 行）、`doc/REBASELINE_PLAN.md` 80% 预算（6628 B/61 行） | **0** |
| AC3 用例稳定性 | 单跑 `--filter FullyQualifiedName~ClosingWhileSecondSaveRequested` ×5 | 5/5 通过（42、42、42、43、43 ms） | 每次 **0** |
| AC3 用例判别力（仓外副本，pre-F-005 生产文件 `5333b66b5`） | 同上 filtered | **1 通过 / 0 失败**（未随修复消失 → 不判别） | **0** |
| AC3 判别性探针（仓外，交付版） | 自定义 `ReviewerProbe_LatePageTurnDuringClose_IsIgnored` | 通过（close 窗口内 `PageIndex` 保持 3、保存调用数不变） | **0** |
| AC3 判别性探针（仓外，pre-F-005） | 同上 | `Assert.Equal() Failure: Values differ`（`PageIndex` 变 5）→ FAIL | **1** |
| AC1 负向对照（仓外，`29d06c462` 生产文件） | build + `--filter FullyQualifiedName~ClosingWhileSaveInFlight` | build 0/0 EXIT=0；test **1 失败 / 0 通过 / 1 总计**（`ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection [FAIL]`） | build **0** / test **1** |
| F-004 探针（仓外，交付版 + 注入 `NotSupportedException`） | 自定义 `ReviewerProbe_NonTypedSaveFailure_IsRecordedAndVisible` | 通过：不抛出、`SaveStatusText == "进度：保存失败（内部错误）"`、`LastSaveResult == null` | **0** |

与预期对账：任务卡/交接预期「filtered 7/7」「全量 396 通过 / 0 失败 / 7 跳过 = 403」「check.ps1 PASS」**全部吻合**；交付日志 `ac1-fix-tests.txt` 的数值与本机复跑一致（build 0/0、filtered 7/7、全量 396/403）。

## 7. 数据安全与工作区

- 分支内改动（`git diff --name-status bb7cbda1d..231ff2ebe`，13 个路径）：`ReaderOverlayViewModel.cs`、`LibraryProgressRefreshTests.cs`、`doc/REBASELINE_PLAN.md`、`doc/tasks/REALUSE-DATA-SAFETY-{7,8}.md`、SAFETY-7 的两份证据文档、SAFETY-8 的 6 份证据文件。**无 `src/`（Python Core）、无 Schema/迁移、无 `.gitattributes`、无用户数据路径。**
- **无用户数据写、无迁移**：本 Task 零数据面改动；`resource-manifest.json` 亦声明"用户数据零访问"（该声明本身与 §7 事实一致）。
- **无 push**：`git rev-parse --abbrev-ref @{u}` → `fatal: no upstream configured`；`git ls-remote --heads origin task/REALUSE-DATA-SAFETY-8` 无输出；`git -C "G:\CODEX\New Manga" branch --contains 231ff2ebe` 仅列出 `task/REALUSE-DATA-SAFETY-8`（未进 main）。
- **main 工作区未被我触碰**：审查开始时 `git -C "G:\CODEX\New Manga" status --porcelain` 为 `M doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md`、`M doc/handoffs/NIGHT-SHIFT-2026-11-01.md`（另一条线的活动）；审查结束时为 `M doc/handoffs/NIGHT-SHIFT-2026-11-01.md`、`?? doc/reviews/FEA-00-dsh-r8-appointment.md`（main 已前进到 `74a772167`）。该变化来自并行的 Codex/FEA 线，非本 Review 造成，也未触碰。
- 本 Review 的 `dotnet build/test` 在 worktree 内产生的仅为被 `.gitignore` 覆盖的 `bin/obj`：复跑完成后、撰写本报告前 `git status --porcelain` 为空；报告写入后工作树仅多出本文件一个未跟踪路径（`?? doc/reviews/REALUSE-DATA-SAFETY-8-review.md`）。

## 8. 独立性声明

- 审查者 `safety8-reviewer` 为 Agent Teams **fresh context** 子 agent（task-5），**未参与** REALUSE-DATA-SAFETY-8 的实现、返修、证据撰写或任何前置提交；未阅读实现者的推理过程，仅基于 `reviewed_head` 的文件、`git` 对象与可执行实验得出结论。
- 只读约束遵守：未修改被审代码、任务卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`.gitattributes`；未执行 `git add/commit/checkout/stash/merge`；未 push；未触碰 main 工作区的未提交改动。
- **仓库内唯一写入**：本文件 `doc/reviews/REALUSE-DATA-SAFETY-8-review.md`。
- 所有破坏性实验（覆盖生产文件、注入异常、判别性探针）均在仓外副本 `G:\CODEX\New Manga.workspace\tmp\safety8-review\negctl` 执行，副本来自 `reviewed_head` 的目录复制（不含 `.git`，故恢复步骤用 `git cat-file blob` 从只读仓库取原始字节替代文档中的 `git checkout HEAD --`，字节效果等价）。

## 9. NOT_RUN

| 项 | 原因 |
|---|---|
| 在真实 SAFETY-7 worktree 内逐字执行 `ac1-negative-control.md` 配方 | 只读约束（不得修改他人 worktree）；改为在仓外副本用等价字节级步骤执行，结果与文档一致（§6） |
| GUI 实体交互（真实点击关闭/翻页、观察 `SaveStatusText` 渲染） | 无显示会话；以 headless `AvaloniaFact` + 绑定核查（`ReaderOverlay.axaml:118`）替代 |
| Python Core 侧测试、全仓治理检查（不带 `-TaskPath`） | 超出本 Task 范围；仅按要求跑 `-TaskPath doc/tasks/REALUSE-DATA-SAFETY-8.md` |
| SAFETY-7 Review 声称的「SAFETY-7 10/10 pin」独立复核 | 超出本 Task 范围（本 Review 只复核 SAFETY-6 的 12 条与 SAFETY-8 的 10 条） |
| 真实用户数据根操作、打包/安装链路 | 本 Task 不涉及数据面与打包面 |
