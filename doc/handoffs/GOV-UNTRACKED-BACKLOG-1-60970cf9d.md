---
task_id: GOV-UNTRACKED-BACKLOG-1
author: dsh
recipient: Codex
base_commit: 6ee8c87b1
delivery_head: 60970cf9da4b2852aeaf5b64f0c9e80883189684
status: ready_for_review
---

# Handoff：GOV-UNTRACKED-BACKLOG-1

## 交付结果

把「1233 个未入库文件」这句流传已久的话，换成三个实测数字与一份可复用指南。

| AC | 结果 | 证据 |
|---|---|---|
| AC1 构成与来源核实 | 达成 —— 1591 文件按目录/来源分类 | `ac1-ac3-composition-and-references.md` |
| AC2 两个异常条目处置 | 达成 —— 指纹、来源推断、引用、结论、安全读取法 | `ac2-anomalous-entries.md` |
| AC3 引用关系核查 | 达成 —— 137 被引用 / 1454 未引用 | `ac3-references.json` |
| AC4 边界化文档 | 达成 —— **最小镜像集 3 个文件** | `ac4-worktree-mirror-guide.md` |
| AC5 只读保护 | 达成 —— 积压 1591 未增未删 | 见下「基线证明」 |
| AC6 交付与 Review | 本文 + 待 Review | — |

## 三个核心数字

| 项 | 值 |
|---|---|
| 未入库文件 | **1591** |
| `verification/` 占比 | **92%**（1470 项，其中 `P02` 独占 1072） |
| 被已入库文档引用 | **137**（全部 load-bearing，一律留原路径） |

**流传的「1233」既不是 `git status` 条目数（1235）也不是文件数（1591）**，来源不明。

## 本轮最有价值的产出：最小镜像集

新建 linked worktree 会看到 **6 个与本 Task 无关的治理错误**——同一 HEAD 在主 checkout 是 PASS。
我在一次性 worktree 里复现了全部 6 个，并证明最小绕过只需复制 **3 个文件**：

```
doc/WORKSPACE_GOVERNANCE.md
archive/history/2026-10-12/README.md
archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md
```

复制后立即 **PASS (1 warnings)**。

**本会话早期我用的是 33 个**（整个 `doc/` + `archive/`）。那是过度的：
过度镜像污染 `git status`，反而让人怀疑动了不该动的文件。

根因：这 3 个文件在主 checkout 是 **untracked**，worktree 只检出追踪文件；
`doc/WORKSPACE_GOVERNANCE.md` 还是检查器 11 个必需静态文件之一。

## 基线证明（AC5）

```
总未入库 1595 = 积压 1591 + 本 Task 证据 4
```

证据入库后积压仍为 **1591**，未增未删。复跑：

```powershell
git ls-files --others --exclude-standard | Where-Object { $_ -notlike 'verification/GOV-UNTRACKED-BACKLOG-1/*' }
```

## 两个异常条目

### `CON`（34778 bytes，SHA-256 `8241373A...C8714`）

Windows **保留设备名**下的真实 CSV 哈希清单——275 行，全部指向 `G:\CODEX\sfx_review\`。
**文件名畸形，内容真实。不得删除。** 建议后续 Task 归档改名，本 Task 不动。

### 长句名文件（72 bytes）

内容只有一行路径。某脚本把**路径参数**写到了**输出文件名**的位置。纯 bug 产物。

两者都**没有任何已入库文档引用**——唯一的提及是本 Task 自己的文件。

## 请 Review 重点核对的三处

### 1. 我修正了自己一个凭空的断言（最需要独立验证）

写 AC2 时我先写下「普通 `Get-Content` 会去读控制台设备而不是 `CON` 文件」，**没有验证**。
实测结果相反：

| 方法 | 结果 |
|---|---|
| `Get-Content -LiteralPath "G:\CODEX\New Manga\CON"` | **275 行** |
| `Get-Content -LiteralPath "\\?\G:\CODEX\New Manga\CON"` | 275 行 |
| 两者 SHA-256 | **完全相同** |

保留名遮蔽在该环境**没有发生**。已在文件内就地更正并说明理由。

请独立验证这一点（`Get-FileHash` 对比两种路径），并判断：
把这段「我先说错了、后改为实测」的过程留在交付文件里，是否恰当——还是该删掉错误版本只留结论。

### 2. 最小镜像集是否真的只需 3 个

请自己新建一个 worktree（或复用已删的 probe 路径）验证：
未镜像任何文件时应正好 6 个错误，复制那 3 个后应为 PASS。
**不要只看我的结论。**

### 3. 1454 个无引用文件是否可以「不管」

AC3 判出 1454 项无已入库文档引用，本 Task 明确**不处置**。
请判断这个边界是否恰当——或者认为无引用即可判为「可删除」，本 Task 应给出该结论。

## 明确未做

- **未删除、未移动、未归档、未重命名**任何积压文件（AC5）。
- 未改 `.gitignore`、`.gitattributes`、`tools/governance/`。
- 未修改任何其它 Task、pin、evidence 或资源。
- 未对 1454 个无引用文件给出可删除结论。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 60970cf9da4b2852aeaf5b64f0c9e80883189684`。
Review 通过后交 Codex 集成与 closeout。
