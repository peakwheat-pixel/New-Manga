---
task: AC11-1-ADJUDICATION-INPUT
title: AC11-1 终态裁决输入：「启动/访问前检查」的解释 A/B、代码事实与回填口径
reviewer: fresh subagent（独立上下文；只读）
session: 8a6c3d10-bc90-4809-95ed-7d3be9648869（DSH fresh subagent）
date: 2026-11-06
reviewed_head: 987d81981baf6e45c0de520bcd905b26f524fd34
recommendation: A+
---

# AC11-1 终态裁决输入（不是最终裁决）

> 用途：供 DSH（Lead / Architect / Integrator）就 `FEA-11` AC11-1 的「启动/访问前检查」解释与终态（`MET` / `PARTIAL`）作裁决。
> 边界：本文件是**裁决输入**，不是裁决；不改生产代码、测试、契约、STATUS、PLAN、LEDGER、历史 Task/Review/证据字节；不 commit/push。
> 基线：`main`，HEAD `987d81981baf6e45c0de520bcd905b26f524fd34`，`git status --short` 为空（复核时点 2026-11-06）。本子代理唯一写入为本文件。
> 执行说明：本子代理**未运行** pytest/.NET/`check.ps1`/`verify_pins.ps1`（只读裁决输入任务）；下文测试结论分两类：**静态核对**（读测试源码断言）与**既有运行记录**（引用各承接卡 closeout 的实跑数字，不重跑、不背书）。

## 0. 结论摘要

1. **推荐 `A+`**：「启动/访问前检查」的权威解释取 **A（访问前 = 每次源访问/读取/操作前 live grant + lease + digest 强验证）**；「启动」由 **冷启动目标枚举 + 启动期 registry/root 可用性与授权核验**（FEA-11-SCAN-2）承载，**不要求启动时全量内容扫描**。同时以 limitation 显式登记「启动不做全量内容扫描」，并保留一个**可选**后续卡位（不是 AC11-1 判 MET 的前置）。
2. **文本层级支持 A**：用户架构决定 AD-003 §3.6（`:89`）与冻结契约 C-01b SC-25（`:84`，FROZEN v5，pin `3c9f5af7…`）的检测组合都只有「访问前检查、操作前强验证、定期扫描、目录 watcher hint」**四项、不含启动扫描**；C-17 v1.1:18 的「四路检测（启动/访问前、操作前、定时扫描、watcher）」把「启动/访问前」写成**一路**；C-17 v1.1 新增的冷启动命令 `source_list_scan_targets` 只**枚举目标**、不读内容。
3. **代码事实支持 A 的“访问前”半边**：读取/操作路径确实有 live grant + strict lease（size + sha256 + file identity）强验证，失配即 typed 失败（`FILE_IDENTITY_CHANGED` / `SOURCE_GRANT_REVOKED`）。
4. **代码事实同时证明 B 的缺口真实存在**：全仓**没有**启动全量内容扫描；SCAN-1 周期循环**先 delay 一个间隔**（默认 900s）再首次 tick；SCAN-2 冷启动只枚举 target/核验 registry，**不扫内容**；FEA-11 卡 `:238` 的「watcher 与启动扫描未承接，登记 WATCH-1/SCAN-2（proposed，未释放）」在 HEAD 已**过期**（两者均 done），属文档时间线缺陷。
5. **若 Lead 采 B**：AC11-1 必须保持 `PARTIAL`，另立 `FEA-11-STARTUP-SCAN-1`；本文件 §5 给出范围草案、依赖、AC 与 limitation 文本。

## 1. AC11-1 原文与相关表述（逐字、行号、时间线）

### 1.1 AC11-1 行逐字（`doc/tasks/FEA-11.md:103`）

> - [ ] **AC11-1（变化检测与阻断）**：启动/访问前检查、操作前强验证、目录 watcher 生产者路径（本卡两条已测；定时扫描与 watcher 消费者承接 FEA-11-SCAN-1）；丢 hint/overflow 后可全量重枚举检测；相同 mtime/size 但字节变可发现；mtime/size 未变不作内容未变证明；强验证=稳定 lease+digest，不被缓存替代；Dirty 阻断依赖旧绑定的新写入而不是直接换 binding。定时扫描若本卡不做，须由 PREREQ/DSH 裁定并登记承接 Task，不得静默缺失。`<<PARTIAL: 待 scope-r2 冻结逐项断言>>` `<<PARTIAL: 定时扫描/watcher 生产承接 FEA-11-SCAN-1；本卡两条已测路径（定时/消费者承接 SCAN-1）>>`

可用读法（按原文，不按目标图推断）：

- 第 1 分句是四类检测：**启动/访问前检查**、**操作前强验证**、**目录 watcher 生产者路径**（原文括注：本卡两条已测；定时扫描与 watcher 消费者承接 FEA-11-SCAN-1）、**定时扫描**（末句要求延期须 DSH 裁定并登记承接）。
- 原文只为**定时扫描**写了显式延期条款；没有为「启动/访问前检查」单列延期。
- 「强验证=稳定 lease+digest，不被缓存替代」「相同 mtime/size 但字节变可发现」「mtime/size 未变不作内容未变证明」是检测语义约束，不是触发时机约束。

### 1.2 双 `<<PARTIAL>>` marker 与时间线冲突

`check.ps1:816-851` 的 AC 门禁正则锚定行末（`:828` `<<(MET|PARTIAL|BLOCKED|NOT_APPLICABLE)(?:: …)?>>[ \t]*$`），因此**只有最后一个 marker 被识别**；第一个 marker 实际不参与机检，只作为正文文本存在。

| # | marker / 行 | 原文 | 冲突事实 |
|---|---|---|---|
| M1 | `FEA-11.md:103` 第一个 | `<<PARTIAL: 待 scope-r2 冻结逐项断言>>` | scope-r2 已于 2026-11-04 `approved`（`doc/reviews/FEA-11-scope-r2.md:19`、`:79-81`）；该 marker 的待办已结束，但从未刷新（`FEA-11.md:114` 的“scope-r2 approved 后细化”未执行）。 |
| M2 | `FEA-11.md:103` 第二个（机检识别） | `<<PARTIAL: 定时扫描/watcher 生产承接 FEA-11-SCAN-1；本卡两条已测路径（定时/消费者承接 SCAN-1）>>` | ① watcher 最终承接 **WATCH-1**（`FEA-11-SCAN-1.md:83` O-2、`:148`、`:223`），不是 SCAN-1；② “本卡两条已测路径（定时/消费者承接 SCAN-1）”自相矛盾——把被延期项写成本卡已测项；WATCH-1 scope review（`:52`）把「本卡两条已测」读作前两路（启动/访问前 + 操作前）；③ 被指名的承接对象（SCAN-1/SCAN-2/WATCH-1）截至 HEAD 均已 `done`，而 marker 仍写“承接中”。 |

时间线（同一事实在不同文档中的漂移）：

| 时点 | 文档/行 | 表述 | HEAD 现状 |
|---|---|---|---|
| 2026-10-31 | `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:89` | 检测组合：**访问前检查、操作前强验证、定期扫描、目录 watcher hint**（无“启动扫描”） | 现行架构决定 |
| 2026-11-01 | `doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md:84` SC-25 | 同上四项；“watcher 与 mtime/size 均非真值，强验证以稳定读取 lease + digest 证明” | **FROZEN v5**，pin `3c9f5af7…`（`FEA-CONTRACT-FROZEN-C01b.md:15-16`） |
| 2026-11-04 | `doc/tasks/FEA-11.md:139`（DSH 裁决） | 本卡首版实现**三路**：**启动/访问前检查**、操作前强验证、watcher 消费者；**只把“定时扫描生产者与后台调度”承接 `FEA-11-SCAN-1`** | 该裁决把“启动/访问前检查”计入 FEA-11 首版范围 |
| 2026-11-04 | `doc/reviews/FEA-11-appointment.md:24` | 同上三路表述 | 与 `:139` 一致 |
| 2026-11-04 | `doc/reviews/FEA-11-scope-r2.md:57` | S11-009 四路（**启动/访问前、操作前、定时扫描、watcher 生产者/消费者**）各有调用证据 | scope 冻结口径 |
| 2026-11-05 | `doc/reviews/FEA-11-r7-acceptance.md:20` L-3 | “定时扫描与 watcher 消费者未实现（本卡两条路径已测）→ `FEA-11-SCAN-1`” | 用户裁决 limitation |
| 2026-11-05 | `doc/tasks/FEA-11-SCAN-1.md:91` O-10 | 冷启动全源枚举另立 `FEA-11-SCAN-2` | SCAN-2 后来做的是**枚举**，不是内容扫描 |
| 2026-11-06 | `doc/tasks/FEA-11-SCAN-1.md:106` | “AC11-1 仍 PARTIAL……watcher（WATCH-1）与**启动扫描（SCAN-2）**仍缺” | 把 SCAN-2 称为“启动扫描”，但 SCAN-2 实际只枚举 |
| 2026-11-06 | `doc/tasks/FEA-11-SCAN-1.md:183` | “首次 tick 在一个间隔之后（**冷启动不枚举**）” | 周期扫描无启动立即 scan |
| 2026-11-06 | 仓外 `...\workspace\FEA-11\scope-review\FEA-11-SCAN-1-scope.md:27-37,186-195` | “启动/访问前**自动扫描**／未找到独立实现”；AC 映射“**启动/访问前检查**／**不承接**；访问前检查仍是读取时强验证” | 首次把“启动”拆成“自动扫描”的解释源 |
| 2026-11-06 | `doc/tasks/FEA-11-SCAN-2.md:58,158,252` | 只闭合冷启动**枚举**半边；**不**把 AC11-1 整体标 MET | SCAN-2 已 done（`555f57b8d`） |
| 2026-11-06 | `doc/tasks/FEA-11-WATCH-1.md:44,73` | “**不做**启动全量扫描；解释歧义留给 AC11-1 终态裁决”；“或按 watcher + 访问前/操作前强验证 + 周期/冷启动扫描组合判定 MET，需显式记录” | WATCH-1 已 done（`00083a977`） |
| 2026-11-06 | `doc/tasks/FEA-11.md:238` | “watcher 与启动扫描未承接，登记 `FEA-11-WATCH-1`/`FEA-11-SCAN-2`（proposed，未释放）” | **过期**：两卡均 done |
| 2026-11-06 | `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:18`（C-17 v1.1） | “四路检测（**启动/访问前**、操作前、定时扫描、watcher）是 FEA-11 的实现责任”；v1.1 仅新增冷启动**目标枚举**命令 | C-17 v1.1 FROZEN，pin `aefa0fa5…`（`FEA-CONTRACT-FROZEN-C17.md:15`） |

结论：**「启动/访问前检查」的语义从未被单一权威文本冻结**；可冻结的上级文本（AD-003、C-01b SC-25）只写“访问前检查”；FEA-11 的 AC 与 DSH 2026-11-04 裁决把它作为**一路**；SCAN-1 scope review 把它拆成“启动自动扫描 + 访问前强验证”，后续卡沿用了这个拆分但从未裁决。

## 2. 代码/测试事实核验（证据表）

### 2.1 “访问前/操作前强验证”确实实现（A 的访问半边）

| # | 事实 | 证据（path:line / 测试名） | 结论 |
|---|---|---|---|
| F1 | 源读取统一走 strict lease：打开非写句柄后校验 file identity + size，读入后校验 size + sha256，再复核 identity；任一不符 → `FILE_IDENTITY_CHANGED`；不可读 → `SOURCE_ACCESS_DENIED` | `src/infrastructure/resource_channel/source_strict_read.py:12-41`（`:27-31` identity，`:33-34` size+sha256，`:35-36` 复核）、`:64-67` `read_verified_bytes` | 读取即强验证，不依赖 mtime/size 真值 |
| F2 | 每次 entry 读取（image/zip/cbz/folder/pdf）都经 `read_verified_bytes` | `src/application/importing/referenced/reader.py:50-111`（`:53/:59/:102/:107` 调用） | “访问前检查”覆盖真实读路径 |
| F3 | 生产装配把 strict reader 注入 referenced scanner | `src/bootstrap/core_assembly.py:1229-1233` | 非测试专用 |
| F4 | commit/操作前再取严格 lease（commit guard） | `src/infrastructure/resource_channel/source_read_refs.py:275-289`（`:281-287`） | “操作前强验证”有独立实现 |
| F5 | `ScanSourceSync` 解析 live grant（revoked/expired typed）后读取内容并算 digest；无 location 时先验证 grant 再报错（grant 错误优先） | `src/application/sources/scanner.py:3`、`:240-258`、`:332-334`、`:504-509`、`:540-587` | 读取前有 live 授权校验；内容检测靠 digest |
| T1 | 过期/撤销 grant → typed 拒绝 | `tests/fea11/test_source_scan.py:168-186`（`SOURCE_GRANT_REVOKED`） | 测试覆盖 |
| T2 | 确认前容器字节变化 → strict 重验 typed `FILE_IDENTITY_CHANGED`，零页写入 | `tests/fea09/test_referenced_flow.py:529-553` | 测试覆盖 |
| T3 | commit 边界撤销 → 中止后续页 | `tests/fea09/test_referenced_flow.py:296-324` | 测试覆盖 |
| T4 | 扫描时身份漂移 → `FILE_IDENTITY_CHANGED`（image/folder 两例） | `tests/fea09/test_referenced_scanner.py:79-89`、`:139-149` | 测试覆盖 |
| T5 | 同步前源字节漂移 → `FILE_IDENTITY_CHANGED` | `tests/fea11/test_source_sync.py:1541-1556` | 测试覆盖 |
| T6 | 同 key 不同 bytes → typed 拒绝，旧发布不被覆盖 | `tests/fea11/test_source_resolve.py:99-139` | 测试覆盖 |
| T7 | 真实 Host-issued grant 的端到端 scan | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs:143-191`（`ScanWithAHostIssuedGrant_WorksEndToEnd`） | gated IPC 测试 |

### 2.2 定时扫描不在启动时立即跑（B 的“启动全量扫描”缺口属实）

| # | 事实 | 证据（path:line / 测试名） | 结论 |
|---|---|---|---|
| F6 | 周期循环**先 delay 一个间隔**再 tick；注释明写 “never enumerates all sources at cold start (O-10 / L-A)” | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:961-994`（`:963`） | 无启动立即扫描 |
| F7 | Ready 后注释：“the first periodic tick still happens after one interval, over the merged/verified target set” | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:1189-1194` | 与 F6 互相印证 |
| F8 | 调度器默认 900s、enabled=true；`Start()` 只启动循环 | `apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs:97-100`；`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:265-273` | 默认行为 |
| F9 | 首次 tick 在 900s 之后（测试注入时钟 advance 900s 才出现 1 次扫描） | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs:279-301`（`Start_IsIdempotent_AndRunsASingleLoop`） | 测试固定该行为 |
| F10 | 卡面冻结行为：“首次 tick 在一个间隔之后（冷启动不枚举）” | `doc/tasks/FEA-11-SCAN-1.md:183` | 范围事实 |
| T8 | 真实 IPC：同 name/size 不同 bytes 在 tick#2 被报 `changed`；删除后 `missing`；全程零 Core 写 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:29-128`（`:39-42` 同 size、`:100-105` changed、`:126-128` 零写） | 周期扫描的检测能力已实测 |

### 2.3 SCAN-2 冷启动是“列 target”，不是“扫内容”

| # | 事实 | 证据（path:line / 测试名） | 结论 |
|---|---|---|---|
| F11 | 枚举器只调冻结只读命令 `source_list_scan_targets`、核验 Host registry、计数 typed skip；“never plans, authorizes, **reads content** or writes any state” | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1727-1733`；C-17 `:228`、`:261-262`、`:279`（只读 SELECT、零写、不铸 grant） | 枚举≠内容扫描 |
| F12 | `RefreshTargetsAsync` 只写内存 target 集/状态，成功后通知 watcher 重新评估覆盖；**不调用** `TickAsync` | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:525-638`（`:547` 单飞、`:615-632` 合并/通知） | 冷启动枚举不触发 scan |
| F13 | HostRuntime 在 Ready 后后台枚举，不阻塞启动 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:1326-1331`；`apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs:119`（默认 true） | 启动期只做枚举 |
| T9 | Ready→后台枚举、非阻塞、typed fail-closed | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Scan2HostRuntimeTests.cs:29-77`（`Ready_StartsBackgroundEnumeration_WithoutBlocking`） | gated 测试 |
| T10 | 无 App 注册的冷启动枚举只读；真实导入→枚举 source_id 权威 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:193`（`ColdStartEnumeration_WithoutAppRegistration_IsReadOnly`）、`:415`（`RealImportThenEnumeration_SharedSource_UsesAllScope_AndCoreSourceId`） | IPC 测试 |
| F14 | 启动期确实有“检查”：枚举时核验 registry/撤销/代次/root 可读；file-root 缺失 → typed `SOURCE_REGISTRY_UNAVAILABLE` fail-closed（不伪 missing） | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1338-1475`（`VerifyEnumeratedTarget`/`_verifiedEnumeratedRoots`）；`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Scan2HostRuntimeTests.cs`；SCAN-2 AC-S2-4/5（`FEA-11-SCAN-2.md:96-97`） | “启动检查”存在，但内容是授权/可用性，不是内容 digest |

### 2.4 watcher（WATCH-1）已兑现，且只触发全量重枚举

| # | 事实 | 证据（path:line / 测试名） | 结论 |
|---|---|---|---|
| F15 | `SourceWatcher` 存在；Ready 后 arm、Stop 后零 hint；hint → due bit → 一次 `ScanSourceSync` | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs`；`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:1299-1320` | 已实现 |
| F16 | 状态面新增 `Watcher` 子记录（计数/typed code，无路径） | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanStatus.cs:31-53` | 可观测 |
| T11 | 真实文件事件→hint→scan→Dispose disarm | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11WatchHostRuntimeTests.cs:22`（`Ready_ArmsWatcher_RealFileEventProducesHint_DisposeDisarms`） | gated 测试 |
| T12 | 去抖/合并/overflow/根删除/单飞/预算/脱敏 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceWatcherTests.cs`（19 个 `[Fact]` 方法，如 `Debounce_MergesManyEventsIntoOneHint_AndOneFullRescan`、`Overflow_HintsAllTargets_Degrades_AndNeverCrashes`、`RealFileSystemWatcher_DetectsIsolatedFileChange`） | 测试覆盖（静态核对） |

### 2.5 汇总判断

- **存在**：访问前/操作前 live grant + lease + digest 强验证；周期全量扫描；冷启动目标枚举与启动期 registry/root 核验；watcher hint 与 overflow 重枚举；同 mtime/size 字节变检测。
- **不存在**：应用启动时对全部已注册源执行**全量内容扫描**（任何入口/任何配置开关都没有；`SourceScanScheduler.LoopAsync` 与 `HostRuntime` 注释、SCAN-1 卡 `:183`、SCAN-1 scope review 均确认）。
- 因此 B 的“缺口”是真实的；A 的“访问前”半边也是真实的；“启动”半边的实现形态是**枚举+可用性/授权核验**，而非内容扫描。

## 3. A/B 论证

### 3.1 文本依据（按效力从高到低）

**A（访问前 = 读取/访问/操作前强验证；启动 = 目标枚举 + 可用性/授权核验）：**

1. **AD-003 §3.6（用户架构决定，2026-10-31）** `:89`：检测组合恰为“访问前检查、操作前强验证、定期扫描、目录 watcher hint”，**没有启动扫描**。这是产品架构层对检测组合的正式记录。
2. **C-01b SC-25（FROZEN v5，2026-11-01，pin `3c9f5af7…`）** `:84`：与 AD-003 逐字一致，并明确“强验证以稳定读取 lease + digest 证明”。A 与冻结条款**完全一致**；B 需要把“访问前检查”扩读为“启动也扫描”，属于对冻结文本的增量解释。
3. **C-17 v1.1:18（FROZEN，2026-11-06，pin `aefa0fa5…`）**：把四路写成“**启动/访问前**、操作前、定时扫描、watcher”，即「启动/访问前」是**一路**（否则是五路）；同版新增的正是冷启动**目标枚举** `source_list_scan_targets`（C-17 `:228`、`:279`），说明契约作者把“启动”落在**枚举/授权核验**，不是内容扫描。
4. **FEA-11 的 DSH 2026-11-04 裁决** `:139` 与 **Appointment** `:24`：首版三路包含“启动/访问前检查”，且只把“定时扫描生产者”延期；即 FEA-11 自身的范围裁决把该路视为**首版已实现**（卡面“本卡两条已测”=启动/访问前 + 操作前；两路均有 §2 的实现/测试证据）。
5. **WATCH-1 scope review §10 P3-2**（`:426`）：明确建议 Lead 冻结“**「启动/访问前检查」= 既有的读取时强验证；本卡不实现启动全量扫描**”；其 §2.3（`:81`）把该子项判为“已覆盖（按「访问前检查」读法）”；§9.3（`:413`）指出若解释为“启动全量扫描”，那是**另一条未承接路径**。
6. **SCAN-2 的“启动检查”事实**：AC-S2-4/5（`FEA-11-SCAN-2.md:96-97`）在启动期核验 registry/撤销/代次/root 可读，root 缺失 typed fail-closed——这为“启动检查”提供了**非内容扫描**的实质实现。
7. **FEA-11 AC 原文的延期条款只覆盖定时扫描**（`:103` 末句），没有为“启动”单列延期；若“启动全量扫描”是硬项，按该卡的延期纪律应被显式登记，而事实是没有（直到 SCAN-1 scope review 才被拆出）。

**B（启动 = 启动时对全部已注册源全量内容扫描）：**

1. **FEA-00 提案 `:442`**（设计提案，非冻结）：“变化检测组合：**启动/访问前检查**、操作前强验证、后台定期扫描、目录 watcher dirty hint”。这是 AC11-1 措辞的直接来源，但它是提案而非契约。
2. **SCAN-1 scope review**（仓外 `workspace/FEA-11/scope-review/FEA-11-SCAN-1-scope.md:27-37,186-195`）：把该子项读成“启动/访问前**自动扫描**”，判“未找到独立实现/本卡不承接；访问前检查仍是读取时强验证”。这是 B 的唯一“审查级”文本依据，但它本身没有裁决效力，且把“自动扫描”加进了原文。
3. **SCAN-1 卡 `:106` 与 FEA-11 `:238`** 把“启动扫描”当作待承接项（后由 SCAN-2 以“冷启动枚举”覆盖；枚举≠内容扫描）——这是承接链的措辞，不是对 AC 语义的冻结。

> 文本层级结论：A 与最高效力文本（AD-003 + C-01b FROZEN）一致；B 依赖提案措辞与一次 scope review 的拆读。若采 B，应视为**对 AC 的重新解释 + 新增实现范围**，而不是“补做遗漏”。

### 3.2 与 C-01b SC-25 / C-17:18 的一致性

| 组合 | C-01b SC-25（FROZEN v5） | C-17 v1.1:18（FROZEN） | 一致性判断 |
|---|---|---|---|
| A | 四项：访问前检查、操作前强验证、定期扫描、watcher hint；A 的四路实现与之一一对应（“启动”落在枚举/核验，不新增检测组件） | “启动/访问前”一路 + 操作前 + 定时 + watcher；A 把“启动/访问前”解释为「启动枚举/核验 + 访问时强验证」 | **一致**（不新增冻结组合之外的检测组件；无需改契约字节） |
| B | 需要把“访问前检查”扩读为“启动也做内容扫描”，或把“启动扫描”作为**第五个**检测组件 | C-17:18 的“启动/访问前”可被读成包含启动扫描；但 C-17 没有定义启动扫描的范围/预算/时序 | **部分一致/需解释**：若作为第五组件，超出 SC-25 的封闭组合；若并入“访问前”，则是对冻结文本的增量解释。两种都应在裁决文件中显式说明，且不应改契约字节。 |

补充：C-01b SC-25 是 `[新增]` 条款且被 WATCH-1 视为“兑现”（`FEA-11-WATCH-1-scope-r1.md:336`）。A 使 SC-25 的四项**全部有实现/测试**，契约债务闭环；B 会让 SC-25 仍需追加解释，但不会使已兑现项失效。

### 3.3 采 A 的风险

| # | 风险 | 说明 | 缓解 |
|---|---|---|---|
| A-R1 | **“启动”字面落空** | 若读者把“启动”理解为“应用启动即检查内容”，A 下没有启动内容扫描；`FEA-11.md:238` 的旧文本也仍写“未承接” | Closeout 补充 + Lead 裁决文件显式写“启动=枚举/可用性核验，不做全量内容扫描”；limitation 固定；旧行不改但注明被补充取代 |
| A-R2 | **检测延迟** | 应用关闭期间源被改，重开后最迟 900s（可配 [60,86400]）或下次访问/操作才发现；watcher 对关闭期间事件无效 | limitation 明示；访问时 typed 失败阻断错误内容；可选后续卡降低延迟 |
| A-R3 | **访问时检测只“阻断”、后续状态未在本裁决验证** | 读取失配抛 `FILE_IDENTITY_CHANGED`（typed 阻断）；本输入未证明它会自动进入 Dirty/plan（Dirty 状态机属 AC11-2 scan/diff/plan 范围） | 在 limitation 中写明“访问时检测为 typed 阻断，后台 changed 观察由周期/watcher 产生”；不把“自动转 Dirty”写成已实现 |
| A-R4 | **文档 marker 仍显示 PARTIAL** | AC 行字节保留，机检仍见 `<<PARTIAL>>`；外部审计可能误读 | Closeout 补充 + STATUS/PLAN 明确“终态以补充为准”；`check.ps1` 仍 PASS（其不比较 STATUS 文本与 AC marker） |
| A-R5 | **冻结条款解释权** | 宣布 SC-25 已兑现属于契约解释；若未来用户/审计不同意，需要回退 | 裁决文件记录依据链（AD-003/C-01b/C-17）与 limitation；不修改契约字节，回退成本低（只需改裁决/STATUS 文本） |

### 3.4 采 B 的必要性、成本与边界

**必要性**：仅是**检测延迟优化**（重开应用后更早后台发现），不是正确性必需——任何访问/读取都会被 lease+digest 拦截；周期扫描已在 900s 内兜底。若产品要求“启动后立即在后台发现外部改动”，B 才有产品价值。

**成本**：

1. 启动时对全部已注册源做全量读+digest（大库/网络盘/大容器）会带来启动期 IO 峰值；必须复用 SCAN-1 的预算（默认 8 目标/256 MiB）、退避、单飞、defer 跨 tick，且不能阻塞 Ready。
2. 需要新的一次性触发 seam（Ready/枚举完成→一次初始 pass）、one-shot 语义、与 watcher hint/tick 的单飞与优先级、停机取消、状态面/脱敏、判别测试；约数百行生产+测试（量级估计，非承诺）。
3. 需要明确**取代** SCAN-1 已冻结的行为“首次 tick 在一个间隔之后（冷启动不枚举）”（`FEA-11-SCAN-1.md:183`）——这不是改契约，但属于对既有卡面行为的范围变更，必须由新卡显式声明，否则 Review 会判越界。
4. 与 SCAN-2 的边界：SCAN-2 只枚举；启动扫描卡消费其 target 集，不重写枚举/registry 核验。

**与 SCAN-1 周期扫描的边界**：B 应实现为“Ready（且枚举尝试完成）后**一次性**初始全量 pass”，受预算/退避/单飞约束，剩余 target 顺延到后续周期；**不改变** 900s 周期语义、不改变 `ScanSourceSync` payload/scope、不建 plan/apply。若把“启动扫描”实现成“把首次 tick 提前”，会与 SCAN-1 的冻结行为冲突，必须在卡内写明“新增一次性 pass，不是修改周期”。

## 4. 推荐裁决：A+（A + 显式 limitation + 可选后续卡）

### 4.1 裁决建议（给 Lead 的原文）

> **AC11-1 终态判 `MET`（带 limitation）**。解释口径：「启动/访问前检查」= **启动期目标枚举与 registry/root 可用性/授权核验（SCAN-2）** + **每次访问/读取/操作前的 live grant + stable lease + digest 强验证**；不要求启动时对全部源做全量内容扫描。冻结依据：AD-003 §3.6、C-01b SC-25（FROZEN v5）、C-17 v1.1:18；实现证据：FEA-11 + SCAN-1 + SCAN-2 + WATCH-1。Limitation：启动不做全量内容扫描；外部变化最迟在默认 900s（可配 [60,86400]）的下一周期或下一次访问/操作时被发现。AC 历史行字节不改；终态以 `FEA-11` 的 Closeout 补充与本裁决记录为准。

### 4.2 在已关闭卡上的回填方式（不改历史 AC 行字节）

**推荐：append-only 的 “Closeout 补充” + 独立裁决记录，两者并用。** 先例：`FEA-11.md:234-239` 已用“Closeout 补充”回填 AC11-4/AC11-3，未改 AC 行。

**不建议**改 `FEA-11.md:103` 的 `- [ ]` 或任一 marker：

- 任务明确要求“不得改历史 AC 行字节”；且 `check.ps1:838-841` 规定 `MET` 必须 `[x]` 且**不得带原因**，改行必须删除 marker 原因文本，等于改写历史语义。
- 保留字节时，机检仍会把该行读成 `PARTIAL`（`check.ps1:816-851` 只读 marker），因此 Closeout 补充必须明确“该 marker 是历史字节，不代表终态”，并由 STATUS/PLAN 指向补充。这是 A+ 的已知治理代价（见 A-R4）。

**建议回填文本（追加到 `doc/tasks/FEA-11.md` 末尾，作为新节，不改任何既有行）**：

```markdown
## Closeout 补充（2026-11-06，AC11-1 终态裁决；DSH）

- **AC11-1 终态：MET（带 limitation）**。裁决依据：`doc/reviews/FEA-11-AC11-1-adjudication-2026-11-06.md`（待 Lead 创建；输入：`doc/reviews/AC11-1-ADJUDICATION-INPUT-2026-11-06.md`）。
- **解释口径（本卡终态权威）**：「启动/访问前检查」= 启动期目标枚举 + registry/root 可用性/授权核验（`FEA-11-SCAN-2`） + 每次访问/读取/操作前 live grant + stable lease + digest 强验证；**不要求启动时全量内容扫描**。冻结依据：AD-003 §3.6（`:89`）与 C-01b SC-25（`:84`，FROZEN v5，pin `3c9f5af7…`）的检测组合均不含启动扫描；C-17 v1.1:18 的「启动/访问前」是一路；C-17 v1.1 的冷启动命令只枚举目标、不读内容。
- **四路闭合**：访问前/操作前强验证（`source_strict_read.py:12-36`；`test_referenced_flow.py:296,529`；`test_source_scan.py:168-186`）；定时扫描（`FEA-11-SCAN-1` `7080167e1`）；watcher hint/overflow（`FEA-11-WATCH-1` `00083a977`）；冷启动枚举（`FEA-11-SCAN-2` `555f57b8d`）。丢 hint/overflow 后全量重枚举、同 mtime/size 字节变、lease+digest 不被缓存替代、Dirty 阻断新写均有实现/测试。
- **Limitation L-3′**：启动不做全量内容扫描；外部变化最迟在默认 900s（`NEWMANGA_SOURCE_SCAN_INTERVAL_SECONDS` 可配 [60,86400]）的下一周期或下一次访问/操作时被发现；访问时检测为 typed 阻断（`FILE_IDENTITY_CHANGED`/`SOURCE_GRANT_REVOKED`），后台 changed 观察由周期/watcher 产生。WATCH-1 的 L-W1…L-W6、SCAN-1 的 L-A/L-G、SCAN-2 的 L-S1/L-S4 继续有效。
- **历史字节与时间线**：AC11-1 行（`doc/tasks/FEA-11.md:103`）的 `- [ ]` 与两个 `<<PARTIAL>>` 按字节保留规则不改；其中“待 scope-r2 冻结逐项断言”“watcher 承接 FEA-11-SCAN-1”等表述已被本补充取代（scope-r2 已 approved；watcher 承接 WATCH-1 且 done；SCAN-1/SCAN-2 均 done）。本补充不改变 `closed_with_limitations` 终态、`delivery_head`、Canonical Evidence 字节或 18 pins。
```

**建议独立裁决记录（新文件，由 Lead 写，不由本子代理创建）**：`doc/reviews/FEA-11-AC11-1-adjudication-2026-11-06.md`，frontmatter 至少含 `task: FEA-11`、`decision: AC11-1-MET-WITH-LIMITATION`、`reviewer/author: DSH`、`date`、`reviewed_head`、`inputs`（本文件、FEA-11 卡、四卡证据）、`limitation`、签名。这样 Review 独立性/可追溯与历史字节保留可同时满足。

### 4.3 需登记的 limitation（A+，可直接并入 §4.2）

```text
AC11-1-L-STARTUP（DSH 裁决 2026-11-06，A 解释）：
应用启动不做全量内容扫描。启动期只做冷启动目标枚举与 registry/root 可用性/授权核验
（FEA-11-SCAN-2），随后由周期全量扫描（FEA-11-SCAN-1，默认 900s，可配 [60,86400]）
与 watcher hint（FEA-11-WATCH-1）承担后台发现；任何访问/读取/操作前仍有 live grant +
stable lease + digest 强验证（失配 typed 阻断）。
因此关闭期间发生的外部变化，最迟在下一周期或下一次访问/操作时被发现；
不承诺应用启动即发现。若产品要求更低延迟，另立可选卡（非 AC11-1 前置）。
```

### 4.4 STATUS / PLAN / LEDGER 最小更新建议

仅文本替换/追加，不触碰历史证据字节：

| 文件 | 行 | 现状 | 建议 |
|---|---|---|---|
| `doc/STATUS.md` | `:7` | “`FEA-11-WATCH-1` `done`（…AC11-1 仍 PARTIAL）” | 删去“AC11-1 仍 PARTIAL”，并在同段追加：“AC11-1 已于 2026-11-06 终态裁决为 MET（带 limitation：启动不做全量内容扫描；最迟 900s 或下次访问/操作发现；见 `FEA-11` Closeout 补充）。” |
| `doc/STATUS.md` | `:10` | “先对 RENDITION-1 做 scope review（AC11-1 仍 PARTIAL）” | 改为“先对 RENDITION-1 做 scope review（AC11-1 已终态 MET，带 limitation）”。 |
| `doc/REBASELINE_PLAN.md` | `:13` | SCAN-1 行“AC11-1 仍 PARTIAL” | 改为“AC11-1 终态 MET（带 limitation，2026-11-06）”。 |
| `doc/REBASELINE_PLAN.md` | `:52` | “AC11-1 仍 PARTIAL” | 同上（终态 MET，带 limitation）。 |
| `doc/REBASELINE_PLAN.md` | `:54` | DAG 行 | 无需改（无 AC 字段）。 |
| `doc/TASK_LEDGER.md` | — | 由脚本生成，无 AC 字段，当前无 FEA-11 非终态行 | 编辑 `FEA-11.md` 后重跑 `python tools/governance/task_ledger.py --write`；预期无实质 diff（status/计数不变），以脚本输出为准。 |

门禁建议（Lead 执行）：`check.ps1 -TaskPath doc/tasks/FEA-11.md`、`check.ps1`、`verify_pins.ps1`（18/18）、`task_ledger.py --write`；追加文本不触碰 `verification/**`，无需重跑 pytest/.NET。**注意**：若有人把 AC 行改成 `[x] <<MET>>`，`check.ps1:838-841` 会要求删除原因文本并保持 `[x]`，这与“历史字节保留”冲突——这正是推荐“补充而不改行”的原因。

## 5. 若 Lead 选 B

### 5.1 AC11-1 保持 `PARTIAL` 的 limitation 文本（可直接追加到 FEA-11 Closeout 补充）

```text
AC11-1-L-STARTUP（DSH 裁决 2026-11-06，B 解释）：
「启动/访问前检查」按「启动时对全部已注册源执行全量内容扫描」解释时，
现有实现只提供冷启动扫描目标枚举与启动期 registry/root 可用性/授权核验
（FEA-11-SCAN-2），并在 Ready 后一个周期（默认 900s）才执行首次周期扫描；
没有启动全量内容扫描。AC11-1 保持 PARTIAL，由 FEA-11-STARTUP-SCAN-1 承接；
该卡 done 前不得在 STATUS/PLAN/Handoff/UI 宣称「启动即发现变化」。
访问/读取/操作前强验证继续有效，不因该缺口而使用旧绑定读取变化后的内容。
```

### 5.2 `FEA-11-STARTUP-SCAN-1` 范围草案（供 Lead 建卡；未创建）

| 项 | 草案 |
|---|---|
| id / title | `FEA-11-STARTUP-SCAN-1`：启动后一次性只读全源扫描（承接 AC11-1「启动」全量扫描解释） |
| kind / status | implementation / `proposed`（须先独立 scope review；不得直接 ready） |
| depends_on | `FEA-11-SCAN-1`（done）、`FEA-11-SCAN-2`（done）、`FEA-11-WATCH-1`（done） |
| 目标 | Host Ready 且冷启动枚举尝试完成后，对当前 target 集执行**一次**只读 `ScanSourceSync` pass（受预算/退避/单飞/停机取消），结果只进 `SourceScanStatus`；不建 plan/apply、零 Core 业务写、不改 900s 周期语义。 |
| In（建议） | ① `SourceScanScheduler` 新增一次性 startup sweep 入口（幂等/one-shot；在枚举完成回调后触发，枚举不可用则跳过并 typed 记录）；② 复用 SCAN-1 executor/预算（默认 8 目标/256 MiB；超限 defer 到后续 tick）；③ 与 watcher hint/tick 单飞/优先级；④ `SourceScanStatus` 增 `InitialSweep` 子状态（计数/结果/是否完成，无路径）；⑤ fake clock 零 sleep 单测 + gated HostRuntime 测试（Ready→枚举→初始 pass，首个 `ScanSourceSync` 早于 900s）；⑥ 证据 `verification/FEA-11-STARTUP-SCAN-1/**`。 |
| Out | C-01b/C-17/C-16/C-15/C-06/M2-C1/ADJ-001/FEA-01 任何字节；schema/wire/capability/依赖；watcher 语义变更；枚举重写；plan/apply/删除/GC/UI/通知；真实用户数据；push。 |
| 与 SCAN-1 的边界 | 只新增“一次性初始 pass”；**不改** SCAN-1 的 900s 周期、预算/退避/单飞/零写语义；卡内须明文声明“`FEA-11-SCAN-1.md:183` 的‘首次 tick 在一个间隔之后’仍是周期语义；初始 pass 是独立的一次性 pass”。 |
| 与 SCAN-2 的边界 | 只消费枚举/合并后的 target 集；不重新枚举、不铸 grant、不发明 target。 |
| AC（建议） | S-1 one-shot（进程内只跑一次，重复 Ready/Refresh 不重复）；S-2 触发时序（不阻塞 Ready；枚举完成后触发；枚举失败 typed skip 不重试风暴）；S-3 预算/defer（>8 目标或 >256 MiB 跨后续 tick，不丢）；S-4 单飞（不与 watcher hint/周期 tick 重叠）；S-5 零写（fake core 命令集合精确 `{ScanSourceSync}`；14/15 表快照相等）；S-6 停机取消/Dispose join；S-7 脱敏；S-8 门禁/回归（pytest/.NET/pins/check/scope diff）；S-9 回填输入（AC11-1 终态复议）。 |
| 风险 | 启动 IO 峰值/大库成本未标定；网络盘/可移动盘；与 watcher 首事件/周期 tick 的竞态（单飞覆盖）；测试计时脆弱（用注入时钟，不 sleep）；对 SCAN-1 冻结行为的“范围变更”争议（必须先 scope review 明确）。 |
| 契约影响 | 预期**零字节**：C-01b SC-25 不要求启动扫描，但也不禁止新增检测通道；若 Lead 认为需要把“启动扫描”写入冻结契约，才走 UNFREEZE（不推荐，成本高且与 A 的结论冲突）。 |

## 6. 必须由 Lead/用户裁决的点

> 归属划分（建议）：**Lead（DSH）裁决** 3/5/6/7 与 1 的技术口径；**用户必须明确确认** 1（终态由 PARTIAL 改 MET，涉及已关闭卡与冻结条款解释）；**用户决定** 2（是否授权改写历史 AC 行）与 4（可选启动扫描卡的产品优先级）。

1. **A vs B（核心）**：建议 Lead 采 **A+**。由于这会把一个已关闭卡的 AC 终态从 `PARTIAL` 改为 `MET`、并宣布 C-01b SC-25 `[新增]` 条款已兑现，**建议取得用户明确确认**（与 `FEA-11-r7-acceptance` 的用户裁决先例一致）；若用户完全不介入，至少由 DSH 以裁决记录 + Closeout 补充留痕。
2. **AC 行字节处置**：保持 `- [ ]` + 双 `<<PARTIAL>>`（推荐，符合“不得改历史 AC 行字节”）；若用户要求机检显示 `MET`，必须显式授权**改写历史 AC 行**（同时删除 marker 原因，违反当前字节保留规则，且与 `check.ps1` 的 MET 语义一致但代价大）。
3. **是否新建独立裁决文件** `doc/reviews/FEA-11-AC11-1-adjudication-2026-11-06.md`（推荐）；本输入文件不能替代裁决。
4. **是否现在建可选启动扫描卡**（`FEA-11-STARTUP-SCAN-1`）：采 A 时它不是 AC11-1 前置；由用户产品优先级决定（与 RENDITION-1/L10 排序）。若采 B，则它是 AC11-1 的必然后续，须先 scope review。
5. **契约解释的落点**：A 下建议**不改 C-01b/C-17 字节**，只用裁决记录解释；若 Lead 认为必须在契约文本中写明“启动=枚举/核验”，则需 UNFREEZE（不推荐）。
6. **STATUS/PLAN 文案**：是否按 §4.4 的最小替换执行；`doc/handoffs/DSH-HANDOFF-2026-11-06.md` 属历史快照，建议**不**回改。
7. **证据归档**：`FEA-11-SCAN-1-scope-r1.md` 在仓库中**不存在**；SCAN-1 的 scope review 只在仓外 `G:\CODEX\New Manga.workspace\FEA-11\scope-review\FEA-11-SCAN-1-scope.md`。本裁决引用它时只能标注“仓外、不可 pin”。Lead 可决定是否将其归档为仓内副本（单独治理动作，本子代理未创建）。

## 7. 未运行 / 限制

- 未运行 pytest / `dotnet test` / `check.ps1` / `verify_pins.ps1` / `task_ledger.py`（只读裁决输入；运行会引入工作区状态变化或与只读约束冲突）。测试结论来自测试源码**静态核对**与各卡 closeout 的**既有实跑记录**（`FEA-11-SCAN-1` 7080167e1、`FEA-11-SCAN-2` 555f57b8d、`FEA-11-WATCH-1` 00083a977）。
- 未逐字节复核 C-01b/C-17 全文；引用其冻结记录 pin 与关键条款行。
- 未检查 `FEA-11-SCAN-1-scope-r1.md` 的仓内不存在是否为归档遗漏；仅记录事实。
- 本文件是**输入**；最终裁决、STATUS/PLAN/LEDGER 修改与任何卡面回填均属 Lead 动作。

---

AC11-1-ADJUDICATION: A+ — 采“访问前=读取/操作前 live grant+lease+digest 强验证、启动=冷启动目标枚举+registry/root 核验”的解释，AC11-1 判 MET（带 limitation：启动不做全量内容扫描；最迟默认 900s 周期或下次访问/操作发现变化），以 FEA-11 Closeout 补充 + 独立裁决记录回填，不改历史 AC 行字节；若用户改判 B，则 AC11-1 保持 PARTIAL 并另立 FEA-11-STARTUP-SCAN-1。
