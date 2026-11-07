---
task: FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
title: Run 源范围解析恢复（L-S4-B-2：RunSourceRange 仍按路径解析，同路径 revoked 旧条目否决 live 授权）权威 scope review r1
reviewer: fresh subagent（独立上下文；未参与 L-S4-B / L-S4-B-1 / B2 / L-S4-A / B1 的实现、返修或审查；只读被审 head）
session: 0f28cb0d-82e2-4f50-8c13-3cfd941d5003（DSH 子会话；独立上下文）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 scope review（fresh context / read-only / 非作者 / 非实现审查者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 3e19f37db2a8fd80e438c7ef8575185634347087
reviewed_head_note: >-
  任务书给的是 `3e19f37db`（main，clean）。实测 HEAD、分支与任务书一致；评审起点
  `git status --porcelain` 为空，结束时仅本报告未跟踪。`0c1390b2a..HEAD`（L-S4-B-1 证据提交之后）
  的 `apps/`、`src/`、`tests/` **零 diff**（其余 diff 仅 `doc/**` 与
  `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/EV.md`）。因此 L-S4-B-1 的 gated 证据仍是
  当前 head 的行为，且 `HostRuntime.cs:1785` 的 Run 面代码自 L-S4-B 起未变化。
verdict: READY-TO-FREEZE
verdict_scope: >-
  推荐形状为 **Host-only：`RunSourceRange.Resolve` 对枚举 target 复用它自己的 live
  `(registry_id, generation)` 条目**（直接复用 L-S4-B-1 已交付的
  `HostSourceScanExecutor.SelectEnumeratedEntry`），非枚举 target 继续走 `ResolveRegistryEntry`；
  不碰 Core/契约/schema/依赖。按此形状 **0 UNFREEZE / 18 pins 全不变**，可冻结。
  其前提是沿用 DSH 在 L-S4-B-1 S-2 已采纳的解释口径：C-17 §5.3 的 fail-closed 主体是
  **target 自己的 registry**，不是同路径任意历史行。若 DSH 推翻该口径，则本卡（以及已 done 的
  L-S4-B-1）需要 C-17 1 pin UNFREEZE + 独立安全复核；那应作为独立治理决策处理，
  **不应把本卡判 BLOCKED**。B2 `roots_available`、folder（L-S4-2）、2C 长 Run 均不并入。
---

# FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1：权威 scope review r1

> **结论先行。**
>
> 1. **缺口成立，且是 L-S4-B-1 同根因在 Run 面的确定性命中。** B1 显式重授权 = 撤销同路径全部
>    非撤销条目 + 只注册一条新条目，旧条目只置 `revoked_at`（generation+1）且永不删除
>    （`SourceRecoveryModels.cs:395-410`、`:461-491`、`:493-519`；`SourceAccessRegistry.cs:100-110`）。
>    L-S4-B 的 reattest 把 Core `source_locations` 的 registry 两列更新到 live
>    （C-16 §2.5 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:95-108`），枚举因此把 target 恢复为
>    live `(registry_id, generation)`（`SourceScanScheduler.cs:2353-2388`；gated 证据
>    `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-closed-loop.json:6-20` 的
>    `old_registry_id` / `live_registry_id` / `recovered_target.registry_id` 就是该状态）。
>    但 **`RunSourceRange.Resolve` 仍按路径** 调用 `ResolveRegistryEntry(registryEntries, target.Path)`
>    （`HostRuntime.cs:1785`）；该方法对整个 registry 做 path-exact 扫描，**先命中同路径 revoked 旧条目
>    就 `return null`**（`SourceScanScheduler.cs:1911-1915`），即使 live exact 条目同时存在
>    （`:1917-1920` 的 `exact ??=` 才不会被用到）。结果：该 source 计入 `Unresolved`
>    （`HostRuntime.cs:1786-1790`），**不会进 `Targets`，也不会进 `ColdSources`**，冷源 on-demand
>    分类在 entry 判定处就被短路。
> 2. **Run 面的影响不是「少一次扫描」，而是用户可见的 Run 失败。** Run 预授权是 best-effort，
>    但那意味着「没有 grant」，不是「Core 放行」：
>    - 若该 source 是唯一可解析 source → `targets.Count == 0` → 不发 `AuthorizeSourceReadForRun`
>      （`HostRuntime.cs:2007-2011`；`SourceReadCoordinator.cs:305-309`）→ Run 照常 dispatch，
>      Core 读取该 source 的引用页时 typed 拒绝；
>    - 若其它 source 铸出了 grant 且 Run 范围含该 source 的 binding 页 → Core per-page 匹配失败
>      → **整命令 `SOURCE_ACCESS_DENIED`**（C-16 §2.4 `:90-91`；`core_service.py:4965-5069`；
>      `source_read_refs.py:485-556`），Host 把 `CoreOperationException` 重抛
>      （`HostRuntime.cs:2027-2032`）→ **Run 命令不 dispatch**（`HostCommandDispatcher.cs:154-158`、`:175-178`）。
>    也就是说「重新授权成功之后，这本书/这一页的 Run 仍被拒绝」，与草稿卡的描述一致且更严重。
> 3. **managed-only Run 不受影响。** C-16 §2.4 的 per-page 规则是「目标页无 binding（managed）→ 跳过」
>    （C-16 `:90`；`source_read_refs.py:517-520`）；managed 页不要求 grant，未解析 source 最多产生一条
>    `unresolved_sources=1` 告警（`HostRuntime.cs:1995-1999`），不阻断 dispatch。只有目标页确属该
>    referenced source 的 binding 时才会命中 §2 的失败面。
> 4. **最小方案是 (a)：枚举 target 用自身 live entry，0 UNFREEZE / 18 pins。** 直接复用
>    `SelectEnumeratedEntry`（`SourceScanScheduler.cs:1957-1988`）即可；非枚举 target 的
>    `ResolveRegistryEntry` 语义（exact-first / revoked-exact fail-closed / containment fallback）
>    字节不变。安全面不降：铸 grant 仍走 `IssueLockedAsync → Registry.Authorize`，逐请求复核
>    live/generation/根包含/卷-文件身份（`SourceReadCoordinator.cs:517`；`SourceAccessRegistry.cs:62-98`），
>    因此「选错条目」只会 typed skip，不会放行。
> 5. **改 `ResolveRegistryEntry` 全局语义 (b) 不推荐、也不需要。** 它是 C-17 §5.3 语义面
>    （`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:279`），需要 C-17 1 pin UNFREEZE + 独立安全复核，
>    并把多 revoked/多 live/时间序歧义塞进 resolver；对枚举 target 反而比「用自身 id」更弱。
>    本卡不采用；若 DSH 要做，应独立决策，不塞进本卡。
> 6. **拆卡：独立单卡（L-S4-B-2），不并入 L-S4-B-1，也不并入 B2/2C。** L-S4-B-1 已 done 且
>    delivery 冻结（`bcc88e4a2` / 证据 `0c1390b2a`），其 allowed_paths 不含 `HostRuntime.cs`、
>    S-4 明写「Run 面另卡」；重开 done 卡会破坏 append-only 生命周期与证据 pin。本卡 = 一个函数内
>    一个分支 + 测试/证据，正好收口。
> 7. **Q4：可行。** 纯函数矩阵可在无 Core 下判别；gated 真实 IPC 也可低成本闭环——Core 的 Run
>    per-page 匹配不比较 registry_id/generation（`source_read_refs.py:558-594`），所以
>    「Host registry 上 revoke 旧条目 + 同路径 register 新条目」+ 既有测试 helper
>    `AlignRegistryAsync`（`Fea11RunGrantIpcTests.cs:1083-1108`）就能在真实 Core 上验证
>    `bound_pages=1` 与 `resolve_page_resource` 成功；由 `error/refusal` 变 `bound_pages=1` 即 before/after。
> 8. **Q5：优先级建议本卡先做（最小、0 pin、消除一个已知用户可见 Run 拒绝），随后 2C 长 Run。**
>    B2 `roots_available` 无消费者继续延后；L-R11/C-04b/SCAN-RH 可穿插；UI P3 最后。
>    DSH 的裁决点不是「要不要 UNFREEZE」，而是「是否沿用 L-S4-B-1 S-2 的 §5.3 口径、
>    gated 证据取轻量版还是完整 Core reattest 版」。

---

## 0. 只读基线与实测命令

| 项 | 值 | 来源/说明 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `3e19f37db2a8fd80e438c7ef8575185634347087` | `git rev-parse HEAD` |
| HEAD 提交 | `2026-11-07 16:28:45 +0800 docs(fea-11-l-s4-b-1): closeout P3 清单对齐 r1 报告 §5（9 项权威清单；结论不变）` | `git log -1` |
| 工作树 | 起点 **clean**；结束时仅本报告未跟踪 | `git status --porcelain`（起点 0 行） |
| `0c1390b2a..HEAD` 生产/测试 diff | `apps/`、`src/`、`tests/` **空** | `git diff --name-only 0c1390b2a..HEAD -- apps src tests` 输出为空；其余 diff 仅 `doc/**`、`verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/EV.md` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0 | 实测；C15 `f9e376a0ed4c`、**C16 `a7f57ebdbd67`**、**C17 `aefa0fa5b17e`** |
| `check.ps1`（默认） | **PASS (3 warnings)**，EXIT=0 | 实测；3 warnings = 9 个非终态 Task + STATUS/PLAN 预算 80%；默认即解析到本卡 `doc\tasks\FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` |
| `check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | **PASS (3 warnings)**，EXIT=0 | 实测 |
| `generate_api_inventory.py --check` | **EXIT=0**；`IHostController` 54 + `IRunController` 6 + `IReaderProgressSink` 1 = **61** | 实测（`PYTHONDONTWRITEBYTECODE=1`，未写 `__pycache__`）；与 C-07 一致 |
| 只读契约核对 | C-16 v1.5 §2.4 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:76-93`；§2.5 `:95-108`；C-17 §5.3 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:279`；C-15 §5 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:293-318`、§6.3 `:324` | HEAD 字节实测 |
| 定向/全量测试 | **NOT_RUN** | 只读 scope review + 本会话「只允许写一个文件」硬约束；`dotnet test`/`pytest` 会写 `bin/obj`、`.pytest_cache`，全量 pytest 历史上还会改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`。本报告不声明任何测试 PASS。 |
| gated 真实 IPC | **NOT_RUN** | 同上；实现卡必须自行跑并入库 |
| 契约 byte-level 复核 | **NOT_RUN** | scope review 不做 byte-level；UNFREEZE 判定见 §2.3 |
| 真实用户数据 / AppData / 回收站 / push | **未触碰** | — |

> **基线口径提醒（冻结/释放时必须重测）**：`doc/STATUS.md:20` 仍写 pytest **3317/10**、.NET
> **1617/0/93**，而 L-S4-B-1 closeout 实跑为 **3360/10**、**1652/0/94**
> （`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md:88`、`:138`）。本卡不得直接继承任一旧数字，
> 必须在 clean head 重测并写「本卡起点基线」。
> 另：`doc/REBASELINE_PLAN.md:53` 仍写「L-S4-B-1（ready）/ B2（proposed）」且 B2/2C 重复出现，
> 与 STATUS/卡面的 `L-S4-B-1 done` 不一致——属既有文档漂移，`check.ps1` 仍 PASS(3 warnings)；
> 本卡不做、也不得顺手改（不在 allowed_paths）。

---

## 1. Q1 缺口核实

### 1.1 确定性链路（B1 → reattest → 枚举恢复 → Run 范围仍 unresolved）

| 步 | 事实 | 锚点 |
|---|---|---|
| 1 | B1 显式重授权 = 先撤销**同路径全部非撤销条目**，再只注册**一条新条目**；旧条目只置 `revoked_at`（generation+1），永不删除，revoked 行累积 | `SourceRecoveryModels.cs:395-410`（doc）、`:461-491`（revoke 循环）、`:493-519`（register 循环）；`SourceAccessRegistry.cs:100-110` |
| 2 | L-S4-B reattest 把 Core `source_locations` 当前行的 `registry_id/authorization_generation` 条件单行更新为 live（`last_verified_at` 不变），于是 Core 枚举重新投影 live pair | C-16 §2.5 `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:95-108`；Host pre-pass `SourceScanScheduler.cs:2185-2258` |
| 3 | 枚举映射要求 target 的 `(registry_id, generation)` 在 Host registry 中 live 且 generation 相等，并用该 entry 的 `roots[0]` 造 `SourceScanTarget.Path` | `SourceScanScheduler.cs:2353-2388`（`:2369-2374` 授权核验；`:2376-2386` Path=root[0]） |
| 4 | scheduler refresh 把 target 合并更新（`existing.Target = target`），watcher 重新覆盖 | `SourceScanScheduler.cs:797-819`、`:776-783`；`SourceWatcher.cs:316-407`（B1 scope review 已核实） |
| 5 | Run 的 `known` 来自 scheduler `TargetSnapshot()`；registry entries 来自 `registry.List` | `HostRuntime.cs:1531-1544`（`knownTargets: () => ScanScheduler?.TargetSnapshot()`；`registryEntries: registry.List`） |
| 6 | `RunSourceRange.Resolve` 对每个 target 先 `HostSourceScanExecutor.ResolveRegistryEntry(registryEntries, target.Path)` | `HostRuntime.cs:1785` |
| 7 | `ResolveRegistryEntry` 遍历整个 registry 做 path-exact：**遇到同路径 revoked 条目立即 `return null`**，即使 live exact 条目同时存在；`exact ??=` 只有在没遇到 revoked 时才会被采用 | `SourceScanScheduler.cs:1897-1938`（关键 `:1911-1915`；`:1917-1920`） |
| 8 | `entry is null` → `unresolved++` + `continue`；该 source 既不进 `Targets`，也不进 `ColdSources`，on-demand scan 不会被触发（entry 判定在 identity cache 判定之前） | `HostRuntime.cs:1785-1798`；`:1768-1774`（MaxRunGrants 分支）；`:1791-1798` |
| 9 | `targets.Count == 0` → 不发 `AuthorizeSourceReadForRun`，Run 继续 dispatch；若有其它 grant 且 Run 范围含该 source 的 binding 页 → Core 整命令 typed `SOURCE_ACCESS_DENIED` → Host 重抛 → Run 不 dispatch | `HostRuntime.cs:2007-2011`、`:2012-2037`（`:2027-2032`）；`SourceReadCoordinator.cs:305-309`、`:310-319`；C-16 `:90-91`；`core_service.py:4965-5069`；`source_read_refs.py:485-556`；`HostCommandDispatcher.cs:154-158`、`:175-178` |

**结论**：链路确定性，不依赖 registry 行顺序——`ResolveRegistryEntry` 即使先取到 live exact，
后续遇到 revoked exact 仍会 `return null`（`:1911-1915`）；而 B1 的旧条目按设计永久保留。
B1 自己的 gated 证据就是该状态的现成样本：同一 `root` 路径上 `old_registry_id` 已撤销、
`live_registry_id` 为 live、`recovered_target.registry_id=live`、`host_registry_unchanged=true`
（`verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-closed-loop.json:6-20`、`:27`），
而该状态只在扫描 tick 上被 B1 修复，Run 面当时零 diff（L-S4-B-1 r1
`doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-r1.md:31`、`:67`、`:111`）。
另外，B1 的纯函数测试已经直接断言了「同状态下 path-only resolver 返回 null」
（`SourceScanExecutionRecoveryTests.cs:87-109`，`:100`），可作为确定性旁证。

### 1.2 影响面

| 面 | 是否受影响 | 事实/锚点 |
|---|---|---|
| **Run 预授权（start_run / control continue\|restart / resume_blocked / retry_failed）** | **是（主影响）** | 全部经 `RunSourceAuthorizer.AuthorizeForCommandAsync → AuthorizeSliceAsync → ResolveWithColdCacheAsync`（`HostRuntime.cs:1912-1959`、`:1972-2038`、`:2043-2092`）；命令集见 `RunCommandPolicy.TriggersStepExecution` `:1702-1709` |
| **Run dispatch 是否被阻止** | **是（部分场景）** | 仅当 Run 范围含该 source 的 binding 页且另有 grant 被铸出时，Core 整命令拒绝 → Host 重抛 → 不 dispatch（`HostRuntime.cs:2027-2032`；`HostCommandDispatcher.cs:154-158`） |
| **冷源 on-demand 分类** | **是（在分类前被短路）** | 先 entry 后 identity（`HostRuntime.cs:1785` 再 `:1793`）；unresolved 的 source 永远不会进 `ColdSources`，因此 `_onDemandScan` 不会被调用（`:2050-2052`、`:2063-2084`） |
| **冷源 on-demand 执行本身** | 否（B1 已修） | `ScanSourceOnDemandAsync → executor.ScanAsync`（`HostRuntime.cs:1553-1563`）；`ScanAsync` 枚举分支已用自身 live entry（`SourceScanScheduler.cs:1511-1523`） |
| **managed-only Run** | 否 | C-16 §2.4「目标页无 binding（managed）→ 跳过」（`:90`；`source_read_refs.py:517-520`）；`known` 为空时早返回（`HostRuntime.cs:1746-1750`）；未解析 source 只产生计数告警（`:1995-1999`），无 grant 需求、不阻断 |
| **周期扫描 tick** | 否 | B1 已修（`SourceScanScheduler.cs:1498-1562`；B1 卡 `:63-68`） |
| **非枚举（SCAN-1 内存注册）Run target** | 否（现状保留） | `ResolveRegistryEntry` 语义不变；生产 App 不调用 `RegisterSourceScanTarget`（仅测试引用，`HostRuntime.cs:169-184` 为 public seam） |
| **Core / registry / 其它 source** | 否 | 本缺口不写 Core、不改 registry 结构；Run 范围解析只读（`HostRuntime.cs:1739-1812` 无 I/O） |

> **口径细化（避免夸大/缩小）**：
> 1. 「all-unresolved」子场景：Run 照常 dispatch，但该 source 的引用页在 Core 侧没有 live grant；
>    用户看到的是 Run 启动后页级读取 typed 失败（不是「Host 提前拒绝」）。
> 2. 「partially-resolved + 目标页属于该 source」子场景：`AuthorizeSourceReadForRun` 整体 typed
>    `SOURCE_ACCESS_DENIED`（C-16 §2.4 `:91` 无部分成功）→ Run 命令不 dispatch。这是最需要修的行为，
>    也是「重新授权后这本书仍不能 Run」的直接原因。
> 3. 若 Run 范围只含 managed 页或其它已解析 source 的页，则不阻断；因此不得把本卡写成
>    「所有 Run 都失败」。

### 1.3 为什么不是「Run 面已随 L-S4-B-1 顺带修好」或「有其它兜底」

1. **B1 的生产 diff 只有 `SourceScanScheduler.cs`**：`apps/`/`src/`/`tests/` 在
   `0c1390b2a..HEAD` 零 diff（§0 实测）；B1 卡 `out_of_scope` 明写 `HostRuntime/RunSourceRange`
   （`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md:31`），DSH 裁决 S-4 也明写 Run 面另卡
   （`:48`）。r1 Review 逐字复核 `HostRuntime.cs:1785` 仍在按路径解析（r1 `:31`、`:67`、`:111`）。
2. **`RunSourceRange` 只有一个解析入口**：全仓 grep 只有 `HostRuntime.cs:1785`（以及测试调用），
   没有第二条能绕开 `ResolveRegistryEntry` 的 Run 解析路径。
3. **best-effort 不是放行**：预授权的语义是「Host 已铸造并注册 grant → Core 绑定页」，缺 grant
   时 Core 仍 fail-closed（C-16 §2.4；`source_read_refs.py:558-594`）。
4. **reattest 修的是 Core 行的授权列，不是 Host 的范围解析**：reattest 之后 Host target 已带 live id，
   但 `RunSourceRange.Resolve` 又丢掉这个身份、退回 path-only 的二次裁决——这是解析权威
   （resolution authority）问题，不是缓存新鲜度问题（与 L-S4-B-1 scope review §1.4 同结论）。
5. **冷源 on-demand 的失败点在分类，不在执行**：执行面 `ScanAsync` 已是 B1 修复版；若只重跑
   on-demand scan 而不改范围解析，source 仍先被判 `unresolved`，根本走不到 executor。

### 1.4 与 L-S4-B-1 卡面/证据/Review 的一致性（不是重开 B1）

- B1 卡面明确只承诺「枚举 target 的扫描执行恢复」，并登记 Run 面 limitation
  （`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md:63-68`、`:72`、`:90-92`、`:98`、
  `:139`）。
- B1 closeout 记录 Run 面零 diff，并把另卡名 `L-S4-B-2-RUN-RANGE-RESOLVE-1` 写明（`:139`）；
  本卡 `depends_on` 也指向 B1（`doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md:11-13`）。
- 因此本卡是**新缺口修复**，不改变 B1 的 AC-SER-1…6 判定、不重跑 B1 证据、也不要求 B1 返修。

---

## 2. Q2 最小方案

### 2.1 候选逐项评估

| 选项 | 具体形状 | 写域/契约 | 取舍 |
|---|---|---|---|
| **(a) 枚举 target 用自身 live `(registry_id, generation)`** | `RunSourceRange.Resolve` 对 `target.IsEnumerated` 复用 `SelectEnumeratedEntry(registryEntries, target, out _)`；`!IsEnumerated` 保持 `ResolveRegistryEntry` | Host read-only；**0 契约** | **推荐**。最小（一个分支）、最精确（授权主体=target 自己的 registry）、与 L-S4-B-1 同一权威；不需要时间序/多 live 歧义规则；铸 grant 仍由 `Registry.Authorize` 逐请求复核（`SourceAccessRegistry.cs:62-98`），安全面不降 |
| **(a') 刷新 scheduler/registry「视图」** | reattest 后让 scheduler 重新枚举/过滤 | Host read-only；0 契约 | **不成立**：scheduler 每次扫描 fresh `Registry.List()`（`SourceScanScheduler.cs:1879-1880`），枚举每次 fresh `SnapshotEntries()`（`:2139`），没有可刷新的缓存视图；target 视图也已在 refresh 合并（`:797-819`）。revoked 行永久存在，刷新视图仍会看到它 |
| **(b) 改 `ResolveRegistryEntry` 全局语义** | 同路径新 live + `live.CreatedAt > old.RevokedAt` 即接受 | Host code 但触及 C-17 §5.3 解释；**+1 pin** | **否决（作为本卡方案）**。把 C-16 §2.5 的 reattest 候选规则搬进 resolver：多 revoked/多 live 歧义、时间解析、containment fallback 语义变化、所有 caller（非枚举 target/未来 caller）受影响；且正是 B1 scope review §2.5 与 `C16-V15-BATCH-scope-r1.md:117` 已讨论过的 C-17 语义面。收益不高于 (a)，代价高得多 |
| **(c1) 给 resolver 传 live-only 视图** | `entries.Where(e => e.RevokedAt is null)` 后再 path resolve | Host read-only；0 契约 | **可接受的次选，但不推荐**：仍是 path 解析、同路径多 live 时取第一条，不能证明「用的是 target 自己的条目」；若把过滤扩散到非枚举 target 就变成语义放宽 |
| **(c2) 删除/改写 revoked 旧条目** | reattest 后删除同路径 revoked 行 | Host registry 写；无授权 | **否决**：破坏 B1 审计/诊断与 revoked 行累积语义；无卡面/契约依据；本质是「按当前路径重新解释历史授权」 |
| **(c3) 让 Core 在枚举返回 path / 枚举时写 location** | 改 C-17 只读枚举或 DTO | Core + C-17；≥1 pin | **否决**：C-17 `:279` 明确枚举只读、不返回路径/secret/grant；与 L-S4-B「reattest 事实由 Host 显式动作传播」冲突 |
| **(c4) 每轮 Run 前重新 reattest** | 每次预授权再发 `ReattestSourceLocation` | 不必要 | **否决**：Core 行已 live；重复写违反「每轮至多一次」精神（C-16 §2.5 Host 前置义务 `:104`）且无收益 |
| **(c5) 清 backoff / 重置失败计数** | target identity 变化时清 `Failures/BackoffUntil` | Host 调度行为 | **不需要**：Run 预授权不读 scheduler 的 backoff；本卡只修范围解析 |
| **(c6) 只改状态/日志** | 把 unresolved 显示成 skipped | 无行为修复 | **否决**：掩盖缺口；Run 仍拿不到 grant |
| **(c7) 接受 limitation、不修** | 文档登记 Run 面未修 | 0 | **否决**：影响是用户可见的 Run 被拒/页读失败，且修复成本极小；继续保留会让「重新授权」的恢复承诺在 Run 面失效 |
| **(c8) 全量改用 target id（含非枚举）** | 对所有 target 优先 `RegistryId`，缺失时再 path | Host read-only；0 契约 | **否决**：非枚举 target 没有 registry id，任何「优先 id」都会改变非枚举语义；本卡只需要枚举分支 |

### 2.2 推荐形状（代码级，供实现卡冻结）

**唯一生产改动**：`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` 的
`RunSourceRange.Resolve`（`:1739-1812`），在 `:1785` 处把 entry 解析拆成两个分支：

```csharp
SourceAuthorization? entry;
if (target.IsEnumerated)
{
    // L-S4-B-2: the enumerated target is authorized by its OWN live (registry_id, generation);
    // reusing the resolver L-S4-B-1 proved for the scan face. A same-path REVOKED sibling row
    // never vetoes this target. The Run face has no skip/frame vocabulary: a refused verdict
    // is simply "unresolved" (best-effort; the mint re-verifies live/generation/root identity).
    entry = HostSourceScanExecutor.SelectEnumeratedEntry(registryEntries, target, out _);
}
else
{
    entry = HostSourceScanExecutor.ResolveRegistryEntry(registryEntries, target.Path);
}
if (entry is null)
{
    unresolved++;
    continue;
}
```

要点（逐条都是红线/判别点）：

1. **只改枚举分支**；非枚举分支保留 `ResolveRegistryEntry(registryEntries, target.Path)`
   （含 exact-first / revoked-exact fail-closed / containment fallback，`:1897-1938`）。
2. **不改 `SourceScanScheduler.cs`**：`SelectEnumeratedEntry` 已是 public static pure helper
   （`:1957-1988`），语义正是「target 自己的 live entry / 否则 typed verdict」；Run 面只是复用。
3. **丢弃 verdict**：Run 没有 `Skipped`/`ScanSourceSync` 词汇；未解析继续计入 `Unresolved`
   （`:1720-1728` 的文档口径不变）。
4. **保持先 entry 后 identity 的顺序**（`:1785` → `:1793`）：未解析的 source 不进入 cold 列表，
   与现行为一致；修复后 live 但无 Core 版本的 source 会正常成为 `ColdSources` 并走既有
   on-demand scan（`:2049-2092`）。
5. **保持 normalized 与 `KindOfSource` 逻辑不变**（`:1775-1784`、`:1799-1809`）；scope 仍带
   `entry.RegistryId/Generation`、`normalized`、`identity.VersionId`、容器成员（`:1800-1809`）。
6. **不新增 I/O、不写 registry、不调用 Register/Revoke/Reset**；`RunSourceRange` 仍是纯函数
   （除 `SourceIdentityCache` 读取）。
7. **异常面**：`SelectEnumeratedEntry` 内部 `SingleOrDefault`（`:1963`）在「同一 registry_id 出现两次」
   时抛 `InvalidOperationException`；该状态被 `Load` 的 unique-id 校验排除
   （`SourceAccessRegistry.cs:168-170`），但 `HostRuntime.cs:2049` 的调用不在 authorizer 的 try 内，
   建议在 Run 分支包一层 `catch (Exception e) when (e is not OutOfMemoryException) { unresolved++; continue; }`
   或注明「unique id 由 Load 保证」，以保持「Host 侧解析失败最多是 unresolved、绝不抛」的现状。
8. **注释修正**：在 `RunSourceRange` 的 XML doc 注明「枚举 target 的授权来源是它自己的
   live `(registry_id, generation)`；path resolver 只服务非枚举 target」（与
   `ResolveRegistryEntry` 的 AC-SER-3 注释一致，`:1891-1895`）。

**安全面（为什么不需要再加身份校验）**：Run scope 的 path/kind 仍会进入
`SourceReadCoordinator.AuthorizeRunAsync → IssueLockedAsync`，其中
`Registry.Authorize(registryId, generation, [path])` 在锁内 fresh 读 registry 并逐请求复核：
entry 存在、未撤销、generation 相等、path 属于该 entry 的 read-able root、根 identity 与登记一致
（`SourceReadCoordinator.cs:517`；`SourceAccessRegistry.cs:62-98`）。若纠错后的条目与路径不匹配，
只会 typed skip（best-effort），不会铸出错误 grant，也不会绕开 fail-closed。

### 2.3 UNFREEZE 判定（哪份/几 pins）

| 契约/面 | 本卡是否变化 | 判定依据（HEAD 字节） |
|---|---|---|
| **C-16 §2.4 `AuthorizeSourceReadForRun`** | **0**：命令/字段/校验顺序/per-page 匹配/零 DB 写/幂等均不变；Host 选择哪一个**已授权**条目去铸 grant 不在 §2.4 的 wire 语义内；Core per-page 匹配键是 `source_id/version/entry/facts`，**不含 registry_id/generation**（`source_read_refs.py:558-594`） | `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:76-93`；`core_service.py:4965-5069` |
| **C-16 §2.5 `ReattestSourceLocation`** | **0**：本卡不发送、不改变 reattest；Core 行由既有 L-S4-B 流程处理 | `:95-108` |
| **C-17 §5.3 fail-closed** | **0 字节**：target 自己的 registry 缺失 → unresolved（无 grant/无命令）；撤销 → unresolved；generation 漂移 → unresolved；枚举只读守卫、`source_list_scan_targets` 零写、上限/identity_digest 规则都不变。变化的只是「同路径另一条更老的已撤销历史行不再否决 target 自己的 live 授权」 | `FEA-C17_SOURCE_SYNC_DRAFT.md:279`；`SourceScanScheduler.cs:1957-1988` |
| **C-15 §5 `SourceAccessRegistry`** | **0**：`List/Authorize/Revoke/Load/Save` 语义与字节不变；`Authorize` 仍逐请求复核根 identity，不自动重建/不自动重授权（`:313`）；撤销仍 generation+1（`:315`）；本卡对 registry 只读 | `FEA-C15_SOURCE_STORAGE_DRAFT.md:293-318` |
| **C-06 / C-07 / M2-C1** | **0**：无新命令/能力/错误码/接口；API inventory 61 不变 | 实测 EXIT=0 |
| **pins** | **18/18 全不变**（C16 `a7f57ebdbd67`、C17 `aefa0fa5b17e`、C15 `f9e376a0ed4c`） | `verify_pins.ps1` 实测 PASS |

**判定：READY-TO-FREEZE（0 UNFREEZE / 18 pins）。**
依据是 DSH 已在 L-S4-B-1 S-2 采纳并落盘的口径：C-17 §5.3 的 fail-closed 主体是 **target 自己的
registry**，同路径 sibling revoked 行不是 target 的 registry（B1 卡 `:46`；B1 scope review
`:241-248`、`:491`；B1 r1 复核 0 pins）。本卡只是把同一口径应用到 Run 面。

**条件说明（必须写进卡面，避免将来歧义）**：若 DSH 不采纳该口径，则「同路径任意 revoked 行都
veto」会被读成 C-17 §5.3 的语义变更 → 需要 **C-17 1 pin UNFREEZE + 独立安全复核**，
且该变更会同时推翻 L-S4-B-1 的 0-pin 判定。那时应作独立治理决策，**不要**把本卡标 BLOCKED。
在采纳口径不变的前提下，本卡不需要任何 UNFREEZE。

### 2.4 红线（实现卡必须逐条保持）

| 红线 | 保持方式 | 判别性 AC |
|---|---|---|
| **不得自动重新授权** | 不调用 `Register`/`Revoke`/`Reset`；live entry 只能由 B1 显式动作产生 | 去掉 B1 的 revoke+register → 无 live 条目 → 仍 unresolved；registry 结构前后相等（除既有 `last_used_at` 审计） |
| **不得自动重建 identity** | 不写回 roots/volume/file/identity_facts；只读 live 条目的登记身份 | 删除 identity 检查或写回 roots → 红；同路径替换文件 → mint typed fail-closed |
| **不得因撤销后自动放行** | target 自己的 `RegistryId` 若 revoked → unresolved；绝不 fallback 到同路径 live sibling | target 指向 revoked id + 同路径 live 条目 → 仍 unresolved |
| **不得删除/改写 revoked 旧行** | 旧行保留；`Revoke` 语义不变 | 解析/铸造前后旧行仍在、`revoked_at` 不变 |
| **不得放松非枚举 target 语义** | `ResolveRegistryEntry` 零改动；非枚举 Run target 仍走 path resolver | 把修复错误地应用到非枚举 target → 既有/新增负例红 |
| **不得放松 path/身份校验** | `Registry.Authorize` 逐请求复核根包含与卷/文件身份 | 删掉 `Authorize` 或 identity 比较 → 红 |
| **不得扩授权面** | 无新命令/能力/错误码/UI 端口；无 path 上 wire；不改 Core/Python/schema/依赖 | 接口/registry/API 计数变化 → 红；wire 出现绝对路径 → 红 |
| **不得夸大** | 只承诺「B1 显式重授权 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类恢复」；不承诺自动恢复/自愈/撤销后放行；不承诺扫描面/B2/folder/2C | 文案出现「自动恢复/自愈/Run 全面恢复」→ 红 |

### 2.5 为什么否决 (b)（补充）

1. **授权主体错位**：`ResolveRegistryEntry(entries, path)` 不知道 target 是谁；让它接受「同路径新
   live」等于让 path 而不是 target 的 registry id 决定授权。对枚举 target 比 (a) 更弱。
2. **歧义规则膨胀**：B1 可多次重授权，registry 里可能有多条 revoked、甚至多条 live；时间序解析
   （`CreatedAt` vs `RevokedAt` 的精度/时区）需要在 resolver 里重实现 planner 逻辑
   （`SourceRootReattestPlanner.cs:227-238` 已有同规则），且不能复用 `source_id` 约束。
3. **影响所有 caller**：非枚举 target、containment fallback、未来任何 caller 都会受影响；
   (a) 只改枚举分支。
4. **C-17 复核成本**：把「revoked exact fail-closed」改成「新 live 可覆盖」正是
   `C16-V15-BATCH-scope-r1.md:117` 已判定的语义面；需要 C-17 UNFREEZE + 独立安全复核，
   而收益只是「少一个分支」。
5. **没有额外收益**：target 自己的 live entry 已在枚举阶段被 `TryMap` 核验
   （`SourceScanScheduler.cs:2369-2374`），Run 面再用它是更强、更精确的授权来源。

---

## 3. Q3 拆卡/范围

### 3.1 单卡还是并入

**推荐：独立单卡 `FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1`（保持 proposed 卡，冻结为 ready）。**

| 候选 | 建议 | 理由 |
|---|---|---|
| **并入 L-S4-B-1（done）** | **否** | B1 的 delivery（`bcc88e4a2`）与证据（`0c1390b2a`）已冻结；其 `allowed_paths` 不含 `HostRuntime.cs`（卡 `:21-28`），`out_of_scope` 明写 HostRuntime/RunSourceRange（`:31`），S-4 明写另卡（`:48`）。重开 done 卡会破坏 append-only 生命周期、证据 pin 与 r1 Review 的有效性 |
| **并入 B2 `roots_available`** | **否** | 无消费者、文件面（registry 投影/wire）不同；混入会把「wire 投影 + 执行解析」压进一个 Review |
| **并入 2C 长 Run（L-G1）** | **否** | 2C 是新 host-control/续期设计，成本/契约面完全不同 |
| **独立单卡（本卡）** | **是** | 一个分支 + 测试/证据；同根因收口，可独立 Review/集成 |

### 3.2 推荐 In / Out（文件级）

**In（推荐）**

1. `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md`（冻结卡面/AC/status）。
2. `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md`（本报告 + 后续实现 Review）。
3. `doc/handoffs/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md`。
4. `verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/**`（EV/logs/manifest/scope/discrimination）。
5. `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`：**只改** `RunSourceRange.Resolve`
   的枚举分支与 XML 注释；不改 `RunSourceAuthorizer`、`ScanSourceOnDemandAsync`、
   `RunCommandPolicy` 或任何其它方法。
6. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRunRangeResolutionTests.cs`（新增）：
   纯函数矩阵（见 §4.2）+ 用脚本化 authorize 的 authorizer 集成负例（unresolved → 不 mint；
   resolved → mint 一次）。
7. `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs`：新增一条
   `[Fea11RunGrantIpcFact]` 真实 IPC 闭环（见 §4.3），复用该文件既有 `SeedAsync` /
   `AlignRegistryAsync` / `Fea11RunGrantIpcFact`。

**Out**

- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`：`SelectEnumeratedEntry` /
  `ResolveRegistryEntry` **零改动**（如有必要只改注释，需 DSH 同意后加 allowed_path）。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs`：`List/Authorize/Revoke/
  Load/Save` 语义零变化。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`：mint/authorize/reattest
  语义零变化。
- `apps/desktop-avalonia/src/NewManga.App/**`（含 `SourceRecoveryModels.cs`）：B1 显式动作不变。
- `doc/plan/**`、`doc/contracts/**`：C-15/C-16/C-17/C-06/C-07/M2-C1 零字节。
- `src/**`、schema/迁移、依赖、`CORE_PROTOCOL_MINOR`。
- 扫描执行面（B1 done）、B2 `roots_available`、folder（L-S4-2）、多根 first-root、
  L-S4-1/L-R1、2C 长 Run、UI 视觉/交互。
- 自动重新授权/自动重建 identity/撤销后自动放行；删除/改写 revoked 行；真实用户数据；push；
  手工改 `TASK_LEDGER`。

### 3.3 建议 allowed_paths（供 DSH 冻结参考）

```yaml
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md
  - doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md
  - verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/**
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRunRangeResolutionTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
```

> 当前占位卡的 `allowed_paths` 只有 4 条 doc/verification（卡 `:21-25`）；冻结时必须补齐上述
> 生产/测试路径，否则实现第一步就 scope 红。`SourceScanScheduler.cs` **不在** allowed_paths
> （复用现有 helper，不改扫描面）。

### 3.4 AC 草案（可判别 / fail-closed / 零漂移 / 门禁）

> 以下为 scope review 建议稿，**未冻结**；编号/措辞由 DSH 定稿。

| ID | AC | 判别性（去掉修复/放宽即红） |
|---|---|---|
| **AC-RUN-1 枚举 target 的 Run 范围恢复（主 AC）** | 给定「旧条目已 revoked（同 locator/root path，generation=2）+ 同路径新 live 条目（generation=1，同一物理身份）+ 枚举 target 携带 live `(registry_id, generation)`」，`RunSourceRange.Resolve` 必须返回该 source 到 `Targets`（`RegistryId/Generation` = live），`Unresolved=0`；scope 的 path/kind/version/容器成员与现行为一致 | 仍走 path-only resolver（或把修复去掉）→ 同一 fixture `Unresolved=1`、`Targets` 为空；纯函数断言 live 条目被选中 → 绿/红可判 |
| **AC-RUN-2 fail-closed 矩阵与「不回落 sibling」** | target 自己的 registry：缺失 → unresolved；revoked → unresolved；generation 漂移 → unresolved；即使同路径同时存在 live sibling 也不采用；以上全部**零 grant、零 `AuthorizeSourceReadForRun` 帧**（`targets` 为空时不发命令） | 把 `RevokedAt`/`Generation` 检查或 own-id 选择去掉 → 负例红；接受 sibling live → 红；unresolved 仍发命令 → 红 |
| **AC-RUN-3 非枚举 target 语义零变化** | `ResolveRegistryEntry` 字节不变（exact-first、revoked-exact → null、containment fallback）；非枚举 Run target 在同状态（同路径 revoked+live）下仍为 `Unresolved`；既有 `RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`、`RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources` 原样通过 | 把 own-entry 逻辑用于非枚举 target（或改全局 resolver）→ 新增的非枚举负例红；既有 Run 范围测试红 |
| **AC-RUN-4 冷源 on-demand 分类恢复** | 枚举 target 为 live 但其 Core version 不在 `SourceIdentityCache` 时，`RunSourceRange.Resolve` 必须把它放进 `ColdSources`（而不是 `Unresolved`）；authorizer 对其执行恰 1 次 bounded on-demand scan，第二次 Resolve 后该 source 进入 `Targets` 并参与 mint；预算/超时/失败仍为 skip（`MaxOnDemandScansPerSlice=8`、30s） | entry 判定仍短路 cold → `ColdSources` 空、`Unresolved=1` 红；on-demand 被调用 0 次或 >1 次 → 红 |
| **AC-RUN-5 无自动授权/无 identity 重建/不写 registry/不抛** | 解析前后 `DescribeRegistryEntries`（不含既有 `last_used_at`）结构相等；无 `Register`/`Revoke`/`Reset`；旧 revoked 行保留；Run 范围解析对任何 Host 侧失败最多计 `unresolved`，不得向 `AuthorizeSliceAsync` 抛新异常（保持 best-effort） | 解析路径写 registry / 调 Register 或 Revoke / 删旧行 → 红；注入重复 registry id 或不可读条目时抛异常而非 unresolved → 红 |
| **AC-RUN-6 gated 真实 IPC 闭环（before/after）** | 真实 Core + 真实 `SourceAccessRegistry` + 真实 referenced 页：registry `Revoke(旧)` + `Register(同路径)`，Core `source_locations` 对齐到 live（复用 `AlignRegistryAsync`）→ 枚举 target 带 live id → `RunSourceRange.Resolve` → `AuthorizeRunAsync` 返回 `bound_pages>=1`、mint=1 → `resolve_page_resource` 成功；修复前同一 fixture：`Unresolved=1`、无 mint、`resolve_page_resource` typed 拒绝；wire/日志无绝对路径，且无部分成功 | 回退修复后同一 test → `Unresolved=1`、无 bind、页读拒绝（before 可判）；断言只测 pure resolver、不跑真实 bind → 不满足闭环 |
| **AC-RUN-7 零契约/零接口漂移** | C-15/C-16/C-17/C-06/C-07/M2-C1 字节零 diff；pins 18/18（C16 `a7f57ebd`、C17 `aefa0fa5`、C15 `f9e376a0`）；`CORE_PROTOCOL_MINOR=3`；API inventory 61 不变；无新命令/能力/错误码/schema/依赖；scope diff ⊆ allowed_paths | 任一契约/协议/接口变化 → 红 |
| **AC-RUN-8 门禁/不夸大/触发口径** | check（默认 + `-TaskPath`）PASS；全量 pytest/.NET 不低于**本卡起点重测值**；已知 flaky 原样记录 + 隔离复跑；跑后 `verification/FEA-09` 恢复 clean；卡/Handoff/EV 不写「自动恢复/自愈/自动重新授权/撤销后放行/扫描面恢复/B2/folder/2C」；恢复口径固定为「B1 显式动作 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」 | 出现红线承诺句 → 红；未重测就写旧基线 → 红；把「Run 预授权恢复」写成「Run 全面恢复」→ 红 |

### 3.5 冻结时的边界提醒

- 占位卡 `out_of_scope` 现文是「生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，
  未冻结」（卡 `:26-27`）；冻结时应改为「只允许 In 列表中的 Host 代码/测试，不碰 Core/契约/
  registry 结构」。
- `status: proposed → ready`、`base_commit` 设为冻结时 clean head（当前 `3e19f37db` 或更新）、
  `evidence_dir` 保持 `verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1`；`suggested_owner: codex`
  可按 DSH 可用性调整（owner/reviewer 由 DSH 指派；Review 必须上下文独立）。
- `depends_on: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1`（done）正确；不要新增对 B2/2C 的依赖。
- 不要在本卡承诺「多根 first-root」「folder」「`source_reset_registry` 后恢复」「2C 长 Run」。
- 把「Run 面同根因」与「扫描执行面已恢复」分开写：本卡不是 B1 返修，B1 的
  AC-SER-1…6 判定不受影响。

---

## 4. Q4 测试/证据

### 4.1 现有 fixture/测试覆盖

| 资产 | 覆盖 | 与本卡的关系 |
|---|---|---|
| `SourceRegistryTests.RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`（`:257-295`） | 非枚举 target 的范围解析、未解析计数、空 known/空 scope | **不覆盖**缺口；`ScanTarget` helper 无 `RegistryId`（`:171-172`） |
| `SourceRegistryTests.RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources`（`:761-781`） | 冷源分类与 warm 版本 | 同上，非枚举 |
| `SourceRegistryTests.RunAuthorizerPerformsOneBoundedOnDemandScanPerColdSource`（`:813-845`） | cold on-demand 一次/二次 warm | 本卡 AC-RUN-4 的模板；需加枚举 target 变体 |
| `SourceRegistryTests.RunSourceRangeCarriesContainerMemberIdentitiesVerbatim`（`:957-1002`） | 容器成员透传 | 非枚举；不受影响 |
| `SourceScanExecutionRecoveryTests.SelectEnumeratedEntry_*`（`:87-154`） | **枚举 target + 同路径 revoked sibling** 的纯函数矩阵；`:100` 直接断言 path-only resolver 返回 null | 复用其状态构造/断言口径；它是扫描面的测试，不覆盖 Run 面 |
| `Fea11ScanIpcTests.ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport`（`:551-690`） | 真实 Core：B1 revoke+register（`:562-573`，root 同为 `oldZip`）→ reattest → 枚举 live target（`:618-624`）→ tick `ok`（`:680-689`） | **证明缺口状态真实存在**；只覆盖扫描执行面；Run 面零断言 |
| `Fea11ScanIpcTests` 证据 JSON | `old_registry_id`（revoked）/ `live_registry_id` / `recovered_target` / `tick_verdict=ok` | 可作为本卡 before 状态的旁证（Run 仍未解析） |
| `SourceRecoveryIpcTests.SamePathReplacement_...`（`:49-189`） | 真实 Core：B1 显式重授权（revoke+register，`:98-112`）与 in-place refresh（`:166-189`） | 证明「同路径 revoked + live」是 B1 的常态产物；不覆盖 Run |
| `Fea11RunGrantIpcTests`（gated，`:29-193`、`:254-350`、`:369-...`、`:555-690`） | 真实 Core 的 Run mint+bind+resolve、folder、容器成员、wire 无路径 | **Run IPC harness 已就绪**；target 均为非枚举（`:301-302`、`:619-624`），未覆盖缺口 |
| `SourceScanSchedulerTests.RegistryResolution_...`（`:879-908`） | 非枚举 path resolver 语义（exact/containment/revoked→null） | AC-RUN-3 的判别器，保持原样 |

**结论**：现有测试**没有任何**覆盖「枚举 Run target + 同路径 revoked 旧条目」的用例；草稿卡
「未测未修」的描述准确。缺口不是测试脆弱，而是没有用例。

### 4.2 最低新增测试集（纯函数，无 Core）

新文件 `SourceRunRangeResolutionTests.cs`，建议至少 7 例：

1. `Resolve_EnumeratedTarget_UsesItsOwnLiveEntry_WhenARevokedSiblingSharesThePath`：
   断言 `ResolveRegistryEntry(entries, path)` 为 null（before 判别）、`RunSourceRange.Resolve`
   返回 1 target、`Unresolved=0`、scope 的 `RegistryId/Generation` = live。
2. `Resolve_EnumeratedTarget_NeverFallsBackToALiveSibling_WhenItsOwnEntryIsRevoked`：
   target 指向 revoked id + 同路径 live → `Targets` 空、`Unresolved=1`。
3. `Resolve_EnumeratedTarget_IsUnresolved_OnMissingRegistryAndGenerationDrift`：
   两种 typed 负例（各自 `Unresolved=1`、零 target）。
4. `Resolve_NonEnumeratedTarget_KeepsThePathOnlyResolver`：
   同一 entries（revoked+live 同路径）+ 非枚举 target → 仍 `Unresolved=1`（证明未扩大授权面）；
   若实现错误地对非枚举也用 own-id 逻辑，此例红。
5. `Resolve_EnumeratedColdSource_IsReportedAsCold_NotUnresolved`：
   枚举 live + 空 identity cache → `ColdSources=1`、`Unresolved=0`。
6. `Authorizer_EnumeratedColdSource_PerformsOneOnDemandScan_ThenMints`：
   脚本化 `onDemandScan` 填 cache；断言 resolve→cold→scan 1 次→第二次 resolve→authorize 收到 1 个
   scope（复用 `SourceRegistryTests.Authorizer` 的构造方式，`:203-215`）。
7. `Authorizer_UnresolvedEnumeratedSource_NeverSendsAuthorizeSourceReadForRun`：
   targets 为空 → `authorize` 调用 0 次；Run dispatch 仍可达（借用
   `RunAuthorizerSkipsColdCacheSourcesAndStillReachesDispatch` 的 dispatcher 模式，`:784-810`）。

判别性建议（2–3 个破坏点，写进证据）：

- 把枚举分支改回 `ResolveRegistryEntry` → 用例 1/6/7 与 gated 测试红；
- 把 `SelectEnumeratedEntry` 换成「任意 live」→ 用例 2 红；
- 把 own-entry 逻辑用到所有 target → 用例 4 红（证明没有扩大授权面）。

### 4.3 gated 真实 IPC：能否复现/验证

**能，且不需要完整 Core reattest。** 关键事实：

- Core 的 Run per-page 匹配只比较 `scope.source_id`、`scope.version`、entry（entry_key/locator/ordinal）
  与 `source_locations` 的物理身份；**不比较 registry_id/generation**
  （`source_read_refs.py:558-594`；C-16 §2.4 `:90`）。
- 因此 Host 侧「`Revoke(旧)` + `Register(同路径同物理身份)`」已足够让真实 Core 接受新 grant 的绑定；
  Core `source_locations` 可用既有测试 helper `AlignRegistryAsync`
  （`Fea11RunGrantIpcTests.cs:1083-1108`，直接 SQLite UPDATE registry 两列）对齐到 live，
  无需真实 reattest 往返。
- 「reattest + 生产枚举恢复」这一环已由 L-S4-B-1 的 gated 证据覆盖
  （`Fea11ScanIpcTests.cs:551-690` + `ipc-closed-loop.json`）；本卡只需证明「枚举 target 带 live id
  时 Run 范围解析 + 真实 bind + 真实页读」这一环，避免重复 B1 的昂贵流程。

**建议测试步骤（一条 gated Fact）**：

1. `SeedAsync` 造真实 referenced 页（复用既有 seed）。
2. `registry.Register(root)` → 得 `old`；`AlignRegistryAsync(db, old.RegistryId)`。
3. B1 显式动作：`registry.Revoke(old.RegistryId)`；`registry.Register(root)` → `live`；
   `AlignRegistryAsync(db, live.RegistryId)`（模拟 L-S4-B reattest 的结果，注明是测试对齐）。
4. 构造生产形状的枚举 target（`SourceScanTarget(..., RegistryId: live.RegistryId, Generation: 1,
   SourceKind: "zip", IdentityDigest: ...)`）或直接走生产枚举器（若代价可接受）。
5. **Before 断言**（不在产品里开关分支）：同一 entries/path 直接调用
   `HostSourceScanExecutor.ResolveRegistryEntry(entries, path)`，断言其为 null（这正是修复前
   `RunSourceRange.Resolve` 会走到的入口）；证据 JSON 记 `before_resolver=null` 与
   `after_unresolved=0`。**不得**为了让测试变绿而在生产代码里留 feature flag。
6. 运行 `coordinator.AuthorizeRunAsync(scopes, "reocr_all", scope)`：修复后 `BoundPages>=1`、
   `MintedGrants=1`、`Skipped=false`；随后 `resolve_page_resource` 成功。
7. 失败面：同一个 target 但 `RegistryId` 指向 revoked 条目 → `Unresolved=1`、不 mint、
   `AuthorizeSourceReadForRun` 零帧。
8. 红线断言：`wire.ndjson`/Core stderr 不含 fixture 绝对路径；`DescribeRegistryEntries`
   前后结构相等（只允许 `last_used_at`）；无 `ReattestSourceLocation` 新增帧（本卡不 reattest）。

成本/风险：新增 1 个真实 Python Core 进程（启动 ≤90s 超时，正常数秒）+ fixture 目录在
`<repo>.workspace/FEA-11-RUN-GRANT-1/fixtures/**`；gated 默认 skip
（`NEWMANGA_FEA11_IPC=1`，`:1325-1333`），不拖慢常规 CI。

### 4.4 全量门禁成本 / flaky / 基线

| 项 | 记录值/成本 | 说明 |
|---|---|---|
| 全量 pytest | 既有记录 **3360 passed / 10 skipped**（L-S4-B closeout；≈252s） | 本卡无 Core 改动；门禁用，不得低于本卡起点重测值 |
| 全量 .NET | 既有记录 **1652 passed / 0 failed / 94 skipped**（L-S4-B-1 closeout；B1 +8） | 本卡预计 +5～8 单测 +1 gated（gated 默认 skip 计入 skip），必须重测 |
| 基线矛盾 | `doc/STATUS.md:20` 仍写 **3317/10、1617/0/93** | 与 B1 closeout 不一致；冻结/释放前必须在 clean head 重测并写「本卡起点」 |
| 已知 flaky | `FluentResidual2VisualEvidenceTests`（历史 Lead 组合跑曾命中，隔离复跑 1 passed）；FluentAssertions/Threading/反射偶发（B1 r1 记录） | 原样记录 + 隔离复跑；不得「重跑到绿」 |
| 写入卫生 | 全量 pytest 历史会改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；`SourceRegistryTests` 写 `verification/FEA-09/native-registry/**` | 跑后 `git status`；只恢复**测试产生的**变更；不把测试噪声当交付 |
| gated IPC | `NEWMANGA_FEA11_IPC=1`；fixture 在 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-1\fixtures\**`；不写 tracked 证据 | 一条证据即可，不要为证据跑全量 |
| 建议命令（实现卡） | `dotnet test apps/desktop-avalonia/NewManga.sln --filter "FullyQualifiedName~SourceRunRangeResolution"`；`--filter "FullyQualifiedName~SourceRegistryTests"`；`$env:NEWMANGA_FEA11_IPC='1'; dotnet test ... --filter "FullyQualifiedName~Fea11RunGrantIpcTests"`；`python -m pytest tests -q`；`pwsh -File tools/governance/verify_pins.ps1`；`check.ps1`（默认 + `-TaskPath`）；`python tools/generate_api_inventory.py --check` | 命令为建议稿；按仓库脚本/路径校准 |

### 4.5 建议证据目录

`verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/`，至少：

- `EV.md`（AC 逐项、before/after、limitation、§5.3 主体解释引用）
- `logs/host-unit.log`（新纯函数/authorizer 测试）
- `logs/host-ipc.log`（gated 1 passed + head）
- `logs/discrimination.log`（2–3 个破坏点，含 restore sha）
- `logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/gates.log`
- `logs/run-range-ipc.json` / `.txt`（gated 的 `before_unresolved`/`after_bound_pages`、wire 无路径）
- `scope-validation.log`、`changed-files.txt`、`RESOURCE-MANIFEST.json`

---

## 5. Q5 优先级与 DSH 裁决点

### 5.1 与队列项的对比

| 项 | 性质 | 用户可见性 | 成本/契约 | 相对建议 |
|---|---|---|---|---|
| **L-S4-B-2（本卡）** | 已登记 limitation 的 Run 面缺口（重新授权后 Run 仍被拒/页读失败） | **中-高**（直接阻断 Run） | **小**：Host-only、0 pins、1 文件 1 分支 + 测试 | **优先冻结/实现**；L-S4-B 收尾的最后一个已知洞 |
| **B2 `roots_available`** | wire 投影，无消费者 | 当前无 | 小（C-16 已冻结字段），另卡 | **延后**到 roots UI/多根管理立项 |
| **2C 长 Run（L-G1）** | >300s 长 Run 失权/中断 | **高** | 高：新 host-control/续期设计，可能多 pin | 用户价值更高但成本大；建议本卡先收口，然后 2C 设计/实现（或并行设计） |
| **L-R11** | gate 统一/审计一致性 | 低 | 小-中；0 pin | 可穿插 |
| **C-04b** | 8 项文档 residual | 无 | 极小；0 pin | 穿插 |
| **SCAN-RH** | 可观测性/limitation | 低 | 小；0 pin | 穿插 |
| **UI P3** | 视觉/交互 | 低 | 小；0 pin | 最后 |

**推荐顺序（供 DSH 裁决）**：**① 冻结并实现本卡 → ② 2C 长 Run 设计/实现（或与本卡并行设计）
→ ③ B2 等 roots UI 立项后再做 → ④ L-R11 / C-04b / SCAN-RH 穿插 → ⑤ UI P3 最后。**
如果 DSH 认为 2C 必须优先，本卡可以后移，但应明确保留「重新授权后 Run 仍被拒」这一已知行为，
不要把 L-S4-B 线标成完全收口。

### 5.2 DSH 裁决点（含推荐）

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **D-1** | 采用哪种形状：枚举 target 用自身 live entry / 改全局 resolver / live-only 过滤？ | **(a) 枚举 target 用自身 live entry**（复用 `SelectEnumeratedEntry`） | 决定 0 pins 还是 C-17 1 pin |
| **D-2** | 是否沿用 L-S4-B-1 S-2 的 §5.3 口径（fail-closed 主体 = target 自己的 registry）？ | **沿用**（→ 0 UNFREEZE）；若不沿用，走 C-17 UNFREEZE 1 pin + 独立安全复核，并同时回看 L-S4-B-1，**不要 BLOCKED** | 决定 UNFREEZE 判定与文档措辞 |
| **D-3** | 拆卡：本卡独立 vs 并入 B1/B2/2C？ | **独立单卡**；B1 done 不重开 | 决定 Review 规模与生命周期 |
| **D-4** | gated 证据取「Host revoke+register + AlignRegistry」轻量闭环，还是完整 Core reattest 闭环？ | **轻量闭环**（Core 匹配不看 registry id；reattest 环已由 B1 gated 覆盖）；证据里写明该测试对齐 | 决定 gated 成本与可判性 |
| **D-5** | 冻结口径：status/base_commit/allowed_paths/AC 编号/owner | `status: ready`；`base_commit`=冻结时 clean head；按 §3.3 补 allowed_paths；AC-RUN-1…8 定稿；owner/reviewer 由 DSH 指派 | 决定实现卡能否开工 |
| **D-6** | 是否顺带清 Run 的 scheduler backoff？ | **不**；本卡不依赖 backoff；AC-RUN-8 写「预授权不读 backoff」 | 避免多一处调度行为变更 |
| **D-7** | 基线：STATUS 3317/1617 vs B1 closeout 3360/1652 | **clean head 重测并写「本卡起点」**；不继承任一旧数 | 决定 AC-RUN-8 可判性 |
| **D-8** | 优先级 vs 2C | **本卡先**（小、0 pin、消除已知 Run 拒绝）；2C 随后/并行设计 | 决定下一活动 Task |

### 5.3 风险

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R1 | 修复被误读为「C-17 §5.3 放宽/撤销后自动放行」 | 中-高 | 卡面/Review 明确「只改枚举 target 的授权来源；target revoked/缺失/漂移仍 unresolved」；AC-RUN-2/3；保留旧 resolver 测试 |
| R2 | 错误地把 own-entry 逻辑用到非枚举 target（授权面扩大） | 中 | AC-RUN-3 + 非枚举负例（§4.2 用例 4） |
| R3 | `SelectEnumeratedEntry` 的 `SingleOrDefault` 抛异常（重复 id） | 低 | `Load` 已强制 unique registry id（`SourceAccessRegistry.cs:168-170`）；建议 Run 分支 try/catch → unresolved（AC-RUN-5） |
| R4 | verify 与 mint 之间发生 revoke/漂移 | 低 | `IssueLockedAsync → Authorize` 逐请求复核（`:517`、`:62-98`）；typed skip，不放行 |
| R5 | gated fixture 噪声/路径泄漏/CI 成本 | 中 | 复用既有 workspace fixture；wire 断言无路径；gated 默认 skip；不写 tracked 证据 |
| R6 | 基线陈旧导致 AC 误判 | 中 | clean head 重测；记录起点/终点/差值归属 |
| R7 | 全量 pytest 改写 tracked `verification/FEA-09` | 中 | 跑后 `git status`；只恢复测试产生的变更；优先 gated/定向 |
| R8 | 把「Run 预授权恢复」写成「Run 全面恢复/自动恢复」 | 中 | AC-RUN-8 措辞红线；只承诺「B1 显式动作 → refresh/reattest → 枚举 → 预授权/冷源分类」 |
| R9 | Scheduler 未启动/枚举失败时 `known` 为空，本卡不产生 grant | 低-中 | 属既有配置行为；卡面 limitation 明写，不承诺 |
| R10 | 同路径「revoked 行 + live 行」只由 B1 显式动作/重导入产生；其他历史重复条目 | 低 | `SelectEnumeratedEntry` 只认 target 自己的 id，不依赖条数/顺序；同 id 唯一由 Load 保证 |
| R11 | 文档漂移（PLAN 仍写 L-S4-B-1 ready；STATUS 基线旧） | 低 | 本卡不修（不在 allowed_paths）；DSH closeout 时统一维护 |

---

## 6. 真实性声明

1. **唯一写入**：本评审只写了
   `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md` 这一个文件。**未**修改/删除/移动任何
   生产代码、测试、契约、冻结记录、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或证据字节；
   **未**执行 `git add`/`git commit`/`git push`；**未**运行会写仓的构建/测试。
2. **独立性**：评审者为独立上下文的 fresh subagent（DSH 子会话
   `0f28cb0d-82e2-4f50-8c13-3cfd941d5003`），未参与 `FEA-11-L-S4-B-AUTO-RECOVERY-1`、
   `FEA-11-L-S4-B-PREREQ-1`、`FEA-11-L-S4-B-1`、B2、L-S4-A/B1 或任何 Run/folder 卡片的实现、
   返修或审查；只读被审 head。
3. **事实优先级**：所有代码/契约断言均来自 `3e19f37db` 的工作树字节（`git status` clean、
   无并发提交），逐条给出 `path:line`；未把卡面/Handoff/Review 的自述当作实现事实（引用时标注
   「既有记录」）。B1 的 gated 证据 JSON 作为「缺口状态真实存在」的既有证据引用，不当作本卡实测。
4. **实测命令**（EXIT 见 §0）：`git rev-parse --abbrev-ref HEAD`、`git rev-parse HEAD`、
   `git status --porcelain`、`git log -1`、`git diff --name-only 0c1390b2a..HEAD -- apps src tests`、
   `git diff --name-only 0c1390b2a..HEAD`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`、
   `check.ps1`（默认 + `-TaskPath`）、`python tools/generate_api_inventory.py --check`
   （`PYTHONDONTWRITEBYTECODE=1`）。
5. **NOT_RUN**（未跑、不声明 PASS）：全量 `pytest tests`、全量 `dotnet test`、定向 .NET、
   gated 真实 IPC、byte-level 契约复核、任何破坏-恢复实验。理由见 §0（只读约束 + 单文件写入约束）。
   §4.4 的数字均为**既有记录**，不是本评审实测。
6. **判别力声明**：本报告未做「破坏-恢复」实验；§3.4/§4.2/§4.3 的「判别性」是给实现卡/Review 的
   **待验证项**，不是本轮已完成证据。
7. **建议性质**：本报告的 In/Out/allowed_paths/AC/UNFREEZE 判定均为**建议**；scope 冻结、
   契约字节变更、Review Appointment、findings 处置与集成验证属 DSH。
8. **limitation**：本报告不评估 B2/2C/L-R11/C-04b/SCAN-RH/UI P3 的实现细节，仅做优先级比较；
   不声称任何测试或 gated IPC 已在当前 head 通过；不声称 DSH 已采纳 §5.3 解释（只陈述其在
   L-S4-B-1 S-2 已落盘的口径）；不声称 Run 面之外的任何恢复。
