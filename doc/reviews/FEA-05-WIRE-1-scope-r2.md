---
task_id: FEA-05-WIRE-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 4dfc8abc4
reviewed_head: 7122d5696
decision: changes_requested
counts: { P0: 0, P1: 5, P2: 8 }
---

# FEA-05-WIRE-1 范围复核 r2（同一独立席位续任）

| 字段 | 值 |
|---|---|
| base_commit | `4dfc8abc4b3d9180ff44eda4c943e97c14a2bfec`（r1 的 reviewed_head；范围 v2 的父提交） |
| reviewed_head | `7122d56960127aa0480a03c8c462f5718ca6560c`（`docs(fea-05-wire-1): 范围 v2…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-WIRE-1.md`（**v2**，113 行；status=proposed） |
| 与 r1 的 diff | `git diff --stat 4dfc8abc4..7122d5696` → 本卡 +77/−36；仅两文件（本卡 + r1 报告入库） |
| reviewer | `fea05-wire-scope-reviewer`（r1→r2 同一席位续任） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；未参与该卡起草/实现/返修；只读被审 head |
| 日期 | 2026-11-02 |
| 审查范围 | 仅范围冻结文本（AC1–AC7、写域、W-1…W-4、契约登记格式、依赖顺序、可执行性、治理三绿）；不含实现审查 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 5 / P2 = 8（共 13）** |

> **一句话理由**：r1 的 3 条 P0 **已全部实质关闭**（契约载体入写域、端口面剔除、Python 测试入写域），范围已从「不可执行」变为「可执行但交付面规格不足」。剩余 5 条 P1 集中在**同一个交付物——命令契约登记**：卡要求「追加 6 条命令（名称/payload/result/错误码/版本）且与既有条目同格式」，但既**既没有 per-command 契约文档**（Region 先例是独立 `V11R_REGION_WRITE_CONTRACT.md` + master §8 指针行），也与 `CommandContractV11RTests` 的解析规则（命令名必须匹配 `^[a-z][a-z0-9_]*$`、状态列必须是最后一个数据列且以 `PENDING` 开头、行必须在 `## 8.` 标题下）未对齐；另外卡 `:61` 列出的 5 个 handler 服务方法名中有 4 个在仓库中不存在。这些都不需要新增契约冻结，改卡即可关闭。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**（卡、契约、STATUS、PLAN、LEDGER、源码、测试、`verification/**` 均未改），未 commit/push。**本报告是本轮唯一新增文件**（在被审卡 `allowed_paths` 的 `doc/reviews/FEA-05-WIRE-1-*.md` 内）。
- **未执行**：`dotnet build`/`dotnet test`、`python -m pytest`、任何 UI/真机运行、任何源码写入。「931/0/60 在当前 head 仍成立」**未验证**，仅引用 FEA-04 入库证据（`doc/handoffs/FEA-04-68c72ba57.md:184`、`verification/FEA-04/build-test-raw.log`、`doc/reviews/FEA-04-r3.md:21`）。
- 已执行（只读）：

| 命令 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `7122d5696…` / 空（clean） |
| `git diff --stat 4dfc8abc4..7122d5696` | 本卡 77+/36−；`doc/reviews/FEA-05-WIRE-1-scope-r1.md` 入库；**未触碰** STATUS/PLAN/LEDGER/契约/源码 |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（2 warnings）**：10 个非终态 Task；`doc/STATUS.md` 达预算 80%（3124 bytes / 45 lines） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0**（1/47/6 = 54 与 C-07 一致） |

**三绿结论：是。** 但注意：三绿是「当前 head 的现状检查」，本卡改的 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` 既不在 15 份 pin 内，也不在 `check.ps1` 的静态治理文件集内（14 项，`check.ps1:169-184`；连同当前 Task 共 15 份被扫描文档），故三绿**不能**证明契约登记内容正确（见 §2.3 / R2-P1-01）。

---

## 1. r1 逐项 disposition（P0×3 / P1×5 / P2×6）

| r1 ID | 级别 | v2 状态 | 复核证据 |
|---|---|---|---|
| P0-01 命令面无契约载体 | P0 | **CLOSED（载体层面）** | `allowed_paths` 新增 `doc/contracts/V11R_COMMAND_CONTRACT_V1.md`（卡 `:24`）；交付范围新增「命令契约登记」（`:60`）；AC1 改为「契约登记 + `CommandContractV11RTests` 通过」（`:69`）。**但登记规格仍不足 → R2-P1-01** |
| P0-02 C-07 端口与 AC6 互斥 | P0 | **CLOSED** | 写域已无 `IHostController.cs`/`HostController.cs`/`NullHostController.cs`/`NewManga.App.Tests`（`:22-34`）；交付范围 `:65`「不做：IHostController 端口面」；AC6 `:74`「C-07 端口清单不变 + `generate_api_inventory.py --check` EXIT 0」；本轮实测 EXIT 0 ✓；端口面顺延 `FEA-05-PORT-1`（`:51`，登记问题见 R2-P2-04） |
| P0-03 Python 测试无写域 | P0 | **CLOSED（tests/core）** | `tests/core/**` 入写域（`:27`）；AC4 `:72` 给出 `python -m pytest tests/core tests/domain -q`；`pytest.ini:2` `testpaths = tests`、`tests/core/conftest.py` 存在 → 命令合法。`tests/domain/**` 未入写域 → **R2-P2-01** |
| P1-01 `drafts.close` 二义 | P1 | **PARTIAL（二义已消除，映射仍缺）** | 命令集合改为 6 条并去掉 `close`（`:53`、W-3 `:89`）✓；但 `drafts.status` 映射仍二义（`get_draft(draft_id)` vs `list_drafts(session_id)`），`open/patch/apply` 所需 `session_id`/`page_binding_version`/`EditToken` 未定，且卡 `:61` 的方法名错误 → **R2-P1-02** |
| P1-02 无 payload/result/错误码映射 | P1 | **OPEN** | 卡 `:60` 只写「名称/payload/result/错误码/版本」字段名，无任何值/字段表；W-4 `:90` 仍是「code/message/details」（漏 `category`/`retryable`，与 `make_error_envelope` 不符）→ **R2-P1-03** |
| P1-03 模板两节缺失 + 写域失衡 | P1 | **OPEN** | 仍无「允许修改范围」与「依赖、风险与阻塞」两节（模板 `doc/templates/TASK.md:34-42`、`:50-52`；协作协议 `09_COLLABORATION.md:215` 要求 Scope 含「是否需要共享接口/Schema/依赖变更授权」）；`src/application/editing/**` 仍在写域（`:26`）而禁止范围 `:81` 说不新增编辑规则 → **R2-P1-05** |
| P1-04 W-1 依据与结论相反 | P1 | **CLOSED** | `:54`、W-1 `:87` 改引 `core_service.py:451-457` + `V11R_REGION_WRITE_CONTRACT.md:39-59` ✓（两处引用均经本轮核对：`:451-457` 为「additive Region 写面、同族 minor、零 envelope 语义」注释；`V11R_REGION_WRITE_CONTRACT.md:39-59` 为 §1.1 envelope/minor 裁定）。残留：仍无一句「协议 minor 保持 3」的显式 AC 表述，且 `:54`「故不依赖零 bump」措辞易误读 → 并入 R2-P1-01 |
| P1-05 CoreClient 漏 registry/parity/domain + 无「不许弱化断言」 | P1 | **OPEN** | `:62` 仍只写「`HostCommandModel`/`HostCommandDispatcher` 新增 6 条命令的请求/响应模型」；AC3 `:71` 未变；全卡无 `HostCommandRegistry`/`V11RAdditiveCommandNames`/`HostCommandDomain` 字样；无断言弱化红线 → **R2-P1-04** |
| P2-01 AC5 命令形式 | P2 | **CLOSED** | `:73` 已含 `dotnet build` + `dotnet test … --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings`（与 FEA-04 r3 冻结形式一致） |
| P2-02 STATUS 预算已满 | P2 | **OPEN** | 仍 3124 bytes / 45 lines（预算 3200/45，`check.ps1:614-621`）；卡未提示压缩约束 → R2-P2-07 |
| P2-03 STATUS:19 LEDGER 计数陈旧 | P2 | **OPEN** | `doc/STATUS.md:19` 仍写 `483 = 471 + 11 + 1`；`doc/TASK_LEDGER.md:9-13` 已是 491 files / 480 terminal / 10 non-terminal → R2-P2-07 |
| P2-04 W-2 指向 FEA-06（不在 DAG） | P2 | **OPEN（部分）** | `:51` 新增「本卡不接 UI 即无端口消费方」✓，但 W-2 `:88` 仍写「UI 接线由 FEA-06 或后续卡」；且 `:51` 说「W-2 声明省略」而 W-2 实际保留 → R2-P2-03 |
| P2-05 工作量/拆分与 worktree 说明 | P2 | **OPEN（缓解）** | 端口面剔除后工作量显著下降；但仍无 kill-criteria/worktree 说明（`:109` 仍「无 worktree」）→ R2-P2-08 |
| P2-06 AC6 与禁止范围的 pin 口径不一 | P2 | **CLOSED** | AC6 `:74` 明确「`verify_pins.ps1` 15/15」；本卡不再触任何受 pin 文件（`V11R_COMMAND_CONTRACT_V1.md` 不在 `verify_pins.ps1:6-13` 映射内） |

**统计**：CLOSED 6（P0×3、P1-04、P2-01、P2-06）／PARTIAL 2（P1-01、P2-04）／OPEN 6（P1-02、P1-03、P1-05、P2-02、P2-03、P2-05）。

> **r1 计数更正（不改写 r1 原文）**：r1 报告 §5.2-2 与 P0-01 行写「17 个码中 15 个为新 wire 码，仅 `LOCK_CHANGED`/`TARGET_NOT_FOUND` 复用」。本轮逐码 `git grep -c` 复算：17 个码中 **3 个复用**（`LOCK_CHANGED`、`PAGE_SIZE_UNAVAILABLE`、`TARGET_NOT_FOUND`）、**14 个新**。r1 的结论（错误码面需逐条冻结 category/retryable）不变，仅数量与复用清单更正；r1 文件按证据纪律保留原字节。

---

## 2. 逐项核查

### 2.1 范围完整性：AC1–AC7 是否可验收

| AC | 判定 | 依据 |
|---|---|---|
| AC1 契约登记 + 未知命令拒绝（`:69`） | **不可验收（改卡可解）** | 登记载体/行格式/命名/状态字面量均未定义，且与 master §8 既有行格式不一致 → R2-P1-01；未知命令拒绝由既有兜底满足（`core_service.py:5440-5455`），无需工作 |
| AC2 语义不变（`:70`） | **不可机械验证** | `:61` 把 handler 目标写成 `next_draft_id`/`add_patch`/`prepare_candidates`/`draft_status`——四个方法名在 `src/`/`apps/`/`tests/`/`doc/` **全部 0 命中**（本轮 `git grep` 实测），真实方法见 R2-P1-02；无 payload/result 映射即无法判「只调用既有服务」→ R2-P1-02/P1-03 |
| AC3 CoreClient 映射（`:71`） | **不完整** | 漏 registry 描述符/additive 集合/域归属/parity 同步，而这些又反向决定 AC1 的命令名 → R2-P1-04 |
| AC4 Python 协议测试（`:72`） | **可验收** | `tests/core/**` 在写域；命令经 `pytest.ini`/conftest 校验可运行；缺 `tests/domain/**` 为 P2 |
| AC5 回归（`:73`） | **可验收** | build + 冻结测试命令 + 基线 931/0/60（引用链见 §0） |
| AC6 冻结 pin（`:74`） | **可验收** | 本轮三绿实测：15/15、EXIT 0；本卡无端口/无 pin 文件写域 |
| AC7 证据（`:75`） | **可验收** | 与模板 `TASK.md:61-66` 一致；`evidence_dir` 已含在 `allowed_paths` |

**结论：7 条中 4 条可验收（AC4–AC7），AC1–AC3 需改卡。** 写域总体已正确（无遗漏的必需路径，除 `tests/domain`），过度项只剩 `src/application/editing/**`。

### 2.2 写域复核（`allowed_paths` `:22-34`）

| 路径 | 判定 |
|---|---|
| `doc/contracts/V11R_COMMAND_CONTRACT_V1.md` | **必需且已加** ✓；不在 15 份 pin、不在 `check.ps1` 治理入口 → 改它不会触红 pin，但也无机械守卫（见 §2.3） |
| `src/bootstrap/core_service.py` | 足够 ✓（白名单/dispatch/handler/`CoreServiceServer.__init__` `:1032-1052`/`main()` 注入 `:5804-5814` 均在本文件；`CoreServices.drafts` 已由 `core_assembly.py:760`、`:1310-1316` 提供） |
| `tests/core/**` | 必需 ✓ |
| `src/application/editing/**` | **过度**：AC2/禁止范围（`:70`、`:81`）均声明不改编辑语义，卡 `:61` 也只调既有方法 → 建议移除或注「只读」 |
| `NewManga.CoreClient/**`、`NewManga.CoreClient.Tests/**` | 必需 ✓；但需收窄到新增测试/明确允许改的两处 parity 断言（R2-P1-04） |
| 已移除的 App 侧三项 | ✓（P0-02） |
| `tests/domain/**` | **卡内引用但未在写域**（`:52` 提及「如需」；AC4 运行它）→ R2-P2-01 |

### 2.3 契约登记格式是否与既有条目一致（Lead 第 3 问）

**答：不一致，且当前写法会让 AC1 机械失败。** 三条硬事实：

1. **master §8 的行没有 payload/result/错误码 列。** 现有行形如 `| C067 | \`create_region\` | Region | core | 3（zero protocol bump，Lead 裁定） | \`PENDING(V11R-F0-1)\` |`（`doc/contracts/V11R_COMMAND_CONTRACT_V1.md:229-239`，表头 `:227` 有 7 列但数据行只有 6 个数据格，状态在末位）。卡 `:60` 要求「名称/payload/result/错误码/版本」写入其中——**既有行格式承载不了**。
2. **Region 先例的 per-command 内容在独立契约文档**：`V11R_REGION_WRITE_CONTRACT.md` 有 `## 2. 逐命令契约（C067–C077）`（`:155-283`，每条 `### C0xx`）+ `## 1. 通用协议语义`（`:37`）+ `## 8. 验证出口`，master §8 `:225` 只是指针行（「上游契约…」）；且该文件 `:9` 明写「本文件是总契约的 C067–C077 节（总契约由 V11R-A-3 维护，不得在本文件重复冻结 C001–C066）」。**本卡没有对应的 FEA-05 契约文档**，故 payload/result/error 无处安放。
3. **测试解析器对行形状有硬约束**（`CommandContractV11RTests.cs`）：
   - 只有位于**标题以 `## 8.` 开头**的节下、且 `C 编号 > 66` 的行才算 pending 行（`:260-266`）；若在上下文新建 `### 8.1 …` 子节，`section` 变成 `### 8.1 …`，**行会被完全忽略** → AC1 失败。
   - pending 行的**命令名取第 3 格**（`cells[2]`），且 `PendingCommandNames` 过滤正则 `^[a-z][a-z0-9_]*$`（`:199-202`）——**点号名 `drafts.open` 会被过滤掉**；卡与 W-3 只给了点号 Core 路由名，未给 Host 命令名（snake_case）→ 若按卡面登记，`RegistrySurface_IsFullyDeclared`（`:70-81`）红。
   - pending 行的**状态取 `cells[^2]`**（倒数第二个格，`:264`），并要求 `StartsWith("PENDING")`（`:92-93`）→ 状态必须是最后一个数据列；若照 §4 baseline 的 12 列格式写（状态在第 11 列、后跟「源码引用」），`cells[^2]` 会读到「源码引用」→ 红。
   - 另：`CommandContractV11RTests.BaselineRows_CoverC001ToC066`（`:31-49`）要求 §4 恰好 66 行，故新行**必须**放 §8。

**注入点另一层风险（P2-05）**：master 文档自述是生成物——`V11R_COMMAND_CONTRACT_V1.md:7-8`「生成器：`verification/V11R-A-3/tools/{extract_contract_facts,build_contract_doc}.py`（…改契约后重新生成）」，而 §8 整段是生成器里的模板文本（`verification/V11R-A-3/tools/build_contract_doc.py:459-480`）。当前 doc 的 §8 已与生成器漂移（doc 有 C077 行、生成器只有 C077 占位），说明「手工追加 §8 行」是本仓既有做法（F0-2 先例），**可以继续用**；但须在交付物里写明「手工追加，不重跑生成器」并在 §10 变更记录登记，否则未来重生成会抹掉 C078–C083。

### 2.4 裁决点与未登记裁决点

- **W-1（`:87`）**：依据已改正 ✓。但 `:54` 的「本卡同时更新命令契约文档，故不依赖『零 bump』」表述把两件事混在一起——文档 rev 不是协议变更，正确表述应为「**协议 minor 保持 3**（Draft 族落默认面，`core_service.py:5468-5476` 的响应投影不新增分支）；契约文档 rev 只是登记」。建议 W-1/AC1 直接写死 `PROTOCOL_MINOR` 不变（并入 R2-P1-01）。
- **W-2（`:88`）**：结论「不接 UI」✓，但指针仍是 DAG 外 `FEA-06`（Q-16 原文为 FEA-05/**FEA-07**，`FEA-04.md:48`）→ R2-P2-03。
- **W-3（`:89`）**：6 条命令集合 ✓（去 `close`）；但**只有 Core 路由名、无 Host 命令名/域/minor**，而这正是 AC1 的机械前提 → R2-P1-01/P1-04。
- **W-4（`:90`）**：错误结构仍漏 `category`/`retryable` → R2-P1-03。
- **仍未登记**：①`drafts.status` 的取数语义；②`EditToken` 传输/TTL/续发；③是否出 `flush(trigger)`（C-13 SC-D02 强制 flush 点，`FEA-C13_DRAFT_PROTECTION_DRAFT.md:47-54`；服务侧 `force_flush/flush_pending`，`drafts.py:576-589`）；④`core.shutdown` 时活动草稿的 flush/清理；⑤Host 命令名 + `HostCommandDomain` 域归属（新增 `Drafts` 域 vs 复用 `Region` 域）→ 合并为 R2-P1-02。

### 2.5 依赖与顺序

- `depends_on: FEA-03 / FEA-04` 仍成立（两者 done：PLAN `:15-16`）。移除端口面后与 `FEA-04b`（in_review，仅写 `doc/design/fluent-v1/**`）**无写域交集，可并行** ✓。
- **新出现的前置**：本卡要改的 master 契约由已收口的 `V11R-A-3` 线维护（`V11R_REGION_WRITE_CONTRACT.md:9`），本卡以 DSH 冻结的写域接管其增量登记——需要一句 DSH 裁决记录（「FEA-05 承接 master 契约 C078+ 增量登记，V11R-A-3 维护权已随其收口回归 DSH」），否则后续 Reviewer 会质疑写权来源（R2-P2-05）。

### 2.6 可执行性（工作量/测试面/隐藏风险）

- 工作量（端口面剔除后）：`core_service.py` 1 族 + 6 handler + 注入（约 150–250 行）；6 个 typed 模型 + dispatcher 分支 + registry 6 条 + 域决策（约 200–350 行）；Python 6–12 例 + CoreClient 6–12 例；契约：1 份新文档（若采纳）+ §8 6 行 + §8 叙述/§10 变更记录。**单卡可完成。**
- 隐藏风险（仍存）：①错误码面 14 个新 wire 码无 category/retryable 映射（R2-P1-03）；②`apply_candidates` 的 receipt 重放（`drafts.py:389-407`）与 `EDIT_TOKEN_REUSED` 必须原样透传，卡内无回执重放测试项；③草稿后台 flush 线程（`drafts.py:711-728`）与 stdio 命令串行（`core_service.py:1061-1062`）的交互无测试项；④`drafts` 未注入时是否 fail-closed `CORE_UNAVAILABLE`（`_require_cleanup` 先例 `core_service.py:1918-1928`）未写进 AC1；⑤契约登记与 registry 命名的双向一致性只靠 `CommandContractV11RTests` 一侧兜底，`CommandParityContractTests` 的 additive 集合断言需同步（R2-P1-04）。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **R2-P1-01** | P1 | 卡 `:60`、`:69`（AC1）、`:54`；`V11R_COMMAND_CONTRACT_V1.md:227-242`、`:7-8`；`CommandContractV11RTests.cs:199-202`、`:260-266`、`:92-93`；`V11R_REGION_WRITE_CONTRACT.md:9`、`:155-283`；`build_contract_doc.py:459-480` | **「契约登记」交付物不可执行/不可判定**：①master §8 行没有 payload/result/错误码列，卡的「同格式 + 含 payload/result/错误码/版本」自相矛盾；②per-command 契约先例是独立文档（Region），本卡没有对应文档；③解析器要求行在 `## 8.` 标题下、命令名为 `cells[2]` 且匹配 `^[a-z][a-z0-9_]*$`（点号名被过滤）、状态为最后一列且以 `PENDING` 开头——卡面只给点号路由名，照写 AC1 必红；④未写协议 minor=3；⑤未说明手工追加后不重跑生成器 | 二选一：**(a) 推荐**——新增 `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md`（结构照 Region §0/§1/§2「逐命令契约 C078–C083」/§8/§9；写域加该路径），master §8 只加 6 条指针行：`\| C078 \| \`drafts_open\` \| Region/Drafts \| core \| 3（zero protocol bump） \| \`PENDING(FEA-05-WIRE-1)\` \|`（名称在第 3 格、状态末列、snake_case），并更新 §8 叙述总数、§10 变更记录；(b) 若不建独立文档，则在卡内逐条给出 §8 行模板与 6 行完整内容，并明确「手工追加、不重跑生成器」。两种方案都须在 AC1 增一句「`PROTOCOL_MINOR` 保持 3，Draft 族响应 minor=3」 |
| **R2-P1-02** | P1 | 卡 `:61`、`:70`（AC2）、`:89`（W-3）；`drafts.py:97`、`:151`、`:158`、`:165`、`:215`、`:304`、`:374`、`:576`、`:584` | **handler 名单方法名错误 + 关键语义未定。** 卡列 `next_draft_id`/`add_patch`/`prepare_candidates`/`draft_status`——全仓 **0 命中**；真实方法为 `open_draft`（需 `session_id`+`page_binding_version`，`:97-105`）、`patch_draft(draft_id, session_id, patch)`（`:165-168`）、`prepare_candidate(region_id, patch, origin=…, draft_id?, base_revision_id?)`（`:304-312`）、`apply_candidates(EditToken, candidate_ids)`（`:374-377`）、`get_draft`/`list_drafts`（`:151`/`:158`）、`discard_draft(draft_id, session_id)`（`:215`）。`drafts.status` 二义未定；无 `flush(trigger)`；`EditToken` TTL/续发未定；`core.shutdown` flush 未定 | 卡内给出「命令 → 真实方法 → 请求字段 → 结果字段」四列表；`drafts.status` 明确为 `get_draft`（单草稿）或 `list_drafts(session_id)`（按会话枚举），不得两可；补 `drafts.flush(trigger)`（trigger 对齐 `_FLUSH_TRIGGERS`，服务侧 `force_flush`/`flush_pending`）或明确 deferral + 承接卡；写明 session 语义（谁持有 `SessionId`、`EditToken` 只在 wire 透传不回写） |
| **R2-P1-03** | P1 | 卡 `:60`、`:70`（AC2）、`:90`（W-4）；`make_error_envelope`（`core_service.py:808-825`）；`drafts.py:775-782`；`M2-C1_TYPED_IPC_CONTRACT.md:3`（rev 2.11 在冻结新命令时同步冻结错误码投影的先例） | **payload/result/错误码映射仍缺。** W-4 仍是「code/message/details」，漏 `category`/`retryable`；`drafts.py` 抛 17 个码中 **14 个**在 `core_service.py` 0 命中（新 wire 码；复用 3 个：`LOCK_CHANGED`/`PAGE_SIZE_UNAVAILABLE`/`TARGET_NOT_FOUND`，本轮逐码 `git grep -c` 实测），无一条给出 category/retryable/details 投影；AC2「不新增编辑规则」无法机械验证 | 在契约文档/卡内给出：①6 条命令的 request/result 字段表（含 token/candidate/receipt/`revisionIds` 的外形）；②新 wire 码 → `{category, retryable, details}` 映射表；③`cause_code` 是否外泄的裁定（建议不外泄，仅 `details.cause_code` 白名单）；④回执重放（`EDIT_TOKEN_REUSED` 原样透传）与并发 flush 各一条测试项 |
| **R2-P1-04** | P1 | 卡 `:62`、`:71`（AC3）、`:29`；`HostCommandDispatcher.cs:59`；`HostCommandModel.cs:5-13`、`:37`；`HostCommandRegistry.cs:310`；`CommandParityContractTests.cs:88-91`、`:109-119`、`:140-144` | **CoreClient 交付面仍漏项，且现在直接决定 AC1。** 卡只写模型+分发器；实际必须同步：①`HostCommandRegistry` 6 条描述符（CoreService 通道须带 `CoreCommand` 与 `CoreMinor>0`，`:140-144`；且必须 `Implemented`，`:131`）；②parity 测试的「注册表新增集合 == `V11RAdditiveCommandNames`」断言（`:88-91`）需扩展（建议新增独立集合而非把 Drafts 塞进 V11R 集合）；③域归属——`HostCommandDomain` 6 域闭集（`:5-13`），新增 `Drafts` 域会牵动每域非空断言（`:109-114`）与 `DomainServices.cs:40-97`；④注册表命令名必须与契约 §8 的 `cells[2]` 名逐字一致（snake_case）；⑤无「不得弱化既有断言」红线 | AC3 补上述 5 项；给出「Host 命令名 ↔ Core 路由 ↔ 域」对照表（例：`drafts_open` ↔ `drafts.open` ↔ Region 或新 Drafts 域），并要求 parity 测试只增不改既有断言 |
| **R2-P1-05** | P1 | 卡 `:22-34`、`:26`、`:52-61`、`:79-81`；`doc/templates/TASK.md:34-42`、`:50-52`；`09_COLLABORATION.md:215` | **模板两节仍缺 + 写域仍过度。** 无「允许修改范围」节（须「共享接口/Schema/依赖变更单列」——本卡改共享命令契约属此类）与「依赖、风险与阻塞」节（须区分硬依赖/可并行、记录未定契约与解除标准）；`src/application/editing/**` 仍全开放而禁止范围说不改编辑规则（若 handler 误调不存在的方法，Owner 有写权在服务层补方法 → 语义漂移风险） | 补两节；把「共享接口/契约变更」单列（命令契约 + wire 错误码 + CoreClient 注册表面）并标注前置依据；`src/application/editing/**` 改为只读或移除；在禁止范围加「不得弱化/删除既有契约对照断言（只允许新增）」 |
| **R2-P2-01** | P2 | 卡 `:52`、`:72`（AC4）、`:28`（写域） | `tests/domain/**` 在卡内被提及（「如需」）且 AC4 会运行，但不在 `allowed_paths`（Lead 转述「已纳入」与实际文件不符） | 要么把 `tests/domain/**` 加入写域，要么把 `:52` 改为「`tests/domain` 只读运行」，二者取一并与 AC4 对齐 |
| **R2-P2-02** | P2 | 卡 `:99`（测试要求表 AC6 行） | 命令写 `python tools/governance/generate_api_inventory.py --check` —— 该脚本实际在 `tools/generate_api_inventory.py`（`FEA-CONTRACT-FROZEN-C07.md:35` 的冻结条件即用此路径），照抄会直接报「文件不存在」 | 改为 `python tools/generate_api_inventory.py --check` |
| **R2-P2-03** | P2 | 卡 `:51`、`:88`（W-2）、`:43-46`；`FEA-04.md:48`；`REBASELINE_PLAN.md:17-18` | W-2 仍指「FEA-06」（当前 DAG 无该节点，Q-16 原文为 FEA-05/**FEA-07**）；`:51` 又说「W-2 声明省略」但 W-2 行仍在——内部不一致 | W-2 依据改指 Q-16 原文 `FEA-04.md:48`（FEA-05/FEA-07）或写「后续卡（待 DSH 释放）」；删除/修正 `:51` 的「声明省略」措辞 |
| **R2-P2-04** | P2 | 卡 `:51`；`REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` | `FEA-05-PORT-1` 是唯一承载 IHostController 端口面 + C-07 UNFREEZE 的后续卡，但全仓仅本卡 `:51` 提及，DAG 与 LEDGER 均无该节点 | 由 DSH 在 PLAN 记一行「候选（未释放）」或在卡内注明「待 DSH 建卡」，避免端口面变成口口相传的悬空 deferral |
| **R2-P2-05** | P2 | 卡 `:24`；`V11R_COMMAND_CONTRACT_V1.md:7-8`、`:220-242`；`build_contract_doc.py:459-480`；`V11R_REGION_WRITE_CONTRACT.md:9` | 契约登记的**写权与生成物纪律**未记录：master 自述由生成器产出、§8 是生成器模板文本、维护归属写的是已收口的 `V11R-A-3`；当前 doc 已手工漂移（C077）说明可手工追加，但卡未裁决「手工追加 vs 重跑生成器」，也未在 §10 变更记录/维护行登记 | 在卡内写一句 DSH 裁决：手工追加 C078+ 行、不重跑生成器（F0-2 先例），并在 master §10 增一行变更记录、把「维护」行改为 DSH/当前 Task；若改为重跑生成器，则须把 `verification/V11R-A-3/tools/**` 与 facts 加入写域（不推荐） |
| **R2-P2-06** | P2 | 卡 `:39-44`（来源链）；`FEA-03.md:153` L-2；`FEA-04.md:99` L-2；`M2-C1_TYPED_IPC_CONTRACT.md`（F0-1 新族未更新） | **L-2 解除记录缺失。** 上游两条 L-2 均要求「透传 Draft 命令/暴露新命令 → blocked，先完成 M2-C1」；本卡改走 V11R 命令契约（与 F0-1 先例一致，M2-C1 并未随 F0-1 更新），但卡内未记录该判定，导致「阻塞条件是否解除」在证据上不可核 | 在来源链加一行：「L-2 解除依据：F0-1 先例（新命令族以 `V11R_COMMAND_CONTRACT_V1` §8 + 独立契约文档承载，M2-C1 不再逐族追加）；FEA-05 同法」 |
| **R2-P2-07** | P2 | 卡 `:31-33`（STATUS/PLAN/LEDGER 写域）；`check.ps1:614-621`；`doc/STATUS.md:19`；`doc/TASK_LEDGER.md:9-13` | r1 P2-02/P2-03 未处置：STATUS 行数已满 45/45、字节 97.6%，任何新增行触发预算报错；STATUS `:19` 的 LEDGER 计数（483=471+11+1）与当前 491/480/10 不符 | 卡内加一行前置（STATUS 须同批压缩）；STATUS `:19` 顺手刷新 |
| **R2-P2-08** | P2 | 卡 `:52-61`、`:104-109` | r1 P2-05 未补：无 kill-criteria（如「契约登记格式未定则不得开工」）、无 worktree 说明（`:109` 仍「无 worktree」，与 FEA-03/04 使用独立 worktree 的先例不同，未说明理由） | 收窄后工作量已下降；建议补一句 kill-criteria 与 worktree 决策（用/不用各一句理由） |

---

## 4. 处置建议（最小成本）

1. **R2-P1-01 是其余 P1 的锚点**：先定契约登记形态（推荐新建 `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md` + master §8 指针行 + §10 变更记录），并把「名称（snake_case Host 名）/域/minor=3/状态 `PENDING(FEA-05-WIRE-1)`」一次写死；这一条同时消化 R2-P1-02 的命名部分与 R2-P1-04 的注册表命名一致性。
2. **R2-P1-02/P1-03 合并处理**：一张表同时给出「命令 → 真实服务方法 → request/result → wire 错误码 → category/retryable」，并在 AC2 引该表为唯一判据。
3. **R2-P1-04**：补 registry/parity/域对照表，加「只增不改断言」红线。
4. **R2-P1-05**：补模板两节，移除 `src/application/editing/**` 写权。
5. P2 批量顺手：`tests/domain` 写域、脚本路径、W-2 指针、`FEA-05-PORT-1` 登记、生成器纪律、L-2 解除记录、STATUS 预算/陈旧计数、kill-criteria。
6. 改卡后派 **r3** 复核；P0/P1 = 0 才置 `ready`。

## 5. 边界声明

本报告**只审范围冻结**（Task 卡文本及其引用的契约/代码/测试事实与治理指针），**不构成实现验收**，也不构成契约、设计或架构批准。结论仅指该范围文本是否可执行、可机械验证、与上游先例与治理规则一致。

本席位（`fea05-wire-scope-reviewer`，r1→r2 同一席位续任）**未参与** FEA-05-WIRE-1 的起草、实现或返修，**未执行** `dotnet build`/`dotnet test`/`pytest`/UI 真机运行，**未修改**任何被审文件、契约、STATUS、PLAN、LEDGER 或源码，**未** commit/push。报告内行号基于 `7122d5696` 实测；标注「未验证」的项（931/0/60 当前是否仍成立）不得当作已核实事实引用。
