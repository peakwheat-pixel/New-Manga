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
| sha256（冻结后最终字节） | `9c1eb974342af889c8c3acb8b7f7d7893ba44f05ee4b32c871116e249b321d74`（v1.5，2026-11-10 UNFREEZE：LIB-1 P5–P8 落地统计 69/76；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md`） |
| 前一 pin（v1.2 保留） | `5673b1c4b53e69ec36f1897ea5bb0ba8eeedbf437320381ee1b2a04448bf2aa6` |
| 前一 pin（v1.1，保留原值） | `3fdb44e49afe9fb25e715c5a41bd247cee269c194d045e1f79946f25067dd714` |
| r1 复核锚（未冻结，处置前字节） | `c67c40e72938ac3d5284d778758a17e66f65d760c38e2aa7c6da548a79f47550` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | v1.0：r2 approved（FEA-GOV-10-r2）；v1.1：**r3 approved（FEA-05-PORT-1，P0/P1=0，P2×11 接受）**；v1.2：**r2 approved**（`doc/reviews/FEA-14-S5-PREQ-1-wire-review-r2.md`，P0/P1/P2=0，6×P3 不阻断；r1 changes_requested → 处置 → r2 approved） |
| 复核后到冻结的改动 | v1.1：Draft 端口 7 方法 + 统计/成员表（UNFREEZE 范围）；v1.2：新增「S5 计划追加」节（25 条计划命令；代码未变、统计不变） |
| 处置 | v1.1 **已重冻**（2026-11-02，r3 approved）；v1.2 **UNFREEZE 已生效**（2026-11-10，PREQ AC2；r2 approved，本记录 §1 与 §5 已登记）；pin = 当前文件 SHA-256 |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验

| # | C-07 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（P1 生成脚本缺失）→ 入库脚本 → r2 [approved](../reviews/FEA-GOV-10-r2.md)（P0×0 / P1×0 / P2×3）；v1.2 UNFREEZE 复核：见载体 §4/§5 |
| 2 | 生成脚本入库 | ✅ | [`tools/generate_api_inventory.py`](../../tools/generate_api_inventory.py)（177 行，UTF-8 stdout 固定） |
| 3 | `--check` 通过 | ✅ | `python tools/generate_api_inventory.py --check` → EXIT=0，**1/54/6 = 61**（代码实测；「S5 计划追加」节不计入脚本统计） |
| 4 | `check.ps1` PASS | ✅ | 冻结时 PASS；2026-11-10 UNFREEZE 后 `check.ps1`（默认 + `-TaskPath`）PASS（3 persistent warnings） |

## 3. 依赖与后果

- **无上游依赖**（清单只读代码）。
- **下游**：所有涉及 `IHostController`/`IRunController`/`IReaderProgressSink` 的实现 Task（须按清单保持旧签名）。
- **实现注意**：清单是**基线**；新增/删除端口方法须在同一 Task 内重跑脚本并更新清单，diff 即审查信号。
- **v1.2 计划追加节**（`## S5 计划追加`）：25 条命令为**预冻结名单**，实现卡落地时须（a）把对应行从「计划追加」移入正式成员表；（b）重跑脚本并把统计从 61 更新为实测值；（c）重算 pin 并在实现卡内记录。计划节本身不改变旧签名与 `--check` 基线 61。

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
| 2026-11-10 | **UNFREEZE v1.1→v1.2（FEA-14-S5-PREQ-1）**：inventory 新增「S5 计划追加」节（25 条计划命令：FONT 4 / LIB 4 / READ 7 / EDIT 5 / AI 5），**代码/旧 54 签名/统计零改动**（`--check` 仍 1/54/6=61）；pin 重算为 `5673b1c4…`（v1.1 pin `3fdb44e4…` 保留，r1 锚 `c67c40e7…` 保留为未冻结中间值）；载体 [CONTRACT-UNFREEZE-2026-11-10-C07](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md)；独立复核 r1 `changes_requested` → 处置 → **r2 `approved`**（P0/P1/P2=0，6×P3 不阻断） | DSH |
