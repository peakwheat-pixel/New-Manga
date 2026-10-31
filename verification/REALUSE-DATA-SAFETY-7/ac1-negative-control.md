# AC1 负向对照记录（R-001）

日期：2026-11-01（**2026-11-01 修订**：改为 post-delivery 配方并附实测输出，对应 SAFETY-7 Review F-002）。

目的：证明新增并发用例 `ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection`
真的在测「关闭与在途保存并发」这条修复，而不是恒真断言。

> 初版本文档记录的步骤是「提交前工作树」配方（`git diff > fix.patch` + `git checkout -- <file>`），
> 在交付 head 上逐字执行是空操作（工作树干净 → `git diff` 为空），无法复现 1 failed。本修订改为
> post-delivery 配方：从 base commit 取出修复前的生产文件覆盖工作树，跑测试，再从 HEAD 恢复。

## 可复现步骤（post-delivery，在 SAFETY-7 worktree 执行）

```powershell
$wt = 'G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-7'
$src = 'apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs'
cd $wt

# 1) 用 base commit 的修复前生产文件覆盖工作树（字节级重定向）
cmd /c "git -C `"$wt`" show 29d06c462:$src > `"$(Join-Path $wt ($src.Replace('/','\')))`""

# 2) 构建并只跑并发用例（cwd 必须在 apps/desktop-avalonia）
cd (Join-Path $wt 'apps\desktop-avalonia')
dotnet build NewManga.sln -v q --nologo
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q --filter "FullyQualifiedName~ClosingWhileSaveInFlight"

# 3) 恢复交付版本
cd $wt
git checkout HEAD -- $src
git status --porcelain   # 应无输出
```

## 实测结果（2026-11-01 01:5x，真实输出）

```
## command: dotnet build NewManga.sln -v q --nologo (cwd=...\worktrees\REALUSE-DATA-SAFETY-7\apps\desktop-avalonia)
已成功生成。
    0 个警告
    0 个错误
EXIT=0

## command: dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q --filter "FullyQualifiedName~ClosingWhileSaveInFlight" (cwd=...\worktrees\REALUSE-DATA-SAFETY-7\apps\desktop-avalonia)
[xUnit.net 00:00:00.63]     NewManga.App.Tests.LibraryProgressRefreshTests.ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection [FAIL]
失败!  - 失败:     1，通过:     0，已跳过:     0，总计:     1，持续时间: 36 ms - NewManga.App.Tests.dll (net9.0)
EXIT=1
```

恢复后 `git status --porcelain` 无输出（工作树回到交付版本）。

## 说明

- 失败形态与 SAFETY-6 Review 的 R-001 描述一致（关闭时在途保存恢复后解引用已清空的 `_book`，
  未捕获 NRE 从 `GoToAsync` 传播到测试）。
- SAFETY-7 独立 Review 也在仓外副本用同一配方独立复现（1 failed / EXIT=1，3/3 稳定）。
