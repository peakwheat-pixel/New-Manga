---
task_id: P09-AC3-DELETE-1
reviewer: Codex
author: Antigravity
base_commit: fdf715e7913798e4c220b09c41d288abdde69b1c
reviewed_head: 41bb13679615af557478b85ad6e0bd217f221666
decision: changes_requested
---

# Review：P09-AC3-DELETE-1 首次独立复审

审查固定在 `fdf715e7913798e4c220b09c41d288abdde69b1c..41bb13679615af557478b85ad6e0bd217f221666`；重点覆盖实现提交 `d9f7a628c` 与 HEAD `41bb13679` 中 P09 相关生成 ACL/schema 文件。Task frontmatter 所登记基线为 `baf4ec90c`。HEAD 上存在大量既存 dirty/untracked 文件，本次未改动它们。

## 1. 结论 decision

**`changes_requested`，不可批准集成或关闭 Task。** Standards 轴发现路径/关系边界、迁移与证据门控问题；Spec 轴发现 AC4、AC5 及删除预检要求未满足。主要阻断项：活动导出可与删除并发；共享 Managed Copy 和跨项目 Revision 引用未拒绝；历史记录仍含删除对象 ID/locator；derived 文件没有纳入清理；AC5 没有 UI 入口；迁移与 AC4 验收存在安全/证据缺口。

## 2. 契约一致性

- **静态核对通过的部分：** 单条 `PermanentlyDeleteBook` 和批量 `PermanentlyDeleteBooks` / `library_delete_books_permanently` 名称、payload、返回形状、协议 minor `10` 与冻结值一致。Core 逐字段 closed-shape 检查；Rust DTO 使用 `#[serde(deny_unknown_fields)]`，通过 `serde_json::from_value` 解析，未知字段会拒绝。错误码映射覆盖契约列出的单条/批量错误，批量 item 错误码使用白名单。HEAD 上 ACL 有 allow/deny 自动生成项，capability 与 `build.rs` 注册两条命令；`PRODUCTION_COMMANDS` 为 53，probe 与 AC1 handler 排除删除命令，生产 handler 注册两条，合计 60 条。
- **R-007 [P1] AC5 的产品入口和二次确认缺失。** `d9f7a628c` 没有改动 React/frontend；`apps/desktop/frontend/src` 中也没有两条删除命令调用。Core 确认字段只证明 IPC 请求形状正确，不能替代“只在回收站显示、列出精确目标/数量、第二次勾选确认”的 AC5/§5.11.1 产品交互。当前能力只能由直接 IPC 调用触发。
- **R-009 [P2] 两处小型契约偏差。** `library.py:662–667` 用“所有现存 ID 是请求 ID 的子集”判定清空整库；当请求含全部现存 ID 加一个不存在 ID 时，返回 whole-library 而非预检的 `BOOK_NOT_FOUND`。`library_bridge.rs:263–270` 将 Core `details.phase` 原样复制，未限制为 `preflight|cleanup`，不符合 host 固定白名单投影要求；当前 Core 仅产生固定值，尚无已观察到的路径泄露。

## 3. ★ P0 源文件零改动复核

**源文件字节路径通过。** `list_book_cleanup_targets`（`library.py:629–660`）只收集 `managed_original_ref`、`artifact_revisions.managed_path` 和持久 manifest；删除路径不把 `source_filename` 或 `source_hash` 当作路径授权。`cleanup_book_files` 只调用 `storage.remove_managed`，不访问 `export_history.output_path`，也不遍历用户导出目录。`remove_managed` 会校验 Managed root containment、词法路径和目标路径 reparse point（`managed_storage.py:125–178`）。因此实现中没有将源文件名/hash转换成删除路径的分支。

我在隔离运行中复算并验证了两个原始源样本在整个工作流各阶段 hash 不变：`AC3-source.png` 为 `36452bb8d135ac96f1c453e11c23689d5917a2f0db42d154aca02722507153d7`；`AC3-workflow-source.png` 为 `ee5f4ae0aae66a3d9ad8166933132bf2fad25da6220d8f02127f69546b5a4795`。**边界瑕疵 R-005 [P2]：** `library.py:893–908` 对 `(root / "books" / book_id).resolve()` 直接 `os.walk`/`rmdir`，没有 containment 或 reparse 检查；若此目录是指向源目录的 junction，或数据库中出现带路径分隔符的 ID，可能删除源目录中的空子目录。该分支只 `rmdir` 空目录，不 unlink 文件，故不推翻本 AC3 的源文件字节结论，但违反目录边界保护，应修复。

## 4. 事务与部分失败语义

`execute_permanent_delete_db`（`library.py:738–878`）将内容删除、历史更新和 manifest 写入包在一个 `with self._conn` 事务内；任一 SQL 异常由 SQLite context rollback，调用方在 DB 阶段失败时返回 `BOOK_DELETE_FAILED`，不会进入文件清理。DB commit 后逐本清理；失败项保留 manifest，批量返回 `BOOK_DELETE_BATCH_CLEANUP_PENDING` 与有序 `deleted/cleanup_pending` 状态；重试只能通过显式命令完成。完成后 manifest 被删，已完成 ID 重放会预检为 `BOOK_NOT_FOUND`。这些实现没有谎报 cleanup 成功。

- **R-001 [P1] 预检不是同一一致性边界，且漏掉进行中的导出。** 预检和目标枚举发生在删除事务之前（`library.py:669–737`），期间 Core 的 pipeline scheduler 可并发启动/恢复 Run。导出由 `P16ExportRuntime.start` 在后台线程执行（`service.py:748–793`）；删除预检只查 `export_history`（`library.py:702–707`），而该表 schema 只允许 `completed/skipped/cancelled/failed` 终态（`schema.py:437–452`），pending/running job 存在于 runtime job store，不会被该查询发现。可复现场景：导出正读取目标 Book 的 Managed Copy 时发起删除，DB 删除并 unlink 输入文件，导出任务失败。应将 Run/Task/Export 状态检查与删除准入协调到同一保护边界。
- **R-002 [P1] 未验证目标外资源引用，且会改写其他 Book。** `preflight_permanent_delete` 只确认路径位于 Managed root，不检查其他 Book 是否引用相同 `managed_path`。两个 Book 指向同一个合法相对路径时，删其中一个会 unlink 另一个仍引用的文件。另 `library.py:840–848` 无条件把所有指向目标 Revision 的 `source_artifact_revision_id` 置空，包括其他 Book 的 Revision，静默破坏其 lineage。契约要求目标外引用预检失败并整批零副作用；这里应返回 conflict，不能修改其他项目。

## 5. Schema v5 迁移安全性

v5 通过重建四张 pipeline 表并复制原列，移除它们对 `pages(page_id)` 的物理 FK，保留了列与索引；正常迁移可由 `MigrationRunner` 逐版本事务和预迁移备份回滚保护。但移除 FK 让 dangling page IDs 不再由 SQLite 检测，只有在历史 ID/locator 真正脱离后才安全；当前实现未完成（见 R-003）。

- **R-006 [P1] FK 开关范围和异常恢复有缺口。** `migrator.py:141–170` 对每个 migration 都先 `foreign_keys=OFF`，不只 v5；`BEGIN IMMEDIATE` 位于 `try/finally` 之外，若 BEGIN 因锁/错误失败，恢复 `foreign_keys=ON` 的 finally 不会执行。迁移提交前也没有 `PRAGMA foreign_key_check`。这会在失败后留下同一连接 FK 关闭状态，也让非 v5 migration 不必要地绕过约束。应只对 v5 关闭，并确保 BEGIN 失败也恢复；提交前检查 FK。

## 6. 保留语义与批量防护

- **R-003 [P1] Pipeline / export 历史并未脱离已删对象。** `library.py:757–835` 只写入 `book_title`、清空部分 JSON；仍保留 `run_json.scope.book_id`、`requested_targets_json`、`pipeline_run_targets.page_id/target_id/region_id`、`pipeline_tasks` / `step_runs` 的 page/target IDs、`step_run_input_refs.revision_id`、candidate `base_revision_id`、`pipeline_stage_states.target_id`。`export_history.book_id/chapter_id/scope_snapshot_json` 同样只追加标题而未清理 ID。`PRAGMA foreign_key_check=0` 不证明它们 detached，因为 v5 已删相应 page FK。书名快照确实写进 pipeline `run_json` 和 export scope snapshot，但 export 历史 DTO/runtime 没有把 `book_title` 投影给 UI，不能据此认定可展示。
- **R-004 [P1] Derived/Cache 资源没有纳入清理清单。** 清单只读 Managed Copy 与 artifact revision 路径；Core 的 `handle_resolve_page_resource` 会通过 `RenderPreviewPublisher.publish_original` 生成 `page-original-{page_id}` 到独立 derived root/catalog（`core_service.py:1810–1825`、`render_preview.py:87–120`），永久删除未查询/删除 catalog entry 或派生文件，留下目标页派生副本。
- 共享 tags/global metadata 保留、用户导出文件不触碰；批量 1..20、重复拒绝、确认 ID 同序相等与 count 匹配、whole-library 保护、全量预检失败、DB 事务、pending 错误和显式幂等重试均在 Core 校验。除 R-009 的 whole-library 过宽匹配外，未发现 Core 侧绕过这些批量防护的调用分支。

## 7. AC6 回补是否成立（含 tree_sha256 缺陷判定）

**P09 AC3 的源文件哈希回补成立。** 我执行了 `verify_all.py` 的完整隔离工作流（将脚本 evidence 输出路径仅在进程内重定向到 `%TEMP%`，避免覆盖仓库 evidence），退出码 0；两份样本在导入、软删除、Page purge、真实 `TRANSLATE_ALL` / `REINPAINT_REGION` / `RERENDER_SINGLE`、项目级单条/批量删除各阶段保持原 SHA-256，用户导出文件亦未变。对 `appdata_protection.tree_sha256` 的判断：**不构成证据缺陷**。脚本 `verify_all.py:49–62` 已明示算法（按 `str(Path)` 排序，拼 `rel.as_posix()|size|sha256`，用 `\n` 连接且不加末尾换行）；我用该脚本复算得 `7136daeb82e32c3e08b3411fa3c9ebc1cba57448d33570bec21ce8d0e64307af`，前后相同，24 文件 / 1,768,641 bytes。Coordinator 用 `rel:hash` 的另一算法得出不同值，不能据此判坏。

- **R-008 [P1] AC4 证据有恒真/不充分断言。** `verify_all.py:206–209` 与 `327–330` 对无 `book_id` 列的 `pages/regions/revisions/artifacts` 等表使用 `else 0`，没有 SQL 查询仍断言零行；`:347–350` 的 FK 检查因 page FK 已删除，不能证明 pipeline 历史无 dangling IDs；`:366–370` 只打印 Managed/Derived 文件数量，没有 orphan 扫描或零 orphan 断言。并且本次验证中 Derived root 从 0 files 开始，因此没有覆盖被遗漏的 derived page copy。故 `p09_ac3_delete_evidence.json` 中 AC4 PASS 不可采信，AC4 应保持未通过。

## 8. 回归

| 验证 | 结果 |
|---|---|
| `pytest tests/core tests/storage/test_schema_migration.py -q -p no:cacheprovider` | **553 passed**, 1 个既有 Pillow deprecation warning，exit 0 |
| `pytest tests/library/test_p09_managed_copy_safety.py -q -p no:cacheprovider` | **7 passed**, exit 0 |
| 隔离运行 `verification/P09-AC3-DELETE-1/verify_all.py` | **exit 0**；源文件/用户导出/AppData 哈希通过；不采信其 AC4 恒真断言 |
| Rust `cargo build/test` | **NOT_RUN**；遵守同 crate 并行 Task 约束 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS**，2 个 STATUS/Plan 体积预算 warning |

## 9. 越界

`d9f7a628c` 的 23 个路径均落在 Task 允许范围：Core/Tauri、相关 schema/Core tests、本 Task 与 P09 状态/证据文件；没有改动源样本或 `AppData`。该提交**没有前端文件**，属于 AC5 缺失而非越界。HEAD 的 `41bb13679` 另加入 4 个 Tauri schema JSON 和 2 个 autogenerated permission TOML；其 allow/deny 名称与当前命令正确。

另行登记：Coordinator 已承认 `41bb13679` 误将用户 23 个未提交生成文件一并提交。该事故与 `d9f7a628c` 的 P09 文件清单分开；P20 文件不能归属为 P09 实现或复审通过。原 43 项 dirty/untracked 状态在审查前已存在，本次未 reset/clean/改写；除本 review 文件外未写仓库文件。

**R-010 [P2] 当前权威 Task 指针未进入 Review/交付状态。** `doc/tasks/P09-AC3-DELETE-1.md` 仍为 `status: ready`、`delivery_head: null`、`canonical_evidence_status: pending`，同时 AC1–AC7 checkbox 已全勾；`doc/STATUS.md` 仍描述 P09 “契约第 2 次冻结进行中”。这不满足可关闭的交付记录要求；本 review 不更新 Task/STATUS。

## 10. AC1–AC7 达成情况与 P09 收口影响

| AC | 复审判定 | 依据 |
|---|---|---|
| AC1 契约先行 | **PASS** | rev 2.10、API/ACL/protocol 静态匹配；R-009 为小型投影/整库匹配偏差。 |
| AC2 项目级永久删除 | **PARTIAL** | DB 删除和 Managed Copy 清理可用；活动导出竞态、跨项目资源引用和 derived 清理未解决。 |
| AC3 源文件零改动 | **PASS** | 原始样本逐阶段 hash 独立复算/隔离复跑相同；无 source filename/hash 路径授权或导出目录遍历。 |
| AC4 无内容/历史/文件残留 | **FAIL** | Pipeline/export locator 未脱离；derived 副本残留；验收脚本对零行/零 orphan 的证据无效。 |
| AC5 误删防护与语义区分 | **FAIL** | Core 校验通过，但缺少回收站入口和第二次确认 UI。 |
| AC6 回补 P09 AC3 | **PASS（仅 AC3 范围）** | 哈希回补充分，tree hash 可复现；Task canonical evidence/closeout metadata 仍 pending。 |
| AC7 不回归 P09 既有项 | **PASS（本轮覆盖范围）** | P09 managed-copy tests 7/7，隔离真实流程中导入、软删除、Page purge、三个 workflow 与源 hash 全通过。 |

因此，**P09 原 AC3 的 BLOCKED 源哈希路径可以移除**，但 `P09-AC3-DELETE-1` 不可关闭，P09 产品级永久删除仍不能作为完整可用功能收口。建议下一步由 **Antigravity** 在本 Task 范围修复 R-001–R-008、补齐 AC5 UI 和可复核 AC4 证据，更新 Task/Handoff 与 canonical evidence，再由 **Codex** 对新 head 独立复审；R-010 状态在交付阶段同步。
