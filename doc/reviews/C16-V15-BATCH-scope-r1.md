---
task: C16-V15-BATCH
title: C-16 v1.5 批量载体（L-S4-B 零交互自动恢复枚举 + B2 roots 可用性投影）权威 scope review r1
reviewer: fresh subagent（独立上下文；未参与 L-S4-A/B1/B2/L-S1 的任何实现、返修或审查；只读被审字节）
session: 委托子会话（独立上下文隔离；会话 id 未在本会话暴露；身份来源与边界见 §10）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: 独立 scope review（fresh context / read-only / 非作者 / 非实现审查者）
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 614aff07fde1b562e1107359fe2f13f324718a58
reviewed_head_note: 任务书给的是 `614aff07f`（main，clean）。实测 HEAD 与任务书一致；评审起点 `git status --porcelain` 为空，结束时仅新增本报告；评审期间无并发提交。本报告全部代码/契约断言取自该 head 的工作树字节。
verdict: BLOCKED
verdict_scope: >-
  按现卡面（「只读枚举 + 零 DB 写」同时承载 B2 与 L-S4-B、单个 C-16 v1.5 载体）**不可冻结**：
  L-S4-B 的「零交互自动恢复」在现有 C-17 exact-match/fail-closed 语义与 C-16 只读命令面下不可达（§2/§3）。
  拆分后：**B2 单独 = READY-TO-FREEZE（C-16 §1 一个 additive 字段，1/18 pins；但今天无消费者，建议延后）**；
  **L-S4-B 经 DSH 改口径为「显式重授权后的条件 re-attest 写命令」= READY-WITH-UNFREEZE（同一 C-16 v1.5，仍 1/18 pins）**；
  若坚持零 DB 写，只能改 C-17 §5.3 语义（+1 pin）并另做安全复核，或延后。
---

# C-16 v1.5 批量载体：权威 scope review r1

> **结论先行。**
>
> 1. **L-S4-B 的缺口事实成立，但卡面给的机制不成立。** 没有写路径介入时，重授权后的 Core `source_locations` 永远停在旧 `(registry_id, generation)`；冷启动枚举由 Core 从该行投影（`src/application/sources/scanner.py:96-177`，`:166-167`；`src/infrastructure/sqlite/source_sync.py:75-94`），Host 的枚举映射与执行期复核要求 `(registry_id, generation)` 在 Host 持久 Registry 中**精确命中且未撤销**（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:2162-2169`、`:1505-1512`、`:1561-1610`），否则 typed skip。而 Host 的 `Register` 每次生成**新 registry_id + generation=1**（`SourceAccessRegistry.cs:34-52`），B1 的显式重授权只动 Host Registry（`SourceRecoveryModels.cs:411-525`），**不写 Core DB（仅 `RevokeSourceReadGrant` 的内存撤销）、不触发扫描刷新**（`ImportDockViewModel.cs:570-599`、`:700-710`）→ 用户「只重授权、不重导入/不 apply」时，该源在冷启动/周期扫描中**静默丢失**（L-S4-1）。
> 2. **只读命令无法闭合 L-S4-B。** Core 侧记录只能由既有写路径改（`runtime.py:462-468`/`:571`/`:689`/`:925`；`service.py:508-516`；唯一 SQL `library.py:2293-2353`、`:2652-2655`），新增一条**只读** host-control 命令没有可授予的新能力（Core 不能改行，Host 也不缺读数据），最多是第二条读面。Host 侧只读「按同路径+同物理身份重证」在技术上可行，但它**改变 C-17 §5.3「registry 撤销/代次不可核验 → Host fail-closed」的既有语义**（`FEA-C17_SOURCE_SYNC_DRAFT.md:279`），需要 C-17 的冻结面变更与独立安全复核，不是「零契约/单 C-16 pin」。
> 3. **推荐形状（改口径后 1 pin）：** C-16 v1.5 = §0 能力 `source.reattest/1` + §2.5 新 host-control **条件写**命令 `ReattestSourceLocation`（Host→Core；唯一请求 `{source_id, grant_id}`；用 live grant 证明「同一物理身份 + 同一 Core source」，只更新 `source_locations` 的 `registry_id/authorization_generation/last_verified_at`，复用 A 卡唯一 SQL；拒绝路径零写；幂等/单调）+ §1 `source_list_roots` 的只读 `roots_available[]`（B2）。**C-15/C-17/C-07/M2-C1 零字节**；C-16 仍只 1/18 pins（`ad25fb3c89bb` → 新值，其余 17 不变）。
> 4. **B2 今天没有消费者**：App 侧没有任何 roots 管理/健康界面，`ParseRoots` 只读单根 `roots[]` 且忽略未知字段（`SourceRecoveryModels.cs:644-674`）；`source_list_roots` 只有两个既有消费者——导入复用选择（`SourceImportModels.cs:818-839`，只看 entries/roots/revoked）与 B1 诊断（`SourceRecoveryModels.cs:344-393`，只把「探测成功/失败」当二元判据），**都不消费可用性**。B2 是合法的 additive，但只有随「多根管理 UI」立项才有产品价值；可以把字段并入 v1.5 以满足「版本号一次性保留」的承诺，但**实现卡建议延后**。

---

## 0. 只读基线与实测命令（未跑项一律 NOT_RUN）

| 项 | 值 | 来源/说明 |
|---|---|---|
| 仓库 / 分支 | `G:\CODEX\New Manga` / `main` | 实测 |
| HEAD | `614aff07fde1b562e1107359fe2f13f324718a58` | `git rev-parse HEAD`（T0 11:57 / T1 12:19 同值） |
| 工作树 | 起点 **clean**；结束时仅本报告未跟踪（`?? doc/reviews/C16-V15-BATCH-scope-r1.md`） | 实测；评审期间无并发提交 |
| 并发会话 | **无**（评审窗口内无提交、无未跟踪/已修改字节） | 实测 |
| `verify_pins.ps1` | **PASS (all 18)**：C15 `f9e376a0ed4c`、**C16 `ad25fb3c89bb`**、C17 `aefa0fa5b17e` | 实测，EXIT=0 |
| `check.ps1`（默认） | **PASS (3 warnings)**（非终态 Task 9 个；STATUS/PLAN 接近预算） | 实测，EXIT=0 |
| `check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | **PASS (3 warnings)** | 实测，EXIT=0 |
| `generate_api_inventory.py --check` | **PASS（EXIT=0，无 diff）** | 实测 |
| 定向 pytest `tests/fea11/test_source_command_parity.py tests/core/test_core_scan_target_commands.py` | **12 passed，3.93 s，EXIT=0** | 实测 |
| 定向 .NET `NewManga.Host.Tests --filter FullyQualifiedName~SourceRegistryResilienceTests` | **8 passed / 0 failed / 1 skipped，625 ms，EXIT=0** | 实测（Release，已有构建） |
| 全量 `pytest tests` | **NOT_RUN**（理由：scope review 只读；且全量历史上有改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` 的记录，本轮不冒写入风险；改用已记录基线 3317/10 讨论） | 既有记录：`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md:85`、`doc/STATUS.md:20` |
| 全量 `dotnet test NewManga.sln` | **NOT_RUN**（理由同上；`SourceRegistryTests` 会写 `verification/FEA-09/native-registry/**`，全量跑不可避免触碰 tracked 证据树） | 既有记录：B1 卡 `:85` **1617/0/93**；STATUS `:20` **1570/0/92**（两者矛盾，见 §5.3） |
| `NEWMANGA_FEA11_IPC=1` 真实 IPC | **NOT_RUN**（无实现 head；B1 的 gated 闭环可作为模板） | 既有记录：B1 卡 `:86`、`:110` |
| 真实用户数据 / AppData / 回收站 / push | **未触碰** | — |
| 冻结契约字节只读核对 | C-16 `§0/:20-23`、`§1/:27-35`、`§2.4/:74-91`、`§6/:170-193`、`§7/:197-206`（§7.3=`:201`）、`§10/:225`；C-17 `:215-228/:261-262/:276/:279`；C-15 `:204/:313-315/:347/:354`；C-16 冻结记录 pin | HEAD 字节实测 |

> 基线口径提醒：`doc/STATUS.md:20` 的 .NET 基线 **1570/0/92** 与 B1 closeout 实跑 **1617/0/93**（B1 卡 `:85`；`doc/handoffs/DSH-PROGRESS-2026-11-07.md:10`）不一致。下一张卡冻结/释放前必须在 clean head 上**重测一次**并写清「本卡起点基线」，不得直接继承任一旧数字（§5.3、R7）。

---

## 1. Q1 需求核实：缺口是什么、为什么现在不恢复、B1 分工

### 1.1 L-S4-B：无写路径 → 冷启动/周期枚举不恢复（可复现链路）

| 步骤 | 事实 | 锚点 |
|---|---|---|
| 1. B1 显式重授权 = 先撤销同路径全部非撤销条目，再注册**一条新条目** | 新条目 `registry_id = Guid.NewGuid()`、`generation = 1`；旧条目 generation+1 且 `revoked_at` 非空 | `SourceAccessRegistry.cs:34-52`、`:100-110`；B1 卡 `:80`（AC-LSB-3）；`SourceRecoveryModels.cs:411-525` |
| 2. Core 的 `source_locations` 只由写路径更新 | 重导入/复用：`runtime.py:462-468` 计算刷新、`:571`/`:925` 传入页单元，`library.py:2652-2655` 与页/binding **同一事务**执行；整源 skip：`runtime.py:408-411`、`:661-699`；新源插入：`runtime.py:905-906`；sync apply：`service.py:508-516`（`BEGIN IMMEDIATE` 内）。B1 不带任何 Core **DB** 写（仅 `RevokeSourceReadGrant` 的内存撤销） | `src/application/importing/referenced/runtime.py:408-411`、`:462-468`、`:571`、`:689`、`:905-906`、`:925`；`src/application/sources/service.py:500-516`；`src/infrastructure/sqlite/library.py:2293-2339`、`:2341-2353`、`:2652-2655` |
| 3. 没有「通知 Core 刷新 location auth」的命令 | host-control 闭集只有 grant/session/C-17 操作命令；`RegisterSourceReadGrant` 只做内存注册；A 卡 D-3 明确否决「在 grant 注册里顺手刷新」 | `src/bootstrap/core_service.py:355-367`、`:4906-4914`；`doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md:50`（D-3）、`:59` |
| 4. 冷启动枚举 = Core 读 `source_locations` 投影 | `source_list_scan_targets` 只读、零写；每 target 的 `registry_id/generation` 直接来自当前 location 行 | `src/application/sources/scanner.py:96-177`（`:166-167`）；`src/infrastructure/sqlite/source_sync.py:75-94`；C-17 `:228`、`:261-262` |
| 5. Host 映射要求精确命中 | Core 记录的 `(registry_id, generation)` 必须在 Host Registry 中找到、**未撤销**且 generation 相等；否则不入 target 集 | `SourceScanScheduler.cs:2162-2169`（revoked/缺失/gen 漂移 → false） |
| 6. 执行期再核验一次 | 已入集的 target 在扫描前再核验：撤销 → `SOURCE_GRANT_REVOKED` skip；gen 漂移 → `SOURCE_REGISTRY_BUSY` skip；缺失/被替换根 → `Error(SOURCE_REGISTRY_UNAVAILABLE)` | `SourceScanScheduler.cs:1505-1512`、`:1561-1610`、`:1627-1632` |
| 7. 触发面 | 冷启动：Host Ready 后后台枚举一次；App 触发：**只有 completed import 才请求一次 refresh**；周期 loop 只跑 tick（不再枚举） | `src/NewManga.Host/HostRuntime.cs:1350-1403`、`:193-220`；`ImportDockViewModel.cs:700-710`；`SourceScanScheduler.cs:1118-1151`、`:894-919` |
| 8. B1 成功路径 | 重授权成功后**只重跑预览**（mint），不导入、不 apply、不 refresh 扫描 | `ImportDockViewModel.cs:570-599`；`SourceRecoveryModels.cs:444-525` |

**结论**：用户只做 B1 的「重新授权」而不完成一次重导入/apply 时：

- Core 的 location 仍是旧 `(registry_id, generation)`；
- 下一次冷启动/导入后 refresh 的枚举把该源当作「registry 未知/已撤销/gen 漂移」→ **不入 target**（`TryMap` false）；
- 即便 target 因某种原因已在内存中，执行期仍 typed skip（`VerifyEnumeratedTarget`）；
- **没有任何自动恢复路径**。这不是「A 卡函数没接上」（A 已接上 `service.py:516`、`runtime.py:689`），而是**缺触发器**：B1 的显式动作没有对应的 Core 写/通知。L-S4-1 原文与代码事实一致（`doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md:80`、`:102`）。

**补充（周期措辞）**：卡面说「冷启动/周期枚举」，严格地讲**周期 loop 不重新枚举**（`SourceScanScheduler.cs:1118-1151` 只 `TickAsync`；`TickAsync` 只扫内存 target 集），因此该源的静默丢失在「进程存活期间」不会因 tick 而恢复；重启后枚举仍会 skip。卡面冻结时应把「周期枚举」改为「冷启动枚举 + 下一次 refresh 枚举（completed import/显式请求）」，避免 AC 写成 tick 恢复。

### 1.2 B2：多根健康不可见 + 一个被冻结的 first-root 启发式

| 事实 | 锚点 |
|---|---|
| `source_list_roots` 响应只回 `roots: [path...]` 与 registry 元数据；**没有可用性/身份投影** | `SourceReadCoordinator.cs:621-624`；C-16 §1 `:30`（冻结形状） |
| `List()` 只返回持久条目；可用性是 `Authorize` 在请求期**派生**（逐根 probe，零写、不持久化） | `SourceAccessRegistry.cs:54-60`、`:62-98`、`:131-139`、`:150-191`；C-15 v1.5 `:313` |
| App 只解析单根 `roots[]`（`GetArrayLength() != 1` 即跳过），且忽略未知字段；没有 roots UI/健康面 | `SourceRecoveryModels.cs:644-674`；`ImportDockView.axaml` 只有错误文本区（B1 卡 `:78-87` 的证据） |
| 枚举 mapping 取 `entry.Roots.FirstOrDefault(Readable && 非空)`，**不探测身份** | `SourceScanScheduler.cs:2171-2176` |
| 执行期要求 `target.Path` 与**某一根精确相等**，再核验该根身份；因此多根条目实际只能扫 `roots[0]`：`roots[0]` 失效时即使 `roots[1]` 健康也 `Error(SOURCE_REGISTRY_UNAVAILABLE)` | `SourceScanScheduler.cs:1599-1632` |
| 本轮 App 的生产写法**每个条目恰一个 root**（`RegisterRoot` 只写一个字符串），所以多根是**潜在**能力，不是当前用户可见路径 | `SourceImportModels.cs:243-252`；`SourceRecoveryModels.cs:213-226`（只复用条目自身 `roots[0]`） |
| 导入复用选择器也不消费可用性（且**不应**消费） | `SelectReusableRoot` 只按「单根 + 路径相等 + 非 revoked + generation」选择（`SourceImportModels.cs:849-878`）；若按 availability 跳过失效条目并自动注册 = 自动重新授权，撞 B1 R-1/AC-LSB-5（B1 卡 `:55`、`:82`） |
| B1 恢复只用「失败预览 + 单根 stale 条目」，**不需要** availability 字段 | `SourceRecoveryModels.cs:344-393`、`:604-619`；B1 卡 `:79-87` |

**结论**：B2 的「多根健康不可见」是事实，但**今天的唯一生产者不产生多根条目，现有两个消费者（导入复用选择、B1 诊断）也都不消费可用性**；它是为未来「roots 管理/健康界面」预留的 wire 投影。若冻结 B2，必须同时承认：它**不修复** §1.2 的 first-root 扫描启发式（那需要 source path 权威，而 Core 不返回路径，C-17 `:279`），它只提供「按根展示是否可用」的只读事实。

### 1.3 与 B1 显式恢复的分工（不得混写）

| 卡 | 触发 | 写域 | 能兑现的承诺 | 不能兑现 |
|---|---|---|---|---|
| **B1（done）** | 用户显式点击「重新授权此来源」/「重置源授权存储」 | Host Registry（revoke/register/reset）；Core 仅 `RevokeSourceReadGrant` ACK | 该路径重新变成「有 live 条目；重跑预览可 mint 成功」 | 不刷新 Core location；不恢复扫描；不自动做下一步导入 |
| **L-S4-A（done）** | 下一次**写路径**（页单元重导入、sync apply） | Core `source_locations` 三列（单点 SQL） | 同物理身份 + live grant 时原地刷新；随后枚举跟随 | 自身不是触发器；没有写路径就不发生 |
| **L-S4-B（本批）** | 显式重授权已发生后，Host 的 read-only 枚举/refresh 触发（推荐形状） | 推荐：Core 条件单行 re-attest（3 列）；Host 只读枚举 + 既有 refresh | 「重授权之后无需再导入/apply，扫描监控自动恢复」 | 不自动重新授权、不自动重建 identity、不自动导入、不发布内容；`source_reset_registry` 之后无旧条目可桥接（limitation） |
| **B2（本批）** | 无（纯读） | Host 只读投影 | 未来 roots UI 可显示逐根可用性/健康 | 不改授权、不改扫描、无任何恢复动作 |

> 卡面冻结时必须把「零交互」限定为「**用户完成 B1 的显式动作之后**，系统不再要求第二次交互」；不得写成「撤销后自动恢复/自动重授权」。C-15 `:314` 的「根级恢复由显式用户操作完成，不得自动」必须保持——B1 的显式动作就是那个「显式」。

---

## 2. Q2 最小形状：逐项取舍与 1 pin 口径

### 2.1 候选形状

| 选项 | 具体形状 | wire/能力/错误闭集 | 取舍 |
|---|---|---|---|
| **(a) `source_list_roots` 加只读可用性字段** | 建议 `roots_available: [bool, ...]`，与 `roots[]` **同序同长**；不改 `roots[]` 的字符串数组形状；派生不持久化 | C-16 §1 additive；无新能力；**无新错误码**（不可用是数据，不是 error）；旧 App 忽略未知字段，新 App 缺字段时按 unknown 处理 | **In（B2）**。最小、可回退、不改授权；但今天无消费者（§1.2），只有随 roots UI 立项才有产品价值。**禁止**把 `roots[]` 改成对象数组（会破坏 B1 的 `ParseRoots` 与既有字节兼容） |
| **(b1) 新 host-control 只读命令（`DescribeSourceRoots`/`PlanAutoRecovery`）** | 新命令 + 新能力，返回「根可用性/建议的恢复计划」 | C-16 §0/§2.x；1 pin | **否决**。Core 没有 Host Registry，无法回答「根可用性」；Host 已经有这些数据。若返回 Core 的 location 事实，则与 `source_list_scan_targets` 第二读面重复（C-17 `:228`），且**不改行、不恢复**，只是把「不能恢复」描述得更详细 |
| **(b2) Host-only 只读「同路径 + 同物理身份」重证** | 不新增命令；`EnumerateAsync` 对「Core 记录的 registry 已撤销」的 target，若存在**同路径、同 volume/file、单根、非撤销**的 live 条目，就用该 live 条目映射/扫描（不写 DB） | 对 L-S4-B 零 C-16 变更；**C-17 §5.3 语义被改**（`FEA-C17_SOURCE_SYNC_DRAFT.md:279`：「registry 撤销/代次不可核验由 Host fail-closed」）；要么 C-17 1 pin，要么 DSH 显式解释并承担语义漂移；另有安全复核成本 | **仅作「绝对禁止 DB 写」时的备选**。技术上可行、零写、无新命令；但把一条明确的 fail-closed 守卫改成「按身份重证」，是**授权面解释变更**——既不「零契约」，也不该由本卡顺手做。且 Core 行永远不愈，形成「持久双语义」 |
| **(b3) 新 host-control 条件写命令 `ReattestSourceLocation`**（推荐） | 唯一请求 `{source_id, grant_id}`（closed shape）；Core 用 live grant 证明「同一 source + 同一物理身份」，只更新三列；失败零写；幂等/单调 | C-16 §0 能力 `source.reattest/1` + §2.5 命令；**复用 §6 错误闭集**；C-15/C-17/C-07/M2-C1 零字节 | **推荐**。保留 C-17 的 exact-match/fail-closed 不变（先修好 Core 行，Host 仍按精确匹配）；复用 A 卡唯一 SQL；无自动授权/无 identity 重建；代价是「写」——必须改卡面红线措辞（§3） |
| **(c) 仅能力协商 + 既有命令字段** | 只在 `core.ping` 加能力，不加命令/字段 | C-16 §0 | **否决**。能力不产生任何效果；既有命令（`ScanSourceSync`/`AuthorizeSourceReadForRun`/`RegisterSourceReadGrant`）都不改 location auth，Host 的 exact-match 也过不去。只会在「能力存在但行为不变」上制造误导 |

### 2.2 推荐形状（冻结草案，非最终字节）

**C-16 v1.5 只做三处 additive：**

1. **§0 能力**：新增 `source.reattest/1`。Host 在发送前用 `core.ping` 探测（沿用 `source.read.run/1` 的「不得靠发送后看结果判断」口径，C-16 `:20-22`）；缺失 → 不发送、不建任何文件、目标保持既有 typed skip。
2. **§2.5 `ReattestSourceLocation`（Host→Core，host-control）**：
   - 请求（closed shape）：`{"source_id":"<Core source id>","grant_id":"<source-read grant id>"}`；未知键/缺键/类型错误 → `INVALID_REQUEST`。
   - 校验顺序（冻结）：①host-only + session（普通 application 面 → `HOST_ONLY_REQUIRED`；session/credential 失败 → 既有码）②形状 ③grant live/未过期/未撤销/同 session（缺失/会话不符 → `SOURCE_ACCESS_DENIED`；过期 → `SOURCE_GRANT_EXPIRED`；撤销 → `SOURCE_GRANT_REVOKED`）④`grant.scope.source_id == source_id`（否则 `SOURCE_ACCESS_DENIED`）⑤grant 的物理身份（`facts.sha256/volume_serial/file_id/size`）必须等于该 source 的**当前** location 行（`content_digest/volume_serial/file_id/size_bytes`；不一致 → `SOURCE_ACCESS_DENIED`）⑥条件 UPDATE（复用 `refresh_source_location_auth` / `commit_source_location_auth_refresh` 的**唯一 SQL**）→ `updated = rowcount > 0`。
   - 响应：`{"updated": <bool>}`（closed shape；`updated:false` = 已是最新/单调保护，不是错误）。
   - 语义：**不是授权**。不创建/不复活/不延长任何 grant；本命令不写 Host Registry（Core 也无法写）；不建 plan/apply/journal/receipt；不发布资源；不重建 identity；只写 `source_locations` 三列（`registry_id/authorization_generation/last_verified_at`），`location_id/source_id/content_digest/volume_serial/file_id/size_bytes/observed_at/is_current` 与 `page_bindings` 全部不变；零 DB 写于任一拒绝路径；幂等；同 registry 代次不倒退、跨 registry 允许 1（复用 A 的单调条件）。**Host 侧铸 grant 仍走既有 `Authorize`**（`SourceAccessRegistry.cs:94-97` 的 `last_used_at` 审计写，是既有 mint 语义，不是本命令新增的授权）。
   - 错误码：**复用 §6，不新增**；消息/details 只允许计数/ID，无路径。
3. **§1 `source_list_roots` additive**：`roots_available: [bool, ...]`（与 `roots[]` 同序同长；派生、只读、不持久化；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`；不可用是 `false` 而非错误码）。不改变 `roots[]` 现有字符串数组。

**Host 侧（L-S4-B）最小接线：**

- `HostSourceScanTargetEnumerator.EnumerateAsync`（`SourceScanScheduler.cs:2041-2100`）在「列出 Core target → 建 entries 字典」之后、`TryMap` 之前，执行一次**有界的恢复 pre-pass**：
  - 只对「Core 记录的 `registry_id` 在 Host Registry 中存在且已撤销」的 target 工作（旧条目保留是 B1 的既有行为，`Revoke` 只置位不删除，`SourceAccessRegistry.cs:100-110`）；
  - 旧条目必须**恰一根**；存在**唯一**的 live 条目（非撤销）且**恰一根**、路径 normalize 后相等、`(volume_serial, file_id)` 相等（`SourceRoot` 自带登记身份，`SourceAccessRegistry.cs:8`）、且 live 条目的 `CreatedAt` **晚于**旧条目的 `RevokedAt`（证明确实是「撤销之后的再授权」，而不是历史重复条目），target kind 为非 folder（与 B1 的 file-source 承诺一致）；live 候选 >1 条 / 时间序不成立 → 歧义，不发送（保持 skip）；
  - 用 live 条目 `IssueAsync`（`SourceReadCoordinator.cs:337-356`）铸一个 grant（path 来自 live 条目；`source_id/version/kind` 来自 Core target；**预算沿用 `SourceScanOptions.MaxBytesPerSource/MaxEntriesPerSource`**，与 `SourceScanScheduler.ScanAsync` `:1533-1539` 同值，超预算按 `SOURCE_BUDGET_EXCEEDED` skip），能力探测（按 Run 先例缓存，`SourceReadCoordinator.cs:114-120`）通过才发送 `ReattestSourceLocation`；
  - **成功后重跑一次 `ListSourceScanTargets`**（Core 权威；不在 Host 侧伪造 Core 的 `registry_id/generation`），再按既有 `TryMap` 映射；失败按 target typed skip，log 只写 code；
  - 每轮 refresh 对同一 target 最多尝试一次，不做无界重试；**文件级 registry 损坏仍沿用整轮 `Unavailable`**（pre-pass 不得把 `SOURCE_REGISTRY_UNAVAILABLE` 降级为部分成功）；第二次枚举失败 → 保留第一轮结果（fail-closed：未重证的 target 不强行入集）。
- **触发**：冷启动 refresh（`HostRuntime.cs:1398-1403`）自动执行；B1 的显式重授权成功后，App 复用既有 `ISourceImportController.RequestSourceScanRefresh()`（`SourceImportModels.cs:66`；`HostController.cs:1571-1587`）主动触发一次（`ImportDockViewModel.cs:570-599` 成功分支；失败分支 0 调用）。
- **不新增 UI→Host 命令**：`HostCommandRegistry.All.Count` 不变（B1 AC-LSB-6 的 111 口径）；`tools/generate_api_inventory.py` 只解析 `IHostController.cs`/`RunContracts.cs`（`:24-29`），C-07 pin 不变；`SourceCommandNames`/parity 测试的 14 条不变。

> 设计取舍说明：为什么不让 Core 在 `ScanSourceSync` 里**隐式**刷新？那会把「扫描」变成写者，破坏 C-17 §5.3 的只读枚举/扫描预期，且 Host 的 exact-match 守卫在扫描**之前**就已经把 target 丢掉——隐式写根本没有机会发生。先 re-attest、再枚举，是唯一不破坏既有守卫的顺序。

### 2.3 1 pin 口径（明确到份数）

| 方案 | C-16 改动 | C-15 | C-17 | C-07 | M2-C1 | pin 数 |
|---|---|---|---|---|---|---|
| **B2 only** | §1 additive | 0 | 0 | 0 | 0 | **1/18**（C16 `ad25fb3c89bb` → 新值；其余 17 逐字节不变） |
| **B2 + reattest（推荐）** | §0 + §1 + §2.5 + §6/§7/§10 澄清行 | **0**（记录解释：`:204` 已要求重授权原地更新；`:314` 的显式动作就是 B1 的点击，reattest 只是记录事实，不是新恢复动作） | **0**（Host 仍 exact-match；先修行后映射） | **0**（不扩 `IHostController`；复用既有 App 端口方法） | **0**（协议 minor 3；additive host-control 命令，按 C-16 `:16` 先例） | **1/18** |
| **B2 + Host-only identity（b2）** | §1（仅 B2） | 0 | **实质变更**：§5.3 `:279` 的「撤销/代次不可核验 → fail-closed」被改写为「可按同路径+同身份重证」；要么 1 pin C-17，要么 DSH 显式解释（语义漂移） | 0 | 0 | **1–2/18** |
| **纯只读新命令（b1）** | §0/§2.x | 0 | 0 | 0 | 0 | 1/18，但**不达目标** |

**C-15 的严格性**：C-15 v1.5 `:204` 逐字要求「重授权/重新注册原地更新该行」；`:314` 要求根级恢复「由显式用户操作完成，不得自动」。推荐方案把「用户显式操作」= B1 的点击，「reattest」= 该操作的事实记录（不是第二个恢复动作、不是授权决定），因此**不需要改 C-15 字节**。这是本评审的推荐解释；如果 DSH 要求字面绝对无歧义，可在同一 C-16 载体里加一句 C-15 澄清 → **多 1 pin（C15）**，仍不改变实现形状。**不得**用「自动恢复」措辞写进 C-15。

**C-17 的严格性（为何不放松）**：C-17 `:279` 明确「registry 缺失/撤销/代次不可核验由 Host fail-closed」；推荐方案让 Core 先变成「可核验」，Host 的这条守卫原文不动，故零字节。b2 则直接改这条语义，必须走 C-17 UNFREEZE + 独立安全复核——这是本评审**不推荐** b2 的核心理由。

**C-07 / M2-C1**：不新增 `IHostController` 成员、不新增 App 端口方法（复用既有 `RequestSourceScanRefresh`），API inventory 实测 EXIT=0；`CORE_PROTOCOL_MINOR=3` 不变（`core_service.py` 的 additive 命令先例：`AuthorizeSourceReadForRun` 未 bump）。**C-06** 也不改：grant 形状/TTL/撤销/Verify 语义零变化。

---

## 3. Q3 红线：推荐形状如何保持、AC 如何判别

> 前提：**只读** 指枚举/投影命令（`source_list_scan_targets`、`source_list_roots`）与全部拒绝路径；**零 DB 写** 指这些命令与任何失败/拒绝路径。推荐形状里唯一的 **Core DB** 写是 `ReattestSourceLocation` 的**条件单行**更新（live grant + 同一身份 + 同一 source），它既不是「自动重新授权」，也不是「自动重建 identity」；Host 侧铸 grant 仍走既有 `Authorize` 的 `last_used_at` 审计写（既有 mint 语义，不是新行为）。卡面必须按这个口径改写 `:39` 的红线，否则实现者只能在「违反红线」或「不达目标」之间二选一。

| 红线 | 推荐形状的保持方式 | 判别性 AC（去掉修复/放宽即红） |
|---|---|---|
| **只读** | 枚举/投影命令不写任何表；reattest 不在枚举命令内隐式发生（独立 host-control 命令，Host 显式发送） | Core 枚举调用前后 **16 表快照**相等；Host 投影前后 **`registry.v1.dat` 字节**相等；把 reattest 塞进 `source_list_scan_targets`/`source_list_roots` 的 handler → 快照/字节红 |
| **零 DB 写（拒绝/失败面）** | 形状错、grant 缺失/过期/撤销、source_id 不符、identity 不符、无 location 行、能力缺失 → 全部 typed + 零写 | 每个负例：`source_locations` 与 16 表快照相等；去掉任一前置校验 → 行被改 → 红 |
| **零自动重新授权** | Core 不创建/不复活/不延长 grant；Host 不因现况自动 `Register`/`Revoke`；reattest 只在「存在 live 条目」时由 Host 发起；live 条目只能由 B1 的显式用户动作产生 | App 失败分支 refresh/reattest 计数 0；删掉 B1 的显式动作 → 无 live 条目 → 无 reattest；把「mint 失败就重注册」写回 → 红（B1 AC-LSB-5 续用） |
| **零自动重建 identity** | 三键（content_digest/volume/file）必须相等；不写回旧条目；不把新身份写进 registry/location | 同路径替换文件（新 volume/file）→ 无 live 匹配 → 不 reattest；把 identity 比较删掉 → 行被改成替换文件 → 红 |
| **不扩大授权面** | 请求无路径（path 只在签名 grant 内）；不接受任意 `registry_id/generation`（取自 live grant，Host 铸）；不新增 UI→Host 命令、不新增 `IHostController` 方法；folder 不支持（L-S4-2） | 接口出现 path/registry 入参 → 红；`HostCommandRegistry` 计数变化 → 红；folder target 被 reattest → 红 |
| **fail-closed** | 任一不可判定（多根、旧条目缺失、Core 行缺失、能力缺失、reattest 返回失败）→ 保持现状 typed skip；不「先扫后判」、不路径回退、不跳过 identity | 删掉「多根 → 不处理」分支 → 歧义 target 被映射 → 红；删掉能力门禁 → 旧 Core 收到未知命令/行为变化 → 红 |

**「零交互」的准确表述（建议写进卡面）**：

> 用户在 B1 的「重新授权此来源」成功后，**无需再次导入/apply/点击刷新**，Host 的下一次冷启动枚举或 App 主动 refresh 会完成条件 re-attest 与重新枚举；这是对**已发生的显式授权**的传播，不是新的授权决定，也不是无人值守的自动修复。

---

## 4. Q4 拆卡/顺序、In/Out、allowed_paths、AC 草案

### 4.1 拆卡建议（推荐：1 份契约 PREREQ + 2 张实现卡）

| 卡 | 内容 | 契约 | 建议 |
|---|---|---|---|
| **PREREQ-1（DSH/Lead 所有）** | C-16 v1.5 UNFREEZE：§0 `source.reattest/1`、§2.5 `ReattestSourceLocation`、§1 `roots_available[]`；冻结记录/矩阵/pin；独立 byte-level 复核 | **C-16 1 pin**；C-15/C-17/C-07 零字节 | **先做**；没有它，两张实现卡都不能开工 |
| **B2（可选，另卡）** | `source_list_roots` 只读可用性投影（Host）+ 测试；不改 App/UI/授权 | 依赖 PREREQ-1；零新增 | **暂缓**（无消费者）；若 DSH 要兑现「v1.5 一次性保留」，可在 PREREQ 里冻结字段，实现随 roots UI 再做 |
| **L-S4-B（推荐主体）** | Core 条件 re-attest 命令 + Host 枚举恢复 pre-pass + App 成功分支 refresh + 测试/证据 | 依赖 PREREQ-1；依赖 L-S4-A/B1 done（均已 done） | **本轮释放（改口径后）** |

**为什么 B2 与 L-S4-B 不能合成一张实现卡**：B2 是 Host 只读投影（碰 `SourceAccessRegistry.cs` 安全文件的只读方法），L-S4-B 是 Core 写路径 + Host 枚举顺序（安全语义更重）；两者唯一重叠是 `SourceReadCoordinator.cs`（B2 的字段投影 vs L-S4-B 的发送方法）。合成会把「wire 字段 + 新命令 + Core 写 + 枚举顺序」压进一个 Review，判别矩阵过大；分开后 B2 可独立回退/延后，L-S4-B 的 gated IPC 也能单独闭环。**若 DSH 要单窗口**：允许把 B2 作为 L-S4-B 卡内的独立 AC 块（先做 B2 的 Host 投影，再做 reattest），但 Review 必须分别出结论、`allowed_paths` 取并集。

### 4.2 推荐 In / Out（文件级）

**L-S4-B In（推荐）**

1. `src/bootstrap/core_service.py`：`_HOST_CONTROL_COMMANDS` 加 `ReattestSourceLocation`；dispatch 分支；`core.ping` 能力声明 `source.reattest/1`；handler 做 closed-shape、host-only/session、grant live、source_id/identity、单行 UPDATE。
2. `src/application/sources/reattest.py`（**新增**；或 `service.py` 内小函数）：解析 live grant、比对 location facts、调用唯一刷新 helper；不写第二份 SQL。
3. `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`：`ReattestSourceLocationAsync`（能力探测 + 发送 + typed 映射）；不改既有 `IssueAsync`/`Authorize`/撤销语义。
4. `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceRootReattestPlanner.cs`（**新增**；纯函数：target+entries → 可恢复候选/跳过原因）与 `SourceScanScheduler.cs`（`EnumerateAsync` 的 pre-pass + 成功后重枚举；`HostSourceScanTargetEnumerator` 构造参数加 coordinator）。
5. `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`：构造 enumerator 时注入 coordinator（`HostRuntime.cs:1350-1356`）；能力缺失时日志 code（无路径）。
6. `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs`：B1 重授权成功分支调用一次 `RequestSourceScanRefresh()`（失败分支 0 调用）。
7. 测试：`tests/core/test_host_control.py`（命令形状/host-only/session/错误闭集/零写）、`tests/fea11/test_source_reattest.py`（**新增**；行更新/幂等/单调/identity 负例/16 表快照）、`tests/core/test_core_scan_target_commands.py`（reattest 后枚举闭环）、`apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceReattestTests.cs`（**新增**；planner 纯函数 + 能力门禁）、`Fea11ScanIpcTests.cs` 或新 `Fea11ReattestIpcTests.cs`（gated 闭环）、`SourceRecoveryUiTests.cs`（App 成功/失败分支 refresh 计数）。
8. `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md`、`doc/reviews/FEA-11-L-S4-B-*.md`、`doc/handoffs/FEA-11-L-S4-B-*.md`、`verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/**`。

**L-S4-B Out（明确不写）**

- 自动重新授权/自动重注册/自动重建 identity/撤销后自动放行；任何 UI→Host 新命令或 `IHostController` 新成员；folder 源（L-S4-2）；`source_reset_registry` 后的自动恢复（旧条目已不存在，无可桥接）；B2 的 availability 字段（另卡）；真实用户数据/AppData/回收站；push；`TASK_LEDGER` 手工编辑（Lead 用 `tools/governance/task_ledger.py --write` 重建）。

**B2 In（可选，文件级）**

- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs`：**新增**只读投影方法（建议 `ListWithAvailability()`：`Locked(() => Load())` 快照后、**锁外**逐根探测；`List()`/`Authorize()`/`Save()`/`Load()` 语义零变化）。
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`：`source_list_roots` 响应加 `roots_available`。
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRootsAvailabilityTests.cs`（**新增**；或扩展 `SourceRegistryResilienceTests.cs`）。
- 卡/Review/Handoff/`verification/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1/**`。

**B2 Out**：`roots[]` 改对象数组、App/UI 展示（除非同卡明确加消费者）、授权/扫描语义、多根扫描修复（first-root 启发式不改；登记 limitation）、新命令/新错误码/新能力。

### 4.3 AC 草案（可判别 / fail-closed / 门禁）

> 以下为 scope review 建议稿，**未冻结**；编号/措辞待 DSH 定稿。

**B2（若释放）**

| ID | AC | 判别性（去掉修复即红） |
|---|---|---|
| **AC-B2-1** | 只 additive：`roots[]` 仍是字符串数组；`roots_available` 同序同长；旧响应/旧 App 兼容（缺字段按 unknown）；未知字段不破坏解析 | 把 `roots[]` 改成对象 → B1 `ParseRoots`/既有测试红 |
| **AC-B2-2** | 可用性正确：缺失根 → false；同路径替换（volume/file 变）→ false；健康根 → true；多根混合逐根独立，死根不毒化兄弟根 | 恒 true / 恒 false / 只探第一个根 → 混合用例红 |
| **AC-B2-3** | 零写/零副作用：`registry.v1.dat` 字节不变；`last_used_at` 不变；无 `.corrupt-*`；不铸 grant、不 revoke、不写 DB | 在 `List`/投影里顺手 `Save` → 字节断言红 |
| **AC-B2-4** | 文件级损坏语义不变：magic/长度/DPAPI/JSON/结构任一坏 → 整命令 `SOURCE_REGISTRY_UNAVAILABLE`，不返回部分 entries | 文件级坏却返回部分数组 → 既有 `FileLevelCorruptionStaysWholeFileFailClosed` 红 |
| **AC-B2-5** | 零新错误码/能力/命令；新字段不含路径/identity/secret；日志/证据无绝对路径 | 新字段回路径或新 code → 红 |
| **AC-B2-6** | 探测有界：每次 `source_list_roots` 至多每根一次 probe；不跨调用缓存；探测在快照后锁外进行，不持有 registry 全局锁做 FS I/O；单根 probe 异常 → false 不抛 | 把 probe 放回 `Locked()` 内长 I/O → 锁顺序/并发用例红（或显式登记可接受） |
| **AC-B2-7** | 门禁：pins 18/18（C16 新值）；check（默认 + `-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（用本卡起点重测值） | 任一失败/未跑未标 → 红 |

**L-S4-B（推荐形状）**

| ID | AC | 判别性 |
|---|---|---|
| **AC-LS4B-1 能力门禁/四象限** | `source.reattest/1` 缺失（旧 Core）→ Host 不发送、不建文件、行为与现状一致（target 仍 typed skip）；新×新才生效；能力探测异常 → 不发 | 删掉能力检查 → 旧 Core 用例红 |
| **AC-LS4B-2 Host 候选精确性** | 仅「旧条目已撤销、旧条目恰 1 根、live 候选**唯一**且恰 1 根、路径 normalize 相等、volume/file 相等、**live.CreatedAt > old.RevokedAt**、kind 非 folder」才进入候选；其余（多根/多 live/时间序不成立/路径不等/身份不等/无 live/未知 id）一律不发送，保持 skip | 放宽到「任意同路径/任选一条/忽略时间序」→ 替换/歧义/历史重复条目用例红 |
| **AC-LS4B-3 Core 身份门禁与零写** | 请求 closed shape；host-only/session；grant live/未过期/未撤销；`grant.scope.source_id == source_id`；grant facts **四键**（`sha256/volume_serial/file_id/size`）== 当前 location 行（`content_digest/volume_serial/file_id/size_bytes`）；任一不符 → typed §6 码 + **16 表快照零写** | 删掉 identity/source_id 校验 → 行被改 → 红 |
| **AC-LS4B-4 单行写/幂等/单调** | 成功只改 `registry_id/authorization_generation/last_verified_at`；location 行数不变；其余列逐列不变；重复调用 `updated:false` 且字节不变；同 registry 代次不倒退、跨 registry 允许 1 | 写第二列/新增行/代次倒退 → 红 |
| **AC-LS4B-5 无授权/无 identity 重建/不扩面** | Core 不创建/不复活 grant；Host Registry **不新增/不撤销/不改 roots 或 identity/generation**（仅既有 `Authorize` 成功的 `last_used_at` 按现状持久化）；不新增 source/version/entry；旧条目身份不被写回；请求无路径；不新增 UI→Host 命令；folder 拒绝 | 呼 `Register`/`RevokeSourceReadGrant`/新增撤销条目 → 红；folder 通过 → 红 |
| **AC-LS4B-6 闭环与前后判别** | 场景：旧条目撤销 + 新条目同路径同身份 + Core 行旧 → 现状枚举 skip；修复后：reattest 成功 → 重枚举返回新 pair → `TryMap` 映射 → 该 target 被扫描一次；未 reattest 的对照仍 skip | 不重枚举/不 reattest → 闭环红；把 skip 改成直接 scan → 见 AC-LS4B-2 |
| **AC-LS4B-7 触发** | 冷启动 refresh 自动尝试；B1 重授权成功后 App 调用一次 `RequestSourceScanRefresh`；失败分支 0 调用；每轮每 target 至多一次、无重试风暴 | 失败分支也 refresh → App 计数红；去掉成功分支 refresh → 重授权后不恢复 → 红 |
| **AC-LS4B-8 脱敏** | wire/log/error/details/证据：无绝对路径、无 entry 名、无 grant/secret 原文；命令只含 id；details 只计数 | 注入路径 fixture → 0 命中断言红 |
| **AC-LS4B-9 零漂移/门禁** | C-17/C-15/C-07/C-06/M2-C1 字节零 diff；`CORE_PROTOCOL_MINOR=3`；pins 18/18；check/API PASS；scope ⊆ allowed_paths；全量不降（起点重测） | 任一契约/协议号 diff → 红 |
| **AC-LS4B-10 不夸大/limitation** | 明写：只覆盖 file-source、同路径、同物理身份、显式重授权之后；`source_reset_registry` 后不自动恢复；folder/L-S4-2 不做；撤销后不自动放行；不得写「零交互自愈/自动重新授权/根级问题全解」 | 文案出现「自动重新授权/自愈」→ 红 |

---

## 5. Q5 测试/证据：三层可行性、门禁成本与 flaky

### 5.1 三层可行性（现有 fixture/模式）

| 层 | 可行性 | 现有可复用资产 | 最低新增 |
|---|---|---|---|
| **Core（Python）** | **高**。host-control 测试有 `_server(tmp_path)` + `_request` 真实 stdio 模式（`tests/core/test_host_control.py:180-247`）；`source_locations`/grant 可用 `tests/fea11/conftest.py` 的 `add_source_tree(..., registry_id, generation)`（`:281-309`）与 `mint_grant(..., registry_id, generation)`（`:161-229`）；16 表零写快照已有 `tests/fea11/test_source_sync.py:588-640` | `test_host_control.py`、`test_source_command_parity.py`、`test_core_scan_target_commands.py`、`test_source_scan.py` | 新 `tests/fea11/test_source_reattest.py`：成功行更新、columns 断言、幂等/单调、identity 不符/撤销/过期/无行零写、shape/host-only、能力声明；枚举闭环扩 `test_core_scan_target_commands.py` |
| **Host（.NET）** | **高（拆分后）**。`TryMap` 是纯函数（`SourceScanSchedulerTests.cs:1045-1121`），planner 可同样做成纯函数；registry 测试有 `SourceRegistryResilienceTests` 的隔离 fixture；真实发送路径用 gated IPC（`Fea11ScanIpcTests` 的 `NEWMANGA_FEA11_IPC=1` 模式） | `SourceScanSchedulerTests.cs`、`SourceRegistryResilienceTests.cs`、`Fea11ScanIpcTests.cs`、`SourceRecoveryIpcTests.cs` | 新 `SourceReattestTests.cs`（planner 候选/跳过矩阵、能力缺失不发、旧条目缺失/多根/身份不等）；扩 `Fea11ScanIpcTests` 一条「旧行 → reattest → 枚举映射 → 扫描」闭环 |
| **App（C#）** | **高**。`SourceRecoveryUiTests` 已有 fake controller + 帧计数（B1 的 `FrameNames()`/`CountCommandLiterals` 模式）；重授权成功/失败分支可直接计数 `RequestSourceScanRefresh` | `SourceRecoveryUiTests.cs`、`FakeHostController.cs`、`ImportDockViewModel` 测试既有模式 | 1 个成功分支用例 + 1 个失败分支用例（refresh 0/1） |
| **真实 IPC** | **高**。B1 的 gated 闭环（`NEWMANGA_FEA11_IPC=1`，1 passed）已证明该模式可承载「注册→替换→typed 失败→显式重授权→再预览→导入→枚举新代次」；本卡再加 reattest 一段 | `SourceRecoveryIpcTests.cs`、`Fea11ScanIpcTests.cs` | 1 条 canonical gated 证据（phase A 现状 skip；phase B reattest 后枚举/扫描恢复） |

### 5.2 必须新增的测试（最低集）

1. **Core**：`ReattestSourceLocation` 形状/host-only/session；成功单行三列；location 行数不变；重复幂等；同 registry 代次倒退 0 行；identity（digest/volume/file/size）任一不符 0 行；grant 过期/撤销 typed 且 0 行；无 location 行 typed 且 0 行；`grant.scope.source_id` 不符 0 行；能力声明。
2. **Core 闭环**：`source_locations` 旧 pair → reattest → `source_list_scan_targets` 返回新 pair，`identity_digest/project_ids` 不变、枚举零写。
3. **Host planner**：旧条目撤销 + 新条目同路径同身份 → 候选；多根/路径不同/身份不同/无 live/未知 registry → 无候选；folder → 无候选；能力缺失 → 无发送。
4. **Host gated IPC**：真实 Core + 真实 Registry + 真实文件 → 现状枚举 skip；触发 refresh → reattest → 重新枚举 → target 入集并可扫描；wire 帧含 `ReattestSourceLocation` 恰 1、无路径。
5. **App**：重授权成功 → `RequestSourceScanRefresh` 恰 1；失败 → 0；不新增命令。
6. **B2（若释放）**：混合 registry 逐根 available；替换/缺失 false；健康 true；`List` 前后 registry 字节相等；文件级损坏仍整命令失败；探测不写 `last_used_at`。

### 5.3 全量门禁成本 / flaky / 基线矛盾

| 项 | 记录值 | 说明 |
|---|---|---|
| `pytest tests` | **3317 passed / 10 skipped**（B1 closeout，`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md:85`；L-S4 review 实测 3305/10 + 12） | 成本约 244 s（L-S4 scope review 实测）；本卡应只增不降 |
| `pytest tests/fea11 tests/core` | 1158 passed / 76.72 s（L-S4 scope review 实测） | 本卡新增后按新数跑 |
| 全量 .NET | **记录冲突**：STATUS `:20` **1570/0/92**；B1 卡 `:85` / progress `:10` **1617/0/93** | 下一卡必须在 clean head 上**重测**并写「起点基线」；不得继承旧数 |
| 已知 flaky | `FluentResidual2VisualEvidenceTests`（Lead combined 全量曾命中，隔离复跑 1 passed）；SCAN-2 记录 FluentAssertions/Threading/reflection 三类偶发 | AC 要求**原样记录 + 隔离复跑**，不得「重跑到绿」 |
| 写入卫生 | 全量 pytest 历史上有改写 `verification/FEA-09/logs/wire-redacted.ndjson` 的记录；`SourceRegistryTests` 写 `verification/FEA-09/native-registry/**` | 跑后 `git status`；只恢复**测试产生的** `verification/FEA-09` 变更；本报告的单一写入约束不变 |
| gated IPC | B1 `NEWMANGA_FEA11_IPC=1` 1 passed（`SourceRecoveryIpcTests`） | 本卡复用同门禁；不要为一条证据跑全量 |
| pins / check / API | 本评审实测 **18/18**、check PASS(3w)×2、API EXIT=0 | 契约 UNFREEZE 后 C16 pin 重算，仍 18/18 |

> 本评审**未跑**全量 pytest/.NET/gated IPC 的理由见 §0；上述数字均为**既有记录**，不是本评审对 clean head 的 PASS 声明。实现卡必须自行重跑并入库。

---

## 6. Q6 优先级与 DSH 裁决点（含推荐）

### 6.1 与队列中其他项的对比

| 项 | 性质 | 用户可见性 | 成本/契约 | 相对建议 |
|---|---|---|---|---|
| **L-S4-B（推荐写形状）** | 监控静默丢失（重授权后不重导入即不恢复） | 中 | 中高：1 pin C-16 + Core 条件写 + Host 枚举顺序 + App 1 行 + 三层测试 | 若本轮目标是**收尾 FEA-11 L 系列**，它是最合理的一张；但必须改口径 |
| **B2** | wire 投影，无消费者 | **当前无** | 小：1 pin（可与 L-S4-B 同载体）+ Host 只读 + 测试 | **延后**到 roots UI 立项；若为兑现「v1.5 一次性保留」可只冻结字段 |
| **2C 长 Run 续期（L-G1）** | 功能缺口（>300 s 长 Run 失权） | **高**（长任务中断） | 高：新 host-control/续期设计 + 可能多 pin + 跨分片 | **用户价值高于 L-S4-B**；若产品连续性优先，应先于本批；至少另卡设计 |
| **L-R11** | gate 统一/审计一致性 | 低 | 小-中；0 pin | 可穿插 |
| **C-04b** | 8 项文档 residual | 无 | 极小；0 pin | 穿插 |
| **SCAN-RH** | 可观测性/limitation | 低 | 小；0 pin | 穿插 |
| **UI P3** | 视觉/交互 | 低 | 小；0 pin | 最后 |

**推荐顺序（供 DSH 裁决）**：**① PREREQ-1（C-16 v1.5，按本报告推荐形状）→ ② L-S4-B（写形状）**；B2 暂缓/只冻结字段；**③ 2C 另卡设计**（若 DSH 认为长 Run 用户价值更高，可把 2C 提到 L-S4-B 之前）；④ L-R11 → ⑤ C-04b/SCAN-RH/UI P3 穿插。**不建议**为 B2 单开窗口（无消费者），也不建议在没有 PREREQ 的情况下先写实现。

### 6.2 需 DSH 裁决的问题（含推荐）

| # | 问题 | 推荐 | 影响 |
|---|---|---|---|
| **D-1** | L-S4-B 的「只读 / 零 DB 写」红字是绝对约束，还是只约束枚举/投影命令？ | **只约束枚举/投影与拒绝路径**；reattest 是「显式重授权后的条件单行事实记录」，改写 `:39` 红字并加 AC-LS4B-5 | 决定卡是「可冻结」还是「BLOCKED」 |
| **D-2** | 形状选哪个：只读新命令（b1）/ Host-only identity（b2）/ 条件写 reattest（b3）？ | **b3**。b1 不达目标；b2 需 C-17 语义变更（+1 pin）与安全复核；b3 保留 C-17 守卫、1 pin、复用 A 的 SQL | 决定 pin 数与安全面 |
| **D-3** | B2 是否纳入 v1.5？ | **可纳入字段（additive）但延后实现**；或把 v1.5 只给 L-S4-B，B2 另开 v1.6。**不建议**为无消费者字段单开实现卡抢占窗口 | 决定版本号分配与窗口 |
| **D-4** | 拆卡：PREREQ + 2 实现卡，还是 PREREQ + 1 合并卡？ | **PREREQ + B2（可选）+ L-S4-B**；若单窗口，B2 作为 L-S4-B 的独立 AC 块（`SourceReadCoordinator.cs` 重叠需顺序） | 决定 Review 规模与 merge 冲突 |
| **D-5** | 触发器：冷启动 + B1 成功后 refresh，是否足够？ | **足够**；不新增 UI→Host 命令；App 只在成功分支调用一次既有 `RequestSourceScanRefresh` | 决定 App 写域与「零交互」定义 |
| **D-6** | C-15 是否需要一句「reattest 不是新恢复动作」的澄清？ | **推荐不加字节**（按 `:204` 重授权原地更新 + `:314` 显式动作解释）；若 DSH 要求字面严格，+1 pin C-15 | 决定 1 pin 还是 2 pins |
| **D-7** | 错误码：是否新增「re-attest 专属码」？ | **不新增**；复用 §6（`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_*`/`SOURCE_REGISTRY_UNAVAILABLE`/`CORE_CAPABILITY_MISSING`/`INVALID_REQUEST`），`updated:false` 是成功 | 决定 wire/兼容与错误闭集 |
| **D-8** | 测试起点基线：STATUS 的 1570 还是 B1 的 1617？ | clean head **重测**后写「本卡起点」；不继承任一旧数；pytest 以 3317/10 为下限再重测 | 决定 AC-LS4B-9 可判性 |
| **D-9** | 优先级：本批 vs 2C？ | 若目标是 FEA-11 L 尾收口 → 本批（L-S4-B）先；若用户连续性优先 → 2C 先。**B2 不应抢占** | 决定下一活动 Task |

---

## 7. 风险

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| **R1** | DSH 不接受改口径 → 卡面「只读/零写」与目标矛盾，冻结后实现者只能违背其一 | **高** | 本报告先 BLOCKED；D-1/D-2 明确后再冻结；卡面逐字改红线与「零交互」定义 |
| **R2** | 「自动恢复」被读成「自动重新授权/自愈」 | 高 | 卡面/文案/证据统一限定「显式重授权之后」；AC-LS4B-10；C-15 `:314` 原文保留 |
| **R3** | reattest 被当成通用「修授权」入口，扩大到撤销后放行/自动重注册 | 高 | 只允许 live grant + live 非撤销条目 + 同一身份；AC-LS4B-3/5；不改 Host Registry；不新增 UI 命令 |
| **R4** | Host 候选匹配放宽（同路径但不同身份/多根/历史重复条目）→ 把替换文件当同源或复活旧授权 | 高 | 候选只接受「恰一根 + volume/file 相等 + `live.CreatedAt > old.RevokedAt`」；AC-LS4B-2；替换/历史重复用例判别 |
| **R5** | Core 行被 reattest 后，仍与旧 binding 的 `authorization_generation` 语义冲突 | 中 | C-15 `:324` 的「binding ≤ 当前 generation」不变；reattest 不写 binding；AC-LS4B-4 断言 binding 不变 |
| **R6** | 枚举 pre-pass 增加 Core 调用/延迟，冷启动变慢或风暴 | 中 | 每轮每 target 至多一次；能力缺失不发送；失败 per-target skip；有界 target 数（C-17 `:279` 的 10000 上限不变）；**恢复目标会双哈希**（reattest grant 一次 + 随后 scan grant 一次）——一次性成本，卡面写明；不得为省哈希而放宽身份校验 |
| **R7** | 基线矛盾（1570 vs 1617）导致 AC 误判 | 中 | D-8：clean head 重测；证据写「起点/终点 + 差值归属」 |
| **R8** | 全量测试污染 tracked 证据（`verification/FEA-09/**`） | 中 | 跑后 `git status`；只恢复测试产生的变更；gated IPC 优先；不要为证据跑全量 |
| **R9** | `source_reset_registry` 后无旧条目 → 无法自动恢复，用户仍须重导入 | 低-中 | 登记 limitation；不宣称「重置后也能自动恢复」 |
| **R10** | folder 源（L-S4-2）身份键不一致 → reattest 误判 | 中 | 本卡明确 folder 不支持；AC-LS4B-2/10；L-S4-2 另卡 |
| **R11** | B2 探测在 registry 全局锁内做 FS I/O → 拖慢/阻塞 revoke/register | 中 | 快照后锁外探测；AC-B2-6；探测有界、不缓存 |
| **R12** | B2 的 first-root 扫描启发式被误认为「多根已修复」 | 中 | 卡面/AC 明写只做投影；first-root 问题登记 limitation，不宣称修复 |
| **R13** | C-17 journal 撤销撕裂（B1 已登记）被误以为本卡修复 | 低 | 保留 limitation；不动 `HostOperationOrchestrator.cs:112-133` |
| **R14** | 1 pin 被误读为「无契约风险」 | 中 | 本报告 §2.3 明确 pin 数与 C-15/C-17 解释；byte-level 复核 + 独立 Review 仍必需 |

---

## 8. 证据锚点索引（结论 → 可复核位置）

| 结论 | 锚点 |
|---|---|
| B1 重授权生成新 registry_id + gen=1；撤销保留旧条目 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs:34-52`、`:100-110` |
| Authorize 逐请求核验/拒绝撤销/gen 漂移 | `SourceAccessRegistry.cs:62-98`、`:131-139` |
| List 返回全部条目、无可用性字段 | `SourceAccessRegistry.cs:54-60`；`SourceReadCoordinator.cs:621-624` |
| Core 的 location auth 只由写路径刷新（唯一 SQL） | `src/infrastructure/sqlite/library.py:2293-2339`、`:2341-2353`、`:2652-2655`；`src/application/importing/referenced/runtime.py:408-411`、`:462-468`、`:571`、`:689`、`:905-906`、`:925`；`src/application/sources/service.py:500-516` |
| host-control 闭集无 reattest；RegisterSourceReadGrant 只内存注册 | `src/bootstrap/core_service.py:355-367`、`:4906-4914` |
| Core 枚举读 location 行、零写 | `src/application/sources/scanner.py:96-177`（`:166-167`）；`src/infrastructure/sqlite/source_sync.py:75-94`；C-17 `:228` |
| Host 枚举精确匹配/撤销 skip/gen 漂移 skip/执行期再核验 | `SourceScanScheduler.cs:2162-2169`、`:1505-1512`、`:1561-1610`、`:1627-1632` |
| 冷启动枚举一次；App 只在 completed import 后 refresh；tick 不枚举 | `HostRuntime.cs:1350-1403`、`:193-220`；`ImportDockViewModel.cs:700-710`；`SourceScanScheduler.cs:1118-1151`、`:894-919` |
| B1 成功只重跑预览，不导入/不 refresh | `ImportDockViewModel.cs:570-599`；`SourceRecoveryModels.cs:411-525` |
| B2 无消费者；App 解析单根并忽略未知字段 | `SourceRecoveryModels.cs:644-674`、`:604-619`；`SourceImportModels.cs:243-252` |
| 多根 first-root 扫描启发式 | `SourceScanScheduler.cs:2171-2176`、`:1599-1632` |
| `roots[]` 冻结形状 | C-16 `:30`；C-16 §7.3 `:199-201` |
| 零 DB 写/只读枚举冻结语义 | C-16 `:89`（§2.4）；C-17 `:228`、`:279`；C-15 `:313-314` |
| C-15 重授权原地更新 | `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:204`；`:314` |
| C-17 fail-closed 守卫 | `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:279`、`:261-262`、`:276` |
| 既有测试固化「撤销/gen 漂移 → skip」 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs:1107-1121`、`:1134-1220` |
| A 的枚举闭环测试（只证刷新后枚举跟随，不证无写路径恢复） | `tests/core/test_core_scan_target_commands.py`（L-S4 AC-LS4-6，卡 `:74`） |
| 16 表零写快照 | `tests/fea11/test_source_sync.py:588-640` |
| gated IPC 模板 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRecoveryIpcTests.cs`；B1 卡 `:86` |
| 基线矛盾 | `doc/STATUS.md:20`（1570/0/92）vs `doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md:85`（1617/0/93）、`doc/handoffs/DSH-PROGRESS-2026-11-07.md:10` |
| 本卡占位现文（只有 4 条 doc/verification allowed_paths） | `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md:3-7`、`:22-26`、`:37-43` |

---

## 9. 建议的 In/Out/allowed_paths 可直接粘贴稿（供 DSH 冻结参考）

### 9.1 L-S4-B（推荐形状）

```yaml
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md
  - doc/reviews/FEA-11-L-S4-B-*.md
  - doc/handoffs/FEA-11-L-S4-B-*.md
  - verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/**
  - src/bootstrap/core_service.py
  - src/application/sources/reattest.py            # 新增（或 service.py 内小函数）
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceRootReattestPlanner.cs   # 新增
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - tests/core/test_host_control.py
  - tests/fea11/test_source_reattest.py            # 新增
  - tests/core/test_core_scan_target_commands.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceReattestTests.cs   # 新增
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SourceRecoveryUiTests.cs
```

> `src/infrastructure/sqlite/library.py` **不在** allowed_paths：只复用既有 `commit_source_location_auth_refresh`，不得新增第二份 SQL。`doc/plan/**`（C-16 字节）由 PREREQ 卡/Lead 负责，本卡不得碰。

### 9.2 B2（可选）

```yaml
allowed_paths:
  - doc/tasks/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1.md
  - doc/reviews/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1-*.md
  - doc/handoffs/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1-*.md
  - verification/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRootsAvailabilityTests.cs   # 新增
```

> 若 DSH 要同窗口消费 B2，再追加 App 的 `SourceRecoveryModels.cs`/相应 View（另立 AC）；否则 B2 只做 Host 投影，`roots_available` 暂由未来的 roots UI 消费。

---

## 10. 真实性声明

1. **唯一写入**：本评审只写了 `doc/reviews/C16-V15-BATCH-scope-r1.md` 这一个文件。**未**修改/删除/移动任何生产代码、测试、契约、冻结记录、矩阵、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或证据字节；**未**执行 `git add`/`git commit`/`git push`。
2. **独立性**：评审者为独立上下文的 fresh subagent，未参与 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`、`FEA-11-L-S1-B-RECOVERY-REAUTH-1`、`FEA-11-L-S1-REGISTRY-RESILIENCE-1`、`FEA-11-RUN-GRANT-*` 或本占位卡的任何实现、返修、审查；只读被审 head。
3. **事实优先级**：所有代码/契约断言均来自 `614aff07f` 的工作树字节（`git status` clean、无并发提交），逐条给出 `path:line`；未采信卡面/Handoff/Review 的自述作为实现事实（引用时标注为「既有记录」）。
4. **实测命令**（已跑，EXIT 见 §0）：`git rev-parse HEAD`、`git status --porcelain`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`（18/18 PASS）、`pwsh -NoProfile -File tools/governance/check.ps1`（默认 + `-TaskPath`，PASS 3w ×2）、`python tools/generate_api_inventory.py --check`（EXIT 0）、`python -m pytest tests/fea11/test_source_command_parity.py tests/core/test_core_scan_target_commands.py -q`（12 passed）、`dotnet test ... --filter FullyQualifiedName~SourceRegistryResilienceTests`（8/0/1）。
5. **NOT_RUN**（未跑、不声明 PASS）：全量 `pytest tests`、全量 `dotnet test NewManga.sln`、`NEWMANGA_FEA11_IPC=1` 真实 IPC、真实用户数据/AppData/回收站、C-16 v1.5 的 byte-level 复核。理由见 §0（只读 scope review；避免写入 tracked 证据树；无实现 head）。§5.3 的数字均为**既有记录**，不是本评审实测。
6. **判别力声明**：本报告未做「破坏-恢复」实验（只读约束下不能改生产/测试字节）；§3/§4.3 的「判别性」是给实现卡/Review 的**待验证项**，不是本轮已完成证据。
7. **建议性质**：本报告的 In/Out/allowed_paths/AC/UNFREEZE 判定均为**建议**；scope 冻结、契约字节变更、Review Appointment、findings 处置与集成验证属 DSH。
8. **limitation**：本报告不评估 2C/L-R11/C-04b/SCAN-RH/UI P3 的实现细节，仅做优先级比较；不声称 C-16 v1.5 字节已就绪（需 PREREQ 载体 + 独立 byte-level 复核 + pin 重算）。
