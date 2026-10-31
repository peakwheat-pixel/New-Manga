# AC1 负向对照记录（R-001）

日期：2026-11-01。目的：证明新增并发用例 `ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection`
真的在测"关闭与在途保存并发"这条修复，而不是恒真断言。

## 可复现步骤

```powershell
$wt = 'G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-7'
cd $wt
# 1) 保存修复补丁并还原生产文件（测试文件保留）
git diff -- apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs > fix.patch
git checkout -- apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs
# 2) 构建并只跑并发用例
cd apps/desktop-avalonia
dotnet build NewManga.sln -v q --nologo
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q --filter "FullyQualifiedName~ClosingWhileSaveInFlight"
# 3) 恢复修复
cd $wt
git apply fix.patch
```

## 实测结果（2026-11-01 01:4x）

- 移除修复后：`失败! - 失败: 1，通过: 0，已跳过: 0，总计: 1`，**EXIT=1**；
  失败用例 `NewManga.App.Tests.LibraryProgressRefreshTests.ClosingWhileSaveInFlight_DoesNotThrow_AndStillReReadsProjection [FAIL]`
- 恢复修复后：同过滤 **6/6 通过**，EXIT=0（见 `ac1-fix-tests.txt`）

## 说明

- 负向对照在**同一 worktree** 内用"还原-重跑-恢复"完成（修复补丁保存在仓外 `tmp/safety7-negctl/fix.patch`），
  未修改 main 工作区。
- 失败形态与 SAFETY-6 Review 的 R-001 描述一致（关闭时在途保存恢复后解引用已清空的 `_book`）。
