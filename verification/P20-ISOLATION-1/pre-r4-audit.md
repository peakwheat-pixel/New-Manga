# `P20-ISOLATION-1` 待闭环项核查（R4 前的只读审计）

**产出**: 2026-10-20 · **性质**: 只读 · **目的**: 为 R4 Review 准备事实

## 一、当前状态

| 项 | 值 |
|---|---|
| `status` | **`in_review`** |
| `owner` / `reviewer` | Antigravity / Codex |
| `review_status` | **`changes_requested`**（R1 7×P1、R2 6×P1、**R3 3×P1 + 2×P2**）|
| `delivery_head` | **`baf4ec90c`** |
| `base_commit` | `dbeca3bab` |
| AC | **4/4 已勾选** |
| 治理检查 | FAIL（1 个 pin 错误 + 2 warnings）|

**四轮 AC 全勾，但三轮 Review 都是 `changes_requested`。** 这个不一致需要 R4 解决。

## 二、R3 之后发生了什么

R3 的 `reviewed_head` 是 `fc7672338`。之后的提交：

| commit | 说明 |
|---|---|
| `2a8774260` | 「correct my evidence overclaim per Codex R3, **retract AC3/AC6**, fix R-015/R-016」|
| `8898e56a0` | 「fix the **R-010 locator defect** and re-prove AC3 with a real draft that reaches the database」|
| `d6a4ab16b` | 「correct evidence pins for the R-010 rerun」|
| `6dca4a030` | 「repair the evidence bookkeeping for the isolation and memory tasks」|
| `e8cc6d1e4` | 「**re-run the AC4 regression** on current code and record both AC3 verdicts」|

**所以 R3 的两个阻断点都有人处理了：**

- **AC3 阻断**（「真实注入确实杀了 sidecar，但没有在创建弹窗中输入草稿」）→
  `8898e56a0` 修了 locator 缺陷并**用真实草稿重证 AC3**。
- **R-016**（脚本 FAIL 不导致非零退出）→ **已修，实测确认**。

## 三、R-016 已修（实测）

`verification/P20-ISOLATION-1/run-r004-timeline.ps1` L112：

```powershell
exit ([int]($script:scriptFails -gt 0))
```

**现在 FAIL 断言会导致非零退出。R-016 闭环。**

## 四、R-015 **仍未闭环**（本轮核查的主要发现）

R3 的 R-015 原文说的是「**R-005 未真正闭环：Task `delivery_head` 仍…**」。

实测：

| 来源 | `delivery_head` |
|---|---|
| `doc/tasks/P20-ISOLATION-1.md` | **`baf4ec90c`** |
| `doc/handoffs/P20-ISOLATION-1-antigravity.md` | **`796613ef4`** |

**两者不一致。**

**并且两个都不是最后一次实质交付**——之后还有：

- `8898e56a0`（R-010 locator 修复 + AC3 重证）——**实质代码/测试变更**
- `e8cc6d1e4`（AC4 回归重跑 + 两个 AC3 判定记录）——**实质验证**

**所以 `delivery_head` 要么应指向 `e8cc6d1e4`，要么应明确记录「三次提交共同构成交付」。**
**当前值是 `baf4ec90c`，落后于实际交付内容。**

## 五、证据 pin 的 blob 不匹配（6/10）

对 10 条 Canonical Evidence 逐条核验「pin 的 commit 中该路径的 blob hash」：

| 结果 | 数量 |
|---|---:|
| `path` 存在于 pin 的 commit | **10 / 10** |
| **blob hash 与 pin 相符** | **4 / 10** |
| blob hash 不符 | **6 / 10** |

不符的 6 条：`EVID-P20-ISOL-SRC`、`-RUSTLOG`、`-FELOG`、`-UITRACE`、`-REVIEW-R1`、`-R010RUN`。

**这与 `GOV-PIN-LINEAGE-1` 的诊断结论一致**：这些都是**时间性/行尾性失配**，
不是内容丢失。**按 r27/r28，它们保留原值、不重算。**

**但其中只有 1 条（`library_bridge.rs`）是当前工作区也不匹配的**，
因此只有它让检查器报 FAIL。

## 六、因此 R4 需要回答的三件事

1. **`delivery_head` 应是什么？** 当前 `baf4ec90c` 与 handoff 的 `796613ef4` 不一致，
   且都落后于 `8898e56a0` / `e8cc6d1e4`。**修正它是否算「改历史」？**
   （按 r27 §3 的精神：`delivery_head` 是元数据，不是证据 pin，修正它不改变任何内容 hash。）
2. **R3 的 AC3 阻断是否已由 `8898e56a0` 解除？** 若已解除，AC3 的 `[x]` 成立。
3. **R3 的两条 P2 是否还有未处理的？**

## 七、明确未做

- **未修改任何文件。** 本文件是主 checkout 的新增证据。
- 未改 `delivery_head`、未改任何 pin、未改任何 AC。
- 未改 `check.ps1`。

## 八、建议

**`P20-ISOLATION-1` 不能转 `done`**——`review_status` 仍是 `changes_requested`，
需要**第四轮 Review**（R4）在 `delivery_head` 修正后复审。

**R-016 与 AC3 阻断看起来已由 R3 之后的提交解决，但那是我的判读，不是 Review 结论。**
**请 Codex 做 R4 并给出终态。**
