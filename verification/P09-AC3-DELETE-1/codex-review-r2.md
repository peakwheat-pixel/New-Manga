---
task_id: P09-AC3-DELETE-1
reviewer: Codex
author: Antigravity
base_commit: 41bb13679615af557478b85ad6e0bd217f221666
reviewed_head: e44a589a0a49193cf38b9184f30c498bf10bff13
decision: changes_requested
---

# Review：P09-AC3-DELETE-1 第二轮独立复审

审查固定在 `41bb13679615af557478b85ad6e0bd217f221666..e44a589a0a49193cf38b9184f30c498bf10bff13`。Task 登记基线仍为 `baf4ec90c`。本轮未修改产品代码或其他版本化文件；未提交、push、reset/clean，也未运行 `cargo build/test`。

## 1. 结论 decision

**`changes_requested`，不能批准集成或关闭 Task。** R-007 已有真实 UI 和行为测试，但回收站数据源拿到的是未软删除的书，导致入口语义反转；Core 的历史脱离、derived 重试、AC4 证据和契约 phase 白名单仍有缺口。另有实现范围释放未在当前权威 Task 中记录的问题。

| ID | 级别 / 状态 | 依据与最小修法 |
|---|---|---|
| R-007 | P1 / open | 回收站调用只列出未软删除书籍。改用明确包含软删除记录的回收站查询，并以全库现存 Book 数校验整库阻止；增加真实服务数据源断言。 |
| R-001 | P1 / partial | 活动导出查询已接入，但 runtime 查询异常被吞掉并继续删除。失败时应 fail-closed，返回 `BOOK_BUSY` 或稳定的不可用错误。 |
| R-002 | closed | Managed Copy 共享引用及目标外 Revision 引用现在在预检中拒绝；现有用例覆盖这些拒绝场景。 |
| R-003 | P1 / partial | `step_runs.page_id` 先清空，后续输出引用清理再按该字段 join，导致清理目标集合为空；同时删除 `pipeline_stage_states` 历史。先保存目标 `step_run_id` 集合后清理输出引用，并按契约保留/脱离 stage-state 历史。 |
| R-004 | P1 / partial | 初次清理可删除 derived，但 cleanup pending 重试时 DB 已无 page IDs，derived 清理被跳过且 manifest 可被删除。将 page/resource IDs 持久化到 cleanup manifest，重试使用该快照。 |
| R-005 | closed | 管理目录使用 sanitized Book ID、root containment 与 reparse-point 检查；本轮未发现 R1 所述源目录空目录删除路径。 |
| R-006 | P2 / open | v5-only FK 开关、迁移内检查与 SQLite 错误回滚已补齐；非 `sqlite3.Error` 异常仍会在事务未回滚时直接尝试开启 FK（事务内该 PRAGMA 不生效）。finally 中先回滚活动事务，再恢复 FK。 |
| R-008 | P1 / open | AC4 验收脚本对多张表硬编码 `rows=0`，存储检查只打印计数，没有 orphan 扫描/断言；修正真实查询并加入历史 locator 与文件 orphan 断言。 |
| R-009 | P2 / partial | Core 整库集合相等语义已修复；Rust `details.phase` 仍原样透传。只投影固定 `preflight` / `cleanup`，其他值丢弃，并补 Rust 单测。 |
| R-010 | P2 / open | Task 仍 `ready`、`delivery_head: null`、evidence/closeout pending，P09 的 Canonical Evidence/Closeout 也有旧 BLOCKED 内容；更新权威指针和证据 pin。 |
| R-011 | P2 / open | 删除清理仍递归遍历 `storage.root/books/<book_id>`；导出目标只按精确文件路径拦截，未排除落在该目录中的用户导出目录。清理只按已登记的 Managed/derived 目标删文件，不遍历该目录。 |
| R-012 | P1 / open | 当前 Task 与冻结契约都写明“契约冻结不授权实现”，且要求 Codex 另行释放；当前 Task 未记录该释放。先把用户裁决、允许修改范围和 release 记录补入权威 Task/STATUS，再决定该 head 是否可进入批准流程。 |

## 2. R-007 前端闭合确认（含测试是否真断言）

UI 交互主体已经实现，第一轮“完全没有 AC5 产品入口”的 finding 不能原样维持：

- 书架工具栏提供回收站入口，书架没有永久删除按钮；永久删除按钮在 `RecycleBinPage`。`RecycleBinPage.test.tsx` 实际断言了书架无永久删除按钮、回收站入口和回收站删除交互。
- `PermanentDeleteConfirmDialog.tsx:126–164` 按目标逐项显示书名和数量；`:184–191` 有三条提示（应用回收站不可恢复、用户导出文件保留、全库历史备份可能含旧快照）；`:210–218` 有“我理解不可恢复”复选框，未勾选时提交按钮禁用。
- `RecycleBinPage.tsx:86–112` 从打开确认时冻结的 `confirmTargets` 生成 `book_ids`，并由它复制 `confirmed_book_ids`、计算 `confirm_count`；同一快照和顺序成立。`:70–84` 也有 UI 侧批量 20 上限和全库阻止。
- `RecycleBinPage.test.tsx:153–164, 184–237, 255–307` 对提示、复选框、IPC payload 顺序/数量、20 上限和全库阻止做了行为断言，不只是渲染快照。但测试用 `initialBooks` 模拟数据，未覆盖正式列表服务与软删除过滤的集成。

**R-007 仍为 P1。** `RecycleBinPage.tsx:31–35` 调 `activeClient.listBooks()`；此方法最终进入 `LibraryService.list_books()`，而 `src/application/library/service.py:74–77` 明确过滤 `not book.deleted`。因此真实 UI 的回收站列出活动书，软删除的书反而不可见；用户可从回收站永久删除活动书。另 `BookshelfPage.tsx:435–437` 把同一活动书列表长度传为 `totalBooksCount`，所以 UI 的整库阻止也不代表真实全库集合。修复数据源后，仍须让整库判定基于 Core 的全部现存 Book 集合，不能依赖当前可见列表长度。

## 3. Core 四项修复确认

1. **活动导出/任务预检：部分闭合。** `library.py:697–740` 检查非终态 Run、Task、export history，并调用 runtime 的 `has_active_exports_for_book`。但 `:739–740` 用 `except Exception: pass`；runtime 状态不可读时会继续到删除，违反 fail-closed。改成拒绝删除并记录安全错误。正常 `BOOK_BUSY` 路径已有新增测试。
2. **共享 Managed Copy / 跨项目 Revision：已闭合。** `library.py:742–788` 在请求集合外查共享页面/Artifact Managed 路径及 `source_artifact_revision_id` 引用，返回 `BOOK_DELETE_CONFLICT`。`test_core_delete_commands.py:323–407` 覆盖冲突、同批共享和目标外冲突。
3. **历史不残留 ID/locator：未闭合。** `library.py:890–898` 先将关联 `step_runs.page_id` 清空；`:900–909` 随后才通过 `step_runs.page_id` join 找 `step_run_output_refs`。该 join 此时无法命中，`value_json` 不会被清理；而 `pipeline.py:504–508` 确认这里实际写入 `step.output`。另外 `library.py:935–951` 直接删除相关 `pipeline_stage_states`，与契约 §5.11.4 要求保留并脱离历史记录相反。最小修法是事务开始时先冻结受影响的 step-run IDs，再按这些 IDs 清空 output refs；保留并脱离 stage-state 记录。当前没有测试核验上述表的实际写入值。
4. **derived 纳入清理：首次清理已实现，故障重试未闭合。** `library.py:1033–1055` 会通过 catalog 和 page IDs 清理派生 preview，成功路径测试在 `test_core_delete_commands.py:409–442`。但 `book_cleanup_manifests` 只存 managed `targets_json`（`:829–833`）；DB 删除后重试时 `core_service.py:1101–1113` 重新读到空 page IDs，`:1033` 的 derived 分支因此跳过，清理结果仍可能删除 manifest 并报告成功（`library.py:1089–1095`）。需要把 derived resource IDs/targets 一并持久化，故障注入验证 cleanup pending 后重试。

**R-009 的 Core 整库语义已闭合。** `library.py:672–677` 采用请求 ID 集合与所有现存 Book ID 集合完全相等；缺失 ID 时不判成整库，之后 `:687–695` 会返回 `BOOK_NOT_FOUND`。`core_service.py:1154–1163` 先作整库判定，再做预检；新增 `test_core_delete_commands.py:445–463` 覆盖“全部现存 ID + 不存在 ID”。

## 4. 第一版回归的修法正当性（是否弱化断言）

对比 `fdf715e7913798e4c220b09c41d288abdde69b1c`：

- `tests/reading_export/test_export.py`、`tests/reading_export/test_reading.py` 没有改动；其陈旧翻译 Revision 判定断言仍在。
- 当前仓库没有 `tests/pipeline/test_pipeline.py`；实际相邻文件 `tests/pipeline/test_pipeline_production_seam.py` 只把 fixture 的 `latest_known_schema_version=3` 改为最新 migration schema version，没有删除或放宽断言。
- Schema v5 相关测试更新了版本期望和 fixture。`tests/storage/test_purge_integrity.py` 将 PRAGMA 期望的页面外键表缩小到 v5 保留的 FK 表，同时仍检查既有依赖表行数。这不是删除用户点名的阅读/导出/流水线行为断言，但它确实把部分 page 关系完整性从 SQLite 约束改成应用层语义责任；须由迁移/删除测试补足 dangling ID 与回滚检查。

因此，**9 个回归的修法没有通过弱化用户点名的三组既有行为断言来消红**。Owner 报告的初次失败根因中，阅读器/导出 stale 条件恢复了既有翻译 Revision 判定，pipeline resume 改为与现有 `PENDING` 外部契约一致并在调度内部传递 resumed 状态；本轮回归结果见 §10。不能据此推定 derived retry 或 AC4 正确，它们没有被现有测试覆盖。

## 5. 契约一致性

- **通过静态核对的部分：** 单条 `PermanentlyDeleteBook` 保持 rev 2.9 payload；批量使用独立 `PermanentlyDeleteBooks` / `library_delete_books_permanently`。Core protocol minor 为 10，Tauri DTO 字段与冻结契约一致，Rust 单/批 DTO 使用 `#[serde(deny_unknown_fields)]`，Core 也作 exact-key 校验。新增命令列在生产 surface/ACL；静态命令目录为 60 条（53 production、4 probe、3 AC1），删除命令不在 probe/AC1 surface。生成 allow/deny permission 均存在。未运行 Cargo，故这里只是源码/配置静态核对，不是 Rust 编译验收。
- 成功和错误 DTO、批量上限/重复 ID/确认同序/count、稳定错误码总体匹配 rev 2.10；Core 的整库语义已纠正。
- **R-009 phase 白名单未闭合。** `library_bridge.rs:265–268` 将 `details.phase` 任意字符串原样投影。契约 `M2-C1_TYPED_IPC_CONTRACT.md:755` 只允许 `preflight` / `cleanup`。即使当前 Core 只发固定值，host 对输入仍未执行白名单；CLOSE-BOUND 正在占用该文件是协调理由，不是契约例外。此项为 P2，但在本 Task 获批前仍须修复或由有权方正式修订契约。

## 6. P0 源文件零改动

**源文件保护路径通过本轮代码审阅，证据支持 AC3 的源样本不变结论。** 删除目标来自 `managed_original_ref`、`artifact_revisions.managed_path` 和受控 cleanup manifest（`library.py:630–661`）；我未发现把 `source_filename` 或 `source_hash` 转成授权路径/删除目标的分支。导出 history 只清理 DB 行的 ID/snapshot 字段，不读 `output_path` 来删文件。Managed 文件删除仍走受控 storage API；derived 文件依据 resource catalog 与 Page ID 删除。

源样本的 `AC3-source.png` 与 `AC3-workflow-source.png` 当前磁盘 SHA-256 分别为 `36452bb8d135ac96f1c453e11c23689d5917a2f0db42d154aca02722507153d7`、`ee5f4ae0aae66a3d9ad8166933132bf2fad25da6220d8f02127f69546b5a4795`；`AC3-source-hashes.json` 两个 case 各自的各阶段（包含项目永久删除后）只记录一个 distinct hash，与当前文件相同。此结论只覆盖样本和受审路径，不替代真实用户数据的前后比对。

**导出目录保护有额外缺口（R-011，P2）。** `library.py:1057–1083` 对 `storage.root/books/<book_id>` 执行 `os.walk` 并尝试移除空目录。`core_service.py:2421–2437` 的导出目标保护仅拒绝与现存 Managed 文件完全相同的路径，没有拒绝位于该 Book 管理目录下的用户导出目录。若用户把导出目录选在此子树内，删除会遍历其中路径，且可能移除空子目录。虽然有文件的导出目录不会被 `rmdir`，但契约 §5.11.4 明确禁止遍历/修改用户选择的导出目录。应取消整棵目录 walk，仅按 manifest/catalog 中逐项登记的 Managed/derived 文件清理，并排除导出 target scope。

## 7. Schema v5 安全性

`schema.py` 的 v5 迁移重建 pipeline 相关表并移除对 `pages(page_id)` 的 FK，保留字段和索引、复制既有行；这样可以让历史行在 Page 删除后继续存在，但 removed FK 不再能验证这些列的语义关联。当前 `step_run_output_refs` 清理顺序问题正说明仅靠 `PRAGMA foreign_key_check` 不足以证明历史脱离。

`migrator.py:141–182` 现在只在 `schema_version == 5` 时关闭 FK；迁移 SQL、`PRAGMA foreign_key_check`、migration 记录及 metadata 更新处于事务，SQLite 异常时 rollback，finally 恢复 FK。**异常边界仍不完整：** `except sqlite3.Error` 之外的异常会跳过 rollback，finally 在事务未结束时执行 `PRAGMA foreign_keys=ON`；SQLite 在事务内不会应用该设置。建议 finally 若 `conn.in_transaction` 先 rollback，再恢复 FK，并增加故障注入测试确认失败后连接状态恢复。

所以 v5 的正常路径和 SQLite 错误路径具备迁移隔离/剩余 FK 检查；`foreign_key_check` 已存在，不需要再重复添加同一 pragma，但应增加覆盖被移除 FK 列的应用层历史脱离断言、数据复制保持及异常回滚/外键恢复测试。

## 8. AC6 回补是否成立（含 `tree_sha256` 定性）

**P09 AC3 的“源文件零修改”这一窄项成立。** 当前文件字节 hash 与 `AC3-source-hashes.json` 一致，各生命周期阶段 hash 恒定；源文件路径未被删除代码授权。关于 `appdata_protection.tree_sha256`：Coordinator 声称的不可复现结果不能复现，是因为用了不同的拼接格式。`verify_all.py:50–68` 明确按路径排序并拼成相对路径、size、文件 SHA-256 的记录后再计算树 SHA；按该脚本口径独立重算得 `7136daeb82e32c3e08b3411fa3c9ebc1cba57448d33570bec21ce8d0e64307af`，与 evidence 相同。因此这不是当前真实 hash 的证据缺陷；Coordinator 的 `rel:hash` 结果不能与该算法直接比较。24 文件、1,768,641 bytes 也与其记录吻合。

但 **AC6 整体仅 PARTIAL**：`doc/tasks/P09.md:128–131` 的 Canonical Evidence 仍将 `AC3-MATRIX` 标为 `partial / blocked`，仍 pin 旧 `AC3-DELETE-BLOCK`，没有把新项目删除后的证据 hash/commit 加入该表；`:159–162` 的 Closeout Record 仍写 AC3 受限、项目级删除不存在。与此相反，`:59` 和 `verification/P09/AC-STATUS.md:14,34–35` 已写完成。证据内容可以支持源不变，但当前 P09 权威 pin 和关闭记录相互矛盾，不能判 AC6 完整闭环。按 Task AC6 补齐 P09 Canonical Evidence 与 closeout 状态，不得只改 AC3 文案。

## 9. 越界

**权威范围未释放（R-012，P1）。** `doc/tasks/P09-AC3-DELETE-1.md:35,111,122,135–142` 写明 AC1 冻结不授权实现；剩余裁决与 Codex 更新实施范围前不得开始 AC2–AC7。共享契约 `M2-C1_TYPED_IPC_CONTRACT.md:1200,1224` 也明确 Core/Tauri/React、Schema/migration、ACL 与生成物尚未授权。当前 Task 没有后续的 release 记录，反而仍是 `status: ready`、`delivery_head: null`，Canonical Evidence 和资源 closeout 均 pending。即使 STATUS 有产品方向性裁决摘要，也不能替代 Task 中要求的具体实现范围释放。当前 head 的 Core/Tauri/React、Schema v5 和生成 ACL 实现不能仅凭 handoff 或 review 请求视为已获准；Codex 应先在权威 Task/STATUS 记录裁决、allowed paths 与 release，再作集成批准。

另，Coordinator 已登记 `41bb13679` 将用户此前未提交生成文件误纳入提交。本轮独立确认该提交包含 `apps/desktop/src-tauri/gen/schemas/**` 和 `permissions/autogenerated/**` 生成路径；这是 Coordinator 记录的提交保管事故，不归因给 Antigravity 的本轮代码修复，也不应通过 reset/clean 或覆盖文件来“修正”。保留原状态，后续按仓库工作区治理逐项核对来源、引用和提交归属。

## 10. AC1–AC7 与 P09 收口影响

| AC | 结论 | 依据 / 限制 |
|---|---|---|
| AC1 契约先行 | **PARTIAL** | rev 2.9/2.10 命令、payload、协议 minor、ACL 与 unknown-field 拒绝静态一致；Rust phase 白名单 R-009 未闭合，且实现授权未在 Task 记录。未运行 Cargo。 |
| AC2 永久删除可用 | **PARTIAL** | Core 单/批删除、共享资源冲突、whole-library 与正常 managed/derived 清理存在；R-001 fail-open、R-004 重试及 R-007 回收站数据源仍阻断可用性。 |
| AC3 源文件零改动 | **PASS（本 Task 样本/代码路径）** | 两样本磁盘 hash 与全阶段证据一致；未发现 `source_filename`/`source_hash` 路径授权。 |
| AC4 无内容/文件残留 | **FAIL** | R-003 历史输出引用未正确清理且 stage-state 历史被删；R-004 可遗留 derived；R-008 验收脚本存在恒真零行和无 orphan 断言；R-011 可能遍历用户导出目录。 |
| AC5 误删防护 | **FAIL** | UI 确认交互/文案/同快照与行为测试存在，但真实回收站数据源展示活动书而非软删除书，整库 UI 分母也不可信（R-007）。 |
| AC6 回补 P09 AC3 | **PARTIAL** | 源文件 hash 回补成立；`tree_sha256` 按证据脚本算法可复现；P09 canonical pin/closeout 仍是旧 BLOCKED 记录。 |
| AC7 不回归 | **PASS（已执行测试覆盖范围）** | 点名的导出/阅读测试未改；pipeline 相邻 test 只改 schema fixture，无断言弱化。全量测试执行受本地 Python 环境的 3 个 collection error 限制，详见下表。 |

**验证记录：**

| 命令 / 检查 | 结果 | 说明 |
|---|---|---|
| `npm test`（`apps/desktop/frontend`） | **PASS：30 test files、294 tests** | 本轮实际执行，Vitest exit 0；这些交互断言存在，但 mock 未覆盖真实回收站数据源。 |
| `pytest tests/core tests/storage tests/reading_export tests/pipeline -q` | **本地 NOT_RUN 完整集 / 采集失败** | 本地默认 Python 3.14 collection 时，3 个文件因 `ModuleNotFoundError: No module named 'tests'` 退出；文件为 `test_p09_fu2_import_pages.py`、`test_page_catalog_modes.py`、`test_pipeline_defaults_assembly.py`。这不是测试断言失败。 |
| 忽略上述 3 个 collection-error 文件重跑剩余模块 | **829 passed, 1 warning** | exit 0。 |
| 针对删除/迁移/阅读/导出/pipeline seams 的 focused pytest | **71 passed** | exit 0；含 `test_core_delete_commands.py`、schema migration、指定 reading/export 和 pipeline seam。 |
| Coordinator Python 3.12 全量结果 | **报告为 865 passed** | 本轮未在其 Python 3.12 task-env 中独立复跑；与本地不同环境，作为交付报告证据引用而非本轮复现结果。 |
| `verify_all.py` / Cargo | **NOT_RUN** | 不运行会写验收 evidence 的整合脚本；遵守 CLOSE-BOUND 同 crate 约束，不运行 Cargo。 |

所以，**P09 AC3 的源哈希阻塞可以在 AC3 这一窄范围解除，但不能据此宣告本删除 Task 完成，也不能把 P09 整体收口为完全闭环**。建议下一步：由 Codex先把用户裁决与实现 release/allowed paths 写入 Task；随后由 Antigravity 在获准范围内修复 R-001、R-003、R-004、R-007、R-008、R-011 和 R-009 phase，补齐故障注入/历史脱离/orphan 测试及 P09 canonical pins；再交 Codex 对新固定 head 复审。
