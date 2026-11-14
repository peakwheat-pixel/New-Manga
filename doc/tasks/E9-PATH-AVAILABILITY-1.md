---
id: E9-PATH-AVAILABILITY-1
title: 容器路径在 journal 写入点是否可得 —— 结论不可得，只剩扩 Core 或接受限制
kind: evidence
governance_version: 3
status: done
disposition: "回答 E9-CARRIER-CORRECTION-1 的问题 1：六个写入入口全都没有容器路径"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E9-CARRIER-CORRECTION-1
base_commit: ed7c323fe
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/E9-PATH-AVAILABILITY-1
allowed_paths:
  - doc/tasks/E9-PATH-AVAILABILITY-1.md
  - doc/reviews/E9-PATH-AVAILABILITY-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/E9-PATH-AVAILABILITY-1/**
---

# E9-PATH-AVAILABILITY-1

## 结论

**六个 journal 写入入口全都没有容器路径**（`Begin` / `Authorize` / `MarkCommitted` /
`payload` 的 `authorization`+`grant_ids` / `registryAuthorizations[]` / `HostAuthorizationMinter.Mint`）。

唯一知道路径的是 `SourceReadCoordinator.IssueLockedAsync` 的 `sourcePath`（Run 授权链,`:564`），
与 operation journal 之间**没有传递通道**。

## 只剩两个选项

- **选项 2（扩 Core）**：改 wire 契约 + Python Core；**跨职责**（Host 授权材料进 Core）。
- **选项 3（接受为能力限制）**：保持 typed 拒绝 + 文档/UI 明确"仅 folder 支持崩溃恢复"。**零代码**。

## DSH 技术判断

倾向选项 3（成本收益不成比例）。**但这是产品取舍**，应派 codex/zcode 裁决；
上一轮 codex 因 Windows 740 无法读代码，该裁决**尚未作出**。

## 未做

未改代码；未派新裁决；带 opt-in 三类基线仍 12/1；条件 3 仍不判 MET。
