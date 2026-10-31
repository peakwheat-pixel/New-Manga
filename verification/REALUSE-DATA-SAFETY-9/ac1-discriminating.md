# AC1（R-002）：判别性断言

日期：2026-11-01。Owner：DSH。基线：`main@5b888cd70`。

## 问题（SAFETY-8 Review R-002）

`ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread` 在 **pre-F-005** 生产文件
（`bb7cbda1d` 版本，`_isClosing` 0 次出现）下同样通过：close 窗口内 `GoToAsync(5)` 调用的
`SaveProgressAsync` 会被仍是 `true` 的 `_isSaving` 早退，旧实现与 F-005 门禁在"不启动第二个保存"
这一点上行为相同；原断言（`loadsBefore + 1`、`IsOpen == false`、`LastSaveResult == Saved`）因此
不判别修复。该用例当时只是"回归栅栏"。

## 修复

在 close 窗口内（gate 尚未释放）增加判别性断言：

```csharp
var closing = library.Reader.CloseAsync();

// A page turn during the close window: must be ignored, not start a second save.
var lateNavigation = library.Reader.GoToAsync(5);

// F-005 discriminator: pre-gate code moves PageIndex to 5 here; the gate keeps it at 3.
Assert.Equal(3, library.Reader.PageIndex);
```

`GoToAsync` 的同步段（`PageIndex` 赋值）在 `_isClosing` 门禁处直接返回；旧实现会先 `PageIndex = 5`
再在 `SaveProgressAsync` 处早退。因此该断言**只**在 F-005 门禁存在时成立。

同时在 `ac3-closing-gate.md`（SAFETY-8 证据）与用例注释中标注其角色：**判别性断言**（不是回归栅栏）。

## 负向对照（实测）

用 `bb7cbda1d` 的 pre-F-005 生产文件覆盖工作树（`_isClosing` 出现 0 次），构建后跑该用例：

```
[xUnit.net]  NewManga.App.Tests.LibraryProgressRefreshTests.ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread [FAIL]
失败!  - 失败: 1，通过: 0，已跳过: 0，总计: 1
EXIT=1
```

恢复交付版后：

```
已通过! - 失败: 0，通过: 1，已跳过: 0，总计: 1
EXIT=0
```

结论：新断言**判别** F-005 门禁（旧代码失败、新代码通过）。
