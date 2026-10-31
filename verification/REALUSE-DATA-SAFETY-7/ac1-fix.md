# AC1（R-001）：关闭阅读浮层与在途保存并发的 NRE 修复

日期：2026-11-01。Owner：DSH。基线：`main@29d06c462`（分支 `task/REALUSE-DATA-SAFETY-7`）。

## 根因

`ReaderOverlayViewModel.SaveProgressAsync`（SAFETY-6 AC1 引入的进度镜像路径）在 `await`
`IHostController.SaveReadingProgressAsync` **之后**继续解引用字段 `_book`：

```
await _controller.SaveReadingProgressAsync(_book.ChapterId, page.PageId, ...);   // 等待 Host
...
await _progressSaved(new ReaderProgressSavedEvent(_book.BookId, _book.ChapterId, ...));
```

并发窗口：用户翻页触发保存（`_isSaving = true`，await 中）后立刻关闭阅读浮层。
`CloseAsync` 先调 `SaveProgressAsync(isClosing: true)` —— 被 `_isSaving` 短路直接返回（**关闭时的权威重读因此丢失**）；
随后 `CloseAsync` 继续执行 `_book = null`、`Pages.Clear()`。等 Host 返回、第一个保存恢复执行时，
`_book` 已是 null → **未捕获 NullReferenceException**（reviewer 在仓外副本复现的堆栈 `:377 ← GoToAsync :308`）。

## 修复（`ReaderOverlayViewModel.cs`）

1. 新增 `_inFlightSave` 字段，`SaveProgressAsync` 改为薄包装：同步置 `_isSaving` 并记录在途任务；
2. 实际保存移入 `SaveProgressCoreAsync`，**在 await 之前**快照 `book` / `page` / `pageCount` 局部变量，
   await 之后只使用局部值，不再触碰可能已被清空的字段；
3. `CloseAsync` 先 `await _inFlightSave`（吞掉已记录的类型化失败），再执行 `isClosing` 保存 ——
   保证关闭时**仍然发生一次权威投影重读**，不会被 `_isSaving` 短路。

## 验证（真实执行，非推断）

| 检查 | 命令 | 结果 |
|---|---|---|
| 新增并发用例 | `dotnet test --filter FullyQualifiedName~LibraryProgressRefreshTests` | **6/6 通过**（原 5 + 新并发用例） |
| 全量回归 | `dotnet test tests/NewManga.App.Tests` | **395 通过 / 0 失败 / 7 跳过（402）**，EXIT=0（`ac1-fix-tests.txt`） |
| 构建 | `dotnet build NewManga.sln -v q --nologo` | 0 警告 / 0 错误，EXIT=0 |
| **负向对照** | 移除生产修复、保留测试后重跑单测 | **1 失败 / 0 通过，EXIT=1**（`ac1-negative-control.md`） |

负向对照证明：该用例确实覆盖"并发关闭不再 NRE 且仍权威重读"，不是恒真断言。
