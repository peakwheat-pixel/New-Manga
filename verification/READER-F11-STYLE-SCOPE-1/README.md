# READER-F11-STYLE-SCOPE-1 · AC1–AC4 证据（2026-11-17）

## 问题（AC1，机制已定位）

`V2LocalStyles.axaml` 只被 `AppShellV2.axaml:16` 与 `ThemeStudioView.axaml:19` 引入；
`ImmersiveReaderWindow` 由 `App.axaml.cs` 的 `WireImmersiveReader` **在代码里构造**（没有 XAML StyleInclude），
因此 `Border.topband`（`V2LocalStyles.axaml:53`）、`Border.statusband`（`:58`）、`Button.chip.on`（`:118`）这些规则在沉浸窗**不生效**。

## 修复（AC3）

`apps/desktop-avalonia/src/NewManga.App/Shell/V2/ImmersiveReaderWindow.cs`：构造时加

```csharp
Styles.Add(new StyleInclude(new Uri("avares://NewManga.App/"))
{
    Source = new Uri("avares://NewManga.App/Views/V2/Shell/Theme/V2LocalStyles.axaml"),
});
```

- **未改** `V2LocalStyles.axaml` 的内容，**未改**其它页面/空间的样式作用域。
- 构建：`dotnet build tests/NewManga.App.Tests` → **0 warnings / 0 errors，BUILD_EXIT=0**。
- 回归：`--filter ImmersiveReader|ReaderOverlay` → **6 passed / 0 failed / EXIT=0**。

## 判别力（AC4，像素实测）

同一页同一状态（BOOK-FIXTURE-1 第 1 页，Webtoon 纵向），修复前后整屏截图取样（原生像素）：

| 位置 | 修复前（无样式作用域） | 修复后（有样式作用域） | 判定 |
|---|---|---|---|
| 顶带 `(600,20)` | `(244,243,240)` 画布色 | `(255,255,255)` Panel 白 | 样式**已生效** |
| 顶带 `(1800,20)` | `(244,243,240)` | `(255,255,255)` | 同上 |
| 底带 `(300,1405/1410/1415/1430/1438)` | `(244,243,240)` | `(255,255,255)` | 同上 |
| 进度轨道线 `(300,1420)` | `(236,234,229)` | `(236,234,229)` | 不变（本就无 topband/statusband 依赖） |
| 画布 `(600,60)` | `(255,255,255)` | `(255,255,255)` | 不变 |
| 模式 chip `Webtoon 纵向` | 无 Accent 高亮 | **Accent 高亮**（`Button.chip.on`） | 样式**已生效** |

## 证据文件

| 文件 | sha256 | 说明 |
|---|---|---|
| `rf11s-01-after-f11.jpg` | `bd9751dc4b835caa9b1d4f5e77a86ccbe693af3b6b8eca9f64016b310fd98be3` | **修复后** F11 整屏（顶/底带已变白、chip 高亮） |
| `rf11s-02-after-inwindow.jpg` | `b7f6bbce33ea7b0c3feaf2b175f787aaef23c84658c30e9f947edc52c5a82dc7` | **修复后** 主窗口内阅读器（对照基线，应与修复前一致） |

> 修复前的对照图沿用条件 3 证据：`verification/MAINT-1-RELEASE-MONITOR/condition3/c3-06-f11-immersive-content.jpg`
> （sha256 `8ce0fc0a…5535`）。两张为同页同态（Webtoon 纵向、第 1 / 8 页、0%）。

## 边界（重要）

1. **本证据来自 Debug 构建**（`src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe`，`--sidecar-dir` 指向 INSTALLER-MATRIX-1 stage 的 core-sidecar）。
   **已发布产物（stage / setup.exe）仍是修复前的行为**；要让安装包带上本修复，需重新 publish + 打包（不在本卡范围）。
2. 因修复会改变 F11 外观，**条件 3 的 `c3-06` 截图在修复后属于"修复前状态"**；条件 3 的结论（全屏/无边框/内容渲染正常）不受影响，
   但若将来重截，外观会与本卡证据一致。
3. 未覆盖：深色主题下的同组对照、其它模式（分页）下的 chip 高亮、缩放/DPI。

## 追加：修复已进入 **Release 单文件发布产物**（2026-11-17）

现状（不是重新打包安装器，而是按仓库发布配方重新 publish 应用）：

```
dotnet publish apps/desktop-avalonia/src/NewManga.App/NewManga.App.csproj -c Release -r win-x64 `
  --self-contained -p:PublishSingleFile=true -p:PublishTrimmed=true `
  -p:IncludeNativeLibrariesForSelfExtract=true -p:PublishReadyToRun=true `
  -p:EnableCompressionInSingleFile=true -o <workspace>\app
```

- **PUBLISH_EXIT=0**；产物 `NewManga.App.exe` **37,344,550 B**，sha256 `6dc473b8651ffb5b2ec6b798c7789137c433346b3d50401adcb6ffd89ccf7d67`。
- 用该产物（`--data-root` 隔离副本、`--sidecar-dir` 指向 INSTALLER-MATRIX-1 stage 的 `core-sidecar`）经 UI Automation 点 `阅读` 再按 `F11`，
  整屏截图取样：顶带 `(600,20)`/`(1800,20)` = **(255,255,255)**、底带 `(300,1410)`/`(300,1430)` = **(255,255,255)**、
  `(2,2)` = **(255,255,255)**、进度轨道线 `(300,1420)` = `(236,234,229)`（不变）。
- 该截图转 JPEG q90 后的 sha256 = **`bd9751dc4b835caa9b1d4f5e77a86ccbe693af3b6b8eca9f64016b310fd98be3`**，
  **与本目录 `rf11s-01-after-f11.jpg` 逐字节相同** ⇒ Debug 与 Release 发布产物的渲染结果一致，修复确实进了发布配方。

**仍然成立的历史事实**：`INSTALLER-MATRIX-1` 的 stage 产物（`2026-11-15` 构建）**早于本修复**，
且按证据字节保留规则**未覆盖**；要让 `setup.exe` 带上本修复，需重新 publish + 跑 NSIS 打包（未做）。
