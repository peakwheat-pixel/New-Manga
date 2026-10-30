---
task: REALUSE-DATA-SAFETY-3
round: 2
reviewer: antigravity-headless
reviewer_participated_in_implementation: false
verdict: PASS
reviewed_head: 4b9b53bb0
reviewed_base: 8b1ca6723
previous_round: FAIL_WITH_MUST_FIX (doc/reviews/REALUSE-DATA-SAFETY-3-antigravity-r1.md)
captured_by: dsh-lead
capture_note: >
  Antigravity 复核原始回答逐字保存（同一会话续接）。正文未做任何编辑；复核者自行跑了全量测试。
---

# REALUSE-DATA-SAFETY-3 独立审查复核（Round 2，Antigravity）

# 独立审查复核报告：REALUSE-DATA-SAFETY-3（Commit `4b9b53bb0`）

- **复核基准**：HEAD commit `4b9b53bb0`（基于 `46ebc31df`）
- **测试状态**：全量测试套件 358 项通过、0 项失败、7 项跳过（全绿灯）
- **复核结论**：**PASS**

---

## 一、重点复核问题答复

### 1. M1 修复是否彻底：是否存在其他“用快照代替读取产生静默替代”的路径？
**结论：彻底，不存在其他静默替代风险。**
- **依据**：[`HostController.cs:349-366`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L349-L366)
  1. 显式请求 `bookId` 时，先校验快照；若快照未命中，立即调用 `runtime.ListBooksAsync(cancellationToken)`；
  2. 若重新拉取后依然不存在，第 365 行显式 `return null;`，彻底删除了旧版中静默 fallback 到第一本书的代码；
  3. 检索全库所有使用 `Snapshot.Books` 的位置（`StudioPageViewModel.cs:889`、`ImportExportPanels.cs:167`、`ReaderWorkbenchPages.cs:339`）：
     - `StudioPageViewModel.ResolveBookTitle` 仅用于标题文本显示，未命中时保留当前 `BookTitle`，不替代实体；
     - 导出（`StartExportAsync`）与进度存储（`SaveReaderProgressAsync`）直接向 Core 发送显式参数，不走快照或前端兜底。

### 2. M2/M3 失效点是否完整：写路径对书架与章节的联动
**结论：完整，所有变更书架或章节的写路径均已正确失效。**
- **创建书籍**（`TryCreateBookAsync`）：在 [`HostController.cs:251`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L251) 成功后调用 `RefreshBooksAsync()`，从而触发 `_chapterCache.Clear()` 并更新书架；
- **创建章节**（`CreateChapterAsync`）：在 [`HostController.cs:311-314`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L311-L314) 成功后精准 `Remove(bookId)` 失效对应书籍的缓存；
- **页面导入**（`ImportFilesAsync` / `ImportFolderAsync`）：导入向既有章节增加页面，完成后由 `LibraryViewModel.ReloadAfterImportAsync` 调用 `RefreshBookCountsAsync`，进而触发 `RefreshBooksAsync()` 清空章节缓存并刷新总页数；
- **恢复备份**（`RestoreBackupAsync`）：在 [`HostController.cs:1700-1704`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1700-L1704) 恢复成功后，立即在锁内 `_chapterCache.Clear()` 并 `await RefreshBooksAsync(...)` 重新加载全库书架；
- **外部 Shell / 外部进程修改**：用户点击界面“刷新”按钮会调用 `RefreshBooksAsync()`，由 M3 在锁内清空 `_chapterCache` 并拉取最新数据。

### 3. M4 锁的覆盖度与死锁风险
**结论：完全覆盖，无任何死锁风险。**
- **依据**：[`HostController.cs:23, 173, 311, 482, 494, 1700`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L23)
- 检查了对 `_chapterCache` 的全部 5 处访问点（1 处 TryGetValue、1 处索引写、1 处 Remove、2 处 Clear），全部包裹在 `lock (_chapterCacheLock)` 块内；
- 所有的 `lock` 语句块内均为纳秒级同步内存读写，**绝对没有任何 `await` 或异步调用**，杜绝了死锁隐患。

### 4. M5 的新语义与单例假设
**结论：语义合理，完全符合单例假设。**
- **“本会话创建但后续失效的 Run”**：在冻结契约无 `ListRuns` 的前提下，`KnownRunIds` 仅作为“本会话已知 Run”的轻量辅助索引（上限 12 个，LRU）。现在用户手动输入拼错的无效 ID 不会再被记录，只有 Studio 创建成功或 Host 返回成功的真实 Run 才会入列。若用户点击了已被清理的 Run，会诚实弹出 `TARGET_NOT_FOUND` 提示，体验符合设计规范。
- **单例一致性**：`AppShellViewModel` 全局唯一持有 `RunStatusMonitor` 实例，`RememberCreatedRun` 由 Studio 批处理完成创建时通过委托单一回调，未产生任何副本实例或竞态破坏。

---

## 二、上轮审查项逐条核验（M1 ~ M6）

| 项编号 | 问题描述 | 判定 | 依据（文件:行号） |
| :--- | :--- | :--- | :--- |
| **M1** | 阅读器在指定 `bookId` 未命中快照时静默打开第一本书 | **已修复** | [`HostController.cs:350-366`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L350-L366)<br>未命中时先拉取 Host，仍无则返回 `null`，严禁 fallback 到其他书籍。 |
| **M2** | 恢复备份后未失效章节缓存且未重新拉取书架 | **已修复** | [`HostController.cs:1700-1704`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L1700-L1704)<br>恢复成功后清空 `_chapterCache` 并调用 `RefreshBooksAsync()`。 |
| **M3** | 章节缓存缺乏失效出口，用户主动刷新无法更新章节 | **已修复** | [`HostController.cs:173-176`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L173-L176)<br>`RefreshBooksAsync` 主动清空 `_chapterCache`，用户刷新/导入即可联动失效。 |
| **M4** | `_chapterCache` 裸 Dictionary 无并发保护 | **已修复** | [`HostController.cs:23, 173, 311, 482, 494, 1700`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs#L23)<br>读写全部加 `_chapterCacheLock` 互斥保护，无并发安全风险。 |
| **M5** | 输入无效或拼错的 `run_id` 污染已知列表并陷入无限轮询 | **已修复** | [`RunStatusMonitor.cs:100-104, 142-148, 241-245`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/Shell/V2/RunStatusMonitor.cs#L100-L104) 与 [`AppShellViewModel.cs:402-406`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Shell/AppShellViewModel.cs#L402-L406)<br>`Track` 不再盲目记忆；仅 Host 确认存在或应用自身创建时才入列。 |
| **M6** | UI 单元测试 await 已完成 Task 导致竞态失败断言红灯 | **已修复** | [`V2ShellUiTests.cs:725, 750, 995, 1004`](file:///G:/CODEX/New%20Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3/apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs#L725-L750)<br>测试显式持有刷新 Task 并在 release gate 后正确 `await`，测试套件 100% 绿灯。 |

---

## 三、总判定

**结论**：**PASS**

所有阻塞性审查问题（M1 ~ M6）均已高质量修复，代码逻辑严密，无副作用与死锁风险，测试套件已完全恢复绿灯。

---

## 推荐下一步

根据 [协作协议 §5.1](file:///g:/CODEX/New%20Manga/doc/09_COLLABORATION.md#51-task-完成后的下一任务建议)，当前 Task（`REALUSE-DATA-SAFETY-3`）的 AC2、AC3、AC4 实现已通过独立审查：
1. **更新任务卡状态**：由 Lead（DSH）将 `doc/tasks/REALUSE-DATA-SAFETY-3.md` 中 AC2、AC3、AC4 的状态由 `<<PARTIAL>>` 推进为通过，填入 Canonical Evidence 与 commit hash（`4b9b53bb0`）；
2. **实施 AC1**：继续完成 AC1（Console 分区接线与说明占位），或在完成 AC1 后统一发起最终集成验证与关闭。
