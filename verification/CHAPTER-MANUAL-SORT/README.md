# CHAPTER-MANUAL-SORT 证据

卡面：`doc/tasks/CHAPTER-MANUAL-SORT.md`。日期 2026-11-14，基线 commit `79606ea4a`（+ 本卡改动）。

## 1. 开卡前的三项核实（codex 点名）

| # | 核实项 | 结论 | 证据位置 |
|---|---|---|---|
| 1 | 写接口与事务边界 | `ReorderChapters` wire 命令**已冻结存在**，写 `sort_order`；原实现为逐章 `update_chapter` 循环，**每次独立事务、无原子性**。`custom_rank` 仅逐章 `UpdateChapterMetadata`，无批量写。 | `src/application/library/service.py:212-224`（改前）、`src/infrastructure/sqlite/library.py:249-263`、`src/bootstrap/core_service.py:5170-5184` |
| 2 | 并发行为 | 无版本号/乐观锁；`reorder_chapters_strict` 仅在提交时校验"全覆盖 + 无重复"，窗口内章节集合变化以 `INVALID_REQUEST` 失败（fail-safe）；两端同时拖拽为 last-write-wins。 | `service.py:317-323`、`core_service.py:5178-5183` |
| 3 | 书架缓存刷新 | `HostController.ListChaptersAsync` 按书缓存一次，**仅 `CreateChapterAsync` 失效**；拖拽后若不新增失效点，重载读旧序 = 假成功。 | `HostController.cs:924-942`（改前） |

补充事实：`Chapter.reorder()` 注释 "User reordering touches sort_order only; import_order is frozen"（`src/domain/books/entities.py:164-167`）；`create_chapter` 按 `max(sort_order)+1` 追加（`service.py:167-171`）⇒ 新增章节天然排末尾。

## 2. 写入方案裁决（DSH，依据 codex 授权"DSH 先确认写入方案"）

**复用已冻结的 `ReorderChapters` 写 `sort_order`；不为拖拽新增 `custom_rank` 写路径。**

偏离登记：codex 裁决 A 字面假设拖拽写 `custom_rank` 并在消费层做 rank 混合排序。该假设基于"C1-5 读回未完成"与"需另建批量原子重排命令"的推测；实际 C1-5 已由 `MAINT-2-C1-BATCH-1` AC5 完成，`ReorderChapters` 命令自 `83e45cfe5`（2026-11-10）即存在。本卡改走 `sort_order`，满足裁决意图（手动顺序生效、wire 顺序不变、失败不假装成功），但**不实现 rank 混合排序语义**；`custom_rank` 保持无消费端，登记为限制。

## 3. 改动清单

| 层 | 文件 | 改动 |
|---|---|---|
| Core 契约 | `src/application/library/ports.py` | 新增 `update_chapters_atomic` 端口方法 |
| Core 持久化 | `src/infrastructure/sqlite/library.py` | 新增 `update_chapters_atomic`：单 `with self._conn:` 事务内批量 UPDATE，空列表 no-op |
| Core 应用层 | `src/application/library/service.py` | `reorder_chapters` 改为先算全部再一次性 `update_chapters_atomic` |
| Core 测试替身 | `tests/library/helpers.py` | fake repo 实现 `update_chapters_atomic` |
| Host 服务层 | `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` | `ReorderChaptersAsync` 成功后失效 `_chapterCache[bookId]`；失败时 `SetLastError(ErrorCodeOf(ex))`（原实现吞掉错误码） |
| UI VM | `.../ViewModels/Fluent/ShelfViewModel.cs` | 新增 `ReorderChapterAsync(from,to)` + `IsReordering` 守卫；失败/越权/只读不改可见顺序并给文案 |
| UI 视图 | `.../Views/Fluent/ShelfPageView.cs` | 章节项拖拽手势（阈值 4px 区分点击与拖拽），自定义 `DataFormat` 与文件导入隔离 |
| UI 测试替身 | `tests/NewManga.App.Tests/FakeHostController.cs` | 新增 `ReorderResult`/`ReorderCallCount`/`ReorderOverride` |

## 4. 测试结果

| AC | 状态 | 证据 |
|---|---|---|
| AC1 原子持久化 | PASS | `tests/storage/test_chapter_reorder_atomic.py` |
| AC2 判别测试（原子性） | PASS（含回退变红） | 见 §5 |
| AC3 缓存失效（集成） | **NOT_RUN** | 见 §6 |
| AC4 VM 拖拽语义 | PASS | `tests/NewManga.App.Tests/ShelfChapterReorderTests.cs`（8 项） |
| AC5 视图拖拽手势 | **NOT_RUN**（需真实 GUI） | 见 §6 |
| AC6 契约零变化 | PASS | `generate_api_inventory.py --check`；`verify_pins.ps1` |
| AC7 新增章节排末尾 | PASS | `test_chapter_created_after_manual_reorder_lands_at_the_end` |
| AC8 失败不假装成功 | PASS | `ReorderChapter_WhenTheWriteFails_KeepsTheVisibleOrderAndSaysSo` |
| AC9 并发保护（同实例重入） | PASS | `ReorderChapter_WhileAWriteIsInFlight_RefusesTheSecondDrag` |
| AC10 不回归 | PASS | 见 §7 |

## 5. AC2 判别力实测（回退变红）

把 `reorder_chapters` 临时改回逐章 `self._repo.update_chapter(chapter)` 循环后重跑
`tests/storage/test_chapter_reorder_atomic.py`：

```
FAILED test_reorder_rolls_back_every_row_when_a_later_write_fails
AssertionError: assert {'...': 2} == {'...': 3}
  Differing items:
  {'d8195f2e-...': 2} != {'d8195f2e-...': 1}
  {'0be6a589-...': 1} != {'0be6a589-...': 3}
```

即逐章实现下 `third` 已被落库为 1、`first` 被改为 2，未回滚 ⇒ 测试确实在实现回退时变红。
还原为单事务实现后 5/5 通过。

## 6. 未执行项及原因（不得当作通过）

- **AC3（缓存失效集成）NOT_RUN**：仓库内 sidecar 构建于 2026-10-23，而 `ReorderChapters` 命令
  自 `83e45cfe5`（2026-11-10）才存在 ⇒ 当前 sidecar 不认识该命令。重建 sidecar 需要 PyInstaller，
  本环境 PyPI 不可达（`ERROR: Could not find a version that satisfies the requirement pyinstaller`），
  无法重建。已写好并保留判别测试于 `pending-host-cache-test.cs.txt`，在 Gate 条件 4 产出绑定当前
  commit 的 sidecar 后可直接启用。缓存失效本身是 `if (updated) { lock { _chapterCache.Remove(bookId); } }`
  一行改动，已由代码审查覆盖，但**没有自动化测试固定住**。
- **AC5（真实 GUI 拖拽）NOT_RUN**：需要可运行的 Avalonia App + 交互；本环境只做了编译级验证
  （`dotnet build -warnaserror` 通过）。视图手势逻辑（阈值、格式隔离、Handled 冒泡）静态审查通过，
  但**没有真机拖拽证据**。

## 7. 四件套与回归

见同目录 `four-pieces.log` 与 `regression.log`（生成后追加）。
