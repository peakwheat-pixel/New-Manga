---
id: TASK-032
title: 修复 SFX Policy Gate 缺失 region_type 前置（F-1）
kind: bugfix
status: proposed
approval: pending_user_review
suggested_owner: ZCode
owner: null
reviewer: null
depends_on: [TASK-011, TASK-019]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-032：修复 SFX Policy Gate 缺失 region_type 前置（F-1）

**PROPOSED（未释放）**：本 Task 由 TASK-019 Review 发现的跨 Task P0 缺陷 **F-1** 转化而来，**需用户批准释放**；未释放前不得实施。**Codex 已完成意图裁决：这是缺陷，不是产品取舍**，因此不需要产品决策（依据见下）。

## 来源与目标

- 来源：[doc/reviews/TASK-019-726baf5.md](../reviews/TASK-019-726baf5.md) 的 R-5 / F-1；[doc/STATUS.md](../STATUS.md) 的 F-1 登记行。
- **规范依据（裁决基础）**：D06 §85「SFX Policy Gate」的前置明确写着 `region_type = sfx`；D08 AC-SFX-001 同样以 `region_type = sfx` 且未额外配置为前提，返回 `SKIP_POLICY` / `reason = sfx_skip`；D03 §7 定义 SFX 策略默认 `skip`——**对 SFX 类型而言该默认是正确的**。
- **缺陷**：`src/application/tasks/service.py:353-361` 在判断 `sfx_policy in {"skip","manual"}` 时**没有检查 `region_type`**，导致普通（`speech`/`narration`/`title`/`note`/`other`）Region 的 `translate`/`segment`/`mask_refine`/`inpaint`/`render` 也被判为 `SKIP_POLICY("sfx_skip")`。
- **影响**：按真实默认值（新建 Region 为 `speech`、`sfx_policy` 默认 `skip`），整条重翻译链在**规划阶段**即被跳过；`src/ui/**` 无任何写入 `sfx_policy` 的路径，用户无从纠正。
- **附带需统一的口径**：`src/infrastructure/sqlite/pipeline.py` 的快照默认与实体/Schema 默认不一致。缺字段时的解释必须唯一：**SFX 类型** 回落文档默认 `skip`；**非 SFX 类型** 该字段不参与判定。

## Acceptance Criteria

- [ ] 规划阶段仅当 `region_type == sfx` 时应用 SFX 策略：`skip`/`manual` → `SKIP_POLICY(reason="sfx_skip")`；`translate` → 按 AC-SFX-002 进入 Translation。
- [ ] 非 SFX 类型 Region 的 `sfx_policy` 取任意值都不影响 `translate/segment/mask_refine/inpaint/render` 的规划结果（用**真实默认值**构造用例，不用测试辅助的 `translate` 默认）。
- [ ] 缺字段口径唯一：SFX 类型回落 `skip`；非 SFX 类型不参与判定；`infrastructure/sqlite/pipeline.py` 的快照默认与实体/Schema 一致。
- [ ] 回归：`tests/pipeline` 新增"真实默认值"用例（新建 `speech` Region + 默认 `sfx_policy` → 各步骤不被 `SKIP_POLICY` 跳过）；既有 `sfx` 用例（`tests/pipeline/test_pipeline.py` 中 `region_type="sfx", sfx_policy="skip"`）行为不变。
- [ ] 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者**独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

- `src/application/tasks/service.py`
- `src/infrastructure/sqlite/pipeline.py`
- `tests/pipeline/**`
- `doc/tasks/TASK-032.md`、`doc/handoffs/TASK-032-*.md`、`verification/TASK-032/**`

超出范围（Schema/migration、D03/D08 文本、`src/ui/**`、`src/domain/**`、其他 Task）先由 Codex 明确范围变更。本 Task **预计不需要 Schema 变更**（`skip` 默认本身正确）。

## 禁止范围

- 不得修改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、生产数据、其他 Task。
- 不得在未获用户批准时改变 `sfx_policy` 的**默认值语义**（D03 §7 已定 `skip`）；若认为需要改变，先取得用户裁决。
- 不得放宽既有测试、删除既有断言或新增 skip 掩盖失败。
- 不得顺手修复 `tests/reading_export` 的 flaky（见 STATUS「已知 flaky 测试（跟踪条目）」；属测试基础设施，另行处理）。

## 测试要求

- 主套件：`python -m pytest tests/pipeline -q`，必须包含"真实默认值"用例与既有 `sfx` 类型用例。
- 回归：`python -m pytest tests/core tests/storage tests/providers -q` 与全仓 `python -m pytest -q`；记录中**分列 passed/skipped 与 skip 原因**。
- 实际记录包含 commit、OS/依赖、准确命令、退出码、结果与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)（planner 归属）、[TASK-019](TASK-019.md)（缺陷发现与 F-1 登记）——均已集成 `done`。

阻塞：**未获用户释放**（`status=proposed`、`approval=pending_user_review`）。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`proposed`，未释放）。
- 最近状态：2026-09-17 由 Codex 依据 TASK-019 的 F-1 登记创建为 `proposed`；释放需用户批准，释放时由 Codex 填写 owner/reviewer/base/branch/worktree。
