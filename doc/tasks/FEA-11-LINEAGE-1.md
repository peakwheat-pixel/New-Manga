---
id: FEA-11-LINEAGE-1
title: FEA-11 lineage native 写入与读路径隔离（C-17 §7.1 续）
kind: implementation
governance_version: 3
status: changes_requested
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；r2 返修范围与口径由 DSH（Lead）2026-11-05 裁决确认（4 点，见 r2 DSH 裁决节）；r2 Review changes_requested（P1=1/P2=3/P3=5）→ r3 最小返修（见 r2 Review 处置计划）
suggested_owner: codex
owner: lineage-impl（r2 返修，DSH 派发 Team teammate；r3 返修继续由该 Owner）
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-11-LINEAGE-1-r1.md`；r2 `doc/reviews/FEA-11-LINEAGE-1-r2.md`，reviewer session `96e81d3c-b09d-4652-b3fe-270b91dc1c1a`）
depends_on:
  - FEA-11-PREREQ-1
base_commit: 81c28d305
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-LINEAGE-1
allowed_paths:
  - doc/tasks/FEA-11-LINEAGE-1.md
  - doc/reviews/FEA-11-LINEAGE-1-*.md
  - doc/handoffs/FEA-11-LINEAGE-1-*.md
  - src/application/editing/ports.py
  - src/application/editing/service.py
  - src/application/editing/drafts.py
  - src/application/sources/lineage.py（r2 新增：隔离 guard + typed code）
  - src/application/sources/service.py
  - src/application/sources/runtime.py
  - src/infrastructure/sqlite/source_sync.py
  - src/infrastructure/sqlite/regions.py
  - src/infrastructure/sqlite/pipeline.py（r2 窄批：Run lineage 写入与守卫）
  - src/infrastructure/providers/handlers.py（r3 窄批：page-scope Run detect 复用可见集合；DSH 2026-11-05 批准）
  - src/application/tasks/service.py（r3 窄批：detect 回填/候选提交 typed 投影；DSH 2026-11-05 批准）
  - src/application/rendering/**
  - src/application/export/**
  - src/bootstrap/core_service.py
  - src/bootstrap/core_assembly.py（DSH 窄批：lineage providers 注入与启动 backfill）
  - tests/fea11/test_source_lineage.py
  - tests/fea11/test_source_lineage_native.py
  - tests/fea11/test_source_lineage_assembly.py（r2 新增：装配级）
  - tests/fea11/conftest.py（r2 窄批：add_sync_switch 种子）
  - verification/FEA-11-LINEAGE-1/**
---

# FEA-11-LINEAGE-1

## Scope Review（DSH，2026-11-05，冻结）

- **范围（冻结）**：
  1. **AC1 native lineage 写入**：`src/infrastructure/sqlite/regions.py` 的 revision 写路径（`add_revision`/`commit_region_revision`/`commit_region_batch_guarded`/`_insert_revision`）在**同一 SQLite 事务**内登记 `source_revision_lineage`（复用 `source_sync.py` 的 `insert_lineage`）；覆盖 B1/R1→B2、same_content 边、changed 切断；draft 写路径（若适用）同口径。
  2. **AC2 读守卫**：`list_regions`（及渲染/导出/Run/编辑入口经 `src/application/rendering/**`、`src/application/export/**`）校验 region 当前 revision 的 lineage binding 与页面当前 binding 一致；不一致 → typed 拒绝（render/export/Run 明确错误码，不静默返回旧坐标）。
  3. **AC3 证据**：旧坐标对新图不可见（AC11-5 隔离）回归测试；`verification/FEA-11-LINEAGE-1/` 证据（含测试日志）。
- **依据**：C-17 §7.1；`doc/reviews/FEA-11-r1.md` R-009；AC11-5 隔离部分；`doc/reviews/FEA-11-r7-acceptance.md` 硬约束（LINEAGE-1 完成前任何 UI/读路径/渲染/导出/Run 不得消费同步 binding）。
- **现状核验（r1 时点）**：`source_sync.py` 已有 lineage 表操作（insert_lineage/lineage_of_revision/lineage_for_binding/lineage_exists_for_regions）；`service.py` 已有 `_capture_lineage`（first-switch capture）。**缺口**：regions.py 写路径未同事务登记 lineage；读路径无 binding 一致性守卫。
- **实施顺序**：AC1（写入+测试）→ AC2（守卫+测试）→ AC3（证据）→ 独立 Review（fresh subagent）→ closeout。
- **allowed_paths**（r1 P1-3 更正；r2 窄批补登；r3 窄批补登）：`application/editing/ports.py`、`application/editing/service.py`、`application/editing/drafts.py`、`application/sources/lineage.py`、`infrastructure/sqlite/pipeline.py`、`infrastructure/providers/handlers.py`（r3）、`application/tasks/service.py`（r3）、`tests/fea11/**`、`bootstrap/core_assembly.py`（共享组合根，DSH 窄批授权）。**`doc/TASK_LEDGER.md` 由 Lead 维护、不计入本卡 allowed_paths**（r2 Review R2-04 更正 r1 错误表述；本卡提交未再修改该文件）。
- **边界（不变）**：不 push；不改冻结契约字节（C-17/ADJ-001/FEA-01…）；不碰真实用户数据/AppData/外部卷/回收站；不新建依赖；实现者不自审。

## r2 DSH 裁决（Lead 2026-11-05，逐条确认 r2 方案）

1. **读守卫作用域**：C-17 §7.1 的规范对象是「本卡涉及的同步页」（字面范围收窄，不是放宽既有要求）。守卫仅在「页面当前 binding 链（`page_bindings.previous_binding_id` 回溯）上存在 `source_binding_publications` 行」时启用；无 page binding 跳过；非同步页（managed 页、或从未切换过的 referenced 页）保持预 LINEAGE-1 行为。**同步页内仍严格 fail-closed**：changed 切断 → typed 拒绝；无 lineage 行/`legacy_unverified`（binding_id NULL）/无 current revision → typed「不可验证」拒绝。
2. **错误码**：新增 **应用层** code `LINEAGE_BINDING_CHANGED` / `LINEAGE_UNVERIFIED`（旧命令面 `conflict`、`retryable=false`），不加入 C-17 §8 闭集、不修改冻结字节。**DSH 裁决：C-17 §8 仅覆盖 C-17 命令投影，旧命令不重映射**。映射表见下「读路径行为矩阵」。
3. **入口形态（旧坐标不可见优先于可用性）**：ListRegions/`list_page_region_texts`/page rerender/export 文本面 → **过滤**不可验证 region 并给出可诊断计数（stderr 一行计数 + render `reports` 的 skip code；不是静默丢失）；单 region rerender → typed `BLOCKED`；编辑写入与 Run region-scope expand → typed 拒绝；draft apply → 映射为 `DraftError(code=LINEAGE_*)`。page-scope Run → 过滤旧坐标 region（新图 region 集合不含旧坐标）。
4. **backfill**：仅覆盖已同步页（publication 链）、幂等、补 `legacy_unverified`（`binding_id=null`）、不猜归属、不抢占首次切换的 `captured_v7` 机会；`core_assembly` 启动时幂等调用一次；实现为「先查缺（anti-join）再插入」、在单事务内完成；**失败记录到 stderr 并继续装配，不使启动崩溃**；幂等复跑结果见 gates 证据（第二次插入 0 行）。

## r2 Review 处置计划（DSH，2026-11-05；Review = changes_requested）

- Review：`doc/reviews/FEA-11-LINEAGE-1-r2.md`（fresh subagent session `96e81d3c-b09d-4652-b3fe-270b91dc1c1a`；reviewed_head `3c40f7020`；P0=0/P1=1/P2=3/P3=5；AC1/AC3 MET，**AC2 PARTIAL**）。
- **R2-01（P1，必须修）**：page-scope Run 的 detect 复用绕过了 lineage 可见集合（`handlers.py` page-id-only repository → hidden region 被复用 → `_backfill_detected_regions` 抛 `LINEAGE_BINDING_CHANGED` → 被 `commit_step` 吞成 `DB_FAILED`）。修复口径：detect 复用必须用 lineage 可见 region 集合（guard/facts 注入 handler deps，或从 Run target snapshot 取可见 ids）；全 hidden 时在**新图**上执行检测；region-requiring 的 page 步骤（render/inpaint）在过滤后空集时 no-op/terminal 或 plan 期 typed 拒绝，不得 DB_FAILED。判别性测试：cut 页 + hidden region + stub detector 跑 `REOCR_ALL` → hidden id 不被复用、新 region 被检测、run 完成、hidden 无新 revision/lineage；`RERENDER_ALL` 干净终态或 typed 拒绝。
- **R2-02（P2，修）**：`commit_step` 显式捕获 lineage 码的 `PipelineError` → 路由到 `input_revision_changed`（保留 prepared candidate；旧命令面 conflict，不重映射 C-17 §8）+ 判别性测试。
- **R2-03（P2，修）**：补 4 个最小测试：draft apply cut 拒绝（typed + 零写）、batch/reorder/merge 写入侧拒绝、backfill 失败不阻断装配（monkeypatch 抛错 + 装配成功 + stderr 告警）、page render skip reports / `handle_rerender_page` LINEAGE 映射。
- **R2-04（P2，已处置于本卡文本）**：更正 line 56 的 `doc/TASK_LEDGER.md` 表述；该文件由 Lead 维护，不计入 allowed_paths（见上）。
- **P3 处置**：R2-05（lineage standing 增 `region_id` 归属校验 + 损坏数据拒绝测试）**本轮修**（低成本防御）；R2-06/R2-07（mixed 页 reorder/text 读诊断、freeze_context 过滤）登记为**已知限制/后续卡**，不在本轮扩大；R2-08（Host `AllowedRunErrorCodes` 未注册 LINEAGE_* 码）登记为**集成限制**（apps/** 不在本卡；后续 Host 窄批卡处理）；R2-09（EV sha256/delivery_head/log 头 shell 行）在 closeout 时补齐。
- **复审**：r3 交付后另派 fresh subagent 复审（不得由本轮实现者自审）。

## 实施记录（r2 返修，2026-11-05）

- **基线**：r1 head `acd3f2263`；r2 起点 `035468a81`（工作树 clean）。r1 `changes_requested`（P0=1/P1=5/P2=7）→ 本轮 `in_progress` → 交付 `in_review`。
- **新增 `application/sources/lineage.py`**：`LineageIsolationGuard` + `LineageFacts` 端口 + `RevisionLineageStanding` + typed 错误（`LineageBindingChanged`/`LineageUnverified`，`code`/`category=conflict`/`safe_message`）；`page_verdict()` 一次 page-binding 查询 + 一次批量 lineage 查询（消除守卫 N+1，r1 P2-6）。
- **SQLite 事实层**：`source_sync.py` 新增 `SourceSyncLineageFacts`（current binding、publication 链 sync-managed 判定、批量 lineage、`same_content` 多跳可达 = 沿 `source_binding_publications.previous` 只经 `same_content` 边）；`SourceSyncStore.backfill_legacy_unverified_lineage()`（anti-join 查缺 + 单事务插入、幂等、只覆盖已同步页）。
- **AC1 写路径补齐（同事务）**：`_commit`/`_commit_batch_or_raise`（既有）+ `_commit_user_or_raise`（`save_manual_translation`/`confirm_final`/`set_locks`）+ `restore_revision_with_number` + draft apply（`DraftProtectionService` 注入 `lineage_binding`，`commit_region_batch_guarded` 带 `lineage_by_region`）+ Run `pipeline._write_region_candidate` + `RegionRepository.add_revision`（端口+SQLite 实现可带 lineage）+ `region_revisions` 三个 INSERT 写者全部覆盖（grep 证据见 gates log gate 6，无旁路）。
- **写入侧防洗白（r2 关键）**：`SqliteRegionRepository` 在 `BEGIN IMMEDIATE` 内、写 revision/lineage 之前对 region 的**当前** revision 调用 `ensure_writable`（同一事务、事实层共享同一连接）；merge/split 把源 region 几何并入新 region 时也校验源 region 可证。历史 revision 被写路径遗漏 → 拒绝，而不是把旧 binding 坐标写成新 binding 的 native lineage。`LineageVerificationError` 在仓库 seam 中 rollback 后**原样上抛**（不降级 DB_FAILED）。
- **AC2 读守卫**：ListRegions/`list_page_region_texts`（`RegionEditingService._visible_regions` 过滤）、page rerender（`RenderService._active_regions` 过滤并在 `reports` 给 skip code）、单 region rerender（typed `BLOCKED`）、export 文本面（`_export_regions` 过滤 + 计数日志）、Run（page-scope 过滤、region-scope typed `PipelineError(code=LINEAGE_*)`、候选提交事务内 `ensure_writable`）。过滤/拒绝均有 stderr 诊断计数，不静默。
- **装配（P1-4）**：`core_assembly` 先建 `SourceSyncStore`/facts/guard，再建 repository/编辑/draft/render/pipeline catalog，**全部共享同一 guard**（装配级测试断言 identity）；启动时幂等 backfill（失败记录并继续）；`CoreServices.lineage_guard` 暴露给 wire 层；`core_service` 把 typed lineage 错误映射为既有 ErrorEnvelope（固定安全文本）。
- **测试（r1 P1-5 重写）**：`tests/fea11/test_source_lineage_native.py` 重写为真实 `:memory:` v8 库 + 生产类（无 fake repo/`__new__`），覆盖全写路径登记、回滚无孤儿行、changed/same_content 多跳/无 lineage/legacy_unverified、编辑与 Run typed 拒绝、混合库作用域矩阵；新增 `tests/fea11/test_source_lineage_assembly.py` 用真实 `assemble_core_services` + `CoreServiceServer` 验证装配接线、启动 backfill 调用点、wire 面 typed 响应与 export 过滤。测试数量：fea11 49 → 62 passed。
- **P2 快项（r1）**：`RegionRepository`/`RegionRevisionCommitter` 协议已声明 `lineage`/`lineage_by_region` 参数；`_commit_batch_or_raise` 改为显式参数调用（去掉 `**dict` + `type: ignore`）；`RevisionLineage.provenance` 使用冻结 Literal；SQLite 写者复用 `SourceSyncStore.insert_lineage`；守卫改为 page 级 1 次 + 批量 lineage 1 次查询（无 N+1）；in-memory committer 仍按既有契约忽略 lineage（无 lineage 表，仅测试/内存装配使用；生产 SQLite 全路径已覆盖）。
- **未变**：C-17/ADJ-001/FEA-01 等冻结契约零 diff（pins 18/18）；未新增依赖；未 push；未改 `doc/STATUS.md`/`REBASELINE_PLAN`/`TASK_LEDGER`/`doc/reviews/**`。
- **commit 列表**：`501fe80c8`（实现）、`7cc963065`（测试）、`436fe97f6`（诊断可见性/backfill 容错）、`966f7762e`（混合库矩阵测试）、证据/卡面 commit 见最终报告。

## 读路径行为矩阵（r2 证据摘要；完整矩阵见 gates-r2.log gate 2）

库形态（升级后的真实混合库）：

| 页面形态 | 守卫 | ListRegions/文本读 | 编辑写入 | 单 region rerender | Run | 说明 |
|---|---|---|---|---|---|---|
| managed 页（无 binding） | 跳过 | 全部可见 | 允许（无 lineage） | 放行（进入原渲染路径） | 允许 | 保持预 LINEAGE-1 行为 |
| referenced 页从未同步切换 | 跳过 | 全部可见 | 允许，登记 native(当前唯一 binding) | 放行 | 允许 | P0 回归保护；不因缺 lineage 拒绝 |
| 同步页 changed 切断 | 启用 | 过滤旧 region（计数可见） | 拒绝 `LINEAGE_BINDING_CHANGED` | `BLOCKED` 同 code | region-scope 拒绝同 code；page-scope 过滤 | 旧坐标对新图不可见 |
| 同步页 same_content（可多跳） | 启用 | 可见（沿等价边） | 允许，新 revision native 当前 binding | 放行 | 允许 | 坐标等价，C-17 §7.1 允许 |
| 同步页缺 lineage 行 / `legacy_unverified` | 启用 | 过滤（计数可见） | 拒绝 `LINEAGE_UNVERIFIED` | `BLOCKED` 同 code | region-scope 拒绝同 code | 不可验证即 fail-closed |

错误码投影（旧命令面，非 C-17 §8 重映射）：`LINEAGE_BINDING_CHANGED` / `LINEAGE_UNVERIFIED` → `category=conflict`、`retryable=false`、固定安全文本；命令映射：`list_regions`/`list_page_region_texts`/`list_region_revisions`/`set_region_type`/`restore_region_revision`/`_REGION_WRITE_COMMANDS` 的 dispatch 统一经 `_lineage_error_envelope`；`rerender_page` 经 `RenderCommandError`；Run 命令经 `_dispatch_run_command` 的 `PipelineError` 映射；`drafts_apply` 经 `_DRAFT_ERROR_CATEGORY`；export 文本面因为过滤（不是拒绝）不产生错误码。

## Acceptance Criteria

- [x] **AC1**：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；B1/R1→B2、same_content 边、changed 切断有测试。 <<MET>>
- [ ] **AC2**：ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding，否则 typed 拒绝；same_content 等价边放行；过滤结果带诊断计数）。 <<PARTIAL: r2 Review：各读面守卫/计数存在且有测试，但 page-scope Run 执行链在 changed/unverified 同步页复用 hidden region → DB_FAILED（R2-01）；draft/batch/render reports 判别性测试缺失（R2-03）；r3 修复后恢复 MET>>
- [x] **AC3**：AC11-5 隔离证据（旧坐标对新图不可见）与回归测试。 <<MET>>

## limitation 修订（r2）

- **L1（导出/Run/ListRegions/单区域渲染守卫）**：**部分闭环（r2 Review 判定）**——ListRegions/文本读过滤、export 文本面过滤、单 region rerender typed `BLOCKED`、page render 过滤+reports、Run region-scope 已有实现与证据；但 **page-scope Run 执行链**（R2-01）使「Run 过滤旧坐标 region」只在 expand 层成立、执行层 DB_FAILED；r3 修复后改回「已闭环」。
- **L2（AC11-5 集成测试）**：**已闭环**——真实 SQLite 仓储 + 装配级集成测试覆盖 native 写入→changed 拒绝 / same_content 放行（多跳）/ 无 lineage typed 诊断 / 回滚无孤儿行 / draft/Run/restore/批量登记。
- **L3（same_content 读边）**：**已闭环**——`SourceSyncLineageFacts.same_content_reachable` 沿 `publication.previous` 只经 `same_content` 边多跳；changed/repoint/missing 切断，测试覆盖。
- **残余（供 r2 Review 裁决）**：
  1. reader 投影（`handle_get_reader_projection`）只消费 translated artifact，不读 region 坐标；旧渲染 artifact 的 stale 判定沿用 FEA-11 既有 `rendered_from_revision_id`/`current_source_revision_id` 逻辑，未纳入本卡范围。若 Review 认为 r7 硬约束解除需覆盖 reader 投影，建议另开卡（不阻塞本卡 AC）。
  2. 非同步页面的「缺 lineage 不拒绝」是按 C-17 §7.1 字面范围的 DSH 裁决结果（见上）；r2 Review 应以此裁决为准复核，而不是据此判 PARTIAL。
  3. `run_source_guard`（lease/gate）与 lineage guard 是两层独立守卫；本卡只新增 lineage 层。

## Canonical Evidence

| evidence_id | 内容 | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-0 | r1 门禁日志（r1 head 的 fea11 49/native 9/9/全量 3060/0/10/.NET 见日志；保留原字节） | verification/FEA-11-LINEAGE-1/logs/gates.log | acd3f2263 | - | CANONICAL |
| EV-1 | r2 门禁日志（fea11/全量 pytest/check/pins/grep/诊断矩阵，含命令/EXIT/head） | verification/FEA-11-LINEAGE-1/logs/gates-r2.log | 791cfef28 | - | CANONICAL |

## r2 就绪声明

- r2 返修范围（r1 P0-1 写入覆盖 + 存量 backfill、P1-1 same_content 读边、P1-2 typed/入口覆盖、P1-5 真实仓储/装配测试、P2 快速项）已全部实现并有实体证据；AC1/AC2/AC3 均为 MET。
- **r2 Review 结果（2026-11-05，续）**：changes_requested（P1=1/P2=3/P3=5；AC1/AC3 MET，AC2 改判 PARTIAL）。处置见上「r2 Review 处置计划」；r3 返修完成后需 fresh subagent 复审，之后才可判 done。
- 门禁（Python-only）：`pytest tests/fea11` 62 passed；`pytest tests` 3073 passed / 10 skipped（基线 3060/10，新增 13）；`check.ps1` PASS；`verify_pins.ps1` 18/18 PASS；冻结契约零 diff；未 push。
- 本实现者**不自审**：请求 Lead 指派独立上下文 fresh reviewer 按本卡 + `doc/reviews/FEA-11-LINEAGE-1-r1.md` + r2 DSH 裁决做 r2 Review（重点：P0-1 六条写路径、守卫作用域裁决、typed 入口覆盖、backfill 幂等/不抢占 captured_v7、真实混合库矩阵证据）。
- 交付 head 与 commit 列表以最终报告为准（本卡 frontmatter `delivery_head` 由 Lead 集成时填写）。
