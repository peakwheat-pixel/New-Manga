# V11R-E2E-1 证据包：主题子系统路径隔离（`--theme-home`）

- Task：`V11R-E2E-1`（Lead 2026-10-30 分配；修 `FOLLOW-UP-E2E-1`，发布前必修）
- Owner：`core-bridge`（未自审）
- 分支：`v11r/core-bridge`；本卡实现 commit 见 Handoff（完成后回报）
- 结论：**PASS** —— 指定 `--theme-home=<temp>` 时主题设置写入隔离目录（`appearance=light`），
  真实 `%APPDATA%\NewManga` **零新建、零修改**（目录 mtime 前后一致、文件集合一致）。

## 1. 问题（真机实测，FOLLOW-UP-E2E-1）

Theme Studio / ThemeService 的持久化路径固定为 `Environment.GetFolderPath(ApplicationData)/NewManga/...`，
**不受 `--data-root` 隔离**（子进程改 `APPDATA` 无效）。L4 真机做"重启持久化 E2E"时写入了用户真实
`%APPDATA%\NewManga\theme-settings.json`（已备份并删除恢复）。E2E / 多实例 / 测试必须能隔离。

## 2. 实现

### 2.1 新增 CLI 选项 `--theme-home <dir>`

单一路径覆盖整个主题子系统（E2E / 诊断 / 便携）：

| 内容 | 路径 |
|---|---|
| 设置文件 | `<dir>/theme-settings.json` |
| 用户主题目录 | `<dir>/themes` |
| 收藏 | `<dir>/theme-studio-favorites.json` |

- 解析支持 `--theme-home=X` 与 `--theme-home X`（A-8 两种写法）；空值/仅空白 → `InvalidReason` + exit 2；
- 加入 `AppOptions.ValueKeys` 与 `TryApply`（`AppOptions.cs`）；
- 未指定时**保持原行为**：`%APPDATA%/NewManga/...`（与 `ThemeSettingsStore.DefaultDirectory` 完全一致）。

### 2.2 纯函数解析器 + 接线

- 新增 `apps/desktop-avalonia/src/NewManga.App/Services/ThemeHome.cs`：
  `ThemeHome.Resolve(AppOptions)` / `ThemeHome.Resolve(string?)` → `ThemeHomePaths`（无 Avalonia 依赖，可单测）；
- `App.axaml.cs` 的 `CreateV2Shell` 调用
  `ThemeEngineThemeStudioService.CreateProduction(this, manager, themeDirectory: ..., settingsFilePath: ..., favoritesFilePath: ...)`；
  这是该服务唯一的生产构造路径（`CreateV2Shell` 内单点接线）。

## 3. 测试（真实执行，见 `test.log`）

| 测试 | 覆盖 | 结果 |
|---|---|---|
| `ThemeHomeTests.NoOverride_KeepsShippedRoamingPaths` | 未指定 → 与 `ThemeSettingsStore.DefaultSettingsFilePath` / `ThemeRegistry.DefaultUserThemeDirectory` / 默认收藏路径一致 | PASS |
| `ThemeHomeTests.BlankOverride_KeepsShippedPaths`（3 组） | `""` / 空白 / `\t` → 默认路径 | PASS |
| `ThemeHomeTests.EqualsAndSpaceForms_ResolveIdentically` | `--theme-home=X` == `--theme-home X` | PASS |
| `ThemeHomeTests.CustomRoot_WithSpaces_MapsAllThreePaths` | 含空格路径 → 三个路径正确 | PASS |
| `ThemeHomeTests.RelativeOverride_IsResolvedToAnAbsoluteRoot` | 相对路径 → 绝对路径 | PASS |
| `ThemeHomeTests.EmptyValue_IsRejectedByTheParser` | `--theme-home=` → `InvalidReason`（含 "non-empty"）→ Program.Main exit 2 | PASS |
| `ThemeHomeTests.WhitespaceValue_IsRejectedByTheParser` | `--theme-home "   "` → `InvalidReason` | PASS |
| `ThemeHomeTests.SettingsStore_WritesOnlyTheCustomThemeHome_DefaultPathUntouched` | 真实 `ThemeSettingsStore` 读写自定义路径；默认 `%APPDATA%\NewManga\theme-settings.json` 不存在/未修改 | PASS |
| `ThemeHomeTests.FavoritesStore_WritesOnlyTheCustomThemeHome` | 收藏写入 `<dir>/theme-studio-favorites.json`；默认收藏路径未修改 | PASS |

`ThemeHomeTests` 共 **11/11 PASS**；全量测试见 `test.log`（0 失败）。构建 `build.log`：`-warnaserror` 0W/0E。

## 4. 真机验证（UIA 真实点击，必须项）

启动（真实 sidecar，隔离 data-root/log-dir/theme-home，`--variant=dark` 以便观察变化）：

```powershell
NewManga.App.exe --shell=v2 --exit-after=600000 `
  --data-root  <temp>\data `
  --log-dir    <temp>\logs `
  --sidecar-dir <packaged sidecar> `
  --theme-home <temp>\theme-home `
  --width=1400 --height=900 --variant=dark --legacy-shell-check=off
```

UIA 操作流（真实窗口、真实点击，非 headless）：

1. `Ctrl+,`（或 UIA 的 `ThemeStudioButton`/`主题工作室`）打开 Theme Studio；
2. 右侧"外观（立即生效）"点击 **浅色**（UIA 元素 `浅色`，界面立即变浅）；
3. 点击 **应用**（UIA 元素 `应用`）；
4. 关闭窗口（WM_CLOSE，进程优雅退出）。

断言结果：

| 断言 | 结果 | 证据 |
|---|---|---|
| `<temp>/theme-home/theme-settings.json` 存在 | **PASS** | `theme-home-settings.json` |
| 设置内容 `appearance == "light"` | **PASS** | `theme-home.json`（`appearance: light`） |
| 真实 `%APPDATA%\NewManga` 无新建 | **PASS**（前后文件集合一致，均为空） | `real-appdata-untouched.json` |
| 真实 `%APPDATA%\NewManga` 无修改 | **PASS**（目录 `LastWriteTimeUtc` 前后一致） | `real-appdata-untouched.json` |
| 主题子系统其余路径也在 `<temp>` 下 | **PASS**（`themes/`、收藏文件均按 `<dir>` 解析；无全局写入） | `theme-home.json` |
| Host 就绪 | **PASS**（`host.log` 含 `core_service ready`） | `logs/host.log`（真实 sidecar） |

真机截图：`launch-dark-before.png`（启动后深色）、`theme-studio-light-applied.png`（Theme Studio 内已应用浅色）。

> 说明：UIA 操作通过 `Cua Driver` 对真实窗口执行（`Ctrl+,` + 坐标点击 `浅色`/`应用`），
> 未修改产品代码以外的 UI；`--theme-home` 生效后所有主题持久化均落在隔离目录。

## 5. 文件清单

```
verification/V11R-E2E-1/
  README.md                     （本文件）
  theme-home.json               （隔离路径 + 设置内容 + UI 流程 + 结果）
  theme-home-settings.json      （隔离目录内真实 theme-settings.json 字节副本）
  real-appdata-untouched.json   （真实 %APPDATA%\NewManga 前后快照 + 断言）
  real-appdata-before.json      （操作前快照）
  build.log                     （dotnet build -warnaserror 输出）
  test.log                      （dotnet test --settings tests/NewManga.runsettings 输出）
  launch-dark-before.png        （启动后、应用浅色前）
  theme-studio-light-applied.png（Theme Studio 应用浅色后）
```

## 6. 备注 / 偏差

1. 真机验证的 `--theme-home` 临时目录位于 `%TEMP%\nm-e2e1`（无空格路径，避免启动参数被 shell 拆分）；
   sidecar 使用打包副本（`HOST-CORECLIENT-1\sidecar-copy` 的临时拷贝）。
2. 应用浅色后设置文件即被写入（外观为"立即生效"并持久化）；随后点击"应用"完成提交，行为与
   Theme Studio 设计一致，未改动 ThemeEngine 语义。
3. 本卡未改 ThemeEngine / DesignSystem / UI 布局；仅 AppOptions/Program 参数、`ThemeHome`、`CreateV2Shell` 接线与测试。
