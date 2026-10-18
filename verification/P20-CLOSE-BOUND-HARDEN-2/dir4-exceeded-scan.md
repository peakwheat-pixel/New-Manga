# 全仓 DIR-4 超限扫描（只读，2026-10-19）

执行者：dsh（Coordinator, epoch 8）· HEAD：`558104392` · **只读：未修改任何 Task 文件**

---

## 1. 触发原因

本次扫描源于我连续两轮的判断失误：

| 轮次 | 我的错误判断 | 实际 |
|---|---|---|
| R55 | 「`P22` 我可以直接复审」（以为复审未开始） | 已有 **9 轮** review，其中 7 轮是我做的 |
| R56 | 「`P20-ISOLATION-1` 是首轮，不涉 DIR-4」 | 已有 **3 轮** `changes_requested` |

两次都是**只读 frontmatter 的一两个字段就下结论**，没有检查 `review_status` 与 review 文件清单。**两次「撞见」超限项，说明缺少一次系统性排查。**

## 2. 扫描方法与范围

- **范围**：`doc/tasks/*.md` 全部 Task
- **终态排除**：`done` / `closed_with_limitations` / `rejected` / `verified_complete` / `superseded` / `cancelled`
- **超限判据**：`review_status` 含 `changes_requested`，**或** 证据目录下 `*review*.md` ≥ 3 份

## 3. 结果

**非终态 Task 共 59 个**；疑似 DIR-4 超限 **3 个**：

| review 文件数 | status | Task | `review_status` |
|---|---|---|---|
| **22** | `in_review` | **`P22`** | （字段为空）|
| 6 | `approved` | `P02-NEW-TIME-X6` | （字段为空）|
| **3** | `in_review` | **`P20-ISOLATION-1`** | `changes_requested（R1 7×P1、R2 6×P1、R3 3×P1+2×P2）` |

## 4. 判定：真正未收敛的只有 2 个

**`P02-NEW-TIME-X6` 虽有多轮 review，但 status 已是 `approved`** —— 多轮之后**收敛了**，不是超限遗留。它出现在清单里是因为判据只看文件数，属**假阳性**，在此明确排除。

**真正卡住的是 2 个**，且形状完全一致：

- 均 `status: in_review` 而 `review_status`/历史显示**未通过**
- 均**不在** `REBASELINE_PLAN` 的 READY/DAG 中
- 均**无承接 Task**（对比：`P09-AC3-DELETE-1` → `HARDEN-1`，`P20-CLOSE-BOUND-HARDEN-1` → `HARDEN-2` 都有承接方）
- 均**远超 DIR-4 的 2 次上限**（`P22` 达 22 份 review 文件；`P20-ISOLATION-1` 3 轮）

## 5. 结论：问题范围可控，但缺一个收口机制

**好消息**：不是大面积蔓延 —— 59 个非终态里只有 2 个真正卡住。

**坏消息**：这 2 个**没有任何机制会让它们浮现**。它们既不在 READY（不会被派发），也不是终态（不会被统计为遗留），只会在某个 Agent 偶然侦察时消耗一轮。**我这两轮就是活生生的例子。**

**因此建议登记的治理缺陷不是「有 Task 超限」**（DIR-4 本就预期会出现超限），**而是「超限后缺少强制收口路径」**：

- 已收口的两个先例（`P09-AC3-DELETE-1`、`P20-CLOSE-BOUND-HARDEN-1`）都是**用户在会话中当场裁决**的
- 一旦那场会话结束而裁决未发生，Task 就**永久停在 `in_review`**
- `STATUS.md` 与 `REBASELINE_PLAN` 都不会列出它们（它们不在 DAG 中）

**建议的处置**（需用户裁决，本报告不擅自执行）：

| Task | 建议 |
|---|---|
| `P22` | 按既有先例 `closed_with_limitations`；22 份 review 未收敛，续做第 23 轮**违反 DIR-4** |
| `P20-ISOLATION-1` | 同上；其 AC 已 4/4 勾选，卡在 review 而非实现 |

**并建议登记一条流程要求**：任何 status 停在非终态超过一轮完整会话、且 `review_status` 为 `changes_requested` 的 Task，应在 `STATUS.md` 的保留项中**显式列出**，使其无法静默滞留。

## 6. 扫描边界

**只读**：读取各 Task 前 40 行的 `status` / `review_status` / `reviewer` 字段，并统计各证据目录下 `*review*.md` 的文件数。**未修改任何 Task 文件、未改派 Owner、未触碰 PLAN/STATUS。** 本报告写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`（本 Task 证据目录）。

**已知局限**：判据基于文件数与 frontmatter 字段，未解析每份 review 的实际结论，因此存在假阳性（`P02-NEW-TIME-X6` 即为一例，已人工排除）。**真实超限数可能略高于 2**，但不会出现数量级偏差。
