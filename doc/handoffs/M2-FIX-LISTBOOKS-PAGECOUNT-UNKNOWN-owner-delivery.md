---
task_id: M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN
author: ZCode（子 agent 代行，用户授权 2026-09-28）
recipient: DeepSeek Harness（非作者 Review r1）→ Codex（Integrator，另一子 agent，保持 Owner≠Integrator）
base_commit: 6199df48
delivery_head: 852a92aefbeffd4b15c701cecd2b19d6229b70ca
status: DELIVERED_FOR_REVIEW
---

# Handoff：M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN（ListBooks page_count unknown/已知度通道，F-2 修复，冻结 None 通道）

## 交付结果

按冻结 None 通道完成三层落地：Python `BookSummaryDto.page_count: int | None`（`handle_list_books` 的 `page_counts.get(book.book_id, 0)` → `get(book.book_id)`，SQL miss → None、有合格页书 → 真实 int）；Rust `library_bridge.rs` `BookSummary.page_count: u32 → Option<u32>`（serde → JSON `null`）；TS `types.ts` `page_count: number | null`，`LibraryPanel.tsx` 对 None 渲染非数字占位 `页数: —`（不得渲染 0）。production `_fetch_page_counts` SQL **零改动**（diff 逐字核对，`_PRODUCTION_COUNT_SQL` 副本同步义务因此无需编辑、逐字一致保持）。ListBooks 命令名/payload/错误码/command 面清单不变；契约文档 M2-C1 登记授权修订 rev `1.2`。

F-2 xfail 场景 `test_ac4_books_without_pages_are_not_presented_as_zero` **先红后绿**：临时移除标记后修复前证红（红点 = `presented_unknown` 断言为 False，`page_count=0` 无 unknown 表达位，EXIT=1），修复后同场景 PASS，随后全量 xfail 清零（35 passed, 0 xfailed，无 XPASS）。

变更路径（全部在允许范围；范围分解证据 raw/scope-and-diff-check.log）：
- `src/bootstrap/core_service.py`（DTO 字段类型 + handler 默认值 + 注释；SQL 字面量未动）
- `apps/desktop/src-tauri/src/library_bridge.rs`（类型 + doc 注释 + 测试 `Some(5)` 适配 + 新增 known-0/null serde 可区分测试）
- `apps/desktop/frontend/src/library/types.ts`、`LibraryPanel.tsx`（占位渲染）、`LibraryPanel.test.tsx`（新增 None 占位用例）
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（rev 1.2：头部版本、Revision history、§5 ListBooks 行）
- `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py`（F-2 xfail 移除 + docstring；corrupt 场景第二次断言按冻结语义更新，见「偏差与判定」）
- `tests/core/test_core_service.py`（无章书断言 0 → None + docstring；新增 DTO 层 known-0 vs None 序列化测试）
- `verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/**`、本 Handoff、Task 回填

Commit ledger：claim `2210d642` → 交付 `852a92ae` → Task 回填（delivery_head=`852a92ae`）。

## 验证证据

| AC/场景 | 实际命令 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 先红（AC3 前置） | 移除 xfail 标记 → `$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py::test_ac4_books_without_pages_are_not_presented_as_zero -q` | py3.12 task-env，HEAD=`2210d642`（src 零改动） | **FAIL（预期红）**：`assert presented_unknown` False（`page_count=0`, `page_count_known=None`），EXIT=1 | raw/red-run-f2-before-fix.log |
| AC1/AC3 全套 | `$py -m pytest tests/m2_acceptance -q` | 交付 tip | **35 passed, 0 xfailed** EXIT=0（F-2 转 PASS，无 XPASS） | raw/pytest-m2_acceptance-after-fix.log |
| AC2/AC4 core 回归 | `$py -m pytest tests/core -q` | 交付 tip | **77 passed** EXIT=0（原 76 + 新增 1） | raw/pytest-core-after-fix.log |
| 锚点点名 | 5 个锚点测试 `-v`（E_LIST_BOOKS_FAILED、filtering、known-0 新测、F-2 场景、corrupt 场景） | 交付 tip | **5 passed** EXIT=0 | raw/pytest-core-targeted-anchors.log |
| Rust 侧 | `cargo test --bin m2rc1-desktop`（cwd=`apps/desktop/src-tauri`） | 交付 tip | **33 passed, 0 failed** EXIT=0（32 + 新增 serde 测试；f02 首跑 flaky 事件与三重复证记录于日志尾部 FLAKY INCIDENT RECORD） | raw/cargo-test.log |
| 前端侧 | `npm test`（vitest run）→ `npm run build`（tsc && vite build） | 交付 tip | vitest **5 files passed**（LibraryPanel 7 tests 含新 None 用例）EXIT=0；build **34 modules** EXIT=0 | raw/npm-test-and-build.log |
| AC5 副本同步 | `git diff 6199df48 -- src/bootstrap/core_service.py` 核对 SQL 字面量 | 交付 tip | SQL 零改动 → `_PRODUCTION_COUNT_SQL` 副本无需编辑、逐字一致保持 | raw/prod-sql-copy-sync-check.log |
| AC6 范围/纪律 | `git diff --check 6199df48..HEAD` 整树；`git diff --name-status` 分解 | 交付 tip `852a92ae` | **整树 EXIT=0**（无 whitespace amend 需要）；owner delta vs claim 全落允许路径；`STATUS.md`/`release-6199df48.md` 来自编排者 release commit `a2380706` 非 owner 改动 | raw/scope-and-diff-check.log |

known-0 vs None 可区分性（AC2）三侧锁定：
- Python：`tests/core/test_core_service.py::test_book_summary_dto_known_zero_and_unknown_are_distinguishable`——直接构造 `page_count=0` 与 `page_count=None` 两个 DTO，`asdict`+`json.dumps` 后断言 `"page_count": 0` ≠ `"page_count": null`、round-trip 后 `== 0` / `is None`。
- Rust：`library_bridge.rs::tests::book_summary_page_count_known_zero_and_null_are_distinguishable`——serde 序列化 `Some(0)` → `"page_count":0`、`None` → `"page_count":null`，反序列化 round-trip 断言。
- TS：`LibraryPanel.test.tsx` None 占位用例锁定 UI 层不把 null 折叠成 0（`页数: —` 且 `not.toContain("页数: 0")`）。

## 偏差与判定（review 重点）

1. **corrupt 场景第二次断言更新**（`test_ac4_corrupt_page_rows_degrade_without_crash_or_fabrication` 尾段）：原断言 `page_count == real_count == 0`；冻结语义「SQL 无行的书 → None」下，全部页损坏被 production 谓词排除 → GROUP BY 无行 → None。更新为 `real_count == 0`（单书 WHERE 版 SQLite 真实值保持断言）+ `page_count is None`（unknown 通道）。该测试的保护意图（不崩溃、不伪造其他字段、呈现值追踪真实行）不变；这是 Task 冻结语义的直接必然后果而非断言弱化，「其余场景断言不改语义」按此口径执行。同因，`tests/core/test_page_count_filtering_discriminating_cases` 无章书 `== 0` → `is None`（docstring 同步）。
2. **cargo f02 flaky**（`tests::f02_equal_size_rewrite_after_first_verify_rejected`，M2-S2 resource-channel digest 测试，src/main.rs，本 Task 零触碰）：首跑默认线程下 FAIL（got 200, want 400，EXIT=101）；复证三连——base（stash 后 HEAD=`2210d642`）单跑 PASS、带改动单跑 ×2 PASS、带改动全量重跑 33 passed EXIT=0。判定为默认线程并发 flaky，与本修复无关；证据链见 raw/cargo-test.log 尾部 FLAKY INCIDENT RECORD。建议 Reviewer/集成方知悉该测试存在偶发并发敏感。
3. **`cargo test --lib` 探针**：`m2rc1-desktop` 为 binary-only crate（no library targets，EXIT=101），改用 `cargo test --bin m2rc1-desktop` 全量口径；前置依赖 `apps/desktop/frontend/dist` 存在（tauri build script 要求 frontendDist），故先 `npm run build` 再 cargo。全程留痕。
4. **环境设置**：worktree 前端 `node_modules` 缺失，`npm install --no-audit --no-fund` 后方可 vitest/tsc（gitignored，不进交付）。
5. **git auto-maintenance 噪音**：交付 commit 时 git 自动维护尝试删除主 repo `.git/worktrees/New-Manga*` 元数据报 Permission denied——删除失败、无实际副作用，其他 worktree 注册未被破坏；非 owner 主动操作，如实登记。

## 回退方法

revert 交付 commit `852a92ae` 即恢复 base 行为（None 通道收敛回 0 伪装态；无 schema/数据迁移、无持久层触碰）。

## 下一任务建议（必填）

- Task ID / 标题：M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 的非作者 Review（DSH r1）→ Codex 集成收口
- 推荐 Agent / Reviewer：DeepSeek Harness（Review）→ Codex（Integrator，另一子 agent，保持 Owner≠Integrator）
- 推荐原因与前置依赖：Task 交付完成，按协作协议进入 Review→集成；本 Task 现为 Review 准备态（in_review）
- Recovery point：仓库 `G:/CODEX/New Manga`；branch=`agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`；worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode`；固定 base=`6199df48`、delivery_head=`852a92ae`
- 允许修改路径：`doc/reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-*/**`（DSH 报告）、`doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md`（review/integration_merge 回填）、`verification/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN/**`（集成记录）、`doc/STATUS.md`
- 禁止范围与新增授权条件：Review/集成不得改实现与测试语义；corrupt 场景断言更新口径（本文件偏差 1）如需推翻须回到编排裁决；f02 flaky 如在集成复跑复现，按 raw/cargo-test.log FLAKY INCIDENT RECORD 口径单线程复证，不计为本 Task 回归
- 交付物：DSH review 报告、集成记录、Task 终态回填
- 验证命令、环境与完成 Gate：`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/m2_acceptance -q`（预期 35 passed, 0 xfailed）+ `... -m pytest tests/core -q`（预期 77 passed）+ `cargo test --bin m2rc1-desktop`（cwd=`apps/desktop/src-tauri`，预期 33 passed；前置 `npm run build` 产 dist）+ `npm test`（前端，5 files）全绿 + 范围复算 + Owner≠Integrator 保持
- 可直接转发给 Agent 的指令：对交付 tip `852a92ae` 做 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 非作者静态 Review（重点：None 通道三侧一致性、known-0 单测有效性、先红真实性、corrupt 断言更新口径、f02 flaky 判定），产出 `doc/reviews/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN-852a92ae-dsh-r1.md`；通过后由 Codex 集成收口。
