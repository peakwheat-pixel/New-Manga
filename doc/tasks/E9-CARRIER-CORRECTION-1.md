---
id: E9-CARRIER-CORRECTION-1
title: 更正 E-9 载体假设（journal 是 DPAPI 文件非 SQLite）+ 新约束（Authorize 不知路径）
kind: evidence
governance_version: 3
status: done
disposition: "上一轮误判需要 schema 迁移；本轮更正：无需迁移，但 Authorize 链拿不到容器路径"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E9-PATH-CARRIER-STUDY-1
base_commit: 52bdf9343
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/E9-CARRIER-CORRECTION-1
allowed_paths:
  - doc/tasks/E9-CARRIER-CORRECTION-1.md
  - doc/reviews/E9-CARRIER-CORRECTION-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/E9-CARRIER-CORRECTION-1/**
---

# E9-CARRIER-CORRECTION-1

## 1. 更正（我上一轮判断错了）

上一轮 `E9-PATH-CARRIER-STUDY-1` 暗示修复需要 **schema 迁移**。**错**：
C# 的 journal 是 **DPAPI 加密的 JSON 文件**（`Write` 用 `JsonSerializer.SerializeToUtf8Bytes` + `Protect`，
`Read` 用 `Unprotect`），**不是 SQLite 表**。加字段无需迁移，旧文件可反序列化（缺字段 → null）。

`schema.py:798` 的 `source_operations` 是 **Python Core 侧**的另一份记录（上一轮曾误称
`source_operation_journal`），与 C# journal 文件是两套东西。

## 2. 新约束

全仓 `_operations.Authorize(...)` **只有 1 个调用点**（`HostOperationOrchestrator.cs:301`，retry-failed 流程），
其上下文**没有**容器路径；`roots` 正是错的 registry root。

真正知道路径的是 `SourceReadCoordinator.IssueLockedAsync` 的 `sourcePath`（grant 发行链），
与写 journal 是两条链。

**⇒ 加字段容易，难在"哪个写入点能拿到真实容器路径"。**

## 3. 待 DSH 裁决的三个问题

见证据 README §3。**不能用局部补丁糊过去。**

## 4. 未做

未改代码；带 opt-in 三类基线仍 12/1；条件 3 仍不判 MET。
