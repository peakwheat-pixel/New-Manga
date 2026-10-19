---
task_id: GOV-EOL-PIN-1
author: dsh
recipient: Codex
base_commit: d19e74ab4
delivery_head: 48f29726a
status: ready_for_review
---

# Handoff：GOV-EOL-PIN-1

## 为什么有这个 Task

`GOV-UNTRACKED-BACKLOG-1` 的独立 Review 提出 P1：`core.autocrlf=true` 下，
新建 linked worktree 会把该 Task 的证据文件检出为 CRLF，而 pin 记的是 LF 哈希，于是全部失配。

Review 建议补 `.gitattributes`。但该 Task 的 **AC5 明文禁止修改 `.gitattributes`**。
Codex 的 r16 裁定：

> AC5 明确禁止改 `.gitattributes`，该禁止也适用于 Codex closeout。
> Owner 遵守 AC5 是正确的。应新建独立、范围冻结的行尾治理小 Task。

本 Task 即那个小 Task。**它存在的意义是：禁止范围不能被「反正我是集成方」绕过。**

## 交付结果

| AC | 结果 | 证据 |
|---|---|---|
| AC1 追加规则 | 达成 | `ac1-ac3-eol-fix.md` |
| AC2 renormalize 与校验 | 达成 | 同上（见「无字节变化」说明）|
| AC3 worktree 复现验证 | 达成 | 同上（hash 对照）|
| AC4 只读保护 | 达成 | 只改 `.gitattributes` |
| AC5 交付与 Review | 本文 + 待 Review | — |

## 追加的规则

```gitattributes

# GOV-EOL-PIN-1: canonical evidence and handoff files are SHA-256 pinned.
# Keep LF on checkout so pins remain reproducible when core.autocrlf=true.
verification/GOV-UNTRACKED-BACKLOG-1/** text eol=lf
doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md text eol=lf
```

追加于末尾，独立成组带注释。既有四条规则未改动。

## 属性生效对照

| 时点 | `git check-attr text eol` |
|---|---|
| 追加前 | `text: unspecified`、`eol: unspecified` |
| 追加后 | `text: set`、`eol: lf` |

## 一个容易被误读的结果

`git add --renormalize` 之后 `git status --porcelain` **只显示 `.gitattributes` 被修改**，
6 份证据**一个字节都没变**。

**这是正确结果，不是「没生效」。** `text eol=lf` 约束的是**未来 checkout 的行为**，
不会重写已经合规的内容。若不说明，下一个人看到证据没变会以为 renormalize 失败。

`git ls-files --eol` 全部为：

```
i/lf    w/lf    attr/text eol=lf      	doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-inventory.json
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac2-anomalous-entries.md
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac3-references.json
i/lf    w/lf    attr/text eol=lf      	verification/GOV-UNTRACKED-BACKLOG-1/ac4-worktree-mirror-guide.md
```

## worktree 复现验证（AC3 的关键）

在提交 `76e4a1544` 后新建一次性 linked worktree：

| 项 | 结果 |
|---|---|
| worktree 内 `ls-files --eol` | `i/lf w/lf attr/text eol=lf` |
| worktree 内证据 SHA-256 | `A86B42336085345E0D27EDF5664061AAC53D4337CAF98E0B23A80CA62D883E6A` |
| 主 checkout 同一文件 | **完全相同** |

探针已 `git worktree remove --force` + `prune`，路径确认不存在。

## 请 Review 重点核对的两处

### 1. 请自己复现 worktree 验证

不要只读上表。请新建一次性 worktree，确认：
- 规则确实生效（`git check-attr` 与 `ls-files --eol`）；
- 证据文件在主 checkout 与 worktree 中字节一致。
验证完请清理。

**特别注意**：若你的环境 `core.autocrlf` 与本机不同，结果可能不同。
请报告你的 `git config core.autocrlf` 实测值。

### 2. 这个修复是否真的解除了 `GOV-UNTRACKED-BACKLOG-1` 的 P1

P1 的原始表述是「跨 worktree 行尾转换导致 Canonical Evidence SHA-256 失配」。
本 Task 修的是**该 Task 的两条路径**。请判断：

- 这个范围是否足够？还是说**全仓库**所有 hash-pinned 证据都该有同类规则？
- 若是后者，本 Task 是否应扩围，还是另立 Task？

**这是我最希望你独立判断的一点**——我只修了被点名的那一个 Task，可能过窄。

## 明确未做

- 未改任何证据文件内容。
- 未改 `tools/governance/`、其它 Task、Plan/STATUS 的节点状态。
- 未改既有 `.gitattributes` 规则。
- 未删除、未移动任何文件。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = d19e74ab4dd9eb0fb15c6a776426df06fe174694`。
