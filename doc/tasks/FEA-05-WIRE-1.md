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
base_commit: a62d9ca10
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

# FEA-05-WIRE-1：Draft 命令面 wire（v4，签名冻结版）

## 来源与授权链

- FEA-03 Q-8（wire 由 FEA-04 承担）→ FEA-04 Q-16（不接 wire）→ 本卡顺延
- 方案 §15.6；AD-002（UI 经 Host/IPC 与 Core 契约访问）
- 上游实现：FEA-03 Core drafts 服务（`src/application/editing/drafts.py`、`src/domain/drafts/entities.py`），**本卡不改其语义**（不取得其写权）

## 复核收敛记录

| 轮次 | 结论 | 处置 |
|---|---|---|
| r1 | changes_requested（P0×3/P1×5） | 纳入契约载体 + Python 测试写域；去掉 C-07 端口面与 `drafts.close` |
| r2 | changes_requested（P0=0/P1×5） | 独立契约文档 + §8 指针行 + CoreClient registry/parity + 写域修正 |
| r3 | changes_requested（P0=0/P1×2） | **本 v4**：映射表按真实签名重写；W-4 错误/Token 传输冻结；契约文档必需内容与 §8 一致性 |

## 命令清册与真实签名映射（冻结，v4）

Host 命令统一下划线（§8 解析器正则 `^[a-z][a-z0-9_]*$`）；参数列即 wire 字段名（Core handler 按列解包，不额外改名）。

| ID | Host 命令 | Core 方法（`drafts.py` 真实签名） | wire 请求字段 | wire 响应（最少） |
|---|---|---|---|---|
| C078 | `drafts_open` | `open_draft(session_id, page_id, region_id, *, base_revision_id, page_binding_version) -> DraftLease` | `sessionId`, `pageId`, `regionId?`, `baseRevisionId?`, `pageBindingVersion` | `draft`（Draft.to_json）、`canEdit`、`token?`（EditToken.to_json） |
| C079 | `drafts_patch` | `patch_draft(draft_id, session_id, patch, *, undo_cursor=None, schedule_flush=True) -> Draft` | `draftId`, `sessionId`, `patch`（对象）, `undoCursor?` | `draft` |
| C080 | `drafts_prepare` | `prepare_candidate(region_id, patch, *, origin, draft_id=None, base_revision_id=None) -> RegionCandidate` | `regionId`, `patch`（对象）, `origin`, `draftId?`, `baseRevisionId?` | `candidate`（RegionCandidate.to_json） |
| C081 | `drafts_apply` | `apply_candidates(token: EditToken \| Mapping, candidate_ids: Sequence[str] = ()) -> dict[str,str]` | `token`（**整份 EditToken JSON，六字段原样回传**）, `candidateIds[]` | `receipt`（键=`draft_sequence` 字符串，值=状态） |
| C082 | `drafts_status` | `get_draft(draft_id) -> Draft` 或 `list_drafts(*, session_id=None) -> list[Draft]`（按 payload 二选一） | `draftId?` 或 `sessionId?`（恰好一个） | `draft` 或 `drafts[]` |
| C083 | `drafts_discard` | `discard_draft(draft_id, session_id) -> None` | `draftId`, `sessionId` | `{ "discarded": true }` |

**EditToken 六字段**（JSON 键大小写以 `EditToken.to_json()` 为准）：`tokenId`、`DraftId`、`DraftSequence`、`SessionId`、`issuedAt`、`expiresAt`。
**DraftLease**：`draft`、`can_edit`、`token`（`token=None` 时 wire 省略或 `null`）。

> 实现要求：handler 解包时**逐字段**校验（类型/必填）；`apply` 必须**整对象**校验（`_token_from_json` 逐字段 + 服务内部 `issued != edit_token` 整对象相等语义），不得拆分/重建 token。

## 交付范围（DSH 冻结）

| 层 | 内容 |
|---|---|
| 契约文档 | 新建 `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`：**头部**（状态 `PENDING` / 版本 `v1.0` / 日期 / 归属 / 上游与实现指针 / 变更记录）、0 范围与非目标、1 命令清册（上表）、2 请求/响应外形、3 错误码与语义、4 兼容性（zero protocol bump / minor 3 / additive 集合）、5 实现位置与测试指针 |
| §8 指针行 | `V11R_COMMAND_CONTRACT_V1.md` §8 **末尾**（`## 8.` 与 `## 9.` 之间）追加 C078–C083 六行；同步更新 §8 段首说明（命令总数、`PENDING` 口径）、约束段、§10 变更记录（追加一行版本说明）；**手工追加、不重跑生成器**（§8 由 `build_contract_doc.py:459-480` 模板生成，重跑会覆盖） |
| Core handler | `core_service.py` 白名单 + handler：6 命令按上表调用真实方法；`DraftError` → 既有错误结构（含 `code`/`message`/`category`/`retryable`/`details`） |
| CoreClient | `HostCommandModel` 6 条请求/响应；`HostCommandRegistry` 注册（域 `Drafts`、通道 `core`、minor 3）；`HostCommandDispatcher` 路由；`V11RAdditiveCommandNames` 同步（见 W-6） |
| 测试 | Python：`tests/core/test_draft_commands.py`（每命令成功路径 + 未知命令 + 非法 payload + 关键错误码：DRAFT_READ_ONLY / DRAFT_INVALID / EDIT_TOKEN_EXPIRED / RECEIPT 相关）；CoreClient：序列化/registry/parity/错误映射 |

## 验收标准

- [ ] **AC1 契约**：`FEA-05_DRAFT_WIRE_CONTRACT.md` 落盘且含头部（状态/版本/日期/变更记录）与五节；§8 追加 6 行且 `CommandContractV11RTests` 通过（行在 §8 内、下划线名、状态 `PENDING` 开头、不进入已冻结集合）；§8 段首总数/约束/§10 已同步。<<TODO>>
- [ ] **AC2 语义不变**：handler 参数与上表逐字段一致（含 `EditToken` 整对象回传）；只调用真实方法；不新增编辑规则、不改 token/candidate/receipt 语义（FEA-03 r5 冻结）。<<TODO>>
- [ ] **AC3 CoreClient**：6 条请求/响应；`HostCommandRegistry` 注册（域/通道/minor 3）；`CommandParityContractTests` 通过。<<TODO>>
- [ ] **AC4 Python 协议测试**：`python -m pytest tests/core tests/domain -q` 全绿；每命令至少一成功 + 一失败用例。<<TODO>>
- [ ] **AC5 回归**：`dotnet build apps/desktop-avalonia/NewManga.sln` EXIT=0；`dotnet test ... --no-build --settings .../NewManga.runsettings` 不退化（基线 931/0/60）。<<TODO>>
- [ ] **AC6 治理**：`verify_pins.ps1` 15/15；C-07 端口清单不变；`generate_api_inventory.py --check` EXIT 0；`check.ps1` PASS。<<TODO>>
- [ ] **AC7 证据**：`verification/FEA-05-WIRE-1/**` 原始日志 + 测试输出 + 证据表。<<TODO>>

## 禁止范围

- 不接 `IHostController`/`HostController`/`NullHostController`（端口面另卡 FEA-05-PORT-1，已登记）；不改 Host 生命周期/凭据。
- 不改 `src/application/editing/**`（编辑语义）；不改 schema/migrations；不改 C-02/C-03/C-04b/C-08 冻结字节。
- 不改 UI（Current/Fluent）；不动用户数据；不 push；不合并 main。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 命令面是兼容扩展还是新协议？ | **兼容扩展 + 独立契约文档**：§8 追加 C078–C083（PENDING→合入后 FROZEN），复用既有 JSON-lines 信封与错误结构，zero protocol bump | `V11R_REGION_WRITE_CONTRACT.md` 先例；`core_service.py:451-457` |
| W-2 | 是否接 UI？ | **否**（只到 CoreClient 命令面） | FEA-04 Q-16/Q-19 |
| W-3 | 命令集合与命名 | **6 条下划线命令**（上表）；不含 `close`；session 结束归 session 层；`flush(trigger)` 不在本卡（见 W-7） | r1/r2/r3 复核；§8 解析器 |
| W-4 | 错误语义与 Token 传输 | **冻结**：错误结构 = `code`/`message`/`category`/`retryable`/`details`；`DraftError` 的 14 个新 wire 码（r2 复算）逐码映射为 `category`（`validation`/`conflict`/`infra`）+ `retryable`（bool，默认 false，`DRAFT_JOURNAL_UNWRITABLE`/锁冲突 true）；`EditToken` **整对象原样回传**（六字段），handler 不得拆分/重建；receipt 重放按 `draft_sequence` 键幂等 | `drafts.py`/`errors.py`；FEA-03 r5 |
| W-5 | 契约文档归属与冻结流程 | 文档由本卡产出；DSH 复核后置 `FROZEN`（本卡交付 `PENDING`，合入 main 后升级）；§8 只追加指针行，不重跑生成器 | Region 契约先例 |
| W-6 | `V11RAdditiveCommandNames` 语义 | **本卡追加 C078–C083 到该集合**（该属性 docstring 原述 V11R-F0-1/F0-2 集合；本卡按「additive 命令名清单」语义扩展并在契约文档 §4 记录）；若复核认为应另立集合，退回 DSH 裁决 | `CommandParityContractTests.cs:88-91` |
| W-7 | `flush(trigger)`/session 结束 | **不在本卡**：`patch_draft(schedule_flush=…)` 已存在；flush 触发点归 FEA-03 C-13 SC-D02 语义与 session 层，本卡只透传既有参数 | FEA-03 |

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

- 2026-11-02 / DSH：v1 → v2（r1）→ v3（r2）→ **v4（r3）**：映射表按 `drafts.py`/`domain/drafts/entities.py` 真实签名重写；W-4 冻结错误/Token 传输；契约文档头部与 §8 一致性要求；W-6/W-7 裁决登记。待 r4 复核。
