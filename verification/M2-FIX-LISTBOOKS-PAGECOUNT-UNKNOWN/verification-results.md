# M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN Verification Results（Owner 交付证据）

- Owner：ZCode（子 agent 代行，用户授权 2026-09-28）
- base：`6199df48`；release commit：`a2380706`；branch：`agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`
- worktree：`G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode`
- 解释器：`"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"`（路径含空格，日志头部以引号包裹；版本 = Python 3.12.3）；Rust：cargo 1.98.1；前端：node v24.15.0 / npm 12.0.1（worktree `node_modules` 经 `npm install --no-audit --no-fund` 安装，gitignored）
- 证据纪律：所有命令日志带 shell/解释器/固定 HEAD/ISO 时间戳，尾部 EXIT；raw 日志见 [raw/](raw/)
- Review 轨迹：DSH r1（`approved_with_conditions`，C1/C2 Owner 返修，C3/C4 留集成方）→ 本文件随 r2 返修建立；r2 tip 绑定复跑日志经 amend 并入（run-at hash 见各日志头部）

## 1. Commit ledger

| # | commit | 内容 |
|---|---|---|
| 1 | `2210d642` | claim（Task frontmatter owner/dispatch_state RELEASED→IN_PROGRESS） |
| 2 | `852a92ae`（= delivery_head） | r1 交付：三层 None 通道（Python/Rust/TS）+ 契约 rev 1.2 + F-2 xfail 移除 + known-0 单测（Python/Rust/TS 单向）+ raw 日志 |
| 3 | r1 回填 `bee7bf59` | Task 回填 AC 判定、status: in_review、DELIVERED_FOR_REVIEW + Handoff + final-tip-rerun 日志（该日志实际随 #3 提交） |
| 4 | r2 返修 commit（本文件所在 tip，hash 见 `git log`；Task frontmatter `delivery_head` 仍指向 #2，r2 tip 在正文 ledger 登记） | DSH r1 C1+C2：TS known-0 正向用例 + `??`→`||` 变异红证/还原、模块 docstring :39 陈旧句、契约 §3.2 例外指针 + 1.2 日期修正、本验证文档、Handoff 修正（tip 表述 + NOT_RUN 小节）；r2 tip 绑定复跑日志 amend 并入 |

## 2. 先红证据（AC3 前置：修复前证红留痕）

- 操作顺序：claim 后**临时移除** `test_ac4_books_without_pages_are_not_presented_as_zero` 的 `@pytest.mark.xfail(strict=True)` 标记（工作区未提交，src/ 零改动）→ 跑单场景 → **真红** → 修复 `core_service.py` → 同场景转绿 → 标记保持正式移除。
- 红点 = `presented_unknown` 断言（`:886`，日志行号一致）：`AssertionError: book 57c8… presents page_count=0 with page_count_known=None: unknown data rendered as a plausible number instead of an unknown marker` / `assert False`。
- 日志：[raw/red-run-f2-before-fix.log](raw/red-run-f2-before-fix.log)（HEAD=`2210d642`，尾部 `EXIT=1`）。

## 3. r1 交付验证（被审树 = 交付树；head 戳说明见 §6 P2-4 注）

| 命令（cwd） | 日志 | head 戳 | 结果 | EXIT |
|---|---|---|---|---|
| `$py -m pytest tests/m2_acceptance -q` | [raw/pytest-m2_acceptance-after-fix.log](raw/pytest-m2_acceptance-after-fix.log) | 修复后工作树 | **35 passed, 0 xfailed**（F-2 转 PASS，无 XPASS） | 0 |
| `$py -m pytest tests/core -q` | [raw/pytest-core-after-fix.log](raw/pytest-core-after-fix.log) | 同上 | **77 passed**（76 + 新增 known-0 DTO 测试） | 0 |
| 5 锚点测试 `-v`（E_LIST_BOOKS_FAILED / filtering / known-0 / F-2 场景 / corrupt 场景） | [raw/pytest-core-targeted-anchors.log](raw/pytest-core-targeted-anchors.log) | 同上 | 5 passed | 0 |
| `cargo test --bin m2rc1-desktop`（`apps/desktop/src-tauri`） | [raw/cargo-test.log](raw/cargo-test.log) | `2210d642`（交付前，见 §6） | **33 passed, 0 failed**（32 + 新增 serde 测试）；RUN 1 全绿 | 0 |
| `npm test` + `npm run build`（`apps/desktop/frontend`） | [raw/npm-test-and-build.log](raw/npm-test-and-build.log) | `2210d642`（同上） | vitest 5 files passed（LibraryPanel 7 tests）+ build 34 modules | 0 / 0 |

cargo f02 flaky 事件（首跑默认线程 `f02_equal_size_rewrite_after_first_verify_rejected` FAIL 200≠400 EXIT=101）与三重复证（base stash 单跑 PASS、带改动单跑×2 PASS、全量重跑 33 passed）见 [raw/cargo-test.log](raw/cargo-test.log) 尾部 FLAKY INCIDENT RECORD；DSH r1 P3-4 判定「代码路径不相交、结论方向认同、证据链偏弱」——集成方复跑口径见 Handoff NOT_RUN/遗留小节。

## 4. AC 逐项判定

| AC | 判定 | 证据 |
|---|---|---|
| AC1 unknown 通道落地 | **PASS** | Python `int \| None` + `get(book_id)`（SQL miss→None）；Rust `Option<u32>`（serde→null，`library_bridge.rs` 测试断言）；TS `number \| null`；`LibraryPanel.tsx` `?? "—"`；None 用例 `页数: —` 且 `not "页数: 0"`（vitest） |
| AC2 known-0 保留 | **PASS（r2 起三侧对称）** | Python DTO 层 `json.dumps`：`"page_count": 0` ≠ `"page_count": null`（`tests/core/test_core_service.py::test_book_summary_dto_known_zero_and_unknown_are_distinguishable`）；Rust serde 双向（`book_summary_page_count_known_zero_and_null_are_distinguishable`）；TS 正向 `0→"页数: 0"` 且非 `"—"`（r2 C1 新用例 `renders a known page_count of 0 as the number 0, never the unknown placeholder` + `??`→`||` 变异红证，见 §5） |
| AC3 xfail 移除转 PASS | **PASS** | 先红（§2）→ 修复 → 35 passed 0 xfailed，无 XPASS；模块 docstring 陈旧句已随 r2 修正（DSH r1 P3-2） |
| AC4 typed 错误保护 | **PASS** | `E_LIST_BOOKS_FAILED` 既有断言点名复跑 PASSED（[raw/pytest-core-targeted-anchors.log](raw/pytest-core-targeted-anchors.log)）；corrupt 场景断言更新为冻结语义必然结果（real_count==0 保留 + None 通道），DSH r1 §0 轴 4 判 PASS |
| AC5 契约与副本同步 | **PASS** | 契约 rev 1.2（头部版本 + Revision history + §5 ListBooks 行）+ r2 补 §3.2 授权例外指针（DSH r1 P2-2）；production SQL 对 base 完整 diff = 仅 2 hunk（DTO/handler），[raw/prod-sql-copy-sync-check.log](raw/prod-sql-copy-sync-check.log) → `_PRODUCTION_COUNT_SQL` 副本无需编辑、逐字一致保持 |
| AC6 证据纪律 | **PASS** | 全部日志带头（shell/解释器/HEAD/ISO）尾 EXIT；三层各自留痕（本文件 §3/§5）；整树 `git diff --check 6199df48..<tip>` EXIT=0（[raw/scope-and-diff-check.log](raw/scope-and-diff-check.log) r1 期 + r2 tip 复验 [raw/r2-final-bind-rerun.log](raw/r2-final-bind-rerun.log)）；范围分解（owner delta vs claim 全落允许路径；STATUS.md/release checkpoint 来自编排者 release commit `a2380706`）见 [raw/scope-and-diff-check.log](raw/scope-and-diff-check.log) scope decomposition 段 |

## 5. r2 返修（DSH r1 C1）——TS known-0 正向锁定 + 变异红证

| 步骤 | 命令 | 日志 | 结果 | EXIT |
|---|---|---|---|---|
| 变异红证 | `LibraryPanel.tsx:145` 临时 `??`→`||`（工作区未提交）→ `npx vitest run src/library/LibraryPanel.test.tsx` | [raw/npm-vitest-known0-mutation-red.log](raw/npm-vitest-known0-mutation-red.log) | **恰新 known-0 用例 FAILED**（`0` 被吞成 `页数: —`，`toContain("页数: 0")` 失败 `:82`），其余 7 用例（null→—、24→24 等）保持绿——变异仅由新用例拦截 | **1** |
| 还原 + 绿证 | `||` 还原 `??`（`git diff --stat` 对该文件为空 = 零残留，见日志尾）→ `npm test` + `npm run build` | [raw/npm-test-after-known0-case.log](raw/npm-test-after-known0-case.log) | LibraryPanel.test.tsx **8 tests** 全绿；5 files passed；build 通过 | 0 / 0 |

新用例：`renders a known page_count of 0 as the number 0, never the unknown placeholder`（`apps/desktop/frontend/src/library/LibraryPanel.test.tsx`）。

## 6. head 戳绑定说明（DSH r1 P2-4 / C3 背景，Owner 侧如实登记）

- r1 期 cargo/npm 日志 head=`2210d642`（claim，交付前）：执行时刻交付 commit 尚未创建；内容层对应交付树（新增用例名、7 tests、33 `#[test]` 与交付文件逐一吻合，DSH r1 §0 轴 6 独立复核）。Handoff 原文「交付 tip」表述已随 r2 修正为「工作树等价于 `852a92ae`，日志 head 戳 `2210d642`（交付前）」。
- **r2 tip 绑定复跑（commit 级绑定，amend 并入 r2 返修 commit）**：[raw/r2-final-bind-rerun.log](raw/r2-final-bind-rerun.log)——在 r2 返修 commit 上复跑 `pytest tests/m2_acceptance -q`（35 passed）、`pytest tests/core -q`（77 passed）、`cargo test --bin m2rc1-desktop`（33 passed）、`npm test`（5 files / 31 tests，LibraryPanel 8）+ `npm run build`、`git diff --check 6199df48..HEAD`（空 + EXIT=0）；日志头 run-at hash = r2 初版 `f4f77808`（本日志自身经 amend 并入，被验树与最终 r2 tip 的差集 = 本日志文件；最终 r2 hash 见 `git log`）。日志中段三条 `EXIT=1` 为一次 bash 重定向路径错误的中止调用（cargo/npm 未执行、无结果产生），已逐行 `ABORTED INVOCATION` 括注，其后的注记 rerun 为有效结果。

## 7. 范围自检

- r1 期：[raw/scope-and-diff-check.log](raw/scope-and-diff-check.log)——`git diff --name-status 6199df48..HEAD` 全 11 路径 + scope decomposition（owner delta `2210d642..852a92ae` 全落允许路径）+ 整树 `git diff --check` EXIT=0。
- `LibraryPanel.test.tsx` 字面缺口（DSH r1 P3-5）：AC1「vitest 用例锁定不渲染 0」的必然要求，集成方按 C4 登记范围解释。
- r2 期 delta（`bee7bf59..r2`）：`LibraryPanel.test.tsx`（新用例）、`test_reader_export_lineage_library_pagecount.py`（仅模块 docstring，零断言改动）、`M2-C1_TYPED_IPC_CONTRACT.md`（§3.2 一行 + 1.2 日期）、Handoff、本文件、raw 新日志、Task ledger——全落允许/AC 必然范围；r2 tip 终验见 [raw/r2-final-bind-rerun.log](raw/r2-final-bind-rerun.log)。

## 8. 遗留（均不阻塞 in_review；处置见 Handoff NOT_RUN 小节）

- P3-1 Rust 真通道 unknown-page 端到端（集成方，1 条 seed 即可闭合）；
- P3-4 f02 flaky 集成复跑口径（≥3 次默认线程 + 单线程对照）；
- P3-6 `Any` 导入（`from __future__ import annotations` 下运行期无碍；集成方按 §2.7 与 base 比对来源）。
