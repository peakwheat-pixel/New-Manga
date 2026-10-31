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

## 负向对照（实测；完整五步 run 于 2026-11-01 02:53:12 在 SAFETY-11 worktree 执行，原始日志见 `verification/REALUSE-DATA-SAFETY-10/ac1-negative-control-full.txt`）

**执行位置**：在 SAFETY-11 的 worktree（`G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-11`）
内**临时覆盖后恢复**——不是在 main 工作区原地覆盖，也没有改动任何已提交的交付字节。完整原始日志见
`verification/REALUSE-DATA-SAFETY-10/ac1-negative-control-full.txt`（R-102 补全：五步全程，含覆盖命令、`_isClosing` 计数、失败运行 EXIT=1、恢复确认、恢复后通过 EXIT=0；早前精简版为同目录 `ac1-negative-control.txt`）。

**命令与 cwd**（host：本机 / pwsh 7 / dotnet 10.0.401）：

```powershell
$wt = 'G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-11'
$src = 'apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs'
cd $wt
cmd /c "git -C `"$wt`" show bb7cbda1d:$src > `"$(Join-Path $wt ($src.Replace('/','\')))`""
# 覆盖后 `_isClosing` 出现次数 = 0（pre-F-005）
cd (Join-Path $wt 'apps\desktop-avalonia')
dotnet build NewManga.sln -v q --nologo --no-incremental
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v n --filter "FullyQualifiedName~ClosingWhileSecondSaveRequested"
# 恢复
cd $wt; git checkout HEAD -- $src; git status --porcelain   # 无输出
```

**断言失败明细**（关键：失败点正是新增断言）：

```
[xUnit.net]  NewManga.App.Tests.LibraryProgressRefreshTests.ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread [FAIL]
  Assert.Equal() Failure: Values differ
  Expected: 3
  Actual:   5
  Stack Trace:
    .../tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs(328,0): at ...ClosingWhileSecondSaveRequested_StillPerformsExactlyOneAuthoritativeReread()

失败!  - 失败: 1，通过: 0，已跳过: 0，总计: 1
EXIT=1
```

`Expected: 3 / Actual: 5` 与失败行 `LibraryProgressRefreshTests.cs:328` 对应新增的
`Assert.Equal(3, library.Reader.PageIndex)`，证明失败来自判别性断言而非其它路径。

恢复交付版后：

```
已通过! - 失败: 0，通过: 1，已跳过: 0，总计: 1
EXIT=0
```

结论：新断言**判别** F-005 门禁（旧代码在 `:328` 以 `Expected 3 / Actual 5` 失败、新代码通过）。

