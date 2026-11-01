---
task_id: FEA-05-PORT-1
reviewer: fea05-wire-scope-reviewer
reviewer_kind: subagent
author: dsh-lead
base_commit: 70dd4322f
reviewed_head: a6c8fb247
decision: changes_requested
counts: { P0: 2, P1: 1, P2: 9 }
---

# FEA-05-PORT-1 范围复核 r1（独立上下文，未参与本卡）

| 字段 | 值 |
|---|---|
| base_commit | `70dd4322fb9980b377e20205bf2c711636d7cb0c`（建卡提交的父提交；卡 `:13` 自记 `base_commit: 70dd4322f` ✓） |
| reviewed_head | `a6c8fb247f3d043724a8124c9ec66c7363ac4a34`（`docs(fea-05-port-1): 建卡…`；`git status --porcelain` 为空） |
| 被审对象 | `doc/tasks/FEA-05-PORT-1.md`（103 行，status=proposed）；提交同时更新 `REBASELINE_PLAN.md`、`STATUS.md`、`TASK_LEDGER.md` |
| reviewer | `fea05-wire-scope-reviewer`（Draft 线 FEA-05-WIRE-1 范围 r1–r7 与实现 impl-r1–r3 同一席位；**本卡未参与者**） |
| reviewer 来源 | DSH Team Lead 派发，**fresh 独立上下文**（DSH 子 agent）；只读被审 head，未 commit/push |
| 日期 | 2026-11-02 |
| 审查范围 | 仅范围冻结文本（任务拆解 P1–P6、AC1–AC7、W-1…W-4、写域、契约 UNFREEZE、端口/registry/测试、治理指针）；不含实现 |
| 结论 | **changes_requested** |
| 计数 | **P0 = 2 / P1 = 1 / P2 = 9（共 12）** |

> **一句话理由**：方向与最小改法正确（Region 契约 v1.6「并集」+ `DraftsCommandNames`；registry 11→17；测试并集断言），但**写域缺两处 AC 必需文件**——`doc/plan/FEA-C07_API_INVENTORY.md`（AC5 的 `--check` 与 `verify_pins` 链必需）与 `doc/reviews/CONTRACT-UNFREEZE-*.md`（AC1/P6 的 UNFREEZE 载体）——导致 **AC1/AC5 按现卡不可达（P0×2）**；另端口面未冻结签名/返回类型，且 C082「抓取/列表二选一」与单个 `GetDraftStatusAsync` 冲突（P1）。其余 9 条 P2 不阻断冻结。

---

## 0. 方法与只读声明

- 只读核查被审 head；**未修改任何被审文件**，未 commit/push；**本报告是本轮唯一新增文件**。
- 已执行（只读）：

| 命令/检查 | 结果 |
|---|---|
| `git rev-parse HEAD` / `git status --porcelain` | `a6c8fb247…` / 空（clean） |
| `git show --stat a6c8fb247` | 4 files：卡（+103）、PLAN（+1）、STATUS（3+/−）、LEDGER（11+/−） |
| `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS（3 warnings）**：10 个非终态 Task；STATUS 3154 bytes/34 lines（80%）；PLAN 3751 bytes/51 lines（80%） |
| `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 15）** |
| `python tools/generate_api_inventory.py --check` | **EXIT 0**（当前 1/47/6 = 54 与 C-07 文档一致） |
| 契约/测试/registry/端口源码核对 | 见 §1 逐项（含行号） |

---

## 1. 七项必查

### 1.1 契约 UNFREEZE 必要性与充分性

- **必要性：成立** ✓。Region 契约 FROZEN v1.5 的不变式有 3 处正文 + 1 处状态头 + 1 处变更记录：`:62-63`（§1.1「并集 `V11RAdditiveCommandNames`（11）」）、`:344-346`（§4「`All` = 冻结 66 + 11 条追加」）、`:457`（§8 验证出口「追加集恰为 `V11RAdditiveCommandNames`（10 写 + 1 读）」）、`:1`/`:3`（标题与版本史）、`:485-494`（§9 变更记录）。任何新家族进入 registry 都会使 `RegionWriteCommandTests:107-117` 的第二条断言失效，**不注册不可行**（端口依赖 registry 路由）。
- **充分性：原则成立** ✓。v1.6 + UNFREEZE 载体 + 重新独立复核 + 重新冻结（含 C-07 pin）是仓库既有冻结纪律（`FEA-CONTRACT-FROZEN-C07.md:15-17`；UNFREEZE 载体先例 `doc/reviews/CONTRACT-UNFREEZE-2026-11-01.md`、`…-C08-…`、`…-C13-…`）。
- **最小改法**：Approach A（本卡）——`V11RAdditiveCommandNames` 扩为并集（17）+ 新增 `DraftsCommandNames`（6）+ 契约 3 处措辞改「各家族声明集合之并」，**是当前最小且与 `HostCommandRegistry.cs:305-313` 自身 docstring「every command ADDED on top of the frozen 66-command snapshot」一致的改法** ✓。替代方案 B（保持 11、另立 `AllAdditiveCommandNames`）需要同样改三处契约文本并多一个属性，不减成本；方案 C（不改契约、把「追加集」解释为 V11R 家族子集）会让冻结契约文本**字面失真**，不可取。
- **更轻替代与代价**：C-07 一侧理论上可只重算 pin 而不走 UNFREEZE（C-07 文档 `:12` 允许「同一 Task 内同步更新清单」，`FEA-CONTRACT-FROZEN-C07.md:42` 称 additive 更新 routine）；但同一冻结记录 `:17` 明写「修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」，且 `CONTRACT-UNFREEZE-2026-11-01.md:17` 已确立「只重算 pin 不充分」。**结论：保守走 UNFREEZE 正确**，但本卡只登记了一个 UNFREEZE 记录、且未写「重新独立复核」环节（见 P0-02）。
- **v1.5→v1.6 覆盖缺口**：卡 `:51` 只写「变更记录 + 新不变式 + `DraftsCommandNames`」，**未枚举 5 处更新站点**（`:1`/`:3`/`:62-63`/`:344-346`/`:457`/`:485-494`），也混淆了 `DraftsCommandNames` 的归属（它是 C# 属性、声明在 `HostCommandRegistry.cs`，契约只需引用/声明并集规则）→ P2-1。

### 1.2 端口面范围

- **6 方法 ↔ C078–C083 名称一一对应** ✓：`OpenDraftAsync`/`PatchDraftAsync`/`PrepareCandidateAsync`/`ApplyCandidatesAsync`/`GetDraftStatusAsync`/`DiscardDraftAsync`（卡 `:52`/`:78`）↔ wire 6 命令（`FEA-05_DRAFT_WIRE_CONTRACT.md:26-31`）。
- **风格一致性** ✓：`HostController` 经 `HostCommandDispatcher.InvokeAsync`（`HostController.cs:728` 等）；`NullHostController` 为确定性假实现（`NullHostController.cs:6-37`）；`IHostController` 现有方法为**强类型返回**（如 `Task<RegionPageProjection?>` `:186`、`Task<RegionRevisionHistory?>` `:191`），不是 `JsonElement`。
- **缺口**：①6 个方法的**参数/返回类型/DTO 归属**未冻结；②**C082 是双模式**（`drafts_status`：`draftId`→`{draft}` / `sessionId`→`{drafts[]}`，契约 `:30`），单个 `GetDraftStatusAsync` 无法用同一返回类型表达两种外形；③`NullHostController` 的「安全默认」语义（返回 null / 空列表 / 抛 NotSupported）未定 → **P1-01**。
- **写域**：`App.Tests/**` 在写域 ✓（`FakeHostController` 位于 `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs`，是仅有的三个实现之一，另两个在写域 ✓）。

### 1.3 CoreClient registry

- 现状核对：`HostCommandRegistry.cs:279-292`（RegionWrite 10）、`:299-303`（RegionRead 1）、`:305-313`（`V11RAdditiveCommandNames` = 两者并集，11）；域枚举 6 值（`HostCommandModel.cs:5-13`）；`AddDomain` 由 `CoreBindings`（`:135+`）决定通道/minor；`HostCommandDispatcher.WriteCorePayload` 逐命令有显式校验 case，`default:` 为**透传**（`:498-503`）。
- 卡 P3 方向正确：11→17 + 域 `Drafts` + 通道 `core` + minor 3 ✓（与 `FEA-05_DRAFT_WIRE_CONTRACT.md:24-31` 一致）。
- **但卡未写**：`DraftsNames` 数组、6 条 `CoreBindings`（`CoreCommand` 应为同名下划线、`Minor=3`，沿 Region 先例）、`HostCommandDomain.Drafts` 枚举成员、`AddDomain` 调用；也未写 dispatcher 是「添加显式 payload 校验 case」还是「依赖 default 透传」→ P2-2。
- **`CommandParityContractTests` 会否红**：`:88-91` 要求 `registry − snapshot == V11RAdditiveCommandNames`；`:109-119` 按枚举派生每域计数并要求非空。只要属性扩为 17 + 新域非空即通过，**无需改测试** ✓。`CommandWiringB1Tests:63-75`、`:115-117`、`:562` 均为派生/动态计数，不受影响 ✓。

### 1.4 契约测试更新

- `RegionWriteCommandTests:107-117` 现状：`additive := registry − snapshot`；`:109` 断言 `additive == V11RAdditiveCommandNames`；`:110-114` 断言 `additive == RegionWrite ∪ RegionRead`；`:115-117` 计数守恒。**改法成立** ✓：把 `:110-114` 改为 `RegionWrite ∪ RegionRead ∪ Drafts`，并保留「`RegionWrite ∪ RegionRead` ⊆ additive」的 Region 子集断言；`:109` 在属性扩为 17 后自然成立。
- **配套未写**：类 docstring（`:9-19` 声称「exactly the ten Region write commands and the one read projection」）与测试名 `Registry_AppendsTheV11RCommands_WithoutEditingTheFrozenSnapshot`（`:92-93`）需同步改语义；契约 §4/§8 引用行也要随 v1.6 对齐 → P2-3。
- `CommandContractV11RTests` **不受影响** ✓：`:68-86` 要求「注册命令必须已声明」——6 条已在 §8.2 pending 行且 impl-r3 已修可见性；`:88-111` 对**已注册**的 pending 名要求 `IsImplemented` 为真——注册后 6 条均为 `Implemented`（Binding 命中，`HostCommandRegistry.cs:340-355`），通过。卡 AC4 写「`CommandContractV11RTests` 通过」正确 ✓。

### 1.5 依赖与顺序

- `depends_on: FEA-05-WIRE-1` **成立** ✓（上游 done、`integration_commit: d9d7dde41`、证据 complete；W-6 明确把端口/registry/不变式留给本卡）。
- **与 FEA-04b 不冲突** ✓：FEA-04b 写域仅 `doc/design/fluent-v1/**` + 指针 + `doc/reviews/FEA-04b-*.md`（其 `allowed_paths`），与本卡无交集；其 AC5（用户确认 + 独立评审 + DSH 冻结，`FEA-04b.md:65`/`:80`）是**设计基线**的前置，针对 FEA-06（UI 交互），不影响本卡（无 UI 行为）。**建议**在卡内写明「FEA-06 须待 FEA-04b AC5 关闭」。
- 另：FEA-05 契约本身仍 `PENDING`（`FEA-05_DRAFT_WIRE_CONTRACT.md:3`），总契约 §8.2 仍 `PENDING`；本卡注册后命令「可被 Host 调用」但仍不得被 UI 当稳定契约消费——**应在卡内登记该前置/收口项（DSH 冻结 FEA-05 契约 + 处置 §8.2 状态）** → P2-6。

### 1.6 可执行性与 AC 可验收性

| AC | 可验收性 | 说明 |
|---|---|---|
| AC1 契约 UNFREEZE | **不可达（P0-02）** | UNFREEZE 载体路径（`doc/reviews/CONTRACT-UNFREEZE-*.md`）不在写域；只登记了一条记录但涉及**两个冻结物**（Region 契约 v1.6 + C-07 重新冻结）；未含「重新独立复核」；「新 pin 由 DSH 签发」与 P6 的 `FEA-CONTRACT-FROZEN-<id>.md` 指向不明（Region 契约**无 pin**，有 pin 的是 C-07） |
| AC2 端口面 | **部分（P1-01）** | 名称/实现/Null 默认可核，但签名/返回类型/双模式未冻结 |
| AC3 registry | **可验收** ✓ | 11→17、域/通道/minor、parity 均可机械核 |
| AC4 契约测试 | **可验收（配套见 P2-3）** ✓ | 并集断言 + Region 子集成立；`CommandContractV11RTests` 不受影响 |
| AC5 端口清单 | **不可达（P0-01）** | `generate_api_inventory.py --check` 比较 `FEA-C07_API_INVENTORY.md:20` 的 `\| IHostController \| 47 \|`；+6 方法后必须改为 53（合计 54→60），但该文件不在写域；且 C-07 文件字节变化会使 `verify_pins` 失配，须同步更新 `FEA-CONTRACT-FROZEN-C07.md:15` 的 sha256 |
| AC6 回归 | **可验收（措辞待改）** | 全量 sln 可跑；但「不退化（基线 931/0/60）」未说明新增测试会使总数变化 → P2-7 |
| AC7 证据 | **可验收** | `verification/FEA-05-PORT-1/**` 在写域 ✓ |

**写域清单核对**：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` ✓、`doc/plan/FEA-CONTRACT-FROZEN-C*.md` ✓（glob 覆盖 `FEA-CONTRACT-FROZEN-C07.md`，也可收窄为单文件）、端口三实现 ✓、`NewManga.CoreClient/**` ✓、两个测试工程 ✓、verification/指针/reviews ✓；**缺**：`doc/plan/FEA-C07_API_INVENTORY.md`（P0-01）、`doc/reviews/CONTRACT-UNFREEZE-*.md`（P0-02，现仅允许 `FEA-05-PORT-1-*.md`）、`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（P2-9，可选）。

### 1.7 治理

- 三绿：`check.ps1` **PASS（3 warnings）**／`verify_pins` **15/15 PASS**／`generate_api_inventory --check` **EXIT 0** ✓。
- 指针：`REBASELINE_PLAN.md:19` 有 `FEA-05-PORT-1` 行 ✓、`TASK_LEDGER.md:46` 有该行 ✓（台账 10 非终态与 check.ps1 一致）。
- **STATUS 不一致**：`:7` 同句重复「`FEA-04b` in_review；上一 `FEA-04b` `in_review`…」；`:10` 仍写「`FEA-05-PORT-1` 待建卡」（已建卡）；另有 STATUS/PLAN 80% 预算警告 → P2-5。

---

## 2. Findings

| ID | 级别 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| **P0-01** | P0 | 卡 `:21-36`（allowed_paths）、`:55`（P5）、`:64`（AC5）；`doc/plan/FEA-C07_API_INVENTORY.md:3`/`:12`/`:20`/`:22`/`:24`；`FEA-CONTRACT-FROZEN-C07.md:15-17`、`:42`；`verify_pins.ps1:6-13`；`generate_api_inventory.py:166-179` | **写域缺 C-07 库存文件 → AC5 不可达。** 加 6 个 `IHostController` 方法后 `--check` 要求文档统计行 `\| IHostController \| 53 \|`（合计 60），而 `doc/plan/FEA-C07_API_INVENTORY.md` **不在写域**；该文件字节变化又使 `verify_pins` 的 C-07 pin（`FEA-CONTRACT-FROZEN-C07.md:15`）失配。卡 P5「若脚本生成清单，需重跑并提交」也不准——该文档是**人工整理版**（脚本只 print），需手改统计/成员表/变更类别 | 二选一：**(a)** 把 `doc/plan/FEA-C07_API_INVENTORY.md` 加入 `allowed_paths`，并在 P5/AC5 写明更新点：`:20` 47→53、`:22` 合计 54→60、`IHostController` 成员表 +6、`:24`「11 个新增」→17、`:4` 生成日期/HEAD；**(b)** 声明该文件与 pin 由 DSH 单点产出，并在 Handoff 明确顺序（实现者先交 `generate_api_inventory.py` 输出，DSH 改文档+pin）。两种都需在 AC5 中写清谁在何时交付 |
| **P0-02** | P0 | 卡 `:23`（写域）、`:55-56`（P5/P6）、`:60`（AC1）、`:80`（W-4）；`FEA-CONTRACT-FROZEN-C07.md:17`/`:31-36`；`doc/reviews/CONTRACT-UNFREEZE-2026-11-01.md:10-17`；`V11R_REGION_WRITE_CONTRACT.md:1`/`:3`/`:485-494` | **UNFREEZE 载体不在写域且范围登记不全 → AC1 不可达。** ①`doc/reviews/CONTRACT-UNFREEZE-*.md` 不被 `doc/reviews/FEA-05-PORT-1-*.md` 覆盖；②本卡实际涉及**两个冻结物**：Region 契约 v1.5→v1.6（无 pin，仅 FROZEN 状态行）与 C-07 库存 bytes→需重算 pin，卡只写「一条 UNFREEZE 记录」「新 pin 写入…（或追加）」，未区分；③冻结记录要求「重新独立复核」（`FEA-CONTRACT-FROZEN-C07.md:17`），AC1 未列；④「新 pin 由 DSH 签发」与写域内 `FEA-CONTRACT-FROZEN-C*.md` 的写权/时序未说清 | 补写：**(a)** 写域加 `doc/reviews/CONTRACT-UNFREEZE-*.md`（或声明 DSH 单点写）；**(b)** P6 明确两条载体（建议 `CONTRACT-UNFREEZE-REGION-2026-11-02.md` + `CONTRACT-UNFREEZE-C07-2026-11-02.md`，或一条明列两对象）及各自「改前 pin/改后 pin」表（沿 `CONTRACT-UNFREEZE-2026-11-01.md:10-17` 格式）；**(c)** AC1 增加「v1.6 与 C-07 新字节经**上下文独立复核**后由 DSH 重签 pin；`verify_pins` 15/15」；**(d)** 写明 Region 契约**无 pin**、pin 工作仅针对 C-07，避免实现者去改 `verify_pins.ps1`（不在写域） |
| **P1-01** | P1 | 卡 `:52`/`:78`（P2/W-2）、`:61`（AC2）；`FEA-05_DRAFT_WIRE_CONTRACT.md:26-31`；`IHostController.cs:106`/`:186`/`:191`；`HostCommandDispatcher.cs:498-503` | **端口面规格不足。** ①6 方法只给名称，**参数/返回类型/DTO 归属未冻结**（现有端口是强类型返回，不是 `JsonElement`；新增 DTO 放 `NewManga.CoreClient` 还是 `NewManga.App/Services` 未说）；②**C082 是双模式**（`draftId`→`{draft}`、`sessionId`→`{drafts[]}`），单个 `GetDraftStatusAsync` 无法用同一返回类型表达两种结果——需拆两个方法或返回包装类型；③`NullHostController`「安全默认」语义未定（null / 空列表 / NotSupported）；④dispatcher 对 6 命令是「加显式 payload 校验 case」还是「依赖 default 透传」（`:498-503`）未定 | 在卡内冻结 6（或 7）个方法签名（参数名映射 wire 字段、返回类型、DTO 归属）与 Null 默认语义；明确 C082 处置：**(a)** 拆 `GetDraftAsync(draftId)` + `ListDraftsAsync(sessionId)`（端口 7 方法），或 **(b)** 单方法返回 `Task<DraftStatusResult>` 包装（`draft`/`drafts` 二选一）；并写明 dispatcher 校验策略 |
| **P2-1** | P2 | 卡 `:51`（P1）、`:79`（W-3）；`V11R_REGION_WRITE_CONTRACT.md:1`/`:3`/`:62-63`/`:344-346`/`:457`/`:485-494`；`HostCommandRegistry.cs:305-313` | 契约 v1.6 只写「变更记录 + 新不变式 + DraftsCommandNames」，未枚举 5 处站点（标题/状态版本史/§1.1/§4/§8/§9）；`DraftsCommandNames` 归属混淆（C# 属性声明在 registry，契约应声明并集规则而非"补声明"） | 在 P1 列出 5 处更新点与目标措辞；P1 改称「契约声明并集包含 `DraftsCommandNames`（6）」 |
| **P2-2** | P2 | 卡 `:53`（P3）；`HostCommandRegistry.cs:76-100`/`:135+`/`:324-330`/`:340-380`；`HostCommandDispatcher.cs:185-503` | registry 实现细节未写：`DraftsNames` 数组、6 条 `CoreBindings`（CoreCommand 同名下划线、Minor=3）、`HostCommandDomain.Drafts` 枚举成员、`AddDomain` 调用；dispatcher 是否加显式校验 case 未说 | 补齐为可逐项核对的实现清单（贴行号），并写明「沿 Region 先例，CoreCommand=同名」 |
| **P2-3** | P2 | 卡 `:54`（P4）、`:63`（AC4）；`RegionWriteCommandTests.cs:9-19`/`:92-93`/`:107-117` | `RegionWriteCommandTests` 改断言时未提配套：类 docstring 与测试名仍称「exactly the ten Region write commands and the one read projection」；契约 §4/§8 的引用文本需随 v1.6 调整 | P4 增加「同步更新类注释/测试名/引用文本」；`CommandParityContractTests` 明确「无需改（派生）」 |
| **P2-4** | P2 | 卡 `:31`（allowed_paths）、`:68-71`（禁止范围） | `NewManga.App/ViewModels/V2/Studio/**` 可写但禁止范围写「不把 Draft 命令接入 UI 交互（FEA-06 负责）」——允许范围与禁止范围矛盾；且端口是接口成员，不需要 Studio 注入 | 删除该路径，或注明「仅编译期接口引用，不改行为」的必要性 |
| **P2-5** | P2 | `doc/STATUS.md:7`/`:10`；`REBASELINE_PLAN.md:19`；`TASK_LEDGER.md:46` | 指针：PLAN/LEDGER 已登记 ✓；**STATUS `:7` 重复「`FEA-04b` in_review；上一 `FEA-04b` in_review」**；`:10` 仍「`FEA-05-PORT-1` 待建卡」；STATUS/PLAN 触 80% 预算警告 | 修正 STATUS 两行（去重、改「已建卡待复核」）；注意后续新增行需先压缩 |
| **P2-6** | P2 | 卡 `:68-71`（禁止范围）、`:45`（来源链）；`FEA-05_DRAFT_WIRE_CONTRACT.md:3`；`V11R_COMMAND_CONTRACT_V1.md:220-258`（§8.2） | FEA-05 契约仍 `PENDING`、总契约 §8.2 仍 `PENDING`；本卡注册后命令可被 Host 调用，但按 §8.2 约束「不得在 UI 中当稳定契约消费」。卡排除这些文件（合理），但未登记「DSH 冻结 FEA-05 契约 + 处置 §8.2 状态」为前置/收口项 | 在「来源与授权链」或 Closeout 登记该前置；FEA-06 前必须完成 |
| **P2-7** | P2 | 卡 `:65`（AC6） | 「不退化（基线 931/0/60）」未说明新增测试会使总数上升；易被误读成必须仍为 931 | 改为「0 failed；总数 ≥ 931（新增本卡测试不计退化）」 |
| **P2-8** | P2 | 卡 `:56`（P6）、`:80`（W-4）、`:60`（AC1） | 「新 pin 写入 `FEA-CONTRACT-FROZEN-<id>.md`（或追加）」「pin 数量不变，pin 值更新」两句未对齐：Region 契约无 pin；C-07 已有 pin 记录，正确动作是**更新 `FEA-CONTRACT-FROZEN-C07.md:15` 的 sha256 + 记录冻结/重冻时间与理由**，不是新建 pin 记录 | 把 P6/W-4 改写成「C-07 pin 重算：更新记录 sha256 与时间；不新增 map 条目」；Region 契约只走 v1.6 状态行+变更记录 |
| **P2-9** | P2 | 卡 `:21-36`；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md:25`/`:71` | 冻结矩阵 `FEA-CONTRACT_FREEZE_MATRIX.md`（C-07 `FROZEN` 行、`:71`「冻结后在 FROZEN-<ID> 记录 pin」）是否需随本次 re-freeze 更新未定；若需，该文件也不在写域 | 由 DSH 决定：矩阵仅记录初冻状态则可不动；若需记录重冻，则加入写域或 DSH 单点更新 |

---

## 3. 处置建议（最小成本）

1. **先修 P0-01/P0-02（写域/交付面）**：把 `doc/plan/FEA-C07_API_INVENTORY.md` 与 `doc/reviews/CONTRACT-UNFREEZE-*.md` 纳入写域（或明确 DSH 单点产出与顺序），并在 AC1/AC5 写清「谁、何时、交付什么、如何核（pin 15/15 + `--check` EXIT 0）」。这是本卡能否 `ready` 的唯一硬阻塞。
2. **P1-01**：冻结 6/7 个端口方法签名 + C082 双模式处置 + Null 默认语义 + dispatcher 校验策略。
3. P2 批量：契约站点枚举（1）、registry/dispatcher 清单（2）、测试配套（3）、Studio 矛盾（4）、STATUS 修正（5）、FEA-05 契约冻结前置（6）、AC6 措辞（7）、pin 语义（8）、冻结矩阵（9）。
4. 改卡后派 **r2** 复核；P0/P1 = 0 才置 `ready`。

## 4. 边界声明

本报告只审范围冻结（Task 卡文本及其引用的契约/代码/测试/治理事实），**不构成实现验收**，也不构成 UNFREEZE 或契约修订批准。本席位未参与 FEA-05-PORT-1 的起草/实现/返修；未修改被审文件、未 commit/push；报告行号基于 `a6c8fb247` 实测。
