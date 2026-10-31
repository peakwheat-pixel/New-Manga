# AC1（MA-09）阅读进度刷新：根因、实现与证据

- Task：REALUSE-DATA-SAFETY-6 / AC1（审计条目 MA-09）
- 分支：`task/REALUSE-DATA-SAFETY-6`（base `main@841cbdc4b`）
- 测试日志：[ac1-progress-refresh-test-log.txt](ac1-progress-refresh-test-log.txt)

## 1. 缺陷现状（改前）

`HostController.SaveReadingProgressAsync` 早已存在且被阅读浮层调用（`ReaderOverlayViewModel.SaveProgressAsync`），**缺的是"保存成功后把结果接回书架"**：

1. 书架详情面板的进度行由 `LibraryViewModel.LoadProgressAsync()` 计算，而它只在**章节切换**时调用（`SelectChapterAsync`）；同章节再次选中会提前 return。阅读浮层翻页/关闭时保存了进度，书架那一行**不会更新** → 回到书架仍看到旧值。
2. 导入完成后走 `ReloadAfterImportAsync()`：只重载页列表和书籍计数，**不重读进度**。导入会改变章节页数（进度分母），于是"读到 第 5 / 8 页"在导入 2 页后仍是 8，信息陈旧。
3. 阅读器自身的"进度：已保存到 Core"与书架的进度行是两个互不知道的值，没有任何一致性保证。

## 2. 实现（最小改动，3 个生产文件）

### 2.1 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs`

- 新增 `ReaderProgressSavedEvent`（book/chapter、1-based 页码、总页数、`IsClosing`、Core 返回的 `ReaderProgressSaveResult`）。
- 构造函数新增可选回调 `Func<ReaderProgressSavedEvent, Task>? progressSaved`（默认 null，保持旧调用方/测试兼容）。
- `SaveProgressAsync(bool isClosing = false)`：**仅当 `result.IsSaved`**（Core 真正提交）时，先记录 `LastSaveResult`，再 `await` 回调。类型化拒绝（NotReady / ReadOnly / Failed）不触发任何书架变化。
- `CloseAsync()` 用 `SaveProgressAsync(isClosing: true)`——关闭时浮层即将消失、书架即将可见，由书架侧改为"重读 Core 投影"。

### 2.2 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs`

- 构造阅读浮层时注入 `OnReaderProgressSavedAsync`。
- `OnReaderProgressSavedAsync`：
  - `IsClosing` → `LoadProgressAsync()`（真正的 Host 投影重读，权威值）；
  - 否则 → 只在**书架当前选中的章节与保存章节一致**时，用同一个格式化器把"已提交的位置"写进 `DetailProgressText`（深链到其它章节的阅读不得改写本书架行）。
- 抽出 `FormatSavedProgress(pageNumber, pageCount)`：投影路径与镜像路径共用同一个字符串格式，避免两套算法漂移。
- `SetDetailProgress(text)`：写值 + `ProgressRefreshes++` + `OnPropertyChanged(nameof(DetailProgressText))`（值相等也通知，UI 不会停留在旧值）。`ProgressRefreshes` 是给测试/证据用的可观测计数。
- `ReloadAfterImportAsync()` 末尾补 `await LoadProgressAsync()`（导入后页数/进度同步刷新）。

### 2.3 `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs`

- 新增 `ReaderLoadCount` 计数（测试支撑）：证明"刷新"确实发生了**一次 Host 投影读**，而不是只重渲染缓存。

### 2.4 为什么不是"每次保存都重读 Host"

阅读浮层每翻一页就保存一次；而 `GetReaderProjection` 在 Core 侧对**每一页**执行 `resolve_page_resource`，并对每页 managed 原件计算 sha256（`src/bootstrap/core_service.py:3270`、`:3296`）。对 169 页的章节，一次投影读≈对 100 MB 做摘要。因此：

- 翻页保存 → 用 Core 返回的已提交结果**本地镜像**（零额外 IO，且数值就是 Core 提交值）；
- 关闭浮层 → 书架即将可见，做**一次**权威投影重读；
- 导入 → 复用既有的 `afterImport` 钩子做一次权威重读。

## 3. 测试证据（真实运行）

`apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs`（新增，5 例）：

| 用例 | 证明什么 |
|---|---|
| `CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader` | 翻到第 5 页后，书架行 == `"读到 " + 阅读器 ProgressText`（同一页码+百分比）；`PropertyChanged(DetailProgressText)` 触发；`ProgressRefreshes` 增加 |
| `ClosingReader_ReReadsHostProjection_AndShelfShowsResumePage` | 关闭时 `FakeHostController.ReaderLoadCount` 增加（真实 Host 读）；书架值等于关闭前阅读器显示值；重开同章节续读到第 5 页且两者仍一致 |
| `Import_RefreshesProgressLine_WithNewPageCount` | 走**真实导入坞**（`ImportDock.OpenWithFilesAsync` → `afterImport`）：导入 2 页后书架行从 `/ 8 页` 变为 `读到 第 5 / 10 页 · 50%`，页列表重载、投影重读 |
| `RefusedSave_DoesNotFabricateShelfRefresh` | 类型化只读拒绝（`ReaderProgressSaveResult.ReadOnly`）时书架保持"未开始阅读"，`ProgressRefreshes` 不变，`FakeProgressStore` 无条目——**不伪造刷新** |
| `ReaderOnAnotherChapter_DoesNotRewriteTheSelectedChapterLine` | 深链阅读其它章节时，书架行与本行刷新计数都不变 |

实际结果（`ac1-progress-refresh-test-log.txt`）：

```
--filter FullyQualifiedName~LibraryProgressRefreshTests
已通过! - 失败: 0，通过: 5，已跳过: 0，总计: 5

全量 NewManga.App.Tests（--no-build，解决方案已重建）
已通过! - 失败: 0，通过: 394，已跳过: 7，总计: 401
```

负向对照（同一分支临时去掉构造函数里的回调接线）：上述 5 例中 **3 例失败**（`CommittedSave_*`、`ClosingReader_*`、`Import_*`），另 2 例（拒绝保存不伪造、深链不串章）按设计仍通过 → 证明这些测试确实在测"刷新已接线"，而不是只看代码存在。

## 4. 已知边界（不隐瞒）

1. **webtoon 模式的百分比口径**：书架行的百分比按"页码/总页数"计算，阅读器 webtoon 模式显示的是滚动比例（合同允许两种：Core 侧 paged 用页比、webtoon 用 `scroll_offset_y/page.height_px`，见 `src/application/reading/service.py:209-214`）。因此 webtoon 下"页码一致"成立、百分比可能不同——这是既有显示语义，本 Task 未改变它；测试用分页模式做严格逐字符一致断言。
2. **每翻一页的本地镜像不写 Host**：若同一时刻另有窗口改了同一章节进度，镜像值会滞后到关闭/下次投影重读才校正。这是刻意用"零额外 IO"换来的取舍，已在 §2.4 记录。
3. **进度行外的其它书架信息**（页数徽标、更新时间）仍由原有 `RefreshBookCountsAsync` 负责，本 Task 未扩大范围。
