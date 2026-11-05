---
id: FEA-11-HOST-AUTH-1
title: FEA-11 Host durable authorization 自签与编排（C-17 §5.2 续）
kind: implementation
governance_version: 3
status: in_progress
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；用户 2026-11-05 授权启动；scope 由本卡 allowed_paths + DSH 窄批登记
suggested_owner: codex
owner: dsh（2026-11-05 用户授权启动）
reviewer: 独立上下文 fresh subagent（doc/reviews/FEA-11-HOST-AUTH-1-r1.md）
depends_on:
  - FEA-11-PREREQ-1
base_commit: 7ab9eea87
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-HOST-AUTH-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/CanonicalJson.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostAuthorizationMinter.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/HostOperationOrchestrator.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CanonicalJsonTests.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/HostAuthorizationMinterTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs
  - doc/TASK_LEDGER.md
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

## 实施证据与 AC 状态（DSH，2026-11-05）

- AC1 MET：`CanonicalJson.cs` + `CanonicalJsonTests` 4/4（与 Core canonical_bytes 逐字节一致的跨实现向量）。
- AC2 MET：`HostAuthorizationMinter`（六字段/排序/canonical digest）+ `HostAuthorizationMinterTests` 3/3；HostRuntime 注入 ApplyRequest（`Fea11HostAuthTests.Apply_InjectsTheHostMintedAuthorizationNotTheCallers`）。
- AC3 PARTIAL（DSH 裁决）：`HostOperationOrchestrator` 顺序（Mint→Registry.Authorize(roots)→journal→Core→MarkCommitted）+ `Fea11HostAuthTests` 5/5（注入/失败留 host-authorized/capability 门/顺序探针/非法 plan_digest 零 journal）。**剩余缺口登记为 limitation**：①完整 HostRuntime→Core 端到端（真实 sidecar + dispatcher 接线）无自动化测试；②ACK 重发/崩溃点矩阵自动化属 FEA-11 L-8 测试债务（IPC 已覆盖 6 字段 ACK 与幂等重放）；③失败后「新 operation_id 重试」语义由 plan 幂等保证（每次 Apply mint 新 op id；`Begin` 拒绝复用避免覆盖终态）。
- AC4 PARTIAL：用户已接受 Core-only limitation（FEA-11 `closed_with_limitations`）；本卡完成 P0-1 实际闭合，待本卡复审（r2）判定。
- 门禁：`verification/FEA-11-HOST-AUTH-1/logs/gates.log`（pytest 3051/0/10、.NET 1370/0、IPC 复跑 3/3、check PASS、pins 18/18；含 IPC flaky 说明）。
- 已知限制：HostRuntime 级端到端（真实 sidecar + UI 命令面）未自动化；ACK 重发/崩溃点矩阵未自动化；`source.read/1` 缺失时 capability item 的 reason 语义待收口（FEA-11 r6 P2-4 遗留）；IPC 套件为 Core 直连（P2-9）。

## DSH 裁决与 limitation 登记（r1 处置后）

- **P1-2 已修**：allowed_paths/owner/base_commit/reviewer/approval 补齐（见 front matter 与本卡窄批节）。
- **P2-6（journal 形状）**：Host journal 内部字节格式不强制等于冻结 `HostJournal` DTO；Core 侧 `source_get_operation` receipt 为主证据；差异登记为内部实现选择，不做 DTO 重写。
- **P2-7（ACK fresh 授权）**：ACK 发送 journal 原始 authorization；Core `_verify_fresh` 已核对 operation/request digest/host_receipt/registry 覆盖/identity/generation，fresh 重新签名登记为后续增强（不改变当前安全边界）。
- **P2-8/P2-9/P2-10**：证据卫生（失败 trx 归档）、IPC flake 定位、CORE_UNAVAILABLE 闭集边界登记为测试债务/deferral。
- **AC3 剩余**：见上（e2e/崩溃点/ACK 重发自动化 → limitation）。

## Acceptance Criteria

- [x] **AC1**：Host 侧 canonical-json/1 + sha256 摘要实现，与 Core 冻结公式逐字节一致（跨实现测试向量 4/4）。 <<MET>>
- [x] **AC2**：HostAuthorization 六字段由 Host 生成，operation_id 由 Host 生成并注入 ApplyRequest（`HostAuthorizationMinter` + 单测 3/3：六字段/排序/canonical digest/唯一性；注入在 HostRuntime 实现）。 <<MET>>
- [ ] **AC3**：先 `SourceAccessRegistry.Authorize` durable 再 journal（顺序断言 + 崩溃点）；Host→Core 集成测试覆盖 ACK 重发/恢复/失败。 <<PARTIAL: 顺序由 HostOperationOrchestrator 保证并有 3 项测试（注入/失败留 host-authorized/capability 门）；完整 HostRuntime→Core 端到端与 ACK 重发待补>>
- [ ] **AC4**：FEA-11 r3 复审接受本卡为 P0-1 闭合路径（或产品方显式接受 Core-only limitation）。 <<PARTIAL: 用户已接受 Core-only limitation（FEA-11 closed_with_limitations）；本卡完成 P0-1 实际闭合，待本卡独立 Review>>
