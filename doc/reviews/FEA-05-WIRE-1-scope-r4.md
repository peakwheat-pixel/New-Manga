---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: a62d9ca10
reviewed_head: c4a88a76d
decision: changes_requested
counts: { P0: 1, P1: 2, P2: 8 }
---

# FEA-05-WIRE-1 范围复核 r4（同一独立席位续任）

| 字段 | 值 |
|---|---|
| base_commit | `a62d9ca10b6aa53f9efcbefa5433fc37c87cae27`（r3 的 reviewed_head；范围 v4 的父提交） |
| reviewed_head | `c4a88a76d4c4c139c0897d629296fc5d5aac1595`（`docs(fea-05-wire-1): 范围 v4…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（**v4**，131 行；status=proposed） |
| 与 r3 的 diff | `git diff --stat a62d9ca10..c4a88a76d` → 本卡 85+/42−；`doc/reviews/FEA-05-WIRE-1-scope-r3.md` 入库。契约文档与 §8 行仍**未落盘**（卡内交付物，正常） |
| reviewer | `fea05-wire-scope-reviewer`（r1→r2→r3→r4 同一席位续任） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与该卡起草/实现/返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | 仅范围冻结文本（AC1–AC7、映射表、W-1…W-7、契约边界、治理三绿）；不含实现审查 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 1 / P1 = 2 / P2 = 8（共 11）** |

> **一句话理由**：r3 的 R3-P1-01（映射表签名）**已实质关闭**——六条签名与 `drafts.py` 逐字一致；R3-P1-02 部分关闭（信封字段齐、Token 整对象回传已冻结）但仍留 category 词表错误。**新出现 1 条 P0：W-6 的处置（把 C078–C083 追加进 `V11RAdditiveCommandNames`）无法满足既有冻结不变式**——`RegionWriteCommandTests` 是 `[Fact]`（无 sidecar 也跑），它同时断言「registry 追加集 == `V11RAdditiveCommandNames`」与「registry 追加集 == `RegionWriteCommandNames ∪ RegionReadCommandNames`」；前者要求扩展该属性、后者要求不扩展，二者不可同时成立，而该不变式出自 **FROZEN** 的 `V11R_REGION_WRITE_CONTRACT.md` §1.1/§4/§8，且该文件不在本卡写域。**结论：W-6 必须退回 DSH（且问题大于 W-6 本身）**，否则 AC5「sln 不退化」按现卡不可满足。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**（在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- **未执行**：`dotnet build`/`dotnet test`、`python -m pytest`、UI 真机。931/0/60 在当前 head **未验证**（引用链：`doc/handoffs/FEA-04-68c72ba57.md:184`、`verification/FEA-04/build-test-raw.log`、`doc/reviews/FEA-04-r3.md:21`）。
- **契约交付物仍未落盘（符合范围卡语义）**：`doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md` ABSENT；`V11R_COMMAND_CONTRACT_V1.md` §8 无 C078–C083 行。二者是本卡交付物，属实现期产物。
- 已执行（只读）：

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `c4a88a76d…` / 空（clean） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 达预算 80%（3124 bytes / 45 lines） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| 测试执行面核对 | `apps/desktop-avalonia/tests/NewManga.runsettings` 仅 `MaxCpuCount=1`（无 trait 过滤）；`RegionWriteCommandTests` 的 4 个用例均为 `[Fact]`（`:49`/`:92`/`:126`/`:257`）→ 无 sidecar 也进全量 `dotnet test` |

**三绿：是**（但三绿是现状检查，不覆盖本卡新命令落地后的注册表不变式，见 §2.4）。

---

## 1. r3 逐项 disposition（P0=0 / P1=2 / P2=9）

| r3 ID | 级别 | v4 状态 | 证据 |
|---|---|---|---|
| R3-P1-01 映射表签名 | P1 | **CLOSED（签名部分）** | 六条签名已逐字一致（§2.1 逐条核对）；残留 C081 响应外形错误 → R4-P1-01；wire 字段细节 → R4-P2-07 |
| R3-P1-02 错误/Token 传输 | P1 | **PARTIAL** | 信封字段 `code`/`message`/`category`/`retryable`/`details` 已冻结（`:105`）、`EditToken` 六字段整对象回传（`:67`、`:70`）、receipt 幂等已写 ✓；但 category 用了**冻结词表外的 `infra`**、14 码未逐码枚举、`cause_code` 未处置 → R4-P1-02 |
| R3-P2-01 §8 文档一致性 | P2 | **CLOSED** | `:77` 要求同步 §8 段首总数/`PENDING` 口径、约束段、§10 变更记录 ✓ |
| R3-P2-02 契约文档头部/冻结流程 | P2 | **CLOSED** | `:76` 要求头部（状态 `PENDING`/版本 `v1.0`/日期/归属/上游与实现指针/变更记录）+ 五节 ✓ |
| R3-P2-03 `V11RAdditiveCommandNames` 裁决 | P2 | **升级为 P0** | W-6 `:107` 决定「追加到该集合」——与 FROZEN `V11R_REGION_WRITE_CONTRACT.md:62-63`/`:344-346`/`:457` 及 `RegionWriteCommandTests:107-117` 冲突 → **R4-P0-01** |
| R3-P2-04 AC5 完整命令 | P2 | **OPEN** | `:88`、`:116` 仍是省略号缩写（`dotnet test ... --no-build --settings .../NewManga.runsettings`）→ R4-P2-01 |
| R3-P2-05 L-2 解除记录 | P2 | **OPEN** | 来源链 `:40-44` 仍无 L-2 记录 → R4-P2-02 |
| R3-P2-06 `FEA-05-PORT-1` 登记 | P2 | **OPEN（且陈述不实）** | `:94` 写「端口面另卡 FEA-05-PORT-1，**已登记**」，但 `REBASELINE_PLAN.md`/`TASK_LEDGER.md`/`STATUS.md` 均无该节点（本轮 `git grep` 复核为空）→ R4-P2-03 |
| R3-P2-07 STATUS 预算/陈旧计数 | P2 | **OPEN** | 未处置（本轮 check.ps1 仍报 3124/45；`doc/STATUS.md:19` 仍 483=471+11+1，现 LEDGER 491/480/10）→ R4-P2-04 |
| R3-P2-08 kill-criteria/worktree/flush deferral | P2 | **PARTIAL** | flush 已由 W-7 `:108` 登记 deferral ✓；kill-criteria 与 worktree 说明仍缺（`:127` 仍「无 worktree」）→ R4-P2-05 |
| R3-P2-09 处置表错记 + 断言红线 | P2 | **PARTIAL** | 错记随旧表删除而消失 ✓；「不得弱化/删除既有契约对照断言」红线仍无 → R4-P2-06 |

**统计（11 项）**：**CLOSED 3**（R3-P1-01 签名部分、R3-P2-01、R3-P2-02）／**PARTIAL 3**（R3-P1-02、R3-P2-08、R3-P2-09）／**OPEN 4**（R3-P2-04、P2-05、P2-06、P2-07）／**升级 P0 1**（R3-P2-03）。

---

## 2. 逐项核查（对应 Lead 的 4 个核查点）

### 2.1 映射表是否与真实服务签名逐字一致 —— **6/6 签名一致；1 处响应外形错误**

| ID | 卡（`:60-65`） | 真实签名（`drafts.py`） | 判定 |
|---|---|---|---|
| C078 `drafts_open` | `open_draft(session_id, page_id, region_id, *, base_revision_id, page_binding_version) -> DraftLease` | `:97-105` **逐字一致** | ✓；响应 `draft`/`canEdit`/`token?` 与 `DraftLease(draft, can_edit, token)`（`entities.py:181-186`）一致 ✓。注：`base_revision_id` 无默认值，wire 省略时须显式传 `None`，卡未写明（R4-P2-07） |
| C079 `drafts_patch` | `patch_draft(draft_id, session_id, patch, *, undo_cursor=None, schedule_flush=True) -> Draft` | `:165-168` 一致 | ✓；wire 未列 `scheduleFlush?`，与 W-7「只透传既有参数」不完全一致（R4-P2-07） |
| C080 `drafts_prepare` | `prepare_candidate(region_id, patch, *, origin, draft_id=None, base_revision_id=None) -> RegionCandidate` | `:304-312` 一致 | ✓；`origin` 需按 `_ORIGIN_VALUES` 校验（handler 责任，AC2 覆盖） |
| C081 `drafts_apply` | `apply_candidates(token: EditToken \| Mapping, candidate_ids: Sequence[str] = ()) -> dict[str,str]` | `:374-376` 一致 | 签名 ✓；**响应 ✗**：真实返回 `dict(receipt_data["revisionIds"])`＝`{region_id: revision_id}`（`drafts.py:500-507`、`:528`），卡写「`receipt`（键=`draft_sequence`，值=状态）」→ **R4-P1-01** |
| C082 `drafts_status` | `get_draft(draft_id) -> Draft` / `list_drafts(*, session_id=None) -> list[Draft]`（按 payload 二选一） | `:151` / `:158` 一致 | ✓；「恰好一个」✓；两分支结果外形分别给出 ✓ |
| C083 `drafts_discard` | `discard_draft(draft_id, session_id) -> None` | `:215` 一致 | ✓；响应 `{"discarded": true}` 是 handler 合成的 wire ack（服务返回 `None`），卡未注明（R4-P2-07） |

`EditToken` 六字段 `tokenId/DraftId/DraftSequence/SessionId/issuedAt/expiresAt`（卡 `:67`）与 `entities.py:141-163` **逐字一致** ✓；`_token_from_json` 的必需键与 `issued != edit_token` 整对象相等语义（`drafts.py:755-773`、`:408-411`）与卡 `:70` 的「不得拆分/重建」要求一致 ✓。

### 2.2 W-4 是否覆盖 `errors.py` 既有结构 —— **信封字段覆盖，但 3 处缺陷**

- `DraftError` 实际签名：`DraftError(code, message="", *, details=None, cause_code=None)`（`errors.py:64-73`）；wire 信封为 `{code, category, message, retryable, details?}`（`make_error_envelope`，`core_service.py:808-825`）。W-4 `:105` 列出的五个字段与信封**一致** ✓。
- **缺陷 1（P1）**：category 用了冻结词表外的 `infra`。M2-C1 §8 的 category 值域为 `validation | not_found | conflict | unavailable | cancelled | internal | unknown`（`M2-C1_TYPED_IPC_CONTRACT.md:380`）；`src/`/`apps/` 全仓无 `"infra"` 字面量（本轮 `git grep` 复核）。按 W-4 实现会产出**不符合冻结错误分类的 envelope**。
- **缺陷 2（P1）**：「14 个新 wire 码逐码映射」仍是规则而非表——未逐码枚举，无法机械核验；且 `drafts.py` 的 17 个码里有 3 个不在六命令可达面（`DRAFT_OWNER_CHANGED` 仅 `transfer_owner`、`DRAFT_FLUSH_TRIGGER_INVALID` 仅 `force_flush`/`flush_pending`、`PAGE_SIZE_UNAVAILABLE` 仅页尺寸路径），可达集合与「14」的关系未说明。
- **缺陷 3（P1）**：`DraftError.cause_code` 未处置（是否进 `details`、是否外泄）；`retryable` 判据「锁冲突 true」语义可疑——`LOCK_CHANGED` 是保护位变更（用户需重新确认），`retryable=true` 会让客户端无效重试。

### 2.3 AC1–AC7 可验收性

| AC | 判定 | 依据 |
|---|---|---|
| AC1 契约（`:84`） | **可验收** | 头部 + 五节 + §8 六行 + 段首/约束/§10 同步 + 解析器约束（§8 内、下划线名、`PENDING` 开头、不进冻结集）全部可机械核 |
| AC2 语义不变（`:85`） | **可验收（除 C081 响应）** | 签名逐字一致；「逐字段一致（含 EditToken 整对象）」可核；C081 结果外形需按 R4-P1-01 修正后才能核 |
| AC3 CoreClient（`:86`） | **可验收（但受 P0 影响）** | 三项断言可核；然而「追加集 == `V11RAdditiveCommandNames`」与 AC5 的 sln 不退化互相矛盾（§2.4） |
| AC4 Python 测试（`:87`） | **可验收** | `tests/core/**`、`tests/domain/**` 在写域；pytest 配置支持该命令 |
| AC5 回归（`:88`） | **不可满足** | `RegionWriteCommandTests` 的冻结不变式必然红（§2.4）；且命令仍省略号缩写（R4-P2-01） |
| AC6 治理（`:89`） | **可验收** | 三绿本轮实测 ✓ |
| AC7 证据（`:90`） | **可验收** | `evidence_dir` 在写域 ✓ |

**6/7 可验收，AC5 不可满足。**

### 2.4 W-6 是否需退回 DSH —— **需要，且问题大于 W-6**

**事实链**（全部本轮只读复核）：

1. `RegionWriteCommandTests.Registry_AppendsTheV11RCommands_WithoutEditingTheFrozenSnapshot` 是 `[Fact]`（`:92`），runsettings 无 trait 过滤（只有 `MaxCpuCount=1`）→ **每次全量 `dotnet test` 都执行**。
2. 该用例断言（`:107-117`）：
   - `additive := registryNames − snapshotNames`；
   - `:109` `Assert.Equal(V11RAdditiveCommandNames, additive)`；
   - `:110-114` `Assert.Equal(RegionWriteCommandNames ∪ RegionReadCommandNames, additive)`；
   - `:115-117` 数量守恒。
3. 本卡必须把 6 条 drafts 命令注册进 `HostCommandRegistry`（`HostCommandDispatcher.InvokeAsync` 以 registry 为唯一路由，`HostCommandDispatcher.cs:59`）→ `additive` 必然从 11 变 17。
4. W-6 让 `V11RAdditiveCommandNames` 也变 17 → `:109` 过、**`:110-114` 必红**（`RegionWrite ∪ RegionRead` 仍是 11）。
5. 反向选择（不扩展该属性、改 `CommandParityContractTests` 的断言）→ **`:109` 必红**。
6. 两个断言不可能同时满足；唯一出路是修改 `RegionWriteCommandTests` 或修改其不变式，而该不变式出自 **FROZEN** 契约：`V11R_REGION_WRITE_CONTRACT.md:62-63`（「`RegionWriteCommandNames`（10 写）、`RegionReadCommandNames`（1 读）与并集 `V11RAdditiveCommandNames`（11）」）、`:344-346`（§4 C# 侧契约：同口径 +「`All` = 冻结 66 条 + 11 条追加」）、`:457`（§8 验证出口：「追加集恰为 `V11RAdditiveCommandNames`（10 写 + 1 读）」）。
7. `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` **不在本卡 `allowed_paths`**（卡 `:22-35`），也不在 15 份 `verify_pins` 内（`verify_pins.ps1:6-13`）——但它的状态行是 `FROZEN`（`:3`），改动须走契约修订/更换版本。

**结论**：W-6 不足以解决；这不是「属性语义命名之争」，而是**「registry 追加集」不变式与冻结区域契约的冲突**。必须退回 DSH 二选一（或三选一）：
- **(a) 推荐**：DSH 授权把不变式升级为「registry 追加集 = 各家族声明集合之并」——同时（i）修改 `RegionWriteCommandTests:107-117` 保留 region 家族自身的 `RegionWrite/RegionRead` 断言、把「== 全量追加集」改为「== 各家族集合之并」，（ii）在 `V11R_REGION_WRITE_CONTRACT.md` 增补一条变更记录/勘误（v1.6）说明 §4/§8 的 11 条口径为 V11R 时代基线、后续家族按合并式扩展；该文件须 DSH 单点提交或加入本卡写域。
- (b) 把 drafts 并入 `RegionWriteCommandNames`/`RegionReadCommandNames`——可让两条断言同时过，但名字语义错误且仍与 `:344`「All = 66 + 11」冲突，不推荐。
- (c) 若 DSH 认为本卡不应触碰该不变式，则本卡须降级为「不落地 registry 注册」（但 dispatch 依赖 registry → 不可行），或整卡重排。

**同时**：W-6 的「若复核认为应另立集合，退回 DSH 裁决」不适用（另立集合同样过不了 `:109`），DSH 需按 (a) 处置。

### 2.5 其他

- **写域**：无遗漏（新契约文档 `:24`、master `:25`、`tests/core/**`、`tests/domain/**`、CoreClient 及其测试；`src/application/editing/**` 与端口三文件均不在域）✓。**若按 §2.4(a) 处置，需追加 `doc/contracts/V11R_REGION_WRITE_CONTRACT.md` 与（允许修改的）`RegionWriteCommandTests.cs` 到写域**，并明确该测试的修改须 DSH 留痕。
- **三绿**：本轮实测全绿（STATUS 预算警告仍在，见 R4-P2-04）。
- **无用户级裁决点**；W-6 的处置属 DSH 契约裁决（见 §2.4）。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R4-P0-01** | P0 | 卡 `:79`（CoreClient 行）、`:86`（AC3）、`:88`（AC5）、W-6 `:107`；`RegionWriteCommandTests.cs:92`、`:107-117`；`V11R_REGION_WRITE_CONTRACT.md:62-63`、`:344-346`、`:457`；`CommandParityContractTests.cs:88-91`；`HostCommandDispatcher.cs:59` | **W-6 处置与冻结不变式冲突 → AC5 不可满足。** `RegionWriteCommandTests`（`[Fact]`，无 sidecar 也跑）同时断言「registry 追加集 == `V11RAdditiveCommandNames`」与「== `RegionWrite ∪ RegionRead`」；注册 6 条 drafts 后追加集=17，扩展属性则第二断言红、不扩展则第一断言红——两断言不可同时成立；该不变式出自 FROZEN `V11R_REGION_WRITE_CONTRACT.md` §1.1/§4/§8，且该文件不在写域。W-6 自带的「另立集合」退路同样无效 | 退回 DSH 裁决：推荐方案 (a)——授权修改 `RegionWriteCommandTests` 把不变式升级为「追加集 = 各家族声明集合之并」（保留 region 家族断言），并在 `V11R_REGION_WRITE_CONTRACT.md` 增补变更记录（v1.6，说明 11 条为 V11R 时代基线）；相应把该契约文件（与 `RegionWriteCommandTests.cs` 的修改授权）纳入写域或由 DSH 单点提交；同时定 `V11RAdditiveCommandNames` 的最终语义（扩展/另立）并同步 `CommandParityContractTests` |
| **R4-P1-01** | P1 | 卡 `:63`（C081 响应列）、`:85`（AC2）；`drafts.py:500-507`、`:528`；`drafts.py:389-407` | **`drafts_apply` 响应外形错误。** 真实返回 `dict(receipt_data["revisionIds"])`＝`{region_id: region_revision_id}`；卡写成「`receipt`（键=`draft_sequence`，值=状态）」，与实现的键/值都不同（receipt 元数据是 `{tokenId,DraftId,DraftSequence,revisionIds,contentDigests,committedAt}`，且**不是**返回值）。照卡实现会让 wire 契约与实现不一致，AC2「逐字段一致」无法通过 | 改为：`result` = `{ "<region_id>": "<region_revision_id>", … }`（`revisionIds` 映射，重放幂等返回同一映射）；receipt 元数据明确「不上 wire（内部审计）」或单列为可选；补一条「同 token 重放 → 同一映射」的测试项 |
| **R4-P1-02** | P1 | 卡 W-4 `:105`、`:78`、`:84`（AC1）；`errors.py:64-73`；`M2-C1_TYPED_IPC_CONTRACT.md:380`；`drafts.py` 17 码清单（3 例不可达） | **W-4 仍不可机械核验且含非法词表值。** ①category 写了 `infra`，不在冻结词表 `validation/not_found/conflict/unavailable/cancelled/internal/unknown`（全仓无该字面量）；②「14 码逐码映射」只有规则没有表，未逐码枚举；③3 个码不在六命令可达面（`DRAFT_OWNER_CHANGED`/`DRAFT_FLUSH_TRIGGER_INVALID`/`PAGE_SIZE_UNAVAILABLE`），可达集合与 14 的关系未说明；④`DraftError.cause_code` 未处置；⑤`retryable` 判据「锁冲突 true」待核（`LOCK_CHANGED` 属用户需重新确认，建议 false） | 契约文档 §3 给逐码表（仅列六命令可达码）＝`code → {category∈冻结词表, retryable, details 形态}`；`cause_code` 规定「不进 wire 或仅 details.cause_code」；AC1 增加一条「契约文档 §3 含逐码映射表」的核验 |
| **R4-P2-01** | P2 | 卡 `:88`（AC5）、`:116`（测试要求） | AC5/测试表仍是省略号缩写（`dotnet test ... --no-build --settings .../NewManga.runsettings`）；r3-P2-04 未处置，与 FEA-04 r2 P1-02「命令须为冻结形式」的教训冲突 | 恢复完整命令串（sln 路径 + `apps/desktop-avalonia/tests/NewManga.runsettings`） |
| **R4-P2-02** | P2 | 卡 `:40-44`（来源链）；`FEA-03.md:153` L-2；`FEA-04.md:99` L-2 | L-2 解除记录仍缺：上游要求「透传 Draft/新增命令 → blocked，先完成 M2-C1」，本卡改走 V11R 命令契约（F0-1 先例），但卡内无该判定记录，阻塞是否解除在证据上不可核 | 来源链加一行「L-2 解除依据：F0-1 先例（V11R 契约 §8 + 独立契约文档；M2-C1 不逐族追加）」 |
| **R4-P2-03** | P2 | 卡 `:94`；`REBASELINE_PLAN.md`、`TASK_LEDGER.md`、`STATUS.md` | `:94` 称 `FEA-05-PORT-1` **已登记**，但三份权威指针均无该节点（本轮 `git grep` 为空）——陈述不实，且该卡承载 C-07 UNFREEZE，悬空将无人承接 | 要么由 DSH 在 PLAN 真正登记（候选/未释放），要么卡内改为「待 DSH 建卡」 |
| **R4-P2-04** | P2 | 卡 `:32-34`；`check.ps1:614-621`；`STATUS.md:19`；`TASK_LEDGER.md:9-13` | r3-P2-07 未处置：STATUS 45/45 行、3124/3200 bytes（任何新增行触发预算报错）；`:19` 的 LEDGER 计数（483=471+11+1）与现行 491/480/10 不符 | 卡内加前置「STATUS 须同批压缩」；顺手刷新 `:19` |
| **R4-P2-05** | P2 | 卡 `:72-80`、`:127` | kill-criteria 仍缺（建议「公式=契约文档/映射表未定则不得开工」）；`:127` 仍「无 worktree」且未给理由（FEA-03/04 先例均用 worktree） | 各补一句 |
| **R4-P2-06** | P2 | 卡 `:92-96`（禁止范围） | 仍无「不得弱化/删除既有契约对照断言（只允许新增）」红线；本卡 P0-01 的处置恰好需要修改 `RegionWriteCommandTests`，无此红线将无法区分「按 DSH 授权改写不变式」与「静默弱化断言」 | 禁止范围加一句，并要求对 `RegionWriteCommandTests` 的任何改动在 Handoff 逐行说明且由 DSH 授权 |
| **R4-P2-07** | P2 | 卡 `:60`、`:61`、`:65`、`:70` | wire 字段细节三处：①`drafts_patch` 未列 `scheduleFlush?`（与 W-7「只透传既有参数」不完全一致，或明确不透传、固定默认 `true`）；②`drafts_open` 的 `baseRevisionId` 是「无默认值可空参」，卡标 `?` 但未写「省略即传 None」；③`drafts_discard` 响应 `{"discarded": true}` 是 handler 合成的 ack（服务返回 `None`），未注明来源 | 三处各补半句 |
| **R4-P2-08** | P2 | 卡 W-5 `:106`、AC1 `:84`；先例 `V11R_REGION_WRITE_CONTRACT.md:3` | 契约文档由 `PENDING` 升级 `FROZEN` 的**触发条件/责任人/证据**未写（W-5 只说「DSH 复核后置 FROZEN，合入 main 后升级」），AC1 只验 `PENDING` 头部；后续谁在什么 commit 升级、以何为据不可核 | W-5 补一句「合入 DSH 集成 commit 后由 DSH 在同一批把状态行改 `FROZEN` + 变更记录追加 + 冻结记录（如需）」 |

---

## 4. 处置建议（最小成本）

1. **先裁 R4-P0-01（返回 DSH）**：按 §2.4(a) 授权「追加集 = 各家族声明集合之并」并同步（i）`RegionWriteCommandTests:107-117`、（ii）`V11R_REGION_WRITE_CONTRACT.md` 变更记录 v1.6、（iii）W-6 的最终语义（扩展或另立）与 `CommandParityContractTests` 断言。这是唯一阻碍 `ready` 的结构性冲突。
2. **R4-P1-01**：C081 响应改为 `revisionIds` 映射 + 重放幂等测试项。
3. **R4-P1-02**：契约文档 §3 逐码表（冻结词表内 category + retryable 判据）+ `cause_code` 处置 + AC1 增核验。
4. P2 批量顺手：完整命令、L-2 记录、PORT-1 真实登记、STATUS 预算/陈旧计数、kill-criteria/worktree、断言红线、wire 字段三处、契约升级流程。
5. 改卡后派 **r5**；P0/P1 = 0 才置 `ready`。

## 5. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的契约/代码/测试事实与治理指针），**不构成实现验收**，也不构成契约、设计或架构批准。结论仅指该范围文本是否可执行、可机械验证、与上游先例和治理规则一致。

本席位（`fea05-wire-scope-reviewer`，r1→r2→r3→r4 同一席位续任）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、契约、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内行号基于 `c4a88a76d` 实测；标注「未验证」的项（931/0/60 是否仍成立、契约落盘后测试是否真通过）不得当作已核实事实引用。
