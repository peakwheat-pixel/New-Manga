---
id: FEA-12-CORE
title: FEA-12 删除线首版实现（A 软删/恢复 + C 彻底删除 + 统一 ProtectionPolicy + Host 命令桥）
kind: implementation
governance_version: 3
status: in_review
approval: 用户 2026-11-05 指令（FEA-12 scope review → 冻结 → 实施 → 独立 Review）；范围冻结 ADJ-2026-11-05-FEA-12-SCOPE（D1–D8）；G-DELETE-IMPL 首版释放（隔离 fixture + 模拟回收站路径）；FEA-12-PREREQ-1 done（wire 冻结，`3e37c595b`）、FEA-11-LINEAGE-1 done（`90a8c8218`）；分片 A/B 已交付；CORE r1 Review changes_requested（P0/P1=0，P2=3，P3=8）→ Lead 处置 + **r2 最小返修交付 in_review（R-001 + R-004/005/007/008/009/010/011/012 处置；AC4 PARTIAL 待 Lead 复审定稿；AC11 由 Lead 定稿 MET）**
suggested_owner: dsh（dsh-agent-team teammates 分片，Lead 集成）
owner: fea12-core-py（分片 A）+ fea12-core-host（分片 B），Lead 集成
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-12-CORE-r1.md` session `b2e5e275-122b-44d4-98bc-c86fec7bfbc1`；未参与实现）
depends_on:
  - FEA-12-PREREQ-1
  - FEA-11-LINEAGE-1
base_commit: e47fd47e41add3edeb7f67e578eefeb48eddce50   # 2026-11-05 释放点 main head
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-CORE
allowed_paths:
  - doc/tasks/FEA-12-CORE.md
  - doc/reviews/FEA-12-CORE-*.md
  - doc/handoffs/FEA-12-CORE-*.md
  - src/application/library/service.py
  - src/application/library/ports.py
  - src/application/maintenance/trash.py
  - src/application/maintenance/cleanup.py
  - src/application/maintenance/ports.py
  - src/domain/books/entities.py
  - src/infrastructure/sqlite/library.py
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py（DSH 窄批：仅删除/保护服务注入）
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs（capability probe：core.ping 缺失→CORE_CAPABILITY_MISSING）
  - apps/desktop-avalonia/src/NewManga.Host/Sources/HostErrorCodes.cs（新错误码投影/白名单，若需要）
  - tests/core/test_core_delete_commands.py
  - tests/core/test_core_service.py（DSH 窄批：capability 列表断言随 §5.13/§5.14 新增 3 名同步；r1 Review R-003 补登）
  - tests/core/test_core_delete_preview_commands.py（新增）
  - tests/core/test_core_trash_commands.py（新增）
  - tests/core/test_p09_ac1_recycle_bin_route.py
  - tests/maintenance/test_cleanup.py
  - tests/storage/test_trash.py
  - tests/storage/test_purge_integrity.py（补 v7/v8 fixture）
  - tests/fea12/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs
  - verification/FEA-12-CORE/**
out_of_scope:
  - FEA-12-PREREQ-1 的 M2-C1/投影内容（已由前置卡完成）
  - B 流程到期/保留期调度；D 流程真实实现（归 FEA-12-DSIM-1 / 后续）
  - FEA-12-UI（IHostController/C-07 冻结面、回收站视图）
  - 新 schema/migration/依赖；18 pinned 冻结契约字节；C-04b/C-09/C-13/C-14/C-17/ADJ-001 正文
  - 真实用户数据/AppData/外部卷/回收站；push
---

# FEA-12-CORE：删除线首版实现

## 来源与目标

- 来源：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`（D1–D8）；`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md` PD-01…PD-10；`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`；`doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md` SC-B04/SC-B04a/SC-B06；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md:147`；`doc/plan/FEA-C13_*`；`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §2/§7.1；`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.11/§5.12（rev 2.13 by PREREQ-1）。
- 目标：让用户**在应用内**可安全软删/恢复/查看回收站，并可对目标书执行"只读预览 → 保护披露 → inventory_digest 专门确认 → 同一事务彻底删除 → 失败整体回滚 → cleanup_pending 显式重试"的完整 C 流程；**永不触碰用户原文件**；引用源书籍（v7/v8 行）可删除（按 D1 X1）；共享引用按 PD-08 可安全拆分不阻断。
- 关键实测事实：当前 C 流程对含 `page_bindings`/C-17 lineage 的书 FK 失败（`workspace\FEA-12\evidence\probe_delete_fk_interaction.json`）；本卡必须修复并有回归。
- **前置事实（FEA-12-PREREQ-1 已 done，delivery/integration `3e37c595b`）**：M2-C1 rev 2.13 已登记 preview/trash wire（目标 minor 11/13；既有 delete minor 10 不变）、2 删除新码 + 3 `TRASH_*` 码、capability 名 `library.delete.preview/1`/`library.trash.read/1`/`library.trash.write/1`；`PurgeTrash` 首版**不实现**（只登记命令面，digest 绑定待后续 additive 裁决）。**R-002 二选一（本卡必须处置）**：`CORE_CAPABILITY_MISSING` 不在 delete/trash 白名单——(a) 把它 additive 加入 `AllowedDeleteTrashErrorCodes` + .NET 投影判别测试，或 (b) 让 probe 错误在 `HostRuntime` 层抛出、绕开 `ProjectDeleteTrashError` + 判别测试；任选其一并在 AC11 证据中说明。

## Acceptance Criteria（release 时按 PREREQ-1 冻结 wire 最终确认；下列为冻结候选）

- [x] **AC1 软删（MoveToTrash）**：逐项 `moved/skipped`；书架不再含、回收站含；DB 除 `books.deleted_at` 外内容行/保护行/current/pin/进度/binding 全不变；受管文件字节哈希前后一致。 <<MET>>
- [x] **AC2 恢复（RestoreFromTrash）**：恢复后书架可见；current/pin/进度/人工数据/binding 与删除前逐字段相等；不存在静默解锁/改 current；不存在条目 → 逐项冲突不整批失败。 <<MET>>
- [x] **AC3 回收站读取面不回归**：`ListRecycleBinBooks` 保持冻结投影（`page_count` `None` 通道、空数组≠失败）；`ListTrash` 映射按 PREREQ-1 冻结形状。 <<MET>>
- [ ] **AC4 只读预览（PD-01/PD-03）**：预览前后 DB 逐表快照相等、文件 mtime/hash 不变；逐项返回 manualRegionCount/lockCount（三锁 ∪ text_json.translation_locked 并集）/currentRevisionId/pinnedRevisionIds/activeRunIds/draftPageCount/deletedFiles/deletedBytes/sharedFileRefs；无路径/明文/堆栈；digest golden 向量可复算。 <<PARTIAL: r2 已修复 r1 R-001——deletedFiles/deletedBytes 现计入 catalog preview/page-original 派生文件（与 managed 去重）并有判别测试+golden 向量；证据齐备，待 Lead 复审定稿恢复 MET>>
- [x] **AC5 专门确认绑定（PD-02/PD-04）**：单/批量 `inventory_digest` 缺失/格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW`；集合级与逐书两级校验；单条拒收 `book_ids`；预览→确认间任何保护变化 → 拒绝并重预览；旧 Host 不传 digest fail-closed 不降级软删。 <<MET>>
- [x] **AC6 单事务与失败回滚（PD-05/PD-06）**：显式 `BEGIN IMMEDIATE`；成功路径内容行按白名单消失、Pipeline 历史脱离保留、清理清单同事务持久化；事务最后一条 DELETE 前注入异常 → 内容行/保护行/v7-v8 行/文件集合与事务前逐项相等、`foreign_key_check` 空、不开始文件清理。 <<MET>>
- [x] **AC7 保护披露与删除边界**：含锁/人工/pin/current/draft 的书预览披露计数准确；删除成功后受保护行确实删除（披露≠阻断）；事务前无顺手解锁/取消 pin/改 current；非终态 Run/Task/Export → `BOOK_BUSY` 零副作用。 <<MET>>
- [x] **AC8 共享引用与原文件边界（PD-08）**：可安全拆分共享引用 → 删除成功、原文件字节与其他项目绑定不变；不可拆分/关系图不一致/未列明目标外引用 → `BOOK_DELETE_CONFLICT` 零副作用；用户源文件/源目录逐文件哈希与集合前后不变；零 Windows 回收站 API（静态 grep + 运行时哨兵）。 <<MET>>
- [x] **AC9 C-17 子图（D1 X1）**：含 `page_bindings` + `source_binding_publications` + `source_revision_lineage` 的书按 X1 同事务删除成功、`foreign_key_check` 空；非终态 source operation → `BOOK_BUSY` 零副作用；`source_sync_plans`/`source_operations` 保留可查询；probe FK 案例变为成功并被测试覆盖。 <<MET>>
- [x] **AC10 统一 ProtectionPolicy**：A/C 共用同一判定函数（同名 scope 判定一致）；有锁+有草稿：软删通过、彻底删除先披露后可执行；非终态 Run 彻底删除 `BOOK_BUSY`；cache 清理不命中受保护对象（回归）。 <<MET>>
- [x] **AC11 Host 命令桥（按 PREREQ-1 wire；Lead 最终定稿）**：新命令在 registry/dispatcher/client 注册且与 Core shape 一致；capability 缺失 → `CORE_CAPABILITY_MISSING`（R-002(b)：probe 在 projection try 之前 gate，typed 不落入 unknown）；旧 Core/旧 Host fail-closed；负向对照按 PREREQ-1 结果；`PurgeTrash` 不实现（只按冻结 wire 登记，禁止偷偷实现）。 <<MET>>
- [x] **AC12 隔离与禁令（元 AC）**：全部删除/回收站测试使用隔离 DataRoot（`tmp_path`/workspace 临时根）；代码/脚本 0 处真实 `%APPDATA%`/真实盘符/真实回收站路径；运行时哨兵证明隔离根外零变化；真实 Windows API 0 调用；真实用户数据零触碰。 <<MET>>

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）。共享组合根 `core_assembly.py` 仅 DSH 窄批；`core_service.py` 与 LINEAGE-1 写域串行（LINEAGE-1 closeout 后才释放本卡）。

## 禁止范围

见 `out_of_scope`。另：不得改 18 pinned 冻结契约字节；不得删测试/放宽断言制造通过；不得把 `skipped` 计入 passed；不得后台自动重试/把清理藏进启动/退出/导入/GC/软删（PD-07）；不得 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC12 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q`（逐 AC 断言） | 隔离 fixture；真实 v1…v8 迁移 | NOT_RUN | verification/FEA-12-CORE/logs/ |
| 全量回归 | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | 仓库根；基线由本卡首日实测记录 | NOT_RUN | logs/gates.log |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`（18/18） | 仓库根 | NOT_RUN | logs/gates.log |
| FK/回滚 | 故障注入：事务最后 DELETE 前抛错；probe 案例复跑（binding/lineage/publication） | 隔离 v8 fixture | NOT_RUN | logs/ac6-*, logs/ac9-* |

## 依赖、风险与阻塞

- 硬依赖：`FEA-12-PREREQ-1`（wire 冻结）；`FEA-11-LINEAGE-1`（`core_service.py`/`core_assembly.py`/sqlite 写域串行）。
- 风险：①PD-08 修正会改变既有测试期望（`test_core_delete_commands.py:323,378`）→ 登记"预期行为变更"，Review 不判回归；②X1 删除 lineage 的审计含义（ADJ §5.1）；③显式 `BEGIN IMMEDIATE` 与现有 `with self._conn:` 差异；④批量 pending 重试语义（PD-07/09）；⑤`.NET` 首跑 flaky（FEA-11 L-11）→ 复跑并记录。
- 阻塞解除标准：PREREQ-1 集成 + LINEAGE-1 closeout + 本卡 AC 证据齐备 + 独立 Review approved。

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-12-CORE-core-py.md`（分片 A：Python Core；commit 列表见 Handoff 与 `verification/FEA-12-CORE/logs/gates-core-py.log`）。
- Review：尚无（Lead 指派上下文独立 Reviewer；实现者交付后不参与 Review）。
- 实际测试（分片 A **r2** 实跑，命令/EXIT/head 见 `verification/FEA-12-CORE/logs/gates-core-py.log`）：
  - `pytest tests/core tests/storage tests/maintenance tests/fea12 -q`：**1104 passed**（相关组；r1 1096 + r2 新增 8）。
  - `pytest tests -q -p no:warnings --tb=no`：**3152 passed / 10 skipped**（基线 3093/10；测试增量口径 **CORE +51 / DSIM-1 +8**，其中 r2 新增 8 条 CORE 测试，无失败）。
  - `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md`：PASS（4 warnings，均既有/分片 B 证据待 Lead 合并登记）。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1`：18/18 PASS。
  - 证据探针（r2 重新生成）：`scripts/core_py_inventory_digest.py`（含 R-001 derived 向量）与 `scripts/core_py_isolation_scan.py`（R-004 修复后）均 EXIT=0。
  - 全量 .NET：属分片 B/Lead 集成门禁；分片 A 零 .NET 改动（集成记录 1405/0/80）。
- 提交（r2）：仅本卡 allowed_paths 文件；commit 列表见 Handoff §1（r1 `5fb300fd2`/`27dfd7514`/`2a8c6cf83`/`85db8354f` + r2 源码/测试/证据 commit + card/Handoff commit）。

## DSH 裁决/实现语义（分片 A 固化，2026-11-05）

Lead 已裁决以下 8 点；完整依据、canonical 形式与证据见 `verification/FEA-12-CORE/core-py-implementation-record.md` §2：

1. 分片 A = Python Core；.NET Host 桥/R-002 归 task-7；AC11 在分片 A 标 PARTIAL（Python 侧 MET）。
2. **`currentRevisionId`**：book 无单一 current 列 → 取该书**首个 lineage-visible region** 的 `current_revision_id`（chapter sort/import/id → page sort/id → region reading_order/id；可见性过 `LineageIsolationGuard.is_region_readable`，与 FEA-11-LINEAGE-1 已释放读口径一致）；无 region 取首个 artifact current；均无 → `null`。golden 向量已固化。
3. **`pinnedRevisionIds`** = `region_revisions.is_pinned=1 ∪ artifact_revisions.is_pinned=1`（去重排序；覆盖 PD-01"受保护 artifact"披露）。
4. **`sharedFileRefs.fileId`**：managed 共享文件 = `"managed:" + sha256(managed 相对路径) 前 16 hex`（不泄路径）；引用源共享 = `source_entries.entry_id`；`otherProjectCount` = 目标集外其他 book 引用数；该结构进入 digest 输入且稳定可复算。
5. **`PurgeTrash` 首版不实现**：typed `UNKNOWN_COMMAND`（validation/false）fail-closed、零副作用、不追加 digest 字段。capability `library.trash.write/1` 公告仅代表 `MoveToTrash`/`RestoreFromTrash` 可用；UI 不得调用 `PurgeTrash`，Host 不得以 `UNKNOWN_COMMAND` 探测能力。
6. **digest 必填**（M2-C1 rev 2.13 §5.11.1a）：旧 Host 不传 → `INVALID_REQUEST` fail-closed，不得忽略 digest 或降级软删；既有 delete 测试按"先 Preview 再回传 digest"更新（预期行为变更，非放宽断言）。
7. **PD-08 跨项目 revision 引用**：可安全拆分不阻断——事务内把目标集外行 `source_artifact_revision_id` 置 NULL（保留存活行与文件），目标行删除；仅真正不可拆/关系图不一致/未列明目标外引用才 `BOOK_DELETE_CONFLICT`（依据 ADJ D3 + page 级 purge 先例，见 `tests/storage/test_purge_integrity.py::test_purge_clears_cross_page_provenance_instead_of_failing`）。
8. **文件放置**：`ProtectionPolicy`/`ProtectionFacts`/`ProtectionVerdict` 在 `src/application/maintenance/ports.py` 且不 import infrastructure；`Book.restore` 在 domain；digest/cursor 纯函数在 `src/application/library/service.py`；DB 在 `src/infrastructure/sqlite/library.py`；**不改 `core_assembly.py`**。

## 预期行为变更（Review 不判回归）

1. **digest 必填**：既有 delete 测试全部改为先 Preview 再回传 digest（§5.11.1a 冻结）；旧 Host 不传 digest 必须 fail-closed。
2. **PD-08 共享引用**：原"存在共享 managed/artifact/跨项目 revision 引用 → 一律 `BOOK_DELETE_CONFLICT`"按 ADJ D3 修正：可安全拆分不阻断（原 `test_core_delete_commands.py:323,378` 期望随之更新）；共享物理文件与其他项目 binding 保留、跨项目 provenance 置 NULL；仅不可拆分才 CONFLICT。
3. **page 级 purge 补 C-17 子图**（`purge_pages`）：`tests/storage/test_purge_integrity.py` fixture 补 v7/v8 行后仍全绿（D1 X1 同语义，child-first）。
4. **capability 列表新增 3 名**：生产装配的 `tests/core/test_core_service.py` 断言随之更新；无 library repository 的最小手搭 Core 不公告（`tests/fea09` 既有断言不变）。

## r1 Review 处置计划（DSH，2026-11-05；Review = changes_requested）

> 依据：`doc/reviews/FEA-12-CORE-r1.md`（fresh subagent session `b2e5e275-122b-44d4-98bc-c86fec7bfbc1`；reviewed_head `85db8354f`，observed `388f5476e`；P0/P1=0，P2=3，P3=8）。代码主体质量获认可（独立复跑 pytest 3144/10、.NET 1405/0/80、pins 18/18、3 个变异实验判别成立）。

- **R-001（P2，必须修）**：AC4 `deletedFiles/deletedBytes` 漏计 catalog preview/page-original 派生文件（`cleanup_book_files` 会删除但不披露）。**DSH 裁决：按冻结语义修复**——预览 inventory 必须计入实际会被清理的派生文件与字节（与 managed 内容文件去重），并补判别测试 + golden 更新；不接受"实现登记为排除"但 AC 仍 MET。修复后 AC4 恢复 MET。
- **R-002（P2，Lead 已处置）**：AC11 已由 Lead 定稿为 `<<MET>>`（分片 B 的 capability gate/R-002(b)/旧 Core/旧 Host 负向证据已并入本卡 Evidence）；`integration_commit`/`delivery_head` 在 closeout 填写。
- **R-003（P2，Lead 已处置）**：`tests/core/test_core_service.py` 已按 DSH 窄批补入 allowed_paths（capability 断言同步，预期行为变更 #4）；实现者应更正 Handoff `:120` 的"已入 allowed_paths"表述为"Lead 于 r1 处置时补登"。
- **P3 处置（随 r2 同批）**：
  - R-004（P3，实现者修）：`core_py_isolation_scan.py` 的 `data_root_under_workspace_temp` 用 `str(parents)` 恒 false 且未纳入 pass；改 `Path.is_relative_to` 并纳入 `runtime["pass"]`；`DRIVE_PATH` 未使用则实际使用或删除；重生成 evidence。
  - R-005（P3，实现者修 + Lead 记录）：测试条数口径拆分为"CORE +43 / DSIM-1 +8"（不把 51 全归本卡）；gates-core-py.log 的 protection 计数改 11（或注明"policy 子集 8"）。
  - R-006（P3，Lead closeout 修）：更新"测试要求"表为实跑结果/证据路径；填 integration/delivery 指针。
  - R-007（P3，实现者修）：`Book.restore` 未接线——**二选一**：让 `restore_book_from_trash` 走 domain 方法（如可行），或把卡/Handoff 措辞改为"命令路径为单语句 SQL；domain helper 为语义占位"并补 domain 单测；不得把未接线方法写成实现点。
  - R-008（P3，DSH 裁决 + 实现者补测）：PD-07 retry 请求的**集合级 digest 只做形状校验**（混合存活+retry 时），逐书 digest 对非 retry 目标仍强校验；本裁决定为 PD-07 限定语义（M2-C1 未定义 retry 集合绑定），实现者补一个"混合 retry"判别测试并在记录/AC5 写明限定。
  - R-009（P3，实现者修）：批量 `execute_permanent_delete_db` 写边界抛 `PermanentDeleteBlockedError` 时 `items[].error_code` 应为 `caught.code`（至少顶层 BOOK_BUSY），补预检→事务间竞态注入测试。
  - R-010（P3，实现者修）：`has_unsafe_source_references` 增加第五条 preflight：目标外 `page_bindings.previous_binding_id` 指向目标 binding → `BOOK_DELETE_CONFLICT`（+判别测试）；若认为应用层不可产生，须在记录中明确"fail-closed internal"限定并给出不可产生论证。
  - R-011（P3，实现者修）：`test_core_delete_preview_commands.py:248` 的 `currentRevisionId` 断言改 `== "rr1"`（钉住 Lead 裁决的"首个可见 region"顺序），并同步 golden。
  - R-012（P3，实现者修，Lead 补充）：批量 cleanup_pending/retry 路径缺直接判别测试——补批量 partial cleanup → `BOOK_DELETE_BATCH_CLEANUP_PENDING` 逐项状态 → 显式重试（只重试 pending、不重跑预览、幂等）、混合 live+retry 的 items/digest 口径断言。
- **r2 处置结果（2026-11-05，实现者 `fea12-core-py`）**：
  - R-001 **已修**：`_derived_cleanup_entries` 按与 cleanup 相同的 catalog 查询把 preview/page-original 派生文件计入 `deletedFiles/deletedBytes`（绝对路径去重），catalog 读失败 → `BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`；判别测试 2 条 + golden 向量 derived 记录。
  - R-004 **已修**：`is_relative_to` 真包含检查并纳入 `runtime["pass"]`；DRIVE_PATH 实际扫描删除模块+证据脚本并纳入 static pass；evidence JSON 重生成（`drive_path_hits=[]`、`data_root_under_workspace_temp=true`）。
  - R-005 **已修**：卡/记录/Handoff 计数改「CORE +51 / DSIM-1 +8」；gates log protection 计数改 11。
  - R-007 **已修（接线）**：`restore_book_from_trash` 经 domain `Book.restore()` 产生值 + `deleted_at IS NOT NULL` guarded UPDATE；补 domain 单测。
  - R-008 **已裁定并补测/限定**：混合 live+retry 批次集合级 digest 仅形状校验；逐书对存活目标强校验；记录 §2.8 与 AC5 写明限定。
  - R-009 **已修**：`PermanentDeleteBlockedError` 携带 `book_id`；批量顶层 `BOOK_BUSY`、items 归因；预检→事务竞态注入测试。
  - R-010 **已修**：第 5 条预检（目标外 binding previous→目标 binding → `BOOK_DELETE_CONFLICT`）+ 判别测试。
  - R-011 **已修**：`currentRevisionId == "rr1"` 钉住顺序。
  - R-012 **已补测**：批量 cleanup-pending → 显式 retry → 幂等重放；混合 live+retry 逐项状态（deleted/cleanup_pending/not_started）。
  - R-002/R-003/R-006：Lead 处置（AC11 MET/allowed_paths 窄批/测试表与指针 closeout）；分片 A 仅更正 Handoff 表述。
  - **r2 门禁**：相关组 1104 passed；全量 pytest 3152 passed/10 skipped；check PASS（4 warnings）；pins 18/18；probes EXIT=0（见 gates log）。
- **复审**：r2 交付后另派 fresh subagent 复审（reviewed_head = r2 交付 head；只审新 head；R-001 修复 + R-004/R-005/R-007/R-008/R-009/R-010/R-011 处置）。
- **closeout 前置**：AC4 恢复 MET、AC11 已 MET、测试表/指针/证据表定稿、`check.ps1 -TaskPath` PASS。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA12CORE-A-RECORD | AC1–AC12 实施记录/证据索引 | verification/FEA-12-CORE/core-py-implementation-record.md | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-DIGEST | AC4/AC5 golden 向量 | verification/FEA-12-CORE/evidence/core-py-inventory-digest-golden.json | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-ISOLATION | AC8/AC12 静态+运行时哨兵 | verification/FEA-12-CORE/evidence/core-py-isolation-scan.json | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC1 | AC1 软删 | verification/FEA-12-CORE/logs/core-py-ac1-move-to-trash.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC2 | AC2 恢复 | verification/FEA-12-CORE/logs/core-py-ac2-restore.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC3 | AC3 读取面 | verification/FEA-12-CORE/logs/core-py-ac3-recycle-read.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC4 | AC4 只读预览 | verification/FEA-12-CORE/logs/core-py-ac4-preview.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC5 | AC5 专门确认 | verification/FEA-12-CORE/logs/core-py-ac5-digest-binding.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC6 | AC6 单事务/回滚 | verification/FEA-12-CORE/logs/core-py-ac6-transaction-rollback.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC7 | AC7 保护披露/边界 | verification/FEA-12-CORE/logs/core-py-ac7-protection-boundary.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC8 | AC8 PD-08/原文件边界 | verification/FEA-12-CORE/logs/core-py-ac8-pd08-shared.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC9 | AC9 C-17 X1 子图 | verification/FEA-12-CORE/logs/core-py-ac9-c17-x1.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC10 | AC10 统一 ProtectionPolicy | verification/FEA-12-CORE/logs/core-py-ac10-protection-policy.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC11 | AC11 Python 侧（PARTIAL） | verification/FEA-12-CORE/logs/core-py-ac11-python-wire.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-AC12 | AC12 隔离与禁令 | verification/FEA-12-CORE/logs/core-py-ac12-isolation.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-GATES | Gate G1–G9 门禁汇总 | verification/FEA-12-CORE/logs/gates-core-py.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-PYTEST-REL | Gate G3 相关组 | verification/FEA-12-CORE/logs/core-py-pytest-related.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-PYTEST-FULL | Gate G4 全量 pytest | verification/FEA-12-CORE/logs/core-py-pytest-full.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-PINS | Gate G1 pins 18/18 | verification/FEA-12-CORE/logs/core-py-pins.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-CHECK | Gate G2 治理 check | verification/FEA-12-CORE/logs/core-py-check.log | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-A-PROBE-DIGEST | AC4/AC5 可复跑探针 | verification/FEA-12-CORE/scripts/core_py_inventory_digest.py | 60dd4d563 | null | SOURCE_PIN |
| EV-FEA12CORE-A-PROBE-ISO | AC12 可复跑探针 | verification/FEA-12-CORE/scripts/core_py_isolation_scan.py | 60dd4d563 | null | SOURCE_PIN |
| EV-FEA12CORE-A-HANDOFF | 分片 A 交付/Review 就绪 | doc/handoffs/FEA-12-CORE-core-py.md | 60dd4d563 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_CAPABILITY_PRO | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/core-host-capability-probe.json | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_IMPLEMENTATION | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/core-host-implementation-record.md | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_OLD_CORE_NEGAT | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/core-host-old-core-negative-control.json | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_BASELINE_NEGAT | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-baseline-negative-control-oldhost.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_CHECK | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-check.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_DOTNET_COMMAND | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-dotnet-command-filter.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_DOTNET_FULL_1 | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-dotnet-full-1.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_DOTNET_FULL_2 | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-dotnet-full-2.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_DOTNET_SIDECAR | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-dotnet-sidecar-negative.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-CORE_HOST_PINS | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/core-host-pins.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-B-GATES_CORE_HOST | 分片 B（Host 桥/R-002/capability gate）证据 | verification/FEA-12-CORE/logs/gates-core-host.log | fc7125586 | null | CANONICAL |
| EV-FEA12CORE-INTEGRATION | Gate 集成门禁（Lead 实跑：pytest 3144/10、.NET 1405/0/80、check、pins） | verification/FEA-12-CORE/logs/gates-integration.log | - | 302e18a06207e54307e4b0b4d54fd3cf836c449ae51fbe75709014148c06d7d7 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\*\FEA-12-CORE\` | PRESERVE_REFERENCED | 同上 | 待交付时填写 | 重复执行日志；判别力证据入 verification |
| worktree | NOT_APPLICABLE（main 工作树，DSH 集成） | NOT_APPLICABLE | — | — | — |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-12-CORE\` | DELETE_SAFE（交付后） | — | 待交付时填写 | 仅隔离 fixture 临时根 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：待关闭时填写。
