---
id: FEA-11-AC4-GAPS-1
title: FEA-11 AC11-4 证据收口（并发 apply / DB 失败 / 第三区域 BaseRevision 冲突）
kind: implementation
governance_version: 3
status: proposed
approval: 承接自 FEA-11 Review r4 P2-11（DSH 2026-11-05 裁决）；待 scope review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-PREREQ-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-AC4-GAPS-1
allowed_paths:
  - doc/tasks/FEA-11-AC4-GAPS-1.md
  - doc/reviews/FEA-11-AC4-GAPS-1-*.md
  - doc/handoffs/FEA-11-AC4-GAPS-1-*.md
  - verification/FEA-11-AC4-GAPS-1/**
  - tests/fea11/test_source_sync.py
  - src/application/sources/service.py
  - src/infrastructure/sqlite/source_sync.py
---

# FEA-11-AC4-GAPS-1

承接 FEA-11 Review r4 P2-11：AC11-4 仍缺的三类证据。

## Acceptance Criteria

- [ ] **AC1**：并发 apply（两线程/两连接）仅一个成功、另一个 typed 冲突且零业务写。 <<PARTIAL: 待实施>>
- [ ] **AC2**：DB 失败注入下 apply 整批回滚（事务原子性证据）。 <<PARTIAL: 待实施>>
- [ ] **AC3**：第三区域 BaseRevisionId 冲突 → apply 拒绝且零写（其余区域不变）。 <<PARTIAL: 待实施>>
