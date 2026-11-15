# AC-CHECKBOX-CONVENTION-AUDIT-1：**我此前对"记录卫生"的判断是错的**

基线 `84a713305`。

## 1. 我此前说过什么

在 `CHAPTER-MANUAL-SORT-VERIFY-1` §6 与 `FINAL-HANDOFF-2026-11-15.md` §7，我写了：

> 两块"记录卫生"问题（不是缺陷，是表格陈旧）：
> `CHAPTER-MANUAL-SORT.md`：`status: done` 但 **AC1–AC10 全未勾**
> `GATE4-PAGES-UPGRADE-1.md`：`status: done` 但 AC 表停在 `NOT_RUN`

**我把"AC 未勾 + status: done"当成了一个需要后人清理的**问题**。**

## 2. 本轮全量扫描的结果

```powershell
Get-ChildItem doc/tasks -Filter "*.md"   # 遍历全部卡片
# 有 status 字段的卡 = 633
# status ∈ {done, closed_with_limitations} 且 "AC 全未勾（[ ] 数>0 且 [x] 数=0)" = 40
```

**⇒ 40 / 633 ≈ 6.3% 的卡片是这种形态。**

**这不是个别现象。**

## 3. 抽样核实：这 40 张**是不是真的没做**

| 卡片 | `evidence_dir` | 目录存在 |
|---|---|---|
| `EXPORT-IPC-1` | `verification/EXPORT-IPC-1` | ✅ 存在 |
| `FEA-04` | `verification/FEA-04` | ✅ 存在 |
| `GATE3-COVERAGE-MATRIX` | `verification/GATE3-COVERAGE-MATRIX` | ✅ 存在 |

**⇒ 抽 3 张，3 张的证据目录都在。**

## 4. ★ 结论更正

**这是本项目的**惯例**，不是"记录卫生问题"**：

- 卡片用 **`evidence_dir`** 字段指向证据目录；
- **`- [ ]` / `- [x]` 的勾选不是主要证据指针**，更像是规划期的清单；
- 大量卡片 `status: done` + AC 未勾 + **`evidence_dir` 真实存在**。

**⇒ 我此前把它说成"需要后人清理的问题"，是**误读**。**

**⇒ 应更正为**：**这是项目约定；核对一张卡的状态应先看 `evidence_dir`，而不是数 AC 勾选。**

## 5. 这是第 16 次错误（表述失准）

| # | 错误 |
|---|---|
| 13 | 写别人目录后才查 |
| 14 | 覆盖既有证据 |
| 15 | 把 `roundsStarted` 数错 |
| **16** | **把项目惯例误判为"记录卫生问题"，并写进交接文档** |

**⇒ 与前几次不同，这次是**把正常的做法说成异常**（反向误判）。**

## 6. 对 `CHAPTER-MANUAL-SORT` / `GATE4-PAGES-UPGRADE-1` 的正确表述

| 卡片 | 准确说法 |
|---|---|
| `CHAPTER-MANUAL-SORT` | `status: done` + `evidence_dir` 存在 + **代码全实现**（`CHAPTER-MANUAL-SORT-VERIFY-1` 逐项核实）；AC 未勾属项目惯例，**不是缺陷** |
| `GATE4-PAGES-UPGRADE-1` | `status: done` + `evidence_dir` 存在 + **workspace 里 4 张真图**（哈希经我实测）；README 内部 §5/§6 的表述不一致是**它自己的**小瑕疵，与 AC 勾选无关 |

## 7. 建议（给后续维护者）

**如果希望 AC 勾选成为权威信号**，那需要一次全项目的一致性清理（40 张卡）；
**如果不希望**，那应在 `doc/09_COLLABORATION.md` 的 Task 约定里明确写"`evidence_dir` 是权威指针，AC 勾选供规划参考"。

**⇒ 这属于文档约定层面的决定，不是我能单方面改的；留给后续。**

## 8. 未做

- 未逐张核实其余 37 张卡的 `evidence_dir`（只抽 3 张）；
- 未修改任何卡片的 AC 勾选（不越权）。
