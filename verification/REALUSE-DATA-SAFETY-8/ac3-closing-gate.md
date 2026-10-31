# AC3（F-005）：关闭期间保存门禁

日期：2026-11-01。Owner：DSH。基线：`main@bb7cbda1d`。

## 问题（SAFETY-7 Review F-005）

`CloseAsync` 在 `await _inFlightSave` 期间把控制权交回 UI 线程；若此时用户再翻页
（`GoToAsync` → `SaveProgressAsync`），新保存会把 `_isSaving` 重新置 true，`CloseAsync` 恢复后的
`SaveProgressAsync(isClosing: true)` 又被短路 → 关闭时的权威重读被跳过（不再 NRE，但违背
「closing 时恰好一次权威重读」）。

## 改动

1. 新增 `_isClosing` 标志，`CloseAsync` 全程置 true（`try/finally` 恢复）；
2. `GoToAsync` 在 `_isClosing` 时直接返回（关闭窗口内的翻页被忽略）；
3. `SaveProgressAsync` 在 `_isClosing && !isClosing` 时直接返回（只有 closing 自身可以保存）；
4. `CloseAsync` 的等待改为循环：等待一个在途保存 → 若期间又出现新的在途任务则继续等待，
   因此「等待 → 关闭保存」之间不会再有第三方保存插入。

```csharp
_isClosing = true;
try
{
    while (_inFlightSave is { } pending)
    {
        try { await pending.ConfigureAwait(true); }
        catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException) { }
        if (_inFlightSave == pending) { _inFlightSave = null; }
    }

    await SaveProgressAsync(isClosing: true).ConfigureAwait(true);
    ...
}
finally { _isClosing = false; }
```

## 验证

新增用例 `ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread`：

- 用 gate 挂起第一个保存；
- 在 `CloseAsync` 等待窗口内调用 `GoToAsync(5)`（模拟用户翻页）；
- **判别性断言（REALUSE-DATA-SAFETY-9 R-002 补强）**：close 窗口内 `PageIndex` 必须保持 3
  （pre-F-005 代码会先移到 5）——该断言在旧代码上失败，见 `verification/REALUSE-DATA-SAFETY-9/ac1-discriminating.md`；
- 回归栅栏断言：`ReaderLoadCount == loadsBefore + 1`（**恰好一次**权威重读）、`IsOpen == false`、`LastSaveResult == Saved`。

结果：filtered **7/7**（原 6 + 新用例），EXIT=0；全量 **396 通过 / 0 失败 / 7 跳过（403）**，EXIT=0。
证据：`ac1-fix-tests.txt`（SAFETY-8）与 `verification/REALUSE-DATA-SAFETY-9/ac1-fix-tests.txt`（SAFETY-9 判别性补强）。

## 边界

- 门禁只在 `CloseAsync` 执行期间生效，正常阅读不受影响；
- 未改变 `GoToAsync` / `SaveProgressAsync` 在非关闭状态下的既有行为；
- 不涉及 Host/Core 协议。
