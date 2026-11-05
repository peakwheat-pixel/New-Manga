---
id: FEA-11-HOST-AUTH-1
title: FEA-11 Host durable authorization 自签与编排（C-17 §5.2 续）
kind: implementation
governance_version: 3
status: in_progress
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；用户 2026-11-05 授权启动；scope 由本卡 allowed_paths + DSH 窄批登记
suggested_owner: codex
owner: dsh（2026-11-05 用户授权启动）
reviewer: 独立上下文 fresh subagent（r1/r2/r3；报告 doc/reviews/FEA-11-HOST-AUTH-1-r1.md…-r3.md）
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
  - apps/desktop-avalonia/src/NewManga.Host/Sources/HostErrorCodes.cs
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

- AC1 MET：`CanonicalJson.cs` + `CanonicalJsonTests` 5/5（含 non-BMP）（跨实现向量：request/authorization/mixed/escapes + non-BMP code-point 排序；sha256 由 Python Core 生成）。
- AC2 MET：`HostAuthorizationMinter`（六字段/排序/canonical digest）+ `HostAuthorizationMinterTests` 6/6（含固定 id 外部向量）；HostRuntime 注入 ApplyRequest（`Fea11HostAuthTests.Apply_InjectsTheHostMintedAuthorizationNotTheCallers`）。
- AC3 PARTIAL（r4 返修后）：typed 业务拒绝（歧义集合外）→ journal **failed + error_code/retryable**（durable，retryable 取 Core 值）；歧义/传输失败 → host-authorized + `requestId=operation_id` 供恢复；**同 operation/request digest 重试已实现且符合 §3.2 行 163**：`RetryAsync` 锁后重读 Registry → `Authorize` durable → **重新 mint 新 HostAuthorization 并原子落盘**（AuthorizationJson/Digest/HostReceiptId 更新）→ dispatch；typed 拒绝再落 failed；已提交 failed 拒绝 retry（走 recover）；non-retryable 拒绝。`Fea11HostAuthTests` 19/19（14 方法）。**剩余 limitation**：①完整 HostRuntime→Core 端到端（真实 sidecar + dispatcher 接线；retry 目前是 Host 编排 API，dispatcher 无冻结 retry 命令）；②ACK 重发/崩溃点矩阵自动化（FEA-11 L-8）。
- AC4 PARTIAL（路径层依据已具备）：`doc/reviews/FEA-11-r3.md` 第 38 行「HOST-AUTH-1 可接受（有条件，并接受为 P0-1 闭合路径）」；P0-1 的实际闭合取决于 AC1–AC3，待本卡复审（r5）判定。
- 门禁：`verification/FEA-11-HOST-AUTH-1/logs/gates.log`（pytest 3051/0/10、.NET 首跑全绿 / 重跑 1390/0/78、IPC 3/3（Core 直连；命令/env 见 gates.log）、check PASS、pins 18/18；含 flaky 说明）。
- 已知限制：HostRuntime 级端到端（真实 sidecar + UI 命令面）未自动化；ACK 重发/崩溃点矩阵未自动化；`source.read/1` 缺失时 capability item 的 reason 语义待收口（FEA-11 r6 P2-4 遗留）；IPC 套件为 Core 直连（P2-9）；dispatcher 无冻结 retry 命令（retry 为 Host 编排 API）；receipt 核对/canonical 重算与 registry scope 精度登记 deferral。

## Deferral 登记表（r5 收口）

| Finding | 范围 | owner | 目标 |
|---|---|---|---|
| R4-P2-01 | Host 输入规则精度：plan_id 字符集/未知嵌套字段/grant_ids 重复与上限/generation 范围 | DSH（Source 线后续轮次） | 在 source 命令面收口时补 fail-closed 与用例 |
| R4-P2-02 | Registry scope/多 registry 原子性/`Begin` 与 `Authorize` 顺序（C-17 §3.2:156-157 崩溃窗口） | DSH | 与 FEA-11-HOST-AUTH-1 后续或 FEA-12 前置一并处置 |
| R4-P2-03 | receipt 核对（operation_id/request_digest/state）与 canonical CommitReceipt 重算 | DSH | ACK/recovery 消费 receipt 前补齐 |
| R4-P2-07 | 分类精度：黑名单含未产出码、typed 歧义分支用例 | DSH | 随命令面稳定性收敛时补测 |
| R4-P2-06 | 证据卫生：gates.log 的 worktree_clean/TRX 表述 | 已修（r5 门禁重写） | — |
| R4-P2-08 | non-BMP canonical 向量 | 已修（5/5） | — |

## DSH 裁决与 limitation 登记（r1 处置后）

- **P1-2 已修**：allowed_paths/owner/base_commit/reviewer/approval 补齐（见 front matter 与本卡窄批节）。
- **P2-6（journal 形状）**：Host journal 内部字节格式不强制等于冻结 `HostJournal` DTO；Core 侧 `source_get_operation` receipt 为主证据；`error_code/retryable` 已补（r2）；完整 `CommitReceipt` canonical 重算未做 → 登记后续增强。
- **P2-7（ACK fresh 授权）**：ACK 发送 journal 原始 authorization；Core `_verify_fresh` 为当前安全托底（operation/request digest/host_receipt/registry 覆盖/identity/generation + live grant）；Host 侧重读 Registry 并重签 fresh 授权登记为正式 limitation（owner：后续 Source 线轮次）。
- **P2-8/P2-9/P2-10**：证据卫生（失败 trx 归档）、IPC flake 定位、CORE_UNAVAILABLE 闭集边界登记为测试债务/deferral。
- **AC3 剩余**：见上（e2e/崩溃点/ACK 重发自动化 → limitation）。

## Acceptance Criteria

- [x] **AC1**：Host 侧 canonical-json/1 + sha256 摘要实现，与 Core 冻结公式逐字节一致（跨实现测试向量 5/5，含 non-BMP）。 <<MET>>
- [x] **AC2**：HostAuthorization 六字段由 Host 生成，operation_id 由 Host 生成并注入 ApplyRequest（`HostAuthorizationMinter` + 单测 6/6：六字段/排序/canonical digest/唯一性/固定向量/格式拒绝；注入在 HostRuntime 实现）。 <<MET>>
- [ ] **AC3**：先 `SourceAccessRegistry.Authorize` durable 再 journal（顺序断言 + 崩溃点）；Host→Core 集成测试覆盖 ACK 重发/恢复/失败。 <<PARTIAL: 顺序+失败语义+retry 由 HostOperationOrchestrator 保证，`Fea11HostAuthTests` 19/19（顺序探针/typed 失败/failed+error_code/歧义/retry fresh auth/kind 守卫/capability 门）；完整 HostRuntime→Core e2e 与 ACK 重发/崩溃点矩阵待补（FEA-11 L-8/L-9 limitation）>>
- [ ] **AC4**：FEA-11 r3 复审接受本卡为 P0-1 闭合路径（或产品方显式接受 Core-only limitation）。 <<PARTIAL: `doc/reviews/FEA-11-r3.md:38` 已接受本卡为 P0-1 闭合路径；P0-1 实际闭合取决于 AC1–AC3，待 r6 复审判定>>
