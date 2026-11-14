---
verdict: REJECT
task: READER-PREF-PERSIST
review_round: r1
reviewer: review-reader-pref（独立上下文子 agent，未参与本卡实现）
target_head: 57f149b0215241affe3f9a1f97ab37638946f469
base: eebfedf6d
review_date: 2026-11-15
mode: 只读复核（仓库内仅写本报告）
---

# READER-PREF-PERSIST 独立复核 r1

## 0. 审查者身份与来源

- 审查者：`review-reader-pref`，由 DSH 主会话派发的**独立上下文子 agent**（会话/subagent 名即上文标识）。
- 未参与本卡实现、未参与返修；复核期间未修改仓库源码、未提交、未 push。
- 被审 head：`57f149b0215241affe3f9a1f97ab37638946f469`（`feat(reader-pref-persist)`），基线 `eebfedf6d`。
- 复核方式：读 diff + 读代码 + 在**隔离沙箱**（`git archive HEAD` 解包到 `G:\CODEX\New Manga.workspace\review-reader-pref-head\`，blob 哈希与 HEAD 逐一对齐）跑测试与变异实验；未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR`；未跑全量 App.Tests。

## 1. 结论

**REJECT**。方向正确、AC7 干净、AC2/AC5 的 VM 语义与判别测试站得住；但存在一处 P1 级"在途保存丢更新"（用户第二次改的值永远进不了 Core，正是 E-4 的症状在竞态窗口里复现），AC4 要求的"控件路径判别测试"并不成立（把 `ReaderPageView.cs` 整体回退到基线后 17/17 仍全绿），另有一处偏好入口（页面双击）未接线；且复核期间工作区存在**实现者未提交的改动与 1 个失败测试**，被审 head 与可运行树不是同一份内容。上述任一项都不满足集成条件。

## 2. 逐 AC 判定

| AC | 判定 | 依据与实测 |
|---|---|---|
| AC1 单双页持久化 | **PARTIAL** | 顶栏按钮已接 `ToggleDoublePagePersistingAsync`（`ReaderPageView.cs:275`），VM 队列有判别测试（实验 A 变红）。但 `ReaderPageView.cs:180` 的**页面双击**仍是 `_viewModel.ToggleDoublePage()`，改内存不保存；"重开读回一致"未做端到端验证（sidecar 早于该命令，E-2）。 |
| AC2 方向持久化 | **PASS**（写路径） | 两处入口（`:276`、`:396`）都接 `ToggleDirectionPersistingAsync`，View 内已无 `ReverseDirection = !...` 残留；实验 A 中该测试变红，判别有效。"重开读回"同样未端到端验证。 |
| AC3 缩放持久化 | **PARTIAL** | 浮动条/底部条/键盘共 7 处入口全部改接（`:393-395`、`:420-422`、`:712/717/722`），无 `ZoomBy(`/`ResetZoom()` 残留；但测试不覆盖控件路径（实验 B），且存在 P1-1 在途丢更新。 |
| AC4 判别测试（控件路径） | **FAIL** | 新测试只调用 VM 的 `*PersistingAsync`（`ReaderPreferencePersistenceTests.cs:43-147`），从不同构造/点击 `ReaderPageView`；把 `ReaderPageView.cs` 换回基线 blob `94ef2163` 后，三个测试类 **17/17 全绿**（实验 B）。AC4 明确要求"断言控件路径确实产生了 Patch"，未满足。 |
| AC5 失败可见 + 不改快照 | **PARTIAL** | 失败分支正确：`ReaderViewModel.cs:196-205` 先 `return` 再写快照，`_appliedPreferences` 未被污染；测试有判别力（实验 A 中两个失败测试变红，且用 1.7 而非 1.5 规避"跳过当已存"假阳性）。但 View 绑定无任何测试（`PreferenceSaveStatusText` 全仓测试零引用）；切书后状态不清（P2-2）。 |
| AC6 不做过量写入 | **PARTIAL** | 合并实现成立（真实异步下 6 连点 1–2 次写入）；但测试**非判别**：去掉全部 `QueuePreferenceSave()` 后 0 次写入仍满足 `<= 2`，实验 A 中唯一通过的测试就是它（P2-4）。首写固定延迟 80ms。 |
| AC7 契约零变化 | **PASS** | `git diff --name-status eebfedf6d..HEAD` 仅本卡允许路径（2 个 App 源文件、2 个测试文件、4 个治理文档、任务卡与证据）；无 wire/DTO/Core；`python tools/generate_api_inventory.py --check` exit 0、`1/80/6=87`；`Skip =` 源级 11→11；`check.ps1` PASS(3 warnings)；`verify_pins.ps1` 18/18；沙箱 `dotnet build -warnaserror` 0 警告/0 错误。 |
| AC8 不回归 | **未验证（我未跑全量）** | 定向（偏好 6 + READ-2 偏好 7 + 可见控件 4）在 HEAD 沙箱 **17/17** 通过；证据日志称全量 `940/0/11`，但该日志时间戳（00:12:33）**早于** HEAD 提交（00:12:48）且未 pin commit。复核时工作区另跑一次定向为 **17/18（1 红）**，见 §5。 |

## 3. Findings

### P1-1 在途保存丢更新：第二次改动的值被记成"已保存"，永远不进 Core
- 位置：`apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/ReaderViewModel.cs:193-204`（HEAD 行号；`patch` 于 :193 由当时值构造，`:195` await，`:204` 用 **await 之后的当前值** 写 `_appliedPreferences`）。
- 证据：沙箱探针（仅沙箱，未入库）把 `FakeHostController` 的保存挂成可阻塞 Task：先 `ZoomByPersistingAsync(0.5)` 让写 1.5 在途，在途期间再 `ZoomByPersistingAsync(0.2)`（显示 1.7），放行后等待排空，再显式 `SaveReadingPreferencesAsync()` —— 结果 `LastSavedPreferences.Zoom = 1.5`（期望 1.7），`_appliedPreferences` 已记为 1.7，第二轮 diff 为空、不发写。测试失败输出：`Expected: 1.7 ... Actual: 1.5`（`ReviewProbeTests.Probe_InFlightSecondChange_IsNotLost`）。
- 影响：真实 Host 是异步 IPC（`HostController.cs:440` 起 `await runtime.Save...`），用户在首写 80ms 延迟 + wire 延迟窗口内再点一次（快速连点很常见）时，第二次增量**静默丢失**；重启后回到第一次的值——与 E-4 用户可见症状相同。现有测试用同步完成的 fake，结构性看不到此问题。
- 建议：快照记录"实际发出的 patch 值"（`mode/zoom/doublePage/layout` 在构造 patch 时固化，如 `direction` 已做的那样），而不是 await 后回读 VM；或仅在 `_preferenceDirty == false` 时提交快照。补一个门控 host 的判别测试。

### P1-2 AC4 名不副实：生产接线（View）零测试覆盖；双击入口未接
- 位置：`ReaderPageView.cs:180`（双击 → `ToggleDoublePage()`）；测试 `ReaderPreferencePersistenceTests.cs:43-147` 全部直接调 VM，`ReaderVisibleControlsTests` 对缩放/单双页/方向零断言（grep 无 `Zoom|DoublePage|Reverse`）。
- 证据（实验 B）：把 `ReaderPageView.cs` 替换为基线 blob `94ef2163eb833da15d5c38b3487dad0691009fbb`（即 E-4 原始缺陷：`ZoomBy`/`ResetZoom`/`ToggleDoublePage`/`ReverseDirection =`），三个测试类 **17/17 全绿**。也就是说，本卡真正修好的那一层可以被整体回退而不触发任何红灯。
- 影响：AC4 不成立；未来任何一次 View 重构都可能在不惊动测试的情况下复发 E-4。双击入口今天就已经漏接：双击页面切单双页 → 内存变了、Core 不变，且不给任何提示。
- 建议：在 `ReaderVisibleControlsTests`（已有 Avalonia UI 线程 harness）里点击真实按钮/触发 `DoubleTapped`，断言 `SaveReadingPreferencesCallCount` 与 `LastSavedPreferences`；把 `:180` 改为 `ToggleDoublePagePersistingAsync`（或明确登记为不持久化手势）。

### P1-3 被审 head 与工作区不一致：未提交修复 + 1 个红灯
- 证据：HEAD 提交后（00:12:48），工作区出现 4 个未提交改动（记录于 00:20:59）：
  - `ReaderViewModel.cs`（sha256 前缀 `8A3B3754F231`，含"pin 目标书"守卫）
  - `FakeHostController.cs`（`B9682305001E`，新增 `SaveReadingPreferencesOverride`）
  - `ReaderPreferencePersistenceTests.cs`（`39B97AA711AF`，新增跨书测试）
  - `verification/READER-PREF-PERSIST/README.md`（`2DB7F5285EB5`）
  对该中间态跑定向：**18 个测试 1 失败**，`FailedSave_ForABookTheUserAlreadyLeft_DoesNotPolluteTheNewBook`（`Assert.DoesNotContain("失败", ...)`）。
- 影响：HEAD 不含这些修复；而"可运行的最新代码"又不绿、且无任何证据记录。任何基于 HEAD 或基于工作区的集成结论都会落空。
- 建议：实现者完成修复→提交→重跑定向+全量→把 commit 写进证据与任务卡，再送复审。

### P2-1 排队保存的目标书在写的时候才读取 → 80ms 窗口内切书会写错书
- 位置：`ReaderViewModel.cs:195`（`Book.BookId` 在 await 处求值）、`:226-239`/`:247-268`（队列与 80ms 延迟）。
- 证据：沙箱探针 `Probe_QueuedSaveAfterBookSwitch_TargetsTheOldBook`：在 b1 上 `ZoomByPersistingAsync(0.5)`（进入 80ms 窗口），立即 `LoadAsync("b2","c2")`（b2 无已存偏好 → `ApplyReadingPreferencesAsync` 早退、`_appliedPreferences` 仍是 b1 的），排空后最后一次写调用的 `bookId = "b2"`（记录于 fake 的 `LastSavedPreferencesBookId`），即把 b1 的 patch 记到 b2。测试失败：`Expected: "b1" Actual: "b2"`。
- 影响：与 `CHAPTER-MANUAL-SORT` r1 修过的 F2 同类；真实用户 80ms 内完成"关阅读器→开另一本"概率低，但 80ms 是下限、负载下会更长，且会随 wire 延迟在"在途"分支放大。
- 建议：在 `QueuePreferenceSave()` 里固化 `bookId`（及当时的 patch 语义），drain 只写该 book；切书时清空 `_appliedPreferences` 并（可选）取消在途队列。工作区未提交的修复把 `bookId` 放在 await 前读，仍晚于 80ms 窗口，**不能**修掉本条，其自带的新测试也正因书已切换而变红。

### P2-2 失败状态跨书泄漏，且不会被 Load 清除
- 位置：`ReaderViewModel.cs:201-205` 设置/清空状态；`LoadAsync`（`:344` 起）不重置 `PreferenceSaveStatus`；`ReaderPageView.cs:536-537` 只在 `Render()` 复制。
- 影响：在 A 书保存失败后打开 B 书，底部条仍显示"阅读偏好保存失败…"，误导用户以为 B 的偏好没保存；HEAD 下在途失败还会在新的书上弹提示。反过来，成功保存才会清空。
- 建议：`LoadAsync` 开头清空状态；失败提示只对发起它的书生效（随 P2-1 一起修）。

### P2-3 drain 无异常处理：一次 host 抛错会把保存队列永久卡死
- 位置：`ReaderViewModel.cs:238`（`_ = DrainPreferenceSavesAsync()`，未观察的 Task）、`:266`（`await SaveReadingPreferencesAsync()` 无 try/catch）。
- 影响：`HostController` 只吞 `CoreOperationException/SidecarException/BridgeException/OperationCanceledException/IOException` 并返回 false；其他异常（例如桥接层换型、`ArgumentException`、`ObjectDisposedException`）会从 `SaveReadingPreferencesAsync` 逃逸 → drain 任务 fault，`_preferenceSaving` 永远为 true，**此后所有偏好变更静默丢弃**，且用户看不到任何失败提示（异常未观察）。
- 建议：drain 内 try/catch（记失败状态，必要时重置 `_preferenceSaving`），或用 `ContinueWith` 观测；补一个 host 抛错的测试。

### P2-4 AC6 测试非判别
- 位置：`ReaderPreferencePersistenceTests.cs:132-147`（`Assert.True(count <= 2)`），`SettleAsync` 默认只等 1 次写（`:35-41`）。
- 证据：实验 A 去掉全部 4 处 `QueuePreferenceSave()` 后，该测试 **通过**（0 ≤ 2），其余 5 个测试变红。
- 建议：断言下界（`Assert.InRange(count, 1, 2)`）或先等到"至少 1 次写"再判上界，并断言最后一次 patch 是 1.6。

### P3-1 `SettleAsync` 只等 host 调用，不等 VM 后置状态
- 位置：`ReaderPreferencePersistenceTests.cs:35-41`、断言 `:98/:108/:118/:125`。
- 影响：`SaveReadingPreferencesCallCount++` 发生在 fake 方法内，而 `PreferenceSaveStatus`/`_appliedPreferences` 在 await 续体中赋值；测试线程可能先看到计数就断言（亚微秒窗口，x86 下概率极低，但属于无同步的数据竞争）；且 1s 墙钟上限在负载 CI 上可能超时。建议 VM 暴露"保存已排空"的 Task/事件供测试等待，替换轮询。

### P3-2 卡面与账本未回填/不一致
- 位置：`doc/tasks/READER-PREF-PERSIST.md:52-67`（AC 全未勾）、`:84-91`（测试表全 NOT_RUN，与 `verification/READER-PREF-PERSIST/README.md` §4 的 PASS 自相矛盾）、`:111-121`（Canonical Evidence 空表，证据未 pin commit）。
- 位置：`doc/TASK_LEDGER.md` 改后仍写 "non-terminal tracked by git 6 / untracked (drafts) 1"，但 `READER-PREF-PERSIST` 已在同一提交中被跟踪（`git ls-files` 有、`git status` 无未跟踪），账本数字与树不一致（`check.ps1` 只报 WARN，不校验该列）。
- 建议：收口时统一回填并经 `check.ps1` 复核；证据文件头部加 `commit:` 字段。

### P3-3 离开阅读器/关窗无 flush
- 位置：`ReaderPageView.cs:193-198` 的 `DetachedFromVisualTree` 只停两个计时器；`ReaderViewModel` 无 `Dispose`；`:252` 固定 80ms。
- 影响：最后一次操作后 80ms 内退出/切页，最后一次变更丢失（概率低，但与 E-4 同类）。
- 建议：离开页面时 flush 队列（类似 `FlushScrollProgressAsync` 的既有模式）。

### P3-4 `_appliedPreferences` 不在 `LoadAsync` 重置（既有，被新队列放大）
- 位置：`ReaderViewModel.cs:344-394`（LoadAsync）与 `:146-172`（Apply 在 preferences 为 null 时早退）。
- 影响：切到"无已存偏好"的书时，diff 基线仍是上一本书；与 P2-1 叠加会写错字段。建议 Load 时清空快照。

## 4. 判别力实测（我亲自做的实验）

全部在隔离沙箱 `G:\CODEX\New Manga.workspace\review-reader-pref-head\`（`git archive HEAD` 解包，`git hash-object` 与 HEAD blob 逐一核对：VM `82dd7caaf`、View `c6ee71b0a`、Fake `d306afad6`）执行；**仓库内未改任何文件**。

1. **基线**：`--filter "ReaderPreferencePersistenceTests|ReaderReadingPreferencesTests|ReaderVisibleControlsTests"` → **17 passed / 0 failed**，与证据 README 的 17 一致。
2. **实验 A（正向判别）**：把 4 个 `*PersistingAsync` 里的 `QueuePreferenceSave();` 全部替换为注释 → **5 failed / 1 passed**。失败：`ToggleDoublePage_PersistsTheNewValue`（`LastSavedPreferences` null）、`ToggleDirection_PersistsTheNewDirection`、`ZoomControls_PersistTheNewZoom`、`FailedSave_IsReportedAndNotTreatedAsApplied`、`SuccessfulSave_ClearsTheStatus`；唯一通过的是 `RapidZoomClicks_CoalesceIntoFewWrites`（0 次写入也满足 `<=2`）。→ AC1/AC2/AC3/AC5 的 VM 层有判别力；AC6 无。
3. **实验 B（AC4 证伪）**：把 `ReaderPageView.cs` 整体替换为基线 blob `94ef2163`（E-4 原始接线：`ZoomBy`/`ResetZoom`/`ToggleDoublePage`/`ReverseDirection =`）→ **17 passed / 0 failed**，编译无错误。→ 生产接线可整体回退而不触发任何红灯。
4. **实验 C（两处竞态探针）**：沙箱内临时给 `FakeHostController` 加 `SaveReadingPreferencesOverride`（可挂起写入）与 `LastSavedPreferencesBookId`，新增 2 个探针测试：
   - `Probe_InFlightSecondChange_IsNotLost` → FAIL：`Expected 1.7`，`Actual 1.5`（P1-1）。
   - `Probe_QueuedSaveAfterBookSwitch_TargetsTheOldBook` → FAIL：`Expected "b1"`，`Actual "b2"`（P2-1）。
5. **还原**：探针测试已删除；沙箱内 VM/View/Fake 从实验前 `.orig` 备份还原，`git hash-object` 复核为 `82dd7caaf`/`c6ee71b0a`/`d306afad6` = HEAD blob，**完全一致**。仓库工作区中那 4 个未提交文件是实现者自己的改动（哈希见 P1-3），不是我的实验产物；我除本报告外未写仓库任何文件（`git status` 复核）。
6. **门禁复核（仓库内、只读）**：`generate_api_inventory.py --check` = `1/80/6=87`（exit 0）；`check.ps1` PASS(3 warnings)；`verify_pins.ps1` PASS(18)；`Skip =` 源级 11（base 11）；`-warnaserror` 构建 0/0（沙箱）。

## 5. 复核期间观察到的并发改动（重要）

- 00:12:48 提交 HEAD；00:13:03 起该作者/会话继续改同一文件（工作区变脏，且 00:14:00 后测试文件与证据 README 又变）。
- 我对其工作区中间态跑过一次定向（18 tests）：**1 失败**，失败点正是 `FailedSave_ForABookTheUserAlreadyLeft_DoesNotPolluteTheNewBook`。该测试断言"已离开的书的失败不得污染新书"，说明实现者已意识到切书问题；但其未提交实现把 `bookId = Book.BookId` 放在 **await 前、80ms 延迟之后**，因此仍不能把 patch 定向到正确的书（见 P2-1），测试本身也仍然红。
- 因此本报告的代码判定一律以 HEAD `57f149b` 为准；工作区内容不作为通过依据。

## 6. 我没有验证的面

- **全量 App.Tests 940/0/11 未跑**（约 5.5 分钟，按派单约定跳过大件）；只跑了 17 个定向测试，并核对 skip 源级计数（11→11）。`940` 总数未独立复核。
- **真实 sidecar 端到端未验证**：仓库 sidecar（2026-10-23）早于 `SaveReadingPreferences` 命令（E-2），无法验证"重开读回一致"（AC1/AC2/AC3 的读回半边），也无法验证真实 IPC 延迟下的合并行为。
- **真实 GUI 手动点击未做**：未在 Avalonia 窗口里手动点按钮/双击/键盘操作，只做了代码级与 headless 测试级验证。
- **多线程 UI 上下文未验证**：drain 在真实 UI 线程上的 SynchronizationContext 行为、`Render()` 调用频率与状态文案的可见性，只做了代码阅读（未在真实窗口中观察）。
- **`--shell=legacy` 的旧 `Views/ReaderPage`（hostless VM）未复核**：按 FEA/AD-002 口径它属历史回退路径，不在本卡范围；这也意味着本次修复只覆盖 Fluent 阅读器。
- **未验证深色模式/可见性/无障碍下的状态文案呈现**（View 层无测试覆盖）。

## 7. 能否进入集成？

**不能。** 需至少完成：

1. 修 P1-1（快照记录"实际发出的值"）与 P2-1（在 `QueuePreferenceSave` 固化 bookId、Load 时清快照）；
2. 补 View 级判别测试（点击真实控件 → 断言写入），并接上 `ReaderPageView.cs:180` 双击入口（或登记为手势不持久化）——直接满足 AC4；
3. 修 P2-3（drain 异常处理）与 P2-4（AC6 断言下界）；
4. 工作区清理：把当前未提交修复完成后**提交**，跑定向 + 全量（如实标注环境）并把 commit 写进 `verification/READER-PREF-PERSIST/README.md` 与任务卡，回填 AC/测试表；
5. 由 DSH 重新派独立上下文复审（本报告结论只对 `57f149b` 有效）。
