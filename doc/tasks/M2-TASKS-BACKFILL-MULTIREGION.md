---
id: M2-TASKS-BACKFILL-MULTIREGION
title: "executor backfill 多 region 页逐 region 跟进调度（SFX-ENTRY 相邻发现）"
kind: feature
status: ready
approval: user_ruling_2026-10-01_three_followups_all
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-TRANSLATE-ENTRY]
base_commit: f534c3e7
branch: agent/zcode/M2-TASKS-BACKFILL-MULTIREGION
worktree: G:/CODEX/New Manga.worktrees/M2-TASKS-BACKFILL-MULTIREGION-zcode
---

# M2-TASKS-BACKFILL-MULTIREGION：backfill 逐 region 跟进调度

## 背景（M2-SFX-TRANSLATE-ENTRY Owner 相邻发现，只登记未修）

`src/application/tasks/service.py:922` 附近的 executor backfill 只把页任务绑定**第一个**检出 region——多 region 页（生产常态：BJ02 5 region、BJ06 17 region）的后续 region 不被 backfill 跟进。影响面与正确语义（逐 region 跟进命令？页任务与 region 任务的绑定关系？）需先勘察后设计。

## 交付（AC）

1. **AC1 勘察先行**：backfill 语义全景（`service.py:922` 上下文、backfill 触发时机、页任务↔region 命令的现有绑定模型、多 region 页当前实际行为——是丢失跟进还是仅首 region）；**勘察结论决定修复语义**（逐 region 展开 / 1:N 绑定 / 其他），写进 handoff 后再落笔。
2. **AC2 实现**：按勘察结论的最小语义修复；不改命令协议与 DB schema（如确需 schema 变更则停，登记移交）。
3. **AC3 测试**（先红后绿）：多 region 页 backfill 行为的红绿；单 region 页零变化；边界（0 region 页、region 中途新增）。
4. **AC4 文档**：Task/Handoff 回填；发现相邻缺陷只登记。

## 允许修改面

`src/application/tasks/**`（backfill 相关）、`tests/`（tasks 相关）、`verification/M2-TASKS-BACKFILL-MULTIREGION/**`、Task/Handoff。

## 禁改面

`src/domain/**`（schema/实体零变更）、`src/infrastructure/sqlite/schema.py`、`src/ports/**`、`src/infrastructure/providers/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、其他 application 模块（勘察后确需则 handoff 登记移交）。

## 纪律

- 基线不回退：main 530+1skipped 0 failed；既有 backfill 行为（单 region 页）零变化。
- 勘察发现语义歧义（backfill 的产品意图不明）时：给出两种语义的行为对比+推荐，**停等集成方/用户裁决**而非自裁——handoff 登记为 BLOCKED_ON_RULING。
