---
id: FEA11-RECOVERY-ROOT-PATH-1
title: 定位恢复路径把 registry root 当容器（产品缺陷 E-9，P2）
kind: evidence
governance_version: 3
status: done
follow_up: E9-RECOVERY-PATH-FIX-1（typed 拒绝已实施；真修需 UNFREEZE）
disposition: "承接 MINT-FAILURE-DIAG-1：UnauthorizedAccessException 指向 fixture root 目录，已定位为产品缺陷"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MINT-FAILURE-DIAG-1
base_commit: c68a67216
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA11-RECOVERY-ROOT-PATH-1
allowed_paths:
  - doc/tasks/FEA11-RECOVERY-ROOT-PATH-1.md
  - doc/reviews/FEA11-RECOVERY-ROOT-PATH-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/FEA11-RECOVERY-ROOT-PATH-1/**
---

# FEA11-RECOVERY-ROOT-PATH-1（定位完成，未修复）

## 结论

**产品缺陷 `E-9`（P2）**：`SourceOperationCoordinator.MintRecoveryGrantsAsync` 在恢复授权时
把 **registry root（目录）** 当作**容器路径**传给 `IssueForRecoveryAsync`，
对 `zip`/`cbz`/`pdf`/`image` 来源必然触发 `DescribeContainer(目录)` 失败。

`sourceKind == "folder"` 时碰巧成立 —— 这正是它长期未被发现的原因。

## 证据

- 完整调用栈（实测）：`DescribeContainer ← IssueLockedAsync ← IssueAsync ← IssueForRecoveryAsync
  ← MintRecoveryGrantsAsync ← AcknowledgeAsync ← HostRuntime.SourceOperationCompletionAsync`。
- 实测异常：`UnauthorizedAccessException: Access to the path '...\r4a-production-<guid>' is denied.`
  （路径是 **root 目录**，不是 `source-v2.zip`）。
- 代码：`roots[0]` 传给 `sourcePath` 形参，而 `sourceKind` 来自 Core 的 scanTargets（实测 `"zip"`）。
- 注释自陈风险："otherwise the source path would be guessed" —— 但"恰好一个 root"解决不了
  "root ≠ 容器"的语义错位。

## 未做

- **未修复**：恢复路径的权威来源需 DSH 裁决（journal? plan materialization? 还是 typed 拒绝）。
- **未验证其它 sourceKind**：zip 之外（cbz/pdf/image）是否同样受害，需逐个复跑。
- 带 opt-in 三类基线仍 **12 passed / 1 failed**；条件 3 仍不判 MET。
