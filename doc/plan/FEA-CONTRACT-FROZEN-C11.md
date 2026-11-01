# C11 候选 Task 表口径 · 冻结记录

**契约**：`doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) + [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md` |
| sha256 | `ea902d71c11000b49ae0c66682bd97648250df7fc40c44857f7264292b95b568` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 2. 冻结条件逐条核验

| # | C-11 §8 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核确认与方案 r4 §12/§15.6/§15.7 一致、无新增语义 | ✅ | r1（2 P1）→ r2（1 P1）→ r3 [approved](../reviews/FEA-GOV-4-c11-r3.md)（P0×0 / P1×0 / P2×3） |
| 2 | C-01b 或 C-02 至少其一已冻结 | ✅ | **C-01b 已冻结**（[冻结记录](FEA-CONTRACT-FROZEN-C01b.md)） |
| 3 | `check.ps1` PASS | ✅ | 冻结时 PASS（3 persistent warnings） |

## 3. 依赖与后果

- **上游**：C-01b 已冻结（候选表的"不落在空契约上"条件满足）。
- **下游**：**候选 → 建卡 → 独立 Review → 释放实现 Task** 的流程现在可用（C-11 §7 五步）。
- **实现注意**：§1 的拆分映射（`FEA-02`→2 行、`FEA-12`→2 行、`FEA-14-*`→N 行）与 §5 的 H1–H7 Gate 引用必须同时用。

## 4. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
