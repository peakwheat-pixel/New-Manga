# AC2 / AC3 — 补勾结果与既有检查错误的区分

**Task**: GOV-SOURCE-RECORDS-1 · **基线**: `32f95fdf9`

## 一、补勾结果

| Task | 补勾 | 保留未勾 |
|---|---:|---:|
| `EXPORT-REVEAL-1` | **6**（AC1/2/3/5/6/7） | **1（AC4）** |
| `P15` | **6**（AC1–AC6） | 0 |
| **合计** | **12** | **1** |

依据逐项见 `ac1-tracing.md`。

### `EXPORT-REVEAL-1` AC4 为什么保留未勾

AC4 有三个子项：

| 子项 | 状态 | 依据 |
|---|---|---|
| ① 生产面存在 / probe 面不存在 | **达成** | `EXPORT-REVEAL-ALLOWLIST-REFUSALS`（AC/Gate = AC4-①/②） |
| ② 拒绝面逐项有测试 | **达成** | 同上 |
| ③ 真实"导出 → reveal → 打开"往返 | **`BLOCKED`** | Closeout 原文：「未跑通：fixture 无有效 book，且无头 Windows 无法取得 WebView2 句柄（`0x80070578`）」 |

**AC 是整体的，③ 阻塞即 AC4 未完整达成。** 保留未勾，不加注把 ①/② 的达成说成整体达成。

## 二、我的改动只动了勾选框

`git diff --stat`：

```
doc/tasks/EXPORT-REVEAL-1.md | 12 ++++++------
doc/tasks/P15.md             | 12 ++++++------
2 files changed, 12 insertions(+), 12 deletions(-)
```

**每行只改 `- [ ]` → `- [x]`**，AC 文字、frontmatter、Closeout Record、证据表一律未动。

## 三、必须单独说明：这两个 Task 的检查一直是 FAIL 的

补勾后跑检查，两个 Task 都报错。我原以为是自己改坏了，**验证后发现全部是既有缺陷**：

用 `git stash` 移除我的改动后重跑：

### `EXPORT-REVEAL-1`

| | 错误数 |
|---|---:|
| **我的改动前** | **3** |
| 我的改动后 | **3** |

三条完全相同：

1. `Evidence SHA-256 不匹配：doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
2. `DONE evidence_dir 含未登记文件：verification/EXPORT-REVEAL-1/post-merge-packaged-capture-error.log` 等
3. `DONE 不能保留未完成 Acceptance Criteria`

### `P15`

| | 错误数 |
|---|---:|
| **我的改动前** | **4** |
| 我的改动后 | **3** |

前三条与上面同类，第四条（`Resource manifest 不存在：verification/P15/resource-manifest.json`）仍在。

**我的改动使 `P15` 的错误从 4 减到 3**（第 3 条「不能保留未完成 AC」因补勾而消失），
`EXPORT-REVEAL-1` 则因 AC4 合法保留而错误数不变。

**结论：本 Task 没有引入任何新错误。**

## 四、这些既有缺陷是什么（不在本 Task 范围）

| 缺陷 | 涉及 | 性质 |
|---|---|---|
| **Evidence SHA-256 不匹配** | `EXPORT-REVEAL-1`（契约文件）、`P15`（测试源文件） | **行尾（LF↔CRLF）导致的 pin 失配**，与本会话 `GOV-EOL-PIN-1` 处理的同一类问题 |
| **evidence_dir 含未登记文件** | 两个 Task 均有 | 历史遗留的过程文件未登记 |
| **Resource manifest 不存在** | `P15` 引用 `verification/P15/resource-manifest.json`，该文件缺失 | 引用悬空 |
| **DONE 保留未完成 AC** | `EXPORT-REVEAL-1` AC4 | **这是真实情况**，不是缺陷——AC4-③ 确实 BLOCKED |

**本 Task 的 AC4 明文禁止改这些**（"不改 status 与其它字段"、"不改任何证据文件、pin、Review"）。

因此我**记录而不修**。它们属于另一类治理债，若要处理需另立 Task。

## 五、一个必须承认的边界

我这次的工作**让这两个文件"更正确"了（勾选状态如实反映事实），但它们的治理检查仍然是红的**。

这看起来像是「做了没用」。但两者是不同的东西：

- **勾选状态**是给人看的**事实陈述**——错的勾选会误导协作者；
- **检查器结果**是机器对**证据完整性**的判定——它红是因为 pin 和登记有问题。

**修好前者不会自动修好后两者**，而且本 Task 被明确禁止碰它们。

**把这一点写清楚，比让检查变绿更重要。** 如果有人只看「检查是否 PASS」就认为本 Task 没做成，这份文档能解释为什么。
