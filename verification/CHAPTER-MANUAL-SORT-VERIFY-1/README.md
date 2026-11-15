# CHAPTER-MANUAL-SORT-VERIFY-1：goal 第二优先（裁决 A）的实施核实

基线 `e0662d40c`。

## 1. 背景：goal 的第二优先我一度漏了

goal 明确写：

> 【第二优先】按 `doc/reviews/MAINT-1-EXTERNAL-ADJUDICATION-codex-2026-11-14.md` 的**裁决执行章节手动排序**

那份裁决只有 29 行、两个裁决：

| 裁决 | 内容 | 要不要开卡 |
|---|---|---|
| **A** | 选 1：**手动拖拽排序**；**保持 wire 顺序为 `sort_order`，排序在 UI/Host 消费层做** | **开 1 张候选卡** |
| **B** | 选 3：**保持现状**，不做运行时重建/错误码拆分；保留"修改配置后重启生效"提示 | **不开卡** |

**⇒ 我在前若干轮专注 Gate 六条，没有回来核实"裁决 A 的卡是否真的落地了"。本轮补上。**

## 2. 卡片状态（表面）

`doc/tasks/CHAPTER-MANUAL-SORT.md`：

```
title: 章节手动排序闭环（书架拖拽 + 原子持久化 + 缓存失效）
status: done
disposition: "codex 外部裁决 A（2026-11-14）落地；L-L1-2 排序 UI 范围由 C3-3 OUT 提升为本卡；DSH 2026-11-14 释放"
canonical_evidence_status: complete
```

**但 AC1–AC10 全部是 `- [ ]`（未勾选）。**

**⇒ 与 `GATE4-PAGES-UPGRADE-1` 同样的记录卫生问题**：`status: done` 但 AC 未勾。

## 3. ★ 逐项核实实现（不看勾选，看代码）

### AC1 原子持久化

```
src/application/library/service.py:212   def reorder_chapters(self, book_id, ordered_chapter_ids)
src/application/library/service.py:323   def reorder_chapters_strict(self, book_id, ordered_chapter_ids)
```

**⇒ 存在。**

### AC1/AC2 原子性测试

```
tests/storage/test_chapter_reorder_atomic.py     ← 文件名就点明"atomic"
tests/library/test_chapters.py
tests/core/test_library_wire.py
```

**⇒ 有专门的原子性测试文件。**

### AC4 VM 拖拽语义

```
apps/desktop-avalonia/src/NewManga.App/Shell/ShelfViewModel.cs:275   public async Task<bool> ReorderChapterAsync(
```

**⇒ 存在。**

### AC5 视图拖拽手势

```
apps/desktop-avalonia/src/NewManga.App/Views/ShelfPageView.cs:161   DragDrop.SetAllowDrop(_root, true);
:162   _root.AddHandler(DragDrop.DragOverEvent, OnDragOver);
:163   _root.AddHandler(DragDrop.DropEvent, OnDrop);
:601   await DragDrop.DoDragDropAsync(args, payload, DragDropEffects.Move);
:614   DragDrop.SetAllowDrop(chapterButton, true);
:638   await _viewModel.ReorderChapterAsync(fromIndex, index);
```

**⇒ 拖拽手势、拖拽启动、拖放调用链全部存在。**

### AC3 缓存失效 / AC6 契约零变化

```
apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs:639   public async Task<bool> ReorderChaptersAsync(
apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs:223  Task<bool> ReorderChaptersAsync(...)
apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs:116
```

**⇒ 消费层三处（实现 + 接口 + 空实现）都在。**

### Wire 层

```
src/bootstrap/core_service.py:7212   elif command == "ReorderChapters":
```

**⇒ Core 侧命令存在，且是**新增**命令（不是改 `list_chapters` 的顺序）。

**⇒ 这符合裁决 A 的"保持 wire 顺序为 `sort_order`，在 UI/Host 消费投影中排序"** ——
新命令做重排，`list_chapters` 的返回顺序不动。

## 4. 结论

**裁决 A 的候选卡（`CHAPTER-MANUAL-SORT`）在代码层面是完整落地的**：

- 后端原子重排（`reorder_chapters` / `reorder_chapters_strict`）
- 原子性测试（`test_chapter_reorder_atomic.py`）
- Wire 新命令（`ReorderChapters`）
- C# 消费层三件套（实现/接口/空实现）
- VM 语义（`ShelfViewModel.ReorderChapterAsync`）
- **视图拖拽手势（`ShelfPageView` 的 DragDrop 全套）**

**裁决 B 按裁决"不开卡、保持现状"，未做任何改动** —— 也符合。

## 5. 未做（诚实）

- **未逐条核对 AC6「wire 字节不变」**（`generate_api_inventory.py --check` 通过，且 pins 18/18 通过，
  间接支持"契约未变"，但我没有逐字节比 `M2-C1`/`C-07` 载体）；
- **未跑 `test_chapter_reorder_atomic.py`**（本轮只做静态核实）；
- **未更新 `CHAPTER-MANUAL-SORT.md` 的 AC 勾选**（那是那张卡的作者/Reviewer 责任，我不越权改它的证据）。

## 6. 这张卡的记录卫生问题（建议）

与 `GATE4-PAGES-UPGRADE-1` 一致：`status: done` + `canonical_evidence_status: complete`
但 **AC1–AC10 全未勾**。**建议原作者或后续 Reviewer 补齐勾选与逐条证据链接**，
否则读者会以为"done 但没做"。
