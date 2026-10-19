---
task_id: GOV-AC-GATE-1
author: dsh
recipient: Codex
base_commit: 3539d8d75
delivery_head: fbf459f28941f3760366d5f8e581f8e8ae79ce18
status: ready_for_review
---

# Handoff：GOV-AC-GATE-1

## 一句话

r20 §2.6 建议的机械 AC 门禁已实现：进入 review/终态时每个 AC 必须有
`<<MET>>` / `<<PARTIAL: 原因>>` / `<<BLOCKED: 原因>>` / `<<NOT_APPLICABLE: 原因>>`，
且与勾选状态一致。**9 个夹具全部按规格行为。**

## 为什么需要它（r20 的原话）

> 单靠「所有已完成 AC 必须勾选」不够机械，因为检查器无法从自由文本推知某项是否已完成。

它针对的具体失效在本会话发生了不止一次：**AC 全部做完、一个框都没勾**。

## 关键设计决定：先量存量，再定 scope

动手前实测：

| 项 | 值 |
|---|---:|
| 有 AC 的 Task | 102 |
| AC 总数 | **618** |
| 未勾选 | **149** |
| **终态/review 却有未勾 AC** | **25 个 Task** |

**若 gate 无差别生效，25 个 Task 会一次全红**——全是本规则之前就存在的缺陷。

因此规则用 `governance_version: 3` 隔离：

- **v1/v2 一律不动**，`[x]`/`[ ]` 语义不变，不回溯补标；
- **只有 v3** 受本节约束。

**代价写进协议而不是隐去**：本门禁只阻止新增，不清算存量；存量由后续专项 Task 处理。

## 9 个夹具

| 案例 | 期望 | 实测 |
|---|---|---|
| F1 全勾 + MET | PASS | OK |
| **F2 未勾 + 无标记** | **FAIL** | OK |
| F3 未勾 + BLOCKED + 原因 | PASS | OK |
| **F4 勾了 + BLOCKED** | **FAIL** | OK |
| F5 MET + 附原因 | FAIL | OK |
| F6 BLOCKED 无原因 | FAIL | OK |
| F7 NOT_APPLICABLE + 原因 | PASS | OK |
| F8 in_progress 无标记 | PASS | OK |
| **F9 未勾 + MET** | **FAIL** | OK |

**9/9 behaved as specified。**

## 请 Review 重点核对的三处

### 1. 夹具是否真的在测 gate，而不是被其它规则顺带判红

第一次跑，9 例中 4 例报「失败」，但报错是 `当前 DAG 未登记非终态 Task`、
`Evidence commit 不含所 pin 文件`——**与 gate 无关**。

我把判据改成「是否出现 AC gate 自身产生的 FAIL」，因为这是**对 gate 的单元测试**，
不是对全检查器的集成测试。

**这个修正有放宽风险**：若 gate 报错文本变了，判据会失配而静默通过。
我做了两件事缓解：判据匹配六种报错形态；测试**打印每条实际报错**。

**请自己构造一个违反情形**（不要用我写的夹具），确认 gate 确实报错、
且报错来自 gate 而不是别的规则。

### 2. `governance_version: 3` 的隔离是否是正确的取舍

我的理由是「25 个存量缺陷不该一次性变红」，代价是「存量不清算」。

请判断：
- 这个取舍是否恰当？
- 还是应该让 gate 全量生效、把 25 个 Task 一次性暴露出来？
- **如果你认为应当全量生效，请明确说出来**——那是范围决策，应由你或 Codex 定，
  不该由我为了「不惹麻烦」而选择窄 scope。

### 3. `MET` 不得附原因这条规则是否过严

我的理由：允许 `MET` 附原因会诱导「用文字解释代替证据」。

但反过来说，某些 AC 的 `MET` 判断本身需要简短说明（例如「按 §5.10 封闭投影实现」
这种依据不在证据文件里而在契约文档里）。

请判断这条是否过严，或是否需要为某些情形开例外。

## 明确未做

- 未改任何 Task 的 AC 内容或勾选状态（除本 Task 自身）。
- 未对 25 个存量 Task 做任何补标或修正。
- 未放宽 gate 来让任何 Task 变绿。
- 未改 `src/`、`apps/`、`tests/`。

## 已声明的局限

1. **gate 不能验证标记是否诚实**——手工把未做的写成 `MET` 不会被发现。
   那需要 Canonical Evidence 的 pin 校验与 Reviewer 判断，是另一层。
2. **AC5 的「0 个 Task 变红」不是回归通过的强证据**：目前唯一的 v3 Task 就是本 Task，
   且仍为 `in_progress`。真正的检验在它进入 `in_review` 时——
   **如果被自己的 gate 拦下，那是 gate 正确工作，不是 gate 太严。**
3. 夹具判据做了收窄（见上文），有静默放宽的理论风险，已用打印实际报错缓解。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = fbf459f28941f3760366d5f8e581f8e8ae79ce18`。
