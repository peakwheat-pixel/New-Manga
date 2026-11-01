---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 2a8baf3a7
reviewed_head: d9d7dde41
decision: approved
counts: { P0: 0, P1: 0, P2: 10 }
---

# FEA-05-WIRE-1 实现复核 r3（同一独立席位；只审过范围、未参与实现）

| 字段 | 值 |
|---|---|
| base_commit | `2a8baf3a7229cefa6234e13627bbf91a4d283b10`（impl-r2 被审 head） |
| reviewed_head | `d9d7dde41a8df244c087dabc70a750090771ba61`（`fix(fea-05-wire-1): 处置实现复核 r2…`；`git status --porcelain` 为空） |
| 与 base 的 diff | `git diff --stat 2a8baf3a7..d9d7dde41` → 9 files, +163/−12；实质改动 = 主契约 1 行（`### 8.2` → `## 8.2`）、FEA-05 契约 1 行（`LOCK_CHANGED` retryable `false`）、`core_service.py` 1 行（`_DRAFT_RETRYABLE`）、tests 29 行（断言 + 新解析守卫）、证据日志/说明 |
| reviewer | `fea05-wire-scope-reviewer`（范围 r1–r7 同一席位；实现 rev 第 3 轮；**未参与实现**，实现者为 DSH，符合 2026-10-31「上下文独立」裁决） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | P1-A 关闭情况（含解析断言的判别性）、retryable 与 W-4 一致性、新问题、剩余 P2 disposition、AC1–AC7、治理三绿 |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 10（10 条均为接受遗留/非阻断）** |

> **一句话结论**：**approved**。P1-A 已真实关闭：主契约 `:245` 改为 `## 8.2 …`，新增守卫测试 `tests/core/test_draft_commands.py:215-240` 按 C# 解析器同规则重放并断言可见集合恰为 C078–C083；我做了**判别性验证**——把文件中的 `## 8.2` 换成 `### 8.2` 后，同一逻辑得到**空集合**（测试必失败），说明该断言不是空转。`retryable` 已按 v5.2 W-4 纠正（`LOCK_CHANGED` → `false`），契约 §3 17 码表与 `_DRAFT_ERROR_CATEGORY`（19 项）逐码比对 **0 mismatch**，且 true 仅落在 `unavailable`/`internal`。回归实测：`pytest` 12/900、定向 `dotnet` 80/80、三绿 PASS。剩余 10 条 P2 均不阻断，其中 AC7 证据表/AC 标记需 DSH 在转 `in_review`/收口前补齐。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**。
- 已执行（本轮实测）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `d9d7dde41…` / 空（clean） |
| `python -m pytest tests/core/test_draft_commands.py -q` | **12 passed**（0.29s） |
| `python -m pytest tests/core tests/domain -q` | **900 passed, 1 warning（59.07s）, EXIT 0** |
| `dotnet test …CoreClient.Tests --filter "…CommandContractV11RTests\|…RegionWriteCommandTests"` | **80 passed / 0 failed**（46ms） |
| 解析器判别性模拟（PowerShell 重放 `:216-217`/`:260` 规则） | 现行 heading → `C078,C079,C080,C081,C082,C083`；把该行换回 `### 8.2` → **空集合** ⇒ 断言具判别性 ✓ |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 3062 bytes / 31 lines |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| 契约 §3 ↔ 代码映射自动比对 | 表 17 行、代码映射 19 项（17 + INTERNAL/UNKNOWN）、**category/retryable 不一致 = 0**；`_DRAFT_RETRYABLE = {PAGE_SIZE_UNAVAILABLE, DRAFT_JOURNAL_UNWRITABLE, INTERNAL}` |
| 证据日志核对 | `pytest-draft-commands.log`=12 passed、`pytest-core-domain.log`=`900 passed, 1 warning in 59.22s`、`dotnet-coreclient-contract.log`=80 passed ✓ 与实测一致 |

- **未执行**：全量 `dotnet build/test`（本提交仍无 `apps/**` 变更；定向 80/80 已复现）；全量 931/0/60 仍**未验证**，建议集成时补跑。

---

## 1. impl-r2 逐项 disposition

| r2 ID | 级别 | 状态 | 证据 |
|---|---|---|---|
| **P1-A** `### 8.2` 行不可见 | P1 | **CLOSED** | 主契约 `:245` 已改 `## 8.2 C078–C083 Draft 命令面（PENDING, FEA-05-WIRE-1）`；`"## 8.2".StartsWith("## 8.")` 为真 → 解析器 section 命中 `:260` 条件，6 行可解析；新增守卫测试 `:215-240` 按同规则重放并断言可见集合恰为 6 条；**判别性已实测**（换回 `###` → 空集合） |
| P2-1 `details` 形状 | P2 | **OPEN（接受遗留）** | `_draft_error_envelope`（`:853-866`）未改：无 cause 时 dict 原样入信封、有 cause 时数组；`make_error_envelope` 约定为 `list[dict]` |
| **P2-2** `LOCK_CHANGED` retryable | P2 | **CLOSED** | `core_service.py:850` 已从集合移除；契约 `FEA-05…:60` 改为 `false` 并注明「需重读状态，不自动重试；W-4」；测试 `:173-174` 同步断言 false；与 v5.2 W-4「仅 `unavailable`/`internal` 类为 true」一致 |
| P2-3 可选字段类型校验 | P2 | **OPEN（接受遗留）** | `:2998-3052` 未改（`regionId`/`draftId`/`baseRevisionId`/`undoCursor`/`candidateIds` 元素） |
| P2-4 契约 §4 `UNKNOWN` 码名 | P2 | **OPEN（接受遗留，DSH 已表态）** | 契约 `:71` 仍写 `UNKNOWN`/`validation`，实际 `UNKNOWN_COMMAND`（`:5588-5592`）；交付说明记「保持，待 PORT-1 统一」——事实性措辞仍不准，但不影响本卡 wire 行为 |
| P2-5 卡/证据/收口 | P2 | **OPEN（收口前置）** | 本轮未改卡（diff 无 `doc/tasks/FEA-05-WIRE-1.md`）：仍 `status: ready`、AC1/2/4/6/7 仍 `<<TODO>>`、Canonical Evidence 占位、Closeout 含 stray CR 与旧「待 r4 复核」行 |
| P2-6 bridge-only 证据 | P2 | **接受遗留** | 交付说明已声明 fake 服务；真实集成归 FEA-05-PORT-1 |
| P2-7 §10 用 bullet 非表格行 | P2 | **OPEN（接受遗留）** | 主契约 `:280` 仍是表格外 bullet |
| P2-8 §3 词表漏 `cancelled` | P2 | **OPEN（接受遗留）** | 契约 `:43` 仍只列六值 |
| P2-9 真实码 envelope 未测 | P2 | **OPEN（接受遗留）** | tests 仍只覆盖 `EDIT_TOKEN_EXPIRED`/`LOCK_CHANGED`/`INTERNAL` + 非法 payload 三类；`DRAFT_NOT_FOUND`→`not_found` 等未直接断言 |
| P2-10 dispatch 弱测试 + EOF | P2 | **PARTIAL** | 测试文件末尾换行已补 ✓；`test_drafts_dispatch_is_registered_and_typed` 仍用 `inspect.getsource` 文本包含（非行为测试）→ 保留 |
| **P2-11（新）** | P2 | OPEN | `verification/FEA-05-WIRE-1/delivery-notes.md` 的 **impl-r1 处置表仍写「P2-02 retryable：保留 LOCK_CHANGED=true（W-4 已冻『锁冲突 true』…）」**，与同一文件新增的 impl-r2 行（已改为 false）**自相矛盾**；且该文件仍有 stray CR/制表符（`\test_…` 等） |

---

## 2. 关键验证细节

### 2.1 P1-A 判別性（Lead 特别要求）

- C# 解析器：`CommandContractV11RTests.cs:216-217` 在 `## ` **或 `### `** 标题处重置 `section`；`:260` pending 行仅接受 `section.StartsWith("## 8.")`。
- 现状：主契约 `:245` = `## 8.2 …` → `section` 以 `## 8.` 开头 → `:251-256` 六行被解析；`dotnet` 80/80（若 6 行未被解析，测试同样会过——故单看 80/80 不足以证明）。
- 新增守卫 `tests/core/test_draft_commands.py:215-240` 复刻上述两条规则；我另用独立脚本重放：
  - 现行文件 → `visible = ["C078","C079","C080","C081","C082","C083"]`；
  - 把文件中该行换回 `### 8.2 …` → `visible = []`；
  - ⇒ 若 DSH 未来退回三级标题，该测试**必然失败**，断言不是空转。
- 同时核实：`## 8.2` 不破坏 `## 9.` 的收束（`:260`），也不影响 `### 4.x` 基线分支与 C067–C077 既有 pending 行。

### 2.2 retryable 与 W-4 一致性

- 契约 §3：17 码逐码 `category`/`retryable`；`true` 仅 `PAGE_SIZE_UNAVAILABLE`（unavailable）、`DRAFT_JOURNAL_UNWRITABLE`（unavailable）；行外注记 `INTERNAL`（internal, true）。
- 代码：`_DRAFT_RETRYABLE = {"PAGE_SIZE_UNAVAILABLE", "DRAFT_JOURNAL_UNWRITABLE", "INTERNAL"}`（`:850`）→ 与表逐项一致；自动比对（17 行表 vs 19 项映射）**0 mismatch**；`LOCK_CHANGED` 表/码/测试三处均为 `false` ✓。
- 与 W-4 对齐：「仅 `unavailable`/`internal` 类为 true」成立（`DRAFT_APPLY_FAILED` 为 internal 但 false，属「仅…才可为 true」的必要条件，未被违反）。

### 2.3 回归与新问题

- Python：`tests/core/test_draft_commands.py` 12 passed、全量 `tests/core tests/domain` 900 passed（较 base +1 = 新增守卫）、EXIT 0。
- C#：定向 `CommandContractV11RTests|RegionWriteCommandTests` 80/80（新增 pending 行后仍全绿，无隐藏计数断言）。
- 三绿：`check.ps1` PASS（2 warnings）/ `verify_pins` 15/15 / api inventory EXIT 0。
- 改动面：9 files / +163−12，实质仅 4 处代码/文档（主契约 1 行、FEA-05 契约 1 行、`core_service.py` 1 行、tests 29 行）+ 证据/评审文件；**未发现新问题**（唯一新增的 P2-11 是证据文档陈旧行，非功能问题）。

---

## 3. AC 逐项判定

| AC | 判定 | 说明 |
|---|---|---|
| **AC1 契约** | **通过** | 契约文档头部/五节/§3 17 码逐码表 ✓；§8 追加 6 行（7 列/下划线/PENDING）✓ 且**可被解析器识别**（P1-A 修复 + 守卫测试）；§8 标题/§10 已同步；`CommandContractV11RTests` 80/80（现有真实断言） |
| **AC2 语义不变** | **通过** | 只调真实签名；`EditToken` 整对象；C081 裸映射；未改 `src/application/editing/**`/`src/domain/drafts/**` |
| **AC3 CoreClient** | **N/A（合法）** | 卡 `:85` `[x]` + 原因；实现未接 registry |
| **AC4 Python 协议测试** | **通过** | 全量 900 passed（实测）；每命令至少一成功 + 一失败成立（12 项） |
| **AC5 回归** | **部分验证** | 无 `apps/**` 变更；定向 C# 80/80；Python 900/0；**全量 sln 未重跑（未验证）**——建议 DSH 集成时补跑基线 931/0/60 |
| **AC6 治理** | **通过** | 三绿本轮独立实跑 |
| **AC7 证据** | **未完成（收口前置）** | 日志/交付说明与实测一致；但卡 Canonical Evidence 仍占位、AC 未标、卡仍 `ready` → P2-5，须在转 `in_review`/`done` 前补齐 |

---

## 4. 结论与建议

1. **实现复核结论：approved**（P0 = 0 / P1 = 0）。实现方向、契约一致性、错误语义与测试覆盖已满足冻结范围；P1-A 与 retryable 两项均真实关闭。
2. **集成前置**（DSH）：①按 AC5 补跑全量 `dotnet build` + `dotnet test --no-build`（基线 931/0/60）；②转 `in_review` 前补齐卡 Canonical Evidence、AC 标记、Closeout（并修 stray CR）；③建议在集成提交中分离 DSH 记账文件。
3. **剩余 P2（10 条，接受遗留，建议在 PORT-1/收口处理）**：`details` 形状统一（P2-1）、可选字段类型校验（P2-3）、契约 §4 `UNKNOWN_COMMAND` 措辞（P2-4）、卡/证据收口（P2-5）、§10 表格行格式（P2-7）、`cancelled` 词表补全（P2-8）、真实码 envelope 测试（P2-9）、dispatch 行为测试（P2-10）、交付说明陈旧行/控制符（P2-11）、bridge-only 证据（P2-6，已在交付说明声明）。
4. 若 DSH 在集成/收口中改动了本卡范围内的代码或契约，需再次派独立复核；纯记账性改动（STATUS/PLAN/LEDGER/证据表）不需要。

## 5. 边界声明

本报告只审实现与契约一致性，不构成集成验收或契约冻结批准；全量 `931/0/60` 与真实 SQLite 端到端**未验证**。本席位只审过范围、未参与实现（实现者为 DSH），符合 2026-10-31「上下文独立」裁决；未修改被审文件、未 commit/push。
