# Antigravity 名下 Task 的波及范围（只读盘点，2026-10-19）

执行者：dsh（Coordinator, epoch 8）· HEAD：`18016ed35` · **只读：未改任何 Task 文件**

---

## 1. 结论

用户指令「本对话不再调用 agy」使 **13 个非终态 Task 失去可执行 Owner**，其中 **2 个属于当前 DAG 的 READY**：

```
READY = ARCH-DOC-REBASELINE、P20      ← 两者 owner 均为 Antigravity
```

即 **READY 列表当前没有一个可以派发** —— 名义 READY、实际停滞。

## 2. 全量分布（`owner: Antigravity`，共 38 个）

| status | 数量 | 性质 |
|---|---|---|
| `done` | 17 | 终态，不受影响 |
| **`ready`** | **6** | ⚠️ 无人可派 |
| `closed_with_limitations` | 5 | 终态，不受影响 |
| **`changes_requested`** | **4** | ⚠️ 待返修 |
| `approved` | 3 | 待集成 |
| **`in_review`** | **2** | ⚠️ 待复审 |
| **`in_progress`** | **1** | ⚠️ 中断 |

**非终态合计 13 个。**

## 3. 关键区分：哪些属于**当前**权威，哪些是历史

这一区分决定处置优先级，不能一概而论：

**属于当前 DAG（必须处置）**

| Task | status |
|---|---|
| `P20` | `ready`（根 Task，P20 系列父节点） |
| `ARCH-DOC-REBASELINE` | `ready` |

**不属于当前 DAG（历史系列，`REBASELINE_PLAN` 未列入 READY）**

| Task | status |
|---|---|
| `T3.2.1-REPAIR-3` / `-7` / `-9` / `-10` | `ready` |
| `T3.2.1-REPAIR-4` / `-5` / `-6` / `-11` | `changes_requested` |
| `T3.2.1-REPAIR-8` / `-12` | `approved` |
| `P20-ISOLATION-1` | `in_review` |
| `P22` | `in_review` |
| `P02PRE-R1H-R6-EXEC-A6` | `in_progress` |

`T3.2.1-REPAIR-*` 是一个 10 项规模的历史返修系列（3–12），其中 4 项 `ready`、4 项 `changes_requested`、2 项 `approved`。按 AGENTS.md，**历史 Task 保留为证据**；它们未列入当前 DAG 的 READY，因此**不构成本次停用的即时阻塞**。

## 4. 建议的处置顺序

1. **优先**：`P20` 与 `ARCH-DOC-REBASELINE` 的 Owner 归属。二者是当前 READY 的全部内容，处置后 READY 才重新具有意义。
   - 可对照 `P20-CLOSE-BOUND-HARDEN-2` 的先例（用户明确指令「改派 dsh」后，Owner 由 Antigravity 改为 dsh，Reviewer 保持 Codex 以满足 owner ≠ reviewer）。
   - **但本次用户仅表示「不再调用 agy」，未指明接手方**，故本盘点**不擅自改派**。
2. **次之**：`P20-ISOLATION-1`、`P22`（`in_review`）—— 已完成实现，等待的是复审；复审方（Reviewer）若为 Codex 或 dsh，则**不受 Antigravity 停用影响**，可先行判定。
3. **再次**：`T3.2.1-REPAIR-*` 系列 —— 先判断该系列**是否仍是当前权威**（历史系列），再决定整体归档或改派，**不建议逐项改派**。
4. `P02PRE-R1H-R6-EXEC-A6`（`in_progress`）—— 属 P02PRE 历史系列，随该系列一并处置。

## 5. 盘点边界

**只读**：读取 `doc/tasks/*.md` 前 30 行的 `owner:` / `status:` 字段并分组统计。**未修改任何 Task 文件、未改派任何 Owner、未触碰 `REBASELINE_PLAN` 或 `STATUS`。** 本报告本身写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`（本 Task 的证据目录）。

## 6. 与本次盘点相关的既有结论

`STATUS.md` 的 READY 行在 2026-10-19 已修正为与 `REBASELINE_PLAN` 一致（`READY=ARCH-DOC-REBASELINE、P20`），并新增 `in_review=P09-AC3-DELETE-HARDEN-1、P20-CLOSE-BOUND-HARDEN-2`。因此本盘点的「READY 无一项可派」是**在指针已自洽的前提下**成立的结论，而非指针错误造成的表象。
