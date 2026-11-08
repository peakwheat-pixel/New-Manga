---
id: FEA-11-RESIDUAL-4A
title: FEA-11 收口（AC11-7 诊断出口 / AC11-9 Host 级生产链路 / AC11-6 folder 用例 / L-M4 裁决 / AC 回填）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-08 残余收口指令（R3）；独立 scope review `doc/reviews/FEA-11-RESIDUAL-4A-scope-r1.md`（session `88de37b5-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §5 改写后冻结）；DSH 2026-11-08 裁决（ADJ §7.7）：0 pin、窄口径 done（L-M1/L-M4 具名 re-home）
suggested_owner: dsh
owner: fea11-residual4a-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；r1 于实现交付后指派）
depends_on:
  - FEA-11
base_commit: c5bd49276
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RESIDUAL-4A
allowed_paths:
  - doc/tasks/FEA-11-RESIDUAL-4A.md
  - doc/tasks/FEA-11.md
  - doc/reviews/FEA-11-RESIDUAL-4A-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-11-RESIDUAL-4A-*.md
  - verification/FEA-11-RESIDUAL-4A/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - tests/fea11/test_source_relink.py
  - tests/fea11/test_source_sync.py
  - tests/fea11/conftest.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Residual4AIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/HostFixture.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - src/infrastructure/sqlite/source_sync.py
out_of_scope:
  - 冻结契约字节：`doc/plan/**`、`doc/contracts/**`、18 pins（**L-M4 需 C-17 UNFREEZE → 本卡只 re-home，不实现**）
  - `IHostController.cs`（加方法即改 C-07 pin → 1 pin，0 pin 不允许）、`src/bootstrap/**`（除死 seam 处置经 DSH 预批外）
  - Core 语义修改：`needs_confirmation` 写入者修复（本卡只登记缺陷并 re-home `FEA-11-DIAG-SURFACE-1`）；folder 身份键修复（只登记 `L-S4-2`）；PDF raster seam（L-M1 re-home）
  - 崩溃点矩阵（已 re-home `FEA-11-HOST-AUTH-3`）；UI 用户流程；真实用户数据/AppData/回收站；push；新依赖
---

# FEA-11-RESIDUAL-4A：FEA-11 收口（0 pin）

> **状态 `ready`**（base `c5bd49276`；0 pin）。目标：把 `FEA-11`（`closed_with_limitations`）翻 `done`，方式 = **5 条 AC 回填 + 4 条 AC 补做（其中 2 条按裁决 re-home 子项）**。
> **术语/口径**：
> - `[x] <<MET>>` **不得带原因**（`check.ps1:838-845`）；limitation 只能写 closeout/ADJ。
> - **L-STARTUP**（AC11-1 子项）→ `NOT_APPLICABLE: 契约解释+产品范围（AD4-003 §3.6 / C-01b SC-25 四项组合不含启动全量扫描；保留 NOT_RUN）`。
> - **L-M1（PDF 插页）/ L-M4（旧证据重算）→ BLOCKED 具名 re-home**（`FEA-11-MATCH-1` 承接卡后另立：L-M1 → `FEA-11-PDF-RECONCILE-1`；L-M4 → `FEA-11-LEGACY-RECOMPUTE-1`，需 C-17 UNFREEZE）。

## 缺陷/缺口（base `c5bd49276`，scope review 已核）

- AC11-1/3/4/5/8：已有承接卡/证据，**卡面 AC 行未回填**（append-only 补登）。
- AC11-6：folder relink typed 拒绝**无测试**；成员重排/多项目**无用例**；folder repoint/resync 逃生路径**无证据**。
- AC11-7：无 binding-status 查询面；`needs_confirmation` **零生产者**（`source_sync.py:885-911`、`library.py:2461-2471` 调用点全 `healthy`）；Core 死 seam `source_sync.py:1030-1047` 零调用者；`defer` 不改状态 ⇒ 与 C-17:273 不符（缺陷）。
- AC11-9：现有 gated 用例 **Core 直连**、未走 HostRuntime/dispatcher、sync 前未 resolve 旧绑定。
- AC11-10：证据/manifest 停旧 head；最终 head 无 approved Review。
- 治理：`doc/STATUS.md:8` 与 `doc/REBASELINE_PLAN.md:53` 仍写 HOST-AUTH-1 `closed_with_limitations`（实际已 done）。

## Acceptance Criteria（冻结）

- [ ] **AC-R3-1（AC11-7 诊断出口）**：Host 只读投影从 durable journal/receipt 读 `bindings[].status ∈ {missing,needs_confirmation}`，**不新增 Core 命令/能力/wire 字段、不改 `IHostController`**；断言「不扩 V(p,t)」（缺失页在 reader/`list_chapter_pages` 仍不可见）；Core 死 seam `tombstone_pages_of_source` **接线或删除**二选一并记录；`needs_confirmation` 零生产者作为具名缺陷登记（→ `FEA-11-DIAG-SURFACE-1`，需 C-17 additive）。 <<MET>>
- [ ] **AC-R3-2（AC11-9 Host 级生产链路）**：gated（`NEWMANGA_FEA11_IPC=1`）经 `Fea09ProductionFixture` launcher + `HostRuntime/Commands.InvokeAsync` 生产 dispatcher 完成 scan→plan→preview→confirm→apply→ACK→resolve；**sync 前**读出旧绑定字节（记录 resource id + sha256），**ACK 后**断言新键/新字节 + 旧资源键/摘要不可变；源 hash/mtime/文件数守恒、应用零写源；缺能力/撤销 fail-closed；默认 skip 且逐条记原因。 <<MET>>
- [ ] **AC-R3-3（AC11-6）**：folder relink **typed 拒绝**判别用例 + folder **resync 成功**用例 + **SC-S11 成员重排保序** + **多项目不误改**；`L-S4-2` 以缺陷登记（`runtime.py:986-991` vs C-15:216 逐项）；**不改 Core 语义**。 <<MET>>
- [ ] **AC-R3-4（L-M4 裁决）**：书面裁决（实现须写 pin 与 UNFREEZE → 明确不做）；re-home `FEA-11-LEGACY-RECOMPUTE-1`（含 reopen 条件：C-17 UNFREEZE + 新 capability）；**不得**出现「已按冻结参数重算旧证据」表述。 <<MET>>
- [ ] **AC-R3-5（回填与翻转）**：AC11-1/3/4/5/8 逐条 before/after 登记（append-only，不改历史 Review/证据字节）；`[x] <<MET>>` 不带原因；L-STARTUP 子项 NA；L-M1/L-M4 具名 re-home；`check.ps1` PASS 且 `done` 无 `<<PARTIAL>>/<<BLOCKED>>`。 <<MET>>
- [ ] **AC-R3-6（证据与治理）**：EV + Resource Manifest 在 R3 head 重生成；pins 18/18 保持（或显式登记变更）；修正 STATUS/PLAN 的 HOST-AUTH-1 陈旧表述；最终 head 取得独立 Review；全量 pytest ≥3390/10、.NET ≥1731/0/98 不降。 <<MET>>

## 实现口径

1. AC11-7 走 **Host journal 只读枚举**（`SourceOperationCoordinator` 加只读 list/lookup，不改 `IHostController`）；`needs_confirmation` 只登记不修（改写入者属 Core 语义 → `FEA-11-DIAG-SURFACE-1`）。
2. AC11-9 复用 `Fea09ProductionFixture` 的 launcher 手法（**仓库无 `Fea11ProductionFixture`**），不碰 bundled sidecar；断言用既有 `RunPythonAsync` 查库，.NET 测试不直连 SQLite。
3. AC11-6 仅补测试 + 登记；**不改** `service.py` 拒绝分支、不改身份模型。
4. L-M4/L-M1 只登记 re-home；不得改契约字节。
5. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。

## 行文口径（红线）

- 不得写「FEA-11 全部 limitation 关闭 / C-17 §3.3 完全实现 / RH-3 已清理」；只写「AC11-1/3/4/5/8 回填；AC11-6/7/9 达成；L-STARTUP 子项 NA；L-M1/L-M4 re-home」。
- 崩溃点 `NOT_RUN`、原生/真机 `NOT_RUN` 不得写成 PASS。
