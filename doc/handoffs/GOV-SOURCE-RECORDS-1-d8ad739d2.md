---
task_id: GOV-SOURCE-RECORDS-1
author: dsh
recipient: Codex
base_commit: 32f95fdf9
delivery_head: d8ad739d2d99ac40fc96c3f2eed955eb59e516fa
status: ready_for_review
---

# Handoff：GOV-SOURCE-RECORDS-1

## 一句话

两个 `done` 的 Task 里 13 个 AC 一条都没勾。**读完它们的 Closeout Record 后可以确认：
这是表单遗漏，不是 AC 未达成。** 本 Task 补勾了 12 项，保留 1 项。

## 补勾结果

| Task | 补勾 | 保留未勾 |
|---|---:|---:|
| `EXPORT-REVEAL-1` | **6**（AC1/2/3/5/6/7） | **1（AC4）** |
| `P15` | **6**（AC1–AC6） | 0 |

## 依据不是 status，是证据表自己的 `AC/Gate` 列

这一点是本 Task 的核心。两个 Task 的 Canonical Evidence 表**早就标注了每份证据支持哪个 AC**：

**`EXPORT-REVEAL-1`**

| 证据 | AC/Gate |
|---|---|
| `EXPORT-REVEAL-CONTRACT` | AC1 |
| `EXPORT-REVEAL-ALLOWLIST-REFUSALS` | AC4-①/② |
| `EXPORT-REVEAL-CORE-TESTS` | AC6 |
| `EXPORT-REVEAL-RUST-PACKAGED` | AC4-③/AC6 |
| `EXPORT-REVEAL-POST-MERGE-HANDOFF` | AC7 |
| `EXPORT-REVEAL-REVIEW-R1` | AC1-AC7 |

**`P15`**

| 证据 | AC/Gate |
|---|---|
| `E1` 前端套件 | AC1–AC5 |
| `E2`–`E5` | AC5 |
| `E6` `SettingsPage.test.tsx` | AC1/AC2 |
| `E7` `client.p15.test.ts` | AC3 |
| `E8` 独立 Review | AC1–AC6 |

**两个 Task 都记录了「哪份证据支持哪个 AC」，只是从来没反映到勾选框里。**

## `EXPORT-REVEAL-1` AC4 为什么保留未勾

| 子项 | 状态 |
|---|---|
| ① 生产面存在 / probe 面不存在 | 达成（`ALLOWLIST-REFUSALS`） |
| ② 拒绝面逐项有测试 | 达成（同上） |
| ③ 真实「导出 → reveal → 文件管理器打开」 | **`BLOCKED`** |

Closeout 原文：

> 真实"成功导出 → reveal → 文件管理器打开"未跑通：测试 fixture 无有效 book，
> 且无头 Windows 无法取得 WebView2 窗口句柄（`0x80070578`）。

**AC 是整体的。** ③ 阻塞即 AC4 未完整达成。**三分之二不是达成**——
把 ①/② 的达成说成整体达成，正是本 Task 要清理的那类替换。

## 我的改动只动了勾选框

```
doc/tasks/EXPORT-REVEAL-1.md | 12 ++++++------
doc/tasks/P15.md             | 12 ++++++------
2 files changed, 12 insertions(+), 12 deletions(-)
```

每行只改 `- [ ]` → `- [x]`。AC 文字、frontmatter、Closeout Record、证据表一律未动。

## 请 Review 重点核对的两处

### 1. 每一个补勾是否真有依据（这是你被要求核对的核心）

Task 的 AC5 原文：

> Review 必须核对：**补勾的每一项都能在 Closeout Record 中找到依据，没有一项是凭 status 推定的。**

请逐项核对 12 个补勾，确认：
- 每一项都能指到具体的证据行（`AC/Gate` 列）或 Closeout Record 的具体条目；
- **没有一项是我根据「status: done」反推的**。

### 2. 这两个 Task 的检查一直是红的——请独立验证不是我造成的

补勾后两个 Task 的检查都 FAIL。我用 `git stash` 移除改动后对比：

| Task | 改动前 | 改动后 |
|---|---:|---:|
| `EXPORT-REVEAL-1` | **3 errors** | 3 errors |
| `P15` | **4 errors** | **3 errors** |

**请自己用 `git stash` 或 `git show HEAD:doc/tasks/P15.md` 的方式独立验证这个对比**，
确认剩余错误是既有的（LF/CRLF pin 失配、未登记过程文件、缺 manifest），
而非我引入的。

**如果你认为我应该在同一个 Task 里顺手修好那些 pin 失配，请明确说出来**——
本 Task 的 AC4 禁止我改，但如果你判断那个禁止在本情形下应当让位于「让检查变绿」，
我需要你的授权而不是自己决定。

## 明确未做

- 未改两个 Task 的任何其它字段、正文、Closeout Record。
- 未改任何证据文件、pin、Review。
- 未把 `BLOCKED` 的 AC4 勾上。
- 未修那两个 Task 既有的 3–4 个检查错误（AC4 明文禁止）。
- 未删除、未移动任何文件。

## 已声明的局限

1. **依据来自 Task 自身的证据表与 Closeout Record**，我没有重新执行任何测试验证
   AC 在技术上是否真的达成——那是原 Task 的 Review 已经做过的事，本 Task 只做记录维护。
2. **`EXPORT-REVEAL-1` AC4 的 ③ 是 `BLOCKED` 而非 `FAILED`**——它从未被声称完成过，
   本 Task 只是保持了这个状态。
3. 本次工作让两个文件**「更正确」了，但检查器仍然是红的**。这两件事不同：
   勾选是给人看的事实陈述，检查器是对证据完整性的机器判定。**修好前者不会自动修好后两者。**

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = d8ad739d2d99ac40fc96c3f2eed955eb59e516fa`。
