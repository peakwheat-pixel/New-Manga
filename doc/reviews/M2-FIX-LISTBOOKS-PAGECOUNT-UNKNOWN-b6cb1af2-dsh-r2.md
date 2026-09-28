approved_with_conditions

**复核范围与手段说明（影响证据强度，先声明）**：本会话 `pwsh` 沙箱初始化失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，前台/后台、`$env:TEMP` workdir 均失败，升级需审批但无审批通道），**无法执行任何 git 命令**。本轮为「纯静态读文件 + Git 元数据直读（`.git/worktrees/.../HEAD`、`.git/refs/heads/...`、`.git/logs/refs/heads/...` reflog）」。因此 commit 区间 diff 类结论只能给到「内容层一致」而非「区间 diff 为空」，对应项列入 not_verified。

---

## 0. r2 tip / ledger 身份核对（reflog 实证）

`G:\CODEX\New Manga\.git\logs\refs\heads\agent\zcode\M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`

| # | reflog 事件（time=ref 更新时间） | 本地时刻（+0800，按 epoch 换算） |
|---|---|---|
| 1 | 分支创建于 `a2380706`（release） | 02:04:09 |
| 2 | `2210d642` claim | 02:07:06 |
| 3 | `852a92ae` 交付（=delivery_head） | 02:15:21 |
| 4 | `10dbc100` 回填 → `bee7bf59`（amend） | 02:17:38 |
| 5 | `f4f77808` **r2 原 commit**（无 amend 标记） | 02:33:11 |
| 6 | `c3f8bb3a` amend #1 | 02:34:42 |
| 7 | `b6cb1af2` amend #2 = **当前 HEAD** | 02:35:19 |

- Owner 声称的 ledger（claim `2210d642` → 交付 `852a92ae` → 回填 `bee7bf59` → r2 `b6cb1af2`）与 reflog **一致**；`.git/refs/heads/...` 内容 = `b6cb1af2299b887461e1e7b2914b7577f8a6871c`，与「r2 tip=当前 HEAD」一致。
- 时间线与各 raw 日志头戳自洽（例：`raw/scope-and-diff-check.log:3` 02:15:44 紧接交付 02:15:21；`raw/final-tip-rerun.log:4` 02:17:45 对应 head=`bee7bf59`；`raw/r2-final-bind-rerun.log:6` 02:33:28 对应 run-at=`f4f77808`）——各 head 戳**未发现伪造迹象**。
- **但**：`b6cb1af2` 全仓不可解析（见 P2-1）。

---

## 1. C1 逐条核对 —— **通过**

| 子项 | 判定 | 证据 |
|---|---|---|
| 新用例存在且承重（0→`页数: 0`） | 通过 | `apps/desktop/frontend/src/library/LibraryPanel.test.tsx:60`（用例名逐字相符）、`:71`（`page_count: 0`）、`:82`（`expect(html).toContain("页数: 0")`） |
| 反向断言（不得是占位符） | 通过 | `LibraryPanel.test.tsx:83`（`not.toContain("页数: —")`）；与 `:56` null 用例的正反两向互锁 |
| 变异红证「恰该用例红」 | 通过 | `raw/npm-vitest-known0-mutation-red.log:6`（mutation 行逐字记录 `||`）、`:14`（`8 tests | 1 failed`）、`:15`（失败用例名 = 新用例）、`:16/:21/:23`（`Expected "页数: 0"`）、`:24`（Received 实渲染 `页数: —`）、`:26`（红点 `test.tsx:82:18`）、`:37`（`1 failed | 7 passed`）、`:41`（`EXIT=1`）。24 页与 null 两用例保持绿——**变异只被新用例拦截**，判别力成立 |
| 还原绿证 | 通过 | `raw/npm-test-after-known0-case.log:17`（`LibraryPanel.test.tsx (8 tests)` 全绿）、`:19-20`（5 files / 31 tests passed）、`:24`（`EXIT_TEST=0`）、`:31`（34 modules）、`:37`（`EXIT_BUILD=0`）；计数算术自洽：3+4+8+8+8=31 |
| `??` 在位（非 `||`） | 通过 | `apps/desktop/frontend/src/library/LibraryPanel.tsx:145`：`` {`页数: ${book.page_count ?? "—"}`} `` |

结论：C1 的「正向用例 + 变异红 + 还原绿 + 无残留」四件套**真实关闭**，且新用例对 `||` 陷阱具承重判别力（r1 的 4 条 P2 中 P2-1 由此关闭）。

---

## 2. C2 逐条核对 —— **通过（附带 2 条 P3 文档瑕疵，不改变通过判定）**

### ① 测试文件模块 docstring 陈旧句 + 零断言改动 —— 通过
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:36-43`：F-1/F-2 两条 marker 均写明「removed once … turned the scenario green/PASS」，并落 `:43`「as of this suite the tree carries no xfail markers at all (DSH r1 P3-2)」——陈旧句已更新，且给出了与事实相符的收口口径。
- 全仓 xfail 残留核实：该文件仅 `:32`（通用约定说明）、`:43`、`:867`（F-2 函数 docstring 史实说明）三处**文字**命中，`@pytest.mark.xfail` **零命中**，与 `35 passed, 0 xfailed` 一致。
- 「零断言改动」的部分独立证据：`raw/red-run-f2-before-fix.log:13-45` 内联了 pre-r2（head=`2210d642`）的 `test_ac4_books_without_pages_are_not_presented_as_zero` 源码，与当前 `:862-894` **逐字一致**（含 docstring 与三段断言）→ 该函数在 r2 未被改动。其余函数只能靠 r2 日志计数（35 passed）与内容比对，见 not_verified。

### ② 契约 §3.2 授权例外指针 + Revision 1.2 日期 —— 通过
- 指针：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:88`「**例外**：经授权 Task 在 Revision history 登记的 nullability widening（`T → T | null`）不升 major，现仅有 §5 `ListBooks` 的 `BookSummary.page_count`（`1.2` 修订，[M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](...））」——与 `:86-87` 的 major/minor 规则衔接，未放宽其他字段。
- 日期：`:7` `1.2`（…，**2026-09-29**）；`:3` 头部版本 `1.2`；`:105` §5 ListBooks 行同步。日期与交付/返修实际发生时间（2026-09-29 02:0x–02:35 +0800）一致。
- 无越权：契约改动仅为 `:7`（Revision history 1.2 条目）、`:88`（§3.2 一行）、`:105`（§5 行）与 `:3` 头部，属 Task:58 允许的「最小修订」。

### ③ verification-results.md 索引完整性 —— 通过
覆盖度逐节核对：`§1` ledger（:10-17）、`§2` 先红（:19-23）、`§3` r1 四套 + flaky 事件（:27-35）、`§4` AC1–AC6 判定（:39-46）、`§5` r2 返修表（:48-55）、`§6` head 戳绑定说明（:57-60）、`§7` 范围自检（:62-66）、`§8` 遗留（:68-72）。未见空引用（所有 raw 链接指向真实存在的文件，glob 已确认 8 个 raw 日志 + release + 本文件全部在位）。瑕疵见 P3-1/P3-2。

### ④ 新 raw 日志头尾纪律 —— 通过
| 日志 | 头（shell/解释器/head/ISO/目的/命令） | 尾 EXIT |
|---|---|---|
| `raw/npm-vitest-known0-mutation-red.log` | :1-7（含 mutation 行逐字记录） | :41 `EXIT=1` |
| `raw/npm-test-after-known0-case.log` | :1-6 | :24 `EXIT_TEST=0`、:37 `EXIT_BUILD=0` |
| `raw/r2-final-bind-rerun.log` | :1-7（shell/python/cargo/node/head(run-at)/time/purpose） | :12/:63 `EXIT=0`、:72 `DIFF_CHECK_EXIT=0`、:137 `EXIT=0`、:156 `EXIT_TEST=0`、:167 `EXIT_BUILD=0` |

四套实测值与声明逐一吻合：35 passed（:11）、77 passed（:17）、`33 passed; 0 failed`（:135，含 `book_summary_page_count_known_zero_and_null_are_distinguishable` :105、`f02_...` :120 绿）、vitest 5 files/31 tests（LibraryPanel 8，:149-152）+ build 34 modules（:161）、`git diff --check 6199df48..HEAD` 空（:71-72）。三条 `EXIT=1` 已逐行 `ABORTED INVOCATION` 括注（:66/:68/:69）并给出有效 rerun（:74）——**中止调用未冒充结果**，披露诚实。另抽查 `raw/scope-and-diff-check.log:1-3`（head/base/time 头）与 `raw/red-run-f2-before-fix.log:1-5`，纪律同构。

### Handoff 侧（C2 附带）
- 「交付 tip」→「交付树」表述与 head 戳说明：`doc/handoffs/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-owner-delivery.md:43`（表注逐字更正为「工作树等价于 `852a92ae`，日志 head 戳 `2210d642`（交付前）」），表内 `:34-38` 均已加 `交付树*`。
- NOT_RUN 小节：`:58-64`（Rust 真通道端到端、TS known-0 补齐说明、交付 commit 级绑定复跑、f02 flaky 复跑口径、`Any` 导入来源）——与 r1 C4 的预置要求一致，且 P3-1/P3-6 诚实标注为「未覆盖 / 留集成方」。

---

## 3. r1 六轴正面结论抽查（r2 delta 是否仅测试/文档/日志）—— 仍成立（1 项降级为内容层一致）

| 轴 | 现状核对 |
|---|---|
| ① None 通道三侧一致 | `src/bootstrap/core_service.py:121`（`page_count: int | None`）、`:169`（`page_counts.get(book.book_id)`，无默认 0）；`apps/desktop/src-tauri/src/library_bridge.rs:35`（`Option<u32>`）；`apps/desktop/frontend/src/library/types.ts:23`（`number | null`）；`LibraryPanel.tsx:145`（`?? "—"`）——与 r1 描述逐项一致 |
| ② known-0 单测有效性 | Python `tests/core/test_core_service.py:533-571`（`"page_count": 0` ≠ `"page_count": null`）；Rust `library_bridge.rs:387-417`（双向 serde round-trip）；TS `LibraryPanel.test.tsx:60-85`（r2 补齐）→ 三侧对称**已闭合** |
| ③ 先红真实性 | `raw/red-run-f2-before-fix.log:46-53`（`page_count=0` / `page_count_known=None` / `assert False` / `EXIT=1`），红点 `:886` 与当前 `:890` 断言同行；未被 r2 触碰 |
| ④ corrupt 断言更新口径 | `test_...py:916-920`（`real_count == 1` 且 `summary == 1`）、`:931-936`（`real_count == 0` → `page_count is None`），与 Handoff 偏差 1 口径一致；r2 未再动 |
| ⑤ f02 flaky 判定 | 与 r2 无关；r2 复跑 `raw/r2-final-bind-rerun.log:120`（`f02_equal_size_rewrite_after_first_verify_rejected ... ok`）、`:135` 33 passed，方向一致 |
| ⑥ head 戳/范围 | r2 修正了表述（Handoff:43、verification-results §6）并补了 commit 级绑定复跑；**但最终 tip 的绑定链不完整** → P2-1 |

补充交叉验证（新做）：无任何 runner/期望值 pin 住前端用例数（`verification/M2-RC2/run_e2e.py`、`verification/M2-AC1/run_e2e.py:135` 仅调 `npm run build`，无 vitest 计数断言），故 7→8 的用例增量**不会**击穿其他 Task 的 gate。

---

## 4. 新增问题

### P2-1｜最终 r2 tip 无绑定日志；amend 轨迹未登记，且 tip hash 在本仓不可解析
- 事实：绑定复跑日志 `raw/r2-final-bind-rerun.log:5` 的 `head (run-at)` = `f4f77808`，而落地 tip = `b6cb1af2`（reflog 第 6/7 行，两次 amend：`f4f77808 → c3f8bb3a → b6cb1af2`）。`verification-results.md:60` 只披露**一次** amend（「本日志自身经 amend 并入，被验树与最终 r2 tip 的差集 = 本日志文件」），未覆盖第二次 amend。
- 连带：`doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md:17` `delivery_head` 仍为 `852a92ae`；`:69` 与 `verification-results.md:17` 均以「hash 见 `git log` / 日志头 run-at 戳」代替具体 hash，而该指向实际给出的是**前身** `f4f77808` 而非最终 tip → 仅读仓库文件无法解析 r2 tip。
- 影响与处置：不构成功能风险（集成方 C3 本就要求在集成 head 复跑），但按本仓先例（M2-FIX-EXPORT-LINEAGE r1 P1-1「交付 tip 无绑定日志、amend 轨迹未披露」→ r2 以 §9.1 逐条登记关闭），应在**同一份证据文档内**登记 amend 轨迹（前身 hashes + 每次差集）或由集成记录承接。
- 复核命令：`git diff --stat f4f77808..b6cb1af2`、`git diff --stat f4f77808..c3f8bb3a`（验证「差集=本日志文件」是否成立）。

### P3-1｜`verification-results.md:16` 的括注与日志时间线互相矛盾
- 该行称 `final-tip-rerun` 日志「实际随 #3（`bee7bf59`）提交」；但该日志头 `raw/final-tip-rerun.log:4` = `2026-09-29T02:17:45+08:00`，而 `bee7bf59` 的 ref 更新时间（reflog 第 4 行）换算为 **02:17:38**——文件内容不可能早于其自身头部时间进入更早的 commit。这与 Owner 自己的偏差说明「`final-tip-rerun.log` 漏提交已补」一致，即该日志实随 r2（#4）落盘；`§1 #3` 括注应删或改。
- 复核命令：`git log --diff-filter=A --format='%h %cI' -- verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/raw/final-tip-rerun.log`。

### P3-2｜「零残留」证据指针不实（指向的 raw 尾部无命令输出）
- `verification-results.md:53` 写「`||` 还原 `??`（`git diff --stat` 对该文件为空 = 零残留，**见日志尾**）」；`raw/npm-test-after-known0-case.log` 尾部只有一行**自述**括注 `:38`「(empty diff-stat above = zero residual mutation in LibraryPanel.tsx)」，其上并无任何 `git diff --stat` 输出。零残留结论本身可信（`LibraryPanel.tsx:145` 现为 `??`，且 r2 复跑 `git diff --check` EXIT=0），但指针应改指 `r2-final-bind-rerun.log` 或补采一次 diff 输出。

### P3-3｜r1 报告未归档，P 编号不可解析
- `doc/reviews/` 下无 `M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-*-dsh-r1.md`（glob 全仓无命中；grep `approved_with_conditions` 命中的是本 Task 自身的 Task/Handoff/verification 文件）。Task:69、Handoff:27、`verification-results.md:8` 引用的「DSH r1 P2-1/P2-2/P3-2/P3-5」等编号在仓库内**无对应原件**。建议集成方随本次 r2 报告一并归档 r1/r2 报告（Task:76 已把 `doc/reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-*/**` 列入允许路径）。

### P3-4｜Task AC6 文本仍是旧 tip
- `Task:51` 仍写 `git diff --check 6199df48..852a92ae`；r2 期复验在 `raw/r2-final-bind-rerun.log:71-72` 与 `verification-results.md:60`，但 AC 文本未随 tip 更新（历史口径可保留，但需在回填时并注 r2 tip 口径）。

---

## 5. not_verified（给命令；本会话 shell 被沙箱拒绝，未执行）

1. `git diff --name-status bee7bf59..b6cb1af2` 与 `git diff --stat bee7bf59..b6cb1af2` —— 独立复核「r2 delta 仅测试/文档/日志、`src/` 零改动」（本次仅做到内容层比对：`core_service.py:121/169`、`library_bridge.rs:35`、`types.ts:23`、`LibraryPanel.tsx:145` 与 r1 描述一致；`test_...py:862-894` 与 pre-r2 红证内联源码逐字一致）。
2. `git diff --stat f4f77808..b6cb1af2` —— 验证 P2-1 的「差集 = 本日志文件」。
3. `git log --diff-filter=A --format='%h %cI' -- verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/raw/final-tip-rerun.log` —— 关闭 P3-1。
4. `git status --porcelain` + `git diff --check 6199df48..b6cb1af2` —— 工作区/整树洁净与 EXIT=0（r2 日志给的是 `6199df48..HEAD`@`f4f77808` 口径）。
5. 套件复跑（`"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q` / `-m pytest tests/core -q` / `cargo test --bin m2rc1-desktop`（cwd=`apps/desktop/src-tauri`，前置 `npm run build`）/ `npm test`）—— 未由本 Reviewer 独立执行，采信 `raw/r2-final-bind-rerun.log`。

---

## 6. 最终推荐

**C1 = 通过；C2 = 通过**（两条件均真实关闭，无 P0/P1，无 src 语义变更迹象）。新增 1×P2（最终 tip 绑定/amend 轨迹）+ 4×P3（均为文档/证据指针级）。

- **可进入集成**，无需 Owner 代码返修。
- 新增**条件 C5（doc-only，可在集成记录内关闭）**：登记 r2 amend 轨迹（`f4f77808 → c3f8bb3a → b6cb1af2` 及每次差集）并把最终 tip hash 落到 `verification-results.md §1 #4`/Task 回填；同时修正 `§1 #3` 的 `final-tip-rerun` 括注（P3-1）与「见日志尾」指针（P3-2）。
- 原 r1 条件 **C3**（集成 head 复跑）与 **C4**（范围/遗留登记）**不变，仍归 Codex（Integrator，保持 Owner≠Integrator）**；由于最终 tip 无绑定日志，C3 的复跑在 P2-1 关闭前是唯一有效的 tip 级证据，不可省略。建议集成方同时归档 r1/r2 报告（P3-3）。
