# CONTRACT UNFREEZE：C-07 API Inventory（v1.9，2026-11-14）

- 契约：`doc/plan/FEA-C07_API_INVENTORY.md`（冻结记录 [`doc/plan/FEA-CONTRACT-FROZEN-C07.md`](../plan/FEA-CONTRACT-FROZEN-C07.md)）
- 关联卡：`FEA-06-RESIDUAL-4A`（契约前置，[卡面](../tasks/FEA-06-RESIDUAL-4A.md)）
- 授权：用户 2026-11-14 直接指令「继续 FEA 线收口，且重开卡走 C-07 UNFREEZE 路线」→ [RO-1 重开裁决](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md) §3 R2（撤销 Q7 `OUT`，固定走 C-07 additive UNFREEZE）
- 同型先例：[CONTRACT-UNFREEZE-2026-11-10-C07](CONTRACT-UNFREEZE-2026-11-10-C07.md)（v1.2 计划节，代码零改动）、[CONTRACT-UNFREEZE-2026-11-10-AI1](CONTRACT-UNFREEZE-2026-11-10-AI1.md)（v1.8 统计翻转）

## 1. 变更范围（append-only 计划节，代码零改动）

| 项 | 旧（v1.8 冻结） | 新（v1.9 UNFREEZE） |
|---|---|---|
| 文件 sha256（pin） | `8ccaba05cbc21eec04a366f8bfa2be2dea4515ba90e6d5aab95b11a7c47f0509` | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` |
| 新增内容 | — | ① 状态行加 v1.9 UNFREEZE 注记；② 生成日期行加 v1.9 重跑记录；③ 新节「RO-1 计划追加（v1.9 预授权，尚未落地）」：1 条计划命令（`ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>` / 落地卡 `FEA-06-RESIDUAL-4B` / 落地行号 `#80`）；④ 「与 C-07 冻结面的关系」补一条「两节计划追加均不计入统计」 |
| 代码 | `IHostController` 79 方法；三接口合计 86（`--check` 实测 `1/79/6 = 86`） | **不变**（仍 79 / 86；本卡不改 `src/**`、`apps/**`、`tests/**`） |
| 正式成员表 | 79 方法 + 4 非方法成员 = 脚本 stdout 逐行一致 | **逐字节不变**（`ALL_MATCH: True` 复核：IReaderProgressSink 1 / IHostController 83 行 / IRunController 6） |
| 统计行 / 合计 | `IHostController 79`、合计 `86` | **不变**（仍 79 / 86 = 代码实测） |
| 旧成员 / 旧签名 | — | **不变**（无删除、无改名、无参数变更；本 UNFREEZE 是纯 additive：新增一节 + 两处注记） |
| 「S5 计划追加」节 | 25/25 全部落地、无待实现行 | **不动**（原字节保留） |
| 其他冻结契约 | — | **零改动**（C-01b…C-17、FEA-01 字节不变，其余 17 pins 不变） |

**差异指纹（可独立复现）**：`git diff --numstat doc/plan/FEA-C07_API_INVENTORY.md` = **+18 / −2**，结构为：① 新增「RO-1 计划追加」一节（12 行）；② 「与 C-07 冻结面的关系」补 1 条（1 行）；③ 状态行、生成日期行两处**行内追加**（2 行被改，内容为追加注记，**未删任何既有语义**）；④ 其余 3 行为上述块的空行归位。`sha256(old) = 8ccaba05…`、`sha256(new) = 91e51ab7…`。统计行、正式成员表、S5 计划节**零字节改动**。

## 2. 为什么必须 UNFREEZE

1. **冻结纪律**：C-07 冻结记录 §1 明文「条款字节自本记录起不得改动；修订须走 UNFREEZE 载体 + 重新独立复核 + 重新冻结」。本次要改 inventory 字节（新增预授权节），因此必须走载体、重算 pin、重新独立复核、重冻。
2. **产品范围重新纳入**：用户 2026-11-14 撤销 Q7 `OUT`，重开「查看对照」（`FEA-06` AC3 的 PARTIAL 缺口之一，设计意图见 `doc/design/fluent-v1/06-page-workbench.md:50`、`09-state-matrix.md:14`）。该能力的 L1 基底文本唯一权威来源是 Core `list_page_region_texts`，而它在 App 侧**没有 `IHostController` 端口**——端口一旦落地就会改 C-07 成员表，因此必须先把契约变更冻结在前。
3. **避免二次 UNFREEZE**：把名称/返回类型/落地行号一次锁死在计划节，`FEA-06-RESIDUAL-4B` 落地时只做「并入正式成员表 + 统计翻转 + 重算 pin」，不再需要第二次名单裁决（与 v1.2 S5 计划节、v1.7/v1.8 落地完全同型）。

**为什么本次不直接翻转统计 79→80 / 86→87**（DSH 2026-11-14 裁决指定口径，本节四条即裁决依据）：

1. `tools/generate_api_inventory.py` 的计数**由源码 interface 块解析得出**（`generate_api_inventory.py:105-119`，源 `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs`）。4A **不动 `apps/**`**，该文件在端口落地前仍是 **79 个方法** ⇒ 80/87 在本卡内**不可达**；
2. `--check` 是**子串判定** `f"| IHostController | {n} |" in doc`（`generate_api_inventory.py:174`），`n=79`；把统计写成 80 必 **FAIL** ⇒ 门禁不可绿。而且正式成员表会与脚本 stdout 差一行（违反 v1.6 起「逐行一致」纪律）；
3. **同型先例**：v1.2（[CONTRACT-UNFREEZE-2026-11-10-C07](CONTRACT-UNFREEZE-2026-11-10-C07.md)）就是「计划追加节 + 代码零改动 + pin 重算」，本次沿用同一形态；
4. [C-07 冻结记录](../plan/FEA-CONTRACT-FROZEN-C07.md) §3「实现注意」要求「新增/删除端口方法须在**同一 Task 内**重跑脚本并更新清单」⇒ 统计翻转与成员表 `#80` 行归**落地卡** `FEA-06-RESIDUAL-4B`（pin **v1.10**）。

**结论**：把统计提前写绿等于让契约对代码说谎。本卡把 80/87 记为**预授权目标值**（§1 表格 + §3 计划节 + 冻结记录 §2 条件 3/§3），真实翻转留在 4B。RO-1 裁决记录中「79→80 / 86→87」的 R2 表述由 DSH 另以 errata 更正，本卡不改 DSH 维护的裁决文件。

## 3. 计划节（新增，唯一授权内容）

| # | 计划命令 | 计划返回类型 | 落地卡 | 落地后行号 |
|---|---|---|---|---|
| RO-1 | `ListPageRegionTextsAsync` | `Task<RegionPageTextProjection?>` | `FEA-06-RESIDUAL-4B` | `#80` |

**接入既有面（已在库，本卡不改）**：
- Core：`src/bootstrap/core_service.py:3533/7787/7796`（`list_page_region_texts` 已实现）；
- Host 注册/分发：`HostCommandRegistry.cs:191/357/465`、`HostCommandDispatcher.cs:868-871`（`page_id` 必填、`region_ids` 可选；**不接受 `expected_revision`**——该字段属 `restore_region_revision`（`core_service.py:3605+`），不得混入本命令签名，否则偏离本预授权）；
- 客户端解析器：`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:224-281`（`RegionPageTextProjection` / `RegionTextDetail`，当前仅测试使用）。

**4B 落地判据（v1.10 的动作清单，本卡不执行）**：
1. 在 `IHostController.cs` 加该 1 个方法（含 `using NewManga.CoreClient.Commands;`），并在 `HostController` / `NullHostController` / 测试 `FakeHostController` 三处实现（降级一律 `null`）；
2. 重跑 `python tools/generate_api_inventory.py`，把计划行并入正式成员表第 **80** 行，统计改 `IHostController 80` / 合计 `87`（`--check` 须 EXIT 0，且成员表与 stdout 逐行一致）；
3. 重算 pin（v1.10），在冻结记录 §1 置顶新行并保留 v1.9 原值，§1B/§2 条件 3/§5 同步。

## 4. 不变量与门禁（本次 UNFREEZE 实测）

1. 旧 79 个 `IHostController` 方法 + `IReaderProgressSink` 1 + `IRunController` 6 的签名与返回类型**零改动**；4 个非方法成员（`Snapshot` / `Changed` / `StartRequests` / `ExportDirectorySuggestion`）**零改动**。
2. 正式成员表 = `python tools/generate_api_inventory.py` stdout **逐行一致**（复核脚本输出 `IReaderProgressSink: ALL_MATCH=True`、`IHostController: 83 行 ALL_MATCH=True`、`IRunController: ALL_MATCH=True`）。
3. `python tools/generate_api_inventory.py --check` **EXIT 0**，基线仍 `1/79/6 = 86`（计划节不计入脚本统计）。
4. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → **PASS (all 18)**，C07 行 = 新 pin `91e51ab7…`，其余 17 pins 逐项不变。
   - **已知限制（P3，非本卡引入）**：`doc/plan/FEA-C07_API_INVENTORY.md` 在 `.gitattributes` 中**没有** `eol=lf` 规则，而本仓库 `core.autocrlf=true`；`git diff` 会警告「LF will be replaced by CRLF the next time Git touches it」。即 pin 在**本工作树（LF）**可复现，但 fresh clone 若按 autocrlf 检查出 CRLF 则 pin 不可复现。该限制对 v1.8 及更早 pin 同样成立（属既有债）。修法是在 `.gitattributes` 增 `doc/plan/FEA-C07_API_INVENTORY.md text eol=lf`，但该文件不在本卡 `allowed_paths`，交 DSH 处置。
5. 无 `src/**` / `apps/**` / `tests/**` / DDL / schema diff；**本提交所含路径**全部 ⊆ `FEA-06-RESIDUAL-4A` 的 `allowed_paths`（含 DSH 授权的一次性 `doc/TASK_LEDGER.md` 机械重生成）。工作树中 `tests/fea11/test_source_match.py` 的未提交改动属 DSH 并行验证，**不在本次提交、不属本卡范围**。
6. `pwsh -NoProfile -File tools/governance/check.ps1`（默认 + `-TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md`）→ **PASS (3 warnings) / EXIT=0**。新增卡使 `doc/TASK_LEDGER.md` 计数由 `task files 599 / non-terminal 7` 变为 `600 / 8`；该重生成经 **DSH 2026-11-14 显式授权**执行一次（`python tools/governance/task_ledger.py --write`，不手写），否则 `check.ps1:272-283` 会因台账过期报错。

## 5. 独立复核（必需）

- 按 C-07 冻结语义，本次 UNFREEZE 须由**未参与本卡写作**的独立上下文 reviewer 复核（2026-10-31 裁决：独立性以上下文独立为准，作者不得自审）。
- 复核面：§1 变更范围与差异指纹、计划节内容与规格字段是否逐字一致、pin 是否等于文件 SHA-256、成员表是否 = 脚本 stdout、冻结记录 §1/§1B/§2/§5 是否自洽、门禁四项实测。
- 结论（`approved` / `changes_requested`）**由复核者追写**到 §6 并同步冻结记录 §1B；**实现者不得代写 approved**。

## 6. 复核记录

**状态：`approved` —— 本 UNFREEZE 已生效并重冻（2026-11-14）。** 起草者（DSH 派出的实施 Agent）未参与复核，也未预填结论。

| 轮次 | 审查者身份与来源 | 被审 head | 结论 | P0/P1/P2/P3 | 门禁 |
|---|---|---|---|---|---|
| r1 | 独立上下文子 agent（`451313d2…`；未参与写作/实现；只读） | `7c1ac472f` | **`changes_requested`** | 0 / 2 / 7 / 5 | 四门禁 EXIT=0；字节层全过（pin 三口径、成员表逐行、越界、pins 18/18） |
| r2 | 独立上下文子 agent（`8389f5bc…`；未参与 r1 与实现；只读） | `756ab29e2` | **`approved`** | 0 / 0 / 2 / 5 | 四门禁 EXIT=0；pin 仍 `91e51ab7…`（修复未触 inventory 字节） |

- **r1 的 2 条 P1**（均为记录层假陈述：§5 假称 `check.ps1` 红、§2 假称 `expected_revision` 是可选 wire 字段）已修，r2 实测「真实关闭」。
- **r1 的 P2** 七条已逐条处置：P2-1/P2-7 直接修；P2-2…P2-6 写入 4A 卡作为 4B 的规格 v1.1 硬约束。r2 的 2 条残余 P2（规格正文未版本化、`TARGET_NOT_FOUND` 层级歧义）已在规格 v1.1 定稿中修正。
- 结论：**满足「重新独立复核后重冻」条件**；pin 保持 `91e51ab7…`（修复未改 inventory 字节，r2 已实测 `756ab29e2` 未触及该文件）。

> **覆盖范围声明（诚实边界）**：r2 的 `reviewed_head` = `756ab29e2`，覆盖 **C-07 v1.9 的 inventory 字节与记录链**。此后对 4A 卡的**规格 v1.1 定稿**（修正 r2 残余 P2-1/P2-2）与 **S7 扩面 errata**（E-1 生产链 4 跳 / E-2 `TARGET_NOT_FOUND` 本地判定 / E-3 4B 实施顺序）属 **r2 后处置**：不改变 inventory 字节、不改变 pin、不改变方法名/返回类型/统计。它们另记于 4A 卡正文，待 4B 释放前由一次 r3 窄复核覆盖。**C-07 v1.9 重冻所依赖的字节/pin/门禁条件已由 r2 实测满足。**

## 7. 不构成什么

- 不构成 `ListPageRegionTextsAsync` 的实现授权（实现按 C-11 选候选、建 Task、独立 Review）；
- 不构成统计 80/87 的已达成声明（**当前仍是 79/86**）；
- 不构成 `FEA-06` AC3 的状态变更（仍为 **PARTIAL**，直到 4B 集成验证通过）；
- 不构成远端 push 授权；
- 不构成 FEA-15 正式验收。
