---
id: FEA-12-CORE
title: FEA-12 删除线首版实现（A 软删/恢复 + C 彻底删除 + 统一 ProtectionPolicy + Host 命令桥）
kind: implementation
governance_version: 3
status: proposed
approval: 用户 2026-11-05 指令（FEA-12 scope review → 冻结 → 实施 → 独立 Review）；范围冻结 ADJ-2026-11-05-FEA-12-SCOPE（D1–D8）；G-DELETE-IMPL 首版释放（隔离 fixture + 模拟回收站路径）
suggested_owner: dsh（dsh-agent-team teammates 分片，Lead 集成）
owner: null
reviewer: 独立上下文 fresh subagent（未参与实现；会话 id 记录在 Review 报告）
depends_on:
  - FEA-12-PREREQ-1
  - FEA-11-LINEAGE-1
base_commit: null   # 释放时由 Lead 固定（PREREQ-1 closeout 后的 main head）
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

- [ ] **AC1 软删（MoveToTrash）**：逐项 `moved/skipped`；书架不再含、回收站含；DB 除 `books.deleted_at` 外内容行/保护行/current/pin/进度/binding 全不变；受管文件字节哈希前后一致。
- [ ] **AC2 恢复（RestoreFromTrash）**：恢复后书架可见；current/pin/进度/人工数据/binding 与删除前逐字段相等；不存在静默解锁/改 current；不存在条目 → 逐项冲突不整批失败。
- [ ] **AC3 回收站读取面不回归**：`ListRecycleBinBooks` 保持冻结投影（`page_count` `None` 通道、空数组≠失败）；`ListTrash` 映射按 PREREQ-1 冻结形状。
- [ ] **AC4 只读预览（PD-01/PD-03）**：预览前后 DB 逐表快照相等、文件 mtime/hash 不变；逐项返回 manualRegionCount/lockCount（三锁 ∪ text_json.translation_locked 并集）/currentRevisionId/pinnedRevisionIds/activeRunIds/draftPageCount/deletedFiles/deletedBytes/sharedFileRefs；无路径/明文/堆栈；digest golden 向量可复算。
- [ ] **AC5 专门确认绑定（PD-02/PD-04）**：单/批量 `inventory_digest` 缺失/格式错 → `INVALID_REQUEST`；不匹配 → `BOOK_DELETE_STALE_PREVIEW`；集合级与逐书两级校验；单条拒收 `book_ids`；预览→确认间任何保护变化 → 拒绝并重预览；旧 Host 不传 digest fail-closed 不降级软删。
- [ ] **AC6 单事务与失败回滚（PD-05/PD-06）**：显式 `BEGIN IMMEDIATE`；成功路径内容行按白名单消失、Pipeline 历史脱离保留、清理清单同事务持久化；事务最后一条 DELETE 前注入异常 → 内容行/保护行/v7-v8 行/文件集合与事务前逐项相等、`foreign_key_check` 空、不开始文件清理。
- [ ] **AC7 保护披露与删除边界**：含锁/人工/pin/current/draft 的书预览披露计数准确；删除成功后受保护行确实删除（披露≠阻断）；事务前无顺手解锁/取消 pin/改 current；非终态 Run/Task/Export → `BOOK_BUSY` 零副作用。
- [ ] **AC8 共享引用与原文件边界（PD-08）**：可安全拆分共享引用 → 删除成功、原文件字节与其他项目绑定不变；不可拆分/关系图不一致/未列明目标外引用 → `BOOK_DELETE_CONFLICT` 零副作用；用户源文件/源目录逐文件哈希与集合前后不变；零 Windows 回收站 API（静态 grep + 运行时哨兵）。
- [ ] **AC9 C-17 子图（D1 X1）**：含 `page_bindings` + `source_binding_publications` + `source_revision_lineage` 的书按 X1 同事务删除成功、`foreign_key_check` 空；非终态 source operation → `BOOK_BUSY` 零副作用；`source_sync_plans`/`source_operations` 保留可查询；probe FK 案例变为成功并被测试覆盖。
- [ ] **AC10 统一 ProtectionPolicy**：A/C 共用同一判定函数（同名 scope 判定一致）；有锁+有草稿：软删通过、彻底删除先披露后可执行；非终态 Run 彻底删除 `BOOK_BUSY`；cache 清理不命中受保护对象（回归）。
- [ ] **AC11 Host 命令桥（按 PREREQ-1 wire）**：新命令在 registry/dispatcher/client 注册且与 Core shape 一致；capability 缺失 → `CORE_CAPABILITY_MISSING`（并按「前置事实」R-002 二选一处置其投影，附判别测试）；旧 Core/旧 Host fail-closed；负向对照按 PREREQ-1 结果；`PurgeTrash` 不实现（只按冻结 wire 登记，禁止偷偷实现）。
- [ ] **AC12 隔离与禁令（元 AC）**：全部删除/回收站测试使用隔离 DataRoot（`tmp_path`/workspace 临时根）；代码/脚本 0 处真实 `%APPDATA%`/真实盘符/真实回收站路径；运行时哨兵证明隔离根外零变化；真实 Windows API 0 调用；真实用户数据零触碰。

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

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

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
