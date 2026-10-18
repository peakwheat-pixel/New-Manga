# 就绪状态依赖链（2026-10-19）

执行者：dsh（Coordinator, epoch 8）· HEAD：`c089faa0b` · **只读分析，未改任何 Task 或指针**

---

## 1. 为什么需要这张图

`STATUS` 与 `REBASELINE_PLAN` 把 Task 表示为**扁平列表**（READY / BLOCKED / in_review）。但本会话的核对显示：**当前无法关闭的 Task 并非各自独立卡住，而是串在一条链上**。扁平列表看不出这一点，于是每个 Task 看起来都"自己有问题"，而实际上**链头只有一个**。

## 2. 依赖链

```
[链头] P20 的 AC4 定性（无障碍 Invoke 部分）
          │ 解锁
          ▼
       P20 可关闭
          │ 解锁（ARCH-DOC-REBASELINE 的明文解除条件）
          ▼
   ARCH-DOC-REBASELINE 的 AC5 裁决
          │ 解锁
          ▼
   ARCH-DOC-REBASELINE 整体 closeout
```

**关键证据**：`doc/tasks/ARCH-DOC-REBASELINE.md` 明文写着：

> **解除条件**：**P20 释放并关闭**后，本 Task 方可做 AC5 裁决并整体 closeout（或按 AC7 另行冻结 consumer-scoped 交付）。

## 3. 每一环的现状

### 环 1：`P20` 的 AC4

| 分项 | 现状 |
|---|---|
| 交互延迟 | **36.0 ms** ✅（阈值 ≤ 50 ms）|
| 帧率 | 按用户裁决 `avg ≤ 50 ms` 记 PASS；`p95 77.5 ms` 如实记录 |
| **无障碍 `Invoke`** | ❌ **未达标** |

Task 原文自述：「**实测部分通过，保留未勾选**」。承载帧率裁决的 `P20-AC4-FPS-1` 已按用户裁决 `closed_with_limitations`。

**⇒ 卡的是「无障碍 Invoke 部分如何定性」，属裁决项，不是实现工作量。**

### 环 2：`P20` 整体

**AC 6/7 已完成**（AC1 打包、AC2 冷启动、AC3 内存、AC5 无 GPU 降级、AC6 故障隔离、AC7 发布 Gate）。**只差 AC4 定性即可关闭。**

### 环 3：`ARCH-DOC-REBASELINE`

**AC 0/7 勾选，但这不等于 7 项都未完成** —— 需区分两种语义：

- **AC7 本身已完成**：三项构成（固定 head 非作者 Review `dsh-review-r1.md`、Codex 集成 `integration_commit: 4227e8b50…`、逐消费者 Gate 裁决 `ac7-per-consumer-gate-ruling.md`）**全部达成**，Task 正文自述「AC7 三项构成全部达成」。
- **但整 Task 按 AC7 自身的规定不得 done**：「某项未完成不标整 Task done」（AC1–AC3 仍 PARTIAL、AC4–AC6 实测部分属消费者责任）。
- 因此 `[ ]` 标的是**整 Task 未完成**，而 `STATUS` 说「AC7 已完成」**同样正确** —— **两者不矛盾，是不同层级的陈述**。

## 4. 结论：处置顺序应当倒过来

| 顺序 | 动作 | 解锁 |
|---|---|---|
| **1** | 裁决 `P20` 的 **AC4**（无障碍 `Invoke` 如何定性） | → `P20` 可关闭 |
| **2** | 关闭 `P20` | → `ARCH-DOC-REBASELINE` 可做 AC5 裁决 |
| **3** | `ARCH-DOC-REBASELINE` 的 AC5 裁决 + 整体 closeout | → **当前 READY 清空** |

**由此得出对 Owner 归属的判断（修正本会话早前的建议）**：

| Task | 建议 | 理由 |
|---|---|---|
| `P20` | **改派 dsh** | 6/7 已完成，只差一项定性；改派后我能推进到收口 |
| `ARCH-DOC-REBASELINE` | **标 `blocked`** | 其最后动作被 `P20` 关闭前置锁住；**改派给任何人都无法推进** |

## 5. 与 DIR-4 扫描的关系

`dir4-exceeded-scan.md` 记录的 `P22`、`P20-ISOLATION-1` 与本图**无关**：它们不在任何依赖链上，纯粹是**超限后无收口路径**。两条问题线需**分别处置**：

- **本图**：正常依赖链，只需按序解锁
- **DIR-4 扫描**：异常滞留，需裁决收口

**不要混为一谈** —— 前者是设计使然，后者是流程缺口。

## 6. 边界

**只读分析**：读取 `P20` / `ARCH-DOC-REBASELINE` / `P20-AC4-FPS-1` 的 Task 正文与证据目录、`STATUS.md` 相关行。**未修改任何 Task、未改任何指针、未改派 Owner。** 本文件写入 `verification/P20-CLOSE-BOUND-HARDEN-2/`（本 Task 证据目录）。

**已纠正的一处自身误判**：本会话 R62 曾把 `ARCH-DOC-REBASELINE` 的「STATUS 说 AC7 完成 / Task 标 `[ ]`」报告为**矛盾**；核实后确认**两者都正确**（AC7 完成 ≠ 整 Task 完成）。本文件 §3 已按正确理解重述。
