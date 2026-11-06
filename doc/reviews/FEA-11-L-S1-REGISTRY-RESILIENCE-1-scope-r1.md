---
task: FEA-11-L-S1-REGISTRY-RESILIENCE-1
title: Scope Review r1：SourceAccessRegistry 根级韧性（file-root 缺失/替换不再使整库不可读）
reviewer: fresh subagent（独立上下文；未参与实现；只读）
session: 976c9d16-a47d-47d8-922e-cdba24f092fa
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: d782c52a403d96c45f7097ffc0cb4bca37024aa1
verdict: READY-WITH-UNFREEZE
---

# Scope Review r1：FEA-11-L-S1-REGISTRY-RESILIENCE-1

> 审查对象：`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`（`proposed` 占位，scope 未冻结）。
> 审查口径：只读；事实以 `d782c52a4` 的仓库字节为准；未运行项一律 `NOT_RUN`。
> 本报告只提出 scope 建议与裁决输入，不冻结 scope、不改卡、不改契约。

## 0. 结论先行

**verdict：`READY-WITH-UNFREEZE`。**

1. **根因是契约写死的，不是纯实现意外**：`SourceAccessRegistry.Load()` 对**每条** `roots[]` 调 `SourceSecurity.Identity()` 并对 volume/fileId 做严格比对（`SourceAccessRegistry.cs:119-129`、`:126-127`），任一不合法即落入 `:132-138` → 复制 `.corrupt-*` 并抛 `SOURCE_REGISTRY_UNAVAILABLE`。这正是 **C-15 v1.1 §5 冻结状态机**的字面要求：「magic/version/长度/DPAPI/JSON/**roots identity 任一不合法** = 损坏：fail-closed……所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`」（`FEA-C15_SOURCE_STORAGE_DRAFT.md:312`，C-15 为 FROZEN v1.1，pin `d8c0a3bcfc21`）。**故本卡不是「零契约」卡**：要动粒度，必须 **UNFREEZE C-15 §5 一条（1 pin）**；C-16、C-17 可保持零字节改动（见 Q2）。
2. **fail-closed 是刻意的，「整库」粒度是契约继承下来的粗粒度**：写盘/解密/结构校验层面「整库判损坏」是正确的安全设计（文件被篡改时不能信任任何条目）；但把「某个 root 现在取不到身份/身份已变」并入同一个「文件损坏」判决，是 C-15 §5 与 FEA-09 scope r1 `:105`（「重启重验根身份」）共同造成的**粗粒度**，从未按条目重新审议。二者要分开评价，不能整句推翻。
3. **影响面比卡面写的更大**：不只扫描。生产引用导入**先**调 `source_list_roots`（`SourceImportModels.cs:761-763`），registry 不可读即抛错 → **任何新导入也被阻断**（`FindOrRegisterRootAsync` 在 `:790-792` 的 `source_register_root` 根本到不了）。同时 `source_register_root`/`source_revoke_root`/`source_reset_registry` 全部走同一 `Load()`（`SourceReadCoordinator.cs:618-644`）；C-17 apply/journal 面（`HostOperationOrchestrator.cs:112-133`）与 watcher（`SourceWatcher.cs:409-424`）也一并降级。**一个用户删/移一个引用源文件，等于全库源线不可用。**
4. **恢复路径今天不存在**：`source_reset_registry` 是 C-15 §5 指定的唯一恢复口（`:313`），但**全仓 App 侧 0 调用**（只有 `source_list_roots` 被 App 调用；`source_reset_registry`/`source_revoke_root` 仅 Host handler + 命令表登记：`HostCommandRegistry.cs:149,384,490`）。即：用户在产品内**没有任何**重授权/重定位/重置入口。这条必须与 L-S1 拆开，且必须在卡面登记为 limitation，否则「韧性」会被读成「已可恢复」。
5. **拆卡建议**：A（读取韧性，零 wire，需 C-15 UNFREEZE）＝本轮释放；B（恢复/重授权 UI，需 C-16 §1 增补 + App；且依赖 L-S4）＝另卡；C（`.corrupt-*` 无界复制治理）＝可选/登记。**不建议把 recovery 塞进 A**：那会把一张窄修复变成「契约 + Core + UI」三面改动。
6. **门禁前置**：`reviewed_head` 上 `check.ps1 -TaskPath` **FAIL**（TASK_LEDGER 陈旧：声明 527 Task/9 非终态，实际 528/10；审查结束时因另一会话并发新增 L-S4 卡，实际计数还会上升）。这是 L-S1 占位卡登记提交带入的漂移，**冻结前必须由 Lead 跑 `tools/governance/task_ledger.py --write` 修掉**，否则卡无法合规释放。

## 1. 只读基线表

| 项 | 值/命令 | 结果 |
|---|---|---|
| HEAD | `git rev-parse HEAD` | `d782c52a403d96c45f7097ffc0cb4bca37024aa1`（main，`2026-11-07 07:14:32 +0800`，docs(handoff)） |
| 工作树 | `git status --porcelain` | **审查开始时为空（clean）**；审查结束时出现 `?? doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（本报告）与 `?? doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`（**另一会话 07:16:23 并发新增的 `proposed` 卡，非本报告产物、本报告未读取其用于任何结论**）。`git diff --stat` 全程为空（零 tracked 改动） |
| 分支 | `git branch --show-current` | `main` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS（all 18）**；C15 `d8c0a3bcfc21`、C16 `ad25fb3c89bb`、C17 `aefa0fa5b17e` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` | **FAIL（2 errors / 3 warnings，EXIT 1）**：`TASK_LEDGER 已过期：声明 527 个 Task，实际 528 个`；`声明 9 个非终态 Task，实际 10 个`。warnings：10 个非终态 Task、STATUS 3123B/27 行达 80% 预算、PLAN 6975B/62 行达 80% 预算 |
| 台账字节 | `doc/TASK_LEDGER.md:9-12` | 自述 `task files 527 / terminal 517 / non-terminal 9`；本卡行见 `:45`（`proposed`）→ 头部计数与行数/文件数不一致 |
| 定向 Host 单测 | `dotnet test apps/desktop-avalonia/NewManga.sln --filter "FullyQualifiedName~SourceRegistryTests\|FullyQualifiedName~SourceScanSchedulerTests"` | **NOT_RUN**。原因：`SourceRegistryTests.EncryptedPersistenceGenerationCorruptionAndExplicitReset` 会把 fixture 写进 `verification/FEA-09/native-registry/<guid>/`（`SourceRegistryTests.cs:140-145`），运行会污染只读工作树并留下未跟踪文件；本次任务禁止除报告外的任何写入 |
| 全量 .NET / pytest / API inventory | — | **NOT_RUN**（只读 scope review；成本与写入理由同上） |
| 真机 IPC | — | **NOT_RUN** |

基线口径提醒：`STATUS.md:20` 记录的最新基线为 **pytest 3249/10、.NET 1527/0/86**（2026-11-06 RENDITION-1 closeout 实测），SCAN-2 卡面 `:124-125` 的 3212/10、1500/0/85 是更早的卡内口径；实现卡 AC 必须引用 STATUS 的当前基线，不得混用。

## 2. Q1 风险与安全口径

### 2.1 现状代码路径（实测字节）

1. **读入口（唯一）**：`SourceAccessRegistry.Load()`（`SourceAccessRegistry.cs:98-139`）——文件不存在＝合法空 Registry（`:100`，与 C-15 `:311` 一致）；存在则 `RejectReparseAncestors`（`:103`）→ 读字节 → magic/长度（`:105`）→ DPAPI 解密（`:108`）→ JSON（`:113`）→ 结构校验（`:116-118`）→ **逐条目逐根 identity 校验**（`:119-129`）：`root.Root` 必须等于自身 `Normalize` 结果且 `Readable`（`:125`），并 `SourceSecurity.Identity(root.Root)` 与持久 `VolumeSerial/FileId` **严格相等**（`:126-127`）。
2. **失败收敛**：`:132-138` 捕获除 OOM 外的一切异常 → `File.Copy(RegistryPath, RegistryPath + ".corrupt-<utc>", false)`（`:134`，尽力而为）→ `throw new SourceAccessException("SOURCE_REGISTRY_UNAVAILABLE")`（`:137`）。**根缺失/根被替换在这里与「文件被篡改」得到同一判决**。
3. **上游异常来源**：`SourceSecurity.RejectReparseAncestors` 对不存在的路径段直接 `SOURCE_ACCESS_DENIED`（`SourceSecurity.cs:95-98`）；`Identity(path)` 打开失败 → `SOURCE_ACCESS_DENIED`（`:113-118`）；handle 型 identity 对 reparse 属性 `0x400` → 拒绝（`:109`）。**这些都发生在 `Load` 的 try 内，被统一改写为 `SOURCE_REGISTRY_UNAVAILABLE`。**
4. **调用面**（全部经 `Locked()` → `Load()`，`:175-199`）：
   - `Register`（`:34-52`，`:36` Load → `:50` Save）：**新增根也被阻断**；
   - `List`（`:54`）：`source_list_roots`（`SourceReadCoordinator.cs:621-624`）、枚举器（`SourceScanScheduler.cs:2080`）、扫描核验（`:1566`）、解析器（`:1874`）、watcher（`SourceWatcher.cs:416`）、apply/journal（`HostOperationOrchestrator.cs:112`）；
   - `Authorize`（`:56-74`，`:58` Load）：grant 铸造（`SourceReadCoordinator.cs:400,403,467`）、apply 授权（`HostOperationOrchestrator.cs:132`）；
   - `Revoke`（`:76-86`，`:78` Load）：撤销也读不了；
   - `Reset`（`:88-96`）：**不 Load**（直接移动文件 + Save 空快照）——今天唯一能"逃出"的路径，代价是**丢弃全部授权条目**。
5. **影响面（用户可见）**：

| 流程 | 代码路径 | 现状（单根缺失/替换） |
|---|---|---|
| 新引用导入 | App `source_list_roots`（`SourceImportModels.cs:761-763`）→ 失败；`source_register_root`（`:790-792`）到不了 | **全阻断**（含与本根无关的新路径） |
| 冷启动扫描枚举 | `RefreshTargetsAsync`（`SourceScanScheduler.cs:689-795`）：枚举器 `List()` 抛错（`:2080` 无 try）→ `:746-749` 收成 `Unavailable(code)` → `RecordEnumerationLocked` | **0 新 target 合入**；已入内存的 target 也只会在核验处 continue 失败 |
| 单目标扫描 | `VerifyEnumeratedTarget`（`:1561-1576`）catch → BUSY 记 Skipped，其余一律 `Error("SOURCE_REGISTRY_UNAVAILABLE")`（`:1573-1575`） | 每个 target 各自 fail-closed（不发 `ScanSourceSync`，不发 missing） |
| 会话内注册目标扫描 | `ResolveRegistryEntry(path)`（`:1873-1874`）→ `List()` 抛 → 冒泡到 `ExecuteAsync` catch（`:1175-1178`）→ `FromCode` → `Error` | 同上（但走的是"抛异常"而非"typed 判定"两条不同路径） |
| Run 预授权 | `RunSourceAuthorizer` 对 `List()` 失败按 best-effort skip（`SourceRegistryTests.cs:298-318` 已固定该语义） | Run 命令仍 dispatch，但 0 grant → Core 侧后续读/绑定 typed 失败 |
| C-17 apply/journal | `HostOperationOrchestrator.cs:112` → 抛；HostRuntime 包装为 `CoreOperationException("SOURCE_REGISTRY_UNAVAILABLE")`（`HostRuntime.cs:963-965`） | plan/apply/ACK 全阻断 |
| watcher | `TryPlan` catch（`SourceWatcher.cs:418-424`）→ uncovered，退回周期扫描 | 不 arm，不崩溃（WATCH-1 已按 L-S1 口径实现） |
| 枚举状态投影 | `SourceScanEnumerationStatus`（`SourceScanScheduler.cs:1026-1033`）带 `last_enumeration_error_code` | App 只能看到"源授权存储不可用"（`SourceImportModels.cs:519`），无处置动作 |

6. **二次缺陷（同一根因的副作用）**：每次 `List()` 失败都会复制一份 `.corrupt-<utc>`（`:134`），而 `.corrupt-*` **全仓无清理/上限**（仅此 1 处写入引用）。单根缺失 → 每 tick × 每 target × 每命令各复制一份（文件上限 4MiB，`:105`）。这会把"误判为损坏"放大成磁盘增长与诊断噪音。

### 2.2 「单根不可用 → 整库不可读」是刻意还是粗粒度？

**两者都有，必须分开写**：

- **刻意（正确、不得放宽）**：文件级不可信（magic/长度/DPAPI/JSON/format_version/重复 registry_id/结构非法）→ 不信任任何条目、不创建空文件、不覆盖原文件、保留 `.corrupt-*` 原件（C-15 `:312`；`SourceAccessRegistry.cs:103-118,132-138`）。这是 fail-closed 安全设计。
- **粗粒度（应改）**：把「授权根的**当前物理身份**」并入同一个文件级判决。其来源是 FEA-09 时期的决策链：FEA-09 卡 `:110`（「重启重验根身份」）、FEA-09 scope r1 `:105`（同句）、C-15 `:312` 把 `roots identity` 写进"损坏"列表。**没有证据表明曾按「单条目不可用/其余条目可用」重新审议过**；SCAN-2 scope review `:375` 的 S-1 也把这一点列为待裁决项（选项①"缺失 root 视为 unreadable 而非 corrupt，窄修 Host Load，需独立安全复核"），SCAN-2 最终取选项②（`:436`）并把韧性留作另卡。所以：**现状是"契约继承下来的粗粒度 + 正确的 fail-closed 倾向"，不是"刻意的整库停摆"设计目标。**
- **不得据此推断**：本报告不认为 C-15 `:312` 当时写错；它是在"没有条目级状态机"的前提下最保守的写法。改它需要显式 UNFREEZE（Q2）。

### 2.3 放宽到条目级时必须保持的不变量（AC 必须逐条可判别）

| # | 不变量 | 现状锚点 | 保持方式 |
|---|---|---|---|
| I-1 | **缺失根 ≠ 无授权** | `Authorize` 的 containment 只认 `root.Readable && Contains`（`:67`），而 `Readable` 只在 `Register` 写 `true`（`:47`，全仓无置 false 的写点） | 缺失/身份不符的根**永远不能**授权任何路径；路径不得回退到"父目录/其他根/无根"放行 |
| I-2 | **不得自动重建 identity** | `Load` 只比对、从不回写（`:126-127`） | 校验失败**零持久化写**（除成功 `Authorize` 的 `last_used_at`）；不得把新 volume/fileId 写回、不得"修正"根路径 |
| I-3 | **不得自动重新授权** | `Register` 只在显式命令下追加（`:49-50`） | 条目级不可用不得触发重注册；恢复只能由用户显式动作（B 卡） |
| I-4 | **grant/扫描/授权 fail-closed 不放宽** | `Authorize` 的 revoked/generation/containment（`:61-69`）；扫描 `VerifyEnumeratedTarget`（`:1585-1632`） | 不可用条目在其所有消费面继续 typed 失败；不得"先扫后判"、不得降级为 best-effort 读取 |
| I-5 | **不得泄漏路径** | C-16 `:199-201`；SCAN-2 AC-S2-8 | 新错误/日志/状态**只允许** code + 计数 + registry_id；`.corrupt-*` 命名不得含路径 |
| I-6 | **文件级损坏仍然整库 fail-closed** | C-15 `:312`；`SourceAccessRegistry.cs:103-118,132-138` | 拆分不得把"文件不可信"降级为"条目 skip" |
| I-7 | **并发/锁语义不变** | `Locked()`（`:175-199`）：mutex→文件锁→action，BUSY 语义（`:185-187,190-191`） | 条目校验必须在**同一把锁内**、读盘之后进行；不得为探测根身份而先放锁再读 |
| I-8 | **重启仍重验根身份** | FEA-09 卡 `:110`；FEA-09 scope r1 `:105` | 首次使用该条目时重验（懒验）可接受；**不得**因拆分而取消重验 |
| I-9 | **持久化形状不变** | C-15 `:296-304`；`FormatVersion != 1` 即损坏（`SourceAccessRegistry.cs:116`） | 禁止 bump `format_version`、禁止新增持久字段（旧二进制读到新字段会整库判损坏，形成降级雷） |

## 3. Q2 最小可行方案

### 3.1 逐项评估

| 选项 | 评估 | 取舍 |
|---|---|---|
| **(a) 读取容错：坏条目投影为条目级 typed 错误，journal/其余条目可用** | **必须做，且是本卡唯一核心**。做法（最小）：①`Load` 只保留**文件级**校验（magic/长度/DPAPI/JSON/format/唯一 id/generation≥1/roots 非空且已 normalize/`Readable` 结构位），**移除**逐根 `Identity()` 探针；②新增仅在 `Locked()` 内、按条目调用的私有校验（探针失败时**只影响该条目**），接入 `Authorize`（对"请求路径所属根"验身份，失败 typed 且**零写**）；③`List()` 保持返回全部条目（无新字段）；④文件级损坏路径**一字不改**。<br>**关键约束**：`Authorize` 现在是唯一的 per-mint 授权闸（`:56-74`），而身份校验过去寄生在 `Load` 里——**如果只删不补，被替换的根会重新获得授权能力（安全回退）**。这是本卡最大的安全风险点，AC 必须判别。 | **In**。这是唯一能同时满足"I-1…I-9"且不碰 wire 的形状。 |
| **(b) 启动时把不可用根登记为 quarantined（不删除）** | **不建议按字面做**。理由：① `Readable` 是持久常量，registry 里**没有任何**条目级状态位（`:47` 全仓唯一写点），要"登记 quarantined"就得新增持久字段 → 撞 I-9（`format_version` 非 1 即损坏）与降级雷；② 「quarantine」一词在 C-15 `:313`/`Reset`（`:88-96`）已被占用为**整文件移动**语义，条目级复用会与既有 quarantine 目录/证据混淆；③ (a) 的"派生不可用"已等价于"保留条目、不删除、不重建"——**状态不需要持久化，只需要可推导**。<br>**建议**：不引入持久 quarantine；术语用「条目级不可用（derived，不持久化）」，把"quarantine"留给 Reset。若 DSH 坚持持久登记，则必须同时出 `format_version` 迁移/降级策略，成本远超本卡。 | **Out（并明确驳回按字面实现）**；以 (a) 的派生语义交付 (b) 的**用户意图**（不删除、可恢复）。 |
| **(c) 恢复路径（重新选择根/重定位）是否本卡做** | **不做**。事实支撑：① 产品内**没有**任何 registry 恢复入口（`source_reset_registry`/`source_revoke_root` 全仓 0 App 调用，只有 `HostCommandRegistry.cs:149,384,490` 登记与 `SourceReadCoordinator.cs:625-644` handler）；② 要做就得动 C-16 §1（`source_list_roots` 无可用性字段，App 无法区分可用条目 → `SourceImportModels.cs:782-786` 会**一直复用**那个已失效的条目，导致同路径导入持续失败）；③ 还要动 App（`SourceImportModels.cs`）+ 可能的 C-07 端口 + UI；④ 「撤销后 Core location auth 不更新」还压在 **L-S4** 死代码上（SCAN-2 `:132`）。四件事叠加，规模 ≥ 本卡 3 倍。<br>**但必须做两件事**：卡面**显式登记 limitation**（"被替换根在 B 卡前无法在产品内恢复"）；并保证 (a) 不使该 limitation 恶化（`source_revoke_root` 在 (a) 后**可用**，这是通向 B 的最小台阶）。 | **Out（另卡 B）**；本卡只保证"撤销/重置命令在 registry 部分不可用时仍可用"。 |
| **(d) 其他候选** | ① **不做**枚举期预探测根可用性（会改变 AC-S2-5 的 target 级 `Error` 判决，把 typed error 变成 `Skipped`，且把 verdict 来源从 executor 分裂成两处）；② **不做** `source_list_roots` 可用性投影（C-16 §1 增补，归 B）；③ **不做**错误码细化（见 3.2）；④ **可选**：`.corrupt-*` 复制上限（见 Q5-R3，建议登记不改）。 | ②③④ 明确 Out；①列为**实现红线**（不得为了"减少噪音"把 verdict 前移）。 |

### 3.2 契约 / UNFREEZE 判定（明确到份数与 pins）

| 契约 | 是否改动 | 判定 |
|---|---|---|
| **C-15 v1.1 §5（FROZEN，pin `d8c0a3bcfc21`）** | **必须改**（`FEA-C15_SOURCE_STORAGE_DRAFT.md:312` 一条状态机句：把「roots identity 不合法」从"文件损坏"移出，改为"条目级不可用（derived）；该条目授权/铸造/扫描核验 typed fail-closed；其余条目不因此整库不可用；文件级校验仍整库 fail-closed"；可选同句注明 `.corrupt-*` 仅用于文件级损坏） | **UNFREEZE 1 份 / 1 pin**（C15 重算；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-0?-C15.md` + 冻结记录 `FEA-CONTRACT-FROZEN-C15.md` 更新，Lead 所有） |
| **C-16 v1.4（pin `ad25fb3c89bb`）** | **不改**。§1 命令/响应字段（`:29-32`）、§6 错误码闭集（`:170-193`）全部原样复用；本方案**不新增**命令/字段/能力/错误码 | **零契约** |
| **C-17 v1.1（pin `aefa0fa5b17e`）** | **不改**。§5.1 `source_list_scan_targets`（`:228`）与 §5.3 的 S-1② 口径（`:279`，"生产 file-root 缺失/替换导致 `SOURCE_REGISTRY_UNAVAILABLE` 属 fail-closed"）在本方案下**依然成立**（受影响的 target 仍得到该 code） | **零契约** |
| C-06 / M2-C1 / ADJ-001 / C-07 / C-01b | 不改 | **零契约** |
| FEA-09 卡 `:110`（"重启重验根身份"） | 不编辑（终态证据）；由 C-15 UNFREEZE 载体**引用**为被取代的决策来源 | 记录即可 |

**为什么不能零契约**：C-15 `:312` 是**状态机字面**，把"root 现在取不到身份"判为文件损坏，并规定"所有 source 操作 `SOURCE_REGISTRY_UNAVAILABLE`"。任何条目级放宽都直接违背该句；仓里也没有第二条可读路径（`Load` 是唯一入口，`List`/`Authorize`/`Register`/`Revoke` 全经过它）。**不存在值得做的"零契约折中"**（例如"只跳过 `.corrupt-*` 复制"仍改变损坏分类，且不解决可用性）。

**错误码取舍（建议：零可观察漂移）**：C-16 §6 把 `SOURCE_REGISTRY_UNAVAILABLE` 定义为"Registry 不可读/不可写/损坏"（`:177`），把根/scope 校验失败定义为 `SOURCE_ACCESS_DENIED`（`:174`）；C-06 §2.3 失败行也写"identity 变化 → `SOURCE_ACCESS_DENIED`"（`FEA-C06_SOURCE_AUTH_DRAFT.md:44`）。即：**契约本身对"根失败该用哪个码"并不完全自洽**（实现统一给了 `SOURCE_REGISTRY_UNAVAILABLE`）。本卡**建议一律保持现状码**（扫描 target 级仍 `SOURCE_REGISTRY_UNAVAILABLE`，以保护 AC-S2-5/C-17 pin；mint 面仍是 `SOURCE_REGISTRY_UNAVAILABLE`），**零 wire 可观察变化**，并把"码义已从整库收窄为条目级"登记为 limitation；码词表细化（区分"整库损坏"与"单根不可用"）留给后续 additive 契约（若做，需 C-16 §6 + C-06 各 1 pin）。这条需 DSH 裁决（D-2）。

## 4. Q3 拆卡与范围

### 4.1 拆卡建议

| 卡 | 内容 | 依赖/契约 | 建议 |
|---|---|---|---|
| **A（= 本卡）** | registry 读取韧性：文件级/条目级分离；per-mint 条目级身份校验；其余条目与 journal/枚举可用；零 wire | C-15 §5 UNFREEZE（1 pin） | **本轮释放** |
| **B**（新卡，暂名 `FEA-11-L-S1-RECOVERY-1`） | 恢复/重授权：`source_list_roots` 可用性投影（C-16 §1 增补）+ App 分流（不复用失效条目）+ 撤销/重置/重注册入口（`source_revoke_root`/`source_reset_registry` 接线）+ **L-S4** `refresh_source_location_auth` | C-16 §1（+可能的 C-07）UNFREEZE；L-S4 | **另卡，A 之后** |
| **C**（可选） | `.corrupt-*` 复制上限/去重（现每失败一次复制一份，`:134`，无清理） | 若做，可与 A 的 C-15 载体同批授权 | 建议**登记 limitation，不本轮做** |

**不拆的代价**：如果 A 单独交付，用户会遇到"被替换的根在同路径永远导入失败"（App 复用失效条目，`SourceImportModels.cs:782-786`）——这是**可接受但必须写明**的中间态；如果 A 与 B 合并，则卡从"1 文件 + 测试"膨胀到"契约 + App + UI + Core 死代码"，与 `proposed` 卡的原始意图（窄修复）不符。

### 4.2 本卡 recommended In / Out

**In（写域，文件级）**

1. `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs` —— 拆分 `Load`（文件级 vs 条目级）；新增条目级身份校验并接入 `Authorize`；`List`/`Register`/`Revoke`/`Reset` 的**可观察行为**仅按 AC 变化；持久化形状**零变化**。
2. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs` —— 扩展隔离 multi-entry 矩阵。
3. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs` —— 把现有"单条目 cold-start 缺失/替换"用例改成"混合 registry"判别（保留其原语义断言）。
4. `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryResilienceTests.cs`（**新增文件**，需显式 allowlist）。
5. `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/**`、`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`、`doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-*.md`、`doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-*.md`。

**Out（明确不写）**

- `apps/desktop-avalonia/src/NewManga.Host/Sources/{SourceScanScheduler,SourceWatcher,SourceReadCoordinator,HostRuntime,HostOperationOrchestrator,SourceOperationCoordinator}.cs`：**预期零改动**。若实施中发现必须改，**停手并申请 scope 修订**，不得边做边扩。
- `apps/desktop-avalonia/src/NewManga.App/**`（含 `SourceImportModels.cs`）、`NewManga.CoreClient/**`、Python Core、C-16/C-17/C-06 字节、`format_version`/schema/迁移/依赖、UI/通知、真实用户数据/AppData/回收站、push。
- 枚举期预探测根可用性；`.corrupt-*` 策略变更；错误码新增/重映射；持久 quarantine 字段。

### 4.3 AC 草案（v3 口径：fail-closed / 零放宽 / 判别性 / 零漂移 / 门禁）

> 以下为 scope review 建议稿，**未冻结**；编号与措辞待 DSH 定稿。

| ID | AC（草案） | 判别性（撤销修复即红） |
|---|---|---|
| **AC-LS1-1 文件级损坏仍整库 fail-closed（零放宽）** | 篡改 magic/长度/DPAPI/JSON/`format_version`/重复 `registry_id`/非法 generation/roots 结构 任一 → `List()`/`Authorize()`/`Register()` 均抛 `SOURCE_REGISTRY_UNAVAILABLE`；不创建空文件、不覆盖原字节；生成 `.corrupt-*` 副本 | 现有 `SourceRegistryTests.cs:136-164` 保持绿；若把文件级校验也改为"跳过"，该用例与新增负例转红 |
| **AC-LS1-2 单根缺失不再整库不可读** | 双条目 registry（A 正常、B 的根文件删除）→ `List()` 返回 2 条（顺序/字段不变）；`source_list_roots` 成功；A 的 `Authorize`+铸造成功且 `last_used_at` 持久化；**B 读取 registry 之外的任何命令均不受影响**（`source_register_root` 新根 C 成功） | 还原"整库判损坏"→ `List()` 抛错 → 红。必须断言"B 仍存在且未被删除/改写" |
| **AC-LS1-3 缺失根不得变成"无授权放行"** | B 名下路径的 `Authorize` → typed 失败；同时（负例）未注册根下的路径、父目录、`..` 越界、reparse 祖先 → 仍 `SOURCE_ACCESS_DENIED`；**不得**因根缺失而回退到"该条目任意路径可读" | 把 containment 放宽为"根缺失则跳过校验"→ 负例红 |
| **AC-LS1-4 根被替换：条目级 fail-closed 且零自动重建** | 同路径删除+重建（volume/fileId 变化）→ B 的 `Authorize` typed 失败；**registry 文件字节不变**（除其他条目成功 `last_used_at`）；不得写入新 volume/fileId、不得改根路径；A 不受影响 | 若把探针失败当"跳过并继续授权"→ 红；若自动回写身份→ 字节断言红 |
| **AC-LS1-5 扫描 blast radius 收敛（保住 AC-S2-5）** | 混合枚举（A、B 两 target）：A 产出 1 个 `ScanSourceSync` 帧（`scope` 按 `ProjectIds.Count` 选 current/all）；B 得到 target 级 `Error("SOURCE_REGISTRY_UNAVAILABLE")`、**0 帧**、**0 missing observation**；B 不导致 A 的 target 被丢弃/跳过 | 还原整库→ A 也失败 → 红 |
| **AC-LS1-6 枚举与状态投影不被单根毒化** | 混合同上：`RefreshTargetsAsync` 返回 `Ok=true`、`Enumeration.last_result=ok`、`targets` 含 A 与 B（B 由 executor 判）；不再整轮 `Unavailable` | 还原→ 枚举 `Unavailable` 且 0 新 target → 红 |
| **AC-LS1-7 并发/锁语义与写序不变** | 锁冲突仍 `SOURCE_REGISTRY_BUSY`（retryable）；`Authorize` 失败**零写**；成功才写 `last_used_at`；条目探针在持锁内、读盘后执行（可用探针计数或注入时钟断言） | 把探针放到锁外→ 并发用例/计数断言红 |
| **AC-LS1-8 零 wire / 零持久化漂移** | `git diff` 对 `doc/plan/FEA-C16*`、`FEA-C17*`、`FEA-C06*`、`src/infrastructure/sqlite/schema.py` 为空；无新命令/字段/能力/错误码；`registry.v1.dat` 的 `format_version` 仍 1，字段集合不变（decrypt 后结构断言）；错误码文本不变 | 任一 wire/格式改动 → 红 |
| **AC-LS1-9 脱敏** | 新增错误/日志/状态无绝对路径、无 entry 名、无 secret/grant 原文；`.corrupt-*` 名字不含路径 | 注入路径断言 → 红 |
| **AC-LS1-10 门禁** | 全量 .NET 不降（基线 **1527/0/86**，`STATUS.md:20`）；定向 Host 测试 PASS；`check.ps1 -TaskPath` PASS（**先修台账**）；`verify_pins.ps1` 18/18（C15 新 pin）；`python tools/generate_api_inventory.py --check` PASS（无 wire 变更应无 diff）；scope diff 仅 allowed_paths；首跑 flaky 逐条记录并隔离复跑 | — |

## 5. Q4 测试与证据

### 5.1 现有覆盖能覆盖什么

| 场景 | 现有用例 | 结论 |
|---|---|---|
| 单根缺失（生产形状：文件本身是根） | `SourceScanSchedulerTests.cs:1177-1197`（`ColdStartMissingRoot_IsRegistryUnavailable`，断言 `Error` + `SOURCE_REGISTRY_UNAVAILABLE`） | **只覆盖单条目**；无法区分"整库不可读"与"条目不可用" |
| 根被替换 | `SourceScanSchedulerTests.cs:1199-1220`（同路径删除+重建） | 同上；且**依赖文件系统分配不同 FileId**（NTFS 可能复用），本身有 flaky 风险 |
| registry 文件损坏（与 journal 无关） | `SourceRegistryTests.cs:136-164`（`[1,2,3]` 字节 → `UNAVAILABLE`；`.corrupt-*` 存在；`Reset(false)`→`INVALID_REQUEST`；`Reset(true)` 清空） | 文件级损坏覆盖**充分**，且本卡必须保持其绿 |
| 多根混合 | —（`SourceWatcherTests.cs:312,359-360` 注册过两个条目但从不使其中一个失效） | **零覆盖** → 本卡新增用例的核心 |
| 注册/撤销/枚举在部分不可用时可用 | — | **零覆盖** |
| 真实 IPC + registry | `Fea11ScanIpcTests.cs:50,212`、`Fea09RealIpcTests.cs:70`、`Fea11SourceIpcTests.cs:154,202` | 均为单条目 fixture；可复用为"混合"扩展的骨架 |

### 5.2 需新增（最低集合）

1. `SourceRegistryResilienceTests`：
   - `TwoEntries_OneDeletedRoot_ListReturnsBoth`（AC-LS1-2）；
   - `TwoEntries_OneDeletedRoot_AuthorizeHealthySucceedsAndPersistsLastUsed`（AC-LS1-2/AC-LS1-7）；
   - `DeletedRoot_AuthorizeIsTypedAndWritesNothing`（AC-LS1-3/AC-LS1-7：写前后 registry 字节相等）；
   - `ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity`（AC-LS1-4）；
   - `RegisterNewRootWhileAnotherRootIsMissing_Succeeds`（AC-LS1-2，导入解阻的直接断言）；
   - `FileLevelCorruption_StillUnavailableAndCopiesOnce`（AC-LS1-1 回归，与既有用例互补）。
2. `SourceScanSchedulerTests` 扩展：`MixedRegistry_HealthyTargetScanned_UnavailableTargetTypedError`（AC-LS1-5/AC-LS1-6），断言帧计数与 `missing` 为空；`EnumerationStatus_StaysOkWithMixedRegistry`。
3. 负例：`MissingRoot_NeverAuthorizesAnyPath`、`PathUnderUndeclaredDirectory_Denied`（AC-LS1-3）。
4. **gated 真机 IPC（建议 1 条，非全量）**：真实 Core + 混合 registry（一条正常 + 一条根已删）→ 枚举成功、正常源产出 1 帧、坏源 0 帧 0 missing、`source_list_roots` 成功、wire 无路径。理由：本卡改的是"可用性判决分布"，组件级单测可判别，但"枚举成功 + 单帧 + 零写"这类跨进程事实按项目惯例仍值得一条 canonical 证据（SCAN-2 的 EV-03/04 已是同族模板）。若 DSH 判定成本过高，可降级为"组件级真实 Core E2E"并在卡面写明限定。

### 5.3 门禁成本 / flaky

- **全量 .NET**：基线 1527/0/86（`STATUS.md:20`）；SCAN-2 已记录 FluentAssertions/`Threading`/reflection 三类偶发 flaky（卡面 `:125`，需逐次记录 + 隔离复跑）。本卡是 Host 单测密集改动，**首跑 flaky 概率不低**，AC 必须要求"原样记录 + 隔离复跑"而不是"重跑到绿"。
- **全量 pytest**：本卡应**零 Python 改动**；仍建议跑一次（3249/10）以便"零漂移"有据；成本按 SCAN-2 经验可接受。
- **API inventory / pins / check**：均为秒级。
- **写入卫生**：`SourceRegistryTests` 现有 fixture 会写 `verification/FEA-09/native-registry/**`（`:140-145`），实施者必须在跑测后 `git status` 并**只清理本次新建的隔离目录**（SCAN-2 已有 `git checkout -- verification/FEA-09` 的先例，卡面 `:101`）；新用例应优先落在 `Path.GetTempPath()` 隔离根（`NewSourceDirectory()` 风格），不要再往 `verification/FEA-09` 堆。

## 6. Q5 风险 / limitation

| # | 风险 | 说明与缓解 |
|---|---|---|
| R1 | **安全放宽**（最高） | 把身份校验从 `Load` 移到"按需"时，若 `Authorize` 漏掉补位，**被替换的根会重新获得授权能力**（现状由 `Load` 的 eager 校验兜住，`SourceAccessRegistry.cs:126-127`）。缓解：AC-LS1-3/AC-LS1-4 用"同路径新文件 + registry 字节零变化"双断言；实现必须保证**所有** `Authorize` 入口（`:400,403,467`、`HostOperationOrchestrator.cs:132`）走同一补位逻辑，不得存在旁路。 |
| R2 | **journal/并发写入** | 每次探针都要在 `Locked()` 内、读盘之后；`Authorize` 的三次调用（`SourceReadCoordinator.cs:400,403,467`）会各做一次探针（每根一次 `CreateFileW`），I/O 微小但**不得**为了省 I/O 把探针结果跨调用缓存（会与"写前重验"矛盾）。失败路径必须零写（C-15 `:309` 同源约束）。 |
| R3 | **`.corrupt-*` 无界复制** | `:134` 每次 `Load` 失败复制一份，无清理（全仓仅此 1 处引用）；文件级损坏下每 tick×每 target 各一份。本卡会消除"根缺失"这个主驱动，但文件级损坏的放大仍在 → **登记 limitation**（可选并入同一 UNFREEZE 载体授权"每次启动至多 N 份/按文件 hash 去重"）。 |
| R4 | **identity 校验语义/粒度** | 现状只比对 `Volume`/`Id`，**不比对 size**（`:126-127`）；目录根也没有 size 概念。因此"同路径、同 FileId、内容被改"不会被根校验发现（由 mint 期 digest/`FILE_IDENTITY_CHANGED` 兜住，`SourceReadCoordinator.cs:444-454`）。本卡**不改变**这一分层，但卡面不得宣称"根校验证明内容未变"。 |
| R5 | **恢复路径复杂度（limitation 主线）** | 见 3.1(c)：产品内 0 恢复入口；被替换根在 B 卡前**无法**在同路径重新导入（App 复用失效条目 `SourceImportModels.cs:782-786`）。必须写进卡面 limitation，并禁止在 A 卡里用"自动重注册"绕过（撞 I-3）。 |
| R6 | **跨平台路径** | 实现全量依赖 Win32（`CreateFileW`/`GetFileInformationByHandle`/DPAPI/`Global\` mutex）：`SourceSecurity.cs:107-129`、`SourceAccessRegistry.cs:175-199`。拆分不得引入任何"非 Windows 分支"或路径假设；测试机必须是 Windows 交互用户（DPAPI）。 |
| R7 | **与 2A 缓存 / 2B 容器成员面的交互** | 2A：`SourceIdentityCache` 与 registry 无关，但 Run 预授权现在因 `List()` 成功而**从"整轮 skip"变成"逐源 mint + 逐源 typed skip"**（`SourceReadCoordinator.cs:159-192`；`SourceRegistryTests.cs:298-318` 是注入式单测，不受影响；真实 e2e 的 warning 计数可能变化 → AC 要求重跑 2A/2B 相关 IPC 或在卡面登记）。2B：容器 mint 必须在**根校验之后**才 `DescribeContainer`/哈希（现状顺序已正确：`:400` authorize → `:411` 打开容器），拆分不得把顺序反转；否则会对"替换后的容器"先做 256MiB 哈希再拒绝。 |
| R8 | **证据夸大** | 三条红线：① 不得用"单条目 fixture 通过"宣称"多根混合可用"（本卡新增混合用例就是为了消掉这个空档）；② 不得用"typed fail-closed 正确"掩盖"用户无法恢复"（必须同时写 limitation）；③ `SOURCE_REGISTRY_UNAVAILABLE` 的**码义已收窄**（条目级 vs 整库），任何证据文本必须写清是哪种。SCAN-2 的 L-S1 证据只到"executor 单测级"（`host-shard-record.md:101`），不得被引用为"韧性已修"。 |

## 7. Q6 优先级与裁决输入

### 7.1 与其它候选的比较

| 候选 | 用户影响 | 成本/风险 | 结论 |
|---|---|---|---|
| **L-S1（本卡 A）** | 中高：删/移/换一个引用源即**全库源线（扫描 + 新导入 + apply）不可用**，且无产品内恢复 | 低：1 文件 + 测试；**1 pin UNFREEZE**（窄句）；无 wire/Core/UI | **建议优先**（唯一"日常动作即可触发 + 全库影响"的可用性缺陷） |
| 2C 长 Run 续期（L-G1） | 高（长 Run 可用性），但是**功能缺口**而非回归 | 高：新 host-control 命令 + 能力 + 可能 C-16 UNFREEZE + Core + 跨分片 | 次之；L-S1 之后 |
| L-S4 `refresh_source_location_auth` 死代码 | 中（撤销/重注册后 Core location auth 不更新） | 低（Core 单点） | **与 B 卡绑定**：B 的"撤销→重注册"恢复链缺它就不完整；建议紧随 A（或与 B 同批） |
| L-R11 gate 统一 | 低（语义一致性） | 中（跨读面） | 排后 |
| C-04b 文档 residual（8 项） | 无运行时影响 | 低 | 排后（可穿插） |
| SCAN-2 RH-1…RH-5 | 低（行为噪声/证据强度） | 低-中 | 排后 |
| UI P3/L3/L4 | 视觉 | 低 | 排后 |

**结论**：L-S1 应排在 2C 之前、L-S4 之前（但 L-S4 紧随，且是 B 的前置）；L-R11/C-04b/SCAN-RH/UI P3 均不应抢占本卡窗口。理由：它是当前队列里**唯一由普通用户动作触发、影响跨源全库、且修复成本最小**的缺陷。

### 7.2 需 DSH / Codex 裁决的具体问题（含推荐）

| # | 问题 | 推荐 |
|---|---|---|
| **D-1** | 是否批准 **C-15 §5 单条 UNFREEZE**（`FEA-C15_SOURCE_STORAGE_DRAFT.md:312`），把"roots identity 不合法"从文件损坏拆为条目级不可用？ | **批准**；1 pin（C15 重算 `d8c0a3bcfc21`），C-16/C-17 零改动；载体内引用 FEA-09 卡 `:110`/FEA-09 scope r1 `:105` 为被取代的决策来源 |
| **D-2** | 错误码：保持现状（mint/scan 都用 `SOURCE_REGISTRY_UNAVAILABLE`）还是按 C-16 `:174`/C-06 `:44` 改成 mint 面 `SOURCE_ACCESS_DENIED`？ | **保持现状**（零可观察漂移、保 AC-S2-5 pin）；把"码义收窄"登记 limitation；码词表细化另案（需 C-16 §6 + C-06 各 1 pin） |
| **D-3** | 是否按 4.1 拆 A/B/C？本轮只释放 A？ | **是**；B 另卡（依赖 L-S4 + 需 C-16 §1），C 只登记 |
| **D-4** | A 是否包含 App 侧"typed 失败后自动重注册根"？ | **否**（撞 I-3 自动重新授权；且把 App 拉进写域）；B 卡用显式用户动作解决 |
| **D-5** | `.corrupt-*` 无界复制是否并入本轮？ | **不并入**；登记 limitation；若 DSH 愿意，可在同一 C-15 载体里授权"每次启动至多 N 份"作为可选小项 |
| **D-6** | `allowed_paths` 是否按 4.2 冻结（含新增测试文件）？ | **按 4.2 冻结**；`SourceScanScheduler.cs`/`HostRuntime.cs`/`SourceWatcher.cs` 等**明确 Out**，需要时走 scope 修订 |
| **D-7** | 是否要求 1 条 gated 真机 IPC（混合 registry）作为 canonical 证据？ | **要求**（成本可控、能消掉"单条目 fixture"空档）；若否，卡面必须写明"组件级补足"的限定 |
| **D-8** | 冻结前是否先修 `TASK_LEDGER` 漂移（当前 `check.ps1 -TaskPath` FAIL）？ | **必须先修**（Lead 执行 `task_ledger.py --write`），否则 AC-LS1-10 无法成立、卡无法合规释放 |
| **D-9** | 是否要求 A 复跑 2A/2B 的 Run/IPC 用例（因警告计数与 skip 分布会变）？ | **要求**跑 `Fea11RunGrantIpcTests`/`Fea11ScanIpcTests` 并记录；若断言漂移，只允许改"计数/警告文本"断言并说明，不得改语义 |

## 8. 真实性声明

1. 本报告由**独立上下文 fresh subagent** 产出（session `976c9d16-…`，父会话 `session-5f1e719c-…`），**未参与** FEA-11-L-S1 或 RUN-GRANT-1/2/2A/2B 的任何实现、返修或审查；全程**只读**，仅在 `reviewed_head` 上新增本文件。
2. 所有代码/契约事实均来自 `d782c52a4` 的仓库字节，逐条给出 `path:line`；未使用 Handoff/卡面自述作为实现事实。
3. **实测命令**（已跑）：`git rev-parse HEAD`、`git status --porcelain`、`git branch --show-current`、`git log -1`、`pwsh -NoProfile -File tools/governance/verify_pins.ps1`（PASS 18/18）、`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`（FAIL 2 errors / 3 warnings）。
4. **NOT_RUN**（原因已写明）：定向 `dotnet test`、全量 .NET、全量 pytest、`generate_api_inventory.py --check`、真实 IPC/真机证据。本报告不对这些项目作 PASS 声明。
5. **并发写入声明**：审查期间另一会话在共享工作树新增了 `doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md`（`proposed`）。本报告未修改、未删除、未以其为依据；该文件会使 TASK_LEDGER 漂移计数进一步增加（见基线表与 D-8）。
6. 本报告中的 In/Out/allowed_paths/AC 与 UNFREEZE 判定均为**建议**；scope 冻结、契约字节变更、Review Appointment 与 findings 处置属 DSH。
7. 未修改任何生产代码、测试、契约、卡、STATUS/PLAN/LEDGER；未执行 `git add/commit/push`。
