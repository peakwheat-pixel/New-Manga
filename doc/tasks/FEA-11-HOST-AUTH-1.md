---
id: FEA-11-HOST-AUTH-1
title: FEA-11 Host durable authorization 自签与编排（C-17 §5.2 续）
kind: implementation
governance_version: 3
status: closed_with_limitations
approval: 承接自 FEA-11 Review r1（DSH 2026-11-05 裁决）；用户 2026-11-05 授权启动；scope 由本卡 allowed_paths + DSH 窄批登记；终态由用户 2026-11-05 委托 Codex 裁决（DECISION A）
suggested_owner: codex
owner: dsh（2026-11-05 用户授权启动；实施 DSH/Team）
reviewer: 独立上下文 fresh subagent（r1–r8；报告 doc/reviews/FEA-11-HOST-AUTH-1-r1.md…-r8.md）；终态裁决 Codex（`doc/reviews/FEA-11-HOST-AUTH-1-codex-adjudication-2026-11-05.md`）
depends_on:
  - FEA-11-PREREQ-1
base_commit: 7ab9eea87
branch: null
worktree: null
integration_commit: cbd561b432f73bce3308d68366f79f408cee000a
delivery_head: cbd561b432f73bce3308d68366f79f408cee000a
canonical_evidence_status: complete
resource_closeout_status: complete
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
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
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
- 状态：proposed（DSH 2026-11-05 裁决承接；FEA-11 承接时 Host 侧为透传实现（本卡已实现 Host 自签授权），Core 侧已完整）。

## 实施证据与 AC 状态（DSH，2026-11-05）

- AC1 MET：`CanonicalJson.cs` + `CanonicalJsonTests` 5/5（含 non-BMP）（跨实现向量：request/authorization/mixed/escapes + non-BMP code-point 排序；sha256 由 Python Core 生成）。
- AC2 MET：`HostAuthorizationMinter`（六字段/排序/canonical digest）+ `HostAuthorizationMinterTests` 6/6（含固定 id 外部向量）；HostRuntime 注入 ApplyRequest（`Fea11HostAuthTests.Apply_InjectsTheHostMintedAuthorizationNotTheCallers`）。
- AC3 PARTIAL（r4 返修后）：typed 业务拒绝（歧义集合外）→ journal **failed + error_code/retryable**（durable，retryable 取 Core 值）；歧义/传输失败 → host-authorized + `requestId=operation_id` 供恢复；**同 operation/request digest 重试已实现（Host 侧四项守卫：kind/request_digest/state/CommitDigest/Retryable；plan 有效性由 Core `take_confirmed` 在 apply 事务内复核）**：`RetryAsync` 锁后重读 Registry → `Authorize` durable → **重新 mint 新 HostAuthorization 并原子落盘**（AuthorizationJson/Digest/HostReceiptId 更新）→ dispatch；typed 拒绝再落 failed；已提交 failed 拒绝 retry（走 recover）；non-retryable 拒绝。`Fea11HostAuthTests` 24/24（19 方法）。**剩余 limitation**：①完整 HostRuntime→Core 端到端（真实 sidecar + dispatcher 接线；retry 目前是 Host 编排 API，dispatcher 无冻结 retry 命令）；②ACK 重发/崩溃点矩阵自动化（FEA-11 L-8）。
- AC4 PARTIAL（路径层依据已具备）：`doc/reviews/FEA-11-r3.md` 第 38 行「HOST-AUTH-1 可接受（有条件，并接受为 P0-1 闭合路径）」；P0-1 的实际闭合取决于 AC1–AC3，r7 changes_requested；r8 approved（待用户裁决 closed_with_limitations）。
- 门禁：`verification/FEA-11-HOST-AUTH-1/logs/gates.log`（pytest 3051/0/10、.NET 首跑全绿 / 重跑 1390/0/78（r5 全量运行 head 0b7e5e03b；r6 复跑 Host.Tests 105/0/49）、IPC 3/3（Core 直连；命令/env 见 gates.log）、check PASS、pins 18/18；含门禁命令/EXIT/provenance）。
- 已知限制：HostRuntime 级端到端（真实 sidecar + UI 命令面）未自动化；ACK 重发/崩溃点矩阵未自动化；`source.read/1` 缺失时 capability item 的 reason 语义待收口（FEA-11 r6 P2-4 遗留）；IPC 套件为 Core 直连（P2-9）；dispatcher 无冻结 retry 命令（retry 为 Host 编排 API）；plan 有效性由 Core `take_confirmed` 事务内兜底；receipt 核对/canonical 重算、registry scope 精度；R7-P2-01 守卫补测已完成（不再 deferral）。

## Deferral 登记表（r5 收口）

| Finding | 范围 | owner | 目标 |
|---|---|---|---|
| R4-P2-01 | Host 输入规则精度：plan_id 字符集/未知嵌套字段/grant_ids 重复与上限/generation 范围 | DSH（Source 线后续轮次） | 在 source 命令面收口时补 fail-closed 与用例 |
| R4-P2-02 | Registry scope/多 registry 原子性/`Begin` 与 `Authorize` 顺序（C-17 §3.2:156-157 崩溃窗口） | DSH | 与 FEA-11-HOST-AUTH-1 后续或 FEA-12 前置一并处置 |
| R4-P2-03 | receipt 核对（operation_id/request_digest/state）与 canonical CommitReceipt 重算 | DSH | ACK/recovery 消费 receipt 前补齐 |
| R4-P2-07 | 分类精度：黑名单含未产出码、typed 歧义分支用例 | DSH | 随命令面稳定性收敛时补测 |
| R6-P2-01 | Host 侧 plan 有效性预检（C-17 §3.2:163 守卫列）；需冻结 plan-read 命令，当前由 Core `take_confirmed` 事务内 fail-closed 复核 | DSH | C-17 若新增冻结 plan-read 命令再做 Host 预检 |
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
- [ ] **AC3**：先 `SourceAccessRegistry.Authorize` durable 再 journal（顺序断言 + 崩溃点）；Host→Core 集成测试覆盖 ACK 重发/恢复/失败。 <<PARTIAL: 顺序+失败语义+retry 由 HostOperationOrchestrator 保证，`Fea11HostAuthTests` 24/24（19 方法）（顺序探针/typed 失败/failed+error_code/歧义/retry fresh auth/kind 守卫/capability 门）；完整 HostRuntime→Core e2e 与 ACK 重发/崩溃点矩阵待补（FEA-11 L-8/L-9 limitation）>>
- [x] **AC4**：FEA-11 r3 复审接受本卡为 P0-1 闭合路径（或产品方显式接受 Core-only limitation）。 <<MET>>
  - r8 窄口径：`doc/reviews/FEA-11-r3.md:38` 已接受本卡为 P0-1 闭合路径，故按「MET（路径层）」记录；这不宣称 P0-1 的全部技术工作完成（AC3 仍 PARTIAL，见 r8 与 10 项 limitation）。

## 终态裁决（Codex，2026-11-05；用户当日委托）

- **DECISION: A — 接受 `closed_with_limitations` 收口**；不宣称技术完成，不进入 READY DAG。裁决原文（原字节）：`doc/reviews/FEA-11-HOST-AUTH-1-codex-adjudication-2026-11-05.md`。
- 依据：r8 approved（P0/P1/P2=0）；AC3 PARTIAL、AC4 MET（路径层）；`doc/09_COLLABORATION.md:79` 要求用户明确裁决（用户 2026-11-05 委托 Codex 裁决）。
- **保留 r8 十项 limitation 原文与顺序，不改写为 PASS**；AC3 保持 `PARTIAL`。
- **附注（Codex 要求，不改写原十项）**：ACK/recovery 当前从 journal 读取原 authorization（`SourceOperationCoordinator.cs` 的 ACK/recovery 路径），C-17 要求 ACK/recovery 使用 fresh grant/authorization；Core 侧 `_verify_fresh` 仍有摘要/基线/identity/live grants 校验，未见 P0/P1 绕过。该行为缺口**映射到 limitation 1/2/5/10**（Host 流程完整性/矩阵缺失/receipt 核对/证据残留）；真正闭合需新授权卡。
- R8-P3 逐项复核：R8-P3-01/02/05 已在 `81c28d30` 修正（卡面历史状态、reviewer r1–r8、STATUS/PLAN 指针、矛盾句）；R8-P3-04（R7-P2-01 用例 2 判别力）保留为 limitation 10；R8-P3-03（gates.log 计数/命令/EXIT/provenance）已在 `verification/FEA-11-HOST-AUTH-1/EV.md` 与 gates.log closure 记录中区分 r6=105 与 r8=107、全量 .NET 1395 来源、IPC 首跑 2/3 flake 与复跑。
- 与 `Deferral 登记表`/`已知限制` 的关系：原 P2-7 类内部限制（ACK fresh 授权等）与 r8 的 P2=0 分开记录，不互相删除或改写。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-AC1-CANON | AC1 | apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CanonicalJsonTests.cs | cbd561b4 | - | CANONICAL |
| EV-AC2-MINTER | AC2 | apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/HostAuthorizationMinterTests.cs | cbd561b4 | - | CANONICAL |
| EV-AC3-HOSTAUTH | AC3 | apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs | cbd561b4 | - | CANONICAL |
| EV-AC4-R3 | AC4 | doc/reviews/FEA-11-r3.md | cbd561b4 | - | CANONICAL |
| EV-R8-REVIEW | 最终独立复审 | doc/reviews/FEA-11-HOST-AUTH-1-r8.md | 81c28d30 | - | CANONICAL |
| EV-CODEX-ADJ | 终态裁决 | doc/reviews/FEA-11-HOST-AUTH-1-codex-adjudication-2026-11-05.md | pending | 009770a3dcdc903c49786eafedd2257c139a2f68a4f221807ae93295a71fbb3a | CANONICAL |
| EV-GATES | 门禁 | verification/FEA-11-HOST-AUTH-1/logs/gates.log | pending | 2a46007165fc95fead9711ae3aaa4dbebe63360bfe19eafcc554039026446479 | CANONICAL |
| EV-CHANGED | 交付清单 | verification/FEA-11-HOST-AUTH-1/changed-files.txt | pending | f9133156ef45f4ebeb2c413a5c6cdceb6fd092e3a84b4724f975bb5f
| SOURCE-PIN-EV | closeout 证据 | verification/FEA-11-HOST-AUTH-1/EV.md | - | ac8a7842bf868bf99768f4bcdb231bb268ece24075da71463c5a5ab08487e83d | SOURCE_PIN |
| SOURCE-PIN-RESOURCE-MANIFEST | closeout 证据 | verification/FEA-11-HOST-AUTH-1/RESOURCE-MANIFEST.md | - | 4848039bc444e30c26db0c47c026e41a5302de3f408670d8e701f69907ac1fd1 | SOURCE_PIN |
| SOURCE-PIN-DELIVERY-MANIFEST | closeout 证据 | verification/FEA-11-HOST-AUTH-1/DELIVERY-MANIFEST.md | - | 0fc1139b73f9da4c2fd17676a7c1d6ea35f7f5ed0ab8d70e1e1a0f157de15cb9 | SOURCE_PIN |42e74015 | CANONICAL |

> 证据索引与口径：`verification/FEA-11-HOST-AUTH-1/EV.md`；交付清单 23 files；`RESOURCE-MANIFEST.md`、`DELIVERY-MANIFEST.md` 同目录。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| evidence | verification/FEA-11-HOST-AUTH-1 | PRESERVE_REFERENCED | verification/FEA-11-HOST-AUTH-1 | verification/FEA-11-HOST-AUTH-1/EV.md | 当前 Task/EV/DELIVERY 引用；原位保留不清理 |
| 代码/测试 | apps/desktop-avalonia | PRESERVE_REFERENCED | apps/desktop-avalonia | verification/FEA-11-HOST-AUTH-1/changed-files.txt | 已集成 main（delivery `cbd561b4`）；不回滚 |
| worktree | NOT_APPLICABLE（main 工作树实施） | NOT_APPLICABLE | — | — | 无 worktree 删除/prune |
| artifact/temp/agent-output/exchange/dataset | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无本任务专属资源；无仓外临时 DB/fixture |

## Closeout Record

- Closeout date / DSH：2026-11-05 / DSH（Lead/Architect/Integrator）。
- 终态：`closed_with_limitations`（裁决人 Codex；用户 2026-11-05 委托；DECISION A）。
- 替代依据：r8 approved（P0/P1/P2=0，P3=5）+ 10 项 limitation + AC3 PARTIAL；`doc/09_COLLABORATION.md:79`；裁决文件见上。
- canonical_evidence_status：`complete`；resource_closeout_status：`complete`。
- 证据定稿：`EV.md`、`RESOURCE-MANIFEST.md`、`DELIVERY-MANIFEST.md`、`changed-files.txt`、`logs/gates.log`（含 closure 记录与 provenance）。
- 未完成 AC/Finding 原始状态：AC3 `PARTIAL`（不改为 PASS）；limitation 10 项原文保留；Deferral 表原样保留。
- 删除、迁移、归档数量/字节数：0（无 DELETE_SAFE）。
- 当前指针清理：STATUS/Plan/TASK_LEDGER 已更新；本卡为终态、不得进入 READY DAG；worker worktree 无（main 实施）。
- 后续：ACK/recovery fresh authorization、HostRuntime e2e、ACK 重发/崩溃点矩阵等仅在**新授权**下另开卡。
