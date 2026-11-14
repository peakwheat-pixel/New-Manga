---
task: FEA-06-RESIDUAL-4B
task_id: FEA-06-RESIDUAL-4B
reviewer: independent sub-agent (v1.10 r1, read-only, not involved in implementation or r1-r4 of 4A)
reviewer_kind: subagent
base_commit: fd4008ce3
reviewed_head: 5c84dc22f
verdict: approved
date: 2026-11-14
p0: 0
p1: 0
p2: 0
p3: 6
---

# C-07 UNFREEZE v1.10 独立字节级复核 r1（4B 批次）

## 0. 结论

**`approved`。P0 = 0，P1 = 0，P2 = 0，P3 = 6（登记，不阻断）。**

被审范围两段：`fd4008ce3..ba6136d0`（9 文件 / +363 / −34，C-07 统计翻 `79/86 → 80/87`、pin 重算 v1.10、新载体）与 `ba6136d0..5c84dc22f`（3 文件，关闭 4A r4 的 P2-1 并清理旧路径字面）。审查起始与结束时 `git status --porcelain` 均为**空**，`HEAD = 5c84dc22fd82ace475ba0fdbc97883d3bf0807e9`；未发现需要「工作树 dirty」免责声明的情形。

**硬结论**：pin 三口径同一个值 `498882eb…6984f`；v1.9 原值 `91e51ab7…6d750` 原值保留且可从 `git show ba6136d0^` 精确复现；正式成员表 84 行（80 方法 + 4 非方法成员）**逐行**等于源码解析结果（`ALL_MATCH` ×3，合计 87）；`IHostController.cs` 的旧 79 个成员行在 C-07 表中**逐字节 0 改动**，新增行确实是唯一插入（纯 append，无隐式重编号）；`fd4008ce3` 的红窗在三个位置如实登记且经 blob 复算证实**只存在一个 commit**；四项门禁（`check.ps1` ×3、`verify_pins`、`--check`）复跑全 `EXIT=0`。

**是否满足重冻 C-07 v1.10 的条件：满足。** 冻结条件①（独立字节级复核通过）已由本报告补足，②③④（生成脚本入库 / `--check` 绿 / `check.ps1` PASS）实测成立，pin 与字节自洽。§5 的 P3 六条均为记录/证据强度层面的登记项，不改变字节、不改变 pin、不阻断重冻。

## 1. pin 三口径

| # | 口径 | 命令 | 实测 | 结论 |
|---|---|---|---|---|
| 1 | 工作树文件 | `Get-FileHash -Algorithm SHA256 doc/plan/FEA-C07_API_INVENTORY.md` | `498882EB17507B89DB463EB7CC8EB4522AF80783A92BA21F80A5229C6D66984F` | **PASS** |
| 2 | `git blob`（LF 归一，按字节） | `git cat-file blob HEAD:doc/plan/FEA-C07_API_INVENTORY.md` → 原样字节算 SHA-256 | `498882eb17507b89db463eb7cc8eb4522af80783a92ba21f80a5229c6d66984f`（13,578 B，CR 字节数 **0**，即 LF） | **PASS** |
| 3 | 冻结记录 §1 置顶 pin | `doc/plan/FEA-CONTRACT-FROZEN-C07.md:15`「sha256（冻结后最终字节）」 | `498882eb17507b89db463eb7cc8eb4522af80783a92ba21f80a5229c6d66984f`（v1.10） | **PASS** |
| 4 | v1.9 原值保留 | 冻结记录 `:16`「前一 pin（v1.9，保留原值）」 | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750` | **PASS**（原值，未替换） |
| 5 | v1.9 可复现 | `git show ba6136d0^:doc/plan/FEA-C07_API_INVENTORY.md` → 字节算 SHA-256 | `91e51ab74da201b99b6704e49fca96e93657d869dcc1e9523661dbb299c6d750`（13,040 B） | **PASS** |

- 三口径**同一个值**，不存在「冻结记录写 A、文件是 B」的漂移；v1.9 与 v1.8 及更早的 pin 链在 §1 逐行保留（`:16`–`:24`）。
- 本工作树文件与 blob 均为 LF（CR = 0），故 `--check`、`verify_pins` 与人工复算口径一致。**限制**：`.gitattributes` 仍无 `doc/plan/*.md text eol=lf`，而 `core.autocrlf=true` ⇒ fresh clone 的 **worktree 哈希口径**可能变 CRLF（blob 口径不受影响）。该债由 v1.9 载体 §4 第 4 条登记，非本批引入，见 P3-5。

## 2. 成员表逐行 = 源码（独立解析，不采信生成器自述）

方法：自写解析器（去注释 → 按 `public interface` 定位花括号体 → 括号/泛型/花括号三深度归零时切分声明 → 区分 method 与 property/event），分别解析 `IHostController.cs` 与 `RunContracts.cs`，再解析 C-07 文档 `## <接口>` 下的成员表行，按 **(序号, 名称, 返回类型)** 三元组**逐行、按顺序**比较。

| 接口 | 源码方法数 | 文档方法行 | 源码非方法成员 | 文档非方法行 | 逐行比较 |
|---|---|---|---|---|---|
| IReaderProgressSink | 1 | 1 | 0 | 0 | **ALL_MATCH** |
| IHostController | **80** | **80** | **4** | **4** | **ALL_MATCH**（84 行） |
| IRunController | 6 | 6 | 0 | 0 | **ALL_MATCH** |

- 合计 = 1 + 80 + 6 = **87**；`IHostController` = **80**，与文档统计表 `:20`–`:22` 的 `80` / `**87**` 一致。
- 第 **#80** 行 = `ListPageRegionTextsAsync` / `Task<RegionPageTextProjection?>`，且它是接口中**最后一个**方法声明（`IHostController.cs:557`，`}` 在 `:561`）。
- 4 个非方法成员（`Snapshot` / `StartRequests` / `ExportDirectorySuggestion` / `Changed`）名称、类型、相对顺序均一致。
- `python tools/generate_api_inventory.py --check` → **EXIT=0**，`OK: rendered counts match FEA-C07 doc`（stderr）；生成器 stdout 的 `1/80/6 = 87` 与我的独立解析逐行相同——两套实现互证，不是「同源自证」。

## 3. 「接口末尾」决定：纯 append 是否属实，以及是否该记 P2

**3.1 纯 append 属实（字节级）。**

| 检查 | 结果 |
|---|---|
| `git diff --numstat fd4008ce3 ba6136d0 -- doc/plan/FEA-C07_API_INVENTORY.md` | `13 12`（+13 / −12，与载体 §1 差异指纹声明一致） |
| 成员表旧 79 个方法行是否被改写 | **0 / 79 行变更**（逐行 `-ceq` 全等比较） |
| 新增行位置 | 唯一插入点在**新表第 82 行**，即 `| 79 |` 之后、4 个 `| — |` 非方法行之前 ⇒ 序号 **#80** |
| 隐式重编号 | **无**：旧表 85 行（表头 + 分隔 + 79 方法 + 4 非方法）是新表 86 行的**顺序子序列**（byte-identical），差值恰为 1 行 |
| 旧行改写范围 | 仅 12 行非成员文本被改写：状态行、生成日期行、统计 2 行、变更类别行、「RO-1 计划追加」标题/导语/口径 2 行、§关系 2 条 bullet——**全部**已被载体 §1 差异指纹 ①–⑥ 枚举，改 12 + 增 13 = numstat 精确吻合，无未披露改动 |

**3.2 该决定是怎么落地的（同一 commit 内移了源码位置）。** `fd4008ce3` 的 `IHostController.cs` 把该方法放在 `LoadPageRegionsAsync`（`#34`）之后，解析序号是 **#35**（r4 §3.7 亦实测到 #35）；`ba6136d0` 把该声明块从 `:264` 处删除并追加到接口末尾（+3 行说明注释，`IHostController.cs:544-560`）。即：**「纯 append」是通过调整 C# 声明顺序换来的，不是靠改写文档换来的**。这一点在三个位置披露：声明处注释（`IHostController.cs:553-555`）、载体 §2 第 4 条、冻结记录 §3「RO-1」bullet。

**3.3 判断：正当，不记 P2（登记 P3-3）。** 理由逐条：

1. C# 接口**成员声明顺序无语义**（不参与 ABI、不影响实现者与调用方），移动不改变任何签名，也不改变 `Contract` 面；载体 §1「旧成员 / 旧签名零改动」的表述因此仍然为真。
2. 位置不是任意选择：v1.9 预授权已把落地行号**写死为 #80**。若按逻辑相邻插入（`LoadPageRegionsAsync` 之后），该行变 #35 并把 35–79 共 **45 行**全部重编号——那既与预授权判据冲突，也会让冻结契约产生 45 行无意义 churn。历史先例（v1.7 / v1.8）确实做过「插入 + 整体重建成员表 + 行号变动」，本次刻意不再重复。
3. 代价是真实的但有限：`ListPageRegionTextsAsync` 与其最相关的 `LoadPageRegionsAsync` 相距 46 行，破坏 Region 读族的局部聚集。可读性由三处锚点补偿（代码注释 / 载体 / 冻结记录），读者不会把它读成「无关追加」。
4. 没有任何迹象表明该移动是为了让数字好看而回避实质：文档新增行内容（名称、返回类型）与源码逐字一致，且预授权本来就给出 #80。

结论：**不损害到应记 P2 的程度**；作为 P3-3 登记「可读性折衷 + 若将来有机会重排契约应一次性归位」。

## 4. 中间态登记是否充分（`fd4008ce3` 的红窗）

先独立复算红窗边界（不改工作区，直接从 git blob 取三份源码与三份文档字节，用 §2 同一解析器复算计数）：

| commit | 源码解析 | 文档统计 | `--check` 应得 |
|---|---|---|---|
| `fd4008ce3^`（4B-2 之前） | 1 / **79** / 6 = 86 | 1 / 79 / 6 = **86** | **GREEN** |
| `fd4008ce3`（4B-2 端口） | 1 / **80** / 6 = 87 | 1 / 79 / 6 = **86** | **RED（EXIT=1）** |
| `ba6136d0`（4B-2b） | 1 / **80** / 6 = 87 | 1 / **80** / 6 = **87** | **GREEN** |
| `HEAD` | 1 / 80 / 6 = 87 | 1 / 80 / 6 = 87 | **GREEN** |

⇒ 红窗**恰好只有 `fd4008ce3` 一个 commit**，前后皆绿。三处登记逐条核对：

| 位置 | 登记要点 | 与实测一致性 |
|---|---|---|
| `doc/tasks/FEA-06-RESIDUAL-4B.md` §「切片执行记录」→ 4B-2 → **中间态登记（重要）** | `--check` **EXIT=1**（`FAIL: IHostController: rendered 80 not in doc`；stdout `80/87` vs 文档 `79/86`）；原因「统计翻转被排到最后一刀」；**已由 4B-2b 原子闭合**，红窗仅在历史 commit `fd4008ce3` | **PASS**（EXIT/差异/归因/边界全部与复算一致） |
| 载体 §4 第 7 条 | 「4B 第二刀 `fd4008ce3` 提交时 `--check` 曾红（stdout 80/87 vs doc 79/86）；本 commit 原子补齐，红窗仅存在于该历史 commit，现网已绿」 | **PASS**（「现网已绿」在 HEAD 实测成立） |
| 冻结记录 §5 `:102` | 「同批登记 `fd4008ce3`（4B-2 端口代码）曾使 `--check` 因统计未跟上而 EXIT=1，本 commit 原子补齐」 | **PASS** |

- **没有**任何一处把该历史状态说成「当时基线正常」；也**没有**反向掩盖（即没有把当前绿说成红——这正是 4A r1 曾出现的 P1 假陈述类型，本批未复现）。
- 4B 卡同时诚实写了「四件套中 3 项绿」（红项即 inventory `--check`），未把红项算进绿项。**结论：登记充分，PASS。**

## 5. 载体 §3 判据逐条兑现

| # | 判据 | 实测证据 | 结论 |
|---|---|---|---|
| 1 | `IHostController` 含 `Task<RegionPageTextProjection?> ListPageRegionTextsAsync(string pageId, IReadOnlyList<string>? regionIds = null, CancellationToken)`，无 `expected_revision` | `IHostController.cs:557-560` 逐字一致（`regionIds` 默认 `null`、`CancellationToken ... = default`）；接口内**无** `expectedRevision` 形参（声明注释 `:549-552` 明写「命令本身无 revision guard，故不暴露」） | **PASS** |
| 2 | 生产三处 + Null/Fake 实现，未就绪/失败一律 `null` | `HostController.cs:1005-1029`（空 pageId / runtime 未就绪 / `IsUiFacingFailure` → `null`）；`NewManga.Host/HostRuntime.cs:848-866`（`_readerIoGate.WaitAsync` + `CoreService ?? throw NotReady()`，typed 抛错由控制器降级为 `null`）；`NullHostController.cs:181-186`（恒 `null`）；`FakeHostController.cs:1208-1218`（未设置 → `null` + 调用日志） | **PASS** |
| 3 | 重跑脚本、并入 **#80**、统计 **80/87**、`--check` EXIT 0 | 实测 stdout `1/80/6 = 87`；`--check` **EXIT=0**、`OK: rendered counts match FEA-C07 doc` | **PASS** |
| 4 | 成员表逐行 = stdout（不只看计数） | 独立解析结果 §2：三接口 `ALL_MATCH`，`IHostController` 84 行 = 80 + 4 | **PASS** |
| 5 | pin 重算 v1.10、v1.9 原值保留 | §1 第 3/4 行 | **PASS** |
| 6 | 独立字节级复核 + 重冻 | 载体 §6 = `pending`，写明「由复核者追写、实现者不得代写 approved」，**未预写 approved**；冻结记录 §1B `:33` 与 §2 条件 1 `:43` 同样记 `pending` | **PASS**（本次即为该 pending 的兑现） |

**「无新 wire 码 / 无 schema 变更」**：`list_page_region_texts` 在 4B 之前**已存在**——Core `src/bootstrap/core_service.py:3533 / 7787 / 7796`、客户端注册表 `HostCommandRegistry.cs:191 / 357 / 465`、分发 `HostCommandDispatcher.cs:868`、解析器 `RegionTextProjection.cs`（`652580152` 时即有）；`eae0eb67a^..HEAD` 与 `fd4008ce3..5c84dc22f` 对 `HostCommandRegistry|HostCommandDispatcher|schema|*.json|python/` 的命中数均为 **0**。⇒ 本批只做了「既有命令的 App 端口暴露」，**无新 wire 码、无 schema 变更**（**PASS**）。

## 6. `5c84dc22f` 是否关闭 4A r4 的 P2

| 检查项 | 实测 | 结论 |
|---|---|---|
| README AC1 改 `MET` | `verification/FEA-06-RESIDUAL-4A/README.md:13` = **MET**：规格 v1.1 定稿 + scope review 形式要件由 r2+r3 替代 | **PASS** |
| README AC2 改 `MET` | `:14` = **MET**：计划节 + `ALL_MATCH: True` + `79/86` 为 4A 时值 + 80/87 归 4B | **PASS** |
| 与卡面 AC1 一致（不再反向陈旧） | 4A 卡 `:59` = `[x]` + `<<MET: … 按 DSH 依 r3 F-9 建议作出的裁决，由 r2+r3 两轮独立字节级复核替代>>`；README 与卡面同一实质、同一结论 | **PASS**（r4 P2-1 关闭） |
| E-1 更正注记不再含旧路径字面 | `doc/tasks/FEA-06-RESIDUAL-4A.md:234` 已改为「本节初稿写成了不存在的子路径，已改」；对 4A 卡与 README 全文检索 `App/Services/HostRuntime.cs` ⇒ **0 命中** | **PASS**（r4 P3-1 亦关闭） |

残余（登记为 P3，不阻断）：4A 卡 AC2–AC4 仍是 `[ ]` + `<<PARTIAL/PENDING>>`（卡首 `:58` 明示这些标记是**起草时**状态、由 DSH 收口更新；与 README 的差异属 r4 已接受的 P3-2 同类）；README `:14` 的「统计维持 `79 / 86` = 代码实测」与 `:63` 的「统计 80/87 NOT_DONE」在 `ba6136d0` 之后已成历史值；`:39` 的 `PLAN 6954 B / 8 个非终态`、`:44` 的 `1/79/6 = 86` 亦为旧值（详见 P3-1）。

## 7. 越界

| 范围 | 文件清单 | 数量/规模 | 结论 |
|---|---|---|---|
| `fd4008ce3..ba6136d0` | `IHostController.cs`、`FEA-C07_API_INVENTORY.md`、`FEA-CONTRACT-FROZEN-C07.md`、`CONTRACT-UNFREEZE-2026-11-14-C07-4B.md`（新增）、`FEA-06-RESIDUAL-4B.md`、`verification/FEA-06-RESIDUAL-4B/logs/{api-inventory,gates-2026-11-14-4b2b,member-table-eq-stdout,pin-before-after}.log`（新增） | **9 文件 / +363 / −34** | **PASS**（与任务描述完全一致，无额外路径） |
| `ba6136d0..5c84dc22f` | `doc/tasks/FEA-06-RESIDUAL-4A.md`、`verification/FEA-06-RESIDUAL-4A/README.md`、`doc/reviews/FEA-06-RESIDUAL-4A-r4.md`（新增） | **3 文件 / +292 / −4** | **PASS** |
| 测试改动 | 两段范围对 `tests/**`、`apps/**/tests/**` 的命中数 | **0 / 0** | **PASS**（本批未改测试） |
| 其他面 | `python/`、`HostCommandRegistry`、`HostCommandDispatcher`、schema/JSON、`.gitattributes`、其余 17 个 pin 文件 | 两段范围命中数 **0** | **PASS** |

## 8. 门禁复跑（真实输出 + EXIT）

工作目录 `G:\CODEX\New Manga`，`HEAD = 5c84dc22f`，工作树 clean。

**① `pwsh -NoProfile -File tools/governance/check.ps1`**

```
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\MAINT-1-RELEASE-MONITOR.md
WARN: 存在 9 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3177 bytes / 32 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：6980 bytes / 64 lines
Governance check: PASS (3 warnings)
EXIT=0
```

**② `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4B.md`** → `Task: doc\tasks\FEA-06-RESIDUAL-4B.md`，同 3 条 WARN，`Governance check: PASS (3 warnings)`，**EXIT=0**

**③ `check.ps1 -TaskPath doc/tasks/FEA-06-RESIDUAL-4A.md`** → `Task: doc\tasks\FEA-06-RESIDUAL-4A.md`，同 3 条 WARN，`Governance check: PASS (3 warnings)`，**EXIT=0**

**④ `pwsh -NoProfile -File tools/governance/verify_pins.ps1`**

```
OK C01b 3c9f5af7d74f
OK C02 bb365ca891a7
OK C03 b77e7968a00b
OK C04b 4b304c0c315f
OK C05 f6e6f3cb1fe1
OK C06 75f8e2b4eb80
OK C07 498882eb1750
OK C08 453f993c1a16
OK C09 dc51226b336c
OK C10 ec8fd862f95f
OK C11 44f4273f7ad1
OK C12 f49835860143
OK C13 8faf1e805eac
OK C14 05056cbf65f9
OK C15 f9e376a0ed4c
OK C16 67286eeca8cb
OK C17 cdeee4872e29
OK FEA01 0370c18932b1
PIN AUDIT: PASS (all 18)
EXIT=0
```

C07 = **`498882eb1750`（v1.10 新 pin）**，其余 17 pins 与 r4 记录逐项相同。

**⑤ `python tools/generate_api_inventory.py --check`**

```
OK: rendered counts match FEA-C07 doc
| 6 | `RetryFailedTargetsAsync` | `Task<RunControlInfo?>` |

EXIT=0
```

（stdout 计数 `IReaderProgressSink 1 / IHostController 80 / IRunController 6 = 87`，与 §2 逐行结果一致。）

## 9. 问题清单

### P0 / P1 / P2

**无（0 / 0 / 0）。** 未发现破坏冻结字节、假陈述、或需要返修才能重冻的问题。

### P3（6 项，登记）

**P3-1｜4A 证据 README 的 4B 前置数值未随 `5c84dc22f` 同步（反向陈旧，非本批 C-07 面）**

- `verification/FEA-06-RESIDUAL-4A/README.md:14` 写「统计维持 `79 / 86` = 代码实测」；`:63` 写「统计 80/87 **NOT_DONE**……属 4B 落地（pin v1.10）」；`:39` 写 `PLAN` 6954 B / 8 个非终态（`check.ps1` 实测 6,980 B / 9）；`:44` 写 `1/79/6 = 86`。在 `ba6136d0` 之后这些数字已是历史值。
- 判 P3 而非 P2：三条陈旧行**自带归属**（「属 4B 落地（pin v1.10）」），不构成「把已做说成未做」的形式要件互斥（r4 的 P2-1 是 AC1 的**形式要件**本身两种状态，性质不同）；且 4A 证据 README 不参与任何 C-07 重冻条件。
- 建议：4A 收口时一次性把 AC2 数值、`:39`、`:44`、`:63` 同步到 v1.10 口径（`80/87`、`PLAN 6980 B / 9`）。

**P3-2｜构建/测试证据强度不足：`gates-2026-11-14-4b2b.log` §5 只有「0 个错误」+ 1.32 s**

- 该日志 §5 = `0 个错误`、`已用时间 00:00:01.32`（增量无编译特征），无 warning 计数；§6 只含 `ListPageRegionTextsPortTests` 8/8。
- 而载体 §4 第 6 条声称「`dotnet build NewManga.sln` **0 error / 0 warning**；App.Tests 897/0/11、Host.Tests 321/0/74、CoreClient.Tests 176/0/24」——这三组数字在该日志内**不可独立复现**。属证据不足而非陈述为假（构建/测试不在本批必需门禁内，我未重跑 `dotnet`）。
- 建议：补一次 `dotnet build --no-incremental`（或 `-t:Rebuild`）与三条 `dotnet test` 的原始 stdout 到同一日志。

**P3-3｜「接口末尾」的可读性折衷**

- 见 §3.3：正确且必要（预授权 #80 + 避免 45 行重编号），但 `ListPageRegionTextsAsync` 与 `LoadPageRegionsAsync` 相距 46 行，Region 读族被打散。有注释/载体/冻结记录三处锚点，故不记 P2。建议若将来允许再改契约，一次性把该成员归位并承担一次重编号。

**P3-4｜4A README AC1 的裁决主体表述与卡面仍差半格**

- README `:13` 写「按 **r3 F-9 裁决**」；卡面 `:59` 已改为「按 **DSH 依 r3 F-9 建议作出的裁决**」。r4 P3-3 只被半关闭（卡面修、README 未修）；数值与结论无差异。

**P3-5｜`.gitattributes` 仍缺 `doc/plan/*.md text eol=lf`（既有债，v1.9 已登记，本批复述）**

- `core.autocrlf=true` 且无对应 eol 规则 ⇒ fresh clone 的 **worktree** 口径可能变 CRLF，届时「工作树 SHA-256」口径不可复现；**blob（LF）口径不受影响**，本工作树与 blob 实测均 LF（CR=0）。该文件不在 4B `allowed_paths`，交 DSH 处置。

**P3-6｜载体 §1 差异指纹把状态行/生成日期行描述为「行内追加」，实为行内改写字句**

- 两行是「删一句 + 写一句」（如「v1.9（RO-1 预授权，尚未落地）」→「v1.9（RO-1 预授权）→ v1.10（4B 落地）」），净效果与 +13/−12 总数吻合、六类枚举完备，措辞「追加」偏乐观。建议今后写作「行内改写」。

## 10. 复核边界

- 本报告只判 `fd4008ce3..ba6136d0` 与 `ba6136d0..5c84dc22f` 的**已提交字节**与记录链；未 checkout、未 commit、未 push、未修改任何既有文件；唯一新建文件即本报告。
- 不构成对「查看对照」UI（4B-3/4B-4、AC3–AC5）的验收，不构成 `FEA-06` AC3 的状态变更（仍 **PARTIAL**），不构成远端 push 授权，不构成 FEA-15 正式验收。
- 审查者未参与 4B 的实现或写作，也未参与 4A 的 r1–r4 复核；与产出这些变更的会话无上下文重叠。

## 11. 重冻处置建议（供 DSH）

1. 在载体 §6 回填本 r1 结论（`approved` / P0=0 / P1=0 / P2=0 / P3=6 / 被审 head `5c84dc22f`）；
2. 冻结记录 §1B `:33`、§2 条件 1 `:43` 把 `v1.10 pending` 改为「r1 `approved`，已重冻」；§5 追加 v1.10 重冻行；
3. pin **不需要重算**（本报告未改 `doc/plan/FEA-C07_API_INVENTORY.md` 任何字节，`498882eb…` 仍为当前文件哈希）；
4. P3-2（构建/测试日志）与 P3-1（4A README 数值）建议随 4B 收口一并补，不阻断重冻。
