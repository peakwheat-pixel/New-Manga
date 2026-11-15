# L-L1-2-CONSTRAINT-VERIFY-1：核实"第二优先"是否落地且**遵守 goal 的硬约束**

基线 `b8579db99`。goal 的**第二优先**原文：

> 按 `doc/reviews/MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md` 的裁决执行**章节手动排序**；
> **wire 顺序保持 `sort_order`，排序在 UI/Host 消费层做，不得擅自改 wire 顺序**。

## 1. 卡片状态与 commit 可达性

- 卡片：`doc/tasks/CHAPTER-MANUAL-SORT.md`，`status: done`。
- `integration_commit: c459b279f` / `delivery_head: c459b279f`。
- **可达性实测**：`git cat-file -t c459b279f` → `commit`；
  `git merge-base --is-ancestor c459b279f HEAD` → **是 HEAD 的祖先**（EXIT 0）。
  ⇒ **不是孤儿/被改写的 commit**。

## 2. 硬约束第 1 条：wire 顺序保持 `sort_order`

实测 `src/infrastructure/sqlite/library.py`：

```
:1200  ORDER BY c.sort_order, c.import_order, c.chapter_id,
:1228  ORDER BY c.sort_order, c.import_order, c.chapter_id,
```

**主排序键是 `sort_order`**；`import_order` / `chapter_id` 只是**并列 tie-breaker**（确定性需要）。
⇒ **wire 顺序仍然由 `sort_order` 决定，未被改动。**

另有 `service.py:167` 的注释作为语义依据：

```
# R-04 (r2): sort_order is the display/read order and must stay unique.
```

⇒ 该字段**本来就是**显示/读取顺序，因此"手动排序 = 改它"是**符合语义**的做法，不是改 wire 契约。

## 3. 硬约束第 2 条：排序在 UI/Host 消费层做

实现路径（实测）：

| 层 | 位置 | 作用 |
|---|---|---|
| **UI** | `ShelfViewModel.ReorderChapterAsync`（`:275`） | 拖拽后算出新的顺序 |
| **Host** | `HostController.ReorderChaptersAsync`（`:639`） | 调用 runtime 持久化 |
| | `IHostController.ReorderChaptersAsync`（`:223`） | 接口 |
| | `NullHostController`（`:116`） | 空实现 |
| **Core** | `runtime.py:865` `sort_order=source_order` | 落库 |

⇒ **分层的顺序决策在上层（UI/Host），Core 只负责持久化**。**没有在 wire 层加重排逻辑。**

## 4. 测试覆盖

| 侧 | 文件 | 覆盖 |
|---|---|---|
| C# | `tests/NewManga.App.Tests/LibraryMetadataPortTests.cs` | `ReorderChapters` 端口行为 |
| Python | `tests/storage/test_chapter_reorder_atomic.py` | **原子性**（reorder 的 all-or-nothing） |
| Python | `tests/library/test_chapters.py`、`tests/storage/test_library_metadata.py` | 章节/元数据 |

⇒ **不是"只有实现没有测试"。**

## 5. 结论

| 检查项 | 结果 |
|---|---|
| 卡片 `done` 且 commit 可达 | ✅ |
| wire 顺序仍按 `sort_order` | ✅（主键；tie-breaker 不改变语义） |
| 排序决策在 UI/Host 层 | ✅（Core 只持久化） |
| 未擅自改 wire 顺序 | ✅ |
| 有测试覆盖 | ✅（含原子性） |

**⇒ 第二优先的"章节手动排序"已落地，且遵守 goal 的全部硬约束。**
