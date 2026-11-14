---
id: E9-LIMITATION-DOC-1
title: E-9 已知限制登记（独立文件，不动被 pin 的 C-17）
kind: doc
governance_version: 3
status: done
disposition: "执行 ZCode 裁决的最小产品动作：文档。因 C-17 被 pin 覆盖，改用独立登记文件"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - E9-KNOWN-LIMITATION-TESTS-1
base_commit: 2d34914c2
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/E9-LIMITATION-DOC-1
allowed_paths:
  - doc/tasks/E9-LIMITATION-DOC-1.md
  - doc/reviews/E9-LIMITATION-DOC-1-*.md
  - doc/reviews/E9-KNOWN-LIMITATION-REGISTER.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/E9-LIMITATION-DOC-1/**
---

# E9-LIMITATION-DOC-1

## 交付

新建 `doc/reviews/E9-KNOWN-LIMITATION-REGISTER.md`：按 ZCode 核实的真实口径登记限制，
并引用 C-17（冻结契约）、E-9 finding、两份证据目录。

## 为什么不动 C-17

核实到 `doc/plan/FEA-CONTRACT-FROZEN-C17.md` **被 pin 覆盖**
（附录写明三指纹与 `truth 17 OK + C17 OK = 18/18`；`verify_pins.ps1` 动态构造
`doc/plan/FEA-CONTRACT-FROZEN-$id.md`）。**改它会使 18/18 变红**。

本限制不需要改契约语义（契约要求"恢复需要容器路径"，产品只是暂时无法提供），
故用独立登记文件承载，**不动冻结字节**。

## 表述纪律

**不得**写"仅崩溃恢复不可用" —— ZCode 核实**正常 ACK 同样不可用**（同一 re-mint 路径）。

## 未做

未改 C-17（有意）；未实现 mint-time 路径映射；未跑测试（只加文档）。
