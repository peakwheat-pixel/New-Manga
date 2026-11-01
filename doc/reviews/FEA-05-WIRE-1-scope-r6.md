---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 25b69b974
reviewed_head: 7346c8efc
decision: changes_requested
counts: { P0: 0, P1: 3, P2: 9 }
---

# FEA-05-WIRE-1 范围复核 r6（形式核对，同一独立席位续任）

| 字段 | 值 |
|---|---|
| base_commit | `25b69b9741d00ed30d9e4b5db7b80b90d6492d54`（r5 的 reviewed_head；范围 v5.1 的父提交） |
| reviewed_head | `7346c8efcd800481c9eb9adf37c8e5ba595c832d`（`docs(fea-05-wire-1): 范围 v5.1…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（**v5.1**，130 行；status=proposed） |
| 与 r5 的 diff | `git diff --stat 25b69b974..7346c8efc` → 本卡 8+/8−；`doc/reviews/FEA-05-WIRE-1-scope-r5.md` 入库。契约文档与 §8 行仍未落盘（卡内交付物，正常） |
| reviewer | `fea05-wire-scope-reviewer`（r1→…→r6 同一席位续任） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与该卡起草/实现/返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | 本轮为 **形式核对**：七项声明逐条验证、AC1–AC7 与写域/交付/禁止范围自洽性、L-2 判定正确性、治理三绿；不含实现审查 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 3 / P2 = 9（共 12）** |

> **一句话理由**：v5.1 修好了 3 项（AC1 §3 逐码表锚点 ✓、AC5 命令补全 ✓、AC3 勾选 N/A ✓、`base_commit`/H1 标题 ✓），但**三个 P1 未关闭**：①r5-P1-01 的修复对象找错了——被要求删的是交付表「**测试**」行 `:79` 的 `；CoreClient：序列化/registry/parity/错误映射` 半句，该行**本轮完全未改**；②新增的 L-2 行 `:97` 把 `\n\n` 写成了**字面字符**，导致「L-2 前置判定」不是节、「附加裁决点（DSH 已裁）」标题被吞掉（卡面结构损坏）；③该 L-2 判定内容本身是**错的**——把 L-2 说成「四表 DDL 未冻」并判 `NOT_APPLICABLE`，而 `FEA-03.md:153`/`FEA-04.md:99` 的 L-2 明确定义为「M2-C1 字节修订 / 新增 Host/Core 命令或 wire 码 → `blocked`」，**本卡正是该条再触发项**；正确写法是记录「触发 → 由 W-1 裁决解除（F0-1 先例）」，不是判 N/A。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**（在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- **未执行**：`dotnet build`/`dotnet test`、`python -m pytest`、UI 真机。931/0/60 在当前 head **未验证**。
- 已执行（只读）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `7346c8efc…` / 空（clean） |
| `git diff 25b69b974..7346c8efc -- doc/tasks/FEA-05-WIRE-1.md` | 逐行核对（6 个 hunk，8+/8−） |
| `Select-String -Path doc/tasks/FEA-05-WIRE-1.md -Pattern '\\n'` | **命中 `:97`**（字面反斜杠-n，见 R6-P1-02） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 达预算 80%（3124 bytes / 45 lines） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| 上游 L 门核对 | `doc/tasks/FEA-03.md:152-154`、`doc/tasks/FEA-04.md:98-100`（L-1/L-2/L-5 定义与再触发条件） |

**三绿：是**（`check.ps1` 的 AC 状态门在 `proposed` 不生效；`in_review` 时 AC3 `[x]`+原因已满足 `check.ps1:842-844` ✓）。

---

## 1. r5 逐项 disposition（P1=1 / P2=10）

| r5 ID | 级别 | v5.1 状态 | 证据 |
|---|---|---|---|
| **R5-P1-01** 交付表/测试表残留 CoreClient | P1 | **OPEN（未关闭）** | 测试要求表 AC3 行已改 `NOT_APPLICABLE`（`:114`）✓、AC3 已勾选 `[x]`（`:85`）✓；**但交付表「测试」行 `:79` 仍原文保留「；CoreClient：序列化/registry/parity/错误映射」**——本轮 diff 未触及 `:71-79` 区块 → R6-P1-01 |
| R5-P2-01 §8/契约措辞四处 | P2 | **OPEN** | `:76`、W-1 `:101`、W-5 `:105` 本轮未改：Core 路由名仍未定义、W-1 仍「PENDING→合入后 FROZEN」、§8 段首「命令总数」歧义、约束段未写「PORT-1 前不得消费」→ R6-P2-01 |
| R5-P2-02 AC1 纳 §3 逐码表 | P2 | **CLOSED** | `:83` 已加「§3 **必须是逐码表**（每码一行 code/category/retryable/触发条件），与 W-4 冲突时以逐码表为准」✓ |
| R5-P2-03 AC5 命令形式 | P2 | **PARTIAL** | AC5 `:87` 已补全为 `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings` ✓；**测试要求表 `:115` 仍是省略号**（`dotnet test ... --no-build --settings .../NewManga.runsettings`）→ R6-P2-02 |
| R5-P2-04 L-2 解除记录 | P2 | **PARTIAL → 升级 P1** | 新增了 L-2 文本，但①`:97` 为字面 `\n` 损坏行；②内容把 L-2 误作「四表 DDL 未冻」并判 `NOT_APPLICABLE`，与上游定义冲突 → **R6-P1-02 + R6-P1-03** |
| R5-P2-05 `FEA-05-PORT-1` 登记 | P2 | **OPEN** | `:93` 仍写「端口面另卡 FEA-05-PORT-1，**已登记**」；三份权威指针仍无该节点（本轮未复检 diff 外文件，PLAN/LEDGER/STATUS 本轮无变更）→ R6-P2-03；**登记本身不阻断批准**（见 §2.1 声明 6） |
| R5-P2-06 STATUS 预算/陈旧计数 | P2 | **OPEN** | 本轮未处置；`check.ps1` 仍报 STATUS 3124 bytes/45 lines；`doc/STATUS.md:19` 仍「LEDGER 483 = 471 + 11 + 1」→ R6-P2-04 |
| R5-P2-07 kill-criteria/worktree | P2 | **OPEN** | `:126` 仍「无 worktree」；无 kill-criteria → R6-P2-05 |
| R5-P2-08 断言弱化红线 | P2 | **OPEN** | 禁止范围 `:91-95` 仍无该红线 → R6-P2-06 |
| R5-P2-09 wire 细节三处 | P2 | **OPEN** | `:59`/`:60`/`:64` 未改（`scheduleFlush?`、`baseRevisionId` 省略→`None`、`discarded` ack 来源）→ R6-P2-07 |
| R5-P2-10 卡内元数据 | P2 | **PARTIAL** | `base_commit: 25b69b974`（`:14`）✓、H1「（v5，收窄至 Core 面）」✓；**但章节 `:53` 仍「（冻结，v4）」、Closeout `:130` 仍「v5（r4）… 待 r4 复核」** → R6-P2-08 |

**统计（11 项）**：**CLOSED 1**（R5-P2-02）／**PARTIAL 3**（R5-P2-03、R5-P2-04、R5-P2-10）／**OPEN 7**（R5-P1-01、R5-P2-01、R5-P2-05、R5-P2-06、R5-P2-07、R5-P2-08、R5-P2-09）。

---

## 2. 形式核对

### 2.1 七项声明逐条验证

| # | DSH 声明 | 实测 | 判定 |
|---|---|---|---|
| 1 | R5-P1-01：交付表 CoreClient 行改「不在本卡」（无序列化/registry/parity 指令）；测试表删 CoreClient 行；AC3 勾选 N/A | CoreClient 行 `:78` 在 v5 时**已**是「不在本卡」（本轮未改）；**真正的残留是「测试」行 `:79` 的 `；CoreClient：序列化/registry/parity/错误映射`，本轮未删**；测试表 `:114` ✓；AC3 `[x]` ✓ | **部分不实**（修复对象错位）→ R6-P1-01 |
| 2 | R5-P2-02：AC1 增 §3 逐码表 + 冲突以表为准 | `:83` 逐字命中 ✓ | **完全属实** |
| 3 | R5-P2-03：AC5 命令补全 | AC5 `:87` ✓ 补全；测试要求表 `:115` 仍省略号 | **部分属实** → R6-P2-02 |
| 4 | R5-P2-04：新增 L-2 前置判定节 | `:97` 为**单行**：`## L-2 前置判定\n\n…\n\n## 附加裁决点（DSH 已裁）`（字面 `\n`）；且内容与上游定义冲突 | **不成立**（结构损坏 + 内容错误）→ R6-P1-02/03 |
| 5 | R5-P2-06（元数据）：base_commit/标题/Closeout | `base_commit` ✓、H1 标题 ✓；**章节 `:53` 仍 v4、Closeout `:130` 仍「v5（r4）…待 r4 复核」**；另注意 DSH 把 r5 编号对错位：r5-P2-06 实为「STATUS 预算/陈旧计数」，元数据是 r5-P2-10（本轮 STATUS 未处置） | **部分属实** → R6-P2-04 + R6-P2-08 |
| 6 | R5-P2-05：PORT-1 是否必须建卡才能 approved | **不必建卡即可 approved。** 先例：FEA-04 的 deferral 表指向 `FEA-05`/`FEA-07`，当时 PLAN 亦无 FEA-07 节点，仍获 approved；`check.ps1` 也不要求 DAG 含尚未释放的卡。**但**卡面 `:93`「已登记」是不实陈述，须改为「待 DSH 建卡（未登记）」或由 DSH 实际登记 | 登记**不阻断**；措辞须改 → R6-P2-03 |
| 7 | 形式核对：AC1–AC7 与写域/交付/禁止范围自洽 | AC 侧自洽（AC3 N/A 合法、`[x]`+原因满足 `check.ps1:842-844`、其余 AC 均可验收）；**交付表 `:79` 与 AC3 N/A/写域矛盾**；**禁止范围 `:93` 与 PLAN 事实矛盾**；**L-2 节与上游门定义矛盾** | **不全自洽** → 3 条 P1 |

### 2.2 AC1–AC7 可验收性

| AC | 判定 | 说明 |
|---|---|---|
| AC1 `:83` | **可验收** | 头部+五节+**§3 逐码表**+§8 六行+段首/约束/§10+解析器约束，均可机械核 |
| AC2 `:84` | **可验收** | 六条签名与 `drafts.py` 逐字一致（v4 已核，v5.1 未改）；C081 响应已对齐真实返回值 |
| AC3 `:85` | **N/A 合法且门禁就绪** | `[x]` + `<<NOT_APPLICABLE: 原因>>` 满足 `check.ps1:842-844` |
| AC4 `:86` | **可验收** | 写域含 `tests/core/**`、`tests/domain/**`；每命令一成功+一失败可核 |
| AC5 `:87` | **可验收** | 完整命令已补；测试表 `:115` 形式残留（P2） |
| AC6 `:88` | **可验收** | 三绿本轮实测 ✓ |
| AC7 `:89` | **可验收** | `evidence_dir` 在写域 |

### 2.3 写域 / 交付 / 禁止范围自洽性

- **写域** ✓：`:22-33` 无任何 `apps/**`；`doc/tasks`、两份 `doc/contracts`、`src/bootstrap/core_service.py`、`tests/core/**`、`tests/domain/**`、`verification/**`、三份指针、评审目录——与 AC1/AC2/AC4/AC6/AC7 覆盖一致。
- **交付表** ✗：`:78`「CoreClient 不在本卡」与 `:79` 测试行「CoreClient：序列化/registry/parity/错误映射」同表矛盾（R6-P1-01）；另 `:75` 契约文档行仍只写「3 错误码与语义」，未同步 AC1 的「§3 逐码表」（P2，R6-P2-09）。
- **禁止范围** ✗：`:93`「端口面另卡 FEA-05-PORT-1，已登记」与事实不符（R6-P2-03）；`:94-95` 与写域一致 ✓。
- **L-2 判定** ✗✗：定义错位 + 结论错（R6-P1-03）。
- **W 表**：W-1…W-7 内容与 v5 一致 ✓，但**其标题「## 附加裁决点（DSH 已裁）」被 `:97` 吞掉**（R6-P1-02）。

### 2.4 治理三绿

`check.ps1` **PASS（2 warnings）**／`verify_pins.ps1` **PASS（15/15）**／`generate_api_inventory.py --check` **EXIT 0**。注意：三绿**不能证明卡面文本自洽**——上述 3 条 P1 全部在三绿之外。

### 2.5 是否仍有 P0/P1

- **P0 = 0**：r4 的 P0（Region 冻结不变式）已由收窄解除，AC5 成立（r5 已核，v5.1 未回退）。
- **P1 = 3**：R6-P1-01（交付表残留）、R6-P1-02（`:97` 字面 `\n` 损坏）、R6-P1-03（L-2 判定错误）。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R6-P1-01** | P1 | 卡 `:79`（交付表「测试」行）↔ `:78`、`:85`（AC3 N/A）、`:22-33`（写域） | **r5-P1-01 未关闭（修复对象错位）。** 该行仍写「Python：…；**CoreClient：序列化/registry/parity/错误映射**」，与本卡冻结的「CoreClient 不在本卡」/AC3 `NOT_APPLICABLE`/无 `apps/**` 写域矛盾；本轮 diff 未触及 `:71-79` 区块 | 删除 `:79` 末尾「；CoreClient：序列化/registry/parity/错误映射」半句（或整句改为「CoreClient 测试归 FEA-05-PORT-1，不在本卡」） |
| **R6-P1-02** | P1 | 卡 `:97` | **卡面被写成字面转义序列。** `:97` 是单行 `## L-2 前置判定\n\n本卡…\n\n## 附加裁决点（DSH 已裁）`——「L-2 前置判定」不是可解析的节、其正文与下一节标题被合并成一行，「附加裁决点（DSH 已裁）」标题实际消失（W-1…W-7 表失去标题）。卡是冻结范围的唯一权威文本，结构损坏会导致渲染/引用出错 | 把 `:97` 改为三行真实文本：`## L-2 前置判定` + 空行 + 判定正文 + 空行 + `## 附加裁决点（DSH 已裁）` |
| **R6-P1-03** | P1 | 卡 `:97`（L-2 判定）；`FEA-03.md:153`、`FEA-04.md:98-99` | **L-2 判定内容错误（假解除记录）。** 卡把 L-2 描述为「四表 DDL 未冻」（那是 **L-1**，`FEA-04.md:98`）并判 `NOT_APPLICABLE`；但上游 L-2 的定义是「**M2-C1 字节修订**：新增 Host/Core 命令或 wire 码 → `blocked`（FEA-05/07 + 先完成 M2-C1）」（`FEA-04.md:99`；`FEA-03.md:153` 同义）。本卡正是该再触发项（新命令面 + 新 wire 码），不能记 N/A——应记为「**触发**，由 W-1 裁决解除：兼容扩展 + 独立契约文档 + zero protocol bump（F0-1 先例），M2-C1 不逐族追加」 | 重写 L-2 行：`L-2（M2-C1 字节修订）`：**触发**（本卡新增 Host/Core 命令面与 14 个新 wire 码，命中 `FEA-04.md:99` 再触发）→ **解除依据**：W-1 裁决（`V11R_COMMAND_CONTRACT_V1` §8 + 独立契约文档，沿 V11R-F0-1 先例；M2-C1 不逐族追加）；**残余风险**：M2-C1 与 §8 的跨文档一致性由 DSH 在契约冻结时复核。同时补 L-1（四表 DDL）N/A 行 |
| **R6-P2-01** | P2 | 卡 `:76`、W-1 `:101`、W-5 `:105` | r5-P2-01 未处置（四处契约措辞）：Core 路由名仍未定义（建议「Core 路由名 = Host 命令名，沿 Region 先例」）；W-1 仍「PENDING→合入后 FROZEN」（应改为 wire+PORT-1 均合入后升级）；§8 段首「命令总数」歧义（应新增 drafts 家族段落而非改写 Region 数字）；约束段未写「PORT-1 前不得消费」 | 四处各补一句 |
| **R6-P2-02** | P2 | 卡 `:115`（测试要求表 AC5 行） | r5-P2-03 残留：AC5 行已补全，但测试表仍省略号 | 与 `:87` 对齐为完整命令 |
| **R6-P2-03** | P2 | 卡 `:93`；`REBASELINE_PLAN.md`、`TASK_LEDGER.md`、`STATUS.md` | `FEA-05-PORT-1` 仍被称「已登记」，三份权威指针无该节点；**但登记不阻断批准**（FEA-04→FEA-07 未登记先例） | 改为「待 DSH 建卡（未登记）」；建议 DSH 在 PLAN 记候选行（可后置） |
| **R6-P2-04** | P2 | 卡 `:30-32`；`check.ps1:614-621`；`STATUS.md:19`；`TASK_LEDGER.md:9-13` | STATUS 3124 bytes/45 lines 触预算警告；`:19` 的「LEDGER 483 = 471 终态 + 11 非终态 + 1 无 status」与现行台账（491/480/10）不符 | 卡内加前置「STATUS 须同批压缩」；刷新 `:19` |
| **R6-P2-05** | P2 | 卡 `:71-79`、`:126` | 无 kill-criteria；`:126`「无 worktree」未给理由 | 各补一句 |
| **R6-P2-06** | P2 | 卡 `:91-95`（禁止范围） | 仍无「不得弱化/删除既有断言（只允许新增）」红线，而写域含既有 `tests/core/**`、`tests/domain/**` 测试 | 禁止范围加一句 |
| **R6-P2-07** | P2 | 卡 `:59`、`:60`、`:64`、`:69` | wire 细节三处：`drafts_patch` 未列 `scheduleFlush?`；`drafts_open` 的 `baseRevisionId` 省略即传 `None` 未写；`drafts_discard` 的 `{"discarded": true}` 是 handler 合成 ack 未注明 | 三处各补半句 |
| **R6-P2-08** | P2 | 卡 `:53`、`:130` | 元数据残留：章节仍「（冻结，v4）」；Closeout 仍「v5（r4）… 待 r4 复核」（应为 v5.1 / r6） | 两处刷新 |
| **R6-P2-09** | P2 | 卡 `:75`（契约文档行）↔ AC1 `:83` | 交付表契约文档行仍只写「3 错误码与语义」，未同步 AC1 新增的「§3 逐码表」要求 | 行内补「（§3 为逐码表，见 AC1）」 |

---

## 4. 处置建议（最小成本）

1. **三条 P1 一次改完**：`①` 删 `:79` CoreClient 半句；`②` 把 `:97` 拆成正常两节（真换行）；`③` 重写 L-2 判定为「**触发 → W-1 裁决解除（F0-1 先例：§8 + 独立契约文档，M2-C1 不逐族追加）**」并补 L-1（四表 DDL）N/A 行。
2. P2 批量顺手：§8/契约措辞四处（01）、测试表 AC5 行（02）、PORT-1 措辞（03）、STATUS 预算/陈旧计数（04）、kill-criteria/worktree（05）、断言红线（06）、wire 三处细节（07）、章节/Closeout 元数据（08）、契约文档行补 §3（09）。
3. 改卡后派 **r7** 做形式核对（本轮出现「声称已修但文件未改」与「脚本写坏」两类，建议保留一次独立核对）；P0/P1 = 0 即置 `ready`。

## 5. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的契约/代码/测试事实与治理指针），**不构成实现验收**，也不构成契约、设计或架构批准。结论仅指该范围文本是否可执行、可机械验证、与上游先例和治理规则一致。

本席位（`fea05-wire-scope-reviewer`，r1→…→r6 同一席位续任）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、契约、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内行号基于 `7346c8efc` 实测；标注「未验证」的项不得当作已核实事实引用。
