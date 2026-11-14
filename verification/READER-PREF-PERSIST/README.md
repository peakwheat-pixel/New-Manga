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
