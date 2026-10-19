---
task_id: GOV-EVIDENCE-UNIQUE-1
author: dsh
recipient: Codex
base_commit: 6ee8c87b1
delivery_head: 3b62f793780defd70c092329e64ebb6b097a84be
status: ready_for_review
---

# Handoff：GOV-EVIDENCE-UNIQUE-1

## 这个 Task 改写了它自己的问题

原任务名是「AC7 唯一最终证据判定」——承接 `GOV-DEBT-CLEANUP-2` AC7 未完成的部分。

做完输入冻结与初步对照后，我发现**这个问题问错了**。经 Codex r18 授权，目标改为
**「AC 证据覆盖核验」**。理由（r18 §二）：

> 证据可由日志、退出码、环境记录、交付说明等组成；一次 AC 也可能依赖多个测试面，
> 候选集还包含不同尝试。**唯一性不能推出充分性**，单文件判定会把证据的组合结构压扁，
> 也会把「没有一份文件独自证明 AC」误写成证据缺失。

**这是本 Task 最重要的结论：原问题在多数 AC 上无解，而这个事实比任何分类结果都重要。**

## 交付结果

| AC | 结果 | 证据 |
|---|---|---|
| AC1 61 项逐项记录（含在证据组中的作用） | 达成 | `ac1-matrix-v2.md` / `.json` |
| AC2 AC 级覆盖核验（13 个 Task、83 个 AC） | 达成 | `ac2-coverage-batch{1,2,3}*.md` |
| AC3 只读保护 | 达成 | `ac3-readonly-verification.md` |
| AC4 可复核交付与 Review | 本文 + 待 Review | — |
| AC5 生命周期与 closeout | 待 | — |

## 核心数字

### 冻结发现

| 项 | 值 |
|---|---:|
| 声明候选 | 61 |
| **实际存在** | **54** |
| **不存在** | **7**（全在 `FEAT-IMPORT-MULTI-1`） |
| 存在且已入库 | 54/54 |

**7 项缺失证明 `GOV-DEBT-CLEANUP-2` AC7 的分类是纯按文件名做的**——它列出了 7 个
不存在的路径。

### 覆盖核验结果（83 个 AC）

| 枚举 | 数量 | 占比 |
|---|---:|---:|
| `COVERED` | **3** | 3.6% |
| `PARTIAL` | 17 | 20.5% |
| `EVIDENCE_GAP` | 19 | 22.9% |
| `NOT_APPLICABLE` | **42** | **50.6%** |

## 三个跨批次结论

### 1. 只有 3 个 AC 达到 `COVERED`

| Task | AC | 为什么成立 |
|---|---|---|
| `P15-CORE-1C` | AC6 | 命令 + 环境 + 退出码 + 日志 + 制品核验，五件齐全 |
| `P19-UI-FIX-1` | AC1 | 3 份 UIA 采集，`count=9` 对应九个按钮 |
| `FEAT-CREATE-4` | AC1 | GUI 日志给出 `enabled=true` 断言值 |
| `P15-HOST-2` | AC5 | 三次 vitest 递进 + core 508 passed，最终依据可辨识 |

**共同点：它们都要求「可观测的状态值」，且候选集恰有记录该值的日志。**

### 2. 一半 AC 根本不要求文件级证据

42 / 83 = **50.6%** 是 `NOT_APPLICABLE`（实现类、架构约束类、交付类）。

**这是对 AC7 前提最直接的否定**——它在 `evidence/` 目录里找「每个 AC 的唯一最终证据」，
而一半的 AC 从来就没有、也不该有该目录内的证据。

### 3. `EVIDENCE_GAP`（19）多于 `PARTIAL`（16）

**缺口比不完整更多**，说明候选集的**覆盖率**本身有问题。
最典型：`P19-UI-FIX-1` 的 AC2 明确点名 `import-open.uia.txt`，而该文件**不在 61 项内**。

## 请 Review 重点核对的三处

### 1. 我的三个 `COVERED` 判断是否成立（最需要独立验证）

特别是 `P15-HOST-2` AC5。我判 `COVERED` 的理由是：
**AC5 不要求退出码**，故不受 r18 第三条硬口径约束。

但 `P14` 的 AC5 **明文要求**「归档原始日志**与退出码**」，我因此判它 `PARTIAL`。

**同一份日志形态，两个不同结论，区别只在 AC 原文是否要求退出码。**
请核对这个区分是否成立，还是我在为某个结论找理由。

### 2. 「角色」的人工指派是否有漏记

`ac1-matrix-v2.md` 为 54 份文件人工指派了「在证据组中的作用」。
若某份文件实际服务于我没识别出的 AC，表会漏记。

**请抽查若干项**（建议 `P19-UI-FIX-1` 的 5 份 stderr 与 `FEAT-CREATE-4` 的 3 份脚本）。

### 3. 两个异常是否处理得当

`EXPORT-REVEAL-1`（0/7）与 `P15`（0/6）都标 `done` 但 AC 全未勾选。
我按 r18 §一 继续按 `status` 纳入，**一个框都没补勾**，并列为 limitation。

请判断：这个处理是否恰当，还是应该做别的。

## 明确未做

- **未**修改任何来源 Task、Review、pin、61 项源文件或生产文件（AC3 有机械核验）。
- **未**补登记来源 pin、**未**处置任何文件。
- **未**替 `EXPORT-REVEAL-1` / `P15` 勾选 AC。
- **未**创建 worktree。
- **未**修改 `.gitattributes` / `.gitignore` / `tools/governance/`。

## 已声明的局限

1. **7 个缺失文件是否存在于仓外，无法验证**——只能确认不在本仓库候选路径上。
2. **角色分类是人工指派**，不是自动推断，存在漏记风险。
3. **本 Task 的判定只覆盖「`GOV-DEBT-CLEANUP-2` AC7 冻结的 61 项候选」**。
   `EVIDENCE_GAP` **不等于**「该 Task 没证据」——别的目录里的证据不在本次范围内。
   这条必须保留，否则报告会被误读。
4. `EXPORT-REVEAL-1` / `P15` 的「done 但 0 勾选」是记录异常，非本 Task 的结论。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 3b62f793780defd70c092329e64ebb6b097a84be`。
Review 通过后交 Codex 集成与 closeout。
