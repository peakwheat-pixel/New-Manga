# C07 API Inventory · 冻结记录

**契约**：`doc/plan/FEA-C07_API_INVENTORY.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) + [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C07_API_INVENTORY.md` |
| sha256 | `5919b084c906f5cdc79d7e6e1b425f05347d915a77bb5c50f9f97f09c3960b5f` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 2. 冻结条件逐条核验

| # | C-07 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（P1 生成脚本缺失）→ 入库脚本 → r2 [approved](../reviews/FEA-GOV-10-r2.md)（P0×0 / P1×0 / P2×3） |
| 2 | 生成脚本入库 | ✅ | [`tools/generate_api_inventory.py`](../../tools/generate_api_inventory.py)（177 行，UTF-8 stdout 固定） |
| 3 | `--check` 通过 | ✅ | `python tools/generate_api_inventory.py --check` → EXIT=0，1/47/6 = 54 与文档一致 |
| 4 | `check.ps1` PASS | ✅ | 冻结时 PASS（3 persistent warnings） |

## 3. 依赖与后果

- **无上游依赖**（清单只读代码）。
- **下游**：所有涉及 `IHostController`/`IRunController`/`IReaderProgressSink` 的实现 Task（须按清单保持旧签名）。
- **实现注意**：清单是**基线**；新增/删除端口方法须在同一 Task 内重跑脚本并更新清单，diff 即审查信号。

## 4. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
