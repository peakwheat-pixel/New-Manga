---
id: FEA-05-WIRE-1
title: Draft 命令面 wire（Core 白名单 + 独立契约 + Python 协议测试）
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
base_commit: 25b69b974
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
  - verification/FEA-05-WIRE-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-05-WIRE-1-*.md
---

# FEA-05-WIRE-1：Draft 命令面 wire（v5，收窄至 Core 面）

## 来源与授权链

- FEA-03 Q-8（wire 由 FEA-04 承担）→ FEA-04 Q-16（不接 wire）→ 本卡顺延
- 方案 §15.6；AD-002（UI 经 Host/IPC 与 Core 契约访问）
- 上游实现：FEA-03 Core drafts 服务（`src/application/editing/drafts.py`、`src/domain/drafts/entities.py`），**本卡不改其语义**（不取得其写权）

## 复核收敛记录

| 轮次 | 结论 | 处置 |
|---|---|---|
| r1 | changes_requested（P0×3/P1×5） | 纳入契约载体 + Python 测试写域；去掉 C-07 端口面与 `drafts.close` |
| r2 | changes_requested（P0=0/P1×5） | 独立契约文档 + §8 指针行 + CoreClient registry/parity + 写域修正 |
| r3 | changes_requested（P0=0/P1×2） | 映射表按真实签名重写；W-4 错误/Token 传输冻结；契约文档必需内容与 §8 一致性 |
| r4 | changes_requested（P0×1/P1×2） | **v5**：C081 响应改真实 `{region_id: region_revision_id}`；W-4 category 改 M2-C1 冻结词表；**收窄不接 CoreClient/registry**（Region 不变式与 FROZEN 契约不冲突），registry 归 FEA-05-PORT-1 |

## 命令清册与真实签名映射（冻结，v4）

Host 命令统一下划线（§8 解析器正则 `^[a-z][a-z0-9_]*$`）；参数列即 wire 字段名（Core handler 按列解包，不额外改名）。

| ID | Host 命令 | Core 方法（`drafts.py` 真实签名） | wire 请求字段 | wire 响应（最少） |
|---|---|---|---|---|
| C078 | `drafts_open` | `open_draft(session_id, page_id, region_id, *, base_revision_id, page_binding_version) -> DraftLease` | `sessionId`, `pageId`, `regionId?`, `baseRevisionId?`, `pageBindingVersion` | `draft`（Draft.to_json）、`canEdit`、`token?`（EditToken.to_json） |
| C079 | `drafts_patch` | `patch_draft(draft_id, session_id, patch, *, undo_cursor=None, schedule_flush=True) -> Draft` | `draftId`, `sessionId`, `patch`（对象）, `undoCursor?` | `draft` |
| C080 | `drafts_prepare` | `prepare_candidate(region_id, patch, *, origin, draft_id=None, base_revision_id=None) -> RegionCandidate` | `regionId`, `patch`（对象）, `origin`, `draftId?`, `baseRevisionId?` | `candidate`（RegionCandidate.to_json） |
| C081 | `drafts_apply` | `apply_candidates(token: EditToken \| Mapping, candidate_ids: Sequence[str] = ()) -> dict[str,str]` | `token`（**整份 EditToken JSON，六字段原样回传**）, `candidateIds[]` | `{ "<region_id>": "<region_revision_id>" }`（真实返回值，`drafts.py:500-507/528`；receipt 元数据不在此返回） |
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
| CoreClient | **不在本卡**（W-6）：`HostCommandModel`/`HostCommandRegistry`/`HostCommandDispatcher`/`V11RAdditiveCommandNames` 归 **FEA-05-PORT-1**（需先契约 UNFREEZE） |
| 测试 | Python：`tests/core/test_draft_commands.py`（每命令成功路径 + 未知命令 + 非法 payload + 关键错误码：DRAFT_READ_ONLY / DRAFT_INVALID / EDIT_TOKEN_EXPIRED / RECEIPT 相关）； |

## 验收标准

- [ ] **AC1 契约**：`FEA-05_DRAFT_WIRE_CONTRACT.md` 落盘且含头部（状态/版本/日期/变更记录）与五节；§3 **必须是逐码表**（每码一行：code/category/retryable/触发条件），与 W-4 冲突时以逐码表为准；§8 追加 6 行且 `CommandContractV11RTests` 通过（行在 §8 内、下划线名、状态 `PENDING` 开头、不进入已冻结集合）；§8 段首总数/约束/§10 已同步。<<TODO>>
- [ ] **AC2 语义不变**：handler 参数与上表逐字段一致（含 `EditToken` 整对象回传）；只调用真实方法；不新增编辑规则、不改 token/candidate/receipt 语义（FEA-03 r5 冻结）。<<TODO>>
- [x] **AC3 CoreClient（不在本卡）**：本卡不接 CoreClient/registry（归 FEA-05-PORT-1，见 W-6）；本 AC 记为 NOT_APPLICABLE 并说明。<<NOT_APPLICABLE: CoreClient 注册与 Region 不变式冲突，归 FEA-05-PORT-1>>
- [ ] **AC4 Python 协议测试**：`python -m pytest tests/core tests/domain -q` 全绿；每命令至少一成功 + 一失败用例。<<TODO>>
- [ ] **AC5 回归**：`dotnet build apps/desktop-avalonia/NewManga.sln` EXIT=0；`dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` 不退化（基线 931/0/60）。<<TODO>>
- [ ] **AC6 治理**：`verify_pins.ps1` 15/15；C-07 端口清单不变；`generate_api_inventory.py --check` EXIT 0；`check.ps1` PASS。<<TODO>>
- [ ] **AC7 证据**：`verification/FEA-05-WIRE-1/**` 原始日志 + 测试输出 + 证据表。<<TODO>>

## 禁止范围

- 不接 `IHostController`/`HostController`/`NullHostController`（端口面另卡 FEA-05-PORT-1，已登记）；不改 Host 生命周期/凭据。
- 不改 `src/application/editing/**`（编辑语义）；不改 schema/migrations；不改 C-02/C-03/C-04b/C-08 冻结字节。
- 不改 UI（Current/Fluent）；不动用户数据；不 push；不合并 main。

## L-2 前置判定
- **L-2（M2-C1 字节修订）**：本卡新增 Host 命令面与 wire 码，**触发** L-2（`FEA-04.md:99`/`FEA-03.md:153`：「新增 Host/Core 命令或 wire 码 → blocked（先完成 M2-C1）」）。**解除依据**：W-1 裁决——按 F0-1 先例走「§8 追加 + 独立契约文档」的兼容扩展，M2-C1 不逐族追加；本卡同时产出 `V11R_COMMAND_CONTRACT_V1.md` §8 指针行，L-2 判定为「已按 W-1 解除」。
- **L-1（四表 DDL 未冻）**：本卡不改 schema/迁移 → **NOT_APPLICABLE**。
- **L-5（整库恢复独占锁）**：本卡无恢复/备份路径 → **NOT_APPLICABLE**。
## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 命令面是兼容扩展还是新协议？ | **兼容扩展 + 独立契约文档**：§8 追加 C078–C083（PENDING→合入后 FROZEN），复用既有 JSON-lines 信封与错误结构，zero protocol bump | `V11R_REGION_WRITE_CONTRACT.md` 先例；`core_service.py:451-457` |
| W-2 | 是否接 UI/CoreClient？ | **否**：本卡只到 Core 命令面 + 契约 + Python 测试；CoreClient/registry/UI 归 FEA-05-PORT-1 | FEA-04 Q-16/Q-19 |
| W-3 | 命令集合与命名 | **6 条下划线命令**（上表）；不含 `close`；session 结束归 session 层；`flush(trigger)` 不在本卡（见 W-7） | r1/r2/r3 复核；§8 解析器 |
| W-4 | 错误语义与 Token 传输 | **冻结**：错误结构 = `code`/`message`/`category`/`retryable`/`details`；`DraftError` 的 14 个新 wire 码逐码映射为 **M2-C1 冻结词表** 的 `category`（`validation`/`not_found`/`conflict`/`unavailable`/`cancelled`/`internal`/`unknown`，**不用 `infra`**）+ `retryable`（bool，默认 false；仅 `unavailable`/`internal` 类为 true；`cause_code` 透传为 `details.causeCode`）；逐码表写入契约文档 §3；`EditToken` **整对象原样回传**（六字段），handler 不得拆分/重建；receipt 重放按 `draft_sequence` 键幂等 | `drafts.py`/`errors.py`；FEA-03 r5 |
| W-5 | 契约文档归属与冻结流程 | 文档由本卡产出；DSH 复核后置 `FROZEN`（本卡交付 `PENDING`，合入 main 后升级）；§8 只追加指针行，不重跑生成器 | Region 契约先例 |
| W-6 | `V11RAdditiveCommandNames` 语义与 Region 不变式 | **本卡不接 CoreClient/registry**——`RegionWriteCommandTests` 的不变式（追加集 == RegionWrite ∪ RegionRead，出自 FROZEN `V11R_REGION_WRITE_CONTRACT.md`）保持原样；drafts 命令的 registry 注册与 additive 集合扩展归 **FEA-05-PORT-1**（该卡需先走契约 UNFREEZE 把不变式升级为「各家族集合之并」） | r4 P0-01；避免改冻结契约 |
| W-7 | `flush(trigger)`/session 结束 | **不在本卡**：`patch_draft(schedule_flush=…)` 已存在；flush 触发点归 FEA-03 C-13 SC-D02 语义与 session 层，本卡只透传既有参数 | FEA-03 |

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC4 | `python -m pytest tests/core tests/domain -q` | Core | NOT_RUN | 待补 |
| AC3 | NOT_APPLICABLE（CoreClient 不在本卡） | — | N/A | — |
| AC5 | `dotnet build apps/desktop-avalonia/NewManga.sln` + `dotnet test ... --no-build --settings .../NewManga.runsettings` | 全量 | NOT_RUN | 待补 |
| AC6 | `verify_pins.ps1` + `generate_api_inventory.py --check` + `check.ps1` | 治理 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（实现提交由 DSH 集成）；资源处置在收口时登记。

## Closeout Record

- 2026-11-02 / DSH：v1 → v2（r1）→ v3（r2）→ v4（r3）→ **v5（r4）**：映射表按 `drafts.py`/`domain/drafts/entities.py` 真实签名重写；W-4 冻结错误/Token 传输；契约文档头部与 §8 一致性要求；W-6/W-7 裁决登记。待 r4 复核。
