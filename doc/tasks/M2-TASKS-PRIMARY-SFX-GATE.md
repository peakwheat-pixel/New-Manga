---
id: M2-TASKS-PRIMARY-SFX-GATE
title: "primary region 重决策（BACKFILL R2 裁决落地：单 region SFX 页 primary 也经 SFX 门）"
kind: feature
status: ready
approval: user_ruling_2026-10-02_three_confirmations
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TASKS-BACKFILL-MULTIREGION]
base_commit: f99a6c55
branch: agent/zcode/M2-TASKS-PRIMARY-SFX-GATE
worktree: G:/CODEX/New Manga.worktrees/M2-TASKS-PRIMARY-SFX-GATE-zcode
---

# M2-TASKS-PRIMARY-SFX-GATE：primary region 纳入 SFX 门重决策

## 背景（M2-TASKS-BACKFILL-MULTIREGION DSH r1 R2，用户裁决②采纳重决策）

backfill fan-out 修复后，`region_ids[0]`（primary）仍沿用 detect 前的页级 plan 决策（`region=None`），SFX gate 对其不可见——"初始 vs 恢复语义不一致"在 primary 上原样存在。DSH 反例：对调 reading_order 使 SFX region 成为 primary + policy=manual ⇒ 落 machine_translation，违反 D06 §85。用户裁决：**采纳重决策**——primary 也走 live region 重决策（与恢复路径/非 primary fan-out 同语义）。

## 交付（AC）

1. **AC1 实现**：backfill 的 primary 处理从 in-place 重绑改为与 `region_ids[1:]` 同路径（`_plan_region` live region 重决策）；**注意本 Task 改变单 region SFX 页行为（正是裁决目的）**——单 region 非 SFX 页零变化（决策等价性需单测钉住：非 SFX region 重决策结果与原页级决策一致）。
2. **AC2 测试**（先红后绿）：DSH 反例场景固化——SFX region 为 primary + policy=manual ⇒ SKIP_POLICY 不翻译（当前红：落 machine_translation）；单 region 非 SFX 页决策零变化；多 region 页回归（BACKFILL 既有 18+2 测试全过）；terminal 账目断言保持（primary 重决策后 terminal 计入口径一致）。
3. **AC3 联动登记**：BACKFILL handoff 的「独立 Task 候选登记」节由本 Task 关闭——handoff 加 superseded-by 互指；SFX-ENTRY/BACKFILL 交付测试如需适配（对调场景）按新语义更新并登记。
4. **AC4 文档**：Task/Handoff 回填；D06 §85 合规性说明（gate 全域生效）。

## 允许修改面

`src/application/tasks/service.py`、`tests/pipeline/**`、`tests/core/test_sfx_policy_end_to_end.py`（对调场景适配）、`verification/M2-TASKS-PRIMARY-SFX-GATE/**`、Task/Handoff。

## 禁改面

`src/domain/**`、`src/infrastructure/**`、`src/ports/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、gate.py（三值语义已就绪零改动）。

## 纪律

- 基线不回退：main 三套件 575+1skipped 0 failed（BACKFILL 集成后口径）；既有非 SFX 单 region 页行为零变化。
- D06 §85 合规是本 Task 的存在理由：任何 SFX region（无论 reading_order 位置）不得绕过门。
