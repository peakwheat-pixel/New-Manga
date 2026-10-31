---
document_id: FEA-GOV-10-r2
kind: independent_review
task_id: FEA-GOV-10
round: 2
scope: very-narrow（只核 r1 的 1×P1 + 4×P2 处置、脚本可执行性、check.ps1 与是否引入新问题）
reviewer: c01b-reviewer
reviewer_kind: subagent
reviewer_source: "Agent Teams durable teammate（task-23；独立上下文；未参与清单/脚本撰写）"
reviewer_independent: true
reviewed_by_implementer: false
predecessor: FEA-GOV-10-review（r1：changes_requested，P0×0 / P1×1 / P2×4）
reviewed_head: c7d4524b9
reviewed_head_full: c7d4524b998cd8de78126fcc789e0486fa03279c
reviewed_head_note: "复核期间 HEAD 未前进（HEAD == reviewed_head == c7d4524b9）"
reviewed_documents:
  - doc/plan/FEA-C07_API_INVENTORY.md
  - tools/generate_api_inventory.py
reviewed_sha256:
  doc/plan/FEA-C07_API_INVENTORY.md: 3802f01a9ab2486cb7d2b2abcf65ebd98ca087f57bc0752a5e0546c289b3fb73
  tools/generate_api_inventory.py: f6508cdee80d0da894d00bfa90a222b7f518147af53446c6926d2f7674f2aaac
reviewed_sha256_basis: "HEAD 的 LF blob（清单 99 行、脚本 177 行；由 c7d4524b9 引入/更新）"
baseline: "apps/desktop-avalonia/src/NewManga.App/Services/{IHostController.cs,RunContracts.cs} · doc/plan/V11R_AVALONIA_CONTRACT.md §5 `:239` · doc/plan/FEA-01_CONTRACT_DRAFT.md C-07 行"
repository: G:/CODEX/New Manga
source_branch: main
verdict: approved
p0_count: 0
p1_count: 0
p2_count: 3
p2_note: "3 条均为非阻断增强项（`--check` 只比计数不验签名、stdout 编码未固定 UTF-8、脚本渲染结构与文档不一致），登记为 K-1/K-2/K-3"
checkps1: "PASS（3 warnings），EXIT=0，本次实跑"
captured_at: 2026-11-01T04:45:26+08:00
captured_by: c01b-reviewer
---

# 独立复核 r2（极窄面）：FEA-C07 API Inventory 处置确认

**本报告不是** 冻结动作、不释放任何 Task，也不构成执行授权。本轮只核 r1 的 1×P1 + 4×P2 是否处置到位、脚本是否真的可跑且解析正确、`check.ps1` 是否 PASS、以及是否引入新问题。

## 1. 结论

**verdict：`approved`（P0 × 0 / P1 × 0 / P2 × 3 非阻断）。**

r1 的 **1 条 P1 与 4 条 P2 全部闭环**，我亲手运行脚本实测：

| # | 项 | 结果 |
|---|---|---|
| 1 | **P1-1**：`tools/generate_api_inventory.py` 入库 + 解析出 54 + `--check` OK + 文档改引脚本/命令 | **✅**（实跑：`IReaderProgressSink 1 / IHostController 47 / IRunController 6`，合计 **54**，`--check` 输出 `OK: rendered counts match FEA-C07 doc`，EXIT=0） |
| 2 | **P2-1**：加「变更类别」说明（36 基线 + 11 新增；additive） | **✅**（`:24` 新增段落；逐成员映射按 `:24` 声明由实现 Task 落地时补） |
| 3 | **P2-2**：表头注明「参数以代码为权威，本文档不列」 | **✅**（三张表 `:28`/`:34`/`:86` 均已注明） |
| 4 | **P2-3**：统计表列出 4 个非方法成员 | **✅**（`:22` 合计行动列 `HostViewSnapshot Snapshot`、`event EventHandler? Changed`、`int StartRequests`、`string ExportDirectorySuggestion`） |
| 5 | **P2-4**：`:11` 改为「`IHostController` 方法数基线 36」，与 57 命令数区分 | **✅**（`36` 方法基线 / `47` 实测（含 11 新增）/ `57` 命令数，三者并列且互不替代） |
| 6 | 新问题 + `check.ps1` | 3 条非阻断增强项（K-1/K-2/K-3，均不影响 54/签名正确性）；**`check.ps1` PASS(3 warnings) EXIT=0**；未 push |

脚本在本机实测（Python 3.14.6）解析 **54/54 正确**，含 4 个属性/事件（`IHostController` 的「属性/事件/字段数 = 4」）；源码无 BOM、CRLF 行尾下解析正常（无漏成员、无串行）。

---

## 2. 5 处核对明细

### 1（P1-1）生成脚本入库并可用 —— ✅

- `tools/generate_api_inventory.py`（177 行）存在且被 `c7d4524b9` 入库（+177 行）。
- **实跑 `python tools/generate_api_inventory.py --check`**：stdout 渲染三接口统计为 `IReaderProgressSink 1 | IHostController 47 | IRunController 6`，合计 **54**；stderr `OK: rendered counts match FEA-C07 doc`；EXIT=0 ✓。
- **独立核对**：脚本对 `IHostController` 报「属性/事件/字段数 = 4」，与 r1 我手工发现的 4 个非方法成员吻合 ✓；源码 `IHostController.cs`/`RunContracts.cs` 均为无 BOM + CRLF（`CR=423`/`612`），脚本仍解析出 47/6/1 → CRLF 不是问题 ✓。
- 文档已改引：`:5`「生成方式：`python tools/generate_api_inventory.py`（…）；重跑同一命令应得到同一集合」；`:97`「冻结时以本文件 + `tools/generate_api_inventory.py` 的输出为准」；`:98`「反复运行 `python tools/generate_api_inventory.py --check`…（`--check` 会对比本文档的计数行）」✓。

### 2（P2-1）变更类别 —— ✅

- `:24`：「**变更类别**：`IHostController` 的 47 个中，**36 个为 V11R §5 `:239` 基线**（签名不得变），**11 个为 FEA 期间新增**（additive；冻结后同样只允许追加）。逐成员的新增/基线标注由实现 Task 在该行落地时补（本文档暂不逐行标）」✓ 与 V11R §5 `:239`（36 方法保持原签名、新增只允许追加）一致；47−36=11 算术成立。

### 3（P2-2）参数口径 —— ✅

- 三张成员表表头均为「返回类型（**参数以代码为权威，本文档不列**）」（`:28`、`:34`、`:86`）✓。

### 4（P2-3）非方法成员 —— ✅

- `:22`：「**合计** | **54**（另有 4 个非方法成员：`HostViewSnapshot Snapshot`、`event EventHandler? Changed`、`int StartRequests`、`string ExportDirectorySuggestion`，均属 `IHostController`）」✓ 与脚本实测「属性/事件/字段数 = 4」一致。

### 5（P2-4）36/57 口径 —— ✅

- `:11`：「**`IHostController` 方法数基线 36**（V11R §5 `:239`）与 **本清单实测 47**（含 11 个新增）是两个不同口径；「命令契约数」（冻结文档的 57）是第三种计数——三者不得互相替代」✓ 不再把 36 说成命令数。

---

## 3. 新问题（3 条非阻断 P2）

#### K-1 — `--check` 只比计数，不验成员/返回类型；`:98`「得到同一集合」措辞偏强

- 位置：脚本 `:159-172`（`--check` 分支）与文档 `:98`。
- 事实：`--check` 只对 3 个接口各查一次 `"| {name} | {n} |"` 是否出现在文档中（`:167`），**不比对成员名/返回类型**；文档 `:98` 写「反复运行 `--check` **得到同一集合**」——该表述超出实际检查能力（改名或改返回类型而计数不变时 `--check` 仍 OK）。
- 建议（二选一）：① 扩展 `--check` 为「完整渲染输出 vs 文档成员表」比对；② 把 `:98` 改为「校验**计数**一致；完整签名以 stdout 全文 diff 为准」（括号内已近似如此，前句需改）。
- 影响：非阻断；当前 stdout 全文（80 行）可 diff，能发现改名/改型。

#### K-2 — 脚本 stdout 编码未固定 UTF-8（Windows 本地实测为 GBK）

- 位置：脚本 `:157`（`print(rendered)`）与全脚本（无 `reconfigure`）。
- 事实：本机（Windows / Python 3.14.6）把 stdout 重定向到文件后，实测 **3918 字节、非 ASCII 106 字节、按 UTF-8 解码为乱码**（即输出为 cp936/GBK）；无 BOM。文档是 UTF-8，若用重定向输出直接生成/比对文档会因编码不同而不稳定。
- 建议：`sys.stdout.reconfigure(encoding="utf-8")`（或 `PYTHONUTF8=1` / `-X utf8`），并在文档注明「输出按 UTF-8 保存」。
- 影响：非阻断（`--check` 只比 ASCII 计数，不受影响；但「重跑得到同一集合」的落盘比对会受影响）。

#### K-3 — 脚本渲染结构与文档结构不一致

- 位置：脚本 `:125-147`（render）vs 文档 `:17-22`、`:28`/`:34`/`:86`。
- 事实：脚本统计表是「接口 | 方法数 | 属性/事件/字段数」，成员表表头「# | 成员 | 返回类型」，且把 4 个非方法成员作为 `—` 行输出；文档统计表是「接口 | 成员数」（2 列），成员表表头「# | 方法 | 返回类型（参数…）」，4 个非方法成员并入合计行动。文档 `:97` 说「以本文件 + 脚本的输出为准」——两者结构不同，需说明关系。
- 建议：明确「文档 = 脚本输出的人工整理版（差异仅在表头措辞与非方法成员的呈现方式）」，或让文档直接由脚本输出生成。

---

## 4. 数据安全与治理

- **`check.ps1` 实跑**：`Governance check: PASS (3 warnings)`，EXIT=0（warning 既有：7 非终态 Task、`STATUS.md` 2891 B / 31 行、`REBASELINE_PLAN.md` 6549 B / 57 行）；运行后 `git status` 为空 ✓。
- **提交面**：`c7d4524b9` 只改清单（+10/−8）、r1 报告（+133）与新增脚本（+177）；`git diff --stat 60b2b4e2b..HEAD -- src apps` 为空（除 Services 未动）✓；**未 push**（`origin/main..HEAD` = 188 提交）✓。
- 被审字节：清单 @ `c7d4524b9` `3802f01a…`（99 行）、脚本 `f6508cde…`（177 行）；本次运行脚本只读（无写入，`git status` 仍空）。

---

## 5. 独立性声明

- 我以 `c01b-reviewer`（Agent Teams **durable teammate**）身份出具 r2，`reviewer_kind: subagent`，独立上下文；r1 亦由我出具（如实披露）。
- **未参与**清单与脚本撰写（作者 = DSH）、未参与 C-07 / V11R / FEA-01 撰写，未参与 `apps/**`、`src/**` 任何实现。
- 本轮**只读**：唯一写入为新建本报告；未修改任何文件；未 `git add`/`commit`/`push`；未触碰真实数据根。执行的命令为只读 `check.ps1`、`python tools/generate_api_inventory.py [--check]`（脚本只读源码、只打印，无写操作；运行前后 `git status` 一致）与只读取证。
- 5 处判定直接对照脚本/文档/源码原文；K-2 的编码结论来自「重定向到 `%TEMP%` 后按字节检查」（3918 B、106 个非 ASCII、UTF-8 解码乱码）。
- **工作树状态记录**：报告落盘前 `git status --porcelain` 为空；`reviewed_head == HEAD == c7d4524b9`。

---

## 6. NOT_RUN

- 未运行 `dotnet build` / `dotnet test` / 任何编译（签名以源码文本为准）。
- 未核 54 个方法的行为语义（只核名称/返回类型/归属/计数）。
- 未核脚本对「极端 C# 语法」的解析鲁棒性（多行属性/表达式体成员/嵌套类型未测；当前两源文件实测正确）。
- 未核 Core 侧命令清册（不在本轮范围）。
- 未核远端历史细节（仅核本地 `origin/main..HEAD` 未 push）。

—— 报告结束（`verdict: approved`，P0×0 / P1×0 / P2×3 非阻断；5 处核实：5 全到位）。
