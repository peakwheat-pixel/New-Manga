# READER-PREF-PERSIST 证据

卡面：`doc/tasks/READER-PREF-PERSIST.md`。基线 commit `eebfedf6d`。

## 1. 缺陷事实（E-4）

- `ReaderViewModel.SaveReadingPreferencesAsync`（`ReaderViewModel.cs:175`）存在且实现了 partial patch，
  但 `apps/desktop-avalonia/src/NewManga.App/**` 生产路径**没有任何调用者** —— 只有测试直接调它。
- `ApplyReadingPreferencesAsync` 由 `LoadAsync`（`:273`）调用，所以偏好**会被读取并应用**；
  缺的是**写回**。用户在阅读器里改单双页/方向/缩放后重启，回到 Core 里的旧值。

## 2. 改动

| 位置 | 改动 |
|---|---|
| `ReaderViewModel.cs` | 新增 `PreferenceSaveStatus`（可见状态）；`SaveReadingPreferencesAsync` 检查返回值（失败时不更新 `_appliedPreferences` 并给文案）；新增 `ToggleDoublePagePersistingAsync` / `ToggleDirectionPersistingAsync` / `ZoomByPersistingAsync` / `ResetZoomPersistingAsync`，均走 `QueuePreferenceSave()`；加锁的 dirty/saving 状态机 + 80ms 合并窗口 |
| `ReaderPageView.cs` | 顶部工具条「单页 / 双页」「反向翻页」、浮动工具条「放大/缩小/适合页面/反向翻页」、底部操作条「缩小/放大/适合页面」、键盘 `+`/`-`/`0` 全部改接 `*PersistingAsync`；新增 `_preferenceStatus` 文本（可见状态）与 `PreferenceSaveStatusText` 测试接缝 |
| `FakeHostController.cs` | 新增 `SaveReadingPreferencesResult`（失败控制）与 `SaveReadingPreferencesCallCount`（写入量计数） |

**未改动**：任何 wire 命令、DTO、Core/`src/**`、偏好语义（字段含义/默认值/partial-patch 规则）。
书签面板、整书进度、reset 确认的既有行为未动。

## 3. 两个实现期发现的真实问题（自登记）

1. **check-then-act 丢保存**：最初用 `_preferenceSavePending` + `_preferenceSaveLoop` 的写法，
   在"循环读到 pending=false → 退出前被置 true"的窗口里会丢掉一次保存（`ZoomControls_PersistTheNewZoom`
   实测暴露为第二次保存不发出）。改为**同一把锁内**判 dirty 与清 saving 的状态机后消除。
2. **合并只在真异步时生效**：`FakeHostController` 的 `Task.FromResult` 同步完成，
   连续 6 次点击产生 6 次保存（`RapidZoomClicks_CoalesceIntoFewWrites` 实测 6 > 2）。
   仅靠"在途标志"无法在同步完成时合并，故加 80ms 合并窗口，使合并不依赖平台异步性。

## 4. 测试

| AC | 测试 | 结果 |
|---|---|---|
| AC1 单双页 | `ToggleDoublePage_PersistsTheNewValue` | PASS |
| AC2 方向 | `ToggleDirection_PersistsTheNewDirection` | PASS |
| AC3 缩放 | `ZoomControls_PersistTheNewZoom` | PASS |
| AC4 判别力 | 去掉 `ToggleDoublePagePersistingAsync` 的 `QueuePreferenceSave()` 后重跑 → **`Assert.NotNull()` Failure: Value is null**（`LastSavedPreferences` 为 null），还原后 PASS | **已实测变红** |
| AC5 失败可见 | `FailedSave_IsReportedAndNotTreatedAsApplied`、`SuccessfulSave_ClearsTheStatus` | PASS |
| AC6 写入量 | `RapidZoomClicks_CoalesceIntoFewWrites`（6 次连点 → ≤2 次写入） | PASS |
| AC8 不回归 | App.Tests 全量（见下） | 见 §5 |

定向合计：`ReaderPreferencePersistenceTests` 6 + `ReaderReadingPreferencesTests` 7 +
`ReaderVisibleControlsTests` 4 = **17 passed**。

## 5. 回归与门禁

见同目录 `four-pieces.log` / `regression.log`（生成后追加）。

## 6. 实现期自查追加（提交 `57f149b02` 之后）

对照 `CHAPTER-MANUAL-SORT` r1 复核修过的同类竞态（F2），本卡自查出同源问题并修复：

- **切书竞态**：`SaveReadingPreferencesAsync` 用 `Book.BookId` 作为目标（await 前求值，因此**写对书**没问题），
  但 await 之后无条件写 `_appliedPreferences`，会让新书的后续 partial-patch diff 拿旧书的快照。
  修复：await 前 pin `bookId`，返回后若 `Book?.BookId != bookId` 则直接返回（不写快照、不打状态）。
- **判别测试**：`FailedSave_ForABookTheUserAlreadyLeft_DoesNotPolluteTheNewBook`
  —— 用 `SaveReadingPreferencesOverride` 把写挂起 → 切到 `b2` → 放行并让旧书的写失败 →
  断言新书不出现"保存失败"文案。**实测去掉守卫后变红**（`Assert.DoesNotContain() Failure: Sub-string found`），
  还原后 7 passed。
- 该测试同时依赖新增的 `FakeHostController.SaveReadingPreferencesOverride`。

## 7. r1 复核处置（**REJECT → 返修**）

复核报告：`doc/reviews/READER-PREF-PERSIST-review-r1.md`（审查者 `review-reader-pref`，未参与实现，
被审 head `57f149b`）。verdict **REJECT**，共 3 P1 / 4 P2。逐项处置：

| finding | 严重度 | 处置 |
|---|---|---|
| **P1-1 在途保存丢更新**：`_appliedPreferences` 用 await **之后**的当前值写快照，patch 却是 await 前构造 ⇒ 写 1.5 在途时改到 1.7，第二次 diff 为空，1.5 永久停在 Core | P1 | **已修**：改为「只记录**实际发送过**的字段」——`mode/zoom/doublePage/layout/direction` 各自 `?? applied ?? intent`。新增 `ChangeMadeWhileASaveIsInFlight_IsStillPersisted`；实测把快照改回"当前值"写法即变红（`Expected 1.7 / Actual 1.5`）。 |
| **P1-2 AC4 不成立**：测试只调 VM；把 `ReaderPageView` 回退到基线 blob，17/17 仍全绿；且页面双击仍走不保存的 `ToggleDoublePage()` | P1 | **已修**：新增 `ReaderPreferenceWiringTests`（4 个 `[AvaloniaFact]`，驱动真实按钮：工具栏单双页/方向、浮动条放大、底部适合页面）；双击入口改接 `ToggleDoublePagePersistingAsync`。实测把工具栏按钮回退成 `_viewModel.ToggleDoublePage` → `Assert.NotNull() Failure: Value is null`。 |
| **P1-3 工作区与 HEAD 不一致**（提交后又改 4 个文件，中间态 17/18） | P1 | **已修**：见本提交；r2 以单一提交送复审。 |
| **P2-1 目标书在写时才读**：80ms 窗口内切书 → b1 的 patch 记到 b2 | P2 | **已修**：改「意图捕获」模型 —— `QueuePreferenceSave` 在**变更那一刻**捕获 `PreferenceIntent(BookId + 全部字段值)`，drain 只用捕获值。窗口内切书也写对书。 |
| **P2-2 失败状态不随 `LoadAsync` 重置** | P2 | **已修**：`ApplyReadingPreferencesAsync` 末尾清空 `PreferenceSaveStatus`。 |
| **P2-3 drain 无 try/catch**：host 抛非契约异常 → `_preferenceSaving` 永久 true，后续偏好全部静默丢弃 | P2 | **已修**：`SavePreferencePatchAsync` 捕获异常并置失败文案后返回，drain 继续。 |
| **P2-4 AC6 测试非判别**：0 次写入也满足 `<=2` | P2 | **已修**：改 `Assert.InRange(count, 1, 2)`。 |
| P3 若干（`SettleAsync` 只等 host 不等续体、卡面 AC 未勾/测试表 NOT_RUN、证据未 pin、flush、`_appliedPreferences` 未在 Load 重置） | P3 | 部分修：`SettleAsync` 增加续体等待窗口；卡面/证据在本轮补齐并 pin；`Load` 重置已随 P2-2 覆盖。**未做**：离开阅读器时的显式 flush（关闭/切页不强制 flush，依赖 80ms 窗口内的保存）。 |

**r2 定向复跑**：`ReaderPreferencePersistenceTests` 8 + `ReaderPreferenceWiringTests` 4 +
`ReaderReadingPreferencesTests` 7 + `ReaderVisibleControlsTests` 4 = **23 passed**。

## 8. r2 复核处置（ACCEPT_WITH_LIMITATIONS，2026-11-15）

复核报告：`doc/reviews/READER-PREF-PERSIST-review-r2.md`（同一独立审查者续接 r2，未参与返修；
被审 `98d42c6b6`）。verdict **ACCEPT_WITH_LIMITATIONS**，**无 P1**；r1 的三项 P1 已逐项实测修复
（P1-1 变红实验 1.5 vs 1.7；P1-2 View 回退基线后 4/4 红；P1-3 工作区 clean）。审查者还独立复跑
App.Tests **946/0/11/957**。

### 已修（最小收口集）

| finding | 处置 |
|---|---|
| **P2-1 意图未带 diff 基线**：80ms 窗口内切到"快照恰好等于待存值"的书 → 这次变更被判无差异、**0 次写入**，旧书修改静默丢失 | **已修**：`PreferenceIntent` 增 `Applied` 字段，`QueuePreferenceSave` 时连同基线一并捕获；保存用 `intent.Applied` 做 diff。新增 `PendingChange_QueuedBeforeASwitchToAMatchingBook_IsStillWritten`；实测改回读当前 `_appliedPreferences` 即变红（"queued change was dropped after the switch (0 writes)"）。 |
| **P3-1 异常路径先置状态后判书**（旧书抛错 → 新书显示失败） | **已修**：catch 内先判 `Book?.BookId == intent.BookId` 再置状态。 |
| **P3-2 切到无偏好书不清状态** | **已修**：`ApplyReadingPreferencesAsync` 的 `preferences is null` 早退分支也清 `PreferenceSaveStatus`。 |
| **AC6 未断言落库值** | **已修**：`RapidZoomClicks_CoalesceIntoFewWrites` 追加 `LastSavedPreferences.Zoom == 1.6`。 |
| 证据日志仍是 r1 时间点 | **已修**：`four-pieces.log` / `regression.log` 按 r3 重生成。 |

### 未修并接受的限制（不得写成通过）

1. **AC1–AC3 的"重开读回"半边未端到端验证**：本卡证明的是"控件路径确实发出了正确的
   `ReadingPreferencesPatch`"与"失败不记账"，**没有**在有真实 sidecar 的环境里做
   "保存 → 重启 → 读回"闭环。原因是 E-2（仓库 sidecar 2026-10-23 早于 `SaveReadingPreferences`），
   `NOT_RUN`。
2. **无 View 级测试覆盖 `DoubleTapped` 与键盘 `+`/`-`/`0` 入口**：它们已接线（`ReaderPageView.cs:180`、
   键处理分支），但只有静态核对。
3. **全局单槽 pending**：`_pendingPreferenceIntent` 只有一个槽；若用户在窗口内对两本书都做了改动，
   较早的意图会被较新的覆盖。已在复审中确认「旧书意图写旧书」是期望语义，但**窗口内的多书并发
   只保证最后一次**。
4. **离开阅读器无显式 flush**：依赖 80ms 合并窗口内的保存；极端情况下进程在窗口内终止会丢最后一次。



