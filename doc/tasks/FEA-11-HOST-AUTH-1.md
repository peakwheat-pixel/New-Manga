---
id: FEA-11-HOST-AUTH-1
title: FEA-11 Host durable authorization 自签与编排（C-17 §5.2 续）
kind: implementation
governance_version: 3
status: proposed
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；待 scope review
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
evidence_dir: verification/FEA-11-HOST-AUTH-1
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-1.md
  - doc/reviews/FEA-11-HOST-AUTH-1-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-1-*.md
  - verification/FEA-11-HOST-AUTH-1/**
---

# FEA-11-HOST-AUTH-1

承接 FEA-11 Review r1 的 P0-1：Host 侧完整 HostAuthorization 生成与编排。

- 范围：Host canonical 摘要规范（C-17 §5.2：canonical-json/1 + sha256）、HostAuthorization 六字段生成（host_receipt_id/operation_id/request_digest/authorization_digest/authorizations/authorized_at）、先 Registry durable 授权再 journal、operation_id 由 Host 生成并注入 ApplyRequest、Host→Core 集成测试（崩溃点/ACK 重发/恢复）。
- 依据：`doc/reviews/FEA-11-r1.md` P0-1；C-17 v1.0 FROZEN §3.2/§5.2。
- 状态：proposed（DSH 2026-11-05 裁决承接；FEA-11 的 Host 侧当前为透传实现，Core 侧已完整）。
