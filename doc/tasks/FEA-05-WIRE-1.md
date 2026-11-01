---
id: FEA-05-WIRE-1
title: Draft 命令面 wire（Core 白名单 + 命令契约登记 + CoreClient）
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
base_commit: 4dfc8abc4
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-05-WIRE-1
allowed_paths:
  - doc/tasks/FEA-05-WIRE-1.md
  - doc/contracts/V11R_COMMAND_CONTRACT_V1.md
  - src/bootstrap/core_service.py
  - src/application/editing/**
  - tests/core/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - verification/FEA-05-WIRE-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-05-WIRE-1-*.md
---

# FEA-05-WIRE-1：Draft 命令面 wire（收窄版）

## 来源与授权链

- FEA-03 Q-8：「ApplicationCore 本地缓冲 + 可注入 seam，不接线 Host/IPC/CoreClient；wire 由 FEA-04 承担」
- FEA-04 Q-16：「不接 wire / 不改 Host/Core/CoreClient 契约」→ wire 顺延
- 方案 §15.6（Fluent 与 Current 共享草稿真值的前提）；AD-002（UI 经 Host/IPC 与 Core 契约访问）
- 上游实现：FEA-03 已在 Core 侧实现完整 drafts 服务；本卡只做**协议面接线 + 契约登记**，不改编辑语义。

## 范围收窄（r1 复核 P0 处置，DSH 裁决）

| # | r1 问题 | 处置 |
|---|---|---|
| P0-01 | 命令面无契约载体（`CommandContractV11RTests.cs:68-86` 要求注册命令在 `V11R_COMMAND_CONTRACT_V1.md` 声明） | **纳入写域**：本卡在 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 追加 6 条命令登记（C078+ 位）；AC1 增加「契约登记」 |
| P0-02 | `IHostController` 47→53 触发 C-07 端口清单不一致（`generate_api_inventory.py --check` EXIT 1），与 AC6「不动 pin」互斥 | **收窄**：本卡**不接 IHostController / HostController / NullHostController**；端口面由后续卡（FEA-05-PORT-1）在 UNFREEZE 流程下处理。W-2 声明省略（本卡不接 UI 即无端口消费方） |
| P0-03 | Python 协议测试无写域（`tests/core/**` 缺失） | **纳入写域**：`tests/core/**`（新增 `test_draft_commands.py`）+ `tests/domain/**`（如需） |
| P1-01 | `drafts.close` 二义（discard 丢编辑 vs end_session 强 flush） | **去掉 `close`**：命令面改为 6 条：`drafts.open` / `drafts.patch` / `drafts.prepare` / `drafts.apply` / `drafts.status` / `drafts.discard`；session 结束由既有 session 层负责，本卡不引入 |
| P1-04 | W-1 引用的 `core_service.py:269-287` 是「新增命令→minor bump」先例，与「零 bump」相反 | **依据改正**：`core_service.py:451-457`（既有命令在同类兼容扩展下的登记方式）+ `V11R_REGION_WRITE_CONTRACT.md:39-59`（兼容扩展先例）；本卡同时更新命令契约文档，故不依赖「零 bump」 |

## 交付范围（DSH 冻结）

| 层 | 内容 |
|---|---|
| 命令契约登记 | `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 追加 C078+ 的 6 条命令（名称/payload/result/错误码/版本）；与既有条目同格式 |
| Core 命令白名单 + handler | `core_service.py` 允许 6 条命令；handler 只调用既有 `draft_*` 服务（`next_draft_id`/`add_patch`/`prepare_candidates`/`apply_candidates`/`draft_status`/`discard_draft`）；错误码透传既有结构 |
| CoreClient | `HostCommandModel`/`HostCommandDispatcher` 新增 6 条命令的请求/响应模型；无 UI 依赖 |
| 测试 | Python：`tests/core/test_draft_commands.py`（成功/未知命令/非法 payload/错误码）；CoreClient：序列化/分发/错误映射 |

**不做**：IHostController 端口面、Host 生命周期/凭据、UI 接线（Current/Fluent）、编辑语义变更、数据库 schema。

## 验收标准

- [ ] **AC1 契约登记**：`V11R_COMMAND_CONTRACT_V1.md` 登 6 条命令，`CommandContractV11RTests` 通过（机械断言一致）；未知命令被拒绝。<<TODO>>
- [ ] **AC2 语义不变**：handler 只调用既有 `draft_*`；不新增编辑规则、不改 token/candidate/receipt 语义（FEA-03 r5 冻结）。<<TODO>>
- [ ] **AC3 CoreClient 映射**：模型与既有命令同风格；错误码/消息透传；无 UI 引用。<<TODO>>
- [ ] **AC4 Python 协议测试**：`python -m pytest tests/core tests/domain -q` 全绿（含新测试）。<<TODO>>
- [ ] **AC5 回归**：`dotnet build apps/desktop-avalonia/NewManga.sln` EXIT=0；`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` 不退化（基线 931/0/60）。<<TODO>>
- [ ] **AC6 冻结 pin 不变**：`verify_pins.ps1` 15/15；C-07 端口清单不变（本卡不新增端口）；`generate_api_inventory.py --check` EXIT 0。<<TODO>>
- [ ] **AC7 证据**：`verification/FEA-05-WIRE-1/**` 原始日志 + 测试输出 + 证据表。<<TODO>>

## 禁止范围

- 不接 IHostController/HostController/NullHostController（端口面另卡）；不改 Host 生命周期/凭据；不改 UI（Current/Fluent）。
- 不改 schema/migrations；不改 C-02/C-03/C-04b/C-08 冻结契约字节；不动用户数据；不 push；不合并 main。
- 不新增编辑业务规则。

## 附加裁决点（DSH 已裁，记录依据）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 命令面是新契约还是兼容扩展？ | **兼容扩展 + 契约登记**：命令追加到 `V11R_COMMAND_CONTRACT_V1.md` 的 C078+ 位，复用既有 JSON-lines 信封与错误结构，不新增协议版本 | `core_service.py:451-457`（既有兼容扩展登记先例）+ `V11R_REGION_WRITE_CONTRACT.md:39-59`（兼容扩展先例）；r1 P1-04 已纠正引用 |
| W-2 | 是否接 UI（Current/Fluent）？ | **否**：本卡只到 CoreClient 命令面；UI 接线由 FEA-06 或后续卡 | FEA-04 Q-16/Q-19；避免同卡混 UI 改造与 C-07 端口冲突 |
| W-3 | 命令集合 | **6 条**：`drafts.open` / `drafts.patch` / `drafts.prepare` / `drafts.apply` / `drafts.status` / `drafts.discard`；不含 `close`（r1 P1-01 二义） | FEA-03 服务方法边界；session 结束归 session 层 |
| W-4 | 失败语义 | 复用既有错误结构（code/message/details）；不静默 | FEA-03 语义 |

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC4 | `python -m pytest tests/core tests/domain -q` | Core | NOT_RUN | 待补 |
| AC3 | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests` | .NET | NOT_RUN | 待补 |
| AC5 | `dotnet build apps/desktop-avalonia/NewManga.sln` + `dotnet test ... --no-build --settings .../NewManga.runsettings` | 全量 | NOT_RUN | 待补 |
| AC6 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` + `python tools/governance/generate_api_inventory.py --check` | 治理 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（实现提交由 DSH 集成）；资源处置在收口时登记。

## Closeout Record

- 2026-11-02 / DSH：按范围复核 r1（P0×3 / P1×5 / P2×6）收窄并改卡——纳入命令契约与 Python 测试写域；去掉 IHostController 端口面与 `drafts.close`；改正 W-1 依据。待 r2 复核。
