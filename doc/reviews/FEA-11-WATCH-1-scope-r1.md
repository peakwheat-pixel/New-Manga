---
task: FEA-11-WATCH-1
title: FEA-11-WATCH-1 独立 scope review r1（watcher 必要性首裁 + 范围冻结草案）
reviewer: fresh subagent（独立上下文；未参与 FEA-11/WATCH-1 任何实现；只读）
session: 14af42fa-c7f5-42dd-a317-d6ace300b147
parent_session: session-8db9dae5-49df-4d09-ac62-696f0805a95c
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
worktree: clean
reviewed_head: 919c9aa1ecd7a4eae02c9b5c2bc0dd2adbde0d3f
verdict: NECESSARY
---

# FEA-11-WATCH-1 Scope Review r1（独立只读）

> **结论先行：`NECESSARY`（在 AC11-1 与 C-01b SC-25 仍是现行冻结承诺的前提下）。**
>
> - AC11-1 **逐字**把「目录 watcher 生产者路径」列入四路变化检测，并把「丢 hint/overflow 后可全量重枚举检测」写成可验证语义；没有 hint 通道，该条款不可实现、不可测试，AC11-1 只能保持 `PARTIAL`。
> - `C-01b`（FROZEN v5，18 pins 之一）**SC-25** 把「目录 watcher hint」写进冻结的「检测组合」，状态 `[新增]`；`C-17:18` 明确「四路检测是 FEA-11 的实现责任；本契约不替其延期或判定完成」。两处都不是 WATCH-1 可自行取消的软约束。
> - 但 watcher 的**安全价值**不是必需的：SCAN-1 周期全量扫描 + SCAN-2 冷启动枚举 + FEA-11 访问前/操作前强验证已经覆盖正确性；watcher 的实际收益是**检测延迟**（900s/下次访问 → 去抖窗口）与让「丢 hint/overflow」语义成为真值可测。因此本裁决是「**为关闭 AC / 兑现冻结契约而必要**」，不是「没有它产品就不安全」。
> - 若 DSH 决定永久接受该缺口，唯一合法路径是显式 limitation（AC11-1 保持 `PARTIAL`、C-01b SC-25 `[新增]` 留作跨卡债务、WATCH-1 `cancelled`）；那是**范围/契约裁决**，不是本 review 的工程结论。备选文本见 §9。
> - 冻结范围必须**极小且 hint-only**：Host 侧 `FileSystemWatcher` → 单源 due bit → 去抖/合并 → 触发既有 `ScanSourceSync` 全量重枚举；绝不把事件当「已同步/已删除」证据，绝不做增量 diff、不建 plan/apply、不新增 wire/schema/依赖。

---

## 1. 只读核验基线（review 时点）

| 项 | 事实 | 证据 |
|---|---|---|
| HEAD | `919c9aa1ecd7a4eae02c9b5c2bc0dd2adbde0d3f`（`docs(fea-11-scan-2): 补 temp 删除实际字节数…`） | `git log -1` |
| 分支/工作树 | `main` / clean（无 modified/untracked） | `git status --porcelain` |
| 冻结 pins | **18/18 PASS**（含 C01b `3c9f5af7d74f`、C17 `aefa0fa5b17e`） | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` |
| watcher 代码 | **全仓 0 命中**：`FileSystemWatcher`/`ReadDirectoryChangesW`/`InternalBufferOverflowException` 在 `*.cs`/`*.py`/`*.csproj` 均无实现；仅文档提及 | `git grep` |
| 现状扫描栈 | `SourceScanScheduler`（单飞/预算/退避/注入时钟/内存状态）+ `HostSourceScanExecutor`（只发 `ScanSourceSync`）+ SCAN-2 枚举器 + `HostRuntime` 启停接线 | 见 §2.2 代码引用 |
| FEA-11 终态 | `closed_with_limitations`；AC11-1 仍 `PARTIAL`（本次不重开） | `doc/tasks/FEA-11.md:6,103,165,238` |

本 review 未修改仓库、未 commit、未 push；报告写在仓外，由 Lead 落盘。

---

## 2. 风险⑥裁决：watcher 是否必要

### 2.1 AC11-1 原文（逐字）

`doc/tasks/FEA-11.md:103`：

> - [ ] **AC11-1（变化检测与阻断）**：启动/访问前检查、操作前强验证、目录 watcher 生产者路径（本卡两条已测；定时扫描与 watcher 消费者承接 FEA-11-SCAN-1）；丢 hint/overflow 后可全量重枚举检测；相同 mtime/size 但字节变可发现；mtime/size 未变不作内容未变证明；强验证=稳定 lease+digest，不被缓存替代；Dirty 阻断依赖旧绑定的新写入而不是直接换 binding。定时扫描若本卡不做，须由 PREREQ/DSH 裁定并登记承接 Task，不得静默缺失。`<<PARTIAL: 待 scope-r2 冻结逐项断言>>` `<<PARTIAL: 定时扫描/watcher 生产承接 FEA-11-SCAN-1；本卡两条已测路径（定时/消费者承接 SCAN-1）>>`

读法（按原文，不按目标图推断）：

1. **四路**：启动/访问前检查、操作前强验证、**目录 watcher 生产者路径**、**定时扫描**；其中「本卡两条已测」= 前两路；「定时扫描与 watcher 消费者承接 FEA-11-SCAN-1」= 后两路被显式延期。
2. **watcher 不是可选装饰**：它被写成四路之一；「丢 hint/overflow 后可全量重枚举检测」只有在存在 hint 通道时才可验证；没有 watcher，这句话没有对象。
3. 原文只给「定时扫描」写了显式延期条款（须 PREREQ/DSH 裁定并登记承接），**没有给 watcher 写**；watcher 的延期是后续 DSH 裁决与承接链造成的，不是 AC 原文授权。
4. 该 AC 行有两个 `<<PARTIAL>>` 标记（末尾的才是 checker 认可的），第二个原因文字与第一个/正文有时间线冲突；这是已关闭卡的文档瑕疵，本 review 只登记为 P3（§10），**不建议**在未授权情况下改 FEA-11 字节。

### 2.2 承接链与代码事实

| 时点 | 文件/行 | 事实 |
|---|---|---|
| FEA-11 scope-r2 | `doc/tasks/FEA-11.md:139` | DSH 2026-11-04 裁决：FEA-11 首版实现三路（启动/访问前、操作前强验证、**watcher 消费者**消费 hint 并全量重枚举）；只把「定时扫描生产者」承接给 `FEA-11-SCAN-1` |
| FEA-11 验收 | `doc/reviews/FEA-11-r7-acceptance.md:20` | **L-3**：定时扫描与 watcher 消费者未实现（本卡两条路径已测）→ 承接 `FEA-11-SCAN-1` |
| SCAN-1 冻结 | `doc/tasks/FEA-11-SCAN-1.md:83` O-2 | watcher 生产者/消费者 → 登记 `FEA-11-WATCH-1`；SCAN-1 只做「定时扫描 + 丢 hint 后全量重枚举」 |
| SCAN-1 收尾 | `doc/tasks/FEA-11-SCAN-1.md:148,223` | 明确「watcher 消费者」「启动/访问前检查」不承接；L-B「watcher 仍缺」 |
| SCAN-2 冻结 | `doc/tasks/FEA-11-SCAN-2.md:50` | out_of_scope：watcher → `WATCH-1`；SCAN-2 只做冷启动目标枚举 |
| SCOPE-ADJ | `doc/reviews/SCOPE-ADJ-2026-11-05-zcode.md:39` D6 | watcher 另立 `FEA-11-WATCH-1`（proposed）；AC11-1 done 后仍 `PARTIAL`（仅闭合定时扫描半边） |
| FEA-11 补充 | `doc/tasks/FEA-11.md:238` | 「AC11-1（定时扫描/watcher）仍 PARTIAL（不回填 MET）… watcher 与启动扫描未承接，登记 WATCH-1/SCAN-2」 |
| 现状代码 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:20-34,199,314-329,339-442,516-538,620-649,709-742` | 已有：目标 record（含 `Path`，`ToString()` 只暴露 `source_id`）、单实例 loop、单飞 `_tickGate`、注入 `TimeProvider`、预算/退避、内存状态；`Snapshot()` 不含路径 |
| 现状执行器 | 同文件 `:931-1260` | 只对每个 target 做完整 `ScanSourceSync`（1 项目 `scope=current`，多项目 `scope=all`），失败/缺失 typed；从不 plan/apply/delete |
| 现状接线 | `HostRuntime.cs:99-133,1181-1186,1217-1233,1240-1295` | Ready 后创建/启动 scheduler；`StopSidecarsAsync`/`DisposeAsync` 先停 scheduler 再停 Core/host session |
| 现状状态 | `SourceScanStatus.cs:12-36` | closed record；已有 `Enumeration` 子状态；**无** watcher 子状态 |
| 现状 registry | `SourceAccessRegistry.cs:8,54,98-139` | `SourceRoot{Root,VolumeSerial,FileId,Readable}`；`List()` 只读；root 缺失/替换可使 `Load()` 抛 `SOURCE_REGISTRY_UNAVAILABLE` |
| 现状枚举 | `SourceScanScheduler.cs:1483,1570,1635` | `TryMap` 只从 Host registry 取**第一个 readable root** 作为 target path；Core 不返回路径 |

**结论性事实**：watcher 生产者/消费者都没有实现；WATCH-1 是承接链的**唯一剩余占位**（SCAN-1/SCAN-2 都已 done）。但 AC11-1 的「启动/访问前检查」是否等价于「读取时强验证」仍存在解释空间（见 §10 P3）；WATCH-1 完成后**不能自动**把 AC11-1 回填 `MET`。

### 2.3 没有 watcher 时 AC11-1 能否满足？

| AC11-1 子项 | 没有 watcher 的证据 | 判定 |
|---|---|---|
| 启动/访问前检查 | 读取时强验证：`scanner.py:540` `_resolve_grants`（live grant/lease）+ `source_strict_read.py:33-34,58-59`（size+sha256 不符 → `FILE_IDENTITY_CHANGED`）；测试 `tests/fea11/test_source_scan.py:168-186`（撤销 grant typed） | **已覆盖**（按「访问前检查」读法） |
| 操作前强验证（lease+digest） | 同上；FEA-11 AC11-1 测试 | **已覆盖** |
| 定时扫描 | `SourceScanScheduler` 默认 900s、全量 `ScanSourceSync`、预算/退避/单飞；`tests/fea11/test_source_scan.py` + `Fea11ScanIpcTests` | **已覆盖**（SCAN-1） |
| 相同 mtime/size 但字节变可发现 | `tests/fea11/test_source_scan.py:128-165`：同 size 重写 zip → `content_digest` 变、`ambiguous/missing_old`（不伪造 changed） | **已覆盖**（FEA-11） |
| mtime/size 未变不作内容未变证明 | 强验证按 digest，不按 stat；同上测试 | **已覆盖**（FEA-11） |
| Dirty 阻断旧绑定的新写入 | C-17 §6 pending gate / FEA-11 实现 | **已覆盖**（FEA-11） |
| **目录 watcher 生产者/消费者** | 全仓 0 实现；无 hint 通道 | **缺失** |
| **丢 hint/overflow 后可全量重枚举** | 没有 hint，语义无对象；定时扫描的「全量重枚举」只能算兜底的一半 | **缺失** |

**判定**：没有 watcher 时，AC11-1 的**安全/正确性结果**可以由「强验证 + 周期全量扫描 + 冷启动枚举」满足（不会把新内容静默当旧页，变化最迟在下次访问/操作或下次 tick 被发现）；但 **AC11-1 作为逐项 AC 不能判 `MET`**，只能 `PARTIAL`。也就是说：

- 「产品是否会被 watcher 缺失弄错」→ **不会**（正确性有兜底）；
- 「AC11-1 是否要求 watcher」→ **是**（逐字、且与 C-01b SC-25/C-17:18 一致）；
- 「watcher 是否必要」取决于目标是「关闭 AC / 兑现冻结契约」还是「只保证正确性」。本 review 采用前者。

### 2.4 收益 / 成本 / 风险

**收益**

1. 检测延迟从「≤900s 或下次访问」降到「去抖窗口（默认 2s）+ 一个 tick」，让「源已变化」更早成为可诊断状态；对后续 UI/通知切片是前置能力（但本卡不做 UI，L-D 仍在）。
2. 让 AC11-1 的「丢 hint/overflow 后可全量重枚举」第一次成为**可测试语义**（有 hint 才谈得上丢 hint/overflow）。
3. 兑现 C-01b SC-25 的冻结检测组合，避免「冻结条款 `[新增]` 但无承接 Task」的契约债务。
4. 复用已有 scheduler 单飞/预算/退避/注入时钟/脱敏状态，增量成本可控；不新增 wire/schema/依赖。

**成本**

1. 新 Host 组件 + 测试：watcher 生命周期、去抖/合并、overflow/re-arm、状态子记录、HostRuntime 接线；预计 300–600 行生产代码 + 600–1000 行测试（量级估计，供排期参考）。
2. 每个 target 一个 OS 句柄（有 cap）；folder target 递归 watch 可能产生大量事件；需要 buffer/队列/cap 降级。
3. 测试需要真实文件树 + 事件等待；CI 时序不稳定是主要工程成本。

**风险**

| # | 风险 | 说明 | 缓解 |
|---|---|---|---|
| W-R1 | 漏事件/事件合并 | `FileSystemWatcher` 事件可丢、可延迟、可合并；overflow 时只报 `Error` | hint 非真值；周期扫描兜底；overflow → 全量重枚举；测试不断言事件次数 |
| W-R2 | 资源/句柄泄漏 | 每 target 一个 watcher；重复 Start/Stop、refresh 可能泄漏 | 单实例、幂等 Start/Stop、Dispose 计数测试、max watches cap |
| W-R3 | 重复扫描/IO 放大 | 一个保存动作可能产生多次事件；hint 直接 tick 会放大 | 单源去抖 + 合并；一次窗口最多一次 hint-triggered tick；仍受 budget/backoff |
| W-R4 | 路径泄露 | 事件参数含绝对路径/文件名；异常 message 也可能含路径 | 只传 `source_id`；日志/状态只记计数/typed code；脱敏断言 |
| W-R5 | 跨平台/卷类型 | 产品 Windows-only，但 NTFS/网络盘/可移动盘行为不同；网络盘可能不支持通知 | arm 失败 → uncovered + 周期扫描；不崩溃；不假设事件一定到达 |
| W-R6 | 测试脆弱性 | 真实 FS 事件时序不稳定，CI 可能 flaky | 生产逻辑用 fake adapter + 注入时钟做确定性单测；只保留 1–2 条真实树 smoke；flaky 如实登记，不删/不 skip |
| W-R7 | 根范围过宽 | SCAN-2 的 target path 是 registry 第一个 root，可能是父目录；file-kind 但 path 是目录时不知文件名 | file target 仅当 path 是文件时 watch 父目录 + 精确文件名过滤（非递归）；否则 `uncovered`，不猜文件名；folder 才递归 |
| W-R8 | 授权漂移 | 撤销后 target 可能仍在 scheduler（SCAN-2 RH-3 targets 只增不减） | arm 时/同步时用 `SourceAccessRegistry.List()` 复核；撤销/缺失 → 不 arm/拆除；扫描路径本身仍会 typed skip |
| W-R9 | overflow 语义被误解 | 「全量重枚举」受 budget 限制，可能跨多 tick | AC 明写：所有 target 标 due，按 budget 分 tick 完成；状态显示 pending/overflow；不声称一次 tick 完成 |
| W-R10 | 无 UI 消费者 | 收益只是延迟，用户仍看不到「源已变化」 | 卡/Handoff 禁止写「用户可见/已同步」；L-D 保留；UI 另行切片 |

### 2.5 裁决

**`NECESSARY`**。理由按权重：

1. **逐字 AC**：AC11-1 把目录 watcher 生产者路径列为四路之一，并要求「丢 hint/overflow 后可全量重枚举检测」；没有 watcher，这些字句不可实现、不可验证，AC 只能 `PARTIAL`。
2. **冻结契约**：C-01b SC-25（FROZEN v5，pin 之一）把「目录 watcher hint」写进检测组合；C-17:18 声明四路检测是 FEA-11 的实现责任，且契约「不替其延期或判定完成」。取消 WATCH-1 等于让一个冻结的 `[新增]` 条款永久无承接。
3. **承接链闭环**：FEA-11 → SCAN-1 → WATCH-1 的延期链有明确记录；WATCH-1 是唯一剩余占位。若取消，必须把「承接放弃」写成 limitation，而不是把「没做」说成「不必要」。
4. **成本可控**：hint-only 设计不碰 wire/schema/契约/依赖，复用既有 scheduler 的单飞/预算/退避/注入时钟；风险集中在测试与 OS 事件，已有明确的降级路径。

**条件/边界**：本裁决成立于「AC11-1 与 C-01b SC-25 仍是现行承诺」。若 DSH 以显式裁决永久接受该缺口（AC11-1 保持 `PARTIAL`、C-01b SC-25 `[新增]` 登记为跨卡债务、WATCH-1 `cancelled`），则转化为 `NOT-NECESSARY` 的**范围裁决**；该路径的文本见 §9，本 review 不推荐但认为它在治理上可成立。

**优先级说明**：`NECESSARY` 不等于「必须先于 RENDITION-1」。WATCH-1 不是 RENDITION-1 的前置；若用户优先 L10/真实 referenced 图源，可先建/推 RENDITION-1，把 WATCH-1 保持 `proposed`（scope 已冻结），**不要取消**。但一旦释放 WATCH-1，它应当在现有 Host 侧完成，不应再拆成第三个占位。

---

## 3. In / Out 冻结草案（到文件/命令/AC 级）

### 3.1 In

| # | 冻结项 | 文件 / 命令 / 接口 | AC |
|---|---|---|---|
| **I-1** | Host 侧 watcher 生命周期与范围 | 新增 `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs`；`SourceScanScheduler.cs` 暴露内部 target 集快照 + `TargetSetChanged` 回调（在 `_gate` 外触发）；`HostRuntime.cs` 在 Ready 后创建、`StopSidecarsAsync`/`DisposeAsync` 先停 watcher 再停 Core；`HostOptions.cs` 增 `SourceWatchEnabled`；单实例、重入幂等；只对 scheduler 当前 target 中「路径存在 + registry 复核通过」者 arm；Stop/Dispose 后零 hint | AC-W1 |
| **I-2** | hint 语义与去抖/合并 | 事件只映射为 `source_id` 的 due bit；**不携带**路径/entry/change type；单源去抖 `SourceWatchDebounceMilliseconds`（默认 2000，范围 [250, 60000]，可注入）；窗口内 N 次事件合并为 1 次；hint → scheduler 的 hint 入口 → 一次 full `ScanSourceSync`；不新增 wire/命令 | AC-W2 |
| **I-3** | overflow / 丢失 / 根删除/替换 | `FileSystemWatcher.Error`/`InternalBufferOverflowException`/根删除/替换 → 不崩溃；`SourceScanStatus.Watcher` 记 `overflow`/`degraded` 计数；全部 target 标 due，请求一次 full re-enumeration（受 budget/backoff，必要时跨多 tick）；重新 arm；arm 失败 → `uncovered`，周期扫描兜底；不静默丢、不伪造「无变化」 | AC-W3 |
| **I-4** | 与 SCAN-1/SCAN-2 协同 | 复用 `_tickGate` 单飞；hint-triggered tick 不绕过 budget/backoff/pause；hinted target 在 budget 内优先；target 集来自 SCAN-2 枚举 + SCAN-1 注册；不改 `ScanSourceSync` payload/scope；不改 SCAN-1 零写/预算/退避语义；不建 plan/preview/confirm/apply/relink/repoint/resync | AC-W4 |
| **I-5** | 资源 / 隐私 / 降级 | `SourceWatchMaxWatches`（默认 256，范围 1–4096）、`SourceWatchInternalBufferBytes`（默认 65536，范围 4096–65536；`FileSystemWatcher` 上限 64 KiB）、`SourceWatchDebounceMilliseconds`、`SourceWatchEnabled` 均可注入/测试覆盖；超 cap/arm 失败 → `uncovered` 计数 + 周期扫描；日志/状态只含 `source_id`/计数/typed code；无绝对路径/root/文件名/grant/session/异常原文；无新依赖（BCL `System.IO.FileSystemWatcher`） | AC-W5 |
| **I-6** | 测试 / 证据 | 新增 `SourceWatcherTests.cs`（fake watcher adapter + `ManualTimeProvider`）；扩展 `SourceScanSchedulerTests.cs`（hint 排序/单飞/退避/合并）；新增 gated `Fea11WatchHostRuntimeTests.cs`（Ready→watcher 状态、停机）；`verification/FEA-11-WATCH-1/**`；真实隔离文件树 smoke | AC-W1…W5 |

### 3.2 Out

| # | 不做项 | 理由 / 边界 |
|---|---|---|
| **O-1** | 扫描执行本体、周期调度、预算/退避/单飞（SCAN-1） | 只复用/接入，不改语义；`ScanSourceSync` payload/scope 不变（`current`/`all` 规则属 SCAN-2） |
| **O-2** | 冷启动枚举、新 Core 命令/DTO/capability（SCAN-2） | 只消费 target 集；C-17 v1.1 字节不动 |
| **O-3** | 从事件推断增量 diff、「已同步/已删除」、entry/页变化 | 事件只是 hint；`missing` 只能来自 C-17 §5.3 `ScanSourceSync` 结果；不得反推用户意图 |
| **O-4** | 通知/attention/UI/持久化/DB 写；自动 plan/preview/confirm/apply/relink/repoint/resync/tombstone/删除/GC | 零写；UI 后续切片；不代用户决策 |
| **O-5** | Core 侧定时器/反向 RPC/新 capability/wire/schema/migration/新依赖 | Host-only；只用 BCL；不新增 package |
| **O-6** | 冻结契约字节（C-17 v1.1 / C-16 / C-15 / C-01b / C-06 / C-14 / C-13 / C-09 / M2-C1 / ADJ-001 / FEA-01）；18 pins | 只读；`git diff` 必须为空；C-01b SC-25 是「兑现」不是「修改」 |
| **O-7** | App/UI 改动；`IHostController`/`RunContracts`/C-07；`LibraryViewModel.cs` | 本卡不需要 App 改；若编译连带不可避免，Owner 先停下请 DSH `allowed_paths` allowlist 例外（SCAN-2 P2-4 先例），不得静默扩 |
| **O-8** | 真实用户数据/AppData/外部卷/回收站；push | 硬边界 |
| **O-9** | 未注册/未授权路径；file-kind + 目录 root 时猜测文件名；递归 watch 父目录 | 只 watch 已注册 target；file target 只在 path 是文件时 watch 父目录（`IncludeSubdirectories=false` + 精确文件名过滤，事件名再做一次大小写不敏感精确匹配）；否则 `uncovered` |
| **O-10** | 自动重新授权/自动 reset registry/自动改写 Core location auth | 授权仍由 Host/scan 路径校验；watcher 不授权、不写 registry 授权字段 |
| **O-11** | 宣称「用户可见变化/已同步/已修复」 | 仍无 UI（L-D）；卡/Handoff/STATUS 禁止回填这类口径 |

---

## 4. AC-W1…AC-W5（可验证条款 + 判别性测试）

> 命名沿用占位卡 `AC-W1…W5`。每条都要求：**删掉实现/改坏关键分支必须变红**；测试不得以固定 sleep 代替注入时钟；真实文件树用例与 fake adapter 用例分列。

### AC-W1 watcher 生命周期与范围

**冻结判定**：

- 只对 `SourceScanScheduler` 当前 target 中、路径存在、且 **registry 复核通过**的 target 建立 watch；一个 normalized root/path 至多 1 个 watcher；同一 `source_id` 重复注册/refresh 不增加 watcher。
- 复核：enumerated target 用 `SourceAccessRegistry.List()` 校验 `registry_id` 存在、未撤销、`generation` 相等、root readable；App 注册 target 校验存在一个 readable root 包含/等于 path；registry 不可读 → typed `uncovered`，不 arm，不崩溃（L-S1 口径）。
- file-kind target：仅当 `target.Path` 是文件时 watch 其父目录（非递归、`Filter`=精确文件名，事件名再做一次大小写不敏感精确匹配）；`target.Path` 是目录 → 不 watch，`uncovered`（不猜文件名）。folder target：watch 该目录，`IncludeSubdirectories=true`。
- 不 watch 未注册/不存在/已撤销（arm 时）的路径；不 watch 任意用户目录。
- 生命周期：`Start` 幂等（重复不产生第二套 watcher）；`Stop`/`Dispose` 幂等，Stop 后零 hint；Host 停机顺序 watcher → scheduler → host session/Core；重入无异常。

**判别性测试**：

1. fake factory 记录 `(path, IncludeSubdirectories, Filter)`：注册 2 target（1 file、1 folder）→ 2 watcher，file 非递归/带 filter，folder 递归；重复注册同一 `source_id` → 仍 1。
2. registry 撤销/缺失/generation 漂移 → 不 arm；refresh 后已 arm 的撤销项被拆；registry 读失败 → `uncovered`，周期扫描仍跑。
3. `Start×2` → 1 套；`Stop×2`/`Dispose×2` → 0；Stop 后写文件 → 0 hint/0 scan；停机时有在飞 scan → join 有界、无未观察异常。
4. file-kind + 目录 root → 0 watcher、`uncovered` 计数 +1（判别：若实现猜测文件名/递归父目录，此测试变红）。
5. HostRuntime gated smoke：Ready 后 `SourceScanStatus.Watcher.Enabled=true`，`RegisterSourceScanTarget` 后 `Active` 计数增加；Stop 后 `Active=0`（允许组件级覆盖，见 §10 HostRuntime seam）。

**证据**：`SourceWatcherTests`、`SourceScanSchedulerTests` 扩展、gated `Fea11WatchHostRuntimeTests`、`verification/FEA-11-WATCH-1/logs/**`。

### AC-W2 hint 语义与去抖/合并

**冻结判定**：

- 事件处理器只做「映射到已注册 `source_id` → 置 due bit」；**不**把 `FullPath`/`ChangeType`/`Name`/entry/大小传给 scheduler 或状态；不因事件推断 diff。
- 单源去抖窗口可注入（默认 2000ms，范围 [250, 60000]）；窗口内 N 次事件合并为 **1** 次 hint；窗口结束后下一次事件再形成 1 次。
- hint 只触发一次 **full** `ScanSourceSync`（该 source 的全量重枚举），受 budget/backoff/pause/单飞约束；不得改用增量/diff。
- hint 不设置 `last_result`；`last_result` 只能来自 scan 结果；无实际变化时 hint 触发的 scan 必须得到 `ok`，不得写成 `changed`。
- 丢失 hint（无事件）仍由周期 tick 扫描到；hint 不是唯一真值。
- 状态只记 `last_hint_at`/hint 次数/去抖计数；不含路径。

**判别性测试**：

1. fake adapter 1 个窗口内 raise 5 次 → 推进注入时钟 → 恰好 1 次 `ScanSourceSync`；窗口后再 raise → 2 次。
2. 无事件、推进时钟 900s → 周期 tick 仍扫描该 source（丢 hint 兜底）。
3. 事件携带路径/文件名 → 断言 scheduler 收到的参数/日志/状态中不含路径子串；同一 source 的 hint 只按 `source_id` 计数。
4. 内容未变 + hint → scan 结果 `ok`；断言 `last_result != changed`（判别：把 hint 当 changed 即变红）。
5. 未注册 source 的事件 → 忽略，不 scan、不报错。

**证据**：`SourceWatcherTests`（fake adapter + `ManualTimeProvider`/`ManualTimer`，沿用 `SourceScanSchedulerTests.cs:20-130` 的模式）、`SourceScanSchedulerTests` 扩展。

### AC-W3 overflow / 丢失 / 根删除/替换

**冻结判定**：

- `FileSystemWatcher.Error`（含 `InternalBufferOverflowException`）、根目录删除/重命名/替换、watcher 句柄失效 → **不崩溃**；状态记录 `overflow`/`degraded`（计数/typed code，不含路径）。
- overflow/未知失效 → 将**当前全部 target** 标 due，请求一次 full re-enumeration；该 pass 仍受 `MaxTargetsPerTick`/backoff/pause 约束，允许跨多 tick 完成；状态显示 pending/overflow，不声称「一次 tick 完成」。
- 重新 arm；arm 失败 → `uncovered` 计数，周期扫描继续；不得静默忽略、不得伪造「无变化」。
- 不因事件 tombstone/删页/改 binding；`missing` 仍只能来自 `ScanSourceSync` 的 C-17 §5.3 结果。

**判别性测试**：

1. fake adapter raise `InternalBufferOverflowException` → 无未观察异常；`Watcher.OverflowCount≥1`；10 targets/budget 4 → 推进时钟后 3 个 tick 全部扫描；扫描后 pending 清零。
2. fake 根删除/重命名 → 重新 arm 或 `uncovered`；degraded 状态可见；周期扫描仍能给出 `missing`（真实 Core 用例可选，组件级 fake 足够）。
3. re-arm 失败（路径不存在）→ `uncovered` +1，不崩溃，后续 tick 仍扫其他 target。
4. 断言 fake core 命令集合仍只有 `ScanSourceSync`（无 plan/apply/delete）。

**证据**：`SourceWatcherTests`（fake error/根删除）、`SourceScanSchedulerTests` 扩展、脱敏日志断言。

### AC-W4 与 SCAN-1/SCAN-2 协同（单飞/预算/退避/零写）

**冻结判定**：

- hint-triggered tick 与周期 tick 共用 `_tickGate`：在飞时 hint **合并**、不排队、不并发；tick 结束后最多补跑 **1** 次 replay（沿用 `_refreshPending` 模式，不能无限链式）。
- budget：hinted target 在预算内**优先**；backoff 中的 target 不因 hint 提前扫描（保留 due bit，退避到期后再扫）；paused/disabled → 不扫描，恢复后处理 due bit。
- 零写：fake core 每 tick 收到的命令集合**精确等于** `{ScanSourceSync}`；不得出现 `PlanSourceSync`/`Preview*`/`Confirm*`/`Apply*`/`Relink*`/`Repoint*`/`Resync*`/`Acknowledge*`/`Recover*`；不建 plan/operation/receipt。
- 不改 `ScanSourceSync` 的 `scope`/`kind`/`project_ids`/`grant_ids` 选择；不改 SCAN-1 的 0-write/预算/退避语义；不改 SCAN-2 的目标集合并/枚举。
- 不把事件当「已同步/已删除」证据；`last_result` 只来自 scan。

**判别性测试**：

1. `TaskCompletionSource` 卡住第一次 scan → 再发 hint + `TickAsync` → 第二次 `TickAsync` 返回 `false`（合并）；释放 → 该 source 最多 2 次扫描（在飞 1 + replay 1），不并发。
2. 10 targets/budget=4，hint 第 10 个 → 第一个 tick 扫描它（hinted 优先）；其余按原 budget 游标。
3. 失败退避中的 target + hint → 退避期内 0 次；推进时钟过期后 1 次。
4. paused + hint → 0 次；resume 后 1 次。
5. fake core 命令集合精确断言；wire 不含 plan/apply；`page_bindings`/业务表零写（组件级 fake；真实 DB 零写由既有 SCAN-1/2 IPC 证据覆盖，WATCH-1 不新增 IPC）。

**证据**：`SourceScanSchedulerTests` 扩展（复用 fake executor/`ManualTimeProvider`）、`SourceWatcherTests`。

### AC-W5 资源/隐私/门禁/回归

**冻结判定**：

- `SourceWatchEnabled`、`SourceWatchMaxWatches`、`SourceWatchInternalBufferBytes`、`SourceWatchDebounceMilliseconds` 可注入；非法值 fail-safe（回落默认，不使 Host 启动失败）；超 cap/arm 失败 → `uncovered` 计数，不崩溃；`InternalBufferSize` 在 [4096, 65536]（超 64 KiB 会抛，必须夹紧）。
- 日志/状态/异常文本：只允许 `source_id`、结果枚举、计数、typed code；禁止绝对路径、root、文件名、`source-` grant id、`host_session`、异常 `Message`/堆栈、凭据。`SourceScanStatus.Watcher` 序列化后不得含盘符/路径。
- `dotnet test` 全量不减少（review 时参考基线：SCAN-2 closeout **1500 passed/0 failed/85 skipped**；释放时须重新实测并在 Handoff 记录 before/after 与 skip 原因，不得直接抄写）；`pytest tests` 不减少（参考 **3212 passed/10 skipped**；本卡零 Python 改动，仍应实跑或明确 NOT_RUN 理由）。
- `verify_pins.ps1` **18/18 PASS**；`generate_api_inventory.py --check` PASS（C-07/`IHostController` 未变）；`check.ps1` PASS；scope diff 0 域外；无新依赖；真实用户数据零触碰；EV/Resource Manifest 完整；独立 Review 与 DSH 集成。

**判别性测试**：

1. max watches=1、2 个 target → 1 armed + `uncovered=1`，不崩溃，周期 tick 仍扫 2 个。
2. buffer 边界（4096/65536/越界夹紧）；debounce 边界（250/60000/非法回落）。
3. `CapturedLog`/序列化状态断言：隔离根路径、文件名、`source-`、`host_session`、异常原文零命中。
4. 门禁：全量 .NET/pytest、pins、API inventory、check、scope diff、changed-files；Handoff 逐项记录 passed/failed/skipped 与 skip 原因。

**证据**：`verification/FEA-11-WATCH-1/logs/**`、`changed-files.txt`、`scope-validation.log`、`gates.log`。

---

## 5. allowed_paths / Owner / Reviewer / 依赖 / 门禁

### 5.1 allowed_paths（建议冻结）

**卡/评审/交接/证据**

- `doc/tasks/FEA-11-WATCH-1.md`
- `doc/reviews/FEA-11-WATCH-1-*.md`
- `doc/handoffs/FEA-11-WATCH-1-*.md`
- `verification/FEA-11-WATCH-1/**`

**Host 生产代码**

- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceWatcher.cs`（新）
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`（改：target 集回调 / hint 入口 / hinted 优先 / 状态子记录；**不得**把 watcher 主体塞进该文件）
- `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanStatus.cs`（改：`Watcher` 子状态，仅计数）
- `apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs`（改：`SourceWatch*` 选项）
- `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`（改：创建/接线/停机顺序）

**Host 测试**

- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceWatcherTests.cs`（新）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanSchedulerTests.cs`（扩展）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11WatchHostRuntimeTests.cs`（新，gated）

**明确不在 Owner 写域（Lead/DSH 维护）**：`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、冻结契约、`FEA-11.md` 历史字节。

**App 路径与 `LibraryViewModel.cs` 先例**：本卡**不需要** App 改动（目标集/生命周期都在 Host）。SCAN-2 的 `LibraryViewModel.cs`（P2-4）是编译连带被 DSH 记录为 allowlist 例外；WATCH-1 若出现同类编译连带，Owner **必须先停下报 DSH 增列 allowed_paths**，不得静默改 App/UI。若实现需要把 watcher 端口拆成第二个新文件，同样先报备，不得静默新增。

### 5.2 Owner / Reviewer

- **Owner：ZCode**（按 ZCode 裁决与用户授权；独立 Feature/长任务实现）。
- **Reviewer：独立上下文 fresh subagent**（不得由实现会话/实现者自审；须记录 session ID 与来源）；Lead 保留 Appointment 与 findings 处置。
- **Lead / Integrator：DSH**（范围冻结、契约/架构裁决、集成验证、push 权限）。

### 5.3 依赖与 base

- `depends_on`：`FEA-11`（`closed_with_limitations`；`ScanSourceSync`/强验证已交付）、`FEA-11-SCAN-1`（done；scheduler/budget/backoff/零写）、`FEA-11-SCAN-2`（done；冷启动目标枚举/registry 核验）。
- `base_commit`：`919c9aa1e`（review HEAD；释放时以 DSH 固定为准）。
- `branch`/`worktree`：null（沿用 SCAN-1/2 的 main 工作树实施）；如需 worktree 由 DSH 创建并登记。

### 5.4 门禁

1. `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` 全量不减少；实测 before/after，passed/failed/skipped 分列，skip 原因逐项记录。
2. `pytest tests` 全量不减少（参考 3212/10；本卡零 Python 改动，仍应实跑或写明 NOT_RUN 理由）。
3. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → **18/18 PASS**。
4. `python tools/generate_api_inventory.py --check` → PASS（`IHostController`/RunContracts/C-07 未变）。
5. `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-WATCH-1.md` → PASS。
6. `git diff --name-only <base>..HEAD` ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`src/infrastructure/sqlite/schema.py` 零 diff。
7. 无新依赖（BCL only）；无真实用户数据/AppData/外部卷/回收站；不 push。
8. EV/Resource Manifest/Handoff/独立 Review/DSH 集成验证；`AC11-1` 是否回填由 DSH 按 §10 解释裁决，**WATCH-1 不自行回填**。

---

## 6. 契约影响（预期零触碰；证据性说明）

| 契约/面 | 是否改 | 证据/说明 |
|---|---|---|
| **C-17 v1.1** | **否** | 不新增命令/DTO/capability/wire；`ScanSourceSync` 字段与 `scope=current/all` 规则不变；`git diff -- doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` 为空；C17 pin `aefa0fa5b17e` 不变 |
| **C-16** | **否** | grant scope / `MissingObservation` 不变；watcher 不铸 grant、不读源；diff 为空 |
| **C-15** | **否** | 无 schema/DDL/binding/版本选择变化；diff 为空 |
| **C-01b** | **字节不变**；SC-25 被**兑现**（不是修改） | C01b pin `3c9f5af7d74f` 不变；`doc/plan` diff 为空；SC-25 `[新增]` 的「目录 watcher hint」由本卡实现 |
| **C-06** | **否** | 授权面不变；watcher 只读 `SourceAccessRegistry.List()`，不授权、不写授权字段；diff 为空 |
| **C-14 / C-13 / C-09 / M2-C1 / ADJ-001 / FEA-01** | **否** | 均在 `doc/plan`/`doc/contracts`，diff 为空；M2-C1 无增量 |
| **18 pins** | **18/18 PASS** | `verify_pins.ps1` 实跑输出；C01b/C17 等 18 项全部 OK |
| **C-07 / API inventory** | **否** | 不改 `IHostController.cs`/`RunContracts.cs`/`FEA-C07_API_INVENTORY.md`；`generate_api_inventory.py --check` PASS |
| **Schema / migration / 依赖** | **否** | 无 `src/infrastructure/sqlite/schema.py` diff；无 csproj/package 变更；`FileSystemWatcher` 属 BCL |

**结论**：WATCH-1 是 Host 侧行为切片，预期**零契约字节、零 schema、零依赖、零 wire**；18 pins 数量与值均不变。唯一与冻结契约的关系是「兑现 C-01b SC-25」，而不是「修改」。

---

## 7. 与 SCAN-1 / SCAN-2 的边界（必须冻结的口径）

1. **hint 只触发全量重枚举，不做增量判定**：watcher 事件只置 due bit；真正的事实来自 `ScanSourceSync` 的全量 scan/diff。不得从事件路径/类型/名称推断「哪页变了/是否已同步/是否已删除」。
2. **事件永不作为 `missing` 证据**：`missing` 只能来自 C-17 §5.3 的 `ScanSourceSync` 结果（或 Host 的 `MissingObservation` 路径）；watcher 的根删除/重命名只触发一次重枚举，不 tombstone、不删页、不改 binding。
3. **不改 SCAN-1 语义**：tick 仍是唯一 `ScanSourceSync` 生产者；单飞/预算/退避/pause/零写不变；hint 只是「更早触发一次 tick + 在预算内优先」。
4. **不改 SCAN-2 语义**：target 集仍由 Core 枚举 + Host registry 核验 + App 刷新合并；`source_id` 权威、`project_ids`/scope 规则不变；watcher 不重新枚举、不铸 grant、不发明 target。
5. **RH-3（targets 只增不减）不修**：本卡不新增 target 删除语义；若未来加删除，watcher 的拆除是后续卡。当前「已撤销 target 仍可能在 scheduler」由 arm 时/同步时 registry 复核 + scan 路径 typed skip 兜底。
6. **不改变「无 UI 呈现」**：L-D 保留；watcher 只改善内部可诊断状态的时效，不得在卡/Handoff/STATUS 写成用户可见能力。

---

## 8. 风险、limitation 与测试可行性

### 8.1 预登记 limitation（WATCH-1 自身）

- **L-W1**：enumerated file-kind target 若 registry root 是目录（无法得知精确文件名），不 arm watcher → `uncovered`；周期扫描覆盖。不得猜文件名/递归父目录。
- **L-W2**：overflow「全量重枚举」受 budget 限制，可能跨多个 tick；状态显示 pending/overflow，不承诺单 tick 完成。
- **L-W3**：撤销/重授权后，watcher 的拆除依赖 refresh/同步或下一次 hint 复核；在窗口内可能仍有一个已 arm 的 watcher 存在，但不会读内容，scan 会 typed skip；窗口有界（下一次 refresh/同步）。
- **L-W4**：真实 FS 事件测试存在平台/时序 flaky 风险；只保留少量 smoke，flaky 如实登记、隔离复跑，不删测试/不放宽断言。
- **L-W5**：无 UI 消费者；收益是延迟与可测性，不是用户可见功能（L-D 仍在）。
- **L-W6**：大库/多 target 的 handle/事件压力未标定；`MaxWatches`/buffer/debounce 默认值需在真实库上观测后再调（不在本卡做 SLA/benchmark）。

### 8.2 测试可行性

| 层 | 用例 | 环境 | 关键点 |
|---|---|---|---|
| 单元（确定性） | `SourceWatcherTests` | fake watcher adapter + `ManualTimeProvider`（复用 `SourceScanSchedulerTests.cs:20-130` 的模式） | 去抖/合并、overflow、arm/disarm、cap、脱敏；**零 sleep** |
| 单元（调度协同） | `SourceScanSchedulerTests` 扩展 | fake executor + manual clock | hinted 优先、单飞合并、budget/backoff/pause、命令集合精确 `{ScanSourceSync}` |
| 真实文件树 smoke | `SourceWatcherTests` 中的 1–2 条 | `G:\CODEX\New Manga.workspace\FEA-11-WATCH-1\fixtures\...`（`TestWorkspacePaths`），隔离根，无用户数据 | 用 `TaskCompletionSource` + 有界 `WaitAsync`（如 10s）等待 hint；不固定 sleep；只断言「最终到达 + 触发一次 scan」，不断言事件次数；覆盖 file replace、folder add/delete |
| HostRuntime gated | `Fea11WatchHostRuntimeTests` | `HostSidecarFact` + 真实 sidecar（沿用 `Fea11Scan2HostRuntimeTests` 模式） | Ready 后 `Watcher.Enabled`、注册 target 后 `Active` 增加、Stop 后 `Active=0`；**不**把真实 scan 成功作为前提（可用 typed 失败） |
| 门禁 | 全量 .NET / pytest / pins / API inventory / check / scope | 仓库根 | 实测记录；不抄历史数字 |

**关于 CI flaky**：项目已有 `FluentResidual2VisualEvidenceTests`、`RunBinding` 等已知 flaky（SCAN-1/2 记录）；WATCH-1 的真实树事件测试是**新增** flaky 源。建议：

- 生产逻辑不依赖真实 OS 事件（fake adapter 覆盖）；
- 真实树 smoke 只验证「OS 事件→hint→tick」一次，超时给足（10s），失败时日志记录隔离根/事件计数（不含路径）；
- 全量失败时隔离复跑并如实记录，不静默重试成绿；若长期不稳定，登记为 L-W4 并由 DSH 决定是否改为 gated/手动证据，**不得删测试**。

---

## 9. 备选（仅备查）：若 DSH 改判 `NOT-NECESSARY`

> 本节**不是**本 review 的结论；仅当 Lead 以显式裁决永久接受 AC11-1/C-01b SC-25 缺口时使用。若采用，必须在 STATUS/PLAN/LEDGER 与 FEA-11 补充记录中同步，且不得把 AC11-1 回填 `MET`。

### 9.1 AC11-1 limitation 文本草案

```text
AC11-1-L-WATCH（watcher 承接放弃，DSH 裁决 2026-11-06）：
不实现 Host 侧 FileSystemWatcher/hint 通道。变化检测组合由
启动/访问前检查、操作前强验证、周期全量扫描（FEA-11-SCAN-1）与
冷启动目标枚举（FEA-11-SCAN-2）承担；“丢 hint/overflow 后可全量
重枚举”语义不适用（无 hint）。AC11-1 保持 PARTIAL，不得回填 MET；
C-01b SC-25 的“目录 watcher hint”子项保持 [新增] 未实现（冻结字节
不变），登记为跨卡债务。未来若需要 watcher，须新建卡并重新 scope
review，不得以本 limitation 视为已完成。
```

### 9.2 WATCH-1 占位卡处置

- `status: cancelled`；`owner/reviewer` 留空；不进入 READY DAG；`canonical_evidence_status`/`resource_closeout_status` 按取消流程核销（无 worktree/temp 则 `NOT_APPLICABLE`）。
- STATUS/PLAN/TASK_LEDGER 移除「AC11-1 唯一承接」的 Active 指针；FEA-11 的「Closeout 补充」追加 limitation 引用（不改历史字节）。

### 9.3 AC11-1 终态口径

- 无 watcher **不能判 `MET`**；只能维持 `PARTIAL`（FEA-11 已 `closed_with_limitations`，无需重开）。
- 若 DSH 想让 AC11-1 判 `MET`，必须显式修订 AC/路由（治理动作）或重开 FEA-11；不能靠 limitation 自动升级。
- 「启动/访问前检查」的解释仍需冻结（见 §10 P3）：若被解释为「启动全量扫描」，那是另一条未承接路径，WATCH-1 也不能关闭它。

### 9.4 替代主线 RENDITION-1 建卡要点（供 Lead 参考）

- 目标：解决 **L10**——真实 referenced 图源/rendition。现状：page-scope Run/detect 的 `_ManagedPageImageSource` 读 `managed_original_ref`（`core_assembly.py:351-428,388,392`），纯 referenced 页在 `pipeline.py:1433-1434` 被 `TARGET_NOT_FOUND "page … has no managed original"` 拒绝；混合页的 detect 输入仍是旧 Managed Copy 图，不是当前 binding 的 C-17 §7.2 rendition（见 `doc/reviews/FEA-11-LINEAGE-1-r3.md:22,95,109`）。
- 范围要点：新增/接线 C-17 §7.2 rendition-backed image provider；让纯 referenced 页可进入 page-scope Run/ListRegions/导出/渲染（受既有预算/授权/缓存约束）；旧坐标不得无条件下套新图；真实 referenced 页 + 真实 Core 的判别测试；C-08/C-17 §7.2/C-15 契约核对；**不含 watcher**。
- 与 WATCH-1 的关系：互不为前置；WATCH-1 取消与否不影响 RENDITION-1 建卡。

---

## 10. 非阻断观察（P3，供 Lead 处置）

1. **AC11-1 双 marker**：`doc/tasks/FEA-11.md:103` 行末有两个 `<<PARTIAL>>`，checker 只认最后一个；第二个原因文字与正文时间线冲突。FEA-11 已关闭，**不建议**在未授权下改字节；若需澄清，用「Closeout 补充」追加，不改 AC 原文。
2. **「启动/访问前检查」解释**：FEA-11 的「本卡两条已测」通常指「访问前强验证 + 操作前强验证」；SCAN-1 scope review 把「启动/访问前自动扫描」列为未实现，WATCH-1 占位卡又把「启动/访问前扫描策略」列 Out。WATCH-1 冻结时应明确：**本卡不实现启动全量扫描**；「启动/访问前检查」= 既有的读取时强验证；否则 WATCH-1 完成后 AC11-1 仍会因另一条解释而 `PARTIAL`。
3. **RH-3 targets 只增不减**：当前没有 target 删除路径；watcher 拆除测试只能覆盖 refresh/撤销/停机，不能覆盖「target 移除」。本卡不应顺手新增删除语义。
4. **HostRuntime seam**：没有 fake-Core 注入；HostRuntime 级测试只能是 gated smoke（`Fea11Scan2HostRuntimeTests` 先例）。AC-W1 的「随 Host 启停」主要靠组件级 + gated smoke 组合，Review 不得因此判不足。
5. **`SourceScanScheduler.cs` 已 67 KB**：watcher 主体应放新文件；scheduler 只加最小钩子（target 集回调/hint 入口/hinted 优先/状态）。若实现把 watcher 塞进 scheduler，Review 可按可维护性判 P2。
6. **基线数字**：SCAN-2 closeout 的 1500/0/85 与 3212/10 只能作参考；WATCH-1 释放时必须重新实测，不得把历史数字写成 WATCH-1 的实跑结果。
7. **Registry 读失败**：`SourceAccessRegistry.Load()` 在 root 缺失/替换时会抛 `SOURCE_REGISTRY_UNAVAILABLE`（`SourceAccessRegistry.cs:98-139`，SCAN-2 L-S1）；watcher 的 arm/同步必须 typed 降级，不得让 Host 启动失败或产生未观察异常。

---

## 11. 摘要

- **裁决：`NECESSARY`**。AC11-1 逐字要求「目录 watcher 生产者路径」和「丢 hint/overflow 后可全量重枚举」；C-01b SC-25（FROZEN，`[新增]`）把「目录 watcher hint」写进冻结检测组合；C-17:18 声明四路检测是 FEA-11 的实现责任且不替其判定完成。无 watcher 时正确性可由 SCAN-1/2 + 强验证兜底，但 AC11-1 只能保持 `PARTIAL`，且冻结契约条款失去承接。
- **范围**：Host-only、hint-only、零 wire/schema/依赖；watcher 只把事件折叠为 `source_id` due bit，去抖/合并后触发既有 `ScanSourceSync` 全量重枚举；overflow/根删除 → 全量重枚举；事件永不作为 `missing`/同步证据；不做增量 diff、不建 plan/apply。
- **AC-W1…W5** 已给出可验证条款与判别测试：生命周期/范围、去抖/合并、overflow/根删除、SCAN-1 单飞/预算/退避/零写、资源/隐私/门禁。
- **Owner=ZCode**；Reviewer=独立上下文 fresh subagent；Lead=DSH；base `919c9aa1e`；depends_on FEA-11/SCAN-1/SCAN-2。
- **契约影响**：零触碰 C-17 v1.1/C-16/C-15/C-01b 字节/C-06/M2-C1/18 pins；C-01b SC-25 是兑现；`verify_pins.ps1` 18/18 PASS（review 时实测）。
- **备选**：若 DSH 显式接受永久 limitation，可按 §9 取消 WATCH-1 并转 RENDITION-1；这是范围裁决，不是「watcher 不必要」的工程结论。

WATCH-1-SCOPE: NECESSARY — AC11-1 逐字包含目录 watcher 生产者路径与「丢 hint/overflow 后可全量重枚举」；C-01b SC-25（FROZEN, [新增]）把「目录 watcher hint」列入冻结检测组合，C-17:18 声明四路检测是 FEA-11 的实现责任；无 watcher 只能 PARTIAL（正确性可由 SCAN-1/2+强验证兜底，但不能关闭 AC/契约）。建议冻结 §3 In/Out + §4 AC-W1…W5，Owner=ZCode，Reviewer=独立上下文；若 DSH 改为永久 limitation，则按 §9 显式取消并转 RENDITION-1，不得把限制写成「不必要」。
