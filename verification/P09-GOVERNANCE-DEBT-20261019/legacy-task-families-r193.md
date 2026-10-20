# 22 个「未在 DAG 登记的非终态 Task」的家族分析

**产出**：2026-10-20 · **数据**：`per-task-check-audit.json`
**用途**：把「22 个 Task 需要逐个裁定」压缩成「**7 个家族需要裁定**」。

## 一、结论先行

**检查器报 22 个非终态 Task「未在当前 DAG 登记」。我逐个核实：**

| 项 | 数 |
|---|---:|
| 非终态 Task 报此错 | **22** |
| **其中在 `REBASELINE_PLAN` 中被提及的** | **0** |
| 归入的家族 | **7** |

**所以这不是 22 个孤立问题，是 7 个家族的性质问题。**

## 二、逐家族

| 家族 | 个数 | 状态分布 | 家族根 Task 状态 |
|---|---:|---|---|
| **`P02-NEW-TIME-X6`** | 3 | `approved` ×3 | 根 `P02-NEW-TIME-X6` **本身非终态**（`approved`）|
| **`P02PRE-R0S*`** | 4 | `blocked` ×4 | `P02PRE` **无文件** |
| **`P02PRE-R1H`** | 6 | `blocked` / `in_progress` / `in_review` | `P02PRE-R1H` **本身非终态**（`in_progress`）|
| **`P15-CORE-1`** | 1 | `blocked` | `P15` = **`done`**（终态）|
| **`P19-AC3-1`** | 1 | `in_review` | `P19` = **`closed_with_limitations`**（终态）|
| **`P19-UI-FIX-3`** | 1 | `blocked` | 同上 |
| **`T3.2.1-REPAIR-*`** | 6 | `approved` / `changes_requested` | `T3.2.1` = **`closed_with_limitations`**（终态）|

**逐项清单**：

```
P02-NEW-TIME-X6                        approved
P02-NEW-TIME-X6-BUILD-CARGO            approved
P02-NEW-TIME-X6-POSTRUN-REVIEW         approved
P02PRE-R0S2                            blocked
P02PRE-R0S4                            blocked
P02PRE-R0S5                            blocked
P02PRE-R0S6                            blocked
P02PRE-R1H                             in_progress
P02PRE-R1H-P2-1-EVIDENCE-CLOSURE       blocked
P02PRE-R1H-R6-EXEC-A4                  blocked
P02PRE-R1H-R6-EXEC-A5                  blocked
P02PRE-R1H-R6-EXEC-A6                  in_progress
P02PRE-R1H-R6-ZCODE-H1                 in_review
P15-CORE-1                             blocked
P19-AC3-1                              in_review
P19-UI-FIX-3                           blocked
T3.2.1-REPAIR-4                        changes_requested
T3.2.1-REPAIR-5                        changes_requested
T3.2.1-REPAIR-6                        changes_requested
T3.2.1-REPAIR-8                        approved
T3.2.1-REPAIR-11                       changes_requested
T3.2.1-REPAIR-12                       approved
```

## 三、两种不同的形状（这个区分很重要）

### 形状 A：**家族根自身非终态**（9 个）

- `P02-NEW-TIME-X6` 家族（3）：根 `approved`
- `P02PRE-R1H` 家族（6）：根 `in_progress`

**这 9 个的父/根**本身**还在活动状态。**
**所以「未在 DAG 登记」对它们是**两重**问题：根没登记，子也没登记。**

**它们不是「收口后遗留」，而是**一整条从未进入当前 Plan 的活动线**。**

### 形状 B：**家族根已终态，子仍非终态**（13 个）

- `P15-CORE-1`（根 `done`）
- `P19-AC3-1`、`P19-UI-FIX-3`（根 `closed_with_limitations`）
- `T3.2.1-REPAIR-*` ×6（根 `closed_with_limitations`）
- `P02PRE-R0S*` ×4（`P02PRE` 无文件，属孤立切片）

**这是我 Round 188 处理过的那一类**：父已收口，子项状态仍写着「进行中/待改」。
**当时的判据是「状态服从授权」——Plan 未激活即不得声称 `ready`。**

**但对这 13 个，状态不是 `ready`**（是 `blocked`/`in_review`/`changes_requested`/`approved`），
**它们描述的是「这件事走到哪一步」，不是「现在可以开工」。**

## 四、我为什么不动它们

**r38 的裁定**：

> **状态字段记录的是生命周期历史，它不证明活性，也不证明死亡。**
> **`superseded` 需要具名替代物或架构裁定。**

**所以我不能因为「它们看起来是遗留」就批量改状态。**

**而 Round 188 我改那 4 个 `T3.2.1-REPAIR-*`，判据是**具体且窄**的**：
**它们的 `status: ready` 是一个「授权声明」，而 Plan 未释放——两者直接矛盾，状态必须让位。**

**这 13 个没有那个矛盾**：`blocked` 断言的是「被阻」，`in_review` 断言的是「送审中」。
**这些陈述**可能与事实不符**，但**不与授权冲突**。

**所以判据不能外推。**

## 五、建议的裁定路径（需 Codex 或 Plan 所有者）

**请按家族裁定，而不是按 Task：**

| 家族 | 建议问的问题 |
|---|---|
| **`P02-NEW-TIME-X6`**（3）| **这条线还要不要？** 若要 → 在 Plan 登记并释放；若不要 → 必须有具名替代或架构裁定才能标 `superseded` |
| **`P02PRE-R1H`**（6）| 同上。**注意根是 `in_progress`——这是唯一一个「声称正在做」的根**，最需要先定性 |
| **`P02PRE-R0S*`**（4）| `P02PRE` 无文件；这 4 个是孤立切片。**建议逐项判断是否已成历史** |
| **`T3.2.1-REPAIR-*`**（6）| 根已 `closed_with_limitations`。**它们是被放弃的返修项，还是被后续 Task 覆盖了？** |
| **`P15-CORE-1`**（1）| 根 `done`。单点判断 |
| **`P19-AC3-1` / `P19-UI-FIX-3`**（2）| 根已 `closed_with_limitations`。单点判断 |

**7 个决定，而不是 22 个。**

## 六、明确未做

- **未修改任何这 22 个 Task 的 `status`**
- **未修改 `REBASELINE_PLAN`**
- **未把任何 Task 标为 `superseded`**（r38 要求具名替代物或架构裁定）
- **未验证**这 22 个 Task 的历史证据是否仍可解析
- **未判断**它们是否已被后续 Task 实际覆盖
