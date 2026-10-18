# P09-AC3-DELETE-1 R-007-fix 交付报告

**作者**：Antigravity  
**任务 ID**：P09-AC3-DELETE-1  
**时间**：2026-10-18T15:19:00+08:00  
**交付证据路径**：`verification/P09-AC3-DELETE-1/P09-AC3-DELETE-1-r1fix.json`

---

## 1. 上一轮未产出报告的原因说明

上一轮（R-007）在完成了前端回收站页面及组件开发、Vitest 测试编写以及 Core 侧多项复审问题修复并成功落盘后，在执行全量测试与生成最终交付报告的过程中，遭遇了系统调用超时/上下文截断中断，导致最后的写盘与报告输出未能完成，在磁盘上留下了缺失状态。本轮已全面接管并修复了后续暴露的 9 项回归问题，并完整补齐了所有交付报告与证据。

---

## 2. 修改清单（逐文件）

### 前端（React / TypeScript）
1. `apps/desktop/frontend/src/library/types.ts`：定义 `PermanentlyDeleteBookRequest`, `PermanentlyDeleteBooksRequest`, `BatchBookDeleteResult`, `BatchDeleteFailedItem` 等契约接口。
2. `apps/desktop/frontend/src/library/client.ts`：在 `LibraryClient` 接口和实现中追加 `deleteBookPermanently` 与 `deleteBooksPermanently` 方法。
3. `apps/desktop/frontend/src/recycleBin/PermanentDeleteConfirmDialog.tsx`：实现二次确认对话框，包含作品列表与数量展示、三条不可恢复/导出保留/备份不处理警示文案、显式勾选框及禁用状态控制。
4. `apps/desktop/frontend/src/recycleBin/RecycleBinPage.tsx`：实现回收站独立页面，限定彻底删除入口仅存在于回收站，实现单选/多选、批量上限 20 拦截、整库阻止拦截、从同源快照装配三项确认字段、调用 IPC 并刷新状态。
5. `apps/desktop/frontend/src/recycleBin/RecycleBinPage.test.tsx`：新增 12 项回收站交互与安全规则 Vitest 单元测试，全部通过。
6. `apps/desktop/frontend/src/bookshelf/BookshelfToolbar.tsx`：在书架顶部工具栏新增“回收站”独立导航入口按钮，不在书架主列表放置任何永久删除按钮。
7. `apps/desktop/frontend/src/bookshelf/BookshelfPage.tsx`：集成回收站视图模式与切换。

### Core / Storage / Pipeline / Tests（Python）
1. `src/infrastructure/sqlite/library.py`：修复 R-001~R-005, R-009：预检活动任务与导出互斥（`BOOK_BUSY`）；跨作品共享 Managed 引用与跨项目 Revision 引用冲突拦截（`BOOK_DELETE_CONFLICT`）；Pipeline/Export 历史深度脱离；Derived 预览联动清理；整库清空精确全等匹配。
2. `src/infrastructure/sqlite/migrator.py`：修复 R-006：将 `foreign_keys=OFF` 严格限制在 v5 迁移阶段，完善 try/finally 并在提交前执行 `PRAGMA foreign_key_check`。
3. `src/bootstrap/core_service.py`：接入 `export_runtime.has_active_exports_for_book` 与 Derived 资源清理联动。
4. `src/application/reading/ports.py`：在 `ReaderPage.translated_stale` 中补回 `translated_revision_id != current_translated_revision_id` 判定，修复阅读器 ViewModel 既有陈旧标记断言。
5. `src/application/export/service.py`：在 `ExportPage.stale` 中补回 `translated_revision_id != current_translated_revision_id` 判定，修复既有导出陈旧性断言；在 `P16ExportRuntime` 中补回 `book_title` 快照读取并新增 `has_active_exports_for_book`。
6. `src/application/tasks/service.py`：引入 `_resumed_runs: set[str]` 集合，跟踪通过 `continue` / `mode="continue"` 恢复的任务，对外保持 `ControlResult` 返回 `PENDING` 契约，内部调度按需消费 `resumed=True`，修复 4 项流水线暂停/恢复断言失败，且不破坏非 pending 状态直接调度时的拦截能力。
7. `tests/core/test_core_delete_commands.py`：修复新增测试中手写 SQL 违反 NOT NULL / CHECK 约束与列名错误问题，补齐批量同批次引用允许用例与整库清空精确匹配用例。

---

## 3. R-007 AC5 交互流程实现

1. **入口只在回收站**：书架卡片与批量工具栏仅提供软删除（移入回收站），无任何彻底删除按钮；仅在 `BookshelfToolbar` 提供“回收站”按钮进入 `RecycleBinPage`，彻底删除入口唯一限定在回收站。
2. **逐项列出书名与数量**：弹窗头部明确渲染“即将永久删除 N 部作品：”，列表逐项显示作品 `title` 与 `original_title`。
3. **显式勾选**：包含受控的“我理解不可恢复”复选框，必须手动勾选后“彻底删除”按钮方可点击。
4. **三项确认字段同源**：点击打开弹窗时从选中的项冻结单一快照，提交时从该快照直接装配 `book_ids`、`confirmed_book_ids`（同序同源）与 `confirm_count`，保证三者一致。
5. **批量上限 20**：选择超过 20 本时直接拦截弹窗并显示警示错误。
6. **整库阻止**：选择数量等于全部作品数时拦截弹窗，提示不能单次批量清空整库。
7. **三条强制提示文案**：
   - • **App 回收站无法恢复**：此操作将永久删除所选作品的数据库记录、章节、页面及受控 Managed Copy，不可撤销。
   - • **用户导出目录内的文件会保留**：已导出的作品文件不会被删除或修改。
   - • **全库历史备份不处理且可能含旧快照**：此操作不会清理或改写全库历史备份，旧备份中可能仍保留删除前的数据快照。

---

## 4. 本轮 9 个失败的根因与修法

| 测试项 | 属性判定 | 根因 | 修法 |
|---|---|---|---|
| `test_core_delete_commands.py::test_delete_book_busy_with_active_tasks_and_exports` | 测试本身缺陷 | SQL 遗漏 `target_type` NOT NULL 列；向 `export_history` 插入 `status='running'` 违反物理 CHECK 约束 | 补充 `target_type='page'`；改用 mock `DummyExports.has_active_exports_for_book` 挂接 `server._exports` 验证 `BOOK_BUSY` |
| `test_core_delete_commands.py::test_delete_book_conflict_with_shared_managed_or_cross_project` | 测试本身缺陷 | 插入 `artifact_revisions` 使用了不存在的列名 `revision_index`（实际为 `revision_no`）且缺少必填字段 | 修正列名为 `revision_no` 并补全必填字段，完整验证三种冲突场景下的拦截与零副作用 |
| `test_export.py` (2 项) | 实现缺陷（语义破坏） | `ExportPage.stale` 条件此前被窄化为仅检查源修订变化，丢失了 D06 的译图修订指针变化判定 | 补充恢复 `translated_revision_id != current_translated_revision_id` 判定，恢复既有契约语义 |
| `test_reading.py::test_stale_translated_flagged_with_message` | 实现缺陷（语义破坏） | `ReaderPage.translated_stale` 同样被窄化为仅检查源修订变化 | 补充恢复 `translated_revision_id != current_translated_revision_id` 判定 |
| `test_pipeline.py` & `test_pipeline_production_seam.py` (4 项) | 实现缺陷（状态机不协调） | `control_run("continue")` 返回了 `RUNNING` 破坏断言，且 `_execute_run_owned` 硬编码 `resumed=False` 导致调度器抛出 `INVALID_RUN_TRANSITION` | 引入 `_resumed_runs` 集合，对外返回 `PENDING`，内部消费 `resumed=True`，调度器非法直接调度保持抛错 |

---

## 5. 全量测试命令与实际结果

- **前端测试**：
  - 命令：`npm test`（目录：`apps/desktop/frontend`）
  - 结果：**Test Files 30 passed (30), Tests 294 passed (294), Duration 2.97s, Exit Code 0**
- **后端 Python 核心测试**：
  - 命令：`& "G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe" -m pytest tests/core tests/storage tests/reading_export tests/pipeline -q -p no:cacheprovider`
  - 结果：**865 passed, 1 warning in 73.68s, Exit Code 0**（0 failed，此前 9 failed 彻底清零）
- **源文件哈希证据**：
  - 路径：`verification/P09/evidence/AC3-source-hashes.json`
  - 结果：**PASS**（两个源文件样本在各阶段保持单一 hash）

---

## 6. 能证明 vs 不能证明

### 能证明
1. AC5 前端交互流程已完整实现并通过 Vitest 自动化测试；
2. Core 侧既有阅读、导出及流水线行为已完全恢复，9 项回归失败彻底修复，全量 865 项 Python 测试与 294 项前端测试全部通过（0 failed）；
3. 永久删除核心防护能力（活动任务/导出预检互斥、跨作品共享 Managed 引用拦截、派生预览联动清理、整库精确匹配判定）均通过真实验证；
4. AC3 源文件零修改保持通过，用户真实 AppData 零触碰。

### 不能证明（Rust 侧待办）
1. `apps/desktop/src-tauri/src/library_bridge.rs` 中 `details.phase` 的白名单限制（受本轮硬约束禁止修改 Rust 文件与 cargo 构建限制，保留为后续待办）；
2. Tauri 端到端二进制打包运行。

---

## 7. 未完成项与下一步推荐操作

- **未完成项**：
  - `library_bridge.rs` 中的 `details.phase` 投影白名单收窄（等待 Rust 锁释放）。
- **推荐下一步**：
  - 交付 Coordinator（Codex）执行正式的二次独立复审（Review R2）；
  - 待 Rust 侧文件编辑锁释放后，合并 `library_bridge.rs` 的 phase 白名单补丁。
