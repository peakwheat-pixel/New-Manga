---
id: FEA-11-MATCH-1
title: FEA-11 页匹配 pixel profile 提取与旧库 fixture（C-17 §7.3 续）
kind: implementation
governance_version: 3
status: proposed
approval: 承接自 FEA-11 Review r1 R-012（DSH 2026-11-05 裁决）；待 scope review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-MATCH-1
allowed_paths:
  - doc/tasks/FEA-11-MATCH-1.md
  - doc/reviews/FEA-11-MATCH-1-*.md
  - doc/handoffs/FEA-11-MATCH-1-*.md
  - verification/FEA-11-MATCH-1/**
---

# FEA-11-MATCH-1

承接 FEA-11 Review r1 的 R-012/R-011（AC11-3）：页匹配的 pixel profile 生产提取与旧库 fixture。

- 范围：生产 scan 的 new entry pixel profile（pixel-digest/1 算法、方向/尺寸/参数可比性）、重复 pixel occurrence 的 needs_confirmation、FEA-09 真实 v7 导入旧库 fixture、独立 match 测试（`test_source_match.py`）。
- 现状：AC11-3 在 FEA-11 中为 PARTIAL 且明确降级——生产 scan 不写 pixel profile，`unique_pixel` 仅在既有数据提供 profile 时生效；测试只有 scan 分类路径。
- 依据：`doc/reviews/FEA-11-r1.md` R-012/P1-11；C-17 §7.3。
