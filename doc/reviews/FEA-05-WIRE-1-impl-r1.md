---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: be9265b34
reviewed_head: 311b79575
decision: changes_requested
counts: { P0: 0, P1: 5, P2: 8 }
---

# FEA-05-WIRE-1 实现复核 r1（同一独立席位；只审过范围、未参与实现）

| 字段 | 值 |
|---|---|
| base_commit | `be9265b342c60a98d63b06b832694aac775f3797`（范围冻结 v5.2，r7 approved） |
| reviewed_head | `311b79575b2870aa3efeec3cebecb992e48a6610`（`feat(fea-05-wire-1): Draft 命令面 wire（C078–C083）…`；`git status --porcelain` 为空） |
| 被审对象 | 实现提交：`doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`（新增）、`doc/contracts/V11R_COMMAND_CONTRACT_V1.md`、`src/bootstrap/core_service.py`、`tests/core/test_draft_commands.py`、`verification/FEA-05-WIRE-1/**`、卡与三份指针文档 |
| 与 base 的 diff | `git diff --stat be9265b34..311b79575` → 14 files, +699/−43；核心实现 = `core_service.py` +141、`test_draft_commands.py` +178、契约文档 +71、§8 +39 |
| reviewer | `fea05-wire-scope-reviewer`（r1→r7 范围复核同一席位；本轮首次审实现，**未参与实现**——实现者为 DSH，符合 2026-10-31「上下文独立」裁决） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | AC1–AC7 逐项、实现与冻结契约/真实服务签名的一致性、错误信封语义、回归与证据 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 5 / P2 = 8（共 13）** |

> **一句话理由**：主体实现方向正确（白名单 + `_dispatch_draft_command` 只调真实签名、`EditToken` 整对象透传、未改 `src/application/editing/**`、未接 registry）；`python -m pytest tests/core tests/domain -q` 实测 **897 passed**、`dotnet test …CoreClient.Tests`（`CommandContractV11RTests`/`RegionWriteCommandTests` 过滤）实测 **80 passed**、三绿 PASS。但**五条 P1** 使其不能通过：①`drafts_apply` 响应被包成 `{"revisions": …}`，与契约/冻结范围表的裸映射不一致；②契约 §3 逐码表**含 3 个服务中不存在的码、漏掉 6 个可达真实码**，导致真实错误回落 `internal` 误分类；③主契约 `V11R_COMMAND_CONTRACT_V1.md` 有 **12 处无关表格分隔行被批量改成 7 列**（§4.x 表头 11 列 vs 分隔行 7 列，渲染失效，超范围回归）；④AC1 的「§10 变更记录同步」「§8 标题」未做；⑤AC4 的「每命令至少一成功 + 一失败用例」未满足（patch/prepare/apply/discard 无失败用例，且测试只到 handler 层、未覆盖 dispatch）。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**（`doc/reviews/FEA-05-WIRE-1-impl-r1.md`，在卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- 已执行（本轮实测，非引用 DSH 日志）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `311b79575…` / 空（clean） |
| `python -m pytest tests/core/test_draft_commands.py -q` | **9 passed**（0.28s）——与证据日志一致 |
| `python -m pytest tests/core tests/domain -q` | **897 passed, 1 warning（58.44s）, EXIT 0**——与 DSH 声称一致 |
| `dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests --filter "…CommandContractV11RTests\|…RegionWriteCommandTests"` | **80 passed / 0 failed**（45ms）——独立复现 DSH 日志 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 3062 bytes / 31 lines |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| 代码/契约逐行核对 | `core_service.py` 全部 141 行新增；契约文档 71 行；§8 39 行 diff；`test_draft_commands.py` 178 行 |

- **未执行**：`dotnet build apps/desktop-avalonia/NewManga.sln` + 全量 `dotnet test --no-build`（理由：本提交无任何 `apps/**` 变更，C# 侧仅受文档影响且已用定向过滤独立复现 80/80；全量 931/0/60 仍**未验证**，建议 DSH 集成时按 AC5 补跑）。

---

## 1. AC 逐项判定

| AC | 判定 | 证据与说明 |
|---|---|---|
| **AC1 契约** | **未通过** | 契约文档已落盘，头部（PENDING/v1.0/日期/归属/上游/实现/编号/变更记录）与五节齐全 ✓；§8 追加 C078–C083 六行（7 列、下划线名、`PENDING(FEA-05-WIRE-1)`、位于 `## 8.` 与 `## 9.` 之间）✓；`CommandContractV11RTests` 80/80 ✓。**但**：①**§3 逐码表内容错误**（P1-02）；②**§10 变更记录未追加**（HEAD §10 `:272-276` 仍只有 2026-10-30 一行）；③§8 标题 `:220` 仍「C067–C077 增量命令」，C078–C083 挂在旧标题下（P1-04）；④主契约 12 处分隔行被改坏（P1-03） |
| **AC2 语义不变** | **未通过** | 六条 handler 与真实签名逐字一致 ✓（`open_draft/patch_draft/prepare_candidate/apply_candidates/get_draft/list_drafts/discard_draft`）；`EditToken` 整对象透传 ✓（`:3029-3039` 传 raw dict，服务侧 `_token_from_json` 校验）；未改 `src/application/editing/**`、`src/domain/drafts/**` ✓（diff 仅 `src/bootstrap/core_service.py`）。**但** C081 响应外形与冻结表不一致（P1-01）；真实错误码被映射为 `internal`（P1-02 的一部分） |
| **AC3 CoreClient** | **N/A（合法）** | 卡 `:85` `[x]` + `<<NOT_APPLICABLE: …>>`；实现确未接 CoreClient/registry ✓ |
| **AC4 Python 协议测试** | **未通过** | 全量 897 passed ✓（实测）。**但**「每命令至少一成功 + 一失败用例」不满足：失败用例仅 `drafts_open` 非法 payload 与 `drafts_status` 双选择器；**patch / prepare / apply / discard 无失败用例**；且全部测试直接调 `_dispatch_draft_command`，**未覆盖 `_dispatch_request` 的白名单分支/错误信封转换/未知命令**；「未知命令」用例（`:159-163`）断言的是**不可达路径**（`drafts_close` 在 dispatch 层落入 `:5581-5596` 的 `UNKNOWN_COMMAND`，不会进 handler）→ P1-05 |
| **AC5 回归** | **部分验证** | 未改 `apps/**` → sln 源码面无回归风险；定向 C# 契约测试 80/80 ✓；Python 全量 897/0 ✓。全量 `dotnet build/test` 未重跑（未验证），建议集成时补 |
| **AC6 治理** | **通过** | 三绿本轮独立实跑：`check.ps1` PASS、`verify_pins` 15/15、api inventory EXIT 0 |
| **AC7 证据** | **未完成** | `verification/FEA-05-WIRE-1/` 有 `delivery-notes.md` + 3 个日志，内容与实测一致（9 passed / 897 passed / 80 passed）✓；**但**卡 `:124-126` 的 Canonical Evidence 表仍为占位 `\| - \|`，无 commit/sha256 证据行；卡仍 `status: ready`、AC1/2/4/6/7 仍 `<<TODO>>`，未转 `in_review` → P2-05 |

**结论：AC1、AC2、AC4 未通过；AC5 部分验证；AC3 N/A；AC6 通过；AC7 未完成。**

---

## 2. Lead 附加核查点

### 2.1 `_draft_error_envelope` 的 category 是否只用冻结词表

- **值域正确** ✓：`_DRAFT_ERROR_CATEGORY`（`:827-843`）与 fallback `.get(code,"internal")`（`:851`）的取值全部落在 M2-C1 冻结七值内，无 `infra`。
- **但表内容错误** ✗：见 P1-02——表里 3 个码在服务中不存在，6 个可达真实码不在表内，导致真实错误回落 `internal`（典型：`DRAFT_NOT_FOUND`→`internal` 应为 `not_found`；`STALE_BASE_REVISION`/`EDIT_TOKEN_REUSED`→`internal` 应为 `conflict`）。

### 2.2 `retryable` 集合是否合理

- 与契约 §3 逐码表一致 ✓（`LOCK_CHANGED`/`PAGE_SIZE_UNAVAILABLE`/`DRAFT_JOURNAL_UNWRITABLE`/`INTERNAL` = true，`:845`）。
- **语义待裁定**（P2-02）：`LOCK_CHANGED`（保护位/摘要变化）标 `retryable=true` 值得复核——该类冲突通常需客户端重读当前状态后再决策，自动重试可能空转；且契约 W-4 的类别规则「仅 `unavailable`/`internal` 为 true」与逐码表冲突（契约宜加注「逐码表优先」或修正 W-4 措辞）。建议 DSH 裁定，不阻塞实现结构。

### 2.3 `drafts_status` 二选一是否与契约一致

- **一致** ✓：契约 §1 `:30` 要求 `draftId` 或 `sessionId` 恰好一个；实现 `:3041-3048` 用 `bool(draft_id) == bool(session_id)` → `DRAFT_INVALID`，两分支返回 `{"draft":…}` / `{"drafts":[…]}` ✓；测试 `:130-139` 覆盖双给（失败）、单给（两种成功）。

### 2.4 是否引入回归（Core 命令分发 / 错误信封）

- 分发面：新增分支在 `_dispatch_request` 内、Region 分支之前，仅匹配 6 个下划线命令；其余命令落入既有分支，未改任何既有分支代码 ✓；全量 Python 897 passed、定向 C# 80 passed、三绿 PASS。
- 错误信封：`_draft_error_envelope` 是新函数，不触碰既有 `make_error_envelope` 调用方 ✓。
- **残余风险**：缺少 dispatch 级测试（见 P1-05），且 §8/主契约文档改动有超范围损坏（P1-03）——后者不影响测试但属文档回归。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **P1-01** | P1 | `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md:29`（C081 行）、卡 v5.2 映射表；`core_service.py:3039`；`test_draft_commands.py:127` | **C081 响应外形与冻结契约不一致。** 契约/范围表：`drafts_apply` 响应 = `{ "<region_id>": "<region_revision_id>" }`（`apply_candidates` 真实返回）；实现返回 `{"revisions": drafts.apply_candidates(...)}`（多包一层 `revisions`），测试 `:127` 把错误外形固定为 `{"revisions": {"r1": "rev2"}}`。AC2「与上表逐字段一致」不成立 | 去掉包装：`return drafts.apply_candidates(token, candidate_ids)`；同步修改测试断言与契约 §1/§2（若坚持包装，必须先由 DSH 改契约/范围表，不能实现单方偏离） |
| **P1-02** | P1 | 契约 §3 `:41-60`；`core_service.py:827-843`；`tests/core/test_draft_commands.py` | **§3 逐码表与真实服务不符（虚构 + 遗漏 → 错误 category）。** ①表中有 3 个服务不存在的码：`DRAFT_SEQUENCE_MISMATCH`、`DRAFT_ALREADY_FLUSHED`、`EDIT_TOKEN_DRAFT_CHANGED`（`git grep` 仅命中 `core_service.py:832/833/836` 的新映射本身，`src/application`/`src/domain` 无定义）；②遗漏 6 个六命令可达真实码：`DRAFT_NOT_FOUND`（patch/get/discard）、`DRAFT_CANDIDATE_NOT_FOUND`（apply）、`STALE_BASE_REVISION`（prepare/apply）、`EDIT_TOKEN_REUSED`（apply 重放/序列）、`DRAFT_APPLY_FAILED`（apply 原子失败）、`DRAFT_OWNER_CHANGED`（存在但未接线）；③后果：真实码经 `.get(code,"internal")` 回落 `internal`，如「draft 不存在」返回 `internal` 而非 `not_found`、「BaseRevision 过期/重放」返回 `internal` 而非 `conflict`；④测试只断言 `EDIT_TOKEN_EXPIRED`/`LOCK_CHANGED`/`INTERNAL` 三码，未覆盖真实码 | 按 `drafts.py` 17 码重写契约 §3 与 `_DRAFT_ERROR_CATEGORY`（可达 13 码逐码给出 category/retryable；不可达码标注「本卡不接线」）；补真实码测试（至少 `DRAFT_NOT_FOUND`→`not_found`、`STALE_BASE_REVISION`→`conflict`、`DRAFT_APPLY_FAILED`→`internal`） |
| **P1-03** | P1 | `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 的 `:18`、`:39`、`:57`、`:95`、`:108`、`:119`、`:128`、`:136`、`:153`、`:170`、`:207`、`:275`（共 12 处） | **主契约无关表格被批量改坏（超范围回归）。** 上述 12 处分隔行被统一改写成 7 列 `\|---\|…`，而原表头分别是 3 列（§1/§3/§5/§6/§8 变体/§10）与 11 列（§4.1–§4.6）；分隔行列数与表头不匹配 → 这些表格在 GFM 渲染下失效。本卡只要求「§8 追加 + 段首/约束/§10 同步」，该批量改写不在交付范围内，且 `CommandContractV11RTests` 跳过 分隔行故未报警 | 从 `be9265b34` 取回该文件后仅重做 §8 增量（或逐处还原 12 处分隔行）；建议提交前 `git diff --stat` 复核「只应改 §8」 |
| **P1-04** | P1 | `V11R_COMMAND_CONTRACT_V1.md:220`（§8 标题）、`:272-276`（§10） | **AC1 的「§10 已同步」「§8 段首」未完成。** §10 变更记录仍只有 2026-10-30 一行，没有 FEA-05 的记录行；§8 标题仍是「C067–C077 增量命令（PENDING, V11R-F0-1 / F0-2）」，而 C078–C083 已挂在其下（新段落 `:246` 补了「77→83」✓，但标题与旧约束段 `:241-242` 未同步） | §10 追加一行（日期/「FEA-05-WIRE-1 手工追加 C078–C083，不重跑生成器」/DSH）；§8 标题改为「C067–C083 增量命令（PENDING）」，旧约束段补一句「C078–C083 另见 FEA-05 契约」 |
| **P1-05** | P1 | `tests/core/test_draft_commands.py`（全文）；卡 AC4 `:86` | **AC4 未满足。** ①「每命令至少一成功 + 一失败用例」：失败用例仅覆盖 `drafts_open`（`:149-156`）与 `drafts_status`（`:130-139`），`drafts_patch`/`drafts_prepare`/`drafts_apply`/`drafts_discard` **无失败用例**；②全部测试直接调 `_dispatch_draft_command`（`:84` 起），**未覆盖** `_dispatch_request` 白名单分支、错误信封转换、`except DraftError` 返回结构和协议版本门（`:5112-5132`）；③`test_unknown_draft_command_is_rejected`（`:159-163`）断言 `drafts_close` 抛 `UNKNOWN`，但该路径在 dispatch 层不可达（unknown 命令走 `:5581-5596` 的 `UNKNOWN_COMMAND`），「未知命令」证据不成立 | 补 4 条失败用例（patch 非对象 patch→`DRAFT_PATCH_INVALID`；prepare 缺 origin→`DRAFT_INVALID`；apply 非对象 token→`EDIT_TOKEN_INVALID`；discard 缺 sessionId→`DRAFT_INVALID`）；补 2–3 条 dispatch 级用例（成功信封 `result`、`DraftError`→信封、未知名→`UNKNOWN_COMMAND`）；把「未知命令」断言改到 dispatch 层 |
| **P2-01** | P2 | `core_service.py:848-861`；契约 §3 `:43` | **`details` 形状不统一。** `DraftError.details` 是 dict（如 `DRAFT_APPLY_FAILED` 的 `{status, detail}`），无 cause 时被原样放进信封 → wire 得到**对象**；有 cause 时被写成 `[{causeCode: …}]` → wire 得到**数组**。而既有 `make_error_envelope` 的签名约定是 `list[dict]`。契约 §3 只写「`cause_code` → `details.causeCode`」，未定义形状 | 统一为既有数组约定（`details=[{...}, {"causeCode": …}]`），契约 §3 补一句 details 形状；`DRAFT_APPLY_FAILED` 的 dict 先展开为 `[{...}]` |
| **P2-02** | P2 | 契约 §3 `:57`；`core_service.py:845`；卡 W-4 `:108` | **`LOCK_CHANGED` 的 `retryable=true` 语义待 DSH 裁定**（契约与实现一致，故非不一致缺陷）：保护位/摘要变化属「需重读状态」冲突，自动重试可能空转；同时 W-4 的「仅 `unavailable`/`internal` 为 true」类别规则与逐码表（`LOCK_CHANGED`=conflict,true）自相矛盾 | DSH 裁定：改 `LOCK_CHANGED` 为 `retryable=false`，或保留 true 但在契约 §3 注明理由并修正 W-4 措辞 |
| **P2-03** | P2 | `core_service.py:2998-3052`；契约 §2 `:35-39` | **可选字段类型校验缺口。** `regionId`/`draftId`/`baseRevisionId`/`undoCursor` 及 `candidateIds` 元素未做类型校验（`_require_str`/`_require_int` 仅用于必填），非字符串值会穿到服务层引发 `TypeError`（未捕获 → 进程级错误/断连风险），而非 typed `DRAFT_INVALID` | 对可选字段补 `None | 类型` 校验（如 `regionId` 必须 `str|None`、`undoCursor` 必须 `int|None`、`candidateIds` 元素非空 `str`） |
| **P2-04** | P2 | 契约 §4 `:66`；`core_service.py:5581-5596`；测试 `:159-163` | **契约对未知命令的描述与实现不符。** 契约 §4 写「Core 对未知命令返回 `UNKNOWN`/`validation`（既有行为）」；实际返回 `UNKNOWN_COMMAND`/`validation`（`:5588-5592`）。测试断言的 `UNKNOWN` 分支只在 handler 内、实际不可达（与 P1-05③ 同源） | 契约改为 `UNKNOWN_COMMAND`/`validation`；测试改到 dispatch 层断言 |
| **P2-05** | P2 | 卡 `:6`、`:83-89`、`:124-126`、Closeout 末行 | **交付/收口项未完成。** 卡仍 `status: ready`、`approval: scope_review_r7_approved…`，AC1/2/4/6/7 仍 `<<TODO>>`（未转 `in_review`）；Canonical Evidence 表仍占位，无 commit/sha256；Closeout 末行含**stray CR**（「置 \ready」，实测文件内有 `\r(?!\n)`）且旧「待 r4 复核」行仍在 | DSH 转 `in_review` 时：补 Canonical Evidence 行（commit/sha256/path）、AC 标记、修 stray CR、刷 Closeout（v5.2/r7/实现 r1） |
| **P2-06** | P2 | `tests/core/test_draft_commands.py:1-7`；`delivery-notes.md`「已知限制」 | **测试仅 bridge 级（`_FakeDrafts`），无真实服务/SQLite/assembly 端到端。** 交付说明已声明；但「协议测试」对真实 `DraftProtectionService` 行为（token 过期/重放/冲突映射）零覆盖，P1-02 的错误码问题正是因此漏检 | 交付说明保留该限制并在验收证据中标注「bridge-only」；建议 FEA-05-PORT-1 或后续 e2e 卡补真实服务路径的最小成功 + 关键错误码用例 |
| **P2-07** | P2 | `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`（diff `+12/−?`） | **改动含卡 `allowed_paths` 之外的文件。** 该进度文件不在本卡写域（`:22-33`），属 DSH 集成侧记账 | 后续把 DSH 记账与本卡实现提交分离，或补授权说明；不阻断 |
| **P2-08** | P2 | `V11R_COMMAND_CONTRACT_V1.md:241-242` 与 `:257` | **§8 新旧约束段并存。** 旧约束段只写 C067–C077，新约束段写 C078–C083，读者需自行拼接 | 与 P1-04 一并修：合并为一段或在新段补「C067–C077 约束不变」 |

---

## 4. 处置建议（最小修复顺序）

1. **先修 P1-01**（C081 去包装）与 **P1-02**（按 `drafts.py` 17 码重写 §3 + `_DRAFT_ERROR_CATEGORY` + 真实码测试）——这是 wire 契约正确性的核心。
2. **恢复主契约**（P1-03）：`git show be9265b34:doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 取回原文件，仅重做 §8 增量；同时补 §10 记录行与 §8 标题（P1-04）。
3. **补 AC4 测试**（P1-05）：4 条失败用例 + 2–3 条 dispatch 级用例；改「未知命令」断言。
4. P2 批量：`details` 形状（01）、`retryable` 裁定（02）、可选字段类型（03）、§4 未知命令措辞（04）、证据/收口（05）、bridge-only 标注（06）、checkpoint 越域（07）、§8 约束段合并（08）。
5. 修完后派 **impl-r2** 复核（本席位可继续，仍只读）；P0/P1 = 0 才进入 DSH 集成。

## 5. 边界声明

本报告**只审实现**（AC1–AC7 与实现-契约一致性），不构成集成验收或契约冻结批准；`931/0/60` 全量 sln 与真实 SQLite 端到端**未验证**。本席位只审过范围、未参与实现（实现者为 DSH），符合 2026-10-31「上下文独立」裁决；未修改任何被审文件、未 commit/push。
