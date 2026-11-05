---
task_id: FEA-12-CORE
reviewer: dsh-fea12-core-r1 (fresh subagent; session b2e5e275-122b-44d4-98bc-c86fec7bfbc1)
reviewer_kind: subagent
review_session_id: b2e5e275-122b-44d4-98bc-c86fec7bfbc1
parent_agent_id: session-8db9dae5-49df-4d09-ac62-696f0805a95c
base_commit: e47fd47e41add3edeb7f67e578eefeb48eddce50
reviewed_head: 85db8354f5d62a93db0a76a784899ddbfe8a405b
observed_head: 388f5476ef39043e8f946026649c5bb629d9fc20
decision: changes_requested
---

# Review：FEA-12-CORE（A 软删/恢复/ListTrash + C 彻底删除 + 统一 ProtectionPolicy + Host 命令桥）

> 审查身份：独立上下文 fresh subagent，未参与本任务的实现、返修或分片设计；会话 `b2e5e275-122b-44d4-98bc-c86fec7bfbc1`，父会话 `session-8db9dae5-49df-4d09-ac62-696f0805a95c`。
> 审查范围：`base_commit=e47fd47e` → `reviewed_head=85db8354f`；`.NET` 与 Python 源码、测试、任务卡、证据、冻结契约、Git 历史。
> 审查方式：只读仓库；所有测试日志、探针输出、变异实验和本报告均写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-core\`；未 commit、未 push、未修改任何仓库文件。仅一次 `git checkout -- verification/FEA-09` 用于回滚我运行全量 .NET 测试造成的既有证据重写（测试副作用，非他人改动），回滚后工作树 clean。

## 0. 结论摘要

**P0=0，P1=0，P2=3，P3=8。decision: changes_requested。**

代码主体质量高：A/C 流程、digest 两级绑定、显式 `BEGIN IMMEDIATE`、失败整体回滚、D1 X1 同事务删除、PD-08 安全拆分、PD-07 显式重试、typed `PurgeTrash`、Host capability probe/R-002(b) 都真实实现并有判别测试。我独立复跑：相关组 **1096 passed**、定向组 **72 passed**、全量 pytest **3144 passed / 10 skipped / EXIT 0**、全量 .NET **1405 passed / 0 failed / 80 skipped / EXIT 0**、pins **18/18**、check **PASS (3 warnings)**、旧 Core 侧车 **6 passed / 0 failed / 0 skipped**。三个变异实验（去掉 X1 删除、去掉 digest 比较、去掉 PD-08 置 NULL）都精确复现失败，证明测试不是空转。

但存在 3 个 P2，使当前 reviewed head **不能按 AC4/AC11 MET 直接收口**：

1. **AC4/C-04b 的 `deletedFiles`/`deletedBytes` 漏计派生预览文件**：冻结的 PD-01/C-04b 写的是“managed/派生文件数与字节量”，实现只统计 managed 内容文件；`cleanup_book_files` 实际还会删除 catalog preview/page-original 派生文件。我用隔离探针复现：预览报 `deletedFiles=1, deletedBytes=13`，同时存在一个 13 字节的派生文件，二者相加才是实际删除量。记录 §6.5 已如实登记，但这不是契约允许的排除，且 AC4 仍标 `MET`。
2. **AC11 未合并定稿**：在 `85db8354f` 与审查期间出现的 `388f5476e` 上，AC11 仍是 `<<PARTIAL...>>`；`388f5476e` 只把分片 B 证据加入 Canonical Evidence 表，没有把 AC11 改成最终口径。分片 B 的代码与证据已实际集成并有独立实测，但 AC 状态需 Lead 定稿。
3. **分片 A 改了 allowed_paths 外的 `tests/core/test_core_service.py`**：`5fb300fd2` 的 6 个测试文件含该文件（capability 列表断言，属预期行为变更 #4），但 `doc/tasks/FEA-12-CORE.md:22-49` 的 allowed_paths 未列它；Handoff `:27` 明确列了它、`:120` 却称“已入 allowed_paths”，与实际不符。

此外有 8 个 P3（证据/文档精度、死代码、批量 retry 契约边角、竞态错误码、预检盲点、测试弱断言），均不改变“无 P0/P1、无数据丢失或安全越界”的结论。

## 1. 审查对象与 HEAD 变化

- 开始审查时：`HEAD=85db8354f`，工作树有 1 个 untracked 文件 `verification/FEA-12-CORE/logs/gates-integration.log`（Lead 集成日志当时尚未入仓）。
- 审查期间 Lead 提交 `388f5476e`（17:08）：仅新增该集成日志与 12 行 Canonical Evidence 表（分片 B/集成证据），**`src`/`tests`/`apps` 零 diff**。`git diff 85db8354f..388f5476e -- src tests apps` 为空。
- 因此本报告对 `85db8354f` 的代码结论同样适用于当前 head；运行门禁均在 `388f5476e`（源码等价）实跑。当前工作树 clean，`HEAD=388f5476e`。
- `origin/main=b1c1f5a5...` 不包含 `85db8354f`/`388f5476e`，未发现 push；`main` 领先 origin 是本地集成提交。

## 2. Findings

### P2

| ID | 级别 | 文件/行 | 问题 | 证据/复现 | 最小返修建议 |
|---|---|---|---|---|---|
| **R-001** | **P2** | `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md:44,46`；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md:58`；`src/infrastructure/sqlite/library.py:1026-1057,1381-1399,1475-1476,2011-2084`；`verification/FEA-12-CORE/core-py-implementation-record.md:139-140`；`doc/tasks/FEA-12-CORE.md:72` | 冻结语义要求 `deletedFiles/deletedBytes` 覆盖“managed/派生文件”；实现只统计 managed page/artifact/manifest 路径，**漏计 catalog preview 与 page-original 派生文件**，但 `cleanup_book_files` 实际会删除它们。AC4 仍标 `MET`。 | 仓外探针 `derived_disclosure_probe.py`：预览返回 `{"deletedFiles":1,"deletedBytes":13}`，同时派生文件存在且为 13 bytes；清理测试 `tests/core/test_core_delete_commands.py:1039-1042` 证明该派生文件会被删除。记录 §6.5 自认“不计入”。 | 二选一：① 预览把派生预览资源/字节计入（或至少给出明确计数口径）并新增判别测试；② 由 Lead/DSH 作出 additive 解释，明确 `deletedFiles/deletedBytes` 仅指 managed 内容文件、派生缓存不属于 PD-01 披露，并同步 AC4/C-04b 引用口径。不建议保留“记录里登记了但 AC 仍 MET”的现状。 |
| **R-002** | **P2** | `doc/tasks/FEA-12-CORE.md:79`、`:122`；`verification/FEA-12-CORE/core-host-implementation-record.md:6,80-90`；`388f5476e` diff | AC11 在 reviewed head 与当前 head 均为 `<<PARTIAL>>`；分片 B 已交付（`9ebb812b0`）且证据已由 `388f5476e` 合并，但 AC11 未改成最终口径（MET 或明确剩余项）。任务卡 `integration_commit`/`delivery_head` 仍为 null。 | `git show 388f5476e -- doc/tasks/FEA-12-CORE.md` 只加证据行；当前 `:79` 仍 PARTIAL。B 侧代码/证据已核。 | Lead 在 closeout 前把 AC11 改为最终判定：分片 B 证据充分，建议 `MET`；同时填 `integration_commit=388f5476e`、`delivery_head`。若仍保留 PARTIAL，必须写明剩余阻塞项。 |
| **R-003** | **P2** | `doc/tasks/FEA-12-CORE.md:22-49`、`:116`、`:136`；`5fb300fd2`；`doc/handoffs/FEA-12-CORE-core-py.md:27,120` | 分片 A 修改了 allowed_paths 未列的 `tests/core/test_core_service.py`（+6/-6，capability 列表精确断言）。任务卡预期行为变更 #4 又明确说该测试会更新。Handoff 声称“已入 allowed_paths”，与实际不符。 | `git show --stat 5fb300fd2` 列该文件；当前 allowed_paths 无该路径；`git diff e47fd47e..85db8354f -- tests/core/test_core_service.py` 为 capability 列表更新（非删测试/非放宽）。 | Lead 在任务卡 allowed_paths 补 `tests/core/test_core_service.py` 并记录该窄批；或要求以另一个 allowed 测试载体完成同一断言。不要以“测试改动无害”替代范围纪律。 |

### P3

| ID | 级别 | 文件/行 | 问题 | 证据 | 建议 |
|---|---|---|---|---|---|
| R-004 | P3 | `verification/FEA-12-CORE/scripts/core_py_isolation_scan.py:53,126-131,195-201`；`verification/FEA-12-CORE/evidence/core-py-isolation-scan.json:11` | `data_root_under_workspace_temp` 用 `str(WORK_ROOT) in str(parents)` 判断；`str(parents)` 会给反斜杠加转义，Windows 上恒为 false（追踪证据也是 false），而 `runtime["pass"]` 根本没把这个字段纳入判定，所以 `pass:true` 与该字段自相矛盾。`DRIVE_PATH` 正则定义后未使用，真实盘符未扫描。 | 我复跑补丁版探针：`data_root=...\workspace\temp\FEA-12-CORE\evidence-isolation\data`，`data_root_under_workspace_temp=false`，`pass=true`；追踪证据同样 false/true。 | 改为 `Path(core.data_root).resolve().is_relative_to(WORK_ROOT.resolve())` 并纳入 `runtime["pass"]`；如保留“真实盘符”措辞，实际使用 `DRIVE_PATH` 或收窄 AC12 措辞为“删除实现模块/探针”。 |
| R-005 | P3 | `doc/tasks/FEA-12-CORE.md:111`；`doc/handoffs/FEA-12-CORE-core-py.md:76`；`verification/FEA-12-CORE/logs/gates-core-py.log:47-50` | “本卡新增测试 51 条”实为 **整个 base→head 区间的测试函数增量**：CORE 43 条（delete 20→28 +8、preview 0→9、trash 0→14、protection 0→11、purge 9→10），DSIM-1 另有 8 条（`tests/fea12/test_recycle_gateway_sim.py` 13→21）。Gate 日志又把 protection 写成 8（实际 11）。 | 计数来源见各文件 `def test_`；3093+51=3144 与全量实跑一致，但 51 不能全部归本卡。 | 把 51 拆为“CORE +43 / DSIM-1 +8”；gates-core-py.log 的 protection 计数改为 11，或给出“仅 policy 子集 8”的说明。 |
| R-006 | P3 | `doc/tasks/FEA-12-CORE.md:90-97,17-18` | “测试要求”表仍全部 `NOT_RUN`，与 `:109-115` 的实跑记录、`gates-integration.log` 矛盾；`integration_commit`/`delivery_head`/`canonical_evidence_status` 仍 pending/null。 | 当前文件原文；388f 只加了 Evidence 表。 | closeout 前更新测试表为实跑结果/证据路径；填 integration/delivery 指针。 |
| R-007 | P3 | `src/domain/books/entities.py:100-109`；`src/infrastructure/sqlite/library.py:954-963` | `Book.restore()` 已新增但**零调用点、零测试**；实际 `RestoreFromTrash` 直接执行 SQL `UPDATE books SET deleted_at=NULL, updated_at=?`。AC2 行为由 wire 测试覆盖，但卡/记录把 `Book.restore` 作为实现点，属于“宣称的方法未接线”。 | 全仓 `restore()` 调用检索无 `Book.restore`；`restore_book_from_trash` 为单语句 SQL。 | 要么让 repository 走 domain 方法（需装载 Book），要么把卡/Handoff 的措辞改为“命令路径为单语句 SQL；domain helper 仅为语义占位”，并补一个 domain 单测（若保留）。 |
| R-008 | P3 | `src/bootstrap/core_service.py:2330-2353`；`verification/FEA-12-CORE/core-py-implementation-record.md:81-83` | 批量中只要含 retry 目标，就跳过集合级 digest 校验（`if not retry_ids:`）；混合“存活书 + pending 重试书”时集合级 digest 只做形状校验。逐书 digest 对存活书仍校验，不构成新的数据破坏，但不符合 §5.11.1a “两级校验”的字面。 | 代码阅读；记录 §2.8 自认“只校验形状”；无混合 retry 测试。 | 在 Lead/契约层面明确 retry 目标的集合级绑定规则，或补一个混合 retry 判别测试；若接受现状，在 AC5/记录中写成限定。 |
| R-009 | P3 | `src/bootstrap/core_service.py:2404-2421` | 批量 `execute_permanent_delete_db` 在写边界抛 `PermanentDeleteBlockedError` 时，返回的 `items[].error_code` 全为 `None`，没有使用 `caught.code`（单条路径正确地返回 `BOOK_BUSY`）。正常预检已覆盖，此分支只在“预检→事务之间状态变化”的竞态出现；仍是错误分类缺陷。 | 代码对比单条 `:2255-2256` 与批量 `:2404-2421`。 | 用 `caught.code` 回填对应 item（若可定位到具体书）或至少顶层 `BOOK_BUSY`；补一个在预检后、事务前把 source operation 置非终态的注入测试。 |
| R-010 | P3 | `src/infrastructure/sqlite/library.py:708,1248-1299` | `has_unsafe_source_references` 未检查“目标外 `page_bindings.previous_binding_id` 指向目标 binding”的不一致图；schema 有该自 FK。此类图会让事务 FK 失败并返回 `BOOK_DELETE_FAILED`（已回滚），而不是契约要求的 `BOOK_DELETE_CONFLICT` 预检失败。 | schema `page_bindings.previous_binding_id REFERENCES page_bindings(binding_id)`；四条 preflight checks 未覆盖该列。 | 增加第五条 preflight check（目标外 binding 的 previous 指向目标 binding → `BOOK_DELETE_CONFLICT`），并补一个直接构造该图的判别测试；或在记录中登记为“fail-closed internal”限定并说明不可由应用层产生。 |
| R-011 | P3 | `tests/core/test_core_delete_preview_commands.py:248` | PD-01 测试对 `currentRevisionId` 只断言 `in {"rr1","rr2"}`，没有固定 Lead 裁决的“首个可见 region”顺序；隐藏 region 测试只证明“隐藏不选”，不能防止“选最后一个可见 region”的回归。 | 该测试 rg1/rg2 均可见，正确值应为 rr1；实现 SQL 排序正确，但测试未钉住。 | 改为 `== "rr1"`（保留 rr2 仅作 pinned 断言），或在 golden 向量里钉住顺序。 |

## 3. AC1–AC12 判定

| AC | 判定 | 依据/说明 |
|---|---|---|
| AC1 软删 | **MET** | `tests/core/test_core_trash_commands.py::test_move_to_trash_only_flips_deleted_at` 比较除 `books` 外全表快照与 books 除 deleted_at/updated_at 外字段；受管文件哈希不变；逐项原子/重放/closed shape 有测试。`library.py:943-952` 只更新 `books` 两列。 |
| AC2 恢复 | **MET** | `test_restore_from_trash_restores_every_field` 全表快照、current/pin/进度/manual/binding 不变；逐项冲突；`restore_book_from_trash` 单语句只清 `deleted_at`。注意 R-007 的 domain helper 未接线（不影响行为）。 |
| AC3 回收站读取面 | **MET** | `test_list_recycle_bin_books_keeps_frozen_projection` 验证空数组、`page_count=None`、字段集合；`ListTrash` 形状/分页/空 bin 有测试；`handle_list_recycle_bin_books` 零改动。 |
| AC4 只读预览 | **PARTIAL（P2 R-001）** | 只读性、PD-01 字段、无路径/明文/堆栈、golden digest 均通过；但 `deletedFiles/deletedBytes` 漏计派生文件，且无测试覆盖该口径。 |
| AC5 专门确认 | **MET（附 P3 R-008）** | 单/批量缺失/格式→INVALID_REQUEST、不匹配→STALE 零副作用、集合级+逐书、重排、预览后加锁、单条拒收 book_ids、旧 Host 不传 digest fail-closed 均有测试；批量 retry 的集合级校验是限定。 |
| AC6 单事务/回滚 | **MET** | `test_delete_book_uses_explicit_begin_immediate` 记录到 `BEGIN IMMEDIATE`；`test_delete_book_transaction_rollback_on_injected_failure` 在最后 `DELETE FROM books` 前注入异常，全表快照相等、文件保留、manifest 不存在、FK check 空；清理清单在事务内写入。 |
| AC7 保护披露/边界 | **MET** | `test_a_flow_passes_while_c_flow_discloses_on_the_same_book` 覆盖锁+人工+pin+current+draft 的披露、软删通过、彻底删除成功后受保护行删除；`test_permanent_delete_blocks_nonterminal_run_while_soft_delete_passes`、busy/export 测试；删除路径无预解锁代码。 |
| AC8 共享引用/原文件 | **MET** | 共享 managed/artifact 拆分成功、共享文件保留；跨项目 provenance 置 NULL；不可拆 publication→CONFLICT 零副作用；隔离 sentinel 与静态扫描零 Windows API。 |
| AC9 C-17 子图（D1 X1） | **MET** | `test_delete_book_v7_v8_fk_probe_case_succeeds` 由失败转成功、FK check 空、plans/operations 保留；`test_delete_book_nonterminal_source_operation_busy` 零副作用；`purge_pages` 同语义新测试。变异实验去掉 X1 删除后该测试精确失败（`BOOK_DELETE_FAILED`）。 |
| AC10 统一 ProtectionPolicy | **MET** | `ProtectionPolicy.evaluate` 唯一实现，A/C 均调用；A/C 同书测试、auto cleanup 拒绝、permanent 披露不阻断、非终态 Run 阻断；cache 清理只接受 `cache/` 前缀。 |
| AC11 Host 命令桥 | **PARTIAL（P2 R-002）** | Python 侧 capability/dispatch/closed shape/typed unsupported 实测通过；.NET 侧 code/evidence 实测通过（我独立跑 6 个 sidecar 测试，证据与追踪 byte-identical）；但 AC 标记未由 Lead 合并定稿。 |
| AC12 隔离/禁令 | **MET（附 P3 R-004）** | 全部新测试用 `tmp_path` 或 workspace 临时根；运行时 sentinel 零变化；全 src 零 Windows 回收站 API；真实数据零触碰。但隔离探针的 `data_root_under_workspace_temp` 布尔恒 false 且未纳入 pass，证据需修。 |

## 4. 预期行为变更核对（不判为回归）

| 预期变更 | 核对结果 |
|---|---|
| **1. digest 必填** | 确认。`tests/core/test_core_delete_commands.py` 20→28 个测试，所有 delete 调用改为先 Preview 再回传 digest；缺 digest/格式错→INVALID_REQUEST，且不进入预检；旧 Host 路径由 B 侧旧 Core 测试验证 `INVALID_REQUEST`。不是放宽断言：原测试没有删除，旧断言被新契约替代。 |
| **2. PD-08 三类安全拆分** | 确认依据 ADJ D3。base `test_core_delete_commands.py:323`（`test_delete_book_conflict_with_shared_managed_or_cross_project`）与 `:378`（`test_delete_books_batch_allows_internal_shared_managed_but_rejects_external`）原文是“共享引用一律 CONFLICT”；当前改为共享 managed 拆分、共享 artifact 拆分、跨项目 provenance 置 NULL、不可拆 publication CONFLICT 四个测试，旧“一律冲突”语义不再保留，属预期对齐，不是放宽。 |
| **3. page purge 补 v7/v8 fixture** | 确认。`tests/storage/test_purge_integrity.py` 新增 v7/v8 fixture 行与 `test_purge_removes_v7_v8_subgraph_and_keeps_operations`；旧 purge 测试保留并通过。 |
| **4. capability 列表新增 3 名** | 确认。`tests/core/test_core_service.py` 精确列表加入 3 名；最小手搭 Core 不公告的逻辑在 `handle_ping` 条件分支；全量 pytest 通过。该测试文件不在 allowed_paths（R-003）。 |

**测试是否删/放宽**：逐项对比未发现删除测试或放宽断言；旧 shared-conflict 测试是被新语义替代，且新测试覆盖三个原场景 + 不可拆场景。新增 CORE 测试 43 条（不是 51；R-005）。

## 5. 宣称 vs 实现

- **`activeRunIds` 不含 active export**：如实登记在 implementation record §6.2 / Handoff §6.2；wire 无 export 字段，运行期 export 仍在 preflight 触发 `BOOK_BUSY`。**不是隐藏缺口**，但 UI 无法从预览看到 export 阻断项，属冻结 wire 的已知限制。
- **`deletedBytes` stat/STALE**：实现用实际文件 `stat`，缺失文件计 0；预览→确认间文件大小变化会改变 digest → STALE。记录 §6.3 如实登记。**成立**。
- **catalog preview 派生文件不计入**：记录 §6.5 如实登记，但 C-04b/PD-01 要求“managed/派生”；这是 R-001 的 P2，不是“已登记即可 MET”。
- **`PurgeTrash` 不实现**：Core handler 返回 typed `UNKNOWN_COMMAND`（validation/false），零副作用；Host 仅登记 capability/门禁；有测试。**成立**，无偷偷实现。
- **`Book.restore`**：方法存在但零调用；实际命令走 SQL。**宣称的实现点未接线**（R-007，P3）。
- **测试数字**：任务卡“本卡新增 51”与 Handoff “+51 本卡”实为 CORE 43 + DSIM 8；**宣称精度问题**（R-005）。
- **隔离探针**：`pass:true` 但 `data_root_under_workspace_temp:false` 且不参与 pass；**证据自洽性缺陷**（R-004）。

## 6. 独立复跑与验证

所有日志在 `G:\CODEX\New Manga.workspace\FEA-12\review-core\`；当前 head `388f5476e`（源码等价 85db）。

| 场景 | 命令 | 结果 | 证据 |
|---|---|---|---|
| 相关组 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q -p no:warnings -p no:cacheprovider --tb=no` | **1096 passed**，EXIT 0，80.78s | `pytest-related.log` |
| 定向 FEA-12 | 上述 5 个新增/改写测试文件 | **72 passed**，EXIT 0，6.2s | `pytest-targeted-core.log` |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings -p no:cacheprovider --tb=no` | **3144 passed / 10 skipped**，EXIT 0，248.7s | `pytest-full.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo` | **1405 passed / 0 failed / 80 skipped / 1485 total**，EXIT 0，173s；分程序集与集成日志一致 | `dotnet-full.log`；运行后 `git checkout -- verification/FEA-09` 已恢复 |
| 旧 Core sidecar | 设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR` + `NEWMANGA_EVIDENCE_DIR`，过滤 Fea12Core/Fea12NewCommands/B1/B2 | **6 passed / 0 failed / 0 skipped**，EXIT 0；生成的两份证据与追踪 sha256 **完全一致** | `dotnet-sidecar.log`；`dotnet-evidence/commands/*` |
| 旧 Host 负向 | `verification/FEA-12-PREREQ-1/tools/baseline-negative-control.ps1` 对 baseline worktree 旧 assembly | `BASELINE_NEGATIVE_CONTROL=CAPTURED`，EXIT 0；5 命令 absent/typed unknown，5 新码 unknown 且 code 保留，旧 Core 拒绝 preview/move | `oldhost-negative-control.log` |
| check | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md`；全量 check | **PASS (3 warnings)**，EXIT 0（非终态 Task、STATUS 80%、PLAN 80%） | `check-task.log`、`check-all.log`；`gates-integration.log` 记录的 4 warnings 是 85db 时 B 证据未登记，388f 已消除 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**，EXIT 0 | `verify-pins.log` |
| digest 探针 | 仓外补丁版 `core_py_inventory_digest.py` | **all_match=true**；逐书 digest/canonical 与追踪证据稳定一致 | `review-digest-golden.json` |
| 隔离探针 | 仓外补丁版 `core_py_isolation_scan.py` | `pass=true`；但 `data_root_under_workspace_temp=false`（R-004） | `review-isolation-scan.json` |
| 派生文件探针 | `derived_disclosure_probe.py` | `deletedFiles=1, deletedBytes=13`，同时派生文件 13 bytes 存在 | `derived-disclosure-probe.log` |

### 6.1 判别性变异（仓外 85db 副本，未改仓库）

| 变异 | 预期 | 实测 |
|---|---|---|
| X1：把 `execute_permanent_delete_db` 内 `self._delete_book_source_graph(book_id)` 禁用 | `test_delete_book_v7_v8_fk_probe_case_succeeds` 失败，复现 FK 回滚 | **1 failed**：`BOOK_DELETE_FAILED`，`mutation-x1.log` |
| digest：把单条 `supplied_digest != inventory_digest(inventory)` 改为 `if False` | `test_delete_book_stale_preview_after_protection_change` 失败 | **1 failed**：删除成功导致 `res["error"]` 为 None，`mutation-digest.log` |
| PD-08：把 `UPDATE artifact_revisions SET source_artifact_revision_id=NULL` 改为 `SELECT 1` | `test_delete_book_pd08_cross_project_provenance_detached` 失败 | **1 failed**：FK 失败→`BOOK_DELETE_FAILED`，`mutation-pd08.log` |

这三个变异证明对应测试确实能判别修复前后；capability gate 未做 .NET 源码变异（需要重编译），但 B 侧 sidecar 测试的“stub gate 放行→旧 Core 收到 command frame”正向对照与 probe 失败路径已独立复跑，足以证明 gate 是失败来源。

## 7. 范围 / 冻结 / 纪律核对

### 7.1 提交与 allowed_paths

| Commit | 归属 | 内容 | 范围核对 |
|---|---|---|---|
| `5fb300fd2` | CORE-A | 5 源文件 + 6 测试（3 新） | 5 源文件与 5 个测试在 allowed_paths；**`tests/core/test_core_service.py` 不在**（R-003） |
| `27dfd7514` | CORE-A | 卡/Handoff/实施记录/证据/日志/探针 | 全在 `verification/FEA-12-CORE/**`、卡、Handoff |
| `2a8c6cf83` | CORE-A | 证据表 commit pin、Handoff | 卡/Handoff，允许 |
| `85db8354f` | CORE-A | gate 日志头部/Handoff | 允许 |
| `9ebb812b0` | CORE-B | 4 个 .NET 文件 + 11 个证据 | 全在 allowed_paths（`HostCommandRegistry.cs` 未改，PREREQ-1 已注册） |
| `fc7125586` | CORE-B | B 记录/门禁 provenance | 允许 |
| 其余 range commits | DSIM-1 / Lead | `d5925957b`（DSIM 源码/测试）、`beee351bb`/`7093efaca`（DSIM 文档）、`564bc0760`/`388f5476e`（Lead STATUS/PLAN/ledger/集成证据） | 非 CORE；CORE commits 未触碰 `simulated_recycle_bin.py`/`test_recycle_gateway_sim.py` |

`git diff --name-status e47fd47e..85db8354f` 中 CORE 文件与上述一致；`src/infrastructure/filesystem/simulated_recycle_bin.py`、`tests/fea12/test_recycle_gateway_sim.py`、FEA-12-DSIM-1 文档属并行任务，不是 CORE 越界。

### 7.2 冻结与依赖

- 18 pinned 契约：`git diff --name-only e47fd47e..85db8354f -- doc/plan/FEA-C0*.md doc/plan/FEA-C1*.md doc/plan/FEA-01*.md doc/contracts/ADJ-001...` 为空；`verify_pins.ps1` 18/18。
- C-17 schema/migrator/connection：零 diff（`git diff --name-only ... -- src/infrastructure/sqlite/{schema,migrator,connection}.py` 为空）。
- 新依赖：`pyproject.toml`/requirements/csproj 零 diff。
- `verification/FEA-09/**`：range 零 diff；全量 .NET 的测试副作用已 `git checkout -- verification/FEA-09` 恢复，当前 clean。
- 真实数据/AppData/外部卷/回收站：所有新测试 `tmp_path`/workspace 临时根；删除实现模块静态扫描零 Windows 回收站 API；隔离 sentinel 零变化；真实 Windows 回收站 D 流程 **NOT_RUN**（首版 OUT）。
- push：`origin/main` 不含 reviewed head；未发现 push。
- 工作树：开始审查时 `?? verification/FEA-12-CORE/logs/gates-integration.log`（Lead 在审期间提交为 `388f5476e`）；当前 clean。

## 8. 残余风险 / limitation

1. **派生文件披露口径**（R-001）：在 Lead 裁决前，预览的 `deletedFiles/deletedBytes` 不能视为完整“将被删除文件”披露。数据安全无影响（派生可重建），但用户会低估清理范围。
2. **批量 retry 集合级 digest**（R-008）：混合 pending+live 时集合级 digest 未校验；逐书 live digest 仍校验。需要契约口径或测试。
3. **预检→事务竞态错误码**（R-009）：source operation 在两步之间变为非终态时，批量返回 item code None；单条正确。
4. **目标外 page_bindings.previous 自 FK**（R-010）：不一致图会以 `BOOK_DELETE_FAILED`（已回滚）而不是 `BOOK_DELETE_CONFLICT` 预检失败；应用层正常路径不产生。
5. **HostRuntime 接线无 Host.Tests**：B record §8.1 已登记；dispatcher 层有 Fact/侧车，HostRuntime 分支只做按命令分流，风险低但未单测。
6. **全量 .NET 的 80 skips** 含 24 个 CoreClient 侧车测试；我另跑 6 个定向 sidecar 全过，但全量门禁本身不覆盖这些环境依赖测试。
7. **`activeRunIds` 无 export 字段**：wire 冻结缺口，已登记；UI 只能通过 `BOOK_BUSY` 得知 export 阻断。
8. **真实 D 流程/真实 Windows 回收站**：NOT_RUN；本卡按范围零实现，不能声称 D 流程完成。
9. **测试数字/卡面**：R-005/R-006；不影响代码，但影响审计可追溯性。

## 9. done vs closed_with_limitations 意见

- **不建议直接 `done`**：AC11 仍未定稿（R-002），AC4 的派生文件披露与冻结 PD-01/C-04b 不一致（R-001），allowed_paths 有缺口（R-003）。
- **建议路径 A（优先）**：Lead 修 R-001（实现派生计数+测试，或作出明确的 additive 口径并改 AC4/记录）、定稿 AC11、补 allowed_paths/证据表/测试数字；代码无需重写，复审可快速 `approved`。
- **路径 B（若 Lead 接受限定）**：把“派生 preview 文件不计入 deletedFiles/Bytes”作为正式产品/契约限定，AC4 改为 `MET（限定）`，AC11 定稿 MET；此时可按 `closed_with_limitations` 收口，但必须在任务卡和 Review 中保留该限定，不能继续写“完整 PD-01 披露”。
- AC12 的证据探针布尔值（R-004）应在 closeout 前修正；它不是行为缺陷，但会让 meta AC 证据自相矛盾。

## 10. 自审声明

- 我未参与 FEA-12-CORE 的实现、返修、分片设计或任务卡编写；本会话为新启动的独立上下文。
- 只读仓库：未修改、未 commit、未 push、未 stash/reset；仓外仅写日志/报告/探针脚本/临时 85db 副本，临时副本与 tar 已删除。
- 未触碰真实用户数据、AppData、外部卷、真实回收站；测试全部使用 `tmp_path`/workspace 临时根；旧 Host 负向脚本只读 baseline worktree，临时数据在 workspace temp。
- 全量 .NET 运行造成 `verification/FEA-09/logs/wire-redacted.ndjson` 的既有测试副作用，已按任务指令 `git checkout -- verification/FEA-09` 恢复，当前 `git status` clean。
- 以上结论基于 Git 对象、文件原文、实际测试/探针/变异输出，不基于聊天记录。

## 最终决定

**decision: changes_requested（P0=0，P1=0，P2=3，P3=8）。**

代码主体与 AC1–AC3、AC5–AC10、AC12 的行为实现通过独立复跑与三个判别性变异；AC11 的 .NET 侧也通过独立 sidecar 复跑（6/6，证据 byte-identical）。阻断点是：AC4 的派生文件披露与冻结 PD-01/C-04b 不一致（P2）、AC11 未由 Lead 合并定稿（P2）、分片 A 的 `tests/core/test_core_service.py` 超出 allowed_paths（P2）；另有 8 个不阻断的 P3。若 Lead 选择将派生文件排除作为正式 additive 限定并完成 AC11/范围文档定稿，可转为 approved/closed_with_limitations；否则应先修 R-001 的最小披露口径与判别测试。
