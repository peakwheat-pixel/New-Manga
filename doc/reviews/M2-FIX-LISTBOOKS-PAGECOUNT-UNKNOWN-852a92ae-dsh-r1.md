approved_with_conditions

> 非作者静态 Review（无 shell，未运行任何测试/构建/git；文中 `verified-by-reading` = 从交付树文件与 raw 日志内容交叉核对得出；`not_verified` = 需集成方代跑）。被审对象：`agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`，base `6199df48` → delivery `852a92ae`（回填 tip `bee7bf59`）。

## 0. 六轴核对（verified-by-reading）

| 轴 | 结论 | 关键证据 |
|---|---|---|
| 1 None 通道三侧一致性 | **PASS（跨边界 E2E 缺失见 P3-1）** | `src/bootstrap/core_service.py:121` `int \| None` + `:169` `get(book_id)` + `:366` `json.dumps` ⇒ `null`；`library_bridge.rs:35` `Option<u32>`（`None`→`null`，由 `:402-417` 实测断言）；`types.ts:23` `number \| null`；`LibraryPanel.tsx:145` `?? "—"`（非数字） |
| 2 known-0 硬约束 | **Python/Rust PASS；TS 正向未锁 → P2-1** | 生产 SQL 为 **INNER JOIN + GROUP BY**（`:180-190`）⇒ 每个返回组至少 1 行、`COUNT(p.page_id)≥1`；即使 `page_id` 可空产生 0，`.get()` 无默认值也把 0 原样带出（`get` 与「行不存在→None」互斥）⇒ **不存在「行存在且 count=0 却被转 None」的路径**；Python `test_core_service.py:564-573`、Rust `library_bridge.rs:404-417` 双向锁定 |
| 3 契约修订最小性 | **基本 PASS，2 处见 P2-2/P3-3** | `M2-C1_TYPED_IPC_CONTRACT.md:3`（版本 1.2）、`:7`（Revision history）、`:105`（§5 ListBooks 行内追加）；`raw/prod-sql-copy-sync-check.log:6-35` 给出 `core_service.py` 对 base 的**完整 diff = 仅 2 个 hunk**（DTO 类型 / handler 取值），命令面未动；`raw/cargo-test.log:41` `production_surface_is_exactly_five_commands ... ok` |
| 4 测试更新口径 | **PASS** | corrupt 断言更新（`test…:929-932`）是「SQL 无行→None」冻结语义的必然结果，`real_count == 0`（`:928`）与 title/收藏字段不伪造（`:933-935`）保留；`_PRODUCTION_COUNT_SQL`（`:124-134`）六条谓词与 production `:183-188` 逐条一致；先红日志（`raw/red-run-f2-before-fix.log:46,49,52`，红点 `:886` + `assert False` + `EXIT=1`）的测试内容/行号与交付测试逐行一致（`test…:886-890`），修红唯一变量 = src |
| 5 flaky 判定 | **代码路径不相交 PASS；证据链偏弱 → P3-4** | f02 在 `main.rs:798-826`（资源通道 equal-size 重写 + mtime/digest 重验证），新增 Rust 测试 `library_bridge.rs:386-418` 为纯内存 serde，零共享状态（每测试独立 `tempfile::tempdir`，`main.rs:446-460`）；但首跑失败无 raw 留存、base 仅单跑 f02 |
| 6 范围与证据纪律 | **部分 PASS，见 P2-3/P2-4/P3-5/P3-6** | 数字独立静态复核全部自洽：`tests/m2_acceptance` 恰 35 个 `def test_`（=35 passed）；`tests/core` 73 `def test_` + 4 类内方法 = **77**；Rust `#[test]` 恰 **33**（`main.rs` 19 + `library_bridge.rs` 5 + `ac1_bridge.rs` 3 … 与 `cargo-test.log:33-68` 33 项一一对应）；vitest `it(` 恰 **30**（8+8+7+3+4）与 `npm-test-and-build.log:13-20` 完全吻合；test/m2_acceptance 全树已无任何 xfail 标记 |

**没有 P0/P1。** 交付主体（三层 None 通道 + known-0 保留 + SQL 零改动 + 契约修订 + 先红后绿）经静态核对成立，问题集中在 TS 正向锁定缺失与证据纪律。

## 1. 分级问题清单

### P0
无。

### P1
无。

### P2

**P2-1｜TS 侧「known 0 正向渲染」零锁定，`??`→`||` 变异可整体逃逸（硬约束的 UI 腿未闭合）**
- 位置：`apps/desktop/frontend/src/library/LibraryPanel.tsx:145`；`apps/desktop/frontend/src/library/LibraryPanel.test.tsx:34-58`（`page_count: null`）、`:8-32`（`page_count: 24`）。
- 证据：现有 7 条用例只覆盖 `null→"页数: —"`（`:55-56`）与 `24→"页数: 24"`（`:28`），**没有 `page_count: 0` 用例**。把 `??` 改成 `||`（JS falsy 陷阱）后，`null→"—"`、`24→"24"` 仍全绿，而 `0` 会被渲染成 `"—"`——即「SQL 数出的 0」在 UI 层被吞成 unknown，正是本 Task 冻结的硬约束（`doc/tasks/…:40`）的反面。
- 说明：这**满足 AC2 的字面要求**（AC2 括号内只点名「TS UI 占位锁定」，`doc/tasks/…:47`），但 Python/Rust 两侧都做了 0/null 双向锁定（`test_core_service.py:564-573`、`library_bridge.rs:404-417`），TS 侧只有单向，三侧不对称。
- 建议：新增一条 `page_count: 0` → `expect(html).toContain("页数: 0")` 且 `not.toContain("页数: —")`。

**P2-2｜契约 §3.2「类型变化 = major 变更」与 1.2 的 minor 修订并存，正文未落例外指针**
- 位置：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:88`（§3.2「字段删除、改名、**类型变化**、枚举旧值语义变化或必填性变化属于 major 变更」）对比 `:3`、`:7`、`:105`（1.2 以 minor 修订 `int → int|null`，仅以「§3 版本规则下属类型变化，由本授权 Task 承接」一句带过）。
- 证据：`:7` 自述 tension 存在，但 §3.2 条文本身未加指针/例外注记；envelope 的 `version.minor` 仍为 `0`（`core_service.py:42`、`library_bridge.rs:183`）。
- 影响：仅读 §3.2 的下一位契约消费者会判定当前契约自相矛盾（minor 内发生 breaking 变更）。旧读者（1.1 版 `number`）遇到 `null` 会静默坏掉。
- 建议（二选一，均为文档层最小改动）：在 §3.2 增一行「经授权 Task 登记的 nullability widening 不升 major」指针，或在 §5 ListBooks 行内显式登记该例外。**不建议**为此改 `version.minor`（超出本 Task 冻结面）。

**P2-3｜`verification-results.md` 缺失，与全部 M2-FIX-* 先例及本次 Review 输入清单不符**
- 位置：`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/` 下只有 `release-6199df48.md` + `raw/*.log`（glob 实测）；对比 `verification/M2-FIX-EXPORT-LINEAGE/verification-results.md`、`verification/M2-FIX-STUB-DECODER/verification-results.md`、`verification/M2-IPC1/verification-results.md` 均存在。
- 证据：Task AC6 只要求「命令日志带 shell/解释器/固定 HEAD/ISO 时间/EXIT」（`doc/tasks/…:51`，raw 已满足），但本次派单把 `verification-results.md` 列为审查输入之一——说明派单方预期该索引文件存在。
- 影响：验收数字目前只能靠 Handoff 表格（`doc/handoffs/…-owner-delivery.md:31-40`）+ 7 个 raw 日志重建，索引与「哪条命令对应哪条 AC」的映射缺一个稳定落点。

**P2-4｜Rust/前端验证未绑定到交付 commit（Handoff 标「交付 tip」但日志 head = `2210d642`），仅 pytest 在 tip 复跑过**
- 位置：`raw/cargo-test.log:3` `head: 2210d642…`、`raw/npm-test-and-build.log:3` 同；`doc/handoffs/…:37-38` 两行均写「交付 tip」；`raw/final-tip-rerun.log:3-15` 的 tip 复跑只含 `pytest tests/m2_acceptance` 与 `pytest tests/core`（head = `bee7bf59`），**不含 cargo/vitest**。
- 证据：`raw/final-tip-rerun.log` 明确「code identical to delivery 852a92ae」，但这是叙述而非证据；`cargo-test.log`/`npm-test-and-build.log` 的 HEAD 戳（2210d642）早于交付 commit（`raw/scope-and-diff-check.log:34` 记录 delta `2210d642..852a92ae`）。
- 影响：内容层可确认日志确实对应交付树（`cargo-test.log:40` 含新增用例名、`npm-test-and-build.log:17` LibraryPanel 7 tests 与当前 `LibraryPanel.test.tsx` 7 条 `it` 一致、Rust `#[test]` 33 与日志 33 项一致），但**「被验证的树 = 被提交的树」缺一个 commit 级绑定**；AC6 的「固定 HEAD」在 Rust/前端两条线上没有落到交付 SHA。

### P3

**P3-1｜None 通道缺一条真正的跨语言端到端证据**
- 位置：`apps/desktop/src-tauri/src/main.rs:957-998` `real_library_sidecar_round_trip_and_eof` 只对**空库**断言 `books.is_empty()`（`:988-989`）；`tests/m2_acceptance/…:302-307` 的 `_list_books` 直接调 `handle_list_books` 拿到 Python dict（**未过 `json.dumps`**，`core_service.py:366`）。
- 影响：现状 = 「Python 侧 null」与「Rust 侧能把 null 解成 `None`」各自单测成立，但「Python 真进程发出的 `"page_count":null` 被 Rust `Option<u32>` 接住」这条线无判别用例。若未来 Rust 侧退回 `u32`，现有 33 个 Rust 测试与 35 个验收测试**全绿**。
- 建议：在 `real_library_sidecar_round_trip_and_eof` 里 seed 一本无页书，断言 `page_count == None`（成本 1 条）。

**P3-2｜冻结验收套件的模块级 docstring 仍写「F-2 remains xfail(strict=True)」**
- 位置：`tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:39`（「F-2 (page_count unknown semantics) remains xfail(strict=True).」）；函数级 docstring 已更新（`:863-868`）。
- 影响：`tests/` 全树已无任何 xfail 标记（grep 实证），该行成为套件自述与事实相反的陈旧登记，恰好落在本 Task 显式授权修改的文件里；Handoff 自称「F-2 xfail 移除 + docstring」（`doc/handoffs/…:23`），实际只改了函数级。

**P3-3｜契约 1.2 修订记录日期与释放/交付日期不一致**
- 位置：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:7` 写 `2026-09-28`；实际释放/交付为 2026-09-29 02:0x–02:15（`verification/…/release-6199df48.md:3`「2026-09-29 02:3x」、`raw/scope-and-diff-check.log:3` `2026-09-29T02:15:44+08:00`、`doc/tasks/…:7` `released_by_orchestrator_2026-09-29`）。

**P3-4｜f02 flaky 判定证据链偏弱（结论方向我认同，但支撑不足）**
- 位置：`raw/cargo-test.log:73-85`（FLAKY INCIDENT RECORD）；失败首跑本身**没有 raw 日志留存**（只有散文复述「32 passed; 1 failed … EXIT=101」），而该文件里的 `### RUN 1` 实际是全绿那次（`:8,33,68`），标签易误读；base 复证只有「f02 单跑 PASS」（`:79-80`）——这与「默认线程并发 flaky」不是同一条件，最接近的可比条件应是 base 全量默认线程跑。
- 静态评估（支持「与本修复无关」）：f02 机制 = 等长原地重写后靠 **mtime/digest 重验证**判 400/200（`main.rs:798-826`、`resource_protocol.rs:426-436`），与 `library_bridge.rs:26-38` 的类型改动零交集；新增 Rust 测试纯内存无共享状态。但「新增第 33 个并行测试会改变调度/负载、可能**暴露**既有潜伏 flake」这一路径无法排除（不是本修复引入，但不能说「完全无关」）。

**P3-5｜允许路径字面缺口：前端测试文件未列入允许范围**
- 位置：`doc/tasks/…:57` 只列 `types.ts`、`LibraryPanel.tsx`（对比 `:56` 对 Rust 明写「含其测试文件」、`:60` 对 `tests/core/` 整体授权、`:59` 对验收文件显式授权）；实际 delta 含 `apps/desktop/frontend/src/library/LibraryPanel.test.tsx`（`raw/scope-and-diff-check.log:6`）。
- 影响：AC1 本身要求「vitest 用例锁定不渲染 0」（`:46`），故该编辑是 AC 的必然要求，但范围自检结论「owner delta 全落允许路径」（`:51`）在字面上对这一个文件不成立。

**P3-6｜无 NOT_RUN 小节；`Any` 未导入疑点**
- 位置：Handoff 无 NOT_RUN 章（`doc/handoffs/…` 全文）；`tests/core/test_core_service.py:394` 使用 `Any` 但全文件无 `from typing import Any`（grep 仅命中该行）。
- 说明：`from __future__ import annotations`（`:7`）使注解不求值，故运行期无碍、77 passed 不受影响；仓库无 mypy/pyproject 配置（仅 `pytest.ini`），属潜伏项。**无法静态判定是否为本次修改误删**（owner 本次在该文件新增 `from dataclasses import asdict` 于 `:34`），需与 base 对比（见 not_verified）。

## 2. not_verified 清单（需集成方代跑，均只读或可还原）

设 `$py = "G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe"`；工作目录 `G:\CODEX\New Manga.worktrees\M2-FIX-LISTBOOKS-zcode`。

1. 契约修订最小性（P2-2 定级依据）：
   `git diff 6199df48..852a92ae -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
   期望：仅头部版本行、Revision history 新增 1.2 段、§5 ListBooks 行三处；命令名/payload 结构/错误码/命令清单零改动。
2. 范围与整树整洁（复核 owner 自述）：
   `git diff --name-status 6199df48..852a92ae`；`git diff --check 6199df48..852a92ae; echo EXIT=$LASTEXITCODE`
   期望：11 条路径（`raw/scope-and-diff-check.log:5-23` 同集）；`diff --check` 空 + EXIT=0。
3. 前端/Rust diff 面（确认只有 page_count 相关行）：
   `git diff 6199df48..852a92ae -- apps/desktop/frontend apps/desktop/src-tauri`
   期望：`types.ts` 类型+注释、`LibraryPanel.tsx:145`、`LibraryPanel.test.tsx` 新增用例、`library_bridge.rs` 类型+注释+测试；无其他语义改动。
4. 交付 tip 绑定复跑（P2-4 关闭条件，须在集成 head 或 `bee7bf59` 执行）：
   `& $py -m pytest tests/m2_acceptance -q`（期望 35 passed，EXIT=0）
   `& $py -m pytest tests/core -q`（期望 77 passed，EXIT=0）
   `cd apps/desktop/frontend; npm test`（期望 5 files / 30 tests，EXIT=0）；`npm run build`（期望 34 modules，EXIT=0）
   `cd apps/desktop/src-tauri; cargo test --bin m2rc1-desktop`（期望 33 passed，EXIT=0；前置 `frontend/dist` 存在）
5. F-2 判别力的可复现红证（替代不可 commit 绑定的红日志）：
   在 tip 上把 `src/bootstrap/core_service.py:169` 临时改回 `page_count=page_counts.get(book.book_id, 0)` →
   `& $py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py::test_ac4_books_without_pages_are_not_presented_as_zero -q`
   期望：**1 failed @`:886`**；随后 `git checkout -- src/bootstrap/core_service.py` 并确认零残留。
6. f02 flake 再判定（P3-4）：
   在 tip 连跑 3 次 `cargo test --bin m2rc1-desktop`（默认线程）并留 raw；若 f02 复现，再 `cargo test --bin m2rc1-desktop -- --test-threads=1` 单线程对照。若复现，建议另立 flaky Task（M2-S2 资源通道 mtime/digest 判定），不计本 Task 回归。
7. `Any` 导入来源（P3-6）：
   `git show 6199df48:tests/core/test_core_service.py | Select-String 'typing|fail_execute'`
   期望：base 亦无 `from typing import Any` ⇒ 属既有潜伏项，非本 Task 引入。
8. TS known-0 正向渲染（P2-1 关闭条件）：
   在 `LibraryPanel.test.tsx` 加 `page_count: 0` 用例后 `cd apps/desktop/frontend; npx vitest run src/library/LibraryPanel.test.tsx`；并可用 `LibraryPanel.tsx:145` 的 `??`→`||` 变异验证该用例会红（红后还原）。
9. 我未独立核对：分支 tip 是否确为 `bee7bf59`、`852a92ae`/`2210d642`/`a2380706` 的实际拓扑与 reflog（无 shell，且 `.git` 元数据在 workspace 之外）：`git log --oneline -6; git rev-parse HEAD`。

## 3. 结论

**判定：approved_with_conditions。** 三层 None 通道类型与序列化语义严格对齐、生产 SQL 零改动、「行存在即 int、无行才 None」的取值语义经 INNER JOIN 结构独立证成（不存在把 SQL 数出的 0 吞成 None 的路径）、corrupt 场景断言更新是冻结语义的必然结果而非保护降级、先红后绿与日志逐行吻合、四套数字（35/77/33/30）经我独立静态复核全部自洽。无 P0/P1，实现主体不建议返工。

**放行条件（C1–C4，均为测试/文档/证据层，不动产品语义）：**
- **C1（P2-1）**：补 TS known-0 正向用例（`0` → `页数: 0`，且不得为 `—`），闭合三侧对称锁定；否则拒绝 `||` 类变异的防护在本 Task 内不成立。
- **C2（P2-2 + P3-2 + P3-3 + P2-3）**：契约 §3.2 落一行授权例外指针（或 §5 行内登记）；修 `tests/m2_acceptance/…:39` 陈旧 docstring；契约 1.2 日期改 `2026-09-29`；补 `verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/verification-results.md`（索引 raw 日志 ↔ AC/命令 ↔ EXIT）。
- **C3（P2-4）**：由集成方在集成 head 复跑 §2 第 4 组并在集成记录中回填 commit 绑定；同时修正 Handoff `:37-38` 的「交付 tip」表述为「工作树等价于 `852a92ae`，head 戳 `2210d642`」。
- **C4（P3-4/P3-5/P3-6）**：集成记录登记三项裁定——f02 复跑口径（≥3 次默认线程 + 单线程对照，复现则另立 flaky Task）；`LibraryPanel.test.tsx` 属 AC1 必然要求的范围解释；Handoff 补 NOT_RUN 小节（至少含：Rust 真通道 unknown-page 路径未覆盖、TS known-0 未锁定）。

**推荐下一步（可直接转发）：**
> **Agent：ZCode（Owner，子 agent 代行）；Task：M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN r2 返修。** 依据 DSH r1 报告（建议归档 `doc/reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-852a92ae-dsh-r1.md`）关闭 **C1 + C2 中除 verification-results.md 之外的全部文档项**：① `apps/desktop/frontend/src/library/LibraryPanel.test.tsx` 新增 `page_count: 0` → `"页数: 0"` 且非 `"页数: —"` 用例；② 修 `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py:39` 模块 docstring（F-2 已转 PASS）；③ `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §3.2 增授权例外指针、1.2 日期改 `2026-09-29`；④ Handoff 修正「交付 tip」表述并补 NOT_RUN 小节；⑤ 新建 `verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/verification-results.md` 索引；⑥ 追加 raw 日志：known-0 新用例 vitest 输出（含 `??`→`||` 变异红证后还原）、`cargo test --bin m2rc1-desktop` 在交付 commit 上的复跑、`git diff --check`。**禁止**改 `core_service.py` 语义、SQL、命令面与既有断言语义；C3/C4 由 Codex 集成收口。完成后交 Codex 集成（Owner≠Integrator 保持）。
