---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 7346c8efc
reviewed_head: be9265b34
decision: approved
counts: { P0: 0, P1: 0, P2: 9 }
---

# FEA-05-WIRE-1 范围复核 r7（形式核对，同一独立席位续任）

| 字段 | 值 |
|---|---|
| base_commit | `7346c8efcd800481c9eb9adf37c8e5ba595c832d`（r6 的 reviewed_head；范围 v5.2 的父提交） |
| reviewed_head | `be9265b342c60a98d63b06b832694aac775f3797`（`docs(fea-05-wire-1): 范围 v5.2…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（**v5.2**，134 行；status=proposed） |
| 与 r6 的 diff | `git diff --stat 7346c8efc..be9265b34` → 本卡 8+/2−（2 个 hunk）；`doc/reviews/FEA-05-WIRE-1-scope-r6.md` 入库。契约文档与 §8 行仍未落盘（卡内交付物，正常） |
| reviewer | `fea05-wire-scope-reviewer`（r1→…→r7 同一席位续任） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与该卡起草/实现/返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | 本轮为 **形式核对**：r6 的 P1×3 逐条验证、AC1–AC7 与写域/交付/禁止范围自洽性、L-2 判定正确性、治理三绿、P2 归属判定 |
| 结论 | **approved** |
| 计数 | **P0 = 0 / P1 = 0 / P2 = 9（9 条均为接受遗留）** |

> **一句话结论**：**approved**。r6 的 3 条 P1 **全部真实关闭**（交付表 `:79` CoreClient 半句已删并由 `Select-String` 复核无命中；字面 `\n` 已清零、`## L-2 前置判定` 与 `## 附加裁决点（DSH 已裁）` 均为独立标题行；L-2 改为「**触发 → W-1 解除**」并补齐 L-1/L-5 N/A，与 `FEA-03.md:153`/`FEA-04.md:98-100` 对齐）。AC1–AC7 均可验收（AC3 为合法 `NOT_APPLICABLE` 且已 `[x]`），写域/交付/禁止范围自洽，三绿 PASS。剩余 9 条 P2 均不阻断冻结，按「接受遗留」处理（建议 ready 前顺手刷新元数据一项，其余归实现期/收口期）。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**（在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- **未执行**：`dotnet build`/`dotnet test`、`python -m pytest`、UI 真机。931/0/60 在当前 head **未验证**（本卡写域无 `apps/**`，AC5 为「运行」而非「修改」）。
- 已执行（只读）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `be9265b34…` / 空（clean） |
| `git diff 7346c8efc..be9265b34 -- doc/tasks/FEA-05-WIRE-1.md` | 2 hunk（`:79` 测试行；L-2 段），8+/2− |
| `Select-String -Pattern 'CoreClient：序列化\|序列化/registry/parity'` | **ABSENT**（残留已清） |
| `Select-String -Pattern '\\n'` | **ABSENT**（无字面换行转义） |
| 标题结构核对 | `:97 ## L-2 前置判定`、`:101 ## 附加裁决点（DSH 已裁）` 均为独立行，W-1…W-7 表恢复标题 ✓ |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 达预算 80%（3124 bytes / 45 lines） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |

**三绿：是**。

---

## 1. r6 逐项 disposition（P1=3 / P2=9）

| r6 ID | 级别 | v5.2 状态 | 证据 |
|---|---|---|---|
| **R6-P1-01** 交付表测试行 CoreClient 半句 | P1 | **CLOSED** | `:79` 现为「…DRAFT_READ_ONLY / DRAFT_INVALID / EDIT_TOKEN_EXPIRED / RECEIPT 相关）；」；`Select-String 'CoreClient：序列化\|序列化/registry/parity'` **无命中** ✓；交付表 5 行（契约文档/§8/Core handler/CoreClient 不在本卡/测试）内部一致 |
| **R6-P1-02** 字面 `\n` 损坏 | P1 | **CLOSED** | 全文 `\\n` **无命中**；`:97` 为真实标题行，`:98-100` 为三行判定，`:101` 为「## 附加裁决点（DSH 已裁）」独立标题，W 表恢复 ✓ |
| **R6-P1-03** L-2 判定内容错误 | P1 | **CLOSED** | `:98` 已改为「**L-2（M2-C1 字节修订）**：…**触发** L-2（`FEA-04.md:99`/`FEA-03.md:153`…）**解除依据**：W-1 裁决——按 F0-1 先例…M2-C1 不逐族追加」；`:99` L-1（四表 DDL 未冻）N/A；`:100` L-5（整库恢复独占锁）N/A ✓ 与上游定义一致 |
| R6-P2-01 §8/契约措辞四处 | P2 | OPEN → **接受遗留** | `:76`、W-1 `:105`、W-5 `:109` 未改（Core 路由名未定义、W-1 仍「PENDING→合入后 FROZEN」、§8 段首「命令总数」歧义、约束段未写「PORT-1 前不得消费」） |
| R6-P2-02 测试表 AC5 仍省略号 | P2 | OPEN → **接受遗留** | `:119` 仍 `dotnet test ... --no-build --settings .../NewManga.runsettings`（AC5 `:87` 已完整） |
| R6-P2-03 `FEA-05-PORT-1`「已登记」 | P2 | OPEN → **接受遗留** | `:93` 未改；三份权威指针仍无该节点（本轮未复检 diff 外文件；r6 已核空） |
| R6-P2-04 STATUS 预算/陈旧计数 | P2 | OPEN → **接受遗留** | 未处置；`check.ps1` 仍报 STATUS 3124 bytes/45 lines；`doc/STATUS.md:19` 仍「LEDGER 483 = 471 + 11 + 1」 |
| R6-P2-05 kill-criteria/worktree | P2 | OPEN → **接受遗留** | `:130` 仍「无 worktree」；无 kill-criteria |
| R6-P2-06 断言弱化红线 | P2 | OPEN → **接受遗留** | 禁止范围 `:91-95` 仍无该红线 |
| R6-P2-07 wire 细节三处 | P2 | OPEN → **接受遗留** | `:59`/`:60`/`:64` 未改（`scheduleFlush?`、`baseRevisionId` 省略→`None`、`discarded` ack 来源） |
| R6-P2-08 卡内元数据 | P2 | OPEN → **接受遗留（新增一处）** | 章节 `:53` 仍「（冻结，v4）」；Closeout `:134` 仍「v5（r4）… 待 r4 复核」；**另：frontmatter `:14` `base_commit: 25b69b974` 自 v5.1 未更新（v5.2 应为 `7346c8efc`）** |
| R6-P2-09 交付表 `:75` 未写 §3 逐码表 | P2 | OPEN → **接受遗留** | `:75` 仍只写「3 错误码与语义」，未同步 AC1 `:83` 的「§3 逐码表」要求 |

**统计（12 项）**：**CLOSED 3**（P1×3，全部真实关闭）／**接受遗留 9**（P2×9）。

---

## 2. 形式核对

### 2.1 三项 P1 逐条验证

1. **交付表测试行**：`:79` 现止于「；」，无 CoreClient 指令；全卡搜索 `CoreClient：序列化` 与 `序列化/registry/parity` 均无命中。交付表现在为「契约文档 / §8 指针行 / Core handler / CoreClient（不在本卡，归 PORT-1）/ 测试（Python）」五行，与 AC1/AC2/AC4、W-2、W-6、写域完全一致 ✓。
2. **`\n` 损坏**：`\\n` 全卡无命中；`:97` `## L-2 前置判定` 是真实标题；`:98-100` 三条判定为真实列表行；`:101` `## 附加裁决点（DSH 已裁）` 独立成行，其下 `:103-111` 的 W-1…W-7 表恢复标题 ✓。**体例提示（非阻断）**：`:97` 标题后与 `:100`→`:101` 之间无空行，与仓库多数文档的「标题后空一行」体例不同；不影响 Markdown 渲染与 `check.ps1`（本轮 PASS），如需统一可顺手补空行。
3. **L-2 判定**：与上游逐字对齐——`FEA-04.md:99`「**L-2** M2-C1 字节修订 … 新增 Host/Core 命令或 wire 码 → `blocked`」、`FEA-03.md:153` 同义；卡 `:98` 记为「**触发**」而不再误判 N/A，并给出解除依据（W-1：§8 追加 + 独立契约文档，F0-1 先例，M2-C1 不逐族追加），与 W-1 `:105` 的裁决一致 ✓。L-1（`FEA-04.md:98`）/L-5（`:100`）两行 N/A 亦与上游定义一致 ✓。**措辞细节（非阻断）**：`:98` 的「本卡新增 Host 命令面与 wire 码」略宽——本卡不注册 Host 命令（registry 归 PORT-1），更精确的表述是「新增 Core 命令面/wire 码 + 在 §8 声明 Host 命令面」；不影响判定成立。

### 2.2 AC1–AC7 可验收性

| AC | 判定 | 说明 |
|---|---|---|
| AC1 `:83` | **可验收** | 头部+五节+**§3 逐码表**+§8 六行+段首/约束/§10 同步+解析器约束，均可机械核 |
| AC2 `:84` | **可验收** | 六条签名与 `drafts.py` 逐字一致（v4 已核，v5.2 未改）；C081 响应已对齐真实返回值 |
| AC3 `:85` | **N/A 合法且门禁就绪** | `[x]` + `<<NOT_APPLICABLE: 原因>>` 满足 `check.ps1:842-844` |
| AC4 `:86` | **可验收** | 写域含 `tests/core/**`、`tests/domain/**`；每命令一成功+一失败可核 |
| AC5 `:87` | **可验收** | 完整命令已补；测试表 `:119` 形式残留（P2-02，接受遗留） |
| AC6 `:88` | **可验收** | 三绿本轮实测 ✓ |
| AC7 `:89` | **可验收** | `evidence_dir` 在写域 |

**6 条可验收 + 1 条 N/A，无不可满足项。**

### 2.3 写域 / 交付 / 禁止范围自洽性

- **写域**（`:22-33`）：无 `apps/**`；含 `doc/tasks`、两份 `doc/contracts`、`src/bootstrap/core_service.py`、`tests/core/**`、`tests/domain/**`、`verification/**`、三份指针、评审目录——覆盖 AC1/AC2/AC4/AC6/AC7 的全部写入需求，无遗漏 ✓。
- **交付表**（`:73-79`）：五行内部一致，无本卡写域外指令 ✓。
- **禁止范围**（`:91-95`）：不接端口面、不改 `src/application/editing/**`、不改 schema/migrations、不改 C-02/C-03/C-04b/C-08 冻结字节、不改 UI、不 push/合并——与写域互不冲突 ✓（`:93` 的「已登记」措辞不实属 P2-03，接受遗留）。
- **L 门**（`:97-100`）：L-2 触发 + 解除、L-1/L-5 N/A，与上游一致 ✓。
- **W 表**（`:103-111`）：W-1…W-7 与 v5 裁决一致，标题已恢复 ✓。

### 2.4 治理三绿

`check.ps1` **PASS（2 warnings）**／`verify_pins.ps1` **PASS（15/15）**／`generate_api_inventory.py --check` **EXIT 0**。`check.ps1` 的 AC 状态门在 `proposed` 不生效；转 `in_review` 时 AC3 的 `[x]`+原因已满足门禁。

### 2.5 P2 逐条 disposition（全部「接受遗留」，附建议时机）

| P2 | 内容 | 处置 | 建议时机/归属 |
|---|---|---|---|
| P2-01 | §8/契约措辞四处（Core 路由名、W-1 FROZEN 条件、§8 段首数字、约束段） | **接受遗留** | 实现期随 AC1 的「§8 段首/约束/§10 已同步」一并落；Core 路由名在契约文档 §1/§2 明确（建议 = Host 命令名，沿 Region 先例） |
| P2-02 | 测试表 `:119` AC5 仍省略号 | **接受遗留** | 实现期一行对齐 AC5 `:87` |
| P2-03 | `:93`「已登记」不实 | **接受遗留** | DSH 记账：改「待 DSH 建卡（未登记）」或实际在 PLAN 登记；不阻断 |
| P2-04 | STATUS 预算/陈旧计数 | **接受遗留** | **建议 handoff 前处理**（STATUS 在写域，任何新增行会触发预算；`:19` 计数已陈旧） |
| P2-05 | kill-criteria/worktree 说明 | **接受遗留** | 实现 Handoff 时补一句 |
| P2-06 | 断言弱化红线 | **接受遗留** | 建议实现前补（写域含既有 `tests/core/**`、`tests/domain/**`） |
| P2-07 | wire 三处细节（`scheduleFlush?`/`baseRevisionId`/`discarded` ack） | **接受遗留** | 建议实现前定，避免契约文档歧义 |
| P2-08 | 元数据（章节 `:53` v4、Closeout `:134` v5/r4、frontmatter `:14` base_commit 25b69b974） | **接受遗留** | **建议 ready 前顺手刷新**（三处各一行） |
| P2-09 | 交付表 `:75` 未写 §3 逐码表 | **接受遗留** | 实现期一行补充 |

### 2.6 是否仍有 P0/P1

- **P0 = 0**：r4 的 Region 冻结不变式冲突已由收窄解除，v5.2 未回退。
- **P1 = 0**：r6 的 3 条 P1 全部关闭且经独立复核属实。
- 因此按约定结论为 **approved**。

---

## 3. Findings

**无 P0；无 P1。** P2 共 9 条，全部为「接受遗留」，明细与处置时机见 §2.5（沿用 r6 编号 R6-P2-01…R6-P2-09，其中 P2-08 新增 `base_commit` 一处）。

---

## 4. 结论与建议

1. **approved**：范围冻结文本可执行、可机械验证、与上游先例与治理规则一致；无遗留 P0/P1。
2. **置 `ready` 前建议顺手做两件非阻断事**（不构成再次复核条件）：①刷新卡内元数据（`:14` `base_commit: 7346c8efc`、`:53` 章节「v5」、`:134` Closeout 补 v5.1/v5.2 与「待 r7 复核」）；②`:93` 的「已登记」改为「待 DSH 建卡」或实际登记 `FEA-05-PORT-1`。
3. 其余 P2 按 §2.5 的时机归属处理；实现期需特别自检 P2-01（§8 段落措辞与 Core 路由名）与 P2-07（wire 字段细节），二者最易在契约文档 §1/§2 与实现之间产生歧义。
4. 本卡置 `ready` 后即可按 DSH 分派进入实现（suggested_owner: codex）；实现完成后由**新派独立上下文**复核（本席位不参与实现，可在实现后继续以只读形式复核实现证据）。

## 5. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的契约/代码/测试事实与治理指针），**不构成实现验收**，也不构成契约、设计或架构批准。结论仅指该范围文本是否可执行、可机械验证、与上游先例和治理规则一致。

本席位（`fea05-wire-scope-reviewer`，r1→…→r7 同一席位续任）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、契约、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内行号基于 `be9265b34` 实测；标注「未验证」的项（931/0/60 是否仍成立、契约落盘后测试是否真通过）不得当作已核实事实引用。
