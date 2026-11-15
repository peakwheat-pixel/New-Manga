# AC2 补齐进展：4 格已补「测试名 (文件:行) + 断言说明」

- head: 34aafa967
- 时间：2026-11-16
- 核实方式：`Select-String` 按文件与测试名定位，**4/4 命中且行号一致**

原 blocked 理由（节选）：「缺 4 格 `测试名 (文件:行)` + 断言说明：Region 编辑 / 阅读偏好 / 主题外观 / 整书进度」，
并指出「矩阵 §7 自认仅 12 格逐行核对断言、其余为类摘要 + 方法名」。

## 本轮补齐的 4 格

| 格 | 测试名 | 文件:行（仓库相对路径） | 断言了什么 |
|---|---|---|---|
| Region 编辑 | `Registry_RegionWriteCommands_AreCoreBackedOnTheRegionFamilyMinor` | `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs:50` | L52 的 `Assert.Equal(...)` 核对 region 写命令由 core 家族命令承载 |
| 阅读偏好 | `LoadAppliesStoredPreferencesAndBookProgress` | `apps/desktop-avalonia/tests/NewManga.App.Tests/ReaderReadingPreferencesTests.cs:26` | L36 `Assert.Equal(1.5, viewModel.Zoom)` —— 存储的缩放已应用到 VM |
| 主题外观 | `Sink_MapsEveryThemeSettingsFieldIntoTheCanonicalDocument` | `apps/desktop-avalonia/tests/NewManga.App.Tests/AppearanceThemeSettingsSinkTests.cs:24` | L42 `Assert.Equal("builtin.fluent-dark", written.VisualThemeId)` —— 主题 id 映射正确 |
| 整书进度 | `CommittedSave_RefreshesShelfDetail_AndShelfMatchesReader` | `apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs:103` | L106 `Assert.Equal(ChapterId, library.SelectedChapter?.ChapterId)` —— 保存后书架与阅读器一致 |

> 注：`RegionWriteCommandTests.cs` 实际位于 **`NewManga.CoreClient.Tests/Commands/`**，不是 `App.Tests`。
> 初稿只写了文件名，经核实后补全为完整相对路径。

## 为什么这不足以关闭 AC2

blocked 理由的**第二半仍然成立**：

> 矩阵 §7 自认仅 **12 格**逐行核对断言、其余为**类摘要 + 方法名**

补这 4 格只解决了「缺 4 格」这一半；**整张矩阵其余格仍缺逐行断言说明**。

⇒ 本轮**只登记进展，不翻转 AC2 状态**。

要把 AC2 真正关闭，需要把矩阵里**所有**格都补成「测试名 (文件:行) + 断言说明」——
那是逐格读测试源码的工作量，需单独立卡。

## 可复算

```powershell
Select-String -Path <上述文件> -Pattern <上述测试名>
```

4 个测试全部命中，行号与表中一致。
