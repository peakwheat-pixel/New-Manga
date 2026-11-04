---
id: FEA-10-PREREQ-1
title: C-08 块②协议注册（M2-C1 rev 2.12：PrepareRun/AcceptRun + 3 错误码 + host 投影白名单）
kind: implementation
governance_version: 3
status: proposed
approval: pending scope freeze（Codex 2026-11-04 裁决 FEA-10 优先；C-08 冻结记录 §3 为释放前置）
suggested_owner: codex
owner: null
reviewer: pending scope review（独立上下文；新 Appointment 后登记）
depends_on:
  - FEA-01-FREEZE-1
base_commit: d831cf968cd856674c0320fe67ce854f4ef9d4b3
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
  - apps/desktop-avalonia/src/NewManga.CoreClient/
  - apps/desktop-avalonia/src/NewManga.Host/
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/
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

## 交付物

1. `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`：rev 2.12 增量（PrepareRun/AcceptRun 请求/结果形状、3 码、§8 未观察、retryable/taxonomy 例外；既有行语义不改）。
2. host 投影层：`allowedRunErrorCodes` 白名单 + 未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**；负向对照测试（未扩 M2-C1 时 3 码降级为 unknown）。
3. CoreClient/Host 对应测试；协议注册与既有 Run 命令回归。
4. `verification/FEA-10-PREREQ-1/**` 证据、Handoff、实现 Review 报告（独立上下文）。

## Acceptance Criteria

- [ ] **AC1（M2-C1 字节增量）**：rev 2.12 只新增/登记 §3 所列内容；既有冻结命令/结果/错误/状态/事件语义零改动；文档 diff 逐条对照 C-08 §3；Core 协议 minor 未提升（除 DSH 批准）。
- [ ] **AC2（host 白名单）**：`allowedRunErrorCodes` 实现；未注册错误码投影为 `category=unknown`、安全消息、原 `code` 保留；三个新码仅在注册后进入白名单；**未注册码不得触发专属恢复/重试动作，也不得作为 UI 分支依据**。
- [ ] **AC3（负向对照）**：模拟未注册码 → 断言 host 投影降级 unknown（不拒绝、不改 code、无专属恢复/重试动作）；注册后 → 断言按冻结 category/retryable 投影。
- [ ] **AC4（回归与冻结面）**：既有 Run 命令 wire/测试不回归；`check.ps1`、`verify_pins.ps1` 17/17；C-05/C-15/C-16 字节未改；无生产 Run 实现。
- [ ] **AC5（证据与 Review）**：真实命令/测试日志（含 EXIT）、范围 diff、独立实现 Review、Handoff、EV/Resource Manifest。

## 测试要求

| 场景/AC | 计划命令 | 前提/环境 | 期望 |
|---|---|---|---|
| AC1 | `git diff -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` + 逐条对照 C-08 §3 | 主工作树 | 仅增量；无旧语义改动 |
| AC2/AC3 | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests` / `NewManga.Host.Tests`（新增投影测试） | .NET 9；隔离数据 | 白名单/unknown 降级通过 |
| AC4 | `pwsh tools/governance/check.ps1`；`verify_pins.ps1`；全量 `dotnet test`（不减少） | 主工作树 | PASS；17/17 |
| AC5 | 证据写 `verification/FEA-10-PREREQ-1/**`；`git diff --name-only` 对照写域 | 主工作树 | 全合规；独立 Review approved |

## 文档 rev 与 wire 版本边界（P2-3 澄清）

- `M2-C1 rev 2.12` 是**协议文档修订号**，不等于 Core `PROTOCOL_MINOR` 提升；本卡只登记 PrepareRun/AcceptRun 命令形状与 3 码的文档增量。
- Core 运行版本、`_RUN_COMMANDS`/dispatch 与兼容回归由 **FEA-10 实现卡**承接（`src/bootstrap/core_service.py`、`core_assembly.py`、`CoreServiceClient.cs` 等）；本卡不实现命令。
- 若实现需要提升 Core `PROTOCOL_MINOR`，须 DSH 另行批准并登记；未批准前不得改运行版本。

## 依赖、风险与阻塞

- 依赖：C-08 已冻结、FEA-01 已冻结；无代码实现前置。
- 风险：M2-C1 是既有运行协议文档，增量必须 additive；host 投影不能改变既有错误处理分支；不得顺手实现 FEA-10。
- 释放条件：scope review approved + DSH Appointment；FEA-10 的 `ready` 以本 Task `done` 为硬前置。

## Closeout Record

- 未开始（proposed）。
