---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: a6c8fb247
reviewed_head: d647805a0
decision: changes_requested
counts: { P0: 0, P1: 2, P2: 10 }
---

# FEA-05-PORT-1 范围复核 r2（独立上下文，未参与本卡）

| 字段 | 值 |
|---|---|
| base_commit | `a6c8fb247f3d043724a8124c9ec66c7363ac4a34`（范围 v1 被审 head） |
| reviewed_head | `d647805a08eb5f8456270566ac991436edb1c391`（`docs(fea-05-port-1): 范围 v2…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-PORT-1.md`（106 行，status=proposed）；同提交另改 `TASK_LEDGER.md`（脚本重生成）并收编 r1 报告 |
| reviewer | `fea05-wire-scope-reviewer`（Draft 线 FEA-05-WIRE-1 范围 r1–r7 与实现 impl-r1–r3 同一席位；**本卡未参与者**） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | r1 的 P0×2/P1×1/剩余 P2 disposition、AC1–AC7 可验收性、写域缺口、新问题 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 0 / P1 = 2 / P2 = 10（共 12）** |

> **一句话理由**：r1 的两条 P0 与 P1-01 **实质关闭**（写域补齐 C-07 库存 + UNFREEZE 载体 + C-07 pin 记录；AC1 改为两冻结物 + 独立复核 + 15/15；端口冻结 7 方法/强类型 DTO/Null/dispatcher），P2 也有 3 条关闭；**但 AC1 ③ 的验收数字算错**（现网 `IHostController` 47、合计 54，+7 后应为 **54 / 61**，卡写「53→59、合计 60→66」），且 **AC2「6 方法」与 W-2 旧名单（含已拆掉的 `GetDraftStatusAsync`）同 P2 的 7 方法自相矛盾**——两条 P1 需修；另有 10 条 P2（含「前置」节 literal `\n` 结构损坏、`DraftPatch` 同名冲突、Null「Never throws」矛盾等）。

---

## 0. 方法与只读声明

- 只读核查被审 head；未修改被审文件、未 commit/push；**本报告是本轮唯一新增文件**。
- 已执行（只读）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `d647805a0…` / 空（clean） |
| `git diff --stat a6c8fb247..d647805a0` | 3 files：卡（+23/−13 实为改写）、LEDGER（+6/−6）、r1 报告（+132） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings）**：10 非终态 Task；STATUS 3154/34（80%）；PLAN 3751/51（80%） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0**；渲染统计 = `IHostController 47` / **合计 54**（据此核算 AC1 数字） |
| 源码核对 | `core_service.py:3015-3018`（`drafts_open` 返回 `draft/canEdit/token`）；`NullHostController.cs:51`（"Never throws"）；`DraftBuffer.cs:21`（既有 `DraftPatch`）；`RegionWriteCommandTests.cs:109-117` |

---

## 1. r1 逐项 disposition

| r1 ID | 级别 | 状态 | 证据 / 缺口 |
|---|---|---|---|
| r1-P0-01 C-07 库存不在写域 | P0 | **CLOSED（留有 1 条新 P1 数字错）** | `allowed_paths:24` 已加 `doc/plan/FEA-C07_API_INVENTORY.md`；AC1 ③ 点名更新 C-07；AC5 `:67` 已改「人工清单与代码一致；脚本只 print 不生成」✓。但 AC1 ③ 数字错（见 P1-01） |
| r1-P0-02 UNFREEZE 载体不在写域 | P0 | **CLOSED** | `:25` 加 `doc/plan/FEA-CONTRACT-FROZEN-C07.md`；`:26` 加 `doc/reviews/CONTRACT-UNFREEZE-*.md`；AC1 改「两个冻结物 + `CONTRACT-UNFREEZE-2026-11-xx` 记录 + 按 `FROZEN-C07:17` 独立复核 + `verify_pins` 15/15」✓；W-4/P6 同步 ✓。残余仅为措辞（见 P2-10） |
| r1-P1-01 端口签名未冻结 | P1 | **CLOSED（附 2 条 P2）** | P2 `:55` 冻结 7 方法完整签名（含 `CancellationToken`）、DTO 归属 `NewManga.CoreClient/Commands/DraftCommands.cs`、Null 逐方法默认、dispatcher 显式 case；C082 拆 `GetDraftAsync`/`ListDraftsAsync` 均发 `drafts_status` ✓ 与 `FEA-05_DRAFT_WIRE_CONTRACT.md:30` 双模式对应。残余：DTO 外形细节（P2-9）、`DraftPatch` 同名（P2-8）、Null 风格陈述（P2-9） |
| r1-P2-1 契约 5 站点未枚举 | P2 | **OPEN** | P1 `:54` 与 v1 完全相同（仍只写「变更记录 + 新不变式 + `DraftsCommandNames`」），`V11R_REGION_WRITE_CONTRACT.md:1/:3/:62-63/:344-346/:457` 五处未列；`DraftsCommandNames` 仍是 C# 属性而卡写在契约项下 |
| r1-P2-2 registry 细节 | P2 | **PARTIAL** | P3 `:56` 已加 `DraftsCommandNames`/`All`/域枚举/`CoreBindings`/`AddDomain` ✓；但 `All` 语义不清（是既有 registry 字典还是新聚合属性），双状态方法共用同一 `drafts_status` descriptor 的映射与 dispatcher 双模式 XOR 校验未写 |
| r1-P2-3 测试配套 | P2 | **CLOSED** | P4 `:57` 已细化 `:109`（17）/`:110-114`（Region 子集）/补 `DraftsCommandNames ⊆ additive`/类注释与测试名同步；`CommandParityContractTests` 派生断言自动成立 ✓（`CommandParityContractTests.cs:88-91/109-119`） |
| r1-P2-4 Studio 写域矛盾 | P2 | **OPEN** | `allowed_paths:34` 仍保留 Studio 写域与「仅注入不改变行为」，而禁止范围 `:74` 仍「不把 Draft 命令接入 UI 交互」；未说明为何需要写 Studio |
| r1-P2-5 STATUS 指针 | P2 | **OPEN** | 本提交未改 STATUS：`:7` 仍重复「`FEA-04b` in_review；上一 `FEA-04b` in_review…」；`:10` 仍「`FEA-05-PORT-1` 待建卡」。（LEDGER 已按脚本重生成：tracked 492 / untracked 0 / 非终态 10 ✓） |
| r1-P2-6 FEA-05 契约/§8.2 前置 | P2 | **CLOSED（结构损坏见 §3 P2-7）** | 新增「前置」节（`:50`）写明 FEA-05 契约与 §8.2 仍 `PENDING`、由 DSH 收口升级；FEA-04b 无写域重叠；FEA-06 待本卡 + 设计基线 AC5 ✓ |
| r1-P2-7 AC6 措辞 | P2 | **PARTIAL** | 测试要求 `:92` 已补全命令（build EXIT=0 + test 全量）✓；但 AC6 `:68` 仍只写「不退化（基线 931/0/60）」，未说明新增测试会使总数变化 |
| r1-P2-8 pin 语义 | P2 | **CLOSED** | P6 `:59`/W-4 `:83`/AC1 ⑤ 已改为「C-07 pin 重算写入 `FEA-CONTRACT-FROZEN-C07.md`；pin 数量不变、C-07 值更新」✓；Region 契约无 pin 的事实已由「pin 数量不变」隐含 |
| r1-P2-9 冻结矩阵 | P2 | **OPEN** | 卡仍未提 `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（`:25`/`:71` C-07 `FROZEN` 行）是否随 re-freeze 更新；写域也没有该文件 |

---

## 2. 关键核查

### 2.1 AC1 ③ 数字核算（P1-01）

- 实测：`python tools/generate_api_inventory.py` 渲染 = `| IHostController | 47 |`、`| **合计** | **54** |`；`FEA-C07_API_INVENTORY.md:20`/`:22` 同为 **47 / 54**。
- 本卡端口为 **7 个方法**（P2 `:55`），故更新后应为 **`IHostController` 47→54、合计 54→61**，成员表 +7、`:24` 变更类别「11 个新增」→18。
- 卡 AC1 ③ 写的是「IHostController **53→59**、合计 **60→66**」——基线疑似把 v1 的 6 方法目标（47+6=53、54+6=60）当成了现值，又在之后只加 6（53+6=59、60+6=66），**四个数字全错**。若实现者按卡落盘，`generate_api_inventory.py --check` 必失败（脚本按 `:166-179` 比对 `| IHostController | N |`），AC5 从而连带失败。

### 2.2 AC2 / W-2 与 P2 的 7 方法矛盾（P1-02）

- P2（`:55`）：**7 个方法**，C082 拆为 `GetDraftAsync`/`ListDraftsAsync`，**不再有** `GetDraftStatusAsync`。
- AC2（`:64`）：仍写「`IHostController` **6 方法** + 实现 + Null 默认」。
- W-2（`:81`，已裁表）：仍列 6 名并含 **`GetDraftStatusAsync`**，与 P2 的 7 方法/拆分名单直接冲突。
- 该冲突会让实现者在「6 还是 7」「`GetDraftStatusAsync` 是否存在」上二义；且 C-07 库存计数（P1-01）也取决于 7 vs 6。

### 2.3 写域与可执行性

- **已闭合**：`doc/plan/FEA-C07_API_INVENTORY.md` ✓（`:24`）、`FEA-CONTRACT-FROZEN-C07.md` ✓（`:25`）、`doc/reviews/CONTRACT-UNFREEZE-*.md` ✓（`:26`）、Region 契约 ✓（`:23`）、端口三实现 ✓、`NewManga.CoreClient/**` ✓（`DraftCommands.cs`）、两个测试工程 ✓、verification/指针/reviews ✓。
- **仍缺/待定**：`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（P2-9，若 DSH 决定登记 re-freeze）；`FEA-05_DRAFT_WIRE_CONTRACT.md` 与总契约 §8.2 由 DSH 收口（前置 `:50` 已声明）✓ 不属本卡写域，可接受。
- **AC 可验收性**：AC1/AC3/AC4/AC5 **可验收**（AC1 需先修 P1-01 数字）；AC2 **不可机械验收**（6 vs 7，P1-02）；AC6 可跑但措辞待补（P2-7）；AC7 可验收。

### 2.4 新发现（细节）

- **前置节结构损坏**：`:50` 一行内含 **5 处 literal `\n`**（`## 前置\n\n- …\n- …\n\n## 任务拆解`），Markdown 会把整段当一条 H2 行，`## 任务拆解` 不再是标题；v1 的 `## 任务拆解` 被此替换（diff 可见）。
- **`DraftPatch` 同名**：`NewManga.ApplicationCore/DraftBuffer.cs:21` 已有 `public sealed record DraftPatch(`；卡再在 `NewManga.CoreClient/Commands/DraftCommands.cs` 定义 `DraftPatch`。命名空间虽不同，但 App ViewModels 同时 using 两侧时会产生歧义/需 alias；卡未决定复用、改名还是别名。
- **Null 风格自述矛盾**：卡称 `NullHostController`「抛 `NotSupportedException`（与既有 Null 风格一致）」，但既有实现 `NullHostController.cs:47-51` 明确「**Never throws**」，且全类无 throw（只返回 null/空/CompletedTask）。
- **DTO 外形/P5**：`DraftLease` 字段（wire `{draft, canEdit, token}`，`core_service.py:3015-3018`）、`DraftPatch` 字段、`GetDraftAsync` 为何可空（wire 返回 `{draft}`，未找到应走 typed error）、`DiscardDraftAsync` 丢弃 `{discarded}` 均未写；P5 `:58` 仍「若脚本生成清单，需重跑并提交」（AC5 已改正，P5 未同步）。

---

## 3. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **P1-01** | P1 | 卡 `:63`（AC1 ③）；`FEA-C07_API_INVENTORY.md:20`/`:22`/`:24`；`generate_api_inventory.py:166-179` | **C-07 数字错**：现网 47/54；+7 方法后应 **54/61**；卡写「53→59、合计 60→66」，且基线/增量/合计数均错。按卡落盘会使 `--check` 失败、AC5 连带红 | 改为「`IHostController` **47→54**、合计 **54→61**、`:24` 变更类别 11→18 个 FEA 新增、成员表 +7、`:4` 生成日期/HEAD 刷新」；建议直接给一句可机核的期望行 |
| **P1-02** | P1 | 卡 `:55`（P2，7 方法）、`:64`（AC2，6 方法）、`:81`（W-2，6 名含 `GetDraftStatusAsync`） | **方法数/名单自相矛盾**：P2 拆 C082 为 `GetDraftAsync`+`ListDraftsAsync`（7 个），AC2 与 W-2 仍 6 个/含旧名 `GetDraftStatusAsync` | AC2 改「7 方法（6 wire 命令，C082 拆 2）」；W-2 名单改为 7 个并注明「C082 两方法均发 `drafts_status`」；P3/AC3 的「6 条模型/注册」保持指 wire 命令并加一句区分 |
| P2-1 | P2 | 卡 `:54`；`V11R_REGION_WRITE_CONTRACT.md:1`/`:3`/`:62-63`/`:344-346`/`:457` | 契约 v1.6 更新站点未枚举；`DraftsCommandNames` 归属（C# 属性 vs 契约声明）未澄清 | 列出 5 处站点与目标措辞；P1 改称「契约声明并集含 `DraftsCommandNames`（6），属性实现在 P3」 |
| P2-2 | P2 | 卡 `:55`/`:56`；`HostCommandRegistry.cs:135+`/`:305-313`；`HostCommandDispatcher.cs:185-503` | `All` 语义不清；`drafts_status` 双模式共用 descriptor 的 CoreBinding（`drafts_status`→`drafts_status`, minor 3）与 dispatcher XOR 校验（draftId/sessionId 恰一）未写 | P3 明确 `All`=既有 registry 字典、两端口方法映射到同一 `drafts_status` descriptor；P2 写明 dispatcher 对 `drafts_status` 的 XOR 校验 |
| P2-3 | P2 | 卡 `:34`/`:74` | Studio 写域与禁止范围的矛盾未处置 | 删除 Studio 路径或改为「仅 DI 占位、不得改行为」并说明必要性 |
| P2-4 | P2 | `doc/STATUS.md:7`/`:10` | STATUS 重复句与「待建卡」陈旧未修 | 随本轮 r2 处置一起修正 STATUS（去重、改「已建卡待复核」） |
| P2-5 | P2 | 卡 `:68`（AC6） | AC6 仍「不退化（基线 931/0/60）」，未说明新增测试使总数上升 | 改「0 failed；总数 ≥931（新增测试不计退化）」 |
| P2-6 | P2 | `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:25`/`:71` | re-freeze 是否更新冻结矩阵未定，写域也没有该文件 | DSH 明确：不更新（记录只写 FROZEN-C07）或加入写域 |
| P2-7 | P2 | 卡 `:50` | 「前置」节含 **5 处 literal `\n`**，`## 前置` 与 `## 任务拆解` 结构损坏（v1 的 `## 任务拆解` 被替换） | 用真实换行重排为独立小节，恢复 `## 任务拆解` 标题 |
| P2-8 | P2 | 卡 `:55`；`DraftBuffer.cs:21` | `DraftCommands.cs` 计划定义的 `DraftPatch` 与 `NewManga.ApplicationCore/DraftBuffer.cs:21` 既有 `DraftPatch` 同名 | 决定复用/改名/别名，并写进 P2（避免 App 层 using 歧义） |
| P2-9 | P2 | 卡 `:55`；`NullHostController.cs:47-51`；`core_service.py:3015-3018`；`FEA-05_DRAFT_WIRE_CONTRACT.md:26-31` | Null 自称「与既有 Null 风格一致（抛 NotSupportedException）」与「Never throws」矛盾；`DraftLease` 三字段、`DraftPatch` 字段、`GetDraftAsync` 可空、`DiscardDraftAsync` 丢 `discarded` 未写 | 二选一：Null 返回空/默认（改陈述）或注明抛异常为例外并逐方法列；DTO 字段以 wire §2/to_json 列出；C083 可返回 `Task<bool>` 或注明丢弃理由 |
| P2-10 | P2 | 卡 `:58`（P5）；`:63`（AC1 ②） | P5 仍「若脚本生成清单，需重跑并提交」与 AC5 已改正矛盾；AC1 ② 说「两份冻结物的…新 pin 值」但 Region 契约无 pin（仅 C-07 有） | P5 改为「人工更新清单（统计+成员表+变更类别+生成日期）」；AC1 ② 改「新 pin 值（仅 C-07；Region 契约无 pin）」 |

---

## 4. 处置建议

1. **P1-01/P1-02 先修**：更正 C-07 数字（47→54、54→61）并统一方法数（7 方法 / 6 wire 命令），同步 AC2/W-2/P3 措辞——这两条是当前唯一阻塞。
2. **P2-7（literal `\n`）与 P2-8（`DraftPatch` 同名）建议本轮一并修**：前者影响卡的可读性与结构；后者影响实现期编译/using 决策。
3. P2 其余：契约站点枚举（1）、registry 细节（2）、Studio（3）、STATUS（4）、AC6（5）、矩阵（6）、Null/DTO（9）、P5/AC1② 措辞（10）。
4. 改卡后派 **r3** 复核（本席位可继续，只读）；P0/P1=0 后 DSH 置 `ready` 并派实现。

## 5. 边界声明

本报告只审范围冻结（Task 卡文本及其引用的契约/代码/测试/治理事实），**不构成实现验收**，也不构成 UNFREEZE 或契约修订批准。本席位未参与 FEA-05-PORT-1 的起草/实现/返修；未修改被审文件、未 commit/push；行号基于 `d647805a0` 实测。
