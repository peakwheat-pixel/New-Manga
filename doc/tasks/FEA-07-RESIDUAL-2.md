---
id: FEA-07-RESIDUAL-2
title: FEA-07 收口 A（AC2 窗口层 draft owner + 生命周期断言 / AC6 指标与规模负载 / AC8 证据）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-08 残余收口指令（R4）；独立 scope review `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md`（session `23a6e437-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §5 拆分与口径修正后冻结）；DSH 2026-11-08 裁决（ADJ §7.10）：0 pin、headless-only
suggested_owner: dsh
owner: fea07-residual2-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审）
depends_on:
  - FEA-07
base_commit: 0a39a78f0
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-2.md
  - doc/tasks/FEA-07.md
  - doc/reviews/FEA-07-RESIDUAL-2-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-07-RESIDUAL-2-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/**
  - apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - verification/FEA-07-RESIDUAL-2/**
out_of_scope:
  - 原生 IME、AC5 双屏/拔屏/DPI 矩阵、真实双屏 broker 落位（`NOT_APPLICABLE: 原生交互未执行（保留 NOT_RUN）+ 用户 2026-11-08 授权豁免`）
  - 冻结契约字节：`doc/plan/**`、`doc/contracts/**`、18 pins（只**引用** C-13 SC-D03，**不复述**规则）
  - 不改 `AppearanceCoordinator`/`FrontendSelector`/组合根语义；不改 `NewManga.DesignSystem/**`、`NewManga.Appearance/**`；不改 `Switching/**` 事务逻辑
  - R4b 面（AC1 A03/ACK、AC3 跨进程崩溃、AC4 真实入口）→ `FEA-07-RESIDUAL-3`
  - 真实用户数据/AppData/外部卷/回收站；L3/L4 真机（NOT_RUN）
---

# FEA-07-RESIDUAL-2：FEA-07 收口 A（headless，0 pin）

> **状态 `ready`**（base `0a39a78f0`；0 pin；headless-only）。目标：完成 `FEA-07` AC2（窗口层 draft owner + 生命周期）、AC6（指标与规模负载）、AC8（证据）；AC1/AC3/AC4 由 `FEA-07-RESIDUAL-3`（R4b）承接，**两卡都 MET 后 FEA-07 才翻 done**。
> **AC2 冻结解释（DSH，scope review §2）**：「第二窗口」= **独立 OS 窗口**（`WindowBroker.WindowRole.Floating`）→ 只读或独立 Session；「同 Session 主画布 + 浮动面板」= **同一窗口内浮动面板**→ 按 **C-13 SC-D03**（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66`）共享 DraftId 可编辑。owner 键 = `(SessionId, RegionId)`；跨 Session ReadOnly；转移显式。**只引用不复述 SC-D03。**

## Acceptance Criteria（冻结）

- [ ] **AC-R4a-1（AC2 窗口层 draft owner）**：新增 `(SessionId,RegionId)` 窗口层 owner registry（App/Presentation 层）：同一 key 跨 **OS 窗口** 只有一个 owner；第二个 `Floating` 窗口 claim 得 `ReadOnly`，其写入尝试被 typed 拒绝且 **Host 零写入**（`FakeHostController` 计数为 0）；同窗口内浮动面板共享同一 `DraftId`（**不得**拒绝，符合 SC-D03）；显式转移后 owner 互斥且幂等；`Release` 后可再 claim；并发 claim 只有一个 owner。 <<MET>>
- [ ] **AC-R4a-2（AC2 生命周期）**：窗口关闭/重建/切换前后 `FakeHostController.StartCalls`/`StartRequests`/`LifecycleLog` 逐项不变；`PresentationWindow` 不调用 `StartAsync`/`DisposeAsync`（计数 + 事件断言）；补窗口级判别测试。 <<MET>>
- [ ] **AC-R4a-3（AC6 指标与规模）**：热切换 p95 门槛 **1000 ms 不变**（W-5 冻结），断言改为 **3 次独立运行的 p95 中位数 ≤ 1000 ms**，记录每轮 p95/max；新增 **`uiThreadSchedulingGapMs`**（UI 线程心跳最大间隔）并首轮基线定标后写死阈值；**真实规模合成负载** N∈{50,200,500}（`FakeHostController.ReadySnapshot`），记录 p50/p95；冷启动单独记录不入门槛。 <<MET>>
- [ ] **AC-R4a-4（AC8 证据 + 治理）**：EV/Resource Manifest/门禁日志；`FEA-07` AC1/AC2/AC3/AC4/AC6/AC8 行 **append-only** before/after 登记（本卡先登记 AC2/AC6/AC8，R4b 完成后再登记 AC1/AC3/AC4）；AC5/AC1-IME/AC2-双屏三条 **NA 只写一次**（在 AC5 行）；`check.ps1` PASS、pins 18/18（0 pin）；pytest ≥3395/10、.NET ≥1733/0/102 不降。 <<MET>>

## 实现口径

1. 新增 `Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs`（线程安全、不可变结果）；`WindowBroker` 薄转发（`TryClaimDraft/ReleaseDraft/RequestDraftTransfer`），保持现有 API 不破。
2. `PresentationWindow` 暴露 `DraftOwnership`；`Floating` 窗口构造时强制 `CanEdit=false`（只读策略）。
3. **只引用** C-13 SC-D03（给行号），禁止复述规则句（双权威判例 `FEA-C10-r1.md:83`）。
4. AC6 指标：保留既有 p95 采集（4 预热 + 20 测量），改 3 次取中位；新增心跳指标与基线文件；不得改 1000 ms 门槛。
5. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。

## 行文口径（红线）

- 不得写「FEA-07 完全实现 / 全部 limitation 关闭 / 可发布」；只写「AC2/AC6/AC8 达成；AC1/AC3/AC4 由 R4b 承接；原生项 NA（NOT_RUN）」。
- `NOT_RUN` 不得写成 PASS；像素/UI 观感不得作为 AC 判据。
