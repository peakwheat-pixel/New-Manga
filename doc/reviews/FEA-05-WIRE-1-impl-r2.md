---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 311b79575
reviewed_head: 2a8baf3a7
decision: changes_requested
counts: { P0: 0, P1: 1, P2: 10 }
---

# FEA-05-WIRE-1 实现复核 r2（同一独立席位；只审过范围、未参与实现）

| 字段 | 值 |
|---|---|
| base_commit | `311b79575b2870aa3efeec3cebecb992e48a6610`（impl-r1 被审 head） |
| reviewed_head | `2a8baf3a7229cefa6234e13627bbf91a4d283b10`（`fix(fea-05-wire-1): 处置实现复核 r1（P1×5…）`；`git status --porcelain` 为空） |
| 与 base 的 diff | `git diff --stat 311b79575..2a8baf3a7` → 9 files, +230/−47（core_service 19 行、tests 37 行、FEA-05 契约 25 行、主契约 46 行、证据日志/说明） |
| reviewer | `fea05-wire-scope-reviewer`（范围 r1–r7 同一席位；实现 rev 第 2 轮；**未参与实现**，实现者为 DSH，符合 2026-10-31「上下文独立」裁决） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | impl-r1 的 P1×5 关闭情况、新引入问题、剩余 P2 disposition、AC1–AC7 复核、治理三绿 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 1 / P2 = 10（共 11）** |

> **一句话理由**：r1 的 5 条 P1 中 **4 条完全关闭、1 条（P1-04）关闭但留格式小项**；主契约 12 处分隔行已恢复（本轮实测仅剩 3 个 hunk）、`drafts_apply` 已改裸映射、§3 已按 17 码重写、测试 9→11 且每命令失败覆盖成立。**但新引入 1 条 P1**：主契约把 C078–C083 放在 **`### 8.2`** 三级标题下（`:245`），而 `CommandContractV11RTests` 的解析器在 `### ` 标题处**重置 section**（`:216-217`），pending 行仅接受 `section.StartsWith("## 8.")`（`:260`）——**6 条 pending 行因此对测试完全不可见**，80/80 是「空过（vacuous）」；待 FEA-05-PORT-1 注册这些命令时，`RegistrySurface_IsFullyDeclared` 会因「未声明」而失败，属潜伏陷阱（且正是范围复核 r2-P1-01 已预警过的同一坑）。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**。
- 已执行（本轮实测）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `2a8baf3a7…` / 空（clean） |
| `python -m pytest tests/core/test_draft_commands.py -q` | **11 passed**（0.29s）——与证据日志一致 |
| `python -m pytest tests/core tests/domain -q` | **899 passed, 1 warning（59.97s）, EXIT 0**——与声称一致 |
| `dotnet test …CoreClient.Tests --filter "…CommandContractV11RTests\|…RegionWriteCommandTests"` | **80 passed / 0 failed**（45ms） |
| `git diff be9265b34..HEAD -- doc/contracts/V11R_COMMAND_CONTRACT_V1.md \| grep '^@@'` | **仅 3 个 hunk**（§8 标题、§8.2 插入、§10 追加）；对 `be9265b34` 的分隔行比较**无删除/改写** → 12 处分隔行已恢复 ✓ |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 3062 bytes / 31 lines |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| 解析器源码核对 | `CommandContractV11RTests.cs:216-217`（`## `/`### ` 均重置 section）、`:260`（pending 行要求 `section.StartsWith("## 8.")`） |
| 证据日志核对 | `pytest-draft-commands.log`=11 passed、`pytest-core-domain.log`=`899 passed, 1 warning in 60.13s`、`dotnet-coreclient-contract.log`=80 passed ✓ 与实测一致 |

- **未执行**：全量 `dotnet build/test`（本提交仍无 `apps/**` 变更；定向 80/80 已复现）；全量 931/0/60 仍**未验证**，建议集成时补。

---

## 1. impl-r1 逐项 disposition（P1=5 / P2=8）

| r1 ID | 级别 | 状态 | 证据 |
|---|---|---|---|
| **P1-01** C081 多包一层 | P1 | **CLOSED** | `core_service.py:3044` 已 `return drafts.apply_candidates(token, candidate_ids)`；测试 `:127` 断言 `result == {"r1": "rev2"}`；契约 `:29` 标注「裸映射」✓ |
| **P1-02** §3 逐码表错 | P1 | **CLOSED** | 契约 §3（`:45-63`）按 `drafts.py` 17 码重写：删 3 个不存在码，补 `DRAFT_FLUSH_TRIGGER_INVALID`/`DRAFT_NOT_FOUND`/`DRAFT_CANDIDATE_NOT_FOUND`/`DRAFT_OWNER_CHANGED`/`EDIT_TOKEN_REUSED`/`STALE_BASE_REVISION`/`DRAFT_APPLY_FAILED`；`_DRAFT_ERROR_CATEGORY`（`:827-847`）同步 17 码 + INTERNAL/UNKNOWN；逐码 category/retryable 与映射表一致 ✓。残留：真实码 envelope 无测试（P2-9） |
| **P1-03** 主契约 12 处分隔行被改坏 | P1 | **CLOSED** | 对 `be9265b34` 的 diff 仅 3 hunk（§8 标题/§8.2/§10），无任何分隔行 `-` 变更；§4.x 11 列分隔行恢复 `\|---\|:--:\|…` ✓ |
| **P1-04** §8 标题/§10 未同步 | P1 | **CLOSED（留格式小项）** | §8 标题已扩为「…与 C078–C083 Draft 命令面」✓；§10 已追加 FEA-05 记录 ✓。**但**追加的是**表格外的 bullet**（`:280`）而非 3 列表格行 → P2-7 |
| **P1-05** AC4 覆盖不足 | P1 | **CLOSED** | 测试 9→11：`test_each_command_rejects_invalid_payload`（8 组，覆盖 open/patch/prepare/apply/discard 的非法 payload）+ 既有 status 双选择器失败用例 → **每命令至少一成功 + 一失败**成立 ✓。**但**新增 `test_drafts_dispatch_is_registered_and_typed` 用 `inspect.getsource` 做源文本包含判断，不是行为测试 → P2-10 |
| P2-01 `details` 形状不一致 | P2 | **OPEN** | `_draft_error_envelope`（`:848-861`）未改：无 cause 时把 `DraftError.details`（dict）原样入信封，有 cause 时写成 `[{causeCode}]`（数组）；与 `make_error_envelope(details: list[dict])` 约定不统一 |
| P2-02 `LOCK_CHANGED` retryable | P2 | **OPEN（且 DSH 处置理由不实）** | 保留 `true`（契约 §3 / `_DRAFT_RETRYABLE` 一致）；但交付说明与答复称「W-4 已冻『锁冲突 true』」——**v5.2 W-4（卡 `:108`）实际写的是「默认 false；仅 `unavailable`/`internal` 类为 true」**，并无「锁冲突 true」。契约/实现与 W-4 的类别规则仍冲突，需 DSH 二选一（改 W-4 或改值），不能以错误依据「接受遗留」 |
| P2-03 可选字段类型校验缺口 | P2 | **OPEN** | `:2998-3052` 未改：`regionId`/`draftId`/`baseRevisionId`/`undoCursor`/`candidateIds` 元素仍无类型校验，非字符串会穿到服务层产生未捕获 `TypeError` |
| P2-04 契约 §4 未知命令码名 | P2 | **OPEN** | 契约 `:71` 仍写「`UNKNOWN`/`validation`」；实现实际返回 `UNKNOWN_COMMAND`/`validation`（`core_service.py:5588-5592`） |
| P2-05 卡/证据/收口未完成 | P2 | **OPEN** | 本轮 commit **未改卡**：仍 `status: ready`、AC1/2/4/6/7 仍 `<<TODO>>`、Canonical Evidence 仍占位、Closeout 仍有 stray CR 与旧「待 r4 复核」行（证据日志已更新但证据表未填） |
| P2-06 bridge-only 证据 | P2 | **接受遗留** | 交付说明 `:36` 已声明「fake 服务，真实集成归 FEA-05-PORT-1」 |
| P2-07 r1「checkpoint 越域」 | P2 | **CLOSED（本轮未涉及）** | 本提交无 `doc/checkpoints/**` 变更 |
| P2-08 r1「§8 新旧约束段并存」 | P2 | **CLOSED（部分）** | §8.2 自带约束段；但旧段仍在 §8.1 位置且标题仍是层级问题（见 P1-A） |

---

## 2. AC 逐项判定

| AC | 判定 | 说明 |
|---|---|---|
| **AC1 契约** | **未通过（1 条 P1）** | 契约文档头部/五节/§3 逐码表 ✓；§8 追加 6 行（7 列/下划线/PENDING）✓；`CommandContractV11RTests` 80/80 ✓；§8 标题 ✓、§10 已追加 ✓。**但** 6 行位于 `### 8.2` 下，解析器不可见（P1-A），AC1 的机械意图未达成；`CommandContractV11RTests` 通过是空过，不能作为该 AC 的证据 |
| **AC2 语义不变** | **通过（附 P2）** | 仅调真实签名 ✓；`EditToken` 整对象透传 ✓；C081 裸映射 ✓；未改 `src/application/editing/**`/`src/domain/drafts/**` ✓。附件：真实码未测（P2-9）、可选字段类型（P2-3） |
| **AC3 CoreClient** | **N/A（合法）** | 卡 `:85` `[x]` + 原因；实现未接 registry ✓ |
| **AC4 Python 协议测试** | **通过（附 P2）** | 全量 899 passed（实测）；每命令至少一成功 + 一失败成立 ✓。附件：dispatch 级弱测试（P2-10） |
| **AC5 回归** | **部分验证** | 无 `apps/**` 变更；定向 C# 80/80 ✓；Python 899/0 ✓；全量 sln 未重跑（未验证） |
| **AC6 治理** | **通过** | 三绿本轮独立实跑 PASS/15-15/EXIT 0 |
| **AC7 证据** | **未完成** | 日志/交付说明与实测一致 ✓；Canonical Evidence 表仍占位、AC 未标（P2-5） |

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **P1-A（新）** | P1 | `doc/contracts/V11R_COMMAND_CONTRACT_V1.md:245`（`### 8.2 …`）与 `:251-256`（C078–C083）；`CommandContractV11RTests.cs:216-217`、`:260` | **§8.2 用三级标题，pending 行对解析器不可见。** 解析器在遇到 `## ` **或 `### `** 标题时重置 `section`（`:216-217`），pending 行只接受 `section.StartsWith("## 8.")`（`:260`）；`### 8.2 …` 使 section 变为 `### 8.2 …`，6 条行全部被跳过。后果：①`CommandContractV11RTests` 80/80 是空过，无法证明 6 条已被契约登记；②FEA-05-PORT-1 注册这 6 条命令时，`RegistrySurface_IsFullyDeclared` 将以「未声明」失败；③范围复核 r2-P1-01 已预警「另起 `### 8.1` 子节会被忽略」，本次复现同一坑 | 把 `### 8.2 …` 改为**非标题的加粗段落**（`**8.2 C078–C083 Draft 命令面（PENDING, FEA-05-WIRE-1）**`）或 `## 8.2 …`（`"## 8.2".StartsWith("## 8.")` 为真，均可被解析）；同时**加一条断言**（建议在 `CommandContractV11RTests` 内）验证 pending 集含 `drafts_open`…`drafts_discard` 6 名——否则该缺陷无法被现有测试发现 |
| P2-1 | P2 | `core_service.py:848-861`；契约 §3 `:43` | `details` 形状不一致（dict vs list）仍未统一；契约未定义 details 形状 | 统一为既有数组约定并写进契约 §3 |
| P2-2 | P2 | 契约 §3 `:61`；`core_service.py:845`；卡 W-4 `:108`；`delivery-notes.md` 处置表 | **`LOCK_CHANGED`=true 的「接受遗留」依据不实**：v5.2 W-4 只写「仅 `unavailable`/`internal` 类为 true」，未写「锁冲突 true」；契约/实现与 W-4 仍冲突 | DSH 二选一：把 `LOCK_CHANGED` 改 false，或修订 W-4 明确「锁冲突可重试」并保留 true；同步修正交付说明中的错误依据 |
| P2-3 | P2 | `core_service.py:2998-3052` | 可选字段（`regionId`/`draftId`/`baseRevisionId`/`undoCursor`/`candidateIds` 元素）无类型校验，可能抛未捕获 `TypeError` | 补 `None|类型` 校验 |
| P2-4 | P2 | 契约 §4 `:71` | 「未知命令返回 `UNKNOWN`/`validation`」与实现（`UNKNOWN_COMMAND`/`validation`，`core_service.py:5588-5592`）不符 | 改为 `UNKNOWN_COMMAND` |
| P2-5 | P2 | 卡 `:6`、`:83-89`、`:124-126`、Closeout | 卡未转 `in_review`、AC 未标、Canonical Evidence 占位、Closeout 含 stray CR 与旧「待 r4 复核」 | DSH 收口时统一刷新（本提交未动卡） |
| P2-6 | P2 | `tests/core/test_draft_commands.py:1-7`；交付说明 | bridge-only 证据（fake 服务），无真实服务/SQLite 端到端 | 接受遗留；建议 PORT-1 e2e |
| P2-7 | P2 | 主契约 `:273-281`（§10） | §10 变更记录用了**表格外 bullet**（`:280`）而非 3 列表格行，与表格格式不一致 | 改为表格行：`\| 2026-11-02 \| FEA-05-WIRE-1 §8.2 新增 C078–C083…\| DSH \|` |
| P2-8 | P2 | 契约 §3 `:43` | 词表行只列 `validation`/`not_found`/`conflict`/`unavailable`/`internal`/`unknown`，漏 M2-C1 的 `cancelled`（虽未使用） | 补 `cancelled` 或写「本契约未使用 `cancelled`」 |
| P2-9 | P2 | `tests/core/test_draft_commands.py:166-178` | 真实码 envelope 未测（`DRAFT_NOT_FOUND`→`not_found`、`STALE_BASE_REVISION`/`EDIT_TOKEN_REUSED`→`conflict`、`DRAFT_APPLY_FAILED`→`internal`） | 补 3–4 条 envelope 断言，锁住 §3 表 |
| P2-10 | P2 | `tests/core/test_draft_commands.py:200-213`（新 dispatch 测试）、文件 EOF、`delivery-notes.md` | ①「dispatch 注册」测试用 `inspect.getsource` 文本包含判断，非行为验证（任何同名字符串都能过）；②测试文件**缺末尾换行**；③交付说明新增段含掉字控制符（「eturn」「\test_…」「pply_candidates」） | ①改为真实调用 `_dispatch_request`（至少覆盖成功信封 + DraftError→信封 + `UNKNOWN_COMMAND`）；②③补换行/清理控制符 |

---

## 4. 处置建议

1. **P1-A（唯一 P1）**：`### 8.2` → 加粗段落或 `## 8.2`；并新增「pending 集含 6 个 drafts 命令」的断言（防止再次回归）。改完重跑 `pytest` 与定向 dotnet（预期仍 80/80，但断言应真正检查到 6 行）。
2. **P2-2 必须先纠正依据**：W-4 v5.2 没有「锁冲突 true」，请按「改 W-4」或「改值为 false」二选一落盘，不能以错误前提记为接受遗留。
3. P2 批量：`details` 形状（1）、可选字段类型（3）、`UNKNOWN_COMMAND` 措辞（4）、卡收口（5）、§10 表格行（7）、`cancelled`（8）、真实码测试（9）、dispatch 行为测试 + EOF/控制符（10）。
4. 改完派 **impl-r3** 复核（本席位可继续，只读）；P0/P1 = 0 后 DSH 集成并按 AC5 补跑全量 sln。

## 5. 边界声明

本报告只审实现与契约一致性，不构成集成验收或契约冻结批准；全量 `931/0/60` 与真实 SQLite 端到端**未验证**。本席位只审过范围、未参与实现（实现者为 DSH），符合 2026-10-31「上下文独立」裁决；未修改被审文件、未 commit/push。
