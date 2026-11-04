---
id: FEA-11-HOST-AUTH-1
title: FEA-11 Host durable authorization 自签与编排（C-17 §5.2 续）
kind: implementation
governance_version: 3
status: in_progress
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；待 scope review
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
evidence_dir: verification/FEA-11-HOST-AUTH-1
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-1.md
  - doc/reviews/FEA-11-HOST-AUTH-1-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-1-*.md
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/SourceSyncJournalTests.cs
  - verification/FEA-11-HOST-AUTH-1/**
---

# FEA-11-HOST-AUTH-1

承接 FEA-11 Review r1 的 P0-1：Host 侧完整 HostAuthorization 生成与编排。

- 范围：Host canonical 摘要规范（C-17 §5.2：canonical-json/1 + sha256）、HostAuthorization 六字段生成（host_receipt_id/operation_id/request_digest/authorization_digest/authorizations/authorized_at）、先 Registry durable 授权再 journal、operation_id 由 Host 生成并注入 ApplyRequest、Host→Core 集成测试（崩溃点/ACK 重发/恢复）。
- 依据：`doc/reviews/FEA-11-r1.md` P0-1；C-17 v1.0 FROZEN §3.2/§5.2。
- 状态：proposed（DSH 2026-11-05 裁决承接；FEA-11 的 Host 侧当前为透传实现，Core 侧已完整）。

## Acceptance Criteria

- [x] **AC1**：Host 侧 canonical-json/1 + sha256 摘要实现，与 Core 冻结公式逐字节一致（跨实现测试向量 4/4）。 <<MET>>
- [ ] **AC2**：HostAuthorization 六字段由 Host 生成，operation_id 由 Host 生成并注入 ApplyRequest。 <<PARTIAL: 已实现（canonical + 自签 + 注入），Host 级集成测试待补>>
- [ ] **AC3**：先 `SourceAccessRegistry.Authorize` durable 再 journal（顺序断言 + 崩溃点）；Host→Core 集成测试覆盖 ACK 重发/恢复/失败。 <<PARTIAL: 顺序已实现（registry.Authorize → Begin → Authorize）；崩溃点/集成测试待补>>
- [ ] **AC4**：FEA-11 r3 复审接受本卡为 P0-1 闭合路径（或产品方显式接受 Core-only limitation）。 <<PARTIAL: 待实施>>
