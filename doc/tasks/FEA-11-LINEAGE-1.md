---
id: FEA-11-LINEAGE-1
title: FEA-11 lineage native 写入与读路径隔离（C-17 §7.1 续）
kind: implementation
governance_version: 3
status: done
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；r2 DSH 4 点裁决；r1/r2/r3 changes_requested → 返修；**r4 Review approved（P0/P1/P2=0，P3=1 cosmetic）→ DSH 集成 closeout**
suggested_owner: codex
owner: lineage-impl（r2/r3 返修，DSH 派发 Team teammate）；r3 Review 处置/closeout 由 Lead 执行（findings disposition / integration）
reviewer: 独立上下文 fresh subagent（r1 `-r1.md`；r2 `-r2.md` session `96e81d3c-b09d-4652-b3fe-270b91dc1c1a`；r3 `-r3.md` session `49d520be-0862-41b2-87f0-0ec35dc28b3d`；r4 `-r4.md` session `dde30402-06b5-43e7-ae1d-374408e55823` approved）
depends_on:
  - FEA-11-PREREQ-1
base_commit: 81c28d305
branch: null
worktree: null
integration_commit: 90a8c8218
delivery_head: 90a8c8218
canonical_evidence_status: complete
resource_closeout_status: complete
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
  - tests/fea11/test_source_lineage_run.py（r3 新增：Run 执行链判别性测试；r3 Review P3 补登）
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

## r3 实施记录与 R2 finding 逐条处置（2026-11-05）

- **基线**：被审对象 r2 head `3c40f7020`；r3 起点为 Lead 处置后的 main；r3 修复 commit `d8ed04e13`、r3 测试 commit `6c0ab6594`、r3 证据 commit `280bb7bd0`。
- **R2-01（P1，已修）page-scope Run 执行链**：`HandlerDependencies` 新增 `lineage_guard` 并由 `build_production_handlers`/`core_assembly` 注入与目标 catalog 同一个 guard；`handle_detect` 复用 region 前改为 `_lineage_visible_live_regions(page_id)`（guard 过滤 + `[providers.detect] lineage_hidden=N` 诊断），**全 hidden 时在 new image 上执行检测**，新 region 由 `region_creator` 以 native lineage 写入当前 binding。`_backfill_detected_regions` 对 detect 输出在 commit 窗口内被隔离隐藏的 region 按「不可读跳过」处理（LINEAGE_* 码加入既有 skip 集，下一次 replan 只读可证集合）。page target 的 `lineage_hidden_regions` 计数进入 `TargetSnapshot.metadata`：当可见集为空且命令链不含 `ocr`（RERENDER_*/REINPAINT_*）时 planner 返回空 unit（task SKIPPED、run COMPLETED 的干净终态），**真正无 region 的页面保持 TASK-040 clean-probe 既有规划语义不变**。判别性测试：cut 页 + hidden region + stub detector 跑 `REOCR_ALL` → hidden id 不在 detect 输出、新图检出 2 个 region、OCR 跑通、run COMPLETED、hidden 无新 revision/lineage；`RERENDER_ALL` → COMPLETED + task SKIPPED + 零 step。
- **R2-02（P2，已修）candidate 提交 typed 投影**：`commit_step` 新增 `except PipelineError` 分支，`LINEAGE_*` 码路由到既有 `input_revision_changed` 冲突投影（prepared token 按既有语义 abandoned、结果 payload 保留为 reason=`INPUT_REVISION_CHANGED` 的候选行且非 abandoned、零业务写），不再是 DB_FAILED；其他 PipelineError 仍按原 DB_FAILED 语义。判别性测试：prepare OCR candidate → changed 切换 → commit，断言 `outcome.status=candidate`、`error_code=INPUT_REVISION_CHANGED`、detail 含 `LINEAGE_BINDING_CHANGED`、无新 revision/lineage、候选行保留。
- **R2-03（P2，已修）4 个判别性测试**：(a) draft apply 在 cut binding 上 `DraftError(code=LINEAGE_BINDING_CHANGED)` + 零写；(b) reorder/merge 写入侧拒绝（`LineageBindingChanged`，零 revision/lineage/新 region）；(c) backfill 失败不阻断装配（monkeypatch 抛错 → `assemble_core_services` 成功、guard 接线仍在、stderr 有 `legacy lineage backfill failed` 告警）；(d) page render 的 skip reports（`skip_reason=LINEAGE_BINDING_CHANGED`、status=skipped）与 `handle_rerender_page` 的 LINEAGE 映射（`RenderCommandError` code/category）。
- **R2-04（P2，已由 Lead 处置于卡文本）**：`doc/TASK_LEDGER.md` 由 Lead 维护、不计入 allowed_paths；本卡 r2/r3 commit 均未再改该文件。
- **R2-05（P3，已修）region 归属校验**：`RevisionLineageStanding` 增加 `region_id`（facts 查询同取），`_code_for` 在 `standing.region_id != region_id` 时按 `LINEAGE_UNVERIFIED` 拒绝（损坏数据防御）；测试构造 FK 合法但归属错误的 lineage 行（binding 经 same_content 可达，仅归属检查能否决）并断言 typed 拒绝。
- **R2-06/R2-07/R2-08（P3）登记为已知限制/集成限制**（见下 limitation 修订），本轮不扩大范围；**R2-09** 证据卫生：gates-r3.log 已补 shell/解释器/sqlite/venv/OS 头与 worktree 快照，EV-0/EV-1/EV-2 补 sha256 或 commit pin；`delivery_head`/`canonical_evidence_status` 按集成生命周期由 Lead closeout 填写。
- **r3 门禁**：fea11 69 passed（基线 62，+7）；全量 pytest 3093 passed / 10 skipped（基线 3073/10；差额含其他 Agent 并发新增测试）；check.ps1 PASS（默认与 `-TaskPath` 本卡均 PASS）；verify_pins 18/18 PASS；本卡 r3 commit 范围内冻结契约/FEA-09/apps 零 diff（gates-r3.log gate 7）；未 push。全量 pytest 后已恢复 tracked `verification/FEA-09` 原字节。

## 读路径行为矩阵（r2/r3 证据摘要；完整矩阵见 gates-r2.log gate 2 / gates-r3.log gate 2）

库形态（升级后的真实混合库）：

| 页面形态 | 守卫 | ListRegions/文本读 | 编辑写入 | 单 region rerender | Run | 说明 |
|---|---|---|---|---|---|---|
| managed 页（无 binding） | 跳过 | 全部可见 | 允许（无 lineage） | 放行（进入原渲染路径） | 允许 | 保持预 LINEAGE-1 行为 |
| referenced 页从未同步切换 | 跳过 | 全部可见 | 允许，登记 native(当前唯一 binding) | 放行 | 允许 | P0 回归保护；不因缺 lineage 拒绝 |
| 同步页 changed 切断 | 启用 | 过滤旧 region（计数可见） | 拒绝 `LINEAGE_BINDING_CHANGED` | `BLOCKED` 同 code | region-scope 拒绝同 code；page-scope 过滤，执行链 detect 只复用可见集合、全 hidden 时在**测试装配 stub 图源**上检测（R2-01；真实 referenced 图源受既有 managed-original 门槛限制，见 L10） | 旧坐标对新图不可见 |
| 同步页 same_content（可多跳） | 启用 | 可见（沿等价边） | 允许，新 revision native 当前 binding | 放行 | 允许 | 坐标等价，C-17 §7.1 允许 |
| 同步页缺 lineage 行 / `legacy_unverified` | 启用 | 过滤（计数可见） | 拒绝 `LINEAGE_UNVERIFIED` | `BLOCKED` 同 code | region-scope 拒绝同 code | 不可验证即 fail-closed |
| 同步页全 hidden + page-scope RERENDER_*/REINPAINT_* | 启用 | 过滤 | n/a | n/a | planner 干净终态（task SKIPPED、run COMPLETED，R2-01） | 无页级 unit → 不会 DB_FAILED/INVALID_INPUT |

错误码投影（旧命令面，非 C-17 §8 重映射）：`LINEAGE_BINDING_CHANGED` / `LINEAGE_UNVERIFIED` → `category=conflict`、`retryable=false`、固定安全文本；实际会抛 lineage 错误的命令映射：`list_regions`/`list_page_region_texts`（过滤面，显式 region_ids 命中 hidden → `TARGET_NOT_FOUND` + stderr 计数）/`set_region_type`/`restore_region_revision`/`_REGION_WRITE_COMMANDS` 的 dispatch 统一经 `_lineage_error_envelope`；`rerender_page` 经 `RenderCommandError`；Run 命令经 `_dispatch_run_command` 的 `PipelineError` 映射（candidate 提交窗口路由既有 `INPUT_REVISION_CHANGED`）；`drafts_apply` 经 `_DRAFT_ERROR_CATEGORY`；export 文本面为过滤（不产生错误码，有计数日志）。`list_region_revisions` 不读取 lineage、不会抛 lineage 错误（r2 Review P3 指出的表述过宽已更正）。

## Acceptance Criteria

- [x] **AC1**：region/draft 写路径同事务登记 native lineage（C-17 §7.1）；B1/R1→B2、same_content 边、changed 切断有测试。 <<MET>>
- [x] **AC2**：ListRegions/渲染/导出/Run/编辑入口的 lineage 读守卫（region 当前 revision 的 binding 必须等于当前 binding，否则 typed 拒绝；same_content 等价边放行；过滤结果带诊断计数）。 <<MET>>
- [x] **AC3**：AC11-5 隔离证据（旧坐标对新图不可见）与回归测试。 <<MET>>

## limitation 修订（r2/r3）

- **L1（导出/Run/ListRegions/单区域渲染守卫）**：**执行链守卫已闭环（r3 Review 限定口径）**——r2 实现 ListRegions/文本读过滤、export 文本面过滤、单 region rerender typed `BLOCKED`、page render 过滤+reports、Run region-scope 守卫；r3 修复 page-scope Run 执行链（R2-01）：detect 复用只取 lineage 可见集合、全 hidden 在**测试装配的 stub 图源**上执行检测、全 hidden 的 render/inpaint page 步骤为干净终态、candidate 提交窗口 typed 投影为既有 conflict。**不得**表述为「真实 referenced 图源已闭环」：provider 图像源仍是 Managed Copy original（`core_assembly.py:351-428`），纯 referenced 同步页在 `_page_or_error` 即被既有 `managed_original_ref` 门槛拒绝（`pipeline.py:1433-1434`）；该缺口见 L10。
- **L2（AC11-5 集成测试）**：**已闭环**——真实 SQLite 仓储 + 装配级集成测试覆盖 native 写入→changed 拒绝 / same_content 放行（多跳）/ 无 lineage typed 诊断 / 回滚无孤儿行 / draft/Run/restore/批量登记；r3 补 page-scope Run 执行链判别性测试。
- **L3（same_content 读边）**：**已闭环**——`SourceSyncLineageFacts.same_content_reachable` 沿 `publication.previous` 只经 `same_content` 边多跳；changed/repoint/missing 切断，测试覆盖。
- **L4（已知限制，r3 登记，R2-06）**：mixed 页（visible + hidden 并存）的 `reorder_regions` 仍要求 `ordered_region_ids` 等于**全部** live id（含 hidden），UI 不可见 hidden id 时无法重排；`create_region` 的 page cap 也计入 hidden；`list_page_region_texts` 显式 region_ids 命中 hidden 时返回 `TARGET_NOT_FOUND`（与未知/已删不可区分，stderr 有计数）。均非数据安全问题，建议后续卡把 reorder/merge 校验改到可见集合或返回显式 typed 诊断码。
- **L5（已知限制，r3 登记，R2-07）**：`SqliteTargetCatalog.freeze_context` 仍直接读相邻页全部 region 的 `ocr_text` 作为翻译上下文，未过 lineage guard；仅文本上下文、无坐标产物、不构成 AC11-5 坐标泄漏。建议后续卡按 guard 过滤 context 页或由 DSH 明确 context 不属于「当前区域读」。
- **L6（集成限制，r3 登记，R2-08）**：Host（`apps/desktop-avalonia/.../HostCommandRegistry.cs` 的 `AllowedRunErrorCodes`）未注册 `LINEAGE_BINDING_CHANGED`/`LINEAGE_UNVERIFIED`，桌面端会把新码投影为 `category=unknown` + generic message（仍 fail-closed、不崩溃），Core 侧 typed 已产生。`apps/**` 不在本卡 allowed_paths；建议后续 Host 窄批登记两码并补 .NET 投影测试（本卡未跑 .NET，见门禁说明）。
- **L7（残余，r2 保留）**：reader 投影（`handle_get_reader_projection`）只消费 translated artifact，不读 region 坐标；旧渲染 artifact 的 stale 判定沿用 FEA-11 既有 `rendered_from_revision_id`/`current_source_revision_id` 逻辑，未纳入本卡范围。
- **L8（裁决依据，不是限制）**：非同步页（managed 页 / 从未切换的 referenced 页）缺 lineage 不拒绝，是 DSH r2 裁决 ① 按 C-17 §7.1「本卡涉及的同步页」字面范围的结果；同步页内仍严格 fail-closed。判别证据：`test_mixed_library_scope_matrix_is_diagnosable`（gates-r3.log gate 2）。
- **L9（分层说明）**：`run_source_guard`（lease/gate）与 lineage guard 是两层独立守卫；本卡只新增 lineage 层。
- **L10（集成限制，r3 Review R3-01 登记）**：page-scope Run 的「全 hidden → 在**新图**检测」只在测试装配的 stub 图源成立，**不是**真实 referenced 图源闭环：①纯 AD-003 referenced 同步页（`managed_original_ref IS NULL`）在既有 `_page_or_error` 门槛即被拒绝（`pipeline.py:1433-1434`，TARGET_NOT_FOUND「page has no managed original」）——这是既有门槛，非 r3 引入；②provider 图像源 `_ManagedPageImageSource` 读取 Managed Copy original（`core_assembly.py:351-428`），不是当前 binding 的 C-17 §7.2 rendition；③r3 判别测试页是「referenced + managed_original 非空」的混合构造，`_StubImages` 未验证图像内容。**风险**：若混合页的 managed original 与当前 binding 图像不同，detect 输出坐标可能以 native lineage 记到新 binding（旧坐标 native 化）；当前真实 referenced 路径被既有门槛挡住，未证实为生产泄漏。**后续**：接 C-17 §7.2 rendition 图源后，需用真实新图与旧 managed original 不同的页断言 detect 输入来自当前 binding，否则禁止写 native；并补「纯 referenced 页 TARGET_NOT_FOUND」边界测试。
- **L11（行为说明/后续增强，r3 Review P3 登记）**：①`lineage_hidden_regions` 进入 page target metadata 后会影响 prepared-snapshot digest，已 prepared 的 Run 可能一次性得到 `RUN_STALE_PREVIEW`（安全、可重预览；后续可考虑把计数从 digest 输入中剥离）；②`_backfill_detected_regions` 对 `LINEAGE_*` 码按「不可读跳过」处理（当前无 stderr 计数），建议后续补诊断计数以便观测。

## Canonical Evidence

| evidence_id | 内容 | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-0 | r1 门禁日志（r1 head 的 fea11 49/native 9/9/全量 3060/0/10/.NET 见日志；保留原字节） | verification/FEA-11-LINEAGE-1/logs/gates.log | acd3f2263 | e4861691e820aaf37e8ca6bba9c18a8548ae76d065112ec555ba2f076abdabf9 | CANONICAL |
| EV-1 | r2 门禁日志（fea11/全量 pytest/check/pins/grep/诊断矩阵，含命令/EXIT/head） | verification/FEA-11-LINEAGE-1/logs/gates-r2.log | 791cfef28 | a2b2aa86d2290890ba8f9ad25bdf36e07483d67202569250c9f79480cb95dfff | CANONICAL |
| EV-2 | r3 门禁日志（fea11 69/全量 3093/10/check/pins/R2-01/R2-02 判别性输出、shell 头、冻结契约零 diff、worktree 快照） | verification/FEA-11-LINEAGE-1/logs/gates-r3.log | 280bb7bd0 | 729ed81edf28f5f618146c7e8517bafcd8b8b56c84ac870b097cd8dd2fa5d4ad | CANONICAL |
| EV-3 | r4 独立复核（approved P0/P1/P2=0；R3 处置核销；独立复跑 fea11 69/check/pins） | doc/reviews/FEA-11-LINEAGE-1-r4.md | - | d73d4358689d717e6716f4f03feaee9d94c112cda2782e925303706d42b3a5f3 | CANONICAL |

## r2 / r3 就绪声明

- r2 返修范围（r1 P0-1 写入覆盖 + 存量 backfill、P1-1 same_content 读边、P1-2 typed/入口覆盖、P1-5 真实仓储/装配测试、P2 快速项）已全部实现并有实体证据；r3 后 AC1/AC2/AC3 均为 MET。
- **r2 Review 结果**：changes_requested（P1=1/P2=3/P3=5；AC1/AC3 MET，AC2 改判 PARTIAL）。
- **r3 处置声明（2026-11-05）**：R2-01（P1）、R2-02、R2-03 的 4 个判别性测试、R2-05 已在 commit `d8ed04e13`/`6c0ab6594` 修复并有真实 SQLite/装配级证据；R2-04 由 Lead 处置于卡文本；R2-06/R2-07/R2-08/R2-09 按处置计划登记为已知限制/集成限制/closeout 项（见 limitation 修订）；AC2 恢复 MET。
- **r3 门禁（Python-only，head `6c0ab6594`；日志 EV-2）**：`pytest tests/fea11` 69 passed；`pytest tests` 3093 passed / 10 skipped；`check.ps1`（默认与本卡 `-TaskPath`）PASS；`verify_pins.ps1` 18/18 PASS；本卡 r3 commit 范围冻结契约/FEA-09/apps 零 diff；未 push；全量 pytest 后已恢复 tracked `verification/FEA-09` 原字节。
- **r3 复审就绪**：请 Lead 指派独立上下文 fresh subagent 做 r3 Review（被审 head：r3 修复 `d8ed04e13` + 测试 `6c0ab6594` + 证据 `280bb7bd0` + 本卡 commit；重点：R2-01 执行链/空集终态、R2-02 candidate 投影语义与「结果留 candidate」判定、R2-03 四测试判别力、R2-05 归属校验、L4-L7 已知限制登记是否充分）。
- 本实现者**不自审**；`delivery_head`/`canonical_evidence_status` 按集成生命周期由 Lead closeout 填写。
- 门禁（Python-only，**r2 时点历史数字**）：`pytest tests/fea11` 62 passed；`pytest tests` 3073 passed / 10 skipped（基线 3060/10）；`check.ps1` PASS；`verify_pins.ps1` 18/18 PASS；冻结契约零 diff；未 push。
- **r3 Review 结果**：changes_requested（P0=0/P1=0/P2=1/P3=4；代码/测试层 R2-01/R2-02/R2-03/R2-05 均核销，R2-02 语义获 approve；唯一 P2 = R3-01 卡面 L1/矩阵过度声明；AC1/AC3 MET、AC2 按原文 MET）。
- **r4 Review 结果（2026-11-05）**：**approved（P0/P1/P2=0，P3=1 cosmetic）**；R3-01/R3-02/R3-03/R3-05 核销，R3-04 仅剩一处 cosmetic（本卡 line 155 r2 门禁数字已标注为历史、line 169 重复自审句已删除）。报告 `doc/reviews/FEA-11-LINEAGE-1-r4.md`（session `dde30402-06b5-43e7-ae1d-374408e55823`）；独立复跑 fea11 69、check PASS、pins 18/18、`90a8c8218..f11bff37e` src/tests/apps 零 diff。

## r3 Review 处置（Lead，2026-11-05；findings disposition）

> 依据：`doc/reviews/FEA-11-LINEAGE-1-r3.md`（fresh subagent session `49d520be-0862-41b2-87f0-0ec35dc28b3d`；reviewed_head `90a8c8218`）。本轮**无代码/测试返修**（Reviewer 明确非代码阻断），仅卡面与限制登记修正；完成后派 fresh subagent r4 复核。

- **R3-01（P2，已处置）**：L1 改为「执行链守卫已闭环（限定口径）」；新增 **L10** 记录真实 referenced 图源缺口（`pipeline.py:1433-1434` 既有门槛、`core_assembly.py:351-428` Managed Copy 图源、混合页旧图坐标潜在风险、后续接 C-17 §7.2 rendition 的判别测试要求）；行为矩阵「全 hidden 时在新图检测」改为「测试装配 stub 图源」。**裁决**：本轮接受该缺口为**已知集成限制**（真实 referenced 页 page-scope Run 属后续卡），不得据此宣称 AD-003 referenced 页已支持；如用户要求本轮闭环，需另开卡接 rendition 图源。
- **R3-02（P3，已登记 L11①）**：`lineage_hidden_regions` 进入 `TargetSnapshot.metadata` → prepared digest，旧 prepared run 一次性 `RUN_STALE_PREVIEW`（安全、可重预览）；后续可把计数从 digest 输入剥离。
- **R3-03（P3，已登记 L11②）**：`_backfill_detected_regions` 对 `LINEAGE_*` 静默 skip；建议后续补 stderr 计数（本轮不改代码，登记增强）。
- **R3-04（P3，已修）**：`tests/fea11/test_source_lineage_run.py` 已补进 frontmatter allowed_paths；删除本卡尾部残留的 r2 门禁/自审段落；历史行号引用以 r3 Report/本卡滚动内容为准。
- **R3-05（P3，已记录）**：gates-r3.log gate1 缺 `-p no:cacheprovider`（复跑一致性瑕疵，不影响结果）；check 警告数差异属并发文档环境，closeout 记录实测值。
- **r4 复核范围**：只确认 ①L1/L10/矩阵修正是否消除过度声明；②R3-02/03 已登记为 L11；③R3-04/R3-05 处置；④AC 标记与 limitation 一致；不重跑全量（引用 r3 独立复跑 69/3093/10 + check/pins），但需复核工作树/commit 范围与冻结零 diff。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树实施） | NOT_APPLICABLE | — | — | 无 worktree 创建/删除/prune |
| artifact/temp/agent-output/dataset | NOT_APPLICABLE（实现与证据均在仓库内；pytest 使用 `:memory:`/`tmp_path`） | NOT_APPLICABLE | — | — | 无本任务专属仓外资源；pytest 缓存已用 `-p no:cacheprovider` 规避 |
| evidence | verification/FEA-11-LINEAGE-1/logs/gates.log、gates-r2.log、gates-r3.log | PRESERVE_REFERENCED | verification/FEA-11-LINEAGE-1/logs | verification/FEA-11-LINEAGE-1/logs/gates-r3.log | 当前 Task/Review 引用；原位保留不清理 |
| 代码/测试 | src/application/{editing,sources,rendering,export}/**、src/infrastructure/sqlite/**、src/infrastructure/providers/handlers.py、src/application/tasks/service.py、src/bootstrap/{core_assembly,core_service}.py、tests/fea11/** | PRESERVE_REFERENCED | src | verification/FEA-11-LINEAGE-1/logs/gates-r3.log | 已集成 main（delivery `90a8c8218`）；不回滚；行级证据见 EV-2 |

## Closeout Record

- Closeout date / DSH：2026-11-05 / DSH（Lead/Architect/Integrator）。
- 终态：`done`；integration_commit / delivery_head = `90a8c8218`（main 线性集成，无 merge commit）。
- Review 链：r1 changes_requested（P0=1）→ r2 changes_requested（P1=1）→ r3 changes_requested（P2=1，仅卡面过度声明）→ **r4 approved（P0/P1/P2=0，P3=1 cosmetic）**；所有 Reviewer 均为独立上下文 fresh subagent，session 见 frontmatter/各报告。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- AC 定稿：AC1 MET、AC2 MET（按原文口径；限定由 L1/L10 承接）、AC3 MET。
- 未完成/保留项（limitation）：L1（执行链守卫已闭环，限定口径）、L2/L3（闭环）、L4/L5（mixed 页 reorder/text 诊断、freeze_context 过滤；后续卡）、L6（Host `AllowedRunErrorCodes` 未含 LINEAGE_*；apps/** 后续 Host 窄批）、L7（reader 投影未纳入；后续卡）、L8（非同步页 fail-open 为 DSH 裁决）、L9（分层说明）、**L10（真实 AD-003 referenced 图源缺口：纯 referenced 页被既有 managed-original 门槛拒绝；detect 图源为 Managed Copy original 而非 C-17 §7.2 rendition；混合页旧图坐标潜在风险）**、L11（prepared-snapshot digest 一次性 `RUN_STALE_PREVIEW`、`_backfill_detected_regions` 静默 skip 待补计数）。
- 残余 P3（cosmetic，已处置）：r4 指出的 r2 门禁数字已标注历史、重复自审句已删除；gates-r3 gate1 缺 `-p no:cacheprovider` 属记录瑕疵，不影响结果。
- 删除、迁移、归档数量/字节数：0。
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新；本卡为终态，不进入 READY DAG；**LINEAGE-1 完成后，FEA-11 r7-acceptance 的「LINEAGE-1 完成前禁止消费同步 binding」硬约束解除**（以本卡 done 为条件）。
- 后续：真实 referenced 图源（C-17 §7.2 rendition）接入、Host 窄批 LIMIT 登记、mixed 页诊断、context 过滤等仅在**新授权**下另开卡。
