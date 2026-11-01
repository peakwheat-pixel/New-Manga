---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: c4a88a76d
reviewed_head: 25b69b974
decision: changes_requested
counts: { P0: 0, P1: 1, P2: 10 }
---

# FEA-05-WIRE-1 范围复核 r5（同一独立席位续任）

| 字段 | 值 |
|---|---|
| base_commit | `c4a88a76d4c4c139c0897d629296fc5d5aac1595`（r4 的 reviewed_head；范围 v5 的父提交） |
| reviewed_head | `25b69b9741d00ed30d9e4b5db7b80b90d6492d54`（`docs(fea-05-wire-1): 范围 v5…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（**v5**，130 行；status=proposed） |
| 与 r4 的 diff | `git diff --stat c4a88a76d..25b69b974` → 本卡 21+/11−；`doc/reviews/FEA-05-WIRE-1-scope-r4.md` 入库。契约文档与 §8 行仍未落盘（卡内交付物，正常） |
| reviewer | `fea05-wire-scope-reviewer`（r1→r2→r3→r4→r5 同一席位续任） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与该卡起草/实现/返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | 仅范围冻结文本（AC1–AC7、映射表、W-1…W-7、写域、治理三绿）；不含实现审查 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 1 / P2 = 10（共 11）** |

> **一句话理由**：r4 的 **P0（W-6 与 Region 冻结不变式冲突）已实质解除**——本卡不再接 CoreClient/registry，`RegionWriteCommandTests` 与 FROZEN `V11R_REGION_WRITE_CONTRACT.md` 均不动，AC5（全量 sln 不退化）因此**成立**，且没有 registry 相关 AC 冲突；R4-P1-01（C081 响应）与 R4-P1-02（W-4 词表）也已修好。**不能写 approved 的唯一原因**是 P0 处置不彻底：交付表 `:79` 的「测试」行与测试要求表 `:113-114` 的 AC3 行**仍保留 CoreClient/registry/parity 可执行指令**，与本卡刚冻结的 W-2/W-6（CoreClient 不在本卡）和 AC3 `NOT_APPLICABLE` 直接矛盾——这是最后一条「冻结范围自相矛盾」项，改两行文字即可关闭。其余 10 条均为 P2（含 8 条 r4 遗留 P2 未处置）。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**（在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- **未执行**：`dotnet build`/`dotnet test`、`python -m pytest`、UI 真机。931/0/60 在当前 head **未验证**（引用链：`doc/handoffs/FEA-04-68c72ba57.md:184`、`verification/FEA-04/build-test-raw.log`、`doc/reviews/FEA-04-r3.md:21`）。
- **契约交付物仍未落盘（符合范围卡语义）**：`doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md` ABSENT；`V11R_COMMAND_CONTRACT_V1.md` §8 无 C078–C083 行。二者是本卡交付物，属实现期产物。
- 已执行（只读）：

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `25b69b974…` / 空（clean） |
| `git diff c4a88a76d..25b69b974 -- doc/tasks/FEA-05-WIRE-1.md` | 逐行核对（v5 改动：title、写域删 CoreClient、C081 行、交付表 CoreClient 行、AC3、W-2、W-4、W-6、收敛表、Closeout） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 达预算 80%（3124 bytes / 45 lines） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| `git grep FEA-05-PORT-1 -- doc/REBASELINE_PLAN.md doc/TASK_LEDGER.md doc/STATUS.md` | **空**（三份权威指针均未登记该节点） |

**三绿：是**（`check.ps1` 的 AC 状态门只在 `in_review/approved/done` 生效，`proposed` 下 AC3 的 N/A 标记暂不触发门禁，见 R5-P2-10）。

---

## 1. r4 逐项 disposition（P0=1 / P1=2 / P2=8）

| r4 ID | 级别 | v5 状态 | 证据 |
|---|---|---|---|
| **R4-P0-01** W-6 与 Region 冻结不变式冲突 | P0 | **CLOSED（主体）** | 写域已删 `NewManga.CoreClient/**`、`NewManga.CoreClient.Tests/**`（`:22-33`）；交付表 CoreClient 行改为「不在本卡（W-6）」（`:78`）；W-2 `:102`、W-6 `:106` 重写为「registry/additive 归 FEA-05-PORT-1（需先 UNFREEZE）」；AC3 `:85` 改 `NOT_APPLICABLE`。`RegionWriteCommandTests` 与 `V11R_REGION_WRITE_CONTRACT.md` 未动（本轮 diff 无 apps/doc/contracts 变更）✓。**残留：交付表测试行与测试要求 AC3 行仍要求 CoreClient 工作 → R5-P1-01** |
| **R4-P1-01** C081 响应外形 | P1 | **CLOSED** | `:62` 已改为 `{ "<region_id>": "<region_revision_id>" }`（真实返回值，`drafts.py:500-507`、`:528`），并注明「receipt 元数据不在此返回」✓ |
| **R4-P1-02** W-4 错误语义/Token | P1 | **CLOSED（主体）** | `:104`：category 改为 M2-C1 冻结七值并显式「不用 `infra`」；retryable 规则（默认 false、仅 `unavailable`/`internal` 类 true）；`cause_code`→`details.causeCode`；逐码表写入契约 §3 ✓。**残留：AC1 未把「§3 逐码表」纳入可核项 → R5-P2-02** |
| R4-P2-01 AC5 命令形式 | P2 | **OPEN** | `:87`、`:115` 仍为省略号缩写 → R5-P2-03 |
| R4-P2-02 L-2 解除记录 | P2 | **OPEN** | 来源链 `:40-42` 仍无 L-2 记录 → R5-P2-04 |
| R4-P2-03 `FEA-05-PORT-1` 登记 | P2 | **OPEN（陈述仍不实）** | `:93` 仍写「端口面另卡 FEA-05-PORT-1，**已登记**」；三份权威指针 grep 为空 → R5-P2-05 |
| R4-P2-04 STATUS 预算/陈旧计数 | P2 | **OPEN** | 未处置（本轮 check.ps1 仍报 3124/45；`doc/STATUS.md:19` 仍 483=471+11+1，现行 LEDGER 491/480/10）→ R5-P2-06 |
| R4-P2-05 kill-criteria/worktree | P2 | **OPEN** | `:126` 仍「无 worktree」；无 kill-criteria → R5-P2-07 |
| R4-P2-06 断言弱化红线 | P2 | **OPEN** | 禁止范围 `:91-95` 仍无该红线；写域含 `tests/core/**`、`tests/domain/**`（既有测试可被改写）→ R5-P2-08 |
| R4-P2-07 wire 字段细节 | P2 | **OPEN** | `:60` 仍未列 `scheduleFlush?`；`:59` 未写 `baseRevisionId` 省略即传 `None`；`:64` 未注明 `{"discarded": true}` 为 handler 合成 ack → R5-P2-09 |
| R4-P2-08 契约 PENDING→FROZEN 流程 | P2 | **OPEN** | W-5 `:105` 未变（只说「DSH 复核后置 FROZEN，合入 main 后升级」）→ 并入 R5-P2-01（FROZEN 条件已因收窄而改变） |

**统计（11 项）**：**CLOSED 3**（R4-P0-01 主体、R4-P1-01、R4-P1-02 主体）／**OPEN 8**（R4-P2-01…P2-08 全部未处置）。本轮新增：**P1×1**（R5-P1-01）+ **P2×2**（R5-P2-01 契约一致性措辞、R5-P2-10 卡内元数据/门禁）。

---

## 2. 逐项核查（对应 Lead 的 4 个核查点）

### 2.1 收窄后 AC5 是否成立 / 是否仍有 registry 相关 AC 冲突 —— **AC5 成立；无 registry ACL 冲突；但有 registry 残留指令**

- **AC5（全量 sln 不退化）成立** ✓：本卡写域不再含 `apps/**`（`:22-33` 无任何 `apps/` 路径），唯一 `.NET` 侧动作是「运行」`dotnet build`/`dotnet test`。唯一可能受影响的 .NET 断言来自 §8 文本改动，而本轮已核对：
  - `CommandContractV11RTests` 对 §8 行只要求「ID 为 `C\d{3}` 且 >66、位于标题以 `## 8.` 开头的节下、命令名匹配 `^[a-z][a-z0-9_]*$`、状态 `StartsWith("PENDING")`」（`CommandContractV11RTests.cs:199-202`、`:260-266`、`:92-93`）；新增 6 条 pending 行**不需要 registry 注册**（`:104-110` 对未注册的 pending 名跳过）。
  - `RegistrySurface_IsFullyDeclared`（`:68-86`）只要求「已注册命令必须在契约声明」，注册表不变 → 仍通过。
  - `RegionWriteCommandTests` 的「追加集 == RegionWrite ∪ RegionRead」不变式（`:107-117`）在 registry 不变时**不受影响** ✓。
  结论：AC1（`CommandContractV11RTests` 通过）+ AC5（sln 不退化）**同时成立**，不再有 r4 那种互斥。
- **registry 相关 AC 冲突**：**无**。AC3 已 N/A（`:85`），其余 AC 不含 registry 断言（AC1 只到契约测试、AC6 只到 C-07/生成器/check）。
- **但残留 registry 可执行指令（P1）**：交付表「测试」行 `:79` 仍写「Python：…；**CoreClient：序列化/registry/parity/错误映射**」；测试要求表 `:113-114` 仍列「`AC3 | dotnet test apps/desktop-avalonia/tests/NewManga.CoreClient.Tests | .NET | NOT_RUN`」。两者与 `:78`「CoreClient 不在本卡」、W-2 `:102`、W-6 `:106`、AC3 N/A 直接矛盾，且写域已无 `apps/**`——按冻结文本执行即越权。这是 P0 处置的**未清理残留** → **R5-P1-01**。

### 2.2 C081 响应 —— **已与真实实现一致**

`apply_candidates` 成功路径构造 `receipt_data`（`tokenId`/`DraftId`/`DraftSequence`/`revisionIds`/`contentDigests`/`committedAt`，`drafts.py:500-507`），最终 `return dict(receipt_data["revisionIds"])`（`:528`），重放分支同样返回 `revisionIds`（`:389-407`）。卡 `:62` 现写 `{ "<region_id>": "<region_revision_id>" }` 并注明 receipt 元数据不在此返回 ✓ 一致。

### 2.3 W-4 逐码表要求是否足以在实现期机械验证 —— **规范本身够，但 AC1 没有锚点**

- 规范侧已可判定：`DraftError(code, message="", *, details=None, cause_code=None)`（`errors.py:64-73`）→ 信封 `{code, category, message, retryable, details?}`（`make_error_envelope`，`core_service.py:808-825`）；W-4 `:104` 冻结了 category 七值词表（与 `M2-C1_TYPED_IPC_CONTRACT.md:380` 一致）、retryable 判据、`cause_code`→`details.causeCode`、逐码表落契约 §3 ✓。
- **可机械验证性缺口**：AC1 `:83` 只要求契约文档「含头部与五节」，**没有**要求 §3 含「14（可达）码逐码表」，也没有样例格式（列：code/category/retryable/details 形态）。实现者写一段散文化 §3 也能过 AC1 → W-4 的冻结在验收上无锚点 → **R5-P2-02**。
- 另需一句消歧：W-4 同时给了「类别规则（仅 unavailable/internal 类 true）」与「逐码表」——应写明**逐码表优先**，避免实现者按类别批量置 true（例如同属 `internal` 的 `DRAFT_APPLY_FAILED` 重试通常无效、而 `DRAFT_JOURNAL_UNWRITABLE` 可重试）。

### 2.4 AC1–AC7 可验收性（AC3 为 N/A）

| AC | 判定 | 依据 |
|---|---|---|
| AC1 契约（`:83`） | **可验收（弱）** | 头部+五节+§8 六行+段首/约束/§10 同步+解析器约束均可机械核；弱在未纳 §3 逐码表（R5-P2-02） |
| AC2 语义不变（`:84`） | **可验收** | 六条签名与真实方法逐字一致（v4 已核，v5 未改）；C081 响应已修正；`EditToken` 整对象回传要求明确 |
| AC3（`:85`） | **N/A 合法** | 标记 `<<NOT_APPLICABLE: 原因>>` 合法且给因；**门禁提醒**：`check.ps1:842-844` 要求 `NOT_APPLICABLE` 必须**勾选**（`[x]`），当前为 `[ ]`——`proposed` 下不触发，转 `in_review` 前必须改 `[x]`，否则 `check.ps1` FAIL（R5-P2-10） |
| AC4 Python 测试（`:86`） | **可验收** | `tests/core/**`、`tests/domain/**` 在写域；pytest 配置支持该命令；「每命令一成功+一失败」可核 |
| AC5 回归（`:87`） | **可验收（形式待补）** | 无 `apps/**` 变更 → 基线可保；但命令仍省略号（R5-P2-03） |
| AC6 治理（`:88`） | **可验收** | 三绿本轮实测 ✓ |
| AC7 证据（`:89`） | **可验收** | `evidence_dir` 在写域 ✓ |

**结论：6 条可验收 + 1 条 N/A；无不可满足项。**

### 2.5 写域（遗漏 / 过度）

- **无遗漏**：契约文档 `:24`、master `:25`、`src/bootstrap/core_service.py`（族集合/dispatch/6 handler/`CoreServiceServer.__init__`/`main()` 注入均在该文件）、`tests/core/**`、`tests/domain/**`、`verification/FEA-05-WIRE-1/**`、三份指针文档、评审目录 ✓。
- **已正确移除**：`apps/desktop-avalonia/src/NewManga.CoreClient/**`、`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/**`、`src/application/editing/**`、端口三文件 ✓。
- **轻度过宽（不阻断）**：`tests/domain/**` 全开放——本卡大概率不需要改 domain 测试（AC4 只是运行它），可收窄为「只读运行」或限定新文件；`tests/core/**` 全开放可接受（先例同），但需配「断言弱化红线」（R5-P2-08）。

### 2.6 是否仍有需 DSH 裁决项 —— **无新的裁决缺口；但 deferral 目标必须真实存在**

- 本卡自身的裁决点（W-1…W-7）已自洽：W-1 兼容扩展、W-2 不接 UI/CoreClient、W-3 六命令、W-4 错误语义、W-5 文档归属、W-6 registry 顺延、W-7 flush 顺延。
- **需 DSH 落实的一项**（非新裁决，是登记动作）：`FEA-05-PORT-1` 现在同时承载「drafts registry/additive 扩展 + V11R 契约 UNFREEZE（把不变式升级为各家族集合之并）+ C-07 端口 UNFREEZE + IHostController 端口面」，但该节点在 PLAN/LEDGER/STATUS **均未登记**（本轮 grep 为空），而卡 `:93` 已称「已登记」→ R5-P2-05。若该 deferral 目标不落地，本卡落地的 Core 命令面将无消费者、冻结契约不变式也无人升级。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R5-P1-01** | P1 | 卡 `:79`（交付表「测试」行）、`:113-114`（测试要求表 AC3 行）↔ `:78`、`:85`（AC3 N/A）、`:102`（W-2）、`:106`（W-6）、`:22-33`（写域） | **P0 处置的未清理残留 → 冻结范围自相矛盾。** 交付表仍把「CoreClient：序列化/registry/parity/错误映射」列为交付项；测试要求表仍给 AC3 一条 `dotnet test …CoreClient.Tests` 的 NOT_RUN 行。二者与本卡刚冻结的「CoreClient 不在本卡」及 AC3 `NOT_APPLICABLE` 直接矛盾，且写域已无 `apps/**`——按冻结文本执行即越权（或让 Owner 在评审答复时被迫自行裁决） | 删掉交付表测试行的「；CoreClient：…」半句；把测试要求表 AC3 行改为 `N/A（归 FEA-05-PORT-1）` 或直接删除该行；改完后本卡即 P0/P1=0 |
| **R5-P2-01** | P2 | 卡 `:76`（§8 指针行）、W-1 `:101`、W-5 `:105`；`V11R_COMMAND_CONTRACT_V1.md:220-242`、`:495-499` | **契约/§8 的三处措辞需随收窄调整：** ①**Core 路由名未定义**——本卡只落 Core 命令面，但表里只有「Host 命令」列（`:57`），JSON-lines 的 `command` 字符串（`drafts_open` 还是 `drafts.open`）全卡未写；建议明确「Core 路由名 = Host 命令名（沿 Region 先例：registry `create_region` ↔ Core `create_region`）」；②W-1 仍写「`PENDING→合入后 FROZEN`」，但本卡只合入 Core 面、registry 归 PORT-1 → 升级条件应改为「wire + PORT-1 registry 均合入后由 DSH 升级 FROZEN」，§8 状态字面量建议 `PENDING(FEA-05-WIRE-1/PORT-1)`；③`:76` 的「§8 段首说明（命令总数…）」有歧义——§8 现有段落是 Region 家族叙述（66→76/77），应**新增**一段 drafts 家族说明（83），而不是改写 Region 数字；④§8 约束段需写明「C078–C083 在 PORT-1 完成 registry 注册前不得被消费」 | 四处各补一句；同步更新 W-5 的 FROZEN 触发条件 |
| **R5-P2-02** | P2 | 卡 `:83`（AC1）、W-4 `:104`；`errors.py:64-73`；`M2-C1:380` | **W-4 的逐码表在 AC 层无锚点。** AC1 只要求契约文档「含头部与五节」，未要求 §3 含逐码表（列：code / category∈七值 / retryable / details 形态）；也缺「逐码表优先于类别规则」的消歧句，实现者可批量按类别置 retryable=true（如 `DRAFT_APPLY_FAILED` 属 internal 但重试无效） | AC1 增一句「§3 含六命令可达码的逐码表（code/category/retryable/details 形态），category ∈ M2-C1 七值，无 `infra`」；W-4 补「逐码表优先」 |
| **R5-P2-03** | P2 | 卡 `:87`（AC5）、`:115`（测试要求） | AC5/测试表仍是省略号缩写（`dotnet test ... --no-build --settings .../NewManga.runsettings`）；r4-P2-01 未处置，与 FEA-04 r2 P1-02「命令须为冻结形式」的教训冲突 | 恢复完整命令串 |
| **R5-P2-04** | P2 | 卡 `:40-42`（来源链）；`FEA-03.md:153` L-2；`FEA-04.md:99` L-2 | L-2 解除记录仍缺：上游要求「透传 Draft/新增命令 → blocked，先完成 M2-C1」；本卡改走 V11R 命令契约（F0-1 先例），但卡内无该判定记录，阻塞是否解除在证据上不可核 | 来源链加一行「L-2 解除依据：F0-1 先例（V11R 契约 §8 + 独立契约文档；M2-C1 不逐族追加）；FEA-05 同法」 |
| **R5-P2-05** | P2 | 卡 `:93`；W-6 `:106`；`REBASELINE_PLAN.md`、`TASK_LEDGER.md`、`STATUS.md` | `FEA-05-PORT-1` 在 `:93` 被称「已登记」，但三份权威指针均无该节点；该卡现承载 drafts registry/additive + V11R 契约 UNFREEZE + C-07 UNFREEZE + 端口面，是本卡 Core 命令面的唯一消费/注册路径 | 由 DSH 在 PLAN 登记（候选/未释放，写明其四项范围），或把 `:93` 改为「待 DSH 建卡」 |
| **R5-P2-06** | P2 | 卡 `:30-32`；`check.ps1:614-621`；`STATUS.md:19`；`TASK_LEDGER.md:9-13` | r4-P2-04 未处置：STATUS 45/45 行、3124/3200 bytes（任何新增行触发预算报错）；`:19` 的 LEDGER 计数（483=471+11+1）与现行 491/480/10 不符 | 卡内加前置「STATUS 须同批压缩」；顺手刷新 `:19` |
| **R5-P2-07** | P2 | 卡 `:71-79`、`:126` | r4-P2-05 未处置：无 kill-criteria（建议「契约文档/§3 逐码表未定则不得开工」）；`:126` 仍「无 worktree」且未给理由 | 各补一句 |
| **R5-P2-08** | P2 | 卡 `:91-95`（禁止范围）；写域 `:27-28` | r4-P2-06 未处置：仍无「不得弱化/删除既有断言（只允许新增）」红线；本卡写域含 `tests/core/**`、`tests/domain/**` 既有测试文件 | 禁止范围加一句（针对 Python 既有测试与契约对照） |
| **R5-P2-09** | P2 | 卡 `:59`、`:60`、`:64`、`:69` | r4-P2-07 未处置（wire 细节三处）：①`drafts_patch` 未列 `scheduleFlush?`，与 W-7「只透传既有参数」不完全一致（或明确固定默认 true）；②`drafts_open` 的 `baseRevisionId` 是「无默认值可空参」，卡标 `?` 但未写「省略即传 `None`」；③`drafts_discard` 的 `{"discarded": true}` 是 handler 合成 ack（服务返回 `None`），未注明来源 | 三处各补半句 |
| **R5-P2-10** | P2 | 卡 frontmatter `:14`、标题 `:36`、章节 `:53`、Closeout `:130`、AC3 `:85`；`check.ps1:842-844` | 卡内元数据/门禁细节四处陈旧：①frontmatter `base_commit: a62d9ca10`（v5 应为 `c4a88a76d`）；②正文标题仍「（v4，签名冻结版）」；③章节名仍「命令清册与真实签名映射（冻结，v4）」；④Closeout 仍「待 r4 复核」（应为 r5）；⑤AC3 为 `[ ]` + `NOT_APPLICABLE`，而 `check.ps1:842-844` 要求 N/A **必须勾选**——转 `in_review` 前须改 `[x]`，否则治理检查 FAIL | 五处一次性刷新 |

---

## 4. 处置建议（最小成本）

1. **R5-P1-01（唯一 P1）**：删 `:79` 的 CoreClient 半句、`:113-114` AC3 行改 N/A 或删——改完本卡即 P0/P1=0，可进 r6 或直接 approved（若只差这一处，建议改卡后派 r6 做形式核对）。
2. **R5-P2-01**：一次把四句话补齐（Core 路由名、FROZEN 升级条件与 §8 状态字面量、§8 新增段落而非改 Region 数字、约束段）。
3. **R5-P2-02**：AC1 加 §3 逐码表锚点；W-4 补「逐码表优先」。
4. P2 批量：完整命令（03）、L-2（04）、PORT-1 真实登记（05）、STATUS 预算/陈旧计数（06）、kill-criteria/worktree（07）、断言红线（08）、wire 三处细节（09）、卡内元数据/门禁（10）。
5. 改卡后派 **r6** 复核；P0/P1 = 0 才置 `ready`。

## 5. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的契约/代码/测试事实与治理指针），**不构成实现验收**，也不构成契约、设计或架构批准。结论仅指该范围文本是否可执行、可机械验证、与上游先例和治理规则一致。

本席位（`fea05-wire-scope-reviewer`，r1→r2→r3→r4→r5 同一席位续任）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、契约、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内行号基于 `25b69b974` 实测；标注「未验证」的项（931/0/60 是否仍成立、§8 行落盘后测试是否真通过）不得当作已核实事实引用。
