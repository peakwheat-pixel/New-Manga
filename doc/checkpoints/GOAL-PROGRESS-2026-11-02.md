# Goal 进度文件 · 2026-11-02（自主推进段 2）

**当前 HEAD**：`91be6c134`（FEA-03 done 收口）
**主推进**：`FEA-04` Current 适配（范围冻结 v1，待独立复核 r1）

---

## 1. 已完成（2026-11-01/02 段）

| 项 | 状态 | 证据 |
|---|---|---|
| `FEA-00A-IMPL-1` | **done** | 集成 `e0ba29eba`；实现复核 r1 approved；194 passed |
| `FEA-03`（草稿与保护） | **done** | 范围复核 r5 approved（r1–r4 changes_requested）；C-13 v6 UNFREEZE approved；实现复核 r5 approved P0/P1=0；集成 `76d947923`；1052 passed；pin 15/15 |
| `FEA-03` 实现 | delivery `1db802f8b` + hygiene `651b6cfb3` | CORE + BRIDGE；V1–V25 证据；P2×13 登记 |

## 2. 待裁决（需用户拍板；已给推荐并先行裁决）

| # | 事项 | 推荐 | 处置 |
|---|---|---|---|
| Q-12 | 释放 `FEA-04`（Current 适配） | 释放（依赖 FEA-02-CORE/FEA-03 均 done） | **DSH 裁决：释放**；owner=ZCode（方案指定），ZCode 不可用时 DSH 可指派 Codex |
| Q-13 | FEA-03 的 V19（旧→新/新→旧组合） | 集成验证 deferral | 已登记（Task 卡 deferral + v-matrix）；集成窗口或 FEA-04 回归覆盖 |
| Q-14 | FEA-03 P2×13 技术债 | 接受遗留，登记在 Review r5 | 不阻塞 done |
| Q-15 | FEA-04 切换（Current↔Fluent）是否本卡实现 | 否，仅 preflight + fail-closed；Fluent 入口在 FEA-05 | 卡内禁止范围已写 |

## 3. 下一动作

1. FEA-04 范围冻结 v1 派独立复核 r1 → 迭代 → ready。
2. 实现（ZCode 优先；不可用则 Codex）→ 独立实现复核 → 集成 → done。
3. 之后候选：`FEA-04b`（Fluent 四页设计规格，写域 `doc/design/fluent-v1/`，可与 FEA-04 并行不冲突）。

## 4. 状态变更记录

| 时间 | 变更 | 记录 |
|---|---|---|
| 2026-11-02 02:45 | 建立；记录 FEA-03 done 与 FEA-04 释放 | DSH |
