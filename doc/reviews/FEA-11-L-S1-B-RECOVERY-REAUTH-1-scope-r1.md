---
task: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: Scope Review r1：根级恢复/重授权入口（B：App 显式恢复；`source_list_roots` 可用性投影是否必须）
reviewer: fresh subagent（独立上下文；未参与 L-S1 A / L-S4 A 的实现、返修或审查；只读）
session: 7d2a572e-28bf-4c96-9c96-949678ca6339
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: d6bc6b11b73d2bf5e53b59a2e4e5e46c65d65cb7
verdict: READY-WITH-UNFREEZE
verdict_scope: 按「最小显式恢复入口」收窄（B1 = App-only、Host 零改动、C-16/C-15/C-17/C-07 零字节、0/18 pins）= **READY-TO-FREEZE**；按占位卡原文（含 `source_list_roots` 可用性投影 / 与 L-S4-B 的零交互自动恢复合并，B2）= **需 C-16 v1.5 UNFREEZE（1/18 pins）**。本报告建议前者先释放、后者另卡。
---

# Scope Review r1：FEA-11-L-S1-B-RECOVERY-REAUTH-1

> **审查对象**：`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`（`proposed` 占位，`approval` 自述「需 C-16 v1.5 UNFREEZE（零交互自动恢复只读枚举/可用性投影，1 pin）」）。
> **审查口径**：只读；事实以 `d6bc6b11b` 的仓库字节为准；未运行项一律 `NOT_RUN`（§7）。
> **本报告只提 scope 建议与裁决输入**：不冻结 scope、不改卡、不改契约、不改 STATUS/PLAN/LEDGER、不 `git add/commit/push`。

## 0. 结论先行

**verdict：`READY-WITH-UNFREEZE`（按拆卡口径：B1 `READY-TO-FREEZE`；B2 需 1 pin）。**

1. **A 卡之后，产品内确实没有恢复路径，而失败是确定性复现的**（不是概率/时序问题）：App 的根复用选择器按「单一 root 字符串相等 + 非 revoked」挑条目（`SourceImportModels.cs:768-786`），被替换/缺失的条目**永远排在被复用位置**；随后同一 `registry_id`/`generation` 的铸造在 `Authorize` 内逐请求重核根身份失败（`SourceAccessRegistry.cs:89-91`、`:131-139`），于是**同一路径的重导入永久失败**，用户看到的只是一句「源授权存储不可用」（`ImportDockViewModel.cs:292-298`、`SourceImportModels.cs:519`）。
2. **占位卡的前提有一半不成立：最小可用恢复不需要任何契约改动。** `source_revoke_root` 与 `source_register_root` 都是 **C-16 v1.4 既有命令**（`:29-32`），Host handler 已实现（`SourceReadCoordinator.cs:618-620`、`:627-644`），Core 侧 ACK 已实现且**允许空 `grant_ids`**（`core_service.py:4928-4938`、`source_read_refs.py:230-251`）；App 侧 **0 接线**（§2.2）。「撤销失效条目 → 重新登记同路径 → 重导入」这条链**今天就能走通**，只是没有入口。**故 B1 = App-only、Host/Core/契约零改动、0/18 pins。**
3. **C-16 v1.5 只在一种设计下才是必须的**：要把「每个已登记根的当前可用性」做成**wire 投影**（`source_list_roots` 响应加字段）或新增只读枚举命令，供一个「源列表/健康」界面使用。对「用户按失败路径显式恢复」这一最小目标，它是 **nice-to-have，不是必需**（§3）。仓内也没有任何 roots 管理界面可承载该投影。
4. **占位卡把两张不同的卡塞进了同一个 approval 句**：`source_list_roots` 可用性投影属本卡（L-S1-B）的加分面；而「零交互自动恢复只读枚举」是 **L-S4-B**（`FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md:80` 的 L-S4-1 limitation），需要**新 host-control 命令 + 新能力**（`doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-scope-r1.md:173`）。两者都自称 **C-16 v1.5** → **版本号/载体冲突**，必须由 DSH 一次性分配（§6 D-3）。
5. **完整闭环依赖 L-S4-A 已经落地的 location auth 刷新**：`revoke → re-register → re-import` 后，页单元在同事务内按「同 digest/volume/file」刷新 `source_locations.registry_id/generation`（`library.py:2652-2655`、`library.py:2293-2353`、`service.py:508-516`；跨 registry 允许 generation 1），枚举随后跟随 → 扫描恢复。**这条链一个新字节的契约都不需要**；不接 L-S4-A，B1 只能做到「导入解阻」，扫描仍不恢复（必须写进 limitation）。
6. **红线在最小方案里可机械判别**（§4）：禁止把 typed 失败转成自动重登记（这会正好复刻「自动重新授权」）、禁止 Host 侧回写 identity、禁止撤销后自动放行、禁止引入任意路径输入或新命令/能力。
7. **门禁现状**：`verify_pins.ps1` **PASS（18/18）**；`check.ps1 -TaskPath` **PASS（3 warnings）**；台账 530 files / 520 terminal / 9 non-terminal，本卡在 `TASK_LEDGER.md:45` 记为 `proposed`。`STATUS.md:20` 的测试基线（pytest 3249/10、.NET 1527/0/86）已落后于最近 closeout（**3317/10、1570/0/92**），冻结前需 Lead 修正（§6 D-10）。

## 1. 只读基线表

| 项 | 值/命令 | 结果 |
|---|---|---|
| HEAD | `git rev-parse HEAD` | **`d6bc6b11b73d2bf5e53b59a2e4e5e46c65d65cb7`**（main，`docs(fea-11-l-s4): r1 最终并发披露澄清入库`） |
| 与任务书差异 | `git log --oneline -1 1c4ad82a9`、`git show --stat d6bc6b11b` | 任务书写的 `1c4ad82a9` 是**父提交**；`d6bc6b11b` 只改 `doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-r1.md`（+6/−5），`src/**`/`tests/**`/`apps/**`/`doc/plan/**`/`doc/contracts/**` **零 diff** → 不影响本 Review 事实 |
| 工作树 | `git status --porcelain=v1` | 审查开始时 **clean（0 行）**；结束时仅本报告 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 18）**；C15 `f9e376a0ed4c`、C16 `ad25fb3c89bb`、C17 `aefa0fa5b17e`、C07 `3fdb44e49afe` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md` | **PASS（3 warnings）**，EXIT 0：9 个非终态 Task；STATUS 3089B/27 行、PLAN 6866B/62 行达 80% 预算 |
| 台账 | `doc/TASK_LEDGER.md:9-16`、`:45` | 530 files / 520 terminal / 9 non-terminal / 1 named in plan；本卡 `proposed`、`named in plan = no` |
| 契约现状 | `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:3`、`FEA-C15…:3`、`FEA-C17…` | C-16 **FROZEN v1.4**、C-15 **FROZEN v1.5**、C-17 v1.1；A/L-S4 均已 done |
| 定向/全量测试 | `dotnet test`、`pytest tests` | **NOT_RUN**（scope review 只读；`SourceRegistryTests` 会把 fixture 写进 `verification/FEA-09/native-registry/**`，`SourceRegistryTests.cs:140-145`；跑测会污染只读工作树） |
| 真实 IPC | — | **NOT_RUN**（同上，且本 Review 不判定实现质量） |

## 2. Q1 现状核实（A 卡之后，单根不可用时的真实用户路径）

### 2.1 五条路径逐条

| 用户动作 | 代码链（path:line） | A 之后的结果 |
|---|---|---|
| **新导入**（未登记过的路径） | `PlanReferencedImportAsync` → `SourceImportCoordinator.PlanAsync`（`SourceImportModels.cs:569-590`）→ `FindOrRegisterRootAsync`（`:759-801`）→ `source_register_root`（`:790-792`）→ `IssueAsync`→`Registry.Authorize`（`SourceReadCoordinator.cs:400`） | **可用**（AC-L2 已证）：注册不再因别的根不可用而整库失败 |
| **同路径重导入（健康根）** | `FindOrRegisterRootAsync` 命中既有条目（`:782-786`）→ `Authorize` 复核通过 | **可用** |
| **同路径重导入（根被替换/缺失）** | 同上，但 `Authorize` → `VerifyRootIdentity`（`SourceAccessRegistry.cs:91`、`:131-139`）→ typed `SOURCE_REGISTRY_UNAVAILABLE` | **永久失败**（见 2.3），用户只看到「源授权存储不可用」（`:519`） |
| **撤销**（`source_revoke_root`） | 命令表存在（`HostCommandRegistry.cs:149`、`:384`、`:490`）；Host handler 存在（`SourceReadCoordinator.cs:627-644`）；Host 路由存在（`HostRuntime.cs:924-930`，需 `WritesAllowed`，`:926`） | **App 侧 0 调用 → 用户不可达** |
| **重置**（`source_reset_registry`） | 同上（handler `SourceReadCoordinator.cs:625-626` → `Registry.Reset`，`SourceAccessRegistry.cs:112-120`） | **App 侧 0 调用 → 用户不可达** |
| **恢复/重授权** | —— | **不存在**（本文档的核心事实） |

补充：扫描侧同样是「静默丢失监控」而非崩溃——跨目标映射在「registry 里没有该 id / 已撤销 / 代次不等」时**直接丢 target**（`SourceScanScheduler.cs:2162-2169`），执行期复核再 typed skip（`:1561-1634`）；枚举状态只存在于进程内记录（`SourceScanStatus.cs:4-7`、`:63-73`），**不是 wire、也不是 UI 面**——App 里既没有扫描状态卡片，也没有源列表（全仓 App 侧对 `SourceScanStatus` 零引用）。

### 2.2 为什么 `source_reset_registry` / `source_revoke_root` 在 App 侧是 0 调用

三件事实同时成立，缺一不可：

1. **命令表有**：`HostCommandRegistry.cs:149`（`LibraryNames`）、`:384`（`HostLocalBindings`）、`:490-491`（`SourceCommandNames`）；
2. **Host handler 有**：`SourceReadCoordinator.cs:609-658` 的 `switch`（`:625-626` reset、`:627-644` revoke）；
3. **UI/Vm/App 服务无接线**：App 侧对 `source_*` 的**全部**调用只有两处——`SourceImportModels.cs:762`（`source_list_roots`）与 `:791`（`source_register_root`）；`ISourceImportController`（`:23-67`）只有 Plan/Start/Receipt/Cancel/RefreshScan 五个成员；`HostController` 的这条面明确「kept OUTSIDE the frozen C-07 IHostController inventory」（`HostController.cs:1378-1383`）；`ImportDockView.axaml:111` 只有一个只读错误 `TextBlock`，没有任何撤销/重置/重授权按钮。

即：**不是被策略挡住（`HostRuntime.cs:926` 只要求 host 可写，生产默认可写），而是从来没做过入口接线。**

### 2.3 「被替换根同路径重导入为何持续失败」——确定性链路

1. App 先列根：`source_list_roots`（`SourceImportModels.cs:761-763`）；
2. 选择器只按「`roots` 恰好 1 条、字符串等于请求路径、非 revoked、有 generation」命中（`:768-786`），**不校验可用性**（响应里本来也没有该字段，`SourceReadCoordinator.cs:622-624`）；
3. 命中后**原样复用**该条目的 `registry_id`/`generation`（`:782-786` → `:748-751`）；
4. 铸造时 `Registry.Authorize` 在同一把锁内、读盘之后逐请求重核该根身份（`SourceAccessRegistry.cs:62-98`、`:131-139`）→ 不匹配 → typed `SOURCE_REGISTRY_UNAVAILABLE` 且**零写**；
5. 下一次重导入回到第 1 步，选中的仍是同一条失效条目 → **永久失败**。注册分支（`:790-792`）**根本到不了**，所以「再注册一次就好了」这个直觉在现状下无效。

**加分点（重要）**：即使 App 绕过复用直接注册同路径，也会先追加一条**新条目**（`Register` 不查跨条目重复，`SourceAccessRegistry.cs:34-52`），旧失效条目仍排在前面 → 选择器仍挑旧的 → 依旧失败。**所以「不动顺序/不撤销」的补丁都不成立**，只有「先让旧条目退出复用集合」才行——这正是撤销（`RevokedAt` 非空即被选择器跳过，`:771`）或删除（无此命令）二选一。

### 2.4 幂等/顺序陷阱（实现前必须钉住）

- 同一路径可能有**多条**非撤销重复条目（历史盲注册 + `Register` 无跨条目去重）：只撤销首条仍会命中第二条 → **必须「撤销全部同路径非撤销条目 → 再注册」**，且顺序不可交换。
- 撤销依赖 Core ACK（`SourceReadCoordinator.cs:631-637`）：Core 不可用 → 撤销失败 → 该路径仍不可用（fail-closed 方向，正确）；**不得**在撤销失败后继续注册（否则又造出一条排在失效条目前面的健康条目 → 复用仍挑旧的）。
- 撤销会让绑定旧 `registry_id` 的 **C-17 journal 操作重试永久失败**（`HostOperationOrchestrator.cs:42-71` 的状态前置 + `:112-133` 按旧 id `Authorize`）；今天 App 对 `source_relink/repoint/resync` 也是 **0 调用**（全仓 App 侧无引用），所以现实影响面小，但必须登记（§8 R5）。

## 3. Q2 最小方案

### 3.1 逐项取舍

| 选项 | 事实依据 | 取舍 |
|---|---|---|
| **(a1) Host 进程内可用性投影**（`SourceAccessRegistry.ListWithAvailability()` 或 `SourceScanStatus` 扩展） | `List` 只返回持久条目（`:60`），可用性是 `Authorize` 里**派生**的（`:131-139`）；`SourceScanStatus` 明示这是「进程内唯一可观测面，从不是 wire/DTO/DB 行」（`SourceScanStatus.cs:4-7`） | **Out（另卡）**。零契约，但会把 B1 从「Host 零改动」变成改安全文件；且 App 没有承载它的 UI（无扫描状态面）。属 A 卡 D-6 的后续，逻辑上应先有 UI 需求。 |
| **(a2) wire 可用性投影**（`source_list_roots` 加字段） | 响应形状 `{entries:[{registry_id,locator,roots[],generation,created_at,last_used_at,revoked}]}`（C-16 `:30`）；改它 = 改冻结条款 | **Out（B2，需 1 pin）**。仅当出现「多根管理界面」时才有价值（要按条目展示健康并逐条处置）。今天 App 只能按**失败路径**学到一个根的可用性，够用。 |
| **(b) C-16 v1.5 新 host-control 只读枚举/可用性命令** | 现有 `source_list_roots` 已提供全部既有字段；`source_list_scan_targets` 是 Core 侧只读枚举（C-17 `:228`），与「Host 根健康」不是一回事 | **否决**。同一事实的第二条读面 = 面扩张 + 双源真相；与 C-17 `:279` 的 fail-closed 口径和 A 卡「零新命令」先例冲突。若未来真要做「零交互自动恢复」，那是 **L-S4-B** 的写路径问题（需新命令 + 新能力），**不是** B1。 |
| **(c) App 分流 + 显式恢复入口** | §2 的全部事实；`ISourceImportController` 不在 C-07 生成清单内（`tools/generate_api_inventory.py:26-29` 只解析 `IHostController.cs`/`RunContracts.cs` 的 3 个接口） | **In（B1 核心）**。零契约、Host 零改动、可判别、可 E2E。 |
| **(d) 其他：撤销后条目清理 / `.corrupt-*` 上限 / `quarantine_path` 脱敏** | 撤销条目永远留在文件里（`:100-110` 只置位）；A 卡 C 项未做；`Reset` 把 `quarantine_path`（绝对路径）作为响应字段返回（`:626`）而 C-16 §7.3 要求「绝对路径…receipt/UI/错误/日志不出现」（`:201`） | (d) **Out，登记 limitation**；`quarantine_path` **不得进 UI/日志**（B1 硬约束，§4 红线 4）。契约面自相矛盾留给 B2 的 UNFREEZE 一并澄清。 |

### 3.2 契约 / UNFREEZE 判定（明确到份数与 pins）

| 契约 | B1（推荐先释放） | B2（可选，另卡） |
|---|---|---|
| **C-16 v1.4**（pin `ad25fb3c89bb`） | **零改动**：只用 §1 既有四个命令（`:29-32`）与 §6 既有码（`:170-193`，零新码） | **1 pin**（v1.5）：§1 `source_list_roots` 响应 additive 字段（如需）＋（如与 L-S4-B 同批）§0 能力 + §2.x 新命令；一次 UNFREEZE 载体、一次 byte-level 复核、一次 pin 重算 |
| **C-15 v1.5**（pin `f9e376a0ed4c`） | **零改动**：B1 正是执行 `:314`「根级恢复由显式用户操作完成，不得自动」；不碰 `:310-315` 状态机 | 零改动（若只做投影）；若把「重授权」定义为新的持久状态则必须回头改 C-15 → **不建议** |
| **C-17 v1.1**（pin `aefa0fa5b17e`） | **零改动**：`:279`（file-root 缺失/替换 fail-closed、S-1②）与 `:276`（「授权撤销/Registry 丢失只诊断，不凭旧快照自动 apply」）均被 B1 遵守 | 零改动 |
| **C-07 API inventory**（pin `3fdb44e49afe`） | **零改动**：新成员只加在 `ISourceImportController`（`SourceImportModels.cs:23`），生成器不解析该接口 | 零改动 |
| **C-06 / C-01b / C-14 / M2-C1** | 零改动 | 零改动 |

**结论：B1 是「0/18 pins」的 App-only 卡；B2 是「1/18 pins」的契约卡。** 占位卡 approval 句把两者混成一句「需 C-16 v1.5」，会让 B1 被误判为需要 UNFREEZE 流程——这是本 Review 建议修正卡面的主要原因。

### 3.3 B1 的形状（供 DSH 冻结参考）

一次显式用户动作 = 「先用只读 `source_list_roots` 探一次 → 按 typed 码分流 → 撤销该路径全部非撤销条目 → 用**条目已登记的 root 字符串**重新 `source_register_root` → 重跑预览」。

- 分流规则：探测抛 `SOURCE_REGISTRY_UNAVAILABLE` → **文件级**，只提供「重置源授权存储」（二次确认 + 全量丢弃披露）；探测成功 + 铸造失败 → **根级**，只提供「重新授权此来源」；探测抛 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY` 等 → **不提供任何恢复动作**，只显示该码（否则会把能力缺失误判成损坏）。
- 不新增任何命令/字段/能力/错误码；不新增 App 侧 `File.Exists` 之类的 OS 预判（存在性交给 Host 的 typed 判定：`Register`→`SourceSecurity.Identity` 失败即 `SOURCE_ACCESS_DENIED`，`SourceSecurity.cs:113-119`）。
- 文案层只做展示细化（`SourceImportModels.cs:519` 的「源授权存储不可用」对「单根失效」有误导性），**不得新增码**；且只显示叶子名，不显示绝对路径（沿用 `ImportDockViewModel.cs:168-169` 的既有口径）。

## 4. Q3 红线（逐条可判别）

| # | 红线 | 现状锚点（不得放宽） | B1 的保持方式 | 判别性测试（去掉修复即红） |
|---|---|---|---|---|
| **R-1** | **不得自动重新授权** | `Register` 只在显式命令下追加（`:34-52`）；A 卡 AC-L4 已证无自动路径 | 恢复只在用户点击后执行；错误处理分支**禁止**调用 revoke/register/reset；禁止把 typed 失败改写成自动重注册 | VM 测试：预览失败后 `revoke/register/reset` 计数 = 0；把恢复接到错误分支 → 计数 > 0 → RED。**另加**：`FindOrRegisterRootAsync` 不得新增「失败就换下一候选并注册」的回退（那等于自动重授权）→ 注入 stale 条目 + 失败 → 注册计数 0 |
| **R-2** | **不得自动重建 identity** | `VerifyRootIdentity` 只读、不写回、失败零 `Save`（`:131-139`、A 卡 AC-L4） | B1 **完全不碰** `SourceAccessRegistry.cs`（Host 零改动）；重授权 = 新条目（新 `registry_id`），旧条目保持原字节（只多 `revoked_at`/generation+1） | Host 层：恢复动作后旧条目仍存在、`Roots[].VolumeSerial/FileId` 逐字节不变；把新身份写回旧条目 → RED |
| **R-3** | **撤销后不得自动放行** | `Authorize` 见 `RevokedAt` 即 `SOURCE_GRANT_REVOKED`（`:67`）；选择器跳过 revoked（`SourceImportModels.cs:771`）；Core 侧同一 push 抬升 generation floor（`source_read_refs.py:242-251`） | 撤销与再注册是**同一次用户动作里的两步**，且顺序固定（先撤后注）；撤销失败即中止，不得继续注册 | 撤销后对旧 `(registry_id,generation)` 铸造 → `SOURCE_GRANT_REVOKED`；篡改顺序（先注后撤）→ 重导入仍失败 → RED |
| **R-4** | **不得扩大授权面** | C-16 §1 四个命令形状冻结（`:29-32`）；§6 零新码（`:170-193`）；`HostRuntime.cs:926` 写门不变 | 不新增命令/能力/字段/错误码；重授权**只接受**条目已登记的 root（接口**不得**出现任意路径参数）；`Reset` 的 `quarantine_path` 不入 UI/日志（`HostCommandRegistry` 命令数不变） | 接口出现 `string path` 入参 → RED；`HostCommandRegistry.All.Count` 变化 → RED；UI/日志出现绝对路径 → RED；`quarantine_path` 渲染 → RED |

**为什么 R-1 是最高风险**：本卡最诱人的「一行修复」是把 `FindOrRegisterRootAsync` 改成「mint 失败就重新注册」——那在语义上正好是**自动重新授权**（用户只选了文件，没有被披露「根的物理身份已变」）。本 Review 明确**否决**该捷径，并在 AC 里把它写成判别项。

## 5. Q4 拆卡与范围（推荐冻结稿）

### 5.1 拆卡建议

| 卡 | 内容 | 契约 | 建议 |
|---|---|---|---|
| **B1（= 本卡，收窄）** | App 显式恢复入口：分流（`source_list_roots` 探针 + typed 码）+ 「重新授权此来源」（撤销全部同路径非撤销条目 → 按登记 root 再注册 → 重跑预览）+ 「重置源授权存储」（二次确认 + 全量丢弃披露）+ 文案/脱敏 + 测试/证据 | **零契约（0/18 pins）**，Host/Core/C-07 零字节 | **本轮释放** |
| **B2（另卡，暂名 `…-ROOTS-AVAILABILITY-1`）** | `source_list_roots` 可用性投影（C-16 §1 additive）+ 多根管理面（逐条健康/撤销/重授权）；如需与 L-S4-B 同批，一个 v1.5 载体承载两处 additive | **C-16 v1.5，1/18 pins** | **暂缓**（无 UI 需求；先有 roots 界面再谈投影） |
| **B3（可选）** | Host 进程内扫描侧可用性投影（A 卡 D-6 遗留） | 零契约 | 随扫描状态 UI 一起做，独立成卡 |

**不建议把三者合并**：合并会把一张「App 接线」卡变成「契约 + Host 安全文件 + Core + UI」四面改动，且 UNFREEZE 会挡住 B1 的即时交付。

### 5.2 recommended In / Out（B1）

**In（写域，文件级）**

1. `apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs` —— `ISourceImportController` 增加恢复面（探测/重授权/重置）；展示文案细化（零新码）。
2. `apps/desktop-avalonia/src/NewManga.App/Services/SourceRecoveryModels.cs` —— **新增文件**（恢复编排 + 结果模型 + 分流判定），避免把 878 行文件继续撑大；需显式 allowlist。
3. `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` —— 实现新成员，复用既有 `SourceImportCoordinator`/`HostCommandDispatcher` 路径。
4. `apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs` —— 编译义务（`NullHostController.cs:12` 实现该接口）。
5. `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs` —— 显式命令 + 状态 + 披露文案。
6. `apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml` —— 错误区两个显式动作 + 确认；无路径输入。
7. 测试：`apps/desktop-avalonia/tests/NewManga.App.Tests/SourceRecoveryUiTests.cs`（**新增**，VM 级 + 计数器判别）、`apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs`（接口实现义务）、`apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRecoveryIpcTests.cs`（**新增**，gated 真实 IPC 闭环）。
8. `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`、本卡、`doc/reviews/…-*.md`、`doc/handoffs/…-*.md`。

**Out（明确不写）**

- `apps/desktop-avalonia/src/NewManga.Host/**`（**预期零改动**；若实施中确实需要改，停手并走 scope 修订）、`apps/desktop-avalonia/src/NewManga.CoreClient/**`。
- `doc/plan/**`（C-16/C-15/C-17/C-07 一律零字节）、`src/**`（Core/Python）、schema/迁移/依赖、`tools/generate_api_inventory.py`。
- 自动恢复/自动重授权/自动重注册；`FindOrRegisterRootAsync` 的「失败换下一个候选」回退；任意路径输入；新命令/能力/错误码；`quarantine_path` 展示。
- 扫描状态 UI、roots 管理界面、`.corrupt-*` 治理、撤销条目清理；真实用户数据/AppData/回收站；push。

**allowed_paths（建议冻结稿，可直接粘进卡面）**

```yaml
allowed_paths:
  - doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md
  - doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceRecoveryModels.cs   # 新增
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SourceRecoveryUiTests.cs    # 新增
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRecoveryIpcTests.cs  # 新增（gated）
```

（若 DSH 决定 B1 不改 `ISourceImportController` 而走其他既有端口，可删去 `NullHostController.cs`/`FakeHostController.cs` 两行；但**不得**把 `IHostController`/`IHostController.cs` 加入写域。）

### 5.3 AC 草案（v3 口径：可判别 / fail-closed / 零漂移 / 门禁）

> 建议稿，**未冻结**；编号与措辞待 DSH 定稿。

| ID | AC（草案） | 判别性（撤销修复即红） |
|---|---|---|
| **AC-LSB-1 入口仅显式** | 导入预览以 `SOURCE_REGISTRY_UNAVAILABLE` 失败时，VM 只暴露「重新授权此来源」/「重置源授权存储」两个显式动作；未点击前 `source_revoke_root`/`source_register_root`/`source_reset_registry` 调用计数均为 **0**（FakeHostController 计数） | 把恢复动作挂进错误处理自动执行 → 计数 > 0 → RED |
| **AC-LSB-2 分流正确** | 恢复入口先做**只读** `source_list_roots` 探针：探测抛 `SOURCE_REGISTRY_UNAVAILABLE` → 只给「重置」；探测成功 + 铸造失败 → 只给「重授权」；探测抛其它码 → **不给任何恢复动作**，只显示该码 | 把 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY` 当文件级（提供重置）→ RED；探测抛错仍给重授权 → RED |
| **AC-LSB-3 撤销→注册顺序与幂等** | 同一路径存在 **2 条** stale 非撤销条目时两条都被撤销（生成 +1、`revoked_at` 非空），随后**只**新增 1 条非撤销条目；重复执行不产生重复条目（幂等） | 先注册后撤销 → 重导入仍命中失效条目 → RED；只撤销首条 → RED |
| **AC-LSB-4 部分失败 fail-closed** | 撤销成功但注册失败（路径已不存在 → `SOURCE_ACCESS_DENIED`）→ 明确显示「已撤销、未重新授权」+ typed 码；**不得**显示成功、不得隐式回滚成「未撤销」的样子（撤销是不可回退的持久事实）；重复点击可重试 | 把注册失败吞掉/显示成功 → RED；失败后自动回滚 `revoked_at` → RED（等于撤销可被撤回） |
| **AC-LSB-5 不自动重授权（安全核心）** | 铸造失败后**不**自动注册/不自动换候选；`FindOrRegisterRootAsync` 的复用选择器语义不变（仍取首个非 revoked 匹配条目） | 新增「失败即换下一候选并注册」回退 → RED（这正是红线 R-1） |
| **AC-LSB-6 授权面不扩大** | 重授权只使用条目已登记的 `roots[0]` 字符串；`ISourceImportController` 的恢复成员**无**任意路径入参；`HostCommandRegistry.All` 数量不变；无新命令/能力/错误码。建议照 `TrashUiTests.cs:415-419` 的「接口分离守卫」先例，断言恢复成员**不在** `IHostController` 上（保 C-07 pin） | 接口出现路径入参 → RED；命令数变化 → RED |
| **AC-LSB-7 脱敏** | 恢复相关文案/通知/日志只含叶子名、typed 码、计数；**不含绝对路径**、不含 `quarantine_path`；gated IPC 用例断言 wire/stderr 中 fixture 根路径 0 命中 | 注入路径断言 → RED；渲染 `quarantine_path` → RED |
| **AC-LSB-8 零漂移/门禁** | `git diff` 对 `apps/desktop-avalonia/src/NewManga.Host/**`、`NewManga.CoreClient/**`、`doc/plan/**`、`src/**` 全为空；`tools/generate_api_inventory.py --check` PASS；`verify_pins.ps1` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；全量 pytest/.NET 不降（基线以最近 closeout **3317/10**、**1570/0/92** 为准） | 任一契约/Host 字节变化 → RED；inventory `--check` FAIL → RED |
| **AC-LSB-9 闭环证据（gated 真实 IPC，1 条）** | 注册→同路径替换→预览 typed 失败→显式重授权→再预览成功→重新导入后 `source_locations.registry_id/generation` 已原地刷新（L-S4-A）→ `source_list_scan_targets` 重新返回该 source 的新代次 | 跳过重授权直接重导入 → 仍 typed 失败 → RED；撤销后 `source_locations` 仍指向旧 registry_id → RED |
| **AC-LSB-10 边界/不夸大** | 只承诺 **file-source 同路径恢复**；folder 变体受 L-S4-2 限制、重定位（换路径）走「重新导入成新源」；`L-S4-1`（零交互恢复枚举）仍开放；不得写「零交互自愈/根级问题全解」 | 卡面/Handoff 出现「自动恢复」承诺 → RED |

### 5.4 其它冻结前置

- `suggested_owner: codex` 与 A/L-S4 记录的「Codex 不可用（product limit）」矛盾；且 B1 有 UI 面（AGENTS.md 规定 ZCode 主责 UI 设计/实现）→ 由 DSH 重新指派或按「服务逻辑 / UI」拆分。
- 本卡 `depends_on` 已含 L-S4 A（done）与 A 卡（done），正确；B1 另外**强依赖 L-S4-A 的刷新**用于闭环（AC-LSB-9），卡面应写明。

## 6. Q5 测试/证据与门禁成本

### 6.1 三层可行性与既有骨架

| 层 | 骨架（path:line） | B1 需要新增 |
|---|---|---|
| **VM 级（零 Core、毫秒级）** | `FakeHostController` 已实现 `ISourceImportController`（`FakeHostController.cs:17`、`:707`），并有 `Fea11ScanRefreshVmTests` 的「计数器 + 脚本化结果」范式（同文件 `:1896-1930`） | 新文件 `SourceRecoveryUiTests.cs`：AC-LSB-1/2/3/4/5/7 的计数与文案断言 |
| **Host 组件级（真实 registry + 真实 dispatcher，无 Core 或不需 Core）** | `SourceRegistryResilienceTests` 的 fixture 范式（`:44-70`、`:99-120`）；`Fea09UiImportIpcTests` 用**生产** `SourceImportCoordinator` + 真实 Host-local 路由（`:78-123`） | 可选：`source_list_roots`/`source_register_root` 分支可无 Core 覆盖；**`source_revoke_root` 必须有一个可用核心**（它要 Core ACK，`SourceReadCoordinator.cs:631-637`），故这一步只能进 gated IPC |
| **真实 IPC（gated，分钟级）** | `SourceRegistryResilienceTests.cs:343-399`（`NEWMANGA_FEA11_IPC=1`，真实 Python Core + `coordinator.InvokeAsync`）；`Fea11RunGrantIpcTests.cs:155-171`（真实 IPC 上 `source_revoke_root` 已被跑过，含撤销后 typed 拒绝） | 新增 `SourceRecoveryIpcTests.cs`：AC-LSB-9 的 6 步闭环 + wire/stderr 路径 0 命中 + 隔离 receipt/日志 |

**可行性结论**：B1 **完全可以**做到「VM 级判别 + 1 条 gated 真实 IPC 闭环」。撤销这一步无法用纯单测证明（需要 Core ACK），这是**既有事实**而非 B1 的缺陷；模板现成（上面两条用例），成本可控。

### 6.2 门禁成本 / flaky

- 全量 `.NET`：基线 **1570/0/92**（`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/full-dotnet.log` 各程序集汇总：21+38+253+117+31+223+167+720 = **1570** passed、跳过 0+0+0+0+0+61+24+7 = **92**；同批 L-S4 记录同值），其中 `NewManga.App.Tests.dll` 720 passed / 7 skipped / 3m5s。已知 flaky：`FluentResidual2VisualEvidenceTests`（A/L-S4 均记录过隔离复跑 1 passed）→ AC 要求「原样记录 + 隔离复跑」，**不许重跑到绿**。
- 全量 `pytest`：基线 **3317/10**（A 卡 `logs/full-pytest.log`），B1 预期零 Python 改动，仍应跑一次以证零漂移。
- `pins`/`check`/`API inventory`：秒级；B1 预期三者全绿且 pin 值不变。
- 写入卫生：新 IPC 用例的 fixture 必须落在 `.workspace/FEA-11-L-S1-B-RECOVERY-REAUTH-1/`（A 卡先例 `:347-349`），**不得**再写 `verification/FEA-09/native-registry/**`。

## 7. Q6 优先级与待 DSH 裁决

### 7.1 与其它候选的比较

| 候选 | 用户影响 | 成本/风险 | 契约 | 结论 |
|---|---|---|---|---|
| **B1（本卡收窄）** | **中高**：被替换根的**同路径重导入永久失败**，且产品内无任何入口 | **低**：Host 零改动、App-only、1 个安全面为零的接线卡 | **0 pin** | **建议先做**（当前队列里唯一「用户可见死路 + 成本最低」的一项） |
| **L-S4-B**（零交互自动恢复枚举） | 中：监控静默丢失（无写路径介入时不自动恢复） | 中高：新 host-control 命令 + 新能力 + Core 写路径，且改「谁何时可写 location auth」 | **1 pin（C-16 v1.5）** | 次之；与 B2 合批 UNFREEZE 更省 |
| **2C 长 Run 续期** | 高（功能缺口，非回归） | 高：新命令 + 能力 + Core + 跨分片 | 可能 1 pin | 次之 |
| **L-R11 gate 统一** | 低（语义一致性） | 中（跨读面） | 0 | 排后 |
| **C-04b 文档 residual** | 无运行时影响 | 低 | 0 | 可穿插 |
| **SCAN-RH（RH-1…RH-5）** | 低（噪声/证据强度） | 低-中 | 0 | 排后 |
| **UI P3** | 视觉 | 低 | 0 | 排后 |

### 7.2 需 DSH 裁决的问题（含推荐）

| # | 问题 | 推荐 |
|---|---|---|
| **D-1** | 是否按 §5.1 拆成 B1（零契约）/ B2（1 pin）/ B3？本轮只释放 B1？ | **是**；B2 暂缓（无 roots 界面），B3 随扫描状态 UI |
| **D-2** | 是否修正占位卡 `approval` 句（现写「需 C-16 v1.5」）？ | **必须修正**为「B1 零契约（0/18 pins）；若纳入可用性投影/自动恢复枚举则为 C-16 v1.5（1/18 pins），另卡」。否则 B1 会被按 UNFREEZE 流程卡住 |
| **D-3** | **C-16 版本号分配**：本卡（可用性投影）与 L-S4-B（新命令+能力）都自称 v1.5 | **二选一**：①本窗口不做 B2，v1.5 留给 L-S4-B；②两者同批批准时**一个 v1.5 载体**同时承载两处 additive（一次复核 + 一次 pin 重算，最省）。禁止两张卡各自改同一份文件 |
| **D-4** | 是否要求现在做 `source_list_roots` 可用性投影？ | **不要求**。以 typed 失败驱动的一次性恢复已满足用户目标；投影只服务「多根健康面板」，该面板不存在 |
| **D-5** | `suggested_owner` | Codex 不可用 → **ZCode**（UI 面），或拆「App 服务逻辑 / UI」两段分派；卡面同步改 |
| **D-6** | 撤销会让绑定旧 `registry_id` 的 C-17 journal 操作重试永久失败（`HostOperationOrchestrator.cs:112-133`） | **登记 limitation**，B1 不处理（App 今天 0 调用 relink/repoint/resync）；如未来 App 接这些写面，必须同批给出 journal 处置 |
| **D-7** | `source_reset_registry` 响应带 `quarantine_path`（绝对路径，`SourceReadCoordinator.cs:626`）与 C-16 §7.3（`:201`）冲突 | B1 **不展示**该字段（硬约束）；若未来要展示，随 D-3 的 UNFREEZE 一并澄清（同一 pin） |
| **D-8** | 确认强度 | 重授权 = 一次显式确认（含「将授权该路径当前内容」披露）；重置 = **二次确认 + 全量丢弃披露**；撤销失败即中止 |
| **D-9** | 是否要求 1 条 gated 真实 IPC 闭环（AC-LSB-9） | **要求**（模板现成；撤销路径必须有 Core ACK 才能证） |
| **D-10** | 测试基线口径 | 冻结前由 Lead 修正 `STATUS.md:20`（3249/10、1527/0/86 → **3317/10、1570/0/92**），否则 AC-LSB-8 无法引用正确基线 |

## 8. 风险

| # | 风险 | 说明与缓解 |
|---|---|---|
| R1 | **把「修复」做成自动重授权**（最高） | 最诱人的捷径是「铸造失败就重注册」；那会让用户在不知情时把被替换的根重新授权。缓解：AC-LSB-5 判别 + 代码评审硬点（`FindOrRegisterRootAsync` 语义不变） |
| R2 | **重置被误用成日常按钮** | `Reset` 丢弃**全部**授权（`SourceAccessRegistry.cs:112-120`），随后所有源扫描失效。缓解：只在「`source_list_roots` 本身 typed 不可用」时提供；二次确认 + 全量披露；文案区分「该来源」与「全部来源」 |
| R3 | **部分失败留下中间态** | 撤销成功后注册失败 → 该路径既无授权也无恢复入口（但**方向是 fail-closed**）。缓解：AC-LSB-4 明确展示 + 可重试；不得伪装成功 |
| R4 | **文案/证据夸大** | 不得写「零交互自愈」「根级问题全解」「恢复已自动可用」；L-S4-1/L-S4-2 保留；`SOURCE_REGISTRY_UNAVAILABLE` 的码义仍是「该请求的根不可用或文件级损坏」（A 卡 limitation） |
| R5 | **撤销撕裂 journal** | 见 D-6；B1 只登记 |
| R6 | **folder 变体** | 根=文件夹时重授权授予「该文件夹当前内容」的读权；folder 身份键（L-S4-2）未修 → AC-LSB-10 明确限定 file-source 闭环 |
| R7 | **契约面自相矛盾被顺手「修掉」** | `quarantine_path` 与 §7.3 冲突必须在 UNFREEZE 里澄清，**不得**在 B1 里悄悄改响应或 UI |
| R8 | **并发写工作树** | 本次审查开始时工作树 clean；A/L-S4 期间均出现过并发 docs 写入。B1 冻结前须在 clean 且已提交的树上重跑门禁 |

## 9. 真实性声明

1. 本报告由**独立上下文 fresh subagent** 产出（session `7d2a572e-28bf-4c96-9c96-949678ca6339`，父会话 `session-5f1e719c-…`），**未参与** `FEA-11-L-S1-REGISTRY-RESILIENCE-1`（含其 PREREQ）、`FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 的实现、返修、scope review 或任何前轮审查；**未参与**本卡的立项/占位写入。全程**只读**。
2. 所有代码/契约事实均来自 `d6bc6b11b` 的仓库字节并逐条给出 `path:line`；未把卡面/Handoff 自述当作实现事实（凡引用卡面处均标注为「卡面」）。
3. **实测命令**（已跑）：`git rev-parse HEAD`、`git rev-parse --abbrev-ref HEAD`、`git status --porcelain=v1`、`git log --oneline`、`git show --stat d6bc6b11b`、`git merge-base --is-ancestor`、`pwsh tools/governance/verify_pins.ps1`（**PASS 18/18**）、`pwsh tools/governance/check.ps1 -TaskPath …`（**PASS，3 warnings，EXIT 0**）、以及大量只读 `read`/`grep`/`Select-String`。
4. **NOT_RUN**（原因已写明）：定向/全量 `dotnet test`、全量 `pytest`、`generate_api_inventory.py --check`、真实 IPC。本报告不对这些项目作 PASS 声明；B1 的门禁数字以最近 closeout 的证据日志为基线引用，未由本轮重跑。
5. **HEAD 差异披露**：任务书称 HEAD `1c4ad82a9`；实测 HEAD 为 `d6bc6b11b`（其子提交），唯一改动是 L-S4 r1 报告的并发披露段落（docs-only），`src/**`/`tests/**`/`apps/**`/`doc/plan/**` 零 diff，对本 Review 结论无影响。
6. **未改动**任何生产代码、测试、契约、冻结记录、Task 卡、STATUS/REBASELINE_PLAN/TASK_LEDGER 或 canonical evidence 字节；未执行 `git add`/`git commit`/`git push`。仓库内唯一新增字节是本报告。
7. 报告中的 In/Out、`allowed_paths`、AC 草案、UNFREEZE 判定与拆卡建议均为**建议**；scope 冻结、契约字节变更、Review Appointment 与 findings 处置属 DSH。
8. **不夸大**：本报告不写「恢复已可用」，只写「最小显式恢复在零契约下可实现」；不写「根级问题全解」；L-S4-1（零交互恢复枚举）、L-S4-2（folder 身份键）、A 卡 C 项（`.corrupt-*`）均保持开放。
