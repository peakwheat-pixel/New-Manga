---
id: TASK-032
title: 修复 SFX Policy Gate 缺失 region_type 前置（F-1）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-011, TASK-019]
base_commit: ca17d454edc03bc1b057e9e3fc463c81da652e53
branch: agent/deepseek/TASK-032-sfx-policy-gate-region-type
worktree: G:/CODEX/New Manga.worktrees/TASK-032-deepseek
integration_commit: null
---

# TASK-032：修复 SFX Policy Gate 缺失 region_type 前置（F-1）

**READY（2026-09-17 用户批准释放；同日按用户指示改派 Owner）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**——Owner 改为 DSH 后，若仍由 DSH 审会构成同体审查，故一并更换）；base=`ca17d45`（释放时的 master HEAD，已与实际代码核对：`src/application/tasks/service.py:353-361` 的缺陷仍在，`sfx_policy` 判断未检查 `region_type`）；branch/worktree 见顶部元数据（已按 `agent/deepseek/...` 命名重建并同步；首次按 `agent/zcode/...` 创建且**无任何提交**的 worktree/分支已移除）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

**Codex 已完成意图裁决：本 Task 修的是缺陷、不是产品取舍**——依据 D06 §85「SFX Policy Gate」的前置 `region_type = sfx` 与 D08 AC-SFX-001（`region_type = sfx` 且未额外配置 → `SKIP_POLICY` / `reason = sfx_skip`）；D03 §7 的默认 `skip` **对 SFX 类型是正确的**，问题在策略泄漏到非 SFX 类型。因此**不需要产品决策**。

**Review 口径**：本 Task 的独立 Review 必须按[协作协议](../09_COLLABORATION.md) §6 的**四轴**执行——**Standards**（`code-review` 技能两轴之一，强制；含 Fowler smell baseline 作为判断项）/ **Spec**（两轴之二）/ Architecture / Verification，并逐轴声明 `executed`/`N/A`、每轴一行小结、**不跨轴排名**；两轴应优先由**独立执行者/线程并行**执行（模板见 [Review 模板](../templates/REVIEW.md)）。

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

Codex 已按 base `ca17d45` 的实际结构核对：三个代码/测试允许路径（`src/application/tasks/service.py`、`src/infrastructure/sqlite/pipeline.py`、`tests/pipeline/**`）均存在。超出范围（Schema/migration、D03/D08 文本、`src/ui/**`、`src/domain/**`、其他 Task）先由 Codex 明确范围变更。本 Task **预计不需要 Schema 变更**（`skip` 默认本身正确）。

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

- Handoff：尚无。Review：尚无。实际执行/测试：尚无。
- **最近状态（当前，唯一）**：2026-09-17 用户批准**释放**，并随后**改派 Owner 为 `DeepSeek Harness`**——`status=ready`、`approval=approved_by_user`、Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`ca17d45`、branch=`agent/deepseek/TASK-032-sfx-policy-gate-region-type`、worktree=`G:/CODEX/New Manga.worktrees/TASK-032-deepseek`（已创建并同步到改派提交）。依赖 TASK-011/TASK-019 均 `done`；Codex 已核对缺陷仍存在于 `src/application/tasks/service.py:353-361`。**实施尚未开始**：实际执行仍为 `NOT_RUN`，Owner 开始前须把 `status` 改为 `in_progress`。
- 历史状态（2026-09-17）：由 Codex 依据 TASK-019 的 F-1 登记创建为 `proposed`；当日获用户批准释放为 `ready`（首版 Owner=`ZCode`、Reviewer=`DeepSeek Harness`，分支 `agent/zcode/TASK-032-sfx-policy-gate-region-type`，**无任何提交**），随后按用户指示改派 Owner 并重建分支/worktree，见上。
