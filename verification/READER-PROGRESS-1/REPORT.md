# READER-PROGRESS-1 验证报告（阅读进度保存接线）

- Task: `doc/tasks/READER-PROGRESS-1.md`（team task-24）
- Branch / worktree: `task/READER-PROGRESS-1` / `G:/CODEX/New Manga.workspace/worktrees/READER-PROGRESS-1`
- Base: `230164c5c`（任务卡冻结 base；实际从释放提交 `b50ab8fc5` 建 worktree，其中已含任务卡与 AD-002 文档）
- 未 push；未改协议/Host 契约语义；未改 Python Core；未改旧壳；未启动旧壳。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 保存/恢复 | **MET** | 翻页/离开阅读器/关闭窗口均调用 `SaveReadingProgress`（参数对齐旧壳：`chapter_id`+`mode`+`page_id`，`scroll_offset_y`/`elapsed_seconds_delta` 仅在有效时发送）；重开同一书由 `GetReaderProjection(start_position=resume)` 恢复到上次页；失败降级为 typed 结果（`NotReady`/`ReadOnly`/`Failed(code)`），UI 不抛异常、不阻塞翻页。见 §3（真机）与 §4（headless）。 |
| AC2 边界 | **MET** | 多书进度按 (book,chapter,mode) 独立（headless 双书）；页数变少：Core `_remap` 回退第一页 + 客户端 `ReaderBookData.FromProjection` 钳制（单测 + headless）；只读 Host 直接 typed `HOST_READ_ONLY` 且不发 Core 请求（Host 集成测）；无 Core → `HOST_NOT_READY`（headless）。 |
| AC3 测试 | **MET** | Headless「打开→翻页→关闭→重开恢复」见 `ReaderProgressTests`；真机 BOOK-FIXTURE 隔离根两会话验证见 §3（截图 01/02 + wire + DB 快照）。 |
| AC4 回归 | **MET** | `scripts/test.ps1` **131/131 passed, 0 skipped**；旧壳 vitest **60 files / 567 tests passed**；pytest **3 failed / 2739 passed / 9 skipped**（与基线 3F/2739P/9S 完全一致，0 新增失败）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；Canonical Evidence 64-hex pin（见任务卡）；本报告 + Handoff。 |

## 2. 实现摘要（全部在 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/CoreServiceClient.cs` | `GetReaderProjectionAsync(chapterId, mode, startPosition)` 支持 `resume`/`beginning` 并解析 `initial_position`/`saved_progress`；新增 `ReadingProgressSnapshot` + `SaveReadingProgressAsync`（可选字段 MISSING=NOT SENT，`elapsed` 仅 >0 发送）；`ReaderProjection` 增加 `InitialPageId`/`InitialScrollOffsetY`/`SavedProgress`。 |
| `src/NewManga.CoreClient/Wire/CoreProtocol.cs` | 新增 `IsEventFrame`：core_service 会把 `ReadingProgressChanged` 事件帧混在响应流里，客户端据此跳过直至拿到响应信封。 |
| `src/NewManga.CoreClient/Transport/SidecarProcess.cs` | 新增 `ReadNextResponseLineAsync`（读取不属于请求的事件帧，仍记入 wire 证据，请求侧为空串）。 |
| `src/NewManga.Host/HostRuntime.cs` | `GetReaderProjectionAsync(chapterId, startPosition)`；`SaveReadingProgressAsync`：写权限门（只读 → typed `ReadOnlyHostException`，不发 Core）+ 与页图读共用 `_readerIoGate` 串行门（core_service 严格一问一答）。 |
| `src/NewManga.App/Services/IHostController.cs` | 新增 `IReaderProgressSink` + `ReaderProgressSaveResult`；`LoadReaderBookAsync(bookId, chapterId)`；`HostController`/`NullHostController` 实现。 |
| `src/NewManga.App/Services/ReaderLibrary.cs` | `ReaderBookData` 增加 `InitialPageIndex`/`InitialScrollOffsetY`/`SavedPageId`，`FromProjection` 把 resumed page 映射为索引并做页数钳制。 |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | 阅读页 `ProgressSink`；`GoToPage(Async)`/`TurnPageAsync`/`SaveProgressAsync`/`FlushProgressAsync`；翻页、滚轮、方向键、沉浸窗 Esc/关闭、离开阅读器页、关闭主窗均保存；**reading clock 只在成功后重置**（不重发已接受区间）；**重复同位置写入合并**（不双计 elapsed）；**恢复期间抑制滚动事件写入**（程序化 restore 的 ScrollChanged 不得覆盖已恢复进度）；webtoon 保存 `scroll_offset_y`（逻辑页原图像素）；恢复时按 `InitialPageIndex`/偏移定位。 |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 注入 `ProgressSink`；`LoadReaderAsync(bookId, chapterId)`；离开阅读器/关闭窗口时 flush；沉浸窗带 sink。 |
| `tests/NewManga.App.Tests/ReaderProgressTests.cs`（新，18 项） | 翻页保存、关闭重开恢复、主窗重开恢复、多书独立、页数缩小回退、页数钳制、只读不写、无 Core、失败 typed、elapsed 不重发、重复合并、webtoon 偏移、沉浸窗 Esc flush、离开页面 flush、关闭窗口 flush、fixture 回退不写、投影映射钳制、**重开 webtoon 不被 restore 覆盖**。 |
| `tests/NewManga.Host.Tests/HostReaderProgressIntegrationTests.cs`（新，3 项）+ `Support/BookFixture.cs` | 真 sidecar：BOOK-FIXTURE 副本上 save→（重启 Host）→ resume 命中、未知 page → `TARGET_NOT_FOUND`、只读 Host → `HOST_READ_ONLY`。 |
| `tests/NewManga.App.Tests/FakeHostController.cs` | 新增 `FakeProgressStore`（按 chapter/mode 持久化，模拟 Core resume/拒绝语义）+ `IReaderProgressSink` 实现。 |
| `scripts/test.ps1` | 新增可选 `-EvidenceDirectory`（并行任务不共享 rerun 证据目录；默认行为不变）；导出 `NEWMANGA_BOOK_FIXTURE_ROOT` 供 Host E2E。 |
| `scripts/start-book-fixture.ps1` | 新增可选 `-ExtraArgs`（真机 `--demo-write` 打开写权限；默认行为不变）。 |

契约对齐说明：写面 payload 与旧壳 `library_save_reading_progress` → `SaveReadingProgress` 保持一致（`scroll_offset_y` 省略表示 0；`elapsed_seconds_delta` 省略=不发送，只发送自上次成功后新增的时长）。`library_save_reading_progress` 在 `HostCommandRegistry` 仍是 `NOT_SUPPORTED`（其 parity 探针用的是错误 payload，见遗留 3），本轮与 READER-LIBRARY-WIRE-1 的 `GetReaderProjection` 一样，从 Host/CoreClient 直接接线，不改 registry 分类与已冻结 parity 证据。

## 3. 真机证据（BOOK-FIXTURE 隔离根，AC3）

环境：发布件 `task-envs/READER-PROGRESS-1/pkg/app/NewManga.App.exe`（Release single-file + `core-sidecar` junction 指向 FINAL-VALIDATION-1 打包件）；数据根 `task-envs/READER-PROGRESS-1/isolated-data`（BOOK-FIXTURE durable 状态副本：`library.db` + `managed/`；`derived/`、`catalog/` 由 Core 重建，因为其绑定源根身份）；启动：
`pwsh -File apps/desktop-avalonia/scripts/start-book-fixture.ps1 -AppExe <pkg>/NewManga.App.exe -DataRoot <isolated-data> -ExtraArgs '--demo-write'`（host.log：`mode=ReadWrite reason=parity reached`）。

- 书：`14340ddad0ed472fbe687fe12340c5d8` / 章：`240bdba549b74281bfc6d901b1a7abd7` / 8 页 / webtoon_vertical。
- **会话 A**（首启）：打开阅读器 → 无进度表行为 0（不写）；翻页 2 次 → 13:05:41 保存页 `4f8a24…`（elapsed 12.85s）、13:05:51 保存页 `a607fc…`（elapsed 10.36s）；离开阅读器 → 13:06:03 flush 页 `a607fc…`（elapsed 11.43s，total 34.64s）；关闭 App。截图 `screens/01-bookshelf-session-a.png`。
- **会话 B**（同数据根重启）：打开阅读器 → `GetReaderProjection start_position=resume` 返回 `initial_position.page_id=a607fc…`（=会话 A 最后页）；**恢复过程 0 次 SaveReadingProgress，DB 行与会话 A 完全一致**（未被恢复事件覆盖）；截图 `screens/02-reader-restored-page.png`（内容为恢复后的第 3 页区域，非首页）。
- 断言（`live-evidence.json.assertions`，全 true）：resume 使用、首次打开 page1、重启 initial=保存页、保存页=最后翻页、恢复不发写、无重复写、elapsed 仅正数、累计时长单调。
- 证据文件：`runtime-logs/wire-session-a.ndjson`（会话 A 命令/响应）、`runtime-logs/wire-session-b-only.ndjson`（会话 B 14 帧，无 Save）、`runtime-logs/wire-full-a-plus-b.ndjson`、`runtime-logs/host.log`、`runtime-logs/reading-progress-session-{a,b}.json`。

## 4. 回归（AC4）

| 门 | 命令 | 结果 |
|---|---|---|
| Avalonia 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | **TEST PASS (Debug): 131/131 passed, 0 skipped**（coreclient 40 / host 40 / app 51；基线 110 + 本轮 21） |
| 旧壳 vitest | `cd apps/desktop/frontend && npm test`（在主仓运行：worktree 无 node_modules；`git diff b50ab8fc5 -- apps/desktop/frontend` 为空，代码与 worktree 相同） | **60 files / 567 tests passed**（与基线一致） |
| pytest | `PYTHONPATH=src python -m pytest -q` | **3 failed / 2739 passed / 9 skipped**（失败集合与基线相同：`test_detection_manga_real` ×2 + `test_workbench_viewmodel` 时序 flaky；0 新增） |
| 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-PROGRESS-1.md` | PASS（见任务卡 64-hex pin 与本 Handoff） |

## 5. 未覆盖 / 遗留（记录不阻塞）

1. **真实 Core 的多书独立 / 页数缩小**：BOOK-FIXTURE 只有 1 本书 1 章 8 页，无法在不改 fixture 语义的前提下制造「第二本书」或「页数变少」。这两条由 headless（FakeProgressStore）与 Core 侧既有 `_remap` 单测覆盖；未在真机重复。
2. **沉浸窗/离开页面 flush 的真机验证**：headless 已覆盖（Esc、Navigate、Close 均 flush）；真机本轮只验证了「离开阅读器页 flush」与「关闭 App」路径（关闭时会话 B 无可写增量，故 DB 未变，属预期）。
3. **`HostCommandRegistry` 的 `library_save_reading_progress` 仍标记 `NOT_SUPPORTED`**：其 parity 探针 `probe-core-commands.ps1` 发送的是错误 payload（`{chapter_id, position}`），Core 回 `INVALID_REQUEST`，据此登记为 NOT_SUPPORTED；本轮运行时不经过该分类（与 GetReaderProjection 相同做法）。建议后续单独任务修正探针 payload 后重分类，需同步冻结 parity 证据，未在本卡范围内改。
4. **进度写入节流**：翻页即时写；webtoon 滚动按“换页或 >1s”节流。未做长时滚动写压力测试。
5. 另需独立 Review（Owner 不得自审）。

## 6. 复现

```pwsh
# 1) 单元/集成回归（131 项）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\READER-PROGRESS-1\evidence

# 2) 真机（需 sidecar 包 + BOOK-FIXTURE 隔离根副本）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/start-book-fixture.ps1 `
  -AppExe G:\CODEX\New Manga.workspace\task-envs\READER-PROGRESS-1\pkg\app\NewManga.App.exe `
  -DataRoot G:\CODEX\New Manga.workspace\task-envs\READER-PROGRESS-1\isolated-data -ExtraArgs '--demo-write'
# 打开阅读器 → 翻页 → 离开 → 关闭 → 再次启动打开阅读器（应回到上次页）
```
