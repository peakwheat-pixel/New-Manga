# Draft 命令面契约 v1.0（PENDING）

状态：`PENDING`（FEA-05-WIRE-1 交付；独立复核 r7 approved 范围，实现完成后由 DSH 复核转 FROZEN）
版本：`v1.0`
日期：2026-11-02
归属：DSH（Lead / Integrator）；实现：Codex/DSH
上游：FEA-03（Core drafts 服务，已 done）、FEA-04（Current 适配，已 done）、M2-C1 rev 1.x（JSON-lines 信封）
实现位置：`src/bootstrap/core_service.py`（handler）、`src/application/editing/drafts.py`（use case）、`src/domain/drafts/entities.py`（EditToken/DraftLease）
命令清册编号：本文件是总契约 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的 **C078–C083** 节（总契约 §8 只追加指针行）。

变更记录：
- v1.0（2026-11-02）：初版，6 条命令（open/patch/prepare/apply/status/discard），zero protocol bump（minor 3）。

---

## 0. 范围与非目标

本契约冻结 Draft 命令面：把 FEA-03 已实现的 Core drafts 服务经 Host wire 暴露给 CoreClient/UI。

**非目标**：不改编辑语义（token/candidate/receipt/journal/锁）；不改 schema；不接 IHostController/CoreClient registry（归 FEA-05-PORT-1）；不做 UI 改造。

## 1. 命令清册

| ID | Host 命令 | 域 | 通道 | minor | Core 方法 | 请求字段 | 响应 |
|---|---|---|---|---|---|---|---|
| C078 | `drafts_open` | Drafts | core | 3 | `open_draft(session_id, page_id, region_id, *, base_revision_id, page_binding_version)` | `sessionId`, `pageId`, `regionId?`, `baseRevisionId?`, `pageBindingVersion` | `{ "draft": Draft, "canEdit": bool, "token": EditToken|null }` |
| C079 | `drafts_patch` | Drafts | core | 3 | `patch_draft(draft_id, session_id, patch, *, undo_cursor=None, schedule_flush=True)` | `draftId`, `sessionId`, `patch`（对象）, `undoCursor?` | `{ "draft": Draft }` |
| C080 | `drafts_prepare` | Drafts | core | 3 | `prepare_candidate(region_id, patch, *, origin, draft_id=None, base_revision_id=None)` | `regionId`, `patch`（对象）, `origin`, `draftId?`, `baseRevisionId?` | `{ "candidate": RegionCandidate }` |
| C081 | `drafts_apply` | Drafts | core | 3 | `apply_candidates(token: EditToken \| Mapping, candidate_ids=())` | `token`（整份 EditToken JSON）, `candidateIds[]` | `{ "<region_id>": "<region_revision_id>" }`（receipt 元数据不在此返回） |
| C082 | `drafts_status` | Drafts | core | 3 | `get_draft(draft_id)` 或 `list_drafts(session_id=…)` | `draftId` 或 `sessionId`（恰好一个） | `{ "draft": Draft }` 或 `{ "drafts": Draft[] }` |
| C083 | `drafts_discard` | Drafts | core | 3 | `discard_draft(draft_id, session_id)` | `draftId`, `sessionId` | `{ "discarded": true }` |

## 2. 请求/响应外形

- 信封：既有 JSON-lines（`request_id`/`command`/`payload` → `result`/`error`），不新增版本。
- 字段命名：wire 用 camelCase；Core 内部 snake_case。handler 负责映射。
- `EditToken` 六字段（`EditToken.to_json()` 原样）：`tokenId`、`DraftId`、`DraftSequence`、`SessionId`、`issuedAt`、`expiresAt`。
- `Draft` 外形以 `Draft.to_json()` 为准（`draft_id`/`session_id`/`page_id`/`region_id`/`draft_sequence`/`status`/`patches` 等）。
- `RegionCandidate`：`candidateId`/`RegionId`/`BaseRevisionId`/`Origin`（按 `to_json()` 实现）。

## 3. 错误码（逐码表，优先于类别规则）

错误信封：`code`/`category`/`message`/`retryable`/`details`（`cause_code` → `details.causeCode`）。category 只用 M2-C1 冻结词表：`validation` / `not_found` / `conflict` / `unavailable` / `cancelled` / `internal` / `unknown`。

| code | category | retryable | 触发条件 |
|---|---|---|---|
| `DRAFT_INVALID` | validation | false | 必填字段缺失/类型错 |
| `DRAFT_PATCH_INVALID` | validation | false | patch 非对象/文本补丁非法 |
| `DRAFT_CANDIDATE_INVALID` | validation | false | candidate 参数/origin 非法 |
| `DRAFT_READ_ONLY` | conflict | false | 另一 Session 持有该 Region |
| `DRAFT_SEQUENCE_MISMATCH` | conflict | false | token/draft sequence 不一致 |
| `DRAFT_ALREADY_FLUSHED` | conflict | false | 对已 flush draft 继续 patch |
| `EDIT_TOKEN_INVALID` | validation | false | token 字段缺失/非法 |
| `EDIT_TOKEN_EXPIRED` | conflict | false | token 过期 |
| `EDIT_TOKEN_DRAFT_CHANGED` | conflict | false | token 与 draft 不再匹配 |
| `TARGET_NOT_FOUND` | not_found | false | draft/region/candidate 不存在 |
| `LOCK_CHANGED` | conflict | true | 并发锁变更（可重试） |
| `PAGE_SIZE_UNAVAILABLE` | unavailable | true | 页面尺寸暂不可用（可重试） |
| `DRAFT_JOURNAL_UNWRITABLE` | unavailable | true | journal 不可写（fail-closed） |
| `INTERNAL` | internal | true | 未分类内部错误 |

## 4. 兼容性

- **zero protocol bump**：命令为既有 M2-C1 协议的兼容扩展（新增命令，不改既有语义）；`PROTOCOL_MINOR` 保持 3（与 Region C067–C077 同口径，依据 `core_service.py:451-457` 先例）。
- **additive 集合**：本契约不修改 `V11RAdditiveCommandNames`（CoreClient registry 归 FEA-05-PORT-1）。
- **未注册命令**：Core 对未知命令返回 `UNKNOWN`/`validation`（既有行为）。

## 5. 实现位置与测试指针

- `src/bootstrap/core_service.py`：`_dispatch_draft_command` + 6 handler；白名单在 `_dispatch_request` 内。
- `tests/core/test_draft_commands.py`：每命令成功 + 失败（未知命令/非法 payload/关键错误码）。
