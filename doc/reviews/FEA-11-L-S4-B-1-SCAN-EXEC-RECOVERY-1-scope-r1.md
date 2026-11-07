---
task: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
title: 扫描执行面恢复（L-S4-B-1：reattest 后 tick 仍被同路径 revoked 旧条目 fail-closed 拦住）权威 scope review r1
reviewer: fresh subagent（独立上下文；未参与 L-S4-B / L-S4-B-1 / B2 / L-S4-A / B1 的实现、返修或审查；只读被审 head）
session: fc6e9df6-336c-49fb-9d2c-154ec6875fb1（DSH 子会话；独立上下文）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 scope review（fresh context / read-only / 非作者 / 非实现审查者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: b34060b2e98b70230747791fa9d50c0aba7cb419
reviewed_head_note: >-
  任务书给的是 `b34060b2e`（main，clean）。实测 HEAD、分支与任务书一致；评审起点
  `git status --porcelain` 为空，结束时仅本报告未跟踪。`30bdeb4ce..HEAD` 的
  `apps/`、`src/`、`tests/` 零 diff（仅 docs/verification），故 L-S4-B 交付时的 gated IPC
  证据（tick `last_result=error`）在当前 head 仍然有效。
verdict: READY-TO-FREEZE
verdict_scope: >-
  推荐形状为 **Host-only：枚举 target 执行时使用其自身已被 `VerifyEnumeratedTarget` 核验的
  `(registry_id, generation)` 条目**，不改 `ResolveRegistryEntry` 对非枚举 target 的语义，
  不碰 Core/契约/schema。按此形状 **0 UNFREEZE / 18 pins 全不变**，可冻结。
  若 DSH 选择另一形状——修改 `ResolveRegistryEntry` 对「同路径 revoked 旧条目 + 新 live 条目」
  的全局接受语义——则构成 C-17 §5.3 fail-closed 的语义变更，**需要 C-17 1 pin UNFREEZE +
  独立安全复核**，本报告不推荐。B2 `roots_available` 实现仍应另卡/延后（无消费者）。
---

# FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1：权威 scope review r1

> **结论先行。**
>
> 1. **缺口成立且确定性可复现。** B1 显式重授权 = 撤销同路径全部非撤销条目 + 注册一条新条目
>    （旧条目只置 `revoked_at`、永不删除）；L-S4-B 的 reattest 把 Core `source_locations` 的
>    `registry_id/authorization_generation` 条件更新为 live 条目；下一次枚举因此恢复，
>    `TryMap` 也把 target 映射为 live `(registry_id, generation)`。但 tick 执行时
>    `VerifyEnumeratedTarget` 已按 live registry id 验证通过后，`ScanAsync`
>    仍然调用 **按路径** 的 `ResolveRegistryEntry(target.Path)`；该方法对整个 registry 做
>    path-exact 扫描，先命中同路径 revoked 旧条目就 `return null`（`SourceScanScheduler.cs:1899-1903`），
>    即使同时存在 live exact 条目（`:1905`）也不采用 → `Error("SOURCE_ACCESS_DENIED")`
>    （`:1514-1519`）→ tick `last_result=error` + backoff。gated IPC 证据
>    `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json` 的
>    `tick_verdict.last_result=error` 是如实的（测试 `Fea11ScanIpcTests.cs:675-676`、`:706-711`）。
> 2. **根因不是「过期视图」，而是「解析权限来源」用错了。** scheduler 并不缓存 registry 视图：
>    每次 `ScanAsync` 都重新 `Registry.List()`（`SourceScanScheduler.cs:1873-1874`），枚举器也每次
>    重新 `SnapshotEntries()`（`:2077`、`:2084`、`:2217-2226`）。reattest 之后的 refresh 已经把
>    scheduler 的 target 更新为 live 条目（`MergeTargetsLocked` `:797-819`），watcher 也已按
>    target 的 registry id 重新 arming（`SourceWatcher.cs:438-465`）。真正的问题是 executor 在
>    target 已携带可信 registry id 的情况下仍退回到 path-only 解析；刷新任何「视图」都不会改变
>    这个结果，因为 revoked 旧条目按设计永久留在 registry 里（`SourceAccessRegistry.cs:100-110`；
>    B1 注释 `SourceRecoveryModels.cs:399-409`）。
> 3. **推荐的最小修复是 Host-only 的枚举执行解析**：枚举 target 使用 `VerifyEnumeratedTarget`
>    已经核验过的同一条 live entry 去铸 grant；非枚举 target 继续走既有
>    `ResolveRegistryEntry`（exact-first / revoked-exact fail-closed / containment fallback 全部
>    不变）。这样既恢复执行面，又不放松「target 自己的 registry 被撤销/缺失/代次漂移 → fail-closed」，
>    也不允许「撤销后自动放行」。按此方案 **0 契约 UNFREEZE、0 pins 变化**。
> 4. **不建议修改 `ResolveRegistryEntry` 的全局语义（同路径新 live + `CreatedAt>RevokedAt` 接受）。**
>    这是把 C-16 §2.5 的 reattest 候选规则搬进 resolver：需要处理多 revoked/多 live 的歧义、
>    时间解析、非枚举 target 的语义变化，并且是 `C16-V15-BATCH-scope-r1.md:117`（b2）已经判定过的
>    C-17 §5.3 语义面；代价（1 pin + 独立安全复核 + 语义漂移）明显高于收益，而推荐形状不需要它。
> 5. **拆卡：单卡即可，B2 不并入。** 本卡 = 扫描执行面（`SourceScanScheduler.cs`）为主，
>    建议把同根因的 Run 源范围解析（`HostRuntime.cs` `RunSourceRange`）一并修（约 5–10 行）；
>    若 DSH 想压窗口，可把 Run 部分拆成后续 `L-S4-B-2-RUN-RANGE-RESOLVE`，但必须在卡面登记
>    limitation。B2 `roots_available` 无消费者、文件面不同，保持另卡。
> 6. **gated IPC 可以把 tick 从 error 验证为 ok（在 reattest 后）：可以。** 现有
>    `ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport` 已经构造出「旧条目 revoked +
>    新条目同路径同身份 + Core 行 reattest 到 live」的精确状态，并把 tick 结果写进证据；实现卡只需把
>    tick 断言从「记录 error」改为「`ok`（fixture 未变）+ 恰 1 个 `ScanSourceSync` 帧」。
>    当前 head 的生产/测试字节与 `30bdeb4ce` 完全相同，因此现有 `error` 证据就是天然的 before。
> 7. **优先级：本卡应排在 B2 之前**（B2 无消费者），也适合作为 L-S4-B 的收尾补洞；2C 长 Run 用户价值
>    更高但成本/设计面大，建议本卡先做或至少与 2C 设计并行。L-R11/C-04b/SCAN-RH 可穿插；UI P3 最后。
> 8. **DSH 需要裁决的不是「要不要 UNFREEZE」，而是 §5.3 的解释口径**：我建议按「§5.3 的 fail-closed
>    主体是 target 自己的 registry 授权，不是同路径任意历史行」解释（→ 0 pins）；若 DSH 按「同路径
>    任意 revoked 行都 veto」解释，则推荐形状变成 C-17 语义变更（1 pin），而不是 BLOCKED。

---

## 0. 只读基线与实测命令

| 项 | 值 | 来源/说明 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `b34060b2e98b70230747791fa9d50c0aba7cb419` | `git rev-parse HEAD` |
| HEAD 提交 | `2026-11-07 15:23:26 +0800 docs(fea-11-l-s4-b): r1 报告复核后附注入库（结论不变）` | `git log -1` |
| 工作树 | 起点 **clean**；结束时仅本报告未跟踪 | `git status --porcelain`（起点 0 行；命令后仍 0 行，报告写入前） |
| `30bdeb4ce..HEAD` 生产/测试 diff | `apps/`、`src/`、`tests/` **空** | `git diff --name-only 30bdeb4ce..HEAD -- apps src tests` 输出为空；其余 diff 仅 `doc/**`、`verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/**` |
| `verify_pins.ps1` | **PASS (all 18)**，EXIT=0 | 实测；C15 `f9e376a0ed4c`、**C16 `a7f57ebdbd67`**、**C17 `aefa0fa5b17e`**；C-16 为 v1.5，C-17 为 v1.1 |
| `check.ps1`（默认） | **PASS (3 warnings)**，EXIT=0 | 实测；3 warnings = 9 个非终态 Task + STATUS/PLAN 预算 80% |
| `check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | **PASS (3 warnings)**，EXIT=0 | 实测 |
| `generate_api_inventory.py --check` | **EXIT=0**；`IHostController` 54 + `IRunController` 6 + `IReaderProgressSink` 1 = **61** | 实测；与 FEA-C07 一致 |
| 只读契约核对 | C-17 §5.3 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:279`；C-16 §2.5 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:95-108`；C-16 §1 `:31`、`:35`；C-15 §5 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:293-318`；C-16 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C16.md:16`、`:109` | HEAD 字节实测 |
| 定向/全量测试 | **NOT_RUN** | 只读 scope review + 本会话「只允许写一个文件」硬约束；`dotnet test`/`pytest` 会写 `bin/obj`、`.pytest_cache`，全量 pytest 历史上还会改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`（见 §4.4）。本报告不声明任何测试 PASS。 |
| gated 真实 IPC | **NOT_RUN** | 同上；实现卡必须自行跑并入库 |
| 契约 byte-level 复核 | **NOT_RUN** | scope review 不做 byte-level 复核；UNFREEZE 判定见 §2.3 |
| 真实用户数据 / AppData / 回收站 / push | **未触碰** | — |

> 基线口径：`doc/STATUS.md:20` 仍写 pytest **3317/10**、.NET **1617/0/93**，而 L-S4-B closeout
> 实跑为 **3360/10**、**1644/0/94**（`doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md:117`、`:171`；
> `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/full-pytest.log` 尾行 `3360 passed, 10 skipped`；
> `full-dotnet.log` 各测试项目合计 1644 passed / 94 skipped）。本卡冻结/释放前必须在 clean head
> 重测一次并写「本卡起点基线」，不得直接继承任一旧数字。

---

## 1. Q1 缺口核实

### 1.1 确定性链路（B1 → reattest → 枚举恢复 → 执行仍失败）

| 步 | 事实 | 锚点 |
|---|---|---|
| 1 | B1 显式重授权 = 先撤销**同路径全部非撤销条目**，再注册**一条新条目**；旧条目只置 `revoked_at`（generation+1），永不删除，revoked 行累积 | `SourceRecoveryModels.cs:399-409`、`:473-491`、`:503-519`；`SourceAccessRegistry.cs:100-110`（Revoke 只写 `revoked_at`/generation）、`:34-52`（Register 新 GUID、generation=1） |
| 2 | L-S4-B reattest 把 Core `source_locations` 当前行的 `registry_id/authorization_generation` 条件单行更新为 live 条目（`last_verified_at` 原值），于是 Core 枚举重新投影 live pair | C-16 §2.5 `FEA-C16_SOURCE_READ_WIRE_DRAFT.md:95-108`；Host pre-pass `SourceScanScheduler.cs:2123-2196`；成功后重读一次 `:2192-2195` |
| 3 | 枚举映射要求 target 的 `(registry_id, generation)` 在 Host registry 中 live 且 generation 相等，并用该 entry 的 `roots[0]` 造 target；reattest 之后这一步通过 | `SourceScanScheduler.cs:2305-2312`、`:2321-2324` |
| 4 | scheduler refresh 把 target 合并更新（`existing.Target = target`），并通知 watcher 重新覆盖（`TargetSetChanged`） | `SourceScanScheduler.cs:797-819`、`:776-783`、`:498-512`；`SourceWatcher.cs:316-407` |
| 5 | tick 执行前 `VerifyEnumeratedTarget` 按 **target.RegistryId** 找到 live entry，验证未撤销、generation 相等、target.Path 精确命中某个 root、`SourceSecurity.Identity(root)` 与登记的 volume/file 一致 → 返回 null（允许继续） | `SourceScanScheduler.cs:1561-1647`（`:1578-1580`、`:1585-1588`、`:1590-1597`、`:1599-1610`、`:1612-1632`） |
| 6 | 随后 `ScanAsync` 调用 `ResolveRegistryEntry(target.Path)`。该方法每次 fresh `Registry.List()`（`:1873-1874`），遍历整个 registry 做 path-exact 匹配；**只要遇到同路径 revoked 条目就 `return null`**（`:1899-1903`），即使同一路径上还有 live exact 条目（`:1905` 的 `exact ??=` 根本没机会被用） | `SourceScanScheduler.cs:1873-1874`、`:1885-1926`（关键 `:1899-1903`） |
| 7 | `entry is null` → `SourceScanOutcome.Error("SOURCE_ACCESS_DENIED")`；不铸 grant、不发 `ScanSourceSync`、不发 missing observation | `SourceScanScheduler.cs:1514-1519`、`:1531-1539` |
| 8 | `ApplyOutcome` 把 Error 记为失败并施加 backoff；`LastResult="error"`；`SourceScanRecentEntry` 记 error | `SourceScanScheduler.cs:1211-1290`（`:1251-1257`、`:1292-1298`）；`SourceScanStatus.cs:67-136` |
| 9 | gated 真实 IPC 如实记录：重授权→reattest→枚举恢复（`target` 为 live），但 `tick_verdict.last_result="error"` | `Fea11ScanIpcTests.cs:675-676`、`:706-711`；`verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json`、`.txt`；`EV.md:85-89` |

**结论**：链路是确定性的，不依赖时序/并发：即使 live entry 在 registry 中排在 revoked 旧条目之前，
`ResolveRegistryEntry` 在遍历到 revoked exact 时仍会 `return null`；因此 tick 必然 error。
`VerifyEnumeratedTarget` 已经证明「target 自己的授权可核验」，失败发生在之后的**冗余第二次解析**。

### 1.2 为什么是 `error` 而不是 `skipped`

- `VerifyEnumeratedTarget` 的否定面确实用 `Skipped`：target registry 缺失 `SOURCE_REGISTRY_UNAVAILABLE`
  （`:1582`）、target registry 已撤销 `SOURCE_GRANT_REVOKED`（`:1587`）、generation 漂移
  `SOURCE_REGISTRY_BUSY`（`:1596`）、root 不可读 `SOURCE_REGISTRY_UNAVAILABLE`（`:1609`）；
  这些都不会发 grant/frame。
- 但 resolver 返回 null 走的是 `Error("SOURCE_ACCESS_DENIED")`（`:1518`）。`ApplyOutcome` 对
  `Error` 计失败并 backoff（`:1251-1257`），不是「下个 tick 再验」。因此现场表现更像「扫描失败」，
  且会逐次拉长 backoff（base 60s，最大 3600s，`:1292-1298`）。
- 这也解释了为什么 L-S4-B 的 gated 证据里 `tick_verdict.last_result="error"`，而不是 `skipped`。

### 1.3 影响面

| 面 | 是否被本缺口影响 | 事实/锚点 |
|---|---|---|
| **周期扫描 tick** | **是（主影响）** | 每个 tick 走 `ScanAsync` → `ResolveRegistryEntry` → error；无 `ScanSourceSync`，无扫描结果；backoff 累积。`SourceScanScheduler.cs:1498-1552`、`:1153-1193` |
| **冷启动/App refresh 枚举** | 否（L-S4-B 已恢复） | `RefreshTargetsAsync` + pre-pass 已把 target 映射为 live；`SourceScanScheduler.cs:689-795`、`:2115-2196` |
| **watcher 覆盖/arming** | 部分（覆盖恢复，但 hint 触发的扫描仍失败） | watcher 的 `TryPlan` 对枚举 target 按 `target.RegistryId` 验证（`SourceWatcher.cs:438-465`），所以 refresh 后会 arm；但 watcher 的 hint 最终触发同一个失败 tick（`SourceScanScheduler.cs:625-649`、`:651-679`）。覆盖状态可能显示 covered，实际 hint 扫描不产出结果。 |
| **Run 源范围预授权** | **是（同根因的相邻消费面）** | `RunSourceRange.Resolve` 用 `HostSourceScanExecutor.ResolveRegistryEntry(registryEntries, target.Path)`（`HostRuntime.cs:1785-1790`），同样被旧 revoked 条目拦住 → 该 source 计入 `Unresolved`（`:1786-1790`）；cold source 的 on-demand scan 又走同一个失败 executor（`:1546-1574`，`:1563`）。Run 预授权是 best-effort，但该 source 的 grant 不会被铸出，Core 页级 gate 仍可能拒绝。 |
| **Host 内 `SourceScanStatus` / UI** | 间接 | `SourceScanStatus` 是 in-process 属性，不是 wire 命令（`HostRuntime.cs:155-161`）；因此没有新 UI，只有 Host 日志/状态里出现 `error`/`SOURCE_ACCESS_DENIED`。 |
| **Core / registry / 其他 source** | 否 | 本缺口不写 Core、不改 registry 结构、不影响其它 source；`IssueAsync` 在成功路径上原本就会写既有 `last_used_at` 审计（`SourceReadCoordinator.cs:498-520`、`SourceAccessRegistry.cs:94-97`），这不是本缺口新增。 |
| **非枚举（SCAN-1 内存注册）target** | 否（现状保留） | 非枚举 target 没有 `RegistryId`；`ResolveRegistryEntry` 的 exact-first / revoked-exact fail-closed / containment fallback 就是它的授权面。本报告不改变它。 |

### 1.4 为什么「Host 在 reattest 成功后刷新 scheduler 的 registry 视图」不成立

1. **scheduler 没有 registry 视图可刷新。** executor 每次扫描都 `_sources.Registry.List()`
   （`SourceScanScheduler.cs:1873-1874`）；枚举器每次 `SnapshotEntries()`（`:2077`、`:2084`、
   `:2217-2226`）。数据永远是 fresh 的；不存在需要更新的缓存副本。
2. **能做的「target 视图更新」已经做了。** refresh 合并时 `existing.Target = target`
   （`:797-819`），target 已带 live `RegistryId/Generation`；watcher 也通过 `TargetSetChanged`
   重新 arming（`:498-512`、`SourceWatcher.cs:316-407`）。所以「更新 target 视图」不是缺失步骤。
3. **旧 revoked 条目按设计永久存在。** B1 的 `Revoke` 只置 `revoked_at` 并 generation+1，不删除
   （`SourceAccessRegistry.cs:100-110`）；`List()` 返回全部条目（`:60`）；B1 注释明确 revoked 行累积
   （`SourceRecoveryModels.cs:399-409`）。因此任何「刷新视图」仍然会看到它。
4. **path-only resolver 忽略 target 的 registry id。** `ResolveRegistryEntry` 的签名只有
   `(entries, path)`（`:1885-1886`），不接收 target；所以即使 target 已带可信 live id，它仍然按路径
   重新裁决，并先命中 revoked 行。
5. **删除/改写旧条目不是「视图刷新」。** 那是 Host registry 的写操作，无本卡授权、破坏 B1 审计/诊断，
   并会把 fail-closed 语义改成「按当前路径重新解释历史授权」；正是 §2.1(b) 要避免的形态。
6. **Host 不能写 Core，也不需要再写。** reattest 已经把 Core 行修正到 live pair；Host 剩下的动作
   只能是「按 target 自己的 live id 使用该授权」。
7. **结论**：缺口不是 cache freshness，而是 **resolution authority**：target 已有可信 live 授权，
   executor 却退回到 path-only 的二次裁决。修复点应落在「枚举 target 使用自己已核验的条目」，
   而不是「刷新视图」。

### 1.5 与 L-S4-B 卡面/证据的一致性（不是重开 L-S4-B）

- L-S4-B 卡面明确只承诺**枚举恢复**，不宣称扫描执行成功：`doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md:88`、
  `:123`、`:132`；closeout `:169-172`；EV `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/EV.md:85-89`；
  Handoff `doc/handoffs/FEA-11-L-S4-B-AUTO-RECOVERY-1-30bdeb4ce.md:64-67`、`:83-85`。
- 因此本卡不是 L-S4-B 的返修，而是新缺口修复；L-S4-B 的 AC-LS4B-1…10 判定不受影响。
- 现有 gated 证据是可信的 before：生产/测试代码自 `30bdeb4ce` 起零 diff（§0），所以 `error` 仍是
  当前 head 的行为；实现卡不需要伪造一个 before。

---

## 2. Q2 最小方案

### 2.1 候选逐项评估

| 选项 | 具体形状 | 写域/契约 | 取舍 |
|---|---|---|---|
| **(a) 刷新 scheduler 的 registry 视图** | reattest 成功后让 scheduler 用新的 registry 快照/过滤视图 | Host read-only；0 契约 | **作为字面「视图刷新」不成立**：没有缓存视图可刷新（§1.4）；若「视图」= 过滤掉 revoked 行再交给 path resolver，则实际已是在改 resolver 语义（见 b/c1），且仍不如按 target id 精确。**否决（字面）**。 |
| **(a') 枚举 target 使用自身已核验的 live entry** | `ScanAsync` 对 `target.IsEnumerated` 使用 `VerifyEnumeratedTarget` 已核验的同一条 `SourceAuthorization`；非枚举 target 继续 path resolver | Host read-only；0 契约 | **推荐**。最小、最精确、与 C-17 §5.3 的 fail-closed 主体一致；不需要时间戳/多 live 歧义规则；`IssueAsync` 仍会 `Authorize` 复核 live/generation/root identity（`SourceReadCoordinator.cs:498-520`），安全面不降。 |
| **(b) 改 `ResolveRegistryEntry` 全局语义** | 同路径新 live 条目 + `live.CreatedAt > old.RevokedAt` 即接受；否则仍 fail-closed | Host code 但触及 C-17 §5.3 解释；可能 1 pin | **否决（作为本卡方案）**。它把 C-16 §2.5 的 reattest 候选规则搬进 resolver：需要处理多个 revoked/多个 live 的歧义、时间解析、containment fallback 语义、非枚举 target 的行为变化；而且这是 `C16-V15-BATCH-scope-r1.md:117`（b2）已判定过的 C-17 §5.3 语义面（该报告 §2.3 `:153` 给 1–2/18）。收益不高于 (a')，风险/复核成本明显更高。 |
| **(c1) 给 resolver 传 live-only 视图** | `entries.Where(e => e.RevokedAt is null)` 后再 path resolve | Host read-only；0 契约 | **可接受的次选**，但语义不如 (a') 精确：若同路径有多条 live（历史重复），`exact ??=` 仍取第一条；且「过滤」容易被读成放宽。只在实现上想最小 diff 时使用，AC 仍需断言「使用的是 target 自己的 entry」。 |
| **(c2) 删除/改写 revoked 旧条目** | reattest 后从 registry 删除同路径 revoked 行 | Host registry 写；无授权 | **否决**。破坏 B1 审计/诊断与 revoked 行累积语义；无卡面/契约依据；不是「视图」。 |
| **(c3) 让 Core 返回 path / 让 Core 在枚举时修 location** | 改 C-17 枚举 DTO 或让只读枚举隐式写 | Core + C-17；1 pin | **否决**。C-17 `:279` 明确 Core 不返回路径；只读枚举不得写；与 L-S4-B 的「reattest 事实传播」设计冲突。 |
| **(c4) 每 tick 重新 reattest** | tick 前再发 `ReattestSourceLocation` | 不必要 | **否决**。Core 行已经 live；重复写违反「每轮至多一次」精神且无收益。 |
| **(c5) 清除 backoff / 重置失败计数** | `MergeTargetsLocked` 在 target identity 变化时清 `Failures/BackoffUntil` | Host 调度行为；0 契约 | **可选、非必需**。本修复后，正常 B1 流程不会在 refresh 前产生该 target 的 tick error；但在「先 error、后 B1/修文件」的同会话场景，既有 backoff 可能延迟恢复。建议先不做，AC 措辞写「下一个未被既有 backoff 抑制的 tick」；若 DSH 要求即时恢复，再作为独立小 AC。 |
| **(c6) 只改状态/日志** | 把 error 显示成 skipped | 无行为修复 | **否决**。掩盖缺口，不恢复扫描。 |

### 2.2 推荐形状（Host-only，0 契约）

**核心改动（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`）**

1. 在 `HostSourceScanExecutor` 内新增一个纯解析 helper（命名建议
   `ResolveEnumeratedEntry` 或 `ResolveTargetEntry`）：
   - 对 `target.IsEnumerated`：在 registry 快照中按 `RegistryId == target.RegistryId` 取条目，并要求
     `RevokedAt is null`、`Generation == target.Generation`；可选再加
     `Roots.Any(r => r.Readable && normalized(r.Root) == normalized(target.Path))` 以保持与
     `VerifyEnumeratedTarget` 同一门槛。
   - 对 `!target.IsEnumerated`：原样调用既有 `ResolveRegistryEntry(entries, target.Path)`。
2. `ScanAsync`：
   - 枚举分支在 `VerifyEnumeratedTarget` 返回 null 后，**直接使用该函数已核验的 entry**（可把
     `VerifyEnumeratedTarget` 改为 `out SourceAuthorization? verified`，或在同一快照中按 id 重新取；
     推荐前者，避免两次 `List()` 之间的 TOCTOU 窗口）；
   - 非枚举分支保持 `ResolveRegistryEntry(target.Path)` 不变；
   - 不改变 `IssueAsync` 的入参语义；`Authorize` 仍会在铸 grant 时复核 live/generation/root identity
     （`SourceReadCoordinator.cs:498-520`），因此即使 verify 与 mint 之间发生 revoke，也不会放行。
3. 更新 `ResolveRegistryEntry` 的 XML 注释：明确它服务**非枚举** target；枚举 target 的授权来源是
   `VerifyEnumeratedTarget` 核验过的 `(registry_id, generation)`。这是注释/命名修正，不是语义放宽。
4. 不改 `TryMap`、`SourceRootReattestPlanner`、`ReattestRevokedTargetsAsync`、`SourceAccessRegistry`、
   `SourceWatcher`、状态枚举、错误码。

**同根因相邻消费面（建议一并，`HostRuntime.cs`）**

5. `RunSourceRange.Resolve`（`HostRuntime.cs:1737-1812`）：对 `target.IsEnumerated` 使用同一个
   helper（按 target.RegistryId+Generation 取 live entry），`!IsEnumerated` 保持
   `ResolveRegistryEntry`。这覆盖 Run 预授权与 cold on-demand scan 的同一断点；
   `RunSourceAuthorizer` 的 best-effort 语义不变（`HostRuntime.cs:1971-2019`）。
6. 若 DSH 决定本卡不碰 Run：把该点登记为
   `L-S4-B-2-RUN-RANGE-RESOLVE`（或本卡 limitation），并明确「Run 源范围的同一根因未修」；
   不要让卡面暗示 Run 已恢复。

**不做**：任何自动 `Register`/`Revoke`/`Reset`；任何 identity/roots/generation 写回；任何 Core DB 写；
任何新命令/能力/错误码/schema/依赖；任何 UI→Host 变更；任何 folder/多根 first-root 修复。

### 2.3 UNFREEZE 判定（哪份/几 pins）

| 方案 | C-16 | C-17 | C-15 | C-06/C-07/M2-C1 | pins | 判定 |
|---|---|---|---|---|---|---|
| **推荐：(a') 枚举 target 用自身已核验 entry** | 0（v1.5 已冻结；`source.reattest/1` 不变） | **0**（§5.3 的 fail-closed 主体仍是 target 自己的 registry；target revoked/缺失/漂移仍 fail-closed） | 0 | 0 | **18/18 全不变** | **READY-TO-FREEZE** |
| **(b) 全局改 `ResolveRegistryEntry` 接受同路径新 live** | 0 | **+1 pin（C-17 §5.3 语义变更）** + 独立安全复核 | 0 | 0 | 18/18（C-17 换新值，其余 17 不变） | **READY-WITH-UNFREEZE**（本报告不推荐） |
| **(c2) 删除/改写 revoked 行** | 0 | 0 | **可能 +1**（C-15 §5 状态机/审计） | 0 | ≥1 | 不推荐 |
| **B2 only（另卡）** | 0（`roots_available` 已在 v1.5 §1 冻结） | 0 | 0 | 0 | 18/18 | READY-TO-FREEZE，但无消费者，建议延后 |
| 只改 `SourceScanScheduler` 注释/测试 | 0 | 0 | 0 | 0 | 18/18 | 不达目标 |

**判定依据（C-17 `:279` 原文）**：该行写的是「registry **缺失/撤销/代次不可核验**由 Host
fail-closed」。推荐形状下，Host 对 **target 自己的** `(registry_id, generation)` 仍然：
缺失 → `Skipped(SOURCE_REGISTRY_UNAVAILABLE)`；撤销 → `Skipped(SOURCE_GRANT_REVOKED)`；
代次不等 → `Skipped(SOURCE_REGISTRY_BUSY)`；身份不符 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`
（`SourceScanScheduler.cs:1578-1632`）。它只是不再让**另一条更老的、已撤销的历史行**否决
target 自己的 live 授权。旧行不是「target 的 registry」；把它的存在解释成 target 的 registry
被撤销，才是把 path 当作授权主体。**这是本评审建议 DSH 采纳的解释口径；若 DSH 不采纳，
则应走 C-17 UNFREEZE，而不是把本卡判 BLOCKED。**

**为什么不是 C-16/C-15**：
- C-16 §2.5 已经冻结 `ReattestSourceLocation` 的写域/校验/Host 前置义务（`:95-108`）；本卡不新增
  命令字段、不改 reattest。
- C-15 §5 的「授权期逐请求校验 / 不得自动重建 identity / 不得自动重授权」保持
  （`FEA-C15_SOURCE_STORAGE_DRAFT.md:313-314`）；本卡只读 registry，不写 Authorization。
- C-15 §6 第 3 条的「既有 binding 的 `authorization_generation` 允许 ≤ 当前 Host generation」
  （`:324`）不受影响；本卡不改 binding。

### 2.4 红线（实现卡必须逐条保持）

| 红线 | 保持方式 | 判别性 AC |
|---|---|---|
| **不得自动重新授权** | 不调用 `Register`/`Revoke`/`Reset`；不创建/复活/延长任何 entry 或 grant；live entry 只能由 B1 的显式动作产生 | 去掉 B1 的显式 revoke+register → 无 live 候选 → 仍 skip；扫描前后 `DescribeRegistryEntries` 结构不变（允许既有 `last_used_at` 审计） |
| **不得自动重建 identity** | 不写回 roots/volume/file/identity_facts；只读 live 条目的登记身份；`VerifyEnumeratedTarget` 仍比对当前 `SourceSecurity.Identity` | 同路径替换文件（新 volume/file）→ `Error(SOURCE_REGISTRY_UNAVAILABLE)`；把 identity 比较删掉 → 红 |
| **不得因撤销后自动放行** | target 自己的 `RegistryId` 若 revoked → `Skipped(SOURCE_GRANT_REVOKED)`；只接受 target 自己的 live entry，不 fallback 到别的 live entry | 把 target 指向 revoked id + 同路径 live 条目 → 仍 skip；把 resolver 改成「任意 live」→ 红 |
| **不得删除/改写 revoked 旧行** | 旧行保留；`Revoke` 语义不变 | 扫描后 registry 中旧行仍在、`revoked_at` 不变；删除行 → 红 |
| **不得放松 path/身份校验** | `IssueAsync` → `Authorize` 仍逐请求验证 root containment 与 volume/file identity（`SourceAccessRegistry.cs:62-98`、`:131-139`） | 把 `Authorize` 或 identity 比较去掉 → 红 |
| **不得扩授权面** | 无新命令/能力/错误码/UI 端口；无 path 上 wire；folder 不支持；不碰 `source_reset_registry` 后无旧条目的场景 | 接口/registry/API 计数变化 → 红；folder target 被修复路径带入 → 红 |
| **不得夸大** | 只承诺「B1 显式重授权后，枚举 + 下一次 refresh 之后，扫描执行面恢复」；不承诺撤销后自动、不承诺 folder/多根/reset 后、不承诺「tick 自愈」 | 文案出现「自动恢复/自愈/自动重新授权」→ 红 |

### 2.5 为什么否决 (b)（补充）

1. **语义主体错位**：`ResolveRegistryEntry(entries, path)` 不知道 target 是谁；让它接受「同路径新
   live」等于让 path 而不是 target 的 registry id 决定授权。对枚举 target，这比 (a') 更弱。
2. **歧义规则膨胀**：多个 revoked（B1 可能多次重授权）、多个 live（重复注册）、时间解析失败、
   `CreatedAt` 与 `RevokedAt` 的精度/时区——都需要在 resolver 里再实现一遍 planner 逻辑
   （`SourceRootReattestPlanner.cs:227-238` 已有时间序规则），且不能复用 planner 的 `source_id` 约束。
3. **影响所有 caller**：非枚举 target、containment fallback、Run、任何未来 caller 都会受影响；
   (a') 只改枚举执行面。
4. **C-17 复核成本**：把「revoked exact fail-closed」改成「新 live 可覆盖」，正是
   `C16-V15-BATCH-scope-r1.md:117`（b2）与 `:158` 讨论的语义面；需要 C-17 UNFREEZE + 独立安全复核，
   而收益只是「少改一个 if」。
5. **没有额外收益**：target 自己的 live entry 已经在 `VerifyEnumeratedTarget` 中核验；用它是更强、
   更精确的授权，不需要时间序猜测。

---

## 3. Q3 拆卡/范围

### 3.1 单卡还是拆卡

**推荐：单卡 `FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1`，包含扫描执行面 + 同根因 Run 源范围解析（可选）。**

| 候选 | 建议 | 理由 |
|---|---|---|
| **扫描执行面（`SourceScanScheduler.cs`）** | **本卡 In（主体）** | 缺口原文；改动小；可用纯 helper + gated tick 闭环判别。 |
| **Run 源范围（`HostRuntime.cs` `RunSourceRange`）** | **本卡 In（建议）**，或拆 `L-S4-B-2-RUN-RANGE-RESOLVE` | 同根因、同一个 helper、约 5–10 行；不并入会留下一个「已重授权但 Run 仍 unresolved」的已知缺口。若 DSH 压窗口，拆出并在本卡 limitation 明写。 |
| **全局 `ResolveRegistryEntry` 语义** | **不单独立卡（本卡 Out）** | 不是恢复所必需；若 DSH 要做，走 C-17 UNFREEZE + 独立安全复核的独立决策，不应塞进本卡。 |
| **B2 `roots_available` 实现** | **另卡/延后** | 无消费者（`C16-V15-BATCH-scope-r1.md:29`、`:94`）；文件面（`SourceAccessRegistry.cs`/`SourceReadCoordinator.cs`）与本卡不重叠；混入会把「wire 投影 + 执行解析」压进一个 Review。 |
| **backoff 清理** | **可选，不单独拆** | 只在「同会话先 error 后恢复」场景影响延迟；建议先不做，AC 写「下一个未被 backoff 抑制的 tick」。 |
| **watcher 代码** | **不需要改** | watcher 按 target.RegistryId 验证，refresh 后已能 arm；修复 tick 后 hint 扫描即可工作。 |

### 3.2 推荐 In / Out（文件级）

**In（推荐）**

1. `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md`（冻结卡面/AC/status）。
2. `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md`（本报告 + 后续实现 Review）。
3. `doc/handoffs/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md`。
4. `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/**`（EV、logs、manifest、scope/discrimination）。
5. `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`：枚举执行解析 helper +
   `ScanAsync` 使用已核验 entry；注释修正；**不改** planner/pre-pass/TryMap/状态枚举。
6. `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`（若 Run 一并）：`RunSourceRange.Resolve`
   的枚举分支 + 必要的纯 helper 调用；**只改这一处**。
7. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanExecutionRecoveryTests.cs`（新增）：
   枚举解析矩阵 + 非枚举/撤销/target revoked 负例。
8. `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs`：把 L-S4-B gated 测试的
   tick 断言从「记录 error」改为「`ok`（fixture 未变）+ 恰 1 个 `ScanSourceSync`」，更新落盘证据 JSON。
9. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs`（若 Run 一并）：新增
   RunSourceRange 的枚举 target 用例（旧 revoked + 新 live 同路径 → resolved；target revoked → unresolved；
   非枚举不变）。
10. 既有 `SourceReattestTests.cs`、`SourceScanSchedulerTests.cs`：**不改**（除非为断言共享 helper 增加
    一行；若需要，逐文件列出并在 Review 说明）。

**Out**

- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs`：`List`/`Authorize`/`Revoke`/
  `Load`/`Save` 语义零变化；本卡不新增 availability/投影。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`：不新增/改 reattest/issue/
  authorize 语义。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceRootReattestPlanner.cs`：候选规则不变。
- `doc/plan/**`、`doc/contracts/**`：C-16/C-17/C-15/C-06/C-07/M2-C1 零字节。
- `src/**`、schema/迁移、依赖、`CORE_PROTOCOL_MINOR`。
- B2 `roots_available` 实现；folder/L-S4-2；多根 first-root；`source_reset_registry` 后恢复；
  L-S4-1/L-R1；2C 长 Run；UI 视觉/交互；真实用户数据；push；手工改 `TASK_LEDGER`。
- 自动重新授权/自动重建 identity/撤销后自动放行；删除/改写 revoked 行；任何新 UI→Host 命令。

### 3.3 建议 allowed_paths（供 DSH 冻结参考）

```yaml
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md
  - doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md
  - verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs          # 仅当 Run 一并；否则删去
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanExecutionRecoveryTests.cs   # 新增
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs   # 仅当 Run 一并
```

> 当前卡面 `allowed_paths` 只有 4 条 doc/verification（`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md:21-27`）；
> 冻结时必须补齐上述代码/测试路径，否则实现卡第一步就 scope 红。`src/infrastructure/sqlite/library.py`
> **不在** allowed_paths（本卡零 Core SQL）。

### 3.4 AC 草案（可判别 / fail-closed / 零漂移 / 门禁）

> 以下为 scope review 建议稿，**未冻结**；编号/措辞由 DSH 定稿。

| ID | AC | 判别性（去掉修复/放宽即红） |
|---|---|---|
| **AC-SER-1 枚举执行面恢复（主 AC）** | 给定「旧条目已 revoked + 新 live 条目同路径同物理身份 + Core 行 reattest 到 live」状态，scheduler 的 `target.RegistryId` = live；`ScanAsync` 必须用 target 自己的 live `(registry_id, generation)` 铸 grant，发送恰 1 个 `ScanSourceSync`，结果 `ok`（fixture 未变）或 `changed`（fixture 变更），**不得** `error`/`SOURCE_ACCESS_DENIED`；wire 无绝对路径。 | 仍调用 path-only resolver（或把 fix 去掉）→ 同一 fixture tick 回到 `error`；纯 helper 断言 live entry 被选中 → 红/绿可判。 |
| **AC-SER-2 fail-closed 矩阵不变** | target 自己的 registry：缺失 → `Skipped(SOURCE_REGISTRY_UNAVAILABLE)`；revoked → `Skipped(SOURCE_GRANT_REVOKED)`；generation 漂移 → `Skipped(SOURCE_REGISTRY_BUSY)`；root 缺失/被替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`；registry 整库不可读 → 现有 typed 行为；以上全部零 grant/零 frame。 | 任一把关被删 → 既有负例（`SourceScanSchedulerTests.cs:1134-1220`）或新增负例红。 |
| **AC-SER-3 非枚举语义零变化** | `ResolveRegistryEntry` 对 `!IsEnumerated` 保持 exact-first、revoked-exact → null、containment fallback；既有 `RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry`（`SourceScanSchedulerTests.cs:879-908`）原样通过。 | 把全局 resolver 改成「live 优先」→ 该测试或新增非枚举断言红。 |
| **AC-SER-4 无自动授权/无 identity 重建/不写 registry 结构** | 扫描前后 `DescribeRegistryEntries`（不含 `last_used_at`）结构相等；无新/撤销条目、无 roots/identity/generation 变化；无 `Register`/`Revoke`/`Reset` 调用；旧 revoked 行保留；仅既有 `Authorize` 的 `last_used_at` 审计可写。 | 在扫描路径调用 `Register`/`Revoke` 或删除旧行 → 红；把 identity 检查删掉 → 红。 |
| **AC-SER-5 Run 源范围（若 In）** | `RunSourceRange.Resolve` 对枚举 target 即使存在同路径 revoked 旧条目也按 target 的 live `(registry_id, generation)` 解析为 `Targets`（warm identity cache）；target registry revoked/缺失/漂移 → 仍 `Unresolved`；非枚举 target 语义不变。 | 仍用 path resolver → 新 Run 用例 unresolved 红；接受 revoked target → 负例红。 |
| **AC-SER-6 零契约/零接口漂移** | C-15/C-16/C-17/C-06/C-07/M2-C1 字节零 diff；pins 18/18（C16 `a7f57ebd`、C17 `aefa0fa5`、C15 `f9e376a0`）；`CORE_PROTOCOL_MINOR=3`；无新命令/能力/错误码/schema/依赖；API inventory 61 不变；无 UI→Host 变更。 | 任一契约/协议/registry 变化 → 红。 |
| **AC-SER-7 gated IPC 闭环（before/after）** | 真实 Core + 真实 registry + 真实 zip：B1 revoke+register → refresh（reattest）→ 枚举恢复 → tick `ok`（或 `changed`），恰 1 个 `ScanSourceSync` 帧，wire 无路径；`source_locations` 仅 auth 两列变化（reattest 时），其余表不变；registry 结构不变。证据 JSON 的 `tick_verdict.last_result` 不再是 `error`。 | 在同一 test 上回退修复 → tick `error`（现有 `ipc-closed-loop.json` 即 before）；断言只有枚举、不 tick → 不满足闭环。 |
| **AC-SER-8 门禁/不夸大/触发口径** | check（默认 + `-TaskPath`）PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不低于**本卡起点重测值**；flaky 原样记录 + 隔离复跑；`verification/FEA-09` 跑后 clean；卡/Handoff/EV 不写「自动重新授权/自愈/撤销后放行/自动恢复」；恢复口径固定为「B1 显式动作 → 既有 refresh（冷启动或 App 成功分支）→ 枚举 → 下一次 tick」；不宣称 tick 单独重新枚举。 | 出现红线承诺句 → 红；未重测就写旧基线 → 红；把 refresh 从路径里拿掉却宣称恢复 → 红。 |

### 3.5 冻结时的边界提醒

- 卡面 `depends_on` 已有 `FEA-11-L-S4-B-AUTO-RECOVERY-1`（done），正确；建议 `base_commit` 设为冻结时 clean head
  （当前 `b34060b2e`），`status: proposed → ready` 由 DSH 决定。
- `out_of_scope` 现文「生产实现/契约/schema/依赖字节……本卡为占位」是占位措辞（`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md:26-27`）；
  冻结时应改为「只允许 In 列表中的 Host 代码/测试，不碰 Core/契约/registry 结构」。
- `suggested_owner: codex` 可按 DSH 的可用性改；本报告不做人员裁决。
- 不要把「B2 `roots_available`」写进本卡 AC；字段已在 C-16 v1.5 §1 冻结（`FEA-C16_SOURCE_READ_WIRE_DRAFT.md:31`、`:35`），
  但实现无消费者（`C16-V15-BATCH-scope-r1.md:29`、`:94`），应另卡。
- 不要把「多根 first-root」或「`source_reset_registry` 后自动恢复」写进承诺：前者是既有启发式
  （`SourceScanScheduler.cs:2314-2319`），后者无旧 revoked 行可桥接（C-16 §2.5 `:108`；L-S4-B 卡 `:85`）。

---

## 4. Q4 测试/证据

### 4.1 现有 fixture 覆盖

| 资产 | 覆盖 | 与本卡的关系 |
|---|---|---|
| `SourceScanSchedulerTests.RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry`（`:879-908`） | 非枚举 path resolver：exact 优先、containment fallback、revoked exact → null | **保持原样**；它是 AC-SER-3 的判别器。 |
| `SourceScanSchedulerTests.Executor_EnumeratedTarget_RevokedRegistry_IsSkipped_NoScan`（`:1134-1154`） | target 自己的 registry revoked → `Skipped(SOURCE_GRANT_REVOKED)`，无 scan | AC-SER-2 负例；修复后必须仍绿。 |
| `..._GenerationDrift_IsSkipped`（`:1156-1175`） | generation 漂移 → `Skipped(SOURCE_REGISTRY_BUSY)` | 同上。 |
| `..._ColdStartMissingRoot...`（`:1177-1197`）/`..._ReplacedRoot...`（`:1199-1220`） | root 缺失/被替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)` | 同上。 |
| `Fea11ScanIpcTests.ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport`（`:548-729`） | **精确复现**：旧条目 revoke + 新条目同路径注册 + Core 行 reattest + 枚举恢复 + tick（当前只记录 error） | **本卡 gated 主证据**；只需把 `:675-676` 的断言升级为 `ok`（或 `changed`）+ `ScanSourceSync` 帧数。 |
| `SourceRegistryTests.RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`（`:257-295`） | RunSourceRange 的非枚举语义 | 若 Run In，新增枚举 target 用例；旧用例保持不变。 |
| `SourceReattestTests` | planner 候选矩阵、能力门禁、reattest 触发 | **不改**；本卡不碰 planner/reattest。 |
| `SourceWatcherTests` / `Fea11WatchHostRuntimeTests` | watcher 按 target.RegistryId 验证、hint | **不改**；修复后 hint 扫描可用，可选加一条集成断言（非必须）。 |

### 4.2 gated IPC：能否把 tick 从 error 验证为 ok

**能，且现有测试已经把最难的状态构造好了。**

- 现有测试的 phase A（legacy enumerator，无 coordinator）证明「Core 行仍 revoked → 枚举 0 target、
  1 skipped」；phase B（生产 enumerator + coordinator）证明「恰 1 帧 reattest → 重枚举 → live target
  入集 → 同一 target 可 tick」。
- 当前 tick 结果 `error` 不是测试缺陷，而是被登记的 limitation（`Fea11ScanIpcTests.cs:543-546`、
  `:706-711`）。实现卡把断言改为：
  - `Assert.Equal(SourceScanResults.Ok, tickVerdict.LastResult)`（fixture 未修改；若 fixture 有变更则
    允许 `changed`，但不得 `error`）；
  - `Assert.Single(RequestLines(client, "ScanSourceSync"))`；
  - `Assert.Equal(liveEntry.RegistryId, target.RegistryId)` 已有（`:620`）；
  - wire 无 `oldZip`/root 路径（已有 `:635-636`）；
  - registry 结构断言（已有 `:657`，`DescribeRegistryEntries` 不含 `last_used_at`）；
  - 证据 JSON `tick_verdict.last_result` 改为 `ok`，加 `scan_frames=1`。
- **before/after 判别**：当前 head 的生产/测试字节与 `30bdeb4ce` 相同（§0），现有
  `ipc-closed-loop.json` 的 `error` 就是 before；实现卡在同一测试上改断言后，base head 会红，
  delivery head 会绿——这是最干净的判别性证据。
- **注意**：phase B 是新建 scheduler（无历史 backoff），所以 `ok` 是确定性的；不要在同一个已 error
  的 scheduler 上直接断言「下一 tick 立刻 ok」（见 §4.4 backoff 提醒）。

### 4.3 最低新增测试集

1. **纯解析矩阵**（新 `SourceScanExecutionRecoveryTests.cs`）：
   - 旧 revoked + 新 live 同路径 + 枚举 target → helper 返回 live entry（`RegistryId/Generation` 正确）。
   - 同一组 entries + 非枚举 target → `ResolveRegistryEntry` 仍 null（revoked exact fail-closed）。
   - 枚举 target 指向 revoked 条目 → helper null（不 fallback 到 live）。
   - 枚举 target 缺失/generation 漂移 → null。
   - 可选：同路径两条 live → helper 仍按 target.RegistryId 精确选中（不靠 first）。
2. **executor 负例**：沿用 `SourceScanSchedulerTests` 现有 4 条（target revoked/gen drift/root missing/
   replaced）；修复后全绿。
3. **Run（若 In）**：`RunSourceRange.Resolve` 枚举 target 旧 revoked + 新 live → `Targets` 包含、`Unresolved=0`；
   target revoked → `Unresolved=1`；非枚举保持既有期望。
4. **gated IPC**：上述 `Fea11ScanIpcTests` 一条，断言 `ok` + 1 个 `ScanSourceSync`。
5. **判别性（建议 2–3 个破坏点）**：
   - 把 `ScanAsync` 的枚举分支改回 path-only resolver → 新 helper/executor 测试与 gated tick 红；
   - 把 helper 的 `RevokedAt is null` 去掉 → target revoked 负例红；
   - 把 `Generation` 比较去掉 → gen drift 负例红。

### 4.4 全量门禁成本 / flaky / 基线

| 项 | 记录值/成本 | 说明 |
|---|---|---|
| `pytest tests` | **3360 passed / 10 skipped**（L-S4-B closeout，`logs/full-pytest.log` 尾行；251.59s） | 本卡无 Core 改动；全量主要用于门禁。不得低于本卡起点重测值。 |
| 全量 .NET | **1644 passed / 0 failed / 94 skipped**（L-S4-B closeout；`logs/full-dotnet.log` 各项目合计） | 本卡只改 Host/测试；必须重测。 |
| 基线矛盾 | `doc/STATUS.md:20` 仍写 **3317/10、1617/0/93** | 与 L-S4-B closeout 不一致（+43 pytest、+27 .NET、+1 skip）；冻结/释放前必须在 clean head 重测并写「本卡起点」。 |
| 已知 flaky | （既有记录）`FluentResidual2VisualEvidenceTests`（Lead combined 曾命中，隔离复跑 1 passed）；SCAN-2 记录 FluentAssertions/Threading/reflection 偶发 | 原样记录 + 隔离复跑；不得「重跑到绿」。 |
| 写入卫生 | （既有记录）全量 pytest 历史会改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`；`SourceRegistryTests` 会写 `verification/FEA-09/native-registry/**` | 跑后 `git status`；只恢复**测试产生的**变更；不把测试噪声当交付。 |
| gated IPC | `NEWMANGA_FEA11_IPC=1`，`Fea11ScanIpcFact` 才运行（`Fea11ScanIpcTests.cs:1156-1164`）；fixture 在 `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`（`:948-955`），不写 tracked 证据 | 一条证据即可，不要为证据跑全量。 |
| 建议命令（实现卡） | `dotnet test apps/desktop-avalonia/NewManga.sln --filter "FullyQualifiedName~SourceScanExecutionRecovery"`；`--filter "FullyQualifiedName~SourceScanSchedulerTests"`；`$env:NEWMANGA_FEA11_IPC='1'; dotnet test ... --filter "FullyQualifiedName~Fea11ScanIpcTests"`；`python -m pytest tests -q`；`pwsh -File tools/governance/verify_pins.ps1`；`check.ps1`（默认 + `-TaskPath`）；`python tools/generate_api_inventory.py --check` | 命令为建议稿；实际入卡时按仓库脚本/路径校准。 |

### 4.5 建议证据目录

`verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/`，至少：

- `EV.md`（AC 逐项、before/after、limitation）
- `logs/host-unit.log`（新纯解析/executor 测试）
- `logs/host-ipc.log`（gated 1 passed + head）
- `logs/feature.log` / `logs/regression.log`（若跑）
- `logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/gates.log`
- `logs/discrimination.log`（2–3 个破坏点，含 restore sha）
- `scope-validation.log`、`changed-files.txt`、`RESOURCE-MANIFEST.json`
- gated 落盘 `reattest-ipc.json/.txt` 的副本或引用（在原 workspace fixture；EV 记录路径与 hash）

---

## 5. Q5 优先级与 DSH 裁决点

### 5.1 与队列项的对比

| 项 | 性质 | 用户可见性 | 成本/契约 | 相对建议 |
|---|---|---|---|---|
| **L-S4-B-1（本卡）** | 已登记 limitation 的执行面缺口（重授权后 tick error） | 中（后台扫描/监控恢复；Run 相邻） | **小**：Host-only，0 pins，1–2 个文件 + 测试 | **优先冻结/实现**；是 L-S4-B 的收尾补洞。 |
| **B2 `roots_available`** | wire 投影，无消费者 | 当前无 | 小（C-16 已冻结字段），但另卡 | **延后**到 roots UI/多根管理立项；不要抢占本卡窗口。 |
| **2C 长 Run（L-G1）** | >300s 长 Run 失权 | **高**（长任务中断） | 高：新 host-control/续期设计，可能多 pin | 用户价值更高但成本大；建议本卡先收尾，2C 另卡设计/实现。 |
| **L-R11** | gate 统一/审计一致性 | 低 | 小-中；0 pin | 可穿插。 |
| **C-04b** | 8 项文档 residual | 无 | 极小；0 pin | 穿插。 |
| **SCAN-RH** | 可观测性/limitation | 低 | 小；0 pin | 穿插。 |
| **UI P3** | 视觉/交互 | 低 | 小；0 pin | 最后。 |

**推荐顺序（供 DSH 裁决）**：**① 冻结并实现本卡（扫描执行面；建议含 Run 相邻）→ ② 2C 设计/实现
（或与本卡并行设计）→ ③ B2 等 roots UI 立项后再做 → ④ L-R11 / C-04b / SCAN-RH 穿插 → ⑤ UI P3 最后。**
如果 DSH 认为 2C 的用户价值必须优先，可把 2C 提到本卡之前；但本卡很小，单独延后会继续保留一个
「B1 后 tick error」的已知行为，不利于 L 线收口。

### 5.2 DSH 裁决点（含推荐）

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **D-1** | 采用哪种形状：刷新视图 / 枚举 target 用自身 live entry / 全局改 resolver？ | **(a') 枚举 target 用自身已核验 live entry**；全局改 resolver 否 | 决定 0 pins 还是 C-17 1 pin |
| **D-2** | C-17 §5.3 的解释口径：fail-closed 主体是 target 自己的 registry，还是同路径任意 revoked 行？ | **target 自己的 registry**（→ 0 pins）；若 DSH 不采纳，改走 C-17 UNFREEZE 1 pin，**不要 BLOCKED** | 决定 UNFREEZE 判定 |
| **D-3** | Run `RunSourceRange` 是否并入本卡？ | **并入**（同 helper、约 5–10 行、避免第二个 limitation）；若压窗口则拆 `L-S4-B-2-RUN-RANGE-RESOLVE` 并在卡面明写 | 决定 `HostRuntime.cs` 是否在 allowed_paths |
| **D-4** | 是否在本卡清 backoff（target identity 变化时）？ | **暂不**；AC 写「下一个未被 backoff 抑制的 tick」；若要求即时恢复，另加小 AC | 决定是否多一处调度行为变更 |
| **D-5** | 冻结口径：status、base_commit、allowed_paths、AC 编号 | 冻结时 `base_commit=b34060b2e`（或当时 clean head）；按 §3.3 补 allowed_paths；AC-SER-1…8 定稿；`status: ready` | 决定实现卡能否开工 |
| **D-6** | 是否把 B2 并入本卡？ | **不并入**；字段已冻结，实现另卡 | 决定 Review 规模/文件面 |
| **D-7** | 基线：STATUS 3317/1617 vs L-S4-B closeout 3360/1644 | **clean head 重测并写「本卡起点」**；不继承任一旧数 | 决定 AC-SER-8 可判性 |
| **D-8** | gated before/after 证据 | 用现有 `ReauthorizedSource...` 测试；before 用 `ipc-closed-loop.json`（error）；after 断言 `ok` + 1 帧 | 决定闭环证据是否成立 |
| **D-9** | 优先级 vs 2C | 本卡先（小、收口）；2C 随后/并行设计 | 决定下一活动 Task |

### 5.3 风险

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| **R1** | 修复被误读为「C-17 §5.3 放宽/撤销后自动放行」 | 中-高 | 卡面/Review 明确「只改枚举 target 的授权来源，不改 target revoked/缺失/漂移的 fail-closed」；AC-SER-2/3；保留旧 resolver 测试。 |
| **R2** | 非枚举 target 行为回归 | 中 | `ResolveRegistryEntry` 不动；AC-SER-3 + 既有测试。 |
| **R3** | Run 相邻改动影响 Run 预授权 | 中 | 纯 `RunSourceRange` 测试 + best-effort 语义不变；若 DSH 担心，拆卡。 |
| **R4** | gated fixture 噪声/路径泄漏 | 中 | 沿用既有 workspace fixture；wire 断言无路径；不写 tracked 证据。 |
| **R5** | 基线陈旧导致 AC 误判 | 中 | 重测 clean head；记录起点/终点/差值归属。 |
| **R6** | 全量 pytest 改写 tracked `verification/FEA-09` | 中 | 跑后 `git status`；只恢复测试产生的变更；优先 gated/定向。 |
| **R7** | 同会话已有 backoff 导致「修复后下一 tick 仍不立即 ok」 | 低-中 | gated 用新 scheduler；AC 措辞「下一个未被 backoff 抑制的 tick」；必要时另加 D-4。 |
| **R8** | verify 与 mint 之间发生 revoke | 低 | `IssueAsync` → `Authorize` 在 registry 锁内复核 live/generation/root identity（`SourceReadCoordinator.cs:498-520`）；不会放行。 |
| **R9** | 多根 first-root / folder / `source_reset_registry` 被误以为已修 | 低-中 | 卡面/AC 明写 Out；保留 limitation。 |
| **R10** | 「扫描恢复」被写成「自动恢复/自愈」 | 中 | AC-SER-8 措辞红线；只承诺「B1 显式动作 → refresh → 枚举 → 下一 tick」。 |

---

## 6. 真实性声明

1. **唯一写入**：本评审只写了
   `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-scope-r1.md` 这一个文件。**未**修改/删除/移动任何
   生产代码、测试、契约、冻结记录、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或证据字节；
   **未**执行 `git add`/`git commit`/`git push`。
2. **独立性**：评审者为独立上下文的 fresh subagent，未参与 `FEA-11-L-S4-B-AUTO-RECOVERY-1`、
   `FEA-11-L-S4-B-PREREQ-1`、`FEA-11-L-S4-B-1` 或 B2/L-S4-A/B1 的实现、返修或审查；只读被审 head。
3. **事实优先级**：所有代码/契约断言均来自 `b34060b2e` 的工作树字节（`git status` clean、无并发提交），
   逐条给出 `path:line`；未把卡面/Handoff/Review 的自述当作实现事实（引用时标注「既有记录」）。
4. **实测命令**（EXIT 见 §0）：`git rev-parse --abbrev-ref HEAD`、`git rev-parse HEAD`、
   `git status --porcelain`、`git log -1`、`git diff --name-only 30bdeb4ce..HEAD -- apps src tests`、
   `pwsh -NoProfile -File tools/governance/verify_pins.ps1`、`check.ps1`（默认 + `-TaskPath`）、
   `python tools/generate_api_inventory.py --check`。
5. **NOT_RUN**（未跑、不声明 PASS）：全量 `pytest tests`、全量 `dotnet test`、定向 .NET/gated IPC、
   byte-level 契约复核、任何破坏性实验。理由见 §0（只读约束 + 单文件写入约束 + 无实现 head）。
   §4.4 的数字均为**既有记录**，不是本评审实测。
6. **判别力声明**：本报告未做「破坏-恢复」实验；§3.4/§4.3 的「判别性」是给实现卡/Review 的
   **待验证项**，不是本轮已完成证据。
7. **建议性质**：本报告的 In/Out/allowed_paths/AC/UNFREEZE 判定均为**建议**；scope 冻结、契约字节变更、
   Review Appointment、findings 处置与集成验证属 DSH。
8. **limitation**：本报告不评估 B2/2C/L-R11/C-04b/SCAN-RH/UI P3 的实现细节，仅做优先级比较；
   不声称任何测试或 gated IPC 已在当前 head 通过；不声称 C-17 §5.3 的解释已被 DSH 采纳。
