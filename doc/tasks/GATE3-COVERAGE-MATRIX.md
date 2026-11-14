---
id: GATE3-COVERAGE-MATRIX
title: Gate 条件 3 覆盖矩阵盘点（四页 × 关键流程，逐格代码依据）
kind: evidence
governance_version: 3
status: in_progress
disposition: "Gate 条件 3（完整 GUI/Core/Host 流程与 Avalonia TestHost）；把「部分」变为可判定证据"
approval: DSH 2026-11-15（纯盘点，零代码改动）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: d86f185ca
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GATE3-COVERAGE-MATRIX
allowed_paths:
  - doc/tasks/GATE3-COVERAGE-MATRIX.md
  - doc/reviews/GATE3-COVERAGE-MATRIX-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE3-COVERAGE-MATRIX/**
---

# GATE3-COVERAGE-MATRIX：Gate 条件 3 覆盖矩阵

## 来源与目标

Gate 条件 3 = "补齐**可安全执行的**完整 GUI / Core / Host 关键流程与 Avalonia TestHost；所有 blocked/skipped
项继续保留原结果"（`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md`）。当前评估把它记为 **部分**
（`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §2 第 3 行），但**没有任何清单**说明
"哪些流程有覆盖、哪些没有"。这让条件 3 无法被判定，也无法判断剩余工作量。

**一个可观察交付结果**：一份 `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`，
按「四页 × 关键流程」逐格给出 **有覆盖 / NOT_RUN**，每格都带代码依据（测试名 + `文件:行` + 该测试
**实际断言了什么**）；无法执行的原因写清（`[SidecarFact]`/E-2、无夹具、功能不存在、需真实窗口）。

## Acceptance Criteria

- [ ] **AC1 矩阵结构**：至少覆盖四页（书架 / 工作台 / 阅读器 / 设置）× 关键流程
      （进入与空态、错误态、只读、导入、导出、阅读进度、阅读偏好、书签、Region 编辑、
      主题/外观、快捷键、焦点与 a11y、Host 生命周期/恢复）。
- [ ] **AC2 逐格代码依据**：每格写 `测试名 (文件:行)` 并**说明该测试断言了什么**；
      不得仅凭测试方法名推断覆盖面。
- [ ] **AC3 可执行性标注**：明确区分 `[AvaloniaFact]`（headless 可跑）、`[Fact]`（纯逻辑）、
      `[SidecarFact]`/`[HostSidecarFact]`（需真实 sidecar → 本环境 E-2 阻塞）。
- [ ] **AC4 NOT_RUN 归因**：每个 NOT_RUN 格写具体原因（E-2 sidecar / 需真实窗口与人工操作 /
      功能未实现 / 无对应测试），不得留空或写"未覆盖"了事。
- [ ] **AC5 零改动**：不修改任何生产代码或既有测试；`git diff` 只含本文档与三指针。
- [ ] **AC6 结论诚实**：矩阵末尾给出**条件 3 的可判定结论**，明确哪些是"有覆盖且无夹具可跑"、
      哪些是"有覆盖但需 E-2"、哪些是"完全无覆盖"；**不得**把 NOT_RUN 汇总成"基本覆盖"。

## 允许修改范围

见 frontmatter。**只新增文档 + 三指针更新**，不碰代码。

## 禁止范围

- 不得修改 `src/**`、`apps/desktop-avalonia/tests/**`（既有测试）或任何 wire/契约。
- 不得把"有测试文件"等同于"该流程被验证"。
- 不得为了矩阵好看而合并不同流程；无法判定就写"无法判定 + 原因"。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 读测试源码逐个核对断言 | 仓库 | NOT_RUN | 无 |
| AC3/AC4 | 分类统计 `[AvaloniaFact]`/`[Fact]`/`[SidecarFact]` | 仓库 | NOT_RUN | 无 |
| AC5 | `git diff --stat` | 仓库根 | NOT_RUN | 无 |
| AC6 | 四件套 | 仓库根 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：矩阵容易变成"测试文件目录"的复述；必须强制"断言了什么"。
- **风险 R2**：某流程可能同时被 headless 与 sidecar 测试覆盖，需分别标注，不能取其一。
- **环境**：真实 sidecar 集成受 E-2 阻塞；本卡不试图绕过，只如实标注。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，且须复核"每格判定是否有代码依据"）。
- 实际测试：本卡为盘点，无新增测试。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 本卡无新增派生物 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待填。
- 当前指针清理：待关闭时更新 STATUS / Plan / TASK_LEDGER / rolling checkpoint。
