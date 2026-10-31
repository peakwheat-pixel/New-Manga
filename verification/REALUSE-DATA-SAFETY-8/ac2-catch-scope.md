# AC2（F-004）：异常捕获收紧

日期：2026-11-01。Owner：DSH。基线：`main@bb7cbda1d`。

## 问题（SAFETY-7 Review F-004）

`ReaderOverlayViewModel.CloseAsync` 等待在途保存时使用 `catch (Exception)` 静默吞掉所有异常；
而 `SaveProgressCoreAsync` 只把 `InvalidOperationException` / `SidecarException` 记为类型化状态。
其余异常（含 R-001 同类 NRE）被完全静默，同类回归今后不可见。

## 改动

### 1. `SaveProgressCoreAsync` 增加通用 catch（不再静默）

```csharp
catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
{
    SaveStatusText = "进度：保存失败（Host 不可用）";
}
catch (Exception ex)
{
    // F-004: never swallow a non-typed failure silently.
    System.Diagnostics.Debug.WriteLine($"ReaderOverlayViewModel: progress save failed: {ex}");
    SaveStatusText = "进度：保存失败（内部错误）";
}
finally
{
    _isSaving = false;
}
```

效果：非类型化异常会写 `Debug` 并设置可见状态；保存路径自身不再向调用方抛出未观察异常。

### 2. `CloseAsync` 的等待 catch 限定为类型化集合

```csharp
catch (Exception ex) when (ex is InvalidOperationException or NewManga.CoreClient.Diagnostics.SidecarException)
{
    // typed failures are already recorded by SaveProgressCoreAsync
}
```

未类型化异常不会在关闭路径被静默：它们已由 core 的通用 catch 记录并设置状态，不会再冒泡到
`CloseAsync`；`CloseAsync` 只吞掉已经记录过的类型化失败。

## 验证

- `dotnet build`：0 警告 / 0 错误，EXIT=0。
- `dotnet test --filter FullyQualifiedName~LibraryProgressRefreshTests`：**7/7**，EXIT=0。
- 全量：**396 通过 / 0 失败 / 7 跳过（403）**，EXIT=0。
- 证据：`ac1-fix-tests.txt`。

## 边界

- 不改保存协议、不改状态文案语义（原有 5 种类型化状态保持不变），仅新增「内部错误」兜底状态。
- 未放宽 `catch` 覆盖范围之外的行为；关闭路径仍保证继续执行。
