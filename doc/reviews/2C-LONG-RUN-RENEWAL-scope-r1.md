---
task: FEA-11-2C-LONG-RUN-RENEWAL-1
title: 2C 长 Run 续期（L-G1：>300s referenced Run 失权）权威 scope review r1
reviewer: fresh subagent（独立上下文；未参与 RUN-GRANT-1/2A/2B/2C 线、L-S1/L-S4 线、RENDITION/Flux/Read 线的实现、返修或审查；只读被审 head）
session: 857903ae-5c63-44ae-a37b-9e4472486829（`$DSH_SESSION_ID` 实测；以 Lead 记录为准）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 scope review（fresh context / read-only / 非作者 / 非实现审查者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 0bf90fc5bff7a29b4312ac60403e7b82d3f19ef2
reviewed_head_note: >-
  实测 HEAD 与任务书 `0bf90fc5b` 一致；评审起点 `git status --porcelain` 为空，结束时仅本报告未跟踪。
  `fad1ec776..HEAD`（L-S4-B-2 delivery 之后）对 `apps/`、`src/`、`tests/` **零 diff**；`313f88905..HEAD`
  仅 `doc/**`。因此本报告的 Run 授权行为事实 = 2A/2B 之后的最新代码字节，不是旧快照。
verdict: READY-WITH-UNFREEZE
verdict_scope: >-
  推荐方案 = **Host 侧在 Run 非终态期间对同一冻结 `{command, scope}` 周期性重铸 grant + 重发
  `AuthorizeSourceReadForRun`**（零 Core 改动、零 Run wire 改动、零新命令/能力/错误码）。
  严格读冻结字节（C-06:43「Run dispatch 前」、C-16:78「用途（冻结）」、C-16:91 单次原子副作用）
  时，mid-run 重复调用**不在**冻结语义内 ⇒ **需 C-06 v1.2→v1.3 + C-16 v1.5→v1.6 两 pin UNFREEZE**
  （其余 16/18 不变），按本仓先例走载体 + 独立 byte-level 复核 + 重冻重算 pin。若 DSH 裁定
  「§2.4 重复调用属既有集合语义」，可 0 pin，但必须在卡/载体/Handoff 记录该解释——本报告不推荐
  该路径（它把「dispatch 前」降级为叙述性文字，后续无法用契约字节阻止真正的放宽）。
  拆卡建议：有 UNFREEZE 时拆 **PREREQ-1（契约澄清）+ 实现卡**；0-pin 裁定时单卡。
---

# 2C 长 Run 续期（L-G1）· 权威 scope review r1

> **结论先行。**
>
> 1. **缺口成立，且比既有登记更宽。** L-G1 现有口径只写「窗口后**提交单元** fail-closed」。实测还有两处：
>    (a) **读图步骤先失败**——referenced 页的 provider 读（det/ocr/translate-context）在 grant 过期后
>    直接 typed `PROVIDER_FAILED`（`core_assembly.py:444-501` → `resolve.py:47-90` →
>    `source_read_refs.py:738-771`/`:855-880` → `infrastructure/pipeline/executor.py:38-39`）；
>    (b) **窗口锚点是 dispatch，不是执行开始**——grant 在 4 个 Run 命令 dispatch 前一次性铸出
>    （`HostCommandDispatcher.cs:74-83`/`:147-158`；`SourceReadCoordinator.cs:286-291`/`:586`），
>    而 Run 由 Core 单线程 scheduler 串行执行（`core_service.py:1277-1319`；`tasks/service.py:1020-1169`、
>    `:1632-1655`），**排队中的 Run 可能在还没跑第一步时就已失权**。
> 2. **全仓不存在任何续期机制。** `AuthorizeRunAsync`（`SourceReadCoordinator.cs:260`）是 Run 侧唯一
>    mint 入口，只在 dispatch 前调用；Host 没有与 source-read grant 相关的 timer/loop（周期扫描器
>    `SourceScanScheduler` 只铸不绑、不参与 Run）；Core 侧 `_checked` 只做过期判定
>    （`source_read_refs.py:855-880`）。窗口后无自动恢复；唯一恢复路径是**再发一条触发执行的 Run 命令**
>    （新窗口），失败 Run 不会被 scheduler 自动续跑。
> 3. **最小方案是 (a) Host 侧周期续期，不是 (b) 延长 TTL，也不是 (c) Core 滑动过期。** (a) 复用已冻结的
>    `RegisterSourceReadGrant` + `AuthorizeSourceReadForRun` + `GetRunSnapshot`，零 Core/零 wire/零新码，
>    且天然满足「Host 是唯一授予方」的方向裁决（C-16:19）。(b) 要改 C-06「≤300s」+ C-16「不延长」+
>    Core `now+300` 校验（`source_read_refs.py:179`）+ Host 常量（`SourceReadCoordinator.cs:586`），
>    仍不解决排队/无界运行；(c) 与「`expires_at` 参与签名」直接冲突（`source_read_refs.py:87-97`、
>    `:172-179`、`SourceReadCoordinator.cs:611-616`），等于 Host 重签，绕一圈回到 (a) 还多破一条不变量。
> 4. **UNFREEZE 判定：严格 2 pins（C-06 + C-16）；16/18 不变。** 依据：C-06 §2.2
>    「Run dispatch 前建立」（`:43`）、C-16 §2.4「用途（冻结）」与「原子性与副作用（冻结）」
>    （`:78`、`:91`）；重复调用是**第二次建立事件**（新 grant id、新请求），冻结字节未描述。
>    0-pin 需要 DSH 的语义解释裁决，且必须在卡/线圈留痕。
> 5. **拆卡：2 张（PREREQ-1 + 实现）**，与 `RUN-GRANT-1-PREREQ-1`、`2B-PREREQ-1` 先例一致；
>    若 DSH 采 0-pin 则单卡。不并入 B2/L-R11/folder/L-S4。
> 6. **测试可行，但 gated IPC 不能替代时间维判别。** Core 侧可用既有 fake clock 先例
>    （`tests/fea11/test_source_run_grant.py:698-716`）在**进程内真实装配**上判别 >300s；.NET gated IPC
>    里的 Core 是**真子进程**，无法前推其时钟，真实等 300s 不可接受 ⇒ gated 只判别「同 scope 二次
>    mint+bind+可读」，时间维由 in-process Python 测试承担。**不建议**为测试加 TTL 缩短 seam
>    （碰 mint 语义，见 §4.3/D-6）。
> 7. **优先级：2C 应作为下一条实现线（B2 继续延后）。** 它是当前队列里唯一「用户可见功能缺口
>    + 已有全部命令面」的项；成本=Host-only + 2 pins。L-R11/C-04b/SCAN-RH 可穿插，UI P3 最后。
> 8. **不夸大边界**：本卡最多关闭「多步长 Run 在续期窗口内可持续」，**不能**关闭「单步 >300s」
>    「续期失败」「加密源（L-G2）」「Core 重启（L-G9）」「viewer 无活跃 Run 时读引用页（L-R1 残余）」
>    「>4096 成员（L-G16）」。L-G1 应从「无续期」降级为「有续期但仍有子限制」，**不得**写成「L-G1 关闭」。

---

## 0. 只读基线与实测命令

| 项 | 值 | 来源/说明 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `0bf90fc5bff7a29b4312ac60403e7b82d3f19ef2` | `git log -1`（2026-11-07 17:34:46 +0800，docs-only） |
| 工作树 | 起点 **clean**；结束时仅本报告未跟踪 | `git status --porcelain`（起点 0 行） |
| `fad1ec776..HEAD` 生产/测试 diff | `apps/`、`src/`、`tests/` **空** | `git diff --name-only fad1ec776..HEAD -- apps src tests` 输出为空 |
| `313f88905..HEAD` diff | 仅 4 个 `doc/**` 文件 | 同上命令（无 `--` 过滤） |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0 | 实测；C06 `99831a20ffd6`、C16 `a7f57ebdbd67`、C17 `aefa0fa5b17e` |
| `check.ps1`（默认） | **PASS (3 warnings)**，EXIT=0 | 实测；3 warnings = 9 个非终态 Task + STATUS/PLAN 预算 80%；默认解析到 `doc\tasks\FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1.md` |
| 只读契约核对 | C-06 v1.2（`:39-56`、`:90-96`）；C-16 v1.5（`:8`、`:19`、`:22`、`:39-93`）；C-17（`:270`、`:279`、`:292`） | HEAD 字节实测 |
| 定向/全量测试 | **NOT_RUN** | 本会话硬约束「只允许写一个文件」；`dotnet test`/`pytest` 会写 `bin/obj`、`.pytest_cache`，全量 pytest 历史上还会改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`。本报告不声明任何测试 PASS。 |
| gated 真实 IPC | **NOT_RUN** | 同上；实现卡必须自行跑并入库 |
| 契约 byte-level 复核 | **NOT_RUN** | scope review 不做 byte-level；UNFREEZE 判定见 §2.3 |
| 真实用户数据 / AppData / 回收站 / push | **未触碰** | — |

> **基线口径提醒（冻结/释放时必须重测）**：`doc/STATUS.md:20` 仍写 pytest **3360/10**、.NET
> **1652/0/94**；L-S4-B-2 closeout 实跑为 pytest **3360/10**、.NET **1661/0/95**
> （`doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md:93`、`:143`）。实现卡不得继承任一旧数字，必须在
> clean head 重测并写「本卡起点」。另：`doc/REBASELINE_PLAN.md:53` 的 DAG 行仍含「B2（proposed）/
> 2C（Long Run）/ B2（proposed…）/ 2C（长 Run）」重复片段，属既有文档漂移（`check.ps1` 仍 PASS），
> 本卡不修（不在 allowed_paths；由 DSH closeout 统一维护）。

**既有依赖状态（读作「本卡的前置已完成」，不是本评审实测）**：

| 依赖 | 状态 | 对本卡的意义 |
|---|---|---|
| `FEA-11-RUN-GRANT-1`（`a11ded0d3`，r3 approved） | done；`AuthorizeSourceReadForRun` 已冻结并实现（C-16 §2.4） | 2C 的续期命令面**已经存在**，不需要新命令 |
| `FEA-11-RUN-GRANT-2A`（`a0bafc89e`，r1 approved） | done；生产 version 通道（`SourceIdentityCache`），禁止常量 `"1"` 回退 | 续期铸 grant 时 version 来自缓存，不需要重扫位 |
| `FEA-11-RUN-GRANT-2B-PREREQ-1`（C-16 v1.4）r **2** 窄面复审 **approved**（`doc/reviews/FEA-11-RUN-GRANT-2B-PREREQ-1-r2.md`） | done；C-16 现为 **v1.5**（含 §2.5 reattest，pin `a7f57ebdbd67`） | 续期只复用 §2/§2.4，v1.6 只追加重复调用句，不回退 v1.4/v1.5 任何语义 |
| `FEA-11-RUN-GRANT-2`（2B 实现）r1 **approved**（`doc/reviews/FEA-11-RUN-GRANT-2-r1.md`，P3×4 非阻断） | done；容器多成员 entry 通道 | 续期沿用同一 mint 路径（容器每 grant 只指纹一次），不新增 entry 语义 |
| `R3-02`（RUN-GRANT-1 r3 P3，`doc/reviews/FEA-11-RUN-GRANT-1-r3.md:253`） | **仍为 P3 非阻断**：`AcceptRunAsync` → seam 的委托行未被测试判别 | 与 2C 接线面相邻，可顺带关闭（D-9），否则保持登记 |


---

## 1. Q1 缺口核实

### 1.1 授权的生命周期锚点：dispatch 前一次，Run 异步整跑

| 事实 | 证据 |
|---|---|
| 只有 4 个 Run 命令触发预授权 | `HostCommandDispatcher.RunAuthorizationCommands`（`HostCommandDispatcher.cs:74-83`）；`RunCommandPolicy.TriggersStepExecution`（`HostRuntime.cs:1700-1712`，`library_control_run` 仅 `continue`/`restart`） |
| 钩子在 dispatch **之前**执行，Core 拒绝则命令不发送 | `HostCommandDispatcher.cs:147-158`（`throw` 出 try-block；Run 错误投影 `:175-178`） |
| 每轮 = 每 source 一个新 grant + 一次 `AuthorizeSourceReadForRun` | `HostRuntime.cs:2005-2071`（`AuthorizeSliceAsync`）；`SourceReadCoordinator.cs:276-291`（逐 source `IssueLockedAsync`）、`:310-319`（发送） |
| grant TTL 硬写 300s | `SourceReadCoordinator.cs:586`（`var expiry = _clock() + 300`）；Core 侧上限校验 `source_read_refs.py:179`（`expires_at > now + 300` → `SOURCE_GRANT_EXPIRED`） |
| Run 在 Core 后台线程整跑，Host 无 per-step 往返 | `core_service.py:1277-1319`（scheduler 线程 + `run_pending_once` 循环）；`tasks/service.py:1020-1169`（一个 `execute_run` 跑完全部 task/unit/step）；`:1632-1655`（`run_pending_once` 串行，一次跑完一个 Run 才返回） |
| Run wire 不含 grant/TTL，续期不需要改 Run wire | `RunContracts.cs:26-30`（`RunStartRequest{Command, Scope, Overrides, IdempotencyKey}`） |
| 无任何续期/刷新路径 | `SourceReadCoordinator.cs:260` 是 Run 侧唯一 mint 入口；`HostRuntime.cs:1523-1544` 只装配一次；全仓 `AuthorizeRunAsync` 调用点为 dispatcher 钩子与 AcceptRun seam（`HostRuntime.cs:101-114`、`:1476-1482`） |

**推论（决定影响面）**：300s 从**命令 dispatch 时刻**起算，而非 Run 真正开始执行。`run_pending_once`
一次只跑一个 Run（`:1632-1655`），所以第二个及以后的 pending Run 必须等前一个整跑完；
它们的 grant 在**尚未开始**时就已过期。**多 Run 连续排队是确定性失权，不是概率问题。**

### 1.2 >300s 的 Run 在哪一步失权

| # | 失权点 | 链路（path:line） | 用户看到的 typed 结果 |
|---|---|---|---|
| ① | **引用页读图**（det / ocr / translate-context） | `core_assembly.py:444-501`（`_referenced_page_image`）→ `resolve.py:47-90`（`prepare_referenced_rendition`）→ `source_read_refs.py:738-771`（`find_bound_for_source`；过期 grant 被 `:761-764` 吞掉）→ 无 live → `SOURCE_ACCESS_DENIED`（`:765-769`）→ `ProviderInputError`（`core_assembly.py:489-492`）→ `StepExecutionError("PROVIDER_FAILED")`（`infrastructure/pipeline/executor.py:38-39`） | 步骤/页失败 `PROVIDER_FAILED` |
| ② | **提交单元**（step commit） | `infrastructure/sqlite/pipeline.py:898-899`（`BEGIN IMMEDIATE` 后立即 `source_commit_guard`）→ `core_assembly.py:1757-1776`（`run_source_guard`，`:1773-1774` 同一个 `find_bound_for_source`）→ `SourceImportError` 逃出，被 `pipeline.py:1077-1080` 归 `db_failed` → `tasks/service.py:971`（`DB_FAILED`） | 步骤/页失败 `DB_FAILED`；候选按既有 `_reject_prepared` 标 `abandoned`（`pipeline.py:1242-1280`） |
| ③ | **容器重验**（不是独立失权点，但决定「重验救不了」） | `source_read_refs.py:294-303`：`commit_guard` 先 `_checked(grant_id)`（过期即 `SOURCE_GRANT_EXPIRED`/被上游吞成无 live），**然后**才 `source_lease(path, facts, …)` 做物理身份复核；读路径同理，`reader.py:50-114` 的 `read_verified_bytes(path, facts, …)` 只在 grant 已通过后执行 | 过期 → ①②；身份漂移 → `FILE_IDENTITY_CHANGED` 族（与 TTL 无关） |
| ④ | **恢复** | 无自动续期/自动重授权。窗口后唯一恢复=再发一条触发执行的命令（新 mint 窗口；`HostCommandDispatcher.cs:74-83`）。失败 Run 不会被 scheduler 自动续跑（`tasks/service.py:1632-1655` 只恢复 PENDING 与「RUNNING 且无 step 在跑」的中断态） | 需 `library_retry_failed_targets`（子 Run）或重发 Run |

**失败后的 Run 终态**：`task_failed` 只取消该 task 剩余 unit，其它 task 继续（`tasks/service.py:1140-1142`），
整 Run 聚合为 `COMPLETED_WITH_FAILURES`（`tasks/service.py:1521-1536`）。即：窗口前的页已提交并保留，
窗口后的页成批失败——不是「整章回滚」，也不是「静默放行」。

### 1.3 影响面

| 面 | 结论 | 依据 |
|---|---|---|
| **用户可见性** | **高**：长章节/多页 Run 在窗口后成批失败，工作台显示失败项，需要用户手动重试；已完成的页不会丢（不破坏数据） | §1.2；`tasks/service.py:1521-1536` |
| **频繁 Run** | 每条 Run 都在 dispatch 时铸一份新 grant（容器要整文件 sha256，`SourceReadCoordinator.cs:528`；folder 逐成员 `:541-581`）→ 频繁 Run 叠加 L-G8 的 mint I/O；续期若按周期做，会再放大（见 §2.1） | `SourceReadCoordinator.cs:498-620` |
| **长 Run** | 只要跨过 300s 就命中；多页章节的 det/ocr/translate 累计极易超过；**单步**（含 provider 重试）超过剩余窗口时，连第一步都可能提交失败 | §1.2 ①② |
| **排队 Run** | **确定性失权**：第二个 pending Run 尚未开始，其 grant 已过期 | `tasks/service.py:1632-1655` |
| **managed-only Run** | **不受影响**：`run_source_guard` 无 binding 直接放行（`core_assembly.py:1759-1762`）；provider 走 managed 分支（`:417-442`）。但 Host 仍会为 book 范围的知识源铸 grant（`HostRuntime.cs:1755-1845`），属既有 L-G8 成本，不是新缺口 | 同左 |
| **viewer / resolve 面** | 与 Run 共用同一 registry：`resolve_page_resource` 的 referenced 分支要求 live bound grant（`core_service.py:4467` handler；`:4505` pending gate；`:4506-4510` `prepare_referenced_rendition(access=registry)`；同一 `find_bound_for_source`）。窗口后从 UI 打开引用页同样会被拒 → **L-R1 残余**，不在本卡范围（本卡的续期只在 Run 存续期有效） | 既有登记；`core_service.py:4467`、`:4505-4510`；`source_read_refs.py:738-771` |

### 1.4 与既有登记口径的差异（必须写进实现卡）

`FEA-11-RUN-GRANT-1` r3 / 2A / 2B 的登记原文是「单 grant ≤300s；窗口后**提交单元** fail-closed（typed），
需重发 Run；续期未做」（`doc/handoffs/FEA-11-RUN-GRANT-2-018008989.md:54`；`FEA-11-RUN-GRANT-2A-a0bafc89e.md:57`）。
本次核实**确认**该结论，但需补两条：

1. **读图先于提交失败**（`PROVIDER_FAILED`），不是只有 `DB_FAILED`；
2. **窗口锚点 = dispatch**，因此**排队 Run 在开始前就失效**。

这两条直接影响 AC 的判别面（必须同时断言读与提交、必须覆盖「迟开始」的 Run），也使「续期启动时机」
不能挂在「Run 开始执行」上（Host 看不到执行开始），只能挂在「dispatch 成功 + `GetRunSnapshot` 状态」上。

---

## 2. Q2 最小方案

### 2.1 (a) Host 侧在 Run 生命周期内续期/重铸（**推荐**）

**形状**：新增 Host 后台 `RunGrantRenewal`（单 Run 单任务），在 4 个执行命令 **dispatch 成功**（拿到
`run_id`）且首轮 `bound_pages > 0` 时启动；每 tick：

1. `GetRunSnapshot(run_id)`（既有命令，`HostRuntime.cs:1487-1519` 已有同样读取）判终态/缺失；
2. 复用该 Run 的**冻结** `{command, scope}` 走同一「resolve → mint → `AuthorizeSourceReadForRun`」路径
   （`HostRuntime.cs:2005-2071` → `SourceReadCoordinator.cs:260-336`）→ 内部重新
   `RunSourceRange.Resolve`（`:1755-1845`）→ 逐 source `IssueLockedAsync`（**重新核验 facts**）→
   一次 `AuthorizeSourceReadForRun`（`SourceReadCoordinator.cs:310-319`）；
3. 记录 counts-only 日志；任何 typed 失败/全 skip → **停止续期，不重试**。

> **实现注意（本报告实测）**：现有 seam `RunSourceAuthorizer.AuthorizeSliceAsync` 返回 `Task`（void，
> 结果只写日志，`HostRuntime.cs:2005-2071`），而 `SourceReadCoordinator.AuthorizeRunAsync` 返回
> `RunAuthorizationResult{BoundPages, MintedGrants, SkippedSources, SkippedCodes}`
> （`SourceReadCoordinator.cs:39-47`、`:260-336`）。续期需要**读得到**这一结果（首轮触发条件、
> all-skip 停止、成本日志），所以实现卡必须让它可返回（例如让 `AuthorizeSliceAsync` 返回
> `RunAuthorizationResult?`，或在 `RunGrantRenewal` 内直接调 coordinator 的返回型方法）；
> **不得**改成「发了就算成功」。

**为什么它是最小**：

| 维度 | 说明 |
|---|---|
| Core 改动 | **0**（`RegisterSourceReadGrant`、`AuthorizeSourceReadForRun`、`GetRunSnapshot` 全部已冻结并已实现：`core_service.py:1485-1516`、`:4965-5069`、`:6181-6204`） |
| Run wire / 命令面 / 能力 / 错误码 | **0**（`RunContracts.cs:26-30`；`source.read.run/1` 已存在 `SourceReadCoordinator.cs:57`） |
| 契约 | 语义澄清 **2 pins**（见 §2.3）；不改任何字段/TTL/撤销/错误闭集 |
| 安全面 | 每轮重新走 `Registry.Authorize`（`SourceAccessRegistry.cs:62-70`：撤销→`SOURCE_GRANT_REVOKED`、generation→`SOURCE_REGISTRY_BUSY`）+ 物理 facts 重算（`SourceReadCoordinator.cs:517`、`:520`、`:528`、`:541-581`、`:584`），撤销/漂移自动停 |
| 失败语义 | best-effort（沿用 R1-01：Host 侧失败绝不阻断 dispatch）；续期失败只停止续期，Core 仍是 fail-closed 权威 |
| 不能解决 | 单步 >300s；续期本身失败；加密源（L-G2）；重启（L-G9）；viewer 无 Run（L-R1 残余） |

**实施要点（供实现卡）**：

- **run_id 捕获**：`AcceptRunAsync` 已有 frozen slice（`HostRuntime.cs:79-92`）；`library_start_run` 的
  run_id 只在 Core 响应里（`RunStartInfo`，`RunContracts.cs:33`）。最小接法有两种，需 DSH 选一：
  (i) `HostCommandDispatcher` 增加**可选 post-dispatch 回调**（`HostCommandDispatcher.cs` 属
  `NewManga.CoreClient`，改动是 Host 侧内部、无 wire 变化）；(ii) 在 `HostController.StartRunAsync`
  （`apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs:2270`）等 4 个调用点显式登记
  —— 会触 App 层，覆盖面也更容易漏。**推荐 (i)。**
- **冻结 scope 来源**：`library_start_run` 用请求 payload（`HostRuntime.cs:1958-1971` 已是同源）；
  `AcceptRun` 用 prepared slice；`library_control_run`/`resume_blocked_run`/`retry_failed_targets` 用
  `GetRunSnapshot`（`HostRuntime.cs:1473-1519` 现有路径）。**禁止**换 command/scope、禁止 `all` 之类扩大。
- **停止条件（全部 fail-closed，无重试）**：Run 终态/不存在；`source.read/1` 或 `source.read.run/1`
  能力缺失（`SourceReadCoordinator.cs:121-128`、`:240-244`）；Core typed 拒绝（含 `SOURCE_ACCESS_DENIED`/
  `SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_BUSY`）；全 source mint skip；
  Host 关闭/Host session 失效；用户撤销 roots。
- **成本控制**：`interval` 默认 **240s**（必须 `< 300 − 安全余量`；墙钟单源 mint 可能 >1s）；
  `maxRenewals` 默认 **12**（≈48 分钟）；只在 Run 存活期续；`TrackedPayloadCount` 上限 256 由既有
  `PruneExpired`（`SourceReadCoordinator.cs:415-443`）维持——续期会持续产生新 grant，必须断言不被击穿。
  `SourceIdentityCache` TTL = **3600s**（`SourceScanScheduler.cs:163`），240s×12 ≈ 48 分钟 < 1h，正常不会
  重新触发 on-demand 扫描；超过 1h 的 Run 可能遇到缓存过期 → 每轮最多 `MaxOnDemandScansPerSlice=8` 次
  扫描（`HostRuntime.cs:1890`）、每次 30s 超时（`:1893`），实现卡必须把它计入 interval 预算（超预算即
  跳过，不得让续期 tick 长期占住 mint gate）。

### 2.2 (b) 延长 TTL / (c) Core 滑动过期 / (d) 其他

| 方案 | 需要改什么 | 判定 | 理由 |
|---|---|---|---|
| **(b) 延长 TTL** | C-06 §2.2「短期（≤ 单次操作，≤300 秒）；不得作为长期通行证复用」（`FEA-C06_SOURCE_AUTH_DRAFT.md:40`）+ C-16 §2.4「不延长」（`FEA-C16_SOURCE_READ_WIRE_DRAFT.md:78`）+ C-16 §2 校验 `now+300`（`source_read_refs.py:179`）+ Host 常量（`SourceReadCoordinator.cs:586`）+ 安全论证 | **不推荐**（≥2 pins + Core 改动） | 仍是有界窗口（只是变长），排队/无界运行照样失效；且违背 C-06 §3.10「不得以 300 秒 TTL 代替即时撤销」的取向（`:71`）——窗口越长，失联/撤销失败的风险窗口越大 |
| **(c) Core 侧 sliding expiry** | 需破坏「`expires_at` 参与 HMAC 签名」（`source_read_refs.py:87-97`、`:172-179`、`SourceReadCoordinator.cs:611-616`）或让 Host 重签；另需 C-06/C-16 | **否决** | 语义上不成立：Core 无权延长自己没签的到期时间；「Core 滑动」= Host 重签 = (a)，还多破一条不变量 |
| **(d2) Core→Host「即将过期/请续期」协议** | 新反向通道 + 新命令/事件 + 能力 + C-16/C-17 | **否决（被冻结边界排除）** | C-16:8「**不新增 Core→Host 反向 RPC 通道**」、:19 方向裁决；且 Host 空闲时不消费 Core 事件（`CoreServiceClient.cs:1520-1529` 只在命令交换间隙跳过 event frame），事件驱动也不可靠 |
| **(d3) 把长 Run 拆成多个短 Run** | 改变 Run 计划/幂等/UI/进度语义 | **否决** | 成本远大于本缺口；破坏 Run 的原子进度与 `COMPLETED_WITH_FAILURES` 语义 |
| **(d4) 失败后引导重试（零代码/文档）** | 无 | **只能附带** | 不修复；但可作为 UI 文案（UI P3） |
| **(d5) 只对「仍有未终态目标页」的 Run 续期** | 需 `GetTaskProjection`（既有只读命令） | **可选优化** | 省 mint 成本；非必需，可作为实现卡的 P3 |

### 2.3 UNFREEZE 判定（严格）

| 冻结字节 | 现文 | 与 (a) 的冲突 |
|---|---|---|
| `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:43`（§2.2 授权建立行） | 「**在 Run dispatch 前**建立……该建立**不延长** ≤300s 有效期……」 | 只描述一次性 dispatch 前建立；mid-run 第二次建立未描述 |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:78`（§2.4 用途） | 「**用途（冻结）**：**Run dispatch 前**，把……建立为**本次 Run** 目标页……的读授权」 | 命令语义被限定在 dispatch 前 |
| `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:91`（原子性与副作用） | 「任一目标页不可授权→整体 typed……全部可授权→写入映射……**不延长 TTL、不撤销/复活 grant**；幂等：同请求重复执行返回同一结果」 | 只定义**单次**调用的原子副作用；续期是**不同请求**（新 grant ids），幂等条款不覆盖 |

**判定：严格读需 2 pins**（C-06 v1.2→v1.3 + C-16 v1.5→v1.6），其余 16/18 pins 不变。
建议的**最小澄清文本**（供 DSH 作为 UNFREEZE 载体基线；不改既有句、只追加）：

- C-06 §2.2 授权建立行**追加**：「在 Run **非终态**期间，Host 可对**同一冻结 `{command, scope}`** 重复执行
  该建立；每次建立**必须重新铸造**新的 source-read grant（各自 ≤300s，顺序重新核验 facts），
  不得延长既有 grant 的 `expires_at`、不得扩大 scope、不得在撤销后重建、不得改选 command/scope。」
- C-16 §2.4 用途句**追加**：「本命令**可**在该 Run 非终态期间对同一 `{command, scope}` 重复调用；
  每次调用只把**当次** live grants 绑定到仍可授权的目标页；不延长任何 grant 的 TTL、不改变 scope、
  不绕过撤销；任一目标页不可授权仍为整请求 typed 拒绝（零映射写入）。」

其余**零改动**：wire 字段/命令集/能力/错误闭集/`≤300s` 上限/撤销/失联/§7 脱敏/Run wire/
`PROTOCOL_MINOR=3`/schema/依赖。

**为什么不做 0-pin「解释性裁定」**：本仓对契约语义的审计粒度是 byte-level pin（v1.2 只新增条目即 2 pins；
v1.4 为一段语义即 1 pin + 独立复核，见 `doc/reviews/CONTRACT-UNFREEZE-2026-11-06-C06-C16.md`、
`...-2026-11-07-C16.md`）。把「dispatch 前」解释成叙述性文字，会让后续「续期=重复调用」与
「续期=持续授权」失去字节级边界，且实现卡无法在 Review 里自证不违反冻结文本。若 DSH 仍采 0-pin，
必须在卡/Handoff/Review 三处留同一句解释，并明确「本解释不改变冻结字节，不构成先例放宽」。

**零契约不可行性**：即使 DSH 采 0-pin，也**必须**有一句卡片级语义裁决——否则实现卡无法区分
「合规的续期」与「违反 §2.4 用途的一次性要求」。因此本报告不接受「什么都不写、直接实现」的路径。

### 2.4 红线（实现卡 AC 必须逐条可判别）

| # | 红线 | 判别方式 |
|---|---|---|
| R-1 | **不得延长单 grant**：每次续期必须新 grant、新 `expires_at ≤300s`；禁改 Core `now+300` 与 Host `+300` 常量 | 断言新 grant id ≠ 旧、`expires_at` 由本 tick 计算；`git diff` 不得触 `source_read_refs.py`/`+300` 常量 |
| R-2 | **不得放宽 identity**：每轮必须重走 `Registry.Authorize` + 物理 facts 重算（容器 sha256 / folder 逐成员），禁止复用旧 facts 跳过校验 | 删除 facts 重算 → 判别用例红（D2） |
| R-3 | **不得绕过撤销**：registry revoked/generation+1 后必须 typed 停止；禁止重试、禁止 `ReattestSourceLocation`、禁止用旧条目重建 | 撤销后断言零新 grant 帧、零 reattest 帧 |
| R-4 | **不得扩大 scope / 新增 source**：只允许该 Run 冻结的 `{command, scope}`；禁止改选命令、禁止 `all`、禁止把新扫描到的 source 注入 | scope 替换 → 判别用例红（D3） |
| R-5 | **不得把续期失败变成放行**：续期失败仅停止续期，Run 仍由 Core fail-closed | 续期失败后断言 Run 命令不被预授权放行 |
| R-6 | **不得自动重新授权已撤销/已失败 source** | 断言不调用 B1 恢复/reattest 路径；不产生新 Run |
| R-7 | **不得新增 Run 面错误码 / wire 字段 / 能力 / `PROTOCOL_MINOR`** | scope diff + API inventory + C16/C17 blob 零漂移 |
| R-8 | **不得阻塞请求线程 / 不得成为新授权入口**：续期只在后台、只对已 dispatch 的 Run，不受理新 scope | 单测断言 renewal 不在 dispatch 路径上同步等待；新 scope 请求无入口 |
| R-9 | **不得宣称任意长 Run 可用** | 卡/Handoff/EV 措辞检查（§1.4 子限制必须保留） |
| R-10 | **不得以续期替代撤销/失联**：Core 断连/EOF 仍全局失效 | 既有 `revoke_all_for_session`/`_disconnected` 语义不改（`source_read_refs.py:253-271`、`:855-880`） |

---

## 3. Q3 拆卡与范围

### 3.1 单卡 / 拆卡

| 选项 | 判定 | 理由 |
|---|---|---|
| **拆 2 张：PREREQ-1（契约澄清）+ 实现卡** | **推荐（2-pin 方案下）** | 契约字节必须先重冻，实现卡才能在「不违反冻结字节」的前提下被审查；仓内先例：`FEA-11-RUN-GRANT-1-PREREQ-1`（2 pins）、`FEA-11-RUN-GRANT-2B-PREREQ-1`（1 pin）。PREREQ 卡只做 C-06/C-16 两句 + 冻结记录/矩阵/载体 + pin 重算 + 独立 byte-level 复核 |
| 单卡（Host-only） | 仅当 DSH 采 0-pin 裁定 | 否则实现与语义澄清混在一张卡，Review 无法区分「实现 correct」与「契约就绪」 |
| 并入 B2 / L-R11 / folder / L-S4 | **禁止** | B2 无消费者；L-R11 是 gate 一致性（`FEA-C16:93` 明确本命令不引入第三套 gate）；folder/容器成员是 2B 已交付面；均无共享写域 |

**命名**：任务书建议 `FEA-11-2C-LONG-RUN-RENEWAL-1`；仓内 handoff 已多次写 `FEA-11-RUN-GRANT-2C`
（`FEA-11-RUN-GRANT-2A-a0bafc89e.md:80`、`FEA-11-RUN-GRANT-2-018008989.md:77`、
`FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-0ebb234bf.md:83`）。**两个名字不得并存建卡**——DSH 二选一，
本报告的 requirement 不变（建议沿用 `FEA-11-RUN-GRANT-2C` 以保持 RUN-GRANT 血统；若用任务书 id，
在卡 `aliases` 里登记旧名）。

### 3.2 建议 In / Out

**In（PREREQ-1）**
- C-06 §2.2 与 C-16 §2.4 的**追加句**（§2.3 文本）；冻结记录 §1B/§9、冻结矩阵 C-06/C-16 行、UNFREEZE 载体；
- `verify_pins.ps1` 重算（18/18，16 不变）；独立 byte-level 复核；
- 明确「契约就绪 ≠ 实现/产品可用」，并登记 L-G1 的子限制清单。

**In（实现卡）**
- Host 侧续期编排（新文件 `RunGrantRenewal.cs`）+ runtime 接线 + run_id 捕获（§2.1 的 (i)/(ii) 二选一）；
- 配置：`enabled`（默认 true）、`interval`（默认 240s）、`maxRenewals`（默认 12）、`TimeProvider` 注入
  （沿用 `HostOptions.cs:112` 的 `SourceScanTimeProvider` 模式）；
- 单测（fake clock/manual tick）、Python in-process 判别（过期前后 + Run 级读/提交）、gated IPC
  「同 scope 二次 mint+bind+可读」；
- 证据（EV/Manifest/logs）与 Handoff；卡面 AC 勾选。

**Out（明确不做）**
- TTL 延长 / Core sliding expiry / Core 侧任何改动；
- Core→Host 反向 RPC、事件协议、新命令/能力/错误码；
- Run wire / `PROTOCOL_MINOR` / schema / 迁移 / 依赖；
- 单步 >300s 的修复；加密源（L-G2）；Core 重启续跑（L-G9）；viewer 无 Run 时的读授权（L-R1 残余）；
  `>4096` 成员源（L-G16）；folder 身份键（L-S4-2）；
- UI 视觉/交互（UI P3）；B2 `roots_available`；L-R11 gate 统一；C-04b；SCAN-RH；
- `doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md`（DSH closeout 专属）；
- push。
- **可选顺带（DSH 裁决）**：RUN-GRANT-1 r3 的 **R3-02（P3）**「`AcceptRunAsync` → seam 的委托行未被测试判别」
  （`doc/reviews/FEA-11-RUN-GRANT-1-r3.md:253`）与本卡接线面相邻，可加一个 HostRuntime 级接线用例顺手关闭；
  若不接受，保持原样登记，不得声称已关闭。

### 3.3 文件级 allowed_paths（建议；DSH 冻结时可裁剪）

**契约（仅 2-pin 方案）**
- `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`
- `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`
- `doc/plan/FEA-CONTRACT-FROZEN-C06.md`
- `doc/plan/FEA-CONTRACT-FROZEN-C16.md`
- `doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`
- `doc/reviews/CONTRACT-UNFREEZE-2026-11-08-C06-C16-RUN-RENEWAL.md`（新载体；日期以实际提交为准）

**Host 生产代码（实现卡）**
- `apps/desktop-avalonia/src/NewManga.Host/Sources/RunGrantRenewal.cs`（新）
- `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`（只允许刷新语义/计数/停止条件；
  **禁止**改 TTL、scope 校验、撤销语义、`MaxRunGrants`/`MaxTrackedPayloads` 的既有值）
- `apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs`（只加续期配置）
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`（仅 §2.1 (i) 的可选
  post-dispatch 钩子；若 DSH 选 (ii)，改为
  `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs`，二者不得同时改）

**测试**
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/RunGrantRenewalTests.cs`（新）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs`
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs`（gated 追加）
- `tests/fea11/test_source_run_grant.py`（Run 级过期判别；**Core 生产代码零改动**）

**文档/证据**
- `doc/tasks/FEA-11-2C-LONG-RUN-RENEWAL-1.md`（或 DSH 选定的 `FEA-11-RUN-GRANT-2C.md`）
- `doc/handoffs/FEA-11-2C-LONG-RUN-RENEWAL-1-<head>.md`
- `doc/reviews/FEA-11-2C-LONG-RUN-RENEWAL-1-r1.md`（由**非实现者**的独立上下文 Reviewer 产出）
- `verification/FEA-11-2C-LONG-RUN-RENEWAL-1/**`

### 3.4 AC 草案（可判别 / fail-closed / 零漂移 / 门禁）

> 编号沿用卡面 `AC-2C-n`；括号内为判别点（破坏后必须变红）。

- **AC-2C-1（缺口复现，before）**：在干净 head 的真实装配上，先正常授权，再用 **fake clock** 把
  `core.source_read_refs._clock` 前推到 `expires_at + 1`（等价 `time.time()+301`，先例
  `tests/fea11/test_source_run_grant.py:698-716`），同一 Run 的 referenced 页**读**与**提交**分别
  typed 失败（`PROVIDER_FAILED` / `DB_FAILED`），且无 revision/page 业务写（候选行按既有
  `_reject_prepared` 标 `abandoned`，不是业务写）。证据：before 输出 + 表快照。
- **AC-2C-2（续期生效，after）**：同一装配下，在 t0 正常授权（G1，`expires_at=t0+300`）；把 fake clock
  前推到 `t0+301`（G1 过期）；执行一次续期 tick（铸 G2，`expires_at=t0+601`）；再把时钟推到 `t0+400`
  （仍在 G2 内），同一 Run 的引用页读与提交**成功**；`bound_pages ≥ 1`、G2 `expires_at > G1`、
  Run 状态/step 计数不被续期改变。**判别点 D1：删除续期 tick → 本 AC 红。**
- **AC-2C-3（只续本 Run 冻结范围）**：续期只使用该 Run 的 `{command, scope}`（`library_start_run` 用请求、
  `AcceptRun` 用 prepared slice、其余用 `GetRunSnapshot`）；不得换命令/换 scope；
  **判别点 D3：把 scope 换成 `all` 或注入新 source → 本 AC 红。**
- **AC-2C-4（撤销/漂移即停，fail-closed）**：registry `Revoke`（generation+1）或容器物理 facts 漂移后，
  下一次续期 typed 停止、**零新 grant 帧、零 `ReattestSourceLocation` 帧、不重试**，Run 仍由 Core
  fail-closed。**判别点 D2/D4：改成「复用旧 grant 延长期限」「失败后重试/reattest/放行」→ 本 AC 红。**
- **AC-2C-5（预算与生命周期）**：单 Run 单续期任务；`interval ≥ 240s` 且 `< 300 − 安全余量`；
  `maxRenewals` 有硬上限；与既有 mint gate 串行（`SourceReadCoordinator._gate`，`:266-267`）；
  Run 终态/缺失/Host 关闭/能力缺失即停；`TrackedPayloadCount ≤ 256`；续期失败**绝不阻断** dispatch。
- **AC-2C-6（managed-only 零回归）**：managed-only Run 不启动续期（首轮 `bound_pages == 0`）、
  零 grant/零帧；`SourceRegistryTests` 既有 32 例不降。
- **AC-2C-7（零漂移与门禁）**：契约 diff 只含 §2.3 的两句（逐行 diff 证据）；wire 字段/命令集/能力/
  错误闭集/TTL ≤300s/撤销/失联/§7/Run wire/`PROTOCOL_MINOR=3`/schema/依赖 **零改动**；
  `src/**` 零 diff；`verify_pins` 18/18 且 16 项不变；全量 pytest/.NET 不低于本卡起点；
  `check.ps1`（默认 + `-TaskPath`）PASS；API inventory EXIT=0；scope diff 全 ALLOWED。
- **AC-2C-8（不夸大）**：只承诺「多步长 Run 在续期窗口内可持续」；保留「单步 >300s、续期失败、L-G2、
  L-G9、L-R1 残余、L-G16」；不得写「任意长 Run 可用」「L-G1 关闭」「Run 全面恢复」。证据：卡/Handoff/EV 措辞核对。

---

## 4. Q4 测试与证据

### 4.1 长 Run 测试可行性（时间加速 / fake clock / 真实 sleep）

| 方式 | 可行性 | 说明 |
|---|---|---|
| **Core in-process fake clock** | **可行（推荐）** | 已有先例：`test_source_run_grant.py:698-716` 直接替换 `core.source_read_refs._clock`；同一 fixture 已有真实 Run 装配（`:453-512` 的 provider 读 + `source_commit_guard`；`:549` 的真实 commit）→ AC-2C-1/2 可零 sleep 判别 |
| Host fake clock / manual tick | **可行** | `SourceReadCoordinator(clock:)`（`SourceReadCoordinator.cs:53-54`）、`PreparedRunSlices(clock:)`（`HostRuntime.cs:1593-1594`）、`HostOptions.TimeProvider`（`:112`）→ 续期调度器接受注入时钟/手动 tick，单测零等待 |
| 真实 sleep 300s | **不可行** | 全量门禁不可接受；且 gated 用例会产生分钟级 flaky |
| .NET gated IPC 内前推 Core 时钟 | **不可行** | `Fea11RunGrantIpcTests` 的 Core 是**真子进程**，测试进程无法 monkeypatch 它的 registry 时钟 |
| 测试专用 TTL 缩短 seam | **不建议** | 会给 mint 增加生产语义开关（哪怕只缩短）；违背 R-1 的「不碰 `+300`」精神。若 DSH 一定要 IPC 级时间证据，需单独立项并明确「seam 只影响测试、默认 300、契约合法（≤300）」 |

### 4.2 最低新增测试集

1. `RunGrantRenewalTests`（Host，fake clock）：
   - `Renewal_RebindsAfterTheWindow_AndTheRunKeepsReading`（AC-2C-2，D1 判别）；
   - `Renewal_StopsOnRevokedRegistry_WithoutAnyNewMintFrame`（AC-2C-4）；
   - `Renewal_NeverWidensTheFrozenCommandOrScope`（AC-2C-3，D3）；
   - `Renewal_IsNotStartedWhenNoPageWasBound`（AC-2C-6）；
   - `Renewal_StopsAtTerminalRun_AndOnShutdown`（AC-2C-5）；
   - `Renewal_DoesNotExceedTheLedgerCap`（AC-2C-5）。
2. `SourceRegistryTests`：续期接线（dispatcher post-dispatch 钩子/ HostController 调用点）各 1 例；
   若顺带关闭 R3-02，加 `AcceptRunAsyncDelegatesToTheAuthorizationSeam` 的真委托判别。
3. `tests/fea11/test_source_run_grant.py`：
   - `test_run_read_and_commit_fail_after_the_window_with_zero_business_writes`（AC-2C-1）；
   - `test_renewed_grant_keeps_the_same_run_readable_past_the_window`（AC-2C-2）；
   - `test_renewal_never_rebinds_a_different_scope_or_command`（AC-2C-3，Python 侧反例）。
4. gated `Fea11RunGrantIpcTests`（`NEWMANGA_FEA11_IPC=1`）：`RenewalMintsAndRebindsTheSameScopeTwice`
   —— 同一 Run scope 连续两轮 mint+bind，第二次 `bound_pages ≥ 1`、页仍可读、wire 无新字段/无路径。

### 4.3 门禁成本 / flaky / 写卫生

| 项 | 记录值 | 说明 |
|---|---|---|
| 全量 pytest | **3360 passed / 10 skipped**（既有记录，≈252s） | 本卡零 Core 改动；仍须在 clean head 重测并记录起点/终点 |
| 全量 .NET | **1661 passed / 0 failed / 95 skipped**（L-S4-B-2 closeout；STATUS 仍写 1652/0/94） | 预计 +6～8 单测 +1 gated（默认 skip）；必须重测 |
| 已知 flaky | `library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`、FluentAssertions/Threading 偶发 | 首跑失败如实记录 + 隔离复跑；不得「重跑到绿」 |
| 写入卫生 | 全量 pytest 历史改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；`SourceRegistryTests` 写 `verification/FEA-09/native-registry/**` | 跑后 `git status`；只恢复**测试产生的**变更 |
| gated | `NEWMANGA_FEA11_IPC=1`；fixture 在 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-1\fixtures\**`；gated 默认 skip | 一条证据即可，不要为证据跑全量 |

### 4.4 建议证据目录

`verification/FEA-11-2C-LONG-RUN-RENEWAL-1/`：

- `EV.md`（AC-2C-1…8 逐项、before/after、子限制、UNFREEZE 引用）
- `logs/host-unit.log`（续期单测 + 回归）
- `logs/pytest-run-grant.log`（AC-2C-1/2/3 的 in-process 判别）
- `logs/host-ipc.log`（gated 1 passed）
- `logs/discrimination.log`（D1–D4 四个破坏点 + restore sha）
- `logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/gates.log`、`logs/pins.log`
- `logs/renewal-ipc.json`（两轮 mint/bind 的 `bound_pages`、无路径、无新字段）
- `scope-validation.log`、`changed-files.txt`、`RESOURCE-MANIFEST.json`
- （PREREQ-1）`pre-post.sha256`、`changed-lines.diff`、`other-16-pins.txt`、`carrier.md`

---

## 5. Q5 优先级与 DSH 裁决点

### 5.1 与队列项对比

| 项 | 性质 | 用户可见性 | 成本 / 契约 | 相对建议 |
|---|---|---|---|---|
| **2C 长 Run 续期（L-G1）** | **功能缺口**（长 Run 成批失败；不是回归） | **高**（长章节/排队 Run 直接失败） | 中：Host-only + **2 pins** + 独立 byte-level 复核 + 一轮续期编排 | **队列最前**（B2 已无消费者） |
| **B2 `roots_available`** | wire 投影，无消费者 | 当前无 | 小（C-16 字段已冻结） | 继续延后到 roots UI/多根管理立项 |
| **L-R11** | 两读面 gate 不一致/审计一致性 | 低 | 小-中；0 pin | 可穿插 |
| **C-04b** | 8 项文档 residual | 无 | 极小；0 pin | 穿插 |
| **SCAN-RH** | 可观测性/limitation | 低 | 小；0 pin | 穿插 |
| **UI P3** | 视觉/交互 | 低 | 小；0 pin | 最后 |

**推荐顺序（供 DSH 裁决）**：**① 2C-PREREQ-1（2 pins UNFREEZE）→ ② 2C 实现卡 → ③ L-R11 / C-04b /
SCAN-RH 穿插 → ④ B2（等 roots UI 立项）→ ⑤ UI P3 最后。** 若 DSH 采 0-pin 裁定，则 ①② 合为一张
Host-only 卡。理由：2C 是当前队列里唯一「用户可见 + 命令面已齐备」的缺口；B2 无消费者；其余为低风险
维护项，不应占住 2C 的 Review/实现带宽。

### 5.2 DSH 裁决点（含推荐）

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **D-1** | 2C 的 UNFREEZE 判定：2 pins（C-06+C-16 追加句）还是 0-pin「§2.4 重复调用属既有语义」？ | **2 pins**（§2.3 的最小追加句）；0-pin 仅在 DSH 明示解释并在卡/载体/Handoff 三处留痕时接受 | 决定拆卡数、pin 数与 Review 规模 |
| **D-2** | 方案：(a) Host 周期续期 / (b) 延长 TTL / (c) Core sliding / (d2) Core 主动协议？ | **(a)**；(b) 只作退化备选；(c)(d2) 否决（§2.2） | 决定是否触 Core 与契约面 |
| **D-3** | 拆卡：PREREQ-1 + 实现卡 vs 单卡 | **2 张**（2-pin 方案）；0-pin 则 1 张 | 决定生命周期与冻结顺序 |
| **D-4** | 参数：`interval`（240s）、`maxRenewals`（12）、`enabled`（默认 true）、`TimeProvider` 注入 | 接受上述默认；硬上限必须写进 AC-2C-5 | 决定用户连续性与 mint 成本 |
| **D-4b** | 续期 mint 的 identity 成本：大 folder（≤10000 成员）每轮逐成员 sha256 可能超过 interval | **必须重算（R-2）+ 单轮 mint 成本上限：超限的 source 本轮 typed skip（Best-effort，登记 L-G8 放大）**；**不接受**「复用旧 digest / 只比 volume+file id」的降级 | 决定是否引入新的 weaker-identity 语义（本报告建议不接受） |
| **D-5** | run_id 接线点：`HostCommandDispatcher` post-dispatch 钩子 vs `HostController` 4 个调用点 | **dispatcher 钩子**(i)（不触 App、不漏命令） | 决定 allowed_paths 是否含 `NewManga.App` |
| **D-6** | 是否加「测试专用 TTL 缩短」seam 以取得 IPC 级时间证据 | **不加**；时间维用 in-process fake clock（§4.1） | 决定是否新增生产语义开关 |
| **D-7** | L-G1 关闭口径 | **只降级不关闭**：从「无续期」→「有续期 + 子限制」（单步 >300s/续期失败/加密/重启/viewer/4096） | 决定卡/STATUS/Handoff 措辞 |
| **D-8** | 基线：STATUS（pytest 3360/10、.NET 1652/0/94）vs L-S4-B-2 closeout（pytest 3360/10、.NET 1661/0/95） | clean head 重测并写「本卡起点」 | 决定 AC-2C-7 可判性 |
| **D-9** | 是否顺带关闭 R3-02（P3，AcceptRun 委托行未判别） | 可顺带；不接受则保持登记 | 决定卡范围多一行测试 |
| **D-10** | 卡 id：`FEA-11-2C-LONG-RUN-RENEWAL-1` vs `FEA-11-RUN-GRANT-2C`（既有 handoff 多处使用） | 二选一，**不得并存**；建议沿用 `FEA-11-RUN-GRANT-2C` 以保持血统 | 决定 PLAN/STATUS/证据目录命名 |

---

## 6. 风险

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | 续期被误读为「放宽授权/延长 TTL/撤销后自动放行」 | **高** | §2.4 红线段 + AC-2C-4 + 契约追加句明写「不延长/不扩 scope/不绕过撤销」 |
| R2 | mint 成本放大（容器整文件 sha256；folder 逐成员）→ 长 Run 每 240s 重算，I/O 可感 | **中-高** | D-4b：单轮成本上限 + best-effort skip；记录单次 mint 耗时；登记 L-G8 放大 |
| R3 | 续期与用户撤销/同步改 binding 竞态 | 中 | 每轮 `Registry.Authorize`（`SourceAccessRegistry.cs:62-70`）+ Core per-page 原子匹配（`source_read_refs.py:485-556`）；失败即停，不放行 |
| R4 | `AuthorizeSourceReadForRun` 全有或全无：任一页 pending/改绑 → 整轮续期失败 | 中 | 明确「续期失败 ≠ Run 失败」；不重试；不拆成 per-source 请求（拆了也会因 scope 含其它 source 页而整拒） |
| R5 | 续期任务泄漏/双重计时（Run 已终态仍续） | 中 | Run 终态/缺失即停；单 Run 单任务；Host 关闭取消 |
| R6 | ledger 被续期击穿（`MaxTrackedPayloads=256`） | 低-中 | AC-2C-5 断言；沿用 `PruneExpired`（`SourceReadCoordinator.cs:415-443`） |
| R7 | 测试只能证明「同 scope 二次绑定」，不能证明「跨 300s 端到端」 | 中 | 时间维用 in-process fake clock（AC-2C-1/2）并在 EV 明写证据边界 |
| R8 | 2 pins 的 pin 漂移/复核成本 | 中 | 只追加两句；`verify_pins` 18/18（16 不变）；独立 byte-level 复核 |
| R9 | 「L-G1 关闭」被写进 STATUS/Handoff（过度宣称） | 中 | AC-2C-8 + D-7；子限制清单固定 |
| R10 | 文档漂移（PLAN 重复片段、STATUS 旧基线） | 低 | 实现卡不修（不在 allowed_paths）；DSH closeout 统一维护 |
| R11 | R3-02 等既有 P3 被顺带「声称关闭」而无判别用例 | 低 | 只有新增真委托判别用例才可关闭；否则保持登记 |

---

## 7. 真实性声明

1. **唯一写入**：本评审只写了 `doc/reviews/2C-LONG-RUN-RENEWAL-scope-r1.md` 这一个文件。**未**修改/删除/
   移动任何生产代码、测试、契约、冻结记录、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或证据字节；
   **未**执行 `git add`/`git commit`/`git push`；**未**运行会写仓的构建/测试。
2. **独立性**：评审者为独立上下文的 fresh subagent（DSH 子会话
   `857903ae-5c63-44ae-a37b-9e4472486829`），未参与 RUN-GRANT-1/2A/2B/2C 线、L-S1/L-S4 线、
   RENDITION/Flux/Read 线的实现、返修或审查；只读被审 head。
3. **事实优先级**：所有代码/契约断言均来自 `0bf90fc5b` 的工作树字节（`git status` clean，评审期间
   无并发提交；`fad1ec776..HEAD` 对 `apps/src/tests` 零 diff），逐条给出 `path:line`；未把卡面/Handoff/
   Review 的自述当作实现事实（引用时标注「既有登记」）。
4. **实测命令**（EXIT 见 §0）：`git log -1`、`git status --porcelain`、
   `git diff --name-only fad1ec776..HEAD -- apps src tests`、`git diff --name-only 313f88905..HEAD`、
   `pwsh -NoProfile -File tools/governance/verify_pins.ps1`、`check.ps1`（默认）。
5. **NOT_RUN**（未跑、不声明 PASS）：全量 `pytest tests`、全量 `dotnet test`、定向 .NET、gated 真实 IPC、
   byte-level 契约复核、任何破坏-恢复实验。§4.3 的数字均为**既有记录**，不是本评审实测。
6. **判别力声明**：本报告未做「破坏-恢复」实验；§3.4/§4.2/§4.4 的 D1–D4 是给实现卡/Review 的
   **待验证项**，不是本轮已完成证据。
7. **建议性质**：本报告的 In/Out/allowed_paths/AC/UNFREEZE 判定均为**建议**；scope 冻结、契约字节变更、
   Review Appointment、findings 处置与集成验证属 DSH。
8. **limitation**：本报告不评估 B2/L-R11/C-04b/SCAN-RH/UI P3 的实现细节，仅做优先级比较；不声称任何
   测试或 gated IPC 已在当前 head 通过；不声称 DSH 已采纳 2-pin 判定；不声称 L-G1 可被关闭——
   按本报告推荐实现后 L-G1 **只降级不关闭**。
