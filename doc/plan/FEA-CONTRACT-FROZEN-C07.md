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
| sha256（冻结后最终字节） | `3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | v1.0：r2 approved（FEA-GOV-10-r2）；v1.1：FEA-05-PORT-1 实现复核 r2 **changes_requested（P1×2）**，待 r3 |
| 复核后到冻结的改动 | v1.1：Draft 端口 7 方法 + 统计/成员表（UNFREEZE 范围） |
| 处置 | **v1.1 尚未重冻**（r2 判 changes_requested）；r3 通过后由 DSH 重冻；当前 pin `3fdb44e4…` 仅作本地校验 |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

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

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `5919b084c906f5cdc79d7e6e1b425f05347d915a77bb5c50f9f97f09c3960b5f` |
| 修正后 pin（最终字节） | `17c8f7016a368a0a827e9a656f9126d9949564aed9d5dc31462c0b5787f1b0c5` |
| 差异范围 | **仅状态行** DRAFT→FROZEN，条款字节未动 |

**为什么保留原值**：pin 是证据，不能静默替换。原值可独立复现（还原本次冻结动作后重算即得），因此证明冻结前的确切字节；修正后的值才是后续校验基准。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。


**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `17c8f7016a368a0a827e9a656f9126d9949564aed9d5dc31462c0b5787f1b0c5`；新增 §1A 修正记录与纪律（见上） | DSH |
| 2026-11-02 | **UNFREEZE v1.0→v1.1（FEA-05-PORT-1）**：`IHostController` 47→54（+7 Draft 端口）、合计 54→61、变更类别 11→18；pin 重算为 `5c48083f…`（原 v1.0 pin `17c8f701…` 保留于 §1A 历史行，不静默替换）；UNFREEZE 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-02.md`；重新独立复核（`FEA-05-PORT-1-impl-r*`） | DSH |
