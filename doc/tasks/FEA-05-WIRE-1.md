---
id: FEA-05-WIRE-1
title: Draft 命令面 wire（Core 白名单 + CoreClient + Host 转发）
kind: implementation
governance_version: 3
status: proposed
approval: pending_review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-03
  - FEA-04
base_commit: 4ad0b06b3
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-05-WIRE-1
allowed_paths:
  - doc/tasks/FEA-05-WIRE-1.md
  - src/bootstrap/core_service.py
  - src/application/editing/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - verification/FEA-05-WIRE-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-05-WIRE-1-*.md
---

# FEA-05-WIRE-1：Draft 命令面 wire

## 来源与授权链

- FEA-03 Q-8：「ApplicationCore 本地缓冲 + 可注入 seam，**不接线** Host/IPC/CoreClient；wire 由 FEA-04 承担」
- FEA-04 Q-16：「不接 wire / 不改 Host/Core/CoreClient 契约」→ wire 顺延至本卡
- 方案 §15.6（Fluent 与 Current 共享草稿真值的前提）；AD-002（UI 不直接访问 DB/路径，经 Host/IPC 与 Core 契约访问）
- 上游实现：FEA-03 已在 Core 侧实现完整 drafts 服务（open/patch/prepare/apply/receipt/journal/锁），本卡只做**协议面接线**，不改编辑语义。

## 目的

把 Core 已实现的 Draft 服务经 Host 暴露给两个 frontend（Current / Fluent），使「编辑→草稿→应用」走同一份真值；不做 UI 改造、不改编辑规则。

## 交付范围（DSH 冻结）

| 层 | 内容 |
|---|---|
| Core 命令白名单 | `core_service.py` 允许命令新增：`drafts.open` / `drafts.patch` / `drafts.prepare` / `drafts.apply` / `drafts.close` / `drafts.status`；每个命令对应既有 application/editing 服务方法，**不新增业务语义** |
| Core handler | 命令 payload/result 映射到既有 `draft_*` 服务（含 token、candidate、receipt）；错误码透传既有结构 |
| CoreClient | `HostCommandModel`/`HostCommandDispatcher`（或等价）新增 6 条命令的请求/响应模型；与既有命令同风格 |
| IHostController | 新增 6 个方法（异步、CancellationToken）；`NullHostController` 返回 `NotSupported`/安全默认 |
| Host 转发 | 确认 Host 不需要改动（若需要，只允许在 Host 的命令转发表面登记，不改生命周期/凭据逻辑） |
| 测试 | Python：命令协议测试（成功/错误/未知命令拒绝）；CoreClient：序列化/分发/错误映射；App：`IHostController` 行为测试（可用 fake） |

## 验收标准

- [ ] **AC1 Core 白名单与 handler**：6 条命令在白名单与 handler 中登记；未知命令/非法 payload 被拒绝（既有错误结构）。<<TODO>>
- [ ] **AC2 语义不变**：命令 handler 只调用既有 `draft_*` 服务；不新增编辑规则、不改 token/candidate/receipt 语义（FEA-03 r5 已冻结）。<<TODO>>
- [ ] **AC3 CoreClient 映射**：请求/响应模型与既有命令同风格；错误码/消息透传；无 UI 依赖。<<TODO>>
- [ ] **AC4 IHostController 面**：6 方法签名稳定、可取消；`NullHostController` 安全默认；既有方法不回归。<<TODO>>
- [ ] **AC5 测试**：Python 协议测试 + CoreClient 测试 + App 测试全绿；`dotnet test apps/desktop-avalonia/NewManga.sln` 不退化（基线 931/0/60）。<<TODO>>
- [ ] **AC6 契约字节**：不改 15 份冻结 pin；若命令面属新契约，需 DSH 裁决并登记（本卡默认「命令白名单扩展」属已冻结 M2-IPC1 的兼容扩展，须在 AC 中记录依据）。<<TODO>>
- [ ] **AC7 证据**：`verification/FEA-05-WIRE-1/**` 原始日志 + 测试输出 + 证据表。<<TODO>>

## 禁止范围

- 不改 `schema.py`/migrations/数据库 schema；不改 C-02/C-03/C-04b/C-08 冻结契约字节；不改 UI 行为（Current/Fluent 的 VM/View）。
- 不动用户数据；不 push；不合并到 main（由 DSH 集成）。
- 不新增编辑业务规则（本卡只接线）。

## 附加裁决点（DSH 已裁，记录依据）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 命令面是新契约还是 M2-IPC1 兼容扩展？ | **兼容扩展**：在既有命令白名单追加 6 条、复用既有请求/响应信封与错误结构，不新增协议版本 | M2-IPC1 允许「命令 added」的向后兼容扩展（`core_service.py:269-287` 注释先例）；若复核认为需新版契约，退回 DSH |
| W-2 | 是否同时把 wire 接进 Current 的 Frontends（替换 ApplicationCore 本地缓冲）？ | **否**：本卡只暴露命令面；Current 接入由 FEA-06（Fluent）或后续卡承担 | FEA-04 Q-16/Q-19；避免同卡混 UI 改造 |
| W-3 | 失败语义 | 复用既有错误结构（code/message/details）；不静默 | FEA-03 语义 |

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `python -m pytest tests/ -q`（含新增 drafts 协议测试） | Core | NOT_RUN | 待补 |
| AC3/AC4 | `dotnet test apps/desktop-avalonia/src/NewManga.CoreClient` + `NewManga.App.Tests` | .NET | NOT_RUN | 待补 |
| AC5 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` | 全量 | NOT_RUN | 待补 |
| AC6 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 治理 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（实现提交由 DSH 集成）；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
