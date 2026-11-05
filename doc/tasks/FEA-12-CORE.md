---
id: FEA-12-CORE
title: FEA-12 删除线首版实现（A 软删/恢复 + C 彻底删除 + 统一 ProtectionPolicy + Host 命令桥）
kind: implementation
governance_version: 3
status: in_review
approval: 用户 2026-11-05 指令（FEA-12 scope review → 冻结 → 实施 → 独立 Review）；范围冻结 ADJ-2026-11-05-FEA-12-SCOPE（D1–D8）；G-DELETE-IMPL 首版释放（隔离 fixture + 模拟回收站路径）；**依赖已满足**：FEA-12-PREREQ-1 done（wire 冻结，`3e37c595b`）、FEA-11-LINEAGE-1 done（写域空出，`90a8c8218`）；DSH 2026-11-05 释放；**分片 A（Python Core）2026-11-05 交付 in_review**：`fea12-core-py`；分片 B（.NET Host 桥/R-002）由 `fea12-core-host` 并行交付，Lead 集成
suggested_owner: dsh（dsh-agent-team teammates 分片，Lead 集成）
owner: fea12-core-py（分片 A：Python Core）
reviewer: 独立上下文 fresh subagent（未参与实现；会话 id 记录在 Review 报告）
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
- [x] **AC4 只读预览（PD-01/PD-03）**：预览前后 DB 逐表快照相等、文件 mtime/hash 不变；逐项返回 manualRegionCount/lockCount（三锁 ∪ text_json.translation_locked 并集）/currentRevisionId/pinnedRevisionIds/activeRunIds/draftPageCount/deletedFiles/deletedBytes/sharedFileRefs；无路径/明文/堆栈；digest golden 向量可复算。 <<MET>>
- [x] **AC5 专门确认绑定（PD-02/PD-04）**：单/批量 `inventory_digest` 缺失/格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW`；集合级与逐书两级校验；单条拒收 `book_ids`；预览→确认间任何保护变化 → 拒绝并重预览；旧 Host 不传 digest fail-closed 不降级软删。 <<MET>>
- [x] **AC6 单事务与失败回滚（PD-05/PD-06）**：显式 `BEGIN IMMEDIATE`；成功路径内容行按白名单消失、Pipeline 历史脱离保留、清理清单同事务持久化；事务最后一条 DELETE 前注入异常 → 内容行/保护行/v7-v8 行/文件集合与事务前逐项相等、`foreign_key_check` 空、不开始文件清理。 <<MET>>
- [x] **AC7 保护披露与删除边界**：含锁/人工/pin/current/draft 的书预览披露计数准确；删除成功后受保护行确实删除（披露≠阻断）；事务前无顺手解锁/取消 pin/改 current；非终态 Run/Task/Export → `BOOK_BUSY` 零副作用。 <<MET>>
- [x] **AC8 共享引用与原文件边界（PD-08）**：可安全拆分共享引用 → 删除成功、原文件字节与其他项目绑定不变；不可拆分/关系图不一致/未列明目标外引用 → `BOOK_DELETE_CONFLICT` 零副作用；用户源文件/源目录逐文件哈希与集合前后不变；零 Windows 回收站 API（静态 grep + 运行时哨兵）。 <<MET>>
- [x] **AC9 C-17 子图（D1 X1）**：含 `page_bindings` + `source_binding_publications` + `source_revision_lineage` 的书按 X1 同事务删除成功、`foreign_key_check` 空；非终态 source operation → `BOOK_BUSY` 零副作用；`source_sync_plans`/`source_operations` 保留可查询；probe FK 案例变为成功并被测试覆盖。 <<MET>>
- [x] **AC10 统一 ProtectionPolicy**：A/C 共用同一判定函数（同名 scope 判定一致）；有锁+有草稿：软删通过、彻底删除先披露后可执行；非终态 Run 彻底删除 `BOOK_BUSY`；cache 清理不命中受保护对象（回归）。 <<MET>>
- [ ] **AC11 Host 命令桥（按 PREREQ-1 wire）**：新命令在 registry/dispatcher/client 注册且与 Core shape 一致；capability 缺失 → `CORE_CAPABILITY_MISSING`（并按「前置事实」R-002 二选一处置其投影，附判别测试）；旧 Core/旧 Host fail-closed；负向对照按 PREREQ-1 结果；`PurgeTrash` 不实现（只按冻结 wire 登记，禁止偷偷实现）。 <<PARTIAL: Python Core 侧 MET（capability 公告+dispatch+closed shape+typed unsupported 均按冻结 wire）；.NET Host 桥注册/capability probe/R-002 归 task-7（fea12-core-host），由 Lead 集成时合并定稿>>
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
- 实际测试（分片 A 2026-11-05 实跑，命令/EXIT/head 见 `verification/FEA-12-CORE/logs/gates-core-py.log`）：
  - `pytest tests/core tests/storage tests/maintenance tests/fea12 -q`：**1096 passed**（相关组，含新增/改写测试）。
  - `pytest tests -q -p no:warnings --tb=no`：**3144 passed / 10 skipped**（基线 3093/10；本卡新增测试 51 条，无失败）。
  - `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md`：PASS。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1`：18/18。
  - 证据探针：`scripts/core_py_inventory_digest.py`（golden 向量）与 `scripts/core_py_isolation_scan.py`（AC12 静态+运行时哨兵）均 EXIT=0。
  - 全量 .NET：属分片 B/Lead 集成门禁；分片 A 零 .NET 改动。
- 提交：仅本卡 allowed_paths 文件（`src/application/library/service.py`、`src/application/maintenance/ports.py`、`src/domain/books/entities.py`、`src/infrastructure/sqlite/library.py`、`src/bootstrap/core_service.py`、`tests/core/*`（3 个）、`tests/storage/test_purge_integrity.py`、`tests/fea12/test_core_delete_protection.py`、`verification/FEA-12-CORE/**`、本卡、Handoff）。

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

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA12CORE-A-RECORD | AC1–AC12 实施记录/证据索引 | verification/FEA-12-CORE/core-py-implementation-record.md | null | 1aa0777eabfc7623572fb997e02e8cfb40dc6655d0ae85a42f70d69885704098 | CANONICAL |
| EV-FEA12CORE-A-DIGEST | AC4/AC5 golden 向量 | verification/FEA-12-CORE/evidence/core-py-inventory-digest-golden.json | null | 1bd4dc26fb814814270d0980e8bdcdbf1b0eff088805aad0ca06f6fdb312b690 | CANONICAL |
| EV-FEA12CORE-A-ISOLATION | AC8/AC12 静态+运行时哨兵 | verification/FEA-12-CORE/evidence/core-py-isolation-scan.json | null | 01f9e6e6eef3f2b39f8d72f911cbcc958a165044b6eb12f1cedeeecda24a7cd9 | CANONICAL |
| EV-FEA12CORE-A-AC1 | AC1 软删 | verification/FEA-12-CORE/logs/core-py-ac1-move-to-trash.log | null | 483d04036a3d79bda9e71a21a663343a43e68a4f62ab9e7b8126677ca7d63416 | CANONICAL |
| EV-FEA12CORE-A-AC2 | AC2 恢复 | verification/FEA-12-CORE/logs/core-py-ac2-restore.log | null | 58fd30b4da53a41ffabecd4a9973e1759e92b945548555e151b3c7a6696cfa0a | CANONICAL |
| EV-FEA12CORE-A-AC3 | AC3 读取面 | verification/FEA-12-CORE/logs/core-py-ac3-recycle-read.log | null | 90d55d903e5dbe7874dce56bebcf952d367668c173a7e5f9fc2cc56719647f7f | CANONICAL |
| EV-FEA12CORE-A-AC4 | AC4 只读预览 | verification/FEA-12-CORE/logs/core-py-ac4-preview.log | null | 8ba3328ad9f8b894f4e47d628d31884bbcbf748369db98b674f6300840afa2c0 | CANONICAL |
| EV-FEA12CORE-A-AC5 | AC5 专门确认 | verification/FEA-12-CORE/logs/core-py-ac5-digest-binding.log | null | d0ec0ccc7f3f5f53e84087b7c0fa13b06be7400616e0a90b3567cec2814f5d82 | CANONICAL |
| EV-FEA12CORE-A-AC6 | AC6 单事务/回滚 | verification/FEA-12-CORE/logs/core-py-ac6-transaction-rollback.log | null | 274cb41b8c5a069daa11617e0f3fccfde60e956b35db98d32c9e2cf18c405303 | CANONICAL |
| EV-FEA12CORE-A-AC7 | AC7 保护披露/边界 | verification/FEA-12-CORE/logs/core-py-ac7-protection-boundary.log | null | a16cdbc52dad49611cf52d54af2b3a868833e88a4bcbd7f389098267f2bed418 | CANONICAL |
| EV-FEA12CORE-A-AC8 | AC8 PD-08/原文件边界 | verification/FEA-12-CORE/logs/core-py-ac8-pd08-shared.log | null | 175f99b8abb676b6db9ed829afa98eb29df427bc3837840c99e8ccd10851b88e | CANONICAL |
| EV-FEA12CORE-A-AC9 | AC9 C-17 X1 子图 | verification/FEA-12-CORE/logs/core-py-ac9-c17-x1.log | null | 82652896fed7272efc9c8ae09d5c7cbc41b9e1996e4c7faef50fe09a08b117a8 | CANONICAL |
| EV-FEA12CORE-A-AC10 | AC10 统一 ProtectionPolicy | verification/FEA-12-CORE/logs/core-py-ac10-protection-policy.log | null | 9f602a487527f3589b77c1e24c2eb7af1b473f952c6f0988759cb7b3b0e35fb0 | CANONICAL |
| EV-FEA12CORE-A-AC11 | AC11 Python 侧（PARTIAL） | verification/FEA-12-CORE/logs/core-py-ac11-python-wire.log | null | 47453ebef4a0c57fd6a95ce6f46730f7552f1a00257d9759c2f1d37ebe429f58 | CANONICAL |
| EV-FEA12CORE-A-AC12 | AC12 隔离与禁令 | verification/FEA-12-CORE/logs/core-py-ac12-isolation.log | null | 638de24effd6faf19230fc5c8078d0b6df4baf235b6d3e629aaca7022d7c6308 | CANONICAL |
| EV-FEA12CORE-A-GATES | Gate G1–G9 门禁汇总 | verification/FEA-12-CORE/logs/gates-core-py.log | null | 76341321c73716d7ffef67daf3056d3d5c6a2b6c5c814dd1176a0d58b082193b | CANONICAL |
| EV-FEA12CORE-A-PYTEST-REL | Gate G3 相关组 | verification/FEA-12-CORE/logs/core-py-pytest-related.log | null | e6f4bd11a7639d0f31450d24c6cba8acd9df9a355dfce4c88274ffa4e89c4421 | CANONICAL |
| EV-FEA12CORE-A-PYTEST-FULL | Gate G4 全量 pytest | verification/FEA-12-CORE/logs/core-py-pytest-full.log | null | 92f6614d197da7a55e85fe4dac5eb791e3433b4f8df5904c160dfc502c84bf7a | CANONICAL |
| EV-FEA12CORE-A-PINS | Gate G1 pins 18/18 | verification/FEA-12-CORE/logs/core-py-pins.log | null | ab5d5708cd2cbf51cb922c26ef3f137c4a8a0b2bedab245fe606219da5b00d6d | CANONICAL |
| EV-FEA12CORE-A-CHECK | Gate G2 治理 check | verification/FEA-12-CORE/logs/core-py-check.log | null | c1235d55039154b509ba0b060e107652e60301803f85645eb01661cfd9110edb | CANONICAL |
| EV-FEA12CORE-A-PROBE-DIGEST | AC4/AC5 可复跑探针 | verification/FEA-12-CORE/scripts/core_py_inventory_digest.py | null | e7c4e5d822f43e1276ad05be4e9a1e63e2f374fdee02bf9a4d6b2e62bcc6134e | SOURCE_PIN |
| EV-FEA12CORE-A-PROBE-ISO | AC12 可复跑探针 | verification/FEA-12-CORE/scripts/core_py_isolation_scan.py | null | 997b0333e37d6115013a3a925818daf69466aaa503c6d82ad3ffb18ac104f0d1 | SOURCE_PIN |
| EV-FEA12CORE-A-HANDOFF | 分片 A 交付/Review 就绪 | doc/handoffs/FEA-12-CORE-core-py.md | null | 49ee56113d52042fd145cabf45c8e6c124f6b48380944d4b4a7c3d79fb389e57 | CANONICAL |

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
