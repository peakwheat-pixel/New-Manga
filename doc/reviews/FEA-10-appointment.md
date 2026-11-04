# FEA-10 Appointment（DSH，2026-11-04）

状态：**scope approved（r6 Codex，P0=0/P1=0/P2=2 非阻断）→ DSH 冻结 scope / Appointment 已完成；Task `blocked`（硬前置 `FEA-10-PREREQ-1` 未 done），不得 ready/实施；不 push**
Task：`doc/tasks/FEA-10.md`
依据：Codex 2026-11-04 下一 Task 裁决（FEA-10 首选）；`doc/reviews/FEA-10-scope-r6.md`（**approved**）；`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`；C-08 冻结记录 §3 / SC-R01…R09；C-13 SC-D07/08。

## 1. 角色

| 角色 | Agent | 说明 |
|---|---|---|
| Owner（实现） | **Codex** 新实现会话 | 只写 allowed_paths；不得自审 |
| Reviewer（实现 Review） | DSH 派发的**全新上下文**（Codex/ZCode；未参与实现/返修） | 只读 reviewed_head；报告归档 |
| Integrator / 裁决 | DSH | 提交、门禁、集成、closeout |

## 2. 冻结范围

- PreparedRun 两阶段（PrepareRun 零 DB/零执行；AcceptRun digest 校验；候选过期 `RUN_PREVIEW_EXPIRED`）。
- canonical request builder：preview/send 共用已确认对象；`preparedDigest` 按 C-08 冻结四元组算法；另比较 preview/send payload digest 同值；敏感材料不入普通快照。
- retry 两分支（SC-R08）；SC-R09 durable receipt（丢 ACK/重启找回/异 fingerprint/request_id 非键）。
- candidate-only + 原子 apply（C-13 SC-D07/08）：10 项故障注入；多 Region 编辑 apply 与 Pipeline step seam 两类事务单位；成功时 live/revision/Run receipt 同事务。
- 控制/完成口径（SC-R06/R07）；真实生产 assembly/IPC；回归/证据/独立 Review/DSH 集成。

## 3. 硬前置

- `FEA-10-PREREQ-1`（C-08 块②协议注册）**done 前** FEA-10 不得 `ready`/`in_progress`；当前 Task 状态 `blocked`。
- 不新增 wire/Schema；不碰 C-05/C-15/C-16/C-07 冻结字节；不实现 FEA-11/12/13/14；共享组合根仅 DSH 单点提交。

## 4. 释放/实施条件

- PREREQ-1 done（实现 Review approved + DSH 集成）→ 本 Task 由 DSH 复核依赖后置 `ready` 并通知 Owner 认领。
- 实施门禁：build 0/0；相关 pytest/.NET 全量不减少；真实 IPC（`NEWMANGA_FEA10_IPC=1`）；`check.ps1` PASS；`verify_pins.ps1` 17/17；范围 diff；证据 `verification/FEA-10/**`（含命令/EXIT）；FEA-09 canonical 证据如被复跑重写须恢复。
- 完成定义：实现 + 测试 + 证据 + Handoff → `in_review` → 全新上下文 Review → DSH 集成 → `done`；不 push。

## 5. 残留（r6 非阻断 P2）

- PREREQ 测试表过滤表达式含裸 `|` 会破坏 Markdown 表格（DSH 在 owner 交付后统一修正）。
- 两卡 Closeout/approval 轮次文字在冻结后同步为 r6。
