---
id: FEA-05-WIRE-1
title: Draft 命令面 wire（Core 白名单 + 命令契约 + CoreClient registry）
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
base_commit: 7122d5696
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-05-WIRE-1
allowed_paths:
  - doc/tasks/FEA-05-WIRE-1.md
  - doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md
  - doc/contracts/V11R_COMMAND_CONTRACT_V1.md
  - src/bootstrap/core_service.py
  - tests/core/**
  - tests/domain/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**
  - verification/FEA-05-WIRE-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-05-WIRE-1-*.md
---

# FEA-05-WIRE-1：Draft 命令面 wire（v3，可执行规格）

## 来源与授权链

- FEA-03 Q-8（wire 由 FEA-04 承担）→ FEA-04 Q-16（不接 wire）→ 本卡顺延
- 方案 §15.6；AD-002（UI 经 Host/IPC 与 Core 契约访问）
- 上游实现：FEA-03 Core drafts 服务（`src/application/editing/**` 已实现；本卡**不改**其语义，故不取得其写权）

## 范围收窄与规格（r1/r2 复核处置）

| # | 复核项 | 处置 |
|---|---|---|
| r1-P0-01 | 命令无契约载体 | 新建 `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`（独立命令契约，参考 `V11R_REGION_WRITE_CONTRACT.md` 结构）+ 在 `V11R_COMMAND_CONTRACT_V1.md` §8 追加 C078–C083 指针行 |
| r1-P0-02 | C-07 端口冲突 | 本卡**不接** `IHostController`/`HostController`/`NullHostController`（端口面另卡 FEA-05-PORT-1） |
| r1-P0-03 | Python 测试无写域 | `tests/core/**`、`tests/domain/**` 纳入写域 |
| r1-P1-01 / r2-P1-01 | `close` 二义 + 契约登记格式不可执行 | 命令集合 6 条且**下划线命名**（§8 解析器正则 `^[a-z][a-z0-9_]*$` 过滤点号名）；独立契约文档 + §8 指针行 |
| r2-P1-02 | 方法名 4/5 不存在 | 按真实服务方法映射（见下表） |
| r2-P1-04 | CoreClient 漏 registry/parity | `HostCommandRegistry` 新增 6 条（域 `Drafts`、通道 `core`、minor 3）；`V11RAdditiveCommandNames` 与 `CommandParityContractTests` 同步 |
| r2-P1-03 | 模板两节缺失 | 契约文档按 Region 契约结构：范围/非目标、命令清册、请求/响应、错误码、兼容性 |
| r2-P2-01 | `tests/domain/**` 未入写域 | 已纳入 |
| r2-P1-05 | 写域含 `src/application/editing/**` 过宽 | **移除**（本卡不改编辑语义） |

## 命令清册与映射（冻结）

| ID | Host 命令 | 域 | 通道 | minor | Core 方法（真实） | 关键参数 |
|---|---|---|---|---|---|---|
| C078 | `drafts_open` | Drafts | core | 3 | `open_draft(session_id, target, page_binding_version)` | session_id、target(page/book/chapter/page)、page_binding_version |
| C079 | `drafts_patch` | Drafts | core | 3 | `patch_draft(draft_id, patches)` | draft_id、patches[]（region 类型/文本补丁） |
| C080 | `drafts_prepare` | Drafts | core | 3 | `prepare_candidate(draft_id)`（或 `prepare_candidates`，按服务现有签名） | draft_id |
| C081 | `drafts_apply` | Drafts | core | 3 | `apply_candidates(token_id, draft_ids)` | token_id（`EditToken`）、draft_ids[] |
| C082 | `drafts_status` | Drafts | core | 3 | `get_draft(draft_id)` / `list_drafts(session_id)`（二选一按 payload） | draft_id 或 session_id |
| C083 | `drafts_discard` | Drafts | core | 3 | `discard_draft(draft_id)` | draft_id |

> **命名**：Host 命令面统一下划线（与 §8 既有 `create_region` 一致）；Core 服务方法保持既有 `snake_case`。点号名（`drafts.open`）**不得**用于 Host 命令（解析器会过滤）。

## 交付范围（DSH 冻结）

| 层 | 内容 |
|---|---|
| 契约文档 | 新建 `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`：范围/非目标、C078–C083 清册、请求/响应外形、错误码（复用 `drafts.py` 既有错误码，14 新/3 复用按 r2 更正）、兼容性（zero protocol bump、minor 3）、实现位置指针 |
| §8 指针行 | `V11R_COMMAND_CONTRACT_V1.md` §8 追加 6 行，格式：`\| C078 \| \`drafts_open\` \| Drafts \| core \| 3（zero protocol bump） \| \`PENDING(FEA-05-WIRE-1)\` \|`；**手工追加、不重跑生成器**（§8 由 `build_contract_doc.py:459-480` 模板生成，重跑会覆盖） |
| Core handler | `core_service.py` 白名单加 6 命令；handler 调用上表真实方法；错误码透传既有结构 |
| CoreClient | `HostCommandModel` 增加 6 条请求/响应；`HostCommandRegistry` 注册（域 `Drafts`、通道 `core`、minor 3）；`HostCommandDispatcher` 路由 |
| 测试 | Python `tests/core/test_draft_commands.py`（成功/未知命令/非法 payload/错误码）；CoreClient 测试（序列化/registry/parity/错误映射）；`V11RAdditiveCommandNames` 同步 |

## 验收标准

- [ ] **AC1 契约**：`FEA-05_DRAFT_WIRE_CONTRACT.md` 与 §8 指针行落盘；`CommandContractV11RTests` 通过（6 条在 §8 可解析、命令名下划线、状态 `PENDING` 开头、不在已冻结集合）。<<TODO>>
- [ ] **AC2 语义不变**：handler 只调用上表真实方法；不新增编辑规则、不改 token/candidate/receipt 语义（FEA-03 r5 冻结）。<<TODO>>
- [ ] **AC3 CoreClient**：6 条请求/响应模型；`HostCommandRegistry` 注册（域/通道/minor）；`CommandParityContractTests` 通过（新增集合 = `V11RAdditiveCommandNames`、每域非空、CoreService 通道带 `CoreCommand` + `CoreMinor>0`）。<<TODO>>
- [ ] **AC4 Python 协议测试**：`python -m pytest tests/core tests/domain -q` 全绿（含新测试；未知命令/非法 payload 被拒）。<<TODO>>
- [ ] **AC5 回归**：`dotnet build apps/desktop-avalonia/NewManga.sln` EXIT=0；`dotnet test ... --no-build --settings .../NewManga.runsettings` 不退化（基线 931/0/60）。<<TODO>>
- [ ] **AC6 治理**：`verify_pins.ps1` 15/15；C-07 端口清单不变；`generate_api_inventory.py --check` EXIT 0；`check.ps1` PASS。<<TODO>>
- [ ] **AC7 证据**：`verification/FEA-05-WIRE-1/**` 原始日志 + 测试输出 + 证据表。<<TODO>>

## 禁止范围

- 不接 IHostController/HostController/NullHostController（端口面另卡）；不改 Host 生命周期/凭据。
- 不改 `src/application/editing/**`（编辑语义）；不改 schema/migrations；不改 C-02/C-03/C-04b/C-08 冻结字节。
- 不改 UI（Current/Fluent）；不动用户数据；不 push；不合并 main。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 命令面是兼容扩展还是新协议？ | **兼容扩展 + 独立契约文档**：命令登记进 §8（C078–C083，PENDING→合入后 FROZEN），复用既有 JSON-lines 信封与错误结构，zero protocol bump | `V11R_REGION_WRITE_CONTRACT.md` 先例（F0-1 走「独立契约 + §8 指针行」）；`core_service.py:451-457` |
| W-2 | 是否接 UI？ | **否**（只到 CoreClient 命令面） | FEA-04 Q-16/Q-19 |
| W-3 | 命令集合与命名 | **6 条下划线命令**（上表）；不含 `close`；session 结束归 session 层 | r1/r2 复核；§8 解析器正则 |
| W-4 | 失败语义 | 复用既有错误结构（code/message/details）；不静默 | FEA-03 |
| W-5 | 契约文档归属 | `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md` 由本卡产出，DSH 复核后冻结；`V11R_COMMAND_CONTRACT_V1.md` §8 只追加指针行 | Region 契约先例 |

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC4 | `python -m pytest tests/core tests/domain -q` | Core | NOT_RUN | 待补 |
| AC3 | `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests` | .NET | NOT_RUN | 待补 |
| AC5 | `dotnet build apps/desktop-avalonia/NewManga.sln` + `dotnet test ... --no-build --settings .../NewManga.runsettings` | 全量 | NOT_RUN | 待补 |
| AC6 | `verify_pins.ps1` + `generate_api_inventory.py --check` + `check.ps1` | 治理 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（实现提交由 DSH 集成）；资源处置在收口时登记。

## Closeout Record

- 2026-11-02 / DSH：范围 v1 → v2（r1 P0×3/P1×5）→ **v3**（r2 P0=0/P1×5）：新建独立契约文档、§8 指针行模板、真实方法映射表、CoreClient registry/parity、写域修正。待 r3 复核。
