---
id: FEA-05-PORT-1
title: Draft 端口面（IHostController + CoreClient registry + Region 契约 UNFREEZE）
kind: implementation
governance_version: 3
status: proposed
approval: pending_review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-05-WIRE-1
base_commit: 70dd4322f
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-05-PORT-1
allowed_paths:
  - doc/tasks/FEA-05-PORT-1.md
  - doc/contracts/V11R_REGION_WRITE_CONTRACT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C*.md
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Studio/**（仅 Draft 端口注入，不改变行为）
  - verification/FEA-05-PORT-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-05-PORT-1-*.md
---

# FEA-05-PORT-1：Draft 端口面（IHostController + CoreClient registry + Region 契约 UNFREEZE）

## 来源与授权链

- FEA-05-WIRE-1（已 done，`d9d7dde41`）交付 Core 命令面 + 契约；其 W-6 明确把「端口面 + CoreClient registry + Region 不变式」留给本卡。
- 方案 §15.2（Fluent 独立 frontend）/§15.6；C-02 V-08b（KeyMap 无关）；C-07（端口清单 = `generate_api_inventory.py`）。
- 上游冻结契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（FROZEN v1.5）——本卡需 UNFREEZE 到 v1.6。

## 任务拆解

| 项 | 内容 | 依赖 |
|---|---|---|
| P1 契约 UNFREEZE | `V11R_REGION_WRITE_CONTRACT.md` v1.5 → v1.6：把「追加集恰为 `V11RAdditiveCommandNames`（10 写 + 1 读）」升级为「追加集 = `RegionWrite ∪ RegionRead ∪ Drafts`（各家族声明集合之并）」，并补 `DraftsCommandNames`（6）声明 | 无 |
| P2 端口面 | `IHostController` 新增 6 个 Draft 方法（`OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync`/`ApplyCandidatesAsync`/`GetDraftStatusAsync`/`DiscardDraftAsync`）；`HostController` 实现（经 `HostCommandDispatcher`）；`NullHostController` 安全默认 | P1 |
| P3 CoreClient registry | `HostCommandModel` 6 条；`HostCommandRegistry` 注册（域 `Drafts`、通道 `core`、minor 3）；`HostCommandDispatcher` 路由；`V11RAdditiveCommandNames` 11 → 17 | P1 |
| P4 契约测试更新 | `RegionWriteCommandTests` 断言改为「additive = RegionWrite ∪ RegionRead ∪ Drafts」并保留 Region 子集断言；`CommandParityContractTests` 每域非空/`CoreMinor>0` | P2/P3 |
| P5 端口清单 | `generate_api_inventory.py --check` 通过（C-07 端口清单更新）；若脚本生成清单，需重跑并提交 | P2 |
| P6 冻结记录 | 新 pin 写入 `doc/plan/FEA-CONTRACT-FROZEN-<id>.md`（或追加）+ `verify_pins.ps1` 15/15；UNFREEZE 记录（`CONTRACT-UNFREEZE-2026-11-xx`） | P1 |

## 验收标准

- [ ] **AC1 契约 UNFREEZE**：`V11R_REGION_WRITE_CONTRACT.md` v1.6 落盘（变更记录 + 新不变式 + `DraftsCommandNames`）；`CONTRACT-UNFREEZE` 记录；新 pin 由 DSH 签发；`verify_pins.ps1` 全绿。<<TODO>>
- [ ] **AC2 端口面**：`IHostController` 6 方法 + 实现 + Null 默认；`App.Tests` 覆盖（fake/failure 路径）；既有方法不回归。<<TODO>>
- [ ] **AC3 CoreClient registry**：6 条模型/注册/路由；`V11RAdditiveCommandNames` = 17；`CommandParityContractTests` 通过。<<TODO>>
- [ ] **AC4 契约测试**：`RegionWriteCommandTests` 改为并集断言且 Region 子集仍成立；`CommandContractV11RTests` 通过。<<TODO>>
- [ ] **AC5 端口清单**：`generate_api_inventory.py --check` EXIT 0（C-07 清单同步）。<<TODO>>
- [ ] **AC6 回归**：全量 `dotnet build` + `dotnet test ... --no-build --settings .../NewManga.runsettings` 不退化（基线 931/0/60）。<<TODO>>
- [ ] **AC7 证据**：`verification/FEA-05-PORT-1/**` 原始日志 + 证据表。<<TODO>>

## 禁止范围

- 不改 Core handler/契约 §8.2（FEA-05-WIRE-1 已交付）；不改 UI 行为/页面；不改 schema；不动用户数据；不 push；不合并 main（本卡直接 main 实现，由 DSH 提交）。
- 不把 Draft 命令接入 UI 交互（FEA-06 负责）。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 是否必须 UNFREEZE Region 契约？ | **是**：不变式（追加集 = RegionWrite ∪ RegionRead）与新家族冲突，只能改契约；走 v1.6 + UNFREEZE 记录 + 新 pin | FEA-05-WIRE-1 impl-r4 复核发现（`RegionWriteCommandTests:107-117` vs 契约 `:62-63/344-346/457`） |
| W-2 | 端口方法名 | `OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync`/`ApplyCandidatesAsync`/`GetDraftStatusAsync`/`DiscardDraftAsync`（与 wire 命令一一对应） | 与 `IHostController` 既有命名风格一致 |
| W-3 | `V11RAdditiveCommandNames` 语义 | 扩为 17（RegionWrite 10 + RegionRead 1 + Drafts 6）；`RegionWriteCommandNames`/`RegionReadCommandNames` 保持原集合 | 契约 v1.6 的并集定义 |
| W-4 | 证据与冻结 | 卡内产出 UNFREEZE 记录 + 契约 v1.6 + 新 pin；DSH 复核后提交；`verify_pins` 必须 15/15（pin 数量不变，pin 值更新） | 契约冻结纪律 |

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `verify_pins.ps1` + 契约 diff | 治理 | NOT_RUN | 待补 |
| AC2/AC3/AC4 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests` + `NewManga.CoreClient.Tests` | .NET | NOT_RUN | 待补 |
| AC5 | `python tools/governance/generate_api_inventory.py --check` | 治理 | NOT_RUN | 待补 |
| AC6 | `dotnet build apps/desktop-avalonia/NewManga.sln` + `dotnet test ... --no-build --settings .../NewManga.runsettings` | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）；资源处置在收口时登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
