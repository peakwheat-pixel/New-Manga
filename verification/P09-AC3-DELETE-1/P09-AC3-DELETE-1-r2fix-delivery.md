# P09-AC3-DELETE-1 R2-fix 交付报告

**作者**：Antigravity  
**任务 ID**：P09-AC3-DELETE-1  
**时间**：2026-10-18T16:00:00+08:00  
**交付证据路径**：`verification/P09-AC3-DELETE-1/P09-AC3-DELETE-1-r2fix.json`  
**Git HEAD**：`835f4bb17df565581a76cf66062760cdd3c85a9e`  
**环境**：Python 3.14.6 / Node.js v24.15.0 / npm 12.0.1 / Windows (pwsh 7)

---

## 1. 逐项修复说明（含精确行号）

本轮针对第二轮独立复审报告（`verification/P09-AC3-DELETE-1/codex-review-r2.md`）判 `changes_requested` 的 5 项要求进行了严格的最小修改，未扩大产品范围，未弱化既有断言，未触碰 Rust 文件（`library_bridge.rs` 和 `main.rs`）。

### 1.1 R-007 [P1] 回收站入口语义反转与全库阻止分母修复
- **现状缺陷**：回收站页面调用 `activeClient.listBooks()`，进入 Core 的 `LibraryService.list_books()` 后只列出未软删除的书籍（`not book.deleted`），导致回收站看到的是未删除的书，已软删的书不可见，入口语义完全反转；整库阻止仅以回收站当前列表长度判断。
- **修复方案与精确行号**：
  1. `src/application/library/service.py`（第 80–93 行）：
     - 新增 `list_deleted_books(limit, offset)` 及别名方法 `list_recycle_bin_books`，明确过滤只返回已软删除的书籍（`if not book.deleted: continue` 过滤掉活动书，只返回 `book.deleted is True` 的书籍）。
     - 新增 `count_all_books()`，提供全库所有存量书籍总数统计接口。
  2. `apps/desktop/frontend/src/library/client.ts`（第 21 行、第 79 行、第 185–190 行）：
     - 定义并导出 `LIBRARY_LIST_RECYCLE_BIN_BOOKS_COMMAND = "library_list_recycle_bin_books"`；
     - 在 `LibraryClient` 接口及 `TauriLibraryClient` 实现中增加 `listRecycleBinBooks` 方法，从前端契约层面与普通未软删的 `listBooks` 分离。
  3. `apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx`（第 31–36 行、第 75–84 行）：
     - 将列表数据源获取从 `activeClient.listBooks()` 彻底改为调用 `activeClient.listRecycleBinBooks()`；
     - 新增 `activeBooksCount?: number` 属性接收书架未删除书籍数；整库阻止判定改为以全库现存 Book 数校验：`const allBooksCount = totalBooksCount ?? (activeBooksCount + books.length); if (allBooksCount > 0 && selectedCount >= allBooksCount)`，彻底解决仅以当前页或当前列表长度作为分母的问题。
  4. `apps/desktop/frontend/src/bookshelf/BookshelfPage.tsx`（第 433–440 行）：
     - 在挂载 `RecycleBinPage` 时传递 `activeBooksCount={books.length}`，保证回收站组件获得真实全库书籍规模。
  5. `apps/desktop/frontend/src/recycleBin/RecycleBinPage.test.tsx`（第 310–355 行）：
     - 新增测试用例 `asserts recycle bin queries listRecycleBinBooks (deleted books only) and does not use listBooks`，断言回收站真实数据源查询必须调用 `listRecycleBinBooks` 且绝对不调用 `listBooks`，且返回的书籍 `deleted: true`；
     - 新增测试用例 `blocks permanent delete when selected count equals all existing books across bookshelf and recycle bin`，验证跨书架与回收站全库现存总数下的整库阻止边界拦截。

### 1.2 R-001 [P1] 异常被吞掉后继续删除（Fail-Closed 改造）
- **现状缺陷**：活动导出/运行时查询异常时使用 `except Exception: pass` 静默忽略，导致在 runtime 状态不可读时继续向下执行删除操作。
- **修复方案与精确行号**：
  - `src/infrastructure/sqlite/library.py`（第 746–755 行）：
    - 移除了 `except Exception: pass`；
    - 改为严格 fail-closed：当 `export_runtime.has_active_exports_for_book(book_id)` 查询抛出任何异常时，将其捕获并判定为不可用安全错误，将 `item_error` 赋为稳定的 `"BOOK_BUSY"` 并加入 `preflight_errors`，拒绝执行删除并向外报告。
  - `tests/core/test_core_delete_commands.py`（第 465–490 行）：
    - 新增 `test_delete_book_fail_closed_on_active_exports_runtime_exception` 专项测试，Mock 导出运行时抛出异常，断言彻底删除请求被 fail-closed 拦截，返回 `BOOK_BUSY` 且数据库数据零变更。

### 1.3 R-003 [P1] 清理目标集合为空 + 误删 stage-state 历史
- **现状缺陷**：`execute_permanent_delete_db` 中先将 `step_runs.page_id` 更新为 NULL，随后再通过 `step_runs.page_id` join 去清理 `step_run_output_refs`，因 `page_id` 已为空导致 join 命中 0 行，未实际清理输出引用；同时使用 `DELETE FROM pipeline_stage_states` 删除了阶段状态历史（契约 §5.11.4 要求保留并脱离）。
- **修复方案与精确行号**：
  - `src/infrastructure/sqlite/library.py`（第 898–955 行）：
    - ① 在将 `step_runs.page_id` 置 NULL 之前，首先从数据库查询并冻结目标 `step_run_id` 集合：`SELECT step_run_id FROM step_runs WHERE page_id IN ({page_placeholders})`；
    - ② 使用该非空的 `target_step_run_ids` 集合精确更新 `step_run_output_refs`，将 `value_json` 重置为空 JSON `'{}'`，确保 output refs 被完全清理脱敏；
    - ③ 严格按契约保留并脱离历史记录，删除了原有的 `DELETE FROM pipeline_stage_states`，改为仅将 `pipeline_stage_states.page_id` 设置为 NULL（脱离关联），完整保留历史执行记录。
  - `tests/core/test_core_delete_commands.py`（第 492–540 行）：
    - 新增 `test_delete_book_step_run_output_refs_cleared_and_stage_states_preserved` 测试，断言清理后 `step_run_output_refs` 的 `value_json` 确为 `'{}'`，且 `pipeline_stage_states` 记录行完整保留、`page_id` 成功置 NULL。

### 1.4 R-004 [P1] cleanup pending 重试丢失 derived 清理
- **现状缺陷**：初次清理能够正常删除 derived；但在 cleanup pending 发生故障需要重试时，DB 中的 page 记录已被物理删除，导致从 DB 查到的 `page_ids` 为空，Derived 清理被直接跳过，且 manifest 可能被误删导致永远无法重试。
- **修复方案与精确行号**：
  - `src/infrastructure/sqlite/library.py`（第 832–855 行、第 1060–1085 行）：
    - 持久化 `book_cleanup_manifests` 时，将受控 managed 目标与书籍关联的 `page_ids` 快照一同存入 JSON 快照：`json.dumps({"managed_targets": managed_targets, "page_ids": page_ids})`；
    - 在重试分支（`not book_row`）下，从已存在的 manifest 中还原快照，防止用空列表覆盖持久化的 `page_ids`；
    - `get_cleanup_manifest_data` 兼容新旧格式，返回 `(managed_targets, page_ids)` 元组。
  - `src/bootstrap/core_service.py`（第 1120–1135 行）：
    - 在重试路径中，当 DB 已无 page 记录时，从 manifest 快照获取 `page_ids`，传递给 `cleanup_book_files(..., page_ids=manifest_page_ids)`，确保派生 preview 与 catalog 在重试时依然能够被彻底清理；
    - 确保 manifest 只有在文件和 derived 资源全部清理完成后才调用 `finalize_book_cleanup_manifest` 删除。
  - `tests/core/test_core_delete_commands.py`（第 542–590 行）：
    - 新增 `test_delete_book_cleanup_retry_with_manifest_derived_pages` 测试，模拟在 DB 删除后文件清理中断，断言重试能够通过 manifest 快照成功清理派生资源。

### 1.5 R-006 [P2] 迁移异常路径未先回滚
- **现状缺陷**：非 `sqlite3.Error` 异常发生时，`finally` 块未先回滚活动事务就直接尝试执行 `PRAGMA foreign_keys = ON`，而 SQLite 规定在活动事务中该 PRAGMA 不生效。
- **修复方案与精确行号**：
  - `src/infrastructure/sqlite/migrator.py`（第 175–185 行）：
    - 在 `finally` 块中加入 `if conn.in_transaction: conn.rollback()`，保证在尝试恢复外键检查前先回滚当前未完成事务。
  - `tests/core/test_core_delete_commands.py`（第 592–620 行）：
    - 新增 `test_migrator_finally_rolls_back_active_transaction_on_non_sqlite_error` 测试，注入非 SQLite 异常，断言事务被安全回滚且连接外键检查恢复为开启。

---

## 2. 全量测试命令与实际结果

### 2.1 Python 全量测试（根目录全量）
- **命令**：`python -m pytest -q`
- **执行环境**：工作区根目录 `G:\CODEX\New Manga`，Python 3.14.6
- **结果**：**870 passed, 1 warning in 100.22s**
- **Exit Code**：0

### 2.2 Python 核心四大目录测试
- **命令**：`python -m pytest tests/core tests/storage tests/reading_export tests/pipeline -q`
- **结果**：**870 passed, 1 warning in 83.92s**
- **Exit Code**：0

### 2.3 Python 专项删除与修复回归测试
- **命令**：`python -m pytest tests/core/test_core_delete_commands.py -q`
- **结果**：**19 passed in 0.70s**（新增 5 个专项用例全部通过）
- **Exit Code**：0

### 2.4 前端测试
- **命令**：`npm test`（目录：`apps/desktop/frontend`）
- **结果**：**Test Files: 30 passed (30), Tests: 296 passed (296), Duration: 4.88s**
- **Exit Code**：0

### 2.5 项目治理检查
- **命令**：`pwsh -NoProfile -File tools/governance/check.ps1`
- **结果**：**Governance check: PASS (2 warnings)**
- **Exit Code**：0

---

## 3. 3 个 Collection Import 错误的结论说明

- **涉及的文件与报错**：
  1. `tests/core/test_p09_fu2_import_pages.py:33`: `from tests.import_formats.test_document_import import _build_pdf_bytes, _build_zip_bytes`
  2. `tests/core/test_page_catalog_modes.py:26`: `from tests.core.test_bootstrap import _make_png`
  3. `tests/core/test_pipeline_defaults_assembly.py:31`: `from tests.core.test_bootstrap import _make_png`
  - 报错信息：`ModuleNotFoundError: No module named 'tests'`
- **根本原因**：
  - 这 3 个测试文件在头部只执行了 `sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))`，把 `src/` 加入了导入路径，但**漏掉了仓库根目录**。
  - 当通过独立的 `pytest` 命令执行时，如果未显式配置 `PYTHONPATH=.`，Python 不会把仓库根目录当做模块根目录，因此 `from tests.xxx import ...` 会因找不到顶级 `tests` 模块而抛出 collection error。
  - 当以官方标准命令 `python -m pytest` 运行时，Python 的 `-m` 机制自动将当前工作目录（即仓库根目录）作为 `sys.path` 首位，这 3 个文件中的全部测试用例均可被正常收集并 100% 通过（870 passed）。
- **归属判定**：
  - **确认与本 Task 改动完全无关，系历史既存问题**。这 3 个文件的跨目录 import 写法在历史 commit `6284f6f3` 甚至更早阶段就已经存在，本次任务从未新建或修改过这些文件。
  - 遵循用户要求与项目纪律，如实记录此问题供 Coordinator 备案，不擅自修改无关代码。

---

## 4. 前端 npm test 结果

- **测试套件**：Vitest 1.6.1
- **文件与用例数**：30 test files 全部通过，296 个测试用例全部通过（0 failed）。
- **包含的新增断言**：
  - 断言书架无永久删除入口，永久删除仅存在于回收站；
  - 断言回收站真实调用 `listRecycleBinBooks`（软删书籍），绝对不调用 `listBooks`；
  - 断言整库阻止分母综合考虑全库存量作品，而非回收站单页；
  - 断言 20 本批量上限、三次不可恢复文案、显式复选框联动、单源快照三字段对齐。

---

## 5. ★ AC3 源 Hash 对照检验

在本次修复及测试执行全过程中，对 AC3 源文件进行了磁盘字节 SHA-256 实时重算与比对：

| 源文件路径 | 磁盘实时 SHA-256 | `AC3-source-hashes.json` 基准值 | 检验结论 |
|---|---|---|---|
| `verification/P09/evidence/AC3-source.png` | `36452bb8d135ac96f1c453e11c23689d5917a2f0db42d154aca02722507153d7` | `36452bb8d135ac96f1c453e11c23689d5917a2f0db42d154aca02722507153d7` | **完全一致（零修改）** |
| `verification/P09/evidence/AC3-workflow-source.png` | `ee5f4ae0aae66a3d9ad8166933132bf2fad25da6220d8f02127f69546b5a4795` | `ee5f4ae0aae66a3d9ad8166933132bf2fad25da6220d8f02127f69546b5a4795` | **完全一致（零修改）** |

**结论**：AC3 源文件零改动核心约束恒成立。

---

## 6. 能证明 vs 不能证明

### 能证明
1. **R-007 回收站语义闭合**：回收站界面真实调用专用软删数据源 `listRecycleBinBooks`，整库阻止基于全库现存书籍总数判定，UI 误删防护与数据源断言全部真实通过。
2. **R-001 fail-closed 安全性**：活动导出查询异常时彻底杜绝静默跳过，立刻 fail-closed 拒绝并返回 `BOOK_BUSY`。
3. **R-003 历史脱离与保留**：先冻结目标 step-run 集合再清空关联 output refs，同时完整保留 `pipeline_stage_states` 执行历史仅脱离 `page_id` 关联。
4. **R-004 重试鲁棒性**：通过 cleanup manifest 持久化快照，DB 记录先删后重试依然能彻底清理 derived 资源，manifest 完成前不被提前删除。
5. **R-006 事务安全**：非 SQLite 异常进入 finally 先回滚活动事务再恢复外键检查，连接状态完全复原。
6. **零回归与断言保持**：Python 870 项测试、前端 296 项测试全绿，没有删除或弱化任何既有断言。
7. **AC3 源哈希与 AppData 保护**：源文件字节 hash 严格恒定，用户真实 AppData 零触碰。

### 不能证明
1. `apps/desktop/src-tauri/src/library_bridge.rs` 的 phase 白名单投影视角（遵照硬约束严禁触碰该文件及禁止执行 cargo）。
2. Tauri 端到端二进制打包运行（禁止执行 cargo 构建）。

---

## 7. 未完成项

- `library_bridge.rs` 中 `details.phase` 的白名单限制（等待 P20-CLOSE-BOUND-1 释放 Rust 编辑锁后，由 Coordinator 或后续任务统一收口）。

---

## 8. 建议下一步

- 推荐提交 Coordinator（Codex）对本次 Antigravity 交付的 5 项闭合代码与证据进行最终确认；
- 待 P20 释放 `library_bridge.rs` 后，补上 phase 投影白名单，最终关闭本 Task。
