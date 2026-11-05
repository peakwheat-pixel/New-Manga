---
id: FEA-12-CORE
title: FEA-12 删除线首版实现（A 软删/恢复 + C 彻底删除 + 统一 ProtectionPolicy + Host 命令桥）
kind: implementation
governance_version: 3
status: in_review
approval: 用户 2026-11-05 指令（FEA-12 scope review → 冻结 → 实施 → 独立 Review）；范围冻结 ADJ-2026-11-05-FEA-12-SCOPE（D1–D8）；G-DELETE-IMPL 首版释放（隔离 fixture + 模拟回收站路径）；FEA-12-PREREQ-1 done（wire 冻结，`3e37c595b`）、FEA-11-LINEAGE-1 done（`90a8c8218`）；分片 A/B 已交付；CORE r1 Review changes_requested（P0/P1=0，P2=3，P3=8）→ Lead 处置 + r2 返修 → r2 approved（P0/P1/P2=0）→ closeout；**Codex 独立裁决（2026-11-05）OVERTURN 2 项（current 保护绑定不完整、混合 retry 绕过集合 digest）→ 重新打开返修（UNFREEZE C-04b v1.1 + M2-C1 rev 2.14）**；**r2 approved → done closeout → Codex 独立裁决 OVERTURN 3a/4 重开 → r3 返修交付 in_review（C-04b v1.1/M2-C1 rev 2.14：current 全量绑定 + retry 集合级 digest 始终校验；AC4/AC5 保持 PARTIAL 待 r3 Review 定稿）**
suggested_owner: dsh（dsh-agent-team teammates 分片，Lead 集成）
owner: fea12-core-py（分片 A）+ fea12-core-host（分片 B），Lead 集成
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-12-CORE-r1.md` session `b2e5e275-122b-44d4-98bc-c86fec7bfbc1`；r2 `doc/reviews/FEA-12-CORE-r2.md` session `113ad38d-f601-4e30-b2c7-0721a95ae384`；均未参与实现）
depends_on:
  - FEA-12-PREREQ-1
  - FEA-11-LINEAGE-1
base_commit: e47fd47e41add3edeb7f67e578eefeb48eddce50   # 2026-11-05 释放点 main head
branch: null
worktree: null
integration_commit: 3da210518
delivery_head: 3da210518
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
- [ ] **AC4 只读预览（PD-01/PD-03）**：预览前后 DB 逐表快照相等、文件 mtime/hash 不变；逐项返回 manualRegionCount/lockCount（三锁 ∪ text_json.translation_locked 并集）/currentRevisionId/**currentRegionRevisionIds（全部 region current，含隐藏）**/**currentArtifactRevisionIds（全部 artifact current）**/pinnedRevisionIds/activeRunIds/draftPageCount/deletedFiles/deletedBytes/sharedFileRefs；无路径/明文/堆栈；digest **v2** golden 向量可复算（字面量已钉死）。 <<PARTIAL: r3/r4 已按 C-04b v1.1 修复；r4 补齐冻结载体 §5-1 的 hidden current 变化判别测试（`test_preview_hidden_region_current_change_is_stale`：旧 digest STALE 零副作用、新 digest 成功）——待 r4 窄面复核/Lead 定稿恢复 MET>>
- [ ] **AC5 专门确认绑定（PD-02/PD-04；C-04b v1.1 §2.2）**：单/批量 `inventory_digest` 缺失/格式错 → `INVALID_REQUEST`；不匹配/重排/换目标 → `BOOK_DELETE_STALE_PREVIEW` 零副作用；集合级与逐书两级校验；单条拒收 `book_ids`；预览→确认间任何保护变化（含非首个/隐藏 current、artifact current）→ 拒绝并重预览；旧 Host 不传 digest fail-closed 不降级软删；**PD-07 retry（纯 pending 与混合）**：首次删除事务在 manifest 持久化原预览有序集合/逐书 digest/集合 digest/绑定输入，retry 校验保序 pending 子集 + 逐书 manifest 值 + **集合级始终校验**（不再形状校验）；corrupt manifest JSON→`BOOK_DELETE_STALE_PREVIEW`（单条/批量）、行缺失→`BOOK_NOT_FOUND`。 <<PARTIAL: r3/r4 已按 C-04b v1.1 §2.2/A3 修复（FAKE/重排/换目标/缺项/篡改/corrupt 全部 STALE；missing=NOT_FOUND；manifest 缺失 fail-closed）——待 r4 窄面复核/Lead 定稿恢复 MET>>
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
| AC1–AC12 | `C:/Python314/python.exe -m pytest tests/core tests/storage tests/maintenance tests/fea12 -q`（逐 AC 断言） | 隔离 fixture；真实 v1…v8 迁移 | **PASS 1116 passed**（r4 工作树，EXIT 0） | `verification/FEA-12-CORE/logs/core-py-pytest-related.log`、`gates-core-py.log` |
| 全量回归 | `pytest tests -q -p no:warnings --tb=no`；apps 零 diff（.NET 引用集成记录） | 仓库根；基线 3093/10 | **pytest 3164 passed/10 skipped EXIT 0**；集成全量 .NET 1405/0/80 | `logs/core-py-pytest-full.log`、`logs/gates-integration.log` |
| 治理 | `check.ps1`（含 `-TaskPath`）；`verify_pins.ps1`（18/18） | 仓库根；契约重冻后 | **check PASS（warnings 均既有全仓告警）；pins 18/18 PASS** | `logs/core-py-check.log`、`logs/core-py-pins.log`、`logs/gates-integration.log` |
| FK/回滚 | 故障注入：事务最后 DELETE 前抛错；probe 案例复跑（binding/lineage/publication） | 隔离 v8 fixture | **PASS**：AC6 回滚零残留、AC9 probe FK 由失败转成功（变异实验判别成立） | `logs/core-py-ac6-transaction-rollback.log`、`logs/core-py-ac9-c17-x1.log`、`doc/reviews/FEA-12-CORE-r2.md` |

## 依赖、风险与阻塞

- 硬依赖：`FEA-12-PREREQ-1`（wire 冻结）；`FEA-11-LINEAGE-1`（`core_service.py`/`core_assembly.py`/sqlite 写域串行）。
- 风险：①PD-08 修正会改变既有测试期望（`test_core_delete_commands.py:323,378`）→ 登记"预期行为变更"，Review 不判回归；②X1 删除 lineage 的审计含义（ADJ §5.1）；③显式 `BEGIN IMMEDIATE` 与现有 `with self._conn:` 差异；④批量 pending 重试语义（PD-07/09）；⑤`.NET` 首跑 flaky（FEA-11 L-11）→ 复跑并记录。
- 阻塞解除标准：PREREQ-1 集成 + LINEAGE-1 closeout + 本卡 AC 证据齐备 + 独立 Review approved。

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-12-CORE-core-py.md`（分片 A：Python Core；commit 列表见 Handoff 与 `verification/FEA-12-CORE/logs/gates-core-py.log`）。
- Review：r1 changes_requested → r2 返修 → r2 approved（`doc/reviews/FEA-12-CORE-r2.md`）→ r2 closeout；2026-11-05 Codex 独立裁决 OVERTURN 3a/4 `doc/reviews/DSH-DECISIONS-2026-11-05-codex.md` → 本卡重开 → r3 返修（待 fresh r3 Review）。
- 实际测试（分片 A **r3** 实跑，命令/EXIT/head 见 `verification/FEA-12-CORE/logs/gates-core-py.log`）：
  - `pytest tests/core tests/storage tests/maintenance tests/fea12 -q`：**1116 passed**（相关组；r2 1104 + r3 10 + r4 2）。
  - `pytest tests -q -p no:warnings --tb=no`：**3164 passed / 10 skipped**（基线 3093/10；测试增量口径 **CORE +63 / DSIM-1 +8** = +71，r4 新增 2 条 CORE 测试，无失败）。
  - `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md`：重冻后 PASS（warnings 均既有全仓告警）。
  - `pwsh -NoProfile -File tools/governance/verify_pins.ps1`：重冻后 18/18 PASS。
  - 证据探针（r3 重新生成）：`scripts/core_py_inventory_digest.py`（digest v2 + current 数组 + R-001 derived 向量）与 `scripts/core_py_isolation_scan.py`（R-004 修复后）均 EXIT=0。
  - apps/.NET：**零 diff**（preview minor 保持 11，Host 无需改动）；全量 .NET 集成记录 1405/0/80 维持。
- 提交（r3）：仅本卡 allowed_paths 文件（apps/.NET 零 diff）；commit 列表见 Handoff §1（r1/r2 历史 + r3 源码/测试/证据 commit + card/Handoff commit）。

## DSH 裁决/实现语义（分片 A 固化，2026-11-05）

Lead 已裁决以下 8 点；完整依据、canonical 形式与证据见 `verification/FEA-12-CORE/core-py-implementation-record.md` §2：

1. 分片 A = Python Core；.NET Host 桥/R-002 归 task-7；AC11 在分片 A 标 PARTIAL（Python 侧 MET）。
2. **current 保护（C-04b v1.1，Codex OVERTURN 3a）**：绑定由两个完整数组承担——
   `currentRegionRevisionIds`（**全部** region current，**含 lineage-hidden/separate/detached
   等历史不可见 region**，不按可见性裁剪；全序、去重）与 `currentArtifactRevisionIds`
   （全部 artifact current，排序去重）。`currentRevisionId` 仅保留**代表展示值**（首个
   lineage-visible region current → 否则首个 artifact current → 否则 `null`），
   **不入 digest v2**。golden v2 向量已固化。
3. **`pinnedRevisionIds`** = `region_revisions.is_pinned=1 ∪ artifact_revisions.is_pinned=1`（去重排序；覆盖 PD-01"受保护 artifact"披露）。
4. **`sharedFileRefs.fileId`**：managed 共享文件 = `"managed:" + sha256(managed 相对路径) 前 16 hex`（不泄路径）；引用源共享 = `source_entries.entry_id`；`otherProjectCount` = 目标集外其他 book 引用数；该结构进入 digest 输入且稳定可复算。
5. **`PurgeTrash` 首版不实现**：typed `UNKNOWN_COMMAND`（validation/false）fail-closed、零副作用、不追加 digest 字段。capability `library.trash.write/1` 公告仅代表 `MoveToTrash`/`RestoreFromTrash` 可用；UI 不得调用 `PurgeTrash`，Host 不得以 `UNKNOWN_COMMAND` 探测能力。
6. **digest 必填**（M2-C1 rev 2.14 §5.11.1a；canonical v2 见 C-04b v1.1）：旧 Host 不传 → `INVALID_REQUEST` fail-closed，不得忽略 digest 或降级软删；既有 delete 测试按"先 Preview 再回传 digest"更新（预期行为变更，非放宽断言）。preview wire minor 12。
7. **PD-08 跨项目 revision 引用**：可安全拆分不阻断——事务内把目标集外行 `source_artifact_revision_id` 置 NULL（保留存活行与文件），目标行删除；仅真正不可拆/关系图不一致/未列明目标外引用才 `BOOK_DELETE_CONFLICT`（依据 ADJ D3 + page 级 purge 先例，见 `tests/storage/test_purge_integrity.py::test_purge_clears_cross_page_provenance_instead_of_failing`）。
8. **文件放置**：`ProtectionPolicy`/`ProtectionFacts`/`ProtectionVerdict` 在 `src/application/maintenance/ports.py` 且不 import infrastructure；`Book.restore` 在 domain；digest/cursor 纯函数在 `src/application/library/service.py`；DB 在 `src/infrastructure/sqlite/library.py`；**不改 `core_assembly.py`**。
9. **retry 集合级 digest（C-04b v1.1 §2.2 / A3，Codex OVERTURN 4）**：首次删除事务在
   `book_cleanup_manifests.targets_json`（JSON additive，无 DDL）持久化原预览有序
   `book_ids`、逐书 `inventory_digest` map、集合级 `inventory_digest`、每书 canonical v2
   绑定输入；retry 的 `book_ids` 必须是原预览有序集合的**保序 pending 子集**，
   `inventory_digests` 逐项等于 manifest 值（并用持久化输入重算检测篡改），集合级
   digest **始终**按请求顺序重拼接校验（纯 pending 与混合均不跳过）；live 目标强校验
   当前重算值。失配/重排/换目标/缺失/篡改 → `BOOK_DELETE_STALE_PREVIEW` 零副作用；
   缺失/格式错 → `INVALID_REQUEST`。**取消 r2 R-008「仅形状校验」限定**。

## 预期行为变更（Review 不判回归）

1. **digest 必填**：既有 delete 测试全部改为先 Preview 再回传 digest（§5.11.1a 冻结）；旧 Host 不传 digest 必须 fail-closed。
2. **PD-08 共享引用**：原"存在共享 managed/artifact/跨项目 revision 引用 → 一律 `BOOK_DELETE_CONFLICT`"按 ADJ D3 修正：可安全拆分不阻断（原 `test_core_delete_commands.py:323,378` 期望随之更新）；共享物理文件与其他项目 binding 保留、跨项目 provenance 置 NULL；仅不可拆分才 CONFLICT。
3. **page 级 purge 补 C-17 子图**（`purge_pages`）：`tests/storage/test_purge_integrity.py` fixture 补 v7/v8 行后仍全绿（D1 X1 同语义，child-first）。
4. **capability 列表新增 3 名**：生产装配的 `tests/core/test_core_service.py` 断言随之更新；无 library repository 的最小手搭 Core 不公告（`tests/fea09` 既有断言不变）。
5. **C-04b v1.1 / M2-C1 rev 2.14（r3）**：preview wire minor **保持 11**（新增响应字段
   additive optional）；`protection` 增两 current 数组（字典序排序去重，region 含 hidden）；
   digest canonical v2（`currentRevisionId` 移出绑定）；retry 改为“保序 pending 子集 +
   原集合 digest 原样回传 + mixed 拒绝”。apps/.NET 零 diff。

## r1 Review 处置计划（DSH，2026-11-05；Review = changes_requested）

> 依据：`doc/reviews/FEA-12-CORE-r1.md`（fresh subagent session `b2e5e275-122b-44d4-98bc-c86fec7bfbc1`；reviewed_head `85db8354f`，observed `388f5476e`；P0/P1=0，P2=3，P3=9（reviewer 最终版））。代码主体质量获认可（独立复跑 pytest 3144/10、.NET 1405/0/80、pins 18/18、3 个变异实验判别成立）。

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
  - **r2 门禁**：相关组 1104 passed；全量 pytest 3152 passed/10 skipped；check PASS（3 warnings）；pins 18/18；probes EXIT=0（见 gates log）。
- **复审**：r2 交付后另派 fresh subagent 复审（reviewed_head = r2 交付 head；只审新 head；R-001 修复 + R-004/R-005/R-007/R-008/R-009/R-010/R-011 处置）。
- **closeout 前置**：AC4 恢复 MET、AC11 已 MET、测试表/指针/证据表定稿、`check.ps1 -TaskPath` PASS。

## r3 返修结果（Codex OVERTURN 3a/4；C-04b v1.1 + M2-C1 rev 2.14，2026-11-05）

> 依据：`doc/reviews/DSH-DECISIONS-2026-11-05-codex.md`（Codex 独立裁决，3a/4 OVERTURN、2 措辞更正、b/c CONFIRM）与 `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`（经 r5/r7 复核）。**已重冻**：UNFREEZE commit `fc9833479`；C-04b v1.1 sha256 `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`、M2-C1 rev 2.14 sha256 `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f`；pins 18/18。实现者 `fea12-core-py`。

- **3a（current 全量绑定）已修**：`protection` 增 `currentRegionRevisionIds`（**全部** region current，含 lineage-hidden/separate/detached，不按可见性裁剪；字典序排序去重）与 `currentArtifactRevisionIds`（全部 artifact current，字典序排序去重）；`currentRevisionId` 仅代表展示值并**移出 digest v2**；canonical v2（UNFREEZE §A2 字段表）、golden v2；preview wire minor **保持 11（不 bump，新增字段 additive optional）**。
  - 判别测试：`test_preview_binds_non_first_region_current`（改非首个 current → 旧 digest STALE 零副作用；代表值不变也拒绝）、`test_preview_current_revision_uses_lineage_visibility`（hidden current=rr1 仍入绑定集、代表值 null）、**`test_preview_hidden_region_current_change_is_stale`（r4 P1-1：hidden current 变化 → 旧 digest STALE、全表/文件零副作用；新 digest 成功）**、`test_preview_binds_artifact_current_set`（artifact current 增/改/删）、`test_preview_binds_region_current_add_and_remove`（集合增删）。
- **4（retry 集合级 digest）已修**：首次删除事务在 `book_cleanup_manifests.targets_json` **JSON additive**（无 DDL）按行持久化 `batch_id`/`original_book_ids`（原预览有序全量）/`original_collection_digest`/`book_id`/`inventory_digest`/`inventory_inputs`（canonical v2 输入快照），批次字段逐行复制、同事务写。**形状分支（最终字节）**：单条命令的 `inventory_digest` = 该书**逐书 digest**（首次=当前重算；retry=manifest 逐书值，不接受集合级值）；批量首次=`live` 重算**集合级**值，retry=manifest `original_collection_digest` **原样回传**；`inventory_digests` key 必须恰好覆盖请求 `book_ids`（缺/多 key → `INVALID_REQUEST`）。retry 校验：`book_ids` 为原预览有序集合的**保序 pending 子集**；逐书等于 manifest 值（并用 `inventory_inputs` 重算检测篡改）；**mixed live+retry 一律拒绝**（STALE 零副作用，须重新预览）；**retry 不受“一次预览→一次确认”时效限制**（PD-07，以 manifest 值校验、不重跑预览）。FAKE、重排、换目标、缺项、key 覆盖错、manifest 缺失/篡改全部拒绝且零副作用；纯 pending 正确路径幂等。
  - 判别测试：`test_delete_books_retry_collection_digest_is_always_validated`、`test_delete_books_retry_order_must_follow_original_preview`、`test_delete_books_retry_manifest_tamper_is_stale_and_missing_is_book_not_found`、`test_delete_book_cleanup_pending_retry_requires_manifest_digest`、**`test_retry_corrupt_manifest_is_stale_both_shapes`（r4 P2-1：corrupt JSON→STALE 单条/批量、零副作用）**；原 r2“FAKE_DIGEST 通过”断言已改为 STALE 断言。
- **措辞更正（裁决 2）**：M2-C1 rev 2.13 实为 **166 insertions / 2 deletions**（版本状态行 + §11 policy 行授权替换），非“纯 additive/既有行零变化”；卡/记录/Handoff 已同步。
- **Host / apps**：按最终契约 preview minor **保持 11**，**apps/.NET 零 diff**（先前按草案批准的 11→12 窄批已全部回退；Host 对新增 additive optional 响应字段无需改动）。
- **门禁（r4 工作树）**：相关组 **1116 passed**；全量 pytest **3164 passed / 10 skipped**；apps 零 diff（不跑 .NET 窄批；全量 .NET 引用集成 1405/0/80）；golden v2 / isolation probes EXIT=0；契约重冻后 `check.ps1 -TaskPath` 与 `verify_pins.ps1`（18/18）复跑并记入 gates log。
- **状态**：保持 `in_review`；AC4/AC5 由 Lead 在 r3 Review 后定稿，不自行改回 MET。

## r4 最小返修结果（r3 Review changes_requested：P0=0/P1=1/P2=1/P3=6）

- **P1-1（证据缺口）已修**：新增 `test_preview_hidden_region_current_change_is_stale`（hidden region current rr1→rr2，代表值仍 null；旧 digest 单条确认 → `BOOK_DELETE_STALE_PREVIEW`，全表快照与受管文件字节零变化；新 digest 成功删除）；卡 AC4/AC5、实施记录 §2.8/§8、Handoff §3 已如实引用，不再声称旧测试覆盖该反例。
- **P2-1（corrupt manifest 分类）已修**：repository 新增 `get_cleanup_manifest_state` 区分 `missing`/`corrupt`/`ok`；`_delete_target_state` 增 `corrupt` 态；单条 corrupt→`BOOK_DELETE_STALE_PREVIEW`、批量 corrupt→顶层 STALE + items 标注；行缺失仍 `BOOK_NOT_FOUND`。补 `test_retry_corrupt_manifest_is_stale_both_shapes`（单条/批量、零副作用、修复 payload 后可重试）。
- **P3 同批**：记录/卡 `preview minor 12`→11；旧 mixed 测试名与“tamper_or_missing”测试名更正；manifest 表述改为顶层 6 键；retry 表述改“原集合 digest 原样回传”；gates “tests 3 文件”→“2 文件”；Handoff 从 r3 commit 列表移除未改动的 `tests/fea12`；preview golden 钉死 v2 字面量；EV-A-GATES pin 改为 r4 主提交并注明“evidence commit pin（head 行在后续 head-pin 提交追加，不改证据字节）”；冻结记录 r7/STATUS/Plan 由 Lead 收口。
- **AC 状态**：AC1–AC3、AC6–AC10、AC11、AC12 = MET；**AC4 待 Lead 恢复 MET**；**AC5 保持 PARTIAL 待 r4 窄面复核/Lead 定稿**。


- **r2 Review 结果（2026-11-05）**：**approved（P0/P1/P2=0，P3=10 非阻断）**。R-001 派生文件披露真实修复（catalog 同源查询 + managed 去重 + catalog 失败 typed UNAVAILABLE；golden derived 向量 3 files/46 bytes；变异去除→测试精确失败）；R-008/R-009/R-010/R-011/R-012/R-004/R-005/R-007 逐项核销；独立复跑相关组 1104、全量 pytest 3152/10、pins 18/18、check PASS(3 warnings)、golden/isolation 探针一致；报告 `doc/reviews/FEA-12-CORE-r2.md`（session `113ad38d-f601-4e30-b2c7-0721a95ae384`）。AC4 恢复 MET、AC11 维持 MET（Lead 定稿）。
- **r2 Review P3 残留（如实保留，不阻断）**：check 警告数/`gates-core-py.log` purge 11→10 等过程记录口径、`EV-A-HANDOFF` pin 已更新为终稿 `3da210518`、Handoff "19→3" 笔误；1 条 catalog 失败→UNAVAILABLE 的仓库测试为可选补充（行为已由 Reviewer 探针验证）。上述不改写已 review 的代码/证据字节。

## Codex 裁决与返修计划（2026-11-05，重新打开）

> 裁决记录：`doc/reviews/DSH-DECISIONS-2026-11-05-codex.md`（Codex 只读独立核验，基线 `604a2d343`；4 项 DSH 裁决：1=CONFIRM、2=CONFIRM（非纯新增行）、3=OVERTURN(a)、4=OVERTURN）。UNFREEZE 提案：`doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md`。

- **缺陷 1（OVERTURN 3a）**：`protection.currentRevisionId` 只绑定一个代表 current；Codex 复现：第二个 region 的 current 从 `rr2` 改为 `rr2-new` 后 digest 不变，旧摘要删除成功（`run-43e38c334dbb48439f82519792fbb34e/current-pointer-probe.json`）。违反 ADJ-001 PD-04「保护集合变化即失效」。**处置**：UNFREEZE C-04b v1.1——预览 DTO 增 `currentRegionRevisionIds[]`/`currentArtifactRevisionIds[]`（完整披露），digest canonical v2 绑定全部 current；非首个 current 变化必须 STALE 零副作用。
- **缺陷 2（OVERTURN 4）**：混合 live+retry 批次跳过集合级 digest（`core_service.py:2437`），`test_core_delete_commands.py:1348` 以 `FAKE_DIGEST` 删除存活书成功。违反 C-04b §2.2 两级都校验。**处置**：集合级 digest 始终绑定完整有序目标集（纯 pending 与混合都一样）；逐书 live 强校验 / pending 按 manifest；错误/重排/换目标/缺失全部拒绝且零副作用。
- **裁决 2 措辞更正（Codex）**：M2-C1 rev 2.13 实为 166 insertions / 2 deletions（版本状态行 + §11 policy 行授权替换），不得表述为"纯 additive/既有行零变化"；相关卡/记录同步更正。
- **b/c 确认**：pinnedRevisionIds 两类并集、deletedFiles/Bytes 含 catalog 派生文件口径不变。
- **返修流程**：①UNFREEZE 提案 fresh subagent 复核；②Lead 执行契约修订 + 重冻 + pins 18/18；③返修实现（fixed 目标：current 全量绑定 + 混合 retry 集合 digest + tests/golden）；④fresh r3 Review；⑤重新 closeout（delivery head 更新）。
- **返修写入域**：`src/bootstrap/core_service.py`、`src/application/library/service.py`、`src/infrastructure/sqlite/library.py`、`tests/core/test_core_delete_commands.py`、`tests/core/test_core_delete_preview_commands.py`、`tests/storage/test_purge_integrity.py`、`verification/FEA-12-CORE/**`；**apps/.NET 零 diff**（最终契约 preview minor 保持 11；此前按草案的窄批已回退）。不改 schema/依赖/apps。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA12CORE-A-RECORD | AC1–AC12 实施记录/证据索引 | verification/FEA-12-CORE/core-py-implementation-record.md | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-DIGEST | AC4/AC5 golden 向量 | verification/FEA-12-CORE/evidence/core-py-inventory-digest-golden.json | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-ISOLATION | AC8/AC12 静态+运行时哨兵 | verification/FEA-12-CORE/evidence/core-py-isolation-scan.json | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC1 | AC1 软删 | verification/FEA-12-CORE/logs/core-py-ac1-move-to-trash.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC2 | AC2 恢复 | verification/FEA-12-CORE/logs/core-py-ac2-restore.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC3 | AC3 读取面 | verification/FEA-12-CORE/logs/core-py-ac3-recycle-read.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC4 | AC4 只读预览 | verification/FEA-12-CORE/logs/core-py-ac4-preview.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC5 | AC5 专门确认 | verification/FEA-12-CORE/logs/core-py-ac5-digest-binding.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC6 | AC6 单事务/回滚 | verification/FEA-12-CORE/logs/core-py-ac6-transaction-rollback.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC7 | AC7 保护披露/边界 | verification/FEA-12-CORE/logs/core-py-ac7-protection-boundary.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC8 | AC8 PD-08/原文件边界 | verification/FEA-12-CORE/logs/core-py-ac8-pd08-shared.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC9 | AC9 C-17 X1 子图 | verification/FEA-12-CORE/logs/core-py-ac9-c17-x1.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC10 | AC10 统一 ProtectionPolicy | verification/FEA-12-CORE/logs/core-py-ac10-protection-policy.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC11 | AC11 Python 侧（PARTIAL） | verification/FEA-12-CORE/logs/core-py-ac11-python-wire.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-AC12 | AC12 隔离与禁令 | verification/FEA-12-CORE/logs/core-py-ac12-isolation.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-GATES | Gate G1–G9 门禁汇总（evidence commit pin；最终 head 行只在后续 docs/head-pin 提交追加，不改证据字节） | verification/FEA-12-CORE/logs/gates-core-py.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-PYTEST-REL | Gate G3 相关组 | verification/FEA-12-CORE/logs/core-py-pytest-related.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-PYTEST-FULL | Gate G4 全量 pytest | verification/FEA-12-CORE/logs/core-py-pytest-full.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-PINS | Gate G1 pins 18/18 | verification/FEA-12-CORE/logs/core-py-pins.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-CHECK | Gate G2 治理 check | verification/FEA-12-CORE/logs/core-py-check.log | 44718d3c9 | null | CANONICAL |
| EV-FEA12CORE-A-PROBE-DIGEST | AC4/AC5 可复跑探针 | verification/FEA-12-CORE/scripts/core_py_inventory_digest.py | 44718d3c9 | null | SOURCE_PIN |
| EV-FEA12CORE-A-PROBE-ISO | AC12 可复跑探针 | verification/FEA-12-CORE/scripts/core_py_isolation_scan.py | 44718d3c9 | null | SOURCE_PIN |
| EV-FEA12CORE-A-HANDOFF | 分片 A 交付/Review 就绪（终稿） | doc/handoffs/FEA-12-CORE-core-py.md | 659c679be | null | CANONICAL |
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
| EV-FEA12CORE-R2-REVIEW | Gate/Review（r2 独立复审 approved） | doc/reviews/FEA-12-CORE-r2.md | - | b1c340b52b6a24750701094e199bf231d3259731a20e8568cae8c777f6feef8d | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | `G:\CODEX\New Manga.workspace\FEA-12\integration\`、`review-core\`、`review-core-r2\` | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-12` | verification/FEA-12-CORE/logs/gates-integration.log | Lead 集成门禁/独立 Reviewer 日志与报告输入；判别力证据以仓内 verification/FEA-12-CORE/** 为准；不清理 |
| worktree | NOT_APPLICABLE（main 工作树，DSH 集成） | NOT_APPLICABLE | — | — | — |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-12-CORE\` | DELETE_SAFE | — | verification/FEA-12-CORE/logs/gates-integration.log | 隔离 fixture 临时根；**DSH 2026-11-05 closeout 已删除**：53 files / 475,640 bytes（删除后不存在；无独有内容，证据已入仓） |

## Closeout Record

- **注：本记录为 r2 closeout 历史；2026-11-05 Codex 独立裁决 OVERTURN 3a/4 后本卡重开（status changes_requested → r3 in_review），由 Lead 在 r3 Review 后更新本记录与 delivery_head。**
- Closeout date / DSH：2026-11-05 / DSH（Lead/Architect/Integrator）。
- 终态：`done`；integration_commit / delivery_head = `3da210518`（r2 交付 head；main 线性集成，无 merge commit）。
- Review 链：r1 changes_requested（P0/P1=0，P2=3/P3=9）→ r2 最小返修 → **r2 approved（P0/P1/P2=0，P3=10 非阻断）**；Reviewer 均为独立上下文 fresh subagent（session 见 frontmatter/报告）。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- AC 定稿：AC1–AC12 全部 MET（AC4 由 Lead 按 r2 复审定稿恢复；AC11 由 Lead 定稿合并 Python+Host 两侧）。
- 残余风险/限定（如实保留）：①`activeRunIds` 不含 active export（wire 冻结无字段；export 仍 BOOK_BUSY 阻断）；②PD-07 retry 混合批次集合级 digest 仅形状校验（R-008 DSH 限定；逐书强校验）；③大书预览有 catalog lookup/stat 成本；④catalog 读失败 fail-closed retryable（`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`）；⑤真实 Windows 回收站 D 流程 NOT_RUN（范围冻结，属 DSIM-1/后续授权）；⑥`PurgeTrash` 首版不实现（typed unsupported）；⑦r2 Review P3 10 项为文档/证据精度与 1 条可选补充测试（不影响契约行为）。
- 删除、迁移、归档数量/字节数：temp 目录 DELETE_SAFE 已删除（53 files / 475,640 B）；无迁移/归档。
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新；本卡为终态，不进入 READY DAG。
- 用户/Lead 裁决引用：ADJ-2026-11-05-FEA-12-SCOPE（D1 X1、D2、D3 PD-08、D4 M2-C1 rev 2.13、D5 D 模拟、D6 写域）；R-001 派生披露按冻结语义修复（C-04b/PD-01）。
