# M2-TASKS-PRIMARY-SFX-GATE 集成记录（代行 Codex / 编排会话）

- 分支 `agent/zcode/M2-TASKS-PRIMARY-SFX-GATE`；链：3-confirmation release `1c3ac590` → `19bf234a`(implement) → `ff9d7d4f`(docs) → r1 修正 commit（本 commit 前刀）
- Review：DSH r1 **有条件通过（CONDITIONAL PASS，0×P0/P1，无代码返修）**——实现语义正确：primary 与 region_ids[1:] 统一进同一 `_plan_region` live-Region 重决策（`service.py:979-1000`），SFX gate 对 primary「不可见→一致生效」裁决②落地无偏差；页级决策链退役后无任何按旧 unit_id 寻址的消费者被破坏；红绿链自洽（`doc/reviews/M2-TASKS-PRIMARY-SFX-GATE-19bf234a-dsh-r1.md`）

## r1 条件闭合（集成刀）

| # | 处置 |
|---|---|
| R1（P2） | 归因撤回更正：「SETTINGS-IPC 批次集成」错误（该 Task 未集成）；真因=**三套件 composition 未统一**（627=含 tests/pipeline 组合 vs 575=providers+core+m2_acceptance 组合，两数不可比皆真）；集成方主 venv 复跑矩阵归档 |
| R2（P2） | numstat 实测 **net +13**（73+/60−）更正「净 -37」 |
| R3（P3） | 5 份日志全部加溯源头重存档（command/venv/worktree/tree-state/date；基线 detach 1c3ac590 实测 **627+1sk** 精确复现、tip 绿 **630+1sk**） |
| R4/R6（P3/P4） | docstring 限定 + Task base_commit 统一 1c3ac590 |
| R5/R7/R8/R9（P3/P4） | 登记 follow-up：except 收窄至 {TARGET_DELETED,TARGET_NOT_FOUND}+run 级诊断（BACKFILL r2 N1 同款）；反例可达性措辞；`_step_flow` 重复步（既有）；primary policy=translate 覆盖测试 |

## 集成运行时项

- 主 venv 双侧（含 pipeline 组合）：baseline 1c3ac590=**627+1sk**、tip=**630+1sk** 0 failed（精确复现 Owner 数字）
- post-merge 三套件（providers+core+m2_acceptance 口径）：见 close commit
- 跨 Task 搬运（main 侧）：BACKFILL 登记节 superseded-by、STATUS R2 候选行更新
