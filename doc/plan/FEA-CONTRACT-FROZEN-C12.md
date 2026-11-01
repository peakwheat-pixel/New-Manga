# C12 检查器职责边界 · 冻结记录

**契约**：`doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) + [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C12_CHECKER_SCOPE_DRAFT.md` |
| sha256 | `292a54e5eff1afb31f0535bd14ed3c9d55c44ff98f3a9efd769190c1df902ed8` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 2. 冻结条件逐条核验

| # | C-12 §6 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | [FEA-GOV-7 r2](../reviews/FEA-GOV-7-r2.md) `approved`（P0×0 / P1×0 / P2×3） |
| 2 | 检查器现有断言与 §2 表一致（可机械核对） | ✅ | 实核 `check.ps1` 863 行：STATUS/PLAN 指针、front matter、Canonical Evidence 6 列、manifest、ledger、预算（含 45 行上限）均与 §2 表对应 |
| 3 | `check.ps1` PASS | ✅ | 冻结时 PASS（3 persistent warnings） |

## 3. 依赖与后果

- **无上游依赖**（可随时冻结）。
- **下游**：无（C-12 是治理边界说明，不阻塞其他契约）。
- **实现**：本文档是检查器职责边界的**说明**，不改 `check.ps1`；新增断言须走独立治理 Task（C-12 §4）。

## 4. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
