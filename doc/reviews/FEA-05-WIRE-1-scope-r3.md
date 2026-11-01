---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 7122d5696
reviewed_head: a62d9ca10
decision: changes_requested
counts: { P0: 0, P1: 2, P2: 9 }
---

# FEA-05-WIRE-1 范围复核 r3（同一独立席位续任）

| 字段 | 值 |
|---|---|
| base_commit | `7122d56960127aa0480a03c8c462f5718ca6560c`（r2 的 reviewed_head；范围 v3 的父提交） |
| reviewed_head | `a62d9ca10b6aa53f9efcbefa5433fc37c87cae27`（`docs(fea-05-wire-1): 范围 v3…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（**v3**，130 行；status=proposed） |
| 与 r2 的 diff | `git diff --stat 7122d5696..a62d9ca10` → 本卡 91+/37−；`doc/reviews/FEA-05-WIRE-1-scope-r2.md` 入库。**未新增契约文件、未改 `V11R_COMMAND_CONTRACT_V1.md`**（二者是卡内交付物，见 §0） |
| reviewer | `fea05-wire-scope-reviewer`（r1→r2→r3 同一席位续任） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与该卡起草/实现/返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | 仅范围冻结文本（AC1–AC7、命令清册与映射、契约登记格式、写域、裁决点、治理三绿）；不含实现审查 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 2 / P2 = 9（共 11）** |

> **一句话理由**：r2 的 P1-01（契约登记格式）、P1-04（CoreClient registry/parity）、P1-05（写域）**已实质关闭**；§8 下划线行模板经解析器规则逐条核对可解析，C078–C083 与 C001–C066 无冲突，写域无遗漏。**剩余 2 条 P1 都落在「命令语义」上**：①卡 `:62-69` 的「命令清册与映射（冻结）」表 **6 行里 5 行与真实服务签名不符**（缺 `session_id`、`EditToken` 只写 `token_id`、`prepare_candidate` 写成只吃 `draft_id`、`open_draft` 的 `target` 含 book/chapter），AC2「handler 只调用上表真实方法」按现表不可满足；②W-4 与契约文档要求仍漏 `category`/`retryable` 与新 wire 码映射，且未规定 `EditToken` 必须整对象透传（只传 `token_id` 无法通过 `_token_from_json`）。两者改卡文本即可关闭。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**（在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- **未执行**：`dotnet build`/`dotnet test`、`python -m pytest`、UI 真机。931/0/60 在当前 head **未验证**（引用链：`doc/handoffs/FEA-04-68c72ba57.md:184`、`verification/FEA-04/build-test-raw.log`、`doc/reviews/FEA-04-r3.md:21`）。
- **两项契约交付物当前不存在（符合范围卡语义）**：`doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md` **ABSENT**；`V11R_COMMAND_CONTRACT_V1.md` §8 **无 C078–C083 行**（`git grep C078 -- doc` 仅命中 r1/r2 报告）。二者是本卡交付物（写域已含），属实现期产物，不构成 r3 阻断；但意味着 AC1 的「落盘」只能在实现复核验证。
- 已执行（只读）：

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `a62d9ca10…` / 空（clean） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；STATUS 达预算 80%（3124 bytes / 45 lines） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0** |
| 解析器规则核对（纯读，不写盘） | §8 行模板按 `CommandContractV11RTests.cs:223-266` 的分列规则模拟：`cells[1]="C078"` ✓、`cells[2]="drafts_open"` 匹配 `^[a-z][a-z0-9_]*$` ✓、`cells[^2]="PENDING(FEA-05-WIRE-1)"` 以 PENDING 开头 ✓ |

**三绿：是**（但三绿是现状检查；本卡的契约文档与 §8 行尚未落盘，见上）。

---

## 1. r2 逐项 disposition（P0=0 / P1=5 / P2=8）

| r2 ID | 级别 | v3 状态 | 复核证据 |
|---|---|---|---|
| R2-P1-01 契约登记格式 | P1 | **CLOSED（主体）** | 新增独立契约文档入写域（卡 `:24`）+ 交付范围 `:77`；§8 指针行模板 `:78`（6 格、名称第 3 格、状态末格、`PENDING(FEA-05-WIRE-1)`）；下划线命名规则 `:53`、`:71`；「手工追加、不重跑生成器」`:78` ✓。残留：§8 heading/总数/§10 变更记录、契约文档自身状态/版本纪律 → R3-P2-01/02 |
| R2-P1-02 方法名/映射 | P1 | **OPEN（未修好）** | `:54` 声称「按真实服务方法映射（见下表）」，但 `:64-69` 表 6 行中 5 行与真实签名不符（见 R3-P1-01）；`:66` 甚至写「（或 `prepare_candidates`，按服务现有签名）」——把冻结推迟到实现期 |
| R2-P1-03 payload/result/错误码映射 | P1 | **PARTIAL** | 契约文档要求含「请求/响应外形、错误码」（`:77`）✓；但 W-4 `:106` 仍是「code/message/details」（漏 `category`/`retryable`），未要求逐码映射，未规定 `EditToken` 整对象透传 → R3-P1-02 |
| R2-P1-04 CoreClient registry/parity | P1 | **CLOSED（主体）** | `:55`、`:80`、AC3 `:87` 明确 `HostCommandRegistry`（域 `Drafts`/通道 `core`/minor 3）、`HostCommandDispatcher` 路由、`V11RAdditiveCommandNames` 同步、`CommandParityContractTests` 三项断言 ✓。残留：`V11RAdditiveCommandNames` 属性语义与「不许弱化断言」→ R3-P2-03/P2-09 |
| R2-P1-05 模板两节/写域/断言红线 | P1 | **PARTIAL** | 写域修好：`src/application/editing/**` 已移除（`:22-35`）、`tests/domain/**` 已加（`:28`）、禁止范围 `:96` 回写 ✓。但「允许修改范围 / 依赖、风险与阻塞」两节仍未加，且处置表 `:56` 把「模板两节缺失」错记为 r2-P1-03（实为 r2-P1-05）→ R3-P2-05/P2-09 |
| R2-P2-01 `tests/domain` 写域 | P2 | **CLOSED** | `:28` ✓ |
| R2-P2-02 AC6 脚本路径 | P2 | **CLOSED（近似）** | 错误的 `tools/governance/…` 已消失；现为裸名 `generate_api_inventory.py`（`:90`、`:116`），建议补全 `tools/` 前缀 |
| R2-P2-03 W-2 指 FEA-06 | P2 | **CLOSED** | W-2 `:104` 改为「否（只到 CoreClient 命令面）」，不再提 FEA-06 ✓ |
| R2-P2-04 FEA-05-PORT-1 登记 | P2 | **OPEN** | 仍只在本卡 `:51` 提及，DAG/LEDGER 无节点 → R3-P2-06 |
| R2-P2-05 生成器/维护归属 | P2 | **PARTIAL** | 「手工追加、不重跑生成器」已写（`:78`）✓；master §10 变更记录与「维护归属」仍无 → R3-P2-01 |
| R2-P2-06 L-2 解除记录 | P2 | **OPEN** | 来源链 `:40-44` 仍无 L-2 记录 → R3-P2-05 |
| R2-P2-07 STATUS 预算/陈旧 LEDGER 计数 | P2 | **OPEN** | 未处置（本轮 check.ps1 仍报 STATUS 3124/45）；`doc/STATUS.md:19` 仍 483=471+11+1（现 491/480/10）→ R3-P2-07 |
| R2-P2-08 工作量/kill-criteria/worktree | P2 | **OPEN** | `:126` 仍「无 worktree」；无 kill-criteria → R3-P2-08 |

**统计（13 项）**：**CLOSED 5**（R2-P1-01、R2-P1-04、R2-P2-01、R2-P2-02、R2-P2-03）／**PARTIAL 3**（R2-P1-03、R2-P1-05、R2-P2-05）／**OPEN 5**（R2-P1-02、R2-P2-04、R2-P2-06、R2-P2-07、R2-P2-08）。

---

## 2. 逐项核查（对应 Lead 的 7 问）

### 2.1 命令名下划线是否满足 §8 解析器正则 —— **满足**

- 解析器只识别「标题以 `## 8.` 开头」的节下、`C 编号 > 66` 的行（`CommandContractV11RTests.cs:260-266`）；命令名取 `cells[2]` 并过正则 `^[a-z][a-z0-9_]*$`（`:199-202`）；状态取 `cells[^2]` 并要求 `StartsWith("PENDING")`（`:264`、`:92-93`）。
- 卡 `:78` 的模板行：`| C078 | \`drafts_open\` | Drafts | core | 3（zero protocol bump） | \`PENDING(FEA-05-WIRE-1)\` |` → 拆分后 `cells[1]=C078`（`^C\d{3}$` ✓）、`cells[2]=drafts_open`（下划线 ✓、正则 ✓）、`cells[^2]=PENDING(FEA-05-WIRE-1)`（✓）。**6 条下划线名（`drafts_open`/`patch`/`prepare`/`apply`/`status`/`discard`）全部可通过**。
- 前提提醒（未写进卡）：行必须落在 `## 8.` 节内且在 `## 9.` 之前；若另起 `### 8.1` 子节，行会被完全忽略（`:216-221` 的 section 赋值），AC1 会红。

### 2.2 C078–C083 是否与已冻结 C001–C066 冲突 —— **不冲突**

- §4 baseline 恰 C001–C066（`CommandContractV11RTests.cs:31-49` 断言 66 行）；§8 现有 C067–C077（`V11R_COMMAND_CONTRACT_V1.md:229-239`）；C078–C083 为下一个空段，全仓 `git grep C078` 只命中本卡评审记录，无其他占用。
- 追加 C078–C083 不会改变 baseline 行数（解析器对 `index<=66` 且 `### 4.` 才计入 baseline），也不会影响 `PendingRows` 既有条目。

### 2.3 AC1–AC7 可验收性

| AC | 判定 | 依据 |
|---|---|---|
| AC1 契约 + §8（`:85`） | **可验收（偏弱）** | 6 条可解析 ✓、下划线 ✓、PENDING ✓、不在冻结集合 ✓；但 AC1 只验「落盘 + 测试」，**不验契约文档内容**（是否真含 6 条逐命令请求/响应/错误码）→ R3-P2-02 |
| AC2 语义不变（`:86`） | **不可验收** | 引用的映射表 `:64-69` 与真实签名不符（R3-P1-01），「只调用上表真实方法」按现表无法满足；`drafts_status` 仍「二选一按 payload」，返回形状未定 |
| AC3 CoreClient（`:87`） | **可验收** | 三项断言与 `CommandParityContractTests.cs:88-91`/`:109-119`/`:140-144` 一致；`HostCommandRegistry` 需加 `Drafts` 枚举成员 + `AddDomain` + 6 条（`HostCommandRegistry.cs:257-265`、`:320-345`），均在本卡写域 |
| AC4 Python 测试（`:88`） | **可验收** | `tests/core/**`、`tests/domain/**` 在写域；`pytest.ini:2` + `tests/core/conftest.py` 支持该命令 |
| AC5 回归（`:89`） | **可验收（形式回退）** | `dotnet test ... --no-build --settings .../NewManga.runsettings` 用省略号缩写（v2 曾是完整命令）→ R3-P2-04 |
| AC6 治理（`:90`） | **可验收** | 本轮三绿实测 ✓ |
| AC7 证据（`:91`） | **可验收** | `evidence_dir` 在写域 ✓ |

**6/7 可验收，AC2 需改表。**

### 2.4 写域（遗漏 / 过度）

- **无遗漏**：新增契约文档（`:24`）与 master 契约（`:25`）已入域；`src/bootstrap/core_service.py` 足够（族集合/dispatch/6 handler/`CoreServiceServer.__init__` `:1032-1052`/`main()` 注入 `:5804-5814` 全在该文件；`CoreServices.drafts` 由 `core_assembly.py:760/1310-1316` 提供）；`tests/core/**`、`tests/domain/**` ✓；CoreClient 与其测试 ✓；端口三文件已不在域 ✓。
- **略过度（可接受/可收窄）**：`NewManga.CoreClient/**` 全库开放（本卡只需 registry/dispatcher/model 三处）；`tests/domain/**` 全开放（本卡大概率不需改 domain 测试，可收窄为「只读或不需」）；`tests/core/**` 全开放（可接受，基准先例同）。
- **不需要的**：本卡不再触任何受 pin 文件（`verify_pins.ps1:6-13` 不含新契约文档与 master 契约）✓；`doc/00_INDEX.md` 无需更新（该索引未逐份列 `doc/contracts/**`，先例 `V11R_REGION_WRITE_CONTRACT.md` 也不在列）。

### 2.5 契约登记格式与既有条目一致性

- **§8 行格式：一致** ✓（与 `V11R_COMMAND_CONTRACT_V1.md:229` 的 `| C067 | \`create_region\` | Region | core | 3（zero protocol bump，Lead 裁定） | \`PENDING(V11R-F0-1)\` |` 同形；只是本条补了作者标识 `FEA-05-WIRE-1`）。
- **per-command 契约：一致** ✓（先例 `V11R_REGION_WRITE_CONTRACT.md:155-283` 是独立文档 + §8 指针行；本卡 `:50`、`:77`、W-5 `:107` 同法）。
- **未随更新的文档一致性（P2）**：§8 heading `:220` 仍「C067–C077」、`:222-223` 总数仍「76/77」、`:241-242` 约束段只写 C067–C077、§10 变更记录（`:495-499`）未预算本卡条目；卡未要求这些。
- **契约文档自身规格（P2）**：Region 先例有 `状态：FROZEN（日期）/ 任务卡 / 上游 / 实现 / 命令清册编号` 头（`V11R_REGION_WRITE_CONTRACT.md:1-9`）与 §9 变更记录；卡 `:77` 未要求本卡契约文档的状态/版本/变更记录，而 W-5 `:107` 只说「DSH 复核后冻结」。

### 2.6 是否仍需用户 / DSH 裁决点

- **无需用户裁决**（无产品取舍项）。
- **需 DSH 裁决 3 项**（建议在改卡时一并落盘）：①`V11RAdditiveCommandNames` 是否并入 Drafts（该属性 docstring 明写是「V11R-F0-1 + F0-2」集合，`HostCommandRegistry.cs:305-313`）——并入会让属性名与实际不符，建议新增 `DraftCommandNames` 并改断言为「注册表新增集 = 各 additive 集之并」；②契约文档冻结流程（W-5 仅一句话，需定「文档状态行 + DSH 复核 + 冻结记录」的最小流程）；③`flush(trigger)` / session 结束是否本卡出（C-13 SC-D02 强制 flush 点；本卡未提；建议至少登记 deferral 与承接卡）。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R3-P1-01** | P1 | 卡 `:62-69`（命令清册「冻结」表）、`:54`、`:86`（AC2）；真实签名：`drafts.py:97-105`、`:151`、`:158`、`:165-168`、`:215`、`:286-302`、`:304-312`、`:374-377`；`entities.py:140-152`；`drafts.py:755-773` | **「冻结」的 6 行映射中 5 行与真实签名不符，AC2 不可满足：** ①`drafts_open`：真实为 `open_draft(session_id, page_id, region_id, *, base_revision_id, page_binding_version)`——表里 `target(page/book/chapter/page)` 把 book/chapter 写进草稿作用域（草稿按 `(page_id, region_id)` 定位，`_target_key`），且漏 `base_revision_id`；②`drafts_patch`：真实 `patch_draft(draft_id, session_id, patch, *, undo_cursor, schedule_flush)`——漏 `session_id`（owner 校验必需）、`patches[]` 与单 `patch` 映射不符；③`drafts_prepare`：真实 `prepare_candidate(region_id, patch, *, origin, draft_id=None, base_revision_id=None)`——**不存在只吃 `draft_id` 的方法**，且行内自认「或 `prepare_candidates`，按服务现有签名」（把冻结推迟到实现期）；④`drafts_apply`：真实 `apply_candidates(token: EditToken\|Mapping, candidate_ids)`——`token_id` 无法重建 token（`_token_from_json` 要求 `tokenId/DraftId/DraftSequence/SessionId/issuedAt/expiresAt` 六字段逐字匹配，且 `issued != edit_token` 做整对象相等），`draft_ids` 应为 `candidate_ids`；⑤`drafts_discard`：真实 `discard_draft(draft_id, session_id)`——漏 `session_id`；⑥`drafts_status` 仍「二选一按 payload」，返回形状（单 Draft vs 列表）未定 | 按真实签名重写映射表六行（含「命令 → 方法 → 请求字段 → 结果字段」四列）；`drafts_status` 定为单一语义（建议 `payload.draft_id` → 单草稿；`payload.session_id` → 列表，**两分支结果外形在契约文档中分别冻结**）；明确 `drafts_open` 结果为 `DraftLease{draft, created, token}`（`drafts.py:148-149`），`drafts_apply` 请求为 `{token:<EditToken 六字段>, candidate_ids:[…]}` |
| **R3-P1-02** | P1 | 卡 `:77`（契约文档交付）、`:86`（AC2）、`:106`（W-4）、`:85`（AC1）；`make_error_envelope`（`core_service.py:808-825`）；`drafts.py:755-773`、`:389-407` | **错误语义与 token 传输仍未冻结：** ①W-4 仍写「复用既有错误结构（code/message/details）」，漏 `category`/`retryable`（信封实际含这两个字段，r2 已提仍未改）；②14 个新 wire 码（`DRAFT_*`/`EDIT_TOKEN_*`/`STALE_BASE_REVISION` 等）无逐码 `{category, retryable, details}` 映射要求；③未规定 `drafts_open` 返回的 `EditToken` 必须**整对象原样回传**（只传 `token_id` 会 `EDIT_TOKEN_INVALID`，见 R3-P1-01④）；④未要求 receipt 重放（`EDIT_TOKEN_REUSED` 原样透传 `revisionIds`，`drafts.py:389-407`）的语义与测试项；⑤AC1 只验「文档落盘」，不校验文档内容 | W-4 补 `category`/`retryable`；契约文档 `:77` 增加必需内容清单：六条命令的 request/result 字段、14 码映射表、`EditToken` 六字段传输、receipt 重放、`cause_code` 不外泄；AC1 增加一条可机械核验的「契约文档包含 6 条逐命令小节 + 错误码映射表」（如 grep 断言或 DSH 复核签字行） |
| **R3-P2-01** | P2 | 卡 `:78`；`V11R_COMMAND_CONTRACT_V1.md:220-223`、`:241-242`、`:495-499`；`build_contract_doc.py:459-480` | §8 指针行只加行、未更新同节文本：heading 仍「C067–C077」、总数仍「66→76/77」、约束段仍只写 C067–C077、§10 变更记录无本卡条目；生成器漂移（未来重跑会抹掉 C078–C083）已由「手工追加」部分覆盖，但无 §10 记录 | 交付范围补一行：同步更新 §8 heading/总数/约束段 + §10 增一行「FEA-05-WIRE-1 手工追加 C078–C083（不重跑生成器）」 |
| **R3-P2-02** | P2 | 卡 `:77`、`:85`（AC1）、W-5 `:107`；先例 `V11R_REGION_WRITE_CONTRACT.md:1-9`、`:485-499` | 新契约文档缺少自身的「状态/版本/任务卡/上游/实现位置/变更记录」头与冻结流程；AC1 不验内容（见 R3-P1-02⑤） | 按 Region 契约头部补规格：`状态：DRAFT→（DSH 复核后）FROZEN + 日期`、任务卡、上游、实现位置指针、§变更记录；AC1 加内容核验 |
| **R3-P2-03** | P2 | 卡 `:55`、`:81`（`V11RAdditiveCommandNames` 同步）；`HostCommandRegistry.cs:279-313`；`CommandParityContractTests.cs:88-91` | 「同步 `V11RAdditiveCommandNames`」未裁语义：该属性 docstring 明写「V11R-F0-1 + F0-2」的并集；把 Drafts 并入会让名字与实际不符，另建集合则测试断言（`Assert.Equal(V11RAdditiveCommandNames, additive)`）需改 | DSH 裁：新增 `DraftCommandNames` 并把断言改为「additive = 各集合并」，或并入现有属性并同步改 docstring；卡内写死选择 |
| **R3-P2-04** | P2 | 卡 `:89`（AC5）、`:115`（测试要求） | AC5 用省略号缩写（`dotnet test ... --no-build --settings .../NewManga.runsettings`），相对 v2 的完整命令是回退；FEA-04 r2 P1-02 的教训即「命令须为冻结形式」 | 恢复完整命令串（`apps/desktop-avalonia/NewManga.sln` + `apps/desktop-avalonia/tests/NewManga.runsettings`） |
| **R3-P2-05** | P2 | 卡 `:40-44`（来源链）；`FEA-03.md:153` L-2；`FEA-04.md:99` L-2 | L-2 解除记录仍缺：上游要求「透传 Draft/新增命令 → blocked，先完成 M2-C1」；本卡改走 V11R 命令契约（F0-1 先例，M2-C1 未随 F0-1 更新），但卡未记录该判定，阻塞解除在证据上不可核。另：建议按 FEA-03/FEA-04 先例加「L 前置适用性判定」小节（非模板硬性要求，但当前已收口卡均有） | 加一行：「L-2 解除依据：F0-1 先例（命令族以 `V11R_COMMAND_CONTRACT_V1` §8 + 独立契约文档承载；M2-C1 不逐族追加）；FEA-05 同法」 |
| **R3-P2-06** | P2 | 卡 `:51`；`REBASELINE_PLAN.md`、`TASK_LEDGER.md` | `FEA-05-PORT-1` 承载 IHostController 端口面 + C-07 UNFREEZE，但仍只存在于本卡文本；DAG/LEDGER 无该节点 | DSH 在 PLAN 记「候选（未释放）」或卡内注「待建卡」 |
| **R3-P2-07** | P2 | 卡 `:32-34`；`check.ps1:614-621`；`doc/STATUS.md:19`；`TASK_LEDGER.md:9-13` | r2-P2-07 未处置：STATUS 45/45 行、3124/3200 bytes（任何新增行触发预算报错）；STATUS `:19` 的 LEDGER 计数（483=471+11+1）与现行 491/480/10 不符 | 卡内加前置「STATUS 须同批压缩」；顺手刷新 `:19` |
| **R3-P2-08** | P2 | 卡 `:73-81`、`:126`；C-13 SC-D02（`FEA-C13_DRAFT_PROTECTION_DRAFT.md:47-54`）；`drafts.py:576-589` | ①无 kill-criteria（如「契约文档/映射表未定则不得开工」）；②`:126` 仍「无 worktree」，未给理由（FEA-03/04 先例均用 worktree）；③`force_flush(trigger)`/`flush_pending` 与 session 结束的 wire 面（C-13 强制 flush 点）未出也未登记 deferral | 补 kill-criteria + worktree 决策一句；登记 flush 的 deferral 与承接卡（或在契约文档 §非目标 写明） |
| **R3-P2-09** | P2 | 卡 `:56`、`:58`（处置表）；`:93-97`（禁止范围） | ①处置表把「模板两节缺失」错记为 `r2-P1-03`（实为 r2-P1-05）、把 `r2-P1-05` 只记成写域一条，导致「允许修改范围/依赖风险阻塞」的诉求被静默丢弃（虽经判定：已收口卡 FEA-03/04 也未用该模板节名，**不构成 P1**，但错记须修）；②全卡无「不得弱化/删除既有契约对照断言（只允许新增）」红线，而 `CommandParityContractTests`/`CommandContractV11RTests` 在写域内 | 修正处置表 ID 映射；禁止范围加一句断言红线 |

---

## 4. 处置建议（最小成本）

1. **先修 R3-P1-01 映射表**（唯一实质规格缺陷）：按 `drafts.py` 真实签名重写六行，并把 `drafts_status` 的两分支结果外形写进契约文档；顺带把 `drafts_open` 结果定义为 `DraftLease{draft, created, token}`、`drafts_apply` 请求定义为 `{token:<EditToken 六字段>, candidate_ids}`。
2. **R3-P1-02**：W-4 补 `category`/`retryable`；契约文档必需内容清单 + AC1 内容核验。
3. P2 批量顺手：§8 文档一致性（R3-P2-01）、契约文档头部/冻结流程（02）、`V11RAdditiveCommandNames` 裁决（03）、AC5 完整命令（04）、L-2 记录（05）、PORT-1 登记（06）、STATUS 预算/陈旧计数（07）、kill-criteria/worktree/flush deferral（08）、处置表错记 + 断言红线（09）。
4. 改卡后派 **r4** 复核；P0/P1 = 0 才置 `ready`。

## 5. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的契约/代码/测试事实与治理指针），**不构成实现验收**，也不构成契约、设计或架构批准。结论仅指该范围文本是否可执行、可机械验证、与上游先例和治理规则一致。

本席位（`fea05-wire-scope-reviewer`，r1→r2→r3 同一席位续任）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、契约、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内行号基于 `a62d9ca10` 实测；标注「未验证」的项（931/0/60 是否仍成立、§8 行落盘后测试是否真通过）不得当作已核实事实引用。
