---
document_id: REALUSE-DATA-SAFETY-7-review
kind: independent_review
task_id: REALUSE-DATA-SAFETY-7
reviewer: safety7-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams fresh context task-4（独立子 agent，未参与实现与返修）"
reviewer_independent: true
author: dsh-lead
base_commit: 29d06c462
reviewed_head: 58596949a
delivery_head: 306ae09ae
verdict: approved
captured_at: 2026-11-01T01:46:00+08:00
---

# Review：REALUSE-DATA-SAFETY-7（上下文独立审查）

> 本报告只对 `base_commit = 29d06c462`、`reviewed_head = 58596949a`（分支 `task/REALUSE-DATA-SAFETY-7`，worktree `G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-7`）有效。审查者只读该 head；**仓库内唯一写入即本文件**。负向对照只在仓外副本 `G:\CODEX\New Manga.workspace\tmp\safety7-review\negctl` 执行，未在仓库内做任何 `checkout`/`apply`/`commit`。

## 1. 结论

**verdict: approved。**

- **P0：0 条；P1：0 条；P2：5 条（均 open，不阻断集成）**。
- **AC1（R-001 并发 NRE）MET**：修复把 `book`/`page`/`pageCount` 在 `await` 前固化为局部值，`_inFlightSave` 记录在途保存，`CloseAsync` 先等待在途保存再执行 closing 保存，因此不再解引用已清空的 `_book`，且关闭时的权威重读不再被 `_isSaving` 短路。本 Review 在仓外副本独立复现负向对照：**1 failed / 0 passed，EXIT=1**，堆栈 `System.NullReferenceException` @ `ReaderOverlayViewModel.cs:377` ← `GoToAsync:308`，与 SAFETY-6 Review R-001 描述一致；修复后 `LibraryProgressRefreshTests` **6/6（重复 6 次全通过）**、全量 **395 通过 / 0 失败 / 7 跳过（402）**（重复 2 次一致）。
- **AC2（R-002 pin 规范化）MET**：`.gitattributes` 仅新增 `verification/REALUSE-DATA-SAFETY-6/** text eol=lf`；`git check-attr` 证明作用域只覆盖 SAFETY-6 证据目录（SAFETY-7/SAFETY-5/源码均 `unspecified`）；该目录 8/8 文件现为 `i/lf w/lf`；SAFETY-6 证据 blob 相对 base **零变化**（未重写历史证据字节）。本 Review 用 `git cat-file blob` 原始字节逐条复核：**SAFETY-6 12/12 条 pin 与对应 commit 的 blob 一致**、**SAFETY-7 10/10 条 pin 一致**。
- **AC3（R-003 日志格式）MET**：`ac1-fix-tests.txt` 含 `generated_at`（ISO 8601 + 时区）、host/shell、两条完整命令与两处 `EXIT=0`；负向对照给出 4 步可执行步骤与实测结果。仍有证据强度缺口（见 F-002/F-003），不改变判定。
- **复跑**：build 0 警告/0 错误（EXIT=0）；全量 395/0/7（EXIT=0）；filtered 6/6（EXIT=0）；`check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-7.md` → **PASS (3 warnings)**（EXIT=0）。与交付证据一致。
- **数据安全**：无用户数据写、无迁移、无冻结契约改动、无 push（远端不存在该分支）、main 工作区无 tracked 变更（仅 1 个 Lead 夜班产生的 untracked handoff，非本 Task 提交）。

**审批判断**：5 条 P2 属"证据文档准确性 / 证据可复现性 / 代码卫生与残留窄竞态"，均不改变 AC1–AC3 的成立，也未被证据掩盖（本 Review 已逐条独立复核 pin、复跑测试、复现负向对照），按仓库门槛可批准集成；建议 Lead 在 Closeout 记录或并入紧随的治理小项处置（F-001～F-005）。

## 2. 审查范围与依据

- **被审对象**：`task/REALUSE-DATA-SAFETY-7` @ `58596949a604ad8aaed32ac04f759071806426cb`；base `29d06c462`（`main` HEAD）。
- **提交链**：

| commit | 内容 | 被审范围 |
|---|---|---|
| `306ae09ae` | 实现（delivery_head）：`ReaderOverlayViewModel.cs` 修复、`FakeHostController.cs` gate、新增并发用例、`.gitattributes`、SAFETY-6 6 条 pin 更新、SAFETY-7 证据 6 文件 | 代码/测试/规则/pin 全量审 |
| `8a343d76f` | SAFETY-7 任务卡 AC 判定与 Canonical Evidence 表、`resource-manifest.json` | 证据/pin 复核 |
| `58596949a` | 任务卡登记 `E-RESOURCE-MANIFEST` pin（reviewed_head） | 证据/pin 复核 |

- **reviewed_head 与实现的对应**：`git diff --stat 306ae09ae..58596949a -- apps .gitattributes` 为空 → 交付后两个提交只动 `doc/**` 与 `verification/**`，reviewed_head 上的代码/规则与 delivery_head 完全一致。
- **变更面**：`git diff --name-status 29d06c462..58596949a` 共 14 项：`M .gitattributes`、`M` 3 个源码/测试文件、`M` 3 个 doc（REBASELINE_PLAN、SAFETY-6、SAFETY-7 任务卡）、`A` 7 个 SAFETY-7 证据文件。无 `data/**`、无 SQLite、无 Python、无迁移、无 `doc/contracts/**`、无 `IHostController` 接口变更。
- **依据**：SAFETY-6 Review R-001/R-002/R-003 原文（`doc/reviews/REALUSE-DATA-SAFETY-6-review.md:54-56,151-161`）、SAFETY-7 任务卡（含 base 版本 AC 原文对照）、`verification/REALUSE-DATA-SAFETY-7/**` 全部 7 文件、`git show 306ae09ae` 全量 diff、修复前后 `ReaderOverlayViewModel.cs` 全文、`LibraryProgressRefreshTests.cs`、`FakeHostController.cs`、`LibraryViewModel.OnReaderProgressSavedAsync/LoadProgressAsync`、`HostController.SaveReadingProgressAsync`、`.gitattributes` 全文与 `git check-attr`、`git ls-files --eol`、`git ls-tree`。
- **视角**：Architecture（分层/契约/持久化/并发安全）与 Verification（实际运行、逐项 PASS/FAIL/NOT_RUN）均已执行；Standards/Spec 按任务卡 AC 原文直接核对，未单独启用（模板声明为可选视角）。

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| F-001 | P2 | `verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md:27,43,47`；`doc/tasks/REALUSE-DATA-SAFETY-7.md:50,65` | **AC2 证据文档的 pin 计数与对照表与实际变更不符。** SAFETY-6 卡当前共 **12** 条 Canonical Evidence（4 代码 + 8 证据）；本 Task 实际改动 **5** 条 pin（3 代码：`E-AC1-READER-VM`、`E-AC1-LIBRARY-VM`、`E-AC1-TEST-FAKE`；2 证据：`E-AC1-LOG`、`E-AC2-DATA`），未变 7 条。文档却写"重算 11 条 pin 对照（2 条更新）""9 条不变 / 2 条更新"，对照表只列 8 条证据文件、**完全未列 4 条代码 pin**，旧 pin 只保留 8 位前缀。另：AC2 原文（base 版本）要求"重算 SAFETY-6 的 11 条 pin 并在任务卡登记 new/old 对照"，实现提交把 AC 文本改写为"…登记于 `ac2-eol-pin.md`"并在同一次提交标记 MET。影响：按文档无法核对代码 pin 的 old→new（pin 本身经本 Review 12/12 与 blob 复核正确，见 §5） | `git show 306ae09ae -- doc/tasks/REALUSE-DATA-SAFETY-6.md` 实为 5 行 pin 值变化；`git cat-file blob` 逐条复核 12/12 与卡内新 pin 一致；`ac2-eol-pin.md:34-41` 表仅 8 行 | 修正 ac2-eol-pin 的计数与表格（补 4 条代码 pin），或在 Closeout 说明本文档的统计口径；由 Lead 确认 AC2 文本改写属授权范围 | open |
| F-002 | P2 | `verification/REALUSE-DATA-SAFETY-7/ac1-negative-control.md:9-21`（步骤）、`:23-27`（结果） | **负向对照的"可复现步骤"在交付 head 上不可复现。** 步骤 1 `git diff -- <file> > fix.patch` + `git checkout -- <file>` 只在"修复尚未提交"的作者工作树里能移除修复；交付 head 工作树干净，逐字执行时 `git diff` 为空、`git checkout --` 无效果，随后 build+test 会 6/6 通过，得不到声称的 1 failed。另：负向对照只有摘要 + `[FAIL]` 行，无原始输出尾巴与 `exit_code=` 字段（R-003 原意是"命令原文、输出尾部与 exit_code="） | 本 Review 在仓外副本用 `git cat-file blob 29d06c462:<path>` 还原生产文件后独立复现 1 failed/0 passed/EXIT=1（§8）；若按文档步骤在交付 head 执行则为空操作 | 改为 post-delivery 配方：`git show 29d06c462:<path> > <path>`（或 `git checkout 29d06c462 -- <path>`）→ build/test → `git checkout HEAD -- <path>` 恢复，并附原始输出与 `exit_code=` | open |
| F-003 | P2 | `verification/REALUSE-DATA-SAFETY-7/ac1-fix-tests.txt:1-21`；`doc/tasks/REALUSE-DATA-SAFETY-7.md:61` | **过滤 6/6 运行未进入 canonical 日志，且日志命令缺工作目录。** 任务卡把"`dotnet test --filter FullyQualifiedName~LibraryProgressRefreshTests` → PASS 6/6，EXIT=0"的证据指向 `ac1-fix-tests.txt`，但该日志只有 build + 全量两段 `## command:`，没有 filtered 段/输出/EXIT。日志把命令写作 `dotnet build NewManga.sln`、`dotnet test tests/NewManga.App.Tests/...` 且未记录 cwd —— 这些相对路径只在 `apps/desktop-avalonia` 下成立，在仓库根执行会 `MSB1009`（本 Review 实测） | `ac1-fix-tests.txt:5,15`；本 Review 在 worktree 根执行 `dotnet test tests/NewManga.App.Tests` → `MSB1009 项目文件不存在`，EXIT=1；在 `apps/desktop-avalonia` 下才通过（§7） | 日志统一记录 cwd/绝对路径，并把 filtered 运行单独列为 `## command:` 段（含 EXIT）；或修改任务卡的证据指向 | open |
| F-004 | P2 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs:286-296`（`catch (Exception)` 在 292） | **`CloseAsync` 用 `catch (Exception)` 静默吞掉在途保存的所有未知异常。** `SaveProgressCoreAsync` 只把 `InvalidOperationException`/`SidecarException` 记成类型化状态；其它异常（含本次修复针对的 NRE 同类）被完全静默，无日志、无通知。修复前该异常是"未观察 Task 异常"（同样静默），故不是行为回归，但本 Task 的目标正是消除某类未观察异常——吞掉全部异常会让同类回归从此不可见 | 代码审阅：`280-296` catch 全类型；`452-455`（core 的类型化 catch）对比 | 限定捕获类型（与 core 一致的类型化集合）或在 swallow 前记录 `Debug`/`Trace`/notify | open |
| F-005 | P2 | `ReaderOverlayViewModel.cs:286-290`（`await pending` 窗口）+ `:366-377`（`_isSaving` 早退） | **关闭等待窗口存在残留窄竞态（不是 NRE）。** `CloseAsync` 在 `await _inFlightSave` 期间控制权回到 UI 线程；若此时用户再触发翻页（`GoToAsync`→`SaveProgressAsync`）启动保存 B，则 CloseAsync 恢复后调 `SaveProgressAsync(isClosing:true)` 仍会被 `_isSaving` 短路，关闭的**权威重读被跳过**（B 的镜像回调仍会更新书架；`_book` 已由局部快照保护，不再 NRE）。AC1"CloseAsync 在 `_isSaving` 时仍保证一次权威重读"因此非绝对。概率极低、影响为一次"镜像而非权威重读"，与 SAFETY-6 Review 的 MA-09 症状同级 | 代码审阅 + 本 Review 理解的事件循环顺序；新用例的确定性 gate 场景**不触发**该窗口（CloseAsync 的 closing 保存在等待完成后执行），故 6/6 通过不覆盖该残留 | closing 期间禁用翻页/置 closing 标志使新保存不启动，或在 closing 时循环等待 `_inFlightSave` 直至 `_isSaving == false` 后再保存 | open |

> 无 P0/P1。F-001～F-003 属证据卫生（不改变任何 pin 或运行结论的事实）；F-004/F-005 属代码卫生与极窄竞态（不产生用户可见失败、不丢数据）。

**Observations（非 finding，供 Lead 处置）**

- **O-1**：`_inFlightSave` 完成后不清空（`:64`、`:375`），会保留最后一次保存任务的状态机（含 `book`/`page` 局部引用）直到下一次保存；属轻微托管内存保留，不泄漏原生资源。
- **O-2**：关闭现在会等待在途保存的剩余时长；`HostController.SaveReadingProgressAsync` 把 `OperationCanceledException` 等映射为 `Failed`，故等待受 IPC 超时/取消约束（`HostController.cs` 的 typed catch 返回 `ReaderProgressSaveResult.Failed`），但关闭时延本次未量化（沿袭 SAFETY-6 Review O-1）。
- **O-3**：main 工作区存在 **1 个 untracked** `doc/handoffs/NIGHT-SHIFT-2026-11-01.md`（`LastWriteTime 2026/11/1 01:34:14`，内容为 DSH 夜班晨报，不在本 Task 提交与 allowed_paths 内，非本 Task 产出）；main 无 tracked 变更。建议 Lead 自行收口，不计入本 Task 数据安全问题。
- **O-4**：SAFETY-6 任务卡 pin 已改为 blob 基准但卡内未注明基准（SAFETY-7 卡 `:70` 已注明）；因 `.gitattributes` 令该目录工作树=LF，blob/worktree 两种口径现已重合，故暂不构成歧义。

## 4. AC1（R-001 并发 NRE）判定：**MET**

| 审查点 | 事实与复核 | 判定 |
|---|---|---|
| 根因确认 | 修复前 `SaveProgressAsync`（base 版本 350-394 行）在 `await _controller.SaveReadingProgressAsync(...)` 之后用 `_book.BookId`/`_book.ChapterId`/`Pages.Count` 构造回调实参；`CloseAsync` 先调 `SaveProgressAsync(isClosing:true)`（被 `_isSaving` 早退），随后 `_book = null; Pages.Clear()`；在途保存恢复即 NRE，且 closing 权威重读丢失。与 SAFETY-6 Review R-001 描述一致 | ✓ |
| 局部固化 | `ReaderOverlayViewModel.cs:383-385` 在 await 前快照 `book`/`page`/`pageCount`；`416-419` 只用局部值；await 之后不再触碰 `_book`/`Pages` | ✓ |
| 在途保存等待 | `:64` 新增 `_inFlightSave`；`:366-377` `SaveProgressAsync` 变为薄包装（同步置 `_isSaving` 并记录任务）；`:281-305` `CloseAsync` 先 `await _inFlightSave`（`:286-296`，吞掉异常后继续），再执行 closing 保存 | ✓ |
| 权威重读仍发生 | 等待完成后 `_isSaving` 已由 core 的 `finally` 置 false（async 方法在 finally 之后才完成任务），因此 closing 保存不会被短路；`LibraryViewModel.cs:1051-1057` 在 `IsClosing` 时 `await LoadProgressAsync()` → `LoadReaderBookAsync`（`FakeHostController.ReaderLoadCount++`）。新用例断言 `ReaderLoadCount > loadsBefore`，而**非 closing** 的保存走镜像路径不增加该计数 → 该断言确实只可能由 closing 权威重读触发 | ✓ |
| 并发用例可靠性 | 用 `TaskCompletionSource` gate 确定性对齐"保存在 Host await 中"的窗口（`FakeHostController.ProgressSaveCalls/SaveGate/SaveGateStarted`，`:272-280`），不依赖 sleep/时序；`WaitAsync(5s)` 仅作兜底；重复 6 次（1+5）全部 6/6 | ✓ |
| 负向对照（判别力） | 本 Review 仓外副本：还原 base 生产文件、保留新测试 → build 0/0（EXIT=0）→ filtered `ClosingWhileSaveInFlight` **失败 1 / 通过 0 / 总计 1，EXIT=1**，`System.NullReferenceException` @ `ReaderOverlayViewModel.cs:377` ← `GoToAsync:308` ← 测试 `:284`；quiet 复跑 3/3 失败。证据 `ac1-negative-control.md` 声称的 1 failed/0 passed/EXIT=1 **属实** | ✓ |
| 全量回归 | 395/0/7（402），EXIT=0，两次一致；build 0 警告/0 错误 | ✓ |

结论：**MET**。残留问题仅为 F-004（异常静默）与 F-005（极窄残留竞态），均不构成用户可见失败或数据风险。

## 5. AC2（R-002 pin 规范化）判定：**MET**

### 5.1 `.gitattributes` 规则范围

- 规则（HEAD `.gitattributes` 末尾）：`verification/REALUSE-DATA-SAFETY-6/** text eol=lf`（上方 3 行注释说明原因）。仓库既有同类先例（`GOV-EOL-PIN-1`、`P19-UI-MANIFEST-VIEW-1`、`SEC-FIX-PATH-ECHO-1`）格式一致。
- `git check-attr text eol` 实测：
  - `verification/REALUSE-DATA-SAFETY-6/ac1-progress-refresh.md` → `text: set`、`eol: lf`；
  - `verification/REALUSE-DATA-SAFETY-7/README.md` → `unspecified`/`unspecified`；
  - `verification/REALUSE-DATA-SAFETY-5/governance-check.txt` → `unspecified`；
  - `apps/desktop-avalonia/src/NewManga.App/Program.cs` → `unspecified`。
  → **规则只作用于 SAFETY-6 证据目录**，未波及其他历史证据与源码。
- `git ls-files --eol verification/REALUSE-DATA-SAFETY-6/`：**8/8 `i/lf w/lf attr/text eol=lf`**（base 时该目录工作树为 CRLF）。
- **证据内容未变**：`git diff --stat 29d06c462..58596949a -- verification/REALUSE-DATA-SAFETY-6/` 为空；`git ls-tree -r` 两个 commit 该目录 blob 完全相同 → 未重写历史证据字节。

### 5.2 pin 复核（`git cat-file blob <commit>:<path>` 原始字节 → SHA256）

复核方法：`Start-Process git cat-file blob <rev>:<path> -RedirectStandardOutput` 落盘原始字节后 `Get-FileHash -Algorithm SHA256`，避免 PowerShell 管道编码污染。

**SAFETY-6（12/12 条与卡内 pin 一致）**

| evidence_id | commit | pin == blob | 说明 |
|---|---|---|---|
| E-AC1-READER-VM | `fb5065013` | ✓ `db99f3eb…` | 代码 pin，改为 blob(LF) 基准 |
| E-AC1-LIBRARY-VM | `fb5065013` | ✓ `bc651c56…` | 代码 pin，改为 blob(LF) 基准 |
| E-AC1-TEST | `fb5065013` | ✓ `135de02c…` | 原值即 LF 基准，未变 |
| E-AC1-TEST-FAKE | `fb5065013` | ✓ `c0c4822b…` | 代码 pin，改为 blob(LF) 基准 |
| E-AC1-DOC | `fb5065013` | ✓ `e913e2dd…` | 不变 |
| E-AC1-LOG | `fb5065013` | ✓ `1bb0ac36…` | **更新**（旧 pin 为 CRLF 工作树哈希） |
| E-AC2-DOC | `fb5065013` | ✓ `1edb35f1…` | 不变 |
| E-AC2-DATA | `fb5065013` | ✓ `e2106154…` | **更新**（旧 pin 为 CRLF 工作树哈希） |
| E-AC3-DOC | `fb5065013` | ✓ `9c27d477…` | 不变 |
| E-EVIDENCE-INDEX | `fb5065013` | ✓ `d199f484…` | 不变 |
| E-GOV-CHECK | `b94dc3d86` | ✓ `bc97d7a7…` | 原 pin 只在 blob 成立；现工作树亦 LF，双口径可复现 |
| E-RESOURCE-MANIFEST | `82e86e97b` | ✓ `133943d7…` | 不变 |

- **工作树口径复现**：8 条证据文件的工作树 SHA256 **8/8 与卡内 pin 相等**（`.gitattributes` 生效后 w/lf）。
- **代码 pin 的 blob 基准**：4 个代码/测试文件工作树仍是 CRLF（无 eol 规则），其 pin 是 blob 哈希 → 需 `git cat-file` 复现；本 Review 4/4 一致。与 SAFETY-7 卡 `:70` 声明的"blob（LF）基准"一致。
- **旧 pin 内容同一性复核（证明只是基准归一化、内容未改）**：对 5 条发生变化的 pin，把 `fb5065013` 的 blob 重新转成 CRLF 后取 SHA256，**5/5 与旧 pin 完全相等**（`E-AC1-READER-VM` `603ed15e…`、`E-AC1-LIBRARY-VM` `2b6f2525…`、`E-AC1-TEST-FAKE` `6c63c2c5…`、`E-AC1-LOG` `2eab8096…`、`E-AC2-DATA` `22f9793f…`）→ 本次 pin 变更是**纯行尾基准归一化**，代码/证据字节内容未改。

**SAFETY-7 自身（10/10 条一致）**：`E-AC1-READER-VM`/`E-AC1-TEST-FAKE`/`E-AC1-TEST`/`E-AC1-DOC`/`E-AC1-NEG`/`E-AC1-LOG`/`E-AC2-DOC`/`E-AC3-DOC`/`E-EVIDENCE-INDEX` @ `306ae09ae`、`E-RESOURCE-MANIFEST` @ `8a343d76f`，全部与 blob 一致；任务卡 `:70` 已声明 blob 基准（SAFETY-7 证据工作树中 `ac1-fix-tests.txt` 为 `w/crlf`，故只能按 blob 口径复现——与声明一致，不构成歧义）。

### 5.3 判定

**MET**。规则范围正确、证据内容未改、SAFETY-6 12/12 与 SAFETY-7 10/10 pin 均与 blob 字节一致，可在任意 checkout 用 `git cat-file` 复现。F-001 仅为证据文档的计数/表格不完整。

## 6. AC3（R-003 日志格式）判定：**MET**

| 要求 | `ac1-fix-tests.txt` 事实 | 判定 |
|---|---|---|
| ISO 时间戳 | `:2` `generated_at: 2026-11-01T01:29:21.6006025+08:00` | ✓ |
| host/shell 头 | `:3` `host: HOME-MY / pwsh 7.6.8` | ✓ |
| 完整命令 | `:5` build、`:15` test 两段 `## command:` | ✓（缺 cwd，见 F-003） |
| EXIT 码 | `:13` `EXIT=0`、`:21` `EXIT=0` | ✓ |
| 负向对照可复现步骤 | `ac1-negative-control.md:8-21` 4 步可执行脚本 | ✓（交付 head 上不可复现，见 F-002） |
| 原始输出 | build 摘要 + 测试摘要（`-v q` 口径） | △ 仅摘要；负向对照无原始输出尾巴与 `exit_code=` |

结论：**MET**（满足 AC3 字面），但证据强度仍弱于 R-003 原意（F-002/F-003）。

## 7. 复跑结果（真实执行）

环境：Windows / pwsh（本 Review 会话）；SDK `dotnet --version` = `10.0.401`；目标框架 net9.0。

| # | 检查 | 命令（cwd） | 执行时刻（+08:00） | 真实输出摘要 | EXIT |
|---|---|---|---|---|---|
| 1 | 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -v q --nologo`（worktree 根） | 2026-11-01T01:36:42 | `已成功生成。0 个警告 0 个错误；已用时间 00:00:04.73` | **0** |
| 2 | 全量测试 | `dotnet test tests/NewManga.App.Tests --nologo -v q`（cwd=`apps/desktop-avalonia`） | 2026-11-01T01:36:59 | `已通过! - 失败: 0，通过: 395，已跳过: 7，总计: 402，持续时间: 55 s` | **0** |
| 3 | 全量测试（复跑） | 同上 | 2026-11-01T01:42:53 | 同上（395/0/7/402，55 s） | **0** |
| 4 | 过滤测试 | `dotnet test tests/NewManga.App.Tests --nologo -v q --filter "FullyQualifiedName~LibraryProgressRefreshTests"`（cwd=`apps/desktop-avalonia`） | 2026-11-01T01:38:04 | `已通过! - 失败: 0，通过: 6，已跳过: 0，总计: 6，持续时间: 72 ms` | **0** |
| 5 | 过滤测试稳定性 | 同 #4，重复 5 次 | 01:38:04–01:39:2x | **5/5 全 PASS**（合计 6 次通过） | 0 |
| 6 | 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REALUSE-DATA-SAFETY-7.md`（worktree 根） | 2026-11-01T01:38:11 | `Governance check: PASS (3 warnings)`；warnings：7 个非终态 Task、`STATUS.md` 预算 80%（3011 bytes/31 lines）、`REBASELINE_PLAN.md` 预算 80%（6624 bytes/59 lines） | **0** |

- **与交付证据一致性**：build 0/0、全量 395/0/7/402、filtered 6/6、check PASS 全部一致；本次 check 为 3 warnings（证据未记录 warning 数，仍为 PASS）。
- **路径说明（同时是 F-003 依据）**：任务书写 `dotnet test tests/NewManga.App.Tests`；在 worktree 根执行会 `MSB1009: 项目文件不存在`（EXIT=1），必须在 `apps/desktop-avalonia` 下执行。交付日志同样未记录 cwd。

## 8. 负向对照独立复现（仓外，未触碰仓库）

- **隔离方式**：`robocopy` 复制 `apps/desktop-avalonia`（排除 `bin/obj/.vs`）到 `G:\CODEX\New Manga.workspace\tmp\safety7-review\negctl`，另复制根相对引用文件 `doc/design/redesign-v1/40-fusion/tokens.json`；用 `git cat-file blob 29d06c462:apps/.../ReaderOverlayViewModel.cs` 覆盖生产文件（**保留** `FakeHostController` gate 与新测试）；未在仓库内执行 `checkout`/`apply`。
- **执行**：`dotnet build NewManga.sln -v q --nologo` → `已成功生成。0 个警告 0 个错误`，EXIT=0；`dotnet test ... --filter "FullyQualifiedName~ClosingWhileSaveInFlight"` → `失败! - 失败: 1，通过: 0，已跳过: 0，总计: 1`，**EXIT=1**。
- **失败形态**（详细日志）：`System.NullReferenceException : Object reference not set to an instance of an object.` 堆栈：
  `ReaderOverlayViewModel.SaveProgressAsync(Boolean isClosing) ... ReaderOverlayViewModel.cs:line 377` ←
  `ReaderOverlayViewModel.GoToAsync(Int32 index) ... ReaderOverlayViewModel.cs:line 308` ←
  `LibraryProgressRefreshTests.ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection() ... LibraryProgressRefreshTests.cs:line 284`。
- **稳定性**：quiet 模式复跑 3 次均 `失败: 1`、EXIT=1 → 用例对修复有判别力，修复确实是 NRE 消失的原因。
- **结论**：交付证据 `ac1-negative-control.md:25-26` 声称的"1 失败 / 0 通过，EXIT=1"与失败用例名 **属实**；但其"可复现步骤"在交付 head 不可复现（F-002）。
- 该临时副本已在收尾时删除（DELETE_SAFE，仅含本 Review 派生内容）。

## 9. 数据安全与仓库状态

| 检查 | 事实 | 判定 |
|---|---|---|
| 用户数据写 | branch diff 仅 `.gitattributes`、3 个源码/测试文件、3 个 doc、7 个新证据；无 `data/**`、SQLite、Python、迁移、安装脚本；SAFETY-6 真实数据证据 blob 未变 | 无写 ✓ |
| 迁移/契约 | 无 `doc/contracts/**`、无 `IHostController` 接口变更、无 schema 改动 | 无 ✓ |
| push | 分支无 upstream；`git for-each-ref refs/remotes` 无 SAFETY-7；`git ls-remote origin "refs/heads/task/REALUSE-DATA-SAFETY-7"` 空输出（EXIT=0）→ 远端不存在该分支 | 无 push ✓ |
| main 工作区 | `git -C "G:\CODEX\New Manga" status --porcelain` = `?? doc/handoffs/NIGHT-SHIFT-2026-11-01.md`（唯一的 untracked，Lead 夜班产出，01:34:14；非本 Task 提交）；无 tracked 变更；main HEAD 仍 `29d06c462` | tracked 未改 ✓（untracked 见 O-3） |
| 资源收口 | `tmp/safety7-negctl` `Test-Path=False`（与 `resource-manifest.json` 的 `deleted=true` 一致）；worktree 存在且被任务卡引用 | 一致 ✓ |
| 审查隔离 | 本 Review 未在仓库内做 `add/commit/checkout/stash/merge/apply`，未 push；唯一写入为本文件 | ✓ |

## 10. 独立性声明与 NOT_RUN

- **独立性**：本 Review 由 `safety7-reviewer`（Agent Teams fresh context `task-4`）执行，**未参与** REALUSE-DATA-SAFETY-7 的实现、返修或证据生成；独立上下文、只读被审 head；负向对照只在仓外副本进行。仓库内唯一写入为 `doc/reviews/REALUSE-DATA-SAFETY-7-review.md`（本文件）。
- **审查前后 git status（worktree）**：
  - 审查前（2026-11-01T01:34）：HEAD `58596949a`，`git status --porcelain` **空**（clean）；
  - 审查后（写入本文件前）：`git status --porcelain` **空**（build/test 产物均在 `.gitignore` 内）；
  - 写入后：仅 `?? doc/reviews/REALUSE-DATA-SAFETY-7-review.md`（本 Review 唯一仓库内写入）。
  - main 工作区审查前后一致（仅 O-3 的 untracked 文件，非本次审查产生）。
- **NOT_RUN**：
  1. 生产 Host IPC / 真机端到端（本 Review 只跑 headless Avalonia 测试与 Fake Host，未启动真实 Core 服务）；
  2. 关闭时延量化（O-2，沿袭 SAFETY-6 Review O-1）；
  3. 在干净 clone（`core.autocrlf=false` / Linux）上验证 LF 检出效果（结论由 `.gitattributes` 规则 + blob/工作树 hash 一致性推得，未实际换环境）；
  4. main 集成后的 build/test/check（属 DSH 集成验证职责，本 Review 只审 worktree head）；
  5. SAFETY-6 全量回归复跑（超出本 Task 范围，未重跑）。

## 11. 剩余风险与建议

1. **F-001**：修正 `ac2-eol-pin.md` 的计数（应为 12 条 pin / 5 条变化，或明确口径）并补 4 条代码 pin 的 old→new；由 Lead 确认 AC2 文本改写属授权范围。
2. **F-002/F-003**：把负向对照配方改为 post-delivery 可执行版本并附原始输出/`exit_code=`；日志补 cwd 与 filtered 段。若不在本 Task 范围，建议并入紧随的治理小项（与 SAFETY-6 R-003 同类）。
3. **F-004/F-005**：可在同一分支小修（限定捕获类型 + closing 期间阻止新保存），但不阻断集成；若延后，建议登记为后续项。
4. **O-3**：Lead 收口 main 工作区的 untracked `doc/handoffs/NIGHT-SHIFT-2026-11-01.md`。
5. **集成注意**：`.gitattributes` 合并到 main 后，main 上 SAFETY-6 证据目录的**存量工作树**需要重新检出（`git checkout --` 或重新 clone）才变为 LF；pin 的 blob 口径此前已可复现，合并后新增"工作树口径"可复现能力。集成后请在 main 复跑 build/test/check 并写入集成证据。

---

**Fixed head review**：`reviewed_head = 58596949a` 可交 DSH 集成；P0/P1 = 0，5 条 P2 见 §3。后续 head 变更或新 Review 出现后，本文件自动转为历史记录，不得覆盖。
