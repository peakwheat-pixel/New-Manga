---
id: FEA-10-PREREQ-1
title: C-08 块②协议注册（M2-C1 rev 2.12：PrepareRun/AcceptRun + 3 错误码 + host 投影白名单）
kind: implementation
governance_version: 3
status: ready
approval: **scope approved（r5 Codex，P0=0/P1=0；仅 P2 残留）+ DSH Appointment 2026-11-04**；C-08 冻结记录 §3 为释放前置；等 Codex 额度恢复（13:31 后）认领实施
suggested_owner: codex
owner: codex（Appointment 2026-11-04；待 Codex 额度恢复后认领）
reviewer: implementation review 待 Appointment（全新上下文；不得由实现者自审）
depends_on:
  - FEA-01-FREEZE-1
base_commit: 1254d4e01608d3c9577872abb1dedea5661889aa
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-10-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-10-PREREQ-1.md
  - doc/tasks/FEA-10.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - apps/desktop-avalonia/src/NewManga.CoreClient/Wire/CoreProtocol.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10PrereqProjectionTests.cs
  - doc/reviews/FEA-10-PREREQ-1-*.md
  - doc/handoffs/FEA-10-PREREQ-1-*.md
  - verification/FEA-10-PREREQ-1/**
out_of_scope:
  - FEA-10 实现（PreparedRun/候选存储/校验/提交 seam；另卡）
  - 既有 Run 命令语义修改、Core 协议 major/minor 提升（除 DSH 明确批准）、wire 行为改动
  - C-01b/C-05/C-08 等冻结契约字节（C-08 记录/冻结矩阵的更新须 DSH 授权）
  - 真实用户数据/AppData/外部卷；push
---

# FEA-10-PREREQ-1：C-08 块②协议注册

> 来源：`doc/plan/FEA-CONTRACT-FROZEN-C08.md` §3「协议注册（块②，释放前置）」；`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md` SC-R01…SC-R09；`doc/reviews/ADJ-2026-11-01-FEA-DECISIONS.md` 冻结授权；`doc/reviews/ADJ-2026-11-04-NEXT-TASK.md`（Codex 裁决 + DSH 修正）。
> 本 Task 是 **FEA-10 的硬前置**：未完成前 FEA-10 不得 `ready`/`in_progress`。

## 事实与缺口

- C-08 已 **FROZEN**（pin `453f993c…`）；其 §3 规定块②：M2-C1 §5.5 追加 `PrepareRun`/`AcceptRun` 两行、3 个新错误码（`RUN_STALE_PREVIEW` conflict/false、`RUN_PREVIEW_EXPIRED` conflict/false、`RUN_SNAPSHOT_INCOMPLETE` unavailable/true）、§8「Proposed（未观察）」3 行、`:1119` retryable 证据规则例外、`:1122` taxonomy 例外、host 投影层 `allowedRunErrorCodes` 白名单、wire 版本登记 minor 2.12。
- **当前 M2-C1 为 rev 2.11，未含 PrepareRun/AcceptRun 与 3 个错误码**（`grep` 实证）；host 错误投影白名单亦未实现 → C-08 释放前置 (b) 未完成。
- 本 Task **只做协议注册与投影注册**，不实现 Run 的两阶段/候选/提交逻辑；不得提前实现 FEA-10。

## 文件级写域矩阵

| 文件 | 用途 | AC |
|---|---|---|
| `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | rev 2.12 命令行/结果/3 码/§8/例外登记 | AC1 |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Wire/CoreProtocol.cs` | 业务错误类型 `CoreErrorInfo`/`CoreOperationException`；`code/category/retryable` 白名单投影落点 | AC2 |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | 客户端命令 registry 映射 | AC1/AC2 |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | dispatch/payload 形状校验 | AC2/AC3 |
| `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | host 投影层/`allowedRunErrorCodes` | AC2/AC3 |
| `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/WireTests.cs` | 注册/投影测试 | AC2/AC3 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs` | host 投影负向对照 | AC3/AC4 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea10PrereqProjectionTests.cs`（新） | 3 码白名单/unknown 降级 | AC2/AC3 |

## 交付物

1. `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：rev 2.12 增量（PrepareRun/AcceptRun 请求/结果形状、3 码、§8 未观察、retryable/taxonomy 例外；既有行语义不改）。
2. host 投影层：`allowedRunErrorCodes` 白名单 + 未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**；负向对照测试（未扩 M2-C1 时 3 码降级为 unknown）。
3. CoreClient/Host 对应测试；协议注册与既有 Run 命令回归。
4. `verification/FEA-10-PREREQ-1/**` 证据、Handoff、实现 Review 报告（独立上下文）。

## Acceptance Criteria

- [ ] **AC1（M2-C1 字节增量与 wire 登记）**：rev 2.12 只新增/登记 §3 所列内容；既有冻结命令/结果/错误/状态/事件语义零改动；文档 diff 逐条对照 C-08 §3；登记 C-08 §3 **已批准的 wire 版本 2.12**（文档 rev 与 Core `PROTOCOL_MINOR` 不是同一概念；是否提升运行 minor 由 DSH 明确批准）；明确客户端 registry/错误投影映射与测试归属（PREREQ 只做文档+host 白名单；Core dispatch/运行实现归 FEA-10）。
- [ ] **AC2（host 白名单）**：`allowedRunErrorCodes` 实现；未注册错误码投影为 `category=unknown`、安全消息、原 `code` 保留；三个新码仅在注册后进入白名单；**未注册码不得触发专属恢复/重试动作，也不得作为 UI 分支依据**。
- [ ] **AC3（负向对照）**：模拟未注册码 → 断言 host 投影降级 unknown（不拒绝、不改 code、无专属恢复/重试动作）；注册后 → 断言按冻结 category/retryable 投影。
- [ ] **AC4（回归与冻结面）**：既有 Run 命令 wire/测试不回归；`check.ps1`、`verify_pins.ps1` 17/17；C-05/C-15/C-16 字节未改；无生产 Run 实现。
- [ ] **AC5（证据与 Review）**：真实命令/测试日志（含 EXIT）、范围 diff、独立实现 Review、Handoff、EV/Resource Manifest。

## 测试要求

| 场景/AC | 计划命令 | 前提/环境 | 期望 |
|---|---|---|---|
| AC1 | `git diff -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` + 逐条对照 C-08 §3 | 主工作树 | 仅增量；无旧语义改动 |
| AC2/AC3 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/NewManga.CoreClient.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~CoreProtocolTests|FullyQualifiedName~AsciiWireTests"`；`dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter FullyQualifiedName~Fea10PrereqProjectionTests` | .NET 9；隔离测试数据根 `G:/CODEX/New Manga.workspace/FEA-10-PREREQ-1/`；日志/EXIT 写 `verification/FEA-10-PREREQ-1/logs/` | 白名单/unknown 降级通过；日志可复现 |
| AC4 | `pwsh -NoProfile -File tools/governance/check.ps1`；`pwsh -NoProfile -File tools/governance/verify_pins.ps1`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`（不减少） | 主工作树；日志/EXIT 写 `verification/FEA-10-PREREQ-1/logs/` | PASS；17/17 |
| AC5 | 证据写 `verification/FEA-10-PREREQ-1/**`；`git diff --name-only` 对照写域 | 主工作树 | 全合规；独立 Review approved |

## 文档 rev 与 wire 版本边界（P2-3 澄清）

- C-08 冻结记录 §3 已批准新命令登记为 **wire 版本 2.12**；`M2-C1 rev 2.12` 是该登记对应的**文档修订号**。Core `PROTOCOL_MINOR` 是否需要提升是独立问题，由 DSH 在实施前明确，不因文档 rev 自动提升。
- 本卡登记：M2-C1 命令行/结果形状/3 码/§8 未观察/例外；客户端 registry 与错误投影映射/白名单；负向对照测试。
- Core `_RUN_COMMANDS`/dispatch、`core_assembly.py`、`CoreServiceClient.cs` 的运行实现与兼容回归由 **FEA-10 实现卡**承接；本卡不实现命令、不改运行语义。

## 依赖、风险与阻塞

- 依赖：C-08 已冻结、FEA-01 已冻结；无代码实现前置。
- 风险：M2-C1 是既有运行协议文档，增量必须 additive；host 投影不能改变既有错误处理分支；不得顺手实现 FEA-10。
- 释放条件：scope review approved + DSH Appointment；FEA-10 的 `ready` 以本 Task `done` 为硬前置。

## Closeout Record

- 未开始（proposed，scope review r4 待派发）。
