---
id: FEA11-ENTRY-MISSING-1
title: SOURCE_ENTRY_MISSING 归因（部分）—— 已排除种子/路径，被兜底映射掩盖
kind: evidence
governance_version: 3
status: blocked
disposition: "剩余失败无法定论：MapMintFailure 的 _ => 兜底丢弃了内层异常类型"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - FEA11-SEED-PIXEL-1
base_commit: 414e3e8d1
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA11-ENTRY-MISSING-1
allowed_paths:
  - doc/tasks/FEA11-ENTRY-MISSING-1.md
  - doc/reviews/FEA11-ENTRY-MISSING-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/FEA11-ENTRY-MISSING-1/**
---

# FEA11-ENTRY-MISSING-1（blocked：无法定论）

## 结论

失败点在 `SourceReadCoordinator.DescribeContainer` 的 `FileStream` 打开处，
但**内层异常类型被 `MapMintFailure` 的 `_ =>` 兜底丢弃**，因此"文件不存在 / 无权限 / 其它"不可区分。

**已排除**：种子未生成 `new_zip`、路径非绝对、schema 版本不符。
**未定论**：`FileStream` 打开的具体失败原因。

## 为什么标 blocked

要定论需要**内层异常类型**，而它被产品代码丢弃。**不是我缺实物，也不是环境缺失**，
而是**产品诊断信息不足**导致的"证据不可得"。

已给出的建议（未实施）：
1. 产品侧 `MapMintFailure` 保留 `innerException` / 在兜底分支保留原始类型（**诊断性**改动，不改错误码语义）；
2. 测试侧先 `Assert.True(File.Exists(newZip))` 并打印路径，把"文件不存在"从"其它"里分离。

## 边界

- 带 opt-in 三类基线仍 **12 passed / 1 failed**。
- 条件 3 仍不判 MET。
