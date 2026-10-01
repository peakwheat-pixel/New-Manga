---
id: M2-TASKS-PRIMARY-SFX-GATE
title: "primary region 重决策（BACKFILL R2 裁决落地：单 region SFX 页 primary 也经 SFX 门）"
kind: feature
status: in_review  # 交付 19bf234a：红 4F/19P → 绿 23P；三套件 630+1sk 0 failed（基线 627+1sk）；待 DSH 非作者 Review → Codex 集成
approval: user_ruling_2026-10-02_three_confirmations
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TASKS-BACKFILL-MULTIREGION]
base_commit: 1c3ac590  # 3-confirmation release（r1 R6 统一口径）
branch: agent/zcode/M2-TASKS-PRIMARY-SFX-GATE
worktree: G:/CODEX/New Manga.worktrees/M2-TASKS-PRIMARY-SFX-GATE-zcode
delivery_head: 19bf234a（implement=19bf234a → handoff/Task 回填/文档=文档 commit）
tip_note: handoff=doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md；语义=primary（region_ids[0]）与 region_ids[1:] 统一走 _plan_region live region 重决策（=恢复路径同语义），D06 §85 全域生效；单 region 非 SFX 页决策逐步等价零变化（等价性单测钉住）；三套件 630+1sk 0 failed（基线 1c3ac590=627+1sk 实测归档；STATUS "575" 快照早于 SETTINGS-IPC 批次）
---

# M2-TASKS-PRIMARY-SFX-GATE：primary region 纳入 SFX 门重决策

## 背景（M2-TASKS-BACKFILL-MULTIREGION DSH r1 R2，用户裁决②采纳重决策）

backfill fan-out 修复后，`region_ids[0]`（primary）仍沿用 detect 前的页级 plan 决策（`region=None`），SFX gate 对其不可见——"初始 vs 恢复语义不一致"在 primary 上原样存在。DSH 反例：对调 reading_order 使 SFX region 成为 primary + policy=manual ⇒ 落 machine_translation，违反 D06 §85。用户裁决：**采纳重决策**——primary 也走 live region 重决策（与恢复路径/非 primary fan-out 同语义）。

## 交付（AC）

1. **AC1 实现** ✅ @19bf234a：backfill 的 primary 处理从 in-place 重绑改为与 `region_ids[1:]` 同路径（`_plan_region` live region 重决策）；**注意本 Task 改变单 region SFX 页行为（正是裁决目的）**——单 region 非 SFX 页零变化（决策等价性需单测钉住：非 SFX region 重决策结果与原页级决策一致）。
2. **AC2 测试**（先红后绿）✅ @19bf234a：红 **4 failed / 19 passed**（旧 src：DSH 反例 pipeline+e2e 2 条 + R1/F1 适配断言 2 条，`red-1c3ac590-src-plus-tests.log`）；绿 **23 passed**（18 既有+3 新增，目标文件 `green-target-files.log`）；三套件 **630+1sk 0 failed**（基线 627+1sk 实测，零回退）。DSH 反例场景固化——SFX region 为 primary + policy=manual ⇒ SKIP_POLICY 不翻译（红态：primary translate decision RUN）；单 region 非 SFX 页决策零变化（F2 重写 + 全链等价性新测试）；多 region 页回归（BACKFILL 18 条全过，R1/F1 断言按新语义适配）；terminal 账目断言保持（primary 重决策后 terminal==planned==17、progress==1.0，primary 的 SKIP unit 同口径计入）。
3. **AC3 联动登记** ✅：BACKFILL handoff 的「独立 Task 候选登记」节由本 Task 关闭——superseded-by 文字备置于本 Task handoff「§BACKFILL 登记节关闭」供集成方搬运（BACKFILL handoff 在本 worktree 不可改）；SFX-ENTRY/BACKFILL 交付测试适配（R1/F1 unit_id 断言按 region-id 形态、F2 重写为决策等价）已登记于本 Task handoff「测试适配登记」节。
4. **AC4 文档** ✅：Task/Handoff 回填（本文件 + `doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md`）；D06 §85 合规性说明（gate 全域生效）见 handoff。

## 允许修改面

`src/application/tasks/service.py`、`tests/pipeline/**`、`tests/core/test_sfx_policy_end_to_end.py`（对调场景适配）、`verification/M2-TASKS-PRIMARY-SFX-GATE/**`、Task/Handoff。

## 禁改面

`src/domain/**`、`src/infrastructure/**`、`src/ports/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、gate.py（三值语义已就绪零改动）。

## 纪律

- 基线不回退：main 三套件 575+1skipped 0 failed（BACKFILL 集成后口径）；既有非 SFX 单 region 页行为零变化。
- D06 §85 合规是本 Task 的存在理由：任何 SFX region（无论 reading_order 位置）不得绕过门。
