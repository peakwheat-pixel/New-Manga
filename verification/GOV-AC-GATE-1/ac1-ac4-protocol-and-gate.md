# AC1–AC4 — AC 状态机械门禁的实现

**Task**: GOV-AC-GATE-1 · **基线**: `3539d8d75` · **授权**: Codex r20 §2.6

## 一、为什么需要这个 gate（r20 的原话）

r20 分析本会话中三次「交付方在自己的 Task 里犯了它正在治理的那类错误」，
第三个是「给漏勾的 AC 补勾，而自己的 AC1–AC4 漏勾」。r20 的结论：

> **建议在协作协议加入机械 AC gate，值得做。** 单靠「所有已完成 AC 必须勾选」
> 不够机械，因为检查器无法从自由文本推知某项是否已完成。
> 可采用最小结构约定：**进入 `in_review` 时每个 AC 必须有显式 machine-readable
> 状态（如 `MET` / `PARTIAL` / `BLOCKED`）**。
>
> 这样能**直接拦住**本 Task 的 4 个已完成 AC 未勾选问题，**也能防止把阻塞项勾成完成**；
> 它不能独自发现「测试没有实际运行却写成 PASS」或错误的字节假设。

本 Task 实现这个建议。

## 二、AC1：状态词汇表（写入 `doc/09_COLLABORATION.md` §4.3）

| 状态 | 语义 | 证据门槛 |
|---|---|---|
| `MET` | 该 AC 在本 Task 范围内成立且已验证 | 需 Canonical Evidence 支撑 |
| `NOT_APPLICABLE` | 该 AC 在本 Task 范围内**不产生要求** | 只需说明理由 |
| `PARTIAL` | 部分达成 | 必填原因 |
| `BLOCKED` | 因外部原因阻塞 | 必填原因 |

**为什么 `MET` 不得附原因**：`MET` 的依据应在 Canonical Evidence 中登记，
而不是写在 AC 行末。允许附原因会诱导「用文字解释代替证据」——正是本规则要防的。

## 三、AC2：书写形式与兼容策略

### 语法

```
- [x] **AC1 标题**：正文…… <<MET>>
- [ ] **AC2 标题**：正文…… <<BLOCKED: 无头 Windows 无法取得 WebView2 句柄>>
- [ ] **AC3 标题**：正文…… <<PARTIAL: ①/② 达成，③ 阻塞>>
- [x] **AC4 标题**：正文…… <<NOT_APPLICABLE: 本 Task 无数据面>>
```

`<<STATUS>>` 或 `<<STATUS: 原因>>`，在行末，其后不得再有内容。
选 `<<>>` 是因为它在 Markdown 中不产生任何渲染效果，且能被正则稳定匹配。

### 勾选与标记的一致性规则

| 勾选 | 允许的标记 |
|---|---|
| `[x]` | `MET` / `NOT_APPLICABLE` |
| `[ ]` | `PARTIAL` / `BLOCKED` |

**矛盾组合一律不允许**：`[x]`+`BLOCKED`、`[ ]`+`MET`、缺标记。

### 兼容策略：**用 `governance_version: 3` 隔离**

这是本 Task 最关键的设计决定。

**存量数据**（实测，2026-10-20）：

| 项 | 值 |
|---|---:|
| Task 文件总数 | 313 |
| 有 AC 的 Task | 102 |
| AC 总数 | **618** |
| 已勾选 | 469 |
| **未勾选** | **149** |
| **已 `in_review` 或终态却有未勾 AC** | **25 个 Task** |

**如果 gate 无差别生效，会有 25 个 Task 一次变红**——其中多数与本次治理无关。

因此：

- **v1/v2 Task 保持原状**，不回溯补标，不套用本节规则；
- **只有 `governance_version: 3` 的 Task** 受本节约束；
- 新 Task 由 Codex 释放时写入 v3。

**这个选择的代价写进了协议，而不是隐去**：

> 本门禁只阻止新增此类缺陷，**不清算存量**。存量由后续专项 Task 处理。

## 四、AC3：检查器 gate

`tools/governance/check.ps1` 改动两处：

1. **L286**：`-eq '2'` → `-in @('2', '3')`，使 v3 Task 继承 v2 的全部检查
   （证据 pin、资源清单等）。
2. **v2 块末尾新增 v3 分支**：对 `in_review` / `approved` / `done` /
   `closed_with_limitations` 的 v3 Task，逐 AC 校验标记。

实现要点：

- 用 `[regex]::Matches` 抓所有 `^\s*-\s*\[([ xX])\]\s*\*\*AC...` 行；
- 每条用 `<<(MET|PARTIAL|BLOCKED|NOT_APPLICABLE)(?::\s*([^>]*))?>>\s*$` 取状态与原因；
- 缺标记 / 组合矛盾 / 缺原因，各自报出**具体 AC 编号**。

**先把 status 设为 `in_progress` 时检查仍 PASS**——这是正确的，
`in_progress` 阶段 AC 本来就没完成，不该被 gate 约束。

## 五、AC4：夹具回归（9 例，全部通过）

夹具写在**系统临时目录**，绝不写进 `doc/tasks/`。运行后断言 `doc/tasks/` 文件集合未变。

```
case                             expect  got     result
------------------------------------------------------------------------------
F1_all_met                       PASS    PASS    OK
F2_unticked_no_marker            FAIL    FAIL    OK
F3_blocked_with_reason           PASS    PASS    OK
F4_checked_but_blocked           FAIL    FAIL    OK
F5_met_with_reason               FAIL    FAIL    OK
F6_blocked_without_reason        FAIL    FAIL    OK
F7_not_applicable_with_reason    PASS    PASS    OK
F8_in_progress_no_gate           PASS    PASS    OK
F9_done_unticked_met             FAIL    FAIL    OK
------------------------------------------------------------------------------
9/9 cases behaved as specified
```

gate 对四类矛盾给出的实际报错：

| 例 | 报错原文 |
|---|---|
| F2 | `AC 状态标记缺失或非法（需行末 <<MET>> / …）：AC2` |
| F4 | `AC 标记为 BLOCKED 时不得勾选：AC2` |
| F5 | `AC 标记为 MET 时不得附原因（依据应进 Canonical Evidence）：AC1` |
| F6 | `AC 标记为 BLOCKED 时必须有原因：AC2` |
| F9 | `AC 标记为 MET 但未勾选：AC1` |

### 一个测试设计上的判断

第一次跑，9 例中 4 例「失败」——但失败原因是**与 gate 无关的规则**
（`当前 DAG 未登记非终态 Task`、`Evidence commit 不含所 pin 文件`）。

**夹具必然触发这些规则**，因为它们不是真实的仓库 Task。

我把判据从「整体 PASS/FAIL」改成「**是否出现 AC gate 自身的 FAIL**」，
因为这是**对 gate 的单元测试**，不是对整个检查器的集成测试。

**这个修正有风险**：如果 gate 的报错文本变了，判据会失配而静默放宽。
因此判据同时匹配 `AC `、`AC 标记`、`AC 状态`、`AC1`、`AC2`、`未找到任何 AC` 六种形态，
并在测试输出中**打印每条实际报错**，便于人工核对是否仍是 gate 在报错。

## 六、这个 gate 不能做什么（写进协议，不隐去）

- 它**不能验证标记是否诚实**——把未做的写成 `MET` 不会被它发现；
- 它**不能发现**「测试没跑却写 PASS」或错误的字节假设；
- 那需要 Canonical Evidence 的 pin 校验与 Reviewer 判断。

**一个能拦住「漏勾」的 gate，不等于能拦住「假装做了」。**
本 Task 只解决前者。

## 七、AC5：全库回归——**0 个 Task 因新 gate 变红**

实测（2026-10-20，gate 落地后）：

```
v3 tasks in review/terminal: 0
Governance check: PASS (1 warnings)
```

逐个扫描 `doc/tasks/*.md`，过滤条件：`status ∈ {in_review, approved, done,
closed_with_limitations}` 且 `governance_version: 3`。**结果为 0 个**。

原因：**目前唯一的 v3 Task 就是本 Task 自己**，而它的 status 是 `in_progress`，
不在 gate 的触发状态集合内。

### 这个「0」意味着两件事，必须分开说

1. **好消息**：新 gate 没有让任何现存 Task 变红。存量 25 个「终态但有未勾 AC」的
   Task 全部是 v1/v2，**完全不受影响**。
2. **但这不是「回归通过」的强证据**：真正的回归意义要在**下一个 v3 Task**
   走完 `in_progress → in_review` 时才体现。本 Task 自己就是第一个样本——
   它必须带着合法标记进入 `in_review`，否则会被自己的 gate 拦下。

**我没有为此放宽 gate。** 如果本 Task 进入 `in_review` 时被拦，那是 gate 正确工作，
不是 gate 太严。

## 八、AC1–AC4 的完成状态

| AC | 结果 | 证据 |
|---|---|---|
| AC1 状态词汇表 | 达成 | `doc/09_COLLABORATION.md` §4.3 |
| AC2 书写形式 + 兼容策略 | 达成 | 同上；存量数据实测于本节 |
| AC3 检查器 gate | 达成 | `tools/governance/check.ps1` 两处改动 |
| AC4 夹具回归 | 达成 | `tools/governance/tests/test_ac_gate.py`，9/9 |

AC5（全库回归）与 AC6（Handoff + Review）待后续轮次。
