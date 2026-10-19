---
id: M2-TASKS-BACKFILL-MULTIREGION
title: "executor backfill 多 region 页逐 region 跟进调度（SFX-ENTRY 相邻发现）"
kind: feature
status: done
# DSH r1 有条件通过 → 返修 R1-R7 全 closed（R1 真修+断言有效性红态 terminal 12≠17）→ r2 approved 0×新 P0/P1/P2

approval: user_ruling_2026-10-01_three_followups_all
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-SFX-TRANSLATE-ENTRY]
base_commit: f99a6c55
branch: agent/zcode/M2-TASKS-BACKFILL-MULTIREGION
worktree: G:/CODEX/New Manga.worktrees/M2-TASKS-BACKFILL-MULTIREGION-zcode
delivery_head: f541b2f4（implement=f541b2f4 → handoff/Task 回填/verification=文档 commit）
tip_note: handoff=doc/handoffs/M2-TASKS-BACKFILL-MULTIREGION-f541b2f4.md；语义=选项 A 逐 region fan-out（复用恢复路径 _plan_region 真实规划，plan 层 SFX gate 原样闭环）；三套件 580+2sk（返修 tip；基线 f99a6c55=574+2sk 双侧归档） 0 failed=基线 f99a6c55 574+2sk+新增 5（F1-F5）
---

# M2-TASKS-BACKFILL-MULTIREGION：backfill 逐 region 跟进调度

## 背景（M2-SFX-TRANSLATE-ENTRY Owner 相邻发现，只登记未修）

`src/application/tasks/service.py:922` 附近的 executor backfill 只把页任务绑定**第一个**检出 region——多 region 页（生产常态：BJ02 5 region、BJ06 17 region）的后续 region 不被 backfill 跟进。影响面与正确语义（逐 region 跟进命令？页任务与 region 任务的绑定关系？）需先勘察后设计。

## 交付（AC）

1. **AC1 勘察先行**：backfill 语义全景（`service.py:922` 上下文、backfill 触发时机、页任务↔region 命令的现有绑定模型、多 region 页当前实际行为——是丢失跟进还是仅首 region）；**勘察结论决定修复语义**（逐 region 展开 / 1:N 绑定 / 其他），写进 handoff 后再落笔。
2. **AC2 实现**：按勘察结论的最小语义修复；不改命令协议与 DB schema（如确需 schema 变更则停，登记移交）。
3. **AC3 测试**（先红后绿）：多 region 页 backfill 行为的红绿；单 region 页零变化；边界（0 region 页、region 中途新增）。
4. **AC4 文档**：Task/Handoff 回填；发现相邻缺陷只登记。

## 交付记录（Owner 回填 2026-10-01，delivery_head=f541b2f4（返修 remediation=95469952+7176b6dc））

- [x] **AC1 勘察先行（未触发 BLOCKED_ON_RULING，语义选项有内部先例）**——backfill 触发时机=detect 步骤 commit 成功时同步调用（`commit_step_result` 内，非 resume 路径）；修复前绑定模型=页任务 regionless unit 链只重绑 `region_ids[0]`，`region_ids[1:]` 无任何 PlanUnit（三重实证：旧 R2 断言 secondary untouched / SFX e2e 旧断言译文空+注释 / 旧 docstring 自认 "later scheduling slice"）；**恢复路径已天然逐 region fan-out**（`plan_run(mode=continue/resume_blocked)` 经 `_plan_target` 遍历全部现存 region，N7 实证）——初始执行与恢复路径语义不一致即缺陷本质。语义四选项对比（A 逐 region 展开/B 1:N 绑定=需改 domain 禁改面/C region 自驱动=超允许面编排/D 维持现状）与判定见 handoff §语义选项对比，选定 **A**。
- [x] **AC2 最小实现**——`service.py` 单文件：primary 原位重绑逐字节保留（单 region 页零变化）；对 `region_ids[1:]` 用**恢复路径同一函数 `_plan_region`** 对 live region 快照真实规划追加 unit 链（unit_id=`{task_id}:{region_id}:{step_type}`）；`planned_step_units` 同步增长。**关键设计（红绿过程发现）**：SFX policy gate 在 plan 层生效（production `handle_translate` 不经 gate），照抄 primary decision 会让 manual/skip 的 SFX region 被机器翻译（违反 D06 §85，被 e2e manual 红态抓到）——改用 `_plan_region` 后 gate/lock/stage 决策与恢复路径逐字节一致。零协议/schema 变更（`SqlitePipelineStore.put` 全量重插自动落库）。
- [x] **AC3 先红后绿**——红：`git checkout f99a6c55 -- src/application/tasks/service.py` 后 rebinding 文件 **6 failed 11 passed**（F1 主红/F4/F5+R0-R2 旧语义断言；初版红态曾 7 failed，R3 断言按 fan-out 执行顺序修正后为 6，F5 固化失败传染）；绿：rebinding 18/18（含 R1 断言） + SFX e2e 2/2；三套件 **579 passed + 2 skipped + 0 failed**（基线 f99a6c55=574+2sk，新增 F1-F5 共 5 测试零回退）；单 region 页零变化（F2+N1/N2/N6）、0 region 页（F3+N3）、region 中途新增（F4）全过；溢出检查 workbench+m2_acceptance+editing **188 passed**。
- [x] **AC4 文档**——handoff `doc/handoffs/M2-TASKS-BACKFILL-MULTIREGION-f541b2f4.md`（勘察结论+语义对比+复现命令+风险登记）；verification 四份红绿日志 `verification/M2-TASKS-BACKFILL-MULTIREGION/`；相邻发现只登记：unit_id 双形态并存（primary=page id 形态/克隆=region id 形态，terminal 计数正确性不受影响）、region 中途删除的 `TARGET_DELETED` 传播为既有路径行为（primary/克隆同构暴露，建议另立 Task）。
- 纪律：`git diff --check` EXIT=0；禁改面（`src/domain/**`、`sqlite/schema.py`、`ports/**`、`providers/**`、`bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、其他 application 模块）零 diff；改动面=仅 `src/application/tasks/service.py` + `tests/pipeline/test_regionless_rebinding.py` + `tests/core/test_sfx_policy_end_to_end.py`（多 region 断言按新语义更新）。

## 允许修改面 / 禁改面

允许：`src/application/tasks/**`（backfill 相关）、`tests/`（tasks 相关）、`verification/M2-TASKS-BACKFILL-MULTIREGION/**`、Task/Handoff。

禁改：`src/domain/**`（schema/实体零变更）、`src/infrastructure/sqlite/schema.py`、`src/ports/**`、`src/infrastructure/providers/**`、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`、其他 application 模块（勘察后确需则 handoff 登记移交）。

## 纪律

- 基线不回退：main 530+1skipped 0 failed；既有 backfill 行为（单 region 页）零变化。
- 勘察发现语义歧义（backfill 的产品意图不明）时：给出两种语义的行为对比+推荐，**停等集成方/用户裁决**而非自裁——handoff 登记为 BLOCKED_ON_RULING。
