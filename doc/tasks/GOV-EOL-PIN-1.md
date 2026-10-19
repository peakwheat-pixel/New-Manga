---
id: GOV-EOL-PIN-1
title: 为 hash-pinned 证据固定 LF 行尾
kind: governance
governance_version: 2
status: in_progress
approval: codex_closeout_backlog_r16_separate_task_required
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: [GOV-UNTRACKED-BACKLOG-1]
base_commit: 94efecc75a3132d6f4b1e76fc66a18c9f2912e8b
branch: null（单一 .gitattributes 改动，主线直接执行）
worktree: null（不建 linked worktree）
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EOL-PIN-1
allowed_paths:
  - .gitattributes
  - doc/tasks/GOV-EOL-PIN-1.md
  - verification/GOV-EOL-PIN-1/
  - doc/handoffs/GOV-EOL-PIN-1-*.md
  - doc/reviews/GOV-EOL-PIN-1-*.md
---

# GOV-EOL-PIN-1：为 hash-pinned 证据固定 LF 行尾

## 来源与目标

`GOV-UNTRACKED-BACKLOG-1` 的独立 Review 提出 P1：`core.autocrlf = true` 下，
新建 linked worktree 会把该 Task 的证据文件检出为 CRLF，而 Canonical Evidence pin 的
SHA-256 是 LF 哈希，于是 pin 全部失配。

该 Review 建议在 `.gitattributes` 补齐规则，但 `GOV-UNTRACKED-BACKLOG-1` 的 AC5
**明文禁止修改 `.gitattributes`**。Codex 的 closeout 裁定（r16）确认：

> AC5 明确禁止改 `.gitattributes`，该禁止也适用于 Codex closeout。Owner 遵守 AC5 是正确的。
> 应新建独立、范围冻结的行尾治理小 Task。

本 Task 即该小 Task。范围**只有一件事**：为已 hash-pinned 的证据路径固定 LF。

## 为什么必须单独做

这不是「顺手修一下」可以处理的类型：

1. 它修改的是**仓库级属性文件**，影响所有 Agent 的检出行为；
2. 它改变的是「未来每次 checkout」的行为，不是一次性数据；
3. 若允许它在被禁止的 Task 内完成，AC5 就变成了可绕过的建议而非约束。

把它单独立项，是对「禁止范围」这一机制的尊重。

## 先例

`.gitattributes` 已有三处同类规则，本 Task 沿用同一模式：

```
doc/handoffs/SEC-FIX-PATH-ECHO-1-c52ce46.md text eol=lf
tools/governance/check.ps1 text eol=lf
verification/P19-UI-MANIFEST-VIEW-1/** text eol=lf
```

## Acceptance Criteria

- [x] **AC1 追加规则**：在 `.gitattributes` 末尾追加带注释的独立规则组，为
  `verification/GOV-UNTRACKED-BACKLOG-1/**` 与 `doc/handoffs/GOV-UNTRACKED-BACKLOG-1-*.md`
  固定 `text eol=lf`。不改动既有任何规则。
- [x] **AC2 renormalize 与校验**：对上述路径执行 `git add --renormalize`，
  用 `git ls-files --eol` 确认结果为 `i/lf w/lf`，
  并用 `Get-FileHash` 或 `sha256sum` 确认 6 份证据文件的字节与
  `GOV-UNTRACKED-BACKLOG-1` 已登记的 pin **完全一致**（预期不变）。
- [x] **AC3 worktree 复现验证**：新建一次性 linked worktree，确认
  `GOV-UNTRACKED-BACKLOG-1` 的证据 pin 在该 worktree 中**不再失配**（修复前应失配）。
  验证后删除探针 worktree。
- [x] **AC4 只读保护**：不改任何证据文件内容、不改其它 Task、不改 `tools/governance/`。
  只改 `.gitattributes`。
- [ ] **AC5 交付与 Review**：入库验证输出（含 `git ls-files --eol` 与 hash 对照）；
  生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。

## 允许修改范围

- `.gitattributes`：仅追加规则。
- `verification/GOV-EOL-PIN-1/`：验证输出。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- 不改任何已入库证据文件的内容。
- 不改 `tools/governance/`、其它 Task、Plan/STATUS 的节点状态。
- 不改既有 `.gitattributes` 规则。
- 不删除、不移动任何文件。

## 测试与验证

```powershell
git check-attr text eol -- verification/GOV-UNTRACKED-BACKLOG-1/ac1-ac3-composition-and-references.md
git ls-files --eol -- verification/GOV-UNTRACKED-BACKLOG-1/ doc/handoffs/GOV-UNTRACKED-BACKLOG-1-60970cf9d.md
pwsh -NoProfile -File tools/governance/check.ps1
```

## Canonical Evidence

交付时登记验证输出、`.gitattributes` diff、worktree 复现对照、Handoff、Review。

## Resource Manifest

本 Task 不处置资源，只追加行尾规则。交付时逐项登记 `.gitattributes` 与证据目录。

## Closeout Record

- 状态：`in_progress`。由 DSH 直接执行（单一文件改动，不建 worktree）。
